# TASK: Seed a portable persona-aware worker PROMPT template + per-platform adapter stubs

slug: persona-subagent-prompt · created: 2026-06-29 · stage: mvp
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
  - `add-method/skill/add/streams.md:## The worker contract` (≈154-211) — the agent-agnostic PROMPT.md template (XML `<objective>`/`<persona>`/`<strategy>`/`<touch_boundary>`/`<context_files>`/`<expertise>`). The `<persona>` (≈169-180) + `<expertise>` (≈208-211) blocks are the persona-injection point THIS task wires to `.add/personas/<slug>.md`.
  - `add-method/skill/add/streams.md:## The spawn adapter` (≈241-256) — the existing per-runner adapter table + HONESTY note ("only the Claude Code column is verified … illustrative shapes — confirm with find-docs"). The per-platform adapter stubs extend here.
  - `.add/personas/<slug>.md` (FROZEN schema, persona-setup) — the injection SOURCE: `## Identity` → the worker persona, `## Critical Rules` → its constraints, `## Success Metrics` → its done-bar. Read-only.
  - `add-method/tooling/templates/*.tmpl` + `add-method/tooling/add.py:_render_template` — the seed/render seam; a portable PROMPT template can ship here (3-tree parity), rendered locally (NO-EXEC), mirroring persona-setup's seed idiom.
  - `add-method/tooling/test_streams_*` / worker-contract doc-truth tests — the pattern the new injection test mirrors.
Context (working folder):
  - `.add/milestones/persona-learning-loop/MILESTONE.md` — shared decisions: ONE canonical portable PROMPT body + thin per-platform adapter stubs (NOT N divergent prompts); platform set = the 9 agents ADD already onboards (Claude Code · Codex · opencode · Cursor · Windsurf · Copilot · Cline · Aider · Gemini CLI); HONESTY RULE — only Claude Code verified, the rest labelled illustrative until find-docs confirms.
  - the persona-injection point is a SHARED/RISKY contract (freeze first) that advisor-persona-select depends on.
Honors (patterns / conventions):
  - agent-agnostic worker contract — no runner-specific tokens in the portable body; only the thin spawn adapter differs per runner.
  - engine NO-EXEC — the engine seeds/renders the template locally; it NEVER spawns the worker or reaches the network.
  - honesty rule — never claim a platform verified until confirmed; illustrative stubs are labelled.
  - 3-tree skill parity (streams.md) + 3-tree engine/template parity (if a template file ships); red/green TDD.
Anchors the contract cites: the streams.md `<persona>`/`<expertise>` injection point · the `.add/personas/<slug>.md` section→block mapping · the portable PROMPT template (`{{PERSONA_SLUG}}`) · the per-platform adapter-stub schema + honesty labelling.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Persona-aware portable worker PROMPT — the streams.md worker contract's `<persona>`/`<expertise>` blocks LOAD the active `.add/personas/<slug>.md`, mapping its sections into the PROMPT (Identity→persona, Critical Rules→constraints, Success Metrics→done-bar). ONE canonical portable body (no runner tokens) is shipped as a seedable template the engine renders locally (NO-EXEC); thin per-platform adapter stubs map the spawn to each of the 9 onboarded runners — Claude Code verified, the rest labelled illustrative.
Framings weighed: extend the EXISTING streams.md worker contract + adapter table with persona-injection + ship one seedable template (chosen — reuses the agent-agnostic contract; no N divergent prompts) · a brand-new standalone subagent file per runner (rejected — divergence + drift) · a Claude-Code-only subagent (rejected — milestone wants cross-runner)
Must:
<must>
  - The portable worker PROMPT template carries a documented persona-injection: `<persona>` loads the active persona's `## Identity` + `## Critical Rules`; `<expertise>` loads the matched persona; `## Success Metrics` becomes the worker's done-bar. A `{{PERSONA_SLUG}}` placeholder names which `.add/personas/<slug>.md` to load.
  - ONE canonical portable body — no runner-specific tokens; the per-platform difference is ONLY the thin spawn adapter.
  - The template is a shipped, seedable artifact the engine renders LOCALLY (no spawn, no network); offline still works (fail-safe), mirroring persona-setup's NO-EXEC seed.
  - Per-platform adapter stubs cover the 9 onboarded agents (Claude Code · Codex · opencode · Cursor · Windsurf · Copilot · Cline · Aider · Gemini CLI). The Claude Code stub is the verified reference; every other stub is explicitly labelled illustrative (honesty rule).
  - When no persona is matched/seeded, the worker still spawns with the generic `<persona>` (degrade-safe; never blocks a build).
  - 3-tree parity: streams.md (+ any template file) lands byte-identical across the skill (and engine/template) trees.
</must>
Reject:
<reject>
  - a per-platform adapter that diverges the PROMPT BODY (not just the spawn mapping) -> "prompt_body_divergence"
  - labelling a non-Claude-Code stub as verified without find-docs confirmation -> "unverified_platform_claim"
  - the engine spawning the worker or fetching over the network to build the PROMPT -> "subagent_engine_no_exec"
  - a persona injection that loses a section (Identity / Critical Rules / Success Metrics) from the load mapping -> "persona_injection_incomplete"
</reject>
After:
<after>
  - The streams.md worker contract documents the persona-injection mapping; the portable body stays runner-token-free; `{{PERSONA_SLUG}}` names the persona to load.
  - A seedable portable PROMPT template exists and renders locally with no network/spawn; the Claude Code path injects the persona's identity + critical-rules + success-metrics.
  - The 9 per-platform adapter stubs exist; only Claude Code is marked verified, the rest illustrative; a test asserts the labelling.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ which persona a worker loads is decided UPSTREAM (advisor-persona-select owns the selection) — THIS task only freezes the injection POINT + mapping + `{{PERSONA_SLUG}}` slot, not the selection logic — lowest confidence because the boundary between "injection point" (here) and "selection" (advisor-persona-select) must be clean or the two tasks collide; if wrong: the placeholder shape changes and advisor-persona-select rebuilds. (Mitigation: freeze ONLY the slot + mapping here; selection fills the slot later.)
  - [ ] shipping the portable body as a seedable `templates/` file (vs leaving it inline in streams.md only) is worth the extra artifact — if wrong: keep it inline in streams.md and drop the template file (the injection mapping is the real deliverable).
  - [ ] the existing 9-agent onboarding set is the right platform list (no more, no fewer) — if wrong: the stub set grows/shrinks with the installer's agent list.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the worker PROMPT loads the active persona by slug
  Given the streams.md worker contract and a {{PERSONA_SLUG}} placeholder
  When the persona-injection is read
  Then the <persona> block loads .add/personas/<slug>.md's "## Identity" and "## Critical Rules"
  And the "## Success Metrics" becomes the worker's done-bar

Scenario: one canonical portable body, no runner tokens
  Given the portable PROMPT template body
  When it is inspected
  Then it contains no runner-specific token (no vendor tool / model id / spawn API)
  And the per-platform difference lives only in the spawn-adapter stubs

Scenario: the template renders locally with no network or spawn (NO-EXEC, fail-safe)
  Given the engine rendering the PROMPT template
  When it runs offline
  Then it produces the PROMPT with no outbound network call and no process spawn
  And it succeeds offline

Scenario: the 9 per-platform stubs exist with the honesty labelling
  Given the spawn-adapter stubs
  When they are read
  Then a stub exists for each of the 9 onboarded agents
  And only the Claude Code stub is marked verified; every other is labelled illustrative

Scenario: a non-Claude-Code stub claimed verified is rejected (honesty)
  Given an adapter stub for a non-Claude-Code runner
  When it is marked verified without find-docs confirmation
  Then it is rejected with unverified_platform_claim
  And the doc-truth test fails

Scenario: degrade-safe when no persona is matched
  Given no persona seeded/matched for a task
  When the worker spawns
  Then it uses the generic <persona> block
  And the build is not blocked

Scenario: the change is byte-identical across the skill trees
  Given the streams.md (+ template) edit
  When the trees are compared
  Then the persona-injection + stubs are byte-identical in each
  And the parity test passes
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

PERSONA-INJECTION POINT — added to `streams.md` worker contract (the SHARED/RISKY contract)
  (described inline — no bare triple-dash / line-start `##` so the §3 span stays intact)
  • The portable PROMPT body gains a `{{PERSONA_SLUG}}` placeholder naming which
    `.add/personas/<slug>.md` to load (the SLOT; selection is advisor-persona-select's job).
  • SECTION → BLOCK mapping (all three sections map; none dropped):
      - persona `## Identity`        → the worker `<persona>` identity line(s)
      - persona `## Critical Rules`  → the worker `<persona>` / `<touch_boundary>` constraints
      - persona `## Success Metrics` → the worker's done-bar (the confidence/▸done check)
  • `<expertise>` loads the matched persona when the runner supports specialist injection;
    otherwise the inlined `<persona>` IS the expertise (existing fallback, unchanged).
  • DEGRADE: no persona matched → the generic `<persona>` block (today's behavior); never blocks.

PORTABLE BODY — ONE canonical body, NO runner-specific tokens. Shipped as a seedable artifact
  (`templates/PROMPT.persona.md.tmpl`, 3-tree parity) the engine renders LOCALLY via the existing
  `_render_template` seam — NO spawn, NO network; offline-safe. (Assumption flagged: the file may
  instead stay inline in streams.md — see the freeze flag.)

PER-PLATFORM ADAPTER STUBS — extend the existing streams.md spawn-adapter table to the 9 onboarded
  agents: Claude Code (VERIFIED reference) · Codex · opencode · Cursor · Windsurf · Copilot · Cline ·
  Aider · Gemini CLI (each ILLUSTRATIVE, labelled, until find-docs confirms). Each stub maps ONLY the
  spawn (how to launch + pass the rendered PROMPT) — never the body.

ENGINE: NO-EXEC throughout — seeds/renders locally, never spawns the worker, never fetches.

ERROR CODES (every §1 Reject has a documented response)
  prompt_body_divergence       -> an adapter that changes the BODY (not just the spawn) is rejected.
  unverified_platform_claim    -> a non-Claude-Code stub marked verified w/o find-docs is rejected.
  subagent_engine_no_exec      -> INVARIANT: the seed/render path performs no network IO and no spawn.
  persona_injection_incomplete -> the mapping MUST cover all three persona sections; none dropped.

PARITY — the streams.md change (+ template file) lands byte-identical in all 3 skill trees
  (and, for the template, the 3 engine/template trees).

VERIFICATION — doc-truth tests assert: the injection mapping covers all 3 sections · the body is
  runner-token-free · the 9 stubs exist with correct verified/illustrative labels · NO-EXEC on the
  seed/render path · parity holds.

Least-sure flag surfaced at freeze: ⚠ [contract] the injection POINT vs the SELECTION boundary —
this task freezes only the `{{PERSONA_SLUG}}` slot + the section→block mapping; advisor-persona-select
(downstream) owns WHICH persona fills the slot. If the slot shape is wrong, advisor-persona-select
rebuilds against a changed contract. Mitigation: freeze the minimal slot + mapping; keep selection out.
Second flag: [contract] shipping a separate `templates/PROMPT.persona.md.tmpl` vs keeping the body
inline in streams.md — if the extra artifact is not worth it, drop the file and keep the mapping inline
(the injection mapping is the real deliverable either way).

Status: FROZEN @ v1 — approved by Tin Dang
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag. -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + Reject scenario has one assertion (doc-truth + parity + NO-EXEC)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_prompt_injection_maps_all_three_sections: streams.md documents Identity→persona, Critical Rules→constraints, Success Metrics→done-bar, with a {{PERSONA_SLUG}} slot
  - test_portable_body_no_runner_tokens: the portable body contains no runner-specific token
  - test_template_renders_offline_no_exec: the PROMPT template renders with no network/spawn (NO-EXEC scan of the render path + offline render)
  - test_nine_platform_stubs_present: a stub exists for each of the 9 onboarded agents
  - test_only_claude_code_verified: only the Claude Code stub is labelled verified; the other 8 are labelled illustrative
  - test_degrade_no_persona_generic: streams.md states the generic <persona> is used when no persona is matched (never blocks)
  - test_subagent_prompt_3tree_parity: the streams.md (+ template) change is byte-identical across trees
</test_plan>

Tests live in: `add-method/tooling/test_persona_subagent_prompt.py` · MUST run red before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/streams.md` `.claude/skills/add/streams.md` `add-method/src/add_method/_bundled/skill/add/streams.md` `add-method/tooling/templates/PROMPT.persona.md.tmpl` `.add/tooling/templates/PROMPT.persona.md.tmpl` `add-method/src/add_method/_bundled/tooling/templates/PROMPT.persona.md.tmpl` `add-method/tooling/test_persona_subagent_prompt.py` `add-method/tooling/engine_pin.py`
Strategy (ordered batches): 1. streams.md — document the persona-injection mapping in the worker contract + extend the spawn-adapter table to the 9 agents with verified/illustrative labels. 2. ship the portable `templates/PROMPT.persona.md.tmpl` (if the freeze keeps the file) with `{{PERSONA_SLUG}}` + the section→block load lines. 3. mirror byte-identically (skill ×3, template ×3). 4. tests (doc-truth + NO-EXEC + parity). 5. re-aim engine pins ONLY if a template file ships (templates are inside the engine digest? confirm — if templates are not in ENGINE_PKG, no re-pin). 6. lean fence — reclaim from streams.md prose if needed. Run red→green.
Known-problem fixes: if the freeze drops the template file, scope shrinks to streams.md-only (no pin change) · lean fence may trip (streams.md pool) → reclaim from the same guide · honesty labels must match the existing streams.md wording ("verified" / "illustrative") for the doc-truth test · NO-EXEC scan must cover the render path, not just a predicate.
Strategy actually used: kept the template file (freeze's primary path). Put the bulk (portable body + 9-agent adapter stubs) in `templates/PROMPT.persona.md.tmpl` (tooling/, OUTSIDE the lean fence) and kept streams.md additions minimal (a `{{PERSONA_SLUG}}` load line + pointer). Two surface-test conflicts surfaced at full-suite: (1) the template's worker-contract XML tags tripped test_template_form_tags (templates must not carry guide XML tags) → rewrote the template body with markdown headers instead of `<objective>`/`<persona>`/… (no XML duplication of streams.md — cleaner, no drift); (2) "fold"/"touch boundary" read as slang on the extended surface → reworded. Also a tests-phase fix: my test read streams.md from the engine dir (wrong) → rewound to tests, repointed at the skill tree, re-crossed. Reclaimed ~373 B from streams.md prose for the lean pool (ratios kept; test_skill_lean untouched). Engine + pins untouched (templates are in neither pin).
Safety rule (feature-specific): the engine never spawns the worker or fetches; the body stays runner-token-free; no stub claims verified without find-docs.
Code lives in: `add-method/skill/add/` + `add-method/tooling/templates/`
Constraints: do NOT change any test or the contract; do NOT diverge the portable body per runner; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 2441/0
- [x] coverage did not decrease — 7 new doc-truth/parity/NO-EXEC tests; none removed
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; the one test fix (streams.md path) was done in the TESTS phase with tests→build re-crossed; build edits were template + streams.md only
- [x] the green was EARNED — doc-truth tests assert real content tokens; read the final template + streams.md in full, coherent (portable body, 3-section mapping, generic fallback, 9 honest stubs); not token-stuffed
- [x] concurrency / timing — n/a (a render template + guide prose; the engine never spawns the worker)
- [x] no exposed secrets, injection openings, or unexpected dependencies — template/prose only; no code, no dependency
- [x] layering & dependencies follow CONVENTIONS.md — template carries no guide XML tags (test_template_form_tags green); no extended-surface slang (test_ubiquitous_language green); 3-tree parity held; engine pins untouched (add.py md5 == pin)
- [x] reviewed — auto-resolved under `autonomy: auto` (no residue); self refute-read (doc/template, content-mapped) + human spot-audit backstop

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
- [x] streams.md worker contract carries the persona-injection (`{{PERSONA_SLUG}}` load line, the 3-section mapping) — CONFIRMED by reading streams.md + the injection test
- [x] the template lists all 9 agents with only Claude Code verified, the rest illustrative — CONFIRMED by the doc-truth tests (count("verified")==1) + a read
- [x] the portable body (before "## Adapter stubs") has no runner-specific tokens — CONFIRMED by the body-scan test
- [x] the template renders offline with no network/process-launch; pins consistent — CONFIRMED by the NO-EXEC render-path test + the add.py md5 == pin check

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING — n/a (no production code); the 7 new test methods all run; the template is rendered via the existing `_render_template` seam
- [x] DEAD-CODE — no new unused symbol (no production code added)
- [x] SEMANTIC — read the edited streams.md `<persona>` injection + the full template (body + adapter stubs): the persona-load mapping covers all 3 sections, the generic fallback never blocks, the 9 stubs carry one canonical body with only Claude Code verified (honesty rule); reads coherently, no token-stuffing.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self · adversarially checked: whether the doc-truth tests could pass on incoherent/divergent content. The body-scan test would catch a runner token leaking into the body; the count("verified")==1 test would catch an over-claimed stub; the NO-EXEC test scans the real render path. Read the final template in full — one canonical body, 9 honestly-labelled stubs, real 3-section mapping. Doc/template change → self refute-read is proportionate.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
Advisor: self (diff review)
1. Security: CLEAR — template + guide prose; no code, no secrets; the engine never spawns the worker or fetches (the body explicitly forbids it; render path is NO-EXEC, test-asserted).
2. Concurrency: CLEAR — no runtime/engine change; the template is rendered, not executed.
3. Architecture: CLEAR — body has no runner tokens (one canonical body, per-runner spawn only); template carries no guide XML tags; honesty rule preserved; 3-tree parity held; engine pins untouched.
Verdict: PASS
Residue: none
Binding: advisory — sensitivity: docs/template (no engine behavior)
Verdict: <PASS | HARD-STOP>
Residue: <none | summary>
Binding: <yes — mechanical | advisory — <sensitivity>>

### GATE RECORD
Outcome: PASS
Reviewed by: auto-resolved (autonomy: auto, no residue) — owner Tin Dang · date: 2026-06-29

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <stub-drift / unverified-claim regressions>

### Decisions (ADR)
- [AI] specify — chose extend the EXISTING streams.md worker contract + adapter table with persona-injection + ship one seedable template; rejected a brand-new standalone subagent file per runner (rejected — divergence + drift) · a Claude-Code-only subagent (rejected — milestone wants cross-runner)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: kept the template file (freeze's primary path). Put the bulk (portable body + 9-agent adapter stubs) in `templates/PROMPT.persona.md.tmpl` (tooling/, OUTSIDE the lean fence) and kept streams.md additions minimal (a `{{PERSONA_SLUG}}` load line + pointer). Two surface-test conflicts surfaced at full-suite: (1) the template's worker-contract XML tags tripped test_template_form_tags (templates must not carry guide XML tags) → rewrote the template body with markdown headers instead of `<objective>`/`<persona>`/… (no XML duplication of streams.md — cleaner, no drift); (2) "fold"/"touch boundary" read as slang on the extended surface → reworded. Also a tests-phase fix: my test read streams.md from the engine dir (wrong) → rewound to tests, repointed at the skill tree, re-crossed. Reclaimed ~373 B from streams.md prose for the lean pool (ratios kept; test_skill_lean untouched). Engine + pins untouched (templates are in neither pin).
- [AI] verify — gate PASS (reviewed by auto-resolved (autonomy: auto, no residue) — owner Tin Dang)

### Spec delta
Forward changes for the next loop — one line each, tagged `[SPEC · open|seeded|dropped]`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency (`DDD · SDD · UDD · TDD · ADD`), status `open`.
