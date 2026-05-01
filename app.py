import json
import subprocess
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="ReqReliability Lab", layout="wide")

st.title("ReqReliability Lab")
st.subheader("Stress-testing automated requirements reviewers")

st.write(
    """
    This prototype tests whether an automated reviewer can catch known defects
    in synthetic safety-critical-style requirements.

    It starts with clean requirements, injects defects like vague timing,
    missing conditions, weak wording, or TBD placeholders, then checks whether
    the reviewer catches them.
    """
)

st.warning(
    "Prototype only. Uses synthetic requirements. Not a certification tool, compliance tool, or production safety system."
)

if st.button("Run baseline experiment"):
    with st.spinner("Running experiment..."):
        result = subprocess.run(
            ["python", "run_lab.py", "--save"],
            capture_output=True,
            text=True
        )

    if result.returncode != 0:
        st.error("Something went wrong.")
        st.code(result.stderr)
        st.stop()

    reports = sorted(Path("reports").glob("experiment_*.json"), reverse=True)
    if not reports:
        st.error("No report file found.")
        st.stop()

    latest_report = reports[0]
    data = json.loads(latest_report.read_text())

    st.success("Experiment completed.")

    summary = data.get("summary", {})
    by_defect = data.get("by_defect_type", {})
    test_log = data.get("test_log", [])

    total = summary.get("total_tests", 0)
    caught = summary.get("true_positives", 0)
    missed = summary.get("false_negatives", 0)
    detection_rate = summary.get("detection_rate_pct", 0)

    st.subheader("Baseline Results")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total tests", total)
    col2.metric("Caught", caught)
    col3.metric("Missed", missed)
    col4.metric("Detection rate", f"{detection_rate}%")

    st.subheader("Detection Rate by Defect Type")

    defect_rows = []
    for defect, values in by_defect.items():
        defect_rows.append(
            {
                "Defect type": defect,
                "Total": values.get("total", 0),
                "Caught": values.get("caught", 0),
                "Missed": values.get("missed", 0),
                "Detection rate": f"{values.get('detection_rate_pct', 0)}%",
            }
        )

    defect_df = pd.DataFrame(defect_rows)
    st.dataframe(defect_df, use_container_width=True)

    st.subheader("What the Baseline Missed")

    missed_items = [item for item in test_log if item.get("outcome") == "MISSED"]

    if missed_items:
        st.write(
            """
            These are the cases where the rule-based reviewer did not catch the injected defect.
            This is useful because it shows where the baseline approach needs improvement.
            """
        )

        missed_rows = []
        for item in missed_items:
            missed_rows.append(
                {
                    "Requirement": item.get("req_id"),
                    "Defect type": item.get("defect_type"),
                    "Mutated requirement": item.get("mutated_text"),
                    "Rules triggered": ", ".join(item.get("rules_triggered", [])),
                }
            )

        st.dataframe(pd.DataFrame(missed_rows), use_container_width=True)
    else:
        st.write("No missed defects in this run.")

    st.subheader("Plain-English Takeaway")

    st.info(
        """
        The rule-based reviewer catches obvious defects very well, especially weak wording,
        vague timing, passive voice, and TBD placeholders. But it misses context-based issues
        like missing conditions or triggers.

        That gives the next experiment a clear purpose: add an LLM reviewer and compare
        whether it catches the cases the rules miss.
        """
    )

    with st.expander("Show full JSON report"):
        st.json(data)

    st.download_button(
        label="Download JSON report",
        data=latest_report.read_text(),
        file_name=latest_report.name,
        mime="application/json",
    )
