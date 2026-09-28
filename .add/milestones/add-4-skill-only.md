---
type: Milestone
title: ADD 4.0 — one skill, no engine
status: done
---
## CARD
goal: ADD ships as one markdown skill the model follows with git and the project's test command — no engine, no CLI verbs, no approval gate
why: the 3.x engine cost 18.2M tokens where spec-kit cost 3.8M at comparable fidelity (benchmark/BENCHMARK.md), and most of its growth guarded its own stamps; Opus-class models plan well enough to run the method from prose

## SCOPE
In:  the skill (SKILL.md + references/format.md + references/explore.md, persona-author kept) ·
     deleting the engine, the agent roster and their tests · installer twins reduced to copy +
     scaffold + 3.x cleanup · the book and front-door docs rewritten · this repo's bundle archived
     and re-seeded as 4.0 · version 4.0.0
Out: publishing 4.0.0 (the human tags it) · the root benchmark/ harness (historical, kept as-is) ·
     finishing any 3.x milestone (archived with the 3.x bundle)

Run note: this milestone was driven directly, not through task files — the loop it ships did not
exist yet while the engine was being removed. Evidence is the commits and the guard tests.

## EXIT
- [x] the method is SKILL.md plus two references, and no engine or roster file ships — evidence: add-method/tests/test_skill_only.py (7 pass) · 98ccf487 · 0c94030f
- [x] both installers install the skill, personas and a 4.0 bundle, and remove a 3.x `.add/tooling/` — evidence: installer tests (89 pass, incl. upgrade over published 3.6.0 artifacts) · 3014c021
- [x] the book and front-door docs teach only 4.0, with a migration page — evidence: add-method/tests/book/ · mkdocs build --strict exit 0 · c157c3f7
- [x] every version declaration reads 4.0.0 and the CHANGELOG says what was removed — evidence: add-method/tests/test_version_parity.py · the release-prep commit
- [x] this repo's `.add/` is a 4.0 bundle and the 3.x bundle is archived — evidence: add-method/tests/test_repo_dogfood.py · 01ec1e2a

## TASKS
- skill — write SKILL.md and its two references
- remove-engine — delete the engine, roster and their tests (after: skill)
- installers — reduce both installers to the 4.0 payload (after: remove-engine)
- book — rewrite the book and front-door docs (after: skill)
- dogfood — archive the 3.x bundle, seed this repo's 4.0 bundle (after: skill)
- release-prep — version 4.0.0, CHANGELOG (after: installers, book, dogfood)
