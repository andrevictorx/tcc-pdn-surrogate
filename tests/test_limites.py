"""Testes de `src/normas/limites.py` contra os valores impressos nas tabelas das normas."""

from __future__ import annotations

import numpy as np
import pytest

from src.normas.limites import carregar, limite_dbuvm


@pytest.mark.parametrize("norma,tabela,f_mhz,esperado", [
    ("CISPR 32:2015", "A4.1", 100, 30), ("CISPR 32:2015", "A4.1", 500, 37),
    ("CISPR 32:2015", "A2.1", 100, 40), ("CISPR 32:2015", "A2.1", 500, 47),
    ("CISPR 32:2015", "A4.4", 30, 42), ("CISPR 32:2015", "A4.4", 1000, 42),
    ("IEC 61000-6-4:2018", "3.3", 30, 52),
])
def test_valores_das_tabelas(norma, tabela, f_mhz, esperado):
    assert limite_dbuvm(f_mhz * 1e6, norma, tabela)[0] == pytest.approx(esperado)


def test_na_transicao_vale_o_limite_mais_baixo():
    assert limite_dbuvm(230e6, "CISPR 32:2015", "A4.1")[0] == pytest.approx(30)
    assert limite_dbuvm(230e6, "CISPR 32:2015", "A4.4")[0] == pytest.approx(35)


def test_variacao_linear_no_logaritmo_da_frequencia():
    f_meio = np.sqrt(30 * 230) * 1e6
    assert limite_dbuvm(f_meio, "CISPR 32:2015", "A4.4")[0] == pytest.approx(38.5)


def test_fora_da_banda_e_nan():
    assert np.isnan(limite_dbuvm([1e6, 2e9], "CISPR 32:2015", "A4.1")).all()


def test_classe_b_igual_a_61000_6_3_e_classe_a_igual_a_61000_6_4():
    f = np.geomspace(30e6, 1e9, 200)
    np.testing.assert_allclose(limite_dbuvm(f, "CISPR 32:2015", "A4.1"), limite_dbuvm(f, "IEC 61000-6-3:2020", "3.1"))
    np.testing.assert_allclose(limite_dbuvm(f, "CISPR 32:2015", "A2.4"), limite_dbuvm(f, "IEC 61000-6-4:2018", "3.3"))


def test_classe_a_e_10_db_acima_da_classe_b():
    f = np.geomspace(30e6, 1e9, 200)
    np.testing.assert_allclose(limite_dbuvm(f, "CISPR 32:2015", "A2.1") - limite_dbuvm(f, "CISPR 32:2015", "A4.1"), 10)


def test_tabela_sem_lacunas_de_30_mhz_a_1_ghz():
    t = carregar()
    for (_, _), g in t.groupby(["norma", "tabela"]):
        g = g.sort_values("f_ini_MHz")
        assert g.f_ini_MHz.iloc[0] == 30 and g.f_fim_MHz.iloc[-1] == 1000
        assert np.all(g.f_ini_MHz.values[1:] == g.f_fim_MHz.values[:-1])
