# Spec: união dos subconjuntos de PDN da SI/PI-Database

**Versão:** 1.1 · **Data:** 2026-08-17 · **Revisado:** 2026-09-07
**Atende:** objetivo específico (a) da proposta — reunir os subconjuntos de PDN em uma
representação de atributos independente da topologia.
**Status:** dois subconjuntos inspecionados de catorze. Carregador genérico implementado
e verificado sobre os dois (`src/data/subsets.py`, `src/data/grid.py`, `src/data/loader.py`).

---

## Por que esta spec existe

A proposta prevê a união de catorze subconjuntos de PDN, de 1 a 13 cavidades. A inspeção
dos dois primeiros mostrou que eles diferem em **mais dimensões do que a proposta
antecipava**: não apenas no espaço de parâmetros e na numeração de portas, mas no próprio
*schema* do `parameter.csv` e na natureza do que varia. Sem um adaptador declarado por
subconjunto, a união produz silenciosamente um conjunto inconsistente.

---

## Inventário dos subconjuntos inspecionados

| | 6-Layer PDN Two Via Arrays | PWR/GND Plane 11×11 Array |
|---|---|---|
| pasta | `6_layer_pcb_based_pdn_with_two_arrays_LHS_mar_2023` | `pwr_gnd_plane_pcb_11x11_array_nov_22_2023` |
| data | mar. 2023 | 22 nov. 2023 |
| cavidades | 5 (6 camadas) | **1** |
| configurações | 985 | **36 199** |
| portas | 36 (`.s36p`) | **2** (`.s2p`) |
| pontos de frequência | **334**, passo 3,000 MHz | **300**, passo 3,341 MHz |
| faixa | 1 MHz – 1 GHz | 1 MHz – 1 GHz |
| placa | 5800 × 4000 mil | **12 × 10 pol = 12000 × 10000 mil** |
| `simu_index` | 1000 – 1984 | **0 – 36198** |
| amostragem | hipercubo latino | Monte Carlo sobre decaps |
| tamanho em disco | 23 GB | 2,0 GB |
| **o que varia** | **geometria** (8 parâmetros) | **decaps** + altura e ε_r |
| **o que é fixo** | decaps (não há) | raio de via 5 mil, antipad 18 mil, passo 40 mil |

### Armadilha 1 — numeração de portas mudou entre lançamentos

Na folha de dados de nov. 2023, **Port 1** é o porto central do arranjo, em `(ic_x, ic_y)` =
(5000, 4000) mil, e é o porto desacoplado — portanto **índice 0** da matriz. O artigo do
IEEE Access de 2021 descreve a mesma estrutura com a numeração **invertida** (Port 2 no
centro). A proposta já previa "um adaptador conferido contra a folha de dados"; fica
registrado que a conferência é obrigatória **por lançamento**, não por estrutura.

Verificado: com 1 cavidade em 1 MHz, os dois portos veem a mesma capacitância, de modo que
o erro de índice não seria detectado por inspeção da curva. Só a folha de dados o revela.

### Armadilha 2 — `parameter.csv` tem schema incompatível

O subconjunto de 6 camadas tem 17 colunas escalares. O de 1 cavidade tem 7 colunas e uma
oitava de **comprimento variável**, com a lista de capacitores no formato
`{ESR/ESL/C/xPos/yPos}{...}`, de 1 a 20 capacitores por configuração. Um leitor de CSV comum
funciona apenas porque não há vírgula dentro das chaves; o parsing correto usa
`re.findall(r'\{([^{}]+)\}', campo)`.

O subconjunto traz ainda `preproc_parameter.csv`, com as posições de decap já codificadas
pelo método de setores em anel usado nos artigos do próprio grupo, e o rótulo `targetMet`
(0 = impedância-alvo violada). É a representação pronta para ML que os autores recomendam.

### Armadilha 3 — a grade de frequência difere

334 pontos a 3,000 MHz contra 300 pontos a 3,341 MHz. A união exige interpolação para grade
comum, como a proposta previa. **Interpolar em `log10|Z|`**, não em `|Z|`, para preservar o
comportamento de lei de potência.

**Implementado em `src/data/grid.py`.** A grade comum é nova e log-espaçada — não a grade
nativa de nenhum dos dois subconjuntos — porque as duas já divergem entre si e um terceiro
subconjunto traria uma terceira grade; amarrar a comum a uma nativa não escala. A densidade
(`N_PONTOS`) foi calibrada empiricamente, não escolhida a priori: a interpolação é exata para
a lei de potência da região quase-estática (testado em `tests/test_subsets.py`), mas o nulo de
série é uma ressonância aguda, e sua profundidade só é recuperada se a grade de destino cair
perto o bastante da frequência nativa do nulo. Medido sobre 6 camadas (a ressonância mais
aguda, sem decaps amortecendo):

| N pontos | erro médio no nulo | erro máx. | % dentro de 5% |
|---|---|---|---|
| 400 (palpite inicial) | 1,06 dB | 3,94 dB | 32% |
| **1500 (adotado)** | **0,23 dB** | **0,78 dB** | **79%** |
| 6000 | 0,06 dB | 0,21 dB | 100% |

N=1500 é o equilíbrio: erro máximo abaixo de 1 dB, e `y` para a família completa
(~135.700 configs) ocupa ~0,8 GB em float32, dentro do orçamento de 8 GB de RAM que a
proposta declara (contra ~3,3 GB em N=6000, arriscado ao lado de X, modelo e overhead). O
resíduo é aceitável porque R1 — a única restrição hoje confirmada como transferível entre
topologias — vive na região quase-estática, onde a interpolação é exata; o nulo é o mínimo de
`|Z|`, a região de menor risco para a camada normativa, que soma dB contra o pior caso
(tipicamente onde `|Z|` é alto, não onde é mínimo).

---

## Requisito novo: janela quase-estática adaptativa

**Este é o achado de pipeline mais importante da inspeção.**

A extração de capacitância e a verificação de R1 usavam os **8 primeiros pontos** de
frequência, número calibrado no subconjunto de 6 camadas. Esse critério **não transfere**.

No subconjunto de 1 cavidade os decaps somam capacitância e empurram o nulo de série para
baixo: mediana de **27,7 MHz**, faixa de 11 a 88 MHz, contra ~97 MHz no de 6 camadas. Em
72 de 150 configurações amostradas o nulo ocorre **antes do oitavo ponto**. Consequência
medida sobre a inclinação log-log:

| janela | inclinação medida | dentro de [−1,05; −0,95] |
|---|---|---|
| 8 primeiros pontos (regra antiga) | −1,282 ± 0,149 | **9 %** |
| 3 primeiros pontos | −1,040 ± 0,033 | — |
| `f < f_nulo/3` | −1,056 ± 0,076 | 91 % |
| 3 primeiros pontos, placa dominante | **−1,0001 ± 0,0113** | **100 %** |

**Regra adotada:** a janela quase-estática é definida por configuração como
`f < f_nulo / K`, com `f_nulo` o mínimo de `|Z11|` e `K ≥ 3`, exigindo no mínimo 3 pontos.
A regra fixa por contagem fica proibida. Registrar `K` e o número de pontos efetivamente
usados em cada extração.

**Implementado em `src/data/touchstone.py:quasi_static_window()`.**
`low_frequency_slope(..., n_points=None)` passa a usá-la; `n_points` inteiro mantém a janela
fixa histórica, só para reproduzir a medição original sobre 40/985 configurações. Reverificado
sobre uma amostra de 500 configurações do subconjunto de 1 cavidade, através do carregador
genérico novo (não mais manualmente): conformidade com R1 sobe de 11,2% (janela fixa) para
92,4% (adaptativa) — mesma ordem de grandeza da medição anterior (9% → 91%).

---

## Atributos independentes de topologia

Definição operacional dos atributos que a proposta lista. Todos em SI, convertidos na
fronteira de entrada.

| atributo | definição | fonte |
|---|---|---|
| `n_cavidades` | número de pares de planos | folha de dados do subconjunto |
| `h_cavidade` | altura da cavidade | `TDIEL` / `diel_height` |
| `espessura_total` | `n_cavidades · h_cavidade + n_planos · t_metal` | derivado |
| `eps_r`, `tan_delta`, `sigma` | material | coluna direta |
| `area_placa` | `x_width · y_width` | folha de dados (**não** está no CSV) |
| `C_placa_analitica` | `ε₀ · eps_r · area · n_cavidades / h_cavidade` | derivado |
| `n_vias`, `densidade_vias` | contagem e contagem por área | folha de dados |
| `raio_via`, `raio_antipad`, `passo` | geometria do arranjo | coluna ou folha de dados |
| `passo_normalizado` | `passo / raio_via` | derivado |
| `razao_antipad` | `raio_antipad / raio_via` | derivado |
| `n_decaps`, `C_decap_total` | banco de desacoplamento | lista `{...}`; **0** onde não há |
| `f_nulo` | frequência do mínimo de `\|Z11\|` | derivado do alvo — **só para diagnóstico, nunca como feature** |

⚠️ `area_placa` e `n_vias` **não aparecem no `parameter.csv`** de nenhum dos dois
subconjuntos. São constantes por subconjunto e precisam ser transcritas manualmente da
folha de dados, com a fonte registrada. É o ponto mais provável de erro silencioso na união.

⚠️ O banco de decaps é parte da física do alvo, não ruído: no subconjunto de 1 cavidade ele
responde pela mediana de **78 %** da capacitância total. Um modelo treinado sobre os dois
subconjuntos sem essa feature não tem como reconciliar as curvas.

---

## O que ficou verificado sobre a física, entre subconjuntos

**R1 (forma capacitiva) transfere.** Com a janela correta, a inclinação é
−1,0001 ± 0,0113 no subconjunto de 1 cavidade (100 % de conformidade, seleção de placa
dominante) e −1,0197 ± 0,0062 no de 6 camadas (100 %). **R1 é a restrição segura para impor
globalmente na função de perda.**

**R2 (escala da capacitância) não transfere.** A razão entre a capacitância medida e a
fórmula de placas paralelas é:

| subconjunto | razão mediana | comportamento |
|---|---|---|
| 6 camadas | **2,13** (66 % das configs) | acima da fórmula; compatível com duas cavidades em paralelo |
| 1 cavidade | **0,46** | abaixo da fórmula; sobe monotonicamente com `h` |

No subconjunto de 1 cavidade a razão vai de 0,43 em `h` de 1–2 mil a 0,90 em 8–12 mil,
tendendo a 1 nas cavidades espessas. Testou-se e **refutou-se** o modelo de uma capacitância
parasita em série: o `C_série` implicado varia de 51,7 nF a 11,0 nF ao longo da faixa de `h`,
com R² negativo em log.

**Consequência para a função de perda:** o termo quase-estático deve ser formulado **apenas
sobre a derivada logarítmica**, que é invariante a fator multiplicativo — exatamente como a
proposta já especifica. A magnitude absoluta não sustenta um termo de perda com um único
coeficiente para todos os subconjuntos.

---

## O que o subconjunto de 1 cavidade validou do pipeline

O banco de decaps é uma grandeza conhecida de forma independente, o que permite um teste que
o subconjunto de 6 camadas não permitia. Regredindo a capacitância extraída contra as duas
contribuições conhecidas:

```
C_extraida = α · C_placa + β · C_decaps
β = 1,065        R² = 0,996        (n = 300)
```

O coeficiente do banco de decaps é recuperado em **1,065**, contra 1,000 esperado. Isso
valida de ponta a ponta a leitura Touchstone, a conversão S → Z, a extração de capacitância
e o parsing da coluna de capacitores, contra uma referência externa. O desvio fica **isolado
no termo da placa** (α), tratado acima.

Verificado também que a condição da porta 2 (aberta contra terminada em 50 Ω) é irrelevante
em baixa frequência: as duas dão o mesmo resultado até a quarta casa decimal.

---

## Critérios de aceitação

- [x] adaptador por subconjunto, com porta de interesse conferida contra a folha de dados
      **do lançamento correspondente**, e o número do documento registrado —
      `src/data/subsets.py`: `SubsetAdapter`, `SEIS_CAMADAS`, `UMA_CAVIDADE`, cada um com
      `fonte_doc`
- [x] `area_placa` e `n_vias` transcritos da folha de dados, com a fonte citada por
      subconjunto — parcial: `x_width_m`/`y_width_m` transcritos e testados
      (`test_adaptadores_tem_campos_consistentes`); `n_vias` **ainda não** — não é usado por
      nenhum código desta etapa, fica para quando servir de atributo independente de topologia
- [x] interpolação para grade comum feita em `log10|Z|` — `src/data/grid.py`, com teste
      analítico de lei de potência exata e teste de propriedade sobre dado real (profundidade
      do nulo)
- [x] janela quase-estática adaptativa, com `K` e número de pontos registrados por extração —
      `quasi_static_window()`; `K` e `min_points` são parâmetros explícitos, não registrados
      por chamada em log (suficiente para esta etapa; se necessário depois, é acréscimo trivial)
- [x] `n_decaps` e `C_decap_total` presentes para todo subconjunto, valendo zero onde não há —
      verificado por teste (`test_features_unidas_de_load_multi_subset_incluem_decaps_sempre`)
      e por execução real (`load_multi_subset`, nenhum `NaN` nessas duas colunas)
- [ ] processamento incremental: baixar, reduzir à curva, descartar o bruto antes do próximo —
      **não implementado nesta etapa**; os dois subconjuntos já estão em disco. Vira relevante
      só ao baixar o 3º/4º subconjunto do Marco 2
- [x] R1 verificada em cada subconjunto novo antes de sua incorporação — reverificada nos dois
      através do carregador genérico (não mais só manualmente): −1,03 (6 camadas, 985/985,
      100%) e −1,06 (1 cavidade, amostra n=500, 92,4%)

## O que a Etapa 2 implementou (2026-09-07)

`src/data/subsets.py`, `src/data/grid.py`, e a reescrita de `src/data/loader.py`
(`load_pdn_dataset(adapter)` genérico + `load_multi_subset(adapters)`). 36 testes em
`tests/test_touchstone.py` + `tests/test_subsets.py`, todos passando — os antigos
inalterados, os novos cobrindo forma/tipo, propriedade e caso analítico, mais um bloco pulado
se a base real não estiver em disco. `load_multi_subset([SEIS_CAMADAS, UMA_CAVIDADE])`
verificado ponta a ponta: `X` com 12 colunas (união de 8+2 features de geometria + 2 de
decaps), `n_decaps`/`C_decap_total` nunca `NaN`, colunas de geometria específicas de cada
subconjunto corretamente `NaN` do lado que não as tem, `y` interpolado sem falhas na grade
comum.

Descoberta durante a verificação (não estava nos critérios originais, mas decorre deles): a
densidade da grade comum precisou ser calibrada empiricamente contra a profundidade do nulo de
série, não escolhida a priori — ver Armadilha 3 acima.
