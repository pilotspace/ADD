# TASK: Persona Schema Hardening

slug: persona-schema-hardening · created: 2026-07-07 · stage: mvp
milestone: self-improving-loop
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): `add_engine/predicates.py:_persona_missing` (presence-based schema check, PURE/NO-EXEC) · `add_engine/constants.py:PERSONA_FRONTMATTER_KEYS/PERSONA_REQUIRED_SECTIONS` (single source the validator reads) · `add.py:~3133` persona-setup check block (WARN on incomplete, INFO on conformant, measure-not-block)
Context (working folder): `templates/personas/_template.md.tmpl` documents `flow:` values design|build|advisor and (as of a73b4d6) a "sweep bare `<…>` placeholders" discipline — both currently AI-honor-system only, the engine never measures either.
Honors (patterns / conventions): measure-not-block (persona findings are WARN, never a check failure) · PURE/NO-EXEC predicates · constants as single source so schema and validator never drift · `_real_persona_slugs` skips `_`-prefixed files · engine edits re-aim ENGINE_MD5 (add.py) + ENGINE_PKG_MD5 (add_engine) and propagate 3 engine trees byte-identically.
Anchors the contract cites: `_persona_quality_warnings` (new, predicates.py) · `PERSONA_FLOW_VALUES` (new, constants.py) · the add.py persona-setup loop at the `_persona_missing` call site.
Ground SHA: a73b4d6

---

## 1 · SPECIFY — the rules

Feature: persona quality warnings — mechanically measure the two template disciplines the schema check can't see
Must:
  - A new PURE predicate `_persona_quality_warnings(md_text)` returns `[]` for a clean persona, else one human-readable string per finding.
  - Finding A (flow enum): a present `flow:` frontmatter line whose comma-separated values are not all in design|build|advisor yields a finding naming the bad value (a typo'd flow is never loaded by any surface — today it fails silently).
  - Finding B (bare placeholder): a bare `<…>` placeholder outside backtick code spans and outside HTML comments yields a finding (a half-filled template copy passes the presence-based check today).
  - `add.py check` runs the predicate on each REAL persona (non-`_`-prefixed) that already passed the schema check, and emits each finding as a WARN `persona_quality: …` naming the slug; a clean persona keeps its existing `schema-conformant` INFO unchanged.
  - Flow values come from one new constant `PERSONA_FLOW_VALUES = ("design", "build", "advisor")` in constants.py (single source; exported in `__all__`).
Reject:
  - A quality finding treated as a check FAILURE -> never; WARN only ("measure_not_block")
  - Predicate performing file IO / network / process launch -> never; text-in list-out ("no_exec_violation")
  - An absent `flow:` line flagged by Finding A -> never; absence is conformant, `_persona_missing` territory ("absence_is_conformant")
Accept: Given a persona file with `flow: builder` and a body line `- <another concrete capability>`, when `add.py check` runs, then check still counts it as 0 failed but emits two `persona_quality` WARNs (one naming `builder`, one naming the bare placeholder) — and the 6 real dogfood personas produce zero quality WARNs.
Assumptions: ⚠ backtick-span + HTML-comment stripping is enough to avoid false positives on legitimate persona prose (e.g. documented `<persona>` XML tags are always backticked) — why: the 6 dogfood personas grep clean under exactly this stripping; if wrong: a false-positive WARN (noise, never a block), fixed by widening the strip.

---

## 3 · CONTRACT — freeze the shape

```
add_engine/constants.py:
  PERSONA_FLOW_VALUES: tuple[str, ...] = ("design", "build", "advisor")   # + in __all__

add_engine/predicates.py:
  def _persona_quality_warnings(md_text: str) -> list[str]
    # PURE, NO-EXEC. [] == clean.
    # Finding A: "flow value '<v>' not one of design|build|advisor"
    #   (only when a flow: line exists in the leading --- fenced frontmatter)
    # Finding B: "bare <…> placeholder remains: '<first ~40 chars>'"
    #   (scans body + frontmatter with backtick code spans and <!-- … --> comments stripped)

add.py persona-setup block (post-schema, REAL personas only — slug not starting with '_'):
  each finding -> warnings.append((f"persona '{slug}'", f"persona_quality: {finding}"))
  conformant INFO line unchanged; check exit/failed count unchanged (WARN only).
```

`Least-sure flag surfaced at freeze:` [test] the placeholder false-positive surface — HTML-comment stripping must not mask a REAL placeholder that sits inside a commented-out section; cost if wrong: a lazily-filled persona hides one finding (still caught by human review; never blocks).
Status: FROZEN @ v1 — approved by Tin Dang

---

## 4 · TESTS — failing-first (red)

Plan: test_persona_schema_hardening.py — test_flow_typo_warns (Accept: `flow: builder` → finding names 'builder') · test_bare_placeholder_warns · test_backticked_and_commented_are_clean · test_absent_flow_is_clean · test_multi_flow_valid_clean (`design, advisor`) · test_check_emits_warn_not_fail (end-to-end: check counts 0 failed, WARN present) · test_dogfood_personas_zero_quality_warns · test_predicate_pure_no_exec (source inspection: no subprocess/open/network) · test_flow_values_single_source (add.py/predicates reference the constant, no duplicate literal).
Tests live in: `add-method/tooling/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/` `add-method/../.add/tooling/`
Strategy & known-problem fixes: 1. red suite first (import fails = wrong-reason red; assert on behavior after defining a stub? no — red via missing symbol is acceptable ImportError-free by importing add and calling getattr) 2. constants.py PERSONA_FLOW_VALUES (+__all__) 3. predicates.py predicate (strip code spans BEFORE comments? strip comments first, then backticks — a backtick inside a comment is already gone) 4. add.py wiring (REAL personas only) 5. re-aim ENGINE_MD5 (engine_pin.py) + ENGINE_PKG_MD5 6. propagate 3 engine trees + prepare_bundle.py — then restore `_bundled/tooling/engine_pin.py` (prepare_bundle never copies it; regeneration deletes it) 7. green: new suite + test_persona_setup + test_persona_self_improve + test_bundle_parity + test_engine_repin_parity + parity/agents/template/lean sweep + add.py check. Persona stance: methodology-engine-dev (build).
Strategy actually used: as planned, plus ONE mid-build widening inside the frozen shape: Finding B also strips ```-fenced blocks (not just inline spans) — the dogfood Playbook skeletons (`# MILESTONE: <name>`, ADR `<decision title>`) are fenced content, not placeholders; without the fence strip the dogfood-clean test correctly went red. Red run failed for the right reason (missing symbol + missing WARN) before any implementation.
Code lives in: `add-method/tooling/` ·   Constraints: change no test, no contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build (new suite 11/11; persona+parity+pin sweep 46 OK; guard sweep 434 OK; `add.py check` 568 passed / only the expected live-task milestone-completeness failure)
- [x] green was EARNED — red run first failed for the right reason (AttributeError on the missing predicate + missing WARN in check output); dogfood-clean test caught the fence false-positive mid-build
- [x] no exposed secrets, injection openings, or unexpected dependencies (predicate is PURE/NO-EXEC, source-inspected by test_predicate_pure_no_exec; stdlib-only)

Build expectations (from §1 Accept + §3 CONTRACT): `add.py check` on a fixture persona with `flow: builder` + a bare placeholder emits two `persona_quality` WARNs and 0 failures; the 6 dogfood personas emit zero quality WARNs — confirmed by the new suite + a live `add.py check` run.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-07
OBSERVE: [engine · open · persona:methodology-engine-dev · anti-pattern] an engine-self-edit build trips build_tampered at the gate (the judged tree IS the build target) — re-cross tests→build to re-anchor, never revert the honest build (evidence: gate attempt 1 return_to_build on add.py/engine_pin.py, cleared by re-cross)

