---
type: Task
title: close the closed-loop and persona research gaps in the 4.0 skill
status: build
kind: docs
risks: [method-drift, turn-cost, stale-docs]
scope: [add-method/skill/add/, add-method/src/add_method/_bundled/skill/add/, .claude/skills/add/, add-method/personas/, add-method/src/add_method/_bundled/personas/, .add/, add-method/tests/test_skill_only.py, add-method/CHANGELOG.md, book/, blog/add-4-vs-3-7.html]
gives: [S1 the shipped skill tree skill/add — SKILL.md + references/{format,explore,evidence,personas}.md]
---
## CARD
goal: the 4.0 skill states every closed-loop invariant (C1–C12) and the persona-routing roadmap as prose the model follows, with no engine and no new turns on ordinary work
why: the user asked to close all gaps found against ADD_3_6_Closed_Loop_Research.md and ADD_Dynamic_Persona_Research.md; 4.0 dropped or weakened C4 C6 C9 C11 and none of the persona roadmap was in

## RULES
- M1 SKILL.md binds each gap in a line the model meets on the path it walks: tripwire (C11), rule origin + falsifier (C1 C3), risks-routed evidence (C4 §7), consumers of a changed gives (C9), executable refute by a counter-lens (C4 §10.3), PASS as an evidence claim (§10.1), successor + prevention drain (C8 C10), tag-only-verified + observes (C6 C7), control yield (C12) (from: request · research docs)
- M2 depth lives in two new references read only when a trigger fires: references/evidence.md (closed loop) and references/personas.md (routing, counter-lens, trace, lifecycle, evals) (from: request "enhance with their reference docs" · skill-creator progressive disclosure)
- M3 a persona carries covers-risks, evidence and counter-lens; every starter persona has them and each counter-lens names a real persona (from: persona research §7.2)
- M4 floor work gets a second reader before the seal — the replacement for the removed human pre-approval (§5 correlated semantic error) (from: closed-loop research §5 · method D3)
- R:BUDGET SKILL.md stays ≤ 200 lines and the task template stays inline (from: add-method/tests/test_skill_only.py · method D5)
- R:NOENGINE no code, CLI or approval gate is added (from: method D1 D3)

## ASSUMPTIONS
- A1 [which] "close all gaps" includes C7 runtime monitors, which 3.7 never built → stated as a PLAN `observes:` line for high-risk work, not tooling → a reviewer may want it out of 4.0
- A2 [experience] the second reader and counter-lens refute add a subagent only on floor work → ordinary Task/Quick work gains no turns → if floor work is common, cost rises there
- A3 [which] the three repo personas in .add/personas get the new fields too (dogfood) → small extra diff
- A4 [when] PROJECT.md invariant 1 names the method's files; it is updated to four references in this task → changes a binding line, visible in this task's diff
- A5 [absent] nested subagents may be unavailable to the model → the skill gives a no-subagent fallback (re-read the task file cold under the counter-lens)

## PLAN
strategy: red guard tests first; SKILL.md edits compressed to fit ≤200; references hold depth; mirror trees with prepare_bundle + rsync; then skill-creator evals (new skill vs snapshot) on 3 fixtures
check: cd add-method && python3 -m pytest -q tests/test_skill_only.py
regression: cd add-method && python3 -m pytest -q

## CHECKS
- C1 covers: M2 · acceptance · tests/test_skill_only.py::test_the_method_is_one_skill_file_and_four_references · falsifier: references written but not shipped/mirrored
- C2 covers: M2 · acceptance · tests/test_skill_only.py::test_references_are_routed_by_a_trigger · falsifier: a reference nobody is told when to read
- C3 covers: M1 · acceptance · tests/test_skill_only.py::test_every_closed_loop_invariant_is_stated · falsifier: an invariant only in a reference the model never opens
- C4 covers: M1 M4 · acceptance · tests/test_skill_only.py::test_task_template_carries_risks_and_falsifier · falsifier: prose asks for a falsifier the template has no slot for
- C5 covers: M3 · acceptance · tests/test_skill_only.py::test_starter_personas_carry_routing_fields · falsifier: a counter-lens naming a persona that does not exist
- C6 covers: R:BUDGET · regression · tests/test_skill_only.py::test_skill_md_stays_short · falsifier: gaps closed by growing past the ceiling
- C7 covers: R:NOENGINE · regression · tests/test_skill_only.py::test_no_engine_file_ships + test_skill_prose_sends_the_model_to_no_cli

## EVIDENCE
<written once, at verify>
