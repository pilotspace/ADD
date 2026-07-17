# TASK: Lift co-specify brainstorm to milestone and foundation altitudes

slug: cospecify-lift · created: 2026-06-03 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Lift co-specify (the brainstorm move) from task §1 up to the milestone (scope.md) and
  foundation (0-setup.md) altitudes — so the AI elicits before drafting at every altitude, not just inside a task.
Framings weighed: lift the existing co-specify three-move (chosen) · invent a parallel elicitation rubric · one shared block in SKILL.md referenced by both guides.
Must:
  - scope.md gains a "## Brainstorm before you draft — co-specify at milestone altitude" section placed
    immediately BEFORE "## Drafting a good MILESTONE.md", carrying a compact Diverge→Converge→Validate
    plus five diverge seeds (Outcome · Edge of scope · Riskiest seam · Done-looks-like · First slice).
  - phases/0-setup.md gains a "### Brainstorm the foundation before you fill it — co-specify at foundation altitude"
    subsection INSIDE step 2 (after the survivor-file list), carrying a four-lens question table (DDD · SDD · UDD · Decisions).
  - Both blocks reference `phases/1-specify.md` as the single source of the three-move AND restate it compactly
    (progressive disclosure: each guide is loaded alone, so it must be self-contained).
  - Both use the flag grammar VERBATIM from 1-specify.md: `⚠ <assumption> — least sure because <why>; if wrong: <cost>`.
  - The change lands in all THREE trees and leaves them byte-identical: canonical `add-method/skill/add/`,
    the regenerated `add-method/src/add_method/_bundled/skill/add/`, and the local `.claude/skills/add/` dogfood install.
Reject:
  - a new or divergent least-sure notation -> "flag_grammar_drift"
  - the block living only in SKILL.md instead of self-contained in each guide -> "breaks_progressive_disclosure"
  - an insertion that balloons past ~16 lines / turns into a manual -> "doc_bloat"
  - trees left out of sync (canonical ≠ bundled ≠ local) -> "tree_drift"
After:
  - An AI loading scope.md or 0-setup.md alone is told to elicit (diverge) before drafting, draft the whole
    artifact (converge), and show least-sure flags first (validate) — the same move it already runs at task §1.
Assumptions — least-sure first:
  ⚠ the rubric belongs as added guidance inside BOTH existing guides rather than one shared SKILL.md block — least sure because it trades a little cross-file repetition for self-containment under progressive disclosure; if wrong: minor doc duplication to refactor later (cheap, reversible).
  - [ ] placing the milestone block right before "## Drafting a good MILESTONE.md" reads in the right order (classify → brainstorm → draft) — confirm.
  - [ ] the local `.claude/skills/add` mirror should track canonical for dogfood parity — they are byte-identical today.

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: scope.md teaches diverge-before-draft
  Given canonical add-method/skill/add/scope.md
  Then it carries a "co-specify at milestone altitude" brainstorm section before "## Drafting a good MILESTONE.md"
  And that section lists the five diverge seeds and references phases/1-specify.md

Scenario: 0-setup.md teaches the four-lens foundation interview
  Given canonical add-method/skill/add/phases/0-setup.md
  Then it carries a "co-specify at foundation altitude" subsection with a four-lens table (DDD · SDD · UDD · Decisions)
  And the subsection sits inside step 2 (after the survivor-file list)

Scenario: flag grammar matches the task layer (reject flag_grammar_drift)
  Given both edited guides
  Then each contains the verbatim flag grammar "⚠ <assumption> — least sure because <why>; if wrong: <cost>"
  And neither introduces a different least-sure notation

Scenario: trees stay byte-identical (reject tree_drift)
  Given the canonical, _bundled, and local .claude copies of both files
  When prepare_bundle.py regenerates the bundle
  Then all three copies of each file are byte-identical
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

This is a prose-guide task, so the contract is the EXACT insertion text + placement anchors + target trees.

```
TARGET TREES (edit canonical, mirror local, regenerate bundle — all three end byte-identical):
  1. add-method/skill/add/{scope.md, phases/0-setup.md}                      (canonical source)
  2. .claude/skills/add/{scope.md, phases/0-setup.md}                        (local dogfood mirror)
  3. add-method/src/add_method/_bundled/skill/add/{...}                      (regenerated via scripts/prepare_bundle.py)

INSERT A — scope.md, immediately BEFORE the line "## Drafting a good MILESTONE.md":
  ## Brainstorm before you draft — co-specify at milestone altitude
  <intro: don't draft from thin input; run the same three-move co-specify as task §1
   (phases/1-specify.md) — Diverge (framings + open questions) → Converge (draft + rank)
   → Validate (show flags first) — raised to milestone scope; ask only what moves the
   goal/In-Out/task-list; draft the WHOLE milestone before showing; nothing hits disk
   until the human confirms.>
  Diverge seeds (pick the live ones):
    - Outcome        — done means a user can do *what* they can't today?  (goal sentence)
    - Edge of scope  — nearest thing assumed IN that you want OUT?         (Out list)
    - Riskiest seam  — which contract, if wrong, costs the most rework?    (freeze-first)
    - Done-looks-like— how do we SEE each outcome without reading code?    (exit criteria)
    - First slice    — which task unblocks the rest?                       (breadth-first order)
  <closer: rank assumptions least-sure first; the top 1–2 get the flag the human reads at confirm:>
    ⚠ <assumption> — least sure because <why>; if wrong: <cost>

INSERT B — phases/0-setup.md, INSIDE step 2, after the survivor-file list, before step 3:
  ### Brainstorm the foundation before you fill it — co-specify at foundation altitude
  <intro: PROJECT.md is read first by every loop; run the same co-specify move as task §1
   across four lenses — ask the load-bearing question per lens (diverge), draft the whole
   file (converge), show it with the least-sure flag first (validate); keep it one screen.>
  | Lens          | The one question that unblocks the section |
  | Domain (DDD)  | The 3–5 core nouns, and the one invariant that must NEVER break? |
  | Spec (SDD)    | The first milestone's outcome — and what's explicitly NOT in v1? |
  | Users (UDD)   | The primary user and the one job they hire this for? (or "no UI — surface is X") |
  | Decisions     | What's already decided that you'd regret re-litigating? (first Key Decision row) |
  <closer: ask only the live ones; rank what you're least sure of; top flag the human reads at confirm:>
    ⚠ <assumption> — least sure because <why>; if wrong: <cost>

Final rendered wording is the two revised drafts already shown to and approved by the human.
```

Status: FROZEN @ v1   <!-- approved 2026-06-03 via one-approval-front; gate-test home = shipped tooling/. Changing a frozen contract = change request back to SPECIFY. -->
<!-- The freeze IS the one approval. Lead it with the bundle's least-sure flag: the 1–2 points
     most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], with why + cost.
     The §1 ⚠ assumptions are its first feeder; a flag may point at a scenario or the contract too. See run.md. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: n/a (prose-guide task) — the gate is "required content present + trees identical", asserted by a test that is RED before the edits.

Plan (one assertion per scenario; assert observable file content, not wording):
  - test_scope_has_milestone_brainstorm: canonical scope.md contains "co-specify at milestone altitude",
    that heading appears BEFORE "## Drafting a good MILESTONE.md", and the five seed labels are present
    (Outcome · Edge of scope · Riskiest seam · Done-looks-like · First slice). [← scenario 1]
  - test_setup_has_foundation_interview: canonical phases/0-setup.md contains "co-specify at foundation altitude"
    and the four lens rows (Domain (DDD) · Spec (SDD) · Users (UDD) · Decisions). [← scenario 2]
  - test_flag_grammar_consistent: BOTH guides contain the verbatim flag string
    "⚠ <assumption> — least sure because <why>; if wrong: <cost>". [← scenario 3]
  - test_trees_identical: for each of the two files, the local .claude copy and the _bundled copy each
    equal the canonical copy byte-for-byte. [← scenario 4]
  - parity backstop: the existing add-method/tooling/test_bundle_parity.py stays green after prepare_bundle.py.

Tests live in: `add-method/tooling/test_cospecify_lift.py` (discovered by `python3 -m unittest discover -s tooling`).
MUST run red (content absent / trees not yet synced) before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): edit the CANONICAL tree, mirror to local, regenerate the bundle via
  scripts/prepare_bundle.py — never hand-edit _bundled/ (the parity guard owns it). All three trees end identical.
Code lives in: the two guide files (canonical `add-method/skill/add/`) + the gate test in `add-method/tooling/`.
Constraints: do NOT change any test or the frozen contract; no new dependencies (stdlib unittest only); ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — cospecify-lift 9/9 + parity 7/7; full suite **243 OK**
- [x] coverage did not decrease — additive guide content + one new test file; nothing removed
- [x] no test or contract was altered during build — frozen §3 honored; gate test written in TESTS, untouched in BUILD
- [x] concurrency / timing — n/a (static prose + a read-only assertion test; no IO, no shared state)
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib `unittest`/`pathlib` only
- [x] layering & dependencies follow CONVENTIONS.md — canonical→mirror→regenerate; no hand-edit of _bundled/
- [x] all four rejects held: no flag_grammar_drift (verbatim flag, test-asserted) · no breaks_progressive_disclosure
      (block is self-contained in each guide) · no doc_bloat (18 / 19-line inserts) · no tree_drift (3 trees byte-identical)
- [x] a person reviewed and approved the change — Tin Dang, 2026-06-03 (reviewed both rendered diffs)

Deviation (human-directed, at verify): §3 froze the 0-setup block "inside step 2"; on review it was
moved to a top-level `###` after the Do list (cleaner table render) with a one-line pointer left in
step 2. Placement-only — the guarded invariant (anchor + four lenses + flag grammar present, trees
identical) is unchanged and still green — so recorded here, not re-opened as a change request.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-03
Evidence: cospecify-lift 9/9 · parity 7/7 · full suite 243 OK · all 4 rejects held · 3 trees byte-identical
Reviewed by: <name> · date: <date>

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): do future milestone/foundation drafts actually open with a
  diverge pass + least-sure flag (vs. drafting from thin input)? The `⚠`-flag grammar now appears at
  three altitudes — watch for drift if anyone edits one guide without the others.
Spec delta for the next loop: co-specify is no longer a task-only move — it's the ONE brainstorm
  primitive at every altitude (foundation · milestone · task). A future loop could lift it to a 4th
  altitude (intake bucket discussion) or factor the shared three-move into one referenced block if the
  three restatements start drifting.

### Competency deltas
- [ADD · folded] the human↔AI brainstorm was specified only at task §1; lifting the same three-move to
  the milestone (scope.md) and foundation (0-setup.md) altitudes closed the "template-driven, not
  dialogue-driven" gap at intake/setup (evidence: this task — scope.md + 0-setup.md now teach diverge-before-draft).
  [folded foundation-version 7 → CONVENTIONS.md "Co-specify at every altitude"]
- [SDD · folded] the spec/foundation is shaped by elicitation quality, not just template prompts; naming
  the five diverge seeds and four foundation lenses makes the SDD layer's "ask before draft" enforceable
  (evidence: test_cospecify_lift asserts the seeds/lenses are present).
  [folded foundation-version 7 → PROJECT.md §Spec "SDD is elicitation-driven"]
- [TDD · folded] prose-guide tasks are red/green-testable too: assert content anchors + cross-tree byte-identity
  instead of behavior (evidence: test_cospecify_lift went red→green; test_bundle_parity backstops drift).
  [folded foundation-version 7 → CONVENTIONS.md "Prose-guide tasks are red→green-testable"]
