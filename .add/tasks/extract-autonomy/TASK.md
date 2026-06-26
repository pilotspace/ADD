# TASK: Extract autonomy-level resolvers (4 fns) to add_engine/autonomy.py + relocate shared _AUTONOMY_LEVELS to constants.py

slug: extract-autonomy · created: 2026-06-26 · stage: mvp
autonomy: auto
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/add.py` — the autonomy-level resolver cluster (4 fns, transitive-closure AST = closed, ZERO outbound): `_autonomy_level`(700-710) · `_effective_autonomy`(719-726, calls `_task_header` now in taskdoc) · `_project_autonomy_token`(3069-3078) · `_project_autonomy`(3081-3087). NONE patched/rebound. Deps: `re`+`Path`(stdlib) + `_task_header`(taskdoc module, re-imported) + `_AUTONOMY_LINE_RE`(private) + `_AUTONOMY_LEVELS`(shared).
  - `_AUTONOMY_LINE_RE`(689) — cluster-PRIVATE (used ONLY @706 in `_autonomy_level`) → travels INTO autonomy.py.
  - `_AUTONOMY_LEVELS`(684) — SHARED: the cluster (700/710/726) AND staying code (`_AUTONOMY_ORDER`@837, cmd_autonomy render @870/885/887) → relocate to constants.py (single source) + add to add.py's `_`-import.
  - `add-method/tooling/add_engine/constants.py` — append `_AUTONOMY_LEVELS` (verbatim, `_`-prefixed, NOT in __all__).
  - `add-method/tooling/add_engine/autonomy.py` — NEW: `import re` + `from pathlib import Path` + `from add_engine.constants import _AUTONOMY_LEVELS` + `from add_engine.taskdoc import _task_header` + local `_AUTONOMY_LINE_RE` + the 4 fns verbatim.
  - `add-method/tooling/add.py` — remove the 4 fns + `_AUTONOMY_LINE_RE` + `_AUTONOMY_LEVELS`; add autonomy re-import + `_AUTONOMY_LEVELS` to the `_`-constants import.
  - `add-method/tooling/engine_pin.py` — both pins re-aimed.
Context: engine package (13 modules → +autonomy = 14, the LAST clean cluster); 3-tree mirror. The autonomy-level read/resolve (declared vs effective vs project-default). Callers (run-gate, cmd_autonomy, render) stay (bare → add's re-imported global).
Honors: cluster-move recipe (re-export, NO qualification — unpatched); CONSTANT-BY-KIND (shared `_AUTONOMY_LEVELS` → constants.py; private `_AUTONOMY_LINE_RE` travels); cross-module `_task_header` from taskdoc.
Anchors: `add_engine/autonomy.py` (NEW) · 4 fns + `_AUTONOMY_LINE_RE` · `_AUTONOMY_LEVELS`→constants · add.py re-import + `_`-import grows · both pins.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: move the 4 autonomy-level resolver fns (+ private `_AUTONOMY_LINE_RE`) from add.py into a NEW `add_engine/autonomy.py`; relocate the shared `_AUTONOMY_LEVELS` to constants.py; add.py re-imports. Sixteenth (last clean) extraction. Pure refactor; zero behavior change.
Framings weighed: whole closed cluster → autonomy.py + shared tuple → constants.py (chosen) · leave in add.py (rejected — closed unpatched cluster, a natural module)
  - chosen — transitive-closure AST proves closure; none patched → plain re-export; `_AUTONOMY_LEVELS` is shared so constants.py is its single source; `_AUTONOMY_LINE_RE` private so it travels.
Must:
<must>
  - autonomy.py defines the 4 fns + `_AUTONOMY_LINE_RE` (verbatim); constants.py defines `_AUTONOMY_LEVELS`; add.py re-imports the 4 so `add.<name>` resolves to the autonomy objects; `_AUTONOMY_LEVELS` resolves in add.py (staying _AUTONOMY_ORDER + cmd_autonomy unchanged) AND in autonomy.py.
  - every autonomy path (declared-level read, effective-level resolve, project default, `autonomy set/show`) behaves identically; full suite passes unchanged.
  - both pins re-aimed (literals); 3-tree byte-identical.
</must>
Reject:
<reject>
  - a fn's behavior changes, `add.<name>` stops resolving, or `_AUTONOMY_LEVELS` stops resolving in the staying code -> "autonomy_drift".
  - the pin recomputes itself -> "vacuous_pin"; a tree missing autonomy.py -> "mirror_incomplete".
  - an import cycle -> "cycle" (autonomy → taskdoc → {constants, components} → stdlib; one-way).
</reject>
After:
<after>
  - engine package gains autonomy.py (14 modules); full suite ≥1948 green; both pins re-aimed.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ relocating `_AUTONOMY_LEVELS` to constants.py keeps BOTH the moved resolvers AND the staying `_AUTONOMY_ORDER`/cmd_autonomy resolving it — add.py imports it via the `_`-import at the top (before `_AUTONOMY_ORDER`@837 eval); autonomy.py imports it directly; the suite (every autonomy path) names a miss. Cost: fix the import.
  - [ ] closed (transitive-closure AST) + unpatched + `_task_header` from taskdoc + `_AUTONOMY_LINE_RE` private — confirmed.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the 4 fns moved but resolve unchanged
  Given they live in add_engine/autonomy.py
  When a test imports add
  Then add._autonomy_level / add._effective_autonomy / add._project_autonomy / add._project_autonomy_token resolve AND are the add_engine.autonomy objects

Scenario: _AUTONOMY_LEVELS relocates, both sides still resolve
  Given _AUTONOMY_LEVELS lives in constants.py
  When the staying _AUTONOMY_ORDER / cmd_autonomy AND the moved _autonomy_level run
  Then both resolve the tuple; add._AUTONOMY_LEVELS == ("manual","conservative","auto")

Scenario: autonomy resolve preserved + no cycle + 3-tree pins
  When _autonomy_level("autonomy: conservative") and _effective_autonomy on a real task
  Then they return the same levels as before
  And importing add_engine.autonomy standalone needs no add; ENGINE_PKG_MD5 == package_digest (incl. autonomy.py) across 3 trees; ENGINE_MD5 == md5(add.py); engine_pin.py no hashlib
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add_engine/constants.py:
  _AUTONOMY_LEVELS = ("manual", "conservative", "auto")   # appended verbatim (shared)

add_engine/autonomy.py (NEW):
  from __future__ import annotations
  import re
  from pathlib import Path
  from add_engine.constants import _AUTONOMY_LEVELS
  from add_engine.taskdoc import _task_header
  _AUTONOMY_LINE_RE = re.compile(r"(?:^|·)[ \t]*autonomy:[ \t]*([^\s<#|]+)", re.MULTILINE)  # private
  def _autonomy_level / _effective_autonomy / _project_autonomy_token / _project_autonomy   # verbatim

add.py:
  from add_engine.constants import ( ..., _AUTONOMY_LEVELS )   # add to the _-import
  from add_engine.autonomy import (
      _autonomy_level, _effective_autonomy, _project_autonomy, _project_autonomy_token,
  )   # the 4 defs + _AUTONOMY_LINE_RE + _AUTONOMY_LEVELS removed; _AUTONOMY_ORDER + cmd_autonomy stay

engine_pin.py: ENGINE_MD5 + ENGINE_PKG_MD5 re-aimed (literals; never hashes).
Mirror: prepare_bundle -> _bundled; cp add.py+add_engine -> .add (no engine_pin.py in .add runtime).
```

Least-sure flag surfaced at freeze: [test] `_AUTONOMY_LEVELS` must resolve in BOTH the staying _AUTONOMY_ORDER/cmd_autonomy and autonomy.py; add.py imports it at the top. The 1948-suite (every autonomy path) is the gate. Cost if wrong: fix the import.
Status: FROZEN @ v1 — approved by Tin Dang (auto mode; closed unpatched cluster, AST-closure-verified, CONSTANT-BY-KIND, suite-gated; the proven cluster+shared-const recipe; the LAST clean cluster)

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every scenario has one test; existing suite (≥1948) stays green.
Plan:
<test_plan>
  - test_autonomy_reexported_same_object: all 4 resolve via add AND `is` the add_engine.autonomy object.
  - test_levels_relocated: add_engine.constants._AUTONOMY_LEVELS == ("manual","conservative","auto") AND add._AUTONOMY_LEVELS resolves (staying side).
  - test_autonomy_level_preserved: _autonomy_level on a header line returns the declared token.
  - test_no_import_cycle + test_pkg_digest_includes_autonomy_3tree + test_pins_literal_and_md5 + test_add_py_no_longer_defines_them.
</test_plan>

Tests live in: `add-method/tooling/test_engine_extract_autonomy.py` (DECLARED in §5; written in tests phase BEFORE the tests→build crossing) · MUST run red before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/add_engine/autonomy.py` `add-method/tooling/add_engine/constants.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_engine_extract_autonomy.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add_engine/autonomy.py` `add-method/src/add_method/_bundled/tooling/add_engine/constants.py`
Strategy: 1. (tests) write the new test red. 2. (build) append `_AUTONOMY_LEVELS` to constants.py; create autonomy.py (4 fns + `_AUTONOMY_LINE_RE` verbatim + imports); remove the 4 fns + `_AUTONOMY_LINE_RE` + `_AUTONOMY_LEVELS` from add.py (precise AST ranges; KEEP `_AUTONOMY_ORDER` + cmd_autonomy); add the autonomy re-import + `_AUTONOMY_LEVELS` to the `_`-constants import. 3. AST undefined-name scan + grep that add.py still resolves `_AUTONOMY_LEVELS`. 4. re-aim both pins. 5. prepare_bundle → _bundled; cp → .add. 6. full suite green.
Safety rule: zero behavior change; move ONLY `_AUTONOMY_LINE_RE`+`_AUTONOMY_LEVELS` (keep `_AUTONOMY_ORDER`); engine_pin.py never hashes; no cycle.
Code lives in: `add-method/tooling/`
Constraints: do NOT change any test or the contract; stdlib + constants + taskdoc only.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all tests pass
- [ ] coverage did not decrease
- [ ] no assertion was weakened
- [ ] the green was EARNED, not gamed — adversarial refute-read; a confirmed cheat is HARD-STOP
- [ ] concurrency / timing safe (pure header read + regex)
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like
- [ ] all 4 `add.<name> is add_engine.autonomy.<name>` — §4
- [ ] `_AUTONOMY_LEVELS` in constants.py; add._AUTONOMY_LEVELS resolves (staying side) — §4
- [ ] `_AUTONOMY_ORDER` still defined in add.py; cmd_autonomy unchanged
- [ ] autonomy resolve preserved; no import cycle — §4
- [ ] package_digest == ENGINE_PKG_MD5 across 3 trees (incl. autonomy.py + grown constants.py); ENGINE_MD5 == md5(add.py); engine_pin.py no hashlib

### Deep checks — do not skim
- [ ] WIRING — add.py re-imports the 4 + `_AUTONOMY_LEVELS`; autonomy imports constants/taskdoc/stdlib; engine_manifest globs it
- [ ] DEAD-CODE — the 4 + `_AUTONOMY_LINE_RE` + `_AUTONOMY_LEVELS` GONE from add.py; `_AUTONOMY_ORDER` intact; no orphan
- [ ] SEMANTIC — n/a (code task)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-26

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch: autonomy read/resolve + cmd_autonomy paths · ENGINE_PKG_MD5 stability

### Spec delta
- [SPEC · dropped] autonomy was the LAST clean closed cluster. The residual add.py is the orchestrator SPINE (load_state/save_state/report_data/_decide_next_pair/_collect_open_deltas/cmd_* dispatch/main) — a connected web around load_state; it STAYS as the entry/orchestrator module (you don't dissolve the entry point). engine-modularization extraction phase COMPLETE at 14 modules, add.py 7049→~5600 (evidence: closure probe 2026-06-26 — no further closed clusters)

### Competency deltas
- [ADD · folded] the modularization terminates when the residual is a single connected web around the central state I/O (load_state/save_state/report_data) — that spine IS the entry module; extracting further would require qualifying its mutual recursion, not a re-export (evidence: the deltas/cmd_* closure = 31 fns around load_state) [folded foundation-version 52]
