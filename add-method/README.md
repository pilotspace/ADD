<p align="center">
  <a href="https://www.npmjs.com/package/@pilotspace/add"><img alt="npm version" src="https://img.shields.io/npm/v/@pilotspace/add.svg"></a>
  <a href="https://pypi.org/project/pilotspace-add/"><img alt="PyPI version" src="https://img.shields.io/pypi/v/pilotspace-add.svg"></a>
  <a href="https://github.com/pilotspace/ADD/blob/main/LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
  <a href="https://pilotspace.github.io/ADD/"><img alt="Read the book" src="https://img.shields.io/badge/docs-read%20the%20book-blue.svg"></a>
  <a href="https://github.com/pilotspace/ADD/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/pilotspace/ADD.svg"></a>
</p>

# ADD — AI-Driven Development

**Your AI's first milestone is always great. ADD is for every milestone after that.**

> One skill file for work the AI plans, builds and verifies — while **you** own the two things
> it cannot do alone: decide *what* to make, and judge whether it is right. No engine, no CLI:
> the tools are files, git, and your project's own test command.

**The agent is the hands. ADD is the memory, judgment, and conscience — the part of the team
that survives when the context window doesn't.** Memory: `.add/PROJECT.md`, one task file per
change, five living specs — plain markdown in your repo. Judgment: every change is sized, and
every guess the agent makes is written down. Conscience: checks sealed in git before the build,
a verdict backed by real test output, and security findings that always stop.

The full reasoning — *why* every rule exists — is [the ADD book](https://pilotspace.github.io/ADD/).

```
  Foundation (context):  DDD  ·  SDD  ·  UDD
  The loop (this skill): TDD  ⇄  ADD
  Per task:  Direction (rules · assumptions · red checks → freeze commit)
             → Build (red → green)  → Verify (seal intact · fresh run · residue · verdict)  ↻
```

## Quick Start

```bash
npx @pilotspace/add init                                # Node / npm
```
```bash
pip install pilotspace-add && pilotspace-add init       # Python / pip
```

Then, in your coding agent, say what you want to build:

> `/add` — *"Let users log in with email + password / SSO, and keep them signed in for 30 days unless they explicitly log out."*

The agent sizes the request, writes the task's rules, assumptions and failing checks, seals them
with a `freeze(<slug>)` commit, builds to green, verifies on a fresh run, and hands you a report
of what it decided and on what evidence. Full walkthrough: the [Quickstart](./GETTING-STARTED.md).

## Highlights

- 📉 **Your agent stops re-breaking last month's work** — every decision lives on disk, in the task files and specs under `.add/`, so a fresh session resumes with the full picture. Measured: quality held flat where a long conversation decayed (six-milestone benchmark, n=1 per arm, ADD 2.0.0, pinned model — [report](https://github.com/pilotspace/ADD/blob/main/benchmark/results/2026-07-add-2.0-remeasure.md)).
- 🧪 **Tests that catch real bugs** — on ADD 4.0.0 with Claude Code (n=3 per arm), ADD's own tests caught more seeded bugs than vanilla's — 0.68 vs 0.51 and 0.79 vs 0.53 — at 2.2–2.9× the cost ([measured](https://github.com/pilotspace/ADD/blob/main/benchmark/results/2026-09-add-4.0-vs-vanilla.md)).
- 🔒 **Checks sealed before the build** — the task file and its checks are committed together as `freeze(<slug>)`. Weakening a check to get green shows up in `git diff`; a changed contract is a visible `refreeze` commit with its reason.
- 🔬 **A verdict backed by evidence, not a plausible diff** — every task ends `PASS`, `RISK-ACCEPTED` or `HARD-STOP`, written with the exact commands, exit codes and counts from a fresh run on the committed tree, plus a read of what tests cannot show and an attempt to break the green.
- 🙋 **Every guess on the record** — each silence in the request becomes an assumption line: what was not said, the reading taken, the cost if wrong. That list is what you review.
- ✅ **Nothing interrupts the run** — the agent routes, seals, builds and verifies on its own; you review the finished work from a report that puts any security finding first.
- 💸 **Ceremony only where it buys trust** — most changes take the Quick lane: a failing test, a fix, a commit, no task file.
- 🧠 **Fits *your* codebase** — project personas carry your domain's judgment; lessons with evidence become decisions that bind later work.
- 🤝 **Keep the agent you already use** — native in Claude Code; Cursor, Codex, Copilot, Gemini and others follow the same skill file.

> _Direction before speed. Trust comes from evidence you can re-run — not from reading code and finding it plausible._

## How much ceremony? — the lanes

**Most changes never create a node.** The agent sizes each request and routes it to the lightest
safe lane. The floor is checked first: anything touching security · data · architecture, or a
surface other code consumes, is at least a Task.

| the request | lane | what persists |
|---|---|---|
| mechanical, or a small behavior — ≤3 adjacent files, one sitting, no unknowns | **Quick** — no node | a red→green test + one commit |
| one behavior worth a written contract | **Task** | `.add/tasks/<slug>.md` + its commits |
| the answer is the deliverable — investigate · evaluate · research | **Explore** | the task's cited `## FINDINGS` |
| a theme, or more than one task | **Milestone** | `.add/milestones/<slug>.md` + its tasks |

Skipped ceremony is never skipped review: a Quick change still writes its test and runs it red.

## Why ADD — context rot, measured

Every AI tool writes code fast and aces a greenfield first milestone. The unsolved part is
**trust across change**: when the spec evolves in milestone 2 and breaks compatibility in
milestone 3, does the work you already trusted *stay* trusted?

Our benchmark ran the same six-milestone evolving project through each flow under a pinned
model with deterministic probe scoring ([report, revised edition](https://github.com/pilotspace/ADD/blob/main/benchmark/results/2026-07-add-2.0-remeasure.md)).
When ONE continued conversation carried the milestones, every flow decayed the same way
(coverage .92 → .75, an early spec violation carried through five more milestones). When every
milestone started a **fresh session resuming from disk**, the floors held at 1.0 across all six.
The lesson: nothing that matters may live only in the chat.

<sub>**Honesty note:** on this friendly workload spec-kit also held the restart floors, and ran cheaper — we published the retraction of our own earlier collapse claim. ADD 4.0 removed its engine because the engine's ceremony cost more than it protected; see [what changed in 4.0](https://pilotspace.github.io/ADD/20-whats-new-in-4/).</sub>

## Measured on 4.0 — what ADD buys Claude Code

The same Claude Code and pinned model, with and without the ADD skill; n = 3 per arm per workload
([results](https://github.com/pilotspace/ADD/blob/main/benchmark/results/2026-09-add-4.0-vs-vanilla.md) · [animated tour](https://pilotspace.github.io/ADD/add-value.html)).

| | vanilla Claude Code | + ADD 4.0 |
|---|---|---|
| seeded bugs its own tests catch (mutation score, wm1 · amb1) | 0.51 · 0.53 | **0.68 · 0.79** |
| runs that built code with no tests | 2 of 5 | **0 of 12** |
| runs that halted on a contradictory spec and shipped nothing | 2 of 7 | **0 of 13** |
| held-out edge cases passed (wm1) | 16.7 of 19 | **19 of 19** |
| claimed test count = a fresh rerun | no claim made | **27 of 27** |
| dollars per run | $0.45–0.73 | $1.31–1.67 — **2.2–2.9×** |
| correctness oracle | passes | passes — saturated, so no gain is shown either way |

<sub>**Fine print:** "vanilla" here is Claude Code carrying the operator's own `~/.claude` config
(which already asks for red/green TDD), not bare Claude Code. Small n: direction, not proof.</sub>

## Install

Pick your ecosystem — all three install the same skill:

```bash
npx @pilotspace/add init                   # Node / npm
```
```bash
pip install pilotspace-add && pilotspace-add init      # Python / pip
```
```text
# Claude Code plugin — no npm or pip needed
/plugin marketplace add pilotspace/ADD
/plugin install add@add-method
```

This installs:

| Path | What |
|------|------|
| `.claude/skills/add/` | the `add` skill — `SKILL.md`, `references/format.md`, `references/explore.md`, and the `persona-author` sub-skill |
| `.add/personas/` | starter personas — yours to edit; a re-install never overwrites one |
| `.add/personas-teacher/` | the vendored corpus personas are distilled from (read while authoring, never at run time) |
| `.add/personas-index/` | which persona to reach for, and when |
| `AGENTS.md` / `CLAUDE.md` etc. | for agents other than Claude Code: a short managed block pointing at the skill |

The installer drops files only. The bundle itself — `.add/PROJECT.md` and the specs — is the
agent's first move when you run `/add`.

**Already installed?** `npx @pilotspace/add@latest update` (or `pipx run pilotspace-add update`)
refreshes the skill and leaves your project work untouched. **Coming from 3.x?** Your bundle reads
as-is; the update removes the old engine files. See
[what changed in 4.0](https://pilotspace.github.io/ADD/20-whats-new-in-4/).

**New here?** Pick the walkthrough that matches what you are making:

- 🔍 [Quickstart](./GETTING-STARTED.md) — your first feature, end to end
- 📒 [Beyond code](./BEYOND-CODE.md) — a month-end close: same loop, where the artifact under check is a ledger rather than a repo

## Boundaries — what this package writes and runs

- **Runs only when you ask.** Nothing executes on install beyond copying files.
- **What it writes:** the skill under `.claude/skills/add/`, persona files under `.add/`, and the managed ADD block in your agent's context file. Never above the project root.
- **Network:** none. `npm`/`pipx` fetch the package; after that ADD is entirely offline.
- **No secrets, no credentials, no privileged access.**

## Use it

You talk to the agent; it drives the method. In Claude Code, `/add` starts or resumes work and
`/add status` summarizes where things stand. Other agents read the managed ADD block the
installer writes into `AGENTS.md` (and `CLAUDE.md`), which points them at the same skill file;
if `.gemini/` exists, the installer also adds `AGENTS.md` to Gemini CLI's context files.

You can always read the state yourself: it is `.add/PROJECT.md`, the task files, and `git log`.

## The non-negotiables

1. **Direction before build** — no production code before rules, assumptions and checks exist and the checks have failed for the right reason.
2. **Evidence, not inspection** — a change is trusted because its checks pass fresh on the committed tree and its residue was read. A green proves the checks you wrote ran — never that they were enough.
3. **Never weaken a sealed check or edit the contract to pass** — changed intent is a visible `refreeze` with a reason.
4. **No silent outcomes** — every task ends `PASS`, `RISK-ACCEPTED` or `HARD-STOP`; every guess is an assumption the human can read. Security findings are always `HARD-STOP`.
5. **`invariants:` bind every change**, Quick included.

## Read the method

- 📖 [Read the book](https://pilotspace.github.io/ADD/) — the full method, chapter by chapter
- 🔍 [Quickstart](./GETTING-STARTED.md) — one real feature, end to end
- 📒 [Beyond code](./BEYOND-CODE.md) — one real month-end close, end to end
- 📊 [Benchmark results](https://github.com/pilotspace/ADD/tree/main/benchmark/results) — every trust and cost claim, measured
- ⚖️ [ADD vs spec-kit — the honest comparison](https://pilotspace.github.io/ADD/appendix-h-add-vs-spec-kit/)

## Develop

```bash
python3 -m pytest -q      # from add-method/
```

License: MIT.
