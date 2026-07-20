# TASK: Heavy archive: compact done milestone/task files

slug: archive-compaction · created: 2026-06-07 · stage: mvp · autonomy: auto
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower
     the autonomy level with `autonomy: conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Heavy archive — `add.py compact <milestone>` moves an archived milestone's files out of the active tree
Framings weighed: move-dirs, bundle-per-milestone (chosen) · mirror-of-active-tree split · single ARCHIVE.md concatenation (lossy recovery) · delete+rely-on-git (recoverability must not depend on VCS)
Must:
<must>
  - `compact <slug>` moves the milestone dir (`milestones/<slug>/`, incl. `pre-archive-state.bak.json`)
    and every member task dir named by the archived rollup's `task_slugs` into one bundle:
    `.add/archive/<slug>/MILESTONE.md` (+ siblings) and `.add/archive/<slug>/tasks/<tslug>/`
  - operates ONLY on milestones already in `state["archived"]` — light archive
    (`archive-milestone`) is the mandatory first step; compact is step two
  - deltas folded first: every member TASK.md is scanned with the existing delta grammar
    before any move — an `open` competency delta anywhere in the bundle is a hard reject
  - validate-all-then-move: every precondition is checked before the first rename;
    any reject leaves the tree AND state.json byte-for-byte unchanged (mirrors
    `cmd_archive_milestone`'s validate-before-mutation discipline)
  - whole task dirs move (tests/ and src/ included) with a loud per-dir report of file
    counts moved — nothing leaves the active tree silently
  - the rollup entry gains an additive `compacted: <ISO date>` field — re-runs become a
    clean named reject and `status` can surface compaction; `task_slugs` is never touched,
    so the add.py:469 invariant (archived ⇒ was PASS-done; deps still resolve) holds untouched
  - recovery = reverse move: `mv` the bundle's parts back restores everything; no state
    edit is needed in either direction (state already dropped these at light archive)
</must>
Reject:
<reject>
  - slug exists as an ACTIVE milestone (not yet light-archived) -> "milestone_not_archived"
  - slug unknown anywhere (active or archived) -> "unknown_milestone"
  - any member TASK.md still holds an `open` competency delta -> "open_deltas_unfolded"
  - rollup entry already carries `compacted` -> "already_compacted"
  - destination `.add/archive/<slug>/` exists without a `compacted` stamp (collision) -> "archive_destination_exists"
  - milestone dir or any member task dir missing on disk -> "source_files_missing"
</reject>
After:
<after>
  - `.add/archive/<slug>/` holds MILESTONE.md (+ every other milestone-dir file) and
    `tasks/<tslug>/` for every rollup member; the active `milestones/<slug>/` and the
    member `tasks/<tslug>/` dirs no longer exist
  - `add.py deltas` output is unchanged (the folded-first precondition guarantees no
    open delta left `_collect_open_deltas`'s glob)
  - `status` · `audit` · `check` results are unchanged (state untouched except the
    additive rollup stamp; those commands iterate state, not the moved files)
  - re-running `compact <slug>` rejects with "already_compacted" — no second mutation
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ "_collect_open_deltas is the ONLY filesystem reader of `tasks/*` / `milestones/*` affected
    by a move" — lowest confidence because add.py is ~2400 lines and a missed glob-based
    reader would change a command's output silently after compaction (audit/check/report/
    _planned_unscaffolded verified state-driven or active-only; deltas handled by the
    folded-first reject); if wrong: a read-only command silently reports differently
    post-compact. Mitigation: harness test pins status+deltas+check output before/after.
  - [ ] adding a `compacted` field to an `archived[]` rollup entry is additive-safe —
    `_archived_task_slugs` reads only `task_slugs`; the status rollup line reads slug/count.
    Confirm in the red suite, not by inspection.
  - [ ] same-filesystem rename suffices (`.add/archive` shares the `.add/` parent with
    `tasks/`); no cross-device fallback needed for mvp.
  - [ ] orphan task dirs (on disk, in NO rollup and NOT in state) are out of scope —
    compact moves exactly the recorded members; today's tree reconciles exactly (79 = 48
    state + 31 archived).
  - [ ] this is the first engine edit since the ENGINE_MD5-tripwire delta: 5 pin tests
    re-stamp + 3-tree byte-identical propagation are build chores, planned in §4/§5 so
    the first red run isn't a surprise.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: compact moves an archived milestone into one bundle
  Given a milestone light-archived with two PASS-done member tasks (files on disk)
  When add.py compact <slug> runs
  Then .add/archive/<slug>/ holds MILESTONE.md, pre-archive-state.bak.json, and tasks/<tslug>/ for both members
  And the active milestones/<slug>/ and both tasks/<tslug>/ dirs no longer exist
  And the output names every moved dir with its file count (loud report)

Scenario: compact stamps the rollup additively
  Given a compactable archived milestone
  When compact succeeds
  Then the archived[] rollup entry carries compacted: <ISO date>
  And task_slugs is byte-identical (archived deps still resolve via _archived_task_slugs)

Scenario: read-only commands are unchanged by compaction
  Given status, deltas, and check output captured before compact
  When compact succeeds
  Then status, deltas, and check produce the same results afterward
  And audit stays clean with the same task count

Scenario: reverse move restores the bundle
  Given a compacted milestone
  When its bundle parts are moved back to milestones/<slug>/ and tasks/<tslug>/
  Then the active tree is byte-identical to its pre-compact snapshot
  And no state edit was needed in either direction

Scenario: open delta blocks compaction
  Given an archived milestone whose member TASK.md holds one `open` competency delta
  When compact runs
  Then it dies with "open_deltas_unfolded" naming the offending task
  And the tree and state.json remain byte-for-byte unchanged

Scenario: active milestone is rejected
  Given a milestone still in state["milestones"] (never light-archived)
  When compact runs
  Then it dies with "milestone_not_archived"
  And the tree and state.json remain byte-for-byte unchanged

Scenario: unknown slug is rejected
  Given a slug in neither active milestones nor the archived rollup
  When compact runs
  Then it dies with "unknown_milestone"
  And the tree and state.json remain byte-for-byte unchanged

Scenario: re-run is a clean reject, not a second mutation
  Given a milestone already compacted (rollup stamped)
  When compact runs again
  Then it dies with "already_compacted"
  And the archive bundle and state.json remain byte-for-byte unchanged

Scenario: unstamped destination collision is rejected
  Given .add/archive/<slug>/ exists but the rollup carries no compacted stamp
  When compact runs
  Then it dies with "archive_destination_exists"
  And the existing destination, the tree, and state.json remain unchanged

Scenario: missing source files are rejected before any move
  Given an archived milestone whose member task dir was hand-deleted from disk
  When compact runs
  Then it dies with "source_files_missing" naming the missing path
  And no partial move happened — the tree and state.json remain unchanged
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add.py compact <milestone-slug>
  ok  -> exit 0; stdout reports: the slug, the destination `.add/archive/<slug>/`,
         and one line PER moved dir with its file count (loud report — nothing silent)
         state: archived[] rollup entry += `compacted: "<YYYY-MM-DD>"` (additive;
         `task_slugs` byte-identical — add.py:469 invariant untouched)
  err -> exit non-zero; stderr names exactly one of
         "milestone_not_archived" | "unknown_milestone" | "open_deltas_unfolded" |
         "already_compacted" | "archive_destination_exists" | "source_files_missing"
         and the tree + state.json stay byte-for-byte unchanged (validate-all-then-move)
Schema: state.json archived[] gains the optional `compacted` field — no other state shape change.
        FS move: `milestones/<slug>/**` -> `.add/archive/<slug>/**` and, per rollup member,
        `tasks/<tslug>/**` -> `.add/archive/<slug>/tasks/<tslug>/**`; same-filesystem renames,
        executed only after EVERY precondition passed.
MIRRORS: the engine ships byte-identical in THREE trees — `add-method/tooling/add.py` ·
        `.add/tooling/add.py` · `add-method/src/add_method/_bundled/tooling/add.py`;
        the build propagates to all three.
TRIPWIRES: the 5 ENGINE_MD5 pin tests re-stamp to the new engine hash — the SOLE
        sanctioned test edit of this build; any other test edit is a violation.
```

Status: FROZEN @ v1 — approved by Tin Dang, 2026-06-07 (one-approval front; autonomy: auto; flag #2 ratified: the stamp enables surfacing, this build leaves `status` rendering unchanged)
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + all 6 reject codes exercised (10 scenarios -> ≥10 tests); harness pattern reused from test_template_form_tags.py (temp project: init -> new-task -> gate PASS -> milestone-done -> archive-milestone -> compact)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_compact_moves_bundle: arrange archived milestone w/ 2 done tasks / act compact / assert destination layout + sources gone + per-dir counts in stdout
  - test_rollup_stamped_additively: act compact / assert `compacted` date on rollup + `task_slugs` byte-identical
  - test_readonly_commands_unchanged: capture status+deltas+check before / act compact / assert identical after (⚠-assumption mitigation)
  - test_reverse_move_restores: act compact then mv parts back / assert tree byte-identical to pre-compact snapshot
  - test_open_delta_blocks: plant one `open` delta in a member TASK.md / act / assert "open_deltas_unfolded" + tree/state unchanged
  - test_active_milestone_rejected: act on never-archived milestone / assert "milestone_not_archived" + unchanged
  - test_unknown_slug_rejected: act on bogus slug / assert "unknown_milestone" + unchanged
  - test_rerun_rejected: compact twice / assert "already_compacted" + bundle/state unchanged
  - test_destination_collision_rejected: pre-create unstamped destination / act / assert "archive_destination_exists" + unchanged
  - test_missing_source_rejected: hand-delete a member dir / act / assert "source_files_missing" + NO partial move
  - test_engine_triplet_parity: assert all three add.py trees byte-identical (md5)
</test_plan>

Tests live in: `add-method/tooling/test_archive_compaction.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): validate-all-then-move — no rename before EVERY precondition passes; compact never deletes, only moves (reverse-move recovery); state write is the LAST step
Code lives in: `add-method/tooling/add.py` (cmd_compact + parser; propagated byte-identically to the dogfood and _bundled trees)
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 562/562 OK (551 prior + 11 new: 10 behavior + 1 triplet-parity guard)
- [x] coverage did not decrease — suite grew 551 -> 562; happy path + all 6 reject codes exercised
- [~] no test or contract was altered during build — frozen §3 untouched; tripwire re-stamps as
      contracted. DISCLOSED RESIDUE: two instrument reactions exceeded the "sole sanctioned test
      edit" clause — (1) test_min_pillar LIFECYCLE gained `["compact", "mvp"]` (the instrument's
      own self-maintenance protocol: a new subcommand FAILS it until classified; additive coverage,
      no assertion weakened); (2) one emitted prose string reworded "fold" -> "consolidate" to
      satisfy test_ubiquitous_language (engine change, not a test edit; the frozen reject code
      `open_deltas_unfolded` is untouched — `\bfold\b` never matches inside it)
- [x] concurrency / timing of the risky operation is safe — single-process CLI; validate-all-
      then-move (no rename before every precondition passes); same-filesystem renames; never a
      delete; state write is the LAST step; mid-move interruption stays reverse-move recoverable
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only; no shell,
      no eval; the slug is gated against state's archived rollup BEFORE any path use (a hostile
      slug dies at unknown_milestone; poisoning state.json is the tool's existing trust boundary)
- [x] layering & dependencies follow CONVENTIONS.md — single-file engine idiom, mirrors
      cmd_archive_milestone's validate-before-mutation pattern; reuses _collect_open_deltas
- [x] a person reviewed and approved the change — gate presented with both residues disclosed;
      human selected PASS

### GATE RECORD
Outcome: PASS — two instrument residues accepted as disclosed (LIFECYCLE classification of the
new subcommand; "fold" -> "consolidate" prose rewording). No security finding: the security
line item was escalated to the human, never auto-passed.
Reviewed by: Tin Dang · date: 2026-06-07

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): per-reject-code hit rate on real usage (expect mostly
open_deltas_unfolded — it is the educational one) · the 8-milestone backlog compaction as first
production run · reverse-move recoveries needed (target: 0)
Spec delta for the next loop: none yet — the backlog compaction is the first production use;
revisit after it runs.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
  - [SDD · folded] "sole sanctioned test edit" clauses under-enumerate the same way mirror clauses
    did: SELF-MAINTAINING instruments (min_pillar's LIFECYCLE census, the ubiquitous-language
    prose ban) react to ANY new CLI verb — a contract adding a subcommand should pre-declare the
    instrument-reaction class (evidence: 2 disclosed residues at this gate)
  - [TDD · folded] run the FULL suite once during the tests phase, not only the new file — both
    instrument reactions were discoverable pre-freeze and would have entered the contract instead
    of the residue list (evidence: test_min_pillar + test_ubiquitous_language failed only at the
    first full-suite build run)
  - [ADD · folded] archive is now a two-step lifecycle (archive-milestone -> compact) — the
    milestone-close fold-pressure nudge and fold.md could name compact as the step after
    consolidation (evidence: cmd_compact landed; status nudge still ends at the fold)
  - [DDD · folded] "compact" / "heavy archive" / "recovery bundle" entered the language — GLOSSARY
    should carry them at the next retrospective consolidation (evidence: new CLI verb + the
    .add/archive/ namespace)
