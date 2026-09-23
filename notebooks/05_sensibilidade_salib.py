"""
Etapa 3 — Integridade do subconjunto PI-4, sensibilidade (SALib) e modelo de referência.

  A. integridade: razão C_extraída/C_analítica contra simu_index
  B. métricas do modelo de referência (gradient boosting, validação cruzada)
  C. índices de sensibilidade do SALib compatíveis com amostra LHS já existente:
     RBD-FAST (S1), delta (δ e S1) e PAWN — Sobol exige amostragem de Saltelli
     e fica para depois do modelo substituto
  D. mapa de S1 por frequência

Lê o cache produzido por 04_sensibilidade_fisica.py.
"""
from __future__ import annotations

import sys
import time
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from SALib.analyze import delta, pawn, rbd_fast
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import KFold, cross_validate

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from src.data.touchstone import MIL_TO_M, plate_capacitance  # noqa: E402

warnings.filterwarnings("ignore")
OUT = Path(__file__).resolve().parent
NOMES = ["TDIEL", "PERMITTIVITY", "A1_VIARADIUS", "A1_ANTIPADRADIUS",
         "A1_VIAPITCH", "A2_VIARADIUS", "A2_ANTIPADRADIUS", "A2_VIAPITCH"]
# Fronteira observada: nenhum desvio de escala a partir daqui (ver PHYSICS_SPEC).
SIMU_CONFIAVEL = 1500
md: list[str] = []


def tabela(cab: list[str], linhas: list[list[str]]) -> None:
    md.append("| " + " | ".join(cab) + " |")
    md.append("|" + "|".join("---" for _ in cab) + "|")
    md.extend("| " + " | ".join(map(str, l)) + " |" for l in linhas)
    md.append("")
    larg = [max(len(str(c)), *(len(str(l[i])) for l in linhas)) for i, c in enumerate(cab)]
    print("  ".join(str(c).ljust(w) for c, w in zip(cab, larg)))
    for l in linhas:
        print("  ".join(str(v).ljust(w) for v, w in zip(l, larg)))
    print()


def secao(t: str) -> None:
    print("=" * 78 + f"\n{t}\n" + "=" * 78)
    md.append(f"\n## {t}\n")


t_ini = time.perf_counter()
d = np.load(ROOT / "data/processed/pdn6_cache.npz")
X, Y, f, simu = d["X"].astype(float), d["y"].astype(float), d["freq"], d["simu_index"]
ok = simu >= SIMU_CONFIAVEL

# ------------------------------------------------------------------ A
secao("A. Integridade: capacitância extraída contra simu_index")
C_ext = np.median(1 / (2 * np.pi * f[:8] * Y[:, :8]), axis=1)
C_ana = np.array([plate_capacitance(X[i, 1], 5800 * MIL_TO_M, 4000 * MIL_TO_M,
                                    X[i, 0] * MIL_TO_M) for i in range(len(X))])
razao = C_ext / C_ana
conf = (razao >= 1.5) & (razao < 3.0)
linhas = []
for lo, hi in [(1000, 1100), (1100, 1200), (1200, 1300), (1300, 1400), (1400, 1500),
               (1500, 1600), (1600, 1700), (1700, 1800), (1800, 1900), (1900, 2000)]:
    m = (simu >= lo) & (simu < hi)
    linhas.append([f"{lo}–{hi - 1}", int(m.sum()), f"{conf[m].mean() * 100:.0f} %",
                   f"{np.median(razao[m]):.2f}"])
tabela(["simu_index", "n", "conformes", "razão mediana"], linhas)
md.append(f"Bloco confiável (simu_index ≥ {SIMU_CONFIAVEL}): **{ok.sum()}** configurações. "
          f"Bloco suspeito: **{(~ok).sum()}**.\n")

fig, ax = plt.subplots(figsize=(11, 4))
ax.scatter(simu[ok], razao[ok], s=10, c="tab:green", alpha=0.6, label=f"simu ≥ {SIMU_CONFIAVEL} (n={ok.sum()})")
ax.scatter(simu[~ok], razao[~ok], s=10, c="tab:red", alpha=0.5, label=f"simu < {SIMU_CONFIAVEL} (n={(~ok).sum()})")
ax.axvline(SIMU_CONFIAVEL - 0.5, color="k", ls="--", lw=1.5)
ax.axhline(2.13, color="tab:blue", ls=":", lw=1.5, label="razão 2,13 (duas cavidades)")
ax.set_yscale("log"); ax.set_xlabel("simu_index")
ax.set_ylabel(r"$C_{\rm extraída}/C_{\rm analítica}$")
ax.set_title("PI-4: correspondência entre parâmetros do CSV e curvas dos arquivos", fontweight="bold")
ax.legend(fontsize=9); ax.grid(alpha=0.3)
fig.savefig(OUT / "05a_integridade_pi4.png", dpi=150, bbox_inches="tight"); plt.close(fig)

# ------------------------------------------------------------------ B
secao("B. Modelo de referência: gradient boosting, validação cruzada 5 dobras")
cv = KFold(5, shuffle=True, random_state=42)
logY = np.log10(Y)
linhas = []
for fm in (1, 10, 50, 97, 300, 600, 1000):
    k = int(np.argmin(np.abs(f / 1e6 - fm)))
    res = []
    for mask in (np.ones(len(X), bool), ok):
        y = logY[mask, k]
        r = cross_validate(GradientBoostingRegressor(max_depth=2, n_estimators=400,
                           learning_rate=0.05, random_state=42), X[mask], y, cv=cv,
                           scoring=("r2", "neg_root_mean_squared_error"))
        rmse = -r["test_neg_root_mean_squared_error"].mean()
        res.append((r["test_r2"].mean(), r["test_r2"].std(), rmse, rmse / abs(y.mean())))
    (a, sa, _, _), (b, sb, rm, nr) = res
    linhas.append([f"{fm} MHz", f"{a:.3f} ± {sa:.3f}", f"{b:.3f} ± {sb:.3f}",
                   f"{rm:.4f}", f"{nr * 100:.2f} %"])
tabela(["log10|Z11| em", "R² todas (985)", "R² confiável (485)",
        "RMSE confiável (déc.)", "nRMSE confiável"], linhas)

# ------------------------------------------------------------------ C
secao(f"C. SALib — bloco confiável (n = {ok.sum()})")
Xo, Yo = X[ok], Y[ok]
prob = {"num_vars": 8, "names": NOMES,
        "bounds": [[Xo[:, j].min(), Xo[:, j].max()] for j in range(8)]}
inull = Yo.argmin(1)
saidas = {
    "log10|Z11| em 1 MHz (regime capacitivo)": np.log10(Yo[:, 0]),
    "frequência do nulo de série (MHz)": f[inull] / 1e6,
    "log10|Z11| no nulo": np.log10(Yo[np.arange(len(Yo)), inull]),
    "log10|Z11| em 1 GHz (regime indutivo)": np.log10(Yo[:, -1]),
}
for nome, y in saidas.items():
    md.append(f"\n### {nome}\n")
    print(f"--- {nome}")
    r = rbd_fast.analyze(prob, Xo, y, seed=42)
    dl = delta.analyze(prob, Xo, y, seed=42, num_resamples=100)
    pw = pawn.analyze(prob, Xo, y, S=10, seed=42)
    ordem = np.argsort(-np.asarray(r["S1"]))
    tabela(["parâmetro", "S1 (RBD-FAST)", "δ (delta)", "S1 (delta)", "PAWN mediana"],
           [[NOMES[j], f"{r['S1'][j]:+.3f} ± {r['S1_conf'][j]:.3f}",
             f"{dl['delta_balanced'][j]:.3f} ± {dl['delta_balanced_conf'][j]:.3f}",
             f"{dl['S1'][j]:+.3f} ± {dl['S1_conf'][j]:.3f}",
             f"{pw['median'][j]:.3f}"] for j in ordem])
    md.append(f"Soma S1 (RBD-FAST) = **{np.sum(r['S1']):.3f}** — quanto mais perto de 1, "
              "mais a saída é explicada por efeitos individuais, sem interações.\n")
    print(f"soma S1 = {np.sum(r['S1']):.3f}\n")

# ------------------------------------------------------------------ D
secao("D. S1 (RBD-FAST) por frequência — bloco confiável")
S1 = np.array([rbd_fast.analyze(prob, Xo, np.log10(Yo[:, k]), seed=42)["S1"]
               for k in range(len(f))]).T
fig, ax = plt.subplots(figsize=(12, 4.2))
im = ax.imshow(np.clip(S1, 0, 1), aspect="auto", cmap="viridis", vmin=0, vmax=1,
               extent=[f[0] / 1e6, f[-1] / 1e6, 7.5, -0.5])
ax.set_xscale("log"); ax.set_yticks(range(8)); ax.set_yticklabels(NOMES, fontsize=9)
ax.axvline(np.median(f[inull]) / 1e6, color="w", ls="--", lw=1.5)
ax.set_xlabel("Frequência (MHz)")
ax.set_title("Índice de primeira ordem S1 por frequência (SALib, RBD-FAST)", fontweight="bold")
plt.colorbar(im, ax=ax, label="S1")
fig.savefig(OUT / "05b_mapa_S1_salib.png", dpi=150, bbox_inches="tight"); plt.close(fig)
somaS1 = np.clip(S1, 0, None).sum(0)
md.append(f"Soma de S1 ao longo da banda: mínima {somaS1.min():.2f}, mediana "
          f"{np.median(somaS1):.2f}, máxima {somaS1.max():.2f}.\n")
print(f"soma S1: min {somaS1.min():.2f} | mediana {np.median(somaS1):.2f} | max {somaS1.max():.2f}")

dt = time.perf_counter() - t_ini
(OUT / "05_resultados_salib.md").write_text(
    "# Etapa 3 — Integridade, sensibilidade (SALib) e modelo de referência\n\n"
    f"Subconjunto PI-4 · tempo de execução: {dt:.0f} s\n" + "\n".join(md), encoding="utf-8")
print(f"\nconcluído em {dt:.0f} s — 05a_integridade_pi4.png · 05b_mapa_S1_salib.png · 05_resultados_salib.md")
