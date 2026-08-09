# TASK: Persist a snapshot of the computed task DAG plan

slug: persist-dag-plan · created: 2026-06-29 · stage: mvp · sensitivity: mechanical · risk: low
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. Multi-component repo (monorepo/multi-repo)? add a `component: <name>` line (declared in `.add/components.toml`) to ADD that component's root to your §5 Scope; omit for single-component projects (byte-identical default). -->
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
  - `add-method/tooling/add.py:_wave_schedule_merged(state, mslugs) -> dict` — the PURE, total DAG scheduler; returns `{waves, critical_path, critical_path_len, tiers, blocked}` (or `{cycle}`). This is the recomputable projection. The plan snapshot stores ITS output.
  - `add-method/tooling/add.py:_wave_schedule(state, mslug)` — single-milestone wrapper over the merged form (byte-identical historical shape).
  - `add-method/tooling/add.py:cmd_waves` + `_wave_block_lines` — the READ-ONLY renderer (text + `--json`); the source of truth stays `state.json` `depends_on` edges, recomputed live every call.
  - `state.json` `tasks.<slug>.depends_on` (+ `milestone`, phase/gate via `_task_done`) — the EDGES = the authority the snapshot must stay fresh against.
  - precedent to reuse: `add.py` cross-component contract snapshot (lines ~909-929: a committed JSON file + a `hash` + idempotent re-write) and the scope-snapshot sidecar + `snapshot_md5` state anchor (lines ~826-834). Same temp+replace via `_atomic_write`, same hash-anchor-then-compare drift idiom.
  - `add_engine/io_state.py` (`_atomic_write`, `load_state`) · `add_engine/milestones.py` (`_active_milestone`, `_archived_task_slugs`) — fail-safe IO + the milestone accessors the snapshot keys on.
Context (working folder):
  - `.add/milestones/<mslug>/MILESTONE.md` — the per-milestone home; the DAG-plan snapshot lives BESIDE it (committed/auditable, NOT in `.gitignore`'s transient list `scope-snapshot.json`/`*.bak.json`).
  - `add-method/tooling/test_dag_scheduler.py` · `test_cross_active_waves.py` · `test_waves_merge.py` — the existing scheduler suite (the byte-identical oracle); a new `test_persist_dag_plan.py` joins them.
  - engine ships across trees: canonical `add-method/tooling/` → `_bundled/` + repo-root `.add/tooling/`; any engine change re-pins ENGINE_MD5 (`engine_pin.py`) + re-bundles (test_shared_engine_pin / test_engine_repin_parity / test_bundle_parity).
Honors (patterns / conventions):
  - MILESTONE shared decision: **"edges are truth, the plan is a snapshot."** The snapshot is NEVER the authority — `waves` keeps recomputing live; the snapshot is a committed projection with a freshness check (drift → stale flag).
  - `_wave_schedule_merged` is PURE/total/never-raises — the writer calls it; the reader recomputes the live edge-fingerprint and compares (no behavior change to the scheduler).
  - fail-safe reader (absent/garbled snapshot → a clean "none"/"unreadable" surface, never a trace), atomic writer (temp+replace), record-only command (no auto-mutation of edges).
Anchors the contract cites: `_wave_schedule_merged` · `state.json depends_on` edges · the new snapshot file `.add/milestones/<mslug>/dag-plan.json` · the new `add.py dag-plan` command · the `status` surfacing line.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Persist a per-milestone snapshot of the computed task DAG plan, with a freshness check against the live `depends_on` edges.
Framings weighed: new read-only-preserving `dag-plan` command writing a committed per-milestone JSON sidecar hash-anchored to the live edge set (chosen) · a `waves --save` flag (rejected — `waves` is contractually READ-ONLY/"writes nothing"; a write flag breaks that invariant + its suite) · a field inside `state.json` (rejected — `state.json` IS the authority/edges; nesting a projection of itself invites split-brain and isn't separately diffable/auditable)
Must:
<must>
  - `add.py dag-plan` (record-only) computes the schedule for the active milestone (or `--milestone <slug>`) via the existing `_wave_schedule_merged`, and writes a committed snapshot `.add/milestones/<mslug>/dag-plan.json`.
  - the snapshot stores: `milestone` · the schedule (`waves`, `critical_path`, `critical_path_len`, `tiers`, `blocked`) · `edges_fingerprint` (md5 over the CANONICAL live edge set — see ⚠) · `generated` (ISO date).
  - the write is atomic (temp+replace, via `_atomic_write`) and committed/auditable — NOT added to `.gitignore`'s transient list.
  - a freshness check recomputes the live edge fingerprint and compares it to the stored one: equal → FRESH; differ → STALE.
  - `add.py status` surfaces one `dag-plan:` line for the active milestone — `fresh ✓` · `stale (edges changed since <date>)` · `none — run add.py dag-plan`.
  - the snapshot is NEVER the authority: `waves` keeps recomputing live and is unchanged; `dag-plan` only records a projection.
  - idempotent: re-running `dag-plan` with an unchanged fingerprint leaves the file byte-identical (stable `generated` when nothing drifted — mirrors the cross-component snapshot's idempotent re-write).
</must>
Reject:
<reject>
  - `--milestone X` where X is not a milestone -> "unknown_milestone"   (reuse cmd_waves' existing reject)
  - no active milestone and no `--milestone` -> "no_active_milestone"   (reuse cmd_waves' existing reject)
  - the scheduler returns a cycle (`{cycle}`) -> "dependency_cycle" and NO snapshot is written (an unschedulable DAG is not persisted)   (reuse cmd_waves' existing reject)
</reject>
After:
<after>
  - `.add/milestones/<mslug>/dag-plan.json` exists with schedule + `edges_fingerprint` + `generated`.
  - immediately after a write, `status` shows `dag-plan: fresh ✓`; after any `depends_on` add/remove/redirect on an open member, `status` shows `dag-plan: stale`.
  - `add.py waves` output is byte-identical to before this task (read-only authority untouched).
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the freshness fingerprint domain — I fingerprint the EDGE STRUCTURE: every member's (done OR open) sorted `depends_on`, NOT the schedule output and NOT open-members-only. lowest confidence because "drift" is a judgment call. ALL-members is correct: `depends_on` is invariant under a task COMPLETING (which changes phase/gate, not edges), so completion stays FRESH, while ADD/REMOVE/REDIRECT of a dep — or a member added/removed — flips it STALE. (v1 used OPEN-only; a pre-test trace showed it flagged completion as drift → change-request to v2.) if still wrong: re-pick the domain (isolated to `_edges_fingerprint`).
  - [ ] snapshot HOME is per-milestone beside `MILESTONE.md` (matches the scheduler's milestone-scoping + the cross-active streams model) — vs one project-wide file; if wrong: a single global snapshot.
  - [ ] command name `dag-plan` (vs `plan` / `waves --snapshot`); a new subcommand ripples into the `test_min_pillar` LIFECYCLE census + help text; if wrong: rename only.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: write a fresh snapshot
  Given an active milestone with open members and depends_on edges
  When I run add.py dag-plan
  Then .add/milestones/<mslug>/dag-plan.json is created with the schedule, edges_fingerprint, and generated date
  And status shows "dag-plan: fresh ✓"
  And add.py waves output is byte-identical to before

Scenario: an edge change marks it stale
  Given a fresh dag-plan snapshot exists
  When a depends_on edge is added, removed, or redirected on an open member
  Then status shows "dag-plan: stale"
  And the snapshot file on disk is unchanged (dag-plan never auto-rewrites)

Scenario: completing a task does NOT mark it stale
  Given a fresh dag-plan snapshot exists
  When an open member completes (gate PASS) with no edge change
  Then status still shows "dag-plan: fresh ✓"
  And the snapshot file on disk is unchanged

Scenario: re-running with unchanged edges is idempotent
  Given a fresh dag-plan snapshot exists
  When I run add.py dag-plan again with no edge change
  Then the file is byte-identical (the generated date is unchanged)

Scenario: no snapshot yet
  Given no dag-plan.json for the active milestone
  When I run add.py status
  Then it shows "dag-plan: none — run add.py dag-plan"
  And no file is created by status

Scenario: a corrupt snapshot reads fail-safe
  Given a dag-plan.json that is not valid JSON
  When I run add.py status
  Then it shows "dag-plan: unreadable — run add.py dag-plan" (never a traceback)
  And the corrupt file is left untouched

Scenario: unknown milestone is rejected
  Given a slug that is not a milestone
  When I run add.py dag-plan --milestone <that slug>
  Then it dies "unknown_milestone"
  And no snapshot file is written

Scenario: no active milestone is rejected
  Given no active milestone and no --milestone given
  When I run add.py dag-plan
  Then it dies "no_active_milestone"
  And no snapshot file is written

Scenario: a dependency cycle is not persisted
  Given a dependency cycle among the milestone's open members
  When I run add.py dag-plan
  Then it dies "dependency_cycle"
  And no snapshot file is written
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
CLI  add.py dag-plan [--milestone <slug>]      # record-only; default target = active milestone
  ok   -> writes .add/milestones/<mslug>/dag-plan.json (atomic, committed) ; prints
          "dag-plan: wrote <mslug> — <W> wave(s), <T> task(s) (fresh ✓)"
  4xx  -> "unknown_milestone" | "no_active_milestone" | "dependency_cycle"   # NO file written on any reject

dag-plan.json   (json.dumps(..., indent=2, sort_keys=True) + "\n"; committed — NOT gitignored)
  { "milestone":         <slug>,
    "generated":         "<YYYY-MM-DD>",
    "edges_fingerprint": "<md5 hex>",
    "schedule": { "waves": [[slug,...],...], "critical_path": [slug,...],
                  "critical_path_len": <int>, "tiers": {slug: "top"|"mid"},
                  "blocked": {slug: [dep,...]} } }

edges_fingerprint := md5( json.dumps( {s: sorted(t.depends_on) for s,t in ALL members of mslug},
                                       sort_keys=True ).encode() ).hexdigest()
  # DOMAIN = ALL members (done OR open). depends_on is the EDGE STRUCTURE — invariant under a
  # task COMPLETING (completion changes phase/gate, never depends_on), and changes only when a dep
  # is added/removed/redirected or a member is added/removed. (v1 used OPEN-only, which wrongly
  # flagged completion as drift — a completed task leaving the dict changes the dict; change-request → v2.)

freshness(root, mslug) -> "none" | "unreadable" | "fresh" | "stale"
  absent file              -> "none"
  OSError / JSON error      -> "unreadable"            # fail-safe, never a traceback
  stored fp == live fp      -> "fresh"
  stored fp != live fp      -> "stale"

status line (active milestone, one line):
  fresh      -> "dag-plan: fresh ✓"
  stale      -> "dag-plan: stale (edges changed since <generated>)"
  none       -> "dag-plan: none — run add.py dag-plan"
  unreadable -> "dag-plan: unreadable — run add.py dag-plan"

idempotent write: if the file exists AND stored fp == live fp → leave it byte-identical (no re-date);
                  else write today's date + live schedule + live fp.
Schema: NO state.json field added (the snapshot is a standalone committed file). add.py waves UNCHANGED
        (still read-only, byte-identical). New: cmd_dag_plan + _dag_plan_path/_edges_fingerprint/
        _dag_plan_freshness helpers + one status line + the `dag-plan` argparse subcommand.
```

Least-sure flag surfaced at freeze: [contract] the **freshness fingerprint domain** — md5 over ALL members' `depends_on` (the edge STRUCTURE), so a task *completing* (the normal loop) does NOT mark the plan stale, while adding/removing/redirecting a `depends_on` (or adding/removing a member) does. v2 change-request: v1 scoped this to OPEN members, which a trace proved WRONG — a completed task leaving the open-set dict changed the fingerprint, flagging completion as drift (the contract's mechanism contradicted its own goal). Corrected to ALL-members before any test was written. Cost if still wrong: re-pick the domain (isolated to `_edges_fingerprint`).

Status: FROZEN @ v2 — approved by Tin Dang
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + every Reject + the ⚠ (completion≠drift) — 10 tests, all behavior-level.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_write_creates_snapshot_and_status_fresh: dag-plan writes the JSON (milestone/generated/fingerprint/schedule) + status shows fresh ✓
  - test_committed_not_gitignored: the snapshot path is not in .gitignore (committed/auditable)
  - test_edge_change_marks_stale_without_rewrite: a depends_on change → status stale; file bytes unchanged
  - test_completing_a_task_is_not_drift: a task done (no edge change) → status still fresh ✓ (the ⚠)
  - test_idempotent_rewrite: re-run with unchanged edges → file byte-identical
  - test_none_before_write: no snapshot → status "none"; status creates nothing
  - test_corrupt_snapshot_reads_fail_safe: invalid JSON → status "unreadable"; file untouched
  - test_unknown_milestone_rejected / test_no_active_milestone_rejected / test_dependency_cycle_not_persisted: each dies with its code, no file written
</test_plan>

Tests live in: `add-method/tooling/test_persist_dag_plan.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/tooling/` `.add/tooling/`
Strategy (ordered batches): 1. red tests (`test_persist_dag_plan.py`) in `add-method/tooling/` · 2. helpers `_dag_plan_path(root, mslug)` + `_edges_fingerprint(state, mslug)` + `_dag_plan_freshness(root, state, mslug)` · 3. `cmd_dag_plan` (compute via `_wave_schedule_merged`; reuse cmd_waves' unknown/no-active/cycle rejects BEFORE any write; atomic + idempotent write) · 4. `dag-plan` argparse subcommand + dispatch · 5. one `dag-plan:` line in `cmd_status` (only when an active milestone exists) · 6. green canonical suite · 7. `prepare_bundle` (engine) + dogfood-sync · 8. re-pin ENGINE_MD5 across trees · 9. full suite — fix `test_min_pillar` LIFECYCLE census + bundle/pin parity ripples.
Known-problem fixes: a new subcommand ripples into `test_min_pillar` LIFECYCLE + help census → add the `dag-plan` entry in the TESTS phase, re-cross tests→build · the status line sits in heavily-tested `cmd_status` → render it ONLY with an active milestone + place it so existing status assertions (streams-posture, identity, goal-ready) don't shift · engine change → re-pin all trees + re-bundle (`test_shared_engine_pin` / `test_bundle_parity` / `test_engine_repin_parity`) · fingerprint MUST be deterministic (`sort_keys`) or idempotency breaks · do NOT touch `cmd_waves` / `_wave_schedule_merged` (waves stays byte-identical).
Strategy actually used: as planned, with one mid-build contract correction. Added `_dag_plan_path` / `_edges_fingerprint` / `_dag_plan_freshness` / `_dag_plan_status_line` / `cmd_dag_plan` after `cmd_waves`; reused cmd_waves' unknown/no-active/cycle rejects BEFORE any write (validate-then-write), atomic temp+replace, deterministic `json.dumps(sort_keys=True)` for idempotency, stable `generated` reused on unchanged-fingerprint rewrite. cmd_waves / _wave_schedule_merged left byte-identical. One `dag-plan:` status line after goal-ready (active-milestone only). DEVIATION from plan step 1/9: the `test_min_pillar` census + the unrelated `test_skill_lean` rebaseline (c05a034 §5-enhance lean fallout, +61 B → baseline 39446→39523, ratio kept; Tin-authorized) were done in BUILD, not the TESTS phase — both fall inside the declared `add-method/tooling/` subtree (no scope_violation) and the engine flagged no tamper; disclosed here. The frozen §3 contract bug (open-only fingerprint → completion falsely stale) was caught pre-test in the prior session and re-frozen @ v2 (ALL members).
Safety rule (feature-specific): record-only — `dag-plan` never mutates `state.json` edges; every reject (unknown/no-active/cycle) fires BEFORE any write (validate-then-write); the write is atomic temp+replace.
Code lives in: the three engine trees above (`add.py` + `engine_pin.py` re-pin + bundle mirror).
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) is live: a completing verify gate refuses an
     out-of-scope build (scope_violation → self-heal) and add.py check surfaces it.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full canonical suite 2322/0 green
- [x] coverage did not decrease — added test_persist_dag_plan (10 tests) + dag-plan census in test_min_pillar
- [x] no test or contract was altered during build — frozen §3 v2 untouched; only ADDITIVE test coverage (census entry) + an authorized fence rebaseline, both in-scope; engine flagged no tamper
- [x] the green was EARNED — adversarial refute-read run (scratch project): real schedule data, byte-identical idempotent rewrite, completion stays fresh, edge-flip→stale, reject writes no file — see refute verdict below
- [x] concurrency / timing safe — record-only; validate-then-write (all rejects fire before any write); atomic temp+replace; no state.json mutation
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only (hashlib/json/pathlib); no new deps
- [x] layering & dependencies follow CONVENTIONS.md — helpers sit beside cmd_waves; reuses _wave_schedule_merged + _md5_text; waves authority untouched
- [x] reviewed — self-gated per risk-tiered posture (mechanical/additive task → AI auto-resolves verify; human spot-audit is the backstop)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [ ] `add.py dag-plan` creates a `dag-plan.json` under the milestone dir carrying milestone · generated · edges_fingerprint · schedule{waves,critical_path,critical_path_len,tiers,blocked} — confirmed by reading the file + test_write_creates_snapshot_and_status_fresh
- [ ] `status` reflects state: `fresh ✓` after a write · `stale` after a depends_on edit · `fresh ✓` still after a task completes · `none`/`unreadable` fail-safe — confirmed by the edge/completion/none/corrupt tests
- [ ] each reject (unknown_milestone · no_active_milestone · dependency_cycle) writes NO snapshot file — confirmed by the three reject tests
- [ ] `add.py waves` output is unchanged and the full suite is green with ENGINE_MD5 re-pinned across all 3 trees — confirmed by test_dag_scheduler + test_shared_engine_pin/test_bundle_parity

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `cmd_dag_plan` is dispatched by the `dag-plan` subparser; `_dag_plan_status_line` is called in cmd_status (active-milestone branch); `_dag_plan_freshness`/`_edges_fingerprint`/`_dag_plan_path` are each called by cmd_dag_plan + the status line. Confirmed by the refute-read (subcommand ran, status line rendered) + test_min_pillar read-spy exercising `dag-plan`.
- [x] DEAD-CODE (code) — no orphaned symbol: every new helper has a caller (grep-confirmed); no helper added "for later". cmd_waves/_wave_schedule_merged unchanged (no dead fork).
- [x] SEMANTIC — n/a (code task); the c05a034 lean-fence prose was rebaselined per the documented surface÷ratio method, not skimmed.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self · adversarially checked: ran `dag-plan` in a fresh scratch project and probed each contract claim for vacuity — (1) snapshot carries REAL schedule (waves [[a],[b]], critical_path_len 2, non-trivial fingerprint), not an empty stub; (2) re-run is byte-identical (idempotency real, `generated` stably reused); (3) completing a task keeps status `fresh ✓` (proves the v2 ALL-members fingerprint, refuting the v1 open-only bug); (4) flipping a `depends_on` edge flips status to `stale (edges changed…)`; (5) `--milestone nope` errors `unknown_milestone` and writes NO file (validate-then-write). No overfit/stub found — green is earned.

### GATE RECORD
Outcome: PASS
Reviewed by: Claude (self-gated — risk-tiered posture: mechanical/additive task auto-resolves verify on evidence + recorded refute-read; Tin's spot-audit is the backstop) · date: 2026-06-29

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose new read-only-preserving `dag-plan` command writing a committed per-milestone JSON sidecar hash-anchored to the live edge set; rejected a `waves --save` flag (rejected — `waves` is contractually READ-ONLY/"writes nothing"; a write flag breaks that invariant + its suite) · a field inside `state.json` (rejected — `state.json` IS the authority/edges; nesting a projection of itself invites split-brain and isn't separately diffable/auditable)
- [human] freeze — froze §3 @ v2 (approved by Tin Dang)
- [AI] build — strategy used: as planned, with one mid-build contract correction. Added `_dag_plan_path` / `_edges_fingerprint` / `_dag_plan_freshness` / `_dag_plan_status_line` / `cmd_dag_plan` after `cmd_waves`; reused cmd_waves' unknown/no-active/cycle rejects BEFORE any write (validate-then-write), atomic temp+replace, deterministic `json.dumps(sort_keys=True)` for idempotency, stable `generated` reused on unchanged-fingerprint rewrite. cmd_waves / _wave_schedule_merged left byte-identical. One `dag-plan:` status line after goal-ready (active-milestone only). DEVIATION from plan step 1/9: the `test_min_pillar` census + the unrelated `test_skill_lean` rebaseline (c05a034 §5-enhance lean fallout, +61 B → baseline 39446→39523, ratio kept; Tin-authorized) were done in BUILD, not the TESTS phase — both fall inside the declared `add-method/tooling/` subtree (no scope_violation) and the engine flagged no tamper; disclosed here. The frozen §3 contract bug (open-only fingerprint → completion falsely stale) was caught pre-test in the prior session and re-frozen @ v2 (ALL members).
- [AI] verify — gate PASS (reviewed by Claude (self-gated — risk-tiered posture: mechanical/additive task auto-resolves verify on evidence + recorded refute-read; Tin's spot-audit is the backstop))

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
