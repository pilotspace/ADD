"""Arm recipe loader — frozen shape per TASK.md §3 CONTRACT @ v1.

Stdlib only (tomllib, py3.11+). An arm recipe missing a required key, or a
competitor arm (gsd|spec-kit) missing `pin`, raises
BenchError("invalid_arm_recipe: <missing key>").
"""
from __future__ import annotations

import dataclasses
import pathlib
import tomllib

from benchmark.schema.run_record import BenchError

ARM_NAMES = ("add", "vanilla", "plan-mode", "gsd", "spec-kit")
PIN_REQUIRED_ARMS = frozenset({"gsd", "spec-kit"})
REQUIRED_KEYS = ("name", "setup_steps", "prompt_wrapper", "pin")
REQUIRED_FAIRNESS_KEYS = ("same_model", "token_ceiling", "turn_ceiling")


@dataclasses.dataclass(frozen=True)
class Arm:
    name: str
    setup_steps: list[str]
    prompt_wrapper: str
    pin: str
    same_model: bool
    token_ceiling: int
    turn_ceiling: int


def load_arm(path: pathlib.Path) -> Arm:
    path = pathlib.Path(path)
    if not path.exists():
        raise BenchError(f"invalid_arm_recipe: file not found {path}")

    with path.open("rb") as fh:
        data = tomllib.load(fh)

    name = data.get("name", path.stem)

    # `pin` is only hard-required for the two competitor arms (fairness/reproducibility);
    # first-party arms (add/vanilla/plan-mode) may leave it empty but the key must exist.
    required = list(REQUIRED_KEYS)
    missing = [k for k in required if k not in data]
    if missing:
        raise BenchError(f"invalid_arm_recipe: missing key(s) {missing} in {path.name}")

    if name in PIN_REQUIRED_ARMS and not data.get("pin"):
        raise BenchError(f"invalid_arm_recipe: missing key ['pin'] in {path.name}")

    missing_fairness = [k for k in REQUIRED_FAIRNESS_KEYS if k not in data]
    if missing_fairness:
        raise BenchError(f"invalid_arm_recipe: missing fairness key(s) {missing_fairness} in {path.name}")

    return Arm(
        name=name,
        setup_steps=list(data["setup_steps"]),
        prompt_wrapper=str(data["prompt_wrapper"]),
        pin=str(data.get("pin", "")),
        same_model=bool(data["same_model"]),
        token_ceiling=int(data["token_ceiling"]),
        turn_ceiling=int(data["turn_ceiling"]),
    )
