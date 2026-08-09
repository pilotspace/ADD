# TASK: Book ch.02: explain breadth-first task list + just-in-time per-task spec at milestone scale

slug: flow-jit-tasks-doc · created: 2026-06-26 · stage: mvp
autonomy: auto
phase: done   <!-- fast lane: ground -> specify -> contract -> tests -> build -> verify -> observe -> done -->
fast: true   <!-- the fast lane: a small task, collapsed flow + minimal template. Omit --fast for full rigor. -->

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols):
- `add-method/docs/02-the-flow.md` — the per-FEATURE 7-step flow chapter. Today it documents one feature's flow + the long Observe→Specify loop, but NEVER explains how a milestone's MANY tasks compose: that tasks are LISTED breadth-first up front (the DAG) yet each is SPECIFIED + built just-in-time. ADD a short subsection after "## The flow" (before "## Why the order is the order", ~line 54) stating this, so the book explains what the MILESTONE.md template only asserts.
- the 4 byte-identical book copies: canonical `add-method/docs/02-the-flow.md` → mirrored to repo-root `./02-the-flow.md`, dogfood `.add/docs/02-the-flow.md`, bundled `add-method/src/add_method/_bundled/docs/02-the-flow.md`. `test_book_parity.py` guards canonical↔root; the bundled/.add copies sync too.
- `add-method/tooling/test_flow_jit_doc.py` (NEW) — the red content test asserting the new rationale anchor exists in the canonical chapter (+ all 4 copies carry it).

Context (working folder):
- the rationale already lives as an assertion in `MILESTONE.md.tmpl` ("THIN: breadth … per-task detail lives in each TASK.md, written just-in-time"; "breadth-first decomposition") and in the skill's `scope.md` (one breadth-first pass: `slug · depends-on · one line`). This task moves the WHY into the book. Source: todo #17.

Honors (patterns / conventions):
- book parity: edit canonical `add-method/docs/`, propagate byte-identically to the 3 mirrors (cp), keep `test_book_parity` + the content tests green.
- additive prose: ADD a subsection; do NOT alter strings other content tests assert (test_decision_arc_book, test_flow_diagram, etc.) — append, don't disturb.

Anchors the contract cites: the new "## … just-in-time" subsection in `02-the-flow.md` (anchor phrases `breadth-first` + `just-in-time`) · the 4-copy parity · `test_flow_jit_doc.py`.

---

## 1 · SPECIFY — the rules

Feature: document the milestone-scale composition rule in book ch.02 — a milestone decomposes into a breadth-first task LIST + DAG up front, but each task runs the seven-step flow just-in-time (its spec absorbs what earlier tasks learned), rather than spec-bundling every task before any build.
Must:
  - `02-the-flow.md` gains a short subsection (after "## The flow") stating: tasks are listed breadth-first up front (with their depends-on DAG), each is specified+built just-in-time, and WHY (anti-rot — a later task's spec benefits from earlier tasks' Observe deltas; the same backward-correction principle at milestone scale).
  - the subsection names the link to the per-task flow (each listed task runs steps 0–7) and points at the milestone living-doc (MILESTONE.md) as where the breadth-first list lives.
  - all 4 book copies stay byte-identical; `test_book_parity` + the existing content tests stay green (additive, no existing string disturbed).
Reject:
  - (no error path — a documentation change; "rejection" = a parity break, which `test_book_parity` already catches.)
Accept: after the edit, `02-the-flow.md` contains a subsection whose prose includes both "breadth-first" and "just-in-time" explaining the milestone→tasks composition, present byte-identically in all 4 copies — asserted by test_flow_jit_doc.
Assumptions: ⚠ ch.02 (the per-feature flow) is the right home vs ch.09 (the loop) — chosen because a reader meets "the flow" here and immediately wonders how many features compose; if wrong: the paragraph moves to 09 (cheap, same content). none other material.

---

## 3 · CONTRACT — freeze the shape

~~~
Book ch.02 — NEW subsection (prose contract), inserted after the "The flow" section,
before the "Why the order is the order" section. Heading (an h2 in the real doc):
  "Many features, one at a time — listed up front, specified just-in-time"
Body (three bullets):
  - A MILESTONE decomposes BREADTH-FIRST into a task LIST at creation: slug · depends-on
    · one line each (the dependency DAG; `add.py waves` views it). The milestone living-doc
    (MILESTONE.md) holds this list + the shared decisions + the exit criteria — it stays THIN.
  - Each listed task then runs the full seven-step flow (0 Ground … 6 Verify) JUST-IN-TIME
    — its specification bundle is written when work reaches it, NOT all bundled up front.
  - WHY just-in-time: a later task's spec absorbs what earlier tasks' Observe deltas taught,
    and a bundle written too early rots before you reach it — the same backward-correction
    principle (Observe → Specify) at milestone scale. List all tasks; specify each in turn.

Invariant: prose contains the anchor phrases "breadth-first" and "just-in-time"; ADDITIVE (no
existing asserted string changed); present byte-identically in all 4 book copies.
~~~

Least-sure flag surfaced at freeze: [spec] ch.02 vs ch.09 placement — ch.02 chosen as where a reader first asks "how do many features compose"; if wrong the same paragraph moves to ch.09 (the loop), cheap. The content itself is settled (it restates the MILESTONE.md template + scope.md, already in force).
Status: FROZEN @ v1 — approved by Tin Dang
<!-- The freeze IS the one approval. Approved -> Status: FROZEN @ vN — approved by <name>.
     Changing a frozen contract = change request back to SPECIFY. -->

---

## 4 · TESTS — failing-first (red)

Plan: test_flow_jit_doc — assert `add-method/docs/02-the-flow.md` contains the new subsection (both "breadth-first" AND "just-in-time" present, in one section) AND all 4 book copies are byte-identical for that chapter. Red now (phrases absent), green after the edit + propagation.
Tests live in: `add-method/tooling/test_flow_jit_doc.py` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `add-method/docs/02-the-flow.md` `add-method/../02-the-flow.md` `.add/docs/02-the-flow.md` `add-method/src/add_method/_bundled/docs/02-the-flow.md` `add-method/tooling/test_flow_jit_doc.py`
<!-- repo-root `02-the-flow.md` declared via the `add-method/..` climb: a token with "/" is project-root-relative, but a BARE name resolves as a sibling of the previous token's dir — so a root-level file needs the climb to land at the project root. -->
Code lives in: `add-method/docs/02-the-flow.md` (canonical; cp to the 3 mirrors)   ·   Constraints: change no other test, no contract; ADDITIVE prose only — do not alter any string the existing content tests assert.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build — full suite 2063 OK (2060→2063, +3 test_flow_jit_doc); check 431/0; audit clean; §3 FROZEN @ v1 untouched; only the 3 tracked book copies + the new test changed (.add/docs is gitignored dogfood)
- [x] green was EARNED — RED for the right reason (heading + position absent) before the edit; asserts the real anchor phrases + section placement + 4-copy byte-identity, not a tautology; book_parity + existing content tests (test_flow_diagram, test_decision_arc_book, …) stayed green → additive prose disturbed no asserted string
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP) — documentation-only prose change; no code, no deps

Build expectations (from §1 Accept + §3 CONTRACT): ch.02 reads with a new "Many features, one at a time — listed up front, specified just-in-time" subsection (both anchor phrases present, between The flow and Why the order is the order) explaining milestone→tasks composition, byte-identical across all 4 copies — confirmed: test_flow_jit_doc green + a render-read of the chapter.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-mode standing authorization; §3 freeze "Freeze as-is") · date: 2026-06-26
OBSERVE: [ADD · open] a §3 contract fence must not contain line-starting `##` — `_phase_spans` reads them as section headers and truncates the §3 span, so the freeze-flag parser can't see the flag (`unflagged_freeze`); describe a doc heading in prose or use a non-`#` marker (evidence: this task's first freeze failed until the literal `##` inside the contract were removed)
<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass.
     OBSERVE (optional): one `[SPEC · open]` or competency-delta line here if the loop taught the foundation something. -->
