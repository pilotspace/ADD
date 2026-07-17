# TASK: Seed .add/SOUL.md from bundled template during install and update

slug: soul-seed-on-install · created: 2026-06-18 · stage: mvp
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
- `add-method/src/add_method/_installer.py:install` (line 532) — main install entry; called after `_reconcile()` drops managed trees; new call to `_seed_soul_md()` goes here
- `add-method/src/add_method/_installer.py:update` (line 839) — main update entry; called after `_reconcile()` + migrations; same `_seed_soul_md()` call goes here (skip-if-exists semantics identical)
- `add-method/src/add_method/_installer.py:_reconcile` — materializes the three MANAGED trees (skill/add · tooling · docs) into the target; SOUL.md is NOT in MANAGED (it is user data, never a managed tree)
- `add-method/src/add_method/_bundled/tooling/templates/SOUL.md.tmpl` — the bundled template source; ships inside the `tooling` MANAGED tree so it is present at `.add/tooling/templates/SOUL.md.tmpl` after install; contains `{{project}}` placeholder (cosmetic header only — file is usable as-is)

Context (working folder):
- `add-method/tooling/test_installer_prompts.py` — test pattern reference: `tempfile.TemporaryDirectory`, `_run_pip(["init"], cwd=tmp)`, `_brain_landed(Path(tmp))` helpers; new tests follow the same shape
- New test file: `add-method/tooling/test_installer_soul_seed.py`

Honors (patterns / conventions):
- Design-for-failure: sources are verified before touching target (`_installer.py` header + line 594–597 pattern)
- User data — never clobber: SOUL.md is human-owned; skip-if-exists on BOTH install and update (same rule as `_write_intent_note` skip-on-empty + the global-data one-way-snapshot)
- `_seed_soul_md(target_path: Path, bundled_root: Path) -> None` — a pure drop helper, fail-soft (never aborts the surrounding install/update on a seeding failure)

Anchors the contract cites:
- `_installer.py:install` — where the seed call is wired
- `_installer.py:update` — where the seed call is wired
- `_installer.py:_seed_soul_md` — the new helper (skip-if-exists)
- `_bundled/tooling/templates/SOUL.md.tmpl` — the source template

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: SOUL.md seeding on install and update
Framings weighed: seed-if-missing (chosen) · always-seed (resets user customizations — wrong) · seed-only-on-init (requires a subsequent human step — misses the goal)
Must:
<must>
  - M1: `install()` copies `bundled_root/tooling/templates/SOUL.md.tmpl` to `<target>/.add/SOUL.md` if the file does not yet exist
  - M2: `update()` copies the same template to `<target>/.add/SOUL.md` if the file does not yet exist
  - M3: If `.add/SOUL.md` already exists, skip silently — never overwrite (SOUL.md is user-owned)
  - M4: A seeding failure (template unreadable, dest unwritable) logs a warning and does NOT abort the surrounding install/update; both functions still return 0
  - M5: Seeding is implemented in a single new helper `_seed_soul_md(target_path: Path, bundled_root: Path) -> None` called from both sites
</must>
Reject:
<reject>
  - Template absent at `bundled_root/tooling/templates/SOUL.md.tmpl` at seed time -> `soul_seed_skipped` (log warning, do not fail)
  - `.add/SOUL.md` already present -> skip silently (not an error, no log)
</reject>
After:
<after>
  - `.add/SOUL.md` exists at the target after a fresh install
  - `.add/SOUL.md` exists at the target after update on a project that had none
  - A pre-existing `.add/SOUL.md` is byte-identical to what it was before either operation
  - `install()` and `update()` return 0 whether seeding wrote, skipped, or soft-failed
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ `SOUL.md.tmpl` is present inside the `tooling` MANAGED tree after `_reconcile()` — lowest confidence because it is a new file; a stale installed wheel could be missing it; if wrong: seeding silently skips (logged `soul_seed_skipped`), no data loss, cost is low
  - [x] `.add/` directory exists when `_seed_soul_md` is called — confirmed: `_reconcile()` calls `_clean_replace()` which calls `dest.parent.mkdir(parents=True, exist_ok=True)` before writing
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: fresh install seeds SOUL.md          # covers M1
  Given a fresh target directory with no .add/SOUL.md
  When install() completes
  Then .add/SOUL.md exists and its content contains "SOUL — Trusting"
  And the managed trees (skill · tooling · docs) are present and unchanged

Scenario: install skips existing SOUL.md       # covers M3
  Given a target directory where .add/SOUL.md already contains custom content "my-voice"
  When install() completes
  Then .add/SOUL.md still contains "my-voice" (not overwritten)

Scenario: update seeds missing SOUL.md         # covers M2
  Given an existing ADD project (state.json present) with no .add/SOUL.md
  When update() completes
  Then .add/SOUL.md exists and its content contains "SOUL — Trusting"
  And state.json and other user data are unchanged

Scenario: update skips existing SOUL.md        # covers M3
  Given an existing ADD project where .add/SOUL.md contains custom content "my-voice"
  When update() completes
  Then .add/SOUL.md still contains "my-voice" (not overwritten)

Scenario: missing template — seed skipped install succeeds    # covers M4 + Reject
  Given a bundled_root where tooling/templates/SOUL.md.tmpl does not exist
  When install() is called
  Then install() returns 0
  And .add/SOUL.md is absent (seeding skipped)
  And the managed trees are present (install succeeded)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
FUNCTION _seed_soul_md(target_path: Path, bundled_root: Path) -> None
  source : bundled_root / "tooling" / "templates" / "SOUL.md.tmpl"
  dest   : target_path / ".add" / "SOUL.md"
  skip-if-exists  : dest already present  → return immediately (no write, no log)
  skip-if-missing : source absent         → _log("soul_seed_skipped: SOUL.md.tmpl not found") → return
  on success      : dest.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
  fail-soft       : any OSError during write → _log warning → return  (never raises)

CALL SITE install()
  position: after _reconcile(target_path, bundled_root), before _write_agent_pointer(...)
  call: _seed_soul_md(target_path, bundled_root)

CALL SITE update()
  position: after _write_stamp(add_dir, new_version, channel=channel)
  call: _seed_soul_md(target_path, bundled_root)
```

Least-sure flag surfaced at freeze: [spec] M4 fail-soft — if `_seed_soul_md` raises unexpectedly beyond OSError (e.g. a logic bug), the call sites have no wrapper today; cost: install/update could surface an unhandled exception. Mitigation: the helper catches all OSError and returns; risk accepted at this scope.

Status: FROZEN @ v1 — approved by Tin Dang

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 100% of `_seed_soul_md`; all 5 scenarios covered
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_fresh_install_seeds_soul_md: arrange empty tmpdir / act install(target=tmp, bundled=bundled_root) / assert .add/SOUL.md exists + contains "SOUL — Trusting" + managed trees present
  - test_install_skips_existing_soul_md: arrange tmpdir with .add/SOUL.md="my-voice" pre-written / act install() / assert .add/SOUL.md still == "my-voice"
  - test_update_seeds_missing_soul_md: arrange tmpdir with prior install (state.json + managed trees) but no SOUL.md / act update(target=tmp, bundled=bundled_root) / assert .add/SOUL.md exists + contains "SOUL — Trusting" + state.json unchanged
  - test_update_skips_existing_soul_md: arrange tmpdir with prior install + SOUL.md="my-voice" / act update() / assert SOUL.md still == "my-voice"
  - test_missing_template_install_still_succeeds: arrange bundled_root copy with SOUL.md.tmpl deleted / act install() / assert returns 0 + managed trees present + .add/SOUL.md absent
</test_plan>

Tests live in: `add-method/tooling/test_installer_soul_seed.py`

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/src/add_method/_installer.py`
Strategy (ordered batches): 1. add `_seed_soul_md()` helper · 2. wire call in `install()` · 3. wire call in `update()`
Safety rule (feature-specific): never write `.add/SOUL.md` if it already exists; the helper must check before writing
Code lives in: `add-method/src/add_method/_installer.py`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 1324/1324 green (was 1319; +5 new)
- [x] coverage did not decrease — 5 new tests cover all 5 scenarios + the new helper
- [x] no test or contract was altered during build — only `_installer.py` was modified
- [x] the green was EARNED — each test arranges a distinct precondition (absent/present SOUL.md, missing template) and asserts an observable file state; no vacuous asserts
- [x] concurrency / timing safe — `_seed_soul_md` is a pure file write; no shared state; called after managed trees are written; no race condition
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only (Path.write_text); no new imports
- [x] layering & dependencies follow CONVENTIONS.md — helper is a private `_` function in `_installer.py`; stdlib only
- [x] a person reviewed and approved the change — Tin Dang (contract freeze 2026-06-18)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
- [x] fresh `install()` produces `.add/SOUL.md` containing "SOUL — Trusting" — confirmed by `test_fresh_install_seeds_soul_md` green
- [x] `install()` on a project with existing SOUL.md leaves it byte-identical — confirmed by `test_install_skips_existing_soul_md` green
- [x] `update()` on project missing SOUL.md seeds it — confirmed by `test_update_seeds_missing_soul_md` green
- [x] `update()` on project with existing SOUL.md leaves it byte-identical — confirmed by `test_update_skips_existing_soul_md` green
- [x] `install()` with missing template returns 0, managed trees intact, no SOUL.md — confirmed by `test_missing_template_install_still_succeeds` green

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_seed_soul_md` defined at `_installer.py:532`; called at line 647 (`install`) and line 906 (`update`); grep confirms 3 references, no orphan
- [x] DEAD-CODE (code) — no new unused symbol; all three references accounted for
- [x] SEMANTIC (prose / non-code) — n/a (no prose artifacts changed)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-18

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
