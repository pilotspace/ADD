# TASK: Persona nudge fires at seams only + tokens_uncached artifact

slug: persona-nudge-quiet · created: 2026-07-08 · stage: mvp
milestone: add-lean-loop
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): add-method/tooling/add.py:2207 (cmd_status persona pointer) + 2 twins · engine_pin.py · benchmark/score.py (tokens_uncached artifact) · 2 new/extended test modules
Context (working folder): benchmark evidence — the unseeded PERSONA_HINT printed 20-30×/run on `status`; agents deliberated it 65-93× and wrote 0 persona files (pure context noise). No test pins the `persona :` status line (grep-verified). init/new-milestone keep their nudges (pinned by test_persona_milestone_nudge). Uncached completion = input+cache_creation+output — 1.0-1.7% of raw totals; the honest "new work" measure.
Honors (patterns · conventions): 3-tree parity + ENGINE_MD5 re-pin; artifacts precedent (engine_calls); frozen 5 metrics untouched
Anchors the contract cites: cmd_status persona branch · score_record artifacts["tokens_uncached"]
Ground SHA: 069033f

---

## 1 · SPECIFY — the rules

Feature: persona nudge fires at seams only + tokens_uncached artifact
Must:
  - full `status` prints the unseeded persona hint ONLY when no task is active (orientation context); during an active task the line is suppressed (the roster line for seeded personas is unchanged)
  - init and new-milestone keep their existing persona nudges byte-unchanged (the discovery seams)
  - score_record writes artifacts["tokens_uncached"] = str(int) — input + cache_creation + output parsed from the transcript's final usage event; "0" when unparseable; frozen 5 metrics untouched
Reject:
  - (none — render + artifact only)
Accept: Given an active task, When `status` prints, Then no "no project-fit persona" line appears; Given no active task and no seeded persona, Then it appears; Given a scored record, Then artifacts carry tokens_uncached.
Assumptions: ⚠ none material — biggest risk: a doc names the status nudge as every-session; grep found none

---

## 3 · CONTRACT — freeze the shape

```
cmd_status: persona unseeded-hint gated on `not _active_task(state)`; seeded roster branch unchanged
score_record: artifacts["tokens_uncached"] = str(input + cache_creation + output)  # from final usage event
frozen: init/new-milestone nudges byte-unchanged; 5 metrics unchanged; 3-tree parity; ENGINE_MD5 re-pin once
```

`Least-sure flag surfaced at freeze:` [spec] suppressing during active tasks may delay persona discovery on long single-task projects — accepted: init/new-milestone/idle-status still carry it; if wrong: re-widen to a once-per-session print
Status: FROZEN @ v1 — approved by Tin Dang (question 2026-07-08: optional personas + completion-only token count)

---

## 4 · TESTS — failing-first (red)

Suites: add-method/tooling/test_persona_nudge_quiet.py — 3 tests (idle status nudges ·
active-task status quiet · new-milestone nudge unchanged); benchmark/tests/
test_adherence_census.py +2 (tokens_uncached from final usage event, cache reads excluded ·
zero fallback). RED confirmed: 1 engine failure (active-task status still nags) + 2
benchmark failures (_tokens_uncached missing) — red for the right reason.

---

## 5 · BUILD — AI writes code

Scope (may touch): `add-method/tooling/add.py` · `.add/tooling/add.py` · `add-method/src/add_method/_bundled/tooling/add.py` · `add-method/tooling/engine_pin.py` · `add-method/tooling/test_persona_nudge_quiet.py` · `benchmark/score.py` · `benchmark/tests/` · `benchmark/runs/` · `tmp/` · `.add/` · `benchmark/arms/`
Strategy & known-problem fixes: <ordered build steps · the trap each known problem must dodge · let the active persona's domain stance (or "generic") shape the approach, not just patterns>
Approach (domain strategy): <technique · shapes · pattern · optimization stance in one line, in the task's domain vocabulary — or "obvious, correctness-first">
Strategy actually used: <fill at verify — what you ACTUALLY did, or "as planned"; harvested into §7 Decisions>
Code lives in: `./src/`   ·   Constraints: change no test, no contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build
- [x] green was EARNED — no overfit / vacuous asserts / stubbed-away logic
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP)

Build expectations (from §1 Accept + §3 CONTRACT): idle `status` keeps the persona discovery nudge; an active-task `status` never re-prints it; `new-milestone` nudge unchanged; score.py emits `tokens_uncached` excluding cache reads — confirmed by test_persona_nudge_quiet.py (3/3), benchmark suite 124 passed, full tooling suite 3209 OK, 3-tree byte fence + ENGINE_MD5 3ea3da85 held.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-08
