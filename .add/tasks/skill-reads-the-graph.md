---
type: Task
title: SKILL.md teaches the graph — read a node whole, query by field, before the loop plans
status: direction
depth: quick
milestone: okf-graph-lookup
depends_on:
  - /tasks/show-verb.md
  - /tasks/search-structured-filters.md
scope:
  - add-method/skill/add
  - add-method/src/add_method/_bundled/skill/add
  - .claude/skills/add
  - add-method/tests/skill
gives:
  - S1 SKILL.md's cookbook and Intake routing — `add show` and `add search`'s field filters named as the read-before-you-plan step, byte-identical across all three shipped skill trees
  - S2 the funding — every added byte paid for by compression inside the existing 176-line and 13258-byte pins, and the prose sha256 pin re-aimed in the same change
  - S3 intake.md — the Task and Project/milestone routes name reading the node and its neighbourhood before drafting scope
generated: { by: add/3.4.0, at: 2026-09-04 }
verified:
  - { by: "plan:okf-graph-lookup", at: 2026-09-04, act: freeze, authority: plan, direction: "sha256:1ef4df90df7dc467", binding: "sha256:bd1235c2e1600e93" }
  - { by: "cli", at: 2026-09-04, act: brief, authority: process, brief: "sha256:154017d2bc3d4e0e" }
---
## CARD
goal: the always-loaded skill teaches reading a node whole and querying the bundle by field, before the loop plans anything.
why: three verbs shipped this milestone and the skill names none of them, so the loop still tells an agent to `open .add/tasks/<slug>.md` and read its CARD by hand — the exact `cat` that `add show` exists to replace. A capability the always-loaded surface does not name is a capability nobody uses.
beat: direction · next: add freeze skill-reads-the-graph

## RULES
<must>
- M1 SKILL.md's orient branch tells the agent to READ the active node through the engine rather than by opening its file
- M2 the Intake Task and Project/milestone routes each name a graph read before planning, beside the `add deltas` step already there
- M3 the cookbook's `search` line shows the field filters, not only the free-text form
- M4 every added byte is funded by compression INSIDE the existing pins — 176 lines and 13258 bytes — and the pins are not raised
- M5 all three shipped skill trees are byte-identical after the change
- M6 the prose sha256 pin is re-aimed in the same change, with its prior hash recorded
</must>
<reject>
- R:BUDGET_BUMP a pin must never be raised to fit an addition; the addition is funded or it is not made -> "BUDGET_BUMP"
- R:NEUTERED compression must not delete a CLAIM — a retired sentence's assertion has to survive somewhere, or the cheapest way to fit is to make the document shorter and worse -> "NEUTERED"
- R:PHANTOM the skill must not name a verb or flag the CLI does not wire -> "PHANTOM"
- R:DRIFT the three trees must not diverge by a single byte -> "DRIFT"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 S2 S3 · n/a · prose in an always-loaded skill file; it grants no capability, changes no floor, and records no stamp. The verbs it names were each gated separately
- A2 [which] covers: S1 · the request does not say which routing points should read the graph; taking the two the loop already stops at to gather context — the orient branch for an ACTIVE node, and Intake's two planning routes — rather than every mention of a node · probe: the orient branch's current instruction is literally to open the file and read its CARD, which `add show` supersedes -> if wrong, the skill grows a read instruction at every step and the budget pays for repetition
- A3 [which] covers: S2 · the request does not say which text may be compressed; taking DUPLICATES ONLY — a line whose claim is stated elsewhere in the same file · found: the `add done` row was retired the same way at show-verb, after asserting its claim survives in the VERIFY beat -> if wrong, compression removes the only statement of a rule and the file gets shorter and worse
- A4 [which] covers: S3 · the request does not say which intake.md sections change; taking the `### Task` and `### Project / milestone` sections, the two that already carry the `add deltas` step, so one convention covers both files -> if wrong, SKILL.md and intake.md disagree about when the loop reads
- A5 [when] covers: S1 S3 · the request does not say where in the beat the read falls; taking BEFORE drafting — the read exists to inform scope and the contract, and a read after the draft is a review, not an input -> if wrong, the agent drafts blind and the read becomes a rubber stamp
- A6 [when] covers: S2 · the request does not say when funding must be found; taking IN THE SAME EDIT — the byte count is asserted before the trees are written, so an over-budget change is never committed and then trimmed -> if wrong, a red pin is discovered after the fact and the cheapest repair is raising it
- A7 [absent] covers: S1 S3 · the request does not say what an absent graph read means; taking it as NOT AN ERROR — the engine gates on contracts and receipts, never on whether the agent read first, so this is routing prose and not a refusal -> if wrong, a missing read becomes a gate condition the engine cannot observe
- A8 [absent] covers: S2 · the request does not say what happens if no fundable duplicate exists; taking REFUSE TO ADD — the addition is dropped rather than the pin raised, and the gap is declared -> if wrong, R:BUDGET_BUMP is bent the first time compression is hard
- A9 [absent] covers: S5 · n/a · there is no fifth surface; the sweep covers S1 S2 S3
- A10 [order] covers: S1 S3 · the request does not say what orders the new instructions; taking the READING ORDER already there — orient before Intake, and within Intake the deltas step before the graph step, because a lesson shapes what you look for -> if wrong, the agent queries the graph before it knows what it is looking for
- A11 [order] covers: S2 · n/a · a byte count is a scalar and the compressions are independent of each other
- A12 [experience] covers: S1 S3 · the receiver is an agent with a fixed context budget; what would make this hard is a read step that costs more than the file it replaces, so the routing names `add show` with its DEFAULT depth and never suggests the cap -> if wrong, the loop spends more context orienting than building
- A13 [experience] covers: S2 · the receiver is the next author who needs budget; taking a compression that leaves the pins UNMOVED, so the next addition faces the same discipline rather than an eroded one -> if wrong, each task raises the pin a little and the always-loaded cost grows without anyone deciding to grow it

## PLAN
contract: SKILL.md's orient branch replaces "open `.add/tasks/<slug>.md`, read its `## CARD`" with `add show <slug>`; the wired-surface sentence names `show`; Intake's Task and Project/milestone routes each gain a graph read beside the existing `add deltas` step; the cookbook's `search` row shows the filters. intake.md's two sections take the matching instruction. Every byte funded by retiring duplicated text, asserted in the same edit. All three trees written from one string. The sha256 prose pin re-aimed with its prior hash recorded.
strategy: write the checks first — including the two pins as checks, so an over-budget draft is red before it is written to any tree — then compose ONE string and write it to all three trees.

## EDGES
- E1 the line budget is exactly at its ceiling before the change, so any net line addition reds
- E2 a claim retired by compression is still stated somewhere in the same file
- E3 every verb and flag the new prose names is wired in the CLI
- E4 the three trees are byte-identical, including the gitignored one if present
- E5 the prose pin reds if the trees change and it is not re-aimed

## CHECKS
- test_orient_reads_the_node_through_the_engine · covers: M1, A2 · the orient branch names `add show` and no longer instructs opening the task file by hand
- test_intake_routes_name_a_graph_read · covers: M2, A4, A5 · both SKILL.md Intake bullets and both intake.md sections name a graph read before drafting
- test_cookbook_shows_the_search_filters · covers: M3 · the `search` row names `--type`, `--status` and `--milestone`
- test_skill_stays_within_both_pins · covers: M4, R:BUDGET_BUMP, E1 · the line and byte counts are at or under the pins, and the pin literals are unchanged from the previous commit
- test_no_claim_was_deleted_by_compression · covers: R:NEUTERED, E2 · every sentence retired to fund the addition has its claim asserted elsewhere in the file
- test_new_prose_names_only_wired_verbs · covers: R:PHANTOM, E3 · every `add <verb>` the new lines name is a real CLI subcommand
- test_three_trees_are_byte_identical · covers: M5, R:DRIFT, E4 · SKILL.md and intake.md match across every tree that exists
- test_prose_pin_was_re_aimed · covers: M6, E5 · the pinned sha256 equals the shipped file and the annotation records a prior hash
red-first: every check MUST fail first.

## EVIDENCE
receipt: runs/n.md
gate: PASS | RISK-ACCEPTED | HARD-STOP

## LESSONS
- a lesson -> add learn lens
