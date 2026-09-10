---
type: Task
title: brief names the roster personas that fit, and selects none
status: done
depth: standard
milestone: personas-load-by-fit
scope:
  - add-method/tooling/add.py
  - add-method/tooling/engine_pin.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - add-method/tests/engine/test_brief_names_the_candidate_lens.py
  - .add/tooling/add.py
  - .add/tooling/engine_pin.py
gives:
  - S1 `brief`'s no-lens branch — what a `<persona ref="none">` element carries when the bundle's roster holds an entry that fits this node's beat and kind
generated: { by: add/3.6.0, at: 2026-09-10 }
verified:
  - { by: "plan:personas-load-by-fit", at: 2026-09-10, act: freeze, authority: plan, direction: "sha256:1390c8792d87911e", binding: "sha256:f8a8085abd2c4018" }
  - { by: "plan:personas-load-by-fit", at: 2026-09-10, act: refreeze, authority: plan, direction: "sha256:1390c8792d87911e", binding: "sha256:f8a8085abd2c4018" }
  - { by: "cli", at: 2026-09-10, act: brief, authority: process, brief: "sha256:f1a69241cc114999" }
  - { by: "process:run", at: 2026-09-10, act: run, authority: process, outcome: PASS, receipt: /tasks/brief-names-the-candidate-lens.d/runs/1.md }
  - { by: "plan:personas-load-by-fit", at: 2026-09-10, act: gate, authority: process, outcome: PASS, receipt: /tasks/brief-names-the-candidate-lens.d/runs/1.md, brief: "sha256:c77a5e8fde33bd4b" }
advised_by: engine-notary
---
## CARD
goal: a brief for a node carrying no lens names the roster entries that FIT it, so the agent about to work the beat can pick one — and the engine picks none of them
why: <why this task exists — optional>
beat: done · next: add status

## RULES
<must>
- M1 when a node carries no lens, `brief` lists the bundle's Persona nodes whose `flow:` names this beat's surface AND whose `task-kinds:` covers the node's `kind:`, and names `add advise` as the verb that records a pick
- M2 the engine SELECTS none of them — it emits the fitting set and stops; ranking, choosing and loading stay the orchestrating agent's judgment (the NO-EXEC floor, `personas.md`)
- M3 the routing keys and the beat-to-surface mapping are the ones the roster already uses — `flow:` and `task-kinds:`, direction→design · build→build · verify→verify, verify falling back to `advisor`
- M4 a bundle whose roster has no fitting entry emits exactly what it emits today, byte for byte — the addition is visible only where it has something to say
- M5 the frontmatter is all that is read: a candidate's BODY is never opened, so the brief cannot grow by the size of a persona it did not pick
</must>
<reject>
- R:ENGINEPICKS the brief names one candidate as the choice, or orders them by a preference the engine invented -> "ENGINEPICKS"
- R:BODYLEAK a candidate's `## Critical Rules` or any other body section reaches the brief -> "BODYLEAK"
- R:SILENTGROWTH the candidate list pushes a brief past its depth budget with no degradation recorded -> "SILENTGROWTH"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the request does not say who reads the candidate list; taking "the agent about to work this beat — `brief` is already the composed prompt it reads, which is exactly why the candidate belongs here and not in a `todo` row (the row refuses a second verb, A12)" -> the list is written for a human skimming a terminal and the agent that needed it never sees it
- A2 [which] covers: S1 · the request does not say which nodes get candidates; taking "only a node carrying NO lens — a node with `persona:` or `advised_by:` already injects that lens's frontmatter and a candidate list beside it would be noise" · probe: a lensed node's brief is unchanged -> every brief carries a roster listing including the ones that already answered the question
- A3 [when] covers: S1 · the request does not say when the fit is computed; taking "at brief time from the live graph, like every other ref the brief resolves — nothing is stored on the node, so re-seeding the roster changes the next brief with no migration" -> a stored candidate list drifts from the roster it describes, which is the bug class this bundle keeps finding
- A4 [absent] covers: S1 · the request does not say what a node with no `kind:` matches; taking "the kind gate is skipped and `flow:` alone decides — `kind:` is optional on a Task, and a node that declared none has not declared it does not fit, so silently matching nothing would hide the whole roster from most of this bundle" · probe: a node with no `kind:` still gets candidates -> the feature is dark for every node that never set an optional field
- A5 [order] covers: S1 · the request does not say what orders the candidates; taking "slug, sorted — an alphabetical list is visibly NOT a ranking, and any other order is the engine expressing a preference it has no basis for (R:ENGINEPICKS)" -> the first row reads as the recommendation and the NO-EXEC floor is gone in everything but name
- A6 [experience] covers: S1 · the request does not say how many candidates or how much of each; taking "every fitting entry, each as slug plus its `task-kinds:` — the two facts a picker needs — and nothing else. This bundle's roster is three, and a roster large enough to flood a brief is a roster problem the brief should show, not hide" · probe: the emitted element carries no line from any persona BODY -> the brief grows by the size of the roster and the budget degrades something that mattered
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: `persona_candidates(graph, node, phase) -> list` returns sorted `(slug, task-kinds)` pairs; `brief`'s no-lens branch renders them inside the existing `<persona ref="none">` element, which stays self-closing when the list is empty.
strategy: write the checks red against the current engine first, then the helper, then the render; mirror all four engine twins and re-aim `ENGINE_MD5`/`ENGINE_PKG_MD5`.

## EDGES
- E1 <a boundary or failure case a check must cover — optional>

## CHECKS
- test_an_unlensed_node_is_offered_the_fitting_roster · covers: M1, A1, A4 · a node with no lens gets the entries whose flow and task-kinds fit, and the verb that records a pick
- test_the_engine_names_no_choice · covers: M2, R:ENGINEPICKS, A5 · the candidates are sorted by slug and no element marks one as preferred
- test_the_keys_are_the_rosters_own · covers: M3 · direction takes a design lens, build a build lens, verify a verify lens and falls back to advisor
- test_a_lensed_or_roster_less_node_is_unchanged · covers: M4, A2 · both a node that already names a lens and a bundle with no fitting persona brief exactly as before
- test_no_persona_body_reaches_the_brief · covers: M5, R:BODYLEAK, A6, R:SILENTGROWTH · only frontmatter is read, and the brief stays inside its depth budget
red-first: every check MUST fail first.

## EVIDENCE
receipt: /tasks/brief-names-the-candidate-lens.d/runs/1.md · kind: test-ids · 11/11 reported · exit 0 · 2026-09-10
gate: PASS · authority process · by plan:personas-load-by-fit · receipt /tasks/brief-names-the-candidate-lens.d/runs/1.md · 2026-09-10

## LESSONS
- none filed — no lesson cites /tasks/brief-names-the-candidate-lens.md (add learn <lens> "<lesson>" --evidence /tasks/brief-names-the-candidate-lens.md)
