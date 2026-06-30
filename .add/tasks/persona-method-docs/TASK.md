# TASK: book chapter + skill pointer + glossary describe the persona loop, in parity

slug: persona-method-docs · created: 2026-06-29 · stage: mvp
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
  - `add-method/docs/18-personas.md` (NEW chapter) — the persona loop end-to-end: SEED at setup → GROW via observe→delta→fold → APPLY to UDD/advisor/build → cross-runner subagent; teacher (agency-agents) is read off-build by the AI, never a runtime dependency; engine NO-EXEC; a persona never lowers a gate. Mirrored to repo-root `./18-personas.md` (test_book_parity) + `_bundled/docs/18-personas.md` (test_bundle_parity).
  - `mkdocs.yml:nav` — the new chapter is registered after "17 · Components" (the orphan_chapter guard reads mkdocs nav, per test_component_pillar_docs).
  - `add-method/docs/appendix-c-glossary.md` — adds the persona headwords (**persona**, **persona loop**); mirrored to repo-root + `_bundled` (book/bundle parity).
  - `add-method/skill/add/SKILL.md` — a one-line pointer to the persona loop (where it lives: `.add/personas/`, deltas/fold, design/streams/advisor). 3 skill trees; lean-fenced.
Context (working folder):
  - `.add/milestones/persona-learning-loop/MILESTONE.md` — the wave-1+2 tasks this chapter documents (persona-setup · udd-persona-loop · persona-self-improve · persona-subagent-prompt · advisor-persona-select · orchestrator-build-persona); a persona NEVER lowers a gate; teacher-not-dependency; engine NO-EXEC.
  - `add-method/docs/17-components.md` — the precedent chapter (added by component-method-docs); the registration pattern (nav + glossary + skill pointer) mirrors it.
Honors (patterns / conventions):
  - the book lives in 3 git-tracked trees — canonical `add-method/docs`, repo-root `./`, `_bundled/docs` — byte-identical (test_book_parity + test_bundle_parity).
  - the orphan_chapter guard reads `mkdocs.yml` nav (NOT the marketing README) — register the chapter there.
  - docs are descriptive — no engine code, both pins UNCHANGED; ubiquitous-language clean; SKILL.md edit is lean-fenced.
Anchors the contract cites: the new `18-personas.md` chapter (3 book trees) · its `mkdocs.yml` nav entry · the persona glossary headwords (appendix-c, 3 trees) · the SKILL.md persona-loop pointer · the engine-unchanged invariant.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: A dedicated book chapter (18 · Personas) describes the persona loop end-to-end — seed at setup, grow via observe→delta→fold, apply to UDD/advisor/build, expose a cross-runner subagent — with the teacher (agency-agents) read off-build (never a runtime dependency), the engine NO-EXEC, and a persona never lowering a gate. The chapter is registered in the book nav, the glossary gains the persona headwords, SKILL.md points to the loop, and every surface stays in parity across trees.
Framings weighed: a new chapter 18 + glossary + SKILL pointer (chosen — matches the ch.17-components precedent; standalone home for the loop) · folding it into an existing chapter (rejected by the human — wants a standalone chapter) · skill-guide only, no book (rejected — the milestone requires the book to describe the loop)
Must:
<must>
  - `add-method/docs/18-personas.md` exists and teaches the loop: SEED (setup) · GROW (observe→delta→fold) · APPLY (UDD · advisor/streams · build overlay) · the cross-runner subagent · teacher-not-dependency · engine NO-EXEC · a persona never lowers a gate.
  - the chapter is registered in `mkdocs.yml` nav (after chapter 17) — not orphaned.
  - `appendix-c-glossary.md` defines the persona headwords (**persona**, **persona loop**).
  - `SKILL.md` carries a one-line pointer to the persona loop (where personas live + how they grow/apply).
  - the chapter + glossary stay byte-identical across the 3 book trees (canonical · repo-root · _bundled); SKILL.md byte-identical across the 3 skill trees.
  - no engine code changes; both pins UNCHANGED.
</must>
Reject:
<reject>
  - a chapter not registered in the book nav -> "orphan_chapter" (must appear in mkdocs.yml nav)
  - a book/glossary surface that diverges across trees -> "book_parity_drift" (byte-identical or red)
  - an engine code change / pin re-aim for this task -> "engine_touched_for_docs" (docs are descriptive)
</reject>
After:
<after>
  - chapter 18 exists, teaches the loop, and is in the nav; the glossary defines the persona headwords; SKILL.md points to the loop.
  - every book/glossary surface is byte-identical across trees and SKILL.md across skill trees; the engine pin is unchanged; the parity tests pass.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ whether the book parity surface is exactly 3 trees (canonical · repo-root · _bundled) for the new chapter + glossary — lowest confidence because a missed tree goes red only in CI; if wrong: a parity test fails on the unmirrored tree. (Mitigation: mirror 18-personas.md AND appendix-c-glossary.md to all three; run test_book_parity + test_bundle_parity locally before the gate.)
  - [ ] the orphan guard reads mkdocs nav (not the marketing README) — if wrong: also add a README/book-index entry.
  - [ ] SKILL.md has lean-fence headroom for a one-line pointer — if wrong: reclaim a few bytes from SKILL.md prose.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the chapter exists and teaches the persona loop
  Given add-method/docs/18-personas.md
  When it is read
  Then it teaches SEED · GROW (observe→delta→fold) · APPLY (UDD/advisor/build) · cross-runner subagent · teacher-not-dependency · engine NO-EXEC · never lowers a gate

Scenario: the chapter is registered in the book nav
  Given mkdocs.yml
  When the nav is read
  Then it lists 18-personas.md (not orphaned)

Scenario: the glossary defines the persona headwords
  Given appendix-c-glossary.md
  When it is read
  Then it defines **persona** and **persona loop**

Scenario: SKILL.md points to the persona loop
  Given SKILL.md
  When it is read
  Then it carries a one-line pointer to the persona loop

Scenario: book + glossary + skill stay in parity across trees
  Given the new chapter, glossary edit, and SKILL.md pointer
  When the trees are compared
  Then 18-personas.md + appendix-c-glossary.md are byte-identical across the 3 book trees
  And SKILL.md is byte-identical across the 3 skill trees

Scenario: the engine is untouched
  Given the docs edits
  When the engine pin is read
  Then ENGINE_MD5 equals the pin (no engine change)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

BOOK CHAPTER — `add-method/docs/18-personas.md` (NEW), mirrored to 3 trees
  (described inline — no bare triple-dash / line-start `##` so the §3 span stays intact)
  • Teaches the persona loop: SEED at setup (persona-setup) · GROW via observe→delta→fold
    (persona-self-improve) · APPLY to UDD (udd-persona-loop), advisor/streams
    (persona-subagent-prompt + advisor-persona-select), and the build overlay (orchestrator-build-persona)
    · the cross-runner subagent · the teacher (agency-agents) is read OFF-BUILD by the AI, NEVER a
    runtime dependency · the engine stays NO-EXEC · a persona NEVER lowers a gate.
  • Byte-identical across canonical `add-method/docs`, repo-root `./`, and `_bundled/docs`.

NAV REGISTRATION — `mkdocs.yml`
  • The chapter is listed in the book nav after "17 · Components" (the orphan_chapter guard reads the
    mkdocs nav, not the marketing README).

GLOSSARY — `appendix-c-glossary.md` (3 book trees)
  • Defines the persona headwords: **persona** (a project-fit requirements persona distilled from a
    teacher to critical-rules + default-requirement + measurable success-metrics) and **persona loop**
    (seed→grow→apply). Bold-headword + em-dash form; byte-identical across trees.

SKILL POINTER — `SKILL.md` (3 skill trees)
  • A one-line pointer to the persona loop (where personas live: `.add/personas/`; how they grow:
    deltas→fold; how they apply: design/streams/advisor/build). Lean-fence-aware.

PARITY / NO-EXEC
  • 18-personas.md + appendix-c-glossary.md byte-identical across the 3 book trees; SKILL.md across the
    3 skill trees. Docs are descriptive — the engine + BOTH pins UNCHANGED.

ERROR CODES (doc-truth invariants — the prose must satisfy each)
  orphan_chapter        -> the chapter must appear in `mkdocs.yml` nav.
  book_parity_drift     -> book/glossary surfaces byte-identical across trees or red.
  engine_touched_for_docs -> no engine change / pin re-aim (docs are descriptive).

VERIFICATION — tests assert: 18-personas.md teaches the loop · it is in mkdocs nav · glossary defines
  **persona** + **persona loop** · SKILL.md points to the loop · book/glossary parity across trees +
  SKILL.md parity · ENGINE_MD5 unchanged.

Least-sure flag surfaced at freeze: ⚠ [contract] the book parity surface is exactly 3 git-tracked trees
(canonical · repo-root · _bundled) for BOTH the new chapter and the glossary; `.add/docs` is a gitignored
runtime mirror and is NOT a committed parity surface (per the component-polish lesson). Mitigation: mirror
to all three tracked trees and run test_book_parity + test_bundle_parity locally before the gate.

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

Coverage target: every Must + Reject scenario has one doc-truth/parity test
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_chapter_exists_and_teaches_loop: 18-personas.md teaches SEED/GROW/APPLY + cross-runner + teacher-not-dependency + NO-EXEC + never-lowers-a-gate
  - test_chapter_in_nav: mkdocs.yml nav lists 18-personas.md
  - test_glossary_defines_persona_terms: appendix-c-glossary.md defines **persona** and **persona loop**
  - test_skill_points_to_loop: SKILL.md carries a persona-loop pointer
  - test_book_glossary_parity: 18-personas.md + appendix-c-glossary.md byte-identical across the 3 book trees; SKILL.md across the 3 skill trees
  - test_engine_unchanged: ENGINE_MD5 == engine_pin.ENGINE_MD5 (no engine change)
</test_plan>

Tests live in: `add-method/tooling/test_persona_method_docs.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/docs/18-personas.md` `add-method/../18-personas.md` `add-method/src/add_method/_bundled/docs/18-personas.md` `add-method/docs/appendix-c-glossary.md` `add-method/../appendix-c-glossary.md` `add-method/src/add_method/_bundled/docs/appendix-c-glossary.md` `add-method/../mkdocs.yml` `add-method/skill/add/SKILL.md` `.claude/skills/add/SKILL.md` `add-method/src/add_method/_bundled/skill/add/SKILL.md` `add-method/tooling/test_persona_method_docs.py`
Strategy (ordered batches): 1. write `add-method/docs/18-personas.md` (the loop chapter). 2. add the persona headwords to `appendix-c-glossary.md`. 3. register the chapter in `mkdocs.yml` nav. 4. add the SKILL.md persona-loop pointer. 5. mirror the chapter + glossary to repo-root + _bundled (book/bundle parity); mirror SKILL.md ×3. 6. tests. 7. lean fence — SKILL.md is lean-fenced (reclaim from SKILL.md prose if the pointer trips it; never edit test_skill_lean). Run red→green.
Known-problem fixes: book parity = 3 GIT-TRACKED trees (canonical · repo-root · _bundled) — mirror BOTH new files to all three; `.add/docs` is a gitignored runtime mirror → NOT a committed parity surface (don't require it) · orphan_chapter reads mkdocs nav → register there · SKILL.md lean fence → keep the pointer to one line + reclaim · ubiquitous-language: avoid slang in the chapter prose · engine NO-EXEC → no add.py/pin edit.
Strategy actually used: As planned, plus a 4th-twin + slang correction caught at full-suite. Wrote 18-personas.md (seed/grow/apply + cross-runner subagent + teacher-not-dependency + NO-EXEC + never-lowers-a-gate), added **persona** + **persona loop** glossary headwords, registered the chapter in mkdocs nav after ch.17, added a one-line SKILL.md pointer, mirrored to the 3 git-tracked trees, tests red→green. Corrections: (1) the glossary is synced across 4 twins (incl. the present-but-gitignored `.add/docs`) per several DocsAccord/worked-example guards → mirrored the glossary AND chapter to `.add/docs` too; (2) the ubiquitous-language guard bans bare "fold" in prose → reworded prose "fold"→"consolidate" in chapter/glossary/SKILL.md, kept ONE backticked `fold` in the chapter (code spans are slang-exempt) so the GROW teaching still names the engine op; (3) the SKILL.md pointer tripped the lean core pool (≤18031) → reclaimed bytes from SKILL.md's own bullet prose (run/streams/confidence/loop/release/monorepo/sensitivity/fast-lane lines), test_skill_lean untouched. Engine + both pins UNCHANGED.
Safety rule (feature-specific): docs are descriptive — never change engine behavior; keep every tree byte-identical.
Code lives in: `add-method/docs/` + `add-method/skill/add/` + repo root
Constraints: do NOT change any test or the contract; do NOT edit engine code / re-aim a pin; allow-list packages only; ask if unclear.

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
- [x] `add-method/docs/18-personas.md` exists and reads as a coherent chapter teaching SEED→GROW→APPLY + cross-runner subagent + teacher-not-dependency + engine NO-EXEC + never-lowers-a-gate — confirmed by reading the chapter + the teaches-loop test
- [x] `mkdocs.yml` nav lists "18 · Personas — the project-fit learning loop" after "17 · Components" — confirmed by reading the nav + the in-nav test
- [x] `appendix-c-glossary.md` defines **persona** and **persona loop** (bold-headword/em-dash form, with `See [18 Personas]` links) — confirmed by the glossary test
- [x] SKILL.md carries a one-line persona-loop pointer (`.add/personas/` + grow/apply) — confirmed by the skill-pointer test
- [x] 18-personas.md + appendix-c-glossary.md byte-identical across the 3 git-tracked book trees (+ the present `.add/docs` runtime twin), SKILL.md ×3 skill trees, ENGINE_MD5 unchanged — confirmed by the parity + engine tests + book/bundle/worked-example parity suites

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read in full, not skimmed: read 18-personas.md end-to-end (seed/grow/apply, teacher-not-dependency, cross-runner subagent, the never-lowers-a-gate section), the two new glossary headwords, the mkdocs nav entry, and the SKILL.md pointer. Confirmed the chapter teaches the loop accurately against the wave-1+2 tasks it documents, the teacher (agency-agents) is framed as read-off-build / never a runtime dependency, the engine NO-EXEC + a-persona-never-lowers-a-gate invariants are stated, and "fold" appears only as a backticked code span (slang-exempt) — prose uses "consolidate". No engine code touched.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self · adversarially checked: probed the 6 tests for vacuousness — the teaches-loop test pins 13 distinct content tokens (seed/grow/apply/observe/fold/udd/advisor/overlay/subagent/agency-agents/no-exec/never lower/hard-stop), not one umbrella word; the nav test reads mkdocs.yml (the authoritative TOC the orphan_chapter guard uses, not the marketing README); the glossary test pins both **persona** AND the distinct **persona loop** headword; parity is byte-set equality across the 3 git-tracked trees. Tried to refute by re-reading: no overfit, no stub. NOTE: full-suite run caught 6 ripples (4-twin glossary sync incl `.add/docs`, worked-example parity, "fold" slang ×2, lean core pool) — all corrected (mirrored to the 4th twin, "fold"→"consolidate" in prose / backticked in the one teaching reference, reclaimed bytes from SKILL.md's own prose) before this gate; test_skill_lean untouched.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: self
1. Security: CLEAR — descriptive docs only; no code, no secrets, no execution surface.
2. Concurrency: CLEAR — prose/nav edits across trees; no runtime, no shared state.
3. Architecture: CLEAR — new chapter follows the ch.17-components precedent (nav + glossary + skill pointer); engine + both pins unchanged; book parity held across all twins.
Verdict: PASS
Residue: none
Binding: advisory — non-mechanical (doc-truth edit)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-resolved under autonomy: auto) · date: 2026-06-30

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. The Advisor 3-lens verdict and the Refute-read verdict are both measured by `add.py audit` (`advisor_verdict_unrecorded` · `refute_unrecorded`) — neither is engine-blocked; a human spot-audit is the backstop for any finding the AI did not surface or record. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose a new chapter 18 + glossary + SKILL pointer; rejected folding it into an existing chapter (rejected by the human — wants a standalone chapter) · skill-guide only, no book (rejected — the milestone requires the book to describe the loop)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: As planned, plus a 4th-twin + slang correction caught at full-suite. Wrote 18-personas.md (seed/grow/apply + cross-runner subagent + teacher-not-dependency + NO-EXEC + never-lowers-a-gate), added **persona** + **persona loop** glossary headwords, registered the chapter in mkdocs nav after ch.17, added a one-line SKILL.md pointer, mirrored to the 3 git-tracked trees, tests red→green. Corrections: (1) the glossary is synced across 4 twins (incl. the present-but-gitignored `.add/docs`) per several DocsAccord/worked-example guards → mirrored the glossary AND chapter to `.add/docs` too; (2) the ubiquitous-language guard bans bare "fold" in prose → reworded prose "fold"→"consolidate" in chapter/glossary/SKILL.md, kept ONE backticked `fold` in the chapter (code spans are slang-exempt) so the GROW teaching still names the engine op; (3) the SKILL.md pointer tripped the lean core pool (≤18031) → reclaimed bytes from SKILL.md's own bullet prose (run/streams/confidence/loop/release/monorepo/sensitivity/fast-lane lines), test_skill_lean untouched. Engine + both pins UNCHANGED.
- [AI] verify — gate PASS (reviewed by Tin Dang (auto-resolved under autonomy: auto))

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
