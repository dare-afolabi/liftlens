from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class LiftlensBaseModel(BaseModel):
    """Small BaseModel subclass to provide a v2-compatible json wrapper.

    Tests (and some callers) use the old ``.json(indent=...)`` API which in
    Pydantic v2 routes indent into ``dumps_kwargs`` and raises. We provide a
    thin wrapper that forwards to ``model_dump_json`` so existing callers keep
    working without changing tests.
    """

    def json(self, *args: object, indent: int | None = None, **kwargs: object) -> str:
        return self.model_dump_json(indent=indent)


class DataSource(LiftlensBaseModel):
    type: Literal["csv", "parquet", "db", "delta"]
    path: Path | None = None
    table: str | None = None
    query: str | None = None

    @field_validator("path")
    def path_required_for_file(cls, v: Path | None, info: Any) -> Path | None:
        # info.data contains other fields on the model during validation
        values = info.data or {}
        if values.get("type") in ["csv", "parquet", "delta"] and not v:
            raise ValueError(f"path required for {values.get('type')}")
        return v


class MetricSpec(LiftlensBaseModel):
    name: str = Field(..., pattern=r"^[a-zA-Z0-9_]+$")
    type: Literal["primary", "robust", "composite"]
    func: str
    params: dict[str, Any] = Field(default_factory=dict)
    weight: float = 1.0


class TransformConfig(LiftlensBaseModel):
    winsorize: tuple[float, float] = (0.01, 0.01)
    cuped: bool = True
    log_transform: bool = False
    standardize: bool = False


class StatsConfig(LiftlensBaseModel):
    alpha: float = 0.05
    power: float = 0.8
    mde: float | None = None
    sequential: bool = False
    bootstrap_samples: int = 10_000
    permutation_tests: int = 5_000


class ReportConfig(LiftlensBaseModel):
    format: Literal["md", "html", "pdf"] = "html"
    interactive: bool = True
    include_diagnostics: bool = True


class ExperimentConfig(LiftlensBaseModel):
    name: str
    data: DataSource
    user_col: str = "user_id"
    baseline_col: str
    outcome_col: str
    group_col: str
    control_label: str = "control"
    treatment_label: str = "treatment"
    metrics: list[MetricSpec]
    transform: TransformConfig = TransformConfig()
    stats: StatsConfig = StatsConfig()
    report: ReportConfig = ReportConfig()
    tags: dict[str, str] = Field(default_factory=dict)

    @field_validator("metrics")
    def at_least_one_metric(cls, v: list["MetricSpec"]) -> list["MetricSpec"]:
        if not v:
            raise ValueError("At least one metric required")
        return v
