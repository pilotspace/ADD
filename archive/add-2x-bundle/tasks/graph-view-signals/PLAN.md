# PLAN: cmd_graph renders signals as nodes (view over text)

slug: graph-view-signals · created: 2026-07-23 · stage: mvp
milestone: signal-graph
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 0 · GROUND — the observed map (anchors opened live 2026-07-23)

- `add-method/tooling/add.py` · `cmd_graph` (~1391) — `flowchart TD`; milestone subgraphs wrap `t_<slug>["<slug> · <phase>"]` nodes; `node_id(slug)` = `t_<slug>` (task) / `p_<slug>` (planned); `edge_style` tuples (depends_on `-->`, extends `-.->`, relates_to `-.-`); `extra_nodes` renders missing/archived edge targets as `x_<slug>`; `classDef done/live/planned`. Deterministic, read-only, print-only.
- `add-method/tooling/add.py` · `_signals(root)` (signal-model, DONE @ v1) — returns `[{id, kind, text, status, edges}]`; edges are `(rel, target_slug)`, rel in {observed-by, resolves-into, blocks}; status in {advisory, captured, evidenced, resolving, resolved, dropped}.
- Engine-edit coupling (signal-model lesson): add.py is 4-way twinned + md5-pinned — the scope MUST cover the tooling DIRS + `engine_pin.py`, not just add.py.
- Floor: the graph is a VIEW — this task only READS `_signals` + renders; it adds no store and does not change `_signals`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `cmd_graph` gains an opt-in `--signals` layer that renders the signals `_signals(root)` produces as nodes wired to their task nodes by typed edges — making the honesty layer's observations navigable in the same mermaid view. Default output (no flag) stays byte-identical.
Framings weighed: opt-in `--signals` flag (chosen — the default graph is asserted byte-for-byte by existing tests, and 100+ tasks' deltas would swamp the default view) · always-on (rejected — breaks every current graph test and floods the diagram)
Must:
<must>
  - M1 default unchanged: `add.py graph` with no `--signals` prints byte-identical output to today.
  - M2 signal nodes: with `--signals`, each LIVE signal (status not in {resolved, dropped}) renders as a node `sig_<sanitized-id>` labelled with kind · status · truncated text; the id is mermaid-safe (non-alphanumeric -> `_`).
  - M3 typed edges: a signal's edges render to the task node — observed-by `-.->`, resolves-into `-->`, blocks `==>` — reusing node_id; a target task not shown reuses the existing `x_<slug>` extra-node fallback (never a dangling id).
  - M4 pure + scoped: the layer only READS `_signals`; no write, no `_signals` change; `--milestone <ms>` still filters (signals whose observed-by task is outside the milestone are omitted).
  - M5 engine parity: add.py byte-identical 4-way + engine_pin.py ENGINE_MD5 repinned across the tracked trees.
</must>
Reject:
<reject>
  - a signal with status resolved or dropped -> not rendered under `--signals` (only live signals) -> "resolved_omitted"
  - a resolves-into/blocks target that is an unknown slug -> the `x_<slug> · missing` fallback, never a bare/dangling node id -> "missing_target_fallback"
</reject>
After:
<after>
  - `add.py graph --signals` shows todos + open §7 deltas as nodes edged to their tasks; `add.py graph` alone is unchanged
</after>
Boundary: input is the live board via `_signals` + the existing task/milestone graph; the tests must speak a captured todo, an evidenced SPEC delta (observed-by), a seeded delta (resolves-into to a live task), a seeded delta pointing at an unknown slug (missing fallback), a resolved/dropped signal (omitted), and the no-flag default (byte-identical).
<assumptions>
  ⚠ rendering only LIVE signals (excluding resolved/dropped) is the right default — if wrong: a user wanting the full resolved history has no view. Mitigated: resolved/dropped are closed observations (noise for a "what's open" graph); a later `--signals=all` can widen it. Cost if wrong is an added flag value, not a redesign.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>
  - Given the live board, When `graph` runs with no flag, Then output is byte-identical to the pre-change engine.
  - Given a captured todo + an evidenced SPEC delta on task alpha, When `graph --signals` runs, Then a sig_ node for each appears, the delta node edged `-.->|observed-by|` to t_alpha.
  - Given a seeded delta on alpha pointing `[→ beta]` (beta live), When `graph --signals` runs, Then the sig node edges `-->|resolves-into|` t_beta.
  - Given a seeded delta pointing at an unknown slug, When `graph --signals` runs, Then the target renders via the `x_<slug> · missing` fallback, no dangling id.
  - Given a resolved todo and a dropped delta, When `graph --signals` runs, Then neither renders.
</scenarios>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — HARD, tamper-guarded)

```
cmd_graph  (additive `--signals` flag; default path byte-unchanged):
  sanitize(id)  -> re.sub(r"[^0-9A-Za-z]", "_", id)          # mermaid-safe node id
  if args.signals:
    LIVE = [s for s in _signals(root) if s["status"] not in {"resolved", "dropped"}]
    for s in LIVE (excluding any whose observed-by task is filtered out by --milestone):
      node:  sig_<sanitize(id)>["<kind> · <status>\n<text[:40]>"]      # quotes/newlines stripped from text
      for (rel, target) in s["edges"]:
        arrow = {observed-by: "-.->", resolves-into: "-->", blocks: "==>"}[rel]
        tid = node_id(target) if target in tasks else x-fallback (reuse extra_nodes: x_<target> · missing|archived)
        emit:  sig_<sanitize(id)> {arrow}|{rel}| {tid}
    classDef signal fill:#e7f5ff,stroke:#1971c2 ; class every sig_ node signal
argparse: `graph` parser gains `--signals` (store_true).
```
Schema: pure read (adds `_signals` render to cmd_graph). No state write, no new store. `_signals` itself is UNTOUCHED (frozen @ signal-model v1).

Target (measurable): `graph` (no flag) stdout byte-identical to the pre-change engine (captured baseline); `graph --signals` stdout contains the sig_ nodes + the three edge arrows with correct labels for the §2 fixtures, omits resolved/dropped, and uses the x_ fallback for an unknown target; `test_graph_signals_*` green; graph/parity/pin regression floor green; add.py 4-way identical.
Least-sure flag surfaced at freeze: [contract] rendering only LIVE signals (status not resolved/dropped) as the `--signals` default — a superset view (`--signals=all`) is deferred; chosen because an open-work graph should show open observations, and the exclusion is a filter over untouched source, not a data change. This is the render contract exit-criterion-nodes will sit beside.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: no

### Build-strategy (SOFT: preferred; the builder self-improves and records actual at verify)
Scope (may touch): `add-method/tooling/` `add-method/.add/tooling/` `add-method/src/add_method/_bundled/tooling/` `.add/tooling/` `./tests/`   >
Regression floor: the existing graph test(s) (`test_*graph*`) + tree parity + engine pin + `test_signal_model` — run green before the gate.
Persona (required): `.add/personas/methodology-engine-dev.md` (deterministic, fail-loud engine work; advisory, never lowers a gate)

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_graph_default_byte_identical: `graph` with no flag == pre-change baseline output · covers: M1
  - test_graph_signals_nodes_and_observed_by: --signals renders a todo + evidenced-delta node, delta edged -.->|observed-by| its task · covers: M2,M3
  - test_graph_signals_resolves_into: a seeded delta edges -->|resolves-into| the live target task · covers: M3
  - test_graph_signals_missing_target_fallback: a seeded delta -> unknown slug renders x_<slug> · missing, no dangling id · covers: M3, R:missing_target_fallback
  - test_graph_signals_omits_resolved_dropped: resolved todo + dropped delta do not render · covers: M2, R:resolved_omitted
  - test_graph_signals_three_trees_identical: add.py byte-identical across the tooling trees · covers: M5
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned — added `--signals` argparse flag + an additive overlay block at the tail of cmd_graph (LIVE signals as sig_ nodes, typed edges to node_id, x_ fallback for missing targets, classDef signal). Default path byte-unchanged (test_graph_views 35 green). Scope declared the tooling DIRS up front (signal-model lesson) so the engine_pin repin (3eb6dc23→acb9dcf6) + 4-way sync were in-scope — NO return-to-build this time.
Code lives in: `add-method/tooling/` (add.py + engine_pin.py, 4-way)
Constraints: do NOT change any test or the frozen §3 contract; do NOT change `_signals` (frozen @ signal-model v1); stay inside §3 Scope; keep the default `graph` output byte-identical; repin engine_pin.py + sync 4-way (the signal-model coupling).

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all §4 tests pass — including graph + parity + pin + signal-model regression floor
- [ ] coverage did not decrease
- [ ] no test or contract altered during build
- [ ] the green was EARNED — test_graph_default_byte_identical proves the default view did not drift
- [ ] no exposed secrets, injection openings, or unexpected dependencies
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
- [SPEC · open] `--signals=all` deferred: the overlay shows only LIVE signals (status not resolved/dropped); a full-history value is a follow-up if a resolved-observation view is wanted (evidence: test_graph_signals_omits_resolved_dropped green — 4 live nodes, resolved/dropped omitted)

### Competency deltas
- [ADD · open] declaring the tooling DIR (not add.py the file) in §3 Scope from the start made the engine_pin repin + 4-way sync in-scope — the signal-model return-to-build did not recur here (evidence: gate passed first attempt; scope-echo showed .add/tooling/ [ok])
