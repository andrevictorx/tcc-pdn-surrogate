# Análise metodológica da literatura

**Data:** 2026-08-11
**Propósito:** fixar as decisões metodológicas do TCC sobre precedentes verificados, e
delimitar o gap que o trabalho ocupa.

> **Regra deste arquivo:** só entra referência cujo PDF foi lido integralmente ou cuja
> existência foi confirmada em base indexada. Cada entrada declara seu status.

---

## 1. Status de verificação das referências

### 1.1 Lidas integralmente (PDF em `referencias/artigos/`)

| # | Referência | Veículo | Status |
|---|---|---|---|
| A | Hassab, Schierholz, Schuster, "Application of Gaussian Process Regression for Data Efficient Prediction of PCB-based PDN Impedance Features" | IEEE 28th Workshop on Signal and Power Integrity (SPI), 2024. DOI 10.1109/SPI60975.2024.10539189 | ✅ lido |
| B | Hillebrecht, Schierholz, Hassab, Alfert, Schuster, "Generation and Application of a Very Large Dataset for Signal Integrity Via Array and Link Analysis" | IEEE Trans. EMC, vol. 66, no. 6, pp. 1967–1976, Dez. 2024. DOI 10.1109/TEMC.2024.3450307 | ✅ lido |
| C | An et al. (KAIST), "Generative Model based Multi-layer PDN Impedance Estimation with Multi-power Domain" | IEEE 75th ECTC, 2025, pp. 927–932. DOI 10.1109/ECTC51687.2025.00162 | ✅ lido |
| D | Jiang, Li (BUPT), "Attention-Guided Reinforcement–Genetic Optimizer: Fast PDN Impedance Prediction and Decoupling Capacitor Design for Power Integrity" | IEEE Int. Workshop on Advanced Interconnects (WAI), 2025. DOI 10.1109/WAI67900.2025.11309316 | ✅ lido |

### 1.2 Lidas e **desaconselhadas** como fonte técnica

| # | Referência | Motivo |
|---|---|---|
| E | Kumar, "Artificial Intelligence Applications to Enhance Signal and Power Integrity in High-Speed Systems", SSRN 5438134, 2025 | **Preprint SSRN, não IEEE, sem revisão por pares.** Erros editoriais evidentes: Fig. 5 legendada como "Impedance matching in transmission lines" exibindo diagrama de olho; Figs. 7 e 8 com legenda idêntica e conteúdo distinto; figuras de terceiros com marca d'água. Nenhum experimento próprio, nenhuma tabela quantitativa. Não citar. |
| F | Kostova, Menxhiqi, Zylfiu, Marinova, "Review of AI Implementation in Electronic Design Automation Methods and Tools", UBT International Conference, 2023 | Conferência regional (Kosovo), não IEEE. Genérico sobre EDA; nenhum conteúdo sobre PDN ou impedância. Uso no máximo contextual na introdução. |

### 1.3 Confirmadas por busca, **PDF pendente**

| # | Referência | Veículo | Por que importa |
|---|---|---|---|
| G | "PDN impedance prediction using cross-stage densely connected network based on attention augmentation" (CSDNet) | IEEE Xplore, doc. 10775857, 2024 | Transfer learning reduz em **80%** os dados rotulados; +41,5% de acurácia sobre DenseNet; avalia empilhamentos de **6 camadas** — mesma classe do subconjunto do TCC. Competidor direto em eficiência de dados. |
| H | Schierholz et al., "Engineering-Informed Design Space Reduction for PCB-Based Power Delivery Networks" | IEEE Trans. CPMT, vol. 13, no. 10, Out. 2023. IEEE Xplore doc. 10173595 | **Redução physics-informed do espaço de projeto** (10^6 → 10^3 pontos de amostragem). É o precedente do próprio grupo TUHH para "usar física para gastar menos dado". |
| I | Garbuglia, Spina, Reuschel, Schuster, Deschrijver, Dhaene, "Modeling electrically long interconnects using physics-informed delayed Gaussian processes" | IEEE Trans. EMC, vol. 65, no. 6, pp. 1715–1723, Dez. 2023 | É a referência para a qual **B aponta** ao declarar que prever toda a banda é problema em aberto. Physics-informed em SI. |
| J | Schierholz et al., "SI/PI-Database of PCB-Based Interconnects for Machine Learning Applications" | IEEE Access, vol. 9, pp. 34423–34432, Fev. 2021 | **Artigo da própria base de dados do TCC.** Citação obrigatória. |
| K | "Development of a Physics-Informed Neural Network Model for Rapid Power Integrity Analysis in Die-Level and Die-Package Co-Design for 2.5-D Chiplet Solutions" | IEEE Xplore doc. 11261767 | PINN aplicado a integridade de potência. Precedente de restrição física dura em PI (embora em IR drop/transiente, não em Z(f)). |
| L | Zhang, Juang, Kiguradze, Pu, Jin, Wu, Yang, Hwang, "Fast PDN Impedance Prediction Using Deep Learning" | **arXiv:2106.10693** (2021); versão de periódico: "Fast impedance prediction for power distribution network using deep learning", *Int. J. Numer. Model.* (Wiley), vol. 35, no. 2, e2956, 2022 | Fundacional (DNN + BEM). **Atenção: não é IEEE** — a versão publicada é Wiley. O preprint arXiv é de acesso livre. |

### 1.4 ⚠️ **Não confirmada — provável título inexistente**

| Título alegado | Resultado da busca |
|---|---|
| "GNN-Based Early Power Integrity Estimation for PDN Design" | **Nenhum registro encontrado** com esse título, em nenhum veículo. A busca retorna trabalhos GNN adjacentes mas distintos (p.ex. *PDNNet: PDN-Aware GNN-CNN Heterogeneous Network for Dynamic IR Drop Prediction*, arXiv:2403.18569 — que trata de **IR drop**, não de Z(f)). **Não citar.** Se houver interesse em GNN, usar PDNNet e declarar que o alvo é outro. |

---

## 2. Comparação metodológica dos quatro artigos sólidos

### 2.1 Dados e alvo

| | A (TUHH/SPI'24) | B (TUHH/T-EMC'24) | C (KAIST/ECTC'25) | D (BUPT/WAI'25) |
|---|---|---|---|---|
| **Estrutura** | PCB 4 camadas | Arranjos de via SE/Diff + link | PDN on-chip multicamada, multi-domínio | PCB 4–12 camadas com decaps |
| **Amostragem** | LHS, 2000 | LHS, ~15000 | aleatória, 400 | Monte Carlo, 1,45 M |
| **Solver** | CIM + modelo PB de via | PB + guia radial | ANSYS HFSS (full-wave 3D) | BEM |
| **Banda** | 1 MHz–1 GHz | 250 MHz–100 GHz, 400 pts lineares | 0,1–30 GHz, 125 pts | — |
| **Alvo** | **6 escalares** derivados da curva | escalares (freq. de atenuação; transmissão em pontos fixos) | **curva** Z(f) completa, em dBΩ | **curva** de impedância |
| **Escala do alvo** | linear | linear | **dBΩ (log)** | dB |

### 2.2 Modelo, treino e avaliação

| | A | B | C | D |
|---|---|---|---|---|
| **Modelo** | GPR, kernel Matérn 5/2, média constante μ=0; **um modelo por alvo** | GPR (hiperp. por *slice sampling*, Bayesiano completo) + ANN feedforward | CNN 3D + multi-head attention | DenseNet (escolhido sobre SimpleCNN e ResNet) |
| **Split** | *active learning*, até 600 iterações | **treino / avaliação / teste** (3 vias); padronização ajustada no treino | **8:2** | — |
| **Loss** | — (GPR) | — | MSE em dBΩ, Adam, 100 épocas | — |
| **Métricas** | RMSE, **nRMSE = RMSE/média** | **R², RMSE, nRMSE** | **MAE em dBΩ** | RMSE |
| **Curva de aprendizado** | ✅ RMSE vs. amostras adicionadas (Figs. 6–7) | ✅ **R² vs. nº de amostras de treino, 0→200 (Fig. 8)** | ✗ | ✗ |
| **Ablação** | ✗ | ✗ | ✅ **de arquitetura** (CNN-only / Attention-only / ambos) | ✅ **de componentes** (Double → Dueling → PER), barras incrementais |
| **Validação física dos dados** | — | ✅ **passividade e reciprocidade** para descartar simulações defeituosas | usa reciprocidade para reduzir o alvo a N(N+1)/2 | — |

### 2.3 Resultados que importam para o TCC

**A — o achado mais útil de todos.** Prever escalares derivados da curva **falha para metade dos alvos**:

| Key-feature | RMSE | nRMSE |
|---|---|---|
| freq. do primeiro nulo `f_r` | 1,8 MHz | **2,04%** ✅ |
| sobressinal no nulo `ΔZ_r` | 0,003 Ω | **3,1%** ✅ |
| primeiro vão de frequência `Δf_s` | 1,58 MHz | **2,24%** ✅ |
| freq. do primeiro máx. local `f_m` | 66,66 MHz | **54,09%** ❌ |
| sobressinal no primeiro máx. `ΔZ_m` | 14,17 Ω | **>100%** ❌ |
| sobressinal máximo `ΔZ_o` | 60,28 Ω | **>100%** ❌ |

Transferência: dados iniciais de um subespaço **próximo** (Sub 4) superam os de um subespaço **distante** (Sub 8) nas primeiras iterações; 50–100 amostras iniciais dão ganho comparável. Conclusão dos autores: falta uma **métrica quantitativa de similaridade entre estruturas**.

**B — degradação com a frequência e a declaração do gap.**

| Caso | Features | Amostras | R² | nRMSE |
|---|---|---|---|---|
| Case 0, `f_-3dB` | 7 | 200 | 0,971 | 4,39% |
| Case 0, `f_-5dB` | 7 | 200 | 0,930 | 5,30% |
| Case 0, `f_-5dB` **com transfer learning** | 7+1 | 200 | **0,947** | **4,68%** |
| Case II, transmissão @ 4 GHz | 13 | 500 | 0,739 | 9,85% |
| Case II, @ 8 GHz | 13 | 500 | 0,747 | 17,23% |
| Case II, @ 16 GHz | 13 | 500 | 0,791 | 27,37% |
| Case II, @ 32 GHz | 13 | 500 | 0,769 | **50,25%** |

ANN: R² entre 0,70 e 0,87; *grid search* sobre >300 variações; treino < 1 min.

> Citação-chave (Seção V-B): *"the prediction of the EM behavior over the full frequency range is a difficult task. The open challenge requires more sophisticated adaptions of ML algorithms"* — seguida de remissão a **[I] Garbuglia (physics-informed delayed GP)**.

**C — a ablação de arquitetura.** MAE total: CNN-only 3,21 dBΩ · Attention-only 3,22 dBΩ · **CNN+Attention 2,93 dBΩ**. Auto-impedância (1,38 dBΩ) é **substancialmente mais fácil** que impedância de transferência (3,97 dBΩ). Inferência 2,35 µs (CPU) contra ~10^4 s do HFSS.

**D — a ablação de componentes.** Capacitores médios necessários: DQN base 14,5 → +Double 13,3 → +Dueling 10,8 → +PER 9,4 → **final 7,9**; taxa de sucesso ~85% → 100%. Surrogate: 1,2 ms/avaliação contra ~10 s do BEM (8,3×10³).

---

## 3. Decisões metodológicas do TCC, com âncora

| Decisão | Âncora | Observação |
|---|---|---|
| **Métricas: R², RMSE e nRMSE** | B (mesmo grupo, mesma base) | Reportar **por ponto de frequência** e agregado. nRMSE = RMSE/média das saídas de teste. |
| **Alvo em escala logarítmica** (`log10 |Z11|`) | C (dBΩ), D (dB) | Já previsto em `DATA_SPEC.md`. É a prática do campo, não uma escolha arbitrária. |
| **Split treino/validação/teste com semente fixa** | B (3 vias, padronização ajustada no treino) | C usa 8:2. Com 985 amostras, o split precisa ser **aninhado** para suportar a curva de aprendizado. |
| **Curva de aprendizado R² vs. nº de amostras** | **B, Fig. 8** e A, Figs. 6–7 | A figura central do TCC tem **forma já estabelecida** pelo grupo que gerou a base. Isso é vantagem retórica: o avaliador reconhece o formato. |
| **Ablação controlada, um termo por vez** | C (arquitetura), D (componentes, barras incrementais) | O TCC troca o *conteúdo* da ablação — termos físicos em vez de blocos de rede — mantendo o *formato* consagrado. |
| **Validar passividade e reciprocidade nos dados** | **B** (descarte de simulações defeituosas) | Confirma as invariantes I1–I3 de `DATA_SPEC.md`. ⚠️ I1 (reciprocidade) falhou em `simu_1000` com `atol=1e-6` — investigar se é tolerância apertada demais ou assimetria real. |
| **Baselines obrigatórios: GPR e ANN** | A e B | São os baselines do campo **para esta base**. Sem eles, não há comparação legítima. |
| **Prever a curva, não escalares** | **A** (3 de 6 escalares com nRMSE > 50%) | Deixa de ser preferência e passa a ser **decisão justificada por evidência publicada**. |

---

## 4. O gap que o TCC ocupa

Encadeando o que foi lido:

1. **B declara o problema em aberto**: prever a resposta EM em toda a banda de frequência é difícil e exige adaptações mais sofisticadas de ML — e aponta para métodos *physics-informed*.
2. **A quantifica o custo de contornar o problema**: reduzir a curva a escalares derivados faz metade dos alvos passar de 50% de nRMSE.
3. **C e D preveem a curva inteira**, mas com **10³–10⁶ amostras** e sem nenhuma restrição física na função de perda.
4. **H e I mostram que o grupo TUHH já usa física** — mas para **reduzir o espaço de projeto** (H) e para interconexões eletricamente longas (I), **não** como termo de perda sobre Z(f) de PDN.

**Portanto:** nenhum dos trabalhos verificados testa, por ablação controlada, se restrições físicas sobre a curva `Z11(f)` melhoram a generalização de um surrogate de PDN **em regime de poucas centenas de amostras**. Esse é o espaço do TCC — e ele é estreito e bem definido, o que é bom.

**Formulação defensável da contribuição:**

> Sobre 985 configurações do subconjunto de 6 camadas da SI/PI-Database, mede-se o efeito de
> restrições físicas verificadas (R1, R3, R4) na função de perda de um surrogate de `Z11(f)`,
> por ablação controlada e curva de aprendizado, contra baselines GPR e ANN estabelecidos
> na literatura da própria base.

Note que a contribuição é **uma medida**, não uma promessa de melhoria. Se a ablação mostrar
que as restrições **não** ajudam, o resultado continua publicável e o TCC continua válido —
desde que a medição seja limpa. Isso protege o cronograma.

---

## 5. PDFs a solicitar (ordem de prioridade)

1. **J** — SI/PI-Database, IEEE Access 9:34423–34432, 2021. *Citação obrigatória: é a base usada.*
2. **H** — Engineering-Informed Design Space Reduction, IEEE T-CPMT 13(10), 2023. *Precedente de "física economiza dado" no mesmo grupo.*
3. **G** — CSDNet, IEEE Xplore 10775857, 2024. *Competidor direto: 6 camadas, −80% de dado rotulado.*
4. **I** — Garbuglia, physics-informed delayed GP, IEEE T-EMC 65(6), 2023. *Ponte entre o gap declarado em B e a hipótese do TCC.*
5. **K** — PINN para integridade de potência 2.5-D, IEEE Xplore 11261767.

**L (Zhang et al.)** não precisa ser solicitado: o preprint está livre em `arxiv.org/abs/2106.10693`.

---

# PARTE II — Segunda rodada de leitura (2026-08-11)

## 6. Descoberta: a procedência do dataset

**O artigo H (Schierholz, Hassab, Schuster, IEEE T-CPMT 13(10), out. 2023, pp. 1613–1623,
DOI 10.1109/TCPMT.2023.3292577) é o artigo que *projetou* o subconjunto usado neste TCC.**

A coluna "Reduced" da Tabela I daquele artigo reproduz, valor a valor, os parâmetros fixos
do `parameter.csv`:

| Parâmetro | Tabela I (coluna "Reduced") | `parameter.csv` do TCC |
|---|---|---|
| `x_width` | 5800 mil | `XWIDTH` = 5800 ✓ |
| `y_width` | 4000 mil | `YWIDTH` = 4000 ✓ |
| `σ_CU` | 5,8·10⁷ S/m | `CONDUCTIVITY` = 5.8e7 ✓ |
| `tan δ` | 0,01 | `LOSSTANGENT` = 0.01 ✓ |
| `t_met` | 1 mil | `TMET` = 1.0 ✓ |
| (X_AI, Y_AI) | (2900 mil, 2000 mil) | `A1_XCENTER`=2900, `A1_YCENTER`=2000 ✓ |
| (X_AII, Y_AII) | (3900 mil, 3000 mil) | `A2_XCENTER`=3900, `A2_YCENTER`=3000 ✓ |
| Nr. Ports | 36 | 36 portas nos `.s36p` ✓ |
| Stackup | 2×GND, 2×PWR, 2×GND | **6 camadas** ✓ |
| ε_r | 2,5 – 4,5 | 2,50 – 4,50 ✓ |
| t_diel | 3 – 80 mil | `TDIEL` 3,12 – 78,99 ✓ |
| Nr. de amostras | ~1×10³ | **985** ✓ |

As faixas de `r_via`, `r_antipad` e `via pitch` no CSV são mais estreitas que as da tabela
(10–20 vs. 3–20; 20–39 vs. 13–40; 80–120 vs. 30–120), indicando reamostragem posterior. Os
**parâmetros fixos**, porém, são impressão digital: coincidem todos.

### Consequências

1. **A justificativa de por que 8 parâmetros variam e 9 são constantes está publicada.** É a
   análise de sensibilidade da Fig. 11 de H, com limiar explícito: *"parameter variations
   resulting in maximal RMSE values lower than 0.02 Ω are fixed at the basic values."*

2. **A justificativa das 6 camadas está publicada** (Seção IV-A de H): planos de terra
   intermediários são curto-circuitados pelas vias de terra e não afetam a impedância na
   banda de interesse; *"the reduced stackup of six layers [2×GND, 2×PWR, 2×GND] can be used
   as a default."*

3. **Existe um ranking de sensibilidade publicado contra o qual validar o pipeline:**

| Parâmetro | RMSE máx. (Fig. 11 de H) | Destino |
|---|---|---|
| `t_diel` (altura da cavidade) | **20,502 Ω** | mantido — **dominante, 14× o segundo** |
| ε_r (permissividade) | 1,443 Ω | mantido |
| `r_via` (raio da via) | 1,325 Ω | mantido |
| `r_antipad` | 0,988 Ω | mantido |
| via pitch | 0,600 Ω | mantido |
| σ_CU (condutividade) | 0,018 Ω | **fixado** |
| tan δ | 0,006 Ω | **fixado** |
| `t_met` | 0,002 Ω | **fixado** |

⚠️ **Tensão a resolver.** A exploração preliminar (`notebooks/02_feature_impact.py`, n=10)
mediu correlação `TDIEL ↔ Z_max` de **−0,007** e `ε_r ↔ Z_max` de −0,702. A física
quase-estática prevê `|Z| ≈ h/(ω ε₀ ε_r a b)`, isto é, `Z_max ∝ TDIEL/ε_r` — a correlação com
TDIEL deveria ser **fortemente positiva**. Com n=10 o erro-padrão de uma correlação é ~0,38,
então o achado é compatível com ruído amostral. **Resolver isso sobre as 985 configurações é
a primeira tarefa.**

---

## 7. Garbuglia et al. (artigo I) — a referência que declara o trabalho do TCC como futuro

Garbuglia, Reuschel, Schuster, Deschrijver, Dhaene, Spina, IEEE T-EMC 65(6), dez. 2023,
pp. 1715–1723, DOI 10.1109/TEMC.2023.3317917.

**Método.** GP com *kernel* physics-informed (τGP): `k_del = k_mean + k_envelope · Π k_τ,m`,
onde `k_τ,m` são *kernels* periódicos cujas frequências fundamentais são os **atrasos de
propagação**, estimados a priori pela transformada de Gabor. Hiperparâmetros por MMLE.

**Estrutura a imitar.** As restrições entram como **quatro Suposições numeradas e
explicitadas** (Assumptions 1–4), cada uma justificando um termo do *kernel*. É exatamente a
forma da `PHYSICS_SPEC.md` (R1–R5) — o que confirma que aquele documento está no formato
certo para virar seção de dissertação.

**Resultados.** Erro médio de modelagem: τGP **−50,5 dB** · DVF −42,8 dB · GP padrão −15,0 dB
· VF −14,1 dB. Com **306 amostras** (Aplicação I) e 500 (Aplicação II) — regime de poucos
dados. Treino: ~10 s.

**Tabela I do artigo** compara técnicas por capacidade. Note que GP e τGP recebem **"no"** em
*"Causality/Passivity enforcement"* — ou seja, **o τGP não impõe passividade**.

**Conclusão do artigo (citar literalmente na justificativa do TCC):**

> *"it constitutes an initial step towards a deeper integration of physical information in
> Bayesian models like Gaussian processes. Further efforts are needed to extend the new
> technique to the modeling of S-parameter values **over additional design variables** and
> **to enforce physical properties, such as causality and passivity, on the predictions of
> the model**."*

Os dois trabalhos futuros declarados são: (i) modelar sobre variáveis de projeto adicionais —
o TCC tem 8; (ii) impor propriedades físicas às predições — o TCC tem o termo R4 de
passividade. **A cadeia fecha:** B aponta para I; I declara como futuro exatamente o que o
TCC faz.

**Arte prévia a conhecer:** ref. [8] de I — Torun, Durgun, Aygün, Swaminathan, *"Causal and
passive parameterization of S-parameters using neural networks"*, IEEE T-MTT 68(10), out.
2020, pp. 4290–4304. É o precedente de imposição de causalidade e passividade em rede neural
para parâmetros S. **Solicitar PDF.**

---

## 8. Chen, Ju, Gu (artigo K) — a forma da função de perda e o teste de extrapolação

Chen, Ju, Gu (Northwestern Univ.), IEEE/ACM ISLPED 2025, DOI 10.1109/ISLPED65674.2025.11261767.

**Forma da perda (Eq. 3):** `L_PINN = ω_RES·L_RES + ω_BC·L_BC + ω_IC·L_IC + ω_DATA·L_DATA`.
É a estrutura da perda do TCC. Os pesos **não são fixos**: *"adaptively adjusted based on
historical ratios of individual losses in multi-objective training"*, citando Bischof &
Kraus, *"Multi-Objective Loss Balancing for Physics-Informed Deep Learning"*,
arXiv:2110.09813 — **resolve o problema de como ponderar os termos sem ajuste manual.**

**Duas ideias diretamente aproveitáveis:**

1. **Medir os resíduos físicos também no baseline.** A Fig. 11(b) plota as perdas de PDE, BC
   e IC ao longo do treino para PINN *e* para a NN convencional. A NN convencional reduz os
   resíduos físicos lentamente e de forma indireta. Isso dá um **segundo eixo de resultados**:
   quanto o baseline viola R1/R3/R4 sem ser instruído a respeitá-los.

2. **Restrição física ajuda a extrapolar, não só a interpolar.** Fig. 12(b): treinado apenas
   com o primeiro *droop* (t ≤ 50 ns), o PINN mantém ajuste quase perfeito além da janela
   enquanto a NN convencional desvia. *"superior accuracy in corner cases, such as scenarios
   beyond the training data range."* → **Experimento barato e forte para o TCC:** treinar num
   subintervalo de `TDIEL` e testar nos extremos retidos.

**Distinção útil:** restrição *dura* (imposta pela arquitetura — no artigo, `I^z ≡ 0` onde não
há interconexão vertical) vs. *macia* (penalidade na perda). R4 (passividade) admite as duas
formas; vale declarar qual foi escolhida e por quê.

**Resultado:** economiza até **80%** dos dados de treino; 299× mais rápido que o solver.

---

## 9. Ou, Xiang, Li, Chen (artigo G, CSDNet) — o formato de tabela a replicar

Ou, Xiang, Li, Chen (BUPT), 2024 6th International Conference on Energy, Power and Grid
(ICEPG), pp. 1828–1832, DOI 10.1109/ICEPG63230.2024.10775857.

⚠️ **Veículo de baixo impacto** para o tema (conferência de energia/redes elétricas, não de
EMC/SI-PI). Usar pela metodologia, não como autoridade.

**Split 7:2:1** (treino/validação/teste), *batch* 128, 1000 iterações. Perda: RMSE.
Métricas: MAE (mΩ) e MRE (%).

**Prática metodológica a adotar:** *"Each prediction model is trained 10 times and averaged
performance in the test set separately to reduce the chance of prediction results."*

**Ablação (Tabela 4)** — cada componente contribui para coisa diferente:

| Modelo | MAE PCB1 | Tempo de treino |
|---|---|---|
| DenseNet | 4,2 mΩ | 2849 s |
| CBAM-DenseNet (atenção) | **2,4 mΩ** | 3486 s |
| CSP-DenseNet | 4,1 mΩ | **2110 s** |
| CSDNet (ambos) | **2,4 mΩ** | 2502 s |

A atenção compra acurácia; o CSP compra velocidade. **Ablação limpa não precisa mostrar que
todo componente melhora a métrica principal** — pode mostrar que cada um resolve um eixo
distinto. Isso é liberdade útil para o TCC.

**Tabela 5 — a curva de aprendizado em forma de tabela (o formato a replicar):**

| Treino | MAE PCB1 | MRE PCB1 |
|---|---|---|
| direto, 500 amostras | 18,3 mΩ | 24,61% |
| direto, 1000 | 13,2 | 15,96% |
| direto, 1500 | 9,8 | 11,74% |
| direto, 2000 | 7,9 | 8,25% |
| direto, 2500 | 6,0 | 6,13% |
| **transferência, 500** | **6,4** | **6,93%** |

500 amostras com transferência ≈ 2500 sem. **Economia de 80% de dado.** A tabela do TCC terá
esta forma exata, trocando "transferência" por "restrições físicas ativas".

📌 **Referência de calibragem:** com 500 amostras e treino direto, o MRE é de ~25%. O TCC tem
**985** amostras — está exatamente no regime onde a intervenção importa.

---

## 10. Convergência: o número 80%

Três trabalhos independentes chegam à mesma cifra de economia de dados:

| Trabalho | Mecanismo | Economia |
|---|---|---|
| G (CSDNet) | transfer learning | **80%** |
| K (PINN) | restrições físicas na perda | **80%** |
| H (Eng.-Informed) | redução do espaço de projeto | 10³× em amostragem |

**80% é o número de referência do campo.** É a marca contra a qual o resultado do TCC será
lido — mesmo que informalmente, pela banca.

---

## 11. Metodologia consolidada (atualização da Seção 3)

Acrescentar às decisões já fixadas:

| Decisão | Âncora | Detalhe |
|---|---|---|
| **Repetir cada treino com N sementes e reportar média ± desvio** | H (11 treinos, RMSE 15,6 ± 0,801 MHz), G (10 treinos) | Sem isso, os deltas da ablação não são interpretáveis. **Não negociável.** |
| **Pesos dos termos físicos balanceados adaptativamente** | K (Eq. 3) + Bischof & Kraus arXiv:2110.09813 | Evita que o TCC vire um exercício de ajuste manual de λ. |
| **Medir resíduos físicos também no baseline** | K, Fig. 11(b) | Segundo eixo de resultados, custo quase zero. |
| **Testar extrapolação, não só interpolação** | K, Fig. 12(b) | Treinar num subintervalo de TDIEL, testar nos extremos. |
| **Validar o ranking de sensibilidade contra a Fig. 11 de H** | H | Valida o pipeline contra resultado publicado sobre os mesmos dados. |
| **Declarar restrição dura vs. macia** | K | R4 admite as duas formas. |

## 12. PDF ainda a solicitar

- Torun, Durgun, Aygün, Swaminathan, *"Causal and passive parameterization of S-parameters
  using neural networks"*, IEEE Trans. MTT, vol. 68, no. 10, pp. 4290–4304, out. 2020.
  *Arte prévia direta sobre imposição de passividade/causalidade em rede neural para
  parâmetros S — o TCC precisa se posicionar em relação a ela.*
