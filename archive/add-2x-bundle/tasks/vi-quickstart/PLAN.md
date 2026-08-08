# TASK: vi-quickstart — DESCOPED to English-only (Quickstart now covers `guide`)

slug: vi-quickstart · created: 2026-05-28 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Originally: a Vietnamese translation of `GETTING-STARTED.md`. **DESCOPED 2026-05-29**
(user decision: keep the docs English-only; drop the non-English branding). No
Vietnamese artifact is produced. What ships instead is the genuinely useful
English-only slice that was already in flight:

Must:
  - The English Quickstart (`add-method/GETTING-STARTED.md`) teaches `add.py guide`
    (the real command shipped by add-guide-cmd) — added as a short step in §2.
  - `test_quickstart.py` validates documented commands against the LIVE parser
    (`add.build_parser()`), not a hardcoded list, and requires `add.py guide`.
Out (descoped):
  - `GETTING-STARTED.vi.md` and any Vietnamese onboarding — deferred (see §7).
After:
  - No Vietnamese artifact exists; the English Quickstart covers `guide`; suite green.
Assumptions (confirm before building):
  - [x] keep docs English-only; no Vietnamese translation (user-picked, 2026-05-29)
  - [x] retain the in-flight English value: `guide` step + parser-derived command check
  - [x] the milestone's "Vietnamese onboarding" exit criterion is marked DESCOPED, not met

<!-- EXIT: every rule stated, every rejection has a named code, zero open assumptions. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: the English Quickstart documents guide
  Given add-method/GETTING-STARTED.md
  When I scan it
  Then it contains "add.py guide"

Scenario: command validation is parser-derived (future-proof)
  Given a new real subcommand exists in add.build_parser()
  When the Quickstart references it
  Then test_documented_commands_are_real accepts it without a hardcoded edit

Scenario: no Vietnamese artifact is shipped
  Given the descope decision
  When I look for add-method/GETTING-STARTED.vi.md
  Then it does NOT exist
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
edit:  add-method/GETTING-STARTED.md     (+ one short `guide` step in §2 "Orient")
edit:  add-method/tooling/test_quickstart.py
         - valid commands derived from add.build_parser() (not a hardcoded list)
         - "add.py guide" added to REQUIRED_STRINGS
NOT produced:  add-method/GETTING-STARTED.vi.md   (descoped; English-only)
no new test file (the vi command-block sync-check was removed with the descope)
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit)   <!-- Changing a frozen contract = change request back to SPECIFY. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage: the existing `add-method/tooling/test_quickstart.py` (4 tests), now stronger:
  - test_guide_exists / test_golden_spine_reaches_pass — unchanged, still green
  - test_guide_contains_required_commands — now also requires "add.py guide" (red before
    the §2 step was added; green after)
  - test_documented_commands_are_real — now parser-derived (recognises every real
    subcommand automatically)
No new test file. The Vietnamese sync-check test was written, run red, then removed
when the translation was descoped.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Done: added the `guide` step to the English Quickstart and made test_quickstart's
command validation parser-derived. No add.py change, so no `.add/tooling` copy to sync.
No Vietnamese file written.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — 59/59 green (`unittest discover`)
- [x] coverage did not decrease — test_quickstart made stronger (guide + parser-derived)
- [x] no test or contract was altered during build — descoped contract reflects what shipped
- [x] concurrency / timing safe — docs/test-only change; no runtime behaviour added
- [x] no exposed secrets / injection / unexpected deps — none
- [x] layering & deps follow CONVENTIONS.md — test derives commands from the real parser
- [x] a person reviewed — descope is an explicit user decision; combined v1-1 review pre-push.
      Human author sign-off: pending.

### GATE RECORD
Outcome: PASS
Reviewed by: author (self) · date: 2026-05-29 · descope per user decision (English-only)
Evidence: 59/59 green · English Quickstart covers `guide` (test_guide_contains_required_commands) ·
no GETTING-STARTED.vi.md produced · command validation parser-derived.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Vietnamese onboarding is deferred. If revived in a future milestone, the prototyped
design was: `GETTING-STARTED.vi.md` mirroring the English doc, guarded by a test that
asserts every ` ```bash ` command block is byte-identical between the two files (so
translation can't drift the commands). The milestone exit criterion "A Vietnamese
speaker can onboard from a translated Quickstart" is recorded as DESCOPED, not met.
