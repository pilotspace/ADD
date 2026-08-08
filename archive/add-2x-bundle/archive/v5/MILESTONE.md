# MILESTONE: The Self-Improving Foundation

goal: Turn ADD's five competencies into a self-improving loop: each task's learnings, tagged by competency and human-confirmed, fold into a versioned PROJECT.md that sharpens DDD·SDD·UDD·TDD·ADD across milestones
stage: mvp · status: active · created: 2026-05-30

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

> Today the foundation update is a *manual, untracked* arrow ("stop and update
> PROJECT.md when a loop reveals the model was wrong"). v5 makes it **systematic
> and evidence-backed**: every loop emits competency-tagged learnings that, once
> the human confirms them, fold into a versioned foundation. The five
> (DDD · SDD · UDD · TDD · ADD) stop being write-once layers and become a measured
> learning loop that converges instead of drifts.

## Scope
In:  the self-improving layer for ADD's foundation — (1) competency-tagged OBSERVE
     deltas (the feedback signal: "this learning improves DDD / that one UDD"); (2) a
     human-gated foundation-update ritual that folds confirmed deltas into a *versioned*
     PROJECT.md; (3) tagging each task/milestone with its primary `*DD` driver so deltas
     route to the right competency and the five become visible in the flow; (4) a
     resume/set-task command so an in-progress loop is re-enterable mid-stream; (5) a
     light convergence signal (open vs folded deltas per competency).
Out: any AUTOMATED or unattended foundation edit — every fold is human-confirmed
     (judgment stays human); any ML / statistical "self-learning" — self-improving here
     means a tracked, evidence-backed, human-gated loop, NOT model training; any NEW
     always-loaded doc — deltas live in TASK.md, folds land in PROJECT.md (kept ≤1
     screen), the v2 Minimal pillar holds; any rework of the 7-phase sequence — v5
     extends OBSERVE + intake/scope and adds one command, it does not re-cut the flow.

## Shared decisions & glossary deltas   (living — every task must honor these)
- **Self-improving = tracked + evidence-backed + human-gated**, never autonomous. The AI
  proposes deltas and proposes folds; the human confirms. This is the v4-1 rule
  ("automate the work, never the judgment") applied to the foundation itself.
- **The engine is truth; the harness is intelligence** (v4-1). Tagging a learning by
  competency and judging whether a delta is real are JUDGMENT — method/skill artifacts,
  not `add.py` logic. The engine may *carry* a delta's shape and *count* it; it must not
  *decide* it. Mechanical-only tasks (resume, count) may live in `add.py`.
- **The Minimal pillar still holds** (v2). No command reads `docs/` at runtime. Deltas
  live in the already-loaded `TASK.md`; folds append to the already-loaded `PROJECT.md`,
  which stays one screen. v5 adds signal, not surface.
- **PROJECT.md becomes versioned.** A foundation version marker advances when confirmed
  deltas fold in; folds are append-only (never silent rewrites), so the survivor layer stays
  auditable. **Fold routing** (resolved by foundation-update-loop — two of the five competencies
  have no PROJECT.md section): DDD/SDD/UDD → their `PROJECT.md` section; **TDD/ADD → `CONVENTIONS.md`**
  (the engine survivor file); EVERY fold also appends a row to `PROJECT.md` §Key Decisions (the
  universal audit log). The version marker lives in `PROJECT.md`.
- New glossary terms: **Competency delta**, **Foundation version**, **`*DD` driver**.
- All design forks are decided with the human (AskUserQuestion) before a contract freezes.

## Shared / risky contracts (freeze these first)
- the **competency-delta shape** — `{ competency ∈ DDD|SDD|UDD|TDD|ADD, learning, evidence,
  status }` — every other task depends on it; freeze it first  -> competency-deltas
- the **PROJECT.md version marker + fold format** (where a confirmed delta lands, how the
  version advances)  -> foundation-update-loop

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] competency-deltas          depends-on: none              — OBSERVE emits learnings tagged by which of the 5 (DDD·SDD·UDD·TDD·ADD) they improve; defines the delta shape  (gate PASS 2026-05-30)
- [ ] competency-driver-tagging  depends-on: competency-deltas — intake/scope tag a task/milestone's primary `*DD` driver; deltas inherit it so they route to the right competency
- [ ] foundation-update-loop     depends-on: competency-deltas — a ritual gathers confirmed deltas and proposes versioned PROJECT.md edits; human confirms (AI proposes, human folds)
- [ ] convergence-signal         depends-on: competency-deltas — status shows open vs folded delta counts per competency (the lightest task; cuttable)
- [ ] resume-command             depends-on: none              — `add.py resume <slug>` re-points active_task; milestone-done clears a stale pointer (the restart-in-the-middle gap)

## Exit criteria (observable; map each to the task that delivers it)
- [x] a finished task records competency-tagged deltas in its OBSERVE phase        (← competency-deltas ✓)
- [ ] every task/milestone declares its primary `*DD` driver                       (← competency-driver-tagging)
- [ ] confirmed deltas fold into a versioned PROJECT.md via one human-gated ritual  (← foundation-update-loop)
- [ ] `add.py status` shows per-competency open/folded delta counts                 (← convergence-signal)
- [ ] a paused task resumes mid-stream with one command; no stale active_task       (← resume-command)
