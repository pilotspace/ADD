# TASK: 'add.py check' delta-grammar/routing guard (fail-closed)

slug: deltas-lint · created: 2026-06-03 · stage: mvp
autonomy: conservative   <!-- a fail-closed guard feeding the fold decision; Verify STOPS for the human (no auto-PASS). -->
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `add.py check` extended — a fail-closed guard that every competency-delta line is well-formed and routable
Framings weighed: extend `check` (chosen) · a separate `deltas --lint` command · a git pre-commit hook
Must:
  - within every task's "### Competency deltas" block, a DELTA ENTRY = a tag line matching `- [<tok> · <tok>]` PLUS its continuation lines (following lines until the next tag line, a blank line, or end of block) — deltas are routinely MULTI-LINE
  - a line is a delta-attempt ONLY if it has the `· ` tag separator inside the brackets; `- [x]` checkboxes and prose lines are NOT deltas
  - SKIP historical entries: any entry whose status is `folded` or `rejected` is not re-validated (the "done tasks are not retrofitted" convention) — open-only enforcement
  - validate every remaining entry against the grammar: COMP ∈ {DDD,SDD,UDD,TDD,ADD}; status ∈ {open,folded,rejected}; an `(evidence: …)` pointer present SOMEWHERE in the entry's unit
  - emit one check per task with at least one delta-attempt — "task '<slug>' deltas well-formed" — PASS or FAIL
  - a malformed/unroutable validated entry FAILS that check (so `check` exits 1), with a reason naming the code
  - skip HTML-comment lines (`<!-- … -->`); stay READ-ONLY and fail-closed (carry v2) — never mutate; an unparseable validated entry FAILS, never silently passes
After:
  - `add.py check` refuses to pass while any task holds a malformed/unroutable OPEN delta — the fold ritual never meets a live delta it cannot route
Reject (codes, from deltas.md / fold.md):
  - competency not one of the five -> "unknown_competency"
  - status not one of the three  -> "unknown_status"
  - no `(evidence: …)` in the unit -> "no_evidence"
  - a tagged attempt matching none of the above shape -> "malformed_delta"
Assumptions — least-sure first:
  ⚠ RESOLVED at the front: the first draft was line-based and would have red-ed this repo (real deltas are multi-line); corrected to multi-line + open-only. One real malformed OPEN delta (onboarding-align, missing evidence) was found and fixed — the guard's first catch.
  - [x] scope strictly to the "### Competency deltas" block, never the whole file — confirmed (gherkin examples elsewhere are not deltas)
  - [x] folded/rejected entries are skipped (historical) — confirmed; only open (and malformed-status) entries are enforced

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: well-formed deltas pass the guard
  Given a task whose deltas block has valid open + folded lines (each with evidence)
  When I run `add.py check`
  Then a "deltas well-formed" check appears and the run does not fail on it

Scenario: unknown competency fails
  Given a deltas-block line "- [XYZ · open] x (evidence: e)"
  When I run `add.py check`
  Then check FAILS (exit 1) with a reason naming "unknown_competency"
  And nothing is written to disk

Scenario: unknown status fails
  Given a line "- [TDD · pending] x (evidence: e)"
  When I run `add.py check`
  Then check FAILS (exit 1) with a reason naming "unknown_status"

Scenario: missing evidence fails
  Given a line "- [TDD · open] a learning with no evidence pointer"
  When I run `add.py check`
  Then check FAILS (exit 1) with a reason naming "no_evidence"

Scenario: a malformed line inside an HTML comment is ignored
  Given a block with a valid delta AND a commented "<!-- - [XYZ · bogus] … -->" line
  When I run `add.py check`
  Then the "deltas well-formed" check passes (exit 0) — the comment is skipped

Scenario: a multi-line open delta with evidence on a continuation line passes
  Given an open delta whose tag line wraps and whose "(evidence: …)" is on the next line
  When I run `add.py check`
  Then the "deltas well-formed" check passes (exit 0)

Scenario: a folded historical delta is not re-validated
  Given a folded multi-line delta that does NOT carry an inline "(evidence: …)" pointer
  When I run `add.py check`
  Then it does not fail (folded history is skipped, open-only enforcement)
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add.py check    (extended — same command + a new family of checks)

For each task, scan its "### Competency deltas" block (skip HTML-comment lines). Group lines into
ENTRIES: a tag line `- [<tok> · <tok>]` starts an entry; following lines until the next tag line /
blank / end-of-block are its continuation. A line without the `· ` in-bracket separator (e.g. a
`- [x]` checkbox or prose) is NOT a tag and starts no entry.

For each entry whose status is NOT `folded`/`rejected` (open-only — history is not retrofitted),
the entry's full unit MUST satisfy:
    tag = [<COMP> · <status>]   COMP ∈ {DDD,SDD,UDD,TDD,ADD}   status ∈ {open,folded,rejected}
    an `(evidence: …)` pointer appears somewhere in the unit

Emit one check per task with ≥1 delta-attempt:
    PASS  task '<slug>' deltas well-formed
    FAIL  task '<slug>' deltas well-formed: <code> -> <offending tag line>
    code ∈ { unknown_competency | unknown_status | no_evidence | malformed_delta }

Any FAIL makes `check` exit 1 (fail-closed). READ-ONLY. Both text and --json honor it (the failed
check joins the checks list and lowers `passed`). Reuse DELTA_RE for the valid shape; classify a
non-historical attempt that fails it into one of the four codes.
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit)   <!-- approved 2026-06-03 (one-approval front, revised to multi-line/open-only); changing it now = change request back to SPECIFY. -->
Least-sure flag surfaced at freeze: ⚠ [contract] open-only — a malformed FOLDED delta is never caught (no-retrofit); ⚠ [contract] entry boundary = next tag/blank/end. Human approved with both in view.
<!-- The freeze IS the one approval. Lead it with the bundle's least-sure flag: the 1–2 points
     most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], with why + cost.
     The §1 ⚠ assumptions are its first feeder; a flag may point at a scenario or the contract too. See run.md. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: one test per scenario (7)
Plan (one test per scenario, asserting behavior not internals):
  - test_well_formed_deltas_pass: valid open+folded / `check` / assert "deltas well-formed" appears, exit 0
  - test_unknown_competency_fails: "[XYZ · open]" / `check` / assert exit 1 + "unknown_competency"
  - test_unknown_status_fails: "[TDD · pending]" / `check` / assert exit 1 + "unknown_status"
  - test_missing_evidence_fails: open entry, no evidence anywhere / `check` / assert exit 1 + "no_evidence"
  - test_comment_malformed_ignored: valid delta + commented malformed / `check` / assert exit 0 + "deltas well-formed"
  - test_multiline_open_evidence_on_continuation_passes: open tag line + "(evidence:)" on next line / `check` / assert exit 0
  - test_folded_multiline_without_evidence_skipped: folded multi-line, no evidence / `check` / assert it does not fail

Tests live in: `add-method/tooling/test_deltas_lint.py` · MUST run red (check has no delta lint yet) before Build.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [ ] all tests pass
- [ ] coverage did not decrease
- [ ] no test or contract was altered during build
- [ ] concurrency / timing of the risky operation is safe
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### GATE RECORD
Outcome: PASS  (conservative dial: worker B returned ESCALATE — NOT auto-resolved; a human recorded this gate)
Evidence: full suite 256 green (deltas-lint 7/7); the real repo's own `add.py check` emits 17 "deltas
          well-formed" PASS checks, 0 failed; read-only guard, no test weakened, contract §1-§3 untouched.
Reviewed by: human (Tin) via orchestrator-presented evidence + diff review · date: 2026-06-03

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the count of `deltas well-formed` FAIL checks in CI `add.py check`
Spec delta for the next loop: a malformed FOLDED delta is currently never caught (open-only) — if history
hygiene ever matters, a `--strict` mode could lint all statuses.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] the conservative autonomy dial got its first real parallel-run exercise: worker B returned
  ESCALATE (not PASS) and a human recorded the verify gate — the dial's "stop for the human" row works
  (evidence: v10 deltas-lint gate is human-recorded; deltas-report ran auto in the same milestone).
- [TDD · folded] linting a grammar needs TWO regexes — a broad attempt-detector and the strict valid-shape
  one; conflating them would either miss malformed attempts or false-skip them (evidence: worker B's
  _TAG_BROAD_RE vs _DELTA_RE split, accepted at review as distinct abstractions).
