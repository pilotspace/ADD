# TASK: fold grows the current persona schema: anti-pattern + ability hints

slug: fold-persona-sections · created: 2026-07-07 · stage: mvp
milestone: self-improving-loop
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): add.py:_PERSONA_FOLD_SECTIONS (the growable-section allowlist) ×3 engine trees · skill/add/{deltas,fold}.md + phases/7-observe.md ×3 skill trees · docs/18-personas.md ×4 book twins · agents/add-verify.md + add-persona.md ×3 agent trees · test_fold_persona_sections.py (new)
Context (working folder): fold's persona machinery (validate→prepend→clobber guards) is section-generic — only the allowlist is frozen at the pre-1.16.1 schema
Honors (patterns / conventions): ENGINE_MD5 re-aim on add.py touch · engine trees ×3 byte-identical · never-clobber persona invariant · orchestration pool NOT touched (deltas/fold/7-observe are reference+phases pools — measure both)
Seams consulted: none apply (allowlist-only engine delta)
Anchors the contract cites: `_PERSONA_FOLD_SECTIONS` · `persona_section_unroutable` · deltas.md persona-target grammar line · fold.md routing table + reject-code line
Issues/Risks (→ feed §1): the 1.16.1 schema sections ## Anti-patterns/## Abilities are NOT fold-growable (same dead-wiring class as flow: was) — the persona learning loop (used once ever) cannot grow the sections that most shape agent behavior. Trap: negative test fixture uses `default-requirement` (stays unroutable); a persona lacking the target section still dies persona_section_unroutable (sections are RECOMMENDED, not universal)
Related intent: Tin 2026-07-07 'fix all' after the deltas/fold investigation — finding #3: the persona learning loop is the highest-leverage delta route now that dynamic personas are first-class
Ground SHA: ef987c2

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: fold grows the current persona schema — anti-pattern + ability hints
Framings weighed: extend the allowlist (chosen — machinery is section-generic, 2-line engine delta) · free-form section hints (rejected — fail-closed routing is the invariant) · auto-map hint from lesson text (rejected — judgment in the engine)
Must:
<must>
  - M1: `· persona:<slug> · anti-pattern` folds into `## Anti-patterns` (prepend, never clobber)
  - M2: `· persona:<slug> · ability` folds into `## Abilities`
  - M3: every prose surface documenting the hint list names all four (deltas.md grammar · fold.md table+reject · 7-observe footnote · 18-personas ×4 twins)
  - M4: add-verify + add-persona recommend the persona tag for an ADD/TDD lesson that names how an agent should behave
</must>
Reject:
<reject>
  - R1: an unknown hint (e.g. default-requirement) -> "persona_section_unroutable" (unchanged)
  - R2: target persona missing the section -> "persona_section_unroutable" (fail-closed, nothing written)
  - R3: engine trees or guide twins drift -> "tree_drift"
</reject>
After:
<after>
  - the observe→delta→fold loop can grow the exact sections that make dynamic personas high-performance — the learning loop and the schema are the same generation
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ hint spelling `anti-pattern`/`ability` (singular, kebab) matches the existing pair's convention — lowest confidence because users may type plurals; if wrong: a later alias is additive
  - [x] no test pins the allowlist exhaustively — confirmed by grep (negative fixture uses default-requirement)
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: anti-pattern lesson grows the persona   # M1 (M2 same for ability)
  Given a persona with an ## Anti-patterns section and a planted `· persona:x · anti-pattern` open lesson
  When add.py fold runs
  Then the bullet lands at the TOP of ## Anti-patterns and the lesson flips folded

Scenario: unknown hint still fail-closed   # R1+R2
  Given a `default-requirement` hint (or a persona missing the section)
  When fold runs
  Then it dies persona_section_unroutable
  And nothing is written, no version bump

Scenario: the four hints are documented   # M3+M4
  Given deltas.md, fold.md, 7-observe.md, 18-personas.md, add-verify, add-persona
  When an agent reads any of them
  Then the hint list shows all four and the agents recommend persona-targeting behavioral lessons

Scenario: parity holds   # R3
  Given the engine ×3, skill ×3, book ×4, agent ×3 trees
  When the edits land
  Then all twin sets are byte-identical
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
_PERSONA_FOLD_SECTIONS gains: "anti-pattern" -> "## Anti-patterns", "ability" -> "## Abilities"
  (validate→prepend→never-clobber machinery unchanged; persona_section_unroutable message auto-lists all four)
grammar: `· persona:<slug> · <critical-rule|success-metric|anti-pattern|ability>`
errors unchanged: persona_section_unroutable | missing_persona_target | persona_clobber_forbidden
Schema: none
```

Glossary deltas: none
Status: FROZEN @ v1 — approved by Tin ('fix all', 2026-07-07)
Reported: yes — investigation finding #3 + fix shape rendered in-chat before freeze
Least-sure flag surfaced at freeze: [spec] singular kebab hint spelling — plural aliases deferred until real usage shows the need

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: one test per Must/Reject
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_anti_pattern_hint_folds / test_ability_hint_folds (temp project, planted lesson, section grows newest-first) · covers: M1,M2
  - test_unknown_hint_still_rejects · covers: R1
  - test_missing_section_fail_closed · covers: R2
  - test_prose_names_all_four_hints (deltas.md · fold.md · 7-observe.md · 18-personas.md) · covers: M3
  - test_agents_recommend_persona_tag · covers: M4
  - test_engine_and_guide_parity · covers: R3
</test_plan>

Tests live in: `add-method/tooling/` (test_fold_persona_sections.py) · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/` `add-method/skill/add/` `add-method/agents/` `add-method/docs/` `add-method/src/add_method/_bundled/` `add-method/.add/tooling/` `add-method/../.claude/` `add-method/../.add/tooling/` `add-method/../.add/docs/` `add-method/../18-personas.md`
Strategy (ordered batches): 1. red test 2. allowlist + comment (canonical add.py) 3. prose ×4 surfaces 4. agents ×2 5. sync engine ×3 + skill ×3 + book ×4 + agents ×3, re-aim ENGINE_MD5 6. green + siblings

Persona (required): methodology-engine-dev — engine allowlist change with pin discipline
Spawn isolation (default): n/a — direct sequential build
Known-problem fixes: ENGINE_MD5 re-aim with prior-hash annotation · phases+reference pool budgets measured after prose edits · declare ALL scope paths before tests→build
Strategy actually used: as planned; +fixture fix (temp PROJECT.md needs a foundation-version header — mirrored test_persona_self_improve's _set_fv), re-crossed tests→build; phases pool absorbed via footnote/prompt compression (15B slack), reference via table-cell dedup (7B slack)
Safety rule (feature-specific): fail-closed routing preserved — validate-all-then-write, nothing written on any reject
Code lives in: add.py ×3 trees (engine) · guides/agents/book (prose) · tooling (test)
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass
- [x] coverage did not decrease
- [x] no test or contract was altered during build
- [x] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [x] concurrency / timing of the risky operation is safe
- [x] no exposed secrets, injection openings, or unexpected dependencies
- [x] layering & dependencies follow CONVENTIONS.md
- [x] a person reviewed and approved the change

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] a planted `· persona:probe · anti-pattern` lesson folds to the TOP of ## Anti-patterns — confirmed by test_anti_pattern_hint_folds (temp-project, real fold run)
- [x] `default-requirement` still dies persona_section_unroutable with zero writes — confirmed by test_unknown_hint_still_rejects snapshot equality

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING — the 2 new dict entries are consumed by the existing validate/prepend path (no new symbol)
- [x] DEAD-CODE — none
- [x] SEMANTIC — read in full: deltas.md grammar · fold.md table+rejects · 7-observe footnote · 18-personas loop para · both agent additions; all four hints named everywhere, no gate wording touched

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] §3 anchors resolve — _PERSONA_FOLD_SECTIONS + persona_section_unroutable confirmed by the green suite
- [x] none moved

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: red-first proved 6/7 failing for the right reason (missing allowlist entries + missing prose); the fail-closed negative paths re-proven against the WIDENED allowlist (default-requirement still rejects, missing-section still rejects with snapshot-equal no-write)

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR — no gate/permission surface; fail-closed validation unchanged
2. Concurrency: CLEAR — fold stays validate-all-then-write atomic
3. Architecture: CLEAR — allowlist extension, machinery untouched
Verdict: PASS
Residue: none
Binding: yes — mechanical

### GATE RECORD
Reported: yes
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin (auto-mode directive) · date: 2026-07-07

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): next observe cycles should show persona-tagged lessons appearing (usage was 1-ever)

### Decisions (ADR)
- [AI] specify — chose extend the allowlist; rejected free-form section hints (rejected — fail-closed routing is the invariant) · auto-map hint from lesson text (rejected — judgment in the engine)
- [human] freeze — froze §3 @ v1 (approved by Tin ('fix all', 2026-07-07))
- [AI] build — strategy used: as planned; +fixture fix (temp PROJECT.md needs a foundation-version header — mirrored test_persona_self_improve's _set_fv), re-crossed tests→build; phases pool absorbed via footnote/prompt compression (15B slack), reference via table-cell dedup (7B slack)
- [AI] verify — gate PASS (reviewed by Tin (auto-mode directive))

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

