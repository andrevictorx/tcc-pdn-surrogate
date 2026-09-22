"""Grade de frequência comum para união de subconjuntos de PDN.

Ver `spec/UNIAO_SUBCONJUNTOS.md`: as grades nativas dos subconjuntos já
divergem entre si (334 pts/3,000 MHz no de 6 camadas; 300 pts/3,341 MHz no de
1 cavidade), e cada subconjunto futuro provavelmente traz sua própria
contagem e espaçamento. A grade comum é, por isso, nova e log-espaçada,
independente de qualquer subconjunto específico — para que toda extração
passe pela mesma interpolação, sem caso especial para "o subconjunto de
referência que não precisa interpolar".
"""

from __future__ import annotations

import numpy as np

FREQ_MIN_HZ = 1e6
FREQ_MAX_HZ = 1e9

# N_PONTOS = 1500, calibrado empiricamente (não o palpite inicial de 400).
#
# A interpolação linear em log-log é exata para uma lei de potência (testado
# em tests/test_subsets.py), mas o nulo de série é uma ressonância aguda, não
# uma lei de potência — seu valor mínimo só é recuperado se algum ponto da
# grade de destino cair perto o bastante da frequência exata do nulo nativo.
# Medido sobre as 985 curvas do subconjunto de 6 camadas (a ressonância mais
# aguda das duas, por não ter decaps amortecendo-a):
#
#   N pontos   erro médio no nulo   erro máx.   % dentro de 5%
#   400        1,06 dB              3,94 dB     32%
#   800        0,57 dB              1,65 dB     47%
#   1500       0,23 dB              0,78 dB     79%
#   3000       0,13 dB              0,47 dB     98%
#   6000       0,06 dB              0,21 dB     100%
#
# 1500 é o ponto de equilíbrio: erro máximo abaixo de 1 dB, e para a família
# completa (~135.700 configs, spec/DATA_SPEC.md) `y` em float32 ocupa ~0,8 GB,
# dentro do orçamento de 8 GB de RAM que a proposta declara como recurso
# (proposta/plano/conteudo.tex, "Recursos necessários"). N=6000 chegaria a
# ~3,3 GB só para `y`, arriscado ao lado de X, modelo e overhead do sistema.
#
# O resíduo é aceitável porque a única restrição física hoje confirmada como
# transferível entre topologias, R1, vive na região quase-estática — abaixo
# do nulo, onde a curva é lei de potência pura e a interpolação é exata (erro
# de máquina, não de amostragem). O nulo é o MÍNIMO de |Z|, a região de menor
# risco para a camada normativa (que soma dB contra o pior caso, tipicamente
# nas regiões de |Z| alto). Se um uso futuro for sensível à profundidade
# exata do nulo, reveja N aqui antes de reveja a arquitetura do pipeline.
N_PONTOS = 1500

GRADE_COMUM = np.logspace(np.log10(FREQ_MIN_HZ), np.log10(FREQ_MAX_HZ), N_PONTOS)


def interpolar_para_grade(
    freq_origem: np.ndarray, z_abs: np.ndarray, freq_destino: np.ndarray
) -> np.ndarray:
    """Interpola |Z(f)| para uma grade nova, em log10|Z| contra log10(f).

    A interpolação linear em espaço log-log é a escolha correta para uma curva
    que segue leis de potência por trechos (R1: |Z| ~ f^-1 abaixo do nulo de
    série) — interpolar em escala linear distorceria justamente a região de
    que a restrição física mais depende.

    Pontos de `freq_destino` fora do intervalo coberto por `freq_origem` são
    saturados no valor de borda (comportamento padrão de `numpy.interp`); isso
    só ocorre se a grade comum ultrapassar os limites nativos do subconjunto,
    o que não acontece para os dois subconjuntos hoje conhecidos (ambos
    1 MHz–1 GHz).

    Args:
        freq_origem: grade nativa, Hz, estritamente crescente, shape (nf_o,).
        z_abs: magnitude de |Z(f)| na grade nativa, mesma shape.
        freq_destino: grade de saída, Hz, shape (nf_d,).

    Returns:
        |Z(f)| interpolado na grade de saída, shape (nf_d,).
    """
    log_f_origem = np.log10(freq_origem)
    log_f_destino = np.log10(freq_destino)
    log_z = np.log10(np.maximum(z_abs, 1e-300))
    log_z_novo = np.interp(log_f_destino, log_f_origem, log_z)
    return 10.0**log_z_novo
