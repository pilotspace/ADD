"""Red suite for `release-stamp` — add release binds a tag's tree to the receipts that verified it.

A PASS proves a source state and a receipt names the commit it observed; nothing said which tree
a tag shipped. `add release <tag> --milestone m` appends `act: release` to a done milestone
after proving, with read-only git, that the tag's tree holds every scope blob the members' gated
receipts recorded (R:UNANCHORED otherwise). `--artifact` and `--build` are recorded as handed.
The engine never tags, publishes or deploys (R:OUTWARD).

Driven as `.add/tasks/release-stamp.md` under milestone `loop-that-closes`.
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

DIMS = ("who", "which", "when", "absent", "order", "experience")
JUNIT = "<testsuite><testcase classname='t' name='test_only_own_rows'/></testsuite>"


def git(*args, cwd):
    return subprocess.run(["git", "-c", "user.email=t@e.c", "-c", "user.name=T", *args],
                          cwd=str(cwd), capture_output=True, text=True, check=True).stdout.strip()


def _authored(root, slug, **fields):
    cid, _ = add.new(root, "Task", slug, title=slug, **fields)
    p = root / cid.lstrip("/")
    t = p.read_text(encoding="utf-8")
    t = t.replace("- S1 <the surface this publishes — an endpoint, function, or section>", "- S1 the lister")
    t = t.replace("goal: <one line>", "goal: the lister lists only the caller's rows.")
    t = re.sub(r"## RULES\n<must>\n.*?\n</must>", "## RULES\n<must>\n- M1 the lister returns only the caller's rows\n</must>", t, flags=re.S)
    t = re.sub(r"<reject>\n.*?\n</reject>", '<reject>\n- R:R1 thing 1 happens -> "R1"\n</reject>', t, flags=re.S)
    lines = "".join(f"- A{i} [{d}] covers: S1 · the request does not say thing {i}; taking reading {i} -> cost {i}\n" for i, d in enumerate(DIMS, 1))
    t = re.sub(r"## ASSUMPTIONS\n.*?\nevery `gives:`", "## ASSUMPTIONS\n" + lines + "every `gives:`", t, flags=re.S)
    t = re.sub(r"## CHECKS\n.*?(?=\n## )", "## CHECKS\n- test_only_own_rows · covers: M1, R:R1 · acceptance · proves isolation\nred-first: every check MUST fail first.\n", t, flags=re.S)
    t = re.sub(r"## PLAN\n.*?\n\n", "## PLAN\ncontract: the lister\nregression: none · fixture\n\n", t, flags=re.S)
    p.write_text(t, encoding="utf-8")
    return cid


def _done_task(root, bundle, slug, scope=("src/a.py",)):
    """Freeze → brief → narrow receipt → gate PASS: a `done` task at a process floor."""
    cid = _authored(bundle, slug, sensitivity="mechanical", milestone="m", scope=list(scope))
    assert add.freeze(bundle, cid, by="plan")[0] is not None
    add.brief_stamp(bundle, cid)
    report = root / f"{slug}.xml"
    assert add.run(bundle, cid, [sys.executable, "-c", f"open({str(report)!r},'w').write({JUNIT!r})"], cwd=root, junit=report)["receipt"]["exit"] == 0
    node, note = add.gate(bundle, cid, "PASS", by="plan")
    assert node is not None, note
    return cid


def _mark_done(bundle, mcid):
    p = bundle / mcid.lstrip("/")
    n = add.read(p, "T2")
    add.write(p, f"---\n{add.set_key(n['raw'], 'status', 'done')}\n---\n{n['body']}")


@pytest.fixture
def released(tmp_path):
    """A git repo with a done milestone `m`, one done task anchored to a committed scope file, tag v1."""
    git("init", "-q", cwd=tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x = 1\n")
    git("add", "src/a.py", cwd=tmp_path)
    git("commit", "-q", "-m", "one", cwd=tmp_path)
    bundle = tmp_path / ".add"
    add.init(bundle, "code", "P")
    mcid, _ = add.new(bundle, "Milestone", "m", title="m", goal="ship")
    t = _done_task(tmp_path, bundle, "t")
    _mark_done(bundle, mcid)
    git("add", "-A", cwd=tmp_path)
    git("commit", "-q", "-m", "bundle", cwd=tmp_path)
    git("tag", "v1", cwd=tmp_path)
    return tmp_path, bundle, mcid, t



def _reopen_in_order(bundle, mcid, cid, to="build", reason="unmet"):
    """`reopen` through the order successor-not-reopen made legal (R:CLOSEDHISTORY refuses a reopen
    inside a CLOSED milestone). The state these checks are about — a member reopened AFTER its
    closing gate, in a milestone that is done by release time — is unchanged; only the order that
    reaches it is: reopen while the milestone is still active, then close it again."""
    p = bundle / mcid.lstrip("/")
    was = (add.read(p, "T2")["fm"] or {}).get("status")
    for status in ("active", was):
        if status == "active":
            n = add.read(p, "T2")
            add.write(p, f"---\n{add.set_key(n['raw'], 'status', 'active')}\n---\n{n['body']}")
            out = add.reopen(bundle, cid, to, reason)
        else:
            n = add.read(p, "T2")
            add.write(p, f"---\n{add.set_key(n['raw'], 'status', status)}\n---\n{n['body']}")
    return out


def _stamps(bundle, cid):
    return [s for s in add.scan(bundle)[cid]["fm"]["verified"] if s.get("act") == "release"]


def test_release_stamps_a_done_milestone_anchored_to_the_tag(released):
    """covers: M1, M5, E1 — stamp keys, tree sha, receipt cid; status --all and show render it."""
    root, bundle, mcid, t = released
    stamps, note = add.release(bundle, "v1", ["m"], by="Tin")
    assert stamps, note
    st = _stamps(bundle, mcid)
    assert len(st) == 1 and st[0]["tag"] == "v1" and st[0]["authority"] == "process"
    assert st[0]["tree"] == git("rev-parse", "v1^{tree}", cwd=root)
    assert "/tasks/t.d/runs/1.md" in str(st[0]["receipts"])
    assert "artifact" not in st[0] and "build" not in st[0]
    assert "v1" in add.status(bundle, all=True), "status --all does not name the tag on the released row"
    _, out = add.show(bundle, "m")
    assert "act: release" in str(out) and "v1" in str(out)
    add.release(bundle, "v1", ["m"], by="Tin")
    assert len(_stamps(bundle, mcid)) == 2, "a second release did not append"


def test_release_refuses_a_tree_that_moved_after_the_receipt(released):
    """covers: M3, R:UNANCHORED, E2 — the task, the path and both blobs, no stamp."""
    root, bundle, mcid, t = released
    (root / "src" / "a.py").write_text("x = 2\n")
    git("commit", "-q", "-am", "moved", cwd=root)
    git("tag", "v2", cwd=root)
    stamps, note = add.release(bundle, "v2", ["m"], by="Tin")
    assert stamps is None and "R:UNANCHORED" in note, f"released a tree the receipt never saw: {note!r}"
    assert "/tasks/t.md" in note and "src/a.py" in note and len(re.findall(r"[0-9a-f]{40}", note)) >= 2, note
    assert not _stamps(bundle, mcid)


def test_release_refuses_not_done_and_no_such_tag(released):
    """covers: M2, E3 — both refusals by name."""
    root, bundle, mcid, t = released
    stamps, note = add.release(bundle, "v9", ["m"], by="Tin")
    assert stamps is None and "R:NOSUCHTAG" in note and "v9" in note
    active, _ = add.new(bundle, "Milestone", "open", title="open", goal="later")
    stamps, note = add.release(bundle, "v1", ["open"], by="Tin")
    assert stamps is None and "R:NOTDONE" in note and "open" in note
    assert not _stamps(bundle, mcid)


def test_artifact_and_build_are_recorded_as_handed(released):
    """covers: M1, R:PROVENANCEJUDGED, E4 — verbatim when given, absent otherwise, never checked."""
    root, bundle, mcid, t = released
    stamps, note = add.release(bundle, "v1", ["m"], by="Tin", artifact="api@sha256:not-a-real-digest", build="gha://repo/run/1")
    assert stamps, note
    st = _stamps(bundle, mcid)[-1]
    assert st["artifact"] == "api@sha256:not-a-real-digest" and st["build"] == "gha://repo/run/1"


def test_unanchorable_and_receiptless_members(released):
    """covers: M3, A4, E5 — a digest-less receipt refuses by name; an explore is skipped by name."""
    root, bundle, mcid, t = released
    ex, _ = add.new(bundle, "Task", "ex", title="ex", kind="explore", milestone="m")
    p = bundle / "tasks" / "ex.md"
    n = add.read(p, "T2")
    add.write(p, f"---\n{add.set_key(n['raw'], 'status', 'done')}\n---\n{n['body']}")
    stamps, note = add.release(bundle, "v1", ["m"], by="Tin")
    assert stamps and "ex" in note and "skipped" in note, f"a receiptless explore was not named as skipped: {note!r}"
    # a done task whose receipt carries no digest: strip the digest from the receipt on disk
    r = bundle / "tasks" / "t.d" / "runs" / "1.md"
    r.write_text(re.sub(r"  scope_digest:\n(    - .*\n)+", "", r.read_text()).replace("freshness: content", "freshness: mtime"))
    stamps, note = add.release(bundle, "v1", ["m"], by="Tin")
    assert stamps is None and "R:UNANCHORED" in note and "/tasks/t.md" in note and "digest" in note, note


def test_floor_receipt_never_anchors(released):
    """covers: A2 (probe) — a later floor receipt with a wider digest leaves the anchor on the narrow one."""
    root, bundle, mcid, t = released
    (root / "src" / "b.py").write_text("y = 1\n")
    add.run(bundle, t, [sys.executable, "-c", "pass"], cwd=root, floor=True)
    stamps, note = add.release(bundle, "v1", ["m"], by="Tin")
    assert stamps, f"a floor receipt recorded after the gate moved the anchor: {note!r}"
    assert "/tasks/t.d/runs/1.md" in str(_stamps(bundle, mcid)[-1]["receipts"])


def test_release_calls_git_read_only(released, monkeypatch):
    """covers: M4, R:OUTWARD, E6 — the spy saw only rev-parse and ls-tree."""
    root, bundle, mcid, t = released
    seen = []
    real = add._git

    def spy(r, *args, **kw):
        seen.append(args[0])
        return real(r, *args, **kw)
    monkeypatch.setattr(add, "_git", spy)
    stamps, note = add.release(bundle, "v1", ["m"], by="Tin")
    assert stamps, note
    assert seen and set(seen) <= {"rev-parse", "ls-tree"}, f"release ran git commands beyond read-only: {sorted(set(seen))}"


def test_registries_and_docs_carry_the_verb():
    """covers: M6 — WIRED, README count, docs/13 row, docs/16 §16.5, FORMAT §8.6."""
    cli = (REPO / "tooling" / "cli.py").read_text()
    assert 'add_parser("release"' in cli
    wired = (REPO / "tests" / "engine" / "test_cli.py").read_text()
    assert '"release"' in wired[wired.find("WIRED = {"):wired.find("}", wired.find("WIRED = {"))]
    assert "`release`" in (REPO / "docs" / "13-command-reference.md").read_text()
    assert "add release" in (REPO / "docs" / "16-releasing.md").read_text()
    fmt = (REPO / "FORMAT.md").read_text()
    assert "### §8.6" in fmt
    sec = fmt.split("### §8.6", 1)[1].split("\n## §9", 1)[0]
    for word in ("R:UNANCHORED", "rev-parse", "ls-tree", "artifact", "never"):
        assert word in sec, f"FORMAT §8.6 never says {word}"
    n = len(set(re.findall(r'sub\.add_parser\("([a-z-]+)"', cli)))
    assert f"{n} verbs" in (REPO / "README.md").read_text(), f"README does not count {n} verbs"


def test_anchor_is_the_gated_receipt_not_the_latest_run(released):
    """covers: M3, A2, E7 — found by the T2 refute: the anchor read the latest run, not the gate's."""
    root, bundle, mcid, t = released
    (root / "src" / "a.py").write_text("x = 3\n")                                   # uncommitted edit …
    add.run(bundle, t, [sys.executable, "-c", "raise SystemExit(1)"], cwd=root)     # … then a red narrow run
    stamps, note = add.release(bundle, "v1", ["m"], by="Tin")
    assert stamps, f"a red run after the PASS moved the anchor off the gated receipt: {note!r}"
    st = _stamps(bundle, mcid)[-1]
    assert "/tasks/t.d/runs/1.md" in str(st["receipts"]) and "runs/2.md" not in str(st["receipts"]), st


def test_long_tag_keeps_the_row_bounded(released):
    """covers: M5, E8 — found by the T2 refute: a 78-char tag pushed the row to 158 (R:ROWBLOAT)."""
    root, bundle, mcid, t = released
    p = bundle / mcid.lstrip("/")
    p.write_text(p.read_text().replace("title: m\n", "title: " + "a milestone with a very long title " * 3 + "\n", 1))
    tag = "release/" + "x" * 70
    git("tag", tag, cwd=root)
    assert add.release(bundle, tag, ["m"], by="Tin")[0]
    row = next(l for l in add.status(bundle, all=True).splitlines() if l.startswith("  · m "))
    assert len(row) <= add.ROW_WIDTH, f"{len(row)} > {add.ROW_WIDTH}: {row!r}"
    assert row.endswith(tag[:len(row) - row.rfind(" · ") - 3]) and "release/x" in row, row
    assert "a milestone" in row, "the tag ate the whole title"


def test_anchor_is_the_closing_gate_not_a_later_finding(released):
    """covers: M3, A2, E9 — found by the second T2 refute: a HARD-STOP after done moved the anchor."""
    root, bundle, mcid, t = released
    (root / "src" / "a.py").write_text("x = 9\n")
    git("commit", "-q", "-am", "moved", cwd=root)
    git("tag", "v2", cwd=root)
    add.run(bundle, t, [sys.executable, "-c", "raise SystemExit(1)"], cwd=root)
    node, note = add.gate(bundle, t, "HARD-STOP", by="incident", reason="a finding on the shipped code")
    assert node is not None, note
    stamps, note = add.release(bundle, "v1", ["m"], by="Tin")
    assert stamps and "/tasks/t.d/runs/1.md" in str(_stamps(bundle, mcid)[-1]["receipts"]), f"the PASS'd tree no longer anchors: {note!r}"
    stamps, note = add.release(bundle, "v2", ["m"], by="Tin")
    assert stamps is None and "R:UNANCHORED" in note, f"the finding's tree was stamped: {note!r}"


def test_empty_anchor_refuses_and_names_the_not_done(released):
    """covers: M3, A6, E10 — a reopened-only or memberless milestone refuses by name, never `0 receipts`."""
    root, bundle, mcid, t = released
    assert _reopen_in_order(bundle, mcid, t)[0]
    stamps, note = add.release(bundle, "v1", ["m"], by="Tin")
    assert stamps is None and "R:UNANCHORED" in note and "/tasks/t.md" in note and "build" in note, note
    e, _ = add.new(bundle, "Milestone", "e", title="e", goal="nothing")
    _mark_done(bundle, e)
    stamps, note = add.release(bundle, "v1", ["e"], by="Tin")
    assert stamps is None and "R:UNANCHORED" in note and "no member" in note, note


def test_success_note_names_not_done_members(released):
    """covers: M3, A6, E11 — found by the third T2 refute: the success path dropped the not-done list."""
    root, bundle, mcid, t = released
    u = _done_task(root, bundle, "u")
    assert _reopen_in_order(bundle, mcid, u)[0]
    stamps, note = add.release(bundle, "v1", ["m"], by="Tin")
    assert stamps, note
    assert "not anchored" in note and "/tasks/u.md (build)" in note, f"the reopened member was not named: {note!r}"
    assert "/tasks/u.d" not in str(_stamps(bundle, mcid)[-1]["receipts"]), "a not-done member anchored"


def test_closing_gate_must_postdate_the_reopen(released):
    """covers: M3, E12 — a reopened-then-hand-marked member is skipped, never anchored on the reset verdict."""
    root, bundle, mcid, t = released
    assert _reopen_in_order(bundle, mcid, t)[0]
    p = bundle / t.lstrip("/")
    n = add.read(p, "T2")
    add.write(p, f"---\n{add.set_key(n['raw'], 'status', 'done')}\n---\n{n['body']}")
    stamps, note = add.release(bundle, "v1", ["m"], by="Tin")
    assert stamps is None and "R:UNANCHORED" in note and "no member anchors" in note, note


def test_a_cited_receipt_must_be_the_members_own(released):
    """Direct follow-up to the fourth T2 read: a gate stamp hand-edited to cite another task's receipt
    (or a path outside the bundle) anchored the member on a digest it never earned."""
    root, bundle, mcid, t = released
    p = bundle / t.lstrip("/")
    for foreign in ("/tasks/u.d/runs/1.md", "/../../../../etc/hosts"):
        p.write_text(p.read_text().replace("receipt: /tasks/t.d/runs/1.md", f"receipt: {foreign}"))
        stamps, note = add.release(bundle, "v1", ["m"], by="Tin")
        assert stamps is None and "R:UNANCHORED" in note and "own" in note and foreign in note, f"{foreign}: {note!r}"
        p.write_text(p.read_text().replace(f"receipt: {foreign}", "receipt: /tasks/t.d/runs/1.md"))
