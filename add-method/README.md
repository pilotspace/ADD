<p align="center">
  <a href="https://www.npmjs.com/package/@pilotspace/add"><img alt="npm version" src="https://img.shields.io/npm/v/@pilotspace/add.svg"></a>
  <a href="https://pypi.org/project/pilotspace-add/"><img alt="PyPI version" src="https://img.shields.io/pypi/v/pilotspace-add.svg"></a>
  <a href="https://github.com/pilotspace/ADD/blob/main/LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
  <a href="https://pilotspace.github.io/ADD/"><img alt="Read the book" src="https://img.shields.io/badge/docs-read%20the%20book-blue.svg"></a>
  <a href="https://github.com/pilotspace/ADD/stargazers"><img alt="GitHub stars" src="https://img.shields.io/github/stars/pilotspace/ADD.svg"></a>
</p>

# ADD — AI-Driven Development

**Your AI's first milestone is always great. ADD is for every milestone after that.**

> A minimal, state-tracked skill for building software when the AI writes the code
> and **you** own the two things it cannot do alone: decide *what* to build, and
> *verify* it is correct.

**The agent is the hands. ADD is the memory, judgment, and conscience — the part
of the team that survives when the context window doesn't.** Memory: the board,
frozen contracts, and living specs on disk (`add.py status` resumes any session
losslessly). Judgment: personas propose each task's lane and the loop learns from
traced outcomes (`add.py deltas`). Conscience: evidence-scored gates, the tamper
tripwire, the security hard-stop.

Native on Claude Code; every other CLI agent follows the same loop through the
phase guides. The full reasoning — *why* every rule exists — is
[the AIDD book](https://pilotspace.github.io/ADD/).

```
  Foundation (context):  DDD  ·  SDD  ·  UDD
  Engine (this skill):   TDD  ⇄  ADD
  Flow per task:  Direction (spec · scenarios · contract · red tests → ONE freeze)
                  → Build (red → green)  → Verify (evidence-scored gate)  ↻
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

The agent sizes it into a milestone (you confirm the shape), drafts the
specification bundle — spec → scenarios → contract → red tests as one Direction
pass (you approve once, at the frozen contract) — then builds and verifies to
green. Full walkthrough: the [10-minute Quickstart](./GETTING-STARTED.md).

## Highlights

- 📉 **Anti-context-rot by design** — every decision lives on disk (`PLAN.md`, frozen contracts, red suites, `.add/state.json`), so a fresh session resumes losslessly; measured flat 1.0 quality across evolving milestones while conversation-carried flows decayed.
- ✅ **Approve once, then let it run** — one human sign-off at the frozen contract; the agent drives Direction → Build → Verify.
- 🔬 **Proof, not promises** — verified against observed behavior and pre-declared expectations, never just a plausible-looking diff; weakening a test to reach green is treated as tampering.
- 💸 **Lean by measurement** — a thin 31-verb state kernel, a 3-call task walk, one file per feature; 3–5× lower per-milestone cost than ADD 1.x.
- 🔒 **Security never gets waved through** — any security finding is a hard stop, human in the loop.
- 🧠 **Personas route the work** — a project-owned persona proposes each task's lane, the freeze ratifies it, outcomes are traced, and the loop reflects on the record (GEPA) so the method adapts to your codebase.
- 🎨 **See it before you build it** — a wireframe and a zero-dependency HTML mock, approved before any code.
- 👥 **Built for teams** — git-native multi-user, N parallel milestones, DAG-scheduled waves; monorepo or multi-repo in one team.
- 🤝 **Works with your AI** — Claude, Copilot, Cursor, Codex, Gemini; install via npm, pip, or the Claude Code plugin.

> _Direction before speed. Trust comes from passing tests — not from reading code and finding it plausible._

## Why ADD — context rot, measured

Every AI tool writes code fast and aces a greenfield first milestone. The unsolved
part is **trust across change**: when the spec evolves in milestone 2 and breaks
compatibility in milestone 3, does the work you already trusted *stay* trusted?

Our benchmark runs the same six-milestone evolving project through each flow under
a pinned model with deterministic probe scoring
([report, revised edition](https://github.com/pilotspace/ADD/blob/main/benchmark/results/2026-07-add-2.0-remeasure.md)).
The causal finding: when ONE continued conversation carried the milestones, every
flow decayed the same way (coverage .92 → .75, an early spec violation carried
through five more milestones). When every milestone instead started a **fresh
session resuming from disk**, ADD held every floor at 1.0 across all six — through
a breaking shape change and a cross-cutting refactor — at a fraction of ADD 1.x's per-milestone cost.

That's the design, in three moves:

- **One file per feature.** Spec, scenarios, contract, test-plan, and gate record all live inline in a single `PLAN.md`. No sprawling doc tree.
- **State on disk, not in chat.** A stdlib-Python kernel tracks where you are in `.add/state.json`, so a fresh session resumes with one command instead of trusting a long conversation's memory.
- **Progressive disclosure.** The skill narrates the whole loop itself and loads a deeper phase reference only when the beat needs it — the context window stays lean.

<sub>**Honesty note:** on this friendly single-app workload a strong model under spec-kit also passed the restart floors (and ran cheaper) — we published the retraction of our own earlier collapse claim when we found the meter defect behind it. What ADD uniquely adds is the *guarantees*: contracts that can't be silently edited, tests that can't be quietly weakened, security findings that can't scroll past.</sub>

## ADD vs skill libraries (e.g. agency-agents)

ADD is the **trust layer** — the gated loop (Direction → Build → Verify) that
decides when work is trusted, plus the on-disk memory it runs on. It answers **how
you trust what gets built**. Skill libraries and role-specific subagents (a backend
expert, a security reviewer) answer **who does the work**. Different layers — they
compose, they don't compete.

ADD's persona loop **distills** a lean, project-fit persona from a teacher corpus
like [agency-agents](https://github.com/msitarzewski/agency-agents) — vendored at
[`personas-teacher/`](./personas-teacher/), read off-build while drafting, never a
runtime dependency — down to the three parts a project needs: **Identity**,
**Critical Rules**, **Success Metrics**. The project then owns that persona.

A distilled persona is an **advisory overlay** during direction, build, or verify:
it shapes *how* a step gets done, never whether it happens. It can't skip a gate,
edit a frozen contract, or wave through a security finding. In 2.0 personas also
propose each task's route (full walk · fast lane · inline); the freeze ratifies it,
the gate traces the outcome, and `add.py deltas` rolls the traces into a per-lane
scoreboard the loop reflects on (GEPA).

**Best setup:** install ADD to drive the loop, keep whatever subagent libraries you
already use. ADD ships ONE `add` agent in the same `.claude/agents/` mechanism as
any other subagent — it coexists with a distilled persona or a built-in expert with
zero conflict, nothing is replaced. Prefer the `add` agent for anything
phase-shaped (verify mode for the adversarial refute-read, build mode for a
red→green batch); reach for another specialist when a piece needs deep domain
expertise the phase guide doesn't carry. **The gates hold no matter who did the
work** — a delegated subagent proposes; the orchestrating agent records.

## Install

Pick your ecosystem — all three install the same skill and tooling:

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

The plugin carries the engine. On first `/add`, the skill materializes it into the
project and scaffolds `.add/` — a self-contained result identical to the npm/pip
flow. No flags needed: the project name is inferred from your folder and the stage
defaults to `prototype` (pass `--name "My App" --stage mvp` to choose up front).

**Already installed?** `npx @pilotspace/add@latest update` (or `pipx run
pilotspace-add update`) re-materializes the skill and tooling while leaving your
project work untouched; add `--check` to see whether a project is behind. **Coming
from 1.x?** One idempotent command — `python3 .add/tooling/add.py migrate` —
converts the whole board (task docs to `PLAN.md`, living 5-DD specs seeded).

**New here?** The [10-minute Quickstart](./GETTING-STARTED.md) walks your first
feature end to end.

This installs:

| Path | What |
|------|------|
| `.claude/skills/add/` | the `add` skill Claude loads — the loop itself, plus three on-demand phase references |
| `.add/tooling/add.py` | the state kernel — scaffolder + tracker, 31 verbs (Python, stdlib only) |
| `.add/personas-teacher/` | the vendored teacher corpus personas are distilled from (off-build reading, never runtime) |
| `.add/DESIGN.md` | (UI projects) front-door to the render-ready UDD foundation — delete it if your project has no UI |

Project state (`.add/state.json`) and the living-documentation files
(`CONVENTIONS.md`, `GLOSSARY.md`, `MODEL_REGISTRY.md`, `dependencies.allowlist`,
`SOUL.md`) are *not* created at install — the installer drops files only;
initialisation is the agent's first move when you run `/add`. On a UI project,
`add.py check` lints the JSON design foundation under `.add/design/`, going red
with a named code on any violation and staying silent when there's no design set.

## Boundaries — what this plugin writes and runs

ADD works *inside your project* — here is exactly what that means:

- **Runs only when you ask.** Nothing executes on install. It acts when you run `/add`. User-initiated, every time.
- **What it runs:** the bundled engine only — `node bin/cli.js` and `python3 .add/tooling/add.py`. No downloaded or remote code.
- **What it writes:** files under your project's `.add/` and the managed guideline block in `CLAUDE.md` / `AGENTS.md`. Never above the project root.
- **Network:** one optional, advisory update check — a single HTTPS GET to the npm registry, ≤ once/24h, 1.5s timeout, fail-open, writes only a one-line note to stderr. Disable with `ADD_NO_UPDATE_CHECK=1`. No telemetry, no analytics.
- **No secrets, no credentials, no privileged access.** Pure local file orchestration.

## Use it

ADD is AI-first: you talk to the agent; it drives the method. The installer detects
which coding agent you're in and drops the context file it reads — so ADD drives
under **Claude Code, Codex, OpenCode, Cursor, Windsurf, Trae, Gemini CLI, GitHub
Copilot, Cline, and Aider** (anything else falls back to a generic `AGENTS.md`).
Only Claude Code runs `/add` natively; every other agent follows the same loop
through `add.py status` / `guide`.

You can hand-drive the CLI too:

```bash
python3 .add/tooling/add.py status      # where am I? (resume point)
```

## The non-negotiables

1. **Direction before speed** — no Build until spec, scenarios, contract, and *red* tests exist.
2. **Trust evidence, not inspection** — a feature is trusted because its tests pass and the non-functional risks (concurrency, security, architecture) were checked.
3. **Never weaken a test or edit a frozen contract** to make the build pass.
4. **No silent skips** — every Verify records `PASS`, `RISK-ACCEPTED`, or `HARD-STOP`. Security findings are always `HARD-STOP`.
5. **Ask, don't guess.**

## The artifacts survive; the code is disposable

The durable asset is the decisions — spec, scenarios, contract, tests. The code is
one implementation that satisfies them and can be regenerated. If the thing you'd
be upset to lose is "the code," you're still working the old way.

## Read the method

- 📖 [Read the book](https://pilotspace.github.io/ADD/) — the full AIDD method, chapter by chapter
- 🔍 [Full hands-on walkthrough](./GETTING-STARTED.md) — one real feature, end to end
- 📊 [Benchmark results](https://github.com/pilotspace/ADD/tree/main/benchmark/results) — every trust and cost claim, measured
- ⚖️ [ADD vs spec-kit — the honest comparison](https://pilotspace.github.io/ADD/appendix-h-add-vs-spec-kit/) — where we tie, where they win, what only ADD guarantees
- 🗞️ [ADD Across the Org: AI-Driven Development Beyond Code](https://inkpaper-blog.pages.dev/series/add-across-the-org/)

## What's new in 2.0

- **Skill-led loop on a thin kernel** — the skill narrates Direction → Build → Verify; `add.py` shrinks to a 31-verb state kernel (54 → 31).
- **`PLAN.md` + one-shot `migrate`** — the per-task file is the plan; a whole 1.x board converts with one idempotent command.
- **Five living 5-DD specs with `delta-append`** — the project's evolving truth, compacted forward instead of rewritten.
- **Persona routes + the GEPA scoreboard** — personas propose lanes, gates trace outcomes, `deltas` shows the per-lane record, and the loop reflects on it.
- **The book stops shipping** — published online only, deep-linked from the engine.

## Develop

```bash
npm test     # runs the Python tests for the tooling (red/green)
```

License: MIT.
