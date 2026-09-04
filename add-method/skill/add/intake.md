# Intake — size a request into the right lane

Before a node exists, ADD turns a raw request into correctly-sized scope. **You propose; the human
confirms.** Never create scope without a confirmed proposal.

## Read the request into a task shape (before you size it)

A raw request is intent wrapped in prose. First read it into shape — do this BEFORE choosing a lane:

1. **Restate the intent** in one line — the outcome the human wants, in their world. Can't state it?
   → ask; never guess it.
2. **Extract the latent requirements** — "fast", "secure", "works like X" are measurable targets in
   disguise. Name each.
3. **Name the unstated** — the assumptions, defaults, and edge behavior the prose skips. These are the
   interview agenda; surface them, never silently fill them.
4. **Surface the hidden work** — migrations, new contract surface, risk. This is what separates a real
   task from a wish, and what raises sensitivity.
5. **Tally the unknowns** — count the unstated items and unmeasurable latents from 2–3 whose answer
   would change the contract shape; trivia and build detail do not count. This tally is the third
   routing axis (beside size and sensitivity).

This analysis IS the node's raw material: the restated intent seeds `## RULES`, the latent requirements
seed the target, the unstated is what the interview settles.

## Pick the lane (you route silently; the human vetoes)

Judge the lane FIRST, cheapest that fits. The closed floor is checked first and always wins over the tally;
among the lanes the floor allows, uncertainty dominates size — ONE contract-shaping unknown already
argues Explore-first ("high" is judgment, never a numeric gate):

### Quick — direct, no node
**Refused first, whatever the size.** A change that trips the closed floor (security · data · architecture),
adds or alters a `gives:` surface anything else consumes, or touches frozen scope takes a Task —
however small it is. Only then size it: at most ~3 adjacent files, a diff one
reviewer reads in one sitting, an unknowns tally of zero. Small **new behavior** is admitted — the
lane is bounded by size and blast radius, not by whether the specs already cover it.

**Route and go.** State one line — `quick: <intent> — <fit>` — and proceed. You do NOT wait for a
confirm here; the human vetoes after the fact, and "make it a task" always wins. Task · Explore ·
Milestone keep the confirm-first rule unchanged.

**The receipt** is the commit — its body names the check you ran and its result — plus exactly one learn line:
`add learn <ddd|sdd|udd|tdd|add> "<lesson>" --evidence <sha>` — a real lesson when one was learned,
otherwise the trace `"quick: <intent>"`. That learn line is the ONLY bundle write; a Quick
change never writes under `.add/tasks|runs|milestones`.

**Sizing up reuses today's vocabulary** — no new lane, tier, verb or stamp. medium = a Task at `--depth quick`;
large = a Task at `standard|deep`, or a Milestone when it spans tasks.

**The five steps**, in order:
1. the route line `quick: <intent> — <fit>`;
2. an inline card **in the reply, before the first edit** — intent · edges · the check you will run ·
   the `invariants:` it touches — never written under `.add/`;
3. red→green: new behavior writes or extends its check and runs it RED first; a mechanical change
   runs the check that already covers it;
4. confirm PROJECT.md `invariants:` hold under the bare declared runtime;
5. the receipt above — commit, then the one learn line.

### Task — one atomic node
`add deltas` first — a lesson may already answer it. Fits the active milestone's stated scope, or is a single behavior needing a frozen contract. Run the 3-beat loop: `add new Task <slug> --title "..." --depth quick|standard|deep`, then Direction.
(The node type is a FORMAT vocabulary word — `Task`, `Milestone` — canonically capitalized.)

### Explore — the answer IS the deliverable
Fits when the **primary work is answering questions**, not editing — investigate a defect, evaluate
a library, research an approach or the web — whatever the eventual code size. High unknowns route
here FIRST (explore-first beats freezing a contract on a guess; the human vetoes the routing as with
every lane). One Task node with `--kind explore`: questions are the Musts, a hard budget sits in
PLAN, the deliverable is a cited `## FINDINGS` brief closed by a sufficiency gate
(`phases/explore.md`). An explicit "research X" ask is always this lane. The closed floor holds:
security-scoped questions keep their human floor.

### Project / milestone — a theme or a slice
`add deltas` first — carried lessons shape goal and scope.
A new product theme no active milestone covers, or a slice too big for one task. **Load the best-fit persona
whose `flow:` includes advisor before drafting** (`personas.md` § planning; skip silently if
no personas are seeded — the load is by fit). Draft the milestone first —
**goal · in/out scope · exit criteria · a breadth-first task list** (`slug · depends-on · one
line` each) — confirm it, then create it and list its tasks, recording the lens on the confirmed
milestone: `add advise <milestone> --persona <p>`. (`add milestone-done` is **wired** — it
refuses to close while a goal box is unchecked; `add milestone-archive` retires it once done.)

## The closed floor — what always sizes up

A change touching **security · data · architecture** ALWAYS becomes a real task — never Quick, no matter
how small. **Security is a HARD-STOP everywhere.** New behavior, a new/changed contract, or anything you
would want a frozen `gives:` for → a Task at least. The route is yours; the veto is not — the human
saying "make it a task" always wins. **When in doubt, size up.**

## The ladder — what each rung costs and what it leaves behind

Ceremony falls as you come down this table; **review never does**. Read a row left to right: the
route says what to create, the third column what you still owe, the fourth what survives the session.

| the change (kind · size) | route | effort · review | what persists |
|---|---|---|---|
| **mechanical**, or small **behavior** — ≤3 adjacent files, one-sitting diff, zero unknowns | direct — no node | inline card before the edit · red→green · `invariants:` hold · self-review | the commit + one `add learn` line |
| one **behavior** worth a frozen contract | Task, `--depth quick` or `standard` | advisor pressure-test at direction · human freeze · receipt-backed verify | the node · its frozen contract · a run receipt |
| an unanswered **question** — investigate · evaluate · research | Task, `--kind explore` | a hard budget · cited findings · sufficiency gate | the node + its cited `## FINDINGS` |
| a **theme**, or a slice spanning tasks | Milestone | persona-led plan · breadth-first task list · goal-gate at close | the milestone + its task nodes |

Effort scales UP with the rung, and review scales with it — **skipped ceremony is never skipped review**.
A direct change still writes its check and runs it red; it simply does not persist a node
to prove it did. A change that fits no rung cleanly sizes UP to the next one.

## Change-request — touching already-frozen scope

If the request modifies a **frozen** contract or a shipped promise, it is not new scope — it is a
change-request back to Direction of the affected node (§3.5: the old `gives:` stays, a `refreeze` stamp
lands, dependents that `need:` it are flagged stale). Never fork the truth into a parallel node.

## What you emit (the proposal)

Present it via `gate.md` — open with the ARC (goal · done · plan), render the chosen lane as a guided
choice with its described alternatives. Emit exactly one of:
**Quick is route-and-go — no confirm.** It never waits for the human: state the route line and
proceed. The proposal below is for Task · Explore · Milestone.

- **a classification** — `{ lane, depth, rationale, command }` — `rationale` names WHY (the fit, the
  theme, the slice, the frozen scope touched — and the unknowns tally when it routed); `depth` makes
  ceremony a decision output the human vetoes, never a silent constant; `command` is the exact
  `add …` line. The human confirms first.
- **a rejection** — create nothing: `ask_human` (too ambiguous to size), `frozen_scope` (route as a
  change-request), or `split_required` (spans lanes — propose the smallest correctly-sized set).

**Batched intake.** N same-lane items arriving together = ONE proposal, one confirm. Mixed lanes →
`split_required`. Record the confirmed `rationale` in the artifact you create — never in a state file.
