# TASK: Extract IO + state primitives to add_engine/io_state.py

slug: extract-io-state · created: 2026-06-26 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. Multi-component repo (monorepo/multi-repo)? add a `component: <name>` line (declared in `.add/components.toml`) to ADD that component's root to your §5 Scope; omit for single-component projects (byte-identical default). -->
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
  - `add-method/tooling/add.py:47-92` — the 4 pure IO primitives `_now()` · `_atomic_write(path,text)` · `_atomic_write_bytes(path,data)` · `_atomic_write_many(writes)` (a CONTIGUOUS leaf block, ends right before `_templates_dir` at :93). Dependency scan: they call NOTHING outside themselves (stdlib os/tempfile/pathlib only). MOVE to `add_engine/io_state.py`; add.py re-imports them as module globals.
  - `add-method/tooling/add_engine/` — existing package (constants.py from task 1); add `io_state.py`.
  - `add-method/tooling/engine_pin.py` — `ENGINE_MD5` (md5 add.py) re-aimed; `ENGINE_PKG_MD5` (engine_manifest.package_digest over add_engine/*.py) re-aimed — both move because add.py shrinks and the package grows.
  - `add-method/tooling/test_scope_gate_enforce.py:394` + `add-method/tooling/test_guidelines.py:145` — the ONLY 2 sites that patch `add._atomic_write`; both intercept add.py-LEVEL callers (`_build_entry`, `cmd_sync_guidelines`) → the re-export (add.py imports `_atomic_write` as a module global, callers use bare names) keeps them GREEN with ZERO edits.
Context (working folder): the 3-tree engine mirror (canonical → `_bundled` via prepare_bundle → `.add` via cp); engine_manifest.package_digest already globs add_engine/*.py so io_state.py auto-joins the pin.
Honors (patterns / conventions): the task-1 playbook — re-export moved names as add.py module globals so `import add; add._atomic_write` + monkeypatching still resolve; two-pin model (ENGINE_MD5=md5(add.py) + ENGINE_PKG_MD5=package digest); byte-identical 3-tree mirror; zero behavior change.
Anchors the contract cites: `add_engine/io_state.py` · the 4 moved primitives · add.py re-import line · ENGINE_MD5 + ENGINE_PKG_MD5 re-aimed.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: extract the 4 pure IO primitives (`_now`, `_atomic_write`, `_atomic_write_bytes`, `_atomic_write_many`) from add.py:47-92 into `add_engine/io_state.py`; add.py re-imports them as module globals. Second module of the engine split (after constants). Pure refactor; zero behavior change. (The state/root/`_die` cluster is deferred to a follow-up `extract-state` task — kept out to keep this a clean contiguous leaf.)
Framings weighed: contiguous IO-primitives leaf (chosen) · whole io+state cluster · the full banner
  - chosen — move only the 4 contiguous dependency-free IO functions (47-92). Safest leaf: zero internal deps, covers the `add._atomic_write` monkeypatch (2 sites, preserved by re-export), proves the function-extraction pattern.
  - whole io+state cluster: deferred — pulls in `_die` (134 callers) + `_state_text_or_die` + load/save_state + find_root; a bigger, scattered (non-contiguous) move — its own task once the leaf pattern is banked.
Must:
<must>
  - `add_engine/io_state.py` defines the 4 primitives (moved verbatim); add.py no longer defines them but re-imports them (`from add_engine.io_state import _now, _atomic_write, _atomic_write_bytes, _atomic_write_many`) so `import add; add._atomic_write` resolves AND `add._atomic_write = spy` still intercepts add.py-level callers.
  - every CLI command + the full suite behave identically (the 2 `add._atomic_write` monkeypatch sites stay green untouched).
  - `ENGINE_MD5` re-aimed to the new md5(add.py); `ENGINE_PKG_MD5` re-aimed to the new package digest (now over constants.py + io_state.py + __init__.py); both literal, identical across all 3 trees.
  - io_state.py + add.py synced byte-identical across canonical · _bundled · .add.
</must>
Reject:
<reject>
  - a primitive's behavior changes or `add.<name>` stops resolving -> "io_primitive_drift" (round-trip identity test).
  - the pin recomputes itself in engine_pin.py -> "vacuous_pin" (engine_pin stays hashlib-free; digest in engine_manifest).
  - io_state missing from any of the 3 trees -> "mirror_incomplete".
</reject>
After:
<after>
  - the engine is a 3-module package (constants · io_state · the add.py entry); full suite ≥1823 green; both pins re-aimed; the next extraction proceeds.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ The 2 `add._atomic_write` patch sites intercept add.py-LEVEL callers (so re-export preserves them) — lowest confidence because if a third site (or one of these) patched `add._atomic_write` to intercept a call made INSIDE another moved function, the re-export wouldn't reach it. Verified: both call `_build_entry` / `cmd_sync_guidelines` (add.py-level); the moved 4 don't call each other in a patched path. Mitigation: the full suite is the gate. Cost if wrong: repoint that site to `add_engine.io_state._atomic_write`.
  - [ ] the 4 functions are a clean contiguous block 47-92 with no interleaved non-moved symbol — confirmed by the dependency scan (next def `_templates_dir` at :93).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the primitives moved but resolve unchanged
  Given the IO primitives are in add_engine/io_state.py
  When a test does `import add`
  Then add._now, add._atomic_write, add._atomic_write_bytes, add._atomic_write_many all resolve
  And each is the same object as add_engine.io_state.<name>

Scenario: monkeypatching add._atomic_write still intercepts add.py callers
  Given the split engine
  When a test sets add._atomic_write = spy and triggers _build_entry / cmd_sync_guidelines
  Then the spy is invoked (the re-export preserves the patch)
  And both existing patch sites (test_scope_gate_enforce, test_guidelines) stay green

Scenario: both pins re-aimed and 3-tree consistent
  Given add.py shrank and io_state.py joined the package
  When engine_pin + engine_manifest are read
  Then ENGINE_MD5 == md5(add.py) and ENGINE_PKG_MD5 == package_digest, identical across canonical/.add/_bundled
  And engine_pin.py contains no hashlib/read_bytes (pins stay literals)

Scenario: behavior unchanged
  Given the split engine
  When `add.py init` + `status` run on a fixture
  Then output is byte-identical to pre-split
  And the full suite is green
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add_engine/io_state.py (NEW module):
  imports: stdlib (os, sys?, tempfile, pathlib.Path) — the 4 fns use os.replace + tempfile only
  def _now() -> str                         # moved verbatim from add.py:47
  def _atomic_write(path, text) -> None     # moved verbatim (temp + os.replace)
  def _atomic_write_bytes(path, data) -> None
  def _atomic_write_many(writes) -> None

add.py (replaces the moved block, same location):
  from add_engine.io_state import _now, _atomic_write, _atomic_write_bytes, _atomic_write_many
  # all 134+ bare callers resolve add's module global -> monkeypatch add._atomic_write still works

engine_pin.py (two literals, re-aimed):
  ENGINE_MD5     = "<md5(new add.py)>"
  ENGINE_PKG_MD5 = "<package_digest over constants.py + io_state.py + __init__.py>"

Mirror: prepare_bundle already copies tooling/add_engine/ (task 1) -> io_state.py rides along;
        .add/tooling/add_engine/ cp'd byte-identical; installers copy tooling/ recursively (no edit).
```

Least-sure flag surfaced at freeze: [test] the 2 `add._atomic_write` monkeypatch sites stay green via re-export (they patch add.py-level callers, verified) — if a hidden site patches an io_state-internal call, the suite catches it and the fix is repointing that site to `add_engine.io_state._atomic_write`. Cost: 1-line test edit. (The contiguous-leaf move itself is low-risk — proven by task 1.)
Status: FROZEN @ v1 — approved by Tin Dang (auto mode; pure refactor, zero behavior change, suite-gated; task-1 pattern proven + merged)
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every scenario has one test; existing suite (≥1823) stays green.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_io_primitives_reexported: import add → assert add._now/_atomic_write/_atomic_write_bytes/_atomic_write_many resolve AND `is` the add_engine.io_state object (io_primitive_drift).
  - test_atomic_write_monkeypatch_preserved: set add._atomic_write = spy; call a path that routes through it; assert spy fired (re-export works). [the 2 existing sites also cover this live]
  - test_pkg_digest_includes_io_state: engine_manifest.package_files(canonical) includes io_state.py; package_digest == ENGINE_PKG_MD5 across 3 trees.
  - test_pins_literal_and_reaimed: ENGINE_MD5 == md5(add.py); engine_pin.py has no hashlib.
</test_plan>

Tests live in: `add-method/tooling/test_engine_extract_io_state.py` · MUST run red (no io_state.py yet) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/add_engine/io_state.py` `add-method/tooling/engine_pin.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add_engine/io_state.py`   <!-- the entry + new module + pins + the _bundled mirror. NOT listed: .add/tooling/** (pruned, cp-synced) · prepare_bundle (unchanged — task 1 already copies add_engine/) · engine_manifest (unchanged) · the §4 test file (tests phase). -->
Strategy (ordered batches): 1. create io_state.py with the 4 fns (verbatim), remove from add.py, add the re-import line — `import add` round-trips. 2. re-aim both pins (md5 add.py + package_digest). 3. prepare_bundle → _bundled; cp → .add. 4. full suite green.
Safety rule (feature-specific): zero behavior change; the 2 add._atomic_write monkeypatch sites MUST stay green (the re-export contract). engine_pin.py never hashes.
Code lives in: `add-method/tooling/`
Constraints: do NOT change any test or the contract; stdlib only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 1830/0 (was 1823; +7 new)
- [x] coverage did not decrease — +7 tests, +1 module under pin
- [x] no test or contract was altered during build — git status shows only the NEW test file; no `M` on any existing test; §3 untouched
- [x] the green was EARNED, not gamed — adversarial refute-read: the move is PROVABLY verbatim (git diff = 90 lines removed from add.py / 0 differ from io_state.py; only the 4 def removals + the re-import line). The real net is the 1830-test suite — incl. the 2 LIVE `add._atomic_write` patch sites (the actual consumers of the re-export contract) — green untouched, not the 7 new asserts.
- [x] concurrency / timing of the risky operation is safe — atomic-write semantics (temp→os.replace, all-or-nothing many-writer, .bak rollback) moved byte-for-byte; unchanged
- [x] no exposed secrets, injection openings, or unexpected dependencies — io_state imports stdlib only (os/tempfile/datetime/pathlib)
- [x] layering & dependencies follow CONVENTIONS.md — io_state is a LEAF (imports only stdlib); add.py → io_state is the only edge; no cycle (constants ← io_state ← add.py)
- [x] a person reviewed and approved the change — Tin Dang, auto mode (standing "auto mode all remaining work"; pure verbatim refactor, suite-gated, task-1 pattern proven+merged)

### Build expectations — what "correct" looks like
- [x] `import add; add._atomic_write is add_engine.io_state._atomic_write` True for all 4 — confirmed by the §4 round-trip test (is-same: True)
- [x] the 2 `add._atomic_write` monkeypatch sites (test_scope_gate_enforce, test_guidelines) pass untouched — 30/30 green
- [x] `engine_manifest.package_files` includes io_state.py; package_digest == ENGINE_PKG_MD5 across 3 trees — confirmed (. / .add / _bundled all True)
- [x] `import add` + CLI round-trips — confirmed by smoke + full suite
- [x] engine_pin.py has no hashlib (both pins literal) — confirmed (`hashlib in engine_pin.py? False`)

### Deep checks — do not skim
- [x] WIRING (code) — add.py re-imports + bare-calls the 4 primitives; io_state imported only by add.py; engine_manifest globs it into the pin
- [x] DEAD-CODE (code) — the 4 defs are GONE from add.py (diff confirms removal; test_add_py_no_longer_defines_them green); no orphan
- [x] SEMANTIC — n/a (code task)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-26   (auto mode — verbatim refactor, full suite 1830/0, seam audit clean 88, both pins re-aimed + 3-tree parity)

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
