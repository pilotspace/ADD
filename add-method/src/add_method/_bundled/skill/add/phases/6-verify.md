# Phase 6 — Verify (evidence + blind-spot checks)

Goal: establish trust and record an outcome. Passing tests are necessary, not
sufficient. Fill **§6** in TASK.md including the GATE RECORD.

> **Who resolves this gate depends on the `autonomy:` header (see `run.md`).**
> Under `autonomy: auto` (the default) a run auto-PASSes once the evidence is
> complete — every test green, the convergence loops dry, and **no residue**
> (security · concurrency · architecture) — recording it as *auto-resolved* with
> the named run as accountable owner: an explicit PASS, not a skip. **Security is
> always a HARD-STOP and is never auto-passed.** Under `autonomy: conservative`,
> or whenever residue is found, this phase is **human-led** and the checks below
> are the human's.

## Part one — confirm the evidence

- [ ] All tests pass.
- [ ] Coverage did not decrease.
- [ ] No test or contract was altered during build.

If any is false, stop and return to Build — there is nothing to verify yet.

## Part two — check what tests miss

- **Concurrency/timing** — is it correct when two run at once? (Tests run serially
  and miss races.) This is usually the single most important check.
- **Security** — exposed secrets, injection openings, unexpected/invented
  dependencies. A security finding is always `HARD-STOP`, never a waiver.
- **Architecture** — does it respect layering/dependency rules in CONVENTIONS.md?

## Record exactly one outcome (no silent pass)

| Outcome | When |
|---------|------|
| `PASS` | all checks met |
| `RISK-ACCEPTED` | a **non-security** gap, with signed owner + ticket + expiry |
| `HARD-STOP` | any failing test or any security finding |

## Exit gate / Next

- [ ] Evidence confirmed, blind-spots checked, outcome recorded — a person approved, or
  (under `autonomy: auto` with no residue) the run auto-resolved as the accountable owner.

```bash
python3 .add/tooling/add.py gate PASS          # marks the task done
# or: add.py gate RISK-ACCEPTED   |   add.py gate HARD-STOP (return to Build)
```
Then read `phases/7-observe.md`. Book: `docs/08-step-6-verify.md`.
