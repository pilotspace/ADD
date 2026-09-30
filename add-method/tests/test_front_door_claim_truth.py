"""The front door must not assert what this repository's own evidence refutes.

Two classes of false claim have reached the READMEs before:

  R:UNBACKEDCLAIM  Highlights once called ADD "the cheap option". The repo's own revised benchmark
                   reports the opposite at equal trust — spec-kit ~$1.42–1.68 per milestone vs ADD
                   ~$2.58–2.92 — and explicitly RETRACTS the earlier cheaper claim.
  R:STALEPROMISE   The front doors advertised mechanism the package no longer has: a verb count
                   read off a CLI parser, a `doctor --sync` line, "you approve once, at the frozen
                   contract". ADD 4.0 has no CLI and no approval step — the human reviews after,
                   from the session report and the PR.

So: no cost-advantage clause, a measured claim that carries its provenance, the size ladder shown
before install, no verb counts and no approval promises, the cited benchmark untouched, and every
number on the 4.0 migration page traceable to a file in this repo.
"""
import re
import subprocess
from pathlib import Path

PKG = Path(__file__).resolve().parents[1]
ROOT = PKG.parent
# BOTH front doors, always — a guard that reads one of two landing pages leaves the refuted sentence
# on the page most visitors actually reach.
READMES = (PKG / "README.md", ROOT / "README.md")
QUICKSTARTS = (PKG / "GETTING-STARTED.md", ROOT / "GETTING-STARTED.md")
BENCH = ROOT / "benchmark" / "results" / "2026-07-add-2.0-remeasure.md"
MIGRATION = PKG / "docs" / "20-whats-new-in-4.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _highlights(path: Path) -> str:
    """The Highlights section. The two front doors head it differently (`## Highlights` vs
    `## ✨ Highlights`), so match the heading TEXT, not the literal line."""
    lines = _read(path).splitlines()
    start = next((i for i, line in enumerate(lines) if line.startswith("#")
                  and line.strip().lstrip("#").strip().lstrip("✨ ") == "Highlights"), None)
    assert start is not None, f"{path} has no Highlights heading"
    out = []
    for line in lines[start + 1:]:
        if line.startswith("#"):
            break
        out.append(line)
    return " ".join(" ".join(out).split())


# --- R:UNBACKEDCLAIM ------------------------------------------------------------------------

def test_no_front_door_claim_contradicts_the_benchmark():
    assert BENCH.is_file(), "the cited benchmark report is missing — the claim cannot be checked"
    assert "retracted" in _read(BENCH).lower(), \
        "the report no longer carries the retraction this guard is anchored to"
    banned = re.compile(r"the cheap(?:er|est)? option|cheaper than|cheapest|"
                        r"lowest[- ]cost|costs? less than", re.I)
    for path in READMES:
        flat = _highlights(path)
        hit = banned.search(flat)
        assert not hit, (f"{path} asserts a cost advantage the repo's own benchmark retracts: "
                         f"…{flat[max(0, hit.start() - 90):hit.end() + 90]}…")


def test_the_trust_claim_names_what_backs_it():
    for path in READMES:
        assert re.search(r"seal|evidence|verdict", _highlights(path), re.I), \
            f"{path}: Highlights no longer says what the trust rests on"


def test_the_measured_claim_carries_its_provenance():
    for path in READMES:
        flat = _highlights(path)
        m = re.search(r"Measured[^.]*\.", flat)
        assert m, f"{path}: the measured claim is gone — if it was cut, cut this check with it"
        window = flat[m.start():m.start() + 320]
        assert re.search(r"n\s*=\s*\d", window), f"{path}: no sample size beside the claim"
        assert re.search(r"\b\d+\.\d+(\.\d+)?\b", window), \
            f"{path}: no version beside the claim"


# --- the ladder -----------------------------------------------------------------------------

def test_the_readme_shows_the_size_ladder_before_install():
    text = _read(PKG / "README.md")
    assert "## Install" in text, "the install section moved — this check's ordering anchor is gone"
    before = text.split("## Install", 1)[0]
    for rung in ("Quick", "Task", "Explore", "Milestone"):
        assert rung in before, f"the ladder never names the `{rung}` lane before Install"
    assert re.search(r"no node|never create a node|without a node", before, re.I), \
        "the ladder must state that most changes never create a task file"
    assert before.index("## Highlights") < before.rindex("Quick"), \
        "the ladder must land AFTER Highlights"


# --- R:STALEPROMISE -------------------------------------------------------------------------

def test_no_front_door_counts_cli_verbs():
    for path in READMES + QUICKSTARTS:
        hit = re.search(r"\b\d+[- ]verbs?\b", _read(path))
        assert not hit, f"{path} still counts CLI verbs ({hit.group(0)}) — 4.0 has no CLI"


def test_no_front_door_promises_an_approval_step():
    banned = re.compile(r"approve once|one approval|single approval|human freeze|"
                        r"you approve (?:the|each|once)", re.I)
    for path in READMES + QUICKSTARTS:
        hit = banned.search(_read(path))
        assert not hit, (f"{path} promises an approval step 4.0 does not have "
                         f"(`{hit.group(0)}`) — the human reviews after, from the report")


# --- the evidence stays the evidence --------------------------------------------------------

def test_the_benchmark_report_is_untouched():
    """The cheapest way to make a front-door claim true is to edit the evidence it contradicts."""
    rel = BENCH.relative_to(ROOT)
    head = subprocess.run(["git", "show", f"HEAD:{rel.as_posix()}"],
                          cwd=str(ROOT), capture_output=True)
    assert head.returncode == 0, f"{rel} is not tracked — the report cannot be held to its form"
    assert head.stdout == BENCH.read_bytes(), \
        f"{rel} was edited — the repair for a refuted claim is to change the CLAIM, never the data"
    text = _read(BENCH)
    assert "retracted" in text.lower() and "spec-kit is cheaper" in text, \
        "the report no longer states the finding the README defers to"


def test_the_migration_page_cites_evidence_that_exists():
    """Every benchmark file the 4.0 cost argument links to is a real file in this repo."""
    cited = re.findall(r"github\.com/pilotspace/ADD/blob/main/(benchmark/[\w./-]+\.md)",
                       _read(MIGRATION))
    assert cited, "the migration page states the cost case with no in-repo citation"
    missing = [c for c in cited if not (ROOT / c).is_file()]
    assert not missing, f"the migration page cites benchmark files that do not exist: {missing}"
