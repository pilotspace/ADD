# TASK: waves --merge: cross-milestone critical-path scheduling across the active SET

slug: waves-merge · created: 2026-06-26 · stage: mvp
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
- `add-method/tooling/add.py:cmd_waves` (2760-2804) — the READ-ONLY DAG command. TODAY: no `--milestone` → spans every active milestone but renders them as N SEPARATE per-milestone blocks (`scheds = [_wave_schedule(state,t) for t in targets]`, "active streams: N"). The `--merge` branch is the new behavior: ONE schedule over the UNION of the active SET's open members.
- `add-method/tooling/add.py:_wave_schedule` (2640-2728) — pure/total scheduler for ONE milestone. `open_members = {tasks whose .milestone == mslug and not done}`; a not-done dep that is NOT an open member here is UNSATISFIABLE → `blocked`. THIS is why a cross-milestone dep shows blocked today. Returns `{waves, critical_path, critical_path_len, tiers, blocked}` or `{cycle}`. Kahn waves + memoized longest-chain critical path; ties break by sorted slug.
- `add-method/tooling/add.py:_wave_block_lines` (2731-2757) — renders ONE schedule's text (`milestone: <slug>` header · `wave i:` · `critical path:` · `tier hint:` · `blocked:`). Merge needs a header naming the merged SET and (since tasks span milestones) per-task milestone disambiguation.
- `add-method/tooling/add.py` waves subparser (5434-5439): `--milestone`, `--json`, `func=cmd_waves`. ADD `--merge` (store_true) here.
- helpers reused unchanged: `_task_done`, `_archived_task_slugs`, `_find_cycle`, `_active_milestone`.

Context (working folder):
- 3 byte-identical add.py copies (`add-method/tooling` · `.add/tooling` · `add-method/src/add_method/_bundled/tooling`) — edit in lockstep + re-pin (engine-edit discipline). All currently == `ea8f87a198c3925778c32dcf25a2b4e0`.
- `engine_pin.py:ENGINE_MD5` = `ea8f87a198c3925778c32dcf25a2b4e0` — re-pin after this engine edit.
- `add-method/tooling/test_cross_active_waves.py` (7 tests, green) is the sibling oracle: `--merge` must NOT change the no-flag (separate-streams) or single-`--milestone` output. New tests land in `add-method/tooling/test_waves_merge.py`.

Honors (patterns / conventions):
- additive + opt-in: `--merge` is a NEW flag; no-flag and `--milestone` behavior stays byte-identical (single-active projects see zero change).
- pure/total scheduler: the merged scheduler is a thin generalization of `_wave_schedule` (membership = "open member of ANY target", not one mslug); never mutates state, never raises on dict input.
- engine-edit discipline: 3-tree byte-identity + same-commit ENGINE_MD5 re-pin; the existing suite is the regression oracle.
- design-for-failure: a cross-milestone dep CYCLE still `_die`s with `dependency_cycle`; an unknown `--milestone` still `_die`s `unknown_milestone`; `--merge` with a single active milestone degrades to that milestone's schedule (no crash).

Anchors the contract cites: `cmd_waves` (the `--merge` branch) · a new merged scheduler `_wave_schedule_merged(state, mslugs)` (or `_wave_schedule` generalized over a milestone SET) · `_wave_block_lines` (merged header + per-task milestone label) · the `--merge` subparser flag · `engine_pin.ENGINE_MD5`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `waves --merge` — fold the active SET into ONE unified DAG schedule so a cross-milestone dependency orders into a single critical path instead of showing as `blocked`. Today `waves` (no `--milestone`) renders each active milestone as a SEPARATE stream; `--merge` schedules over the UNION of their open members.
Framings weighed: thin generalization — a `_wave_schedule_merged(state, mslugs)` whose membership is "open member of ANY target milestone", with `_wave_schedule(state, mslug)` becoming a one-element wrapper over it (chosen — one scheduler, single == merge-over-one; the 7 existing tests prove single-milestone output is byte-identical) · stitch the N separate per-milestone schedules after the fact (rejected — a cross-milestone dep A→B can't reorder once each milestone is scheduled in isolation; the dep must live in the SAME DAG) · make the no-flag default merged (rejected — breaks the separate-streams byte-identity + 7 green tests; merge must be opt-in).
Must:
<must>
  - `waves --merge` (no `--milestone`) builds ONE schedule over the union of open (not-done) members across ALL active milestones (`_active_milestone` primary + `active_milestones`, primary first), honoring cross-milestone `depends_on`. A not-done dep that is an open member of ANOTHER active milestone now SCHEDULES into a later wave (the whole point), not `blocked`.
  - membership rule widens but does not loosen: a not-done dep that is NOT an open member of ANY target (external/unknown/archived-incomplete) is still UNSATISFIABLE → `blocked` (same fix-point propagation as `_wave_schedule`).
  - merged TEXT render: a header naming the set — `merged: <m1> + <m2> (<N> milestones)` — and each scheduled task carries its milestone — `<slug> [<milestone>]` (+ ` (deps: …)` when it has member-deps) — so cross-milestone tasks are unambiguous. Critical-path / tier-hint / blocked lines mirror `_wave_block_lines`.
  - merged JSON render: one object `{"merged": [<targets>], "waves", "critical_path", "critical_path_len", "tiers", "blocked"}` — distinct from the existing `{"streams":[…]}` multi-stream shape.
  - `--merge` over a single milestone — whether only one is active OR an explicit `--milestone <slug>` is given — DEGRADES gracefully to that one milestone's schedule rendered in merged format (header `merged: <m1> (1 milestone)`); `--merge --milestone` is NOT a conflict. Never crashes.
  - BYTE-IDENTITY: the no-flag (separate streams) and explicit `--milestone` outputs (text + JSON) are UNCHANGED — proven by the full existing suite (incl. the 7 `test_cross_active_waves`) staying green with NO test weakened.
  - all 3 add.py copies byte-identical + `ENGINE_MD5` re-pinned in the same change; parity/pin tests green.
</must>
Reject:
<reject>
  - `--merge --milestone <unknown>` (an explicit target with no record) -> `"unknown_milestone"` (the existing target validation, applied on the merge path; a VALID explicit milestone is not rejected — it degrades to a 1-milestone merge)
  - `--merge` with NO active milestone and no `--milestone` -> `"no_active_milestone"` (the existing no-target reject, unchanged)
  - a dependency cycle across the merged DAG (a→b in m1, b→a in m2) -> `"dependency_cycle"` (the existing cycle reject, now spanning milestones)
</reject>
After:
<after>
  - `waves --merge` prints ONE unified schedule over the active SET; a cross-milestone dep orders into the single critical path; the separate-streams and single-`--milestone` outputs are unchanged; the full suite is green with no test changed; the 3 copies + pin are green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the merged RENDER format — header `merged: a + b (N milestones)` and per-task `slug [milestone]` — is NEW surface the existing tests don't constrain; lowest confidence because it's a presentation choice, not logic. If the labels read poorly it's a cosmetic re-format (no data/logic risk), caught by this task's own new render test. Cost if wrong: re-edit the two render lines.
  - [x] `--merge` + `--milestone` DEGRADES to that single milestone's merged schedule (not a reject) — RESOLVED at freeze: Tin chose degrade over fail-loud (2026-06-26). A valid explicit target → 1-milestone merge; an unknown one → `unknown_milestone`.
  - [ ] critical-path tie-break stays "sorted slug" across the merged set — relies on task slugs being globally unique project-wide (they are: `new-task` rejects a duplicate slug, observed this session). Confirm: yes, unique.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: Cross-milestone dependency schedules instead of blocking
  Given two active milestones m1 (open task t1) and m2 (open task t2, depends_on t1)
  When `waves --merge` runs
  Then t1 is in wave 1 and t2 is in wave 2 (t2 is NOT reported blocked)
  And the critical path is t1 → t2 (2 tasks)

Scenario: Merged render names the set and labels each task's milestone
  Given the same two-milestone state
  When `waves --merge` renders text
  Then the first line is "merged: m1 + m2 (2 milestones)"
  And t1 renders as "t1 [m1]" and t2 as "t2 [m2] (deps: t1)"

Scenario: External/unknown dep still blocks under merge
  Given m1 has open task t1 depends_on "ghost" (no record, not done, not a member of any target)
  When `waves --merge` runs
  Then t1 is reported "blocked: t1 (waiting on ghost)" and is not scheduled

Scenario: Merge over a single active milestone degrades gracefully
  Given exactly one active milestone m1 with open tasks
  When `waves --merge` runs
  Then it prints a merged block headed "merged: m1 (1 milestone)" over m1's tasks
  And it does not crash

Scenario: Merge JSON shape
  Given two active milestones
  When `waves --merge --json` runs
  Then it prints one object with keys "merged" (the target list), "waves", "critical_path", "critical_path_len", "tiers", "blocked"

Scenario: Merge with a valid explicit milestone degrades to that milestone
  Given two active milestones but `--milestone m1` is passed with `--merge`
  When `waves --merge --milestone m1` runs
  Then it prints a merged block headed "merged: m1 (1 milestone)" over m1's tasks only
  And it does not error

Scenario: Reject — merge with an unknown explicit milestone
  Given `--milestone ghost` (no such milestone) is passed with `--merge`
  When `waves --merge --milestone ghost` runs
  Then it exits with error "unknown_milestone"

Scenario: Reject — merge with no active milestone
  Given no active milestone and no --milestone
  When `waves --merge` runs
  Then it exits with error "no_active_milestone"

Scenario: Reject — cross-milestone dependency cycle
  Given m1 task a depends_on b and m2 task b depends_on a (both open)
  When `waves --merge` runs
  Then it exits with error "dependency_cycle"

Scenario: Existing outputs are byte-identical (regression oracle)
  Given the existing full suite, including test_cross_active_waves
  When the merged scheduler lands and `_wave_schedule` becomes a one-element wrapper
  Then the no-flag separate-streams output and the single `--milestone` output are unchanged
  And the full suite stays green with NO test modified

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
# waves --merge — one unified DAG schedule over the active SET (internal CLI; READ-ONLY, writes nothing, no `next:` footer)

cmd_waves(args) when args.merge is True:
  if args.milestone:                                            # explicit target → degrade to a 1-milestone merge (NOT a conflict)
    if args.milestone not in (state.get("milestones") or {}): _die("unknown_milestone: '<slug>' is not a milestone in this project")
    targets = [args.milestone]
  else:
    primary = _active_milestone(state)
    if not primary:   _die("no_active_milestone")
    targets = [primary] + [m for m in (state.get("active_milestones") or []) if m != primary]   # all active, primary first, de-duped
  sched = _wave_schedule_merged(state, targets)
  if "cycle" in sched: _die("dependency_cycle: " + " -> ".join(sched["cycle"]))
  TEXT:  print "\n".join(_wave_block_lines_merged(state, targets, sched))
  JSON:  print json.dumps({"merged": targets, **sched})         # sched = {waves, critical_path, critical_path_len, tiers, blocked}

_wave_schedule_merged(state, mslugs) -> dict        # pure · total · never mutates · never raises on dict input
  # SAME return shape + SAME algorithm as _wave_schedule, except membership spans the milestone SET:
  open_members = {s: t for s, t in tasks.items() if t.get("milestone") in set(mslugs) and not _task_done(t)}
  # → identical blocked fix-point (dep unsatisfiable iff not _ok and not a still-schedulable member),
  #   identical Kahn waves, identical memoized longest-chain critical path, tie-break by sorted slug.
  returns {"cycle":[…]}  OR  {"waves","critical_path","critical_path_len","tiers","blocked"}

_wave_schedule(state, mslug) -> dict                 # BECOMES a one-element wrapper (output byte-identical, proven by the 7 tests)
  return _wave_schedule_merged(state, [mslug])

_wave_block_lines_merged(state, mslugs, sched) -> list[str]    # the merged TEXT
  header:           "merged: " + " + ".join(mslugs) + f" ({len(mslugs)} milestone{'s' if len!=1 else ''})"
  per scheduled task in each wave:  f"{slug} [{tasks[slug]['milestone']}]" + (f" (deps: {', '.join(member_deps)})" if member_deps else "")
  then:             "critical path: …", "tier hint: …", "blocked: …"   # identical formatting to _wave_block_lines

Invariant: for the no-flag (separate streams) and explicit --milestone paths, text AND json output are
  BYTE-IDENTICAL to pre-change (the full suite incl. test_cross_active_waves is the oracle; NO test changed).
Errors: unknown_milestone (existing) · no_active_milestone (existing) · dependency_cycle (existing). No NEW error code — `--merge --milestone` degrades, it does not reject.
Engine: 3 add.py copies byte-identical + ENGINE_MD5 re-pinned in the same commit.
```

Status: FROZEN @ v1 — approved by Tin Dang
Least-sure flag surfaced at freeze: [contract] the merged RENDER format — header `merged: a + b (N milestones)` + per-task `slug [milestone]` — is NEW surface the existing tests don't constrain; it is a presentation choice, not logic, so if it reads poorly it is a cosmetic re-format (no data/logic risk), caught by this task's own render test. Second flag: [spec] `--merge --milestone` was RESOLVED at freeze to DEGRADE to a 1-milestone merge (Tin's call 2026-06-26), not reject — a valid explicit target → 1-milestone merge, an unknown one → `unknown_milestone`.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every new branch of `_wave_schedule_merged` + the `--merge` arm of `cmd_waves` (both text + json) + each reject; the full suite as the regression oracle for the unchanged paths.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_merge_schedules_cross_milestone_dep: m1{t1}, m2{t2 dep t1} → merged sched: wave1==[t1], wave2==[t2], critical_path==[t1,t2], t2 NOT in blocked
  - test_merge_render_header_and_milestone_labels: text first line == "merged: m1 + m2 (2 milestones)"; contains "t1 [m1]" and "t2 [m2] (deps: t1)"
  - test_merge_external_dep_still_blocks: m1{t1 dep "ghost"} → "ghost" unsatisfiable → t1 in blocked, not scheduled
  - test_merge_single_milestone_degrades: one active milestone m1 → header "merged: m1 (1 milestone)", schedules m1's tasks, no exception
  - test_merge_json_shape: --merge --json → dict with keys {merged, waves, critical_path, critical_path_len, tiers, blocked}; merged==targets
  - test_merge_explicit_milestone_degrades: --merge --milestone m1 → merged block "merged: m1 (1 milestone)" over m1's tasks; no error
  - test_merge_unknown_milestone_dies: --merge --milestone ghost → _die "unknown_milestone"
  - test_merge_no_active_milestone_dies: no active milestone, --merge → _die "no_active_milestone"
  - test_merge_cross_milestone_cycle_dies: m1{a dep b}, m2{b dep a} → _die "dependency_cycle"
  - test_wave_schedule_wrapper_identity: for several states, _wave_schedule(state,"m") == _wave_schedule_merged(state,["m"]) (the wrapper changes nothing)
  - (regression) the FULL existing suite incl. test_cross_active_waves stays green with NO test changed — separate-streams + single --milestone output byte-identical
  - test_three_trees_pinned: 3 add.py copies byte-identical AND == engine_pin.ENGINE_MD5
</test_plan>

Tests live in: `add-method/tooling/test_waves_merge.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_waves_merge.py`
Strategy (ordered batches): 1. write `test_waves_merge.py` red (merged scheduler branches + cmd_waves --merge text/json + each reject). · 2. in `add-method/tooling/add.py`: rename the body of `_wave_schedule` to `_wave_schedule_merged(state, mslugs)` (membership over `set(mslugs)`); make `_wave_schedule(state, mslug)` return `_wave_schedule_merged(state, [mslug])`; add `_wave_block_lines_merged`; add the `--merge` branch to `cmd_waves`; add the `--merge` subparser flag. · 3. run the FULL suite — separate-streams + single `--milestone` must stay green with NO test change (the oracle). · 4. mirror byte-identically to the other 2 copies; re-pin ENGINE_MD5; green incl. parity/pin.
Safety rule (feature-specific): the `_wave_schedule` → `_wave_schedule_merged([mslug])` refactor MUST be output-identical for a single milestone (the 7 `test_cross_active_waves` + full suite are the oracle); `_wave_schedule_merged` stays pure/total (never mutates state, never raises on dict input); diff the 3 copies before re-pinning.
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

- [x] all tests pass — full suite 2037 OK (1972→2037; +11 test_waves_merge); check 432/0; audit clean (90 tasks)
- [x] coverage did not decrease — 11 new tests cover every new branch (merged scheduler · cmd_waves --merge text+json · degrade · 3 rejects · wrapper identity · pin)
- [x] no test or contract was altered during build — git shows only add.py ×3 + engine_pin.py (all §5-declared) changed; test_waves_merge.py is NEW (written in TESTS); no existing test touched; §3 FROZEN @ v1 untouched
- [x] the green was EARNED, not gamed — the behavioral tests were RED before / GREEN after (cross-milestone dep would block on old code); byte-identity proven by the 2037 suite green with NO test changed; refute-read found no overfit/vacuous asserts; `state["tasks"][s]` in the merged render is keyed only on scheduled members (no KeyError path)
- [x] concurrency / timing of the risky operation is safe — read-only command; `_wave_schedule_merged` is pure/total (no state mutation, set-based membership); single-process CLI
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only, no new import; milestone slug validated (`unknown_milestone`) before use; no shell/eval
- [x] layering & dependencies follow CONVENTIONS.md — additive opt-in flag; the merged scheduler is a thin generalization, `_wave_schedule` now a one-element wrapper; no command logic changed on the existing paths
- [x] a person reviewed and approved the change — Tin Dang (auto-mode standing authorization) + the §3 freeze approval (degrade decision) + a manual adversarial refute-read

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `waves --merge` on a 2-milestone state where beta(m2) depends on alpha(m1) puts alpha in wave 1 and beta in wave 2 with critical path `alpha → beta` (NOT `blocked: beta`) — confirmed: test_merge_schedules_cross_milestone_dep green; the test was RED on pre-build code (beta blocked)
- [x] the merged block renders `merged: m1 + m2 (2 milestones)` and per-task `slug [milestone]` (e.g. `beta [m2] (deps: alpha)`) — confirmed: test_merge_render_header_and_milestone_labels green + LIVE stdout showed `merged: multi-active-polish (1 milestone)` / `wave 1: waves-merge [multi-active-polish]`
- [x] no-flag (separate streams) + single `--milestone` text AND json output unchanged — confirmed: test_cross_active_waves 7/7 green + full suite 2037 green with NO test modified; LIVE `waves` still prints `milestone:`-headed format (no `merged:`)
- [x] `--merge --milestone m1` degrades to `merged: m1 (1 milestone)`; unknown → `unknown_milestone`; no active → `no_active_milestone`; cross-ms cycle → `dependency_cycle` — confirmed: test_merge_explicit_milestone_degrades / _unknown_milestone_dies / _no_active_milestone_dies / _cross_milestone_cycle_dies all green
- [x] 3 add.py copies byte-identical + `ENGINE_MD5` re-pinned — confirmed: all three == `e67bc6d796a2c9529ca580deee16b147` == engine_pin.ENGINE_MD5

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_wave_schedule_merged` called by both `_wave_schedule` (wrapper) and `cmd_waves` (--merge branch); `_wave_block_lines_merged` called by the --merge text branch; `--merge` flag read via `getattr(args,"merge",False)`; all live
- [x] DEAD-CODE (code) — no orphaned symbol; the old `_wave_schedule` body moved into `_wave_schedule_merged` (still reached via the wrapper on every existing path); no unreferenced helper introduced
- [ ] SEMANTIC (prose / non-code) — N/A (code change; the one prose touch — `--merge` help + docstring — passed the ubiquitous-language lint after rewording "fold"→"unify")

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang (auto-mode standing authorization) · date: 2026-06-26

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): do users reach for `waves --merge` vs the separate streams? rate of `dependency_cycle` on the merged DAG (a cross-milestone cycle is a real planning smell).

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · open] the merged header does not de-dup repeated entries in `active_milestones` (a leftover dup would read `merged: m1 + m1 (2 milestones)`) — cosmetic only; guard if `active_milestones` is ever observed to carry dups (evidence: de-dup is only against the primary today, this task)

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] a NEW add.py prose string must dodge the reserved ubiquitous-language terms (here "fold") — the lint fires at FULL-SUITE time, not at write time, so an engine edit that adds help/docstring prose should grep the new strings against the ban list before the first full run (evidence: `--merge` help + docstring used "fold", caught by test_ubiquitous_language, reworded → "unify", this task) [folded foundation-version 55]
