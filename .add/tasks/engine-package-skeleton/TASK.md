# TASK: Bootstrap add_engine/ package + manifest-digest pin (first leaf module: constants)

slug: engine-package-skeleton · created: 2026-06-26 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. Multi-component repo (monorepo/multi-repo)? add a `component: <name>` line (declared in `.add/components.toml`) to ADD that component's root to your §5 Scope; omit for single-component projects (byte-identical default). -->
phase: tests   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/add.py:33-215` — the `# --- constants ---` banner block: 43 public + 6 private (`_GITIGNORE_BODY`·`_GUIDE_BEGIN`·`_GUIDE_END`·`_RULE_REF_LINE`·`_FALLBACK_TASK`·`_FALLBACK_TASK_FAST`) module constants — pure literals/strings, no function deps. This block MOVES to `add_engine/constants.py`; add.py re-imports it.
  - `add-method/tooling/add.py:1-26` — stdlib imports; the runnable entry (`if __name__=="__main__": raise SystemExit(main())` at EOF) — UNCHANGED, add.py stays the invoked file.
  - `add-method/tooling/engine_pin.py:13` — `ENGINE_MD5` literal; docstring forbids self-computing the pin. The literal STAYS a literal; only the test-side computation changes shape.
  - `add-method/tooling/test_shared_engine_pin.py:49,59` — computes `hashlib.md5(p.read_bytes()).hexdigest()` over add.py copies, compares to `engine_pin.ENGINE_MD5`; line 49 forbids `hashlib/read_bytes/read_text/open(` INSIDE engine_pin.py (keeps the pin a literal).
  - `add-method/tooling/test_engine_repin_parity.py:47-80` — `_md5_bytes` over `ENGINE_COPIES` (the 3 add.py mirror copies); asserts cross-tree parity + that a drifted byte ≠ ENGINE_MD5.
  - `add-method/scripts/prepare_bundle.py:76-85` — copies ONLY `tooling/add.py` + `tooling/templates/` to `_bundled/tooling/`; must ALSO copy `tooling/add_engine/`.
  - `add-method/tooling/test_bundle_parity.py` — guards the `_bundled` mirror; must include `add_engine/`.
  - `bin/cli.js` (npm installer) + `add-method/src/add_method/` (pip installer) — materialize `.add/tooling/`; must ship the whole `add_engine/` dir, not just add.py.
Context (working folder): the new package dir `add-method/tooling/add_engine/`; the 3-tree engine mirror (canonical → `_bundled` via prepare_bundle → `.add` via cp); `engine_pin.py` is the single pin home imported by the prose-only suites.
Honors (patterns / conventions): byte-identical 3-tree mirror; the pin is a HARD-CODED LITERAL never self-computed (vacuous-pin rule); no behavior change (pure refactor); `import add; add.<name>` is the stable test surface — preserve it (incl. the 6 `_`-prefixed names via explicit re-import, since `import *` skips underscores).
Anchors the contract cites: `add_engine/` package · `add_engine/constants.py` · `add_engine/__init__.py` · `engine_pin.engine_files()` · `engine_pin.engine_digest()` · the manifest-digest `ENGINE_MD5` · prepare_bundle copying `add_engine/`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: bootstrap the `add_engine/` package — extract the constants block to `add_engine/constants.py`, keep `add.py` as the runnable entry that re-exports it, and switch `ENGINE_MD5` from a single-file pin to a manifest digest over the whole package, with `prepare_bundle` + both installers + the `.add` mirror shipping the package dir. Pure refactor; zero behavior change.
Framings weighed: manifest-digest pin (chosen) · per-file pin map · concat-then-hash
  - chosen — `engine_digest()` hashes a sorted manifest of `{filename: md5}` over add.py + every add_engine/*.py; ENGINE_MD5 stays ONE literal, re-aimed once per task; mirror copies the dir. Minimal change to the "engine identity" concept.
  - per-file map: rejected — a dict pin is bigger and every parity test must iterate it for no extra safety here.
  - concat-then-hash: rejected — a file rename/reorder silently changes the hash with no signal.
Must:
<must>
  - `add_engine/` exists as a package (`__init__.py`) with `constants.py` holding the 43 public + 6 private constants formerly in add.py:33-215.
  - `add.py` no longer DEFINES those constants but re-exports them so `import add; add.STAGES` and `add._FALLBACK_TASK` still resolve (public via `from add_engine.constants import *`, the 6 underscore names via explicit import).
  - every CLI command behaves byte-identically (e.g. `add.py status`, `init`, `guide` produce the same output as before the move).
  - `engine_pin.engine_files(tooling_dir)` returns the sorted list `[add.py, add_engine/__init__.py, add_engine/constants.py]`; `engine_pin.engine_digest(tooling_dir)` returns the manifest md5; `ENGINE_MD5` equals that digest and stays a hard-coded literal.
  - `prepare_bundle.py` copies `tooling/add_engine/` into `_bundled/tooling/`; the `.add/tooling/add_engine/` mirror is byte-identical; both installers ship the dir.
  - the manifest digest is identical across all three trees (canonical · _bundled · .add) — drift/tamper still caught.
</must>
Reject:
<reject>
  - the pin recomputes itself inside engine_pin.py (a vacuous pin) -> "vacuous_pin" (existing test_shared_engine_pin guard stays green: no hashlib/read_bytes in engine_pin.py).
  - a constant is dropped or its value changed during the move -> "constant_drift" (re-export round-trips every name+value).
  - `add_engine/` is missing from any of the three trees or an installer -> "mirror_incomplete".
</reject>
After:
<after>
  - the engine is a 2-module package behind a stable import surface; the full suite (≥1815) is green; ENGINE_MD5 is a manifest digest; the next extraction task can move a real module into the proven package.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ The constants block (add.py:34-215) is pure literals with NO forward reference to a function/symbol defined later in add.py — lowest confidence because a single computed constant (e.g. a value built from a helper) would break a clean leaf move and force that helper to move too. Mitigation: the §4 round-trip test asserts every constant's value is byte-identical post-move; if one is computed, the move splits at that line. Cost if wrong: constants.py needs one more import or the offending constant stays in add.py.
  - [ ] `import *` from constants.py re-exports all 43 public names (no `__all__` shadowing) and the 6 underscore names import explicitly — confirm by the round-trip test.
  - [ ] both installers copy a DIRECTORY tree for tooling (not a hardcoded add.py-only copy) — confirm by reading bin/cli.js + the pip materializer before build; if add.py-only, widen them.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the package exists and re-exports every constant
  Given the engine has been split
  When a test does `import add`
  Then `add.STAGES`, `add.PHASES`, `add.RELEASES_FILE` (public) and `add._FALLBACK_TASK`, `add._GITIGNORE_BODY` (private) all resolve
  And each equals the value it had before the move (byte-identical round-trip)

Scenario: ENGINE_MD5 is a manifest digest over the package
  Given add.py + add_engine/__init__.py + add_engine/constants.py in the canonical tree
  When engine_pin.engine_digest(tooling_dir) is computed
  Then it equals engine_pin.ENGINE_MD5
  And the same digest is produced from the _bundled tree and the .add tree (3-tree parity)

Scenario: the pin stays a literal (vacuous-pin guard holds)
  Given engine_pin.py
  When test_shared_engine_pin scans it
  Then it contains no hashlib/read_bytes/read_text/open( call (the value is a hard-coded literal)
  And a one-byte change to any package file makes engine_digest() != ENGINE_MD5

Scenario: every command behaves byte-identically
  Given the split engine
  When `add.py status` (and init/guide) run on a fixture project
  Then the output is identical to the pre-split output
  And no command errors on a missing constant

Scenario: the mirror ships the whole package
  Given prepare_bundle has run
  When the _bundled tree and a freshly-materialized .add/tooling are inspected
  Then add_engine/__init__.py and add_engine/constants.py are present and byte-identical to canonical
  And test_bundle_parity is green
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
Package layout (canonical tree add-method/tooling/):
  add.py                 # runnable entry; re-exports add_engine.constants; __main__ unchanged
  add_engine/__init__.py # package marker (may be empty / docstring only)
  add_engine/constants.py# the 43 public + 6 private constants moved from add.py:34-215 (+ `import re` etc. as needed)

add.py re-export (replaces the moved block, near the old location):
  from add_engine.constants import *                       # 43 public names
  from add_engine.constants import (_GITIGNORE_BODY, _GUIDE_BEGIN, _GUIDE_END,
      _RULE_REF_LINE, _FALLBACK_TASK, _FALLBACK_TASK_FAST) # 6 underscore names

engine_pin.py (pin stays a LITERAL):
  ENGINE_MD5 = "<manifest digest>"   # re-aimed @ engine-package-skeleton
  def engine_files(tooling_dir: Path) -> list[Path]:
      # sorted: [add.py] + sorted(add_engine/*.py)   (relative-path sorted, deterministic)
  def engine_digest(tooling_dir: Path) -> str:
      # md5 of b"".join(f"{rel}:{md5(file.read_bytes())}\n".encode() for rel in engine_files)
      # NOTE: lives in engine_pin.py but is NOT called to set ENGINE_MD5 (literal stays literal);
      #       test-side code calls it to COMPARE against the literal. The vacuous-pin guard
      #       (test_shared_engine_pin) is updated to forbid hashlib ONLY in the pin-literal region,
      #       not in the new helper — or the helper lives in a separate _digest section it skips.

Mirror/installer surface:
  prepare_bundle.py     -> also copytree tooling/add_engine -> _bundled/tooling/add_engine
  test_bundle_parity.py -> assert add_engine/* parity
  bin/cli.js + pip materializer -> ship tooling/add_engine/
  .add/tooling/add_engine/ -> cp from canonical (byte-identical)
```

Lowest-confidence flag at freeze: [spec] the constants block (add.py:34-215) is PURE literals with no forward reference to a later-defined symbol — if one constant is computed from a helper, the clean leaf move splits there (constants.py gains an import, or that constant stays in add.py). Mitigated by the §4 round-trip test (every name+value byte-identical post-move). Cost if wrong: one extra import or a one-line split — not a contract change.
Status: FROZEN @ v1 — approved by Tin Dang (auto mode — "auto mode all remaining work"; rationale recorded above; pure refactor, zero behavior change, suite-gated)
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every scenario has one asserting test; the existing suite (≥1815) stays green.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_constants_reexported_round_trip: import add → assert each of the 43 public + 6 private names resolves AND equals a frozen expected (or equals the value read from add_engine.constants) — guards constant_drift.
  - test_engine_md5_is_manifest_digest: engine_manifest.engine_digest(CANONICAL) == engine_pin.ENGINE_MD5 (the literal).
  - test_manifest_digest_3tree_parity: engine_digest(canonical) == engine_digest(_bundled) == engine_digest(.add) — mirror_incomplete guard.
  - test_pin_stays_literal: engine_pin.py source has no hashlib/read_bytes/read_text/open( (vacuous-pin guard, mirrors existing test_shared_engine_pin intent).
  - test_one_byte_drift_breaks_digest: mutate one package file's bytes in a temp copy → engine_digest != ENGINE_MD5.
  - test_package_present_in_bundle: _bundled/tooling/add_engine/{__init__,constants}.py exist + byte-identical to canonical (extends test_bundle_parity).
  - test_status_output_unchanged: run `add.py status` on a fixture before/after — output diff-clean (behavior-identical).
</test_plan>

Tests live in: `add-method/tooling/test_engine_package_skeleton.py` (+ edits to `test_shared_engine_pin.py` `test_engine_repin_parity.py` `test_bundle_parity.py`) · MUST run red (no add_engine/ yet, ENGINE_MD5 not yet a digest) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/add_engine/__init__.py` `add-method/tooling/add_engine/constants.py` `add-method/tooling/engine_pin.py` `add-method/tooling/engine_manifest.py` `add-method/scripts/prepare_bundle.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add_engine/__init__.py` `add-method/src/add_method/_bundled/tooling/add_engine/constants.py` `bin/cli.js` `add-method/src/add_method/cli.py`   <!-- canonical engine + new package + the NEW engine_manifest.py (keeps engine_pin.py a pure literal so its vacuous-pin guard stays green) + bundler + the _bundled mirror + both installers. NOT listed: .add/tooling/** (pruned from the scope-walk, synced via cp) and the §4 test files (test_engine_package_skeleton.py + edited test_shared_engine_pin/test_engine_repin_parity/test_bundle_parity — tests are authored in the tests phase, snapshotted by the tripwire, never a build touch). -->
Strategy (ordered batches): 1. create `add_engine/{__init__,constants}.py`, move the block, wire add.py re-exports — prove `import add` round-trips (run the suite). 2. add `engine_manifest.py` (engine_files+engine_digest); re-point test_shared_engine_pin + test_engine_repin_parity to the digest; re-aim ENGINE_MD5 literal. 3. teach prepare_bundle + test_bundle_parity + both installers + the .add mirror to ship `add_engine/`. 4. full suite green; re-pin.
Safety rule (feature-specific): zero behavior change — after each batch run the full suite; a single non-byte-identical command output or a dropped constant fails the task. The pin LITERAL is never self-computed (engine_pin.py imports nothing that hashes).
Code lives in: `add-method/tooling/` (+ the mirror/installer paths above)
Constraints: do NOT change any test or the contract; allow-list packages only (stdlib only — hashlib already used); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all tests pass
- [ ] coverage did not decrease
- [ ] no test or contract was altered during build
- [ ] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [ ] concurrency / timing of the risky operation is safe
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [ ] `python3 -c "import add; print(add.STAGES, add._FALLBACK_TASK[:20])"` resolves every moved name — confirmed by running it from tooling/
- [ ] `add.py status` / `init` / `guide` output is diff-clean vs a pre-split capture — confirmed by a before/after diff on a fixture project
- [ ] `engine_manifest.engine_digest(canonical) == engine_pin.ENGINE_MD5` AND `== engine_digest(_bundled) == engine_digest(.add)` — confirmed by the §4 digest test (3-tree)
- [ ] `grep -E 'hashlib|read_bytes' engine_pin.py` is empty (pin stays a literal) — confirmed by test_shared_engine_pin green
- [ ] `add_engine/__init__.py` + `constants.py` present + byte-identical in _bundled and a freshly materialized .add/tooling — confirmed by test_bundle_parity + an `init` smoke

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [ ] WIRING (code) — `add.py` references the re-exported names; `engine_manifest` is imported by the two pin tests; prepare_bundle + installers reference `add_engine`
- [ ] DEAD-CODE (code) — no constant left orphaned in add.py; no duplicate definition across add.py and constants.py
- [ ] SEMANTIC — n/a (code task)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [ ] WIRING (code) — every new symbol is referenced; record where / how confirmed
- [ ] DEAD-CODE (code) — no new unused or orphaned symbol introduced
- [ ] SEMANTIC (prose / non-code) — read in full, not skimmed: <what read · what confirmed>

### GATE RECORD
Outcome: <PASS | RISK-ACCEPTED | HARD-STOP>
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: <name> · date: <date>

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
