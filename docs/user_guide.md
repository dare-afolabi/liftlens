
# User Guide

**liftlens** is a modular, end‑to‑end platform for running statistically‑sound experiments at scale.

---

## 1. Installation

```bash
git clone https://github.com/dare-afolabi/liftlens.git
cd liftlens
poetry install --with dev,docs
```

### Optional extras

```bash
poetry install --extras "parallel"   # Dask / Ray
poetry install --extras "docs"       # MkDocs
```

---

## 2. Generate Synthetic Data

```bash
poetry run generate-synthetic \
  --n_users 10_000 \
  --effect_size 0.08 \
  --heterogeneity \
  --output data/synthetic.csv
```

*Creates a CSV with `user_id`, `group`, `baseline`, `outcome`, `country`.*

---

## 3. Run an Experiment

### 3.1 CLI (recommended)

```bash
poetry run liftlens run \
  --config examples/revenue_test.yaml \
  --output output/run_1
```

### 3.2 Python API

```python
from pathlib import Path
from liftlens.workflows.pipeline import run_pipeline

run_pipeline(
    config_path=Path("examples/revenue_test.yaml"),
    output_dir=Path("output/run_1")
)
```

---

## 4. Configuration (YAML)

```yaml
# examples/revenue_test.yaml
name: Revenue Lift Test
data:
  type: csv or parquet
  path: data/synthetic.csv          # S3, GCS, DB URL also supported
baseline_col: baseline
outcome_col: outcome
group_col: group
control_label: control
treatment_label: treatment

metrics:
  - name: revenue_lift
    func: mean_diff
    weight: 1.0
  - name: arpu
    func: ratio_metric
    params:
      denominator_col: active_users

transform:
  winsorize: [0.01, 0.01]   # 1 % tail clipping
  cuped: true
  log_transform: true
  standardize: false

stats:
  alpha: 0.05
  sequential:
    enabled: true
    method: obf            # obf | pocock
  power:
    target: 0.80
    effect_size: 0.08

report:
  format: html             # html | pdf
  interactive: true
```

---

## 5. Key Features

| Feature | How to enable |
|---------|---------------|
| CUPED | `transform.cuped: true` |
| SRM detection | Automatic (Chi²) |
| Sequential testing | `stats.sequential.enabled: true` |
| Heterogeneous effects | Use `causal_forest_effect` or `meta_learner_effect` in custom code |
| Parallel execution | Set `LIFTLENS_PARALLEL_BACKEND=dask` in `.env` |
| API authentication | X-API-Key header (see `.env.example`) |

--- 

## 6. View Results

```bash
# HTML report
open output/run_1/report.html

# API
curl -H "X-API-Key: $LIFTLENS_API_KEY" http://localhost:8000/results/

# Dashboard
http://localhost:8501
```

---

## 7. Docker Compose (API + Dashboard)

```bash
docker-compose up -d
```

*FastAPI:* **8000** | *Streamlit:* **8501**

---

## 8. Extending the Framework

1. **Add a metric:** `src/liftlens/metrics/registry.py` + new file under `metrics/`.
2. **Custom transform:** `src/liftlens/data/transform.py`.
3. **New statistical test:** `src/liftlens/stats/`.

All new modules are auto‑registered via the global registry.

---

## 9. Troubleshooting

| Symptom | Fix |
|---------|-----|
| `FileNotFoundError` on data | Use absolute path or S3 URI |
| `KeyError: denominator_col` | Provide params in metric spec |
| `ImportError: econml` | `pip install econml` (optional) |

*All commands above have been verified with the current codebase.*


