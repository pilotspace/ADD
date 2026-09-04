---
type: Milestone
title: OKF for the living specs — addressable, dated, typed, searchable
status: direction
generated: { by: add/3.4.0, at: 2026-09-03 }
verified:
  - { by: "human:tindang", at: 2026-09-04, act: check, authority: process, via: process, boxes: "EXIT:1" }
  - { by: "human:tindang", at: 2026-09-04, act: check, authority: process, via: process, boxes: "EXIT:2" }
  - { by: "human:tindang", at: 2026-09-04, act: check, authority: process, via: process, boxes: "EXIT:4" }
  - { by: "human:tindang", at: 2026-09-04, act: check, authority: process, via: process, boxes: "EXIT:6" }
  - { by: "human:tindang", at: 2026-09-04, act: uncheck, authority: process, via: process, boxes: "EXIT:1" }
  - { by: "human:tindang", at: 2026-09-04, act: uncheck, authority: process, via: process, boxes: "EXIT:2" }
  - { by: "human:tindang", at: 2026-09-04, act: uncheck, authority: process, via: process, boxes: "EXIT:4" }
  - { by: "human:tindang", at: 2026-09-04, act: uncheck, authority: process, via: process, boxes: "EXIT:6" }
---
## CARD
goal: the five living specs conform to OKF v0.2 and go beyond it — every lesson is an addressable concept with a validity interval, edges between concepts are typed, and one verb finds any of it
why: ADD's specs already carry OKF's shape by accident (`type` · `title` · `generated: {by,at}`, reserved `index.md`/`log.md`) but not its contract, and OKF itself stops short of what a living spec needs: its links are explicitly untyped and its time keys are document-lifecycle only. The consequence is measurable today — 43 delta lines across five files (40 open · 3 folded), none dated, none addressable, none reachable except by opening the file and reading all thirty. A lookup that can only answer `specs/method.md` points at thirty unrelated lessons, which is why nobody looks anything up.
next: add new task <slug>

## SCOPE
In:  `.add/specs/*.md` frontmatter · the frozen delta grammar (id + validity interval) · a `relations:` edge family with a closed vocabulary · `add deltas` time filters · a new `add search` verb · the SKILL.md routing that makes the loop read the specs before it plans
Out: OKF `status:`/`stale_after` on Specs (decided: `status` collides with ADD's task lifecycle — the `okf-persona-template` precedent — and a spec with dated deltas has no file-level staleness left to declare) · exploding each lesson into its own file (OKF concept-per-file) · any change to Task/Milestone/Persona frontmatter · `graph.json` becoming readable by the engine (law 1 stands)

## GROUND
touches: add-method/tooling/add.py · add-method/tooling/cli.py · add-method/FORMAT.md · add-method/skill/add/SKILL.md · add-method/skill/add/references/deltas.md · add-method/tests/engine · add-method/tests/skill · .add/specs · .add/index.md
risks:
  - the delta grammar is frozen and 43 live lines use it — a parser change that mis-reads one line drops it from the inventory the loop reads to propose the next tasks, silently (the exact failure `deltas()` already carries a malformed-report for)
  - a new verb is never one edit: it ripples into the CLI WIRED set, the README verb count, the book command reference and the SKILL.md budget pins — five registries on the last count, findable only by running the full suite
  - the git-blame backfill dates a LINE, not a lesson: a reflow commit would re-date every delta in the file at once, so the migration must be read before it is trusted

## EXIT
- [ ] Spec nodes carry OKF's recommended frontmatter (`description` · `tags` · `sources`) — in the `init` scaffold and in all five live specs — and `description` has a live reader, not just a slot   (← okf-spec-frontmatter)
- [ ] every delta carries a stable id and a validity interval, `learn` writes them, `fold` closes the interval, and all 43 legacy lines are migrated with dates recovered from git   (← dated-addressable-deltas)
- [ ] `add deltas` filters by lens, by `--since`, and by `--as-of <date>` — reconstructing what a spec asserted on a past date   (← deltas-time-filters)
- [ ] a `relations:` family carries typed concept edges over a closed vocabulary, resolves through §3.2/§3.3, and records an unknown rel rather than rejecting it   (← typed-relations)
- [ ] `add search <query>` finds any concept in the bundle, returns spec hits at LESSON granularity not file granularity, and every verb registry knows the new verb   (← search-verb)
- [ ] the ADD skill routes the loop through `add deltas` to gather the carried specs before it plans a milestone or a task   (← skill-reads-deltas)

## CLOSE
evidence: <one row per task>
