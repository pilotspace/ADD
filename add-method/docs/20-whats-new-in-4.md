# 20 · What changed in 4.0 — migrating from 3.x

[← 17 Components — monorepo and multi-repo](./17-components.md) · [Contents](./README.md) · Next: [Appendix C Glossary →](./appendix-c-glossary.md)

---

## In one paragraph

ADD 4.0 removes the engine. There is no `.add/tooling/`, no `cli.py`, no `add.py`, no `add <verb>` commands, no refusal codes and no agent roster. The method is one skill file — `SKILL.md` with four references: `format.md` (file shapes), `explore.md` (the research lane), `evidence.md` (the closed loop from intent to production) and `personas.md` (routing lenses) — that the agent follows with the tools every project already has: files, git, and the project's own test command. There is also no approval step: the agent routes, seals, builds and verifies without stopping, and the human reviews afterwards from a report that lists every assumption it took.

## Why

The engine was built to make the method's promises mechanical: a freeze could not be faked, a verdict needed a receipt, a stale green was refused. It did that. It also cost more than it protected.

- **Cost against vanilla prompting.** On the amb1 ambiguity track, vanilla prompting cost $0.61 per run with an oracle score of 1.00; ADD 3.x cost $2.13–2.52 per run with oracle scores of 0.75–1.00 ([amb1 findings](https://github.com/pilotspace/ADD/blob/main/benchmark/FINDINGS-2026-08-10.md)). The intervention that run measured changed what ADD *wrote down*, not what it *built*.
- **Cost against spec-kit.** Over five evolving milestones, ADD 3.x cost $34.37 against spec-kit's $18.66 — 1.8× in dollars — at a minimum per-milestone fidelity of 0.97 against 0.95. On the two larger milestones ADD's cost rose far more steeply, driven by per-task ceremony over a growing codebase ([benchmark, WM4/WM5 extension](https://github.com/pilotspace/ADD/blob/main/benchmark/BENCHMARK.md)).
- **Where the tokens went.** Cost tracked turns × context per turn, and a large share of the agent's turns were spent driving the engine — status, stamps, receipts, gates — rather than doing the work.

What the engine enforced turned out to be expressible without it:

| 3.x mechanism | 4.0 equivalent |
|---|---|
| `add freeze` stamping a digest of the direction | a `freeze(<slug>)` **git commit** of the task file and its check files |
| the tamper tripwire on sealed files | `git diff <freeze> HEAD -- <sealed files>` must print nothing |
| `add refreeze` / change requests | a `refreeze(<slug>): <why>` commit, reason under `## LOG` |
| `add run` writing a Run receipt | real command output — command, exit code, counts — written into `## EVIDENCE` |
| `add gate PASS \| RISK-ACCEPTED \| HARD-STOP` | the same three verdicts, written into `## EVIDENCE`, committed as `verify(<slug>): <verdict>` |
| `add refute` stamps and refute tiers | 1–3 executable probes from the sealed rules; on floor work a fresh subagent loading the counter-lens persona writes them after the build |
| `add interview` and the human freeze | `## ASSUMPTIONS` and `derived:` rules, reviewed afterwards in the session report; on floor work a second reader (a fresh subagent under the counter-lens) challenges them before the seal |
| a Must names its source | `(from: request \| <file> \| <spec> \| derived: <why>)` on each rule; each check names its `falsifier:` |
| the regression floor PLAN line | `regression:` in PLAN — the full suite, `affected: … — why`, or `none — why` |
| a refreeze that moves `gives:` marks consumers stale | Verify step 3: `git grep` the surface's users and run their tests; a broken consumer is not a PASS |
| the quick-lane tripwire | Quick work that turns out to touch the floor "is a Task now" — stop and write the task file |
| `add release <tag>` binding a tag to receipts | tag only a commit whose tasks since the last tag each end in a `verify(` commit; `observes:` names what to watch after release |
| an escape drains only with why-missed + prevention; closed history superseded | a successor task with `fixes: <slug>@<verify sha>`, a reproducing check, why the checks missed it, and a bound prevention |
| `add status` | read `.add/PROJECT.md` and the open task files; `git log` |
| `add new` | write the task or milestone file from `format.md` |
| `add learn` / `add deltas` / `add fold` | a line in the spec's `## Deltas`; promotion to `## Decisions that bind` |
| `add milestone-done` goal gate | tick each EXIT box with its evidence; `status: done` when all are ticked |
| `add wave` / `add join` | one git worktree per independent task, disjoint `scope:`, merged one at a time |
| `add advise` / persona records | route a lead persona by the task's `risks:` against each persona's `covers-risks:`; its `counter-lens:` reads at verify; a `lens:` line in EVIDENCE records what it caught |
| `add doctor --sync`, `graph.json`, compiled `index.md`, `log.md` | nothing — nothing is compiled; the files are the state |
| `add-worker` / `add-advisor` agents | removed; the model plans and spawns fresh subagents where the skill says to |

What did **not** change: Direction → Build → Verify; rules, assumptions and checks before any production code; red for the right reason; never weaken a sealed check; the three verdicts; security is always a `HARD-STOP`; `invariants:` bind every change; the lanes and the floor.

## Upgrading a project

1. **Update the install** with the same command you installed with — e.g. `npx @pilotspace/add@latest update`, or `pipx run pilotspace-add update`. The installer replaces the skill, removes `.add/tooling/` and the retired `add-worker` / `add-advisor` agent files, and seeds any missing starter personas without overwriting yours.
2. **Keep your bundle.** A 3.x `.add/` reads as-is. Its extra frontmatter (`verified:`, `generated:`, digests), `graph.json`, `index.md`, `log.md`, `runs/` and `tasks/<slug>.d/` are history: leave them, do not maintain them. New work uses the shapes in [12 · The bundle](./12-bundle-format.md). If you prefer a clean tree, move the 3.x bundle aside — this repository keeps its own under `archive/add-3x-bundle/`.
3. **Make sure `PROJECT.md` has `goal:`, `invariants:` and `test_cmd:`.** The agent reads it first every session.
4. **Open tasks** carry on under the 4.0 loop. A task frozen under 3.x has no `freeze(<slug>)` commit; when resuming it, commit its task file and check files as `freeze(<slug>)` so Verify has a seal to diff against.
5. **Update your agent pointers.** Re-running the installer rewrites the managed ADD block in `CLAUDE.md` / `AGENTS.md`; text outside the markers is untouched.
6. **Retire scripts and CI steps** that call the old CLI. A CI job that ran the engine's audit becomes an ordinary test run.

## What you give up

Mechanical refusal. In 3.x the engine refused to record a `PASS` over a stale receipt; in 4.0 a dishonest agent could write one. What stands in its place is that every claim is checkable by anyone with git: the seal is a diff, the evidence names the exact commands at an exact commit, and every change of intent is a visible commit. The human's review moved to the end, where the evidence is — and the report is written so that disagreeing is easy.
