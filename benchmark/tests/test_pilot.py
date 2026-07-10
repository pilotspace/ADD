"""Scenarios: pilot orchestration — resolve_setup_steps, attest_record,
run_pilot (M4-M10, R3-R7) — fully hermetic via the fake-agent/fake-judge
seam, zero live `claude` calls (grep-checked: this module never invokes the
live claude binary)."""
from __future__ import annotations

import pathlib
import sys
import textwrap

import pytest

from benchmark import pilot as pilot_mod
from benchmark.arms.loader import ARM_NAMES, Arm, load_arm
from benchmark.runner.records import write_record_atomic
from benchmark.schema.run_record import BenchError, validate

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
ARMS_DIR = REPO_ROOT / "benchmark" / "arms"


def test_no_live_claude_call_in_this_module():
    """Guard: this test module never spawns the literal `claude` binary argv
    (mirrors bench-scoring's own no-live-claude assertion pattern) — every
    agent_cmd/judge_cmd used below is a fake stdlib script. Excludes this
    function's own body (the docstring/assert text legitimately names the
    live binary while describing the guard itself)."""
    import ast

    tree = ast.parse((REPO_ROOT / "benchmark" / "tests" / "test_pilot.py").read_text())
    this_fn = "test_no_live_claude_call_in_this_module"
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name != this_fn:
            for sub in ast.walk(node):
                if isinstance(sub, ast.Constant) and isinstance(sub.value, str):
                    assert "claude" not in sub.value, f"{node.name} names the live claude binary"


def _write_script(tmp_path: pathlib.Path, name: str, body: str) -> pathlib.Path:
    script = tmp_path / name
    script.write_text(textwrap.dedent(body))
    script.chmod(0o755)
    return script


def _fake_agent_ok(tmp_path: pathlib.Path, name: str = "fake_ok.py") -> list[str]:
    script = _write_script(
        tmp_path,
        name,
        """
        #!/usr/bin/env python3
        import json, sys
        print(json.dumps({
            "type": "result",
            "total_cost_usd": 0.01,
            "usage": {"input_tokens": 10, "output_tokens": 5,
                      "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0},
        }))
        sys.exit(0)
        """,
    )
    return [sys.executable, str(script)]


def _fake_agent_fail(tmp_path: pathlib.Path, name: str = "fake_fail.py") -> list[str]:
    script = _write_script(
        tmp_path,
        name,
        """
        #!/usr/bin/env python3
        import sys
        sys.exit(1)
        """,
    )
    return [sys.executable, str(script)]


def _fake_judge(tmp_path: pathlib.Path, value: str = "0.75", name: str = "fake_judge.py") -> list[str]:
    script = _write_script(
        tmp_path,
        name,
        f"""
        #!/usr/bin/env python3
        import sys
        print({value!r})
        """,
    )
    return [sys.executable, str(script)]


def _blank_arm(name: str) -> Arm:
    return Arm(
        name=name,
        setup_steps=[],
        prompt_wrapper="raw",
        pin="",
        same_model=True,
        token_ceiling=200000,
        turn_ceiling=60,
    )


def _seed_record(runs_root: pathlib.Path, arm: str, wm: int, **overrides) -> None:
    defaults = dict(
        arm=arm,
        wm=wm,
        rep=0,
        status="done",
        metrics={
            "regression_rate": 0.0,
            "spec_fidelity": 0.0,
            "tokens_total": 0.0,
            "cost_usd": 0.0,
            "context_rot_slope": 0.0,
            "time_to_first_edit": 0.0,
        },
        artifacts={"workspace": "w", "transcript": "t", "oracle_report": "o"},
    )
    defaults.update(overrides)
    record = validate(defaults)
    write_record_atomic(runs_root / arm / f"wm{wm}" / "record.json", record)


# --------------------------------------------------------------------------
# M5, M6, R7 — resolve_setup_steps
# --------------------------------------------------------------------------


def test_resolve_setup_steps_substitutes_token(tmp_path):
    arm = load_arm(ARMS_DIR / "add.toml")
    original_steps = list(arm.setup_steps)

    resolved = pilot_mod.resolve_setup_steps(arm, tmp_path)

    assert any(str(tmp_path) in line for line in resolved.setup_steps)
    assert arm.setup_steps == original_steps  # original untouched


def test_resolve_setup_steps_noop_without_token(tmp_path):
    arm = load_arm(ARMS_DIR / "vanilla.toml")

    resolved = pilot_mod.resolve_setup_steps(arm, tmp_path)

    assert resolved.setup_steps == arm.setup_steps


def test_resolve_setup_steps_rejects_bad_repo_root(tmp_path):
    arm = load_arm(ARMS_DIR / "add.toml")

    with pytest.raises(BenchError, match="invalid_repo_root"):
        pilot_mod.resolve_setup_steps(arm, pathlib.Path("/does/not/exist/definitely"))


@pytest.mark.slow
def test_add_arm_setup_succeeds_in_bare_sandbox(tmp_path):
    import shutil

    if shutil.which("uv") is None:
        pytest.skip("uv not found on PATH — loud skip, never a silent pass (M6)")

    from benchmark.runner.core import execute_wm

    arm = load_arm(ARMS_DIR / "add.toml")
    resolved = pilot_mod.resolve_setup_steps(arm, REPO_ROOT)

    agent_cmd = _fake_agent_ok(tmp_path)
    runs_root = tmp_path / "runs"
    record = execute_wm(resolved, 1, agent_cmd=agent_cmd, timeout_s=300.0, retries=0, runs_root=runs_root)

    transcript = (runs_root / "add" / "wm1" / "transcript.jsonl").read_text()
    setup_lines = [ln for ln in transcript.splitlines() if ln.startswith("setup:")]
    assert len(setup_lines) == 3
    for line in setup_lines:
        assert "exit 0" in line
    assert record.status != "failed" or "setup" not in record.artifacts.get("attempts", "")


# --------------------------------------------------------------------------
# M4, R3-R5 — attest_record
# --------------------------------------------------------------------------


def test_attest_then_report_drops_unaudited(tmp_path):
    from benchmark import report as report_mod

    runs_root = tmp_path / "runs"
    _seed_record(runs_root, "add", 1, metrics={
        "regression_rate": 0.0,
        "spec_fidelity": 0.82,
        "tokens_total": 100.0,
        "cost_usd": 0.1,
        "context_rot_slope": 0.0,
        "time_to_first_edit": 1.0,
    })

    before = report_mod.render_report(runs_root, arms=["add"], wms=[1])
    assert "(unaudited)" in before

    updated = pilot_mod.attest_record("add", 1, "matches PROMPT.md requirements", runs_root=runs_root)
    assert updated.artifacts["spec_fidelity_audit"] == "spot-checked: matches PROMPT.md requirements"

    after = report_mod.render_report(runs_root, arms=["add"], wms=[1])
    assert "(unaudited)" not in after
    assert "0.82" in after


def test_attest_record_not_found(tmp_path):
    runs_root = tmp_path / "runs"
    with pytest.raises(BenchError, match="record_not_found"):
        pilot_mod.attest_record("add", 2, "x", runs_root=runs_root)
    assert not (runs_root / "add" / "wm2" / "record.json").exists()


def test_attest_record_not_done(tmp_path):
    runs_root = tmp_path / "runs"
    _seed_record(runs_root, "add", 1, status="failed")
    record_path = runs_root / "add" / "wm1" / "record.json"
    before_bytes = record_path.read_bytes()

    with pytest.raises(BenchError, match="record_not_done"):
        pilot_mod.attest_record("add", 1, "x", runs_root=runs_root)

    assert record_path.read_bytes() == before_bytes


def test_attest_record_not_scored(tmp_path):
    runs_root = tmp_path / "runs"
    _seed_record(runs_root, "add", 1, status="done")  # spec_fidelity default 0.0 placeholder
    record_path = runs_root / "add" / "wm1" / "record.json"
    before_bytes = record_path.read_bytes()

    with pytest.raises(BenchError, match="record_not_scored"):
        pilot_mod.attest_record("add", 1, "x", runs_root=runs_root)

    assert record_path.read_bytes() == before_bytes


# --------------------------------------------------------------------------
# M7, M8, M9, R6 — run_pilot
# --------------------------------------------------------------------------


def test_run_pilot_halts_arm_on_non_done_wm(tmp_path, monkeypatch):
    runs_root = tmp_path / "runs"
    arms_dir = tmp_path / "arms"
    arms_dir.mkdir()
    for name in ("add", "vanilla"):
        (arms_dir / f"{name}.toml").write_text(
            f'name = "{name}"\n'
            "setup_steps = []\n"
            'prompt_wrapper = "raw"\n'
            'pin = ""\n'
            "same_model = true\n"
            "token_ceiling = 200000\n"
            "turn_ceiling = 60\n"
        )
    monkeypatch.setattr(pilot_mod, "ARMS_DIR", arms_dir)

    ok_agent = _fake_agent_ok(tmp_path, "fake_ok.py")
    fail_agent = _fake_agent_fail(tmp_path, "fake_fail.py")

    call_log: list[tuple[str, int]] = []
    real_execute_wm = pilot_mod.execute_wm

    def _fake_execute_wm(arm, wm, **kwargs):
        call_log.append((arm.name, wm))
        agent_cmd = fail_agent if (arm.name == "add" and wm == 3) else ok_agent
        kwargs = dict(kwargs)
        kwargs["agent_cmd"] = agent_cmd
        return real_execute_wm(arm, wm, **kwargs)

    monkeypatch.setattr(pilot_mod, "execute_wm", _fake_execute_wm)

    score_calls: list[tuple[str, int]] = []
    real_score_record = pilot_mod.score_record

    def _fake_score_record(arm_name, wm, **kwargs):
        score_calls.append((arm_name, wm))
        kwargs = dict(kwargs)
        kwargs["judge_cmd"] = _fake_judge(tmp_path)
        kwargs["runs_root"] = runs_root
        return real_score_record(arm_name, wm, **kwargs)

    monkeypatch.setattr(pilot_mod, "score_record", _fake_score_record)

    pilot_mod.run_pilot(
        arms=["add", "vanilla"],
        wms=(1, 2, 3),
        resume=False,
        runs_root=runs_root,
        repo_root=REPO_ROOT,
    )

    add_wm1 = validate_from(runs_root, "add", 1)
    add_wm2 = validate_from(runs_root, "add", 2)
    add_wm3 = validate_from(runs_root, "add", 3)
    assert add_wm1.status == "done"
    assert add_wm2.status == "done"
    assert add_wm3.status == "failed"

    for wm in (1, 2, 3):
        vanilla_record = validate_from(runs_root, "vanilla", wm)
        assert vanilla_record.status == "done"

    assert ("add", 3) not in score_calls
    assert ("add", 1) in score_calls
    assert ("add", 2) in score_calls
    for wm in (1, 2, 3):
        assert ("vanilla", wm) in score_calls


def validate_from(runs_root: pathlib.Path, arm: str, wm: int):
    from benchmark.schema.run_record import RunRecord

    path = runs_root / arm / f"wm{wm}" / "record.json"
    return RunRecord.from_json(path.read_text())


def test_run_pilot_resumes_without_reinvoking(tmp_path, monkeypatch):
    runs_root = tmp_path / "runs"
    arms_dir = tmp_path / "arms"
    arms_dir.mkdir()
    (arms_dir / "add.toml").write_text(
        'name = "add"\n'
        "setup_steps = []\n"
        'prompt_wrapper = "raw"\n'
        'pin = ""\n'
        "same_model = true\n"
        "token_ceiling = 200000\n"
        "turn_ceiling = 60\n"
    )
    monkeypatch.setattr(pilot_mod, "ARMS_DIR", arms_dir)

    for wm in (1, 2, 3, 4, 5, 6):
        _seed_record(
            runs_root,
            "add",
            wm,
            metrics={
                "regression_rate": 0.0 if wm != 3 else 0.1,
                "spec_fidelity": 0.8,
                "tokens_total": 10.0,
                "cost_usd": 0.01,
                "context_rot_slope": 0.0,
                "time_to_first_edit": 1.0,
            },
        )

    before_bytes = {
        wm: (runs_root / "add" / f"wm{wm}" / "record.json").read_bytes() for wm in (1, 2, 3, 4, 5)
    }

    def _boom_execute_wm(*args, **kwargs):
        raise AssertionError("execute_wm must not be invoked — all WMs already done")

    def _boom_score_record(*args, **kwargs):
        raise AssertionError("score_record must not be invoked — all WMs already scored")

    monkeypatch.setattr(pilot_mod, "execute_wm", _boom_execute_wm)
    monkeypatch.setattr(pilot_mod, "score_record", _boom_score_record)

    pilot_mod.run_pilot(arms=["add"], resume=True, runs_root=runs_root, repo_root=REPO_ROOT)

    for wm in (1, 2, 3):
        after = (runs_root / "add" / f"wm{wm}" / "record.json").read_bytes()
        assert after == before_bytes[wm]


def test_run_pilot_rejects_unknown_arm(tmp_path):
    runs_root = tmp_path / "runs"

    with pytest.raises(BenchError, match="unknown_arm"):
        pilot_mod.run_pilot(arms=["ghost"], runs_root=runs_root, repo_root=REPO_ROOT)

    assert not (runs_root / "ghost").exists()


# --------------------------------------------------------------------------
# CLI surface: `pilot.py attest` / `pilot.py run-all`
# --------------------------------------------------------------------------


def test_cli_attest_success_and_rejection(tmp_path, capsys):
    runs_root = tmp_path / "runs"
    _seed_record(
        runs_root,
        "add",
        1,
        metrics={
            "regression_rate": 0.0,
            "spec_fidelity": 0.9,
            "tokens_total": 10.0,
            "cost_usd": 0.01,
            "context_rot_slope": 0.0,
            "time_to_first_edit": 1.0,
        },
    )

    rc = pilot_mod.main(["attest", "--arm", "add", "--wm", "1", "--note", "x", "--runs-root", str(runs_root)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "spot-checked: x" in out

    rc2 = pilot_mod.main(
        ["attest", "--arm", "add", "--wm", "2", "--note", "x", "--runs-root", str(runs_root)]
    )
    assert rc2 == 2
    err = capsys.readouterr().err
    assert "record_not_found" in err


def test_cli_run_all_rejects_unknown_arm(tmp_path, capsys):
    runs_root = tmp_path / "runs"

    rc = pilot_mod.main(["run-all", "--arms", "ghost", "--runs-root", str(runs_root), "--repo-root", str(REPO_ROOT)])
    assert rc == 2
    err = capsys.readouterr().err
    assert "unknown_arm" in err


# --------------------------------------------------------------------------
# harness-multirep — aggregate_reps (pure) + run_reps (spy) + --reps CLI
# --------------------------------------------------------------------------


def _rec(arm: str, wm: int, *, tokens: float, cost: float, fidelity: float) -> "object":
    """Build a validated RunRecord with the given distribution metrics
    (the others are irrelevant to aggregate_reps and pinned to 0)."""
    return validate(
        dict(
            arm=arm,
            wm=wm,
            rep=0,
            status="done",
            metrics={
                "regression_rate": 0.0,
                "spec_fidelity": fidelity,
                "tokens_total": tokens,
                "cost_usd": cost,
                "context_rot_slope": 0.0,
                "time_to_first_edit": 0.0,
            },
            artifacts={"workspace": "w", "transcript": "t", "oracle_report": "o"},
        )
    )


def test_aggregate_reps_groups_by_arm_wm_with_mean_min_max():
    records = [
        _rec("add", 1, tokens=100.0, cost=1.0, fidelity=0.90),
        _rec("add", 1, tokens=200.0, cost=3.0, fidelity=0.96),
        _rec("spec-kit", 1, tokens=50.0, cost=0.5, fidelity=0.80),
    ]

    agg = pilot_mod.aggregate_reps(records)

    assert set(agg.keys()) == {("add", 1), ("spec-kit", 1)}

    add = agg[("add", 1)]
    assert add["n"] == 2
    assert add["tokens"] == {"mean": 150.0, "min": 100.0, "max": 200.0}
    assert add["cost"] == {"mean": 2.0, "min": 1.0, "max": 3.0}
    assert add["fidelity"] == {"mean": pytest.approx(0.93), "min": 0.90, "max": 0.96}

    sk = agg[("spec-kit", 1)]
    assert sk["n"] == 1
    assert sk["tokens"] == {"mean": 50.0, "min": 50.0, "max": 50.0}
    assert sk["cost"] == {"mean": 0.5, "min": 0.5, "max": 0.5}
    assert sk["fidelity"] == {"mean": 0.80, "min": 0.80, "max": 0.80}


def test_aggregate_reps_empty_is_empty_dict():
    assert pilot_mod.aggregate_reps([]) == {}


def test_run_reps_invokes_run_pilot_once_per_rep_with_distinct_roots(tmp_path, monkeypatch):
    runs_root = tmp_path / "runs"
    calls: list[dict] = []

    def _spy_run_pilot(arms, wms, **kwargs):
        calls.append({"arms": list(arms), "wms": tuple(wms), **kwargs})
        # each rep returns one synthetic record so run_reps can concatenate
        return [_rec("add", 1, tokens=float(len(calls)), cost=1.0, fidelity=0.9)]

    monkeypatch.setattr(pilot_mod, "run_pilot", _spy_run_pilot)

    records = pilot_mod.run_reps(
        arms=["add"],
        wms=(1,),
        reps=3,
        runs_root=runs_root,
        repo_root=REPO_ROOT,
    )

    assert len(calls) == 3
    # each rep runs into a DISTINCT rep{i} root, resume disabled (fresh each rep)
    roots = [pathlib.Path(c["runs_root"]) for c in calls]
    assert roots == [runs_root / "rep0", runs_root / "rep1", runs_root / "rep2"]
    assert all(c["resume"] is False for c in calls)
    # flat concatenation of every rep's records
    assert len(records) == 3


def test_run_reps_rejects_non_positive_reps(tmp_path):
    with pytest.raises(BenchError, match="invalid_reps"):
        pilot_mod.run_reps(arms=["add"], wms=(1,), reps=0, runs_root=tmp_path, repo_root=REPO_ROOT)


def test_cli_run_all_reps_routes_through_run_reps(tmp_path, monkeypatch, capsys):
    runs_root = tmp_path / "runs"
    seen: dict = {}

    def _spy_run_reps(arms, wms, reps, **kwargs):
        seen["reps"] = reps
        seen["arms"] = list(arms)
        return [_rec("add", 1, tokens=10.0, cost=1.0, fidelity=0.9)]

    monkeypatch.setattr(pilot_mod, "run_reps", _spy_run_reps)

    rc = pilot_mod.main(
        ["run-all", "--arms", "add", "--wms", "1", "--reps", "3",
         "--runs-root", str(runs_root), "--repo-root", str(REPO_ROOT)]
    )

    assert rc == 0
    assert seen["reps"] == 3
    out = capsys.readouterr().out
    assert "add" in out and "1" in out  # aggregate summary printed
