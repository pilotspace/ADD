"""The `add run` line the skill teaches is the line the engine tells you to run.

`run` now sniffs the report path out of the command it was already handed, so the engine's own
`next:` hint names that path ONCE. The shipped skill still taught the doubled form — and taught it
in words, with a comment explaining that the repetition was deliberate. Both spellings still WORK
(the flag survives as an override), which is exactly why nothing failed: `test_receipt_idiom_truth`
scopes itself to report-READING examples, decided by whether the engine-side flag is present, so
dropping that flag makes an example invisible to it rather than wrong.

That is the guard-class hole this release exists to close, one turn later and self-inflicted: a
capability the prose PROMISES with no noun on the engine to bind it to. The binding here is
`BEAT_NEXT["build"]` — the string the user is actually shown at the end of a build.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "skill" / "add"
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _taught_lines():
    """Every `add run … -- …` example in the shipped skill, shell continuations joined."""
    out = []
    for f in sorted(SKILL.rglob("*.md")):
        raw = f.read_text(encoding="utf-8").splitlines()
        i = 0
        while i < len(raw):
            start, line = i + 1, raw[i].rstrip()
            while line.endswith("\\") and i + 1 < len(raw):
                i += 1
                line = line[:-1].rstrip() + " " + raw[i].strip()
            if "add run " in line and " -- " in line:
                out.append((f.relative_to(SKILL), start, line.strip()))
            i += 1
    return out


def test_the_engine_hint_names_the_report_path_once():
    """covers: M1 — the binding subject, stated before it is compared against."""
    assert add.BEAT_NEXT["build"].count("--junitxml") == 1, add.BEAT_NEXT["build"]


def test_no_taught_example_names_the_report_path_twice():
    """covers: M1, M2 — what the skill teaches agrees with what the engine prints.

    Scoped by the path, not by the flag: an example naming `add-run.xml` on both sides of the
    `--` is the doubled form however it is spelled, so this cannot go quiet the way the incumbent
    guard did when the engine-side flag disappeared.
    """
    examples = _taught_lines()
    assert examples, "no `add run` example found — the guard would be vacuous"
    # The trailing `# …` comment is stripped first: it is prose, not an argument anyone copies,
    # and the corrected line legitimately NAMES the override flag there while passing it once.
    doubled = [f"{rel}:{n} — {line}" for rel, n, line in examples
               if (a := line.split("#", 1)[0]).count("--junitxml") > 1
               or a.count("add-run.xml") > 1]
    assert not doubled, (
        "these teach a report path the engine no longer asks for, while `next:` prints it once:"
        "\n  " + "\n  ".join(doubled))


def test_the_prose_does_not_defend_the_repetition():
    """covers: M3 — the doubling was explained on purpose, so the explanation must go too.

    A stale example is a typo; a stale SENTENCE saying the repetition is deliberate teaches the
    reader to distrust the engine's own hint. This is the half a find-and-replace leaves behind.
    """
    stale = []
    for f in sorted(SKILL.rglob("*.md")):
        text = f.read_text(encoding="utf-8")
        for m in re.finditer(r"[^\n.]*path twice[^\n.]*", text):
            stale.append(f"{f.relative_to(SKILL)} — {m.group(0).strip()}")
    assert not stale, "the prose still defends the doubled path:\n  " + "\n  ".join(stale)


def test_the_override_is_still_documented():
    """covers: M4, E1 — the flag did not disappear, and a reader must still be able to find it.

    Dropping the doubling from the examples must not delete the escape hatch from the docs: a
    runner that writes its report where the command line never names it has no other route.
    """
    text = " ".join((SKILL / "phases" / "verify.md").read_text(encoding="utf-8").split())
    assert "--junitxml" in text, "verify.md no longer mentions --junitxml at all"
    assert "override" in text.lower() or "sniff" in text.lower(), \
        f"verify.md does not explain how the report path is found:\n{text[:400]}"
