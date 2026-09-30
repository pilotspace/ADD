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

- 📜 **Every change leaves its reasoning in your repo** — the rules, the guesses and the checks live in one task file next to the code, so the next session or teammate reads the intent instead of guessing it.
- 🛡️ **Safer guesses where your spec is silent** — ADD takes the least-privilege reading when nobody said *who* may act, and seals a check for it.
- 🔒 **Trust rests on evidence, not a plausible diff** — checks are sealed in a `freeze` commit before the build, and every task ends in a verdict you can re-run. Security findings always lead the report.
- ⚖️ **An honest price** — Measured on ADD 4.0.0 with Claude Sonnet 5.5, n = 3 per arm per workload: 1.7–2.1× the dollars and 4.0–5.1× the minutes of vanilla Claude Code. The code quality ties; ADD gets more of a spec's silences right ([results](https://github.com/pilotspace/ADD/blob/main/benchmark/results/2026-09-add-4.0-vs-vanilla.md)).
- 💸 **Ceremony only where it buys trust** — most changes take the Quick lane: one red→green test, one commit, no task file.

## What ADD gives your project

Vanilla Claude Code already writes good code: on Sonnet 5.5 it passed every held-out edge case in
our benchmark. What it does not leave behind is the *why*. ADD 4.0 is one skill file, with no
engine and no CLI, that makes every change leave the reasoning in your repository, next to the code:

| | What your project keeps | Why it pays off later |
|---|---|---|
| 📜 **A contract per change** | `.add/tasks/<slug>.md`: the rules, the guesses, and the checks that prove them | the next session, or the next teammate, reads the intent instead of reverse-engineering it from code |
| 🙋 **Every guess on the record** | each silence in your request becomes an ASSUMPTION: the reading taken and the cost if wrong, costliest first | you review a short list of decisions, not a diff; a wrong guess is one line to correct |
| 🛡️ **Safer readings of silence** | when nobody said *who* may do something, ADD takes the least-privilege reading and seals a check for it | the booking benchmark never said who may cancel: vanilla let anyone in 8 of 8 runs; ADD chose owner-only in 3 of 3 on Sonnet 5.5 |
| 🔒 **Checks sealed before the code** | the failing checks are committed as `freeze(<slug>)` before any build | a test weakened to get green shows up in `git diff`; a change of intent is a visible `refreeze` commit |
| 🔬 **Evidence you can re-run** | a verdict (`PASS`, `RISK-ACCEPTED` or `HARD-STOP`) with the exact commands and counts, committed as `verify(<slug>)` | the claimed test count matched a fresh rerun in 33 of 33 benchmark runs; security findings always lead the report |
| 🧠 **Memory that outlives the chat** | state lives on disk, not in the conversation | over six evolving milestones, one long chat's requirement coverage fell .92 → .75, while fresh sessions resuming from disk held 1.0 ([report](https://github.com/pilotspace/ADD/blob/main/benchmark/results/2026-07-add-2.0-remeasure.md)) |

## Vanilla Claude vs Claude + ADD — the same request, two flows

Two real round-6 runs on Sonnet 5.5, given the same spec: a booking service whose requirements
contradict each other (a conflict gets `202` waitlisted *and* `409` rejected) and say nothing on six
other decisions. ▶ **[Watch both play on one clock](https://pilotspace.github.io/ADD/add-vs-vanilla.html)**.

| clock | 🏃 **vanilla Claude Code** (`vanilla-amb/rep1`) | 🛡️ **Claude Code + ADD** (`add-4-amb/rep1`) |
|---|---|---|
| 0 s | reads the repo | orients from `.add/PROJECT.md` |
| 31 s | writes `app/` and 7 tests in one command | … |
| 46 s | tests pass, smoke run OK: **done, $0.28** | … |
| 56–94 s | | **Direction:** writes `.add/tasks/booking-waitlist.md` with 17 rules, 8 ASSUMPTIONS and 19 checks, plus the tests |
| 97 s | | runs the 19 checks red and seals them: `freeze(booking-waitlist)` |
| 110–154 s | | **Build:** code until all 19 pass, sealed files untouched; live probe with `curl` |
| 186 s | | **Verify:** the seal diff is empty, a fresh run gives 19 OK, and the verdict is committed as `verify(booking-waitlist): PASS` |
| 195 s | | **done, $0.63** |
| **the contradiction** | caught it and chose waitlist-by-default with a `"waitlist": false` opt-out, **in its chat reply** | caught it and made the same choice, **as ASSUMPTION A1 in the task file**, first in the report as the costliest guess |
| **who may cancel a booking?** | anyone | the owner only (rule `R:OWNER`, sealed check C11) |
| **left in your repo** | the code and its tests | the code, the checks, the contract and the evidence, as three commits |

Same code quality, same headline decision. The difference is where that decision lives, and the
guesses nobody asked about.

## Measured on 4.0 — what you get, what you pay

The same Claude Code with and without the ADD skill, on `claude-sonnet-5-5` (Sonnet 5.5), n = 3 per
arm per workload ([results](https://github.com/pilotspace/ADD/blob/main/benchmark/results/2026-09-add-4.0-vs-vanilla.md) ·
[both flows, animated](https://pilotspace.github.io/ADD/add-vs-vanilla.html) ·
[the earlier rounds, animated](https://pilotspace.github.io/ADD/add-value.html)).

| on Sonnet 5.5 (wm1 · amb1) | vanilla Claude Code | + ADD 4.0 |
|---|---|---|
| **you pay:** dollars per run | $0.31 · $0.33 | $0.52 · $0.68, **1.7× · 2.1×** |
| **you pay:** minutes per run | 0.8 · 0.85 min | 4.1 · 3.4 min, **5.1× · 4.0×** |
| held-out edge cases passed | 19 of 19 · 14 of 14 | 19 of 19 · 14 of 14, a tie |
| seeded bugs its own tests catch (mutation) | 0.83 · 0.76 | 0.75 · 0.79, within noise |
| planted ambiguities handled right, of 7 (amb1) | 4.3 | **5.7** |
| "who may cancel?" read as owner-only (amb1) | 0 of 3 | **3 of 3** |
| surfaced the spec's contradiction (amb1) | **2 of 3** | 1 of 3 |
| claimed test count = a fresh rerun | no claim made | **6 of 6** |

On the older Sonnet 5 (rounds 4–5), ADD's own tests caught more seeded bugs (0.68 vs 0.51 and 0.79
vs 0.53) and vanilla shipped no tests in 2 of 5 runs, at 2.2–2.9× the dollars. Sonnet 5.5 closed
those gaps on these workloads, and ADD's cost fell from $1.67 to $0.52 a run.

<sub>**Fine print:** "vanilla" is Claude Code carrying the operator's own `~/.claude` config
(which already asks for red/green TDD), not bare Claude Code. Both workloads are saturated at
Sonnet 5.5, and n = 3 is direction, not proof.</sub>

## When vanilla Claude is the right call

- **Throwaway work** (a script, a spike, a one-shot): use vanilla. It runs 4–5× faster at about
  half the price, and on a strong model the code is as good.
- **A product you will still be changing next month** (several milestones, teammates, or anything
  where *who may do this?* matters): use ADD. The decisions outlive the chat, the guesses get
  reviewed, and the checks cannot quietly weaken.
- **In between**, ADD sizes each request itself. Most changes take the Quick lane, which is one
  red→green test and one commit, with no task file.

ADD works with the agent you already use (Claude Code, Codex, Cursor, Copilot, Gemini) and installs
via npm, pip, or the Claude Code plugin.

> _Direction before speed. Trust comes from evidence you can re-run, not from reading code and finding it plausible._

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
