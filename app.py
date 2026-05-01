import json
import subprocess
from pathlib import Path

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

    if result.returncode == 0:
        st.success("Experiment completed.")
        st.code(result.stdout)

        reports = sorted(Path("reports").glob("experiment_*.json"), reverse=True)
        if reports:
            latest_report = reports[0]
            st.write(f"Latest report: `{latest_report}`")

            data = json.loads(latest_report.read_text())

            st.subheader("Report Preview")

            if isinstance(data, list):
                caught = sum(1 for item in data if item.get("outcome") == "CAUGHT")
                missed = sum(1 for item in data if item.get("outcome") == "MISSED")
                total = len(data)

                col1, col2, col3 = st.columns(3)
                col1.metric("Total tests", total)
                col2.metric("Caught", caught)
                col3.metric("Missed", missed)

                st.dataframe(data, use_container_width=True)

            else:
                st.json(data)

            st.download_button(
                label="Download latest JSON report",
                data=latest_report.read_text(),
                file_name=latest_report.name,
                mime="application/json"
            )
    else:
        st.error("Something went wrong.")
        st.code(result.stderr)
