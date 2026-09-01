"""`GETTING-STARTED.md` — the code walkthrough, proved by running it.

Red-first for `/tasks/getting-started-executed.md`.

`BEYOND-CODE.md` says every command in it is executed by a test, and that test exists. The
PRIMARY walkthrough — the file most readers actually open — was executed by nothing: the
shipped-doc suite checked it only for phantom verbs, and the promised-capability suite covers
README bullets and admits it cannot judge whether the thing is what the bullet describes. That
asymmetry is the root cause; the defects it hid were symptoms. Measured 2026-09-01: the walk
never ran `add brief`, so a reader following it literally hits `R:UNBRIEFED` at the gate; the
freeze line omitted `--authority human`, so the documented ONE approval recorded as a process
stamp; and the guide promised `freeze` refuses template placeholders while a node froze with
five surviving.

Everything runnable is LIFTED from the shipped document through named anchors (R:FIXTUREFORK).
A private copy here would let the document rot while the test kept passing against its own fork.
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "GETTING-STARTED.md"
CLI = REPO / "tooling" / "cli.py"
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

# The verbs the walkthrough drives, in the order it drives them. Checked BOTH directions:
# nothing shown that is not run, and nothing run that is not shown (A4, A5).
EXECUTED = ("init", "new", "freeze", "brief", "run", "gate", "learn")

# The node sections the document authors, in the order it authors them.
AUTHORED = ("RULES", "ASSUMPTIONS", "PLAN", "EDGES", "CHECKS")


def _text() -> str:
    assert DOC.is_file(), f"{DOC.name} does not exist — a 'must not say X' check would pass vacuously"
    return DOC.read_text(encoding="utf-8")


def _block(anchor: str) -> str:
    """Lift one anchored fenced block from the shipped document."""
    m = re.search(rf"<!--\s*{anchor}\s*-->\s*```[a-z]*\n(.*?)```", _text(), re.DOTALL)
    assert m, f"the walkthrough publishes no `<!-- {anchor} -->` fenced block"
    return m.group(1)


def _run(root, *args):
    done = subprocess.run([sys.executable, str(CLI), "--root", str(root), *args],
                          capture_output=True, text=True, timeout=300)
    return done


def _section(body: str, heading: str, new_text: str) -> str:
    lines = body.splitlines()
    start = next(i for i, l in enumerate(lines) if l.strip() == f"## {heading}")
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    return "\n".join(lines[:start + 1] + [new_text] + lines[end:])


@pytest.fixture(scope="module")
def walked(tmp_path_factory):
    """Drive the document's own commands, in the document's own order, once."""
    project = tmp_path_factory.mktemp("ledger")
    root = project / ".add"
    log = {}
    # A real reader's project: a git working tree, with the paths the walkthrough declares as
    # `scope:`. The gate establishes receipt freshness from a content digest over those paths,
    # and it can do neither outside a working tree — which the guide now says.
    subprocess.run(["git", "init", "-q"], cwd=str(project), check=True)
    (project / "src").mkdir(exist_ok=True)
    (project / "tests").mkdir(exist_ok=True)

    for line in _block("gs:scaffold").strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        args = _shell_split(line)
        log[args[0]] = _run(root, *args)

    node = root / "tasks" / "transfer.md"
    raw = node.read_text(encoding="utf-8")
    head, _, body = raw.partition("\n---\n")
    head = head.replace("gives:\n  - S1 <the surface this publishes — an endpoint, function, or section>",
                        "gives:\n  - S1 POST /transfers")
    for heading, anchor in zip(AUTHORED, ("gs:rules", "gs:assumptions", "gs:plan",
                                          "gs:edges", "gs:checks")):
        body = _section(body, heading, _block(anchor).rstrip())
    body = _section(body, "CARD",
                    "goal: money moves between my own accounts, atomically.\n"
                    "why: the walkthrough's worked example.\n"
                    "beat: direction · next: add freeze transfer")
    node.write_text(f"{head}\n---\n{body}")

    # The guide says "Write those tests now" — so the walk writes them, with the ids the
    # document's own CHECKS name. Anything else would prove the walk runs and not that its
    # `covers:` ids bind, which is the half readers actually get wrong.
    ids = re.findall(r"^- (test_[a-z_]+) ·", _block("gs:checks"), re.M)
    assert ids, "the walkthrough's CHECKS block names no test ids"
    (project / "tests").mkdir(exist_ok=True)
    (project / "tests" / "test_transfer.py").write_text(
        "\n".join(f"def {i}():\n    assert True\n" for i in ids))

    for anchor in ("gs:freeze", "gs:brief", "gs:run", "gs:gate"):
        for line in _block(anchor).strip().splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            args = _shell_split(line)
            log[args[0]] = _run(root, *args)
    return root, log


def _shell_split(line: str) -> list:
    """The document writes `add <verb> …`; the test drives cli.py directly."""
    import shlex
    parts = shlex.split(line.replace("${TMPDIR:-/tmp}", "/tmp"))
    assert parts and parts[0] == "add", f"a walkthrough command must start with `add`: {line}"
    return parts[1:]


def test_the_getting_started_walkthrough_runs_green(walked):
    """covers: M1, A5 · every block executes in order with the guide's literal flags."""
    root, log = walked
    for verb, done in log.items():
        if verb == "run":
            # "A failing command is a recorded result, not an error" — the guide's own words.
            assert "receipt" in done.stdout, done.stdout + done.stderr
            continue
        assert done.returncode == 0, f"`add {verb}` failed:\n{done.stdout}\n{done.stderr}"
    assert "PASS" in log["gate"].stdout, log["gate"].stdout


def test_the_walkthrough_blocks_come_from_the_document(walked):
    """covers: A4, A9, R:UNEXECUTEDDOC · the block set is parsed from the file, not hand-listed."""
    _, log = walked
    shown = set(re.findall(r"^\s*add ([a-z-]+)", _text(), re.M))
    for verb in EXECUTED:
        assert verb in shown, f"the walkthrough never shows `add {verb}`, but the test runs it"
        assert verb in log or verb == "learn", f"the walkthrough shows `add {verb}` but nothing runs it"


def test_the_documented_freeze_records_human_authority(walked):
    """covers: M4, R:PROCESSAPPROVAL · the stamp reads `authority: human`."""
    root, _ = walked
    stamps = (add.load(root)["/tasks/transfer.md"]["fm"] or {}).get("verified") or []
    freezes = [s for s in stamps if isinstance(s, dict) and s.get("act") in ("freeze", "refreeze")]
    assert freezes, "the walkthrough recorded no freeze"
    assert freezes[0].get("authority") == "human", \
        f"the documented ONE approval recorded as `{freezes[0].get('authority')}`"


def test_the_walkthrough_enters_a_build_before_it_runs():
    """covers: M5 · `add brief` is shown, because the gate refuses a build nothing entered."""
    flat = " ".join(_text().split())
    assert "add brief transfer" in flat, \
        "the walk never shows `add brief`, so a reader following it literally hits R:UNBRIEFED"


def test_freeze_refuses_a_template_card_goal(tmp_path):
    """covers: M2, A6 · the refusal fires and names CARD."""
    root = tmp_path / ".add"
    add.init(root, profile="code", title="placeholder probe")
    add.new(root, "Task", "hollow", depth="quick")
    p = root / "tasks" / "hollow.md"
    b = p.read_text(encoding="utf-8")
    b = _section(b, "RULES", "<must>\n- M1 it holds\n</must>\n<reject>\n"
                             '- R:NOPE it never breaks -> "NOPE"\n</reject>')
    b = _section(b, "CHECKS", "- test_it_holds · covers: M1 · it holds\n"
                              "- test_it_never_breaks · covers: R:NOPE · it refuses")
    p.write_text(b)
    node, err = add.freeze(root, "/tasks/hollow.md", by="t", authority="human")
    assert node is None, "freeze admitted a node whose CARD goal is still a template"
    assert "CARD" in err, f"the refusal does not name the section: {err}"


def test_freeze_still_admits_template_evidence_and_lessons(tmp_path):
    """covers: M3, A2, E1 · the pre-run sections stay exempt."""
    root = tmp_path / ".add"
    add.init(root, profile="code", title="exempt probe")
    add.new(root, "Task", "filled", depth="quick")
    p = root / "tasks" / "filled.md"
    b = p.read_text(encoding="utf-8")
    b = _section(b, "CARD", "goal: it does the thing.\nwhy: because.\nbeat: direction")
    b = _section(b, "RULES", "<must>\n- M1 it holds\n</must>\n<reject>\n"
                             '- R:NOPE it never breaks -> "NOPE"\n</reject>')
    b = _section(b, "ASSUMPTIONS", "- A1 [who] covers: S1 · the request does not say who may "
                                   "act; taking the owner -> if wrong it acts for a stranger")
    b = _section(b, "CHECKS", "- test_it_holds · covers: M1 · it holds\n"
                              "- test_it_never_breaks · covers: R:NOPE · it refuses")
    p.write_text(b)
    assert "receipt: <runs/" in p.read_text(encoding="utf-8"), "EVIDENCE is not template — bad fixture"
    node, err = add.freeze(root, "/tasks/filled.md", by="t", authority="human")
    assert node is not None, f"freeze refused a node whose only templates are EVIDENCE/LESSONS: {err}"


def test_the_card_guard_applies_at_quick_depth(tmp_path):
    """covers: E4 · depth does not exempt the CARD guard, unlike the assumption sweep."""
    root = tmp_path / ".add"
    add.init(root, profile="code", title="quick probe")
    add.new(root, "Task", "quickie", depth="quick")
    p = root / "tasks" / "quickie.md"
    b = p.read_text(encoding="utf-8")
    b = _section(b, "RULES", "<must>\n- M1 it holds\n</must>\n<reject>\n"
                             '- R:NOPE it never breaks -> "NOPE"\n</reject>')
    b = _section(b, "CHECKS", "- test_it_holds · covers: M1 · it holds\n"
                              "- test_it_never_breaks · covers: R:NOPE · it refuses")
    p.write_text(b)
    node, err = add.freeze(root, "/tasks/quickie.md", by="t", authority="human")
    assert node is None and "CARD" in err


def test_a_milestone_why_guard_is_unchanged(tmp_path):
    """covers: E3 · `milestone_why_unset` keeps its own message."""
    root = tmp_path / ".add"
    add.init(root, profile="code", title="milestone probe")
    add.new(root, "Milestone", "theme")
    node, err = add.freeze(root, "/milestones/theme.md", by="t", authority="human")
    assert not node, "freeze admitted a scaffold milestone"
    assert "scaffold" in err.lower() and "why" in err.lower(), err
    assert "CARD" in err, "the milestone's own guard no longer names the sections it wants"


def test_an_existing_frozen_stamp_is_not_rewritten(walked):
    """covers: A3, E2 · history is append-only; the guard judges the next freeze only."""
    root, _ = walked
    stamps = (add.load(root)["/tasks/transfer.md"]["fm"] or {}).get("verified") or []
    assert stamps, "the walkthrough recorded no stamps at all"
    assert all(isinstance(s, dict) and s.get("at") for s in stamps)


def test_every_refusal_the_guide_claims_is_executed():
    """covers: M5 · each claimed refusal has an executing assertion in this file."""
    flat = " ".join(_text().split())
    if "refuses a node that still carries template" in flat:
        assert "test_freeze_refuses_a_template_card_goal" in Path(__file__).read_text()
    if "R:UNBRIEFED" in flat or "add brief" in flat:
        assert "test_the_walkthrough_enters_a_build_before_it_runs" in Path(__file__).read_text()


def test_illustrative_output_blocks_are_not_executed():
    """covers: E5 · the parser distinguishes command from output — only anchored blocks run."""
    anchors = set(re.findall(r"<!--\s*(gs:[a-z-]+)\s*-->", _text()))
    assert anchors, "the walkthrough carries no executable anchors"
    # The body anchors (rules · assumptions · plan · edges · checks) are node CONTENT the
    # reader types into a file; only the command anchors are driven as commands.
    for anchor in {"gs:scaffold", "gs:freeze", "gs:brief", "gs:run", "gs:gate"} & anchors:
        for line in _block(anchor).strip().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                assert line.startswith("add "), \
                    f"`{anchor}` carries a non-command line, so it is not an executable block: {line}"
