---
type: Spec
title: System
lens: system
project: AIDD-Book
description: how the engine is built and what that forecloses — notary discipline, the twins, the pins, and the cost of a verb
tags: [engine, pins, twins, vendored]
sources: []
generated: { by: add/3.0.0, at: 2026-08-08 }
delta_seq: 11
---
## Now
how it is built, and what that forecloses

## Decisions that bind
- <the first decision that constrains the rest>

## Deltas
- <what changed, and the evidence that changed it>
- [SDD · S11 · open · 2026-09-04] A dedup key must carry every field that distinguishes two things. neighborhood() dedups relations on (family, label, src, ref, target) and drops relations()'s src_id, so two lessons refining the same target collapse into one row — 4 relations in the live bundle, 3 emitted. Worse, the edges[] schema pinned in FORMAT §11 has no field that could carry src_id, so a consumer cannot recover the loss even in principle. Before writing a dedup key, ask what the producer returns that the key does not. (evidence: /specs/method.md:13-14 M8 and M31 both refine #M4 · neighborhood() emits one row)
- [SDD · S10 · open · 2026-09-04] One word for two vocabularies is a collision a scraper cannot see through. The new JSON payload named a result field 'kind' while the engine already spends 'kind' on the receipt-evidence ladder; test_stampable_rungs_are_documented read the payload literal as a receipt kind no doc named and failed correctly. The fix is to remove the collision, never to narrow the guard — a deliberately broad extractor is broad so a kind stamped in an unseen branch cannot shrink its set. Before naming a payload field, grep the engine for that key. (evidence: /tasks/json-emission.md · kind -> match, guard unchanged)
- [SDD · S9 · open · 2026-09-04] A twin set is an explicit LIST, never a glob. Mirroring an engine edit with rglob('tooling/add.py') matched 120 paths — benchmark run workspaces, two sibling git worktrees, and the archived 2.x bundle — all gitignored, so 'git status' showed 2 modified files and the damage was invisible to the usual check. Recovery worked only because each vendored bundle carries its own engine_pin.py: the pin is a self-verifying restore key, so 86 copies were restored by md5 lookup against historical blobs and 23 more by matching their untouched sibling cli.py to its commit. (evidence: /tasks/one-address-per-concept.md · rglob clobbered 120 copies, restored 109, 2 disposable tmp/smoke left)
- [SDD · S8 · open · 2026-09-04] A twin set is per-FILE, not per-engine: add.py has three mirrors and so does cli.py, but a scope: assembled by hand listed only two of cli.py's. The bundled twin was mirrored during build and never declared, which the gate would have caught as scope_violation. Derive the twin list from the tree, never from memory — and note that two of the six twins are gitignored, so git status cannot show you the omission. (evidence: /tasks/search-structured-filters.md)
- [SDD · S7 · open · 2026-09-04] The engine's declared floor is Python 3.10 (requires-python >=3.10) and NOTHING in the suite compiles it there, so a py3.12-only f-string shipped green locally: a backslash inside an f-string EXPRESSION part is a SyntaxError before PEP 701. The 1263-test suite runs on one interpreter and says nothing about the other two the package claims. A version floor with no compile guard is a claim, not a constraint. (evidence: /tasks/show-verb.md)
- [SDD · S6 · open · 2026-09-04] The `covers:` key has TWO grammars in one node: the ASSUMPTIONS sweep splits on WHITESPACE (covers: S1 S2 S3) and the CHECKS binding splits on COMMAS (covers: M2, E2). A space-separated CHECKS line parses as the single rule id 'M2 E2', which matches no referent, so every id on that line silently goes unbound — and the gate reports 'no reported passing check', which reads like a missing test rather than a punctuation error. Two separators for one key name is a trap the refusal message cannot name. (evidence: /tasks/milestone-membership-is-an-edge.md)
- [SDD · S5 · open · 2026-09-04] A verb-count pin names no verb, so it is invisible to every grep for the verb you are adding: test_no_new_verb_in_the_cli_surface hard-codes the COUNT and went red on a change no textual search for 'search' could have predicted. Find a new verb's registries by running the suite; a census by grep is a census of the sites that happen to spell the name. (evidence: add-method/tests/skill/test_authoring_beat.py · /tasks/search-verb.md)
- [SDD · S4 · open · 2026-09-04] An engine change has TWO pins, not one: ENGINE_MD5 pins add.py and ENGINE_PKG_MD5 pins cli.py (repurposed, and its name does not say so). Four tasks in this milestone touched only add.py and passed on one re-aim; the first task to touch cli.py failed test_cli_py_matches_ENGINE_PKG_MD5 after a green add.py re-aim. Re-aim both, or find them by running tooling/test_tree_parity.py. (evidence: add-method/tooling/engine_pin.py:20,23 · /tasks/deltas-time-filters.md)
- [SDD · S3 · open · 2026-09-03] The vendored engine's bytecode cache is gitignored, so the FIRST run after a clone, after any add.py edit, and after every `doctor --sync` re-vendor pays ~31ms to recompile add.py — a third of a 61ms `status`. It amortises where the install dir is writable and never amortises where it is not. (evidence: python3 -X importtime: add self 32467us cold vs 1643us warm)
- [SDD · S2 · open · 2026-08-12] a denylist of RETIRED phrases must be paired with an assertion that each retired sentence's CLAIM survived — otherwise the cheapest way to pass is deleting the paragraph, which makes the doc shorter and worse. R:NEUTERED (evidence: add-method/tests/skill/test_front_door_copy.py)
- [SDD · S1 · open · 2026-08-12] a skill-surface addition has a three-tree blast radius; a scope narrower than that ships a red suite and the architecture residue lens is what catches it (evidence: /tasks/domain-evidence-recipe.d/runs/2.md)
