# TASK: Global ADD home: engine+book+skill installed once, updated for all projects

slug: global-install · created: 2026-06-17 · stage: mvp
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
  - `add-method/bin/cli.js:cmdInit/cmdUpdate/dropFiles/reconcile/MANAGED/writeStamp` — npm twin. reconcile(args,target) already clean-replaces the managed trees into ANY target (precheck-all-sources, fail-closed) — reused with a global target. parseArgs is where `--global` lands.
  - `add-method/src/add_method/_installer.py:install/update/_reconcile/MANAGED/_write_stamp/_read_stamp` — pip twin (parity). install() already takes test hooks (bundled, env); add `global`.
  - `add-method/src/add_method/_cli.py:main` — pip arg routing; add `--global` to the init + update parsers.
  - `add-method/tooling/add.py:find_root` — resolves the project DATA root by cwd-walk for `.add/state.json`, INDEPENDENT of where the engine code lives (the seam that lets a project use any engine). NOT modified — only relied on.
  - `add-method/tooling/add.py:_atomic_write` — the temp+os.replace primitive the registry write MIRRORS (each twin re-declares its own atomic write; engine unchanged).
Context (working folder):
  - Default install is SELF-CONTAINED + git-tracked: `.add/.gitignore` (scaffolded by init) ignores ONLY transient artifacts (scope-snapshot/pre-archive-bak/.update-cache), so `.add/tooling/` + `.add/docs/` ARE committed. The milestone PRESERVES this — global is strictly OPT-IN; the default per-project path is UNCHANGED.
  - HARD constraints (tests): drops-files-only (no `add.py init`, no Python spawn — `test_v8_install`/`test_installer_handoff`) · `test_update.py` (same-version no-op WHEN nothing missing · user-data sacred · fails-closed without a project) · npm↔pip parity suites · agent-detect's per-project pointer drop unchanged.
  - Package CLIs are ALREADY global (npm `bin:{add}`, pip `pilotspace-add`); the NEW piece is a global HOME for the managed assets + per-project resolution + update-all.
  - Independent design review (2026-06-17): adopted COPY+registry over symlink (a committed symlink to ~/.add dangles on a teammate clone) and over a re-exec shim (breaks self-contained-clone). See [[project_global_install_design]].
Honors (patterns / conventions):
  - managed↔user-data boundary (global reconcile touches ONLY managed trees; never state/PROJECT/tasks) · drops-files-only + no-Python-spawn · npm↔pip parity (identical home resolution, layout, registry semantics, update-all) · design-for-failure (home unwritable → clear error; corrupt registry → LOUD fail, never a silent empty no-op; missing registered project → prune+warn) · reuse `reconcile`/`_reconcile` (no new copy primitive).
Anchors the contract cites: `resolveGlobalHome()`/`resolve_global_home()` (ADD_HOME → XDG_DATA_HOME/add → ~/.add); a `--global` install path that reconciles the managed layer into the home as a bundled MIRROR (skill/add+tooling+docs) + deploys skill → `~/.claude/skills/add` + a "global" version stamp + REGISTERS the project in `<home>/registry.json` (atomic, dedup); a `update --global` that refreshes the home + skill then propagates to each registered+existing project via reconcile-from-home (prune missing); the registry read/write helpers.
  - `bin/cli.js`: `resolveGlobalHome`, `readRegistry`/`writeRegistry`, `cmdInit --global`, `cmdUpdate --global`.
  - `_installer.py`: `resolve_global_home`, `_read_registry`/`_write_registry`, `install(global=…)`, `update(global=…)` (parity).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Global ADD home — an OPT-IN `--global` that installs the managed layer (engine + book + skill) ONCE to a shared home, registers each opting project, and lets `update --global` refresh the home + propagate to every registered project; the per-project self-contained/git-tracked default is untouched
Framings weighed: COPY into the home + a `registry.json` of opted-in project paths that `update --global` iterates (chosen — preserves git-portability + the teammate-clone invariant; reuses `reconcile`) · per-project SYMLINK `.add/tooling`→home (rejected: a committed symlink to ~/.add dangles on a teammate clone; Windows-fragile) · re-exec SHIM committed at `.add/tooling/add.py` (rejected: breaks self-contained-clone — a teammate without the global home gets a dead engine) · PATH-CLI + a guideline-block variant calling `add` (rejected: changes the stable `python3 .add/tooling/add.py` pointer every project + the book rely on)
Must:
<must>
  - G1 home resolution is PURE + total: `resolveGlobalHome()` = `ADD_HOME` (if set, non-empty) → else `XDG_DATA_HOME/add` (if set) → else `~/.add`. Uses the home dir primitive (never `$HOME` directly); never throws. Identical on both twins.
  - G2 `init --global [dir]` reconciles the managed layer INTO the home as a CANONICAL MIRROR of the bundled layout: skill/add→`<home>/skill/add`, tooling→`<home>/tooling` (strip test_*.py), docs→`<home>/docs`; the skill is ALSO deployed to `~/.claude/skills/add` (Claude's user-global skill dir, unless --no-skill); writes `<home>/.add-version` (channel "global"). Reuses the reconcile precheck (all sources exist first, fail-closed). The home mirroring the bundled layout is what lets `update --global` propagate via `reconcile(project, source=<home>)` reusing the SAME MANAGED map — no special-casing.
  - G3 `init --global [dir]` REGISTERS dir's resolved absolute path in `<home>/registry.json` (a JSON list): atomic write, de-duplicated; then performs the NORMAL per-project drop for dir (self-contained copy + agent-detect pointer — unchanged), so the project still works standalone.
  - G4 `update --global` refreshes the home (tooling+docs+skill, re-stamp) THEN propagates: for each registered project that still exists, reconcile it FROM THE HOME (every project lands the same version); a registered path that no longer exists is PRUNED (warn, continue); the pruned registry is written back atomically.
  - G5 drops-files-only holds for --global too: no `add.py init` runs, no Python is spawned, NO state.json is created in the home or the project.
  - G6 npm↔pip parity: identical home resolution, home layout, registry filename + JSON shape + dedup rule, and update-all propagation order; only clack richness differs.
  - G7 the per-project DEFAULT is UNCHANGED: a plain (non-`--global`) install/update behaves exactly as today (self-contained, git-tracked, no home touched, no registry).
  - G8 design-for-failure: a home/dir that can't be created or written → clear error, target left as-is (the user can fall back to a plain local install); `update --global` with no home install yet → "no global ADD install" error.
</must>
Reject:
<reject>
  - `update --global` when `<home>/.add-version` is absent -> "no_global_home" (nothing to update; tells the user to run `init --global` first)
  - `<home>/registry.json` is present but corrupt (unparseable JSON) -> "registry_corrupt" (LOUD fail + exit 1; never a silent empty-list no-op that quietly skips every project — tells the user to fix/delete it)
  - the global home (or `~/.claude/skills/add`) is unwritable -> "home_unwritable" (clear error; the managed package + the per-project default path remain usable)
  # a registered project path that no longer exists is NOT a reject — it is pruned+warned (G4).
</reject>
After:
<after>
  - after `init --global`, the home holds skill/add+tooling+docs at the package version + a "global" stamp, the skill is ALSO deployed at `~/.claude/skills/add`, the project path is in registry.json (once), and the project has its normal self-contained drop; no state.json anywhere.
  - after `update --global`, the home + every still-existing registered project are at the package version; missing registrations are pruned; user data everywhere is byte-identical.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ G-A1 [contract] the COPY+registry model (vs a symlink/shim that needs no propagation) is the right mvp — lowest confidence because "update propagates to N projects" is a multi-write fan-out that can partially fail. Mitigation: reconcile is atomic PER TREE (precheck-all-sources first) so a mid-fan-out crash leaves earlier projects updated + later ones healable on the next run; the registry is advisory (a project's local copy works even if registry is empty); chosen because it ALONE preserves git-portability + the teammate-clone invariant the milestone mandates. (Accept — reviewed.)
  ⚠ G-A2 [contract] the global SKILL belongs at `~/.claude/skills/add` (Claude's user-global skill dir) — lowest because non-Claude agents have no equivalent global skill path. Mitigation: engine+book (the agent-agnostic core) live in the home and serve every agent; the global skill is a Claude convenience, and other agents still get AGENTS.md per project. A cross-agent global skill map is a SPEC delta. (Accept.)
  - [x] registry.json is a flat JSON list of absolute project-root paths (not keyed/object) — ADOPTED for mvp (global-data may later enrich it to objects).
  - [x] concurrent `update --global` is out of mvp scope — ADOPTED: atomic single-writer writes only; a file lock is a deferred SPEC delta (documented, not silently ignored).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: home resolution precedence                              # G1
  Given ADD_HOME unset and XDG_DATA_HOME=/x
  When resolveGlobalHome() runs
  Then it returns /x/add
  And with ADD_HOME=/h set it returns /h; with both unset it returns ~/.add

Scenario: global install populates the home                       # G2
  Given a fresh global home and a packaged source
  When init --global runs
  Then <home>/tooling/add.py and <home>/docs/*.md exist, the skill is at ~/.claude/skills/add,
       and <home>/.add-version records the package version (channel "global")

Scenario: global install registers the project + drops it locally # G3
  Given init --global is run in project P
  Then P's absolute path is in <home>/registry.json exactly once
  And P has its normal self-contained .add/tooling + .add/docs drop
  And re-running init --global in P does not duplicate the registry entry

Scenario: update --global refreshes the home and all projects     # G4
  Given the home + two registered projects stamped at an OLD version
  When update --global runs at a NEW package version
  Then the home and BOTH projects are reconciled to the new version
  And user data in each project is byte-identical

Scenario: update --global prunes a vanished project               # G4
  Given a registry listing a project path that no longer exists
  When update --global runs
  Then it warns and removes that path, updates the remaining projects, and rewrites the registry

Scenario: global path drops no state.json and spawns no Python     # G5
  Given init --global runs
  Then no state.json exists in the home or the project, and the installer spawns no subprocess

Scenario: a plain install is unchanged by this feature            # G7
  Given init WITHOUT --global
  Then it behaves exactly as today (self-contained drop), touches no global home, writes no registry

Scenario: update --global with no home install fails closed        # Reject no_global_home
  Given no <home>/.add-version
  When update --global runs
  Then it errors "no global ADD install" and writes nothing

Scenario: a corrupt registry fails loudly                          # Reject registry_corrupt
  Given <home>/registry.json contains invalid JSON
  When update --global runs
  Then it errors (nonzero) and does NOT silently skip all projects
  And it leaves the registry for the user to fix or delete

Scenario: an unwritable home fails closed                          # Reject home_unwritable
  Given the global home cannot be created/written
  When init --global runs
  Then it errors clearly and the per-project default path remains usable
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
resolveGlobalHome() -> path        # _installer.resolve_global_home() is the pip twin
  ADD_HOME (set, non-empty)  ->  expanduser(ADD_HOME)
  else XDG_DATA_HOME (set)   ->  XDG_DATA_HOME / "add"
  else                       ->  home() / ".add"        # Path.home() / os.homedir() — never $HOME
  pure · total · never throws · may return a path that doesn't exist yet

GLOBAL HOME LAYOUT   (mirrors the bundled managed layer — the canonical source for propagation)
  <home>/skill/add/      the skill (CANONICAL source; ALSO deployed to ~/.claude/skills/add)
  <home>/tooling/        engine (add.py + templates; test_*.py stripped)
  <home>/docs/           the book
  <home>/.add-version    { version, channel:"global", installed_at }
  <home>/registry.json   ["<abs project root>", …]   (flat list; atomic; deduped)
  ~/.claude/skills/add/  the skill DEPLOYED for Claude discovery (skipped under --no-skill)

readRegistry(home) -> list[str]        # _read_registry; [] when the file is ABSENT (not corrupt)
writeRegistry(home, list) -> void      # _write_registry; ATOMIC (temp + rename); writes deduped
  a PRESENT-but-unparseable registry.json is NOT [] -> it is "registry_corrupt" (see errors)

init --global [dir]   (dir defaults to cwd)
  precheck packaged sources exist (reconcile precheck) -> else fail closed
  reconcile -> <home>: skill/add, tooling, docs (clean-replace; the canonical managed mirror)
  deploy    -> ~/.claude/skills/add  from <home>/skill/add   (unless --no-skill)
  write <home>/.add-version (channel "global")
  reg = readRegistry(home); add abspath(dir) if absent; writeRegistry(home, reg)
  dropFiles(dir)                                # the NORMAL per-project drop (self-contained
                                                #  copy + agent-detect pointer) — UNCHANGED
  print: home trees restored/refreshed · "registered <dir> (registry: N)" · then the project drop
  drops-files-only: NO add.py init, NO Python spawn, NO state.json

update --global [--force]
  home = resolveGlobalHome()
  if no <home>/.add-version            -> error "no_global_home" (exit 1, nothing written)
  reconcile -> <home> skill/add+tooling+docs ; deploy ~/.claude/skills/add ; re-stamp
  reg = readRegistry(home)             # corrupt -> "registry_corrupt" (exit 1, see errors)
  for p in reg:
     if not exists(p): warn "registered project <p> not found — pruning"; drop from reg; continue
     reconcile(p, source=<home>)       # standard MANAGED map, sourced from the home mirror
  writeRegistry(home, pruned reg)
  print: "ADD <ver> · home + M projects reconciled (K pruned)"

plain init / update (NO --global)  -> UNCHANGED (today's self-contained per-project behavior;
                                       no home, no registry, no skill-to-~/.claude)

errors (fail-closed; nothing partially written on the rejecting step)
  no_global_home   -> "no global ADD install at <home> (.add-version not found) — run `init --global` first" + exit 1
  registry_corrupt -> "global registry <home>/registry.json is corrupt — fix or delete it; not propagating" + exit 1
  home_unwritable  -> "cannot write global home <home> — <err>" + exit 1 (per-project default path unaffected)

State / schema: writes ONLY the home's managed trees + .add-version + registry.json, and (per
  project) the existing self-contained drop. NO state.json is created anywhere. registry.json is
  the ONLY new persistent artifact; flat JSON list of absolute paths; atomic writes only.
```

Least-sure flag surfaced at freeze:
  ⚠ [contract] COPY+registry makes `update --global` a multi-project WRITE fan-out (vs a single symlink target) — a partial failure could leave projects on mixed versions. Accepted because reconcile is atomic per tree (precheck-all-first), later runs heal stragglers, and the registry is advisory (each project's local copy stands alone); this is the ONLY model that keeps a teammate's clone working (no dangling symlink / dead shim) — the milestone's self-contained invariant. Reviewed independently 2026-06-17.
  ⚠ [contract] the global skill lands at `~/.claude/skills/add` (Claude-specific) — non-Claude agents get no global skill; mitigated by the agent-agnostic engine+book in the home + per-project AGENTS.md. A cross-agent global-skill map is a SPEC delta.

Status: FROZEN @ v2 — approved by Tin Dang (full-auto mode delegated 2026-06-17; design independently reviewed; open assumptions resolved: flat-list registry · concurrency deferred — both adopted)
  CHANGE @ v2 (build-time, full-auto): the global home now MIRRORS the bundled managed layer —
  it ALSO holds `<home>/skill/add` as the canonical source, with `~/.claude/skills/add` a deployed
  copy. Reason: v1 said `update --global` propagates via `reconcile(p, source=<home>)` but the v1
  layout had no skill source in the home, so reconcile's MANAGED map (skill/add+tooling+docs) had no
  skill to read — an internal inconsistency. Mirroring the bundle makes propagation reuse the SAME
  MANAGED map with zero special-casing. Test-compatible (no test asserts the home lacks skill/add);
  honest change request, NOT a code-around of the frozen text.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: behavior-complete across the 10 scenarios. Fully hermetic: home + skill base are
resolved from the injected `env` (REUSING agent-detect's `env` hook) — tests pass `env={"ADD_HOME":
<tmp>, "HOME": <tmp>}` so NOTHING touches the real ~/.add or ~/.claude. npm uses subprocess with the
same env injected (skips without node).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_resolve_home_precedence_pip: resolve_global_home for ADD_HOME / XDG_DATA_HOME / neither → /h, /x/add, <HOME>/.add (G1).
  - test_global_install_populates_home_pip: install(global, env) / <home>/tooling/add.py + <home>/docs/*.md + <userhome>/.claude/skills/add exist + <home>/.add-version channel=="global" (G2).
  - test_global_install_registers_and_drops_pip: install(global) in P / abspath(P) in registry.json once (re-run → still once) + P/.add/tooling present (self-contained) (G3).
  - test_update_global_refreshes_home_and_projects_pip: home + 2 registered projects stamped OLD / update(global) at NEW / home + both projects at NEW + their state.json byte-identical (G4).
  - test_update_global_prunes_missing_pip: registry lists a deleted path / update(global) / warns + prunes it + updates the rest + registry rewritten without it (G4).
  - test_global_no_state_pip: install(global) / no state.json in home or project (G5); (structural) cli.js has no spawnSync.
  - test_plain_install_untouched_pip: install WITHOUT global / no home created, no registry.json, project self-contained — today's behavior (G7).
  - test_update_global_no_home_fails_pip: update(global) with no <home>/.add-version / nonzero + "no global" message + nothing written (Reject no_global_home).
  - test_registry_corrupt_fails_loud_pip: <home>/registry.json = invalid JSON / update(global) / nonzero + registry left intact (NOT emptied) (Reject registry_corrupt).
  - test_home_unwritable_fails_pip: home path is a FILE (mkdir impossible) / install(global) / nonzero, per-project default path still usable (Reject home_unwritable).
  - test_global_install_npm: subprocess init --global with env ADD_HOME+HOME / home + skill populated + project registered (G2,G3,G6) [skipUnless node].
  - test_update_global_npm: subprocess update --global / home + registered project refreshed (G4,G6) [skipUnless node].
  - test_parity_global: cli.js + _installer.py both name resolveGlobalHome/resolve_global_home, "registry.json", "ADD_HOME", "XDG_DATA_HOME" (G6 structural).
</test_plan>

Tests live in: `add-method/tooling/test_global_install.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/bin/cli.js` `add-method/src/add_method/_installer.py` `add-method/src/add_method/_cli.py` `add-method/tooling/test_global_install.py`
  (NO add.py change — find_root/_atomic_write are only relied on/mirrored. _cli.py gains the `--global` flag on init+update.)
Strategy (ordered batches): 1. add `resolveGlobalHome`/`resolve_global_home(env)` + `readRegistry`/`writeRegistry` (atomic, dedup; corrupt→raise) on both twins → 2. wire `init --global`: reconcile→home as a bundled MIRROR (skill/add+tooling+docs) + deploy skill→~/.claude/skills/add + stamp + register + then the normal per-project drop → 3. wire `update --global`: refresh home+skill, propagate to registered+existing projects via `reconcile(p, source=<home>)` (the home mirror feeds the standard MANAGED map), prune missing, atomic registry → 4. thread `--global` through parseArgs (cli.js) + _cli.py init/update parsers; resolve home + skill base from the injected `env`.
Safety rule (feature-specific): home + skill base come from the injected `env` (ADD_HOME/XDG_DATA_HOME/HOME) so nothing touches the real ~/ in tests; registry writes are ATOMIC (temp+rename); a corrupt registry is a LOUD fail (never a silent empty no-op); per-tree reconcile precheck keeps a partial fan-out healable; the plain (non-global) path is byte-unchanged; no Python spawn, no init, no state.json.
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

- [x] all tests pass — global-install 13/13; FULL suite 1255 green (was 1242 + 13 new).
- [x] coverage did not decrease — +13 tests + 3 hardened assertions (home/skill/add mirror · fail-closed-before-drop · complete-home-after-update); no test removed or weakened.
- [x] no test or contract was altered DURING build — the §3 v2 change was a CHANGE REQUEST (re-frozen + re-crossed contract→tests→build BEFORE build); the 3 test-hardening edits were made at the TESTS phase + re-crossed tests→build (re-snapshotted). The engine's build_tampered tripwire advanced clean both times.
- [x] the green was EARNED, not gamed — INDEPENDENT adversarial review (full-auto safeguard for the riskiest task): verdict MERGE-WITH-NITS, 0 blocking, earned-green PASS. Both disclosed gaps CLOSED by test-hardening (N5 fail-closed-before-drop · the home-mirror source assertion); N2 (propagation-source indistinguishability) is semantically moot — update refreshes home==bundled before propagating — recorded as a §7 note, not a bug.
- [x] concurrency / timing of the risky operation is safe — registry writes are SINGLE-WRITER atomic (temp + os.replace/renameSync); per-tree reconcile prechecks ALL sources first so a mid-fan-out crash leaves earlier projects updated + later ones healable next run; the registry is advisory (a project's local copy stands alone). Concurrent `update --global` is OUT of mvp scope — file-lock seeded as a §7 SPEC delta (documented, not silently ignored).
- [x] no exposed secrets, injection openings, or unexpected dependencies — review SECURITY: no finding. No shell-exec of any kind in the new code (no exec/spawn/subprocess/shell calls — grep-confirmed); no new dependency. Home/skill paths come from user-controlled env (ADD_HOME/XDG_DATA_HOME/HOME) for an OPT-IN local tool. A crafted registry.json path is reconciled-into, but writing it needs prior ~/.add write access (already arbitrary-write) — acceptable for a local dev tool; a registered-path-validation guard for any future multi-user/CI context is a §7 SPEC delta. NOT a security HARD-STOP.
- [x] layering & dependencies follow conventions — reuses the `reconcile`/`_clean_replace` primitive (no new copy path); managed↔user-data boundary held (global touches ONLY managed trees + .add-version + registry.json); npm↔pip parity confirmed by the review across resolution precedence · layout · registry dedup/atomicity/corrupt-behavior · prune order · path registration.
- [x] a person reviewed and approved the change — full-auto mode (Tin Dang delegated 2026-06-17); the INDEPENDENT review subagent is the proportionate human-stand-in safeguard committed for this task. Auto-gated on complete evidence (recorded as auto-resolved — an explicit PASS, not a skip).

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — every new symbol referenced (review traced: pip resolve_global_home/_claude_skills_dir/_registry_path/_read_registry/_write_registry/_GLOBAL_TREES/_reconcile_global/_update_global all called from install()/update(); npm resolveGlobalHome/claudeSkillsDir/registryPath/readRegistry/writeRegistry/GLOBAL_TREES/reconcileGlobal/installGlobal/cmdUpdateGlobal all reached via cmdInit/cmdUpdate; _cli.py threads --global→as_global on both parsers).
- [x] DEAD-CODE (code) — no new unused or orphaned symbol (review: "No orphaned symbols detected").
- [ ] SEMANTIC (prose / non-code) — n/a (code task).

### GATE RECORD
Outcome: PASS  (auto-resolved under autonomy: auto — complete evidence; no security HARD-STOP; backed by an independent adversarial review, verdict MERGE-WITH-NITS / 0 blocking, both disclosed gaps closed)
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: AI auto-gate + independent review subagent (full-auto, Tin Dang delegated) · date: 2026-06-17

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): registry_corrupt rate (a spike = users hand-editing the
registry) · prune rate on `update --global` (high = stale registrations / moved projects) ·
home_unwritable rate (perms/path issues). Note: N2 from the review — within `update --global`
the home is refreshed from the bundle BEFORE propagation, so propagate-from-home and
propagate-from-bundle are observationally identical there; the §6 hardening instead asserts the
home mirror is COMPLETE (the source has skill/add+tooling+docs), which is the meaningful invariant.

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

  - [SPEC · carried] add a file-lock around `update --global` so concurrent runs serialize (evidence: §1 G-A2-adjacent — atomic single-writer covers a crash mid-write but NOT two `update --global` racing; deferred from mvp, documented). [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]
  - [SPEC · carried] validate registered project paths before reconciling into them (reject traversal / non-project dirs) for any future multi-user or CI-service context (evidence: review SECURITY — a crafted registry.json path is reconciled-into; acceptable for an opt-in local tool today, a hazard if the registry ever becomes shared/remote). [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]
  - [SPEC · carried] a cross-agent global-skill map — non-Claude agents have no `~/.claude/skills/add` equivalent, so the global skill is Claude-only today (evidence: §1 G-A2; engine+book in the home already serve every agent + per-project AGENTS.md covers the rest). [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->

  - [ADD · folded] a frozen-contract INTERNAL inconsistency found at build (here: "propagate from <home>" but the home layout lacked the skill source MANAGED needs) is a legit CHANGE REQUEST — re-freeze (v2) + re-cross contract→tests→build BEFORE coding around it, never a silent code-around (evidence: §3 v2 mirror change). [folded foundation-version 38]
  - [TDD · folded] a "propagate FROM X" contract where, at runtime, X is rebuilt from the same fixture the test seeds, is UN-distinguishable by a naive presence test — assert the SOURCE is complete instead of trying to prove which source was read (evidence: review N2 → §6 hardening asserts the home holds skill/add+tooling+docs). [folded foundation-version 38]
  - [ADD · folded] for the riskiest task in a milestone, an INDEPENDENT adversarial review subagent is a proportionate stand-in for the human gate under full-auto — and its disclosed NITs should be CLOSED (test-hardening) before the PASS, not just filed (evidence: review found N5/N2; both addressed pre-gate). [folded foundation-version 38]
