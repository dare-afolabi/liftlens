import functools
import time
from collections.abc import Callable
from typing import Any

from loguru import logger


def timer(func: Callable[..., Any]) -> Callable[..., Any]:
    """Log execution time."""

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.debug(f"{func.__name__} executed in {elapsed:.3f}s")
        return result

    return wrapper


def retry(
    max_attempts: int = 3, delay: float = 1.0
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Exponential backoff retry."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            attempt = 0
            while attempt < max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    if attempt == max_attempts:
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise
                    wait = delay * (2 ** (attempt - 1))
                    logger.warning(
                        f"Retry {attempt}/{max_attempts} for {func.__name__} in {wait}s: {e}"
                    )
                    time.sleep(wait)
            return None

        return wrapper

    return decorator


def cache(func: Callable[..., Any]) -> Callable[..., Any]:
    """Simple in-memory cache."""
    cache_dict: dict[tuple[Any, Any], Any] = {}

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        key = (args, frozenset(kwargs.items()))
        if key in cache_dict:
            logger.debug(f"Cache hit: {func.__name__}")
            return cache_dict[key]
        result = func(*args, **kwargs)
        cache_dict[key] = result
        return result

    return wrapper
