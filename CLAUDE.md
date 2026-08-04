# CLAUDE.md — Instruções para Claude Code (Multi-Agents & Spec-Driven Dev)

**Objetivo:** Este arquivo **define como trabalhar neste projeto** com Claude Code, especialmente em modo **multi-agents** e **spec-driven development**.

---

## 🎯 Princípios Gerais

1. **Spec-Driven:** Ler `spec/` ANTES de qualquer código. Specs definem O QUÊ, não COMO.
2. **Design-First:** Ler `design/` para entender arquitetura. Nunca coda sem plano.
3. **Code-Second:** Implementação é a última etapa.
4. **Tests-Always:** Tudo tem testes (unit + integration).
5. **Docs-Live:** Documentação é código; manter sincronizado.

---

## 📂 Convenções de Diretórios

| Diretório | Propósito | Quem usa | Exemplos |
|-----------|----------|---------|----------|
| `spec/` | Especificações (requisitos, escopo) | Planejamento, design | SCOPE.md, ROADMAP.md |
| `design/` | Design docs (arquitetura, APIs) | Antes de código | architecture.md, data_pipeline.md |
| `src/` | Código produção | Desenvolvimento | Python packages, modules |
| `notebooks/` | Exploração + prototipagem | Pesquisa, EDA | Jupyter notebooks numerados |
| `data/` | Datasets e referências | Análise, treino | raw/, processed/, external/ |
| `experiments/` | Rastreamento de experimentos | ML, otimização | exp_*/config.yaml, results/ |
| `tests/` | Testes (unit, integration) | QA | test_*.py |
| `scripts/` | Utilitários e entry points | Ops | train.py, verify_data.py |
| `docs/` | Documentação geral | Comunicação | INSTALLATION.md, API.md |

---

## 🤖 Multi-Agent Workflow

Quando usar **múltiplos agentes Claude em paralelo:**

### Agente 1: **Spec & Architecture** (Explore + Plan)
**Quando:** Definindo novo feature ou refatoração  
**O que faz:** Lê specs, design docs, propõe arquitetura  
**Saída:** `design/*.md`, updated specs  
**Comandos:**
```bash
# Agente explora codebase e propõe design
claude-code explore --query "como estruturar data pipeline para 3 datasets?"
claude-code plan --prompt "design module de data loading"
```

### Agente 2: **Implementation** (Code)
**Quando:** Construindo novo módulo depois de Agente 1 validar  
**O que faz:** Implementa em `src/`, segue design doc  
**Saída:** Python code, testes  
**Comandos:**
```bash
# Escrever módulo especificado no design
claude-code edit src/data/loader.py
claude-code write tests/test_data.py
```

### Agente 3: **Analysis & Experiments** (Notebooks)
**Quando:** Explorando dados, prototipando modelos  
**O que faz:** Jupyter notebooks, análise, gráficos  
**Saída:** `notebooks/*.ipynb`, `experiments/*/results/`  
**Comandos:**
```bash
claude-code write notebooks/01_data_exploration.ipynb
```

### Agente 4: **Testing & QA** (Code Review)
**Quando:** Antes de merge  
**O que faz:** Roda testes, valida spec compliance, code review  
**Saída:** Test reports, coverage  
**Comandos:**
```bash
pytest tests/ --cov=src/
pytest tests/ -v --tb=short
```

---

## 📋 Spec-Driven Development (Template)

Toda tarefa começa com uma **spec** em `spec/`:

### Exemplo: Spec para "Carregar datasets"

**Arquivo:** `spec/LOAD_DATA_SPEC.md`

```markdown
# Spec: Data Loading Pipeline

## Requisitos
1. Carregar 3 datasets (PDN, SE-SI, Diff-SI) em paralelo
2. Validar integridade (n_rows, n_cols vs. esperado)
3. Retornar dicts: `{"pdn": df, "se_si": df, "diff_si": df}`
4. Cache: se já processado, skip re-load (usar pickle/parquet)

## Entradas
- `data/raw/*/parameter.csv` (tabulares)
- `data/raw/*/variation/*.S*p` (Touchstone, se necessário)

## Saídas
- `data/processed/{dataset_name}.pkl` ou `.parquet`
- Log de validação

## Aceitação
- ✓ Carrega 3 datasets em < 30s
- ✓ Valida schemas
- ✓ Testes passam com 100% de cobertura

## Design (já disponível em design/data_pipeline.md)
```

**Uso:** Agente 1 cria/refina spec. Agente 2 implementa conforme spec. Agente 4 valida.

---

## 🔄 Workflow Típico (Multi-Agent)

### Cenário: "Treinar surrogate model para PDN"

**Passo 1: Spec & Design (Agente 1 + Explore)**
```
User: "Vamos treinar ANN para prever Z_max da PDN. Me ajuda a planejar."

Agente 1 (Explore):
  - Lê design/architecture.md
  - Lê design/model_design.md (já existe?)
  - Se não existir, cria: design/model_design.md
  - Define: features entrada, alvo, train/test split, arquitetura ANN
  - Output: design doc aprovado pelo usuário
```

**Passo 2: Implementação (Agente 2)**
```
User: "Tá bom, agora implementa conforme design."

Agente 2:
  - Lê design/model_design.md
  - Cria: src/models/surrogate.py
  - Cria: tests/test_surrogate.py
  - Output: Módulo pronto, testes verdes
```

**Passo 3: Análise & Experimento (Agente 3)**
```
User: "Treina o modelo com os dados e plota resultados."

Agente 3:
  - Cria: notebooks/03_surrogate_training.ipynb
  - Executa treinamento
  - Salva experimento em experiments/exp_001_baseline/
  - Output: Gráficos, métricas, modelo treinado
```

**Passo 4: QA & Merge (Agente 4)**
```
User: "Valida tudo antes de finalizarmos."

Agente 4:
  - Roda pytest, coverage
  - Verifica compliance com spec
  - Output: "Pronto pra merge"
```

---

## 🎯 Specs Atuais (Ler PRIMEIRO)

| Spec | Status | Prioridade |
|------|--------|-----------|
| [`spec/RESEARCH_BRIEF.md`](spec/RESEARCH_BRIEF.md) | ✓ Criado | 1 |
| [`spec/SCOPE.md`](spec/SCOPE.md) | ✓ Criado | 1 |
| [`spec/ROADMAP.md`](spec/ROADMAP.md) | ✓ Criado | 1 |
| [`design/architecture.md`](design/architecture.md) | ✓ Criado | 2 |
| [`design/data_pipeline.md`](design/data_pipeline.md) | ✓ Criado | 2 |
| [`design/model_design.md`](design/model_design.md) | ⏳ TODO | 3 |
| `spec/LOAD_DATA_SPEC.md` | ⏳ TODO | 3 |

---

## 🚨 Regras Duras

### ✅ Fazer:
- [ ] Ler `spec/` e `design/` ANTES de escrever código
- [ ] Um arquivo = uma responsabilidade
- [ ] Testes pra tudo que é lógica
- [ ] Documentação inline (docstrings)
- [ ] Usar `hydra` para configs (não hardcode)
- [ ] Experimentos em `experiments/exp_XXX/` com config + logs

### ❌ Não Fazer:
- [ ] Não codar sem spec/design aprovado
- [ ] Não misturar EDA + produção (notebooks vs src/)
- [ ] Não commitar dados grandes (use .gitignore)
- [ ] Não deixar código "TODO" sem issue
- [ ] Não usar print() (usar logger)

---

## 💾 Git Workflow (Se Versionando)

```bash
# Sempre em branch de feature
git checkout -b feat/load-data-pipeline

# Commits atômicos (um spec/design/code change por commit)
git add spec/LOAD_DATA_SPEC.md && git commit -m "spec: define data loading interface"
git add design/data_pipeline.md && git commit -m "design: data pipeline architecture"
git add src/data/loader.py && git commit -m "feat: implement data loader"
git add tests/test_data.py && git commit -m "test: add data loader tests"

# Push e PR (só merge após Agente 4 OK)
git push origin feat/load-data-pipeline
```

---

## 🔧 Ferramentas Aprovadas

| Ferramenta | Uso | Config |
|-----------|-----|--------|
| `pytest` | Testes unitários | `tests/conftest.py` |
| `hydra` | Configuração | `config/*.yaml` |
| `mlflow` | Rastreamento de experimentos | `experiments/*.py` |
| `pandas` | Data manipulation | Padrão |
| `scikit-learn` | ML baseline | `src/models/` |
| `torch` | Deep learning (se precisar) | `requirements.txt` |
| `jupyter` | Exploração | `notebooks/` |

---

## 📞 Quando Chamar Qual Agente

| Tarefa | Agente | Comando |
|--------|--------|---------|
| "Entender arquitetura" | Explore | `/explore` ou `/code-review` |
| "Planejar feature" | Plan | `/plan` (ou ExitPlanMode) |
| "Implementar módulo" | Implement | Edit/Write files |
| "Explorar dados" | Analysis | Write notebooks |
| "Validar tudo" | Code-Review | `/code-review` |
| "Paralelo: 2+ tarefas" | Multi | Launch 2–3 agentes em paralelo via Bash |

---

## 📖 Leitura Recomendada (Ordem)

1. [`README.md`](README.md) — Visão geral
2. [`spec/RESEARCH_BRIEF.md`](spec/RESEARCH_BRIEF.md) — Por que fazemos isso
3. [`spec/SCOPE.md`](spec/SCOPE.md) — O que vamos fazer
4. [`spec/ROADMAP.md`](spec/ROADMAP.md) — Quando vamos fazer
5. [`design/architecture.md`](design/architecture.md) — Como estruturamos
6. Código em `src/` (depois de tudo acima)

---

## 🎓 Exemplo: Session com Multi-Agents

```
User: "Vamos começar a análise de dados? Preciso de exploração + design de features."

Claude (como agente orquestrador):
  1. Chama Explore: "Leia os datasets e descreva o que vê"
     → Output: Insights sobre dimensionalidade, missing values, ranges
  2. Chama Plan: "Baseado no Explore, projeta engenharia de features"
     → Output: design/feature_engineering.md
  3. Chama Analysis: "Cria notebook 01 com EDA"
     → Output: notebooks/01_data_exploration.ipynb
  4. Chama Code: "Implementa feature_engineering.py conforme design"
     → Output: src/features/engineering.py + tests
  5. Chama QA: "Valida tudo"
     → Output: "Pronto! R² = 0.87 em holdout."
```

---

## ❓ FAQ

**P: Posso começar a codar direto sem spec?**  
R: Não. Spec-driven dev economiza tempo no longo prazo.

**P: E se a spec precisar mudar?**  
R: Update a spec, update o design, depois código. Isso é iterativo.

**P: Como rastrear experimentos?**  
R: Use `mlflow` ou crie `experiments/exp_001/config.yaml + results/`.

**P: Posso usar notebooks em produção?**  
R: Não. Notebooks são exploração. Código pronto vai em `src/`.

---

## 🔗 Referências Rápidas

- Specs: `spec/`
- Design: `design/`
- Código: `src/`
- Notebooks: `notebooks/`
- Testes: `tests/`
- Experimentos: `experiments/`
- Dados: `data/`

---

**Última atualização:** 2026-07-09  
**Autor:** Claude Code  
**Próximo passo:** Validar specs com usuário
