# TASK: Align book ch02 flow + diagram + GLOSSARY to the expectations-first plan phase

slug: book-plan-align · created: 2026-07-13 · stage: mvp
milestone: expectations-first
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: Align the BOOK's phase-model prose to the expectations-first flow — the GLOSSARY names the unified **Plan** phase and redefines **Ground** as Plan's first sub-block (no longer a phase-0 preamble/step-0 before Specify), and no stale "contract phase"/"ground phase"/"step 0 preamble" phrasing survives anywhere in `docs/`. ch02 narrative + the mermaid diagram were already realigned by guides-and-skill (T3); this task closes the remaining GLOSSARY + references gap and PINS the alignment so it cannot silently regress.
Framings weighed: GLOSSARY-term rewrite + a stale-prose grep guard (chosen — the surgical, test-pinnable gap: ch02/mermaid/SKILL are already aligned and green, so a deep ch02 rewrite would be make-work and risk regressing passing prose) · full ch02 narrative rewrite (rejected — already done by T3; test_flow_diagram + test_ground_prose green) · leave the GLOSSARY as-is (rejected — the exit criterion requires the GLOSSARY to name the plan phase, and a reader hitting "Ground (phase-0 preamble)… step 0" is told the OLD flow the engine no longer runs).
Must:
<must>
  - M1: `docs/appendix-c-glossary.md` defines a **Plan** phase term — the unified step 3 that grounds the real code, freezes the contract, and sets the build strategy, costing the flow exactly ONE human approval (the plan freeze).
  - M2: the **Ground** GLOSSARY term is redefined as the FIRST part of the Plan phase (AI-owned, adds no approval), NOT "the per-task phase before Specify" / "step 0" / a "phase-0 preamble" — the stale phase-0 framing is removed.
  - M3: no stale phase-model phrasing survives in `docs/` — none of "phase-0 preamble", "step 0" (as a phase), "the contract phase", "the ground phase" as a live phase — pinned by a grep-test over the book trees.
  - M4: the book GLOSSARY stays byte-synced across its tracked twins (the existing ×4 `_doc_trees("appendix-c-glossary.md")` parity), and ch02's already-green alignment (`seven steps` brand, `plan` named, mermaid backward edges) is NOT regressed.
</must>
Reject:
<reject>
  - R1: redefining Ground/adding Plan must NOT weaken or delete the **Contract** concept -> the frozen-external-shape meaning stays; the contract is now frozen WITHIN the Plan phase, not renamed away.
  - R2: this task introduces NO new approval gate and NO engine/behavior change -> docs-only; ENGINE_MD5/ENGINE_PKG_MD5 unchanged (a code touch here is out of scope, a change-request).
  - R3: the grep guard must not false-flag legitimate prose -> "grounding is the first part of Plan" and a historical "(formerly …)" bridge stay green; only the LIVE stale framing is forbidden.
</reject>
After:
<after>
  - a reader of the book GLOSSARY sees Plan named and Ground defined as Plan's first sub-block; no stale phase-0/contract-phase prose remains in docs/; a grep-test pins it; the glossary twins stay byte-synced; the engine is untouched.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ ch02 (`02-the-flow.md`) + the mermaid diagram are ALREADY fully aligned by T3 (guides-and-skill), so this task is GLOSSARY + appendix-g + a pin-test, NOT a ch02 rewrite. Lowest confidence because a stale phrase could hide in a chapter my grep didn't cover; if wrong (ch02 still carries stale phase prose): the same grep guard catches it and the fix extends to that chapter — a contained widening, not a reshape. The grep-test IS the safety net for this assumption.
  - [x] the **Contract** GLOSSARY term (appendix-c) gains a one-clause "frozen within the Plan phase" nod — RESOLVED at freeze (Tin Dang): in scope, tiny diff, consistent with the new flow.
  - [x] the add-flow.png raster IS re-rendered — RESOLVED at freeze (Tin Dang): the raster is stale (last built pre-expectations-first; the tracked image-gen prompt `add-method/diagrams/prompt-flow.txt` still labels step 3 "Contract"). This task UPDATES the tracked render SOURCE (prompt-flow.txt → "Plan"; the mermaid + CHECKLIST are already aligned/green); the raster PNG regeneration itself is an image-model + HUMAN visual-gate step (test_flow_diagram: "image models garble labels — reviewed against CHECKLIST by a person") — I cannot rasterize headless (no mmdc/image tool), so the corrected prompt is prepared and the raster render is flagged as a release/verify human step.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: GLOSSARY names the Plan phase   # M1
  Given the book glossary docs/appendix-c-glossary.md
  When I read it
  Then it defines a **Plan** term describing the unified step 3 (ground the code, freeze the contract, set the build strategy) that costs exactly one human approval

Scenario: Ground is redefined as Plan's first part   # M2
  Given the **Ground** term in the book glossary
  When I read its definition
  Then it names grounding as the FIRST part of the Plan phase (AI-owned, no new approval)
  And it does NOT call Ground "the per-task phase before Specify" nor "step 0" nor "phase-0 preamble"

Scenario: no stale phase-model prose survives   # M3
  Given every book file under docs/ (and its synced trees)
  When a grep-test scans for the forbidden live-phase phrasings ("phase-0 preamble", "step 0" as a phase, "the contract phase", "the ground phase")
  Then no match is found

Scenario: glossary twins stay byte-synced and ch02 alignment is preserved   # M4
  Given the ×4 appendix-c-glossary.md trees and ch02
  When I run the existing test_ground_prose + test_flow_diagram suites
  Then appendix-c-glossary.md is byte-identical across all trees
  And ch02 still names "seven steps" + the "plan" phase and the mermaid keeps its backward-correction edges (no regression)

Scenario: the Contract concept is preserved   # R1
  Given the **Contract** glossary term
  When I read the book after this change
  Then the Contract still means the fixed external shape frozen before the build
  And it is not deleted or renamed away (only clarified as frozen within Plan)

Scenario: docs-only, engine untouched   # R2
  Given this task's build
  When it completes
  Then no engine file changed — ENGINE_MD5 and ENGINE_PKG_MD5 are the values plan-legibility left (9311ec35 / 28212a55), unchanged
  And only docs/ (+ synced doc trees) were written

Scenario: the grep guard does not false-flag legitimate prose   # R3
  Given prose like "grounding is the first part of Plan" and a historical "(formerly the ground phase)" bridge
  When the M3 grep-test runs
  Then those lines stay green (only the LIVE stale framing is forbidden, not a history bridge)
```

</scenarios>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Grounding (the real code the contract will cite — gather BEFORE you freeze)
Touches (files · symbols · signatures): `docs/appendix-c-glossary.md` — the book glossary (×4 trees: repo-root · `add-method/docs` canonical · `_bundled/docs` · `.add/docs` dogfood); carries a stale `**Ground (phase-0 preamble)**` term (~l.39: "the per-task phase *before* Specify … precedes the seven steps as step 0") and NO `**Plan**` term · `docs/appendix-g-references.md` (×4) — spec-kit comparison (~l.94: "ADD's specify and contract phases map onto specify and plan") · `add-method/tooling/test_ground_prose.py` — the pin home (`BookGlossaryTest.test_book_glossary_defines_ground` asserts only that `**Ground`/`**Grounding map` exist; `test_book_glossary_synced_x4` byte-syncs the 4 trees via `_doc_trees`) · `02-the-flow.md` — ALREADY aligned by T3 (names "3 Plan" + "seven steps"; `test_flow_diagram` + `test_ground_prose.FlowChapterTest` green — do not regress).
Context (working folder): the AIDD book under `docs/` (4 synced trees); no code/state — docs-only.
Honors (patterns / conventions): book parity = 4 byte-synced trees (3 git-tracked + the `.add/docs` dogfood; walk-excluded but still byte-synced) · GLOSSARY style `**Term** — definition`, one name per concept · the "seven steps" brand (grounding is Plan's first PART, never an 8th step) · docs-only, engine untouched (ENGINE_MD5/PKG unchanged) · T3's `git mv`-and-hand-edit-all-trees convention (no auto-sync script).
Seams consulted: `.add/SEAMS.md#scope-token-grammar` — a bare token resolves under the TASK dir; the repo-root book twins are named `add-method/../<file>` (the only grammar form that reaches a bare repo-root file), verified against `_declared_scope`.
Anchors the contract cites: the `**Plan**` / `**Ground**` / `**Contract**` glossary terms · `test_ground_prose.BookGlossaryTest` · `_doc_trees("appendix-c-glossary.md")`.
Issues/Risks: a stale phrase could hide in a chapter my grep missed — VERIFIED not: a full `docs/` scan for old-flow phrasing found only appendix-c (Ground term) + appendix-g ("contract phases"); 03/04/06/10/appendix-f/README/GETTING-STARTED cite "contract" as a valid CONCEPT, not a stale phase (the grep-guard is the standing net) · the grep-guard must not false-flag a legitimate "(formerly …)" history bridge or "grounding is the first part of Plan" · byte-sync must cover all 4 trees incl. the walk-excluded `.add/docs` twin (edited but invisible to the scope guard).
Related intent: expectations-first milestone — the plan phase now unites ground+contract+build-strategy (one freeze); this task pays the book-narrative debt guides-and-skill (T3) explicitly deferred. Exit criterion: "book ch02 + GLOSSARY name the plan phase and expectations-first order — pinned by grep-test".
Ground SHA: `ca86bf1`

### Contract (freeze the shape — the HARD, tamper-guarded core)

```
# docs contract — observable book-glossary shape (prose task; no API/schema)
appendix-c-glossary.md (all 4 trees, byte-identical) defines:
  **Plan** — the unified step 3: ground the real code → freeze the contract → set the
             build strategy; costs the flow exactly ONE human approval (the plan freeze).
  **Ground** — the FIRST part of the Plan phase (AI-owned, adds no approval); NOT "the
             per-task phase before Specify", NOT "step 0", NOT a "phase-0 preamble".
  **Contract** — PRESERVED + a one-clause nod: the fixed external shape, frozen WITHIN the Plan phase, before the build (the frozen-external-shape meaning is unchanged).
diagram render SOURCE (add-method/diagrams/prompt-flow.txt) labels step 3 "Plan" (not "Contract"),
  matching the already-aligned CHECKLIST.md + ch02 mermaid; the add-flow.png RASTER regeneration is a
  human image-model visual-gate step (not produced in this task).
grep-guard (test_ground_prose) over the walked book trees:
  FORBID (live-phase framing): "phase-0 preamble" · "step 0" as a phase · "the contract phase" · "the ground phase"
  ALLOW: "grounding is the first part of Plan" · a "(formerly …)" history bridge
engine untouched: ENGINE_MD5 == 9311ec35… AND ENGINE_PKG_MD5 == 28212a55… (unchanged)
```

Glossary deltas: `Plan (phase): the unified step 3 — ground the code, freeze the contract, set the build strategy; one human approval (the plan freeze).` (a BOOK-glossary term; the engine GLOSSARY.md.tmpl already carries plan-flow vocabulary)
Status: FROZEN @ v1 — approved by Tin Dang
Reported: no
Least-sure flag surfaced at freeze: [contract] ch02 + the mermaid are ALREADY aligned (T3), so this is a surgical GLOSSARY + appendix-g + pin-test change, NOT a ch02 rewrite — the M3 grep-guard is the standing net if a stale phrase hides in a chapter the ground scan missed (§1 ⚠). Cost-if-wrong: the guard goes red and the fix widens to that one chapter — contained, not a reshape.

### Build-strategy (the intended approach — SOFT: preferred; the builder self-improves and records what it ACTUALLY did at verify)
Scope (may touch): `add-method/docs/` `add-method/src/add_method/_bundled/docs/` `add-method/diagrams/` `add-method/tooling/test_ground_prose.py` `add-method/../appendix-c-glossary.md` `add-method/../appendix-g-references.md`   <the WALKED book trees (canonical + bundle dirs) + the tracked diagram-source dir (prompt-flow.txt) + the pin test + the two repo-root twins (named via the add-method dot-dot form since the token grammar can't reach a bare repo-root file); the dot-add docs twin is byte-synced too but walk-excluded. Verified against the live declared-scope resolver. NEVER backtick a path in this note — backticks parse as scope tokens.>
Strategy (ordered batches): 1. red — extend `test_ground_prose.py`: assert appendix-c defines a `**Plan**` term + a stale-prose grep-guard (forbid the 4 live-phase phrasings across the walked book trees, allow the history bridge) → confirm RED against the current stale glossary. 2. rewrite the appendix-c `**Ground**` term (Plan's first part, drop phase-0/step-0) + ADD the `**Plan**` term + the one-clause `**Contract**` "within the Plan phase" nod; canonical (`add-method/docs`) first. 3. fix appendix-g "specify and contract phases" → "specify and plan phases". 4. update the tracked diagram render source `add-method/diagrams/prompt-flow.txt` step 3 "Contract" → "Plan" (match CHECKLIST.md + mermaid); the raster PNG regeneration is a HUMAN visual-gate step (flagged in §6/release, not produced here — no headless rasterizer). 5. byte-sync all 4 book trees (canonical → root · bundle · `.add/docs`) + any diagram-source twin. 6. targeted suite (test_ground_prose + test_flow_diagram) + a repo-wide stale-prose sweep; confirm ENGINE_MD5/PKG unchanged.
Approach (domain strategy): surgical prose edit that PRESERVES the "seven steps" brand and the Contract concept; the grep-guard forbids only LIVE stale framing (a history bridge stays green) — from §1 Framings (the test-pinnable gap, not a make-work rewrite of already-green ch02).
Data strategy: none — prose files; the "shape" is the observable glossary text + the grep-guard, per the Contract block above.
Pattern: the book-parity convention (byte-synced doc trees) + the existing `test_ground_prose` pin home; extends T3's realignment, does not redraw it.
Optimization stance: readability + reader-truth first (a glossary must describe the flow the engine actually runs) — no perf budget; ⚠ least-trusted facet: the grep-guard's forbidden-phrase list catching every LIVE stale framing without false-flagging a bridge (mitigated by R3's allow cases in the red suite).
Persona (required): book-technical-writer — the method prose IS the product surface; a stale glossary is a product bug.
Spawn isolation (default): none — inline, single-context docs edit (no subagent spawn; small surgical surface).
Known-problem fixes: backticks in the Scope NOTE parse as scope tokens (kept OUT here) · a bare repo-root filename mis-resolves under the task dir (used `add-method/..`) · the `.add/docs` twin is walk-excluded so a missed sync there won't scope-fail but WILL break `test_book_glossary_synced_x4` (sync all 4).

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: <e.g. 90%>
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_<scenario>: arrange <Given> / act <When> / assert <Then> + assert <unchanged> · covers: <M#, R:code — optional>
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

> The change plan — grounding + contract + build-strategy — was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope, follow the strategy (improve on it if the code teaches you better), and touch no test or the frozen contract.
Strategy actually used: <fill at VERIFY — the strategy you ACTUALLY used (or "as planned"); harvested into the §7 Decisions (ADR) block as the [AI] build decision>
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the frozen §3 contract; stay inside the §3 Build-strategy Scope; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — test_ground_prose (18) + test_flow_diagram green; full suite confirmed (see GATE RECORD)
- [x] coverage did not decrease — added 5 tests (PlanPhaseGlossaryTest + EngineUntouchedByBookAlignTest); removed none
- [x] no test or contract was altered during build — test_ground_prose.py was written in the TESTS phase (pre-snapshot); build touched only docs/ + the diagram prompt; tamper tripwire clean
- [x] the green was EARNED, not gamed — the M1/M2/M3 tests were RED against the stale glossary and pass only because the real prose changed; the guard has a non-vacuous "still catches a live stale claim" assertion (refute-read below)
- [x] concurrency / timing — N/A: docs-only, no runtime code path
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose edits; zero new deps
- [x] layering & dependencies follow CONVENTIONS.md — book-parity convention (4 byte-synced trees) honored; engine untouched
- [x] a person reviewed and approved the change — freeze approved by Tin Dang (v1); gate auto-PASS under autonomy:auto (see GATE RECORD)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] **Plan** term present (appendix-c l.39): "the unified step 3 … grounds the real code, freezes the **Contract**, and sets the build strategy … exactly ONE human approval — the plan freeze" — confirmed by grep + read
- [x] **Ground** term reads "the FIRST part of the **Plan** phase" and carries none of phase-0 preamble / as step 0 / phase before specify — confirmed by grep + read
- [x] **Contract** term carries "Frozen within the **Plan** phase", meaning intact — confirmed by read
- [x] appendix-g reads "specify and plan phases map onto" (no "contract phases") — confirmed by grep
- [x] prompt-flow.txt card 3 reads `3  "Plan"  — "ground the code, freeze the contract"` (matches CHECKLIST.md l.9) — confirmed by grep
- [x] all 4 appendix-c + all 4 appendix-g trees byte-identical (md5 set size 1 each) — confirmed by md5
- [x] the 3 formerly-RED tests (M1/M2/M3) now pass; test_flow_diagram still green; ENGINE_MD5 == pin (add.py untouched) — confirmed by targeted run

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] DIALECT — the guard's forbidden-phrase list speaks the contract's own literal stale strings (phase-0 preamble · as step 0 · phase before specify · the contract/ground phase); the M1/M2 asserts read the real rendered term text, not a proxy
- [x] WIRING (code) — the one new symbol `_stale_phase_hits` is referenced by both M3 (`test_no_stale_phase_prose_in_book`) and R3 (`test_grep_guard_allows_legitimate_prose`); `_STALE_PHASE_PROSE` + `_deemphasize` feed it
- [x] DEAD-CODE (code) — no orphan; every added helper/constant is exercised by a test in the same file
- [x] SEMANTIC (prose / non-code) — read in full: the new **Plan** term (grounds → freezes → strategy, one approval), the rewritten **Ground** term (Plan's first part, no phase-0), the **Contract** nod, the Grounding-map §0→§3 fix, appendix-g, and the prompt-flow card all read true to the expectations-first flow; the "seven steps" brand is preserved (grounding is Plan's PART, not an 8th step)

### Live-verify evidence — confirm the §3 PLAN grounding anchors still resolve (fill at the gate)
> Re-resolve every symbol the §3 Contract cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] every anchor the §3 Contract cites still resolves — the `**Plan**`/`**Ground**`/`**Contract**` terms exist in appendix-c; `test_ground_prose.BookGlossaryTest` + `_doc_trees("appendix-c-glossary.md")` resolve and run green; add-method/diagrams/prompt-flow.txt + CHECKLIST.md exist
- [x] no anchor moved/renamed since Ground SHA ca86bf1 — only content within the named files changed; no file renamed

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: (1) is the green vacuous? No — M1/M2/M3 were RED against the real stale glossary and pass only because the prose changed; I re-ran them pre-fix (3 failures) then post-fix (pass). (2) does the guard test only tautologies? No — R3 asserts the guard STILL fires on a live stale claim ("precedes the seven steps as step 0"), so a no-op guard would fail R3. (3) is the "formerly" exemption a loophole that lets stale prose hide? It only exempts lines that self-label as history bridges; the shipped glossary uses no "formerly" line to smuggle stale framing (verified by the raw sweep, which found zero non-formerly hits). (4) engine untouched — add.py md5 == pin, so R2 isn't gamed by a hidden code edit.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR — prose-only; no code path, no input handling, no secret/dependency surface
2. Concurrency: CLEAR — no runtime behavior; static doc + test-file edits
3. Architecture: CLEAR — honors the book-parity convention (4 byte-synced trees) + the existing test_ground_prose pin home; adds no new phase/gate; engine byte-identical
Verdict: PASS
Residue: none — EXCEPT the add-flow.png RASTER remains stale by design (image-model + human visual-gate artifact; the tracked render SOURCE prompt-flow.txt is updated) → a release/verify human step, tracked in §7 Watch
Binding: advisory — mechanical/docs

### GATE RECORD
Reported: yes — the gate report (banner/ARC + evidence) rendered before this outcome was recorded
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: auto-gate (autonomy:auto) on complete evidence — full suite 3446 green · scope clean (0 out-of-scope) · engine byte-identical (ENGINE_MD5 == pin) · Advisor 3-lens CLEAR (no security finding) · Refute-read EARNED · freeze approved by Tin Dang (v1). Residue: the add-flow.png raster regen is a human visual-gate release step (§7). · date: 2026-07-13

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the M3 stale-prose grep-guard (`test_ground_prose.PlanPhaseGlossaryTest`) is the standing monitor — it goes red if any future edit reintroduces phase-0/contract-phase framing into the book. OPEN HUMAN STEP (release): regenerate `add-flow.png` from the corrected `prompt-flow.txt` (image model) and review the raster against `add-method/diagrams/CHECKLIST.md` — the raster is a human visual gate (image models garble labels), not producible headless; the tracked render source is already aligned.

### Decisions (ADR)
- [AI] specify — chose GLOSSARY-term rewrite + a stale-prose grep guard; rejected full ch02 narrative rewrite (rejected — already done by T3; test_flow_diagram + test_ground_prose green) · leave the GLOSSARY as-is (rejected — the exit criterion requires the GLOSSARY to name the plan phase, and a reader hitting "Ground (phase-0 preamble)… step 0" is told the OLD flow the engine no longer runs).
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — approach: surgical prose edit that PRESERVES the "seven steps" brand and the Contract concept; the grep-guard forbids only LIVE stale framing (a history bridge stays green) — from §1 Framings (the test-pinnable gap, not a make-work rewrite of already-green ch02).
- [AI] build — data strategy: none — prose files; the "shape" is the observable glossary text + the grep-guard, per the Contract block above.
- [AI] build — pattern: the book-parity convention (byte-synced doc trees) + the existing `test_ground_prose` pin home; extends T3's realignment, does not redraw it.
- [AI] build — optimization stance: readability + reader-truth first (a glossary must describe the flow the engine actually runs) — no perf budget; ⚠ least-trusted facet: the grep-guard's forbidden-phrase list catching every LIVE stale framing without false-flagging a bridge (mitigated by R3's allow cases in the red suite).
- [AI] build — strategy used: as planned
- [AI] verify — gate PASS (reviewed by auto-gate (autonomy:auto) on complete evidence — full suite 3446 green)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

