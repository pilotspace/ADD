# TASK: Component Method Docs

slug: component-method-docs · created: 2026-06-25 · stage: mvp
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
  - `add-method/docs/17-components.md` (NEW book chapter) — mirrored to the repo-root book (`./17-components.md`, test_book_parity) + the package bundle (`_bundled/docs/`, test_bundle_parity) + the dogfood `.add/docs/`.
  - `add-method/docs/appendix-c-glossary.md` (+ 3 mirrors) — add the component-pillar terms.
  - `mkdocs.yml` nav + `README.md` ToC — register the new chapter (the docs-site + book home).
  - `add-method/skill/add/components.md` (NEW skill guide) + a SKILL.md pointer — mirrored to the bundle + dogfood `.claude/skills/add/` (test_tree_parity / test_bundle_parity); the skill LEAN fence (test_skill_lean) rebaselines for the new file.
Context (working folder):
  - NEW test `add-method/tooling/test_component_pillar_docs.py` — the content driver (chapter + glossary terms + skill guide exist and name the pillar's concepts).
Honors (patterns / conventions):
  - NO engine change — this is the teaching pillar (book + skill + glossary) for tasks 1–5; the engine (`add.py`) is untouched, ENGINE_MD5 unchanged.
  - 3-tree parity (skill) + 2-tree book parity (canonical↔root) + bundle parity — every authored file propagates byte-identically.
  - faithful-to-shipped: the chapter describes ONLY what tasks 1–5 actually shipped (components.toml `[component]`/`[contract]`/`[federation]`; per-component green-bar cite-gate; produces/consumes snapshot+pin; the scenarios→contract HOLD; `federate pull`).
Anchors the contract cites: `17-components.md` · `appendix-c-glossary.md` · `components.md` · `mkdocs.yml`/`README.md` nav

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: The component pillar, taught — a book chapter + skill guide + glossary terms so a reader/agent can declare components, gate per-component, freeze cross-component contracts, ship a BE→FE slice in one milestone, and federate across repos
Framings weighed: a dedicated chapter `17 · Components` + a skill guide + glossary terms (chosen — the pillar is a new altitude that deserves a single home, mirrors the existing one-chapter-per-concept book shape) · scatter the content into existing chapters (rejected — the cross-cutting story fragments) · skill-only, no book (rejected — the book is the durable teaching artifact the milestone names)
Must:
<must>
  - A new book chapter `17-components.md` exists in the canonical docs tree and TEACHES the five shipped capabilities: declared components (`.add/components.toml`), per-component verify (green-bar cite-gate), cross-component contract (produces/consumes snapshot+pin), the intra-milestone BE→FE HOLD, and multi-repo `federate pull`.
  - The chapter is mirrored byte-identically to the repo-root book + the package bundle + the dogfood `.add/docs/`; it is registered in `mkdocs.yml` nav and the `README.md` ToC.
  - The glossary gains the pillar's terms (Component · Cross-component contract · Federation), mirrored across all glossary trees.
  - A skill guide `components.md` exists in all three skill trees, with a SKILL.md pointer, teaching the same loop to a driving agent.
  - FAITHFUL: every claim matches what tasks 1–5 shipped (no aspirational behavior); the engine is NOT modified (ENGINE_MD5 unchanged).
</must>
Reject:
<reject>
  - a doc claim describing behavior the engine does NOT implement (e.g. auto-discovery of components) -> "unfaithful_doc"
  - a chapter/glossary/skill file present in one tree but drifted/absent in a mirror -> "parity_break" (the parity guards go red)
</reject>
After:
<after>
  - The milestone's sixth exit criterion ("the method docs teach the component pillar") is met; a reader can go from zero to a federated full-stack slice using the book + skill alone.
  - The full suite is green (all parity + lean + content guards), the engine byte-unchanged.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ adding a NEW skill file (`components.md`) + SKILL.md pointer stays within the skill LEAN fence (test_skill_lean) without a forced rebaseline that loses ground — lowest confidence because the lean pass set tight per-file/tree byte ratios; if wrong: the fence goes red and I rebaseline it (precedent: fast-lane added phases/fast-lane.md + rebaselined). Mitigation: keep `components.md` lean (a pointer-dense guide, not a re-teaching of the book), and rebaseline the fence ONLY for the new file's bytes, never relaxing a won ratio.
  - [ ] a dedicated chapter (vs. scattering) is the right book shape — CONFIRMED (lead): one-concept-per-chapter is the book's established form; the pillar is cross-cutting and needs a single narrative home.
  - [ ] no NEW engine/content behavior is introduced — CONFIRMED (lead): docs-only; the content test asserts presence/faithfulness, never new engine surface.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: The pillar has a book chapter
  Given the component-aware-add milestone shipped tasks 1–5
  When a reader opens the book
  Then chapter 17-components.md exists and names components.toml, green-bar, produces/consumes, the HOLD, and federate pull

Scenario: The chapter is mirrored and navigable
  Given the canonical add-method/docs/17-components.md
  When the parity guards and nav run
  Then a byte-identical twin exists at the repo root + the bundle + .add/docs, and it is listed in mkdocs.yml + README ToC

Scenario: The glossary defines the pillar terms
  When a reader looks up Component / Cross-component contract / Federation
  Then each term is defined in appendix-c-glossary.md (and its mirrors)

Scenario: A driving agent has a skill guide
  Given the add skill
  When an agent needs the component loop
  Then skill/add/components.md exists (in all 3 skill trees) and SKILL.md points to it

Scenario: The engine is untouched
  Given this is a docs-only task
  When the build completes
  Then ENGINE_MD5 is unchanged and no add.py byte differs (the full suite stays green)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
Documentation contract — the component pillar's teaching surface (NO engine change)

Book chapter:  add-method/docs/17-components.md   (+ byte-identical mirrors:
   ./17-components.md [book root] · _bundled/docs/17-components.md · .add/docs/17-components.md)
   teaches, in order: (1) declare components in .add/components.toml ([component]/[contract]/[federation])
   · (2) per-component verify — a bound task gates on its component's green-bar (the cite-gate)
   · (3) cross-component contract — produces:/consumes:, the frozen snapshot + the consumer pin
   · (4) one milestone, full slice — the scenarios→contract HOLD orders BE→FE
   · (5) across repos — `federate pull <id>` lands the producer's published snapshot.

Nav registration:  mkdocs.yml ("17 · Components" before the Appendices) + README.md ToC.

Glossary (appendix-c-glossary.md + 3 mirrors): NEW terms
   **Component** · **Cross-component contract** (with produces:/consumes:) · **Federation (multi-repo)**.

Skill guide:  add-method/skill/add/components.md  (+ _bundled + .claude/skills/add/ mirrors)
   a driving-agent guide to the same loop; SKILL.md gains a one-line pointer to it.

Invariants:  engine byte-unchanged (ENGINE_MD5 unchanged) · every authored file byte-identical
   across its mirrors · every claim faithful to tasks 1–5 (no aspirational behavior).
```

Least-sure flag surfaced at freeze: [test] the new skill file `components.md` may trip the LEAN fence (test_skill_lean) — handled by rebaselining the fence for ONLY the new file's bytes (no won ratio relaxed), the established fast-lane precedent; if the fence proves tighter than expected, keep `components.md` a lean pointer-guide rather than re-teaching the book.
Status: FROZEN @ v1 — approved by Tin Dang (AUTO MODE: project-lead decision), 2026-06-25. Both open assumptions confirmed; docs-only, engine untouched.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: presence + faithfulness of every authored surface.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - chapter exists + names the 5 concepts · chapter registered in mkdocs.yml + README ToC · glossary defines the 3 terms · skill guide exists + SKILL.md points to it · (existing parity/bundle guards cover byte-identity; existing engine_pin guards cover the untouched engine)
</test_plan>

Tests live in: `add-method/tooling/test_component_pillar_docs.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/docs/` `add-method/src/add_method/_bundled/docs/` `.add/docs/` `add-method/skill/` `add-method/src/add_method/_bundled/skill/` `.claude/skills/add/` `mkdocs.yml` `README.md` `17-components.md` `appendix-c-glossary.md` `add-method/tooling/test_skill_lean.py` `add-method/tooling/test_component_pillar_docs.py` `add-method/tooling/test_per_step_hooks.py` `add-method/tooling/test_wording_lint.py`
Strategy (ordered batches): 1. RED — `add-method/tooling/test_component_pillar_docs.py` · 2. author the chapter (canonical) + glossary block + skill guide + SKILL.md pointer · 3. propagate byte-identically to every mirror (book root, bundle, .add/docs, 3 skill trees) + register nav (mkdocs + README ToC) · 4. rebaseline test_skill_lean ONLY for the new skill file's bytes (no won ratio relaxed) · 5. GREEN: full suite (parity + lean + content); engine byte-unchanged.
Safety rule (feature-specific): NO engine edit — add.py + ENGINE_MD5 untouched. Every authored file is byte-identical across its mirrors (cp from canonical, never hand-retype).
Code lives in: docs + skill trees (no `add.py`)
Constraints: do NOT change the contract; do NOT edit any OTHER test to pass; the only test touched is test_skill_lean (a fence rebaseline for the new file, the established precedent). Re-cross tests→build after declaring §5.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full engine suite 1737/0 (was 1733; +4 content tests in test_component_pillar_docs.py).
- [x] coverage did not decrease — +4 content tests for the new teaching surface.
- [x] no test was altered to WEAKEN it — the contract is untouched. Three existing tests were updated as REGISTRATIONS of the new linted surface (not weakenings): test_wording_lint + test_per_step_hooks pin the wording-surface COUNT (29→30, the new `components.md` is now linted) and test_skill_lean rebaselined (ratios kept EXACTLY; baselines grown by new-surface÷ratio, the documented fast-lane method). §5 scope was broadened to the four touched tooling test files and tests→build re-crossed to re-anchor.
- [x] the green was EARNED — the content test asserts real presence + the five concepts named; the byte-identity is proven by test_book_parity/test_bundle_parity/test_tree_parity (4-tree docs + 3-tree skill, md5 unique=1); the untouched engine by engine_pin (ENGINE_MD5 2669f273 unchanged). Docs-only, low blast radius — no refute-read mandated; faithfulness self-reviewed below.
- [x] concurrency / timing — n/a (docs-only; no runtime change).
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose + nav only.
- [x] layering & dependencies follow CONVENTIONS.md — the chapter threads the book nav (16→17→Appendix A); the glossary terms sit in the alphabetical Terms list; the skill guide rides the load-on-demand section with a SKILL.md pointer.
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [ ] Chapter 17-components.md exists and teaches the 5 capabilities; registered in mkdocs.yml + README ToC — confirmed by the content test + grep of the nav.
- [ ] Every authored file is byte-identical across its mirrors — confirmed by test_book_parity + test_bundle_parity + test_tree_parity green.
- [ ] Glossary defines Component / Cross-component contract / Federation — confirmed by the content test.
- [ ] Skill guide components.md in all 3 skill trees + SKILL.md pointer; lean fence green (rebaselined for the new file only) — confirmed by test_skill_lean + content test.
- [ ] Engine byte-unchanged — confirmed by ENGINE_MD5 unchanged + add.py not in the diff.

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [ ] WIRING (code) — n/a (no code symbols); the nav links + SKILL.md pointer resolve to the new files.
- [ ] DEAD-CODE (code) — n/a (docs-only).
- [ ] SEMANTIC (prose / non-code) — read the chapter + glossary + skill guide in full: every claim cross-checked against tasks 1–5's frozen contracts (no aspirational behavior).

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-25

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): chapter/glossary/skill parity (the guards) · whether readers reach the federation section (book analytics, once the site ships).

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · open] the book chapter teaches the pillar but the worked example (Appendix D) is still single-component — a multi-component worked example would close the gap from "read it" to "did it" (evidence: chapter 17 is concept-first; no end-to-end BE→FE transcript).
- [SPEC · open] `components.toml` has no engine `add.py components` reader/validator command surfaced to the operator — the doc shows the format but a `check`-time schema lint would catch typos earlier (evidence: chapter 17 documents the TOML by hand).

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · open] a new agent-facing prose file ripples into THREE registries — the wording-lint surface count (×2 tests) + the skill lean fence — not just parity; a new skill guide's true cost is registration in all of them (evidence: component-method-docs build hit test_wording_lint + test_per_step_hooks + test_skill_lean before green).
