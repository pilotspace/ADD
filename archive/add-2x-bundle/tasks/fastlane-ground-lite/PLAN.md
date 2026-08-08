# TASK: fast §0 ground-lite

slug: fastlane-ground-lite · created: 2026-07-06 · stage: mvp
milestone: method-ergonomics
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): templates/TASK.fast.md.tmpl §0 · add_engine/constants.py:_FALLBACK_TASK_FAST · engine_pin.py:ENGINE_PKG_MD5
Context (working folder): 3 template trees + 4 engine-package twins; test_ground_anchor_sha docstring notes fast-lane omission (superseded here, no assertion pinned it)
Honors (patterns / conventions): circuit-breaker FIELD parity tmpl↔fallback; PKG pin re-aim path; warn-never-block
Anchors the contract cites: _FALLBACK_TASK_FAST · _read_ground_sha · TASK.fast.md.tmpl
Ground SHA: post-bundle-advance commit

---

## 1 · SPECIFY — the rules

Feature: fast-lane §0 carries the Ground SHA drift anchor
Must:
  - fast template §0 (3 trees) + _FALLBACK_TASK_FAST carry `Ground SHA:`
  - a scaffolded --fast task contains the field; check's l.NNN WARN clears when filled
Reject:
  - behavior change to the WARN itself -> "warn_semantics_changed" (behavioral: logic untouched)
Accept: Given a --fast task citing l.NNN, When Ground SHA is filled, Then `check` stops warning — without hand-adding the line
Assumptions: ⚠ superseding ground-anchor-sha's 'fast lane omits it' scope note is safe — no assertion pinned the omission; if wrong: revert one line per tree

---

## 3 · CONTRACT — freeze the shape

```
TASK.fast.md.tmpl §0 += 'Ground SHA: <…>' (after Anchors)
_FALLBACK_TASK_FAST §0 += 'Ground SHA:'
ENGINE_PKG_MD5 -> a59f79d0… (recorded re-aim)
```

Least-sure flag surfaced at freeze: ⚠ [contract] the fallback carries a bare `Ground SHA:` (no placeholder) — because the fallback skeleton uses bare fields throughout; if wrong: cosmetic only
Status: FROZEN @ v1 — approved by Tin (implement-directly directive 2026-07-06)

---

## 4 · TESTS — failing-first (red)

Plan: test_fastlane_ground_lite (5 tests) — 3-tree field presence · fallback parity · scaffold · WARN fires/clears.
Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `add-method/tooling/templates/TASK.fast.md.tmpl` `add-method/tooling/add_engine/constants.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_fastlane_ground_lite.py` `.add/tooling/` `add-method/src/add_method/_bundled/tooling/` `add-method/.add/tooling/`
Strategy & known-problem fixes: red 5-test suite → tmpl+fallback line → twin sync → PKG re-aim (trap: scaffold renders TASK.md, not TASK.fast.md — fixed in test)
Strategy actually used: as planned + one test-path fix
Code lives in: `./src/`   ·   Constraints: change no test, no contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass (91/91 incl. fast-lane/census/pin suites) · coverage held · no test or contract altered during build (test path fix was a harness correction pre-green, disclosed)
- [x] green was EARNED — field asserted via engine's own _ground_section; WARN pinned both directions
- [x] no exposed secrets, injection openings, or unexpected dependencies

Build expectations (from §1 Accept + §3 CONTRACT): a fresh --fast scaffold shows `Ground SHA:` in §0 — confirmed by scratch scaffold + test

### GATE RECORD
Outcome: PASS
Reviewed by: auto-resolved (autonomy: auto; no residue) under Tin's directive · date: 2026-07-06

