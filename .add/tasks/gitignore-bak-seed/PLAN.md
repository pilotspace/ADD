# TASK: Seed .add/.gitignore (incl. pre-update-state.bak.json) if missing on update/init

slug: gitignore-bak-seed · created: 2026-06-25 · stage: mvp
autonomy: auto
phase: done   <!-- fast lane: ground -> specify -> contract -> tests -> build -> verify -> observe -> done -->
fast: true   <!-- the fast lane: a small task, collapsed flow + minimal template. Omit --fast for full rigor. -->

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols):
- `add-method/tooling/add.py:_GITIGNORE_BODY` (109-115) — the body `cmd_init` writes to `.add/.gitignore` (scope-snapshot · pre-archive-state.bak.json · .update-cache.json). MISSING `pre-update-state.bak.json` — the update backup BOTH installers write (`cli.js:cmdUpdate` 932 · `_installer.py.update` `shutil.copyfile(... pre-update-state.bak.json)`), so it leaks into git. Doc comment 101-108 explains each entry. `cmd_init` (957) writes it never-clobber.
- `add-method/tooling/templates/SOUL.md.tmpl` — the seed-template PRECEDENT; lives in all 3 trees (prepare_bundle copies `tooling/templates/`; dogfood via cp). The new `gitignore.tmpl` rides the same mirror. No ENGINE_MD5 coverage for templates (only add.py is pinned).
- `add-method/src/add_method/_installer.py:_seed_soul_md` (729) + its call sites install (845) / update (after reconcile, 1116) — the pip seed PRECEDENT to mirror with `_seed_gitignore`.
- `add-method/bin/cli.js:seedSoulMd` (~565) + call sites `dropFiles` / `cmdUpdate` (just shipped in soul-seed-npm-parity) — the npm twin to mirror with `seedGitignore`.
- `add-method/tooling/test_add.py:test_init_scaffolds_gitignore` (45-52) — the existing init body-content assertion (the model). `test_soul_seed_npm_parity.py` — the cli.js text-invariant model.

Anchors the contract cites: `tooling/templates/gitignore.tmpl` (canonical body) · `_GITIGNORE_BODY` (+ parity to the tmpl) · pip `_seed_gitignore` · npm `seedGitignore` · seed-if-missing + append-if-absent semantics.

---

## 1 · SPECIFY — the rules

Feature: .add/.gitignore carries pre-update-state.bak.json AND is seeded/refreshed on update by BOTH installers
Must:
  - The canonical ignore body lists `pre-update-state.bak.json` (beside the archive backup). Single-sourced in `tooling/templates/gitignore.tmpl`; the engine `_GITIGNORE_BODY` constant stays byte-identical to it (a parity test enforces no drift).
  - `add.py init` still seeds `.add/.gitignore` (never-clobber) and the seed now contains the new line.
  - BOTH installers, on install AND update (after reconcile), ensure `.add/.gitignore`: SEED it from the template if missing; else APPEND-IF-ABSENT any engine-transient line the template carries that the existing file lacks (the "refresh" — so an existing project gains `pre-update-state.bak.json` without losing user-added lines). Idempotent · additive-only · fail-soft (never abort, never reorder/remove user content).
Reject:
  - (none — content/hygiene; no error code. A clobber or a removal of user lines would be the failure mode the tests forbid.)
Accept: Given an existing project whose `.add/.gitignore` lacks `pre-update-state.bak.json`, When the installer runs update, Then the file gains that line (append-if-absent) and keeps every prior + user line; And a fresh `add.py init` writes a `.add/.gitignore` already containing it.
Assumptions: ⚠ append-if-absent (mutating an existing user file) vs seed-if-missing-only — append is needed to satisfy "existing projects get the line", but it touches a user-owned file; mitigated by additive-only + idempotent + fail-soft. If too aggressive: fall back to seed-if-missing (then existing customized files stay stale — the explicit ask unmet).

---

## 3 · CONTRACT — freeze the shape

```
NEW tooling/templates/gitignore.tmpl (canonical body, 3 trees):
    # ADD engine transient artifacts — local working state, never committed.
    # (Scaffolded by `add.py init`; refreshed additively by the installer on update.)
    scope-snapshot.json
    pre-archive-state.bak.json
    pre-update-state.bak.json      # the `update` pre-write state backup (cmdUpdate / pip twin)
    .update-cache.json

add.py: _GITIGNORE_BODY := byte-identical to gitignore.tmpl (gains pre-update-state.bak.json);
    doc comment names it. cmd_init unchanged (writes _GITIGNORE_BODY, never-clobber).
    Parity test: read(templates/gitignore.tmpl) == _GITIGNORE_BODY.  (re-pin ENGINE_MD5)

pip _installer.py — _seed_gitignore(target_path, bundled_root):
    src = bundled_root/tooling/templates/gitignore.tmpl ; dest = target/.add/.gitignore
    missing src -> _log skip ; dest missing -> write src (seed)
    else -> for each non-blank line in src not present in dest: append it (append-if-absent)
    fail-soft (OSError -> _log, return). Call after reconcile in install (845) AND update (1116),
    beside _seed_soul_md.

npm cli.js — seedGitignore(target):  faithful twin of _seed_gitignore (seed-if-missing else
    append-if-absent, fail-soft). Call after reconcile in dropFiles AND cmdUpdate, beside seedSoulMd.

Tests (test_gitignore_bak_seed.py):
  - engine: fresh init -> .add/.gitignore contains pre-update-state.bak.json (+ prior lines)
  - parity: templates/gitignore.tmpl text == _GITIGNORE_BODY
  - pip behavioral: _seed_gitignore seeds a missing file from tmpl; append-if-absent adds ONLY
    the missing line to a partial file and PRESERVES a user-added line; idempotent on re-run
  - npm text-invariant: cli.js defines seedGitignore, references gitignore.tmpl, calls it in
    BOTH dropFiles + cmdUpdate
```

`Least-sure flag surfaced at freeze:` [spec] append-if-absent mutates an existing user-owned `.add/.gitignore` (additive-only · idempotent · fail-soft · never reorders/removes) — chosen so existing projects actually gain the line; if judged too aggressive, narrow to seed-if-missing (one-line change) at the cost of leaving existing customized files stale.
Status: FROZEN @ v1 — approved by Tin Dang (AskUserQuestion freeze, append-if-absent refresh), 2026-06-25.
<!-- The freeze IS the one approval. Approved -> Status: FROZEN @ vN — approved by <name>.
     Changing a frozen contract = change request back to SPECIFY. -->

---

## 4 · TESTS — failing-first (red)

Plan: `test_gitignore_bak_seed.py` — four checks:
  (a) engine: a fresh `add.py init` writes `.add/.gitignore` containing `pre-update-state.bak.json` (+ prior lines);
  (b) parity: `tooling/templates/gitignore.tmpl` text == `_GITIGNORE_BODY`;
  (c) pip behavioral: `_seed_gitignore` seeds a missing `.add/.gitignore` from the tmpl; on a partial existing file it APPENDS only the missing line and PRESERVES a user-added line; a second run is idempotent (no dup);
  (d) npm text-invariant: cli.js defines `seedGitignore`, references `gitignore.tmpl`, calls it in BOTH `dropFiles` and `cmdUpdate`.
Red first: no gitignore.tmpl, no `_seed_gitignore`/`seedGitignore`, body lacks the line.
Tests live in: `add-method/tooling/test_gitignore_bak_seed.py` · MUST run red before Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `add-method/tooling/add.py` · `.add/tooling/add.py` · `add-method/src/add_method/_bundled/tooling/add.py` · `add-method/tooling/engine_pin.py` · `add-method/tooling/templates/gitignore.tmpl` · `.add/tooling/templates/gitignore.tmpl` · `add-method/src/add_method/_bundled/tooling/templates/gitignore.tmpl` · `add-method/src/add_method/_installer.py` · `add-method/bin/cli.js` · `add-method/tooling/test_gitignore_bak_seed.py`
Strategy (ordered): 1. gitignore.tmpl (3 trees) + `_GITIGNORE_BODY` line + doc comment. 2. pip `_seed_gitignore` + 2 call sites. 3. npm `seedGitignore` + 2 call sites. 4. mirror add.py 3 trees + re-pin. 5. red→green.
Code lives in: `add-method/`   ·   Constraints: append-if-absent is ADDITIVE ONLY (never reorder/remove/clobber user lines); fail-soft everywhere; keep `_seed_gitignore`/`seedGitignore` faithful twins; no new dependency; mirror engine 3 trees + re-pin.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build — full suite 1771/0 (+7); `node --check cli.js` clean; 3-tree engine md5 d59cd43e + pin match; gitignore.tmpl in all 3 trees.
- [x] green was EARNED — pip side is BEHAVIORAL (seed-if-missing · append-if-absent adds only the missing line · PRESERVES a user line · idempotent no-dup · comment lines not appended · fail-soft on missing template); parity test pins tmpl==_GITIGNORE_BODY; npm twin text-invariant (defined + both call sites). No vacuous asserts.
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP) — reads a packaged template, writes a user file ADDITIVELY (never removes/reorders); stdlib only; fail-soft everywhere; no new dep.

Build expectations (from §1 Accept + §3 CONTRACT): (1) a fresh `add.py init` writes `.add/.gitignore` listing `pre-update-state.bak.json`; (2) the template == `_GITIGNORE_BODY` (no drift); (3) the pip `_seed_gitignore` seeds a missing file AND append-if-absent adds only the missing line to a partial file while preserving a user line (idempotent); (4) cli.js carries a `seedGitignore` twin called in both install + update — all CONFIRMED by `test_gitignore_bak_seed.py` red→green + existing test_add/soul/update suites green + 3-tree pin matching.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-gate on evidence, autonomy: auto) · date: 2026-06-25
<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass.
     OBSERVE (optional): one `[SPEC · open]` or competency-delta line here if the loop taught the foundation something. -->
