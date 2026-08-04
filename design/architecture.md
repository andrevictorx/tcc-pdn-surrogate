# Architecture: PDN ML Optimization System

**Document:** High-level system design  
**Version:** 1.0  
**Date:** 2026-07-09  

---

## 🏗️ System Overview

```
┌─────────────────────────────────────────────────────┐
│                    User / Researcher                │
└────────────────────┬────────────────────────────────┘
                     │
    ┌────────────────┴──────────────────┐
    │                                   │
┌───▼──────────────────┐    ┌──────────▼────────────┐
│  notebooks/*.ipynb   │    │  scripts/train.py    │
│  (Exploration)       │    │  (Automation)        │
└───┬──────────────────┘    └──────────┬────────────┘
    │                                   │
    └────────────────────┬──────────────┘
                         │
            ┌────────────▼──────────────┐
            │  src/ (Core Logic)        │
            │                           │
            │  ├─ data/                 │
            │  │  ├─ loader.py          │
            │  │  └─ preprocessor.py    │
            │  │                        │
            │  ├─ models/               │
            │  │  ├─ surrogate.py       │
            │  │  └─ optimizer.py       │
            │  │                        │
            │  ├─ analysis/             │
            │  │  ├─ sensitivity.py     │
            │  │  └─ visualization.py   │
            │  │                        │
            │  └─ utils/                │
            │     ├─ config.py          │
            │     └─ logger.py          │
            └────────────┬──────────────┘
                         │
        ┌────────────────┴─────────────────┐
        │                                  │
    ┌───▼──────────────┐      ┌──────────▼─────────┐
    │  data/           │      │  experiments/      │
    │  ├─ raw/         │      │  ├─ exp_001/       │
    │  ├─ processed/   │      │  │  ├─ config.yaml │
    │  └─ external/    │      │  │  └─ results/    │
    │                  │      │  └─ exp_002/       │
    └──────────────────┘      └────────────────────┘
         │                              │
         └──────────────┬───────────────┘
                        │
                  ┌─────▼──────┐
                  │  Outputs   │
                  │  models/   │
                  │  metrics/  │
                  │  plots/    │
                  └────────────┘
```

---

## 📦 Module Structure

### 1. `src/data/` — Data Pipeline
**Responsibility:** Carregar, validar, preprocessar dados

```python
# loader.py
def load_pdn_dataset(path: str) -> pd.DataFrame:
    """Carrega CSV do PDN, valida schema."""
    pass

def load_touchstone(path: str) -> np.ndarray:
    """Carrega arquivo Touchstone (.S2p), retorna S-params."""
    pass

# preprocessor.py
class PDNPreprocessor:
    def normalize_features(self) -> pd.DataFrame:
        """Normaliza features (StandardScaler)."""
    
    def extract_target(self) -> pd.Series:
        """Extrai |Z_max| de S-parâmetros."""
    
    def train_test_split(self, test_size=0.2):
        """Split 80/20 com stratification."""
```

**Input:** `data/raw/{pdn_lhs}/parameter.csv` + `variation/*.S2p`  
**Output:** `data/processed/pdn_preprocessed.pkl`

---

### 2. `src/models/` — ML Models
**Responsibility:** Treinar, prever, otimizar

```python
# surrogate.py
class SurrogateModel:
    """Wrapper para ANN ou GPR."""
    
    def __init__(self, model_type='gpr', n_features=13):
        self.model = GaussianProcessRegressor() or MLPRegressor()
    
    def train(self, X_train, y_train, cv=5):
        """Treinar com CV, log metrics."""
        pass
    
    def predict(self, X) -> np.ndarray:
        """Prever Z_max para configs novas."""
        pass
    
    def evaluate(self, X_test, y_test) -> dict:
        """Retorna R², RMSE, MAPE, etc."""
        pass
    
    def save(self, path: str):
        """Serializar com joblib."""
        pass

# optimizer.py
class PDNOptimizer:
    """GA ou Bayesian Optimization para PDN."""
    
    def __init__(self, surrogate: SurrogateModel, constraints: dict):
        self.surrogate = surrogate
        self.constraints = constraints  # e.g., {"cavity_height_max": 80}
    
    def objective(self, config: dict) -> float:
        """Fitness: minimizar |Z_max|."""
        z_max = self.surrogate.predict([config])[0]
        return z_max
    
    def optimize(self, n_generations=100) -> dict:
        """Rodar GA, retornar config ótima."""
        pass
    
    def plot_convergence(self):
        """Gráfico de fitness vs. generation."""
        pass
```

**Input:** Modelo treinado + constraints  
**Output:** Config ótima + logs

---

### 3. `src/analysis/` — Analysis & Visualization
**Responsibility:** Insights, plots, relatórios

```python
# sensitivity.py
def shap_importance(model, X) -> pd.DataFrame:
    """Feature importance via SHAP values."""
    pass

def correlation_features(X) -> np.ndarray:
    """Matriz de correlação."""
    pass

# visualization.py
def plot_z_freq_response(s_params, frequencies):
    """Plot Z(f) — impedância vs. frequência."""
    pass

def plot_ga_convergence(history):
    """Convergência do GA ao longo de gerações."""
    pass

def plot_feature_importance(shap_values):
    """Bar plot de top-10 features."""
    pass
```

**Output:** Gráficos em `experiments/exp_*/plots/`

---

### 4. `src/utils/` — Utilities
**Responsibility:** Configuração, logging, helpers

```python
# config.py
from dataclasses import dataclass

@dataclass
class TrainConfig:
    learning_rate: float = 0.001
    batch_size: int = 32
    epochs: int = 100
    cv_folds: int = 5
    random_seed: int = 42

# logger.py
import logging
logger = logging.getLogger(__name__)

def setup_logging(log_file: str):
    """Configure logger para arquivos + console."""
    pass
```

---

## 🔄 Data Flow

```
1. RAW DATA
   ├─ data/raw/6_layer_pdn_lhs/parameter.csv (986 rows)
   └─ data/raw/6_layer_pdn_lhs/variation/*.S2p (986 files)
            │
            ▼
2. LOAD & VALIDATE
   ├─ src/data/loader.py
   └─ Check: n_rows=986, n_features=13, S-params valid
            │
            ▼
3. PREPROCESS
   ├─ Normalize features (StandardScaler)
   ├─ Extract target: |Z_max| from S-params
   ├─ Handle missing (0 expected, log if any)
   └─ Train/test split: 80%/20%
            │
            ▼
4. PROCESSED DATA
   └─ data/processed/pdn_preprocessed.pkl (X_train, X_test, y_train, y_test)
            │
            ▼
5. TRAIN MODEL
   ├─ src/models/surrogate.py
   ├─ ANN or GPR with 5-fold CV
   └─ Log metrics (R², RMSE) to MLflow
            │
            ▼
6. TRAINED MODEL
   └─ experiments/exp_001/models/surrogate.pkl
            │
            ▼
7. OPTIMIZE
   ├─ src/models/optimizer.py (GA or Bayesian)
   ├─ Use surrogate as fitness function
   └─ Constraint: cavity_height ≤ 80 mil, etc.
            │
            ▼
8. OPTIMIZED CONFIG
   └─ experiments/exp_001/results/best_config.yaml
            │
            ▼
9. ANALYSIS
   ├─ src/analysis/sensitivity.py (SHAP)
   └─ Feature importance + design guidelines
            │
            ▼
10. OUTPUTS
    ├─ experiments/exp_001/results/*.json (metrics)
    ├─ experiments/exp_001/plots/*.png (visualizations)
    └─ docs/REPORT.md (final report)
```

---

## 🔗 Dependencies

```
External Libraries:
├─ numpy, scipy (numeric)
├─ pandas (data manipulation)
├─ scikit-learn (baseline ML)
├─ scipy.optimize, deap (optimization)
├─ torch / tensorflow (optional, for NN)
├─ shap (interpretability)
├─ matplotlib, seaborn (plotting)
├─ hydra-core (config management)
├─ mlflow (experiment tracking)
└─ pytest (testing)

Internal Modules:
├─ src.data
├─ src.models
├─ src.analysis
├─ src.utils
└─ tests.*
```

---

## 🧪 Testing Strategy

```
Unit Tests (pytest):
├─ test_data.py
│  ├─ test_loader_reads_csv()
│  ├─ test_preprocessor_normalizes()
│  └─ test_train_test_split_valid()
├─ test_models.py
│  ├─ test_surrogate_trains()
│  ├─ test_surrogate_predict_shape()
│  └─ test_optimizer_converges()
└─ test_utils.py
   ├─ test_config_loads()
   └─ test_logger_writes()

Integration Tests:
├─ test_pipeline_end_to_end()
│  ├─ Load data → Preprocess → Train → Optimize
│  └─ Verify outputs exist + valid

Coverage Target: ≥ 90% of src/
```

---

## 📊 Experiment Tracking

**Tool:** MLflow (or Hydra + custom logger)

```
experiments/
├─ exp_001_baseline/
│  ├─ config.yaml
│  │  ├─ model_type: "random_forest"
│  │  ├─ n_estimators: 100
│  │  └─ random_seed: 42
│  ├─ results/
│  │  ├─ metrics.json      (R², RMSE, time)
│  │  ├─ predictions.csv   (y_true, y_pred)
│  │  └─ model.pkl         (serialized)
│  └─ logs/
│     └─ train.log         (stdout + errors)
│
└─ exp_002_gpr/
   ├─ config.yaml
   │  ├─ model_type: "gpr"
   │  ├─ kernel: "rbf"
   │  └─ n_restarts: 5
   ├─ results/
   └─ logs/
```

**Purpose:** Rastrear qual modelo, params, fecha de experimento, permite reproducibilidade.

---

## 🔐 Reproducibility

Requisitos:
1. **Seeds:** Todos randoms têm `random_seed: 42`
2. **Versions:** Pin `requirements.txt` com versões exatas
3. **Data:** Checksums de datasets (`data/raw/checksums.txt`)
4. **Config:** Tudo em YAML, zero hardcode
5. **Logs:** Salvar stdout de treinamento

Reproduzir:
```bash
python scripts/train.py --config experiments/exp_001/config.yaml
# Deve gerar mesmos R², loss curves, etc.
```

---

## 🚀 Deployment (Future)

**Scope TCC:** Não incluído  
**Future:** Possível containerizar (Docker) + API (FastAPI)

```dockerfile
# Dockerfile (v2.0)
FROM python:3.9-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ /app/src
CMD ["python", "-m", "app.api"]
```

---

**Owner:** André + Prof. Leandro  
**Next:** Refinar `design/data_pipeline.md`, `design/model_design.md`
