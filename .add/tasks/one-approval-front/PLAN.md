# TASK: Compress the front to one approval at the contract-freeze seam

slug: one-approval-front · created: 2026-06-01 · stage: mvp · depends-on: auto-default-dial
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done · PASS: conservative scope, human diff review complete (Tin Dang, 2026-06-02) -->
autonomy: conservative   <!-- method/trust-layer edit = high-risk scope -> conservative (the v7 guard, self-applied) -->

> v7 · *DD driver: ADD. Owns run.md §"The one-approval front". Reduces the human-led front to ONE gate.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md
The human-led front compresses from three approvals (Specify·Scenarios·Contract) to ONE.
Must:
  - the AI **drafts the whole front as one bundle** (Spec + Scenarios + Contract + Tests) from user input
  - the human gives **ONE approval, at the frozen contract** (the seam) — that approval starts the run
  - the AI **never freezes its own contract** — the seam stays human (this keeps "never self-gate a human-led gate")
  - rejecting any part = backward-correction (principle 4), the bundle returns to draft
Reject:
  - zero human approval / AI self-freezes the seam -> "self_frozen_seam" (removes the last human checkpoint)
After: run.md §"The one-approval front" documents draft-bundle -> single human approval at the seam -> auto run.
Assumptions (confirm before building):
  - [x] human chose "One batched approval at contract-freeze" over spec-only/two-approval (AskUserQuestion)

<!-- EXIT: every rule stated, every rejection has a named code, zero open assumptions. -->

---

## 2 · SCENARIOS ▸ docs/04-step-2-scenarios.md
```gherkin
Scenario: the front is one approval at the seam
  Given run.md
  Then it documents a single human approval AT the frozen contract, and the AI drafting the front bundle
Scenario: the seam stays human
  Given run.md
  Then the AI never freezes its own contract; a person approves the frozen shape before any auto-run
```
<!-- EXIT: one scenario per Must/Reject; observable. -->

---

## 3 · CONTRACT ▸ docs/05-step-3-contract.md
```
ARTIFACT: run.md §"The one-approval front" + the intro front sentence (both skill trees, md5-identical)
FROZEN: AI drafts Spec+Scenarios+Contract+Tests as one bundle; human gives ONE approval at the frozen
        contract (the seam); seam stays human (AI never self-freezes); reject any part = backward-correction.
GUARD: test_v7_auto_default.py::test_one_approval_front_at_the_seam
reject codes: self_frozen_seam
```
Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit) · (HUMAN-approved at the seam — AskUserQuestion "One batched approval at contract-freeze")
<!-- EXIT: frozen + rejections answered + glossary names. -->

---

## 4 · TESTS ▸ docs/06-step-4-tests.md
Structural — test_v7 asserts run.md names the single approval, ties it to the contract-freeze seam, and
says the AI drafts the bundle. RED first (run.md had no one-approval-front section).
<!-- EXIT: one test per scenario; red first. -->

---

## 5 · BUILD ▸ docs/07-step-5-build.md
Rubric prose: new run.md §"The one-approval front" + updated intro sentence. Both skill trees synced
byte-identical via cp. No add.py change; no test/contract edit after freeze.
<!-- EXIT: green; no test/contract touched. -->

---

## 6 · VERIFY ▸ docs/08-step-6-verify.md
- [x] all tests pass — full suite 154 OK
- [x] coverage held — one-approval + seam-stays-human asserted; proven RED first
- [x] no test weakened; both skill trees md5-identical
- [x] **a person reviewed the IMPLEMENTATION** — YES. Tin Dang reviewed the built diff (run.md
      §"The one-approval front" + the updated intro sentence) at the verify gate and recorded PASS.
      `conservative` scope review complete; the seam stays human as specified.

### GATE RECORD
Outcome: PASS — human-reviewed (conservative-scope diff review completed at verify)
Direction approved by: Tin Dang (human, AskUserQuestion). Implementation reviewed by: Tin Dang (human, diff review at verify). date: 2026-06-02
<!-- security = HARD-STOP; one outcome. Do NOT record PASS until a human reviews the diff (conservative scope). -->

---

## 7 · OBSERVE ▸ docs/09-the-loop.md
Watch: whether one batched approval at the seam loses edge-case coverage that three separate gates
(Specify, Scenarios, Contract) used to catch — does compressing the front cost direction quality?
Spec delta: may need a lightweight "front checklist" the human ticks at the single approval so the
compression does not silently drop scenario/edge review.

### Competency deltas
- [UDD · folded] one approval may rush the human past Scenarios/Contract review they'd have done separately — the seam needs a surfaced checklist so the single gate stays a real gate, not a rubber stamp (evidence: design-level risk, unobserved in real use yet)
  [folded foundation-version 8 → PROJECT.md §Spec OPEN "one-approval review checklist" (deferred feature)]
- [ADD · folded] "seam stays human" is prose — nothing prevents an over-eager run from drafting AND treating the contract as frozen without a recorded human approval (evidence: no add.py gate records the seam approval distinctly from verify)
  [folded foundation-version 8 → reinforces CONVENTIONS.md "Never self-gate a human-led gate"]
