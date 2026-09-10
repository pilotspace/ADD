"""Red suite for `/tasks/refute-tier-and-changed.md` — the refute stamp says WHICH TIER read the
green and WHAT ITS PROBES CHANGED.

dogfood-and-measure F2/F4: both refutes on evidence-over-tests were T1 with the tier written inside
`--by`, and the one probe that changed the build was stamped `held` because no frozen rule forbade
it — so the memo's `--found` trigger read 0 where the honest count was 1 of 6. `--tier` and
`--changed` make both countable from `verified[]` alone. The engine records the CLAIM (a builder
may still write T2); the gate reads neither key (notary law 3).
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

BODY = """## CARD
goal: a task with a green worth refuting
beat: build · next: add run

## RULES
<must>
- M1 the first rule
</must>
<reject>
- R:BAD something forbidden -> "BAD"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the request does not say who; taking anyone -> cost
- A2 [which] covers: S1 · n/a · fixture
- A3 [when] covers: S1 · n/a · fixture
- A4 [absent] covers: S1 · n/a · fixture
- A5 [order] covers: S1 · n/a · fixture
- A6 [experience] covers: S1 · n/a · fixture

## CHECKS
- test_one · covers: M1 · acceptance · the rule
- test_two · covers: R:BAD · acceptance · the reject
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>
"""


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)


def _bundle(tmp_path, slug="tiered"):
    git("init", "-q", cwd=tmp_path)
    git("config", "user.email", "t@example.com", cwd=tmp_path)
    git("config", "user.name", "T", cwd=tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "service.py").write_text("def book():\n    return True\n")
    root = tmp_path / ".add"
    add.init(root, "code", "Tiered")
    cid, _ = add.new(root, "Task", slug, title=f"{slug} task", depth="standard", sensitivity="data",
                     scope=["src/service.py"])
    path = root / cid.lstrip("/")
    n = add.read(path, "T2")
    raw = n["raw"].replace("  - S1 <the surface this publishes — an endpoint, function, or section>",
                           "  - S1 book()")
    add.write(path, f"---\n{raw}\n---\n{BODY}")
    ok, note = add.freeze(root, cid, "human:tindang")
    assert ok, note
    add.brief_stamp(root, cid)
    git("add", "-A", cwd=tmp_path)
    git("commit", "-q", "-m", slug, cwd=tmp_path)
    xml = tmp_path / "r.xml"
    cases = "".join(f'<testcase classname="c" name="{i}"/>' for i in ("test_one", "test_two"))
    doc = f"<testsuites><testsuite>{cases}</testsuite></testsuites>"
    add.run(root, cid, [sys.executable, "-c", f"open({str(xml)!r},'w').write({doc!r})"],
            cwd=tmp_path, junit=xml)
    return cid


def _stamps(repo, cid, act="refute"):
    fm = add.read(repo / ".add" / cid.lstrip("/"), "T0")["fm"] or {}
    return [s for s in (fm.get("verified") or []) if isinstance(s, dict) and s.get("act") == act]


def _evidence(repo, cid):
    body = add.read(repo / ".add" / cid.lstrip("/"), "T2")["body"]
    return add._section_of(body, "EVIDENCE")


def _cli(repo, *args):
    return subprocess.run([sys.executable, str(repo / ".add/tooling/cli.py"), *args],
                          cwd=str(repo), capture_output=True, text=True)


@pytest.fixture
def repo(tmp_path):
    cid = _bundle(tmp_path)
    return tmp_path, cid


# --- M1 / M2: the two keys ---------------------------------------------------------------------

def test_tier_recorded_when_given_and_absent_otherwise(repo):
    """covers: M1 — `--tier T2` → `tier: T2`; no flag → no key. Recorded as given, never invented."""
    tmp, cid = repo
    stamp, note = add.refute(tmp / ".add", cid, by="advisor:method-steward", held=True, probes=2, tier="T2")
    assert stamp, note
    s = _stamps(tmp, cid)[-1]
    assert s.get("tier") == "T2", s
    stamp, note = add.refute(tmp / ".add", cid, by="builder", held=True, probes=1)
    assert stamp, note
    s = _stamps(tmp, cid)[-1]
    assert "tier" not in s, s


def test_changed_recorded_oneline_with_either_outcome(repo):
    """covers: M2 — held+changed and found+changed both carry it, normalized like `note:`; "" → no key."""
    tmp, cid = repo
    stamp, note = add.refute(tmp / ".add", cid, by="v", held=True, probes=3,
                             changed='argparse now\nrefuses a "negative" count')
    assert stamp, note
    s = _stamps(tmp, cid)[-1]
    assert s.get("changed") == "argparse now refuses a 'negative' count", s
    stamp, note = add.refute(tmp / ".add", cid, by="v", held=False, finding="amount == 0",
                             changed="the spec gained an edge")
    assert stamp, note
    s = _stamps(tmp, cid)[-1]
    assert s.get("outcome") == "refuted" and s.get("changed") == "the spec gained an edge", s
    stamp, note = add.refute(tmp / ".add", cid, by="v", held=True, probes=0, changed="   ")
    assert stamp, note
    assert "changed" not in _stamps(tmp, cid)[-1]


def test_cli_exposes_tier_choices_and_changed(repo):
    """covers: M1, M2, R:BADTIER — the front door: `--tier` with choices T1 T2 T3, `--changed`; T4 exits 2."""
    tmp, cid = repo
    r = _cli(tmp, "refute", "--help")
    assert "--tier" in r.stdout and "--changed" in r.stdout, r.stdout
    assert re.search(r"\{T1,T2,T3\}", r.stdout), r.stdout
    r = _cli(tmp, "refute", "tiered", "--by", "v", "--held", "--tier", "T4")
    assert r.returncode == 2, (r.returncode, r.stderr)
    assert _stamps(tmp, cid) == []
    r = _cli(tmp, "refute", "tiered", "--by", "v", "--held", "--probes", "2", "--tier", "T2",
             "--changed", "one probe moved a boundary")
    assert r.returncode == 0, r.stdout + r.stderr
    s = _stamps(tmp, cid)[-1]
    assert s.get("tier") == "T2" and s.get("changed") == "one probe moved a boundary", s


# --- R:BADTIER / E2 / A2 ------------------------------------------------------------------------

def test_bad_tier_refused_at_library_no_stamp(repo):
    """covers: R:BADTIER, E2, A2 — T4 and t2 are refused naming T1–T3; verified[] unchanged."""
    tmp, cid = repo
    before = len((add.read(tmp / ".add" / cid.lstrip("/"), "T0")["fm"] or {}).get("verified") or [])
    for bad in ("T4", "t2", "T0", "fresh", " T2 "):   # the padded form: the T2 refute found the two doors disagreeing
        stamp, note = add.refute(tmp / ".add", cid, by="v", held=True, tier=bad)
        assert stamp is None and "BADTIER" in note, (bad, note)
        assert "T1" in note and "T3" in note, note
    after = len((add.read(tmp / ".add" / cid.lstrip("/"), "T0")["fm"] or {}).get("verified") or [])
    assert before == after


# --- M3: the view ------------------------------------------------------------------------------

def test_evidence_line_renders_tier_and_changed(repo):
    """covers: M3 — the `refute:` line carries `tier T2` and `changed: …`; without them neither token."""
    tmp, cid = repo
    add.refute(tmp / ".add", cid, by="v", held=True, probes=1)
    ev = _evidence(tmp, cid)
    line = next(l for l in ev.splitlines() if l.startswith("refute:"))
    assert " tier T" not in line and "changed:" not in line, line   # the slug "tiered" itself carries the substring
    add.refute(tmp / ".add", cid, by="advisor:x", held=True, probes=3, tier="T2",
               changed="argparse refuses a negative count", note="P1 boundary · P2 compose")
    ev = _evidence(tmp, cid)
    line = next(l for l in ev.splitlines() if l.startswith("refute:"))
    assert "tier T2" in line and "changed: argparse refuses a negative count" in line, line
    assert "P1 boundary" in line, line


# --- R:JUDGED / E1: the gate reads neither -----------------------------------------------------

def test_gate_rung_indifferent_to_tier_and_changed(repo):
    """covers: R:JUDGED, E1 — a held refute carrying `changed:` passes the rung; `_refute_of` names neither key."""
    tmp, cid = repo
    add.refute(tmp / ".add", cid, by="advisor:x", held=True, probes=2, tier="T2",
               changed="argparse now refuses a negative count")
    ok, note = add.gate(tmp / ".add", cid, "PASS", "plan:t2")
    assert ok, note
    src = Path(add.__file__).read_text(encoding="utf-8")
    m = re.search(r"def _refute_of\(.*?\n(?=\n\ndef |\n\n# )", src, re.S)
    assert m, "_refute_of not found"
    assert "tier" not in m.group(0) and "changed" not in m.group(0), m.group(0)


# --- M4: the prose ------------------------------------------------------------------------------

def test_format_docs_and_cookbook_name_both_flags():
    """covers: M4 — FORMAT §8.4 · docs 13 · docs 05 · the cookbook line in all three SKILL.md trees."""
    fmt = (REPO / "FORMAT.md").read_text(encoding="utf-8")
    sec = fmt.split("### §8.4", 1)[1].split("\n### ", 1)[0]
    assert "tier:" in sec and "changed:" in sec, sec
    assert re.search(r"reads neither|never reads", sec), sec
    d13 = (REPO / "docs" / "13-command-reference.md").read_text(encoding="utf-8")
    row = next(l for l in d13.splitlines() if l.startswith("| `refute`"))
    assert "--tier" in row and "--changed" in row, row
    d05 = (REPO / "docs" / "05-verify.md").read_text(encoding="utf-8")
    assert "--tier" in d05 and "--changed" in d05
    for p in (REPO / "skill/add/SKILL.md",
              REPO.parent / ".claude/skills/add/SKILL.md",
              REPO / "src/add_method/_bundled/skill/add/SKILL.md"):
        line = next(l for l in p.read_text(encoding="utf-8").splitlines() if l.startswith("add refute "))
        assert "--tier" in line, (p, line)
