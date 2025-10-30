import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from loguru import logger

from .session import session


class ExperimentRegistry:
    """SQLite-based experiment registry with MLflow-compatible metadata."""

    SCHEMA_VERSION = 1

    def __init__(self, db_path: Path | None = None):
        # Default to a registry file inside the session's temp dir so tests
        # and ephemeral runs do not pollute the repository root. This keeps
        # test runs isolated and avoids stale entries across test runs.
        self.db_path = db_path or (session.temp_dir / ".liftlens_registry.sqlite")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS experiments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    run_id TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    status TEXT CHECK(status IN ('running', 'completed', 'failed')),
                    config_json TEXT NOT NULL,
                    results_json TEXT,
                    tags_json TEXT,
                    schema_version INTEGER NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    experiment_id INTEGER,
                    metric_name TEXT,
                    value REAL,
                    step INTEGER,
                    FOREIGN KEY(experiment_id) REFERENCES experiments(id)
                )
            """)
            # Ensure schema version (PRAGMA doesn't accept parameter placeholders)
            conn.execute(f"PRAGMA user_version = {int(self.SCHEMA_VERSION)}")
        logger.debug(f"Registry initialized at {self.db_path}")

    def start_run(
        self, name: str, config: dict[str, Any], tags: dict[str, str] | None = None
    ) -> str:
        # Include microseconds to avoid collisions when runs start within the
        # same second (unit tests / CI can start multiple runs quickly).
        run_id = f"run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}_{session.seed}"
        start_time = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO experiments
                (run_id, name, start_time, status, config_json, tags_json, schema_version)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    run_id,
                    name,
                    start_time,
                    "running",
                    # Serialize Pydantic models / objects safely; fall back to JSON-serializing with str for unknown types
                    json.dumps(
                        (
                            config.model_dump()
                            if hasattr(config, "model_dump")
                            else (config.dict() if hasattr(config, "dict") else config)
                        ),
                        default=str,
                    ),
                    json.dumps(tags or {}, default=str),
                    self.SCHEMA_VERSION,
                ),
            )
        logger.info(f"Started experiment run: {run_id}")
        return run_id

    def end_run(
        self,
        run_id: str,
        status: str = "completed",
        results: dict[str, Any] | None = None,
    ) -> None:
        end_time = datetime.now(timezone.utc).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE experiments
                SET end_time = ?, status = ?, results_json = ?
                WHERE run_id = ?
            """,
                (
                    end_time,
                    status,
                    json.dumps(results, default=str) if results else None,
                    run_id,
                ),
            )
        logger.info(f"Ended experiment run {run_id}: {status}")

    def log_metric(
        self, run_id: str, metric_name: str, value: float, step: int = 0
    ) -> None:
        exp_id = self._get_experiment_id(run_id)
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT INTO metrics (experiment_id, metric_name, value, step)
                VALUES (?, ?, ?, ?)
            """,
                (exp_id, metric_name, value, step),
            )

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute("SELECT * FROM experiments WHERE run_id = ?", (run_id,))
            row = cur.fetchone()
            if not row:
                return None
            return dict(row)

    def list_runs(self, name: str | None = None) -> list[dict[str, Any]]:
        query = "SELECT * FROM experiments"
        params: list[Any] = []
        if name:
            query += " WHERE name = ?"
            params.append(name)
        query += " ORDER BY start_time DESC"
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.execute(query, params)
            return [dict(row) for row in cur.fetchall()]

    def _get_experiment_id(self, run_id: str) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute("SELECT id FROM experiments WHERE run_id = ?", (run_id,))
            row = cur.fetchone()
            if not row:
                raise ValueError(f"Run {run_id} not found")
            return int(row[0])


# Global registry instance
registry = ExperimentRegistry()
