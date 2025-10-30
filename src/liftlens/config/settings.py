from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Global application settings."""

    app_name: str = "A/B Test Framework"
    debug: bool = False
    output_dir: Path = Path("output")
    data_source: Literal["csv", "parquet", "db", "delta"] = "csv"
    db_url: str = ""
    parallel_backend: Literal["joblib", "dask", "ray"] = "joblib"
    seed: int = 42
    registry_path: Path = Path(".liftlens_registry.sqlite")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    api_key: str | None = None

    model_config = {"env_prefix": "LIFTLENS_", "env_file": ".env", "extra": "ignore"}


settings = Settings()
