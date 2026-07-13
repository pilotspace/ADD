# TASK: Gate render cards: phase guides self-suffice; big references read-once

slug: gate-read-diet · created: 2026-07-13 · stage: mvp
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
Feature: gate render cards — the weight audit measured report-template.md (9.6KB, 3 call sites) + run.md (8.9KB, 4 call sites) re-read per gate/session; the two heaviest task-agnostic reads after SKILL.md
Must:
  - phases/3-plan.md's freeze section carries a RENDER CARD: the report skeleton (banner - ARC - SHAPE - SUMMARY - FLAGS - DECIDED - EVIDENCE - APPROVE - NEXT) inline, so the guide alone suffices for a standard freeze
  - phases/6-verify.md's gate section carries the same card shape (with the reconcile-FLAGS sentence kept)
  - SKILL.md states the read-once rule: report-template.md / run.md load at most once per session; the phase cards carry the gate essentials
  - the report-gate imperatives survive verbatim (render before FROZEN/gate - record Reported: yes - never self-stamp/timeout)
Reject:
  - copying report-template.md RULES into the cards -> the card is a SKELETON + pointer; details keep ONE home (template-dedup discipline)
  - phases pool over its 33284B target -> compress-to-absorb, never rebaseline
Accept: Given a fresh session at a freeze or verify gate, When the agent reads only the phase guide, Then it can render the full report skeleton and knows the big files are read-at-most-once references.
Boundary: two gate dialects — freeze (3-plan) and verify (6-verify) cards; same skeleton, gate-specific imperative lines
Assumptions: ⚠ arc_gate_wiring pins ("report-template" - "ARC" - "reconcile" - "report --decide") are the only prose pins on these sections — why: grepped the literal assertIns; if wrong: the fence names the pin and the card rewords around it (cost: one re-run)

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols): skill/add/phases/3-plan.md (freeze section ~40-48) · skill/add/phases/6-verify.md (gate section ~44-50) · skill/add/SKILL.md (report-template line ~105) · x3 skill trees
Context (working folder): phases pool 32180/33284 (1104B headroom) · core pool holds SKILL.md — fence checks it
Honors (patterns / conventions): arc_gate_wiring pins (report-template · ARC · reconcile · report --decide stay in each gate guide) · report-shape-scan pins (Summary-first sentence) · slang guard · template-dedup discipline (skeleton+pointer, one home for details)
Anchors the contract cites: the freeze section (3-plan) · the gate section (6-verify) · SKILL.md report-template sentence
Ground SHA: 2fe9cb3 — stamped by freeze

### Contract

```
3-plan.md freeze section gains (replacing the bare "per report-template.md" load):
  Render from this card — banner - ARC (goal - done - plan, engine-sourced) -
  SHAPE - SUMMARY - FLAGS (lowest-confidence first) - DECIDED - EVIDENCE -
  APPROVE (guided choice) - NEXT; `report-template.md` = full template +
  examples, read at most once per session.
  Imperative kept verbatim: render before FROZEN - record Reported: yes -
  never on a timeout. See run.md pointer kept.
6-verify.md gate section gains the same card (verify dialect): banner - ARC -
  SUMMARY - FLAGS - EVIDENCE - APPROVE - NEXT + the kept reconcile sentence
  (add.py report --decide) + render-before-gate imperative verbatim.
SKILL.md: one read-once sentence at the report-template.md mention — the big
  references load at most once per session; the phase cards carry the gate
  essentials.
Pools: phases pool stays <= 33284; any overflow compresses SAME-guide prose.
```

`Least-sure flag surfaced at freeze:` [spec] the read-once rule changes agent behavior only via prose — why: no engine enforcement backs it (by design, message layer); if wrong: re-reads persist and only the re-measure shows it (cost: the lever under-delivers, measured not silent)
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): `add-method/tooling/` `add-method/skill/` `add-method/src/add_method/_bundled/skill/` `add-method/src/add_method/_bundled/tooling/` `.claude/skills/`
Strategy & known-problem fixes: 1) red tests in add-method/tooling/test_gate_read_diet.py 2) 3-plan card 3) 6-verify card 4) SKILL.md sentence 5) sync x3 skill trees 6) pool check + compress-to-absorb 7) fence. Traps: phases pool 1104B headroom binds BOTH cards; arc_gate_wiring literals must survive; the Summary-first pinned sentence untouched.
Approach (domain strategy): skeleton-card + read-once pointer, single home for details

### AI-verify record (required when gate_mode: ai-plan-verify)
- [x] §3 PLAN grounding anchors resolve in the current tree (3-plan ~40-48 · 6-verify ~44-50 · SKILL.md ~105 — read this session)
- [x] §1 every Must + every Reject present, each Reject paired with an outcome
- [x] §3 Contract shape is concrete (no template placeholder text remains)
- [x] Lowest-confidence flag surfaced and substantive (prose-only lever, measured at the re-measure)
Verified by: claude-opus-4-8 (orchestrator, inline) · at: 2026-07-13T12:20:00Z

---

## 4 · TESTS — failing-first (red)

Plan: test_plan_guide_carries_render_card (skeleton section names in order) · test_verify_guide_carries_render_card · test_read_once_rule_in_skill · test_imperatives_survive (render-before + Reported: yes + never-self-stamp verbatim in both guides) · test_wiring_pins_survive (report-template/ARC/reconcile/report --decide) · test_phases_pool_within_target.
Tests live in: `add-method/tooling/test_gate_read_diet.py` · MUST run red before Build.

---

## 5 · BUILD — AI writes the code (execution)

> The change plan was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope; improve on the strategy if the code teaches you better.
Strategy actually used: as planned, plus two fence-driven reworks the §1 flag predicted: (1) test_report_shape_scan_audit pins 'rendering SHAPE then the freeze APPROVE as a guided choice' verbatim x3 trees — the 3-plan card carries that sentence inline after the skeleton; (2) the core pool's frozen 18186B target absorbed the SKILL.md read-once sentence via same-pool compression (nothing-duplicated tail · voice parenthetical · plan-phase sentence · fast-bullet trims) — landed exactly 18186/18186. My own imperative test also caught a mid-phrase line wrap in the card — rewrapped the guide, never the test.
Code lives in: `./src/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build (fence 3470/3470 OK, +7 = this task's suite; §3 untouched post-freeze)
- [x] green was EARNED — the 7 tests pin ordered skeleton names, verbatim imperatives, wiring pins, and the pool byte target against the REAL guide files; no fixture to overfit
- [x] input dialect held — prose-only task; the two gate dialects (freeze card vs verify card) are each pinned by their own ordered-section test
- [x] no exposed secrets, injection openings, or unexpected dependencies (prose-only; no engine change — ENGINE_MD5 unchanged)

Build expectations (from §1 Accept + §3 CONTRACT): a fresh session at a freeze or verify gate can render the full report skeleton from the phase guide alone, and both big references are marked read-at-most-once — confirmed by test_gate_read_diet (7/7) + pools at 32509/33284 phases and exactly 18186/18186 core.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-13

