"""Testes de `src/data/consistencia.py`: casos analíticos (RLC série) e as bases reais, se presentes."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from src.data.consistencia import (
    EPS_0,
    acoplamento_modal,
    capacitancia_medida,
    frequencia_modal,
    inclinacao_quase_estatica,
    monotonica_ate_nulo,
    portoes,
    resumo,
)
from src.data.touchstone import primeiro_minimo

FREQ = np.linspace(1e6, 1e9, 334)
CACHE = Path(__file__).resolve().parents[1] / "data/processed"


def rlc(R=5e-3, L=1e-9, C=10e-9, f=FREQ):
    w = 2 * np.pi * f
    return R + 1j * w * L + 1 / (1j * w * C)


def test_inclinacao_de_capacitor_ideal_e_menos_um():
    f = np.geomspace(1e6, 1e9, 400)
    z = np.abs(rlc(R=0, L=1e-9, C=10e-9, f=f))          # f0 = 50 MHz: janela até 17 MHz, (f/f0)² ≤ 0,11
    s, n = inclinacao_quase_estatica(f, z)
    assert s == pytest.approx(-1, abs=0.05) and n >= 3


def test_primeiro_minimo_de_rlc_esta_na_ressonancia():
    L, C = 1e-9, 10e-9
    f0 = 1 / (2 * np.pi * np.sqrt(L * C))
    passo = FREQ[1] - FREQ[0]
    assert abs(FREQ[primeiro_minimo(np.abs(rlc(L=L, C=C)))] - f0) <= passo


def test_primeiro_minimo_antes_do_global_quando_ha_antirressonancia():
    z = np.abs(rlc(L=1e-9, C=10e-9)) * (1 + 0.9 * np.exp(-((FREQ - 20e6) / 2e6) ** 2))
    z[(FREQ > 15e6) & (FREQ < 18e6)] *= 0.01
    assert primeiro_minimo(z) < int(np.argmin(np.abs(rlc(L=1e-9, C=10e-9))))


def test_capacitancia_medida_recupera_c_mesmo_perto_da_ressonancia():
    assert capacitancia_medida(FREQ, rlc(C=10e-9)) == pytest.approx(10e-9, rel=0.02)
    assert capacitancia_medida(FREQ, rlc(L=10e-9, C=50e-9)) == pytest.approx(50e-9, rel=0.05)   # f0 = 7 MHz


def test_capacitancia_medida_ignora_excesso_de_parte_real_em_1MHz():
    z = rlc(C=50e-9)
    z[0] += 10.0                                          # artefato de baixa frequência
    assert capacitancia_medida(FREQ, z) == pytest.approx(50e-9, rel=0.05)


def test_monotonicidade_rlc():
    assert monotonica_ate_nulo(np.abs(rlc()))


def test_acoplamento_no_no_e_zero():
    assert acoplamento_modal(1, 0, 0.5, 0.3) == pytest.approx(0, abs=1e-12)
    assert acoplamento_modal(2, 0, 0.5, 0.3) == pytest.approx(1)


def test_frequencia_modal_tm10():
    assert frequencia_modal(1, 0, 4.0, 0.1, 0.2) == pytest.approx(299792458.0 / (2 * 2 * 0.1))


def test_portoes_aprovam_rlc_coerente_e_rejeitam_incoerente():
    A, h, er = 0.01, 100e-6, 4.0
    C = EPS_0 * er * A / h
    z = np.vstack([rlc(C=C), rlc(C=C), rlc(C=3 * C), -rlc(C=C).real + 1j * rlc(C=C).imag])
    df = portoes(FREQ, z, er, A, h, n_pg=1)
    assert df["C1_ok"].tolist() == [True, True, False, True]
    assert df["C7_passiva"].tolist() == [True, True, True, False]
    assert df["incluir_treino"].tolist() == [True, True, False, False]


# --- bases reais ------------------------------------------------------------------------

def _pi1():
    from src.data.subsets import UMA_CAVIDADE
    d = np.load(CACHE / "pi1_cache.npz")
    X = d["X"].astype(float)
    z = d["zabs"].astype(float) * np.exp(1j * d["zang"].astype(float))
    return d["freq"], z, X, UMA_CAVIDADE


@pytest.mark.skipif(not (CACHE / "pi1_cache.npz").exists(), reason="cache do PI-1 ausente")
def test_pi1_h1_e_h3_aceitas_com_espessura_efetiva():
    freq, z, X, ad = _pi1()
    rng = np.random.default_rng(0)
    i = rng.choice(len(z), 3000, replace=False)
    df = portoes(freq, z[i], X[i, 1], ad.x_width_m * ad.y_width_m, ad.espessura_efetiva_m(X[i, 0]),
                 ad.n_cavidades_alim_terra, c_decaps=X[i, 3], tem_decaps=True)
    r = resumo(df)
    assert r["H1_aceita"] and r["H3_aceita"] and r["H4_aceita"]


@pytest.mark.skipif(not (CACHE / "pi4_cache.npz").exists(), reason="cache do PI-4 ausente")
def test_pi4_planilha_corrigida_passa_c1_e_original_nao():
    from src.data.subsets import SEIS_CAMADAS as ad
    d = np.load(CACHE / "pi4_cache.npz")
    if "X_corrigido" not in d.files:
        pytest.skip("cache sem a planilha corrigida")
    z, freq = d["z11"].astype(complex), d["freq"]
    area = ad.x_width_m * ad.y_width_m
    corr = portoes(freq, z, d["X_corrigido"][:, 1], area, ad.espessura_efetiva_m(d["X_corrigido"][:, 0]), 2)
    orig = portoes(freq, z, d["X"][:, 1], area, ad.espessura_efetiva_m(d["X"][:, 0]), 2)
    assert corr["C1_ok"].mean() > 0.99
    assert orig["C1_ok"].mean() < 0.80
