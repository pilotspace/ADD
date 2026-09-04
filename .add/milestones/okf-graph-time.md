---
type: Milestone
title: OKF for the living specs — addressable, dated, typed, searchable
status: done
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
  - { by: "human:tindang", at: 2026-09-04, act: check, authority: process, via: process, boxes: "EXIT:1" }
  - { by: "human:tindang", at: 2026-09-04, act: check, authority: process, via: process, boxes: "EXIT:2" }
  - { by: "human:tindang", at: 2026-09-04, act: check, authority: process, via: process, boxes: "EXIT:3" }
  - { by: "human:tindang", at: 2026-09-04, act: check, authority: process, via: process, boxes: "EXIT:4" }
  - { by: "human:tindang", at: 2026-09-04, act: check, authority: process, via: process, boxes: "EXIT:5" }
  - { by: "human:tindang", at: 2026-09-04, act: check, authority: process, via: process, boxes: "EXIT:6" }
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
- [x] Spec nodes carry OKF's recommended frontmatter (`description` · `tags` · `sources`) — in the `init` scaffold and in all five live specs — and `description` has a live reader, not just a slot   (← okf-spec-frontmatter)
- [x] every delta carries a stable id and a validity interval, `learn` writes them, `fold` closes the interval, and all 43 legacy lines are migrated with dates recovered from git   (← dated-addressable-deltas)
- [x] `add deltas` filters by lens, by `--since`, and by `--as-of` an ISO date — reconstructing what a spec asserted on a past date   (← deltas-time-filters)
- [x] a `relations:` family carries typed concept edges over a closed vocabulary, resolves through §3.2/§3.3, and records an unknown rel rather than rejecting it   (← typed-relations)
- [x] `add search` finds any concept in the bundle from a query string, returns spec hits at LESSON granularity not file granularity, and every verb registry knows the new verb   (← search-verb)
- [x] the ADD skill routes the loop through `add deltas` to gather the carried specs before it plans a milestone or a task   (← skill-reads-deltas)

## CLOSE
evidence: eight tasks, each gated PASS on a receipt whose checks were proven red first
- okf-spec-frontmatter — Spec nodes carry OKF `description`/`tags`/`sources`; root declares `okf_version: "0.2"`; `doctor` reads it into an `okf_conformance` finding · /tasks/okf-spec-frontmatter.d/runs/2.md
- dated-addressable-deltas — the grammar carries a stable id and a validity interval; 43 legacy lines migrated, dates recovered from git blame and corroborated · /tasks/dated-addressable-deltas.d/runs/2.md
- deltas-time-filters — `add deltas --lens --since --as-of`, reporting the status a delta HELD THEN over a half-open interval · /tasks/deltas-time-filters.d/runs/2.md
- typed-relations — a `relations:` family, `refines` with four live instances, §3.3 gains a delta-id form in both oracles; found and fixed a pre-existing containment hole where `edge_out_of_bundle` silently downgraded to info · /tasks/typed-relations.d/runs/3.md
- search-verb — `add search` as the 25th verb, lesson granularity with a citable address; tags populated from each spec's own words; FORMAT §4 repaired · /tasks/search-verb.d/runs/2.md
- skill-reads-deltas — the loop gathers the carried lessons before it plans a Task or Milestone, in all three skill trees · /tasks/skill-reads-deltas.d/runs/1.md
- scan-skips-receipt-evidence — the graph scan defers a receipt's evidence payload; 97 receipts were 68% of all T0 parse time · /tasks/scan-skips-receipt-evidence.d/runs/3.md
- doctor-reads-each-body-once — four loops re-read the same bodies; reads 386 to 207 · /tasks/doctor-reads-each-body-once.d/runs/2.md

measured: `add status` 81.2ms -> 61.3ms (-24.6%), interleaved subprocess A/B, warm bytecode both arms, min of 15, instrument control 0.1ms
suite: 1234 passed, 7 skipped, 0 failed
carried: 13 lessons filed by `add learn` (D1 · Q10-Q13 · S3-S5 · M30-M31 · X4 and two earlier), each addressable and dated under the grammar this milestone landed

not done, declared:
- `## Decisions that bind` holds only the scaffold placeholder in all five specs, and `bind_sections()` feeds that placeholder into every brief (D1)
- `test_no_engine_output_was_added` asserts a working-tree diff is empty, so it reds for any uncommitted engine change by any future task
- `supersedes` ships as a §3.2 edge key with zero live uses, as it did before this milestone
