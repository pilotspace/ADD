# MILESTONE: Production-ready ADD

goal: gates enforced by CI distinct from the agent; AI agents beyond Claude follow ADD; 1.1.0 published
stage: mvp · status: active · created: 2026-06-05

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  the enforcement gap open since v7 ("a self-asserted gate is circular") closed by
     `add.py audit` + CI wiring; the high-risk guard moved prose→engine; non-Claude
     agents routed to the phase guides via AGENTS.md + the CLI; the one-approval
     checklist surfaced at the freeze seam; version 1.1.0 on npm + PyPI.
Out: the full production observe loop (monitors/feedback channel) and the dogfood
     stage flip mvp→production — both post-v14 decisions per the confirmed
     def-of-done; any judgment INSIDE the engine (audit checks record SHAPE, never
     decides outcomes — the engine stays judgment-free); telemetry of any kind.

## Shared decisions & glossary deltas   (living — every task must honor these)
- The audit is JUDGMENT-FREE: it verifies that human seams left well-formed records
  (a named human at the freeze, one gate outcome, a human-named reviewer wherever the
  security line carries text) — it never re-decides an outcome.
- Enforcement lives OUTSIDE the agent: CI invokes audit; the agent cannot stamp its
  own enforcement green (never-self-gate, foundation v2).
- Additive evolution: no existing command, JSON key, or exit-code semantic changes;
  `audit` is a new read-only command with its own exit codes.
- Verified-closed gaps are NOT rescoped: CI suite runs (ci.yml), `use <slug>`,
  fold-pressure nudge all shipped — re-verify any claimed gap before scoping (v10).
- 3-tree md5 parity for every touched artifact.

## Shared / risky contracts (freeze these first)
- `add.py audit` exit codes + finding grammar -> owning task gate-audit
  (audit-ci and high-risk-signal both consume it)

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] gate-audit         depends-on: none       — `add.py audit`: read-only checks of recorded human seams (FROZEN-by-name · one gate outcome · security-line ⇒ human reviewer · no RISK-ACCEPTED on security)
- [x] audit-ci           depends-on: gate-audit — audit wired into ci.yml + shipped in the package; CI fails on a malformed seam record
- [x] high-risk-signal   depends-on: gate-audit — `unguarded_high_risk_auto` detected by the engine/audit, not prose
- [x] agent-portability  depends-on: none       — AGENTS.md block routes any agent to the phase guides through the CLI alone
- [x] review-checklist   depends-on: none       — the one-approval review checklist surfaced at the freeze seam (skill prose)
- [x] release-1-1-0      depends-on: audit-ci   — CHANGELOG · version 1.1.0 · npm + PyPI publish via tag · GETTING-STARTED refresh

## Exit criteria (observable; map each to the task that delivers it)
- [x] `add.py audit` exits non-zero naming the task when a done task lacks a human-stamped freeze or a well-formed GATE RECORD  (← gate-audit)
- [x] CI fails on a commit introducing a malformed seam record — enforcement is a job distinct from the agent  (← audit-ci)
- [x] A high-risk/method-defining scope left at autonomy auto is refused by the engine, not by prose  (← high-risk-signal)
- [x] A non-Claude agent can locate and follow the correct phase guide starting from AGENTS.md alone  (← agent-portability)
- [x] The freeze seam presents a review checklist without re-adding GSD-style ceremony  (← review-checklist)
- [x] npm `@pilotspace/add` and PyPI `pilotspace-add` are both live at 1.1.0 with a CHANGELOG  (← release-1-1-0; run 27009563639, `npm view` -> 1.1.0, PyPI JSON -> 1.1.0, 2026-06-05)
