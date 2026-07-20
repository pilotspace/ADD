# TASK: already-initialised refusal points at the resume command

slug: init-resume-pointer · created: 2026-07-13 · stage: mvp
milestone: call-floor
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 1 · SPECIFY — the rules

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: init resume pointer — the WM1 re-measure showed every rep re-running `init` on a project the harness had already initialised (+2 calls/rep: the refusal, then re-orientation)
Must:
  - the `already initialised` refusal names the resume command in the SAME message: `— resume: add.py status`
  - the refusal stays a refusal: exit code and the existing message head byte-identical (reject-writes-nothing untouched)
Reject:
  - `init --force` behavior change -> none; --force still resets
Accept: Given an initialised project, When `init` runs without --force, Then the refusal ends with `resume: add.py status` and exits nonzero with no tree write.
Boundary: none — no external input
Assumptions: none material — biggest risk: an unseen doc restates the refusal verbatim (grepped test_*.py: zero pins)

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols): add-method/tooling/add.py:cmd_init (~593, the already-initialised _die)
Context (working folder): ENGINE_MD5 re-aims; SEAMS _declared_scope pin drifts only if line count changes above 5581 (one-line edit: no)
Honors (patterns / conventions): reject path writes nothing · message-layer single line
Anchors the contract cites: cmd_init
Ground SHA: 726693d — stamped by freeze

### Contract

```
_die(f"already initialised at {root} (use --force to reset state) — resume: add.py status")
```

`Least-sure flag surfaced at freeze:` [test] the assertion greps stderr of a real double-init board — why: trivial surface; if wrong: cost one re-run
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/tooling/` `add-method/../.add/` `.add/tooling/` `add-method/.add/`
Strategy & known-problem fixes: red test -> one-line edit -> sync x3 + re-pin. Trap: never sync the test into twins.
Approach (domain strategy): obvious, correctness-first

### AI-verify record (required when gate_mode: ai-plan-verify)
- [x] §3 PLAN grounding anchors resolve in the current tree (add.py:593 read this session)
- [x] §1 every Must + every Reject present, each Reject paired with an outcome
- [x] §3 Contract shape is concrete
- [x] Lowest-confidence flag surfaced (trivial surface, flagged honestly)
Verified by: claude-opus-4-8 (orchestrator, inline) · at: 2026-07-13T16:00:00Z

---

## 4 · TESTS — failing-first (red)

Plan: test_refusal_names_resume (double init -> stderr ends with resume pointer, nonzero exit, tree byte-identical) · test_force_still_resets.
Tests live in: `add-method/tooling/test_init_resume_pointer.py` · MUST run red before Build.

---

## 5 · BUILD — AI writes the code (execution)

> The change plan was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope; improve on the strategy if the code teaches you better.
Strategy actually used: as planned — one-line message edit, zero pins hit.
Code lives in: `./src/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build (shared batch fence 3496/3496 OK)
- [x] green was EARNED — the test drives a real double-init board and asserts message + exit + byte-identical tree
- [x] input dialect held — no external input (§1 Boundary: none)
- [x] no exposed secrets, injection openings, or unexpected dependencies (one message literal)

Build expectations (from §1 Accept + §3 CONTRACT): the refusal ends with `resume: add.py status`, exits nonzero, writes nothing — confirmed by test_init_resume_pointer (2/2).

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-13

