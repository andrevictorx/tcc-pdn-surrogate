"""Portões de consistência dos dados e medidas das hipóteses H1–H5.

Implementa `spec/CONSISTENCIA_DADOS.md`. Cada função recebe arrays já reduzidos
(curvas de Z11 e parâmetros físicos) e devolve medidas por curva; a decisão de
excluir ou marcar uma linha fica em `portoes()`, que segue a tabela da Parte B.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .touchstone import primeiro_minimo

EPS_0 = 8.8541878128e-12
C_0 = 299792458.0

TOL_C1 = 0.25
FASE_CAPACITIVA_GRAUS = (-95.0, -80.0)
MIN_PONTOS_JANELA = 3
FATOR_JANELA = 3.0
TOL_PASSIVIDADE = 0.02
TOL_H1 = 0.10
FAIXA_H3 = (0.95, 1.15)


def inclinacao_quase_estatica(freq: np.ndarray, z_abs: np.ndarray) -> tuple[float, int]:
    """Inclinação log–log de |Z| em f < f_nulo/3, com f_nulo = primeiro mínimo local (H1).

    Returns:
        (inclinação, nº de pontos na janela). Com menos de 2 pontos, a inclinação é NaN.
    """
    janela = freq < freq[primeiro_minimo(z_abs)] / FATOR_JANELA
    n = int(janela.sum())
    if n < 2:
        return float("nan"), n
    return float(np.polyfit(np.log10(freq[janela]), np.log10(z_abs[janela]), 1)[0]), n


def capacitancia_medida(freq: np.ndarray, z: np.ndarray) -> float:
    """Capacitância da placa a partir de Im{Z}, com correção do LC série.

    Usa o ponto mais capacitivo (maior |Im|/Re) com f < f_nulo/2 e corrige a
    indutância pela ressonância série: Im{Z} = −(1 − (f/f0)²)/(ωC). Não usa só o
    ponto de 1 MHz porque ali a SI/PI-Database tem um excesso de parte real
    (~10 Ω no PI-4, independente da geometria, decaindo com f^−1,4) que distorce
    Im{Z} nas cavidades finas, onde a reatância é pequena.
    """
    f0 = freq[primeiro_minimo(np.abs(z))]
    janela = np.flatnonzero(freq < f0 / 2)
    if len(janela) == 0:
        janela = np.array([0])
    q = -z[janela].imag / np.maximum(z[janela].real, 1e-12)
    j = janela[int(np.argmax(q))]
    return float((1 - (freq[j] / f0) ** 2) / (-2 * np.pi * freq[j] * z[j].imag))


def capacitancia_prevista(eps_r, area_m2, h_ef_m, n_pg, c_decaps=0.0):
    """C = n_pg·ε0·εr·A/h_ef + C_decaps (H3)."""
    return n_pg * EPS_0 * np.asarray(eps_r) * np.asarray(area_m2) / np.asarray(h_ef_m) + c_decaps


def monotonica_ate_nulo(z_abs: np.ndarray) -> bool:
    """|Z| estritamente decrescente de 1 MHz até o mínimo global (H4)."""
    k = int(np.argmin(z_abs))
    return bool(k == 0 or np.all(np.diff(z_abs[: k + 1]) < 0))


def acoplamento_modal(m: int, n: int, u, v):
    """|cos(mπu)·cos(nπv)|: amplitude do modo TM_mn na posição relativa (u, v) da porta (H2)."""
    return np.abs(np.cos(m * np.pi * np.asarray(u)) * np.cos(n * np.pi * np.asarray(v)))


def frequencia_modal(m: int, n: int, eps_r, a_m, b_m):
    """f_mn = c0/(2√εr)·√((m/a)² + (n/b)²), em Hz."""
    return C_0 / (2 * np.sqrt(np.asarray(eps_r))) * np.hypot(m / np.asarray(a_m), n / np.asarray(b_m))


def portoes(freq: np.ndarray, z: np.ndarray, eps_r, area_m2, h_ef_m, n_pg: int,
            c_decaps=None, tem_decaps: bool = False) -> pd.DataFrame:
    """Aplica os portões C1, C5, C6 e C7 e mede H1, H3 e H4 em cada curva.

    Args:
        freq: grade, Hz, shape (nf,).
        z: Z11 complexo, shape (n, nf).
        eps_r, area_m2, h_ef_m: por curva (arrays de shape (n,)) ou escalares.
        n_pg: nº de cavidades alimentação–terra.
        c_decaps: capacitância total dos decaps por curva, F (None = 0).
        tem_decaps: se True, H4 não se aplica ao subconjunto (fora do domínio).

    Returns:
        Um DataFrame com uma linha por curva. `incluir_treino` = C1 e C7 aprovados;
        `elegivel_h1_h3` = C5 e C6 aprovados.
    """
    n = z.shape[0]
    z_abs = np.abs(z)
    c_dec = np.zeros(n) if c_decaps is None else np.asarray(c_decaps, float)
    eps_r, area_m2, h_ef_m = (np.broadcast_to(np.asarray(x, float), (n,)) for x in (eps_r, area_m2, h_ef_m))

    inclin, npts = zip(*(inclinacao_quase_estatica(freq, a) for a in z_abs))
    fase = np.degrees(np.angle(z[:, 0]))
    c_med = np.array([capacitancia_medida(freq, zz) for zz in z])
    c_prev = capacitancia_prevista(eps_r, area_m2, h_ef_m, n_pg, c_dec)
    razao = c_med / c_prev
    re_rel = (z.real / z_abs).min(axis=1)

    df = pd.DataFrame({
        "fase_1MHz_graus": fase,
        "n_pontos_janela": np.array(npts),
        "inclinacao_H1": np.array(inclin),
        "razao_C": razao,
        "re_min_relativo": re_rel,
        "monotonica_H4": [monotonica_ate_nulo(a) for a in z_abs],
    })
    df["C1_ok"] = np.abs(razao - 1) <= TOL_C1
    df["C5_janela_ok"] = df["n_pontos_janela"] >= MIN_PONTOS_JANELA
    lo, hi = FASE_CAPACITIVA_GRAUS
    df["C6_capacitivo"] = (fase > lo) & (fase < hi)
    df["C7_passiva"] = re_rel >= -TOL_PASSIVIDADE
    df["elegivel_h1_h3"] = df["C5_janela_ok"] & df["C6_capacitivo"]
    df["H1_ok"] = np.abs(df["inclinacao_H1"] + 1) <= TOL_H1
    df["incluir_treino"] = df["C1_ok"] & df["C7_passiva"]
    df.attrs["H4_aplicavel"] = not tem_decaps
    return df


def resumo(df: pd.DataFrame) -> dict[str, float]:
    """Taxas por hipótese e portão, com os critérios de aceitação da spec."""
    el = df["elegivel_h1_h3"]
    r = df.loc[el, "razao_C"]
    out = {
        "n_curvas": int(len(df)),
        "C1_excluidas": int((~df["C1_ok"]).sum()),
        "C7_excluidas": int((~df["C7_passiva"]).sum()),
        "elegiveis_H1_H3_pct": float(el.mean() * 100),
        "H1_pct_tol010": float(df.loc[el, "H1_ok"].mean() * 100),
        "H1_mediana": float(df.loc[el, "inclinacao_H1"].median()),
        "H3_razao_mediana": float(r.median()),
        "H4_pct": float(df["monotonica_H4"].mean() * 100),
        "H4_aplicavel": bool(df.attrs.get("H4_aplicavel", True)),
        "H5_pct": float((df["re_min_relativo"] >= 0).mean() * 100),
    }
    out["H1_aceita"] = out["H1_pct_tol010"] >= 95
    out["H3_aceita"] = FAIXA_H3[0] <= out["H3_razao_mediana"] <= FAIXA_H3[1]
    out["H4_aceita"] = (not out["H4_aplicavel"]) or out["H4_pct"] >= 99.9
    out["H5_aceita"] = out["C7_excluidas"] == 0 or out["C7_excluidas"] / out["n_curvas"] < 1e-3
    return out
