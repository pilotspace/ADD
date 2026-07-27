"""Every workload family on disk must be runnable from the CLI.

This is the `unknown_arm` defect again in a different costume. That one was a
second arm allowlist inside score.py that drifted from the loader's; 423 tests
were green and the new arm was still unrunnable, discovered only by paying for
a launch that immediately failed. `--family` has the identical shape: two
hardcoded `choices=("wm", "hv", "amb")` tuples, in pilot.py and report.py,
with nothing tying them to `benchmark/workload/`.

Porting the payments track as `pay1-4` made both stale again. Enumerating the
directories is the fix that holds for the NEXT track too.

Note this guard does not require the reverse — `hv` is a deliberately retained
choice for a workload pruned 2026-07-10 whose archive still scores through
`report --trust --family hv`, so an accepted family with no directory is fine.
"""
from __future__ import annotations

import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import pytest

BENCH = pathlib.Path(__file__).resolve().parents[1]
WORKLOAD = BENCH / "workload"


def _families_on_disk() -> set[str]:
    families = set()
    for path in WORKLOAD.iterdir():
        if not path.is_dir() or path.name.startswith(("_", ".")):
            continue
        match = re.fullmatch(r"([a-z]+)(\d+)", path.name)
        assert match, f"workload/{path.name} does not match <family><index>"
        families.add(match.group(1))
    assert families, "no workload families found — this guard would pass vacuously"
    return families


def _cli_choices(module_name: str) -> set[str]:
    src = (BENCH / module_name).read_text()
    match = re.search(r'--family".*?choices=\(([^)]*)\)', src, re.S)
    assert match, f"{module_name}: no --family choices tuple found"
    return set(re.findall(r'"([a-z]+)"', match.group(1)))


@pytest.mark.parametrize("module_name", ["pilot.py", "report.py"])
def test_every_workload_family_is_an_accepted_cli_choice(module_name):
    missing = _families_on_disk() - _cli_choices(module_name)
    assert not missing, (
        f"{module_name} cannot run workload families {sorted(missing)} — "
        "they exist on disk but are not in the --family choices tuple")


def test_both_cli_surfaces_accept_the_same_families():
    # A family runnable but not reportable is the same trap one step later.
    assert _cli_choices("pilot.py") == _cli_choices("report.py")
