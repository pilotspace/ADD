# TASK: Stop dev junk shipping in the npm tarball

slug: npm-hygiene · created: 2026-05-29 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

The published `@mrq/add` tarball must contain only the runtime surface — no dev junk.
Ground truth from `npm pack --dry-run` (2026-05-29): the tarball ships 9 `__pycache__/*.pyc`
files (~130kB, incl. an orphaned `test_quickstart_vi.cpython-314.pyc` whose source was
deleted) and 7 `tooling/test_*.py` sources. `cli.js` already treats the install as
"runtime-only" (strips test_*.py + __pycache__ when copying into the target), so shipping
them in the tarball is incoherent dead weight. `.DS_Store` does NOT ship (npm default-ignores
it) — the old memory note was wrong; `__pycache__` is the real culprit.

Must:
  - The npm tarball MUST NOT contain any `__pycache__/`, `*.pyc`/`*.pyo`, or `test_*.py`.
  - The tarball MUST still contain the runtime surface: `bin/cli.js`, `skill/`, `docs/`,
    `tooling/add.py`, `tooling/templates/`, `README.md`, `GETTING-STARTED.md`.
  - `engines.node` MUST be `>=18` (cli.js uses `fs.cpSync`, added 16.7; 16 is EOL).
  - Defense in depth: BOTH a `.npmignore` (denylist OS/build junk) AND a tightened `files`
    allowlist (name `tooling/add.py` + `tooling/templates/`, not the whole `tooling/`), so a
    future `.pytest_cache`/`.mypy_cache` can't leak without a deliberate change.
  - A guard test pins this: `npm pack --dry-run --json` shows zero junk entries.
Reject (guard-test failure modes, not user input — this is config):
  - any junk entry in the dry-run file list -> test fails naming the offending path.
After:
  - `npm pack --dry-run` lists only runtime files; `engines.node == ">=18"`; the guard test
    is green (or cleanly skipped where `npm` is absent).
Assumptions (confirm before building):
  - [x] exclude test_*.py from the tarball (cli.js already strips them; minimal ethos) — user-confirmed
  - [x] add a durable guard test, npm-coupled but `skipif npm absent` — user-confirmed
  - [x] dogfood as a gated v1-1 task — user-confirmed
  - [x] clean the working-tree `__pycache__` first (npm packs the working dir, not git)

<!-- EXIT: every rule stated, every rejection has a named code, zero open assumptions. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: no compiled bytecode ships
  Given the package with a stray tooling/__pycache__ on disk
  When I run `npm pack --dry-run --json`
  Then no listed file path contains "__pycache__" or ends in ".pyc"/".pyo"

Scenario: no test sources ship
  Given the package
  When I run `npm pack --dry-run --json`
  Then no listed file path matches "test_*.py"

Scenario: the runtime surface still ships
  Given the package
  When I run `npm pack --dry-run --json`
  Then the list includes bin/cli.js, tooling/add.py, a tooling/templates/* file,
       a skill/* file, a docs/* file, README.md and GETTING-STARTED.md

Scenario: node floor is correct
  Given package.json
  When I read engines.node
  Then it is ">=18"

Scenario: the guard is honest when npm is unavailable
  Given an environment with no `npm` on PATH
  When the guard test runs
  Then it SKIPS (never a false green, never a hard error)
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
artifact: package.json  (config, not code)
  engines.node           = ">=18"
  files (allowlist)      = ["bin/", "skill/", "tooling/add.py", "tooling/templates/",
                            "docs/", "README.md", "GETTING-STARTED.md"]
                           # was ["tooling/"] — now names only the runtime subpaths

artifact: .npmignore  (new — denylist, defense in depth)
  __pycache__/
  *.pyc
  *.pyo
  .DS_Store
  *.swp

invariant: `npm pack --dry-run --json` -> files[].path satisfies
  none match  (/__pycache__/ | \.py[co]$ | (^|/)test_.*\.py$)
  all present (bin/cli.js, tooling/add.py, tooling/templates/, skill/, docs/,
               README.md, GETTING-STARTED.md)

test: add-method/tooling/test_packaging.py
  @skipif shutil.which("npm") is None    # honest skip, never false-green
  runs `npm pack --dry-run --json` from the package root, parses files[].path
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit)   <!-- Changing a frozen contract = change request back to SPECIFY. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: all 5 scenarios (new file add-method/tooling/test_packaging.py).
Plan (run `npm pack --dry-run --json` ONCE in setUpClass; parse files[].path):
  - test_no_bytecode_or_os_junk_ships: no path has "__pycache__", ends .pyc/.pyo, or is .DS_Store
  - test_no_test_sources_ship:  no path matches (^|/)test_.*\.py$
  - test_runtime_surface_ships: bin/cli.js, tooling/add.py, a tooling/templates/*, a skill/*,
                                a docs/*, README.md, GETTING-STARTED.md all present
  - test_node_floor_is_18:      package.json engines.node == ">=18"  (reads file, no npm)
  - scenario 5 (honest skip):   realized by `@skipUnless(_npm_on_path(), ...)` on the npm-coupled
                                tests — a missing npm SKIPS, never false-greens; not a standalone
                                test (asserting one's own skip decorator is circular).
Red-for-the-right-reason (before build): test_*.py ship via files:["tooling/"] -> red;
engines is ">=16" -> red; __pycache__ present on disk -> red. NOT a parse/import error.

Tests live in: `add-method/tooling/test_packaging.py` · MUST run red before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): an allowlist (`files`) is the primary filter — strictly
more robust than a denylist, since unforeseen junk can't leak without a deliberate change.
The `.npmignore` is defense-in-depth for junk inside an allowlisted dir + `.DS_Store`
everywhere. Clean the working-tree `__pycache__` before any `npm pack` (npm reads the
working dir, not git). No code/behavior change — config only; zero npm dependencies added.
Changes:
  - `add-method/package.json`: `files` "tooling/" -> "tooling/add.py" + "tooling/templates/";
    `engines.node` ">=16" -> ">=18".
  - `add-method/.npmignore` (new): __pycache__/, *.pyc, *.pyo, .DS_Store, *.swp.
  - `bin/cli.js` UNCHANGED — its test/__pycache__ prune stays as defense-in-depth for non-tarball
    install paths (`npm link`, git/monorepo installs) the allowlist doesn't cover.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — 67/67 green; 4 new in test_packaging.py (3 npm-coupled + 1 config)
- [x] coverage did not decrease — tests only added; red-first confirmed (3 FAIL for the right
      reason: ">=16"!=">=18", test sources listed, __pycache__ listed; runtime-surface stayed green)
- [x] no test or contract was altered during build — contract FROZEN @ v1; config-only change
- [x] concurrency / timing safe — guard runs `npm pack` with a 120s timeout (design-for-failure);
      no shared mutable state; reject path is the test failing, not a partial write
- [x] no exposed secrets / injection / unexpected deps — zero npm deps added; subprocess argv is a
      fixed list (no shell, no interpolation); `.npmignore` + `files` are static config
- [x] layering & deps follow CONVENTIONS.md — packaging config only; stdlib-only test (shutil,
      subprocess, json, re); cli.js untouched
- [x] a person reviewed — author self-review + advisor review of the approach (allowlist+denylist,
      exclude tests, npm-coupled guard with honest skip). Empirical evidence: tarball 68->52 files,
      `npm pack --dry-run --json` junk check = NONE. Human author sign-off: pending pre-push.

### GATE RECORD
Outcome: PASS
Reviewed by: author (self) + advisor (approach) · date: 2026-05-29 · author sign-off pre-push
Evidence: red→green on test_packaging.py (3 RED for the right reason → 4 GREEN); `npm pack
--dry-run` 68→52 files, tooling/ = add.py + templates/ only, junk check NONE; full suite 67/67.
Allowlist-narrowing risk closed: `tooling/` before = {add.py, templates/*, test_*.py, __pycache__/*};
after = {add.py, templates/*} — everything dropped was test/bytecode, so NO runtime file was excluded
(the package is correct, not merely junk-free).

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): run `npm test` (or test_packaging.py) before every
publish — the guard is the monitor. If it ever skips silently in CI, CI lacks npm; gate on
npm presence there. Watch tarball size: docs/*.jpg (~2.7MB of 2.8MB) dominate — if install
weight becomes a complaint, that's the lever, not the now-clean tooling surface.

Guard scope (known limit): test_packaging.py verifies the npm MANIFEST (files[].path from
`npm pack --dry-run`), NOT an actual install round-trip. It proves the right files are LISTED,
not that `npx @mrq/add init` still RUNS after a `files` change. Failure mode it can't catch: a
new runtime file cli.js reads, added but forgotten in the `files` allowlist. An install test
(pack → extract → `add.py init` → `add.py status`) would close that — out of scope for this chore.

Spec delta for the next loop:
  - docs images: 5 of 9 shipped *.jpg are orphans (no chapter references them) — ADD-context-engine,
    AIDD, cognitive-matrix (the authoritative methodology diagrams: intentional reference assets even
    if not inline-linked), risk-matrix, and community.jpg (268kB). community.jpg is ALSO Vietnamese-
    language content shipping in the English-only product. It is NOT the "Học Ứng Dụng AI" branding
    266b45f removed (a different asset — that removal was complete); this is a separate, smaller
    English-only inconsistency. A docs-image cleanup (drop truly-dead images / lower-res / docs-site
    link) is a candidate next task, not part of this one.
  - consider a `prepublishOnly` script that runs the guard so a dirty working tree (stray
    __pycache__) can never publish.
Memory corrected: `.DS_Store` never leaked (npm default-ignores it); `__pycache__/*.pyc` +
test_*.py were the real junk.
