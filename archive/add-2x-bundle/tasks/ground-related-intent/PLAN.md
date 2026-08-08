# TASK: §0 Related-intent links to the foundation

slug: ground-related-intent · created: 2026-06-30 · stage: mvp
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
  - `add-method/skill/add/phases/0-ground.md` — GROUND guide; `## Gather` + `## Exit gate`. New "Related intent" gather bullet + exit checkbox. (×3 skill trees)
  - `add-method/tooling/templates/TASK.md.tmpl` — `## 0 · GROUND`; new `Related intent:` line (after the new Issues/Risks line). (×3 template trees)
  - `add-method/tooling/test_ground_related_intent.py` — NEW test, mirrors `test_ground_issues.py` (just shipped).
Context (working folder):
  - the foundation link targets: `.add/PROJECT.md` (domain/spec intent), `.add/GLOSSARY.md` (vocabulary), `.add/CONVENTIONS.md`, `.add/SOUL.md` (voice). NO `.add/conversation.md` exists.
  - sibling pattern `add-method/tooling/test_ground_issues.py` (shipped 28b1283); `engine_pin.ENGINE_MD5`; `test_skill_lean.py` phases pool.
Honors (patterns / conventions):
  - same lean discipline: task-delta only; 3-tree parity; engine byte-identical (no add.py edit); grounding measure keys only on the Anchors line.
Anchors the contract cites: 0-ground.md `## Gather` "Related intent" bullet · TASK.md.tmpl §0 `Related intent:` line · the foundation docs named (PROJECT/GLOSSARY/conversation) · Anchors line preserved · engine_pin.ENGINE_MD5
Issues/Risks (→ feed §1):
  - ⚠ **phases pool now at 32051/32052 — 1 B headroom** (task 1 consumed the slack). This task's new bullet + exit checkbox + template line needs MORE compaction than task 1; the safe-prose budget in the phase guides is nearly exhausted → a human-approved rebaseline is a likely fallback here (unlike task 1).
  - **`conversation.md` does not exist** — "Related intent" can't link a file that isn't there; the conversation target must be defined (lean pointer vs new artifact) — a §1 decision.
  - **overlap with Honors** — Honors already cites PROJECT.md/CONVENTIONS.md; Related-intent must be distinct (the WHY/intent + glossary terms + originating request), not a duplicate of the conventions-to-honor.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: §0 GROUND sixth field — "Related intent" — links the task to its foundation intent
Framings weighed: sixth §0 sub-field, lean pointer to PROJECT§·GLOSSARY·origin (chosen) · new .add/conversation.md artifact (rejected — heavier, Tin chose lean) · fold into Honors (rejected — Honors is conventions-to-honor, not the WHY/intent)
Must:
<must>
  - M1: `0-ground.md` `## Gather` names a **"Related intent"** category — links the task to its foundation intent: `PROJECT.md §` (the domain/spec intent), `GLOSSARY` term(s), and the originating request / milestone rationale (the "conversation" that sized it). Task-delta only.
  - M2: `TASK.md.tmpl` `## 0 · GROUND` gains ONE `Related intent:` line, AFTER the `Issues/Risks (→ feed §1):` line.
  - M3: Related-intent is DISTINCT from Honors — it names the WHY/intent + glossary + origin, NOT the conventions-to-honor.
  - M4: `0-ground.md` `## Exit gate` gains a checkbox for the field.
  - M5: invariants — the `Anchors the contract cites:` line verbatim, `## 0`/`GROUND` headings, `add.py` == `engine_pin.ENGINE_MD5`.
  - M6: `0-ground.md` ×3 + `TASK.md.tmpl` ×3 byte-identical; the `phases` pool stays within budget by COMPACTION; only if compaction is impossible without risking a pinned phrase, a human-approved rebaseline (baseline += ⌈surface/0.80⌉) — reported, never silent.
</must>
Reject:
<reject>
  - the build edits/moves the `Anchors the contract cites:` measure line -> "anchors_line_broken"
  - the build changes `add.py` (ENGINE_MD5 drifts) -> "engine_touched"
  - the pool baseline is bumped silently (not reported, no human approval) -> "lean_rebaselined_silently"
  - any guide or template tree copy drifts from its siblings -> "tree_drift"
</reject>
After:
<after>
  - The GROUND gather names 6 categories (… · Issues/Risks · Related intent); §0 template carries the Related intent line; engine unchanged; guide×3 + template×3 byte-identical; phases pool within budget (compaction, or a reported human-approved rebaseline); full suite green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ The `phases` pool is at 1 B headroom (32051/32052) — task 1 took the slack. Fitting task 2 by compaction alone may be impossible without risking a sibling phase-guide's pinned phrase. Lowest confidence: whether compaction suffices. If wrong: a SMALL human-approved rebaseline (Tin pre-approved the path; I report the exact ⌈surface/0.80⌉ before committing).
  - [ ] "Related intent" distinctness from Honors — confirmed framing: intent/why + glossary + origin, not conventions-to-honor.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: guide names the Related-intent category   # M1, M3
  Given the 0-ground.md guide
  When I read its ## Gather section
  Then it names a "Related intent" category linking PROJECT.md § · GLOSSARY term(s) · the originating request
  And it frames the field as intent/why, distinct from Honors (conventions-to-honor)
  And the Touches/Context/Honors/Anchors/Issues-Risks categories remain

Scenario: template carries the Related intent line   # M2
  Given the TASK.md.tmpl ## 0 · GROUND section
  When I read it
  Then it has one "Related intent:" line, after the "Issues/Risks (→ feed §1):" line
  And the "Anchors the contract cites:" line is unchanged

Scenario: exit gate covers Related intent   # M4
  Given the 0-ground.md ## Exit gate
  When I read it
  Then it has a checkbox for the Related-intent field
  And the existing four/five checkboxes remain

Scenario: the engine is not touched   # R:engine_touched, M5
  Given the change is applied
  When I md5 every add.py copy
  Then each equals engine_pin.ENGINE_MD5

Scenario: lean budget held honestly   # R:lean_rebaselined_silently, M6
  Given the new surface is added
  When I sum the phases pool
  Then it is ≤ the test_skill_lean phases target (compaction); OR if rebaselined, the baseline change is recorded in test_skill_lean.py with a comment
  And no baseline moved without a recorded human-approved comment

Scenario: all tree copies stay byte-identical   # R:tree_drift, M6
  Given the change is applied
  When I md5 the 3 guide copies and the 3 template copies
  Then each set is byte-identical
  And the _bundled copies match their canonical source
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
GROUND §0 sixth field — frozen shape @ v1   (doc/method contract: text-shape + invariants)

0-ground.md  ## Gather:
  + bullet "Related intent" — links the task to its foundation intent: PROJECT.md § (domain/spec
    intent) · GLOSSARY term(s) · the originating request / milestone rationale (the "conversation").
    Distinct from Honors (intent/why, NOT conventions-to-honor). Task-delta only.
  ## Exit gate: + a checkbox for the field.

TASK.md.tmpl  ## 0 · GROUND:
  + ONE line, AFTER "Issues/Risks (→ feed §1):":
      Related intent: <PROJECT.md § · GLOSSARY term(s) · originating request/milestone rationale — task-delta>

conversation target = LEAN POINTER (no new artifact): the originating request / milestone rationale.

INVARIANTS:
  - "Anchors the contract cites:" line byte-unchanged · "## 0"/"GROUND" headings preserved
  - every add.py copy == engine_pin.ENGINE_MD5
  - 0-ground.md ×3 + TASK.md.tmpl ×3 byte-identical; _bundled regenerated
  - phases pool within budget by COMPACTION; if impossible, a human-approved rebaseline RECORDED in
    test_skill_lean.py (baseline += ⌈surface/0.80⌉ + a comment) — never silent

Tests: add-method/tooling/test_ground_related_intent.py  (mirrors test_ground_issues.py)
```

Least-sure flag surfaced at freeze: [contract/test] whether the new field fits by compaction is the least-sure part — the pool is at 1 B headroom, so the fallback (a recorded human-approved phases rebaseline, baseline += ⌈surface/0.80⌉) is likely; Tin pre-approved that path and I report the exact number before committing.
Status: FROZEN @ v1 — approved by Tin
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: behavioral guards (mirrors test_ground_issues.py)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_guide_names_related_intent: 0-ground.md ## Gather names "Related intent" + PROJECT/GLOSSARY/origin + distinct-from-Honors; existing categories remain   (M1,M3)
  - test_template_has_related_intent_line: TASK.md.tmpl §0 has "Related intent:" AFTER the Issues/Risks line; Anchors line unchanged   (M2)
  - test_exit_gate_covers_related_intent: ## Exit gate has a Related-intent checkbox   (M4)
  - test_engine_byte_identical_to_pin: every add.py == engine_pin.ENGINE_MD5   (R:engine_touched,M5)
  - test_lean_budget_honest: phases pool ≤ target; OR if rebaselined, the change is RECORDED (baseline comment) in test_skill_lean.py — never a silent bump   (R:lean_rebaselined_silently,M6)
  - test_copies_byte_identical: 0-ground.md ×3 + TASK.md.tmpl ×3 each byte-identical   (R:tree_drift,M6)
</test_plan>

Tests live in: `add-method/tooling/test_ground_related_intent.py` · MUST run red (missing field) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/phases/` `.claude/skills/add/phases/` `add-method/src/add_method/_bundled/skill/add/phases/` `add-method/tooling/templates/` `.add/tooling/templates/` `add-method/src/add_method/_bundled/tooling/templates/` `add-method/tooling/test_ground_related_intent.py` `add-method/tooling/test_skill_lean.py` `add-method/tooling/test_ground_issues.py`
Strategy (ordered batches): 1. write test_ground_related_intent.py RED (mirror test_ground_issues.py). 2. add the "Related intent" gather bullet + exit checkbox to 0-ground.md + the §0 line to TASK.md.tmpl (after Issues/Risks). 3. compact phase-guide prose to absorb it; 4. if compaction can't fit without risking a pinned phrase → record a human-approved phases rebaseline in test_skill_lean.py (baseline += ⌈surface/0.80⌉ + comment) and REPORT the number. 5. propagate canonical → twins, prepare_bundle.py. 6. full suite green.

Persona (optional): <name the persona file under `.add/personas/` this build embodies as a domain stance atop SOUL.md — advisory, never lowers a gate; absent = generic>
Known-problem fixes: <trap → planned fix — the failure modes this build must dodge; guidance, not enforced>
Strategy actually used: <fill at VERIFY — the strategy you ACTUALLY used (or "as planned"); harvested into the §7 Decisions (ADR) block as the [AI] build decision>
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

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

- [x] all tests pass — full suite 2519/0
- [x] coverage did not decrease — n/a (doc/method task; behavioral guards)
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; test_ground_issues edit was the human-approved baseline migration (in §5 scope), not a weakening
- [x] the green was EARNED, not gamed — refute-read below
- [x] concurrency / timing — n/a (static guide/template prose)
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose only; no new deps
- [x] layering & dependencies follow CONVENTIONS.md — field follows the existing §0 sub-field pattern
- [ ] a person reviewed and approved the change — auto-resolved under `autonomy: auto` (Tin approved the §3 freeze AND the rebaseline; build auto-PASSed; refute-read is the backstop)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] §0 shows a `Related intent:` line after `Issues/Risks (→ feed §1):` — confirmed: test_related_intent_after_issues green
- [x] `0-ground.md` reads with a 6th gather category "Related intent" (PROJECT/GLOSSARY/origin) + exit-gate checkbox — confirmed: test_guide_links_foundation + test_exit_gate_covers_related_intent green
- [x] full suite green incl. test_ground_related_intent — confirmed: Ran 2519 tests, OK
- [x] lean budget honest: phases pool 32224 ≤ target 32224; baseline move 40065→40280 RECORDED with a comment + ⌈172/0.80⌉=215 — reported to Tin and approved before commit
- [x] add.py == engine_pin.ENGINE_MD5; guide ×3 + template ×3 byte-identical — confirmed: engine test + parity tests green

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read in full: 0-ground.md re-read end-to-end after edits; the 6 gather categories + 6 exit checkboxes read coherently, Related-intent is distinct from Honors, no pinned token dropped; the rebaseline comment in test_skill_lean.py states the surface + formula.
- [x] WIRING — the field is guarded by test_ground_related_intent and rendered by the template; the budget migration keeps task-1's real invariant (pool ≤ live target) intact.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self · adversarially checked: (a) is the rebaseline a disguised weakening? No — it's the documented surface÷ratio formula for genuinely-new human-approved surface, recorded with a comment; the migrated task-1 test still enforces the REAL invariant (pool ≤ live target, baseline only grows) rather than a frozen number; (b) is the field vacuous? No — gather bullet + exit checkbox + template line + the test's foundation-link assertion (PROJECT+GLOSSARY) are substantive; (c) did parity/engine regress? No — engine == pin, all trees 1 md5; (d) is the pool genuinely within budget? Yes — 32224 ≤ 32224. No overfit, no contract edit.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: self
1. Security: CLEAR — guide/template prose + a test-budget constant; no code path, no secrets
2. Concurrency: CLEAR — static documents; no runtime
3. Architecture: CLEAR — field follows the §0 pattern; the budget migration improves the mechanism (live target vs frozen pin); engine == ENGINE_MD5
Verdict: PASS
Residue: none
Binding: yes — mechanical

### GATE RECORD
Outcome: PASS
Reviewed by: self (auto-resolved under autonomy: auto; mechanical + green + no residue; rebaseline human-approved) · date: 2026-06-30

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. The Advisor 3-lens verdict and the Refute-read verdict are both measured by `add.py audit` (`advisor_verdict_unrecorded` · `refute_unrecorded`) — neither is engine-blocked; a human spot-audit is the backstop for any finding the AI did not surface or record. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose origin; rejected sixth §0 sub-field, lean pointer to PROJECT§ · GLOSSARY · new .add/conversation.md artifact (rejected — heavier, Tin chose lean) · fold into Honors (rejected — Honors is conventions-to-honor, not the WHY/intent)
- [human] freeze — froze §3 @ v1 (approved by Tin)
- [AI] build — strategy used: as planned
- [AI] verify — gate PASS (reviewed by self (auto-resolved under autonomy: auto; mechanical + green + no residue; rebaseline human-approved))

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
