<img src="assets/logo.jpeg" alt="LiftLens logo">

# liftlens

![Build Status](https://img.shields.io/github/actions/workflow/status/dare-afolabi/liftlens/ci.yml?branch=main&style=for-the-badge)
![Coverage](https://img.shields.io/codecov/c/github/dare-afolabi/liftlens?style=for-the-badge)
![PyPI version](https://img.shields.io/pypi/v/liftlens?style=for-the-badge)
![License: MIT](https://img.shields.io/badge/license-MIT-blue?style=for-the-badge)
![Downloads](https://img.shields.io/pypi/dm/liftlens?style=for-the-badge)
[![Sponsor](https://img.shields.io/badge/Sponsor-%E2%9D%A4-lightgrey?style=for-the-badge&logo=github-sponsors)](https://github.com/sponsors/dare-afolabi)

Confirm the lift before you launch using **liftlens**, an **enterprise-grade A/B testing platform** with:

- **CUPED**, **SRM detection**, **sequential testing (OBF/Pocock)**
- **Heterogeneous treatment effects** (Causal Forest, S/X/T-Learner)
- **FastAPI + JWT auth**, **Streamlit dashboard**
- **Parallel execution** (Joblib/Dask/Ray)
- **Interactive HTML/PDF reports** with Plotly
- **SQLite experiment registry**
- **95%+ test coverage**, **CI/CD ready**

---

## Quick Start

```bash
# 1. Clone & install
git clone https://github.com/dare-afolabi/liftlens.git
cd liftlens
poetry install --with dev,docs

poetry run generate-synthetic --n_users 10000 --output data/synthetic.csv

# 3. Run experiment
poetry run liftlens run \
  --config examples/revenue_test.yaml \
  --output output/run_1

# 4. Launch API + Dashboard
docker-compose up
```

- **API:** `http://localhost:8000/docs`
- **Dashboard:** `http://localhost:8501`
- **Report:** `output/run_1/report.html`

---

## Configuration (YAML)

```yaml
# examples/revenue_test.yaml
name: Revenue Lift Test
data:
  type: csv
  path: data/synthetic.csv
baseline_col: baseline
outcome_col: outcome
group_col: group
metrics:
  - name: revenue_lift
    func: mean_diff
  - name: arpu
    func: ratio_metric
    params:
      denominator_col: active_users
transform:
  winsorize: [0.01, 0.01]
  cuped: true
  log_transform: true
stats:
  sequential: true
  method: obf
```

---

## Features

- CUPED Variance Reduction
- SRM Detection (Chi²)
- Sequential Testing (OBF/Pocock)
- Bootstrap + Permutation Tests
- Multiple Comparison Corrections
- Heterogeneous Treatment Effects
- ANCOVA, Mixed Effects, GAM
- FastAPI + API Key Auth
- Streamlit Dashboard
- HTML/PDF Reports (Jinja2 + WeasyPrint)
- Parallel Processing
- SQLite Registry
- Docker Compose

---

## Project Structure

```bash
liftlens/
├── core/           # Session, registry
├── config/         # Pydantic schemas
├── data/           # IO, validation, transforms
├── metrics/        # Primary, robust, composite
├── stats/          # Inference, power, sequential, HTE
├── viz/            # Plotly: dist, effects, diagnostics
├── report/         # Jinja2 templates + builder
├── workflows/      # Pipeline, presets
├── engine/         # Parallel execution
├── api/            # FastAPI, Streamlit, auth
├── utils/          # Logging, decorators
└── cli.py          # Typer CLI
```

---

## Development

```bash
# Install pre-commit
poetry run pre-commit install

# Run tests
poetry run pytest -m "not slow"

# Lint & format
poetry run ruff check .
poetry run black .

# Build docs
poetry run mkdocs serve
```

---

## License

Apache 2.0


