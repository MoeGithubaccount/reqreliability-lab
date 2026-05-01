# Requirements Reliability Lab

**A mutation testing bench for evaluating automated requirement reviewers.**

Most AI projects show what AI can do.  
This one measures whether AI can be trusted.

---

## The Problem

In aerospace and safety-critical software development, bad requirements are expensive.
Research consistently shows that requirements defects caught late cost 10–200× more
to fix than those caught during initial analysis.

Automated tools — including generative AI — can help review requirements.  
But before deploying them in a serious engineering context, you need evidence:
*How well does the reviewer actually catch the issues that matter?*

This lab answers that question.

---

## How It Works

```
Clean Requirement
      │
      ▼
┌──────────────┐    inject known defect     ┌─────────────────────┐
│   Mutator    │ ─────────────────────────▶ │  Mutated Requirement │
└──────────────┘                            └─────────────────────┘
                                                       │
                                          run through reviewer
                                                       │
                                                       ▼
                                           ┌───────────────────┐
                                           │  Issues Found?    │
                                           └───────────────────┘
                                                       │
                                         compare against known defect
                                                       │
                                          ┌─────────────────────┐
                                          │  Score: CAUGHT/MISSED│
                                          └─────────────────────┘
```

1. **Inject** — Apply one of 5 defect types to a clean baseline requirement
2. **Review** — Run the mutated requirement through an automated reviewer
3. **Score** — Did the reviewer catch the injected defect?
4. **Report** — Aggregate detection rates by defect type across all test cases

This is not a requirement *generator*. It is a requirement reviewer *evaluator*.

---

## Defect Types

| Defect | Example | Risk |
|--------|---------|------|
| **WEAK_MODAL** | `shall` → `should` | Removes mandatory enforcement |
| **VAGUE_TIMING** | `200ms` → `quickly` | Makes requirement untestable |
| **PASSIVE_VOICE** | Actor removed | Hides system responsibility |
| **MISSING_CONDITION** | Trigger clause removed | Creates ambiguous scope |
| **TBD_PLACEHOLDER** | Value replaced with `[TBD]` | Blocks test case generation |

---

## Quick Start

No external dependencies. Runs on Python 3.8+.

```bash
git clone https://github.com/your-username/req-reliability-lab.git
cd req-reliability-lab

python run_lab.py          # run experiment, print results
python run_lab.py --save   # also save full JSON report to reports/
```

---

## Sample Output

```
══════════════════════════════════════════════════════════════
  REQUIREMENTS RELIABILITY LAB
  Experiment: Rule-Based Reviewer Baseline
══════════════════════════════════════════════════════════════

OVERALL RESULTS
  Total tests run  : 46
  Defects caught   : 38
  Defects missed   : 8
  Detection rate   : [████████████████░░░░] 82.6%

DETECTION RATE BY DEFECT TYPE
  Weak modal verb          [████████████████] 100.0%  (10/10)
  Vague timing / no value  [████████████████] 100.0%  (9/9)
  Passive voice / no actor [████████████████] 100.0%  (10/10)
  Missing condition        [░░░░░░░░░░░░░░░░] 0.0%    (0/8)  ← blind spot
  TBD placeholder          [████████████████] 100.0%  (9/9)
```

**The 0% on MISSING_CONDITION is the most interesting result.**  
The rule-based reviewer has no mechanism to detect what's *absent*.  
That's the justification for adding an LLM reviewer — and the next experiment.

---

## Project Structure

```
req-reliability-lab/
├── data/
│   └── requirements.py     # 10 synthetic aerospace-style requirements
├── lab/
│   ├── mutators.py         # 5 defect injection functions
│   ├── reviewers.py        # Reviewer implementations (rule-based baseline)
│   └── evaluate.py         # Experiment orchestration and scoring
├── reports/                # JSON output from experiments
├── run_lab.py              # Main entry point
└── requirements.txt        # No external deps for MVP
```

---

## Architecture Decisions

**Rules-based first, LLM second.**  
The baseline reviewer uses deterministic logic — fast, free, repeatable, and explainable.
This gives a meaningful baseline before introducing an LLM reviewer.
When the LLM reviewer is added, you can directly compare detection rates.

**Defect injection over generated test cases.**  
Rather than asking an LLM to generate "bad requirements", we inject specific known
defect types into clean requirements. This gives us ground truth — we know exactly
what was injected — so scoring is reliable and reproducible.

**Separation of concerns.**  
Mutators, reviewers, and evaluation logic are separated. Adding a new defect type
or a new reviewer is additive — no other files need to change.

---

## Roadmap / Week 2 Upgrade

- [ ] Add LLM reviewer using LangChain + OpenAI GPT-4
- [ ] Compare LLM vs rule-based detection rates side-by-side
- [ ] Multi-prompt comparison (Prompt A vs Prompt B on same test set)
- [ ] Expand defect type library
- [ ] Streamlit dashboard for visual results
- [ ] GitHub Actions for automated regression tracking

---

## Background

This project draws on:
- NASA Systems Engineering Handbook — requirements quality checklist
- INCOSE Guide to Writing Requirements
- IBM Engineering Requirements Quality Assistant (RQA) — industry context
- Bashir et al. (2023), "Requirements Ambiguity Detection and Explanation with LLMs"
- Mutation testing methodology from software engineering, applied to requirements

---

## What This Is and Isn't

**Is:**  A proof-of-concept experiment framework for evaluating requirement reviewers.  
**Is:**  A practical demonstration of systematic GenAI evaluation methodology.  
**Is:**  An open tool for exploring where automated reviewers succeed and fail.

**Is not:**  A production-ready, certified, or compliance-validated tool.  
**Is not:**  A substitute for formal requirements management processes.  
**Is not:**  Affiliated with any aerospace organization.

---

## Author

Mohamed Ibrahim  
AI Consultant
[LinkedIn](https://www.linkedin.com/in/mohamed-ibrahim-91b393103/)
