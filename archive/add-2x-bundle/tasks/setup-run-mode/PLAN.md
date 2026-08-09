# TASK: Setup: autonomy×streams table + parallel+auto default

slug: setup-run-mode · created: 2026-06-15 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
- `.claude/skills/add/phases/0-setup.md` (≈53–69 "§3 Draft to the lock") — the setup guide; gains a "## Run mode" step proposing the autonomy×streams default. 3 byte-identical trees (canonical `add-method/skill/add/`, dogfood `.claude/skills/add/`, bundle `_bundled/skill/add/`) — guarded by test_tree_parity + test_bundle_parity.
- `.claude/skills/add/streams.md` (≈5 "The default ADD path is one task at a time"; ≈38 "## The autonomy level is the throttle") — the line whose default flips to parallel+auto-opt-out when chosen at setup.
- `.add/PROJECT.md` — has a "Key Decisions" area; the run-mode choice is recorded there (no engine change — the default is orchestrator behavior + a recorded decision, not a new flag). Project autonomy is ALREADY `auto` (state.json `project autonomy: auto`); streams is the part currently opt-in.
- prior art: `add-method/tooling/test_cospecify_lift.py` — the content-test pattern (read CANONICAL guide, assert anchors + ordering, 3-tree parity).
Context (working folder): the just-shipped `add.py waves` (task dag-scheduler) is the scheduler the run-mode table points at; `run.md` autonomy table (auto = default, verify auto-PASS) is the autonomy half of the comparison.
Honors (patterns / conventions): no engine change (guide + recorded decision only); 3-tree byte-identical skill sync via cp + prepare_bundle; content tested by substring/anchor assertions; the irreducible one-approval-per-contract floor is preserved (the default changes order/throttle, never whether the human gate fires).
Anchors the contract cites: the "## Run mode" heading in 0-setup.md · the comparison table (rows: sequential vs auto+parallel; cols: human gates · concurrency/flow) · the "parallel+auto is the default — confirm to keep" proposal · the `add.py waves` + autonomy-dial citations · the PROJECT.md Key Decisions record · the streams.md default-flip note.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: a "Run mode" step at setup — the guide presents an autonomy×streams comparison table so
the human is AWARE of the features + flow behavior, then proposes parallel+auto as the DEFAULT
(confirm-to-keep), recording the choice in PROJECT.md Key Decisions.
Framings weighed: setup proposes the default + shows the table, human confirms-to-keep (chosen) ·
silent global flip with no table (rejected — the human must SEE the flow they're opting into; never
pre-stamp) · keep streams fully opt-in, only document it (rejected — the human chose to make
parallel+auto the default).
Must:
<must>
  - phases/0-setup.md gains a "## Run mode" step that PRESENTS a comparison table covering at least
    two modes — sequential (one task at a time, every gate serial) vs auto+parallel (builds overlap,
    only the contract decision point + escalations queue) — with columns naming the HUMAN GATES and
    the CONCURRENCY/flow behavior, so the human is aware of each mode's behavior.
  - the step PROPOSES parallel+auto as the DEFAULT and asks the human to confirm-to-keep (or downgrade)
    — never a silent flip; the choice is recorded in PROJECT.md Key Decisions.
  - the table/step CITES the real seams: `add.py waves` (the scheduler) and the autonomy dial
    (`add.py autonomy`, run.md), so "parallel" and "auto" are concrete, not hand-wave.
  - streams.md's "one task at a time" framing is updated to name parallel+auto as the project default
    (an OPT-OUT) when chosen at setup — the two guides agree.
  - the irreducible floor is preserved in prose: the default changes ORDER/THROTTLE, never whether the
    one-approval-per-contract gate fires.
  - all 3 skill trees stay byte-identical (test_tree_parity + test_bundle_parity).
</must>
Reject:
<reject>
  - (prose task — no runtime input to reject; the "rejection" is a malformed guide) a freeze whose
    guide lacks the table OR the confirm-to-keep proposal OR the waves/autonomy citation -> the
    content tests stay red; never ship a half-section.
</reject>
After:
<after>
  - a reader of 0-setup.md sees the run-mode table, knows parallel+auto is the proposed default, and
    knows it is confirm-to-keep; streams.md agrees; the human gate is explicitly preserved.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [spec] making parallel+auto the DEFAULT (confirm-to-keep) reverses streams.md's long-standing
    "one task at a time" default — lowest confidence because it is a philosophy shift, not a feature
    add; if wrong (teams want conservative-by-default): the proposal over-pushes concurrency — mitigated
    because it is CONFIRM-to-keep (the human sees the table and can downgrade in one step) and the
    safety floor (one approval per contract) is unchanged.
  - [ ] [contract] the choice lives in PROJECT.md Key Decisions, not a new state.json flag — assumes
    run-mode is orchestrator behavior, not engine state; if wrong: a later task adds a state field.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: setup teaches the run-mode comparison table
  Given the setup guide phases/0-setup.md
  When I read the "## Run mode" step
  Then it contains a comparison table naming sequential AND auto+parallel modes
  And the table has columns for the human gates and the concurrency/flow behavior

Scenario: setup proposes parallel+auto as the default, confirm-to-keep
  Given the "## Run mode" step
  When I read its proposal
  Then it names parallel+auto as the DEFAULT and asks the human to confirm-to-keep
  And it records the choice in PROJECT.md Key Decisions (named in the step)

Scenario: the run-mode step cites the real seams
  Given the "## Run mode" step
  When I read it
  Then it cites `add.py waves` and the autonomy dial
  And it states the one-approval-per-contract gate still fires (order/throttle only)

Scenario: streams.md agrees on the new default
  Given streams.md
  When I read its default framing
  Then it names parallel+auto as the project default (opt-out) when chosen at setup

Scenario: the three skill trees stay byte-identical
  Given canonical, dogfood, and bundled skill trees
  When the edit lands
  Then 0-setup.md and streams.md are byte-identical across all three
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
DOC CONTRACT — phases/0-setup.md MUST contain a section:
  "## Run mode" (a setup step, placed in the draft-to-lock flow)
    ├─ a comparison table with rows {sequential | auto+parallel}
    │   and columns naming {human gates, concurrency/flow behavior}
    ├─ a proposal: "parallel + auto is the default — confirm to keep" (downgrade in one step)
    ├─ cites `add.py waves` AND the autonomy dial (`add.py autonomy` / run.md)
    ├─ records the choice in "PROJECT.md" Key Decisions
    └─ states the one-approval-per-contract gate still fires (order/throttle only)
  streams.md MUST name parallel+auto as the project DEFAULT (opt-out) when chosen at setup.
Required substrings (render-blind, asserted by the test):
  "## Run mode" · "confirm" · "parallel" · "auto" · "add.py waves" · "Key Decisions"
Parity: 0-setup.md + streams.md byte-identical across canonical · dogfood · bundle.
No engine change · no state.json field.
```

Status: FROZEN @ v1 — approved by Tin Dang (autonomous authorization 2026-06-15)
Least-sure flag surfaced at freeze: [spec] making parallel+auto the DEFAULT reverses streams.md's "one task at a time" default — a deliberate philosophy shift the human chose; risk mitigated because it is CONFIRM-to-keep (the table is shown, downgrade is one step) and the one-approval-per-contract floor is unchanged.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every required substring + the 3-tree parity (content-test pattern, per test_cospecify_lift).
Plan (one test per scenario, asserting content not internals; read CANONICAL guide):
<test_plan>
  - test_run_mode_table_present: 0-setup.md has "## Run mode" + a table naming sequential & auto+parallel + gate/concurrency columns
  - test_proposes_parallel_auto_default: the step says parallel+auto is the default + "confirm" to keep
  - test_cites_waves_and_autonomy: the step cites "add.py waves" + the autonomy dial + preserves the one-approval gate
  - test_streams_names_new_default: streams.md names parallel+auto as the project default (opt-out)
  - test_records_in_project_key_decisions: the step names "Key Decisions" (PROJECT.md) as where the choice is recorded
  - test_three_trees_byte_identical: 0-setup.md + streams.md identical across canonical/dogfood/bundle
</test_plan>

Tests live in: `add-method/tooling/test_setup_run_mode.py` · MUST run red (missing section) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/phases/0-setup.md` `.claude/skills/add/phases/0-setup.md` `add-method/src/add_method/_bundled/skill/add/phases/0-setup.md` `add-method/skill/add/streams.md` `.claude/skills/add/streams.md` `add-method/src/add_method/_bundled/skill/add/streams.md`
Strategy (ordered batches): 1. add the "## Run mode" step to canonical 0-setup.md (table + proposal + citations + Key-Decisions record + gate-preserved note). 2. update streams.md's default framing. 3. cp canonical→dogfood for both files + `python3 scripts/prepare_bundle.py` (canonical→bundle). 4. green the content suite + parity.
Safety rule (feature-specific): prose only — no engine/state change; the one-approval-per-contract floor must remain explicit in the new text (do not imply auto removes the gate).
Code lives in: the 3 skill trees (canonical edited, cp'd to dogfood, bundle regenerated).
Constraints: do NOT change any test or the contract; keep 0-setup.md + streams.md byte-identical across all 3 trees; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 1064 green; test_setup_run_mode 6/6; test_tree_parity + test_bundle_parity green.
- [x] coverage did not decrease — 6 new content tests; no test removed.
- [x] no test or contract was altered during build — §3 FROZEN @ v1 unchanged; only the 6 skill-tree files (declared §5) edited.
- [x] the green was EARNED — prose task: the SEMANTIC read IS the check (below). Tests assert real substrings (table, both modes, confirm, waves, Key Decisions, opt-out) not vacuous truths; the wording lint (test_ubiquitous_language) caught a slang regression ("dial") which was fixed to "autonomy level".
- [x] concurrency / timing — N/A (documentation change).
- [x] no exposed secrets / injection / unexpected deps — prose only; no code, no deps.
- [x] layering & dependencies follow CONVENTIONS.md — 3-tree parity held; wording rubric (no "dial" slang) satisfied; the new section preserves the one-approval floor (no contradiction with run.md/streams.md).
- [x] a person reviewed and approved the change — Tin Dang (autonomous authorization); auto-gate, no residue.

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose) — read the "## Run mode" section + the streams.md default note in full: the table names both modes with gate + concurrency columns; the proposal is confirm-to-keep (not a silent flip); it cites `add.py waves` + the autonomy level; it explicitly states the one-approval-per-contract gate still fires (order/throttle only); streams.md now names parallel+auto as the project default (opt-out) and stays internally consistent with the autonomy-throttle table below it.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (autonomous authorization) · date: 2026-06-15
Evidence: full suite 1064 green; 6 content tests; 3-tree parity held; wording lint green (slang fixed).

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): how often new projects keep vs downgrade the parallel+auto default (recorded in PROJECT.md Key Decisions) — a high downgrade rate means the default is wrong.
Spec delta for the next loop: setup-suggest-milestone + setup-domain-deepdive will extend the same setup flow; a future delta could let `add.py init` record the run-mode choice as state (the §1 assumption-2 path) if PROJECT.md prose proves too soft.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] a default-flip is safe to ship as a PROPOSAL + comparison table + confirm-to-keep — the human sees the flow before owning it; "show before ask" applies to defaults too (evidence: setup-run-mode shipped the philosophy shift behind a confirm, floor unchanged)
- [SDD · folded] the wording lint is a real guard on prose tasks — it caught "dial" slang the content tests would have passed; prose freezes need the lint in the green bar (evidence: test_ubiquitous_language went red on autonomy-dial, fixed to "autonomy level")
