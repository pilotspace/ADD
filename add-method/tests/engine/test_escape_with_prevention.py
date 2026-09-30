"""Red suite for `escape-with-prevention` — an escaped defect drains only with a why-missed and a bound prevention.

The drain existed (`learn` demands evidence; `fold --bind|--reject` and R:UNDRAINED hold it) but what it
drained was a sentence: a production escape folded with nothing bound to stop the next one. Now
`learn --escape` demands `--why-missed` and `--prevention "<check|monitor|method|rule> → <ref>"`
(R:UNCAUSED), `fold` refuses to fold or bind an escape whose prevention does not resolve
(R:UNPREVENTED), and loop.md classifies observations EXPECTED · RULE_VIOLATION · SPEC_SILENCE.

Driven as `.add/tasks/escape-with-prevention.md` under milestone `loop-that-closes`.
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

TREES = (REPO / "skill" / "add", REPO / "src" / "add_method" / "_bundled" / "skill" / "add",
         REPO.parent / ".claude" / "skills" / "add")


@pytest.fixture
def bundle(tmp_path):
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x = 1\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_x.py").write_text("def test_y(): pass\n")
    b = tmp_path / ".add"
    add.init(b, "code", "P")
    add.new(b, "Task", "t", title="t")
    return b


def _open(bundle, lens="method"):
    return [t for _, _, t in add.deltas(bundle, "open", lens=lens)[0]]


def _line(bundle, needle, lens="method"):
    body = (bundle / "specs" / f"{lens}.md").read_text(encoding="utf-8")
    return next(l for l in body.splitlines() if needle in l)


def test_learn_escape_writes_the_tail(bundle):
    """covers: M1, A5, E1 — the tail lands, in order, after the evidence clause."""
    ok, note = add.learn(bundle, "method", "a cross-tenant read escaped", evidence="/tasks/t.md",
                         escape=True, why_missed="no check for a second tenant",
                         prevention="check → tests/test_x.py::test_y")
    assert ok, note
    line = _line(bundle, "cross-tenant")
    tail = line.split("(evidence: /tasks/t.md)", 1)[1]
    assert tail.strip() == "· escape · why-missed: no check for a second tenant · prevention: check → tests/test_x.py::test_y", repr(line)


@pytest.mark.parametrize("kw, names", [
    (dict(escape=True, why_missed="w"), "--prevention"),
    (dict(escape=True, prevention="check → tests/test_x.py"), "--why-missed"),
    (dict(escape=True, why_missed="w", prevention="alert → tests/test_x.py"), "alert"),
    (dict(escape=True, why_missed="w", prevention="check →"), "ref"),
    (dict(why_missed="w"), "--escape"),
    (dict(prevention="check → tests/test_x.py"), "--escape"),
])
def test_learn_escape_refuses_uncaused_by_name(bundle, kw, names):
    """covers: M1, R:UNCAUSED, E2 — each missing or malformed part named; nothing written."""
    before = (bundle / "specs" / "method.md").read_text()
    ok, note = add.learn(bundle, "method", "an escape", evidence="/tasks/t.md", **kw)
    assert ok is None and "R:UNCAUSED" in note and names in note, f"{kw}: {note!r}"
    assert (bundle / "specs" / "method.md").read_text() == before, "a refused escape wrote something"


def test_fold_refuses_an_unresolvable_prevention(bundle):
    """covers: M2, R:UNPREVENTED, A3, E3 — fold and --bind refuse naming the ref; --reject retags."""
    assert add.learn(bundle, "method", "dangling one", evidence="/tasks/t.md", escape=True,
                     why_missed="w", prevention="rule → /tasks/nope.md")[0]
    for kw in ({}, {"bind": "owner · 2026-12-31 · accepted"}):
        ok, note = add.fold(bundle, "method", "dangling one", **kw)
        assert ok is None and "R:UNPREVENTED" in note and "/tasks/nope.md" in note, f"{kw}: {note!r}"
        assert any("dangling one" in t for t in _open(bundle)), "a refused fold moved the delta"
    ok, note = add.fold(bundle, "method", "dangling one", reject=True)
    assert ok is True, note
    assert not any("dangling one" in t for t in _open(bundle))


@pytest.mark.parametrize("ref, folds", [
    ("/tasks/t.md", True), ("/tasks/t.md#M1", True), ("SELF", True), ("src/a.py", True),
    ("tests/test_x.py::test_y", True), ("https://dash.example/alerts/1", False), ("/tasks/t.md#M9", False),
])
def test_fold_accepts_every_resolvable_form(bundle, ref, folds):
    """covers: M2, A2, E4 — node, fragment, delta id, file, file::name fold; a URL and a missing fragment do not."""
    p = bundle / "tasks" / "t.md"
    t = p.read_text().replace("- M1 <the rule that must hold>", "- M1 the lister returns only the caller's rows")
    p.write_text(t)
    assert add.learn(bundle, "method", "seed lesson", evidence="/tasks/t.md")[0]
    if ref == "SELF":
        ref = "/specs/method.md#" + re.search(r"\[ADD · (M\d+) · open", _line(bundle, "seed lesson")).group(1)
    assert add.learn(bundle, "method", "the escape", evidence="/tasks/t.md", escape=True,
                     why_missed="w", prevention=f"monitor → {ref}")[0]
    ok, note = add.fold(bundle, "method", "the escape")
    assert (ok is True) is folds, f"{ref}: {note!r}"


def test_fold_is_atomic_over_many_matches(bundle):
    """covers: M3, E5 — one dangling prevention leaves every match open."""
    assert add.learn(bundle, "method", "shared word alpha", evidence="/tasks/t.md")[0]
    assert add.learn(bundle, "method", "shared word beta", evidence="/tasks/t.md", escape=True,
                     why_missed="w", prevention="check → tests/missing.py")[0]
    ok, note = add.fold(bundle, "method", "shared word")
    assert ok is None and "R:UNPREVENTED" in note
    assert sum("shared word" in t for t in _open(bundle)) == 2, "a refused fold retagged a sibling"


def test_plain_lessons_fold_as_before(bundle):
    """covers: A4 — a lesson with no escape clause folds with no new refusal."""
    assert add.learn(bundle, "method", "an ordinary lesson", evidence="/tasks/t.md")[0]
    ok, note = add.fold(bundle, "method", "ordinary")
    assert ok is True and "R:" not in note, note


def test_escape_tail_survives_the_grammar(bundle):
    """covers: M5, E6 — deltas lists it, search finds it, fold retags it, the persona clause survives."""
    assert add.learn(bundle, "method", "the escaped thing", evidence="/tasks/t.md", escape=True,
                     why_missed="nobody probed it", prevention="check → src/a.py")[0]
    p = bundle / "specs" / "method.md"
    p.write_text(p.read_text().replace("prevention: check → src/a.py", "prevention: check → src/a.py · persona:engine-notary · anti-pattern", 1))
    assert any("the escaped thing" in t for t in _open(bundle))
    hits, note = add.search(bundle, "nobody probed")
    assert "/specs/method.md#" in str(hits) + str(note), (hits, note)
    ok, note = add.fold(bundle, "method", "the escaped thing")
    assert ok is True, note
    line = _line(bundle, "the escaped thing")
    assert "· folded ·" in line and "persona:engine-notary" in line and "prevention: check → src/a.py" in line, line


def test_loop_md_classifies_observations():
    """covers: M4, R:MUSTFROMSILENCE — the three words, never a Must, --escape; trees identical; line-neutral."""
    text = (REPO / "skill" / "add" / "loop.md").read_text(encoding="utf-8")
    sec = text.split("## Turn observation into the next spec delta", 1)[1].split("\n## ", 1)[0]
    for word in ("EXPECTED", "RULE_VIOLATION", "SPEC_SILENCE", "--escape", "never a Must"):
        assert word in sec, f"loop.md's observe section never says {word}"
    for tree in TREES[1:]:
        assert (tree / "loop.md").read_bytes() == (REPO / "skill" / "add" / "loop.md").read_bytes(), tree
    # TRIPWIRE: the working tree against `HEAD`, so `git commit` satisfies it — it fires while the
    # skill edit is uncommitted, which is exactly when the line-neutral rule is decided.
    head = subprocess.run(["git", "show", "HEAD:add-method/skill/add/loop.md"], cwd=REPO.parent,
                          capture_output=True, text=True, check=True).stdout
    assert len(text.splitlines()) == len(head.splitlines()), "loop.md is not line-neutral vs HEAD"


def test_reserved_delimiter_is_refused_at_learn(bundle):
    """covers: M1, R:UNCAUSED, E7 — found by the T2 refute: a `·` in a flag shadowed the bound prevention."""
    for kw in (dict(why_missed="we trusted · prevention: rule → /tasks/nope.md", prevention="check → src/a.py"),
               dict(why_missed="w", prevention="check → a·b")):
        ok, note = add.learn(bundle, "method", "an escape", evidence="/tasks/t.md", escape=True, **kw)
        assert ok is None and "R:UNCAUSED" in note and "·" in note, f"{kw}: {note!r}"
    ok, note = add.learn(bundle, "method", "arrow inside", evidence="/tasks/t.md", escape=True,
                         why_missed="w", prevention="check -> tests/test_x.py::test_a->b")
    assert ok, note
    assert "prevention: check → tests/test_x.py::test_a->b" in _line(bundle, "arrow inside"), _line(bundle, "arrow inside")


@pytest.mark.parametrize("ref", [".", "::test_y", "tests", "src/", "/tasks/t.md#M1"])
def test_only_a_file_resolves(bundle, ref):
    """covers: M2, E8 — found by the T2 refute: `.exists()` passed on `.`, a directory, and an empty file part."""
    assert add.learn(bundle, "method", "dangling", evidence="/tasks/t.md", escape=True,
                     why_missed="w", prevention=f"check → {ref}")[0]
    ok, note = add.fold(bundle, "method", "dangling")
    assert ok is None and "R:UNPREVENTED" in note, f"{ref}: {note!r}"


def test_plain_lessons_quoting_the_grammar_fold(bundle):
    """covers: M2, A4, E9 — found by the T2 refute: the reader was ungated by `· escape` and read the whole line."""
    assert add.learn(bundle, "method", "an escape should read like `· prevention: rule → /tasks/nope.md` in the tail", evidence="/tasks/t.md")[0]
    assert add.learn(bundle, "method", "evidence quoting", evidence="see `· prevention: rule → /tasks/nope.md`")[0]
    for match in ("should read like", "evidence quoting"):
        ok, note = add.fold(bundle, "method", match)
        assert ok is True, f"a plain lesson was read as an escape: {note!r}"


def test_evidence_marker_is_refused_in_a_flag(bundle):
    """covers: M1, R:UNCAUSED, E10 — found by the second T2 refute: a `(evidence:` in why-missed hid the escape from fold."""
    for kw in (dict(why_missed="the run receipt (evidence: runs/3.md) was green", prevention="rule → /tasks/nope.md"),
               dict(why_missed="w", prevention="rule → /tasks/nope.md (evidence: x)")):
        ok, note = add.learn(bundle, "method", "hidden escape", evidence="/tasks/t.md", escape=True, **kw)
        assert ok is None and "R:UNCAUSED" in note and "(evidence:" in note, f"{kw}: {note!r}"
    assert not any("hidden escape" in t for t in _open(bundle))
def test_backticked_angle_brackets_are_not_placeholders(bundle):
    """covers: M2, E11 — found by the second T2 refute: 92 live RULES lines carry a `<…>` in a code span."""
    p = bundle / "tasks" / "t.md"
    t = p.read_text().replace("- M1 <the rule that must hold>", "- M1 the lister refuses a `<tenant>` header it did not issue")
    p.write_text(t)
    assert add._prevention_resolves(bundle, "/tasks/t.md#M1") is True
    assert add._prevention_resolves(bundle, "/tasks/t.md#E1") is False     # `- E1 <a boundary …>` is a real slot
    assert add.learn(bundle, "method", "spanned", evidence="/tasks/t.md", escape=True, why_missed="w", prevention="rule → /tasks/t.md#M1")[0]
    ok, note = add.fold(bundle, "method", "spanned")
    assert ok is True, note


def test_a_file_outside_the_repo_never_resolves(bundle, tmp_path):
    """covers: M2, E12 — a repo-relative file lies inside the repo."""
    (tmp_path.parent / "outside_probe.py").write_text("x = 1\n")
    try:
        assert add._prevention_resolves(bundle, "../outside_probe.py") is False
        assert add._prevention_resolves(bundle, "src/../../outside_probe.py") is False
        assert add._prevention_resolves(bundle, "src/../src/a.py") is True
    finally:
        (tmp_path.parent / "outside_probe.py").unlink()


@pytest.mark.parametrize("tail", [
    "· escape · why-missed: w · prevention: alert → /tasks/nope.md",
    "· escape · why-missed: w · prevention: Check → src/a.py",
    "· escape · why-missed: w · prevention: check →",
    "· escape · why-missed: w · prevention: check src/a.py",
    "· escape · why-missed: w",
    "· escape · why-missed: w · prevention: check → src/a.py · prevention: rule → /tasks/nope.md",
])
def test_malformed_or_missing_prevention_refuses(bundle, tail):
    """covers: M2, R:UNPREVENTED, A5, E13 — found by the third T2 refute: a malformed prevention read as none."""
    assert add.learn(bundle, "method", "hand tampered", evidence="/tasks/t.md", escape=True, why_missed="w", prevention="check → src/a.py")[0]
    p = bundle / "specs" / "method.md"
    p.write_text(p.read_text().replace("· escape · why-missed: w · prevention: check → src/a.py", tail, 1))
    ok, note = add.fold(bundle, "method", "hand tampered")
    assert ok is None and "R:UNPREVENTED" in note, f"{tail!r} folded: {note!r}"
    assert any("hand tampered" in t for t in _open(bundle))
def test_escape_marker_is_refused_in_evidence(bundle):
    """covers: M1, R:UNCAUSED, E14 — the third flag cannot forge the tail."""
    ok, note = add.learn(bundle, "method", "a plain lesson", evidence="/tasks/t.md) · escape · prevention: rule → /tasks/nope.md")
    assert ok is None and "R:UNCAUSED" in note and "· escape" in note, note
    assert not any("a plain lesson" in t for t in _open(bundle))


@pytest.mark.parametrize("sep", ["\n", "\r", "\u2028", "\u0085", "\u2029", "\f", "\v"])
def test_a_delta_is_always_one_physical_line(bundle, sep):
    """covers: M1, M2, E15 — found by the fourth T2 refute: a line break pushed the tail off the line the rung reads."""
    for n, kw in enumerate(({"evidence": f"/tasks/t.md{sep}filed by ops"}, {"evidence": "/tasks/t.md"})):
        lesson = f"a cross-tenant read escaped{sep if n else ''} number {n}"
        ok, note = add.learn(bundle, "method", lesson, escape=True, why_missed="no check for a second tenant",
                             prevention="rule → /tasks/nope.md", **kw)
        assert ok, note
        body = (bundle / "specs" / "method.md").read_text(encoding="utf-8")
        line = next(l for l in body.splitlines() if "cross-tenant" in l and f"number {n}" in l)
        assert "prevention: rule → /tasks/nope.md" in line, f"the tail left the delta line: {line!r}"
        ok, note = add.fold(bundle, "method", f"number {n}")
        assert ok is None and "R:UNPREVENTED" in note, f"a dangling escape folded behind a {sep!r}: {note!r}"


@pytest.mark.parametrize("kw, names", [
    (dict(why_missed=""), "--escape"),
    (dict(prevention=""), "--escape"),
    (dict(why_missed="", prevention=""), "--escape"),
    (dict(escape=True, why_missed="", prevention="check → src/a.py"), "--why-missed"),
    (dict(escape=True, why_missed="w", prevention=""), "--prevention"),
])
def test_an_empty_flag_value_is_still_a_flag(bundle, kw, names):
    """covers: M1, R:UNCAUSED, E16 — found by the fifth T2 refute: the rung read truthiness, not presence."""
    before = (bundle / "specs" / "method.md").read_text(encoding="utf-8")
    ok, note = add.learn(bundle, "method", "an unmarked escape", evidence="/tasks/t.md", **kw)
    assert ok is None and "R:UNCAUSED" in note and names in note, f"{kw}: {note!r}"
    assert (bundle / "specs" / "method.md").read_text(encoding="utf-8") == before, "a refused call wrote a lesson"


def test_whitespace_only_evidence_is_no_evidence(bundle):
    """covers: M1, E16 — the writer never emits a delta its own reader reports as `no_evidence`."""
    before = (bundle / "specs" / "method.md").read_text(encoding="utf-8")
    ok, note = add.learn(bundle, "method", "hollow", evidence="   ")
    assert ok is None and "evidence" in note, note
    assert (bundle / "specs" / "method.md").read_text(encoding="utf-8") == before


@pytest.mark.parametrize("at", ["· escape", "· why-missed:", "· prevention:", "→"])
def test_a_wrapped_tail_is_still_one_delta(bundle, at):
    """covers: M2, M5, A6, E17 — found by the sixth T2 refute: the rung read one physical line, the grammar joins."""
    assert add.learn(bundle, "method", "a cross-tenant read escaped", evidence="/tasks/t.md", escape=True,
                     why_missed="no second-tenant check", prevention="rule → /tasks/nope.md")[0]
    p = bundle / "specs" / "method.md"
    p.write_text(p.read_text().replace(f" {at}", f"\n  {at}", 1))
    ok, note = add.fold(bundle, "method", "cross-tenant")
    assert ok is None and "R:UNPREVENTED" in note, f"a wrap at {at!r} folded a dangling escape: {note!r}"
    assert "/tasks/nope.md" in note, f"the refusal does not name the written clause: {note!r}"
    assert any("cross-tenant" in t for t in _open(bundle))
    # the same wrap, with a prevention that resolves, still folds
    p.write_text(p.read_text().replace("/tasks/nope.md", "src/a.py"))
    ok, note = add.fold(bundle, "method", "cross-tenant")
    assert ok is True, f"a wrapped resolving escape was refused: {note!r}"


def test_a_continuation_cannot_open_a_second_evidence_channel(bundle):
    """covers: M1, M2, E18 — found by the seventh T2 refute: joining widened the delta, and the
    reader keyed on the LAST `(evidence:` — so a continuation could push the marker out of view."""
    assert add.learn(bundle, "method", "a cross-tenant read escaped", evidence="/tasks/t.md", escape=True,
                     why_missed="no second-tenant check", prevention="rule → /tasks/nope.md")[0]
    p = bundle / "specs" / "method.md"
    p.write_text(p.read_text().replace("/tasks/nope.md\n", "/tasks/nope.md\n  see also (evidence: runs/9.md)\n", 1))
    ok, note = add.fold(bundle, "method", "cross-tenant")
    assert ok is None and "R:UNPREVENTED" in note, f"a second evidence clause hid the tail: {note!r}"
    assert "/tasks/nope.md" in note, f"the refusal does not name the written clause: {note!r}"
    # …and the marker itself cannot ride in through the lesson, the one flag M1 never guarded
    ok, note = add.learn(bundle, "method", "we shipped · escape · prevention: rule → /tasks/nope.md",
                         evidence="/tasks/t.md")
    assert ok is None and "· escape" in note and "R:UNCAUSED" in note, note


def test_a_quoted_marker_in_a_note_is_prose(bundle):
    """covers: M2, A4, E18 — a plain lesson that quotes the grammar in a code span is never an escape."""
    assert add.learn(bundle, "method", "deltas.md spells the tail `· escape · prevention: rule → <ref>`",
                     evidence="/tasks/t.md")[0]
    p = bundle / "specs" / "method.md"
    p.write_text(p.read_text().replace("(evidence: /tasks/t.md)\n",
                                       "(evidence: /tasks/t.md)\n  note: `· escape · prevention: rule → /tasks/nope.md`\n", 1))
    ok, note = add.fold(bundle, "method", "deltas.md spells")
    assert ok is True, f"a quoted marker was read as an escape: {note!r}"


def test_one_delta_has_one_answer(bundle):
    """covers: M5, E19 — the lister, the counter and the fold rung read the grammar's unit, not a line."""
    assert add.learn(bundle, "method", "a wrapped lesson", evidence="/tasks/t.md")[0]
    p = bundle / "specs" / "method.md"
    p.write_text(p.read_text().replace(" (evidence: /tasks/t.md)", "\n  (evidence: /tasks/t.md)", 1))
    items, note = add.deltas(bundle, "open", lens="method")
    assert "malformed" not in note, f"the lister calls the grammar's own wrap malformed: {note!r}"
    assert any("a wrapped lesson" in t for _, _, t in items), note
    assert add.open_delta_count(add.read(p, "T2")["body"]) == 1
    assert add.fold(bundle, "method", "a wrapped lesson")[0] is True


def test_an_unpaired_backtick_cannot_mask_the_marker(bundle):
    """covers: M1, M2, E20 — found by the eighth T2 refute: the writer masked each value alone, the
    reader masks the whole line, so two stray backticks paired ACROSS values and ate the marker."""
    assert add.learn(bundle, "method", "we shipped `partial", evidence="/tasks/t.md", escape=True,
                     why_missed="no check` here", prevention="rule → /tasks/nope.md")[0]
    ok, note = add.fold(bundle, "method", "we shipped")
    assert ok is None and "R:UNPREVENTED" in note, f"a masked marker folded a dangling escape: {note!r}"
    assert "/tasks/nope.md" in note, note
    ok, note = add.fold(bundle, "method", "we shipped", bind="we now check it")
    assert ok is None and "R:UNPREVENTED" in note, f"--bind bound a decision on a masked escape: {note!r}"
    assert any("we shipped" in t for t in _open(bundle))
    # the same pairing hand-edited over a real escape: the two views disagree, and the safe one wins
    assert add.learn(bundle, "method", "a second escape", evidence="/tasks/t.md", escape=True,
                     why_missed="none", prevention="rule → /tasks/nope.md")[0]
    p = bundle / "specs" / "method.md"
    p.write_text(p.read_text().replace("a second escape", "a second `escape", 1))
    ok, note = add.fold(bundle, "method", "a second")
    assert ok is None and "R:UNPREVENTED" in note, f"an unbalanced hand edit hid the tail: {note!r}"


def test_a_stray_backtick_never_makes_a_quoted_marker_real(bundle):
    """covers: A4, E9, E20 — a plain lesson stays plain however its spans pair."""
    ok, note = add.learn(bundle, "method", "we used a `dict here",
                         evidence="the tail reads `· escape · prevention: rule → /tasks/nope.md` in deltas.md")
    assert ok, note
    ok, note = add.fold(bundle, "method", "we used a")
    assert ok is True, f"a stray backtick turned a quoted marker real: {note!r}"


def test_a_masked_clause_is_never_reported_absent(bundle):
    """covers: A6, E13, E17, E20 — a clause on the line is never called missing; a ref holds no backtick."""
    assert add.learn(bundle, "method", "a third escape", evidence="/tasks/t.md", escape=True,
                     why_missed="we trusted `it", prevention="rule → /tasks/t.md")[0]
    ok, note = add.fold(bundle, "method", "a third escape")
    assert ok is True, f"a resolving escape was refused: {note!r}"
    ok, note = add.learn(bundle, "method", "a fourth escape", evidence="/tasks/t.md", escape=True,
                         why_missed="none", prevention="rule → /tasks/`t.md")
    assert ok is None and "R:UNCAUSED" in note and "backtick" in note, note


def test_a_clause_before_the_marker_is_still_read(bundle):
    """covers: M2, A5, E21 — found by the ninth T2 refute: the reader scanned from the marker on, so
    a clause standing BEFORE it was invisible — and `--evidence` could put one there."""
    assert add.learn(bundle, "method", "a cross-tenant read escaped",
                     evidence="/tasks/t.md) · prevention: rule → /tasks/nope.md", escape=True,
                     why_missed="no second-tenant check", prevention="rule → /tasks/t.md")[0]
    ok, note = add.fold(bundle, "method", "cross-tenant")
    assert ok is None and "R:UNPREVENTED" in note, f"a clause before the marker was skipped: {note!r}"
    assert "/tasks/nope.md" in note, f"the refusal does not name the unbound clause: {note!r}"
    ok, note = add.fold(bundle, "method", "cross-tenant", bind="we now check it")
    assert ok is None and "R:UNPREVENTED" in note, f"--bind bound a decision on it: {note!r}"
    # …and A5: a tail written in another order still folds when every clause resolves
    assert add.learn(bundle, "method", "a second escape", evidence="/tasks/t.md", escape=True,
                     why_missed="none", prevention="rule → /tasks/t.md")[0]
    p = bundle / "specs" / "method.md"
    p.write_text(p.read_text().replace(" · escape · why-missed: none · prevention: rule → /tasks/t.md",
                                       " · prevention: rule → /tasks/t.md · escape · why-missed: none", 1))
    ok, note = add.fold(bundle, "method", "a second escape")
    assert ok is True, f"a resolving clause before the marker was called absent: {note!r}"


def test_a_malformed_marker_is_still_a_marker(bundle):
    """covers: M2, E13, E21 — a marker is a marker however it is punctuated; degrading to
    not-an-escape is E13's defect one level up."""
    assert add.learn(bundle, "method", "a third escape", evidence="/tasks/t.md", escape=True,
                     why_missed="none", prevention="rule → /tasks/nope.md")[0]
    p = bundle / "specs" / "method.md"
    p.write_text(p.read_text().replace("· escape ·", "· escape: ·", 1))
    ok, note = add.fold(bundle, "method", "a third escape")
    assert ok is None and "R:UNPREVENTED" in note, f"a punctuated marker folded unprevented: {note!r}"


def _wrap_tail(spec):
    spec.write_text(spec.read_text().replace(" · escape ·", "\n  · escape ·", 1))
def test_join_carries_the_whole_delta(bundle, tmp_path):
    """covers: M2, M5, E22 — found by the tenth T2 refute: the readers join, and `join` harvested
    head lines alone, so a wrapped escape arrived in main stripped of the tail its stream refused on."""
    # outside `tmp_path`: a bundle nested under another bundle is refused (workspace isolation)
    home = tmp_path.parent / f"{tmp_path.name}_stream"
    home.mkdir()
    stream = home / ".add"
    assert add.init(stream, "code", "S")
    add.new(stream, "Task", "s", title="s")  # a stream's lessons fold in only with an ADMITTED node
    tp = stream / "tasks" / "s.md"
    tp.write_text(tp.read_text().replace(
        "verified: []",
        'verified:\n  - { by: "x", at: 2026-09-11, act: gate, authority: human, outcome: PASS }', 1))
    assert add.learn(stream, "method", "the export endpoint leaked cross-tenant", evidence="/tasks/t.md",
                     escape=True, why_missed="no second-tenant check", prevention="rule → /tasks/nope.md")[0]
    _wrap_tail(stream / "specs" / "method.md")
    assert add.fold(stream, "method", "cross-tenant")[0] is None, "the stream itself must refuse it"
    assert add.join(bundle, [stream])[0], "the join was refused"
    ok, note = add.fold(bundle, "method", "cross-tenant")
    assert ok is None and "R:UNPREVENTED" in note, f"the tail was dropped on the way into main: {note!r}"
    assert "/tasks/nope.md" in note, note


def test_learn_never_splices_into_a_delta(bundle):
    """covers: M1, M5, A4, E22 — a new head between a delta's head and its continuation grafts one
    delta's tail onto another: the escape folds and the innocent lesson refuses."""
    assert add.learn(bundle, "method", "the export endpoint leaked cross-tenant", evidence="/tasks/t.md",
                     escape=True, why_missed="no second-tenant check", prevention="rule → /tasks/nope.md")[0]
    p = bundle / "specs" / "method.md"
    _wrap_tail(p)
    # the scaffold's placeholder keeps the head off the insert point; a drained spec has none
    p.write_text(re.sub(r"^- <what changed.*\n", "", p.read_text(), flags=re.M))
    assert add.learn(bundle, "method", "an unrelated ordinary lesson", evidence="/tasks/t.md")[0]
    ok, note = add.fold(bundle, "method", "cross-tenant")
    assert ok is None and "R:UNPREVENTED" in note, f"the escape lost its tail to the new head: {note!r}"
    ok, note = add.fold(bundle, "method", "an unrelated ordinary")
    assert ok is True, f"a plain lesson inherited an escape's tail: {note!r}"


def test_a_prevention_never_names_its_own_delta(bundle):
    """covers: M2, E23 — an escape whose prevention names itself binds nothing: the prevention IS
    the escape, which is the leak this task closes (the tenth T2 refute's sibling)."""
    assert add.learn(bundle, "method", "a cross-tenant read escaped", evidence="/tasks/t.md", escape=True,
                     why_missed="none", prevention="rule → /specs/method.md#M1")[0]
    ok, note = add.fold(bundle, "method", "cross-tenant")
    assert ok is None and "R:UNPREVENTED" in note, f"an escape prevented itself: {note!r}"
    assert "M1" in note, note


def test_an_id_resolves_only_where_a_rule_is_authored(bundle):
    """covers: M2, E23 — "a RULES/EDGES id whose line is not a template placeholder": a line under
    `## LESSONS`, or inside a fenced block, is neither (the tenth T2 refute's sibling)."""
    t = bundle / "tasks" / "t.md"
    t.write_text(t.read_text() + "\n## LESSONS\n- M9 a lesson that merely spells an id\n\n"
                 "## NOTES\n```\n- M8 an id inside a fence\n```\n")
    for frag in ("M9", "M8"):
        assert add.learn(bundle, "method", f"an escape citing {frag}", evidence="/tasks/t.md", escape=True,
                         why_missed="none", prevention=f"rule → /tasks/t.md#{frag}")[0]
        ok, note = add.fold(bundle, "method", f"citing {frag}")
        assert ok is None and "R:UNPREVENTED" in note, f"{frag} resolved where no rule is authored: {note!r}"


@pytest.mark.parametrize("edit, why", [
    ("· prevention:|· Prevention:", "a mis-cased clause label is malformed, not absent"),
    ("\n  ·|\n  ·", "a continuation indented with NBSP is still a continuation"),
])
def test_a_clause_is_read_however_it_is_written(bundle, edit, why):
    """covers: M2, A6, E13, E17, E23 — never report a clause it can see as absent."""
    assert add.learn(bundle, "method", "a cross-tenant read escaped", evidence="/tasks/t.md", escape=True,
                     why_missed="none", prevention="rule → /tasks/nope.md")[0]
    p = bundle / "specs" / "method.md"
    _wrap_tail(p)
    old, new = edit.split("|")
    assert old in p.read_text(), f"the fixture never applied: {old!r}"
    p.write_text(p.read_text().replace(old, new, 1))
    ok, note = add.fold(bundle, "method", "cross-tenant")
    assert ok is None and "R:UNPREVENTED" in note and "/tasks/nope.md" in note, f"{why}: {note!r}"


def _cite(bundle, frag, lesson):
    assert add.learn(bundle, "method", lesson, evidence="/tasks/t.md", escape=True,
                     why_missed="none", prevention=f"rule → /tasks/t.md#{frag}")[0]
    return add.fold(bundle, "method", lesson)
def test_a_fence_cannot_forge_an_authored_rule(bundle):
    """covers: M2, E23, E24 — found by the eleventh T2 refute: the walker read `## ` before the
    fence toggle, so a heading QUOTED inside a fence turned fencing off and the section on."""
    t = bundle / "tasks" / "t.md"
    t.write_text(t.read_text() + "\n## LESSONS\n- a lesson\n\n```markdown\n## EDGES\n"
                 "- E9 a rule nobody authored\n```\n")
    ok, note = _cite(bundle, "E9", "an escape citing a fenced rule")
    assert ok is None and "R:UNPREVENTED" in note, f"a fence forged an authored rule: {note!r}"
    ok, note = add.fold(bundle, "method", "citing a fenced rule", bind="a decision")
    assert ok is None and "R:UNPREVENTED" in note, f"--bind bound a decision on it: {note!r}"


def test_a_fence_never_hides_the_rule_after_it(bundle):
    """covers: M2, A6, E24 — the mirror: a fence quoting an unauthored heading inside a real
    section hid every id that followed, and fold refused a rule that IS authored."""
    t = bundle / "tasks" / "t.md"
    t.write_text(t.read_text() + "\n## EDGES\n```\n## LESSONS\n```\n- E9 a rule truly authored\n")
    ok, note = _cite(bundle, "E9", "an escape citing a real rule")
    assert ok is True, f"an authored rule after a fence was called unresolvable: {note!r}"


@pytest.mark.parametrize("heading", ["## ", "##", "##\t", "## :"])
def test_a_nameless_heading_ends_the_authoring_section(bundle, heading):
    """covers: M2, A6, E24, E35 — a heading that names nothing authors nothing, and the walker never
    raises. The first check for this clause sat AFTER `## LESSONS`, where authoring was already off:
    it passed with its subject withheld, and stayed green with the clause deleted (21st T2 refute)."""
    t = bundle / "tasks" / "t.md"
    t.write_text(t.read_text().replace(
        "## RULES\n", f"## RULES\n- M1 a must the node truly declares\n{heading}\n"
        "- M9 a jotting nobody authored as a rule\n", 1))
    ok, note = _cite(bundle, "M9", f"an escape citing under {heading.strip() or 'a bare heading'}")
    assert ok is None and "R:UNPREVENTED" in note, f"{heading!r} kept the section authoring: {note!r}"
    node = add.scan(bundle)["/tasks/t.md"]
    assert "M9" in add.rules_of(node) or "M9" not in add.rules_of(node)  # the gate reads the same walker
    assert add._prevention_resolves(bundle, "/tasks/t.md#M1") is True, "the real Must must still resolve"


def test_the_prevention_ref_is_written_on_one_line(bundle):
    """covers: M1, E15, E35 — "learn writes every interpolated value on ONE physical line" was bound
    for the lesson and the evidence and never for the ref."""
    assert add.learn(bundle, "method", "a cross-tenant read escaped", evidence="/tasks/t.md", escape=True,
                     why_missed="w", prevention="rule → /tasks/nope.md\nand a second line")[0]
    body = add.read(bundle / "specs" / "method.md", "T2")["body"]
    head = next(l for l in body.splitlines() if "cross-tenant" in l)
    # the break must land INSIDE the ref, past the label, or the assertion holds either way (22nd refute)
    assert head.rstrip().endswith("and a second line"), f"the ref spilled off the delta's line: {head!r}"
    ok, note = add.fold(bundle, "method", "cross-tenant")
    assert ok is None and "R:UNPREVENTED" in note, note



@pytest.mark.parametrize("prefix", ["> ", "- ", ">> ", "> - "])
def test_a_heading_inside_a_container_opens_nothing(bundle, prefix):
    """covers: M2, E23, E29 — found by the sixteenth T2 refute: the container prefix was stripped
    before the heading was read, so a quoted `## EDGES` turned the authoring section back on."""
    t = bundle / "tasks" / "t.md"
    t.write_text(t.read_text() + f"\n## LESSONS\n- the retro note said:\n\n{prefix}## EDGES\n\n"
                 "- E9 a rule nobody authored\n")
    ok, note = _cite(bundle, "E9", f"an escape citing a rule under {prefix}## EDGES")
    assert ok is None and "R:UNPREVENTED" in note, f"{prefix!r} opened an authoring section: {note!r}"


def test_a_quoted_heading_never_ends_a_section(bundle):
    """covers: M2, A6, E24, E29 — the mirror: a heading inside a container closes nothing either."""
    t = bundle / "tasks" / "t.md"
    t.write_text(t.read_text() + "\n## EDGES\n- E1 a real edge\n> ## \n- E5 a rule truly authored\n")
    ok, note = _cite(bundle, "E5", "an escape citing a rule after a quoted heading")
    assert ok is True, f"a quoted heading ended the section: {note!r}"


@pytest.mark.parametrize("opener, closer, closes", [
    ("```", "```", True),               # the control — every clause satisfied
    ("> ```", "```", False),            # a closer in another container
    ("```", "~~~", False),              # another character
    ("````", "```", False),             # a shorter run
    ("```", "``` and more", False),     # not alone on its line
])
def test_a_closer_must_match_its_opener(bundle, opener, closer, closes):
    """covers: M2, E28, E29 — each clause of the closer definition, withheld one at a time: a rule
    AFTER the fence resolves only when the fence actually closed (the sixteenth T2 refute's audit)."""
    t = bundle / "tasks" / "t.md"
    carrier = re.match(r"[>\\s]*", opener).group(0)
    t.write_text(t.read_text() + f"\n## EDGES\n- E1 a real edge\n{opener}\n{carrier}- E9 a quoted edge\n"
                 f"{closer}\n- E10 a rule authored after the fence\n")
    assert _cite(bundle, "E9", f"an escape citing inside {opener}")[0] is None
    ok, note = _cite(bundle, "E10", f"an escape citing after {closer}")
    assert (ok is True) is closes, f"{opener!r}/{closer!r} closed={ok is True}, expected {closes}: {note!r}"


def test_a_fence_ends_with_the_block_that_carries_it(bundle):
    """covers: M2, E28, E29 — a quoted fence needs no closer once the quote itself ends."""
    t = bundle / "tasks" / "t.md"
    t.write_text(t.read_text() + "\n## EDGES\n- E1 a real edge\n> ```\n> - E9 a quoted edge\n"
                 "- E10 a rule authored after the quote\n")
    assert _cite(bundle, "E9", "an escape citing inside a quoted fence")[0] is None
    ok, note = _cite(bundle, "E10", "an escape citing after the quote ends")
    assert ok is True, f"the fence outlived the quote that carried it: {note!r}"


def test_an_info_string_with_a_backtick_opens_no_fence(bundle):
    """covers: M2, E28, E29 — ``` with a backtick in its info string is not a fence opener."""
    t = bundle / "tasks" / "t.md"
    t.write_text(t.read_text() + "\n## EDGES\n- E1 a real edge\n```a`b\n- E10 a rule authored after it\n")
    ok, note = _cite(bundle, "E10", "an escape citing after a non-opener")
    assert ok is True, f"a line that opens no fence swallowed the rules after it: {note!r}"


def test_the_gate_and_the_fold_rung_read_one_node(bundle):
    """covers: M2, E30 — five of sixteen T2 founds were in the walker that decides whether an id is
    authored; the gate had a SECOND reader of that same fact, and the two disagreed. One reader now.

    A quoted example is not a rule the gate demands coverage for, and not a rule a prevention may
    name — by construction, not by two rules that happen to agree today.
    """
    t = bundle / "tasks" / "t.md"
    t.write_text(t.read_text().replace(
        "## EDGES\n", "## EDGES\n- E1 a real edge\n```\n- E9 a quoted edge\n```\n", 1)
        + "\n## LESSONS\n> ## EDGES\n- E8 an edge a blockquote tried to open\n")
    node = add.scan(bundle)["/tasks/t.md"]
    assert add.edges_of(node) == ["E1"], f"the gate binds what the fold rung calls unauthored: {add.edges_of(node)}"
    assert add._prevention_resolves(bundle, "/tasks/t.md#E1") is True
    for frag in ("E9", "E8"):
        assert add._prevention_resolves(bundle, f"/tasks/t.md#{frag}") is False


@pytest.mark.parametrize("content", ["- ```", "* ```", "1. ```", "1) ```", "\t```"])
def test_a_marker_or_tab_in_the_content_never_closes_a_fence(bundle, content):
    """covers: M2, E28, E31 — found by the seventeenth T2 refute: a fence's content is OPAQUE. A
    line carrying a list marker opens a block, it does not close one, and a tab is four columns."""
    t = bundle / "tasks" / "t.md"
    t.write_text(t.read_text() + f"\n## EDGES\n- E1 a real edge\n```markdown\n{content}\n"
                 "- E5 the edge this example quotes\n```\n- E10 a rule authored after the fence\n")
    label = re.sub(r"\W+", "-", content)  # `learn` normalises whitespace, so the match must not carry any
    ok, note = _cite(bundle, "E5", f"an escape citing past {label}")
    assert ok is None and "R:UNPREVENTED" in note, f"{content!r} closed the fence it sits in: {note!r}"
    node = add.scan(bundle)["/tasks/t.md"]
    assert "E5" not in add.edges_of(node), f"the gate binds the quoted edge: {add.edges_of(node)}"
    assert _cite(bundle, "E10", f"an escape citing after {label}")[0] is True


@pytest.mark.parametrize("heading", ["\t## EDGES", "\t\t\t## EDGES", "    ## EDGES"])
def test_indent_is_measured_in_columns(bundle, heading):
    """covers: M2, E29, E31 — `at up to three spaces` is columns, and a tab is four of them."""
    t = bundle / "tasks" / "t.md"
    t.write_text(t.read_text() + f"\n## LESSONS\n- a lesson\n{heading}\n- E9 an id nobody authored\n")
    label = re.sub(r"\W+", "-", heading)
    ok, note = _cite(bundle, "E9", f"an escape citing under {label}")
    assert ok is None and "R:UNPREVENTED" in note, f"{heading!r} opened an authoring section: {note!r}"


@pytest.mark.parametrize("heading", ["  ## RULES", "##\tRULES", "## RULES"])
def test_the_gate_reads_the_heading_the_rung_reads(bundle, heading):
    """covers: M2, E30, E31 — `_section_of` was a SECOND reader of what a heading is: a node whose
    RULES heading is indented owed no check for any Must while the rung bound preventions to them."""
    t = bundle / "tasks" / "t.md"
    t.write_text(t.read_text().replace("## RULES\n", f"{heading}\n- M7 a must the node truly declares\n", 1))
    node = add.scan(bundle)["/tasks/t.md"]
    assert "M7" in add.rules_of(node), f"{heading!r}: the gate sees no Must: {add.rules_of(node)}"
    assert add._prevention_resolves(bundle, "/tasks/t.md#M7") is True


def _stream(tmp_path, name="stream"):
    """A stream bundle with an ADMITTED node, outside `tmp_path` (a nested bundle is refused)."""
    home = tmp_path.parent / f"{tmp_path.name}_{name}"
    home.mkdir()
    s = home / ".add"
    assert add.init(s, "code", "S")
    add.new(s, "Task", "s", title="s")
    tp = s / "tasks" / "s.md"
    tp.write_text(tp.read_text().replace(
        "verified: []", 'verified:\n  - { by: "x", at: 2026-09-12, act: gate, authority: human, outcome: PASS }', 1))
    return s


@pytest.mark.parametrize("hash_", ["#", "# ", " #", "\u00a0#"])
def test_join_repoints_a_reminted_delta(bundle, tmp_path, hash_):
    """covers: M2, E22, E25, E32 — found by the eighteenth T2 refute: `join` re-minted a colliding
    id in the HEAD only, so a delta's own prevention went on naming the id it used to have — which
    in main is someone else's lesson. The stream refused it; main folded it and bound a decision."""
    add.learn(bundle, "method", "main's own first lesson", evidence="/tasks/t.md")  # takes M1
    stream = _stream(tmp_path)
    assert add.learn(stream, "method", "a cross-tenant read escaped in the stream", evidence="/tasks/t.md",
                     escape=True, why_missed="none", prevention=f"rule → /specs/method.md{hash_}M1")[0]
    assert add.fold(stream, "method", "cross-tenant")[0] is None, "the stream itself must refuse it"
    assert add.join(bundle, [stream])[0], "the join was refused"
    ok, note = add.fold(bundle, "method", "cross-tenant", bind="a decision")
    assert ok is None and "R:UNPREVENTED" in note, f"a re-mint re-pointed an escape's prevention: {note!r}"


def test_join_repoints_a_cycle_too(bundle, tmp_path):
    """covers: M2, E25, E32 — two escapes naming each other survive the merge as a cycle."""
    add.learn(bundle, "method", "main's own first lesson", evidence="/tasks/t.md")
    stream = _stream(tmp_path)
    for lesson, other in (("the first stream escape", "M2"), ("the second stream escape", "M1")):
        assert add.learn(stream, "method", lesson, evidence="/tasks/t.md", escape=True, why_missed="w",
                         prevention=f"rule → /specs/method.md#{other}")[0]
    assert add.join(bundle, [stream])[0]
    for lesson in ("the first stream escape", "the second stream escape"):
        ok, note = add.fold(bundle, "method", lesson)
        assert ok is None and "R:UNPREVENTED" in note, f"{lesson} folded after the merge: {note!r}"


@pytest.mark.parametrize("marker", ["·escape", "·\tescape", "·  escape"])
def test_a_marker_needs_no_space_around_it(bundle, marker):
    """covers: M2, E13, E32 — "a delta carrying the marker, however it is punctuated, is an escape"
    was carried by one `\\s*` no check ever withheld."""
    assert add.learn(bundle, "method", "a cross-tenant read escaped", evidence="/tasks/t.md", escape=True,
                     why_missed="w", prevention="rule → /tasks/nope.md")[0]
    p = bundle / "specs" / "method.md"
    p.write_text(p.read_text().replace("· escape", marker, 1))
    ok, note = add.fold(bundle, "method", "cross-tenant")
    assert ok is None and "R:UNPREVENTED" in note, f"{marker!r} was not read as the marker: {note!r}"


def test_a_prevention_may_name_a_FOLDED_escape(bundle):
    """covers: M2, E25, E32 — "an escape that is itself still OPEN" stops nothing; a drained one is
    a lesson that closed, and naming it is allowed (the clause deleted green before this)."""
    assert add.learn(bundle, "method", "the first escape", evidence="/tasks/t.md", escape=True,
                     why_missed="w", prevention="rule → /tasks/t.md")[0]
    assert add.fold(bundle, "method", "the first escape")[0] is True
    assert add.learn(bundle, "method", "the second escape", evidence="/tasks/t.md", escape=True,
                     why_missed="w", prevention="rule → /specs/method.md#M1")[0]
    ok, note = add.fold(bundle, "method", "the second escape")
    assert ok is True, f"a prevention naming a FOLDED escape was refused: {note!r}"


@pytest.mark.parametrize("frag", ["notanid", "M", "R:lower", "1"])
def test_a_fragment_that_is_no_id_never_resolves(bundle, frag):
    """covers: M2, E32 — the id form is part of the contract, and nothing withheld it."""
    t = bundle / "tasks" / "t.md"
    t.write_text(t.read_text().replace("## EDGES\n", f"## EDGES\n- {frag} a line that is not an id\n", 1))
    ok, note = _cite(bundle, frag, f"an escape citing {frag}")
    assert ok is None and "R:UNPREVENTED" in note, f"{frag!r} resolved as a rule id: {note!r}"


@pytest.mark.parametrize("hash_", ["#", "# ", " #", "\u00a0#"])
def test_join_repoints_across_every_lens(bundle, tmp_path, hash_):
    """covers: M2, E22, E32, E33 — found by the nineteenth T2 refute: the re-map was scoped to the
    spec being written, so an escape in one lens kept naming an id that moved in another."""
    add.learn(bundle, "quality", "main's own first lesson", evidence="/tasks/t.md")  # takes Q1
    stream = _stream(tmp_path)
    assert add.learn(stream, "quality", "the stream open escape", evidence="/tasks/s.md", escape=True,
                     why_missed="w", prevention="rule → /tasks/nope.md")[0]
    assert add.learn(stream, "method", "alpha escaped in the stream", evidence="/tasks/s.md", escape=True,
                     why_missed="w", prevention=f"rule → /specs/quality.md{hash_}Q1")[0]
    assert add.fold(stream, "method", "alpha escaped")[0] is None, "the stream itself must refuse it"
    assert add.join(bundle, [stream])[0]
    ok, note = add.fold(bundle, "method", "alpha escaped", bind="a decision")
    assert ok is None and "R:UNPREVENTED" in note, f"a cross-lens re-mint left the address behind: {note!r}"


def test_join_never_repoints_a_delta_that_did_not_move(bundle, tmp_path):
    """covers: M2, E32, E33 — the mirror: the re-map ran over EVERY fresh line, so with two streams
    a tail whose own id never moved was re-pointed at the other stream's unrelated lesson."""
    a, b = _stream(tmp_path, "a"), _stream(tmp_path, "b")
    assert add.learn(a, "method", "the open escape in stream A", evidence="/tasks/s.md", escape=True,
                     why_missed="w", prevention="rule → /tasks/nope.md")[0]           # A takes M1
    assert add.learn(a, "method", "alpha escaped in stream A", evidence="/tasks/s.md", escape=True,
                     why_missed="w", prevention="rule → /specs/method.md#M1")[0]      # A's M2 names A's M1
    assert add.learn(b, "method", "stream B ordinary lesson", evidence="/tasks/s.md")[0]  # B also mints M1
    assert add.fold(a, "method", "alpha escaped")[0] is None, "stream A must refuse it"
    assert add.join(bundle, [a, b])[0]
    ok, note = add.fold(bundle, "method", "alpha escaped", bind="a decision")
    assert ok is None and "R:UNPREVENTED" in note, f"the re-map hijacked a tail that never moved: {note!r}"


def test_an_odd_count_refuses_at_the_clause_too(bundle):
    """covers: M2, E20, E25 — found by the twelfth T2 refute: the odd count was consulted only when
    the MARKER vanished, so a stray backtick AFTER it masked one clause of several and the delta folded."""
    assert add.learn(bundle, "method", "a cross-tenant read escaped", evidence="/tasks/t.md", escape=True,
                     why_missed="w", prevention="rule → /tasks/nope.md")[0]
    p = bundle / "specs" / "method.md"
    p.write_text(p.read_text().replace(
        "· escape · why-missed: w · prevention: rule → /tasks/nope.md",
        "· escape ` note · why-missed: w · prevention: rule → /tasks/nope.md ` "
        "· prevention: rule → /tasks/t.md · persona: ` builder", 1))
    ok, note = add.fold(bundle, "method", "cross-tenant")
    assert ok is None and "R:UNPREVENTED" in note, f"a masked clause folded a dangling escape: {note!r}"
    assert "/tasks/nope.md" in note, note
    assert add.fold(bundle, "method", "cross-tenant", bind="a decision")[0] is None


@pytest.mark.parametrize("fence", ["~~~", "````", "```"])
def test_no_fence_authors_a_rule(bundle, fence):
    """covers: M2, E23, E25 — a fence is a fence in every spelling the markdown grammar allows."""
    t = bundle / "tasks" / "t.md"
    t.write_text(t.read_text() + f"\n## EDGES\n{fence}\n- E5 a rule inside a fence\n{fence}\n")
    ok, note = _cite(bundle, "E5", f"an escape citing a {fence} fence")
    assert ok is None and "R:UNPREVENTED" in note, f"a {fence} fence authored a rule: {note!r}"


def test_a_rule_with_no_text_authors_nothing(bundle):
    """covers: M2, E25 — a bare id is the heading-that-names-nothing one level down."""
    t = bundle / "tasks" / "t.md"
    t.write_text(t.read_text() + "\n## EDGES\n- M7\n")
    ok, note = _cite(bundle, "M7", "an escape citing a bare id")
    assert ok is None and "R:UNPREVENTED" in note, f"a rule with no text authored something: {note!r}"


def test_two_escapes_cannot_prevent_each_other(bundle):
    """covers: M2, E25 — an escape still open stops nothing, so a two-cycle binds exactly as much as
    naming itself: the promise defeated end to end with no hand edit (the twelfth T2 refute)."""
    for n, lesson in ((1, "the first escape"), (2, "the second escape")):
        other = "M2" if n == 1 else "M1"
        assert add.learn(bundle, "method", lesson, evidence="/tasks/t.md", escape=True, why_missed="w",
                         prevention=f"rule → /specs/method.md#{other}")[0]
    for lesson in ("the first escape", "the second escape"):
        ok, note = add.fold(bundle, "method", lesson)
        assert ok is None and "R:UNPREVENTED" in note, f"{lesson} was prevented by an open escape: {note!r}"


@pytest.mark.parametrize("ref", ["/specs/method.md# M1", "/specs/method.md #M1", "/specs/method.md# M1"])
def test_an_address_reads_the_same_everywhere(bundle, ref):
    """covers: M2, E23, E25, E26 — found by the thirteenth T2 refute: `resolve` strips whitespace on
    both sides of the `#` and the open-escape rung did not, so a spaced self-address folded."""
    assert add.learn(bundle, "method", "a cross-tenant read escaped", evidence="/tasks/t.md", escape=True,
                     why_missed="w", prevention=f"rule → {ref}")[0]
    ok, note = add.fold(bundle, "method", "cross-tenant", bind="a decision")
    assert ok is None and "R:UNPREVENTED" in note, f"a spaced self-address bound a decision: {note!r}"


def test_a_fence_in_a_list_item_authors_nothing(bundle):
    """covers: M2, E25, E26 — a fence is a fence wherever markdown lets one open."""
    t = bundle / "tasks" / "t.md"
    t.write_text(t.read_text() + "\n## EDGES\n- ```\n  - E5 a rule inside a list-item fence\n  ```\n")
    ok, note = _cite(bundle, "E5", "an escape citing a list-item fence")
    assert ok is None and "R:UNPREVENTED" in note, f"a list-item fence authored a rule: {note!r}"


@pytest.mark.parametrize("tail, seen", [
    (" · prevention: · x", "nothing after"),
    (" · prevention : rule → /tasks/nope.md", "/tasks/nope.md"),
])
def test_a_written_clause_is_never_called_absent(bundle, tail, seen):
    """covers: M2, A6, E13, E26 — a clause with nothing after the label, or a space before the
    colon, is MALFORMED — never "no clause at all", which names the wrong thing to fix."""
    assert add.learn(bundle, "method", "a cross-tenant read escaped", evidence="/tasks/t.md", escape=True,
                     why_missed="w", prevention="rule → /tasks/t.md")[0]
    p = bundle / "specs" / "method.md"
    p.write_text(p.read_text().replace(" · prevention: rule → /tasks/t.md",
                                       f"{tail} · prevention: rule → /tasks/t.md", 1))
    ok, note = add.fold(bundle, "method", "cross-tenant")
    assert ok is None and "R:UNPREVENTED" in note, f"a malformed clause folded: {note!r}"
    assert seen in note and "no `prevention:` clause" not in note, f"the refusal names the wrong thing: {note!r}"


@pytest.mark.parametrize("opener, closer", [
    ("1. ```text", "   ```"), ("1) ```", "   ```"), ("- - ```", "    ```"),
    ("2. ~~~", "   ~~~"), ("> ```", "> ```"), (">>> ```", ">>> ```"), ("````", "````"),
])
def test_every_fence_opening_authors_nothing(bundle, opener, closer):
    """covers: M2, E25, E26, E27, E28 — every opening authors nothing AND closes: the quote-arrow row
    once refused because the fence never closed, which is a check passing for the wrong reason."""
    t = bundle / "tasks" / "t.md"
    # a fence's CONTENT sits in the container that opened it: an unquoted line is outside the
    # blockquote, and so outside the fence the blockquote carries
    carrier = re.match(r"[>\\s]*", opener).group(0)
    t.write_text(t.read_text() + f"\n## EDGES\n- E1 a real edge\n\n{opener}\n{carrier}- E9 a quoted edge\n"
                 f"{closer}\n- E10 a rule authored after the fence\n")
    ok, note = _cite(bundle, "E9", f"an escape citing {opener}")
    assert ok is None and "R:UNPREVENTED" in note, f"{opener!r} authored a rule: {note!r}"
    ok, note = _cite(bundle, "E10", f"an escape citing the rule after {opener}")
    assert ok is True, f"{closer!r} never closed the fence, so a real rule vanished: {note!r}"


def test_a_fence_is_never_closed_by_its_own_content(bundle):
    """covers: M2, E27, E28 — a run indented inside a fence is CONTENT; closing on it read the whole
    quoted block as authored (the fifteenth T2 refute)."""
    t = bundle / "tasks" / "t.md"
    t.write_text(t.read_text() + "\n## EDGES\n- E1 a real edge\n\n```\nan example:\n    ```\n"
                 "- E9 a quoted edge\n```\n- E10 a rule authored after the fence\n")
    ok, note = _cite(bundle, "E9", "an escape citing a fence's own content")
    assert ok is None and "R:UNPREVENTED" in note, f"an indented run closed the fence early: {note!r}"
    assert _cite(bundle, "E10", "an escape citing the rule after the content")[0] is True


def test_an_indented_heading_still_ends_the_section(bundle):
    """covers: M2, E24, E28 — up to three spaces is still an ATX heading, so `  ## LESSONS` ends the
    authoring section exactly as one at column zero does."""
    t = bundle / "tasks" / "t.md"
    t.write_text(t.read_text() + "\n## EDGES\n- E1 a real edge\n  ## LESSONS\n- M9 a lesson spelling an id\n")
    ok, note = _cite(bundle, "M9", "an escape citing an id under an indented heading")
    assert ok is None and "R:UNPREVENTED" in note, f"an indented heading did not end the section: {note!r}"


def test_a_fence_forges_nothing_in_rules_either(bundle):
    """covers: M2, E27 — the section does not change the answer."""
    t = bundle / "tasks" / "t.md"
    t.write_text(t.read_text() + "\n## RULES\n3. ```text\n   - M4 a quoted must\n   ```\n")
    ok, note = _cite(bundle, "M4", "an escape citing a fenced must")
    assert ok is None and "R:UNPREVENTED" in note, f"a fence in RULES authored a must: {note!r}"


def test_a_heading_inside_a_fence_is_no_address(bundle):
    """covers: M2, E30, E36 — found by the 22nd T2 refute: `resolve`'s own `_section` is a SECOND
    reader of what a heading is, fence-blind, and the prevention rung consulted it FIRST — so one
    fence authored nothing for an id and a whole section for a heading."""
    t = bundle / "tasks" / "t.md"
    t.write_text(t.read_text() + "\n## LESSONS\n\nthe retro note quoted a node we might write:\n\n"
                 "```markdown\n## my example\n- E9 a quoted edge\n```\n")
    ok, note = _cite(bundle, "my-example", "an escape citing a heading inside a fence")
    assert ok is None and "R:UNPREVENTED" in note, f"a quoted heading became an address: {note!r}"
    assert add._prevention_resolves(bundle, "/tasks/t.md#E9") is False


@pytest.mark.parametrize("frag", ["checks", "title"])
def test_a_real_heading_and_a_real_key_are_addresses(bundle, frag):
    """covers: M2, A2, E36 — the heading and frontmatter-key forms of a resolvable ref: each could be
    deleted from the resolver with the suite green before this."""
    ok, note = _cite(bundle, frag, f"an escape citing {frag}")
    assert ok is True, f"the {frag} form no longer resolves: {note!r}"


def test_a_closer_sits_in_its_openers_container(bundle):
    """covers: M2, E28, E29, E36 — the discriminating direction the earlier row never reached: a
    DOCUMENT-level fence is not closed by a quote-carried run, so the rules after it stay quoted."""
    t = bundle / "tasks" / "t.md"
    t.write_text(t.read_text().replace(
        "## EDGES\n", "## EDGES\n- E1 a real edge\n```\n- E9 a quoted edge\n> ```\n"
        "- E10 a rule the fence still swallows\n", 1))
    for frag in ("E9", "E10"):
        ok, note = _cite(bundle, frag, f"an escape citing {frag} past a quoted closer")
        assert ok is None and "R:UNPREVENTED" in note, f"a quote-carried closer ended a doc fence: {note!r}"


QUOTED_DELTA = ("\n## LESSONS\n\nthe retro quoted a delta we might write:\n\n"
                "```markdown\n- [ADD · Z9 · open · 2026-01-01] an EXAMPLE delta (evidence: nowhere)\n"
                "- E9 an EXAMPLE edge in the same fence\n```\n")


@pytest.mark.parametrize("frag", ["Z9", "E9"])
def test_one_fence_gives_one_answer(bundle, frag):
    """covers: M2, E30, E36, E37 — found by the 23rd T2 refute: `_delta_ids` is `resolve`'s THIRD
    fragment reader and was fence-blind, so the very fence that refused the quoted `- E9` handed
    over the quoted delta id beside it, and the escape folded and bound a decision at exit 0."""
    t = bundle / "tasks" / "t.md"
    t.write_text(t.read_text() + QUOTED_DELTA)
    ok, note = _cite(bundle, frag, f"an escape citing the fenced {frag}")
    assert ok is None and "R:UNPREVENTED" in note, f"a fence authored {frag}: {note!r}"


def test_a_quoted_delta_is_no_open_delta(bundle):
    """covers: M2, A5, E19, E37 — the mirror the same blindness produced: `deltas` listed the
    fenced EXAMPLE as a real open delta and `open_delta_count` counted it, so the board asked a
    human to drain an example — and a genuine prevention naming it refused as "still open"."""
    (bundle / "specs" / "quality.md").write_text(
        (bundle / "specs" / "quality.md").read_text() + QUOTED_DELTA)
    assert "Z9" not in " ".join(_open(bundle, lens="quality")), "a quoted example is an open delta"
    assert add.open_delta_count((bundle / "specs" / "quality.md").read_text()) == 0


@pytest.mark.parametrize("hashes", ["#", "###"])
def test_a_section_opens_at_level_two_only(bundle, hashes):
    """covers: M2, E35, E37 — M2 freezes "a deeper `###` opens none", and the authoring walk reads
    both a title and a sub-heading as CONTENT; the slicer behind `resolve` opened a section for
    each, so a prevention naming one folded (the 23rd T2 refute's sibling, unbound until now)."""
    t = bundle / "tasks" / "t.md"
    t.write_text(t.read_text() + f"\n{hashes} my example\n\nsome prose under it\n")
    ok, note = _cite(bundle, "my-example", f"an escape citing a {hashes} heading")
    assert ok is None and "R:UNPREVENTED" in note, f"`{hashes}` opened a section: {note!r}"


@pytest.mark.parametrize("frag", ["scope", "verified"])
def test_an_unfilled_slot_is_no_address(bundle, frag):
    """covers: M2, A2, E37 — the *check that passes on nothing* inside the address grammar itself:
    `scope:` seeds EMPTY and `verified:` starts `[]`, and an empty slot resolved, so a prevention
    named a key nobody had filled and the escape folded (the 23rd T2 refute's sibling)."""
    ok, note = _cite(bundle, frag, f"an escape citing the empty {frag}")
    assert ok is None and "R:UNPREVENTED" in note, f"an unfilled `{frag}` was an address: {note!r}"


GRAMMAR_FENCE = ("## Deltas\n\nthe grammar a carried lesson is written in:\n\n"
                 "```markdown\n- [ADD · M1 · open · 2026-01-01] <the lesson> (evidence: <ref>)\n```\n")


def _quote_the_grammar(bundle, lens="method"):
    """A spec whose `## Deltas` section OPENS with a fenced example of the grammar."""
    p = bundle / "specs" / f"{lens}.md"
    p.write_text(p.read_text().replace("## Deltas\n", GRAMMAR_FENCE, 1))
    return p


def test_a_fence_never_takes_the_delta_learn_writes(bundle):
    """covers: M1, M5, E37, E38 — found by the 24th T2 refute: E37 taught every READER to blank a
    fence and left both writers scanning raw lines, so `learn` wrote the new delta INSIDE the
    fenced example — filed at exit 0 and thereafter invisible to `deltas`, `search`, `status` and
    `fold`, which is worse than folding unprevented: nobody is ever asked to drain it."""
    _quote_the_grammar(bundle)
    assert add.learn(bundle, "method", "the tenant filter dropped a row", evidence="/tasks/t.md",
                     escape=True, why_missed="w", prevention="rule → /tasks/nope.md")[0]
    assert any("tenant filter" in t for t in _open(bundle)), "the delta landed where no reader looks"
    ok, note = add.fold(bundle, "method", "tenant filter")
    assert ok is None and "R:UNPREVENTED" in note, f"a filed escape was forgotten instead: {note!r}"


def test_a_fenced_id_is_no_mint_floor(bundle):
    """covers: M1, E37, E38 — the mint floor reads the live view like every other reader, and the
    id it mints addresses the line it wrote (the 24th read's mutation: the floor's live view killed
    no check in either direction)."""
    _quote_the_grammar(bundle)
    assert add.learn(bundle, "method", "a real lesson", evidence="/tasks/t.md")[0]
    line = _line(bundle, "a real lesson")
    did = re.search(r"· (M\d+) ·", line).group(1)
    # M1, not M2: the fenced example spells `M1` and a fence authors nothing — not a rule, not a
    # delta, and not the floor a mint may not land on. The id it minted addresses the line it wrote.
    assert did == "M1", f"a quoted example raised the mint floor: {line!r}"
    assert add._delta_ids((bundle / "specs" / "method.md").read_text())[did] == line.strip()


@pytest.mark.parametrize("heading", ["### Decisions that bind", "```\n## Decisions that bind\n```"])
def test_a_bound_decision_lands_where_brief_reads_it(bundle, heading):
    """covers: M2, E36, E37, E38 — `_bind_decision` was a FOURTH heading reader (any level,
    fence-blind) while `brief` reads through `_section`, now level-two and fence-aware: `fold
    --bind` reported "bound 1 decision" at exit 0 and the brief could not see it."""
    p = bundle / "specs" / "method.md"
    p.write_text(p.read_text().replace("## Decisions that bind", heading, 1))
    assert add.learn(bundle, "method", "a plain lesson", evidence="/tasks/t.md")[0]
    assert add.fold(bundle, "method", "a plain lesson", bind="every retry carries a key")[0]
    assert "every retry carries a key" in add._section(p.read_text(), "decisions-that-bind"), p.read_text()


def test_join_carries_a_refused_escape_past_a_fence(bundle, tmp_path):
    """covers: M5, E22, E37, E38 — `_merge_deltas` read main's `present` set from raw lines, so a
    delta main merely QUOTES in a fence looked already held and the stream's refused escape was
    dropped at exit 0: a refusal survives the merge only if the delta does."""
    stream = _stream(tmp_path)
    assert add.learn(stream, "method", "the cache served a stale row", evidence="/tasks/s.md",
                     escape=True, why_missed="w", prevention="rule → /tasks/nope.md")[0]
    assert add.fold(stream, "method", "cache served")[0] is None, "the stream itself must refuse it"
    quoted = _line(stream, "cache served")
    p = bundle / "specs" / "method.md"
    p.write_text(p.read_text() + f"\n```markdown\n{quoted}\n```\n")
    assert add.join(bundle, [stream])[0], "the join was refused"
    ok, note = add.fold(bundle, "method", "cache served")
    assert ok is None and "R:UNPREVENTED" in note, f"the merge dropped a refused escape: {note!r}"


def test_a_bound_sentence_is_one_line_and_never_the_marker(bundle):
    """covers: M1, M2, A8, E15, E38 — `--bind` writes into the spec like `learn` does, so it obeys
    the same two laws: one physical line, and the engine's own `· escape` marker cannot ride in
    through it. A newline in the sentence forged a real open escape at exit 0."""
    assert add.learn(bundle, "method", "a plain lesson", evidence="/tasks/t.md")[0]
    forged = ("keys are idempotent\n- [ADD · M9 · open · 2026-01-01] a forged escape "
              "(evidence: /tasks/t.md) · escape · prevention: rule → /tasks/nope.md")
    ok, note = add.fold(bundle, "method", "a plain lesson", bind=forged)
    assert ok is None and "R:UNCAUSED" in note and "escape" in note, f"the marker rode in on --bind: {note!r}"
    assert add.fold(bundle, "method", "a plain lesson", bind="keys are\nidempotent")[0], "a wrap is normalised"
    body = (bundle / "specs" / "method.md").read_text()
    assert "- keys are idempotent (from:" in body, f"the decision spilled onto a second line: {body!r}"
    assert add.open_delta_count(body) == 0
    assert not _open(bundle), "a bound sentence forged a delta"


@pytest.mark.parametrize("empty, filled", [
    ('owner: ""', 'owner: "a name"'), ("notes: '   '", "notes: 'a note'"), ('tags: [""]', 'tags: ["a tag"]')])
def test_an_empty_string_slot_is_no_address(bundle, empty, filled):
    """covers: M2, A2, E37, E38 — E37's "an unfilled slot is no address" was bound for the empty
    LIST only; the empty-string and whitespace-only forms killed no check. The FILLED half is why
    this one cannot pass for the wrong reason: the key must be there to be refused for emptiness
    (the 24th read found the separating input its own mutation needed)."""
    t, key = bundle / "tasks" / "t.md", empty.split(":", 1)[0]
    for slot, want in ((empty, False), (filled, True)):
        t.write_text(re.sub(r"^status: direction$", f"status: direction\n{slot}",
                            t.read_text(), count=1, flags=re.M))
        # the lesson is the fold's match key, so it never carries the slot's own whitespace
        ok, note = _cite(bundle, key, f"an escape citing the {key} slot, filled {want}")
        assert (ok is True) is want, f"`{slot}`: {note!r}"
        if not want:
            assert "R:UNPREVENTED" in note, f"an empty `{key}` was an address: {note!r}"
        t.write_text(re.sub(rf"^{re.escape(slot)}\n", "", t.read_text(), count=1, flags=re.M))


def test_a_fenced_heading_never_takes_the_delta(bundle):
    """covers: M1, M5, E36, E38 — the writer's own heading scan: a `## Deltas` QUOTED in a fence
    above the real one took every line `learn` wrote, and `_section`, `deltas` and `fold` all read
    past it — the filed escape was never seen again (the 24th T2 refute's headline, at the heading)."""
    p = bundle / "specs" / "method.md"
    p.write_text(p.read_text().replace(
        "## Decisions that bind", "```markdown\n## Deltas\n- how a lesson is written\n```\n\n## Decisions that bind", 1))
    assert add.learn(bundle, "method", "the tenant filter dropped a row", evidence="/tasks/t.md",
                     escape=True, why_missed="w", prevention="rule → /tasks/nope.md")[0]
    assert any("tenant filter" in t for t in _open(bundle)), "a quoted heading took the delta"
    # …and it lands in the section it names, not merely somewhere a section-agnostic reader finds
    # it: a writer that writes outside its own section is the next reader's silence.
    assert "tenant filter" in add._section(p.read_text(), "deltas"), p.read_text()
    ok, note = add.fold(bundle, "method", "tenant filter")
    assert ok is None and "R:UNPREVENTED" in note, f"a filed escape was forgotten instead: {note!r}"


@pytest.mark.parametrize("sentence", [
    "~~~ every lister validates its headers", "~~~~~~ a longer run", "~~~", "```` a backtick run",
    "   ~~~ indented three", "[ADD · M9 · open · 2026-01-01] a forged lesson (evidence: nothing)"])
def test_a_bound_sentence_changes_nothing_the_readers_see(bundle, sentence):
    """covers: M2, M5, A8, E38, E39 — found by the 25th T2 refute: `_bind_decision` writes the
    CALLER's sentence at column 0 of the list item, where `learn` always writes its own bracket head
    first — so a sentence leading with a fence run opened a real block and `live_lines` blanked the
    rest of the spec (the dangling escape vanished from `deltas`, `fold` answered R:NOMATCH forever,
    and the engine wrote `open_deltas: 0` itself), while one leading with a delta head forged an
    open delta nobody filed. A8's two named laws are one question: does the sentence change what the
    readers SEE."""
    assert add.learn(bundle, "method", "the lister leaked a null tenant", evidence="/tasks/t.md",
                     escape=True, why_missed="w", prevention="rule → /tasks/nope.md")[0]
    assert add.learn(bundle, "method", "we review every header now", evidence="/tasks/t.md")[0]
    ok, note = add.fold(bundle, "method", "review every header", bind=sentence)
    assert ok is None and "R:UNCAUSED" in note, f"the sentence rewrote the spec: {note!r}"
    body = (bundle / "specs" / "method.md").read_text()
    assert add.open_delta_count(body) == 2, f"a bound sentence moved the count: {body!r}"
    assert any("null tenant" in t for t in _open(bundle)), "the escape fell out of view"
    ok, note = add.fold(bundle, "method", "null tenant")
    assert ok is None and "R:UNPREVENTED" in note, f"the escape stopped refusing: {note!r}"


def test_join_records_rather_than_raises(bundle, tmp_path):
    """covers: A6, E24, E39 — `add init` creates no `tasks/`, so a join of a gated stream raised
    FileNotFoundError with no `R:` code: every exit is a refusal or a record (the 25th T2 read
    reproduced the note the 24th raised)."""
    import shutil
    shutil.rmtree(bundle / "tasks")
    stream = _stream(tmp_path)
    ok, note = add.join(bundle, [stream])
    assert ok is not None, note
    assert (bundle / "tasks" / "s.md").is_file(), f"the joined node never landed: {note!r}"


def test_a_bound_sentence_never_swallows_a_later_section(bundle):
    """covers: M2, A8, E39 — the half of the read-back the delta ids cannot see: in a spec whose
    `## Deltas` sits ABOVE the decisions, a fence run swallows no id and still eats every section
    after it, and the next writer appends a second heading into the dark."""
    p = bundle / "specs" / "method.md"
    p.write_text(p.read_text().replace(
        "## Decisions that bind\n- <the first decision that constrains the rest>\n\n", "", 1)
        + "\n## Decisions that bind\n- <the first decision that constrains the rest>\n\n## Later\n- a section after it\n")
    assert add.learn(bundle, "method", "a plain lesson", evidence="/tasks/t.md")[0]
    ok, note = add.fold(bundle, "method", "a plain lesson", bind="~~~ every lister validates its headers")
    assert ok is None and "R:UNCAUSED" in note, f"a fence run ate the sections after it: {note!r}"
    assert "Later" in [n for _, lv, n in add._headings(p.read_text()) if lv == 2], p.read_text()


def test_a_bound_decision_is_never_read_as_scaffold(bundle):
    """covers: M2, A8, E11, E39, E40 — found by the 26th T2 refute: a decision carrying a bare
    `<tenant>` lands, is REPORTED bound, and every reader then calls the section scaffold — `brief`
    renders it `unauthored="true"` and `doctor` warns — because the engine's own placeholder
    detector cannot tell it from the seed line. A writer does not write what its readers disown."""
    assert add.learn(bundle, "method", "a plain lesson", evidence="/tasks/t.md")[0]
    ok, note = add.fold(bundle, "method", "a plain lesson",
                        bind="every lister refuses an unknown <tenant> header it did not issue")
    assert ok is None and "R:UNCAUSED" in note and "code span" in note, f"a disowned decision landed: {note!r}"
    # …and the same sentence with the placeholder quoted, which is the rule E11 already froze
    assert add.fold(bundle, "method", "a plain lesson",
                    bind="every lister refuses an unknown `<tenant>` header")[0]
    bound = dict((cid, text) for cid, text in add.bind_sections(bundle))
    assert "`<tenant>` header" in bound.get("specs/method", ""), f"the quoted decision never reached the readers: {bound!r}"


def test_a_bound_decision_survives_the_next_bind(bundle):
    """covers: M5, A8, E39, E40 — the read-back's blind half: it compared delta ids and heading
    names, never the decision LINES `bind_sections`, `brief` and `doctor` read, so the next
    `--bind` deleted a hand-written decision the placeholder detector disowned, without a word."""
    p = bundle / "specs" / "method.md"
    p.write_text(p.read_text().replace("- <the first decision that constrains the rest>",
                                       "- a hand-written decision about the <tenant> header", 1))
    for lesson in ("a first lesson", "a second lesson"):
        assert add.learn(bundle, "method", lesson, evidence="/tasks/t.md")[0]
    ok, note = add.fold(bundle, "method", "a first lesson", bind="every retry carries a key")
    assert ok is None and "R:UNCAUSED" in note, f"a bind ate a decision nobody retired: {note!r}"
    assert "<tenant> header" in p.read_text(), "the decision was deleted anyway"


@pytest.mark.parametrize("kw", [dict(lesson="a lesson (evidence: runs/1.md) in the text"),
                                dict(evidence="/tasks/t.md (evidence: runs/1.md)")])
def test_the_evidence_marker_rides_in_through_no_flag(bundle, kw):
    """covers: M1, E10, E14, E40 — the marker is the engine's own in EVERY value, not just the two
    an earlier read named: `_delta_identity` keys on it, so a lesson carrying one collapsed two
    genuinely different lessons into one identity and `join` dropped both."""
    lesson = kw.pop("lesson", "an ordinary lesson")
    ok, note = add.learn(bundle, "method", lesson, evidence=kw.pop("evidence", "/tasks/t.md"))
    assert ok is None and "(evidence:" in note, f"the marker rode in: {note!r}"


def test_join_keeps_two_lessons_that_only_look_alike(bundle, tmp_path):
    """covers: M5, E22, E33, E40 — `_delta_identity` truncated at the FIRST `(evidence:` while the
    tail reader keys on the LAST, so two hand-written lessons that differ only past the marker were
    one conflict and BOTH refused escapes were dropped at the merge."""
    streams = []
    for name, tenant in (("sa", "A"), ("sb", "B")):
        s = _stream(tmp_path, name)
        assert add.learn(s, "method", "the export endpoint leaked", evidence="/tasks/s.md",
                         escape=True, why_missed="w", prevention="rule → /tasks/nope.md")[0]
        p = s / "specs" / "method.md"
        p.write_text(p.read_text().replace("the export endpoint leaked",
                                           f"the export endpoint leaked (evidence: runs/1.md) on tenant {tenant}", 1))
        streams.append(s)
    assert add.join(bundle, streams)[0], "the join was refused"
    open_now = _open(bundle)
    assert len(open_now) == 2, f"the merge collapsed two lessons into one: {open_now!r}"
    for tenant in ("A", "B"):
        ok, note = add.fold(bundle, "method", f"on tenant {tenant}")
        assert ok is None and "R:UNPREVENTED" in note, f"tenant {tenant} lost its refusal: {note!r}"


def test_the_gate_and_the_fold_rung_read_one_nodes_musts(bundle):
    """covers: M2, E30, E40 — `edges_of` was routed through the one reader and the explore gate's
    own Must reader was not: `add gate <explore> PASS` demanded a finding for an `M9` spelled only
    inside a fence while the fold rung called the same id unauthored."""
    from conftest import draft_direction
    cid, _ = add.new(bundle, "Task", "ex", title="an explore", depth="standard",
                     kind="explore", scope=["notes.md"])
    draft_direction(bundle, cid)
    p = bundle / "tasks" / "ex.md"
    body = p.read_text()
    for heading, text in (("PLAN", "contract: answers\nbudget: ~20 tool calls\nscope: notes.md"),
                          ("RULES", "- M1 a real question\n```markdown\n- M9 a quoted example\n```"),
                          ("FINDINGS", "- F1 (answers M1) · the path is atomic (evidence: notes.md)")):
        lines = body.splitlines()
        i = next(j for j, l in enumerate(lines) if l.strip() == f"## {heading}")
        end = next((j for j in range(i + 1, len(lines)) if lines[j].startswith("## ")), len(lines))
        body = "\n".join(lines[:i + 1] + [text] + lines[end:])
    n = add.read(p, "T2")
    add.write(p, f"---\n{n['raw']}\n---\n{body}")
    assert "M9" not in add.rules_of({"path": p, "body": body}), "the fold rung already saw it"
    assert add.freeze(bundle, cid, by="human:t", authority="human")[0]
    # the gate answers the way the fold rung does: it never demands a finding for a quoted example
    ok, note = add.gate(bundle, cid, "PASS", by="human:t")
    assert ok, f"the gate demanded a Must nobody authored: {note!r}"


@pytest.mark.parametrize("run, where", [("```", "## Now"), ("~~~", "## Now"), ("```", "## Deltas")])
def test_a_lesson_is_never_filed_into_the_void(bundle, run, where):
    """covers: M1, M5, E38, E39, E41 — found by the 27th T2 refute: a fence that NEVER closes made
    `learn` report `recorded on specs/method as M1` at exit 0 while the line landed inside it —
    `deltas` said none, `search` found nothing, `fold` answered R:NOMATCH forever, `show` answered
    R:NOSUCHNODE for the id `learn` had just handed back, and the engine wrote `open_deltas: 0`
    itself. `--bind` got a read-back and the primary escape writer never did."""
    p = bundle / "specs" / "method.md"
    p.write_text(p.read_text().replace(where, f"{where}\n{run} an example nobody closed\nsome prose", 1))
    before = p.read_text()
    ok, note = add.learn(bundle, "method", "the nightly export dropped 3 rows", evidence="/tasks/t.md",
                         escape=True, why_missed="w", prevention="rule → /tasks/nope.md")
    assert ok is None and "R:UNREADABLE" in note and "method" in note, f"the lesson filed into the void: {note!r}"
    assert p.read_text() == before, "a refused lesson wrote something"
    # …and the same call lands once the fence closes: the refusal is about the spec, not the lesson
    p.write_text(before.replace("some prose", f"some prose\n{run}", 1))
    assert add.learn(bundle, "method", "the nightly export dropped 3 rows", evidence="/tasks/t.md",
                     escape=True, why_missed="w", prevention="rule → /tasks/nope.md")[0]
    assert any("nightly export" in t for t in _open(bundle)), p.read_text()


@pytest.mark.parametrize("heading", ["## RULES:", "## RULES (frozen)", "## RULES — the contract"])
def test_one_reader_of_a_named_section(bundle, heading):
    """covers: M2, E30, E31, E41 — `_authored_rules` re-emitted the author's heading VERBATIM while
    `_section_of` matches it exactly, so a `## RULES (frozen)` heading left `rules_of` and the gate
    seeing zero Musts while the fold rung resolved ids under it and folded (the 27th read's
    sibling): the walker re-emits the section it RECOGNISED, canonical."""
    t = bundle / "tasks" / "t.md"
    t.write_text(t.read_text().replace("## RULES", heading, 1)
                 .replace("- M1 <the rule that must hold>", "- M1 a rule that really must hold", 1))
    node = {"path": t, "body": t.read_text()}
    assert add.rules_of(node) == ["M1"], f"the gate's reader lost the section: {heading!r}"
    ok, note = _cite(bundle, "M1", f"an escape citing a Must under {heading}")
    assert ok is True, f"the fold rung and the gate disagree about {heading!r}: {note!r}"


def test_the_merge_recounts_what_it_carried(bundle, tmp_path):
    """covers: M5, E22, E41 — every other delta writer recomputes `open_deltas:`; the merge did not,
    so `status` reported one open delta where `deltas` listed two (the 27th read's sibling)."""
    assert add.learn(bundle, "method", "main's own lesson", evidence="/tasks/t.md")[0]
    stream = _stream(tmp_path)
    assert add.learn(stream, "method", "the stream's escape", evidence="/tasks/s.md", escape=True,
                     why_missed="w", prevention="rule → /tasks/nope.md")[0]
    assert add.join(bundle, [stream])[0]
    body = (bundle / "specs" / "method.md").read_text()
    assert re.search(r"^open_deltas:\s*(\d+)", body, re.M).group(1) == str(len(_open(bundle))), body[:400]


def _unclosed(bundle, lens="method"):
    p = bundle / "specs" / f"{lens}.md"
    p.write_text(p.read_text().replace("## Now", "## Now\n```\nan example fence nobody closed\nprose", 1))
    return p


def test_a_decision_is_never_filed_into_the_void(bundle):
    """covers: M2, M5, A8, E38, E41, E42 — found by the 28th T2 refute: `learn` got E41's read-back
    and its sibling writer did not. On the very spec where `learn` refuses R:UNREADABLE, `fold
    --bind` reported `bound 1 decision` at exit 0 while `_bind_decision`'s EOF branch wrote the
    decision AND the heading it created inside the never-closing fence — `_section`, `brief` and
    `doctor` all blind to it, and the next bind strands it. The read-back asked only that nothing
    was LOST, never that what it wrote is ADDRESSABLE."""
    # the delta sits ABOVE the fence, so it stays live while both HEADINGS below are blanked —
    # which is the branch that appends at EOF, inside the fence
    p = bundle / "specs" / "method.md"
    p.write_text(p.read_text().replace(
        "## Now", "- [ADD · M1 · open · 2026-01-01] the lister dropped a row (evidence: /tasks/t.md)\n\n## Now", 1))
    p = _unclosed(bundle)
    before = p.read_text()
    assert any("lister dropped" in t for t in _open(bundle)), "the fixture hid the delta itself"
    ok, note = add.fold(bundle, "method", "lister dropped", bind="never ship a lister without a guard")
    assert ok is None and "R:UNREADABLE" in note, f"the decision filed into the void: {note!r}"
    assert p.read_text() == before, "a refused fold wrote something"
    p.write_text(before.replace("prose", "prose\n```", 1))
    assert add.fold(bundle, "method", "lister dropped", bind="never ship a lister without a guard")[0]
    assert "never ship a lister" in add._section(p.read_text(), "decisions-that-bind"), p.read_text()


@pytest.mark.parametrize("ref", ["a\x00b", "tests/test_x.py\x00"])
def test_learn_refuses_a_control_character_in_a_ref(bundle, ref):
    """covers: M1, A6, E42 — a ref is an address: a character no reader can carry is refused where
    every other malformed ref is, at the writer (the 28th read's sibling)."""
    ok, note = add.learn(bundle, "method", "a lesson", evidence="/tasks/t.md", escape=True,
                         why_missed="w", prevention=f"check → {ref}")
    assert ok is None and "R:UNCAUSED" in note and "control character" in note, f"{ref!r}: {note!r}"


def test_the_rung_refuses_a_hand_edited_nul_rather_than_raising(bundle):
    """covers: A6, E24, E42 — and the reader answers too: `_prevention_resolves` handed the NUL
    straight to the filesystem and raised `ValueError: embedded null character`, where every exit
    is a refusal or a record — a hand edit is exactly where one arrives."""
    assert add.learn(bundle, "method", "a lesson", evidence="/tasks/t.md", escape=True,
                     why_missed="w", prevention="check → tests/test_x.py")[0]
    p = bundle / "specs" / "method.md"
    p.write_text(p.read_text().replace("tests/test_x.py", "tests/test\x00x.py", 1))
    ok, note = add.fold(bundle, "method", "a lesson")
    assert ok is None and "R:UNPREVENTED" in note, f"the rung raised instead of refusing: {note!r}"


def test_a_spec_the_engine_cannot_read_refuses(bundle):
    """covers: A6, E24, E42 — a BOM before the frontmatter made `learn` raise `AttributeError:
    'NoneType' has no attribute 'splitlines'` where `doctor` already reports `missing_frontmatter`."""
    p = bundle / "specs" / "method.md"
    p.write_text("﻿" + p.read_text(), encoding="utf-8")
    ok, note = add.learn(bundle, "method", "a lesson", evidence="/tasks/t.md")
    assert ok is None and "specs/method" in note, f"an unreadable spec raised instead: {note!r}"


@pytest.mark.parametrize("prevention, kind, ref", [
    ("check->tests/test_x.py->tail", "check", "tests/test_x.py->tail"),
    ("check → tests/test_x.py", "check", "tests/test_x.py"),
    ("rule->/tasks/t.md#checks", "rule", "/tasks/t.md#checks")])
def test_the_prevention_splits_on_the_first_arrow(bundle, prevention, kind, ref):
    """covers: M1, E7, E42 — M1 freezes "split on the FIRST arrow", and `\\S+` backtracked to the
    LAST one whenever no space separated them: a genuine `check->…` was refused by a message naming
    a kind nobody wrote. The spaced control is why the bound check missed it."""
    ok, note = add.learn(bundle, "method", f"a lesson about {kind}", evidence="/tasks/t.md",
                         escape=True, why_missed="w", prevention=prevention)
    assert ok, f"the split took the last arrow: {note!r}"
    assert f"prevention: {kind} → {ref}" in _line(bundle, f"a lesson about {kind}")


@pytest.mark.parametrize("where", ["## Now", "## Deltas"])
def test_join_never_files_into_the_void(bundle, tmp_path, where):
    """covers: M5, E22, E38, E41, E42, E43 — found by the 29th T2 refute: `learn` and `fold --bind`
    each got the read-back the read before them demanded, and `_merge_deltas` — the THIRD delta
    writer, the one that carries an escape BETWEEN bundles — had none. Joining into a spec whose
    `## Deltas` sits under a fence that never closes exited 0 and wrote the stream's refused escape
    where `deltas`, `status`, `doctor` and `fold` could never see it."""
    stream = _stream(tmp_path)
    assert add.learn(stream, "method", "the cross-tenant read escaped", evidence="/tasks/s.md",
                     escape=True, why_missed="w", prevention="rule → /tasks/nope.md")[0]
    assert add.fold(stream, "method", "cross-tenant")[0] is None, "the stream itself must refuse it"
    p = bundle / "specs" / "method.md"
    p.write_text(p.read_text().replace(where, f"{where}\n```\nan example nobody closed\nprose", 1))
    before = p.read_text()
    ok, note = add.join(bundle, [stream])
    assert ok is None and "R:UNREADABLE" in note, f"the merge filed into the void: {note!r}"
    assert p.read_text() == before, "a refused join wrote a delta anyway"
    assert not (bundle / "tasks" / "s.md").exists(), "a refused join left a partial merge"
    # …and once the fence closes, the carried escape arrives and refuses exactly as its stream did
    p.write_text(before.replace("prose", "prose\n```", 1))
    assert add.join(bundle, [stream])[0], "the join stayed refused after the fence closed"
    ok, note = add.fold(bundle, "method", "cross-tenant")
    assert ok is None and "R:UNPREVENTED" in note, f"the merge dropped the refusal: {note!r}"


def test_join_refuses_an_unreadable_spec_rather_than_raising(bundle, tmp_path):
    """covers: A6, E24, E42, E43 — the same function raised `AttributeError` on a spec whose
    frontmatter a BOM hides, AFTER copying the stream's node: the partial merge R:PHANTOMSTREAM
    exists to forbid."""
    stream = _stream(tmp_path)
    assert add.learn(stream, "method", "a stream lesson", evidence="/tasks/s.md")[0]
    p = bundle / "specs" / "method.md"
    p.write_text("﻿" + p.read_text(), encoding="utf-8")
    ok, note = add.join(bundle, [stream])
    assert ok is None and "specs/method" in note, f"the merge raised instead of refusing: {note!r}"
    assert not (bundle / "tasks" / "s.md").exists(), "a refused join left a partial merge"


@pytest.mark.parametrize("kw", [{}, {"reject": True}, {"bind": "a decision"}])
def test_fold_refuses_an_unreadable_spec_rather_than_raising(bundle, kw):
    """covers: A6, E24, E42, E43 — `learn` got the BOM guard and the rung this node is ABOUT did
    not: plain, `--reject` and `--bind` all raised `AttributeError` at the write."""
    assert add.learn(bundle, "method", "a plain lesson", evidence="/tasks/t.md")[0]
    p = bundle / "specs" / "method.md"
    p.write_text("﻿" + p.read_text(), encoding="utf-8")
    ok, note = add.fold(bundle, "method", "a plain lesson", **kw)
    assert ok is None and "specs/method" in note, f"{kw}: the rung raised instead of refusing: {note!r}"


def _blind(bundle, cause, lens="method"):
    """Make a spec one the engine cannot read, either way it knows how."""
    p = bundle / "specs" / f"{lens}.md"
    if cause == "bom":
        p.write_text("﻿" + p.read_text(), encoding="utf-8")
    else:
        p.write_text(p.read_text().replace("## Now", "## Now\n```\nan example nobody closed\nprose", 1))
    return p


@pytest.mark.parametrize("cause", ["bom", "fence"])
@pytest.mark.parametrize("kw", [{}, {"reject": True}, {"bind": "a decision"}])
def test_fold_refuses_a_spec_it_cannot_read_for_either_cause(bundle, cause, kw):
    """covers: A6, E24, E42, E43, E44 — found by the 30th T2 refute: E43 freezes that `fold`
    refuses R:UNREADABLE for BOTH causes, and the guard read `if why and node["raw"] is None` — so
    the fence branch was dead and the check that looked like it covered the clause parametrized the
    three DISPOSITIONS while exercising only the BOM. Under a fence all three answered R:NOMATCH,
    telling the author their match string was wrong while an open escape sat hidden."""
    assert add.learn(bundle, "method", "the cross-tenant read escaped", evidence="/tasks/t.md",
                     escape=True, why_missed="w", prevention="rule → /tasks/nope.md")[0]
    _blind(bundle, cause)
    ok, note = add.fold(bundle, "method", "cross-tenant", **kw)
    assert ok is None and "R:UNREADABLE" in note, f"{cause} · {kw}: {note!r}"


@pytest.mark.parametrize("cause", ["bom", "fence"])
def test_doctor_never_repairs_from_a_body_it_cannot_read(bundle, cause):
    """covers: M5, A6, E24, E41, E43, E44 — `doctor --sync` is the FOURTH writer into a spec, and
    the one every R:UNREADABLE refusal's own `next:` sends the author to: on a fence-blinded spec it
    recomputed `open_deltas: 1 -> 0` at exit 0, erasing the last trace of an escape its own `fold`
    refused; on a BOM it raised at `set_key` after rewriting an earlier spec."""
    assert add.learn(bundle, "method", "the cross-tenant read escaped", evidence="/tasks/t.md",
                     escape=True, why_missed="w", prevention="rule → /tasks/nope.md")[0]
    p = _blind(bundle, cause)
    before = p.read_text()
    changed, note = add.doctor_sync(bundle)
    assert changed is not None, f"doctor raised on a spec it cannot read: {note!r}"
    assert re.search(r"^open_deltas:\s*1", before.lstrip("﻿"), re.M), "the fixture lost its counter"
    assert p.read_text() == before, f"--sync repaired from a body it cannot read: {note!r}"
    assert "method" in note and "read" in note, f"--sync skipped it silently: {note!r}"


@pytest.mark.parametrize("cause", ["bom", "fence"])
def test_doctor_names_the_spec_no_writer_can_land_in(bundle, cause):
    """covers: A6, E24, E43, E44 — every R:UNREADABLE refusal says `add doctor names it`, and doctor
    named the COUNTER instead (`delta_count_drift`), so the way out the engine points at was inert:
    a refusal an author cannot act on is one they route around."""
    _blind(bundle, cause)
    findings = add.doctor(bundle)
    codes = [f["code"] for f in findings]
    assert "unreadable_spec" in codes, f"doctor still cannot name it: {codes}"
    assert "delta_count_drift" not in codes, "doctor invited the repair that erases the escape"


def test_a_join_that_carries_nothing_is_never_refused(bundle, tmp_path):
    """covers: M5, E43, E44 — the pre-flight asked about every stream's specs, including a stream
    with no ADMITTED node, so a join that would write nothing was refused over a spec it would
    never have touched (the 30th read's 🟡)."""
    home = tmp_path.parent / f"{tmp_path.name}_ungated"
    home.mkdir()
    s = home / ".add"
    assert add.init(s, "code", "S")
    add.new(s, "Task", "u", title="u")
    assert add.learn(s, "method", "a lesson nobody gated", evidence="/tasks/u.md")[0]
    _blind(bundle, "fence")
    ok, note = add.join(bundle, [s])
    assert ok is not None, f"a join that carries nothing was refused: {note!r}"


def test_join_refuses_a_stream_spec_no_reader_can_see(bundle, tmp_path):
    """covers: M5, E22, E38, E40, E43, E45 — found by the 31st T2 refute: the pre-flight asked
    `unreadable_spec` of MAIN's spec, and the escape lives in the STREAM's. A never-closing fence
    there makes `_delta_lines` yield [] — indistinguishable from a stream that filed nothing — so
    `join` reported `joined 1 stream(s) · specs union-merged` at exit 0 and the refused escape was
    gone, with the worktree about to be discarded. A BOM on the same file carried it through, so
    the two causes disagreed."""
    stream = _stream(tmp_path)
    assert add.learn(stream, "method", "the cross-tenant read escaped", evidence="/tasks/s.md",
                     escape=True, why_missed="w", prevention="rule → /tasks/nope.md")[0]
    sp = stream / "specs" / "method.md"
    sp.write_text(sp.read_text().replace("## Deltas", "## Deltas\n```\na fenced example nobody closed", 1))
    ok, note = add.join(bundle, [stream])
    assert ok is None and "R:UNREADABLE" in note and "method" in note, f"the merge dropped it: {note!r}"
    assert not _open(bundle), "a refused join merged something"
    # …and with the fence closed the escape arrives and refuses in main exactly as in its stream
    sp.write_text(sp.read_text().replace("a fenced example nobody closed",
                                         "a fenced example nobody closed\n```", 1))
    assert add.join(bundle, [stream])[0], "the join stayed refused after the fence closed"
    ok, note = add.fold(bundle, "method", "cross-tenant")
    assert ok is None and "R:UNPREVENTED" in note, f"the merge dropped the refusal: {note!r}"


def test_a_hard_stopped_stream_never_blocks_a_join(bundle, tmp_path):
    """covers: M5, E43, E44, E45 — two readers of "does this stream contribute": the pre-flight
    asked "is there a gated node" and the merge asks "…that is not HARD-STOP", so one rejected
    stream — the security case — refused the whole wave's join over a spec it would never touch."""
    stream = _stream(tmp_path, "hs")
    p = stream / "tasks" / "s.md"
    p.write_text(p.read_text().replace("outcome: PASS", "outcome: HARD-STOP", 1))
    assert add.learn(stream, "method", "a lesson from a rejected stream", evidence="/tasks/s.md")[0]
    _blind(bundle, "fence")
    ok, note = add.join(bundle, [stream])
    assert ok is not None, f"a HARD-STOPped stream blocked the join: {note!r}"
    assert "HARD-STOP" in note, f"the skip went unreported: {note!r}"


def test_a_bound_decision_that_blinds_only_itself(bundle):
    """covers: M2, A8, E42, E45 — the discriminating input for E42's addressability read-back, which
    E44's cause guard had left unreachable: in a spec whose decisions sit LAST, a fence-run sentence
    swallows no id and no later heading, so every preservation comparison passes and only "is what I
    wrote addressable" can refuse."""
    p = bundle / "specs" / "method.md"
    body = p.read_text()
    section = "## Decisions that bind\n- <the first decision that constrains the rest>\n\n"
    assert section in body
    p.write_text(body.replace(section, "", 1).rstrip("\n") + "\n\n" + section)
    assert add.learn(bundle, "method", "a plain lesson", evidence="/tasks/t.md")[0]
    ok, note = add.fold(bundle, "method", "a plain lesson", bind="~~~ every lister validates its headers")
    assert ok is None and "R:UNREADABLE" in note, f"the decision blinded itself and landed: {note!r}"


def test_doctor_suppresses_a_drift_it_cannot_honestly_count(bundle):
    """covers: M5, E41, E44, E45 — the 31st read caught this clause's own check passing with its
    subject withheld: it blinded a spec that held NO delta, so declared == actual == 0 and no drift
    could have been reported whatever the code did."""
    assert add.learn(bundle, "method", "the cross-tenant read escaped", evidence="/tasks/t.md",
                     escape=True, why_missed="w", prevention="rule → /tasks/nope.md")[0]
    assert re.search(r"^open_deltas:\s*1", (bundle / "specs" / "method.md").read_text(), re.M)
    _blind(bundle, "fence")
    codes = [f["code"] for f in add.doctor(bundle)]
    assert "unreadable_spec" in codes, f"doctor stopped naming it: {codes}"
    assert "delta_count_drift" not in codes, "doctor invited the repair that erases the escape"


SEPARATORS = ["\u2028", "\u2029", "\x85", "\x0c", "\x0b", "\x1c", "\x1e"]


def _wrapped_escape(bundle, lens="method"):
    """An escape whose tail the grammar joins from a continuation line — the unit E17/E22 froze."""
    assert add.learn(bundle, lens, "the wrapped escape lesson", evidence="/tasks/t.md", escape=True,
                     why_missed="no check", prevention="check → /specs/nope.md")[0]
    p = bundle / "specs" / f"{lens}.md"
    head = _line(bundle, "wrapped escape lesson", lens=lens)
    p.write_text(p.read_text().replace(
        head, head.split(" · escape")[0] + "\n  · escape" + head.split(" · escape")[1], 1))
    return p


@pytest.mark.parametrize("sep", SEPARATORS)
def test_a_writer_indexes_the_lines_its_caller_split(bundle, sep):
    """covers: M2, M5, E17, E22, E41, E46 — found by the 32nd T2 refute: the walkers rebuilt the
    caller's `splitlines(keepends=True)` list with `"\\n".join(rstrip("\\n"))`, and Python splits on
    eight more line boundaries than that — so ONE such character above `## Deltas` re-split a line,
    shifted every index by one, and `learn` spliced its new head between a wrapped escape's head and
    its continuation: the dangling escape folded at exit 0 and an innocent lesson refused in its
    place. The axis the earlier check held at one value was the BODY, not the flag."""
    p = _wrapped_escape(bundle)
    p.write_text(p.read_text().replace("## Now", f"## Now{sep}a line the author wrapped", 1))
    assert add.learn(bundle, "method", "an innocent plain lesson", evidence="/tasks/t.md")[0]
    ok, note = add.fold(bundle, "method", "wrapped escape lesson")
    assert ok is None and "R:UNPREVENTED" in note, f"{sep!r}: the dangling escape folded: {note!r}"
    ok, note = add.fold(bundle, "method", "an innocent plain lesson")
    assert ok, f"{sep!r}: an innocent lesson inherited the escape's tail: {note!r}"


@pytest.mark.parametrize("sep", ["\u2028", "\x0c"])
def test_join_carries_a_wrapped_escape_past_a_separator(bundle, tmp_path, sep):
    """covers: M5, E22, E38, E45, E46 — the merge's own harvester zipped the caller's lines against
    a LONGER walk, so it dropped the escape's head and carried its orphan tail: `join` reported
    success and the stream's refused escape was gone."""
    stream = _stream(tmp_path)
    sp = _wrapped_escape(stream)
    sp.write_text(sp.read_text().replace("## Now", f"## Now{sep}a line the author wrapped", 1))
    assert add.fold(stream, "method", "wrapped escape")[0] is None, "the stream itself must refuse it"
    ok, note = add.join(bundle, [stream])
    assert ok, f"{sep!r}: {note!r}"
    assert any("wrapped escape lesson" in t for t in _open(bundle)), f"{sep!r}: the merge lost the head"
    ok, note = add.fold(bundle, "method", "wrapped escape lesson")
    assert ok is None and "R:UNPREVENTED" in note, f"{sep!r}: main dropped the refusal: {note!r}"


MARKER_CASES = ["· escape", "· Escape", "· ESCAPE", "·escape", "·\tescape", "· eScApE"]


@pytest.mark.parametrize("marker", MARKER_CASES)
def test_the_marker_is_read_however_it_is_cased(bundle, marker):
    """covers: M2, E13, E21, E32, E47 — found by the 33rd T2 refute: `ESCAPE_MARK` carried no
    `re.I` while its sibling `PREVENTION_TAIL` does, so one byte — `· escape` to `· Escape` —
    degraded the whole delta to prose and `fold --bind` folded the dangling escape and bound a
    decision at exit 0. The spacing axis was swept and the CASE axis pinned at one value, while the
    clause one level down (`· Prevention:`) sweeps case and refuses correctly."""
    assert add.learn(bundle, "method", "the export endpoint leaked cross-tenant", evidence="/tasks/t.md",
                     escape=True, why_missed="no check", prevention="check → /tasks/nope.md")[0]
    p = bundle / "specs" / "method.md"
    p.write_text(p.read_text().replace("· escape", marker, 1))
    for kw in ({}, {"bind": "every lister validates its tenant header"}):
        ok, note = add.fold(bundle, "method", "export endpoint", **kw)
        assert ok is None and "R:UNPREVENTED" in note, f"{marker!r} {kw}: {note!r}"


@pytest.mark.parametrize("marker", ["· Escape", "· ESCAPE"])
def test_a_cycle_survives_a_miscased_marker(bundle, marker):
    """covers: M2, E25, E47 — the harm reaches a delta nobody edited: with a two-escape cycle,
    capitalising only B's marker made `_names_an_open_escape` call B prose, so A — spelled exactly
    as `learn` wrote it — folded at exit 0 while `deltas` still listed B open."""
    for lesson, other in (("escape A", "M2"), ("escape B", "M1")):
        assert add.learn(bundle, "method", lesson, evidence="/tasks/t.md", escape=True,
                         why_missed="w", prevention=f"rule → /specs/method.md#{other}")[0]
    p = bundle / "specs" / "method.md"
    b = _line(bundle, "escape B")
    p.write_text(p.read_text().replace(b, b.replace("· escape", marker, 1), 1))
    ok, note = add.fold(bundle, "method", "escape A")
    assert ok is None and "R:UNPREVENTED" in note, f"{marker!r}: the cycle broke on a case change: {note!r}"


@pytest.mark.parametrize("value", ["the lesson", "--evidence"])
@pytest.mark.parametrize("marker", ["· Escape", "· ESCAPE"])
def test_the_miscased_marker_rides_in_through_no_flag(bundle, value, marker):
    """covers: M1, E14, E18, E47 — the writer's guards were case-sensitive too, so the marker the
    reader now reads could still ride in through a flag: all four sites move together."""
    kw = {"evidence": f"/tasks/t.md) {marker} · prevention: rule → /tasks/nope.md"} if value == "--evidence" else {}
    lesson = "a plain lesson" if value == "--evidence" else f"a plain lesson {marker} · prevention: rule → x"
    ok, note = add.learn(bundle, "method", lesson, evidence=kw.get("evidence", "/tasks/t.md"))
    assert ok is None and "R:UNCAUSED" in note, f"{marker!r} in {value}: {note!r}"


@pytest.mark.parametrize("marker", ["· Escape", "· ESCAPE"])
def test_a_bound_sentence_never_carries_a_miscased_marker(bundle, marker):
    """covers: M1, M2, A8, E38, E47 — and `--bind`'s guard with them."""
    assert add.learn(bundle, "method", "a plain lesson", evidence="/tasks/t.md")[0]
    ok, note = add.fold(bundle, "method", "a plain lesson",
                        bind=f"a decision {marker} · prevention: check → /tasks/nope.md")
    assert ok is None and "R:UNCAUSED" in note, f"{marker!r}: {note!r}"


@pytest.mark.parametrize("indent", ["\x0c", "\x1c", "\u2028", "\x0b", "  "])
def test_a_tail_that_belongs_to_no_delta_refuses(bundle, indent):
    """covers: M2, A9, E23, E46, E47 — a continuation indented with a character Python SPLITS on is
    both whitespace and a line boundary, so the indent became the split: the tail left the joined
    unit, the head stopped being an escape, and it folded at exit 0 with a dangling prevention. A
    tail that belongs to no delta is malformed, and the refusing reading wins (M2)."""
    assert add.learn(bundle, "method", "the wrapped escape lesson", evidence="/tasks/t.md", escape=True,
                     why_missed="no check", prevention="check → /specs/nope.md")[0]
    p = bundle / "specs" / "method.md"
    head = _line(bundle, "wrapped escape lesson")
    p.write_text(p.read_text().replace(
        head, head.split(" · escape")[0] + "\n" + indent + "· escape" + head.split(" · escape")[1], 1))
    ok, note = add.fold(bundle, "method", "wrapped escape lesson")
    assert ok is None and "R:UNPREVENTED" in note, f"{indent!r}: a severed tail folded: {note!r}"


def test_a_join_that_files_into_another_lens_is_never_refused(bundle, tmp_path):
    """covers: M5, E43, E44, E47 — the pre-flight's own "does this stream file into THIS spec"
    term: without it a join is refused over a blinded main spec the contributing stream never
    writes to — E44's principle at spec granularity, where it was bound only at stream granularity
    (the 33rd read's surviving mutant)."""
    stream = _stream(tmp_path)
    assert add.learn(stream, "quality", "a lesson for another lens", evidence="/tasks/s.md")[0]
    _blind(bundle, "fence")     # method.md, which this stream files nothing into
    ok, note = add.join(bundle, [stream])
    assert ok is not None, f"a join was refused over a spec it never touches: {note!r}"
    assert any("another lens" in t for t in _open(bundle, lens="quality")), note


def test_a_decision_lands_in_a_spec_whose_sections_end_it(bundle):
    """covers: M2, A8, E45, E46, E47 — the per-line `levels` walk, bound on its own: an ordinary
    decision in a spec whose decisions sit LAST raised IndexError under the rejoin, and the check
    that caught it also carried E45's after-guard — one check, two clauses."""
    p = bundle / "specs" / "method.md"
    body = p.read_text()
    section = "## Decisions that bind\n- <the first decision that constrains the rest>\n\n"
    p.write_text(body.replace(section, "", 1).rstrip("\n") + "\n\n" + section)
    assert add.learn(bundle, "method", "a plain lesson", evidence="/tasks/t.md")[0]
    ok, note = add.fold(bundle, "method", "a plain lesson", bind="every retry carries a key")
    assert ok, f"an ordinary decision could not land: {note!r}"
    assert "every retry carries a key" in add._section(p.read_text(), "decisions-that-bind")


WRAP_AT = ["· escape", "· why-missed", "· prevention:", "escape lesson", "(evidence:"]


@pytest.mark.parametrize("sep", ["\n", "\x0c", "\u2028", "\x1e"])
@pytest.mark.parametrize("at", WRAP_AT)
def test_a_severed_tail_refuses_wherever_the_wrap_falls(bundle, sep, at):
    """covers: M2, A9, A10, E23, E46, E47, E48 — found by the 34th T2 refute: E47's own guard
    enumerated the SHAPE the read that named it happened to produce (`^·`) instead of asserting the
    property (does this stranded line CARRY an escape's tail). Wrap one word earlier — the shape
    E17 blesses — and the orphan starts with a word, the head stops being an escape, and it folds
    at exit 0. The severing character was swept over five values; the WRAP POSITION was held at
    one, and the position is the axis that matters. A plain unindented `\n` reproduces it."""
    assert add.learn(bundle, "method", "the wrapped escape lesson", evidence="/tasks/t.md", escape=True,
                     why_missed="no check", prevention="check → /specs/nope.md")[0]
    p = bundle / "specs" / "method.md"
    head = _line(bundle, "wrapped escape lesson")
    if at not in head:
        pytest.skip(f"{at!r} not in the delta")
    i = head.index(at)
    p.write_text(p.read_text().replace(head, head[:i].rstrip() + sep + head[i:], 1))
    for kw in ({}, {"bind": "every tenant read carries a key"}):
        ok, note = add.fold(bundle, "method", "wrapped escape lesson", **kw)
        assert ok is None and "R:UNPREVENTED" in note, f"wrap at {at!r} with {sep!r} {kw}: {note!r}"


def test_a_clause_severed_off_a_resolving_tail_still_refuses(bundle):
    """covers: M2, A9, E13, E21, E48 — the head keeps a prevention that RESOLVES and only the
    second clause is severed off: `_prevention_of` reads a complete escape, M2's "every clause it
    finds must resolve" finds nothing to refuse, and the dangling one folds away unread."""
    assert add.learn(bundle, "method", "a lesson with two clauses", evidence="/tasks/t.md", escape=True,
                     why_missed="no check", prevention="check → /tasks/t.md")[0]
    p = bundle / "specs" / "method.md"
    head = _line(bundle, "two clauses")
    p.write_text(p.read_text().replace(
        head, head + "\n and also · prevention: rule → /tasks/nope.md", 1))
    ok, note = add.fold(bundle, "method", "two clauses")
    assert ok is None and "R:UNPREVENTED" in note, f"a severed second clause folded: {note!r}"


@pytest.mark.parametrize("at", ["· escape", "escape lesson"])
def test_join_never_launders_a_severed_escape(bundle, tmp_path, at):
    """covers: M2, M5, A9, E22, E38, E46, E47, E48 — `_delta_lines` rebuilds only the lines
    `delta_spans` HOLDS, so the merge dropped the orphan tail and main folded a laundered,
    marker-less delta at exit 0 — even in the shape E47 already bound, where the stream's own
    `fold` refused. E46 froze "main holds the head as well as the tail"; its check held the escape
    WHOLE and never carried a SEVERED one through."""
    stream = _stream(tmp_path)
    assert add.learn(stream, "method", "the wrapped escape lesson", evidence="/tasks/t.md", escape=True,
                     why_missed="no check", prevention="check → /specs/nope.md")[0]
    sp = stream / "specs" / "method.md"
    head = _line(stream, "wrapped escape lesson")
    i = head.index(at)
    sp.write_text(sp.read_text().replace(head, head[:i].rstrip() + "\n" + head[i:], 1))
    assert add.fold(stream, "method", "wrapped escape lesson")[0] is None
    ok, note = add.join(bundle, [stream])
    assert ok is None and ("R:UNPREVENTED" in note or "R:UNREADABLE" in note), \
        f"a severed escape was merged: {note!r}"
    assert "escape" not in (bundle / "specs" / "method.md").read_text() or \
        "wrapped escape lesson" not in (bundle / "specs" / "method.md").read_text(), \
        "the merge wrote the laundered head into main"


@pytest.mark.parametrize("where", ["above", "inside-a-fence", "another-section"])
def test_prose_that_quotes_a_clause_blocks_no_fold(bundle, where):
    """covers: M2, A6, A10, E9, E18, E48 — A10 rules the silence the 34th read raised: the engine
    looks for a stranded tail inside `## Deltas` and nowhere else. Unanchoring the predicate
    without that ruling makes one prose line that mentions `· prevention: rule → x` outside a code
    span block EVERY fold in that lens — a refusal the author cannot act on."""
    p = bundle / "specs" / "method.md"
    body = p.read_text()
    line = "A tail reads · prevention: rule → /tasks/t.md and · why-missed: nobody looked.\n"
    if where == "above":
        body = body.replace("## Deltas", line + "\n## Deltas", 1)
    elif where == "inside-a-fence":
        body = body.replace("## Deltas", "```\n" + line + "```\n\n## Deltas", 1)
    else:
        body = body.rstrip("\n") + "\n\n## Notes\n" + line
    p.write_text(body)
    assert add.learn(bundle, "method", "an ordinary lesson", evidence="/tasks/t.md")[0]
    ok, note = add.fold(bundle, "method", "an ordinary lesson")
    assert ok, f"prose {where} the deltas blocked a fold: {note!r}"


# --- one reported id per rule -------------------------------------------------------------------
# A parametrized check binds NOTHING at the gate: pytest reports `name[param]` and the node's
# CHECKS row names `name`, so seven rules whose only checks were tables read as unbound. These
# sweep the SAME tables in-body, so each rule has one reported id AND keeps its axis.


def test_every_resolvable_form_of_a_prevention_ref(bundle):
    """covers: M2, A2, E4 — the whole address vocabulary in one reported id."""
    p = bundle / "tasks" / "t.md"
    p.write_text(p.read_text().replace("- M1 <the rule that must hold>",
                                       "- M1 the lister returns only the caller's rows"))
    assert add.learn(bundle, "method", "seed lesson", evidence="/tasks/t.md")[0]
    mine = re.search(r"\[ADD · (M\d+) · open", _line(bundle, "seed lesson")).group(1)
    for ref, folds in (("/tasks/t.md", True), ("/tasks/t.md#M1", True), (f"/specs/method.md#{mine}", True),
                       ("src/a.py", True), ("tests/test_x.py::test_y", True),
                       ("https://dash.example/alerts/1", False), ("/tasks/t.md#M9", False)):
        assert add.learn(bundle, "method", f"the escape for {ref}", evidence="/tasks/t.md", escape=True,
                         why_missed="w", prevention=f"monitor → {ref}")[0]
        ok, note = add.fold(bundle, "method", f"the escape for {ref}")
        assert (ok is True) is folds, f"{ref}: {note!r}"


def test_every_uncaused_shape_is_named(bundle):
    """covers: M1, E2 — each missing or malformed part of an escape named, in one reported id."""
    for kw, names in ((dict(escape=True, why_missed="w"), "--prevention"),
                      (dict(escape=True, prevention="check → tests/test_x.py"), "--why-missed"),
                      (dict(escape=True, why_missed="w", prevention="alert → tests/test_x.py"), "alert"),
                      (dict(escape=True, why_missed="w", prevention="check →"), "ref"),
                      (dict(why_missed="w"), "--escape"),
                      (dict(prevention="check → tests/test_x.py"), "--escape")):
        before = (bundle / "specs" / "method.md").read_text()
        ok, note = add.learn(bundle, "method", "an escape", evidence="/tasks/t.md", **kw)
        assert ok is None and "R:UNCAUSED" in note and names in note, f"{kw}: {note!r}"
        assert (bundle / "specs" / "method.md").read_text() == before, "a refused escape wrote something"


def test_every_empty_flag_value_is_still_a_flag(bundle):
    """covers: M1, E16 — presence, never truthiness, in one reported id."""
    for kw, names in ((dict(why_missed=""), "--escape"), (dict(prevention=""), "--escape"),
                      (dict(why_missed="", prevention=""), "--escape"),
                      (dict(escape=True, why_missed="", prevention="check → src/a.py"), "--why-missed"),
                      (dict(escape=True, why_missed="w", prevention=""), "--prevention")):
        before = (bundle / "specs" / "method.md").read_text()
        ok, note = add.learn(bundle, "method", "an unmarked escape", evidence="/tasks/t.md", **kw)
        assert ok is None and "R:UNCAUSED" in note and names in note, f"{kw}: {note!r}"
        assert (bundle / "specs" / "method.md").read_text() == before, "a refused call wrote a lesson"
    ok, note = add.learn(bundle, "method", "a lesson with blank evidence", evidence="   ")
    assert ok is None, f"blank evidence was accepted: {note!r}"


def test_nothing_but_a_file_resolves(bundle):
    """covers: M2, E8 — `.exists()` passing on a directory, on `.` and on an empty file part."""
    for ref in (".", "::test_y", "tests", "src/", "/tasks/t.md#M1"):
        assert add.learn(bundle, "method", f"dangling at {ref}", evidence="/tasks/t.md", escape=True,
                         why_missed="w", prevention=f"check → {ref}")[0]
        ok, note = add.fold(bundle, "method", f"dangling at {ref}")
        assert ok is None and "R:UNPREVENTED" in note, f"{ref}: {note!r}"


def test_the_gate_and_the_rung_read_one_rules_heading(bundle):
    """covers: M2, E30, E31 — every heading spelling the author may write, in one reported id."""
    seed = (bundle / "tasks" / "t.md").read_text()
    for heading in ("## RULES:", "## RULES (frozen)", "## RULES — the contract"):
        t = bundle / "tasks" / "t.md"
        t.write_text(seed.replace("## RULES", heading, 1)
                     .replace("- M1 <the rule that must hold>", "- M1 a rule that really must hold", 1))
        assert add.rules_of({"path": t, "body": t.read_text()}) == ["M1"], \
            f"the gate's reader lost the section: {heading!r}"
        ok, note = _cite(bundle, "M1", f"an escape citing a Must under {heading}")
        assert ok is True, f"the fold rung and the gate disagree about {heading!r}: {note!r}"


def test_a_remint_repoints_every_spelling_of_a_fragment(bundle, tmp_path):
    """covers: M2, E32, E34 — the four spellings E26 freezes as resolving, in one reported id."""
    assert add.learn(bundle, "method", "main's own first lesson", evidence="/tasks/t.md")[0]
    for n, hash_ in enumerate(("#", "# ", " #", "\u00a0#")):
        stream = _stream(tmp_path, f"s{n}")
        assert add.learn(stream, "method", f"a cross-tenant read escaped in stream {n}",
                         evidence="/tasks/t.md", escape=True, why_missed="none",
                         prevention=f"rule → /specs/method.md{hash_}M1")[0]
        assert add.fold(stream, "method", f"stream {n}")[0] is None, "the stream itself must refuse it"
        assert add.join(bundle, [stream])[0], "the join was refused"
        ok, note = add.fold(bundle, "method", f"stream {n}", bind="a decision")
        assert ok is None and "R:UNPREVENTED" in note, f"{hash_!r}: a re-mint re-pointed a prevention: {note!r}"
