---
name: add
description: >-
  ADD (AI-Driven Development) — a minimal, state-tracked workflow: the AI writes
  the code, the human owns direction and verification. Drives every feature through
  one lean TASK.md: Specify → Scenarios → Plan → Tests → Build → Verify → Observe,
  red/green TDD built in. Use whenever a repo has `.add/`, or the user says "add",
  "start a task", "next phase", "specify this feature", "ADD method", "AI-driven
  development", or wants spec/tests-first discipline over vague-prompt coding. Also
  resumes work across sessions via `.add/state.json` (never re-read the whole repo).
user-invocable: true
category: workflows
keywords: [add, aidd, ai-driven-development, spec-first, tdd, contract, scenarios, verify, milestone, task-orchestration]
argument-hint: "status | init | continue | --todo <text> | [describe new short goals or expectation]"
license: MIT
metadata:
  author: add
  version: "1.8.0"
---

# ADD — the orchestration engine

You are the orchestrator. ADD keeps the AI fast *and* safe by fixing direction
(spec, scenarios, contract, failing tests) **before** the build, and trusting the
result through passing evidence, not a plausible-looking diff.

**One file = one task.** Each feature is one `.add/tasks/<slug>/TASK.md` — seven step sections,
filled top to bottom; the tool tracks where you are. The **plan** phase unites grounding + frozen
contract + build strategy.

**The `--todo` fast-path.** When the skill ARGUMENTS begin with `--todo`, skip orienting: route to
`add.py todo` and print its output — `--todo <text>` captures · `--todo` lists open todos ·
`--todo --done <id>` closes (engine errors surface verbatim) — then STOP.

## Always start here (orient — do not skip)

Engine: `.add/tooling/add.py` · book: `.add/docs/`. Ensure it is in the project:

- It exists → go to `status` below.
- It does NOT (a plugin install — engine + book ride in it) → materialize once:
  `node "${CLAUDE_PLUGIN_ROOT}/bin/cli.js" init --no-skill` — drops `.add/tooling/` (engine) +
  `.add/docs/` (book) + the agent-agnostic `CLAUDE.md` block; the skill stays in the plugin.

Resume from the tool, never re-read the repo:

```bash
python3 .add/tooling/add.py status
```

`status` names two orient files: `.add/PROJECT.md` (the foundation) and `.add/SOUL.md`
(your **voice** — read each session; human-owned, self-improving — `soul.md`). Then branch on state:

- **No `.add/state.json` yet** (`status` says `no .add/ project found`) → **autonomous setup**: read
  `.add/.intent` if present (the installer's first-build intent — a NOTE, never an init trigger), then
  YOU run `add.py init --name "<inferred>" --stage <picked> --await-lock` and read `phases/0-setup.md`
  to draft the foundation + §1–§3 to the human baseline approval.
- **A task is active** → open its `.add/tasks/<active>/TASK.md`, read the `phase:` marker, load the
  matching `phases/<n>-<phase>.md`. Work *only* that phase.
- **No active task** → first SIZE the request (Intake below), then `add.py new-task <slug> --title "..."`.

**Quick ref** — `status --brief` resume · `advance --fill <draft>` write+continue · `status --section <n>` one §body · `gate PASS` at verify.
**Flag mode** — two human-owned settings (never auto-picked): **fast** (task) · **auto** (mode).
- **fast** — `new-task --fast`: minimal template, freeze-gated; a milestone-free `--fast` task is
  the blessed low-ceremony lane. Jot ideas: `add.py todo "<text>"` · `todo` lists · `todo --done <id>`.
- **auto** — `autonomy: auto` (default) auto-gates verify on evidence; `add.py autonomy set
  conservative|manual` restores a human gate · `new-milestone --await-confirm` confirm-gates
  a milestone's tasks.

## Intake — size a request before creating scope

Classify a raw request BEFORE any scope: read `intake.md`, place it in one bucket — `new-major` ·
`sub-milestone` · `task` · `change-request` — propose `{ bucket, rationale, command }`; the human
confirms. Unsharp intent? **Interview before you size** (`intake.md`). For a milestone bucket draft
`MILESTONE.md` (goal · scope · exit criteria · breadth-first tasks) — read `scope.md` — then
`new-milestone --await-confirm` + `milestone-confirm <slug>` (gates `new-task` until agreed). For
`task`/`change-request`: `add.py new-task` then the first phase guide.

## The flow and which file to load

Load **only the phase you are in** (progressive disclosure):

| Phase | Guide | Produces (TASK.md section) | Who leads | Bundle |
|-------|-------|----------------------------|-----------|--------|
| setup | `phases/0-setup.md` | `.add/` + living docs + first §1–§3 + `SETUP-REVIEW.md` | AI drafts → **human locks** (the baseline approval) | – |
| specify | `phases/1-specify.md` | §1 rules + ranked lowest-confidence flag | AI drafts (co-specify)† | DIRECTION |
| scenarios | `phases/2-scenarios.md` | §2 Given/When/Then | AI drafts† | DIRECTION |
| plan | `phases/3-plan.md` | §3 grounding + frozen shape + build-strategy | AI drafts → **human approves once** (the decision point)† | DIRECTION |
| tests | `phases/4-tests.md` | §4 + red suite in `tests/` | AI drafts† | DIRECTION |
| build | `phases/5-build.md` | code in `src/`, tests green | **AI** | BUILD |
| verify | `phases/6-verify.md` | §6 checks + gate record | **AI auto-gates on evidence**; human on residue/security‡ | VERIFY |
| observe | `phases/7-observe.md` | §7 spec delta | human + AI | VERIFY |

† **The specification bundle (v7).** §1–§4 are one bundle; the human gives **one approval at the
contract freeze**, lowest-confidence-first — `run.md`.
‡ **Verify auto-gate (v6–v7).** Under `autonomy: auto` (default) a run may auto-PASS on complete
evidence (*auto-resolved* — an explicit PASS, not a skip). **Security always escalates** (HARD-STOP);
so do concurrency / architecture residue and a lowered autonomy level — `run.md`.

At every human decision point (intake · bundle approval · gate · milestone close) follow
`report-template.md`: open with the banner then the ARC (goal · done · plan, engine-sourced), then PLAN/SHAPE → SUMMARY →
FLAGS → DECIDED → EVIDENCE → APPROVE → NEXT; show-before-ask; never pre-stamp; the question is a summary, never the artifact.
Read `report-template.md`/`run.md` at most once per session — each phase guide carries its gate card.

In **observe**, emit **lessons learned** tagged by which of the five (`DDD · SDD · UDD · TDD · ADD`)
they improve (written `open`; the human consolidates into `PROJECT.md`) — grammar + lifecycle in
`deltas.md`. At milestone close the retrospective consolidation gathers confirmed deltas into a versioned
foundation — `fold.md`; then compact each spec's stable tail — `compact-foundation.md`. Observe also
tunes your voice: a confirmable delta the human confirms rewrites `SOUL.md` (the human is the only
writer) — `soul.md`.

## Beyond the bundle — load on demand

One trigger = one guide — full prose: `beyond.md`; load only when a trigger fires:

- §3 FROZEN → auto-gated run `run.md` · pipelines `streams.md` · subagent roster `advisor.md` (agent-call-preferred, the default execution mode) ·
  self-score `confidence.md`
- small low-risk task → fast lane `phases/fast-lane.md` · UI feature → UDD loop `design.md`
- milestone goal unmet at `milestone-done` → `loop.md`
- status cues: `MVP covered` → `graduate.md` · closed-milestone cut → `release.md`
- monorepo green-bars → `components.md` · the persona loop (`.add/personas/`) → `docs/18-personas.md` ·
  `sensitivity:` risk classes + `advisor-gate-relax` → `sensitivity.md`

## Non-negotiable rules (from the method)

<constraints>
1. **Direction before speed.** Never start Build until §1–§4 exist and tests are red.
2. **Trust evidence, not inspection.** A feature is trusted because its tests pass and the
   non-functional risks (concurrency, security, architecture) were checked — not because the code
   reads plausibly.
3. **Never weaken a test or edit a frozen contract to make the build pass.** That inverts the method.
   A real change is a *change request* back to Specify.
4. **No silent skips.** Every Verify ends in exactly one recorded outcome: `PASS`, `RISK-ACCEPTED`
   (signed, non-security only), or `HARD-STOP`. A security finding is always `HARD-STOP`.
5. **Ask, don't guess.** If a requirement is unclear, stop and ask the user.
</constraints>

## Advancing

Exit gate met → advance (also syncs the TASK.md marker):

```bash
python3 .add/tooling/add.py advance            # next phase of the active task
python3 .add/tooling/add.py gate PASS          # at verify: records PASS, marks done
python3 .add/tooling/add.py use <slug>         # switch the active task
```

## Depth by stage

The steps never change; their depth does (stage from `add.py status`):

- **prototype** — light; throwaway code; design/experience is the point.
- **poc** — contract/tests/build deep on the single riskiest slice only.
- **mvp** — full flow, narrow scope, light observation.
- **production** — full rigor + the observe loop; reached via the `graduate.md` orchestration
  (`MVP covered → propose graduation`), never a bare `stage production` flip.

## The method rationale

The full method (the *why*) is the AIDD book in `.add/docs/`; each phase guide
points to its chapter. Read it only when a decision is genuinely unclear — never duplicate it here.
