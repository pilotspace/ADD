# TASK: Contract-freeze to autonomous-run handoff (scope-lock)

slug: scope-lock-trigger · created: 2026-06-01 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
autonomy: auto   <!-- v6 autonomy dial: conservative | auto. This run is the dogfood (auto). -->

> v6 · *DD driver: ADD. Owns the run.md spine: the trigger + the touch-boundary. Method-only (a rubric,
> not add.py). Other v6 tasks fill the remaining run.md sections.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

The seam where ADD hands off human->AI is the FROZEN contract. v6 makes the far side a dynamic run; this
task defines WHEN that run may start and WHAT it may touch — the safety frame everything else stands on.

Must:
  - the run's trigger is the **frozen contract** (§3 `FROZEN @ vN`) AND red §4 tests — nothing else
  - no frozen contract -> no run (starting earlier is the forward-skip the flow forbids)
  - a **touch-boundary**: the run MAY rewrite code (disposable), drive tests to green without weakening
    them, and gather evidence; it MUST NOT edit the frozen contract or locked scope, weaken/skip a test,
    or touch §1–§3 except to halt and escalate
  - a boundary breach is backward-correction: the run STOPS and hands to a human (principle 4), never
    re-locks scope itself
  - run.md is method-only (a rubric) and md5-identical across both skill trees; SKILL.md points to it
Reject:
  - a run proposed with no frozen contract            -> "unlocked_run" (forward-skip)
  - the run editing the frozen contract / locked scope -> "boundary_breach"
  - a test weakened to pass the build                  -> "test_weakened" (method inversion)
After:
  - run.md documents the trigger + boundary; both trees identical; SKILL.md links it.
Assumptions (confirm before building):
  - [x] the trigger is the existing frozen-contract seam, not a new engine state — RESOLVED (milestone).
  - [x] run.md is a rubric, not an add.py command — RESOLVED (engine stays judgment-free).

<!-- EXIT: every rule stated, every rejection has a named code, zero open assumptions. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: the run starts only on a frozen contract
  Given run.md
  When I read when the run begins
  Then it requires §3 FROZEN and red §4 tests, and states no frozen contract -> no run

Scenario: the touch-boundary is explicit
  Given run.md
  When I read what the run may and may not touch
  Then code is disposable (may rewrite); the frozen contract and locked scope are MUST NOT
  And weakening a test to pass is forbidden

Scenario: a breach stops and escalates
  Given run.md
  When the run hits a gap only the front can resolve
  Then it STOPS and hands back to a human (never re-locks scope)

Scenario: run.md is parity-synced and linked
  Given both skill trees
  When I compare run.md md5 and read SKILL.md
  Then run.md is identical in both trees and SKILL.md points to it
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
ARTIFACT: skill/add/run.md (NEW, both trees, md5-identical) — §"When the run begins" + §"The touch-boundary"
          SKILL.md (both trees) — a pointer to run.md
TRIGGER (frozen): run starts iff §3 FROZEN @ vN AND §4 tests RED. Else: no run.
BOUNDARY (frozen): MAY {rewrite code, drive tests green w/o weakening, gather evidence};
          MUST NOT {edit frozen contract or locked scope, weaken/skip a test, touch §1–§3 except to halt}.
          breach -> STOP + escalate to human (principle 4).
GUARD: add-method/tooling/test_v6_run.py — the scope-lock tests (parity, SKILL link, trigger, boundary).
  (test_v6_run.py grows one section per v6 task; this task owns the trigger + boundary assertions.)
reject codes: unlocked_run · boundary_breach · test_weakened
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit; originally self-gated at v6 dogfood — no human at the original seam)

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: structural — trigger + boundary invariants asserted in test_v6_run.py (+ shared parity/link).
Tests live in: `add-method/tooling/test_v6_run.py` · MUST run red (run.md absent) before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule: run.md is a RUBRIC — no add.py change; the engine cannot start a run on its own. Both skill
trees byte-identical; SKILL.md pointer added to both. Do NOT change the test or contract.
Code lives in: skill/add/run.md (×2 trees), SKILL.md (×2 trees).

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — scope-lock tests GREEN; full suite green (see run)
- [x] coverage did not decrease — trigger + boundary asserted; proven RED first (run.md absent)
- [x] no test or contract was altered during build — built to the frozen list
- [x] concurrency / timing — N/A (rubric); the risky op is the autonomous run itself, fenced by the boundary
- [x] no exposed secrets / injection / unexpected deps — docs only
- [x] layering & dependencies — method-only; engine untouched (no run command); both trees md5-identical
- [ ] a person reviewed and approved — **NO. Self-gated under the v6 dogfood; human review pending.**

BLIND-SPOT FINDING: run.md PROHIBITS the run from editing the frozen contract — yet this very dogfood
self-gated a FROZEN contract earlier (principle-reframe). The rubric I'm writing forbids what the run
executing it just did. The boundary is sound on paper; the dogfood already drove across it. → delta.

### GATE RECORD
Outcome: PASS  (provisional — automated evidence only)
Reviewed by: AI self-gate (v6 dogfood) — NOT human-verified · date: 2026-06-01

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): run.md md5 parity; whether a later task's run violates its own boundary.
Spec delta for the next loop: the touch-boundary needs a runtime ENFORCER (CI check), not just prose — a rubric the run can ignore is not a guardrail.

### Competency deltas
- [ADD · folded] the run's touch-boundary is prose-only; nothing MECHANICALLY stops a run from editing a frozen contract — the dogfood already did exactly that (evidence: principle-reframe self-gated a FROZEN contract; this rubric forbids it)
- [SDD · folded] "no frozen contract -> no run" is unenforceable while the run and the gate are the same agent — the trigger is self-asserted (evidence: scope-lock-trigger has no human between freeze and run)
