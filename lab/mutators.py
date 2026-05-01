"""
mutators.py — Defect injection module.

Each mutator function takes a clean requirement dict and returns
a mutated version with metadata about what was injected.
Returns None if the mutation cannot be applied to this requirement.

Defect types inspired by:
- NASA Systems Engineering Handbook (requirements checklist)
- INCOSE Guide to Writing Requirements
- Common issues found in DO-178C / ARP4754A development
"""

import re
import copy


# ──────────────────────────────────────────────
# DEFECT TYPE 1: Weak Modal Verb
# "shall" → "should" removes mandatory enforcement
# ──────────────────────────────────────────────

def inject_weak_modal(req: dict) -> dict | None:
    """
    Replace 'shall' with 'should'.
    This weakens a mandatory requirement into a recommendation,
    which is a common and expensive mistake in aerospace specs.
    """
    if "shall" not in req["text"]:
        return None

    mutated = copy.deepcopy(req)
    mutated["text"] = req["text"].replace("shall", "should", 1)
    mutated["defect_type"] = "WEAK_MODAL"
    mutated["defect_description"] = (
        "Changed 'shall' to 'should' — removes mandatory enforcement. "
        "In requirements engineering, 'shall' is mandatory; 'should' is optional."
    )
    mutated["original_text"] = req["text"]
    return mutated


# ──────────────────────────────────────────────
# DEFECT TYPE 2: Vague Timing / Measurable Value
# Replaces numeric thresholds with vague qualitative terms
# ──────────────────────────────────────────────

TIME_PATTERN = re.compile(
    r'\d+(?:\.\d+)?\s*'
    r'(?:milliseconds?|ms|seconds?|s\b|Hz|hours?|kPa|percent|%)',
    re.IGNORECASE
)


def inject_vague_timing(req: dict) -> dict | None:
    """
    Replace a specific measurable value with the vague term 'quickly'.
    Loss of measurability is one of the most common requirement defects.
    """
    match = TIME_PATTERN.search(req["text"])
    if not match:
        return None

    target = match.group(0)
    mutated = copy.deepcopy(req)
    mutated["text"] = req["text"].replace(target, "quickly", 1)
    mutated["defect_type"] = "VAGUE_TIMING"
    mutated["defect_description"] = (
        f"Replaced specific measurable value '{target.strip()}' with vague term 'quickly'. "
        "Vague timing makes requirements untestable."
    )
    mutated["original_text"] = req["text"]
    return mutated


# ──────────────────────────────────────────────
# DEFECT TYPE 3: Passive Voice / Hidden Actor
# Removes the system responsible for the action
# ──────────────────────────────────────────────

ACTOR_PATTERN = re.compile(
    r'^(The [\w\s]+?(?:system|display|unit|module|recorder|sensor))\s+shall\s+',
    re.IGNORECASE
)


def inject_passive_voice(req: dict) -> dict | None:
    """
    Remove the system actor, converting to passive voice.
    'The flight control system shall...' → 'It shall be ensured that...'
    Hidden actors make accountability impossible to assign.
    """
    match = ACTOR_PATTERN.match(req["text"])
    if not match:
        return None

    actor = match.group(1)
    remainder = req["text"][match.end():]
    mutated = copy.deepcopy(req)
    mutated["text"] = f"It shall be ensured that {remainder}"
    mutated["defect_type"] = "PASSIVE_VOICE"
    mutated["defect_description"] = (
        f"Removed system actor '{actor}', obscuring which system is responsible. "
        "Passive voice hides accountability and complicates test case writing."
    )
    mutated["original_text"] = req["text"]
    return mutated


# ──────────────────────────────────────────────
# DEFECT TYPE 4: Missing Condition
# Removes the trigger or qualifying context
# ──────────────────────────────────────────────

CONDITION_PHRASES = [
    "under all operating conditions",
    "during flight operations",
    "throughout the mission",
    "upon detection of manual override activation",
    "when cabin pressure drops below 75 kPa",
    "when remaining fuel drops below 15 percent of total capacity",
    "of detecting a traffic conflict",
    "of receiving the control signal",
]


def inject_missing_condition(req: dict) -> dict | None:
    """
    Remove a qualifying condition or trigger clause.
    Without conditions, requirements become ambiguous about WHEN they apply.
    """
    for phrase in CONDITION_PHRASES:
        if phrase in req["text"]:
            mutated = copy.deepcopy(req)
            # Remove the phrase and any leading connector words
            text = req["text"]
            for connector in [f" {phrase}", f", {phrase}", f" upon {phrase}"]:
                if connector in text:
                    mutated["text"] = text.replace(connector, "")
                    break
            else:
                mutated["text"] = text.replace(phrase, "")

            mutated["defect_type"] = "MISSING_CONDITION"
            mutated["defect_description"] = (
                f"Removed qualifying condition: '{phrase}'. "
                "Missing conditions make it unclear when the requirement applies, "
                "creating gaps in verification coverage."
            )
            mutated["original_text"] = req["text"]
            return mutated
    return None


# ──────────────────────────────────────────────
# DEFECT TYPE 5: TBD Placeholder
# Replaces defined values with an unresolved marker
# ──────────────────────────────────────────────

def inject_tbd(req: dict) -> dict | None:
    """
    Replace a specific numeric value with TBD.
    TBD placeholders in delivered specs signal incomplete design
    and block test case generation.
    """
    match = TIME_PATTERN.search(req["text"])
    if not match:
        return None

    target = match.group(0)
    mutated = copy.deepcopy(req)
    mutated["text"] = req["text"].replace(target, "[TBD]", 1)
    mutated["defect_type"] = "TBD_PLACEHOLDER"
    mutated["defect_description"] = (
        f"Replaced defined value '{target.strip()}' with TBD placeholder. "
        "Requirements with TBD values cannot be verified or tested."
    )
    mutated["original_text"] = req["text"]
    return mutated


# ──────────────────────────────────────────────
# Registry — all mutators used by the lab runner
# ──────────────────────────────────────────────

ALL_MUTATORS = [
    inject_weak_modal,
    inject_vague_timing,
    inject_passive_voice,
    inject_missing_condition,
    inject_tbd,
]

DEFECT_DESCRIPTIONS = {
    "WEAK_MODAL": "Weak modal verb ('should' instead of 'shall')",
    "VAGUE_TIMING": "Vague timing — specific value replaced with qualitative term",
    "PASSIVE_VOICE": "Passive voice — system actor removed",
    "MISSING_CONDITION": "Missing condition — qualifying trigger removed",
    "TBD_PLACEHOLDER": "TBD placeholder — value left undefined",
}
