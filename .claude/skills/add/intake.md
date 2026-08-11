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

### Quick — below the scope floor
Fits when **all** hold: one file or a few adjacent ones · behavior the specs already cover (typo,
wording, a config value, a mechanical rename) · no new contract surface anyone consumes · sensitivity
mechanical. Then **no node**: make the edit and leave the receipt —
1. the **git diff** is the change record (commit as usual);
2. `add learn <ddd|sdd|udd|tdd|add> "<lesson>" --evidence <ref>` files what was learned into the
   living 5-DD spec (**wired** — the real `add` CLI; evidence is required). A lane run that teaches nothing appends nothing.

### Task — one atomic node
Fits the active milestone's stated scope, or is a single behavior needing a frozen contract. Run the
3-beat loop: `add new Task <slug> --title "..." --depth quick|standard|deep`, then Direction.
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
A new product theme no active milestone covers, or a slice too big for one task. **Load the best-fit
persona whose `flow:` includes advisor before the drafting starts** (`personas.md` § planning;
if no personas are seeded, skip silently — the load is by fit). Draft the milestone first —
**goal · in/out scope · exit criteria · a breadth-first task list** (`slug · depends-on · one
line` each) — confirm it, then create it and list its tasks, recording the lens on the confirmed
milestone: `add advise <milestone> --persona <p>`. (`add milestone-done` is **wired** — it
refuses to close while a goal box is unchecked; `add milestone-archive` retires it once done.)

## The closed floor — what always sizes up

A change touching **security · data · architecture** ALWAYS becomes a real task — never Quick, no matter
how small. **Security is a HARD-STOP everywhere.** New behavior, a new/changed contract, or anything you
would want a frozen `gives:` for → a Task at least. The route is yours; the veto is not — the human
saying "make it a task" always wins. **When in doubt, size up.**

## Change-request — touching already-frozen scope

If the request modifies a **frozen** contract or a shipped promise, it is not new scope — it is a
change-request back to Direction of the affected node (§3.5: the old `gives:` stays, a `refreeze` stamp
lands, dependents that `need:` it are flagged stale). Never fork the truth into a parallel node.

## What you emit (the proposal)

Present it via `gate.md` — open with the ARC (goal · done · plan), render the chosen lane as a guided
choice with its described alternatives. Emit exactly one of:
- **a classification** — `{ lane, depth, rationale, command }` — `rationale` names WHY (the fit, the
  theme, the slice, the frozen scope touched — and the unknowns tally when it routed); `depth` makes
  ceremony a decision output the human vetoes, never a silent constant; `command` is the exact
  `add …` line. The human confirms first.
- **a rejection** — create nothing: `ask_human` (too ambiguous to size), `frozen_scope` (route as a
  change-request), or `split_required` (spans lanes — propose the smallest correctly-sized set).

**Batched intake.** N same-lane items arriving together = ONE proposal, one confirm. Mixed lanes →
`split_required`. Record the confirmed `rationale` in the artifact you create — never in a state file.
