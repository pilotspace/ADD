---
type: Spec
title: System
lens: system
project: AIDD-Book
generated: { by: add/3.0.0, at: 2026-08-08 }
delta_seq: 3
---
## Now
how it is built, and what that forecloses

## Decisions that bind
- <the first decision that constrains the rest>

## Deltas
- <what changed, and the evidence that changed it>
- [SDD · S3 · open · 2026-09-03] The vendored engine's bytecode cache is gitignored, so the FIRST run after a clone, after any add.py edit, and after every `doctor --sync` re-vendor pays ~31ms to recompile add.py — a third of a 61ms `status`. It amortises where the install dir is writable and never amortises where it is not. (evidence: python3 -X importtime: add self 32467us cold vs 1643us warm)
- [SDD · S2 · open · 2026-08-12] a denylist of RETIRED phrases must be paired with an assertion that each retired sentence's CLAIM survived — otherwise the cheapest way to pass is deleting the paragraph, which makes the doc shorter and worse. R:NEUTERED (evidence: add-method/tests/skill/test_front_door_copy.py)
- [SDD · S1 · open · 2026-08-12] a skill-surface addition has a three-tree blast radius; a scope narrower than that ships a red suite and the architecture residue lens is what catches it (evidence: /tasks/domain-evidence-recipe.d/runs/2.md)
