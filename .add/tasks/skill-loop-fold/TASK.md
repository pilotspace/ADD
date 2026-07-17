# TASK: SKILL.md narrates the 3-beat loop; phases/ 7→3 on-demand references; zero mandatory guide reads

slug: skill-loop-fold · created: 2026-07-17 · stage: mvp
milestone: thin-engine-loop
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: SKILL.md narrates the whole 3-beat loop inline; phases/ collapses 7→3 on-demand reference files; an ordinary task reads ZERO guide files
Framings weighed: fold-into-3-references (chosen — mirrors phase-collapse-3: the skill's shape tracks the engine's) · keep-7-add-an-index (rejected: the index is another read; files still 33.5KB) · delete-phases-entirely (rejected: deep/stuck paths still need the reference depth SKILL.md can't hold at ≤9500B)
Must:
<must>
  - M1 phases/ holds EXACTLY direction.md · build.md · verify.md (×3 skill trees): 0-setup + 1-specify + 3-plan + 4-tests fold into direction.md (setup IS direction at project scale — same human seam); 5-build → build.md; 6-verify → verify.md; fast-lane.md deleted, its routing absorbed into SKILL.md's flag-mode paragraph
  - M2 SKILL.md narrates the 3-beat loop INLINE (orient → direction bundle → ONE freeze --by --cross → build → gate PASS) and names phase files as ON-DEMAND references ("stuck or deep"), never a mandatory per-phase load
  - M3 every test-pinned teaching anchor survives in its new home: "## Declaring where tests live" + declare grammar → direction.md · setup baseline/run-mode + UDD trigger → direction.md · facets + persona spawn teaching → build.md · deep-checks "do not skim" rubric + refute-read + security escalation + ADR harvest → verify.md
  - M4 SKILL.md ≤ 9500 B AND the phases/ pool measurably smaller than 33,496 B (byte ledger in-test)
  - M5 the 3 files byte-identical across add-method/skill · .claude/skills · _bundled/skill
</must>
Reject:
<reject>
  - a 4th file (or a surviving old name) in any phases/ tree -> "guide_census_broken"
  - a pinned teaching anchor lost in the fold -> "anchor_dropped"
  - SKILL.md over its byte ceiling -> "skill_over_budget"
  - the loop table re-instructs a mandatory per-phase guide read -> "mandatory_read_reintroduced"
</reject>
After:
<after>
  - an ordinary task runs new-task → freeze --by --cross → gate PASS with SKILL.md as the ONLY method text read; phases/ is reference depth, loaded on demand
</after>
Boundary: none — no external input (prose + file-census task; the tests speak file paths and byte counts only)
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ ~17 test files pin guide PATHS or CONTENT (census below) — lowest confidence because the pinned-phrase census is LONG and some pins are byte-exact rubric anchors; if wrong: extra red-fix loops, no floor at risk (the 8-name path lists are already exists()-tolerant — 2-scenarios/7-observe died long ago)
  - [x] the engine never reads skill phases/ (its `guide` points at .add/docs chapters) — confirmed: zero add.py references; NO engine repin this task
  - [x] SKILL.md is at EXACTLY 9500B — every inline-narration byte must be funded by compressing the 7-row flow table into the 3-beat form
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: census is exactly three   # M1, R:guide_census_broken
  Given the three skill trees
  When phases/ is globbed in each
  Then exactly {direction.md, build.md, verify.md} exist
  And no legacy name (0-setup…6-verify, fast-lane) survives anywhere

Scenario: the loop lives inline   # M2, R:mandatory_read_reintroduced
  Given SKILL.md
  When its flow section is read
  Then the 3-beat recipe (direction → freeze --by --cross → gate PASS) is narrated inline
  And no instruction mandates loading a phases/ file per phase — references are "on demand"

Scenario: pinned teachings survive the fold   # M3, R:anchor_dropped
  Given the anchor census (grammar section · setup baseline · facets · deep-check rubric · refute-read · security escalation)
  When each anchor is searched in its mapped new file
  Then every anchor resolves
  And the content-pinning suites (test_declare_grammar_doc … test_verify_deepen) stay green after their path re-aim

Scenario: budgets hold   # M4, R:skill_over_budget
  Given the byte ledger
  When SKILL.md and the phases/ pool are measured
  Then SKILL.md ≤ 9500 and sum(phases/) < 33496
  And the orchestration dedup pool floor (≤41300, test_loop_surfacing_nudges) still holds

Scenario: trees in lockstep   # M5
  Given the 3 skill trees
  When the 3 files are hashed across them
  Then each name has exactly one digest
```

</scenarios>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Grounding (the real code the contract will cite — gather BEFORE you freeze)
Touches (files · symbols · signatures): add-method/skill/add/SKILL.md (flow table §"The flow" + flag-mode para — 9500B, zero slack) · phases/{0-setup,1-specify,3-plan,4-tests}.md → phases/direction.md · phases/5-build.md → phases/build.md · phases/6-verify.md → phases/verify.md · phases/fast-lane.md → deleted · ~17 content-pinning test files re-aim paths (census: declare_grammar_doc·verify_deepen·earned_green_rubric·ground_prose·ground_wiring·review_checklist·orchestrator_build_persona·strategy_facets·stale_guide_sync·setup_run_mode·adr_audit·refute_record_required·security_escalation_disclosure·milestone_ground·skill_onramp·agent_portability·udd_design_template·tree_parity)
Context (working folder): 3 skill trees — add-method/skill/add (canonical) · .claude/skills/add · _bundled/skill/add; phases/ pool 33,496B over 7 files
Honors (patterns / conventions): skill shape tracks the engine shape (phase-collapse-3 precedent) · progressive disclosure — SKILL.md is the always-loaded surface, references load on demand · doc/skill edits do NOT repin the engine · 3-tree parity
Seams consulted: .add/SEAMS.md#three-tree-parity
Anchors the contract cites: SKILL.md · phases/direction.md · phases/build.md · phases/verify.md
Issues/Risks: SKILL.md at EXACTLY 9500B (every added byte funded by a cut) · 8-name path lists in ~10 more tests are exists()-tolerant (no re-aim needed) · roster agents (agents/add-*.md) may cite phase-guide paths — sweep in build · byte-exact rubric pins (DEEP_ANCHORS, WATCH-style) must move VERBATIM
Related intent: thin-engine-loop exit criterion 3 ("ordinary task completes with ZERO phase-guide file reads") · user goal 2026-07-17: clean+lightweight ADD, effective tokens, minimize ceremony
Ground SHA: 91230a3 — stamped by freeze

### Contract (freeze the shape — the HARD, tamper-guarded core)

```
skill surface (what an agent reads, per path)
  ordinary task -> SKILL.md ONLY (≤9500B): orient · intake · the 3-beat loop inline
                   (direction bundle → freeze --by <name> --cross → build → gate PASS)
  stuck / deep  -> phases/direction.md | build.md | verify.md   (on-demand references)
  census        -> phases/ = exactly those 3 files, ×3 trees, byte-identical
  errors (test names): guide_census_broken · anchor_dropped · skill_over_budget ·
                       mandatory_read_reintroduced
Schema: no state.json change; engine change LIMITED to the planned _PHASE_GUIDE_FILES
re-aim (3-line dict -> direction.md/build.md/verify.md + ENGINE_MD5/PKG repin; the
phase-collapse-3 comment reserved this re-aim for this task — v2 amendment)
```

Glossary deltas: none
Least-sure flag surfaced at freeze: [test] ~17 files pin guide paths/content — the census is long and some pins are byte-exact rubric anchors; a missed one costs a red-fix loop, no floor at risk.
Status: FROZEN @ v2 — approved by Tin Dang (v2: sanctioned engine dict re-aim)
Reported: yes — the freeze report (banner/ARC/SHAPE) rendered before this froze

### Build-strategy (the intended approach — SOFT: preferred; the builder self-improves and records what it ACTUALLY did at verify)
Scope (may touch): `add-method/skill/` `.claude/skills/` `add-method/src/add_method/_bundled/` `add-method/tooling/` `tmp/`
Strategy (ordered batches): 1. red suite test_skill_loop_fold.py · 2. write phases/direction.md (fold 0-setup+1-specify+3-plan+4-tests, compress hard, keep every M3 anchor verbatim) · 3. build.md + verify.md (rename + trim) · 4. delete the 4 old files + fast-lane; rewrite SKILL.md flow section inline (fund bytes from the 7-row table) · 5. re-aim the ~17 content-pinning tests · 6. sync ×3 trees · full suite · ledger
Approach (domain strategy): fold along the engine's own 3-beat seams — content moves to the beat that OWNS it, never summarized away when a test pins it verbatim
Data strategy: n/a (prose files + byte ledger; no persisted shapes)
Pattern: progressive disclosure (SKILL.md = loop, references = depth) — the same layering the Beyond section already uses for beyond.md
Optimization stance: tokens-per-ordinary-task — budget: ZERO guide reads on the happy path, SKILL.md ≤9500B, phases/ pool < 33,496B; ⚠ least-sure: direction.md compression (4 files → 1 without dropping a pinned anchor)
Persona (required): book-technical-writer (prose fold) with methodology-engine-dev consulted on test re-aims
Spawn isolation (default): inline (sequential prose surgery on one surface — inline-over-heavy-spawns)
Known-problem fixes: byte-exact rubric pins → move blocks VERBATIM then trim around them · SKILL.md zero slack → cut the flow table BEFORE writing new narration · guide-path lists in tolerant tests → leave them (exists()-skip) · roster agents cite guides → grep agents/ before closing

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every §2 scenario has exactly one red test
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_phases_census_exactly_three: arrange 3 skill trees / act glob phases/ / assert {direction,build,verify}.md only, no legacy name · covers: M1, R:guide_census_broken
  - test_skill_narrates_loop_inline_no_mandatory_read: arrange SKILL.md / act read flow section / assert 3-beat recipe present + the "load the matching phases/<n>-<phase>.md" mandate gone · covers: M2, R:mandatory_read_reintroduced
  - test_pinned_anchors_survive_fold: arrange anchor→file map / act search each / assert all resolve in direction/build/verify.md · covers: M3, R:anchor_dropped
  - test_byte_budgets: arrange ledger / act stat / assert SKILL.md ≤9500 + sum(phases/) < 33496 with exactly 3 files · covers: M4, R:skill_over_budget
  - test_three_tree_lockstep: arrange 3 trees / act md5 the 3 files / assert one digest per name · covers: M5
</test_plan>

Tests live in: `add-method/tooling/` (file: test_skill_loop_fold.py) · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

> The change plan — grounding + contract + build-strategy — was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope, follow the strategy (improve on it if the code teaches you better), and touch no test or the frozen contract.
Strategy actually used: as planned (fold → SKILL.md inline rewrite → re-aim → sync ×3 → full suite), with three recorded improvements: (1) the live content-pin census was 35 test files, not ~17 — re-aimed by a quote-anchored bulk script that skipped the frozen red suite, the engine-seam mirror, and the dead PHASES_POOL constants (§3 said leave them); (2) §3 v2 amendment ratified mid-build — the engine _PHASE_GUIDE_FILES re-aim the doc-only line forbade but the engine's own phase-collapse-3 comment reserved for this task (re-crossed by Tin Dang); (3) two wording-rubric keep-terms (Objective: · living documentation) re-homed into build.md/direction.md after the fold dropped their only carriers.
Safety rule (feature-specific): never weaken a floor pin — freeze/gate/tamper/security teachings move VERBATIM, never summarized away.
Code lives in: `./src/`
Constraints: do NOT change any test or the frozen §3 contract; stay inside the §3 Build-strategy Scope; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 3100 OK (run 2, EXIT=0); fold suite 8/8
- [x] coverage did not decrease — every deleted guide's pinned teaching re-anchored (anchor census green); 8 new tests added
- [x] no test/contract altered outside sanction — §3 v2 amendment + test re-aims ratified via re-cross --by (tamper tripwire re-snapshotted); the frozen red suite test_skill_loop_fold.py untouched
- [x] the green was EARNED, not gamed — refute-read below; the first full-suite run's 3 latent reds (wording lint · SEAMS anchor · bundle table) were FIXED at the surface, none silenced
- [x] concurrency / timing — n/a (prose + a static dict; no runtime concurrency path touched)
- [x] no exposed secrets, injection openings, or new dependencies (doc surfaces + 3-line dict)
- [x] layering holds — progressive disclosure preserved (SKILL.md = loop; references on demand); 3-tree skill parity + 4-way tooling parity green
- [x] a person reviewed and approved — Tin Dang ratified §3 v2 (engine re-aim, then PASS) at the mid-build seam, 2026-07-17

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] `python3 -m unittest test_skill_loop_fold` → Ran 8 tests, OK (7 reds flipped; ceiling pin held) — run transcript
- [x] `ls phases/` → build.md direction.md verify.md, byte-identical ×3 trees (md5 lockstep test) — shell output
- [x] SKILL.md narrates the 3-beat loop inline (freeze --by … --cross · gate PASS); references “on demand — never a mandatory read” — read in full
- [x] full suite green — 3100 OK (35 re-aimed files included) — backgrounded run log full-suite-slf2.log
- [x] byte ledger: SKILL.md 9324 ≤ 9500 · phases/ pool 23,586 < 33,496 (−30%) — wc -c

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] DIALECT — re-aimed tests pin the guides' literal paths/phrases in the exact form the files carry (quote-anchored, no loose regex weakening)
- [x] WIRING (code) — no new symbol; the re-aimed _PHASE_GUIDE_FILES is consumed by _phase_guide_path — live: `add.py guide --json` → ".claude/skills/add/phases/build.md" (was null)
- [x] DEAD-CODE (code) — none introduced; pre-existing dead PHASES_POOL constants in 8 tests left per §3 (noted in §7)
- [x] SEMANTIC (prose) — direction.md/build.md/verify.md read in full; every M3 anchor verbatim (DEEP_ANCHORS, freeze-review “seven”, security HARD-STOP teaching); wording_lint 0 findings

### Live-verify evidence — confirm the §3 PLAN grounding anchors still resolve (fill at the gate)
> Re-resolve every symbol the §3 Contract cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] every §3 anchor resolves: SKILL.md + phases/direction.md·build.md·verify.md exist ×3 trees (lockstep md5); error-name tests (guide_census_broken · anchor_dropped · skill_over_budget · mandatory_read_reintroduced intents) all green
- [x] moved since Ground SHA: _PHASE_GUIDE_FILES (add.py) re-aimed under §3 v2; SEAMS.md _declared_scope pin 5972→5971

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: red suite failed for the RIGHT reason pre-build (census/anchors/legacy, not harness); parity tests non-vacuous (all 3 trees exist); the 3 latent full-suite reds were root-caused and fixed at the SURFACE (reword/re-pin), never by gutting the guard; keep-terms restored rather than rubric-edited.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR — no secrets/injection surface; diff = markdown + a 3-line path dict; security-HARD-STOP teaching preserved verbatim in verify.md + SKILL.md
2. Concurrency: CLEAR — no runtime path
3. Architecture: CLEAR — progressive disclosure kept; ENGINE_MD5 repinned once (349901707a…), 4-way twin parity 1-digest
Verdict: PASS
Residue: none
Binding: advisory — undeclared sensitivity (method-doc task; the human ratified the §3 v2 seam incl. PASS)

### GATE RECORD
Reported: yes — the DECIDE card (banner/ARC) rendered before this outcome was recorded
Outcome: PASS
If RISK-ACCEPTED -> n/a
Reviewed by: auto-resolved on complete evidence (autonomy: auto); Tin Dang ratified the §3 v2 seam incl. PASS · date: 2026-07-17

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): guide-file reads per ordinary task (thin-engine-loop exit criterion 3 — expect ZERO on the happy path) · SKILL.md byte headroom (9324/9500) · phases/ pool 23,586/33,496.

### Decisions (ADR)
- [AI] specify — chose fold-into-3-references; rejected keep-7-add-an-index (rejected: the index is another read; files still 33.5KB) · delete-phases-entirely (rejected: deep/stuck paths still need the reference depth SKILL.md can't hold at ≤9500B)
- [human] freeze — froze §3 @ v2 (approved by Tin Dang (v2: sanctioned engine dict re-aim))
- [AI] build — approach: fold along the engine's own 3-beat seams — content moves to the beat that OWNS it, never summarized away when a test pins it verbatim
- [AI] build — data strategy: n/a (prose files + byte ledger; no persisted shapes)
- [AI] build — pattern: progressive disclosure (SKILL.md = loop, references = depth) — the same layering the Beyond section already uses for beyond.md
- [AI] build — optimization stance: tokens-per-ordinary-task — budget: ZERO guide reads on the happy path, SKILL.md ≤9500B, phases/ pool < 33,496B; ⚠ least-sure: direction.md compression (4 files → 1 without dropping a pinned anchor)
- [AI] build — strategy used: as planned (fold → SKILL.md inline rewrite → re-aim → sync ×3 → full suite), with three recorded improvements: (1) the live content-pin census was 35 test files, not ~17 — re-aimed by a quote-anchored bulk script that skipped the frozen red suite, the engine-seam mirror, and the dead PHASES_POOL constants (§3 said leave them); (2) §3 v2 amendment ratified mid-build — the engine _PHASE_GUIDE_FILES re-aim the doc-only line forbade but the engine's own phase-collapse-3 comment reserved for this task (re-crossed by Tin Dang); (3) two wording-rubric keep-terms (Objective: · living documentation) re-homed into build.md/direction.md after the fold dropped their only carriers.
- [AI] verify — gate PASS (reviewed by auto-resolved on complete evidence (autonomy: auto); Tin Dang ratified the §3 v2 seam incl. PASS)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).
- [SPEC · seeded] fast-lane routing now lives in SKILL.md flag mode — glossaries (×4 book trees + .add/GLOSSARY.md) rewritten off TASK.fast.md/fast-lane.md (evidence: wording sweep this task)
- [SPEC · open] freeze-flag label affordance — unified render still doesn't pre-seed the least-sure flag LABEL (carried from template-unify §7)

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

- [ADD · open] a guide-path census freezes SHORT: grep the whole test dir for the old names BEFORE freezing — the ~17 estimate was 35 live files / 97 reds (evidence: first targeted run)
- [ADD · open] wording-rubric keep-terms bind across folds — a deleted file's sole keep-term carrier (Objective:) must be re-homed, not dropped (evidence: wording_lint 4 findings)
- [ADD · open] a "doc-only" contract line can contradict an engine comment reserving a re-aim for the same task — grep the engine for the task slug at freeze time (evidence: §3 v2 amendment)
