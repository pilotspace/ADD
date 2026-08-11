"""Red suite for `docs-beta2-refresh` — the mkdocs book teaches the engine that ships.

3.0.0-beta.2 turned five docket items into engine checkpoints (brief entry, gate probes,
broader collapse detection, routing-index freshness, `add upgrade`), and the skill docs
followed — but the BOOK, the cold adopter's first hour, still described the beta.1 subset:
only 2 of 25 pages named any beta.2 verb. A book that under-describes the engine is the
same drift class as the overclaim pass burned us on, in the other direction.

The load-bearing check is parser-derived (M1): every wired verb has a command-reference
row, with `cli.build_parser()` as the oracle — so the NEXT wired verb reds this suite too,
instead of waiting for a human to remember the table.

Driven as dogfood task `.add/tasks/docs-beta2-refresh.md` (v3.0.0 hardening tally #4).
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import cli  # noqa: E402

DOCS = REPO / "docs"


def _page(name: str) -> str:
    return (DOCS / name).read_text(encoding="utf-8")


def _wired_verbs() -> set:
    parser = cli.build_parser()
    subactions = next(a for a in parser._actions
                      if a.__class__.__name__ == "_SubParsersAction")
    return set(subactions.choices)


def test_command_reference_carries_every_wired_verb():
    """covers: M1,E1 — parser-derived roster; each verb named in a table row."""
    text = _page("13-command-reference.md")
    rows = "\n".join(l for l in text.splitlines() if l.startswith("|"))
    missing = sorted(v for v in _wired_verbs() if not re.search(rf"`{re.escape(v)}`", rows))
    assert not missing, f"wired verbs with no command-reference row: {missing}"


def test_direction_teaches_the_probe_grammar():
    """covers: M2 — `· probe:` taught where assumptions are authored."""
    text = _page("03-direction.md")
    assert "probe:" in text, "Direction never teaches the `· probe:` opt-in"
    assert "checkable" in text or "gate holds" in text, \
        "the probe's consequence (the gate binds it) is not stated"


def test_build_teaches_the_brief_entry():
    """covers: M2 — `add brief` as the recorded entry into Build."""
    text = _page("04-build.md")
    assert "add brief" in text, "Build never names its own entry verb"
    assert "act: brief" in text or "entry" in text.lower(), \
        "the brief is mentioned but not as the recorded ENTRY into Build"


def test_verify_names_the_unbriefed_refusal():
    """covers: M2 — R:UNBRIEFED among the gate's refusal ladder."""
    text = _page("05-verify.md")
    assert "UNBRIEFED" in text, "the gate's brief-entry refusal is absent from Verify"


def test_bundle_format_shows_stamp_probe_and_okf():
    """covers: M3 — the stamp and token verbatim; OKF as alignment, not certification."""
    text = _page("12-bundle-format.md")
    assert "act: brief" in text, "the brief stamp shape is not shown"
    assert "probe:" in text, "the probe token is not shown"
    assert "Open Knowledge Format" in text, "the OKF alignment note is absent"
    assert "OKF-certified" not in text and "fully conformant" not in text, \
        "the OKF note overclaims — alignment is the honest word"


def test_adoption_names_the_upgrade_path():
    """covers: M2 — `add upgrade` where adopters with a 2.x bundle land."""
    text = _page("11-adoption.md")
    assert "add upgrade" in text, "an adopter with a 2.x bundle finds no path in Adoption"
    assert "archive" in text.lower(), \
        "the upgrade's nothing-is-deleted contract (whole-bundle archive) is not stated"


def test_scoped_pages_stay_buildable():
    """covers: M4 — the two things `mkdocs build --strict` actually reds on, portably:
    every scoped page is reachable from the nav, and its relative links resolve."""
    nav = (REPO.parent / "mkdocs.yml").read_text(encoding="utf-8")
    pages = ["03-direction.md", "04-build.md", "05-verify.md",
             "11-adoption.md", "12-bundle-format.md", "13-command-reference.md"]
    for name in pages:
        assert name in nav, f"{name} fell out of the mkdocs nav"
        for target in re.findall(r"\]\(\./([\w.-]+\.md)", _page(name)):
            assert (DOCS / target).is_file(), f"{name} links to missing page {target}"


def test_no_page_promises_unshipped_enforcement():
    """covers: A3, R:OVERCLAIM (probe) — the six pages name no verb the CLI does not wire."""
    wired = _wired_verbs()
    pages = ["03-direction.md", "04-build.md", "05-verify.md",
             "11-adoption.md", "12-bundle-format.md", "13-command-reference.md"]
    for name in pages:
        for verb in re.findall(r"`add ([a-z][a-z-]*)\b", _page(name)):
            assert verb in wired, f"{name} names `add {verb}`, which the CLI does not wire"
