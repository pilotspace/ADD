---
name: add
description: >-
  ADD (AI-Driven Development) — a minimal, state-tracked workflow: the AI writes
  the code, the human owns direction and verification. Drives every feature through
  one lean PLAN.md: Specify → Plan → Tests & Scenarios → Build → Verify → Observe,
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
  version: "2.5.0"
---

# ADD — memory · judgment · conscience (the agent is the hands)

You turn intent into the right task, then drive it. ADD keeps the AI fast *and* safe by fixing direction
(spec, scenarios, contract, failing tests) **before** the build, and trusting the
result through passing evidence, not a plausible diff.

**One task = one atomic node.** Each feature is one `.add/tasks/<slug>/PLAN.md`; its frozen §3
(contract · scope · Target) is the interface neighbor nodes depend on — edges compile from the
milestone, `graph` renders the DAG, `locate` walks a failure to its node. Shard context beside it.

**The `--todo` fast-path.** ARGUMENTS begin with `--todo`? Skip orienting: run `add.py todo`, print
it — `--todo <text>` captures · `--todo` lists · `--todo --done <id>` closes — then STOP.

## Always start here (orient — do not skip)

Engine: `.add/tooling/add.py`. Missing (a plugin install)? Materialize it once —
`node "${CLAUDE_PLUGIN_ROOT}/bin/cli.js" init --no-skill` drops `.add/tooling/` + the agent-agnostic
`CLAUDE.md` block; the skill stays in the plugin.

Resume from the tool, never re-read the repo — run `add.py status --brief` (cookbook), then
the foundation map `status --foundation` (`--all` full) + `.add/SOUL.md` (**voice**); mid-flow, trust
each verb's `next:` footer. Then branch on state:

- **No `.add/state.json` yet** (`status` says `no .add/ project found`) → **autonomous setup**: read
  `.add/.intent` if present (the installer's first-build intent — a NOTE, never an init trigger), then
  YOU run `add.py init --name "<inferred>" --stage <picked> --await-lock` and drive setup via
  `phases/direction.md` (brownfield repo → map it silently, `adopt.md`) — to the human baseline `lock`.
- **A task is active** → open its `.add/tasks/<active>/PLAN.md`, read the `phase:` marker, work that
  beat per the loop below.
- **No active task** → first SIZE the request (Intake below), then `add.py new-task`.

**Flag mode** — ONE atomic template serves every task (no lanes); flags are header declarations.
- **gate_mode** — headless/agent-crossed freeze: declare `gate_mode: ai-plan-verify` in the PLAN.md
  header + fill the §3 AI-verify record; security|data|architecture stay human-frozen (unstrikeable).
- **auto** — `autonomy: auto` (default) auto-gates verify on evidence; `add.py autonomy set
  conservative|manual` restores a human gate.

## Intake — size a request before creating scope

Classify a raw request BEFORE any scope: read `intake.md`. Too small for scope → the **inline lane**
(diff + `delta-append` receipt; security·data·architecture escalates). Else one bucket — `new-major` ·
`sub-milestone` · `task` · `change-request` — propose `{ bucket, rationale, command }`; the human
confirms. Unsharp intent? **Interview before you size** (`intake.md`). A milestone bucket: draft
`MILESTONE.md` (goal · scope · exit criteria · breadth-first tasks — `phases/direction.md`), then the
`new-milestone`/`milestone-confirm` pair below (new-task inherits each node's depends-on). A
`task`/`change-request`: `add.py new-task`, then beat 1 above.

## The 3-beat loop (this file IS the loop; references load on demand)

Every task is three beats (seven steps, folded), three engine calls, ONE human decision:

1. **DIRECTION** — load the domain-fit persona from the `status --all` roster (`slug[flow] — vibe`;
   `check` prints the same as one line) — frontmatter, not bodies. **select → fold → author** (a roster of near-duplicates is worse than one
   sharp lens): a sibling's `use-when` fits → use it · almost fits → fold in (bump `folded:`) · no
   lens owns it, or none seeded → author it (add-worker persona-mode + the `persona-author` skill).
   NEVER blocks — no fit → the generic fallback, a 15-year specialist in the task's kind, which never
   lowers a gate. Then compose
   the whole bundle in ONE silent draft — §1·§3 + §5-scope, no per-section narration; §4 then runs red — in PLAN.md: §1 rules + ranked ⚠ flag (co-specify) ·
   §3 PLAN (grounding → frozen contract shape → build-strategy + Scope + Target) ·
   §4 TESTS & SCENARIOS — the red suite (cases live here; optional inline gherkin when a human needs it): one test per Must & per Reject (a Must/Reject encoded in no §4 test = §1 not understood — stop); minor behaviors are prose build-guidance, not gated; run red for the RIGHT reason; fill each `covers:` key. Then the ONE approval,
   presented lowest-confidence-first: `add.py freeze` (a setup session's baseline `lock` IS this approval).
2. **BUILD** — code in `src/` until every red is green; change no test, no frozen contract; stay
   inside the §3 Scope. A test OUTSIDE your suite failing? `add.py locate` names the owning node, the
   failure class, the frozen §3 clause it proves, and who re-verifies if a settled contract must move.
3. **VERIFY** — confirm evidence · 3 lenses (**security always HARD-STOP**) · earned-green
   refute-read · then `add.py gate PASS` (from build it compound-crosses; under `autonomy: auto` a
   run auto-PASSes on complete no-residue evidence — *auto-resolved*, an explicit PASS, never a skip; residue or
   lowered autonomy → human — `run.md`).

Stuck or deep? On demand: `phases/direction.md` · `phases/build.md` · `phases/verify.md` · opaque
term? `terms.md`. Delegating? Spawn the roster agent — it loads its own refs (you read ONLY this file).

At each decision point (intake · bundle · gate · close) the fitting persona OWNS the gate report —
`gate-udd.md` (read once per session) holds the principles: CONVEY decision + ARC (engine-sourced) ·
shape · flags (lowest-first) · evidence · a guided APPROVE. The persona owns the form, never the four
floors (security stays HARD-STOP) — the question is a summary, never the artifact.

Emit **lessons learned** tagged by which of the five (`DDD · SDD · UDD · TDD · ADD`) they improve —
in-flight, via `delta-append` → its living spec in `.add/specs/`. The living specs
ARE the foundation; the close counts what §7 still holds open. Observe also tunes your voice: a
confirmable delta the human confirms rewrites `SOUL.md` (the human is the only writer) — `deltas.md`.

## Beyond the bundle — one trigger = one guide (full prose: `beyond.md`); load only on a trigger

- §3 FROZEN → auto-gated run `run.md` · subagent roster + pipelines (agent-call-preferred, the
  default execution mode) → `phases/verify.md` · self-score → `phases/direction.md`
- UI/experience surface → UDD loop `design.md` · milestone goal unmet at `milestone-done` → `loop.md`
- multi-task / high-uncertainty milestone → persona-framed strategy loop `strategy.md` (fills the `## Strategy` slot; micro/`--tiny` → skip)
- graduation · release · monorepo green-bars → persona-owned playbooks, `beyond.md` ·
  the persona loop (`.add/personas/`) → `docs/18-personas.md` · `sensitivity:`/`advisor-gate-relax` → `phases/verify.md`

## Non-negotiable rules (from the method)

<constraints>
1. **Direction before speed.** Never start Build until §1–§4 exist and tests are red.
2. **Trust evidence, not inspection.** A feature is trusted because its tests pass and the
   non-functional risks (concurrency, security, architecture) were checked — not because the code
   reads plausibly.
3. **Never weaken a test or edit a frozen contract to make the build pass.** That inverts the
   method. A real change is a *change request* back to Specify.
4. **No silent skips.** Every Verify ends in exactly one recorded outcome: `PASS`, `RISK-ACCEPTED`
   (signed, non-security only), or `HARD-STOP`. A security finding is always `HARD-STOP`.
</constraints>

## Command cookbook — copy a line; `-h` only off-menu

`add.py` = `python3 .add/tooling/add.py`; lines 2–4 = the 3 calls — default is ONE composed draft then bare `advance`/`freeze`; `advance --fill <draft>` = step-wise, only for a large/uncertain task.

```bash
add.py status --brief        # resume · status --section <n|phase> = §body · --foundation · --json
add.py new-task <slug> --title "..."  # --milestone m · --depends-on a,b · --sensitivity security
add.py freeze --by "<name>" --cross   # the ONE approval -> build (--ai-plan-verify = headless)
add.py gate PASS --target-hit yes     # partial|no · RISK-ACCEPTED --owner --ticket --expires
add.py locate tests/x.py::test_y      # failure -> owning node + its frozen §3 clause
add.py graph --milestone <slug>       # mermaid DAG · relate <slug> --depends-on|--extends
add.py delta-append tdd "<lesson>"    # lens: ddd|sdd|udd|tdd|add
add.py new-milestone <slug> --title "..." --goal "..." --await-confirm  # confirm-gates its tasks
add.py milestone-confirm <slug> --by "<name>"   # compiles Tasks -> DAG; unlocks new-task
add.py report [<milestone>|<task>] --decide  # rollup/drill-in · check · search · use
```

## Depth by stage

Steps never change; depth does (`add.py status`):

- **prototype** — light; throwaway code; design/experience is the point.
- **poc** — contract/tests/build deep on the single riskiest slice only.
- **mvp** — full flow, narrow scope, light observation.
- **production** — full rigor + the observe loop; reached via the graduation playbook
  (`beyond.md`), never a bare `stage production` flip.

The **method rationale** (the *why*) lives in the AIDD book — https://pilotspace.github.io/ADD/ (the `docs/…` chapters the
guides cite). Read it when a decision is genuinely unclear; never duplicate it here.

