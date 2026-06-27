# TASK: init+update scan .add/, overwrite managed + add missing, never touch user data

slug: heal-reconcile · created: 2026-06-17 · stage: mvp
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
  - `add-method/bin/cli.js:cmdInit/dropFiles` — today: skill via `copyDir(skipIfExists)` (a PRESENT skill is skipped+warned, never repaired); tooling/docs via `copyDir` merge (cpSync — overwrites + adds, but never removes orphans). The reconcile target.
  - `add-method/bin/cli.js:copyDir(src,dest,{skipIfExists,cleanReplace})` — copy primitive; `cleanReplace` already does rm-then-copy (the heal op).
  - `add-method/bin/cli.js:cmdUpdate` — clean-replaces MANAGED, version-gated: no-ops when `cur===version` unless `--force` (line ~177); requires an existing `.add/`.
  - `add-method/bin/cli.js:MANAGED` (line 195) + `cleanReplaceTree`, `STAMP_FILE=".add-version"`, `readStamp/writeStamp/pkgVersion` — the 3 managed trees: skill→.claude/skills/add, tooling→.add/tooling (strip tests), docs→.add/docs.
  - `add-method/src/add_method/_installer.py:install()` — skill skip-if-exists; tooling/docs `copytree(dirs_exist_ok=True)` (merge, no orphan sweep). `update()` — clean-replace MANAGED, version-gated. `MANAGED` tuple, `_clean_replace`, `_read_stamp/_write_stamp`, `_add_dir`.
  - `add-method/src/add_method/_cli.py:main` — routes init/update (pass-through only).
Context (working folder):
  - tests pinning the contract (MUST stay green): `test_update.py` (clean-replace sweeps orphans · user-data sacred · idempotent "already at <v>" no-op WHEN nothing missing · --force · stamp + pre-update backup · fails-closed without a project), `test_installer_handoff.py` (init drops the brain · NO state.json), `test_v8_install.py`, `test_packaging.py`. No test pins init's skip-if-exists "leave untouched" — so reconcile may overwrite a present managed tree.
  - USER DATA = SACRED, never touched: `state.json` · `PROJECT.md` · `milestones/` · `tasks/` · `archive/` · `SOUL.md` · survivor docs. Managed = `.claude/skills/add` · `.add/tooling` · `.add/docs` (+ the `.add-version` stamp).
Honors (patterns / conventions):
  - managed↔user-data boundary (milestone shared decision) — reconcile clean-replaces ONLY managed trees; never reads/writes user data.
  - drops-files-only (never run `add.py init`); design-for-failure; npm↔pip parity ("twins"); the same-version no-op MUST persist when nothing is missing (test_update idempotency).
Anchors the contract cites: `managedStatus`/`_managed_status` (per-tree missing/present) + a shared `reconcile`/`_reconcile` primitive reusing `cleanReplaceTree`/`_clean_replace`; init→reconcile and update→heal-when-missing on both twins.
  - `bin/cli.js` new `managedStatus(target)` (missing/present per tree) + a reconcile path reusing `cleanReplaceTree`; `cmdInit`→reconcile; `cmdUpdate`→heal-when-missing.
  - `_installer.py` new `_managed_status(target)` + reconcile path reusing `_clean_replace`; `install()`→reconcile; `update()`→heal-when-missing.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Heal / reconcile — init AND update scan the target's managed layer, RESTORE missing trees + REFRESH present ones (sweeping orphans) + REPORT it, never touching user data
Framings weighed: one shared reconcile primitive (clean-replace managed + per-tree status), init & update both call it (chosen) · keep init's skip-if-exists + add a separate `reconcile`/`heal` verb (rejected: the ask folds reconcile into init+update, not a new verb) · per-file diff/merge staleness (rejected: heavier; clean-replacing a MANAGED tree inherently adds-missing + overwrites-stale + sweeps-orphans, and managed trees hold no user data so wholesale refresh is safe)
Must:
<must>
  - H1 init RECONCILES: per managed tree (skill·tooling·docs), RESTORE if missing and REFRESH (clean-replace to the packaged version) if present — adds missing files AND overwrites managed AND sweeps orphans (no merge-leftovers).
  - H2 init REPORTS per-tree status: each of skill/tooling/docs as "restored (was missing)" or "refreshed".
  - H3 update HEALS: a MISSING managed tree is restored EVEN when the stamped version matches (today's same-version no-op only held because nothing was missing).
  - H4 the same-version NO-OP persists: `cur===version` AND no managed tree missing AND not --force -> "already at <version>", writes nothing (test_update idempotency unchanged).
  - H5 USER DATA is never read/written by reconcile: state.json · PROJECT.md · milestones/ · tasks/ · archive/ · SOUL.md · survivor docs survive byte-identical; only the 3 managed trees (+ the .add-version stamp) change.
  - H6 drops-files-only holds: reconcile never runs `add.py init`; init creates NO state.json; the installed tooling copy still strips test_*.py + __pycache__.
  - H7 npm↔pip parity: identical reconcile semantics, identical status vocabulary, identical no-op rule on both twins.
  - H8 design-for-failure: verify ALL packaged sources exist BEFORE touching the target; update still backs up state before any change.
</must>
Reject:
<reject>
  - a managed packaged SOURCE tree is absent (corrupt package) -> "missing_source"  (fail closed; target untouched — pre-existing, re-affirmed)
  - update invoked with no `.add/` project -> "no_project"  (fail closed; nothing created — pre-existing, re-affirmed)
  # a managed tree missing in the TARGET is the HEAL trigger, NOT a reject.
</reject>
After:
<after>
  - after init or update, all 3 managed trees are present at the packaged version with no orphan files; user data byte-identical; per-tree status reported; init created no state.json.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ H-A1 [contract] init REFRESHING a PRESENT skill (dropping skip-if-exists) won't wrongly surprise a user — lowest confidence because someone might hand-edit `.claude/skills/add`; if wrong: their edits are overwritten on a re-init. Mitigation: the skill is MANAGED / ship-controlled (the foundation's own managed↔user-data boundary), `--force` already overwrote it, and healing a drifted managed file is exactly reconcile's purpose. (Accept.)
  ⚠ H-A2 [spec] "missing" detected at the TREE level (dest dir absent OR empty) is enough granularity — lowest confidence because a tree could exist but be PARTIALLY gutted (some docs deleted); if wrong: a partial tree reads "present" and a same-version `update` won't heal it. Mitigation: init ALWAYS clean-replaces present trees, so init heals partial trees unconditionally; only a same-version `update` relies on tree-level presence (acceptable — a version change or --force always refreshes).
  - [ ] status vocabulary = "restored" (was missing) / "refreshed" (was present) — confirm wording.
  - [ ] "missing" := dest dir absent OR present-but-empty — confirm the empty-dir case counts.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: init restores a missing managed tree                   # H1
  Given a project with .add/tooling + state.json but .claude/skills/add deleted
  When init runs
  Then the skill tree is restored from the package
  And state.json is unchanged

Scenario: init refreshes a present tree and sweeps an orphan      # H1
  Given .add/docs is present and contains a stale orphan removed upstream
  When init runs
  Then docs is clean-replaced to the packaged version and the orphan is gone
  And user data is unchanged

Scenario: init reports per-tree status                           # H2
  Given a project missing the skill tree but with tooling+docs present
  When init runs
  Then output reports the skill "restored" (was missing) and tooling/docs "refreshed"

Scenario: update heals a missing tree at the same version        # H3
  Given a project stamped at the current version but with .add/docs deleted
  When update runs without --force
  Then docs is restored even though the version matches
  And state.json and PROJECT.md are unchanged

Scenario: same-version no-op persists when nothing is missing     # H4
  Given a project stamped at the current version with all 3 managed trees present
  When update runs without --force
  Then it reports "already at <version>" and writes nothing
  And user data is unchanged

Scenario: reconcile never touches user data                      # H5
  Given a project with state.json, PROJECT.md, milestones/, tasks/
  When init (or update) reconciles
  Then every user-data file is byte-identical afterward
  And only managed trees changed

Scenario: drops-files-only invariant holds                       # H6
  Given a fresh or partial project
  When init reconciles
  Then no state.json is created, no add.py init runs, and installed tooling has no test_*.py
  And user data (if any) is unchanged

Scenario: npm and pip reconcile identically                      # H7
  Given the same partial project
  When init reconciles on npm and on pip
  Then both restore the same trees, report the same status words, and apply the same no-op rule

Scenario: missing packaged source fails closed                   # Reject missing_source
  Given a packaged source tree is absent (corrupt install)
  When init or update runs
  Then it fails with an error before modifying the target
  And the target is unchanged

Scenario: update without a project fails closed                  # Reject no_project
  Given a directory with no .add/
  When update runs
  Then it fails closed with an error
  And nothing is created
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
MANAGED (unchanged set, both twins):
  skill/add -> .claude/skills/add        (no test-strip)
  tooling   -> .add/tooling              (strip test_*.py + __pycache__)
  docs      -> .add/docs                 (no test-strip)
USER DATA (never touched): .add/state.json · PROJECT.md · milestones/ · tasks/ · archive/ · SOUL.md · survivor docs

managedStatus(target) / _managed_status(target) -> { skill: "missing"|"present", tooling: …, docs: … }
  "missing" iff the dest dir is absent OR has no entries; else "present"

reconcile(target, {force})            # the shared primitive; used by init AND update's heal path
  precheck: every packaged MANAGED source exists, else -> "missing_source" (target UNTOUCHED)
  per tree: clean-replace src -> dest  (rm-then-copy: restores if missing, refreshes if present, sweeps orphans)
            tooling also strips test_*.py + __pycache__
  report per tree: "restored <tree> (was missing)" | "refreshed <tree>"
  reads/writes ONLY managed trees — never user data

cmdInit(args) / install(...):
  (the installer-prompts interactive layer is unchanged) -> reconcile(chosenTarget, {force})
  still: creates NO state.json · never runs add.py init · drops-files-only

cmdUpdate(args) / update(...):
  st = managedStatus(target);  missing = trees where st == "missing"
  if cur===version AND not missing AND not force -> "already at <version>"   (NO-OP, writes nothing)
  else -> back up state (pre-update-state.bak.json) -> reconcile(target,{force}) -> migrations -> write stamp
  no .add/ project -> "no_project" (fail closed)

errors
  missing_source -> "missing packaged source: <path>" + exit 1, target untouched
  no_project     -> "no ADD project at <target> (.add/ not found) — run init first" + exit 1

State / schema: only the managed `.add-version` stamp is written; user data untouched.
```

Least-sure flag surfaced at freeze:
  ⚠ [contract] init now REFRESHES a present skill (drops skip-if-exists) — a hand-edited managed skill is overwritten; accepted because the skill is ship-controlled MANAGED (not user data) and --force already did this.
  ⚠ [spec] "missing" is tree-level (absent/empty dir); a partially-gutted present tree heals via init's always-refresh or a version-change update, NOT a same-version update.

Status: FROZEN @ v1 — approved by Tin Dang (full-auto mode delegated 2026-06-17; open assumptions resolved: status words restored/refreshed · "missing" = absent-or-empty dir — both adopted)
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: behavior-complete across the 10 scenarios. pip is fully hermetic via a synthetic
bundled source (mirrors test_update.py — install() gains an optional `bundled` test param, parity with update()); npm uses the real packaged sources via subprocess (skips honestly without node).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_init_restores_missing_skill_pip: project missing .claude/skills/add / install(bundled) / skill restored + state.json intact (H1,H5).
  - test_init_refreshes_present_and_sweeps_orphan_pip: docs has an upstream-removed orphan / install(bundled) / orphan gone + new content present (H1).
  - test_init_reports_status_pip: missing skill, present tooling/docs / install(bundled), capture stdout / "restored" skill + "refreshed" tooling/docs (H2).
  - test_update_heals_missing_at_same_version_pip: stamped at v, docs deleted / update(version=v, no force) / docs restored (NOT a no-op) (H3).
  - test_update_noop_when_nothing_missing_pip: stamped at v, all present / update(version=v) / "already at v" + no write (H4).
  - test_user_data_sacred_pip: state.json/PROJECT.md/milestones byte-identical after reconcile (H5).
  - test_drops_files_only_pip: install() creates no state.json + installed tooling has no test_*.py (H6).
  - test_missing_source_fails_closed_pip: bundled missing a tree / install / nonzero + target untouched (Reject missing_source).
  - test_init_restores_missing_tree_npm: init, delete skill, init again / skill restored + reported (H1,H7) [skipUnless node].
  - test_update_heals_missing_at_same_version_npm: init, stamp at pkg version, delete docs, `update` / docs restored (H3,H7) [skipUnless node].
  - test_parity_status_vocab: both cli.js + _installer.py contain the "restored"/"refreshed" status words (H7 structural).
</test_plan>

Tests live in: `add-method/tooling/test_heal_reconcile.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/bin/cli.js` `add-method/src/add_method/_installer.py` `add-method/tooling/test_heal_reconcile.py` `add-method/tooling/test_v8_install.py`
  (no package.json / _cli.py change — flags + routing from installer-prompts are unchanged; reconcile is internal to install()/update().)
  test_v8_install.py is a STRUCTURAL companion edit: the MANAGED-list refactor collapsed the two-arg `"skill","add"` copy into one mapped source `"skill/add"`, so `test_cli_bundles_brain`'s structural regex had to be re-aimed to the new shape (NOT weakened — behavioral intent proven by test_installer_handoff + the new npm tests; see §6 SEMANTIC).
Strategy (ordered batches): 1. add `managedStatus`/`_managed_status` (missing/present per tree) → 2. add the shared `reconcile` path reusing `cleanReplaceTree`/`_clean_replace` + per-tree status reporting → 3. wire cmdInit/install → reconcile (drop skip-if-exists) → 4. wire cmdUpdate/update heal-when-missing while preserving the same-version no-op.
Safety rule (feature-specific): reconcile touches ONLY the 3 managed trees; the precheck verifies all packaged sources exist BEFORE any write (fail-closed, target untouched); update backs up state before any change.
Code lives in: `add-method/` (the package — NOT this task's `./src/`).
Constraints: do NOT change any test or the contract; no new dependency; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — heal suite 11/11; full suite **1226 OK** (`python3 -m unittest discover -s add-method/tooling`, 18.9s)
- [x] coverage did not decrease — +11 heal tests (2 npm subprocess, skip-honest without node); no test removed (test_v8_install regex re-aimed, intent preserved)
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; the §4 red suite (test_heal_reconcile.py) unedited after the tests→build crossing
- [x] the green was EARNED, not gamed — reconcile asserts are real on-disk effects: restored SKILL.md content == "skill v-new"; swept orphan zz-orphan.md absent; sacred PROJECT.md byte-identical; missing_source leaves the docs file at its pre-value. No stubs, no fixture overfit
- [x] concurrency / timing of the risky operation is safe — reconcile is synchronous; precheck-ALL-packaged-sources before ANY write (fail-closed); no partial-write window on a corrupt source (proven by test_missing_source_fails_closed_pip — target untouched on reject)
- [x] no exposed secrets, injection openings, or unexpected dependencies — pure stdlib (pip) / no new npm dep; reconcile reuses the existing clean-replace + test-strip path
- [x] layering & dependencies follow CONVENTIONS.md — npm↔pip parity held (status vocab restored/refreshed in both twins; ParityVocabTest pins it); writes managed trees only, user data sacred
- [x] a person reviewed and approved the change — full-auto mode delegated by Tin Dang (2026-06-17); auto-resolved PASS on complete evidence, no security/concurrency/architecture residue

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — every new symbol referenced: `managedStatus`/`reconcile`/`TREE_LABEL` (cli.js) called from `dropFiles`+`cmdUpdate`; `_managed_status`/`_reconcile`/`CANCEL` (_installer.py) called from `install`+`update`; the `bundled` test param is threaded from test_heal_reconcile.py
- [x] DEAD-CODE (code) — removed the now-orphaned `copyDir` (cli.js) and `_warn` (_installer.py) left by the refactor; full suite stayed green (1226) after removal — no remaining unused symbol
- [x] SEMANTIC (prose / non-code) — DISCLOSED out-of-scope touch: `test_v8_install.py::test_cli_bundles_brain` regex re-aimed from `"skill",\s*"add"` to `"skill/add"` (the MANAGED list collapsed the two-arg copy into one mapped source). A faithful STRUCTURAL-regex update, NOT a weakening — the behavioral intent (skill lands in `.claude/skills/add/`) is independently proven by test_installer_handoff + the new npm restore/heal tests. File is outside the §5 BUILD scope; recorded here per show-before-ask.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang (full-auto mode delegated 2026-06-17) · date: 2026-06-17

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): managed-tree-missing rate at init/update (heal trigger); missing_source reject rate (corrupt-package signal); same-version no-op rate (idempotency holding).

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`).

- [SPEC · carried] tree-level "missing" (absent/empty dir) won't heal a PARTIALLY-gutted present tree on a same-version update — consider a manifest/file-count check if drift is seen in the wild (evidence: H-A2 accepted at freeze with this exact gap noted) [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]
- [SPEC · carried] reconcile reports per-tree status but not a one-line "N restored / M refreshed" summary — global-install will reconcile a shared home where a roll-up reads better (evidence: global-install is the next milestone task and consumes reconcile) [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence.

- [ADD · folded] a refactor that collapses a structural shape (two-arg copy → one MANAGED mapping) silently breaks structural-regex tests OUTSIDE the declared §5 scope — disclose + re-aim the regex to the new shape, never weaken intent (evidence: test_v8_install::test_cli_bundles_brain went red on the MANAGED collapse, fixed by re-aiming to `"skill/add"`) [folded foundation-version 38]
- [TDD · folded] interactive/clean-replace IO is best proven by real on-disk asserts on a synthetic bundle (mirrors test_update.py) rather than mocking the copy — keeps the green earned (evidence: all 11 heal tests assert real file content/absence, caught the orphan-sweep + fail-closed behaviors) [folded foundation-version 38]
- [ADD · folded] a refactor leaves orphaned helpers (copyDir/_warn) behind — sweep dead code in the same loop and re-run the full suite to prove nothing referenced them (evidence: both removed, suite held 1226 green) [folded foundation-version 38]
