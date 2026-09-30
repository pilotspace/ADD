---
type: Task
title: the benchmark can run each arm on its own model and advisor, with two lean ADD arms that switch models by beat
status: build
kind: feature
risks: [measurement-validity, compatibility]
scope: [benchmark/arms/, benchmark/runner/agent.py, benchmark/runner/core.py, benchmark/pilot.py, benchmark/tests/test_arm_models.py, benchmark/tests/test_arms.py, benchmark/tests/conftest.py, benchmark/tests/test_session_mode.py, benchmark/tests/test_wv2_family.py]
gives: [S1 `run-all --model <id>` and the arm-toml keys `model` / `advisor`]
---
## CARD
goal: run the round-6 benchmark on claude-sonnet-5-5 and compare two model-switching ADD arms — Build on a Haiku subagent, and a Haiku main session with a Sonnet 5.5 advisor — against ADD and vanilla
why: Direction is 56% of ADD's wall time (4.1 of 7.3 min) and about 44% of its tokens; the harness pins every arm to claude-sonnet-5, so neither a newer model nor a per-beat model switch can be measured

## RULES
- M1 an arm toml may set `model` and `advisor`; both default to empty (from: request — "smart model switcher by advisor")
- M2 `run-all --model <id>` (and `run_reps` / `run_pilot` `model=`) sets the model for every arm that does not set its own; the resolved model is `arm.model` or the `--model` value or `PINNED_MODEL` (from: request — "run benchmark use sonnet-5-5")
- M3 the live argv carries `--model <resolved>` and `--effort medium`, plus `--advisor <advisor>` only when the arm sets one (from: research — `--advisor <model>` works headless, probed 2026-09-30)
- M4 every record's artifacts carry the resolved model, and `advisor` when set, so a comparison can be checked for a model mix-up (from: benchmark/runner/agent.py — the model-pin rationale)
- M5 two arms load: `add-4-lean` runs every add-4 setup step and overwrites the installed SKILL.md with `benchmark/arms/variants/add-4-lean/SKILL.md` after the install and before the workspace's baseline commit; `add-4-advisor` does the same with `model = "claude-haiku-4-5-20251001"` and `advisor = "claude-sonnet-5-5"` (from: request) (derived: the two arms share one variant, so the model switch is the only difference between them)
- M6 the lean variant differs from the shipped skill in exactly three places: stubs only what the checks import; the lead persona is picked by grepping `.add/personas/`, the 65 KB index only grepped when none fits; Build runs in one foreground subagent on `model: haiku`, and the main session verifies (from: PILOT r5 transcripts — 10.7 Direction writes per run, about half stubs; 5 of 6 runs opened the 65 KB index; Build is 53–54% of tokens)
- R:DEFAULT with no `--model` and no arm model, argv and records are exactly as before — `claude-sonnet-5` (from: benchmark/tests — the model-pin tests)
- R:NO_LIVE no test launches the real `claude` binary; the guard refuses at process launch, so a test that replaces the launcher itself may drive `execute_wm` without an injected agent (from: benchmark/tests/conftest.py — the 2026-09-28 live-spend incident)
- R:ARMCOUNT `ARM_NAMES` grows from 8 to 10; the fairness fields stay identical across all arms (from: benchmark/tests/test_arms.py::test_all_arms_validate_with_fairness_parity — its count changes with this contract)

## ASSUMPTIONS
- A1 [which] "sonnet-5-5" means `claude-sonnet-5-5` → found: the model id answers; the bare alias `sonnet-5-5` is refused (evidence: `claude -p … --model claude-sonnet-5-5` → OK; `--model sonnet-5-5` → unrecognized_model)
- A2 [which] Haiku 4.5 takes `--effort medium` and `--advisor` together → found: it does (evidence: `claude -p "reply with just OK" --model claude-haiku-4-5-20251001 --effort medium --advisor claude-sonnet-5-5` → OK)
- A3 [experience] an advisor call is expensive — it received 57.7k uncached input tokens in one consult ($0.13 of a $0.18 run) → the advisor arm may cost more than it saves if Haiku consults often → measured, not assumed
- A4 [which] the variant is measured before it is shipped → it lives under benchmark/arms/variants/, not in add-method/skill/
- A5 [who] a Haiku Build subagent may write weaker code → the sealed checks and the main-session Verify are the guard; mutation, edge and oracle scores show it

## PLAN
strategy: red tests for load, resolution, argv and records; add the fields and plumb `model` through pilot → run_reps → run_pilot → execute_wm → build_argv; write the two arm tomls and the variant skill; then round 6
check: python3 -m pytest -q benchmark/tests/test_arm_models.py benchmark/tests/test_arms.py
regression: python3 -m pytest -q benchmark/tests

## CHECKS
- C1 covers: M1 · acceptance · benchmark/tests/test_arm_models.py::test_arm_toml_model_and_advisor_default_empty · falsifier: the loader ignores the new keys
- C2 covers: M2 R:DEFAULT · acceptance · benchmark/tests/test_arm_models.py::test_resolved_model_prefers_arm_then_flag_then_pin · falsifier: `--model` overrides the advisor arm's own Haiku
- C3 covers: M3 · acceptance · benchmark/tests/test_arm_models.py::test_argv_carries_model_effort_and_advisor_only_when_set · falsifier: `--advisor` with an empty value on every arm
- C4 covers: M4 M2 · acceptance · benchmark/tests/test_arm_models.py::test_execute_wm_passes_and_records_the_resolved_model · falsifier: argv uses the new model but the record still says claude-sonnet-5
- C5 covers: M2 · acceptance · benchmark/tests/test_arm_models.py::test_run_all_cli_accepts_model · falsifier: the flag parses but never reaches run_reps
- C6 covers: M5 R:ARMCOUNT · acceptance · benchmark/tests/test_arm_models.py::test_lean_and_advisor_arms_load · falsifier: the advisor arm runs the shipped skill, or the lean arm pins a model
- C7 covers: M6 · acceptance · benchmark/tests/test_arm_models.py::test_lean_variant_changes_exactly_three_things · falsifier: a variant that also drops a check rule or the seal
- C9 covers: R:NO_LIVE · acceptance · benchmark/tests/test_arm_models.py::test_no_test_can_launch_the_real_claude · falsifier: a guard that only wraps build_argv, which a test calling the launcher directly walks past
- C8 covers: R:ARMCOUNT · regression · benchmark/tests/test_arms.py::test_all_arms_validate_with_fairness_parity · falsifier: arms added with diverging fairness fields

## LOG
- 2026-09-30 refreeze in build: the autouse guard in benchmark/tests/conftest.py wraps `build_argv` with a two-argument signature and raises whenever no agent is injected, so C4 — which replaces `_invoke_once` and launches nothing — cannot run. The guard moves to the launch layer (refuse a process whose binary is `claude`), keeping its purpose; scope widens to conftest.py; R:NO_LIVE and C9 make the safety property a sealed check.
- 2026-09-30 refreeze in build: C6 demanded the arm's first steps equal all four add-4 steps, which puts the variant copy after `workspace_git.py`'s baseline commit — the agent would then see a modified SKILL.md in its working tree, fouling Verify's clean-tree run. C6 now requires every add-4 step in order, with the copy between the install and the baseline commit; M5 says so.
- 2026-09-30 refreeze in build: two older tests pin the old two-argument `build_argv` shape — test_session_mode's spy takes (prompt, agent_cmd), and test_wv2_family greps core.py for the literal `"model": PINNED_MODEL`. Their intent (every WM starts a fresh conversation; every record stamps the model it ran on) is unchanged: the spy passes new arguments through and the grep looks for the resolved model. Scope widens to both files.

## EVIDENCE
<written once, at verify>
