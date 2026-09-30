<p align="center">
  <img src="add-banner.jpg" alt="ADD — AI-Driven Development" width="100%">
</p>

<p align="center">
  <a href="https://www.npmjs.com/package/@pilotspace/add"><img alt="npm version" src="https://img.shields.io/npm/v/@pilotspace/add.svg"></a>
  <a href="https://pypi.org/project/pilotspace-add/"><img alt="PyPI version" src="https://img.shields.io/pypi/v/pilotspace-add.svg"></a>
  <a href="https://github.com/pilotspace/ADD/blob/main/LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
  <a href="https://pilotspace.github.io/ADD/"><img alt="Read the book" src="https://img.shields.io/badge/docs-read%20the%20book-blue.svg"></a>
  <a href="https://github.com/pilotspace/ADD/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/pilotspace/ADD.svg"></a>
</p>

<h1 align="center">ADD — AI-Driven Development</h1>
<p align="center"><strong>Your AI's first milestone is always great. ADD is for every milestone after that.</strong></p>
<p align="center">Describe the feature. The agent plans, seals, builds and verifies it — and hands you a report of every decision it made, backed by evidence you can re-run.</p>

---

## AI work doesn't fail on day one — it rots

Every AI tool ships a beautiful first feature. The failure shows up **across milestones**:
requirements evolve, the conversation gets long, and the agent quietly re-breaks what it already
got right. That decay has a name — **context rot** — and we measure it instead of hand-waving.

The cause turned out to be simple: **context rot lives in the conversation, not in the method or
the model.** The same agent that decays inside one long chat holds a perfect line when every
milestone restarts from state on disk.

So ADD's answer isn't a bigger context window or a smarter summary. It's this: **nothing that
matters lives in the chat.** Rules, assumptions, checks and verdicts are plain files in your
repository, sealed by git. Close the laptop, lose the session, swap the agent: the next session
reads them back and loses nothing.

| Same model, six evolving milestones | One long conversation | Fresh session per milestone, resumed from disk |
|---|---|---|
| Requirement coverage | **.92 → .75, never recovered** | **1.0 flat across all six** |
| An early spec violation | carried through **five more milestones**, never re-examined | **never introduced** — each session re-derived the shape from the spec |
| New-feature quality at milestone 6 | still good — but the old promises rotted | **1.0** — new work stays good *and* old work holds |

<sub>[Campaign report, revised edition](./benchmark/results/2026-07-add-2.0-remeasure.md) — pinned model, deterministic probes, no LLM judge.</sub>

## What ADD is

An agent already knows how to do the work. What it *structurally cannot* keep is everything
outside one context window: what's true so far, what was promised, what must never be traded
away.

> **The agent is the hands. ADD is the memory, judgment, and conscience — the part of the team
> that survives when the context window doesn't.**

ADD 4.0 is **one skill file**. No engine, no CLI, no approval step: the agent's tools are files,
git, and your project's own test command.

| Faculty | What it holds | See it yourself |
|---|---|---|
| 🧠 **Memory** — *what is true* | `.add/PROJECT.md`, one task file per change, five living specs | open `.add/` — it is plain markdown |
| ⚖️ **Judgment** — *how to work here* | every request sized into a lane; every guess written as an assumption; lessons promoted into binding decisions | read a task's `## ASSUMPTIONS` |
| 🛡️ **Conscience** — *what is trusted* | checks sealed in a `freeze` commit before the build; a verdict with real test output; security always a hard stop | `git diff` the sealed files against the freeze commit |

## ✨ Highlights

- 📉 **Your agent stops re-breaking last month's work** — every decision lives on disk, so a fresh session resumes with the full picture instead of a drifting memory. Measured: quality held flat where a long conversation decayed (six-milestone benchmark, n=1 per arm, ADD 2.0.0, pinned model — [report](https://github.com/pilotspace/ADD/blob/main/benchmark/results/2026-07-add-2.0-remeasure.md)).
- 🧪 **Tests that catch real bugs** — on ADD 4.0.0 with Claude Code (n=3 per arm), ADD's own tests caught more seeded bugs than vanilla's — 0.68 vs 0.51 and 0.79 vs 0.53 — at 2.2–2.9× the cost ([measured](https://github.com/pilotspace/ADD/blob/main/benchmark/results/2026-09-add-4.0-vs-vanilla.md)).
- 🔒 **Checks sealed before the build** — the rules and the failing checks are committed together as `freeze(<slug>)`; weakening a check to get green shows up in `git diff`, and a changed contract is a visible `refreeze` commit with its reason.
- 🔬 **Know it's correct without reading every line** — every task ends `PASS`, `RISK-ACCEPTED` or `HARD-STOP`, with the exact commands, exit codes and counts from a fresh run, a read of what tests cannot show, and an attempt to break its own green. Evidence you can re-run, never a diff that merely *looks* right.
- 🙋 **Every guess on the record** — each silence in your request becomes an assumption: what was not said, the reading taken, the cost if wrong. That list is what you review.
- ✅ **Stop babysitting the build** — nothing interrupts the run; you review the finished work from a report that puts any security finding first.
- 💸 **Ceremony only where it buys trust** — most changes take the Quick lane and never create a task file.
- 🔒 **Never ship a security hole on autopilot** — any security finding is a `HARD-STOP`, at the top of the report.
- 🤝 **Keep the agent you already use** — Claude Code, Codex, Cursor, Copilot, Gemini; install via npm, pip, or the Claude Code plugin.

> _Direction before speed. Trust comes from evidence you can re-run — not from reading code and finding it plausible._

<sub>**Fine print:** benchmark cells are single-rep (direction, not statistical proof). On this friendly workload spec-kit also passed the restart floors, and ran cheaper — the report's revised edition retracts our own earlier "collapse" claim. ADD 4.0 dropped its engine because the engine's ceremony cost more than it protected ([what changed in 4.0](https://pilotspace.github.io/ADD/20-whats-new-in-4/)).</sub>

## ADD vs vanilla — when it earns its keep

ADD isn't free. It asks the agent to write rules, assumptions and failing checks before any code,
and asks you to read the report afterwards. That is the whole trade.

|  | 🏃 **Vanilla** — just prompt the agent | 🛡️ **ADD** |
|---|---|---|
| **First feature** | fastest — start typing | one Direction pass first, then the build |
| **Across milestones** | quality decays; old promises silently break | sealed checks and living specs; trust holds |
| **What you verify** | you re-read the diff and hope | a verdict with re-runnable evidence and a list of every assumption |
| **Resuming later** | re-explain the goal, re-read the repo | read back from `.add/` and `git log`, lossless |
| **Best for** | throwaway scripts, one-shots, spikes | evolving products, multiple milestones, teams |

**Rule of thumb:** building something you'll throw away this week? Vanilla is fine. Building
something you'll still be changing next month? The Direction pass pays for itself the first time
the agent *doesn't* re-break a feature you shipped three milestones ago.

## Measured on 4.0 — what ADD buys Claude Code

The same Claude Code and pinned model, with and without the ADD skill; n = 3 per arm per workload
([results](./benchmark/results/2026-09-add-4.0-vs-vanilla.md) · [animated tour](https://pilotspace.github.io/ADD/add-value.html)).

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

---

## 🚀 Get Started

**Prerequisites:** Node ≥ 18 *(npm path)* or Python ≥ 3.10 *(pip path)*, a git repository, and a coding agent.

### 1 · Install into your project

```bash
npx @pilotspace/add init      # Node / npm
```
```bash
pip install pilotspace-add && pilotspace-add init      # Python / pip
```
```text
# Claude Code plugin — no npm or pip needed
/plugin marketplace add pilotspace/ADD
/plugin install add@add-method
```

> See a real one: this repo's own [`.add/`](https://github.com/pilotspace/ADD/tree/main/.add) folder.

### 2 · Describe your first feature

In Claude Code, run **`/add`** and say what you want to build:

```bash
/add 'Let users log in with email + password / SSO, and keep them signed in for 30 days unless they explicitly log out.'
```

The agent:

1. 🧭 **Orients** from `.add/PROJECT.md` and the open task files — never re-reading your whole repo.
2. 📐 **Sizes** the request: Quick, Task, Explore or Milestone.
3. ✍️ **Writes the direction** — rules, assumptions and failing checks — and seals them in a `freeze` commit.
4. ✅ **Builds and verifies** to a written verdict, then reports; a security finding always goes to the top.

### 3 · Resume anytime

```markdown
/add status | continue
```

State lives on disk, not in the chat.

---

## ⚙️ How ADD Works

**One task · three beats · one file.** Every change worth a contract is one task file at
**`.add/tasks/<slug>.md`**. **Direction** writes its rules, assumptions and checks, runs the
checks red, and seals them with a `freeze(<slug>)` commit. **Build** turns them green without
touching the sealed files. **Verify** proves the seal is intact, runs everything fresh, reads
what tests cannot show, tries to break the green, and writes one verdict — `PASS`,
`RISK-ACCEPTED`, or `HARD-STOP` — committed as `verify(<slug>)`. The decisions are what you keep;
the code is disposable.

![Foundation Domain Documents](add-foundation.png)

**Tasks compound into milestones; milestones grow the project.** A milestone lists its tasks up
front, runs each just in time, and is done only when every exit criterion carries its evidence.

---

## 📚 Learn More

- 📖 [Read the book](https://pilotspace.github.io/ADD/) — the full method, chapter by chapter
- 🆕 [What changed in 4.0](https://pilotspace.github.io/ADD/20-whats-new-in-4/) — the engine removed, and why
- ⚖️ [ADD vs spec-kit — the honest comparison](https://pilotspace.github.io/ADD/appendix-h-add-vs-spec-kit/)
- ⚡ [Getting Started](./GETTING-STARTED.md) · 🔍 [Full walkthrough](./add-method/GETTING-STARTED.md)
- 📒 [Beyond code — a month-end close, end to end](./add-method/BEYOND-CODE.md)
- 📊 [Benchmark results](./benchmark/) — every trust and cost claim, reproducible from this repo
- 📦 [Package source](./add-method/README.md) · [Changelog](./add-method/CHANGELOG.md)
- 🗞️ [ADD Across the Org: AI-Driven Development Beyond Code](https://inkpaper-blog.pages.dev/series/add-across-the-org/)

**Releases:** [`@pilotspace/add`](https://www.npmjs.com/package/@pilotspace/add) (npm) · [`pilotspace-add`](https://pypi.org/project/pilotspace-add/) (PyPI)

---

## Star History

<a href="https://www.star-history.com/?repos=pilotspace%2FADD&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=pilotspace/ADD&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=pilotspace/ADD&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=pilotspace/ADD&type=date&legend=top-left" />
 </picture>
</a>

---

<p align="center">MIT License · <a href="https://github.com/pilotspace/ADD">pilotspace/ADD</a></p>
