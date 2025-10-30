
from pathlib import Path
from typing import Literal, cast

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from loguru import logger
from sqlalchemy import create_engine, text

from ..config.schemas import DataSource
from .validator import validate_schema


def load_data(source: str | Path | DataSource) -> pd.DataFrame:
    """
    Unified data loader supporting CSV, Parquet, SQL databases, and Delta Lake.

    Args:
        source: Path string, Path object, or DataSource config.

    Returns:
        pandas.DataFrame with loaded data.
    """
    if isinstance(source, (str, Path)):
        src_type = _detect_type(str(source))
        source = DataSource(type=cast(Literal["csv", "parquet", "db", "delta"], src_type), path=Path(source))

    if not isinstance(source, DataSource):
        raise TypeError("source must be str, Path, or DataSource")

    logger.info(f"Loading data from {source.type}: {source.path or source.table}")

    if source.type == "csv":
        df = pd.read_csv(source.path)
    elif source.type == "parquet":
        table = pq.read_table(source.path)
        df = table.to_pandas()
    elif source.type == "db":
        engine = create_engine(_get_db_url())
        if source.query:
            df = pd.read_sql(text(source.query), engine)
        else:
            df = pd.read_sql_table(source.table, engine)
    elif source.type == "delta":
        import deltalake as dl
        df = dl.read(source.path).to_pandas()
    else:
        raise ValueError(f"Unsupported data source type: {source.type}")

    logger.info(f"Loaded {len(df):,} rows, {len(df.columns)} columns")
    validate_schema(df, source.type)
    return df


def save_data(df: pd.DataFrame, path: str | Path, format: str | None = None) -> None:
    """Save DataFrame to disk in specified format."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fmt = format or _detect_format(path)

    if fmt == "csv":
        df.to_csv(path, index=False)
    elif fmt == "parquet":
        table = pa.Table.from_pandas(df)
        pq.write_table(table, path)
    else:
        raise ValueError(f"Unsupported save format: {fmt}")

    logger.info(f"Saved data to {path}")


def _detect_type(path_str: str) -> str:
    """Detect file type from extension."""
    if path_str.endswith(('.csv', '.csv.gz')):
        return "csv"
    elif path_str.endswith('.parquet'):
        return "parquet"
    elif path_str.startswith(('postgresql://', 'sqlite://', 'mysql://')):
        return "db"
    elif path_str.endswith('/'):  # directory → assume Delta
        return "delta"
    else:
        raise ValueError(f"Cannot detect type from path: {path_str}")


def _detect_format(path: Path) -> str:
    """Detect output format from file extension."""
    if path.suffix in {'.csv', '.gz'}:
        return "csv"
    elif path.suffix == '.parquet':
        return "parquet"
    else:
        return "parquet"  # default


def _get_db_url() -> str:
    """Get database URL from environment or config."""
    from ..config.settings import settings
    if settings.db_url:
        return settings.db_url
    raise ValueError("DB_URL not configured. Set LIFTLENS_DB_URL environment variable.")


