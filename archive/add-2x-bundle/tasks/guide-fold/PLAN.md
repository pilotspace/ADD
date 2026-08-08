# TASK: advance folds the guide's chapter pointer + says no need to re-run guide

slug: guide-fold · created: 2026-07-14 · stage: mvp
milestone: orientation-honesty
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; the observe note is one optional line at the gate.

---

## 1 · SPECIFY — the rules

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: a COMPLETING `advance` folds in the landed phase's guide chapter — the ONE `add.py guide` line the `next:` footer lacks (the footer already carries the command + the short why) — as a `guide: .add/docs/<chapter>` line printed right ABOVE the footer, plus a note that this + the footer ARE the guide (no separate `add.py guide` call). Kills the stubborn re-run-`guide` habit the anatomy flagged, WITHOUT duplicating the footer (dedup concern: the footer already gives command+why, so the fold adds only the chapter + the "don't re-run" cue — never the command or why again).
Must:
  - a completing `advance` that LANDS in a non-`done` phase prints `guide: .add/docs/<chapter>` for the LANDED phase (chapter from `PHASE_GUIDE[nxt][1]`), on its own line, BEFORE the existing `next:` footer — the footer is unchanged, still exactly one `next:` line
  - the fold line states the agent needn't re-run `add.py guide` (a stable cue naming `add.py guide`)
  - landing in `done` prints NO guide-fold line — Arm B (the milestone decision) owns that juncture; only the `next:` footer prints
  - a bundle fast-forward INTERMEDIATE crossing prints no fold (it returns above the footer already); only the FINAL landing folds — so still exactly one fold line per completing advance
Reject:
  - a corrupt/unmapped landed phase (not in PHASE_GUIDE) -> print NO fold line, never a KeyError (fail-soft, mirroring the footer's own ethos) -> "fold_failsoft_skip"
Accept: Given a fresh task at specify, When `add.py advance` lands it in plan, Then stdout carries `guide: .add/docs/05-step-3-plan.md` (plan's chapter) above the single `next:` footer AND names `add.py guide` as the thing not to re-run; and advancing a task INTO done prints only the footer, no `.add/docs/` fold
Boundary: a mid-flight landing (specify/plan/tests/build/verify → folds the landed chapter) vs the `done` landing (no fold, Arm B footer only) — the two shapes the test pins
Assumptions: ⚠ the fold placed right before `print(_next_footer(...))` (after the bundle fast-forward `return`) only ever runs on the FINAL landing — verified by the code path: intermediates `return` above it; if wrong (a fold prints per intermediate): the test's single-fold-line assert catches it, no silent double-print

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols): `add.py:cmd_advance` — add the guide-fold print right before its final `print(_next_footer(root, state))` (after the bundle fast-forward `return`), guarded `nxt != "done"` and PHASE_GUIDE-present; reuses `PHASE_GUIDE[nxt][1]` (the chapter, the same source `cmd_guide`'s `read:` line uses)
Context (working folder): `add-method/tooling/` (canonical add.py + 4 twins); ENGINE_MD5 re-pinned; SEAMS `_declared_scope` re-pinned if its line drifts (cmd_advance @ ~1638 is ABOVE _declared_scope@5711 → adding ~4 lines shifts it DOWN → expect a re-pin)
Honors (patterns / conventions): `cmd_guide`'s `read   : .add/docs/<chapter>` line (the fold mirrors that exact chapter source, `PHASE_GUIDE[phase][1]`); the footer's own fail-soft ethos (a completed+saved advance NEVER crashes on a render step — `.get(nxt)` guard, no KeyError); the additive-cue convention (present-only, one extra line, footer untouched)
Anchors the contract cites: `cmd_advance` · `_next_footer` · `PHASE_GUIDE`
Ground SHA: 0798bd2 — stamped by freeze

### Contract

```
cmd_advance, on the FINAL landing (past the `_to` bundle fast-forward return), before print(_next_footer(...)):
  if nxt != "done":
    entry = PHASE_GUIDE.get(nxt)            # fail-soft: unmapped phase -> no fold, no KeyError
    if entry is not None:
      print(f"guide: .add/docs/{entry[1]} — the phase chapter (this + the next line ARE `add.py guide`; no separate call)")
  print(_next_footer(root, state))          # UNCHANGED — still exactly one next: line
# done landing: nxt == "done" -> no fold; Arm B footer only
# intermediate bundle crossings: return above this point -> never fold
```

`Least-sure flag surfaced at freeze:` [contract] whether the fold belongs in `cmd_advance` (vs inside `_next_footer`) — it must stay in cmd_advance so `_next_footer` remains a PURE single-`next:`-line resolver reused by every other verb (status/gate/new-task); folding inside the footer would leak a chapter line onto surfaces that must print only `next:`. If wrong (some other verb also wants the fold): additive later, never a regression — cmd_advance is the only completing verb that lands an agent INTO a working phase.
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `.add/tooling/engine_pin.py` `add-method/.add/tooling/engine_pin.py` `add-method/src/add_method/_bundled/tooling/engine_pin.py` `.add/SEAMS.md` `add-method/tooling/test_guide_fold.py`
Strategy & known-problem fixes: 1. RED test_guide_fold (advance specify→plan prints `guide: .add/docs/05-step-3-plan.md` + names `add.py guide`, above ONE `next:` footer; advance INTO done prints no `.add/docs/` fold; still exactly one fold line — no per-intermediate double-print). 2. add the guarded fold print before `_next_footer` in cmd_advance (trap: guard `nxt != "done"` AND `.get(nxt)` fail-soft; place AFTER the fast-forward `return` so intermediates never fold). 3. sync ×4 add.py twins, re-pin ENGINE_MD5, re-pin SEAMS `_declared_scope` if it drifted.
Approach (domain strategy): footer-adjacent chapter fold

### AI-verify record (required when gate_mode: ai-plan-verify)
- [x] §3 PLAN grounding anchors resolve in the current tree — cmd_advance, _next_footer, PHASE_GUIDE all live in add.py/constants.py
- [x] §1 every Must + every Reject present, each Reject paired with an error code — fold_failsoft_skip on unmapped phase
- [x] §3 Contract shape is concrete (no template placeholder text remains)
- [x] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar) — cmd_advance vs _next_footer placement
Verified by: orchestrator · at: 2026-07-14

---

## 4 · TESTS — failing-first (red)

Plan: test_<accept> — assert the §1 Accept line's Then (behavior, not internals).
Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution)

> The change plan was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope; improve on the strategy if the code teaches you better.
Strategy actually used: as planned — added the guarded guide-fold `print` in `cmd_advance` right before `print(_next_footer(...))`, after the bundle fast-forward `return` (so intermediates never fold), guarded `nxt != "done"` + `PHASE_GUIDE.get(nxt)` fail-soft. Synced ×4 add.py twins, ENGINE_MD5→c8e0a3e5…; SEAMS `_declared_scope` re-pinned 5711→5723 (the fold + its comment sit above it in cmd_advance). No divergence.
Code lives in: `./src/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build — guide-fold 4 green, 94 footer/ergonomics/pin tests green, full fence (pending tail)
- [x] green was EARNED — the 3 fold asserts were RED (0 fold lines) before the cmd_advance print existed; the done-landing assert guards the fold from leaking onto the Arm-B juncture (verify-landing DOES fold, done-landing does NOT — both pinned)
- [x] input dialect held — the test speaks the real CLI stdout dialect (advance stdout lines) + the exact chapter strings PHASE_GUIDE emits
- [x] no exposed secrets/injection/deps — pure static string + a dict lookup (security = HARD-STOP: none)

Build expectations (from §1 Accept + §3 CONTRACT): a completing `add.py advance` that lands in a non-done phase prints a `guide: .add/docs/<chapter>` line (chapter = the LANDED phase's, e.g. `05-step-3-plan.md` for specify→plan, `06-step-4-tests.md` for plan→tests) naming `add.py guide` as not-to-re-run, ABOVE the single `next:` footer; advancing INTO done prints only the footer (no `.add/docs/` fold) — confirmed by test_guide_fold (4 asserts) + the full fence.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-14

