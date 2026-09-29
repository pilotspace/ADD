---
type: Project
title: AIDD-Book
goal: ship ADD as one markdown skill any agent can follow — direction before build, evidence over inspection, a durable bundle — installable as @pilotspace/add / pilotspace-add, with no engine and no lost context across sessions
invariants:
  - the method is skill/add/SKILL.md plus references/{format,explore,evidence,personas}.md — no engine code ships (add-method/tests/test_skill_only.py)
  - the three shipped skill trees are byte-identical (skill/add, src/add_method/_bundled/skill/add, .claude/skills/add)
  - the npm and pip installers produce the same install
  - every version declaration agrees (add-method/tests/test_version_parity.py)
test_cmd: cd add-method && python3 -m pytest -q
stage: mvp
---
## CARD
goal: the method and its book — shipped as a skill, dogfooded on itself
state: 4.0.0 cut on feat/add-4-skill-only (milestone add-4-skill-only done; full suite 128 pass); 3.7.0 (PR #224) is the last engine release; the 3.x bundle is archived at archive/add-3x-bundle/
next: human review of the 4.0 PR, merge after #224, tag v4.0.0
