# MILESTONE: Trim the §3 Build-strategy block

goal: Keep the enforced Scope line (relabel: it is HARD scope-lock, currently mislabeled SOFT); make Regression floor + Persona implicit/optional. Template + _FALLBACK_TASK + guides + conformance tests, retire-in-place.
stage: mvp · status: active · created: 2026-07-23T05:32:30+00:00 · lane: tiny
release: pending

> Tiny plan — small scope, one approval. Keep it to a handful of lines; if it
> outgrows this shape, recreate without --tiny (the full SDD scaffold).

## Plan
- [x] trim-build-strategy-labels — relabel §3 Build-strategy (Scope HARD; Strategy/Approach/Regression/Persona SOFT-optional) across 4 PLAN.md.tmpl twins + `_PLAN_FIELDS`/`_build_plan`, with backward-compat + conformance suite (PASS 2026-07-23)

## Done when
- [x] PLAN.md.tmpl §3 header names `Scope (may touch)` as the HARD scope-lock; the rest reads SOFT/optional — verifier: test_build_strategy_labels.test_header_marks_scope_hard
- [x] `Persona (required):` → `Persona (optional):` across all 4 template twins; freeze digest still surfaces Persona for legacy tasks — verifier: test_build_strategy_labels.test_persona_label_is_optional + test_legacy_persona_still_surfaces
- [x] machine-read `Scope (may touch):` / `Regression floor:` prefixes preserved verbatim (scope-lock + inherited-floors census intact) — verifier: test_build_strategy_labels.test_scope_and_regression_prefixes_preserved + test_template_atomic
- [x] `_FALLBACK_TASK` + guides confirmed already consistent (no SOFT-mislabel, no required-Persona) — no change needed; verified by grep
- [x] full tooling suite green, twins byte-identical, ENGINE_MD5 repinned — verifier: full suite 2253/0 + test_build_strategy_labels.test_template_twins_byte_identical
