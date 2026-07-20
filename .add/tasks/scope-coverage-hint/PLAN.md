# TASK: Freeze echo flags Touches paths outside the declared scope

slug: scope-coverage-hint · created: 2026-07-13 · stage: mvp
milestone: call-floor
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 1 · SPECIFY — the rules

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: scope coverage hint — the WM1 re-cross repairs (2/rep in two reps) came from TOO-NARROW declarations: every token resolved [ok] but the build touched §3 Touches paths outside them; the dead-token class is already rendered, the narrow class is invisible at freeze
Must:
  - when the declaration RESOLVES to entries, the freeze echo also prints `note: §3 Touches cites <path> outside the declared scope` for each Touches path that exists in the tree but is NOT covered (_in_scope) by the resolved entries
  - covered or nonexistent Touches paths print nothing; UNDECLARED/garbage keep their existing proposal branch unchanged
Reject:
  - writing anything to TASK.md -> never (propose-not-impose, same as the echo)
  - any hint failure blocking a freeze -> fail-open (inside the existing _scope_echo try)
Accept: Given a frozen declaration covering `pkg/api/` while §3 Touches also cites an existing `lib/util.py`, When freeze runs, Then stdout carries the outside-scope note for `lib/util.py` and nothing for the covered path.
Boundary: two Touches shapes — covered path (silent) · existing-but-outside path (noted); nonexistent paths stay silent (never speculative)
Assumptions: ⚠ the Touches path-head regex under-extracts prose-heavy lines — why: free prose; if wrong: a miss stays silent, never a false note (cost: the hint under-fires, today's behavior)

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols): add-method/tooling/add.py:_scope_echo (extend the resolved-entries branch) · add_engine/components.py:_in_scope (read-only reuse, already imported at add.py:61)
Context (working folder): ENGINE_MD5 re-aims; SEAMS _declared_scope pin drifts (insertion above 5581) — re-pin
Honors (patterns / conventions): propose-not-impose · fail-open echo (scope-echo-draft) · never speculative (exists() gate before noting)
Anchors the contract cites: _scope_echo · _in_scope
Ground SHA: 726693d — stamped by freeze

### Contract

```
_scope_echo, in the `else:` (resolved entries) branch, after the [ok|MISSING] loop:
    for tok in <same Touches path-head extraction as the proposal branch>:
        if (rootp / tok).exists() and not _in_scope(tok, resolved):
            print(f"note: §3 Touches cites {tok} outside the declared scope")
(the proposal branch for None/[]/all-MISSING is untouched)
```

`Least-sure flag surfaced at freeze:` [contract] a Touches path that is legitimately read-only (grounding context, not build target) draws a note anyway — why: the echo can't tell read from write intent; if wrong: one advisory line the human ignores at the freeze they're already reading (cost: negligible vs a 2-call re-cross repair)
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/tooling/` `add-method/../.add/` `.add/tooling/` `add-method/.add/`
Strategy & known-problem fixes: red tests -> extract the Touches-path helper (shared by proposal + hint) -> sync x3 + re-pin ENGINE_MD5 + SEAMS. Traps: no 'seam'/'fold' slang, no SEAMS.md# in literals; footer-last.
Approach (domain strategy): mechanical containment check, advisory render

### AI-verify record (required when gate_mode: ai-plan-verify)
- [x] §3 PLAN grounding anchors resolve in the current tree (_scope_echo + _in_scope read this session)
- [x] §1 every Must + every Reject present, each Reject paired with an outcome
- [x] §3 Contract shape is concrete
- [x] Lowest-confidence flag surfaced and substantive (read-only Touches false-positive)
Verified by: claude-opus-4-8 (orchestrator, inline) · at: 2026-07-13T16:25:00Z

---

## 4 · TESTS — failing-first (red)

Plan: test_outside_path_noted (covered silent + outside noted, same freeze) · test_nonexistent_silent · test_undeclared_branch_unchanged (proposal still prints, no coverage notes) · test_footer_stays_last.
Tests live in: `add-method/tooling/test_scope_coverage_hint.py` · MUST run red before Build.

---

## 5 · BUILD — AI writes the code (execution)

> The change plan was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope; improve on the strategy if the code teaches you better.
Strategy actually used: as planned — Touches extraction factored into a nested _touches_paths helper shared by the proposal and the hint; scope-echo-draft suite stayed green untouched.
Code lives in: `./src/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build (shared batch fence 3496/3496 OK)
- [x] green was EARNED — the tests freeze a real board with covered/outside/nonexistent Touches paths and assert per-class output
- [x] input dialect held — two Touches shapes each pinned per the §1 Boundary
- [x] no exposed secrets, injection openings, or unexpected dependencies (pure read, _in_scope reuse)

Build expectations (from §1 Accept + §3 CONTRACT): an existing-but-uncovered Touches path draws the note, covered/nonexistent stay silent, UNDECLARED branch unchanged — confirmed by test_scope_coverage_hint (4/4) + test_scope_echo_draft (6/6).

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-13

