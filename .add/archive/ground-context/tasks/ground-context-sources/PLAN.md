# TASK: Broaden the §0 GROUND gather to the full working-folder context

slug: ground-context-sources · created: 2026-06-11 · stage: mvp
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
  - `add-method/skill/add/phases/0-ground.md` (+ `.claude/skills/add/phases/0-ground.md` + `add-method/src/add_method/_bundled/skill/add/phases/0-ground.md` — ×3 byte-identical, md5 6becb20b) — the ground phase guide; its `## Gather` section currently lists **Touches / Honors / Anchors** only. This task broadens it to the working-folder context categories.
  - `add-method/tooling/templates/TASK.md.tmpl` → `## 0 · GROUND` (+ `.add/tooling/templates/TASK.md.tmpl` + `_bundled/tooling/templates/TASK.md.tmpl` — ×3 byte-identical, md5 0c49513b) — the §0 template; fields `Touches (files · symbols · signatures):` / `Honors (patterns / conventions):` / `Anchors the contract cites:`. Broadened with a LIGHT context line (§0-stays-lean), not a per-category field block.
  - `add-method/tooling/test_ground_context.py` (NEW) — the red→green guard: the new working-folder categories appear in the §0 template + `0-ground.md` `## Gather`, and the ×3 template + ×3 guide copies stay byte-identical.
Honors (patterns / conventions):
  - **Dogfood parity** (CONVENTIONS) — the ×3 skill (`0-ground.md`) and ×3 template (`TASK.md.tmpl`) copies must stay md5-identical; a structural test asserts it.
  - **§0 stays lean** (this milestone's shared decision) — enrich the GUIDE; keep the §0 artifact light, no rigid per-category field block.
  - **measure-not-block — PRESERVE the `Anchors the contract cites:` line** — `_grounded_state` (test_ground_wiring) keys on that exact line; the measure is scoped OUT of this milestone, so the line's role is untouched.
  - **test_ground_phase pins** `## 0`, `GROUND`, and the guide saying "gather"/"codebase" — keep all three through the broaden.
  - **four mirror trees** (CONVENTIONS:396) — IF the book prose that enumerates gather categories is touched (02-the-flow ×4 · appendix-c ×4), sync all four incl. the unguarded appendix root (decided at §3; default: keep task 1 to guide+template, leave book prose to a follow-up).
Anchors the contract cites: `phases/0-ground.md` `## Gather` (the category list) · `TASK.md.tmpl` `## 0 · GROUND` (the field lines) · the PRESERVED `Anchors the contract cites:` line (measure invariant) · `test_ground_context.py` (new guard: categories present + ×3 template parity + ×3 guide parity)

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Broaden the §0 GROUND gather to the full working-folder context
Framings weighed: enrich the guide + a light §0 "Context" line (chosen) · a rigid per-category §0 field block · guide-only with no §0 template change
Must:
<must>
  - `0-ground.md` `## Gather` names the working-folder context categories beyond code: docs/textbase · TODOs/task markers · config/manifests · data/fixtures — each a one-line "gather this" cue, task-specific delta only.
  - the `## 0 · GROUND` template records the broadened context with ONE light affordance (a `Context (working folder):` line), not a per-category field block — §0 stays lean.
  - the `Anchors the contract cites:` line is preserved verbatim in role — `_grounded_state` keys on it; the measure is untouched.
  - every copy stays byte-identical: `0-ground.md` ×3 (skill trees), `TASK.md.tmpl` ×3 (template trees).
</must>
Reject:
<reject>
  - a guide/template copy drifts (one edited, mirrors not) -> the ×3 parity guard reds (test_ground_context)
  - the broadened §0 omits a named category (docs/todos/config/data) -> the category-presence guard reds
  - the `Anchors the contract cites:` line is removed/renamed -> the measure-invariant guard reds (it would silently break `_grounded_state`)
</reject>
After:
<after>
  - `0-ground.md` `## Gather` lists the 4 working-folder categories; the §0 template carries the `Context (working folder):` line; ×3 guide + ×3 template byte-identical; `add.py status` still prints `grounded ✓` on a filled §0; the add.py engine is byte-identical to `engine_pin` (no measure edit).
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the §0 template gains ONE light `Context (working folder):` line (vs folding into Touches, or a per-category block) — lowest confidence because it is the lean-vs-explicit tradeoff the milestone flagged; if wrong (too light): a category gets skipped with no slot; if wrong (too heavy): every TASK.md §0 carries dead weight. Resolved at the §3 freeze.
  - [ ] the book prose that enumerates gather categories (02-the-flow ×4 · appendix-c ×4) is NOT touched this task — left as the high-level summary; a follow-up if it must mirror the categories — confirm or deny; if it must mirror, +×4/×4 sync work.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the guide names the working-folder categories
  Given the broadened 0-ground.md ## Gather section
  When an agent reads it at the ground phase
  Then it names docs/textbase, TODOs, config/manifests, and data/fixtures as things to gather
  And the Touches / Honors / Anchors structure is still present

Scenario: the §0 template carries the light Context line
  Given a freshly scaffolded TASK.md
  When its ## 0 · GROUND section is rendered
  Then it contains a "Context (working folder):" line
  And the "Anchors the contract cites:" line is unchanged

Scenario: all copies stay byte-identical
  Given the guide and template edits are applied
  When the ×3 0-ground.md copies and the ×3 TASK.md.tmpl copies are md5'd
  Then each set hashes identically
  And no other template/guide section changed

Scenario: a drifted copy reds the guard
  Given one copy is edited but its mirrors are not
  When test_ground_context runs
  Then the parity assertion fails
  And the non-parity assertions are unaffected

Scenario: the grounding measure is unchanged
  Given a §0 with a filled "Anchors the contract cites:" line
  When add.py status runs
  Then it prints "grounded ✓"
  And the add.py engine is byte-identical to engine_pin (measure untouched)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
GROUND-GATHER SHAPE  (prose/template contract — frozen text shapes, not an HTTP API)

0-ground.md `## Gather` — the bullet set becomes:
  - Touches (code)                — files · symbols · signatures            [existing]
  - Context (working folder)      — the NON-code artifacts the task touches:
        docs/textbase (README · *.md · notes) · TODOs (TODO.md · FIXME/TODO/HACK · task lists) ·
        config/manifests (configs · .env.example · pyproject/package · CI) · data/fixtures (samples · fixtures · schemas).
        Task-delta only; never a full-repo index or a setup re-scan.        [NEW]
  - Honors                        — patterns / conventions                  [existing]
  - Anchors the contract cites    — the symbols §3 names                    [existing · PRESERVED]

TASK.md.tmpl `## 0 · GROUND` — gains ONE line, placed between Touches and Honors:
  Context (working folder): <docs · todos · config · data the task touches — task-delta only>
  (the Touches, Honors, and `Anchors the contract cites:` lines are unchanged)

Sync         : 0-ground.md ×3 byte-identical · TASK.md.tmpl ×3 byte-identical
Guard        : add-method/tooling/test_ground_context.py
Invariants   : `Anchors the contract cites:` line role unchanged (measure) · `## 0`/`GROUND` present ·
               guide keeps "gather"/"codebase" · add.py engine == engine_pin (no measure edit)
Out of scope : the book prose (02-the-flow ×4 · appendix-c ×4) — left as the high-level summary this task
```

Least-sure flag surfaced at freeze: [contract] the §0 artifact shape — froze the NEW `Context (working folder):` line over folding the categories into the Touches label; if too light a category gets skipped with no slot, if too heavy every TASK.md §0 carries dead weight (a re-freeze if wrong, cheap pre-build). Human-approved this exact shape at the freeze.

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

Coverage target: the new categories + the ×3/×3 parity + the preserved invariants (structural prose guards)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_guide_lists_working_folder_categories: assert 0-ground.md ## Gather names docs/textbase, todos, config/manifests, data/fixtures; assert Touches/Honors/Anchors still present
  - test_template_has_context_line: assert TASK.md.tmpl §0 contains "Context (working folder):"; assert the "Anchors the contract cites:" line is preserved
  - test_guide_copies_byte_identical: assert the ×3 0-ground.md copies md5-equal
  - test_template_copies_byte_identical: assert the ×3 TASK.md.tmpl copies md5-equal
  - test_grounding_invariants_preserved: assert §0 keeps "## 0"/"GROUND"; assert add.py == engine_pin.ENGINE_MD5 (measure code untouched)
</test_plan>

Tests live in: `add-method/tooling/test_ground_context.py` · MUST run red (missing categories/line) before Build.
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

- [x] all tests pass — full suite 800 OK; test_ground_context 10/10
- [x] coverage did not decrease — additive (+10 tests); nothing removed/weakened
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; the suite was written RED first (3 feature failures) then made green by the guide+template edits only
- [x] concurrency / timing of the risky operation is safe — N/A: prose/template change, no runtime or concurrency
- [x] no exposed secrets, injection openings, or unexpected dependencies — N/A: markdown/template only, no code or dependency added
- [x] layering & dependencies follow CONVENTIONS.md — ×3 guide + ×3 template byte-identical (dogfood parity); the grounding measure untouched (add.py == engine_pin); §0-stays-lean honored (one light line)
- [x] a person reviewed and approved the change — the human approved the §3 freeze (the one gate); verify auto-resolves under autonomy:auto (no security finding, no residue)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — test_ground_context.py's 10 tests run in the suite (executed, 800 OK); the §0 Context line is rendered by the scaffolder (test_template_has_context_line green) and the guide's Context bullet is the gather instruction. No orphan symbol.
- [x] DEAD-CODE (code) — no new unused symbol; the only new code is the test file (all 10 asserts active).
- [x] SEMANTIC (prose / non-code) — read in full: `0-ground.md` `## Gather` gained a coherent **Context (working folder)** bullet enumerating docs/textbase · TODOs · config/manifests · data/fixtures (task-delta scoped); `TASK.md.tmpl` §0 gained the `Context (working folder):` line between Touches and Honors; the `Anchors the contract cites:` measure line + `## 0`/`GROUND` preserved; book prose (02-the-flow ×4 · appendix-c ×4) NOT touched (out-of-scope boundary held); engine pin unchanged. Coherence note: the guide's intro line still says "codebase" without naming the working-folder context — recorded as a §7 follow-up, not edited (contract-exact build).
- SECURITY — none: markdown/template only, no attack surface.

### GATE RECORD
Outcome: PASS
Reviewed by: AI (auto-resolved under autonomy:auto — complete evidence, no security finding); human approved the §3 freeze · date: 2026-06-11

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): whether agents actually fill the §0 Context line on real tasks (a dead slot = the line is decorative); whether the 4 categories are the right set or one is never used.
Spec delta for the next loop: task 2 (ground-gather-hint) adds the gather-METHOD (subagent/skim + deepen); a follow-up may align the guide's intro framing to the broadened gather.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] the FIRST lived ground run (a task created AT `ground`, not retrofitted) reached `grounded ✓` — closing the "zero lived runs starting at ground" ceiling folded at fv25 in real time (evidence: ground-context-sources created at phase ground; status showed `grounded ✓ — §0 cites the anchors §3 names` after §0 was filled, never retrofitted)
- [ADD · folded] dogfooded the milestone's own technique on its own first task — a haiku subagent did the broad working-folder sweep (returned the ×3/×3 sync md5s + the guard list) while the main context deepened on the precise guard assertions; the split (cheap subagent for breadth · main context for the measure invariant) pre-mapped the `Anchors` line before the broaden touched it (evidence: the Explore/haiku sweep located the guards; the build preserved the `Anchors the contract cites:` line, measure stayed `grounded ✓`)
- [SDD · folded] an additive §0 template LINE (inserted between existing fields) is byte-invisible to the existing guard surface — 800→810 with zero scaffold/render test broken — because the template tests pin tokens/structure, not exact line-sets; the template twin of the additive-engine-surface-byte-invisible convention (evidence: full suite OK after the `Context (working folder):` line landed; only test_ground_context asserts it; test_ground_phase's `## 0`/`GROUND` asserts unaffected)
- [TDD · folded] a prose/template task's RED suite splits into "the feature is missing" (red) + "the invariants still hold" (green) — triaging that split confirms the red is the new behavior, not a broken invariant (evidence: test_ground_context RED 3/3 on the category+Context-line asserts, GREEN from the first run on the ×3/×3 parity + engine-pin invariants)
- [ADD · folded] (follow-up) the guide's intro/goal line ("gather the REAL current codebase — files, symbols, signatures, patterns, conventions") under-describes the broadened gather; align the framing in task 2 or a follow-up — recorded, not edited (the §3 contract scoped only the `## Gather` bullet + the §0 line) (evidence: 0-ground.md intro lines 3-5 unchanged this task) — SELF-CLOSED at fv26: ground-gather-hint reworded the intro "REAL current codebase" → "REAL current working folder"; no foundation bullet, the follow-up it named is done
