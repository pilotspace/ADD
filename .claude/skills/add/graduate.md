# Stage graduation — propose the move to production as a roadmap, never a flip

A project graduates when the MVP is genuinely covered AND a human-confirmed roadmap of production work exists. This is the **4th scope level** — after setup, intake/scope, and the milestone loop. It turns the bare `add.py stage` flip into the **final step** of an analytics-driven, interview-led orchestration.

You **gather and propose**; the **human confirms and judges**; the engine only counts tallies and enforces the floor. The engine never decides "ready" — that is judgment, and it belongs to the interview.

## The cue

When every milestone is `done` AND the human's stage-goal-criteria in `PROJECT.md` are all `[x]`, `add.py status` prints:

```
  → MVP covered → propose graduation
```

Before both tallies complete, status is silent. A project with no stage-goal-criteria block is grandfathered — zero change.

## The flow

1. **Gather** — run `add.py graduation-report` (`--json` to branch on it). Clusters the MVP loop's evidence: open deltas by competency · open RISK-ACCEPTED waivers · RETRO records · verify residue · observe-loop coverage gaps. Gathers, never judges.
2. **Co-specify interview** — synthesize *"what production means HERE"* WITH the human, using the gathered records as the agenda. Interview to real confidence — do not guess what "production-ready" means for this project.
3. **Draft the roadmap** — for each production outcome the interview surfaces, draft a production milestone: `add.py new-milestone <slug> --stage production --goal "…"`, then write its exit criteria. The roadmap is **≥1** milestone containing the hardening work (SLOs, rollback tests, incident runbooks).
4. **Human confirms** — present the roadmap via `report-template.md`, opening with the ARC (goal · done · plan). Render as a guided choice (per `report-template.md`). Nothing advances on an unconfirmed draft.
5. **Flip — the final step** — only now run `add.py stage production`. Because ≥1 production milestone now exists, the guard passes and the transition is recorded.

## The floor

`add.py stage production` is **guarded**: refuses with `stage_no_roadmap` when zero milestones have `stage: production`. The check is a tally, never a readiness judgment. `--force` overrides for grandfathered/edge cases.

Guard is on the `→production` transition only. Flips to prototype/poc/mvp are unchanged. `add.py init --stage production` is an explicit at-creation declaration — out of scope of the guard.

## Invariants

- **The flip is the final step**, never called outside this confirmed-roadmap path.
- **No auto-flip.** Every step is human-confirmed; the engine gathers, counts, and enforces the floor — it does not advance the stage on its own.
- **The flow is continuous, not cue-reentrant.** Once you draft the first production milestone, `status` stops printing the cue. Do NOT re-await the cue; carry straight through to confirm and flip.

## Depth and reuse

The same orchestration serves prototype→poc and poc→mvp; **mvp→production** is the rigorous proof case. At lower stages, run it light — same shape, less depth.
