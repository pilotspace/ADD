# 09 · Governance — verdicts, floors, review after

[← 08 Parallel work — worktrees](./08-parallel-work.md) · [Contents](./README.md) · Next: [10 Personas — expert lenses →](./10-personas.md)

---

## What governance rests on

ADD 4.0 has no enforcement engine. Its governance rests on three things any reviewer can check with git and a text editor:

- **The seal** — a `freeze(<slug>)` commit of the task file and its checks. Whether a sealed file changed afterwards is one `git diff` away, and every legitimate change is a `refreeze(<slug>): <why>` commit in the history.
- **The evidence** — the verdict in the task's `## EVIDENCE`, with the freeze and head commits, the exact commands, their exit codes and counts, and the residue and refute notes. Anyone can re-run the commands at the recorded commit.
- **The report** — every session ends with HARD-STOPs first, then per task the verdict, the evidence and every assumption taken.

The agent drives the whole loop without interruption. The human governs by reading — the report, the assumptions, the diff when something looks off — and by answering what the report raises. That is where the attention of a person is worth the most: on decisions already made and evidence already produced, not on drafts.

## The three verdicts

| Verdict | Meaning | Allowed when |
|---------|---------|--------------|
| **`PASS`** | seal intact, fresh green on the committed tree, residue clean | the normal path |
| **`RISK-ACCEPTED`** | proceed with a known limitation, its reason and an owner written down | a **non-security** gap only |
| **`HARD-STOP`** | cannot be trusted as it stands | a security finding, or a green you cannot honestly trust |

**Security is always `HARD-STOP`.** It is never folded into a `RISK-ACCEPTED`, never softened by a persona, and never buried: it goes at the top of the report and at the top of the pull request. The task stays open until it is fixed through Direction.

The rule behind it is **no silent outcomes** — every task ends with one written verdict, and every guess is an assumption on the record.

### Why each step exists

When someone proposes skipping a step "to go faster", this is the answer:

| Step skipped | What happens | How you notice |
|---|---|---|
| Rules | the wrong thing gets built | shipped, but nobody uses it |
| Assumptions | silent decisions ship as defaults | "who decided that?" in review — nobody did |
| Red checks first | checks that pass anything | green suite, broken feature |
| The seal | checks quietly weakened to pass | the bug the check was written for ships |
| Fresh run | a stale green stands in for current code | "it passed yesterday" |
| Residue read | races, secrets, tangles | incidents tests never reproduced |
| Learn | the same mistakes recur | the same delta, again |

## The floor — what always gets a task

Sizing is the agent's call, with one closed floor it cannot talk down: anything touching **security · data · architecture**, or a surface other code consumes, is at least a Task — with rules, assumptions, sealed checks and a written verdict. For those same three kinds, the refute step in Verify uses a **fresh subagent** that reads the task file before the diff.

## The continuous concerns

| Concern | Begins at | Held by |
|---|---|---|
| **Security** | setup — secrets out of the repo, dependencies verified | the residue read; any finding is `HARD-STOP` |
| **Testing** | the red checks each task writes | the seal; the `regression:` suite on every verify |
| **Observability** | setup — logging and metric conventions | checks reused as production monitors |
| **Cost** | the lane choice | Quick for small work; ceremony only where it buys trust |

## AI supply chain

- **Record the model.** Output is non-deterministic; provenance matters when you compare or reproduce.
- **Verify the package exists** and is the one intended. AI code imports plausible-but-wrong names that an attacker can register.
- **License-scan** both generated and pulled-in code.

## Metrics that matter — and the anti-metrics

Measure the scarce things: how rarely sealed contracts change, the share of rules covered by a passing check, verification throughput, and delivery reliability (lead time, change-failure rate, time to recover).

Do **not** optimize lines of AI code generated, prompt counts, or velocity measured in code volume. They count the cheap, disposable thing.

---

> **Governance, compressed.** Seal in git, evidence in the task file, a report the human reads. Three verdicts, one written every time. Security is always a HARD-STOP, and always at the top.
