# TASK: Competency Deltas

slug: competency-deltas · created: 2026-05-30 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

This task defines the **competency-delta shape** — the freeze-first seam that
`competency-driver-tagging`, `foundation-update-loop`, and `convergence-signal` all build on.
A delta is a single learning, tagged by which of the five competencies it improves, written in
a task's OBSERVE phase so the next loop can fold it into the foundation.

Must:
  - a competency delta is ONE line in this exact grammar:
    `- [<COMPETENCY> · <status>] <learning> (evidence: <pointer>)`
  - `<COMPETENCY>` is EXACTLY one of: `DDD` · `SDD` · `UDD` · `TDD` · `ADD` (the five competencies)
  - `<status>` is EXACTLY one of: `open` · `folded` · `rejected`; a newly emitted delta is `open`
  - every delta carries a NON-EMPTY `(evidence: …)` pointer — a failing scenario, a production
    signal, or a review note (no evidence → it is an opinion, not a delta)
  - each `TASK.md` OBSERVE section provides a `### Competency deltas` block to hold them, and the
    `add.py new-task` scaffold ships that empty block so every new task has the slot
  - a rubric `skill/add/deltas.md` tells the AI HOW to pick the right competency, what counts as
    evidence, and the status lifecycle (open → folded | rejected — who moves it, and when)
Reject (well-formedness codes the rubric names; no engine validator yet — the AI is first check):
  - missing or unknown competency tag -> "unknown_competency"
  - missing / empty evidence pointer  -> "no_evidence"
  - unknown status token              -> "unknown_status"
After:
  - a finished task's OBSERVE holds zero or more well-formed deltas, each parseable to EXACTLY one
    competency; new tasks scaffold with the empty `### Competency deltas` block already present.
Assumptions (confirm before building):
  - [x] the `·` middle-dot separator matches existing repo style (used throughout the docs) and is
        safe to parse — RESOLVED: yes, reuse it for visual consistency.
  - [x] existing done tasks are NOT retrofitted; the convention applies to new/future OBSERVE
        phases only — RESOLVED: yes, backward compatible (no churn on closed tasks).
  - [x] the parser/counter that READS deltas is OUT of scope here — RESOLVED: yes, deferred to
        `convergence-signal` per the v5 milestone (this task freezes the SHAPE, not the reader).

<!-- EXIT: every rule stated, every rejection has a named code, zero open assumptions. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: a well-formed delta parses to four fields
  Given the line "- [DDD · open] domain model missed tenancy (evidence: scenario_x failed)"
  When the frozen grammar is applied
  Then it yields competency=DDD, status=open, learning + a non-empty evidence pointer

Scenario: all five competencies are valid tags
  Given skill/add/deltas.md
  When I read the documented competency tags
  Then DDD, SDD, UDD, TDD, and ADD are each named as valid
  And no sixth competency tag is introduced

Scenario: the status lifecycle is documented
  Given skill/add/deltas.md
  When I read the status rules
  Then open, folded, and rejected are each defined, a new delta starts open,
       and who moves open → folded | rejected is stated

Scenario: a new task scaffolds with the deltas block
  Given add.py new-task creates a fresh TASK.md
  When I read its OBSERVE section
  Then a "### Competency deltas" block is present
  And the existing scaffold sections (1–7) are unchanged

Scenario: the rubric is byte-identical across both skill trees
  Given add-method/skill/add/deltas.md and .claude/skills/add/deltas.md
  When I compare their md5
  Then the two are identical
  And SKILL.md (both trees) links to deltas.md

Scenario: a delta with no/unknown competency is rejected
  Given a delta line whose tag is missing or not one of the five
  When the rubric's well-formedness rules are applied
  Then it is named "unknown_competency"
  And valid deltas are unaffected

Scenario: a delta with no evidence is rejected
  Given a delta line lacking a non-empty "(evidence: …)" pointer
  When the rubric's well-formedness rules are applied
  Then it is named "no_evidence"
  And valid deltas are unaffected

Scenario: a delta with an unknown status is rejected
  Given a delta line whose status is not open | folded | rejected
  When the rubric's well-formedness rules are applied
  Then it is named "unknown_status"
  And valid deltas are unaffected
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
DELTA GRAMMAR (frozen):  - [<COMPETENCY> · <status>] <learning> (evidence: <pointer>)
    <COMPETENCY> ∈ { DDD, SDD, UDD, TDD, ADD }          # exactly one of the five
    <status>     ∈ { open, folded, rejected }            # a newly emitted delta is `open`
    <pointer>    = non-empty text after "evidence:"       # required; no evidence → not a delta
  reject codes (rubric names them; no engine validator yet):
    unknown_competency · no_evidence · unknown_status

ARTIFACTS (method, no judgment in the engine):
  skill/add/deltas.md (NEW)  — the rubric. MUST contain: the grammar above; all 5 competencies,
    each with a one-line "what it covers"; the status lifecycle (new=open; the human moves
    open→folded when a delta is merged into PROJECT.md, open→rejected when declined); the 3
    reject codes; one worked example written in the frozen grammar.
  SKILL.md (both skill trees)  — a pointer to deltas.md in the loop/OBSERVE area.
  appendix-c-glossary.md (3 doc trees)  — a "Competency delta" entry.

SCAFFOLD (mechanical, in add.py):
  add.py new-task's TASK.md template gains, inside section 7 OBSERVE, a `### Competency deltas`
  block whose example is an HTML COMMENT (so a future parser never counts the template line as a
  real delta). Sections 1–7 otherwise unchanged; human-text output unchanged.

STRUCTURAL GUARD — tooling/test_competency_deltas.py — EXACTLY these 8 tests (frozen):
  1. deltas.md exists in BOTH skill trees and is md5-identical
  2. deltas.md documents all five competencies (DDD·SDD·UDD·TDD·ADD), no sixth
  3. deltas.md documents all three statuses AND states a new delta is `open`
  4. deltas.md documents all three reject codes (unknown_competency·no_evidence·unknown_status)
  5. deltas.md states the delta grammar (the bracketed-tag + (evidence:) shape)
  6. SKILL.md links deltas.md in both trees and the two SKILL.md are identical
  7. add.py new-task scaffold emits a `### Competency deltas` block in OBSERVE, example commented
  8. appendix-c-glossary.md has a "Competency delta" entry
```

Status: FROZEN @ v1   (human-approved 2026-05-30)   <!-- Changing a frozen contract = change request back to SPECIFY. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: structural — all 8 frozen invariants asserted (this is a method/docs task; the
unit of "coverage" is the contract surface, not LOC).
Plan (the 8 frozen tests, one assertion-cluster each):
  - test_deltas_md_exists_in_both_trees_with_md5_parity
  - test_documents_all_five_competencies
  - test_documents_all_three_statuses_and_new_is_open
  - test_documents_all_three_reject_codes
  - test_states_the_delta_grammar
  - test_skill_md_links_deltas_and_both_trees_identical
  - test_scaffold_emits_competency_deltas_block_commented_example
  - test_glossary_has_competency_delta_entry

Tests live in: `add-method/tooling/test_competency_deltas.py` (the suite is rooted there, like
test_scope_loop.py) · MUST run red (artifacts absent) before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): the scaffold's delta example MUST be an HTML comment, so a
future parser (convergence-signal) never counts a fresh task's template line as a real `open`
delta. No engine validator yet — the rubric's reject codes are the AI's self-check.
Code lives in: this is a method/docs task — artifacts are `skill/add/deltas.md`,
`tooling/templates/TASK.md.tmpl`, both `SKILL.md`, the 3 glossary trees, and the structural test.
Constraints: do NOT change any test or the contract; sync both skill trees + 3 doc trees + the
dogfood `.add/tooling` template (md5 parity); ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — 8/8 new GREEN; full suite 122 OK (was 114, +8, no regressions)
- [x] coverage did not decrease — all 8 frozen invariants asserted; proven RED first (4 fail + 4 err, artifact-absent)
- [x] no test or contract was altered during build — frozen 8-test list built to, not edited
- [x] concurrency / timing of the risky operation is safe — N/A (docs/method); the one failure-mode
      (parser counting the template example) is designed against: example is an HTML comment, verified
      end-to-end (scaffolded a throwaway task → block present, example commented)
- [x] no exposed secrets, injection openings, or unexpected dependencies — secret scan clean; no new deps
- [x] layering & dependencies follow CONVENTIONS.md — engine carries the SHAPE (scaffold slot) only;
      judgment (tagging, folding) lives in the method (deltas.md); Minimal pillar held (deltas live in
      already-loaded TASK.md, no new always-loaded doc); both skill trees + 3 glossary trees + dogfood
      `.add/tooling` template all md5-identical
- [ ] a person reviewed and approved the change — awaiting the human verify gate (owner=human; not self-signed)

Disclosed gap (does NOT block — regression-risk, not present-falsehood): test 7 guards the
CANONICAL template (`add-method/tooling/templates/TASK.md.tmpl`); the scaffold that actually runs
is the git-tracked dogfood copy `.add/tooling/templates/TASK.md.tmpl`. They are md5-identical NOW
(synced + e2e-verified this build), but no test guards that parity and no automated sync exists —
a future canonical edit could silently diverge. Same class as scope-loop's section-checklist note.
Out of scope to fix here (contract froze exactly 8 tests; a parity guard is a change-request /
follow-up). Captured as this task's own first competency delta in §7 OBSERVE.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-05-30   (parity gap disclosed above, accepted as a follow-up)

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): do future tasks actually fill this block with real deltas, or
leave the placeholder? (the first signal that the self-improving loop is alive vs. ceremonial.)
Spec delta for the next loop: the delta shape held under its own first use (this task dogfooded it).

### Competency deltas
This task is the first dogfood of its own mechanism — real deltas, not the placeholder:
- [ADD · folded] the dogfood `.add/tooling` template can silently diverge from the canonical `add-method` copy; no test guards the parity (evidence: md5 mismatch caught manually this build)
- [TDD · folded] structural tests guard canonical artifacts but not their git-tracked dogfood twins — 3rd recurrence of this gap class (evidence: scope-loop OBSERVE note + this build)
