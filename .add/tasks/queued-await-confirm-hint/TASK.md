# TASK: queued + await-confirm prints the milestone-confirm reminder

slug: queued-await-confirm-hint · created: 2026-06-26 · stage: mvp
autonomy: auto
phase: done   <!-- fast lane: ground -> specify -> contract -> tests -> build -> verify -> observe -> done -->
fast: true   <!-- the fast lane: a small task, collapsed flow + minimal template. Omit --fast for full rigor. -->

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols):
- `add-method/tooling/add.py:cmd_new_milestone` (~2477) — the output block. The `await_confirm` reminder (`(unconfirmed — show the MILESTONE.md, then: add.py milestone-confirm <slug>)`) is appended ONLY in the `else` (active) branch (2480-2481). The `if queued:` branch (2478) prints just the promote hint → a `--queued --await-confirm` milestone records the gate (`await_confirm=True, confirmed=False`, 2471) but never reminds the user. ADD the reminder to the queued branch too.
- `add-method/src/add_method/_bundled/tooling/add.py` + `.add/tooling/add.py` — engine 3-tree mirror (byte-identical); ENGINE_MD5 re-pinned.
- `add-method/tooling/engine_pin.py:ENGINE_MD5` (13) — re-aim the pin (canonical-only, not mirrored).
Context (working folder): `test_milestone_queued_state.py` is the natural sibling for the new red test (or a small new fast-task test); the milestone-confirm gate state shape (`await_confirm`/`confirmed`) is set at 2471, unchanged.
Honors (patterns / conventions): **additive / byte-identical default** — the new line prints ONLY when `queued AND await_confirm` (a combo that today yields just the plain queued line); all other paths byte-unchanged. **Engine 3-tree mirror + ENGINE_MD5 re-pin**. **Never silently gate** — the reminder makes the already-recorded confirm gate visible.
Anchors the contract cites: cmd_new_milestone queued+await_confirm output · the milestone-confirm reminder text · ENGINE_MD5 re-pin + 3-tree mirror.

---

## 1 · SPECIFY — the rules

Feature: when a milestone is created with BOTH `--queued` and `--await-confirm`, the output surfaces the `milestone-confirm` reminder (so the recorded confirm gate is visible), not just the promote hint.
Must:
  - `new-milestone --queued --await-confirm <slug>` prints the promote hint AND a reminder that the milestone is unconfirmed / needs `milestone-confirm` after promotion.
  - `new-milestone --queued <slug>` (no --await-confirm) is BYTE-IDENTICAL to today (only the promote hint; no reminder).
  - active-branch output (with/without --await-confirm) is unchanged; engine mirror byte-identical + ENGINE_MD5 re-pinned.
Reject:
  - emitting the reminder when `await_confirm` is False -> "not_byte_identical" (additive-only contract)
Accept: Given `--queued --await-confirm beta`, When new-milestone runs, Then stdout contains the promote hint AND a "milestone-confirm beta" reminder; AND with `--queued` alone, stdout has NO "milestone-confirm" text.
Assumptions: none material — biggest risk: wording drift between the active-branch reminder and the new queued-branch reminder; the test asserts the stable token `milestone-confirm <slug>`, not the full phrase.

---

## 3 · CONTRACT — freeze the shape

```
add.py new-milestone --queued --await-confirm <slug>   (output-only change; no new args, no new state)
  WHEN queued AND await_confirm:
    stdout += "  (unconfirmed — after promote: add.py milestone-confirm <slug>)"   (after the promote hint)
  WHEN queued AND NOT await_confirm:  → byte-identical to today (promote hint only)
  active branch (queued False): UNCHANGED
Invariant: additive-only — reminder prints iff (queued AND await_confirm); engine 3-tree byte-identical + ENGINE_MD5 == md5(add.py).
State: writes NOTHING new (await_confirm/confirmed already recorded at creation).

v2 AMENDMENT (change request, approved): re-pinning the engine breaks the merged test
test_roadmap_intake_guide.test_engine_unchanged, which HARDCODES the prior pin e81bef8b — the exact
fv54 TDD lesson recurring. Fix per that lesson: change its assertion from `== "<literal>"` to
`== md5(add.py)` (self-relative) — a STRONGER invariant (a stale pin is the real bug), already
redundant with two other self-relative pin tests. Adds test_roadmap_intake_guide.py to §5 scope.
```

`Least-sure flag surfaced at freeze:` [contract] reminder wording for the queued branch — I use "after promote: add.py milestone-confirm <slug>" (vs the active branch's "show the MILESTONE.md, then: …") because for a queued milestone confirm happens after promotion. If wrong: a second wording to reconcile later. Low cost (test keys on the stable `milestone-confirm <slug>` token).
Status: FROZEN @ v2 — approved by Tin Dang (2026-06-26); v1 queued-branch wording "after promote" + v2 self-relative pin fix (fv54 lesson applied)
<!-- The freeze IS the one approval. Approved -> Status: FROZEN @ vN — approved by <name>.
     Changing a frozen contract = change request back to SPECIFY. -->

---

## 4 · TESTS — failing-first (red)

Plan: test_<accept> — assert the §1 Accept line's Then (behavior, not internals).
Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `add-method/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `.add/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_queued_await_confirm_hint.py` `add-method/tooling/test_roadmap_intake_guide.py`
Code lives in: cmd_new_milestone output block (add.py ×3) + the pin + the new red test + (v2) the self-relative pin fix in test_roadmap_intake_guide.py.   ·   Constraints: change no OTHER test, no contract; additive output only; the only pre-existing test touched is test_roadmap_intake_guide (v2 amendment, self-relative pin); allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build — full suite 2017/0; check 424/0. All edits (test, fix, propagate, re-pin, v2 self-relative pin fix) happened in the tests phase BEFORE the tests→build snapshot; build phase made no edits (tripwire clean). The only pre-existing test touched (test_roadmap_intake_guide) is the v2-amended scope item.
- [x] green was EARNED — the test drives real `new-milestone` via captured stdout: asserts the reminder token `milestone-confirm beta` is present WITH --await-confirm (red until built) and ABSENT with --queued alone; plus the gate state (await_confirm/confirmed) is recorded, and ENGINE_MD5 == md5(add.py). Visually confirmed both output paths in a throwaway demo.
- [x] no exposed secrets, injection openings, or unexpected dependencies — none; output-only change, zero new deps

Build expectations (from §1 Accept + §3 CONTRACT): `new-milestone --queued --await-confirm beta` prints `promote it with: add.py activate beta` AND `(unconfirmed — after promote: add.py milestone-confirm beta)`; `new-milestone --queued gamma` prints only the promote hint (no milestone-confirm) — BOTH confirmed in the live /tmp demo. Engine: 3 add.py copies md5 f97eed6d…, ENGINE_MD5 == md5(add.py), pin re-aimed.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (contract approved @ freeze v1; v2 amendment human-approved via change-request; verify auto-gated on complete evidence under autonomy:auto) · date: 2026-06-26
OBSERVE: [TDD · applied] the fv54 hardcoded-pin lesson recurred on the very next engine task and is now FIXED at root — test_roadmap_intake_guide's pin guard is self-relative (`== md5(add.py)`), so no future engine task needs a literal bump. Standalone fast task (todo #15 / PR#98 Finding 1).
