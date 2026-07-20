# TASK: Right-size the gate render to the risk class

slug: risk-report-render · created: 2026-07-13 · stage: mvp
milestone: ceremony-to-effort
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 1 · SPECIFY — the rules

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: risk-proportional gate render — a mechanical/fast task's verify gate renders a compact form; the full card is reserved for security/data/architecture and every freeze (prose-only, message layer)
Must:
  - 6-verify.md's gate card gains the dispatch: `sensitivity: mechanical` + fast-lane tasks render the compact form (banner - SUMMARY - EVIDENCE - APPROVE); security / data / architecture always get the full card
  - 3-plan.md states the freeze always renders the full card, never the compact form
  - fast-lane.md's render sentence matches: freeze full, fast verify gate compact
  - report-template.md stays the FULL template's single home, untouched (reference pool has 32B headroom)
Reject:
  - the compact form weakening an imperative -> render-before-gate + Reported: yes + never-self-stamp survive verbatim
  - phases pool over 33284B -> compress-to-absorb
Accept: Given a `sensitivity: mechanical` or fast-lane task at the verify gate, When the agent reads 6-verify.md, Then it renders the compact banner-SUMMARY-EVIDENCE-APPROVE form, and the guide reserves the full card for security/data/architecture and every freeze.
Boundary: two render dialects — compact (mechanical/fast verify) and full (risk classes + freeze); the freeze side stated in 3-plan.md, the verify side in 6-verify.md + fast-lane.md
Assumptions: ⚠ no suite pins fast-lane.md's current "collapses sections, never the report" sentence — why: grepped 'collapses/never the report' across test_*.py, only unrelated hits; if wrong: the fence names it (cost: one re-run). NOTE the banned-slang regex \bcollapses? to\b — new wording avoids it

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols): skill/add/phases/6-verify.md (gate card, task 4/7's) · skill/add/phases/3-plan.md (freeze card) · skill/add/phases/fast-lane.md:23-24 (render sentence, unpooled) · x3 skill trees
Context (working folder): pools — phases 32509/33284 (775B headroom) · reference 51853/51885 (32B — report-template.md untouchable)
Honors (patterns / conventions): single-home dispatch (template-dedup discipline) · arc_gate_wiring pins (report-template + ARC per gate guide) · report-gate imperatives verbatim · banned slang list
Anchors the contract cites: the 6-verify gate card · the 3-plan freeze card · fast-lane.md's human-gates sentence
Ground SHA: dbb3a97 — stamped by freeze

### Contract

```
6-verify.md, appended to the gate-card paragraph:
  "Right-size the render to the risk: `sensitivity: mechanical` and fast-lane
   tasks use the compact form — banner - SUMMARY - EVIDENCE - APPROVE;
   `security` / `data` / `architecture` always get the full card."
3-plan.md, appended after the freeze card sentence:
  "The freeze always renders the full card — never the compact form."
fast-lane.md 23-24 ->
  "Both human gates still render: the freeze gets the full card (3-plan.md);
   the fast verify gate uses the compact form — banner - SUMMARY - EVIDENCE -
   APPROVE (6-verify.md). Collapse sections, never the gate."
report-template.md: zero bytes changed.
```

`Least-sure flag surfaced at freeze:` [spec] dropping FLAGS from the compact form assumes a mechanical/fast task's flags fit in SUMMARY — why: those lanes rarely carry open flags at verify; if wrong: a flagged mechanical task under-renders at its gate (cost: the human asks one follow-up; the full card is one read away)
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): `add-method/tooling/` `add-method/skill/` `add-method/src/add_method/_bundled/skill/` `.claude/skills/`
Strategy & known-problem fixes: 1) red tests test_risk_report_render.py 2) the three guide edits 3) sync x3 skill trees 4) pool check 5) fence. Traps: avoid the \bcollapses? to\b banned idiom; imperatives stay verbatim; report-template.md untouched (32B reference headroom).
Approach (domain strategy): single-home dispatch lines, prose-only, no engine change

### AI-verify record (required when gate_mode: ai-plan-verify)
- [x] §3 PLAN grounding anchors resolve in the current tree (all three guide spots read this session)
- [x] §1 every Must + every Reject present, each Reject paired with an outcome
- [x] §3 Contract shape is concrete (no template placeholder text remains)
- [x] Lowest-confidence flag surfaced and substantive (FLAGS dropped from the compact form)
Verified by: claude-opus-4-8 (orchestrator, inline) · at: 2026-07-13T13:55:00Z

---

## 4 · TESTS — failing-first (red)

Plan: test_verify_card_dispatch (mechanical + fast -> compact; security/data/architecture -> full) · test_compact_subset_order (banner-SUMMARY-EVIDENCE-APPROVE ordered in the dispatch) · test_freeze_reserves_full (3-plan: never the compact form) · test_fast_lane_matches (freeze full + verify compact) · test_imperatives_survive (both guides verbatim) · test_single_home (dispatch phrase absent from report-template.md) · test_phases_pool_within_target.
Tests live in: `add-method/tooling/test_risk_report_render.py` · MUST run red before Build.

---

## 5 · BUILD — AI writes the code (execution)

> The change plan was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope; improve on the strategy if the code teaches you better.
Strategy actually used: as planned, with one pool correction: fast-lane.md sits in the REFERENCE pool (32B headroom), not outside it — the ~93B sentence growth busted the lean fence; absorbed by compressing the same guide (my own sentence tightened + two prose trims), landing the pool back under 51885. The dispatch text itself shipped as contracted.
Code lives in: `./src/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build (fence 3483/3483 OK, +7 = this task's suite)
- [x] green was EARNED — the 7 tests pin ordered dispatch text, verbatim imperatives, the single-home guard, and the pool target against the REAL guides
- [x] input dialect held — the two render dialects (compact verify vs full freeze) each pinned by its own test, per the §1 Boundary
- [x] no exposed secrets, injection openings, or unexpected dependencies (prose-only; ENGINE_MD5 unchanged)

Build expectations (from §1 Accept + §3 CONTRACT): a mechanical/fast task's verify gate reads the compact form off 6-verify.md; security/data/architecture and every freeze keep the full card — confirmed by test_risk_report_render (7/7) + reference pool back under 51885 and phases at 32823/33284.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-13

