"""Red/green test for harness-workspace-isolation (orientation-honesty, frozen §3 v1).

The WM runner must scope the agent's root-walk to its workspace by exporting
`ADD_ROOT_CEILING=<workspace_dir>` into the agent subprocess env — so a workspace
nested under an ancestor `.add/` resolves its own project, not the parent. A fake
agent records the env value it saw; the runner behaviour is otherwise unchanged.

Run: python3 -m pytest benchmark/tests/test_workspace_isolation.py -q
"""
import pathlib
import sys
import textwrap

from benchmark.arms.loader import Arm
from benchmark.runner.core import execute_wm


def _arm(name: str = "fake-arm") -> Arm:
    return Arm(
        name=name,
        setup_steps=[],
        prompt_wrapper="raw",
        pin="",
        same_model=True,
        token_ceiling=200000,
        turn_ceiling=60,
    )


def _write_script(tmp_path: pathlib.Path, name: str, body: str) -> pathlib.Path:
    script = tmp_path / name
    script.write_text(textwrap.dedent(body))
    script.chmod(0o755)
    return script


def test_runner_scopes_root_ceiling_to_workspace(tmp_path):
    # the fake agent runs with cwd == workspace and records what ADD_ROOT_CEILING it saw
    script = _write_script(
        tmp_path,
        "fake_env.py",
        """
        #!/usr/bin/env python3
        import json, os, pathlib, sys
        pathlib.Path("ceiling_seen.txt").write_text(
            os.environ.get("ADD_ROOT_CEILING", "<UNSET>"))
        print(json.dumps({"type": "tool_use", "name": "Write"}))
        print(json.dumps({
            "type": "result", "total_cost_usd": 0.0,
            "usage": {"input_tokens": 1, "output_tokens": 1,
                      "cache_creation_input_tokens": 0, "cache_read_input_tokens": 0},
        }))
        sys.exit(0)
        """,
    )
    runs_root = tmp_path / "runs"
    record = execute_wm(
        _arm(), 1,
        agent_cmd=[sys.executable, str(script)],
        timeout_s=10, retries=1, runs_root=runs_root,
    )
    assert record.status == "done"
    workspace = runs_root / "fake-arm" / "wm1" / "workspace"
    seen = (workspace / "ceiling_seen.txt").read_text().strip()
    assert seen != "<UNSET>", "runner must export ADD_ROOT_CEILING into the agent env"
    assert pathlib.Path(seen).resolve() == workspace.resolve(), (
        f"ceiling must equal the workspace dir; saw {seen!r}")
