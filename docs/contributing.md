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
