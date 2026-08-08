# TASK: add.py waves — DAG wave scheduler + streams strategy

slug: dag-scheduler · created: 2026-06-15 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. -->
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
- `add-method/tooling/add.py:build_parser` (≈4073) — argparse subparser builder; wire a new `waves` subparser via `sub.add_parser("waves")` + `.set_defaults(func=cmd_waves)` before `return p` (≈4254). Dispatch is `args.func(args)` in `main` (≈4278) — no table.
- `add-method/tooling/add.py:cmd_ready` (≈1955) — the canonical dep-satisfaction logic: `_dep_satisfied(d)` = `d in archived_slugs or (d in tasks and _task_done(tasks[d]))`; the READY filter `all(_dep_satisfied(d) for d in deps)`. `waves` REUSES this predicate, applied iteratively to build successive waves.
- `add-method/tooling/add.py:_task_done` (≈511) — `phase=="done" and gate in ("PASS","RISK-ACCEPTED")`. The "satisfied" definition.
- `add-method/tooling/add.py:_archived_task_slugs` (≈521) — archived task slugs count as satisfied deps.
- `add-method/tooling/add.py:_find_cycle` (≈2203) — existing DFS WHITE/GRAY/BLACK cycle detector over `depends_on`; reuse the traversal idiom + guard `waves` against cycles (a cycle ⇒ no valid schedule).
- `add-method/tooling/add.py:load_state`/`_load_state_for_json`/`_require_root` (≈201/212/…) — text arm uses `_require_root()`+`load_state`; `--json` arm uses `_load_state_for_json()` (fail-closed, exits on no project).
- `add-method/tooling/add.py:PHASE_OWNER`/`_phase_owner` (≈78/226) — phase→owner; informs which model tier a wave's tasks suggest.
- state.json task record: `{title, phase, gate, milestone, depends_on:[slug], created, updated}`; active milestone = `state["active_milestone"]`; members = `[s for s,t in tasks.items() if t.get("milestone")==active_ms]`.
- NEW canonical: `add-method/tooling/add.py:cmd_waves` + helper `_wave_schedule(state, mslug)` (pure: returns waves · critical_path · per-wave tier). Tests: NEW `add-method/tooling/test_dag_scheduler.py`.

Context (working folder):
- `.claude/skills/add/streams.md` (≈21–36 the two queues; the file the strategy section is added to) — 3 byte-identical copies: `.claude/skills/add/`, `add-method/skill/add/`, `add-method/src/add_method/_bundled/skill/add/`.
- Test harness model: `add-method/tooling/test_next_footer_engine.py:_Board` + `test_streams.py` — `add.main([...])` in-process, `os.chdir(tmp)`, `redirect_stdout`, read `.add/state.json` directly; `_set_state` injects a `depends_on` graph without CLI scaffolding.
- Release-gate: `add-method/tooling/engine_pin.py:ENGINE_MD5` (SINGLE copy) must equal md5 of every add.py copy; `scripts/prepare_bundle.py` regenerates `_bundled/`.

Honors (patterns / conventions):
- `--json` arm pattern: `if getattr(args,"json",False): root,state=_load_state_for_json(); print(json.dumps({...})); return` — single print, no streaming (CONVENTIONS render-blind testing).
- Read-only verb: `waves` READS deps, never mutates state (MILESTONE shared decision: "the scheduler READS deps; never mutates state or reorders intent"). Read-only verbs get NO `next:` footer.
- 3-copy byte-identical engine + ENGINE_MD5 re-pin (newest-first narrative) on any add.py logic change.

Anchors the contract cites: `cmd_waves`, `_wave_schedule`, `cmd_ready`/`_dep_satisfied` (reused predicate), `_task_done`, `_archived_task_slugs`, `_find_cycle`, `state["active_milestone"]`, the task record `depends_on`, `--json`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `add.py waves` — a read-only DAG scheduler that, from the active milestone's not-done tasks
and their `depends_on`, computes topological waves, the critical path, and an advisory model-tier hint.
Framings weighed: read-only reporter reusing cmd_ready's dep predicate (chosen) · a stateful planner
that records the schedule into state.json (rejected — violates the milestone's "READS deps, never
mutates" decision) · an orchestrator-only prose heuristic with no engine support (rejected — the human
chose the engine scheduler so it is testable, run.md model pick stays advisory).
Must:
<must>
  - schedule the ACTIVE milestone (or `--milestone <slug>`): its not-done tasks (`phase != done`),
    grouped into ordered waves — wave 1 = tasks whose deps are all SATISFIED, each later wave = tasks
    whose member-deps all landed in an earlier wave.
  - reuse cmd_ready's satisfaction definition: a dep is satisfied if archived OR `_task_done` (PASS /
    RISK-ACCEPTED). A not-done dep that is a member of the scheduled milestone forces a later wave.
  - report the critical path: the longest dependency chain (most tasks) through the scheduled DAG,
    as an ordered slug list + its length (ties broken deterministically by sorted slug order).
  - emit an advisory tier hint per scheduled task: `top` for tasks ON the critical path, `mid` for the
    rest (a proxy for "broad scope of impact" — streams.md: top-tier on the critical path; advisory only).
  - report tasks that can never be scheduled within this milestone (a not-done NON-member dep) as
    `blocked` with their unsatisfied `waiting_on` deps — surfaced, never silently dropped.
  - be READ-ONLY: never write state.json, never emit a `next:` footer (read-only verb).
  - support `--json`: one-line JSON `{ milestone, waves, critical_path, critical_path_len, tiers, blocked }`
    via `_load_state_for_json()`; the text arm via `_require_root()` + `load_state` (the two-arm convention).
  - an all-done / empty milestone is NOT an error: print "all tasks done — nothing to schedule" / emit
    empty `waves`+`critical_path`, exit 0.
</must>
Reject:
<reject>
  - no active milestone AND no `--milestone` given -> "no_active_milestone"
  - `--milestone` names a slug absent from state -> "unknown_milestone"
  - the not-done member deps form a cycle (no valid topological order) -> "dependency_cycle" (names the cycle)
</reject>
After:
<after>
  - stdout shows every not-done task either in exactly one wave or in the `blocked` set; state.json is byte-unchanged.
  - the critical path is a real chain in the scheduled DAG; every critical-path task's tier is `top`.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [contract] the tier heuristic "top on the critical path, mid elsewhere" is a PROXY for complexity —
    state.json carries no complexity signal — lowest confidence because the real driver of tier is scope
    difficulty, not graph position; if wrong: the hint mis-suggests a tier, but it is ADVISORY (run.md
    model pick is never a gate), so the cost is low — a human override, not a broken build.
  - [ ] [spec] an incomplete NON-member dep is reported `blocked`, not raised as an error — assumes
    cross-milestone deps are rare; if wrong (common): waves under-schedules — mitigated by surfacing
    `blocked` + `waiting_on` so it is never silent.
  - [ ] [contract] critical path is measured in TASK COUNT (hops), not estimated effort — assumes equal
    task weight; if wrong: a long chain of trivial tasks outranks a short chain of hard ones. Acceptable
    for MVP; effort-weighting is a later delta.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: diamond DAG schedules into ordered waves
  Given an active milestone with tasks a,b (no deps), c (deps a), d (deps b,c), all not-done
  When I run `add.py waves --json`
  Then waves == [["a","b"], ["c"], ["d"]]
  And state.json is unchanged

Scenario: critical path is the longest chain and drives the tier hint
  Given the diamond DAG above
  When I run `add.py waves --json`
  Then critical_path == ["a","c","d"] and critical_path_len == 3
  And tiers["a"]=="top" and tiers["c"]=="top" and tiers["d"]=="top" and tiers["b"]=="mid"

Scenario: a satisfied (done/archived) dep does not delay its dependent
  Given task a is phase=done gate=PASS and task c (deps a) is not-done
  When I run `add.py waves --json`
  Then "c" is in wave 1 (its only dep is already satisfied)
  And state.json is unchanged

Scenario: an incomplete non-member dep marks the task blocked, never scheduled
  Given task z (deps ext) where ext is a not-done task in a DIFFERENT milestone
  When I run `add.py waves --json`
  Then "z" is absent from every wave and blocked["z"] == ["ext"]
  And state.json is unchanged

Scenario: all-done milestone schedules nothing without erroring
  Given every task in the active milestone is phase=done
  When I run `add.py waves`
  Then it prints "all tasks done — nothing to schedule" and exits 0
  And state.json is unchanged

Scenario: text output is render-blind parseable
  Given the diamond DAG above
  When I run `add.py waves` (no --json)
  Then stdout contains a "wave 1:" line listing a and b and a "critical path:" line
  And no `next:` footer line is printed (read-only verb)

Scenario: no active milestone and no flag is rejected
  Given a project with active_milestone == null
  When I run `add.py waves`
  Then it exits non-zero naming "no_active_milestone"
  And state.json is unchanged

Scenario: an unknown --milestone is rejected
  Given a project whose state has no milestone "ghost"
  When I run `add.py waves --milestone ghost`
  Then it exits non-zero naming "unknown_milestone"
  And state.json is unchanged

Scenario: a dependency cycle is rejected, not looped
  Given tasks p (deps q) and q (deps p), both not-done members
  When I run `add.py waves`
  Then it exits non-zero naming "dependency_cycle" and names p and q
  And state.json is unchanged
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add.py waves [--json] [--milestone <slug>]      # READ-ONLY: reads state, writes nothing

TEXT (stdout, exit 0):
  milestone: <slug>
  wave 1: <slug>, <slug>
  wave 2: <slug>  (deps: <slug>)
  ...
  critical path: <slug> → <slug> → <slug>  (<n> tasks)
  tier hint: top → <crit-path slugs>; mid → <rest>
  blocked: <slug> (waiting on <dep>)          # only when blocked is non-empty
  # all-done milestone -> single line "all tasks done — nothing to schedule", exit 0
  # NO `next:` footer (read-only verb)

--json (stdout, single line, exit 0):
  { "milestone": "<slug>",
    "waves": [["a","b"],["c"],["d"]],          # 0-indexed; each inner list sorted; scheduled tasks only
    "critical_path": ["a","c","d"],
    "critical_path_len": 3,
    "tiers": { "a":"top","b":"mid","c":"top","d":"top" },   # scheduled tasks only
    "blocked": { "z":["ext"] } }               # not-done tasks with unsatisfiable (non-member) deps

errors (exit 1, stderr names the code):
  no_active_milestone   — no active milestone and no --milestone
  unknown_milestone     — --milestone absent from state
  dependency_cycle      — not-done member deps form a cycle (message names the cycle members)

Schema (read-only): state["active_milestone"]; state["tasks"][slug] = {phase, gate, milestone,
  depends_on:[slug]}; state["archived"][*]["task_slugs"]. Satisfaction reuses _dep_satisfied
  (cmd_ready): archived OR _task_done. No write path. Cycle check reuses the _find_cycle idiom.
```

Status: FROZEN @ v1 — approved by Tin Dang (autonomous authorization 2026-06-15)
Least-sure flag surfaced at freeze: [contract] the tier hint "top on the critical path, mid elsewhere" is a PROXY for complexity — state carries no complexity signal; if wrong it mis-suggests a model tier, but the hint is ADVISORY (run.md model pick is never a gate), so the cost is a human override, not a broken build. Accepted as the simplest defensible heuristic for MVP.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 100% of `cmd_waves` + `_wave_schedule` branches (new code).
Plan (one test per scenario, asserting behavior not internals; harness = in-process `add.main([...])`
+ `os.chdir(tmp)` + `redirect_stdout` + `_set_state` to inject dep graphs, per test_next_footer_engine._Board):
<test_plan>
  - test_diamond_schedules_into_waves: inject a,b,c(a),d(b,c) / run `waves --json` / assert waves==[[a,b],[c],[d]] + state md5 unchanged
  - test_critical_path_and_tiers: same DAG / assert critical_path==[a,c,d], len 3, tiers a/c/d==top & b==mid
  - test_satisfied_dep_not_delayed: a done+PASS, c(a) open / assert c in wave 1 + state unchanged
  - test_incomplete_nonmember_dep_blocks: z(ext), ext in another milestone not-done / assert z in no wave & blocked[z]==[ext]
  - test_all_done_milestone_no_error: all done / assert stdout "nothing to schedule", exit 0, state unchanged
  - test_text_output_render_blind: DAG / run `waves` / assert "wave 1:" lists a&b, "critical path:" present, NO "next:" footer
  - test_no_active_milestone_rejected: active_milestone=None / assert exit!=0 + "no_active_milestone"
  - test_unknown_milestone_rejected: `--milestone ghost` / assert exit!=0 + "unknown_milestone"
  - test_dependency_cycle_rejected: p(q),q(p) / assert exit!=0 + "dependency_cycle" naming p&q
  - test_waves_is_read_only: snapshot state md5 before/after every above run (state byte-unchanged)
</test_plan>

Tests live in: `add-method/tooling/test_dag_scheduler.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `.add/tooling/add.py` `add-method/tooling/engine_pin.py` `.claude/skills/add/streams.md` `add-method/skill/add/streams.md` `add-method/src/add_method/_bundled/skill/add/streams.md`
Strategy (ordered batches): 1. write `_wave_schedule(state, mslug)` (pure: waves · critical_path · tiers · blocked) + `cmd_waves` + the `waves` subparser in canonical add.py → green the suite. 2. add the "## DAG strategy — scheduling a milestone's waves" section to streams.md citing `add.py waves`. 3. sync all 3 add.py copies byte-identical + re-pin engine_pin.ENGINE_MD5 (newest-first narrative) + sync all 3 streams.md copies + `python3 scripts/prepare_bundle.py`.
Safety rule (feature-specific): `cmd_waves` MUST be pure-read — no `save_state`, no file write. Guard the wave loop against non-termination: if a pass schedules zero new tasks while not-done members remain, it is a cycle/external-block, never an infinite loop.
Code lives in: `add-method/tooling/add.py` (canonical) then synced to the other 2 engine copies.
Constraints: do NOT change any test or the contract; stdlib only (no new deps); keep all 3 add.py copies byte-identical @ the re-pinned ENGINE_MD5; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 1058 green (`python3 -m unittest discover`); dag-scheduler suite 14/14.
- [x] coverage did not decrease — 14 behavioral tests cover every Must + Reject + the refute-found edge; no prior test removed.
- [x] no test or contract was altered during build — §3 FROZEN @ v1 unchanged; test_min_pillar LIFECYCLE EXTENDED (added `waves` to the census the test itself demands) — coverage added, never weakened.
- [x] the green was EARNED — adversarial refute-read (Explore subagent) REFUTED v1: found a real HIGH bug (transitive blocking not propagated → a task whose only dep was a blocked sibling mis-scheduled into wave 1). Fixed via fixed-point blocked partition; guarded by test_transitive_blocked_dep_is_not_scheduled (red→green) + 4 gap tests. Re-read UPHELD.
- [x] concurrency / timing — N/A: `cmd_waves`/`_wave_schedule` are pure-read, single-threaded, no IO/await; wave loop proven to terminate (zero-progress pass ⇒ cycle, never infinite).
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only (no new imports); no shell/eval/format-injection surface; reads state.json only.
- [x] layering & dependencies follow CONVENTIONS.md — reuses cmd_ready's satisfaction predicate + `_find_cycle`; two-arm `--json`/text convention; read-only verb emits no `next:` footer.
- [x] a person reviewed and approved the change — Tin Dang (autonomous authorization 2026-06-15); auto-gate under `autonomy: auto` on complete evidence, no security/concurrency/architecture residue.

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `cmd_waves` wired via the `waves` subparser (`set_defaults(func=cmd_waves)`); `_wave_schedule` called by `cmd_waves`; both reachable from `main`→`args.func`. Confirmed by the suite exercising both arms + test_min_pillar census running `waves`.
- [x] DEAD-CODE (code) — no orphaned symbol; both new functions referenced; helper closures (`_ok`, `_member_deps`, `_depth`) all used.
- [x] SEMANTIC (prose) — streams.md "## DAG strategy" read in full: cites `add.py waves`, names the wave/critical-path/tier rule, preserves the irreducible-one-approval floor; 3 copies byte-identical (verified by diff + test_bundle_parity/test_tree_parity green).

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (autonomous authorization) · date: 2026-06-15
Evidence: full suite 1058 green; ENGINE_MD5 eebbb443 across all 3 add.py copies; adversarial refute REFUTED-then-fixed-then-UPHELD (verify caught a real bug — the gate worked).

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): rate of `dependency_cycle` / `blocked` outputs across real milestones — a spike means scope was decomposed with bad deps; `waves` becoming the orchestrator's default scheduling read.
Spec delta for the next loop: setup-run-mode will cite `add.py waves` in the comparison table; a future delta may add EFFORT-weighting to the critical path (today it counts hops, not difficulty — §1 assumption 3).

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] the verify adversarial refute-read earns its place — it caught a real HIGH correctness bug (transitive blocking not propagated) that all 9 first-pass tests missed; the gate is not ceremony (evidence: refute REFUTED v1 → fixed → test_transitive_blocked_dep_is_not_scheduled)
- [TDD · folded] when verify reveals a MISSING test, reopen to TESTS not build — adding the guard test while in build tripped the tamper tripwire (build_tampered); the honest loop is reopen→tests→re-snapshot→build (evidence: gate returned return_to_build attempt 1/3, cleared by re-crossing tests→build)
- [ADD · folded] a read-only reporter that REUSES the existing satisfaction predicate (_dep_satisfied) inherits its correctness for free — the bug lived only in the NEW transitive layer, never the reused base (evidence: the satisfied-dep + archived-dep scenarios passed first try)
