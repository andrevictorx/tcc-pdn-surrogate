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


def low_frequency_slope(freq: np.ndarray, z_abs: np.ndarray, n_points: int = 8) -> float:
    """Inclinação log-log de |Z| na região quase-estática.

    Vale -1 para comportamento capacitivo ideal. Invariante verificável I6 de
    `spec/DATA_SPEC.md`; medida em -1.018 +- 0.008 sobre 40 configurações.
    """
    lo = slice(0, n_points)
    return float(np.polyfit(np.log10(freq[lo]), np.log10(z_abs[lo]), 1)[0])


def check_invariants(network: Network, atol: float = 1e-6) -> dict[str, bool]:
    """Verifica as invariantes físicas I1-I4 de `spec/DATA_SPEC.md`.

    Returns:
        Mapa nome -> resultado. Nenhuma exceção é levantada; a decisão sobre o
        que fazer com uma violação cabe ao chamador.
    """
    s = network.s
    singular = np.linalg.svd(s, compute_uv=False)
    z = s_to_z(network)
    diagonal = np.einsum("kii->ki", z)
    return {
        "I1_reciprocidade": bool(np.allclose(s, np.swapaxes(s, 1, 2), atol=atol)),
        "I2_passividade_S": bool(np.all(singular <= 1.0 + atol)),
        "I3_passividade_Z": bool(np.all(diagonal.real >= -1e-9)),
        "I4_freq_crescente": bool(np.all(np.diff(network.freq) > 0)),
    }
