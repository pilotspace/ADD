# TASK: Teacher-grade load performance: current-schema bodies + frontmatter-first selection

slug: persona-load-performance · created: 2026-07-07 · stage: mvp
milestone: dynamic-personas
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): .add/personas/*.md ×6 (bodies) · templates/personas/_template.md.tmpl · add-method/agents/add-{design,build,verify,advisor,persona}.md ×3 trees · add-method/skill/add/advisor.md ×3 trees · add-method/tooling/test_persona_load_performance.py (new)
Context (working folder): .add/personas-teacher/ (18 division dirs = the domain routing index; README 71.6KB is catalog, not routing)
Honors (patterns / conventions): template distillation discipline #4 (metrics are invariants, not snapshots) + #6 (abilities anchored to real files/commands) · orchestration pool ceiling (advisor.md edit must absorb, 678B slack) · agents ×3-tree + skill ×3-tree parity · persona never lowers a gate
Seams consulted: none apply (no engine change)
Anchors the contract cites: each persona's ## Abilities / ## Anti-patterns sections (new) · Success Metrics literals · the 'Become the persona' stanzas · advisor.md <persona> block · the template's Abilities guidance block
Issues/Risks (→ feed §1): dogfood bodies predate the 1.16.1 schema (0/6 Abilities, 0/6 Anti-patterns) · 3 rotted '2491/0' suite-count literals (suite is ~3062 now) assert a false invariant at load time · every selection load reads all ~25KB of personas when frontmatter (name·vibe·flow) suffices to choose · add-persona browses a 112KB teacher library with no routing hint. NOT an issue (false positive from review): the ## skeletons in method-product-owner/methodology-engine-dev are inside fenced code blocks — guard test must parse fence-aware
Related intent: Tin 2026-07-07 — 'review optimize opportunity of personas and personas template to enhance AI Agent performance when load personas' + 'fix All prose/personas directly' — same value proposition as persona-flow-routing: dynamic personas, teacher-grade performance
Ground SHA: cb945e8

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: persona load performance — what an agent ingests at load is current-schema, true, and cheap to select
Framings weighed: upgrade bodies + prose conventions (chosen — no engine change, immediate) · engine-rendered persona roster index in status (rejected for now — engine change, prose convention gets ~90% of the win) · per-persona byte budget test (rejected — premature; revisit if personas bloat)
Must:
<must>
  - M1: all 6 dogfood personas carry `## Abilities` (≥2 bullets, ≥1 anchored to a backticked real command/file) and `## Anti-patterns` (the default-suspect instincts)
  - M2: no volatile suite-count literal (NNNN/0 snapshot) survives in any persona — metrics restated as invariants
  - M3: the 4 flow-routed roster agents + advisor.md instruct frontmatter-first selection (read name·vibe·flow of all, body of the ONE become)
  - M4: add-persona routes into the teacher by division directory name and is told to skip the catalog README
  - M5: the persona template's Abilities guidance names the orient-commands convention (lead with 1–3 commands to run on load)
</must>
Reject:
<reject>
  - R1: gate-semantics wording change -> "persona_gate_creep" (advisory/never-blocks sentences preserved)
  - R2: orchestration pool over ceiling -> "pool_budget_bust"
  - R3: tree drift (agents ×3, advisor.md ×3) -> "tree_drift"
</reject>
After:
<after>
  - an agent that loads a persona gets current-schema, invariant-true, command-anchored stance for ~5KB instead of a 25KB stale-schema read — and a dynamically drafted persona inherits the same conventions from the template
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ frontmatter-first as prose convention (not engine index) is enough — lowest confidence because nothing measures whether agents comply; if wrong: the engine-rendered roster line (rejected framing) is the escalation, recorded as a SPEC delta
  - [x] the fenced skeletons are schema-conformant as-is — confirmed by add.py check (6× schema-conformant) + fence-aware read
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: persona load is current-schema   # M1+M2
  Given any of the 6 dogfood personas
  When an agent loads it
  Then it finds ## Abilities (command-anchored) + ## Anti-patterns, and no stale suite-count snapshot

Scenario: selection is frontmatter-cheap   # M3
  Given a roster of seeded personas
  When a flow-routed agent or an advisor spawn selects one
  Then the instruction says: choose from frontmatter, read only the chosen body

Scenario: dynamic draft routes into the teacher   # M4+M5
  Given a domain with no seeded persona
  When add-persona drafts one
  Then it reads only the matched division dir's teacher file(s), never the catalog README, and the template tells it to lead Abilities with orient commands

Scenario: floor and budgets unchanged   # R1+R2+R3
  Given the edited surfaces
  When the suite runs
  Then never-blocks/HARD-STOP wording survives, the pool is under ceiling
  And all twin trees stay byte-identical
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
PROSE CONTRACT (no engine change):
  .add/personas/*.md ×6: + ## Abilities (after Identity; first bullet = orient command where natural)
    + ## Anti-patterns (smell → default reaction); Success Metrics literals -> invariants (per template #4)
  _template.md.tmpl: Abilities guidance gains the orient-commands convention (1–3 commands to run on load)
  add-{design,build,verify,advisor}.md ×3 trees + advisor.md ×3 trees: frontmatter-first selection sentence
  add-persona.md ×3 trees: teacher routing = division dir names; never the catalog README
  guard: test_persona_load_performance.py — errors surface as failing assertions:
    "persona_gate_creep" | "pool_budget_bust" | "tree_drift"
Schema: none
```

Glossary deltas: none (orient/abilities/anti-patterns are template-internal conventions, not method headwords)
Status: FROZEN @ v1 — approved by Tin ('fix All prose/personas directly', 2026-07-07)
Reported: yes — the ranked review (A–E findings + correction table) rendered in-chat; Tin approved fixing directly
Least-sure flag surfaced at freeze: [spec] prose-convention compliance is unmeasured — if agents keep reading whole roster files despite the frontmatter-first instruction, the engine-rendered roster index is the recorded escalation path

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: one assertion per Must + per Reject (prose task — guard suite)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_personas_carry_abilities_and_antipatterns (fence-aware section census) · covers: M1
  - test_abilities_are_command_anchored (≥1 backticked token per Abilities) · covers: M1
  - test_no_rotted_suite_count_literals · covers: M2
  - test_agents_instruct_frontmatter_first ×5 surfaces · covers: M3
  - test_add_persona_routes_by_division_dir · covers: M4
  - test_template_names_orient_convention · covers: M5
  - test_never_blocks_and_gate_floor_preserved · covers: R1
  - test_pool_ceiling_held · covers: R2
  - test_tree_parity · covers: R3
</test_plan>

Tests live in: `add-method/tooling/` (test_persona_load_performance.py) · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/agents/` `add-method/skill/add/` `add-method/src/add_method/_bundled/` `add-method/tooling/` `add-method/../.claude/` `add-method/../.add/personas/`
Strategy (ordered batches): 1. red guard 2. six persona bodies (Abilities/Anti-patterns/invariant metrics) 3. template orient convention 4. agent + advisor frontmatter-first sentences (measure pool) 5. add-persona teacher routing 6. sync all twins 7. green + sibling suites. Stance: move existing instinct prose into ## Anti-patterns where it exists (tdd-verifier's red-flags list) rather than duplicating — bytes stay honest.

Persona (required): book-technical-writer — this IS a prose-surface task (persona bodies are method prose agents load)
Spawn isolation (default): n/a — direct build, sequential, per Tin's directive
Known-problem fixes: fenced ## headers → fence-aware census in the guard · pool bust → absorb in advisor.md · '## Abilities' already pinned by test_persona_setup/test_release_1_16_1 (template side — keep) · scope snapshot → declare all real paths BEFORE tests→build crossing (learned last task)
Strategy actually used: as planned; add-advisor needed its own patch phrasing (no semicolon variant), and the template synced to 3 tooling trees (engine-tree twins), not just canonical
Safety rule (feature-specific): a persona never lowers a gate; security-gatekeeper's HARD-STOP wording is untouchable
Code lives in: .add/personas/ + templates + agents + skill trees (prose) · add-method/tooling/ (guard test)
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass (124 persona/roster/lean/xml tests + 49 pin/template tests + add.py check 549/0)
- [x] coverage did not decrease (new 10-test guard suite)
- [x] no test or contract was altered during build (the M3 assertion was strengthened IN the tests phase, before build, against vacuous pass)
- [x] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [x] concurrency / timing — n/a, prose only
- [x] no exposed secrets, injection openings, or unexpected dependencies
- [x] layering & dependencies follow CONVENTIONS.md (all twin trees synced: agents ×3 · advisor.md ×3 · template ×4 tooling trees)
- [x] a person reviewed and approved the change — Tin: 'fix All prose/personas directly' after the rendered review

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] every dogfood persona shows ## Abilities (orient-command-led) + ## Anti-patterns on read — confirmed by the fence-aware census test + manual read of all six
- [x] grep '2[0-9]{3}/0' across .add/personas/ returns nothing — confirmed by test_no_rotted_suite_count_literals

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING — n/a (guard test discovered by unittest discover)
- [x] DEAD-CODE — none; the tdd-verifier red-flags list was MOVED to ## Anti-patterns, not duplicated
- [x] SEMANTIC — read in full: all 6 upgraded persona bodies + template guidance + 5 agent stanzas + advisor block · confirmed each Abilities bullet anchors to a real command/file and no gate wording moved

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] every §3 anchor resolves — confirmed by the green guard suite reading those exact sections
- [x] no anchor moved since ground

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: the M3 roster assertion was caught passing VACUOUSLY pre-build (last task's 'frontmatter' phrase already matched) and strengthened to require the cost instruction ('body of the one') while still red-eligible; 7/10 red before build, 10/10 green after

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR — security-gatekeeper's un-forceable wording verbatim-preserved (guard-tested)
2. Concurrency: CLEAR — prose only
3. Architecture: CLEAR — conventions land in the template so dynamic drafts inherit them; no new mechanism
Verdict: PASS
Residue: none
Binding: yes — mechanical

### GATE RECORD
Reported: yes — review + correction table rendered before build; evidence summarized before this record
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin (directive) · date: 2026-07-07

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): do spawned agents actually cite orient-command output early in their transcripts; does persona read-cost per spawn drop

### Decisions (ADR)
- [AI] specify — chose upgrade bodies + prose conventions; rejected engine-rendered persona roster index in status (rejected for now — engine change, prose convention gets ~90% of the win) · per-persona byte budget test (rejected — premature; revisit if personas bloat)
- [human] freeze — froze §3 @ v1 (approved by Tin ('fix All prose/personas directly', 2026-07-07))
- [AI] build — strategy used: as planned; add-advisor needed its own patch phrasing (no semicolon variant), and the template synced to 3 tooling trees (engine-tree twins), not just canonical
- [AI] verify — gate PASS (reviewed by Tin (directive))

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).
  - [SPEC · seeded] if agents keep whole-roster reads despite the frontmatter-first instruction, add an engine-rendered persona roster line (slug · flow · vibe) to status/check — the recorded escalation (evidence: TASK §1 ⚠) [→ roster-status-line]

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

  - [TDD · folded] check a new guard for VACUOUS pass against the current tree before calling it red — an assertion satisfied by unrelated existing prose guards nothing (evidence: M3 'frontmatter' matched last task's phrase) [folded foundation-version 65]
  - [ADD · folded] a review finding derived from grep must be re-verified fence-aware before it becomes scope — the 'leaked skeletons' finding was a false positive (evidence: fenced ## headers in 2 personas) [folded foundation-version 65]
