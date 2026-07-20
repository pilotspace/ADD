# TASK: add .pytest_cache/.coverage to the scope-walk exclusion set (regenerated test artifacts, false scope_violation)

slug: scope-exclude-test-caches · created: 2026-07-07 · stage: mvp
milestone: add-bench
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): the 3 byte-identical engine trees — `add-method/tooling/add.py:_SCOPE_EXCLUDE_DIRS`/`:_SCOPE_EXCLUDE_FILES` (+ `.add/tooling/add.py` and `add-method/src/add_method/_bundled/tooling/add.py` twins) · `add-method/tooling/engine_pin.py:ENGINE_MD5` (byte pin, must follow).
Context (working folder): the constant's own comment documents this exact additive change-request path ("a regenerated artifact is NOT a source touch… widening it is an additive change-request, never silent"); trigger: bench-pilot-report heal_exhausted HARD-STOP on gate-regenerated `benchmark/.pytest_cache` + `.coverage`.
Honors (patterns / conventions): 3-tree engine parity (test_release `test_engine_trees_parity`) · additive-only widening of the ONE named exclusion constant · engine change ripples into ENGINE_MD5 pin.
Anchors the contract cites: `_SCOPE_EXCLUDE_DIRS` · `_SCOPE_EXCLUDE_FILES` · `ENGINE_MD5` (engine_pin.py).
Ground SHA: 0c716f0

---

## 1 · SPECIFY — the rules

Feature: scope-walk exclusion of regenerated test-cache artifacts
Must:
  - `.pytest_cache` is in `_SCOPE_EXCLUDE_DIRS` and `.coverage` in `_SCOPE_EXCLUDE_FILES`, identically in all 3 engine trees; ENGINE_MD5 re-pinned to the new byte-identical trees
Reject:
  - trees diverge (any add.py md5 != ENGINE_MD5) -> release test `test_engine_trees_parity` red
Accept: Given a task with declared scope `x/` and a regenerated `benchmark/.pytest_cache/…` + `.coverage` in the tree, When the §5 scope walk runs, Then those paths are excluded (no scope_violation) while a genuine out-of-scope source touch still trips.
Assumptions: none material — biggest risk: an unrelated SEAMS.md line-number pin drifts from the +1-line add.py growth (check `add.py check`/audit after the edit).

---

## 3 · CONTRACT — freeze the shape

```
_SCOPE_EXCLUDE_DIRS  += (".pytest_cache",)      # tuple constant, all 3 trees
_SCOPE_EXCLUDE_FILES += (".coverage",)          # tuple constant, all 3 trees
engine_pin.ENGINE_MD5 = <md5 of the new identical add.py bytes>
behavior: scope walk prunes .pytest_cache dirs at any depth and skips .coverage files; everything else unchanged
```

`Least-sure flag surfaced at freeze:` [test] the guard test asserts the constants' membership, not a full walk simulation — why: a walk-level test would need a scaffolded project; if wrong (membership present but walk ignores it): the walk already consumes these exact constants at its only call site (dirnames prune + file skip), read-verified; cost: none beyond re-read.
Status: FROZEN @ v1 — approved by Tin Dang (2026-07-07, the HARD-STOP resolution answer)

---

## 4 · TESTS — failing-first (red)

Plan: test_scope_excludes_test_caches — assert `.pytest_cache` ∈ _SCOPE_EXCLUDE_DIRS and `.coverage` ∈ _SCOPE_EXCLUDE_FILES in all 3 trees + trees byte-identical.
Tests live in: `add-method/tooling/` (test_scope_exclude_test_caches.py) · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/tooling/` `.add/tooling/`
Strategy & known-problem fixes: 1. red guard test 2. edit the two tuple constants in add-method/tooling/add.py 3. copy byte-identical to the 2 twins 4. recompute + update ENGINE_MD5 (engine_pin.py) 5. run guard + release-parity tests + add.py check. Trap: ceiling/SEAMS line pins drift on add.py growth — keep the edit zero-net-lines if possible (extend existing tuple lines in place).
Approach (domain strategy): obvious, correctness-first — additive tuple widening at the one documented seam; persona: methodology-engine-dev.
Strategy actually used: as planned, plus one trap hit and healed — the pin-update glob over-reached into `.claude/worktrees/*` checkouts and the gitignored dogfood twin `add-method/.add/`; worktrees restored via git checkout, dogfood twin re-pinned to its OWN add.py bytes (9be0267f). Lesson recorded at the gate.
Code lives in: `./src/`   ·   Constraints: change no test, no contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build (14/14 incl. release-parity; check 621/0)
- [x] green was EARNED — the guard asserts real module constants loaded from each tree's bytes; parity test md5s the real files
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP) — additive tuple widening only

Build expectations (from §1 Accept + §3 CONTRACT): guard test green in all 3 trees + `test_release_1_17_0` engine-parity green on the new pin + `add.py check` green — confirmed: 14/14 OK, check 621/0.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (HARD-STOP resolution = the approval) · date: 2026-07-07
OBSERVE: [ADD · open] a `**/engine_pin.py` glob is the wrong tool for the 3-tree pin update — it reaches sibling worktrees and the gitignored dogfood twin; enumerate the 3 canonical pins explicitly (evidence: this task's build healed 3 over-pinned files)

