# TASK: Classify a request: new-major | sub-milestone | task (AI proposes, human confirms)

slug: versioning-policy · created: 2026-05-29 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Purpose: give the AI a deterministic-enough RUBRIC to classify any incoming request into
exactly ONE of four buckets — and to record WHY — so intake (scope-loop, the next task) sizes
and versions scope correctly. The AI proposes; the human confirms. This is judgment guidance
(method-side), NOT engine logic — by the v4-1 rule "the engine is truth; the harness is the
intelligence", classification cannot live in `add.py` as a decision procedure.

Must:
  - A FOUR-bucket rubric, each with a crisp decision test and the `add.py` command it implies:
      • new-major  (vN)    — a new product theme/pillar not covered by any active milestone's
                             goal  -> `add.py new-milestone vN`
      • sub-milestone(vN-M)— a slice of an EXISTING major theme, too big for one task
                             -> `add.py new-milestone vN-M`
      • task               — fits within the ACTIVE milestone's stated scope
                             -> `add.py new-task <slug>`
      • change-request     — modifies ALREADY-FROZEN scope (a frozen contract or a shipped
                             milestone's promise) -> route back to SPECIFY/CONTRACT of the
                             affected task; do NOT size it as new scope.
  - Buckets are mutually exclusive; the rubric states the tie-break ORDER: (1) does it touch
    frozen scope? -> change-request. else (2) size test: new theme -> major · slice -> sub ·
    fits -> task. Exactly one bucket per request.
  - The AI emits a PROPOSAL = { bucket, rationale, the exact `add.py` command implied }; the
    human confirms or overrides BEFORE anything is created.
  - The rationale is RECORDED in the artifact created/affected (the new MILESTONE.md goal/body,
    the new TASK.md, or — for change-request — a note in the affected TASK.md). State surface,
    not a machine field (form decision: method-only, human-confirmed).
  - The rubric lives in `add-method/skill/add/intake.md` (NEW; a new INTAKE altitude — phases
    0–7 are per-task, intake is request->milestone), loaded only at intake (progressive
    disclosure), with a pointer from `SKILL.md`. No `add.py` change; reads no docs/ chapter to
    decide (the v2 Minimal pillar holds). intake.md is a SKILL artifact, synced byte-identical
    across the 2 skill trees (canonical + dogfood); the glossary touch is the DOCS artifact,
    synced across its 3 doc trees.
Reject (named situations the rubric must NOT mishandle):
  - an ambiguous / underspecified request -> the AI STOPS and asks, never guesses a bucket
    -> "ask_human"  (the skill's "ask, don't guess" rule, at milestone altitude).
  - a request that changes frozen scope -> MUST be classified change-request and routed to
    SPECIFY/CONTRACT; never spawn a parallel milestone that forks the truth -> "frozen_scope".
  - a request spanning multiple buckets -> split it; propose the SMALLEST set of correctly-sized
    items, each with its own rationale; never force a multi-theme request into one milestone
    -> "split_required".
After:
  - given any request, the AI can produce a confirmed { bucket + rationale + implied command };
    scope-loop (next task) consumes THIS rubric to draft the actual versioned MILESTONE.md.
    Nothing in the engine changed; the human made every sizing decision.
Assumptions (confirm before building):
  - [x] Form = method-only rubric (no engine change; rationale recorded in the created/affected
        doc, not state.json). Confirmed by human 2026-05-29 (AskUserQuestion).
  - [x] Taxonomy = 4 buckets incl. change-request (-> back to SPECIFY/CONTRACT). Confirmed by
        human 2026-05-29 (AskUserQuestion).
  - [x] Home = `skill/add/intake.md` (loaded at intake) + pointer from SKILL.md. Confirmed by
        human 2026-05-30 — forced by the Minimal pillar (a runtime rubric must be on the loaded
        State surface, not in docs/); a NEW intake altitude that scope-loop will extend.
  - [x] Verification of a JUDGMENT artifact (the honest tension — ADD's red/green is code-centric;
        this deliverable is a rubric). Confirmed red/green surface (human 2026-05-30): a table of
        WORKED EXAMPLES (request -> expected bucket + rationale shape); a thin machine test guards
        STRUCTURE (intake.md exists, documents all 4 buckets + the tie-break order, every example
        maps to a valid bucket and is well-formed) and goes RED before the rubric exists; the human
        reviews the JUDGMENT (do the example classifications hold up) at verify.

<!-- EXIT: every rule stated, every rejection has a named code, zero open assumptions. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

Worked examples use THIS project's real history (dogfood: the cases are checkable against
what actually happened) — they double as the red/green example table the structural test reads.

```gherkin
Scenario: a brand-new theme -> new-major
  Given a request "give ADD a hosted web dashboard" not covered by any active milestone's goal
  When the AI applies the rubric
  Then the proposed bucket is "new-major" with the implied command `add.py new-milestone v5`
  And the rationale names WHY it is a new theme (not a slice of an existing one)

Scenario: a slice of an existing theme -> sub-milestone
  Given a request "add the build corridor + tests-red-before-build" under the live v4 theme
  When the AI applies the rubric
  Then the proposed bucket is "sub-milestone" with the implied command `add.py new-milestone v4-2`
  And the rationale names the parent theme it slices

Scenario: work that fits the active milestone -> task
  Given a request "expose owner/stop as --json" while v4-1 (the intake interface) is active
  When the AI applies the rubric
  Then the proposed bucket is "task" with the implied command `add.py new-task <slug>`
  And the rationale shows it fits the active milestone's stated scope

Scenario: a change to already-frozen scope -> change-request
  Given a request "guide --json phase/gate should be str|null" against the FROZEN
        machine-state-json contract
  When the AI applies the rubric
  Then the proposed bucket is "change-request" routed to SPECIFY/CONTRACT of that task
  And no new milestone or task is created to fork the truth

Scenario: the tie-break order puts frozen-scope first
  Given a request that both looks like new work AND touches frozen scope
  When the AI applies the rubric
  Then it is classified "change-request" (the frozen-scope test runs before the size test)

Scenario: every classification emits the full proposal shape
  When the AI classifies any request
  Then it emits { bucket, rationale, the exact implied `add.py` command }
  And the human confirms or overrides before anything is created

Scenario: the rationale is recorded in the artifact
  Given a confirmed classification
  When the milestone/task is created (or a change-request note is added)
  Then the rationale is written into that MILESTONE.md / TASK.md (State surface, not state.json)

Scenario: an ambiguous request stops and asks            # Reject (ask_human)
  Given a request too underspecified to size
  When the AI applies the rubric
  Then it returns "ask_human" and asks the human instead of guessing a bucket
  And no milestone, task, or file is created

Scenario: a multi-theme request must be split            # Reject (split_required)
  Given a request that spans more than one bucket
  When the AI applies the rubric
  Then it returns "split_required" and proposes the SMALLEST set of correctly-sized items
  And nothing is forced into a single milestone

Scenario: applying the rubric stays minimal             # Minimal pillar + no engine change
  When the rubric is applied
  Then it reads no docs/ chapter and requires no change to add.py
  And the rubric lives in skill/add/intake.md, identical across the shipped + dogfood trees

Scenario: the structural test is red before the rubric exists   # red-first
  Given skill/add/intake.md does not yet document the 4 buckets + tie-break + examples
  When the structural test runs
  Then it FAILS — proving the test guards the artifact, not a tautology
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

No CLI/API surface (method-only). The "shape" frozen here is (a) the rubric ARTIFACT, (b) the
PROPOSAL the AI emits, and (c) the STRUCTURAL TEST's machine-checkable invariants.

```
ARTIFACT: intake.md — created in BOTH synced skill trees, kept byte-identical (md5 parity):
    canonical : add-method/skill/add/intake.md      (shipped npm)
    dogfood   : .claude/skills/add/intake.md         (what Claude loads in THIS repo)
  MUST contain, in order:
    1. the 4 BUCKETS, each as a row: { bucket, decision-test, implied `add.py` command }
         buckets ∈ { "new-major", "sub-milestone", "task", "change-request" }   (exactly these 4)
    2. the TIE-BREAK ORDER, stated as: frozen-scope test FIRST, then the size test
    3. the 3 REJECT codes, each with its handling: { "ask_human", "frozen_scope", "split_required" }
    4. a WORKED-EXAMPLES table — a markdown table with columns | request | bucket | rationale |
       (machine-parseable); every `bucket` cell ∈ the 4 buckets (the structural test parses this)
  PLUS: a pointer line added to BOTH SKILL.md copies -> intake.md (intake altitude discoverable),
        keeping the two SKILL.md byte-identical.

PROPOSAL (what the AI emits per request; recorded in the created/affected doc, NOT state.json):
  classify(request) -> one of
    { "bucket": "new-major"|"sub-milestone"|"task"|"change-request",
      "rationale": str,            # WHY this bucket (names the theme / slice / fit / frozen scope)
      "command": str }             # the exact implied `add.py …`:
                                   #   new-major     -> `add.py new-milestone vN`
                                   #   sub-milestone -> `add.py new-milestone vN-M`
                                   #   task          -> `add.py new-task <slug>`
                                   #   change-request-> `add.py phase specify|contract <affected>`
  | { "reject": "ask_human"|"frozen_scope"|"split_required", "rationale": str }   # nothing created

STRUCTURAL TEST (the red/green guard; asserts the artifact, not the AI's judgment):
  - intake.md exists in BOTH skill trees and is byte-identical (md5 parity)
  - it documents all 4 buckets AND all 3 reject codes (by their exact frozen names)
  - it states the tie-break order (frozen-scope before size)
  - the worked-examples markdown table parses and every bucket cell is one of the 4
  - BOTH SKILL.md copies link to intake.md (and remain byte-identical to each other)
  - RED before intake.md exists / is incomplete  (non-tautology)
```

Names match the glossary additions this task introduces: "request bucket" (the 4) and the 3
reject codes. To be added to the glossary as part of build (like owner/stop in machine-state-json).

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit) · (approved by Tin Dang via AskUserQuestion, 2026-05-30)   <!-- Changing a frozen contract = change request back to SPECIFY. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: every STRUCTURAL invariant in the frozen contract (the judgment is human-
reviewed at verify, not unit-tested — see SPECIFY assumption 4). 6 structural tests:
  - test_intake_exists_in_both_trees_with_md5_parity — both skill trees + byte-identical
  - test_documents_all_four_buckets — the 4 frozen bucket names present
  - test_documents_all_three_reject_codes — ask_human / frozen_scope / split_required present
  - test_states_tiebreak_order_frozen_before_size — one line: frozen-scope BEFORE size
  - test_worked_examples_table_parses_and_buckets_valid — table parses; every bucket cell valid; all 4 covered
  - test_both_skill_md_link_intake_and_are_identical — both SKILL.md link intake.md + md5-identical

Tests live in: `add-method/tooling/test_intake_rubric.py` (NEW, 6 tests; paths resolved from
`__file__`, not cwd). Stripped from installs by cli.js (test_*.py glob); runs only in the dev repo.
Red-first evidence: 6/6 RED before build — 2 failures (no SKILL.md pointer; intake.md absent) +
4 errors (read_text on the missing intake.md). All red for the SAME real reason: the artifact
does not exist yet (non-tautology — the test guards the rubric, not itself).

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): NO `add.py` change (classification is judgment, not engine
logic). The deliverable is a doc artifact kept byte-identical across its synced trees — the
structural test enforces md5 parity so the shipped and dogfood rubrics can never drift.
Built:
  - `skill/add/intake.md` (NEW) — the rubric: 4 buckets table, tie-break order (frozen-scope
    before size), the 3 reject codes, and a worked-examples table (real project history).
    Created in BOTH skill trees, byte-identical (md5 7db837e).
  - `SKILL.md` — added an "Intake" section + pointer to intake.md; both copies byte-identical (988d199).
  - `appendix-c-glossary.md` — "Intake" + "Request bucket" entries (covers the 4 buckets + 3
    reject codes); synced across all 3 doc trees (md5 239c4d9).
Tests: `test_intake_rubric` 6/6 green; full suite 106/106 (100 prior + 6 new). Minimal pillar
unaffected (new files are skill/docs, not a code path; no add.py change). Secret scan clean.
Constraints honored: no test or contract altered during build; no new dependency (stdlib only).

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

Evidence pre-filled by the AI; the gate signature itself is the human's (Verify owner=human).
- [x] all tests pass — full suite 107/107 (100 prior + 7 new); test_intake_rubric 7/7
- [x] coverage did not decrease — 7 structural tests added (one per frozen invariant), none removed
- [x] no test or contract was altered during build — only intake.md + SKILL.md + glossary added
- [x] concurrency / timing safe — N/A: a static doc artifact, no code path, no IO, nothing to race
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose only; secret scan clean; stdlib-only test
- [x] layering & dependencies follow CONVENTIONS.md — new INTAKE altitude in the skill (loaded surface), no docs/ auto-load; intake.md md5-identical across both skill trees (7db837e), SKILL.md (988d199), glossary across 3 trees (239c4d9)
- [x] a person reviewed and approved the change   ← Tin Dang, 2026-05-30 (gate PASS)

Decision to sign at the gate (the one judgment call this task can't unit-test):
  - **The rubric's JUDGMENT** — do the 4 worked examples classify correctly? (dashboard→new-major,
    corridor→sub-milestone, --json→task, str|null amendment→change-request). The structural test
    proves the artifact is well-formed; only a person can vouch the classifications are sound.
Hardening applied before the gate (advisor pass):
  - The structural suite under-covered the frozen CONTRACT — it asserted the 4 bucket NAMES
    appeared in prose but not that the buckets TABLE or the proposal shape existed (and
    `assertIn('task')` was near-tautological, "task" being ubiquitous in the prose). Added
    test_buckets_table_lists_all_four_with_commands (parses the table; goes red if it or a row
    is deleted — proven: table removed → 0 buckets parsed) and test_proposal_shape_documented.
    Suite 106→107. The artifact was already conformant; this closes a regression gap, not a defect.
  - SPECIFY's tree-count wording was imprecise ("3 doc/skill trees"); corrected in place — the
    rubric is a SKILL artifact (2 skill trees), the glossary the DOCS artifact (3 doc trees).
    SPECIFY is not frozen, so this is an edit, not a change-request.

### GATE RECORD
Outcome: PASS
The reviewer vouched the rubric's JUDGMENT — the 4 worked-example classifications
(dashboard→new-major, corridor→sub-milestone, --json→task, str|null→change-request)
hold against this project's real history. Structural suite 107/107; md5 parity across
both skill trees + 3 doc trees confirmed. No add.py change (method-only).
Reviewed by: Tin Dang · date: 2026-05-30

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors):
  - **human-override rate** — how often the human changes the AI's proposed bucket at intake.
    This is the rubric's true error signal; the structural test cannot see live judgment, only
    the override rate reveals miscalibration. A rising rate = the rubric or tie-break is drifting.
  - **per-reject-code rate** — `ask_human` vs `frozen_scope` vs `split_required`. A spike in
    `split_required` hints the bucket boundaries are too narrow; a spike in `ask_human`, that
    requests arrive under-specified (an intake-prompt problem, not a rubric one).
Spec delta for the next loop:
  - If a recurring request fits no bucket, that is a 5th-bucket signal → reopen this rubric as a
    change-request (the buckets list is frozen @ v1; growing it is a versioned amendment).
  - Residual coverage gap (logged, not blocking): the structural suite guards the artifact's
    SHAPE; it can never assert a classification is *correct* — that stays a human gate call. If
    overrides cluster on one bucket, add that case to the worked-examples table.
