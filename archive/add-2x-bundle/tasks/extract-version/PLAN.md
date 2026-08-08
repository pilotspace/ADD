# TASK: Extract version-check helpers (3 fns) to add_engine/version.py

slug: extract-version · created: 2026-06-26 · stage: mvp
autonomy: auto
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/add.py` — the update-nudge version helpers (3 fns, closed): `_read_json_safe`(5891) · `_version_gt`(5905) · `_fetch_latest_version`(5919, IO: urllib GET w/ timeout, fail-soft). + cluster-PRIVATE `_REGISTRY_LATEST`(5888, npm registry URL — used ONLY @5935 in _fetch_latest_version). The 3 fns DO NOT call each other (no internal qualification needed). Deps: `json`+`urllib.request`+`Path`(stdlib) + `_REGISTRY_LATEST`(travels).
  - ⚠ PATCH SHAPE: `test_update_nudge.py` REASSIGNS `add._fetch_latest_version = lambda *a,**k: ...` (a module-global rebind, NOT patch.object). The CALLER (the update-nudge check @5935-5972) STAYS in add.py and bare-calls `_fetch_latest_version()` → resolves add's re-imported global → the test's rebind on `add._fetch_latest_version` STILL intercepts. Standard re-export; NO qualification.
  - `add-method/tooling/add_engine/version.py` — NEW: `import json` + `import urllib.request` + `from pathlib import Path` + `_REGISTRY_LATEST` + the 3 fns verbatim.
  - `add-method/tooling/add.py` — remove the 3 fns + `_REGISTRY_LATEST`; add `from add_engine.version import (the 3)`.
  - `add-method/tooling/engine_pin.py` — both pins re-aimed.
Context: engine package (10 modules → +version = 11); 3-tree mirror. The npm/PyPI update-nudge subsystem. The nudge-check CALLER stays (bare → add's re-imported global).
Honors: cluster-move recipe (re-export, NO qualification — caller is in add.py, the rebind hits add's global; the 3 fns don't call each other); cluster-private const travels.
Anchors: `add_engine/version.py` (NEW) · the 3 fns + `_REGISTRY_LATEST` · add.py re-import · both pins.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: move the 3 version-check/update-nudge helper fns (+ private `_REGISTRY_LATEST`) from add.py into a NEW `add_engine/version.py`; add.py re-imports. Thirteenth extraction. Pure refactor; zero behavior change incl. the fail-soft network path.
Framings weighed: the closed version cluster → version.py (chosen) · leave in add.py (rejected — closed cluster, a natural module)
  - chosen — closure verified; the 3 fns don't call each other; the test rebinds `add._fetch_latest_version` and the caller stays in add.py → plain re-export intercepts; cohesive concern (registry version check).
Must:
<must>
  - version.py defines the 3 fns + `_REGISTRY_LATEST` (verbatim); add.py re-imports so `add.<name>` resolves to the version objects AND the test rebind `add._fetch_latest_version = lambda` still steers the nudge.
  - the update-nudge behaves identically (fetch fail-soft, version-gt compare, cache read); full suite incl. test_update_nudge.py passes unchanged.
  - both pins re-aimed (literals); 3-tree byte-identical.
</must>
Reject:
<reject>
  - a fn's behavior changes, `add.<name>` stops resolving, or the test rebind stops steering the nudge -> "version_drift".
  - the pin recomputes itself -> "vacuous_pin"; a tree missing version.py -> "mirror_incomplete".
  - an import cycle (version↔add) -> "cycle" (version imports only stdlib).
</reject>
After:
<after>
  - engine package gains version.py (11 modules); full suite ≥1919 green; both pins re-aimed.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the `add._fetch_latest_version = lambda` rebind in test_update_nudge.py still steers the nudge after re-export — the caller (nudge check) STAYS in add.py and bare-resolves add's global, so the rebind on add's name intercepts; the 3 fns don't call each other (no internal binding). The suite (test_update_nudge.py) is the gate. Cost if wrong: qualify the caller's call site.
  - [ ] closed + 3 fns don't call each other + `_REGISTRY_LATEST` private — confirmed.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the 3 fns moved but resolve unchanged
  Given they live in add_engine/version.py
  When a test imports add
  Then add._read_json_safe / add._version_gt / add._fetch_latest_version resolve AND are the add_engine.version objects

Scenario: the nudge test rebind still steers
  Given add._fetch_latest_version is reassigned to a stub lambda (as test_update_nudge.py does)
  When the update-nudge check (a staying add.py fn) runs
  Then it uses the stub (the rebind on add's global intercepts the bare call)

Scenario: version compare preserved + no cycle + 3-tree pins
  When _version_gt("1.2.0","1.1.9") and _version_gt("1.0.0","1.0.0")
  Then True and False respectively
  And importing add_engine.version standalone needs no add; ENGINE_PKG_MD5 == package_digest (incl. version.py) across 3 trees; ENGINE_MD5 == md5(add.py); engine_pin.py no hashlib
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add_engine/version.py (NEW):
  from __future__ import annotations
  import json
  import urllib.request
  from pathlib import Path
  _REGISTRY_LATEST = "https://registry.npmjs.org/@pilotspace/add/latest"   # cluster-private
  def _read_json_safe / _version_gt / _fetch_latest_version              # verbatim

add.py:
  from add_engine.version import (
      _read_json_safe, _version_gt, _fetch_latest_version,
  )   # the 3 defs + _REGISTRY_LATEST removed; the nudge-check caller stays (bare -> add's global)

engine_pin.py: ENGINE_MD5 + ENGINE_PKG_MD5 re-aimed (literals; never hashes).
Mirror: prepare_bundle -> _bundled; cp add.py+add_engine -> .add (no engine_pin.py in .add runtime).
```

Least-sure flag surfaced at freeze: [test] the `add._fetch_latest_version` rebind — the caller stays in add.py so the rebind on add's global intercepts. test_update_nudge.py is the gate. Cost if wrong: qualify the caller's call site.
Status: FROZEN @ v1 — approved by Tin Dang (auto mode; closed cluster, caller-stays re-export, rebind-safe, suite-gated; the proven cluster recipe ×11)

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every scenario has one test; existing suite (≥1919) incl. test_update_nudge.py stays green.
Plan:
<test_plan>
  - test_version_reexported_same_object: all 3 resolve via add AND `is` the add_engine.version object.
  - test_rebind_steers_nudge: reassign add._fetch_latest_version to a stub, assert the staying nudge-check uses it (the rebind intercepts).
  - test_version_gt_preserved: _version_gt true/false cases.
  - test_no_import_cycle + test_pkg_digest_includes_version_3tree + test_pins_literal_and_md5 + test_add_py_no_longer_defines_them.
</test_plan>

Tests live in: `add-method/tooling/test_engine_extract_version.py` (DECLARED in §5; written in tests phase BEFORE the tests→build crossing) · MUST run red before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/add_engine/version.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_engine_extract_version.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add_engine/version.py`
Strategy: 1. (tests) write the new test red. 2. (build) create version.py (3 fns + `_REGISTRY_LATEST` verbatim + imports); remove the 3 + `_REGISTRY_LATEST` from add.py; add the re-import. 3. AST undefined-name scan. 4. re-aim both pins. 5. prepare_bundle → _bundled; cp → .add. 6. full suite green.
Safety rule: zero behavior change; engine_pin.py never hashes; no cycle; the nudge rebind stays steerable.
Code lives in: `add-method/tooling/`
Constraints: do NOT change any test or the contract; stdlib only.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all tests pass
- [ ] coverage did not decrease
- [ ] no assertion was weakened
- [ ] the green was EARNED, not gamed — adversarial refute-read; a confirmed cheat is HARD-STOP
- [ ] concurrency / timing safe (network fetch is fail-soft, timeout-bounded)
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like
- [ ] all 3 `add.<name> is add_engine.version.<name>` — §4
- [ ] the `add._fetch_latest_version` rebind still steers the nudge — §4
- [ ] _version_gt true/false preserved; no import cycle — §4
- [ ] package_digest == ENGINE_PKG_MD5 across 3 trees (incl. version.py); ENGINE_MD5 == md5(add.py); engine_pin.py no hashlib

### Deep checks — do not skim
- [ ] WIRING — add.py re-imports the 3; version.py imports stdlib only; engine_manifest globs it
- [ ] DEAD-CODE — the 3 + _REGISTRY_LATEST GONE from add.py; no orphan
- [ ] SEMANTIC — n/a (code task)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-26

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch: update-nudge path · ENGINE_PKG_MD5 stability

### Spec delta
- [SPEC · dropped] version was the LAST clean closed cluster. The residual add.py is the coupled CORE (deltas/autonomy/next-pair/cmd_* dispatch/report_data/save/load/main, a 31-fn web around load_state) — probe for closed SUB-clusters (autonomy-only, delta-lint-only) to extract; what remains is the legitimate entry/orchestrator module (you don't dissolve the entry point). Milestone extraction phase nears its natural end at ~13 modules (evidence: closure scans 2026-06-26)

### Competency deltas
- [ADD · folded] a test that REBINDS a module global (`add.X = lambda`, not patch.object) is re-export-safe IFF the caller stays in the host module (bare call resolves the host global) AND the moved fns don't call X internally — same rule as patch.object, different syntax (evidence: test_update_nudge.py rebinds add._fetch_latest_version; caller is the staying nudge-check) [folded foundation-version 52]
