# MILESTONE: Stage Graduation — the 4th scope altitude (mvp → production)

goal: When the MVP is covered, ADD proposes the move to production as an analytics-driven, interview-led roadmap of milestones the human confirms before the stage ever advances.
rationale: intake = new-major — the stage-graduation orchestration is a new pillar no active milestone's goal covers: the absent 4th scope altitude (setup · intake · milestone-loop already exist; the stage transition is a bare `add.py stage` label flip with no analytics, interview, or proposal). Confirmed 2026-06-08.
stage: mvp · status: active · created: 2026-06-08

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  an additive checkable stage-goal-criteria block in PROJECT.md (the human's "this stage
     is genuinely covered" affirmation) + an `add.py status` graduation CUE that fires when
     all milestones are `done` AND those boxes are all `[x]`; a read-only graduation-analytics
     harvest (`add.py graduation-report --json` for GATHERING) that clusters the MVP loop's
     evidence (open deltas · open RISK-ACCEPTED waivers · RETROs · verify residue · observe-loop
     coverage gaps); a new `graduate.md` skill guide that drives cue → analytics → co-specify
     interview → N production MILESTONE drafts → human confirm → then (and only then)
     `stage production`; SKILL routing to it; aligned book ch.10 + GLOSSARY.
Out: the production milestones THEMSELVES (the hardening work — SLOs, rollback tests, incident
     runbooks) — v22 ships the orchestration that PROPOSES them, not the work it proposes;
     no engine JUDGEMENT of readiness (engine counts tallies + lists records; the human decides
     and the interview synthesizes); no auto-flip (the stage never advances without a confirmed
     roadmap); no new build→verify autonomy behavior; the prototype→poc and poc→mvp transitions
     reuse the same guide but mvp→production is the v22 proof case, not those.

## Shared decisions & glossary deltas   (living — every task must honor these)
- `stage-graduation` — the stage-altitude orchestration that proposes advancing a project's
  stage as several milestones, AI-proposed from analytics, human-confirmed. The 4th scope
  altitude after setup (`phases/0-setup.md`), intake (`intake.md`/`scope.md`), and the milestone
  loop (`loop.md`). The bare `add.py stage` flip becomes its FINAL step, never a standalone act.
- `graduation analytics` — the read-only harvest that clusters accumulated MVP-loop evidence
  (open deltas by competency · open RISK-ACCEPTED waivers by expiry · RETRO themes · verify
  residue · observe-loop coverage gaps) into a production-readiness picture. GATHERING is
  mechanical (a read-only command, the v9 `report`/`--json` precedent); the SYNTHESIS ("what
  production means here") is the interview's judgment, never the engine's.
- `stage-goal-criteria` — additive checkable boxes in PROJECT.md capturing the human's
  stage-covered affirmation. Mirrors the milestone goal-gate at stage altitude: the engine reads
  the tally (never judges); the cue fires ONLY when the block exists and is all `[x]` (no block →
  no cue → zero behavior change, exactly like the milestone goal-gate fires only when criteria exist).
- The flip is the LAST step. `add.py stage production` is never called outside `graduate.md`'s
  confirmed-roadmap path; a bare flip with no roadmap is the symptom this milestone removes.

## Shared / risky contracts (freeze these first)
- `add.py status` graduation-cue output seam — ADDITIVE only (existing status text + exit codes
  byte-unchanged; the cue is a new line that appears solely when both tallies complete)
  -> owning task `stage-goal-criteria`   [the guide depends on this]
- stage-goal-criteria block shape in PROJECT.md (how the boxes are written + parsed)
  -> owning task `stage-goal-criteria`
- `graduation-report` output shape (evidence sources + clustering; `--json` facts seam)
  -> owning task `graduation-analytics`
- `add.py stage production` guard — the flip REFUSES when 0 milestones have `stage: production`
  (error `stage_no_roadmap`; `--force` escape; scoped to →production ONLY — every other flip
  byte-unchanged). ADDED as a v22 task-3 decomposition deviation: `cmd_stage` is a shared engine
  surface beyond the three contracts above; the human chose engine-enforcement (B, 2026-06-09) so
  "the stage NEVER reaches production without a roadmap" (exit criterion 4) is real + red/green
  testable, mirroring the milestone goal-gate (`milestone_goal_unmet`). GATHER-not-judge holds: the
  guard checks a tally (≥1 production milestone exists), it never judges readiness.
  -> owning task `graduate-guide`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] stage-goal-criteria   depends-on: none                                       — additive PROJECT.md stage-goal-criteria block + `add.py status` graduation cue (engine reads two existing tallies — all milestones done + boxes all `[x]` — and emits a cue; never decides) (freeze-first)
- [x] graduation-analytics  depends-on: none                                       — read-only `add.py graduation-report` (+ `--json`) clustering open deltas + open waivers + RETROs + verify residue + observe-loop coverage gaps into a production-readiness report (gather, not judge)
- [x] graduate-guide        depends-on: stage-goal-criteria,graduation-analytics   — new `graduate.md`: cue → analytics → co-specify interview → N production MILESTONE drafts via existing `new-milestone`+goal-gate → confirm → then `stage production`; + SKILL routing to it on the cue; + a mechanical `stage production` guard (refuse without ≥1 production milestone, `--force` escape) so the flip is enforced as the final step (B, engine-enforced)
- [x] stage-book-align      depends-on: graduate-guide                             — align docs/10 (stages) + GLOSSARY so the stage-graduation scope level reads consistently with the three existing scope levels (slug `stage-book-align`: declared `book-align` collided with the done v12 task)

## Exit criteria (observable; map each to the task that delivers it)
- [x] With all milestones `done` AND the stage-goal-criteria all `[x]`, `add.py status` emits a
      `MVP covered → propose graduation` cue; before that it stays silent — existing status output
      + exit codes byte-unchanged   (← stage-goal-criteria)
- [x] A project with no stage-goal-criteria block behaves exactly as today (no cue) — grandfathered,
      zero behavior change   (← stage-goal-criteria)
- [x] `add.py graduation-report` produces a clustered production-readiness report from existing
      records, naming each evidence source (deltas · waivers+expiry · RETROs · residue · coverage
      gaps); read-only, judges nothing; `--json` is the stable facts seam   (← graduation-analytics)
- [x] `graduate.md` drives the full orchestration end-to-end and the stage NEVER reaches
      `production` without a human-confirmed roadmap of ≥1 production milestone; the flip is the
      orchestration's final recorded step   (← graduate-guide)
- [x] SKILL routes to `graduate.md` on the cue; the "Depth by stage" lines point at the
      orchestration, not just a depth hint   (← graduate-guide)
- [x] docs/10 + GLOSSARY describe stage-graduation, graduation analytics, and stage-goal-criteria
      consistently with setup/intake/loop   (← stage-book-align)
