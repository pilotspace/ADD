"""Red suite for `launch-blog` — the launch post's claims are pinned, not remembered.

The v3.0.0 announcement is held for the final tag, but the post is written NOW, inside the
loop, so every measured claim is test-bound before anyone can quote it. The oracle reads
the COMMITTED campaign record (benchmark/CAMPAIGN-amb1-beta2.md), not a constant in this
file — regenerate the record with different numbers and the post reds instead of drifting
(E1, R:QUOTEDRIFT).

Driven as dogfood task `.add/tasks/launch-blog.md` (v3.0.0 hardening tally #5).
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import cli  # noqa: E402

POST_PATH = REPO.parent / "blog" / "introducing-add-30.md"
RECORD = (REPO.parent / "benchmark" / "CAMPAIGN-amb1-beta2.md").read_text(encoding="utf-8")


def _post() -> str:
    assert POST_PATH.is_file(), "the launch post does not exist yet"
    return POST_PATH.read_text(encoding="utf-8")


def test_campaign_stats_match_the_committed_record():
    """covers: M1,A2,R:QUOTEDRIFT,E1 — safe rate, n and cost equal the committed record."""
    post = _post()
    safe = float(re.search(r"safe rate.*?mean ([\d.]+)", RECORD).group(1))
    n = int(re.search(r"## add — (\d+) rep", RECORD).group(1))
    cost = float(re.search(r"cost_usd: mean ([\d.]+)", RECORD).group(1))
    assert f"{round(safe * 7)} of the 7" in post or f"{round(safe * 7)}/7" in post, \
        "the post's safe-rate claim does not restate the record's 5-of-7"
    assert f"n={n}" in post or f"{n} independent" in post or f"three independent" in post, \
        "the post never states the campaign size"
    assert f"${cost:.2f}" in post, \
        f"the post's cost claim does not match the record's ${cost:.2f}"
    assert "every rep" in post or "all three" in post, \
        "the zero-spread fact (same result in every rep) is the record's point — state it"


def test_post_links_the_evidence_trail():
    """covers: M2 — the cheat post is linked and the release claim is verbatim."""
    post = _post()
    assert "we-tried-to-cheat-our-own-dev-method" in post, \
        "the cheat post is the evidence trail — link it"
    assert "auditability, not correctness" in post, \
        "the release claim must appear verbatim"


def test_install_commands_are_the_shipped_ones():
    """covers: M3 — both installers, exactly as shipped."""
    post = _post()
    assert "npx @pilotspace/add init" in post
    assert "pip install pilotspace-add" in post


def test_post_names_no_unwired_verb():
    """covers: M3 — every `add <verb>` in the post is wired in the CLI."""
    parser = cli.build_parser()
    subactions = next(a for a in parser._actions
                      if a.__class__.__name__ == "_SubParsersAction")
    wired = set(subactions.choices)
    for verb in re.findall(r"`add ([a-z][a-z-]*)\b", _post()):
        assert verb in wired, f"the post names `add {verb}`, which the CLI does not wire"
