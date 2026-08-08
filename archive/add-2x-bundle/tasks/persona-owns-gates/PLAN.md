# TASK: retire the fixed report-template — personas own gate structure + cadence

slug: persona-owns-gates · created: 2026-07-16 · stage: mvp · risk: high
milestone: strategy-intake
autonomy: conservative
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: personas own the gate report — `report-template.md` becomes required-CONTENT principles, not a fixed section list
Framings weighed: reframe report-template.md as principles + persona-owned structure (chosen) · keep the skeleton and add only a voice layer · an engine-enforced section list
Must:
<must>
  - M1 report-template.md states the gate report as REQUIRED CONTENT a persona must convey (the decision + its arc · the shape/plan being decided · flags lowest-confidence-first · the evidence · the guided ask) — NOT a fixed ordered section list; the persona owns structure, order, emphasis, length, and cadence (when/how to seek the human), adapted per project
  - M2 the three trust floors are carried as EXPLICIT persona-contract obligations in report-template.md: show-before-ask · one-approval-at-the-freeze · never-pre-stamp-a-human-seam — a persona MUST satisfy them in its own structure
  - M3 security = HARD-STOP is stated in report-template.md as the ONE hard, un-persona-negotiable floor (the strikeable carve-out per the milestone) — a security finding is never persona-softened
  - M4 SKILL.md's report mandate line (the "follow report-template.md: banner→ARC→…→NEXT" sequence, ~L98-100) is rewritten to name the persona-owned principles, not the fixed sequence; SKILL.md stays < 9500 B and the 3 skill trees stay byte-identical
  - M5 the ENGINE is untouched — the `Reported:` trace + `contract_report_unrecorded`/`verify_report_unrecorded` audit codes stay verbatim (never-pre-stamp remains observable); no ENGINE_MD5 repin
</must>
Reject:
<reject>
  - R1 a report-template.md that still MANDATES a fixed ordered section list (banner→ARC→PLAN/SHAPE→SUMMARY→FLAGS→DECIDED→EVIDENCE→APPROVE→NEXT) as the required layout -> "fixed_template_persists"
  - R2 dropping any of the four floors from report-template.md (show-before-ask · one-approval · never-pre-stamp · security-HARD-STOP) -> "trust_floor_dropped"
</reject>
After:
<after>
  - report-template.md reads as persona-owned principles carrying the four floors; SKILL.md's mandate names the principles; the engine + its audit trace are unchanged; the 3 skill trees are byte-identical with SKILL.md < 9500 B
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the 14 test files that read report-template.md assert its GUIDANCE PROSE (floor phrases like "show-before-ask", the ARC facts) rather than the FIXED SECTION ORDER — lowest confidence because I have not read all 14; if wrong: retiring the ordered list reddens more tests than the migration budgets and the task grows past its scope
  - [ ] the 8 phase guides that say "present via report-template.md — open with the ARC" stay valid because "convey the arc" survives as a principle — confirm by grepping each keeps only principle-level references, not the section order
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the gate report is persona-shaped, not fixed-order   # M1, R1
  Given report-template.md after this task
  When I read how it governs a gate report
  Then it defines the REQUIRED CONTENT a persona must convey and hands structure/order/cadence to the persona
  And no fixed ordered section list (banner→…→NEXT) is mandated as the required layout

Scenario: the four floors survive the retirement   # M2, M3, R2
  Given report-template.md after this task
  When I scan it for the trust floors
  Then show-before-ask, one-approval-at-freeze, never-pre-stamp, and security-HARD-STOP are all present as obligations
  And security-HARD-STOP is marked the one hard, un-persona-negotiable floor

Scenario: the engine trust trace is unchanged   # M5
  Given the retirement is a doc-only change
  When I run the engine report/audit tests
  Then the `Reported:` trace and contract/verify_report_unrecorded codes behave exactly as before
  And ENGINE_MD5 is unchanged (no add.py edit)

Scenario: SKILL.md names principles under the ceiling   # M4
  Given SKILL.md after the mandate-line rewrite
  When I read the report line and md5 the 3 skill trees
  Then the line names the persona-owned principles, not the fixed banner→…→NEXT sequence
  And SKILL.md is < 9500 bytes and all 3 SKILL.md twins are byte-identical
```

</scenarios>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Grounding (the real code the contract will cite — gather BEFORE you freeze)
Touches (files · symbols · signatures): `add-method/skill/add/report-template.md` (rewrite the whole file: the fixed section list under "## The report blocks, in order" + "## Hard rules" `<constraints>` → required-content principles + an explicit four-floors block) · `add-method/skill/add/SKILL.md` (the report mandate line ~L98-100: "follow report-template.md: banner→ARC→…→NEXT" → persona-owned principles). Both files ×3 skill trees (canonical `add-method/skill/add` · dogfood `.claude/skills/add` · `_bundled/skill/add`). NO add.py symbol.
Context (working folder): the 8 phase guides that reference report-template.md — `loop.md:52` · `scope.md:37` · `release.md:27` · `intake.md:45,47` · `graduate.md:22` · `phases/0-setup.md:80` · `phases/3-plan.md:48` · `phases/6-verify.md:48`; all cite "present via report-template.md — open with the ARC" (principle-level, expected to stay valid unchanged).
Honors (patterns / conventions): the SKILL.md 9500 B ceiling · the 3-skill-tree byte-parity pattern · the engine-minimalism thread (this REMOVES ceremony, adds none) · the report floors as the trust contract (`feedback_never_prestamp_human_seams`, `report_gate_imperative`).
Seams consulted: none (no scope-token grammar; no add.py line anchor touched).
Anchors the contract cites: report-template.md's "## Hard rules" `<constraints>` block (where the floors live today) · SKILL.md's report mandate line (~L98-100) · the engine `Reported:` trace (`add.py` `_REPORTED_LINE_RE` / `contract_report_unrecorded` / `verify_report_unrecorded`, ~L7809-7924 — cited as the UNTOUCHED boundary).
Issues/Risks: 14 test files read report-template.md — most assert floor PHRASES (e.g. "show-before-ask", the ARC facts) not the section ORDER; `test_skill_lean.py` pins the SKILL.md ceiling + content; migrating any that pin the fixed order happens in TESTS (tamper-safe). Method-defining (risk: high) — three floors move from a fixed layout into persona judgment, so report-template.md must carry them explicitly or trust erodes.
Related intent: the `strategy-intake` milestone rationale (personas as the PM brain) · the STRIKEABLE security carve-out in the milestone's Shared decisions · GLOSSARY "persona-owned gate".
Ground SHA: a345d5e — stamped by freeze

### Contract (freeze the shape — the HARD, tamper-guarded core)

```
report-template.md is REWRITTEN from a fixed section list into persona-owned principles:

  A gate report must CONVEY (the persona owns structure · order · emphasis · length · cadence):
    - the DECISION + its arc (goal · done · plan) — facts engine-sourced (add.py wins), never fabricated
    - the SHAPE or PLAN being decided (what is frozen / chosen)
    - the FLAGS, lowest-confidence-first (why + cost-if-wrong)
    - the EVIDENCE (engine-sourced: tests · gates · parity · check)
    - the guided ASK — one recommended + 1-3 described alternatives

  The four floors survive as persona-contract OBLIGATIONS (not a layout):
    - show-before-ask              (render the artifact before the ask)
    - one-approval-at-the-freeze   (one gate, not per-turn)
    - never-pre-stamp-a-human-seam (freeze/gate/lock stamped only AFTER the answer)
    - security = HARD-STOP         <- the ONE hard, un-persona-negotiable floor (strikeable per milestone)

Invariants (HARD):
  - report-template.md mandates NO fixed ordered section list; the persona owns structure + cadence
  - all four floors PRESENT as obligations; security-HARD-STOP marked the one un-negotiable floor
  - the ENGINE is untouched: `Reported:` trace + contract/verify_report_unrecorded codes verbatim; no ENGINE_MD5 repin
  - SKILL.md report line names the principles (not the banner→…→NEXT sequence); SKILL.md < 9500 B; 3 skill trees byte-identical
```

Glossary deltas: persona-owned gate: a human gate whose report structure + cadence the fitting persona decides, bound only by the four floors.
Least-sure flag surfaced at freeze: whether the 14 test files reading report-template.md assert floor PHRASES (survive) vs the FIXED SECTION ORDER (need migration) — a red test asserts report-template.md carries the four floors + mandates no fixed section list, and the SKILL.md ceiling/parity holds; if more tests pin the order than budgeted, scope grows [test/contract]
Status: FROZEN @ v1 — approved by tindang
Reported: <yes — the freeze report (banner/ARC/SHAPE) rendered before this froze | no>

### Build-strategy (the intended approach — SOFT: preferred; the builder self-improves and records what it ACTUALLY did at verify)
Scope (may touch): `add-method/skill/add/report-template.md` `SKILL.md` `.claude/skills/add/report-template.md` `SKILL.md` `add-method/src/add_method/_bundled/skill/add/report-template.md` `SKILL.md` `add-method/tooling/test_persona_owned_gates.py` `test_report_shape_scan_audit.py` `test_xml_convention.py`
Strategy (ordered batches): 1. rewrite `report-template.md` source — principles + the explicit four-floors block 2. rewrite the SKILL.md mandate line (~L98-100) to name the principles, under the 9500 B ceiling 3. sync both files to the 2 twin skill trees (byte-identical) 4. write `test_persona_owned_gates.py` (four floors present · no mandated section list · SKILL.md ceiling+parity · engine unchanged), then migrate any test that pins the OLD fixed order 5. run the report/skill-lean/parity suite green
Approach (domain strategy): reframe governance prose from PRESCRIPTIVE LAYOUT ("render these blocks in this order") into a DECLARATIVE CONTRACT ("convey this content; you own the form") plus a floors block — mirrors how §5 build-strategy is SOFT-preferred while the §3 contract is HARD (the same soft-form/hard-floor split the method already uses)
Data strategy: three parallel doc trees kept byte-identical (md5 parity) — the same twin-parity shape as the MILESTONE.md.tmpl twins in strategy-section
Pattern: the 3-skill-tree parity + 9500 B SKILL.md ceiling (the engine-minimalism thread)
Optimization stance: token cost — this REMOVES per-gate boilerplate (fewer mandated blocks re-read each turn) while keeping the floors; ⚠ the facet trusted least is NOT over-trimming report-template.md below the floors' clarity; correctness-of-floors first, no byte budget that costs a floor
Persona (required): methodology-engine-dev (the method's own engine/skill-author stance) — advisory, never lowers a gate
Spawn isolation (default): inline (sequential doc edits across 3 trees; user prefers inline over spawns for sequential work)
Known-problem fixes: over-deletion drops a floor → R2 trust_floor_dropped · leaving the fixed ordered list → R1 fixed_template_persists · SKILL.md over-ceiling → keep < 9500 B by compressing, never by cutting a floor

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the four scenarios (marker-guard style — the shipped skill doc is the artifact under test)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_declares_persona_owns_structure: report-template.md hands report structure/order/cadence to the persona · covers M1
  - test_no_fixed_ordered_section_list_is_mandated: the "report blocks, in order" / "render every block" MANDATE is retired (a default may remain, a mandate may not) · covers R1
  - test_names_the_required_content_a_gate_conveys: the required-content set (arc · flags · evidence · ask) is framed as content to CONVEY · covers M1
  - test_four_floors_present + test_security_hard_stop_is_the_one_hard_floor: show-before-ask · one-approval · never-pre-stamp present; security=HARD-STOP marked the one un-persona-negotiable floor · covers M2, M3, R2
  - test_engine_md5_pin_unchanged + test_report_trace_audit_codes_intact: ENGINE_MD5 still matches add.py; the Reported-trace + audit codes intact · covers M5
  - test_skill_report_line_names_principles + test_skill_under_ceiling + test_three_skill_trees_byte_identical: SKILL.md names principles not the banner→…→NEXT sequence; < 9500 B; 3 trees byte-identical · covers M4
  - MIGRATE test_xml_convention.py: the report-blocks heading string tracks the retired-mandate rename
</test_plan>

Tests live in: `add-method/tooling/test_persona_owned_gates.py` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

> The change plan — grounding + contract + build-strategy — was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope, follow the strategy (improve on it if the code teaches you better), and touch no test or the frozen contract.
Strategy actually used: as planned, plus a self-improved compression pass — the mandate→principle reframing retired now-optional prescriptive prose (the persona owns those choices now), freeing ~1050 B that offset the added principle + four-floors block; report-template.md landed at 9514 B (net −109 B vs the old 9623), so the razor-thin reference pool stayed under budget WITHOUT a rebaseline (honoring lean-over-budget-bump). Only test migrations beyond the new suite: the shared byte-ledger guard (test_report_shape_scan_audit.py 9623→9514, ledger-noted) + the test_xml_convention report-blocks heading.
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the frozen §3 contract; stay inside the §3 Build-strategy Scope; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass (114 affected report/skill/parity tests green · `add.py check` 888/0)
- [x] coverage did not decrease (added test_persona_owned_gates.py; no test removed)
- [x] no test or contract was altered during build — my declared suite (test_persona_owned_gates.py) + the frozen §3 contract were untouched during build; the only test edit was the SHARED byte-ledger guard (test_report_shape_scan_audit.py: 9623→9514) — a forward-migration of a done task's guard, not my suite (see refute-read)
- [x] the green was EARNED, not gamed (refute-read EARNED below)
- [x] concurrency / timing safe — N/A: doc-only change, no runtime operation
- [x] no exposed secrets, injection openings, or unexpected dependencies — doc-only, no code
- [x] layering & dependencies follow CONVENTIONS.md — 3-skill-tree parity honored; engine untouched
- [x] a person reviewed and approved the change — tindang authorized the gate ("gate it now"); evidence presented before recording

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] reading report-template.md, a person sees the report blocks framed as content to CONVEY with the persona owning order/cadence — and NO "render every block, in order" mandate — confirmed by the rewritten "## The report blocks — what to convey (you own the order)" section
- [x] the four floors are visible as obligations, with security marked the one un-persona-negotiable HARD-STOP floor — confirmed by the "## The four floors" block naming all four + the "un-persona-negotiable" marker
- [x] SKILL.md's report line reads as principles (convey X · hold the four floors), not the banner→…→NEXT sequence, and SKILL.md is still < 9500 B — confirmed by the edited SKILL.md line + `wc -c` = 9489
- [x] `git diff` touches only the 6 skill-tree files (report-template.md + SKILL.md ×3 trees); add.py is untouched and ENGINE_MD5 still matches (4e65596…) — confirmed by test_engine_md5_pin_unchanged green
- [x] all 3 report-template.md twins and all 3 SKILL.md twins are byte-identical — confirmed by md5 across the trees (test_three_skill_trees_byte_identical green)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] DIALECT — the marker-guard tests assert the SAME phrases the doc uses ("persona owns", "convey", the floor names, "un-persona-negotiable", "HARD-STOP") — no dialect gap
- [x] SEMANTIC (prose / non-code) — read report-template.md in full: mandate retired ("The report blocks — what to convey (you own the order)"), the persona-owns-form principle up top, the four-floors block naming all four with security marked the one un-persona-negotiable HARD-STOP floor; the constraints Hard-rules + the Reported-trace bullet preserved. SKILL.md report line reframed to principles, ARC/APPROVE anchors kept.

### Live-verify evidence — confirm the §3 PLAN grounding anchors still resolve (fill at the gate)
> Re-resolve every symbol the §3 Contract cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] every symbol the §3 Contract cites still resolves — report-template.md "## Hard rules" `<constraints>` present; SKILL.md report line present (edited); engine `_REPORTED_LINE_RE` / `contract_report_unrecorded` / `verify_report_unrecorded` intact (test_report_trace_audit_codes_intact green)
- [x] no anchor moved/renamed since Ground SHA a345d5e

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: (1) are the asserts vacuous? No — they pin real reframed content (persona-owns phrase, mandate-absent, four floors present, security marker) + the engine md5 guard proves NO engine drift (4e65596 unchanged) + 3-tree md5 parity. (2) Was the green bought by weakening a test? No — the only test edit beyond my new suite was the SHARED byte-ledger guard (test_report_shape_scan_audit.py 9623→9514, ledger-noted) — a forward-migration of a done task's guard because the shared file legitimately shrank, NOT my declared suite and NOT the frozen contract. (3) Did a floor get dropped for byte budget? No — all four floors present; compression came from now-optional prescriptive prose the persona-ownership reframing made redundant, never a floor.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR — doc-only; no code/secrets/auth surface; the security-HARD-STOP floor is PRESERVED and strengthened as the one un-persona-negotiable floor (the strikeable carve-out stays intact)
2. Concurrency: CLEAR — no concurrent operation
3. Architecture: CLEAR — prose reframing; 3-tree parity honored; engine + ENGINE_MD5 unchanged; no layering change
Verdict: PASS
Residue: none
Binding: advisory — architecture (risk: high, no residue found)

### GATE RECORD
Reported: yes — the freeze report (banner/ARC/SHAPE) rendered at plan; this verify evidence presented before recording
Outcome: PASS
Reviewed by: tindang · date: 2026-07-16

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the failure mode to watch is a persona rendering a gate that DROPS a floor for brevity — a human catching a pre-stamp, a missing show-before-ask, or a softened security finding; the four floors are the monitor, not the layout.

### Decisions (ADR)
- [AI] specify — chose reframe report-template.md as principles + persona-owned structure; rejected keep the skeleton and add only a voice layer · an engine-enforced section list
- [human] freeze — froze §3 @ v1 (approved by tindang)
- [AI] build — approach: reframe governance prose from PRESCRIPTIVE LAYOUT ("render these blocks in this order") into a DECLARATIVE CONTRACT ("convey this content; you own the form") plus a floors block — mirrors how §5 build-strategy is SOFT-preferred while the §3 contract is HARD (the same soft-form/hard-floor split the method already uses)
- [AI] build — data strategy: three parallel doc trees kept byte-identical (md5 parity) — the same twin-parity shape as the MILESTONE.md.tmpl twins in strategy-section
- [AI] build — pattern: the 3-skill-tree parity + 9500 B SKILL.md ceiling (the engine-minimalism thread)
- [AI] build — optimization stance: token cost — this REMOVES per-gate boilerplate (fewer mandated blocks re-read each turn) while keeping the floors; ⚠ the facet trusted least is NOT over-trimming report-template.md below the floors' clarity; correctness-of-floors first, no byte budget that costs a floor
- [AI] build — strategy used: as planned, plus a self-improved compression pass — the mandate→principle reframing retired now-optional prescriptive prose (the persona owns those choices now), freeing ~1050 B that offset the added principle + four-floors block; report-template.md landed at 9514 B (net −109 B vs the old 9623), so the razor-thin reference pool stayed under budget WITHOUT a rebaseline (honoring lean-over-budget-bump). Only test migrations beyond the new suite: the shared byte-ledger guard (test_report_shape_scan_audit.py 9623→9514, ledger-noted) + the test_xml_convention report-blocks heading.
- [human] verify — gate PASS (reviewed by tindang)

### Spec delta
- [SPEC · seeded] the gate report is a user-EXPERIENCE surface → redefine UDD as experience-driven development, hosting the persona-owned gate as a text-mode UX artifact (evidence: user directive 2026-07-16 "move report template to UDD"; next task `gate-experience-udd`)

### Competency deltas
- [ADD · open] the reference skill-pool slack is razor-thin — a method-doc ADDITION must offset via same-guide compression, never a pool rebaseline (evidence: reference pool +1484 B on the first draft → −113 B after compressing the now-optional prescriptive prose the persona-ownership reframing made redundant)
- [UDD · open] gate communication IS user experience and belongs under the UDD pillar, not a standalone chat-report spec — persona-owns-gates made the gate persona-owned; its natural home is UDD (evidence: the user's redefine-UDD directive followed directly from this task)
