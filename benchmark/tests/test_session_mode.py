"""Behavioral proof of session-mode (persistent-workspace, fresh conversations).

The fresh mode (default, unchanged) starts a NEW agent conversation per WM in
a NEW per-WM workspace seeded by copy. `session_mode="continue"` persists the
PROJECT, never the conversation: ONE workspace
(`runs/<arm>/session/workspace`, never re-copied), setup at WM1 only, and a
FRESH conversation every milestone — the on-disk board is the only carrier
across milestones. (`--continue` was removed 2026-07-18 by user decision; the
conversation-carried variant lives on only in the archived
runs-session wm1–6 records and the 2026-07-add-2.0-remeasure report.)

Contract:
  - continue-mode shares a single workspace across WMs; nothing is seeded by
    copy (the project persists in place);
  - setup_steps run at WM1 ONLY (a re-run would clobber the continuing board);
  - the agent argv NEVER carries `--continue` — not in any mode, not at any
    WM; every milestone opens a fresh conversation;
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

# a fake agent that emits a parseable result line
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


class TestArgvNeverContinues:
    def test_default_argv_has_no_continue(self):
        assert "--continue" not in default_agent_cmd("do it")

    def test_injected_cmd_prompt_is_final_arg(self):
        assert build_argv("do it", ["fake"]) == ["fake", "do it"]

    def test_continue_mode_argv_is_fresh_every_wm(self, tmp_path, monkeypatch):
        # the mode persists the WORKSPACE, never the conversation — every
        # milestone's argv must be conversation-fresh
        import benchmark.runner.core as core
        seen: list[list[str]] = []
        real = core.build_argv

        def spy(prompt, agent_cmd):
            argv = real(prompt, agent_cmd)
            seen.append(argv)
            return argv

        monkeypatch.setattr(core, "build_argv", spy)
        arm = _arm(tmp_path)
        runs = tmp_path / "runs"
        for wm in (1, 2):
            execute_wm(arm, wm, agent_cmd=_FAKE_AGENT, timeout_s=30.0,
                       runs_root=runs, session_mode="continue")
        assert len(seen) == 2
        for argv in seen:
            assert "--continue" not in argv, "every milestone must open a fresh conversation"


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


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
