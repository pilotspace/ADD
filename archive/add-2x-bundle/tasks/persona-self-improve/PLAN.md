# TASK: observe->delta->fold grows project personas from real usage without clobbering

slug: persona-self-improve · created: 2026-06-29 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. Multi-component repo (monorepo/multi-repo)? add a `component: <name>` line (declared in `.add/components.toml`) to ADD that component's root to your §5 Scope; omit for single-component projects (byte-identical default). -->
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

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/add_engine/constants.py` `add-method/tooling/add_engine/taskdoc.py` `add-method/skill/add/fold.md` `add-method/skill/add/deltas.md` `add-method/tooling/test_persona_self_improve.py` `add-method/tooling/engine_pin.py` `.add/tooling/add.py` `.add/tooling/add_engine/constants.py` `.add/tooling/add_engine/taskdoc.py` `.claude/skills/add/fold.md` `.claude/skills/add/deltas.md` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add_engine/constants.py` `add-method/src/add_method/_bundled/tooling/add_engine/taskdoc.py` `add-method/src/add_method/_bundled/skill/add/fold.md` `add-method/src/add_method/_bundled/skill/add/deltas.md`
Strategy (ordered batches): 1. add.py cmd_fold — add the persona route (parse `persona:<slug>` + section hint; prepend into `.add/personas/<slug>.md`; reject missing-target/unroutable; reuse `_persona_missing` to assert conformance; design-for-failure — validate before any write). 2. fold.md — add the persona-route row to the routing table; deltas.md — document the optional `persona:<slug>` annotation. 3. mirror byte-identically (engine ×3 + skill ×3). 4. tests. 5. re-aim both engine pins. 6. lean fence if fold.md/deltas.md pool trips. Run red→green per batch.
Known-problem fixes: validate-then-write so a reject never half-writes (mirror lock/init atomicity) · a folded lesson must be skipped on re-gather (idempotent) — reuse the existing `folded` status filter · prepend must not corrupt the `## <section>` header (insert after the header line) · editing add.py re-aims BOTH pins · NO-EXEC scan must cover the new cmd_fold branch.
Strategy actually used: As planned, with one design correction. (1) Extended `_DELTA_RE` (constants.py) with an OPTIONAL **non-capturing** persona clause between status and `]` (group numbering 1/2/3 = comp/status/text UNCHANGED) + a sibling `_PERSONA_TAG_RE` that pulls slug+hint when a route needs them; `_COMP_OPEN_TOKEN_RE` extended so the open→folded flip preserves the persona annotation. (2) cmd_fold partitions selected lessons into persona vs foundation, validates persona ones fail-closed BEFORE any write (slug valid + file exists → else `missing_persona_target`; hint in {critical-rule,success-metric} → else `persona_section_unroutable`), then prepends a dated bullet under the hinted §section via `_prepend_to_section`, asserts never-clobber (multiset of prior lines ⊆ merged) + post-merge `_persona_missing==[]` (→ `persona_clobber_forbidden`), and joins the persona writes into the same `_atomic_write_many` batch. (3) fold.md routing row + reject codes, deltas.md grammar bullet. (4) mirrored ×3 engine + ×3 skill, both pins re-aimed. CORRECTION: my first pass used NAMED groups in `_DELTA_RE`, which hid the literal `(DDD|SDD|UDD|TDD|ADD)` the grammar-dedup test counts → reverted to positional + a separate persona regex (zero blast radius on the 3 existing callers).
Safety rule (feature-specific): never clobber persona content (prepend-only); fail-closed on a missing target; NO-EXEC on the fold path.
Code lives in: `add-method/tooling/` + `add-method/skill/add/`
Constraints: do NOT change any test or the contract; do NOT add a version field to the frozen persona schema; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite **2448/0** (`python3 -m unittest discover`); `add.py check` 518/0 (29 warnings); `add.py audit` clean for this task (repo-wide risk/sensitivity_unset are measure-not-block).
- [x] coverage did not decrease — +7 new tests in `test_persona_self_improve.py`, one per scenario; no test deleted.
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; all test edits were done in the TESTS phase (the surface-test ripples in delta-grammar-dedup / ubiquitous-language / skill-lean were fixed by correcting the engine/docs TOKENS, never the tests).
- [x] the green was EARNED, not gamed — refute-read below.
- [x] concurrency / timing of the risky operation is safe — validate-all-then-write; persona writes ride the same `_atomic_write_many` all-or-nothing batch as PROJECT/CONVENTIONS/TASK.
- [x] no exposed secrets, injection openings, or unexpected dependencies — no new deps; slug path-traversal blocked by `_persona_slug_valid` (alnum + `-`/`_` only); no network, no child launch.
- [x] layering & dependencies follow CONVENTIONS.md — reuses `_prepend_to_section`, `_persona_missing`, `_atomic_write_many`; engine stays NO-EXEC; no new engine.
- [x] a person reviewed and approved the change — pending Tin's review at the milestone PR (auto-gated under `autonomy: auto`).

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
- [x] running fold on a persona lesson prepends one dated bullet under the right section, all prior content intact — `test_persona_lesson_folds_prepended_no_clobber` asserts the bullet lands under `## Success Metrics`, precedes the prior metric, and every pre-existing line survives byte-for-byte.
- [x] `_persona_missing` returns [] on the merged file — `test_persona_conformant_after_fold`.
- [x] a missing persona target rejects with nothing written and no version bump — `test_missing_persona_target_rejects` (full-tree snapshot byte-unchanged + fv unchanged).
- [x] no network/spawn on the fold-into-persona path; pins re-aimed; parity holds — `test_fold_persona_no_exec` (static scan + offline run) + `test_fold_persona_3tree_parity` (byte-identical trees + ENGINE_MD5 re-aimed).

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — persona route in `cmd_fold` (add.py ~5520-5630): partition `persona_sel`/`found_sel` → fail-closed validation loop → `_persona_bullet` + `_prepend_to_section` transcribe loop → writes joined into `_atomic_write_many`. Grammar in `_DELTA_RE` + `_PERSONA_TAG_RE` (constants.py); flip-preservation in `_COMP_OPEN_TOKEN_RE` (add.py); slug+hint capture in `_collect_open_deltas`.
- [x] DEAD-CODE (code) — no new unused symbol; `_PERSONA_FOLD_SECTIONS`, `_PERSONA_TAG_RE`, `_persona_bullet` all referenced.
- [x] SEMANTIC (prose / non-code) — read the edited fold.md/deltas.md in full: routing table row + reject codes + the persona grammar bullet all match the engine behavior; retired-codes note retained for the machine-token pin; lean fence re-cleared by reclaiming prose from the same two guides (ratios kept; `test_skill_lean` untouched).

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self · adversarially checked: probed for vacuity (reject tests assert a full-tree byte snapshot + no version bump, not just an error string), path traversal (`../..` slug → `_persona_slug_valid` False → `missing_persona_target`), idempotency (the open→folded flip preserves the persona annotation via `_COMP_OPEN_TOKEN_RE`; re-gather skips non-`open`, so no double-apply), never-clobber (multiset subset guard would fire on any dropped line), and atomicity (every validation `_die`s before any write). No overfit, no stubbed-away logic.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
Advisor: self
1. Security: CLEAR — slug path-confined by `_persona_slug_valid` (alnum + `-`/`_`); a traversal/empty slug fails closed to `missing_persona_target`. No network/child-launch on the path (static scan + offline run).
2. Concurrency: CLEAR — validate-all-then-write; persona writes join the existing all-or-nothing `_atomic_write_many` batch (a stage/rename failure rolls back every file). No new shared state.
3. Architecture: CLEAR — reuses the judgment-free fold loop + `_persona_missing` + `_prepend_to_section`; no new learning engine; engine stays NO-EXEC.
Verdict: PASS
Residue: none
Binding: yes — mechanical (deterministic doc-truth + engine routing; tests + check + audit green).

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang (auto-resolved under autonomy: auto) · date: 2026-06-29

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <persona-fold adoption / clobber regressions>

### Decisions (ADR)
- [AI] specify — chose extend cmd_fold + the delta grammar with a persona route; rejected a dedicated `add.py persona-learn` command (rejected — a parallel learning engine the milestone forbids) · manual hand-edit of persona files only (rejected — not a loop; no traceability)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: As planned, with one design correction. (1) Extended `_DELTA_RE` (constants.py) with an OPTIONAL **non-capturing** persona clause between status and `]` (group numbering 1/2/3 = comp/status/text UNCHANGED) + a sibling `_PERSONA_TAG_RE` that pulls slug+hint when a route needs them; `_COMP_OPEN_TOKEN_RE` extended so the open→folded flip preserves the persona annotation. (2) cmd_fold partitions selected lessons into persona vs foundation, validates persona ones fail-closed BEFORE any write (slug valid + file exists → else `missing_persona_target`; hint in {critical-rule,success-metric} → else `persona_section_unroutable`), then prepends a dated bullet under the hinted §section via `_prepend_to_section`, asserts never-clobber (multiset of prior lines ⊆ merged) + post-merge `_persona_missing==[]` (→ `persona_clobber_forbidden`), and joins the persona writes into the same `_atomic_write_many` batch. (3) fold.md routing row + reject codes, deltas.md grammar bullet. (4) mirrored ×3 engine + ×3 skill, both pins re-aimed. CORRECTION: my first pass used NAMED groups in `_DELTA_RE`, which hid the literal `(DDD|SDD|UDD|TDD|ADD)` the grammar-dedup test counts → reverted to positional + a separate persona regex (zero blast radius on the 3 existing callers).
- [AI] verify — gate PASS (reviewed by Tin Dang (auto-resolved under autonomy: auto))

### Spec delta
Forward changes for the next loop — one line each, tagged `[SPEC · open|seeded|dropped]`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency (`DDD · SDD · UDD · TDD · ADD`), status `open`.
