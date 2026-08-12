---
type: Milestone
title: Experience becomes a question the plan must answer
status: done
generated: { by: add/3.1.0, at: 2026-08-12 }
verified: []
---
## CARD
goal: a task cannot reach a frozen contract without naming who receives its output and what would make that output hard for them
why: ADD's instruments are all about correctness — RULES is what must be true, EDGES the boundaries, CHECKS the proof. The `experience` lens ships in BOTH profiles and maps to UDD in `LENS_COMP`, and every bundle gets an `experience.md` spec, but nothing in the loop ever writes it: UDD appears only as a retrospective tag on `add learn`, filed after something already misled someone. So a task can be provably correct and unusable, and the loop registers nothing. In this repo's own bundle, 1 of 25 tasks mentions experience at all. Meanwhile both READMEs still promise "a wireframe and a zero-dependency HTML mock, approved before any build" — a 1.7-era UI step that 3.0 removed and no guard noticed, because `front-door-truth` checks nouns the engine EXPOSES and never capabilities the prose PROMISES.
next: add new task experience-sweep

## SCOPE
In:  a sixth sweep dimension `[experience]` in the closed vocabulary, its scaffold line, and the living prose that enumerates the vocabulary; retirement of the wireframe/HTML-mock claim from both READMEs; a guard for promised-capability drift
Out: re-adding a design-preview beat (screen-shaped, and a reconciliation has no wireframe — the milestone that just shipped made this method domain-general and a UI step would undo it); rewriting dated announcement posts, which described 3.0 accurately when published; the `experience.md` spec's own content, which the new dimension will feed over time rather than being seeded here

## GROUND
touches: add-method/tooling/add.py, add-method/src/add_method/_bundled/tooling/add.py, add-method/skill/add/ (x3 trees), add-method/FORMAT.md, add-method/GETTING-STARTED.md, add-method/docs/, README.md, add-method/README.md, add-method/tests/
risks:
  - a sixth dimension is a stricter freeze for every unfrozen task in every installed project — one more (dimension, surface) pair per surface. Frozen tasks are untouched, and `depth: quick` is already exempt, but this is a behavior change that has to be declared in the CHANGELOG rather than shipped as a quiet minor.
  - the vocabulary is enumerated as a literal in eight living files and as "all five"/"five dimensions" in prose. A change that updates the engine and misses the prose reproduces exactly the drift this milestone exists to close.

## EXIT
- [x] `freeze` refuses a task whose surfaces are unswept on `[experience]`, and the scaffold frames both halves — who receives this, and what would make it hard   (← experience-sweep)
- [x] every LIVING surface that enumerates the dimension vocabulary agrees with the engine, derived rather than pinned   (← experience-sweep)
- [x] the wireframe/HTML-mock promise is gone from both READMEs, and a guard fails when the front door promises a capability the skill does not carry   (← promised-capability-guard)

## CLOSE
evidence:
- experience-sweep · gate PASS @ plan · receipt runs/4.md · freshness fresh · 6 checks bound. Reopened TWICE by its own author: once because `scope:` was written into `## PLAN` but never into frontmatter, where the engine reads it, so the first PASS attested nothing; once because the dated-record check pinned `CHANGELOG.md` byte-identical to HEAD and would have refused the release entry this milestone has to write.
- promised-capability-guard · gate PASS @ process · receipt runs/1.md · freshness fresh · 4 checks bound. Retired the wireframe-and-HTML-mock promise from both READMEs and narrowed the reasoning-floor bullet to the advisor pass that ships.
- CHANGELOG entry under `[Unreleased]` is milestone collateral, outside either task's scope, and is what proved the CHANGELOG fix.
- Suite 700 passed / 7 skipped, up from 690/7 (+10 checks).
- The lesson, in one line: the guards built in 3.1 all check nouns the engine EXPOSES, and a capability the prose PROMISES has no noun to look up — so it rotted for two minor versions with nothing able to see it. Both halves of this milestone are the same shape as `adoption-beyond-code`'s: when a rule quantifies over a set, its check must ENUMERATE that set and fail loudly on a member it was never taught about.
