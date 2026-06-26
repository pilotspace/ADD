# TASK: Extract component/federation subsystem (7 fns) to add_engine/components.py

slug: extract-components · created: 2026-06-26 · stage: mvp
autonomy: auto
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/add.py` — the component/federation reader cluster (7 fns, transitive-closure AST = closed, ZERO outbound): `_confined`(3116) · `_components`(3257) · `_cite_region`(3319) · `_contracts`(3377) · `_federation`(3396) · `_contract_snapshot`(3427) · `_in_scope`(3503). Strict free-name recheck: deps = ONLY `re`+`Path`(stdlib) + `tomllib`(guarded stdlib). NO constants. NONE patched, NONE add.X in tests. components.toml path is a literal (`root / "components.toml"`).
  - ⚠ `tomllib` GUARD: add.py guards `try: import tomllib except ModuleNotFoundError: tomllib = None` (@28-31); the moved fns reference bare `tomllib` + check `if tomllib is None`. components.py MUST replicate that exact guard (NOT a bare `import tomllib`), or `import add` dies on py3.10 (CI runs 3.10). add.py KEEPS its own `tomllib` import — the staying `_component_findings`(3335, a tomllib-user NOT in this closure) needs it.
  - `add-method/tooling/add_engine/components.py` — NEW: stdlib (re/Path) + the guarded tomllib + the 7 fns verbatim.
  - `add-method/tooling/add.py` — remove the 7 fns; add `from add_engine.components import (the 7)`. KEEP the tomllib guard (staying _component_findings uses it).
  - `add-method/tooling/engine_pin.py` — both pins re-aimed.
Context: engine package (9 modules → +components = 10); 3-tree mirror. The component-aware-add subsystem (registry · contracts · federation · scope-confinement). Callers (cmd_* / verify / report) stay (bare → add's re-imported global).
Honors: cluster-move recipe (re-export, NO qualification since unpatched; transitive-closure AST upfront); replicate a degrade-safe stdlib guard, don't bare-import.
Anchors: `add_engine/components.py` (NEW) · the 7 fns · the tomllib guard · add.py re-import · both pins.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: move the 7 component/federation reader fns from add.py into a NEW `add_engine/components.py` (replicating the degrade-safe tomllib guard); add.py re-imports. Eleventh extraction. Pure refactor; zero behavior change incl. the py<3.11 degrade-to-opt-out path.
Framings weighed: the closed component cluster → components.py (chosen) · leave in add.py (rejected — closed unpatched cluster, a natural subsystem)
  - chosen — transitive-closure AST proves closure; none patched → plain re-export; the tomllib guard is replicated so py3.10 import stays safe.
Must:
<must>
  - components.py defines the 7 fns (verbatim) + the guarded tomllib import; add.py re-imports so `add.<name>` resolves to the components objects.
  - byte-identical-when-no-components.toml invariant holds; py<3.11 still degrades (tomllib None → {} / opt-out); the full suite (incl. the component suites that skip on 3.10) passes unchanged.
  - both pins re-aimed (literals); 3-tree byte-identical.
</must>
Reject:
<reject>
  - a fn's behavior changes, `add.<name>` stops resolving, or `import add` breaks on py3.10 -> "component_drift".
  - the pin recomputes itself -> "vacuous_pin"; a tree missing components.py -> "mirror_incomplete".
  - an import cycle (components↔add) -> "cycle" (components imports only stdlib).
</reject>
After:
<after>
  - engine package gains components.py (10 modules); full suite ≥1901 green on BOTH py3.10 + py3.12; both pins re-aimed.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ replicating the tomllib guard in components.py keeps py3.10 `import add` safe AND the moved readers degrade identically — lowest confidence; CI runs py3.10 (the gate); a bare `import tomllib` would crash 3.10 import. Mitigation: the guard is copied verbatim; the component suites' setUpModule SkipTest still skips runtime on 3.10. Cost: fix the guard.
  - [ ] closed (transitive-closure AST) + unpatched + no constants — confirmed (strict recheck: only re/Path/tomllib).
  - [ ] staying `_component_findings` keeps add.py's own tomllib — add.py retains the guard.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the 7 fns moved but resolve unchanged
  Given they live in add_engine/components.py
  When a test imports add
  Then add._components / add._contracts / add._federation / ... resolve AND are the add_engine.components objects

Scenario: byte-identical with no registry
  Given a project with no .add/components.toml
  When _components(root) runs
  Then it returns {} exactly as before (opt-in invariant)

Scenario: py<3.11 degrade-safe + no cycle + 3-tree pins
  Given components.py replicates the tomllib guard
  Then importing add_engine.components standalone needs no add and does not crash when tomllib is absent
  And ENGINE_PKG_MD5 == package_digest (incl. components.py) across 3 trees; ENGINE_MD5 == md5(add.py); engine_pin.py no hashlib
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add_engine/components.py (NEW):
  from __future__ import annotations
  import re
  from pathlib import Path
  try:                          # component registry parse (Python 3.11+); degrade-safe
      import tomllib
  except ModuleNotFoundError:
      tomllib = None
  def _confined / _components / _cite_region / _contracts / _federation /
      _contract_snapshot / _in_scope                                   # verbatim

add.py:
  # KEEP the existing tomllib guard (staying _component_findings uses it)
  from add_engine.components import (
      _confined, _components, _cite_region, _contracts, _federation,
      _contract_snapshot, _in_scope,
  )   # the 7 defs removed; bare callers resolve add's global

engine_pin.py: ENGINE_MD5 + ENGINE_PKG_MD5 re-aimed (literals; never hashes).
Mirror: prepare_bundle -> _bundled; cp add.py+add_engine -> .add (no engine_pin.py in .add runtime).
```

Least-sure flag surfaced at freeze: [test] the tomllib guard replication — py3.10 CI is the gate (a bare import would crash). The guard is copied verbatim; the 1901-suite on both 3.10+3.12 confirms. Cost if wrong: fix the guard.
Status: FROZEN @ v1 — approved by Tin Dang (auto mode; closed unpatched cluster, AST-closure-verified, tomllib-guard replicated, suite-gated on both py versions; the proven cluster recipe ×10)

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every scenario has one test; existing suite (≥1901) stays green on 3.10 + 3.12.
Plan:
<test_plan>
  - test_components_reexported_same_object: all 7 resolve via add AND `is` the add_engine.components object.
  - test_no_registry_returns_empty: _components on a dir with no components.toml returns {} (opt-in invariant).
  - test_no_import_cycle: import add_engine.components standalone (no add).
  - test_pkg_digest_includes_components_3tree + test_pins_literal_and_md5 + test_add_py_no_longer_defines_them.
</test_plan>

Tests live in: `add-method/tooling/test_engine_extract_components.py` (DECLARED in §5; written in tests phase BEFORE the tests→build crossing) · MUST run red before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/add_engine/components.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_engine_extract_components.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add_engine/components.py`
Strategy: 1. (tests) write the new test red. 2. (build) create components.py (the guarded tomllib + 7 fns verbatim); remove the 7 from add.py (KEEP add.py's tomllib guard); add the re-import. 3. AST undefined-name scan. 4. re-aim both pins. 5. prepare_bundle → _bundled; cp → .add. 6. full suite green.
Safety rule: zero behavior change; the tomllib guard replicated verbatim (no bare import); engine_pin.py never hashes; no cycle.
Code lives in: `add-method/tooling/`
Constraints: do NOT change any test or the contract; stdlib only.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all tests pass (3.10 + 3.12 in CI)
- [ ] coverage did not decrease
- [ ] no assertion was weakened
- [ ] the green was EARNED, not gamed — adversarial refute-read; a confirmed cheat is HARD-STOP
- [ ] concurrency / timing safe (pure file reads; opaque TOML parse, never executed)
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like
- [ ] all 7 `add.<name> is add_engine.components.<name>` — §4
- [ ] no-registry → {} (opt-in invariant) — §4
- [ ] import add_engine.components standalone (no cycle); py3.10 import safe (guard) — §4 + CI
- [ ] package_digest == ENGINE_PKG_MD5 across 3 trees (incl. components.py); ENGINE_MD5 == md5(add.py); engine_pin.py no hashlib

### Deep checks — do not skim
- [ ] WIRING — add.py re-imports the 7 + KEEPS its tomllib guard; components.py replicates the guard; engine_manifest globs it
- [ ] DEAD-CODE — the 7 GONE from add.py; no orphan; add.py tomllib guard retained for _component_findings
- [ ] SEMANTIC — n/a (code task)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-26

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch: component/federation paths · py3.10 import safety · ENGINE_PKG_MD5 stability

### Spec delta
- [SPEC · dropped] next clean clusters: md5 (trivial) · version-update (_fetch_latest_version PATCHED) · deltas (7 shared constants → constants.py) · release/changelog; THEN cmd_*/save/load/main core (evidence: per-cluster coupling map in memory)

### Competency deltas
- [ADD · folded] a degrade-safe stdlib guard (try/except import → None) must be REPLICATED in the new module, not bare-imported — the staying module keeps its own copy for its own users (evidence: tomllib in both components.py and add.py for _component_findings) [folded foundation-version 52]
