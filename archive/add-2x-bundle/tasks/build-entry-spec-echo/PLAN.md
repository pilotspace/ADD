# TASK: Build-entry spec echo: Must/Reject + contract summary at the tests->build tick

slug: build-entry-spec-echo · created: 2026-07-14 · stage: mvp
milestone: six-phase-loop
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; the observe note is one optional line at the gate.

---

## 1 · SPECIFY — the rules

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: build-entry spec echo — the tick INTO build re-renders WHAT to build (§1 Must/Reject + the frozen §3 contract head), so the builder starts from the spec on the screen, not from memory
Must:
  - a successful tests->build tick prints `build to (frozen plan):` then one `  must: <bullet first line>` per §1 Must bullet, one `  reject: <bullet first line>` per §1 Reject bullet, then `  contract: <first non-empty line inside the §3 Contract fence>`
  - the echo fires on BOTH build entries — `advance` (tests->build) AND the `phase build` admin override — because both funnel through _build_entry; it renders at the TAIL of the gate stack, after every guard + snapshot, so a refused entry never echoes
  - pure read, fail-open: state.json, TASK.md, and the exit code are byte-identical with or without the echo; the call is wrapped so any parse failure prints what parsed (possibly nothing) — never a die, never a traceback
Reject:
  - any echo failure blocking a build entry -> fail-open (wrapped; the tick completes and state is written exactly as before)
  - echo on a refused crossing (contract_not_frozen · build_expectations_unfilled · unflagged_freeze) -> never; validate-then-write puts every guard before it
Accept: Given a fast task with a frozen §3 and two Must + one Reject bullets, When `advance` ticks tests->build, Then stdout carries `build to (frozen plan):` + one line per bullet + the §3 fence head, and the tick's state/TASK.md writes match a pre-echo build entry.
Boundary: three §1/§3 shapes the echo must speak — well-formed (full echo) · missing/malformed Must/Reject block or contract fence (that part silently absent, no crash) · --skip-freeze DRAFT-§3 crossing (echo still renders whatever exists)
Assumptions: ⚠ no existing suite pins the exact stdout TAIL of a tests->build advance — why: prior fences grepped advance output via assertIn only; if wrong: the fence names the pinning suite and the echo line-shape adjusts (cost: one re-run)

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols): add-method/tooling/add.py:_build_entry (tail insert, after the spec-dialect loop) · add.py:_spec_echo (NEW pure-read helper, beside _scope_echo) · add.py:_raw_phase_bodies (read-only reuse)
Context (working folder): SEAMS.md `_declared_scope` pin (add.py:5603) drifts on this insertion — re-pin; ENGINE_MD5 + ENGINE_PKG_MD5 re-aim; engine syncs x3 twins
Honors (patterns / conventions): fail-open derived-render (mirrors _scope_echo's freeze call + the dialect warnings) · validate-then-write (echo strictly after every guard/snapshot) · Seams consulted: .add/SEAMS.md
Anchors the contract cites: _build_entry · _scope_echo · _raw_phase_bodies
Ground SHA: be74a90 — stamped by freeze

### Contract

```
_spec_echo(root: Path, slug: str) -> None      # NEW, PURE read — prints only, never writes
  renders, in order:
    build to (frozen plan):
      must: <first line of each §1 Must bullet>
      reject: <first line of each §1 Reject bullet>
      contract: <first non-empty line inside the §3 Contract fence>
  a missing/malformed section -> that part silently absent (never a die)
call site: TAIL of _build_entry (after the spec-dialect loop) — so BOTH entries
  (`advance` tests->build AND `phase build`) echo; wrapped
  try/except Exception -> pass (fail-open: exit code, state.json, and TASK.md
  are byte-identical with or without the echo)
```

`Least-sure flag surfaced at freeze:` [test] the byte-identity Must — proving state/TASK.md identical "with or without the echo" can't run two engines side by side; the test approximates it by forcing the helper to raise and asserting the tick still completes with identical state — why: monkeypatch is the only seam; if wrong: the assert re-shapes to behavioral-only (cost: one test rewrite, no engine change)
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/tooling/` `.add/tooling/` `add-method/.add/`
Strategy & known-problem fixes: 1) red test_build_entry_spec_echo.py 2) _spec_echo helper beside _scope_echo (regex over _raw_phase_bodies bodies 1+3) 3) wrapped tail call in _build_entry 4) sync engine x3 · re-pin ENGINE_MD5/PKG · check SEAMS line-pin drift (add.py grows ~40 lines) 5) full fence backgrounded; trap: the §1 Must/Reject parse must stop at the next top-level `Key:` line, not swallow Accept/Boundary
Approach (domain strategy): derived-render tail print over already-parsed section bodies — obvious, correctness-first

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS — failing-first (red)

Plan: test_build_entry_spec_echo.py — echo at `advance` tests->build (must/reject/contract lines, in order, after the gate stack's own output) · echo at the `phase build` override · fail-open (helper forced to raise -> tick completes, state written) · malformed §1/§3 -> partial echo, no crash · refused crossing (DRAFT §3, no skip) -> no echo · engine-twin parity.
Tests live in: `add-method/tooling/test_build_entry_spec_echo.py` (the engine's own suite; the file named exactly — the dir form swept the build targets into the tamper snapshot) · MUST run red before Build.

---

## 5 · BUILD — AI writes the code (execution)

> The change plan was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope; improve on the strategy if the code teaches you better.
Strategy actually used: as planned — _spec_echo beside _scope_echo (bullet walk stops at the next top-level `Key:` line, the noted trap), wrapped tail call after the dialect loop; ENGINE_MD5 re-aimed bf89b033, ENGINE_PKG_MD5 correctly NOT re-aimed (add_engine/ untouched), SEAMS _declared_scope pin 5603->5653
Code lives in: `./src/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build
- [x] green was EARNED — no overfit / vacuous asserts / stubbed-away logic
- [x] input dialect held — tests speak the spec's example formats (spec-dialect floor)
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP)

Build expectations (from §1 Accept + §3 CONTRACT): a tests->build tick on a task with a frozen §3 prints `build to (frozen plan):` + one must/reject line per §1 bullet + the contract fence head, on both the advance and `phase build` paths, and a forced echo failure never blocks the tick — confirmed by test_build_entry_spec_echo.py + the full fence

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-14

