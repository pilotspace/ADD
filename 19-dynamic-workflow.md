# 19 · The dynamic path — explore, steer, fan out

ADD 3.0 shipped one fixed route: every request became a contract, every contract a build, every
build a gate. That is the right route for work you already understand — and the wrong first move
for work you don't. 3.1 makes the **path** adaptive while the **trust spine stays byte-identical**:
uncertainty gets a lane, steering gets a stamp, research gets a receipt. Nothing here weakens a
floor; adaptivity changes the route, never what passes.

The patterns are field-imports, not inventions: the workflow/agent split and the
research-loop anatomy (clarify → budget → query → read → reflect → refine → compress → stop) from
the published agent-engineering literature, plan-and-execute replanning, and
parallelize-reads-serialize-writes. What ADD adds is the part the field leaves informal: **every
dynamic move lands as a recorded, refusable artifact.**

## Route by uncertainty, not only by size

Intake (`intake.md`) always sized a request by scope and sensitivity. It now tallies a third axis
first: **the unknowns whose answer would change the contract's shape**. Trivia and build detail
don't count; a latent requirement you cannot yet state as a measurable target does.

- The **closed floor is checked first and always wins** — security · data · architecture size up,
  whatever the tally says.
- Among the lanes the floor allows, **uncertainty dominates size**: ONE contract-shaping unknown
  already argues Explore-first. Freezing a contract on a guess is how a plausible task ships the
  wrong thing with perfect receipts.
- The human still vetoes the route, as with every lane.

## The Explore lane — when the answer is the deliverable

Some work's deliverable is an **answer**, not an edit: investigate a defect, evaluate a library,
survey prior art. That work now has a first-class lane on the **existing Task lifecycle** — no new
node type, no new verb:

```bash
add new Task <slug> --title "..." --kind explore
```

- **Questions are the contract.** Each `Must` in `## RULES` is a question the explore must answer,
  stated so "answered" is judgeable. Questions freeze like contracts — rewriting a frozen question
  to fit the answer found is the same inversion as weakening a check.
- **The budget is hard.** `## PLAN` carries one hard number (tool calls, sources, or wall-clock).
  The engine refuses to freeze a budgetless explore (`R:UNBOUNDED`). Overrun is a recorded
  re-freeze, never a silent continuation.
- **One approval.** The freeze seam is *what will be asked and what it may cost* — the same single
  human approval every task gets, at the same place.
- **The loop is query → read → reflect → refine**, stopped by sufficiency (every frozen question
  answered well enough to act on) or by the budget — both explicit.
- **The deliverable is `## FINDINGS`**: a compressed, cited brief — one line per frozen question,
  `F<n> (answers M<n>) · the finding · (evidence: <ref>)`. An uncited finding is an opinion, and
  the engine treats it as one.

The sufficiency gate is engine-enforced. A findings-only explore gates directly on its brief:

```bash
add gate <slug> PASS --by "<name>"
```

The gate refuses an unfrozen explore (`R:UNFROZEN_EXPLORE` — the questions+budget approval IS the
lane's human seam), refuses when any frozen question lacks an evidence-carrying finding
(`R:HOLLOW_EXPLORE`, naming the open ones), refuses post-freeze edits to the questions exactly as
the drift tripwire does everywhere else, and records a passing verdict with evidence kind
`sources` and the closed tally (`closed: "3/3"`). Security keeps its floor: a finding surfaced *by
research* escalates to the human exactly as one surfaced by tests.

Downstream, the brief is a frozen fragment neighbors consume:

```yaml
needs:
  - /tasks/<explore-slug>.md#findings
```

`add brief` compiles those findings into the next task's Direction prompt — assumptions arrive
pre-discharged as evidence-carried facts. That is the lane's whole point: **explore-first turns
the next contract's unknowns into knowns before it freezes.**

## Micro-spikes — discharge an assumption instead of pricing it

Direction's `## ASSUMPTIONS` always priced a guess (`if wrong → consequence`). When a guess is
cheaply checkable, a **micro-spike** discharges it instead: run the two-minute probe, then record
what was found on the assumption line — `found: <what>` with its evidence ref, on one physical
line. A priced guess stays legitimate; a discharged one is simply better. An assumption that
grows past a quick probe is the signal to route the question through the Explore lane instead.

## Steering vs the contract — `add replan`

Builds discover things. A strategy that turned out wrong, a sequencing change, a constraint the
plan didn't know — that is **steering**, and it now lands as a recorded, additive stamp:

```bash
add replan <slug> --note "pivoting to the sorted-merge approach"
```

The seal is untouched; the note joins the `verified:` trail as an `act: replan` entry, so the turn
is visible in the record instead of silently absorbed. The engine refuses a replan on an unfrozen
task (nothing is being steered) and on a done one (the trail is closed — that lesson belongs in
`add learn`). The boundary is absolute: anything that would move a frozen `gives:`, a Must, or a
check is a **change-request** — reopen and refreeze, never a replan. Steering steers the route;
it never touches the seal (`R:SEAL_TOUCH`).

## Read fan-out — facts merge, decisions serialize

Parallel work (chapter 08) serializes **writes** through waves and worktrees. Reads never needed
that ceremony, and now the method says so: research streams, spec reads, and codebase surveys fan
out freely — **facts merge**. The moment a stream would *write* — an edit, a stamp, a decision
that binds a contract — it re-enters the serialized path (**one write taints the stream**). The
floors are unchanged; fan-out widens what you can learn per hour, not who signs.

## Planning wears a lens

Milestone drafts, intake proposals, and the loop's next-task proposal now load the best-fit
persona whose `flow:` includes **advisor** *before* drafting starts, and the confirmed artifact
records the lens (`add advise <milestone> --persona <p>`). The load is by fit and by roster — a
bundle with no personas skips silently and behaves exactly as before. Chapter 10 covers the
persona system; this is the one addition: **planning is a loading surface too.**

## What never moved

The dynamic path is additive by construction, and the engine enforces the additivity:

| floor | status under the dynamic path |
|---|---|
| security finding | HARD-STOP, everywhere — including findings surfaced by research |
| one human approval at the freeze | unchanged; the Explore lane's freeze IS that approval |
| receipt binding (`covers:` → evidence) | unchanged; findings bind questions the same way |
| frozen contracts move only by refreeze | unchanged; enforced on questions too |
| budgets (skill surface, task depth) | unchanged; explores add a hard research budget |

A project that never uses `--kind explore`, never replans, and seeds no personas runs 3.1 exactly
as it ran 3.0. The dynamic path is there for the day the work is uncertain — which is most days
worth recording.
