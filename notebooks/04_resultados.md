# Etapa 1 — Sensibilidade e verificação física

985 configurações · 334 pontos de frequência · 1 MHz a 1.00 GHz

## A. Carga do dataset


## B. Mapa de sensibilidade de Spearman (8 x 334)


## C. Ranking de sensibilidade e comparacao com a Fig. 11 publicada

| # | parametro | |rho| max | |rho| abaixo do nulo | |rho| acima do nulo | RMSE Fig.11 (ohm) | posicao publicada |
|---|---|---|---|---|---|---|
| 1 | TDIEL | 0.451 | 0.408 | 0.389 | 20.502 | 1 |
| 2 | PERMITTIVITY | 0.322 | 0.189 | 0.041 | 1.443 | 2 |
| 3 | A1_VIARADIUS | 0.184 | 0.073 | 0.067 | 1.325 | 3 |
| 4 | A2_ANTIPADRADIUS | 0.111 | 0.051 | 0.082 | 0.988 | 6 |
| 5 | A1_VIAPITCH | 0.109 | 0.029 | 0.035 | 0.600 | 7 |
| 6 | A1_ANTIPADRADIUS | 0.084 | 0.034 | 0.068 | 0.988 | 5 |
| 7 | A2_VIARADIUS | 0.043 | 0.015 | 0.019 | 1.325 | 4 |
| 8 | A2_VIAPITCH | 0.043 | 0.018 | 0.031 | 0.600 | 8 |


## D. Lei quase-estatica  |Z| = h / (2 pi f eps_0 eps_r a b)

| termo | coeficiente | erro-padrao | IC 95% | esperado | situacao |
|---|---|---|---|---|---|
| intercepto | +1.8160 | 0.0773 | [+1.665, +1.967] | - | - |
| log10(TDIEL) | +0.4279 | 0.0286 | [+0.372, +0.484] | +1.0 | DESVIO |
| log10(eps_r) | -0.5737 | 0.1208 | [-0.810, -0.337] | -1.0 | DESVIO |


**R² = 0.1967** (n = 985)


Embaralhado: R² = 0.0018 ± 0.0019. **Diagnóstico: expoente inesperado**


## E. R1 — inclinacao log-log em baixa frequencia

| grandeza | valor |
|---|---|
| media | -1.0197 |
| desvio-padrao | 0.0062 |
| minimo | -1.0373 |
| maximo | -0.9800 |
| esperado | -1.0000 |
| dentro de [-1,05; -0,95] | 100.0 % |


## F. R2 — escala da capacitancia

| estatistica | C_extraida / C_analitica |
|---|---|
| p5 | 0.511 |
| p25 | 2.032 |
| mediana | 2.130 |
| p75 | 2.344 |
| p95 | 9.088 |
| minimo | 0.106 |
| maximo | 43.165 |

| termo | coef. de log10(C_extraida) | IC 95% | esperado |
|---|---|---|---|
| log10(TDIEL) | -0.4245 | [-0.480, -0.369] | -1.0 |
| log10(eps_r) | +0.5683 | [+0.335, +0.802] | +1.0 |

| faixa de TDIEL (mil) | n | mediana da razao |
|---|---|---|
| 0 a 10 | 78 | 0.853 |
| 10 a 20 | 130 | 2.040 |
| 20 a 30 | 131 | 2.060 |
| 30 a 40 | 133 | 2.098 |
| 40 a 60 | 263 | 2.186 |
| 60 a 80 | 250 | 2.313 |


## F2. Populacao conforme (razao entre 1,5 e 3,0) vs. desviante

| grupo | n | % |
|---|---|---|
| razao < 1,5 | 169 | 17.2 |
| 1,5 <= razao < 3,0  (duas cavidades) | 653 | 66.3 |
| 3,0 <= razao < 10 | 121 | 12.3 |
| razao >= 10 | 42 | 4.3 |

| amostra | n | coef. log10(TDIEL) | coef. log10(eps_r) | R2 |
|---|---|---|---|---|
| todas as 985 | 985 | +0.428 +- 0.056 | -0.574 +- 0.237 | 0.197 |
| so conformes | 653 | +0.952 +- 0.012 | -0.974 +- 0.048 | 0.973 |
| esperado pela fisica | - | +1.000 | -1.000 | - |


**Na população conforme (66,3%) a lei quase-estática é confirmada: expoentes +0.952 e -0.974 contra +1 e -1 previstos, com R² = 0.973.**


## F3. Quanto as 8 features explicam de log|Z11(1 MHz)|

| modelo | termos | R2 |
|---|---|---|
| quase-estatico (TDIEL, eps_r) | 2 | 0.1967 |
| todas as 8 features | 8 | 0.2052 |
| ganho das 6 de geometria de via | - | +0.0085 |

| feature | coeficiente | IC 95% |
|---|---|---|
| TDIEL | +0.4278 | [+0.372, +0.484] |
| PERMITTIVITY | -0.5527 | [-0.789, -0.316] |
| A1_VIARADIUS | +0.0832 | [-0.102, +0.269] |
| A1_ANTIPADRADIUS | -0.2060 | [-0.413, +0.001] |
| A1_VIAPITCH | -0.0052 | [-0.322, +0.312] |
| A2_VIARADIUS | +0.0067 | [-0.177, +0.190] |
| A2_ANTIPADRADIUS | +0.2403 | [+0.027, +0.454] |
| A2_VIAPITCH | +0.1328 | [-0.176, +0.442] |


## G. Reciprocidade — varredura de tolerancia (20 configuracoes)

| tolerancia (atol) | aprovados / 20 |
|---|---|
| 1e-09 | 0 / 20 |
| 1e-08 | 0 / 20 |
| 1e-07 | 0 / 20 |
| 1e-06 | 0 / 20 |
| 1e-05 | 11 / 20 |
| 1e-04 | 20 / 20 |
| 1e-03 | 20 / 20 |


Assimetria máxima `|S − Sᵀ|`: mediana 9.355e-06, máximo 1.511e-05
