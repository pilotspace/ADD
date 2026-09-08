"""Red suite for `deltas-drain-at-close` — the drain, and the promotion it enables.

`rejected` has been one of three statuses in a frozen grammar since the grammar was frozen,
and no command could ever produce it. `fold` flipped a tag and wrote nothing anywhere else,
so 75 lessons became 75 retagged lines and never once a decision. This task connects `learn`
to `brief` and puts the drain at the seam the human already owns — the milestone close.

The window is the point: it is anchored on the CLOSING milestone's creation date, so the
existing backlog can never block a close (R:BACKLOGBLOCK). One test per Must / Reject, plus
every filled edge and every probed assumption — the gate binds all of them (M31, M38).
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

BIND = "Decisions that bind"


def _spec(root, lens="method"):
    return Path(root) / "specs" / f"{lens}.md"


def _decisions(root, lens="method"):
    return add._section(_spec(root, lens).read_text().split("---", 2)[2], "decisions-that-bind")


@pytest.fixture
def bundle(tmp_path):
    add.init(tmp_path, "code", "Drain")
    return tmp_path


def _file(root, *lessons, lens="method"):
    for text in lessons:
        add.learn(root, lens, text, evidence="/tasks/t.md")


# ------------------------------------------------------------------ S1 · reject


def test_reject_is_the_first_verb_for_rejected(bundle):
    """covers: M1, A4, E5 — one matcher, two verdicts, and R:NOMATCH is unchanged."""
    _file(bundle, "a wrong lesson about gates", "a right lesson about gates")
    ok, note = add.fold(bundle, "method", "wrong lesson", reject=True)
    assert ok, note
    raw = _spec(bundle).read_text()
    assert "· rejected · " in raw, f"reject did not retag:\n{raw}"
    assert raw.count("· rejected ·") == 1, "reject retagged more than it matched"
    # A4: the reject and the fold see ONE set — the same match retags the same line.
    ok, _ = add.fold(bundle, "method", "right lesson")
    assert ok and "· folded · " in _spec(bundle).read_text()
    assert add.open_delta_count(_spec(bundle).read_text()) == 0, \
        "a rejected delta is still counted as open"
    # E5: a reject matching nothing refuses exactly as a bare fold does.
    ok, note = add.fold(bundle, "method", "no such lesson", reject=True)
    assert not ok and "R:NOMATCH" in note, note


# ------------------------------------------------------------------ S2 · bind


def test_bind_writes_a_decision(bundle):
    """covers: M2, A7, A10, E1 — one write, every id cited, section created when absent."""
    _file(bundle, "gates bind ids one", "gates bind ids two", "gates bind ids three")
    spec = _spec(bundle)
    spec.write_text(spec.read_text().replace(f"## {BIND}\n", ""))   # A10: section absent
    ok, note = add.fold(bundle, "method", "gates bind ids",
                        bind="every referent a check names is bound at the gate")
    assert ok, note
    decisions = _decisions(bundle)
    assert "every referent a check names is bound at the gate" in decisions, decisions
    for did in ("M1", "M2", "M3"):                                   # E1: all three cited
        assert f"#{did}" in decisions, f"{did} was retagged and not cited:\n{decisions}"
    assert _spec(bundle).read_text().count("· folded ·") == 3, "A7: the retag did not land"


def test_bind_drops_the_scaffold_and_keeps_real_decisions(bundle):
    """covers: M2, R:BINDLOSS, A11, E2 — prepended, and nothing already there is lost."""
    _file(bundle, "first lesson", "second lesson")
    add.fold(bundle, "method", "first lesson", bind="an older decision that already bound")
    before = _decisions(bundle)
    assert "<" not in before, f"the scaffold line survived a real decision:\n{before}"

    add.fold(bundle, "method", "second lesson", bind="a newer decision")
    after = _decisions(bundle)
    assert "an older decision that already bound" in after, "R:BINDLOSS — an existing decision went"
    assert after.index("a newer decision") < after.index("an older decision"), \
        f"A11 — the newer decision was appended, not prepended:\n{after}"


def test_reject_and_bind_together_refuse(bundle):
    """covers: M3, R:REJECTBINDS — a lesson judged wrong cannot also bind."""
    _file(bundle, "a lesson")
    before = _spec(bundle).read_text()
    ok, note = add.fold(bundle, "method", "a lesson", reject=True, bind="but also a decision")
    assert not ok and "REJECTBINDS" in note, note
    assert _spec(bundle).read_text() == before, "a refused call still wrote to the spec"


def test_bound_decision_reaches_the_brief(bundle):
    """covers: M2, A1 — the whole point: `brief` stops saying no decision binds."""
    add.new(bundle, "Task", "t", title="A task")
    _file(bundle, "a lesson worth binding")
    assert 'id="specs/method#decisions-that-bind" unauthored="true"' in \
        add.brief(bundle, "/tasks/t.md")["text"], "the fixture already reported a bound decision"
    add.fold(bundle, "method", "worth binding", bind="a decision the brief must carry")
    xml = add.brief(bundle, "/tasks/t.md")["text"]
    assert "a decision the brief must carry" in xml, f"the decision never reached the brief:\n{xml[:400]}"


# ------------------------------------------------------------------ S3 · the rung


def _milestone(root, slug, created, exit_checked=True, tasks=()):
    add.new(root, "Milestone", slug, title=slug)
    path = Path(root) / "milestones" / f"{slug}.md"
    s = path.read_text()
    s = s.replace("goal: <one line>", "goal: close cleanly")
    s = s.replace("why: <why this milestone exists — required>", "why: to prove the rung")
    s = s.replace("- [ ] <criterion>   (← <task>)",
                  f"- [{'x' if exit_checked else ' '}] the one criterion   (a task)")
    s = s.replace("evidence: <one row per task>", "evidence: recorded")
    if created is None:
        s = "\n".join(l for l in s.splitlines() if not l.startswith("generated:")) + "\n"
    else:
        s = add.set_key(s, "generated", f"{{ by: add/test, at: {created} }}") \
            if "generated:" in s.split("---")[1] else s
        s = s.replace("at: " + s.split("at: ")[1].split(" ")[0], "at: " + created, 1)
    path.write_text(s)
    return f"/milestones/{slug}.md"


def _date_a_delta(root, match, when, lens="method"):
    """Rewrite one delta's `valid_from` — the filing date the window reads."""
    p = _spec(root, lens)
    out = []
    for line in p.read_text().splitlines(keepends=True):
        if match in line and "· open ·" in line:
            head = line[line.index("[") + 1:line.index("]")]
            fields = [f.strip() for f in head.split("·")]
            fields[3] = when
            line = line.replace(head, " · ".join(fields), 1)
        out.append(line)
    p.write_text("".join(out))


def test_close_refuses_undrained_lessons(bundle):
    """covers: M4, A2, A14 — the refusal names the address and the way through."""
    cid = _milestone(bundle, "m-open", "2026-09-01")
    _file(bundle, "a lesson filed during the milestone")
    _date_a_delta(bundle, "during the milestone", "2026-09-03")
    ok, note = add.milestone_done(bundle, cid)
    assert not ok and "UNDRAINED" in note, note
    assert "/specs/method.md#M1" in note, f"the refusal named no address:\n{note}"
    for flag in ("fold", "--reject", "--bind"):
        assert flag in note, f"the refusal never named `{flag}`:\n{note}"


def test_close_never_blocks_on_the_backlog(bundle):
    """covers: M5, R:BACKLOGBLOCK, A8, A13 — 75 open lessons must never block a close."""
    cid = _milestone(bundle, "m-late", "2026-09-05")
    _file(bundle, "an older lesson", "an undated legacy lesson")
    _date_a_delta(bundle, "an older lesson", "2026-08-01")
    spec = _spec(bundle)                                    # A8: a LEGACY two-field head
    spec.write_text(spec.read_text().replace(
        "[ADD · M2 · open · ", "[ADD · open] ").replace("] an undated legacy", " an undated legacy"))
    # ARM IT FIRST. Asserting that two lessons do NOT block is worthless while nothing can
    # block at all: prove the rung fires in this very bundle, then withdraw its subject.
    _file(bundle, "an in-window lesson")
    _date_a_delta(bundle, "in-window lesson", "2026-09-06")
    armed, note = add.milestone_done(bundle, cid)
    assert not armed and "UNDRAINED" in note, f"the rung never fires, so this proves nothing:\n{note}"
    add.fold(bundle, "method", "in-window lesson")

    ok, note = add.milestone_done(bundle, cid)
    assert ok, f"the backlog blocked a close (R:BACKLOGBLOCK):\n{note}"


def test_same_day_delta_is_inside_the_window(bundle):
    """covers: A6, E3 — created and taught on one day is the common case, not an edge."""
    cid = _milestone(bundle, "m-sameday", "2026-09-02")
    _file(bundle, "a same day lesson")
    _date_a_delta(bundle, "same day lesson", "2026-09-02")
    ok, note = add.milestone_done(bundle, cid)
    assert not ok and "UNDRAINED" in note, f"the boundary was exclusive:\n{note}"


def test_unreadable_anchor_skips_and_says_so(bundle):
    """covers: M6, R:SILENTSKIP, A9, E4 — a rung that did not run must say so."""
    cid = _milestone(bundle, "m-noanchor", None)
    _file(bundle, "a lesson with nothing to compare against")
    ok, note = add.milestone_done(bundle, cid)
    assert ok, note
    assert "drain" in note.lower(), f"the close hid a rung it never ran (R:SILENTSKIP):\n{note}"


def test_the_rung_runs_after_the_goal_gate(bundle):
    """covers: M7, A12 — never report the drain while the goal is still unmet."""
    cid = _milestone(bundle, "m-unmet", "2026-09-01", exit_checked=False)
    _file(bundle, "an undrained lesson")
    _date_a_delta(bundle, "undrained lesson", "2026-09-03")
    ok, note = add.milestone_done(bundle, cid)
    assert not ok and "goal_unmet" in note, f"the drain jumped the goal-gate:\n{note}"
    assert "UNDRAINED" not in note, note
    # And the rung WAS armed the whole time — check the box and the same close refuses on it.
    path = Path(bundle) / "milestones" / "m-unmet.md"
    path.write_text(path.read_text().replace("- [ ] the one criterion", "- [x] the one criterion"))
    ok, note = add.milestone_done(bundle, cid)
    assert not ok and "UNDRAINED" in note, \
        f"the goal-gate was merely first because nothing came after it:\n{note}"


def test_anchor_is_the_creation_date(bundle):
    """covers: A3 — creation precedes every stamp, so the drafted second clause is dead."""
    cid = _milestone(bundle, "m-stamped", "2026-09-01")
    assert add.freeze(bundle, cid, by="plan:x", authority="plan")[0], "the fixture never froze"
    fm = add.scan(bundle)[cid]["fm"]
    stamps = [str(e.get("at")) for e in (fm.get("verified") or []) if isinstance(e, dict)]
    assert stamps, "the fixture recorded no stamp, so this proves nothing"
    assert all(s >= "2026-09-01" for s in stamps), \
        f"a stamp predates creation, so the anchor needs the second clause after all: {stamps}"
    assert add.milestone_window_anchor(fm) == "2026-09-01"


# ------------------------------------------------------------------ the shape of the change


def test_the_drain_adds_no_verb(bundle):
    """covers: R:NEWVERB, A15 — two flags and one rung, and no new addressing scheme."""
    cli_src = (REPO / "tooling" / "cli.py").read_text()
    for absent in ('add_parser("drain"', 'add_parser("bind"', 'add_parser("reject"'):
        assert absent not in cli_src, f"a new verb was added: {absent}"
    assert '"--reject"' in cli_src and '"--bind"' in cli_src, "the flags were never wired"
    _file(bundle, "one lesson about substrings")
    ok, _ = add.fold(bundle, "method", "about substrings", bind="a decision")
    assert ok, "A15 — the flags did not take the same substring `fold` takes"
