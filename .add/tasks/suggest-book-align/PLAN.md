# TASK: Book + GLOSSARY describe the guided-decision convention

slug: suggest-book-align · created: 2026-06-16 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): the book documents the convention beside its sibling, the "decision arc":
- `02-the-flow.md:86` — the "What the human sees … the decision arc" paragraph; I add one guided-choice sentence here.
- `appendix-c-glossary.md` — add 2 headwords: `**Guided decision**` + `**Recommended pick**` (format: `**Headword** — definition. See [ref].`; the `decision arc` entry at line 43 is the sibling).
- Book trees (byte-identical, parity-guarded): canonical `add-method/docs/` ↔ repo-root `*.md` (test_book_parity) ↔ `add-method/src/add_method/_bundled/docs/` (test_bundle_parity `test_docs_tree_byte_identical`). Plus the dogfood `.add/docs/` (gitignored, NOT parity-guarded — sync it too so the dogfood instance stays accurate).
- new red guard `.add/tasks/suggest-book-align/tests/test_suggest_book_align.py` — asserts the 2 glossary headwords + the 02-the-flow guided-choice line present across the parity trees (mirrors release-docs-align's accord suite).

Context (working folder):
- `add-method/tooling/test_book_parity.py` (canonical↔root, EXCLUDE README.md) + `test_bundle_parity.py` `test_docs_tree_byte_identical` (canonical↔_bundled) — the guards I must keep green.
- `add-method/tooling/wording_lint.py` surface INCLUDES `docs/appendix-b-prompts.md` only (not the whole book), but new prose still avoids banned phrases; keep_list terms unchanged.

Honors (patterns / conventions):
- PROJECT.md §Users — the dogfood `.add/docs/` can drift silently (gitignored, outside test_bundle_parity); sync it deliberately, do not trust it as guarded.
- CONVENTIONS — "docs-guard-cross-checks-source"; the book DESCRIBES the convention, it does not re-specify it (report-template.md is the operational source); ×N-tree byte-identical.
- the glossary entry shape + the decision-arc footprint (02-the-flow + glossary) — mirror it exactly for the sibling convention.

Anchors the contract cites:
- `02-the-flow.md` decision-arc paragraph (the insertion point for the guided-choice sentence)
- `appendix-c-glossary.md` (the 2 new headwords)
- the book parity tree set (canonical · root · _bundled · dogfood)
- `test_suggest_book_align.py` headword + line tokens (the checkable seam)

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Book + GLOSSARY describe the guided-decision convention — one sentence in 02-the-flow.md beside the decision arc + 2 GLOSSARY headwords, byte-identical across the book trees.
Framings weighed: document beside the decision arc (chosen) · a new standalone book section · glossary-only
  — chose beside-the-decision-arc: the guided choice is a SIBLING of the arc (both are what the human sees at a decision point), so co-locating keeps the book lean + discoverable; a standalone section over-weights a presentation refinement; glossary-only would hide it from the flow narrative.
Must:
<must>
  - M1 — `02-the-flow.md` gains one sentence beside the decision-arc paragraph: at every human decision point the AI presents the DECISION as a guided choice (a recommended pick + described alternatives).
  - M2 — `appendix-c-glossary.md` gains 2 headwords — **Guided decision** (a decision point presented as a recommended pick + its described alternatives) and **Recommended pick** (the one highlighted option) — each with a See ref to report-template.md / the flow chapter.
  - M3 — the book DESCRIBES, does not re-specify: it points at report-template.md as the operational source; it does not re-list the convention's rules (single-source-point-not-restate).
  - M4 — byte-identical across the parity trees (canonical `add-method/docs/` ↔ repo-root ↔ `_bundled/docs/`); the dogfood `.add/docs/` synced too; test_book_parity + test_bundle_parity green.
</must>
Reject:
<reject>
  - a glossary headword (Guided decision · Recommended pick) absent from the book -> "headword_absent"   # the RED state §4 asserts before build
  - a parity tree missing the book change (canonical ≠ root ≠ _bundled) -> "book_drift"
  - the book re-specifies the convention's rules instead of pointing at report-template.md -> "book_respecifies"   # review-caught
</reject>
After:
<after>
  - `02-the-flow.md` + GLOSSARY describe the convention across all trees byte-identical; `report-template.md` UNCHANGED; the dogfood `.add/docs/` synced.
  - the §4 red guard (`test_suggest_book_align.py`) asserts the 2 headwords + the 02-the-flow guided-choice line + cross-tree parity — green only after build.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ co-locating with the decision arc (02-the-flow + glossary), not a standalone Governance (ch.11) section, is the right book footprint — lowest confidence because a reader might look for decision-gate behavior under Governance; if wrong: lower discoverability (cheaply fixed by a one-line cross-ref). Mitigation: the decision arc — the closest sibling — lives in exactly these two places, so the convention matches its proven footprint.
  - [x] "Guided decision" + "Recommended pick" are the right headwords — confirmed; named in the MILESTONE glossary deltas.
  - [x] the dogfood `.add/docs/` must be synced though unguarded — confirmed (PROJECT.md §Users records it as a known silent-drift gap).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
# Observability: the book is prose; "Then" is a grep over the canonical tree + a cross-tree md5 compare.

Scenario: The flow chapter describes the guided choice (M1)
  Given 02-the-flow.md after build
  When the §4 guard scans it
  Then it finds a guided-choice sentence beside the decision-arc paragraph

Scenario: GLOSSARY defines both headwords (M2)
  Given appendix-c-glossary.md after build
  When the guard reads it
  Then **Guided decision** and **Recommended pick** are both defined headwords

Scenario: The book points, not re-specifies (M3)
  Given the new book prose
  When the guard reads it
  Then it references report-template.md and does not re-list the convention's rules

Scenario: Parity holds across trees (M4)
  Given the book change applied
  When test_book_parity + test_bundle_parity run
  Then canonical add-method/docs == repo-root == _bundled/docs for the changed files

Scenario: REJECT headword_absent — a headword missing (Reject 1)
  Given the book without one headword
  When the §4 guard runs
  Then it FAILS naming the missing headword

Scenario: REJECT book_drift — a tree not updated (Reject 2)
  Given the change applied to only one tree
  When the parity guards run
  Then they FAIL (canonical ≠ root ≠ _bundled)

Scenario: REJECT book_respecifies — the book re-lists the rules (Reject 3)
  Given prose that restates the convention instead of pointing
  When a human reviews at the gate
  Then it is sent back (the book describes; report-template.md specifies)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
CONVENTION  book + GLOSSARY description of the guided-decision convention (a docs seam — no engine)

  BOOK TREES (byte-identical; parity-guarded except the dogfood):
    canonical  add-method/docs/                              (source)
    root       <repo-root>/*.md                              (test_book_parity, EXCLUDE README.md)
    bundled    add-method/src/add_method/_bundled/docs/       (test_bundle_parity test_docs_tree_byte_identical)
    dogfood    .add/docs/                                     (gitignored — synced, NOT guarded)

  REQUIRED (the checkable seam §4 asserts, in the canonical tree):
    B1 02-the-flow.md — a "guided choice" sentence beside the decision-arc paragraph
    B2 appendix-c-glossary.md — headword "**Guided decision**" defined
    B3 appendix-c-glossary.md — headword "**Recommended pick**" defined
    B4 the new prose references report-template.md (points, does not re-specify)

  INVARIANTS:
    I1 report-template.md UNCHANGED by this task
    I2 canonical == root == bundled for every changed file (+ dogfood synced)
    I3 engine add.py byte-identical

  REJECT (named; §4 asserts each):
    headword_absent  -> B2 or B3 missing (the RED pre-build state)
    book_drift       -> a parity tree not updated
    book_respecifies -> the book re-lists the convention's rules instead of pointing (review-caught)
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-16 (bundle approval; autonomy: auto — freeze is the one gate)
Least-sure flag surfaced at freeze: [spec] book footprint — co-locating the guided-choice description with the decision arc (02-the-flow.md + GLOSSARY) vs a Governance (ch.11) section; if wrong: lower discoverability for a reader who looks for gate behavior under Governance (cheaply fixed by a one-line cross-ref). Mitigation: the sibling decision arc lives in exactly these two places, so the convention matches its proven footprint. Human approved the co-located footprint at the freeze.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: B1–B4 + each reject condition asserted; docs accord (no line %).
Plan (reads the canonical tree + cross-tree md5):
<test_plan>
  - test_flow_describes_guided_choice (B1): assert "guided choice" present in add-method/docs/02-the-flow.md
  - test_glossary_headwords (B2+B3/headword_absent): assert "**Guided decision**" and "**Recommended pick**" in add-method/docs/appendix-c-glossary.md
  - test_book_points_at_report_template (B4): assert the new glossary entries reference "report-template"
  - test_book_trees_parity (book_drift/I2): assert md5 equal for 02-the-flow.md + appendix-c-glossary.md across canonical · root · _bundled
  - test_convention_untouched (I1): assert report-template.md still has "guided choice" + "▶" (unchanged by this task)
  # Reject headword_absent is the RED meta-property: test_glossary_headwords FAILS before build.
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/../02-the-flow.md` `add-method/docs/02-the-flow.md` `add-method/src/add_method/_bundled/docs/02-the-flow.md` `.add/docs/02-the-flow.md` `add-method/../appendix-c-glossary.md` `add-method/docs/appendix-c-glossary.md` `add-method/src/add_method/_bundled/docs/appendix-c-glossary.md` `.add/docs/appendix-c-glossary.md` `./tests/`   — each book file ×4 (repo-root via the `add-method/..` climb · canonical · bundled · dogfood) + guard tests. The repo-root copy MUST use the `add-method/../<name>` climb (a slash-bearing token resolves at project root); a BARE `<name>` would resolve as a sibling of the previous token's dir (`add-method/docs/`), NOT the root — the cause of the first scope_violation. The `.add/…` homes are ride-along (scope-walk excludes `.add/`); the `add-method/…` copies, the repo-root copies, + `./tests/` are the gated anchors.
Strategy (ordered batches): 1. write the red guard in `./tests/`. 2. edit the CANONICAL `add-method/docs/` (02-the-flow guided-choice sentence + 2 glossary headwords). 3. mirror byte-identical to repo-root + `_bundled/docs/` + the dogfood `.add/docs/`. 4. run the guard + test_book_parity + test_bundle_parity green.
Safety rule (feature-specific): `report-template.md` UNTOUCHED; all parity trees byte-identical for the 2 changed files; the dogfood `.add/docs/` synced even though unguarded.
Code lives in: the book trees (prose — no `src/`).
Constraints: do NOT change report-template.md, any test, or the contract; engine `add.py` byte-identical; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — task guard 5/5; full engine suite 1158/1158; book-parity + bundle-parity 8/8; xml-convention 17/17; wording-lint 0
- [x] coverage did not decrease — docs accord (no line %); B1–B4 + each reject asserted
- [x] no test or contract was altered during build — §3 frozen + §4 suite unchanged; git confirms report-template.md untouched (I1)
- [x] the green was EARNED, not gamed — adversarial refute-read: headwords use own-entry regex (not bare substring); B1 asserts the sentence sits INSIDE the decision-arc paragraph; B4 asserts the entry references report-template; tests read the real book trees. No overfit, no vacuous assert.
- [x] concurrency / timing of the risky operation is safe — N/A: prose docs, no runtime path
- [x] no exposed secrets, injection openings, or unexpected dependencies — N/A: prose only; no code, no deps
- [x] layering & dependencies follow CONVENTIONS.md — book DESCRIBES, report-template.md SPECIFIES (docs-guard-cross-checks-source); ×N-tree byte-identical
- [x] a person reviewed and approved the change — auto-resolved under `autonomy: auto` (docs accord, no residue, no security); recorded as an explicit PASS

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [ ] WIRING (code) — every new symbol is referenced; record where / how confirmed
- [ ] DEAD-CODE (code) — no new unused or orphaned symbol introduced
- [x] SEMANTIC (prose / non-code) — read in full, not skimmed: read both new glossary entries + the 02-the-flow guided-choice sentence across all 4 trees · confirmed they DESCRIBE the concept and POINT at report-template.md (M3, no rule re-listing) · the guided-choice sentence is co-located with the decision arc (B1) · "Guided decision"/"Recommended pick" are own-entry headwords (B2/B3) · md5-identical canonical·root·_bundled + dogfood synced (I2) · report-template.md byte-unchanged (I1)

### GATE RECORD
Outcome: PASS (auto-resolved — `autonomy: auto`, complete evidence, no security/residue)
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: auto-resolved (autonomy: auto) · date: 2026-06-16

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the headword-absent / book-drift rejects as guard signals — a future glossary edit that drops a headword or de-syncs a tree fails test_suggest_book_align.
Spec delta for the next loop: a presentation convention is documented where its closest SIBLING lives, not in a topical chapter — co-locating "guided decision" with "the decision arc" (02-the-flow + glossary, both "what the human sees when it is their turn") kept the book lean and the convention discoverable beside its kin.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [SDD · folded] a docs-accord task that DESCRIBES a convention (vs specifies it) verifies by own-entry-regex + cross-tree md5 + a points-at-source assertion — the book stays a pointer, never a second source of truth (evidence: test_book_points_at_report_template asserts the entry references report-template.md, not the rules) (evidence: test_suggest_book_align 5/5)
- [ADD · folded] the decision-point UX now has a complete trail — convention (report-template.md) → 8 gate cues → book+glossary — so a reader meets "guided decision" at the flow narrative, the glossary, and every guide (evidence: decision-suggestions milestone 3/3 across suggestion-block · gate-wiring · suggest-book-align)
