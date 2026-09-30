# Explore — when the answer is the deliverable

Use it for "investigate", "evaluate", "research", "why does X happen" — or when one unknown would
shape a contract. Freezing a contract on a guess ships the wrong thing with a perfect test run.

## 1 · Direction — questions and a budget, sealed

Write `.add/tasks/<slug>.md` with `kind: explore` and:

- **CARD** — `goal:` the decision this research feeds · `why:`.
- **QUESTIONS** — `Q<n> <an answerable question> → feeds: <the decision it informs>`. One per line.
- **BUDGET** — a hard ceiling, e.g. `≤ 40 tool calls · ≤ 8 sources · ≤ 1 spike`. At the ceiling
  you stop and report what is answered.

Commit `freeze(<slug>): <goal>`. The questions and budget are now sealed.

## 2 · Investigate

Read code, run experiments, read docs and sources. Split the work into disjoint questions and
answer them in turn; the subagent budget in SKILL.md holds here too — at most one, in the
foreground, for a question whose reading would flood your context. Spikes and prototypes are
throwaway — a scratch branch or directory, labelled as such — never production code.

## 3 · Findings — cited or not a finding

```markdown
## FINDINGS
- Q1 <answer> · confidence: high | medium | low · evidence: <file:line | command → output | URL>
- Q2 unanswered within budget · what it would take: <next step>
```

No citation, no finding. A finding that shows a question was the wrong question: note it, and
refreeze with the corrected question rather than rewriting the sealed one silently.

## 4 · Verify and verdict

Seal intact: `git diff <freeze> HEAD -- .add/tasks/<slug>.md` prints nothing (FINDINGS and EVIDENCE
stay uncommitted until the verify commit). Every question answered or declared unanswered, every
answer cited, each answer good enough to decide on. Verdict in `## EVIDENCE`:
`PASS` (answered and cited) · `RISK-ACCEPTED` (partial, stated plainly) · `HARD-STOP` (a security
finding). Commit `verify(<slug>): <verdict>` together with the FINDINGS.

## 5 · Hand off

Findings that shape work become Tasks whose ASSUMPTIONS cite them:
`A1 … · found: <answer> (evidence: tasks/<slug>.md Q2)`. Durable lessons go to `.add/specs/`.
