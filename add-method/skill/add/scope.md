# Scope drafting — turn a classified request into a versioned MILESTONE.md

`intake.md` CLASSIFIES a request into a bucket; scope drafting turns that into a confirmed, well-formed, versioned `MILESTONE.md` through discussion. The MILESTONE.md template is the SHAPE; this rubric is HOW to fill it well.

## What to do per intake outcome

| intake outcome | scope-loop action | creates (after confirm) |
|----------------|-------------------|-------------------------|
| `new-major` / `sub-milestone` | draft ONE MILESTONE.md (fill the template via discussion) | 1 milestone |
| `task` | route to `add.py new-task <slug>` (fits the active milestone) | 0 milestones |
| `change-request` | route to SPECIFY/CONTRACT of the affected task | 0 milestones |
| `split_required` | draft ALL N items as a batch in ONE pass | N milestones/tasks |

**Confirm before create is the convention.** "One pass" means one drafting pass, NOT auto-creation — nothing is written until the human confirms; enforced only by the opt-in `--await-confirm` (below).

**Confirm the milestone before detailing tasks.** `new-milestone <slug> --await-confirm` seeds it *unconfirmed* — `new-task` is HELD (`milestone_unconfirmed`) until you show the filled `MILESTONE.md`, get the human's go, and run `milestone-confirm <slug>`. Keeps you from digging into task §0–§5 before the parent is agreed. (Omit the flag: no gate.)

## Position the goal — ground in assets, relate to the milestone map   (do this FIRST)

Before drafting the goal sentence, position the request in what already exists — distinct from intake's classification, not redundant with it.

1. **Ground in current assets.** Read the goal against what exists — the goal must reflect what the project already is. Ground as rigorously as a task's §0 (`phases/0-ground.md`), using the **same four fields** at milestone scope: **Touches** (the subsystems/files the milestone spans) · **Context** (the docs · todos · config · data it works against) · **Honors** (the `PROJECT.md` / `CONVENTIONS.md` invariants it must respect) · **Anchors** (the existing contracts/symbols its tasks will cite). Grounding is complete when each is named from real assets, not assumed.
2. **Relate to the milestone map.** Run `add.py search <keyword> [<keyword> ...]` first — then read every existing goal — `.add/milestones/*/MILESTONE.md` and `.add/archive/*` — and name THIS request's relationship: *extends* X · *depends-on* Y · *overlaps* Z. Record in the `rationale` line.
3. **If the goal is already delivered** by an existing milestone, reject `duplicate_goal` and route as `task` or `change-request`.

## Brainstorm before you draft — co-specify at milestone level

Don't draft from thin input. Run the three-move co-specify (`phases/1-specify.md`) — Diverge → Converge → Validate — raised to milestone scope. Ask only what moves the goal, the In/Out line, or the task list.

Diverge seeds (pick the live ones):
- **Outcome** — done means a user can do *what* they can't today?
- **Edge of scope** — nearest thing assumed IN that you want OUT?
- **Riskiest decision point** — which contract, if wrong, costs the most rework?
- **Done-looks-like** — how do we SEE each outcome without reading code?
- **First slice** — which task unblocks the rest?

Rank assumptions lowest-confidence first; top 1–2 get the flag: `⚠ <assumption> — lowest confidence because <why>; if wrong: <cost>`. Present via `report-template.md` — open with the ARC (goal · done · plan), render as a guided choice.

## Drafting a good MILESTONE.md (section by section)

- **goal** — ONE outcome sentence (no "and" — that is two milestones).
- **rationale** — intake bucket + WHY, AND the milestone relationship from "Position the goal". Never in state.json.
- **Scope In/Out** — explicit anti-creep deferral list. An empty Out list means scope is not yet thought through. UI/UX scope? use the template's Scope hint vocabulary, not generic prose.
- **Shared decisions & glossary deltas** — cross-cutting rules every task must honor. New terms get a glossary entry.
- **Shared / risky contracts to freeze first** — decision points between tasks; name the owning task.
- **Tasks (breadth-first)** — `slug · depends-on · one line` each. Decompose by deliverable; keep each task one-file-sized.
- **Exit criteria** — observable; **every exit criterion maps to a declared task slug** (no dangling criterion).
- **Close — ship review** + **Release steps** — **drafted-blank** here; filled LATER (`milestone-done` and `release.md`). Named so you know the full 9-section shape.

## Draft well-formedness gate

A scope draft is well-formed only when:
- [ ] goal is ONE outcome sentence (no "and")
- [ ] every exit criterion maps to a declared task slug (no dangling criterion)
- [ ] `rationale` records the bucket + milestone relationship from "Position the goal"
- [ ] `Close — ship review` and `Release steps` are left as the template (drafted-blank)
- [ ] the In/Out list names what is deferred

Propose only a well-formed draft — an incomplete one lets a milestone reach task breakdown half-formed.

## Reject codes

<reject_codes>
- `not_classified` — the request has not been through intake. Classify it first.
- `dangling_criterion` — a drafted MILESTONE.md has an exit criterion that maps to no declared task slug. FIX the draft before proposing.
- `no_milestone` — intake routed to `task` or `change-request`; create NO milestone.
- `duplicate_goal` — the goal is already delivered by an existing milestone (live or in `.add/archive/`). Route as `task` or `change-request`, create nothing.
</reject_codes>

## Worked example

Request: *"open the Interface & Intake milestone"* → intake classified it `sub-milestone` of v4 → scope drafting produced **`.add/milestones/v4-1/MILESTONE.md`**: goal *make ADD harness-drivable and self-scoping*; tasks (breadth-first) `machine-state-json` · `versioning-policy` · `scope-loop`; each exit criterion maps to its slug.
