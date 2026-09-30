import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def _no_live_agent(monkeypatch):
    """No test may start the REAL `claude` binary — it spends money.

    `execute_wm` falls back to the live agent argv whenever `agent_cmd` is None. On
    2026-09-28 a refusal test written red-first (the refusal did not exist yet) passed no
    agent_cmd, so `run_pilot` fell through and ran `vanilla` WM1-WM3 live (~$0.9) before it
    was killed. A per-module grep for the literal binary cannot see that path; this can.
    The guard sits at process launch, so it holds however the argv was built, and a test that
    replaces the launcher itself (`_invoke_once`) may drive `execute_wm` without an agent.
    Tests that inspect the argv itself call `benchmark.runner.agent` directly, untouched.
    """
    import subprocess

    real = subprocess.Popen

    def guarded(args, *a, **kw):
        first = args[0] if isinstance(args, (list, tuple)) and args else str(args).split(" ", 1)[0]
        if pathlib.Path(str(first)).name == "claude":
            raise RuntimeError("test reached the live `claude` agent — inject agent_cmd")
        return real(args, *a, **kw)

    monkeypatch.setattr(subprocess, "Popen", guarded)
