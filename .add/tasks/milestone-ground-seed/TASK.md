# TASK: Milestone Ground seed: specify projects from a milestone-level Ground

slug: milestone-ground-seed · created: 2026-07-12 · stage: mvp
milestone: expectations-first
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: A milestone-level `## Ground` — shared real-code context gathered ONCE per milestone — that each task's `specify` projects its expectations from, so tasks stop re-grounding shared context.
Framings weighed: thin `## Ground` after Scope + a specify-guide cue, NO engine enforcement (chosen) · template-only, no guide cue (rejected: exit criterion names the guide too) · engine-validated milestone-Ground (rejected: milestone Out explicitly defers a heavy validator)
Must:
<must>
  - M1  `MILESTONE.md.tmpl` (all 3 trees, byte-identical) carries a `## Ground` section placed immediately after `## Scope` and before `## Shared decisions` — so tasks read it before their §1.
  - M2  the `## Ground` section is THIN: it reuses the task-Grounding vocabulary at milestone altitude (a `Touches (shared files · symbols)` line, an `Anchors` line, an `Honors (conventions)` line, an `Issues/Risks (shared)` line), gathered once, task-delta — never a per-task grounding table. [v2: `Honors (conventions)` replaces the v1 label — the v1 spelling tripped the slang guard; `Honors` mirrors the task-Grounding field.]
  - M3  the `specify` phase guide (`phases/1-specify.md`, all 3 skill trees) names projecting the §1 expectations from the milestone `## Ground` + the request (the TASK.md §1 template cue already carries this from plan-phase-core; the guide gains the matching line).
  - M4  the milestone-drafting guide `scope.md` names the new `## Ground` among the MILESTONE.md sections it drafts; `test_scope_loop`'s named-section count moves 9 → 10.
  - M5  prose/template-only: no `add.py`/`constants.py` engine logic reads or validates the milestone Ground — ENGINE_MD5 and ENGINE_PKG_MD5 are unchanged (a heavy validator is deferred, per the milestone Out).
  - M6  full suite green; the 3 `MILESTONE.md.tmpl` copies stay byte-identical; a new red→green test pins the `## Ground` section (presence + the four field labels + placement after Scope) and the specify-guide cue.
</must>
Reject:
<reject>
  - <a MILESTONE.md.tmpl missing the `## Ground` section after this task> -> "milestone_ground_absent"
  - <the 3 MILESTONE.md.tmpl copies drifting from byte-identical> -> "milestone_tmpl_drift"
  - <this task editing add.py/constants engine logic so ENGINE_MD5 changes> -> "engine_touched"
</reject>
After:
<after>
  - `MILESTONE.md.tmpl` ×3 carry a thin `## Ground` after Scope; `scope.md` drafts it; the specify guide + §1 template cue both project from it; the suite is green and the engine digest is unchanged.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ `## Ground` placement (after `## Scope`, before `## Shared decisions`) and the exact field vocabulary — lowest confidence because the milestone-section ordering is pinned by `test_scope_loop` and drafted in order by `scope.md`; if wrong: the section lands where the drafting guide/test doesn't expect it → a re-point of the test + guide (mechanical). Human-confirmed 2026-07-12 (thin, after Scope).
  - [ ] the `specify`-guide cue belongs to THIS task, not T3 `guides-and-skill` — the exit criterion attributes the specify cue to milestone-ground-seed; T3 does the FULL guide/SKILL realign. If wrong: a one-line overlap with T3, harmless (idempotent).
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: Ground section present after Scope   # M1
  Given the canonical MILESTONE.md.tmpl
  When I scan its `## ` headings in order
  Then a `## Ground` heading appears immediately after `## Scope`
  And it appears before `## Shared decisions & glossary deltas`

Scenario: Ground section is thin with the milestone-altitude vocabulary   # M2
  Given the `## Ground` section body in MILESTONE.md.tmpl
  When I read its field labels
  Then it carries `Touches (shared files · symbols):`, `Anchors:`, `Honors (conventions):`, and `Issues/Risks (shared):`
  And it contains no per-task grounding table (no `- [ ] <slug>` rows)

Scenario: Specify guide cues projecting from the milestone Ground   # M3
  Given the canonical phases/1-specify.md
  When I read it
  Then it names projecting the §1 expectations from the milestone `## Ground` + the request

Scenario: scope.md drafts the new section and the count test tracks it   # M4
  Given the milestone-drafting guide scope.md and test_scope_loop
  When I read the drafted-section list
  Then scope.md names `## Ground` among the MILESTONE.md sections it drafts
  And test_scope_loop asserts the named-section count is 10 (was 9)

Scenario: engine untouched — prose/template only   # M5
  Given this task's committed changes
  When I compute md5(add.py) and the add_engine package digest
  Then both equal engine_pin.ENGINE_MD5 and ENGINE_PKG_MD5 unchanged from before the task
  And no add.py/constants.py logic reads or validates the milestone Ground

Scenario: suite green and the 3 templates stay byte-identical   # M6
  Given the full test suite after the build
  When it runs
  Then it is green, the new milestone-Ground test passes, and md5 of the 3 MILESTONE.md.tmpl copies are identical

Scenario: a template missing Ground is caught   # R1
  Given a MILESTONE.md.tmpl with no `## Ground` heading
  When the milestone-Ground test runs
  Then it fails, reporting the missing section ("milestone_ground_absent")
  And no other section's assertions are silently relaxed to compensate

Scenario: template drift across the 3 trees is caught   # R2
  Given the 3 MILESTONE.md.tmpl copies where one differs by a byte
  When the byte-parity test runs
  Then it fails ("milestone_tmpl_drift")
  And the canonical copy is unchanged

Scenario: an engine edit under this prose task is caught   # R3
  Given add.py changed so md5(add.py) ≠ ENGINE_MD5
  When the prose-only engine-untouched guard runs
  Then it fails ("engine_touched")
  And the guard does not re-pin the digest to pass itself
```

</scenarios>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-contract.md

### Grounding (the real code the contract will cite — gather BEFORE you freeze)
Touches (files · symbols · signatures):
  - `add-method/tooling/templates/MILESTONE.md.tmpl` + 2 twins (`.add/tooling/templates/` gitignored dogfood · `add-method/src/add_method/_bundled/tooling/templates/`) — insert `## Ground` between `## Scope` (line 12) and `## Shared decisions & glossary deltas` (line 24)
  - `add-method/skill/add/phases/1-specify.md` + 2 twins (`.claude/skills/add/phases/` · `_bundled/skill/add/phases/`) — add one line cueing "project §1 from the milestone `## Ground` + the request"
  - `add-method/skill/add/scope.md` + 2 twins (`.claude/skills/add/` · `_bundled/skill/add/`) — name `## Ground` among the MILESTONE.md sections the drafting step lists
  - `add-method/tooling/test_scope_loop.py`: `TEMPLATE_SECTIONS` (append `"ground"` → len 10) · `test_covers_all_nine_template_sections` → `test_covers_all_ten_template_sections`
Context (working folder): `.add/tooling/templates/MILESTONE.md.tmpl` is GITIGNORED (dogfood twin) yet byte-parity-pinned by `test_milestone_uiux_hint` — edit it too; use an `exists()`-skip in the new test for any gitignored twin.
Honors (patterns / conventions): 3-tree skill/template byte-parity (`.add/SEAMS.md#three-tree-parity`); prose/template-only ⇒ engine digest UNCHANGED (`.add/SEAMS.md#engine-md5-repin` must NOT fire); `test_scope_loop` checks per-token presence, not a numeric count.
Seams consulted: `.add/SEAMS.md#three-tree-parity` (skill + template twins) · `.add/SEAMS.md#engine-md5-repin` (guard it stays quiet — no engine edit).
Anchors the contract cites: `MILESTONE.md.tmpl` `## Scope` / `## Shared decisions & glossary deltas` headings · `TEMPLATE_SECTIONS` · `test_tree_parity.CANON_SKILL` (whole-tree rglob) · the 3-tmpl-tree list in `test_milestone_uiux_hint`.
Issues/Risks: gitignored `.add` twin silently skipped by git but pinned by the tmpl test → must edit + exists()-skip; scope-token grammar (first physical line only) → declare directory tokens; tmp/ commit-msg write is a post-gate scope_violation trap (write it after the gate).
Related intent: milestone `expectations-first` goal — "no re-grounding shared context per task"; the milestone `## Ground` is the once-gathered source `specify` projects from. Reuses the existing GLOSSARY `Ground` / `Grounding map` terms (no new term).
Ground SHA: cee79a0

### Contract (freeze the shape — the HARD, tamper-guarded core)

```
MILESTONE.md.tmpl — insert VERBATIM between `## Scope` and `## Shared decisions & glossary deltas`
(headings below indented one space to avoid the §-scanner's line-start terminator — insert them flush-left):

 ## Ground   (shared real-code context — gathered ONCE; every task's specify projects from this)
 Touches (shared files · symbols): <the code every task in this milestone lands in — gathered once, task-delta>
 Anchors: <the shared symbols tasks may cite — the floor each task's contract builds on>
 Honors (conventions): <PROJECT.md · CONVENTIONS.md · SEAMS.md rules every task honors>
 Issues/Risks (shared): <traps in the shared code that feed each task's §1 expectations>

phases/1-specify.md — carries a line naming: project the §1 expectations from the milestone Ground section + the request (light, not re-grounded per task).
scope.md — the drafting step names the Ground section (drafted from the milestone's shared real code) among the MILESTONE.md sections.
test_scope_loop — TEMPLATE_SECTIONS contains "ground"; the coverage test asserts all 10 sections.

Byte-parity: MILESTONE.md.tmpl ×3 identical · phases/1-specify.md ×3 identical · scope.md ×3 identical.
Engine floor: md5(add.py) == ENGINE_MD5 and add_engine digest == ENGINE_PKG_MD5 (UNCHANGED — prose/template only).
```

Glossary deltas: none — "milestone Ground" reuses the existing `Ground` / `Grounding map` terms at milestone altitude.
Least-sure flag surfaced at freeze: [spec/contract] the `## Ground` placement (after `## Scope`) + the four field labels — human-confirmed thin/after-Scope on 2026-07-12; if the ordering is wrong it is a mechanical re-point of `test_scope_loop` + `scope.md`, no behavior at risk.
Status: FROZEN @ v2 — approved by Tin Dang
Reported: yes — the DECIDE report (banner/flag-first/CONTRACT verbatim) rendered before this freeze

### Build-strategy (the intended approach — SOFT: preferred; the builder self-improves and records what it ACTUALLY did at verify)
Scope (may touch): `add-method/` · `.claude/skills/add/` · `.add/tooling/templates/`   <directory tokens cover their subtrees: add-method/ = templates+skill+_bundled+tooling/test_scope_loop; .claude/skills/add/ = dogfood skill; .add/tooling/templates/ = gitignored MILESTONE twin>
Strategy (ordered batches): 1. write the red test (test_milestone_ground.py) + bump test_scope_loop; 2. insert the frozen `## Ground` block into MILESTONE.md.tmpl ×3; 3. add the specify cue to phases/1-specify.md ×3; 4. name `## Ground` in scope.md ×3; 5. sync twins + run test_tree_parity/test_bundle_parity/test_milestone_uiux_hint; 6. confirm md5(add.py)==ENGINE_MD5 (engine untouched).
Approach (domain strategy): additive template + guide prose — mirror the task-level Grounding vocabulary UP to milestone altitude (gathered once, shared) rather than inventing new fields; keeps the mental model identical between MILESTONE `## Ground` and TASK §3 `### Grounding`.
Data strategy: no data/schema — pure markdown template + guide text; the "shape" is the literal `## Ground` block frozen above.
Pattern: the three-tree-parity twin convention (`.add/SEAMS.md#three-tree-parity`) — every template/skill edit propagates to its twins before the gate.
Optimization stance: correctness-first, no budget — the hard floors are byte-parity ×3 and engine-digest-unchanged; ⚠ trust-least facet = the gitignored `.add/tooling/templates/` twin sync (silent to git, caught only by the tmpl-parity test).
Persona (required): book-technical-writer — the method prose IS the product surface; the `## Ground` wording must teach, not just slot in.
Spawn isolation (default): inline (no spawn) — small, sequential, single-context prose edit; a worktree/subagent would cost more than the work (inline-over-heavy-spawns).
Known-problem fixes: gitignored `.add` twin → edit it AND exists()-skip in the new test; scope line reads first physical line only → all tokens on one line; write the tmp/ commit-msg AFTER the gate (post-gate scope_violation trap).

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + Reject has an asserting test (behavior, not internals).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_ground_section_present: assert `## Ground` in MILESTONE.md.tmpl · covers M1, R1(milestone_ground_absent)
  - test_ground_placed_after_scope_before_shared_decisions: index(## Scope) < index(## Ground) < index(## Shared decisions) · covers M1
  - test_ground_is_thin_with_altitude_vocabulary: the 4 field labels present in the Ground block · covers M2
  - test_ground_is_not_a_per_task_table: no `- [ ]` rows in the Ground block · covers M2
  - test_ground_names_gathered_once: "once" in the Ground block · covers M2
  - test_specify_guide_cues_projecting_from_milestone_ground: "ground" + "project" in phases/1-specify.md · covers M3
  - test_scope_guide_names_ground_section: literal `## Ground` in scope.md (not the incidental substring) · covers M4
  - test_covers_all_ten_template_sections (test_scope_loop): TEMPLATE_SECTIONS 11 tokens/10 sections incl "ground" · covers M4
  - test_*_byte_identical (×3 tmpl/specify/scope): one md5 per trio · covers M6, R2(milestone_tmpl_drift)
  - test_engine_untouched: md5(add.py ×3) == ENGINE_MD5 · covers M5, R3(engine_touched)
</test_plan>

Tests live in: `add-method/tooling/`   (`test_milestone_ground.py` new + `test_scope_loop.py` bump) · MUST run red (missing implementation) before Build.
RED confirmed: 6 failures for the right reason (## Ground absent · specify cue absent · scope.md names no `## Ground`); byte-parity + engine-untouched already green.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

> The change plan — grounding + contract + build-strategy — was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope, follow the strategy (improve on it if the code teaches you better), and touch no test or the frozen contract.
Strategy actually used: <fill at VERIFY — the strategy you ACTUALLY used (or "as planned"); harvested into the §7 Decisions (ADR) block as the [AI] build decision>
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the frozen §3 contract; stay inside the §3 Build-strategy Scope; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite `Ran 3408 tests ... OK` (275s); test_milestone_ground + test_scope_loop + slang guard green
- [x] coverage did not decrease — new test_milestone_ground.py (11 tests) + test_scope_loop bump; every Must/Reject asserted
- [x] no test or contract was altered during build — the v2 label change went through a documented change request (phase plan → re-freeze v2), not a silent build-time edit
- [x] the green was EARNED — refute-read below: budgets met by COMPRESSION under the existing frozen targets (never bumped); the scope.md test was STRENGTHENED (vacuous 'ground' substring → literal `## Ground`)
- [x] concurrency / timing — n/a: template + guide prose, no runtime code
- [x] no exposed secrets / injection / deps — markdown-only edits, stdlib-only test
- [x] layering & dependencies — 3-tree byte-parity held (MILESTONE.md.tmpl · 1-specify.md · scope.md); md5(add.py)==ENGINE_MD5 (engine untouched)
- [x] a person reviewed and approved — Tin Dang approved the v1 freeze + the v2 label change request (2026-07-12)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] a rendered `MILESTONE.md.tmpl` shows `## Ground` between `## Scope` and `## Shared decisions` with the 4 labels (Touches · Anchors · Honors (conventions) · Issues/Risks (shared)) — confirmed by reading the canonical template
- [x] `add.py new-milestone` scaffolds a MILESTONE.md that includes `## Ground` (after Scope, before Shared decisions, all 4 labels) — CONFIRMED live in a throwaway project
- [x] `phases/1-specify.md` Converge step now reads: draft §1 by PROJECTING from the milestone `## Ground` + the request — confirmed by reading the guide
- [x] `scope.md` Position-the-goal step now records the grounding as the milestone's `## Ground` section (persists, not discarded) — confirmed by reading it
- [x] the 3 copies of MILESTONE.md.tmpl / 1-specify.md / scope.md are byte-identical, md5(add.py)==ENGINE_MD5 — confirmed by parity + engine-untouched tests green

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] DIALECT — n/a: no data-value dialect; the spec's 'examples' are markdown section/field names, asserted verbatim by test_milestone_ground
- [x] WIRING — n/a (no code symbols): the `## Ground` section is wired into the workflow via new-milestone scaffolding + the specify guide + scope.md references
- [x] DEAD-CODE — n/a (no code): no orphaned prose — the `## Ground` block is referenced by both guides and scaffolds live
- [x] SEMANTIC (prose / non-code) — read in full: the `## Ground` block teaches (gathered ONCE, projected-from); the specify Converge cue + scope.md persist-sentence are coherent; NOTE: scope.md's Position-the-goal fields (Touches/Context/Honors/Anchors) differ slightly from the `## Ground` fields (Touches/Anchors/Honors/Issues-Risks) — a prose-harmonization opportunity for T3, disclosed, not a defect

### Live-verify evidence — confirm the §3 PLAN grounding anchors still resolve (fill at the gate)
> Re-resolve every symbol the §3 Contract cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] the §3 Contract cites markdown anchors (## Scope / ## Shared decisions headings · TEMPLATE_SECTIONS · CANON_SKILL rglob · the 3-tmpl-tree list) — all resolve; exercised green by the suite
- [x] one anchor changed by CHANGE REQUEST since Ground SHA cee79a0: the field label `Conventions/Seams:` → `Honors (conventions):` (v2) — named here, re-frozen, not left silent

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: (1) budget-gaming — CONFIRMED honest: the phases pool / reference pool / whole-tree budgets were met by COMPRESSING prose under the EXISTING frozen targets (33284 / 51885 / 145974), never by raising a target (lean-over-budget-bump). (2) vacuous asserts — the scope.md check was STRENGTHENED from the incidental 'ground' substring (already present via 'grounding') to the literal `## Ground` section reference. (3) contract-tamper — the v2 label change is a documented change request (phase plan → amend → re-freeze @ v2 → human-approved), not a silent build-time edit. (4) dead prose — the `## Ground` section scaffolds live into every new MILESTONE.md (verified) and is referenced by the specify guide + scope.md.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR — template + guide prose; no auth/secret/injection/input surface.
2. Concurrency: CLEAR — no runtime code; markdown only.
3. Architecture: CLEAR — a milestone-altitude `## Ground` mirroring the task-Grounding vocabulary; NO engine change (md5(add.py) unchanged); no new coupling. RESIDUE (advisory): scope.md's goal-grounding fields vs the `## Ground` fields diverge slightly — harmonize in T3 guides-and-skill.
Verdict: PASS
Residue: minor prose-vocabulary divergence (scope.md vs `## Ground`) → T3; no behavioral residue
Binding: advisory — prose/template (not mechanical-gate-relax)

### GATE RECORD
Reported: yes — the DECIDE report (banner/ARC/flag-first) rendered before this outcome was recorded
Outcome: PASS
Reviewed by: auto-gate on complete evidence (autonomy: auto); human approved the freeze v1 + the v2 label change request — Tin Dang · date: 2026-07-12

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency — the §3 Build-strategy Optimization stance budget is a monitor here, not just an intention>

### Decisions (ADR)
- [AI] specify — chose thin `## Ground` after Scope + a specify-guide cue, NO engine enforcement; rejected template-only, no guide cue (rejected: exit criterion names the guide too) · engine-validated milestone-Ground (rejected: milestone Out explicitly defers a heavy validator)
- [human] freeze — froze §3 @ v2 (approved by Tin Dang)
- [AI] build — approach: additive template + guide prose — mirror the task-level Grounding vocabulary UP to milestone altitude (gathered once, shared) rather than inventing new fields; keeps the mental model identical between MILESTONE `## Ground` and TASK §3 `### Grounding`.
- [AI] build — data strategy: no data/schema — pure markdown template + guide text; the "shape" is the literal `## Ground` block frozen above.
- [AI] build — pattern: the three-tree-parity twin convention (`.add/SEAMS.md#three-tree-parity`) — every template/skill edit propagates to its twins before the gate.
- [AI] build — optimization stance: correctness-first, no budget — the hard floors are byte-parity ×3 and engine-digest-unchanged; ⚠ trust-least facet = the gitignored `.add/tooling/templates/` twin sync (silent to git, caught only by the tmpl-parity test).
- [AI] build — strategy used: as planned
- [AI] verify — gate PASS (reviewed by auto-gate on complete evidence (autonomy: auto); human approved the freeze v1 + the v2 label change request — Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

