# MILESTONE: Flag-first freeze + autonomy dial

goal: close the freeze-and-autonomy seam: the lowest-confidence flag is mechanically required at every freeze, and the autonomy level is an explicit 3-mode dial (manual/conservative/auto) the human sets
rationale: sub-milestone of the live autonomy theme — close the freeze/autonomy seam with MECHANICAL (not prose-only) guards: the human sets the throttle AND the freeze flag is real. (MILESTONE body back-filled at close — it was a stub during the task-driven build.)
stage: mvp · status: active · created: 2026-06-10

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  two fail-closed guards on the freeze/autonomy seam — (1) the lowest-confidence flag is mechanically
     required at every freeze; (2) the per-task autonomy header is an explicit ordered 3-mode level
     (manual < conservative < auto), prose ≡ enforcement across GLOSSARY + book + skill.
Out: a PROJECT-level autonomy default at init (→ goal-auto-ready); removing/relaxing the freeze gate itself;
     CI enforcement that a human actually engaged the flag (prose ≠ enforcement, deferred).

## Shared decisions & glossary deltas   (living — every task must honor these)
- autonomy level — the per-scope throttle, an ordered ladder `manual < conservative < auto`, declared in the
  TASK.md header and reviewed at the freeze (GLOSSARY); the high-risk guard refuses an UN-lowered `auto`.
- the lowest-confidence flag is a FROZEN-shape requirement, mechanically enforced, not prose-only.

## Shared / risky contracts (freeze these first)
- the autonomy-token grammar + high-risk guard      -> owning task explicit-autonomy-dial
- the unflagged-freeze guard (advance refuse + audit verified-marker) -> owning task unflagged-freeze

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] unflagged-freeze        depends-on: none  — mechanically require the lowest-confidence flag at every freeze (fail-closed)
- [x] explicit-autonomy-dial  depends-on: none  — explicit 3-mode autonomy level + widened high-risk guard + status surface + check lint

## Exit criteria (observable; map each to the task that delivers it)
- [x] `add.py advance` REFUSES to leave the contract phase without a lowest-confidence flag, and `audit` flags an unflagged frozen record   (← unflagged-freeze)
- [x] the engine recognizes `autonomy: manual|conservative|auto`; `risk: high` without a lowered rung is refused at gate + audit (`unguarded_high_risk_auto`); `status` surfaces the active level; `check` reds an unknown level   (← explicit-autonomy-dial)
- [x] GLOSSARY + book (appendix-c · 10-setup · 11-governance) + skill (run.md · streams.md · SKILL.md) describe the 3-mode level, prose ≡ enforcement, synced ×3   (← explicit-autonomy-dial)
