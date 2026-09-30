# 05 · Verify — evidence, residue, refute, verdict

[← 04 Build — red to green, inside the lines](./04-build.md) · [Contents](./README.md) · Next: [06 Learn — lessons, milestones, the report →](./06-the-loop.md)

---

## Where trust is established

The build produced passing checks. That is necessary but not sufficient. Verification is where trust is established, and the rule governing it is *trust evidence, not the diff*.

"Not the diff" does not mean "don't look at the code". It means the *basis* of trust is evidence you produced — a sealed contract, a fresh run, a deliberate read of what tests cannot catch — rather than a general impression that the code reads plausibly. Plausibility is exactly the trap: AI code is often plausible and wrong.

Verify has five steps. Each one leaves something in the task's `## EVIDENCE`.

## 1 · Seal intact

Find the latest freeze (or refreeze) commit and diff the sealed files against it:

```bash
F=$(git log -1 --format=%H --grep='freeze(transfer-own-accounts)')
git diff $F HEAD -- .add/tasks/transfer-own-accounts.md tests/test_transfer_contract.py
```

It must print nothing. Any output means a sealed check or the contract changed after the seal without a `refreeze` — back to Build, or record the change honestly as a refreeze with its reason.

## 2 · Fresh green, on the committed tree

With a clean `git status`, run the task's `check:` command and the `regression:` command. Record the **real** exit codes and counts, from output you saw:

```text
$ python3 -m pytest -q tests/test_transfer_contract.py
7 passed in 0.09s                                     → exit 0 · 7 passed
$ python3 -m pytest -q
8 passed in 0.09s                                     → exit 0 · 8 passed
```

Never record a result you did not run. A green from before the last edit is not evidence for the code as it stands — which is why the run happens here, on the committed tree, not earlier.

## 3 · Residue — what passing tests cannot show

Read the diff for three things every time:

- **Security** — authorization, injection, secrets, unsafe input, dependencies with plausible-but-wrong names.
- **Concurrency** — races, ordering, atomicity. Tests usually run serially and miss simultaneity.
- **Architecture** — boundaries and dependencies the project already committed to.

Then by kind: **data** — is the migration reversible? **infra and release** — what is the rollback path? **UI** — can a keyboard and a screen reader reach it? **integration** — retries and idempotency.

Also check **wiring**: new code that nothing calls passes its checks while the feature is, in practice, absent. For each new entry point, name the production caller.

▶ *For the transfer: the one property the checks alone might not force is atomicity. Read the transaction boundary; confirm two simultaneous transfers from one account cannot both pass the balance check.*

## 4 · Refute — try to break your own green

A green nobody tried to break is reported, not earned. Run one to three probes derived **only** from the sealed rules:

| derive a probe by | ▶ transfer example |
|---|---|
| new values for a rule | amount = balance, balance + 1 |
| two rules composed | a foreign source *and* a zero amount — which error wins, and does it leak anything? |
| a boundary a rule implies | 1 cent from a balance of 1 cent |

Never invent a requirement: an expected answer that cannot be derived from the sealed rules and assumptions is a spec silence, and belongs in the report as a question — not a finding. A probe that breaks the green is a defect: back to Build, or a refreeze if the rule itself was wrong. A probe that holds can stay in the repository as an ordinary regression test.

For **security, data or architecture** work, do not refute your own work alone: spawn a fresh subagent that reads the task file *before* the diff and tries to break it. A builder tends to share its own misunderstanding with its own checks; a fresh reader does not.

## 5 · Verdict — exactly one, written down

Write the verdict into `## EVIDENCE` with everything a reviewer needs to check it:

```markdown
## EVIDENCE
freeze: 3a4b3a7 (refreeze of 1bfa9ee) · head: 3a4b3a7
seal: git diff 3a4b3a7 3a4b3a7 -- .add/tasks/transfer-own-accounts.md tests/test_transfer_contract.py → empty
check: `python3 -m pytest -q tests/test_transfer_contract.py` → exit 0 · 7 passed
regression: `python3 -m pytest -q` → exit 0 · 8 passed
residue: security — ownership is checked before amount or balance, so no error reveals whether an id exists; concurrency — check and debit run under one lock, and C6 now fails without it; architecture — src/transfers.py only, no new dependency
refute: a->b 1 from a balance of 1 → allowed, leaves 0; foreign source + amount 0 → 403 forbidden; unknown source + overdraw → 403 forbidden · held
verdict: PASS
```

These are the real values from the run in [Appendix D](./appendix-d-worked-example.md) — including why the seal is a refreeze: the first refute probe found that C6 could not fail, and the check was re-aimed in the open.

| Verdict | Meaning | When |
|---|---|---|
| `PASS` | seal intact, fresh green, residue clean | the normal path |
| `RISK-ACCEPTED` | a known **non-security** risk, with its reason and an owner | a gap you can name and someone can close later |
| `HARD-STOP` | a security finding, or a green you cannot honestly trust | the task stays open |

Set `status: done` only on `PASS` or `RISK-ACCEPTED`, and commit:

```bash
git commit -m "verify(transfer-own-accounts): PASS"
```

A `HARD-STOP` leaves `status: build`. Fix it through Direction if you can — and put it at the top of the report either way. A security finding is never a `RISK-ACCEPTED`.

## Common mistakes

- **Shipping on plausibility.** Reading the diff, finding it reasonable, and writing PASS without the seal check, the fresh run and the residue read.
- **A result you did not run.** Every exit code and count in EVIDENCE comes from output you saw, on the committed tree.
- **Trusting a filtered run.** The `regression:` suite is load-bearing; a green on a subset hides collateral breakage.
- **Treating a security gap as acceptable risk.** It is a `HARD-STOP`.
- **Refuting against an invented requirement.** Derive every probe's expected answer from the sealed rules.
- **Rewriting a closed task's EVIDENCE.** It records what was true when it was written; new findings go in a new task.

## Exit check

- [ ] The sealed files are unchanged since the latest freeze or refreeze commit.
- [ ] `check:` and `regression:` ran fresh on the committed tree; real exit codes and counts are recorded.
- [ ] Security, concurrency and architecture residue read, plus the kind-specific lens; new code is wired.
- [ ] One to three refute probes ran (a fresh subagent for security, data or architecture work).
- [ ] Exactly one verdict is in `## EVIDENCE`, and the verify commit is made.
