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
state: 4.1.0 prepared on feat/add-low-effort-bench (PR #232): skill tasks lean-bounded-fixes, value-final, blind-spots, maintainer-intent, cut-sites-record closed; fresh SWE-bench Lite 300 at medium effort ADD 226 vs vanilla 215 (p = 0.099); READMEs recommend --effort medium; suites 192 + 560 pass. Before: 4.0.0 cut on feat/add-4-skill-only (milestone add-4-skill-only done; close-research-gaps PASS — closed-loop invariants and persona routing stated in the skill, 4 references; full suite 134 pass); 3.7.0 (PR #224) is the last engine release; the 3.x bundle is archived at archive/add-3x-bundle/
next: owner's 6-issue blinded review study (benchmark/review-study) → owner approves PR #232 → merge → owner tags v4.1.0 (publishes npm + PyPI)
