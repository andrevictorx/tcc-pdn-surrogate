# Research Brief: PDN Optimization com Machine Learning

**Documento:** Briefing da pesquisa
**Data:** 2026-07-09 · **Revisado:** 2026-08-01
**Status:** SUPERSEDED em parte — ver aviso abaixo

---

> ## ⚠️ Aviso de desatualização
>
> Este documento foi escrito **antes** da inspeção dos arquivos. Vários fatos
> aqui afirmados foram refutados por verificação direta em 2026-08-01.
> **Fonte de verdade atual:**
>
> - dados → [`spec/DATA_SPEC.md`](DATA_SPEC.md)
> - física → [`spec/PHYSICS_SPEC.md`](PHYSICS_SPEC.md)
> - proposta completa → `proposta/main.tex`
>
> Correções principais:
>
> | Afirmado aqui | Verificado |
> |---|---|
> | 13 features de entrada | **8** (9 dos 17 parâmetros são constantes) |
> | 986 configurações | **985** |
> | alvo = escalar `|Z_max|` | alvo = **curva** `Z11(f)`, 334 pontos |
> | R² > 0,85 como meta | **R² > 0,90**, com curva de aprendizado e ablação |
> | dataset "6,7 GB comprimido" | **24 GB** descompactados, 24 MB por arquivo |
> | — | frequência é **linear** (3 MHz), não logarítmica |
> | âncora modal utilizável | **refutada** para `Z11` nesta banda |
>
> Mantido como registro histórico do raciocínio inicial.

---

## ❓ Problema

**Contexto:** Design de PCBs para eletrônicos de alta velocidade (PCI Gen 6, 32 GHz+) é crítico em EMI/EMC. A integridade de potência (PDN) é o **principal limitante** — falha em PDN causa 90% dos problemas de compatibilidade eletromagnética.

**Desafio:** Projetistas tipicamente usam **tentativa-e-erro** ou simulações EM caras (ANSYS, HFSS) que levam 15–30 min por configuração. Não há ferramenta rápida que diga:
> "Dado meu stackup (nº de camadas, altura de cavidade, pitch de via), qual Z(f) vou ter?"

**Oportunidade:** A SI/PI-Database (TUHH) tem 986 configurações de PDN 6-camadas já simuladas com precisão. Isso é suficiente para treinar um **surrogate model** (preditor rápido) de ML.

---

## 💡 Solução Proposta

**Abordagem:** Spec-Driven, Multi-Fase

1. **Fase 1: Surrogate Model**  
   Treinar rede neural (ANN) ou Gaussian Process (GPR) que, em < 1 ms, prediz impedância Z(f) de uma PDN a partir de parâmetros de projeto.
   - **Entrada:** ε_r, tan δ, σ, cavity_height, via_pitch, via_radius, nº camadas, etc. (13 features)
   - **Saída:** |Z_max| entre 1 MHz – 1 GHz (ou curva inteira)
   - **Alvo:** R² > 0.85 em test set

2. **Fase 2: Otimizador**  
   Usar o surrogate dentro de um algoritmo de otimização (GA ou Bayesian Optimization) para encontrar a configuração que **minimize |Z_max|** sujeito a restrições (e.g., cavity_height ≤ 80 mil).

3. **Fase 3: Análise**  
   Extrair **feature importance** (SHAP) para responder: "Qual parâmetro mais impacta Z?" → gerar guia prático de design.

---

## 📊 Dados

**Dataset:** SI/PI-Database v1.0 (TUHH)  
**Subconjunto:** 6-Layer PDN com Two Via Arrays, Latin Hypercube Sampling (LHS)
- **Configurações:** 986 designs
- **Features:** 13 (ε_r, σ, tan δ, stackup, via geometry, geometry)
- **Alvo:** S-parâmetros (Touchstone) → derivar Z(f)
- **Tamanho:** 6.7 GB (comprimido)
- **Licença:** CC-BY 4.0 (TUHH, cite papers)

**Base teórica:** 
- Hillebrecht et al. 2024 (IEEE TEMC) — Dataset, análise de features
- Schierholz et al. 2023 (DesignCon) — Data-efficient ML para PDN
- Schierholz et al. 2021 (IEEE Access) — SI/PI-Database original

---

## 🎯 Objetivos

| # | Objetivo | Métrica | Target |
|---|----------|---------|--------|
| O1 | Surrogate model acurado | R² (test) | > 0.85 |
| O2 | Predição rápida | Latência | < 1 ms por predição |
| O3 | Otimizador funcional | Convergência | GA find optimum em < 100 gerações |
| O4 | Insights de design | Feature importance | Top 5 features identificados |
| O5 | Publicável | Paper IEEE | SPI/DesignCon 2027 |

---

## 🔍 Metodologia (Alto Nível)

1. **EDA (Exploratory Data Analysis)**
   - Carregar dados de 3 datasets (PDN + SI arrays)
   - Visualizar distribuição de features, correlações
   - Identificar outliers, missing values
   - Output: Notebooks 01–02

2. **Feature Engineering**
   - Normalizar features (escalas diferentes: μm vs. GHz)
   - Possíveis transformações: log(σ), polynomial terms
   - Select top features (reduzir dimensionalidade)
   - Output: `src/features/engineering.py`

3. **Baseline Model**
   - Treinar modelo simples (Linear Regression, Random Forest)
   - Usar train/test 80/20
   - Registrar baseline R², RMSE
   - Output: Notebook 02

4. **Surrogate Model (Principal)**
   - Treinar ANN (2–3 hidden layers) + GPR em paralelo
   - Avaliar com cross-validation (5-fold)
   - Hiperparameter tuning (batch size, learning rate, kernel)
   - Output: `src/models/surrogate.py`, modelo `.pkl`

5. **Otimização**
   - Implementar GA (deap library) ou Bayesian Opt (optuna)
   - Usar surrogate como fitness function
   - Rodar otimizador por N gerações/iterações
   - Comparar com layouts padrão (estado-da-arte)
   - Output: `src/models/optimizer.py`, resultados em `experiments/`

6. **Análise de Sensibilidade**
   - Treinar modelo interpretável (Decision Tree/Linear Model)
   - Calcular SHAP values para feature importance
   - Gerar recomendações de design
   - Output: Gráficos, guia prático

7. **Documentação & Paper**
   - Escrever metodologia, resultados, conclusões
   - Comparar com work relacionado
   - Submeter para IEEE SPI 2027
   - Output: `.pdf` + `docs/PAPER.md`

---

## 🚀 Entregáveis Esperados

| Fase | Entregável | Formato | Critério de Aceitação |
|------|-----------|---------|----------------------|
| 1–2 | EDA Report | Notebooks + Plots | Distribuições claras, outliers documentados |
| 3–4 | Baseline Model | `.pkl` + Métricas | R² ≥ 0.70 |
| 5–6 | Surrogate Model | `.pkl` + Docs | R² ≥ 0.85, < 1 ms latência |
| 7–8 | Otimizador | `.py` + Config | Converge, melhora baseline 10%+ |
| 9 | Feature Importance | Gráficos + Guia | Top 5 features documentados |
| 10 | Documentação | `.md` + `.py` docstrings | 100% functions documented |
| 11 | Paper/Relatório | `.pdf` + `.tex` | Submetível a IEEE SPI |

---

## ⏱️ Timeline (Estimado)

- **Semanas 1–2:** Setup, exploração, specs finais
- **Semanas 3–5:** EDA, feature engineering
- **Semanas 6–8:** Baseline + Surrogate model
- **Semanas 9–11:** Otimização, validação
- **Semanas 12–14:** Análise, documentação
- **Semanas 15–16:** Polish, paper, defesa

**Total:** ~4 meses (half-time), pode compactar para 3 meses full-time.

---

## 🎓 Contribuição Científica

1. **Primeira aplicação de surrogate ML em PDN design** (na UFPR, que temos contato)
2. **Validação de dataset TUHH** em contexto UFPR/brasileiro
3. **Ferramenta prática** (open-source) que pode ser usada por designers
4. **Metodologia** transferível a outros tipos de otimização de PCB

---

## 🔗 Referências Chave

1. Hillebrecht et al., "Generation and Application of a Very Large Dataset...", IEEE TEMC, 2024
2. Schierholz et al., "SI/PI-Database of PCB-Based Interconnects...", IEEE Access, 2021
3. Schierholz et al., "Data-efficient supervised ML technique for PCB noise decoupling", DesignCon, 2023
4. Kostova et al., "Review of AI Implementation in Electronic Design Automation", UBT Int. Conf., 2023

---

## ✅ Validação

- [ ] Orientador (Prof. Leandro) validou problema?
- [ ] Dataset acessível? (✓ sim, baixado)
- [ ] Metodologia viável em 1 semestre? (✓ sim, baseada em papers existentes)
- [ ] Recursos computacionais OK? (✓ sim, sklearn/torch em laptop)
- [ ] Próximo passo? → Refinar SCOPE.md, validar com Prof.

---

**Status:** Pronto para discussão com Prof. Leandro  
**Próximo:** Agendar reunião, revisar specs finais
