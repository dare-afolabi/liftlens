
# API Reference

liftlens exposes **three public entry‑points**:

1. **CLI**: `liftlens.cli:app`
2. **FastAPI**: `liftlens.api.server:app`
3. **Python SDK**: `liftlens.workflows.pipeline.run_pipeline`

---

## 1. CLI (`liftlens`)

```bash
poetry run liftlens --help
```

| Sub‑command | Description |
|-------------|-------------|
| `run` | Execute a full experiment from a YAML/JSON config |
| `list` | List runs in the SQLite registry |
| `show <run_id>` | Print run metadata & results |
| `serve` | Start FastAPI server (alias for `uvicorn`) |

#### Flags

```bash
--config PATH      # required
--output PATH      # optional (default: output/run_)
--log-level LEVEL  # DEBUG, INFO, WARNING, ERROR
```

---

## 2. FastAPI Endpoints

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| POST | /run | Submit experiment config: returns `run_id` | `X-API-Key` |
| GET | `/results/{run_id}` | Full JSON result | `X-API-Key` |
| GET | `/report/{run_id}` | HTML report (streamed) | `X-API-Key` |
| GET | `/health` | Health check | `-` |

#### Example

```bash
curl -X POST http://localhost:8000/run \
  -H "X-API-Key: $LIFTLENS_API_KEY" \
  -H "Content-Type: application/json" \
  -d @examples/revenue_test.yaml
```

---

## 3. Python SDK

```python
from pathlib import Path
from liftlens.workflows.pipeline import run_pipeline

run_pipeline(
    config_path=Path("examples/revenue_test.yaml"),
    output_dir=Path("output/run_1")
)
```

---

## 4. Core Registries

| Registry | Global Instance | Purpose |
|----------|-----------------|---------|
| `MetricRegistry` | `liftlens.metrics.registry.registry` | Register / call KPI functions |
| `ExperimentRegistry` | `liftlens.core.registry.registry` | SQLite persistence of runs |

#### Usage

```python
from liftlens.metrics.registry import registry as metric_reg
lift = metric_reg.call("mean", df, "group", "outcome")
```

---

## 5. Configuration Schemas (`pydantic`)

| Model | File |
|-------|------|
| `ExperimentConfig` | `src/liftlens/config/schemas.py` |
| `DataSource` | same |
| `MetricSpec` | same |
| `TransformConfig` | same |

All fields are **strictly typed** and validated on load.

---

## 6. Parallel Execution

```python
from liftlens.engine.parallel import parallel_apply

results = parallel_apply(my_func, items, backend="dask")
```

Supported backends: `joblib` (default), `dask`, `ray`.

_All endpoints, models, and registry calls are **fully implemented** and **type‑checked** with MyPy._


# == docs/contributing.md =

# Contributing

All contributions are welcome! Please follow the guidelines below.

---

## 1. Development Setup

```bash
git clone https://github.com/dare-afolabi/liftlens.git
cd liftlens
poetry install --with dev,docs,parallel
poetry run pre-commit install
```

---

## 2. Branching

| Type | Prefix |
|------|--------|
| Feature | `feat/` |
| Bugfix | `fix/` |
| Docs | `docs/` |
| Chore | `chore/` | 

```bash
git checkout -b feat/cuped-log-transform
```

---

## 3. Code Style

| Tool | Command |
|------|---------|
| **Black** | `poetry run black .` |
| **Ruff** | `poetry run ruff check .` |
| **MyPy** | `poetry run mypy src` |

All CI checks **must pass**.

---

## 4. Testing

```bash
# Unit tests
poetry run pytest -m "not slow"

# Full suite (including e2e)
poetry run pytest
```

_Aim for **≥ 95 %** coverage._

---

## 5. Adding a New Metric

1. Create `src/liftlens/metrics/my_metric.py`.
2. Implement a function with signature `(df, group_col, metric_col, **params) -> float`.
3. Register in `src/liftlens/metrics/registry.py`: 
```python
registry.register("my_metric", my_metric_func, alias="mm")
```
4. Write tests in `tests/unit/test_metrics/test_my_metric.py`.

---

## 6. Documentation

- **User‑facing**: `docs/user_guide.md`
- **API**: `docs/api_reference.md`
- **Contributing**: this file

Run locally:

```bash
poetry run mkdocs serve
```

---

## 7. Pull Request Checklist

- `black` formatted
- `ruff` clean
- `mypy` passes
- Tests added / updated
- Docs updated
- Changelog entry (if public)

---

## 8. Release Process

1. Bump version in `pyproject.toml`.
2. Update `CHANGELOG.md`.
3. Tag: `git tag -a vX.Y.Z -m "Release X.Y.Z"`.
4. Push tag - GitHub Actions publishes to PyPI.

*Thank you for helping make the framework better!*


