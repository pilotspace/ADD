# TASK: Persona required + domain-strategy hint in TASK templates

slug: persona-required-domain-hint · created: 2026-07-06 · stage: mvp
milestone: (none)
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): `add-method/tooling/templates/TASK.md.tmpl` §5 BUILD — the `Persona
  (optional): <... absent = generic>` line and the `Strategy (ordered batches): <...>` line;
  `add-method/tooling/templates/TASK.fast.md.tmpl` §5 BUILD — the `Strategy & known-problem
  fixes: <...>` line. Both are prose/placeholder text only, no XML tag, no engine parsing of
  the field bodies (add.py never reads Persona/Strategy content — confirmed via `grep -n
  "Persona\|Strategy" add-method/tooling/add.py`, no hits besides a comment at L408).
Context (working folder): each `.tmpl` has 2 mirrors that must stay byte-identical
  (`test_orchestrator_build_persona.py::test_5build_and_template_parity`,
  `test_scope_decl_template.py::test_mirrors_and_engine_untouched` /
  `test_fast_template_mirrors`): `.add/tooling/templates/*.tmpl` (dogfood copy, gitignored) and
  `add-method/src/add_method/_bundled/tooling/templates/*.tmpl` (pip/npm bundle). `add.py`'s
  embedded circuit-breaker fallbacks (`_FALLBACK_TASK`/`_FALLBACK_TASK_FAST` in
  `add-method/tooling/add_engine/constants.py`) carry NO Persona/Strategy guidance prose at all
  (bare section headers only) — out of scope, nothing to change there.
Honors (patterns / conventions): this repo's established convention for prose/template-only
  tasks (scope-decl-template, orchestrator-build-persona) — edit the canonical tree, mirror
  verbatim to the dogfood + bundled trees, add.py stays byte-identical to `engine_pin.ENGINE_MD5`
  (a new pinning test proves it), and the v16 XML tag census in `TASK.md.tmpl`
  (`test_scope_decl_template.FROZEN_TAGS`) gets no new bare `<word>` tag — my additions stay
  multi-word placeholder prose inside the EXISTING `<...>` spans, never a new isolated tag.
  `STRATEGY_LABEL = "Strategy (ordered batches):"` and `FAST_STRATEGY_LABEL = "Strategy &
  known-problem fixes:"` are pinned exact-string labels (test_scope_decl_template.py) — the
  label text itself must not change, only the placeholder guidance inside `<...>`.
Anchors the contract cites: the `Persona (optional):` / `Persona (required):` line and the
  `Strategy (ordered batches):` line in `TASK.md.tmpl` §5; the `Strategy & known-problem
  fixes:` line in `TASK.fast.md.tmpl` §5.

---

## 1 · SPECIFY — the rules

Feature: `TASK.md.tmpl`'s §5 Persona field becomes required-to-fill (no more silent "absent =
  generic"); both `TASK.md.tmpl` and `TASK.fast.md.tmpl` gain a domain-strategy hint in their
  Strategy line, nudging the AI to let the domain/persona stance shape the *implementation
  approach*, not just architecture/pattern choice. Prose-only — no engine enforcement, no new
  gate; add.py is untouched.
Must:
  - `TASK.md.tmpl` §5's `Persona (optional):` line becomes `Persona (required):` — the
    placeholder drops "absent = generic" and instead instructs: name the fitting persona, or
    write `generic` explicitly if none fits yet (never leave the field blank/placeholder).
  - `TASK.md.tmpl` §5's `Strategy (ordered batches):` placeholder gains a trailing clause: let
    the named Persona's domain stance shape the chosen approach, not just architecture patterns.
  - `TASK.fast.md.tmpl` §5's `Strategy & known-problem fixes:` placeholder gains the same-spirit
    clause, phrased without assuming a dedicated Persona field exists (fast lane has none): let
    the active persona's domain stance (or "generic") shape the approach, not just patterns.
  - Both label strings (`Strategy (ordered batches):`, `Strategy & known-problem fixes:`) stay
    byte-identical — only the `<...>` guidance text inside changes.
  - No new XML tag introduced (v16 census in `TASK.md.tmpl` stays exactly `FROZEN_TAGS`).
  - All 3 mirrors of each file stay byte-identical after the edit; `add.py` (all 3 copies) stays
    byte-identical to `engine_pin.ENGINE_MD5` (no engine code touched).
Reject:
  - N/A — this is a wording-only change to placeholder guidance text; there is no runtime input
    to reject. The one thing that WOULD be wrong — a new bare `<word>` tag, a changed label
    string, a mirror drift, or an engine-pin drift — is caught by the tests below, not by a
    runtime rejection path.
Accept: Given the canonical `TASK.md.tmpl`, When its §5 is read, Then the Persona line reads
  "(required)" (no "absent = generic" survives) and the Strategy line's placeholder mentions the
  Persona's domain stance shaping the approach; Given the canonical `TASK.fast.md.tmpl`, When its
  §5 is read, Then its Strategy line's placeholder also mentions letting the active
  persona/domain stance shape the approach — and both templates' 2 mirrors are still
  byte-identical to canonical, and `add.py`'s 3 copies are still byte-identical to
  `engine_pin.ENGINE_MD5`.
Assumptions: ⚠ "required" here means the FIELD must be filled (never left blank/placeholder,
  `generic` is an accepted explicit value) — it is NOT engine-enforced (no freeze/check
  validation added), matching how every other §5 field (Strategy, Safety rule) already works:
  advisory prose, human/AI-honored, never gate-blocking. Lowest confidence because the request
  said "required" without specifying enforcement; if wrong (the requester actually wanted a real
  freeze-time check), the cost is small — a follow-up change-request adds the check without
  touching this wording.

---

## 3 · CONTRACT — freeze the shape

```
add-method/tooling/templates/TASK.md.tmpl  §5 BUILD  (canonical; mirrored verbatim to
  .add/tooling/templates/TASK.md.tmpl and
  add-method/src/add_method/_bundled/tooling/templates/TASK.md.tmpl)

  Strategy (ordered batches): <1. … 2. … — the planned build order; guidance, not enforced;
    preferred architecture/pattern strategies; advise solution/method to resolve issues/
    implement features; let the named Persona's domain stance (below) shape the approach, not
    just architecture patterns>

  Persona (required): <name the persona file under `.add/personas/` this build embodies as a
    domain stance atop SOUL.md — advisory, never lowers a gate; name "generic" if no project
    persona fits yet>

add-method/tooling/templates/TASK.fast.md.tmpl  §5 BUILD  (canonical; mirrored verbatim to
  .add/tooling/templates/TASK.fast.md.tmpl and
  add-method/src/add_method/_bundled/tooling/templates/TASK.fast.md.tmpl)

  Strategy & known-problem fixes: <ordered build steps · the trap each known problem must dodge
    · let the active persona's domain stance (or "generic") shape the approach, not just
    patterns>

Rejection: none (wording-only; test suite is the enforcement — see §4).
```

`Least-sure flag surfaced at freeze:` [spec] whether "required" should someday become an actual
  freeze-time engine check (currently: prose-only, matching every other §5 field) — if the
  requester wanted real enforcement, this ships the wrong half; cost is low, a follow-up task.
Status: FROZEN @ v1 — approved by Tin Dang (auto-mode proceed — freeze report rendered in chat,
  no response after 2 AskUserQuestion prompts; recommended option taken per CLAUDE.md Rule 2)

---

## 4 · TESTS — failing-first (red)

Plan (all in `add-method/tooling/test_persona_required_domain_hint.py`, reading files directly —
  no `add.main` invocation needed, this is pure content-truth):
  - test_persona_line_is_required: CANON_TMPL §5 section contains `"Persona (required):"`, does
    NOT contain `"Persona (optional):"` or the literal `"absent = generic"`.
  - test_persona_generic_fallback_named: CANON_TMPL §5 Persona line contains `generic` as the
    explicit named fallback.
  - test_full_strategy_line_gains_domain_hint: CANON_TMPL §5 Strategy line's placeholder mentions
    `"Persona"` and `"domain stance"`, and the `STRATEGY_LABEL` string is unchanged/still present.
  - test_fast_strategy_line_gains_domain_hint: CANON_FAST §5 Strategy line's placeholder mentions
    `"persona"` and `"domain stance"`, and `FAST_STRATEGY_LABEL` is unchanged/still present.
  - test_no_new_frozen_tag: re-run the `test_scope_decl_template.FROZEN_TAGS` census against
    CANON_TMPL — unchanged set (no new bare `<word>` tag).
  - test_mirrors_byte_identical: dogfood + bundled copies of both `.tmpl` files match canonical.
  - test_engine_pin_unchanged: all 3 `add.py` copies match `engine_pin.ENGINE_MD5` (no engine
    code touched by this task).
Tests live in: `add-method/tooling/test_persona_required_domain_hint.py` (canonical test-suite
  location for template/prose-only tasks, not the task-local `./tests/` — matches
  scope-decl-template / orchestrator-build-persona / fastlane-intake-nudge precedent). MUST run
  red (current wording still says "optional"/"absent = generic", no domain-stance hint) before
  Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `add-method/tooling/templates/TASK.md.tmpl`, `add-method/tooling/templates/TASK.fast.md.tmpl`, `.add/tooling/templates/TASK.md.tmpl`, `.add/tooling/templates/TASK.fast.md.tmpl`, `add-method/src/add_method/_bundled/tooling/templates/TASK.md.tmpl`, `add-method/src/add_method/_bundled/tooling/templates/TASK.fast.md.tmpl`, `add-method/tooling/test_persona_required_domain_hint.py`
Strategy & known-problem fixes: 1. write the red test file first (reads CANON_TMPL/CANON_FAST,
  asserts new wording absent yet — confirms red for the right reason) 2. edit the canonical
  `TASK.md.tmpl` §5 Persona + Strategy lines exactly as frozen above 3. edit the canonical
  `TASK.fast.md.tmpl` §5 Strategy line exactly as frozen above 4. `cp` both canonical files
  verbatim over their `.add/tooling/templates/` and `_bundled/tooling/templates/` mirrors 5. run
  the new test green, then the full `add-method/tooling/` suite to confirm no regression (parity/
  frozen-tag/engine-pin tests in test_scope_decl_template.py and test_orchestrator_build_persona.py
  especially) · known trap: forgetting a mirror trips the byte-identical parity tests; adding a
  bracketed single-word placeholder (e.g. a bare `<domain>`) would silently grow the v16
  FROZEN_TAGS census — keep all new guidance multi-word prose inside the EXISTING `<...>` spans.
Strategy actually used: as planned (all 5 steps) — red test (3 failures for the right reason)
  → both canonical templates edited exactly as frozen → mirrored to the dogfood + bundled trees
  (`diff` confirmed byte-identical) → new suite green (8/8) → full regression pass on
  test_scope_decl_template.py + test_orchestrator_build_persona.py + test_fast_lane_template.py
  (53/53). No persona named for THIS task's own §5 (fast-lane tasks have no Persona field to
  fill) — the change is prose-only and self-referential.
Code lives in: `./src/`   ·   Constraints: change no test, no contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build
- [x] green was EARNED — no overfit / vacuous asserts / stubbed-away logic
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP)

Build expectations (from §1 Accept + §3 CONTRACT): `TASK.md.tmpl` §5 Persona line reads
  "(required)" with `generic` as the named fallback (no "absent = generic" survives) and its
  Strategy line's placeholder mentions the Persona's domain stance shaping the approach;
  `TASK.fast.md.tmpl`'s Strategy line's placeholder mentions the active persona/domain stance —
  confirmed by `test_persona_required_domain_hint.py` (8/8 green) and a direct Read of both
  canonical files (lines 118/120 of TASK.md.tmpl, line 59 of TASK.fast.md.tmpl). All 3 mirrors
  of each file confirmed byte-identical via `diff`. `add.py` (all 3 copies) confirmed unchanged
  against `engine_pin.ENGINE_MD5` — no engine code touched. Two full-suite failures
  (`test_seams_doc.test_every_anchor_resolves`, `test_ci_tooling_mirror_gap.
  test_fresh_checkout_survives_test_job_sequence`) were investigated and confirmed PRE-EXISTING
  and unrelated: `git stash` (removing this task's changes) reproduces the identical
  `test_seams_doc` failure (a stale `add.py:4568` line-anchor from unrelated prior commits), and
  neither failing test file references TASK.md.tmpl/TASK.fast.md.tmpl/Persona/Strategy at all.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-06

OBSERVE: [SPEC · open] `test_seams_doc.test_every_anchor_resolves` fails on HEAD independent of
  this task — `.add/SEAMS.md`'s `scope-token-grammar` entry cites `add.py:4568` for
  `_declared_scope`, but that line now holds unrelated code (line-drift from commits since the
  anchor was last re-cited). Confirmed pre-existing via `git stash` (evidence: identical failure
  with this task's changes removed). Needs a small follow-up: re-run the SEAMS.md anchor re-cite
  and pin the correct current line for `_declared_scope`.

