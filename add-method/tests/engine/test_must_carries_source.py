"""Red suite for `must-carries-source` — a Must says where it was told, and what would read it wrong.

RULES already means "what you were told", and nothing recorded by whom. A Must may now end
`(from: <ref> · fails-on: <the plausible wrong reading>)`: the interview asks for the source of
every Must that has none, `confirm` writes `from: interview` onto the line, and `freeze` notices
the unsourced ids at a rung floor without ever refusing for them. The tail is Must TEXT, so the
direction digest moves with it and every existing reader is untouched.

Driven as `.add/tasks/must-carries-source.md` under milestone `loop-that-closes`.
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

from conftest import DRAFTED_ASSUMPTIONS, draft_direction  # noqa: E402

TREES = (REPO / "skill" / "add", REPO / "src" / "add_method" / "_bundled" / "skill" / "add",
         REPO.parent / ".claude" / "skills" / "add")

SOURCED = """<must>
- M1 the admit path is atomic (from: PRD §3 · fails-on: two callers both taking the last token)
- M2 a refused admission names the limit it hit
</must>
<reject>
- R:OVERADMIT two callers must never both take the last token -> "OVERADMIT"
</reject>"""

CHECKS = ("- test_atomic_admit · covers: M1 · concurrent callers never over-admit\n"
          "- test_named_limit · covers: M2 · the refusal names the limit\n"
          "- test_no_overadmit · covers: R:OVERADMIT · the last token goes to exactly one caller")


def _floor(bundle, cid):
    """A rung-bound task's `## PLAN` must carry a regression floor (R:NOFLOOR) before it freezes."""
    p = bundle / cid.lstrip("/")
    n = add.read(p, "T2")
    add.write(p, f"---\n{n['raw']}\n---\n" + n["body"].replace(
        "## PLAN", "## PLAN\nregression: none · fixture", 1))


@pytest.fixture
def task(tmp_path):
    b = tmp_path / ".add"
    add.init(b, "code", "P")
    cid, _ = add.new(b, "Task", "t", title="t", sensitivity="architecture")
    draft_direction(b, cid, rules=SOURCED, checks=CHECKS, assumptions=DRAFTED_ASSUMPTIONS)
    _floor(b, cid)
    return b, cid


def _musts(bundle, cid):
    body = add.read(bundle / cid.lstrip("/"), "T2")["body"]
    return {line.split()[1]: line.strip()
            for line in add._section(body, "rules").splitlines()
            if line.strip().startswith("- M")}


def test_sourced_musts_are_not_asked_and_bare_ones_are(task):
    """covers: M1, M2, A2, A5, E1 — the Must decision's shape and place, and a Reject never asked
    for a source: a Reject is derived from a Must or a floor, and the interview already puts it by
    id."""
    bundle, cid = task
    node = add.read(bundle / cid.lstrip("/"), "T2")
    ds = add._open_decisions(node)
    musts = [d for d in ds if d["of"] == "must"]
    assert [d["id"] for d in musts] == ["M2"], f"the sourced Must was asked, or the bare one was not: {ds}"
    assert musts[0]["dim"] == "source" and "names the limit" in musts[0]["reading"], musts[0]
    kinds = [d["of"] for d in ds]
    assert kinds.index("must") > max(kinds.index("assumption"), kinds.index("edge") if "edge" in kinds else -1,
                                     kinds.index("reject")), f"Musts must come last: {kinds}"
    assert not [d for d in ds if d["of"] == "reject" and d["dim"] == "source"], "a Reject was asked for a source"


def test_confirm_writes_from_interview(task):
    """covers: M2, A3, E2, E3 — `confirm` is the one verdict that writes; the tail it writes joins
    an existing `fails-on:` rather than replacing it."""
    bundle, cid = task
    for verdict, expect in (("defer", False), ("correct", False), ("confirm", True)):
        p = bundle / cid.lstrip("/")
        before = _musts(bundle, cid)["M2"]
        add.interview(bundle, cid, {"M2": verdict}, by="human:x")
        after = _musts(bundle, cid)["M2"]
        assert (("(from: interview)" in after) is expect), f"{verdict}: {after!r}"
        if not expect:
            assert after == before, f"{verdict} rewrote the line: {after!r}"
    # a tail carrying only fails-on: GAINS from:, it is never replaced
    p = bundle / cid.lstrip("/")
    n = add.read(p, "T2")
    add.write(p, f"---\n{n['raw']}\n---\n" + n["body"].replace(
        "- M1 the admit path is atomic (from: PRD §3 · fails-on: two callers both taking the last token)",
        "- M1 the admit path is atomic (fails-on: two callers both taking the last token)"))
    add.interview(bundle, cid, {"M1": "confirm"}, by="human:x")
    m1 = _musts(bundle, cid)["M1"]
    assert "(from: interview · fails-on: two callers both taking the last token)" in m1, m1


def test_human_floor_freeze_holds_the_unsourced_must(task):
    """covers: M4, E4 — an unsourced Must is an unanswered decision at a human floor, exactly as an
    un-interviewed assumption is, and answering it is what lets the freeze land."""
    bundle, _ = task
    # a SECURITY task: the computed floor is `human`, which is where the interview is a refusal
    cid, _ = add.new(bundle, "Task", "s", title="s", sensitivity="security")
    draft_direction(bundle, cid, rules=SOURCED, checks=CHECKS, assumptions=DRAFTED_ASSUMPTIONS)
    _floor(bundle, cid)
    ok, note = add.freeze(bundle, cid, "human:x", "human")
    assert ok is None and "R:UNINTERVIEWED" in note, f"the human freeze did not hold: {note!r}"
    node = add.read(bundle / cid.lstrip("/"), "T2")
    fm = add.scan(bundle)[cid]["fm"]
    assert "M2" in add.interview_gap(node, fm), "the unsourced Must is not owed an answer"
    assert "M1" not in add.interview_gap(node, fm), "the SOURCED Must was owed one"
    # answering everything EXCEPT the Must must still hold the freeze — M4's whole claim
    ids = [d["id"] for d in add._open_decisions(node)]
    add.interview(bundle, cid, {i: "confirm" for i in ids if i != "M2"}, by="human:x")
    ok, note = add.freeze(bundle, cid, "human:x", "human")
    assert ok is None and "M2" in note, f"the unsourced Must alone did not hold it: {note!r}"
    ids = [d["id"] for d in add._open_decisions(add.read(bundle / cid.lstrip("/"), "T2"))]
    add.interview(bundle, cid, {i: "confirm" for i in ids}, by="human:x")
    ok, note = add.freeze(bundle, cid, "human:x", "human")
    assert ok, f"the interviewed node did not freeze: {note!r}"


def test_freeze_notices_at_plan_never_refuses(task):
    """covers: M3, R:SOURCEASREFUSAL, A4, E5 — a notice names the ids; a fully sourced node says
    nothing; a process-floor node says nothing either."""
    bundle, cid = task
    ok, note = add.freeze(bundle, cid, "plan:m", "plan")
    assert ok, f"a plan freeze must never refuse for a source: {note!r}"
    assert "notice:" in note and "M2" in note and "no from:" in note, note
    p = bundle / cid.lstrip("/")
    n = add.read(p, "T2")
    add.write(p, f"---\n{n['raw']}\n---\n" + n["body"].replace(
        "- M2 a refused admission names the limit it hit",
        "- M2 a refused admission names the limit it hit (from: the on-call runbook)"))
    ok, note = add.freeze(bundle, cid, "plan:m", "plan")
    assert ok and "no from:" not in note, f"a fully sourced node still noticed: {note!r}"

    b2 = bundle.parent / "second" / ".add"
    add.init(b2, "code", "P")
    c2, _ = add.new(b2, "Task", "u", title="u")
    draft_direction(b2, c2, rules=SOURCED, checks=CHECKS, assumptions=DRAFTED_ASSUMPTIONS)
    _floor(b2, c2)
    ok, note = add.freeze(b2, c2, "me", "process")
    assert ok and "no from:" not in note, f"a process floor noticed: {note!r}"


def test_tail_is_sealed_and_never_judged(task):
    """covers: M1, R:DIGESTDRIFT, R:SOURCEJUDGED, E6 — the same Must with and without a tail seals
    differently, and the engine never resolves what `from:` names."""
    bundle, cid = task
    p = bundle / cid.lstrip("/")
    node = add.read(p, "T2")
    bare = add.direction_digest(node)
    add.write(p, f"---\n{node['raw']}\n---\n" + node["body"].replace(
        "- M2 a refused admission names the limit it hit",
        "- M2 a refused admission names the limit it hit (from: /tasks/nowhere.md#M9)"))
    sourced = add.direction_digest(add.read(p, "T2"))
    assert bare != sourced, "a sourced and an unsourced Must sealed alike"
    ok, note = add.freeze(bundle, cid, "plan:m", "plan")
    assert ok, f"the engine judged the source it cannot resolve: {note!r}"
    assert "/tasks/nowhere.md#M9" in _musts(bundle, cid)["M2"], "the source was rewritten"


def test_a_tail_is_recorded_as_handed(task):
    """covers: M1, A10, R:SOURCEJUDGED — reversed halves, an empty half, and odd text: recorded as
    written, never rewritten, and never a refusal."""
    bundle, cid = task
    p = bundle / cid.lstrip("/")
    for tail in ("(fails-on: … · from: a hallway conversation)", "(from:)", "(from: a · b · c)"):
        n = add.read(p, "T2")
        add.write(p, f"---\n{n['raw']}\n---\n" + add._section_swap(n["body"], "M2", tail)
                  if hasattr(add, "_section_swap") else
                  f"---\n{n['raw']}\n---\n" + "\n".join(
                      (line.split(" (")[0] + " " + tail) if line.strip().startswith("- M2 ") else line
                      for line in n["body"].splitlines()))
        ok, note = add.freeze(bundle, cid, "plan:m", "plan")
        assert ok, f"{tail}: a freeze refused on a tail it must only record: {note!r}"
        assert tail in _musts(bundle, cid)["M2"], f"{tail}: the tail was rewritten"


def test_direction_md_states_it():
    """covers: M5 — direction.md names the tail and what `fails-on:` is for; three trees identical."""
    d = (REPO / "skill" / "add" / "phases" / "direction.md").read_text(encoding="utf-8")
    assert "from:" in d and "fails-on:" in d, "direction.md does not name the Must tail"
    for tree in TREES[1:]:
        assert (tree / "phases" / "direction.md").read_bytes() == (REPO / "skill" / "add" / "phases" / "direction.md").read_bytes(), tree
    # TRIPWIRE against HEAD, so `git commit` satisfies it — it fires while the edit is uncommitted,
    # which is exactly when the line-neutral rule is decided.
    head = subprocess.run(["git", "show", "HEAD:add-method/skill/add/phases/direction.md"],
                          cwd=REPO.parent, capture_output=True, text=True, check=True).stdout
    assert len(d.splitlines()) == len(head.splitlines()), "direction.md is not line-neutral vs HEAD"


def test_an_answer_survives_the_edit_the_interview_made(task):
    """covers: M2, M4, A3, E2 — confirming a source REWRITES the Must line, which moves the
    interview digest; reading only the new one would erase every answer from an earlier sitting,
    so a human who answers the source question last would be asked everything again. The stamp
    seals the text the interview produced and carries forward what this conversation settled."""
    bundle, _ = task
    cid, _ = add.new(bundle, "Task", "s", title="s", sensitivity="security")
    draft_direction(bundle, cid, rules=SOURCED, checks=CHECKS, assumptions=DRAFTED_ASSUMPTIONS)
    _floor(bundle, cid)
    node = add.read(bundle / cid.lstrip("/"), "T2")
    ids = [d["id"] for d in add._open_decisions(node)]
    add.interview(bundle, cid, {i: "confirm" for i in ids if i != "M2"}, by="human:x")   # sitting 1
    add.interview(bundle, cid, {"M2": "confirm"}, by="human:x")                          # sitting 2
    ok, note = add.freeze(bundle, cid, "human:x", "human")
    assert ok, f"the source question re-opened every earlier answer: {note!r}"


HOSTILE = [r"a \d+ id is parsed as a count", r"a \n in the ref", r"\1 wins the group",
           r"\g<0> repeats it", r"C:\newdir instead of the UNC path", r"100\% of the rows"]


@pytest.mark.parametrize("fails", HOSTILE)
def test_the_writer_records_the_tail_it_was_handed(task, fails):
    """covers: M1, M2, R:SOURCEJUDGED, E2, E3, E7 — found by the T2 refute: the merge spliced the
    human's `fails-on:` text into a `re.sub` REPLACEMENT TEMPLATE, where a backslash is grammar,
    so the engine RESOLVED what it must record — `\\d` raised `re.PatternError` straight out of the
    verb (leaving a sidecar with no stamp), `\\n` split the frozen Must in two, `\\1` deleted text and
    `\\g<0>` duplicated the tail. R:SOURCEJUDGED was bound only on the READ path; this drives the
    one verb that writes, and this bundle already authors a Must containing `\\d+`."""
    bundle, cid = task
    p = bundle / cid.lstrip("/")
    n = add.read(p, "T2")
    add.write(p, f"---\n{n['raw']}\n---\n" + n["body"].replace(
        "- M2 a refused admission names the limit it hit",
        f"- M2 a refused admission names the limit it hit (fails-on: {fails})", 1))
    before = len(add.read(p, "T2")["body"].splitlines())
    ok, note = add.interview(bundle, cid, {"M2": "confirm"}, by="human:x")
    assert ok is not None, f"{fails!r}: the interview refused or raised: {note!r}"
    line = _musts(bundle, cid)["M2"]
    assert line.endswith(f"(from: interview · fails-on: {fails})"), f"{fails!r}: {line!r}"
    assert len(add.read(p, "T2")["body"].splitlines()) == before, f"{fails!r}: the Must line was split"
    assert not add._musts_without_source(add.read(p, "T2")), "the readers disagree after the write"


def test_the_authored_must_is_the_one_rewritten(task):
    """covers: M2, E8 — `_musts_without_source` reads `_authored_rules` (fence-blind) and the write
    read the RAW body, so a fenced EXAMPLE of the same Must took the tail and the authored line
    stayed bare: the question was asked forever and the answer landed in prose."""
    bundle, cid = task
    p = bundle / cid.lstrip("/")
    n = add.read(p, "T2")
    quoted = "```\n- M2 a refused admission names the limit it hit\n```\n"
    add.write(p, f"---\n{n['raw']}\n---\n" + n["body"].replace("## RULES", quoted + "## RULES", 1))
    add.interview(bundle, cid, {"M2": "confirm"}, by="human:x")
    body = add.read(p, "T2")["body"]
    assert "(from: interview)" in _musts(bundle, cid)["M2"], "the authored Must was not rewritten"
    fenced = body.split("```")[1]
    assert "(from: interview)" not in fenced, f"the fenced COPY was rewritten: {fenced!r}"


# Swept IN THE BODY, not by `parametrize`. pytest reports a parametrized case as `name[param]`
# while the node's `## CHECKS` names `name`, so the gate binds NOTHING to a parametrized check and
# refuses PASS with "these rules have no reported passing check" — which is exactly how E9 and E12
# came to be the only two unbound rules after six T2 reads had hardened everything around them.
SECTION_PLACEMENTS = [("## CARD", False), ("## CARD", True),
                      ("## EVIDENCE", False), ("## RULES", True)]


def test_only_the_authored_must_is_ever_rewritten(task):
    """covers: M2, E8, E9 — the SECTION axis, which E8's first check pinned at "fenced". The reader
    (`_musts_without_source`) reads `_authored_rules`: fence-blind AND scoped to the authored
    sections. The writer read `live_lines`, which blanks fences only — so an unfenced copy in
    `## CARD`, the section that precedes `## RULES` in every live node, took the tail while the
    authored Must stayed bare: asked forever, the answer landing in prose."""
    bundle, cid = task
    p = bundle / cid.lstrip("/")
    pristine = add.read(p, "T2")["body"]
    for where, fenced in SECTION_PLACEMENTS:
        n = add.read(p, "T2")
        copy = "- M2 a refused admission names the limit it hit"
        block = f"```\n{copy}\n```\n" if fenced else f"{copy}\n"
        add.write(p, f"---\n{n['raw']}\n---\n" + pristine.replace(where, f"{where}\n{block}", 1))
        add.interview(bundle, cid, {"M2": "confirm"}, by="human:x")
        assert "(from: interview)" in _musts(bundle, cid)["M2"], \
            f"{where}{' (fenced)' if fenced else ''}: the authored Must was not the one rewritten"
        assert not add._musts_without_source(add.read(p, "T2")), "the readers disagree after the write"
        body = add.read(p, "T2")["body"]
        if fenced:
            assert "(from: interview)" not in body.split("```")[1], "the fenced COPY took the tail"
        if where != "## RULES":
            section = add._section(body, where[3:].lower())
            assert "(from: interview)" not in section, f"the copy in {where} took the tail:\n{section}"


@pytest.mark.parametrize("sep", [" ", " ", "\x85", "\x0b", "\x0c"])
def test_the_write_leaves_every_other_line_as_it_found_it(task, sep):
    """covers: M2, E10 — the interview was the ONE body writer of fourteen that re-joined with
    `"\\n".join(splitlines())` instead of slicing `keepends=True`. Every line boundary Python knows
    but `\\n` does not preserve was silently converted by a verb that touched one line — E45/E46's
    own class, reintroduced at a new write site, in a bundle whose specs carry such characters."""
    bundle, cid = task
    p = bundle / cid.lstrip("/")
    n = add.read(p, "T2")
    marked = n["body"].replace("## PLAN", f"a line{sep}with a boundary\n\n## PLAN", 1)
    add.write(p, f"---\n{n['raw']}\n---\n{marked}")
    add.interview(bundle, cid, {"M2": "confirm"}, by="human:x")
    after = add.read(p, "T2")["body"]
    assert f"a line{sep}with a boundary" in after, f"{sep!r} was rewritten by a write that never touched it"
    assert after.endswith("\n") == marked.endswith("\n"), "the node's final newline moved"


def test_a_placeholder_inside_a_real_must_is_still_a_must(task):
    """covers: M1, M2, E11 — `PLACEHOLDER` marks a SCAFFOLD line, not any line containing angle
    brackets: skipping every Must that merely mentions `<the caller>` made a real rule invisible to
    the question, to the notice, and to `confirm`, which refused it as no such decision. M2 and M3
    quantify over EVERY Must with no `from:`."""
    bundle, cid = task
    p = bundle / cid.lstrip("/")
    n = add.read(p, "T2")
    add.write(p, f"---\n{n['raw']}\n---\n" + n["body"].replace(
        "- M2 a refused admission names the limit it hit",
        "- M2 a refused admission names the limit <the caller> hit", 1))
    assert [m for m, _ in add._musts_without_source(add.read(p, "T2"))] == ["M2"], "a real Must went invisible"
    ok, note = add.interview(bundle, cid, {"M2": "confirm"}, by="human:x")
    assert ok is not None, f"confirm refused a real Must: {note!r}"
    assert "(from: interview)" in _musts(bundle, cid)["M2"]
    # the SCAFFOLD line is still exempt — that is what the placeholder rule is for
    b2 = bundle.parent / "third" / ".add"
    add.init(b2, "code", "P")
    c2, _ = add.new(b2, "Task", "u", title="u")
    assert not add._musts_without_source(add.read(b2 / c2.lstrip("/"), "T2")), \
        "a scaffold Must was asked for a source it cannot have"


def test_a_refused_interview_leaves_no_orphan_sidecar(task):
    """covers: M2, E7 — the first refute's actual damage: the verb raised AFTER writing
    `.d/interviews/<n>.md`, leaving a record with no stamp — the `orphan_receipt` shape a notary
    must never manufacture. Bound as a COUNT, so any future raise between the two writes is caught
    whatever raised it."""
    bundle, cid = task
    p = bundle / cid.lstrip("/")
    n = add.read(p, "T2")
    add.write(p, f"---\n{n['raw']}\n---\n" + n["body"].replace(
        "- M2 a refused admission names the limit it hit",
        r"- M2 a refused admission names the limit it hit (fails-on: a \d+ id parsed as a count)", 1))
    add.interview(bundle, cid, {"M2": "confirm"}, by="human:x")
    side = sorted((p.parent / f"{cid.rsplit('/', 1)[-1][:-3]}.d" / "interviews").glob("*.md"))
    stamps = [s for s in add.scan(bundle)[cid]["fm"]["verified"] if s.get("act") == "interview"]
    assert len(side) == len(stamps), f"{len(side)} sidecar(s), {len(stamps)} stamp(s) — an orphan record"


DUPLICATE_PLACEMENTS = ["<must>", "## EDGES"]          # in-body, for the reason above


def test_one_line_takes_one_tail(task):
    """covers: M1, M2, R:SOURCEJUDGED, E12 — found by the third T2 refute: `live` was snapshotted
    once and the per-decision loop restarted at the first index, so two Musts sharing an id and a
    text both bound to the SAME line — the first took `(from: interview) (from: interview)`, the
    second stayed bare, the gap closed on the id, and the freeze sealed a tail nobody handed it
    while the notice printed forever with its own `next:` verb unactionable. Two checks swept
    WHERE a copy lives and both pinned MULTIPLICITY at one."""
    bundle, cid = task
    p = bundle / cid.lstrip("/")
    pristine = add.read(p, "T2")["body"]
    for where in DUPLICATE_PLACEMENTS:
        n = add.read(p, "T2")
        dup = "- M2 a refused admission names the limit it hit"
        body = pristine.replace(dup, f"{dup}\n{dup}", 1) if where == "<must>" \
            else pristine.replace("## EDGES", f"## EDGES\n{dup}", 1)
        add.write(p, f"---\n{n['raw']}\n---\n{body}")
        add.interview(bundle, cid, {"M2": "confirm"}, by="human:x")
        after = add.read(p, "T2")["body"]
        assert "(from: interview) (from: interview)" not in after, f"{where}: one line took two tails"
        assert not add._musts_without_source(add.read(p, "T2")), \
            f"{where}: a Must the engine asked about is still unsourced:\n{add._section(after, 'rules')}"
        if where == "## EDGES":
            assert "(from: interview)" not in add._section(after, "edges"), \
                "a line in ## EDGES was read as a Must — `rules_of` reads only ## RULES"


def test_the_rewritten_line_keeps_its_own_terminator(task):
    """covers: M2, E10 — the clause the third read found bound by nothing: the rewrite re-attaches
    the line's OWN terminator, so a Must ended by U+2028 keeps it and a Must that is the file's
    last line gains no newline. A write that silently normalises how a line ends is a write nobody
    asked for — and the check that was meant to bind this passed on a Must the reader never saw."""
    bundle, cid = task
    p = bundle / cid.lstrip("/")
    n = add.read(p, "T2")
    # (a) the rewritten line's own boundary character survives
    add.write(p, f"---\n{n['raw']}\n---\n" + n["body"].replace(
        "- M2 a refused admission names the limit it hit\n",
        "- M2 a refused admission names the limit it hit\u2028", 1))
    add.interview(bundle, cid, {"M2": "confirm"}, by="human:x")
    after = add.read(p, "T2")["body"]
    assert "(from: interview)\u2028" in after, f"the line's own terminator was normalised: {after[:400]!r}"

    # (b) a Must that IS the last line, with no trailing newline, gains none
    head = n["body"][:n["body"].index("## RULES")]
    add.write(p, f"---\n{n['raw']}\n---\n" + head +
              "## RULES\n<must>\n- M9 the last rule of all\n</must>\n- M8 truly last")
    assert not add.read(p, "T2")["body"].endswith("\n")
    add.interview(bundle, cid, {"M9": "confirm"}, by="human:x")
    body = add.read(p, "T2")["body"]
    assert "- M9 the last rule of all (from: interview)" in body, body
    assert not body.endswith("\n"), "the interview appended a newline the author never wrote"


# The fifth T2 read's finding, bound. Every axis this task swept — VERDICT, TEXT, FENCE, SECTION,
# MULTIPLICITY — was swept on the READER and the WRITER. The SEAL was swept on none of them, and it
# was slicing the raw body: fence-blind, indent-blind, and matching the heading only when spelled
# exactly `## RULES`. So the question and the writer read one view, the seal read a fourth, and on
# a node whose heading is quoted or non-canonically spelled a sourced and an unsourced Must sealed
# ALIKE — R:DIGESTDRIFT verbatim, with the whole Must/Reject payload outside the seal behind it.
RULES_HEADINGS = (
    ("a fenced example above the real section",
     "```markdown\n## RULES\n<must>\n- M2 the quoted copy nobody authored\n</must>\n```\n\n## RULES"),
    ("a heading with a parenthetical", "## RULES (frozen)"),
    ("a heading with a colon", "## RULES:"),
    ("an indented heading", "  ## RULES"),
)


def _reheaded(bundle, cid, opening, pristine=None):
    """Rewrite the node so its `## RULES` section opens with `opening` — the same Musts, quoted or
    spelled the way an author actually writes them. A sweep passes `pristine` so each shape starts
    from the drafted body and never from the previous shape's rewrite."""
    p = bundle / cid.lstrip("/")
    n = add.read(p, "T2")
    body = (pristine if pristine is not None else n["body"]).replace("## RULES", opening, 1)
    add.write(p, f"---\n{n['raw']}\n---\n" + body)
    return p


def test_the_seal_reads_the_view_the_question_and_the_writer_read(task):
    """covers: M1, R:DIGESTDRIFT, E6 — the tail moves the direction digest on every heading shape a
    human writes, not only the one `add new` emits. A seal that slices the raw body reads a quoted
    example as the section, and a Must with a source then seals identically to one without."""
    bundle, cid = task
    pristine = add.read(bundle / cid.lstrip("/"), "T2")["body"]
    for why, opening in RULES_HEADINGS:
        p = _reheaded(bundle, cid, opening, pristine)
        bare = add.direction_digest(add.read(p, "T2"))
        n = add.read(p, "T2")
        add.write(p, f"---\n{n['raw']}\n---\n" + "\n".join(
            line + " (from: PRD §4)" if line.strip().startswith("- M2 a refused") else line
            for line in n["body"].splitlines()))
        assert add.direction_digest(add.read(p, "T2")) != bare, \
            f"{why}: a sourced and an unsourced Must sealed alike"


def test_the_seal_reads_the_authored_musts_and_not_a_quoted_copy(task):
    """covers: M1, E6 — what the seal took was the FENCE's content, so editing a quoted example
    moved the contract's digest while editing the real Must did not. Both halves, one node."""
    bundle, cid = task
    p = _reheaded(bundle, cid, RULES_HEADINGS[0][1])
    before = add.direction_digest(add.read(p, "T2"))
    n = add.read(p, "T2")
    add.write(p, f"---\n{n['raw']}\n---\n" + n["body"].replace(
        "- M2 the quoted copy nobody authored", "- M2 the quoted copy, reworded"))
    assert add.direction_digest(add.read(p, "T2")) == before, \
        "rewording a fenced example moved the frozen contract's seal"
    n = add.read(p, "T2")
    add.write(p, f"---\n{n['raw']}\n---\n" + n["body"].replace(
        "- M1 the admit path is atomic", "- M1 the admit path is atomic enough"))
    assert add.direction_digest(add.read(p, "T2")) != before, \
        "rewording the authored Must did not move the seal"


def test_a_gutted_must_is_drift_on_every_heading_shape(task):
    """covers: M1, R:DIGESTDRIFT, E6 — end to end: after a freeze, replacing a frozen Must with one
    that permits what the Reject forbids is refused as drift. This is constraint 3 itself, and on a
    non-canonical heading it was a check that passed on nothing."""
    bundle, cid = task
    pristine = add.read(bundle / cid.lstrip("/"), "T2")["body"]
    for why, opening in RULES_HEADINGS:
        p = _reheaded(bundle, cid, opening, pristine)
        n = add.read(p, "T2")
        add.write(p, f"---\n{add.set_key(n['raw'], 'status', 'build')}\n---\n" + n["body"])
        assert add.freeze(bundle, cid, "plan:m", "plan")[0], why
        n = add.read(p, "T2")
        add.write(p, f"---\n{n['raw']}\n---\n" + n["body"].replace(
            "- M2 a refused admission names the limit it hit",
            "- M9 the admit path may over-admit whenever it likes"))
        assert add.sealed_direction(add.read(p, "T2")["fm"]) != \
            add.direction_digest(add.read(p, "T2")), f"{why}: the Musts were gutted under the seal"


def test_the_referent_seal_reads_the_same_view(task):
    """covers: M1, E6 — `binding_digest` sealed the same raw slice, so a node whose `## EDGES` sits
    under a quoted heading bound an empty referent set: the gate's other half of constraint 3."""
    bundle, cid = task
    p = bundle / cid.lstrip("/")
    n = add.read(p, "T2")
    add.write(p, f"---\n{n['raw']}\n---\n" + n["body"]
              .replace("## EDGES", "## EDGES (probed)", 1)
              .replace("- E1 <a boundary or failure case a check must cover — optional>",
                       "- E1 Given the last token · When two callers admit · Then exactly one wins"))
    before = add.binding_digest(add.read(p, "T2"))
    assert before != add.binding_digest({"body": "", "fm": {}}), "the fixture bound no referents"
    n = add.read(p, "T2")
    add.write(p, f"---\n{n['raw']}\n---\n" + "\n".join(
        line for line in n["body"].splitlines() if not line.strip().startswith("- E1 "))) 
    assert add.binding_digest(add.read(p, "T2")) != before, "retiring an edge was invisible to the seal"


def test_a_must_is_one_line_shape_everywhere(task):
    """covers: E12, M2 — the ONE view narrowed the SECTION axis and left the LINE-SHAPE axis open:
    `_musts_without_source` matched `\\s*-\\s*M\\d+` while `rules_of` matches `RULE_ID`, so an
    indented continuation and a dash with no space were asked, noticed and REWRITTEN as Musts by a
    floor that also says they are not rules."""
    bundle, cid = task
    p = bundle / cid.lstrip("/")
    n = add.read(p, "T2")
    add.write(p, f"---\n{n['raw']}\n---\n" + n["body"].replace(
        "- M2 a refused admission names the limit it hit",
        "- M2 a refused admission names the limit it hit\n"
        "  - M6 an indented line the author wrapped under M2\n"
        "-M7 a line with no space after the dash", 1))
    node = add.read(p, "T2")
    asked = {m for m, _ in add._musts_without_source(node)}
    assert asked == {"M2"}, f"a non-rule was put to the human as a Must: {sorted(asked)}"
    assert set(add.rules_of({"path": p})) >= {"M1", "M2"}, add.rules_of({"path": p})
    assert not (asked - set(add.rules_of({"path": p}))), "the question and the gate disagree on what a Must is"


def test_every_sealed_section_reads_the_authored_view(task):
    """covers: M1, E6 — `direction:` seals RULES + CHECKS + `gives:` and `binding:` seals EDGES +
    probed `A<n>`. Each slice was its own raw read, so the sweep asks every one of them the same
    question: does a non-canonical heading take the section outside the seal?"""
    bundle, cid = task
    p = bundle / cid.lstrip("/")
    pristine = add.read(p, "T2")["body"]
    for heading, edit, seal in (
            ("## CHECKS", ("- test_named_limit · covers: M2 · the refusal names the limit",
                           "- test_named_limit · covers: M2 · the refusal names WHICH limit"),
             add.direction_digest),
            ("## ASSUMPTIONS", ("- A1 [", "- A9 ["), add.binding_digest)):
        n = add.read(p, "T2")
        # A probed `A<n>` is what `binding:` seals — the drafted sweep carries no `· probe:`, so
        # the fixture pins one on before the heading is spelled the way an author spells it.
        add.write(p, f"---\n{n['raw']}\n---\n" + pristine
                  .replace(heading, heading + " (drafted)", 1)
                  .replace("the admit limit is defeated",
                           "the admit limit is defeated · probe: test_atomic_admit"))
        before = seal(add.read(p, "T2"))
        assert before != seal({"body": "", "fm": {}}), f"{heading}: the fixture sealed nothing"
        n = add.read(p, "T2")
        add.write(p, f"---\n{n['raw']}\n---\n" + n["body"].replace(*edit, 1))
        assert seal(add.read(p, "T2")) != before, \
            f"{heading} under a non-canonical heading sealed nothing"


# The fifth T2 read's finding, and the check that would have caught reads three, four AND five.
# Each earlier fix closed ONE reader pair by hand: template→raw body, raw→fence view, fence→section
# view, section→multiplicity, and the seal. Every one was found by a probe that swept an axis some
# check pinned at the one well-formed shape `add new` writes. This check does not sweep shapes at
# all — it asserts the PROPERTY: for a given node, every reader of "which line is a Must" returns
# the same answer. A sixth reader can be added to the engine and this check still asks it.
MUST_SHAPES = (
    ("a colon after the id", "- M2:"),
    ("an em dash after the id", "- M2—"),
    ("a comma after the id", "- M2,"),
    ("the canonical shape", "- M2"),
)


def test_every_reader_of_a_must_line_agrees(task):
    """covers: E12, M1, M2 — the ONE view is a view of WHERE and a pattern for WHAT, and the
    question, the notice, the gate's `rules_of` and the WRITER must all give one answer.

    The writer kept its own third pattern (`\\s*-\\s*M\\d+\\s+`): looser on the left than `RULE_ID`,
    which FORMAT publishes, and stricter on the right. So `- M2:` was a Must to `rules_of` and to
    the question but invisible to the writer — `interview --answer M2=confirm` exited 0, wrote
    nothing, and the node then carried an `act: interview` stamp attesting `M2=confirm` beside a
    freeze note saying `M2 carry no from:`, forever."""
    bundle, cid = task
    p = bundle / cid.lstrip("/")
    pristine = add.read(p, "T2")["body"]
    for why, opening in MUST_SHAPES:
        n = add.read(p, "T2")
        add.write(p, f"---\n{n['raw']}\n---\n" + pristine.replace(
            "- M2 a refused admission names the limit it hit",
            f"{opening} a refused admission names the limit it hit", 1))
        node = add.read(p, "T2")
        gate_says = set(add.rules_of({"path": p}))
        question_says = {m for m, _ in add._musts_without_source(node)}
        # The ENGINE's own candidate set, asked by name — re-implementing the desired pattern here
        # would make this check pass on nothing, which is the defect it exists to catch.
        writer_says = set(add.must_lines(node["body"]).values())
        assert question_says <= gate_says, \
            f"{why}: the question asks about a line the gate says is not a rule: {question_says - gate_says}"
        assert question_says <= writer_says, \
            f"{why}: the question asks about a line the writer cannot find: {question_says - writer_says}"


def test_a_confirm_the_question_asked_always_writes(task):
    """covers: M1, M2, E8, E12 — end to end, the harm itself: whatever shape a Must is written in,
    if the interview ASKED about it then answering `confirm` must move the line and the seal. An
    answer that changes nothing leaves two engine-written records of one fact that disagree."""
    bundle, cid = task
    p = bundle / cid.lstrip("/")
    pristine = add.read(p, "T2")["body"]
    for why, opening in MUST_SHAPES:
        n = add.read(p, "T2")
        add.write(p, f"---\n{n['raw']}\n---\n" + pristine.replace(
            "- M2 a refused admission names the limit it hit",
            f"{opening} a refused admission names the limit it hit", 1))
        before = add.direction_digest(add.read(p, "T2"))
        asked = {m for m, _ in add._musts_without_source(add.read(p, "T2"))}
        if "M2" not in asked:
            continue                                   # not asked is a different claim (E12 above)
        add.interview(bundle, cid, {"M2": "confirm"}, by="human:x")
        node = add.read(p, "T2")
        assert "(from: interview)" in add._section(node["body"], "rules"), \
            f"{why}: the interview asked, the human answered, and nothing was written"
        assert add.direction_digest(node) != before, f"{why}: the answer did not move the seal"
        assert not [m for m, _ in add._musts_without_source(node) if m == "M2"], \
            f"{why}: the notice still reports the Must the human just sourced"


def test_a_must_naming_a_placeholder_is_asked_and_noticed(task):
    """covers: E11, M2, M3 — E11's other half. A real Must that names a `<placeholder>` in its own
    sentence is not a scaffold: it is asked, and if the human defers it, the freeze NOTICES it.

    The fifth T2 read found this half unreachable as E11 spells it, for a reason outside this
    task: `placeholders_in` refuses the freeze of any RULES line carrying an unbackticked `<…>`,
    which is the documented F8 guard — backticked spans are code, not template tokens. So the half
    is read the way the convention actually authors it, and `placeholders_in` is routed through the
    same authored view as everything else so it cannot disagree about where RULES is either."""
    bundle, cid = task
    p = bundle / cid.lstrip("/")
    n = add.read(p, "T2")
    add.write(p, f"---\n{n['raw']}\n---\n" + n["body"].replace(
        "- M2 a refused admission names the limit it hit",
        "- M2 a refused admission names the limit `<the caller>` hit", 1))
    node = add.read(p, "T2")
    assert not add.placeholders_in(node), f"a backticked span was read as a template token: {add.placeholders_in(node)}"
    assert "M2" in {m for m, _ in add._musts_without_source(node)}, "a real Must was skipped as scaffold"
    ok, note = add.freeze(bundle, cid, "plan:m", "plan")
    assert ok, f"the freeze refused a Must that names a placeholder in its own sentence: {note!r}"
    assert "M2" in note and "no from:" in note, f"the freeze did not notice the unsourced Must: {note!r}"
