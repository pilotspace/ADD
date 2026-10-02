"""Each arm runs on its own model and advisor (.add/tasks/bench-model-switch.md)."""
import dataclasses
import difflib
import pathlib
import subprocess

import pytest

from benchmark import pilot
from benchmark.arms.loader import ARM_NAMES, Arm, load_arm
from benchmark.runner import agent, core

ROOT = pathlib.Path(__file__).resolve().parents[1]
ARMS_DIR = ROOT / "arms"
SHIPPED = ROOT.parent / "add-method" / "skill" / "add" / "SKILL.md"
VARIANT = ARMS_DIR / "variants" / "add-4-lean" / "SKILL.md"
SONNET55, HAIKU = "claude-sonnet-5-5", "claude-haiku-4-5-20251001"


def _arm(**over) -> Arm:
    base = Arm(name="vanilla", setup_steps=[], prompt_wrapper="raw", pin="", same_model=True,
               token_ceiling=200000, turn_ceiling=60)
    return dataclasses.replace(base, **over)


def test_arm_toml_model_and_advisor_default_empty(tmp_path):
    vanilla = load_arm(ARMS_DIR / "vanilla.toml")
    assert vanilla.model == "" and vanilla.advisor == ""
    toml = (ARMS_DIR / "vanilla.toml").read_text() + '\nmodel = "m-x"\nadvisor = "a-y"\n'
    (tmp_path / "vanilla.toml").write_text(toml)
    arm = load_arm(tmp_path / "vanilla.toml")
    assert (arm.model, arm.advisor) == ("m-x", "a-y")


def test_resolved_model_prefers_arm_then_flag_then_pin():
    assert agent.resolve_model("", None) == agent.PINNED_MODEL == "claude-sonnet-5"
    assert agent.resolve_model("", SONNET55) == SONNET55
    assert agent.resolve_model(HAIKU, SONNET55) == HAIKU


def test_argv_carries_model_effort_and_advisor_only_when_set():
    plain = agent.build_argv("p", None)
    assert plain[plain.index("--model") + 1] == "claude-sonnet-5"
    assert plain[plain.index("--effort") + 1] == "medium"
    assert "--advisor" not in plain
    switched = agent.build_argv("p", None, model=HAIKU, advisor=SONNET55)
    assert switched[switched.index("--model") + 1] == HAIKU
    assert switched[switched.index("--advisor") + 1] == SONNET55
    assert switched[switched.index("--effort") + 1] == "medium"
    fake = agent.build_argv("p", ["python3", "fake.py"], model=HAIKU, advisor=SONNET55)
    assert fake == ["python3", "fake.py", "p"], "an injected fake agent must stay untouched"


def test_execute_wm_passes_and_records_the_resolved_model(tmp_path, monkeypatch):
    seen = []

    def fake_invoke(argv, **kwargs):
        seen.append(list(argv))
        return "failed", [], 0.0

    monkeypatch.setattr(core, "_invoke_once", fake_invoke)
    rec = core.execute_wm(_arm(model=HAIKU, advisor=SONNET55), 1, runs_root=tmp_path, retries=0)
    assert seen and seen[0][seen[0].index("--model") + 1] == HAIKU
    assert seen[0][seen[0].index("--advisor") + 1] == SONNET55
    assert rec.artifacts["model"] == HAIKU and rec.artifacts["advisor"] == SONNET55

    seen.clear()
    rec = core.execute_wm(_arm(name="add-4"), 1, runs_root=tmp_path / "b", retries=0, model=SONNET55)
    assert seen[0][seen[0].index("--model") + 1] == SONNET55
    assert rec.artifacts["model"] == SONNET55 and "advisor" not in rec.artifacts


def test_run_all_cli_accepts_model(monkeypatch):
    got = {}
    monkeypatch.setattr(pilot, "run_reps", lambda **kw: got.update(kw) or [])
    pilot.main(["run-all", "--arms", "vanilla", "--wms", "1", "--reps", "2", "--model", SONNET55])
    assert got.get("model") == SONNET55


def test_lean_arm_loads_and_advisor_arm_retired():
    # .add/tasks/bench-sonnet-only.md M1: the Haiku-main advisor arm retires after round 6
    assert "add-4-lean" in ARM_NAMES and "add-4-advisor" not in ARM_NAMES and len(ARM_NAMES) == 12
    assert not (ARMS_DIR / "add-4-advisor.toml").exists()
    lean, base = (load_arm(ARMS_DIR / f"{n}.toml") for n in ("add-4-lean", "add-4"))
    for arm in (lean,):
        assert [s for s in arm.setup_steps if s in base.setup_steps] == base.setup_steps, \
            f"{arm.name} must run every add-4 step, in order"
        cp = [i for i, s in enumerate(arm.setup_steps)
              if "variants/add-4-lean/SKILL.md" in s and ".claude/skills/add/SKILL.md" in s]
        assert cp, f"{arm.name} does not install the lean variant"
        installed = arm.setup_steps.index(base.setup_steps[2])
        baseline = arm.setup_steps.index(base.setup_steps[-1])
        assert installed < cp[0] < baseline, \
            f"{arm.name} must overwrite the skill after install and before the workspace's baseline commit"
    assert lean.model == "" and lean.advisor == "", "the lean arm must take the run's --model"


def test_lean_variant_changes_exactly_two_things():
    # .add/tasks/bench-sonnet-only.md M2: Build stays in the main Sonnet session
    shipped, variant = SHIPPED.read_text().splitlines(), VARIANT.read_text().splitlines()
    hunks = [g for g in difflib.SequenceMatcher(None, shipped, variant).get_opcodes() if g[0] != "equal"]
    assert len(hunks) == 2, f"the variant differs in {len(hunks)} places, not 2"
    flat = " ".join(" ".join(variant).split())
    for phrase in ("stub only what the checks import", "grep -H '^covers-risks' .add/personas/*.md"):
        assert phrase in flat, f"the variant does not state {phrase!r}"
        assert phrase not in " ".join(" ".join(shipped).split()), f"{phrase!r} already ships"
    assert "haiku" not in flat.lower(), "the variant still names a Haiku model"
    for kept in ("freeze(", "falsifier", "at least one per Must and Reject", "the way a real caller sends them"):
        assert kept in flat, f"the variant dropped {kept!r}"


def test_every_pinned_arm_model_is_sonnet():
    # .add/tasks/bench-sonnet-only.md M3: an arm that pins a model pins a Sonnet one
    arms = [load_arm(ARMS_DIR / f"{n}.toml") for n in ARM_NAMES]
    assert len(arms) == len(ARM_NAMES) > 0
    pinned = {a.name: a.model for a in arms if a.model}
    assert all(m.startswith("claude-sonnet-") for m in pinned.values()), f"non-Sonnet arm models: {pinned}"
    assert all(not a.advisor for a in arms), "an arm still sets an advisor"


def test_no_test_can_launch_the_real_claude():
    with pytest.raises(RuntimeError, match="live"):
        subprocess.Popen(["claude", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with subprocess.Popen(["python3", "-c", "pass"]) as ok:
        assert ok.wait() == 0, "the guard must not block other processes"
