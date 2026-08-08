# RESEARCH — udd-catalog-content-schema (json-render alignment, 2026-06-13)

Builds on the source-verified findings in `../udd-token-schema/RESEARCH.md` (json-render
EXISTS, v0.19.0, HEAD `4e4dc46a3738d11daba31c907fb93a7e6565e7bb`). This note pins what THIS
task's contract must align to, and the one clarification that shapes the design.

## The render target — json-render's Spec (a JSON tree we MIRROR)

Verbatim from `packages/core/src/types.ts` @ `4e4dc46`:

```
Spec       = { root: string, elements: Record<id, UIElement>, state?: Record<string,unknown> }
UIElement  = { type: string, props: object, children?: string[],
               visible?: …, on?: Record<event, ActionBinding[]>, repeat?: {statePath,key} }
```

- FLAT: `elements` is an id→element map; `children` are id REFERENCES (not nested). `root` names the entry id.
- `type` = a catalog component name. Catalog-constrained at validate-time via `z.enum(componentNames)`
  (`catalog.validate(spec)`); the runtime renderer warns+null on an uncataloged type (soft).
- Streaming = line-delimited RFC-6902 JSON Patches (not needed for our static foundation).

## The clarification that shapes our design

**json-render has NO JSON catalog format** — a catalog is authored in TypeScript via
`defineCatalog(schema, { components })`, where each component is `{ props: z.object({...}),
hasChildren?, description? }`. It EXPORTS `catalog.jsonSchema()` / `catalog.prompt()` but does not
INGEST a JSON catalog. So:

- our CONTENT TREE mirrors json-render's `Spec` shape EXACTLY → directly render-compatible.
- our CATALOG is OUR compact JSON doc (json-render has none). The RENDER RECIPE is a thin (~20-line)
  adapter that maps `catalog.json` → `defineCatalog(...)` (props → a Zod object). "json-render-aligned"
  = the tree is render-ready as-is; the catalog needs the documented adapter.
- PIN the render target at json-render **v0.19.0 / commit `4e4dc46`** AT THE FREEZE (the milestone's
  named top risk: young-project schema drift). The Spec shape above is what we pin against.

## What this task must add (over task 1's token validator)

- a CATALOG schema: component → { description?, hasChildren?, props: {name: PropSpec} }, where a
  PropSpec is a literal type (string/number/boolean/enum) OR a token-binding (the prop value, in a tree,
  must cite a SEMANTIC token of a named `$type`) — this extends task 1's citation rule to component props.
- a CONTENT-TREE schema = json-render's flat Spec, catalog-constrained.
- a validator `_catalog_tree_violations(catalog, tree)` → list[(code, path, detail)], fail-closed, pure,
  stdlib — SEPARATE from task 1's `_token_layer_violations` (udd-check-lint composes both). The milestone
  names `tree-cites-uncataloged-component`; the natural fail-closed set adds unknown_prop ·
  prop_type_mismatch · non_semantic_prop_token · dangling_child · children_not_allowed · missing_root.
- a SAMPLE catalog + prototype tree that validate clean and render via the recipe.

## Foundation-shape decision (this task OWNS it — a freeze fork)

The milestone's shared/risky contract: "the foundation JSON shape (token layers + catalog + content
trees, one file OR a named set)." → Fork at the freeze: ONE `foundation.json` vs a NAMED SET
(`tokens.json` · `catalog.json` · `prototypes/<name>.json`). Recommendation leans named-set (mirrors
json-render's catalog/spec separation; each file lints independently) — but it is a genuine fork.
