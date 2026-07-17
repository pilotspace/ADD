# TASK: run.md: fan-out build->verify with in-run convergence

slug: dynamic-run-engine · created: 2026-06-01 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
autonomy: auto   <!-- v6 dial: dogfood -->

> v6 · *DD driver: ADD. Owns run.md §"The dynamic run". Lean TASK.md — the substance is the rubric prose.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md
Once the run starts (scope-lock-trigger), it fans out the independent build work and converges before
the gate, instead of one linear pass.
Must:
  - run.md describes **fan-out** of independent work (build attempts, fix loops, checks)
  - run.md documents three convergence loops: **loop-until-dry**, **adversarial verify**, **completeness-critic**
  - the run ends only when the loops are dry AND the gate's evidence holds (convergence before gate)
  - it is self-improving WITHIN the turn (same convergence the foundation loop runs across milestones)
Reject:
  - stopping at first green (no loop-until-dry)        -> "premature_green"
  - a "done" claim with no adversarial refutation pass -> "unrefuted_claim"
After: run.md §"The dynamic run" documents fan-out + the 3 loops; guarded by test_v6_run.

<!-- EXIT: rules stated, rejections named, no open assumptions. -->

---

## 2 · SCENARIOS ▸ docs/04-step-2-scenarios.md
```gherkin
Scenario: the run fans out and converges
  Given run.md §"The dynamic run"
  Then it documents fan-out and the loops loop-until-dry, adversarial verify, completeness-critic
Scenario: convergence precedes the gate
  Given run.md
  Then the run ends only when the loops are dry AND the evidence holds
```
<!-- EXIT: one scenario per Must/Reject; observable. -->

---

## 3 · CONTRACT ▸ docs/05-step-3-contract.md
```
ARTIFACT: run.md §"The dynamic run — fan-out and in-run convergence" (both trees, md5-identical)
FROZEN: fan-out + {loop-until-dry · adversarial verify · completeness-critic}; loops-dry AND evidence -> end.
GUARD: test_v6_run.py::test_dynamic_run_fanout_and_convergence
```
Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit; originally self-gated at v6 dogfood — no human at the original seam)
<!-- EXIT: frozen + rejections answered + glossary names. -->

---

## 4 · TESTS ▸ docs/06-step-4-tests.md
Structural — test_v6_run.py asserts fan-out + the 3 named loops. Ran RED (section absent) before Build.
<!-- EXIT: one test per scenario; red first. -->

---

## 5 · BUILD ▸ docs/07-step-5-build.md
Rubric prose in run.md (both trees byte-identical). No add.py change. No test/contract edits.
<!-- EXIT: green; no test/contract touched. -->

---

## 6 · VERIFY ▸ docs/08-step-6-verify.md
- [x] all tests pass — test_v6_run 8/8 green; full suite 147 OK
- [x] coverage held — fan-out + 3 loops asserted; proven RED first
- [x] no test/contract altered; concurrency N/A (rubric); no secrets/deps; both trees md5-identical
- [ ] a person reviewed — **NO. Self-gated (v6 dogfood).**

BLIND-SPOT FINDING: run.md PRESCRIBES fan-out + adversarial verify, but THIS dogfood run executed the
build sequentially and single-pass — I did not actually fan out or spawn skeptics. The rubric describes
a run richer than the run that wrote it. Words describe a capability the execution didn't use. → delta.

### GATE RECORD
Outcome: PASS  (provisional — automated evidence only)
Reviewed by: AI self-gate (v6 dogfood) — NOT human-verified · date: 2026-06-01
<!-- security = HARD-STOP; one outcome. -->

---

## 7 · OBSERVE ▸ docs/09-the-loop.md
Watch: whether any real run actually fans out vs. executes linearly.
Spec delta: run.md should mark which loops are MANDATORY vs. optional-by-scope — an all-or-nothing run is rarely right.

### Competency deltas
- [ADD · folded] the rubric prescribes fan-out + adversarial verify, but the dogfood that authored it ran sequential single-pass — prescribed > practiced (evidence: this turn's build had no parallel agents, no skeptic pass)
  [folded foundation-version 8 → reinforces CONVENTIONS.md "Words-exist ≠ method-works" (prescribed > practiced)]
- [TDD · folded] test_v6_run asserts the loop NAMES exist in prose, not that a run performs them — the hardest property (does it converge?) is unguarded (evidence: test_dynamic_run_fanout_and_convergence checks strings only)
