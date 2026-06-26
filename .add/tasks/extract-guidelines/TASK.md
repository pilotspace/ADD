# TASK: Extract the guidelines/CLAUDE.md-injection subsystem (8 fns) to add_engine/guidelines.py

slug: extract-guidelines · created: 2026-06-26 · stage: mvp
autonomy: auto
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/add.py:194-433` — the guideline-injection subsystem (banner + 8 CONTIGUOUS fns + 1 cluster-private constant): `_guideline_block`(202) · `_inject_block`(238) · `_rule_file_mode`(270) · `_strip_inline_block`(288) · `_insert_rule_reference`(306) · `_ensure_claude_reference`(335) · `_inject_guidelines`(359) · `_INIT_EXCLUDE`(416, used ONLY by _is_brownfield) · `_is_brownfield`(423). Transitive-closure AST scan: the cluster makes ZERO outbound calls to non-cluster add fns (self-contained); deps = constants (GUIDELINE_FILES·RULES_FILE_REL·WORKFLOW_HEADINGS·_GUIDE_BEGIN·_GUIDE_END·_RULE_REF_LINE — all in constants.py) + `_atomic_write` (io_state) + os/re/sys/Path (stdlib). NONE patched. Callers (cmd_init·cmd_sync_guidelines·cmd_new_task) stay in add.py and call bare → add's re-imported global (no qualification needed — nothing patched).
  - `add-method/tooling/add_engine/guidelines.py` — NEW module: stdlib + `from add_engine.constants import (the 6)` + `from add_engine.io_state import _atomic_write`; holds `_INIT_EXCLUDE` + the 8 fns verbatim.
  - `add-method/tooling/add.py` — banner+8 fns+_INIT_EXCLUDE removed; add re-import `from add_engine.guidelines import (the 8)`.
  - `add-method/tooling/engine_pin.py` — both pins re-aimed.
Context (working folder): the engine package (6 modules → +guidelines = 7); 3-tree mirror. First clean CLUSTER past the leaf phase — bigger than a leaf but unpatched + self-contained (NOT the entangled cmd_*/report core).
Honors (patterns / conventions): the cluster-move recipe (re-export as add globals; NO qualification since unpatched; two-pin model; 3-tree byte-identical; zero behavior change; transitive-closure AST scan upfront); a cohesive subsystem → its own module; the cluster-private constant travels with its only user.
Anchors the contract cites: `add_engine/guidelines.py` (NEW) · the 8 fns + _INIT_EXCLUDE · add.py re-import · both pins.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: move the guidelines/CLAUDE.md-injection subsystem (8 fns + its private `_INIT_EXCLUDE` constant) from add.py into a NEW `add_engine/guidelines.py`; add.py re-imports. Eighth extraction — the first clean cohesive CLUSTER. Pure refactor (file IO is via _atomic_write only); zero behavior change.
Framings weighed: the whole closed cluster into guidelines.py (chosen) · split helpers vs cmd_* (rejected — the cmd_* callers stay; only the closed helper-subsystem moves)
  - chosen — transitive-closure AST proves the 8 fns are self-contained (no outbound add-fn calls); none patched → plain re-export works; the subsystem is a natural module (AGENTS.md/CLAUDE.md block sync).
Must:
<must>
  - guidelines.py defines the 8 fns + `_INIT_EXCLUDE` (verbatim); add.py re-imports the 8 so `add.<name>` resolves to the guidelines objects.
  - every CLI path that injects/syncs the ADD block (init · sync-guidelines · new-task) behaves identically; the full suite passes unchanged.
  - both pins re-aimed (literals); identical across 3 trees; guidelines.py byte-identical across canonical · _bundled · .add.
</must>
Reject:
<reject>
  - a fn's behavior changes or `add.<name>` stops resolving -> "guideline_drift".
  - the pin recomputes itself -> "vacuous_pin"; a tree missing guidelines.py -> "mirror_incomplete".
  - an import cycle (guidelines↔add) -> "cycle" (guidelines imports only constants+io_state+stdlib, never add).
</reject>
After:
<after>
  - the engine package gains guidelines.py (7 modules); add.py holds the cmd_*/validator/report core + dispatch; full suite ≥1874 green; both pins re-aimed.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the cluster is truly closed (no outbound add-fn call) so plain re-export needs no qualification — lowest confidence, but the transitive-closure AST scan returned an EMPTY outbound set AND none are patched; if a hidden caller relied on a local def, the suite names it LOUDLY. Cost: import the missed dep.
  - [ ] the 6 constants live in constants.py (auto-available to add.py via `import *`); _INIT_EXCLUDE is cluster-private (only _is_brownfield; test refs are comments) — confirmed.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the 8 fns moved but resolve unchanged
  Given the subsystem lives in add_engine/guidelines.py
  When a test does `import add`
  Then add._inject_guidelines / add._guideline_block / ... all resolve AND are the add_engine.guidelines objects

Scenario: the ADD block still injects/syncs identically
  Given the split engine
  When `init` / `sync-guidelines` run in a real project
  Then the marker-delimited ADD block is written to AGENTS.md/CLAUDE.md exactly as before (byte-for-byte block)

Scenario: no import cycle; guidelines is a constants+io_state leaf
  Given guidelines.py imports only constants + io_state + stdlib
  Then importing add_engine.guidelines standalone does NOT require add

Scenario: guidelines.py joins the pin, 3-tree consistent
  Then ENGINE_PKG_MD5 == package_digest (incl. guidelines.py) across 3 trees; ENGINE_MD5 == md5(add.py); engine_pin.py no hashlib
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add_engine/guidelines.py (NEW):
  from __future__ import annotations
  import os, re, sys
  from pathlib import Path
  from add_engine.constants import (GUIDELINE_FILES, RULES_FILE_REL, WORKFLOW_HEADINGS,
                                     _GUIDE_BEGIN, _GUIDE_END, _RULE_REF_LINE)
  from add_engine.io_state import _atomic_write
  _INIT_EXCLUDE = {...}                                  # moved verbatim (cluster-private)
  def _guideline_block() / _inject_block / _rule_file_mode / _strip_inline_block /
      _insert_rule_reference / _ensure_claude_reference / _inject_guidelines / _is_brownfield   # verbatim

add.py:
  from add_engine.guidelines import (
      _guideline_block, _inject_block, _rule_file_mode, _strip_inline_block,
      _insert_rule_reference, _ensure_claude_reference, _inject_guidelines, _is_brownfield,
  )   # the banner + 8 defs + _INIT_EXCLUDE removed; bare callers resolve add's global

engine_pin.py: ENGINE_MD5 + ENGINE_PKG_MD5 re-aimed (literals; never hashes).
Mirror: prepare_bundle -> _bundled; cp add.py+add_engine -> .add (no engine_pin.py in .add runtime).
```

Least-sure flag surfaced at freeze: [test] the closed-cluster assumption — transitive-closure AST scan returned EMPTY outbound; none patched. Residual: a hidden local dependence → the 1874-suite (every init/sync path) names it. Cost if wrong: import the dep.
Status: FROZEN @ v1 — approved by Tin Dang (auto mode; closed unpatched cluster, AST-closure-verified, suite-gated; the proven leaf/cluster recipe ×7)

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every scenario has one test; existing suite (≥1874) stays green.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_guidelines_reexported_same_object: all 8 resolve via add AND `is` the add_engine.guidelines object.
  - test_block_injection_byte_identical: a real `init` writes the canonical ADD block (markers + body) into CLAUDE.md unchanged.
  - test_no_import_cycle: import add_engine.guidelines standalone (no add).
  - test_pkg_digest_includes_guidelines_3tree + test_pins_literal_and_md5 + test_add_py_no_longer_defines_them.
</test_plan>

Tests live in: `add-method/tooling/test_engine_extract_guidelines.py` (DECLARED in §5; written in the tests phase BEFORE the tests→build crossing) · MUST run red before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/add_engine/guidelines.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_engine_extract_guidelines.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add_engine/guidelines.py`
Strategy (ordered batches): 1. (tests phase) write the new test red. 2. (build) create guidelines.py (8 fns + _INIT_EXCLUDE verbatim + imports); remove banner+8 fns+_INIT_EXCLUDE from add.py; add the re-import. 3. AST undefined-name scan of guidelines.py. 4. re-aim both pins. 5. prepare_bundle → _bundled; cp → .add. 6. full suite green.
Safety rule (feature-specific): zero behavior change; engine_pin.py never hashes; no import cycle; transitive-closure AST scan before suite.
Code lives in: `add-method/tooling/`
Constraints: do NOT change any test or the contract; stdlib + constants + io_state only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all tests pass
- [ ] coverage did not decrease
- [ ] no assertion was weakened
- [ ] the green was EARNED, not gamed — adversarial refute-read; a confirmed cheat is HARD-STOP
- [ ] concurrency / timing of the file-write paths is safe (writes via _atomic_write only)
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like
- [ ] all 8 `add.<name> is add_engine.guidelines.<name>` — §4
- [ ] a real init writes the canonical ADD block byte-identically — §4
- [ ] add_engine.guidelines imports standalone (no cycle) — §4
- [ ] package_digest == ENGINE_PKG_MD5 across 3 trees (incl. guidelines.py); ENGINE_MD5 == md5(add.py); engine_pin.py no hashlib

### Deep checks — do not skim
- [ ] WIRING (code) — add.py re-imports the 8; guidelines.py imports constants/io_state/stdlib; engine_manifest globs it
- [ ] DEAD-CODE (code) — the banner + 8 fns + _INIT_EXCLUDE GONE from add.py; no orphan
- [ ] SEMANTIC — n/a (code task)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-26

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): init/sync block injection · ENGINE_PKG_MD5 stability

### Spec delta
- [SPEC · open] remaining core = cmd_* dispatch (~1100L) · UDD validator (~1500L) · report (~3100L) — each needs its own task; cmd_* extraction needs the dispatch table repointed (evidence: this banked the last closed helper-cluster)

### Competency deltas
- [ADD · open] a transitive-closure AST scan (not just one-level free-names) proves a cluster is self-contained → a closed unpatched cluster moves by plain re-export, no qualification (evidence: the 8-fn guidelines subsystem, empty outbound set)
