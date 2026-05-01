"""
evaluate.py — Experiment evaluation engine.

Orchestrates the full experiment loop:
  1. Take clean baseline requirements
  2. Apply each mutator to generate defect-injected variants
  3. Run each variant through a reviewer
  4. Compare reviewer findings against known injected defects
  5. Score performance by defect type and overall

This is the heart of the Requirements Reliability Lab.
"""

import copy
from datetime import datetime
from lab.mutators import ALL_MUTATORS

# ──────────────────────────────────────────────
# Defect → Rule mapping
# Maps each injected defect type to the rule codes
# that a good reviewer SHOULD trigger.
# ──────────────────────────────────────────────

DEFECT_TO_EXPECTED_RULES = {
    "WEAK_MODAL":        ["WEAK_MODAL", "MISSING_SHALL"],
    "VAGUE_TIMING":      ["VAGUE_TERM", "NO_MEASURABLE_VALUE"],
    "PASSIVE_VOICE":     ["PASSIVE_VOICE"],
    "MISSING_CONDITION": [],  # Rule-based baseline expected to miss this
    "TBD_PLACEHOLDER":   ["TBD_PLACEHOLDER"],
}


def run_experiment(requirements: list, reviewer_fn, reviewer_name: str = "Reviewer") -> dict:
    """
    Run a full experiment: mutate all requirements, review each mutation,
    evaluate whether the reviewer caught the injected defect.

    Args:
        requirements: list of clean requirement dicts
        reviewer_fn:  callable(text: str) -> list[issue dicts]
        reviewer_name: label for this reviewer in the output

    Returns:
        results dict with full detail and aggregate metrics
    """
    results = {
        "meta": {
            "reviewer": reviewer_name,
            "timestamp": datetime.now().isoformat(),
            "total_requirements": len(requirements),
            "mutators_applied": len(ALL_MUTATORS),
        },
        "summary": {
            "total_tests": 0,
            "true_positives": 0,
            "false_negatives": 0,
            "detection_rate_pct": 0.0,
        },
        "by_defect_type": {},
        "test_log": [],
    }

    for req in requirements:
        for mutator_fn in ALL_MUTATORS:

            # Apply mutation
            mutant = mutator_fn(copy.deepcopy(req))
            if mutant is None:
                continue  # Mutation not applicable to this requirement

            defect_type = mutant["defect_type"]

            # Run reviewer on the mutated text
            issues_found = reviewer_fn(mutant["text"])
            found_rule_codes = {issue["rule"] for issue in issues_found}

            # Determine if reviewer caught the injected defect
            expected_rules = DEFECT_TO_EXPECTED_RULES.get(defect_type, [])
            caught = bool(expected_rules) and any(
                rule in found_rule_codes for rule in expected_rules
            )
            # Special case: MISSING_CONDITION has no expected rule,
            # so we always count it as a miss (demonstrating the baseline limit)

            outcome = "CAUGHT" if caught else "MISSED"

            # Update totals
            results["summary"]["total_tests"] += 1
            if caught:
                results["summary"]["true_positives"] += 1
            else:
                results["summary"]["false_negatives"] += 1

            # Update per-defect-type breakdown
            if defect_type not in results["by_defect_type"]:
                results["by_defect_type"][defect_type] = {
                    "total": 0, "caught": 0, "missed": 0,
                    "detection_rate_pct": 0.0,
                    "expected_rules": expected_rules,
                }
            dt = results["by_defect_type"][defect_type]
            dt["total"] += 1
            if caught:
                dt["caught"] += 1
            else:
                dt["missed"] += 1

            # Log full test detail
            results["test_log"].append({
                "req_id": req["id"],
                "defect_type": defect_type,
                "defect_description": mutant["defect_description"],
                "original_text": req["text"],
                "mutated_text": mutant["text"],
                "expected_rules": expected_rules,
                "rules_triggered": list(found_rule_codes),
                "issues_found": issues_found,
                "outcome": outcome,
            })

    # ── Compute final rates ──
    total = results["summary"]["total_tests"]
    if total > 0:
        tp = results["summary"]["true_positives"]
        results["summary"]["detection_rate_pct"] = round(tp / total * 100, 1)

    for defect_type, stats in results["by_defect_type"].items():
        if stats["total"] > 0:
            stats["detection_rate_pct"] = round(stats["caught"] / stats["total"] * 100, 1)

    return results
