# 11 · Governance

[← 10 Setup and stages](./10-setup-and-stages.md) · [Contents](./README.md) · Next: [12 Roles →](./12-roles.md)

Governance is what keeps the method honest when a team runs it at speed. It is the same regardless of which AI tool writes the code, because it lives in the process and the pipeline, not in the agent.

---

## The autonomy ladder

How much the AI is allowed to do is not one switch; it is a setting chosen per area, rising with evidence and with your capacity to verify.

| Level | The AI… | A person… | Typical use |
|-------|---------|-----------|-------------|
| **Suggest** | proposes options | decides and writes | early, exploratory work |
| **Draft-and-review** | drafts artifacts | edits and approves each one | specs, scenarios, contracts |
| **Generate-behind-gate** | generates code | reviews the change; it merges only if the contract and tests pass | the normal build |
| **Auto-with-evidence** | generates and merges | samples and audits; auto-merge allowed only with a full evidence bundle attached | narrow, well-tested areas |

The governing rule, restated from the principles: **operate only at the level your review capacity can sustain.** If the AI produces more than the team can verify, drop a level.

The **per-scope default is auto-with-evidence behind a one-approval decision point**: the AI drafts the specification bundle, a human approves the frozen contract once, and the build auto-gates on evidence. You *lower* a scope toward draft-and-review or suggest wherever risk is high or evidence is thin — and a high-risk or method-defining scope is *always* lowered (it is never auto-run). The default sets where you start; review capacity and risk set where you stay.

The engine expresses this per task as an explicit three-rung level — `autonomy: manual | conservative | auto`, an ordered ladder `manual < conservative < auto` declared in the `TASK.md` header and reviewed at the freeze. `auto` is auto-with-evidence behind the one approval (the seeded default); `conservative` is the deliberate lowering that keeps a person at the verify gate; `manual` is the strict floor where the human owns the gate and nothing auto-resolves. A high-risk or method-defining scope refuses an unguarded `auto` (`unguarded_high_risk_auto`) — it must be lowered to `conservative` or `manual`. The prose here and that engine token are one rule: prose ≡ enforcement.

**Autonomy is earned by goal-clarity — the auto-ready goal.** The autonomy level decides *who* resolves Verify; an **auto-ready goal** decides whether a self-verifying run is even *meaningful*. A milestone goal is *auto-ready* when **every exit criterion cites a verifier** — `(verify: <test | command | metric>)` — so the engine can check the result against the goal without human judgment. `add.py check` raises a `goal_not_auto_ready` WARN (never red, the active milestone only) while the goal has criteria not all cited, and `status` surfaces a `goal-ready:` line every session, so the goal-clarity gap stays visible. The WARN *measures*, it never blocks: it changes neither the freeze gate nor the autonomy level — clarifying the goal is the prerequisite that *earns* trust, not a new gate (a zero-criteria goal reads not-auto-ready and is milestone-shaping's nudge, not this one's). The lint raises the floor — a citation slot per criterion — but cannot prove the citation is honest: a human can still write `(verify: it works)`, and closing that is a person's judgment, not the engine's.

## The gate-fail protocol and the three reports

Every checkpoint produces three short reports — **Test** (does it pass?), **Quality** (is it well-made and conformant?), and **Risk** (what could go wrong, and who owns it?) — and resolves to exactly one outcome:

- **`PASS`** — criteria met; proceed.
- **`RISK-ACCEPTED`** — proceed with a signed waiver carrying a named owner, a linked ticket, and an expiry. Allowed for non-security gaps only.
- **`HARD-STOP`** — cannot proceed. Triggered by any failing test or any security finding. A non-security limitation may proceed only with a signed `RISK-ACCEPTED` record carrying an owner and an expiry; security is never waved through.

The rule behind the protocol is *no silent skips.* A report nobody is accountable for approving is just a document; an outcome with an owner is governance.

### Why each step exists (institutional memory)

When someone proposes skipping a step "to go faster," this table is the answer:

| Step skipped | What happens | How you notice |
|--------------|--------------|----------------|
| Specify | the wrong thing gets built | shipped, but users do not use it |
| Scenarios | the feature is vague, edges missing | the AI keeps asking questions mid-build |
| Contract | interfaces drift | front, back, and AI disagree on shapes |
| Tests | AI code is uncontrollable | no way to know it is right but to test by hand |
| Verify (architecture check) | entropy explodes | the codebase is a tangle within months |
| Operate / loop | silent rot | the same incidents recur |

## The continuous concerns

Four concerns are not steps but threads that run through every step, starting at project setup. Pulling them forward ("shifting left") is far cheaper than bolting them on at the end.

| Concern | Begins at | Enforced at the build gate by |
|---------|-----------|-------------------------------|
| **Security** | setup (secret scanning, dependency allow-list) | zero high-severity findings; every AI-suggested package verified to exist |
| **Testing** | the scenarios step | coverage must not decrease; no test weakened to pass |
| **Observability** | setup (logging/metric conventions) | instrumentation present; service objectives verified after release |
| **Cost** | setup (an AI-usage budget per task) | a task may not exceed its budget without escalation |

## AI-specific governance

A method built on AI agents needs controls older methods did not:

- **Pin the model.** Record the model and version; re-check the prompt library before adopting an upgrade. AI output is non-deterministic, so provenance matters.
- **Test the prompts.** The reusable instructions in `playbook/` are themselves artifacts: give each golden input/output cases, and re-check them when edited. A prompt that fails its check does not ship.
- **Guard the supply chain.** No package outside the allow-list without human approval; verify each suggested package actually exists, to defeat the risk of an agent inventing a plausible name an attacker has registered.
- **Track provenance and licensing.** License-scan both generated and pulled-in code; keep a record of what the AI produced.

## Metrics that matter — and the anti-metrics

Measure the scarce things:

- **Contract stability** — how rarely the frozen contracts change; high churn is genuinely expensive.
- **Validated requirement coverage** — the share of rules confirmed against real behavior.
- **Review throughput** — the team's verification capacity, which sets the safe autonomy level.
- **Delivery and reliability** — lead time, deployment frequency, change-failure rate, time to recover.

Do **not** optimize: lines of AI code generated, code-reuse percentage, prompt counts, or velocity measured in code volume. These count the cheap, disposable thing and create incentives to keep bad code to protect a number.

## Profiles: one method, three intensities

| | **Express** (startup) | **Standard** (most teams) | **Regulated** (audited) |
|---|---|---|---|
| Steps | combine Specify + Scenarios into a one-page brief; light contract | full flow | full flow, all `HARD-STOP` |
| Scenarios | happy path only | happy + key alternatives | exhaustive, incl. compliance |
| Autonomy ceiling | generate-behind-gate from day one | up to auto-with-evidence | generate-behind-gate max; the AI never merges its own work |
| Gate default | `RISK-ACCEPTED` allowed | `PASS` required to advance | `HARD-STOP`; full audit trail |

Choose the profile deliberately — a startup spike and a banking system are not the same risk — and run different products at different profiles as appropriate. The choice is owned by the delivery lead (see [12 Roles](./12-roles.md)).
