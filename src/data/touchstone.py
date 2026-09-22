"""Leitura de arquivos Touchstone e conversão para impedância.

Implementa `spec/DATA_SPEC.md`. Todas as grandezas internas em SI; a conversão
a partir de mil ocorre apenas em `mil_to_m`, na fronteira de entrada.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

MIL_TO_M = 25.4e-6
DEFAULT_Z0 = 50.0


def mil_to_m(value: np.ndarray | float) -> np.ndarray | float:
    """Converte mil para metro. Única fronteira de unidade do pipeline."""
    return np.asarray(value) * MIL_TO_M


@dataclass(frozen=True)
class Network:
    """Resposta em parâmetros de espalhamento de uma estrutura de N portas.

    Attributes:
        freq: grade de frequência em Hz, estritamente crescente, shape (nf,).
        s: matriz de espalhamento adimensional, shape (nf, n_ports, n_ports).
        z0: impedância de referência das portas, em ohms.
    """

    freq: np.ndarray
    s: np.ndarray
    z0: float = DEFAULT_Z0

    @property
    def n_ports(self) -> int:
        return self.s.shape[1]

    @property
    def n_freq(self) -> int:
        return self.freq.size


def parse_touchstone(path: str | Path, n_ports: int) -> Network:
    """Lê um Touchstone v1.1 em formato real-imaginário.

    O formato distribui os 2*P^2 valores de cada frequência por múltiplas linhas,
    de modo que a estrutura de linhas não é confiável para delimitar blocos. A
    leitura concatena todos os tokens numéricos e reagrupa por contagem.

    Args:
        path: caminho do arquivo .sNp.
        n_ports: número de portas P esperado.

    Returns:
        Network com freq (nf,) e s (nf, P, P).

    Raises:
        ValueError: se a contagem de valores não for múltipla de 1 + 2*P^2, ou
            se a grade de frequência não for estritamente crescente.
    """
    path = Path(path)
    rows: list[str] = []
    with path.open() as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped[0] in "!#":
                continue
            rows.append(stripped)

    values = np.fromstring(" ".join(rows), sep=" ")
    stride = 1 + 2 * n_ports * n_ports
    if values.size % stride:
        raise ValueError(
            f"{path.name}: {values.size} valores não são múltiplos de {stride} "
            f"(esperado para {n_ports} portas em formato RI)"
        )

    blocks = values.reshape(-1, stride)
    freq = blocks[:, 0]
    if not np.all(np.diff(freq) > 0):
        raise ValueError(f"{path.name}: grade de frequência não é estritamente crescente")

    pairs = blocks[:, 1:].reshape(-1, n_ports, n_ports, 2)
    s = pairs[..., 0] + 1j * pairs[..., 1]
    logger.debug("%s: %d frequências, %d portas", path.name, freq.size, n_ports)
    return Network(freq=freq, s=s)


def s_to_z(network: Network) -> np.ndarray:
    """Converte parâmetros de espalhamento em matriz de impedância.

    Z = sqrt(Z0) (I + S) (I - S)^-1 sqrt(Z0), com Z0 escalar reduzindo-se a
    Z = Z0 (I + S)(I - S)^-1. Resolvido por sistema linear; a inversa explícita
    é numericamente inferior e não é usada.

    Returns:
        Matriz complexa em ohms, shape (nf, P, P).
    """
    s = network.s
    n_freq, n_ports, _ = s.shape
    eye = np.eye(n_ports)
    z = np.empty_like(s)
    for k in range(n_freq):
        # resolve (I - S)^T X^T = (I + S)^T, equivalente a (I + S)(I - S)^-1
        z[k] = network.z0 * np.linalg.solve((eye - s[k]).T, (eye + s[k]).T).T
    return z


def self_impedance(network: Network, port: int = 0) -> np.ndarray:
    """Autoimpedância Z_ii(f) de uma porta, em ohms."""
    return s_to_z(network)[:, port, port]


def plate_capacitance(eps_r: float, width_m: float, length_m: float, height_m: float) -> float:
    """Capacitância de placas paralelas de uma cavidade retangular, em farad.

    Descreve a tendência da resposta quase-estática, não seu valor absoluto: em
    empilhamentos multicamadas a porta acopla-se a um número variável de
    cavidades. Ver R2 em `spec/PHYSICS_SPEC.md`.
    """
    eps_0 = 8.8541878128e-12
    return eps_0 * eps_r * width_m * length_m / height_m


def cavity_modes(eps_r: float, width_m: float, length_m: float, f_max: float,
                 max_order: int = 3) -> np.ndarray:
    """Frequências dos modos TM_mn0 de uma cavidade retangular, em Hz.

    Fornecida para análise; NÃO usar como restrição de treinamento sobre a
    autoimpedância — ver R5 em `spec/PHYSICS_SPEC.md`, refutada empiricamente.
    """
    c_0 = 299792458.0
    modes = [
        c_0 / (2 * np.sqrt(eps_r)) * np.hypot(m / width_m, n / length_m)
        for m in range(max_order + 1)
        for n in range(max_order + 1)
        if (m, n) != (0, 0)
    ]
    modes = np.array(sorted(f for f in modes if f <= f_max))
    return modes


def quasi_static_window(
    freq: np.ndarray, z_abs: np.ndarray, factor: float = 3.0, min_points: int = 3
) -> np.ndarray:
    """Máscara booleana da região quase-estática, adaptativa por curva.

    A janela fixa dos primeiros N pontos (usada até `spec/UNIAO_SUBCONJUNTOS.md`)
    pressupõe que o nulo de série está sempre distante do início da banda. Isso
    falha quando decaps deslocam o nulo para baixo: no subconjunto de 1 cavidade,
    8 pontos fixos capturam apenas 9% das curvas dentro do regime capacitivo
    puro, contra 91-100% com a janela adaptativa `f < f_nulo/factor`.

    Args:
        freq: grade de frequência, Hz, shape (nf,).
        z_abs: magnitude de |Z11(f)|, mesma shape.
        factor: a janela cobre f < f_nulo/factor. Maior => janela mais estreita,
            mais distante do nulo, portanto mais seguramente quase-estática.
        min_points: garante ao menos esta contagem de pontos mesmo se o nulo
            estiver muito próximo do início da banda.

    Returns:
        Máscara booleana, shape (nf,), com min_points True no mínimo.
    """
    f_nulo = freq[int(np.argmin(z_abs))]
    mask = freq < f_nulo / factor
    if mask.sum() < min_points:
        mask = np.zeros_like(mask)
        mask[:min_points] = True
    return mask


def low_frequency_slope(
    freq: np.ndarray, z_abs: np.ndarray, n_points: int | None = 8, factor: float = 3.0
) -> float:
    """Inclinação log-log de |Z| na região quase-estática.

    Vale -1 para comportamento capacitivo ideal. Invariante verificável I6 de
    `spec/DATA_SPEC.md`.

    Args:
        n_points: se um inteiro, usa a janela fixa histórica (compatibilidade
            retroativa com a medição de -1.018 +- 0.008 sobre 40 configurações
            do subconjunto de 6 camadas). Se None, usa a janela adaptativa
            `quasi_static_window` — necessária para subconjuntos onde o nulo de
            série pode cair dentro dos primeiros pontos da banda (ex.: 1
            cavidade com decaps). Ver `spec/UNIAO_SUBCONJUNTOS.md`.
        factor: repassado a `quasi_static_window` quando n_points é None.
    """
    if n_points is None:
        mask = quasi_static_window(freq, z_abs, factor=factor)
    else:
        mask = np.zeros_like(z_abs, dtype=bool)
        mask[:n_points] = True
    return float(np.polyfit(np.log10(freq[mask]), np.log10(z_abs[mask]), 1)[0])


def check_invariants(
    network: Network,
    atol_reciprocidade: float = 1e-4,
    atol_passividade_s: float = 1e-6,
    atol_passividade_z: float = 1e-9,
) -> dict[str, bool]:
    """Verifica as invariantes físicas I1-I4 de `spec/DATA_SPEC.md`.

    Tolerâncias distintas por invariante, conforme medido empiricamente: I1
    (reciprocidade) exige 1e-4 porque a assimetria numérica do solver chega a
    1.5e-5 mesmo em simulações fisicamente saudáveis (ver nota em
    `spec/DATA_SPEC.md`, 20/20 configurações aprovadas nessa tolerância contra
    0/20 em 1e-6). I2 e I3 permanecem nas tolerâncias originais, mais estritas.

    Returns:
        Mapa nome -> resultado. Nenhuma exceção é levantada; a decisão sobre o
        que fazer com uma violação cabe ao chamador.
    """
    s = network.s
    singular = np.linalg.svd(s, compute_uv=False)
    z = s_to_z(network)
    diagonal = np.einsum("kii->ki", z)
    return {
        "I1_reciprocidade": bool(np.allclose(s, np.swapaxes(s, 1, 2), atol=atol_reciprocidade)),
        "I2_passividade_S": bool(np.all(singular <= 1.0 + atol_passividade_s)),
        "I3_passividade_Z": bool(np.all(diagonal.real >= -atol_passividade_z)),
        "I4_freq_crescente": bool(np.all(np.diff(network.freq) > 0)),
    }
