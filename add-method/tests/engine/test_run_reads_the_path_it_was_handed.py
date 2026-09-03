"""The same report path, typed twice, and getting it wrong costs a receipt that binds nothing.

`--junitxml` on `add run` tells the ENGINE where to READ the report. The command writes it. So the
documented idiom names one path in two places:

    add run x --junitxml "$X" -- pytest ... --junitxml="$X"

The engine already holds the command as a list. The second mention is not information — it is a
restatement the caller can get wrong, and the punishment is a receipt with `ids: unknown`, which
makes every rule read as unbound and (until this branch) offered a signed waiver as the only exit.

The flag stays, as an OVERRIDE: a runner may write its report to a path the command line never
names — a config file, a fixed CI location — and those callers must keep working.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402
from add import scan  # noqa: E402

WRITE = ("import sys,pathlib; p=pathlib.Path(sys.argv[1]); "
         "p.write_text('<testsuites><testsuite>"
         "<testcase classname=\"c\" name=\"test_x\"/></testsuite></testsuites>')")


def _bundle(tmp_path):
    """A node that CITES `test_x`, so a bound report reaches `passed:` and not only the tally.

    `passed:` is filtered to the ids the node's `## CHECKS` cite. A fixture that cites nothing
    records an empty `passed:` however well the report was read, which would let this file pass
    on a receipt that binds nothing.
    """
    add.init(tmp_path, "code", "T")
    cid, _ = add.new(tmp_path, "Task", "t", title="t")
    node = Path(scan(tmp_path)[cid]["path"])
    node.write_text(node.read_text(encoding="utf-8").replace(
        "<test_name>", "test_x", 1), encoding="utf-8")
    return tmp_path, cid


def _writes(path, *extra):
    """A command that really writes a JUnit report to `path`, naming it the way pytest does."""
    return [sys.executable, "-c", WRITE, str(path), *extra]


# ------------------------------------------------------------------ M1 · the sniff

def test_run_sniffs_the_report_path_from_the_command(tmp_path):
    """covers: M1, A2 — the doubled path, written once."""
    root, cid = _bundle(tmp_path)
    xml = tmp_path / "r.xml"
    out = add.run(root, cid, _writes(xml, f"--junitxml={xml}"))     # NO junit= kwarg
    assert out["receipt"].get("ids") != "unknown", (
        "the command named its report and `run` did not read it:\n"
        f"{out['receipt']}")
    # `passed:` is keyed `classname::name`, so the cited bare id lands qualified. Asserting on
    # it — not only on the tally — is what makes this bind: a report the engine read but could
    # not bind to a rule still counts `1/1 reported`.
    assert "c::test_x" in (out["receipt"].get("passed") or []), out["receipt"]


def test_the_two_token_form_is_read_too(tmp_path):
    """covers: M1, A2 — `--junitxml path`, not only `--junitxml=path`."""
    root, cid = _bundle(tmp_path)
    xml = tmp_path / "r2.xml"
    out = add.run(root, cid, _writes(xml, "--junitxml", str(xml)))
    assert out["receipt"].get("ids") != "unknown", out["receipt"]


# ------------------------------------------------------------------ M2 · the override

def test_an_explicit_flag_wins_over_a_sniffed_one(tmp_path):
    """covers: M2, A3 — the flag is an override, never a fallback.

    A runner may write its report somewhere the command line never names. If a sniffed value
    could beat a stated one, the escape hatch would not be one.
    """
    root, cid = _bundle(tmp_path)
    real, decoy = tmp_path / "real.xml", tmp_path / "decoy.xml"
    # the command NAMES the decoy but WRITES the real one
    out = add.run(root, cid, _writes(real, f"--junitxml={decoy}"), junit=real)
    assert out["receipt"].get("ids") != "unknown", (
        f"the explicit --junitxml was ignored in favour of the sniffed decoy: {out['receipt']}")


# ------------------------------------------------------------------ M3/M4 · nothing invented

def test_no_path_named_leaves_ids_unknown(tmp_path):
    """covers: M3, A4, E1, E2, R:GUESSPATH — a path is never fabricated.

    E1: the flag as the last token, with no value after it. E2: the flag's name appearing inside
    an argument to something else. Both must sniff nothing rather than bind a wrong file.
    """
    root, cid = _bundle(tmp_path)
    for command in (
            [sys.executable, "-c", "pass"],                       # names nothing
            [sys.executable, "-c", "pass", "--junitxml"],         # E1: no value follows
            [sys.executable, "-c", "print('--junitxml=/tmp/x')"],  # E2: inside another argument
    ):
        out = add.run(root, cid, command)
        assert out["receipt"].get("ids") == "unknown", (
            f"a report path was invented from {command[-1]!r}: {out['receipt']}")


def test_a_sniffed_path_is_judged_for_staleness(tmp_path):
    """covers: M4 — sniffed and explicit are the same value to everything downstream.

    A report that predates the run is not evidence of it. That guard must not be skipped just
    because the path arrived by a different route.
    """
    root, cid = _bundle(tmp_path)
    xml = tmp_path / "stale.xml"
    xml.write_text("<testsuites><testsuite><testcase classname='c' name='test_old'/>"
                   "</testsuite></testsuites>", encoding="utf-8")
    out = add.run(root, cid, [sys.executable, "-c", "pass", f"--junitxml={xml}"])
    assert out["receipt"].get("ids") == "unknown", (
        "a report that predates the run was accepted as its evidence")
    assert "predates" in str(out["receipt"].get("note", "")) or \
           "junit" in str(out["receipt"].get("note", "")), out["receipt"]


def test_the_last_report_path_wins(tmp_path):
    """covers: A5, E3 — the runner honours the last occurrence, so the reader must agree."""
    root, cid = _bundle(tmp_path)
    first, last = tmp_path / "first.xml", tmp_path / "last.xml"
    out = add.run(root, cid, _writes(last, f"--junitxml={first}", f"--junitxml={last}"))
    assert out["receipt"].get("ids") != "unknown", (
        f"the reader took a report path the runner would have overwritten: {out['receipt']}")


# ------------------------------------------------------------------ M5 · the hint

def test_the_build_hint_names_the_path_once(tmp_path):
    """covers: M5, A6, S2 — the line people paste.

    The doubled path is the one line in the loop that gets pasted wrong, and the punishment is a
    refusal about unbound rules that says nothing about the real cause.
    """
    hint = add.BEAT_NEXT["build"]
    assert hint.count("--junitxml") == 1, (
        f"the build hint still names the report path twice: {hint}")
    assert "add run" in hint and "--" in hint, hint
