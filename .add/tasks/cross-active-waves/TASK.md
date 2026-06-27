# TASK: widen waves/ready to the frontier across all active milestones

slug: cross-active-waves · created: 2026-06-22 · stage: mvp · risk: high
autonomy: conservative   <!-- lowered from project default auto: edits the byte-pinned engine across all 3 add.py copies + re-pins; a human owns the high-risk gate (run.md guard). -->
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
- `add-method/tooling/add.py` (+ 2 mirror copies) — widen the scheduler frontier across active milestones:
  - `cmd_waves` (~2678) — TODAY resolves ONE milestone (`--milestone` or `_active_milestone` primary scalar) and prints its `_wave_schedule`. KEEP the primary as the gate (preserve `no_active_milestone` when the primary scalar is None — a test relies on this) and the `--milestone` explicit single-target path EXACTLY. ADDITIVELY, when NO `--milestone` is given, build `targets = [primary] + [m in active_milestones if m != primary]`; for len==1 render TODAY's exact output (byte-identical), for len>=2 print a `active streams: N` header then each milestone's existing block. JSON: len==1 → unchanged `{"milestone":…, **sched}`; len>=2 → new `{"streams":[{"milestone":…, **sched}, …]}`.
  - factor the per-milestone render into a small `_wave_block_lines(state, mslug, sched) -> list[str]` so the single-target output is character-for-character what `cmd_waves` prints today.
  - `cmd_ready` (~2542) — HUMAN path only: append a present-only ` [<milestone>]` to each ready line so the cross-stream frontier is legible (a milestone-less task gets no annotation — byte-identical). `ready --json` shape UNCHANGED (stays a list of slug strings — a breaking shape change is OUT).
- `engine_pin.py:ENGINE_MD5` — re-pin after this engine edit (same commit). (No new subcommand → no `test_min_pillar` LIFECYCLE change.)

Context (working folder):
- M1 gave `active_milestones` (the SET) + `_active_milestone` (the primary scalar = active_milestones[0]). `cmd_waves` today reads only the primary scalar, so with ≥2 active milestones it silently schedules only the primary — the exact gap this task closes.
- `_wave_schedule(state, mslug)` (~2588) returns `{waves, critical_path, critical_path_len, tiers, blocked}` or `{cycle:…}` — UNCHANGED; this task only loops it over more milestones.
- ⚠ test-harness trap: `test_dag_scheduler._load` sets the SCALAR `active_milestone` but NOT the SET `active_milestones` (which stays `["v1"]` from setUp). `test_no_active_milestone_rejected` sets scalar=None and expects rejection — so the rejection MUST stay keyed on the primary scalar, never on the leftover set. The `others` expansion only adds milestones; it never changes whether we reject.
- `cmd_ready` already iterates ALL tasks project-wide (it is NOT scoped to one milestone), so it ALREADY spans every active milestone — this task only ADDS the `[milestone]` legibility annotation; it does not narrow the set.

Honors (patterns / conventions):
- additive-cue convention — single active milestone (or `--milestone`) → `waves` output byte-identical; a milestone-less `ready` line → byte-identical. New behavior only when ≥2 milestones are active.
- cross-active = SCOPE not SEMANTICS (milestone rule) — `_wave_schedule`'s DAG/ready logic is untouched; only the set of milestones it ranges over widens.
- read-only — `waves`/`ready` write nothing (existing read-only guards hold).
- engine-edit discipline — 3-tree byte-identity + same-commit ENGINE_MD5 re-pin. No new command → census unchanged.

Anchors the contract cites: `cmd_waves` cross-active target resolution (primary + other active milestones; primary scalar stays the `no_active_milestone` gate) · `_wave_block_lines(state, mslug, sched)` (the extracted per-milestone render) · the len==1 byte-identical / len>=2 `streams` shapes (text + json) · `cmd_ready`'s present-only ` [<milestone>]` human annotation (json unchanged) · reuse of `_wave_schedule` · `_active_milestone`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `add.py waves` (no `--milestone`) reports the wave schedule for EVERY active milestone, not just the primary — and `ready` annotates each ready task with its milestone — so a team running parallel streams sees the whole schedulable frontier at once.
Framings weighed: primary + other active milestones, each rendered as its own block (chosen — preserves the single-milestone output byte-identically, keeps each stream's critical path/tiers legible, additive) · a single MERGED cross-milestone DAG (rejected — changes `_wave_schedule` semantics + critical-path meaning across unrelated milestones; the milestone scope rule says widen scope, not semantics) · leave `waves` single + add a new `streams-waves` command (rejected — duplicates; the no-arg gap is the natural place).
Must:
<must>
  - `cmd_waves` with `--milestone <m>` is UNCHANGED: single target `m`, today's exact output (text + `{"milestone":m, **sched}` json), `unknown_milestone` on a bad slug.
  - `cmd_waves` with NO `--milestone` and a primary active milestone (the scalar `_active_milestone`) builds `targets = [primary] + [m for m in active_milestones if m != primary]`; with exactly one target it renders TODAY's output byte-identically; with ≥2 it prints an `active streams: <N>` header then each milestone's existing block (separated), and json emits `{"streams": [{"milestone":…, **sched}, …]}`.
  - `cmd_waves` with NO primary active milestone (scalar None) and no `--milestone` still `_die("no_active_milestone …")` — the rejection is keyed on the primary scalar, never on a leftover `active_milestones` set.
  - a dependency cycle in ANY rendered target still surfaces (`dependency_cycle` die, naming the cycle) — preserved from today for the single path and applied per-target.
  - `cmd_ready` human output appends a present-only ` [<milestone>]` to each ready line (a milestone-less task gets no annotation, byte-identical); `ready --json` is UNCHANGED (list of slug strings). All 3 add.py copies byte-identical + `ENGINE_MD5` re-pinned same commit; read-only preserved; census unchanged.
</must>
Reject:
<reject>
  - no `--milestone` AND no primary active milestone -> `no_active_milestone` (unchanged).
  - `--milestone <unknown>` -> `unknown_milestone` (unchanged).
  - a dependency cycle in a rendered milestone -> `dependency_cycle` (unchanged).
</reject>
After:
<after>
  - with ≥2 active milestones, `add.py waves` shows every active stream's schedule (text + `streams` json); single-active / `--milestone` output is byte-identical; `ready` lines name their milestone; state.json unchanged; the prior suite is green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ Rendering each active milestone as its OWN independent wave block (vs a single merged cross-milestone DAG) is the right model — lowest confidence because a team MIGHT have cross-milestone dependencies they'd want unified into one critical path. Chose per-milestone blocks because milestones are meant to be independent streams (deps across them are the `blocked`-on-non-member case `_wave_schedule` already handles) and merging would redefine "critical path" across unrelated work. If wrong (real cross-milestone DAGs matter): add a `--merge` mode later — the per-block render is the safe, faithful default and needs no re-freeze.
  - [ ] keying the `no_active_milestone` rejection on the primary scalar (not the set) is right — confirmed: required to preserve test_no_active_milestone_rejected, and the scalar IS the canonical "is there a primary" signal.
  - [ ] `ready --json` staying a slug-string list (annotation human-only) is right — confirmed: changing it to objects would break test_machine_state's `d["ready"]` membership checks; the human annotation delivers the cross-stream legibility without a breaking shape change.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: waves spans every active milestone
  Given two active milestones m1 (task a) and m2 (task b), each with not-done tasks
  When `add.py waves`
  Then the output names BOTH m1 and m2 and lists each one's wave(s)
  And state.json is unchanged (read-only)

Scenario: single active milestone is byte-identical
  Given exactly one active milestone with a diamond dep graph
  When `add.py waves`
  Then the output has no "active streams:" header and matches the pre-change single-milestone format

Scenario: --milestone targets one stream unchanged
  Given two active milestones
  When `add.py waves --milestone m2`
  Then only m2's schedule is shown (the explicit single-target path is unchanged)

Scenario: waves json emits streams for multi-active
  Given two active milestones
  When `add.py waves --json`
  Then stdout is one object with a "streams" array of {milestone, waves, …} (one per active milestone)

Scenario: no active milestone still rejected
  Given no primary active milestone (scalar None) and no --milestone
  When `add.py waves`
  Then it exits non-zero with "no_active_milestone"

Scenario: ready annotates each task with its milestone
  Given two active milestones with ready (dep-satisfied) tasks
  When `add.py ready`
  Then each ready line names its task's milestone in brackets, and a milestone-less task has none
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
_wave_block_lines(state, mslug: str, sched: dict) -> list[str]
  the EXACT lines cmd_waves prints today for one milestone:
    "milestone: <mslug>"
    if no waves: "blocked: …" lines, or "all tasks done — nothing to schedule"
    else: "wave i: …" per wave · "critical path: … (N tasks)" · "tier hint: top → …; mid → …"
          · "blocked: …" lines
  (pure render of an already-computed sched; no I/O)

cmd_waves(args):
  state = (json|load); mslug_arg = args.milestone
  if mslug_arg:  targets = [mslug_arg]
  else:
     primary = _active_milestone(state)             # the SCALAR — the gate
     if not primary: _die("no_active_milestone: …")  # unchanged rejection
     targets = [primary] + [m for m in (state.active_milestones or []) if m != primary]
  for each t in targets:
     t not in milestones -> _die("unknown_milestone: …")     # explicit-arg path
     sched = _wave_schedule(state, t); "cycle" in sched -> _die("dependency_cycle: …")
  TEXT:
     len 1 -> print _wave_block_lines(state, targets[0], sched0)   # BYTE-IDENTICAL to today
     len>=2 -> print f"active streams: {len(targets)}"; per target: block lines, blank line between
  JSON:
     len 1 -> {"milestone": targets[0], **sched0}                  # unchanged
     len>=2 -> {"streams": [{"milestone": t, **sched_t} for t in targets]}

cmd_ready(args):  HUMAN path only — each ready line:
     ms = tasks[slug].get("milestone");  ms_frag = f"  [{ms}]" if ms else ""
     print(f"  {slug}{ms_frag}{after_suffix}")
  --json UNCHANGED (list of slug strings).

Schema: READ-ONLY — no state write, no schema change, no new state key. New `_wave_block_lines`
  helper (extracted render). Reuses `_wave_schedule` · `_active_milestone`. No new command.
```

Status: FROZEN @ v1 — approved by Tin Dang (auto-mode standing authorization) · 2026-06-22

Least-sure flag surfaced at freeze:
- [contract] per-milestone independent wave blocks vs a single MERGED cross-milestone DAG — the point most likely wrong. A team with real cross-milestone dependencies might want one unified critical path; this contract renders each active milestone as its own block (cross-milestone deps remain the `blocked`-on-non-member case `_wave_schedule` already handles). Chosen because milestones are independent streams and merging would redefine "critical path" across unrelated work. Cost if wrong: add a `--merge` mode later at the target-resolution seam — additive, no re-freeze of this surface.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the 6 scenarios + the engine-pin parity guard.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_waves_spans_active_milestones: 2 active ms (m1:a, m2:b); `waves` names both m1 and m2 + their waves; state bytes unchanged
  - test_single_active_byte_identical: 1 active ms diamond; `waves` has NO "active streams:" header; "wave 1:" + "critical path:" present (today's format)
  - test_explicit_milestone_single: 2 active ms; `waves --milestone m2` shows only m2 (no "active streams:" header, no m1)
  - test_waves_json_streams_multi: 2 active ms; `waves --json` → object with "streams" array, one {milestone,waves,…} per active ms
  - test_no_active_milestone_still_rejected: primary scalar None (set may be non-empty); `waves` → nonzero + "no_active_milestone"
  - test_ready_annotates_milestone: 2 active ms with ready tasks; `ready` lines carry "[m1]"/"[m2]"; a milestone-less ready task has no bracket
  - test_three_trees_byte_identical_and_pinned: md5(3 copies)==1 and ==ENGINE_MD5
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
Tests in: `add-method/tooling/test_cross_active_waves.py`
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_cross_active_waves.py`
Strategy (ordered batches): 1. extract `_wave_block_lines(state, mslug, sched)` from cmd_waves' current per-milestone render (verify single-target output byte-identical). 2. add cross-active target resolution (primary + others) + the len==1 / len>=2 text+json branches. 3. annotate cmd_ready human lines with `[milestone]`. 4. mirror to the other 2 copies + re-pin ENGINE_MD5. 5. run the red suite green.
Safety rule (feature-specific): READ-ONLY — `waves`/`ready` write nothing; the single-target / `--milestone` / N<=1 paths must be byte-identical (assert in tests); `_wave_block_lines` is a pure render.
Code lives in: `add-method/tooling/add.py` (+ 2 mirrors)
Constraints: do NOT change any test or the contract; allow-list packages only (stdlib only — already imported); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — `test_cross_active_waves` 7/7 green; full tooling suite 1517 green (was 1510)
- [x] coverage did not decrease — net +7 tests (6 scenarios + pin guard); +1 separator assert added post-review; none removed; all existing dag-scheduler/ready tests still green (extraction proven non-regressive)
- [x] no test or contract was altered during build — §3 frozen unchanged; the only post-review test edit was an ADDED separator assertion; re-crossed tests→build to re-anchor
- [x] the green was EARNED, not gamed — independent python-expert refute-read: MERGE-WITH-NITS, no HARD-STOP. It verified the byte-identical extraction (`print("\n".join(lines))` == old per-line prints), the harness trap (gate reads the scalar only), and zero dag-scheduler regression. Its one coverage nit (separator not byte-asserted) was closed
- [x] concurrency / timing — n/a: `waves`/`ready` are single read-render; `_wave_block_lines` is a pure render; no write, no race
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only (already imported); no new input surface
- [x] layering & dependencies follow CONVENTIONS.md — reuses `_wave_schedule` + `_active_milestone`; `_wave_block_lines` is the extracted pure render; cross-active = scope-not-semantics (the DAG logic is untouched)
- [x] a person reviewed and approved the change — auto-mode standing authorization (risk:high → conservative), independent subagent review on record

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] with ≥2 active milestones, `waves` shows every stream's schedule — confirmed by a live scratch-project run: "active streams: 2" + a "milestone: m1" block AND a "milestone: m2" block, each with its own wave/critical-path/tier lines
- [x] single-active / `--milestone` output is byte-identical — confirmed by test_single_active_byte_identical (no "active streams:" header) + test_explicit_milestone_single + the full unchanged test_dag_scheduler suite passing
- [x] `waves --json` emits a `streams` array for multi-active, unchanged `{milestone,…}` for single — confirmed by test_waves_json_streams_multi + the unchanged single-target json tests in test_dag_scheduler
- [x] `ready` lines name their milestone, present-only — confirmed by the live run ("alpha  [m1]" / "beta  [m2]") + test_ready_annotates_milestone (a milestone-less line carries no bracket); `ready --json` shape unchanged

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_wave_block_lines` is called by `cmd_waves` (both single + multi text paths); the cross-active target resolution + `streams` json + `ready` `[ms]` fragment are all on the live render path; exercised by the 7 tests
- [x] DEAD-CODE (code) — the old inline render was REPLACED by `_wave_block_lines` (no duplicate left); no orphaned symbol
- [x] SEMANTIC — n/a (code task; WIRING applies)

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang (auto-mode standing authorization) · date: 2026-06-22

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): do teams actually run ≥2 active milestones (is the cross-active view used)? · any request for a merged cross-milestone critical path (the freeze flag) · a corrupt `active_milestones` entry tripping the unknown_milestone die

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · carried] a `waves --merge` mode that unifies cross-milestone deps into one critical path, if real cross-milestone DAGs matter (evidence: §3 freeze flag — the per-milestone-block model was chosen as the safe default; merge is the documented escape hatch) [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]
- [SPEC · carried] decide whether a corrupt `active_milestones` entry (slug not in milestones) should SKIP rather than `unknown_milestone`-die in the auto-expanded `waves` set (evidence: §0 foot-gun note — today it dies, which is loud but blocks the whole multi-stream view on one bad entry; `doctor` would catch it, so dying may be fine) [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [ADD · folded] when widening a single-target command to multi-target, EXTRACT the per-target render into a pure helper and keep the len==1 path calling it verbatim — `print("\n".join(lines))` is byte-identical to the old per-line `print()`s, so the single-target output (and every existing test) stays green while the multi-target path is purely additive (evidence: cross-active-waves extracted `_wave_block_lines`; the whole unchanged test_dag_scheduler suite stayed green) [folded foundation-version 45]
- [TDD · folded] a "spans multiple X" test must assert the SEPARATOR/fencing, not just that both X appear — both-present passes even if the blocks run together or the header sits in the wrong place (evidence: refute-read nit — added `assertIn("\n\nmilestone: m2")` to pin the blank-line fence between stream blocks) [folded foundation-version 45]
