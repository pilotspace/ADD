# TASK: Persona proposes route (full|fast|oneshot) + depth at new-task; human ratifies at the freeze

slug: persona-routes-depth · created: 2026-07-16 · stage: mvp
milestone: thin-engine-loop
autonomy: auto
phase: done
route: full · routed-by: persona:methodology-engine-dev — engine parse + audit lints + doctrine text: full rigor, no lane collapse

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: persona-routed lane — the fitting persona proposes the route (full|fast|oneshot) in the TASK header; the freeze ratifies + records it; audit measures, never blocks
Framings weighed: header-line + freeze-record + audit-measure (chosen) · engine splices route at new-task (rejected: a per-lane line breaks template-unify's strict fast-subset pin; the engine can't pick a persona) · freeze REFUSES unrouted tasks (rejected: adds a 5th floor — charter says measure-not-block)
Must:
<must>
  - M1 route grammar: one header line `route: <full|fast|oneshot> · routed-by: <persona:<slug> | human> — <why>` written while drafting the bundle (the persona's proposal), no engine render change
  - M2 freeze ratifies: the direction→build cross parses the line and records state.json tasks[<slug>].route = { lane, by } — the durable ratify evidence (re-cross re-records)
  - M3 measure-not-block: a missing/malformed route line never refuses the freeze — recorded as lane "unrouted"
  - M4 audit measures: `add.py audit` gains route_unrecorded (a post-feature freeze record whose lane is "unrouted") and route_lane_mismatch (recorded lane contradicts the task's actual lane flags) — findings, never gates
  - M5 doctrine: SKILL.md flag mode teaches propose-then-ratify (persona proposes the route; the human's flag/freeze ratifies); the four floors named unchanged on fast/oneshot routes; SKILL.md stays ≤9500B
  - M6 grandfather: a task frozen before this feature has no route key — audit never retro-reds it
</must>
Reject:
<reject>
  - unknown lane token in the route line (e.g. route: turbo) -> recorded as "unrouted" (surfaces as "route_unrecorded")
  - recorded lane contradicts the scaffold's real lane (route: full on a --fast task) -> "route_lane_mismatch"
  - route line deleted after a recorded freeze -> "route_unrecorded" (state key is the witness; mirrors unflagged_freeze's tamper glint)
</reject>
After:
<after>
  - every NEW freeze writes tasks[<slug>].route; add.py audit on a routed task reports 0 route findings; the doctrine text is live ×3 skill trees; old records audit exactly as before
</after>
Boundary: the route line's `·` separator and `— <why>` tail are the format variants the tests must speak (persona:<slug> vs human author); no other external input shape.
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [test] SKILL.md's flag-mode paragraph ("two human-owned settings · never auto-picked") is pinned by an un-censused set of wording tests, and the byte headroom is 176B — lowest confidence because the last three tasks each under-counted wording pins; if wrong: red-fix loops + byte-funding cuts, no floor at risk
  - [ ] _build_entry is the single write point for freeze-time state (flag_verified precedent) — confirmed by reading add.py:_build_entry
  - [ ] audit grandfathering by key-absence matches the flag_verified precedent — confirmed at _audit_findings
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: routed freeze records the lane   # M1+M2
  Given a task whose header carries route: full · routed-by: persona:methodology-engine-dev — engine change
  When add.py freeze --by "Tin Dang" --cross
  Then state.json tasks[slug].route == { lane: "full", by: "persona:methodology-engine-dev — engine change" }
  And the §3 contract and flag stamps behave exactly as before

Scenario: unrouted freeze still crosses   # M3
  Given a task with no route line in its header
  When freeze --cross
  Then the cross succeeds and route.lane records "unrouted"
  And no new refusal error exists at the freeze (floor census unchanged)

Scenario: unknown lane token   # R1
  Given a header line route: turbo · routed-by: human — hunch
  When freeze --cross
  Then route.lane records "unrouted"
  And audit on the finished task reports route_unrecorded

Scenario: lane mismatch measured   # R2+M4
  Given a --fast task frozen with route: full · routed-by: human — misfiled
  When add.py audit
  Then findings include route_lane_mismatch naming the slug
  And the task's gate outcome is untouched (measure, never a gate)

Scenario: route line deleted after freeze   # R3
  Given a routed, gated task whose header route line is then hand-deleted
  When add.py audit
  Then findings include route_unrecorded
  And nothing blocks — a human spot-audit is the backstop

Scenario: grandfather   # M6
  Given a task record frozen before this feature (no route key in state.json)
  When add.py audit
  Then no route finding fires for it
  And the audit board is never retro-redded

Scenario: doctrine live   # M5
  Given the three skill trees
  When SKILL.md's flag-mode paragraph is read
  Then it teaches persona-proposes → human-ratifies (route line named) and the fast/oneshot floors unchanged
  And SKILL.md ≤ 9500 bytes, trees byte-identical
```

</scenarios>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Grounding (the real code the contract will cite — gather BEFORE you freeze)
Touches (files · symbols · signatures): add.py:_build_entry — freeze-time state writes (the flag_verified stamp is the insertion seam) · add.py:_audit_findings — the measure-not-block lint home (grandfather idiom at the flag_verified check) · add.py header regexes (_RISK_HIGH_RE cluster) — new _ROUTE_LINE_RE lands beside them · engine_pin.py ENGINE_MD5 (repin) · add-method/skill/add/SKILL.md flag-mode paragraph (9,324B / 9,500 ceiling) · phases/direction.md (one route-line sentence in the plan span)
Context (working folder): .add/tasks/persona-routes-depth/ (this bundle) · tmp/ (commit msg)
Honors (patterns / conventions): measure-not-block audit idiom (refute_unrecorded · advisor_verdict_unrecorded) · grandfather-by-key-absence (flag_verified) · validate-then-write in _build_entry · doc/skill edits alone never repin, engine edits do (4-way twin parity)
Seams consulted: .add/SEAMS.md#three-tree-parity
Anchors the contract cites: _build_entry · _audit_findings · _ROUTE_LINE_RE (new) · tasks[slug].route (new state key) · SKILL.md flag mode
Issues/Risks: SKILL.md wording pins on "human-owned settings" un-censused (the ⚠ flag) · template-unify's strict fast-subset pin forbids per-lane spliced lines (why the engine does NOT render the route) · audit/freeze fixtures asserting exact state dicts may need the new route key tolerated
Related intent: thin-engine-loop exit criterion 4 (route header ratified at freeze, floors hold on fast) · the milestone's route-header charter line · user goal: persona-adaptive ADD, minimum ceremony
Ground SHA: d74a58b — stamped by freeze

### Contract (freeze the shape — the HARD, tamper-guarded core)

```
header line (AI/persona writes it while drafting; no engine render change)
  route: <full|fast|oneshot> · routed-by: <persona:<slug> | human> — <why>
freeze / re-cross (direction→build, in _build_entry beside flag_verified)
  parse header -> state.tasks[<slug>].route = { lane: "full|fast|oneshot|unrouted", by: <str|null> }
  never refuses on route (measure-not-block); every existing floor unchanged
audit (measure-not-block, grandfathered by key absence)
  route_unrecorded    -> route key present AND lane == "unrouted"
  route_lane_mismatch -> lane valid AND lane != actual (oneshot > fast > full from state flags)
Schema: state.json tasks[<slug>].route { lane: str, by: str|null } — written ONLY at freeze/re-cross
```

Glossary deltas: route: the ceremony lane of a task (full | fast | oneshot), persona-proposed in the TASK header and human-ratified at the freeze
Least-sure flag surfaced at freeze:
  ⚠ [test] SKILL.md's flag-mode wording is pinned by an un-censused set of tests and the byte headroom is 176B — cost if wrong: red-fix loops + byte-funding cuts, no floor at risk.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: yes — the freeze report (banner/ARC/SHAPE) rendered before this froze

### Build-strategy (the intended approach — SOFT: preferred; the builder self-improves and records what it ACTUALLY did at verify)
Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/` `.add/tooling/` `add-method/.add/tooling/` `add-method/skill/` `.claude/skills/` `tmp/`
Strategy (ordered batches): 1. red suite test_persona_routes_depth.py · 2. _ROUTE_LINE_RE + parse/record in _build_entry · 3. the two audit lints (grandfathered) · 4. SKILL.md flag-mode rewrite (census the wording pins FIRST) + direction.md sentence, sync ×3 · 5. repin + 4-way twin sync · 6. full suite
Approach (domain strategy): mirror the flag_verified seam end-to-end (parse at the same write point, grandfather the same way, lint in the same audit body) — chosen in §1 Framings over engine-rendered lines
Data strategy: one nested dict on the existing per-task state record, written at one seam — agrees with the Contract Schema line
Pattern: measure-not-block + grandfather-by-key-absence (Grounding Honors: refute_unrecorded / flag_verified precedents)
Optimization stance: engine bytes + SKILL.md tokens — budget: SKILL.md ≤9500B, no new freeze refusal, audit stays O(tasks); ⚠ least-trusted facet: the SKILL.md wording-pin census
Persona (required): methodology-engine-dev (engine seams) with book-technical-writer consulted on the doctrine text
Spawn isolation (default): inline (sequential engine surgery on one seam — inline-over-heavy-spawns)
Known-problem fixes: wording pins on the flag-mode para -> grep test_*.py for its phrases BEFORE editing · state-dict-exact fixtures -> tolerate the new route key · a per-lane spliced line breaks the fast-subset pin -> never render route at new-task · SKILL.md byte adds -> fund from the same paragraph

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 100% of the new parse/record/lint branches (7 scenarios -> 9 tests)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_routed_freeze_records_lane: tmp project, header route line, freeze --cross / assert state route dict · covers: M1+M2
  - test_recross_rerecords_route: edit the line, re-cross --by / assert re-recorded · covers: M2
  - test_unrouted_freeze_crosses: no line, freeze / assert lane "unrouted" + cross succeeded · covers: M3
  - test_unknown_lane_records_unrouted: route: turbo, freeze / assert "unrouted" · covers: R1
  - test_audit_route_unrecorded: gated unrouted task / assert finding code · covers: M4+R3
  - test_audit_route_lane_mismatch: --fast task frozen route: full / assert finding · covers: M4+R2
  - test_audit_grandfather: record without route key / assert zero route findings · covers: M6
  - test_skill_doctrine_propose_ratify: SKILL.md names the route line + persona-proposes/human-ratifies; <=9500B; x3 md5 lockstep · covers: M5
  - test_no_new_freeze_refusal: floor pin — the freeze refusal census gains nothing · covers: M3 floor
</test_plan>

Tests live in: `add-method/tooling/test_persona_routes_depth.py` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

> The change plan — grounding + contract + build-strategy — was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope, follow the strategy (improve on it if the code teaches you better), and touch no test or the frozen contract.
Strategy actually used: as planned, one addition — the R3 tamper glint needed a second lint branch (state-vs-header cross-check mirroring unflagged_freeze) that the first cut missed; the ⚠ wording-pin risk never materialized (zero external pins on the flag-mode paragraph).
Safety rule (feature-specific): measure-not-block — no new freeze refusal may exist (floor-pinned by test_no_new_freeze_refusal).
Code lives in: `./src/`
Constraints: do NOT change any test or the frozen §3 contract; stay inside the §3 Build-strategy Scope; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 3111 OK; own suite 11/11
- [x] coverage did not decrease — 11 new tests, none removed
- [x] no test or contract altered during build — red suite byte-untouched since freeze; §3 untouched
- [x] the green was EARNED — 8 red flipped by implementing exactly the contract seams; refute-read below
- [x] concurrency — n/a (single-writer state record at the existing freeze seam)
- [x] no secrets/injection/deps — a regex + a dict on state.json; stdlib only
- [x] layering — regex in the header-regex cluster, record at the flag_verified seam, lint in _audit_findings; 4-way twin parity
- [x] a person reviewed — Tin Dang froze §3 v1 (the one approval), 2026-07-17

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] a freeze on a routed tmp task leaves "route": {"lane","by"} in state.json — test_routed_freeze_records_lane fixture, state read
- [x] audit surfaces route_lane_mismatch on the mismatched fixture; a keyless pre-feature record fires nothing — _audit_findings asserted both ways
- [x] SKILL.md flag mode reads propose-then-ratify; 9,480B ≤ 9,500; 3 trees one digest — wc -c + md5
- [x] suite red-first (8 red/3 floors) then 11/11; full suite 3111 OK; ENGINE_MD5 ec9a5730… repinned once, 4-way parity — run logs

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] DIALECT — tests speak the contract's literal route-line format (middot + em-dash tail, both routed-by forms per §1 Boundary)
- [x] WIRING — _ROUTE_LINE_RE/_ROUTE_LANES consumed by _route_record; _route_record called from _build_entry AND the audit glint; grep-verified
- [x] DEAD-CODE — none; every new symbol has ≥2 call sites or a floor test
- [x] SEMANTIC — SKILL.md flag-mode + direction.md freeze paragraph read in full; wording_lint 0 findings

### Live-verify evidence — confirm the §3 PLAN grounding anchors still resolve (fill at the gate)
> Re-resolve every symbol the §3 Contract cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] every §3 anchor resolves: _build_entry · _audit_findings · _ROUTE_LINE_RE · tasks[slug].route (live in this repo's own state after the dogfood freeze) — grep + state read
- [x] moved since Ground SHA: _declared_scope drifted 5971→5990 (SEAMS.md re-pinned)

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: red-for-right-reason pre-build; floors green BEFORE build (grandfather · unrouted-crosses · no-refusal) and still green after; the R3 red was fixed by ADDING the glint branch, never by weakening the assert.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR — no input crosses a trust boundary (repo-local header line); HARD-STOP teaching untouched
2. Concurrency: CLEAR — same single save_state path
3. Architecture: CLEAR — mirrors flag_verified end-to-end; measure-not-block honored
Verdict: PASS
Residue: none
Binding: advisory — undeclared sensitivity (method/engine task; the freeze was the human approval)

### GATE RECORD
Reported: yes — the DECIDE card rendered before this outcome was recorded
Outcome: PASS
If RISK-ACCEPTED -> n/a
Reviewed by: auto-resolved on complete evidence (autonomy: auto; freeze @ v1 by Tin Dang was the one approval) · date: 2026-07-17

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): route_unrecorded rate across the next tasks (audit board) · fast/oneshot proposal uptake vs full — feeds persona-gepa-loop.

### Decisions (ADR)
- [AI] specify — chose header-line + freeze-record + audit-measure; rejected engine splices route at new-task (rejected: a per-lane line breaks template-unify's strict fast-subset pin; the engine can't pick a persona) · freeze REFUSES unrouted tasks (rejected: adds a 5th floor — charter says measure-not-block)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — approach: mirror the flag_verified seam end-to-end (parse at the same write point, grandfather the same way, lint in the same audit body) — chosen in §1 Framings over engine-rendered lines
- [AI] build — data strategy: one nested dict on the existing per-task state record, written at one seam — agrees with the Contract Schema line
- [AI] build — pattern: measure-not-block + grandfather-by-key-absence (Grounding Honors: refute_unrecorded / flag_verified precedents)
- [AI] build — optimization stance: engine bytes + SKILL.md tokens — budget: SKILL.md ≤9500B, no new freeze refusal, audit stays O(tasks); ⚠ least-trusted facet: the SKILL.md wording-pin census
- [AI] build — strategy used: as planned, one addition — the R3 tamper glint needed a second lint branch (state-vs-header cross-check mirroring unflagged_freeze) that the first cut missed; the ⚠ wording-pin risk never materialized (zero external pins on the flag-mode paragraph).
- [AI] verify — gate PASS (reviewed by auto-resolved on complete evidence (autonomy: auto; freeze @ v1 by Tin Dang was the one approval))

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).
- [SPEC · open] test-corpus-slim candidate: 8 dead PHASES_POOL constants, ~38 scattered ENGINE_MD5 pins, and heavy 3-tree-parity duplication across ~167 files invite a consolidation task (evidence: 2026-07-17 census)

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

- [ADD · open] a tamper-glint contract clause (state-is-the-witness) needs its OWN lint branch — recording the state key alone doesn't measure a deleted header line (evidence: R3 red survived the first build cut)
