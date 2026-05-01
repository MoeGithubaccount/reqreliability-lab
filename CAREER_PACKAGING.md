# Requirements Reliability Lab — Career Packaging

---

## RESUME BULLET — MVP Version (use tonight)

Built the Requirements Reliability Lab, a Python experiment framework that injects
known defects into aerospace-style requirements (weak modals, vague timing, passive
voice, missing conditions, TBD placeholders) and measures automated reviewer detection
rates by defect type, producing structured experiment reports.

---

## RESUME BULLET — Week 2 Version (after LLM integration)

Engineered the Requirements Reliability Lab, a Python/LangChain testbench that injects
known requirement defects and compares LLM vs. rule-based reviewer detection rates
across defect categories, demonstrating systematic GenAI evaluation for safety-critical
development contexts. Rule-based baseline: 82.6% detection. LLM reviewer: [your result].

---

## GITHUB README — Opening paragraph

Requirements Reliability Lab is an experiment framework that injects known defects into
safety-critical-style requirements — vague timing, weak modal verbs, passive voice,
missing conditions — then measures how well automated reviewers detect them. It produces
quantitative detection rates by defect type, showing exactly where a reviewer succeeds
and where it fails. Built to explore a question that matters in serious engineering
contexts: before you trust an AI tool to review requirements, how do you know it works?

---

## TAGLINE

"Mutation testing for requirements. Measures whether AI reviewers can actually be trusted."

---

## 30-SECOND INTERVIEW ANSWER

"I built a tool called the Requirements Reliability Lab. The idea is straightforward:
take clean, well-written requirements, inject specific known defects — things like
vague timing, weak modal verbs, removed conditions — then run an automated reviewer
and measure whether it catches them. I started with a rule-based baseline reviewer.
It caught 82.6% of injected defects overall — 100% on obvious linguistic issues,
but 0% on missing conditions, because you can't detect what's absent with rules alone.
That gap is what justifies adding an LLM reviewer as the next experiment."

---

## 2-MINUTE INTERVIEW ANSWER

"In safety-critical engineering, bad requirements are expensive. The standard guidance
from NASA and INCOSE is clear on what good requirements look like — they use 'shall'
not 'should', they have measurable values, they specify conditions. The question is
whether automated tools, including AI, can reliably catch when those standards aren't
met.

I built the Requirements Reliability Lab to answer that question systematically. It
takes clean baseline requirements and applies what I call mutators — functions that
inject one specific defect at a time. A weak modal mutator changes 'shall' to 'should'.
A vague timing mutator replaces '200 milliseconds' with 'quickly'. A missing condition
mutator removes the trigger clause. Each mutant has a known ground truth defect.

I then run each mutated requirement through an automated reviewer and measure whether
it flags the injected issue. The baseline reviewer I built is rule-based — fast,
deterministic, no API calls. It caught 82.6% of defects overall. Strong on obvious
linguistic issues. But 0% on missing conditions, because rules can only find what's
present, not what's absent.

That 0% is the most interesting result. It's the precise justification for adding an
LLM reviewer as the next experiment — and exactly the kind of evidence-driven iteration
the Collins ART team is focused on. The project is on GitHub with the full experiment
report."

---

## LINKEDIN POST — In Mohamed's voice

Most AI project posts start with "excited to share."

This one starts with a 0%.

I ran my first experiment on the Requirements Reliability Lab — a Python tool I built
to test how well automated reviewers catch defects in safety-critical requirements.

The approach: take clean, well-written requirements. Inject known defects — vague
timing, weak modal verbs, passive voice, missing conditions. Measure how many the
reviewer catches.

The rule-based baseline I built caught 82.6% overall.

100% on weak modal verbs. 100% on vague timing. 100% on TBD placeholders.

0% on missing conditions.

That 0% is the finding. Rules can only detect what's present. They're completely
blind to what's absent — a removed condition, a missing trigger clause, a gap that
looks like a sentence but isn't a complete requirement.

That's the gap an LLM might close. That's the next experiment.

The tool is on GitHub. No external dependencies. Runs in one command.

What defect types would you add?

[GitHub link]

---

## WHAT NOT TO SAY

Do not say:
- "DO-178C compliant" or "certified for aerospace use"
- "production-ready" or "deployed in safety-critical environments"
- "I have extensive aerospace engineering experience"
- "I built this in my role at Collins" (you haven't started there)
- "This replaces current requirement review processes"
- "I'm an expert Python developer"

Do say:
- "proof-of-concept experiment framework"
- "demonstrates the methodology"
- "baseline results show..."
- "next step is..."
- "I studied NASA guidelines and industry research to inform this"
- "I built this to demonstrate systematic GenAI evaluation thinking"

---

## WEEK 2: ADDING THE LLM REVIEWER

When you add LangChain + OpenAI, the additional resume bullet becomes:

"Extended the Requirements Reliability Lab with a LangChain-integrated GPT-4 reviewer,
enabling side-by-side comparison of LLM vs. rule-based detection rates. LLM reviewer
improved missing-condition detection from 0% to [your result]%, demonstrating targeted
GenAI value in safety-critical requirements analysis."

The key number to report: did the LLM catch MISSING_CONDITION better than 0%?
That's your headline finding and your interview story.
