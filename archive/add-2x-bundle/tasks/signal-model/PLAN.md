# PLAN: Unified signal grammar — note = todo = delta, status + edges

slug: signal-model · created: 2026-07-23 · stage: mvp
milestone: signal-graph
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 0 · GROUND — the observed map (anchors opened live 2026-07-23)

- `add-method/tooling/add.py` · `cmd_todo` (2520) — a todo is `state["todos"]` = `{id, text, created, status: open|done}`. Addressable (int id), off-graph today.
- `add-method/tooling/add_engine/constants.py` · `_SPEC_DELTA_RE` (281) `- [ SPEC · open|seeded|dropped|carried ] text` · `_DELTA_RE` (274) competency `- [DDD|SDD|UDD|TDD|ADD · status] text` (groups: competency, status, text) · `_EVIDENCE_RE` (280) trailing `(evidence: …)`.
- `add-method/tooling/add.py` (288) — the `[SPEC · seeded] … [→ slug]` delta→task backlink parser: the ONE real signal edge that exists today (resolves-into).
- `add-method/tooling/add.py` · `_raw_phase_bodies(root, slug)` — reads a task's §7 body text (where deltas live); `cmd_graph` (1391) renders task/milestone nodes + depends_on/extends/relates_to edges.
- Floor: the graph is a VIEW — this task adds a PURE projection reader over `state["todos"]` + §7 lines; NO new store, NO line rewrite (backward-reading).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: one pure reader `_signals(root)` that projects the three split observation primitives (todo · SPEC delta · competency delta) into a unified `signal` node list — each with a stable id, a status on one lifecycle, and edges — reading existing text in place, writing nothing.
Framings weighed: projection reader over existing text (chosen — honors the thin-engine floor; the graph is a view) · a new `state["signals"]` store (rejected — a second source of truth, breaks the milestone's own goal, needs a migration)
Must:
<must>
  - M1 unify: `_signals(root)` returns one Signal shape `{id, kind, text, status, edges}` for todos AND both §7 delta tracks, from a single read of state["todos"] + every task's §7 body.
  - M2 status lifecycle: each source maps onto ONE closed status set {advisory, captured, evidenced, resolving, resolved, dropped} by a defined rule (open todo -> captured · done todo -> resolved · SPEC open -> evidenced-if-evidence-else-captured · SPEC seeded -> resolving · SPEC dropped -> dropped · competency open -> evidenced).
  - M3 edges: a signal carries typed edges `(rel, target_slug)` with rel in {observed-by, resolves-into, blocks}; observed-by points at the task whose §7 holds it, resolves-into reuses the existing `[→ slug]` backlink.
  - M4 stable addressable id: todos -> `t<id>`; §7 deltas -> `<track>:<task-slug>:<ordinal>` (track = s|c) — stable across reads so a signal can be named.
  - M5 backward-reading, no write: every pre-existing todo + §7 delta parses to a signal with a sensible default status; `_signals` performs NO write and adds NO new state key/store.
  - M6 tree parity: byte-identical across all three tooling trees.
</must>
Reject:
<reject>
  - a malformed §7 line / corrupt todos entry -> skipped, never raises -> "silent_skip" (a projection is fail-soft)
  - an unknown competency/status token -> the line is skipped, not coerced -> "unknown_token_skip"
</reject>
After:
<after>
  - calling `_signals(root)` on the live project returns todos and §7 deltas as one typed node list with status + edges
  - state.json is byte-unchanged by the call (pure read); no `signals` key is created
</after>
Boundary: the input shapes the tests must speak — an open todo · a done todo · a SPEC delta [open] with and without `(evidence:)` · a SPEC delta [seeded … [→ slug]] · a SPEC delta [dropped] · a competency delta [ADD · open] · a malformed §7 line (skipped). Note-kind signals (the ephemeral advisory) are OUT of this task — the atomicity-signal task adds the seed-a-note path onto this grammar.
<assumptions>
  ⚠ the six-state lifecycle {advisory, captured, evidenced, resolving, resolved, dropped} is the right closed set — if wrong: a real observation state has no home and a signal is mis-labeled. Mitigated: the set is a superset of today's todo{open,done} + SPEC{open,seeded,dropped} + competency{open}, so every existing line maps; "advisory" is reserved for the note-kind the next task adds. Cost if wrong is a rename, not data loss (the source text is untouched).
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>
  - Given state["todos"] with one open + one done todo, When _signals runs, Then two signals appear: t<id> captured and t<id> resolved.
  - Given a task §7 with `[SPEC · open] … (evidence: X)`, When _signals runs, Then a signal s:<slug>:1 status=evidenced with an observed-by edge to <slug>.
  - Given a task §7 with `[SPEC · seeded] … [→ other]`, When _signals runs, Then status=resolving with a resolves-into edge to <other>.
  - Given a task §7 with `[SPEC · dropped] …`, When _signals runs, Then status=dropped.
  - Given a competency delta `[ADD · open] … (evidence: Y)`, When _signals runs, Then a signal c:<slug>:1 status=evidenced observed-by <slug>.
  - Given a malformed §7 line and a corrupt todos entry, When _signals runs, Then both are skipped and no exception is raised.
  - Given any of the above, When _signals runs, Then state.json is byte-identical afterward and has no "signals" key.
</scenarios>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — HARD, tamper-guarded)

```
Signal = { id: str, kind: str, text: str, status: str, edges: list[(rel, target_slug)] }
  kind   in {todo, spec-delta, competency-delta}
  status in {advisory, captured, evidenced, resolving, resolved, dropped}   # closed set
  rel    in {observed-by, resolves-into, blocks}

_signals(root: Path) -> list[Signal]        # PURE projection — reads, never writes
  from state["todos"]:
    open  -> id=f"t{id}"  kind=todo  status=captured   edges=[]
    done  -> id=f"t{id}"  kind=todo  status=resolved   edges=[]
  from each task's §7 body (via _raw_phase_bodies), per matched line, ordinal n (1-based per track per task):
    SPEC   [open]           -> id=f"s:{slug}:{n}"  status = evidenced if (evidence:…) else captured  edges=[(observed-by, slug)]
    SPEC   [seeded → ptr]   -> id=f"s:{slug}:{n}"  status = resolving   edges=[(observed-by, slug), (resolves-into, ptr)]
    SPEC   [dropped]        -> id=f"s:{slug}:{n}"  status = dropped     edges=[(observed-by, slug)]
    comp   [DD · open]      -> id=f"c:{slug}:{n}"  status = evidenced   edges=[(observed-by, slug)]
  malformed line / corrupt todo -> skipped (fail-soft), never raises.
```
Schema: reads `state["todos"]` + `.add/tasks/*/PLAN.md` §7 via existing primitives. Writes NOTHING. Adds NO state key. Reuses `_SPEC_DELTA_RE` / `_DELTA_RE` / `_EVIDENCE_RE` from constants.py — no new grammar, only a unified projection.

Target (measurable): `_signals(root)` on a fixture project returns the exact expected Signal list (id · kind · status · edges asserted) across all seven §2 scenarios; a byte-compare proves state.json unchanged and no "signals" key added; `test_signal_*` green; three-tree parity + the existing delta/todo suites stay green; no new state-store key anywhere (grep-asserted).
Least-sure flag surfaced at freeze: [contract] the six-state lifecycle {advisory, captured, evidenced, resolving, resolved, dropped} is the right closed set — it is a superset of every existing todo/SPEC/competency status so all current lines map, and "advisory" is held for the note-kind the atomicity-signal task adds; if a real observation state is missing, it is a rename over untouched source text, not data loss. This set is the contract graph-view-signals + atomicity-signal both cite.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: no

### Build-strategy (SOFT: preferred; the builder self-improves and records actual at verify)
Scope (may touch): `add-method/tooling/` `add-method/.add/tooling/` `add-method/src/add_method/_bundled/tooling/` `.add/tooling/` `./tests/`   >
Regression floor: the existing delta + todo suites (`test_*delta*`, `test_*todo*`) + bundle-parity (three-tree byte-identity) — run green before the gate.
Persona (required): `.add/personas/methodology-engine-dev.md` (deterministic, fail-loud engine work; advisory, never lowers a gate)

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_signal_todo_open_and_done: two todos -> t<id> captured + t<id> resolved · covers: M1,M2,M4
  - test_signal_spec_open_evidenced: SPEC [open] (evidence:) -> evidenced + observed-by edge · covers: M1,M2,M3
  - test_signal_spec_seeded_resolving: SPEC [seeded → other] -> resolving + resolves-into edge · covers: M2,M3
  - test_signal_spec_dropped: SPEC [dropped] -> dropped · covers: M2
  - test_signal_competency_open: competency [ADD · open] -> c:<slug>:1 evidenced · covers: M1,M2,M4
  - test_signal_backward_read_and_failsoft: a real existing §7 + a malformed line + corrupt todo -> parses, skips junk, no raise · covers: M5, R:silent_skip, R:unknown_token_skip
  - test_signal_pure_no_store: state.json byte-identical after _signals; no "signals" key created · covers: M5
  - test_signal_three_trees_identical: _signals byte-identical across the three tooling trees · covers: M6
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: implemented `_signals` after `_seeded_delta_pointers`, reusing the imported delta regexes; competency backward-reading COMPLETED the under-specified contract (open→evidenced already pinned; ADDED folded→resolved, rejected→dropped, and SPEC carried→captured — all within the frozen closed status set, required by M5). SCOPE RESIDUE (declared here, mechanical, zero-behavior): the frozen §3 Scope named 3 add.py trees but an engine edit is 4-way twinned and md5-pinned — I also (a) synced the 4th dogfood twin `./.add/tooling/add.py` and (b) repinned `engine_pin.py` ENGINE_MD5 (764bf47→3eb6dc23) across all 4 tooling trees. Both are mandatory couplings of ANY engine edit that the SOFT Scope line under-declared; test_tree_parity (test_engine_pin_holds + test_engine_files_byte_identical) proves they were required and are now green. → §7 SPEC delta filed.
Code lives in: `add-method/tooling/add.py` plus the three mirror trees (4-way) + engine_pin.py repin
Constraints: do NOT change any test or the frozen §3 contract; stay inside §3 Scope; keep the §3 Regression floor green; `_signals` is pure-read — it must add no state key and write nothing; reuse the existing delta regexes, do not fork the grammar.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all §4 tests pass — including the delta/todo + parity regression floor
- [ ] coverage did not decrease
- [ ] no test or contract altered during build
- [ ] the green was EARNED — test_signal_pure_no_store proves the thin-engine floor (no store) held
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
- [SPEC · open] competency backward-reading: the frozen contract pinned only `competency:open → evidenced`; build completed it with `folded → resolved` and `rejected → dropped` (plus SPEC `carried → captured`) to satisfy M5 over the real corpus — a follow-up should fold these into the signal-model contract text (evidence: test_signal_backward_read_and_failsoft green; _DELTA_RE statuses = open|folded|rejected)
- [SPEC · open] scope-token file-vs-dir under-declaration: a §3 Scope that names `add-method/tooling/add.py` (a FILE) omits the mandatory `engine_pin.py` repin and the 4th dogfood twin `./.add/tooling/add.py` — an engine-editing task should declare the tooling DIR (or an "engine-edit" scope macro) so the repin + 4-way sync are in-scope (evidence: test_tree_parity test_engine_pin_holds required both; recorded as scope residue in §5)

### Competency deltas
- [ADD · open] an engine edit in this repo is a 4-way twin + md5-pin coupling, not a single-file change — the scope-atomicity nudge this milestone will build should itself flag a §3 Scope that names add.py without the tooling dir (evidence: 2 parity reds surfaced only at the gate, not at freeze) (evidence: engine_pin.ENGINE_MD5 repin + REPO/.add twin sync both mandatory)
