# Phase 6 — Verify (evidence + non-functional review)

Goal: establish trust and record an outcome. Passing tests are necessary, not
sufficient. Fill **§6** in TASK.md including the GATE RECORD.

> **Who resolves this gate depends on the `autonomy:` header (see `run.md`).**
> Under `autonomy: auto` (the default) a run auto-PASSes once evidence is complete —
> every test green, convergence loops dry, and **no residue** (security · concurrency · architecture) —
> recorded as *auto-resolved* with the named run as accountable owner. **Security is
> always a HARD-STOP and is never auto-passed.** Under `autonomy: conservative`, or
> whenever residue is found, this phase is **human-led**.

## Before you build — declare the build expectations

Fill the §6 **Build expectations** block BEFORE Build: OBSERVABLE outcomes derived from §2 SCENARIOS + §3 CONTRACT. At this gate, confirm each against real evidence (the `confirmed by` column). An expectation with no evidence is not yet verified.

## Part one — confirm the evidence

- [ ] All tests pass.
- [ ] Coverage did not decrease.
- [ ] No test or contract was altered during build.
- [ ] Every §6 Build expectation is confirmed by real evidence (not just a green test).

If any is false, stop and return to Build.

## Part two — check what tests miss

- **Concurrency/timing** — correct when two run at once? (Tests run serially and miss races.)
- **Security** — exposed secrets, injection openings, unexpected dependencies. A security finding is always `HARD-STOP`, never a waiver. ANY note here escalates to the human — start it with `NOTE` or `⚠` so `add.py audit` can see it (`unescalated_security_note`).
- **Architecture** — respects layering/dependency rules in CONVENTIONS.md?

## Part three — the deep check (do not skim)

Deep check — do not skim. If the task produced code, record that every new symbol is referenced (wiring) and that no new dead/unused code was introduced. If it produced prose or non-code, record a semantic read — what you read in full and what it confirmed. Which path applies is the resolver's judgement; the engine never classifies.

Record it in the §6 **Deep checks** block. An unfilled Deep checks block is a **shallow verify**, not a PASS.

## Part four — was the green earned?

A green suite proves tests pass — not that the build EARNED them. Three judgment cheats pass the unchanged suite: src overfit to the test fixtures (special-cased to literal inputs), vacuous asserts (tautological — green against an empty implementation), and real logic stubbed away. These are invisible to the mechanical tamper tripwire. Score them with an adversarial refute-read: an independent reviewer — the engine never spawns one — prompted to argue the green was NOT earned. A confirmed earned-green failure is HARD-STOP-class: never auto-passed, never RISK-ACCEPTED — a first cheat enters the bounded self-heal loop (run.md).

## Record exactly one outcome (no silent pass)

When you present this gate, open with the ARC per `report-template.md`, render the DECISION as a guided choice, and reconcile FLAGS with `add.py report --decide`'s open-item count before the ask.

| Outcome | When |
|---------|------|
| `PASS` | all checks met |
| `RISK-ACCEPTED` | a **non-security** gap, with signed owner + ticket + expiry |
| `HARD-STOP` | any failing test or any security finding |

## Exit gate / Next

<exit_gate>
- [ ] Evidence confirmed, non-functional risks checked, outcome recorded — a person approved, or
  (under `autonomy: auto` with no residue) the run auto-resolved as the accountable owner.
</exit_gate>

> **Advisor · Confidence** — the earned-green refute-read is the canonical adversarial spawn (advisor.md); score the verdict before you record the gate (confidence.md).

```bash
python3 .add/tooling/add.py gate PASS          # marks the task done
# or: add.py gate RISK-ACCEPTED   |   add.py gate HARD-STOP (return to Build)
```
Then read `phases/7-observe.md`. Book: `docs/08-step-6-verify.md`.
