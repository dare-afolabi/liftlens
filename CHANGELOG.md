
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
- Comprehensive tests 74%+ coverage)
- Interactive Plotly reports (HTML/PDF)
- Synthetic data generator with heterogeneity

### Changed
- Original `ab_test.py` refactored into `workflows/presets.py`
- Enhanced logging with Loguru (JSON/rotating)

### Fixed
- Group normalization, winsorization bounds validation
- Small sample fallbacks (Mann-Whitney U)

## [0.0.1] - 2025-10-28
### Added
- Initial `ab_test.py` and `generate_synthetic_data.py`
- A self-contained A/B Test Pipeline for CSV or PostgreSQL input. Features include:
  - Supports input from **CSV** or **PostgreSQL** database (`--input db`), accommodating real-world data sources.
  - **Handles key A/B testing elements**: metric selection (`--metric spend_amount`), baseline covariate (`--baseline_col baseline`), group assignment (`--group_col group`), and user identification (`--user_col user_id`).
  - **Implements preprocessing**: optional random or quartile-stratified sampling (`--n_users`, `--sample_by_q`), and winsorization at specified quantiles (`--winsor_lower`, `--winsor_upper`).
  - **Performs statistical inference**: **Welch’s t-test** (for unequal variances) and **ANCOVA** (to control for baseline differences), both standard in A/B testing for mean comparisons.
  - Generates **diagnostic figures** (histograms with `--bins` and boxplots) and a comprehensive Markdown report (`liftlens_report.md`) in the specified output directory.
  - **Reproducibility and Usability**: Fixed random seed (`--random_seed`), verbose logging (`-v`), and a detailed CLI (`--help`) ensure transparent, repeatable execution. Example commands in `arguments_example.sh` and the quick-start workflow demonstrate practical usability.
- **Outputs**: processed dataset (`liftlens_data.csv`), figures (`*.png`), and a full report (`liftlens_report.md`).

[0.1.0]: https://github.com/dare-afolabi/liftlens/compare/0.0.1...0.1.0


