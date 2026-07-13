"""run.py must resolve {REPO_ROOT} in arm setup_steps before execute_wm (todo #27).

The pilot path calls resolve_setup_steps; the thin run.py CLI bypassed it, so a
live `run --arm add --wm 1` executed the literal `uv pip install -e
{REPO_ROOT}/add-method` and every rep died at setup (observed 2026-07-13,
ceremony-to-effort WM1 re-measure rep 1 — cost $0, caught before agent spend).
"""
from unittest import mock

import benchmark.run as run_cli


def _invoke_run_capturing_arm(argv):
    captured = {}

    def _fake_execute_wm(arm, wm, **kwargs):
        captured["arm"] = arm
        raise SystemExit(0)  # stop before any workspace/agent work

    with mock.patch.object(run_cli, "execute_wm", _fake_execute_wm):
        try:
            run_cli.main(argv)
        except SystemExit:
            pass
    return captured["arm"]


def test_run_resolves_repo_root_token():
    arm = _invoke_run_capturing_arm(["run", "--arm", "add", "--wm", "1"])
    joined = "\n".join(arm.setup_steps)
    assert "{REPO_ROOT}" not in joined, (
        "run.py passed the arm to execute_wm with the {REPO_ROOT} placeholder "
        "unresolved — the setup step is unrunnable"
    )
    assert "add-method" in joined  # the resolved path still points at the engine


def test_resume_resolves_repo_root_token():
    with mock.patch.object(run_cli, "find_resume_point", return_value=1):
        arm = _invoke_run_capturing_arm(["resume", "--arm", "add"])
    assert "{REPO_ROOT}" not in "\n".join(arm.setup_steps)
