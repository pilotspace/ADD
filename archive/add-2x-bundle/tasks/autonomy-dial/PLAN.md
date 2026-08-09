# TASK: The autonomy dial: per-scope auto-gate setting

slug: autonomy-dial · created: 2026-06-01 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
autonomy: auto   <!-- v6 dial: dogfood (this very task ran at auto) -->

> v6 · *DD driver: ADD. Owns run.md §"The autonomy dial". Lightest task; the safety valve on the auto-gate.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md
How much a run may auto-gate is a per-scope SETTING, not a global switch (principle 5: trust earned per scope).
Must:
  - a task declares its level in its TASK.md header: `autonomy: conservative | auto`
  - **conservative is the DEFAULT** — run does the work + converges but STOPS at verify for a human (auto-PASS off)
  - **auto** — run may auto-PASS when evidence + residue checks hold; security still always escalates
  - raising to `auto` is deliberate + recorded for a low-risk well-tested scope; lowerable anytime
  - the dial is a **rubric convention** read by human + run; **NOT an add.py flag** (engine stays judgment-free)
Reject:
  - auto as the global/implicit default          -> "auto_by_default" (violates principle 5; conservative is default)
  - making the dial an add.py flag/state field   -> "engine_judgment" (the engine must not decide autonomy)
After: run.md §"The autonomy dial" documents the per-scope setting, conservative default, rubric-not-engine.

<!-- EXIT: rules stated, rejections named, no open assumptions. -->

---

## 2 · SCENARIOS ▸ docs/04-step-2-scenarios.md
```gherkin
Scenario: the dial is per-scope with a conservative default
  Given run.md
  Then `autonomy: conservative | auto` is a TASK.md header and conservative is the default
Scenario: the dial is a convention, not an engine flag
  Given run.md
  Then it states the dial is NOT an add.py flag (engine stays judgment-free)
```
<!-- EXIT: one scenario per Must/Reject; observable. -->

---

## 3 · CONTRACT ▸ docs/05-step-3-contract.md
```
ARTIFACT: run.md §"The autonomy dial" (both trees, md5-identical)
FROZEN: `autonomy: conservative | auto` TASK.md header; conservative=default (auto-PASS off, stop for human);
        auto=may auto-PASS (security still escalates); rubric convention, NOT an add.py flag.
GUARD: test_v6_run.py::test_autonomy_dial_per_scope
reject codes: auto_by_default · engine_judgment
```
Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit; originally self-gated at v6 dogfood — no human at the original seam)
<!-- EXIT: frozen + rejections answered + glossary names. -->

---

## 4 · TESTS ▸ docs/06-step-4-tests.md
Structural — test_v6_run.py asserts the `autonomy:` setting + conservative-default + not-an-add.py-flag. RED first.
<!-- EXIT: one test per scenario; red first. -->

---

## 5 · BUILD ▸ docs/07-step-5-build.md
Rubric prose in run.md (both trees byte-identical). No add.py change. No test/contract edits.
<!-- EXIT: green; no test/contract touched. -->

---

## 6 · VERIFY ▸ docs/08-step-6-verify.md
- [x] all tests pass — test_v6_run 8/8 green; full suite 147 OK
- [x] coverage held — dial + default + rubric-not-engine asserted; proven RED first
- [x] no test/contract altered; no secrets/deps; both trees md5-identical
- [ ] a person reviewed — **NO. Self-gated (v6 dogfood).**

BLIND-SPOT FINDING: the dial's DEFAULT is `conservative` (stop for a human) — yet every v6 task set
`autonomy: auto` and self-gated. The dogfood ran the entire milestone at the NON-default, most-permissive
setting on the highest-stakes scope (defining the method itself) — the exact inversion of principle 5,
which says raise autonomy only on low-risk, well-tested scope. The dial is sound; the dogfood maxed it
where it should have been lowest. → delta.

### GATE RECORD
Outcome: PASS  (provisional — automated evidence only)
Reviewed by: AI self-gate (v6 dogfood) — NOT human-verified · date: 2026-06-01
<!-- security = HARD-STOP; one outcome. -->

---

## 7 · OBSERVE ▸ docs/09-the-loop.md
Watch: whether real tasks default to conservative or drift to auto.
Spec delta: the dial needs a RISK input — `auto` should be refused (or warn) on a high-risk/method-defining scope, not just available; principle 5 ties autonomy to risk, the dial currently only to choice.

### Competency deltas
- [ADD · folded] the dogfood ran the WHOLE milestone at `auto` on the riskiest possible scope (the method itself), inverting principle 5 (autonomy ∝ low risk) — the dial allows a choice the principle would forbid (evidence: all 6 v6 tasks header `autonomy: auto`; all self-gated)
- [UDD · folded] the dial has no signal of "you are about to auto-gate a high-risk scope" — the human/run get no friction at exactly the moment friction matters (evidence: no warning surfaced during this run)
  [folded foundation-version 8 → PROJECT.md §Spec OPEN "high-risk-auto friction signal" (deferred feature)]
- [TDD · folded] nothing tests that conservative is actually ENFORCED as default — test asserts the prose says so, not that a run with no header stops for a human (evidence: test_autonomy_dial_per_scope checks strings)
