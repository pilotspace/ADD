# TASK: Extract pure active-task/milestone accessors to add_engine/accessors.py

slug: extract-accessors · created: 2026-06-26 · stage: mvp
autonomy: auto
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/add.py:109-166` — the 6 PURE active-task/milestone state-dict accessors (CONTIGUOUS block, ends before `_git_config` at :167): `_active_milestone(state)` · `_active_task(state, milestone=None)` · `_set_active_milestone(state, slug)` · `_set_active_task(state, slug, milestone=None)` · `_activate_milestone(state, slug)` · `_deactivate_milestone(state, slug)`. Rigorous AST free-name scan: the ONLY free name is `_active_milestone` (used by `_set_active_task`) — itself in the move set. ZERO external deps, no constants, no stdlib, no missed transitive deps. MOVE to a NEW `add_engine/accessors.py`.
  - `add-method/tooling/add_engine/accessors.py` — NEW module (pure in-memory state-dict accessors).
  - `add-method/tooling/engine_pin.py` — `ENGINE_MD5` (md5 add.py) + `ENGINE_PKG_MD5` (package digest, accessors.py auto-joins via glob) re-aimed.
  - patch landscape: NONE of the 6 are monkeypatched (pure dict mutators). The identity/`_stamp_gate_record`/`_my_work` accessors are entangled (subprocess/getpass/`_task_*` deps, some patched) → DEFERRED to follow-up tasks; this task is the clean namesake core only.
Context (working folder): the engine package (constants · io_state · NEW accessors · the add.py entry); 3-tree mirror.
Honors (patterns / conventions): the task-1/2/3 playbook — re-export moved names as add.py module globals; two-pin model; byte-identical 3-tree mirror; zero behavior change; the AST free-name scan ran UPFRONT (extract-state lesson) and is clean.
Anchors the contract cites: `add_engine/accessors.py` (NEW) · the 6 accessors · add.py re-import · both pins re-aimed.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: move the 6 pure active-task/milestone state-dict accessors (`_active_milestone`, `_active_task`, `_set_active_milestone`, `_set_active_task`, `_activate_milestone`, `_deactivate_milestone`) from add.py into a NEW `add_engine/accessors.py`; add.py re-imports them as module globals. Fourth extraction of the engine split. Pure refactor; zero behavior change.
Framings weighed: the 6-pure-contiguous core into a new accessors.py (chosen) · the whole 20-fn accessor seam
  - chosen — move only the 6 pure, contiguous, dependency-free state-dict accessors (the seam's namesake). Safest leaf: zero deps (AST-confirmed), unpatched, clean block.
  - whole seam: deferred — the identity functions (`_git_config`/`_os_user`/`_whoami`/`_actor_*`) hit subprocess/getpass + are patched in identity tests; `_stamp_gate_record`/`_my_work` call `_task_*` helpers that stay in add.py. Each is its own follow-up (likely with the reduce-or-repoint decision like save_state).
Must:
<must>
  - `add_engine/accessors.py` defines the 6 accessors (moved verbatim); add.py re-imports them so `add._active_task`/`add._set_active_milestone`/etc. all resolve to the accessors objects.
  - every CLI command + the full suite behave identically (the multi-active / team-collaboration tests that exercise these accessors stay green).
  - `ENGINE_MD5` re-aimed to md5(new add.py); `ENGINE_PKG_MD5` re-aimed (accessors.py joins the digest); both literal, identical across all 3 trees.
  - accessors.py + add.py synced byte-identical across canonical · _bundled · .add.
</must>
Reject:
<reject>
  - an accessor's behavior changes or `add.<name>` stops resolving -> "accessor_drift" (round-trip identity test).
  - the pin recomputes itself in engine_pin.py -> "vacuous_pin".
  - accessors.py missing from any of the 3 trees -> "mirror_incomplete".
</reject>
After:
<after>
  - the engine package gains accessors.py (4 modules: constants · io_state · accessors · the add.py entry); full suite ≥1838 green; both pins re-aimed; the next extraction proceeds.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ The 6 accessors are fully self-contained — lowest confidence is essentially nil: the rigorous AST free-name scan (run upfront, the extract-state lesson) shows the only free name is `_active_milestone`, itself in the move set. If somehow wrong, the full suite goes red and names it. Cost: fold the missed dep.
  - [ ] none of the 6 are monkeypatched — confirmed (pure dict mutators; grep clean).
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the 6 accessors moved but resolve unchanged
  Given the accessors live in add_engine/accessors.py
  When a test does `import add`
  Then add._active_milestone, add._active_task, add._set_active_milestone,
       add._set_active_task, add._activate_milestone, add._deactivate_milestone all resolve
  And each is the same object as add_engine.accessors.<name>

Scenario: active-task/milestone selection still works end-to-end
  Given a project with a milestone and tasks
  When new-milestone / new-task / use run via the CLI
  Then the active milestone + task track correctly (the accessors drive selection)

Scenario: accessors.py joins the package pin, 3-tree consistent
  Given accessors.py is new in the package
  When engine_manifest + engine_pin are read
  Then ENGINE_PKG_MD5 == package_digest (incl. accessors.py), identical across the 3 trees
  And ENGINE_MD5 == md5(add.py); engine_pin.py has no hashlib
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add_engine/accessors.py (NEW module):
  from __future__ import annotations
  def _active_milestone(state) -> str | None          # moved verbatim
  def _active_task(state, milestone=None) -> str | None
  def _set_active_milestone(state, slug) -> None
  def _set_active_task(state, slug, milestone=None) -> None
  def _activate_milestone(state, slug) -> None
  def _deactivate_milestone(state, slug) -> None
  # zero imports beyond __future__ — pure in-memory dict ops (AST-confirmed)

add.py (the 6 defs removed; re-import added):
  from add_engine.accessors import (
      _active_milestone, _active_task, _set_active_milestone,
      _set_active_task, _activate_milestone, _deactivate_milestone,
  )   # bare callers resolve add's module global; `add.<name>` still works

engine_pin.py (two literals, re-aimed):
  ENGINE_MD5     = "<md5(new add.py)>"
  ENGINE_PKG_MD5 = "<package_digest over constants.py + io_state.py + accessors.py + __init__.py>"

Mirror: prepare_bundle → _bundled (copies add_engine/ recursively); cp add.py+engine_pin+add_engine → .add
        (do NOT ship engine_pin.py into .add runtime tree).
```

Least-sure flag surfaced at freeze: [test] essentially none material — the AST free-name scan (the extract-state lesson, run UPFRONT) proves the 6 are dependency-free; they are unpatched pure dict ops. The single biggest residual risk is a behavior-sensitive CALLER elsewhere in add.py relying on these being local — covered by the full 1838-suite (the multi-active/team-collab tests exercise active selection heavily). Cost if wrong: suite names it; fold the fix.
Status: FROZEN @ v1 — approved by Tin Dang (auto mode; pure verbatim refactor, AST-verified dependency-free, suite-gated; tasks 1-3 pattern proven+merged)

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every scenario has one test; existing suite (≥1838) stays green.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_accessors_reexported_same_object: import add → all 6 resolve AND `is` the add_engine.accessors object.
  - test_active_selection_end_to_end: init + new-milestone + new-task + use; assert active milestone/task track (the accessors drive it through the real CLI).
  - test_pkg_digest_includes_accessors_3tree: package_files includes accessors.py; package_digest == ENGINE_PKG_MD5 across 3 trees.
  - test_pins_literal_and_md5: ENGINE_MD5 == md5(add.py); engine_pin.py has no hashlib.
  - test_add_py_no_longer_defines_them: add.py carries no `def <name>(` for the 6.
</test_plan>

Tests live in: `add-method/tooling/test_engine_extract_accessors.py` · MUST run red (no accessors.py yet) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/add_engine/accessors.py` `add-method/tooling/engine_pin.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add_engine/accessors.py`
Strategy (ordered batches): 1. create accessors.py with the 6 (verbatim), remove from add.py, add the re-import. 2. AST free-name scan of accessors.py (catch any missed dep). 3. re-aim both pins. 4. prepare_bundle → _bundled; cp → .add. 5. full suite green.
Safety rule (feature-specific): zero behavior change; engine_pin.py never hashes; run the AST undefined-name scan before the suite (extract-state lesson).
Code lives in: `add-method/tooling/`
Constraints: do NOT change any test or the contract; stdlib only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 1846/0 (was 1838; +8 new)
- [x] coverage did not decrease — +8 tests, +1 module under the package pin
- [x] no test or contract was altered during build — git status shows only the NEW test file; §3 untouched
- [x] the green was EARNED, not gamed — adversarial refute-read: the move is PROVABLY verbatim (git diff = exactly the 6 def removals + the re-import). The real net is the 1846-suite — the multi-active/team-collab tests exercise active selection through these accessors. No surprises (the AST free-name scan ran UPFRONT and was clean — no 806-class miss).
- [x] concurrency / timing safe — pure in-memory dict ops; no IO, no timing surface
- [x] no exposed secrets, injection openings, or unexpected dependencies — accessors.py imports nothing beyond __future__ (AST-confirmed pure leaf)
- [x] layering & dependencies follow CONVENTIONS.md — accessors.py is the purest leaf yet (zero imports); add.py → accessors the only edge; no cycle
- [x] a person reviewed and approved the change — Tin Dang, auto mode (standing directive; pure verbatim refactor, suite-gated)

### Build expectations — what "correct" looks like
- [x] all 6 `add.<name> is add_engine.accessors.<name>` True — §4 identity test green
- [x] active milestone/task selection works through the CLI — §4 end-to-end test green (active task tracks after new-task)
- [x] package_digest == ENGINE_PKG_MD5 across 3 trees (incl. accessors.py); ENGINE_MD5 == md5(add.py) — §4 pin test green
- [x] engine_pin.py has no hashlib — confirmed
- [x] AST free-name scan of accessors.py clean — confirmed before suite (undefined: [])

### Deep checks — do not skim
- [x] WIRING (code) — add.py re-imports + bare-calls the 6; accessors.py pure leaf (no imports); engine_manifest globs it into the pin
- [x] DEAD-CODE (code) — the 6 GONE from add.py (test_add_py_no_longer_defines_them green); the accessor-seam banner stays (14 fns remain under it); no orphan
- [x] SEMANTIC — n/a (code task)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-26   (auto mode — pure verbatim refactor; full suite 1846/0, seam audit clean 90, both pins re-aimed + 3-tree parity; AST free-name scan clean upfront)

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): suite green count · ENGINE_PKG_MD5 stability across trees

### Spec delta
- [SPEC · open] next = extract-contracts (or the deferred identity/_stamp_gate_record accessor sub-tasks) (evidence: the 14 remaining accessor-seam fns are entangled — own tasks)

### Competency deltas
- [ADD · open] running the AST free-name scan UPFRONT (at ground) pre-empts the 806-error class from extract-state (evidence: this task's scan was clean before any code moved)
