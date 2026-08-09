# TASK: status renders the active set as parallel streams

slug: parallel-status-view · created: 2026-06-22 · stage: mvp · risk: high
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
- `add-method/tooling/add.py:cmd_status` (1147) — the render. Two surfaces: the `--json` branch (top) emits `active_task` + a milestone rollup; the human-readable branch prints `active  : <task|(none)>` (1232) and the milestone rollup loop (1215-1221) marks `"*" if mslug == active_ms`.
- `add-method/tooling/add.py` accessors (277-308) — read the SET/map through the task-2 seam: `_active_milestone(state)` (primary scalar), `_active_task(state, milestone=None)`, and the raw `state.get("active_milestones")` / `state.get("active_tasks")` for the SET + map.
- `engine_pin.py:ENGINE_MD5` = `929ced7e72f573aa547c8f57809a75ee` — re-pin after this engine edit.

Context (working folder):
- 3 byte-identical add.py copies — edit in lockstep + re-pin.
- existing status tests assert `assertIn("active  :", out)` (loose) — keeping that line preserves them; no test does an exact key-set match on `status --json` (additive JSON keys are safe).
- the migration seeds `active_milestones` from the scalar (≤1 member); the streams view only differs from today at N≥2.

Honors (patterns / conventions):
- additive-when-richer — every prior status cue (graduation/release/spec/fold) is N≤1 byte-identical, a new line ONLY when the richer condition holds; the streams block follows that exact convention (gate on `len(active_milestones) >= 2`).
- presentation-only — no command DECISION changes; the full suite is the N≤1 byte-for-decision oracle.
- read through the task-2 accessor seam; engine-edit discipline — 3-tree byte-identity + same-commit re-pin.

Anchors the contract cites: `cmd_status` (both surfaces) · `_active_milestone`/`_active_task` · `state["active_milestones"]`/`state["active_tasks"]` · the new `streams :` block · the rollup mark `mslug in active_milestones` · `engine_pin.ENGINE_MD5`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `status` renders the active SET as parallel streams — when ≥2 milestones are active, each is shown as its own stream (active task + phase), so a user working N milestones in parallel reads all live fronts at a glance instead of a single active line.
Framings weighed: additive streams block gated on N≥2 (chosen — N≤1 output stays byte-identical, so the full suite is the untouched oracle; the richer view appears exactly when parallelism exists) · always-replace the `active :` line with a streams view (rejected — churns every existing status test for zero N≤1 benefit) · a separate `streams` subcommand (rejected — status is the one orientation surface; a parallel user shouldn't have to know a second verb).
Must:
<must>
  - When `len(active_milestones) <= 1`: the human-readable status output is BYTE-IDENTICAL to today (the `active  : <task|(none)>` line; the rollup `*` on the single active milestone). No streams block.
  - When `len(active_milestones) >= 2`: after the `active  :` line, print a `streams :` block — one line per active milestone (PRIMARY first, then the rest in activation order), each naming its active task (from `active_tasks`, `(none)` if unset) and that task's phase (`-` if the task is absent), with the primary marked `▸` and tagged `(primary)`.
  - The milestone rollup mark becomes `"*" if mslug in active_milestones else " "` (N≤1: identical, since `active_milestones == [primary]` or `[]`; N≥2: every active member is marked).
  - `status --json` ADDITIVELY gains `active_milestones` (list) + `active_tasks` (map); every existing key is unchanged.
  - Presentation-only: no command DECISION changes; the full prior suite stays green with no test weakened.
  - All 3 add.py copies byte-identical + ENGINE_MD5 re-pinned in the same change; parity/pin tests green.
</must>
Reject:
<reject>
  - (none — `status` is a read-only render; it has no input to reject. The "negative" case is the N≤1 path producing byte-identical output, asserted as a scenario.)
</reject>
After:
<after>
  - With ≥2 active milestones, `status` shows a `streams :` block listing each active milestone with its own active task + phase, primary first and tagged; with ≤1 active milestone the output is byte-identical to today; `status --json` exposes the SET + map; the 3 copies + pin are green; the full prior suite is green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ The streams block is gated on `len(active_milestones) >= 2` (not >=1), so a single-active project never sees it. Lowest confidence because a user might expect the richer block once ANY milestone is active; chosen because N≤1 byte-identity keeps the entire existing status suite as an untouched oracle (the codebase's standing additive-cue convention). If wrong: lower the gate to `>= 1` in a one-line follow-up (still additive — N=0 shows nothing).
  - [ ] Primary-first ordering with a `▸`/`(primary)` tag (vs activation order, or marking none primary). Confirm at freeze — cosmetic, only affects line order + the tag.
  - [ ] Per-stream phase reads `tasks[active_tasks[m]]["phase"]`, falling to `-` when the milestone has no active task or the task record is absent. Confirm at freeze.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: Two active milestones render as parallel streams
  Given active_milestones=["m1","m2"] (primary m2), active_tasks={"m1":"t1","m2":"t2"}, t1 phase=verify, t2 phase=build
  When `status`
  Then the output contains "streams : 2 active milestones"
  And a line for m2 marked "▸" tagged "(primary)" naming task=t2 phase=build
  And a line for m1 naming task=t1 phase=verify
  And m1 AND m2 both carry "*" in the milestone rollup

Scenario: Single active milestone is byte-identical to today
  Given active_milestones=["m1"] (the migrated single-active shape)
  When `status`
  Then the output contains "active  :" and NO "streams :" block
  And the rollup marks only m1 with "*"

Scenario: No active milestone shows no streams block
  Given active_milestones=[] (no active milestone)
  When `status`
  Then the output contains "active  : (none)" and NO "streams :" block

Scenario: A stream with no active task reads (none)/-
  Given active_milestones=["m1","m2"] (primary m2) and active_tasks={"m2":"t2"} (m1 has no active task)
  When `status`
  Then the m1 stream line shows task=(none) phase=-

Scenario: status --json exposes the SET and the map
  Given active_milestones=["m1","m2"], active_tasks={"m1":"t1","m2":"t2"}
  When `status --json`
  Then the JSON has active_milestones==["m1","m2"] AND active_tasks=={"m1":"t1","m2":"t2"}
  And the existing active_task key is still present

Scenario: Single-active behavior is unchanged
  Given the existing suite (the oracle)
  When the streams block + json keys are added
  Then the full prior suite stays green with no test changed

Scenario: The engine edit stays pinned
  Given all three add.py copies are edited
  Then they are byte-identical AND match the re-pinned ENGINE_MD5
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
# status render: the active SET as parallel streams (presentation-only; decisions unchanged)

cmd_status  (human-readable branch)
  let A = state.get("active_milestones") or []   (read via the task-2 seam shape)
  let primary = _active_milestone(state)
  # the `active  : <task|(none)>` line is UNCHANGED.
  # rollup mark (milestones loop): "*" if mslug in A else " "      # N<=1 == today
  if len(A) >= 2:                                                  # additive — printed ONLY at true parallelism
      order = [primary] + [m for m in A if m != primary]          # primary first, then activation order
      print "streams : {len(A)} active milestones"
      for m in order:
          tk   = (state.get("active_tasks") or {}).get(m)
          ph   = (state.get("tasks") or {}).get(tk, {}).get("phase", "-") if tk else "-"
          mark = "▸" if m == primary else " "
          tag  = "  (primary)" if m == primary else ""
          print f"  {mark} {m:<20} task={tk or '(none)'}  phase={ph}{tag}"

cmd_status  (--json branch)
  ADD (existing keys unchanged):
    "active_milestones": list(state.get("active_milestones") or [])
    "active_tasks":      dict(state.get("active_tasks") or {})

Invariant: presentation-only — no command DECISION changes; N<=1 text + the existing json keys are
  byte-for-decision identical (the full suite is the oracle).
Engine: 3 add.py copies byte-identical + ENGINE_MD5 re-pinned same commit.
No reject codes — status is a read-only render.
```

Status: FROZEN @ v1 — approved by Tin Dang (2026-06-22; auto-mode standing authorization; multi-active foundation 4/5; additive streams gated on N>=2 · primary-first `▸`/(primary) · per-stream phase via the task record)
Least-sure flag surfaced at freeze: [contract] the streams block is gated on `len(active_milestones) >= 2`, so a single-active project never sees the richer view — chosen to keep N≤1 output byte-identical (the entire existing status suite stays an untouched oracle, the codebase's standing additive-cue convention). If the block is wanted at N≥1, it is a one-line gate change later (still additive: N=0 prints nothing). Second flag: [contract] primary-first ordering + the `▸`/`(primary)` tag is cosmetic — only line order + the tag, no data.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the streams block at N=0/1/2 + the no-active-task fallback + the 2 json keys; full suite as the N≤1 oracle.
Plan (one test per scenario, asserting behavior not internals; via add.main in-proc with redirect_stdout):
<test_plan>
  - test_two_active_render_as_streams: craft active_milestones=[m1,m2] primary m2, active_tasks={m1:t1,m2:t2}, phases set → "streams : 2 active milestones", a "▸ m2 … task=t2 phase=build … (primary)" line, an " m1 … task=t1 phase=verify" line
  - test_single_active_no_streams_block: active_milestones=[m1] → "active  :" present, "streams :" absent
  - test_no_active_no_streams_block: active_milestones=[] → "active  : (none)", "streams :" absent
  - test_stream_without_active_task_shows_none: active_tasks lacks m1 → m1 line "task=(none)  phase=-"
  - test_rollup_marks_every_active_member: N=2 → both m1 and m2 rollup lines carry "*"
  - test_json_exposes_set_and_map: status --json → active_milestones==[m1,m2], active_tasks=={m1:t1,m2:t2}, active_task still present
  - (regression) FULL prior suite green, no test changed (N≤1 oracle)
  - test_engine_three_trees_pinned: 3 copies byte-identical == ENGINE_MD5
</test_plan>

Tests live in: `add-method/tooling/test_parallel_status_view.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_parallel_status_view.py` `add-method/tooling/test_wave_status_hint.py`
Strategy (ordered batches): 1. write `test_parallel_status_view.py` red. · 2. in `cmd_status`: change the rollup mark to `mslug in active_milestones`; add the `streams :` block after the `active  :` line gated on `len(A) >= 2`; add the 2 json keys. · 3. green new suite + FULL suite (N≤1 oracle, no test change). · 4. mirror to 2 copies; re-pin ENGINE_MD5; green incl. parity.
Safety rule (feature-specific): additive only — the N≤1 text path and every existing json key stay byte-identical; read the SET/map through the task-2 seam shape; diff the 3 copies before re-pinning.
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

- [x] all tests pass — full suite 1411→1420 green; new test_parallel_status_view.py [10] green
- [x] coverage did not decrease — +10 new tests; +3 verify-hardening assertions (N=1 rollup mark + N=1 json)
- [x] no FROZEN CONTRACT altered — §3 untouched. Tests ADDED (the red suite + 2 review-NIT hardening tests) + 1 SIBLING guard co-updated (test_wave_status_hint json-surface ratifies the 2 new additive keys; base keys immutable, set still tight) — declared in §5 Scope; none weakened
- [x] the green was EARNED, not gamed — independent python-expert adversarial refute-read (0.88) verdict MERGE-WITH-NITS, 0 blocking; it confirmed crash-safety on partial/legacy state + a tight json-surface guard; its 3 test-honesty NITs (unproven N=1 rollup-mark / N=1 json byte-identity) were CLOSED with hardening assertions
- [x] concurrency / timing — N/A (read-only render; no IO mutation)
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only; no new imports
- [x] layering & dependencies follow CONVENTIONS.md — reads the SET/map through the task-2 accessor seam shape; additive-cue convention (N≤1 byte-identical) matched
- [x] a person reviewed and approved the change — Tin Dang (auto-mode standing authorization) after the independent review + NIT closure

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] N≥2: `status` prints `streams : <N> active milestones` then one task+phase line per active milestone, primary first marked `▸`/`(primary)` — confirmed by test_two_active_render_as_streams + test_primary_listed_first + the eyeballed CLI run (`▸ m2 … task=t2 phase=build (primary)` then ` m1 … task=t1 phase=verify`)
- [x] N≤1: the human-readable `status` output is byte-identical to today (no `streams :` line; the single active milestone keeps its `*`) — confirmed by the full existing status suite staying green + test_single_active_no_streams_block (now also asserting the N=1 rollup mark) / test_no_active_no_streams_block
- [x] `status --json` carries `active_milestones` + `active_tasks` alongside the unchanged `active_task` — confirmed by test_json_exposes_set_and_map + test_json_single_active_preserves_active_task (N=1)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — the streams block + json keys read the SET/map through the task-2 seam shape (`state.get("active_milestones")`/`active_tasks`, `_active_milestone`); no new helper introduced (inline render); rollup mark + streams + json all exercised by the 10 tests
- [x] DEAD-CODE (code) — no orphaned symbol; the rollup-mark change REPLACES the prior `== active_ms` test (not duplicated); the streams locals are all consumed
- [x] SEMANTIC (prose / non-code) — n/a (engine-render + test only; no prose/guide changed)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-mode standing authorization) · date: 2026-06-22
Evidence: full suite 1420 green · new red→green suite test_parallel_status_view.py [10] · dogfood check 404/0 · audit clean (74) · 3-tree byte-identity + ENGINE_MD5 fa8e9818 re-pinned · eyeballed CLI on a crafted 2-active board renders the streams block correctly. Independent python-expert adversarial review (0.88) MERGE-WITH-NITS, 0 blocking — confirmed crash-safety on partial state + tight json-surface guard; its 3 test-honesty NITs closed with N=1 rollup-mark + N=1 json hardening assertions. Presentation-only; no frozen contract altered; no test weakened.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [TDD · folded] a "byte-identical at N≤1" claim needs a test that LOCKS the unchanged path (the N=1 rollup `*`, the N=1 json shape), not just one asserting the new path's ABSENCE — else the oracle can't catch a future regression in the boundary (evidence: review NIT — the absence-only tests left the rollup-mark change unproven until the hardening assertions were added) [folded foundation-version 41]
- [ADD · folded] a frozen presentation-only render still has a guarded SURFACE — `status --json` is ratified by an explicit sanctioned-keys test; adding keys is a census co-update (extend the sanctioned set, keep base immutable + the equality tight), not a silent append (evidence: test_wave_status_hint.test_json_surface_frozen went red on the 2 new keys until ratified) [folded foundation-version 41]
