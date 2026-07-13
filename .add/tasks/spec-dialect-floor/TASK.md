# TASK: Spec-dialect test floor — the red suite must speak the contract's own example formats

slug: spec-dialect-floor · created: 2026-07-11 · stage: mvp
milestone: quality-floors
autonomy: auto
phase: done
fast: true
oneshot: true
gate_mode: ai-plan-verify

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): `add-method/tooling/add.py:_build_entry` (:1105 — the shared tests→build gate stack; the scope-still-default WARNING at :1181 is the exact print-only pattern to mirror) · `add-method/tooling/add_engine/constants.py` (registry home — _GATE_MODES/_SKIPPABLE_PHASES precedent for a new closed tuple) · `add_engine/taskdoc.py:_declared_test_files` (:46 — resolves §4 declared test files, PURE) · `add.py:cmd_check` audit block (:7143-7223 — risk_unset/refute_unrecorded list shape) · three byte-identical engine trees + engine_pin.py re-aim · new `test_spec_dialect_floor.py` (harness: test_scope_repair_path.py's _Board)
Context (working folder): MILESTONE.md quality-floors plan item 1; evidence = benchmark/results/2026-07-wv1-rep0.md wm2 root cause (own tests spoke naive timestamps; spec examples were Z-suffixed; crash shipped green)
Honors (patterns / conventions): warn-never-refuse at the crossing (scope-gate-repair-path M1: print-only, state byte-identical either way) · audit-measured-never-blocked (risk_unset shape) · closed registry tuple in constants with __all__ entry · every engine edit propagates to all three trees before the gate
Anchors the contract cites: `_build_entry` · `_declared_test_files` · `cmd_check` audits · `add_engine/constants.py:_DIALECT_CLASSES` (new)
Ground SHA: `cd78268`
Skip rationale: scenarios — the §1 Accept line + 4 named pins cover the behavior matrix; observe — one optional delta line at the gate

---

## 1 · SPECIFY — the rules

Feature: spec-dialect floor — when a frozen §3 contract carries a value in a recognized FORMAT DIALECT (v1 registry: one class, aware ISO-8601 timestamps `…T…Z`/`±hh:mm`) and NO declared §4 test file speaks that dialect, the tests→build crossing WARNS (print-only, never refuses) and `add.py check` names the task in a `dialect_gap` audit — closing the wm2 class (own tests spoke a friendlier input dialect than the spec's own examples) for ~zero turns
Must:
  - `add_engine/constants.py`: `_DIALECT_CLASSES` — closed tuple of (name, regex) pairs, v1 = ("aware-iso-timestamp", …); listed in `__all__` (a new trust surface is named, mirrors _GATE_MODES)
  - a PURE helper `_dialect_gaps(root, slug)` -> list of class names present in the raw §3 body but absent from EVERY declared §4 test file (empty when §3 has no match, when tests cover it, or when §4 declares no files — fail-open, never fail-noisy)
  - `_build_entry` prints one warning per gap class AFTER the scope-default warning: names the class, the wm2 evidence in one clause, and the repair (add one test speaking the format, then re-cross) — exit/state byte-identical to the no-gap path
  - `cmd_check`: `dialect_gap` audit lists tasks at build/verify/done whose frozen §3 has a gap vs their declared §4 files — audit-measured, never blocked, rescannable
  - all three engine trees byte-identical + ENGINE_MD5 re-aimed; full tooling suite green
Reject:
  - the crossing REFUSING (exit != 0) on a dialect gap -> "floor_overreach" (warn-then-gate means v1 warns; gating is a future, human-approved escalation)
  - regex false-positive on prose dates without the T separator (e.g. `2026-07-10` in a comment) -> "dialect_false_positive" (the class requires the full aware-timestamp shape)
Accept: Given a task whose frozen §3 pins `"2028-01-01T09:00:00Z"` and whose declared §4 test file contains only naive `"2028-01-01 09:00"` values, When it crosses tests→build, Then the crossing succeeds AND prints the aware-iso-timestamp warning AND `add.py check` lists the task under `dialect_gap`; adding one test line with a Z-suffixed timestamp clears both
Assumptions: ⚠ the raw §3 body is the right dialect source (not §1/§2) — the frozen shape is where examples are binding; if wrong: a contract that defers examples to §1 slips the floor, cost = the warning stays silent for that task (fail-open, same as today)

---

## 3 · CONTRACT — freeze the shape

```
add_engine/constants.py:
  _DIALECT_CLASSES: tuple[tuple[str, str], ...] = (
      ("aware-iso-timestamp",
       r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})"),
  )   # closed registry; in __all__

add.py (both trees + bundle):
  _dialect_gaps(root: Path, slug: str) -> list[str]     # PURE; §3 raw body vs _declared_test_files contents
  _build_entry: after the scope-default warning —
      for cls in _dialect_gaps(...): print(f"warning: ... dialect '{cls}' ... add.py re-cross ...")
  cmd_check audits: dialect_gap[] = [slug for tasks at build|verify|done with gaps]  # print + summary line

success: crossing exit 0 with warning text on stdout when gapped; silent when covered/no-match/no-files
rejections: floor_overreach (never a _die on gaps) · dialect_false_positive (bare dates never match)
```

`Least-sure flag surfaced at freeze:` [test] the audit scans build/verify/done tasks on every check run — on this repo's ~250 archived-but-on-disk TASK.md files the scan could be slow or noisy against historical tasks that predate the floor; if wrong: check output gains a long grandfathered list, cost = audit noise (mitigation pinned: audit only ACTIVE state tasks, not archived ones)
Status: FROZEN @ v1 — approved by claude-fable-5
Freeze mode: ai-plan-verify — verified by claude-fable-5 at 2026-07-10T17:25:01+00:00

### AI-verify record (required when gate_mode: ai-plan-verify)
- [x] §0 GROUND anchors resolve in the current tree — _build_entry:1105, scope warning :1181, _declared_test_files taskdoc.py:46, audit block :7143-7223, all grepped live at cd78268
- [x] §1 every Must + every Reject present, each Reject paired with an error code (floor_overreach · dialect_false_positive)
- [x] §3 CONTRACT shape is concrete — registry literal, helper signature, hook points, audit key all named
- [x] Lowest-confidence flag surfaced and substantive — audit-scan scope on a 250-task repo, with the mitigation pinned
Verified by: claude-fable-5 (session ee9aef91, orchestrator inline) · at: 2026-07-10T20:15:00Z

---

## 4 · TESTS — failing-first (red)

Plan: test_spec_dialect_floor.py (harness: _Board pattern from test_scope_repair_path.py) — test_gapped_crossing_warns_but_succeeds (Accept's first Then) · test_covered_suite_is_silent (the clearing arm) · test_no_dialect_contract_is_silent + bare-date false-positive pin (R2) · test_check_names_dialect_gap_audit · test_crossing_never_refuses_on_gap (R1: exit 0). Red first: the registry/helper don't exist.
Tests live in: `add-method/tooling/test_spec_dialect_floor.py` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `add-method/` `.add/tooling/` `tmp/`
Strategy & known-problem fixes: 1. red pins 2. constants registry 3. helper + warning + audit in add-method/tooling/add.py 4. cp to the two twin trees 5. engine_pin re-aim 6. full tooling suite. Traps: SEAMS line pins drift on add.py growth (re-pin x17 if the seams test reds) · the audit must read ACTIVE state tasks only (least-sure mitigation) · warning text must not contain the word freeze-gate vocab that trips slang guards · three-tree parity test fails on any missed cp
Approach (domain strategy): methodology-engine-dev stance — a floor is a named, closed, greppable registry + a pure predicate + print-only surfacing; never a refusal in v1
Strategy actually used: as planned — registry → helper → warning → check lint → 3-tree cp → both pins re-aimed (7f96609e / 710a009f) → SEAMS x17 re-pin; zero repair loops
Code lives in: `./src/`   ·   Constraints: change no test, no contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build — full tooling suite 3367 passed + the 6 new floor pins; the only transient red was the known SEAMS line-pin drift, re-pinned x17 (never a test weakened)
- [x] green was EARNED — the gapped-crossing pin drives the REAL CLI end-to-end (init → task → freeze → cross) and asserts warning text + exit 0 + advanced state together; the false-positive pin proves bare dates never match; check lint verified against a live board
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP) — pure regex over files already read by the engine; no subprocess, no new imports

Build expectations (from §1 Accept + §3 CONTRACT): a Z-timestamp contract + naive-only suite crossing prints the aware-iso-timestamp warning yet exits 0 with phase=build, and `check` lists the task under dialect_gap — confirmed by test_gapped_crossing_warns_but_succeeds + test_check_names_dialect_gap_audit running the real CLI; clearing arm confirmed by test_covered_suite_is_silent

### GATE RECORD
Outcome: PASS
Reviewed by: auto-resolved (autonomy: auto — complete evidence, print-only floor, no refusal path added) · date: 2026-07-10
OBSERVE: [SPEC · open] the registry has ONE class; candidate second class = currency/decimal-precision literals (the money half of the data-sensitivity rule) — add only with a real evidence case, never speculatively (evidence: _DIALECT_CLASSES closed-tuple design)

