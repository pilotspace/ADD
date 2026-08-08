# MILESTONE: Advisor Context

goal: every ADD step carries richer AI-facing context — a tool-agnostic advisor strategy for spawning a plan-following subagent, and an advisory confidence self-score rubric — so any agent driving the loop knows when to delegate and how to self-assess, without the engine ever spawning or gating on it
rationale: new-major (confirmed intake 2026-06-14) — the subagent-spawn pattern is scattered today (ground sweep · verify refuter · streams adapter) and the confidence self-score lives only in the streams worker prompt; this promotes both into first-class, per-step guidance so every agent that drives the loop knows when to delegate and how to self-assess
stage: mvp · status: active · created: 2026-06-14

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  a shared `advisor.md` strategy (when-to-spawn · reusable plan-following prompt template · vendor-neutral tier pick — generalizing the existing ground/verify/streams patterns); a shared `confidence.md` guideline (0–1 six-dimension self-score · refine-if-<0.9 · feeds the lowest-confidence-first flag · MAY recommend lowering autonomy); a thin per-step Advisor+Confidence hook woven into all 8 phase guides; discoverability cross-refs in SKILL.md / run.md; content-assertion tests + XML-convention compliance + mirror propagation
Out: any engine spawn capability (the method is tool-agnostic — the engine never spawns; refused); confidence as a GATE (refused — violates "the AI never asserts a gate it cannot prove", run.md); changing the existing lowest-confidence-first FLAG semantics; any new top-level XML tag that breaks the frozen vocabulary (test_xml_convention)

## Shared decisions & glossary deltas   (living — every task must honor these)
- Tool-agnostic: the advisor RECOMMENDS spawning; `add.py` never spawns one (mirrors the existing "the engine never spawns one" in 0-ground.md / 6-verify.md)
- Confidence is advisory-only: it never auto-passes and never auto-blocks; at most it RECOMMENDS lowering autonomy or re-drafting — the gate stays evidence-based and human-owned
- One source each + progressive disclosure: the strategy lives in `advisor.md`, the rubric in `confidence.md`; each phase guide carries a THIN hook that POINTS to them — never restates them (anti-bloat)
- XML-vocab compliance: per-step hooks honor the frozen closed tag vocabulary (test_xml_convention) — no new top-level XML tags in phase guides
- Phase-appropriate, not boilerplate: the advisor hook fits the step (ground→broad-sweep subagent · tests→red-suite author · build→batch implementer · verify→adversarial refuter · …), never a copy-pasted block

## Shared / risky contracts (freeze these first)
- the confidence rubric grammar (the six dimensions · the 0–1 scale · the refine threshold — render-blind testable) -> owning task confidence-rubric
- the advisor hook grammar (what a per-step hook says + the reusable plan-following prompt template — render-blind testable) -> owning task advisor-strategy

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] confidence-rubric   depends-on: none                          — `confidence.md`: 0–1 six-dimension self-score · refine-if-<0.9 · feeds the lowest-confidence flag · advisory-only (never a gate)
- [x] advisor-strategy    depends-on: none                          — `advisor.md`: when-to-spawn decision · reusable plan-following prompt template · vendor-neutral tier pick · "the engine never spawns"
- [x] per-step-hooks      depends-on: confidence-rubric,advisor-strategy — thin Advisor+Confidence hook in all 8 phase guides + SKILL.md/run.md cross-refs; XML-clean; mirrors propagated + parity green

## Exit criteria (observable; map each to the task that delivers it)
- [x] `confidence.md` defines the 0–1 six-dimension rubric + the refine-if-<0.9 rule + the advisory-only statement   (verify: test_confidence_rubric green — rubric + no gate language)   (← confidence-rubric)
- [x] `advisor.md` carries the when-to-spawn decision + the plan-following prompt template + the "the engine never spawns" line   (verify: test_advisor_strategy green — tool-agnostic line + fenced template)   (← advisor-strategy)
- [x] all 8 `phases/*.md` carry an Advisor hook AND a Confidence hook that point to the shared docs   (verify: test_per_step_hooks green — all 8 guides + distinctness)   (← per-step-hooks)
- [x] the frozen XML vocabulary still holds — no new top-level tags in phase guides   (verify: test_xml_convention green)   (← per-step-hooks)
- [x] every mirror is propagated and parity is green   (verify: test_tree_parity · test_book_parity · test_bundle_parity green)   (← per-step-hooks)
