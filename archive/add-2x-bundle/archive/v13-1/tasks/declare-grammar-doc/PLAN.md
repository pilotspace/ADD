# TASK: State the Tests-live-in declaration grammar in template + guide

slug: declare-grammar-doc · created: 2026-06-05 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: state the `Tests live in:` declaration grammar in the §4 template + phase guide
  (v13 fold residue (a): the grammar is engine-parsed by `_declared_tests_count` but
  written nowhere a §4 author can read)
Framings weighed: template comment + guide section (chosen) · visible template prose
  (rejected: bloats every scaffolded TASK.md for a rule most tasks never need — the
  default `./tests/` just works) · docstring-only (rejected: that's the status quo —
  authors don't read add.py source)
Must:
  - TASK.md.tmpl §4 carries a compact comment at the `Tests live in:` line stating
    every form the engine parses; the comment is copied into every scaffolded TASK.md.
  - phases/4-tests.md gains a "Declaring where tests live" section stating: the FIRST
    line matching `Tests live in:` is read · paths are the BACKTICKED tokens on that
    line · `./…` resolves to the task dir · a token containing `/` resolves to the
    project root (the parent of `.add/`) · a bare name resolves as a sibling of the
    previous token's directory (else the task dir) · a directory token counts the
    `*.py` files directly inside it (non-recursive) · a `.py` file token counts itself;
    anything else is ignored · resolved files are deduped · the report marks declared
    counts with `†`.
  - The prose mirrors engine behavior exactly (one source of truth — v13-1 shared
    decision); wording follows the `_declared_tests_count` docstring.
  - Both touched files sync 3-tree byte-identical (canonical · dogfood · bundled).
Reject:
  - any add.py change -> impossible in this task (engine md5 unchanged ×3)
  - any NEW token form or recursive globbing -> out of scope (grammar STATED, not extended)
After:
  - A §4 author can write every declaration form the engine parses without reading
    add.py source; scaffolded tasks carry the grammar inline.
Assumptions — least-sure first:
  ⚠ a template COMMENT (HTML comment, like the existing EXIT markers) is the right
    carrier in TASK.md.tmpl — least sure because comments are invisible in rendered
    markdown previews; if the human wants the grammar VISIBLE in scaffolds, the fix is
    one line flipped from comment to prose (cost: small, one change request)
  - [ ] the `_declared_tests_count` docstring wording is authoritative — verified
    against the code this session (tokens/resolution/dedupe all match)
  - [ ] templates/ parity is already guarded (test_bundle_parity covers canonical ≡
    bundled); the new test pins the dogfood copy too

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: template states the grammar
  Given the shipped TASK.md.tmpl
  When its §4 block is read
  Then a comment at the Tests-live-in line names every form: ./ task-relative,
       /-rooted, bare sibling, directory -> non-recursive *.py, backticked tokens
  And the visible default line `./tests/` is unchanged

Scenario: scaffolds carry the grammar
  Given a fresh project
  When new-task scaffolds a TASK.md
  Then the generated §4 contains the same grammar comment

Scenario: guide section exists
  Given phases/4-tests.md
  When the "Declaring where tests live" section is read
  Then it states first-matching-line, backticked tokens, all three resolution
       forms, non-recursive *.py, dedupe, and the † report marker

Scenario: three trees agree
  Given the canonical, dogfood, and bundled copies of both touched files
  When their bytes are compared
  Then all three copies of each file are identical

Scenario: engine untouched
  Given add.py in all three trees
  When the task is complete
  Then its md5 is unchanged from before the task
  And the existing declared-fallback behavior suite still passes
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
TASK.md.tmpl §4 — after the existing line (which stays byte-identical):
  Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
add ONE comment line:
  <!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
       a token with "/" = project root · a bare name = sibling of the previous
       token's dir · a directory counts its *.py files (non-recursive); reports
       mark declared counts with † -->

phases/4-tests.md — new section "## Declaring where tests live" between
  "## Produce" and "## AI prompt": ~8 lines of prose covering first-matching-line ·
  backticked tokens · ./ = task dir · "/" = project root (parent of .add/) ·
  bare = sibling of previous (else task dir) · dir -> non-recursive *.py ·
  .py file -> itself, else ignored · dedupe · † marker in reports.

Sync: both files ×3 trees byte-identical · add.py untouched (md5 ×3 unchanged)
No engine, CLI, or JSON change of any kind — a prose-only task.
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (one-approval front; template-comment carrier accepted)   <!-- Changing a frozen contract = change request back to SPECIFY. -->
<!-- The freeze IS the one approval. Lead it with the bundle's least-sure flag: the 1–2 points
     most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], with why + cost.
     The §1 ⚠ assumptions are its first feeder; a flag may point at a scenario or the contract too. See run.md. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: every Must (template comment · scaffold carry-through · guide section ·
3-tree parity) + the engine-untouched Reject — content anchors red→green (the folded
"prose-guides-are-TDD-able" convention); behavior itself stays pinned by the existing
test_declared_fallback.py suite (honest limit: anchors prove the words exist, the
behavior suite proves the engine works — the accord between them is by construction
and human review, per words-exist ≠ method-works).
Plan (one test per scenario):
  - test_template_states_grammar: TASK.md.tmpl contains the comment + each form's
    anchor phrase (`./…`, project root, sibling, non-recursive, †)
  - test_scaffold_carries_grammar: new-task in a tmp project → generated §4 contains
    the grammar comment (behavioral, not file-presence)
  - test_guide_section_present: 4-tests.md contains "## Declaring where tests live" +
    each resolution rule's anchor phrase, placed before "## AI prompt"
  - test_grammar_doc_tree_parity: md5(TASK.md.tmpl) ×3 equal AND md5(4-tests.md) ×3 equal
  - test_engine_untouched: the three add.py md5s equal each other (green-by-design
    regression guard; the canonical hash assertion lives in the build evidence)

Tests live in: `add-method/tooling/test_declare_grammar_doc.py` (suite root, like every
prior tooling task) · MUST run red (anchors missing) before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): the existing visible template line and every other
template/guide byte stay unchanged — the build ADDS one comment + one section, nothing else.
Code lives in: `add-method/tooling/templates/TASK.md.tmpl` + `add-method/skill/add/phases/4-tests.md`
  (canonical) → template synced to `.add/tooling/templates/` + `_bundled/tooling/templates/`;
  guide synced to `.claude/skills/add/phases/` + `_bundled/skill/add/phases/` (3-tree parity).
Constraints: do NOT change any test or the contract; no add.py edit; prose only.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — 367/367 (362 prior + 5 new), `add.py check` 192/0 (4 pre-existing warns)
- [x] coverage did not decrease — 5 tests added, none removed/weakened; red 3-for-the-right-reason
      (anchors missing in template/scaffold/guide) + 2 green-by-design guards (×3 parity ·
      engine-untouched)
- [x] no test or contract was altered during build — §3 untouched post-freeze; the build added
      ONE template comment + ONE guide section, nothing else (visible default line byte-identical)
- [x] concurrency / timing safe — prose-only change, no code path touched
- [x] no exposed secrets, injection openings, or unexpected dependencies — no code change at all;
      add.py md5 c607d214161911af7d700e3314dd3191 unchanged ×3; nothing on this line to escalate
- [x] layering & dependencies follow CONVENTIONS.md — both files synced ×3 trees byte-identical
      (test_grammar_doc_tree_parity green); one-source-of-truth honored (prose mirrors the
      _declared_tests_count docstring)
- [x] a person reviewed and approved the change — Tin approved the frozen contract
      (one-approval front, 2026-06-05); gate auto-resolved on complete evidence per
      `autonomy: auto` (no deviation, no residue, security line genuinely empty)

### GATE RECORD
Outcome: PASS (auto-resolved on complete evidence — all green · loops dry · no residue ·
no deviation: build touched exactly TASK.md.tmpl ×3 + 4-tests.md ×3 + the new test file)
Reviewed by: auto-gate under `autonomy: auto` · contract approved by Tin · date: 2026-06-05

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): §4 authors still writing declaration forms the engine
can't parse (would mean the grammar comment/section is unclear or unread); any future
`_declared_tests_count` change that diverges from the stated prose (the one-source-of-truth
accord is by construction — a drift here reopens this task as a change request).
Spec delta for the next loop: v13's SDD residue (a) is closed — the declaration grammar is
stated where authors read it (template comment + guide section); residue (b) confinement
remains, owned by declared-path-confinement.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
  - [TDD · folded] a scaffold-template change is testable BEHAVIORALLY, not just by file anchors —
    run the scaffolder in a tmp project and assert the generated artifact carries the change
    (evidence: test_scaffold_carries_grammar caught nothing extra this time, but pins the
    template→scaffold copy path that a pure file-anchor test would miss)
