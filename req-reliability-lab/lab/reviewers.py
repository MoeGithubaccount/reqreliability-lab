"""
reviewers.py — Requirement reviewer implementations.

Each reviewer takes a requirement string and returns a list of issues found.
The lab measures how well each reviewer catches injected defects.

Reviewer interface contract:
    fn(requirement_text: str) -> list[dict]
    Each dict: {"rule": str, "description": str, "severity": str}

Starting with a rule-based reviewer as the baseline.
LLM reviewer will be added in the 7-14 day upgrade.
"""

import re


# ──────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────

WEAK_MODALS = ["should", "may", "might", "could", "would", "can"]

VAGUE_TERMS = [
    "quickly", "fast", "slow", "appropriately", "adequately", "promptly",
    "sufficient", "sufficient", "reasonable", "as needed", "user-friendly",
    "easy", "flexible", "robust", "reliable", "good", "appropriate",
    "effective", "efficient", "simple", "better", "optimal", "acceptable",
    "minimal", "maximum performance", "high quality", "state of the art",
    "etc", "and/or",
]

TBD_MARKERS = ["tbd", "tba", "[tbd]", "[tba]", "to be determined", "to be announced"]

# Regex for measurable values (numbers + units)
MEASURABLE_VALUE_PATTERN = re.compile(
    r'\d+(?:\.\d+)?\s*'
    r'(?:milliseconds?|ms|seconds?|Hz|hours?|kPa|percent|%|km|m\b|kg|N\b|°)',
    re.IGNORECASE
)


# ──────────────────────────────────────────────
# Rule-Based Reviewer (Baseline)
# ──────────────────────────────────────────────

def rule_based_reviewer(requirement_text: str) -> list:
    """
    Baseline rule-based requirement reviewer.

    Applies deterministic checks based on common requirements quality rules
    drawn from NASA guidelines and INCOSE standards.

    Returns a list of issue dicts, empty list if no issues found.
    """
    issues = []
    text_lower = requirement_text.lower().strip()

    # ── Rule 1: No 'shall' present ──
    if "shall" not in text_lower:
        issues.append({
            "rule": "MISSING_SHALL",
            "description": "Requirement does not use 'shall'. Mandatory requirements must use 'shall'.",
            "severity": "HIGH"
        })

    # ── Rule 2: Weak modal verb ──
    for modal in WEAK_MODALS:
        if re.search(r'\b' + modal + r'\b', text_lower):
            issues.append({
                "rule": "WEAK_MODAL",
                "description": f"Found weak modal verb: '{modal}'. "
                               f"Use 'shall' for mandatory requirements. "
                               f"'Should' implies discretion, not obligation.",
                "severity": "HIGH"
            })
            break  # Report once per requirement

    # ── Rule 3: Vague or unmeasurable terms ──
    found_vague = []
    for term in VAGUE_TERMS:
        if re.search(r'\b' + re.escape(term) + r'\b', text_lower):
            found_vague.append(term)
    if found_vague:
        issues.append({
            "rule": "VAGUE_TERM",
            "description": f"Found vague term(s): {found_vague}. "
                           f"Replace with specific, measurable criteria that can be verified.",
            "severity": "HIGH"
        })

    # ── Rule 4: TBD / placeholder values ──
    for marker in TBD_MARKERS:
        if marker in text_lower:
            issues.append({
                "rule": "TBD_PLACEHOLDER",
                "description": f"Requirement contains unresolved placeholder '{marker}'. "
                               f"All values must be defined before requirements are baselined.",
                "severity": "CRITICAL"
            })
            break

    # ── Rule 5: Passive voice indicator ──
    passive_indicators = [
        r'^it shall\b',
        r'^it should\b',
        r'^it is required that\b',
        r'shall be ensured',
        r'shall be performed',
    ]
    for pattern in passive_indicators:
        if re.search(pattern, text_lower):
            issues.append({
                "rule": "PASSIVE_VOICE",
                "description": "Requirement appears to use passive voice. "
                               "Specify a clear system actor (e.g., 'The flight control system shall...').",
                "severity": "MEDIUM"
            })
            break

    # ── Rule 6: No measurable value ──
    if not MEASURABLE_VALUE_PATTERN.search(requirement_text):
        # Only flag if this looks like a performance requirement
        performance_keywords = ["respond", "update", "store", "activate", "extend", "retract",
                                "log", "issue", "alert", "maintain", "transmit", "process"]
        if any(kw in text_lower for kw in performance_keywords):
            issues.append({
                "rule": "NO_MEASURABLE_VALUE",
                "description": "Performance requirement contains no measurable values (numbers + units). "
                               "Requirements must be verifiable with specific thresholds.",
                "severity": "MEDIUM"
            })

    return issues


# ──────────────────────────────────────────────
# Reviewer registry
# ──────────────────────────────────────────────

AVAILABLE_REVIEWERS = {
    "rule_based_v1": {
        "fn": rule_based_reviewer,
        "name": "RuleBasedReviewer v1",
        "description": "Deterministic checks for common requirement defects. No LLM. Fast and repeatable.",
        "requires_api": False,
    }
    # LLM reviewer will be added in week 2 upgrade:
    # "gpt4_reviewer": { "fn": gpt4_reviewer, ... }
}
