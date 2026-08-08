# TASK: Run findings become open competency deltas (v6 run -> v5 fold)

slug: run-emits-deltas · created: 2026-06-01 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
autonomy: auto   <!-- v6 dial: dogfood -->

> v6 · *DD driver: ADD. Owns run.md §"Emitting deltas". Wires the v6 run into v5's human-gated fold.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md
The run's completeness-critic must not discard what it finds. Findings become `open` competency deltas
in OBSERVE (deltas.md grammar), which feed v5's human-gated fold (fold.md). The run emits; the human folds.
Must:
  - the completeness-critic's findings become **`open` competency deltas** in the task OBSERVE block
  - both kinds emit: a finding the run FIXED but that taught the foundation; a residue it could NOT fix
  - deltas route to v5's fold (fold.md) at milestone close — **run emits `open`; human folds** (no self-fold)
  - the loop closes: **v6 run -> v5 foundation** (findings compound, not evaporate)
Reject:
  - run findings discarded at end-of-run            -> "lost_findings"
  - the run folding its own deltas                  -> "self_fold" (v5 rule: folding is human judgment)
After: run.md §"Emitting deltas" documents open-delta emission + human-gated fold routing.

<!-- EXIT: rules stated, rejections named, no open assumptions. -->

---

## 2 · SCENARIOS ▸ docs/04-step-2-scenarios.md
```gherkin
Scenario: findings become open deltas
  Given run.md
  Then the completeness-critic's findings become open competency deltas in OBSERVE
Scenario: human folds, run never self-folds
  Given run.md
  Then deltas route to fold.md and the run emits open while the human folds
```
<!-- EXIT: one scenario per Must/Reject; observable. -->

---

## 3 · CONTRACT ▸ docs/05-step-3-contract.md
```
ARTIFACT: run.md §"Emitting deltas — feeding the foundation back" (both trees, md5-identical)
FROZEN: critic findings -> open competency deltas (deltas.md grammar) in OBSERVE;
        route to v5 fold (fold.md), human-gated; run emits open, never self-folds; v6 run -> v5 foundation.
GUARD: test_v6_run.py::test_run_emits_open_deltas
reject codes: lost_findings · self_fold
```
Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit; originally self-gated at v6 dogfood — no human at the original seam)
<!-- EXIT: frozen + rejections answered + glossary names. -->

---

## 4 · TESTS ▸ docs/06-step-4-tests.md
Structural — test_v6_run.py asserts open-delta emission + critic source + fold routing. RED first.
<!-- EXIT: one test per scenario; red first. -->

---

## 5 · BUILD ▸ docs/07-step-5-build.md
Rubric prose in run.md (both trees byte-identical). No add.py change. No test/contract edits.
<!-- EXIT: green; no test/contract touched. -->

---

## 6 · VERIFY ▸ docs/08-step-6-verify.md
- [x] all tests pass — test_v6_run 8/8 green; full suite 147 OK
- [x] coverage held — emission + fold routing asserted; proven RED first
- [x] no test/contract altered; no secrets/deps; both trees md5-identical
- [x] this task's mechanism is the one part of the dogfood working as designed — every v6 task DID emit
      honest open deltas (12+ across the run), feeding v5's fold
- [ ] a person reviewed — **NO. Self-gated (v6 dogfood).**

BLIND-SPOT FINDING: this is the most-honored rule of v6 — the run really did emit deltas. But it means
the deltas now PILED UP `open` with no fold, and the only fold ritual (v5 fold.md) is human-gated — which
the dogfood explicitly did NOT do (we self-gate, but do not self-fold, correctly). So v6's output is a
backlog of open deltas that a human MUST process. That is the loop working — but it is unfinished. → delta.

### GATE RECORD
Outcome: PASS  (provisional — automated evidence only)
Reviewed by: AI self-gate (v6 dogfood) — NOT human-verified · date: 2026-06-01
<!-- security = HARD-STOP; one outcome. -->

---

## 7 · OBSERVE ▸ docs/09-the-loop.md
Watch: the open-delta count across v6 tasks; whether the human runs the fold.
Spec delta: a dynamic run that emits deltas should also surface a "deltas pending fold" count at milestone close (convergence-signal, v5) — emission without a visible backlog invites the deltas to rot.

### Competency deltas
- [ADD · folded] v6 emitted 12+ open deltas but provides NO automated nudge to fold them — emission and folding are decoupled, so a fast run can outproduce the human fold capacity (evidence: this v6 run left every task's deltas open; no fold occurred)
  [folded foundation-version 8 → PROJECT.md §Spec OPEN "automated fold-nudge" (deferred feature)]
- [SDD · folded] the v6/v5 seam works only if the human actually folds — v6 makes the RUN faster but the FOLD is still the human bottleneck (principle 6 in a new place) (evidence: open-delta backlog from this run)
