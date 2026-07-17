# TASK: AI-facilitated request -> versioned MILESTONE.md proposal (consumes the intake rubric)

slug: scope-loop · created: 2026-05-30 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Purpose: the SECOND half of intake. intake.md CLASSIFIES a request into a bucket; scope-loop
is the facilitation method that turns a classified request into a confirmed, well-formed,
versioned `MILESTONE.md` through structured discussion. The MILESTONE.md template
(`tooling/templates/MILESTONE.md.tmpl`) is the SHAPE; scope-loop is HOW to fill it well. This
is judgment guidance (method-side), NOT engine logic — by the v4-1 rule "the engine is truth;
the harness is the intelligence", drafting cannot live in `add.py`. The AI proposes; the human
confirms BEFORE anything is created.

Must:
  - A facilitation rubric in `add-method/skill/add/scope.md` (NEW) describing what GOOD content
    looks like for each MILESTONE.md section: goal (one sentence, an outcome not an output);
    Scope In/Out (the explicit anti-creep deferral list); Shared decisions & glossary deltas;
    Shared/risky contracts to freeze first; a breadth-first task decomposition (slug · depends-on
    · one line each); Exit criteria (observable, each mapped to a declared task slug).
  - Behavior for ALL FOUR intake outcomes (scope-loop honors intake's classification, never re-sizes):
      • new-major / sub-milestone -> draft ONE MILESTONE.md by filling the template via discussion;
        implied command `add.py new-milestone vN` (or `vN-M`).
      • task            -> NO milestone; route to `add.py new-task <slug>` (it fits the active milestone).
      • change-request  -> NO new scope; route back to SPECIFY/CONTRACT of the affected task.
      • split_required  -> draft ALL N items as a BATCH of proposals in ONE drafting pass; present
        the batch; the human confirms the batch BEFORE any milestone/task is created.
  - Confirm-before-create is INVARIANT, including the one-pass split case: "one pass" means one
    drafting pass, not auto-creation — creation stays gated behind the human's batch confirmation.
  - Every exit criterion in a drafted MILESTONE.md MUST map to a declared task slug (no dangling
    criterion). scope.md ADVISES this well-formedness; nothing in the engine enforces it
    (Enforcement decision: method-only). The human catches a violation at review.
  - Method-only: scope.md is loaded only at the scope-drafting step (progressive disclosure),
    with a pointer from `SKILL.md`. No `add.py` change; reads no docs/ chapter to decide (the v2
    Minimal pillar holds). scope.md is a SKILL artifact, synced byte-identical across the 2 skill
    trees (canonical + dogfood); any glossary touch is the DOCS artifact (3 doc trees).
Reject (named situations the rubric must NOT mishandle):
  - a request not yet classified by intake -> scope-loop does not run; classify first
    -> "not_classified" (you cannot draft scope for an unclassified request).
  - a drafted MILESTONE.md whose exit criterion maps to no task slug -> the AI fixes the draft
    (add the task or drop the criterion) before proposing -> "dangling_criterion" (never propose
    a malformed milestone; with no engine lint, the human is the backstop at review).
  - a request intake routed to `task` or `change-request` -> scope-loop creates NO milestone
    -> "no_milestone" (it is not milestone-sized; honor intake's classification).
After:
  - given a classified request, the AI produces a confirmed, well-formed versioned MILESTONE.md
    (or, for split_required, the confirmed batch) ready for `add.py new-milestone`. This closes
    the v4-1 intake interface: request -> classified (intake) -> versioned scope (scope-loop).
    Nothing in the engine changed; the human confirmed every created artifact.
Assumptions (confirm before building):
  - [x] Home = NEW `skill/add/scope.md` (sibling to intake.md; progressive disclosure) + pointer
        from SKILL.md. Confirmed by human 2026-05-30 (AskUserQuestion).
  - [x] Enforcement = method-only doc; NO engine lint (no `add.py` change). scope.md advises the
        exit-criteria→slug rule; the human catches a dangling criterion at review. Confirmed by
        human 2026-05-30 (AskUserQuestion). [Tradeoff surfaced: a `check` lint would enforce it
        mechanically per the design-for-failure rule; the human chose minimal.]
  - [x] split_required = draft ALL N as a batch of proposals in ONE pass; human confirms the batch
        BEFORE creation. Confirmed by human 2026-05-30 (AskUserQuestion). [Interpretation surfaced:
        "one pass" = one drafting pass; creation stays gated, preserving confirm-before-create.]
  - [x] Verification of a JUDGMENT artifact (same tension as intake; ADD's red/green is code-centric,
        this is a rubric). Confirmed surface (human 2026-05-30): a thin structural test guards
        scope.md's STRUCTURE (exists in both skill trees + md5 parity; documents the behavior for
        all 4 intake outcomes; carries a WORKED EXAMPLE built from a REAL milestone in this repo's
        history; SKILL.md links it) and goes RED before scope.md exists; the human reviews the
        JUDGMENT (does the guidance produce sound milestones) at verify.

<!-- EXIT: every rule stated, every rejection has a named code, zero open assumptions. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

Worked examples use THIS repo's real milestones (dogfood: checkable against what happened) —
the well-formedness example reads v4-1/MILESTONE.md, whose exit criteria each map to a slug.

```gherkin
Scenario: new-major -> draft one MILESTONE.md
  Given intake classified "give ADD a hosted web dashboard" as new-major (v5)
  When the AI applies scope.md
  Then it drafts ONE MILESTONE.md filling goal · Scope In/Out · exit criteria · breadth-first tasks
  And the implied command is `add.py new-milestone v5`

Scenario: sub-milestone -> draft one MILESTONE.md
  Given intake classified "build corridor + tests-red-before-build" as sub-milestone (v4-2)
  When the AI applies scope.md
  Then it drafts ONE MILESTONE.md whose goal names the slice of the live v4 theme
  And the implied command is `add.py new-milestone v4-2`

Scenario: task outcome -> no milestone            # Reject (no_milestone)
  Given intake classified "expose owner/stop as --json" as task (fits active v4-1)
  When the AI applies scope.md
  Then it creates NO milestone and routes to `add.py new-task <slug>`
  And no MILESTONE.md is drafted (intake's classification is honored)

Scenario: change-request -> no new scope          # Reject (no_milestone)
  Given intake classified "guide --json phase/gate should be str|null" as change-request
  When the AI applies scope.md
  Then it creates NO milestone and routes back to SPECIFY/CONTRACT of the affected task
  And no parallel milestone is drafted to fork the truth

Scenario: split_required -> batch of N drafts in one pass
  Given intake returned split_required for a request spanning two themes
  When the AI applies scope.md
  Then it drafts ALL N MILESTONE.md proposals in ONE pass and presents them as a batch
  And nothing is created until the human confirms the batch

Scenario: confirm-before-create is invariant
  Given any drafted MILESTONE.md (single or batch)
  When the AI finishes the draft
  Then it PROPOSES and waits; no milestone/task exists on disk
  And creation happens only after the human confirms

Scenario: every exit criterion maps to a task slug    # well-formedness (advised)
  Given a drafted MILESTONE.md
  When the AI checks well-formedness per scope.md
  Then each exit criterion names a task slug declared in the task decomposition
  And v4-1/MILESTONE.md (the worked example) satisfies this — every criterion has (← slug)

Scenario: a dangling exit criterion is fixed before proposing   # Reject (dangling_criterion)
  Given a draft whose exit criterion maps to no declared task slug
  When the AI checks well-formedness
  Then it fixes the draft (adds the task or drops the criterion) before proposing
  And no malformed milestone is proposed (the human is the backstop; no engine lint)

Scenario: an unclassified request is refused         # Reject (not_classified)
  Given a raw request that intake has NOT yet classified
  When scope-loop is invoked
  Then it returns "not_classified" and routes to intake first
  And no MILESTONE.md is drafted

Scenario: scope.md is method-only and on the loaded surface
  Given the scope-drafting step
  When the AI loads guidance
  Then it reads scope.md (a SKILL artifact), not a docs/ chapter, and `add.py` is unchanged
  And the v2 Minimal pillar holds (no command reads docs/ at runtime)

Scenario: scope.md is synced across both skill trees
  Given the canonical and dogfood skill trees
  When scope.md is compared
  Then it is byte-identical (md5 parity) and both SKILL.md copies link to it
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

This is a JUDGMENT artifact (a facilitation rubric), not code — so the contract freezes the
ARTIFACT's structure and the test that guards it, never the AI's live drafting.

```
ARTIFACT: scope.md — created in BOTH synced skill trees, byte-identical (md5 parity):
    canonical: add-method/skill/add/scope.md
    dogfood:   .claude/skills/add/scope.md
  MUST contain:
    - an OUTCOMES table mapping each of the 4 intake outcomes to scope-loop's action + what it creates:
        | intake outcome           | scope-loop action                         | creates (after confirm) |
        | new-major / sub-milestone | draft ONE MILESTONE.md (fill the template) | 1 milestone             |
        | task                      | route to `add.py new-task <slug>`          | 0 milestones            |
        | change-request            | route to SPECIFY/CONTRACT of the task      | 0 milestones            |
        | split_required            | draft ALL N as a batch in ONE pass         | N (after batch confirm) |
    - the 3 reject codes by name: not_classified · dangling_criterion · no_milestone
    - the confirm-before-create INVARIANT, stated for both single and one-pass-batch cases
    - the well-formedness rule: every exit criterion maps to a DECLARED task slug
    - a MILESTONE.md section checklist: goal · Scope In/Out · Shared decisions · Shared contracts · Tasks · Exit criteria
    - a WORKED EXAMPLE naming a REAL milestone slug in this repo (e.g. v4-1) — checkable against the actual file

PROPOSAL (what the AI emits at the scope step, awaiting human confirm before creation):
    new-major / sub-milestone -> a drafted MILESTONE.md (template filled)
    split_required            -> a BATCH [ MILESTONE.md, ... ] in one pass
    task / change-request     -> a route note; NO milestone drafted
  reject -> { reject, rationale }   reject ∈ { not_classified, dangling_criterion, no_milestone }

STRUCTURAL TEST (red/green guard on the ARTIFACT — never the live judgment), in tooling/test_scope_loop.py:
    test_scope_exists_in_both_trees_with_md5_parity
    test_documents_all_four_intake_outcomes        (outcomes table lists all 4 + action)
    test_documents_all_three_reject_codes
    test_states_confirm_before_create_invariant
    test_states_exit_criteria_map_to_task_slug
    test_worked_example_references_real_milestone  (names a slug that exists under .add/milestones/)
    test_both_skill_md_link_scope_and_are_identical

GLOSSARY delta (DOCS artifact, synced across 3 doc trees): add "Scope drafting (scope-loop)".
NAMES match GLOSSARY: intake · request bucket · scope drafting.
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit)   <!-- frozen by human 2026-05-30 (AskUserQuestion). Changing it = change request back to SPECIFY. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: structural — one assertion per frozen-artifact invariant (a JUDGMENT artifact;
the human reviews the drafting quality at verify, the test only guards scope.md's shape).
Plan (maps 1:1 to the CONTRACT's STRUCTURAL TEST list):
  - test_scope_exists_in_both_trees_with_md5_parity — scope.md in both skill trees, byte-identical
  - test_documents_all_four_intake_outcomes — the outcomes table lists all 4 outcomes + actions
  - test_documents_all_three_reject_codes — not_classified · dangling_criterion · no_milestone
  - test_states_confirm_before_create_invariant — the invariant is stated (incl. one-pass batch)
  - test_states_exit_criteria_map_to_task_slug — the well-formedness rule is present
  - test_worked_example_references_real_milestone — names a slug that EXISTS under .add/milestones/
  - test_both_skill_md_link_scope_and_are_identical — both SKILL.md point to scope.md + md5 parity

Tests live in: `add-method/tooling/test_scope_loop.py` · MUST run red (scope.md absent) before Build.
Red proof: collected before scope.md exists -> failures are "missing artifact", not tautology.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): no `add.py` change (method-only, per the Enforcement decision);
the artifact must stay byte-identical across its synced trees (cp + md5, never hand-divergence).
Built (no test or frozen contract touched):
  - `add-method/skill/add/scope.md` (NEW) — outcomes table (4 outcomes), 3 reject codes, the
    confirm-before-create invariant, the exit-criteria→slug rule, a MILESTONE.md section
    checklist, and a worked example built from the REAL `.add/milestones/v4-1/MILESTONE.md`.
  - `skill/add/SKILL.md` (both trees) — pointer to scope.md added in the Intake section.
  - `appendix-c-glossary.md` (3 doc trees) — "Scope drafting (scope-loop)" entry.
  - `.claude/skills/add/scope.md` — cp of canonical (md5 4a9b158, parity verified).
Result: full suite 114/114 (107 prior + 7 new); test_scope_loop 7/7; red proven before build
(scope.md absent → 7 failures; non-tautology confirmed). Secret scan clean. No `add.py` change.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

Evidence pre-filled by the AI; the gate signature itself is the human's (Verify owner=human).
- [x] all tests pass — full suite 114/114 (107 prior + 7 new); test_scope_loop 7/7
- [x] coverage did not decrease — 7 structural tests added, none removed (NB: the frozen contract
      lists 8 MUST-contain artifact items; the MILESTONE.md section checklist is the 1 untested one — logged in OBSERVE)
- [x] no test or contract was altered during build — only scope.md + SKILL.md + glossary added
- [x] concurrency / timing safe — N/A: a static doc artifact, no code path, no IO, nothing to race
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose only; secret scan clean; stdlib-only test
- [x] layering & dependencies follow CONVENTIONS.md — scope.md is on the loaded skill (State) surface, no docs/ auto-load; scope.md md5-identical across both skill trees (4a9b158), SKILL.md (e051769), glossary across 3 trees (ebe0ad8)
- [x] a person reviewed and approved the change   ← Tin Dang, 2026-05-30 (gate PASS)

Decision to sign at the gate (the one judgment a test can't sign):
  - **The rubric's JUDGMENT** — does scope.md produce SOUND milestones? Two checks: (a) the
    per-outcome behavior is right (esp. split_required = batch-in-one-pass, creation still gated);
    (b) the worked example is faithful — its goal now quotes the REAL v4-1 goal, its tasks
    (machine-state-json · versioning-policy · scope-loop) and exit-criteria→slug mapping match
    `.add/milestones/v4-1/MILESTONE.md`. The structural test proves the artifact is well-formed;
    only a person can vouch the guidance is sound.

### GATE RECORD
Outcome: PASS
The reviewer vouched the rubric's JUDGMENT — the per-outcome behavior (incl. split_required =
batch-in-one-pass, creation still gated) and the worked example (faithful to the real
v4-1/MILESTONE.md: goal, tasks, exit-criteria→slug mapping). The disclosed section-checklist
coverage gap was accepted as an OBSERVE note (artifact conformant; regression-risk only).
Structural suite 114/114; md5 parity across both skill trees + 3 doc trees. No add.py change.
Reviewed by: Tin Dang · date: 2026-05-30

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors):
  - **human-edit rate on drafts** — how heavily the human rewrites a proposed MILESTONE.md.
    Low edits = the rubric drafts well; heavy edits = the section guidance is off. The structural
    test can't see draft quality; only the edit rate reveals it.
  - **dangling_criterion catches** — how often the human (the backstop, since there's no engine
    lint) finds an exit criterion mapping to no task. A nonzero rate is the cost of the method-only
    choice; if it climbs, revisit the Enforcement decision (a `check` lint becomes worth it).
Spec delta for the next loop:
  - If dangling_criterion catches recur, that is the change-request signal to add the engine lint
    (reopen this task's frozen Enforcement decision as a change-request — not a silent edit).
  - Residual coverage gap (logged, not blocking): the structural suite guards scope.md's SHAPE;
    it can never assert a drafted milestone is well-sized — that stays a human gate call.
  - Test/contract gap (advisor-caught, logged not blocking): the frozen contract froze exactly 7
    tests but lists 8 MUST-contain artifact items — the MILESTONE.md section checklist (goal · Scope
    In/Out · Shared decisions · Shared contracts · Tasks · Exit criteria), the substantive core, is
    NOT structurally guarded; deleting that section keeps the suite green. The artifact IS conformant
    (the section is present), so this is regression-risk, not a defect. Adding an 8th test edits the
    frozen test list → if wanted, it is a change-request back to CONTRACT, never a silent edit.
