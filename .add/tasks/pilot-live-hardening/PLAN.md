# TASK: live-pilot hardening: idempotent add venv, drop bogus sanity setup lines, npx gsd, runner survives unlaunchable setup

slug: pilot-live-hardening · created: 2026-07-07 · stage: mvp
milestone: add-bench
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 0 · GROUND — the real codebase

Touches (files · symbols): `benchmark/runner/core.py:_run_setup_steps` (subprocess.run without FileNotFoundError handling — crashes the pilot on an unlaunchable command, violating bench-runner's frozen 'visible, never swallowed' Must) · `benchmark/arms/{add,vanilla,plan-mode,gsd}.toml:setup_steps` (content, not frozen shape)
Context (working folder): live-pilot failure evidence in benchmark/runs/*/wm1/record.json (all failed at setup, 0 tokens spent) + pilot-run.log FileNotFoundError traceback
Honors (patterns / conventions): fail-loud (a crash is NOT loud-in-the-record — the record is the loud surface); list-argv only; TOML content edits are pre-authorized by bench-pilot-report's frozen §3 flag ('a targeted fix to two TOML lines + a re-run')
Anchors the contract cites: `_run_setup_steps` · `benchmark/arms/*.toml:setup_steps`
Ground SHA: 4553494

---

## 1 · SPECIFY — the rules

Feature: live-pilot setup hardening
Must:
  - an unlaunchable setup command (FileNotFoundError/OSError at exec) fails that ATTEMPT loudly — "setup: <argv> -> unlaunchable: <err>" in attempts+transcript, record status="failed" — the pilot process never crashes
  - add arm venv line is idempotent under retry/resume (`uv venv .venv --clear`)
  - vanilla/plan-mode setup_steps are empty (no ceremony IS their arm definition)
  - gsd setup uses `npx -y get-shit-done-cc@1.42.3 init` (no global-install PATH dependency)
Reject:
  - a setup command that launches but exits nonzero -> unchanged existing behavior (failed attempt, visible)
Accept: Given an arm whose setup line names a nonexistent binary, When execute_wm runs, Then a validate()-clean record with status="failed" is written whose attempts note the unlaunchable step, and the calling process does not raise.
Assumptions: none material — biggest risk: gsd's npx package may expose a different init entrypoint; if wrong, that one arm records failed loudly (no crash) and iterates.

---

## 3 · CONTRACT — freeze the shape

```
_run_setup_steps: subprocess launch errors (FileNotFoundError/OSError) -> (False, log) with
  "setup: <argv> -> unlaunchable: <ExcName: msg>"; execute_wm converts to status="failed" record (existing path)
arms/add.toml     setup_steps[0] = "uv venv .venv --clear"
arms/vanilla.toml setup_steps = []
arms/plan-mode.toml setup_steps = []
arms/gsd.toml     setup_steps = ["npx -y get-shit-done-cc@1.42.3 init"]
```

`Least-sure flag surfaced at freeze:` [spec] gsd's npx init entrypoint is assumed from its npm bin — why: not spiked; if wrong: that arm records failed loudly and the line iterates (cost: one TOML line, no shape change)
Status: FROZEN @ v1 — approved by Tin Dang (2026-07-07, the fix-all-3 + resume answer)

---

## 4 · TESTS — failing-first (red)

Plan: test_unlaunchable_setup_fails_attempt_loudly (drives execute_wm with a setup line naming a nonexistent binary; asserts failed record + unlaunchable note + no raise) · test_arm_setup_lines_hardened (asserts the 4 TOML content changes).
Tests live in: `benchmark/tests/` (test_pilot_hardening.py) · MUST run red before Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `benchmark/runner/core.py` `benchmark/arms/` `benchmark/tests/`
Strategy & known-problem fixes: red tests → try/except around subprocess.run in _run_setup_steps → TOML edits. Trap: don't catch inside-command failures differently (nonzero exit path unchanged).
Approach (domain strategy): obvious, correctness-first; persona: methodology-engine-dev.
Strategy actually used: as planned; confirmed plan-mode's arm identity is carried by prompt_wrapper='plan-then-execute' (core.py:_wrap_prompt), so dropping its broken setup line loses nothing.
Code lives in: `./src/`   ·   Constraints: change no test, no contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build (82/82, incl. 2 new)
- [x] green was EARNED — the unlaunchable test drives the REAL execute_wm with a real missing binary, no mock
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP) — try/except + TOML data only

Build expectations (from §1 Accept + §3 CONTRACT): unlaunchable-setup test passes with a real nonexistent binary through execute_wm (failed record, 'unlaunchable' in attempts, no raise); TOML asserts green — confirmed: 82/82 suite green.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (fix-all-3 + resume decision) · date: 2026-07-07
OBSERVE: [TDD · open] hermetic fake-agent tests cannot catch a setup line that only fails against the real environment (missing binary, prompt-less --print, non-idempotent venv) — a cheap real-exec smoke of each arm's setup_steps in a tmp dir belongs in the suite (evidence: 3 arms failed at live setup with 0 hermetic failures)

