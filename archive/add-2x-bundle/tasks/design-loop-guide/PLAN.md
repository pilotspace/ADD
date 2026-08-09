# TASK: Author design.md — the design-definition loop

slug: design-loop-guide · created: 2026-06-15 · stage: mvp · risk: high
autonomy: conservative   <!-- LOWERED from the project `auto` default: this task is method-defining scope (it defines a new UDD facet — the design-definition loop), which the high-risk guard (run.md) requires be gated; the run does all the work and converges but STOPS at verify for a human gate. -->
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
- `add-method/skill/add/design.md` (canonical · NEW — absent in all 3 trees) + mirrors `add-method/src/add_method/_bundled/skill/add/design.md` + `.claude/skills/add/design.md` — the design-definition loop guide; ×3 skill trees, byte-identical (test_bundle_parity).
- `add-method/skill/add/SKILL.md` — "## Beyond the bundle — load on demand" para: design.md joins advisor.md/confidence.md/run.md/streams.md as a loadable guide.
- `add-method/skill/add/phases/0-setup.md:76-77` — the `DESIGN.md` scaffold line (UI projects) — add a THIN pointer to design.md.
- `add-method/skill/add/phases/1-specify.md:18-21,71` — the "Identity is direction (UDD)" note + "UI feature? sketch flows + every screen" line — add a THIN pointer to design.md's loop.
- read-only contracts the loop BINDS (does not change): `add-method/tooling/templates/udd-tokens.md` (compact-DTCG token dialect) + `udd-catalog.md` (catalog `_catalog_tree_violations` + content-tree `Spec` + render recipe).
- shape/voice model for a thin on-demand engine doc: `add-method/skill/add/advisor.md` + `confidence.md`.

Context (working folder):
- `add-method/tooling/test_xml_convention.py:193` `ENGINE_FILES` dict — a new engine guide needs an entry (tags + narrative section headers); adding design.md trips it (`new-engine-doc-trips-inventory-guards`).
- `add-method/tooling/test_wording_lint.py:169` — the `skill/add` surface count ("25 files" → 26 with design.md).
- `add-method/tooling/test_per_step_hooks.py:55` — guard that a step names advisor.md via `_MARKER`; the model if design.md becomes a per-step hook on setup/specify.
- book homes (the `book-glossary-align` task fills these, not this one): `add-method/docs/03-step-1-specify.md` · `docs/14-foundation.md` (UDD §) · `.add/GLOSSARY.md` (the 4 new terms).

Honors (patterns / conventions):
- `capability-as-prose-recommendation-engine-tool-agnostic` — render/capture is a RECOMMENDED recipe; the engine never renders.
- `build-in-build + thin-pointer` — the loop body lives in design.md; setup/specify carry THIN pointers, never the loop.
- `new-engine-doc-trips-inventory-guards` + `enumerate-full-set + distinctness` — update ENGINE_FILES + the wording-lint surface count + parity when adding design.md.
- v16 XML convention (closed 5 BLOCK-level tags; skeleton labels stay plain) · leanness as a dual-audience UX constraint (the guide reads for BOTH agent + human).
- identity values human-owned (UDD) — the loop surfaces tokens, never auto-picks · four-tree byte-identical (test_bundle_parity).

Anchors the contract cites: `design.md` (×3 trees, the deliverable) · the `SKILL.md` on-demand-list entry · the thin pointers in `phases/0-setup.md` + `phases/1-specify.md` · `test_xml_convention.py` `ENGINE_FILES` entry · `test_wording_lint.py` surface count.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: design.md — the design-definition loop (DDD→UDD): an on-demand guide that takes a UI feature from the domain to a human-confirmed captured screen BEFORE build.
Framings weighed: on-demand `design.md` guide + thin pointers from setup/specify (chosen, human-confirmed) · a new gated `design` phase · fold inline into specify.
Must:
<must>
  - design.md defines the loop as FOUR ordered, named beats: (1) review-domain · (2) research-components · (3) wireframe · (4) render-capture-confirm.
  - beat 1 (review-domain) starts from the DOMAIN: read the domain model (entities · flows · ubiquitous language) → derive the screens + per-screen regions; map entities to *presentational* components (DDD→UDD bridge).
  - beat 2 (research-components) is REUSE-BEFORE-INVENT: check `catalog.json` FIRST and reuse; research (websearch reference UIs / pattern galleries) and propose a NEW component only for a genuine domain gap, with a cited reference.
  - beat 3 (wireframe) produces a LOW-FI structural layout (regions + component slots, pre-styling) — the "expected layout" the human aligns on cheaply before any styling.
  - beat 4 (render-capture-confirm) renders a self-contained HTML mock (component lib via CDN + `tokens.json`→CSS vars + the reusable per-component kit + mock data), captures a REAL image, and presents it for design-confirm (show-before-ask) BEFORE build; the confirmed layout records back to `prototypes/<name>.json` + `catalog.json`.
  - the engine stays TOOL-AGNOSTIC: capture is a RECOMMENDED recipe + a named default; the captured image is a design-confirm EVIDENCE artifact, never an engine output (the engine never renders).
  - discoverability: design.md is referenced by a THIN pointer from `phases/0-setup.md` + `phases/1-specify.md`, listed in `SKILL.md`'s on-demand guides, and added to `test_xml_convention.py` `ENGINE_FILES`; shipped ×3 trees byte-identical; the wording-lint surface count goes 25→26.
  - the loop BINDS the existing UDD contracts (`tokens.json` · `catalog.json` · `prototypes/<name>.json`) read-only — it never alters the frozen `prototypes/<name>.json` data shape, and identity values stay human-owned.
</must>
Reject:
<reject>
  - the guide directs the ENGINE to render or capture (not tool-agnostic) -> "engine_renders"
  - the four beats are missing one or are out of the named order -> "loop_beats_unordered"
  - beat 2 proposes a new component without first checking the catalog -> "invent_before_reuse"
  - design-confirm is placed AT or AFTER build instead of before -> "confirm_after_build"
  - the guide alters the `prototypes/<name>.json` data contract (vs. binding it) -> "data_contract_changed"
  - the guide auto-picks an identity value (brand color · palette · type) -> "identity_autopicked"
</reject>
After:
<after>
  - design.md exists ×3 trees (byte-identical), defines the 4-beat loop, and is discoverable from setup + specify + SKILL.md + ENGINE_FILES; the existing UDD contracts are unchanged; a UI project can follow the loop from domain → a human-confirmed captured layout before build.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [contract] the FOUR-beat decomposition + its boundaries — lowest confidence because "review-domain" risks overlapping specify's own domain analysis, and "wireframe" (beat 3) vs "render-capture" (beat 4) could collapse into one beat or split into three; if wrong: the freeze-first loop contract is mis-shaped and every downstream task (mock recipe · capture · book) reworks against the wrong beats.
  - [ ] [contract] tool-agnostic stance (engine never renders; capture = recommended recipe + named default) — medium confidence: you said "capture via HTML/websearch", which I read as a recommended recipe, not a bundled engine feature; if wrong: the method would need a prescribed/bundled renderer, contradicting its identity.
  - [ ] [spec] design.md as a THIN pointer from setup/specify vs. a first-class per-step HOOK (like advisor/confidence under `test_per_step_hooks`) — if wrong: the guide is either less discoverable, or over-coupled to the hook guard.
  - [x] reuse-before-invent via `catalog.json` is the consistency mechanism (human-confirmed).
  - [x] new-major milestone + on-demand `design.md` placement (human-confirmed).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the loop is four ordered, named beats          # Must 1
  Given the shipped design.md guide
  When a reader reads its loop section
  Then it names exactly four beats in order: review-domain → research-components → wireframe → render-capture-confirm

Scenario: beat 1 starts from the domain                  # Must 2
  Given design.md beat 1 (review-domain)
  When an agent applies it to a UI feature
  Then it derives the screens + per-screen regions from the domain model and maps entities to presentational components

Scenario: beat 2 reuses before inventing                 # Must 3
  Given a catalog.json that already declares a needed component
  When an agent runs beat 2 (research-components)
  Then it reuses the existing catalog component, proposing a NEW one only for a genuine gap with a cited reference

Scenario: beat 3 yields a low-fi wireframe               # Must 4
  Given design.md beat 3 (wireframe)
  When an agent applies it
  Then it produces a structural, pre-styling layout (regions + component slots) the human aligns on before styling

Scenario: beat 4 confirms a real captured image before build   # Must 5
  Given design.md beat 4 (render-capture-confirm)
  When an agent applies it
  Then it renders a self-contained HTML mock (lib via CDN + tokens.json→CSS vars + per-component kit + mock data), captures a real image, presents it for design-confirm, and records the confirmed layout back to prototypes/<name>.json + catalog.json

Scenario: the engine never renders                       # Must 6 / Reject engine_renders
  Given design.md's capture guidance
  When a reader checks who renders
  Then capture is a recommended recipe + named default run by the agent's own tools, and the captured image is design-confirm evidence
  And the guide never directs the engine to render or capture          # else "engine_renders"

Scenario: design.md is discoverable across the surface   # Must 7
  Given the shipped ×3 trees
  When the inventory + seams are checked
  Then design.md is referenced from phases/0-setup.md + phases/1-specify.md, listed in SKILL.md on-demand guides, present in test_xml_convention ENGINE_FILES, byte-identical across the 3 trees, and the wording-lint surface count is 26

Scenario: the loop binds existing contracts unchanged    # Must 8 / Reject data_contract_changed
  Given the frozen prototypes/<name>.json data contract
  When the guide ships
  Then the guide binds tokens.json · catalog.json · prototypes/<name>.json read-only
  And the prototypes/<name>.json data shape is unchanged                # else "data_contract_changed"

Scenario: a missing or reordered beat is rejected        # Reject loop_beats_unordered
  Given a draft design.md missing a beat or with beats out of order
  When the guide-shape test runs
  Then it fails with "loop_beats_unordered"
  And the shipped guide keeps the four beats in order

Scenario: inventing before reuse is rejected             # Reject invent_before_reuse
  Given beat 2 guidance that proposes a new component without checking the catalog
  When the guide-shape test runs
  Then it fails with "invent_before_reuse"
  And beat 2 keeps reuse-before-invent

Scenario: confirming at/after build is rejected          # Reject confirm_after_build
  Given guidance that places design-confirm at or after build
  When the guide-shape test runs
  Then it fails with "confirm_after_build"
  And the loop keeps design-confirm before build

Scenario: auto-picking an identity value is rejected     # Reject identity_autopicked
  Given guidance that auto-picks a brand color / palette / typeface
  When the guide-shape test runs
  Then it fails with "identity_autopicked"
  And identity values remain human-owned
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
GUIDE design.md   (canonical add-method/skill/add/design.md + 2 mirrors — byte-identical ×3 trees)

  loop beats (ordered, named):
    review-domain  →  research-components  →  wireframe  →  render-capture-confirm

  beat outputs:
    review-domain          -> screens + per-screen regions (derived from the domain); entities → presentational components
    research-components     -> per-screen component list mapped to catalog.json (REUSE-FIRST); a new component only for a gap, cited
    wireframe               -> low-fi structural layout per screen (regions + slots, pre-styling)
    render-capture-confirm  -> self-contained HTML mock (component lib via CDN + tokens.json→CSS vars + per-component kit + mock data)
                               -> real captured image = design-confirm EVIDENCE, shown to the human BEFORE build
                               -> confirmed layout recorded to prototypes/<name>.json + catalog.json

  stance:    engine-never-renders · capture = recommended recipe + named default · captured image = evidence (not engine output)
  binds:     tokens.json · catalog.json · prototypes/<name>.json   (read-only; data contract UNCHANGED)
  identity:  human-owned (surfaced for the human, never auto-picked)

  seams:
    - referenced (THIN pointer) from phases/0-setup.md + phases/1-specify.md
    - listed in SKILL.md "Beyond the bundle — load on demand"
    - entry in test_xml_convention.py ENGINE_FILES (tags + narrative headers)
    - wording-lint surface count 25 → 26
    - byte-identical across the 3 skill trees (test_bundle_parity)

  reds (named; asserted by test_design_loop_guide):
    engine_renders · loop_beats_unordered · invent_before_reuse · confirm_after_build · data_contract_changed · identity_autopicked

Schema (files touched):
  NEW:        skill/add/design.md            ×3 trees (canonical · _bundled · dogfood)
  NEW:        tooling/test_design_loop_guide.py    (the guide-shape test)
  EDIT:       skill/add/SKILL.md  ·  phases/0-setup.md  ·  phases/1-specify.md   ×3 trees (on-demand list + thin pointers)
  EDIT:       tooling/test_xml_convention.py (ENGINE_FILES)  ·  tooling/test_wording_lint.py (surface 25→26)
  UNCHANGED:  tokens.json / catalog.json / prototypes/<name>.json data contracts · udd-tokens.md / udd-catalog.md templates
```

Status: FROZEN @ v1 — approved by Tin Dang · 2026-06-15
Least-sure flag surfaced at freeze: ⚠ [contract] the 4-beat decomposition + boundaries (§1) — accepted with cost-if-wrong in view; [contract] tool-agnostic stance + [spec] thin-pointer-vs-hook also flagged. A change to this frozen shape = change request back to SPECIFY.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + every Reject has a guide-shape assertion (12 tests); behavior = the shipped guide's content + seams, NOT internals.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_guide_exists: design.md present in the canonical tree
  - test_loop_four_ordered_beats: the 4 beats appear in the frozen order (Must 1 / loop_beats_unordered)
  - test_beat1_starts_from_domain: beat 1 cites domain · screen · presentational (Must 2)
  - test_beat2_reuse_before_invent: beat 2 cites reuse · catalog · before (Must 3 / invent_before_reuse)
  - test_beat3_lowfi_wireframe: beat 3 cites wireframe + low-fi/structural (Must 4)
  - test_beat4_render_capture_confirm_before_build: beat 4 cites html · mock · capture · design-confirm · before build (Must 5 / confirm_after_build)
  - test_engine_is_tool_agnostic: states engine-never-renders + recommended/tool-agnostic + evidence (Must 6 / engine_renders)
  - test_binds_contracts_unchanged: binds tokens.json · catalog.json · prototypes/ read-only/unchanged (Must 8 / data_contract_changed)
  - test_identity_human_owned: identity stays human-owned (identity_autopicked)
  - test_discoverable_in_skill_on_demand: SKILL.md cross-refs design.md (Must 7)
  - test_discoverable_from_setup_and_specify: a thin pointer in both phase guides (Must 7)
  - test_design_in_wording_surface: design.md joins the linted surface — presence, not a magic count (Must 7)
</test_plan>

Tests live in: `add-method/tooling/test_design_loop_guide.py` · run RED (missing implementation) before Build — confirmed: 12/12 fail for the right reason (design.md absent).
Build-note (count correction, transparent): the wording-lint surface base is 26 (not the 25 the §3 annotation read); adding design.md → 27. The frozen SEAM is unchanged (design.md increments the surface guard by one + both `test_wording_lint:180` and `test_per_step_hooks:74` update 26→27); only the descriptive integer was off. Recorded as an OBSERVE delta, not a silent contract edit.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/` `add-method/src/add_method/_bundled/skill/add/` `.claude/skills/add/` `add-method/tooling/test_xml_convention.py` `add-method/tooling/test_wording_lint.py` `add-method/tooling/test_per_step_hooks.py`
Strategy (ordered batches): 1. write canonical `design.md` (the 4-beat guide). 2. wire canonical seams — SKILL.md on-demand list + thin pointers in phases/0-setup.md + phases/1-specify.md. 3. update inventory guards (EVOLUTION not weakening): ENGINE_FILES +design.md · wording-lint surface 26→27 · per-step-hooks count 26→27. 4. mirror design.md + the 3 edited skill files to `_bundled` + dogfood `.claude/` trees (byte-identical). 5. full suite green.
Safety rule (feature-specific): NEVER touch `add-method/tooling/test_design_loop_guide.py` (the red target under the tamper tripwire) or the frozen §3; the existing `prototypes/<name>.json` data contract stays unchanged (bind only).
Code lives in: `add-method/skill/add/design.md` (+ ×3-tree mirrors).
Constraints: do NOT change the red test or the contract; the guard-count edits are inventory evolution (a real new file), recorded transparently; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 1119 green (`python3 -m unittest discover`); target `test_design_loop_guide` 12/12 green (was 12 red).
- [x] coverage did not decrease — +12 new guide-shape tests; nothing removed.
- [~] no test or contract was altered during build — the RED target (`test_design_loop_guide.py`) and the FROZEN §3 are UNTOUCHED (tamper tripwire clean). I DID edit 3 inventory guards — `test_xml_convention.py` (+design.md ENGINE_FILES entry), `test_wording_lint.py` (surface 26→27), `test_per_step_hooks.py` (count 26→27). This is inventory EVOLUTION (a real new file joins the globbed surface + the engine-doc inventory), the `new-engine-doc-trips-inventory-guards` + `evolution-not-weakening-discriminator` convention — each still asserts an exact count/shape, the correct one for the new reality. ⚠ HUMAN: confirm you accept this as evolution, not weakening.
- [x] the green was EARNED, not gamed — assertions check substantive guide content (the 4 ordered beats, reuse/catalog, wireframe, capture+design-confirm+before-build, engine-never-renders+evidence, binds tokens/catalog/prototypes read-only, identity human-owned) — not vacuous tautologies; design.md is a real coherent guide, not strings special-cased to the tests. No independent refute-read spawned (prose task at a human gate; the human read IS the refute).
- [x] concurrency / timing — N/A: a markdown guide + stdlib-unittest inventory edits; no runtime concurrency.
- [x] no exposed secrets, injection openings, or unexpected dependencies — pure markdown + existing stdlib tests; zero new dependencies. No security finding.
- [x] layering & dependencies follow CONVENTIONS.md — on-demand-guide pattern (like advisor.md), XML 5-tag vocab (only `<constraints>` outside fences), thin-pointer seams, ×3-tree byte-identical parity.
- [x] a person reviewed and approved the change — Tin Dang, at the conservative + risk:high human gate (2026-06-16); guard edits accepted as inventory evolution.

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (prose-guide) — design.md is referenced from SKILL.md (on-demand para), `phases/0-setup.md` (DESIGN.md line), `phases/1-specify.md` (identity note), `test_xml_convention.py` ENGINE_FILES, and is globbed into `wording_lint.surface_files()` — no orphan; ×3 trees byte-identical (test_bundle_parity green).
- [x] DEAD-CODE — no orphaned content: every design.md section maps to a Must; no unused symbol introduced.
- [x] SEMANTIC (prose) — read design.md in FULL: it defines the 4 beats in the frozen order, the DDD→UDD bridge (entities→presentational), reuse-before-invent against `catalog.json`, the low-fi wireframe, render→capture→**design-confirm before build**, the tool-agnostic/engine-never-renders stance with the image as evidence, read-only binding of the UDD contracts, and identity staying human-owned. Confirms the §1 Musts + the frozen §3 shape. Honest residue: the loop ships built-for-downstream (ADD is CLI/no-UI), validated by shape-lint + the design.md content, not a live ADD screen.

### GATE RECORD
Outcome: PASS — human-gated (conservative · risk: high · method/trust-layer residue; the 3 inventory-guard edits accepted as evolution, not weakening; red target + frozen §3 untouched)
Reviewed by: Tin Dang · date: 2026-06-16

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): a downstream UI project's first design-loop run is the real monitor — does it reach a human-confirmed captured screen before build? (no live signal here — ADD is CLI/no-UI).
Spec delta for the next loop: design.md's beat 4 should also reference the captured image in the feature's TASK.md (human steering, post-ship) — coordinated into `capture-evidence` (task 3), which owns the capture convention and will reopen the guide to add it.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] §5 BUILD Scope must be declared BEFORE the tests→build crossing — the scope anchor captures `_declared_scope` at that advance, so a placeholder §5 frozen there makes every real touch read out-of-scope; the documented recovery is re-crossing tests→build (evidence: gate PASS flagged scope_violation on 15 files, cleared by `phase tests` + `advance` re-snapshot).
- [SDD · folded] a frozen-contract DESCRIPTIVE annotation can be wrong without the SEAM being wrong — §3 read "wording-lint surface 25→26" but the real base was 26 (→27); the binding seam (design.md increments the guard by one + both guards update) held, only the integer was off (evidence: test_wording_lint:180 + test_per_step_hooks:74 both asserted 26).
- [UDD · folded] design-confirm captures must be attached/mentioned in the feature's TASK.md, not only recorded to prototypes/catalog — the task record is where design consistency + traceability live (evidence: human steering "rendered images must attach or mention into Task.md for consistency design"); delivered by `capture-evidence` (task 3), reopening design.md beat 4.
- [ADD · folded] the method dogfooded its own guards on a method-defining task — risk:high forced the human gate, the scope-gate caught the late §5, the tamper-tripwire stayed clean across the re-cross (evidence: auto-PASS refused; scope_violation caught + healed; §3/red-test md5 unchanged).
- [UDD · folded] the loop ships built-for-downstream — ADD is CLI/no-UI, so it is validated by shape-lint + the design.md content, not a live ADD screen (evidence: no prototypes/ tree in this repo; same honest ceiling as udd-design-foundation).
