# TASK: observe->delta->fold grows project personas from real usage without clobbering

slug: persona-self-improve · created: 2026-06-29 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. Multi-component repo (monorepo/multi-repo)? add a `component: <name>` line (declared in `.add/components.toml`) to ADD that component's root to your §5 Scope; omit for single-component projects (byte-identical default). -->
phase: contract   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/add.py:cmd_fold` — the judgment-free consolidation: it TRANSCRIBES each confirmed `open` lesson into its routed home (PROJECT.md §Domain/§Spec/§Users/… per competency) and bumps `foundation-version`. THIS task adds a persona route: a `persona:<slug>` lesson transcribes into `.add/personas/<slug>.md`.
  - `add-method/skill/add/fold.md:## Consolidation routing` (≈23-35) — the competency→section routing table; a persona-target row joins here. 3 skill trees.
  - `add-method/skill/add/deltas.md` — the lesson grammar (`[<competency> · <status>] <text>`); THIS task extends it with an optional `persona:<slug>` target annotation. 3 skill trees.
  - `add-method/tooling/add_engine/predicates.py:_persona_missing` (persona-setup) — re-used to assert the persona file stays schema-conformant AFTER a fold merge.
  - `add-method/tooling/test_fold_*` / fold tests — the pattern the new fold-into-persona test mirrors.
Context (working folder):
  - `.add/milestones/persona-learning-loop/MILESTONE.md` — shared decision: self-improvement REUSES ADD's existing observe→delta→`fold` loop; NO new learning engine. The persona is grown from real usage; the LEARNING is dynamic, the APPLIED persona is recorded/frozen.
  - `.add/personas/<slug>.md` (FROZEN schema, persona-setup) — the merge TARGET; `## Critical Rules` + `## Success Metrics` are the growable sections.
Honors (patterns / conventions):
  - fold is JUDGMENT-FREE — it only transcribes captured text + stamps `folded`; it never composes/merges prose and never self-approves (running the command IS the human confirmation).
  - survivor never-clobber — a persona fold PREPENDS (newest-first) under the target section; it NEVER overwrites existing persona content.
  - the persona schema stays conformant after the merge (re-use `_persona_missing` to assert).
  - engine NO-EXEC; 3-tree engine parity + 3-tree skill parity; red/green TDD.
Anchors the contract cites: cmd_fold persona routing · the `persona:<slug>` delta annotation · `.add/personas/<slug>.md` `## Critical Rules`/`## Success Metrics` prepend (never clobber) · the post-merge schema-conformance invariant.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Personas self-improve through the EXISTING loop — an observe-phase lesson can target a project persona (`persona:<slug>` annotation on a competency delta); `add.py fold` then judgment-free-transcribes that lesson's captured text into `.add/personas/<slug>.md` under `## Critical Rules` or `## Success Metrics`, PREPENDED (newest-first), NEVER clobbering existing content, stamped `folded`. The persona file stays schema-conformant after the merge. No new learning engine; reuses delta→fold.
Framings weighed: extend cmd_fold + the delta grammar with a persona route (chosen — reuses the existing judgment-free loop, no new engine) · a dedicated `add.py persona-learn` command (rejected — a parallel learning engine the milestone forbids) · manual hand-edit of persona files only (rejected — not a loop; no traceability)
Must:
<must>
  - The delta grammar accepts an optional `persona:<slug>` target on a competency lesson (e.g. `[UDD · open · persona:ui-designer · success-metric] 4.5:1 contrast (evidence: audit)`); a section hint (critical-rule | success-metric) routes which persona section it lands in.
  - `add.py fold` routes a confirmed `persona:<slug>` lesson into `.add/personas/<slug>.md` under the named section, PREPENDED newest-first, stamped `folded` — judgment-free transcription (no prose composition).
  - Never clobber: existing persona content is preserved byte-for-byte except the prepended line; re-running fold does not duplicate an already-folded lesson (a `folded` lesson is not re-gathered).
  - After the merge the persona file is still schema-conformant (`_persona_missing` returns `[]`); the four required sections survive.
  - Fail-closed: a `persona:<slug>` whose file does not exist -> reject `missing_persona_target`, write nothing, bump nothing.
  - The engine performs NO network IO and NO spawn on the fold-into-persona path; 3-tree engine + skill parity.
</must>
Reject:
<reject>
  - a `persona:<slug>` target whose `.add/personas/<slug>.md` does not exist -> "missing_persona_target"
  - a persona lesson naming a section that is not a growable persona section -> "persona_section_unroutable"
  - a fold that overwrites or drops existing persona content -> "persona_clobber_forbidden"
  - the engine spawning or fetching on the fold path -> "fold_engine_no_exec"
</reject>
After:
<after>
  - A confirmed persona lesson flows observe→delta→fold and prepends to the target persona file under the right section, stamped folded, never clobbering; a test asserts the merge.
  - The persona file remains schema-conformant after the merge; re-fold is idempotent (folded lessons are not re-applied).
  - A missing persona target rejects fail-closed; no engine network/spawn on the path.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ whether a persona fold should bump the existing `foundation-version` (PROJECT.md) or carry its OWN per-persona stamp — lowest confidence because personas are a separate living doc from PROJECT.md; if wrong: the version semantics confuse (a persona edit bumping the foundation version) OR a new per-persona version field reopens the persona-setup schema. (Mitigation: stamp the folded lesson + prepend a dated line in the persona section; do NOT add a version field to the persona schema — reuse the lesson's `[folded foundation-version N]` stamp on the DELTA side only.)
  - [ ] section routing via an explicit hint (critical-rule | success-metric) vs inferring from the competency tag — if wrong: infer the section (UDD→success-metric, etc.) and drop the hint.
  - [ ] prepend (newest-first) matches the existing fold convention for personas too — if wrong: append-at-section-end instead.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: a confirmed persona lesson folds into the persona file without clobbering
  Given .add/personas/ui-designer.md with existing Critical Rules and Success Metrics
  And an observe delta "[UDD · open · persona:ui-designer · success-metric] 4.5:1 contrast (evidence: audit)"
  When add.py fold runs (the human confirmation)
  Then the line is prepended under "## Success Metrics" in ui-designer.md
  And every pre-existing rule and metric is preserved byte-for-byte

Scenario: the persona stays schema-conformant after the merge
  Given a persona fold just completed
  When _persona_missing is evaluated on the merged file
  Then it returns [] (all four required sections survive)

Scenario: re-running fold does not duplicate an already-folded lesson (idempotent)
  Given a persona lesson already stamped folded
  When add.py fold runs again
  Then the persona file is unchanged
  And the lesson is not transcribed twice

Scenario: a missing persona target is rejected fail-closed
  Given a delta "[UDD · open · persona:ghost] ..." with no .add/personas/ghost.md
  When add.py fold runs
  Then it rejects with missing_persona_target
  And nothing is written and no version is bumped

Scenario: an unroutable persona section is rejected
  Given a persona lesson naming a non-growable section
  When add.py fold runs
  Then it rejects with persona_section_unroutable
  And the persona file is unchanged

Scenario: the fold-into-persona path is NO-EXEC
  Given the cmd_fold persona-routing code path
  When it executes
  Then no network IO and no spawn occurs
  And the fold completes offline

Scenario: the change is byte-identical across engine and skill trees
  Given the cmd_fold + fold.md/deltas.md edits
  When the trees are compared
  Then the change is byte-identical in each
  And the parity tests pass
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

PERSONA DELTA ANNOTATION — extends the `deltas.md` lesson grammar
  (described inline — no bare triple-dash / line-start `##` so the §3 span stays intact)
  • A competency lesson MAY carry a `persona:<slug>` target plus a section hint:
    `[<competency> · <status> · persona:<slug> · <critical-rule|success-metric>] <captured text>`
  • The annotation is OPTIONAL — a lesson without it folds into PROJECT.md as today (unchanged).

FOLD ROUTING — `add.py fold` (cmd_fold) gains a persona route (judgment-free transcription)
  • A confirmed `open` lesson with a `persona:<slug>` target transcribes its captured text into
    `.add/personas/<slug>.md` under `## Critical Rules` (hint critical-rule) or `## Success Metrics`
    (hint success-metric), PREPENDED newest-first as one dated bullet; the lesson is stamped `folded`.
  • NEVER CLOBBER: only the new bullet is inserted; all existing persona bytes are preserved. A
    `folded` lesson is not re-gathered (idempotent re-fold).
  • POST-MERGE INVARIANT: `_persona_missing(merged) == []` — the four required sections survive.
  • VERSION: the persona fold reuses the DELTA-side `folded` stamp; it does NOT add a version field
    to the persona schema (the schema stays as persona-setup froze it). (Flagged below.)

ERROR CODES (every §1 Reject has a contracted response)
  missing_persona_target     -> `persona:<slug>` with no `.add/personas/<slug>.md` — reject, write
                                nothing, bump nothing (fail-closed; design-for-failure).
  persona_section_unroutable -> a section hint that is not `critical-rule|success-metric` — reject.
  persona_clobber_forbidden  -> INVARIANT: a fold that would overwrite/drop existing content is a bug;
                                the merge is prepend-only.
  fold_engine_no_exec        -> INVARIANT: the fold-into-persona path performs no network IO, no spawn.

PARITY — cmd_fold change byte-identical across the 3 engine trees; fold.md + deltas.md across the 3
  skill trees; both engine pins (ENGINE_MD5 + ENGINE_PKG_MD5) re-aimed.

VERIFICATION — tests assert: a persona lesson folds + prepends + never clobbers · schema-conformant
  after · idempotent re-fold · missing-target + unroutable-section reject · NO-EXEC on the path · parity.

Least-sure flag surfaced at freeze: ⚠ [contract] version semantics — a persona fold reuses the
delta-side `folded`/`[folded foundation-version N]` stamp and does NOT add a version field to the
persona file (that would reopen the persona-setup frozen schema). If a per-persona version is later
needed, it is a change request to persona-setup. Mitigation: keep the persona schema untouched; the
fold's traceability lives on the DELTA, plus a dated bullet in the persona section.

Status: FROZEN @ v1 — approved by Tin Dang
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag. -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + Reject scenario has one test (new symbols 100%)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_persona_lesson_folds_prepended_no_clobber: a confirmed persona success-metric lesson prepends under "## Success Metrics" and preserves all prior content
  - test_persona_conformant_after_fold: `_persona_missing` returns [] on the merged file
  - test_refold_idempotent: a folded persona lesson is not transcribed twice; file unchanged on re-run
  - test_missing_persona_target_rejects: `persona:ghost` with no file -> missing_persona_target, nothing written, no version bump
  - test_unroutable_section_rejects: a bad section hint -> persona_section_unroutable, file unchanged
  - test_fold_persona_no_exec: scan cmd_fold persona-routing path -> no socket/urllib/subprocess/spawn; offline fold succeeds
  - test_fold_persona_3tree_parity: cmd_fold + fold.md + deltas.md byte-identical across trees; pins re-aimed
</test_plan>

Tests live in: `add-method/tooling/test_persona_self_improve.py` · MUST run red before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/skill/add/fold.md` `add-method/skill/add/deltas.md` `add-method/tooling/test_persona_self_improve.py` `add-method/tooling/engine_pin.py` `.add/tooling/add.py` `.claude/skills/add/fold.md` `.claude/skills/add/deltas.md` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/src/add_method/_bundled/skill/add/fold.md` `add-method/src/add_method/_bundled/skill/add/deltas.md`
Strategy (ordered batches): 1. add.py cmd_fold — add the persona route (parse `persona:<slug>` + section hint; prepend into `.add/personas/<slug>.md`; reject missing-target/unroutable; reuse `_persona_missing` to assert conformance; design-for-failure — validate before any write). 2. fold.md — add the persona-route row to the routing table; deltas.md — document the optional `persona:<slug>` annotation. 3. mirror byte-identically (engine ×3 + skill ×3). 4. tests. 5. re-aim both engine pins. 6. lean fence if fold.md/deltas.md pool trips. Run red→green per batch.
Known-problem fixes: validate-then-write so a reject never half-writes (mirror lock/init atomicity) · a folded lesson must be skipped on re-gather (idempotent) — reuse the existing `folded` status filter · prepend must not corrupt the `## <section>` header (insert after the header line) · editing add.py re-aims BOTH pins · NO-EXEC scan must cover the new cmd_fold branch.
Strategy actually used: <fill at VERIFY>
Safety rule (feature-specific): never clobber persona content (prepend-only); fail-closed on a missing target; NO-EXEC on the fold path.
Code lives in: `add-method/tooling/` + `add-method/skill/add/`
Constraints: do NOT change any test or the contract; do NOT add a version field to the frozen persona schema; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all tests pass
- [ ] coverage did not decrease
- [ ] no test or contract was altered during build
- [ ] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [ ] concurrency / timing of the risky operation is safe
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
- [ ] running fold on a persona lesson prepends one dated bullet under the right section, all prior content intact — confirmed by a before/after read + diff
- [ ] `_persona_missing` returns [] on the merged file — confirmed by the conformance test
- [ ] a missing persona target rejects with nothing written and no version bump — confirmed by the reject test + state compare
- [ ] no network/spawn on the fold-into-persona path; pins re-aimed; parity holds — confirmed by the NO-EXEC + parity + pin tests

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [ ] WIRING (code) — the new cmd_fold branch + any helper referenced; record where
- [ ] DEAD-CODE (code) — no new unused symbol
- [ ] SEMANTIC (prose / non-code) — read the edited fold.md/deltas.md in full: <what confirmed>

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: <EARNED | NOT-EARNED>
By: <self | agent-id> · adversarially checked: <what was probed>

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
Advisor: <agent-id | self>
1. Security: <CLEAR | HARD-STOP: finding>
2. Concurrency: <CLEAR | RESIDUE: finding>
3. Architecture: <CLEAR | RESIDUE: finding>
Verdict: <PASS | HARD-STOP>
Residue: <none | summary>
Binding: <yes — mechanical | advisory — <sensitivity>>

### GATE RECORD
Outcome: <PASS | RISK-ACCEPTED | HARD-STOP>
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: <name> · date: <date>

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <persona-fold adoption / clobber regressions>

### Decisions (ADR)
<harvested at done from §1/§3/§5/§6 — do not hand-edit>

### Spec delta
Forward changes for the next loop — one line each, tagged `[SPEC · open|seeded|dropped]`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency (`DDD · SDD · UDD · TDD · ADD`), status `open`.
