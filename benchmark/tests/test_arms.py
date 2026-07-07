"""Scenarios: five valid arm recipes / reject unpinned competitor arm (M3, R:invalid_arm_recipe)."""
import pathlib
import shutil
import tempfile

import pytest

from benchmark.schema.run_record import BenchError
from benchmark.arms.loader import ARM_NAMES, load_arm

ROOT = pathlib.Path(__file__).resolve().parents[1]
ARMS_DIR = ROOT / "arms"


def test_five_arms_validate_with_fairness_parity():
    arms = [load_arm(ARMS_DIR / f"{name}.toml") for name in ARM_NAMES]
    assert len(arms) == 5
    fairness = {(a.same_model, a.token_ceiling, a.turn_ceiling) for a in arms}
    assert len(fairness) == 1, f"fairness fields diverge across arms: {fairness}"
    for a in arms:
        assert a.same_model is True
        if a.name in ("gsd", "spec-kit"):
            assert a.pin, f"{a.name} missing pin"


def test_unpinned_arm_rejected(tmp_path):
    src = ARMS_DIR / "gsd.toml"
    text = src.read_text()
    lines = [ln for ln in text.splitlines() if not ln.strip().startswith("pin")]
    broken = tmp_path / "gsd.toml"
    broken.write_text("\n".join(lines))

    with pytest.raises(BenchError) as exc_info:
        load_arm(broken)
    assert "invalid_arm_recipe" in str(exc_info.value)
    assert "pin" in str(exc_info.value)

    # other arms still validate
    for name in ARM_NAMES:
        if name == "gsd":
            continue
        load_arm(ARMS_DIR / f"{name}.toml")
