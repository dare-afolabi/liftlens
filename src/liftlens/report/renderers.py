from typing import Any, cast

from loguru import logger
from weasyprint import HTML


def render_markdown(md_content: str) -> str:
    """Convert Markdown to HTML."""
    try:
        import markdown  # type: ignore

        return cast(
            str, markdown.markdown(md_content, extensions=["tables", "fenced_code"])
        )
    except ImportError:
        logger.error("markdown package required")
        return md_content


def render_pdf(html_content: str, css_path: str | None = None) -> bytes:
    """Render HTML to PDF using WeasyPrint."""
    html = HTML(string=html_content)
    if css_path:
        html = HTML(string=html_content, base_url=css_path)
    pdf_bytes = html.write_pdf()
    logger.info("PDF generated")
    return cast(bytes, pdf_bytes)


def render_json(data: dict[str, Any]) -> str:
    """Serialize full report to JSON."""
    import json

    return json.dumps(data, indent=2, default=str)
