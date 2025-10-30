#!/usr/bin/env python3
"""
Migrate old registry format to current SQLite schema.
"""
import json
import sqlite3
from pathlib import Path

from loguru import logger


def migrate(old_path: Path, new_path: Path):
    if not old_path.exists():
        logger.error(f"Old registry not found: {old_path}")
        return

    conn = sqlite3.connect(new_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS experiments (
            id INTEGER PRIMARY KEY,
            run_id TEXT UNIQUE,
            name TEXT,
            config_json TEXT,
            results_json TEXT
        )
    """)

    with open(old_path) as f:
        old_data = json.load(f)

    for run in old_data.get("runs", []):
        conn.execute("""
            INSERT OR REPLACE INTO experiments
            (run_id, name, config_json, results_json)
            VALUES (?, ?, ?, ?)
        """, (run["run_id"], run["name"], json.dumps(run["config"]), json.dumps(run["results"])))

    conn.commit()
    logger.success(f"Migrated {len(old_data['runs'])} runs to {new_path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--old", type=Path, default=".liftlens_registry.json")
    parser.add_argument("--new", type=Path, default=".liftlens_registry.sqlite")
    args = parser.parse_args()
    migrate(args.old, args.new)
