---
type: Task
title: a scaffold says whether a plan still wants it
status: done
depth: standard
scope:
  - add-method/tooling/add.py
  - add-method/tooling/cli.py
  - add-method/tests/engine/test_a_plan_says_what_it_wants.py
  - add-method/skill/add/SKILL.md
  - add-method/src/add_method/_bundled/skill/add/SKILL.md
  - add-method/README.md
  - add-method/tests/engine/test_beat_read_truth.py
  - add-method/tests/engine/test_todo.py
  - add-method/tests/engine/test_roadmap_reads_as_a_roadmap.py
  - add-method/tests/engine/test_check_verb.py
  - add-method/tests/engine/test_cli.py
  - add-method/tests/engine/test_show_verb.py
  - add-method/tests/engine/test_authoring_beat.py
  - add-method/tests/skill/test_claimed_output_guard.py
  - add-method/tests/skill/test_search_registry.py
  - add-method/tests/skill/test_surface.py
  - add-method/tests/skill/test_front_door_truth.py
  - add-method/tests/test_front_door_claim_truth.py
  - add-method/tests/book/test_beta2_coverage.py
  - add-method/tooling/engine_pin.py
  - add-method/skill/add/loop.md
  - add-method/src/add_method/_bundled/skill/add/loop.md
  - .claude/skills/add/loop.md
  - add-method/docs/13-command-reference.md
  - README.md
  - .claude/skills/add/SKILL.md
gives:
  - S1 the scaffold beat's PROVENANCE answer: what `status`, `todo` and `show` say about an unauthored task
  - S2 `add drop <slug> --reason` — the verb that writes the `dropped` status the engine already reads
generated: { by: add/3.6.0, at: 2026-09-10 }
verified:
  - { by: "process:auto", at: 2026-09-10, act: freeze, authority: process, direction: "sha256:cb9615b6ee053570", binding: "sha256:dfaaafef4ca33182" }
  - { by: "builder", at: 2026-09-10, act: replan, authority: process, note: "The 27th verb ripples wider than S2 implied: every registry that ENUMERATES the verb set has to learn it (CLI WIRED lists, three skill trees, two READMEs, the book command reference, four count pins), and four checks pinned the literal word 'scaffold' whose rule still holds but whose premise expired. Scope widened to the ripple; E6 records it." }
  - { by: "process:auto", at: 2026-09-10, act: refreeze, authority: process, direction: "sha256:70749f812df21795", binding: "sha256:311ab01c5825b9cf" }
  - { by: "process:auto", at: 2026-09-10, act: refreeze, authority: process, direction: "sha256:70749f812df21795", binding: "sha256:311ab01c5825b9cf" }
  - { by: "cli", at: 2026-09-10, act: brief, authority: process, brief: "sha256:1b49b3b89d05361f" }
  - { by: "process:run", at: 2026-09-10, act: run, authority: process, outcome: PASS, receipt: /tasks/a-plan-says-what-it-wants.d/runs/1.md }
  - { by: "process:auto", at: 2026-09-10, act: gate, authority: process, outcome: PASS, receipt: /tasks/a-plan-says-what-it-wants.d/runs/1.md, brief: "sha256:6373612d64cf848f" }
---
## CARD
goal: an unauthored task reports queued, abandoned or adrift, and a milestone cannot close leaving unauthored tasks behind in silence
why: a 40-task roadmap shipped for review with 38 nodes unauthored. 3.6.0 made them legible — every row now carries its title and the headline counts them — but a reader still cannot tell a task the plan is WORKING TOWARD from one the plan walked away from. Both read `[scaffold]`. And `milestone-done` never looks at its member tasks, so a milestone closing on its exit criteria abandons whatever it queued, silently
beat: done · next: add status

## RULES
<must>
- M1 an unauthored task reports whether a plan still wants it: `queued` (a milestone claims it and that milestone is open), `abandoned` (its milestone closed without it), or `adrift` (no milestone claims it, or the one named does not exist)
- M2 the answer is DERIVED from state that already exists — no new frontmatter field, no author burden, nothing to keep in sync
- M3 `milestone-done` refuses to close a milestone still holding unauthored tasks, naming each one, so abandonment is a decision somebody made rather than a side effect of closing
- M4 `add drop <slug> --reason "<why>"` writes the `dropped` status the engine already reads in three places and no verb could ever write
- M5 the `status` headline and `todo` split their counts by the same three words the rows use — a reader never has to map one vocabulary onto another
- M6 a `dropped` task is counted as neither scaffold nor queued anywhere, and its reason survives on the node
</must>
<reject>
- R:SILENTABANDON a milestone closes leaving unauthored tasks behind and nothing in the transcript says so -> "SILENTABANDON"
- R:DEADWORD a status the engine READS that no verb can WRITE — vocabulary that exists only in the reader -> "DEADWORD"
- R:NEWFIELD the provenance answer is stored rather than derived, so it can disagree with the milestone it describes -> "NEWFIELD"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the request does not say who reads the provenance word; taking "a reviewer reading a roadmap cold, who has no other way to tell a queue from a graveyard — so the word appears in the ROW, not only in a verb they would have to know to run" -> the distinction ships in `doctor` alone and the reviewer who was burned never sees it
- A2 [which] covers: S1 · the request does not say which milestone states count as closed; taking "`done` AND `archived` both close a plan — archiving is what happens after done, and a task the plan left behind is abandoned under either" · probe: an archived milestone's scaffold reports `abandoned`, not `queued` -> a whole archived milestone's leftovers read as an active queue
- A3 [when] covers: S1, S2 · the request does not say when `dropped` may be set; taking "any time before `done` — dropping is a planning act, not a lifecycle stage, and a task that was never authored is exactly the one most likely to be dropped" -> `drop` refuses the case it exists for
- A4 [absent] covers: S1 · the request does not say what a MISSING milestone means — `milestone: m-typo` naming nothing; taking "`adrift`, identical to no milestone at all: in both cases no plan that exists claims it, and a dangling reference must not crash a read verb" · probe: a task naming a non-existent milestone reports adrift and `status` still renders -> orientation dies on a typo
- A5 [order] covers: S1 · the request does not say what wins when a task is both `dropped` and unauthored; taking "`dropped` wins and the task leaves the scaffold vocabulary entirely — a dropped task is answered, not pending" -> a dropped task keeps appearing in the queue it was dropped from
- A6 [experience] covers: S1, S2 · the request does not say what M3's refusal must say; taking "it names every unauthored task and offers all three real fixes — author it, drop it, or move it to another milestone — because a refusal with one fix pushes the author toward whichever fix was named" -> the author drops work they meant to keep, because dropping was the only exit the message offered
- A7 [who] covers: S2 · the request does not say who may drop a task; taking "anyone who can create one — `drop` is a planning act at the `process` floor, not an approval; it records WHO and WHY, and the record is what makes it reviewable rather than a permission gate that would just get worked around" -> dropping needs an approval nobody is present to give, and the work rots as a scaffold instead
- A8 [which] covers: S2 · the request does not say which node types `drop` accepts; taking "lifecycle nodes only (Task and Milestone) — a Persona or Spec has no lifecycle to drop out of, and `advise` already refuses non-lifecycle nodes with R:NOTATASK, so this follows a shape the engine has" -> `drop` writes a meaningless status onto a Spec and every reader must learn to ignore it
- A9 [absent] covers: S2 · the request does not say what an ABSENT reason means; taking "`--reason` is required, exactly as `reopen` requires it — a dropped task with no reason is the silent abandonment this task exists to stop, merely relocated into a status field" -> R:SILENTABANDON returns through the verb built to prevent it
- A10 [order] covers: S2 · the request does not say what dropping an already-`done` task means; taking "refuse it — `done` is an outcome the gate recorded, and overwriting it with `dropped` would erase a receipt-backed verdict; the verb for revisiting a done task is `reopen`" -> a signed PASS is silently replaced by a planning note

## PLAN
contract: `_scaffold_kind(graph, cid) -> "queued" | "abandoned" | "adrift"` reads the task's `milestone:` against that milestone's status in the SAME graph — derived, never stored (R:NEWFIELD). `_beat_of` returns it in place of the bare `"scaffold"`, so every surface that already renders a beat inherits the word with no per-surface edit. `milestone_done` gains a rung after the goal-gate, listing unauthored members. `drop` is a new verb: `_transition` to `status: dropped` with the reason recorded, mirroring `reopen`'s shape.
strategy: the derivation first (it is what every other piece reads), then the milestone rung, then the verb.

## EDGES
- E1 a scaffold in an ARCHIVED milestone — archived and done are both closed, and only one of them is the obvious case
- E2 a `dropped` task appears in no scaffold count, no queued count, and no `todo` worklist
- E3 a milestone holding zero tasks closes exactly as it does today — the new rung must not invent a refusal
- E4 a milestone whose members are ALL authored closes as today; only unauthored members trip M3
- E5 a task naming a milestone that does not exist reports `adrift` and never raises
- E6 a 27th verb ripples into every registry that enumerates the verb set — CLI WIRED lists, three SKILL.md trees, two READMEs, the book command reference and four count pins; the ripple is the cost of the verb, and a check that enumerates the set is what makes it finite

## CHECKS
- test_a_scaffold_says_which_plan_wants_it · covers: M1, M2, R:NEWFIELD, A2, A4, E1, E5 · the three words, driven for real against open, done, archived, missing and absent milestones, with no new frontmatter key written
- test_a_milestone_cannot_close_on_unauthored_tasks · covers: M3, R:SILENTABANDON, A6, E3, E4 · the rung names every unauthored member and offers all three fixes; an empty or fully-authored milestone closes untouched
- test_drop_writes_the_status_the_engine_reads · covers: M4, R:DEADWORD, A3, A5, E2 · `add drop` at the front door writes `dropped`, records the reason, and the task leaves the scaffold vocabulary
- test_the_counts_and_the_rows_use_one_vocabulary · covers: M5, M6, A1 · the `status` headline and `todo` split by the same words the rows show, and neither counts a dropped task
- test_every_registry_enumerating_verbs_learned_drop · covers: E6 · every file that lists the verb set names `drop`, so the ripple a new verb causes is finite and checkable rather than discovered one CI failure at a time
red-first: every check MUST fail first.

## EVIDENCE
receipt: /tasks/a-plan-says-what-it-wants.d/runs/1.md · kind: test-ids · 296/296 reported · exit 0 · 2026-09-10
gate: PASS · authority process · by process:auto · receipt /tasks/a-plan-says-what-it-wants.d/runs/1.md · 2026-09-10

## LESSONS
- none filed — no lesson cites /tasks/a-plan-says-what-it-wants.md (add learn <lens> "<lesson>" --evidence /tasks/a-plan-says-what-it-wants.md)
