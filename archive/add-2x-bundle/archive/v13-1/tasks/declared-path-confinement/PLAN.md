# TASK: Confine declared test paths to the project root (contract v2)

slug: declared-path-confinement · created: 2026-06-05 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: confine §4-declared test paths to the project root (v13 fold residue (b);
  the human-ratified change request that cuts contract v2 of the declared-fallback
  seam — the frozen v1 of tests-declared-fallback is never edited)
Framings weighed: resolve-then-confine each FILE read (chosen) · confine the token
  only (rejected: a symlink inside the tree, or a symlinked member of a globbed
  dir, still escapes) · sandbox/chroot the read (rejected: stdlib-minimal, the
  read is a def-count, full isolation is disproportionate)
Must:
  - Every file `_declared_tests_count` actually READS must resolve (symlinks
    followed) inside the project root (the parent of `.add/`); anything else
    contributes 0 — no read is even attempted outside the root.
  - This closes the live escapes: `..` traversal in a `/`-token · an ABSOLUTE
    token (pathlib: `root / "/abs"` IS `/abs` — escapes today) · a symlink inside
    the tree pointing outside · a symlinked member of a globbed directory.
  - In-root declarations keep v1 behavior byte-for-byte: `./` task-relative,
    root-relative, bare sibling, dir → non-recursive *.py, dedupe, † footnote.
  - A `..`-containing token that RESOLVES inside the root still counts (the rule
    is where the path lands, not how it is written).
Reject:
  - token resolving outside the root -> contributes 0 (silent skip, fail-closed —
    same posture as v1's missing-path/OSError handling; no new error surface)
  - resolution errors (OSError on resolve) -> contributes 0 (fail-closed)
After:
  - `report`/`decide` can never read a byte outside the project root via a §4
    declaration; the §6 security note of tests-declared-fallback is closed.
Assumptions — least-sure first:
  ⚠ SILENT skip (count 0, no warning) is the right surface for an out-of-tree
    token — least sure because an author with a typo'd `../` path gets no signal
    beyond a 0/† absence; if the human wants a WARN line in check/report, that is
    a small additive follow-up (cost: one extra task or scope line, not a re-cut)
  - [ ] `Path.is_relative_to` (py3.9+) is safe at our 3.10 floor — verified: ci.yml
    tests 3.10 + 3.12
  - [ ] no existing test pins out-of-tree reads — verified: all 8 declared-fallback
    fixtures live inside the tmp project root

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: dot-dot traversal counts zero
  Given a §4 token `../<sibling-dir>/t.py` whose target exists OUTSIDE the project root
  When report renders the milestone rollup and --json
  Then the task's tests count is 0 with no † footnote
  And the out-of-tree file is never opened

Scenario: absolute token counts zero
  Given a §4 token holding an ABSOLUTE path to a real test file outside the root
  When report renders
  Then the count is 0 (the pathlib absolute-join escape is closed)

Scenario: symlink escape counts zero
  Given a symlink inside the project root pointing at an out-of-tree test file
  And a §4 token declaring that symlink
  When report renders
  Then the count is 0

Scenario: in-root declarations unchanged
  Given the v1 forms (./ task-relative · root-relative · bare sibling · directory)
    all resolving inside the root
  When report renders
  Then every count and the † footnote match v1 behavior exactly

Scenario: dot-dot that lands inside still counts
  Given a token `sub/../tests/t.py` that RESOLVES inside the root
  When report renders
  Then its tests are counted (confinement is by destination, not spelling)

Scenario: confinement stays pure
  Given any of the bodies above
  When report and its --json twin run
  Then the .add file set and state.json bytes are unchanged and every exit is 0
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
_declared_tests_count(root, slug) -> int     # signature + call sites UNCHANGED
  # v2 adds ONE rule to v1 resolution: before any filesystem read, the candidate
  #   (and every file collected from a directory token) must satisfy
  #   path.resolve().is_relative_to(root.parent.resolve())
  # outside / unresolvable -> skipped silently, contributes 0 (fail-closed)
  # inside -> v1 behavior byte-for-byte (glob, dedupe, def-count, † footnote)
CLI · JSON keys · exit codes · report/decide surfaces: all unchanged
prose accord: the 4-tests.md grammar section + the TASK.md.tmpl §4 comment each
  gain one clause — "anything resolving outside the project root counts 0" —
  synced ×3 trees (the task-1 anchors all still hold)
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (one-approval front; silent-skip confinement accepted)   <!-- Changing a frozen contract = change request back to SPECIFY. -->
<!-- The freeze IS the one approval. Lead it with the bundle's least-sure flag: the 1–2 points
     most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], with why + cost.
     The §1 ⚠ assumptions are its first feeder; a flag may point at a scenario or the contract too. See run.md. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: every Must + both Rejects — the three escape routes each get a red
test proving the count drops to 0; v1 in-root behavior + purity get green-by-design
regression guards; asserting rendered report/--json output, never function internals.
Plan (one test per scenario):
  - test_dotdot_traversal_zero: real out-of-tree file w/ 3 defs via `../<dir>/t.py` → 0, no †
  - test_absolute_token_zero: absolute-path token to the same file → 0
  - test_symlink_escape_zero: in-tree symlink → out-of-tree file → 0
  - test_inroot_forms_unchanged: ./ + root-relative + bare-sibling + dir forms → same
    counts as v1 (guard)
  - test_dotdot_inside_counts: `sub/../tests/t.py` resolving in-root → counted (guard)
  - test_confinement_pure: file set + state hash unchanged across text + --json, exit 0 (guard)
  - test_prose_clause_present: the grammar comment + guide section carry the confinement
    clause, ×3 parity held (anchors)

Tests live in: `add-method/tooling/test_path_confinement.py` (suite root, like every
prior tooling task) · MUST run red (escapes currently count) before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): in-root behavior byte-for-byte — only the escape
routes change outcome; the v1 suite (test_declared_fallback.py) must stay green untouched.
Code lives in: `add-method/tooling/add.py` `_declared_tests_count` (canonical) → synced
  ×3; prose clause in TASK.md.tmpl + 4-tests.md → synced ×3.
Constraints: do NOT change any test or the contract; stdlib only; no new error codes.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — 374/374 (367 prior + 7 new), `add.py check` 193/0 (4 pre-existing warns)
- [x] coverage did not decrease — 7 tests added, none removed/weakened; red 4-for-the-right-reason
      (all three escapes counted 3 pre-build, prose clause absent) + 3 green-by-design guards
      (in-root v1 forms · dot-dot-landing-inside · purity); one mid-build fix went to the BUILD
      output, not the matcher (guide reflowed so the clause sits on one line)
- [x] no test or contract was altered during build — §3 untouched post-freeze; code change is
      `_confined` + the v2 check inside `_declared_tests_count` (signature + call sites unchanged)
- [x] concurrency / timing safe — pure read-side check, no shared state, no IO added beyond
      path resolution
- [x] no exposed secrets, injection openings, or unexpected dependencies — NOTE (security line,
      escalating per foundation-version 11 rule): the change REMOVES a read capability (out-of-tree
      file contents are no longer reachable), but the confinement check itself calls
      `Path.resolve()`, which performs stat/readlink METADATA syscalls on path components that may
      lie outside the root before rejecting them — file CONTENTS are never opened; this residual
      metadata touch is inherent to symlink-following confinement
- [x] layering & dependencies follow CONVENTIONS.md — stdlib only; 3-tree md5 parity
      e053526c2ae346d37868a350ce0f7b70 ×3; prose accord synced ×3 (template + guide carry the clause)
- [x] a person reviewed and approved the change — Tin approved the frozen contract
      (one-approval front, 2026-06-05); gate ESCALATED to the human (security-line note above)

### GATE RECORD
Outcome: PASS — security-line note escalated and HUMAN-confirmed (residual resolve() metadata
touch accepted as inherent to symlink-following confinement; file contents never read; the
targeted out-of-tree content leak is closed)
Reviewed by: Tin (human gate, escalated per the security-line rule) · date: 2026-06-05

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): authors hitting the silent skip on a typo'd `../`
declaration (the accepted ⚠ — a 0/† absence is the only signal; a WARN in check/report is
the additive follow-up if it bites); any future declaration form added without routing it
through `_confined`.
Spec delta for the next loop: v13's SDD residue (b) is closed — the declared-fallback seam
is at contract v2 with root confinement; the v13-1 exit criterion "no read occurs outside
the root" holds for file contents (metadata resolution accepted at the human gate).

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
  - [ADD · folded] the security-line-always-escalates rule works in practice and is CHEAP — the
    note (resolve() metadata touch) took one question to adjudicate; writing the nuance on the
    line instead of self-clearing it kept the human gate honest (evidence: this task's GATE
    RECORD, first escalation since the rule was folded at foundation-version 11)
  - [SDD · folded] pathlib absolute-join is a quiet escape hatch — `root / "/abs"` IS `/abs`;
    any future path-resolving seam should name absolute tokens explicitly in its contract
    (evidence: test_absolute_token_zero was red pre-build, the hole was live in v1)
