"""bench-carry-forward: WM(k) workspace seeded from WM(k-1).

WM2/WM3 prompts assume the prior milestone's app exists; the harness gave every
WM a fresh dir (A4 delta, confirmed by the enforced rerun: the add agent
honestly refused an empty wm3). Seeding makes the benchmark truly longitudinal.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

from benchmark.runner.core import _seed_from_prior  # noqa: E402


def _mk_prior(root: pathlib.Path, arm: str, wm: int) -> pathlib.Path:
    ws = root / arm / f"wm{wm}" / "workspace"
    (ws / "app").mkdir(parents=True)
    (ws / "app" / "main.py").write_text("print('wm app')\n")
    (ws / ".venv" / "bin").mkdir(parents=True)
    (ws / ".venv" / "bin" / "python").write_text("fake\n")
    return ws


class TestSeedFromPrior:
    def test_seeds_app_excludes_venv(self, tmp_path):
        _mk_prior(tmp_path, "add", 1)
        target = tmp_path / "add" / "wm2" / "workspace"
        target.mkdir(parents=True)
        note = _seed_from_prior(target, "add", 2, tmp_path)
        assert (target / "app" / "main.py").read_text() == "print('wm app')\n"
        assert not (target / ".venv").exists()
        assert note is not None and "seeded" in note

    def test_wm1_never_seeds(self, tmp_path):
        target = tmp_path / "add" / "wm1" / "workspace"
        target.mkdir(parents=True)
        assert _seed_from_prior(target, "add", 1, tmp_path) is None
        assert list(target.iterdir()) == []

    def test_non_empty_workspace_untouched(self, tmp_path):
        _mk_prior(tmp_path, "add", 1)
        target = tmp_path / "add" / "wm2" / "workspace"
        target.mkdir(parents=True)
        (target / "existing.txt").write_text("resume state\n")
        assert _seed_from_prior(target, "add", 2, tmp_path) is None
        assert not (target / "app").exists()

    def test_missing_prior_notes_unseeded(self, tmp_path):
        target = tmp_path / "add" / "wm3" / "workspace"
        target.mkdir(parents=True)
        note = _seed_from_prior(target, "add", 3, tmp_path)
        assert note is not None and "unseeded" in note
        assert list(target.iterdir()) == []


class TestWiredIntoExecute:
    def test_execute_wm_calls_seeder(self):
        src = pathlib.Path(
            pathlib.Path(__file__).resolve().parents[1] / "runner" / "core.py"
        ).read_text()
        after_mkdir = src.split("workspace_dir.mkdir(parents=True, exist_ok=True)", 1)[1]
        assert "_seed_from_prior" in after_mkdir.split("def ", 1)[0]
