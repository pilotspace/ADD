# TASK: Pilot round-2 hardening: agent cwd + headless permissions + pytest-capable regression scoring

slug: pilot-cwd-hardening · created: 2026-07-07 · stage: mvp
milestone: add-bench
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).

---

## 0 · GROUND — the real codebase

Touches (files · symbols): `benchmark/runner/core.py:_invoke_once` (Popen has NO cwd — agent inherits pilot cwd = repo root; wm1 transcript shows the agent exploring the harness and asking a meta-question instead of building) · `benchmark/runner/core.py:execute_wm` (call site, must pass workspace_dir) · `benchmark/score.py:compute_regression_rate` (hard-codes `sys.executable -m pytest`; homebrew python3.14 lacks pytest → exit 1 + "No module named pytest" on stderr slips the `returncode not in (0,1)` guard and parses as 0 collected)
Context (working folder): round-2 evidence in `benchmark/runs/add/wm{1..3}/` — status done, workspace contains only `.add/` scaffolding, oracle `app_reachable: false`, judge honestly scored 0.0; pilot aborted at add-wm3 scoring with `regression_run_failed: no regression tests collected`
Honors (patterns / conventions): injectable-argv seams stay intact (`build_argv`, `judge_cmd`); fail-loud BenchError codes; list-argv no shell=True; wrapper scripts live OUTSIDE the repo (scratchpad) so `--dangerously-skip-permissions` is a launch-time concern, not frozen code
Anchors the contract cites: `_invoke_once`, `execute_wm`, `compute_regression_rate`, `_pytest_argv` (new)
Ground SHA: 0ff7d75

---

## 1 · SPECIFY — the rules

Feature: pilot round-2 hardening (agent sandbox cwd + pytest-capable regression scoring)
Must:
  - `_invoke_once` accepts a required `cwd` kwarg and passes it to Popen; `execute_wm` passes the WM workspace dir — the agent process starts INSIDE its sandbox, never the repo root.
  - `compute_regression_rate` builds its pytest argv via `_pytest_argv()`: `[sys.executable, -m, pytest]` when `importlib.util.find_spec("pytest")` resolves, else the uv fallback `["uv","run","--no-project","--with","pytest","python","-m","pytest"]`.
Reject:
  - regression pytest run yields 0 collected tests -> "regression_run_failed" message MUST now include stderr (so a missing-module cause is visible, not silent)
Accept: Given a fake agent argv that prints its os.getcwd(), When execute_wm runs it, Then the transcript records the workspace dir (not the repo root); And Given no pytest in the current interpreter (find_spec patched to None), When _pytest_argv() is called, Then it returns the uv fallback argv.
Assumptions: ⚠ `uv` present on PATH for the fallback — true on this host (pilot setup_steps already depend on it); if wrong: regression scoring raises loudly with stderr attached (fail-loud, not silent 0).

---

## 3 · CONTRACT — freeze the shape

```
_invoke_once(argv, *, cwd: pathlib.Path, timeout_s, log_path) -> (outcome, lines, first_edit_elapsed)
    Popen(..., cwd=str(cwd), start_new_session=True)   # agent starts inside the sandbox
execute_wm: _invoke_once(..., cwd=workspace_dir, ...)

score.py:
_pytest_argv() -> list[str]
    find_spec("pytest") is not None -> [sys.executable, "-m", "pytest"]
    else                            -> ["uv", "run", "--no-project", "--with", "pytest", "python", "-m", "pytest"]
compute_regression_rate: argv = [*_pytest_argv(), "-m", "regression", "-p", "no:cacheprovider", "--tb=no", "-q", str(WM3_REGRESSION_TEST_PATH)]
    total == 0 -> BenchError(f"regression_run_failed: no regression tests collected\n{stdout}\nstderr:\n{stderr}")
```

`Least-sure flag surfaced at freeze:` [test] the fake-agent cwd assertion — a wrapper script echoing $PWD must be read back from the transcript, whose format (raw lines appended) could swallow it; if wrong: test flakes, cost = one rewrite of the assertion to read the fake agent's own side-effect file instead.
Status: FROZEN @ v1 — approved by Tin Dang (via the standing "fix minimally + resume" round-1 precedent, unattended GO).

---

## 4 · TESTS — failing-first (red)

Plan: `benchmark/tests/test_pilot_cwd_hardening.py` — test_agent_runs_inside_workspace (fake agent writes os.getcwd() to a side-effect file; assert == workspace dir) · test_pytest_argv_falls_back_to_uv (find_spec patched None) · test_pytest_argv_uses_sys_executable_when_available (find_spec patched truthy) · test_zero_collected_error_includes_stderr (subprocess.run patched: rc=1, empty stdout, stderr="No module named pytest"; assert message carries it).
Tests live in: `benchmark/tests/` · MUST run red before Build.

---

## 5 · BUILD — AI writes code

Scope (may touch): `benchmark/runner/core.py` · `benchmark/score.py` · `benchmark/tests/test_pilot_cwd_hardening.py`
Strategy & known-problem fixes: add cwd kwarg (trap: keep signature keyword-only to match existing call style) · _pytest_argv seam kept module-level so tests patch `benchmark.score.importlib` cleanly · stderr appended to the zero-collected raise (trap: don't touch the rc-not-in-(0,1) raise, already carries stderr).
Approach (domain strategy): obvious, correctness-first — two-line cwd plumbing + one small argv seam.
Strategy actually used: as planned.
Code lives in: `benchmark/` · Constraints: change no test, no contract; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass (86/86 benchmark suite incl. 4 new) · coverage held · no test or contract altered during build
- [x] green was EARNED — cwd asserted via the fake agent's own side-effect file; argv seams asserted literally; stderr propagation asserted on a patched subprocess
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP)

Build expectations (from §1 Accept + §3 CONTRACT): fake agent's recorded cwd == workspace dir; _pytest_argv returns uv fallback when pytest unimportable; zero-collected BenchError message contains the stderr text — confirmed by the 4 new tests + full benchmark suite green.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-07
