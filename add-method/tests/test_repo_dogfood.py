"""The repo runs the method it ships.

A project that ships ADD while its own bundle follows a retired format is the one claim a reader
can check for free, so it is a test rather than an intention. The 3.x bundle is kept, readable,
under `archive/add-3x-bundle/` (and the 2.x one under `archive/add-2x-bundle/`) as the record of
how this repo was built. These checks are about what is CURRENT.
"""
import re
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]      # add-method/
ROOT = PKG.parent
BUNDLE = ROOT / ".add"
LENSES = ("domain", "system", "experience", "quality", "method")


def _frontmatter(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{path} has no frontmatter"
    return text.split("---\n", 2)[1]


def test_project_declares_goal_invariants_and_test_command():
    fm = _frontmatter(BUNDLE / "PROJECT.md")
    assert re.search(r"^type: Project$", fm, re.M)
    assert re.search(r"^goal: \S", fm, re.M), "PROJECT.md has no goal"
    assert re.search(r"^invariants:\n  - \S", fm, re.M), "PROJECT.md binds no invariants"
    assert re.search(r"^test_cmd: \S", fm, re.M), "PROJECT.md names no test command"


def test_every_lens_has_a_spec():
    for lens in LENSES:
        fm = _frontmatter(BUNDLE / "specs" / f"{lens}.md")
        assert re.search(rf"^lens: {lens}$", fm, re.M), f"specs/{lens}.md declares the wrong lens"


def test_no_engine_artifact_is_tracked_in_the_live_bundle():
    stale = [n for n in ("graph.json", "index.md", "log.md", "tooling", "runs") if (BUNDLE / n).exists()]
    assert not stale, f"3.x engine artifacts in the live bundle: {stale}"


def test_the_3x_bundle_is_archived_not_lost():
    archive = ROOT / "archive" / "add-3x-bundle"
    assert (archive / "PROJECT.md").is_file()
    assert len(list((archive / "tasks").glob("*.md"))) > 100, "the 3.x task record is incomplete"


def test_every_task_and_milestone_carries_a_known_status():
    allowed = {"tasks": {"direction", "build", "done", "dropped"}, "milestones": {"active", "done"}}
    nodes = 0
    for kind, statuses in allowed.items():
        for f in (BUNDLE / kind).glob("*.md"):
            nodes += 1
            m = re.search(r"^status: (\S+)$", _frontmatter(f), re.M)
            assert m and m.group(1) in statuses, f"{f.name}: status {m and m.group(1)!r}"
    assert nodes, "the bundle has no task or milestone at all"
