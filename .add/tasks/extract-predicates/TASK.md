# TASK: Extract state/markdown predicates to add_engine/predicates.py

slug: extract-predicates · created: 2026-06-26 · stage: mvp
autonomy: auto
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/add.py:246-300` — 4 CONTIGUOUS unpatched predicates (block ends before `_stamp_gate_record` at :301): `_phase_owner(phase)` · `_setup_locked(state)` · `_milestone_confirmed(state, mslug)` · `_section_unfilled(md_text, header)`. AST free-name scan: deps = `PHASE_OWNER` (constant) + `_die` (io_state) + `re` (stdlib); `_setup_locked`/`_milestone_confirmed` are pure dict reads; `ln` in `_section_unfilled` is a for-loop var (false positive). MOVE to a NEW `add_engine/predicates.py`.
  - `add-method/tooling/add_engine/predicates.py` — NEW module: `import re` + `from add_engine.constants import PHASE_OWNER` + `from add_engine.io_state import _die`.
  - `add-method/tooling/engine_pin.py` — `ENGINE_MD5` + `ENGINE_PKG_MD5` re-aimed.
  - patch landscape: NONE of the 4 patched. The entangled accessor-seam neighbours (`_my_work`/`_load_state_for_json`/`_stamp_gate_record` + identity fns) stay in add.py for their own tasks.
Context (working folder): the engine package (constants · io_state · accessors · NEW predicates · the add.py entry); 3-tree mirror.
Honors (patterns / conventions): the tasks-1-4 playbook — re-export as add.py module globals; two-pin model; byte-identical 3-tree mirror; zero behavior change; AST free-name scan ran UPFRONT (clean).
Anchors the contract cites: `add_engine/predicates.py` (NEW) · the 4 predicates · add.py re-import · both pins re-aimed.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: move 4 pure state/markdown predicates (`_phase_owner`, `_setup_locked`, `_milestone_confirmed`, `_section_unfilled`) from add.py into a NEW `add_engine/predicates.py`; add.py re-imports them. Fifth extraction of the engine split. Pure refactor; zero behavior change.
Framings weighed: the 4 contiguous unpatched predicates into a new predicates.py (chosen) · fold into accessors.py
  - chosen — a clean contiguous unpatched block with importable deps; a distinct concern (phase ownership · setup/milestone gating · section-filled checks) → its own module.
  - fold into accessors.py: rejected — accessors.py is purposely import-free (pure dict ops); these need re/constants/io_state, a different dependency profile.
Must:
<must>
  - `add_engine/predicates.py` defines the 4 (moved verbatim); add.py re-imports them so `add._phase_owner`/`add._setup_locked`/`add._milestone_confirmed`/`add._section_unfilled` all resolve to the predicates objects.
  - every CLI command + the full suite behave identically.
  - `ENGINE_MD5` re-aimed to md5(new add.py); `ENGINE_PKG_MD5` re-aimed (predicates.py joins the digest); both literal, identical across all 3 trees.
  - predicates.py + add.py synced byte-identical across canonical · _bundled · .add.
</must>
Reject:
<reject>
  - a predicate's behavior changes or `add.<name>` stops resolving -> "predicate_drift".
  - the pin recomputes itself in engine_pin.py -> "vacuous_pin".
  - predicates.py missing from any of the 3 trees -> "mirror_incomplete".
</reject>
After:
<after>
  - the engine package gains predicates.py (5 modules); full suite ≥1846 green; both pins re-aimed; the next extraction proceeds.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ The 4 predicates' deps are fully importable (PHASE_OWNER·_die·re) — lowest confidence near nil: AST scan confirmed; PHASE_OWNER is in add_engine.constants, _die in add_engine.io_state. If wrong, the suite names it. Cost: fold the dep.
  - [ ] none of the 4 are monkeypatched — confirmed.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the 4 predicates moved but resolve unchanged
  Given the predicates live in add_engine/predicates.py
  When a test does `import add`
  Then add._phase_owner, add._setup_locked, add._milestone_confirmed, add._section_unfilled all resolve
  And each is the same object as add_engine.predicates.<name>

Scenario: predicate behavior is preserved
  Given the split engine
  When _phase_owner("contract") / _setup_locked(state) / _section_unfilled(md, header) are called
  Then they return the same values as before (phase owner mapping, lock check, fill check)

Scenario: predicates.py joins the package pin, 3-tree consistent
  Given predicates.py is new in the package
  When engine_manifest + engine_pin are read
  Then ENGINE_PKG_MD5 == package_digest (incl. predicates.py), identical across the 3 trees
  And ENGINE_MD5 == md5(add.py); engine_pin.py has no hashlib
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add_engine/predicates.py (NEW module):
  import re
  from add_engine.constants import PHASE_OWNER
  from add_engine.io_state import _die
  def _phase_owner(phase) -> str                       # moved verbatim
  def _setup_locked(state) -> bool                     # moved verbatim
  def _milestone_confirmed(state, mslug) -> bool       # moved verbatim
  def _section_unfilled(md_text, header) -> bool       # moved verbatim

add.py (the 4 defs removed; re-import added):
  from add_engine.predicates import (
      _phase_owner, _setup_locked, _milestone_confirmed, _section_unfilled,
  )   # bare callers resolve add's module global; `add.<name>` still works

engine_pin.py (two literals, re-aimed):
  ENGINE_MD5     = "<md5(new add.py)>"
  ENGINE_PKG_MD5 = "<package_digest over the add_engine/*.py modules>"

Mirror: prepare_bundle → _bundled; cp add.py+engine_pin+add_engine → .add (no engine_pin.py in .add runtime).
```

Least-sure flag surfaced at freeze: [test] none material — AST free-name scan (run UPFRONT) confirms deps are importable (PHASE_OWNER·_die·re); the 4 are unpatched. Residual risk: a caller relying on these being local — covered by the full 1846-suite. Cost if wrong: suite names it; fold.
Status: FROZEN @ v1 — approved by Tin Dang (auto mode; pure verbatim refactor, AST-verified, suite-gated; tasks 1-4 pattern proven+merged)

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every scenario has one test; existing suite (≥1846) stays green.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_predicates_reexported_same_object: import add → all 4 resolve AND `is` the add_engine.predicates object.
  - test_predicate_behavior_preserved: _phase_owner returns the PHASE_OWNER mapping; _section_unfilled detects a filled vs unfilled section.
  - test_pkg_digest_includes_predicates_3tree: package_files includes predicates.py; package_digest == ENGINE_PKG_MD5 across 3 trees.
  - test_pins_literal_and_md5: ENGINE_MD5 == md5(add.py); engine_pin.py has no hashlib.
  - test_add_py_no_longer_defines_them: add.py carries no `def <name>(` for the 4.
</test_plan>

Tests live in: `add-method/tooling/test_engine_extract_predicates.py` · MUST run red (no predicates.py yet) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/add_engine/predicates.py` `add-method/tooling/engine_pin.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add_engine/predicates.py`
Strategy (ordered batches): 1. create predicates.py with the 4 (verbatim) + imports, remove from add.py, add the re-import. 2. AST undefined-name scan of predicates.py. 3. re-aim both pins. 4. prepare_bundle → _bundled; cp → .add. 5. full suite green.
Safety rule (feature-specific): zero behavior change; engine_pin.py never hashes; AST scan before suite.
Code lives in: `add-method/tooling/`
Constraints: do NOT change any test or the contract; stdlib only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 1854/0 (was 1846; +8 new)
- [x] coverage did not decrease — +8 tests, +1 module under the package pin
- [x] no test or contract was altered during build — git status shows only the NEW test file; §3 untouched
- [x] the green was EARNED, not gamed — adversarial refute-read: provably verbatim (git diff = the 4 def removals + the re-import); the §4 behavior test asserts real outputs (PHASE_OWNER mapping, section fill detection), and the 1854-suite exercises every CLI path that calls these predicates
- [x] concurrency / timing safe — pure functions (dict reads + a regex/string scan); no IO surface
- [x] no exposed secrets, injection openings, or unexpected dependencies — predicates.py imports re + PHASE_OWNER (constants) + _die (io_state); AST-confirmed
- [x] layering & dependencies follow CONVENTIONS.md — predicates → {constants, io_state} (one-way; no cycle); add.py → predicates the only new edge
- [x] a person reviewed and approved the change — Tin Dang, auto mode (standing directive; pure verbatim refactor, suite-gated)

### Build expectations — what "correct" looks like
- [x] all 4 `add.<name> is add_engine.predicates.<name>` True — §4 identity test green
- [x] _phase_owner maps every PHASE_OWNER entry; _section_unfilled detects filled vs empty — §4 behavior test green
- [x] package_digest == ENGINE_PKG_MD5 across 3 trees (incl. predicates.py); ENGINE_MD5 == md5(add.py) — §4 pin test green
- [x] engine_pin.py has no hashlib — confirmed
- [x] AST free-name scan of predicates.py clean — confirmed before suite (undefined: [])

### Deep checks — do not skim
- [x] WIRING (code) — add.py re-imports + bare-calls the 4; predicates.py imports re/PHASE_OWNER/_die; engine_manifest globs it into the pin
- [x] DEAD-CODE (code) — the 4 GONE from add.py (test_add_py_no_longer_defines_them green); no orphan banner (the 4 sat between _load_state_for_json and _stamp_gate_record, both stay)
- [x] SEMANTIC — n/a (code task)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-26   (auto mode — pure verbatim refactor; full suite 1854/0, seam audit clean 91, both pins re-aimed + 3-tree parity; AST scan clean upfront)
Reviewed by: Tin Dang · date: 2026-06-26

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): suite green count · ENGINE_PKG_MD5 stability

### Spec delta
- [SPEC · open] next = the identity cluster (own module + repoint identity-test patches) or a guideline-injection sub-slice (evidence: remaining regions are entangled)

### Competency deltas
- [ADD · folded] new module per cohesive concern keeps each extraction a clean leaf with a distinct dependency profile (evidence: accessors=import-free, predicates=re/const/io_state) [folded foundation-version 52]
