# PLAN: Milestone exit-criteria render as delivered-by graph nodes

slug: exit-criterion-nodes · created: 2026-07-23 · stage: mvp
milestone: signal-graph
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 0 · GROUND — the observed map (anchors opened live 2026-07-23)

- `add-method/tooling/add_engine/milestones.py` · `_exit_criteria` (53) — parses `## Exit criteria` in MILESTONE.md, counts `- [x]`/`- [ ]` for a (met, total) tally. NO per-criterion `(← slug)` mapping today. (Kept UNTOUCHED — editing add_engine moves ENGINE_PKG_MD5; this task stays add.py-only so only ENGINE_MD5 re-pins.)
- `add-method/tooling/add.py` · `cmd_graph` + the `--signals` overlay (graph-view-signals, DONE) — the tail block that renders LIVE signals as `sig_` nodes + typed edges + `x_<slug>` fallback + `classDef`. The exit-criterion overlay extends this same block.
- MILESTONE.md exit-criterion line shape (this repo's own, e.g. signal-graph): `- [x] <observable> … (← <slug>)  (verify: <citation>)` — the `(← <slug>)` IS the delivered-by pointer; `[x]` = met.
- `node_id(slug)` = `t_<slug>` (task) / `p_<slug>` (planned); the `--signals` overlay already has the `shown`/`x_<slug>` machinery to reuse.
- Floor: the graph is a VIEW — this task READS MILESTONE.md only, adds no store, does not change `_exit_criteria`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: extend the opt-in `--signals` overlay so each milestone exit-criterion renders as a node edged `delivered-by` to the task that satisfies it, classed met/unmet — making goal-completion (the admin-longtail "7/10") a graph fact, not a checkbox count. Default output unchanged.
Framings weighed: fold into the existing `--signals` overlay (chosen — the milestone's thesis is ONE navigable honesty surface; a second flag fragments a lean UX) · a separate `--goals` flag (rejected — more surface for the same overlay; can be split later at zero cost)
Must:
<must>
  - M1 parse: `_exit_criterion_nodes(root)` PURE-reads each MILESTONE.md `## Exit criteria` section and returns per criterion {ms, idx, text, met: bool, delivered_by: slug|None} (delivered_by from the `(← <slug>)` pointer, None if absent).
  - M2 render: under `--signals`, each exit-criterion renders as node `ec_<ms>_<idx>` labelled met-glyph + truncated text.
  - M3 delivered-by edge: a criterion with a delivered_by task edges `-.->|delivered-by|` node_id(slug); a slug not in tasks uses the existing `x_<slug>` fallback; no pointer -> node with NO edge (never dangling).
  - M4 met/unmet class: `[x]` -> classDef ec_met, `[ ]` -> ec_unmet.
  - M5 default unchanged + pure: `graph` (no flag) prints no `ec_` node; the fn writes nothing, no store, `_exit_criteria` untouched.
  - M6 engine parity: add.py byte-identical 4-way + engine_pin.py ENGINE_MD5 re-pinned (ENGINE_PKG_MD5 unchanged — add_engine not touched).
</must>
Reject:
<reject>
  - a criterion line with no `(← slug)` pointer -> node rendered, NO delivered-by edge -> "unpointed_ok"
  - a `(← slug)` naming a task not on the board -> the `x_<slug>` fallback, never a bare id -> "missing_target_fallback"
</reject>
After:
<after>
  - `graph --signals` shows each milestone's exit-criteria as met/unmet nodes edged to their delivering tasks; `graph` alone is unchanged
</after>
Boundary: input is each MILESTONE.md `## Exit criteria` section; the tests must speak a met `[x]` criterion with `(← live-slug)`, an unmet `[ ]` with `(← live-slug)`, a criterion with no pointer, and a pointer to an unknown slug; plus the no-flag default (no `ec_`).
<assumptions>
  ⚠ folding exit-criteria into `--signals` (one overlay flag) rather than a separate `--goals` flag is the right UX — if wrong: a user wanting signals WITHOUT criteria (or vice-versa) can't separate them. Mitigated: both are "the honesty layer made navigable" (this milestone's whole goal); splitting into two flags later is additive and cheap. Cost if wrong is a flag split, not a redesign.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>
  - Given a milestone with one `[x] … (← alpha)` and one `[ ] … (← beta)` criterion, When `graph --signals` runs, Then two ec_ nodes render, each edged `-.->|delivered-by|` its task, one classed ec_met and one ec_unmet.
  - Given a criterion with no `(← slug)`, When `graph --signals` runs, Then its ec_ node renders with no delivered-by edge.
  - Given a criterion `(← ghosttask)` not on the board, When `graph --signals` runs, Then the edge target is `x_ghosttask`, no dangling id.
  - Given any board, When `graph` runs with no flag, Then no `ec_` node appears (default unchanged).
</scenarios>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — HARD, tamper-guarded)

```
_exit_criterion_nodes(root: Path) -> list[dict]     # PURE read of every MILESTONE.md
  for each milestone in state["milestones"], within its `## Exit criteria` section,
  for each line matching  - [ (x| ) ] <text>:
    {ms, idx (1-based within the ms), text, met: bool([x]), delivered_by: <slug from (← slug)> | None}
  missing file/section -> that milestone contributes nothing (fail-soft).

cmd_graph --signals (extend the existing overlay tail, additive):
  for n in _exit_criterion_nodes(root):
    nid = f"ec_{n['ms']}_{n['idx']}"
    glyph = "✓" if n["met"] else "○"
    node:  {nid}["{glyph} {text[:40]}"]            # quotes/brackets/pipe/newline stripped
    if n["delivered_by"]:
      tid = node_id(slug) if slug in tasks else x_<slug> fallback (missing|archived)
      edge:  {nid} -.->|delivered-by| {tid}
    class {nid} -> ec_met if met else ec_unmet
  classDef ec_met fill:#d3f9d8,stroke:#2b8a3e ; classDef ec_unmet fill:#f1f3f5,stroke:#868e96
  (--milestone <ms> filter: only that milestone's criteria render)
```
Schema: pure read of MILESTONE.md files. No state write, no store. `_exit_criteria` / add_engine untouched (ENGINE_PKG_MD5 stable).

Target (measurable): `_exit_criterion_nodes` returns the expected per-criterion dicts (met + delivered_by) for a fixture milestone; `graph --signals` renders ec_ nodes with delivered-by edges + met/unmet classes, x_ fallback for unknown targets; `graph` (no flag) has zero `ec_`; `test_exit_criterion_*` green; graph/parity/pin/signal-model regression floor green; add.py 4-way identical, ENGINE_PKG_MD5 unchanged.
Least-sure flag surfaced at freeze: [contract] folding exit-criteria into the existing `--signals` overlay (one honesty-overlay flag) rather than a separate `--goals` flag — chosen because signals + criteria together ARE this milestone's "navigable honesty layer"; a later split into two flags is additive and free. This is the render contract atomicity-signal sits beside.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: no

### Build-strategy (SOFT: preferred; the builder self-improves and records actual at verify)
Scope (may touch): `add-method/tooling/` `add-method/.add/tooling/` `add-method/src/add_method/_bundled/tooling/` `.add/tooling/` `./tests/`   >
Regression floor: the graph test(s) (`test_graph_views`, `test_graph_view_signals`) + tree parity + engine pin + `test_signal_model` — run green before the gate.
Persona (required): `.add/personas/methodology-engine-dev.md` (deterministic, fail-loud engine work; advisory, never lowers a gate)

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_exit_criterion_parse_met_and_pointer: a milestone with [x](← alpha) + [ ](← beta) -> two dicts, met flags + delivered_by correct · covers: M1
  - test_graph_exit_criterion_nodes_and_edges: --signals renders ec_ nodes edged -.->|delivered-by| their tasks · covers: M2,M3
  - test_exit_criterion_met_unmet_class: [x] -> ec_met, [ ] -> ec_unmet class lines · covers: M4
  - test_exit_criterion_missing_target_fallback: (← ghosttask) unknown -> x_ghosttask, no dangling · covers: M3, R:missing_target_fallback
  - test_exit_criterion_no_pointer_no_edge: a criterion with no (← slug) -> node, no delivered-by edge · covers: M3, R:unpointed_ok
  - test_graph_default_no_exit_nodes: `graph` (no flag) prints no ec_ node · covers: M5
  - test_exit_criterion_three_trees_identical: add.py byte-identical across the tooling trees · covers: M6
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned — added `_exit_criterion_nodes(root)` beside `_signals` (pure MILESTONE.md read, reusing the `## Exit criteria` section regex; `(← slug)` → delivered_by) + extended the SAME `--signals` overlay tail with an ec_ block (met glyph ✓/○, ec_met/ec_unmet class, `-.->|delivered-by|` edge, x_ fallback, no edge when unpointed). add.py-only so ENGINE_PKG_MD5 held (81553881); ENGINE_MD5 repinned acb9dcf6→ed8624a2 + 4-way sync. Scope declared the tooling DIRS up front — NO return-to-build. Dogfood proof: `graph --signals --milestone signal-graph` renders all 5 criteria, edges signal-model/graph-view-signals/exit-criterion-nodes to their tasks, x_atomicity-signal for the uncreated 4th, criterion 5 (no pointer) edgeless.
Code lives in: `add-method/tooling/` (add.py + engine_pin.py, 4-way; add_engine untouched)
Constraints: do NOT change any test or the frozen §3 contract; do NOT edit add_engine (keep ENGINE_PKG_MD5); stay inside §3 Scope; keep default `graph` byte-identical; repin ENGINE_MD5 + sync 4-way.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all §4 tests pass — including graph + parity + pin + signal-model floor
- [ ] coverage did not decrease
- [ ] no test or contract altered during build
- [ ] the green was EARNED — test_graph_default_no_exit_nodes proves the default view held
- [ ] ENGINE_PKG_MD5 unchanged (add_engine untouched)
- [ ] a person reviewed and approved the change

### GATE RECORD
Reported: no
Outcome: PASS | RISK-ACCEPTED | HARD-STOP
Reviewed by: name · date: date

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
harvested at done

### Spec delta
- [SPEC · open] a `--milestone <ms>` filter narrows the ec_ overlay to that milestone's criteria (already implemented via the shared `only` var); a `--signals=all` split for signals+criteria remains the open question inherited from graph-view-signals (evidence: `graph --signals --milestone signal-graph` scoped to 5 ec_ nodes, other milestones omitted)

### Competency deltas
- [ADD · open] folding exit-criteria into the existing `--signals` overlay (the frozen least-sure flag) paid off — ONE honesty surface, no second flag, and the ec_ block reuses the signal block's x_ fallback + text-sanitize verbatim; a later `--goals` split stays additive (evidence: 7 green, default `graph` byte-unchanged via test_graph_default_no_exit_nodes + test_graph_views 9 green)
- [ADD · open] declaring the tooling DIRS in §3 Scope up front (graph-view-signals lesson) again avoided the signal-model return-to-build — the engine_pin repin + 4-way sync landed in-scope, first-pass gate (evidence: check 446/0, tree-parity 6 green)
