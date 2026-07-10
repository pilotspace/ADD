# TASK: Benchmark ADD arm stops at the delivered+verified gate (drop the milestone-ledger tail from measured cost)

slug: harness-fair-meter · created: 2026-07-09 · stage: mvp
milestone: three-phase-flow
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): `benchmark/runner/core.py:_wrap_prompt` — the "add-loop" branch builds the prompt string the ADD-arm agent receives; today it says "drive this repo's ADD loop for the whole job" + "the job is done only when the app meets the requirements", which the headless agent read as license to also run the milestone-ledger close-out (`milestone-done`/`fold`/`archive-milestone`) AFTER the app was delivered+verified. · `benchmark/tests/test_adherence_census.py:TestAddLoopWrapper` — the string-assert tests over `_wrap_prompt`.
Context (working folder): `benchmark/THREE-PHASE-FLOW-PROOF.md` (documents the measured 29% asymmetry this closes: ADD run turns 127→163 = milestone ceremony spec-kit never does) · `benchmark/BENCHMARK.md` (harness contract).
Honors (patterns / conventions): the wrapper is PROSE, tested by substring asserts (mirror `test_add_loop_prefixes_instruction`); no runner code depends on milestone-done/fold/archive (verified: `grep -rn` in benchmark/runner finds only unrelated comment hits) — the oracle checks `app_reachable`, not milestone state, so stopping at the gate cannot break scoring.
Anchors the contract cites: `_wrap_prompt` "add-loop" branch string.
Ground SHA: 3b3a4da

---

## 1 · SPECIFY — the rules

Feature: the benchmark ADD arm meters FEATURE-DELIVERY cost only — it stops at the recorded verify gate, not through the milestone-ledger close-out (symmetric with spec-kit, which has no milestone ledger).
Must:
  - the `add-loop` wrapper instructs the agent to FINISH once the app meets the requirements AND the verify gate is recorded.
  - the `add-loop` wrapper explicitly instructs the agent NOT to run `milestone-done`, `fold`, or `archive-milestone` in a benchmark run.
  - the wrapper KEEPS the existing floor instructions: `add.py status` first, contract FROZEN + red suite before app code, proxy authority, record the verify gate.
Reject:
  - any wrapper other than "add-loop" is altered -> unknown/`raw` wrappers must still pass the text through VERBATIM (guards spec-kit's arm).
Accept: `_wrap_prompt("<wl>", "add-loop")` contains a stop-at-the-recorded-verify-gate instruction AND names milestone-done/fold/archive as NOT to be run, while still containing `add.py status`, `frozen`, `red`, and `proxy authority`; `_wrap_prompt("x","no-such-wrapper") == "x"` unchanged.
Assumptions: ⚠ that a benchmark ADD run legitimately omits milestone-done/fold/archive — those are amortized project-lifecycle overhead, not per-feature delivery cost, and the WM-scoped benchmark measures per-feature delivery; if wrong (the ledger close-out is deemed part of "delivering the milestone"), the fix is instead to have spec-kit do equivalent close-out — but no runner code needs the ledger, so this is low-risk.
   (or "none material — biggest risk: X")

---

## 3 · CONTRACT — freeze the shape

```
_wrap_prompt(text, "add-loop") -> str   (benchmark/runner/core.py)
The returned string MUST contain, in addition to the existing floor tokens:
  • a STOP-boundary instruction: finish once the app meets the requirements AND
    the verify gate is recorded — do NOT run milestone-done / fold /
    archive-milestone (the milestone-ledger close-out) in a benchmark run.
Existing tokens PRESERVED (unchanged asserts): "add.py status", "frozen",
  "red", "proxy authority", and the fast-lane "--oneshot" + "scenarios"/"observe".
Ends with `text` verbatim (assert out.endswith(text)).
Non-"add-loop" wrapper: unchanged — _wrap_prompt("x","no-such-wrapper") == "x".

New test (RED first): test_add_loop_stops_at_gate — asserts the returned string
names "milestone-done" (or the ledger close-out) as NOT-to-run AND mentions the
verify gate as the finish boundary; existing wrapper asserts still pass.
```

`Least-sure flag surfaced at freeze:` [spec] whether omitting the milestone-ledger close-out is the fair meter boundary (vs having spec-kit do equivalent close-out) — chosen because the WM-scoped benchmark measures per-feature delivery and no runner code depends on the ledger; if wrong, symmetrize the other direction instead (spec-kit close-out), a one-arm wrapper change, this contract's Musts unaffected.
Status: FROZEN @ v1 — approved by Tin Dang

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §0 GROUND anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 CONTRACT shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS — failing-first (red)

Plan: `test_add_loop_stops_at_gate` (test_adherence_census.py::TestAddLoopWrapper) — asserts the add-loop string names milestone-done/fold/archive as NOT-to-run + the "verify gate" finish boundary, preserves add.py-status/frozen/red + endswith(text). RED confirmed.
Tests live in: `benchmark/tests/test_adherence_census.py` · ran RED before build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `benchmark/runner/core.py` `benchmark/tests/test_adherence_census.py`
Strategy & known-problem fixes: <ordered build steps · the trap each known problem must dodge · let the active persona's domain stance (or "generic") shape the approach, not just patterns>
Approach (domain strategy): <technique · shapes · pattern · optimization stance in one line, in the task's domain vocabulary — or "obvious, correctness-first">
Strategy actually used: as planned — appended one stop-boundary sentence to the add-loop wrapper string ("Finish the run once the app meets the requirements and the verify gate is recorded — do NOT run milestone-done, fold, or archive-milestone…"); no runner/scoring code touched; only benchmark/runner/core.py + the new test.
Code lives in: `./src/`   ·   Constraints: change no test, no contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass (126/126 benchmark suite) · coverage held · no test or contract altered during build
- [x] green was EARNED — test ran RED (`milestone-done` absent) before the wrapper edit; asserts check observable wrapper content, not internals
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP) — prose-only wrapper change, no runner/scoring/IO code touched

Build expectations (from §1 Accept + §3 CONTRACT): the add-loop wrapper string contains the stop-at-verify-gate + do-not-run-milestone-done/fold/archive instruction while keeping every prior floor token — confirmed by `test_add_loop_stops_at_gate` GREEN + the existing `test_add_loop_prefixes_instruction`/`test_add_loop_instructs_benchmark_skip` still GREEN, full benchmark suite green.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-gated on complete evidence — mechanical wrapper-prose change, autonomy auto) · date: 2026-07-09
[SPEC · open] a benchmark must meter identical work-boundaries across arms (feature-delivered gate), never one arm's full lifecycle vs another's minimal flow — evidence: the 29% milestone-ceremony asymmetry this task closes.

