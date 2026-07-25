"""A probe must find its subject INSIDE the workspace under test.

Born from a real contamination: a benchmark run left `pip install -e .` of its own
workspace in the machine's global site-packages, so `python -m app.cli list` resolved
to a PREVIOUS RUN's app for every subsequent run. `R-cli-parity` then returned
covered=True on a completely empty workspace, inflating `requirement_coverage` by
1/12 for every run scored on that machine — and asymmetrically, since the leaked
workspace belonged to one arm.

The isolated_workspace copy could not catch this: an editable install is on sys.path
for every Python process on the machine, so there is nothing to copy away from. The
only durable defence is provenance — the probe proves the entry point it ran lives
under `ws` before it is allowed to score.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from benchmark.workload.wm1.checklist import _p_cli_parity


def _leak(tmp_path: pathlib.Path) -> pathlib.Path:
    """A CLI that exits 0, importable from OUTSIDE the workspace under test."""
    pkg = tmp_path / "leak" / "app"
    pkg.mkdir(parents=True)
    (pkg / "__init__.py").write_text("", encoding="utf-8")
    (pkg / "cli.py").write_text("import sys; print('[]'); sys.exit(0)\n", encoding="utf-8")
    return tmp_path / "leak"


class TestProbeProvenance:
    def test_empty_workspace_scores_false_despite_an_importable_app(self, tmp_path,
                                                                   monkeypatch):
        # THE REGRESSION. An empty workspace built nothing, so it satisfies nothing —
        # no state of the surrounding machine may change that verdict.
        ws = tmp_path / "ws"
        ws.mkdir()
        monkeypatch.setenv("PYTHONPATH", str(_leak(tmp_path)))
        assert _p_cli_parity("http://127.0.0.1:1", ws) is False, \
            "probe scored an empty workspace — a leaked install can satisfy it"

    def test_workspace_owned_cli_still_scores_true(self, tmp_path, monkeypatch):
        # The guard must not cost the probe its real signal: an app that genuinely
        # ships the CLI in its own workspace still scores, leak present or not.
        ws = tmp_path / "ws"
        pkg = ws / "app"
        pkg.mkdir(parents=True)
        (pkg / "__init__.py").write_text("", encoding="utf-8")
        (pkg / "cli.py").write_text("import sys; print('[]'); sys.exit(0)\n", encoding="utf-8")
        monkeypatch.setenv("PYTHONPATH", str(_leak(tmp_path)))
        assert _p_cli_parity("http://127.0.0.1:1", ws) is True, \
            "provenance guard rejected a CLI the workspace really owns"
