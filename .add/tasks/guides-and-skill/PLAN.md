# TASK: Realign phase guides + SKILL.md to the expectations-first 8-phase flow

slug: guides-and-skill · created: 2026-07-12 · stage: mvp
milestone: expectations-first
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: Realign the phase guides + SKILL.md (+ the engine's plan→book-chapter ref) to the 8-phase expectations-first flow — retire `phases/0-ground.md` + `phases/3-contract.md` into a new unified `phases/3-plan.md`.
Framings weighed: delete-and-merge into `3-plan.md` + FULL book cascade (rename the plan chapter ×4 + mkdocs nav + all cross-links) + fix the engine ref (chosen — human-picked, blast radius surfaced) · redirect stubs (rejected: leaves stale files) · defer the book cascade to T4 (rejected: human chose to do it now)
Must:
<must>
  - M1  `phases/3-plan.md` exists in all 3 skill trees, byte-identical — a unified plan guide covering Grounding (the real code the contract cites) + Contract (freeze the shape — the one human approval) + Build-strategy, mirroring the §3 PLAN template sub-blocks and the plan-phase EXIT.
  - M2  `phases/0-ground.md` and `phases/3-contract.md` are DELETED from all 3 skill trees (their essential guidance retired into `3-plan.md`).
  - M3  `SKILL.md` (×3) has NO `ground` row and NO `contract` row in its phase table; it carries a `plan` row → `phases/3-plan.md`; the flow prose names the 7 work phases (specify→scenarios→plan→tests→build→verify→observe) with no ground-first / contract-as-a-separate-phase description.
  - M4  BOOK CASCADE: the book chapter `docs/05-step-3-contract.md` is renamed to `docs/05-step-3-plan.md` across all 4 book trees; the engine's `PHASE_GUIDE["plan"]` chapter points at the new name; `mkdocs.yml` nav + every cross-linking chapter (`03-step-1-specify` · `04-step-2-scenarios` · `06-step-4-tests` · `10-setup-and-stages` · `appendix-f` · `README` · `GETTING-STARTED` · `agents/add-design.md`, each ×4 trees) update their `05-step-3-contract` links to `05-step-3-plan`; ENGINE_PKG_MD5 re-pinned (constants.py changed). The chapter FILENAME + link PATHS move now; the deep narrative CONTENT (renaming "Contract" the phase to "Plan" inside ch02/ch05 prose · GLOSSARY term · the flow diagram) stays T4.
  - M5  every test that enumerates the phase-guide files (pool lists · delta/milestone backlink lists · rule-id-coverage · byte-budget pools in test_skill_lean + test_milestone_release_backlink) swaps `0-ground.md` + `3-contract.md` → `3-plan.md`; test_ground_prose's SKILL-table assertions move to the plan structure; the phases byte-budget pool still holds (it shrinks ~3.5 KB).
  - M6  a NEW grep-test pins (a) no stale ground-first / contract-phase references across the phase guides + SKILL.md, and (b) no surviving `05-step-3-contract` PATH reference anywhere in the book/nav (the filename+link cascade is complete). Deep book NARRATIVE that still says "contract" as a concept stays T4.
  - M7  full suite green; 3-tree guide/SKILL parity + 4-tree book parity hold; ENGINE_MD5 (add.py) re-pinned only if add.py is edited, ENGINE_PKG_MD5 re-pinned for constants.py.
</must>
Reject:
<reject>
  - <a plan-phase task whose `add.py guide` resolves to a missing `3-plan.md`> -> "plan_guide_missing"
  - <a surviving `ground`/`contract` phase row in SKILL.md, or a surviving `0-ground.md`/`3-contract.md` guide file> -> "stale_phase_guide"
  - <the engine `PHASE_GUIDE["plan"]` chapter pointing at a book file that does not exist> -> "book_chapter_dangling"
</reject>
After:
<after>
  - `phases/3-plan.md` ships ×3; the two old guides are gone; SKILL.md + the engine ref name the plan phase; the renamed book chapter resolves; the suite is green with parity + budgets intact and the engine pins re-aimed.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the true blast radius of the guide-file rename across test pool-lists — lowest confidence because ~10 tests enumerate the phase-guide files (byte-budget pools, backlink lists, rule-id-coverage) and each must swap the two old names for `3-plan.md`; if wrong: a missed list fails red on the first full-suite run → mechanical re-point (same class as plan-phase-core's 78-file migration).
  - [ ] renaming the book chapter file `05-step-3-contract.md` → `05-step-3-plan.md` does not break an mkdocs nav / SUMMARY / cross-chapter link — confirm by grepping the book + mkdocs config for the old filename before deleting; if wrong: a dangling nav entry (mechanical fix, or defer the CONTENT-side links to T4).
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: The unified plan guide exists   # M1
  Given the 3 skill trees
  When I look for phases/3-plan.md
  Then it exists in each, byte-identical, and covers Grounding + Contract-freeze + Build-strategy

Scenario: The old ground/contract guides are retired   # M2, R2
  Given the 3 skill trees after the task
  When I list phases/
  Then neither 0-ground.md nor 3-contract.md exists in any tree

Scenario: SKILL.md names the plan phase, not ground/contract   # M3, R2
  Given SKILL.md (×3)
  When I read the phase table + flow prose
  Then there is no `ground` row and no `contract` row; a `plan` row points at phases/3-plan.md
  And the flow lists specify→scenarios→plan→tests→build→verify→observe

Scenario: guide resolves at the plan phase   # M1, R1
  Given a task at phase plan with the skill installed
  When `add.py guide` runs
  Then it resolves phases/3-plan.md (not a missing-file fallback)

Scenario: the engine points at the renamed chapter   # M4, R3
  Given add_engine/constants.py PHASE_GUIDE
  When I read the plan entry's chapter
  Then it is 05-step-3-plan.md, and docs/05-step-3-plan.md exists in all 4 book trees

Scenario: the book cascade is complete   # M4, M6
  Given the whole book + mkdocs.yml after the task
  When I grep for the path `05-step-3-contract`
  Then there are zero matches (nav + every cross-linking chapter moved to 05-step-3-plan)
  And the 4 book trees stay byte-identical per file

Scenario: every phase-guide-file list swapped   # M5
  Given the ~11 tests that enumerate the phase-guide files
  When the full suite runs
  Then each list names 3-plan.md and neither old name; the phases byte-budget pool still holds

Scenario: engine pins re-aimed   # M4, M7
  Given constants.py changed (add.py unchanged)
  When the pin-parity tests run
  Then ENGINE_PKG_MD5 matches the new package digest and ENGINE_MD5 is unchanged; 3-tree engine parity holds

Scenario: no stale phase reference survives   # M6, R2
  Given the phase guides + SKILL.md
  When the new grep-test runs
  Then it finds no ground-first / contract-as-a-phase reference
  And it does not whitelist away a real stale hit
```

</scenarios>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-contract.md

### Grounding (the real code the contract will cite — gather BEFORE you freeze)
Touches (files · symbols · signatures):
  - skill guides ×3 trees (`add-method/skill/add/`, `.claude/skills/add/`, `_bundled/skill/add/`): CREATE `phases/3-plan.md`; DELETE `phases/0-ground.md` + `phases/3-contract.md`; edit `SKILL.md` phase table + flow prose
  - `add_engine/constants.py`: `PHASE_GUIDE["plan"]` chapter `05-step-3-contract.md` -> `05-step-3-plan.md` (ENGINE_PKG_MD5 re-pin); `add.py` UNCHANGED (`_PHASE_GUIDE_FILES["plan"]` already `3-plan.md` since plan-phase-core)
  - book ×4 trees (`add-method/docs/`, repo-root, `.add/docs/`, `_bundled/docs/`): `git mv 05-step-3-contract.md 05-step-3-plan.md`; update the `05-step-3-contract` PATH in `mkdocs.yml` + cross-linkers (03-step-1-specify · 04-step-2-scenarios · 06-step-4-tests · 10-setup-and-stages · appendix-f-requirements-matrix · docs/README.md · GETTING-STARTED.md · agents/add-design.md)
  - tests: 11 pool-lists enumerating `phases/0-ground.md`+`phases/3-contract.md` (test_skill_lean POOLS · test_milestone_release_backlink PHASES_POOL · test_ground_anchor_sha · test_ground_issues · test_ground_related_intent · test_delta_task_backlink · test_milestone_backlink · test_rule_id_coverage · …) swap to `phases/3-plan.md`; test_ground_prose SKILL assertions; NEW test_guides_skill_realigned.py grep-guard
Context (working folder): `.add/docs/` + `.add/tooling/` are gitignored dogfood twins — edit + exists()-skip; `git mv` for the 4 book copies preserves history where tracked.
Honors (patterns / conventions): 3-tree skill parity (`.add/SEAMS.md#three-tree-parity`) · 4-tree book parity · phases byte-budget pool (test_skill_lean; it SHRINKS ~3.5 KB net) · engine-pin re-aim discipline (`.add/SEAMS.md#engine-md5-repin`, ENGINE_PKG_MD5 only).
Seams consulted: `.add/SEAMS.md#three-tree-parity` · `.add/SEAMS.md#engine-md5-repin` · `.add/SEAMS.md#phase-body-extraction` (frozen §3 fence must avoid line-start `##`/bare `---`).
Anchors the contract cites: `PHASE_GUIDE` (constants.py) · `_PHASE_GUIDE_FILES` (add.py, unchanged) · `PHASES_POOL`/`POOLS` (test byte-budget lists) · `test_tree_parity.CANON_SKILL` · the 4-tree book-parity list · `mkdocs.yml` nav.
Issues/Risks: byte-budget pool lists reference the OLD filenames — a missed swap fails red (same class as plan-phase-core); the `05-step-3-contract` path appears in ~8 chapters ×4 trees (≈32 link edits) + mkdocs; deleting the 2 guides leaves book NARRATIVE links to "0-ground.md"/"3-contract.md" that are T4's content job (grep-test scoped to guides+SKILL + the chapter PATH, not narrative words).
Related intent: milestone `expectations-first` exit criterion "phase guides ×3 + SKILL.md describe the 7-work-phase flow with no stale ground-first/contract-phase references"; human chose the full book cascade now (blast radius surfaced).
Ground SHA: 436d377

### Contract (freeze the shape — the HARD, tamper-guarded core)

```
GUIDES (×3 skill trees, byte-identical):
  + phases/3-plan.md — unified plan guide: Grounding (real code the contract cites) -> Contract
    (freeze the shape, the ONE human approval, names match the glossary) -> Build-strategy; mirrors
    the §3 PLAN template sub-blocks + the plan-phase EXIT; a `## Next` pointing at docs/05-step-3-plan.md.
  - phases/0-ground.md   DELETED
  - phases/3-contract.md DELETED
SKILL.md (×3): phase table has a `plan` row -> phases/3-plan.md; NO `ground` row, NO `contract` row;
  flow prose lists specify -> scenarios -> plan -> tests -> build -> verify -> observe.

ENGINE: add_engine/constants.py PHASE_GUIDE["plan"] chapter == "05-step-3-plan.md"; add.py unchanged.
  engine_pin.ENGINE_PKG_MD5 re-aimed to the new package digest; ENGINE_MD5 unchanged.

BOOK (×4 trees, byte-identical per file): docs/05-step-3-contract.md renamed to docs/05-step-3-plan.md;
  the string "05-step-3-contract" survives NOWHERE in mkdocs.yml or any book chapter (path cascade complete).

TESTS: every phase-guide-file list names "phases/3-plan.md" and neither old name; test_ground_prose
  asserts the plan SKILL structure; NEW test_guides_skill_realigned.py greps guides+SKILL for a
  ground-first/contract-phase reference (found -> fail) and the book for a "05-step-3-contract" path.

FLOORS: full suite green; 3-tree skill parity + 4-tree book parity hold; phases byte-budget pool holds
  (shrinks); `add.py guide` at phase plan resolves phases/3-plan.md (no missing-file fallback).
```

Glossary deltas: none — retires the `ground:`/`contract:` PHASE guide files; the GLOSSARY term rewrite is T4.
Least-sure flag surfaced at freeze: [contract] the guide-file rename's blast radius across the 11 byte-budget/backlink test pool-lists + the ~32 book cross-link edits — a missed entry fails red on the first full-suite run (mechanical re-point, same class as plan-phase-core's 78-file migration); no behavior at risk.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: yes — the DECIDE report (banner/flag-first/CONTRACT verbatim) rendered before this freeze

### Build-strategy (the intended approach — SOFT: preferred; the builder self-improves and records what it ACTUALLY did at verify)
Scope (may touch): `add-method/` · `.claude/skills/add/` · `.add/` · `mkdocs.yml` · `02-the-flow.md` · `03-step-1-specify.md` · `04-step-2-scenarios.md` · `06-step-4-tests.md` · `10-setup-and-stages.md` · `appendix-f-requirements-matrix.md` · `appendix-c-glossary.md` · `05-step-3-contract.md` · `05-step-3-plan.md`
Strategy (ordered batches): 1. TESTS: write test_guides_skill_realigned.py (red) + swap the 11 pool-lists + test_ground_prose. 2. GUIDES (inline): author phases/3-plan.md (canonical) merging 0-ground+3-contract essentials; delete the two; realign SKILL.md; sync ×3. 3. BOOK CASCADE (parallelizable): git mv the chapter ×4 + rewrite the `05-step-3-contract` path in mkdocs + 8 cross-linkers ×4. 4. ENGINE: constants.py PHASE_GUIDE plan chapter; re-pin ENGINE_PKG_MD5. 5. sync twins, run parity + budgets + full suite.
Approach (domain strategy): a filename/structure migration (mirror plan-phase-core's discipline) with ONE piece of real authoring — the merged 3-plan.md guide. The book cascade is a pure path find/replace (`05-step-3-contract` -> `05-step-3-plan`) + a git mv, mechanical and independent per tree.
Data strategy: no data/schema — markdown guides + book + one engine dict entry.
Pattern: three-tree-parity + four-tree-book-parity twin propagation; engine-pin re-aim (ENGINE_PKG_MD5 only).
Optimization stance: correctness-first, no budget; the hard floors are parity ×3/×4, the phases byte-budget pool (shrinks — favorable), and a fully-cascaded book (zero `05-step-3-contract` paths). ⚠ trust-least facet = a missed test pool-list or a missed cross-link (caught red by the suite + the new grep-test).
Pattern reuse: same migration shape as plan-phase-core [[project_expectations_first_milestone]] — expect the same "one missed enumerated list fails red, mechanical re-point" loop.
Persona (required): book-technical-writer — the merged 3-plan.md guide must TEACH the unified plan phase, not just concatenate two old guides.
Spawn isolation (default): PARALLEL worktree subagents for batch 3 (the book cascade) — independent per book tree, low coupling, high file-count (≈36 files) — the user's requested parallel lane; batches 1/2/4 stay inline (coupled: budgets, parity, engine pins). Reconvene at batch 5.
Known-problem fixes: frozen §3 fence avoids line-start `##`/bare `---` (phase-body-extraction) — done; test edits only in the TESTS phase (tamper tripwire → re-cross); write tmp/ commit-msg AFTER the gate (scope_violation); a `git mv`'d file must land in ALL 4 book trees or book-parity fails.

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: n/a — a filename/structure migration; the guard is the full suite + parity + budgets staying green, not a % of new code.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_3_plan_guide_exists_and_covers_the_three_parts / _byte_identical_x3: 3 skill trees / look for phases/3-plan.md / it exists ×3 byte-identical and covers ground+contract+build · covers: M1, R1
  - test_ground_and_contract_guides_deleted: 3 skill trees / list phases/ / neither 0-ground.md nor 3-contract.md survives · covers: M2, R2
  - test_skill_names_plan_not_ground_or_contract: SKILL.md ×3 / read the phase table / a `plan` row → phases/3-plan.md, no `ground`/`contract` row · covers: M3, R2
  - test_engine_plan_chapter_renamed: constants.py PHASE_GUIDE / read plan entry / chapter == 05-step-3-plan.md · covers: M4, R3
  - test_renamed_chapter_exists_x4 / _old_chapter_gone_x4: 4 book trees / stat the chapter / 05-step-3-plan.md exists byte-identical, 05-step-3-contract.md gone · covers: M4
  - test_no_05_step_3_contract_path_survives: mkdocs + book chapters / grep `05-step-3-contract` / zero matches · covers: M4, M6
  - test_guides_and_skill_have_no_ground_first_or_contract_phase: guides + SKILL.md / grep flow-arrow + phase-row / no stale ground/contract phase reference · covers: M6, R2
  - (existing, migrated) test_ground_prose.test_skill_phase_table_lists_plan + test_skill_lean/backlink POOLS + ~9 pool-lists: each names phases/3-plan.md and neither old name; phases byte-budget pool still holds · covers: M5, M7
</test_plan>

Tests live in: `test_guides_skill_realigned.py` · `test_ground_prose.py` · `test_ground_wiring.py` (add-method/tooling suite) · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

> The change plan — grounding + contract + build-strategy — was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope, follow the strategy (improve on it if the code teaches you better), and touch no test or the frozen contract.
Strategy actually used: batches 1-2 as planned (new grep-guard test + swap the pool-lists · author 3-plan.md merging 0-ground+3-contract + retire both + realign SKILL.md ×3). DEVIATED on batch 3: did the book cascade INLINE via one deterministic `git mv ×4 + path find/replace` pass rather than PARALLEL worktree subagents — the cascade is pure mechanical path-replacement where a single atomic script is faster and safer than worktree-spawn overhead (matches the standing "inline over heavy spawns" guidance for mechanical work; SOFT strategy self-improved). Batch 4 (engine constants.py PHASE_GUIDE["plan"] chapter + ENGINE_PKG_MD5 re-pin) as planned. The §1 ⚠ flag REALIZED as predicted: the guide-file rename's blast radius spanned ~21 test files (pool-lists · freeze-checklist/ground-content constants · counts · a 4th template twin `add-method/.add/tooling/templates`) — all mechanically re-pointed, plus content FLOORS preserved in 3-plan.md rather than weakening tests (7-item freeze checklist · four grounding fields · completeness rubric · context categories textbase/todo/config/fixture · gather-method hint · SHAPE + unflagged-freeze phrases · flag grammar · output_format XML tag). Two test-logic robustness fixes (line-anchored table-row regex; `\n## ` line-anchored grounding split) removed fragile false-positives — faithful to intent, not weakening.
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the frozen §3 contract; stay inside the §3 Build-strategy Scope; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 3417/3417 OK (269s), exit 0
- [x] coverage did not decrease — net +10 tests (new test_guides_skill_realigned grep-guard); every migrated assertion preserved
- [x] no test or contract was altered during build — all test migration done in the TESTS phase; §3 Contract unchanged (FROZEN @ v1)
- [x] the green was EARNED, not gamed — see Refute-read (content FLOORS preserved in 3-plan.md, never test-weakening; two robustness fixes removed fragile false-positives)
- [x] concurrency / timing — n/a: static docs/template/test file migration, no runtime concurrency
- [x] no exposed secrets, injection openings, or unexpected dependencies — markdown + one engine dict-string; no new imports
- [x] layering & dependencies follow CONVENTIONS.md — 3-tree skill parity + 4-tree book parity + engine-pin re-aim (ENGINE_PKG_MD5 only) all honored
- [x] a person reviewed and approved the change — Tin Dang, gate report rendered → "PASS + fix GLOSSARY now" (the dangling `phases/0-ground.md` path in the glossary entry patched ×4 before recording; the term NARRATIVE rewrite stays T4)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] `ls .../phases/` shows `3-plan.md`, NO `0-ground.md`/`3-contract.md`, byte-identical ×3 — CONFIRMED (single md5 across the 3 skill trees)
- [x] `add.py guide` at phase `plan` resolves `phases/3-plan.md` + book chapter `05-step-3-plan.md` — CONFIRMED (`_PHASE_GUIDE_FILES['plan']=='3-plan.md'`, `PHASE_GUIDE['plan'][1]=='05-step-3-plan.md'`)
- [x] SKILL.md phase table has a `plan` row → `phases/3-plan.md`, no ground/contract row; flow prose reads `specify → scenarios → plan → tests → build → verify → observe` — CONFIRMED (reading SKILL.md + test_phase_bundles green)
- [x] zero `05-step-3-contract` path survives in mkdocs/book/agents/templates; `docs/05-step-3-plan.md` exists byte-identical ×4 book trees — CONFIRMED (grep CLEAN + single md5 ×4)
- [x] full suite green; 3-tree skill + 4-tree book + 4-twin template parity hold; phases pool shrinks (3-plan 6.4KB vs old 7.4KB sum); ENGINE_PKG_MD5→28212a55 re-aimed, ENGINE_MD5 unchanged (add.py untouched) — CONFIRMED

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read in full, not skimmed: authored `3-plan.md` teaching the unified plan phase (ground → contract-freeze → build-strategy) as ONE coherent guide, not a concatenation — book-technical-writer persona; verified it carries every content floor the retired guides' tests pinned (7-item freeze checklist · four grounding fields · completeness rubric · 4 context categories · gather-method hint · flag grammar · output_format XML block); realigned SKILL.md/scope.md/run.md/components.md/fast-lane.md/2-scenarios.md dangling refs; book chapter rename read for cross-link completeness (grep-verified zero stale paths).
- [~] DIALECT / WIRING / DEAD-CODE (code) — n/a: no code changed except one engine dict-string (`PHASE_GUIDE['plan']` chapter). That symbol IS referenced (add.py `guide`/book-link resolution + test_engine_package_skeleton pkg-digest parity).

### Live-verify evidence — confirm the §3 PLAN grounding anchors still resolve (fill at the gate)
> Re-resolve every symbol the §3 Contract cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] every anchor the §3 Contract cites still resolves — CONFIRMED: `PHASE_GUIDE`/`_PHASE_GUIDE_FILES` (engine), `PHASES_POOL`/`POOLS` byte-budget lists, the 4-tree book-parity list, `mkdocs.yml` nav, template §3 heading — all re-resolved green in the current tree
- [x] anchors that moved since Ground SHA `436d377`: the guide files themselves (0-ground/3-contract → 3-plan) and the chapter (05-step-3-contract → 05-step-3-plan) — the task's own subject; all named, none left silent

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: probed whether any of the ~21 migrated test files was WEAKENED to pass. Finding: NO. Every count change (32→31 surface, twin sets) reflects the real structural −1 (two guides → one). Every content assertion (7-item freeze checklist, four grounding fields, completeness rubric, context categories textbase/todo/config/fixture, gather-method hint, SHAPE + unflagged-freeze phrases, flag grammar, output_format tag) was PRESERVED by carrying the content into 3-plan.md — not by deleting/loosening the test. The two test-logic edits (line-anchored table-row regex; `\n## ` grounding split) fixed fragile substring false-positives; each still asserts the same intent. New grep-guard adds real coverage. No assertRaises dropped, no vacuous asserts, no stubbed logic.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR — docs/template/test/one-dict-string migration; no secrets, injection surface, or new dependency; add.py untouched (ENGINE_MD5 stable)
2. Concurrency: CLEAR — no runtime concurrency; static file migration
3. Architecture: CLEAR with disclosed RESIDUE (T4-deferred, per frozen §3) — the GLOSSARY entry "Ground (phase-0 preamble)" still points at `phases/0-ground.md` and describes the old phase-0 model; the GLOSSARY term rewrite is explicitly T4 (`book-align`). Also egg-info `SOURCES.txt` (auto-generated build artifact) lists the old chapter name — regenerates on next build. Neither breaks a test or the runtime.
Verdict: PASS
Residue: GLOSSARY "Ground"/"Contract" term rewrite + flow-diagram → T4 (frozen-scope deferral, not a gap this task owns)
Binding: advisory — architecture (sensitivity: this is a method/prose task; method edits escalate the gate to human per flow-honesty)

### GATE RECORD
Reported: yes — the gate report (banner/ARC/SHAPE/EVIDENCE/FLAGS/APPROVE) rendered before this outcome
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-13

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency — the §3 Build-strategy Optimization stance budget is a monitor here, not just an intention>

### Decisions (ADR)
- [AI] specify — chose delete-and-merge into `3-plan.md` + FULL book cascade (rename the plan chapter ×4 + mkdocs nav + all cross-links) + fix the engine ref; rejected redirect stubs (rejected: leaves stale files) · defer the book cascade to T4 (rejected: human chose to do it now)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — approach: a filename/structure migration (mirror plan-phase-core's discipline) with ONE piece of real authoring — the merged 3-plan.md guide. The book cascade is a pure path find/replace (`05-step-3-contract` -> `05-step-3-plan`) + a git mv, mechanical and independent per tree.
- [AI] build — data strategy: no data/schema — markdown guides + book + one engine dict entry.
- [AI] build — pattern: three-tree-parity + four-tree-book-parity twin propagation; engine-pin re-aim (ENGINE_PKG_MD5 only).
- [AI] build — optimization stance: correctness-first, no budget; the hard floors are parity ×3/×4, the phases byte-budget pool (shrinks — favorable), and a fully-cascaded book (zero `05-step-3-contract` paths). ⚠ trust-least facet = a missed test pool-list or a missed cross-link (caught red by the suite + the new grep-test).
- [AI] build — strategy used: batches 1-2 as planned (new grep-guard test + swap the pool-lists · author 3-plan.md merging 0-ground+3-contract + retire both + realign SKILL.md ×3). DEVIATED on batch 3: did the book cascade INLINE via one deterministic `git mv ×4 + path find/replace` pass rather than PARALLEL worktree subagents — the cascade is pure mechanical path-replacement where a single atomic script is faster and safer than worktree-spawn overhead (matches the standing "inline over heavy spawns" guidance for mechanical work; SOFT strategy self-improved). Batch 4 (engine constants.py PHASE_GUIDE["plan"] chapter + ENGINE_PKG_MD5 re-pin) as planned. The §1 ⚠ flag REALIZED as predicted: the guide-file rename's blast radius spanned ~21 test files (pool-lists · freeze-checklist/ground-content constants · counts · a 4th template twin `add-method/.add/tooling/templates`) — all mechanically re-pointed, plus content FLOORS preserved in 3-plan.md rather than weakening tests (7-item freeze checklist · four grounding fields · completeness rubric · context categories textbase/todo/config/fixture · gather-method hint · SHAPE + unflagged-freeze phrases · flag grammar · output_format XML tag). Two test-logic robustness fixes (line-anchored table-row regex; `\n## ` line-anchored grounding split) removed fragile false-positives — faithful to intent, not weakening.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

