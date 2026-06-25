# TASK: Port SOUL.md seed-if-missing to the npm cli.js installer (pip parity)

slug: soul-seed-npm-parity · created: 2026-06-25 · stage: mvp
autonomy: auto
phase: done   <!-- fast lane: ground -> specify -> contract -> tests -> build -> verify -> observe -> done -->
fast: true   <!-- the fast lane: a small task, collapsed flow + minimal template. Omit --fast for full rigor. -->

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols):
- `add-method/src/add_method/_installer.py:_seed_soul_md` (729-743) — the pip twin: seeds `.add/SOUL.md` from `bundled_root/tooling/templates/SOUL.md.tmpl` if missing; skip-if-exists (user-owned, never clobber); fail-soft (logs `soul_seed_skipped`, never aborts). Called at install (845) AND update (1116), after reconcile. THE behavior to mirror.
- `add-method/bin/cli.js` — the npm twin, has NO SOUL.md seeding (parity GAP). Insertion points: `dropFiles` (install) after `reconcile(args, target)` (571) · `cmdUpdate` after `reconcile(args, target)` (934). `PKG_ROOT` (31) = package root; template at `PKG_ROOT/tooling/templates/SOUL.md.tmpl`.
- `add-method/tooling/test_update.py` (CLI_JS at 38) — cli.js is tested TEXT-INVARIANT (grep the source for required patterns; no node harness), e.g. `test_cli_js_has_update_verb` asserts `'case "update"' in src`. The new test mirrors that style.
- `add-method/tooling/test_installer_soul_seed.py` — the EXISTING pip behavioral coverage (fresh-install seeds · skip-existing · update re-seeds); the npm side is the missing parity twin.

Anchors the contract cites: a `cli.js` SOUL.md-seed function wired into BOTH install and update paths · `tooling/templates/SOUL.md.tmpl` · the text-invariant parity assertions.

---

## 1 · SPECIFY — the rules

Feature: npm cli.js seeds .add/SOUL.md if missing — parity with the pip _seed_soul_md twin
Must:
  - cli.js defines a SOUL.md-seed function mirroring `_seed_soul_md`: seed `.add/SOUL.md` from `PKG_ROOT/tooling/templates/SOUL.md.tmpl` only if the dest is missing (skip-if-exists, never clobber), fail-soft (warn + return, never abort the install/update).
  - it is wired into BOTH the install path (`dropFiles`, after reconcile) and the update path (`cmdUpdate`, after reconcile) — matching the pip twin's two call sites.
Reject:
  - (none — prose/installer hygiene; no error code. Fail-soft on a missing template or unwritable dest, exactly like the pip twin.)
Accept: Given an ADD project whose `.add/SOUL.md` was deleted, When `cli.js` runs install or update, Then it re-seeds SOUL.md from the bundled template (and skips when one already exists) — asserted text-invariant on cli.js source (seed fn present + called in both paths), parity with `test_installer_soul_seed.py`.
Assumptions: ⚠ the bundled template path is `PKG_ROOT/tooling/templates/SOUL.md.tmpl` (same relative path the pip twin uses under bundled_root) — why most likely wrong: npm ships `tooling/` as a MANAGED tree, so templates ride along; if wrong: the seed fails fail-soft (warn, no abort) and the path is a one-line fix.

---

## 3 · CONTRACT — freeze the shape

```
cli.js — new function (mirror of _installer.py:_seed_soul_md):

  function seedSoulMd(target) {
    const dest = path.join(target, ".add", "SOUL.md");
    if (fs.existsSync(dest)) return;                       // skip-if-exists (never clobber)
    const source = path.join(PKG_ROOT, "tooling", "templates", "SOUL.md.tmpl");
    if (!fs.existsSync(source)) { warn("soul_seed_skipped: SOUL.md.tmpl not found ..."); return; }
    try {
      fs.mkdirSync(path.dirname(dest), { recursive: true });
      fs.writeFileSync(dest, fs.readFileSync(source, "utf8"));
    } catch (e) { warn("soul_seed_skipped: could not write .add/SOUL.md — " + (e.message||e)); }
  }

Wired: dropFiles  — `seedSoulMd(target);` after `reconcile(args, target);` (install path)
       cmdUpdate  — `seedSoulMd(target);` after `reconcile(args, target);` (update path)

Test (text-invariant, in test_update.py-style): cli.js source contains `seedSoulMd`,
references `SOUL.md.tmpl`, and calls `seedSoulMd(` in BOTH the install and update regions.
The pip behavioral parity already lives in test_installer_soul_seed.py (unchanged).
```

`Least-sure flag surfaced at freeze:` [test] a text-invariant grep proves the WIRING exists, not the runtime seed (no node harness in this repo) — same proof model `test_update.py` already uses for cli.js; if a behavioral gap slips through, the pip twin's behavioral test still guards the shared contract.
Status: FROZEN @ v1 — approved by Tin Dang (AskUserQuestion freeze), 2026-06-25.
<!-- The freeze IS the one approval. Approved -> Status: FROZEN @ vN — approved by <name>.
     Changing a frozen contract = change request back to SPECIFY. -->

---

## 4 · TESTS — failing-first (red)

Plan: `test_soul_seed_npm_parity.py` — text-invariant on cli.js source:
  (a) defines a `seedSoulMd` function · references `SOUL.md.tmpl`;
  (b) calls `seedSoulMd(` in the install region (`dropFiles`) AND the update region (`cmdUpdate`);
  (c) skip-if-exists guard present (`if (fs.existsSync(dest)) return`).
Red first: today cli.js has no SOUL.md seeding (grep for `seedSoulMd` → absent).
Tests live in: `add-method/tooling/test_soul_seed_npm_parity.py` · MUST run red before Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `add-method/bin/cli.js` · `add-method/tooling/test_soul_seed_npm_parity.py`
Code lives in: `add-method/bin/`   ·   Constraints: cli.js only (no engine, no _installer.py change — the pip twin already has it); mirror _seed_soul_md faithfully (skip-if-exists · fail-soft · both paths); no new npm dependency (stdlib fs/path only).

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build — full suite 1764/0 (+3); `node --check cli.js` clean; pip twin (test_installer_soul_seed) + test_update parity green.
- [x] green was EARNED — the text-invariant tests assert the REAL wiring (seedSoulMd defined · SOUL.md.tmpl referenced · skip-if-exists guard · called in both dropFiles + cmdUpdate), and seedSoulMd faithfully mirrors `_seed_soul_md`. Runtime behavior guarded by the pip twin's behavioral suite.
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP) — stdlib fs/path only; reads a packaged template, writes one user file; fail-soft on every error; no new npm dep.

Build expectations (from §1 Accept + §3 CONTRACT): cli.js gains a `seedSoulMd` that skips when `.add/SOUL.md` exists and re-seeds from `tooling/templates/SOUL.md.tmpl` when missing, called after reconcile in BOTH `dropFiles` and `cmdUpdate` — CONFIRMED by `test_soul_seed_npm_parity.py` red→green + the pip behavioral twin (`test_installer_soul_seed.py`) staying green; npm↔pip parity restored.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-gate on evidence, autonomy: auto) · date: 2026-06-25
<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass.
     OBSERVE (optional): one `[SPEC · open]` or competency-delta line here if the loop taught the foundation something. -->
