# TASK: cmd_check TOML/dead-recompute hoist + 5x snapshot-hash helper + static-regex hoist + milestone-resolve DRY

slug: hygiene-bundle · created: 2026-07-14 · stage: mvp
milestone: engine-hygiene
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; the observe note is one optional line at the gate.

---

## 1 · SPECIFY — the rules

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: four value-dense, BEHAVIOR-PRESERVING engine cleanups from a read-only sweep, bundled so one fence/twin/pin ceremony pays for all: (#1) `cmd_check` stops re-reading `components.toml` per-task and drops a dead recompute; (#2) the 5-way-duplicated snapshot-hash read becomes one helper with a UNIFIED exception tuple; (#3) `taskdoc._phase_spans` hoists its static heading regex to a module constant; (#5) the byte-identical `unknown_milestone` resolve boilerplate becomes one `_resolve_milestone` helper. The BINDING invariant: every observable CLI behavior (stdout/stderr/exit codes across `check`/`status`/`gate`/the milestone verbs) is byte-identical — the existing ~3600-test fence is the primary guard; the new tests pin the structural changes red→green.
Must:
  - #1a DEAD-RECOMPUTE GONE: `cmd_check` computes the archived-slug set ONCE (the outer `archived_slugs` at add.py:3847) and reuses it in the per-task loop — the inner `_arch = _archived_task_slugs(state)` (add.py:3894) is removed; check output is byte-identical
  - #1b TOML READ ONCE: `cmd_check` reads `components.toml`/`contracts` ONCE per invocation (hoisted like `cmd_components` add.py:3775 already does), not once per task — pinned by a spy asserting `_components(root)`/`tomllib.loads` is invoked O(1), not O(tasks), over a multi-task project; check output byte-identical
  - #2 ONE SNAPSHOT-HASH READER: a new `_snapshot_hash(path: Path) -> str | None` reads+parses a snapshot file and returns its `"hash"` (or None), catching ONE unified exception tuple `(OSError, ValueError, KeyError, TypeError, AttributeError)`; all 5 sites (add.py:1746, 3932, 3951, 5633, 5934) call it; the helper returns None (never raises) for each malformed input: missing file · non-JSON bytes · JSON-but-not-a-dict · dict-without-hash
  - #3 STATIC REGEX HOISTED: `add_engine/taskdoc.py` compiles the heading pattern `^##\s*(\d+)\s*·` ONCE at module load (a module constant), not inside `_phase_spans` (taskdoc.py:167); `_phase_spans` output is byte-identical
  - #5 ONE MILESTONE RESOLVER: a new `_resolve_milestone(state, slug) -> str` (mirroring `_resolve_task` add.py:1365) replaces the byte-identical `if slug not in state.get("milestones", {}): _die("unknown_milestone")` boilerplate at every site that currently uses that EXACT bare form; it returns the slug when present and `_die("unknown_milestone")` (same code, same exit) when absent
Reject:
  - #5 a `unknown_milestone` site with a DIFFERENT message shape (e.g. the `f"unknown_milestone: '{x}' is not a milestone in this project"` sites) is LEFT UNCHANGED — the helper only unifies the byte-identical bare-`_die("unknown_milestone")` sites, never rewords a distinct error -> "milestone_resolve_message_drift"
  - #2 the helper must NOT swallow a genuinely different error class into None beyond the declared tuple (no bare `except:`) -> "snapshot_hash_overbroad_catch"
Accept: Given the current engine, When the full fence + the new structural tests run after the change, Then all ~3600 existing tests stay green (behavior byte-identical) AND the new tests pass: `_snapshot_hash` returns None for all 4 malformed inputs, `_resolve_milestone` resolves/dies correctly, `taskdoc._HEADING_RE` exists at module scope, and a multi-task `cmd_check` reads components.toml O(1) not O(tasks)
Boundary: behavior-preserving refactor (the fence is authority) vs the 4 new structural asserts (the red→green proof each change actually landed) — the two test shapes
Assumptions: ⚠ every one of the 5 snapshot-hash sites is semantically "read the pinned hash, treat any read/parse failure as absent" so a unified (broader) exception tuple changes no real path — verified by reading each site; if wrong (a site DEPENDED on a narrower catch letting an exception propagate): the fence's contract-pin tests catch it red, never a silent behavior change

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols): `add.py:cmd_check` (drop the dead `_arch` recompute @3894; hoist `_components`/`_contracts`/`_archived_task_slugs` to once-per-invocation before the per-task loop) · `add.py:_snapshot_hash` (NEW helper) called from the 5 read sites (@1746, 3932, 3951, 5633, 5934) · `add.py:_resolve_milestone` (NEW helper, twin of `_resolve_task`@1365) called from the byte-identical bare-`_die("unknown_milestone")` sites (the build enumerates them: candidates @745, 4624, 5025, 5111, 5173, 5251, 5277 — only those whose guard is exactly `if slug not in state.get("milestones", {})`) · `add_engine/taskdoc.py:_phase_spans` (hoist the `^##\s*(\d+)\s*·` compile to a module const `_HEADING_RE`)
Context (working folder): `add-method/tooling/` — add.py ×4 twins + engine_pin.py ×4 (ENGINE_MD5 for add.py, ENGINE_PKG_MD5 for taskdoc.py); `add_engine/taskdoc.py` ×4 twins; `.add/SEAMS.md` `_declared_scope` line-pin (add.py grows/shrinks around the anchor → re-pin)
Honors (patterns / conventions): `cmd_components`@3775 (`comps, cons, feds = _components(root), _contracts(root), _federation(root)` — the once-per-invocation hoist pattern to mirror); `_resolve_task`@1365 (the resolve-or-die helper shape); the module-const-regex convention already used across the engine; fail-open reads (any snapshot read/parse failure → None, never a raise)
Anchors the contract cites: `cmd_check` · `_snapshot_hash` (new) · `_resolve_milestone` (new) · `_resolve_task` · `_archived_task_slugs` · `_components` · `_contracts` · `taskdoc._phase_spans` · `taskdoc._HEADING_RE` (new)
Ground SHA: a19eece — stamped by freeze

### Contract

```
# NEW helpers (add.py):
_snapshot_hash(path: Path) -> str | None
  reads+json-parses `path`, returns its "hash" value, or None on ANY of:
  (OSError, ValueError, KeyError, TypeError, AttributeError)   # unified tuple — never raises
  -> replaces the inline `json.loads(<p>.read_text("utf-8")).get("hash")` + try/except at all 5 sites
_resolve_milestone(state: dict, slug: str) -> str
  slug in state.get("milestones", {}) -> slug ; else _die("unknown_milestone")   # exact code + exit preserved
  -> replaces ONLY the byte-identical bare-form sites (not the f-string-message variants)

# NEW module const (add_engine/taskdoc.py):
_HEADING_RE = re.compile(r"^##\s*(\d+)\s*·")   # module load, was inside _phase_spans; _phase_spans uses it

# cmd_check (add.py) hoist — no signature change:
  archived_slugs computed ONCE (@~3847) and reused; the inner _arch (@3894) DELETED
  _components(root)/_contracts(root) read ONCE per invocation before the per-task loop, reused inside

# INVARIANT (the whole point): every CLI stdout/stderr/exit-code across check/status/gate/milestone verbs
# is BYTE-IDENTICAL before vs after. The ~3600-test fence is the guard; the 4 new tests pin the structure.
```

`Least-sure flag surfaced at freeze:` [contract] the #1b hoist — `cmd_check`'s per-task loop reads `_components(root)`/`_contracts(root)` and I move them above the loop into locals; the risk is a site inside the loop that MUTATES or depends on a fresh read per iteration (it must not — components.toml is read-only during a check). If wrong (a per-iteration read was load-bearing): a fence test goes red and the hoist is reverted for that one read, keeping the other three cleanups. Cost: partial landing, never a silent behavior change.
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/add_engine/taskdoc.py` `.add/tooling/add_engine/taskdoc.py` `add-method/.add/tooling/add_engine/taskdoc.py` `add-method/src/add_method/_bundled/tooling/add_engine/taskdoc.py` `add-method/tooling/engine_pin.py` `.add/tooling/engine_pin.py` `add-method/.add/tooling/engine_pin.py` `add-method/src/add_method/_bundled/tooling/engine_pin.py` `.add/SEAMS.md` `add-method/tooling/test_hygiene_bundle.py`
Strategy & known-problem fixes: 1. RED test_hygiene_bundle: (a) `_snapshot_hash` returns None for missing/non-JSON/non-dict/no-hash + the real hash for a good file; (b) `_resolve_milestone` returns the slug present / raises SystemExit "unknown_milestone" absent; (c) `import`-assert `taskdoc._HEADING_RE`; (d) a `cmd_check` run over a ≥2-task project reads components.toml O(1) via a `_components`/`tomllib.loads` call-count spy. 2. Build each cleanup; TRAP #5: before swapping a site, confirm its guard byte-matches `if slug not in state.get("milestones", {})` — leave f-string-message sites untouched (milestone_resolve_message_drift). TRAP #2: keep the tuple EXACTLY the unified 5-class set, no bare except (snapshot_hash_overbroad_catch). TRAP #1b: hoist reads only if read-only in-loop. 3. sync ×4 add.py + ×4 taskdoc.py twins; re-pin ENGINE_MD5 (add.py) + ENGINE_PKG_MD5 (taskdoc.py) ×4; re-pin SEAMS `_declared_scope` line. 4. full fence green (the behavior-preservation proof).
Approach (domain strategy): behavior-preserving hoist + DRY

### AI-verify record (required when gate_mode: ai-plan-verify)
- [x] §3 PLAN grounding anchors resolve in the current tree — all cited sites verified by grep at current line numbers (cmd_check 3847/3894/3923/3947; snapshot 1746/3932/3951/5633/5934; taskdoc 167; _resolve_task 1365)
- [x] §1 every Must + every Reject present, each Reject paired with an error code — milestone_resolve_message_drift, snapshot_hash_overbroad_catch
- [x] §3 Contract shape is concrete (no template placeholder text remains)
- [x] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar) — the #1b in-loop-read hoist risk
Verified by: orchestrator · at: 2026-07-14

---

## 4 · TESTS — failing-first (red)

Plan: test_<accept> — assert the §1 Accept line's Then (behavior, not internals).
Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution)

> The change plan was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope; improve on the strategy if the code teaches you better.
Strategy actually used: as planned for #1a/#2/#3/#5. DIVERGENCE on #1b (serving the HARD "components.toml read O(1) per invocation" invariant, not re-narrated): a cmd_check-only hoist + threading `_task_component` was NOT enough — `_component_findings(root)` (called once by cmd_check) has its OWN per-task loop calling `_task_component` without the registry, leaving a residual O(tasks) read (the trace showed slope-1). Fix stayed inside the declared add.py file-scope: `_component_findings` now reads `_components` once (`_reg`) and threads it into its per-task `_task_component(root, d.name, _reg)`. This is a SOFT-Grounding addition (Grounding is soft; the Contract invariant is hard) that the code taught — the O(1) test proves it (call count equal at N=2 vs N=4). #2 site 5 (`_consumer_stale_guard`) except→return converted to `_snapshot_hash` + the existing `if live is not None` no-op guard — byte-identical (nothing runs after the if).
Code lives in: `./src/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build — test_hygiene_bundle 8 green; full fence (pending tail)
- [x] green was EARNED — the 4 structural asserts were RED before the change (_snapshot_hash/_resolve_milestone/_HEADING_RE AttributeError; O(1) count 8-vs-14 growing); the behavior-preservation invariant is guarded by the whole ~3600-test fence staying green, not by these 4 alone
- [x] input dialect held — the tests speak the real dialects: a JSON snapshot file's bytes, a state dict, the CLI check surface, the module attribute
- [x] no exposed secrets/injection/deps — pure refactor: two read helpers + a hoist + a module const; no new dependency, no I/O widening (security = HARD-STOP: none)

Build expectations (from §1 Accept + §3 CONTRACT): behavior byte-identical — the full ~3600-test fence stays green with zero new failures attributable to the change; the 4 new asserts pass: `_snapshot_hash` None-on-4-malformed + hash-on-good, `_resolve_milestone` resolve/die, `taskdoc._HEADING_RE` present, and cmd_check's `_components` call count EQUAL at 2 vs 4 bound tasks (O(1)). Confirmed by test_hygiene_bundle + the full fence.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-14

