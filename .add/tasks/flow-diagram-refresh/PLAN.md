# TASK: Flow diagram shows non-waterfall loopback + nested TDD⇄ADD engine

slug: flow-diagram-refresh · created: 2026-05-29 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

The gap (a Story↔Story drift): ch02's PROSE already states principle 4 — "any phase
may send you back to an earlier one … forward-skipping is forbidden" — but the flow
DIAGRAM (mermaid + ASCII + add-flow.png) draws a pure left-to-right line with a single
Observe→Specify loop. The picture says waterfall; the words say any-phase loopback. For
v2 (Transparent · Provable) the canonical diagram must stop contradicting the method.

Must:
  - The flow diagram (all three surfaces) shows the FORWARD spine as solid arrows
    Specify→Scenarios→Contract→Tests→Build→Verify→Observe (forward-skip forbidden).
  - It shows BACKWARD CORRECTION is allowed: at least the prose's own two examples as
    dashed arrows — Build→Specify and Verify→Build — plus a one-line annotation
    "any phase may return to an earlier one" (draw the RULE, not every edge).
  - It shows the nested red/green engine: Tests⇄Build as a labelled "red/green loop"
    (the per-feature TDD⇄ADD engine), distinct from the big Observe→Specify loop.
  - Forward = solid, backward correction = dashed — the two rules that never conflict,
    legible at a glance (maps to ch02 "the flow runs in two directions").
  - English only (no non-English glyphs introduced).
  - Every phase label EXACTLY matches the engine's PHASES tuple and appears in CHECKLIST.
  - The reusable render pipeline (prompt + CHECKLIST + invocation) lives TRACKED in the
    shipped package (add-method/diagrams/), not in gitignored scratch.
Reject (what a reviewer must turn down):
  - a label that does not match engine PHASES, or a dropped/garbled acronym -> reject + re-render
  - a diagram with NO backward edge while the prose still claims loopback -> "loopback_not_drawn"
  - a forward arrow that skips a phase (implies forward-skip is allowed) -> reject
After:
  - ch02's mermaid + ASCII encode the forward spine, ≥1 backward edge, and the 4⇄5 loop;
    add-flow.png re-rendered to match; all three doc trees byte-identical for ch02;
    add-method/diagrams/ holds the committed, reusable pipeline.
Assumptions (confirm before building):
  - [x] Render via /nanobanana-rest, key in ~/.nanobanana.env. CONFIRMED (AskUserQuestion).
  - [x] Depict nested TDD⇄ADD engine (not just loopback). CONFIRMED (AskUserQuestion).
  - [x] Commit the reusable pipeline, not just the one PNG. CONFIRMED (AskUserQuestion).
  - [x] Mermaid is the testable/canonical surface; the PNG is a human visual gate, not
        machine-tested (image labels can garble). CONFIRMED (advisor).
  - [x] Surfaces need be LABEL-consistent (via CHECKLIST), NOT structurally identical —
        the nested-engine motif may be richer in the PNG than in mermaid. CONFIRMED (advisor).

<!-- EXIT: every rule stated, every rejection has a named code, zero open assumptions. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: every phase label matches the engine
  Given the refreshed ch02 mermaid and CHECKLIST
  When I read the node labels
  Then each name in the engine PHASES tuple appears as a label
  And no label is a non-PHASES or garbled token        # Story<->State

Scenario: the drawn loopback matches the written rule
  Given ch02 still states "any phase may send you back to an earlier one"
  When I parse the mermaid block
  Then it contains at least one backward-correction edge
  And if the prose rule is ever removed OR the backward edge is, the proof fails  # Story<->Story

Scenario: the flow chapter is identical across the three doc trees
  Given 02-the-flow.md in repo-root, add-method/docs, and .add/docs
  When I compare them
  Then all three are byte-identical                    # no surface drifts silently

Scenario: a rendered label is wrong  (human visual gate, not automated)
  Given a freshly rendered add-flow.png
  When a reviewer checks every glyph against CHECKLIST
  Then any misspelled/dropped/duplicated label is rejected and re-rendered
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

Two surfaces, two gates (deliberately asymmetric — text is provable, raster is judged):

```
TEXT (mermaid + ASCII in 02-the-flow.md)  — automated proof, test_flow_diagram.py:
  - labels_match_phases : {p for p in add.PHASES} ⊆ {mermaid node labels} ∩ {CHECKLIST tokens}
  - loopback_drawn      : prose contains principle-4 rule  AND  mermaid has ≥1 backward edge
                          (assert the CLAIM+drawing coexist; do NOT pin exact edge syntax)
  - trees_identical     : md5(root) == md5(add-method/docs) == md5(.add/docs) for ch02
RASTER (add-flow.png)  — human visual gate at VERIFY (NOT machine-tested):
  - every label spelled exactly per CHECKLIST; forward solid; backward dashed; 4⇄5 loop shown
PIPELINE (add-method/diagrams/)  — tracked + reusable:
  - prompt-flow.txt, CHECKLIST.md, and a regen note with the nanobanana-rest invocation
```

Frozen labels (must match engine PHASES + ch02): Specify · Scenarios · Contract · Tests ·
Build · Verify · Observe.  Acronyms guarded: DDD · SDD · UDD · TDD · ADD.

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit)   <!-- changing the tested invariants or the label set = change request back to SPECIFY. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: the three TEXT invariants from the contract (the raster gate is human).
Each test must go red for a REAL independent change, not just "someone edited this diagram"
(advisor's circularity bar) — so they pin the diagram to the engine and to the prose.
Plan (one test per testable scenario; the 4th scenario is a human gate, intentionally not coded):
  - test_every_phase_label_in_mermaid_and_checklist: assert each name in `add.PHASES`
    appears in ch02's mermaid block AND in diagrams/CHECKLIST.md. Red if a phase is
    renamed in the engine but not the diagram (Story↔State).
  - test_loopback_claim_and_drawing_coexist: assert ch02 prose still contains the
    principle-4 rule ("any phase may send you back to an earlier one") AND the mermaid
    block contains ≥1 backward edge (a target node that is upstream of its source on the
    forward spine). Do NOT match exact edge syntax. Red if either the words or the
    backward drawing disappears (Story↔Story) — this pins the actual gap.
  - test_flow_chapter_identical_across_trees: md5 of 02-the-flow.md equal in repo-root,
    add-method/docs, .add/docs. Red if any surface drifts.

Tests live in: `add-method/tooling/test_flow_diagram.py` · MUST run red (the current
mermaid has no backward edge; diagrams/CHECKLIST.md not yet in the shipped path) before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): the render is an external API call (Gemini) — load the
key from ~/.nanobanana.env without echoing it; render to a temp file, gate visually,
and only propagate a PASS; one retry on failure (per CLAUDE.md "design IO for failure").
Built:
  - 02-the-flow.md: mermaid gained 3 dashed backward edges (Build→Tests "red/green",
    Verify→Build, Build→Specify) + a legend paragraph (solid=forward / dashed=correction);
    ASCII redrawn with the 4⇄5 loop and a backward-correction line; image alt-text updated.
  - add-method/diagrams/ (NEW, tracked): prompt-flow.txt (rewritten for the new arrows),
    the other 3 prompts + CHECKLIST.md lifted out of gitignored tmp/, and README.md with
    the nanobanana-rest invocation + accept/propagate steps.
  - add-flow.png re-rendered (gemini-3-pro-image-preview, 16:9 2K → resized 1600×893 to
    match siblings, 183K), label-verified, propagated byte-identical to all 3 trees.
Constraints honored: no test or frozen contract changed; stdlib + the existing skill only.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — suite 83/83 OK (80 + 3 flow); `add.py check` 47/0
- [x] coverage did not decrease — net +3 tests; the 3 text invariants are covered
- [x] no test or contract was altered during build — tests written red FIRST (loopback
      FAIL on no backward edge; labels ERROR on missing shipped CHECKLIST), then made green
- [x] external-IO risk handled — render to temp first; key sourced from ~/.nanobanana.env,
      never echoed; visual gate before propagate; one retry budgeted (first render passed)
- [x] no exposed secrets / no unexpected deps — stdlib + the existing nanobanana-rest skill;
      no API key committed (tmp/ is gitignored; ~/.nanobanana.env is outside the repo)
- [x] layering follows CONVENTIONS.md — diagram source in add-method/diagrams/ (shipped),
      tests in add-method/tooling/, PNG in all 3 doc trees; engine untouched (md5 stable)
- [x] RASTER human visual gate — every glyph checked against CHECKLIST: 7 cards + phrases,
      3 bands, 4 dashed-arrow labels, the "any phase may return…" note, margin note — all
      correct, English-only, forward solid / backward dashed, 4⇄5 red/green loop present
- [x] a person reviewed and approved the change — author review below

### GATE RECORD
Outcome: PASS
Note: The diagram no longer contradicts principle 4 — solid forward spine + dashed
backward correction (Build→Specify, Verify→Build) + nested red/green Tests⇄Build engine,
on all three surfaces (mermaid machine-proved, PNG human-gated, ASCII redrawn). The
reusable pipeline is now tracked in add-method/diagrams/. All three design forks were
decided by the author via AskUserQuestion before SPECIFY froze.
Reviewed by: Tin Dang (author) · date: 2026-05-29

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): does any future engine phase rename or prose edit
turn test_flow_diagram red? That is the diagram catching drift, working as intended.
Spec delta for the next loop (feeds T4 minimalism-audit):
  - The flow now lives as THREE kept-in-sync surfaces (mermaid + ASCII + PNG). That is a
    minimalism smell — three things to keep aligned where the prose already carries the
    rule. T4 should ask whether the ASCII (or even the PNG) earns its keep, or whether one
    canonical surface + a generated view is leaner. (Advisor flagged this; deferred here.)
  - The other 3 diagrams (foundation · hierarchy · competencies) now have tracked prompts
    but were NOT re-rendered this task — their PNGs predate add-method/diagrams/. A later
    loop could re-render them through the same pipeline for provenance parity (low priority).
  - Pipeline hardening: README documents the render, but there is no single regen script;
    if diagrams churn, a `diagrams/render.sh <name>` wrapping the invocation would help.
