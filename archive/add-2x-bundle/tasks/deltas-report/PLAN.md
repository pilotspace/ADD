# TASK: Read-only 'add.py deltas' report (open deltas grouped by competency)

slug: deltas-report · created: 2026-06-03 · stage: mvp
autonomy: auto   <!-- read-only, deterministic, decides nothing (risk ≈ status). Worker may auto-PASS on evidence. -->
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `add.py deltas` — a read-only report of OPEN competency deltas, grouped by competency
Framings weighed: read-only report (chosen) · a fold-applying command · auto-folding into `status`
Must:
  - scan every `.add/tasks/*/TASK.md` "### Competency deltas" block for delta lines
  - show only `open` deltas (exclude `folded`/`rejected`), grouped by competency in canonical order (DDD·SDD·UDD·TDD·ADD)
  - print a per-competency count and a grand total
  - support `--json` for a single machine-readable object
  - be strictly READ-ONLY — never write state.json or any file
After:
  - in one command, a human sees every open delta grouped by competency before running the fold ritual
Reject / edge (this is a REPORT, not a guard — so these are graceful, never errors):
  - no open deltas anywhere -> print "no open deltas." and exit 0
  - a non-delta or malformed line -> skipped silently (flagging malformed deltas is deltas-lint's job, not this one)
Assumptions — least-sure first:
  ⚠ report SKIPS malformed lines rather than flagging them — least sure because it splits responsibility with deltas-lint; if wrong: a malformed open delta stays invisible until lint runs (cost: a delta could be missed at fold)
  - [ ] reuse the existing `DELTA_RE` (add.py:1079) rather than a new parser — confirm
  - [ ] group order is the canonical five-competency order, not alphabetical — confirm

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: group open deltas by competency
  Given two tasks whose OBSERVE blocks hold open deltas in TDD (x2) and ADD (x1)
  When I run `add.py deltas`
  Then the output groups them under TDD (2) and ADD (1) with a total of 3
  And state.json is unchanged

Scenario: exclude folded and rejected
  Given a task with one open, one folded, and one rejected delta
  When I run `add.py deltas`
  Then only the open delta is shown
  And the folded and rejected lines do not appear

Scenario: no open deltas
  Given no task has any open delta
  When I run `add.py deltas`
  Then the output is "no open deltas." and the exit code is 0

Scenario: machine-readable output
  Given open deltas exist in two competencies
  When I run `add.py deltas --json`
  Then stdout is one JSON object with a numeric `total` and a `by_competency` map
  And nothing is written to disk

Scenario: malformed line is skipped, not fatal
  Given a "### Competency deltas" block containing a malformed (non-grammar) line
  When I run `add.py deltas`
  Then the command exits 0 and reports only the well-formed open deltas
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add.py deltas [--json]

text (default) -> stdout:
    open competency deltas (<total> total):
      <COMP> (<n>):
        - <text>  [<slug>]
    ...                              # groups in canonical order DDD·SDD·UDD·TDD·ADD
  when none -> "no open deltas."

--json -> ONE object to stdout (nothing else):
    { "total": <int>,
      "by_competency": { "<COMP>": [ { "task": <slug>, "text": <str>, "evidence": <str> } ] } }

exit 0 ALWAYS (read-only report; it never fails)
Reads: .add/tasks/*/TASK.md  "### Competency deltas" blocks.   Writes: NOTHING.
Parser: reuse DELTA_RE (add.py:1079); competency/status taxonomy per deltas.md.
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit)   <!-- approved 2026-06-03 (one-approval front); changing it now = change request back to SPECIFY. -->
Least-sure flag surfaced at freeze: ⚠ [spec/contract] report skips malformed lines (delegated to deltas-lint); ⚠ [contract] text layout frozen by tests. Human approved with both in view.
<!-- The freeze IS the one approval. Lead it with the bundle's least-sure flag: the 1–2 points
     most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], with why + cost.
     The §1 ⚠ assumptions are its first feeder; a flag may point at a scenario or the contract too. See run.md. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: one test per scenario (5)
Plan (one test per scenario, asserting behavior not internals):
  - test_groups_open_by_competency: write open TDDx2 + ADDx1 / run `deltas` / assert counts + total + state.json unchanged
  - test_excludes_folded_and_rejected: open+folded+rejected / run `deltas` / assert only open shown
  - test_no_open_deltas_message: none open / run `deltas` / assert "no open deltas." + exit 0
  - test_json_shape: open in 2 comps / run `deltas --json` / assert one dict with numeric total + by_competency map
  - test_malformed_line_skipped: malformed line in block / run `deltas` / assert exit 0 + only valid open shown

Tests live in: `add-method/tooling/test_deltas_report.py` · MUST run red (no `deltas` command) before Build.

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
Outcome: PASS  (auto-resolved under autonomy=auto by stream-worker A, then orchestrator-verified at merge)
Evidence: full suite 249 green excluding the not-yet-built deltas-lint tests; deltas-report 5/5;
          parity guards (tree/bundle/cospecify) green; no test weakened; contract §1-§3 untouched; read-only.
Residue: none security/concurrency/architecture (read-only report). One DRY smell folded to a delta below.
Reviewed by: orchestrator (manual diff review of cmd_deltas + test_min_pillar) · date: 2026-06-03

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>
Spec delta for the next loop: <what production taught you>

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] cmd_deltas duplicated the delta grammar as a new module-level _DELTA_RE instead of
  reusing the existing one — two unguarded sources of truth for the regex (evidence: worker A residue;
  _DELTA_RE added alongside the original ~add.py:1079).
- [TDD · folded] the report shows only a delta's first line; a multi-line open delta's text is truncated
  (evidence: onboarding-align's wrapped open delta; report tests do not cover the multi-line shape).
- [ADD · folded] the streams spawn forked the worker's worktree from a STALE base (e7e2171, pre-v10), not
  current HEAD — the worker had to recreate the frozen test byte-identically; streams.md should add
  "verify worktree base == HEAD after committing the front" (evidence: worker A worktree HEAD = e7e2171).
