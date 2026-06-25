---
name: add
description: >-
  ADD (AI-Driven Development) — a minimal, state-tracked workflow for building
  software where the AI writes the code and the human owns direction and
  verification. Drives every feature through one lean TASK.md: Specify →
  Scenarios → Contract → Tests → Build → Verify → Observe, with red/green TDD
  built in. Use this skill whenever working in a repo that has a `.add/`
  directory, when the user says "add", "start a task", "next phase", "specify
  this feature", "ADD method", or "AI-driven development", or when scaffolding a
  new feature and you want spec/tests-first discipline instead of vague-prompt
  coding. Also use it to resume work across sessions (it reads `.add/state.json`
  so you never re-read the whole repo).
user-invocable: true
when_to_use: "Invoke in any repo with a `.add/` directory, or when the user wants spec/tests-first feature work, resumes ADD work, or asks to start/advance a task."
category: workflows
keywords: [add, aidd, ai-driven-development, spec-first, tdd, contract, scenarios, verify, milestone, task-orchestration]
argument-hint: "status | init | continue | [describe new short goals or expectation]"
license: MIT
metadata:
  author: add
  version: "1.8.0"
---

# ADD — the orchestration engine

You are the orchestrator. ADD keeps the AI fast *and* safe by fixing direction
(spec, scenarios, contract, failing tests) **before** the build, and trusting the
result through passing evidence rather than a plausible-looking diff.

**One file = one task.** Each feature is one `.add/tasks/<slug>/TASK.md` — a §0 ground
preamble plus seven step sections, filled top to bottom. The Python tool tracks where you
are so context never rots across sessions.

## Always start here (orient — do not skip)

Engine: `.add/tooling/add.py` · book: `.add/docs/`. Ensure the engine is in the project first:

- It exists → go straight to `status` below.
- It does NOT (ADD installed as a Claude Code plugin — engine + book ride in the plugin) →
  materialize once: `node "${CLAUDE_PLUGIN_ROOT}/bin/cli.js" init --no-skill`. That drops
  `.add/tooling/` (engine) + `.add/docs/` (book) + the agent-agnostic `CLAUDE.md` block — like an
  npm/pip install; the skill stays in the plugin, nothing duplicated.

Find the resume point from the tool, not by re-reading the repo:

```bash
python3 .add/tooling/add.py status
```

`status` names two files to read when orienting: `.add/PROJECT.md` (the foundation) and `.add/SOUL.md`
(your **voice** — tone, style, what keeps the human's trust; read it each session — human-owned and
self-improving via the `soul-self-improve` path). Then branch on state:

- **No `.add/state.json` yet** (`status` says `no .add/ project found`) → **autonomous setup**: if
  `.add/.intent` exists, read it — the installer's one-line first-build intent (a NOTE, never an init
  trigger) — to seed your kickoff; then YOU run init — `add.py init --name "<inferred>" --stage <picked>
  --await-lock` — and read `phases/0-setup.md` to draft the foundation + §1–§3 through to the human
  baseline approval.
- **A task is active** → open its `.add/tasks/<active>/TASK.md`, read the `phase:` marker, load the
  matching `phases/<n>-<phase>.md`. Work *only* that phase.
- **No active task** → first SIZE the request (Intake below), then `add.py new-task <slug> --title "..."`.

**Quick ref** — `status` resume · `init` bootstrap · `advance` continue · `gate PASS` at verify.
**Flag mode** — two human-owned settings (never auto-picked): **fast** (task) · **auto** (mode).
- **fast** — `new-task --fast`: minimal template, freeze-gated; a milestone-free `--fast` task is a
  blessed standalone low-ceremony lane. Jot ideas first with `add.py todo "<text>"` (then `todo` to
  list · `todo --done <id>`).
- **auto** — `autonomy: auto` (default) auto-gates verify on evidence; lower the autonomy level with
  `add.py autonomy set conservative|manual` for a human gate · `new-milestone --await-confirm`
  confirm-gates a milestone's tasks.

## Intake — size a request before creating scope

Classify a raw request BEFORE any milestone or task: read `intake.md`, place it in one bucket —
`new-major` · `sub-milestone` · `task` · `change-request` — propose `{ bucket, rationale, command }`;
the human confirms. A question or unsharp intent? **Interview before you size** (`intake.md`). Once
`new-major`/`sub-milestone`, draft the `MILESTONE.md` (goal · scope · exit criteria · breadth-first
tasks) — read `scope.md`. Create it `new-milestone --await-confirm`, then `milestone-confirm <slug>`
gates `new-task` until the parent is agreed. For `task`/`change-request`: `add.py new-task` then the
first phase guide.

## The flow and which file to load

Load the phase guide **only for the phase you are in** (progressive disclosure):

| Phase | Guide | Produces (TASK.md section) | Who leads |
|-------|-------|----------------------------|-----------|
| setup | `phases/0-setup.md` | `.add/` + living docs + first §1–§3 + `SETUP-REVIEW.md` | AI drafts → **human locks** (the baseline approval) |
| ground | `phases/0-ground.md` | §0 GROUND map (real files · symbols · the anchors §3 cites) | **AI** (the §0 preamble — no new gate) |
| specify | `phases/1-specify.md` | §1 rules + ranked lowest-confidence flag | AI drafts (co-specify)† |
| scenarios | `phases/2-scenarios.md` | §2 Given/When/Then | AI drafts† |
| contract | `phases/3-contract.md` | §3 frozen shape | AI drafts → **human approves once** (the decision point)† |
| tests | `phases/4-tests.md` | §4 + red suite in `tests/` | AI drafts† |
| build | `phases/5-build.md` | code in `src/`, tests green | **AI** |
| verify | `phases/6-verify.md` | §6 checks + gate record | **AI auto-gates on evidence**; human on residue/security‡ |
| observe | `phases/7-observe.md` | §7 spec delta | human + AI |

† **The specification bundle (v7).** §1–§4 are one bundle; the human gives **one approval at the
contract freeze**, lowest-confidence-first — see `run.md`.
‡ **Verify auto-gate (v6–v7).** Under `autonomy: auto` (default) a run may auto-PASS on complete
evidence (*auto-resolved* — an explicit PASS, not a skip). **Security always escalates** (HARD-STOP);
so do concurrency / architecture residue and a lowered autonomy level (`conservative` / `manual`) — `run.md`.

At every human decision point (intake · bundle approval · gate · milestone close) follow
`report-template.md`: open with the ARC (goal · done · plan, engine-sourced), then SUMMARY → DECISION →
FLAGS → DECIDED → EVIDENCE → NEXT; show-before-ask; never pre-stamp; the question is a summary, never the artifact.

In **observe**, emit **lessons learned** tagged by which of the five (`DDD · SDD · UDD · TDD · ADD`)
they improve (write them `open`; the human consolidates into `PROJECT.md`) — grammar + lifecycle in
`deltas.md`. At milestone close (or on demand) the retrospective consolidation gathers confirmed deltas
into a versioned foundation — `fold.md`; then (separately, after) compact each foundation spec's stable
tail — `compact-foundation.md`. Observe also tunes your voice: propose a confirmable voice delta that,
once the human confirms, rewrites `SOUL.md` (the human is the only writer) — `soul.md`.

## Beyond the bundle — load on demand

- **§3 CONTRACT FROZEN** → build→verify is a dynamic, auto-gated run (`autonomy: auto` default; lower to
  `conservative`/`manual` for a human gate) — `run.md`. Pipeline several ready tasks behind their frozen
  contracts — `streams.md`. Delegate one piece of your plan to a subagent (when to spawn, the prompt
  template, the tier) — `advisor.md`. Self-score a draft (0–1 across six dimensions, refine if any < 0.9)
  — `confidence.md`. Both advisory: the engine never spawns; the self-score is never a gate.
- **Small, low-risk task**, less ceremony → the **fast lane**: `new-task --fast` scaffolds the minimal
  `TASK.fast.md`, bundle approved in one freeze — `phases/fast-lane.md`. Floor held (frozen contract ·
  red test · verify gate; `--fast` is freeze-gated under any milestone). Collapse, never skip; opt-in.
- **UI feature** at specify → the **design-definition loop** (UDD): review the domain → research and
  reuse components → wireframe → a real captured screen the human confirms **before** build — `design.md`.
  Tool-agnostic; the engine never renders.
- Tasks all done but the milestone **goal** unmet → `milestone-done` holds it open; the loop turns open
  deltas + extras into the next tasks (you propose, the human confirms) until the goal is met — `loop.md`.
- `status` prints **`MVP covered → propose graduation`** (every milestone done AND stage criteria all
  `[x]`) → `graduate.md`: `graduation-report` → co-specify interview → draft ≥1 production milestone →
  human confirm → then `stage production`. Guarded (`stage_no_roadmap`); the FINAL step, never a bare flip.
- `status` prints **`→ releasable: N milestone(s) closed since last release`** → `release.md` (the 5th
  scope level): `release-report` → draft notes from the consolidated deltas → meet the readiness floor
  (security HARD-STOP is un-forceable) → human confirms → `add.py release <version>` records the cut
  (CHANGELOG + `RELEASES.md` ledger + milestone attribution). The engine records; the human runs the
  tag / publish / deploy. A release bundles ≥1 milestone and is orthogonal to stage.
- **Monorepo / multi-repo** — a milestone spans more than one green bar (a BE + its FE, services across
  repos) → the **component pillar**: declare components in `.add/components.toml`, gate each task on its
  component's green-bar, freeze cross-component contracts (`produces:`/`consumes:`), hold the FE until the
  BE freezes, and `federate pull` a contract across repos — `components.md`. Opt-in; no components = today.

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

After a phase's exit gate is met, advance the state (this also syncs the TASK.md marker):

```bash
python3 .add/tooling/add.py advance            # next phase of the active task
python3 .add/tooling/add.py gate PASS          # at verify: records PASS, marks done
python3 .add/tooling/add.py use <slug>         # switch the active task (e.g. across parallel streams)
```

## Depth by stage

The steps never change; their depth does (read the stage from `add.py status`):

- **prototype** — run light; code is throwaway; design/experience is the point.
- **poc** — run contract/tests/build deeply on the single riskiest slice only.
- **mvp** — full flow, narrow scope, light observation.
- **production** — every step at full rigor + the observe loop. Reach it via the `graduate.md`
  orchestration when status shows `MVP covered → propose graduation`, never a bare `stage production` flip.

## The method rationale

The full method (the *why* behind every rule) is the AIDD book in `.add/docs/`. When a phase decision is
genuinely unclear, read the linked chapter — each phase guide points to its chapter. Do not duplicate
the book here; load it on demand.
