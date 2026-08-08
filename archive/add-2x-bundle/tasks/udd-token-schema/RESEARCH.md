# RESEARCH — udd-token-schema (source-verified 2026-06-13)

Two subagents fetched live sources (not training recall) per the verify-from-source mandate.
This is the evidence trail behind the §3 contract. Pin these; do not re-derive from memory.

## DTCG (Design Tokens Format Module) — VERIFIED

- **Real version: `2025.10`** — "Design Tokens Format Module 2025.10", published **28 Oct 2025**.
  - Canonical stable URL: https://www.designtokens.org/tr/2025.10/format/  ← PIN THIS
  - Status: **"Final Community Group Report"** (a W3C Community Group publication, NOT a W3C
    Recommendation). The spec prose says "This specification is considered stable."
  - ⚠ DIVERGENCE #1 (label): the milestone calls it "stable v2025.10". Accurate in substance
    (2025.10 is the stable release) but the FORMAL label is "Final Community Group Report".
    Cite as "DTCG Format Module 2025.10 (Final Community Group Report)".
  - ⚠ TRAP: `https://tr.designtokens.org/format/` redirects to a PREVIEW DRAFT ("do not
    implement anything in this document"). NEVER pin there. Use the dated 2025.10 URL.

- **Token shape:** `$value` (required), `$type` (optional; inherits from nearest parent group
  with `$type`), `$description` (optional), `$extensions` (optional), `$deprecated` (optional).
- **`$type` values (exact):** color · dimension · fontFamily · fontWeight · duration ·
  cubicBezier · number · strokeStyle · border · transition · shadow · gradient · typography.
- **Group:** any JSON object lacking `$value`. Token/group names MUST NOT start with `$` or
  contain `{`, `}`, `.`.
- **Aliases:** `{group.token}` curly-brace syntax as a `$value`; resolves to the target's
  `$value`; aliases MAY chain; MUST NOT be circular. (A `$ref` JSON-Pointer form also exists but
  is heavier / partly draft — DROP for our dialect.)
- **color `$value` is an OBJECT:** `{colorSpace, components:[...], alpha?, hex?}` — NOT a bare
  hex string. (Compaction-divergence candidate.)
- **dimension `$value` is an OBJECT:** `{value, unit}` (e.g. `{value:0.5, unit:"rem"}`).
- ⚠ **TIERS ARE NOT IN THE SPEC.** primitive → semantic → component is a COMMUNITY CONVENTION
  layered on groups + aliases. The DTCG glossary has no "primitive/semantic/component token"
  entries. Our 3-layer citation rule is OURS — name it as our convention, not a DTCG feature.

## vercel-labs/json-render — VERIFIED (anchors the NEXT task, udd-catalog-content-schema)

- **Exists.** https://github.com/vercel-labs/json-render — "The Generative UI framework",
  Apache-2.0, ~15k stars. Latest release **v0.19.0** (2026-05-12). HEAD commit
  **`4e4dc46a3738d11daba31c907fb93a7e6565e7bb`**. ← PIN a tag/commit at the catalog freeze.
- **Catalog:** `defineCatalog(schema, { components, actions })`; each component
  `{ props: z.object({...}), hasChildren?, description? }`.
- **Content tree (FLAT):** `Spec = { root: string, elements: Record<id, UIElement>, state? }`;
  `UIElement = { type, props, children?: string[], visible?, on?, repeat? }`. Children are ID
  references (flat adjacency), not inline nesting. `nestedToFlat()` exists for human authoring.
- **Catalog-constrained:** `z.enum(componentNames)` on `type` (hard, via `catalog.validate`);
  runtime renderer warns+null on uncataloged type (soft).
- **Streaming:** SpecStream = line-delimited RFC-6902 JSON Patches; `createSpecStreamCompiler`.

## Codebase wiring (the seams, from add.py — GROUND, not research)

- `_templates_dir()` → `add-method/tooling/templates/` (×3 mirrors: canonical · `_bundled` ·
  dogfood `.add/`). `_render_template(name, **subs)` loads `<name>.tmpl`, substitutes `{{key}}`.
  A new sample/template file lands here (×3 byte-identical, `test_bundle_parity`).
- `cmd_check` builds `checks: list[(ok, description, reason)]` and exits 1 on any false. This is
  the seam **udd-check-lint** wires the named token/catalog reds into — NOT this task.
</content>
