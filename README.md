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
<p align="center"><strong>Describe the feature. The agent drives the build. You approve once — exactly where a mistake would actually cost you.</strong></p>

---

## Why This Exists

Every AI coding tool can write code fast now. The part that never got solved is trust — how do you know it built the *right* thing, and how do you know it's *correct*, without reading every line yourself?

ADD answers both. Freeze the direction *before* any code is written — spec → scenarios → contract → tests — then give **one** human approval, at that frozen contract. From there the agent builds and verifies against real evidence: passing tests and checked risks, never a diff that merely *looks* right.

It's for anyone who builds software with AI in the loop — engineers, architects, testers, designers, product owners, and the people who lead them.

## ✨ Highlights

- ✅ **Approve once, then let it run** — one human sign-off at the frozen contract; the agent builds the rest.
- 🔬 **Proof, not promises** — verified against observed behavior and pre-declared expectations, never just a plausible-looking diff.
- 🔒 **Security never gets waved through** — any security finding is a hard stop, human in the loop.
- 🌱 **Prototype to production** — task → milestone → graduate (analytics-gated) → recorded release, one method throughout.
- 🧠 **Smarter as you go** — lessons fold into a living, compacting foundation carried across milestones.
- 🎨 **See it before you build it** — a wireframe and a zero-dependency HTML mock, approved before any code.
- 👥 **Built for teams** — git-native multi-user, N parallel milestones, DAG-scheduled waves.
- 🧩 **One slice, many components** — monorepo or multi-repo, in one team.
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
# Node / npm
npx @pilotspace/add init
npx @pilotspace/add update    # later, to update
```

or

```bash
# Python / pip
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

> `/add 'Describe your goal'`

*Example: `/add simple JWT auth`*

From there the agent runs the on-ramp for you:

1. 🧭 **Orients** from `add.py status` (the resume point) — never re-reading your whole repo.
2. 📐 **Sizes** your request into a **milestone** (goal · scope · breadth-first tasks ·
   exit criteria) — *you confirm the shape.*
3. ✍️ **Drafts** each feature's **one-approval front** — Spec + Scenarios + Contract + Tests
   as one bundle — *you give one approval, at the frozen contract.*
4. ✅ **Runs** build → verify to green; a security finding always stops back to you.

So your first feature is: **describe it → confirm the milestone → approve the contract → review the result.** Everything in between is the agent.

### 3 · Resume anytime

> `/add status` or `/add continue`

State lives on disk, not in the chat — the agent reports exactly where the project stands. Close your laptop, come back tomorrow, and pick up exactly where you left off. No context rot.

**Want more power?** [ccsk-cli](https://github.com/ccsk-org/ccsk-cli) sharpens your agent's skillset for ADD (optional, recommended).

---

## ⚙️ How ADD Works

**Curious how it works end to end?** Three pictures, zoomed out one level at a time.

**One task · eight steps · one file.** Every feature is a single **`TASK.md`** that fills in section by section as it moves around the loop — each step produces exactly one durable artifact. The contract freeze is the *one* human approval; the agent drives the rest. (The artifacts are what you keep — the code is disposable.)

![Foundation Domain Documents](add-foundation.png)

![How one TASK.md grows — eight steps circle a single TASK.md file; each step writes its own section, from §0 grounding map through §3 frozen contract (the one approval) to §7 deltas; a red⇄green engine runs between Tests and Build, and Observe loops back to the next Specify](add-task-growth-wheel.png)

**Tasks compound into milestones; milestones grow the project.**

![MILESTONE.md and TASK.md lifecycle — a milestone decomposes breadth-first into a task DAG of TASK.md files run just-in-time; each task's Observe step feeds a spec delta into the next task; the milestone is goal-gated; at close, the ship-review folds lessons into PROJECT.md and CONVENTIONS.md, which loop back to ground the next milestone](add-milestone-task-lifecycle.png)

---

## 📚 Learn More

- 📖 [Read the book](https://pilotspace.github.io/ADD/) — the full AIDD method, chapter by chapter
- ⚡ [2-minute Getting Started](./GETTING-STARTED.md)
- 🔍 [Full hands-on walkthrough](./add-method/GETTING-STARTED.md) — one real feature, end to end
- 📦 [Package source](./add-method/README.md) · [Changelog](./add-method/CHANGELOG.md)
- 🗞️ [ADD Across the Org: AI-Driven Development Beyond Code](https://inkpaper-blog.pages.dev/series/add-across-the-org/)

**Releases:** [`@pilotspace/add`](https://www.npmjs.com/package/@pilotspace/add) (npm) · [`pilotspace-add`](https://pypi.org/project/pilotspace-add/) (PyPI)

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=pilotspace/ADD&type=Date)](https://star-history.com/#pilotspace/ADD&Date)

---

<p align="center">MIT License · <a href="https://github.com/pilotspace/ADD">pilotspace/ADD</a></p>
