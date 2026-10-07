# Resumo técnico do notebook `TCC_PDN_Colab.ipynb`

**TCC — Engenharia Elétrica, UFPR** · André Victor Xavier Pires · Orientador: Prof. Dr. Leandro dos Santos Coelho
**Situação em:** 6 de outubro de 2026 · **Notebook:** [`notebooks/TCC_PDN_Colab.ipynb`](../notebooks/TCC_PDN_Colab.ipynb)

Este documento resume, em ordem, tudo o que o notebook faz e o que se concluiu. Cada seção indica a parte do
notebook correspondente, para consulta das figuras.

---

## 1. O problema em uma página

### 1.1 O que é a PDN e por que a impedância importa

A **rede de distribuição de energia** (*power distribution network*, PDN) de uma placa de circuito impresso
multicamadas leva a tensão do regulador (VRM) até os circuitos integrados. Ela é formada por **pares de planos de
cobre**, um de alimentação e um de terra, separados por um dielétrico. Cada par forma uma **cavidade**.

Quando um circuito integrado comuta, ele puxa uma corrente transitória $I(f)$. A tensão de ruído que aparece nos
trilhos é, pela lei de Ohm no domínio da frequência,

$$V_{\rm ruído}(f) = Z_{11}(f)\cdot I(f)$$

em que $Z_{11}(f)$ é a **autoimpedância** vista pela porta do circuito integrado. Quanto menor $Z_{11}$, menor o
ruído. Esse ruído se acopla às estruturas da placa e é **irradiado**. A emissão irradiada é limitada por norma:
**CISPR 32** (classes A e B) e **IEC 61000-6-3 / 6-4**, a partir de **30 MHz**.

### 1.2 O objetivo do TCC

Construir um **modelo substituto** (*surrogate model*) que preveja $Z_{11}(f)$ de 1 MHz a 1 GHz a partir dos
parâmetros geométricos e de material da placa, em milissegundos em vez das horas de uma simulação eletromagnética.
Esse modelo deve ser **informado por física**: além de ajustar os dados, ele deve obedecer às leis conhecidas da PDN.
No TCC II, a curva prevista alimenta uma **margem normativa em dB** contra os limites de emissão, como medida
**ordinal** para comparar projetos (não como certificação).

### 1.3 Os dados

Os dados vêm da **SI/PI-Database** do Institut für Theoretische Elektrotechnik da TUHH (Schierholz *et al.*, *IEEE
Access*, 2021). Cada simulação é um arquivo **Touchstone** (`.sNp`) com a **matriz de espalhamento** $S(f)$ de $N$
portas, acompanhado de uma linha num `parameter.csv` com os parâmetros de projeto usados.

A conversão da matriz de espalhamento para a matriz de impedâncias é a relação clássica de redes de $N$ portas, com
impedância de referência $Z_0 = 50\ \Omega$:

$$Z = Z_0\,(I + S)(I - S)^{-1}$$

Da matriz $Z$ usa-se só o elemento diagonal da porta de interesse, $Z_{11}(f)$.

---

## 2. Os quatro subconjuntos analisados

| Código | Nome na base | Empilhamento | Simulações usadas | Portas | O que varia |
|---|---|---|---|---|---|
| **PI-1** | PWR/GND Plane PCB with 11×11 Via-Array (nov. 2023) | 1 cavidade | 36 199 | 2 | espessura, $\varepsilon_r$ e banco de capacitores de desacoplamento |
| **PI-2** | 4-Layer PCB based PDN with Two Via Arrays (fev. 2022) | 4 planos, 3 cavidades, 2 entre alimentação e terra | 9 999 de 10 000 | 28 | espessura, $\varepsilon_r$, tamanho da placa, tangente de perdas, passo e posição dos arranjos |
| **PI-4** | 6-Layer PCB based PDN with Two Via Arrays, LHS (mar. 2023) | 6 planos, 5 cavidades, 2 entre alimentação e terra | 485 de 985 | 36 | espessura, $\varepsilon_r$ e geometria das vias de dois arranjos |
| **PI-3** | 8-Layer PCB based PDN with Two Via Arrays, LHS (jul. 2022) | 8 planos, 7 cavidades, 2 entre alimentação e terra | 10 000 | 28 | espessura, $\varepsilon_r$, tamanho da placa e posição dos arranjos |

### 2.1 Entradas de cada subconjunto

**PI-4** (placa fixa de 5 800 × 4 000 mil, isto é, 147 × 102 mm; 1 mil = 25,4 µm):

| Grandeza | Símbolo | Coluna | Faixa |
|---|---|---|---|
| Espessura do dielétrico das cavidades alimentação–terra | $h$ | `TDIEL` | 3,1 – 79 mil |
| Permissividade relativa | $\varepsilon_r$ | `PERMITTIVITY` | 2,5 – 4,5 |
| Raio da via, raio do antipad e passo do arranjo I (onde está a porta) | $r_{v,1}, r_{a,1}, p_1$ | `A1_*` | 10–20, 20–39, 80–120 mil |
| Os mesmos três do arranjo II | $r_{v,2}, r_{a,2}, p_2$ | `A2_*` | mesmas faixas |

**PI-1** (placa de 12 × 10 polegadas, arranjo de vias 11 × 11 fixo):

| Grandeza | Símbolo | Coluna | Faixa |
|---|---|---|---|
| Espessura do dielétrico | $h$ | `diel_height` | 1,15 – 11,4 mil |
| Permissividade relativa | $\varepsilon_r$ | `epsilon_r` | 3 – 9 |
| Banco de capacitores de desacoplamento (ESR, ESL, C, posição) | — | `{ESR/ESL/C/xPos/yPos}` | 1 a 20 capacitores |
| Derivadas: número de capacitores e capacitância total | $n_{\rm dec}$, $C_{\rm dec}$ | — | 1–20; 1 nF – 808 nF |

**PI-3 e PI-2** (o tamanho da placa passa a variar):

| Grandeza | Símbolo | Coluna | PI-3 | PI-2 |
|---|---|---|---|---|
| Espessura do dielétrico | $h$ | `TDIEL` | 5 – 50 mil, contínua | 3 – 39 mil, 37 níveis |
| Permissividade relativa | $\varepsilon_r$ | `PERMITTIVITY` | 2,0 – 4,5, contínua | 2,0 – 4,5, 11 níveis |
| Largura e altura da placa | $a$, $b$ | `XWIDTH`, `YWIDTH` | 4 200–18 000 e 3 000–18 000 mil | idem |
| Tangente de perdas | $\tan\delta$ | `LOSSTANGENT` | 0,02 fixa | 0,005 – 0,025 |
| Passo do arranjo A1 | $p_1$ | `A1_VIAPITCH` | 60 mil fixo | 50 – 70 mil |
| Posição do arranjo A1 (lado do CI) | $x_1, y_1$ | `A1_XCENTER/YCENTER` | qualquer ponto da placa | idem |
| Posição do regulador | $x_{\rm VRM}, y_{\rm VRM}$ | `VRM_XCENTER/YCENTER` | perto do centro | idem |

Nas análises do PI-3 e do PI-2 usam-se ainda a área $A = a\,b$ e a posição relativa da porta, $u = x_1/a$ e
$v = y_1/b$.

### 2.2 Saídas (as mesmas para todos)

| Saída | Símbolo | Como se obtém |
|---|---|---|
| Autoimpedância complexa | $Z_{11}(f)$ | conversão S → Z, em 300 ou 334 frequências de 1 MHz a 1 GHz |
| Módulo em escala logarítmica | $\log_{10}\lvert Z_{11}\rvert$ | variável-alvo dos modelos |
| Impedância máxima | $\lvert Z\rvert_{\max}$ | ocorre em 1 MHz, no extremo capacitivo |
| Frequência de ressonância série (nulo) | $f_{\rm nulo}$ | frequência do mínimo de $\lvert Z_{11}\rvert$ |
| Capacitância extraída | $C_{\rm ext}$ | $C = 1/(2\pi f\lvert Z\rvert)$ nos primeiros pontos |
| Inclinação em baixa frequência | $d\log\lvert Z\rvert / d\log f$ | ajuste linear em escala log–log abaixo do nulo |
| Menor parte real | $\min \mathrm{Re}\{Z_{11}\}$ | teste de passividade |

---

## 3. A física da curva de impedância

Toda curva $\lvert Z_{11}(f)\rvert$ da base tem a mesma forma, que se explica com um **circuito RLC série** equivalente.

| Região | Comportamento | Modelo | Inclinação em log–log |
|---|---|---|---|
| Abaixo do nulo | **capacitiva** | capacitor de placas paralelas $C = \varepsilon_0\varepsilon_r A/h$ | −1 |
| No nulo | **ressonância série** | $f_{\rm nulo} = 1/(2\pi\sqrt{L_{\rm eq}C})$; o mínimo é limitado pela resistência | — |
| Acima do nulo | **indutiva** | indutância de espalhamento dos planos vista pela via, $L_{\rm eq}\propto h$ | +1 |
| Faixa alta | **ressonâncias de cavidade** | modos TM$_{mn}$ da cavidade retangular | picos |

Os modos de uma cavidade retangular de lados $a$ e $b$ com paredes magnéticas nas bordas ocorrem em

$$f_{mn} = \frac{c_0}{2\sqrt{\varepsilon_r}}\sqrt{\left(\frac{m}{a}\right)^2 + \left(\frac{n}{b}\right)^2}$$

e a tensão do modo na posição $(x, y)$ é proporcional a $\cos(m\pi x/a)\cos(n\pi y/b)$. Um modo só aparece na
impedância de uma porta se a porta **não** estiver num nó de tensão dele.

---

## 4. Parte 0 — Leitura e benchmark de processamento

**Objetivo.** Medir quanto custa transformar os arquivos brutos, já em disco, nas curvas usadas pelo TCC.

**Resultado.** O PI-4 leva cerca de 6 min em um processo e 80 s com 8 processos; o PI-1, de 1 a 1,5 min e 10 s. De
90 a 96 % do tempo é gasto lendo o texto dos arquivos Touchstone; a álgebra S → Z é barata. O PI-4 é o caso extremo
de redução: 23 GB de matrizes 36 × 36 viram um cache de 2,5 MB, porque só se usa $Z_{11}$.

**PI-3 e PI-2.** Os zips têm 147 e 113 GB descompactados. O script
[`scripts/reduzir_zip_pdn.py`](../scripts/reduzir_zip_pdn.py) lê cada arquivo **dentro do zip**, sem extrair,
converte S → Z e guarda só três curvas por simulação: $Z$ na porta P11 (arranjo A1), na porta P1 (regulador) e a
transimpedância entre elas. Cada subconjunto leva cerca de 9 min e gera um cache de 75 MB. Nenhuma das 20 000 leituras
falhou.

---

## 5. Parte I — PI-4: a placa de 6 camadas

### 5.1 Visão geral (I.1)
A curva é capacitiva até o nulo de série, por volta de 100 MHz, e indutiva acima. $\lvert Z\rvert_{\max}$ está em
1 MHz. As ressonâncias que importam para a compatibilidade eletromagnética aparecem perto de 900 MHz a 1 GHz, dentro
da banda da CISPR 32.

### 5.2 Integridade dos dados (I.2) e o bloco não confiável (I.2b)

**O que se mediu.** Para cada simulação, a capacitância **extraída da curva** foi comparada à capacitância
**calculada com a linha do CSV**, pela fórmula de placas paralelas. Se o CSV descreve o arquivo, a razão entre as duas
deve ser constante.

**O que se encontrou.** A partir da simulação 1500 a razão fica entre 2,04 e 2,33, com correlação $r = 0{,}999$ entre
as duas capacitâncias. Nas simulações 1000 a 1499 a correlação é $r = 0{,}02$: as duas grandezas não têm relação.

**O que significa "não confiável".** O arquivo `simu_i` existe e contém uma resposta fisicamente correta, mas **não foi
gerado com os parâmetros escritos na linha $i$ do CSV**. Para aprendizado supervisionado, isso é fatal: o modelo
aprenderia a associar entradas a saídas que não lhes pertencem.

**Quatro hipóteses testadas (Figura I.2b):**

| Hipótese | Teste | Resultado | Veredito |
|---|---|---|---|
| 1. As curvas estão fisicamente erradas | inclinação abaixo do nulo e passividade | −1,022 ± 0,007; Re{Z} sempre positivo | descartada |
| 2. As linhas estão deslocadas ($i \to i+k$) | correlação para todo $k$ entre −400 e +400 | melhor $r = 0{,}22$ | descartada |
| 3. As linhas estão embaralhadas dentro do bloco | melhor atribuição um-para-um curva × linha (algoritmo húngaro) | erro 0,156 década, contra 0,059 no controle | descartada |
| 4. Os arquivos vêm de outra amostragem, não registrada | espessura inferida da própria curva por um modelo inverso | cobre 4–78 mil, mas não concorda com o CSV (R² = −1,12) | compatível |

**Cronologia dos arquivos (I.2c).** O zip preserva a data e a hora de gravação de cada arquivo, e todas são de 6 de
março de 2023, nos servidores da TUHH:

| Grupo | Arquivos | Gravados | Coerentes com a planilha |
|---|---|---|---|
| simu 1000–1499 | 500 | 07:20:14 – 07:24:50 | 15 % (só por acaso) |
| simu 1500–1999, antes da planilha | 206 | 07:24:51 – 07:29:07 | 100 % |
| `parameter.csv` | 1 | **07:59:03** | — |
| simu 1500–1999, depois da planilha | 279 | 08:09:33 – 08:16:01 | 99 % |

Os arquivos 1499 e 1500 foram gravados com **um segundo** de diferença, no mesmo fluxo contínuo. O processo de
gravação foi o mesmo; o que muda é a lista de parâmetros. As 500 primeiras linhas da planilha descrevem uma amostragem
diferente da que foi simulada. A hipótese mais provável é que essa parte da lista tenha sido sorteada de novo, ou
sobrescrita, antes de a planilha ser escrita.

**O arquivo original já tinha o defeito?** Sim. As datas são as do servidor da TUHH, preservadas pelo zip, e a planilha
nunca foi editada localmente. Baixar de novo traria o mesmo defeito.

**É possível corrigir a planilha a partir das curvas?** Só em parte, e não vale a pena. Um modelo inverso, que lê o
parâmetro a partir da curva, treinado no bloco confiável, recupera:

| Parâmetro | R² do modelo inverso | Recuperável? |
|---|---|---|
| espessura `TDIEL` | 0,98 | sim |
| permissividade `PERMITTIVITY` | 0,75 | aproximadamente |
| raio da via do arranjo I | 0,56 | mal |
| os outros cinco (antipad e passo do arranjo I; todo o arranjo II) | negativo | **não** |

É a contrapartida da análise de sensibilidade: se um parâmetro mexe pouco na curva, a curva diz pouco sobre ele. Uma
planilha "corrigida" teria valores inventados nas colunas das vias e contaminaria a análise de sensibilidade. O ganho
seriam 500 linhas num total que, com PI-2 e PI-3, passa de 20 000.

**Conclusão.** O defeito está no rótulo, não na simulação. **A única correção legítima é pedir à TUHH a lista de
parâmetros original**, que existe no script de geração da amostragem. Até lá, todas as análises usam o **bloco
confiável** de 485 simulações. As 500 curvas ainda podem servir para conferir restrições que não dependem dos
parâmetros (H1, H4, H5).

### 5.3 As hipóteses físicas no PI-4 (I.3 a I.7)

| Seção | Hipótese | Resultado |
|---|---|---|
| I.3 | **H1** — inclinação −1 abaixo do nulo | −1,020 ± 0,006 em todas as 985 curvas |
| I.4 | **H3** — $C \propto \varepsilon_r/h$ | expoentes +0,955 e −1,022, R² = 0,998; fator 2,13 (duas cavidades em paralelo) |
| I.5 | **H4** — decrescimento monotônico até o nulo | 100 % das curvas |
| I.6 | **H2** — ressonâncias nos modos da cavidade | TM$_{10}$ e TM$_{01}$ ausentes; pico compatível com TM$_{11}$ em 171 de 296 curvas |
| I.7 | **H5** — passividade, $\mathrm{Re}\{Z_{11}\} \ge 0$ | 100 % das curvas |

### 5.4 Análise de sensibilidade (I.8)

Com a biblioteca SALib, usaram-se dois métodos: **RBD-FAST**, direto sobre os dados, e **índices de Sobol** de
primeira ordem ($S_1$) e total ($S_T$), calculados sobre um modelo substituto. A espessura do dielétrico domina
$\lvert Z\rvert_{\max}$ ($S_1 \approx S_T \approx 0{,}95$), seguida de $\varepsilon_r$ e do raio da via. **As três
primeiras posições coincidem com Schierholz, Hassab e Schuster (2023)**, obtidas por outro método. O nulo de série é
governado por $\varepsilon_r$ e pela via do arranjo I, e o arranjo II, que não tem a porta, tem efeito quase nulo.

### 5.5 Modelo substituto (I.9)

Um ExtraTrees prevê a curva inteira (334 pontos) a partir dos 8 parâmetros. No bloco confiável: **R² global de 0,97**
e **R² de $\lvert Z\rvert_{\max}$ de 0,99**, acima da meta de 0,90 da proposta. O erro se concentra no nulo e nas
ressonâncias perto de 1 GHz.

---

## 6. Parte II — PI-1: uma cavidade com capacitores de desacoplamento

| Seção | O que se viu |
|---|---|
| II.1 | Os capacitores de desacoplamento somam capacitância à da placa: o nulo cai para 24 MHz (mediana), contra 106 MHz no PI-4. |
| II.2 | **A janela de medição precisa ser adaptativa.** Com a janela fixa de 8 pontos, calibrada no PI-4, quase todo o PI-1 parece violar H1, porque o nulo cai dentro da janela. Com a janela $f < f_{\rm nulo}/3$: 61 % das curvas em ±0,05 e 91 % em ±0,10; 99 % quando a placa domina a capacitância. |
| II.3 | **Validação do pipeline.** A capacitância do banco de decaps é recuperada com coeficiente β ≈ 1 e R² ≈ 0,99 sobre 36 199 configurações: leitura, conversão e extração estão corretas de ponta a ponta. |
| II.4 | A razão $C_{\rm ext}/C_{\rm 1\,cavidade}$ dá **0,45**, quando o esperado para uma cavidade seria 1. **Pendência sem explicação.** |

---

## 7. Parte II-B — PI-3 e PI-2: placas de 8 e 4 camadas com regulador

### 7.1 Desenho experimental (II-B.0)
O PI-3 é um **hipercubo latino contínuo**: cada uma das 10 faixas de espessura recebe exatamente 1 000 amostras. O PI-2
é um sorteio sobre uma **grade** (37 espessuras, 11 permissividades). Nos dois, as entradas são independentes entre
si, o que valida a análise de sensibilidade. O regulador fica sempre perto do centro; o arranjo A1, com a porta
observada, pode estar em qualquer ponto. As placas vão de cerca de 11 × 8 cm a 46 × 46 cm.

### 7.2 Visão geral (II-B.1)
A forma é a mesma do PI-4. Como as placas são maiores, o nulo cai mais baixo — mediana de **55 MHz no PI-3 e 70 MHz no
PI-2** — e fica **dentro da banda normativa** de 30 MHz a 1 GHz.

### 7.3 H3 e o número de cavidades (II-B.2)

**Previsão a partir das folhas de dados.** Só as cavidades entre um plano de alimentação e um de terra armazenam carga
entre os trilhos. Cavidades entre dois planos de terra não contam. Nos três subconjuntos multicamadas há **duas**
cavidades alimentação–terra, ligadas em paralelo pelas vias, então a capacitância deve ser o dobro da de uma cavidade.

| Subconjunto | Cavidades no total | Cavidades alimentação–terra | Razão medida (mediana) |
|---|---|---|---|
| PI-2 | 3 | 2 | **2,02** |
| PI-4 | 5 | 2 | **2,13** |
| PI-3 | 7 | 2 | **2,03** |
| PI-1 | 1 | 1 | 0,45 (pendente) |

**Conclusão.** A previsão se confirmou em três topologias diferentes. Para a união dos subconjuntos, o atributo correto
é o **número de cavidades entre alimentação e terra**, e não o total. Os dois subconjuntos novos não têm bloco
descasado; só a primeira linha do PI-2 (simulação 110000) não descreve seu arquivo e foi descartada.

### 7.4 H1 e H5 (II-B.3)
A janela fixa falha pelo mesmo motivo do PI-1, porque o nulo é baixo. Com a janela adaptativa, **99,6 % (PI-3) e
99,9 % (PI-2)** das curvas ficam em ±0,10 de −1. A passividade vale em todas as curvas do PI-2. No PI-3, duas de
10 000 curvas têm parte real negativa num único ponto, em 1 MHz, com cerca de 1 % do módulo: resíduo numérico do
simulador.

### 7.5 Modelo substituto (II-B.4)

| Subconjunto | R² global | R² de $\lvert Z\rvert_{\max}$ | Erro médio em $\lvert Z\rvert$ |
|---|---|---|---|
| PI-4 | 0,97 | 0,99 | 10 % |
| PI-3 | 0,96 | 0,99 | 14 % |
| PI-2 | 0,90 | 0,99 | 24 % |

A curva inteira é mais difícil nos subconjuntos novos, porque o tamanho da placa varia e há muito mais ressonâncias
acima do nulo.

### 7.6 Sensibilidade (II-B.5)

Índice $S_1$ (RBD-FAST), fração da variância de cada saída explicada por cada entrada:

| Entrada | $\log\lvert Z\rvert$ 1 MHz | $f_{\rm nulo}$ | $\log\lvert Z\rvert$ no nulo | $\log\lvert Z\rvert$ 1 GHz |
|---|---|---|---|---|
| espessura $h$ | 0,41 – 0,47 | ≈ 0,0 – 0,05 | 0,34 – 0,59 | **0,74 – 0,94** |
| largura e altura $a$, $b$ | ≈ 0,5 somadas | **≈ 0,8 somadas** | ≈ 0,15 | ≈ 0 |
| permissividade $\varepsilon_r$ | 0,06 – 0,07 | 0,10 – 0,11 | ≈ 0,02 | ≈ 0 |
| tangente de perdas (só PI-2) | 0 | 0 | **0,15** | 0 |
| posição da porta $u$, $v$ | ≈ 0 | ≈ 0 | ≈ 0 | ≈ 0 |

**Leitura.** Em 1 MHz vale o capacitor, $h/(\varepsilon_r A)$. A frequência do nulo depende da área e não da
espessura, porque $C \propto 1/h$ e $L_{\rm eq} \propto h$ se cancelam no produto $LC$. A profundidade do nulo depende
da resistência, por isso a tangente de perdas aparece ali. Em 1 GHz, na região indutiva, domina a espessura.

### 7.7 Três leis de livro-texto nos dados (II-B.6)

1. **Placas paralelas.** $\log\lvert Z(1\,{\rm MHz})\rvert$ contra $\log[h/(\varepsilon_r A)]$ tem inclinação
   1,03 (PI-3) e 1,05 (PI-2), com $r^2 \ge 0{,}997$.
2. **Indutância de espalhamento.** $L_{\rm eq} = 1/[(2\pi f_{\rm nulo})^2 C]$ cresce quase linearmente com $h$
   ($r = 0{,}99$ e $0{,}97$ entre os logaritmos), entre cerca de 0,25 e 2,6 nH, e não depende do tamanho da placa.
3. **Modos de cavidade.** O primeiro pico acima do nulo cai sobre o TM$_{10}$ da maior dimensão (mediana de 0,995 da
   previsão). Com a porta longe do nó desse modo, **98 a 99 % das curvas acertam em ±5 %**. Com a porta perto do nó,
   no meio da placa, o TM$_{10}$ não é excitado e o primeiro pico salta para 2·TM$_{10}$, que é o TM$_{20}$.

**Consequência para o PI-4.** A porta do PI-4 fica no centro da placa, que é nó do TM$_{10}$ e do TM$_{01}$. A
ausência desses modos, que tinha levado a declarar H2 refutada, é exatamente o que a teoria prevê para essa posição.
H2 passa a **confirmada, condicionada à posição da porta**. O pico do PI-4 compatível com TM$_{11}$ continua sem
explicação, porque o centro também é nó desse modo.

---

## 8. Parte III — Síntese das hipóteses

| H | Requisito | Hipótese | Evidência principal | Status |
|---|---|---|---|---|
| H1 | R1 | Comportamento capacitivo (inclinação −1) | PI-4: −1,020 ± 0,006; PI-3 e PI-2: > 99 % em ±0,10; PI-1: 91 % em ±0,10 | **Confirmada**; exige janela adaptativa |
| H2 | R5 | Ressonâncias nos modos da cavidade | PI-3 e PI-2: 98–99 % em ±5 % do TM$_{10}$ com a porta fora do nó; PI-4: ausência explicada pelo nó | **Confirmada**, condicionada à posição da porta |
| H3 | R2 | Escala da capacitância e número de cavidades | fator 2 em três topologias com 2 cavidades alimentação–terra | **Confirmada**; PI-1 pendente |
| H4 | R3 | Monotonicidade antes do nulo | 100 % no PI-4 | **Confirmada** |
| H5 | R4 | Passividade | 100 % em PI-4, PI-1 e PI-2; 2 resíduos numéricos no PI-3 | **Confirmada**; restrição obrigatória |

---

## 9. Parte IV — Redes neurais informadas por física (PINN)

### 9.1 A ideia
Uma PINN é uma rede neural comum treinada com uma **Loss function** de dois termos. O primeiro mede o erro contra os
dados. O segundo mede o quanto a rede desobedece a uma lei física conhecida. As derivadas necessárias são calculadas
por **diferenciação automática**, a mesma ferramenta que treina a rede.

### 9.2 O que é $\hat y$ e de onde vêm −1, +1 e −1
$\hat y$ é a **saída da rede**: a previsão de $\log_{10}\lvert Z_{11}\rvert$. O chapéu indica "estimado"; sem chapéu,
$y$ é o valor da simulação. Abaixo do nulo:

$$\lvert Z\rvert = \frac{h}{2\pi f\,\varepsilon_0\,\varepsilon_r\,A}
\quad\Longrightarrow\quad
\log\lvert Z\rvert = (+1)\log h + (-1)\log\varepsilon_r + (-1)\log f - \log(2\pi\varepsilon_0 A)$$

Cada coeficiente é a derivada de $\log\lvert Z\rvert$ em relação ao logaritmo daquela grandeza. Multiplicar $f$ por 10
divide $\lvert Z\rvert$ por 10 (−1). Multiplicar $h$ por 10 multiplica $\lvert Z\rvert$ por 10 (+1). Multiplicar
$\varepsilon_r$ por 10 divide $\lvert Z\rvert$ por 10 (−1).

### 9.3 A Loss function

$$\mathcal{L}_{\rm dados} = \frac{1}{N}\sum_{i=1}^{N}(\hat y_i - y_i)^2
\qquad
\mathcal{L}_{\rm física} = \frac{1}{M}\sum_{j=1}^{M}\left[\left(\frac{\partial\hat y}{\partial\log f}+1\right)^2
+\left(\frac{\partial\hat y}{\partial\log h}-1\right)^2+\left(\frac{\partial\hat y}{\partial\log\varepsilon_r}+1\right)^2\right]_j$$

$$\mathcal{L}_{\rm total} = \lambda_d\,\mathcal{L}_{\rm dados} + \lambda_f\,\mathcal{L}_{\rm física}$$

Os $N$ pontos de dados são simulações. Os $M$ **pontos de colocação** são combinações de parâmetros sorteadas em todo
o espaço de projeto, sem simulação: neles só se avalia a física.

### 9.4 Arquitetura

| Item | Valor |
|---|---|
| Tipo | perceptron multicamadas (MLP) totalmente conectado |
| Entradas | 9: os 8 parâmetros do PI-4 (com $h$ e $\varepsilon_r$ em log) e $\log f$, normalizados |
| Camadas ocultas | 2 × 64 neurônios |
| Ativação | **tanh** |
| Saída | 1 neurônio linear, $\hat y$ |
| Parâmetros treináveis | 4 865 |
| Pontos de colocação | 256 |
| Pesos | $\lambda_d = \lambda_f = 1$ |
| Otimizador | Adam, taxa de aprendizado $3\times10^{-3}$, 2 000 épocas |
| Região | 8 primeiras frequências (região quase-estática) |

**Por que tanh e não ReLU.** Treinar a Loss física exige o gradiente de uma derivada da rede, o que envolve a
**segunda derivada** da ativação. A ReLU tem segunda derivada nula em quase todo ponto e descontínua na origem; a tanh
é suave em todas as ordens.

### 9.5 Demonstração de extrapolação (IV.1)
A rede foi treinada com **10 simulações de dielétricos finos** e testada nos espessos, fora da faixa de treino.

| Modelo | R² de extrapolação |
|---|---|
| Rede só com dados | negativo (−3,9): não extrapola |
| PINN | **0,96** |

A física guia a rede onde não há dados. **Limite:** a demonstração usa só a região quase-estática, onde a lei é
conhecida em forma fechada. A curva completa, com nulo e ressonâncias, é o problema do TCC II.

### 9.6 Fronteira de Pareto (IV.2)
Variando o peso da física de 0 a 10: sem física, a violação das derivadas é mais de cem vezes maior e o R² de
extrapolação cai para 0,74. O ganho satura perto de peso 1. O treinamento por **currículo** não trouxe ganho neste
problema, que não é rígido.

### 9.7 Painel de métricas (IV.3)

Treino com 10 ou 20 simulações finas (TDIEL < 40 mil), três sementes. Interpolação: as demais simulações finas.
Extrapolação: as espessas.

| Categoria | Métrica | Alvo | Só dados (20) | PINN (10) | PINN (20) |
|---|---|---|---|---|---|
| Dados | Erro relativo $L_2$ de $\lvert Zvert$, treino | < 1–5 % | ✅ 0,8 % | ✅ 1,9 % | ✅ 2,2 % |
| Dados | Erro relativo $L_2$, interpolação | < 1–5 % | ❌ 29 % | ❌ 17 % | ✅ 4,7 % |
| Dados | $R^2$ interpolado | > 0,99 | ❌ 0,931 | ❌ 0,966 | ✅ 0,999 |
| Física | Resíduo $\mathcal{L}_{m física}$ | < $10^{-3}$ | ❌ 0,91 | ✅ $6{,}5	imes10^{-4}$ | ✅ $3{,}6	imes10^{-4}$ |
| Generalização | $R^2$ em extrapolação | > 0,90–0,95 | ❌ 0,744 | ✅ 0,965 | ✅ 0,994 |
| Otimização | Razão de gradientes $\lVert
abla\mathcal{L}_{m dados}Vert/\lVert
abla\mathcal{L}_{m física}Vert$ | ≈ 1 | — | ❌ 0,03 | ❌ 0,10 |
| Desempenho | Tempo de inferência, 1 projeto | < 1 ms | ✅ | ✅ | ✅ 16–29 µs; 2,6 µs em lote |

**Leitura.**
- **A rede só com dados decora o treino.** Tem o menor erro de treino, mas erra 29 % ao lado, dentro da mesma faixa. O
  expoente de $h$ que ela aprende vale +0,65 ± 0,29 e varia de ponto para ponto; a PINN aprende +1,00 ± 0,005.
- **O erro de treino maior da PINN é esperado.** Ela impõe +1 para o expoente de $h$, mas os dados têm +0,955, porque
  a fórmula de placas paralelas ignora o efeito de borda. Passo do TCC II: aprender o expoente em vez de fixá-lo
  (PINN inversa).
- **A razão de gradientes revela desequilíbrio.** O gradiente da Loss física é de 10 a 30 vezes maior que o da Loss de
  dados. Aqui os dados ainda são ajustados com 2 % de erro, mas na curva completa isso tende a fazer a rede ignorar os
  dados. Correção: balanceamento adaptativo dos pesos $\lambda$ (Wang, Teng e Perdikaris, 2021).
- **Os alvos são referências, não normas.** O resíduo "< $10^{-3}$" depende da escala da Loss: aqui equivale a um erro
  típico de 0,03 no expoente.

### 9.8 Hardware

Todo o processamento roda em CPU (Ryzen 7 5825U, 8 núcleos e 16 threads, 15 GB de RAM): cerca de 3 s por treino da
demonstração. Uma rede de 4 865 pesos não se beneficia de GPU, porque o custo de transferir os dados para a placa
supera o cálculo. Sobre as GPUs disponíveis:

| GPU | Situação para PyTorch |
|---|---|
| Radeon integrada do Ryzen 7 5825U (Linux) | sem suporte oficial no ROCm; divide a RAM com a CPU; não compensa |
| RX 570 (Windows) | arquitetura Polaris, fora do ROCm atual; só via `torch-directml`, sem garantia de suporte às derivadas de segunda ordem de que a Loss física depende; seria preciso testar antes de confiar |
| Google Colab (T4) | opção prática se o TCC II precisar de GPU, por exemplo para a curva completa com 20 000 simulações × 334 frequências |

---

## 10. Parte V — Inferência causal

**Pergunta.** Qual o efeito *isolado* de uma variável, como a espessura, sobre a margem normativa?

- **Num único subconjunto** amostrado por hipercubo latino, as entradas foram atribuídas pelo experimentador. Não há
  confundimento, e a análise de sensibilidade já mede o efeito.
- **Na união de subconjuntos**, o subconjunto de origem e o número de cavidades passam a influenciar ao mesmo tempo as
  entradas e a resposta: é um **confundidor**.

**Isso não é motivo para retirar a união.** O confundidor é **observado** (cada linha sabe de onde veio), e variável
observada se ajusta: estratificando por subconjunto, incluindo-a como atributo (o critério *backdoor* do `dowhy` faz
isso a partir do grafo causal) ou comparando apenas dentro da mesma topologia.

**Teste de refutação (V.2).** A estimativa feita com os dados contaminados do PI-4 dá +0,43 em vez de +1 e **mesmo
assim passa no teste de placebo**. Refutação estatística verifica a robustez da estimativa, não a fidelidade dos dados.

---

## 11. Parte VI — Situação e próximos passos

| Período | Marco | Situação |
|---|---|---|
| set. 2026 | **M1** — pipeline validado contra propriedades analíticas | ✅ cumprido |
| out. 2026 | integridade do PI-4 | ✅ diagnosticada; reportar à TUHH |
| out. 2026 | PI-3 e PI-2 | ✅ reduzidos direto do zip; confirmar a porta P11 |
| nov. 2026 | **M2** — 4 subconjuntos e referência com R² > 0,80 | 🟡 4 de 4 reduzidos; falta a união (`load_multi_subset`) |
| nov. 2026 | normas | ⬜ tabular CISPR 32 A/B e IEC 61000-6-3/6-4 |
| dez. 2026 | entrega do TCC I | ⬜ |
| mar.–abr. 2027 | **M3** — PINN da curva completa superando a ablação | ⬜ |
| abr.–mai. 2027 | camada normativa: $Z(f)$ → ruído → emissão → margem em dB | ⬜ |
| mai.–jun. 2027 | **M4** — otimização (NSGA-II) e interpretabilidade (SHAP) | ⬜ |
| jul. 2027 | defesa | ⬜ |

### Pendências abertas
1. **Porta P11** do PI-3 e do PI-2: equivalência assumida com a porta do PI-4; conferir na folha de dados.
2. **PI-1** com razão 0,45 em vez de 1.
3. **Pico compatível com TM$_{11}$ no PI-4**, que não deveria ser excitado no centro da placa.
4. **Bloco 1000–1499 do PI-4**: reportar aos mantenedores da TUHH.

---

## Glossário

| Termo | Significado |
|---|---|
| PDN | rede de distribuição de energia: planos, vias e capacitores que levam a alimentação aos CIs |
| Cavidade | par de planos paralelos separados por dielétrico |
| Autoimpedância $Z_{11}$ | razão tensão/corrente na própria porta, com as demais em aberto |
| Parâmetros S | matriz de espalhamento: ondas refletidas e transmitidas, normalizadas a $Z_0$ |
| Touchstone | formato de arquivo-texto padrão para parâmetros S |
| Nulo de série | ressonância série entre a capacitância da placa e a indutância das vias |
| Modo TM$_{mn}$ | ressonância de cavidade com campo elétrico normal aos planos e $m$, $n$ meias-ondas nas direções $x$, $y$ |
| Decap | capacitor de desacoplamento; ESR e ESL são sua resistência e indutância série equivalentes |
| mil | milésimo de polegada, 25,4 µm |
| Hipercubo latino (LHS) | amostragem que divide cada faixa em $n$ intervalos e usa cada um exatamente uma vez |
| Modelo substituto | modelo rápido que imita uma simulação cara |
| R² | coeficiente de determinação; 1 é ajuste perfeito, 0 é prever a média, negativo é pior que a média |
| Índice de Sobol $S_1$ | fração da variância da saída explicada por uma entrada sozinha |
| Loss function | função que o treinamento minimiza |
| Ponto de colocação | ponto do espaço de entradas, sem simulação, onde só se avalia a Loss física |
| Confundidor | variável que influencia ao mesmo tempo a causa e o efeito estudados |
