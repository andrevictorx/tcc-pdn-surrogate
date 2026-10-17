"""Validação do pipeline e das hipóteses contra as referências teóricas.

Executa os itens V1–V13 de `spec/PLANO_VALIDACAO.md` e grava os resultados em
`data/processed/validacao.json`. Os arquivos brutos são opcionais: sem eles, os
itens V1–V4 ficam marcados como "sem dados".

Uso:
  python scripts/validacao_teorica.py
"""
from __future__ import annotations

import json
import logging
import sys
import zipfile
from pathlib import Path

import numpy as np
from scipy.signal import find_peaks
from scipy.stats import spearmanr

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
from scripts.reduzir_zip_pdn import ler_touchstone_texto, s_para_z  # noqa: E402
from src.data.consistencia import capacitancia_medida, frequencia_modal  # noqa: E402
from src.data.subsets import SEIS_CAMADAS, UMA_CAVIDADE  # noqa: E402
from src.data.touchstone import primeiro_minimo  # noqa: E402

log = logging.getLogger("validacao")
EPS0, MIL, IN = 8.8541878128e-12, 25.4e-6, 0.0254
CACHE = RAIZ / "data/processed"
R: dict[str, dict] = {}


def registra(chave, referencia, criterio, valores, aprovado):
    R[chave] = {"referencia": referencia, "criterio": criterio, "valores": valores,
                "aprovado": None if aprovado is None else bool(aprovado)}
    estado = {True: "APROVADO", False: "REPROVADO", None: "SEM DADOS"}[R[chave]["aprovado"]]
    log.info("%-4s %-10s %s", chave, estado, json.dumps(valores, ensure_ascii=False))


def ajuste_log(y, *xs):
    """Mínimos quadrados de log y contra log x_i; devolve os expoentes e o R²."""
    M = np.column_stack([np.ones(len(y))] + [np.log(x) for x in xs])
    b, *_ = np.linalg.lstsq(M, np.log(y), rcond=None)
    r = np.log(y) - M @ b
    return b[1:], 1 - (r @ r) / ((np.log(y) - np.log(y).mean()) ** 2).sum()


# ----------------------------------------------------------------------------------- dados
def carrega():
    d4 = np.load(CACHE / "pi4_cache.npz")
    d1 = np.load(CACHE / "pi1_cache.npz")
    sub = {
        "PI-4": dict(f=d4["freq"], z=d4["z11"].astype(complex), X=d4["X_corrigido"], F=[str(c) for c in d4["features"]],
                     n_pg=2, A=np.full(len(d4["z11"]), SEIS_CAMADAS.x_width_m * SEIS_CAMADAS.y_width_m),
                     a=np.full(len(d4["z11"]), SEIS_CAMADAS.x_width_m), b=np.full(len(d4["z11"]), SEIS_CAMADAS.y_width_m),
                     tand=np.full(len(d4["z11"]), 0.01)),
        "PI-1": dict(f=d1["freq"], z=d1["zabs"].astype(float) * np.exp(1j * d1["zang"].astype(float)), X=d1["X"].astype(float),
                     F=[str(c) for c in d1["features"]], n_pg=1,
                     A=np.full(len(d1["zabs"]), UMA_CAVIDADE.x_width_m * UMA_CAVIDADE.y_width_m),
                     a=np.full(len(d1["zabs"]), UMA_CAVIDADE.x_width_m), b=np.full(len(d1["zabs"]), UMA_CAVIDADE.y_width_m),
                     tand=np.full(len(d1["zabs"]), 0.02)),
    }
    s4, s1 = sub["PI-4"], sub["PI-1"]
    s4["h"], s4["er"] = s4["X"][:, 0] * MIL, s4["X"][:, 1]
    s1["h"], s1["er"], s1["cdec"], s1["ndec"] = UMA_CAVIDADE.espessura_efetiva_m(s1["X"][:, 0]), s1["X"][:, 1], s1["X"][:, 3], s1["X"][:, 2]
    for nome, arq in [("PI-3", "pi3_cache.npz"), ("PI-2", "pi2_cache.npz")]:
        d = np.load(CACHE / arq)
        F = [str(c) for c in d["features"]]
        X = d["X"].astype(float)
        ok = d["simu_index"] != 110000
        col = lambda c: X[ok, F.index(c)]
        sub[nome] = dict(f=d["freq"], z=d["z_a1"].astype(complex)[ok], X=X[ok], F=F, n_pg=2,
                         h=col("TDIEL") * MIL, er=col("PERMITTIVITY"), a=col("XWIDTH") * MIL, b=col("YWIDTH") * MIL,
                         A=col("XWIDTH") * col("YWIDTH") * MIL ** 2, tand=col("LOSSTANGENT"),
                         u=col("A1_XCENTER") / col("XWIDTH"), v=col("A1_YCENTER") / col("YWIDTH"))
    for s in sub.values():
        s.setdefault("cdec", np.zeros(len(s["z"])))
        s.setdefault("ndec", np.zeros(len(s["z"])))
        s["Zabs"] = np.abs(s["z"])
        s["k1"] = np.array([primeiro_minimo(a) for a in s["Zabs"]])
        s["f0"] = s["f"][s["k1"]]
        s["C"] = np.array([capacitancia_medida(s["f"], zz) for zz in s["z"]])
        s["C_prev"] = s["n_pg"] * EPS0 * s["er"] * s["A"] / s["h"]
    return sub


# ----------------------------------------------------------------------- A. pipeline
def bloco_a():
    amostras = []
    p4 = RAIZ / "6_layer_pcb_based_pdn_with_two_arrays_LHS_mar_2023/variation"
    p1 = RAIZ / "pwr_gnd_plane_pcb_11x11_array_nov_22_2023"
    if p4.exists():
        amostras += [("PI-4", (p4 / f"simu_{i}.s36p").read_text(), 36, 0, i, "pi4") for i in (1000, 1500, 1999)]
    arq1 = sorted(p1.rglob("simu_*.s2p"))[:3] if p1.exists() else []
    amostras += [("PI-1", a.read_text(), 2, 0, int(a.stem.split("_")[1]), "pi1") for a in arq1]
    for nome, zipn, alvo in [("PI-3", "8-layer-pcb-based-pdn-two-via-arrays-lhs-28-jul-2022.zip", "pi3"),
                             ("PI-2", "4-layer-pcb-based-pdn-21-feb-2022.zip", "pi2")]:
        if (RAIZ / zipn).exists():
            with zipfile.ZipFile(RAIZ / zipn) as zf:
                nomes = [n for n in zf.namelist() if n.endswith(".s28p")][:2]
                amostras += [(nome, zf.read(n).decode("ascii"), 28, 10, int(Path(n).stem.split("_")[1]), alvo) for n in nomes]
    if not amostras:
        for k in ("V1", "V2", "V3", "V4"):
            registra(k, "—", "—", {}, None)
        return
    import skrf
    import tempfile
    err_skrf, assim, sv_max, rep = [], [], [], []
    caches = {"pi4": np.load(CACHE / "pi4_cache.npz"), "pi1": np.load(CACHE / "pi1_cache.npz"),
              "pi3": np.load(CACHE / "pi3_cache.npz"), "pi2": np.load(CACHE / "pi2_cache.npz")}
    for nome, txt, n, porta, simu, alvo in amostras:
        f, s = ler_touchstone_texto(txt, n)
        z = s_para_z(s)
        with tempfile.NamedTemporaryFile("w", suffix=f".s{n}p", delete=False) as t:
            t.write(txt)
        zr = skrf.Network(t.name).z
        Path(t.name).unlink()
        err_skrf.append(float(np.max(np.linalg.norm(z - zr, axis=(1, 2)) / np.linalg.norm(zr, axis=(1, 2)))))
        assim.append(float(np.max(np.abs(s - np.swapaxes(s, 1, 2)))))
        sv_max.append(float(np.linalg.svd(s, compute_uv=False).max()))
        c = caches[alvo]
        i = int(np.flatnonzero(c["simu_index"] == simu)[0])
        zc = c["z11"][i] if alvo == "pi4" else (c["zabs"][i] * np.exp(1j * c["zang"][i]) if alvo == "pi1" else c["z_a1"][i])
        rep.append(float(np.max(np.abs(zc - z[:, porta, porta]) / np.abs(z[:, porta, porta]))))
    registra("V1", "scikit-rf 2.1 (implementação de referência de Z = Z0(I+S)(I−S)⁻¹)", "‖Z − Z_skrf‖/‖Z_skrf‖ < 1e-10 em toda frequência (matriz inteira)",
             {"amostras": len(amostras), "erro_max": max(err_skrf)}, max(err_skrf) < 1e-10)
    registra("V2", "rede passiva e recíproca: S = Sᵀ (teoria de redes)", "max|S − Sᵀ| < 1e-4",
             {"assimetria_max": max(assim)}, max(assim) < 1e-4)
    registra("V3", "passividade da rede de N portas: valores singulares de S ≤ 1", "σ_max ≤ 1 + 1e-6",
             {"sigma_max": max(sv_max)}, max(sv_max) <= 1 + 1e-6)
    registra("V4", "reprodutibilidade: cache × reprocessamento do arquivo bruto", "erro relativo máx. < 1e-2 (float16 na fase do PI-1)",
             {"erro_max": max(rep), "por_amostra": [round(x, 6) for x in rep]}, max(rep) < 1e-2)


# ------------------------------------------------------------------------ B. física
def bloco_b(sub):
    # V5 — capacitância de placas paralelas com campo de borda (Bogatin 2010, p. 133; Palmer 1937; Ott 2009, §11.4.6)
    palmer = lambda a, b, h: (a + h / np.pi * (1 + np.log(2 * np.pi * a / h))) * (b + h / np.pi * (1 + np.log(2 * np.pi * b / h))) / (a * b)
    vals, ok = {}, True
    for nome, s in sub.items():
        r = s["C"] / (s["C_prev"] + s["cdec"])
        p = palmer(s["a"], s["b"], s["h"]) if nome != "PI-1" else np.ones(len(r))
        vals[nome] = {"razao_mediana": round(float(np.median(r)), 4), "Palmer_mediana": round(float(np.median(p)), 4),
                      "medido_sobre_Palmer": round(float(np.median(r / p)), 4)}
        ok &= abs(np.median(r / p) - 1) < 0.02
    s = sub["PI-4"]
    p = palmer(s["a"], s["b"], s["h"])
    rho = spearmanr(s["C"] / s["C_prev"], p).statistic
    vals["PI-4_rho_medido_Palmer"] = round(float(rho), 3)
    ok &= rho > 0.8
    s = sub["PI-3"]
    sel = (np.abs(s["h"] / MIL - 5) < 0.5) | (np.abs(s["h"] / MIL - 10) < 0.5)
    pf_in2 = s["C"][sel] / s["n_pg"] / (s["A"][sel] / IN ** 2) * 4.5 / s["er"][sel] * 1e12
    h5 = np.abs(s["h"][sel] / MIL - 5) < 0.5
    vals["Ott_pF_por_pol2_eps4.5"] = {"h=5 mil": round(float(np.median(pf_in2[h5])), 1), "h=10 mil": round(float(np.median(pf_in2[~h5])), 1)}
    ok &= 150 <= np.median(pf_in2[h5]) <= 260 and 75 <= np.median(pf_in2[~h5]) <= 130
    registra("V5", "Bogatin (2010) p. 133: placas paralelas subestimam C (campo de borda); Palmer (1937): correção de borda para placas retangulares; Ott (2009) §11.4.6: 5–10 mil → ~100–200 pF/pol²",
             "medido/Palmer = 1 ± 0,02 em cada subconjunto; ρ(medido, Palmer) > 0,8 no PI-4; pF/pol² na faixa de Ott", vals, ok)

    # V6 — inclinação abaixo do nulo: desvio de −1 explicado pelo LC série
    vals, ok = {}, True
    for nome, s in sub.items():
        med, prev = [], []
        for zabs, f0 in zip(s["Zabs"], s["f0"]):
            jan = s["f"] < f0 / 3
            if jan.sum() < 3:
                continue
            fw = s["f"][jan]
            med.append(np.polyfit(np.log10(fw), np.log10(zabs[jan]), 1)[0])
            prev.append(np.polyfit(np.log10(fw), np.log10(np.abs(1 - (fw / f0) ** 2) / fw), 1)[0])
        med, prev = np.array(med), np.array(prev)
        vals[nome] = {"medida": round(float(np.median(med)), 4), "prevista_LC": round(float(np.median(prev)), 4),
                      "residuo_mediano": round(float(np.median(med - prev)), 4)}
        ok &= abs(np.median(med - prev)) < 0.02
    registra("V6", "circuito LC série: |Z| = (1 − (f/f0)²)/(2πfC) → inclinação < −1 perto do nulo",
             "|mediana(medida − prevista)| < 0,02", vals, ok)

    # V7 — indutância de espalhamento: L ∝ h·ln(b/a) (Bogatin 2010, eq. 13-31), mais um termo fixo (pads e porta)
    vals, ok = {}, True
    for nome in ("PI-4", "PI-3", "PI-2"):
        s = sub[nome]
        m = s["f0"] < s["f"][-1]
        L = 1 / ((2 * np.pi * s["f0"][m]) ** 2 * s["C"][m]) * 1e12
        hm = s["h"][m] / MIL
        (L0, k), *_ = np.linalg.lstsq(np.column_stack([np.ones(len(L)), hm]), L, rcond=None)
        e = np.polyfit(np.log(hm), np.log(L - L0), 1)[0] if L0 < L.min() else float("nan")
        vals[nome] = {"L0_pH": round(float(L0)), "k_pH_por_mil": round(float(k), 1), "expoente_de_(L-L0)": round(float(e), 3)}
        ok &= 0.9 <= e <= 1.1
    s = sub["PI-4"]
    L = 1 / ((2 * np.pi * s["f0"]) ** 2 * s["C"])
    rv = s["X"][:, s["F"].index("A1_VIARADIUS")] * MIL
    coef, *_ = np.linalg.lstsq(np.column_stack([np.ones(len(L)), np.log(rv)]), L / (s["h"] / MIL) * 1e12, rcond=None)
    vals["PI-4_d(L/h)/d_ln_raio_pH_por_mil"] = round(float(coef[1]), 1)
    vals["Bogatin_k_um_par_de_planos_pH_por_mil"] = "5,1·ln(b/a) ≈ 25–40 para b/a = 150–2500"
    ok &= coef[1] < 0
    registra("V7", "Bogatin (2010) eq. 13-31: L_espalhamento = 5,1·h·ln(b/a) pH (h em mil)",
             "L = L0 + k·h com expoente de (L − L0) em h = 1 ± 0,1; L/h decresce com o raio da via", vals, ok)

    # V8 — nulo de série: f0 = 1/(2π√(LC)) com C ∝ εr·A/h e L ∝ h → f0 ∝ (εr·A)^(−1/2)·h⁰
    vals, ok = {}, True
    for nome in ("PI-3", "PI-2"):
        s = sub[nome]
        e, r2 = ajuste_log(s["f0"], s["A"], s["h"], s["er"])
        vals[nome] = {"expoente_A": round(float(e[0]), 3), "expoente_h": round(float(e[1]), 3), "expoente_er": round(float(e[2]), 3), "R2": round(float(r2), 3)}
        ok &= abs(e[0] + 0.5) < 0.1 and abs(e[1]) < 0.15 and abs(e[2] + 0.5) < 0.1
    registra("V8", "ressonância série f0 = 1/(2π√(LC)) (Bogatin 2010, cap. 13)", "expoentes de A e εr em −0,5 ± 0,1; de h em 0 ± 0,15", vals, ok)

    # V9 — modos: f_mn ∝ 1/√εr e ∝ 1/lado (Bogatin 2010 eq. 12-20; Ott 2009 eq. 6-42)
    vals, ok = {}, True
    s = sub["PI-1"]
    sel = np.flatnonzero(s["ndec"] <= 2)
    fp, er_ = [], []
    for i in sel:
        k = s["k1"][i]
        p, _ = find_peaks(np.log10(s["Zabs"][i, k:]), prominence=0.1)
        f02 = frequencia_modal(0, 2, s["er"][i], s["a"][i], s["b"][i])
        c = s["f"][k + p]
        j = np.flatnonzero(np.abs(c / f02 - 1) < 0.05)
        if len(j):
            fp.append(c[j[0]]); er_.append(s["er"][i])
    (e,), r2 = ajuste_log(np.array(fp), np.array(er_))
    vals["PI-1_TM02_expoente_er"] = round(float(e), 3)
    ok &= abs(e + 0.5) < 0.03
    for nome in ("PI-3", "PI-2"):
        s = sub[nome]
        lado = np.maximum(s["a"], s["b"])
        u_lado = np.where(s["a"] >= s["b"], s["u"], s["v"])
        fp, ld, er_ = [], [], []
        for i in np.flatnonzero(np.abs(np.cos(np.pi * u_lado)) > 0.5):
            k = s["k1"][i]
            p, _ = find_peaks(np.log10(s["Zabs"][i, k:]), prominence=0.3)
            f10 = frequencia_modal(1, 0, s["er"][i], lado[i], 1.0)
            if len(p) and abs(s["f"][k + p[0]] / f10 - 1) < 0.05:
                fp.append(s["f"][k + p[0]]); ld.append(lado[i]); er_.append(s["er"][i])
        e, r2 = ajuste_log(np.array(fp), np.array(ld), np.array(er_))
        vals[f"{nome}_TM10"] = {"expoente_lado": round(float(e[0]), 3), "expoente_er": round(float(e[1]), 3), "n": len(fp)}
        ok &= abs(e[0] + 1) < 0.05 and abs(e[1] + 0.5) < 0.05
    registra("V9", "Bogatin (2010) eq. 12-20; Ott (2009) eq. 6-42: f_mn = c0/(2√εr)·√((m/a)² + (n/b)²)",
             "expoente de εr = −0,5 ± 0,03 (PI-1) / ± 0,05; expoente do lado = −1 ± 0,05", vals, ok)

    # V10 — nós de tensão: detecção do modo × acoplamento κ
    vals, ok = {}, True
    for nome in ("PI-3", "PI-2"):
        s = sub[nome]
        lado = np.maximum(s["a"], s["b"])
        u_lado = np.where(s["a"] >= s["b"], s["u"], s["v"])
        kap = np.abs(np.cos(np.pi * u_lado))
        f10 = frequencia_modal(1, 0, s["er"], lado, 1.0)
        hit = np.zeros(len(s["z"]), bool)
        for i in range(len(s["z"])):
            k = s["k1"][i]
            p, _ = find_peaks(np.log10(s["Zabs"][i, k:]), prominence=0.3)
            hit[i] = len(p) > 0 and abs(s["f"][k + p[0]] / f10[i] - 1) < 0.05
        alto, baixo = hit[kap > 0.5].mean(), hit[kap < 0.2].mean()
        vals[nome] = {"deteccao_kappa>0,5": round(float(alto), 3), "deteccao_kappa<0,2": round(float(baixo), 3)}
        ok &= alto > 0.9 and baixo < 0.5
    s = sub["PI-4"]
    f20 = frequencia_modal(2, 0, s["er"], s["a"], s["b"])
    dentro = f20 < 990e6
    tem = np.array([len(find_peaks(np.log10(s["Zabs"][i, s["k1"][i]:]), prominence=0.05)[0]) > 0 for i in range(len(s["z"]))])
    vals["PI-4_TM20_kappa1_com_pico"] = round(float(tem[dentro].mean()), 3)
    ok &= tem[dentro].mean() > 0.9
    registra("V10", "teoria de cavidades: tensão do modo ∝ cos(mπu)·cos(nπv); porta no nó não excita o modo",
             "detecção > 90 % com κ > 0,5 e < 50 % com κ < 0,2; TM20 (κ = 1) presente no PI-4", vals, ok)

    # V11 — profundidade do nulo: na ressonância X_C = √(L/C), e a perda dielétrica vale R_d = tan δ·√(L/C) (Ott 2009, eq. 10-3)
    vals, ok = {}, True
    for nome in ("PI-4", "PI-3", "PI-2"):
        s = sub[nome]
        idx = np.arange(len(s["z"]))
        L = 1 / ((2 * np.pi * s["f0"]) ** 2 * s["C"])
        prev = s["tand"] * np.sqrt(L / s["C"])
        rnulo = s["z"][idx, s["k1"]].real
        rho = spearmanr(prev, rnulo).statistic
        q = np.median(rnulo / prev)
        vals[nome] = {"Re_nulo_sobre_tand_raiz_LC": round(float(q), 2), "rho": round(float(rho), 3)}
        ok &= rho > 0.85 and 1.0 <= q <= 3.0
    registra("V11", "Ott (2009) eq. 10-3: Q = √(L/C)/R; na ressonância série a perda dielétrica é R_d = tan δ·√(L/C)",
             "ρ(tan δ·√(L/C), Re{Z} no nulo) > 0,85 e razão em [1; 3] (a perda no cobre se soma à dielétrica)", vals, ok)

    # V12 — passividade de Z11
    vals = {n: int((s["z"].real / s["Zabs"]).min(axis=1).__lt__(-0.02).sum()) for n, s in sub.items()}
    registra("V12", "rede passiva: Re{Z11} ≥ 0", "nenhuma curva com Re/|Z| < −2 %", vals, all(v == 0 for v in vals.values()))

    # V13 — parte real em baixa frequência × perda dielétrica esperada
    vals = {}
    for nome, s in sub.items():
        esperado = s["tand"] * np.abs(s["z"][:, 0].imag)
        vals[nome] = {"Re_1MHz_mediano_ohm": round(float(np.median(s["z"][:, 0].real)), 3),
                      "Re_sobre_tand_Im": round(float(np.median(s["z"][:, 0].real / esperado)), 1)}
    registra("V13", "perda dielétrica: Re{Z} ≈ tan δ·|Im{Z}| em regime capacitivo",
             "diagnóstico (sem critério): razão ≫ 1 indica excesso de parte real não físico", vals, None)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    sub = carrega()
    bloco_a()
    bloco_b(sub)
    (CACHE / "validacao.json").write_text(json.dumps(R, ensure_ascii=False, indent=1))
    n_ok = sum(v["aprovado"] is True for v in R.values()); n_f = sum(v["aprovado"] is False for v in R.values())
    log.info("\n%d aprovados · %d reprovados · %d sem critério", n_ok, n_f, len(R) - n_ok - n_f)
