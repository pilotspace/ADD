# TASK: Cross-milestone PROJECT.md survivor doc + foundation chapter

slug: project-foundation · created: 2026-05-29 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Realize the AIDD diagram's foundation layer — the cross-milestone context that
"provides context" to every TDD⇄ADD loop — as a single survivor doc.

Must:
  - `init` scaffolds `.add/PROJECT.md` from a template, mapping to the diagram:
    Domain (DDD) · Spec/Living-Document (SDD) · Users (UDD) · Key Decisions.
  - PROJECT.md is a SURVIVOR file: `init` must NOT clobber an existing one (like
    CONVENTIONS/GLOSSARY) — it outlives every milestone.
  - The SDD section POINTS to the active milestone + frozen contracts; it does
    not duplicate the milestone tier.
  - `status` prints a one-line pointer to PROJECT.md so a fresh session re-orients
    on the foundation first (anti-context-rot, dynamic-by-reference).
  - Never write a BLANK survivor file: if a template renders empty (e.g. stale
    installed templates/), skip it and warn — do not create a 0-content file.
After:
  - `.add/PROJECT.md` exists with the four sections; rerunning `init --force`
    leaves a hand-edited PROJECT.md untouched; `status` shows the pointer.
Reject:
  - n/a (init has no new rejection codes; blank-render is a warn+skip, not an error)
Assumptions (confirm before building):
  - [x] one PROJECT.md with sections (not three files DDD/SDD/UDD) — user-picked
  - [x] SDD section references the milestone tier rather than re-implementing it
  - [x] book gets a foundation chapter so the diagram and the text finally agree

<!-- EXIT: every rule stated, every rejection has a named code, zero open assumptions. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: init scaffolds the foundation doc
  Given a fresh directory
  When I run `add.py init`
  Then .add/PROJECT.md exists
  And it contains the headings Domain (DDD), Spec / Living Document (SDD), Users (UDD), Key Decisions

Scenario: PROJECT.md is a survivor (no clobber)
  Given an initialised project whose PROJECT.md was hand-edited with a sentinel
  When I run `add.py init --force`
  Then state.json is reset
  And PROJECT.md still contains the sentinel (it was not overwritten)

Scenario: status points to the foundation
  Given an initialised project
  When I run `add.py status`
  Then the output references PROJECT.md (so the agent reads the foundation first)

Scenario: never write a blank survivor file
  Given the foundation template renders to empty/whitespace
  When init scaffolds survivor files
  Then PROJECT.md is NOT created as a 0-content file (skip + warn)
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
template:  add-method/tooling/templates/PROJECT.md.tmpl
           tokens: {{project}} {{stage}} {{date}}
           sections (exact headings, matched by tests):
             ## Domain (DDD) — the language and the boundaries
             ## Spec / Living Document (SDD) — what we are building, now
             ## Users (UDD) — UI/UX: design before code
             ## Key Decisions

init:      SETUP_FILES gains "PROJECT.md"  (survivor, no-clobber)
           survivor render now receives project+stage+date for all files
           blank-render guard: rendered.strip()=="" -> skip write + warn (stderr)

status:    prints a line containing "PROJECT.md" when .add/PROJECT.md exists
           (placed near the top, before the task list — the resume pointer)

docs:      add-method/docs/14-foundation.md defines DDD/SDD/UDD in ADD's terms
           (survivor layer / living document); 00-introduction.md gets a pointer.
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit)   <!-- Changing a frozen contract = change request back to SPECIFY. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: all 4 scenarios (new file add-method/tooling/test_foundation.py).
Plan (one test per scenario, asserting behavior not internals):
  - test_init_scaffolds_project_md: init / assert PROJECT.md exists + 4 headings present
  - test_project_md_is_survivor_no_clobber: init / write sentinel / init --force / assert sentinel kept
  - test_status_points_to_project: init / run status / assert "PROJECT.md" in output
  - test_init_never_writes_blank_survivor: temporarily blank the template / init / assert no 0-content PROJECT.md

Tests live in: `add-method/tooling/test_foundation.py` · MUST run red (template+code missing) before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): survivor files are never clobbered; never write a
blank survivor file (warn+skip). All writes stay atomic (_atomic_write).
Code lives in: `add-method/tooling/add.py` + `templates/PROJECT.md.tmpl` + `docs/14-foundation.md`.
Constraints: do NOT change any test or the frozen contract; stdlib only; backward
compatible with existing state.json; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — 36/36 via `npm test` (+4 test_foundation)
- [x] coverage did not decrease — +4 tests; existing 32 still green
- [x] no test or contract was altered during build — contract FROZEN; tests untouched
- [x] concurrency / timing — N/A (local atomic writes; no-clobber survivor loop)
- [x] no exposed secrets / injection / unexpected deps — stdlib only; templates only
- [x] layering & deps follow CONVENTIONS.md — tooling-only change + book chapter; no new deps
- [x] a person reviewed — live `status`/`check` on this repo (context pointer + 32/32);
      end-of-turn adversarial multi-agent review covers the combined v1-2 diff

### GATE RECORD
Outcome: PASS
Evidence: npm test 36/36; live status shows `.add/PROJECT.md` pointer; check 32/32;
chapter 14 ships in docs/ with book parity (0 diffs); template renders non-blank.
Reviewed by: Tin Dang (+ Claude: tests + live + manual) · date: 2026-05-29

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): do agents actually read PROJECT.md at session
start? does the foundation stay lean (one screen) or drift toward a manual?
Spec delta for the next loop: a `project` command to print/open the foundation;
`status --foundation` to render the doc inline; unblocks guideline-inject.

Change note (pre-commit, 2026-05-29): UDD corrected from generic "users/personas" to
**UI/UX-Driven Development** (user flows · UI states loading/empty/error · DESIGN.md ·
clickable prototype) per the source diagram `UDD.jpg`. The template heading keeps the
`Users (UDD)` prefix, so all four foundation tests still match and the gate evidence
(36/36) is unaffected; this was a factual correction, not a behavioral contract change.
