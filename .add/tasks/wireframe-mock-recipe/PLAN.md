# TASK: Wireframe Mock Recipe

slug: wireframe-mock-recipe · created: 2026-06-16 · stage: mvp · risk: high
autonomy: conservative   <!-- lowered from the project default (auto): method-defining scope (a new recommended UDD artifact + worked sample) whose verify is a human judgment — does the mock render the EXPECTED layout? The human owns the verify gate (run.md unguarded_high_risk_auto). -->
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
- `add-method/tooling/templates/udd-wireframe.md` (canonical · NEW) + mirror `add-method/src/add_method/_bundled/tooling/templates/udd-wireframe.md` — the wireframe format (Stage A) + self-contained HTML-mock recipe (Stage B: tokens→CSS vars · per-component kit · compose the prototype tree · mock data). Templates are byte-identical canonical↔_bundled (test_bundle_parity `test_templates_byte_identical`).
- NEW worked-sample set under `add-method/tooling/templates/` (+ _bundled mirror) — `wireframe.sample.txt` (low-fi structural) · `tokens.sample.css` (semantic tokens → CSS custom properties) · `kit.sample.css` (one class per catalog component) · `welcome.sample.html` + `settings.sample.html` (two screens, the 2nd REUSES ≥1 component; both link the shared kit + tokens so a token flip re-renders both).
- NEW test `add-method/tooling/test_wireframe_mock_recipe.py` (+ a `test_component_reuse` case).
- read-only BINDS (consumed, not reshaped): `templates/tokens.sample.json` (primitive·semantic·component) · `catalog.sample.json` (Screen·Card·Text·Button + typed props) · `prototype.sample.json` (root+elements content tree) · `udd-tokens.md` · `udd-catalog.md` (render recipe) · `skill/add/design.md` beats 3–4 (the loop this recipe implements).

Context (working folder):
- `add-method/tooling/test_bundle_parity.py:86` `test_templates_byte_identical` — new template + sample files must exist byte-identical in `_bundled/tooling/templates/`.
- existing UDD schema guards `test_udd_token_schema.py` · `test_udd_catalog_content_schema.py` — the bound `*.sample.json` must keep validating; the new samples are CSS/HTML/txt (outside those validators).

Honors (patterns / conventions):
- milestone shared decisions: **reuse-before-invent + consistency-by-construction** (the per-component kit; a semantic-token flip re-renders every screen) · **tool-agnostic** (the recipe is prose + a worked sample; no bundled renderer) · **bind read-only** (consume tokens/catalog/prototype, never reshape).
- `capability-as-prose-recommendation-engine-tool-agnostic` · template byte-identical parity (canonical↔_bundled) · the compact-DTCG alias form `{semantic.dotted.path}` → CSS var.

Anchors the contract cites: `udd-wireframe.md` (the recipe) · the worked-sample set (`tokens.sample.css` · `kit.sample.css` · `welcome.sample.html` · `settings.sample.html` · `wireframe.sample.txt`) · `test_wireframe_mock_recipe.py` (+ `test_component_reuse`) · the bound `tokens/catalog/prototype.sample.json`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: udd-wireframe.md — the wireframe (Stage A) + self-contained HTML-mock recipe (Stage B) that renders a prototype tree into a real, screenshot-able screen by composing a reusable per-component kit bound to `tokens.json`; + a worked two-screen sample proving reuse + token-flip consistency.
Framings weighed: shared `tokens.css` + `kit.css` linked per screen (chosen — a token flip re-renders every screen) · single self-contained file per screen (no reuse) · render via the json-render React runtime (heavier; the existing TS recipe in `udd-catalog.md`).
Must:
<must>
  - `udd-wireframe.md` defines a Stage-A WIREFRAME format: a low-fi structural map (regions + component slots) of a screen, derived from the prototype tree, pre-styling.
  - `udd-wireframe.md` defines a Stage-B HTML-MOCK recipe: resolve `tokens.json`'s semantic layer → CSS custom properties; one per-component CSS class per `catalog.json` component (the kit); compose the prototype tree's elements into HTML using the kit classes + mock data → a self-contained (no-network) screen a headless tool can screenshot.
  - consistency-by-construction: every screen composes from the SHARED per-component kit + token vars — never hand-styled per screen — so flipping a semantic token re-renders every screen the same way.
  - a worked sample set ships and renders: `tokens.sample.css` (from `tokens.sample.json` semantic) · `kit.sample.css` (Screen·Card·Text·Button) · `welcome.sample.html` (renders `prototype.sample.json`) · `settings.sample.html` (a SECOND screen that REUSES ≥1 kit component) · `wireframe.sample.txt` (the Stage-A low-fi for welcome).
  - bind read-only: the recipe consumes `tokens`/`catalog`/`prototype.sample.json` + the dialects unchanged; the captured image of a mock is design-confirm evidence (design.md beat 4), attached/mentioned in the feature's TASK.md.
  - the template + sample set ship byte-identical canonical↔`_bundled` (test_bundle_parity).
</must>
Reject:
<reject>
  - a sample screen hand-styles instead of composing from the kit -> "bespoke_screen"
  - a token rendered as a literal value instead of a CSS var resolved from `tokens.json` -> "unbound_token"
  - the recipe or a sample reshapes `tokens`/`catalog`/`prototype` (vs binding read-only) -> "contract_reshaped"
  - the second screen redefines a component instead of reusing the kit class -> "duplicate_component"
  - a template/sample file missing from the `_bundled` mirror -> "parity_break"
</reject>
After:
<after>
  - `udd-wireframe.md` + the sample set exist (canonical + `_bundled` byte-identical); welcome + settings render from the shared kit + `tokens.css`; flipping one semantic token in `tokens.sample.css` re-renders BOTH screens; the existing UDD JSON contracts are unchanged.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [contract] the sample-set SHAPE — shared linked `tokens.css` + `kit.css` (chosen) vs a single self-contained file per screen — lowest confidence because design.md beat 4 says "self-contained HTML mock" yet the reuse/token-flip requirement needs a SHARED stylesheet; I read "self-contained" as no-network/local-only (shared local CSS still screenshots headless), which makes the token-flip-reuse demonstrable; if wrong: re-author the samples inline-per-file (losing the shared-flip demo).
  - [ ] [spec] `tokens`→CSS-custom-properties as the binding — the natural web mapping for the `{semantic.…}` alias; if wrong (a non-web stack) the recipe needs a per-stack binding note (deferred).
  - [ ] [contract] the Stage-A wireframe as plain-text `.txt` vs a grayscale HTML — chose `.txt` for zero-dep low-fi; if wrong: minor re-author.
  - [x] reuse via a per-component kit + token vars is the consistency mechanism (milestone-confirmed).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
# --- one per Must ---

Scenario: Stage-A wireframe is a low-fi structural map        # Must 1
  Given udd-wireframe.md and the worked wireframe.sample.txt
  When a reader looks for the Stage-A format
  Then udd-wireframe.md defines a WIREFRAME as a low-fi structural map (regions + component slots) derived from the prototype tree, pre-styling
  And wireframe.sample.txt shows welcome's regions/slots as plain-text structure, naming no colors or pixel styles

Scenario: Stage-B recipe renders a self-contained screen      # Must 2
  Given udd-wireframe.md
  When a reader looks for the Stage-B HTML-mock recipe
  Then it states the four moves: resolve tokens.json semantic -> CSS custom properties, one kit class per catalog component, compose the prototype tree into HTML using kit classes + mock data, into a no-network (self-contained) screen a headless tool screenshots

Scenario: Consistency by construction via the shared kit      # Must 3
  Given welcome.sample.html and settings.sample.html
  When both screens are inspected for how they style components
  Then each composes from the SHARED kit.sample.css classes + tokens.sample.css vars and hand-styles nothing per screen
  And both link the same kit.sample.css and tokens.sample.css

Scenario: The worked sample set ships and renders             # Must 4
  Given the templates dir
  When the sample set is listed
  Then tokens.sample.css, kit.sample.css, welcome.sample.html, settings.sample.html and wireframe.sample.txt all exist
  And welcome.sample.html composes the catalog components of prototype.sample.json (Screen/Card/Text/Button)

Scenario: Bind read-only; capture is design-confirm evidence  # Must 5
  Given udd-wireframe.md
  When a reader looks for how the recipe treats the UDD contracts and the captured image
  Then it states it consumes tokens/catalog/prototype.sample.json unchanged
  And it states the captured image of a mock is design-confirm evidence (design.md beat 4) attached/mentioned in the feature's TASK.md

Scenario: Sample set is byte-identical across the two trees   # Must 6
  Given the canonical templates dir and the _bundled templates mirror
  When udd-wireframe.md and every sample file are compared
  Then each file is byte-identical canonical <-> _bundled (test_bundle_parity)

# --- one per Reject ---

Scenario: bespoke_screen — a screen hand-styles off-kit       # Reject
  Given a sample screen that sets its own inline/per-screen styles instead of kit classes
  When test_wireframe_mock_recipe inspects it
  Then it is rejected as "bespoke_screen"
  And the shipped samples keep composing only from kit.sample.css (unchanged)

Scenario: unbound_token — a literal value, not a token var    # Reject
  Given a sample that writes a literal color/space value instead of a var() resolved from tokens
  When test_wireframe_mock_recipe inspects kit.sample.css / the screens
  Then it is rejected as "unbound_token"
  And the shipped kit resolves every visual value via var(--…) from tokens.sample.css (unchanged)

Scenario: contract_reshaped — a bound JSON is mutated         # Reject
  Given an edit that reshapes tokens/catalog/prototype.sample.json rather than binding it read-only
  When the UDD schema guards run
  Then it is rejected as "contract_reshaped"
  And tokens.sample.json, catalog.sample.json and prototype.sample.json stay byte-for-byte unchanged

Scenario: duplicate_component — second screen redefines a part # Reject
  Given settings.sample.html defining its own class for a component already in the kit
  When test_component_reuse compares the two screens
  Then it is rejected as "duplicate_component"
  And settings reuses ≥1 kit class from welcome instead of redefining it (unchanged)

Scenario: parity_break — a file missing from the mirror       # Reject
  Given udd-wireframe.md or a sample file present in canonical but absent in _bundled
  When test_bundle_parity runs
  Then it is rejected as "parity_break"
  And shipping requires every template/sample file in BOTH trees (unchanged)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
ARTIFACT  udd-wireframe.md   (tooling/templates/, canonical + _bundled mirror)
  A recommendation guide (prose + a worked sample), tool-agnostic — no bundled renderer.
  Required structure (asserted by test_wireframe_mock_recipe):
    ## Stage A — wireframe   : a low-fi STRUCTURAL map (regions + component slots) of a
                               screen, derived from the prototype tree, pre-styling. Names
                               wireframe.sample.txt as the worked example.
    ## Stage B — HTML mock    : the four moves, in order —
                               (1) resolve tokens.json `semantic` layer → CSS custom properties,
                               (2) one kit CSS class per catalog.json component (the reusable kit),
                               (3) compose the prototype tree's elements into HTML via kit classes,
                               (4) populate with mock data → a self-contained (no-network) screen
                                   a headless tool screenshots.
    ## Reuse & consistency    : screens compose ONLY from the shared kit + token vars (never
                               hand-styled); a semantic-token flip re-renders every screen.
    ## Capture is evidence    : the screenshot of a mock is design-confirm evidence (design.md
                               beat 4), attached/mentioned in the feature's TASK.md; the engine
                               never renders (capture recipe = recommendation + named default).
    ## Binds (read-only)      : consumes tokens.json / catalog.json / prototypes/<name>.json +
                               the dialects UNCHANGED.

WORKED SAMPLE SET   (tooling/templates/, canonical + _bundled mirror — byte-identical)
  wireframe.sample.txt   : Stage-A low-fi for the welcome screen (plain-text regions/slots).
  tokens.sample.css      : tokens.sample.json `semantic` layer → `:root { --<dotted-path>: <value>; }`.
  kit.sample.css         : one class per catalog.sample.json component (Screen·Card·Text·Button),
                           every visual value via `var(--…)` (no literals).
  welcome.sample.html    : links tokens.sample.css + kit.sample.css; composes prototype.sample.json
                           (Screen > Card > {Text, Text, Button}) using kit classes + mock data.
  settings.sample.html   : a SECOND screen; links the SAME two stylesheets; REUSES ≥1 kit class
                           from welcome (e.g. card/text/button) without redefining it.

TEST   test_wireframe_mock_recipe.py   (tooling/, checks the CANONICAL tree; parity covers mirrors)
  one case per Must + per Reject (see §4), incl. test_component_reuse (welcome ∩ settings kit
  classes ≥ 1) and a token-flip assertion (both screens resolve the same semantic var).

Reject codes (named, observable):
  bespoke_screen      — a sample screen carries per-screen/inline styling instead of kit classes
  unbound_token       — a visual value written literally instead of var(--…) from tokens.sample.css
  contract_reshaped   — tokens/catalog/prototype.sample.json edited (not bound read-only)
  duplicate_component — settings redefines a kit class instead of reusing welcome's
  parity_break        — udd-wireframe.md or a sample file missing from the _bundled mirror

Touches (read-only BINDS, unchanged): tokens.sample.json · catalog.sample.json ·
  prototype.sample.json · udd-tokens.md · udd-catalog.md · skill/add/design.md (beats 3–4).
Frozen UDD JSON data contracts (prototypes/<name>.json json-render shape) are UNCHANGED.
```

Status: FROZEN @ v1 — approved by Tin Dang · 2026-06-16
Least-sure flag surfaced at freeze: ⚠ [contract] the sample-set SHAPE — shared linked `tokens.css` + `kit.css` (chosen, so one semantic-token flip re-renders BOTH screens) vs inline self-contained per file; "self-contained" read as no-network/local-only. Human approved the shared-CSS shape.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + every Reject has a test (guide-shape + sample-content suite, like test_design_loop_guide).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  # --- Musts ---
  - test_stage_a_wireframe_is_lowfi (Must 1): udd-wireframe.md has a Stage-A section; wireframe.sample.txt exists and names regions/slots, citing no colors/pixel styles.
  - test_stage_b_recipe_four_moves (Must 2): udd-wireframe.md's Stage-B names all four moves — tokens→CSS vars · kit class per catalog component · compose the tree · mock data → self-contained/headless.
  - test_screens_compose_from_shared_kit (Must 3): welcome + settings each <link> tokens.sample.css AND kit.sample.css; neither carries an inline style= attr.
  - test_sample_set_exists_and_composes (Must 4): all 5 sample files exist; welcome.sample.html uses the kit class for each catalog component in prototype.sample.json (Screen/Card/Text/Button).
  - test_binds_readonly_and_capture_is_evidence (Must 5): udd-wireframe.md states it consumes tokens/catalog/prototype unchanged AND that the captured image is design-confirm evidence attached/mentioned in TASK.md; the 3 bound *.sample.json still parse with their layer/component keys (unchanged-shape proxy).
  - test_bundled_mirror_byte_identical (Must 6): udd-wireframe.md + all 5 samples exist in the _bundled mirror, byte-identical to canonical.
  # --- Rejects ---
  - test_reject_bespoke_screen: no sample .html contains an inline `style=` attribute (composes from the kit, unchanged samples stay kit-only).
  - test_reject_unbound_token: kit.sample.css uses `var(--…)` and contains NO hex color literal (`#rrggbb`); literals live only in tokens.sample.css.
  - test_reject_contract_reshaped: tokens.sample.json has `semantic`, catalog.sample.json has `Screen`, prototype.sample.json has `root` — the bound JSONs keep their shape (not reshaped by the recipe).
  - test_component_reuse (duplicate_component): welcome ∩ settings kit CSS classes ≥ 1, and settings defines no `<style>` block redefining a kit class.
  - test_parity_break_named: udd-wireframe.md names the _bundled mirror / parity as a ship requirement (the reject is enforced by test_bundle_parity).
  # --- consistency ---
  - test_token_flip_rerenders_both: both screens link the SAME tokens.sample.css, and kit.sample.css resolves `var(--semantic-…)` names defined in tokens.sample.css (so one flip re-renders both).
</test_plan>

Tests live in: `add-method/tooling/test_wireframe_mock_recipe.py` · checks the CANONICAL tree (parity covers the mirror, like test_design_loop_guide) · MUST run red (template + samples absent) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/templates/` `add-method/src/add_method/_bundled/tooling/templates/` `add-method/tooling/test_wireframe_mock_recipe.py`   <!-- two template dirs (canonical + _bundled mirror) where the NEW udd-wireframe.md + 5 sample files land byte-identical; + the new red test. Declared BEFORE the freeze so the tests→build scope anchor captures the real footprint (task-1 lesson). Directory tokens = a may-touch ceiling; only the new files are written, existing templates untouched. -->
Strategy (ordered batches): 1. canonical udd-wireframe.md (the recipe prose) · 2. canonical sample set (tokens.sample.css → kit.sample.css → welcome.sample.html → settings.sample.html → wireframe.sample.txt) · 3. byte-identical _bundled mirror of all 6 · 4. green the red test.
Safety rule (feature-specific): touch ONLY the two template dirs + the test; never edit the bound `*.sample.json`, the dialect docs, or design.md (read-only binds — a change there is a change-request).
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.
Build log (transparent — no silent skips):
  - test-matcher false positive: `test_component_reuse`'s `assertNotIn("<style", …)` is a crude substring and tripped on the literal `<style>` written inside settings.sample.html's explanatory COMMENT (an inert comment, not a real style block). Per rule 3 I did NOT touch the test; I reworded the sample comment ("no per-screen stylesheet") so it no longer embeds that token. Recorded as a §7 TDD delta (the matcher should ignore comments).
  - json-render fast-path ADDED mid-build on a human decision (deep-review of vercel-labs/json-render): a "## Fast path — render via json-render" section in udd-wireframe.md — render `prototype.json` through the project's real catalog (`defineCatalog` / `@json-render/shadcn`) and capture via `@json-render/image` (Satori → PNG/SVG, no browser). ADDITIVE: no frozen §3 section removed, no reject changed, all 12 tests + parity still green → no re-freeze. `@json-render/image` earmarked as a capture default for task 3 (capture-evidence). Recorded as a §7 UDD delta.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — `test_wireframe_mock_recipe` 12/12; full suite 1131 green (`python3 -m unittest discover`).
- [x] coverage did not decrease — net-new test file; every Must + Reject + the token-flip has a case.
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; the test was hardened in TESTS (existence guard on bespoke_screen), never weakened in build. The one in-build adjustment was to a SAMPLE comment (see §5 build log), not a test.
- [x] the green was EARNED, not gamed — adversarial refute-read (self): `test_reject_contract_reshaped` is green pre- and post-build (a "must-not-reshape" guard on the read-only binds, not a feature test — acceptable as a guard, mildly weak as a reshape detector); all feature tests went red→green on the artifacts; `test_token_flip` is corroborated by REAL pixels (one-line `#3B82F6`→`#16A34A` re-themed BOTH buttons). The only weakness found — the crude `<style` substring matcher — is recorded as a §7 TDD delta, not a cheat. No vacuous/overfit pass remains.
- [x] concurrency / timing — N/A: static template + sample files; no runtime, no shared state.
- [x] no exposed secrets, injection openings, or unexpected dependencies — samples are static HTML/CSS with mock data, NO `<script>`, NO network/external links (local siblings only). json-render is a prose RECOMMENDATION, not a method dependency. No security finding.
- [x] layering & dependencies follow conventions — artifacts live in `tooling/templates/` + the `_bundled` mirror (byte-identical, test_bundle_parity); honors `capability-as-prose-recommendation-engine-tool-agnostic`.
- [ ] a person reviewed and approved the change   <!-- conservative gate: human-owned; left unstamped until the answer -->

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `test_wireframe_mock_recipe.py` is unittest-discovered and runs (12 cases); it references the real new files. No orphan.
- [x] DEAD-CODE — no unused symbol; helpers (`_text`, `_html_classes`) are each exercised.
- [x] SEMANTIC (prose) — read `udd-wireframe.md` in full: states the four Stage-B moves in order, the floor/fast-path tiers, binds tokens/catalog/prototype read-only, capture = design-confirm evidence attached to TASK.md, byte-identical parity. Accurate. RENDER EVIDENCE: headless-Chrome captures of `welcome` + `settings` render the expected layout from the shared kit; a one-line semantic-token flip re-rendered BOTH (PNGs shown to the human at the gate). Capture-viewport lesson (viewport ≥ screen max-width) earmarked for task 3.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-16   (conservative gate; approved after reviewing the rendered welcome/settings + token-flip captures)

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): bespoke_screen / unbound_token / duplicate_component rates as real projects author screens; capture-clip incidents (viewport < screen width).
Spec delta for the next loop: `capture-evidence` (task 3) inherits three things from here — the `@json-render/image` named-default capture, the capture-viewport rule (viewport ≥ screen max-width), and the captures-in-TASK.md rule (reopen design.md beat 4).

### Competency deltas
- [UDD · folded] json-render is itself a Generative-UI **catalog** framework (multi-framework: React/Vue/Svelte/Solid/RN/Satori) and our `prototype.json` IS its `Spec` — so the fast-path renders the *real product*, and `@json-render/image` (Satori → PNG/SVG, no browser) is a deterministic capture engine (evidence: deep-review WebFetch; fast-path section added; earmarked for task 3).
- [UDD · folded] consistency-by-construction is real + demonstrable: ONE semantic-token line flip (`#3B82F6`→`#16A34A`) re-rendered BOTH screens identically (evidence: welcome/settings flipped PNGs).
- [TDD · folded] content-shape tests with crude substring matchers (`assertNotIn("<style", …)`) false-positive on the token appearing in PROSE/comments — matchers over structural artifacts should strip comments or assert on parsed structure (evidence: test_component_reuse tripped on settings.sample.html's comment; fixed by rewording the sample, not the test).
- [TDD · folded] a headless capture's viewport MUST be ≥ the screen's max content width or the image clips — a capture-settings issue, not a layout bug (evidence: first welcome.png clipped at a 210 CSS-px viewport) → task 3 capture recipe.
- [ADD · folded] declaring §5 Scope BEFORE the freeze (applied from task 1) made the tests→build scope anchor capture the real footprint — ZERO scope-gate findings this task (evidence: clean gate). Confirms the task-1 lesson generalizes.
- [SDD · folded] additive doc content (the json-render fast-path) folded in mid-build with NO re-freeze because it removed no frozen §3 section and changed no reject — the "additive ⊆ frozen contract" judgment (evidence: 12 tests + parity stayed green after the edit).
