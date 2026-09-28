import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def _no_live_agent(monkeypatch):
    """No test may reach the REAL `claude -p` fallback — it spends money.

    `execute_wm` falls back to the live agent argv whenever `agent_cmd` is None. On
    2026-09-28 a refusal test written red-first (the refusal did not exist yet) passed no
    agent_cmd, so `run_pilot` fell through and ran `vanilla` WM1-WM3 live (~$0.9) before it
    was killed. A per-module grep for the literal binary cannot see that path; this can.
    Tests that inspect the argv itself call `benchmark.runner.agent` directly, untouched.
    """
    from benchmark.runner import core

    real = core.build_argv

    def guarded(prompt, agent_cmd):
        if not agent_cmd:
            raise RuntimeError("test reached the live `claude -p` fallback — inject agent_cmd")
        return real(prompt, agent_cmd)

    monkeypatch.setattr(core, "build_argv", guarded)
