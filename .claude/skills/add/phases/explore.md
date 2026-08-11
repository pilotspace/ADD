# Explore — the research lane (find out, then commit)

Some work's deliverable is an **answer**, not an edit: investigate a defect, evaluate a library,
research an approach, survey prior art on the web. Intake routes that here (`intake.md` § Explore).
An explore runs on the **existing Task lifecycle** — same node, same freeze, same gate — but its
contract is a set of questions and its green is a sufficient answer. No new node type, no new verb.

## The node — questions in, findings out

```bash
add new Task <slug> --title "..." --kind explore [--milestone m]
```

`kind: explore` marks the shape. Author the node so each section carries the research meaning:

- **`## RULES`** — each `Must` is a **question the explore must answer**, stated so "answered" is
  judgeable (`M1 which lock-free queue fits our latency budget — with the evidence`). A `Reject`
  names what the explore must not do (`R:SCOPE_CREEP building the thing instead of answering`).
- **`## PLAN`** — the **budget line is required**: tool calls, sources, or wall-clock — one hard
  number (`budget: ~40 tool calls / 15 sources`). The scope tokens stay what they always are.
- **`## CHECKS`** — acceptance form (flexible-TDD): one line per question, `covers:` bound, each
  judged at the gate against `## FINDINGS` — not by pytest.
- **`## FINDINGS`** — starts empty. An explore starts with questions, not answers; the section is
  demanded by the gate, never by the graph (an unresolved `#findings` fragment is only `info`).

## The freeze seam — questions + budget, one approval

The human approves **what will be asked and what it may cost** — that is this lane's freeze. Present
it via `gate.md` exactly as any Direction; the sensitivity floor computes unchanged, and a
security-scoped question keeps its human floor.

## The loop — query → read → reflect → refine

Run the research as a loop, not a sweep:

1. **Query** — start **broad**, then progressively **narrow**; follow the evidence, not the plan.
2. **Read** — primary sources over summaries; record where each fact came from as you go.
3. **Reflect** — after each read, judge: which frozen questions moved? what gap remains? is a
   question now answerable, dead, or split?
4. **Refine** — the next query targets the largest remaining gap. Repeat.

Two stop conditions, both explicit:

- **Sufficiency** — every frozen question is answered well enough to act on, judged against the
  questions as frozen — never against enthusiasm for one more source.
- **The declared budget is the hard backstop** — when it is spent, the loop stops even unfinished;
  unanswered questions are recorded open, and more budget is a re-freeze, not a quiet overrun.

Delegation fans out freely here: read-only research streams need no wave and no worktree
(`streams.md`) — findings are facts, and facts merge.

## Compress — the brief is the deliverable

Write `## FINDINGS` as a **compressed, cited brief** — roughly a page, never a transcript:

- one entry per frozen question: `F<n> (answers M<n>) · the finding · (evidence: <source/link/ref>)`;
- every claim carries its evidence ref — an uncited finding is an opinion;
- raw tool output, quotes-in-full, and dead ends are **discarded**, not appended;
- questions the budget left open are listed as open, each with what it would take to close.

## The sufficiency gate — one recorded outcome

```bash
add gate <slug> PASS --by "<name>"   # findings-only: the gate reads ## FINDINGS directly
```

The gate records **which questions closed and which stayed open** — a findings-only explore stamps
evidence kind `sources` with the closed tally; every frozen question needs an evidence-carrying
`F` line or the gate refuses naming the open ones. The verdict set is unchanged — PASS
(sufficient), RISK-ACCEPTED (signed: acting despite named open questions), HARD-STOP. Record a run
receipt (`add run`) ONLY when **every** frozen question binds to an executable check — a recorded
receipt puts the normal receipt path in charge, and a findings-only question would then hold the
gate as unbound; a mixed explore keeps executable output as a cited evidence ref inside
`## FINDINGS` instead. **Security is a HARD-STOP here too**: a finding surfaced *by research*
escalates to the human exactly as one surfaced by tests.

## Downstream — findings seed the next Direction

The brief is a frozen fragment neighbors consume. A follow-on task declares:

```yaml
needs: [/tasks/<explore-slug>.md#findings]
```

and `add brief` compiles the findings into that task's Direction prompt — assumptions arrive
pre-discharged as evidence-carried facts instead of priced guesses. This is the lane's whole point:
**explore-first turns the next task's unknowns into knowns** before its contract freezes.

<constraints>
- **Questions freeze like contracts.** Rewriting a frozen question to fit the answer found is the
  same inversion as weakening a check — a real change is a re-freeze.
- **The budget is hard.** Overrun is a recorded re-freeze, never a silent continuation.
- **Findings are facts, not authority.** A brief informs the next freeze; it never replaces one,
  and it never lowers a floor — **security = HARD-STOP**, un-lane-negotiable.
- **No building.** An explore edits no product code; the moment the answer is "now build it",
  that is the next task, through intake.
</constraints>
