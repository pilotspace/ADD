"""meter — the content-derived version stamp for a scored record.

A scored number you cannot date is a number you cannot trust. The archived
campaigns hold records produced by at least three different meters (before the
reading-probe fixes, after them, and after `tests_weakened` learned to read
unittest assertions), and nothing on a record said which. Telling them apart
meant reading git history and matching dates by hand.

The stamp is an md5 over the CONTENT of the modules that decide a score, never
a hand-maintained constant: a version someone must remember to bump is the
`turn_ceiling` failure mode — declared in every arm, asserted equal by a test,
and read by nothing.

A missing module raises rather than hashing nothing, so renaming a scorer
fails loudly instead of quietly drifting the stamp toward a constant.
"""
from __future__ import annotations

import hashlib
import pathlib

BENCH_ROOT = pathlib.Path(__file__).resolve().parent

# Every file whose bytes can change a metric. Add here when a new scorer lands —
# the guard in test_meter_provenance.py proves the stamp actually moves.
METER_MODULES: tuple[str, ...] = (
    "score.py",
    "tamper.py",
    "ambiguity.py",
    "trust.py",
    "workload/_oracle_lib.py",
)


def meter_version() -> str:
    """12 hex chars identifying the scoring code that produced a record.

    Short enough for a table cell or a filename; long enough that a collision
    between two meters in one project is not a practical concern.
    """
    digest = hashlib.md5()
    for rel in METER_MODULES:
        path = BENCH_ROOT / rel
        digest.update(path.read_bytes())   # missing -> FileNotFoundError, loudly
    return digest.hexdigest()[:12]
