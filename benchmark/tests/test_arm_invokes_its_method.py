"""An arm that installs a method's scaffolding must invoke that method.

THE DEFECT THIS CATCHES. `benchmark/arms/spec-kit.toml` ran
`specify init --here --force` and then handed the agent the bare prompt
(`prompt_wrapper = "raw"`). Across every automated campaign it produced ZERO
`specs/` artifacts — no spec, no plan, no tasks. Worse, `specify init` without
`--integration` "default[s] to Copilot in non-interactive sessions", so the
slash commands landed in `.github/prompts/` where the runner's agent never
looks. The arm had no path to its own method at all, and `gsd` carries the
identical shape.

493 tests were green throughout, because nothing compared an arm's setup
against its wrapper. `test_arms.py` checks pins and fairness fields; it never
asks whether an arm does the thing its name claims. Every comparative number
this benchmark published was therefore "ADD vs a competent agent with no
method", labelled as a method.

The guard enumerates `arms/*.toml` rather than naming arms, so an arm added
later is covered the day it lands — the same enumerative shape that caught the
collection-shape defect in the ported payments track.
"""
from __future__ import annotations

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))

import tomllib

import pytest

from benchmark.runner.core import _wrap_prompt

ARMS_DIR = pathlib.Path(__file__).resolve().parents[1] / "arms"


def _load(path: pathlib.Path) -> dict:
    return tomllib.loads(path.read_text())


def _arm_files() -> list[pathlib.Path]:
    files = sorted(ARMS_DIR.glob("*.toml"))
    assert files, "no arm TOMLs found — this guard would pass vacuously"
    return files


def _offenders(arms: list[tuple[str, dict]]) -> list[str]:
    """Arms that install scaffolding, never invoke it, and never say so."""
    bad = []
    for name, data in arms:
        if not data.get("setup_steps"):
            continue                                  # nothing installed
        if data.get("prompt_wrapper", "raw") != "raw":
            continue                                  # a wrapper drives it
        if data.get("scaffold_only"):
            continue                                  # declared, checked below
        bad.append(name)
    return bad


@pytest.mark.parametrize("path", _arm_files(), ids=lambda p: p.stem)
def test_every_arm_that_installs_scaffolding_invokes_it(path):
    data = _load(path)
    assert not _offenders([(path.stem, data)]), (
        f"silent_method_arm: {path.stem} installs scaffolding but is handed the raw "
        "prompt and declares no scaffold_only — it cannot exercise the method its "
        "name implies")


@pytest.mark.parametrize("path", _arm_files(), ids=lambda p: p.stem)
def test_scaffold_only_requires_a_reason(path):
    data = _load(path)
    if not data.get("scaffold_only"):
        return
    reason = (data.get("scaffold_only_reason") or "").strip()
    assert len(reason) > 20, (
        f"unexplained_scaffold_only: {path.stem} opts out of invoking its method "
        "without stating why — the escape hatch must cost a sentence")


def test_guard_enumerates_disk_not_a_hardcoded_list(tmp_path):
    # A new arm dropped in must be covered without editing this file.
    newcomer = tmp_path / "newcomer.toml"
    newcomer.write_text(
        'name = "newcomer"\nsetup_steps = ["npx some-method init"]\n'
        'prompt_wrapper = "raw"\npin = "some-method@1"\n')
    assert _offenders([("newcomer", _load(newcomer))]) == ["newcomer"]


def test_a_wrapped_arm_is_not_an_offender(tmp_path):
    ok = tmp_path / "ok.toml"
    ok.write_text('name = "ok"\nsetup_steps = ["x init"]\nprompt_wrapper = "add-loop"\n')
    assert _offenders([("ok", _load(ok))]) == []


def test_vanilla_needs_no_declaration():
    # setup_steps == [] is scaffolding-free: the honest raw control stays raw.
    data = _load(ARMS_DIR / "vanilla.toml")
    assert data["setup_steps"] == []
    assert _offenders([("vanilla", data)]) == []


class TestSpecKitActuallyRunsSpecKit:
    def test_installs_the_claude_integration(self):
        data = _load(ARMS_DIR / "spec-kit.toml")
        setup = " ".join(data["setup_steps"])
        assert "--integration claude" in setup, (
            "specify init defaults to Copilot in non-interactive sessions, so its "
            "commands land in .github/prompts/ where the runner's agent never reads them")

    def test_wrapper_drives_the_documented_cycle(self):
        data = _load(ARMS_DIR / "spec-kit.toml")
        assert data["prompt_wrapper"] == "spec-kit"
        wrapped = _wrap_prompt("BUILD THE THING", "spec-kit").lower()
        for step in ("specify", "plan", "tasks", "implement"):
            assert step in wrapped, f"the spec-kit wrapper never names '{step}'"

    def test_wrapper_still_carries_the_workload_prompt(self):
        # A wrapper that drops the prompt would score the arm on nothing.
        assert "BUILD THE THING" in _wrap_prompt("BUILD THE THING", "spec-kit")


def test_existing_arms_still_load():
    from benchmark.arms.loader import load_arm

    for path in _arm_files():
        arm = load_arm(path)
        assert arm.name, path
