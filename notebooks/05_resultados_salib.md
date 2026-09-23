# Etapa 3 — Integridade, sensibilidade (SALib) e modelo de referência

Subconjunto PI-4 · tempo de execução: 80 s

## A. Integridade: capacitância extraída contra simu_index

| simu_index | n | conformes | razão mediana |
|---|---|---|---|
| 1000–1099 | 100 | 38 % | 2.17 |
| 1100–1199 | 100 | 29 % | 2.40 |
| 1200–1299 | 100 | 39 % | 2.14 |
| 1300–1399 | 100 | 34 % | 1.92 |
| 1400–1499 | 100 | 28 % | 1.95 |
| 1500–1599 | 97 | 100 % | 2.15 |
| 1600–1699 | 96 | 100 % | 2.14 |
| 1700–1799 | 98 | 100 % | 2.13 |
| 1800–1899 | 98 | 100 % | 2.11 |
| 1900–1999 | 96 | 100 % | 2.14 |

Bloco confiável (simu_index ≥ 1500): **485** configurações. Bloco suspeito: **500**.


## B. Modelo de referência: gradient boosting, validação cruzada 5 dobras

| log10|Z11| em | R² todas (985) | R² confiável (485) | RMSE confiável (déc.) | nRMSE confiável |
|---|---|---|---|---|
| 1 MHz | 0.111 ± 0.054 | 0.995 ± 0.001 | 0.0192 | 0.88 % |
| 10 MHz | 0.109 ± 0.053 | 0.996 ± 0.001 | 0.0186 | 1.60 % |
| 50 MHz | 0.113 ± 0.065 | 0.994 ± 0.001 | 0.0223 | 6.02 % |
| 97 MHz | 0.027 ± 0.050 | 0.721 ± 0.049 | 0.2476 | 41.17 % |
| 300 MHz | 0.034 ± 0.038 | 0.993 ± 0.002 | 0.0234 | 4.42 % |
| 600 MHz | 0.045 ± 0.051 | 0.994 ± 0.002 | 0.0220 | 2.47 % |
| 1000 MHz | 0.053 ± 0.061 | 0.679 ± 0.042 | 0.1913 | 16.69 % |


## C. SALib — bloco confiável (n = 485)


### log10|Z11| em 1 MHz (regime capacitivo)

| parâmetro | S1 (RBD-FAST) | δ (delta) | S1 (delta) | PAWN mediana |
|---|---|---|---|---|
| TDIEL | +0.924 ± 0.019 | 0.562 ± 0.017 | +0.850 ± 0.033 | 0.548 |
| PERMITTIVITY | +0.070 ± 0.076 | 0.111 ± 0.026 | +0.052 ± 0.044 | 0.176 |
| A2_ANTIPADRADIUS | +0.017 ± 0.066 | 0.098 ± 0.023 | +0.003 ± 0.019 | 0.119 |
| A1_VIAPITCH | +0.001 ± 0.056 | 0.057 ± 0.018 | +0.048 ± 0.019 | 0.104 |
| A2_VIAPITCH | -0.000 ± 0.061 | 0.056 ± 0.018 | +0.008 ± 0.015 | 0.098 |
| A2_VIARADIUS | -0.008 ± 0.076 | 0.043 ± 0.021 | +0.010 ± 0.017 | 0.160 |
| A1_VIARADIUS | -0.009 ± 0.066 | 0.091 ± 0.015 | +0.017 ± 0.016 | 0.118 |
| A1_ANTIPADRADIUS | -0.022 ± 0.064 | 0.095 ± 0.020 | +0.008 ± 0.015 | 0.095 |

Soma S1 (RBD-FAST) = **0.973** — quanto mais perto de 1, mais a saída é explicada por efeitos individuais, sem interações.


### frequência do nulo de série (MHz)

| parâmetro | S1 (RBD-FAST) | δ (delta) | S1 (delta) | PAWN mediana |
|---|---|---|---|---|
| PERMITTIVITY | +0.540 ± 0.083 | 0.343 ± 0.029 | +0.507 ± 0.052 | 0.304 |
| A1_VIARADIUS | +0.332 ± 0.095 | 0.201 ± 0.031 | +0.385 ± 0.067 | 0.226 |
| A1_VIAPITCH | +0.075 ± 0.086 | 0.123 ± 0.024 | +0.102 ± 0.046 | 0.132 |
| TDIEL | +0.020 ± 0.066 | 0.083 ± 0.024 | +0.048 ± 0.032 | 0.108 |
| A2_ANTIPADRADIUS | +0.007 ± 0.071 | 0.046 ± 0.026 | +0.040 ± 0.022 | 0.115 |
| A2_VIAPITCH | +0.004 ± 0.059 | 0.078 ± 0.025 | +0.004 ± 0.024 | 0.079 |
| A1_ANTIPADRADIUS | +0.002 ± 0.066 | 0.060 ± 0.026 | +0.003 ± 0.019 | 0.085 |
| A2_VIARADIUS | -0.020 ± 0.061 | 0.051 ± 0.024 | +0.003 ± 0.013 | 0.106 |

Soma S1 (RBD-FAST) = **0.961** — quanto mais perto de 1, mais a saída é explicada por efeitos individuais, sem interações.


### log10|Z11| no nulo

| parâmetro | S1 (RBD-FAST) | δ (delta) | S1 (delta) | PAWN mediana |
|---|---|---|---|---|
| TDIEL | +0.675 ± 0.059 | 0.370 ± 0.028 | +0.662 ± 0.049 | 0.403 |
| A1_VIARADIUS | +0.056 ± 0.090 | 0.108 ± 0.027 | +0.084 ± 0.047 | 0.128 |
| PERMITTIVITY | +0.023 ± 0.071 | 0.060 ± 0.027 | +0.008 ± 0.023 | 0.120 |
| A1_VIAPITCH | +0.022 ± 0.066 | 0.101 ± 0.026 | +0.092 ± 0.030 | 0.131 |
| A2_VIAPITCH | +0.019 ± 0.062 | 0.039 ± 0.019 | +0.003 ± 0.020 | 0.107 |
| A2_ANTIPADRADIUS | +0.006 ± 0.062 | 0.080 ± 0.029 | +0.034 ± 0.025 | 0.121 |
| A2_VIARADIUS | -0.004 ± 0.066 | 0.075 ± 0.023 | +0.005 ± 0.020 | 0.144 |
| A1_ANTIPADRADIUS | -0.011 ± 0.065 | 0.084 ± 0.018 | +0.007 ± 0.011 | 0.096 |

Soma S1 (RBD-FAST) = **0.786** — quanto mais perto de 1, mais a saída é explicada por efeitos individuais, sem interações.


### log10|Z11| em 1 GHz (regime indutivo)

| parâmetro | S1 (RBD-FAST) | δ (delta) | S1 (delta) | PAWN mediana |
|---|---|---|---|---|
| TDIEL | +0.611 ± 0.092 | 0.334 ± 0.028 | +0.597 ± 0.080 | 0.382 |
| PERMITTIVITY | +0.031 ± 0.071 | 0.084 ± 0.025 | +0.033 ± 0.039 | 0.129 |
| A1_VIAPITCH | +0.024 ± 0.065 | 0.109 ± 0.022 | +0.045 ± 0.024 | 0.100 |
| A2_VIAPITCH | +0.013 ± 0.060 | 0.068 ± 0.024 | +0.005 ± 0.016 | 0.114 |
| A1_VIARADIUS | +0.010 ± 0.080 | 0.132 ± 0.025 | +0.045 ± 0.031 | 0.106 |
| A2_VIARADIUS | +0.008 ± 0.074 | 0.081 ± 0.020 | +0.026 ± 0.022 | 0.123 |
| A2_ANTIPADRADIUS | -0.001 ± 0.054 | 0.078 ± 0.020 | +0.017 ± 0.018 | 0.117 |
| A1_ANTIPADRADIUS | -0.010 ± 0.070 | 0.042 ± 0.019 | +0.016 ± 0.020 | 0.107 |

Soma S1 (RBD-FAST) = **0.687** — quanto mais perto de 1, mais a saída é explicada por efeitos individuais, sem interações.


## D. S1 (RBD-FAST) por frequência — bloco confiável

Soma de S1 ao longo da banda: mínima 0.46, mediana 1.00, máxima 1.01.
