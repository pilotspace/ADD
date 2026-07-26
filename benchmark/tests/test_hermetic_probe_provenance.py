"""A probe must find its subject INSIDE the workspace under test.

Born from a real contamination: a benchmark run left `pip install -e .` of its own
workspace in the machine's global site-packages, so `python -m app.cli list` resolved
to a PREVIOUS RUN's app for every subsequent run. `R-cli-parity` then returned
covered=True on a completely empty workspace, inflating `requirement_coverage` by
1/12 for every run scored on that machine — and asymmetrically, since the leaked
workspace belonged to one arm.

The repo had ALREADY diagnosed and cured this class on 2026-07-18: `running_app`
boots the app under `-E -s -S`, the bare declared runtime. `_p_cli_parity` spawns its
own subprocess and never got the same flags, so it stayed the single path that
bypassed the fix. These tests pin BOTH layers, because the first version of this file
pinned only the second and was quietly vacuous:

  1. the bare-runtime flags — the real cure, and the repo's own idiom
  2. the entry-point provenance check — belt to those braces

NOTE ON TEST DESIGN: a PYTHONPATH-based leak is invisible once `-E` is set, so a test
that plants a leak that way and then calls the probe would pass even with every guard
removed. Each test below either exercises a guard directly or plants the leak through
a channel the guard under test can actually see.
"""
from __future__ import annotations

import os
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from benchmark.workload.wm1 import checklist
from benchmark.workload.wm1.checklist import _BARE, _entry_exists, _p_cli_parity


def _write_cli(root: pathlib.Path) -> None:
    pkg = root / "app"
    pkg.mkdir(parents=True, exist_ok=True)
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "cli.py").write_text("import sys; print('[]'); sys.exit(0)\n", encoding="utf-8")


class TestBareRuntime:
    """Layer 1 — the cure `running_app` already uses, applied to the CLI probe."""

    def test_probe_spawns_under_the_bare_runtime(self):
        # The flags ARE the fix; if they are ever dropped the leak returns silently,
        # so pin them rather than trusting the comment above them.
        assert _BARE == ("-E", "-s", "-S")

    def test_bare_runtime_blocks_a_foreign_app(self, tmp_path):
        # The property, proven end-to-end: an app importable from OUTSIDE the
        # workspace cannot satisfy the probe. This is the mechanism that made the
        # empty-workspace pass possible in the first place.
        _write_cli(tmp_path / "leak")
        ws = tmp_path / "ws"
        ws.mkdir()
        env = {**os.environ, "PYTHONPATH": str(tmp_path / "leak")}
        rc = subprocess.run([sys.executable, *_BARE, "-m", "app.cli", "list"],
                            cwd=ws, env=env, capture_output=True, text=True).returncode
        assert rc != 0, "bare runtime let a foreign app satisfy an empty workspace"

    def test_probe_matches_running_app_isolation(self):
        # Both spawn paths must agree. They drifted once, and that drift IS the bug:
        # the app boot was hardened and the CLI probe was not.
        lib = (pathlib.Path(checklist.__file__).parents[1] / "_oracle_lib.py"
               ).read_text(encoding="utf-8")
        assert '"-E", "-s", "-S"' in lib, \
            "running_app no longer uses the bare runtime — the two spawn paths drifted"


class TestProbeProvenance:
    """Layer 2 — exercised DIRECTLY, so these cannot pass with the guard removed."""

    def test_empty_workspace_owns_no_entry_point(self, tmp_path):
        ws = tmp_path / "ws"
        ws.mkdir()
        for module in ("app.cli", "cli", "app.__main__"):
            assert _entry_exists(ws, module) is False, f"{module} claimed by an empty ws"

    def test_every_legitimate_cli_shape_is_recognised(self, tmp_path):
        # The guard must not cost the probe its real signal. These are the four
        # shapes the invocation table actually supports.
        shapes = {
            "app/cli.py": "app.cli",
            "app/cli/__init__.py": "app.cli",
            "cli.py": "cli",
            "app/__main__.py": "app.__main__",
        }
        for rel, module in shapes.items():
            ws = tmp_path / rel.replace("/", "_")
            f = ws / rel
            f.parent.mkdir(parents=True, exist_ok=True)
            f.write_text("", encoding="utf-8")
            assert _entry_exists(ws, module) is True, f"guard rejected {rel}"

    def test_empty_workspace_never_scores(self, tmp_path):
        # THE REGRESSION, stated as the property that actually matters: an empty
        # workspace built nothing, so it satisfies nothing.
        ws = tmp_path / "ws"
        ws.mkdir()
        assert _p_cli_parity("http://127.0.0.1:1", ws) is False

    def test_workspace_owned_cli_still_scores(self, tmp_path):
        ws = tmp_path / "ws"
        _write_cli(ws)
        assert _p_cli_parity("http://127.0.0.1:1", ws) is True, \
            "guard rejected a CLI the workspace really owns"
