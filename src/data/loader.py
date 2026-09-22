"""
Carregador genérico de subconjuntos de PDN da SI/PI-Database.

Cada subconjunto é descrito por um `SubsetAdapter` (`src/data/subsets.py`), que
declara o que o `parameter.csv` não diz sozinho: número de portas, porta de
interesse, quais colunas são features de geometria, se há banco de decaps, e
as dimensões físicas da placa. `load_pdn_dataset()` carrega um único
subconjunto; `load_multi_subset()` une vários numa mesma grade de frequência,
com uma coluna `subconjunto_id` para permitir validação com topologia retida.

Implementa `spec/UNIAO_SUBCONJUNTOS.md`.
"""

from __future__ import annotations

import logging
import os
import re
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import NamedTuple

import numpy as np
import pandas as pd

from .grid import GRADE_COMUM, interpolar_para_grade
from .subsets import SubsetAdapter
from .touchstone import parse_touchstone, self_impedance

logger = logging.getLogger(__name__)

_DECAP_RE = re.compile(r"\{([^{}]+)\}")


class PDNDataset(NamedTuple):
    """Estrutura retornada por `load_pdn_dataset()` e `load_multi_subset()`."""

    X: np.ndarray
    """Features de projeto, shape (n_configs, n_features)."""

    y: np.ndarray
    """Curvas |Z11(f)|, shape (n_configs, n_freq), em Ohms."""

    freq: np.ndarray
    """Grade de frequência, shape (n_freq,), em Hz. Nativa do subconjunto em
    `load_pdn_dataset()` sem `grid`; a grade comum em `load_multi_subset()`."""

    simu_index: np.ndarray
    """Índice de simulação original de cada configuração, shape (n_configs,)."""

    subconjunto_id: np.ndarray
    """Nome do subconjunto de origem de cada linha, shape (n_configs,), dtype
    objeto. Permite filtrar por origem para validação com topologia retida."""

    feature_names: list[str]
    """Nomes das colunas de X, na mesma ordem."""

    metadata: dict
    """Contagens, faixas de frequência, subconjuntos incluídos, versão."""


def _parse_decaps(campo: str) -> tuple[int, float]:
    """Extrai (n_decaps, capacitância_total_F) da coluna {ESR/ESL/C/x/y}{...}.

    O formato não tem vírgulas internas — cada capacitor é um bloco
    `{ESR/ESL/C/xPos/yPos}`, e blocos se concatenam sem separador. A regex
    encontra blocos sem chaves aninhadas, o que basta porque a estrutura tem
    profundidade fixa de 2 (lista externa, capacitor interno).
    """
    blocos = _DECAP_RE.findall(campo)
    if not blocos:
        return 0, 0.0
    c_total = sum(float(bloco.split("/")[2]) for bloco in blocos)
    return len(blocos), c_total


def _load_single_config(
    args: tuple,
) -> tuple[int, int, np.ndarray, np.ndarray] | None:
    """Worker: lê um Touchstone e extrai |Z| na porta de interesse.

    Args:
        args: (variation_dir, n_portas, porta, idx, simu_index).

    Returns:
        (idx, simu_index, freq, z_abs) ou None se a leitura falhar.
    """
    variation_dir, n_portas, porta, idx, simu_index = args
    path = variation_dir / f"simu_{simu_index}.s{n_portas}p"
    try:
        network = parse_touchstone(path, n_ports=n_portas)
        z_abs = np.abs(self_impedance(network, port=porta))
        return idx, simu_index, network.freq, z_abs
    except Exception as e:
        logger.warning(f"Erro ao carregar simu_{simu_index}: {e}")
        return None


def load_pdn_dataset(
    adapter: SubsetAdapter,
    n_workers: int | None = None,
    verbose: bool = True,
    grid: np.ndarray | None = None,
) -> PDNDataset:
    """Carrega um subconjunto de PDN descrito por `adapter`.

    Args:
        adapter: descreve o subconjunto — ver `src/data/subsets.py`.
        n_workers: processos paralelos. Default: min(8, CPUs).
        verbose: se True, imprime progresso.
        grid: se fornecida, interpola cada curva para esta grade de
            frequência (log10|Z| contra log10(f); ver `src/data/grid.py`).
            Se None, mantém a grade nativa do subconjunto — usar assim para
            reproduzir medições feitas sobre a grade original (ex.: R1).

    Returns:
        PDNDataset. Configurações cujo arquivo Touchstone falhou ao carregar
        são descartadas (não preenchidas com zero — zero em |Z| quebra
        `log10` e contaminaria qualquer ajuste físico).

    Raises:
        FileNotFoundError: subconjunto, parameter.csv ou variation/ ausentes.
        RuntimeError: nenhuma configuração carregou com sucesso.
    """
    caminho = adapter.caminho
    if not caminho.exists():
        raise FileNotFoundError(f"Subconjunto não encontrado: {caminho}")

    params_csv = caminho / "parameter.csv"
    if not params_csv.exists():
        raise FileNotFoundError(f"parameter.csv não encontrado em {caminho}")

    if verbose:
        print(f"[{adapter.nome}] carregando parâmetros de {params_csv}...")

    df = pd.read_csv(params_csv)
    X_geo = df[list(adapter.features_geometria)].values.astype(np.float64)
    simu_indices_csv = df["simu_index"].values.astype(np.int64)

    if adapter.tem_decaps:
        colunas_decap = [c for c in df.columns if c.strip().startswith("{")]
        if not colunas_decap:
            raise ValueError(
                f"[{adapter.nome}] tem_decaps=True mas nenhuma coluna "
                f"'{{ESR/ESL/C/xPos/yPos}}' encontrada em {params_csv}"
            )
        parsed = df[colunas_decap[0]].map(_parse_decaps)
        n_decaps = np.array([p[0] for p in parsed], dtype=np.float64)
        c_decap_total = np.array([p[1] for p in parsed], dtype=np.float64)
    else:
        n_decaps = np.zeros(len(df), dtype=np.float64)
        c_decap_total = np.zeros(len(df), dtype=np.float64)

    feature_names = list(adapter.features_geometria) + ["n_decaps", "C_decap_total"]
    X_csv = np.column_stack([X_geo, n_decaps, c_decap_total])

    if verbose:
        print(f"  {len(X_csv)} configurações no CSV · {len(feature_names)} features")

    variation_dir = caminho / "variation"
    if not variation_dir.exists():
        raise FileNotFoundError(f"Diretório variation não encontrado em {caminho}")

    if n_workers is None:
        n_workers = min(8, os.cpu_count() or 1)

    if verbose:
        print(
            f"  carregando {len(X_csv)} arquivos .s{adapter.n_portas}p "
            f"com {n_workers} workers (porta {adapter.porta_interesse})..."
        )

    worker_args = [
        (variation_dir, adapter.n_portas, adapter.porta_interesse, i, int(s))
        for i, s in enumerate(simu_indices_csv)
    ]

    resultados: dict[int, tuple[np.ndarray, np.ndarray]] = {}
    n_falhas = 0
    with ProcessPoolExecutor(max_workers=n_workers) as executor:
        futures = {executor.submit(_load_single_config, a) for a in worker_args}
        completos = 0
        for future in as_completed(futures):
            r = future.result()
            if r is None:
                n_falhas += 1
            else:
                idx, _simu_index, freq_nativa, z_abs = r
                resultados[idx] = (freq_nativa, z_abs)
            completos += 1
            if verbose and completos % max(1, len(worker_args) // 10) == 0:
                print(f"  [{completos}/{len(worker_args)}] {len(resultados)} ok, {n_falhas} falhas")

    if not resultados:
        raise RuntimeError(f"[{adapter.nome}] nenhuma configuração carregada com sucesso")
    if n_falhas:
        logger.warning(f"[{adapter.nome}] {n_falhas}/{len(X_csv)} arquivos falharam")

    idxs_ok = sorted(resultados)
    X = X_csv[idxs_ok]
    simu_indices = simu_indices_csv[idxs_ok]

    if grid is None:
        freq_destino = resultados[idxs_ok[0]][0]
        y = np.stack([resultados[i][1] for i in idxs_ok])
    else:
        freq_destino = grid
        y = np.stack(
            [interpolar_para_grade(f_nat, z, grid) for f_nat, z in (resultados[i] for i in idxs_ok)]
        )

    subconjunto_id = np.full(len(X), adapter.nome, dtype=object)

    metadata = {
        "n_configs": len(X),
        "n_falhas": n_falhas,
        "n_features": len(feature_names),
        "n_frequencies": len(freq_destino),
        "freq_min_Hz": float(freq_destino.min()),
        "freq_max_Hz": float(freq_destino.max()),
        "grid_interpolada": grid is not None,
        "features": feature_names,
        "subconjunto": adapter.nome,
        "fonte_doc": adapter.fonte_doc,
        "version": "2.0",
    }

    if verbose:
        print()
        print("=" * 70)
        print(f"[{adapter.nome}] CARREGADO")
        print("=" * 70)
        print(f"X: {X.shape}   y: {y.shape}   freq: {freq_destino[0]/1e6:.1f} MHz "
              f"→ {freq_destino[-1]/1e9:.2f} GHz ({len(freq_destino)} pontos)")
        print(f"Features: {', '.join(feature_names)}")
        print()

    return PDNDataset(
        X=X,
        y=y,
        freq=freq_destino,
        simu_index=simu_indices,
        subconjunto_id=subconjunto_id,
        feature_names=feature_names,
        metadata=metadata,
    )


def load_multi_subset(
    adapters: list[SubsetAdapter],
    n_workers: int | None = None,
    verbose: bool = True,
    grid: np.ndarray | None = None,
) -> PDNDataset:
    """Carrega e une vários subconjuntos numa mesma grade de frequência.

    Colunas de features específicas de um subconjunto (ex.: `TDIEL` do de 6
    camadas) recebem `NaN` nas linhas de subconjuntos que não têm essa coluna
    — não existe unificação semântica entre nomes de coluna diferentes aqui
    (ex.: `TDIEL` e `diel_height` são fisicamente análogos, mas permanecem
    colunas distintas; unificá-los em atributos independentes de topologia é
    trabalho futuro, listado em `spec/UNIAO_SUBCONJUNTOS.md`). `n_decaps` e
    `C_decap_total` são a exceção: já saem de `load_pdn_dataset()` sempre
    presentes (zero onde o subconjunto não tem decaps), então nunca ficam NaN.

    Args:
        adapters: lista de `SubsetAdapter` a unir.
        n_workers, verbose: repassados a cada `load_pdn_dataset()`.
        grid: grade de frequência comum. Default: `GRADE_COMUM`
            (log-espaçada, 400 pontos, 1 MHz–1 GHz — ver `src/data/grid.py`).

    Returns:
        PDNDataset único, com `metadata['subconjuntos']` listando a origem.
    """
    if grid is None:
        grid = GRADE_COMUM

    datasets = [
        load_pdn_dataset(a, n_workers=n_workers, verbose=verbose, grid=grid) for a in adapters
    ]

    features_unidas: list[str] = []
    for d in datasets:
        for f in d.feature_names:
            if f not in features_unidas:
                features_unidas.append(f)

    blocos_X, blocos_y, blocos_sub, blocos_simu = [], [], [], []
    for d in datasets:
        bloco = np.full((len(d.X), len(features_unidas)), np.nan)
        for j, nome_feat in enumerate(d.feature_names):
            bloco[:, features_unidas.index(nome_feat)] = d.X[:, j]
        blocos_X.append(bloco)
        blocos_y.append(d.y)
        blocos_sub.append(d.subconjunto_id)
        blocos_simu.append(d.simu_index)

    X = np.vstack(blocos_X)
    y = np.vstack(blocos_y)
    subconjunto_id = np.concatenate(blocos_sub)
    simu_index = np.concatenate(blocos_simu)

    metadata = {
        "n_configs": len(X),
        "n_features": len(features_unidas),
        "n_frequencies": len(grid),
        "freq_min_Hz": float(grid.min()),
        "freq_max_Hz": float(grid.max()),
        "features": features_unidas,
        "subconjuntos": [a.nome for a in adapters],
        "n_configs_por_subconjunto": {d.metadata["subconjunto"]: d.metadata["n_configs"] for d in datasets},
        "version": "2.0",
    }

    if verbose:
        print()
        print("=" * 70)
        print("UNIÃO DE SUBCONJUNTOS CONCLUÍDA")
        print("=" * 70)
        print(f"X: {X.shape}   y: {y.shape}   subconjuntos: {metadata['subconjuntos']}")
        print(f"Features unidas ({len(features_unidas)}): {', '.join(features_unidas)}")
        print()

    return PDNDataset(
        X=X,
        y=y,
        freq=grid,
        simu_index=simu_index,
        subconjunto_id=subconjunto_id,
        feature_names=features_unidas,
        metadata=metadata,
    )


if __name__ == "__main__":
    from .subsets import SEIS_CAMADAS, UMA_CAVIDADE

    logging.basicConfig(level=logging.INFO)

    print("Testando loader genérico...")
    ds6 = load_pdn_dataset(SEIS_CAMADAS, verbose=True)
    ds1 = load_pdn_dataset(UMA_CAVIDADE, verbose=True)

    print("\nUnindo os dois subconjuntos...")
    unido = load_multi_subset([SEIS_CAMADAS, UMA_CAVIDADE], verbose=True)
    print(f"\nX unido: {unido.X.shape}")
    print(f"Origem das primeiras/últimas linhas: {unido.subconjunto_id[0]}, {unido.subconjunto_id[-1]}")
