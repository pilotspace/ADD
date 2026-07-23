# TASK: add a drafted-blank ## Strategy slot to MILESTONE.md.tmpl + engine handling

slug: strategy-section · created: 2026-07-16 · stage: mvp
milestone: strategy-intake
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: a drafted-blank `## Strategy` slot in the milestone template
Framings weighed: drafted-blank template section like Close/Release (chosen) · an engine-parsed required section · a separate STRATEGY.md file
Must:
<must>
  - M1 the milestone template (`MILESTONE.md.tmpl`) carries a `## Strategy` section, drafted-blank (placeholder guidance + `<...>` slots, exactly like `## Close` / `## Release steps`)
  - M2 a milestone created via `add.py new-milestone` renders the `## Strategy` slot into its `MILESTONE.md`
  - M3 the `## Strategy` section is placed OUTSIDE the engine-parsed spans (`## Tasks`, `## Exit criteria`) so the task-DAG parse and `milestone-confirm`/`check` are byte-behaviour-unchanged
  - M4 all three `MILESTONE.md.tmpl` twins (source · `_bundled` · `.add` mirror) stay byte-identical
</must>
Reject:
<reject>
  - R1 a new-milestone flow that HOLDS or warns on an UNFILLED `## Strategy` -> "strategy_must_stay_soft" (drafted-blank is valid; Strategy is advisory, never a gate)
  - R2 placing `## Strategy` INSIDE the `## Tasks` span (between `## Tasks` and the next `## `) so the depends-on/DAG parse changes -> "tasks_parse_corrupted"
</reject>
After:
<after>
  - every new `MILESTONE.md` carries a drafted-blank `## Strategy` slot; existing milestone parsing (Tasks DAG · confirm · check) is unchanged; the 3 template twins are byte-identical
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the engine does NOT need to PARSE `## Strategy` for this task — lowest confidence because add.py already parses some milestone `## ` sections (Tasks DAG @ ~1336; a pre-confirm section check @ ~4828); if wrong: engine section-handling creeps in and this task grows past a template edit
  - [ ] `## Strategy` placed AFTER `## Exit criteria` (before `## Close`) leaves every engine-parsed span intact — confirm by a red test on the Tasks-DAG parse + a live new-milestone
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: new milestone renders the Strategy slot   # M1, M2
  Given a project with the strategy-aware MILESTONE.md.tmpl
  When I run `add.py new-milestone demo`
  Then the created MILESTONE.md contains a `## Strategy` heading, drafted-blank
  And the `## Tasks` and `## Exit criteria` sections are still present and parseable

Scenario: the Tasks DAG parse is unchanged   # M3, R2
  Given a MILESTONE.md with a `## Strategy` section and N depends-on task rows
  When the engine parses the `## Tasks` span for the DAG
  Then it reads exactly the N task rows
  And no `## Strategy` line is mistaken for a task row

Scenario: Strategy stays soft — never a gate   # R1
  Given a milestone whose `## Strategy` slot is left drafted-blank
  When I run `add.py milestone-confirm` and `add.py check`
  Then both succeed with no strategy-related hold or warning
  And the milestone confirms exactly as before this section existed

Scenario: the three template twins stay identical   # M4
  Given the strategy-aware MILESTONE.md.tmpl
  When I md5 the source, _bundled, and .add-mirror copies
  Then all three hashes are equal
```

</scenarios>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Grounding (the real code the contract will cite — gather BEFORE you freeze)
Touches (files · symbols · signatures): `add-method/tooling/templates/MILESTONE.md.tmpl` (+ `_bundled` + `.add` twins) — insert one `## Strategy` section between the `## Exit criteria` and `## Close — ship review` headings. NO `add.py` symbol: `new-milestone` renders the template verbatim, so the slot flows without an engine edit.
Context (working folder): `.add/milestones/*/MILESTONE.md` (rendered instances) · `scope.md` (the guide that FILLS Strategy — a later task, not this one).
Honors (patterns / conventions): the drafted-blank section convention of `## Close` / `## Release steps` (placeholder `<...>` slots + a guidance `>` blockquote); the 3-tree template-parity pattern.
Seams consulted: none (no scope-token grammar touched).
Anchors the contract cites: the `## Exit criteria` heading (insert AFTER) · the `## Close — ship review` heading (insert BEFORE) · the `## Tasks` DAG-parse span (add.py ~1336).
Issues/Risks: add.py reads the `## Tasks` span up to the next `## ` heading (~1336) — a section placed INSIDE that span would be mis-read as a task row (R2). Safe placement is AFTER `## Exit criteria`. No engine parse consumes `## Strategy` this task.
Related intent: the `strategy-intake` milestone rationale (the persona-led strategy session); GLOSSARY term "milestone strategy".
Ground SHA: 5cd78b1 — stamped by freeze

### Contract (freeze the shape — the HARD, tamper-guarded core)

```
MILESTONE.md.tmpl gains ONE section, inserted between `## Exit criteria (...)` and
`## Close — ship review (...)`:

    ## Strategy   (AI-drafted WITH the human — the optimized task plan; SOFT/advisory like §5; drafted-blank for a micro/--fast milestone)
    > The persona-led strategy over THIS milestone's tasks — sequencing, freeze-first contracts,
    > parallel waves, the first unblocking slice, tradeoffs named. SOFT: the preferred plan; the
    > loop may deviate and records what it did. Drafted-blank is valid (risk-proportional).
    - Approach (sequencing): <risk-first | dependency-first | first-slice-unblocks — and WHY>
    - Freeze-first: <the shared/risky contract to freeze before the rest>
    - Waves (parallel): <task slugs that can run concurrently behind frozen contracts — or "sequential">
    - Tradeoffs weighed: <alternative decompositions considered + why this one>

Invariants (HARD):
  - placement AFTER `## Exit criteria`, BEFORE `## Close` — NEVER inside the `## Tasks` span
  - the engine does NOT parse or gate on `## Strategy` (no reject code, no confirm/advance/check hold)
  - all 3 MILESTONE.md.tmpl twins byte-identical
  - no add.py edit, no ENGINE_MD5 repin (template renders verbatim)
```

Glossary deltas: milestone strategy: the SOFT, persona-led optimized task plan recorded in a milestone's `## Strategy` section.
Least-sure flag surfaced at freeze: whether placing `## Strategy` after `## Exit criteria` leaves the `## Tasks` DAG parse (add.py ~1336) and the pre-confirm section scan (~4828) byte-behaviour-unchanged — a dedicated red test asserts the DAG reads exactly N task rows and confirm/check stay clean [contract/test]
Status: FROZEN @ v1 — approved by tindang
Reported: <yes — the freeze report (banner/ARC/SHAPE) rendered before this froze | no>

### Build-strategy (the intended approach — SOFT: preferred; the builder self-improves and records what it ACTUALLY did at verify)
Scope (may touch): `add-method/tooling/templates/MILESTONE.md.tmpl` · `add-method/src/add_method/_bundled/tooling/templates/MILESTONE.md.tmpl` · `.add/tooling/templates/MILESTONE.md.tmpl` · `add-method/tooling/test_strategy_section.py`
Strategy (ordered batches): 1. write the RED test (renders the slot · Tasks-DAG reads exactly N rows · confirm/check clean · 3-twin md5 parity) 2. add `## Strategy` to the SOURCE template after `## Exit criteria` 3. sync the 2 twins byte-for-byte 4. green.
Approach (domain strategy): a drafted-blank template section mirroring the `## Close` / `## Release steps` convention — NO engine parsing (renders verbatim via `new-milestone`), so zero `engine_pin` churn; derives from the "drafted-blank section like Close/Release" framing chosen in §1.
Data strategy: n/a — static template text; the rendered `MILESTONE.md` instance is the only artifact, and it must agree with the Contract's placement invariants.
Pattern: the existing drafted-blank section convention (`## Close`, `## Release steps`) + the 3-tree template-parity pattern.
Optimization stance: correctness-first, no perf budget — ⚠ the facet I trust least is placement NOT disturbing the `## Tasks` DAG parse; a dedicated red test asserts the parse reads exactly N task rows.
Persona (required): methodology-engine-dev — the method/engine domain stance (advisory, never lowers a gate).
Spawn isolation (default): inline — sequential template edit, no subagent spawn (per the inline-build preference).
Known-problem fixes: Tasks-DAG parse truncation → place AFTER `## Exit criteria` + test the parse reads exactly N rows · twin drift → md5 3-parity test · covert-gate creep → test milestone-confirm/check stay clean with Strategy drafted-blank.

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the 4 §2 scenarios (M1–M4, R1–R2)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_strategy_slot_present_and_placed: assert MILESTONE.md.tmpl carries `## Strategy` placed AFTER `## Exit criteria` and BEFORE `## Close` · covers: M1, M2
  - test_strategy_is_drafted_blank: assert the `## Strategy` block has `<...>` placeholder slots (advisory, never a required fill) · covers: R1
  - test_twins_byte_identical: assert all MILESTONE.md.tmpl twins are md5-equal · covers: M4
  - test_tasks_dag_ignores_strategy: `_compile_task_graph` on a doc with `## Tasks`(2 rows) + `## Exit criteria` + `## Strategy` + `## Close` reads exactly {alpha, beta} with beta→alpha intact · covers: M3, R2
  - test_engine_never_parses_strategy: assert add.py holds no `"## Strategy"` literal and no `strategy_must_stay_soft` reject code (renders verbatim, never gated) · covers: R1
</test_plan>

Tests live in: `add-method/tooling/test_strategy_section.py` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

> The change plan — grounding + contract + build-strategy — was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope, follow the strategy (improve on it if the code teaches you better), and touch no test or the frozen contract.
Strategy actually used: as planned — wrote the RED suite (slot present+placed · drafted-blank · 4-twin md5 parity · Tasks-DAG reads exactly N rows via `_compile_task_graph` · engine-never-parses guard), inserted the `## Strategy` block into the SOURCE `MILESTONE.md.tmpl` after `## Exit criteria`/before `## Close` (contract's verbatim content), synced the 3 twins byte-for-byte, green. Zero add.py edit → ENGINE_MD5 unchanged (template renders verbatim via new-milestone).
Safety rule (feature-specific): placement AFTER `## Exit criteria` keeps `## Strategy` out of the `## Tasks` DAG-parse span (`_compile_task_graph` bounds ## Tasks at the next `## ` heading) — the task graph is byte-behaviour-unchanged.
Code lives in: `add-method/tooling/templates/MILESTONE.md.tmpl` (+ 3 twins)
Constraints: do NOT change any test or the frozen §3 contract; stay inside the §3 Build-strategy Scope; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — test_strategy_section 5/5; milestone/template suite (template_atomic · bundle_parity · packaging · ship_clean) 33/0; `add.py check` clean
- [x] coverage did not decrease — net +5 conformance tests; nothing removed
- [x] no test or contract was altered during build — §3 frozen @ v1 untouched; the red suite was authored in the tests phase, before build
- [x] the green was EARNED, not gamed — 2 slot assertions ran RED before the insert, GREEN after; the DAG test drives the REAL `_compile_task_graph` on a synthesized doc (not a stub); live new-milestone render confirmed independently
- [x] concurrency / timing of the risky operation is safe — N/A: static template text, no IO/concurrency
- [x] no exposed secrets, injection openings, or unexpected dependencies — pure template prose; no deps
- [x] layering & dependencies follow CONVENTIONS.md — 4-twin parity held; NO add.py edit → ENGINE_MD5 correctly unchanged (renders verbatim, the contract's HARD invariant)
- [x] a person reviewed and approved the change — mechanical template edit; AI-verified under autonomy: auto on complete evidence

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] a freshly `new-milestone`-created MILESTONE.md shows a `## Strategy` heading — confirmed by live run in /tmp: `grep -c "## Strategy"` = 1
- [x] `milestone-confirm` + `check` stay clean with Strategy drafted-blank — confirmed by live run: "confirmed milestone" + "check: 5 passed, 0 failed", no strategy hold/warning

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read in full, not skimmed: the inserted `## Strategy` block matches the frozen §3 Contract content verbatim; placement verified AFTER `## Exit criteria`, BEFORE `## Close`; the `> ` guidance blockquote + `<...>` slots mirror the `## Close`/`## Release steps` drafted-blank convention

### Live-verify evidence — confirm the §3 PLAN grounding anchors still resolve (fill at the gate)
> Re-resolve every symbol the §3 Contract cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] every symbol the §3 Contract cites still resolves in the current tree — confirmed: `## Exit criteria` (insert-after anchor) + `## Close — ship review` (insert-before anchor) both present in the current MILESTONE.md.tmpl; `_compile_task_graph` (add.py:4633) bounds `## Tasks` at the next `## ` heading, unchanged since Ground SHA
- [x] any anchor that moved/renamed since Ground SHA is named here — none moved; the template grew sections (## Scope/## Ground/## Shared) but the two cited anchors are intact and correctly ordered

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self (add-worker, verify beat) · adversarially checked: (1) tried to corrupt the Tasks-DAG — `_compile_task_graph` on a 2-task doc WITH `## Strategy` present still reads exactly {alpha, beta} with the beta→alpha edge intact, so R2 holds; (2) confirmed the engine holds NO `"## Strategy"` literal and NO `strategy_must_stay_soft` reject → the section can never become a covert gate (R1); (3) live new-milestone + confirm + check independently proved the render and the non-gating.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
Advisor: self
1. Security: CLEAR — static template prose, no input surface
2. Concurrency: CLEAR — no IO, no shared state
3. Architecture: CLEAR — mirrors the existing drafted-blank section convention; zero engine coupling (renders verbatim)
Verdict: PASS
Residue: none
Binding: advisory — sensitivity unset (template edit, mechanical in nature)

### GATE RECORD
Reported: yes — the gate report (banner/ARC) rendered before this outcome recorded
Outcome: PASS
Reviewed by: Tin Dang (auto-gate on complete evidence) · date: 2026-07-23

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency — the §3 Build-strategy Optimization stance budget is a monitor here, not just an intention>

### Decisions (ADR)
- [AI] specify — chose drafted-blank template section like Close/Release; rejected an engine-parsed required section · a separate STRATEGY.md file
- [human] freeze — froze §3 @ v1 (approved by tindang)
- [AI] build — approach: a drafted-blank template section mirroring the `## Close` / `## Release steps` convention — NO engine parsing (renders verbatim via `new-milestone`), so zero `engine_pin` churn; derives from the "drafted-blank section like Close/Release" framing chosen in §1.
- [AI] build — data strategy: n/a — static template text; the rendered `MILESTONE.md` instance is the only artifact, and it must agree with the Contract's placement invariants.
- [AI] build — pattern: the existing drafted-blank section convention (`## Close`, `## Release steps`) + the 3-tree template-parity pattern.
- [AI] build — optimization stance: correctness-first, no perf budget — ⚠ the facet I trust least is placement NOT disturbing the `## Tasks` DAG parse; a dedicated red test asserts the parse reads exactly N task rows.
- [AI] build — strategy used: as planned — wrote the RED suite (slot present+placed · drafted-blank · 4-twin md5 parity · Tasks-DAG reads exactly N rows via `_compile_task_graph` · engine-never-parses guard), inserted the `## Strategy` block into the SOURCE `MILESTONE.md.tmpl` after `## Exit criteria`/before `## Close` (contract's verbatim content), synced the 3 twins byte-for-byte, green. Zero add.py edit → ENGINE_MD5 unchanged (template renders verbatim via new-milestone).
- [AI] verify — gate PASS (reviewed by Tin Dang (auto-gate on complete evidence))

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

