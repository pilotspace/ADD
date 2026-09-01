---
type: Task
title: The run line the skill tells you to copy is a line that earns a bound receipt
status: direction
depth: quick
milestone: first-run-truth
scope:
  - add-method/skill/add
  - add-method/tests/skill
gives:
  - S1 the `add run` idiom as printed in SKILL.md, its cookbook, and phases/verify.md
generated: { by: add/3.3.0, at: 2026-09-01 }
verified:
  - { by: "Tin Dang", at: 2026-09-01, act: freeze, authority: human, direction: "sha256:4b67eb94d4553839" }
---
## CARD
goal: The `add run` line the skill prints, copied verbatim, earns a `test-ids` receipt — because the line itself shows the wrapped command writing the report that `run` reads.
why: SKILL.md:102, SKILL.md:152 (the cookbook, the line the file labels "copy a line") and phases/verify.md:9 all print `add run <slug> --junitxml "${TMPDIR:-/tmp}/add-run.xml" -- <test cmd>`. The engine never hands that path to the wrapped command — `subprocess.run` at add.py:2419 passes the argv through unchanged — so `--junitxml` on `add run` is READ-ONLY: `extract_ids` finds no report, `_report_predates_run` fires, and the receipt records `kind: command-exit`. An empty `reported` set means every `covers:` referent is unbound, and the gate refuses the PASS at add.py:3708 naming `unbound_covers` — a message that says nothing about the missing flag on the user's own command. This is the FIRST receipt a new user ever earns, on the one line the file tells them to copy. This repo's own receipts prove the correct idiom (`.add/tasks/direct-lane-size-gate.d/runs/4.md:5` carries `--junitxml` inside the wrapped command), and `.add/tasks/receipt-artifact-leak.md:59` already recorded the lesson — it just never reached the shipped skill. `domains.md:45-47` is the only file in the corpus that happens to show the right shape, and it never states it as the rule.
beat: direction · next: add freeze receipt-idiom-truth

## RULES
<must>
- M1 Every printed `add run` example shows the WRAPPED command writing the JUnit report, at the same path `--junitxml` reads.
- M2 `phases/verify.md` states plainly that `run` only READS the report and the wrapped command must write it.
- M3 A guard asserts every `add run` example across the shipped skill tree satisfies M1, enumerated from the files rather than from a hand list.
- M4 SKILL.md stays at or under its pinned line count — the change is funded by compression, never by a budget bump.
</must>
<reject>
- R:HOLLOWRUN a printed run example must never produce a `command-exit` receipt when copied verbatim -> "R:HOLLOWRUN"
</reject>

## ASSUMPTIONS
- A1 [which] covers: S1 · the request does not say which test runner to show; taking pytest's `--junitxml`, because it is what this repo runs and what every existing example already assumes -> if wrong a non-pytest reader must translate one flag · probe: the example names its runner explicitly rather than saying `<test cmd>` alone.
- A2 [absent] covers: S1 · the request does not say what a MISSING report should do; taking the incumbent behaviour unchanged — the receipt honestly records `command-exit` and the gate refuses a bound rule -> if wrong the fix hides the failure instead of preventing it · probe: no engine behaviour changes in this task.
- A3 [experience] covers: S1 · the request does not say what the reader needs; taking a copy-pasteable line showing the path TWICE with a one-clause reason, because the failure is invisible until the gate refuses far downstream -> if wrong the reader copies the shape without understanding it and drifts on their next command · probe: the verify guide states the read/write split in words, not only in the example.
- A4 [who] covers: S1 · n/a · a printed example is read identically by every actor.
- A5 [when] covers: S1 · n/a · documentation has no temporal boundary; nothing already recorded is rewritten.
- A6 [order] covers: S1 · n/a · the three printed sites are independent of one another.
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: the three printed `add run` examples show the wrapped command carrying its own `--junitxml` at the same path; `verify.md` gains one clause stating run READS and the command WRITES; a new guard enumerates run examples from the skill tree and asserts the shape. Funded inside the SKILL.md line pin.
scope: add-method/skill/add, add-method/tests/skill

## EDGES
- E1 `domains.md:45-47`, which already shows the correct shape with a non-pytest command — must keep passing the new guard.
- E2 an example that deliberately shows a FAILING or receipt-less run — the guard must not demand a report where none is the point.
- E3 the SKILL.md line pin — the edit must land at or under it (M4).

## CHECKS
- test_every_printed_run_example_writes_its_report · covers: M1, M3, R:HOLLOWRUN · examples enumerated from the skill tree, each shows the path twice.
- test_verify_states_run_only_reads_the_report · covers: M2, A3 · the read/write split is stated in words.
- test_the_domains_example_still_passes · covers: E1, A1 · the non-pytest example satisfies the guard.
- test_a_deliberately_receiptless_example_is_not_flagged · covers: E2 · the guard scopes itself to bound examples.
- test_skill_md_is_within_its_line_pin · covers: M4, E3 · the budget holds after the edit.
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
