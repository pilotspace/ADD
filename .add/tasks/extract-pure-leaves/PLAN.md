# TASK: Extract the last two pure leaves: _task_done -> predicates.py, _load_state_for_json -> io_state.py

slug: extract-pure-leaves · created: 2026-06-26 · stage: mvp
autonomy: auto
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/add.py:673-680` — `_task_done(t: dict) -> bool`. AST free-name scan: deps = NONE (pure dict read of phase+gate). A pure state-dict PREDICATE → its rightful home is `add_engine/predicates.py`. 17 bare callers across add.py (all resolve add's re-imported global post-move). Unpatched.
  - `add-method/tooling/add.py:149-160` — `_load_state_for_json() -> tuple[Path, dict]`. AST free-name scan: deps = `find_root`·`_die`·`_migrate_state`·`_state_text_or_die` (ALL already in io_state.py) + `json`·`Path` (stdlib, already imported by io_state). The fail-closed `--json` state loader → its rightful home is `add_engine/io_state.py`. 6 bare callers. Unpatched.
  - `add-method/tooling/add_engine/predicates.py` — gains `_task_done` (no new import needed).
  - `add-method/tooling/add_engine/io_state.py` — gains `_load_state_for_json` (calls its own module globals find_root/_die/_migrate_state/_state_text_or_die; json/Path already imported).
  - `add-method/tooling/add.py` — extend the existing `from add_engine.predicates import (...)` with `_task_done` and `from add_engine.io_state import (...)` with `_load_state_for_json`.
  - `add-method/tooling/engine_pin.py` — both pins re-aimed.
Context (working folder): the engine package (6 modules); 3-tree mirror. These are the LAST clean pure leaves — after this only the giant entangled regions (commands ~1300L · UDD ~1500L · report ~3100L) remain (their own sub-milestone).
Honors (patterns / conventions): the proven pure-leaf recipe (re-export as add globals; two-pin model; 3-tree byte-identical; zero behavior change; AST scan upfront); extend the rightful existing module rather than spawn a new one (predicate→predicates, state-load→io_state).
Anchors the contract cites: `_task_done`→predicates.py · `_load_state_for_json`→io_state.py · add.py re-imports · both pins.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: move the two remaining pure leaves to their rightful existing modules — `_task_done` (pure predicate) → predicates.py; `_load_state_for_json` (state loader, deps all in io_state) → io_state.py. add.py re-imports both. Seventh extraction; finishes the clean-leaf phase. Pure refactor; zero behavior change.
Framings weighed: extend the rightful existing module (chosen) · a new module per fn (rejected — neither is a new concern: one is a predicate, one is a state-load)
  - chosen — `_task_done` IS a state predicate (predicates.py's concern); `_load_state_for_json`'s every dep already lives in io_state.py. No new module, no cycle, no qualification (neither patched; bare callers resolve add's global).
Must:
<must>
  - predicates.py defines `_task_done` (verbatim); io_state.py defines `_load_state_for_json` (verbatim); add.py re-imports both so `add._task_done`/`add._load_state_for_json` resolve to the module objects.
  - every CLI command + the full suite behave identically (the `--json` paths + every done-check).
  - both pins re-aimed (literals); identical across all 3 trees; predicates.py + io_state.py byte-identical across canonical · _bundled · .add.
</must>
Reject:
<reject>
  - a fn's behavior changes or `add.<name>` stops resolving -> "leaf_drift".
  - the pin recomputes itself -> "vacuous_pin"; a tree missing the change -> "mirror_incomplete".
  - an import cycle (io_state↔predicates↔add) -> "cycle".
</reject>
After:
<after>
  - the clean-leaf phase is COMPLETE; add.py holds only the entangled core; full suite ≥1866 green; both pins re-aimed.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ `_load_state_for_json`'s deps are all already in io_state.py (find_root·_die·_migrate_state·_state_text_or_die) — lowest confidence near nil: AST scan + tasks-2/3 confirm they live there; json/Path are io_state imports. If wrong, the suite names it. Cost: fold the dep.
  - [ ] neither is monkeypatched — confirmed (grep empty).
  - [ ] no cycle — predicates.py already imports io_state (_die); _task_done adds no import; _load_state_for_json stays within io_state. No new edge.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: _task_done moved to predicates, resolves unchanged
  Given _task_done lives in add_engine/predicates.py
  When a test does `import add`
  Then add._task_done resolves AND is add_engine.predicates._task_done
  And _task_done({"phase":"done","gate":"PASS"}) is True; a bare `phase done` (gate none) is False

Scenario: _load_state_for_json moved to io_state, resolves unchanged
  Given _load_state_for_json lives in add_engine/io_state.py
  When a test does `import add`
  Then add._load_state_for_json resolves AND is add_engine.io_state._load_state_for_json
  And a --json command in a real project returns (root, migrated_state)

Scenario: both gone from add.py, no cycle, 3-tree pins consistent
  Given the two moves
  Then add.py defines neither (re-import only); no import cycle
  And ENGINE_PKG_MD5 == package_digest across 3 trees; ENGINE_MD5 == md5(add.py); engine_pin.py no hashlib
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add_engine/predicates.py: + def _task_done(t: dict) -> bool          # moved verbatim (no new import)
add_engine/io_state.py:   + def _load_state_for_json() -> tuple[Path, dict]   # moved verbatim
                            (uses io_state's own find_root/_die/_migrate_state/_state_text_or_die + json/Path)

add.py:
  from add_engine.predicates import ( ..., _task_done )                # extend the existing re-import
  from add_engine.io_state  import ( ..., _load_state_for_json )       # extend the existing re-import
  # the two defs removed; bare callers resolve add's module global; add.<name> still works

engine_pin.py: ENGINE_MD5 + ENGINE_PKG_MD5 re-aimed (literals; never hashes).
Mirror: prepare_bundle -> _bundled; cp add.py+add_engine -> .add (no engine_pin.py in .add runtime).
```

Least-sure flag surfaced at freeze: [test] none material — both pure & unpatched; AST scan confirms _load_state_for_json's deps already live in io_state.py; the 1866-suite exercises every --json path and done-check. Cost if wrong: suite names it; fold.
Status: FROZEN @ v1 — approved by Tin Dang (auto mode; pure verbatim refactor, AST-verified, unpatched, suite-gated; the proven leaf recipe ×6)

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every scenario has one test; existing suite (≥1866) stays green.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_task_done_in_predicates_reexported: add._task_done is add_engine.predicates._task_done; the done/not-done truth table holds.
  - test_load_state_for_json_in_io_state_reexported: add._load_state_for_json is add_engine.io_state._load_state_for_json; a real --json load returns (root, migrated state).
  - test_add_py_no_longer_defines_them: add.py carries no `def _task_done(`/`def _load_state_for_json(`.
  - test_no_import_cycle: importing add_engine.predicates + add_engine.io_state standalone does not require add.
  - test_pkg_digest_3tree + test_pins_literal_and_md5.
</test_plan>

Tests live in: `add-method/tooling/test_engine_extract_pure_leaves.py` · MUST run red before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/add_engine/predicates.py` `add-method/tooling/add_engine/io_state.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_engine_extract_pure_leaves.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add_engine/predicates.py` `add-method/src/add_method/_bundled/tooling/add_engine/io_state.py`
Strategy (ordered batches): 1. move _task_done → predicates.py + _load_state_for_json → io_state.py (verbatim); remove both from add.py; extend the two re-imports. 2. AST undefined-name scan of both modules. 3. re-aim both pins. 4. prepare_bundle → _bundled; cp → .add. 5. full suite green.
Safety rule (feature-specific): zero behavior change; engine_pin.py never hashes; no import cycle; AST scan before suite.
Code lives in: `add-method/tooling/`
Constraints: do NOT change any test or the contract; stdlib only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all tests pass
- [ ] coverage did not decrease
- [ ] no assertion was weakened
- [ ] the green was EARNED, not gamed — adversarial refute-read; a confirmed cheat is HARD-STOP
- [ ] concurrency / timing safe
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like
- [ ] add._task_done is add_engine.predicates._task_done; truth table holds — §4
- [ ] add._load_state_for_json is add_engine.io_state._load_state_for_json; --json load works — §4
- [ ] add.py defines neither; no import cycle — §4
- [ ] package_digest == ENGINE_PKG_MD5 across 3 trees; ENGINE_MD5 == md5(add.py); engine_pin.py no hashlib

### Deep checks — do not skim
- [ ] WIRING (code) — add.py extends both re-imports; predicates gains _task_done (no new import), io_state gains _load_state_for_json (own globals)
- [ ] DEAD-CODE (code) — both GONE from add.py; no orphan
- [ ] SEMANTIC — n/a (code task)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-26

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): suite green · ENGINE_PKG_MD5 stability

### Spec delta
- [SPEC · dropped] clean-leaf phase COMPLETE; remaining = the entangled giant regions (commands/udd/report) → scope as a sub-milestone using the qualification technique proven on identity (evidence: this finishes the pure leaves)

### Competency deltas
- [ADD · folded] a pure helper's rightful home is the existing module that owns its concern/deps (predicate→predicates, state-load→io_state) — extend, don't proliferate modules (evidence: _task_done, _load_state_for_json) [folded foundation-version 52]
