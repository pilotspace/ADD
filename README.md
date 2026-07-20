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
<p align="center">Describe the feature. The agent drives the build. You approve once — exactly where a mistake would actually cost you.</p>

---

## The problem: AI coding doesn't fail on day one — it rots

Every AI coding tool ships a beautiful first feature. The failure mode of AI-driven
development is **what happens across milestones**: requirements evolve, the
conversation gets long or gets lost, and the agent quietly re-breaks things it
already got right. That decay has a name — **context rot** — and we measure it
instead of hand-waving about it.

Our benchmark runs the *same* six-milestone project (CRUD → business rules + auth
→ a breaking shape change → filters/pagination/recurring → a cross-cutting rooms
refactor → correctness hardening) through each flow, scored by deterministic
probes — no LLM judge, no vibes ([campaign report, revised
edition](./benchmark/results/2026-07-add-2.0-remeasure.md), pinned model, same
prompts per arm):

| six evolving milestones, same model | one continued conversation | fresh session per milestone, resuming from disk |
|---|---|---|
| requirement coverage | **.92 → .80 → .75 → decayed** — never recovered the early loss | **1.0 flat, all six milestones**, zero regressions |
| the WM1 deviation (list-shape spec violation) | carried through **five further milestones** — never re-examined, even while editing that exact endpoint | never introduced: each session re-derived the shape from the spec, 4 of 4 runs |
| new-feature quality at milestone 6 | still 1.0 — *new* work stays good while old promises rot | 1.0 |

The finding that shaped ADD 2.0: **context rot is real, measurable, and lives in
the conversation — not in the method, and not in the model.** The same agent that
decays inside one long conversation holds a perfect line when every milestone
restarts from state on disk. So the deciding question for any AI dev flow is: *is
your on-disk state good enough to restart from, every time?* ADD is built so the
answer is structurally yes — and honesty note: on this friendly single-app
workload a strong model with spec-kit's files also passed the restart bar; the
report says so plainly. The gap ADD keeps is what's *guaranteed* rather than
usual: contracts can't be silently edited, tests can't be quietly weakened,
security findings can't scroll past.

ADD's answer isn't a longer context window or a smarter summary. It's this:
**nothing that matters lives in the chat.** The spec, the frozen contract, the red
suite, the gate records — all of it is state on disk. Close the laptop, lose the
session, swap the agent: the next session resumes with one command and loses
nothing. Long conversations don't need surviving when they're unnecessary.

## What ADD is

An agent already knows how to write code. What it structurally *cannot* keep is
everything that lives outside one context window: what's true so far, what was
promised, what worked last time, what must never be traded away. Human teams keep
those in senior engineers' heads — and AI has no head that survives the session.

> **The agent is the hands. ADD is the memory, judgment, and conscience — the part
> of the team that survives when the context window doesn't.**

Every faculty is a file on disk and a command that shows it — never a promise:

| Faculty | What it holds | See it yourself |
|---|---|---|
| 🧠 **Memory** — *what is true* | the board, frozen contracts, red suites, five living specs compacting forward | `add.py status` — a brand-new session resumes mid-build, losing nothing |
| ⚖️ **Judgment** — *how to work here* | personas propose each task's lane; gates trace outcomes; the loop reflects on the record (GEPA) | `add.py deltas` — the per-lane scoreboard: what got gated, what passed, what healed |
| 🛡️ **Conscience** — *what is trusted* | one freeze per feature, evidence-scored gates, tamper tripwire, security hard-stop | edit a frozen test and watch the gate refuse — weakening a test to get green is structurally impossible, not just unusual |

## The pain points every coding agent faces — and ADD's receipt for each

These are the failure modes users of *any* agent tool know first-hand. Each row is
what ADD does about it, with the evidence from the
[benchmark](./benchmark/results/2026-07-add-2.0-remeasure.md) — same project, same
model, deterministic probes, retractions published when the meter itself was wrong:

| Pain point you've hit | What ADD does | Receipt |
|---|---|---|
| **The session degrades** — long conversations drift; compaction silently drops constraints | Nothing that matters lives in the chat; every milestone starts a fresh session from the board | Measured: one continued conversation decayed **.92 → .75** and carried an early spec violation through **five further milestones**; fresh sessions from disk held **1.0 flat** across all six |
| **An early wrong turn becomes permanent** — the agent keeps trusting its own past decisions over the spec | The frozen contract and red suite are re-read from disk every session — the agent's memory of itself never outranks the written spec | The locked-in deviation appeared **only** in conversation-carry mode, in every flow tried; never once in a restart-from-disk run |
| **It games the tests** — the fastest path to green is deleting the assertion | Weakening a frozen test is *tampering* — the gate refuses; recovery requires a human-visible re-cross | A structural guarantee, not a habit: the tamper tripwire fires on any frozen-suite edit during build (WV2 measured no arm gaming on friendly workloads — this floor exists for the day that stops being true) |
| **A confident diff that's wrong** — it looks right, so it merges | Trust comes from pre-declared expectations passing, never from a plausible diff; you approve once, at the frozen contract | Coverage **1.0 on all six milestones** including a cross-cutting refactor, scored by probes the agent never sees |
| **Every session starts over** — re-reading the repo, re-explaining the goal, paying for it | One command orients from `state.json`; the skill loads only the beat you're in | **~$2.90 per milestone** at full discipline — a **3–5× cut vs ADD 1.x** ($4.65–13.94), competitive with the lightest structured flows |
| **Security findings scroll past** in auto-accept mode | A security finding is a `HARD-STOP` — the one gate no flag, persona, or lane can soften | A structural floor in every mode, including the fully-autonomous lanes |

## Why This Exists

Every AI coding tool can write code fast now. The part that never got solved is
trust — how do you know it built the *right* thing, and how do you know it's
*correct*, without reading every line yourself?

ADD answers both. Freeze the direction *before* any code is written — spec,
scenarios, contract, and *red* tests as one bundle — then give **one** human
approval, at that frozen contract. From there the agent builds and verifies against
real evidence: passing tests and checked risks, never a diff that merely *looks*
right. And because yesterday's contracts and tests stay frozen and re-run, the
things you already trust **stay** trusted while the project moves.

It's for anyone who builds software with AI in the loop — engineers, architects,
testers, designers, product owners, and the people who lead them.

## ✨ Highlights — what 2.0 is

- 📉 **Anti-context-rot by design** — state on disk, fresh sessions lossless; measured flat 1.0 across evolving milestones while conversation-carried flows decayed.
- ✅ **Approve once, then let it run** — one human sign-off at the frozen contract; the agent drives Direction → Build → Verify.
- 🔬 **Proof, not promises** — deterministic gates on observed behavior; never a plausible-looking diff. Weakening a test to get green is treated as tampering.
- 💸 **Lean enough to be the cheap option** — a thin 31-verb state kernel and a 3-call task walk; **$2.20 per trusted milestone** vs spec-kit's $3.90 in our latest head-to-head.
- 🔒 **Security never gets waved through** — any security finding is a hard stop, human in the loop.
- 🧠 **Personas that learn your project** — the routing brain: a persona proposes each task's lane, outcomes are traced, and the loop reflects on what worked (GEPA) so the method adapts to *your* codebase.
- 📄 **One file per feature** — spec, scenarios, contract, tests, and gate record live in a single `PLAN.md`; five living specs carry the project's evolving truth.
- 🎨 **See it before you build it** — a wireframe and a zero-dependency HTML mock, approved before any code.
- 👥 **Built for teams** — git-native multi-user, N parallel milestones, DAG-scheduled waves.
- 🤝 **Works with your AI** — Claude, Copilot, Cursor, Codex, Gemini; install via npm, pip, or the Claude Code plugin.

> _Direction before speed. Trust comes from passing tests — not from reading code and finding it plausible._

---

## 🚀 Get Started

![Three steps — 1. Install with npx @pilotspace/add init (also pip, or the Claude Code plugin); 2. Spawn a feature with /add 'your goal' and give one approval at the frozen contract; 3. Resume anytime with /add — state lives in .add/state.json, no context rot](add-install.png)

Here's the whole path, from nothing to your first running feature.

**Prerequisites:** Node ≥ 18 *(npm path)* or Python ≥ 3.10 *(pip path)*, plus a CLI coding agent — Claude Code, Codex, or similar.

### 1 · Install into your project

From your project root (an empty folder or an existing repo), pick one ecosystem:

```bash
# Node / npm in project folder
npx @pilotspace/add init
npx @pilotspace/add update    # later, to update
```

or

```bash
# Python / pip in project folder
pip install pilotspace-add && pilotspace-add init
pilotspace-add update         # later, to update
```

or, on **Claude Code**, install the skill straight from the marketplace — no npm or pip needed:

```text
/plugin marketplace add pilotspace/ADD
/plugin install add@add-method
```

> See a real one: this repo's own [`.add/`](https://github.com/pilotspace/ADD/tree/main/.add) folder.

### 2 · Spawn your first feature — talk to the agent

In Claude Code, run **`/add`** and say what you want to build:

```bash
# in claude code -> spawn ADD skill
> /add 'Describe your goal'
```

*Example*: 

```bash
/add 'Let users log in with email + password / SSO, and keep them signed in for 30 days unless they explicitly log out.'
```

From there the agent runs the on-ramp for you:

1. 🧭 **Orients** from `add.py status` (the resume point) — never re-reading your whole repo.
2. 📐 **Sizes** your request into a **milestone** (goal · scope · breadth-first tasks · exit criteria) — **you confirm the shape.**
3. ✍️ **Drafts** each task's whole **Direction bundle** — Spec + Scenarios + Contract + red Tests in one pass — *you give one approval, at the frozen contract.*
4. ✅ **Runs** Build → Verify to green; a security finding always stops back to you.

### 3 · Resume anytime

```markdown
/add status | continue
```

State lives on disk, not in the chat — the agent reports exactly where the project
stands. Close your laptop, come back tomorrow, and pick up exactly where you left
off. No context rot: in our measurements this is the difference between quality
decaying every milestone (−.08 coverage/milestone in one continued conversation)
and holding flat at 1.0.

**Want more power?** [ccsk-cli](https://github.com/ccsk-org/ccsk-cli) sharpens your agent's skillset for ADD (optional, recommended).

---

## ⚙️ How ADD Works

**Curious how it works end to end?** Three pictures, zoomed out one level at a time.

**One task · three beats · one file.** Every feature is a single **`PLAN.md`** that
fills in section by section as the agent walks three beats — **Direction** (spec →
scenarios → frozen contract → red tests, the *one* human approval), **Build**
(red → green, scope-fenced), **Verify** (evidence-scored gate: `PASS`,
`RISK-ACCEPTED`, or `HARD-STOP`). Each beat writes its own sections; the artifacts
are what you keep — the code is disposable.

![Foundation Domain Documents](add-foundation.png)

![How one PLAN.md grows — the steps circle a single PLAN.md file; each writes its own section, from §0 grounding map through §3 frozen contract (the one approval) to §7 deltas; a red⇄green engine runs between Tests and Build, and Observe loops back to the next Specify](add-task-growth-wheel.png)

**Tasks compound into milestones; milestones grow the project.**

![MILESTONE.md and PLAN.md lifecycle — a milestone decomposes breadth-first into a task DAG of PLAN.md files run just-in-time; each task's Observe step feeds a spec delta into the next task; the milestone is goal-gated; at close, the ship-review folds lessons into PROJECT.md and CONVENTIONS.md, which loop back to ground the next milestone](add-milestone-task-lifecycle.png)

---

## 📊 The receipts

Every claim above is a number in a committed report, reproducible from this repo's
[`benchmark/`](./benchmark/) harness (deterministic probes, pinned model, per-run
records):

- [ADD 2.0 remeasure + context-rot campaign](./benchmark/results/2026-07-add-2.0-remeasure.md) — add vs spec-kit, fresh vs one-continued-conversation
- [Earlier campaigns](./benchmark/results/) — hostile-change resistance, ceremony-cost anatomy, multi-arm sweeps

Honest fine print: cells are single-rep (direction, not statistical proof); on the
friendly single-app workload a strong model passed the floors under spec-kit too,
and spec-kit's rep ran cheaper — the report's revised edition retracts our own
earlier collapse claim after we found the meter defect behind it. ADD's case rests
on the context-rot result, the structural guarantees, and the 3–5× cost cut vs its
own 1.x — not on a rival's failure.

## 📚 Learn More

- 📖 [Read the book](https://pilotspace.github.io/ADD/) — the full AIDD method, chapter by chapter
- ⚖️ [ADD vs spec-kit — the honest comparison](https://pilotspace.github.io/ADD/appendix-h-add-vs-spec-kit/) — where we tie, where they win, what only ADD guarantees
- ⚡ [2-minute Getting Started](./GETTING-STARTED.md)
- 🔍 [Full hands-on walkthrough](./add-method/GETTING-STARTED.md) — one real feature, end to end
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
