# 09 · Governance

[← 08 Parallel work — waves and worktrees](./08-parallel-work.md) · [Contents](./README.md) · Next: [10 Personas — the team as lenses →](./10-personas.md)

---

## Governance rests on what the engine actually enforces

Governance is not a policy document that hopes to be followed; in ADD it is the set of outcomes the gate refuses to skip. Everything below is either something `add gate` records and enforces, or a discipline the team owns around it. Where the prose says "the gate refuses," the engine refuses — prose ≡ enforcement.

Three levers carry the whole model, and they are orthogonal:

- **The gate outcome** — how a checkpoint resolves: `PASS`, `RISK-ACCEPTED`, or `HARD-STOP`.
- **The sensitivity floor** — how much authority a task demands, set by *what it touches*.
- **The depth dial** — how much ceremony a task runs, set by how much you want to think aloud.

The first is enforced at Verify, the second at Direction and the gate, the third is yours to turn. None of them is a global mode; all three are per task.

## The three gate outcomes

Every verification ends with exactly one recorded outcome, carrying an accountable owner — never a silent pass:

| Outcome | Meaning | Allowed when |
|---------|---------|--------------|
| **`PASS`** | complete, fresh, bound evidence and clean residue | the normal path |
| **`RISK-ACCEPTED`** | proceed on a signed waiver: named owner, linked ticket, expiry | a **non-security** gap only |
| **`HARD-STOP`** | cannot proceed | any failing check, or any security finding |

```
add gate <slug> PASS --by "<name>"
add gate <slug> RISK-ACCEPTED --by "<name>" --reason "<owner · ticket · expiry>"
```

A `RISK-ACCEPTED` is a deliberate, documented decision to ship a known, non-security limitation; the reason the engine requires — owner, ticket, expiry — is what lets the team find and close it later. A `PASS` auto-closes the task; a `HARD-STOP` leaves it open and returns the finding to Direction as a change request.

**Security is always `HARD-STOP`, and this one is engine-enforced.** The gate refuses a `RISK-ACCEPTED` on a security-sensitive node — a security finding cannot be signed away, whatever the evidence or the waiver says. No depth setting and no lens buys it back. A security limitation escalates to a human and is resolved to `PASS` or stays a `HARD-STOP`; there is no third door.

The rule behind the protocol is **no silent skips.** A report nobody is accountable for approving is just a document; an outcome with an owner — a person, or a named automated run — is governance. The gate also refuses a stale or unbound receipt: evidence that passed *before* the last edit, or a rule with no passing check behind it, is not evidence at all (see [05 Verify](./05-verify.md)).

### Why each step exists (institutional memory)

When someone proposes skipping a step "to go faster," this table is the answer:

| Step skipped | What happens | How you notice |
|--------------|--------------|----------------|
| Specify the rules | the wrong thing gets built | shipped, but users do not use it |
| Edge cases | the feature is vague, edges missing | the AI keeps asking questions mid-build |
| Contract | interfaces drift | front, back, and AI disagree on shapes |
| Checks | AI code is uncontrollable | no way to know it is right but to test by hand |
| Verify (architecture lens) | entropy explodes | the codebase is a tangle within months |
| The loop | silent rot | the same incidents recur |

## The sensitivity floor — the per-task authority setting

How much the AI is allowed to resolve unattended is not a switch you flip for the whole project. It is set per task, by *what the task touches* — its `sensitivity:`. The floor is mechanical: the engine maps each level to the lowest lane the task may run in, and it cannot be talked down.

| `sensitivity:` | Authority floor | Meaning |
|----------------|-----------------|---------|
| **mechanical** | `process` | a light floor; no new contract at stake |
| **data** | `plan` | a real task node, a human at the freeze |
| **architecture** | `plan` | a real task node, a human at the freeze |
| **security** | `human` | a human owns the gate; `HARD-STOP` on any finding |

The floor is closed: **security, data, and architecture always become a real task with a human at the freeze**, no matter how small the diff looks or how confident the agent is. The floor outranks the depth dial in one direction only — you may always run *more* ceremony than the floor demands, never less. This replaces any notion of a per-project "mode": there is nothing to set globally, because the task's own sensitivity already decided.

## The depth dial — ceremony, never authority

Orthogonal to the floor is the **depth dial** — `quick · standard · deep` — which tunes how much of the loop a task writes down, not how much it is trusted. A `quick` task still passes the same gate; it just carries fewer edge cases and a terser plan. A `deep` task spells out more of its reasoning for a reviewer to follow. Depth changes the paperwork; the floor changes the authority. A `quick` depth can never lower a `security` floor — the two dials do not talk to each other, and that separation is the whole point: you can go light on ceremony for a risky task and heavy on ceremony for a trivial one, and the gate is unmoved either way.

## The continuous concerns

Four concerns are not steps but threads that run through every beat, starting at setup. Pulling them forward ("shifting left") is far cheaper than bolting them on at the end.

| Concern | Begins at | Enforced at the gate by |
|---------|-----------|-------------------------|
| **Security** | setup (secret scanning, package verification) | zero high-severity findings; a security finding is `HARD-STOP` |
| **Testing** | the checks a task writes red-first | coverage must not decrease; no check weakened to pass |
| **Observability** | setup (logging/metric conventions) | instrumentation present; service objectives verified after release |
| **Cost** | setup (an AI-usage budget per task) | a task may not exceed its budget without escalation |

## AI-supply-chain governance

A method built on AI agents needs controls older methods did not:

- **Pin the model.** Record the model and version behind the work; re-check your prompts before adopting an upgrade. AI output is non-deterministic, so provenance matters.
- **Verify the package exists.** AI code is known to import packages by plausible-but-wrong names — a name an attacker can register and wait for. Before a suggested dependency lands, confirm it actually exists and is the one intended.
- **License-scan both generated and pulled-in code**, and keep a record of what the AI produced. Provenance is part of the artifact, not an afterthought.

## Metrics that matter — and the anti-metrics

Measure the scarce things:

- **Contract stability** — how rarely the frozen contracts change; high churn is genuinely expensive.
- **Validated requirement coverage** — the share of rules confirmed against real behavior by a passing, bound check.
- **Review throughput** — the team's verification capacity, which is the real ceiling on how fast the AI can safely run.
- **Delivery and reliability** — lead time, deployment frequency, change-failure rate, time to recover.

Do **not** optimize: lines of AI code generated, code-reuse percentage, prompt counts, or velocity measured in code volume. These count the cheap, disposable thing and create incentives to keep bad code to protect a number.

---

> **Governance, compressed.** Three outcomes, one recorded every time; security always stops for a human, and the engine enforces it. The task's sensitivity sets its authority floor; the depth dial sets its ceremony, and never the reverse. No silent skips — a named run is as accountable as a signature, and a security finding is neither.
