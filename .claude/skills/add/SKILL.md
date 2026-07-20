---
name: add
description: >-
  ADD (AI-Driven Development) — a minimal, state-tracked workflow: the AI writes
  the code, the human owns direction and verification. Drives every feature through
  one lean PLAN.md: Specify → Scenarios → Plan → Tests → Build → Verify → Observe,
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
  version: "2.0.0"
---

# ADD — memory · judgment · conscience (the agent is the hands)

You are the orchestrator. ADD keeps the AI fast *and* safe by fixing direction
(spec, scenarios, contract, failing tests) **before** the build, and trusting the
result through passing evidence, not a plausible-looking diff.

**One plan = one task.** Each feature is one `.add/tasks/<slug>/PLAN.md` — the engine-known
spine; its §3 PLAN (grounding · contract · scope · measurable Target) is the core artifact.
Shard free context files beside it in the task folder — the AI owns that architecture.

**The `--todo` fast-path.** When the skill ARGUMENTS begin with `--todo`, skip orienting: route to
`add.py todo` and print its output — `--todo <text>` captures · `--todo` lists open todos ·
`--todo --done <id>` closes — then STOP.

## Always start here (orient — do not skip)

Engine: `.add/tooling/add.py`. Ensure it is in the project:

- It exists → go to `status` below.
- It does NOT (a plugin install) → materialize once:
  `node "${CLAUDE_PLUGIN_ROOT}/bin/cli.js" init --no-skill` — drops `.add/tooling/` (engine)
  + the agent-agnostic `CLAUDE.md` block; the skill stays in the plugin.

Resume from the tool, never re-read the repo — mid-flow, trust each verb's
`next:` footer:

```bash
python3 .add/tooling/add.py status --brief
```

Then read the foundation map `add.py status --foundation` (`--all` full) + `.add/SOUL.md` (**voice**). Then branch on state:

- **No `.add/state.json` yet** (`status` says `no .add/ project found`) → **autonomous setup**: read
  `.add/.intent` if present (the installer's first-build intent — a NOTE, never an init trigger), then
  YOU run `add.py init --name "<inferred>" --stage <picked> --await-lock` and drive the setup span of
  `phases/direction.md` — foundation + first bundle to the human baseline `lock`.
- **A task is active** → open its `.add/tasks/<active>/PLAN.md`, read the `phase:` marker, work that
  beat per the loop below.
- **No active task** → first SIZE the request (Intake below), then `add.py new-task <slug> --title "..."`.

**Quick ref** — `status --brief` resume · `advance --fill <draft>` write+continue · `status --section <n>` one §body · `gate PASS` at verify.
**Flag mode** — ONE atomic template serves every task (no lanes); flags are header declarations.
- **gate_mode** — headless/agent-crossed freeze: declare `gate_mode: ai-plan-verify` in the PLAN.md
  header + fill the §3 AI-verify record; security|data|architecture stay human-frozen (unstrikeable).
- **auto** — `autonomy: auto` (default) auto-gates verify on evidence; `add.py autonomy set
  conservative|manual` restores a human gate · `new-milestone --await-confirm` confirm-gates
  a milestone's tasks.

## Intake — size a request before creating scope

Classify a raw request BEFORE any scope: read `intake.md`. Too small for scope → the
**inline lane** (diff + `delta-append` receipt; security·data·architecture escalates). Else
one bucket — `new-major` ·
`sub-milestone` · `task` · `change-request` — propose `{ bucket, rationale, command }`; the human
confirms. Unsharp intent? **Interview before you size** (`intake.md`). For a milestone bucket draft
`MILESTONE.md` (goal · scope · exit criteria · breadth-first tasks — `phases/direction.md`), then
`new-milestone --await-confirm` + `milestone-confirm <slug>` (gates `new-task` until agreed). For
`task`/`change-request`: `add.py new-task`, then beat 1 above.

## The 3-beat loop (inline — this file IS the loop; references load on demand)

Every task is three beats, three engine calls, ONE human decision point:

1. **DIRECTION** — ground §3 in the `neighborhood` card new-task/status print (inherited interfaces — not code re-reads), then draft the whole bundle top-to-bottom in PLAN.md: §1 rules + ranked ⚠ flag (co-specify) ·
   §2 scenarios · §3 PLAN (grounding → frozen contract shape → build-strategy + Scope + Target) · §4 red suite
   (run it — red for the RIGHT reason). Then the ONE approval, presented
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
Read each at most once per session.

Emit **lessons learned** tagged by which of the five (`DDD · SDD · UDD · TDD · ADD`)
they improve — **in-flight**: `add.py delta-append <dd> "<lesson>"` → its living spec in
`.add/specs/` (grammar: `deltas.md`).
The living specs ARE the foundation — the close just counts what §7 still holds open. Observe also
tunes your voice: a confirmable delta the human confirms rewrites `SOUL.md` (the human is the only
writer) — `deltas.md`.

## Beyond the bundle — load on demand

One trigger = one guide — full prose: `beyond.md`; load only when a trigger fires:

- §3 FROZEN → auto-gated run `run.md` · subagent roster + pipelines (agent-call-preferred,
  the default execution mode) → `phases/verify.md` · self-score → `phases/direction.md`
- UI/experience surface → UDD loop `design.md`
- milestone goal unmet at `milestone-done` → `loop.md`
- graduation · release · monorepo green-bars → persona-owned playbooks, `beyond.md` ·
  the persona loop (`.add/personas/`) → `docs/18-personas.md` · `sensitivity:` + `advisor-gate-relax` → `phases/verify.md`

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
- **production** — full rigor + the observe loop; reached via the graduation playbook
  (`beyond.md`), never a bare `stage production` flip.

## The method rationale

The full method (the *why*) is the AIDD book — https://pilotspace.github.io/ADD/
(the `docs/…` chapters the guides cite). Read it only when a
decision is genuinely unclear — never duplicate it here.
