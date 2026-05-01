#!/usr/bin/env python3
"""
Requirements Reliability Lab — Main Runner

Usage:
    python run_lab.py                    # run with default rule-based reviewer
    python run_lab.py --save             # save full JSON report to reports/

What this does:
  1. Loads 10 clean aerospace-style requirements
  2. Applies 5 defect injection types to each (where applicable)
  3. Runs the rule-based reviewer on every mutated requirement
  4. Scores detection rate by defect type and overall
  5. Prints a structured experiment summary

This is the baseline. The rule-based reviewer gives you
the floor — how much a simple deterministic checker can catch.
The next step (week 2) is to add an LLM reviewer and compare.
"""

import json
import os
import sys
from datetime import datetime

from data.requirements import REQUIREMENTS
from lab.reviewers import rule_based_reviewer
from lab.evaluate import run_experiment


# ── Terminal formatting helpers ──────────────────────────────

RESET  = "\033[0m"
BOLD   = "\033[1m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
DIM    = "\033[2m"


def sep(char="─", width=62):
    print(char * width)


def color_rate(rate: float) -> str:
    if rate >= 80:
        return f"{GREEN}{rate}%{RESET}"
    elif rate >= 50:
        return f"{YELLOW}{rate}%{RESET}"
    else:
        return f"{RED}{rate}%{RESET}"


def progress_bar(rate: float, width: int = 20) -> str:
    filled = int(rate / 100 * width)
    empty = width - filled
    bar = "█" * filled + "░" * empty
    return bar


# ── Main print functions ─────────────────────────────────────

def print_header():
    sep("═")
    print(f"{BOLD}  REQUIREMENTS RELIABILITY LAB{RESET}")
    print(f"  Experiment: Rule-Based Reviewer Baseline")
    print(f"  {DIM}A mutation testing bench for requirement quality evaluation{RESET}")
    sep("═")
    print()


def print_summary(results: dict):
    meta = results["meta"]
    summary = results["summary"]

    print(f"{BOLD}EXPERIMENT PARAMETERS{RESET}")
    print(f"  Reviewer        : {meta['reviewer']}")
    print(f"  Requirements    : {meta['total_requirements']}")
    print(f"  Defect types    : {meta['mutators_applied']}")
    print(f"  Run time        : {meta['timestamp']}")
    print()

    sep()
    print(f"{BOLD}OVERALL RESULTS{RESET}")
    sep()
    print(f"  Total tests run  : {summary['total_tests']}")
    print(f"  Defects caught   : {GREEN}{summary['true_positives']}{RESET}")
    print(f"  Defects missed   : {RED}{summary['false_negatives']}{RESET}")
    print()

    rate = summary["detection_rate_pct"]
    bar = progress_bar(rate)
    print(f"  Overall detection rate : [{bar}] {color_rate(rate)}")
    print()


def print_by_defect_type(results: dict):
    sep()
    print(f"{BOLD}DETECTION RATE BY DEFECT TYPE{RESET}")
    sep()

    type_labels = {
        "WEAK_MODAL":        "Weak modal verb",
        "VAGUE_TIMING":      "Vague timing / no measure",
        "PASSIVE_VOICE":     "Passive voice / no actor",
        "MISSING_CONDITION": "Missing condition / trigger",
        "TBD_PLACEHOLDER":   "TBD placeholder",
    }

    for defect_type, stats in results["by_defect_type"].items():
        label = type_labels.get(defect_type, defect_type)
        rate = stats["detection_rate_pct"]
        bar = progress_bar(rate, width=16)
        caught = stats["caught"]
        total = stats["total"]
        expected = stats["expected_rules"]

        print(f"\n  {BOLD}{label}{RESET}")
        print(f"  [{bar}] {color_rate(rate)}  ({caught}/{total})")
        if not expected:
            print(f"  {DIM}↳ No rule covers this defect type — baseline blind spot{RESET}")
        else:
            print(f"  {DIM}↳ Expected rules: {expected}{RESET}")
    print()


def print_missed_defects(results: dict):
    missed = [t for t in results["test_log"] if t["outcome"] == "MISSED"]
    if not missed:
        print(f"{GREEN}No missed defects. All injected issues were caught.{RESET}")
        return

    sep()
    print(f"{BOLD}SAMPLE MISSED DEFECTS  (first 3 of {len(missed)}){RESET}")
    sep()
    print(f"{DIM}These are the injected issues the reviewer failed to flag.{RESET}")
    print(f"{DIM}Each is an opportunity to improve the reviewer.{RESET}\n")

    for item in missed[:3]:
        print(f"  {CYAN}REQ {item['req_id']}{RESET} — {item['defect_type']}")
        print(f"  Defect: {item['defect_description']}")
        orig = item['original_text'][:72]
        mutd = item['mutated_text'][:72]
        print(f"  {DIM}Original : {orig}...{RESET}")
        print(f"  {YELLOW}Mutated  : {mutd}...{RESET}")
        triggered = item["rules_triggered"] or ["(none)"]
        print(f"  Rules triggered: {triggered}")
        print()


def print_next_steps():
    sep()
    print(f"{BOLD}WHAT THIS TELLS YOU{RESET}")
    sep()
    print()
    print("  This is your baseline. The rule-based reviewer is fast,")
    print("  deterministic, and catches obvious defects reliably.")
    print()
    print("  The gaps above — especially MISSING_CONDITION — show")
    print("  where a rule-based approach hits its limit.")
    print()
    print(f"  {BOLD}Next experiment:{RESET} Add an LLM reviewer.")
    print("  Compare its detection rate against this baseline.")
    print("  That's the interesting result to talk about.")
    print()
    sep("═")
    print()


# ── Save report ──────────────────────────────────────────────

def save_report(results: dict) -> str:
    os.makedirs("reports", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = f"reports/experiment_{ts}.json"
    with open(path, "w") as f:
        json.dump(results, f, indent=2)
    return path


# ── Entry point ──────────────────────────────────────────────

def main():
    save_flag = "--save" in sys.argv

    print_header()

    print(f"  Running experiment...\n")

    results = run_experiment(
        requirements=REQUIREMENTS,
        reviewer_fn=rule_based_reviewer,
        reviewer_name="RuleBasedReviewer_v1"
    )

    print_summary(results)
    print_by_defect_type(results)
    print_missed_defects(results)
    print_next_steps()

    if save_flag:
        path = save_report(results)
        print(f"  Full JSON report saved: {path}\n")
    else:
        print(f"  {DIM}Tip: run with --save to write full JSON report to reports/{RESET}\n")


if __name__ == "__main__":
    main()
