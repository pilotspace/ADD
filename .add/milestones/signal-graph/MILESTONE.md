# MILESTONE: Unified signal graph — note = todo = delta as nodes

goal: Unify the three off-graph observation primitives (ephemeral note, todo, §7 delta) into ONE addressable signal node with a status lifecycle and edges, promote exit-criteria to delivered-by nodes, and render them through cmd_graph as a VIEW over existing text — no new persistence store; the honesty layer's output becomes navigable, not just readable
rationale: bucket new-milestone (a new theme no active milestone's goal covers) — extends the prior task-graph-native line (W1 edge-truth · W2 locate · W3 clause-repair · W4 graph-views) from a task/milestone graph to a full observation graph. Trigger: the admin-longtail analysis showed the honesty layer RECORDS everything (6 §7 deltas, 7/10 goal) but as prose you read by eye, not nodes you can navigate; and the scope-atomicity nudge is an ephemeral print that rots. Both are the same missing primitive: an addressable signal node.
stage: mvp · status: active · created: 2026-07-23T02:20:33+00:00
relations: extends: thin-engine-loop · relates-to: strategy-intake, honest-fidelity-meter

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/PLAN.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  ONE unified `signal` entity that subsumes today's three split primitives (the `note:` advisory print · the `todo` flat-list item · the §7 `[SPEC|competency · …]` delta line) — a signal carries a `status` lifecycle (advisory → captured → evidenced → resolved → dropped) and edges (observed-by → task · resolves-into → task · blocks → task); signals stay GIT-DIFFABLE TEXT (todos file + §7 lines) — the graph is a projection, never a database; `cmd_graph` extended to render signals + their edges as nodes from the existing `[→ slug]` backlinks; exit-criteria promoted to `exit-criterion` nodes with a `delivered-by` edge (the admin-longtail "7/10" legibility fix); the scope-atomicity nudge rebuilt to SEED a signal instead of printing (applied case).
Out: a real graph DATABASE or any new state.json store (the thin-engine floor — the graph is a VIEW over text that already exists); auto-creating tasks from signals (the human confirm-before-create floor stays); any change to the 6-phase task flow or the §7 delta EVIDENCE requirement; retiring the `note:` print convention for engine diagnostics (only OBSERVATION notes become signals, not every advisory line).

## Ground   (shared real-code context — gathered ONCE; every task's specify projects from this)
Touches (shared files · symbols): `add-method/tooling/add.py` — `cmd_graph` (1391, node_id/edge_style) · `cmd_todo` (2520) · `cmd_deltas` · `_edge_hints` (1126) · `cmd_relate` (1209) · the `[SPEC · seeded] … [→ slug]` delta-backlink parser (288) · `_milestone_relations` (1189) · the three byte-identical tooling trees
Anchors: the existing edge vocabulary (`depends_on` blocking · `extends`/`relates_to` legibility · component `produces`/`consumes`) · the `[→ slug]` delta→task backlink (the one real signal edge today) · the mermaid flowchart render contract (read-only, print-only, paste-into-any-renderer) · the §7 delta grammar + its `(evidence: …)` tail
Honors (conventions): the thin-engine / engine-minimalism floor (no new store; the graph is a view) · the engine RECORDS, the skill/human DRIVES (no engine auto-create of tasks from signals) · security is always HARD-STOP · three-tree byte-identity (bundle-parity tests) · deltas keep their evidence requirement
Issues/Risks (shared): unifying three primitives risks a migration of every existing todo + open §7 delta into the signal grammar — keep it BACKWARD-READING (old lines parse as signals with a default status, never a rewrite); the "graph is a view not a store" line is the load-bearing constraint — any task that adds a persisted node table breaks the milestone's own goal; over-noding (making everything a node) re-adds the ceremony this project keeps removing — the signal type is deliberately narrow (observations only)

## Shared decisions & glossary deltas   (living — every task must honor these)
- glossary: "signal" (the unified observation node: note = todo = delta at three lifecycle stages) · "signal status" (advisory · captured · evidenced · resolved · dropped) · "graph-as-view" (the DAG is a projection over existing text, not a persisted store)
- the three primitives UNIFY but stay stored where they already live (todos file · §7 lines) — a signal is a READING of that text, added status + edges, never a new file/table
- edges a signal carries: observed-by (→ the task that surfaced it) · resolves-into (→ the task that will close it, today's `[→ slug]`) · blocks (→ a task it gates, e.g. admin-longtail #25 blocks-on #72)
- exit-criteria become nodes with a delivered-by edge — a milestone's goal-completion is a graph fact, not a checkbox count
- backward-reading is mandatory: every existing todo + open delta must parse as a signal with a sensible default status; NO migration rewrite

## Shared / risky contracts (freeze these first)
- the `signal` grammar + status lifecycle + edge set (the text encoding every other task reads) -> owning task **signal-model**   (freeze BEFORE graph-view-signals / atomicity-signal cite it)
- the `cmd_graph` signal-node render contract (how a signal + its edges appear in the mermaid view) -> owning task **graph-view-signals**

## Tasks (breadth-first decomposition; detail lives in each PLAN.md)
- [ ] signal-model         depends-on: none          — define the unified signal entity: text encoding (todo + §7 delta share one grammar), status lifecycle, edge set. The contract the rest cite. Backward-reading old lines.
- [ ] graph-view-signals   depends-on: signal-model   — cmd_graph renders signals + observed-by/resolves-into/blocks edges as nodes; a VIEW over existing text, no new store
- [ ] exit-criterion-nodes depends-on: signal-model   — milestone exit-criteria render as delivered-by nodes; goal-completion becomes a graph fact (the admin-longtail 7/10 legibility fix)
- [ ] atomicity-signal     depends-on: signal-model   — reopen scope-atomicity-guard (change-request to its frozen §3): the nudge SEEDS a signal instead of an ephemeral print

## Exit criteria (observable; map each to the task that delivers it)
- [ ] note, todo, and §7 delta are read as ONE signal type with a status + edges, still stored as git-diffable text (no new store)   (← signal-model)  (verify: test_signal_unify — a todo line and a §7 delta line both parse to a signal carrying status + edges)
- [ ] `add.py graph` renders signals as nodes with observed-by / resolves-into / blocks edges                                       (← graph-view-signals)  (verify: test_graph_renders_signals — graph stdout contains signal nodes and their edge labels)
- [ ] a milestone's exit-criteria render as delivered-by nodes — goal-completion is visible as a graph fact                          (← exit-criterion-nodes)  (verify: test_graph_exit_criterion_nodes — each exit-criterion appears as a node with a delivered-by edge to its task)
- [ ] the scope-atomicity nudge seeds a persistent signal (not an ephemeral print), addressable after the freeze scrolls away        (← atomicity-signal)  (verify: test_atomicity_seeds_signal — freezing a multi-Part task creates an addressable signal, asserted after the freeze call)
- [ ] every pre-existing todo + open delta still parses (backward-reading) and no persistence store was added (thin-engine floor held) (← signal-model, graph-view-signals)  (verify: test_backward_read_existing plus a grep proving no new state-store key/table was added)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Cross-task review the AI fills — the evidence behind the EXISTING milestone-done gate, NOT a new approval.

### Ship by domain   (what changed, per bounded context)
- tooling : <add.py cmd_graph/cmd_todo/deltas + signal grammar — what shipped, or "untouched">
- skill   : <SKILL.md / phases/* / guides — signal/graph guidance, or "untouched">
- book    : <docs/* — the signal-graph chapter, or "untouched">

### Cross-task evidence   (one row per task)
- <slug> : gate=<PASS|RISK-ACCEPTED> · tests=<n green> · residue=<none|note>

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [ ] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which)
- goal: <restate the milestone goal — and the one evidence line that proves the ship meets it>

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> AI-written steps for THIS milestone (hints, not engine commands); MERGE is one small step; the human runs the cut.
- [ ] open a PR from the Close ship-review above; the human reviews + merges
- [ ] rebuild scope-atomicity-guard on the new signal primitive (its parked freeze reopens as a change-request)
- [ ] tag / publish / deploy  (human-run)
