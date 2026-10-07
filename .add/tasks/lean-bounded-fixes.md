---
type: Task
title: act on rounds 7–8 and the SWE-bench Lite pilot — bounded fixes take the Quick lane, guesses only where the spec is silent, contradictions resolved in the caller's favour, honest price in the READMEs
status: done
kind: docs
risks: [method-drift, teaching-to-the-meter, front-door-claim-truth]
scope: [add-method/skill/add/, add-method/src/add_method/_bundled/skill/add/, .claude/skills/add/, add-method/tests/test_round8_lessons.py, add-method/tests/test_skill_only.py, README.md, add-method/README.md, benchmark/results/2026-10-add-4.0-low-effort-vs-vanilla.md, benchmark/swe/runner.py, benchmark/tests/test_swe_smoke.py, add-method/CHANGELOG.md, add-method/tests/test_docs_value.py, add-method/tests/test_docs_tradeoff.py, benchmark/arms/variants/BASE-4.0.0-SKILL.md, benchmark/tests/test_arm_models.py, benchmark/tests/test_arm_effort.py]
gives: [S1 the shipped skill tree skill/add]
---
## CARD
goal: cut ADD's cost on bounded work without losing the tests that carry its measured value, fix the one broken path, and replace the README's contaminated price with the isolated one
why: round 8 (isolated) — ADD at low ties vanilla at medium on correctness, wins test strength (amb1 mutation 0.83 vs 0.19), costs 1.3–1.9×; SWE Lite pilot — 23/30 vs 21/30 at 2.7×, and 26 of 30 ADD patches touch ≤3 files yet every run paid for a full Task, because the floor sends any fix that *touches* a consumed surface to a Task

## RULES
- M1 a fix that restores a consumed surface's intended behaviour without changing its shape (signature, return shape, status code, format) is not floor work by itself; changing that shape is (from: benchmark/SWE-LITE-PILOT-2026-10-03.md — 26/30 patches ≤3 files, all routed to a Task by the "touching a surface" floor) (derived: the floor guards consumers against contract change; a bug fix that keeps the shape breaks no consumer)
- M2 a Quick commit records its sizing and evidence as an artifact in the commit body: `lane: quick — <why it fits>` and `red→green: <test> · suite: <cmd> → <result>` (from: PILOT-4v3-2026-09-30-r5 — a rule transfers when it names an artifact the model writes, not when it advises)
- M3 ASSUMPTIONS hold only real silences: a dimension the request settles gets no line, and `- none — <why>` is a valid section (from: PILOT-4v3-2026-10-02-r7 round 8 — with operator config isolated, vanilla handled 5.0 of 7 ambiguities against ADD's 5.3; the sweep's measured edge is small and it costs output)
- M5 the skill and references/personas.md send the model to `.add/personas-index/use-when.md`, where the installer puts it (from: benchmark/PROMPT-AUDIT-2026-10-02.md findings 1–2)
- M6 both READMEs state round 8's isolated price (1.3–1.9× the dollars, 1.8–2.4× the minutes), recommend `--effort low`, name the operator-config contamination of the earlier minutes, and quote the amb1 mutation gap pooled over rounds 8–9 (0.81 vs 0.43), not round 8's 0.83 vs 0.19 (from: PILOT-4v3-2026-10-02-r7 — the 4.0–5.1× minutes were the operator's security-guidance plugin reviewing every commit)
- M7 the SWE-bench runner's ADD prompt lets the skill size the work instead of forcing one Task (from: SWE-LITE-PILOT — the prompt demanded a freeze commit)
- R:BUDGET SKILL.md stays ≤ 200 lines (from: add-method/tests/test_skill_only.py)
- R:MIRROR the three shipped skill trees stay identical (from: PROJECT.md invariants)

## ASSUMPTIONS
- A1 [which] M4 moves amb1's A-conflict-response item to the reading the ambiguity meter scores as defensible → a gain there after this change is taught, not emergent → reported that way
- A2 [which] M1 narrows the floor → a real contract change misread as "restores behaviour" escapes to Quick → the C11 tripwire ("is a Task now") stays, and M1 names shape change explicitly
- A3 [which] item 2 of the improvement list (split SKILL.md to shrink context) is dropped → it saves ≈ $0.01 a run (3.3k tokens × ~15 calls × $0.20/M) and contradicts test_a_task_needs_no_second_file · found: per-run cache-read delta is driven by calls 6.3→15.4, not skill bytes (evidence: costsplit on benchmark/runs-swe/pilot30-s0)

## PLAN
strategy: red guards in add-method/tests/test_round8_lessons.py (+ the SWE prompt test) pin M1–M7; edit SKILL.md compressing elsewhere to stay ≤ 200; mirror the trees; rewrite the README price line + table from round 8 with a results file; then re-measure — SWE Lite pilot slice (30, seed 0) ADD arm + amb1 ×3 — as the behavioural evidence
check: cd add-method && python3 -m pytest -q tests/test_round8_lessons.py && cd .. && python3 -m pytest -q benchmark/tests/test_swe_smoke.py
regression: cd add-method && python3 -m pytest -q ; python3 -m pytest -q benchmark/tests

## CHECKS
- C1 covers: M1 · acceptance · add-method/tests/test_round8_lessons.py::test_floor_is_shape_change_not_touch · falsifier: the floor still says "a surface other code consumes" with no shape qualifier
- C2 covers: M2 · acceptance · add-method/tests/test_round8_lessons.py::test_quick_commit_carries_its_lane_and_evidence · falsifier: Quick still ends at "a one-line why"
- C3 covers: M3 · acceptance · add-method/tests/test_round8_lessons.py::test_assumptions_hold_only_real_silences · falsifier: the six-dim sweep still asks for a line per dimension
- C5 covers: M5 · acceptance · add-method/tests/test_round8_lessons.py::test_persona_index_path_resolves · falsifier: either file still says the bare `personas-index/use-when.md`
- C6 covers: M6 · acceptance · add-method/tests/test_round8_lessons.py::test_readmes_state_the_isolated_price · falsifier: "4.0–5.1× the minutes" survives in either README
- C7 covers: M7 · acceptance · benchmark/tests/test_swe_smoke.py::PromptTest::test_add_arm_lets_the_skill_size_the_work · falsifier: the prompt still demands a freeze commit for every issue
- C8 covers: R:BUDGET · regression · add-method/tests/test_skill_only.py::test_skill_md_stays_short · falsifier: the rules land by growing past 200 lines
- C9 covers: R:MIRROR · regression · add-method/tests/test_skill_only.py::test_shipped_skill_trees_are_identical · falsifier: only skill/add is edited

## LOG
- refreeze: scope grows to the two README guard tests — they pin the measured section's numbers to the 2026-09 results page; M6 moves the section to the 2026-10 page, so the guard must read the page the section links (same strength: every number still traces to a cited results page)
- refreeze: scope grows to the benchmark variant tests — they diffed the round-6/7 variants against the LIVE skill, which this task changes; they now diff against a snapshot of the 4.0.0 skill the variants were cut from (same assertion, stable base)

- refreeze: M4 (contradictions → the caller-in-control reading) is dropped — round 9 (benchmark/runs-r9-lean): all 3 amb1 runs took "reject", which left the spec's waitlist requirements 4–6 without anything to act on; ambiguities handled fell 5.3 → 4.0 and one run's oracle fell to 0.88. A1 predicted the meter risk; the cost was in requirements, not only the meter. C4 goes with it.
- refreeze: M6 restates the mutation gap pooled over rounds 8–9 — round 9 vanilla scored 0.67 on amb1 against round 8's 0.19, so 0.83 vs 0.19 overstated the gap

## EVIDENCE
freeze: 1f3a25d4 · refreeze: 0a7fa836 · head: 00a8384e
seal: git diff 0a7fa836 00a8384e -- .add/tasks/lean-bounded-fixes.md add-method/tests/test_round8_lessons.py benchmark/tests/test_swe_smoke.py → empty
check: `cd add-method && python3 -m pytest -q tests/test_round8_lessons.py` → exit 0 · 5 passed; `python3 -m pytest -q benchmark/tests/test_swe_smoke.py` → exit 0 · 22 passed
regression: `cd add-method && python3 -m pytest -q` → exit 0 · 159 passed; `python3 -m pytest -q benchmark/tests` → exit 0 · 547 passed, 12 skipped
consumers: S1 skill tree → the bundled + .claude copies are byte-identical (test_shipped_skill_trees_are_identical green); the installer ships it (probe 1)
residue: security — text-only change, no new commands; architecture — A2 (M1 narrows the floor) stands, guarded by "is a Task now"; concurrency — n/a
probes: (1) fresh `pilotspace-add init` in a temp dir: the path the installed SKILL.md names, `.add/personas-index/use-when.md`, exists → pass · (2) the installed skill carries the shape-change floor → pass · (3) the reverted contradiction rule is absent from the installed skill → pass
behaviour (rounds 9 + SWE rerun, isolated, n = 3 / n = 30):
- M1 transferred: SWE Lite slice 30/30 ADD runs took the Quick lane (0 task files, was 14); cost $7.56 → $4.94 (−35%, 2.7× → 1.8× vanilla), 86 s → 49 s per instance; tests in 30/30 patches
- resolved 21/30 (was 23/30; vanilla 21/30): lost scikit-learn-14087, sphinx-8801, sympy-19007; gained sympy-13915 — one sample at n = 30, not separable from noise
- M2 did not transfer: 7 of 30 runs committed in the foreign repo, 1 of those 7 wrote `lane: quick` — kept, logged as not yet effective
- M4 measured harmful in round 9 and was reverted (refreeze 0a7fa836)
- wm1/amb1: ADD-low ties vanilla on oracle and edges; mutation pooled r8–9 0.86 vs 0.78 (wm1), 0.81 vs 0.43 (amb1); cost unchanged ($0.28–0.30 a run)
lens: build=self · refute=self cold reread (no security risk) · found: 1 confirmed (M4 harmful, round 9), 0 rejected
verdict: RISK-ACCEPTED — every check held on this commit; the open risk is that the Quick lane trades some SWE resolve rate for −35% cost (23 → 21 of 30, within noise). Owner: Tin Dang, to settle with the full 300-instance run before the next release.
