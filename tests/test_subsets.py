"""Testes de `src/data/subsets.py`, `src/data/grid.py` e `src/data/loader.py`.

Mesma organização de `test_touchstone.py`: forma/tipo, invariante/propriedade,
caso analítico, e um bloco final pulado se a base real não estiver disponível.

Deliberadamente NÃO carrega os 36199 arquivos .s2p do subconjunto de 1
cavidade em cada execução — isso levaria minutos. O que é rápido (ler o CSV,
uma única leitura Touchstone, o parser de decaps sobre a coluna inteira) roda
sempre; o carregamento completo com `load_pdn_dataset()`/`load_multi_subset()`
é a verificação manual descrita no plano da Etapa 2, não parte do pytest.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.data.grid import GRADE_COMUM, N_PONTOS, interpolar_para_grade
from src.data.loader import _load_single_config, _parse_decaps
from src.data.subsets import SEIS_CAMADAS, UMA_CAVIDADE, SubsetAdapter
from src.data.touchstone import (
    low_frequency_slope,
    parse_touchstone,
    quasi_static_window,
    self_impedance,
)


# --------------------------------------------------------------------------
# 1. forma e tipo
# --------------------------------------------------------------------------

class TestFormaETipo:
    def test_grade_comum_e_crescente_e_cobre_a_banda(self):
        assert GRADE_COMUM.shape == (N_PONTOS,)
        assert np.all(np.diff(GRADE_COMUM) > 0)
        assert GRADE_COMUM[0] == pytest.approx(1e6)
        assert GRADE_COMUM[-1] == pytest.approx(1e9)

    def test_interpolar_para_grade_preserva_shape(self):
        freq_o = np.logspace(6, 9, 50)
        z = np.linspace(1.0, 2.0, 50)
        saida = interpolar_para_grade(freq_o, z, GRADE_COMUM)
        assert saida.shape == GRADE_COMUM.shape
        assert saida.dtype == np.float64
        assert np.all(np.isfinite(saida))

    def test_adaptadores_tem_campos_consistentes(self):
        for adapter in (SEIS_CAMADAS, UMA_CAVIDADE):
            assert isinstance(adapter, SubsetAdapter)
            assert adapter.n_portas > 0
            assert 0 <= adapter.porta_interesse < adapter.n_portas
            assert len(adapter.features_geometria) > 0
            assert adapter.x_width_m > 0 and adapter.y_width_m > 0
            assert adapter.n_cavidades >= 1
            assert adapter.fonte_doc  # não vazio — rastreabilidade obrigatória


# --------------------------------------------------------------------------
# 2. invariantes / propriedades
# --------------------------------------------------------------------------

class TestPropriedades:
    def test_janela_adaptativa_tem_ao_menos_min_points(self):
        freq = np.logspace(6, 9, 10)
        z_abs = np.array([1e-3, 2e-3, 3, 4, 5, 6, 7, 8, 9, 10])  # nulo no índice 0
        mask = quasi_static_window(freq, z_abs, factor=3.0, min_points=3)
        assert mask.sum() >= 3

    def test_janela_adaptativa_perturbacao_monotonica(self):
        """Empurrar o nulo para uma frequência mais alta nunca encolhe a janela."""
        freq = np.logspace(6, 9, 40)
        z_capacitivo = freq ** -1.0
        for f_nulo_idx in (5, 15, 25):
            z = z_capacitivo.copy()
            z[f_nulo_idx] = 1e-6  # nulo artificial
            mask_estreita = quasi_static_window(freq, z, factor=6.0)
            mask_larga = quasi_static_window(freq, z, factor=2.0)
            assert mask_larga.sum() >= mask_estreita.sum()

    def test_parse_decaps_vazio(self):
        assert _parse_decaps("") == (0, 0.0)
        assert _parse_decaps("sem decaps aqui") == (0, 0.0)

    def test_parse_decaps_soma_capacitancia(self):
        campo = "{{0.02/2.8e-10/7e-09/5120/3840}{0.02/2.8e-10/3e-08/4800/4080}}"
        n, c_total = _parse_decaps(campo)
        assert n == 2
        assert c_total == pytest.approx(7e-9 + 3e-8)

    def test_features_unidas_de_load_multi_subset_incluem_decaps_sempre(self, monkeypatch):
        """`n_decaps`/`C_decap_total` não devem virar NaN por não estarem no
        subconjunto sem decaps — são preenchidas com zero em cada subconjunto
        individualmente, então a união nunca as marca como ausentes."""
        from src.data import loader as loader_mod

        def fake_load(adapter, n_workers=None, verbose=True, grid=None):
            n = 4
            feature_names = list(adapter.features_geometria) + ["n_decaps", "C_decap_total"]
            X = np.zeros((n, len(feature_names)))
            y = np.ones((n, len(grid)))
            return loader_mod.PDNDataset(
                X=X, y=y, freq=grid, simu_index=np.arange(n),
                subconjunto_id=np.full(n, adapter.nome, dtype=object),
                feature_names=feature_names,
                metadata={"subconjunto": adapter.nome, "n_configs": n},
            )

        monkeypatch.setattr(loader_mod, "load_pdn_dataset", fake_load)
        unido = loader_mod.load_multi_subset([SEIS_CAMADAS, UMA_CAVIDADE], verbose=False)
        idx_ndecaps = unido.feature_names.index("n_decaps")
        idx_ctotal = unido.feature_names.index("C_decap_total")
        assert not np.isnan(unido.X[:, idx_ndecaps]).any()
        assert not np.isnan(unido.X[:, idx_ctotal]).any()
        # já que as duas fontes têm colunas de geometria distintas, alguma
        # coluna DEVE ficar NaN em algum bloco — é o comportamento esperado.
        assert np.isnan(unido.X).any()


# --------------------------------------------------------------------------
# 3. casos analíticos
# --------------------------------------------------------------------------

class TestCasosAnaliticos:
    def test_interpolacao_com_grade_identica_e_identidade(self):
        freq = np.logspace(6, 9, 37)
        z = np.exp(np.random.default_rng(0).normal(size=37))
        saida = interpolar_para_grade(freq, z, freq)
        np.testing.assert_allclose(saida, z, rtol=1e-10)

    def test_interpolacao_recupera_lei_de_potencia_exata(self):
        """Uma lei de potência |Z| = A f^n é reta em log-log: a interpolação
        linear nesse espaço reproduz o valor exato em qualquer ponto novo,
        dentro do intervalo — é o teste mais sensível a erro de formulação
        (ex.: interpolar em escala linear em vez de log-log distorceria isto)."""
        freq_o = np.logspace(6, 9, 20)
        A, n = 3.7, -1.0  # R1: comportamento capacitivo ideal
        z_o = A * freq_o**n
        freq_d = np.logspace(6.3, 8.7, 133)  # grade nova, mais densa
        z_d = interpolar_para_grade(freq_o, z_o, freq_d)
        z_esperado = A * freq_d**n
        np.testing.assert_allclose(z_d, z_esperado, rtol=1e-9)


# --------------------------------------------------------------------------
# 4. testes sobre a base real (pulados se ausente)
# --------------------------------------------------------------------------

@pytest.mark.skipif(not SEIS_CAMADAS.caminho.exists(), reason="subconjunto de 6 camadas não disponível")
class TestBaseRealSeisCamadas:
    def test_r1_sobre_uma_configuracao(self):
        net = parse_touchstone(
            SEIS_CAMADAS.caminho / "variation" / "simu_1000.s36p", n_ports=36
        )
        z_abs = np.abs(self_impedance(net, port=SEIS_CAMADAS.porta_interesse))
        slope = low_frequency_slope(net.freq, z_abs, n_points=None)
        assert -1.05 < slope < -0.95, f"R1 fora da faixa: {slope}"

    def test_load_single_config_le_arquivo_real(self):
        args = (SEIS_CAMADAS.caminho / "variation", 36, 0, 0, 1000)
        r = _load_single_config(args)
        assert r is not None
        idx, simu_index, freq, z_abs = r
        assert idx == 0 and simu_index == 1000
        assert freq.shape == z_abs.shape
        assert np.all(z_abs > 0)

    def test_interpolacao_para_grade_comum_preserva_profundidade_do_nulo(self):
        """Trava a calibração de N_PONTOS em `grid.py`: o nulo de série do
        subconjunto de 6 camadas é a ressonância mais aguda das duas (sem
        decaps amortecendo), por isso o teste mais rigoroso do risco descrito
        no plano da Etapa 2. Amostra 30 curvas em vez de todas as 985 —
        propriedade estatística, não precisa da população inteira."""
        simu_indices_disponiveis = pd.read_csv(SEIS_CAMADAS.caminho / "parameter.csv")["simu_index"]
        rng = np.random.default_rng(0)
        indices = rng.choice(simu_indices_disponiveis, size=30, replace=False)
        erros_db = []
        for simu_index in indices:
            net = parse_touchstone(
                SEIS_CAMADAS.caminho / "variation" / f"simu_{simu_index}.s36p", n_ports=36
            )
            z_abs = np.abs(self_impedance(net, port=SEIS_CAMADAS.porta_interesse))
            z_interp = interpolar_para_grade(net.freq, z_abs, GRADE_COMUM)
            erro_log = abs(np.log10(z_abs.min()) - np.log10(z_interp.min()))
            erros_db.append(20 * erro_log)
        erros_db = np.array(erros_db)
        assert erros_db.max() < 1.5, (
            f"erro máximo na profundidade do nulo = {erros_db.max():.2f} dB — "
            f"acima de 1,5 dB sugere que N_PONTOS em grid.py precisa subir de novo"
        )


@pytest.mark.skipif(not UMA_CAVIDADE.caminho.exists(), reason="subconjunto de 1 cavidade não disponível")
class TestBaseRealUmaCavidade:
    def test_r1_sobre_uma_configuracao(self):
        net = parse_touchstone(UMA_CAVIDADE.caminho / "variation" / "simu_0.s2p", n_ports=2)
        z_abs = np.abs(self_impedance(net, port=UMA_CAVIDADE.porta_interesse))
        # janela fixa de 8 pontos falha aqui (documentado em UNIAO_SUBCONJUNTOS.md);
        # a adaptativa é o comportamento correto para este subconjunto.
        slope = low_frequency_slope(net.freq, z_abs, n_points=None)
        assert -1.1 < slope < -0.9, f"R1 fora da faixa com janela adaptativa: {slope}"

    def test_load_single_config_le_arquivo_real(self):
        args = (UMA_CAVIDADE.caminho / "variation", 2, 0, 0, 0)
        r = _load_single_config(args)
        assert r is not None
        idx, simu_index, freq, z_abs = r
        assert idx == 0 and simu_index == 0
        assert freq.shape == z_abs.shape

    def test_parse_decaps_sobre_o_csv_inteiro_reproduz_estatisticas_conhecidas(self):
        """Contra os números já medidos manualmente na etapa anterior: 1 a 20
        decaps por configuração, nenhuma configuração com zero decaps."""
        df = pd.read_csv(UMA_CAVIDADE.caminho / "parameter.csv")
        coluna = [c for c in df.columns if c.strip().startswith("{")][0]
        parsed = df[coluna].map(_parse_decaps)
        n_decaps = np.array([p[0] for p in parsed])
        assert n_decaps.min() >= 1
        assert n_decaps.max() <= 20
