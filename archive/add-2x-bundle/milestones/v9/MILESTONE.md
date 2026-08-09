# MILESTONE: Awareness surface — render what happened

goal: A person can see what just happened, what it cost, and what was learned — per-task phase results rolled up under a milestone retrospective — rendered on demand to stdout and persisted as RETRO.md at milestone close, without reading prose by hand
stage: mvp · status: active · created: 2026-06-02

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

> **Why now.** ADD already records everything a retrospective needs — `phase`/`gate`
> per task in state.json, the verify outcome + observe delta + competency deltas in each
> TASK.md, exit criteria + Close note in MILESTONE.md — but it never *renders* it. The
> only awareness surface, `status`, answers "where are we / what's next", never "what
> just happened / what did it cost / what did we learn." A human who wants the retro
> reads four files of prose by hand. v9 turns the scattered record into one render.

## Scope
In:  (1) **`add.py report [milestone]`** — a read-only command that prints a NESTED digest:
     a milestone header (goal · status · task + gate tally) → one block per task (its phase,
     gate outcome, tests-changed count, one-line observe delta) → a milestone footer
     (exit-criteria coverage X/Y · RISK-ACCEPTED waivers · carried-forward competency deltas).
     Defaults to the active milestone. (2) **RETRO.md at close** — the milestone-close ritual
     persists the SAME render to `.add/milestones/<v>/RETRO.md`, realizing appendix-f's
     spec'd "Milestone exit report" artifact.
Out: any new data capture — v9 renders what tasks ALREADY record; it adds no field to
     TASK.md/state.json and no new phase. Grading/scoring the retro (engine renders, human
     judges — carry v2 boundary). A hosted/web dashboard (that is v5's separate web line, if ever).
     Cross-milestone roll-ups or trend charts (single-milestone scope only). Editing or
     rewriting the deltas/Close note the retro surfaces (it reflects them verbatim).
     PER-PHASE DETAIL (deferred → next milestone): v9 reports each task's phase ROLLUP (which
     phase reached), NOT each phase's RESULT (scenarios set · contract frozen · verify findings ·
     per-phase observe). Owner-directed 2026-06-02 ("improve ADD to report each phase"); tracked
     as the [ADD · open] delta on report-render. A future loop adds a drill-down
     (`report <milestone> <task>` / `--phases`) — out of scope here to keep v9 shippable.

## Shared decisions & glossary deltas   (living — every task must honor these)
- **One renderer, one canonical content; presentation is a tty-only skin.** Both sinks come from
  ONE function — `render_report(root, state, mslug, *, width=72, ascii=False)` returns the
  CANONICAL plain text. RETRO.md persists exactly that canonical string. `report`'s stdout
  shows the SAME content but MAY skin it for the live terminal (color when tty, adaptive width
  64–100, ASCII glyph tier under a non-UTF-8 locale) — skinning never changes which facts
  appear, only their bytes. So the invariant is **content-identical**, not byte-identical to
  stdout: RETRO.md == `render_report(width=72, ascii=False)`, which a piped/redirected `report`
  also yields. (v3 lesson: a render's *facts* are the contract; its *pixels* are presentation.)
- **Structured-first, fail-closed on prose.** Reliable fields come from structured state —
  `phase`/`gate` from state.json, exit-criteria coverage from MILESTONE.md checkboxes, waivers
  from recorded gate outcomes. Prose fields (observe delta, carried learnings, tests-changed)
  are extracted by KNOWN section headers / the competency-delta grammar; any miss renders a
  visible `(unknown)` marker — never a silent omission (carry v2/v3 fail-closed).
- **`report` is pure read-only; RETRO.md is a doc artifact, never engine state.** `report`
  writes nothing. The close ritual writes `RETRO.md` — a generated DOCUMENT (like a milestone
  doc), it never mutates `state.json`. This preserves the "read-only surfaces don't mutate
  state" rule while still persisting the exit report.
- **Engine renders structure; the human owns judgement** (carry v2 boundary): the retro
  surfaces deltas/outcomes as written; it does not grade, score, or rewrite them.
- New glossary terms: **Retro / RETRO.md** — the rendered milestone exit report (appendix-f),
  auto-built from per-task results + the Close note. **Awareness surface** — a read-only render
  of recorded state for a human (`status` = where-we-are; `report` = what-happened).

## Shared / risky contracts (freeze these first)
- the **render shape** — the exact nested digest (milestone header → per-task block → footer),
  which field is sourced from state.json vs TASK.md vs MILESTONE.md, and the `(unknown)`
  fail-closed marker. Both tasks consume it; freeze it in report-render first.  -> owning task report-render

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [x] report-render   depends-on: none          — `add.py report [milestone]`: read state.json + each TASK.md + MILESTONE.md, render the nested digest to stdout; freeze the render shape + `(unknown)` fail-closed rule
- [x] retro-artifact  depends-on: report-render  — persist the SAME render to `.add/milestones/<v>/RETRO.md` at milestone close; reuse the one renderer; write a doc, never touch state.json

## Exit criteria (observable; map each to the task that delivers it)
- [x] `add.py report` (no arg) prints a nested digest for the active milestone: header + one block per task (phase · gate · tests-changed · observe delta) + footer (exit-criteria coverage · waivers · carried deltas)   (← report-render)
- [x] `add.py report <v>` renders a named milestone; an unparseable/missing prose field shows `(unknown)`, never a silent gap, and `report` writes nothing to disk                                                       (← report-render)
- [x] closing a milestone writes `.add/milestones/<v>/RETRO.md` byte-identical to the canonical render `render_report(root, state, <v>, width=72, ascii=False)` (the same plain content a piped `report <v>` yields; tty color/width are presentation-only)                              (← retro-artifact)
- [x] writing RETRO.md leaves `state.json` unchanged (read-only-state invariant holds)                                                                                                                                      (← retro-artifact)
