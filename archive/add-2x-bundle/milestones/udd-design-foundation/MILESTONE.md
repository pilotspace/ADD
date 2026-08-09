# MILESTONE: Udd Design Foundation

goal: a UI project gets a render-ready UDD foundation the AI drafts from and into — DESIGN.md plus a JSON foundation (token layers + component catalog + prototype content trees) that a json-render-style renderer displays as a living design system and clickable prototype, and that add.py check lints
rationale: new-major (human-confirmed intake 2026-06-11; render-ready adjustment human-confirmed 2026-06-12) — UDD is the foundation pillar with no artifact today; a DESIGN.md-style template + guarded JSON gives the AI a frozen design ground to draft UI from (faster, cheaper, render-previewable) instead of ad-hoc styling
stage: mvp · status: active · created: 2026-06-12

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  DTCG-aligned compact token schema (primitive → semantic → component; `$value`/`$type`, `{path}` aliases — DTCG stable v2025.10); a component CATALOG (typed props, semantic-token refs only — the json-render guardrail model); prototype CONTENT TREES (flat element trees citing only catalog entries, json-render-compatible, streaming-friendly); a DESIGN.md template wired into the 0-setup foundation flow; stdlib `add.py check` lint; a documented render recipe (point json-render at the foundation)
Out: building/bundling the renderer itself · fixture app · Figma/tooling sync · runtime CSS emit

## Shared decisions & glossary deltas   (living — every task must honor these)
- the 3-layer citation rule: components cite ONLY semantic tokens; semantic cite ONLY primitive; a content tree cites ONLY cataloged components — every violation is a named lint red (fail-closed)
- JSON is the AI-economy dialect: compact keys, DTCG-compatible where it costs nothing, divergences NAMED in the schema doc — never silent
- the engine lints SHAPE only (stdlib, tool-agnostic); rendering happens outside the engine via the documented recipe
- pin the json-render schema to a NAMED version at the catalog freeze (young project — drift is the top risk)

## Shared / risky contracts (freeze these first)
- the foundation JSON shape (token layers + catalog + content trees, one file or a named set) -> owning task udd-catalog-content-schema
- the compact-DTCG dialect (what we keep, what we drop, named divergences) -> owning task udd-token-schema

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] udd-token-schema            depends-on: none                       — the token layers: DTCG-aligned but compact; 3 layers; the citation rule
- [ ] udd-catalog-content-schema  depends-on: udd-token-schema           — the render-ready half: component catalog (props + semantic refs) + flat prototype trees, json-render-aligned
- [ ] udd-design-template         depends-on: udd-catalog-content-schema — DESIGN.md template binding prose + tokens + catalog + prototypes into 0-setup, with the render recipe
- [ ] udd-check-lint              depends-on: udd-catalog-content-schema — check: unresolved alias · component-cites-primitive · tree-cites-uncataloged-component · unknown $type → named reds

## Exit criteria (observable; map each to the task that delivers it)
- [x] A sample tokens file validates the 3-layer citation rules (← udd-token-schema) (verify: test_udd_token_schema.py::test_sample_validates_clean)
- [x] A sample prototype tree validates catalog-constrained and renders via the documented recipe (← udd-catalog-content-schema) (verify: test_udd_catalog_content_schema.py::test_sample_validates_clean + udd-catalog.md "## Render recipe")
- [x] 0-setup on a UI project drafts DESIGN.md from the template (← udd-design-template) (verify: test_udd_design_template.py::test_init_drafts_nonblank_design)
- [x] `add.py check` goes red, with a named code, on a layer or catalog violation (← udd-check-lint) (verify: test_udd_check_lint.py::test_token_layer_violation_red + test_catalog_tree_violation_red)
