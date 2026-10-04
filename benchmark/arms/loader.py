"""Arm recipe loader — frozen shape per TASK.md §3 CONTRACT @ v1.

Stdlib only (tomllib, py3.11+). An arm recipe missing a required key, or a
competitor arm (gsd|spec-kit) missing `pin`, raises
BenchError("invalid_arm_recipe: <missing key>").
"""
from __future__ import annotations

import dataclasses
import pathlib
import tomllib

from benchmark.runner.agent import EFFORT_LEVELS
from benchmark.schema.run_record import BenchError

# add-main: the MAIN-branch control arm (v2-wv1-longitudinal M5 @v2) — first-party,
# SHA-pinned via its toml so branch-engine changes are controlled against the release.
# add-4 / add-3x: the ADD 4.0 (this worktree, skill-only) vs ADD 3.7.0 (pinned engine)
# head-to-head. `add` stays listed so its archived records still score and report, but
# it is RETIRED (`retired =` in add.toml): run paths refuse it before any workspace.
ARM_NAMES = ("add", "add-main", "add-3x", "add-4", "add-4-lean", "add-4-low", "add-4-audited-low", "add-4-probe-low", "vanilla", "vanilla-low", "plan-mode",
             "gsd", "spec-kit")
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
    # OPTIONAL. Non-empty = the arm may no longer be RUN (it still loads, scores and
    # reports); the text says why and which arm replaces it. See `refuse_retired`.
    retired: str = ""
    # OPTIONAL. The main model this arm runs on, and the advisor it may consult (`--advisor`);
    # empty `model` = the run's `--model`, else the pinned meter model (runner/agent.py).
    model: str = ""
    advisor: str = ""
    # OPTIONAL. The `--effort` this arm runs at; empty = the run's `--effort`, else medium.
    effort: str = ""


def refuse_retired(arm: Arm) -> None:
    """Raise BenchError("retired_arm: ...") for an arm that must not be run any more.

    Called by every run path BEFORE a workspace exists, so a retired recipe fails loud and
    free instead of spending a setup (or an agent) on an installer it no longer matches."""
    if arm.retired:
        raise BenchError(f"retired_arm: {arm.name!r} — {arm.retired}")


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

    effort = str(data.get("effort", ""))
    if effort and effort not in EFFORT_LEVELS:
        raise BenchError(f"invalid_arm_recipe: effort {effort!r} not one of {list(EFFORT_LEVELS)} in {path.name}")

    return Arm(
        name=name,
        setup_steps=list(data["setup_steps"]),
        prompt_wrapper=str(data["prompt_wrapper"]),
        pin=str(data.get("pin", "")),
        same_model=bool(data["same_model"]),
        token_ceiling=int(data["token_ceiling"]),
        turn_ceiling=int(data["turn_ceiling"]),
        retired=str(data.get("retired", "")),
        model=str(data.get("model", "")),
        advisor=str(data.get("advisor", "")),
        effort=effort,
    )
