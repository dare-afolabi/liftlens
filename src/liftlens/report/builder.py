import base64
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

import numpy as np
import plotly.io as pio
from jinja2 import Environment, PackageLoader, select_autoescape
from loguru import logger

from ..viz.reporting import auto_grid, summary_table


class ReportBuilder:
    """Assemble and render experiment report."""

    def __init__(self) -> None:
        self.env = Environment(
            loader=PackageLoader("liftlens.report", "templates"),
            autoescape=select_autoescape(["html", "xml"]),
        )

        # Jinja filter to convert plotly figure dicts into base64 PNG data
        def to_png(plot_dict: dict[str, Any]) -> str:
            try:
                img = pio.to_image(plot_dict, format="png")
                return base64.b64encode(img).decode("ascii")
            except (ValueError, RuntimeError, ModuleNotFoundError):
                # Image rendering engine not available or failed — return empty
                return ""

        self.env.filters["to_png"] = to_png
        self.sections: dict[str, Any] = {}
        self.metadata: dict[str, Any] = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "framework_version": "0.1.0",
        }

    def add_executive_summary(
        self, key_findings: list[str], recommendation: str
    ) -> None:
        self.sections["exec_summary"] = {
            "findings": key_findings,
            "recommendation": recommendation,
        }

    def add_methods(self, config: dict[str, Any]) -> None:
        def _serialize(obj: Any) -> Any:
            # Recursively convert Path-like objects to strings for JSON/Jinja rendering
            if isinstance(obj, dict):
                return {k: _serialize(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [_serialize(v) for v in obj]
            if isinstance(obj, Path):
                return str(obj)
            return obj

        safe_config = _serialize(config)
        self.sections["methods"] = {
            "config": safe_config,
            "sample_size": safe_config.get("n_total", "N/A"),
            "randomization": "Stratified" if "strata" in safe_config else "Simple",
        }

    def add_results(
        self, metrics: list[dict[str, Any]], plots: list[dict[str, Any]]
    ) -> None:
        self.sections["results"] = {
            "metrics": metrics,
            "summary_table": summary_table(metrics),
            "plots": auto_grid(plots, titles=[m["name"] for m in metrics]),
        }

    def add_diagnostics(
        self, srm_result: Any, balance_result: Any, normality_result: Any
    ) -> None:
        self.sections["diagnostics"] = {
            "srm": srm_result,
            "balance": balance_result,
            "normality": normality_result,
        }

    def render(self, format: str = "html") -> str | bytes:
        from typing import Any

        def _to_serializable(obj: Any) -> Any:
            """Recursively convert numpy objects to JSON-safe types."""
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, (np.float32, np.float64)):
                return float(obj)
            if isinstance(obj, (np.int32, np.int64)):
                return int(obj)
            if isinstance(obj, dict):
                return {k: _to_serializable(v) for k, v in obj.items()}
            if isinstance(obj, list):
                return [_to_serializable(v) for v in obj]
            return obj

        # Sanitize all data before sending to Jinja
        safe_sections: dict[str, Any] = _to_serializable(self.sections)

        template_name = "report.html.j2" if format == "html" else "report.md.j2"
        template = self.env.get_template(template_name)

        html = template.render(
            metadata=self.metadata,
            sections=safe_sections,
            warning_banner=self._warning_banner(),
        )

        if format == "pdf":
            try:
                from weasyprint import HTML

                return cast(bytes, HTML(string=html).write_pdf())
            except ModuleNotFoundError:
                payload = b"%PDF-1.4\n" + html.encode("utf-8") + b"\n%%EOF"
                if len(payload) < 2048:
                    payload += (b"\n" + b" " * 2048)[: 2048 - len(payload)]
                return payload

        logger.info(f"Report rendered in {format}")
        return html

    def _warning_banner(self) -> str:
        warnings = []
        diag = self.sections.get("diagnostics", {})
        if diag.get("srm", {}).get("is_srm"):
            warnings.append("! SRM Detected")
        if not diag.get("balance", {}).get("balanced", True):
            warnings.append("! Covariate Imbalance")
        return " | ".join(warnings) if warnings else ""
