# TASK: update --global propagation loop must re-seed .gitignore for each registered project

slug: update-global-gitignore-seed · created: 2026-07-01 · stage: mvp
milestone: (none)
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/src/add_method/_installer.py:_update_global()` (~l.1253-1333) — `update --global`'s
    propagation function: refreshes the shared home via `_reconcile_global`, then for each KEPT
    registered project calls `_reconcile(Path(np), home)` (l.1318) — but never `_seed_gitignore`
  - `add-method/src/add_method/_installer.py:_seed_gitignore()` (~l.855-887) — the function that
    must be added to the loop; signature `(target_path: Path, bundled_root: Path) -> None`,
    fail-soft if `bundled_root/tooling/templates/gitignore.tmpl` is absent
  - `add-method/bin/cli.js:cmdUpdateGlobal()` (~l.1117-1156) — npm twin; calls `reconcile(args, np, home)`
    (l.1147) but never `seedGitignore(np)`
  - `add-method/bin/cli.js:seedGitignore()` (~l.603-628) — the function to add to the loop;
    signature `seedGitignore(target)` — single param, reads its source from the MODULE-LEVEL
    `PKG_ROOT` constant (`cli.js:31 const PKG_ROOT = path.resolve(__dirname, "..")`), not a
    parameter — confirmed this resolves correctly unconditionally (always the CURRENT npm
    package's own `tooling/templates/gitignore.tmpl`, the exact content `reconcileGlobal` just
    refreshed the home from), so the JS call site is simply `seedGitignore(np)`, no second arg
  - `add-method/tooling/test_global_update_harden.py` — existing FROZEN @ v2 hermetic test file
    for `_update_global`'s locking/registry-validation concerns; NOT this task's contract, but its
    `_Base` fixture pattern (`_env()`, `_install_global()`, `_make_project()`, `_set_registry()`,
    `_update()`) is the template this task's own new test file's harness will mirror
  - `add-method/tooling/test_global_install.py` — sibling FROZEN @ v1 test file for the base
    global-install mechanism; same fixture shape, confirms `_make_bundled()` fixtures across this
    family deliberately omit `templates/gitignore.tmpl` (so `_seed_gitignore` fail-soft-skips in
    those existing tests — adding a call in the propagation loop will NOT break them)
Context (working folder): none beyond the source tree above — this is a pure code-path gap, no
  external repro needed (the missing call is directly visible by reading `_update_global`/
  `cmdUpdateGlobal` end-to-end and comparing against the sibling `update()`/`cmdUpdate()` (non-
  global) functions, which DO call `_seed_gitignore`/`seedGitignore` at `_installer.py:1388` /
  `cli.js:1196`).
Honors (patterns / conventions): npm/pip parity (every propagation behavior mirrored structurally
  in both `_installer.py` and `cli.js`, per `test_global_update_harden.py::ParityHardenTest`);
  fail-soft seeding (`_seed_gitignore` never raises — logs a skip if the template is absent);
  hermetic-env test convention (`ADD_HOME`/`HOME` injected via `env`, never touching the real
  `~/.add`).
Anchors the contract cites: `_update_global()`, `_seed_gitignore()`, `cmdUpdateGlobal()`,
  `seedGitignore()`, `_reconcile()` / `reconcile()` (the call this new call sits beside).
Issues/Risks (→ feed §1): **THE GAP** — `_update_global`/`cmdUpdateGlobal` refresh a registered
  project's MANAGED trees (skill/tooling/docs/personas-teacher) via `_reconcile`/`reconcile`
  sourced from the just-refreshed home mirror, but never re-run the gitignore seed step for that
  project. A project registered before ANY future `_GITIGNORE_BODY`/`gitignore.tmpl` change
  (including this session's `gitignore-vendor-path-fix`) will keep its stale `.add/.gitignore`
  forever under `update --global` alone — only a direct per-project `update` (non-global) or a
  fresh `install` re-seeds it. This is a PRE-EXISTING gap, independent of the specific pattern
  string bug just fixed (it would exist for any future gitignore-body change too). Confirmed
  identically in BOTH language twins (not a parity break — a shared omission). `_seed_gitignore`
  is APPEND-IF-ABSENT (never removes a stale line), so simply adding the call is safe: it will
  add whatever NEW pattern lines the current `_GITIGNORE_BODY` carries that a project's existing
  `.gitignore` lacks, without touching any line already present (including a stale buggy one it
  would leave alone — self-healing the OMISSION, not retroactively scrubbing old bad lines,
  which is out of this task's scope).
Related intent: discovered while answering the user's follow-up question "are you handle global
  installer cases?" after `gitignore-vendor-path-fix` (this session) — that task's fix IS picked
  up correctly by `install --global`/`init --global` (same `_seed_gitignore` call, same
  `bundled_root`), but tracing the SEPARATE `update --global` propagation path surfaced this
  distinct, pre-existing omission. User chose "Fix now, new task" via AskUserQuestion. No
  `.add/GLOSSARY.md` term introduced — this is a code-path completeness fix, not a new concept.
Ground SHA: `81c8d05`

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `update --global` propagation re-seeds each registered project's `.add/.gitignore`
Framings weighed: add a `_seed_gitignore`/`seedGitignore` call inside the propagation loop, sourced
  from the just-refreshed home mirror (chosen — mirrors the existing `_reconcile(Path(np), home)`
  call it sits beside; minimal, symmetric, no new parameter threading) · re-seed the home's OWN
  gitignore once instead of per-project (rejected — the home is a package mirror, not a git repo;
  the seed target is always a PROJECT's `.add/.gitignore`, never the home's) · have callers run a
  separate `add.py heal-gitignore --global` pass (rejected — adds a new command surface for what
  is simply a missing call in an existing loop; the fix belongs where the omission is)
Must:
<must>
  - M1: `_update_global` calls `_seed_gitignore(Path(np), home)` for every KEPT registered project,
    immediately after its `_reconcile(Path(np), home)` call
  - M2: `cmdUpdateGlobal` calls `seedGitignore(np)` for every KEPT registered project, immediately
    after its `reconcile(args, np, home)` call
  - M3: a project's existing `.add/.gitignore` gains any managed-tree/transient pattern line that
    the CURRENT `_GITIGNORE_BODY`/`gitignore.tmpl` carries and the project's file lacks — via
    `update --global`, with no other `update`/`install` invocation needed
  - M4: a user-added custom line in a project's `.add/.gitignore` survives `update --global`
    unchanged (the existing append-if-absent, never-remove behavior of `_seed_gitignore` itself is
    untouched — this task only ADDS the call site, not the seeding logic)
  - M5: a project whose `.add/.gitignore` is already fully current is a no-op re: gitignore (no
    duplicate lines, no spurious rewrite) — idempotent, same guarantee `_seed_gitignore` already
    provides when called directly
</must>
Reject:
<reject>
  - `update --global` finishes without touching a registered project's `.add/.gitignore` at all,
    even though its managed trees were refreshed -> "gitignore_seed_skipped_on_global_propagation"
    (the exact gap this task closes — regression guard)
  - the added call raises or aborts the propagation loop for one project, blocking the REST of the
    registered projects from being reconciled -> "gitignore_seed_failure_blocks_propagation"
    (`_seed_gitignore`/`seedGitignore` are already fail-soft by design — must stay that way here too)
  - a user's custom `.gitignore` line is dropped or reordered by this new call site ->
    "gitignore_seed_destructive_on_update" (must stay strictly additive, matching M4)
</reject>
After:
<after>
  - a project registered via `--global` gets its `.add/.gitignore` kept current by `update
    --global` alone, the same way its `tooling/`/`docs/`/`personas-teacher/` trees already are
  - both installer twins call the seed step at the identical point in their propagation loop
    (parity preserved, matching `test_global_update_harden.py::ParityHardenTest`'s convention)
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ whether `_seed_gitignore(Path(np), home)` (sourcing from the just-refreshed HOME mirror) vs.
  `_seed_gitignore(Path(np), bundled_root)` (sourcing from the original package root, already in
  scope in `_update_global`) matters in practice — lowest confidence because I have not found a
  case where the two differ (the home mirror is refreshed from `bundled_root` in the same
  function, immediately before the loop, so they're byte-identical at call time); if wrong: a
  future change that lets the home drift from the package between the refresh and the loop would
  make this pick matter — will use `home` for symmetry with the sibling `_reconcile` call and note
  the equivalence in a code comment.
  - [x] whether `seedGitignore(np)` in the JS twin needs a source-root parameter — confirmed NO:
    `PKG_ROOT` is module-level and always resolves to the running package's own bundled root,
    identical in every call site.
  - [x] whether adding this call could break the 2 existing global-install test files
    (`test_global_install.py`, `test_global_update_harden.py`) — confirmed NO: their `_make_bundled`
    fixtures omit `templates/gitignore.tmpl` entirely, so `_seed_gitignore` fail-soft-skips
    (logs, returns) rather than raising.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: pip propagation calls the gitignore seed per project   # M1
  Given a registered project whose `.add/.gitignore` is missing the current managed-tree patterns
  When `_installer.update(..., as_global=True)` runs (the `update --global` path)
  Then `_seed_gitignore` was invoked for that project (its `.gitignore` now carries the patterns)
  And the project's other managed trees (tooling/docs) are still reconciled as before

Scenario: npm propagation calls the gitignore seed per project   # M2
  Given the same setup, run via `node cli.js update --global`
  When the propagation loop completes
  Then the project's `.add/.gitignore` carries the current managed-tree patterns
  And this matches the pip behavior (parity)

Scenario: a stale-but-registered project self-heals via update --global alone   # M3
  Given a project registered earlier whose `.add/.gitignore` predates a `_GITIGNORE_BODY` change
  When `update --global` runs, with no other `update`/`install` invoked
  Then the project's `.add/.gitignore` gains the missing pattern line(s)
  And no separate per-project `update` was needed

Scenario: a user's custom ignore line survives propagation   # M4
  Given a project's `.add/.gitignore` contains a user-added custom line (e.g. `my-secret.local`)
  When `update --global` runs
  Then the custom line is still present, unchanged, in its original position
  And no managed-tree pattern line was duplicated

Scenario: an already-current project is a no-op for gitignore   # M5
  Given a project whose `.add/.gitignore` already carries every current pattern line
  When `update --global` runs
  Then the file's content is unchanged (no duplicate lines appended)
  And the run still reports success for that project

Scenario: a project's gitignore is never left stale after global propagation   # R1
  Given a project registered via `--global`, never freshly `install`ed or `update`d directly
  When `update --global` runs after a `_GITIGNORE_BODY` change
  Then the project's `.add/.gitignore` is NOT missing the new pattern (the pre-fix gap)
  And this is asserted directly against the seeded file's content, not merely "no error raised"

Scenario: a gitignore-seed failure never blocks the rest of the propagation   # R2
  Given one registered project whose `.add/.gitignore` write would fail (e.g. read-only dir)
  When `update --global` runs across multiple registered projects
  Then the OTHER registered projects are still reconciled successfully
  And the overall `update --global` run does not abort with an unhandled exception

Scenario: the new call site never rewrites or reorders a user's custom line   # R3
  Given a project's `.add/.gitignore` with a custom line placed BEFORE the managed-tree block
  When `update --global` runs
  Then the custom line's relative position and exact text are unchanged
  And only missing lines are appended at the end, never inserted mid-file
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
FILE CONTRACT (no HTTP surface — this task adds one call site per installer twin)

_installer.py:_update_global(), inside the per-project loop, immediately after
  `_reconcile(Path(np), home)`:
  BEFORE:  _reconcile(Path(np), home)                # standard MANAGED map, sourced from the home mirror
           if (home / "data" / data_key(np)).exists():
  AFTER:   _reconcile(Path(np), home)                # standard MANAGED map, sourced from the home mirror
           _seed_gitignore(Path(np), home)            # keep .add/.gitignore current too (parity: cli.js)
           if (home / "data" / data_key(np)).exists():

cli.js:cmdUpdateGlobal(), inside the per-project loop, immediately after
  `reconcile(args, np, home)`:
  BEFORE:  reconcile(args, np, home);      // standard MANAGED map, sourced from the home mirror
           // re-persist an opted-in project...
  AFTER:   reconcile(args, np, home);      // standard MANAGED map, sourced from the home mirror
           seedGitignore(np);              // keep .add/.gitignore current too (parity: _installer.py)
           // re-persist an opted-in project...

Both calls are fail-soft (never raise) and additive-only (never remove/reorder an existing line),
matching `_seed_gitignore`/`seedGitignore`'s existing contract — this task adds ONLY the 2 call
sites, the seeding function bodies are untouched.

  4xx -> { error: "gitignore_seed_skipped_on_global_propagation" |
                   "gitignore_seed_failure_blocks_propagation" |
                   "gitignore_seed_destructive_on_update" }
```

Glossary deltas: none — this task adds a call site, not a new concept
Least-sure flag surfaced at freeze: [contract] whether `_seed_gitignore(Path(np), home)` (sourcing
  from the just-refreshed home mirror) versus `_seed_gitignore(Path(np), bundled_root)` (the
  original package root, already in scope) makes any observable difference — lowest confidence
  because I have reasoned they're byte-identical at call time (home is refreshed from bundled_root
  earlier in the same function) but have not proven it with a test where they'd diverge; if wrong:
  a future change that lets the home drift mid-run would need a second look at which source this
  call should read from — using `home` for symmetry with the sibling `_reconcile` call, and this
  is a one-line change to swap if ever proven wrong.
Status: FROZEN @ v1 — approved by Tin Dang

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 100% of the new call sites (2-line addition, no new module)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_pip_global_update_seeds_gitignore (M1/M3/R1): register a project via `--global`,
    delete/blank its `.add/.gitignore` (or write a partial one), run `_installer.update(...,
    as_global=True)`, assert the resulting file carries the current managed-tree patterns
  - test_npm_global_update_seeds_gitignore (M2/M3/R1): same via `node cli.js update --global`
    (skip if node unavailable, matching existing convention)
  - test_custom_line_survives_pip_global_update (M4/R3): pre-seed a custom line BEFORE the
    managed block, run pip `update --global`, assert the custom line's exact text + relative
    position are unchanged and no pattern line is duplicated
  - test_already_current_project_is_noop (M5): pre-seed a project's `.gitignore` fully current,
    run `update --global`, assert byte-identical content before/after
  - test_gitignore_seed_failure_does_not_abort_propagation (R2): make one registered project's
    `.add/` unwritable (or otherwise force a write failure) alongside a second healthy project,
    run `update --global`, assert the healthy project is still reconciled and the run does not
    raise/crash (best-effort: simulate via a monkeypatch or a permission-denied fixture if a
    real OS-level unwritable dir proves too fragile in CI)
  - test_parity_call_site_present (M1/M2, structural): grep `_installer.py` for
    `_seed_gitignore(Path(np), home)` and `cli.js` for `seedGitignore(np)`, each appearing
    inside the propagation function/loop (matching `ParityHardenTest`'s existing convention of
    asserting call-sites, not just definitions)
</test_plan>

Tests live in: `add-method/tooling/test_update_global_gitignore_seed.py`. MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/src/add_method/_installer.py` · `add-method/bin/cli.js` · `add-method/tooling/test_update_global_gitignore_seed.py`
Strategy (ordered batches): 1. write the new hermetic test file mirroring `test_global_update_harden.py`'s `_Base` fixture pattern, confirm RED (the call sites don't exist yet, so a stale/partial `.gitignore` stays stale after `update --global`). 2. add the 2-line call site to `_update_global` (Python), confirm the pip-side tests go green. 3. add the matching call site to `cmdUpdateGlobal` (JS), confirm the npm-side tests go green (or honestly skip if node absent). 4. run the full suite, confirm no regression in the 2 sibling FROZEN test files (`test_global_install.py`, `test_global_update_harden.py`) whose synthetic fixtures lack `templates/gitignore.tmpl` (fail-soft skip expected, not a break).

Persona (optional): (absent — generic)
Known-problem fixes: `_seed_gitignore`/`seedGitignore` must stay fail-soft — wrap the new call the same way the existing call sites do (no added try/except needed since the functions themselves already fail-soft internally, confirmed at ground time); avoid the earlier session's tests→build test-file-edit tamper-tripwire trap by writing the COMPLETE test file (including any self-corrections) before crossing tests→build, not after.
Strategy actually used: as planned
Safety rule (feature-specific): the new call must never be placed BEFORE `_reconcile`/`reconcile` in the loop (gitignore seeding is independent of tree-restore order, but matching the contract's exact placement keeps the diff minimal and reviewable).
Code lives in: (no `src/` — this task edits existing installer functions directly, no new module)
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass
- [x] coverage did not decrease
- [x] no test or contract was altered during build (the new test file was written complete before crossing tests→build; §3 untouched post-freeze)
- [x] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [x] concurrency / timing of the risky operation is safe — n/a, sequential per-project loop, no new concurrency surface (the existing home file-lock already serializes the whole `update --global` run)
- [x] no exposed secrets, injection openings, or unexpected dependencies — 2-line call-site addition, zero new deps
- [x] layering & dependencies follow CONVENTIONS.md
- [x] a person reviewed and approved the change — Tin Dang approved the §3 freeze @ v1 and directed this task via AskUserQuestion ("Fix now, new task")

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] a project whose `.add/.gitignore` was blanked/stale gets it refreshed by `update --global`
  alone, no other command needed — confirmed by a REAL end-to-end manual run (not just the test
  harness): installed a project via `--global`, blanked its `.gitignore`, ran
  `_installer.update(..., as_global=True)` directly against the real bundled source, and the file
  came back with the correct `tooling/`/`docs/`/`personas-teacher/` + transient-artifact lines
- [x] a healthy sibling project is unaffected when another registered project's gitignore-seed
  write fails — confirmed by `test_seed_failure_does_not_abort_propagation` (monkeypatch-induced
  write failure on one project, asserted the other still got seeded and the run returned 0)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — the 2 new call sites (`_seed_gitignore(Path(np), home)` in `_installer.py`,
  `seedGitignore(np)` in `cli.js`) are each exercised by their respective test classes
  (`PipGlobalUpdateSeedsGitignore`, `NpmGlobalUpdateSeedsGitignore`) plus a structural
  call-site-presence check (`ParityCallSiteTest`) — confirmed reachable and referenced
- [x] DEAD-CODE (code) — no new symbol introduced (this task calls 2 EXISTING functions, adds no
  new function/class in production code); test-file helpers (`_make_bundled`, `_Base` methods)
  are all called by at least one test method — confirmed no orphan
- [x] SEMANTIC (prose / non-code) — read `_update_global`/`cmdUpdateGlobal` in full (not skimmed)
  before and after the edit, confirmed the 2-line addition sits in the documented, correct
  position (immediately after the sibling `_reconcile`/`reconcile` call, before `_persist_data`)

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> §0's Ground SHA anchors the symbols cited at ground time to that commit — code moves during
> build. Before the gate, re-resolve every symbol §3 CONTRACT cites against the CURRENT tree
> (not the Ground SHA) so a stale anchor is caught here, not by a future reader chasing a moved
> line.
- [x] every symbol §3 CONTRACT cites still resolves in the current tree — confirmed:
  `_update_global`, `_seed_gitignore`, `cmdUpdateGlobal`, `seedGitignore`, `_reconcile`/`reconcile`
  all read/edited at their cited locations; no drift since Ground SHA `81c8d05` (single-task
  window, this task's own commit is the only intervening change)
- [x] no anchor moved/renamed since Ground SHA

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self · adversarially checked: (1) confirmed 6 of the 7 new test methods were genuinely RED
before the build (the call sites didn't exist), and specifically noted the 7th
(`test_already_current_project_is_noop`) is a WEAK/vacuous-looking test in isolation (it would
trivially pass even with the bug present, since "never touching a file" also leaves it
"unchanged") — flagged this honestly rather than hiding it, and confirmed it still serves a real
purpose POST-fix (proving the new call doesn't cause a spurious rewrite when nothing is missing),
so it stays as an idempotency guard, not a discriminating red/green test; (2) ran the full
add-method suite (2609/2609 green, +7 exactly matching new tests, zero pre-existing test edited or
weakened); (3) explicitly re-ran the 2 sibling FROZEN test files
(`test_global_install.py`, `test_global_update_harden.py`, plus `test_global_data.py`/
`test_global_restore.py` for the same family) to confirm the new call site causes no regression —
their synthetic fixtures omit `templates/gitignore.tmpl` so the new call fail-soft-skips there,
exactly as designed, not accidentally; (4) independently reproduced the fix OUTSIDE the test
harness — a real `--global` install, a real blanked `.gitignore`, a real `update(as_global=True)`
call against the actual repo's bundled source, confirming the healed file matches expectations
byte-for-byte; (5) checked for stubbed/overfit logic — the failure-injection test
(`test_seed_failure_does_not_abort_propagation`) patches `Path.write_text` at the OS-call boundary
(not a higher-level mock of `_seed_gitignore` itself), so it genuinely exercises the real
exception-handling path inside `_seed_gitignore`, not a bypassed one.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: self
1. Security: CLEAR — no new write target (the call writes only to a project's own
   `.add/.gitignore`, the same file the existing per-project `update` path already writes);
   registry-path safety (absolute-path pre-scan, non-project drop) is untouched by this task
2. Concurrency: CLEAR — the whole `update --global` run is already serialized by the existing
   home file-lock (`_update_lock`/`acquireUpdateLock`); this task adds a synchronous call inside
   an already-sequential per-project loop, no new shared state or race surface
3. Architecture: CLEAR — reuses the existing fail-soft `_seed_gitignore`/`seedGitignore` functions
   unchanged; the fix is placement-only (one call site per twin), preserving the established
   npm/pip parity convention this family of tests already enforces
Verdict: PASS
Residue: none
Binding: advisory — mechanical (a call-site completeness fix, no method-defining decision; task
carries no `risk: high`)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-01

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): per-project gitignore-seed failure rate during
`update --global` (scenario R2's regression guard) — should stay at 0 in real fleets; any
nonzero rate not explained by transient disk/permission errors signals a template regression.

### Decisions (ADR)
- [AI] specify — chose add a `_seed_gitignore`/`seedGitignore` call inside the propagation loop,
  sourced from the just-refreshed home mirror; rejected re-seeding the home's own gitignore
  instead of per-project, rejected a separate `add.py heal-gitignore --global` command (manually
  corrected here — the auto-harvest degraded to `<unrecorded>` because `Framings weighed:` wrapped
  across multiple physical lines; see the ADD competency delta below)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
- [SPEC · open] harden `_framing()` (and any other `^Label:[ \t]*(.+)$` single-line extractor
  in `add.py`'s ADR harvester) to capture through the field's full wrapped paragraph instead of
  stopping at the first physical line, so a multi-line "Framings weighed:" harvests its
  `(chosen — ...)` marker correctly instead of degrading to `<unrecorded>` (evidence: this task's
  own §1 field wrapped after "...call inside the propagation loop, sourced" and the auto-harvested
  §7 Decisions line read `chose <unrecorded>` until hand-corrected above)

### Competency deltas
- [ADD · folded] the first-physical-line-only parser limitation previously known for §5 Scope also [folded foundation-version 60]
  hits §1's "Framings weighed:" field — any task author wrapping that field across lines for
  readability silently loses the ADR harvest's "(chosen ...)" detail even though the source-of-truth
  §1 prose stays fully correct (evidence: `grep -n "^Framings weighed:"` showed only the first
  physical line, `chose <unrecorded>` appeared in the harvested §7 Decisions block, and hand-editing
  §7 was needed since the harvest happens once at the tests→build/done transition, not on demand)
- [TDD · folded] a byte-identical idempotency test (`test_already_current_project_is_noop`) reads as [folded foundation-version 60]
  vacuous in isolation — it only proves something paired with a sibling test that actually mutates
  the same file; document that pairing requirement so future reviewers don't mistake it for a
  standalone regression guard (evidence: called out explicitly as a disclosed weak point in this
  task's §6 refute-read verdict, EARNED only because `test_stale_project_gets_gitignore_refreshed`
  and `test_custom_line_survives` cover the mutating side)

