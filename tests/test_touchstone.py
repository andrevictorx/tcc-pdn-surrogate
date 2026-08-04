"""Testes de `src/data/touchstone.py` contra `spec/DATA_SPEC.md`.

Organizados nas três categorias exigidas pelo Apêndice A da proposta:
forma/tipo, invariante física e caso analítico. A terceira é a única capaz de
detectar erros de unidade e de fator constante, aos quais as duas primeiras são
cegas.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import numpy as np
import pytest

from src.data.touchstone import (
    MIL_TO_M,
    Network,
    cavity_modes,
    check_invariants,
    low_frequency_slope,
    mil_to_m,
    parse_touchstone,
    plate_capacitance,
    s_to_z,
    self_impedance,
)

A_MIL, B_MIL = 5800.0, 4000.0
EPS_0 = 8.8541878128e-12
C_0 = 299792458.0


# --------------------------------------------------------------------------
# auxiliares
# --------------------------------------------------------------------------

def _write_touchstone(tmp_path: Path, freq: np.ndarray, s: np.ndarray) -> Path:
    """Escreve um Touchstone RI válido, quebrando linhas a cada 4 pares."""
    path = tmp_path / "caso.s2p"
    lines = ["! Touchstone Version 1.1", "#   Hz S RI R   50.00"]
    for k, f in enumerate(freq):
        flat = []
        for i in range(s.shape[1]):
            for j in range(s.shape[2]):
                flat += [s[k, i, j].real, s[k, i, j].imag]
        tokens = [f"{f:.16E}"] + [f"{v:.16E}" for v in flat]
        # primeira linha: frequência + 4 pares; demais: 4 pares
        lines.append(" " + " ".join(tokens[:9]))
        rest = tokens[9:]
        while rest:
            lines.append(" " * 26 + " ".join(rest[:8]))
            rest = rest[8:]
    path.write_text("\n".join(lines) + "\n")
    return path


def _series_rlc_network(freq: np.ndarray, r: float, l: float, c: float) -> Network:
    """Rede de 1 porta terminada por um RLC série, em parâmetros S."""
    w = 2 * np.pi * freq
    z = r + 1j * w * l + 1 / (1j * w * c)
    s11 = (z - 50.0) / (z + 50.0)
    return Network(freq=freq, s=s11.reshape(-1, 1, 1))


# --------------------------------------------------------------------------
# 1. testes de forma e tipo
# --------------------------------------------------------------------------

class TestFormaETipo:
    def test_parse_devolve_formas_corretas(self, tmp_path):
        freq = np.array([1e6, 2e6, 3e6])
        rng = np.random.default_rng(0)
        s = 0.1 * (rng.random((3, 2, 2)) + 1j * rng.random((3, 2, 2)))
        net = parse_touchstone(_write_touchstone(tmp_path, freq, s), n_ports=2)

        assert net.freq.shape == (3,)
        assert net.s.shape == (3, 2, 2)
        assert net.n_ports == 2 and net.n_freq == 3
        assert np.iscomplexobj(net.s)
        np.testing.assert_allclose(net.freq, freq)
        np.testing.assert_allclose(net.s, s, atol=1e-12)

    def test_s_to_z_preserva_forma(self):
        freq = np.logspace(6, 9, 20)
        net = _series_rlc_network(freq, 0.1, 1e-9, 1e-9)
        assert s_to_z(net).shape == (20, 1, 1)

    def test_self_impedance_e_vetor_complexo(self):
        freq = np.logspace(6, 9, 12)
        z = self_impedance(_series_rlc_network(freq, 0.1, 1e-9, 1e-9))
        assert z.shape == (12,) and np.iscomplexobj(z)

    def test_contagem_incompativel_e_erro(self, tmp_path):
        path = tmp_path / "ruim.s2p"
        path.write_text("! cab\n#   Hz S RI R   50.00\n 1.0 0.1 0.2 0.3\n")
        with pytest.raises(ValueError, match="não são múltiplos"):
            parse_touchstone(path, n_ports=2)

    def test_frequencia_nao_crescente_e_erro(self, tmp_path):
        freq = np.array([3e6, 1e6])
        s = np.zeros((2, 1, 1), dtype=complex)
        with pytest.raises(ValueError, match="crescente"):
            parse_touchstone(_write_touchstone(tmp_path, freq, s), n_ports=1)


# --------------------------------------------------------------------------
# 2. testes de invariante física
# --------------------------------------------------------------------------

class TestInvariantes:
    def test_rede_passiva_satisfaz_invariantes(self):
        freq = np.logspace(6, 9, 40)
        # 2 portas recíprocas e passivas por construção
        s11 = 0.3 * np.exp(-1j * 2 * np.pi * freq / 1e10)
        s21 = 0.2 * np.exp(-1j * 2 * np.pi * freq / 1e10)
        s = np.zeros((freq.size, 2, 2), dtype=complex)
        s[:, 0, 0] = s[:, 1, 1] = s11
        s[:, 0, 1] = s[:, 1, 0] = s21

        result = check_invariants(Network(freq=freq, s=s))
        assert all(result.values()), result

    def test_passividade_detecta_violacao(self):
        freq = np.logspace(6, 9, 10)
        s = np.full((10, 1, 1), 1.8 + 0j)  # |S| > 1: rede ativa
        result = check_invariants(Network(freq=freq, s=s))
        assert not result["I2_passividade_S"]

    def test_reciprocidade_detecta_assimetria(self):
        freq = np.logspace(6, 9, 10)
        s = np.zeros((10, 2, 2), dtype=complex)
        s[:, 0, 1] = 0.2
        s[:, 1, 0] = 0.5  # assimétrico
        assert not check_invariants(Network(freq=freq, s=s))["I1_reciprocidade"]

    def test_parte_real_da_impedancia_nao_negativa(self):
        freq = np.logspace(6, 9, 50)
        z = self_impedance(_series_rlc_network(freq, 0.5, 1e-9, 1e-9))
        assert np.all(z.real >= -1e-9)


# --------------------------------------------------------------------------
# 3. testes de caso analítico
# --------------------------------------------------------------------------

class TestCasosAnaliticos:
    def test_s_to_z_recupera_rlc_serie(self):
        """Ida e volta S -> Z sobre carga de valor conhecido."""
        freq = np.logspace(6, 9, 60)
        r, l, c = 0.25, 2e-9, 5e-10
        z = self_impedance(_series_rlc_network(freq, r, l, c))
        w = 2 * np.pi * freq
        esperado = r + 1j * w * l + 1 / (1j * w * c)
        np.testing.assert_allclose(z, esperado, rtol=1e-9)

    def test_carga_casada_da_impedancia_de_referencia(self):
        """S = 0 corresponde a Z = Z0. Detecta fator ausente na conversão."""
        freq = np.array([1e6, 1e9])
        z = s_to_z(Network(freq=freq, s=np.zeros((2, 1, 1), dtype=complex)))
        np.testing.assert_allclose(z[:, 0, 0].real, 50.0)

    def test_inclinacao_capacitiva_vale_menos_um(self):
        """Invariante I6: capacitor puro tem inclinação log-log exatamente -1."""
        freq = np.linspace(1e6, 25e6, 8)
        z_abs = 1 / (2 * np.pi * freq * 1e-9)
        assert low_frequency_slope(freq, z_abs) == pytest.approx(-1.0, abs=1e-9)

    def test_inclinacao_indutiva_vale_mais_um(self):
        freq = np.linspace(1e6, 25e6, 8)
        z_abs = 2 * np.pi * freq * 1e-9
        assert low_frequency_slope(freq, z_abs) == pytest.approx(+1.0, abs=1e-9)

    def test_capacitancia_de_placas_valor_conhecido(self):
        """1 m^2, 1 mm, vácuo -> C = eps_0 / 1e-3. Detecta erro de unidade."""
        c = plate_capacitance(eps_r=1.0, width_m=1.0, length_m=1.0, height_m=1e-3)
        assert c == pytest.approx(EPS_0 / 1e-3, rel=1e-12)

    def test_capacitancia_escala_com_parametros(self):
        base = plate_capacitance(3.0, 0.1, 0.1, 1e-4)
        assert plate_capacitance(6.0, 0.1, 0.1, 1e-4) == pytest.approx(2 * base)
        assert plate_capacitance(3.0, 0.1, 0.1, 2e-4) == pytest.approx(base / 2)

    def test_primeiro_modo_da_cavidade(self):
        """TM100 = c0 / (2 a sqrt(eps_r)), verificado com valores da base."""
        a, b = mil_to_m(A_MIL), mil_to_m(B_MIL)
        modes = cavity_modes(eps_r=2.5, width_m=a, length_m=b, f_max=1e9)
        assert modes[0] == pytest.approx(C_0 / (2 * a * np.sqrt(2.5)), rel=1e-12)
        assert modes[0] / 1e6 == pytest.approx(644.0, abs=1.0)

    def test_modos_da_base_caem_na_banda(self):
        """Faixa reportada na proposta: TM100 entre 480 e 644 MHz."""
        a, b = mil_to_m(A_MIL), mil_to_m(B_MIL)
        f_baixo = cavity_modes(4.5, a, b, 1e9)[0] / 1e6
        f_alto = cavity_modes(2.5, a, b, 1e9)[0] / 1e6
        assert f_baixo == pytest.approx(480.0, abs=1.0)
        assert f_alto == pytest.approx(644.0, abs=1.0)

    def test_conversao_de_unidade(self):
        assert mil_to_m(1.0) == pytest.approx(25.4e-6)
        assert mil_to_m(A_MIL) == pytest.approx(0.147320, abs=1e-6)


# --------------------------------------------------------------------------
# 4. teste sobre a base real (pulado se ausente)
# --------------------------------------------------------------------------

DATASET = Path(
    "/home/andre/Downloads/TCC/6_layer_pcb_based_pdn_with_two_arrays_LHS_mar_2023"
)


@pytest.mark.skipif(not DATASET.exists(), reason="base de dados não disponível")
class TestBaseReal:
    def test_dimensoes_declaradas_na_spec(self):
        net = parse_touchstone(DATASET / "variation" / "simu_1000.s36p", n_ports=36)
        assert net.n_ports == 36
        assert net.n_freq == 334
        assert net.freq[0] == pytest.approx(1e6)
        assert net.freq[-1] == pytest.approx(1e9)

    def test_invariante_i6_inclinacao_capacitiva(self):
        """R1 de PHYSICS_SPEC: medida -1.018 +- 0.008 sobre 40 configurações."""
        net = parse_touchstone(DATASET / "variation" / "simu_1000.s36p", n_ports=36)
        slope = low_frequency_slope(net.freq, np.abs(self_impedance(net)))
        assert -1.05 < slope < -0.95, f"inclinação fora da faixa esperada: {slope}"
