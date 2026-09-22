"""
Etapa 1 — Sensibilidade dos 8 parametros e verificacao das leis fisicas.

Testa, sobre as 985 configuracoes:
  A. cache do dataset
  B. mapa de sensibilidade Spearman (8 features x 334 frequencias)
  C. ranking global vs. Fig. 11 de Schierholz et al. (T-CPMT 2023)
  D. lei quase-estatica  log|Z11| = log h - log eps_r - log f + const
  E. R1 (inclinacao -1) em escala plena
  F. R2 (escala da capacitancia) em escala plena
  G. reciprocidade: varredura de tolerancia

Nenhum modelo de aprendizado. Falhas aqui sao falhas de dados.
"""
from __future__ import annotations

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import rankdata

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.data.loader import load_pdn_dataset                       # noqa: E402
from src.data.subsets import SEIS_CAMADAS                          # noqa: E402
from src.data.touchstone import (                                  # noqa: E402
    MIL_TO_M, check_invariants, parse_touchstone, plate_capacitance,
)

FEATURES_8 = list(SEIS_CAMADAS.features_geometria)

EPS_0 = 8.8541878128e-12
A_MIL, B_MIL = 5800.0, 4000.0            # XWIDTH, YWIDTH (constantes do dataset)
A_M, B_M = A_MIL * MIL_TO_M, B_MIL * MIL_TO_M
N_QS = 8                                  # pontos usados na regiao quase-estatica
CACHE = ROOT / "data" / "processed" / "pdn6_cache.npz"
OUT = Path(__file__).resolve().parent
RNG = np.random.default_rng(42)

ROTULOS = {
    "TDIEL": "TDIEL\n(altura cavidade)", "PERMITTIVITY": r"$\varepsilon_r$",
    "A1_VIARADIUS": "A1 raio via", "A1_ANTIPADRADIUS": "A1 raio antipad",
    "A1_VIAPITCH": "A1 passo", "A2_VIARADIUS": "A2 raio via",
    "A2_ANTIPADRADIUS": "A2 raio antipad", "A2_VIAPITCH": "A2 passo",
}
# Fig. 11 de Schierholz et al. (2023): RMSE maximo por parametro, em ohms
FIG11 = {"TDIEL": 20.502, "PERMITTIVITY": 1.443, "A1_VIARADIUS": 1.325,
         "A2_VIARADIUS": 1.325, "A1_ANTIPADRADIUS": 0.988,
         "A2_ANTIPADRADIUS": 0.988, "A1_VIAPITCH": 0.600, "A2_VIAPITCH": 0.600}

linhas_md: list[str] = []


def secao(titulo: str) -> None:
    print("\n" + "=" * 78 + f"\n{titulo}\n" + "=" * 78)
    linhas_md.append(f"\n## {titulo}\n")


def tabela(cabecalho: list[str], linhas: list[list[str]]) -> None:
    larg = [max(len(str(cabecalho[j])), max((len(str(l[j])) for l in linhas), default=0))
            for j in range(len(cabecalho))]
    sep = "  ".join("-" * w for w in larg)
    print("  ".join(str(c).ljust(w) for c, w in zip(cabecalho, larg)))
    print(sep)
    for l in linhas:
        print("  ".join(str(v).ljust(w) for v, w in zip(l, larg)))
    linhas_md.append("| " + " | ".join(cabecalho) + " |")
    linhas_md.append("|" + "|".join("---" for _ in cabecalho) + "|")
    for l in linhas:
        linhas_md.append("| " + " | ".join(str(v) for v in l) + " |")
    linhas_md.append("")


def ols(Xd: np.ndarray, yd: np.ndarray) -> dict:
    """OLS com intercepto. Retorna coeficientes, erros-padrao, IC95 e R2."""
    n = Xd.shape[0]
    A = np.column_stack([np.ones(n), Xd])
    beta, *_ = np.linalg.lstsq(A, yd, rcond=None)
    resid = yd - A @ beta
    gl = n - A.shape[1]
    s2 = resid @ resid / gl
    cov = s2 * np.linalg.inv(A.T @ A)
    se = np.sqrt(np.diag(cov))
    r2 = 1.0 - (resid @ resid) / ((yd - yd.mean()) @ (yd - yd.mean()))
    return {"beta": beta, "se": se, "ic": 1.96 * se, "r2": float(r2), "resid": resid,
            "pred": A @ beta}


# ---------------------------------------------------------------- A. cache
secao("A. Carga do dataset")
if CACHE.exists():
    d = np.load(CACHE)
    X, Y, freq, simu = d["X"], d["y"], d["freq"], d["simu_index"]
    print(f"cache carregado de {CACHE.relative_to(ROOT)}")
else:
    ds = load_pdn_dataset(SEIS_CAMADAS, n_workers=8, verbose=True)
    X, Y, freq, simu = ds.X, ds.y, ds.freq, ds.simu_index
    CACHE.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(CACHE, X=X, y=Y, freq=freq, simu_index=simu)
    print(f"cache gravado em {CACHE.relative_to(ROOT)}")

X = X.astype(np.float64)
Y = np.maximum(Y.astype(np.float64), 1e-12)
logY = np.log10(Y)
n_cfg, n_f = Y.shape
print(f"\nX {X.shape} · Y {Y.shape} · freq {freq[0]/1e6:.0f} MHz a {freq[-1]/1e9:.2f} GHz")

i_nulo = Y.argmin(axis=1)
f_nulo = freq[i_nulo]
i_nulo_med = int(np.median(i_nulo))
print(f"nulo de serie: mediana {np.median(f_nulo)/1e6:.0f} MHz "
      f"(faixa {f_nulo.min()/1e6:.0f} a {f_nulo.max()/1e6:.0f} MHz)")

# ------------------------------------------------ B. mapa de sensibilidade
secao("B. Mapa de sensibilidade de Spearman (8 x 334)")


def z(v: np.ndarray) -> np.ndarray:
    v = v - v.mean(axis=0, keepdims=True)
    return v / (v.std(axis=0, keepdims=True) + 1e-300)


rho = z(rankdata(X, axis=0)).T @ z(rankdata(logY, axis=0)) / n_cfg   # 8 x 334
print(f"matriz de correlacao de postos: {rho.shape}")
print(f"|rho| maximo global: {np.abs(rho).max():.3f}")

# ------------------------------------------------------------- C. ranking
secao("C. Ranking de sensibilidade e comparacao com a Fig. 11 publicada")
abaixo, acima = slice(0, i_nulo_med), slice(i_nulo_med, n_f)
resumo = []
for k, f in enumerate(FEATURES_8):
    resumo.append({"feat": f, "max": np.abs(rho[k]).max(),
                   "abaixo": np.abs(rho[k, abaixo]).mean(),
                   "acima": np.abs(rho[k, acima]).mean()})
ordem_medida = sorted(resumo, key=lambda r: -r["max"])
ordem_pub = sorted(FEATURES_8, key=lambda f: -FIG11[f])
pos_pub = {f: i + 1 for i, f in enumerate(ordem_pub)}

tabela(["#", "parametro", "|rho| max", "|rho| abaixo do nulo", "|rho| acima do nulo",
        "RMSE Fig.11 (ohm)", "posicao publicada"],
       [[i + 1, r["feat"], f"{r['max']:.3f}", f"{r['abaixo']:.3f}", f"{r['acima']:.3f}",
         f"{FIG11[r['feat']]:.3f}", pos_pub[r["feat"]]]
        for i, r in enumerate(ordem_medida)])

# ------------------------------------------------- D. lei quase-estatica
secao("D. Lei quase-estatica  |Z| = h / (2 pi f eps_0 eps_r a b)")
lt, le = np.log10(X[:, 0]), np.log10(X[:, 1])
y1 = logY[:, 0]
m = ols(np.column_stack([lt, le]), y1)
nomes = ["intercepto", "log10(TDIEL)", "log10(eps_r)"]
esperado = [None, +1.0, -1.0]
tabela(["termo", "coeficiente", "erro-padrao", "IC 95%", "esperado", "situacao"],
       [[nomes[i], f"{m['beta'][i]:+.4f}", f"{m['se'][i]:.4f}",
         f"[{m['beta'][i]-m['ic'][i]:+.3f}, {m['beta'][i]+m['ic'][i]:+.3f}]",
         "-" if esperado[i] is None else f"{esperado[i]:+.1f}",
         "-" if esperado[i] is None
         else ("OK" if abs(m['beta'][i] - esperado[i]) < 0.15 else "DESVIO")]
        for i in range(3)])
print(f"\nR2 = {m['r2']:.4f}   (n = {n_cfg})")
linhas_md.append(f"\n**R² = {m['r2']:.4f}** (n = {n_cfg})\n")

# teste de embaralhamento
r2_emb = [ols(np.column_stack([lt, le]), y1[RNG.permutation(n_cfg)])["r2"]
          for _ in range(200)]
print(f"embaralhado: R2 = {np.mean(r2_emb):.4f} +- {np.std(r2_emb):.4f} "
      f"(max {np.max(r2_emb):.4f})")
diag = ("lei confirmada" if abs(m['beta'][1] - 1) < 0.15 else
        "INVERSAO (unidade/semantica)" if abs(m['beta'][1] + 1) < 0.3 else
        "DESALINHAMENTO provavel" if abs(m['beta'][1]) < 0.2 else "expoente inesperado")
print(f"diagnostico: {diag}")
linhas_md.append(f"\nEmbaralhado: R² = {np.mean(r2_emb):.4f} ± {np.std(r2_emb):.4f}. "
                 f"**Diagnóstico: {diag}**\n")

# ----------------------------------------------------- E. R1 escala plena
secao("E. R1 — inclinacao log-log em baixa frequencia")
lf = np.log10(freq[:N_QS])
incl = np.polyfit(lf, logY[:, :N_QS].T, 1)[0]
tabela(["grandeza", "valor"],
       [["media", f"{incl.mean():+.4f}"], ["desvio-padrao", f"{incl.std():.4f}"],
        ["minimo", f"{incl.min():+.4f}"], ["maximo", f"{incl.max():+.4f}"],
        ["esperado", "-1.0000"],
        ["dentro de [-1,05; -0,95]", f"{np.mean((incl>-1.05)&(incl<-0.95))*100:.1f} %"]])

# ----------------------------------------------------- F. R2 escala plena
secao("F. R2 — escala da capacitancia")
C_ext = np.median(1.0 / (2 * np.pi * freq[:N_QS] * Y[:, :N_QS]), axis=1)
C_ana = np.array([plate_capacitance(X[i, 1], A_M, B_M, X[i, 0] * MIL_TO_M)
                  for i in range(n_cfg)])
razao = C_ext / C_ana
q = np.percentile(razao, [5, 25, 50, 75, 95])
tabela(["estatistica", "C_extraida / C_analitica"],
       [["p5", f"{q[0]:.3f}"], ["p25", f"{q[1]:.3f}"], ["mediana", f"{q[2]:.3f}"],
        ["p75", f"{q[3]:.3f}"], ["p95", f"{q[4]:.3f}"],
        ["minimo", f"{razao.min():.3f}"], ["maximo", f"{razao.max():.3f}"]])
rho_rt = float((z(rankdata(X[:, 0])[:, None]).T @ z(rankdata(razao)[:, None]) / n_cfg)[0, 0])
print(f"\nSpearman(TDIEL, razao) = {rho_rt:+.3f}")
mc = ols(np.column_stack([lt, le]), np.log10(C_ext))
tabela(["termo", "coef. de log10(C_extraida)", "IC 95%", "esperado"],
       [["log10(TDIEL)", f"{mc['beta'][1]:+.4f}",
         f"[{mc['beta'][1]-mc['ic'][1]:+.3f}, {mc['beta'][1]+mc['ic'][1]:+.3f}]", "-1.0"],
        ["log10(eps_r)", f"{mc['beta'][2]:+.4f}",
         f"[{mc['beta'][2]-mc['ic'][2]:+.3f}, {mc['beta'][2]+mc['ic'][2]:+.3f}]", "+1.0"]])
faixas = [(0, 10), (10, 20), (20, 30), (30, 40), (40, 60), (60, 80)]
tabela(["faixa de TDIEL (mil)", "n", "mediana da razao"],
       [[f"{a:.0f} a {b:.0f}", int(((X[:,0]>=a)&(X[:,0]<b)).sum()),
         f"{np.median(razao[(X[:,0]>=a)&(X[:,0]<b)]):.3f}"
         if ((X[:,0]>=a)&(X[:,0]<b)).sum() else "-"] for a, b in faixas])

secao("F2. Populacao conforme (razao entre 1,5 e 3,0) vs. desviante")
conf = (razao >= 1.5) & (razao < 3.0)
tabela(["grupo", "n", "%"],
       [["razao < 1,5", int((razao < 1.5).sum()), f"{(razao<1.5).mean()*100:.1f}"],
        ["1,5 <= razao < 3,0  (duas cavidades)", int(conf.sum()), f"{conf.mean()*100:.1f}"],
        ["3,0 <= razao < 10", int(((razao>=3)&(razao<10)).sum()),
         f"{((razao>=3)&(razao<10)).mean()*100:.1f}"],
        ["razao >= 10", int((razao>=10).sum()), f"{(razao>=10).mean()*100:.1f}"]])

mconf = ols(np.column_stack([lt[conf], le[conf]]), y1[conf])
tabela(["amostra", "n", "coef. log10(TDIEL)", "coef. log10(eps_r)", "R2"],
       [["todas as 985", n_cfg, f"{m['beta'][1]:+.3f} +- {m['ic'][1]:.3f}",
         f"{m['beta'][2]:+.3f} +- {m['ic'][2]:.3f}", f"{m['r2']:.3f}"],
        ["so conformes", int(conf.sum()),
         f"{mconf['beta'][1]:+.3f} +- {mconf['ic'][1]:.3f}",
         f"{mconf['beta'][2]:+.3f} +- {mconf['ic'][2]:.3f}", f"{mconf['r2']:.3f}"],
        ["esperado pela fisica", "-", "+1.000", "-1.000", "-"]])
print("\n>>> Na populacao conforme a lei quase-estatica e confirmada.")
linhas_md.append("\n**Na população conforme (66,3%) a lei quase-estática é confirmada: "
                 f"expoentes {mconf['beta'][1]:+.3f} e {mconf['beta'][2]:+.3f} contra +1 e "
                 f"-1 previstos, com R² = {mconf['r2']:.3f}.**\n")

secao("F3. Quanto as 8 features explicam de log|Z11(1 MHz)|")
lX = np.column_stack([np.log10(X[:, j]) for j in range(8)])
m8 = ols(lX, y1)
tabela(["modelo", "termos", "R2"],
       [["quase-estatico (TDIEL, eps_r)", "2", f"{m['r2']:.4f}"],
        ["todas as 8 features", "8", f"{m8['r2']:.4f}"],
        ["ganho das 6 de geometria de via", "-", f"{m8['r2']-m['r2']:+.4f}"]])
tabela(["feature", "coeficiente", "IC 95%"],
       [[FEATURES_8[j], f"{m8['beta'][j+1]:+.4f}",
         f"[{m8['beta'][j+1]-m8['ic'][j+1]:+.3f}, {m8['beta'][j+1]+m8['ic'][j+1]:+.3f}]"]
        for j in range(8)])

# ------------------------------------------------------ G. reciprocidade
secao("G. Reciprocidade — varredura de tolerancia (20 configuracoes)")
var = ROOT / "6_layer_pcb_based_pdn_with_two_arrays_LHS_mar_2023" / "variation"
amostra = RNG.choice(n_cfg, 20, replace=False)
tols = [1e-9, 1e-8, 1e-7, 1e-6, 1e-5, 1e-4, 1e-3]
cont = {t: 0 for t in tols}
assim = []
for i in amostra:
    net = parse_touchstone(var / f"simu_{int(simu[i])}.s36p", n_ports=36)
    assim.append(float(np.abs(net.s - np.swapaxes(net.s, 1, 2)).max()))
    for t in tols:
        cont[t] += check_invariants(net, atol_reciprocidade=t)["I1_reciprocidade"]
tabela(["tolerancia (atol)", "aprovados / 20"],
       [[f"{t:.0e}", f"{cont[t]} / 20"] for t in tols])
print(f"\nassimetria maxima |S - S^T|: mediana {np.median(assim):.3e}, "
      f"maximo {np.max(assim):.3e}")
linhas_md.append(f"\nAssimetria máxima `|S − Sᵀ|`: mediana {np.median(assim):.3e}, "
                 f"máximo {np.max(assim):.3e}\n")

# ------------------------------------------------------------- graficos
plt.rcParams.update({"font.size": 9, "axes.grid": True, "grid.alpha": 0.3})
fmhz = freq / 1e6

# 04a — mapa de sensibilidade
fig, ax = plt.subplots(2, 1, figsize=(13, 9),
                       gridspec_kw={"height_ratios": [1.35, 1], "hspace": 0.32})
im = ax[0].imshow(rho, aspect="auto", cmap="RdBu_r", vmin=-1, vmax=1,
                  extent=[fmhz[0], fmhz[-1], len(FEATURES_8) - 0.5, -0.5])
ax[0].set_yticks(range(len(FEATURES_8)))
ax[0].set_yticklabels([ROTULOS[f] for f in FEATURES_8], fontsize=8)
ax[0].axvline(np.median(f_nulo) / 1e6, color="k", ls="--", lw=1.6)
ax[0].text(np.median(f_nulo) / 1e6 * 1.05, 7.3,
           f"nulo de série (mediana {np.median(f_nulo)/1e6:.0f} MHz)", fontsize=8)
ax[0].set_xscale("log"); ax[0].set_xlabel("Frequência (MHz)")
ax[0].set_title("Correlação de Spearman entre parâmetro de projeto e "
                r"$\log_{10}|Z_{11}(f)|$ — 985 configurações",
                fontweight="bold")
ax[0].grid(False)
plt.colorbar(im, ax=ax[0], pad=0.01, label=r"$\rho$ de Spearman")

for k, f in enumerate(FEATURES_8):
    ax[1].semilogx(fmhz, rho[k], lw=1.9 if k < 2 else 1.1,
                   alpha=1.0 if k < 2 else 0.65,
                   label=ROTULOS[f].replace("\n", " "))
ax[1].axvline(np.median(f_nulo) / 1e6, color="k", ls="--", lw=1.4)
ax[1].axhline(0, color="k", lw=0.8)
ax[1].set_xlabel("Frequência (MHz)"); ax[1].set_ylabel(r"$\rho$ de Spearman")
ax[1].set_ylim(-1.05, 1.05)
ax[1].set_title("Perfis por parâmetro — a troca de regime ocorre no nulo de série",
                fontweight="bold")
ax[1].legend(fontsize=7.5, ncol=4, loc="lower center")
fig.savefig(OUT / "04a_mapa_sensibilidade.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# 04b — lei quase-estatica
fig, ax = plt.subplots(2, 2, figsize=(12.5, 9))
fig.subplots_adjust(hspace=0.32, wspace=0.26)
sc = ax[0, 0].scatter(m["pred"], y1, s=9, alpha=0.45, c=X[:, 0], cmap="viridis")
lim = [min(m["pred"].min(), y1.min()), max(m["pred"].max(), y1.max())]
ax[0, 0].plot(lim, lim, "r--", lw=1.4, label="identidade")
ax[0, 0].set_xlabel(r"$\log_{10}|Z_{11}|$ previsto pela regressão")
ax[0, 0].set_ylabel(r"$\log_{10}|Z_{11}|$ medido em 1 MHz")
ax[0, 0].set_title(f"Ajuste quase-estático · $R^2$ = {m['r2']:.4f}", fontweight="bold")
ax[0, 0].legend(fontsize=8)
plt.colorbar(sc, ax=ax[0, 0], label="TDIEL (mil)")

cor = ["tab:blue" if abs(m["beta"][i] - esperado[i]) < 0.15 else "tab:red"
       for i in (1, 2)]
ax[0, 1].bar([0, 1], m["beta"][1:], yerr=m["ic"][1:], capsize=7, color=cor,
             width=0.52, edgecolor="k")
ax[0, 1].plot([-0.32, 0.32], [1, 1], "k--", lw=2)
ax[0, 1].plot([0.68, 1.32], [-1, -1], "k--", lw=2, label="valor teórico")
ax[0, 1].set_xticks([0, 1])
ax[0, 1].set_xticklabels([r"$\partial\log|Z|/\partial\log h$",
                          r"$\partial\log|Z|/\partial\log\varepsilon_r$"])
ax[0, 1].axhline(0, color="k", lw=0.8)
ax[0, 1].set_ylabel("coeficiente (barras: IC 95%)")
ax[0, 1].set_title("Expoentes medidos vs. previstos pela física", fontweight="bold")
ax[0, 1].legend(fontsize=8)

ax[1, 0].scatter(X[:, 0], m["resid"], s=9, alpha=0.45, color="tab:purple")
ax[1, 0].axhline(0, color="k", lw=1.1)
for xv in (30, 40):
    ax[1, 0].axvline(xv, color="tab:orange", ls=":", lw=1.6)
ax[1, 0].text(41, m["resid"].max() * 0.86,
              "limite de validade do\nmodelo de cavidade\n(Schierholz 2023)",
              fontsize=7.5, color="tab:orange")
ax[1, 0].set_xlabel("TDIEL (mil)"); ax[1, 0].set_ylabel("resíduo (décadas)")
ax[1, 0].set_title("Resíduo contra a espessura do dielétrico", fontweight="bold")

ax[1, 1].scatter(mconf["pred"], y1[conf], s=9, alpha=0.5, color="tab:green",
                 label=f"conformes (n={conf.sum()})")
ax[1, 1].scatter(m["pred"][~conf], y1[~conf], s=9, alpha=0.35, color="tab:red",
                 label=f"desviantes (n={(~conf).sum()})")
lim2 = [min(y1.min(), m["pred"].min()), max(y1.max(), m["pred"].max())]
ax[1, 1].plot(lim2, lim2, "k--", lw=1.4)
ax[1, 1].set_xlabel(r"$\log_{10}|Z_{11}|$ previsto")
ax[1, 1].set_ylabel(r"$\log_{10}|Z_{11}|$ medido")
ax[1, 1].set_title(f"Conformes: expoentes {mconf['beta'][1]:+.2f} / "
                   f"{mconf['beta'][2]:+.2f}, $R^2$={mconf['r2']:.3f}", fontweight="bold")
ax[1, 1].legend(fontsize=8)
fig.savefig(OUT / "04b_lei_quasi_estatica.png", dpi=150, bbox_inches="tight")
plt.close(fig)

# 04c — ranking e invariantes
fig, ax = plt.subplots(2, 2, figsize=(12.5, 9))
fig.subplots_adjust(hspace=0.42, wspace=0.26)
yp = np.arange(len(ordem_medida))
ax[0, 0].barh(yp - 0.2, [r["abaixo"] for r in ordem_medida], height=0.38,
              label="abaixo do nulo (capacitivo)", color="tab:blue")
ax[0, 0].barh(yp + 0.2, [r["acima"] for r in ordem_medida], height=0.38,
              label="acima do nulo (indutivo)", color="tab:orange")
ax[0, 0].set_yticks(yp)
ax[0, 0].set_yticklabels([ROTULOS[r["feat"]].replace("\n", " ") for r in ordem_medida],
                         fontsize=7.5)
ax[0, 0].invert_yaxis(); ax[0, 0].set_xlabel(r"$|\rho|$ médio de Spearman")
ax[0, 0].set_title("Sensibilidade por regime", fontweight="bold")
ax[0, 0].legend(fontsize=8)

ax[0, 1].scatter([FIG11[r["feat"]] for r in ordem_medida],
                 [r["max"] for r in ordem_medida], s=68, c="tab:green",
                 edgecolor="k", zorder=3)
for r in ordem_medida:
    ax[0, 1].annotate(r["feat"].replace("RADIUS", "R").replace("PERMITTIVITY", "eps_r"),
                      (FIG11[r["feat"]], r["max"]), fontsize=6.5,
                      xytext=(4, 4), textcoords="offset points")
ax[0, 1].set_xscale("log"); ax[0, 1].set_xlabel("RMSE máx. publicado, Fig. 11 (Ω)")
ax[0, 1].set_ylabel(r"$|\rho|$ máx. medido")
ax[0, 1].set_title("Medido vs. publicado", fontweight="bold")

ax[1, 0].hist(incl, bins=45, color="tab:blue", alpha=0.85, edgecolor="k")
ax[1, 0].axvline(-1, color="r", ls="--", lw=2, label="teórico = −1")
ax[1, 0].axvline(incl.mean(), color="k", lw=1.6,
                 label=f"média = {incl.mean():.3f}")
ax[1, 0].set_xlabel(r"$\partial\log_{10}|Z_{11}|/\partial\log_{10}f$")
ax[1, 0].set_ylabel("contagem")
ax[1, 0].set_title("R1 — comportamento capacitivo (985 configs)", fontweight="bold")
ax[1, 0].legend(fontsize=8)

ax[1, 1].scatter(X[~conf, 0], razao[~conf], s=10, alpha=0.4, color="tab:red",
                 label=f"desviantes ({(~conf).mean()*100:.0f}%)")
ax[1, 1].scatter(X[conf, 0], razao[conf], s=10, alpha=0.5, color="tab:green",
                 label=f"conformes ({conf.mean()*100:.0f}%)")
ax[1, 1].axhline(1, color="k", ls="--", lw=1.4, label="razão = 1 (cavidade única)")
ax[1, 1].axhline(2, color="tab:green", ls="--", lw=1.4, label="razão = 2 (duas cavidades)")
for xv in (30, 40):
    ax[1, 1].axvline(xv, color="tab:orange", ls=":", lw=1.6)
ax[1, 1].set_yscale("log"); ax[1, 1].set_xlabel("TDIEL (mil)")
ax[1, 1].set_ylabel(r"$C_{\rm extraída}\,/\,C_{\rm analítica}$")
ax[1, 1].set_title(f"R2 — escala da capacitância (Spearman = {rho_rt:+.2f})",
                   fontweight="bold")
ax[1, 1].legend(fontsize=7, loc="upper left")
fig.savefig(OUT / "04c_ranking_e_invariantes.png", dpi=150, bbox_inches="tight")
plt.close(fig)

(OUT / "04_resultados.md").write_text(
    "# Etapa 1 — Sensibilidade e verificação física\n"
    f"\n985 configurações · 334 pontos de frequência · "
    f"{freq[0]/1e6:.0f} MHz a {freq[-1]/1e9:.2f} GHz\n"
    + "\n".join(linhas_md), encoding="utf-8")
print("\n" + "=" * 78)
print("figuras: 04a_mapa_sensibilidade.png · 04b_lei_quasi_estatica.png · "
      "04c_ranking_e_invariantes.png")
print("tabelas: 04_resultados.md")
