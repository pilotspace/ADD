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
> *verify* it is correct. Native on Claude Code; every other CLI coding agent
> follows the same loop through the phase guides.

**The agent is the hands. ADD is the memory, judgment, and conscience — the part
of the team that survives when the context window doesn't.** Memory: the board,
frozen contracts, and living specs on disk (`add.py status` resumes any session
losslessly). Judgment: personas propose each task's lane and the loop learns from
the traced outcomes (`add.py deltas`). Conscience: evidence-scored gates, the
tamper tripwire, the security hard-stop. It sits on top of a context foundation
(DDD → SDD → UDD) and runs as a red/green TDD ↔ AI-build loop.
The full reasoning — *why* every rule exists — is [the AIDD book, published
online](https://pilotspace.github.io/ADD/). Read it once; keep it open beside you.

```
  Foundation (context):  DDD  ·  SDD  ·  UDD
  Engine (this skill):   TDD  ⇄  ADD
  Flow per task:  Direction (spec · scenarios · contract · red tests → ONE freeze)
                  → Build (red → green)  → Verify (evidence-scored gate)  ↻
```

## Quick Start

```bash
# Node / npm
npx @pilotspace/add init
```

```bash
# Python / pip
pip install pilotspace-add && pilotspace-add init
```

Then, in your coding agent, say what you want to build:

> `/add` — *"Let users log in with email + password / SSO, and keep them signed in for 30 days unless they explicitly log out."*

The agent sizes it into a milestone (you confirm the shape), drafts the
specification bundle — spec → scenarios → contract → red tests as one Direction
pass (you approve once, at the frozen contract), then builds and verifies to
green. Full detail below — **Install**, **Use it**, and the
[10-minute Quickstart](./GETTING-STARTED.md).

## Highlights

- 📉 **Anti-context-rot by design** — every decision lives on disk (`PLAN.md`, frozen contracts, red suites, `.add/state.json`), so a fresh session resumes losslessly; measured flat 1.0 quality across evolving milestones while conversation-carried flows decayed.
- ✅ **Approve once, then let it run** — one human sign-off at the frozen contract; the agent drives Direction → Build → Verify.
- 🔬 **Proof, not promises** — verified against observed behavior and pre-declared expectations, never just a plausible-looking diff; weakening a test to reach green is treated as tampering.
- 💸 **Lean by measurement** — a thin 31-verb state kernel, a 3-call task walk, one file per feature; $2.20 per trusted milestone vs spec-kit's $3.90 in the latest head-to-head.
- 🔒 **Security never gets waved through** — any security finding is a hard stop, human in the loop.
- 🧠 **Personas route the work** — a project-owned persona proposes each task's lane, the freeze ratifies it, outcomes are traced, and the loop reflects on the record (GEPA) so the method adapts to your codebase.
- 🎨 **See it before you build it** — a wireframe and a zero-dependency HTML mock, approved before any code.
- 👥 **Built for teams** — git-native multi-user, N parallel milestones, DAG-scheduled waves.
- 🧩 **One slice, many components** — monorepo or multi-repo, in one team.
- 🤝 **Works with your AI** — Claude, Copilot, Cursor, Codex, Gemini; install via npm, pip, or the Claude Code plugin.

> _Direction before speed. Trust comes from passing tests — not from reading code and finding it plausible._

## Why ADD — the pain point is context rot, and we measured it

Every AI coding tool can write code fast now, and every flow we benchmark aces a
greenfield first milestone. The unsolved part is **trust across change**: when the
spec evolves in milestone 2 and breaks compatibility in milestone 3, does the work
you already trusted *stay* trusted?

Our benchmark runs the same six-milestone evolving project through each flow under
a pinned model with deterministic probe scoring
([report, revised edition](https://github.com/pilotspace/ADD/blob/main/benchmark/results/2026-07-add-2.0-remeasure.md)).
The causal finding: when ONE continued conversation carried the milestones, every
flow decayed the same way (coverage .92 → .75, with an early list-shape spec
violation carried through five further milestones, never re-examined). When every
milestone instead started a **fresh session resuming from disk**, ADD held every
floor at 1.0 across all six milestones — through a breaking shape change and a
cross-cutting refactor — with zero regressions, at ~$2.90 per milestone (a 3–5×
cut vs ADD 1.x's $4.65–13.94 per trusted feature). Honesty note, from the same
report: on this friendly workload a strong model under spec-kit also passed the
restart-mode floors (and ran cheaper) — we published the retraction of our own
earlier collapse claim when we found the meter defect behind it. What ADD uniquely
adds is the *guarantees*: contracts that can't be silently edited, tests that
can't be quietly weakened, security findings that can't scroll past.

That's the design, in three moves:

- **One file per feature.** Spec, scenarios, contract, test-plan, and gate record
  all live inline in a single `PLAN.md`. No sprawling doc tree.
- **State on disk, not in chat.** A stdlib-Python kernel tracks where you are in
  `.add/state.json`, so a fresh session resumes with one command instead of
  re-reading the repo — and instead of trusting a long conversation's memory.
- **Progressive disclosure.** The skill narrates the whole loop itself and loads a
  deeper phase reference only when the beat needs it — the context window stays
  lean.

## Where ADD fits vs. skill libraries (e.g. agency-agents)

ADD is the **trust layer** — the gated loop (Direction → Build → Verify)
that decides when work is trusted, and the on-disk memory it runs on. It is not a
catalog of ready-made expert personas. Skill libraries like [agency-agents](https://github.com/msitarzewski/agency-agents), or
role-specific subagents (a backend expert, a security reviewer, a senior Java engineer), sit at a
different layer: they answer **who does the work** — a domain stance, vocabulary, and craft rules
for one kind of task. ADD answers **how you trust what gets built**, no matter who or what wrote it.

The two layers compose; they don't compete. ADD's persona loop **distills** a lean, project-fit
persona from a teacher corpus like agency-agents — vendored at
[`personas-teacher/`](./personas-teacher/), read **off-build** by the AI while drafting a persona,
never a runtime dependency — down to the three parts a project actually needs: **Identity** (the
stance), **Critical Rules** (the non-negotiables), and **Success Metrics** (the done-bar). The
project then owns that persona outright.

A distilled persona is applied as an **advisory overlay** during direction, build, or verify — it
shapes *how* a step gets done, never whether it happens: it can't skip a gate, edit a frozen
contract, or wave through a security finding. In 2.0 personas also carry **task-kinds** and
propose each task's route (full walk · fast lane · inline); the freeze ratifies the route, the
gate traces the outcome, and `add.py deltas` rolls the traces into a per-lane scoreboard the
loop reflects on (GEPA). That gated loop is what ADD contributes underneath any persona,
distilled or not.

## Best setup: ADD alongside other agent libraries

1. **Install ADD** (below) — it drives the loop: which phase you're in, what needs your approval,
   whether something is proven.
2. **Keep whatever subagent libraries you already use.** ADD ships ONE `add` agent in the same
   `.claude/agents/` mechanism as any other Claude Code subagent — the spawn names the mode
   (direction · build · verify · advise · persona) and the agent loads that beat's guide plus the
   best-fit persona. It coexists with a distilled persona, an agency-agents-derived specialist,
   or a built-in expert with zero conflict; nothing is replaced.
3. **Prefer the `add` agent for anything phase-shaped** — spawn it in verify mode for the
   independent adversarial refute-read, in build mode for a red→green batch — before an ad-hoc
   spawn. Reach for another specialist when a piece needs deep domain expertise the phase guide
   doesn't carry (a Java-specific review, a payments-domain lens).
4. **The gates hold no matter who did the work.** A delegated subagent proposes; the orchestrating
   agent records. A security finding is always a `HARD-STOP`, and a low self-reported confidence
   means refine or re-spawn — never a pass — whichever subagent produced it.

## Install

Pick your ecosystem — all three install the same skill and tooling:

```bash
# Node / npm
npx @pilotspace/add init
```

```bash
# Python / pip
pip install pilotspace-add
pilotspace-add init
```

```text
# Claude Code plugin — no npm or pip needed
/plugin marketplace add pilotspace/ADD
/plugin install add@add-method
```

The plugin carries the engine. On first `/add`, the skill materializes it into the
project (`node "${CLAUDE_PLUGIN_ROOT}/bin/cli.js" init --no-skill`) and scaffolds
`.add/` — a self-contained, portable result identical to the npm/pip flow. The skill stays
in the plugin, so nothing is duplicated.

No flags needed — the project name is inferred from your folder and the stage
defaults to `prototype` (pass `--name "My App" --stage mvp` to choose up front).

**Already installed?** Refresh to the latest without a re-install —
`npx @pilotspace/add@latest update` (or `pipx run pilotspace-add update`)
re-materializes the skill and tooling while leaving your project work
(`.add/state.json`, `PROJECT.md`, milestones, tasks) untouched; add `--check` to
see whether a project is behind the installed package. Coming from 1.x? One
command — `python3 .add/tooling/add.py migrate` — converts the whole board
(task docs to `PLAN.md`, living 5-DD specs seeded); it's idempotent and refuses
to guess on conflicts.

**New here?** Follow the [10-minute Quickstart](./GETTING-STARTED.md) — it walks
your first feature end to end.

This installs:

| Path | What |
|------|------|
| `.claude/skills/add/` | the `add` skill Claude loads — the loop itself, plus three on-demand phase references |
| `.add/tooling/add.py` | the state kernel — scaffolder + tracker, 31 verbs (Python, stdlib only) |
| `.add/personas-teacher/` | the vendored teacher corpus personas are distilled from (off-build reading, never runtime) |
| `.add/DESIGN.md` | (UI projects) the prose front-door to the **render-ready UDD foundation** — delete it if your project has no UI |

The AIDD book itself no longer installs into projects — it lives online at
[pilotspace.github.io/ADD](https://pilotspace.github.io/ADD/), and the engine
deep-links the exact chapter whenever a gate or guide cites its rationale.

On a UI project, UDD gives the AI a frozen design ground to draft from: `DESIGN.md`
plus a lintable JSON foundation under `.add/design/` (design tokens · component
catalog · prototype trees). `add.py check` lints that foundation, going red with a
named code on any layer, catalog, tree, or cross-file violation — and staying
silent when a project has no design set.

Project state (`.add/state.json`) and the living-documentation files (`CONVENTIONS.md`,
`GLOSSARY.md`, `MODEL_REGISTRY.md`, `dependencies.allowlist`, `SOUL.md` — the AI's
human-owned voice) are *not* created here — the installer drops files only;
initialisation is the agent's first move when you run `/add`.

## What this plugin does, writes, and runs (boundaries)

ADD is a development methodology, so by design it works *inside your project* — here is
exactly what that means, so there are no surprises:

- **Runs only when you ask.** Nothing executes on install. The skill acts when you run
  `/add` (or another agent follows the guideline block). It is user-initiated, every time.
- **What it runs:** the bundled engine and bootstrapper only — `node bin/cli.js` and
  `python3 .add/tooling/add.py`. No downloaded or remote code is executed; everything it
  runs ships in the package.
- **What it writes:** files under your project's `.add/` (state, milestones, tasks) and
  the managed guideline block in `CLAUDE.md` / `AGENTS.md`. On a plugin install
  it also materializes the engine into `.add/` on first run. It writes nowhere
  outside the project working directory; it never touches files above the project root.
- **Network:** one optional, advisory update check. On `status` / `guide` the engine may
  make a single HTTPS GET to `https://registry.npmjs.org/@pilotspace/add/latest` to see if
  a newer version exists — at most once per 24h (cached in `.update-cache.json`), 1.5s
  timeout, fail-open (offline ⇒ silent no-op). It only writes a one-line note to **stderr**
  and never changes a command's output or exit code. Disable it entirely with
  `ADD_NO_UPDATE_CHECK=1`. No other network access, no telemetry, no analytics.
- **No secrets, no credentials, no privileged access.** Pure local file orchestration.

## Use it

ADD is AI-first: you talk to the agent; it drives the method. In Claude Code, run
**`/add`** and say what you want to build:

> `/add` — *"Let users log in with email + password / SSO, and keep them signed in for 30 days unless they explicitly log out."*

**Works with your agent.** The installer detects which coding agent you're in and
drops the context file it reads — so ADD drives through the CLI under **Claude Code,
Codex, OpenCode, Cursor, Windsurf, Trae, Gemini CLI, GitHub Copilot, Cline, and
Aider** (anything else falls back to a generic `AGENTS.md`). Only Claude Code runs
the `/add` skill natively; every other agent follows the same loop through the
phase guides via `add.py status` / `guide`.

The agent orients from `state.json`, **sizes your request into a milestone** (you
confirm the shape), then drafts each task's **specification bundle** — Spec +
Scenarios + Contract + Tests as one Direction pass — and you give **one approval at
the frozen contract**. A self-driving build→verify run takes it to green; security
findings always stop back to you.

Under the hood the agent runs the CLI as its hands — and you can hand-drive it too:

```bash
python3 .add/tooling/add.py status      # where am I? (resume point)
```

## The non-negotiables

1. **Direction before speed** — no Build until spec, scenarios, contract, and *red*
   tests exist.
2. **Trust evidence, not inspection** — a feature is trusted because its tests pass
   and the non-functional risks (concurrency, security, architecture) were checked.
3. **Never weaken a test or edit a frozen contract** to make the build pass.
4. **No silent skips** — every Verify records `PASS`, `RISK-ACCEPTED`, or
   `HARD-STOP`. Security findings are always `HARD-STOP`.
5. **Ask, don't guess.**

## The artifacts survive; the code is disposable

The durable asset is the decisions — spec, scenarios, contract, tests. The code is
one implementation that satisfies them and can be regenerated. If the thing you'd
be upset to lose is "the code," you're still working the old way. This is also the
anti-context-rot stance in one sentence: the artifacts on disk, not the
conversation, are the project's memory.

## Read the method

Start at [the book](https://pilotspace.github.io/ADD/) — Foundations → the loop →
operating it across a team → templates, prompts, and a full worked example.

More entry points:

- 📖 [Read the book online](https://pilotspace.github.io/ADD/) — the full AIDD method, chapter by chapter
- 🔍 [Full hands-on walkthrough](./GETTING-STARTED.md) — one real feature, end to end
- 📊 [Benchmark results](https://github.com/pilotspace/ADD/tree/main/benchmark/results) — every trust and cost claim, measured
- 🗞️ [ADD Across the Org: AI-Driven Development Beyond Code](https://inkpaper-blog.pages.dev/series/add-across-the-org/)

## What's new in 2.0

- **Skill-led loop on a thin kernel** — the skill narrates Direction → Build →
  Verify; `add.py` shrinks to a 31-verb state kernel (54 → 31).
- **`PLAN.md` + one-shot `migrate`** — the per-task file is the plan; a whole 1.x
  board converts with one idempotent command.
- **Five living 5-DD specs with `delta-append`** — the project's evolving truth,
  compacted forward instead of rewritten.
- **Persona routes + the GEPA scoreboard** — personas propose lanes, gates trace
  outcomes, `deltas` shows the per-lane record, and the loop reflects on it.
- **The book stops shipping** — published online only, deep-linked from the engine.
- **Measured**: every trust floor 1.0 across the 3-milestone benchmark at $2.20 per
  trusted milestone; plus a new `--session-mode continue` harness that measures
  context rot itself.

## Develop

```bash
npm test     # runs the Python tests for the tooling (red/green)
```

License: MIT.
