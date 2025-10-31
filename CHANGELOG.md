
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2025-10-30
### Added
- Full A/B testing pipeline with Welch's t-test, ANCOVA, CUPED, SRM detection
- Modular architecture: data, metrics, stats, viz, report, workflows, api
- Parallel processing (Joblib/Dask/Ray)
- FastAPI server and Streamlit dashboard
- SQLite experiment registry
- Comprehensive tests (74%+ coverage)
- Interactive Plotly reports (HTML/PDF)
- Synthetic data generator with heterogeneity
