"""Reduz um subconjunto PDN da SI/PI-Database à curva de impedância, lendo direto do zip.

Os zips de PI-2 e PI-3 têm de 113 a 147 GB descompactados. Em vez de extrair, cada
arquivo Touchstone é lido em memória, convertido de S para Z e descartado; só as
curvas reduzidas vão para disco. É o procedimento de `spec/UNIAO_SUBCONJUNTOS.md`:
baixar, reduzir à curva, descartar o bruto.

Guarda três curvas por simulação. Pela Fig. 3 das folhas de dados, P1–P10 ficam no
arranjo do regulador (VRM) e P11–P28 no arranjo A1; P11 é a primeira via de alimentação
do A1 vista pelo topo, a mesma posição da porta 0 do PI-4:
  z_a1   autoimpedância na primeira porta do arranjo A1 (P11, índice 10)
  z_vrm  autoimpedância na primeira porta do arranjo VRM (P1, índice 0)
  z_tr   transimpedância entre as duas (Z[P11, P1])

Uso:
  python scripts/reduzir_zip_pdn.py <arquivo.zip> <saida.npz> [--portas 28] [--limite N]
"""
from __future__ import annotations

import argparse
import logging
import time
import zipfile
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import pandas as pd

log = logging.getLogger("reduzir_zip_pdn")
PORTA_A1, PORTA_VRM = 10, 0
_zip: zipfile.ZipFile | None = None


def _abre(caminho: str) -> None:
    """Inicializador do processo: cada processo mantém o próprio handle do zip."""
    global _zip
    _zip = zipfile.ZipFile(caminho)


def ler_touchstone_texto(texto: str, n_portas: int) -> tuple[np.ndarray, np.ndarray]:
    """Lê Touchstone v1 em formato RI: devolve (freq [Hz], S [nf, P, P] complexo)."""
    dados = [l for l in texto.splitlines() if l.strip() and l.lstrip()[0] not in "!#"]
    v = np.array(" ".join(dados).split(), dtype=float)
    b = v.reshape(-1, 1 + 2 * n_portas**2)
    par = b[:, 1:].reshape(-1, n_portas, n_portas, 2)
    return b[:, 0], par[..., 0] + 1j * par[..., 1]


def s_para_z(s: np.ndarray, z0: float = 50.0) -> np.ndarray:
    """Z = Z0 (I + S)(I − S)^-1, resolvido como sistema linear."""
    eye = np.eye(s.shape[1])
    return z0 * np.swapaxes(
        np.linalg.solve(np.swapaxes(eye - s, 1, 2), np.swapaxes(eye + s, 1, 2)), 1, 2
    )


def _processa(args: tuple[str, int]) -> tuple[str, np.ndarray | None, np.ndarray | None, str]:
    nome, n_portas = args
    try:
        texto = _zip.read(nome).decode("ascii")  # verifica o CRC ao terminar a leitura
        freq, s = ler_touchstone_texto(texto, n_portas)
        z = s_para_z(s)
        curvas = np.stack([z[:, PORTA_A1, PORTA_A1], z[:, PORTA_VRM, PORTA_VRM], z[:, PORTA_A1, PORTA_VRM]])
        return nome, freq, curvas.astype(np.complex64), ""
    except Exception as e:  # noqa: BLE001 — registra e segue; a falha entra no relatório
        return nome, None, None, f"{type(e).__name__}: {e}"


def reduzir(zip_path: Path, saida: Path, n_portas: int, limite: int | None, processos: int) -> None:
    zf = zipfile.ZipFile(zip_path)
    csv = next(i.filename for i in zf.infolist() if i.filename.endswith("parameter.csv"))
    with zf.open(csv) as f:
        df = pd.read_csv(f)
    membros = {Path(i.filename).name: i.filename for i in zf.infolist() if i.filename.endswith(f".s{n_portas}p")}
    simu = df["simu_index"].to_numpy()
    nomes = [membros.get(f"simu_{i}.s{n_portas}p") for i in simu]
    sem_arquivo = int(sum(n is None for n in nomes))
    alvo = [(n, n_portas) for n in nomes if n is not None][:limite]
    log.info("%s: %d linhas no CSV, %d arquivos no zip, %d linhas sem arquivo; processando %d",
             zip_path.name, len(df), len(membros), sem_arquivo, len(alvo))

    t0 = time.perf_counter()
    res: dict[str, tuple] = {}
    with ProcessPoolExecutor(processos, initializer=_abre, initargs=(str(zip_path),)) as ex:
        for k, r in enumerate(ex.map(_processa, alvo, chunksize=8), 1):
            res[r[0]] = r[1:]
            if k % 500 == 0 or k == len(alvo):
                dt = time.perf_counter() - t0
                log.info("%d/%d arquivos · %.0f s · restam ~%.0f s", k, len(alvo), dt, dt / k * (len(alvo) - k))

    falhas = {n: r[2] for n, r in res.items() if r[2]}
    ok = [i for i, n in enumerate(nomes) if n in res and not res[n][2]]
    freq = next(res[nomes[i]][0] for i in ok)
    curvas = np.stack([res[nomes[i]][1] for i in ok])  # (n, 3, nf)
    feats = [c for c in df.columns if c != "simu_index"]
    np.savez_compressed(
        saida, X=df.loc[ok, feats].to_numpy(float), features=np.array(feats), simu_index=simu[ok], freq=freq,
        z_a1=curvas[:, 0], z_vrm=curvas[:, 1], z_tr=curvas[:, 2],
        portas=np.array([f"z_a1 = Z[{PORTA_A1},{PORTA_A1}] (P11)", f"z_vrm = Z[{PORTA_VRM},{PORTA_VRM}] (P1)",
                         f"z_tr = Z[{PORTA_A1},{PORTA_VRM}]"]),
        origem=np.array(zip_path.name),
    )
    log.info("salvo %s (%.1f MB): %d curvas, %d falhas, %.0f s",
             saida, saida.stat().st_size / 1e6, len(ok), len(falhas), time.perf_counter() - t0)
    for n, e in list(falhas.items())[:20]:
        log.warning("falha em %s: %s", n, e)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s", datefmt="%H:%M:%S")
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("zip", type=Path)
    ap.add_argument("saida", type=Path)
    ap.add_argument("--portas", type=int, default=28)
    ap.add_argument("--limite", type=int, default=None, help="processa só os N primeiros (teste)")
    ap.add_argument("--processos", type=int, default=8)
    a = ap.parse_args()
    reduzir(a.zip, a.saida, a.portas, a.limite, a.processos)
