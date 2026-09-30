---
type: Task
title: close the gaps round 3 found — rule coverage, checked guesses, subagent cost, input robustness
status: build
kind: docs
risks: [method-drift, turn-cost, teaching-to-the-meter]
scope: [add-method/skill/add/, add-method/src/add_method/_bundled/skill/add/, .claude/skills/add/, add-method/tests/test_skill_only.py, add-method/CHANGELOG.md]
gives: [S1 the shipped skill tree skill/add]
---
## CARD
goal: the skill closes the four gaps benchmark/PILOT-4v3-2026-09-29.md and the task-contract audit found, without adding turns to ordinary work
why: 2 of 6 contracts left a Must without a check; `found:` appeared 0–1 times per task; the second reader cost 2.3× on amb1 (one run spawned 3 subagents, one slept on a wakeup waiting for one); 5 of 9 apps 5xx'd on a null or number body

## RULES
- M1 SKILL.md states that every RULES id appears on some `covers:` line before the seal (from: task-contract audit 2026-09-29 — amb1 rep1 M4, rep2 M5 uncovered)
- M2 SKILL.md asks the agent to check its cheap guesses now and record `found:` (from: audit — 0–1 `found:` per task)
- M3 a fresh subagent is spawned only for security work, at most one per beat, run in the foreground; every other second read or refute is the agent's own cold reread under the counter-lens (from: PILOT-4v3-2026-09-29 — amb1 cost 2.3×, 3 subagents in one run, a ScheduleWakeup wait) (derived: data/architecture keep the cold reread, not a spawn)
- M4 a surface that takes input gets a check that malformed or wrong-typed input is refused, never a crash (from: quality edge suite — null/number bodies 5xx in 5 of 9 apps; `bool` passing an int check)
- R:BUDGET SKILL.md stays ≤ 200 lines (from: add-method/tests/test_skill_only.py)
- R:CONSISTENT every reference (format · explore · evidence · personas) says the same as SKILL.md about when and how many subagents are spawned (from: derived: two readers of one rule must agree; widened at refute — explore.md still said "parallel subagents")

## ASSUMPTIONS
- A1 [which] M4 overlaps what the held-out edge suite measures → a gain there after this change is partly taught, not emergent → reported that way in the remeasure
- A2 [experience] data/architecture work losing its subagent may weaken the second read → the invite-expiry gain came from a security task, which keeps it → watch amb1/wm1 quality for a drop

## PLAN
strategy: red guard tests pinning M1–M4 and the subagent rule in both references; compress SKILL.md to absorb; mirror trees; then the same-day benchmark (add-4 vs vanilla, wm1+amb1, n=3) is the behavioural evidence
check: cd add-method && python3 -m pytest -q tests/test_skill_only.py
regression: cd add-method && python3 -m pytest -q

## CHECKS
- C1 covers: M1 M2 M4 · acceptance · tests/test_skill_only.py::test_round3_gaps_are_stated · falsifier: the rule lives only in a reference the model never opens
- C2 covers: M3 R:CONSISTENT · acceptance · tests/test_skill_only.py::test_subagents_are_security_only_one_per_beat_foreground · falsifier: SKILL.md narrows the spawn but a reference (evidence.md, explore.md) still fans work out to subagents
- C3 covers: R:BUDGET · regression · tests/test_skill_only.py::test_skill_md_stays_short · falsifier: gaps closed by growing past the ceiling

## LOG
- 2026-09-30 refreeze at refute: probe P1 (`grep -rn -i "subagent\|spawn" SKILL.md references/`) found references/explore.md:19 "give parallel subagents disjoint questions" — contradicts SKILL.md:46 "at most one per beat, in the foreground". R:CONSISTENT named only evidence.md and personas.md, so C2 could not see it. R:CONSISTENT widened to every reference; C2 now walks REFERENCES and flags "parallel subagents". Strengthened, not weakened.

## EVIDENCE
<written once, at verify>
