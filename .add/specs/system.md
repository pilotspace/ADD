---
type: Spec
title: System
lens: system
project: AIDD-Book
description: how the engine is built and what that forecloses — notary discipline, the twins, the pins, and the cost of a verb
tags: [engine, pins, twins, vendored]
sources: []
generated: { by: add/3.0.0, at: 2026-08-08 }
delta_seq: 6
---
## Now
how it is built, and what that forecloses

## Decisions that bind
- <the first decision that constrains the rest>

## Deltas
- <what changed, and the evidence that changed it>
- [SDD · S6 · open · 2026-09-04] The `covers:` key has TWO grammars in one node: the ASSUMPTIONS sweep splits on WHITESPACE (covers: S1 S2 S3) and the CHECKS binding splits on COMMAS (covers: M2, E2). A space-separated CHECKS line parses as the single rule id 'M2 E2', which matches no referent, so every id on that line silently goes unbound — and the gate reports 'no reported passing check', which reads like a missing test rather than a punctuation error. Two separators for one key name is a trap the refusal message cannot name. (evidence: /tasks/milestone-membership-is-an-edge.md)
- [SDD · S5 · open · 2026-09-04] A verb-count pin names no verb, so it is invisible to every grep for the verb you are adding: test_no_new_verb_in_the_cli_surface hard-codes the COUNT and went red on a change no textual search for 'search' could have predicted. Find a new verb's registries by running the suite; a census by grep is a census of the sites that happen to spell the name. (evidence: add-method/tests/skill/test_authoring_beat.py · /tasks/search-verb.md)
- [SDD · S4 · open · 2026-09-04] An engine change has TWO pins, not one: ENGINE_MD5 pins add.py and ENGINE_PKG_MD5 pins cli.py (repurposed, and its name does not say so). Four tasks in this milestone touched only add.py and passed on one re-aim; the first task to touch cli.py failed test_cli_py_matches_ENGINE_PKG_MD5 after a green add.py re-aim. Re-aim both, or find them by running tooling/test_tree_parity.py. (evidence: add-method/tooling/engine_pin.py:20,23 · /tasks/deltas-time-filters.md)
- [SDD · S3 · open · 2026-09-03] The vendored engine's bytecode cache is gitignored, so the FIRST run after a clone, after any add.py edit, and after every `doctor --sync` re-vendor pays ~31ms to recompile add.py — a third of a 61ms `status`. It amortises where the install dir is writable and never amortises where it is not. (evidence: python3 -X importtime: add self 32467us cold vs 1643us warm)
- [SDD · S2 · open · 2026-08-12] a denylist of RETIRED phrases must be paired with an assertion that each retired sentence's CLAIM survived — otherwise the cheapest way to pass is deleting the paragraph, which makes the doc shorter and worse. R:NEUTERED (evidence: add-method/tests/skill/test_front_door_copy.py)
- [SDD · S1 · open · 2026-08-12] a skill-surface addition has a three-tree blast radius; a scope narrower than that ships a red suite and the architecture residue lens is what catches it (evidence: /tasks/domain-evidence-recipe.d/runs/2.md)
