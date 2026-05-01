import json
import re
import subprocess
from pathlib import Path

import pandas as pd
import streamlit as st

st.set_page_config(page_title="ReqReliability Lab", layout="wide")

PERFORMANCE_WORDS = [
    "respond", "update", "process", "alert", "activate", "store", "transmit",
    "notify", "disengage", "detect", "display", "log", "maintain", "issue"
]

VAGUE_TERMS = [
    "quickly", "fast", "soon", "timely", "efficient", "efficiently",
    "appropriate", "appropriately", "adequate", "adequately", "sufficient",
    "sufficiently", "robust", "reliable", "user-friendly", "easy to use",
    "as needed", "as appropriate", "normal operation", "real time", "real-time"
]

WEAK_MODALS = ["should", "may", "could", "might", "will"]

CONDITION_WORDS = ["when", "upon", "after", "before", "during", "under", "if", "while"]


def has_measurable_value(text: str) -> bool:
    pattern = r"\b\d+(\.\d+)?\s*(ms|millisecond|milliseconds|second|seconds|sec|minute|minutes|min|hour|hours|hz|khz|mhz|percent|%|psi|kpa|mb|gb|days?)\b"
    return bool(re.search(pattern, text.lower()))


def review_single_requirement(text: str):
    findings = []
    t = text.strip()
    lower = t.lower()

    if not t:
        return findings

    if "tbd" in lower or "[tbd]" in lower or "to be determined" in lower:
        findings.append({
            "Issue": "TBD placeholder",
            "Severity": "Critical",
            "Why it matters": "A requirement with an unresolved placeholder cannot be verified or tested.",
            "Suggestion": "Replace TBD with a defined value, threshold, or condition."
        })

    if "shall" not in lower:
        findings.append({
            "Issue": "Missing 'shall'",
            "Severity": "High",
            "Why it matters": "Mandatory requirements usually need clear obligation language.",
            "Suggestion": "Use 'shall' when the requirement is mandatory."
        })

    for word in WEAK_MODALS:
        if re.search(rf"\b{re.escape(word)}\b", lower):
            findings.append({
                "Issue": f"Weak modal verb: '{word}'",
                "Severity": "High" if word == "should" else "Medium",
                "Why it matters": f"'{word}' can make the requirement sound optional or unclear.",
                "Suggestion": "Use 'shall' for mandatory behavior, or clarify if the statement is only a goal."
            })

    found_vague = [term for term in VAGUE_TERMS if term in lower]
    if found_vague:
        findings.append({
            "Issue": "Vague or unverifiable wording",
            "Severity": "High",
            "Why it matters": f"Terms like {', '.join(found_vague)} are hard to test without measurable criteria.",
            "Suggestion": "Replace vague wording with a measurable threshold, condition, or acceptance criterion."
        })

    if any(word in lower for word in PERFORMANCE_WORDS) and not has_measurable_value(t):
        findings.append({
            "Issue": "Missing measurable value",
            "Severity": "Medium",
            "Why it matters": "Performance-related requirements should usually include a measurable pass/fail threshold.",
            "Suggestion": "Add a specific value such as time, frequency, percentage, capacity, or threshold."
        })

    if re.search(r"\bshall be\b|\bit shall be\b|\bmust be\b", lower):
        findings.append({
            "Issue": "Possible passive voice / unclear actor",
            "Severity": "Medium",
            "Why it matters": "Passive wording can hide which system or component is responsible.",
            "Suggestion": "Name the responsible system or component directly."
        })

    if any(word in lower for word in PERFORMANCE_WORDS) and not any(word in lower for word in CONDITION_WORDS):
        findings.append({
            "Issue": "Possible missing condition or trigger",
            "Severity": "Medium",
            "Why it matters": "The requirement may describe an action without saying when or under what condition it applies.",
            "Suggestion": "Add a trigger such as 'when...', 'upon...', 'during...', or 'under...'."
        })

    return findings


def suggested_rewrite(text: str):
    return (
        "Suggested structure:\n\n"
        "The [system/component] shall [specific action] within [measurable threshold] "
        "when/upon/during [defined condition].\n\n"
        "Example:\n"
        "The flight display module shall update pilot input status within 200 milliseconds "
        "upon input activation."
    )


st.title("ReqReliability Lab")
st.subheader("Stress-testing automated requirements reviewers")

st.write(
    """
    This prototype tests whether an automated reviewer can catch known defects
    in synthetic technical requirements, workflow rules, and acceptance criteria.

    It can run a built-in baseline experiment, or you can paste your own requirement
    to see what the reviewer flags.
    """
)

st.warning(
    "Prototype only. Uses synthetic examples. Do not enter sensitive, proprietary, regulated, employer, student, patient, customer, or confidential data."
)

tab1, tab2, tab3 = st.tabs(["Run Demo Experiment", "Try Your Own Requirement", "About"])

with tab1:
    st.header("Run the baseline experiment")

    st.write(
        """
        This runs the built-in experiment: clean synthetic requirements are mutated with known defects,
        then the rule-based reviewer tries to catch them.
        """
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

        st.dataframe(pd.DataFrame(defect_rows), use_container_width=True)

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

with tab2:
    st.header("Try your own requirement")

    st.write(
        """
        Paste a requirement, acceptance criterion, support workflow, project task, or technical statement below.
        The reviewer will flag wording that may be hard to test, verify, or assign clearly.
        """
    )

    example = "The system should respond quickly when the user submits a request."

    user_req = st.text_area(
        "Requirement to review",
        value=example,
        height=120
    )

    if st.button("Review this requirement"):
        findings = review_single_requirement(user_req)

        if findings:
            st.subheader("Issues Found")
            st.dataframe(pd.DataFrame(findings), use_container_width=True)
        else:
            st.success("No issues found by the current rule set.")

        st.subheader("Suggested Rewrite Pattern")
        st.code(suggested_rewrite(user_req))

        st.info(
            """
            This is a rule-based review, not a final engineering judgment.
            Treat it as a first-pass check to make vague or untestable wording easier to notice.
            """
        )

with tab3:
    st.header("About this project")

    st.write(
        """
        ReqReliability Lab is a small experiment harness for testing requirements reviewers.

        The key idea is simple: before trusting an automated reviewer, test what it catches
        and what it misses.

        The built-in demo creates known defects in synthetic technical requirements.
        The tool then measures whether the reviewer catches them.

        This is useful beyond aerospace-style examples. Product managers, QA testers,
        project managers, software teams, and AI teams can all use the same idea:
        if a requirement cannot be tested, it probably needs to be rewritten.
        """
    )

    st.write(
        """
        Current version:
        - Rule-based reviewer
        - Synthetic requirements
        - Built-in mutation experiment
        - Single-requirement review mode

        Next version:
        - Optional LLM reviewer
        - CSV upload
        - Better reports
        - Prompt/model comparison
        """
    )
