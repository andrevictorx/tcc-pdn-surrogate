"""Definições operacionais dos alvos derivados da curva de impedância (`spec/ALVO_ZMAX.md`)."""

from __future__ import annotations

import numpy as np

from .touchstone import primeiro_minimo

F_REF_HZ = 1e6
F_SENSIBILIDADE_HZ = 4.34e6
FATOR_JANELA = 3.0


def zmax_extrapolado(freq: np.ndarray, z: np.ndarray, f_ref: float = F_REF_HZ) -> float:
    """|Z|max pela lei capacitiva com correção do LC série, sem usar o ponto de 1 MHz (definição principal).

    Args:
        freq: grade, Hz, shape (nf,).
        z: Z11 complexo de uma curva, shape (nf,).
        f_ref: frequência em que o alvo é avaliado.

    Returns:
        |Z| previsto em f_ref, em ohms.
    """
    f0 = freq[primeiro_minimo(np.abs(z))]
    janela = np.flatnonzero((freq < f0 / FATOR_JANELA) & (np.arange(len(freq)) > 0))
    if len(janela) == 0:
        janela = np.array([1])
    w = 2 * np.pi * freq[janela]
    c = float(np.median((1 - (freq[janela] / f0) ** 2) / (-w * z[janela].imag)))
    return float((1 - (f_ref / f0) ** 2) / (2 * np.pi * f_ref * c))


def zmax_4mhz(freq: np.ndarray, z: np.ndarray, f: float = F_SENSIBILIDADE_HZ) -> float:
    """|Z| interpolado em log–log em 4,34 MHz (definição de sensibilidade)."""
    return float(10 ** np.interp(np.log10(f), np.log10(freq), np.log10(np.abs(z))))
