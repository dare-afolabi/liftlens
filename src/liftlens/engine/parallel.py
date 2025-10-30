from collections.abc import Callable
from typing import Any, cast

from loguru import logger

from ..config.settings import settings


def parallel_apply(
    func: Callable[[Any], Any],
    items: list[Any],
    backend: str | None = None,
    **kwargs: Any,
) -> list[Any]:
    """
    Apply function in parallel using configured backend.
    Backends: joblib (default), dask, ray
    """
    backend = backend or settings.parallel_backend
    logger.debug(f"Parallel apply using {backend} on {len(items)} items")

    if backend == "joblib":
        from joblib import Parallel, delayed

        return cast(
            list[Any],
            Parallel(n_jobs=-1, **kwargs)(delayed(func)(item) for item in items),
        )

    elif backend == "dask":
        import dask

        delayed_items = [dask.delayed(func)(item) for item in items]
        return cast(
            list[Any], dask.compute(*delayed_items, scheduler="threads", **kwargs)
        )

    elif backend == "ray":
        import ray

        if not ray.is_initialized():
            ray.init(ignore_reinit_error=True)
        ray_funcs = [ray.remote(func).remote(item) for item in items]
        return cast(list[Any], ray.get(ray_funcs))

    else:
        raise ValueError(f"Unsupported backend: {backend}")
