<!-- ADD:BEGIN — managed by `add.py sync-guidelines`; do not edit inside -->
## ADD — how to work in this repo

**ADD (AI-Driven Development)** — you, the AI, drive the build; the human owns direction
and verification. Works for any agent (Claude · Cursor · Copilot · Codex) through the CLI
alone. Before you touch code, orient:

1. `python3 .add/tooling/cli.py status` — your resume point; read it first each session.
2. `.add/PROJECT.md` — the thin read-first index (goal · `invariants:` · pointers into
   `.add/specs/`, the 5-DD standing picture); drill into a spec on demand.

**Size the work before you spend ceremony on it.** The floor is checked FIRST and always wins:
security · data · architecture, a `gives:` surface something else consumes, or frozen scope → a
node, however small. Security is a HARD-STOP. Under that floor, route by kind and size — you
route and go, the human vetoes after ("make it a task" always wins):

| the change (kind · size) | route | effort · review | what persists |
|---|---|---|---|
| **mechanical**, or small **behavior** — ≤3 adjacent files, one-sitting diff, zero unknowns | direct — no node | inline card before the edit · red→green · `invariants:` hold · self-review | the commit + one `add learn` line |
| one **behavior** worth a frozen contract | Task, `--depth quick` or `standard` | advisor pressure-test at direction · human freeze · receipt-backed verify | the node · its frozen contract · a run receipt |
| an unanswered **question** — investigate · evaluate · research | Task, `--kind explore` | a hard budget · cited findings · sufficiency gate | the node + its cited `## FINDINGS` |
| a **theme**, or a slice spanning tasks | Milestone | persona-led plan · breadth-first task list · goal-gate at close | the milestone + its task nodes |

Effort scales UP with the rung, and review scales with it — **skipped ceremony is never skipped review**.
A direct change still writes its check and runs it red; it simply does not persist a node to prove it
did. A change that fits no rung cleanly sizes UP to the next one.

Each task drafts the **specification bundle** (Spec · Contract · Tests & Scenarios) —
ONE human approval at the frozen contract, then a self-driving build→verify run.
Non-negotiable: Never weaken a test or edit a frozen contract to pass a build; a
security finding is always HARD-STOP. PROJECT.md `invariants:` bind EVERY task — the
artifact must hold under the BARE declared runtime.

Roster (`agents/*.md`): `add-worker` runs each beat (direction · build · verify · persona);
`add-advisor` is the second mind it spawns to plan, pressure-test, or resolve a delegable
ambiguity. Each loads the beat's guide + the best-fit `.add/personas/` persona — personas
carry the expertise, the agent carries the discipline.

On Claude Code the `add` skill drives this loop; other agents follow the steps above.
Book: https://pilotspace.github.io/ADD/. Edit outside the markers.
<!-- ADD:END -->
