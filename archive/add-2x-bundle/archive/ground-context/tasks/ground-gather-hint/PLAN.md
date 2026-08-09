# TASK: Add the gather-method hint — prefer a subagent/skim sweep + deepen task-specifically

slug: ground-gather-hint · created: 2026-06-11 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it. -->
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
  - `add-method/skill/add/phases/0-ground.md` (×3 skill trees, byte-identical md5 5aa4c645 after task 1) — the ground guide; `## Gather` (Touches/Context/Honors/Anchors) + `## AI prompt` (Role/Steps). Task 2 adds the gather-METHOD hint (HOW to gather efficiently), distinct from task 1's WHAT (the categories).
  - `add-method/tooling/test_ground_context.py` (existing, from task 1) — EXTEND with a method-hint assertion (the guide names a subagent/index/skim sweep + task-specific deepening) + keep the ×3 parity / engine-pin guards.
Context (working folder):
  - docs — `.add/milestones/ground-context/MILESTONE.md` (the **gather-method hint** shared decision: "prefer a small-model subagent / fast index / skim for the broad sweep + deepen task-specifically; a recommendation, never an engine-spawned action — tool-agnostic"); task 1's §7 follow-up (the guide intro under-describes the broadened gather — a candidate to align here).
  - no todos/config/data relevant to this prose task.
Honors (patterns / conventions):
  - **Dogfood parity** — `0-ground.md` ×3 byte-identical; the extended guard asserts it.
  - **§0/guide stays lean · lean-over-GSD** — a compact hint, not a heavy methodology section.
  - **gather-method hint = a RECOMMENDATION, never engine-spawned** (milestone shared decision) — the guide RECOMMENDS a subagent; `add.py` never spawns one (tool-agnostic). No engine edit → pin holds.
  - **test_ground_phase invariants** — keep `## 0`/`GROUND` (template, untouched) and the guide saying "gather"/"codebase".
  - **measure untouched** — no `add.py` change (engine == engine_pin).
Anchors the contract cites: the NEW gather-method-hint text in `0-ground.md` (`## Gather` and/or the `## AI prompt` Steps) · the EXTENDED `test_ground_context.py` (method-hint present + ×3 parity + engine-pin) · the task-1 §7 intro-coherence follow-up (resolved or re-deferred at §3)

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: The gather-method hint — gather efficiently (subagent/skim sweep) + deepen task-specifically
Framings weighed: a compact "How" line after ## Gather + a Step-0 in the AI prompt (chosen) · a dedicated ## How to gather section · a guide-intro reword only
Must:
<must>
  - `0-ground.md` tells the AI to prefer a small-model SUBAGENT / fast INDEX / SKIM for the BROAD sweep — offload to a cheap context, return a compact map (anti-context-rot).
  - `0-ground.md` tells the AI to DEEPEN task-specifically — follow what THIS task needs deeper into the codebase, never lock a shallow first pass.
  - the hint is a RECOMMENDATION, not an engine action — `add.py` never spawns a subagent (tool-agnostic); no engine edit.
  - the guide's intro is aligned to the broadened gather (task-1 §7 follow-up: "the real current working folder", not only "codebase") — a one-phrase coherence touch.
  - copies stay ×3 byte-identical; the grounding measure is untouched (add.py == engine_pin).
</must>
Reject:
<reject>
  - a guide copy drifts (one edited, mirrors not) -> the ×3 parity guard reds
  - the method hint is missing (no subagent/skim OR no deepen) -> the method-hint guard reds
  - an add.py change appears -> the engine-pin guard reds (the hint must stay a recommendation, never an engine action)
</reject>
After:
<after>
  - `0-ground.md` names the subagent/index/skim sweep + task-specific deepening; the intro reads "working folder"; ×3 byte-identical; add.py == engine_pin; full suite green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the hint lands as a compact "How" line (after ## Gather) + one AI-prompt Step, NOT a dedicated section — lowest confidence because it is the lean-vs-explicit tradeoff again; if too terse the agent skips it, if too heavy the lean guide bloats. Resolved at the §3 freeze.
  - [ ] aligning the guide intro ("codebase" -> "working folder") is folded INTO this task (closing the task-1 §7 follow-up) rather than re-deferred — confirm; if out, the intro stays the high-level summary.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the guide recommends a fast subagent/skim sweep
  Given the gather-method hint in 0-ground.md
  When an agent reads the ground guide
  Then it recommends a small-model subagent / fast index / skim for the broad sweep
  And the gather still cues code tools / never-memory (task 1's WHAT is intact)

Scenario: the guide says to deepen task-specifically
  Given the gather-method hint in 0-ground.md
  When an agent reads it
  Then it says to deepen on what THIS task needs (never lock a shallow first pass)
  And the ## Gather categories from task 1 are still present

Scenario: the hint is a recommendation, not an engine action
  Given the gather-method hint
  When the add.py engine is hashed
  Then it is byte-identical to engine_pin (no subagent is engine-spawned)
  And the §0 template and grounding measure are unchanged

Scenario: all copies stay byte-identical
  Given the guide edits are applied
  When the ×3 0-ground.md copies are md5'd
  Then they hash identically
  And no template/measure change occurred

Scenario: a drifted copy reds the guard
  Given one 0-ground.md copy is edited but its mirrors are not
  When test_ground_context runs
  Then the parity assertion fails
  And the non-parity assertions are unaffected
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
GATHER-METHOD HINT SHAPE  (prose contract — frozen text shapes in 0-ground.md)

0-ground.md gains a compact gather-METHOD hint (HOW — distinct from task 1's WHAT):
  - a "How — gather efficiently:" line at the end of `## Gather`:
      for the BROAD sweep, prefer a small-model SUBAGENT / fast INDEX / SKIM (offload to a
      cheap context, return a compact map); then DEEPEN on what THIS task needs — never lock a
      shallow first pass. A recommendation; the engine never spawns it (tool-agnostic).
  - the `## AI prompt` Steps gain a leading method step (Step 0): sweep broad cheaply
      (subagent/index/skim), then deepen task-specifically.
  - intro coherence (task-1 §7): line 3 "gather the REAL current codebase" -> "gather the REAL
      current working folder" (names the broadened gather; the seven-steps/§0 brand unchanged).

Sync         : 0-ground.md ×3 byte-identical
Guard        : add-method/tooling/test_ground_context.py — EXTENDED (method-hint asserts) + keep ×3 parity + engine-pin
Invariants   : add.py == engine_pin (no engine action) · the §0 template + grounding measure UNTOUCHED ·
               task-1's WHAT (categories · code-tools/never-memory) intact · "gather"/"codebase" still cued
Out of scope : the book prose (02-the-flow ×4 · appendix-c ×4) — still the high-level summary
```

Least-sure flag surfaced at freeze: [contract] hint shape — a compact "How" line + AI-prompt Step 0 + a one-phrase intro reword, vs a dedicated "## How to gather" section; if too terse agents skip it, if too heavy the lean guide bloats. The intro-reword also folds in task-1's §7 coherence follow-up.

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

Coverage target: the method-hint presence + the preserved invariants (structural prose guards)
Plan (extending test_ground_context.py — one test per scenario):
<test_plan>
  - test_guide_recommends_subagent_sweep: assert 0-ground.md names "subagent" + ("index" or "skim") for the broad sweep
  - test_guide_says_deepen_task_specifically: assert it says to "deepen" task-specifically (never lock a shallow first pass)
  - test_intro_names_working_folder: assert the guide intro names "working folder" (task-1 §7 coherence closed)
  - test_hint_is_recommendation_not_engine: assert add.py == engine_pin.ENGINE_MD5 (no engine action) — extends EngineMeasureUntouched
  - (kept from task 1) test_guide_copies_byte_identical: ×3 0-ground.md md5-equal
</test_plan>

Tests live in: `add-method/tooling/test_ground_context.py` · MUST run red (missing method hint) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 803 OK; test_ground_context 13/13 (the 3 GatherMethodHint tests RED→green by the guide edits only)
- [x] coverage did not decrease — +3 tests (GatherMethodHint class); no test removed/weakened
- [x] no test or contract was altered during build — tests written red first, then guide+template made them green; §3 contract untouched
- [x] concurrency / timing of the risky operation is safe — N/A (prose-only: guide + template + test; no runtime path)
- [x] no exposed secrets, injection openings, or unexpected dependencies — N/A (no code/deps added; no security surface)
- [x] layering & dependencies follow CONVENTIONS.md — honors dogfood ×3 parity (md5 ba7147e5) + lean-over-GSD (one "How" line + one Step 0); add.py == engine_pin (no engine action)
- [x] a person reviewed and approved the change — auto-resolved (autonomy: auto); the human owns the milestone-close arc (fold + archive) that immediately follows this final task

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [ ] WIRING (code) — N/A (no code symbols added)
- [ ] DEAD-CODE (code) — N/A (no code symbols added)
- [x] SEMANTIC (prose / non-code) — read in full: 0-ground.md (×3, ba7147e5) — (1) intro line 3 now reads "gather the REAL current working folder" + line 4 names docs/todos/config/data; (2) a "How — gather efficiently:" line closes `## Gather` (subagent/index/skim broad sweep → DEEPEN task-specifically → "a recommendation … the engine never spawns a subagent (tool-agnostic)"); (3) `## AI prompt` Steps gain a leading Step 0 (sweep broad cheaply, then deepen). CONFIRMED: matches the frozen §3 shape in intent; task-1's WHAT (Context categories · code-tools/never-memory) intact; "gather"/"codebase"/"ground" still cued; the `Anchors the contract cites:` measure line untouched; book prose (02-the-flow ×4 · appendix-c ×4) correctly left as the high-level summary (scoped out).

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: auto-resolved (autonomy: auto — prose-only, no security/concurrency/architecture residue; §3 flag was a lean-vs-explicit prose judgment, human-approved at freeze) · date: 2026-06-11

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the method-hint guards in test_ground_context.py (subagent/skim sweep present · deepen present · intro names "working folder" · ×3 parity · engine-pin) red on any drift.
Spec delta for the next loop: ground now tells the AI not just WHAT to gather (the working-folder categories, task 1) but HOW (offload the broad sweep to a cheap context, then deepen task-specifically) — the method now has an opinion on grounding *economics*, not only grounding *completeness*.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] Ground has TWO axes — completeness (WHAT: the working-folder categories) and economics (HOW: sweep broad cheaply via a subagent/index/skim, then deepen task-specifically); naming the economics stops the agent from either skipping context or indexing the whole repo (evidence: this milestone needed BOTH a WHAT task and a HOW task — task 1's categories alone left "never lock a shallow first pass" unsaid).
- [ADD · folded] A method hint can RECOMMEND a tool action (a small-model subagent) while the engine stays tool-agnostic — the guide prose carries the recommendation, add.py spawns nothing, so the engine pin holds across a capability addition (evidence: add.py == engine_pin through both ground-context tasks; the subagent is the orchestrator's choice, never the engine's).
- [TDD · folded] A prose-economics hint is pinnable by token-presence guards the same way a structural hint is — assert "subagent"+("index"|"skim"), "deepen", and "working folder" in the intro; behavior pinned, phrasing free (evidence: GatherMethodHint's 3 tests went RED→green on the guide edits alone, no test touched at build).
- [ADD · folded] Dogfooding the very technique being shipped validates it in-flight — a haiku subagent ran the broad working-folder sweep (returned the ×3/×3 sync md5s + guard list) while the main context deepened on the guard assertions, exactly the sweep-cheap-then-deepen split this task added to the guide (evidence: the build used the method it documents).
