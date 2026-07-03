# Phase 6 — Verify (evidence + non-functional review)

Goal: establish trust and record an outcome. Passing tests are necessary, not
sufficient. Fill **§6** in TASK.md including the GATE RECORD.

> **Who resolves this gate depends on the `autonomy:` header.** Under `autonomy: auto` (the default)
> a run auto-PASSes on complete evidence with **no residue** (security · concurrency · architecture),
> recorded *auto-resolved* with the named run as owner;
> **security is always a HARD-STOP and is never auto-passed**. Under `conservative`, or whenever
> residue is found, this phase is **human-led** (auto-PASS conditions: `run.md`).

## Before you build — declare the build expectations

Fill the §6 **Build expectations** block BEFORE Build: OBSERVABLE outcomes derived from §2 + §3. At this gate, confirm each against real evidence (the `confirmed by` column) — one with no evidence isn't yet verified.

## Part one — confirm the evidence

- [ ] All tests pass.
- [ ] Coverage did not decrease.
- [ ] No test or contract was altered during build.
- [ ] Every §6 Build expectation is confirmed by real evidence (not just a green test).
- [ ] §1 rules trace to §2/§4 — an untraced rule is a coverage gap (`add.py audit`'s `rule_coverage_gap`; `check` has detail).
- [ ] every §3-cited symbol still resolves in the CURRENT tree, not just Ground SHA (§6 Live-verify evidence catches a stale/moved anchor here, not later).

If any is false, stop and return to Build.

## Part two — check what tests miss

- **Concurrency/timing** — correct when two run at once? (Tests run serially and miss races.)
- **Security** — exposed secrets, injection openings, unexpected dependencies. A security finding is always `HARD-STOP`, never a waiver. ANY note here escalates to the human — start it with `NOTE` or `⚠` so `add.py audit` can see it (`unescalated_security_note`). **But that check sees only what you wrote down:** it fires on a *marked* note auto-gated to PASS — a finding you never marked is **invisible**, escalated to no one. Under `auto`, a human **spot-audit** (reading the diff) is the only backstop for a *missed* security finding.
- **Architecture** — respects layering/dependency rules in CONVENTIONS.md?

Run the three lenses in order — a Security `HARD-STOP` ends the checklist (leave the rest blank). Record in §6 `### Advisor 3-lens verdict` (Verdict · Residue · Binding): `sensitivity: mechanical` → Binding `yes` (engine reads it for `advisor-gate-relax`), every other class → Binding `advisory`. `add.py audit` flags an unfilled block `advisor_verdict_unrecorded`, a companion to `refute_unrecorded`.

## Part three — the deep check (do not skim)

If the task produced code, record that every new symbol is referenced (wiring) and that no new dead/unused code was introduced. If it produced prose or non-code, record a semantic read — what you read in full and what it confirmed. The resolver judges which path; the engine never classifies.

Record in the §6 **Deep checks** block — an unfilled one is a **shallow verify**, not a PASS.

## Part four — was the green earned?

A green suite proves tests pass — not that the build EARNED them. Three judgment cheats pass the unchanged suite: src overfit to the test fixtures (special-cased to literal inputs), vacuous asserts (green against an empty implementation), and real logic stubbed away — all invisible to the mechanical tamper tripwire. Score them with an adversarial refute-read: an independent reviewer — the engine never spawns one — prompted to argue the green was NOT earned. A confirmed earned-green failure is HARD-STOP-class: never auto-passed, never RISK-ACCEPTED — a first cheat enters the bounded self-heal loop (run.md). Under `auto`, **record the verdict** in §6's `### Refute-read verdict` block — `add.py audit` flags an unrecorded `refute_unrecorded`, one of three measure-not-block shape lints it surfaces (also `shallow_deep_check` + `risk_unset`).

## Record exactly one outcome (no silent pass)

Present this gate via `report-template.md`'s ARC, render APPROVE, and reconcile FLAGS with `add.py report --decide`'s open-item count. **Human-led: render before `gate` and record `Reported: yes` in §6, never self-stamp.**

| Outcome | When |
|---------|------|
| `PASS` | all checks met |
| `RISK-ACCEPTED` | a **non-security** gap, with signed owner + ticket + expiry |
| `HARD-STOP` | any failing test or any security finding |

## Exit gate / Next

<exit_gate>
- [ ] Evidence confirmed, non-functional risks checked, outcome recorded — a person approved, or
  (under `autonomy: auto`, no residue) the run auto-resolved as accountable owner.
</exit_gate>

> **Persona** — run the refute-read under the fit persona / Code-Reviewer lens (advisory; security still HARD-STOPs).
> **Advisor · Confidence** — the earned-green refute-read is the canonical adversarial spawn (advisor.md); score it before recording the gate (confidence.md).

```bash
python3 .add/tooling/add.py gate PASS          # marks the task done
# or: add.py gate RISK-ACCEPTED   |   add.py gate HARD-STOP (return to Build)
```
Then read `phases/7-observe.md`. Book: `docs/08-step-6-verify.md`.
