# Scope: PDN ML Optimization Project

**Versão:** 1.0
**Data:** 2026-07-09 · **Revisado:** 2026-08-01
**Responsável:** André Pires

---

> ## ⚠️ Aviso de desatualização
>
> Escrito antes da inspeção dos dados. Divergências relevantes em relação ao
> escopo atual, definido em `proposta/main.tex`:
>
> - **features:** são 8, não 13
> - **alvo:** curva `Z11(f)` completa (334 pontos), não o escalar `|Z_max|` — o
>   escalar passa a ser métrica secundária derivada
> - **meta de acurácia:** R² > 0,90, não 0,85
> - **contribuição central:** deslocada de "treinar um surrogate" para "testar
>   se restrições físicas melhoram a generalização em regime de poucos dados",
>   o que exige **ablação controlada** e **curva de aprendizado** — itens
>   ausentes deste documento
> - **cobertura de testes:** "100% de `src/`" substituído por critério de
>   propriedade (forma/tipo, invariante física, caso analítico), mais adequado a
>   código tensorial que percentual de linhas
>
> Ver `spec/DATA_SPEC.md` e `spec/PHYSICS_SPEC.md`.

---

## ✅ In Scope (O que FAZEMOS)

### Core
1. **Dados:** Carregar + processar dataset 6-Layer PDN (986 configs)
2. **Model:** Treinar ANN/GPR para prever |Z_max| (impedância PDN)
   - Features: 13 parâmetros de projeto (ε_r, cavity_height, pitch, etc.)
   - Alvo: |Z| máximo entre 1 MHz–1 GHz
   - Métrica: R² > 0.85, RMSE < 5 mΩ
3. **Optimizer:** GA (Genetic Algorithm) ou Bayesian para minimizar Z
4. **Analysis:** Feature importance (SHAP) + guia prático de design
5. **Testing:** Unit tests (pytest) + integration tests

### Documentação
6. **Specs:** research_brief, scope, roadmap (este doc)
7. **Design:** architecture, data_pipeline, model_design
8. **Code Docs:** Docstrings, README, comments
9. **Experiments:** MLflow/Hydra config + results tracking
10. **Report:** Relatório final (.md + .pdf) + possível paper IEEE SPI

---

## ❌ Out of Scope (O que NÃO fazemos)

- [ ] Usar dataset SE-SI ou Diff-SI (apenas PDN por agora)
- [ ] Prever curva inteira Z(f) (apenas |Z_max| escalar)
- [ ] Deep RL (Reinforcement Learning) — fica para mestrado
- [ ] Integração com EDA tools (KiCad plugin) — future work
- [ ] Validação experimental (teste em lab) — fora do escopo TCC
- [ ] Otimização multi-objetivo (Pareto) — pode ser extensão
- [ ] Dados reais do scanner 3D — nice-to-have, não core
- [ ] Comparação com simuladores comerciais (Ansys, CST)
- [ ] Training em GPU/distributed — laptop é suficiente
- [ ] API REST/web service — versão 2.0

---

## 📋 Requisitos Funcionais

| ID | Requisito | Descrição | Prioridade |
|----|-----------|-----------|-----------|
| RF1 | Load Data | Carregar 986 configs + validar schemas | MUST |
| RF2 | Preprocess | Normalizar features, handle missing data | MUST |
| RF3 | Train Model | Treinar ANN/GPR com CV | MUST |
| RF4 | Predict | Prever Z_max em < 1 ms | MUST |
| RF5 | Optimize | GA/Bayesian encontrar config ótima | MUST |
| RF6 | Analyze | Feature importance via SHAP | SHOULD |
| RF7 | Visualize | Gráficos de Z(f), evolução GA, etc. | SHOULD |
| RF8 | Report | Docstring + markdown report | MUST |
| RF9 | Test | 100% coverage de lógica | SHOULD |
| RF10 | Track Exp | MLflow/Hydra para rastrear runs | NICE |

---

## 📋 Requisitos Não-Funcionais

| ID | Requisito | Descrição | Target |
|----|-----------|-----------|--------|
| RNF1 | Performance | Treino < 5 min (CPU laptop) | < 5 min |
| RNF2 | Accuracy | R² > 0.85 em holdout | > 0.85 |
| RNF3 | Latency | Predição per sample < 1 ms | < 1 ms |
| RNF4 | Code Quality | Pylint score > 8.0 | > 8.0 |
| RNF5 | Docs | Todas functions têm docstrings | 100% |
| RNF6 | Reproducibility | Seeds fixos, resultados repeatáveis | Sempre |
| RNF7 | Maintainability | Code style PEP8, type hints | Sempre |

---

## 🗂️ Artifacts (Saídas)

| Artifact | Formato | Local | Descrição |
|----------|---------|-------|-----------|
| Dados Processados | `.pkl` / `.parquet` | `data/processed/` | Datasets limpos + preprocessados |
| Modelo Treinado | `.pkl` (joblib) | `experiments/exp_001/` | ANN/GPR serializado |
| Otimizador | `.py` | `src/models/optimizer.py` | Código de GA/Bayesian |
| Resultados | `.yaml` + `.json` | `experiments/exp_001/results/` | Métricas, config, loss curves |
| Notebooks | `.ipynb` | `notebooks/` | 01–04 (EDA, baseline, model, results) |
| Tests | `.py` | `tests/` | Unit + integration |
| Docs | `.md` | `docs/` | API, usage, architecture |
| Report | `.md` + `.pdf` | `docs/REPORT.md` | Relatório final |

---

## 🎯 Success Criteria

**Projeto é sucesso se:**

1. ✅ **Modelo:** R² ≥ 0.85 no test set (20% dos dados)
2. ✅ **Performance:** Treino < 5 min, predição < 1 ms
3. ✅ **Otimizador:** Encontra config que melhora baseline 10%+
4. ✅ **Testes:** 100% coverage de `src/`
5. ✅ **Docs:** Todos módulos documentados (docstrings + .md)
6. ✅ **Reproducibilidade:** Alguém consegue rodar `python scripts/train.py` e obter mesmos resultados
7. ✅ **Relatório:** Paper/relatório submissível a IEEE SPI
8. ⭐ **Bonus:** Código em GitHub, publicado, reutilizável

---

## 🚫 Critérios de Falha

**Projeto falha se:**

- [ ] R² < 0.70 (modelo não é melhor que baseline)
- [ ] Não consegue treinar em laptop sem GPU
- [ ] Zero tests ou coverage < 50%
- [ ] Código não roda (`pip install` falha)
- [ ] Não há documentação (README vazio)
- [ ] Specs/design não existem ou desatualizados

---

## 📞 Dependências Externas

| Dependência | Descrição | Status |
|-------------|-----------|--------|
| Prof. Leandro | Feedback, validação | ✓ Agendado |
| SI/PI-Dataset | Dados de entrada | ✓ Baixado |
| sklearn/torch | Libraries | ✓ Instalado |
| Papers IEEE | Referências | ✓ Tem |
| GitHub (opcional) | Versionamento | ⏳ Setup pós-TCC |

---

## 🔄 Change Control

Se novo requisito surgir:
1. Abrir issue/discussion
2. Avaliar impacto no timeline
3. Atualizar scope se aprovado
4. Comunicar ao Prof. Leandro

---

## ✋ Constraints

- **Tempo:** 4 meses (agosto–novembro 2026)
- **Recurso:** 1 pessoa (André) part-time
- **Dados:** Limitado ao dataset TUHH (não coletar novos)
- **Compute:** Laptop padrão (8GB RAM, CPU)
- **Costo:** Gratuito (open-source)

---

**Aprovado por:** [Pendente Prof. Leandro]  
**Data aprovação:** ___  
**Próximo review:** +1 mês
