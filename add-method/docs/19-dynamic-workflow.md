# 19 · Explore — when the answer is the deliverable

[← 07 Setup and the four lanes](./07-setup-and-lanes.md) · [Contents](./README.md) · Next: [08 Parallel work — worktrees →](./08-parallel-work.md)

---

Some work's deliverable is an **answer**, not an edit: investigate a defect, evaluate a library, survey prior art, find out why X happens. And some tasks hinge on one unknown that would change the contract's shape. For both, the Explore lane comes first — because a contract sealed on a guess ships the wrong thing with a perfect test run.

Explore is an ordinary task file with `kind: explore`. It runs the same seal, the same verify and the same verdicts; only the sections differ.

## 1 · Direction — questions and a budget, sealed

```markdown
---
type: Task
title: pick a money type
status: direction
kind: explore
---
## CARD
goal: decide how transfer amounts are represented before transfer-own-accounts is sealed
why: floats lose cents; the choice shapes every payments contract

## QUESTIONS
- Q1 does the database driver round-trip Decimal without loss? → feeds: the column type
- Q2 does the JSON layer serialize Decimal as a string or a number? → feeds: the API contract
- Q3 what do the existing account balances use today? → feeds: whether a migration is needed

## BUDGET
≤ 30 tool calls · ≤ 6 sources · ≤ 1 spike
```

One answerable question per line, each naming the decision it feeds. The budget is a hard ceiling: at the ceiling you stop and report what is answered.

Commit `freeze(<slug>): <goal>`. The questions and the budget are now sealed — rewriting a sealed question to fit the answer you found is the same inversion as weakening a check.

## 2 · Investigate

Read code, run experiments, read docs and sources. Split the work into disjoint questions and answer them in turn; the subagent budget holds here too — at most one, in the foreground, for a question whose reading would flood your context. Spikes and prototypes are throwaway — a scratch branch or directory, labelled as such — never production code.

## 3 · Findings — cited, or not a finding

```markdown
## FINDINGS
- Q1 yes — the driver maps NUMERIC(19,4) to Decimal and back exactly · confidence: high · evidence: `python spike/roundtrip.py` → 10000/10000 equal
- Q2 as a number by default, losing precision above 2^53 · confidence: high · evidence: src/api/json.py:22
- Q3 unanswered within budget · what it would take: read the production schema dump
```

No citation, no finding. A finding that shows a question was the wrong question is noted, and the task is refrozen with the corrected question — never silently rewritten.

## 4 · Verify and verdict

The seal check is the same: `git diff <freeze> HEAD -- .add/tasks/<slug>.md` prints nothing (FINDINGS and EVIDENCE stay uncommitted until the verify commit). Every question is answered or declared unanswered, every answer is cited, and each answer is good enough to decide on. The verdict goes in `## EVIDENCE`:

- `PASS` — answered and cited.
- `RISK-ACCEPTED` — partly answered, stated plainly.
- `HARD-STOP` — research surfaced a security finding.

Commit `verify(<slug>): <verdict>` together with the FINDINGS.

## 5 · Hand off

Findings that shape work become tasks whose assumptions cite them, so the guess arrives already discharged:

```markdown
- A1 [which] the money type is not stated → Decimal, serialized as a string · found: JSON numbers lose precision (evidence: tasks/pick-a-money-type.md Q2)
```

Durable lessons go to `.add/specs/`.

## Smaller than an explore: check the assumption now

Not every unknown needs a lane. When a guess in Direction can be checked in a minute, check it and append the answer to the assumption line: `· found: <answer> (evidence: <file:line | command>)`. A priced guess is legitimate; a discharged one is better. A guess that grows past a quick probe is the signal to open an Explore task instead.

## Reads are free; writes serialize

Reading never needs the seal: research questions, spec reads and codebase surveys can run in any order, and their facts merge. The moment a stream would *write* — an edit, a seal, a decision that binds a contract — it rejoins the serialized path described in [08 · Parallel work](./08-parallel-work.md).
