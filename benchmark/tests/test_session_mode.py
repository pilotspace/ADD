"""Behavioral proof of session-mode (context-rot-cross-milestones).

The fresh mode (default, unchanged) starts a NEW agent conversation per WM in
a NEW per-WM workspace seeded by copy — it measures the method with context
externalized. `session_mode="continue"` is the context-rot arm: ONE persistent
project workspace (`runs/<arm>/session/workspace`, never re-copied) and ONE
continuing conversation (`--continue` on the agent argv for wm>1), so the
context accumulated across milestones is exactly what gets measured.

Contract:
  - continue-mode shares a single workspace across WMs; nothing is seeded by
    copy (the project persists in place);
  - setup_steps run at WM1 ONLY (a re-run would clobber the continuing board);
  - the default `claude -p` argv gains `--continue` for wm>1 — never for wm1,
    never in fresh mode; an injected fake agent_cmd sees the flag too;
  - per-WM records still land at runs/<arm>/wm<k>/record.json (report
    machinery untouched) and stamp artifacts["session_mode"];
  - fresh mode is byte-for-byte the old behavior (default).

Run: python3 -m pytest benchmark/tests/test_session_mode.py
"""
from __future__ import annotations

import json
import pathlib
import sys

import pytest

BENCH = pathlib.Path(__file__).resolve().parents[1]
REPO = BENCH.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from benchmark.arms.loader import Arm                       # noqa: E402
from benchmark.runner.agent import build_argv, default_agent_cmd  # noqa: E402
from benchmark.runner.core import execute_wm                # noqa: E402

# a fake agent that "builds" by touching a file and emits a parseable result line
_FAKE_AGENT = [sys.executable, "-c",
               "import json,sys; print(json.dumps({'type':'result','total_cost_usd':0.0,"
               "'usage':{'input_tokens':1,'output_tokens':1}}))"]


def _arm(tmp_path: pathlib.Path) -> Arm:
    marker = tmp_path / "setup-ran.count"
    return Arm(name="vanilla", setup_steps=[
        f"{sys.executable} -c \"import pathlib;"
        f"p=pathlib.Path(r'{marker}');"
        f"p.write_text(str(int(p.read_text() or 0) + 1 if p.exists() else 1))\"",
    ], prompt_wrapper="raw", pin="test",
        same_model=True, token_ceiling=200000, turn_ceiling=60)


class TestArgvContinueFlag:
    def test_default_argv_gains_continue(self):
        argv = default_agent_cmd("do it", continue_session=True)
        assert "--continue" in argv

    def test_default_argv_fresh_has_no_continue(self):
        assert "--continue" not in default_agent_cmd("do it")

    def test_build_argv_injected_cmd_sees_flag(self):
        argv = build_argv("do it", ["fake"], continue_session=True)
        assert "--continue" in argv
        assert argv[-1] == "do it", "the prompt stays the final positional arg"

    def test_build_argv_default_is_unchanged(self):
        assert build_argv("do it", ["fake"]) == ["fake", "do it"]


class TestContinueModeWorkspace:
    def test_shared_workspace_and_single_setup(self, tmp_path):
        arm = _arm(tmp_path)
        runs = tmp_path / "runs"
        recs = [execute_wm(arm, wm, agent_cmd=_FAKE_AGENT, timeout_s=30.0,
                           runs_root=runs, session_mode="continue")
                for wm in (1, 2)]
        ws = {r.artifacts["workspace"] for r in recs}
        assert len(ws) == 1, "continue-mode must reuse ONE project workspace"
        assert ws == {str(runs / "vanilla" / "session" / "workspace")}
        marker = tmp_path / "setup-ran.count"
        assert marker.read_text() == "1", "setup_steps run at WM1 only"

    def test_records_still_per_wm(self, tmp_path):
        arm = _arm(tmp_path)
        runs = tmp_path / "runs"
        for wm in (1, 2):
            execute_wm(arm, wm, agent_cmd=_FAKE_AGENT, timeout_s=30.0,
                       runs_root=runs, session_mode="continue")
        for wm in (1, 2):
            rec = json.loads((runs / "vanilla" / f"wm{wm}" / "record.json").read_text())
            assert rec["wm"] == wm
            assert rec["artifacts"]["session_mode"] == "continue"

    def test_fresh_mode_unchanged(self, tmp_path):
        arm = _arm(tmp_path)
        runs = tmp_path / "runs"
        rec = execute_wm(arm, 1, agent_cmd=_FAKE_AGENT, timeout_s=30.0, runs_root=runs)
        assert rec.artifacts["workspace"] == str(runs / "vanilla" / "wm1" / "workspace")
        assert "session_mode" not in rec.artifacts, "fresh mode stays byte-identical"


class TestContinueFlagThreading:
    def test_wm1_never_continues_wm2_does(self, tmp_path, monkeypatch):
        import benchmark.runner.core as core
        seen: list[tuple[int, bool]] = []
        real = core.build_argv

        def spy(prompt, agent_cmd, continue_session=False):
            seen.append(continue_session)
            return real(prompt, agent_cmd, continue_session=continue_session)

        monkeypatch.setattr(core, "build_argv", spy)
        arm = _arm(tmp_path)
        runs = tmp_path / "runs"
        for wm in (1, 2):
            execute_wm(arm, wm, agent_cmd=_FAKE_AGENT, timeout_s=30.0,
                       runs_root=runs, session_mode="continue")
        assert seen == [False, True], "wm1 opens the session; wm2 continues it"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
