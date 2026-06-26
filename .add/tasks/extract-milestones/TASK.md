# TASK: Extract milestone-doc readers (7 fns) to add_engine/milestones.py

slug: extract-milestones · created: 2026-06-26 · stage: mvp
autonomy: auto
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/add.py` — the milestone-doc reader cluster (7 fns, transitive-closure AST = closed, ZERO outbound): `_has_production_roadmap`(1105, scattered) · `_project_goal`(3056) · `_milestone_doc`(3092) · `_exit_criteria`(3107) · `_exit_criteria_cited`(3126) · `_stage_criteria`(3156) · `_all_milestones_done`(3174). + cluster-PRIVATE `_VERIFY_CITE_RE`(3123, used ONLY @3142 in _exit_criteria_cited). NONE patched, NONE add.X in tests. Imports needed: `re`+`Path`(stdlib) + `GOAL_UNSET`+`MILESTONE_FILE`(constants.py) + `_VERIFY_CITE_RE`(travels). Nothing unaccounted.
  - `add-method/tooling/add_engine/milestones.py` — NEW: stdlib + `from add_engine.constants import GOAL_UNSET, MILESTONE_FILE` + local `_VERIFY_CITE_RE` + the 7 fns verbatim.
  - `add-method/tooling/add.py` — remove the 7 fns + `_VERIFY_CITE_RE`; add `from add_engine.milestones import (the 7)`.
  - `add-method/tooling/engine_pin.py` — both pins re-aimed.
Context: engine package (8 modules → +milestones = 9); 3-tree mirror. A clean closed cluster (MILESTONE.md/state goal+exit-criteria readers); callers (cmd_status/report/graduate) stay (bare → add's re-imported global).
Honors: cluster-move recipe (re-export, NO qualification since unpatched; transitive-closure AST upfront); cluster-private const travels.
Anchors: `add_engine/milestones.py` (NEW) · the 7 fns + `_VERIFY_CITE_RE` · add.py re-import · both pins.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: move the 7 milestone/state goal+exit-criteria reader fns (+ private `_VERIFY_CITE_RE`) from add.py into a NEW `add_engine/milestones.py`; add.py re-imports. Tenth extraction. Pure refactor; zero behavior change.
Framings weighed: the closed milestone-doc cluster → milestones.py (chosen) · leave in add.py (rejected — closed unpatched cluster, a natural module)
  - chosen — transitive-closure AST proves closure; none patched → plain re-export; a cohesive concern (read MILESTONE.md goal / exit-criteria / stage-criteria / all-done).
Must:
<must>
  - milestones.py defines the 7 fns + `_VERIFY_CITE_RE` (verbatim); add.py re-imports so `add.<name>` resolves to the milestones objects.
  - every milestone/graduation/report path (exit-criteria counts, goal display, all-milestones-done) behaves identically; full suite passes unchanged.
  - both pins re-aimed (literals); 3-tree byte-identical.
</must>
Reject:
<reject>
  - a fn's output changes or `add.<name>` stops resolving -> "milestone_drift".
  - the pin recomputes itself -> "vacuous_pin"; a tree missing milestones.py -> "mirror_incomplete".
  - an import cycle (milestones↔add) -> "cycle" (milestones imports only constants + stdlib).
</reject>
After:
<after>
  - engine package gains milestones.py (9 modules); full suite ≥1893 green; both pins re-aimed.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ closure is complete (no hidden call to a kept add fn) — transitive-closure AST returned EMPTY outbound; if wrong the suite (every milestone/graduation path) names it. Cost: import the dep.
  - [ ] none patched; `_VERIFY_CITE_RE` private (only _exit_criteria_cited) — confirmed.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the 7 fns moved but resolve unchanged
  Given they live in add_engine/milestones.py
  When a test imports add
  Then add._project_goal / add._exit_criteria / add._all_milestones_done / ... resolve AND are the add_engine.milestones objects

Scenario: milestone reads are preserved
  Given the split engine
  When _exit_criteria / _exit_criteria_cited / _project_goal run against a real milestone
  Then they return the same counts/goal as before

Scenario: no cycle; milestones.py joins the pin, 3-tree consistent
  Then importing add_engine.milestones standalone needs no add; ENGINE_PKG_MD5 == package_digest (incl. milestones.py) across 3 trees; ENGINE_MD5 == md5(add.py); engine_pin.py no hashlib
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add_engine/milestones.py (NEW):
  from __future__ import annotations
  import re
  from pathlib import Path
  from add_engine.constants import GOAL_UNSET, MILESTONE_FILE
  _VERIFY_CITE_RE = re.compile(r"\(verify:\s*\S.*?\)", re.I)   # cluster-private (moved verbatim)
  def _has_production_roadmap / _project_goal / _milestone_doc / _exit_criteria /
      _exit_criteria_cited / _stage_criteria / _all_milestones_done   # verbatim

add.py:
  from add_engine.milestones import (
      _has_production_roadmap, _project_goal, _milestone_doc, _exit_criteria,
      _exit_criteria_cited, _stage_criteria, _all_milestones_done,
  )   # the 7 defs + _VERIFY_CITE_RE removed; bare callers resolve add's global

engine_pin.py: ENGINE_MD5 + ENGINE_PKG_MD5 re-aimed (literals; never hashes).
Mirror: prepare_bundle -> _bundled; cp add.py+add_engine -> .add (no engine_pin.py in .add runtime).
```

Least-sure flag surfaced at freeze: [test] none material — closed (transitive-closure AST) + unpatched; the 1893-suite is the gate. Cost if wrong: import the dep.
Status: FROZEN @ v1 — approved by Tin Dang (auto mode; closed unpatched cluster, AST-closure-verified, suite-gated; the proven cluster recipe ×9)

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every scenario has one test; existing suite (≥1893) stays green.
Plan:
<test_plan>
  - test_milestones_reexported_same_object: all 7 resolve via add AND `is` the add_engine.milestones object.
  - test_exit_criteria_preserved: a real milestone's exit-criteria counts/goal unchanged.
  - test_no_import_cycle + test_pkg_digest_includes_milestones_3tree + test_pins_literal_and_md5 + test_add_py_no_longer_defines_them.
</test_plan>

Tests live in: `add-method/tooling/test_engine_extract_milestones.py` (DECLARED in §5; written in tests phase BEFORE the tests→build crossing) · MUST run red before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/add_engine/milestones.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_engine_extract_milestones.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add_engine/milestones.py`
Strategy: 1. (tests) write the new test red. 2. (build) create milestones.py (7 fns + `_VERIFY_CITE_RE` verbatim + imports); remove the 7 + `_VERIFY_CITE_RE` from add.py; add the re-import. 3. AST undefined-name scan. 4. re-aim both pins. 5. prepare_bundle → _bundled; cp → .add. 6. full suite green.
Safety rule: zero behavior change; engine_pin.py never hashes; no cycle; transitive-closure AST scan before suite.
Code lives in: `add-method/tooling/`
Constraints: do NOT change any test or the contract; stdlib + constants only.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all tests pass
- [ ] coverage did not decrease
- [ ] no assertion was weakened
- [ ] the green was EARNED, not gamed — adversarial refute-read; a confirmed cheat is HARD-STOP
- [ ] concurrency / timing safe (pure file reads)
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like
- [ ] all 7 `add.<name> is add_engine.milestones.<name>` — §4
- [ ] exit-criteria counts / goal unchanged — §4
- [ ] no import cycle — §4
- [ ] package_digest == ENGINE_PKG_MD5 across 3 trees (incl. milestones.py); ENGINE_MD5 == md5(add.py); engine_pin.py no hashlib

### Deep checks — do not skim
- [ ] WIRING — add.py re-imports the 7; milestones.py imports constants/stdlib; engine_manifest globs it
- [ ] DEAD-CODE — the 7 + _VERIFY_CITE_RE GONE from add.py; no orphan
- [ ] SEMANTIC — n/a (code task)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-26

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch: milestone/graduation/report paths · ENGINE_PKG_MD5 stability

### Spec delta
- [SPEC · open] next clean clusters: md5 (trivial) · components (tomllib-guard care) · version-update (_fetch_latest_version PATCHED) · deltas (7 shared constants → constants.py) · release/changelog; THEN cmd_*/save/load/main core (evidence: per-cluster coupling map in memory)

### Competency deltas
- [ADD · open] a scattered cluster member (e.g. _has_production_roadmap far from the rest) extracts fine — AST line-range capture handles non-contiguity (evidence: this cluster spanned 1105 + 3056-3174)
