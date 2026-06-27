# TASK: Active milestone/task accessor seam; route all call sites

slug: active-accessors · created: 2026-06-22 · stage: mvp · risk: high
autonomy: conservative   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
- `add-method/tooling/add.py` — introduce the accessor SEAM + route every active-milestone/active-task read & write through it. Sites (grounded by grep on the current source):
  - READ active_milestone: 535 (cmd_new_task milestone default) · 1120 / 1148 (cmd_status) · 1868 (cmd_milestone_done) · 2266 (cmd_set_milestone/wave) · 3851 (report rollup) · 4968 (cmd_report drill)
  - READ active_task: 654 (cmd_guide/advance default) · 1097 (status --json) · 1106 (status text) · 1273 / 1293 (report/decide defaults) · 1883 (cmd_milestone_done) · 3800 (report rollup) · ~4964 (cmd_report drill)
  - WRITE active_milestone: 2115 (cmd_new_milestone set) · 2406 (cmd_archive_milestone clear)
  - WRITE active_task: 587 (cmd_new_task) · 2408 (cmd_archive_milestone clear) · 2517 (cmd_use)
  - cmd_check non-JSON branch reads state.json directly (~1773) — the THIRD seam the state-schema-migration review flagged (§7 SPEC delta inbound here): today reads legacy keys only; route its active-task read through the accessor for forward-safety.
- `add-method/tooling/add.py:_migrate_state` (260) — the migration already lands `active_milestones` + `active_tasks` + the scalar mirror; the accessors are the READ/WRITE counterpart over that shape.
- `engine_pin.py:ENGINE_MD5` = `aef59d9ce7482ffa5d1a78f00f6e09bc` — re-pin after this engine edit.

Context (working folder):
- 3 byte-identical add.py copies (tooling · .add/tooling · _bundled) — edit in lockstep + re-pin (engine-edit discipline).
- The full suite (1388) is the regression oracle: routing must keep single-active behavior byte-for-decision identical, so the suite stays green with NO test change.
- The two inbound §7 SPEC deltas from state-schema-migration (this task consumes them): route the cmd_check direct read · default `active_tasks` to `{}` on read (partial-state tolerance).

Honors (patterns / conventions):
- byte-for-decision identity for N≤1 — the read accessor returns exactly today's scalar value; the write accessor keeps the scalar + the new structures in sync. No behavior change in this task (multi-active SEMANTICS land in multi-active-commands).
- design-for-failure — accessors are pure/total, `.get`-defaulted (a missing active_tasks → {} ; a missing active_milestones → []); never raise.
- engine-edit discipline — 3-tree byte-identity + same-commit re-pin.

Anchors the contract cites: the NEW accessors `_active_milestone(state)` · `_active_task(state, milestone=None)` · `_set_active_milestone(state, slug)` · `_set_active_task(state, slug, milestone=None)` · the routed read/write sites · `engine_pin.ENGINE_MD5`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: An accessor SEAM for the active milestone(s)/task — read & write helpers that every engine call site routes through, so multi-active semantics can land later in ONE place. This task changes indirection only: single-active behavior stays byte-for-decision identical.
Framings weighed: thin accessors over the migrated shape (chosen — `_active_milestone`/`_active_task` return today's scalar; `_set_*` keep scalar+structures in sync; the seam is the whole deliverable) · rewrite every reader to iterate the SET now (rejected — that is multi-active-commands' job; doing it here couples two contracts + risks regressions with no command to exercise them) · leave reads on the scalar, wrap only writes (rejected — readers would still need a second edit pass in task 3, defeating the seam).
Must:
<must>
  - NEW read accessors: `_active_milestone(state) -> str|None` returns the primary active milestone (today: the scalar `active_milestone`, == active_milestones[0] for N≤1); `_active_task(state, milestone=None) -> str|None` returns the active task (milestone given → active_tasks[milestone]; else the global scalar `active_task`). Both pure, total, `.get`-defaulted (missing active_tasks → {}), never raise.
  - NEW write accessors: `_set_active_milestone(state, slug)` sets the scalar AND keeps `active_milestones` consistent ([slug] or [] for N≤1); `_set_active_task(state, slug, milestone=None)` sets the scalar AND `active_tasks[primary]` (or clears when slug is None). The scalar mirror is always kept in sync (the not-yet-multi readers still rely on it).
  - EVERY grounded read site (active_milestone ×7, active_task ×8) routes through the read accessor; EVERY write site (active_milestone ×2, active_task ×3) routes through the write accessor; cmd_check's direct active-task read routes through the accessor too (consumes the inbound §7 delta).
  - Byte-for-decision identity: for any state with ≤1 active milestone, every command produces the SAME decision/output as before — proven by the full existing suite (1388) staying green with NO test weakened.
  - Partial-state tolerance: a state with `active_milestones` but no `active_tasks` reads as `{}` (consumes the second inbound §7 delta).
  - All 3 add.py copies byte-identical + ENGINE_MD5 re-pinned in the same change; parity/pin tests green.
</must>
Reject:
<reject>
  - (no new error codes — this is a pure refactor behind a seam; the accessors are total and the routed commands keep their existing reject codes unchanged)
</reject>
After:
<after>
  - Every active-milestone/active-task access in add.py goes through the four accessors; the scalar keys remain the synced N≤1 mirror; the full suite is green with no test change; the 3 copies + pin are green. Multi-active SEMANTICS remain dormant (one active milestone only) until multi-active-commands.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ "primary active milestone" semantics — `_active_milestone` returns the single scalar today, but defining a SINGLE "primary" presupposes one focus even when task 3 allows N. If the eventual multi-active UX needs a per-command milestone argument instead of a global "primary", some readers routed here may need re-routing in task 3. Lowest confidence because the multi-active command UX isn't designed yet; if wrong, a subset of the ~15 read sites get a second touch in multi-active-commands (mechanical, not a data risk). Mitigation: `_active_task` already takes an optional `milestone=` so per-milestone callers exist from day one.
  - [ ] `_set_active_task` writing `active_tasks[primary]` — when there is no active milestone (orphan/global active task), it writes only the scalar and leaves active_tasks untouched (mirrors the migration's orphan rule). Confirm at freeze.
  - [ ] no behavior change is observable — relies on the suite as oracle; a site with subtly different semantics than `.get(scalar)` would surface as a red test. Confirm by the green suite.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: Read accessor returns the primary active milestone
  Given a migrated state with active_milestones=["m1"] and active_milestone="m1"
  When _active_milestone(state) is called
  Then it returns "m1"

Scenario: Read accessor returns the per-milestone active task
  Given a state with active_tasks={"m1":"t1"}
  When _active_task(state, "m1") is called
  Then it returns "t1"
  And _active_task(state) with no milestone returns the global scalar active_task

Scenario: Read accessor tolerates a partial state
  Given a state with active_milestones=["m1"] but no active_tasks key
  When _active_task(state, "m1") is called
  Then it returns None (defaulted, no KeyError)

Scenario: Write accessor keeps scalar and structures in sync
  Given a fresh state
  When _set_active_milestone(state, "m1") then _set_active_task(state, "t1", "m1")
  Then active_milestone=="m1" AND active_milestones==["m1"] AND active_task=="t1" AND active_tasks=={"m1":"t1"}

Scenario: Write accessor clears consistently
  Given a state with m1/t1 active
  When _set_active_task(state, None, "m1")
  Then active_task is None AND active_tasks has no "m1" entry (or maps it to None per the frozen rule)

Scenario: Single-active behavior is byte-for-decision identical
  Given the existing full test suite (the regression oracle)
  When all read/write sites are routed through the accessors
  Then the suite stays green with NO test changed (status/new-task/use/archive/milestone-done/report unchanged)

Scenario: cmd_check's active-task read is routed
  Given cmd_check's non-JSON branch
  When it reads the active task
  Then it goes through _active_task (not a raw state["active_task"]), so the migration/seam covers it

Scenario: The engine edit stays pinned
  Given all three add.py copies are edited
  When the parity + ENGINE_MD5 tests run
  Then the three copies are byte-identical AND match the re-pinned ENGINE_MD5
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
# Accessor seam over the multi-active state (no API; internal helpers in add.py)

_active_milestone(state) -> str | None
  return state.get("active_milestone")            # primary = the N≤1 scalar mirror (== active_milestones[0])

_active_task(state, milestone=None) -> str | None
  if milestone is None: return state.get("active_task")                 # global/primary active task
  return (state.get("active_tasks") or {}).get(milestone)              # per-milestone; partial-state -> None

_set_active_milestone(state, slug) -> None
  state["active_milestone"] = slug
  state["active_milestones"] = [] if slug is None else [slug]          # N≤1 sync (multi-active-commands generalizes)

_set_active_task(state, slug, milestone=None) -> None
  state["active_task"] = slug                                          # scalar mirror always synced
  ms = milestone if milestone is not None else _active_milestone(state)
  tasks_map = state.setdefault("active_tasks", {})
  if ms is None: pass                                                  # orphan/global active task: scalar only (migration's orphan rule)
  elif slug is None: tasks_map.pop(ms, None)                           # clear removes the entry
  else: tasks_map[ms] = slug

Routing (behavior-preserving):
  READ active_milestone (535·1120·1148·1868·2266·3851·4968) -> _active_milestone(state)
  READ active_task     (654·1097·1106·1273·1293·1883·3800·~4964 + cmd_check ~1773) -> _active_task(state)
  WRITE active_milestone (2115 set · 2406 clear) -> _set_active_milestone(state, slug|None)
  WRITE active_task      (587 · 2517 set · 2408 clear) -> _set_active_task(state, slug|None[, ms])
Invariant: for any state with len(active_milestones) <= 1, every routed command's decision/output is
  IDENTICAL to pre-routing (the full suite is the oracle; NO test changed).
Errors: none new. Engine: 3 add.py copies byte-identical + ENGINE_MD5 re-pinned same commit.
```

Status: FROZEN @ v1 — approved by Tin Dang (2026-06-22; auto-mode standing authorization; multi-active foundation 2/5; seam-only refactor, single-active byte-identical, suite is the oracle)
Least-sure flag surfaced at freeze: [contract] "primary active milestone" presupposes a single focus — `_active_milestone` returns the scalar today; if multi-active-commands needs per-command milestone targeting instead of a global primary, a subset of the ~15 routed reads get a second (mechanical) touch in task 3. Mitigated: `_active_task` already accepts `milestone=` so per-milestone callers exist now; cost if wrong is a re-route pass, not data loss. Second flag: [contract] `_set_active_task(slug=None)` clears by popping the milestone entry (not mapping to None) — chosen for a clean map.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the 4 accessors at every branch + the full suite as the regression oracle (single-active identity).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_active_milestone_returns_primary: active_milestone="m1" → _active_milestone==“m1”; None → None
  - test_active_task_per_milestone: active_tasks={"m1":"t1"} → _active_task(state,"m1")=="t1"; _active_task(state)==global scalar
  - test_active_task_partial_state: active_milestones=["m1"], no active_tasks → _active_task(state,"m1") is None (no KeyError)
  - test_set_milestone_syncs_list: _set_active_milestone(state,"m1") → active_milestone=="m1" AND active_milestones==["m1"]; (None) → both empty
  - test_set_task_syncs_map: _set_active_task(state,"t1","m1") → active_task=="t1" AND active_tasks=={"m1":"t1"}
  - test_set_task_clear_pops_entry: from m1/t1, _set_active_task(state,None,"m1") → active_task is None AND "m1" not in active_tasks
  - test_set_task_orphan_scalar_only: with no active milestone, _set_active_task(state,"t9") → active_task=="t9" AND active_tasks=={}
  - test_cmd_check_routes_active_task: cmd_check reads via the accessor (grep/AST assert no raw state["active_task"] left in cmd_check) OR behavior test that a migrated state checks clean
  - (regression) the FULL existing suite stays green with NO test changed — the byte-for-decision-identity oracle
  - test_engine_three_trees_pinned: 3 add.py copies byte-identical AND == engine_pin.ENGINE_MD5
</test_plan>

Tests live in: `add-method/tooling/test_active_accessors.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_active_accessors.py`
Strategy (ordered batches): 1. write `test_active_accessors.py` red (4 accessors + branches). · 2. add the 4 accessors near `_migrate_state` in `add-method/tooling/add.py`; route all read sites then all write sites + cmd_check (smallest behavior-preserving diffs). · 3. run the FULL suite — it must stay green with no test change (the oracle). · 4. mirror byte-identically to the other 2 copies; re-pin ENGINE_MD5; green incl. parity/pin.
Safety rule (feature-specific): each routing edit is behavior-preserving for N≤1 — `_active_milestone` returns exactly `state.get("active_milestone")`, so a routed read must be value-identical. Do NOT change any command's logic, only the access. Diff the 3 copies before re-pinning.
Code lives in: `add-method/tooling/add.py` (+ its two mirror copies)
Constraints: do NOT change any test or the contract; stdlib only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 1398 OK (1388→1398; +10 test_active_accessors); no test changed
- [x] coverage did not decrease — 10 new accessor tests; the 4 helpers covered at every branch
- [x] no test or contract was altered during build — build/verify touched only add.py ×3 + engine_pin.py (all §5-declared); test file written in TESTS
- [x] the green was EARNED, not gamed — the FULL pre-existing suite is the byte-for-decision-identity oracle: 37 pre-mirror failures were ALL pin/parity guards (zero behavioral), every one green after re-pin; an AST routing test asserts cmd_check has no raw active_task access; independent review (below) found zero missed sites / value divergence
- [x] concurrency / timing safe — accessors are pure/synchronous; setdefault returns the live map ref (intended); single-process CLI
- [x] no exposed secrets, injection openings, or unexpected dependencies — pure refactor, stdlib only, no new import
- [x] layering & dependencies follow CONVENTIONS.md — one seam, all sites routed; no command logic changed (only access path)
- [x] a person reviewed and approved the change — Tin Dang, auto-mode standing authorization + an independent python-expert review (MERGE-WITH-NITS, 0 blocking, 0.97)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] Single-active behavior byte-for-decision identical — confirmed: 1388 pre-existing tests green with NO test changed; the only pre-mirror failures were the 3-tree pin guards, all green post-repin
- [x] Every active-milestone/active-task access goes through an accessor — confirmed: AST scan (independent review) found zero raw `state["active_task"]`/`state.get("active_milestone")` outside the 4 accessor bodies + init literal + the schema membership check
- [x] cmd_check's read routed (consumed §7 delta) — confirmed: test_cmd_check_has_no_raw_active_task_read green
- [x] 3 copies byte-identical + ENGINE_MD5 current — confirmed: all three == `5eb79fa818b9c70b9f4eb4289ce70944` == engine_pin.ENGINE_MD5

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — the 4 accessors each have live callers (the routed sites); `_set_active_task` calls `_active_milestone` for default-primary resolution (intended); AST scan confirms no bypass remains
- [x] DEAD-CODE (code) — no orphaned symbol; `_active_task(state, milestone)`'s per-milestone arm is exercised by the archive fix + tests (not dead)
- [ ] SEMANTIC (prose / non-code) — N/A (code change)
- [x] INDEPENDENT REVIEW — python-expert, 5 probes (missed-sites/value-divergence/write-correctness/recursion-aliasing/archive-ordering): **MERGE-WITH-NITS, 0 blocking, 0.97**. Nit 1 (stale active_tasks after archive) FIXED in-verify (clear task before milestone; pin → 5eb79fa8). Nit 2 (cmd_use cross-milestone map entry, PRE-EXISTING) → §7 delta for multi-active-commands.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang (auto-mode standing authorization) · date: 2026-06-22

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · carried] in multi-active-commands, `cmd_use` should record the active task under the task's OWN milestone, not the current primary — `_set_active_task(state, slug)` at the use site writes active_tasks[primary] which can mislabel when the selected task belongs to another active milestone (evidence: independent review nit 2, pre-existing N≤1 oddity made visible by the seam) [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]
- [SPEC · carried] multi-active-commands must filter `active_tasks` against LIVE milestones when reading per-milestone — a stale entry can only arise from edge paths now, but the map should be treated as advisory until task 3 owns its lifecycle (evidence: archive map-hygiene reasoning, this task) [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] a global find-and-replace that routes accessors will also rewrite the accessor's OWN body into self-recursion — introduce the helper, then route, then re-fix the two helper bodies (evidence: the _active_milestone/_active_task RecursionError caught at first test run, this task) [folded foundation-version 41]
