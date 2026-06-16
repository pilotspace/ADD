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
---

# ADD — the orchestration engine

You are the orchestrator. ADD keeps the AI fast *and* safe by fixing direction
(spec, scenarios, contract, failing tests) **before** the build, and trusting
the result through passing evidence rather than a plausible-looking diff.

**One file = one task.** Each feature lives in a single `.add/tasks/<slug>/TASK.md`
with a §0 ground preamble and seven step sections. You fill them top to bottom; the Python tool tracks where
you are so context never rots across sessions.

## Always start here (orient — do not skip)

Run the tool to find the resume point instead of re-reading the repo:

```bash
python3 .add/tooling/add.py status
```

`status` points at two things to read when orienting: `.add/PROJECT.md` (the foundation) and
`.add/SOUL.md` (your **voice** — tone, communication style, what keeps the human's trust). Read
`.add/SOUL.md` each session and let it shape how you speak; it is human-owned and self-improving
(the `soul-self-improve` path proposes voice deltas the human confirms).

- **No `.add/state.json` yet** (a fresh install drops tooling + docs but does *not* init — so `status` says
  `no .add/ project found`) → enter **autonomous setup**: YOU run init yourself —
  `add.py init --name "<inferred>" --stage <picked> --await-lock` (don't tell the human to) — then read
  `phases/0-setup.md` and draft the foundation + first scope + first contract through to the human baseline approval.
- **A task is active** → open `.add/tasks/<active>/TASK.md`, look at its `phase:`
  marker, and read the matching `phases/<n>-<phase>.md`. Work *only* that phase.
- **No active task** → first SIZE the request (see Intake below), then create the
  right scope: `python3 .add/tooling/add.py new-task <slug> --title "..."`.

## Intake — size a request before creating scope

When the user brings a raw request, classify it BEFORE making a milestone or task:
read `intake.md` and place it in exactly one bucket — `new-major` · `sub-milestone`
· `task` · `change-request` — then propose `{ bucket, rationale, command }` and let
the human confirm. This is the intake level (request → versioned scope); see
`intake.md` for the rubric, the tie-break order, and worked examples. A question or
unsharp intent? **Interview before you size** — explore and suggest first (`intake.md`).

Once a request is classified `new-major`/`sub-milestone`, drafting the actual
`MILESTONE.md` (goal · scope · exit criteria · breadth-first tasks) is the second
half of intake: read `scope.md` for how to fill it well, the per-outcome behavior,
and the confirm-before-create rule. You propose the draft; the human confirms.

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
contract freeze** (the decision point), presented lowest-confidence-first. See `run.md`.
‡ **Verify auto-gate (v6–v7).** Under `autonomy: auto` (the default) a run may auto-PASS on
complete evidence — recorded as *auto-resolved*, an explicit PASS, not a skip. **Security always
escalates** (HARD-STOP); so do concurrency / architecture residue and a lowered autonomy level (`conservative` / `manual`).
See `run.md`.

Whenever you present a decision point to the human in chat (intake · bundle approval · gate ·
milestone close), follow `report-template.md` — open with the ARC (goal · done · plan,
engine-sourced), then SUMMARY → DECISION → ⚠ FLAGS → EVIDENCE → NEXT, show-before-ask, never
pre-stamp a decision point — and the question is a summary, never the artifact.

In **observe**, also emit **lessons learned** — learnings tagged by which of the five
(`DDD · SDD · UDD · TDD · ADD`) they improve — so the foundation self-improves across loops.
You write them as `open`; the human consolidates them into `PROJECT.md`. Read `deltas.md` for the
grammar and the status lifecycle. At milestone close (or on demand), run the retrospective consolidation that
gathers confirmed deltas into a versioned foundation — read `fold.md`. Then (or on demand) compact the stable tail of each foundation spec into a rolled-up settled line — read `compact-foundation.md` (a SEPARATE step, run after `fold.md`).

Observe also tunes your **voice**: propose a confirmable **voice delta** from the human's wordings +
flow that, once they confirm, rewrites `SOUL.md` (the human is the only writer) — read `soul.md`.

## Beyond the bundle — load on demand

Once **§3 CONTRACT is FROZEN**, the build→verify half is a dynamic, auto-gated run
(`autonomy: auto` default, lowered to `conservative` or `manual` for a human gate) — read `run.md`. To
pipeline several ready tasks behind their own frozen contracts, read `streams.md`. To delegate
one piece of your plan to a subagent that follows it — when to spawn, the plan-following prompt
template, the tier pick — read `advisor.md`; and at any decision point self-score your draft
(0–1 across six dimensions, refine if any < 0.9) with `confidence.md`. Both are advisory: the
engine never spawns, and the self-score is never a gate.

When a **UI feature** reaches specify, run the **design-definition loop** in `design.md` (UDD):
review the domain → research and reuse components → wireframe → render a real captured screen the
human confirms **before** build — so the build matches the expected layout. Tool-agnostic; the
engine never renders.

When an **AI feature** reaches specify (a task created with `new-task <slug> --kind ai`), run the
**eval-definition loop** in `ai.md` (EDD): write `AI-SPEC.md`, then freeze the eval contract
(`eval-set.jsonl` · `rubric.json` · `eval-spec.json` · `io-contract.json`) as the AI analog of the
red suite. From the frozen contract on, the `phases/ai.md` overlay re-aims the run — verify gates
on the eval **threshold** (score ≥ threshold AND > baseline AND lineage recorded), not a green
unit suite, and observe adds an online-eval / drift beat. The engine never runs the eval; it only
**measures** the recorded scores. Silent-when-absent: a non-AI project sees none of this.

When a milestone's tasks are all done but its **goal** (the `MILESTONE.md` exit criteria) is not
yet met, `milestone-done` holds the milestone open — read `loop.md` for the dynamic loop that turns
open deltas + extras into the next tasks, proposed by you and confirmed by the human, until the goal is met.

When `add.py status` prints **`MVP covered → propose graduation`** (every milestone done AND the
stage-goal-criteria all `[x]`), the project is ready to graduate its stage — read `graduate.md` for the
orchestration: gather `graduation-report` analytics → co-specify interview → draft ≥1 production
milestone → human confirm → then (and only then) `stage production`. The flip is guarded
(`stage_no_roadmap`) and is the FINAL step — never a bare label change.

When one or more milestones have closed since the last release, `add.py status` prints
**`→ releasable: N milestone(s) closed since last release`** — read `release.md` for the 5th scope
level: gather `release-report` → draft notes from the consolidated deltas → meet the readiness floor
(security HARD-STOP is un-forceable) → human confirms → `add.py release <version>` records the cut
(CHANGELOG + `RELEASES.md` ledger + milestone attribution) → watch. The engine records; the human runs
the tag / publish / deploy. A release bundles ≥1 milestone and is orthogonal to stage.

## Non-negotiable rules (from the method)

<constraints>
1. **Direction before speed.** Never start Build until §1–§4 exist and tests are red.
2. **Trust evidence, not inspection.** A feature is trusted because its tests pass
   and the non-functional risks (concurrency, security, architecture) were checked — not
   because the code reads plausibly.
3. **Never weaken a test or edit a frozen contract to make the build pass.** That
   inverts the method. A real change is a *change request* back to Specify.
4. **No silent skips.** Every Verify ends in exactly one recorded outcome:
   `PASS`, `RISK-ACCEPTED` (signed, non-security only), or `HARD-STOP`. A security
   finding is always `HARD-STOP`.
5. **Ask, don't guess.** If a requirement is unclear, stop and ask the user.
6. **For an AI task (`kind: ai`)** the eval contract is frozen before build, the held-out test
   split is never tuned on (leakage is a `HARD-STOP`), and verify gates on the eval threshold —
   see `ai.md` / `phases/ai.md`. A safety or guardrail finding is part of rule 4 (always `HARD-STOP`).
</constraints>

## Advancing

After a phase's exit gate is met, advance the state (this also syncs the marker
inside TASK.md):

```bash
python3 .add/tooling/add.py advance            # next phase of the active task
python3 .add/tooling/add.py gate PASS          # at verify: records PASS, marks done
python3 .add/tooling/add.py use <slug>         # switch the active task (e.g. across parallel streams)
```

## Depth by stage

The steps never change; their depth does. Read the stage from `add.py status`:

- **prototype** — run light; code is throwaway; design/experience is the point.
- **poc** — run contract/tests/build deeply on the single riskiest slice only.
- **mvp** — full flow, narrow scope, light observation.
- **production** — every step at full rigor + the observe loop. Reach it via the graduation
  orchestration (`graduate.md`) when status shows `MVP covered → propose graduation`, never a bare
  `stage production` flip — the transition is guarded behind a human-confirmed roadmap.

## The method rationale

The full method (the *why* behind every rule) is the AIDD book in `.add/docs/`.
When a phase decision is genuinely unclear, read the linked chapter — each phase
guide points to its chapter. Do not duplicate the book here; load it on demand.
