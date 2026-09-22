# Spec: Restrições físicas para a função de perda

**Versão:** 1.0
**Data:** 2026-08-01
**Status:** verificado empiricamente sobre 40 configurações (semente 42)

---

## Por que esta spec existe

O núcleo científico do TCC é a hipótese de que restrições físicas conhecidas
melhoram a generalização em regime de poucos dados. Essa hipótese só é testável
se as restrições forem **componentes isolados e desativáveis**: a ablação precisa
ser uma mudança de configuração, nunca uma edição de código.

Além disso — e esta é a lição mais cara aprendida até aqui — **uma restrição só
entra na função de perda depois de verificada sobre os dados**. Ver "Registro de
refutação" adiante.

---

## Constantes da geometria (subconjunto PDN 6 camadas)

```
a = 5800 mil = 147,32 mm      # XWIDTH
b = 4000 mil = 101,60 mm      # YWIDTH
ε₀ = 8,8541878128e-12 F/m
c₀ = 299792458 m/s
```

---

## R1 — Forma capacitiva em baixa frequência  ✅ CONFIRMADA

**Enunciado.** Abaixo do nulo de série, `|Z11(f)| ∝ 1/f`, isto é, a derivada
`d log10|Z11| / d log10 f` vale −1.

**Evidência.** Inclinação medida sobre os 8 primeiros pontos de frequência
(f < 25 MHz). Verificada em **todas as 985 configurações** em 2026-08-11
(`notebooks/04_sensibilidade_fisica.py`):

```
985 configs   média  −1,0197   desvio-padrão  0,0062   faixa  [−1,0373 ; −0,9800]
              100,0 % dentro de [−1,05 ; −0,95]
 40 configs   média  −1,018    desvio-padrão  0,008    (verificação anterior)
```

**Status: confirmada em escala plena e verificada entre topologias.** Nenhuma
configuração viola o critério. É a única restrição que pode ser imposta globalmente
sem ressalva.

**Verificação cruzada (2026-08-17).** No subconjunto *PWR/GND Plane 11×11 Array*, de
**uma** cavidade, a inclinação é **−1,0001 ± 0,0113** com 100 % de conformidade. R1
transfere entre topologias.

⚠️ **Mas a janela de medição não transfere.** A regra dos 8 primeiros pontos foi
calibrada no subconjunto de 6 camadas. No de 1 cavidade os decaps empurram o nulo de
série para 27,7 MHz (mediana), e a mesma regra derruba a conformidade para **9 %**. A
janela quase-estática passa a ser definida por configuração como `f < f_nulo/K`, com
`K ≥ 3` e no mínimo 3 pontos. Ver `spec/UNIAO_SUBCONJUNTOS.md`.

**Uso.** Termo `L_cap`, penalizando o desvio da derivada logarítmica em relação
a −1. Formulação invariante a fator multiplicativo — ver R2.

---

## R2 — Escala da capacitância  ⚠️ CONFIRMADA APENAS COMO TENDÊNCIA

**Enunciado testado.** `C = ε₀ ε_r a b / h` (placas paralelas, cavidade única).

**Evidência (985 configurações, 2026-08-11).** A razão `C_extraída/C_analítica`
tem mediana 2,130, mas a população é **heterogênea**:

| grupo | n | % |
|---|---|---|
| razão < 1,5 | 169 | 17,2 % |
| **1,5 ≤ razão < 3,0 (duas cavidades)** | **653** | **66,3 %** |
| 3,0 ≤ razão < 10 | 121 | 12,3 % |
| razão ≥ 10 | 42 | 4,3 % |

Restringindo a regressão `log10|Z11(1 MHz)| ~ log10(TDIEL) + log10(ε_r)` à população
conforme, os expoentes batem com a física:

| amostra | n | coef. log10(TDIEL) | coef. log10(ε_r) | R² |
|---|---|---|---|---|
| todas | 985 | +0,428 ± 0,056 | −0,574 ± 0,237 | 0,197 |
| **só conformes** | **653** | **+0,952 ± 0,012** | **−0,974 ± 0,048** | **0,973** |
| previsto pela física | — | +1,000 | −1,000 | — |

**Interpretação.** Para dois terços do conjunto, a porta acopla-se a **duas cavidades em
paralelo** e a lei de placas paralelas vale com precisão (R² = 0,973). O fator ≈ 2,1 fica
confirmado. O terço restante desvia por motivo **ainda não identificado**.

**O que já foi descartado como causa do desvio:**

- *artefato de porta* — os 36 portos de uma mesma configuração dão razões idênticas
  a 0,08 %, como a física quase-estática exige (em 1 MHz a placa é um capacitor único);
- *desalinhamento global entre `parameter.csv` e os `.s36p`* — R² real 0,197 contra
  0,0018 ± 0,0019 com rótulos embaralhados (200 repetições);
- *desalinhamento parcial por permutação de linhas* — o pareamento de `ε_r/h` observado
  contra o do CSV **não é bijetivo** (916 pareamentos usando apenas 514 linhas distintas)
  e o teste KS rejeita que os desviantes venham da mesma distribuição (p = 0,007);
- *dependência das features de projeto* — as médias das 8 features são estatisticamente
  indistinguíveis entre conformes e desviantes.

**Direção do desvio:** dielétricos finos (< 10 mil) tendem a razão < 1; espessos
(> 50 mil) a razão ≫ 1. Compatível, no extremo espesso, com a ressalva de Schierholz et al.
(T-CPMT 2023, Seç. IV-A): *"For very long vias, the potential cannot be assumed to be
constant across the via as is usually assumed for the cavity model wave propagation."*
O extremo fino permanece sem explicação.

**Verificação cruzada (2026-08-17).** No subconjunto de **uma** cavidade a razão é
**0,46** — abaixo da fórmula, e não acima — subindo monotonicamente de 0,43 em `h` de
1–2 mil até 0,90 em 8–12 mil. O modelo de uma capacitância parasita em série foi testado
e **refutado** (`C_série` implicado varia de 51,7 a 11,0 nF; R² negativo em log). A escala
absoluta, portanto, **não transfere entre topologias**, o que reforça a formulação do termo
quase-estático apenas sobre a derivada logarítmica, invariante a fator multiplicativo.

**Uso.** **Não** impor R2 globalmente. Ou restringir à população conforme, ou estimar `γ`
por configuração, ou ponderar o termo pela confiança. A ablação deve reportar R2 com e sem
restrição de domínio — é resultado, não detalhe de implementação.

**Uso.** **Não** impor o valor analítico. Usar `C_ef = γ · ε₀ ε_r a b / h`, com
`γ` estimado sobre o conjunto de treinamento. A informação de forma (R1) é a
restrição forte; a de escala é um termo auxiliar de peso menor.

---

## R3 — Monotonicidade até o nulo de série  ✅ CONFIRMADA

**Enunciado.** `|Z11(f)|` decresce monotonicamente até o nulo de série, situado
em torno de 100 MHz.

**Uso.** Termo `L_mono`, função de dobradiça sobre diferenças de pontos
consecutivos abaixo de `f₀`. Suprime oscilação espúria em regiões pouco
amostradas.

---

## R4 — Passividade  ✅ OBRIGATÓRIA POR CONSTRUÇÃO

**Enunciado.** `Re{Z11(f)} ≥ 0` ∀ f. Equivalente: valores singulares de `S` ≤ 1.

**Uso.** Termo `L_pass`, dobradiça quadrática. Aplicável apenas à variante que
prediz impedância complexa.

---

## R5 — Localização modal  ❌ REFUTADA para `Z11` nesta banda

**Enunciado testado.** Máximos de `|Z11|` nas frequências
`f_mn = c₀/(2√ε_r) · √((m/a)² + (n/b)²)`.

Para ε_r ∈ [2,5; 4,5]: TM₁₀₀ ∈ [480; 644] MHz, TM₀₁₀ ∈ [695; 933] MHz — ambos
internos à banda de análise.

**Evidência contrária.** A resposta **não** apresenta máximos pronunciados nessas
frequências. Após o nulo de série em ~100 MHz, `|Z11|` cresce monotonicamente até
o limite superior da banda. A densidade dos arranjos de vias amortece fortemente
os modos e a autoimpedância de uma única porta não os evidencia.

**Uso.** **Nenhum.** Não incorporar à perda. Reaberto como hipótese secundária a
investigar em `Z_ij` (i≠j) e em subconjuntos com menor densidade de vias.

### Registro de refutação — como o erro quase passou

Uma primeira análise reportou "erro mediano de casamento modal de 3,1%, com 83%
das amostras abaixo de 10%" e foi tomada como confirmação de R5. Estava errada
por dois motivos encadeados:

1. o detector de picos localizava máximos locais de amplitude desprezível —
   ondulação numérica, não ressonância;
2. com 15 modos previstos dentro da banda, **qualquer** frequência dista poucos
   pontos percentuais de algum modo. A estatística media a densidade do espectro
   modal, não a concordância física.

O erro só apareceu ao **plotar a região modal e olhar**: as curvas subiam
monotonicamente, sem picos, enquanto as linhas verticais dos modos previstos não
coincidiam com nada.

**Regra que decorre disso, obrigatória neste projeto:** nenhuma estatística
agregada sustenta uma conclusão antes de ser inspecionada graficamente. Vale para
métricas de modelo tanto quanto para verificação física.

---

## Interface exigida

Cada restrição é uma classe independente com a mesma assinatura, ativável por
configuração:

```python
class PhysicsTerm(Protocol):
    name: str
    def __call__(self, y_pred, x, freq) -> Tensor:  # escalar, ≥ 0
        ...
```

Requisitos:
- retorno **escalar não negativo**, zero quando a restrição é satisfeita
- diferenciável em `y_pred`
- sem estado entre chamadas
- custo O(nf) — nenhuma restrição exige diferenciação automática de segunda ordem

## Testes obrigatórios por termo

1. **caso analítico** — curva sintética que satisfaz exatamente a restrição ⇒ retorno < 1e-10
2. **monotonicidade** — perturbação crescente ⇒ retorno crescente
3. **forma e tipo** — escalar, dtype do modelo, sem NaN
4. **gradiente** — `grad` finito e não nulo fora do ótimo

## Critérios de aceitação

- [ ] cada termo desativável por configuração, sem edição de código
- [ ] ablação completa reprodutível por um único arquivo de config
- [ ] os 4 testes acima passam para cada termo ativo
- [ ] R5 permanece desativado até que haja evidência gráfica em contrário
