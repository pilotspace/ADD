# TASK: deltas/report renders full multi-line delta (no first-line truncation)

slug: deltas-multiline-render · created: 2026-06-04 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
autonomy: auto

> **CLOSED AS ALREADY-SATISFIED** (2026-06-04). This follow-up was routed out of the
> v10/v12 fold from a v10-era `deltas-report` TDD delta describing first-line truncation.
> Investigation at intake found the gap was **already closed by v11 commit `1b817c0`**
> ("fold-nudge + multi-line delta render + failure-path tests") and is **already guarded**
> by a regression test. No build was manufactured — the method forbids a fabricated task
> as much as a silent skip. The evidence is recorded in §6.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `add.py deltas` (and the milestone report) render an open competency delta whose
learning wraps across physical lines in FULL — never truncated to its first line, and never
dropping a `(evidence: …)` clause that lands on a continuation line.
Framings weighed: render-in-full (chosen) · re-wrap-for-terminal · leave-truncated (rejected)
Must:
  - An open delta spanning a tag line + indented continuation line(s) is read and rendered with
    ALL of its learning text, in both the human (`deltas`) and `--json` views.
  - The `(evidence: …)` clause is captured even when it sits on a continuation line.
Reject:
  - n/a — read-only reporting surface; no inputs to reject (a malformed delta line is skipped,
    already covered by `test_malformed_line_skipped`).
After:
  - The lint, the `deltas` command, and the report agree on the multi-line shape (one shared
    collector `_collect_open_deltas` / `_task_prose` joins continuations).
Assumptions — least-sure first:
  ⚠ "render in full" means "no learning text dropped" (joined onto one readable line), NOT
    "preserve the original physical line breaks" — least sure because a purist could read it
    the second way; if wrong: the human view would need a re-wrap pass (small, additive).
  - [x] the shared collector is the single source for both views — confirmed by reading
    `_collect_open_deltas` (line 1642) + `_task_prose` (line 1194).

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: multi-line open delta rendered in full
  Given a TASK.md whose §7 has "- [SDD · open] <clause-one>,\n  <clause-two> (evidence: e)"
  When I run `add.py deltas` (and `add.py deltas --json`)
  Then the rendered text contains both <clause-one> and <clause-two>
  And the captured evidence equals "e" (not lost on the continuation line)
```

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add.py deltas [--json]
  human  -> "    - <full joined learning>  [<task>]"   (per open delta, grouped by competency)
  --json -> { total, by_competency: { COMP: [ {task, text:<full>, evidence:<full>} ] } }
Schema: read-only; no state mutation. Collector: _collect_open_deltas / _task_prose.
```

Status: FROZEN @ v1 (pre-existing — the shape was frozen and shipped in v11; this task adopts it).

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: the multi-line shape is covered by an EXISTING regression test.
Covering test (pre-existing): `add-method/tooling/test_deltas_report.py::test_multiline_open_delta_not_truncated`
  - arrange: a TASK.md with a wrapped SDD open delta + evidence on the continuation line
  - assert: `entry["text"]` contains "returning forbidden"; `entry["evidence"]` == the full clause
No new test authored — writing a duplicate of a green guard would be redundant, not red.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

No build. The implementation already exists: `_collect_open_deltas` (add.py:1642) groups a tag
line with its continuation lines and joins them; `cmd_deltas` (add.py:1697) prints the full
`e['text']`. Delivered by v11 commit `1b817c0`.

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — `test_multiline_open_delta_not_truncated` is green in the suite
- [x] coverage did not decrease — no code changed; the guard already exists
- [x] no test or contract was altered — none touched
- [x] concurrency / timing — n/a (pure read of files, no shared mutable state)
- [x] no exposed secrets, injection openings, or unexpected dependencies — read-only reporting
- [x] layering & dependencies follow CONVENTIONS.md — uses the shared collector, no new surface
- [x] a person reviewed and approved the change — human chose "close as already-satisfied" at intake (2026-06-04)

### GATE RECORD
Outcome: PASS
Evidence (already-satisfied, no build):
  1. v11 commit `1b817c0` ("fold-nudge + multi-line delta render + failure-path tests")
  2. existing guard `test_deltas_report.py::test_multiline_open_delta_not_truncated`
  3. empirical run (2026-06-04): `add.py deltas` on a wrapped SDD delta renders
     "the export endpoint must reject a cross-tenant token, returning forbidden not not_found"
     in full (continuation text present); `--json` carries text + evidence intact.
Reviewed by: Tin Dang · date: 2026-06-04

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): per-task delta render fidelity (text dropped? evidence lost?)
Spec delta for the next loop: the fold that routed this follow-up out should check whether a
routed delta was ALREADY closed by interim work before scoping it as open — a delta authored at
foundation-version N can be silently delivered by version N+1 before the fold reads it.

### Competency deltas
- [ADD · folded] a fold can route an already-closed delta as an open follow-up; the fold ritual
  should verify a routed delta's gap still exists against current code before scoping it
  (evidence: deltas-multiline-render arrived open but was already delivered by v11 `1b817c0`)
