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
<p align="center">Describe the feature. The agent drives the build. You approve once — right where a mistake would actually cost you.</p>

---

## AI work doesn't fail on day one — it rots

Every AI tool ships a beautiful first feature. The failure shows up **across
milestones**: requirements evolve, the conversation gets long, and the agent
quietly re-breaks what it already got right. That decay has a name — **context
rot** — and we measure it instead of hand-waving.

The cause turned out to be simple: **context rot lives in the conversation, not
in the method or the model.** The same agent that decays inside one long chat
holds a perfect line when every milestone restarts from state on disk.

So ADD's answer isn't a bigger context window or a smarter summary. It's this:
**nothing that matters lives in the chat.** Spec, frozen contract, red suite,
gate records — all state on disk. Close the laptop, lose the session, swap the
agent: the next session resumes with one command and loses nothing.

| Same model, six evolving milestones | One long conversation | Fresh session per milestone, resumed from disk |
|---|---|---|
| Requirement coverage | **.92 → .75, never recovered** | **1.0 flat across all six** |
| An early spec violation | carried through **five more milestones**, never re-examined | **never introduced** — each session re-derived the shape from the spec |
| New-feature quality at milestone 6 | still good — but the old promises rotted | **1.0** — new work stays good *and* old work holds |

<sub>[Campaign report, revised edition](./benchmark/results/2026-07-add-2.0-remeasure.md) — pinned model, deterministic probes, no LLM judge.</sub>

## What ADD is

An agent already knows how to do the work — write the code, draft the analysis,
reconcile the ledger. What it *structurally cannot* keep is everything outside one
context window: what's true so far, what was promised, what must never be traded
away. Teams keep that in their most senior people's heads. AI has no head that
survives the session.

> **The agent is the hands. ADD is the memory, judgment, and conscience — the
> part of the team that survives when the context window doesn't.**

Every faculty is a file on disk and a command that shows it — never a promise:

| Faculty | What it holds | See it yourself |
|---|---|---|
| 🧠 **Memory** — *what is true* | the board, frozen contracts, red suites, five living specs | `cli.py status` — a brand-new session resumes mid-build, losing nothing |
| ⚖️ **Judgment** — *how to work here* | personas propose each task's approach; gates record outcomes; lessons land on the spec they belong to | `cli.py deltas` — the carried inventory: every lesson recorded, by lens |
| 🛡️ **Conscience** — *what is trusted* | one freeze per feature, evidence-scored gates, tamper tripwire, security hard-stop | edit a frozen contract and watch the gate refuse — the Musts, Rejects and `gives:` you approved cannot move under a build |

## ✨ Highlights

- 📉 **Your agent stops re-breaking last month's work** — every decision lives on disk, so a fresh session resumes with the full picture instead of a drifting memory. Measured: quality held flat where a long conversation decayed (six-milestone benchmark, n=1 per arm, ADD 2.0.0, pinned model — [report](https://github.com/pilotspace/ADD/blob/main/benchmark/results/2026-07-add-2.0-remeasure.md)).
- ✅ **Stop babysitting the build** — you approve once, at the frozen contract; from there the agent drives Direction → Build → Verify on its own and only comes back when it matters.
- 🔬 **Know it's correct without reading every line** — trust comes from your pre-declared tests passing, never a diff that merely *looks* right; the contract you approved cannot be edited under a build without the change appearing in the record.
- 💸 **Pay ceremony only where it buys something** — most changes take the direct lane and never create a node at all; when one does, a thin 24-verb kernel and a 3-call walk carry it. What you get for the ceremony is concrete: a frozen contract the agent cannot edit, a run receipt bound to the checks it names, and a gate that refuses rather than waves through.
- 🔒 **Never ship a security hole on autopilot** — any security finding is a hard stop with you in the loop, in every mode, even the fully-autonomous ones.
- 🧠 **The method adapts to *your* codebase** — a persona proposes each task's approach, outcomes are recorded, and the lessons land on the spec they belong to.
- 🧭 **The agent reasons before it drafts** — a second mind pressure-tests the plan before the freeze, and returns a recommendation with its confidence per dimension instead of a confident-sounding paragraph. Fluent ≠ true.
- 🙋 **"Who has to live with this?" is a question it cannot skip** — every surface is swept for who *receives* the output and what would make it hard for them, alongside the five correctness dimensions. Provably right and unusable is a failure the freeze now catches.
- 📄 **Everything about a feature in one place** — rules, assumptions, contract, checks, and gate record in a single task file at `.add/tasks/<slug>.md`; no doc tree to hunt through.
- 👥 **Grows with your team** — git-native multi-user, N parallel milestones, DAG-scheduled waves.
- 🤝 **Keep the agent you already use** — Claude, Copilot, Cursor, Codex, Gemini; install via npm, pip, or the Claude Code plugin.

> _Direction before speed. Trust comes from passing tests — not from reading code and finding it plausible._

<sub>**Fine print:** benchmark cells are single-rep (direction, not statistical proof). On this friendly single-app workload a strong model under spec-kit also passed the restart floors, and ran cheaper — the report's revised edition retracts our own earlier "collapse" claim after we found the meter defect behind it. ADD's case rests on the context-rot result and the structural guarantees — not on a rival's failure.</sub>

## ADD vs vanilla — when it earns its keep

ADD isn't free. It asks for one thing vanilla prompting doesn't: **you approve a
frozen contract before any code is written.** That upfront pass is the whole
trade — you spend minutes on direction to buy trust that holds across milestones.

|  | 🏃 **Vanilla** — just prompt the agent | 🛡️ **ADD** |
|---|---|---|
| **First feature** | fastest — start typing | one Direction pass first, then builds |
| **Across milestones** | quality decays; old promises silently break | frozen contracts + red suites re-run; trust holds |
| **What you verify** | you re-read the diff and hope | pre-declared tests pass, or the gate refuses |
| **Resuming later** | re-explain the goal, re-read the repo | one command, read back off the `.add/` bundle, lossless |
| **Cost** | near-zero ceremony up front | one bounded direction pass per milestone — minutes, not a doc tree |
| **Best for** | throwaway scripts, one-shots, spikes | evolving products, multiple milestones, teams |

**Rule of thumb:** building something you'll throw away this week? Vanilla is
fine. Building something you'll still be changing next month? The Direction pass
pays for itself the first time the agent *doesn't* re-break a feature you shipped
three milestones ago.

---

## 🚀 Get Started

![Three steps — 1. Install with npx @pilotspace/add init (also pip, or the Claude Code plugin); 2. Spawn a feature with /add 'your goal' and give one approval at the frozen contract; 3. Resume anytime with /add — state lives on disk in the .add/ bundle, no context rot](add-install.png)

**Prerequisites:** Node ≥ 18 *(npm path)* or Python ≥ 3.10 *(pip path)*, plus a CLI agent — Claude Code, Codex, or similar.

### 1 · Install into your project

From your project root, pick one ecosystem:

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

**Not building software?** The bundle's spec lenses are chosen when the *bundle* is
initialised — which is the agent's first move, not the installer's. ADD ships two sets:
`--profile code` (the default: domain · system · experience · quality · method) and
`--profile doc`, which drops the build-shaped lenses for work whose artifact is a
document, a review, or an analysis. A profile selects *lenses*; it never changes what a
gate demands, and a name ADD does not ship is refused rather than quietly treated as
`code`.

Tell the agent which one you want — or set it by hand after installing:

```bash
python3 .add/tooling/cli.py init --profile doc "My Project"
```

> See a real one: this repo's own [`.add/`](https://github.com/pilotspace/ADD/tree/main/.add) folder.

### 2 · Spawn your first feature

In Claude Code, run **`/add`** and say what you want to build:

```bash
/add 'Let users log in with email + password / SSO, and keep them signed in for 30 days unless they explicitly log out.'
```

The agent runs the on-ramp for you:

1. 🧭 **Orients** from `cli.py status` — never re-reading your whole repo.
2. 📐 **Sizes** your request into a **milestone** — *you confirm the shape.*
3. ✍️ **Drafts** each task's **Direction bundle** — Spec + Scenarios + Contract + red Tests in one pass — *you give one approval, at the frozen contract.*
4. ✅ **Runs** Build → Verify to green; a security finding always stops back to you.

### 3 · Resume anytime

```markdown
/add status | continue
```

State lives on disk, not in the chat. Close your laptop, come back tomorrow, and
pick up exactly where you left off — no context rot.

---

## ⚙️ How ADD Works

**One task · three beats · one file.** Every feature is a single task file at
**`.add/tasks/<slug>.md`** that fills in section by section as the agent walks three
beats — **Direction** (rules → assumptions → frozen contract → red checks, the *one*
human approval), **Build** (red → green, scope-fenced), **Verify** (evidence-scored
gate: `PASS`, `RISK-ACCEPTED`, or `HARD-STOP`). The decisions are what you keep — the
output is disposable.

![Foundation Domain Documents](add-foundation.png)

![How one task file grows — the steps circle a single task file; each writes its own section, from the grounding card through the frozen contract (the one approval) to the closing deltas; a red⇄green engine runs between Checks and Build, and Observe loops back to the next Direction](add-task-growth-wheel.png)

**Tasks compound into milestones; milestones grow the project.**

![Milestone and task lifecycle — a milestone decomposes breadth-first into a task DAG run just-in-time; each task's Observe step feeds a spec delta into the next task; the milestone is goal-gated; at close, the ship-review folds lessons back into the living specs, which ground the next milestone](add-milestone-task-lifecycle.png)

> **Diagrams pending redraw.** These three graphics still render the 2.x file names
> (`PLAN.md`, `MILESTONE.md`, `state.json`) and the retired `§0…§7` section numbering.
> The prose and alt text above are correct for 3.x; the artwork is not, and is tracked
> as an open residual rather than quietly left to read as current.

---

## 📚 Learn More

- 📖 [Read the book](https://pilotspace.github.io/ADD/) — the full AIDD method, chapter by chapter
- ⚖️ [ADD vs spec-kit — the honest comparison](https://pilotspace.github.io/ADD/appendix-h-add-vs-spec-kit/) — where we tie, where they win, what only ADD guarantees
- ⚡ [2-minute Getting Started](./GETTING-STARTED.md) · 🔍 [Full hands-on walkthrough](./add-method/GETTING-STARTED.md) — building software
- 📒 [Beyond code — a month-end close, end to end](./add-method/BEYOND-CODE.md) — the same loop where the artifact is a reconciliation, not a repo
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
