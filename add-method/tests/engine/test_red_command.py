"""e17 · a gate cannot pass over a receipt whose command failed.

The red suite for `refuse-red-command`. F17: `gate` has five refusals — the verdict, the
node, the reason, the receipt's existence, its freshness, its placeholders, its unbound
rules — and not one of them reads `exit`. The function never looks at the field that says
whether the command succeeded.

The shape that makes it survive is in `test_green_ids_cannot_mask_a_red_command`: a suite
can report ten passing IDs while the process running it exits non-zero, for a collection
error, a plugin crash, a coverage threshold, or a post-run hook. The receipt then says the
run failed and the gate says the work passed, in the same file.

Every check here must fail because `gate` RECORDS where it should refuse — never because a
name is missing.
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402


TASK_BODY = """## CARD
goal: a task whose rules are all provable
beat: build · next: add run

## RULES
<must>
- M1 the first rule
- M2 the second rule
</must>
<reject>
- R:BAD something forbidden -> "BAD"
</reject>

## CHECKS
- test_one · covers: M1 · proves the first
- test_two · covers: M2, R:BAD · proves the second and the reject
red-first: every check MUST fail first.
"""

CID = "/tasks/gated.md"


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)


@pytest.fixture
def repo(tmp_path):
    """A git repo with a bundle and a task that is gate-ready in every OTHER respect.

    This matters more here than anywhere: if the node carried a placeholder or an unbound
    rule, `gate` would refuse for that reason and every check below would pass while
    proving nothing about the exit code. The fixture removes every other refusal so the
    only thing left to fail on is F17.
    """
    git("init", "-q", cwd=tmp_path)
    git("config", "user.email", "t@example.com", cwd=tmp_path)
    git("config", "user.name", "T", cwd=tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "service.py").write_text("def book():\n    return True\n")

    root = tmp_path / ".add"
    add.init(root, "code", "Red command")
    cid, _ = add.new(root, "Task", "gated", title="A gated task", depth="standard",
                     sensitivity="mechanical", scope=["src/service.py"])
    path = root / cid.lstrip("/")
    n = add.read(path, "T2")
    add.write(path, f"---\n{add.set_key(n['raw'], 'status', 'build')}\n---\n{TASK_BODY}")
    git("add", "-A", cwd=tmp_path)
    git("commit", "-q", "-m", "init", cwd=tmp_path)
    return tmp_path


def _receipt(repo, exit_code=0, ids=("test_one", "test_two")):
    """Record a real receipt through `run` — junit reporting `ids` green, command exiting `exit_code`.

    The junit is written by the command itself, so the two halves of the receipt come from
    the same process, exactly as they would in a real run.
    """
    xml = repo / "r.xml"
    cases = "".join(f'<testcase classname="c" name="{i}"/>' for i in ids)
    script = (f"open({str(xml)!r}, 'w')"
              f".write('<testsuites><testsuite>{cases}</testsuite></testsuites>')\n"
              f"raise SystemExit({exit_code})\n")
    return add.run(repo / ".add", CID, [sys.executable, "-c", script], cwd=repo, junit=xml)


def _gate(repo, verdict="PASS", reason=None):
    return add.gate(repo / ".add", CID, verdict, "human:t", reason=reason)


# ------------------------------------------------------- M1 · the refusal itself (R:GREENLIE)


def test_pass_refused_over_a_red_receipt(repo):
    """covers: M1, R:GREENLIE · a PASS cannot be recorded while the receipt says the run failed."""
    node = _receipt(repo, exit_code=1)
    assert node["receipt"]["exit"] == 1, "the fixture did not produce a red receipt"
    ok, note = _gate(repo)
    assert not ok, f"gate recorded PASS over a receipt with exit 1:\n{note}"


def test_green_receipt_still_passes(repo):
    """covers: M1 · the refusal must not fire on a healthy run — the non-regression half.

    A refusal that fires wrongly is more expensive than one that never fires, because it
    teaches the author to work around the oracle (F8's lesson, recorded at e8).
    """
    _receipt(repo, exit_code=0)
    ok, note = _gate(repo)
    assert ok, f"gate refused a green receipt:\n{note}"


def test_green_ids_cannot_mask_a_red_command(repo):
    """covers: M4, R:GREENLIE · F17's exact shape — every cited ID passes, the command does not.

    This is why the defect survived: `bind` is satisfied, `unbound` is empty, freshness holds,
    and the only field that dissents is the one nothing reads.
    """
    node = _receipt(repo, exit_code=2)
    assert node["receipt"]["kind"] == "test-ids", node["receipt"]
    assert node["receipt"]["passed"], "the fixture reported no passing IDs"
    ok, note = _gate(repo)
    assert not ok, f"a red command was masked by green test IDs:\n{note}"


def test_the_refusal_precedes_freshness(repo):
    """covers: M1 · a receipt that is BOTH red and stale reports red, the more actionable fact."""
    _receipt(repo, exit_code=1)
    (repo / "src" / "service.py").write_text("def book():\n    return False\n")
    ok, note = _gate(repo)
    assert not ok
    assert "exit" in note.lower(), f"the stale refusal hid the red one: {note}"


# ------------------------------------------------------------- M2 · what the refusal says (R:MUTE)


def test_the_refusal_names_the_exit_code(repo):
    """covers: M2, R:MUTE · `gate`'s contract is that a refusal says what would make it pass.

    Asserts the refusal FIRST and the digit in a phrase, not the digit alone: a bare
    `"3" in note` passed against the un-fixed engine because a brief hash contains digits.
    A check that a hex digest can satisfy is not checking the message (F18's class).
    """
    _receipt(repo, exit_code=3)
    ok, note = _gate(repo)
    assert not ok, "the refusal did not fire, so there is no message to inspect"
    assert "exit 3" in note or "exited 3" in note, \
        f"the refusal did not name the exit code: {note}"


def test_the_refusal_names_the_command(repo):
    """covers: M2, R:MUTE · naming the command is what makes the fix the run, not the verdict."""
    _receipt(repo, exit_code=1)
    _, note = _gate(repo)
    assert "SystemExit" in note or "python" in note.lower(), \
        f"the refusal did not name the command that failed: {note}"


# --------------------------------------------------------------- M3 · the node is not trapped (R:TRAP)


def test_risk_accepted_survives_a_red_receipt(repo):
    """covers: M3, R:TRAP · a verdict is how a node LEAVES a bad state; refusing all of them traps it."""
    _receipt(repo, exit_code=1)
    ok, note = _gate(repo, "RISK-ACCEPTED", reason="the failure is a known flake, tracked in F-x")
    assert ok, f"a red receipt left the node with no legal verdict:\n{note}"


def test_hard_stop_survives_a_red_receipt(repo):
    """covers: M3, R:TRAP · HARD-STOP is the honest verdict over a failed run and must be recordable."""
    _receipt(repo, exit_code=1)
    ok, note = _gate(repo, "HARD-STOP", reason="the run failed and the cause is not understood")
    assert ok, f"HARD-STOP was refused over the very receipt that justifies it:\n{note}"
