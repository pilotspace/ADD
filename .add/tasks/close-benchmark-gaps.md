---
type: Task
title: close the gaps round 3 found — rule coverage, checked guesses, subagent cost, input robustness
status: done
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
verdict: RISK-ACCEPTED — every sealed check holds; M4 is stated but did not change behaviour (below)
freeze: 533ca1c4 · refreeze: 84a0563f · head: 1db784d7
seal: `git diff 84a0563f HEAD -- .add/tasks/close-benchmark-gaps.md add-method/tests/test_skill_only.py` → empty
check: `cd add-method && python3 -m pytest -q tests/test_skill_only.py` → exit 0, 15 passed (clean tree)
regression: `cd add-method && python3 -m pytest -q` → exit 0, 136 passed; three skill trees identical; SKILL.md 200 lines
consumers: S1 is the installed skill tree; the benchmark `add-4` arm installed it at 0ec8b2d5 for six same-day runs, all oracle-green but one (a defect in the generated app, not the skill)
behaviour (benchmark/PILOT-4v3-2026-09-30.md, n = 3 per workload):
- M1 every rule covered: 5 of 6 contracts fully covered (round 3: 4 of 6)
- M2 `found:` 1–3 per task, mean 1.7 (round 3: 0–1)
- M3 0 subagents in 6 of 6 runs (round 3 amb1: 1 · 0 · 3); add-4 amb1 cost $2.51 → $1.61, partly environment
- M4 written in 6 of 6 contracts but at field level; a null / number / non-object body still 5xx'd in 4 of 6 add-4 runs (vanilla 3 of 6) — did not transfer
residue: docs-only change; no security, concurrency or architecture surface. A1 held — the edge suite moved +0.7, so no taught gain to discount
probes:
- P1 `grep -rn -i "subagent\|spawn" SKILL.md references/` → references/explore.md:19 "give parallel subagents" contradicted the budget → refreeze 84a0563f, fixed in e19be2b7
- P2 same grep after the fix → every hit names the budget or a single foreground subagent
- P3 the six round-4 contracts read against M4 → the rule lands on fields, never on the body itself
risk accepted: M4's wording does not reach body-level garbage, and naive-vs-aware timestamps escaped one run the same way. Reason: the fix is a new "shape" sweep, which is a contract change, not a patch to this one. Owner: Tin Dang, at review; the proposal is in the pilot report's "What to optimize" §3
lens: own cold reread (docs work, not security) — caught the explore.md contradiction the sealed check could not see
