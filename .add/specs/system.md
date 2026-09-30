---
type: Spec
lens: system
---
## Now
`add-method/` is the package: the skill (`skill/add/`), starter personas (`personas/`), the vendored
teacher corpus (`personas-teacher/`, `personas-index/`), two installer twins (`bin/cli.js` for npm,
`src/add_method/` for pip, with `_bundled/` as pip's copy of the payload), and the book (`docs/`).

## Decisions that bind
- D1 the npm and pip installers are twins: same flags, same resulting tree (evidence: add-method/tests/test_npm_pip_parity.py)
- D2 the skill ships in three identical trees; edit `skill/add/` and mirror it (evidence: add-method/tests/test_skill_only.py)
- D3 an installer never overwrites a user's file; it refreshes only what ADD owns (the skill, the teacher corpus) (evidence: installer tests)

## Deltas
