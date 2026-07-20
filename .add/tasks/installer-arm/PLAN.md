# TASK: Installer drops files only — stop auto-running add.py init so /add reaches the lock-down

slug: installer-arm · created: 2026-06-04 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Installer drops files only — defer `add.py init` to the AI/user so the v12 lock-down is reachable.
Framings weighed:
  - **drops-files-only** (chosen, human Option A 2026-06-04): both installers copy skill+tooling+docs and STOP;
    the AI (via `/add`) or a CLI user runs `init --await-lock` themselves → gate arms, AI sees `brownfield:`.
  - installer-runs-`init --await-lock` (Option B, rejected): gate arms at install, but the AI didn't run init so
    it loses the live `brownfield:` signal + needs status/routing + 0-setup.md rework.
  - keep-plain-init, accept opt-in (Option C, rejected): guts the "any repo by default" headline.
Must:
  - `bin/cli.js` (npm) MUST NOT run `add.py init` — no `add.py` subprocess, no `init` argv. Install needs no
    Python (init no longer runs), so the `hasPython()` detection is removed too.
  - `src/add_method/_installer.py` (pip) MUST NOT run `add.py init` — no `mod.main(["init", ...])`, no `init_argv`,
    no importlib exec of add.py for init.
  - Both still copy skill → `.claude/skills/add/`, tooling → `.add/tooling/`, docs → `.add/docs/` with their
    existing non-clobber / clean-replace guards UNCHANGED.
  - Both closing hints keep the v8 AI-first invariant (contains `/add`, frames milestone/build, NOT `new-task`)
    AND name that the agent now also sets up (runs init, drafts the foundation, you sign once at the lock-down),
    AND offer a manual CLI fallback: `python3 .add/tooling/add.py init --await-lock`.
  - Both file docstrings updated (today they promise "then runs `add.py init`").
Reject:
  - installer auto-running init in ANY form -> the exact gap this task closes (structural prohibition; tests enforce).
  - a closing hint that sends the user to bare `new-task` -> violates the v8 on-ramp invariant (test_v8_install).
After:
  - A fresh `npx @pilotspace/add init` (or pip install) leaves skill+tooling+docs present and NO `.add/state.json`.
  - `/add` → `status` finds no `.add/state.json` → AI runs `init --await-lock` → gate armed → 0-setup.md reachable.
Assumptions — least-sure first:
  ⚠ The CLI-only user (never opens Claude Code) is still adequately served by the manual-fallback hint line —
    least sure because we trade away the "it's inited the moment install finishes" convenience; if wrong: a
    pure-CLI user installs and faces an un-inited project. Mitigation: the closing hint prints the exact
    `init --await-lock` command and says the lock-down follows.
  - [x] No test or downstream tooling asserts a post-install `state.json` — CONFIRMED: grep across all
    `test_*.py` shows `test_v8_install` is structural-only, `test_packaging` checks bundle file-presence; the
    318-test baseline is green and none of it depends on the installer having run init.
  - [x] `hasPython()` in cli.js becomes dead once init isn't spawned — remove it (install = pure file-copy).

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: npm installer drops files only
  Given a fresh target repo
  When bin/cli.js cmdInit runs
  Then it copies skill/tooling/docs into the target
  And it never spawns add.py to run init (no init argv) and creates no .add/state.json

Scenario: pip installer drops files only
  Given a fresh target repo
  When _installer.py install() runs
  Then it copies skill/tooling/docs into the target
  And it never execs add.py init (no mod.main(["init", ...]), no init_argv) and creates no .add/state.json

Scenario: closing hint stays AI-first and names setup-by-AI
  Given either installer finishes
  When the user reads the closing hint
  Then it points at /add and frames the milestone/build flow
  And it does NOT send the user to bare new-task

Scenario: manual CLI fallback is offered
  Given a user who will not open Claude Code
  When they read the closing hint
  Then a manual `add.py init --await-lock` command is shown
  And the existing bundling (skill + docs + add.py shipped/copied) is unchanged
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

This is a source-structure contract (not HTTP) — the invariants both installers must satisfy:

```
bin/cli.js — cmdInit():
  KEEP : copy skill -> .claude/skills/add/ · tooling -> .add/tooling/ · docs -> .add/docs/   (+ guards)
  DROP : hasPython() · const initArgs=[...] · spawnSync(py, initArgs, ...)  → NO add.py subprocess at all
  HINT : "/add" present · matches milestone|build|describe · NO "new-task" · manual line `add.py init --await-lock`

src/add_method/_installer.py — install():
  KEEP : copy the same three trees   (+ guards)
  DROP : init_argv=[...] · importlib spec/exec of add.py · mod.main(["init", ...])  → NO add.py exec for init
  HINT : same shape as cli.js (npm ↔ pip parity)

Post-install observable:
  exists  : .add/tooling/add.py · .claude/skills/add/ · .add/docs/
  absent  : .add/state.json   (init deferred to AI/user)

Tests (test_v8_install.py — honest structural scope, matching the file's existing convention: source
assertions on words + file-ops, NOT a live end-to-end install):
  - cli.js has no add.py-init spawn (no "spawnSync" / no "initArgs")
  - _installer.py has no add.py-init exec (no 'mod.main(' / no "init_argv")
  - both closing hints keep the v8 AI-first invariant (/add, no new-task)
  - both closing hints carry the manual `init --await-lock` fallback
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit)   <!-- self-frozen 2026-06-04 per the v12-tail cadence ("pause only at each VERIFY gate"); lead-flag below -->
<!-- Bundle least-sure flag — [contract]: the assertion "cli.js has no `spawnSync`". `hasPython()` currently
     uses spawnSync for `--version`; this contract REMOVES python detection wholesale (init no longer runs →
     install needs no Python). If a future installer step ever needs Python, `assertNotIn("spawnSync")`
     over-constrains. Cost: low — narrow the assertion to "no add.py-init spawn". Decision: remove hasPython;
     install is now pure file-copy, so the broad assertion is correct AND documents the simplification. -->
<!-- The freeze IS the one approval. Lead it with the bundle's least-sure flag: the 1–2 points
     most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], with why + cost.
     The §1 ⚠ assumptions are its first feeder; a flag may point at a scenario or the contract too. See run.md. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: structural invariants (source assertions) — matching `test_v8_install.py`'s declared HONEST
SCOPE ("prove the installer's WORDS + file ops are as contracted, NOT that a user follows the flow"). A live
end-to-end install (run cli.js via node / install the wheel) is out of scope here — node may be absent in CI
and the bundle-resolution path is exercised by test_packaging.

Plan (one test per scenario):
  - test_cli_does_not_autorun_init   : cli.js source has no add.py-init spawn (no "spawnSync", no "initArgs").  [RED now]
  - test_installer_py_does_not_autorun_init : _installer.py has no add.py-init exec (no 'mod.main(', no "init_argv").  [RED now]
  - test_cli_hint_offers_manual_init : cli.js closing hint carries `init --await-lock` (manual CLI fallback).
  - test_installer_py_hint_offers_manual_init : _installer.py closing hint carries `init --await-lock`.
  (the v8 AI-first hint invariant — /add present, no `new-task` — is already guarded by the existing
   test_cli_next_hint_is_ai_first; my hint edits keep it green.)

Tests live in: `add-method/tooling/test_v8_install.py` · MUST run red (installers still spawn init) before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): the installer is a one-shot file-copy — its only IO is `fs.cpSync` /
`shutil.copytree` into the target. Design-for-failure preserved: sources verified before any copy
(cli.js `copyDir` fails on missing source; `_installer.py` `_bundled_root()` + per-subtree existence check),
non-clobber (skill skip-if-exists unless `--force`), clean-replace on `--force`. Removing the init subprocess
REMOVES a whole failure mode (python-absent / init-exit-non-zero) rather than adding one.
Code lives in: `add-method/bin/cli.js` (npm) · `add-method/src/add_method/_installer.py` (pip).
What changed:
  - cli.js: dropped `hasPython()` + the `add.py init` spawn + the `require("child_process")` import; rewrote the
    closing hint (drops-files-only, names the lock-down, manual `init --await-lock` fallback); updated docstring.
  - _installer.py: dropped the importlib spec/exec of add.py + `mod.main(["init", ...])` + `import importlib.util`;
    same closing-hint rewrite (npm↔pip parity); updated docstring. `force` still used; `stage`/`name` now feed the
    manual hint (no dead params).
Constraints honored: did NOT change any test or the §3 contract; no new dependencies (net REMOVAL of
`child_process` + `importlib.util`); `add.py` untouched (3-tree md5 unchanged).

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — **`Ran 322 tests … OK`** (was 318; +4 installer-arm tests).
- [x] coverage did not decrease — net +4 structural tests; no test removed/weakened.
- [x] no test or contract was altered during build — §3 FROZEN @ v1; §4 tests written before build, unchanged after.
- [x] concurrency / timing of the risky operation is safe — N/A: installer is a one-shot file-copy; removing the
      `add.py init` subprocess REMOVES a failure mode (python-absent / init-non-zero-exit), adds none.
- [x] no exposed secrets, injection openings, or unexpected dependencies — net dependency REMOVAL
      (`child_process`/`spawnSync` from cli.js; `importlib.util` from _installer.py). The manual hint interpolates
      `name`/`stage` into a PRINTED string the user reads (never executed by us), so no injection surface.
- [x] layering & dependencies follow CONVENTIONS.md — installer stays stdlib/zero-dep (npm: no deps; pip: stdlib only).
- [ ] a person reviewed and approved the change — **PENDING (this gate)**.

### Evidence
- **RED→GREEN**: the 4 new tests failed pre-build (installers still spawned init / lacked the `--await-lock`
  fallback) → all 4 green after the edit. Full suite `Ran 322 tests … OK`.
- **Both installers compile**: `node --check bin/cli.js` OK · `ast.parse(_installer.py)` OK.
- **npm ↔ pip parity**: both now drop files only + carry the identical closing-hint shape (drops-files-only ·
  names the lock-down · manual `init --await-lock` fallback). Guarded symmetrically (cli + _installer test pairs).
- **Reachability restored**: a fresh install leaves no `.add/state.json` → `/add` → `status` finds an un-inited
  repo → 0-setup.md §1's existing entry fires (AI runs `init --await-lock`). v12 exit #4 (installer-arm) met.
- **Least-sure flag (from §3 freeze)** — resolved: the broad `assertNotIn("spawnSync")` on cli.js is correct
  because install is now pure file-copy (no Python needed); `hasPython()` removed.
- **Disclosed (non-blocking) observation**: `add-method/dist/` holds a pre-built wheel with the OLD _installer.py.
  A publish rebuilds the wheel (`prepublishOnly` → `test_packaging` builds fresh), so stale `dist/` does not ship;
  noted only so a manual `twine upload dist/*` from the stale artifact is avoided.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin · 2026-06-04
Note: installer drops files only (npm + pip); fresh install leaves no `.add/state.json`, so `/add` reaches the
autonomous-setup → lock-down flow. Suite 322 OK (RED→GREEN +4). `dist/` staleness disclosed (non-blocking;
publish rebuilds). Human PASS at the verify gate.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>
Spec delta for the next loop: <what production taught you>

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
