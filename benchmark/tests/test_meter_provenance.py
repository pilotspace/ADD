"""A scored number you cannot date is a number you cannot trust.

The archived campaigns hold records produced by at least three different
meters: before the reading-probe fixes, after them, and after
`tests_weakened` learned to read unittest assertions. Nothing on a record says
which. Comparing two of them is comparing two instruments, and the only way to
tell was to read git history and match dates by hand.

The stamp is derived from the CONTENT of the scoring modules rather than
hand-maintained, because a version someone must remember to bump is the
`turn_ceiling` failure mode: declared in every arm, asserted equal by a test,
read by nothing.
"""
from __future__ import annotations

import hashlib
import pathlib
import shutil
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import pytest

from benchmark.meter import METER_MODULES, meter_version

BENCH = pathlib.Path(__file__).resolve().parents[1]


class TestTheStamp:
    def test_meter_version_is_stable_across_calls(self):
        assert meter_version() == meter_version()

    def test_meter_version_is_short_and_hex(self):
        v = meter_version()
        assert len(v) == 12 and all(c in "0123456789abcdef" for c in v), v

    def test_meter_version_tracks_module_content(self, tmp_path):
        # Hash the same module set from a mutated copy: the stamp must move.
        def digest(root: pathlib.Path) -> str:
            h = hashlib.md5()
            for rel in METER_MODULES:
                h.update((root / rel).read_bytes())
            return h.hexdigest()[:12]

        copy = tmp_path / "bench"
        shutil.copytree(BENCH, copy, ignore=shutil.ignore_patterns(
            "runs*", "__pycache__", ".pytest_cache"))
        before = digest(copy)
        assert before == meter_version(), "copy should reproduce the live stamp"

        target = copy / METER_MODULES[0]
        target.write_text(target.read_text() + "\n# scorer changed\n")
        assert digest(copy) != before, "editing a scoring module left the stamp unchanged"

    def test_missing_module_fails_loud(self, monkeypatch):
        # Hashing a set that silently skips absentees would drift toward a
        # meaningless constant as modules are renamed.
        monkeypatch.setattr("benchmark.meter.METER_MODULES", ("does_not_exist.py",))
        with pytest.raises(Exception):
            meter_version()


class TestTheRecordCarriesIt:
    def test_scored_record_carries_the_stamp(self):
        import inspect

        from benchmark import score

        src = inspect.getsource(score.score_record)
        assert "meter_version" in src, (
            "score_record does not stamp the record — provenance that depends on a "
            "caller remembering is not provenance")

    def test_validate_accepts_the_extra_artifact_key(self):
        from benchmark.schema.run_record import validate

        record = {
            "arm": "add", "wm": 1, "rep": 0, "status": "done",
            "metrics": {
                "requirement_coverage": 1.0, "oracle_pass_rate": 1.0,
                "regression_rate": 0.0, "cost_usd": 1.0, "tokens_total": 1.0,
                "time_to_first_edit": 1.0, "context_rot_slope": 0.0,
            },
            "artifacts": {
                "workspace": "w", "transcript": "t", "oracle_report": "o",
                "meter_version": meter_version(),
            },
        }
        assert validate(record).artifacts["meter_version"] == meter_version()
