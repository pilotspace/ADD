# TASK: Extract changelog/release-render helpers (6 fns) to add_engine/release.py

slug: extract-release · created: 2026-06-26 · stage: mvp
autonomy: auto
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/add.py` — the changelog/RELEASES render cluster (6 SCATTERED fns, transitive-closure AST = closed, ZERO outbound to staying fns): `_releases_path`(5068) · `_closed_milestones`(5094) · `_key_decisions_for`(5150) · `_build_in_flight`(5283) · `_render_changelog_block`(5303) · `_render_releases_row`(5318). NONE patched, NONE rebound, NONE add.X in tests. Deps = `re`+`Path`(stdlib) + `RELEASES_FILE`(constants.py). NO private constants, NO cluster overlap.
  - `add-method/tooling/add_engine/release.py` — NEW: `import re` + `from pathlib import Path` + `from add_engine.constants import RELEASES_FILE` + the 6 fns verbatim.
  - `add-method/tooling/add.py` — remove the 6 fns; add `from add_engine.release import (the 6)`.
  - `add-method/tooling/engine_pin.py` — both pins re-aimed.
Context: engine package (11 modules → +release = 12); 3-tree mirror. The RELEASE-pillar render helpers (CHANGELOG block · RELEASES.md row · closed-milestone attribution). The release-report/`cmd_release` CALLERS stay (bare → add's re-imported global).
Honors: cluster-move recipe (re-export, NO qualification since unpatched; transitive-closure AST upfront).
Anchors: `add_engine/release.py` (NEW) · the 6 fns · add.py re-import · both pins.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: move the 6 changelog/RELEASES render helper fns from add.py into a NEW `add_engine/release.py`; add.py re-imports. Fourteenth extraction. Pure refactor; zero behavior change.
Framings weighed: the closed release-render cluster → release.py (chosen) · leave in add.py (rejected — closed unpatched cluster, a natural module for the RELEASE pillar)
  - chosen — transitive-closure AST proves closure; none patched → plain re-export; a cohesive concern (render the CHANGELOG block + RELEASES.md row + milestone attribution).
Must:
<must>
  - release.py defines the 6 fns (verbatim); add.py re-imports so `add.<name>` resolves to the release objects.
  - every release-render path (CHANGELOG block, RELEASES row, closed-milestone attribution, in-flight build) behaves identically; full suite passes unchanged.
  - both pins re-aimed (literals); 3-tree byte-identical.
</must>
Reject:
<reject>
  - a fn's output changes or `add.<name>` stops resolving -> "release_drift".
  - the pin recomputes itself -> "vacuous_pin"; a tree missing release.py -> "mirror_incomplete".
  - an import cycle (release↔add) -> "cycle" (release imports only constants + stdlib).
</reject>
After:
<after>
  - engine package gains release.py (12 modules); full suite ≥1928 green; both pins re-aimed.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ closure is complete (no hidden call to a staying add fn) — transitive-closure AST returned EMPTY outbound; the suite (every release path) names a miss. Cost: import the dep.
  - [ ] none patched/rebound; no private constants; deps = re/Path/RELEASES_FILE — confirmed.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the 6 fns moved but resolve unchanged
  Given they live in add_engine/release.py
  When a test imports add
  Then add._render_changelog_block / add._render_releases_row / add._closed_milestones / ... resolve AND are the add_engine.release objects

Scenario: release render is preserved
  Given the split engine
  When _render_releases_row / _render_changelog_block run with fixed inputs
  Then they return the same strings as before

Scenario: no cycle; release.py joins the pin, 3-tree consistent
  Then importing add_engine.release standalone needs no add; ENGINE_PKG_MD5 == package_digest (incl. release.py) across 3 trees; ENGINE_MD5 == md5(add.py); engine_pin.py no hashlib
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add_engine/release.py (NEW):
  from __future__ import annotations
  import re
  from pathlib import Path
  from add_engine.constants import RELEASES_FILE
  def _releases_path / _closed_milestones / _key_decisions_for /
      _build_in_flight / _render_changelog_block / _render_releases_row   # verbatim

add.py:
  from add_engine.release import (
      _releases_path, _closed_milestones, _key_decisions_for,
      _build_in_flight, _render_changelog_block, _render_releases_row,
  )   # the 6 defs removed; bare callers resolve add's global

engine_pin.py: ENGINE_MD5 + ENGINE_PKG_MD5 re-aimed (literals; never hashes).
Mirror: prepare_bundle -> _bundled; cp add.py+add_engine -> .add (no engine_pin.py in .add runtime).
```

Least-sure flag surfaced at freeze: [test] none material — closed (transitive-closure AST) + unpatched; the 1928-suite is the gate. Cost if wrong: import the dep.
Status: FROZEN @ v1 — approved by Tin Dang (auto mode; closed unpatched cluster, AST-closure-verified, suite-gated; the proven cluster recipe ×12)

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every scenario has one test; existing suite (≥1928) stays green.
Plan:
<test_plan>
  - test_release_reexported_same_object: all 6 resolve via add AND `is` the add_engine.release object.
  - test_render_preserved: _render_releases_row / _render_changelog_block return expected strings on fixed inputs.
  - test_no_import_cycle + test_pkg_digest_includes_release_3tree + test_pins_literal_and_md5 + test_add_py_no_longer_defines_them.
</test_plan>

Tests live in: `add-method/tooling/test_engine_extract_release.py` (DECLARED in §5; written in tests phase BEFORE the tests→build crossing) · MUST run red before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/add_engine/release.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_engine_extract_release.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add_engine/release.py`
Strategy: 1. (tests) write the new test red. 2. (build) create release.py (6 fns verbatim + imports); remove the 6 from add.py; add the re-import. 3. AST undefined-name scan. 4. re-aim both pins. 5. prepare_bundle → _bundled; cp → .add. 6. full suite green.
Safety rule: zero behavior change; engine_pin.py never hashes; no cycle; transitive-closure AST scan before suite.
Code lives in: `add-method/tooling/`
Constraints: do NOT change any test or the contract; stdlib + constants only.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all tests pass
- [ ] coverage did not decrease
- [ ] no assertion was weakened
- [ ] the green was EARNED, not gamed — adversarial refute-read; a confirmed cheat is HARD-STOP
- [ ] concurrency / timing safe (pure string formatting + file reads)
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like
- [ ] all 6 `add.<name> is add_engine.release.<name>` — §4
- [ ] release render outputs unchanged — §4
- [ ] no import cycle — §4
- [ ] package_digest == ENGINE_PKG_MD5 across 3 trees (incl. release.py); ENGINE_MD5 == md5(add.py); engine_pin.py no hashlib

### Deep checks — do not skim
- [ ] WIRING — add.py re-imports the 6; release.py imports constants/stdlib; engine_manifest globs it
- [ ] DEAD-CODE — the 6 GONE from add.py; no orphan
- [ ] SEMANTIC — n/a (code task)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-26

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch: release-report / cmd_release render · ENGINE_PKG_MD5 stability

### Spec delta
- [SPEC · open] next closed clusters (probe-confirmed 2026-06-26): task-doc parsing (`_task_header`·`_task_prose`·`_count_test_defs`·`_declared_test_files`·`_primary_test_files`·`_declared_tests_count`·`_tests_count`·`_tests_info`·`_raw_phase_bodies`·`_phase_spans`·`_spec_delta_entries`; owns shared `_task_header`) → THEN autonomy (`_autonomy_level`·`_effective_autonomy`·`_project_autonomy`·`_project_autonomy_token`; imports `_task_header` from taskdoc). THEN the orchestrator spine stays as add.py (evidence: closure probe)

### Competency deltas
- [ADD · open] the RELEASE-pillar render helpers form their own closed module (release.py) distinct from the milestone-doc readers (milestones.py) — scope-level concerns (RELEASE vs MILESTONE) map to separate modules even when both read ledgers (evidence: release.py vs milestones.py)
