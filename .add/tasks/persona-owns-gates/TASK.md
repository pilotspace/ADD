# TASK: retire the fixed report-template — personas own gate structure + cadence

slug: persona-owns-gates · created: 2026-07-16 · stage: mvp · risk: high
milestone: strategy-intake
autonomy: conservative   <!-- level: manual<conservative<auto — lowered: method-defining trust-layer change, human gate at verify. Relations: `--depends-on`/`--extends`/`--relates-to` task edges (GLOSSARY; `check` validates). -->
phase: tests   <!-- specify→plan→tests→build→verify→done; plan unites grounding + frozen contract + build strategy -->
<!-- high-risk/method-defining? declare `risk: high` on the slug line + lowered autonomy — the engine refuses an unguarded completion (`unguarded_high_risk_auto`). A comment is never a declaration. -->

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

<!-- EXIT: the specify guide's exit_gate binds (rules + ranked ⚠ assumptions). -->

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

<!-- EXIT: the scenarios guide's exit_gate binds. -->

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
Scope (may touch): `add-method/skill/add/report-template.md` `SKILL.md` `.claude/skills/add/report-template.md` `SKILL.md` `add-method/src/add_method/_bundled/skill/add/report-template.md` `SKILL.md` `add-method/tooling/test_persona_owned_gates.py`
Strategy (ordered batches): 1. rewrite `report-template.md` source — principles + the explicit four-floors block 2. rewrite the SKILL.md mandate line (~L98-100) to name the principles, under the 9500 B ceiling 3. sync both files to the 2 twin skill trees (byte-identical) 4. write `test_persona_owned_gates.py` (four floors present · no mandated section list · SKILL.md ceiling+parity · engine unchanged), then migrate any test that pins the OLD fixed order 5. run the report/skill-lean/parity suite green
Approach (domain strategy): reframe governance prose from PRESCRIPTIVE LAYOUT ("render these blocks in this order") into a DECLARATIVE CONTRACT ("convey this content; you own the form") plus a floors block — mirrors how §5 build-strategy is SOFT-preferred while the §3 contract is HARD (the same soft-form/hard-floor split the method already uses)
Data strategy: three parallel doc trees kept byte-identical (md5 parity) — the same twin-parity shape as the MILESTONE.md.tmpl twins in strategy-section
Pattern: the 3-skill-tree parity + 9500 B SKILL.md ceiling (the engine-minimalism thread)
Optimization stance: token cost — this REMOVES per-gate boilerplate (fewer mandated blocks re-read each turn) while keeping the floors; ⚠ the facet trusted least is NOT over-trimming report-template.md below the floors' clarity; correctness-of-floors first, no byte budget that costs a floor
Persona (required): methodology-engine-dev (the method's own engine/skill-author stance) — advisory, never lowers a gate
Spawn isolation (default): inline (sequential doc edits across 3 trees; user prefers inline over spawns for sequential work)
Known-problem fixes: over-deletion drops a floor → R2 trust_floor_dropped · leaving the fixed ordered list → R1 fixed_template_persists · SKILL.md over-ceiling → keep < 9500 B by compressing, never by cutting a floor

<!-- The freeze IS the one approval — it freezes the whole PLAN; lead it with the bundle's lowest-confidence flag (§1 ⚠ feeds it; a flag may point at any part — run.md). The Contract shape is HARD (tamper-guarded); Grounding + Build-strategy are SOFT (the builder may improve on the strategy, recording actual at §5/verify). Approved -> Status: FROZEN @ vN — approved by <name>; changing the frozen Contract = change request back to SPECIFY. Scope tokens, backticked, on the Scope line: `./…` = this task dir · a token with "/" = project root · a bare name = sibling of the previous token's dir · a DIRECTORY token covers its whole subtree · outside-root resolutions drop fail-closed · absent line = UNDECLARED (grandfathered — an undeclared task is never retro-red). The plan guide's exit_gate binds: frozen · every rejection contracted · names match GLOSSARY · anchors grounded · flag surfaced. -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: <e.g. 90%>
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_<scenario>: arrange <Given> / act <When> / assert <Then> + assert <unchanged> · covers: <M#, R:code — optional>
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir · a token with "/" = the project root · a bare name = a sibling of the previous token's dir · a directory counts its *.py files (non-recursive) · declared counts marked † · outside the project root counts 0 -->

<!-- EXIT: the tests guide's exit_gate binds (red for the RIGHT reason). -->

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

> The change plan — grounding + contract + build-strategy — was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope, follow the strategy (improve on it if the code teaches you better), and touch no test or the frozen contract.
Strategy actually used: <fill at VERIFY — the strategy you ACTUALLY used (or "as planned"); harvested into the §7 Decisions (ADR) block as the [AI] build decision>
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the frozen §3 contract; stay inside the §3 Build-strategy Scope; allow-list packages only; ask if unclear.

<!-- Scope-lock source: the §3 `Scope (may touch)` line; an out-of-scope build fails the gate (scope_violation); the build guide's exit_gate binds. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all tests pass
- [ ] coverage did not decrease
- [ ] no test or contract was altered during build
- [ ] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [ ] concurrency / timing of the risky operation is safe
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [ ] <observable outcome a correct build must produce> — confirmed by <how / where>
- [ ] <another observable outcome> — confirmed by <evidence seen>

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [ ] DIALECT — tests speak the same value formats the spec's examples use (spec-dialect floor): <what confirmed>
- [ ] WIRING (code) — every new symbol is referenced; record where / how confirmed
- [ ] DEAD-CODE (code) — no new unused or orphaned symbol introduced
- [ ] SEMANTIC (prose / non-code) — read in full, not skimmed: <what read · what confirmed>

### Live-verify evidence — confirm the §3 PLAN grounding anchors still resolve (fill at the gate)
> Re-resolve every symbol the §3 Contract cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [ ] every symbol the §3 Contract cites still resolves in the current tree — confirmed by <how / where>
- [ ] any anchor that moved/renamed since Ground SHA is named here, not left silent

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: <EARNED | NOT-EARNED>
By: <self | agent-id> · adversarially checked: <what was probed>

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: <agent-id | self>
1. Security: <CLEAR | HARD-STOP: finding>
2. Concurrency: <CLEAR | RESIDUE: finding>
3. Architecture: <CLEAR | RESIDUE: finding>
Verdict: <PASS | HARD-STOP>
Residue: <none | summary>
Binding: <yes — mechanical | advisory — <sensitivity>>

### GATE RECORD
Reported: <yes — the gate report (banner/ARC) rendered before this outcome recorded | no>
Outcome: <PASS | RISK-ACCEPTED | HARD-STOP>
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: <name> · date: <date>

<!-- Security is ALWAYS HARD-STOP; record exactly one outcome — no silent pass. The Advisor 3-lens and Refute-read verdicts are audit-measured (`advisor_verdict_unrecorded` · `refute_unrecorded`), never engine-blocked; a human spot-audit backstops anything unrecorded. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency — the §3 Build-strategy Optimization stance budget is a monitor here, not just an intention>

### Decisions (ADR)
<harvested at done from §1/§3/§5/§6 — do not hand-edit; one actor-tagged line per decision, refilled only while this placeholder stands>

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
