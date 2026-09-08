---
type: Milestone
title: the learning loop converges instead of accumulating
status: direction
generated: { by: add/3.5.0, at: 2026-09-08 }
verified:
  - { by: "Tin Dang", at: 2026-09-08, act: freeze, authority: plan, direction: "sha256:75a11da44c802486", binding: "sha256:e3b0c44298fc1c14" }
---
## CARD
goal: a lesson filed inside a milestone is drained at its close, a drained lesson can be promoted to a decision that binds every future brief, and no orientation surface reports zero carried work while lessons are open
why: the method's headline claim is that the five specs converge on reality, and nothing holds it. 75 lessons are open across 18 closed milestones, 2 were ever folded, `rejected` has no verb at all, and every `brief` in this bundle emits unauthored="true" for all five `## Decisions that bind` sections — so the loop tells each worker, correctly, that no decision binds. `learn` writes Deltas, `brief` reads Decisions, and no verb connects them.
next: add freeze loop-that-drains

## SCOPE
In:  the drain (milestone-done R:UNDRAINED, windowed to the milestone's own lessons) · the promotion path (fold --bind, fold --reject) · the orientation listings (status delta count + project goal, doctor unauthored_root + delta_count_drift) · the root's authoring gap (init writes invariants:, upgrade carries goal:) · two refusal rungs already paid for by repeat failures (freeze R:UNCOVERED from M31, milestone interview from M34) · resolving the 75-delta backlog
Out: any NEW verb — every change is a flag, a rung, or a listing on a verb that already exists · a second per-task human gate · a fourth delta status · a `retract` verb for a superseded stamp (append-only is the feature) · `via: tty` stamp provenance (an agent-typed stamp is never a tty) · extending R:UNCOVERED past filled E-numbered edges and probed A-numbered assumptions until the fixture breakage is measured, not estimated · enforcing the Quick lane's `add learn` line (no node exists to refuse)

## GROUND
touches: add-method/tooling/{add.py,cli.py} · add-method/tests/** · the three git-tracked skill twins ({loop,deltas,direction}.md) · .add/PROJECT.md · .add/specs/*.md · CLAUDE.md
risks:
  - R:UNCOVERED at freeze is the one rung whose blast radius is ESTIMATED, not run — the advisor scored its own practicality 0.88 for exactly this. It ships fourth, narrowed to filled E-numbered edges and probed A-numbered assumptions, and the full suite runs before its receipt (M32).
  - a windowed R:UNDRAINED is only as honest as its anchor; if the window resolves wrong, either the backlog blocks every close or the rung never fires at all. The anchor (generated.at, or the first verified stamp, whichever is earlier) is an assumption to discharge at Direction, not to carry into build.
  - a verb-level guard fires on the whole engine source, so a change in `fold` can red a guard belonging to `status` and never show in a targeted run (M32).
  - the skill is at 1487 of 1500 lines. Every prose line this milestone adds must be funded by a cut, or the surface guard reds.
  - `## Decisions that bind` has no FORMAT grammar and one reader (`brief`). Writing to it via --bind must mirror the existing `(evidence: ...)` tail convention rather than introduce a new format, or this milestone becomes a bundle-format change.

## EXIT
- [ ] `add status` names the open-delta count and the project `goal:` at T0, and an unknown count renders `? open deltas` rather than `0`   (← orientation-sees-carried-work)
- [ ] `add doctor` warns `unauthored_root` on a template Project or Spec, and reports `delta_count_drift` which `--sync` repairs   (← orientation-sees-carried-work)
- [ ] `add init` writes an `invariants:` key, `add upgrade` carries `goal:` forward, and `doctor` is the key's reader so no key exists that nothing reads   (← orientation-sees-carried-work)
- [ ] `add fold --reject` exists, giving the `rejected` status its first verb, and `add fold --bind` writes a decision into `## Decisions that bind` so `brief` stops emitting unauthored="true" for that spec   (← deltas-drain-at-close)
- [ ] `add milestone-done` refuses `R:UNDRAINED` for a delta filed inside that milestone's own window, and does not refuse for one filed before it   (← deltas-drain-at-close)
- [ ] every one of the 75 pre-existing deltas is resolved — folded, rejected or bound — and `add deltas` reads 0 open   (← backlog-drain)
- [ ] `add freeze` refuses `R:UNCOVERED` when CHECKS omit a FILLED E-numbered edge or a PROBED A-numbered assumption, and the enumeration shares one function with `gate` rather than a second copy   (← freeze-binds-what-you-authored)
- [ ] `add interview` accepts a Milestone, and `freeze --authority human` refuses R:UNINTERVIEWED while an EXIT criterion is unanswered   (← milestone-freeze-is-interviewed)
- [ ] no new verb is added: the verb set is unchanged from 3.5.0, and the change lands as flags, rungs and listings on existing verbs   (← all)
- [ ] the skill surface stays within its 1500-line ceiling, every added line funded by a cut   (← all)

## CLOSE
evidence: one row per task, recorded at close
