# MILESTONE: Quality floors for lean ADD

goal: convert the WV1 wm2 miss (own tests spoke a friendlier input dialect than the spec's own examples → aware/naive datetime crash shipped green) into narrow, ~zero-turn floors — the lean lane keeps its −27–33% cost while the failure CLASS is closed; quality is bought with mechanical floors, never with re-added ceremony
stage: mvp · status: active · created: 2026-07-10T17:12:27+00:00 · lane: tiny
release: 1.18.0

> Tiny plan — small scope, one approval. Keep it to a handful of lines; if it
> outgrows this shape, recreate without --tiny (the full SDD scaffold).
> Origin: benchmark evidence (results/2026-07-wv1-rep0.md root-cause) + the human's
> 4-lever pick, 2026-07-10 ("build floors now", no reproduction spend).

## Plan

1. **spec-dialect-floor** — engine check at the tests→build crossing: the red suite must exercise the §3/§1 contract's own literal example values (e.g. a `Z`-suffixed timestamp in the contract ⇒ at least one test carries one). Warn-then-gate shape like scope-decl: a crossing warning first, audit-measured.
2. **fast-lane-boundary-line** — TASK.fast.md carries a `Boundary:` line (≥1 format-variant per external input shape); the fast freeze refuses a placeholder there the same way unflagged_freeze refuses a missing least-sure flag.
3. **refute-dialect-check** — one §6 line in both templates: "input dialect: tests speak the same value formats as the spec's examples — confirmed by <where>"; audit-measured like the other verify records.
4. **data-sensitivity-vocab** — GLOSSARY.md sensitivity classes gain the guidance entry: datetime/money/timezone arithmetic ⇒ `data` (full lane); sensitivity.md guide names the wm2 evidence.

## Done when

- a fast task whose contract pins a `Z`-timestamp example cannot cross tests→build with a suite that never uses one (warning + audit named) — pinned by test
- a fast freeze with a placeholder `Boundary:` line is refused with a repair-carrying error — pinned by test
- both templates render the §6 dialect line; `add.py check` counts it like the other audit-measured records
- GLOSSARY/sensitivity guide name the datetime/money/tz ⇒ data rule with the wm2 evidence line
