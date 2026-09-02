"""The README leads with the ladder, and the walkthrough it links contains none of it.

README:69 opens "Most changes never create a node." and points every newcomer at
GETTING-STARTED as the walkthrough. That file had ZERO occurrences of ladder, direct lane,
explore, size or mechanical; §2 goes straight to "it sizes your request and proposes a
milestone", the appendix straight to `add new Task`, and `init`'s own next-hint says
`add new milestone <slug>`. A reader who follows only what the front door points at creates
a node for every change — the exact behaviour the ladder exists to stop.

Two smaller truths in the same file: it said the scaffold lands at beat `direction` when the
engine says `scaffold` (and the walkthrough test hardcoded the doc's version, so it could not
catch the drift), and `--nested` / `--no-skill` are flags a real refusal and a real install
path need, documented nowhere.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO.parent
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

GS = REPO / "GETTING-STARTED.md"
SKILL = REPO / "skill" / "add" / "SKILL.md"
READMES = [ROOT / "README.md", REPO / "README.md"]


def _text(p):
    return p.read_text(encoding="utf-8") if p.is_file() else ""


def test_the_walkthrough_names_the_ladder_the_front_door_leads_with():
    """covers: M1, R:ORPHANCLAIM — a headline nobody can act on from the page it links."""
    gs = _text(GS).lower()
    missing = [w for w in ("ladder", "direct", "explore") if w not in gs]
    assert not missing, (
        "the README leads with the ceremony ladder and the walkthrough it links never "
        f"mentions: {missing}")


def test_the_walkthrough_states_the_scaffold_beat_the_engine_reports(tmp_path):
    """covers: M2, A1 — measured against the engine, never against the doc's own claim."""
    add.init(tmp_path, "code", "T")           # `init` returns a tuple, not the root
    root = tmp_path
    cid, _ = add.new(root, "Task", "transfer", title="t")
    beat = add._beat_of(add.scan(root)[cid])
    gs = _text(GS)
    m = re.search(r"leaves it\s*\n?\s*at beat `(\w+)`", gs)
    assert m, "the walkthrough no longer states a scaffold beat — this guard is stale"
    assert m.group(1) == beat, (
        f"the walkthrough says beat `{m.group(1)}`; the engine reports `{beat}`")


def test_the_documented_flags_that_a_refusal_names_are_documented():
    """covers: M3 — R:RIVALBUNDLE's escape hatch is documented only inside the refusal."""
    engine = _text(REPO / "tooling" / "add.py")
    assert "--nested" in engine, "the guard is stale — R:RIVALBUNDLE no longer names --nested"
    docs = "".join(_text(p) for p in READMES + [GS, SKILL])
    assert "--nested" in docs, (
        "`add init --nested` is the only way past R:RIVALBUNDLE and both READMES promise "
        "monorepo support; the flag appears in no shipped doc")


def test_the_plugin_bootstrap_names_no_skill():
    """covers: M4 — a bare bootstrap installs a duplicate skill that shadows the plugin's."""
    js = _text(REPO / "bin" / "cli.js")
    assert "--no-skill" in js, "the guard is stale — the installer no longer offers --no-skill"
    skill = _text(SKILL)
    if "CLAUDE_PLUGIN_ROOT" in skill:
        line = [l for l in skill.splitlines() if "CLAUDE_PLUGIN_ROOT" in l and "cli.js" in l]
        assert not line or all("--no-skill" in l for l in line), (
            "the plugin bootstrap command omits `--no-skill`, so a plugin user gets a second, "
            f"project-local copy of the skill that goes stale on every upgrade: {line}")


def test_the_interview_cookbook_names_every_verdict():
    """covers: M5 — `correct` is the verdict for "the AI got this wrong"; it was missing."""
    skill = _text(SKILL)
    line = [l for l in skill.splitlines() if "add interview" in l]
    assert line, "SKILL.md no longer documents `add interview` — this guard is stale"
    for verdict in add.INTERVIEW_VERDICTS:
        assert any(verdict in l for l in line), (
            f"the cookbook's interview line omits `{verdict}`: {line}")
