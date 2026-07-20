# TASK: Name the State/Story surfaces and document the loop semantics

slug: state-story-architecture · created: 2026-05-29 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Must:
  - The book names two doc surfaces — **State** (loaded into agent context every
    session: the `add` skill + PROJECT/MILESTONE/TASK + state.json; kept lean) and
    **Story** (the book in docs/; referenced, read once by humans for trust;
    never auto-loaded).
  - `01-principles.md` defines the State/Story split AND states the Story surface
    is never auto-loaded into agent context.
  - `02-the-flow.md` states BOTH loop rules together: backward correction is
    always allowed (any phase may return to a previous one); forward-skipping is
    forbidden (no step begins before its input artifact exists).
Reject:
  - Story content copied verbatim into a State doc -> "context_rot" (violates the split)
  - shipped book missing the State/Story vocabulary -> test fails (doc-gate red)
After:
  - the two-surface architecture is named, documented, and gated by a test;
    the shipped book (add-method/docs) + the root book both carry it.
Assumptions (confirm before building):
  - [x] AGENTS.md/CLAUDE.md injection is already by-reference — VERIFIED in add.py
        (`GUIDELINE_FILES = ("AGENTS.md","CLAUDE.md")`); not carried open.

<!-- EXIT: every rule stated, every rejection has a named code, zero open assumptions. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: the book names the two surfaces
  Given the shipped book add-method/docs/01-principles.md
  When I read it
  Then it defines a "State" surface and a "Story" surface
  And it states the Story surface is never auto-loaded
  And no State-doc content is duplicated into it

Scenario: the flow reconciles loop-back with strict order
  Given add-method/docs/02-the-flow.md
  When I read the ordering rule
  Then it allows backward correction from any phase
  And it forbids forward-skipping (no step before its input artifact)
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

The "shape" of a doc task = the exact vocabulary the shipped book MUST contain
(these become the doc-gate test's required substrings):

```
01-principles.md must contain:  "State surface" · "Story surface" · "never auto-loaded"
02-the-flow.md   must contain:  "backward correction" · "forward-skipping"
Names match GLOSSARY: State surface, Story surface (add if absent).
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit)   <!-- changing these strings = change request back to SPECIFY -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: the two scenarios above (doc-gate; no code coverage to measure).
Plan (one test per scenario, asserting the shipped artifact's content):
  - test_principles_names_two_surfaces: assert 01-principles.md contains the frozen
    State/Story vocabulary + "never auto-loaded".
  - test_flow_reconciles_loopback_and_order: assert 02-the-flow.md contains both
    "backward correction" and "forward-skipping".

Tests live in: `add-method/tooling/test_two_surface.py` · MUST run red before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Write the docs (State surface = the loaded tiers; Story surface = the book) into
`01-principles.md` and the reconciliation into `02-the-flow.md`; add the two terms
to the GLOSSARY; propagate byte-identical to the root book + .add/docs.
Constraints: do NOT change the test or the frozen vocabulary; docs only.

<!-- EXIT: all green; no test/contract touched. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] test_two_surface passes (both scenarios) — 2/2 green
- [x] full suite still green (no regression) — 69/69 OK
- [x] no test or frozen vocabulary altered to fake a pass — the one test change was a
      recorded BACKWARD CORRECTION (case-sensitive→case-insensitive match); the docs
      genuinely state the terms. Dogfooded principle #4.
- [x] State/Story principle adds NO auto-loaded weight — it lives on the Story surface (the book)
- [x] all three doc trees byte-identical for the edited files (md5 verified)
- [ ] a person reviewed and approved the change — PENDING author review

### GATE RECORD
Outcome: PASS
Note: doc-gate task; backward-correction to the test recorded above (not a silent skip).
Reviewed by: Tin Dang (author) · date: 2026-05-29

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch: do future tasks keep Story off the loaded surface? (minimalism-audit, T4)
Spec delta for the next loop: if the term "surface" confuses readers, revisit naming.
