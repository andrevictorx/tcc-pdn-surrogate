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

**Evidência.** Inclinação medida em 40 configurações, sobre os 8 primeiros
pontos de frequência (f < 25 MHz):

```
média  −1,018    desvio-padrão  0,008    faixa  [−1,029 ; −0,980]
```

**Uso.** Termo `L_cap`, penalizando o desvio da derivada logarítmica em relação
a −1. Formulação invariante a fator multiplicativo — ver R2.

---

## R2 — Escala da capacitância  ⚠️ CONFIRMADA APENAS COMO TENDÊNCIA

**Enunciado testado.** `C = ε₀ ε_r a b / h` (placas paralelas, cavidade única).

**Evidência.** Correlação log-log entre `C` extraída e `C` analítica:
`r = 0,64`. A razão `C_extraída / C_analítica` tem mediana 2,1 mas varia de
0,49 a 22,6.

**Interpretação.** A mediana ≈ 2 é compatível com uma porta acoplada a duas
cavidades em paralelo num empilhamento de seis camadas. A dispersão restante não
está explicada e depende de acoplamento entre cavidades.

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
