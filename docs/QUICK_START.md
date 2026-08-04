# Quick Start Guide

**For:**  André, Prof. Leandro, Claude Code  
**Time:** 5 minutes to be operational

---

## 🚀 1-Minute Setup

```bash
# Clone/enter project
cd /home/andre/Downloads/TCC

# Create conda environment
conda env create -f environment.yml

# Activate
conda activate tcc_pdn

# Verify datasets loaded
python scripts/verify_data.py
```

Expected output:
```
✓ 6-Layer PDN: 986 configs
✓ SE-SI Array: 1933 configs
✓ Diff-SI Array: 1917 configs
Ready to go!
```

---

## 📚 5-Minute Understanding

1. **What?** PDN impedance prediction with ML (ANN/GPR)
2. **Why?** EMI/EMC is critical; 90% of failures come from PDN
3. **How?** Surrogate model → GA optimization → feature analysis
4. **Data?** TU Hamburg SI/PI-Database (986+ configs of PDN)
5. **Timeline?** 16 weeks (4 months), phases in `spec/ROADMAP.md`

---

## 💻 Running Code

### Explore Data
```bash
jupyter notebook notebooks/01_data_exploration.ipynb
```

### Train Baseline Model
```bash
python scripts/train.py --model random_forest --log
```

### Run Tests
```bash
pytest tests/ -v --cov=src/
```

### View Experiments
```bash
ls -la experiments/*/results/
cat experiments/exp_001/results/metrics.json
```

---

## 🤖 Claude Code Multi-Agent

### When to use which agent:

**Agente 1: Explore (specs/design)**
```
/explore "how to structure data pipeline?"
→ Returns: insights + proposes design
```

**Agente 2: Implement (code)**
```
Edit src/models/surrogate.py
→ Returns: working code + tests
```

**Agente 3: Analysis (notebooks)**
```
Claude writes: notebooks/01_data_exploration.ipynb
→ Returns: plots + insights
```

**Agente 4: QA (review)**
```
/code-review
→ Returns: issues + fixes
```

---

## 📋 Project Structure (TL;DR)

```
TCC/
├─ spec/          ← Specs (why/what/when)
├─ design/        ← Architecture (how)
├─ src/           ← Code (implementation)
├─ notebooks/     ← Exploration
├─ data/          ← Datasets (raw/processed)
├─ experiments/   ← ML experiment tracking
├─ tests/         ← Unit + integration tests
└─ docs/          ← Final documentation
```

**Read first:** `README.md` → `CLAUDE.md` → `spec/RESEARCH_BRIEF.md`

---

## ✅ Key Files to Know

| File | Purpose | When to Read |
|------|---------|--------------|
| `README.md` | Overview | First (2 min) |
| `CLAUDE.md` | How to use Claude Code | Before coding (5 min) |
| `spec/RESEARCH_BRIEF.md` | Problem statement | Understand goal (10 min) |
| `spec/SCOPE.md` | What's in/out | Define boundaries (10 min) |
| `spec/ROADMAP.md` | Timeline + milestones | Plan work (5 min) |
| `design/architecture.md` | System design | Before coding (10 min) |
| `src/data/loader.py` | Load data | When implementing data pipeline |
| `notebooks/01_*.ipynb` | EDA | Explore first time |
| `tests/test_*.py` | Validation | Before merging code |

---

## 🔧 Common Commands

```bash
# Activate environment
conda activate tcc_pdn

# Run all tests with coverage
pytest tests/ -v --cov=src/ --cov-report=html

# Format code
black src/ tests/ notebooks/

# Check code quality
flake8 src/ tests/
mypy src/

# Launch Jupyter
jupyter lab notebooks/

# Train model (configure in experiments/exp_001/config.yaml)
python scripts/train.py --config experiments/exp_001/config.yaml

# View experiment results
cat experiments/exp_001/results/metrics.json | jq .

# Save current environment
conda env export > environment.yml
```

---

## 🐛 Troubleshooting

**Problem:** `ModuleNotFoundError: No module named 'sklearn'`
```bash
→ Solution: conda activate tcc_pdn
```

**Problem:** Jupyter kernel not found
```bash
→ Solution: python -m ipykernel install --user --name tcc_pdn
```

**Problem:** Data files not found
```bash
→ Solution: Run python scripts/verify_data.py
→ Ensure data/raw/ has subdirectories
```

**Problem:** Tests failing
```bash
→ Solution: pytest tests/ -v --tb=short
→ Check .gitignore if data files missing
```

---

## 📊 Data Access

All datasets in `data/raw/`:
- `6_layer_pdn_lhs/parameter.csv` (986 rows, 13 features)
- `universal_se_si/parameter.csv` (1933 rows)
- `universal_diff_si/parameter.csv` (1917 rows)

**Warning:** Do NOT commit raw data (in `.gitignore`). Process → `data/processed/`

---

## 🎯 Typical Workflow

```
1. Read specs (RESEARCH_BRIEF, SCOPE, ROADMAP)
2. Read design (architecture.md)
3. Explore data (notebooks/01_*)
4. Implement feature (edit src/*)
5. Write tests (edit tests/*)
6. Commit & push
7. Run /code-review
8. Update docs
9. Repeat
```

---

## 💬 Questions?

1. **About project:** See `spec/RESEARCH_BRIEF.md`
2. **About workflow:** See `CLAUDE.md`
3. **About code:** See docstrings in `src/`
4. **About results:** See `experiments/*/results/`
5. **Stuck?** Check `README.md` → `INSTALLATION.md`

---

**Next:** Read `README.md`, then `CLAUDE.md` 📖
