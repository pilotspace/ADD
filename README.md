# (ADD) AI-Driven Development - LOOP SKILL AGENT
AI Workflow Methodology - AI Tool - MIT
> 1 LOOP skill ⟳ 5 Specs ⟳ 8 Growth-Steps
> 
> **SKILL's assets in**: [.add](https://github.com/pilotspace/ADD/tree/main/.add)

📖 **Read the book online:** <https://pilotspace.github.io/ADD/> 

---

## Highlight

- ✅ **Approve once, then let it run** — one human sign-off at the frozen contract; the agent builds the rest.
- 🔬 **Proof, not promises** — verify on observed behavior and pre-declared build-expectations, not code-reading.
- 🔒 **Security never gets waved through** — any security finding is a HARD-STOP; **Human in-loop**
- 🚀 **Prototype to production** — task → milestone → graduate (analytics-gated) → recorded release, one method.
- 🚀 **Smarter as you go** — competency deltas fold into a living, compacting foundation carried across milestones.
- 🚀 **See it before you build it** — a UDD wireframe + zero-dependency HTML mock, approved before any code.
- 👥 **Built for teams** — support git-native multi-user, N parallel milestones, DAG-scheduled waves.
- 🧩 **One slice across many components** — Support monorepo or multi-repo in teams
- 🤝 **Works with your AI** — Claude, Copilot, Cursor, Codex, Gemini; install via npm, pip, or the Claude Code plugin.

> _Direction before speed. Trust comes from passing tests — not from reading code and finding it plausible._

---

![Foundation Domain Documents](add-foundation.png)

This is a complete guide to **AIDD (AI-Driven Development)** — a way of building software in which an AI agent writes most of the code and people do the two things AI cannot reliably do alone: decide *what* to build, and *verify* that what was built is correct.

Anyone who builds software with AI in the loop: engineers, architects, testers, designers, product owners, and the managers who lead them. No part assumes you have read the others; cross-references point you to what you need.

[ADD Across the Org: AI-Driven Development Beyond Code](https://inkpaper-blog.pages.dev/series/add-across-the-org/)


---

## 🚀 How the ADD work grows

**One task · eight steps · one file.** Every feature is a single **`TASK.md`** that fills in section by section as it moves around the loop — each step produces exactly one durable artifact. The contract freeze is the *one* human approval; the agent drives the rest. (The artifacts are what you keep — the code is disposable.)

![How one TASK.md grows — eight steps circle a single TASK.md file; each step writes its own section, from §0 grounding map through §3 frozen contract (the one approval) to §7 deltas; a red⇄green engine runs between Tests and Build, and Observe loops back to the next Specify](add-task-growth-wheel.png)

**Tasks compound into milestones; milestones grow the project.**

![MILESTONE.md and TASK.md lifecycle — a milestone decomposes breadth-first into a task DAG of TASK.md files run just-in-time; each task's Observe step feeds a spec delta into the next task; the milestone is goal-gated; at close, the ship-review folds lessons into PROJECT.md and CONVENTIONS.md, which loop back to ground the next milestone](add-milestone-task-lifecycle.png)

---

## 🚀 Get Started

![Three steps — 1. Install with npx @pilotspace/add init (also pip, or the Claude Code plugin); 2. Spawn a feature with /add 'your goal' and give one approval at the frozen contract; 3. Resume anytime with /add — state lives in .add/state.json, no context rot](add-install.png)

Here is the whole path, from nothing to your first running feature.

- 🧱 **Prerequisites:** Node ≥ 18 *(npm path)* or Python ≥ 3.10 *(pip path)*
- 🤖 **CLI Coding Agent:** Claude Code, Codex, ...
- ⚡ **Maximize performance with agent's skillset**: https://github.com/ccsk-org/ccsk-cli (recommended — opt-in)

### 1 · Install into your project

From your project root (an empty folder or an existing repo), pick either ecosystem:
> Example [.add](https://github.com/pilotspace/ADD/tree/main/.add)

```bash
# Node / npm
npx @pilotspace/add init

# Update
npx @pilotspace/add update
```

or

```bash
# Python / pip
pip install pilotspace-add && pilotspace-add init

pilotspace-add update
```

or, on **Claude Code**, install the skill straight from the marketplace — no npm or pip needed:

```text
/plugin marketplace add pilotspace/ADD
/plugin install add@add-method
```

### 2 · Spawn your first feature — talk to the agent

In Claude Code, run **`/add`** and say what you want to build:

> `/add 'Describe your goal'`

*Example: `/add simple JWT auth`*

From there the agent runs the on-ramp for you:

1. 🧭 **Orients** from `add.py status` (the resume point) — never re-reading your repo.
2. 📐 **Sizes** your request into a **milestone** (goal · scope · breadth-first tasks ·
   exit criteria) — *you confirm the shape.*
3. ✍️ Drafts each feature's **one-approval front** — Spec + Scenarios + Contract + Tests
   as one bundle — *you give one approval at the frozen contract.*
4. ✅ Runs **build → verify** to green; a security finding always stops back to you.

So your first feature is: **describe it → confirm the milestone → approve the contract → review the result.** Everything in between is the agent.

### 3 · Resume anytime

> `/add status|continue`

*AI will report to you how are current status of this project?*

State lives on disk, not in the chat — close your laptop, come back tomorrow, and this
tells you exactly where you left off. No context rot.

**Go deeper:** 
- the [2-minute Getting Started](./GETTING-STARTED.md) 
- the [full hands-on walkthrough](./add-method/GETTING-STARTED.md) (one real feature, end to end)
- [package source](./add-method/README.md)
- [`CHANGELOG`](./add-method/CHANGELOG.md). 

Releases: 
- `@pilotspace/add` (npm) - https://www.npmjs.com/package/@pilotspace/add
-  `pilotspace-add` (PyPI) — https://pypi.org/project/pilotspace-add/

---

## 📚 Deepdive into ADD Method - [https://pilotspace.github.io/ADD/](https://pilotspace.github.io/ADD/)
