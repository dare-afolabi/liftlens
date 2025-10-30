
from pathlib import Path

import pandas as pd
import streamlit as st

from ..core.registry import registry

st.set_page_config(page_title="A/B Test Dashboard", layout="wide")

st.title("A/B Test Framework Dashboard")

# List runs
runs = registry.list_runs()
if not runs:
    st.info("No experiments yet. Run via CLI or API.")
    st.stop()

selected = st.selectbox("Select Experiment", options=runs, format_func=lambda r: f"{r['name']} ({r['run_id']})")
run = registry.get_run(selected["run_id"])
if run is None:
    st.error("Selected run not found")
    st.stop()
assert run is not None

col1, col2 = st.columns(2)
with col1:
    st.metric("Status", run["status"].title())
    st.metric("Start Time", run["start_time"][:19])
with col2:
    st.metric("Duration", f"{(pd.Timestamp(run['end_time']) - pd.Timestamp(run['start_time'])).seconds}s" if run["end_time"] else "Running")

# Results
if run.get("results_json"):
    results = pd.read_json(run["results_json"])["metrics"]
    st.subheader("Key Metrics")
    st.dataframe(results)

# Report
report_path = Path("output") / run["run_id"] / "report.html"
if report_path.exists():
    st.components.v1.html(report_path.read_text(), height=800, scrolling=True)


