# TASK: Flip the autonomy default to auto, guard high-risk scope

slug: auto-default-dial · created: 2026-06-01 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done · PASS: conservative scope, human diff review complete (Tin Dang, 2026-06-02) -->
autonomy: conservative   <!-- v7 dial: this task edits the method/trust-layer = high-risk scope -> MUST be conservative (the new guard, applied to itself) -->

> v7 · *DD driver: ADD. Owns run.md §"The autonomy dial" + book principle 5 reframe. Reverses v6.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md
The per-scope autonomy default flips `conservative` -> `auto` (human-directed reversal of v6).
Must:
  - run.md §"The autonomy dial" states **`auto` is the default**; `conservative` is the deliberate lowering
  - the dial stays **per-scope** (principle 5 intact) and a **rubric**, NOT an `add.py` flag
  - a **high-risk / method-defining scope must lower to `conservative`** — `auto` there is rejected
  - **security stays HARD-STOP**, always; book principle 5 reframed to "start auto, lower on risk"
Reject:
  - leaving `auto` on a high-risk/method-defining scope -> "unguarded_high_risk_auto" (autonomy ∝ low risk)
  - making the dial an `add.py` flag/state field       -> "engine_judgment" (engine stays judgment-free)
After: run.md + principle 5 + governance default say auto-by-default with the high-risk guard; `auto_by_default` retired.
Assumptions (confirm before building):
  - [x] human confirmed the reversal with the contradiction visible (AskUserQuestion: "Flip the global default to auto")

<!-- EXIT: rules stated, rejections named, no open assumptions. -->

---

## 2 · SCENARIOS ▸ docs/04-step-2-scenarios.md
```gherkin
Scenario: auto is the default
  Given run.md
  Then `autonomy: auto | conservative` is the header and auto is named the default; `auto_by_default` is gone
Scenario: high-risk scope is guarded
  Given run.md
  Then a high-risk / method-defining scope must lower to conservative, named `unguarded_high_risk_auto`
Scenario: principle 5 still per-scope
  Given docs/01-principles.md
  Then principle 5 reads "start auto, lower on risk" AND keeps trust earned per scope; security HARD-STOP intact
```
<!-- EXIT: one scenario per Must/Reject; observable. -->

---

## 3 · CONTRACT ▸ docs/05-step-3-contract.md
```
ARTIFACT: run.md §"The autonomy dial" (both skill trees, md5-identical) + docs/01-principles.md (3 trees)
FROZEN: `autonomy: auto | conservative` header; auto=default; conservative=deliberate lowering;
        high-risk/method-defining MUST lower (reject `unguarded_high_risk_auto`); rubric not add.py flag;
        security always HARD-STOP. `auto_by_default` retired.
GUARD: test_v7_auto_default.py (auto-default · per-scope · high-risk guard · principle reframe · security)
        + test_v6_run.py::test_autonomy_dial_per_scope (updated to the v7 reality)
reject codes: unguarded_high_risk_auto · engine_judgment
```
Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit) · (HUMAN-approved at the seam — AskUserQuestion, two forks confirmed — NOT self-gated)
<!-- EXIT: frozen + rejections answered + glossary names. -->

---

## 4 · TESTS ▸ docs/06-step-4-tests.md
Structural — test_v7_auto_default.py asserts auto-default + retired reject code + high-risk guard +
per-scope + security HARD-STOP + principle reframe across trees. RED first (run.md still said conservative).
<!-- EXIT: one test per scenario; red first. -->

---

## 5 · BUILD ▸ docs/07-step-5-build.md
Rubric prose: run.md §dial rewritten; one-approval intro updated (front task owns the section); book
principle 5 reframed; governance default note. All trees synced byte-identical via cp. No add.py change.
<!-- EXIT: green; no test/contract touched. -->

---

## 6 · VERIFY ▸ docs/08-step-6-verify.md
- [x] all tests pass — full suite 154 OK (test_v7 7/7 + test_v6 8/8 green)
- [x] coverage held — auto-default · high-risk guard · per-scope · security · reframe all asserted; proven RED first
- [x] no test weakened; all doc trees md5-identical (run.md ×2; principles ×3; governance ×3)
- [x] no secrets/deps; engine untouched (dial stays a rubric)
- [x] **a person reviewed the IMPLEMENTATION** — YES. Tin Dang reviewed the built diff (run.md §dial +
      §one-approval front, principle-5 reframe, new reject codes) at the verify gate and recorded PASS.
      Caveat accepted: the high-risk guard is PROSE, not engine-enforced — the enforcer is the next task
      (open delta + OBSERVE spec-delta below), not a blocker for a method-doc deliverable.

### GATE RECORD
Outcome: PASS — human-reviewed (conservative-scope diff review completed at verify)
Direction approved by: Tin Dang (human, AskUserQuestion). Implementation reviewed by: Tin Dang (human, diff review at verify). date: 2026-06-02
<!-- security = HARD-STOP; one outcome. Do NOT record PASS until a human reviews the diff (conservative scope). -->

---

## 7 · OBSERVE ▸ docs/09-the-loop.md
Watch: whether ordinary tasks actually start at `auto` and high-risk ones get lowered — or whether the
prose guard is ignored because nothing enforces it.
Spec delta: the high-risk guard needs an ENFORCER (a CI check / add.py warning) — prose alone is the
same words-exist≠method-works gap v6 hit; this task itself ran at `autonomy: conservative` (it is method-editing).

### Competency deltas
- [ADD · folded] the high-risk guard `unguarded_high_risk_auto` is prose, not enforcement — nothing stops a high-risk scope staying at `auto` (evidence: no add.py/CI check; relies on the human/run reading run.md)
  [folded foundation-version 8 → reinforces CONVENTIONS.md "Never self-gate a human-led gate" (prose≠enforcement)]
- [TDD · folded] tests assert the dial's WORDS, not that a header-less or high-risk run actually behaves — words-exist≠method-works recurs from v6 (evidence: test_v7 is structural string-matching)
  [folded foundation-version 8 → reinforces CONVENTIONS.md "Words-exist ≠ method-works"]
- [SDD · folded] v7 reverses a foundation-v2 learning by human direction but is itself NOT yet validated in a real (non-method) project — the auto default is unproven outside the dogfood (evidence: only this milestone uses it)
  [folded foundation-version 8 → reinforces PROJECT.md §Spec "v6/v7 NOT human-validated outside dogfood"]
