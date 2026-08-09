# MILESTONE: V23

goal: Every human decision gate presents a transparent synthesized report — the goal it serves, what's been achieved toward it, and the plan ahead — so the human confirms with full sight of the work's arc, not a local snapshot.
rationale: new-major — decision-point transparency is a new method theme no prior milestone's goal covers; it enriches the synthesized report at every human gate (lock · freeze · verify · intake · scope · close · graduation) with a goal · achievement · plan arc. Confirmed via /add intake on 2026-06-09.
stage: mvp · status: active · created: 2026-06-09

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  Enrich `report-template.md` with a GOAL -> ACHIEVEMENT -> PLAN arc integrated with the existing 5 blocks (SUMMARY · DECISION · ⚠ · EVIDENCE · NEXT); apply it consistently to EVERY human gate — baseline-lock · contract-freeze · verify · intake · scope · milestone-close · graduation; source the arc from engine facts that already exist (m-goal · exit-criteria met/total · tasks done · DECIDE NEXT); align the book + glossary.
Out: No change to gate LOGIC or outcomes (same approvals — only the presentation gets richer) · no new gates · no wording-lint or frozen-contract changes · not a dashboard (chat report only).

## Shared decisions & glossary deltas   (living — every task must honor these)
- The arc is PRESENTATION, never a new gate — it never changes a PASS / RISK-ACCEPTED / HARD-STOP / freeze semantic.
- Engine-sourced facts only: the EVIDENCE rule extends to the arc — goal · achievement · plan are pulled from `add.py` output, never re-typed from memory.
- The arc ADAPTS per gate (verify's achievement = tests + evidence; close's = exit-criteria met; intake's = the request sized) but the three-part shape (goal · achievement · plan) is constant.
- Honest scope: "achievement" reports proven facts, never aspirational ones.
- New glossary term: **the decision arc** (goal · achievement · plan) — the transparency layer every gate report carries.

## Shared / risky contracts (freeze these first)
- the report-arc shape — the exact goal/achievement/plan layer in `report-template.md` + whether it is template-composed from existing `add.py` output or needs the engine to surface a new fact -> owning task `report-arc`

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] report-arc        depends-on: none         — enrich `report-template.md` with the goal->achievement->plan arc + per-gate guidance + the SKILL pointer; freeze the arc shape (template-composed vs engine-sourced) (freeze-first) — DONE: gate PASS 2026-06-09, ARC block above the 5 blocks, 3 trees byte-identical, +test_report_arc
- [x] arc-gate-wiring   depends-on: report-arc   — ensure every human-gate path (setup-lock · contract · verify · intake · scope · loop · graduate) presents the arc — DONE: gate PASS 2026-06-09, all 7 guides cue the ARC, reconcile rule folded central, +test_arc_gate_wiring
- [x] arc-book-align    depends-on: report-arc   — align the book (decision-point / report chapter) + GLOSSARY with the arc — DONE: gate PASS 2026-06-09, GLOSSARY term + 02-the-flow span all 7 wired gates (v1→v2 change-request closed a 5-of-7 gap at verify), +test_decision_arc_book, 4 trees byte-identical, 691 OK

## Exit criteria (observable; map each to the task that delivers it) — all met, human-confirmed 2026-06-09
- [x] `report-template.md` defines the goal->achievement->plan arc integrated with the 5 blocks, with per-gate guidance   (← report-arc)
- [x] every human gate (lock · freeze · verify · intake · scope · close · graduation) presents the arc — traceable in each gate path   (← arc-gate-wiring)
- [x] the book + GLOSSARY describe the decision arc consistently with the gates   (← arc-book-align)
