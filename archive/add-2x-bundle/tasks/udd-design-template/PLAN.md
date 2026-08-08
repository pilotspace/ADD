# TASK: DESIGN.md template binding prose + tokens + catalog + prototypes into 0-setup, with the render recipe

slug: udd-design-template · created: 2026-06-13 · stage: mvp
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
  - `add-method/tooling/add.py:SETUP_FILES` (L83) — the hardcoded tuple `("PROJECT.md","CONVENTIONS.md",
    "GLOSSARY.md","MODEL_REGISTRY.md","dependencies.allowlist")` that `cmd_init` (L365) walks (L377–389),
    rendering each via `_render_template` → `.add/<name>` (skip-not-clobber if it exists). Adding `"DESIGN.md"`
    here is the ENGINE wiring (the testable artifact) — ×3 add.py mirrors stay byte-identical + engine-pin re-aim.
  - `add-method/tooling/add.py:_render_template` (L152) / `_templates_dir` (L148) — loads `templates/<name>.tmpl`,
    substitutes `{{date}}`/`{{project}}`/`{{stage}}` (the call at L381); a blank render is warn-skipped (so the
    template must render non-blank). The new `templates/DESIGN.md.tmpl` rides this path.
  - `add-method/skill/add/phases/0-setup.md` (L54 "Draft to the lock" living-docs list) — names PROJECT.md ·
    CONVENTIONS · GLOSSARY · MODEL_REGISTRY · dependencies.allowlist; NO DESIGN.md today. A step naming
    DESIGN.md as the UI-project design doc is the "wired into 0-setup" prose half (skill ×3 mirrors).
Context (working folder):
  - `add-method/tooling/templates/PROJECT.md.tmpl` (L31 `## Users (UDD) — UI/UX: design before code`; L40
    `Design source of truth → DESIGN.md`) — the foundation already POINTS to DESIGN.md as the destination;
    DESIGN.md is the anticipated truth doc, not a duplicate of PROJECT.md's cross-cutting UX stance.
  - `add-method/tooling/templates/udd-tokens.md` (task 1) · `udd-catalog.md` (task 2; the render recipe lives in
    its `## Render recipe` section ~L87) · `tokens.sample.json` · `catalog.sample.json` · `prototype.sample.json`
    — the shipped foundation DESIGN.md binds prose to (the named set tokens.json · catalog.json · prototypes/).
Honors (patterns / conventions):
  - the SETUP_FILES idiom: a foundation file = a `templates/<name>.tmpl` rendered to `.add/<name>` at init;
    skip-not-clobber; `{{project}}`/`{{stage}}`/`{{date}}` substitution; the template must be non-blank.
  - the milestone shared decisions: DESIGN.md binds prose + the named-set foundation + the render recipe; identity
    VALUES stay human-owned (the udd-tokens.md / 1-specify.md guideline — DESIGN.md prompts, never pre-fills brand).
  - the ×3-mirror + parity idiom: a template needs canonical + bundle mirrors (`test_bundle_parity` asserts the
    template SET + byte-identical); a `0-setup.md` edit needs skill ×3 (`test_tree_parity` canonical↔dogfood +
    `test_bundle_parity` canonical↔bundle); `test_add.py::test_init_creates_state_and_setup_files` iterates
    SETUP_FILES so `DESIGN.md` auto-extends it; the engine change re-aims engine_pin (carry udd-catalog-content-schema).
Anchors the contract cites: `SETUP_FILES` + the appended `"DESIGN.md"` (the engine wiring) · `templates/DESIGN.md.tmpl` (NEW, rendered via `_render_template` with `{{project}}`/`{{stage}}`/`{{date}}` → `.add/DESIGN.md`) · the DESIGN.md SECTIONS (design prose + the named-set foundation pointers tokens.json/catalog.json/prototypes/ + the render-recipe pointer to udd-catalog.md + the human-owned identity stance) · the `phases/0-setup.md` DESIGN.md step · `cmd_init` (the render+write loop, L377–389) · `test_bundle_parity`/`test_tree_parity`/`test_add.py::test_init_creates_state_and_setup_files` (the guards) · engine_pin re-aim.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: a DESIGN.md template wired into 0-setup — `add.py init` drafts `.add/DESIGN.md` from
`templates/DESIGN.md.tmpl`, a STRUCTURED BINDING doc: human-owned design identity + principles + pointers
binding the named-set foundation (tokens · catalog · prototypes) + the render recipe. The milestone's UDD
foundation now has a prose front-door the AI drafts UI from, alongside the JSON the validators lint.

Framings weighed: template + engine-wired-into-setup (chosen) · template-only doc · full design-system generator.
  - CHOSEN template + engine-wired: ship `DESIGN.md.tmpl` AND append `"DESIGN.md"` to `SETUP_FILES` so a fresh
    init drafts it — the milestone's "wired into the 0-setup foundation flow". A red→green: init must draft it.
  - template-only: ship the template but don't wire it into init. Rejected — fails the milestone exit criterion
    ("0-setup drafts DESIGN.md from the template") and leaves no testable behavior change.
  - full design-system generator: emit tokens/catalog/prototypes too. Rejected (Fork B) — scope creep beyond
    this task's named exit; the AI adapts the shipped samples instead.

Must:
<must>
  - WIRE: append `"DESIGN.md"` to `SETUP_FILES` (add.py L83) — UNCONDITIONAL (Fork C), so `cmd_init` renders +
    writes `.add/DESIGN.md` via the existing L377–389 loop (skip-not-clobber). ×3 add.py mirrors + engine-pin re-aim.
  - TEMPLATE: ship `templates/DESIGN.md.tmpl` (canonical + bundle mirror), rendered by `_render_template` with
    `{{project}}`/`{{stage}}`/`{{date}}`; MUST render non-blank (else init warn-skips it).
  - SECTIONS (Fork A — structured binding doc), in order:
      · a header (`{{project}}` · `{{stage}}` · `{{date}}`) + a one-line "what this doc is" + a "no UI? this
        doc is optional — delete it" self-note (Fork C unconditional).
      · IDENTITY — brand color · palette · typeface — as PROMPTED placeholders (HTML-comment prompts), with NO
        concrete value pre-filled (the identity-values guideline: design identity is human-owned, set at specify).
      · PRINCIPLES / persona — the design intent prose the AI drafts UI against.
      · SCREENS & flows — a prompted index of the app's `prototypes/<name>.json` by screen name, SEEDED with the
        shipped `prototype.sample.json` as the one worked row; the AI adds rows as screens are designed.
      · FOUNDATION — pointers binding the NAMED SET: `tokens.json` (+ `udd-tokens.md`) · `catalog.json`
        (+ `udd-catalog.md`) · `prototypes/<name>.json`; STARTING from the shipped samples (Fork B — point to
        `tokens.sample.json` · `catalog.sample.json` · `prototype.sample.json`, which the AI adapts).
      · RENDER — a pointer to the render recipe (`udd-catalog.md` `## Render recipe`).
  - SETUP PROSE: add a DESIGN.md line to `phases/0-setup.md` "Draft to the lock" living-docs list (skill ×3
    mirrors) — naming DESIGN.md as the UI-project design doc setup drafts.
  - PARITY: template canonical+bundle byte-identical (`test_bundle_parity` template SET); skill 0-setup.md ×3
    (`test_tree_parity` + `test_bundle_parity`); add.py ×3; `test_init_creates_state_and_setup_files` auto-covers DESIGN.md.
</must>
Reject:
<reject>
  - `DESIGN.md` ∉ `SETUP_FILES` (init does not draft `.add/DESIGN.md`) -> "design_not_wired"
  - `DESIGN.md.tmpl` renders blank / missing (init warn-skips it) -> "design_template_blank"
  - the template SHIPS a concrete identity VALUE (e.g. a literal brand hex) instead of a human-owned prompt -> "identity_prefilled"
  - a required SECTION (identity · principles · screens · foundation pointers · render recipe) is absent from the drafted doc -> "design_section_missing"
  - the template / skill mirrors are not byte-identical across the ×3/×2 mirror set -> "mirror_drift"
</reject>
After:
<after>
  - a fresh `add.py init` writes a NON-BLANK `.add/DESIGN.md` carrying identity (prompted) · principles ·
    screens index · foundation pointers · render recipe; substitutions resolved.
  - `DESIGN.md` ∈ `SETUP_FILES`; `phases/0-setup.md` names it; ×3/×2 mirrors byte-identical; engine re-pinned.
  - NO concrete identity value is shipped — the identity section prompts, never pre-fills.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ DESIGN.md SECTION SET (Fork A) — the structured-binding sections (identity · principles · screens · foundation
    pointers · render recipe). Lowest-confidence because it is a DESIGN-doc shape the human owns, and
    udd-check-lint (task 4) does NOT lint DESIGN.md prose, so nothing downstream enforces it — if the sections
    are wrong, rewrite the template (CONTAINED: template-only, no engine/validator change). The freeze pins the
    section set so the doc is coherent, not arbitrary.
  - [ ] FOUNDATION POINTERS (Fork B) — DESIGN.md points to the SAMPLES (tokens.sample.json etc.) as the start,
    not scaffolded JSON. If wrong: add JSON scaffolding to setup later (additive engine change).
  - [ ] UNCONDITIONAL WIRING (Fork C) — `DESIGN.md` drafted on EVERY init; the template self-notes "no UI? optional".
    If wrong: gate cmd_init on a UI flag (additive engine change).
  - [ ] ENGINE DELTA is ONLY `SETUP_FILES += "DESIGN.md"` — no other cmd_init logic changes (the L377–389 loop is
    generic). Low risk (mirrors how every existing SETUP_FILES entry works).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: init drafts a non-blank DESIGN.md (the exit criterion)
  Given a fresh project directory with no .add/
  When add.py init runs
  Then .add/DESIGN.md exists and is non-blank, with {{project}}/{{stage}}/{{date}} substituted

Scenario: DESIGN.md is registered as a setup file
  Given the engine module
  When SETUP_FILES is read
  Then "DESIGN.md" is a member

Scenario: the drafted DESIGN.md carries every required section
  Given the rendered DESIGN.md
  When its headings are read
  Then identity, principles, screens, foundation (tokens/catalog/prototypes pointers), and render-recipe sections are all present

Scenario: the screens section indexes the prototypes by name
  Given the rendered DESIGN.md screens section
  When its rows are read
  Then it names prototypes/<name>.json by screen and seeds with the shipped prototype.sample.json as the one worked row

Scenario: the identity section prompts, never pre-fills (human-owned)
  Given the DESIGN.md.tmpl identity section
  When its brand/palette/type fields are read
  Then each is an empty PROMPTED placeholder (HTML-comment), with no concrete value

Scenario: the foundation section points to the named-set samples
  Given the rendered DESIGN.md foundation section
  When its pointers are read
  Then it names tokens.json/catalog.json/prototypes/ and the shipped samples + udd-tokens.md/udd-catalog.md

Scenario: 0-setup names DESIGN.md as a living doc to draft
  Given phases/0-setup.md
  When the "Draft to the lock" list is read
  Then DESIGN.md is named there

Scenario: DESIGN.md missing from SETUP_FILES is rejected
  Given a build that ships DESIGN.md.tmpl but does NOT add "DESIGN.md" to SETUP_FILES
  When the suite runs
  Then a "design_not_wired" failure is raised (init drafts no .add/DESIGN.md)
  And the other SETUP_FILES are still drafted unchanged

Scenario: a blank DESIGN.md template is rejected
  Given a DESIGN.md.tmpl that renders empty
  When add.py init runs
  Then a "design_template_blank" failure is raised (init warn-skips it, no .add/DESIGN.md)
  And no other setup file is affected

Scenario: a pre-filled identity value is rejected
  Given a DESIGN.md.tmpl whose identity section ships a concrete brand hex
  When the suite runs
  Then an "identity_prefilled" failure is raised
  And the prompted (empty) form is what passes — the guideline holds unchanged

Scenario: a missing required section is rejected
  Given a DESIGN.md.tmpl lacking the foundation (or render) section
  When the suite runs
  Then a "design_section_missing" failure is raised
  And a template with all sections passes unchanged

Scenario: mirror drift is rejected
  Given the DESIGN.md.tmpl (or 0-setup.md) mirrors are not byte-identical
  When test_bundle_parity / test_tree_parity run
  Then a "mirror_drift" failure is raised
  And byte-identical mirrors report no violation
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
ENGINE WIRING (the testable behavior change):
  SETUP_FILES (add.py ~L83) gains one member, "DESIGN.md", appended LAST — UNCONDITIONAL (Fork C).
  No other cmd_init logic changes: the existing L377–389 render+write loop walks it like every entry —
  _render_template("DESIGN.md", date=, project=, stage=) → .add/DESIGN.md (skip-not-clobber; blank → warn-skip).
  ×3 add.py mirrors byte-identical (canonical · _bundled · dogfood); engine_pin re-aimed (carry udd-catalog-content-schema).

TEMPLATE  templates/DESIGN.md.tmpl  (NEW; canonical + bundle mirror, byte-identical):
  Renders NON-BLANK with {{project}}/{{stage}}/{{date}} substituted. A STRUCTURED BINDING doc (Fork A) —
  SIX required sections, machine-detected by these H2 heading anchors, in this order:
    1. header        a title line carrying {{project}} · {{stage}} · {{date}} + a one-line "what this doc is"
                     + a "No UI in this project? This doc is optional — delete it." self-note (Fork C).
    2. "## Identity"   brand color · palette · typeface as HTML-comment PROMPTS (`<!-- … -->`) ONLY —
                     NO concrete value pre-filled (the identity-values-human-owned guideline; set at specify).
    3. "## Principles"  the design intent / persona prose the AI drafts UI against (prompted, may be empty-bodied).
    4. "## Screens"     a prompted index of the app's prototypes/<name>.json by screen name, SEEDED with the shipped
                       prototype.sample.json as the one worked row; the AI adds rows as screens are designed.
    5. "## Foundation"  pointers binding the NAMED SET, each naming its file + its doc + its shipped sample:
                       tokens.json (udd-tokens.md · tokens.sample.json) · catalog.json (udd-catalog.md ·
                       catalog.sample.json) · prototypes/<name>.json (prototype.sample.json) — START from the
                       samples (Fork B), which the AI adapts; no JSON scaffolded by the engine.
    6. "## Render"      a pointer to the render recipe (udd-catalog.md "## Render recipe" — catalog.json → defineCatalog).

  codes  (the DESIGN.md named reds; the new red suite asserts each; udd-check-lint does NOT lint DESIGN.md prose):
    "design_not_wired"        "DESIGN.md" ∉ SETUP_FILES — a fresh init drafts no .add/DESIGN.md
                              (and the OTHER setup files are still drafted unchanged)
    "design_template_blank"   DESIGN.md.tmpl missing OR renders empty/whitespace — init warn-skips it
    "identity_prefilled"      the Identity section ships a concrete value (a /#[0-9A-Fa-f]{6}/ hex, or a
                              non-comment brand/type literal) instead of an HTML-comment prompt
    "design_section_missing"  any of the six heading anchors (header · Identity · Principles · Screens ·
                              Foundation · Render) is absent from the rendered doc
    "mirror_drift"            DESIGN.md.tmpl (canonical↔bundle) or 0-setup.md (canonical↔bundle↔dogfood) not byte-identical

SETUP PROSE  phases/0-setup.md (skill ×3 mirrors): the "Draft to the lock" living-docs list gains a DESIGN.md
  line — naming DESIGN.md as the UI-project design doc setup drafts. Byte-identical across canonical · bundle · dogfood.

PARITY GUARDS (existing, auto-extending — no guard logic written this task):
  test_bundle_parity  — asserts the template SET equality + byte-identical (DESIGN.md.tmpl auto-joins the set) +
                        the skill-tree set (0-setup.md).
  test_tree_parity    — canonical↔dogfood skill trees (0-setup.md).
  test_add.py::test_init_creates_state_and_setup_files — iterates SETUP_FILES dynamically → auto-covers DESIGN.md.

BOUNDARY (the forks frozen here):
  Fork A — DESIGN.md is a STRUCTURED BINDING doc (the six-section set above), not a free-form note nor a generator.
  Fork B — Foundation POINTS to the shipped samples as the start; no tokens/catalog/prototypes JSON is scaffolded.
  Fork C — wiring is UNCONDITIONAL (every init drafts DESIGN.md); the self-note tells a non-UI project to delete it.
  ENGINE DELTA is ONLY SETUP_FILES += "DESIGN.md" — the render+write loop is generic and untouched.

Files touched (→ §5 scope): add.py (+2 mirrors) SETUP_FILES += "DESIGN.md" · templates/DESIGN.md.tmpl
  (+1 bundle mirror) NEW · skill phases/0-setup.md (+2 mirrors) the living-docs line · engine_pin.py re-aim
  (canonical-only) · test_udd_design_template.py (NEW red suite, this task dir).
```

Least-sure flag surfaced at freeze: [contract] FORK A — the DESIGN.md SECTION SET (the six heading
  anchors header · Identity · Principles · Screens · Foundation · Render). Lowest-confidence because it is a design-doc
  shape the human owns and NOTHING downstream enforces it (udd-check-lint task 4 does not lint DESIGN.md prose) —
  if the set is wrong, the fix is template-only (rewrite DESIGN.md.tmpl; no engine/validator change). The freeze
  pins it so the drafted doc is coherent, not arbitrary.

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-13.
  v1 (the freeze approval, "Freeze + Screens section"): the human added a SIXTH section to the Fork-A set —
  "## Screens" (a prompted index of prototypes/<name>.json by screen name, SEEDED with the shipped
  prototype.sample.json as the one worked row), placed after Principles, before Foundation. §1 Must/Reject/
  After/Assumptions + §2 scenarios (incl. a new "screens section indexes the prototypes" scenario) + §3
  template section list + design_section_missing anchors + the Fork-A flag amended to match before the stamp.
  All other terms (the SETUP_FILES wiring · the 5 reject codes · the parity guards · Forks B/C) unchanged.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 90% (the DESIGN.md.tmpl render + the SETUP_FILES wiring + the 0-setup line)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_init_drafts_nonblank_design: init in a temp dir / assert .add/DESIGN.md exists, non-blank, {{}}-free, project substituted (the exit criterion)
  - test_design_is_a_setup_file: assert "DESIGN.md" ∈ add.SETUP_FILES (design_not_wired, positive form)
  - test_other_setup_files_still_drafted: init / assert PROJECT/CONVENTIONS/GLOSSARY/MODEL_REGISTRY still drafted (wiring is additive)
  - test_template_renders_nonblank_substituted: _render_template("DESIGN.md",…) non-blank, no raw {{token}}, header carries the subs (design_template_blank)
  - test_all_required_sections_present: render / assert the header self-note + the five H2 anchors Identity·Principles·Screens·Foundation·Render (design_section_missing)
  - test_identity_section_prompts_not_prefilled: Identity block has `<!--` prompts + NO `#RRGGBB` hex outside a comment (identity_prefilled)
  - test_screens_section_indexes_prototypes: Screens block names prototypes/ + seeds with prototype.sample.json
  - test_foundation_points_to_named_set_samples: Foundation block names tokens/catalog/prototypes + the 3 samples + udd-tokens.md/udd-catalog.md
  - test_render_section_points_to_recipe: Render block points to udd-catalog.md + names "Render recipe"
  - test_0setup_names_design_md: canonical phases/0-setup.md names DESIGN.md as a living doc to draft
  - test_design_template_mirrored: DESIGN.md.tmpl byte-identical canonical↔bundle (+ dogfood copy) (mirror_drift)
  - test_0setup_mirrored: phases/0-setup.md byte-identical across the ×3 skill mirrors (mirror_drift)
  - test_pin_annotation_names_this_task: engine_pin records "re-aimed @ udd-design-template" + carries "udd-catalog-content-schema"
</test_plan>

Tests live in: `add-method/tooling/test_udd_design_template.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `.add/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/templates/DESIGN.md.tmpl` `add-method/src/add_method/_bundled/tooling/templates/DESIGN.md.tmpl` `.add/tooling/templates/DESIGN.md.tmpl` `add-method/skill/add/phases/0-setup.md` `add-method/src/add_method/_bundled/skill/add/phases/0-setup.md` `.claude/skills/add/phases/0-setup.md` `add-method/tooling/test_udd_design_template.py`
Strategy (ordered batches): 1. red suite + a worked render fixture (render DESIGN.md.tmpl, assert the five anchors + the identity-prompt + the foundation pointers) → red for the right reason. 2. ship `templates/DESIGN.md.tmpl` (canonical) + append `"DESIGN.md"` to SETUP_FILES (canonical add.py) → canonical init drafts a non-blank DESIGN.md, green. 3. mirror add.py ×2 + DESIGN.md.tmpl ×2 (bundle + dogfood) + 0-setup.md ×3 living-docs line + re-pin engine_pin.py (`re-aimed @ udd-design-template`, carry `udd-catalog-content-schema`) → parity green. 4. pin self-test green.
Safety rule (feature-specific): the engine delta is ONLY `SETUP_FILES += "DESIGN.md"` — do NOT touch the generic L377–389 render+write loop; the template ships NO concrete identity value (HTML-comment prompts only); a blank render is a fail (warn-skip), so the template must render non-blank.
Code lives in: `add-method/tooling/` (the engine + templates) + the skill ×3 + the new red suite.
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full tooling suite 978 OK on python3.14 + python3.10; new test_udd_design_template.py 13/13; add.py check 305/0.
- [x] coverage did not decrease — +13 tests (render + wiring + prose + parity + pin), all green.
- [x] no test or contract was altered during BUILD — the build changed zero tests, zero contract. (The test
      STRENGTHENING below happened at VERIFY in response to the refute, routed honestly back through the tests phase —
      `phase tests` → re-advance → re-snapshot — NOT slipped in during build; the build_tampered tripwire fired on
      the first gate attempt and was cleared by re-baselining, never by forcing the gate. §3 untouched.)
- [x] the green was EARNED — adversarial refute-read ran (python-expert subagent, autonomy=auto). Verdict: REFUTED on
      TEST-STRENGTH grounds only — NO confirmed cheat, NO vacuous/overfit assert, NO security finding. Four gaps disclosed
      (identity OR-half · section order · screens-table · self-note-in-comment); ALL FOUR closed before the gate
      (close-gap-before-gate), each strengthened assert proven non-vacuous against the refute's own counterexample.
- [x] concurrency / timing — N/A: a static template + a single SETUP_FILES tuple member; no concurrency, no shared state.
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only; the template is static prose
      written via the existing _atomic_write path; no new dependency; no secret. The identity section ships NO concrete
      brand value (prompts only) — the human-owned-identity guideline holds.
- [x] layering & dependencies follow CONVENTIONS.md — the engine delta is one tuple member on the generic render loop;
      no new layer, no import added.
- [x] a person reviewed — auto-gated on evidence under autonomy=auto; surfaced to Tin Dang (the refute + the four closes).

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — the new SETUP_FILES member `"DESIGN.md"` IS referenced: cmd_init iterates SETUP_FILES (L377–389)
      and renders+writes it; test_init_drafts_nonblank_design confirms `.add/DESIGN.md` lands on disk, non-blank.
- [x] DEAD-CODE (code) — no new symbol introduced (a tuple member + a template file + a prose line); nothing orphaned.
- [x] SEMANTIC (prose / non-code) — DESIGN.md.tmpl read IN FULL by the refute: six sections present + in contracted
      order (header·Identity·Principles·Screens·Foundation·Render); identity is HTML-comment prompts with no pre-filled
      value; foundation points to the named-set samples + docs; render points to udd-catalog.md's `## Render recipe`;
      0-setup.md names DESIGN.md in the "Draft to the lock" list. All mirrors byte-identical (diff-confirmed).

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang (auto-gated under autonomy=auto; refute ran + 4 gaps closed + re-probed) · date: 2026-06-13

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): a fresh `add.py init` on a UI project drafts a non-blank `.add/DESIGN.md`
  carrying the six sections (the exit criterion as a live monitor); the identity section never ships a concrete value.
Spec delta for the next loop: udd-check-lint (task 4) lints the JSON named set (tokens·catalog·prototypes) but
  NOT DESIGN.md prose — the prose contract is test-guarded only; if drift becomes a problem, a `cmd_check` DESIGN.md
  section-presence lint is the additive next step.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
  - [UDD · folded] DESIGN.md is the prose FRONT-DOOR that binds the named-set JSON (tokens·catalog·prototypes) the AI
    drafts UI from; design identity stays human-owned — the doc PROMPTS for brand/palette/type, never pre-fills (evidence:
    the shipped DESIGN.md.tmpl identity section is HTML-comment prompts + the identity_prefilled guard, both halves).
  - [UDD · folded] the human added a SCREENS section at the freeze ("Freeze + Screens section") — DESIGN.md doubles as the
    per-screen prototypes/<name>.json index, a shape worth defaulting into the template (evidence: the v1 §3 amendment).
  - [TDD · folded] string-PRESENCE asserts under-enforce a STRUCTURED-PROSE contract — `assertIn(anchor)` misses order, table
    form, and the OR-half of identity_prefilled (a non-hex literal); a prose contract needs STRUCTURE asserts (evidence: the
    verify refute found 4 such gaps a presence check passed; the 4 strengthened asserts each catch their counterexample).
  - [ADD · folded] strengthening a test at VERIFY (close-gap-before-gate) trips build_tampered — the honest path is reopen
    → tests → re-advance (re-snapshot), NEVER force the gate past the tripwire (evidence: build_tampered fired on the first
    `gate PASS` attempt; cleared by `phase tests` + re-advance, not by overriding — the §3 contract stayed untouched).
