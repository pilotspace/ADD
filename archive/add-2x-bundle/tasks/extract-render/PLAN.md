# TASK: Extract terminal-render primitives (8 fns) to add_engine/render.py

slug: extract-render · created: 2026-06-26 · stage: mvp
autonomy: auto
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/add.py` — the terminal-render primitive cluster (8 SCATTERED fns, transitive-closure AST = closed, ZERO outbound calls): `_bar`(3055) · `_phase_track`(3062) · `_use_ascii`(3080) · `_color_enabled`(3086) · `_term_width`(3092) · `_colorize`(3100) · `_clip`(3907) · `_wrap`(3912). NONE patched, NONE referenced as `add.X` in tests. Deps: `PHASES`(constants.py) + `_DEFAULT_WIDTH`+`_ANSI`(add.py constants) + os/re/shutil/sys (stdlib).
  - `_ANSI`(3051): render-PRIVATE (only `_colorize` uses it) → moves INTO render.py.
  - `_DEFAULT_WIDTH`(3044): SHARED — used by the render cluster AND staying fns (render_report sigs, cmd_*) as a default-arg value → moves to constants.py (single source; add to its `_`-prefixed explicit import in add.py so the staying default-args still resolve).
  - `add-method/tooling/add_engine/render.py` — NEW: stdlib + `from add_engine.constants import PHASES, _DEFAULT_WIDTH` + local `_ANSI` + the 8 fns verbatim.
  - `add-method/tooling/add_engine/constants.py` — gains `_DEFAULT_WIDTH = 72`.
  - `add-method/tooling/add.py` — remove the 8 fns + `_ANSI` + `_DEFAULT_WIDTH`; add `from add_engine.render import (the 8)` + add `_DEFAULT_WIDTH` to the constants `_`-import.
  - `add-method/tooling/engine_pin.py` — both pins re-aimed.
Context (working folder): engine package (7 modules → +render = 8); 3-tree mirror. A clean closed cluster (terminal rendering); the render_report/dashboard CALLERS stay (bare → add's re-imported global).
Honors: cluster-move recipe (re-export, NO qualification since unpatched; transitive-closure AST upfront); render-private const travels with the cluster; a SHARED const goes to constants.py (single source).
Anchors: `add_engine/render.py` (NEW) · the 8 fns + `_ANSI` · `_DEFAULT_WIDTH`→constants · add.py re-import · both pins.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: move the 8 terminal-render primitives (+ render-private `_ANSI`) from add.py into a NEW `add_engine/render.py`; relocate the SHARED `_DEFAULT_WIDTH` to constants.py; add.py re-imports. Ninth extraction. Pure refactor; zero behavior change.
Framings weighed: whole closed render cluster → render.py + shared const → constants.py (chosen) · keep render in add.py (rejected — it's a closed unpatched cluster, a natural module)
  - chosen — transitive-closure AST proves closure; none patched → plain re-export; `_DEFAULT_WIDTH` is shared so constants.py is its single source (render.py + the staying default-args both import it).
Must:
<must>
  - render.py defines the 8 fns + `_ANSI` (verbatim); constants.py defines `_DEFAULT_WIDTH`; add.py re-imports the 8 so `add.<name>` resolves to the render objects; `_DEFAULT_WIDTH` resolves in add.py (the staying default-arg sigs unchanged).
  - every render path (status/report dashboard, persisted RETRO render) behaves identically; full suite passes unchanged.
  - both pins re-aimed (literals); 3-tree byte-identical.
</must>
Reject:
<reject>
  - a fn's output changes or `add.<name>`/`_DEFAULT_WIDTH` stops resolving -> "render_drift".
  - the pin recomputes itself -> "vacuous_pin"; a tree missing render.py -> "mirror_incomplete".
  - an import cycle (render↔add) -> "cycle" (render imports only constants + stdlib).
</reject>
After:
<after>
  - engine package gains render.py (8 modules); full suite ≥1882 green; both pins re-aimed.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ `_DEFAULT_WIDTH` relocated to constants.py still resolves in the staying default-arg signatures (evaluated at def-time/module-load) — lowest confidence: add.py imports it via the explicit `_`-prefixed constants import at the TOP (before any def), so it's in-namespace when those defs execute; the suite (every render path) names a miss LOUDLY. Cost: fix the import.
  - [ ] the 8 are closed + unpatched + not `add.X` in tests — confirmed (transitive-closure AST + grep).
  - [ ] `_ANSI` is render-private (only `_colorize`) — confirmed.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the 8 render fns moved but resolve unchanged
  Given they live in add_engine/render.py
  When a test imports add
  Then add._colorize / add._bar / add._wrap / ... all resolve AND are the add_engine.render objects

Scenario: rendering is byte-identical
  Given the split engine
  When _bar / _phase_track / _wrap / _colorize run with fixed inputs
  Then they return the same strings as before (progress bar cells, wrapped lines, ANSI when enabled)

Scenario: _DEFAULT_WIDTH relocation keeps the dashboard width
  Given _DEFAULT_WIDTH moved to constants.py
  When the persisted (non-interactive) report renders
  Then it uses width 72 exactly as before (the staying default-args resolve _DEFAULT_WIDTH)

Scenario: no cycle; render.py joins the pin, 3-tree consistent
  Then importing add_engine.render standalone needs no add; ENGINE_PKG_MD5 == package_digest (incl. render.py) across 3 trees; ENGINE_MD5 == md5(add.py); engine_pin.py no hashlib
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add_engine/constants.py:  + _DEFAULT_WIDTH = 72          # shared (render + staying default-args)
add_engine/render.py (NEW):
  from __future__ import annotations
  import os, re, shutil, sys
  from add_engine.constants import PHASES, _DEFAULT_WIDTH
  _ANSI = {...}                                           # render-private (moved verbatim)
  def _bar / _phase_track / _use_ascii / _color_enabled / _term_width / _colorize / _clip / _wrap   # verbatim

add.py:
  from add_engine.constants import ( ..., _DEFAULT_WIDTH )   # add to the _-prefixed explicit import
  from add_engine.render import (
      _bar, _phase_track, _use_ascii, _color_enabled, _term_width, _colorize, _clip, _wrap,
  )   # the 8 defs + _ANSI + _DEFAULT_WIDTH removed from add.py

engine_pin.py: ENGINE_MD5 + ENGINE_PKG_MD5 re-aimed (literals; never hashes).
Mirror: prepare_bundle -> _bundled; cp add.py+add_engine -> .add (no engine_pin.py in .add runtime).
```

Least-sure flag surfaced at freeze: [test] `_DEFAULT_WIDTH` relocation — must be imported into add.py at the top (before the staying default-arg defs). The 1882-suite (every render/report path) is the gate. Cost if wrong: fix the import.
Status: FROZEN @ v1 — approved by Tin Dang (auto mode; closed unpatched cluster, AST-closure-verified, suite-gated; the proven cluster recipe ×8)

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every scenario has one test; existing suite (≥1882) stays green.
Plan:
<test_plan>
  - test_render_reexported_same_object: all 8 resolve via add AND `is` the add_engine.render object.
  - test_render_output_preserved: _bar / _wrap / _colorize(enabled) return expected strings.
  - test_default_width_in_constants: add_engine.constants._DEFAULT_WIDTH == 72 AND add._DEFAULT_WIDTH resolves.
  - test_no_import_cycle + test_pkg_digest_includes_render_3tree + test_pins_literal_and_md5 + test_add_py_no_longer_defines_them.
</test_plan>

Tests live in: `add-method/tooling/test_engine_extract_render.py` (DECLARED in §5; written in tests phase BEFORE the tests→build crossing) · MUST run red before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/add_engine/render.py` `add-method/tooling/add_engine/constants.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_engine_extract_render.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add_engine/render.py` `add-method/src/add_method/_bundled/tooling/add_engine/constants.py`
Strategy: 1. (tests) write the new test red. 2. (build) add `_DEFAULT_WIDTH` to constants.py; create render.py (8 fns + `_ANSI` verbatim + imports); remove the 8 + `_ANSI` + `_DEFAULT_WIDTH` from add.py; add the render re-import + `_DEFAULT_WIDTH` to the constants import. 3. AST undefined-name scan of render.py. 4. re-aim both pins. 5. prepare_bundle → _bundled; cp → .add. 6. full suite green.
Safety rule: zero behavior change; engine_pin.py never hashes; no cycle; transitive-closure AST scan before suite.
Code lives in: `add-method/tooling/`
Constraints: do NOT change any test or the contract; stdlib + constants only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all tests pass
- [ ] coverage did not decrease
- [ ] no assertion was weakened
- [ ] the green was EARNED, not gamed — adversarial refute-read; a confirmed cheat is HARD-STOP
- [ ] concurrency / timing safe (pure string formatting + term-size read)
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like
- [ ] all 8 `add.<name> is add_engine.render.<name>` — §4
- [ ] _bar/_wrap/_colorize outputs unchanged — §4
- [ ] add_engine.constants._DEFAULT_WIDTH == 72; add._DEFAULT_WIDTH resolves; dashboard width unchanged — §4
- [ ] package_digest == ENGINE_PKG_MD5 across 3 trees (incl. render.py); ENGINE_MD5 == md5(add.py); engine_pin.py no hashlib

### Deep checks — do not skim
- [ ] WIRING — add.py re-imports the 8 + imports _DEFAULT_WIDTH; render.py imports constants/stdlib; engine_manifest globs it
- [ ] DEAD-CODE — the 8 + _ANSI + _DEFAULT_WIDTH GONE from add.py; no orphan
- [ ] SEMANTIC — n/a (code task)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-26

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch: status/report dashboard render · ENGINE_PKG_MD5 stability

### Spec delta
- [SPEC · dropped] remaining clean clusters (deps already in modules): deltas (_lint_task_deltas/_collect_open_deltas/_spec_delta_*) · release (_render_changelog_block/_render_releases_row/_closed_milestones) · milestone-doc (_project_goal/_exit_criteria/_stage_criteria) · components (_components/_contracts/_federation) · version-io (_read_json_safe/_version_gt/_fetch_latest_version[PATCHED]) · md5 (_md5_text/_md5_file). Then the cmd_*/save/load/main core. (evidence: 85 leaf-now candidates found)

### Competency deltas
- [ADD · folded] a SHARED constant (used by both moving + staying code) relocates to constants.py as the single source — distinguish from a cluster-PRIVATE const (travels with the cluster, like _ANSI/_INIT_EXCLUDE) (evidence: _DEFAULT_WIDTH vs _ANSI) [folded foundation-version 52]
