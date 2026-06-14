# ADD — AI-Driven Development

> A minimal, state-tracked Claude Code skill for building software when the AI
> writes the code and **you** own the two things it cannot do alone: decide *what*
> to build, and *verify* it is correct.

ADD is the **orchestration engine** of the AIDD method. It sits on top of a
context foundation (DDD → SDD → UDD) and runs as a red/green TDD ↔ AI-build loop.
The full reasoning — *why* every rule exists — is the AIDD book bundled in
[`docs/`](./docs/README.md). Read it once; keep it open beside you.

```
  Foundation (context):  DDD  ·  SDD  ·  UDD
  Engine (this skill):   TDD  ⇄  ADD
  Flow per feature:  Specify → Scenarios → Contract → Tests → Build → Verify → Observe ↻
```

## Why ADD (and why it is minimal)

Heavy doc-first methods burn your time writing documents and lose the thread
across sessions (context rot). ADD fixes both:

- **One file per feature.** Spec, scenarios, contract, test-plan, and gate record
  all live inline in a single `TASK.md`. No sprawling doc tree.
- **State on disk, not in chat.** A Python tool tracks where you are in
  `.add/state.json`, so a fresh session resumes with one command instead of
  re-reading the repo.
- **Progressive disclosure.** The skill loads only the guide for the phase you are
  in — the context window stays lean.

## Install

Pick your ecosystem — both install the same skill, tooling, and book:

```bash
# Node / npm
npx @pilotspace/add init
```

```bash
# Python / pip
pip install pilotspace-add
pilotspace-add init
```

No flags needed — the project name is inferred from your folder and the stage
defaults to `prototype` (pass `--name "My App" --stage mvp` to choose up front).

**Already installed? Update in place — no re-install:**

```bash
npx @pilotspace/add@latest update      # npm (one shot)
pipx run pilotspace-add update         # pip (one shot)
```

`update` refreshes the skill, tooling, and book to the latest version and leaves
your project state (`state.json`, `PROJECT.md`, milestones, tasks) untouched;
`update --check` reports whether a project is behind.

**New here?** Follow the [10-minute Quickstart](./GETTING-STARTED.md) — it walks
your first feature end to end.

This installs:

| Path | What |
|------|------|
| `.claude/skills/add/` | the `add` skill Claude loads (thin router + per-phase guides) |
| `.add/tooling/add.py` | scaffolder + state tracker (Python, stdlib only) |
| `.add/docs/` | the AIDD book — the method rationale |

Project state (`.add/state.json`) and the living-documentation files (`CONVENTIONS.md`,
`GLOSSARY.md`, `MODEL_REGISTRY.md`, `dependencies.allowlist`) are *not* created
here — the installer drops files only; initialisation is the agent's first move
when you run `/add`.

## Use it

ADD is AI-first: you talk to the agent; it drives the method. In Claude Code, run
**`/add`** and say what you want to build:

> `/add` — *"I want to let users transfer money between their own accounts."*

The agent orients from `state.json`, **sizes your request into a milestone** (you
confirm the shape), then drafts each feature's **specification bundle** — Spec +
Scenarios + Contract + Tests as one bundle — and you give **one approval at the
frozen contract**. A self-driving build→verify run takes it to green; security
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
be upset to lose is "the code," you're still working the old way.

## Read the method

Start at [`docs/README.md`](./docs/README.md) — Foundations → the six steps →
operating it across a team → templates, prompts, and a full worked example.

## Develop

```bash
npm test     # runs the Python tests for the tooling (red/green)
```

License: MIT.
