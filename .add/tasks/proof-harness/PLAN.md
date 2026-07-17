# TASK: Prove the engine enforces the gate guardrails the book promises

slug: proof-harness · created: 2026-05-29 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

The book PROMISES guardrails the engine does not yet enforce. The proof-harness is
the executable layer that makes those promises checkable — and the build closes the
one real divergence it surfaces (gate PASS can skip verify).

Must:
  - `add.py gate PASS` succeeds ONLY when the task has reached the `verify` phase
    (index ≥ verify in PHASES: verify, observe, done). This makes principle 7
    ("no silent skips") and Matrix 3 ("done only when Verify reads PASS") true in
    the engine, not just the prose.
  - The explicit `add.py phase <name>` command remains a deliberate, recorded
    escape hatch — it may set ANY phase (the human override; honest because it is
    logged in state + TASK.md marker). The guardrail bans the *silent* skip via
    `gate`, never the deliberate one via `phase`.
  - `HARD-STOP` and `RISK-ACCEPTED` outcomes remain recordable from ANY phase — a
    security finding is ALWAYS HARD-STOP and can occur mid-build (book invariant).
  - The book's three gate OUTCOMES (PASS · RISK-ACCEPTED · HARD-STOP) match the
    engine's GATES exactly (minus the internal sentinel `none`) — Story↔State agree.
Reject:
  - `gate PASS` while phase ∈ {specify, scenarios, contract, tests, build}
    -> "gate_pass_before_verify" (SystemExit, exit 1 via _die; engine refuses, state unchanged)
After:
  - the engine cannot fast-forward a task to `done` without passing through verify;
    each guarded behavior is pinned by a test mapped to a requirements-matrix row.
Assumptions (confirm before building):
  - [x] add.py is the enforcement point for THIS invariant (not deferred to CI):
        "no silent skips" is a core method invariant (principle 7), distinct from
        principle 8's gate-depth enforcement which CI owns. CONFIRMED with author.
  - [x] Escape hatch = the existing `phase` command; no new flag. CONFIRMED.

<!-- EXIT: every rule stated, every rejection has a named code, zero open assumptions. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: gate PASS is refused before verify  (the divergence the harness surfaces)
  Given a fresh task at phase "specify"
  When I run `gate PASS`
  Then the engine exits non-zero with "gate_pass_before_verify"
  And the task phase is still "specify" and gate is still "none"   # state unchanged

Scenario: gate PASS at verify reaches done  (the happy path of the guardrail)
  Given a task advanced to phase "verify"
  When I run `gate PASS`
  Then the task phase becomes "done" and gate becomes "PASS"

Scenario: phase is the deliberate escape hatch
  Given a fresh task at phase "specify"
  When I run `phase verify` then `gate PASS`
  Then the task reaches "done"   # explicit, logged override is allowed

Scenario: HARD-STOP is recordable mid-build
  Given a task at phase "build"
  When I run `gate HARD-STOP`
  Then gate becomes "HARD-STOP" and phase stays "build"   # security finding anytime

Scenario: the book's gate outcomes match the engine
  Given the engine constant GATES and the glossary's gate-outcome terms
  When I compare them
  Then PASS, RISK-ACCEPTED, HARD-STOP appear in both   # Story↔State agree
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

Engine signature change (the only behavior change):
```
cmd_gate(args):
  if args.outcome == "PASS" and phase_index(current) < phase_index("verify"):
      _die("gate_pass_before_verify")        # SystemExit(1) via _die default; state NOT written
  # NOTE: contract corrected v1->v1.1 — exit code is 1 (the _die default + repo
  # convention, cf. check's exit 1), not 2. Caught by reading _die before build;
  # recorded as a backward correction, not a silent edit.
  # unchanged otherwise: record outcome, PASS -> phase "done"
```
Helper (new, pure): `_phase_index(name) -> int` = PHASES.index(name). No new command,
no new flag, no state-schema change. `phase`, HARD-STOP, RISK-ACCEPTED unchanged.

Proof tests (each pinned to a requirements-matrix row — the executable "what proves it"):
```
test_gate_pass_refused_before_verify   -> Matrix 3 / principle 7 (no silent skips)
test_gate_pass_at_verify_reaches_done  -> Matrix 3 (done only when Verify reads PASS)
test_phase_override_escape_hatch       -> SPECIFY escape-hatch rule (deliberate ≠ silent)
test_hardstop_recordable_mid_build     -> book invariant: security finding ALWAYS HARD-STOP
test_book_gate_outcomes_match_engine   -> Story↔State consistency (GATES vs glossary)
```
Tests live in: `add-method/tooling/test_proof_harness.py`.
Existing test rewritten (NOT weakened): `test_gate_pass_marks_done` must advance to
verify before `gate PASS` — it currently encodes the divergence; the rewrite encodes
the guardrail. Recorded as a deliberate change, not a silent edit.

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit)   <!-- changing the error code / signature = change request back to SPECIFY. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: the 5 scenarios above (behavioral; the guardrail branch in cmd_gate).
Plan (one test per scenario, asserting behavior not internals):
  - test_gate_pass_refused_before_verify: init+new-task (phase specify); assert
    `gate PASS` raises SystemExit AND state phase=="specify", gate=="none".
  - test_gate_pass_at_verify_reaches_done: advance to verify; `gate PASS`; assert done/PASS.
  - test_phase_override_escape_hatch: `phase verify` then `gate PASS`; assert done.
  - test_hardstop_recordable_mid_build: `phase build`; `gate HARD-STOP`; assert phase=="build".
  - test_book_gate_outcomes_match_engine: assert {PASS,RISK-ACCEPTED,HARD-STOP} ⊆ GATES
    AND each appears in the shipped glossary.

Tests live in: `add-method/tooling/test_proof_harness.py` · MUST run red (test 1 fails:
engine currently allows the skip) before Build. Also: rewrite test_add.py
`test_gate_pass_marks_done` to advance to verify first (recorded change).

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — 74/74 OK (69 prior + 5 proof-harness); `add.py check` 41/0
- [x] coverage did not decrease — net +5 tests; the new cmd_gate branch is covered
- [~] no test altered to fake a pass — tests WERE changed, but to encode the
      guardrail, not weaken it. Contract authorized rewriting test_gate_pass_marks_done;
      BUILD found the blast radius wider — 4 milestone/archive scaffolding sites
      gated PASS from specify. Each now uses the deliberate `phase verify` escape
      hatch (same assertions, honest path). Recorded here, not silently patched.
- [x] contract honored — only deviation is the v1->v1.1 exit-code correction (2->1),
      itself a recorded backward correction caught by reading `_die` before build
- [x] no concurrency risk — `gate` is a single synchronous state write; guard runs
      before any mutation and `_die` raises before `save_state` (state untouched on refusal)
- [x] no exposed secrets / no new dependencies — stdlib only; `_phase_index` is pure
- [x] layering follows CONVENTIONS.md — guard lives in cmd_gate beside its siblings
- [x] engine change propagated to .add/tooling/add.py (md5-identical); matrix doc to all 3 trees
- [x] a person reviewed and approved the change — author review below

### GATE RECORD
Outcome: PASS
Note: The proof-harness did its job — it surfaced a real Story↔State divergence
(`gate PASS` skipped verify) and the build closed it. Test changes are recorded
above as guardrail-encoding, not weakening (no silent skip). One contract exit-code
correction recorded (v1->v1.1).
Reviewed by: Tin Dang (author) · date: 2026-05-29

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): does any future command reach `done` without
passing `verify`? The proof-harness is the standing monitor — CI fails if it regresses.
Spec delta for the next loop: a CONCRETE next divergence is already known — `gate
RISK-ACCEPTED` records the outcome but leaves phase at `verify` (never `done`), so a
risk-accepted task cannot complete its milestone, and the waiver fields (owner ·
ticket · expiry) are not captured. Matrix 3 says done = "PASS (or a signed
RISK-ACCEPTED)" — same divergence as PASS, one outcome over. Deferred to its own
decision (done-transition + waiver schema deserve an AskUserQuestion), NOT folded
into T2. The proof-harness pattern — book-claim → engine-enforces → named test — is
reusable; T4 (minimalism-audit) should audit the rest of the matrix the same way.
