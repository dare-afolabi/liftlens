
import os
import random
import tempfile
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

import numpy as np
from loguru import logger


class Session:
    """Global session context for reproducibility and temp file management."""

    def __init__(self, seed: int = 42, temp_dir: Path | None = None):
        self.seed = seed
        self.temp_dir = temp_dir or Path(tempfile.mkdtemp(prefix="liftlens_"))
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self._set_seeds()
        logger.debug(f"Session initialized with seed={seed}, temp_dir={self.temp_dir}")

    def _set_seeds(self) -> None:
        np.random.seed(self.seed)
        random.seed(self.seed)
        os.environ["PYTHONHASHSEED"] = str(self.seed)

    @contextmanager
    def temp_path(self, suffix: str = "") -> Generator[Path, None, None]:
        """Yield a temporary file path that is automatically cleaned up."""
        with tempfile.NamedTemporaryFile(dir=self.temp_dir, suffix=suffix, delete=False) as f:
            path = Path(f.name)
        try:
            yield path
        finally:
            if path.exists():
                path.unlink()

    def cleanup(self) -> None:
        """Remove all temporary files."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir, ignore_errors=True)
            logger.debug(f"Cleaned up temp directory: {self.temp_dir}")


# Global session instance
session = Session()


