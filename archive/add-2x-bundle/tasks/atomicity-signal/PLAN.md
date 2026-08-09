# PLAN: Atomicity nudge SEEDS a signal at freeze (not an ephemeral print)

slug: atomicity-signal · created: 2026-07-23 · stage: mvp
milestone: signal-graph
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 0 · GROUND — the observed map (anchors opened live 2026-07-23)

- `add-method/tooling/add.py` · `cmd_freeze` (~1065) — after the atomic Status flip + `print("froze §3 …")` (~1201) it runs advisory printers in a fail-open guard: `try: _scope_echo(root, slug) except Exception: pass` (~1202). This IS the seam — a sibling seed call added here fires at the freeze the human already reads, never blocking it, BEFORE the `--cross` branch (~1215) so a bare freeze seeds too.
- `add-method/tooling/add.py` · `cmd_todo` (~2688) — the existing lightweight-backlog store: `state["todos"]` append `{id (max+1), text, created, status:"open"}` + `save_state`. The signal SEED reuses THIS store (an existing store — the thin-engine floor forbids a NEW one, not writing to an old one).
- `add-method/tooling/add.py` · `_signals(root)` (304, FROZEN @ signal-model v1) — reads `state["todos"]`: open→`captured`, done→`resolved`, id `t<n>`, kind `todo`, edges `[]`. So a seeded todo is ALREADY an addressable signal + a `graph --signals` node with ZERO change to the frozen reader.
- `add-method/tooling/add.py` · `_raw_phase_bodies(root, slug)` — section-int→body text; the read primitive `_scope_parts` uses to reach §1/§3.
- The parked `scope-atomicity-guard` (milestone intake-atomicity, FROZEN v1, UNBUILT) designed `_scope_parts` + a PRINTING `_atomicity_nudge`. This task is its change-request: same detector, output print→SEED (the milestone's applied case — the nudge becomes a persistent signal).
- Four tooling trees stay byte-identical + `engine_pin.py` ENGINE_MD5 re-pins (add.py-only → ENGINE_PKG_MD5 holds). Precedent: measure-not-block nudges (`_scope_echo`, persona-seed-nudge) never gate.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: at the §3 contract-freeze, when a task's scope reads as more than one independent Part (a longtail/drain/sweep catch-all), SEED a persistent, addressable signal (a `captured` todo) instead of an ephemeral print — so the atomicity concern survives after the freeze output scrolls away and appears in `graph --signals`. Measure-not-block: the freeze always proceeds.
Framings weighed: seed a todo signal (chosen — todos are the existing lightweight-backlog store `_signals` already reads as `captured`; zero new store, zero change to frozen `_signals`, addressable after freeze) · a §7 delta (rejected — §7 is the observe-phase spec/competency grammar with an evidence tail; an intake-atomicity concern at freeze is the wrong altitude and shape) · print-only, as the parked design (rejected — ephemeral; the milestone's whole point is a persistent navigable node)
Must:
<must>
  - M1 detect multi-Part scope: `_scope_parts(root, slug)` PURE-reads §1/§3 and returns the ordered independent-Part labels; union of numbered-bold (`N. **label**`) ∪ marker (`(N parts)` / `N-part`, N≥2) ∪ catch-all keyword (longtail|drain|sweep|catch-all|grab-bag in slug or title). Returns [] when fewer than 2 Parts (silence = pass).
  - M2 SEED a signal: `_atomicity_signal_seed(root, slug)` with ≥2 Parts appends ONE `captured` todo to `state["todos"]` whose text names the task, the Part count + labels, and the steer; returns the new id. The seeded todo is read by `_signals` as an addressable signal and renders under `graph --signals`.
  - M3 idempotent: a second seed for the same slug (re-freeze / re-cross) adds NO duplicate — an OPEN todo already tagged for this slug short-circuits the append.
  - M4 non-blocking, fail-open: the freeze hook is a pure sibling of `_scope_echo` — it never changes the freeze exit status; a single-Part scope or a malformed/absent §1/§3 seeds nothing and never raises.
  - M5 default unchanged: a single-Part task freeze seeds nothing and its freeze stdout stays byte-identical to today.
  - M6 engine parity: add.py byte-identical 4-way + `engine_pin.py` ENGINE_MD5 re-pinned (ENGINE_PKG_MD5 unchanged — add_engine untouched; `_signals` untouched).
</must>
Reject:
<reject>
  - single-Part or unenumerated scope (a normal atomic task) -> no seed, no print -> "single_none" (silence is the pass)
  - a malformed / missing §1 and §3 -> no seed, no raise -> "silent_absent"
  - a second freeze/seed of an already-seeded slug -> no duplicate todo -> "idempotent_reseed"
</reject>
After:
<after>
  - freezing a task whose scope enumerates two or more Parts leaves a `captured` atomicity signal on the board (visible in `todo`, `_signals`, and `graph --signals`) AND records FROZEN normally
  - freezing a normal single-Part task is byte-unchanged (no seed)
</after>
Boundary: the external input is a task PLAN.md's §1/§3 body text — Part enumeration appears as a numbered-bold list (`N. **label**`), a `(N parts)` / `N-part` marker, or a catch-all keyword in slug/title. Tests must speak all three plus the single-Part negative, and the real freeze command must leave a signal.
<assumptions>
  ⚠ seeding the atomicity concern as a TODO (edgeless captured signal) rather than a signal edged `observed-by` its task is acceptable — if wrong: the atomicity node floats in `graph --signals` without a visible link to the multi-Part task. Mitigated: the seeded text NAMES the slug, and `_signals`'s todo reader (frozen @ signal-model v1) carries no edges — adding an edge would be a change-request to a frozen contract; a follow-up can widen the todo grammar if the floating node proves confusing. Cost if wrong is a text-only readability nit, not a data or store change.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>
  - Given a task whose §3 lists `1. **A**` / `2. **B**` / `3. **C**`, When `_scope_parts` reads it, Then it returns three Part labels; When it is frozen, Then a `captured` atomicity signal exists on the board naming the three Parts.
  - Given a task whose §1/§3 carries a `(4 parts)` marker, When `_scope_parts` reads it, Then ≥2 Parts are detected.
  - Given a task whose slug contains `longtail`, When `_scope_parts` reads it, Then the catch-all keyword fires even with no numbered list.
  - Given a normal atomic task with one contract shape and no enumeration, When frozen, Then no signal is seeded and the freeze stdout is byte-unchanged.
  - Given an already-seeded multi-Part task, When seeded again, Then no duplicate signal appears.
  - Given the board after a seed, When `graph --signals` runs, Then the atomicity signal renders as a node.
</scenarios>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — HARD, tamper-guarded)

```
_scope_parts(root: Path, slug: str) -> list[str]     # PURE read of §1/§3 body
  body = §1 + §3 via _raw_phase_bodies; slugword = slug + task title.
  Part labels (union, order-preserving, deduped):
    numbered-bold   a line matching  ^\s*\d+\.\s+\*\*(.+?)\*\*
    marker          "(N parts)" / "N-part"  with N >= 2  -> N synthetic labels if no bold list
    catch-all kw    slugword matches  longtail|drain|sweep|catch-all|grab-bag
  returns [] when fewer than 2 Parts detected (the silent-pass case).

_atomicity_signal_seed(root: Path, slug: str) -> int | None     # SEEDS, not prints
  parts = _scope_parts(root, slug)
  if len(parts) < 2: return None                     # silence = pass
  tag = f"atomicity: {slug} —"                        # stable per-slug marker
  if any OPEN todo text startswith(tag): return None  # idempotent (M3)
  text = f"{tag} §3 scope reads as {len(parts)} Parts ({', '.join(parts)}); consider new-milestone + one task per Part."
  append {id: max+1, text, created: _now(), status:"open"} to state["todos"]; save_state
  print f"note: seeded atomicity signal #{id} — §3 scope reads as {len(parts)} Parts (addressable after this freeze)"
  return id

cmd_freeze (hook, additive — sibling of the _scope_echo fail-open guard, before --cross):
  try: _atomicity_signal_seed(root, slug)
  except Exception: pass                              # never blocks a freeze
```
Schema: writes ONLY the existing `state["todos"]` store (no new store/table); `_signals` / `_exit_criterion_nodes` / add_engine untouched (ENGINE_PKG_MD5 stable). Pure read for `_scope_parts`.

Target (measurable): `_scope_parts` returns ≥2 labels for a numbered-bold / marker / catch-all fixture and [] for a single-Part task; `_atomicity_signal_seed` appends exactly one `captured`-reading todo (idempotent on re-call), visible via `_signals` + `graph --signals`; a REAL `freeze` of a multi-Part task leaves a signal asserted after the call; a single-Part freeze seeds nothing + stdout byte-identical; `test_atomicity_*` green; freeze + signal-model + graph regression floor green; add.py 4-way identical, ENGINE_PKG_MD5 unchanged.
Least-sure flag surfaced at freeze: [contract] seeding the atomicity concern as an edgeless `captured` TODO (not a signal edged `observed-by` its task) — chosen because `_signals`'s todo reader is frozen @ signal-model v1 and carries no edges, and the todo store is the purpose-built lightweight-backlog home the reader already projects; the seeded text names the slug so the link is legible in prose. Adding a real edge is a change-request to the frozen `_signals`, deferrable at zero cost. This closes the milestone (the applied case of note=todo=delta=nudge as ONE signal).
Status: FROZEN @ v1 — approved by Tin Dang
Reported: no

### Build-strategy (SOFT: preferred; the builder self-improves and records actual at verify)
Scope (may touch): `add-method/tooling/` `add-method/.add/tooling/` `add-method/src/add_method/_bundled/tooling/` `.add/tooling/` `./tests/`
Regression floor: the freeze suite(s) (`test_freeze_command`, `test_unflagged_freeze`) + `test_signal_model` + `test_graph_view_signals` + tree parity + engine pin — run green before the gate.
Persona (required): `.add/personas/methodology-engine-dev.md` (deterministic, fail-loud engine work; advisory, never lowers a gate)

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_scope_parts_numbered_bold: §3 with `1. **A**` / `2. **B**` / `3. **C**` -> 3 Part labels · covers: M1
  - test_scope_parts_marker: `(4 parts)` marker with no bold list -> >=2 Parts · covers: M1
  - test_scope_parts_catchall_keyword: slug carrying `longtail` -> Parts via keyword, no numbered list · covers: M1
  - test_scope_parts_single_none: a normal one-Part task -> [] · covers: M1, R:single_none
  - test_seed_appends_captured_signal: _atomicity_signal_seed on a multi-Part task adds one todo read by _signals as kind=todo status=captured · covers: M2
  - test_seed_idempotent: two seeds of the same slug -> one todo only · covers: M3, R:idempotent_reseed
  - test_seed_in_graph_signals: after a seed, `graph --signals` renders the atomicity signal node · covers: M2
  - test_freeze_multipart_leaves_signal: the REAL `freeze` command on a multi-Part task leaves an addressable signal (asserted after the freeze call) · covers: M2, M4
  - test_freeze_single_part_no_seed: a single-Part task freeze seeds nothing (no atomicity todo) · covers: M5, R:single_none
  - test_seed_fail_open_absent: a slug with no §1/§3 body -> seed returns None, no raise · covers: M4, R:silent_absent
  - test_three_trees_identical: add.py byte-identical across the tooling trees · covers: M6
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned — added `_scope_parts(root, slug)` (numbered-bold ∪ `(N parts)` marker ∪ catch-all keyword over §1+§3 body + slug/title) and `_atomicity_signal_seed(root, slug)` (idempotent-per-slug append to the existing `state["todos"]` store, read straight back by frozen `_signals` as a `captured` todo signal) beside `_exit_criterion_nodes`; wired the seed as a fail-open sibling of `_scope_echo` in cmd_freeze (before the `--cross` branch, so a bare freeze seeds too). NO new store, `_signals` + add_engine untouched (ENGINE_PKG_MD5 held 81553881); ENGINE_MD5 repinned ed8624a2→e7ad9f97 + 4-way sync. Scope declared the tooling DIRS up front — NO return-to-build. Test-harness fix during direction (pre-freeze): freeze slug is positional, not `--slug`. Dogfood: atomicity-signal's OWN §3 reads as [] (atomic — no self-seed).
Code lives in: `add-method/tooling/` (add.py + engine_pin.py, 4-way; add_engine + _signals untouched)
Constraints: do NOT change any test or the frozen §3 contract; do NOT edit add_engine or `_signals` (keep ENGINE_PKG_MD5 + the signal-model v1 contract); stay inside §3 Scope; keep single-Part freeze stdout byte-identical; repin ENGINE_MD5 + sync 4-way.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all §4 tests pass — including freeze + signal-model + graph + parity + pin floor
- [ ] coverage did not decrease
- [ ] no test or contract altered during build
- [ ] the green was EARNED — test_freeze_single_part_no_seed proves the default freeze held
- [ ] the seed writes ONLY state["todos"] (no new store) — ENGINE_PKG_MD5 unchanged, _signals untouched
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
- [SPEC · open] the seeded atomicity signal is an edgeless `captured` todo (no `observed-by` edge to its multi-Part task) because `_signals`'s todo reader is frozen @ signal-model v1; a follow-up change-request could widen the todo grammar to carry an edge if the floating node reads as disconnected (evidence: test_seed_in_graph_signals green — the node renders, its text names the slug, but no edge line)
- [SPEC · open] the parked `scope-atomicity-guard` (intake-atomicity, print-only) is now SUPERSEDED by this seed-based design; its release step ("rebuild scope-atomicity-guard on the new signal primitive") is satisfied — the parked frozen task can be closed/archived as delivered-by atomicity-signal (evidence: `_scope_parts` + the freeze hook shipped here cover its full frozen §3)

### Competency deltas
- [ADD · open] "no new store" ≠ "no writes" — seeding into the EXISTING `state["todos"]` store honored the thin-engine floor while making the nudge persistent+addressable; the store choice (todo vs §7 delta) followed altitude (an intake-time backlog jot IS a todo) (evidence: test_seed_appends_captured_signal green, ENGINE_PKG_MD5 unchanged, no new state key)
- [ADD · open] a self-referential engine feature must be dogfood-checked against ITSELF at freeze — verified atomicity-signal's own §3 reads as [] before freezing so the new hook wouldn't spuriously self-seed (evidence: `_scope_parts('.add','atomicity-signal') == []`; freeze emitted no seed note)
- [ADD · open] declaring the tooling DIRS in §3 Scope up front (signal-model lesson) again gave a first-pass gate — engine_pin repin + 4-way sync in-scope, no return-to-build (evidence: freeze scope-echo all [ok], check 452/0)
