
from liftlens.report.builder import ReportBuilder


def test_report_builder():
    builder = ReportBuilder()
    builder.add_executive_summary(
        key_findings=["Revenue up 8%", "No SRM"],
        recommendation="Launch"
    )
    builder.add_methods({"n_total": 2000})
    builder.add_results(
        metrics=[{"name": "revenue", "value": 0.08, "p_value": 0.001}],
        plots=[{"data": [], "layout": {}}]
    )
    builder.add_diagnostics(
        srm_result={"is_srm": False},
        balance_result={"balanced": True},
        normality_result={"normal": True}
    )

    html = builder.render("html")
    assert "Revenue up 8%" in html
    assert "Launch" in html
    assert "No SRM" in html
    assert "2000" in html


