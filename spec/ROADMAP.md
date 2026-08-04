# Roadmap: PDN ML Optimization (2026/2 – 2027/1)

**Timeline:** 16 semanas (agosto – novembro 2026)  
**Milestone Reviews:** Bi-weekly com Prof. Leandro  

---

## Fase 1: Setup & Planning (Semanas 1–2)

**Goal:** Infraestrutura pronta, specs validadas

| Semana | Task | Owner | Deliverable | Status |
|--------|------|-------|-------------|--------|
| 1 | Environment setup | André | `environment.yml` + deps installed | ⏳ |
| 1 | Validar datasets | André | Verificar 986 configs, schemas OK | ⏳ |
| 2 | Meeting Prof. Leandro | André + Prof | Feedback specs, ajustes | ⏳ |
| 2 | Design architecture | André + Claude | `design/architecture.md` finalizado | ⏳ |

**Gate:** Specs aprovadas, ambiente testado

---

## Fase 2: Exploração & Baseline (Semanas 3–5)

**Goal:** Entender dados, modelo baseline

| Semana | Task | Owner | Deliverable | Status |
|--------|------|-------|-------------|--------|
| 3 | EDA completo | André | `notebooks/01_data_exploration.ipynb` | ⏳ |
| 3 | Feature analysis | André | Correlação, distribuição, outliers | ⏳ |
| 4 | Feature engineering | André | `src/features/engineering.py` | ⏳ |
| 4 | Baseline model | André | Linear Reg + Random Forest, R² ≈ 0.70 | ⏳ |
| 5 | Baseline notebook | André | `notebooks/02_baseline_model.ipynb` | ⏳ |
| 5 | Mid-point review | André + Prof | Feedback, ajustes | ⏳ |

**Gate:** Baseline R² ≥ 0.65, entendimento dados solidário

---

## Fase 3: Surrogate Model (Semanas 6–8)

**Goal:** ANN/GPR treinado, R² > 0.85

| Semana | Task | Owner | Deliverable | Status |
|--------|------|-------|-------------|--------|
| 6 | Design model | André + Claude | `design/model_design.md` | ⏳ |
| 6 | Implementar ANN | André | `src/models/surrogate.py` | ⏳ |
| 7 | Hiperparameter tuning | André | Grid search, CV folds | ⏳ |
| 7 | Train final | André | Modelo `.pkl`, metrics | ⏳ |
| 8 | Validação | André | Test set R², RMSE, plots | ⏳ |
| 8 | Notebook resultados | André | `notebooks/03_surrogate_training.ipynb` | ⏳ |

**Gate:** R² ≥ 0.85 em holdout, < 1 ms latência

---

## Fase 4: Otimização (Semanas 9–11)

**Goal:** Otimizador GA/Bayesian funcional

| Semana | Task | Owner | Deliverable | Status |
|--------|------|-------|-------------|--------|
| 9 | Design optimizer | André + Claude | `design/optimizer_spec.md` | ⏳ |
| 9 | Implementar GA | André | `src/models/optimizer.py` | ⏳ |
| 10 | Tuning GA | André | Population size, generations, convergence | ⏳ |
| 10 | Rodar experimentos | André | `experiments/exp_001_ga/` | ⏳ |
| 11 | Análise resultados | André | Comparar com baseline, ganhos % | ⏳ |
| 11 | Visualização | André | Plots de convergência, Pareto (se aplicável) | ⏳ |

**Gate:** Otimizador converge, melhora baseline 10%+

---

## Fase 5: Análise & Insights (Semanas 12–13)

**Goal:** Feature importance, guia prático

| Semana | Task | Owner | Deliverable | Status |
|--------|------|-------|-------------|--------|
| 12 | SHAP analysis | André | Feature importance ranking | ⏳ |
| 12 | Design guidelines | André | Recomendações (e.g., "pitch é crítico") | ⏳ |
| 13 | Notebook análise | André | `notebooks/04_sensitivity_analysis.ipynb` | ⏳ |
| 13 | Comparison SOTA | André | vs. simuladores, vs. papers | ⏳ |

**Gate:** Top-5 features documentadas, insights validados

---

## Fase 6: Testing & QA (Semanas 13–14)

**Goal:** 100% coverage, código pronto

| Semana | Task | Owner | Deliverable | Status |
|--------|------|-------|-------------|--------|
| 13 | Unit tests | André | `tests/test_*.py`, 90%+ coverage | ⏳ |
| 14 | Integration tests | André | End-to-end pipeline | ⏳ |
| 14 | Code review | Claude | `/code-review`, style checks | ⏳ |
| 14 | Reproducibility | André | Scripts, configs, seeds | ⏳ |

**Gate:** Tests pass, coverage ≥ 90%, código rodável

---

## Fase 7: Documentation (Semanas 14–15)

**Goal:** Docs completos, relatório

| Semana | Task | Owner | Deliverable | Status |
|--------|------|-------|-------------|--------|
| 14 | API docs | André | `docs/API.md` (função signatures + examples) | ⏳ |
| 15 | Install guide | André | `docs/INSTALLATION.md` | ⏳ |
| 15 | Usage guide | André | `docs/USAGE.md` (exemplos end-to-end) | ⏳ |
| 15 | Relatório | André | `docs/REPORT.md` (metodologia, resultados) | ⏳ |
| 15 | PDF | André | Exportar REPORT.md para `.pdf` | ⏳ |

**Gate:** Alguém externo consegue rodar tudo com README

---

## Fase 8: Polish & Defesa (Semanas 15–16)

**Goal:** Apresentação pronta, repository limpo

| Semana | Task | Owner | Deliverable | Status |
|--------|------|-------|-------------|--------|
| 15 | Presentation | André | Slides (formato: `.pptx` ou `.md` reveal) | ⏳ |
| 16 | Final review | André + Prof | Feedback final | ⏳ |
| 16 | Défesa | André + Prof | Apresentação + discussão | ⏳ |
| 16 | GitHub/archival | André | Código + docs archived, link no relatório | ⏳ |

**Gate:** Defesa aprovada

---

## 🎯 Milestones Críticos (Kill Points)

| Milestone | Target Date | Exit Criteria | Impact |
|-----------|-------------|---------------|--------|
| **M1: Data ready** | Semana 2 | 986 configs, 13 features, zero errors | CRÍTICO |
| **M2: Baseline OK** | Semana 5 | R² ≥ 0.65 | CRÍTICO |
| **M3: Model converge** | Semana 8 | R² ≥ 0.85, < 1 ms latency | CRÍTICO |
| **M4: Optimizer works** | Semana 11 | GA converge, melhora 10%+ | CRÍTICO |
| **M5: Tests 90%** | Semana 14 | Coverage ≥ 90%, all pass | IMPORTANTE |
| **M6: Docs complete** | Semana 15 | README, API, usage, paper | IMPORTANTE |

---

## ⚠️ Riscos & Mitigação

| Risk | Probabilidade | Impacto | Mitigação |
|------|---------------|--------|-----------|
| Dataset corrupt/incomplete | Baixa | CRÍTICO | ✓ Validação Sem1, backup |
| Model overfits (R² baixo test) | Média | CRÍTICO | CV strict, regularização, dropout |
| GA não converge | Média | IMPORTANTE | Tune population, selection, mutation |
| Laptop insuficiente | Baixa | IMPORTANTE | Usar Google Colab (free GPU) |
| Papers não encontrados | Muito baixa | MENOR | Já temos 4 papers principais |
| Prof. Leandro indisponível | Baixa | IMPORTANTE | Buffer 2 semanas antes defesa |

**Plano B:** Se R² < 0.80, mudar estratégia:
- Usar ensemble (ANN + GPR + RF)
- Prever no log-space ou com transformação
- Reduzir features via PCA
- Focar em SHAP insights (menos model-dependent)

---

## 📅 Calendar View (Trimestre)

```
AGOSTO 2026
S  T  W  T  F  S  S
               1  2  3
4  5  6  7  8  9  10     ← Sem 1: Setup
11 12 13 14 15 16 17    ← Sem 2: Design
18 19 20 21 22 23 24    ← Sem 3: EDA
25 26 27 28 29 30 31    ← Sem 3–4

SETEMBRO 2026
1  2  3  4  5  6  7
8  9  10 11 12 13 14    ← Sem 4–5: Baseline
15 16 17 18 19 20 21    ← Sem 5–6
22 23 24 25 26 27 28    ← Sem 6–7: Model
29 30

OUTUBRO 2026
...                      ← Sem 7–8: Model final
                         ← Sem 9–11: Optimizer
NOVEMBRO 2026
...                      ← Sem 12–14: Analysis + QA
...                      ← Sem 15–16: Docs + Defesa
```

---

## 📊 Weekly Sync Template

**Agenda (todo Thursday 30 min):**
1. Completed last week?
2. Blocked on what?
3. Plans next week?
4. Risks emerged?

**Log:** `docs/weekly_meetings.md`

---

## 🔄 Iterative Checkpoints

- **Semana 2:** Specs validadas?
- **Semana 5:** Baseline OK?
- **Semana 8:** Surrogate pronto?
- **Semana 11:** Otimizador funciona?
- **Semana 14:** Tests + Docs OK?
- **Semana 16:** Defesa!

**Rollback:** Se milestone falha, discutir com Prof., possível ajuste de escopo.

---

**Owner:** André + Prof. Leandro  
**Last Updated:** 2026-07-09  
**Next Review:** 2026-08-01
