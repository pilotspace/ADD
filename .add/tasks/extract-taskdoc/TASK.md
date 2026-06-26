# TASK: Extract TASK.md structural readers (11 fns) to add_engine/taskdoc.py + relocate 3 shared delta regexes to constants.py

slug: extract-taskdoc · created: 2026-06-26 · stage: mvp
autonomy: auto
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/add.py` — the TASK.md structural-reader cluster (11 SCATTERED fns, transitive-closure AST = closed, ZERO outbound): `_task_header`(711) · `_count_test_defs`(3112) · `_primary_test_files`(3121) · `_tests_count`(3130) · `_declared_test_files`(3134) · `_declared_tests_count`(3174) · `_tests_info`(3179) · `_task_prose`(3592) · `_phase_spans`(3734) · `_raw_phase_bodies`(3761) · `_spec_delta_entries`(4527). NONE patched/rebound (the 3 `add.X` test refs are plain calls). Deps: `re`+`Path`(stdlib) + `_confined`(components module, re-imported) + 3 SHARED regexes.
  - ⚠ 3 SHARED delta regexes used by the cluster (`_task_prose`@3609-3613, `_spec_delta_entries`) AND the STAYING deltas web (`_lint_task_deltas`/`_collect_open_spec_deltas`/`_resolve_spec_delta` @4504-4682): `_DELTA_RE`(4357-4359) · `_EVIDENCE_RE`(4360) · `_SPEC_DELTA_RE`(4369-4371). CONSTANT-BY-KIND shared rule → relocate to constants.py (single source) + add to add.py's `_`-import. The interleaved `_SPEC_STATUSES`(4365)·`_STATUS_SETS`(4373)·`_TAG_BROAD_RE`(4377) STAY (deltas-web only) — move ONLY the 3 regex Assign nodes, surgically.
  - `add-method/tooling/add_engine/constants.py` — add `import re`; append `_DELTA_RE`/`_EVIDENCE_RE`/`_SPEC_DELTA_RE` (verbatim, `_`-prefixed, NOT in __all__).
  - `add-method/tooling/add_engine/taskdoc.py` — NEW: `import re` + `from pathlib import Path` + `from add_engine.constants import _DELTA_RE, _EVIDENCE_RE, _SPEC_DELTA_RE` + `from add_engine.components import _confined` + the 11 fns verbatim.
  - `add-method/tooling/add.py` — remove the 11 fns + the 3 regex defs; add taskdoc re-import + the 3 regexes to the `_`-constants import.
  - `add-method/tooling/engine_pin.py` — both pins re-aimed.
Context: engine package (12 modules → +taskdoc = 13); 3-tree mirror. The TASK.md/structure readers (header · prose · test-count · phase-span · §7 delta entries). Callers (status/report/verify/next-pair) stay (bare → add's re-imported global).
Honors: cluster-move recipe (re-export, NO qualification — unpatched); CONSTANT-BY-KIND (3 SHARED regexes → constants.py single source); a cross-module helper `_confined` imported from components.
Anchors: `add_engine/taskdoc.py` (NEW) · 11 fns · 3 regexes→constants.py · add.py re-import + `_`-import grows · both pins.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: move the 11 TASK.md structural-reader fns from add.py into a NEW `add_engine/taskdoc.py`; relocate the 3 SHARED delta regexes to constants.py; add.py re-imports. Fifteenth extraction. Pure refactor; zero behavior change.
Framings weighed: whole closed cluster → taskdoc.py + shared regexes → constants.py (chosen) · split `_spec_delta_entries` out (rejected — it's pulled into the closure transitively; can't cleanly separate)
  - chosen — transitive-closure AST proves closure; none patched → plain re-export; the 3 regexes are shared (cluster + staying deltas web) so constants.py is their single source.
Must:
<must>
  - taskdoc.py defines the 11 fns (verbatim); constants.py defines the 3 regexes; add.py re-imports the 11 so `add.<name>` resolves to the taskdoc objects; the 3 regexes resolve in add.py (staying deltas web unchanged) AND in taskdoc.py.
  - every TASK.md-read path (test-count, phase-span, prose, §7 delta entries) + the staying deltas-web lint behave identically; full suite passes unchanged.
  - both pins re-aimed (literals); 3-tree byte-identical.
</must>
Reject:
<reject>
  - a fn's output changes, `add.<name>` stops resolving, or a regex stops resolving in the staying lint -> "taskdoc_drift".
  - the pin recomputes itself -> "vacuous_pin"; a tree missing taskdoc.py -> "mirror_incomplete".
  - an import cycle -> "cycle" (taskdoc imports constants + components + stdlib only; constants imports stdlib only).
</reject>
After:
<after>
  - engine package gains taskdoc.py (13 modules); full suite ≥1938 green; both pins re-aimed.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ relocating the 3 shared regexes to constants.py keeps BOTH the moved readers AND the staying deltas-web lint resolving them — add.py imports them via the explicit `_`-import at the top (before the staying lint defs eval); taskdoc imports them directly; the suite (every delta path) names a miss. Cost: fix the import.
  ⚠ removing ONLY the 3 regex Assign nodes leaves `_SPEC_STATUSES`/`_STATUS_SETS`/`_TAG_BROAD_RE` intact — done via precise AST lineno ranges, not text munging. Cost: restore an over-deleted line.
  - [ ] closed (transitive-closure AST) + unpatched + `_confined` from components — confirmed.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the 11 fns moved but resolve unchanged
  Given they live in add_engine/taskdoc.py
  When a test imports add
  Then add._task_prose / add._tests_info / add._phase_spans / add._spec_delta_entries / ... resolve AND are the add_engine.taskdoc objects

Scenario: the 3 shared regexes relocate, both sides still resolve
  Given _DELTA_RE/_EVIDENCE_RE/_SPEC_DELTA_RE live in constants.py
  When the staying deltas-web lint AND the moved _spec_delta_entries run
  Then both resolve the regexes and parse identically; add._DELTA_RE resolves

Scenario: reads preserved + no cycle + 3-tree pins
  When _tests_count / _phase_spans run against a real TASK.md
  Then they return the same values as before
  And importing add_engine.taskdoc standalone needs no add; ENGINE_PKG_MD5 == package_digest (incl. taskdoc.py) across 3 trees; ENGINE_MD5 == md5(add.py); engine_pin.py no hashlib
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add_engine/constants.py:
  import re                                # + (new)
  _DELTA_RE = re.compile(...)              # appended verbatim (shared: taskdoc + deltas web)
  _EVIDENCE_RE = re.compile(...)
  _SPEC_DELTA_RE = re.compile(...)

add_engine/taskdoc.py (NEW):
  from __future__ import annotations
  import re
  from pathlib import Path
  from add_engine.constants import _DELTA_RE, _EVIDENCE_RE, _SPEC_DELTA_RE
  from add_engine.components import _confined
  def _task_header / _count_test_defs / _primary_test_files / _tests_count /
      _declared_test_files / _declared_tests_count / _tests_info / _task_prose /
      _phase_spans / _raw_phase_bodies / _spec_delta_entries          # verbatim

add.py:
  from add_engine.constants import ( ..., _DELTA_RE, _EVIDENCE_RE, _SPEC_DELTA_RE )   # add to the _-import
  from add_engine.taskdoc import (the 11)                                            # new re-import
  # the 11 defs + the 3 regex Assigns removed; _SPEC_STATUSES/_STATUS_SETS/_TAG_BROAD_RE KEPT

engine_pin.py: ENGINE_MD5 + ENGINE_PKG_MD5 re-aimed (literals; never hashes).
Mirror: prepare_bundle -> _bundled; cp add.py+add_engine -> .add (no engine_pin.py in .add runtime).
```

Least-sure flag surfaced at freeze: [test] the 3 shared regexes must resolve in BOTH the staying lint and taskdoc; add.py imports them at the top. The 1938-suite (every delta path) is the gate. Cost if wrong: fix the import.
Status: FROZEN @ v1 — approved by Tin Dang (auto mode; closed unpatched cluster, AST-closure-verified, CONSTANT-BY-KIND for the shared regexes, suite-gated; the proven cluster+shared-const recipe)

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every scenario has one test; existing suite (≥1938) stays green.
Plan:
<test_plan>
  - test_taskdoc_reexported_same_object: all 11 resolve via add AND `is` the add_engine.taskdoc object.
  - test_shared_regexes_relocated: add_engine.constants._DELTA_RE/_EVIDENCE_RE/_SPEC_DELTA_RE exist AND add._DELTA_RE resolves (staying lint side).
  - test_no_import_cycle + test_pkg_digest_includes_taskdoc_3tree + test_pins_literal_and_md5 + test_add_py_no_longer_defines_them.
</test_plan>

Tests live in: `add-method/tooling/test_engine_extract_taskdoc.py` (DECLARED in §5; written in tests phase BEFORE the tests→build crossing) · MUST run red before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/add_engine/taskdoc.py` `add-method/tooling/add_engine/constants.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_engine_extract_taskdoc.py` `add-method/tooling/test_delta_grammar_dedup.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add_engine/taskdoc.py` `add-method/src/add_method/_bundled/tooling/add_engine/constants.py`
NOTE (scope widened mid-build, re-anchored): the relocation of `_DELTA_RE`/`_SPEC_DELTA_RE` from add.py to constants.py (forced — taskdoc's `_task_prose`/`_spec_delta_entries` import them; can't stay in add.py without a cycle) stales `test_delta_grammar_dedup.py`'s `_add_source()`, which scans ONLY add.py for the single enumerated grammar. The DRY invariant (`== 1` compilation) is UNCHANGED and still holds — in constants.py. Faithfulness-preserving fix: widen `_add_source()` to scan the whole engine (add.py + add_engine/*.py) so the canonical-source-count invariant measures the engine, not just add.py. The `== 1` assertion is NOT weakened (a duplicate would still fail). Same class as repointing a moved patch target. Docstring CONTRACT updated to name constants.py as the new home.
Strategy: 1. (tests) write the new test red. 2. (build) add `import re` + the 3 regexes to constants.py; create taskdoc.py (11 fns verbatim + imports); remove the 11 fns + the 3 regex Assigns from add.py (precise AST ranges; KEEP _SPEC_STATUSES/_STATUS_SETS/_TAG_BROAD_RE); add the taskdoc re-import + the 3 regexes to the `_`-constants import. 3. AST undefined-name scan of taskdoc + a grep that add.py still resolves the 3 regexes. 4. re-aim both pins. 5. prepare_bundle → _bundled; cp → .add. 6. full suite green.
Safety rule: zero behavior change; move ONLY the 3 regex Assigns (not the sibling delta constants); engine_pin.py never hashes; no cycle.
Code lives in: `add-method/tooling/`
Constraints: do NOT change any test or the contract; stdlib + constants + components only.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all tests pass
- [ ] coverage did not decrease
- [ ] no assertion was weakened
- [ ] the green was EARNED, not gamed — adversarial refute-read; a confirmed cheat is HARD-STOP
- [ ] concurrency / timing safe (pure file reads + regex)
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like
- [ ] all 11 `add.<name> is add_engine.taskdoc.<name>` — §4
- [ ] the 3 regexes in constants.py; add._DELTA_RE resolves (staying lint) — §4
- [ ] _SPEC_STATUSES/_STATUS_SETS/_TAG_BROAD_RE still defined in add.py
- [ ] reads preserved; no import cycle — §4
- [ ] package_digest == ENGINE_PKG_MD5 across 3 trees (incl. taskdoc.py + grown constants.py); ENGINE_MD5 == md5(add.py); engine_pin.py no hashlib

### Deep checks — do not skim
- [ ] WIRING — add.py re-imports the 11 + the 3 regexes; taskdoc imports constants/components/stdlib; engine_manifest globs it
- [ ] DEAD-CODE — the 11 + the 3 regex Assigns GONE from add.py; the sibling delta consts intact; no orphan
- [ ] SEMANTIC — n/a (code task)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-26

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch: TASK.md-read + deltas-web lint paths · ENGINE_PKG_MD5 stability

### Spec delta
- [SPEC · dropped] next + last closed cluster: autonomy (`_autonomy_level`·`_effective_autonomy`·`_project_autonomy`·`_project_autonomy_token`) — imports `_task_header` from taskdoc. THEN the orchestrator spine (load_state/save_state/report_data/_decide_next_pair/_collect_open_deltas/cmd_*/main) STAYS as the add.py entry module (evidence: closure probe 2026-06-26)

### Competency deltas
- [ADD · folded] a SHARED constant interleaved with same-concern siblings is relocated by precise AST Assign-node ranges (move ONLY the shared names), leaving the siblings — text-region deletion would over-capture the interleaved keepers (evidence: 3 delta regexes among _SPEC_STATUSES/_STATUS_SETS/_TAG_BROAD_RE) [folded foundation-version 52]
