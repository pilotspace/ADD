---
type: Milestone
title: a scaffold hands you a node the engine will accept
status: done
generated: { by: add/3.3.0, at: 2026-09-03 }
verified:
  - { by: "Tin Dang", at: 2026-09-03, act: freeze, authority: human, direction: "sha256:75a11da44c802486", binding: "sha256:e3b0c44298fc1c14" }
---
## CARD
goal: what `new` writes is what the engine reads, and what a lane promises it seeds.
why: measured — `--kind explore` scaffolds a body `freeze` then refuses; the template's only `scope:` slot sits where no reader looks; five task kinds route to no seeded persona, security among them.
next: add new task seed-the-missing-lenses

## SCOPE
In:  the scaffold `new` writes, the taxonomy it accepts, the personas `init` seeds, and the two readers (`doctor`, `join`) that report success over input they never read
Out: the gate's refusal tiers, the seal, and every verdict path — closed by verdict-truth and refusals-that-work

## GROUND
touches: add-method/tooling/add.py, add-method/tooling/cli.py, add-method/tooling/templates/personas/, add-method/tests/engine/
risks:
  - a template edit ripples into the twins, both MD5 pins and every fixture that builds a node by hand — the scaffold is a pinned interface
  - tightening the sweep can refuse nodes already written; this repo's own bundle is the first thing it must not break

## EXIT
- [x] every task kind in the taxonomy routes to a seeded persona, and a guard fails when the next one does not   (← seed-the-missing-lenses)
- [x] `new --kind explore` writes the body the explore lane reads, and `freeze` accepts it unedited   (← the-explore-scaffold-is-an-explore)
- [x] a waived sweep dimension states its reason, and the docstring's promise is the code's behaviour   (← a-silence-states-its-reason)
- [x] `new` refuses a kind outside the closed taxonomy and names it   (← a-kind-is-from-the-taxonomy)
- [x] `scope:` is written where its readers look, and `phantom_scope` can fire   (← scope-is-where-its-readers-look)
- [x] `doctor` reports an unauthored node instead of no findings   (← doctor-sees-an-unauthored-node)
- [x] `join` refuses a path that is not a bundle   (← join-refuses-what-it-cannot-read)

## CLOSE
| task | verdict | receipt |
|---|---|---|
| seed-the-missing-lenses | PASS | runs/1.md — 5 lenses seeded, 11/11 kinds claimed |
| the-explore-scaffold-is-an-explore | PASS | runs/1.md — a slot no longer satisfies its own guard |
| a-silence-states-its-reason | PASS | runs/1.md — 4 real waivers, 0 refused |
| a-kind-is-from-the-taxonomy | PASS | runs/1.md — the third instance of the sensitivity refusal |
| scope-is-where-its-readers-look | PASS | runs/1.md — empty, not a placeholder; 29 tests said so |
| doctor-sees-an-unauthored-node | PASS | runs/1.md — one oracle, two callers |
| join-refuses-what-it-cannot-read | PASS | runs/1.md — _is_bundle_index, not tasks/ |
