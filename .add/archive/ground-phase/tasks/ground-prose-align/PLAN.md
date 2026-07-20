# TASK: Name the ground phase in book + skill + GLOSSARY

slug: ground-prose-align · created: 2026-06-10 · stage: mvp
autonomy: conservative   <!-- lowered from project default (auto): prose-only but touches ~14 byte-synced tree copies (book ×4 · skill ×3 · template ×3 · survivor) + a new test; conservative keeps me at the verify gate (under Tin Dang's full-autonomy delegation). NOT risk:high (additive prose; engine untouched). -->
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): `docs/02-the-flow.md` (mermaid already has S0 Ground; prose still says "seven steps" from Specify) ×4 [root · add-method/docs · .add/docs · _bundled/docs] · `docs/appendix-c-glossary.md` (`**Term** — …` entries, alpha order) ×4 · `skill/add/SKILL.md` (the "## The flow and which file to load" phase table, setup→observe) ×3 · `.add/GLOSSARY.md` survivor (`Phase:` line @ L6) · `tooling/templates/GLOSSARY.md.tmpl` (ADD vocabulary) ×3 · `skill/add/phases/0-ground.md` (the ground playbook, exists) · `add.py:PHASE_GUIDE["ground"]` → ("…", "02-the-flow.md").
Honors (patterns / conventions): test_flow_diagram derives FLOW_PHASES from add.PHASES (ground already in mermaid + CHECKLIST, already green); the DocsAccord pattern (test_goal_auto_ready_gate) — every named surface defines the term + byte-synced trees; prose-only → engine == engine_pin (no add.py edit).
Anchors the contract cites: `02-the-flow.md` ground-preamble paragraph · `appendix-c-glossary.md` **Ground** + **Grounding map** terms · `SKILL.md` ground phase-row · `.add/GLOSSARY.md` Phase line + terms · `GLOSSARY.md.tmpl` terms · `test_ground_prose.py`.
<!-- grounded retroactively at build: this task was grandfathered at `specify`; the §0 records the prose-surface grounding done via the survey above. -->

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: name the `ground` phase across the prose surfaces — book + skill phase-table + GLOSSARY — rendered as the §0 preamble to the seven steps (prose ≡ enforcement)
Framings weighed: describe ground IN the flow chapter 02-the-flow.md as the §0 preamble (chosen) · a dedicated `step-N` chapter for ground (rejected — GSD-heavy; the seven steps keep their identity) · rebrand "seven steps"→"eight" (rejected — ground is phase-0, the seven keep their brand)
Must:
<must>
  - The book flow chapter `02-the-flow.md` names `ground` as the phase-0 preamble (the AI gathers the real codebase before Specify) — closing the prose/diagram gap (the mermaid already draws S0 Ground). Synced byte-identical ×4.
  - The book glossary `appendix-c-glossary.md` defines **Ground** + **Grounding map / anchors**; synced ×4.
  - The skill `SKILL.md` phase table gains a `ground` row (`phases/0-ground.md` · §0 GROUND map · AI-led preamble) before `specify`; synced ×3.
  - The GLOSSARY survivor `.add/GLOSSARY.md` `Phase:` line lists `ground` first AND adds `ground` + `grounding map` terms; the template `GLOSSARY.md.tmpl` adds the two terms; synced ×3.
  - The engine stays byte-identical ×3 == engine_pin (PROSE-ONLY; `PHASE_GUIDE["ground"]→02-the-flow.md` is the legitimate home — no retarget); full suite green.
</must>
Reject:
<reject>
  - rebrand "the seven steps" → "eight steps" -> the seven keep their identity; ground is the §0 preamble (reject the rebrand)
  - a dedicated `step-N` book chapter for ground -> GSD-heavy; ground is a preamble described in the flow chapter (reject)
  - touch add.py / PHASE_GUIDE -> prose-only; the engine must stay == pin (a touch fails test_ground_prose engine-untouched + the existing prose-only guards)
</reject>
After:
<after>
  - every prose surface (book flow + book glossary + skill phase-table + GLOSSARY survivor + template) names `ground` as the §0 preamble; all trees byte-synced (×4 docs, ×3 skill/template); engine == pin; suite green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [contract] 02-the-flow.md is the right home for the ground prose (NOT a dedicated chapter, NOT a PHASE_GUIDE retarget) — lowest confidence because ground-phase-engine's §7 noted "retarget away from the placeholder 02-the-flow.md", so this reverses that note; reason: ground is a phase-0 PREAMBLE, not a step (the seven steps each own a chapter; ground belongs in the flow overview); if wrong: a follow-up adds a dedicated chapter + retargets PHASE_GUIDE (1 engine line + 1 file). Cost: low.
  - [ ] both the survivor AND the template GLOSSARY get the terms — the survivor is the live dogfood, the template seeds new projects; both are "GLOSSARY" so prose ≡ enforcement needs both.
  - [ ] no test hardcodes the SKILL phase-row count or the GLOSSARY Phase enumeration — test_flow_diagram derives FLOW_PHASES from add.PHASES (already green with ground); the full suite is the safety net for any output-conformance.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the book flow chapter names the ground preamble
  Given docs/02-the-flow.md
  When I read its flow prose
  Then it names "ground" as the phase-0 preamble before the seven steps
  And the mermaid still draws the S0 Ground node (unchanged)

Scenario: the book glossary defines ground
  Given docs/appendix-c-glossary.md
  Then a "Ground" term and a "Grounding map" term are defined

Scenario: the skill phase table lists ground
  Given skill/add/SKILL.md
  Then the phase table has a "ground" row pointing at phases/0-ground.md

Scenario: the GLOSSARY names ground
  Given .add/GLOSSARY.md and tooling/templates/GLOSSARY.md.tmpl
  Then both name "ground" and "grounding map"
  And the survivor `Phase:` line lists "ground" first

Scenario: the prose surfaces are byte-synced across trees
  Given the canonical edits are synced
  Then 02-the-flow.md is identical ×4, appendix-c-glossary.md ×4, SKILL.md ×3, GLOSSARY.md.tmpl ×3

Scenario: the engine is untouched   # REJECT (prose-only task)
  Given this is a prose-only task
  When the suite checks the engine
  Then md5(add.py) ×3 == engine_pin.ENGINE_MD5 (no engine edit)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
PROSE DELTAS — name `ground` as the §0 preamble (prose ≡ enforcement); engine UNTOUCHED

BOOK · docs/02-the-flow.md (synced ×4: root · add-method/docs · .add/docs · _bundled/docs)
   + a ground-preamble paragraph after the flow intro: ground is a phase-0 preamble — the AI
     gathers the real current codebase (files · symbols · signatures · conventions · the anchors
     the contract will cite) before Specify; the seven steps keep their numbering and brand.
   KEEP: the "seven steps" framing · the mermaid S0 Ground node · "any phase may send you back to
         an earlier one" (test_flow_diagram). NO renumber of the seven.

BOOK · docs/appendix-c-glossary.md (synced ×4)
   + **Ground (phase-0 preamble)** — … gathers the real codebase the task touches into a §0 map …
   + **Grounding map / anchors** — the §0 artifact: real files/symbols/conventions + the anchors §3 cites …
   (alpha order: after **Gate**, before **`HARD-STOP`**) · + an optional "Ground" row in the formal-mapping table.

SKILL · skill/add/SKILL.md (synced ×3)
   + a phase-table row BEFORE `specify`:
     | ground | `phases/0-ground.md` | §0 GROUND map (real files · symbols · anchors) | **AI** (the §0 preamble) |

GLOSSARY survivor · .add/GLOSSARY.md (single live file)
   Phase line: "specify, scenarios, …" -> "ground, specify, scenarios, …"
   + ground: … (phase-0 preamble; AI gathers the real codebase before specify)
   + grounding map / anchors: … (the §0 artifact: real files/symbols + the anchors §3 cites)

GLOSSARY template · tooling/templates/GLOSSARY.md.tmpl (synced ×3)
   + ground + grounding map terms in the "ADD method vocabulary" block (seed for new projects).

NO-TOUCH (prose-only invariants)
   add.py / PHASE_GUIDE / PHASES / engine_pin (== `e6b8c3da…`) · the seven-step brand · the mermaid +
   CHECKLIST (already carry ground) · CHANGELOG history.
TREE PARITY: 02-the-flow.md ×4 · appendix-c-glossary.md ×4 · SKILL.md ×3 · GLOSSARY.md.tmpl ×3 byte-identical; add.py ×3 == pin.
```

Status: FROZEN @ v1 — approved by AI (autonomous, under Tin Dang's full-autonomy delegation) · 2026-06-11
Least-sure flag surfaced at freeze: [contract] 02-the-flow.md is the ground prose's home (no dedicated chapter, no PHASE_GUIDE retarget) — this reverses ground-phase-engine's §7 "retarget away from the placeholder" note; ground is a PREAMBLE not a step, so the flow chapter is its natural home; fallback if a dedicated chapter is later wanted = 1 engine line + 1 file. Decided at freeze.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + every Reject scenario (prose surfaces + byte-sync + engine-untouched)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_flow_chapter_names_ground_preamble: 02-the-flow.md names "ground" as the phase-0 preamble; "seven steps" + the S0 mermaid node retained
  - test_book_glossary_defines_ground: appendix-c-glossary.md defines a "Ground" term and a "Grounding map" term
  - test_skill_phase_table_lists_ground: SKILL.md phase table has a "ground" row → phases/0-ground.md
  - test_glossary_survivor_and_template_name_ground: .add/GLOSSARY.md + GLOSSARY.md.tmpl name "ground"/"grounding map"; survivor Phase line lists ground first
  - test_flow_chapter_synced_x4: 02-the-flow.md byte-identical ×4
  - test_book_glossary_synced_x4: appendix-c-glossary.md byte-identical ×4
  - test_skill_synced_x3: SKILL.md byte-identical ×3
  - test_glossary_tmpl_synced_x3: GLOSSARY.md.tmpl byte-identical ×3
  - test_engine_untouched: md5(add.py) ×3 == engine_pin.ENGINE_MD5 (prose-only)
</test_plan>

Tests live in: `test_ground_prose.py` · run via `cd add-method/tooling && python3 -m unittest discover -p 'test_*.py'`.
RED baseline: the prose surfaces don't name "ground" yet (assertion fail) — red for the right reason; engine-untouched is GREEN now and must STAY green (the prose-only guard).
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): PROSE-ONLY — never touch add.py / PHASE_GUIDE / engine_pin (the engine stays == `e6b8c3da…`); edit each canonical doc once → sync byte-identical to its twins (×4 docs · ×3 skill/template); the survivor `.add/GLOSSARY.md` is a single live file (no twin).
Code lives in: `docs/02-the-flow.md` (×4) · `docs/appendix-c-glossary.md` (×4) · `skill/add/SKILL.md` (×3) · `tooling/templates/GLOSSARY.md.tmpl` (×3) · `.add/GLOSSARY.md` (survivor). Tests: `add-method/tooling/test_ground_prose.py`.
Constraints: do NOT change any test, the frozen §3, or the engine; keep the "seven steps" brand + the mermaid S0 + "any phase may send you back to an earlier one" (test_flow_diagram).

Build note: also resynced the stale repo-root `appendix-c-glossary.md` mirror (it had drifted from canonical in a past task — missing the "Auto-ready goal" term + the updated autonomy entry; no existing test caught it). The ×4 sync brought it current AND added the ground terms; test_ground_prose.test_book_glossary_synced_x4 now guards it. The §0-section dogfood was added to this task at build (grandfathered at specify) — live `status` shows `grounded ✓`.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite **790 OK** (was 780; +10 from test_ground_prose); live dogfood `check: 265 passed, 0 failed`
- [x] coverage did not decrease — +10 new tests; every Must + Reject scenario covered (named surfaces + ×4/×3 byte-sync + engine-untouched)
- [x] no test or contract was altered to pass — frozen §3 untouched; no existing test edited (the new behavior is additive prose; the suite went 780→790 by ADDITION only)
- [x] concurrency / timing — N/A: prose-only; no code path added
- [x] no exposed secrets / injection / unexpected deps — pure documentation; SKILL.md (on the wording-lint surface) stays green (no banned idiom/emphasis token); no new dependency
- [x] layering & dependencies follow CONVENTIONS.md — prose ≡ enforcement (the DocsAccord pattern); engine UNTOUCHED (== pin); all trees byte-synced (×4 docs, ×3 skill/template)
- [x] a person reviewed and approved the change — see GATE RECORD (gate delegated to the AI under Tin Dang's explicit full-autonomy directive 2026-06-11; the §3 freeze was AI-under-delegation; security N/A)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (n/a — prose task) — no new code symbol; the engine is byte-identical ×3 == engine_pin `e6b8c3da` (test_ground_prose.EngineUntouchedTest green), so nothing in add.py changed to wire.
- [x] DEAD-CODE (n/a — prose task) — no symbol added; `PHASE_GUIDE["ground"]→02-the-flow.md` was deliberately NOT retargeted (the flow chapter is the legitimate home), so no dangling pointer.
- [x] SEMANTIC (prose) — read in full: 02-the-flow.md names `ground` as the phase-0 preamble (consistent with the mermaid S0 + the "seven steps" brand; "any phase may send you back" retained → test_flow_diagram green); appendix-c defines **Ground** + **Grounding map** (+ a formal-mapping row); SKILL.md gains the `ground` phase-row + an accurate "§0 ground preamble and seven step sections" intro; the survivor GLOSSARY Phase line lists ground first + two terms; GLOSSARY.md.tmpl carries the two terms. All byte-synced; the stale repo-root appendix-c mirror was brought current (and is now test-guarded).

### GATE RECORD
Outcome: PASS
Reviewed by: AI (autonomous self-review under Tin Dang's explicit full-autonomy delegation — the human DELEGATED this gate; the §3 freeze was AI-under-delegation) · date: 2026-06-11
Evidence: full suite **790 OK**; prose-only — md5(add.py) ×3 == engine_pin `e6b8c3da` UNCHANGED (no engine edit); every prose surface (book flow + book glossary + skill phase-table + GLOSSARY survivor + template) names `ground` as the §0 preamble; all trees byte-synced (×4 docs incl. the resynced stale root, ×3 skill/template); no existing test weakened (suite grew 780→790 by addition). No security surface (documentation) → HARD-STOP invariant not in play.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): every prose surface names `ground` (test_ground_prose); the ×4/×3 byte-sync guards; the engine-untouched guard.
Spec delta for the next loop: the ground phase is now fully named in prose ≡ enforcement — the milestone goal is met; the only remaining ground gap is a LIVED run starting at `ground` (carried from ground-phase-engine's §7), available next milestone.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [SDD · folded] a byte-sync test written for a NEW term surfaced a PRE-EXISTING drift no prior test caught — the repo-root appendix-c mirror had silently fallen behind canonical (missing a whole term); a "synced ×N" guard pays for itself beyond the change that adds it (evidence: test_book_glossary_synced_x4 was red on the stale root before any ground edit; root was 2 lines + the "Auto-ready goal" term behind canonical)
- [ADD · folded] a phase-0 PREAMBLE earns prose in the flow chapter, not a step-chapter — keeping ground in 02-the-flow.md (vs a dedicated chapter + a PHASE_GUIDE retarget) preserves the "seven steps" brand and the lean-over-GSD rule, and the engine pointer was already correct (evidence: PHASE_GUIDE["ground"]→02-the-flow.md left unchanged; test_flow_diagram green with "seven steps" retained; reverses ground-phase-engine §7's "retarget" note with rationale)
- [TDD · folded] deriving a test's expected set from the engine constant (FLOW_PHASES = [p for p in add.PHASES if p != "done"]) means a ladder change auto-propagates the prose requirement — adding ground to PHASES made test_flow_diagram REQUIRE ground in the mermaid+CHECKLIST without a test edit (evidence: test_flow_diagram stayed green through ground-phase-engine because the mermaid/CHECKLIST were updated to satisfy the engine-derived set)
- [ADD · folded] retrofitting a §0 map onto each grandfathered milestone task at build let all three tasks dogfood `grounded ✓` live, turning the "zero lived dogfood" ceiling into "zero lived runs STARTING at ground" — a narrower, more honest residual (evidence: ground-bundle-wiring + ground-prose-align both show `grounded ✓` yet started at `specify`)
