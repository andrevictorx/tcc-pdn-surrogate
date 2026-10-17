# Spec: Hipóteses físicas e consistência dos dados

**Criado em:** 2026-10-17 · **Fonte dos números:** `notebooks/TCC_PDN_Colab.ipynb` e medições registradas abaixo
**Relaciona-se com:** `spec/PHYSICS_SPEC.md` (R1–R5), `spec/UNIAO_SUBCONJUNTOS.md`, `src/data/subsets.py`

## Por que esta spec existe

Uma PINN tem duas Losses: uma que puxa a rede para os dados e outra que a puxa para a física. Se os dois não
concordam, os gradientes brigam, e a rede ou ignora os dados ou ignora a física. Isso acontece de dois jeitos:

1. **Dado inconsistente.** Rótulo que não corresponde à curva, empilhamento mal documentado, porta errada. Exemplo
   real: com a planilha original do PI-4, a lei $C \propto \varepsilon_r/h$ dava R² = 0,20, e uma Loss física
   correta teria sido punida pelos dados.
2. **Hipótese aplicada fora da região em que vale.** Exemplo real: a monotonicidade (H4) é falsa em 6 % das placas
   com capacitores de desacoplamento. Uma Loss de H4 aplicada ao PI-1 empurraria a rede contra curvas corretas.

Esta spec define, para cada hipótese, **o enunciado exato, como medir, o critério de aceitação e onde vale**. Para
cada subconjunto, define os **portões de consistência** que os dados precisam passar antes de entrar em qualquer
modelo. Nenhum termo físico entra na Loss sem passar aqui.

---

## Parte A — Hipóteses físicas

### Convenções

- $\hat y = \log_{10}|Z_{11}|$; $f_{\rm nulo}$ = frequência de $\min|Z_{11}|$.
- $h_{\rm ef}$ = distância entre os planos de uma cavidade alimentação–terra (ver C4); $n_{pg}$ = número de cavidades
  alimentação–terra.
- **Uso na PINN:** *dura* = penalidade sempre ativa, alto peso; *branda* = penalidade com peso calibrado; *diagnóstico* =
  só medida, não entra na Loss.

### H1 — Comportamento capacitivo quase-estático

| | |
|---|---|
| **Enunciado** | Abaixo do nulo de série, $d\hat y/d\log_{10} f = -1$. |
| **Física** | Capacitor de placas paralelas: $\lvert Z\rvert = 1/(2\pi f C)$. |
| **Medição** | Ajuste linear de $\hat y$ contra $\log_{10} f$ na **janela adaptativa** $f < f_{\rm nulo}/3$, com pelo menos 3 pontos. A janela fixa de 8 pontos **não pode** ser usada: falha quando o nulo é baixo. |
| **Critério** | $\lvert s + 1\rvert \le 0{,}10$ em pelo menos 95 % das curvas elegíveis. |
| **Elegibilidade** | Curvas cuja fase em 1 MHz está entre −95° e −80° (regime capacitivo) e cuja janela tem ≥ 3 pontos. |
| **Uso na PINN** | Branda, só na janela adaptativa de cada curva. |

| Subconjunto | Resultado | Situação |
|---|---|---|
| PI-4 | 100 % (−1,020 ± 0,006) | ✅ |
| PI-3 | 99,6 % | ✅ |
| PI-2 | 99,9 % | ✅ |
| PI-1 | 91 % em ±0,10 | ⚠️ abaixo do critério: a grade de 3,34 MHz deixa só 2–3 pontos antes de $f_{\rm nulo}/3$ (mediana 3); refazer só com as curvas elegíveis |

### H2 — Ressonâncias nos modos de cavidade

| | |
|---|---|
| **Enunciado** | Os picos de $\lvert Z_{11}\rvert$ acima do nulo ocorrem em $f_{mn} = \frac{c_0}{2\sqrt{\varepsilon_r}}\sqrt{(m/a)^2+(n/b)^2}$, **desde que a porta não esteja num nó do modo**. |
| **Medição** | 1º pico com proeminência > 0,3 década acima do nulo, comparado ao modo previsto; acoplamento da porta $\kappa_{mn} = \lvert\cos(m\pi u)\cos(n\pi v)\rvert$, com $u = x/a$, $v = y/b$. |
| **Critério** | Com $\kappa > 0{,}5$: pico em ±5 % de $f_{mn}$ em pelo menos 90 % das curvas que têm pico. |
| **Uso na PINN** | Branda, ponderada por $\kappa_{mn}$. Nunca como restrição de modo fixo, independente da porta. |

| Subconjunto | Resultado | Situação |
|---|---|---|
| PI-3 | TM10: 98 % com $\kappa > 0{,}5$ | ✅ |
| PI-2 | TM10: 99 % com $\kappa > 0{,}5$ | ✅ |
| PI-4 | TM10 e TM01 ausentes, como prevê $\kappa = 0$ no centro; pico compatível com TM11 em 313 de 601 curvas, sem explicação ($\kappa_{11} = 0$) | ⚠️ não usar H2 no PI-4 até explicar o pico |
| PI-1 | não testada (placa de 12 × 10 pol: TM10 ≈ 240 MHz para εr = 4,2) | ⬜ pendente |

### H3 — Escala da capacitância

| | |
|---|---|
| **Enunciado** | $C_{\rm medida} = n_{pg}\,\varepsilon_0\varepsilon_r A/h_{\rm ef} + C_{\rm decaps}$. |
| **Medição** | $C = -1/(2\pi f\,\mathrm{Im}\{Z_{11}\})$ em 1 MHz, só nas curvas elegíveis de H1. |
| **Critério** | Mediana de $C_{\rm medida}/C_{\rm prevista}$ entre 0,95 e 1,15. O limite superior acomoda o **campo de borda**, que cresce com $h$ (no PI-4, razão e $h$ têm $r = 0{,}86$). |
| **Uso na PINN** | Através das derivadas, que não dependem de escala: $\partial\hat y/\partial\log h = +1$ e $\partial\hat y/\partial\log\varepsilon_r = -1$, branda. O valor absoluto de $C$ só entra como portão de consistência (C1), não como Loss. |

| Subconjunto | $n_{pg}$ | $h_{\rm ef}$ | Razão / $n_{pg}$ | Situação |
|---|---|---|---|---|
| PI-1 | 1 | $2h + 1$ mil | 0,996 | ✅ após a correção de C4 |
| PI-2 | 2 | $h$ | 1,01 | ✅ |
| PI-4 | 2 | $h$ | 1,06 (expoentes +0,973 e −1,016) | ✅ |
| PI-3 | 2 | $h$ | 1,01 | ✅ |

### H4 — Monotonicidade antes do nulo

| | |
|---|---|
| **Enunciado** | Entre 1 MHz e $f_{\rm nulo}$, $\lvert Z_{11}\rvert$ é estritamente decrescente. |
| **Validade** | **Só em placas sem capacitores de desacoplamento.** Com capacitores, cada um tem a sua própria ressonância série, e entre duas ressonâncias aparece uma antirressonância (pico) antes do nulo principal. |
| **Critério** | 100 % das curvas elegíveis. |
| **Uso na PINN** | Dura, pune $\partial\hat y/\partial\log f > 0$ abaixo do nulo, **só nos subconjuntos sem capacitores**. |

| Subconjunto | Resultado | Situação |
|---|---|---|
| PI-4, PI-3, PI-2 | 100 % | ✅ |
| PI-1 | 94,1 % | ❌ fora do domínio de validade: **não aplicar H4 ao PI-1** |

### H5 — Passividade

| | |
|---|---|
| **Enunciado** | $\mathrm{Re}\{Z_{11}(f)\} \ge 0$ em toda frequência. |
| **Física** | Potência média absorvida $P = \tfrac12\lvert I\rvert^2\,\mathrm{Re}\{Z_{11}\} \ge 0$ numa rede sem fonte. |
| **Critério** | Nenhuma violação maior que 2 % de $\lvert Z_{11}\rvert$ no mesmo ponto. |
| **Uso na PINN** | Dura, em toda a banda. |

| Subconjunto | Resultado | Situação |
|---|---|---|
| PI-4, PI-1, PI-2 | 100 % | ✅ |
| PI-3 | 2 de 10 000 curvas com 1 ponto negativo em 1 MHz, cerca de 1 % do módulo | ✅ dentro da tolerância numérica |

---

## Parte B — Portões de consistência dos dados

Cada subconjunto só entra num modelo depois de passar por todos os portões. Uma linha que falha num portão marcado
como **excluir** sai do treino; uma linha que falha num portão marcado como **marcar** fica no treino, mas fora dos
testes de hipótese.

| Portão | O que verifica | Ação se falhar |
|---|---|---|
| **C1 — planilha × arquivo** | $C_{\rm medida}/(n_{pg}C_{\rm prevista})$ dentro de ±25 % | excluir a linha |
| **C2 — índices** | todo `simu_index` do CSV tem arquivo, e vice-versa | registrar; ausências podem ser esperadas |
| **C3 — porta** | a porta de interesse foi conferida na figura de numeração da folha de dados | bloquear o subconjunto |
| **C4 — empilhamento** | $n_{pg}$ e $h_{\rm ef}$ transcritos da folha **e confirmados por H3** | bloquear o subconjunto |
| **C5 — grade e janela** | a grade tem ≥ 3 pontos abaixo de $f_{\rm nulo}/3$ | marcar a curva como inelegível para H1/H3 |
| **C6 — regime capacitivo** | fase em 1 MHz entre −95° e −80° | marcar a curva como inelegível para H1/H3 |
| **C7 — passividade numérica** | H5 com tolerância de 2 % | excluir a linha |
| **C8 — desenho experimental** | faixas, independência das entradas, blocos de amostragem distintos | documentar e definir a estratificação |
| **C9 — versão dos dados** | arquivo e data da planilha usada | registrar no cache |

### Situação por subconjunto (17/10/2026)

| Portão | PI-1 | PI-2 | PI-4 | PI-3 |
|---|---|---|---|---|
| C1 | 17 de 36 199 fora de ±25 %: todas com $h \le 1{,}4$ mil, fase −50° em 1 MHz, ou seja, falham C6, e não C1 | 1 linha (simu 110000) | 1 de 985 após a correção | 0 |
| C2 | ✅ | ✅ | 15 ausentes, esperados segundo a TUHH (falha de simulação) | ✅ |
| C3 | ✅ porta 1 | ✅ P11 | ✅ P1 | ✅ P11 |
| C4 | ✅ $h_{\rm ef} = 2h + 1$ mil (corrigido em 17/10) | ✅ | ✅ | ✅ |
| C5 | ⚠️ grade de 3,34 MHz: 2–7 pontos na janela | ✅ | ✅ | ✅ |
| C6 | 17 curvas inelegíveis | ✅ | ✅ | ✅ |
| C7 | ✅ | ✅ | ✅ | ✅ |
| C8 | 67 % das linhas com $h$ nominal 4,4 e 75 % com $\varepsilon_r$ nominal 4,2: amostragem concentrada | grade de níveis; posição do regulador = função do tamanho da placa | **dois blocos com faixas de via diferentes**: estratificar | LHS contínuo; posição do regulador = função do tamanho da placa |
| C9 | cache de nov. 2023 | zip de fev. 2022 | **planilha corrigida pela TUHH, validada em 15/10/2026** | zip de jul. 2022 |

### Detalhe dos portões que já mudaram o projeto

- **C1 no PI-4.** O bloco 1000–1499 falhava (r = 0,02). A TUHH corrigiu a planilha. Com ela, r = 0,9997.
- **C4 no PI-1.** A folha de dados descreve a cavidade como tendo altura `diel_height`. A capacitância simulada só
  fecha com $h_{\rm ef} = 2\cdot$`diel_height` + 1 mil: duas camadas de dielétrico com uma camada de sinal de 1 mil
  entre elas. Como as camadas estão em série, as espessuras se somam:
  $1/C = \sum t_i/(\varepsilon_0\varepsilon_r A)$. Teste sem parâmetro livre: razão 0,996 (p5–p95 0,988–1,003).
- **C8 no PI-4.** O bloco 1000–1499 usa vias com raio de 3–9 mil e o bloco 1500–1999, de 10–20 mil. Na união, as
  entradas de via ficam correlacionadas pelo bloco. Consequências: a análise de sensibilidade usa só um bloco, e as
  divisões de treino e teste devem ser estratificadas por bloco.
- **C8 no PI-2 e no PI-3.** A posição do regulador tem correlação 1,00 com o tamanho da placa. Ela não entra como
  entrada independente.

---

## Parte C — Regras para os modelos

1. **Nenhuma linha que falhe em C1 ou C7 entra no treino.**
2. **Um termo físico só entra na Loss onde a hipótese foi aceita**, conforme a matriz abaixo.
3. **As curvas inelegíveis (C5, C6) ficam no treino de dados, mas fora dos pontos de colocação** de H1 e H3.
4. **Validação:** além da divisão aleatória, sempre reportar a **topologia retida** (treina em 3 subconjuntos e testa
   no 4º) e, no PI-4, a estratificação por bloco.
5. **Toda mudança nos dados reabre esta spec:** nova planilha, novo subconjunto ou nova porta exigem refazer as
   Partes A e B antes de treinar.

### Matriz de uso: hipótese × subconjunto

| | PI-1 | PI-2 | PI-4 | PI-3 |
|---|---|---|---|---|
| H1 (inclinação −1) | ⚠️ só nas curvas elegíveis | ✅ | ✅ | ✅ |
| H2 (modos, ponderados por κ) | ⬜ testar antes | ✅ | ❌ até explicar o TM11 | ✅ |
| H3 (derivadas em $h$ e $\varepsilon_r$) | ✅ com $h_{\rm ef}$ | ✅ | ✅ | ✅ |
| H4 (monotonicidade) | ❌ fora do domínio | ✅ | ✅ | ✅ |
| H5 (passividade) | ✅ | ✅ | ✅ | ✅ |

## Pendências

- [ ] H1 no PI-1 restrita às curvas elegíveis (C5 e C6): confirmar se passa de 95 %.
- [ ] H2 no PI-1: medir.
- [ ] Explicar o pico compatível com TM11 no PI-4.
- [ ] Explicar a fase de −50° em 1 MHz nas cavidades finas do PI-1 ($h \le 1{,}4$ mil).
- [ ] Implementar os portões C1–C9 como funções em `src/data/` com testes, e rodá-los em `load_multi_subset()`.
- [ ] Avisar a TUHH sobre a descrição da espessura na folha de dados do PI-1.
