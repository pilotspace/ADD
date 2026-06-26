# TASK: Fold md5 hashing helpers (2 fns) into add_engine/io_state.py

slug: extract-md5 · created: 2026-06-26 · stage: mvp
autonomy: auto
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/add.py` — `_md5_text`(3188) + `_md5_file`(3192): tiny PURE hashing helpers. `_md5_file` is fail-closed (OSError → None: an unreadable tracked file counts DIVERGED at the gate, never a crash). Closed (no add-fn calls); deps = `hashlib` + `Path` (stdlib). NONE patched. Used widely (snapshot/contract/scope-gate @528·3209·3217·3225·3229·3349·3428·3447).
  - `add-method/tooling/add_engine/io_state.py` — the low-level IO/byte primitives module (`_atomic_write*`, `find_root`, `_die`, `_state_text_or_die`). md5-of-bytes/text is an IO primitive → FOLD here (precedent: io_state already grew `_load_state_for_json`; predicates grew `_task_done`). Add `import hashlib`; append the 2 fns verbatim.
  - `add-method/tooling/add.py` — remove the 2 defs; add `_md5_text, _md5_file` to the EXISTING `from add_engine.io_state import (...)` block.
  - `add-method/tooling/engine_pin.py` — both pins re-aimed.
Context: engine package (10 modules; io_state GROWS, no new module). 3-tree mirror. Callers stay (bare → add's re-imported global).
Honors: grow-an-existing-module recipe (re-export, NO qualification since unpatched); a SHARED low-level helper joins the foundational io_state module.
Anchors: io_state.py (+hashlib +2 fns) · add.py io_state re-import block · both pins.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: fold the 2 md5 hashing helpers from add.py into add_engine/io_state.py; add.py re-imports via the existing io_state block. Twelfth extraction (a module-grow, not a new module). Pure refactor; zero behavior change incl. the fail-closed OSError→None path.
Framings weighed: fold md5 into io_state (chosen) · a new 2-fn hashing.py (rejected — two one-liners don't warrant a module; io_state IS the low-level byte/IO primitives home)
  - chosen — md5-of-bytes/text is a low-level IO primitive; io_state already imports Path and owns _atomic_write/read paths; precedent set by _load_state_for_json / _task_done.
Must:
<must>
  - io_state.py defines `_md5_text` + `_md5_file` (verbatim) + `import hashlib`; add.py re-imports both so `add._md5_text`/`add._md5_file` resolve to the io_state objects.
  - every hashing path (snapshot/contract/scope-gate md5s) behaves identically incl. _md5_file's OSError→None; full suite passes unchanged.
  - both pins re-aimed (literals); 3-tree byte-identical.
</must>
Reject:
<reject>
  - a hash changes, the fail-closed None path breaks, or `add.<name>` stops resolving -> "hash_drift".
  - the pin recomputes itself -> "vacuous_pin"; a tree's io_state.py out of sync -> "mirror_incomplete".
  - an import cycle (io_state↔add) -> "cycle" (io_state imports only constants + stdlib).
</reject>
After:
<after>
  - io_state.py owns the md5 helpers; engine stays 10 modules; full suite ≥1909 green; both pins re-aimed.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ `import hashlib` added to io_state keeps it cycle-free and the helpers resolve in every caller — high confidence (hashlib is stdlib; add.py re-imports both; callers bare-resolve add's global). Cost if wrong: fix the import.
  - [ ] both closed + unpatched + only hashlib/Path — confirmed.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the 2 fns folded but resolve unchanged
  Given they live in add_engine/io_state.py
  When a test imports add
  Then add._md5_text / add._md5_file resolve AND are the add_engine.io_state objects

Scenario: hashing is preserved incl. fail-closed
  Given the folded helpers
  When _md5_text("x") and _md5_file(<missing path>) run
  Then _md5_text returns the known md5 hex AND _md5_file returns None on OSError (never raises)

Scenario: no cycle; io_state grows, 3-tree consistent
  Then importing add_engine.io_state standalone needs no add; ENGINE_PKG_MD5 == package_digest (io_state.py grew) across 3 trees; ENGINE_MD5 == md5(add.py); engine_pin.py no hashlib
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add_engine/io_state.py:
  import hashlib                         # + (new)
  def _md5_text(s) -> str       ...      # appended verbatim
  def _md5_file(p) -> str | None ...     # appended verbatim (OSError -> None)

add.py:
  from add_engine.io_state import (
      ..., _md5_text, _md5_file,         # added to the existing block
  )   # the 2 defs removed; bare callers resolve add's global

engine_pin.py: ENGINE_MD5 + ENGINE_PKG_MD5 re-aimed (literals; never hashes).
Mirror: prepare_bundle -> _bundled; cp add.py+add_engine -> .add (no engine_pin.py in .add runtime).
```

Least-sure flag surfaced at freeze: [test] none material — closed + unpatched + stdlib-only; the 1909-suite (every md5 path) is the gate. Cost if wrong: fix the import.
Status: FROZEN @ v1 — approved by Tin Dang (auto mode; closed unpatched helpers, stdlib-only, suite-gated; the proven grow-a-module recipe)

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every scenario has one test; existing suite (≥1909) stays green.
Plan:
<test_plan>
  - test_md5_folded_same_object: add._md5_text/_md5_file resolve AND `is` the add_engine.io_state object.
  - test_md5_preserved: _md5_text("abc") == known hex; _md5_file(missing) is None (fail-closed).
  - test_no_import_cycle + test_pkg_digest_3tree + test_pins_literal_and_md5 + test_add_py_no_longer_defines_them.
</test_plan>

Tests live in: `add-method/tooling/test_engine_extract_md5.py` (DECLARED in §5; written in tests phase BEFORE the tests→build crossing) · MUST run red before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/add_engine/io_state.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_engine_extract_md5.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add_engine/io_state.py`
Strategy: 1. (tests) write the new test red. 2. (build) add `import hashlib` + append the 2 fns verbatim to io_state.py; remove the 2 defs from add.py; add both names to the existing io_state re-import block. 3. AST undefined-name scan. 4. re-aim both pins. 5. prepare_bundle → _bundled; cp → .add. 6. full suite green.
Safety rule: zero behavior change; engine_pin.py never hashes; no cycle.
Code lives in: `add-method/tooling/`
Constraints: do NOT change any test or the contract; stdlib only.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all tests pass
- [ ] coverage did not decrease
- [ ] no assertion was weakened
- [ ] the green was EARNED, not gamed — adversarial refute-read; a confirmed cheat is HARD-STOP
- [ ] concurrency / timing safe (pure hashing; fail-closed read)
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like
- [ ] both `add.<name> is add_engine.io_state.<name>` — §4
- [ ] _md5_text known hex; _md5_file(missing) is None — §4
- [ ] no import cycle — §4
- [ ] package_digest == ENGINE_PKG_MD5 across 3 trees (io_state grew); ENGINE_MD5 == md5(add.py); engine_pin.py no hashlib

### Deep checks — do not skim
- [ ] WIRING — add.py re-imports both via the io_state block; io_state imports hashlib; engine_manifest unchanged (same files)
- [ ] DEAD-CODE — the 2 defs GONE from add.py; no orphan
- [ ] SEMANTIC — n/a (code task)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-26

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch: snapshot/contract/scope-gate md5 paths · ENGINE_PKG_MD5 stability

### Spec delta
- [SPEC · open] remaining clean cluster: version (`_fetch_latest_version`/`_read_json_safe`/`_version_gt` + private `_REGISTRY_LATEST`; the test reassigns `add._fetch_latest_version` → standard re-export, caller stays in add.py). THEN the coupled CORE (deltas/autonomy/next-pair/cmd_*/report_data/save/load/main) is a 31-fn web around load_state — NOT a clean cluster; probe for closed SUB-clusters, else it stays as the add.py entry/orchestrator module (evidence: closure scan from cmd_deltas = 31 fns crossing load_state/report_data/autonomy)

### Competency deltas
- [ADD · open] a 2-line low-level helper folds INTO the nearest foundational module (io_state) rather than spawning a thin single-purpose module — modularization groups by concern, not by maximizing module count (evidence: md5 → io_state, not a new hashing.py)
