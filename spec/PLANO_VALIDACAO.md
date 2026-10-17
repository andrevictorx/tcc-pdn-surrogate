# Plano de validação: o que está sendo feito é consistente com a teoria?

**Criado e executado em:** 2026-10-17 · **Script:** `scripts/validacao_teorica.py` → `data/processed/validacao.json`
**Relaciona-se com:** `spec/CONSISTENCIA_DADOS.md` (hipóteses e portões), `spec/PHYSICS_SPEC.md`

## Objetivo

Verificar, de forma independente das análises que geraram as hipóteses, que:

- **A.** o pipeline numérico reproduz uma implementação de referência e respeita as propriedades de redes passivas;
- **B.** cada lei física usada no TCC concorda **quantitativamente** com os livros-texto, e não só em tendência;
- **C.** os resultados estatísticos e de modelos concordam com a literatura;
- **D.** código, notebook e documentos dizem a mesma coisa.

Cada item tem uma referência, um critério de aprovação fixado **antes** de olhar o resultado e o resultado obtido.
Quando um critério falhou, a falha foi investigada antes de qualquer mudança. As três falhas da primeira execução
estão registradas no fim, com o que se aprendeu de cada uma.

## Referências teóricas

| Código | Referência |
|---|---|
| [Bog] | E. Bogatin, *Signal and Power Integrity — Simplified*, 2. ed., Prentice Hall, 2010 |
| [Ott] | H. W. Ott, *Electromagnetic Compatibility Engineering*, Wiley, 2009 |
| [Pal] | L. S. Palmer, "Capacitance of a parallel-plate capacitor by the Schwartz-Christoffel transformation", *Trans. IEE Japan*, 1937 (fórmula de correção de borda para placas retangulares) |
| [TS] | Touchstone File Format Specification, v1.1 (EIA/IBIS) |
| [skrf] | scikit-rf 2.1, implementação de referência da conversão de parâmetros de rede |
| [Sch23] | M. Schierholz, Y. Hassab, C. Schuster, *IEEE Trans. CPMT*, v. 13, n. 10, 2023 |

---

## Bloco A — Fidelidade numérica do pipeline

| Item | O que verifica | Referência | Critério | Resultado | |
|---|---|---|---|---|---|
| V1 | Conversão $Z = Z_0(I+S)(I-S)^{-1}$, matriz inteira, 10 arquivos dos 4 subconjuntos | [skrf] | $\lVert Z - Z_{\rm skrf}\rVert/\lVert Z_{\rm skrf}\rVert < 10^{-10}$ | $3{,}1\times10^{-14}$ | ✅ |
| V2 | Reciprocidade $S = S^T$ | teoria de redes | $\max\lvert S - S^T\rvert < 10^{-4}$ | $3{,}3\times10^{-5}$ | ✅ |
| V3 | Passividade da rede de N portas: valores singulares de $S \le 1$ | teoria de redes | $\sigma_{\max} \le 1 + 10^{-6}$ | $1 + 8\times10^{-8}$ | ✅ |
| V4 | Cache = reprocessar o arquivo bruto | — | erro relativo $< 10^{-2}$ | $4{,}9\times10^{-4}$ (fase em float16 no PI-1) | ✅ |

## Bloco B — Física contra os livros-texto

| Item | Lei | Referência | Critério | Resultado | |
|---|---|---|---|---|---|
| V5 | Placas paralelas **com campo de borda** | [Bog] p. 133; [Pal]; [Ott] §11.4.6 | medido/Palmer = 1 ± 0,02 em cada subconjunto; ρ > 0,8 no PI-4; pF/pol² na faixa de Ott | medido/Palmer: **1,0002** (PI-4), 0,990 (PI-3), 0,989 (PI-2), 0,995 (PI-1); ρ = 0,93; 196 pF/pol² (5 mil) e 102 pF/pol² (10 mil) | ✅ |
| V6 | Inclinação abaixo do nulo: o desvio de −1 vem do LC série, $\lvert Z\rvert = (1-(f/f_0)^2)/(2\pi f C)$ | circuito LC série | \|medida − prevista\| < 0,02 | resíduos de −0,001 a −0,009 | ✅ |
| V7 | Indutância de espalhamento $L = 5{,}1\,h\ln(b/a)$ pH | [Bog] eq. 13-31 | $L = L_0 + k h$, com expoente de $(L - L_0)$ em $h$ = 1 ± 0,1; $L/h$ decresce com o raio da via | expoentes 0,96 / 1,00 / 1,01; $L_0$ ≈ 50–130 pH; $k$ = 27–70 pH/mil (Bogatin: 25–40 por par de planos); sinal do raio negativo | ✅ |
| V8 | Nulo de série $f_0 = 1/(2\pi\sqrt{LC})$ com $C \propto \varepsilon_r A/h$ e $L \propto h$ | [Bog] cap. 13 | expoentes de $A$ e $\varepsilon_r$ = −0,5 ± 0,1; de $h$ = 0 ± 0,15 | $A$: −0,504 / −0,507; $\varepsilon_r$: −0,498 / −0,498; $h$: +0,06 / +0,15 | ✅ |
| V9 | Modos $f_{mn} \propto 1/\sqrt{\varepsilon_r}$ e $\propto 1/\text{lado}$ | [Bog] eq. 12-20; [Ott] eq. 6-42 | expoente de $\varepsilon_r$ = −0,5; do lado = −1 | PI-1 (TM02): $\varepsilon_r$ −0,501; PI-3 (TM10): lado −0,997, $\varepsilon_r$ −0,501; PI-2: −1,000 e −0,501 | ✅ |
| V10 | Nós de tensão: modo só aparece se $\kappa = \lvert\cos(m\pi u)\cos(n\pi v)\rvert$ não for pequeno | teoria de cavidades | detecção > 90 % com κ > 0,5 e < 50 % com κ < 0,2 | 96–97 % × 5–7 %; PI-4: TM20 (κ = 1) em 100 % das curvas em que cai na banda | ✅ |
| V11 | Profundidade do nulo: na ressonância $X_C = \sqrt{L/C}$, e a perda dielétrica vale $R_d = \tan\delta\sqrt{L/C}$ | [Ott] eq. 10-3 ($Q = \sqrt{L/C}/R$) | ρ($\tan\delta\sqrt{L/C}$, $\mathrm{Re}\{Z\}$ no nulo) > 0,85; razão em [1; 3], porque a perda no cobre se soma | ρ = 0,95 / 0,97 / 0,88; razão 1,6 / 1,6 / 2,2: a perda dielétrica explica a escala e ~60 % do valor | ✅ |
| V12 | Passividade de $Z_{11}$ | teoria de redes | nenhuma curva com $\mathrm{Re}/\lvert Z\rvert < -2\,\%$ | 0 nos quatro | ✅ |
| V13 | Parte real em baixa frequência × perda dielétrica, $\mathrm{Re} \approx \tan\delta\cdot\lvert\mathrm{Im}\rvert$ | perda dielétrica | diagnóstico | razão 7,7 (PI-4), 6,8 (PI-3), 13 (PI-2), 1,8 (PI-1) | ⚠️ achado |

### O achado do V13: anomalia no ponto de 1 MHz

Nos três subconjuntos da família "Two Via Arrays" (PI-2, PI-3, PI-4), o ponto de 1 MHz tem uma parte real de 4 a
13 Ω, de 7 a 13 vezes a perda dielétrica esperada. Ela cai com $f^{-1,4}$ e quase não depende da geometria. Os
efeitos sobre $\lvert Z\rvert$:

| Subconjunto | Desvio mediano de $\lvert Z(1\,\text{MHz})\rvert$ da curva capacitiva | Curvas com desvio > 5 % | Em 4,3 MHz |
|---|---|---|---|
| PI-4 | +1,9 % | 1,2 % | — |
| PI-3 | +2,6 % | 25,7 % (placas pequenas, $f_0$ alto) | +0,3 % |
| PI-2 | +2,1 % | 27,7 % | — |
| PI-1 | +0,1 % | 0,1 % | — |

A teoria (capacitor: $\lvert Z\rvert\cdot f$ constante) não prevê nada assim, e o efeito some a partir do segundo
ponto da grade. A interpretação mais provável é um artefato numérico do simulador na frequência mais baixa. **Isso
afeta o alvo $\lvert Z\rvert_{\max}$, que é medido justamente em 1 MHz.** Virou o portão C10 de
`spec/CONSISTENCIA_DADOS.md`.

## Bloco C — Estatística e modelos contra a literatura

| Item | O que verifica | Referência | Resultado | |
|---|---|---|---|---|
| V14 | Ranking de sensibilidade de $\lvert Z\rvert_{\max}$ (Sobol) | [Sch23] Fig. 11 | 3 primeiras posições iguais (TDIEL, $\varepsilon_r$, raio da via A1) | ✅ |
| V15 | Modelo substituto atinge a meta da proposta | proposta do TCC | R² global 0,98 (PI-4), 0,96 (PI-3), 0,90 (PI-2); meta 0,90 | ✅ (topologia retida: pendente, M2) |
| V16 | As leis impostas à PINN são as que os dados seguem | V5, V6 | expoente de $h$: imposto +1, dados +0,973, e a diferença é o campo de borda de Palmer; inclinação em $f$: imposta −1, dados −1,02 a −1,04, e a diferença é o LC série | ⚠️ coerente, mas a lei imposta é a **assintótica** |

**Consequência do V16 para o TCC II.** A PINN de demonstração impõe os limites assintóticos (−1, +1, −1). Os dados
seguem as versões completas, que a validação mostrou valerem com precisão:

$$\lvert Z\rvert = \frac{1 - (f/f_0)^2}{2\pi f\,C}, \qquad C = n_{pg}\,\varepsilon_0\varepsilon_r\,\frac{A_{\rm Palmer}(h)}{h_{\rm ef}}$$

Usar essas formas na Loss física elimina o conflito entre dados e física medido no IV.3, de cerca de 1,4 ponto
percentual de erro de treino.

## Bloco D — Coerência interna

| Item | O que verifica | Resultado | |
|---|---|---|---|
| V17 | Testes automatizados | 52 de 52 | ✅ |
| V18 | Adaptadores × folhas de dados: portas, empilhamento, $n_{pg}$, $h_{\rm ef}$, dimensões | conferidos; testes de $h_{\rm ef}$ e $n_{pg}$ | ✅ |
| V19 | Notebook, `RESUMO_NOTEBOOK.md`, specs e Obsidian citam os mesmos números e status | atualizados nesta rodada: H1 do PI-1, H2 do PI-1 e do PI-4 (TM20), C10 | ✅ após a atualização |

---

## O que as falhas da primeira execução ensinaram

| Item | Falha | Causa | Ação |
|---|---|---|---|
| V1 | erro de 0,5 % contra a scikit-rf | **bug real:** a norma Touchstone v1 grava os arquivos de **2 portas** como S11, S21, S12, S22 (coluna a coluna), e o leitor assumia linha a linha. No PI-1, S12 e S21 vinham trocados. $Z_{11}$ não foi afetado, porque depende de $S_{12}S_{21}$ | corrigido nos três leitores (src, script de redução, notebook) e no gerador de arquivos dos testes; teste novo |
| V5 | ρ(razão, h) negativo no PI-2 | critério mal especificado: o campo de borda previsto nas placas grandes do PI-2 e do PI-3 é menor que 2 %, abaixo da resolução, e o artefato do V13 domina | critério trocado pela comparação quantitativa com Palmer, que passou com folga |
| V7 | expoente 0,71 no PI-2 | a eq. 13-31 descreve só o espalhamento; o laço tem também um termo fixo $L_0$ (pads e porta), que puxa o expoente aparente para baixo | modelo $L = L_0 + k h$: expoente da parte variável = 1,00 |

## Como reexecutar

```bash
venv/bin/python scripts/validacao_teorica.py     # ~15 s com os caches; V1–V4 exigem os arquivos brutos
venv/bin/python -m pytest tests -q
```
