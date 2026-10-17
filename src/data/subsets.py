"""Adaptadores de subconjunto para o carregador genérico de PDN.

Cada `SubsetAdapter` declara o que o `parameter.csv` de um subconjunto NÃO diz
sozinho: número de portas, qual porta é a de interesse (conferida contra a
folha de dados do lançamento correspondente — a numeração já mudou entre
lançamentos, ver `spec/UNIAO_SUBCONJUNTOS.md`), e as dimensões físicas da
placa, que nunca aparecem no CSV.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .touchstone import MIL_TO_M

_ROOT = Path(__file__).resolve().parent.parent.parent
_MIL_PER_INCH = 1000.0


@dataclass(frozen=True)
class SubsetAdapter:
    """Descreve como extrair um subconjunto de PDN da SI/PI-Database.

    Attributes:
        nome: identificador curto, usado como `subconjunto_id` no dataset unido.
        caminho: diretório raiz do subconjunto (contém parameter.csv e variation/).
        n_portas: número de portas dos arquivos Touchstone (.sNp).
        porta_interesse: índice 0-based da porta de autoimpedância a extrair,
            conferido contra a folha de dados do lançamento correspondente.
        features_geometria: colunas escalares do parameter.csv que variam.
        tem_decaps: se True, a última coluna do parameter.csv é a lista
            {ESR/ESL/C/xPos/yPos} de capacitores de desacoplamento.
        x_width_m: largura da placa, em metros. Não está no parameter.csv —
            transcrita da folha de dados.
        y_width_m: comprimento da placa, em metros. Mesma origem.
        n_cavidades: número de cavidades dielétricas do empilhamento.
        fonte_doc: citação da folha de dados, para rastreabilidade.
        n_cavidades_alim_terra: cavidades entre um plano de alimentação e um de
            terra. Só elas armazenam carga entre os trilhos, e ficam em paralelo
            pelas vias: C = n · ε0·εr·A/h_ef (H3, `spec/CONSISTENCIA_DADOS.md`).
        fator_espessura, espessura_extra_mil: espessura efetiva entre os planos de
            uma cavidade alimentação–terra, h_ef = fator · h_csv + extra. No PI-1
            a cavidade tem duas camadas de dielétrico de espessura `diel_height`
            e uma camada de sinal de 1 mil entre elas: h_ef = 2·h + 1 mil.
    """

    nome: str
    caminho: Path
    n_portas: int
    porta_interesse: int
    features_geometria: tuple[str, ...]
    tem_decaps: bool
    x_width_m: float
    y_width_m: float
    n_cavidades: int
    fonte_doc: str
    n_cavidades_alim_terra: int = 1
    fator_espessura: float = 1.0
    espessura_extra_mil: float = 0.0

    def espessura_efetiva_m(self, h_csv_mil):
        """Distância entre os planos de uma cavidade alimentação–terra, em metros."""
        return (self.fator_espessura * h_csv_mil + self.espessura_extra_mil) * MIL_TO_M


SEIS_CAMADAS = SubsetAdapter(
    nome="6_camadas",
    caminho=_ROOT / "6_layer_pcb_based_pdn_with_two_arrays_LHS_mar_2023",
    n_portas=36,
    porta_interesse=0,
    features_geometria=(
        "TDIEL",
        "PERMITTIVITY",
        "A1_VIARADIUS",
        "A1_ANTIPADRADIUS",
        "A1_VIAPITCH",
        "A2_VIARADIUS",
        "A2_ANTIPADRADIUS",
        "A2_VIAPITCH",
    ),
    tem_decaps=False,
    x_width_m=5800.0 * MIL_TO_M,
    y_width_m=4000.0 * MIL_TO_M,
    n_cavidades=5,
    n_cavidades_alim_terra=2,   # GND/GND/PWR/PWR/GND/GND: GND–PWR e PWR–GND, ambas com espessura TDIEL
    fonte_doc=(
        "TUHH, folha de dados '6-Layer PCB based PDN with Two Via Arrays — "
        "Latin Hypercube Sampling', Morten Schierholz, 6 mar. 2023"
    ),
)

UMA_CAVIDADE = SubsetAdapter(
    nome="1_cavidade",
    caminho=_ROOT / "pwr_gnd_plane_pcb_11x11_array_nov_22_2023",
    n_portas=2,
    # Port 1 (índice 0) é o centro do arranjo — a porta desacoplada pelos
    # decaps — conforme a Fig. 1 da folha de dados de 22/11/2023. A numeração
    # já mudou entre lançamentos (ver spec/UNIAO_SUBCONJUNTOS.md); reconferir
    # a folha de dados de qualquer novo subconjunto antes de reusar este valor.
    porta_interesse=0,
    features_geometria=("diel_height", "epsilon_r"),
    tem_decaps=True,
    x_width_m=12.0 * _MIL_PER_INCH * MIL_TO_M,
    y_width_m=10.0 * _MIL_PER_INCH * MIL_TO_M,
    n_cavidades=1,
    n_cavidades_alim_terra=1,
    # Medido em 17/10/2026: só h_ef = 2·diel_height + 1 mil reproduz a capacitância
    # simulada (99,6 %, p5–p95 98,8–100,3 % nas 36 199 configurações); a folha de
    # dados descreve a espessura de outro modo. Ver notebook, seção II.0.
    fator_espessura=2.0,
    espessura_extra_mil=1.0,
    fonte_doc=(
        "TUHH, folha de dados 'PWR/GND Plane PCB with 11x11 Via-Array', "
        "Morten Schierholz, 22 nov. 2023"
    ),
)

SUBCONJUNTOS_PDN = (SEIS_CAMADAS, UMA_CAVIDADE)
