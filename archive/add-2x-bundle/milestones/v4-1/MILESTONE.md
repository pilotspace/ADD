# MILESTONE: Self-driving ADD · 1 — Interface & Intake

goal: Make ADD harness-drivable and self-scoping: machine-readable state (--json + owner/stop) plus an AI-facilitated request->versioned-milestone intake loop, framed as ADD
stage: mvp · status: active · created: 2026-05-29

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

> First slice of the **v4 "Self-driving ADD"** roadmap (full autonomous lifecycle,
> delivered as thin sub-milestones). v4-1 ships the harness *interface* + the *intake*
> loop. v4-2 = document autopilot + build corridor. v4-3 = orchestration + gate-guard.

## Scope
In:  the enabling layer for an autonomous ADD lifecycle — (1) machine-readable engine
     state so ANY harness (Claude Code, Codex, CI) can read where the project is and where
     it must stop; and (2) an AI-facilitated intake loop that turns a raw request into a
     versioned milestone + plan, framed in ADD's own vocabulary (the thing this very
     session did by hand). Autonomy here = the AI drives the *facilitation*; the human
     still makes the *decisions* through the discussion.
Out: the build corridor and "tests-red-before-build" enforcement (v4-2); the end-to-end
     orchestrator and the self-sign gate-guard (v4-3); L3 cross-task fan-out; any path
     that lets the AI sign a gate or a waiver on the human's behalf.

## Shared decisions & glossary deltas   (living — every task must honor these)
- **Automate the work, never the judgment.** The two human seams are irreducible:
  *scope-freeze* (approve the milestone plan) and *verify-gate* (vouch for the result).
  The AI drafts everything; producing a draft is not vouching for it.
- **The loop is fractal** (existing book idea): the milestone-altitude intake loop mirrors
  the per-task Specify->Scenarios->Contract — scope the request, name the exit criteria,
  freeze the plan. Same rule, milestone scale.
- **The engine is the source of truth; the harness is the intelligence.** `--json` exposes
  state + stop-signals; it carries NO orchestration logic and reads no Story at runtime
  (the v2 Minimal pillar still holds — JSON is built from State, not docs).
- **Fail-closed, parseable.** `--json` always emits VALID json (even with no active task);
  errors go to stderr with a clean (empty) stdout — never half-printed json.
- All design forks are decided with the human (AskUserQuestion) before a contract freezes.

## Shared / risky contracts (freeze these first)
- the `--json` state schema: field set, the `owner` enum (human|seam|ai) and how each phase
  maps to it, and the `stop` signal's meaning -> machine-state-json
- the versioning rule the intake loop applies (new-major | sub-milestone | task) -> versioning-policy

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] machine-state-json   depends-on: none                 — `guide`/`status --json` expose phase · owner · stop; backward-compatible  (gate PASS 2026-05-29)
- [x] versioning-policy    depends-on: machine-state-json   — classify a request: new-major | sub-milestone | task (AI proposes, human confirms)  (gate PASS 2026-05-30)
- [x] scope-loop           depends-on: versioning-policy    — AI-facilitated request -> versioned `MILESTONE.md` proposal, framed as ADD  (gate PASS 2026-05-30)

## Exit criteria (observable; map each to the task that delivers it)
- [x] `add.py guide --json` and `status --json` emit valid, parseable state incl. owner+stop   (← machine-state-json ✓)
- [x] the human-text output is unchanged when `--json` is absent (backward compatible)          (← machine-state-json ✓)
- [x] given a request, the AI proposes a version (major/sub/task) with a recorded rationale      (← versioning-policy ✓)
- [x] given a request, the AI produces a confirmed versioned `MILESTONE.md` via discussion        (← scope-loop ✓)
