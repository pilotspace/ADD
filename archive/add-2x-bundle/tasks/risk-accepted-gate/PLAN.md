# TASK: RISK-ACCEPTED completes a task with a signed waiver (owner/ticket/expires)

slug: risk-accepted-gate · created: 2026-05-29 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Closes the known gap T2 surfaced: Matrix 3 says a task is done when Verify reads
"PASS (or a signed RISK-ACCEPTED)", but the engine advanced only PASS to done.
Decisions confirmed with the author via AskUserQuestion (see Assumptions).

Must:
  - `gate RISK-ACCEPTED` advances the task to `done` (like PASS) — making Matrix 3's
    "(or a signed RISK-ACCEPTED)" true in the engine, so a waived task can complete
    its milestone.
  - `gate RISK-ACCEPTED` requires the task to have reached `verify` (the SAME guard
    as PASS — a waiver is a verify-step outcome). HARD-STOP stays recordable anywhere.
  - A waiver is SIGNED: `gate RISK-ACCEPTED` requires `--owner`, `--ticket`,
    `--expires`; all three are stored in state.json under the task so a later
    `check` can read/expire them (capture now; expiry-enforcement is future work).
Reject:
  - `gate RISK-ACCEPTED` while phase < verify -> "gate_risk_accepted_before_verify"
    (SystemExit 1; state unchanged). [PASS keeps its T2 code "gate_pass_before_verify".]
  - `gate RISK-ACCEPTED` missing any of owner/ticket/expires -> "waiver_incomplete"
    (SystemExit 1; state unchanged — no partial waiver recorded).
After:
  - a verify-phase task gated RISK-ACCEPTED with a full waiver is `done`, gate=
    RISK-ACCEPTED, and state.tasks[slug].waiver = {owner, ticket, expires}.
Assumptions (confirm before building):
  - [x] Completion: RISK-ACCEPTED → done, same verify-guard as PASS. CONFIRMED (AskUserQuestion).
  - [x] Waiver fields: require all three (--owner/--ticket/--expires), refuse without,
        store in state.json. CONFIRMED (AskUserQuestion).
  - [x] "non-security gaps only" (glossary) stays a documented human rule — the engine
        cannot detect a security gap, so it is NOT mechanically enforced here.

<!-- EXIT: every rule stated, every rejection has a named code, zero open assumptions. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: RISK-ACCEPTED is refused before verify
  Given a fresh task at phase "specify"
  When I run `gate RISK-ACCEPTED --owner a --ticket T-1 --expires 2026-12-31`
  Then the engine exits non-zero with "gate_risk_accepted_before_verify"
  And the task phase is still "specify" and gate is still "none"   # state unchanged

Scenario: RISK-ACCEPTED is refused without a full waiver
  Given a task at phase "verify"
  When I run `gate RISK-ACCEPTED` with no waiver flags
  Then the engine exits non-zero with "waiver_incomplete"
  And the task phase is still "verify" and gate is still "none"    # no partial waiver

Scenario: RISK-ACCEPTED with a partial waiver is refused
  Given a task at phase "verify"
  When I run `gate RISK-ACCEPTED --owner a --ticket T-1` (no --expires)
  Then the engine exits non-zero with "waiver_incomplete"
  And the task phase is still "verify"                            # all three required

Scenario: a signed RISK-ACCEPTED at verify completes the task
  Given a task at phase "verify"
  When I run `gate RISK-ACCEPTED --owner a --ticket T-1 --expires 2026-12-31`
  Then the task phase becomes "done" and gate becomes "RISK-ACCEPTED"
  And state.tasks[slug].waiver == {owner: a, ticket: T-1, expires: 2026-12-31}
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

CLI surface (the `gate` subparser gains three optional flags):
```
add.py gate RISK-ACCEPTED <slug?> --owner <str> --ticket <str> --expires <str>
  refuse "gate_risk_accepted_before_verify"  if phase_index(current) < phase_index("verify")
  refuse "waiver_incomplete"                  if any of owner/ticket/expires missing
  else -> phase="done", gate="RISK-ACCEPTED",
          state.tasks[slug].waiver = {owner, ticket, expires}
```
Engine shape (cmd_gate, extends the T2 guard — NOT a rewrite of it):
  - completing outcomes = {PASS, RISK-ACCEPTED} share the verify-phase guard; the
    error code is per-outcome (PASS keeps "gate_pass_before_verify" from T2).
  - waiver validation + storage applies ONLY to RISK-ACCEPTED.
  - HARD-STOP unchanged (recordable anywhere; never advances to done).
  - --expires is stored verbatim (string); date-format validation + expiry checking
    are deferred (out of scope — captured for a later `check`).

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit)   <!-- changing an error code / a required flag = change request back to SPECIFY. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: the 4 scenarios above (the new RISK-ACCEPTED branch in cmd_gate).
Plan (one test per scenario, asserting behavior not internals):
  - test_risk_accepted_refused_before_verify: specify; gate RA + full waiver; assert
    SystemExit AND phase=="specify", gate=="none".
  - test_risk_accepted_requires_waiver: phase verify; gate RA, no flags; assert
    SystemExit AND phase=="verify", gate=="none", no "waiver" key in state.
  - test_risk_accepted_partial_waiver_refused: phase verify; gate RA --owner --ticket
    (no --expires); assert SystemExit AND phase=="verify".
  - test_risk_accepted_complete_reaches_done: phase verify; gate RA + all three;
    assert phase=="done", gate=="RISK-ACCEPTED", waiver=={owner,ticket,expires}.
  - [added in verify, see below] test_milestone_done_accepts_a_waived_task &
    test_check_tolerates_a_recorded_waiver: the HEADLINE — a waived task completes
    its MILESTONE end-to-end (milestone-done + check over a real waiver-bearing state).

Tests live in: `add-method/tooling/test_waiver.py` · MUST run red (the flags + branch
don't exist yet) before Build. T2's test_proof_harness stays untouched (regression guard).

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — 78/78 OK (74 + 4 waiver); `add.py check` 44/0
- [x] coverage did not decrease — net +4 tests; the new RISK-ACCEPTED branch is covered
- [x] no test or contract altered to fake a pass — test_proof_harness (T2) untouched and
      still green = regression guard; only NEW test_waiver.py added; no frozen contract changed
- [x] no concurrency risk — single synchronous state write; both `_die`s (verify-guard,
      waiver_incomplete) raise before `save_state`, so a refusal leaves state untouched
- [x] no exposed secrets / no new dependencies — stdlib only; flags are plain strings
- [x] layering follows CONVENTIONS.md — logic stays in cmd_gate; symmetric with the PASS guard
- [x] engine propagated to .add/tooling/add.py (md5-identical); Matrix 4 to all 3 trees
- [x] glossary already named the waiver fields (owner · ticket · expiry) — names match, no drift
- [x] a person reviewed and approved the change — author review below

### GATE RECORD
Outcome: PASS
Note: Clean feature, tests green — PASS (no risk to accept here; the irony is noted).
Both design forks (completion → done with verify-guard; require all three waiver fields)
were decided by the author via AskUserQuestion before SPECIFY froze. Closes the Matrix 4
"Known gap" T2 surfaced.
Reviewed by: Tin Dang (author) · date: 2026-05-29

BACKWARD CORRECTION (post-gate, advisor-caught — recorded, not silent):
The SPECIFY Must says the point of the waiver is "so a waived task can COMPLETE ITS
MILESTONE", but the first build only made `gate RISK-ACCEPTED` reach phase `done` —
it never proved the milestone half, and the green suite hid the gap. A post-build
advisor verify pass found the shared completeness predicate `_task_done` still counted
only `PASS`, so a waived task reached `done` yet silently blocked `milestone-done`,
`ready` (deps), `check` and `archive`. Fix (one point): `_task_done` now counts a
signed `RISK-ACCEPTED`; the misleading "(N tasks all PASS)" milestone message now reads
"complete (N via a signed RISK-ACCEPTED waiver)". Pinned red-first by the two end-to-end
tests above. Lesson (feeds OBSERVE): proving the TASK completes is not proving the
MILESTONE can — assert the headline outcome, not the nearest mechanism. Suite 80/80 OK.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): are waivers ever recorded with an --expires in
the past? The fields are now captured but NOT yet expiry-checked.
Spec delta for the next loop: the natural follow-on is teaching `add.py check` to flag
an expired waiver (a RISK-ACCEPTED whose --expires has passed) — capture is done here,
enforcement is the next loop. Feeds T4 (minimalism-audit) and the standing matrix audit.
