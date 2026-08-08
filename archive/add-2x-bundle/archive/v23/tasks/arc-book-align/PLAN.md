# TASK: Align the book + GLOSSARY with the decision arc

slug: arc-book-align · created: 2026-06-09 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower
     the autonomy level with `autonomy: conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: the decision arc, described in the book — a GLOSSARY term + one book-chapter
mention, so the method's own prose explains the goal · done · plan arc that every human
gate report now opens with, consistently with the shipped gates (exit-criterion 3).

Framings weighed: glossary-term + one chapter mention (chosen) · glossary-only (rejected — a
term with no chapter to give it a home reads as orphaned jargon) · new dedicated chapter
(rejected — the arc is a presentation refinement of an existing concept, not a new step; it
belongs beside the decision point it serves, not in its own chapter).

Must:
<must>
  - Add a GLOSSARY term **The decision arc** to `add-method/docs/appendix-c-glossary.md`,
    defining it as the three engine-sourced lines a gate report opens with — `goal:` (the
    milestone goal the work serves) · `done:` (achievement — the proven progress toward it) ·
    `plan:` (what comes next) — rendered first, above the report summary.
  - Define the term as **goal · done · plan** (the shipped label set), glossing `done` as
    "achievement / proven progress" so the book reconciles the milestone's "achievement"
    wording with the gate reports that actually render `done:`.
  - State, in the term, that the arc is presentation only — it never adds a gate or changes a
    `PASS` / `RISK-ACCEPTED` / `HARD-STOP` / freeze outcome — and is engine-sourced like all
    evidence (never re-typed from memory).
  - Mention the arc in `add-method/docs/02-the-flow.md`, beside the decision-point / "Who does
    what" passage, naming that whenever the flow stops for the human the report opens with the
    arc, and pointing to the GLOSSARY term. [v2] The paragraph MUST span all seven wired gates
    (baseline approval · contract-freeze · verify · intake · scope · milestone close · stage
    graduation) — consistent with `test_arc_gate_wiring` and the term's "every decision point".
  - Keep the new prose lint-clean on the ubiquitous-language surface (all `docs/*.md` are
    globbed; the glossary is a bridge file) — no banned idiom, no emphasis tokens.
  - Mirror both canonical edits to the bundle (`_bundled/docs/`, parity-guarded) AND the
    dogfood tree (`.add/docs/`); the glossary leg is test-guarded both ways, the chapter leg's
    dogfood copy is NOT (md5 it by hand — bundle-green is false comfort for the chapter).
</must>
Reject:
<reject>
  - the glossary copies the milestone's "achievement" label verbatim as the term's three-part
    name, contradicting the `done:` the gates render -> "arc_label_inconsistent_with_gates"
  - new prose introduces a banned idiom or emphasis token on the lint surface -> "wording_lint_red"
  - either canonical edit lands without its bundle + dogfood mirror -> "tree_drift"
  - the mention reframes the arc as a new gate or as changing an outcome -> "arc_misdescribed_as_gate"
</reject>
After:
<after>
  - The GLOSSARY defines **The decision arc** (goal · done · plan) consistently with the
    shipped gate reports, with achievement glossed onto the `done:` line.
  - `02-the-flow.md` names the arc beside the decision point and links the GLOSSARY term.
  - The full test suite is green (ubiquitous-language + bundle parity + the new presence fence);
    all three trees byte-identical for the glossary, md5-confirmed for the chapter.
  - A human has read both edits in full and confirmed the prose is right (the substantive guard).
</after>
Assumptions — lowest-confidence first:
<assumptions>
  - [x] a one-paragraph mention in `02-the-flow.md` (beside "Who does what") is the RIGHT chapter
    home — RESOLVED at freeze: the human chose 02-the-flow.md (2026-06-09), and the mention names
    the wider gates (intake · close · graduation) while the GLOSSARY holds the single definition.
    Lowest confidence at the freeze; the forward-watch is logged §7 (relocate one paragraph if it
    reads mislocated — no contract churn).
  - [x] the term belongs in the GLOSSARY right after **Decision point** — RESOLVED: placed there;
    reads as the where ↔ what-rendered-there pairing, not a duplicate (semantic read, §6).
  - [x] a one-line presence fence is worth adding over pure parity + human read — RESOLVED:
    added test_decision_arc_book (4 cases), honest red→green confirmed; the human read stays the
    substantive guard.
  - [x] "report" polysemy is handled — RESOLVED: the GLOSSARY term carries the bridging clause
    (chat report at a decision point vs the verify gate's three Test/Quality/Risk reports →
    links 11-governance).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: GLOSSARY defines the decision arc
  Given appendix-c-glossary.md with no "decision arc" term
  When the term is added
  Then a reader finds **The decision arc** defined as goal · done · plan, rendered first
  And the existing **Decision point** term is unchanged (the pairing, not a rewrite)

Scenario: the label reconciles with the shipped gates
  Given the gate reports render `goal:` / `done:` / `plan:`
  When the GLOSSARY term names the arc
  Then it uses goal · done · plan and glosses `done` as "achievement / proven progress"
  And it does NOT name the three parts "goal · achievement · plan" (the gates would contradict it)

Scenario: the arc is described as presentation, not a gate
  Given the term and the chapter mention
  When a reader reads what the arc does
  Then it states the arc never adds a gate or changes a PASS / RISK-ACCEPTED / HARD-STOP outcome
  And no prose reframes it as a new step in the flow

Scenario: the chapter gives the term a home and spans all 7 gates
  Given 02-the-flow.md with no mention of the arc
  When the mention is added beside the decision-point / "Who does what" passage
  Then a reader sees that the report opens with the arc when the flow stops for the human
  And the mention links to the GLOSSARY term (the single definitional home)
  And the paragraph names all seven wired gates — including the baseline approval and scope
      (the two the v1 5-list dropped) — consistent with test_arc_gate_wiring

Scenario: the new prose is lint-clean
  Given the ubiquitous-language suite globs every docs/*.md
  When it scans the two edited files
  Then no banned idiom or emphasis token is found
  And the suite stays green

Scenario: all three trees agree
  Given canonical edits to glossary + 02-the-flow.md
  When the bundle and dogfood mirrors are synced
  Then bundle parity is green and the glossary leg is byte-identical across all three trees
  And the chapter leg is md5-confirmed by hand (no test guards canon↔dogfood for it)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

A docs task: the "contract" is the frozen prose shape — what the two files must say,
and the test fence that guards the named term. No `add.py` change, no engine surface.

```
GLOSSARY  add-method/docs/appendix-c-glossary.md
  + new term, placed immediately AFTER **Decision point** (where ↔ what-rendered-there):

  **The decision arc** — the three engine-sourced lines a gate report opens with at every
  human decision point: `goal:` the milestone goal the work serves · `done:` the
  achievement, the proven progress toward it (the same line the reports render — "achievement"
  and `done` are one thing, named two ways) · `plan:` what comes next. What `done` reports
  ADAPTS per gate (verify: tests + evidence · milestone close: exit-criteria met · intake: the
  request sized) while the three-part shape stays constant. Rendered first, above the report's
  summary, so the human confirms with sight of the whole trajectory, not a local snapshot.
  Engine-sourced like all evidence — goal · done · plan are pulled from `add.py` output, never
  re-typed. Presentation only: it never adds a gate or changes a `PASS` / `RISK-ACCEPTED` /
  `HARD-STOP` / freeze outcome. See the `add` skill's `report-template.md`.
  [v2: lowercased "SUMMARY"→"summary" (the book never describes the five-block report); added
   the per-gate adaptation clause per the milestone's shared decision.]

CHAPTER  add-method/docs/02-the-flow.md
  + one paragraph after the "Who does what" table (line ~81), before "## What survives":

  names that whenever the flow stops for the human the report opens with the decision arc
  (goal · done · plan), rendered first so the human sees the whole trajectory, not a local
  snapshot; presentation only, never a new gate; links to Appendix C. It MUST span ALL SEVEN
  wired gates (the set `test_arc_gate_wiring` enforces): the baseline approval that ends setup ·
  contract-freeze · verify · intake · scope · milestone close · stage graduation.
  [v2 change-request: was a 5-gate list (omitted the baseline approval + scope); verify found it
   inconsistent with the 7 wired+tested gates and the term's "every decision point". Widened to 7.]

TEST FENCE  tests/test_decision_arc_book.py  (regression guard on the named term; NOT a quality proof)
  - "decision arc" (case-insensitive) appears in canonical appendix-c-glossary.md
  - "decision arc" appears in canonical 02-the-flow.md
  - the glossary term carries all three labels goal / done / plan AND the gloss word "achievement"
  - the glossary term does NOT name the trio "goal · achievement · plan" (gate-consistency guard)
  - [v2] the chapter arc paragraph names the baseline approval AND scope — the two gates the
    5-list dropped — so this gap class cannot regress silently (gate-coverage fence)
  the substantive guard remains the human read + the existing ubiquitous-language + parity suites
```

Lowest-confidence flag (bundle-wide): ⚠ [spec] the `02-the-flow.md` "Who does what" neighborhood
is the right chapter home — the arc spans gates this chapter doesn't enumerate, so a reader could
expect it in 11-governance. Mitigated: the mention names the wider gates and the GLOSSARY is the
single definition. If wrong, a follow-up relocates one paragraph — cheap, no contract churn.
RESOLVED at freeze: human chose 02-the-flow.md (beside "Who does what") — 2026-06-09.
v2 flag (change-request): ⚠ [spec] gate enumeration — the v1 chapter listed 5 of 7 wired gates;
verify caught it (baseline approval undocumented). RESOLVED: widened to all 7 + a gate-coverage
fence so it can't regress. Human-authorized Option A (span all 7), 2026-06-09.

Status: FROZEN @ v2 — approved by Tin Dang · date: 2026-06-09 (chapter home: 02-the-flow.md;
   v2 change-request: chapter spans all 7 wired gates + summary-case + per-gate adaptation)
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: presence-fence only (prose task — the human read is the substantive guard;
parity + ubiquitous-language are the standing suites). 4 marker cases.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_glossary_defines_the_arc: assert canonical appendix-c-glossary.md contains "decision arc"
    (case-insensitive) → RED now (term absent)
  - test_label_reconciles_with_gates: assert the glossary "decision arc" definition carries goal,
    done, plan AND the word "achievement"; assert it does NOT contain the literal trio
    "goal · achievement · plan" → RED now (term absent → first assert fails)
  - test_chapter_gives_the_term_a_home: assert canonical 02-the-flow.md contains "decision arc"
    → RED now (mention absent)
  - test_arc_described_as_presentation: assert the glossary term says "presentation" and names a
    gate outcome (PASS / RISK-ACCEPTED / HARD-STOP) — i.e. the not-a-gate framing is present
    → RED now (term absent)
  - [v2] test_chapter_spans_all_wired_gates: extract the 02-the-flow arc paragraph; assert it
    names the baseline approval AND scope (the two the v1 5-list dropped) → RED until widened
    (gate-coverage fence; the regression that triggered the change-request can't recur silently)
  (lint-clean + tree-agreement scenarios are covered by the standing test_ubiquitous_language +
   test_bundle_parity + test_v8_docs + test_inline_citations + test_flow_diagram suites — the
   last two guard the chapter across ALL FOUR trees incl. the root copy; the APPENDIX root copy
   is unguarded and synced by hand, logged §6/§7)
</test_plan>

Tests live in: `tests/test_decision_arc_book.py` · MUST run red (term/mention absent) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 691 OK (686 baseline + 5 in test_decision_arc_book incl. the v2 fence)
- [x] coverage did not decrease — added a test file; no code removed; prose-only change
- [x] no test or contract was altered to pass a build — §3 was changed via a DELIBERATE
      change-request (v1→v2), human-authorized (Option A), then re-frozen; the build follows the
      v2 contract. Existing tests unchanged; the §4 fence was STRENGTHENED (gate-coverage case) as
      part of the change-request. The build also brought prose into compliance with two pre-existing
      cross-tree guards (test_inline_citations, test_flow_diagram) — never weakened them.
- [x] concurrency / timing — N/A (documentation; no runtime path)
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose only; no deps
- [x] layering & dependencies follow CONVENTIONS.md — docs change; the term links 11-governance
      + report-template.md (correct cross-references, no new coupling)
- [ ] a person reviewed and approved the change   ← this gate

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read both edited passages in full:
      · GLOSSARY **The decision arc** (appendix-c-glossary.md, between **Decision point** and
        **Specification bundle**): defines the trio as `goal:` · `done:` · `plan:`, glosses
        `done` = "the achievement, the proven progress … (the gate reports render this line as
        `done`)" — CONFIRMS the milestone's "achievement" wording reconciles to the shipped
        `done:` label, never naming the contradicting "goal · achievement · plan". States
        presentation-only (names PASS / RISK-ACCEPTED / HARD-STOP / freeze, none changed),
        engine-sourced, and bridges the "report" polysemy (chat report at a decision point vs
        the verify gate's three Test/Quality/Risk reports → links 11-governance).
      · 02-the-flow.md paragraph [v2] (after "Who does what", before "What survives"): now names
        ALL SEVEN wired gates — the baseline approval that ends setup · contract-freeze · verify
        within each task · intake · scope · milestone close · stage graduation. CONFIRMS the
        chapter is consistent with `test_arc_gate_wiring` (7) and the term's "every decision point",
        renders-first, presentation-only, links Appendix C, no new step.
      · [v2] glossary fixes read + confirmed: "SUMMARY"→"summary" (the book never describes the
        five-block report, so lowercase is correct); added the per-gate adaptation clause (verify:
        tests+evidence · close: exit-criteria met · intake: request sized) per the milestone's
        shared decision — the trio shape stays constant.
      · Lint: test_ubiquitous_language green over both files (no banned idiom; `transparency`
        is not the banned `trust layer`; no emphasis token).
- [N/A] WIRING / DEAD-CODE (code) — no code symbols introduced (prose + one test file).

CHANGE-REQUEST CLOSURE (v1→v2): the v1 verify pass-attempt found the chapter named 5 of 7 wired
gates (baseline approval + scope undocumented) while the term claimed "every decision point" — a
gate-consistency gap failing exit-criterion-3. Resolved by the method, not around it: reopened to
contract (`add.py phase contract`), re-froze §3 @ v2 (human-authorized Option A), widened the
chapter to all 7, added a gate-coverage fence (red→green), re-synced all 4 trees, re-ran 691 OK.
The arc dogfooded its own theme — the gate that hid a known gap is the gate this milestone exists
to close.

Build-time finding (deviation from a §1 assumption — surfaced, not hidden): the book has FOUR
tracked trees, not three — a ROOT published copy (`./02-the-flow.md`, `./appendix-c-glossary.md`)
beyond canon/bundle/dogfood. The CHAPTER is guarded across all four (test_inline_citations +
test_flow_diagram caught the unsynced root copy — RED until synced). The APPENDIX root copy is
guarded only canon↔bundle↔dogfood (test_v8_docs + bundle_parity); its ROOT copy has NO test guard
— it stayed stale silently and was synced by hand. All four trees now md5-identical for both
files. Logged as a §7 delta.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-09
Notes: v2 — book spans all 7 wired gates; 691 tests OK; 4 trees byte-identical; the
  v1→v2 gate-coverage gap was closed via change-request (reopen→contract→re-freeze),
  not waived. Human-led verify (method-defining docs change). Deep-check SEMANTIC read
  done; WIRING/DEAD-CODE N/A (prose + one test file). No security surface.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the gate-coverage fence (test_chapter_spans_all_wired_gates)
checks only baseline + scope today — if a future gate is wired into test_arc_gate_wiring, the book
enumeration AND this fence must grow with it, or the book silently under-describes again.
Spec delta for the next loop: the **Decision point** glossary term still lists 4 illustrative gates
(cf · verify · intake · close); a later pass could make it explicitly illustrative or expand to all
7 for full term-level consistency with "every decision point". Forward-watch: the arc's chapter home
(02-the-flow) — relocate one paragraph if reader feedback shows it reads mislocated (no contract churn).

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
  - [ADD · folded] the book has FOUR mirror trees (root · canon · bundle · dogfood), and an APPENDIX's
    root copy is guarded by NO test (only chapters are, via test_inline_citations + test_flow_diagram);
    a docs task must sync all 4 by hand and md5-confirm the appendix root leg (evidence: the glossary
    root copy stayed stale through the v1 build with no test catching it; the chapter root copy was
    caught RED by test_inline_citations)
  - [SDD · folded] a presence fence is not a coverage fence — asserting a term EXISTS does not assert
    WHERE its claim holds; a consistency claim ("at every decision point") needs a test reconciling it
    against ground truth (evidence: 690 OK while the chapter named 5 of 7 wired gates; v2 added
    test_chapter_spans_all_wired_gates to fence the gap class)
  - [ADD · folded] dogfooding the deliverable at its own gate surfaced the gap the tests missed — the
    verify report's `done:` arc line forced an honest 7-vs-5-vs-4 reconciliation no assertion checked
    (evidence: the milestone's own theme — transparent gates — exposed its own undocumented gate;
    advisor-confirmed at the verify gate)
  - [ADD · folded] the change-request is the method working, not a failure — a frozen-contract gap caught
    at verify was fixed via reopen→contract→re-freeze (v1→v2), never a silent build edit (evidence:
    phase verify→contract→re-freeze @ v2 → re-verify, 691 OK; §3 carries both freeze stamps)
