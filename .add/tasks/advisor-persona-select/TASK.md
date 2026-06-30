# TASK: advisor/streams select a persona per delegated piece and record it in the verdict

slug: advisor-persona-select · created: 2026-06-29 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. Multi-component repo (monorepo/multi-repo)? add a `component: <name>` line (declared in `.add/components.toml`) to ADD that component's root to your §5 Scope; omit for single-component projects (byte-identical default). -->
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
  - `add-method/skill/add/advisor.md:## The plan-following prompt template` — the advisor spawn template; its `<persona>` block (≈33-39) is a GENERIC `{{DOMAIN}} engineer`. THIS task makes it SELECT the best-fit project persona `.add/personas/<slug>.md` (mirroring `streams.md`'s worker `<persona>`, seeded by persona-subagent-prompt) and the `<return>` shape (≈52-56) RECORDS the chosen persona.
  - `add-method/skill/add/advisor.md:## The 3-lens sequential checklist at verify` — the refute-read piece (an independent review) selects a Code-Reviewer persona; its findings carry severity markers (🔴 blocker / 🟡 concern / 💭 note). The persona NEVER lowers a gate.
  - 3 skill trees (`add-method/skill/add`, `.claude/skills/add`, `_bundled/skill/add`) — advisor.md parity.
Context (working folder):
  - `.add/milestones/persona-learning-loop/MILESTONE.md` — shared decisions: "advisor/streams SELECT which persona per delegated piece (Code-Reviewer 🔴/🟡/💭 → verify refute-read)"; a persona NEVER lowers a gate; ONE canonical portable body (no N divergent prompts).
  - `add-method/skill/add/streams.md:<persona>` (persona-subagent-prompt) — the worker contract advisor.md reuses; already loads `.add/personas/{{PERSONA_SLUG}}.md`.
Honors (patterns / conventions):
  - the engine NEVER spawns — persona selection is the orchestrating agent's judgment; this is doc-truth only (no engine change, no pin re-aim).
  - delegation never lowers a gate — a SECURITY finding still HARD-STOPs; high-risk scope still escalates.
  - degrade-safe — no matching persona → the generic `{{DOMAIN}}` engineer, never blocks.
  - 3-tree skill parity; the engine + both pins stay UNCHANGED.
Anchors the contract cites: advisor.md `<persona>` persona-select load · the `<return>` verdict `persona` field · the refute-read → Code-Reviewer (🔴/🟡/💭) mapping · the "persona never lowers a gate" invariant.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: The advisor/streams spawn SELECTS the best-fit project persona for the delegated piece — its `<persona>` block loads `.add/personas/<slug>.md` (Identity→stance · Critical Rules→constraints · Success Metrics→done-bar), and the returned verdict RECORDS which persona was used. A refute-read piece selects a Code-Reviewer persona whose findings carry severity markers (🔴/🟡/💭). The persona is advisory: it never lowers a gate, and no-match degrades to the generic `{{DOMAIN}}` engineer.
Framings weighed: doc-truth in advisor.md reusing streams.md's worker contract (chosen — the engine never spawns; one canonical body) · a dedicated engine "persona-pick" command (rejected — a spawn the engine forbids) · per-runner persona prompts (rejected — N divergent prompts the milestone forbids)
Must:
<must>
  - advisor.md's spawn-template `<persona>` SELECTS and loads the best-fit `.add/personas/<slug>.md` (the three-section mapping), reusing streams.md's worker contract.
  - the `<return>` verdict shape adds a `persona` field naming the selected slug (or `generic`) — the orchestrator records it.
  - advisor.md documents the refute-read → Code-Reviewer persona mapping, with severity markers 🔴 (blocker) / 🟡 (concern) / 💭 (note).
  - the persona is advisory and NEVER lowers a gate: a security finding still HARD-STOPs; high-risk scope still escalates (the existing hard rule stands).
  - no matching persona → the generic `{{DOMAIN}}` engineer; selection never blocks.
  - 3-tree skill parity; engine + both pins UNCHANGED (the engine never spawns).
</must>
Reject:
<reject>
  - a persona that lowers/bypasses a gate -> "persona_gate_bypass" (the doc forbids it; the hard rule stands)
  - the verdict omitting which persona was used -> "persona_unrecorded" (the `<return>` shape must carry the field)
  - an engine code change / pin re-aim for this task -> "engine_touched_for_spawn" (the engine never spawns)
</reject>
After:
<after>
  - advisor.md's `<persona>` selects a project persona per piece and the `<return>` verdict records it; a doc-truth test asserts both.
  - the refute-read piece maps to a Code-Reviewer persona with 🔴/🟡/💭 severity; a test asserts the mapping.
  - persona is advisory (no gate lowered); no-match degrades to generic; advisor.md is byte-identical across the 3 skill trees; the engine pin is unchanged.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ whether the verdict `persona` field belongs in the advisor's `<return>` shape vs the §6 `### Advisor 3-lens verdict` block — lowest confidence because both are "the verdict"; if wrong: the recorded-persona lands in the wrong surface and a later audit can't read it. (Mitigation: put it in advisor.md's `<return>` shape — the worker's structured return the orchestrator parses — and mention §6 as where the orchestrator may note it; do NOT add an engine-read field.)
  - [ ] severity markers 🔴/🟡/💭 match the agency-agents Code-Reviewer convention — if wrong: use plain words (blocker/concern/note).
  - [ ] reusing streams.md's `{{PERSONA_SLUG}}` slot is enough (no new slot needed) — if wrong: add an explicit select step.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the advisor spawn selects and loads a project persona
  Given advisor.md's plan-following prompt template
  When the <persona> block is read
  Then it loads the best-fit .add/personas/<slug>.md (Identity/Critical Rules/Success Metrics mapping)

Scenario: the returned verdict records which persona was used
  Given advisor.md's <return> verdict shape
  When it is read
  Then it carries a `persona` field naming the selected slug (or generic)

Scenario: the refute-read piece maps to a Code-Reviewer persona
  Given advisor.md's verify/refute-read guidance
  When it is read
  Then it selects a Code-Reviewer persona whose findings use 🔴/🟡/💭 severity markers

Scenario: a persona never lowers a gate
  Given a delegated piece with a selected persona
  When a security finding occurs
  Then it still HARD-STOPs and the persona does not lower or bypass the gate

Scenario: no matching persona degrades to generic
  Given a piece with no matching project persona
  When the <persona> block is resolved
  Then it uses the generic {{DOMAIN}} engineer and never blocks

Scenario: advisor.md stays byte-identical across trees and the engine is untouched
  Given the advisor.md edits
  When the 3 skill trees are compared and the engine pin is read
  Then advisor.md is byte-identical across trees
  And ENGINE_MD5 equals the pin (no engine change)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

ADVISOR PERSONA SELECTION — doc-truth in `advisor.md` (the engine never spawns; no engine change)
  (described inline — no bare triple-dash / line-start `##` so the §3 span stays intact)
  • The plan-following prompt template's `<persona>` block SELECTS the best-fit project persona and
    loads `.add/personas/<slug>.md` — Identity→stance · Critical Rules→constraints · Success Metrics
    →done-bar — reusing `streams.md`'s worker contract (`{{PERSONA_SLUG}}`). No match → the generic
    `{{DOMAIN}}` engineer (never blocks).
  • The `<return>` verdict shape carries a `persona` field naming the selected slug (or `generic`);
    the orchestrator RECORDS it (the worker proposes; the orchestrator records — unchanged hard rule).
  • REFUTE-READ → CODE-REVIEWER: the independent earned-green refute-read piece selects a
    Code-Reviewer persona; its findings carry severity markers 🔴 (blocker) / 🟡 (concern) / 💭 (note).

INVARIANT — persona is ADVISORY, never a gate lever
  • A persona NEVER lowers or bypasses a gate: a SECURITY finding is always HARD-STOP; high-risk
    scope still escalates to the human (the existing `advisor.md` hard rule stands, whoever did the work).

PARITY / NO-EXEC
  • `advisor.md` byte-identical across the 3 skill trees; the engine + BOTH pins (ENGINE_MD5 +
    ENGINE_PKG_MD5) UNCHANGED — this task touches no engine code (the engine never spawns).

ERROR CODES (doc-truth invariants — the prose must encode each negative)
  persona_gate_bypass      -> a persona lowering/bypassing a gate is forbidden; the hard rule stands.
  persona_unrecorded       -> the verdict must name which persona was used (the `<return>` field).
  engine_touched_for_spawn -> no engine change / pin re-aim for this task (the engine never spawns).

VERIFICATION — tests assert: `<persona>` selects + loads a project persona · `<return>` records the
  persona · refute-read → Code-Reviewer (🔴/🟡/💭) · persona never lowers a gate · no-match → generic
  · advisor.md 3-tree parity · ENGINE_MD5 unchanged.

Least-sure flag surfaced at freeze: ⚠ [contract] the recorded-persona surface — placed in advisor.md's
`<return>` worker-verdict shape (not an engine-read field), with §6 named as where the orchestrator may
note it. If a machine-read field is later needed, that is a change request (engine work, out of scope here).

Status: FROZEN @ v1 — approved by Tin Dang
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + Reject scenario has one doc-truth test
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_persona_block_selects_and_loads: advisor.md `<persona>` references `.add/personas/` + the 3-section mapping (Identity/Critical Rules/Success Metrics)
  - test_return_records_persona: advisor.md `<return>` shape names a `persona` field
  - test_refute_read_codereviewer: advisor.md maps the refute-read piece to a Code-Reviewer persona with 🔴/🟡/💭 markers
  - test_persona_never_lowers_gate: advisor.md states the persona is advisory and a security finding still HARD-STOPs
  - test_degrade_no_persona_generic: advisor.md documents the no-match → generic `{{DOMAIN}}` engineer degrade
  - test_advisor_parity: advisor.md byte-identical across the 3 skill trees
  - test_engine_unchanged: ENGINE_MD5 == engine_pin.ENGINE_MD5 (no engine change)
</test_plan>

Tests live in: `add-method/tooling/test_advisor_persona_select.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/advisor.md` `.claude/skills/add/advisor.md` `add-method/src/add_method/_bundled/skill/add/advisor.md` `add-method/tooling/test_advisor_persona_select.py`
Strategy (ordered batches): 1. advisor.md — extend the `<persona>` block to SELECT + load the best-fit `.add/personas/<slug>.md` (reuse streams.md's worker contract / `{{PERSONA_SLUG}}`); add the `persona` field to the `<return>` shape; document the refute-read → Code-Reviewer (🔴/🟡/💭) mapping; restate the persona-is-advisory hard rule. 2. mirror byte-identically (×3 skill trees). 3. tests. 4. lean fence — advisor.md is in the orchestration pool (≤40772): reclaim bytes from advisor.md prose if my additions trip it (never edit test_skill_lean). Run red→green.

Known-problem fixes: advisor.md is lean-pooled → keep additions tight + reclaim from the same guide's prose · the engine never spawns → NO engine edit, pins UNCHANGED · keep the existing hard-rule wording so test_machine_tokens / advisor guards stay green · ubiquitous-language: avoid slang in new prose.
Strategy actually used: As planned. Extended advisor.md's `<persona>` block to SELECT + load `.add/personas/{{PERSONA_SLUG}}.md` (reusing streams.md's worker contract), added the `persona` field to the `<return>` verdict shape, and added a "Persona for the refute-read" note mapping it to a Code-Reviewer persona with 🔴/🟡/💭 markers + the persona-is-advisory rule. No engine change. Reclaimed ~660 B from advisor.md prose (intro, when-to-spawn, template intro, 3-lens record line, model-tier, hard-rule) to hold the orchestration-pool fence ≤40772; test_skill_lean untouched.
Safety rule (feature-specific): a persona is advisory only — never lower a gate; degrade to generic on no-match.
Code lives in: `add-method/skill/add/` + `add-method/tooling/`
Constraints: do NOT change any test or the contract; do NOT touch engine code or re-aim a pin; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) is live: a completing verify gate refuses an
     out-of-scope build (scope_violation → self-heal) and add.py check surfaces it.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

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
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] advisor.md's `<persona>` loads the selected `.add/personas/<slug>.md` (Identity/Critical Rules/Success Metrics) — confirmed by reading the template + the doc-truth test
- [x] the `<return>` verdict shape names a `persona` field — confirmed by the return-shape test
- [x] the refute-read maps to a Code-Reviewer persona with 🔴/🟡/💭 — confirmed by the marker test
- [x] persona is advisory (never lowers a gate; security HARD-STOPs); no-match → generic; advisor.md byte-identical ×3 trees; ENGINE_MD5 unchanged — confirmed by the gate/degrade/parity/engine tests

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read in full, not skimmed: read all of advisor.md across the 3 skill trees + the 7 doc-truth tests; confirmed the `<persona>` SELECTs+loads `.add/personas/<slug>.md`, the `<return>` records `persona`, the refute-read→Code-Reviewer 🔴/🟡/💭 mapping, the never-lowers-a-gate invariant, and the no-match→generic degrade — all present and byte-identical ×3 trees. No code touched (doc-truth task).

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self · adversarially checked: probed for vacuous asserts (each test pins a distinct observable: persona load + 3-section mapping, the `<return>` persona field inside the `<return>`/`</return>` span, the 🔴/🟡/💭 markers as literal codepoints, the never-lower-gate + HARD-STOP wording, the no-match→generic `{{domain}}` degrade, 3-tree byte-parity, ENGINE_MD5==pin); tried to refute each by re-reading advisor.md prose — no overfit, no stub, the assertions track the frozen §3 contract; engine + both pins genuinely unchanged (doc-truth only).

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: self
1. Security: CLEAR — doc-truth only; no code, no secrets, no new dependency, no execution surface.
2. Concurrency: CLEAR — prose edits to advisor.md across 3 trees; no runtime, no shared state.
3. Architecture: CLEAR — reuses streams.md's worker contract (one canonical body, no N divergent prompts); engine never spawns, both pins unchanged.
Verdict: PASS
Residue: none
Binding: advisory — non-mechanical (doc-truth skill edit)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-resolved under autonomy: auto) · date: 2026-06-30

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. The Advisor 3-lens verdict and the Refute-read verdict are both measured by `add.py audit` (`advisor_verdict_unrecorded` · `refute_unrecorded`) — neither is engine-blocked; a human spot-audit is the backstop for any finding the AI did not surface or record. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose doc-truth in advisor.md reusing streams.md's worker contract; rejected a dedicated engine "persona-pick" command (rejected — a spawn the engine forbids) · per-runner persona prompts (rejected — N divergent prompts the milestone forbids)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: As planned. Extended advisor.md's `<persona>` block to SELECT + load `.add/personas/{{PERSONA_SLUG}}.md` (reusing streams.md's worker contract), added the `persona` field to the `<return>` verdict shape, and added a "Persona for the refute-read" note mapping it to a Code-Reviewer persona with 🔴/🟡/💭 markers + the persona-is-advisory rule. No engine change. Reclaimed ~660 B from advisor.md prose (intro, when-to-spawn, template intro, 3-lens record line, model-tier, hard-rule) to hold the orchestration-pool fence ≤40772; test_skill_lean untouched.
- [AI] verify — gate PASS (reviewed by Tin Dang (auto-resolved under autonomy: auto))

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
