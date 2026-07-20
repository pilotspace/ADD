# TASK: new-milestone names the oneshot lane at the bait point

slug: milestone-lane-nudge · created: 2026-07-13 · stage: mvp
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
Feature: milestone lane nudge — WM1 rep r1 lost 9-10 calls to milestone ceremony on single-task work despite the wrapper prescribing the oneshot lane; upstream instructions don't land, command-point nudges do (kickoff-truth precedent)
Must:
  - new-milestone's SUCCESS output gains one advisory line naming the cheaper lane, prefixed `lane:` (NOT `note:` — that marker class is pinned one-per-invocation): `lane: single task? the oneshot lane is cheaper: add.py new-task <slug> --oneshot`
  - the line prints before the next-footer (footer stays last); all existing output lines survive
Reject:
  - any behavior change -> none; advisory print only, milestone creation identical
Accept: Given any new-milestone creation, When it succeeds, Then stdout contains the oneshot advisory line and still ends with the next-footer.
Boundary: none — no external input
Assumptions: ⚠ some suite pins new-milestone stdout as an exact set — why: several nudge suites read it; if wrong: fence names it, additive line moves (cost: one re-run)

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols): add-method/tooling/add.py:cmd_new_milestone (tail, before the next-footer print)
Context (working folder): ENGINE_MD5 re-aims
Honors (patterns / conventions): footer-last · advisory nudges print `note:`-style lines (persona nudge precedent) · command-point beats wrapper prose (kickoff-truth)
Anchors the contract cites: cmd_new_milestone
Ground SHA: 726693d — stamped by freeze

### Contract

```
cmd_new_milestone tail, before print(_next_footer(...)):
    print("lane: single task? the oneshot lane is cheaper: add.py new-task <slug> --oneshot")
(v2: the `lane:` prefix — three persona-nudge suites pin `note:` as a counted one-per-invocation marker class on this exact output)
```

`Least-sure flag surfaced at freeze:` [spec] an always-on nudge may read as noise on genuinely multi-task milestones — why: the engine can't see intent; if wrong: one advisory line of noise, droppable later (cost: negligible; the r1 bait cost 9-10 calls)
Status: FROZEN @ v2 — approved by Tin Dang
### Build-strategy
Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/tooling/` `add-method/../.add/` `.add/tooling/` `add-method/.add/`
Strategy & known-problem fixes: red test -> one print line -> sync x3 + re-pin. Traps: footer-last; no banned slang in the literal.
Approach (domain strategy): obvious, correctness-first

### AI-verify record (required when gate_mode: ai-plan-verify)
- [x] §3 PLAN grounding anchors resolve in the current tree (cmd_new_milestone tail read this session)
- [x] §1 every Must + every Reject present, each Reject paired with an outcome
- [x] §3 Contract shape is concrete
- [x] Lowest-confidence flag surfaced and substantive (noise-on-multi-task tradeoff)
Verified by: claude-opus-4-8 (orchestrator, inline) · at: 2026-07-13T16:10:00Z

---

## 4 · TESTS — failing-first (red)

Plan: test_nudge_prints (new-milestone stdout carries the oneshot line) · test_footer_stays_last.
Tests live in: `add-method/tooling/test_milestone_lane_nudge.py` · MUST run red before Build.

---

## 5 · BUILD — AI writes the code (execution)

> The change plan was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope; improve on the strategy if the code teaches you better.
Strategy actually used: v2 after the fence named the collision the §1 flag predicted — three persona-nudge suites pin `note:` as a counted one-per-invocation marker class on new-milestone output; the advisory re-prefixed `lane:` (change request v1->v2), all three suites green.
Code lives in: `./src/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build (shared batch fence 3496/3496 OK; v2 change request re-froze §3 BEFORE the prefix edit)
- [x] green was EARNED — the tests read real new-milestone stdout; the three persona-nudge marker suites pin the counting semantics independently
- [x] input dialect held — no external input
- [x] no exposed secrets, injection openings, or unexpected dependencies (one advisory print)

Build expectations (from §1 Accept + §3 CONTRACT): every new-milestone success carries the lane advisory and still ends with the footer — confirmed by test_milestone_lane_nudge (2/2) + test_persona_fit_nudge/test_persona_milestone_nudge green.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-13

