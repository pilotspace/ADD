---
type: Spec
lens: quality
---
## Now
The suite is `cd add-method && python3 -m pytest -q`, run by CI on Python 3.10 and 3.12. It guards
the package's shape (one skill, no engine), the installer twins, version agreement, and the book.

## Decisions that bind
- D1 a check that can pass on nothing is not a check — every guard asserts on something that exists first (evidence: archive/add-3x-bundle/specs/quality.md Q2, Q27)
- D2 SKILL.md has a line ceiling, pinned in one place (evidence: add-method/tests/test_skill_only.py)

## Deltas
