"""Each arm runs at its own effort: ADD at `low` against raw Claude Code at `medium`, same model.

The question this makes askable: does ADD's ceremony buy back what a cheaper effort level gives
up? One global `--effort medium` could neither run that asymmetry nor record it."""
import dataclasses
import pathlib

import pytest

from benchmark import pilot
from benchmark.arms.loader import ARM_NAMES, Arm, load_arm
from benchmark.runner import agent, core
from benchmark.schema.run_record import BenchError

ARMS_DIR = pathlib.Path(__file__).resolve().parents[1] / "arms"


def _arm(**over) -> Arm:
    base = Arm(name="vanilla", setup_steps=[], prompt_wrapper="raw", pin="", same_model=True,
               token_ceiling=200000, turn_ceiling=60)
    return dataclasses.replace(base, **over)


def test_effort_defaults_empty_and_loads_from_toml(tmp_path):
    assert load_arm(ARMS_DIR / "vanilla.toml").effort == ""
    (tmp_path / "vanilla.toml").write_text((ARMS_DIR / "vanilla.toml").read_text() + '\neffort = "low"\n')
    assert load_arm(tmp_path / "vanilla.toml").effort == "low"


def test_unknown_effort_is_refused_at_load(tmp_path):
    (tmp_path / "vanilla.toml").write_text((ARMS_DIR / "vanilla.toml").read_text() + '\neffort = "lo"\n')
    with pytest.raises(BenchError, match="effort"):
        load_arm(tmp_path / "vanilla.toml")


def test_resolved_effort_prefers_arm_then_flag_then_medium():
    assert agent.resolve_effort("", None) == agent.DEFAULT_EFFORT == "medium"
    assert agent.resolve_effort("", "high") == "high"
    assert agent.resolve_effort("low", "high") == "low"


def test_argv_carries_the_effort():
    assert (lambda a: a[a.index("--effort") + 1])(agent.build_argv("p", None)) == "medium"
    low = agent.build_argv("p", None, effort="low")
    assert low[low.index("--effort") + 1] == "low"
    assert agent.build_argv("p", ["python3", "f.py"], effort="low") == ["python3", "f.py", "p"]


def test_execute_wm_passes_and_records_the_effort(tmp_path, monkeypatch):
    seen = []
    monkeypatch.setattr(core, "_invoke_once", lambda argv, **kw: seen.append(list(argv)) or ("failed", [], 0.0))
    rec = core.execute_wm(_arm(effort="low"), 1, runs_root=tmp_path, retries=0)
    assert seen[0][seen[0].index("--effort") + 1] == "low" and rec.artifacts["effort"] == "low"
    seen.clear()
    rec = core.execute_wm(_arm(), 1, runs_root=tmp_path / "b", retries=0)
    assert seen[0][seen[0].index("--effort") + 1] == "medium" and rec.artifacts["effort"] == "medium"


def test_run_all_cli_accepts_effort(monkeypatch):
    got = {}
    monkeypatch.setattr(pilot, "run_reps", lambda **kw: got.update(kw) or [])
    pilot.main(["run-all", "--arms", "vanilla", "--wms", "1", "--reps", "2", "--effort", "low"])
    assert got.get("effort") == "low"


def test_add_4_low_is_add_4_at_low_effort():
    assert "add-4-low" in ARM_NAMES
    low, base = load_arm(ARMS_DIR / "add-4-low.toml"), load_arm(ARMS_DIR / "add-4.toml")
    assert low.setup_steps == base.setup_steps and low.prompt_wrapper == base.prompt_wrapper
    assert (low.effort, low.model) == ("low", "")
    assert base.effort == "" and load_arm(ARMS_DIR / "vanilla.toml").effort == "", \
        "the control arms keep the meter's medium default"


AUDITED = ARMS_DIR / "variants" / "add-4-audited" / "SKILL.md"
# the shipped ADD 4.0.0 skill the variants were cut from — the live skill moves on
SHIPPED = ARMS_DIR / "variants" / "BASE-4.0.0-SKILL.md"


def test_audited_arm_installs_the_audited_variant_at_low_effort():
    assert "add-4-audited-low" in ARM_NAMES
    arm, base = load_arm(ARMS_DIR / "add-4-audited-low.toml"), load_arm(ARMS_DIR / "add-4.toml")
    assert (arm.effort, arm.model) == ("low", "")
    assert [s for s in arm.setup_steps if s in base.setup_steps] == base.setup_steps
    cp = [s for s in arm.setup_steps if "variants/add-4-audited/SKILL.md" in s and ".claude/skills/add/SKILL.md" in s]
    assert cp and base.setup_steps[2] in arm.setup_steps[: arm.setup_steps.index(cp[0])], \
        "the variant must overwrite the skill after install"


def test_audited_variant_drops_turn_counts_and_keeps_the_method():
    shipped = " ".join(SHIPPED.read_text().split())
    variant = " ".join(AUDITED.read_text().split())
    for gone in ("Direction = three turns", "Verify = two turns"):
        assert gone in shipped and gone not in variant, f"{gone!r} should be audited out"
    for new in ("stub only what the checks import", "grep -H '^covers-risks' .add/personas/*.md",
                ".add/personas-index/use-when.md"):
        assert new in variant and new not in shipped, f"the variant does not add {new!r}"
    for kept in ("freeze(<slug>)", "falsifier", "at least one per Must and Reject", "NotImplementedError",
                 "the way a real caller sends them", "foreground",
                 "Never edit a sealed check", "HARD-STOP", "<constraints>"):
        assert kept in variant, f"the variant dropped {kept!r}"


PROBE = ARMS_DIR / "variants" / "add-4-probe" / "SKILL.md"


def test_probe_arm_is_the_audited_variant_plus_the_probe_rule_at_low_effort():
    assert "add-4-probe-low" in ARM_NAMES
    arm = load_arm(ARMS_DIR / "add-4-probe-low.toml")
    assert (arm.effort, arm.model) == ("low", "")
    assert any("variants/add-4-probe/SKILL.md" in s for s in arm.setup_steps)
    import difflib
    audited, probe = AUDITED.read_text().splitlines(), PROBE.read_text().splitlines()
    hunks = [g for g in difflib.SequenceMatcher(None, audited, probe).get_opcodes() if g[0] != "equal"]
    assert len(hunks) == 1, f"the probe variant differs from the audited one in {len(hunks)} places, not 1"
    flat = " ".join(" ".join(probe).split())
    for phrase in (".probes/", "not servers started by hand", "kill $P"):
        assert phrase in flat, f"the probe rule does not state {phrase!r}"


def test_measured_session_ignores_the_operators_user_settings():
    """Round 8: the operator's `security-guidance` plugin ran an Opus security review on every
    `git commit` (100-185 s each, billed outside the run record) and the user CLAUDE.md told the
    agent to interview the human. ADD commits and vanilla does not, so the operator's config was
    measured as ADD's cost. `--setting-sources project,local` drops user plugins, hooks and CLAUDE.md."""
    argv = agent.build_argv("p", None)
    assert argv[argv.index("--setting-sources") + 1] == "project,local"
