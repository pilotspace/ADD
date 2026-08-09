# MILESTONE: Installer seeds SOUL.md on install and update

goal: When ADD is installed or updated, .add/SOUL.md is seeded from the bundled template if it does not yet exist — so the voice file is present from the first session without waiting for add.py init.
rationale: one-task micro-milestone; doesn't fit the active installer-smarts-polish goal (PTY test harness); one-task gap rule applied (intake.md)
stage: mvp · status: active · created: 2026-06-18

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  `_seed_soul_md()` helper in `_installer.py`; wired to `install()` and `update()`; skip-if-exists (user data); fail-soft
Out: replacing `{{project}}` placeholder in the seeded file; enriching SOUL.md content beyond the default template; npm/cli.js parity (tracked separately)

## Shared decisions & glossary deltas   (living — every task must honor these)
- SOUL.md is user-owned: never overwrite on install or update

## Shared / risky contracts (freeze these first)
- `_seed_soul_md(target_path, bundled_root)` -> soul-seed-on-install

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] soul-seed-on-install   depends-on: none   — add _seed_soul_md helper; wire to install() and update()

## Exit criteria (observable; map each to the task that delivers it)
- [x] After `install()` on a fresh target, `.add/SOUL.md` exists and contains the default voice content   (← soul-seed-on-install)

## Close — ship review

### Ship by domain
- tooling : `_installer.py` — `_seed_soul_md()` added; called from `install()` (after `_reconcile`) and `update()` (after `_write_stamp`); `SOUL.md.tmpl` already present in `_bundled/tooling/templates/`
- skill   : `intake.md` — one-task gap rule added to all three copies (`.claude/skills/add/`, `add-method/skill/add/`, `add-method/src/add_method/_bundled/skill/add/`)
- book    : untouched

### Cross-task evidence
- soul-seed-on-install : gate=PASS · tests=5 green (1324 total, +5) · residue=none

### Goal met?
- [x] "After install(), .add/SOUL.md exists" satisfied by soul-seed-on-install gate=PASS (test_fresh_install_seeds_soul_md green)
- goal: installer seeds SOUL.md on install and update — confirmed by 5 green tests covering install/update/skip/fail-soft paths

## Release steps
- [ ] Open PR: `_installer.py` + `intake.md` (3 copies) + `test_installer_soul_seed.py`; human reviews + merges
- [ ] Verify CI green on the PR
- [ ] Bundle into next release cut (tag / publish — human-run, per release.md)
