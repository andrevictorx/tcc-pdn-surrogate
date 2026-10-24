"""Curvas-limite de emissão irradiada de 30 MHz a 1 GHz (`spec/NORMAS.md`).

Regras das normas aplicadas aqui (IEC 61000-6-3:2020 e 61000-6-4:2018, requisitos gerais de emissão):
- onde o limite varia numa faixa, ele muda linearmente com o logaritmo da frequência;
- na frequência de transição entre duas faixas, vale o limite mais baixo.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

ARQUIVO = Path(__file__).resolve().parents[2] / "data/normas/limites_emissao_irradiada.csv"


def carregar(arquivo: Path = ARQUIVO) -> pd.DataFrame:
    """Tabela de faixas: uma linha por (norma, tabela, faixa de frequência)."""
    return pd.read_csv(arquivo)


def limite_dbuvm(freq_hz, norma: str, tabela: str, faixas: pd.DataFrame | None = None) -> np.ndarray:
    """Limite em dB(µV/m) da cláusula `tabela` de `norma`, nas frequências dadas.

    Fora de 30 MHz–1 GHz o resultado é NaN: a norma não define limite irradiado ali.
    """
    faixas = carregar() if faixas is None else faixas
    sel = faixas[(faixas["norma"] == norma) & (faixas["tabela"] == tabela)]
    if sel.empty:
        raise KeyError(f"{norma}, cláusula {tabela}: não tabelada")
    f_mhz = np.atleast_1d(np.asarray(freq_hz, float)) / 1e6
    saida = np.full(f_mhz.shape, np.nan)
    for _, r in sel.iterrows():
        m = (f_mhz >= r.f_ini_MHz) & (f_mhz <= r.f_fim_MHz)
        t = (np.log10(f_mhz[m]) - np.log10(r.f_ini_MHz)) / (np.log10(r.f_fim_MHz) - np.log10(r.f_ini_MHz))
        valor = r.limite_ini_dBuVm + t * (r.limite_fim_dBuVm - r.limite_ini_dBuVm)
        saida[m] = np.fmin(saida[m], valor) if np.any(~np.isnan(saida[m])) else valor
    return saida
