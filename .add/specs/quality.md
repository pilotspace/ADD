---
type: Spec
title: Quality
lens: quality
project: AIDD-Book
generated: { by: add/3.0.0, at: 2026-08-08 }
---
## Now
what counts as proof

## Decisions that bind
- <the first decision that constrains the rest>

## Deltas
- <what changed, and the evidence that changed it>
- [TDD · open] A green suite is only evidence about the tests that RAN. The command that runs a subset must not produce output shaped like the command that runs everything — an uncollected suite reports as a smaller number, and a smaller number reads as success. (evidence: /tasks/partial-run-visible.md)
- [TDD · open] an assumption is worth writing only if you will go DISPROVE it: A1 assumed the installers pass --profile through. Ten minutes of reading bin/cli.js showed its 'profile' is agent detection and the flag is ignored — with its value silently becoming the target directory. The assumption cost a shipped falsehood because it was recorded and then trusted rather than tested (evidence: .add/tasks/profile-refusal.md)
- [TDD · open] a derived guard must distinguish a DEAD name from a LAZILY-CREATED one: probing with `init` alone made the corrected prose .add/tasks/<slug>.md fail beside the state.json it replaced. Drive the probe through a bundle that has been USED (init + first task), which still refuses names no sequence of verbs produces (evidence: add-method/tests/skill/test_front_door_truth.py)
- [TDD · open] a 'must never contain X' check passes vacuously when the file is missing — assert existence FIRST or it rides into the freeze proving nothing (evidence: add-method/tests/skill/test_domains_recipe.py:32)
- [TDD · folded] the gate coverage map binds EVERY referent — probed A-lines and E-lines included; write covers: complete at Direction or the first gate refuses on rules your suite already proves (evidence: /tasks/explore-lane.d/runs/2.md)
