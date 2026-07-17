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

**One plan = one task.** Each feature is one `.add/tasks/<slug>/TASK.md` — the engine-known
spine; its §3 PLAN (grounding · contract · scope · measurable Target) is the core artifact.
Shard free context files beside it in the task folder — the AI owns that architecture.

**The `--todo` fast-path.** When the skill ARGUMENTS begin with `--todo`, skip orienting: route to
`add.py todo` and print its output — `--todo <text>` captures · `--todo` lists open todos ·
`--todo --done <id>` closes (engine errors surface verbatim) — then STOP.

## Always start here (orient — do not skip)

Engine: `.add/tooling/add.py` · book: `.add/docs/`. Ensure it is in the project:

- It exists → go to `status` below.
- It does NOT (a plugin install — engine + book ride in it) → materialize once:
  `node "${CLAUDE_PLUGIN_ROOT}/bin/cli.js" init --no-skill` — drops `.add/tooling/` (engine) +
  `.add/docs/` (book) + the agent-agnostic `CLAUDE.md` block; the skill stays in the plugin.

Resume from the tool (COLD start), never re-read the repo — mid-flow, trust each verb's
`next:` footer:

```bash
python3 .add/tooling/add.py status --brief
```

Then read the foundation map `add.py status --foundation` (one section: `--foundation "Users"` · `--all` full) + `.add/SOUL.md` (**voice** — `soul.md`). Then branch on state:

- **No `.add/state.json` yet** (`status` says `no .add/ project found`) → **autonomous setup**: read
  `.add/.intent` if present (the installer's first-build intent — a NOTE, never an init trigger), then
  YOU run `add.py init --name "<inferred>" --stage <picked> --await-lock` and drive the setup span of
  `phases/direction.md` — foundation + first bundle to the human baseline `lock`.
- **A task is active** → open its `.add/tasks/<active>/TASK.md`, read the `phase:` marker, work that
  beat per the loop below.
- **No active task** → first SIZE the request (Intake below), then `add.py new-task <slug> --title "..."`.

**Quick ref** — `status --brief` resume · `advance --fill <draft>` write+continue · `status --section <n>` one §body · `gate PASS` at verify.
**Flag mode** — the fitting persona proposes; the human ratifies (flag + freeze), never auto-applied.
- **route** — propose the lane in the TASK header: `route: <full|fast|oneshot> · routed-by:
  <persona:<slug> | human> — <why>`; the freeze records the ratified lane (audit measures a
  missing record — never blocks).
- **fast** — `new-task --fast`: lean derived render, freeze-gated; a milestone-free `--fast` task is
  the blessed low-ceremony lane.
- **auto** — `autonomy: auto` (default) auto-gates verify on evidence; `add.py autonomy set
  conservative|manual` restores a human gate · `new-milestone --await-confirm` confirm-gates
  a milestone's tasks.

## Intake — size a request before creating scope

Classify a raw request BEFORE any scope: read `intake.md`, place it in one bucket — `new-major` ·
`sub-milestone` · `task` · `change-request` — propose `{ bucket, rationale, command }`; the human
confirms. Unsharp intent? **Interview before you size** (`intake.md`). For a milestone bucket draft
`MILESTONE.md` (goal · scope · exit criteria · breadth-first tasks) — read `scope.md` — then
`new-milestone --await-confirm` + `milestone-confirm <slug>` (gates `new-task` until agreed). For
`task`/`change-request`: `add.py new-task`, then beat 1 above.

## The 3-beat loop (inline — this file IS the loop; references load on demand)

Every task is three beats, three engine calls, ONE human decision point:

1. **DIRECTION** — draft the whole bundle top-to-bottom in TASK.md: §1 rules + ranked ⚠ flag (co-specify) ·
   §2 scenarios · §3 PLAN (grounding → frozen contract shape → build-strategy + Scope + Target) · §4 red suite
   (run it — red for the RIGHT reason) · §6 Build expectations. Then the ONE approval, presented
   lowest-confidence-first: `add.py freeze --by "<name>" --cross` (a setup session's baseline `lock`
   IS this approval).
2. **BUILD** — code in `src/` until every red is green; change no test, no frozen contract; stay
   inside the §3 Scope.
3. **VERIFY** — confirm evidence · 3 lenses (**security always HARD-STOP**) · earned-green
   refute-read · then `add.py gate PASS --target-hit yes|partial|no` (from build it compound-crosses; under `autonomy: auto` a
   run auto-PASSes on complete no-residue evidence — *auto-resolved*, an explicit PASS, never a
   skip; residue or lowered autonomy → human — `run.md`).

Stuck or deep? References, on demand — never a mandatory read: `phases/direction.md` ·
`phases/build.md` · `phases/verify.md`. Delegating? Spawn the roster agent for the beat; it loads
its own references (you read ONLY this file).

At each decision point (intake · bundle · gate · close) the fitting persona OWNS the gate report (banner then the ARC) —
`gate-udd.md` holds the principles: CONVEY decision + ARC (engine-sourced) · shape · flags (lowest-first) ·
evidence · a guided APPROVE; the persona owns the form, never the four floors (security stays HARD-STOP) — the question is a summary, never the artifact.
Read `gate-udd.md`/`run.md` at most once per session.

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
- UI/experience surface → UDD loop `design.md` (the fast lane is flag-mode above — no extra guide)
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

## Advancing — the 3-call walk

```bash
python3 .add/tooling/add.py new-task <slug> --title "..."   # born at direction
python3 .add/tooling/add.py freeze --by "<name>" --cross    # the ONE approval -> build
python3 .add/tooling/add.py gate PASS                       # verify recorded, task done
# add.py advance = step-wise alternative · add.py use <slug> = switch tasks
```

## Depth by stage

The steps never change; their depth does (stage from `add.py status`):

- **prototype** — light; throwaway code; design/experience is the point.
- **poc** — contract/tests/build deep on the single riskiest slice only.
- **mvp** — full flow, narrow scope, light observation.
- **production** — full rigor + the observe loop; reached via the `graduate.md` orchestration,
  never a bare `stage production` flip.

## The method rationale

The full method (the *why*) is the AIDD book in `.add/docs/`. Read it only when a
decision is genuinely unclear — never duplicate it here.
