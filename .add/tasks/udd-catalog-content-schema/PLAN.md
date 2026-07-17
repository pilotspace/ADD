# TASK: UDD catalog + content trees — component catalog (typed props · semantic-token refs) + flat json-render-aligned prototype trees

slug: udd-catalog-content-schema · created: 2026-06-13 · stage: mvp
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
  - `add-method/tooling/add.py` — home for a NEW pure validator `_catalog_tree_violations(catalog: dict,
    tree: dict) -> list[(code, path, detail)]` (the testable artifact). SEPARATE from task 1's
    `_token_layer_violations` (L~1108, shipped udd-token-schema) — udd-check-lint composes BOTH. NOT wired into
    `cmd_check` here (same Fork-A boundary task 1 froze). ×3 engine mirrors stay byte-identical.
  - `add-method/tooling/add.py:_token_layer_violations` / `_token_value_form_ok` (shipped task 1) — the token
    dialect + alias form `{layer.dotted.path}` this task's catalog prop-bindings + tree token-citations REUSE.
    The 3rd token layer (`semantic`) is what a `token`-typed catalog prop binds to.
  - `add-method/tooling/add.py:_templates_dir()`/`_render_template` (L148/152) — the sample catalog + prototype
    tree ship in `templates/` as assets (×3 mirrors — `test_bundle_parity` + `test_tree_parity` rglob templates/).
  - `add-method/tooling/add.py:cmd_check` (L~1109) — the SEAM udd-check-lint wires the catalog/tree named reds
    into; NAMED-not-touched here (Fork A boundary).
Context (working folder):
  - `.add/tasks/udd-catalog-content-schema/RESEARCH.md` — json-render pin (v0.19.0 / `4e4dc46`) + the Spec shape
    we mirror + the clarification (json-render has no JSON catalog → ours is a compact JSON doc + a documented
    adapter recipe). Read before the freeze.
  - `.add/tasks/udd-token-schema/` (shipped) — the tokens dialect (`templates/tokens.sample.json`,
    `templates/udd-tokens.md`) this task builds atop; the foundation-shape decision unifies tokens + catalog + trees.
Honors (patterns / conventions):
  - milestone shared decisions: a content tree cites ONLY cataloged components (fail-closed named red); the
    engine lints SHAPE only (stdlib, tool-agnostic); PIN json-render to a NAMED version at THIS freeze (the
    milestone's top risk). The token citation rule extends: a `token`-typed component prop cites a SEMANTIC token.
  - the task-1 contract pattern: ship the validator FUNCTION (Fork A), a SAMPLE that validates clean, a dialect
    doc with NAMED divergences; ×3 byte-identical mirrors; engine-pin re-aim + pin self-test from ground.
  - the [SDD] grounding-inline rule + the [SDD] leaf-ness lesson (task 1 §7): state structural containment
    rules (which components may have children; props ⊆ declared) EXPLICITLY, not implied.
Anchors the contract cites: `_catalog_tree_violations(catalog, tree) -> list[(code,path,detail)]` (NEW, separate from `_token_layer_violations`) · the CATALOG schema (component → {description?, hasChildren?, props:{name: PropSpec}}) · the CONTENT-TREE schema = json-render flat Spec `{root, elements:{id:{type,props,children?}}}` (pinned @ v0.19.0/`4e4dc46`, RESEARCH.md) · the named reds (tree_cites_uncataloged_component + unknown_prop · prop_type_mismatch · non_semantic_prop_token · dangling_child · children_not_allowed · missing_root) · the SAMPLE catalog + prototype tree in `templates/` · the render-recipe doc · `cmd_check` (downstream seam, named-not-touched) · `test_bundle_parity`/`test_tree_parity` (×3 guards).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: the render-ready half of the UDD foundation — a component CATALOG (typed props, semantic-token
bindings) + flat json-render-aligned prototype CONTENT TREES, plus a pure validator
`_catalog_tree_violations(catalog, tree)` that a shipped sample passes clean. Settles the foundation JSON
shape (token layers + catalog + content trees) the whole milestone builds on.

Framings weighed: catalog+tree-validator (chosen) · full-json-render-mirror · doc-and-sample-only.
  - CHOSEN catalog+tree-validator: OUR compact JSON catalog + json-render's flat `Spec` for trees (mirrored
    so trees render as-is) + a SEPARATE pure validator; udd-check-lint composes it with task 1's token
    validator. Catalog needs a documented ~20-line adapter to json-render's TS `defineCatalog` (RESEARCH.md).
  - full-json-render-mirror: mirror TS `defineCatalog` + the full `UIElement` (state/on/visible/repeat)
    verbatim. Max fidelity but heavy + TS-coupled, against the compact AI-economy dialect. (Fork B, §3.)
  - doc-and-sample-only: defer ALL validation to udd-check-lint. Rejected (same as task 1: no red→green here).

Must:
<must>
  - FOUNDATION SHAPE: a NAMED SET — `tokens.json` (the task-1 dialect) · `catalog.json` · `prototypes/<name>.json`.
    (Fork A — the milestone-owned shape decision; surfaced at the freeze.)
  - CATALOG = `{ "components": { "<Name>": { "description"?: str, "hasChildren"?: bool (default false),
    "props": { "<prop>": PropSpec } } } }`. A PropSpec is exactly one of:
      · `{ "type": "string" | "number" | "boolean" }`           — a literal-valued prop
      · `{ "type": "enum", "values": [str, …] }`                — a constrained literal
      · `{ "type": "token", "token": "<$type>" }`               — value MUST cite a SEMANTIC token of that
        `$type` (`$type` ∈ the task-1 supported set: color·dimension·number·fontFamily·fontWeight·duration).
  - CONTENT TREE = json-render flat `Spec` (pinned @ json-render v0.19.0 / commit `4e4dc46`):
    `{ "root": "<id>", "elements": { "<id>": { "type": "<Name>", "props": {…}, "children"?: ["<id>", …] } } }`.
      · `type` ∈ catalog component names.
      · each `props` key ⊆ the component's declared props; each value matches its PropSpec (a `token` prop's
        value is the alias form `{semantic.dotted.path}` from the task-1 dialect — it MUST target the
        `semantic` LAYER (first path segment); the target token's existence + `$type`-match are resolved
        downstream by udd-check-lint (which composes tokens.json) — NOT checkable from (catalog, tree)). [v2]
      · `children` only on a `hasChildren` component; every child id ∈ `elements`.
      · `root` ∈ `elements`.
      · json-render's optional `state`/`on`/`visible`/`repeat` are PASSED THROUGH — render-compatible (a
        clickable prototype) but NOT linted, keeping the validator lean. (Fork B, §3.)
  - `_catalog_tree_violations(catalog: dict, tree: dict) -> list[(code, path, detail)]` — pure, stdlib,
    deterministic order; `[]` == valid. SEPARATE from `_token_layer_violations`; udd-check-lint composes both.
  - A SAMPLE `catalog.sample.json` + `prototype.sample.json` that validate clean against each other, plus a
    documented RENDER RECIPE (the json-render adapter) — the milestone's render-ready exit criterion.
</must>
Reject:
<reject>
  - a tree element `type` not in the catalog -> "tree_cites_uncataloged_component"
  - a tree element `props` key not declared on its component -> "unknown_prop"
  - a prop value whose form mismatches its PropSpec (string given a number; enum value outside the set; a
    `token` prop given a non-alias literal) -> "prop_type_mismatch"
  - a `token` prop whose alias does not target the SEMANTIC layer (first path segment ≠ `semantic`) -> "non_semantic_prop_token"
    [v2 narrow: target-token existence + `$type`-match need tokens.json → deferred to udd-check-lint, which composes tokens+catalog+tree]
  - a `children` id absent from `elements` -> "dangling_child"
  - a NON-EMPTY `children` on a component whose `hasChildren` is false -> "children_not_allowed"
    [v3 note: an EMPTY `children` array is treated as ABSENT — no violation (present = a non-empty array)]
  - `root` missing or absent from `elements` -> "missing_root"
  - a catalog component with a malformed PropSpec (unknown `type`, a `token` prop naming an unknown `$type`),
    OR a component entry that is not an object -> "malformed_catalog"   [v3: non-dict component entry added]
  - a tree element that is not an object, or whose `props` is not an object, or whose `children` is not an
    array -> "malformed_element"   [v3 NEW code: fail-closed structural validation of a tree element]
</reject>
After:
<after>
  - the foundation shape + the render recipe are documented, with the json-render pin (v0.19.0/`4e4dc46`) NAMED.
  - the sample catalog + prototype tree validate clean: `_catalog_tree_violations(catalog, tree) == []`.
  - `_catalog_tree_violations` is pure stdlib and NOT yet wired into `cmd_check` (that is udd-check-lint).
  - ×3 mirrors byte-identical (validator in add.py; the sample assets in templates/).
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ FOUNDATION SHAPE (Fork A) — a NAMED SET (`tokens.json` · `catalog.json` · `prototypes/<name>.json`) vs ONE
    combined `foundation.json`. Lowest-confidence because it is the milestone-owned "foundation JSON shape"
    contract that udd-design-template (the DESIGN.md binding) and the render recipe both build on; if wrong,
    re-freeze the file layout + rewrite the sample + the recipe (touches two downstream tasks' assumptions).
  - [ ] JSON-RENDER ALIGNMENT DEPTH (Fork B) — validate only the structural core (type/props/children) and
    PASS THROUGH json-render's on/state/visible/repeat (render-compatible + clickable, but unlinted) vs lint
    the full interactivity surface. If wrong: add interactivity rules later (additive, low cost).
  - [ ] PROP-TOKEN BINDING (Fork C) — a `token`-typed prop cites a SEMANTIC token ONLY. Alternative: also allow
    component-LAYER tokens. If wrong: widen the allowed layer set (small, additive).
  - [ ] VALIDATOR BOUNDARY (Fork D, consistent with task 1) — ship the function; udd-check-lint wires it into
    cmd_check + composes it with the token validator. Low-risk (mirrors the frozen task-1 boundary).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the shipped sample catalog + prototype validate clean (the exit criterion)
  Given the sample catalog.json + prototype.json shipped in templates/ (typed props, semantic-token bindings, nested children)
  When _catalog_tree_violations(catalog, tree) runs
  Then it returns [] (no violations)

Scenario: a token-typed prop citing a matching semantic token passes
  Given a Button prop "background" declared {type:token, token:color} and a tree element binding it to "{semantic.color.action}" (a semantic color token)
  When _catalog_tree_violations runs
  Then no violation is reported for that element

Scenario: literal-typed props matching their form pass
  Given a tree element with a string prop, a number prop, a boolean prop, and an enum prop whose value is in the declared set
  When _catalog_tree_violations runs
  Then no violation is reported for that element

Scenario: children on a hasChildren component with present ids pass
  Given a catalog Card with hasChildren:true and a tree where Card's children ids all exist in elements
  When _catalog_tree_violations runs
  Then no violation is reported for the container or its children

Scenario: json-render interactivity fields are passed through unlinted
  Given a tree element carrying state/on/visible/repeat alongside a valid type+props
  When _catalog_tree_violations runs
  Then it returns [] (the passthrough fields are render-compatible but not linted)

Scenario: a tree element typed to an uncataloged component is rejected
  Given a tree element whose "type" is "Carousel", absent from the catalog
  When _catalog_tree_violations runs
  Then a ("tree_cites_uncataloged_component", path, detail) violation is returned
  And cataloged elements in the same tree report no violation

Scenario: a prop key not declared on its component is rejected
  Given a tree Button element with a props key "elevation" the catalog does not declare on Button
  When _catalog_tree_violations runs
  Then an ("unknown_prop", path, detail) violation is returned
  And the element's declared props report no violation

Scenario: a prop value whose form mismatches its PropSpec is rejected
  Given a tree element giving a number to a string-typed prop (and an enum value outside its declared set, and a non-alias literal to a token-typed prop)
  When _catalog_tree_violations runs
  Then a ("prop_type_mismatch", path, detail) violation is returned for each
  And props whose values match their PropSpec report no violation

Scenario: a token prop whose alias does not target the semantic layer is rejected
  Given a token-typed (color) prop bound to "{primitive.color.blue}" (alias targets the primitive layer, not semantic)
  When _catalog_tree_violations runs
  Then a ("non_semantic_prop_token", path, detail) violation is returned
  And a token prop bound to a "{semantic.*}" alias reports no violation here
  # [v2] target existence + $type-match (e.g. a {semantic.space.*} dimension bound to a color prop) need tokens.json — covered by udd-check-lint (task 4)

Scenario: a child id absent from elements is rejected
  Given a hasChildren element listing a child id "missing-1" not present in elements
  When _catalog_tree_violations runs
  Then a ("dangling_child", path, detail) violation is returned
  And the present sibling child ids report no violation

Scenario: children on a non-container component is rejected
  Given a tree element of a component whose hasChildren is false (default) carrying a non-empty children list
  When _catalog_tree_violations runs
  Then a ("children_not_allowed", path, detail) violation is returned
  And a sibling hasChildren container with children reports no violation

Scenario: a missing or absent root is rejected
  Given a tree whose "root" id is absent from elements (or the root key is missing)
  When _catalog_tree_violations runs
  Then a ("missing_root", path, detail) violation is returned
  And the elements map is otherwise read unchanged (pure, no mutation)

Scenario: a malformed catalog PropSpec is rejected
  Given a catalog prop with an unknown "type" (or a token prop naming an unknown $type)
  When _catalog_tree_violations runs
  Then a ("malformed_catalog", path, detail) violation is returned
  And well-formed PropSpecs in the same catalog report no violation

Scenario: a non-object catalog component entry is rejected (and never crashes)  # [v3] refute Finding 1
  Given a catalog whose component value is a string (not an object), cited by a tree element with children
  When _catalog_tree_violations runs
  Then a ("malformed_catalog", "components.<Name>", detail) violation is returned
  And the call returns a list (it does NOT raise) — a pure total function over dict inputs

Scenario: a malformed tree element structure is rejected  # [v3] refute Finding 2 — malformed_element
  Given a tree element that is not an object, OR whose "props" is not an object, OR whose "children" is not an array
  When _catalog_tree_violations runs
  Then a ("malformed_element", path, detail) violation is returned for each
  And well-formed sibling elements report no violation

Scenario: an empty children array on a non-container is treated as absent  # [v3] refute Finding 3
  Given a non-hasChildren component carrying "children": []
  When _catalog_tree_violations runs
  Then no violation is returned (present = a non-empty array; empty == absent)
  And a sibling with a non-empty illegal children list still reports children_not_allowed
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
fn _catalog_tree_violations(catalog: dict, tree: dict) -> list[tuple[str, str, str]]
  []                      -> the tree is valid against the catalog
  [(code, path, detail)…] -> one tuple per violation, in deterministic order
                             (elements walked in document key order; root checked first)
  PURE: never mutates `catalog`/`tree`; stdlib only; no I/O. (Parsing JSON → dict is the caller's job.)
  SEPARATE from _token_layer_violations (task 1); udd-check-lint composes BOTH.

  codes  (the catalog/tree named reds; udd-check-lint surfaces them inside cmd_check):
    "tree_cites_uncataloged_component"  element "type" ∉ catalog["components"]
    "unknown_prop"                      a props key not declared on the element's component
    "prop_type_mismatch"                value form ≠ PropSpec (str↔num↔bool · enum value ∉ values · token prop given a non-alias literal)
    "non_semantic_prop_token"           a token-prop alias does not target the SEMANTIC layer (first path segment ≠ "semantic")
                                        [v2: existence + $type-match of the target token defer to udd-check-lint, which has tokens.json]
    "dangling_child"                    a child id ∉ elements
    "children_not_allowed"              a NON-EMPTY children list on a component whose hasChildren is false (empty == absent)
    "missing_root"                      "root" absent, or names an id ∉ elements
    "malformed_catalog"                 a PropSpec with unknown "type" · a token prop naming an unknown $type · OR a non-object component entry [v3]
    "malformed_element"                 [v3] a tree element that is not an object · "props" not an object · "children" not an array

CATALOG  (OUR compact JSON — json-render has no JSON catalog; the render recipe adapts it to defineCatalog):
  { "components": { "<Name>": {
      "description"?: str,
      "hasChildren"?: bool   (default false),
      "props": { "<prop>": PropSpec } } } }
  PropSpec = exactly one of:
    { "type": "string" | "number" | "boolean" }              literal-valued prop
    { "type": "enum", "values": [str, …] }                   constrained literal (value ∈ values)
    { "type": "token", "token": "<$type>" }                  value cites a SEMANTIC token of that $type
                                                             ($type ∈ task-1 set: color·dimension·number·
                                                              fontFamily·fontWeight·duration)

CONTENT TREE  (json-render flat Spec — pinned @ vercel-labs/json-render v0.19.0 / commit `4e4dc46`):
  { "root": "<id>",
    "elements": { "<id>": {
        "type": "<Name>",            ∈ catalog component names
        "props": { … },              keys ⊆ component's declared props; each value matches its PropSpec
        "children"?: ["<id>", …]     only if the component hasChildren; every id ∈ elements
    } } }
  token-prop value = alias "{semantic.dotted.path}" (task-1 dialect) → MUST target the semantic LAYER (first
    path segment); the target token's existence + $type-match are resolved downstream by udd-check-lint. [v2]
  PASSTHROUGH (Fork B): json-render's optional state/on/visible/repeat are render-compatible (a clickable
    prototype) but NOT linted — keeps the validator lean; interactivity rules stay additive for later.

SAMPLE: templates/catalog.sample.json + templates/prototype.sample.json — typed props, ≥1 semantic-token
  binding, a hasChildren container with present children; _catalog_tree_violations(parse both) == [].
  RENDER RECIPE: templates/udd-catalog.md documents the ~20-line catalog.json → defineCatalog(...) adapter
  (props → a Zod object) + that the tree feeds catalog.validate(spec) AS-IS. (×3 mirrors, test_bundle_parity.)

BOUNDARY (Fork A=foundation shape · Fork D=validator boundary, both consistent with task 1):
  FOUNDATION SHAPE = a NAMED SET — tokens.json (task 1) · catalog.json · prototypes/<name>.json (Fork A).
  THIS task ships _catalog_tree_violations + the two sample assets + the render-recipe doc.
  udd-check-lint LATER calls this fn inside cmd_check (named reds) and composes it with _token_layer_violations.
  cmd_check is NAMED-not-touched here.
  [v2 DEFERRAL] non_semantic_prop_token here is LAYER-only (the alias must target `semantic`); the target
  token's existence + $type-match are udd-check-lint's job — it is the composer that holds tokens.json.

Files touched (→ §5 scope): add.py (+2 mirrors) new _catalog_tree_violations · templates/catalog.sample.json
  + templates/prototype.sample.json (+2 mirrors each) · templates/udd-catalog.md the render-recipe doc
  (+2 mirrors) · test_udd_catalog_content_schema.py (new red suite, this task dir).
```

Status: FROZEN @ v3 — approved by Tin Dang 2026-06-13.
  v3 (change-request raised at VERIFY by the adversarial refute, Option A): the refute found a HARD-STOP
  crash (a non-object component cited by an element with children threw AttributeError) + a structural
  fail-open (props not an object / children not an array silently passed). Closed FAIL-CLOSED: a 9th code
  `malformed_element` (element not an object · props not an object · children not an array); `malformed_catalog`
  deepened to also flag a non-object component entry; the validator is now a pure TOTAL function (never raises);
  empty `children` is documented as ABSENT (no violation). The signature + the original behavior of the prior
  8 codes are UNCHANGED — strict fail-closed additions. §1 reject + §2 scenarios amended to match.
  v2 (change-request raised at TESTS, Option B): the frozen `(catalog, tree)` signature cannot resolve a
  token's existence/$type (that needs tokens.json), so `non_semantic_prop_token` is NARROWED to LAYER-only —
  a token-prop alias must target the `semantic` layer (first path segment); target existence + $type-match
  DEFER to udd-check-lint (task 4), the composer that holds tokens+catalog+tree. A strict narrowing: the
  signature and the other 7 codes are UNCHANGED; no behavior is added. §1 reject + §2 scenario amended to match.
  v1 fork resolutions (still stand — the freeze answers, all recommended defaults):
  A = NAMED SET (`tokens.json` · `catalog.json` · `prototypes/<name>.json`) — mirrors json-render's
  catalog/spec split; each file lints independently · B = CORE + PASSTHROUGH (lint type/props/children;
  json-render's `state`/`on`/`visible`/`repeat` render-compatible but unlinted) · C = SEMANTIC-ONLY
  prop-token binding (extends task-1's citation rule) · D = SHIP THE VALIDATOR HERE (udd-check-lint later
  wires it into `cmd_check` + composes with `_token_layer_violations`; `cmd_check` named-not-touched).
  Changing this contract now = a change request back to SPECIFY.
Least-sure flag surfaced at freeze: [contract] FOUNDATION SHAPE (Fork A) — a NAMED SET (`tokens.json` ·
  `catalog.json` · `prototypes/<name>.json`) rather than ONE combined `foundation.json`. Lowest-confidence
  across the whole bundle because it is the milestone-owned "foundation JSON shape" contract that BOTH
  downstream tasks build on — udd-design-template binds DESIGN.md to these files and the render recipe maps
  them to json-render. Leans named-set: it mirrors json-render's own catalog/spec separation, each file lints
  independently (token vs catalog/tree validators stay separate), and a prototype can be added without
  touching tokens or catalog. Cost if wrong: re-freeze the file layout + rewrite the two sample assets + the
  recipe + adjust two downstream tasks' assumptions — but the VALIDATOR logic (codes, PropSpec forms, the
  flat-Spec walk) is shape-independent, so the red→green behavior is not thrown away. Secondary flags:
  [contract] Fork B passthrough (state/on/visible/repeat unlinted — additive if we later lint them) and
  [contract] Fork C prop-token binds SEMANTIC-only (widening to component-layer is additive).
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 90% (the validator + the shipped sample pair)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_sample_validates_clean: load catalog.sample.json + prototype.sample.json / _violations / assert []
  - test_token_prop_semantic_binding_ok: valid token prop → "{semantic.*}" / assert no violation
  - test_literal_props_ok: string·number·boolean·enum-in-set values / assert no violation
  - test_children_present_ok: hasChildren container, all child ids present / assert no violation
  - test_passthrough_fields_unlinted: element carries on/state/visible/repeat / assert []
  - test_tree_cites_uncataloged_component: type ∉ catalog / assert ("tree_cites_uncataloged_component", path) + cataloged elems clean
  - test_unknown_prop: props key not declared / assert ("unknown_prop", path) + declared props clean
  - test_prop_type_mismatch: number→string prop, enum∉set, token prop non-alias literal / assert ("prop_type_mismatch", path) each + matching props clean
  - test_non_semantic_prop_token: token prop alias "{primitive.*}" / assert ("non_semantic_prop_token", path) + a "{semantic.*}" binding clean
  - test_dangling_child: child id ∉ elements / assert ("dangling_child", path) + present sibling clean
  - test_children_not_allowed: children on a non-hasChildren component / assert ("children_not_allowed", path) + a real container clean
  - test_missing_root: root absent / root ∉ elements / assert ("missing_root", path); input not mutated
  - test_malformed_catalog: PropSpec unknown "type"; token prop unknown $type / assert ("malformed_catalog", path) + good specs clean
  - test_violations_are_pure_and_ordered: deterministic order + input not mutated
  - test_parity_samples_and_doc_mirrored: catalog/prototype/doc ×3 byte-identical (canonical=bundled=dogfood)
  - test_pin_annotation_names_this_task: engine_pin records "re-aimed @ udd-catalog-content-schema" + carries "udd-token-schema"
</test_plan>

Tests live in: `add-method/tooling/test_udd_catalog_content_schema.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `.add/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/templates/catalog.sample.json` `add-method/src/add_method/_bundled/tooling/templates/catalog.sample.json` `.add/tooling/templates/catalog.sample.json` `add-method/tooling/templates/prototype.sample.json` `add-method/src/add_method/_bundled/tooling/templates/prototype.sample.json` `.add/tooling/templates/prototype.sample.json` `add-method/tooling/templates/udd-catalog.md` `add-method/src/add_method/_bundled/tooling/templates/udd-catalog.md` `.add/tooling/templates/udd-catalog.md` `add-method/tooling/test_udd_catalog_content_schema.py`
Strategy (ordered batches): 1. red suite + the sample catalog/prototype fixtures → red for the right reason. 2. `_catalog_tree_violations` in canonical add.py → canonical green. 3. mirror add.py ×2 + re-pin engine_pin.py (`re-aimed @ udd-catalog-content-schema`, carry `udd-token-schema`) + ship catalog.sample.json ×3 + prototype.sample.json ×3 + udd-catalog.md ×3 → parity green. 4. pin self-test green.
Safety rule (feature-specific): the validator is PURE — never mutate `catalog`/`tree`, stdlib only, no I/O, deterministic order; fail-closed (never skip a subtree / pass a malformed PropSpec silently).
Code lives in: `add-method/tooling/add.py` (the engine; `_catalog_tree_violations` is a pure helper, NOT yet wired into cmd_check — Fork A/D).
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

- [x] all tests pass — full suite 965 OK on python3.14 + python3.10; add.py check 300/0.
- [x] coverage did not decrease — +3 net tests (16→19) over v2; the new fail-closed paths are covered.
- [x] no test or contract was altered during build — the §3 amendments (v2 at tests, v3 at verify) went
      through the proper change-request flow back to SPECIFY (human-approved each), NOT edited during build;
      the build phase touched only add.py/engine_pin/mirrors. Tests were STRENGTHENED (refute Finding 4) at the
      tests phase, never weakened.
- [x] the green was EARNED — an adversarial refute (python-expert subagent, Rule 5) argued the green was NOT
      earned and FOUND a HARD-STOP crash (non-object component cited with children → AttributeError) + a
      structural fail-open (props not an object / children not an array silently passed) + 4 weak/redundant
      tests. ALL closed before this gate (close-gap-before-gate): v3 made the validator a pure TOTAL function,
      added `malformed_element` + non-dict-component → malformed_catalog, and strengthened the 4 tests. The exact
      refute inputs were re-probed and now behave (malformed_catalog/malformed_element returned, no raise). No
      overfit (each valid test now a distinct minimal fixture), no vacuous asserts (the purity test asserts the
      injected faults are reported), no stubbed logic.
- [x] concurrency / timing safe — the validator is PURE (no mutation, no shared/global state), stdlib-only,
      no I/O; safe under concurrent calls (re-entrant by construction).
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only, no new imports, no
      eval/exec/format-injection; a pure dict→list function. NO security finding.
- [x] layering & dependencies follow conventions — a pure helper beside `_token_layer_violations`; NOT wired
      into cmd_check (documented Fork A/D boundary — udd-check-lint composes both validators later).
- [x] reviewed — auto-resolved under `autonomy: auto` (accountable owner: the run / Tin Dang), AFTER an
      independent adversarial refute + a human-approved v3 contract amendment. No residue (security/concurrency/
      architecture all clear).

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_catalog_tree_violations` is referenced by test_udd_catalog_content_schema.py (19
      tests); helpers `_propspec_malformed` + `_prop_value_code` are called inside it. cmd_check wiring is the
      DEFERRED Fork A/D seam (udd-check-lint) — not dead, it is tested now and composed later.
- [x] DEAD-CODE (code) — no orphan: all 3 new symbols referenced (tests + internal calls); grep confirms no
      unused symbol introduced.
- [x] SEMANTIC (prose) — templates/udd-catalog.md read in full: the named-set foundation, the 9-code table,
      the v2 layer-only note, and the ~20-line defineCatalog render recipe all match the frozen §3 @ v3.

### GATE RECORD
Outcome: PASS
Reviewed by: auto-resolved under autonomy=auto (run owner: Tin Dang) · adversarial refute by python-expert subagent · date: 2026-06-13

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): per-code violation rate from udd-check-lint once it composes both
validators; especially malformed_element / malformed_catalog (the fail-closed structural reds) and
non_semantic_prop_token (the layer-only red whose $type-match lands in udd-check-lint).
Spec delta for the next loop: udd-check-lint must (a) wire both validators into cmd_check, and (b) own the
DEFERRED cross-file check — a token-prop's `{semantic.*}` alias actually resolving to a semantic token of the
prop's declared `$type` (needs tokens.json). udd-design-template binds DESIGN.md to the named-set foundation.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
  - [TDD · folded] a traversal/validator task needs a TOTAL-FUNCTION (never-raises) probe + a wrong-JSON-type
    probe from ground — the 13 scenarios all used well-formed dicts, so the adversarial refute, not the suite,
    caught the crash (evidence: refute Finding 1 — non-object component + children → AttributeError).
  - [SDD · folded] freeze-time check: every Reject must be SATISFIABLE by the frozen signature — non_semantic_
    prop_token's $type-match needed tokens.json the `(catalog, tree)` signature never receives (evidence: v2
    change-request raised while writing the red test for that scenario).
  - [SDD · folded] "lint shape only" left tree-element STRUCTURE (props is an object, children is an array)
    implied, not stated — the 9th code malformed_element had to be added at verify (evidence: v3 refute
    Finding 2 — props:[…]/children:"x" silently passed).
  - [UDD · folded] identity VALUES are human-owned — surface design tokens (brand color, palette, type) at
    specify, never auto-pick from a menu (evidence: the "add branding color token" request → the
    identity-values guideline, committed 560442a; udd-tokens.md + phases/1-specify.md).
  - [ADD · folded] a same-task verify re-cross updates ENGINE_MD5 (774e025 → 3cdfaab) WITHOUT changing the
    `re-aimed @ <slug>` annotation — the slug names the TASK, the md5 names the build (evidence: v3 re-pin).
