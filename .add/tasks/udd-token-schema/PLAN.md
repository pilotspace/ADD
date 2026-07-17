# TASK: UDD token layers — DTCG-aligned compact dialect, 3 layers, the citation rule

slug: udd-token-schema · created: 2026-06-13 · stage: mvp
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
  - `add-method/tooling/add.py` — the home for a NEW pure validator `_token_layer_violations(tokens: dict)
    -> list[(code, path, detail)]` (the testable artifact this task ships). It reads a parsed tokens dict and
    returns layer/alias/citation violations. NOT wired into `cmd_check` here — that integration + named reds
    is the downstream task udd-check-lint (boundary fork, see §3). ×3 engine mirrors stay byte-identical.
  - `add-method/tooling/add.py:_templates_dir()` (L148) → `templates/`; `_render_template(name, **subs)`
    (L152) loads `templates/<name>.tmpl` + substitutes `{{key}}`. A SAMPLE tokens file ships here as a
    template/asset (×3 mirrors — `test_bundle_parity`).
  - `add-method/tooling/add.py:cmd_check` (L1109) — builds `checks: list[(ok, desc, reason)]`, exits 1 on any
    false. The SEAM udd-check-lint will append the token/catalog reds to; this task only supplies the function
    it will call. Named here so the boundary is explicit, NOT touched.
Context (working folder):
  - `.add/tasks/udd-token-schema/RESEARCH.md` — source-verified DTCG 2025.10 + json-render facts (fetched
    live, URLs + pinned commit `4e4dc46`). The §3 dialect decisions cite it; read it before the freeze.
  - templates dir today: CONVENTIONS · dependencies.allowlist · GLOSSARY · MILESTONE · MODEL_REGISTRY ·
    PROJECT · TASK (all `.tmpl`). The token sample is a NEW asset alongside these.
Honors (patterns / conventions):
  - milestone shared decisions (every task honors): the 3-layer citation rule (component→semantic→primitive,
    fail-closed); JSON = AI-economy dialect (compact, DTCG-compatible where free, divergences NAMED); the
    engine lints SHAPE only (stdlib, tool-agnostic); pin json-render to a NAMED version at the catalog freeze.
  - ADDITIVE + ×3 mirror parity (`test_bundle_parity`): a new template asset lands byte-identical in all three
    template trees; the validator lands byte-identical in all three add.py mirrors.
  - the [SDD] grounding-inline rule (delta from next-step-seams): keep the Anchors line INLINE (below).
Anchors the contract cites: `_token_layer_violations(tokens)->list[(code,path,detail)]` (the NEW validator) · the compact-DTCG dialect from RESEARCH.md (DTCG 2025.10 Final CG Report — `$value`/`$type`/`{alias}` kept; color+dimension scalar divergences NAMED) · the 3-layer top-level groups `primitive`/`semantic`/`component` + the citation rule · the SAMPLE tokens file in `templates/` · `cmd_check` (the downstream wiring seam, named-not-touched) · `test_bundle_parity` (the ×3 guard).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: the compact-DTCG token dialect — a 3-layer (primitive · semantic · component) token format,
DTCG 2025.10-aligned but compacted for the AI economy, with a fail-closed citation rule; plus a pure
stdlib validator `_token_layer_violations(tokens)` that a shipped SAMPLE tokens file passes clean.

Framings weighed: compact-dialect+validator (chosen) · faithful-DTCG-verbatim · doc-and-sample-only.
  - CHOSEN compact-dialect+validator: keep DTCG's `$value`/`$type`/`{alias}`/group model, but DIVERGE
    to SCALAR value forms (hex string for color, `"16px"` string for dimension) for AI-economy compactness
    — each divergence NAMED against DTCG 2025.10 (RESEARCH.md). Ship a pure validator function THIS task;
    udd-check-lint later wires it into `cmd_check` with named reds + adds the catalog/tree rules.
  - faithful-DTCG-verbatim: keep DTCG 2025.10 value OBJECTS exactly (`color`={colorSpace,components,…},
    `dimension`={value,unit}). Max interop, zero NAMED divergence — but heavier tokens, against the
    milestone's "AI-economy dialect" decision. (Fork B, §3.)
  - doc-and-sample-only: ship just the dialect doc + sample, defer ALL validation to udd-check-lint. But
    then "a sample file VALIDATES the citation rules" has no red→green artifact in THIS task. (Fork A, §3.)

Must:
<must>
  - THREE layers, as top-level groups: `primitive`, `semantic`, `component`. A token's LAYER = its
    top-level group name. (Convention layered on DTCG groups — NOT a DTCG feature; RESEARCH.md.)
  - DTCG keys kept: `$value` (required on a token), `$type` (optional; inherits from the nearest parent
    group with `$type`), `$description` (optional). A GROUP is any object without `$value`.
  - ALIAS = `{layer.path.to.token}` curly-brace string as a `$value` (DTCG syntax); chains allowed; never
    circular. Resolves to the target token's `$value`.
  - THE CITATION RULE (fail-closed, the milestone's core invariant):
      · a `primitive` token's `$value` MUST be a literal (no alias).
      · a `semantic`  token's `$value` MUST be a literal OR an alias to a `primitive` token only.
      · a `component` token's `$value` MUST be a literal OR an alias to a `semantic` token only.
    No layer-skipping, no upward/sideways citation.
  - COMPACT value forms (NAMED divergences from DTCG 2025.10): `color` = hex string `"#RRGGBB"`/`"#RRGGBBAA"`
    (DTCG: object); `dimension` = `"<number><unit>"` e.g. `"16px"`/`"1rem"` (DTCG: {value,unit}); `number`,
    `fontWeight`, `duration`, `fontFamily` = DTCG-compatible scalars/array.
  - SUPPORTED `$type` set (MVP): color · dimension · number · fontFamily · fontWeight · duration. (Composites
    shadow/typography/border DEFERRED — additive later; cubicBezier/strokeStyle/gradient/transition dropped.)
  - `_token_layer_violations(tokens: dict) -> list[(code, path, detail)]` — pure, stdlib, deterministic
    order; `[]` == valid. The codes are the token-layer named reds udd-check-lint will surface.
  - A SAMPLE tokens file ships in `templates/` exercising all 3 layers + the citation rule, and
    `_token_layer_violations(sample) == []`.
</must>
Reject:
<reject>
  - a token under an unknown top-level group (not primitive/semantic/component) -> "unknown_layer"
  - a `$type` outside the supported set -> "unknown_type"
  - an alias `{…}` resolving to no existing token -> "unresolved_alias"
  - a citation that skips or inverts a layer (component→primitive, semantic→component, any →same/up) -> "cross_layer_citation"
  - a `primitive` token whose `$value` is an alias -> "primitive_has_alias"
  - a `$value` whose form doesn't match its `$type` (color not hex, dimension not `<n><unit>`) -> "malformed_value"
</reject>
After:
<after>
  - the dialect is documented with every divergence NAMED + DTCG 2025.10 cited (the pinned dated URL).
  - the shipped sample validates clean: `_token_layer_violations(sample) == []`.
  - `_token_layer_violations` is pure stdlib and NOT yet wired into `cmd_check` (that is udd-check-lint).
  - ×3 mirrors byte-identical (validator in add.py; sample in templates/).
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ THE COMPACTION STANCE (Fork B) — that we SHOULD diverge from DTCG's value OBJECTS to SCALAR forms
    (hex / "16px") for the AI economy. Lowest confidence because it trades DTCG interop for compactness, and
    a future token→CSS/render step (json-render is React-prop-based, not token-aware) may prefer DTCG-object
    color. If wrong: re-freeze the dialect + rewrite sample & validator value-checks (contained to this task).
  - [ ] THE BOUNDARY (Fork A) — that THIS task ships the validator FUNCTION and udd-check-lint only wires it
    into `cmd_check` + adds catalog/tree rules. If wrong (defer all validation): this task ships doc+sample
    only; "validates" becomes a structural test; check-lint owns the function. Confirm at the freeze.
  - [ ] LAYER-BY-GROUP (Fork C) — that a token's layer is its top-level group name, not a per-token `$layer`
    key. If wrong: add a marker key (small, additive).
  - [ ] the MVP `$type` subset (6 scalars, composites deferred) is enough for a first render-ready foundation.
    If wrong: add types later (additive, low cost).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the shipped sample validates clean (the exit criterion)
  Given the sample tokens file shipped in templates/ (all 3 layers, valid citations)
  When _token_layer_violations(sample) runs
  Then it returns [] (no violations)

Scenario: a valid semantic→primitive citation passes
  Given a semantic color token whose $value aliases a primitive color token
  When _token_layer_violations runs
  Then no violation is reported for that token

Scenario: a valid component→semantic citation passes
  Given a component token whose $value aliases a semantic token
  When _token_layer_violations runs
  Then no violation is reported for that token

Scenario: chained + literal primitives validate
  Given a component→semantic→primitive chain ending in a literal hex primitive
  When _token_layer_violations runs
  Then it returns [] (chains to a literal resolve)

Scenario: unknown layer is rejected
  Given a token under a top-level group "foundation" (not primitive/semantic/component)
  When _token_layer_violations runs
  Then a ("unknown_layer", path, detail) violation is returned
  And tokens under the valid layers report no violation (pure, isolated)

Scenario: unsupported $type is rejected
  Given a token with $type "elevation" (outside the supported set)
  When _token_layer_violations runs
  Then a ("unknown_type", path, detail) violation is returned
  And the input tokens dict is not mutated

Scenario: dangling alias is rejected
  Given a semantic token aliasing {primitive.color.missing} which does not exist
  When _token_layer_violations runs
  Then an ("unresolved_alias", path, detail) violation is returned
  And valid tokens in the same file report no violation

Scenario: layer-skipping citation is rejected
  Given a component token whose $value aliases a primitive token directly (skips semantic)
  When _token_layer_violations runs
  Then a ("cross_layer_citation", path, detail) violation is returned
  And the cited primitive token itself reports no violation

Scenario: a primitive holding an alias is rejected
  Given a primitive token whose $value is "{primitive.color.base}" (an alias, not a literal)
  When _token_layer_violations runs
  Then a ("primitive_has_alias", path, detail) violation is returned
  And the input tokens dict is not mutated

Scenario: a value whose form mismatches its $type is rejected
  Given a primitive color token whose $value is "blue" (not a #hex string)
  When _token_layer_violations runs
  Then a ("malformed_value", path, detail) violation is returned
  And a sibling primitive color token with a valid #hex reports no violation
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
fn _token_layer_violations(tokens: dict) -> list[tuple[str, str, str]]
  []                      -> tokens are valid
  [(code, path, detail)…] -> one tuple per violation, in deterministic document order
                             (depth-first, key order as written)
  PURE: never mutates `tokens`; stdlib only; no I/O. (Parsing JSON → dict is the caller's job.)

  codes  (the token-layer named reds; udd-check-lint surfaces them inside cmd_check):
    "unknown_layer"        top-level group ∉ {primitive, semantic, component}
    "unknown_type"         resolved $type ∉ {color, dimension, number, fontFamily, fontWeight, duration}
    "unresolved_alias"     "{a.b.c}" resolves to no token bearing a $value
    "cross_layer_citation" primitive may not alias · semantic→primitive ONLY · component→semantic ONLY
    "primitive_has_alias"  a primitive token's $value is an alias (must be a literal)
    "malformed_value"      $value form mismatches resolved $type (color≠#hex · dimension≠"<n><unit>")

DIALECT  (the frozen shape; divergences from DTCG 2025.10 Final CG Report are NAMED — RESEARCH.md):
  token  = object WITH "$value" (required); optional "$type", "$description"
  group  = object WITHOUT "$value"; optional "$type" (inherited by descendants)
  layer  = top-level group name ∈ {primitive, semantic, component}   (Fork C: layer = group name)
  alias  = "{layer.dotted.path}" string used as a $value  (DTCG curly syntax; chains; never circular)
  color      $value = "#RRGGBB" | "#RRGGBBAA"                      [DIVERGES from DTCG object form]
  dimension  $value = "<number><unit>", unit ∈ {px,rem,em,%,vh,vw} [DIVERGES from DTCG {value,unit}]
  number     $value = JSON number
  fontWeight $value = JSON number 100..900 | keyword string
  duration   $value = "<number>ms" | "<number>s"
  fontFamily $value = string | [string, …]

SAMPLE: templates/tokens.sample.json — all 3 layers + a valid component→semantic→primitive chain;
        _token_layer_violations(parse(sample)) == [].   (×3 mirrors byte-identical, test_bundle_parity)

BOUNDARY (Fork A): THIS task ships _token_layer_violations + tokens.sample.json + the dialect doc.
        udd-check-lint LATER calls this fn inside cmd_check (named reds) and ADDS the catalog/tree rules.
        cmd_check is NAMED-not-touched here.

Files touched (→ §5 scope): add.py (+2 mirrors) new _token_layer_violations · templates/tokens.sample.json
        (+2 mirrors) · the dialect doc (a templates/-adjacent reference; exact path settled at build).
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-13.
  Fork resolutions (the freeze answers): B = COMPACT SCALARS (hex/`"16px"`; divergences from DTCG
  2025.10 NAMED) · A = SHIP THE VALIDATOR HERE (udd-check-lint later wires it into cmd_check + adds
  catalog/tree rules) · C = LAYER = TOP-LEVEL GROUP NAME (no per-token `$layer` key). All recommended
  defaults; the draft stands unchanged. Changing this contract now = a change request back to SPECIFY.
Least-sure flag surfaced at freeze: [contract] THE COMPACTION STANCE (Fork B) — diverging to SCALAR value
  forms (color `"#3B82F6"`, dimension `"16px"`) instead of DTCG 2025.10's value OBJECTS. Lowest-confidence
  because it trades DTCG interop for AI-economy compactness; a future token→CSS step (not json-render, which
  is React-prop-based) could prefer object color. Resolved at the freeze → COMPACT SCALARS (human-approved).
  Cost if wrong: re-freeze the dialect + rewrite the sample & the value-form checks — CONTAINED to this task
  (§2 scenarios + §4 tests target the citation BEHAVIOR + the named codes, which are stance-independent, so
  the layer/alias logic is not thrown away). Biggest residual risk: the value-form regexes (#hex / `<n><unit>`)
  are a judgment call on strictness, not a testable invariant beyond the cases enumerated in §2.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 90% (the validator + the shipped sample)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_sample_validates_clean: parse templates/tokens.sample.json → assert _token_layer_violations(sample) == []
  - test_semantic_cites_primitive_ok / test_component_cites_semantic_ok / test_full_chain_to_literal_ok:
      arrange a valid citation → assert no violation for that token
  - test_unknown_layer: token under "foundation" → assert ("unknown_layer", path, _) present; valid layers clean
  - test_unknown_type: $type "elevation" → assert ("unknown_type", …); assert input dict not mutated
  - test_unresolved_alias: {primitive.color.missing} → assert ("unresolved_alias", …); other tokens clean
  - test_cross_layer_citation: component→primitive (skips semantic) → assert ("cross_layer_citation", …)
  - test_primitive_has_alias: primitive $value is an alias → assert ("primitive_has_alias", …); not mutated
  - test_malformed_value: color $value "blue" → assert ("malformed_value", …); valid #hex sibling clean
  - test_violations_are_pure_and_ordered: same input twice → identical list; deep-copy equality of input pre/post
  - test_parity_sample_and_doc_mirrored: tokens.sample.json + udd-tokens.md byte-identical across the ×3 trees
  - test_pin_annotation_names_this_task: engine_pin.py records "re-aimed @ udd-token-schema" + carries the prior
      "re-aimed @ gate-owner-marker" (the pin idiom self-test — in the red suite FROM GROUND, per the RETRO delta)
</test_plan>

Tests live in: `add-method/tooling/test_udd_token_schema.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `.add/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/templates/tokens.sample.json` `add-method/src/add_method/_bundled/tooling/templates/tokens.sample.json` `.add/tooling/templates/tokens.sample.json` `add-method/tooling/templates/udd-tokens.md` `add-method/src/add_method/_bundled/tooling/templates/udd-tokens.md` `.add/tooling/templates/udd-tokens.md` `add-method/tooling/test_udd_token_schema.py`
Strategy (ordered batches): 1. red suite + the sample fixture → red for the right reason. 2. `_token_layer_violations` in canonical add.py → canonical green. 3. mirror add.py ×2 + re-pin engine_pin.py (`re-aimed @ udd-token-schema`, carry `gate-owner-marker`) + ship tokens.sample.json ×3 + udd-tokens.md ×3 → parity green. 4. pin self-test green.
Safety rule (feature-specific): the validator is PURE — never mutates `tokens`, no I/O, stdlib only; deterministic violation order (depth-first, key order); fail-CLOSED (an unrecognized shape yields a named violation, never a silent pass). Note: `.add/tooling/*` mirrors are updated for tree-parity but lie OUTSIDE the scope-gate walk (.add is excluded) — listed for honesty.
Code lives in: `add-method/tooling/add.py` (the engine; the validator is a pure helper, NOT yet wired into cmd_check).
Constraints: do NOT change any test or the contract; allow-list packages only (stdlib only here); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite **946** on python3.14 + python3.10 (both `OK`, 0 fail/0 error); was 932 → +14 (13 §2/§4 scenarios + the refute gap guard). `add.py check` 295 passed / 0 failed (13 pre-existing WARNs, none udd-token-schema; the §0 anchors were inlined so no task_not_grounded).
- [x] coverage did not decrease — +14 tests, nothing removed; `test_bundle_parity` + `test_tree_parity` stay green (the new sample + doc + add.py land byte-identical in all 3 trees).
- [x] no test or contract was altered during build — §3 FROZEN @ v1 unchanged (the 6 codes + the dialect); the gap guard was added by a CLEAN re-cross (verify→tests→build→verify; reopen, add the guard RED, re-baseline the tests-snapshot, fix, re-cross) — never an in-build test edit. No frozen test weakened.
- [x] the green was EARNED — adversarial refute-read (python-expert subagent, Rule 5) FOUND a real **fail-OPEN gap**: a node with `$value` AND non-`$` children skipped its subtree, so malformed nested tokens passed silently — a breach of the milestone's fail-closed invariant. CLOSED before the gate (close-gap-before-gate): `_index`/`_walk` now ALWAYS descend; `test_nested_token_children_are_validated` guards it. The refute confirmed PURITY (input never mutated) + DETERMINISM hold and the suite is NOT overfit (each code asserted with a named path). Residual refute findings are DEFENSIBLE under-specs of the frozen dialect (fontWeight accepts any keyword string; weight floats rejected; negative dimensions allowed) → recorded as §7 deltas, not gate-blockers.
- [x] concurrency / timing — N/A: a pure stdlib function over an in-memory dict; no shared mutable state, no I/O, no ordering hazard.
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only (`re`); no new dependency; reads a parsed dict, writes nothing; no eval/exec/format-injection surface.
- [x] layering & dependencies follow conventions — the validator is a PURE helper in add.py, NOT wired into `cmd_check` (Fork A boundary, human-approved at the freeze — udd-check-lint wires it later); ×3 add.py mirrors byte-identical (md5 `c107344`); engine_pin re-aimed @ udd-token-schema with the prior carry-chain preserved (every earlier pin self-test still green).
- [x] a person reviewed and approved the change — AUTO-RESOLVED under `autonomy: auto`: an explicit PASS, not a skip. No human gate required — no security surface, no concurrency/architecture residue, the dial is auto (not lowered), and the one finding (the fail-open gap) was CLOSED, not residual. The change touches the ENGINE (add.py) but NOT the human-owned foundation (`.add/PROJECT.md`). Surfaced to the human in full (the refute → gap → closure → deferred weaknesses) for visibility.

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_token_layer_violations` + `_token_value_form_ok` are referenced by `test_udd_token_schema.py` (14 tests) and documented in `templates/udd-tokens.md`. The `cmd_check` wiring is DELIBERATELY deferred to udd-check-lint by the frozen Fork-A boundary (named in §3 + the engine_pin annotation) — a reserved seam, not an orphan.
- [x] DEAD-CODE (code) — `_token_value_form_ok` is called by `_token_layer_violations`, which is called by the suite; no unused/orphaned symbol. The not-yet-wired-into-cmd_check state is intentional + documented (Fork A).
- [x] SEMANTIC (prose) — read in full: `templates/udd-tokens.md` (the NAMED divergences match the validator's ACTUAL forms — color #hex, dimension `<n><unit>`, the 6 codes; DTCG 2025.10 cited with the dated stable URL) and `templates/tokens.sample.json` (3 layers + a valid component→semantic→primitive chain; validates clean). RESEARCH.md cross-checked: the dialect claims trace to fetched sources.

### GATE RECORD
Outcome: PASS
Reviewed by: AI auto-gate (autonomy=auto) · date: 2026-06-13   (adversarial refute run + gap closed before the gate; surfaced to Tin Dang)

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): `_token_layer_violations(parse(templates/tokens.sample.json)) == []` stays green (the shipped sample never drifts from the dialect); as real projects author tokens, track which of the 6 codes fire most (the per-rejection rate) to spot dialect friction.
Spec delta for the next loop: the validator is ready for udd-check-lint to WIRE into `cmd_check` (named reds) and for udd-catalog-content-schema to EXTEND with the catalog + flat-tree rules. Pin json-render @ v0.19.0 / commit `4e4dc46` at the catalog freeze (RESEARCH.md). The 3-layer + alias model is the citation backbone the catalog's component→token references must also honor.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [TDD · folded] the verify-gate adversarial refute earns its keep on a TRAVERSAL validator — 10 behavior scenarios all passed yet missed a fail-OPEN gap (a `$value` node with non-`$` children skipped its whole subtree, so malformed nested tokens passed silently); a recursive validator's red suite needs a "never skip a subtree / no phantom children" probe FROM GROUND, not discovered at verify (evidence: the python-expert refute reproduced it on a nested malformed child; closed via reopen→tests→build→verify re-cross; `test_nested_token_children_are_validated` + `_index`/`_walk` now always descend; md5 8329cd4→c107344)
- [SDD · folded] "a token = object with `$value`; a group = object without `$value`" left token LEAF-ness IMPLIED, not stated — the gap existed precisely because the frozen §1 never said "a token is a leaf (no child tokens)"; future schema tasks (catalog/tree) should state structural leaf/containment rules explicitly so the validator isn't the only place the invariant lives (evidence: the fail-open gap was an under-specified structural case, resolved by the fail-closed principle at verify, not by a frozen rule)
- [UDD · folded] the compact dialect's value-form STRICTNESS is under-pinned in three spots the frozen contract did not nail: `fontWeight` accepts ANY string as a "keyword" (no enumerated set), weight FLOATS like `700.0` are rejected, and NEGATIVE dimensions like `"-16px"` pass — all defensible for MVP but a real renderer would reject some; tighten in a follow-up if real token files hit them (evidence: refute WEAKNESSES 1-3, classified non-blocking; deferred rather than change-requested against the frozen v1)
