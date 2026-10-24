"""Testes de `src/data/alvos.py`."""

from __future__ import annotations

import numpy as np
import pytest

from src.data.alvos import zmax_4mhz, zmax_extrapolado

FREQ = np.linspace(1e6, 1e9, 334)


def rlc(R=5e-3, L=1e-9, C=10e-9, f=FREQ):
    w = 2 * np.pi * f
    return R + 1j * w * L + 1 / (1j * w * C)


def test_extrapolado_reproduz_lc_em_1mhz():
    L, C = 1e-9, 10e-9
    f0 = 1 / (2 * np.pi * np.sqrt(L * C))
    esperado = (1 - (1e6 / f0) ** 2) / (2 * np.pi * 1e6 * C)
    assert zmax_extrapolado(FREQ, rlc(L=L, C=C)) == pytest.approx(esperado, rel=0.02)


def test_extrapolado_ignora_anomalia_no_ponto_de_1mhz():
    z = rlc()
    limpo = zmax_extrapolado(FREQ, z)
    z = z.copy()
    z[0] = 10.0 + 0.8 * z[0].imag * 1j
    assert zmax_extrapolado(FREQ, z) == pytest.approx(limpo, rel=1e-9)


def test_4mhz_interpola_em_log_log():
    z = rlc(R=0, L=1e-15)
    assert zmax_4mhz(FREQ, z) == pytest.approx(1 / (2 * np.pi * 4.34e6 * 10e-9), rel=0.01)
