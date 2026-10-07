---
type: Task
title: keep what the benchmarks show ADD buys, cut what they show it never does — a Quick test with a falsifier, no dead `found:` step, refute where it measured, and the README's value table from isolated evidence
status: done
kind: docs
risks: [method-drift, front-door-claim-truth, teaching-to-the-meter]
scope: [add-method/skill/add/, add-method/src/add_method/_bundled/skill/add/, .claude/skills/add/, add-method/tests/test_value_final.py, add-method/tests/test_skill_only.py, README.md, add-method/README.md, benchmark/results/2026-10-add-4.0-low-effort-vs-vanilla.md, add-method/CHANGELOG.md]
gives: [S1 the shipped skill tree skill/add]
---
## CARD
goal: align the skill with its measured yield — strengthen the one thin spot (Quick-lane test depth), drop two steps the model never performs, and finalize the README's value table from rounds 8–9 and the SWE-bench pilot
why: the value ADD measurably adds is the checks (falsifier per check → mutation 0.81 vs 0.43), the test discipline (repo tests run in 30/30 SWE runs vs vanilla 7/30; tests shipped 30/30 vs 2/30), the recorded guesses (owner-only 3/3 vs 0/3) and checkable claims — while `found:` (0/24) and refute probes (1/24) are instructions the model does not follow, and the Quick test is one assertion deep (1.3/fix) where the 3 SWE losses were wrong fixes, not regressions

## RULES
- M1 a Quick test covers the request's own example and one case the most plausible wrong fix would pass — its falsifier (from: benchmark/SWE-LITE-PILOT-2026-10-03.md rerun — 1.3 assertions per fix; the 3 lost instances failed FAIL_TO_PASS with 0–1 PASS_TO_PASS failures, i.e. wrong fixes, not regressions) (derived: the falsifier is the practice with the measured mutation gain in the Task lane)
- M2 the ASSUMPTIONS step no longer asks to verify cheap guesses with `found:` (from: 0 of 24 rounds 8–9 task files carry a `found:` line, after round 3 added the instruction; SKILL.md §Learn — a control with zero yield is cut or fixed)
- M3 Refute probes are required for security work, written by the counter-lens; other tasks record `probes: none — <why>` or the probes they ran (from: 1 of 24 task files record probes, 24 of 24 verdicts PASS; the second reader's measured gain came from security work — add-method/tests/test_skill_only.py::test_subagents_are_security_only_one_per_beat_foreground)
- M4 both READMEs' value table carries the isolated measurements: repo tests run (30/30 vs 7/30), tests shipped with the fix (30/30 vs 2/30), and the pooled mutation gap (0.81 vs 0.43); the results page backs them (from: SWE pilot transcripts + PILOT-4v3-2026-10-02-r7.md)
- R:INVARIANTS the closed-loop phrases (second reader, counter-lens, falsifier, …) stay in SKILL.md (from: add-method/tests/test_skill_only.py::test_every_closed_loop_invariant_is_stated)
- R:BUDGET SKILL.md stays ≤ 200 lines · R:MIRROR three trees identical (from: PROJECT.md invariants)

## ASSUMPTIONS
- A1 [which] M1 may raise SWE resolve only if the extra case targets the hidden test's semantics → measured on the same 30-instance slice, not claimed · found: lost instances are F2P failures (evidence: pilot30-s0-lean eval report.json for scikit-learn-14087, sphinx-8801, sympy-19007)
- A2 [which] M3 narrows refute → a non-security task loses a step it never performed (1/24) → no measured loss expected; HARD-STOP paths unchanged
- A3 [which] M2 removes a round-3 guard phrase ("check the cheap ones now") → that guard's own premise (found: almost never used) still holds after the fix attempt, so it is cut, not kept as dead text

## PLAN
strategy: red guards in add-method/tests/test_value_final.py pin M1–M4; edit SKILL.md (Quick paragraph, ASSUMPTIONS bullet, Verify step 5), keep ≤ 200; mirror; README value rows + results page; then re-measure the SWE slice (ADD arm, 30, seed 0) and amb1/wm1 ×3
check: cd add-method && python3 -m pytest -q tests/test_value_final.py
regression: cd add-method && python3 -m pytest -q ; python3 -m pytest -q benchmark/tests

## CHECKS
- C1 covers: M1 · acceptance · add-method/tests/test_value_final.py::test_quick_test_carries_a_falsifier · falsifier: Quick still says only "write the failing test"
- C2 covers: M2, A3 · acceptance · add-method/tests/test_value_final.py::test_no_dead_found_step · falsifier: the ASSUMPTIONS bullet still asks for `· found:`
- C3 covers: M3 · acceptance · add-method/tests/test_value_final.py::test_refute_is_required_for_security_work · falsifier: step 5 still requires probes on every task
- C4 covers: M4 · acceptance · add-method/tests/test_value_final.py::test_readmes_value_table_is_measured · falsifier: the table lacks the test-run or test-shipped rows
- C5 covers: R:INVARIANTS, R:BUDGET, R:MIRROR · regression · add-method/tests/test_skill_only.py · falsifier: a cut removes a closed-loop phrase, or the file grows past 200

## EVIDENCE
freeze: 6fc12fe4 · head: 9d95c588
seal: git diff 6fc12fe4 9d95c588 -- .add/tasks/value-final.md add-method/tests/test_value_final.py add-method/tests/test_skill_only.py → empty
check: `cd add-method && python3 -m pytest -q tests/test_value_final.py` → exit 0 · 4 passed
regression: `cd add-method && python3 -m pytest -q` → exit 0 · 163 passed; `python3 -m pytest -q benchmark/tests` → exit 0 · 549 passed, 12 skipped
consumers: S1 skill tree → three trees byte-identical (test_shipped_skill_trees_are_identical green)
residue: security — text-only change, no new commands; architecture — none; concurrency — n/a
probes: none — no security risk; behaviour was measured instead (below)
behaviour (round 10, isolated, claude-sonnet-5-5; wm1/amb1 n = 3 per cell; SWE Lite 30 instances seed 0, official harness):
- SWE resolved: ADD-low 24/30 (lean skill 21, 4.0.0 23); vanilla-medium 20, vanilla-low 21, ADD-medium 22. ADD-low ⊇ vanilla-medium, plus django-11630, django-13158, sympy-14817, sympy-19007
- M1 falsifier: the A1 hypothesis held on the slice. 2 of the 3 lean-skill losses came back (sphinx-8801, sympy-19007), and sympy-13915 was lost
- SWE cost $5.46 / 30 ($0.23 per resolved, 59 s per issue) against vanilla-medium $2.83 ($0.14, 27 s); repo tests run 30/30 vs 11/30; tests shipped 30/30 vs 1/30
- wm1/amb1: oracle 1.00 and edges 22/22 in every cell; amb1 ambiguities ADD-low 5.3 vs vanilla 4.3; mutation ADD-low 0.92 · 0.78 vs vanilla-medium 0.75 · 0.67; seals intact and verdict PASS on every ADD run
- M4: README rows trace to the results page (test_docs_value green)
lens: build=self · refute=self cold reread (no security risk) · found: 0 confirmed, 0 rejected
verdict: PASS — every check held on this commit, and the re-measure recovered the lean skill's SWE loss (21 → 24 of 30) at a cost below 4.0.0's ($5.46 vs $7.56). Directional at n = 30; the full 300 remains the release-grade test.
