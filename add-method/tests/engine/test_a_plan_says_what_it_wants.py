"""Red suite for `a-plan-says-what-it-wants` — a scaffold says whether a plan still wants it.

3.6.0 made a 40-task roadmap legible: every row carries its title and the headline counts the
unauthored ones. It still could not answer the question a reviewer actually has — is this a queue
or a graveyard? A task the plan is working toward and a task the plan walked away from both read
`[scaffold]`.

`milestone-done` is where the graveyard comes from: it tallies exit criteria and never looks at
its member tasks, so a milestone closes and whatever it queued is abandoned with nothing said.

And `dropped` was already a word the engine READ in three places, that no verb could WRITE.
"""

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO.parent
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

CLI = [sys.executable, str(REPO / "tooling" / "cli.py")]


@pytest.fixture
def bundle(tmp_path):
    add.init(tmp_path, "code", "Plan")
    return tmp_path


def _milestone(root, slug, status=None):
    """A milestone, optionally forced to a closed status. Returns its cid."""
    cid, _ = add.new(root, "Milestone", slug, title=slug)
    if status:
        path = Path(root) / cid.lstrip("/")
        n = add.read(path, "T2")
        add.write(path, f"---\n{add.set_key(n['raw'], 'status', status)}\n---\n{n['body']}")
    return cid


def _task(root, slug, milestone=None):
    fields = {"milestone": milestone} if milestone else {}
    cid, _ = add.new(root, "Task", slug, title=slug, **fields)
    return cid


def test_a_scaffold_says_which_plan_wants_it(bundle):
    """covers: M1, M2, R:NEWFIELD, A2, A4, E1, E5 — the three words, derived, never stored."""
    _milestone(bundle, "m-open")
    _milestone(bundle, "m-done", status="done")
    _milestone(bundle, "m-archived", status="archived")      # E1/A2: archived closes a plan too

    cases = {
        "t-queued":    ("m-open",     "queued"),
        "t-abandoned": ("m-done",     "abandoned"),
        "t-archived":  ("m-archived", "abandoned"),
        "t-typo":      ("m-nosuch",   "adrift"),               # E5/A4: a dangling reference
        "t-orphan":    (None,         "adrift"),
    }
    for slug, (milestone, _) in cases.items():
        _task(bundle, slug, milestone)

    graph = add.scan(bundle)
    wrong = []
    for slug, (milestone, expected) in cases.items():
        got = add._beat_of(graph[f"/tasks/{slug}.md"], None, graph)
        if got != expected:
            wrong.append(f"  {slug} (milestone={milestone!r}): said {got!r}, wants {expected!r}")
    assert not wrong, "a scaffold reported the wrong provenance:\n" + "\n".join(wrong)

    # R:NEWFIELD — the answer is DERIVED. Nothing was written onto the task to carry it, so it
    # cannot drift out of step with the milestone it describes.
    for slug in cases:
        fm = add.read(bundle / "tasks" / f"{slug}.md", "T0")["fm"]
        stored = sorted(k for k in fm if str(k).lower() in
                        ("queued", "abandoned", "adrift", "provenance", "scaffold_kind"))
        assert not stored, f"{slug} stores the derived answer in frontmatter: {stored}"

    # A read verb must survive a dangling reference, not merely compute past it (E5).
    note = add.status(bundle)
    assert "t-typo" in note, f"`status` dropped the task with the dangling milestone:\n{note}"


def test_a_milestone_cannot_close_on_unauthored_tasks(bundle):
    """covers: M3, R:SILENTABANDON, A6, E3, E4 — abandonment becomes a decision."""
    empty = _authored_milestone(bundle, "m-empty")
    ok, note = add.milestone_done(bundle, empty)
    assert ok, f"E3 — a milestone with no tasks stopped closing:\n{note}"

    holding = _authored_milestone(bundle, "m-holding")
    _task(bundle, "t-left-behind", "m-holding")
    _task(bundle, "t-also-left", "m-holding")
    ok, note = add.milestone_done(bundle, holding)
    assert ok is None, "R:SILENTABANDON — the milestone closed and left two unauthored tasks behind"
    for slug in ("t-left-behind", "t-also-left"):
        assert slug in note, f"A6 — the refusal did not name `{slug}`:\n{note}"
    for fix in ("author", "drop", "milestone"):
        assert fix in note.lower(), (
            f"A6 — the refusal offered no `{fix}` exit; a message with one fix pushes the author "
            f"toward whichever fix it named:\n{note}")


def test_drop_writes_the_status_the_engine_reads(bundle):
    """covers: M4, R:DEADWORD, A3, A5, E2 — `dropped` becomes reachable, at the front door."""
    _task(bundle, "t-drop")
    out = subprocess.run(CLI + ["--root", str(bundle), "drop", "t-drop",
                                "--reason", "the API it wrapped was withdrawn"],
                         capture_output=True, text=True)
    assert out.returncode == 0, f"R:DEADWORD — `add drop` is not reachable at the CLI:\n{out.stderr}"

    text = (bundle / "tasks" / "t-drop.md").read_text()
    assert "status: dropped" in text, f"`drop` did not write the status the engine reads:\n{text[:400]}"
    assert "the API it wrapped was withdrawn" in text, "A9 — the reason was not recorded"

    # A5/E2: a dropped task is answered, not pending — it leaves the scaffold vocabulary.
    beat = add._beat_of(add.scan(bundle)["/tasks/t-drop.md"])
    assert beat == "dropped", f"a dropped task still reports {beat!r}"
    assert "t-drop" not in add.todo(bundle)[1], "a dropped task is still on the worklist"

    # A10: `done` is a recorded verdict, not a planning slot.
    _task(bundle, "t-done")
    path = bundle / "tasks" / "t-done.md"
    n = add.read(path, "T2")
    add.write(path, f"---\n{add.set_key(n['raw'], 'status', 'done')}\n---\n{n['body']}")
    ok, note = add.drop(bundle, "/tasks/t-done.md", "changed my mind")
    assert ok is None, "A10 — `drop` overwrote a recorded `done` verdict"
    assert "reopen" in note, f"the refusal did not name the verb that does revisit a done task:\n{note}"


def test_the_counts_and_the_rows_use_one_vocabulary(bundle):
    """covers: M5, M6, A1 — the headline splits by the words the rows show."""
    _milestone(bundle, "m-live")
    _milestone(bundle, "m-shut", status="done")
    _task(bundle, "t-q", "m-live")
    _task(bundle, "t-a", "m-shut")
    _task(bundle, "t-x")
    add.drop(bundle, _task(bundle, "t-gone"), "not needed")

    headline = add.status(bundle).splitlines()[0]
    for word, n in (("queued", 1), ("abandoned", 1), ("adrift", 1)):
        assert f"{n} {word}" in headline, (
            f"A1 — the headline does not count `{word}`, so the split lives only in a verb the "
            f"reviewer would have to know to run:\n{headline}")
    assert "dropped" not in headline, "M6 — a dropped task was counted in the pending split"


def _authored_milestone(root, slug):
    """A milestone that passes the why-gate and the goal-gate, so only the new rung can refuse."""
    cid = _milestone(root, slug)
    path = Path(root) / cid.lstrip("/")
    s = path.read_text()
    for hole, filled in (("goal: <one line>", "goal: a goal a human wrote"),
                         ("why: <why this milestone exists — required>", "why: a reason a human wrote"),
                         ("evidence: <one row per task>", "evidence: recorded at close"),
                         ("- [ ] <criterion>   (← <task>)", "- [x] the one thing   (a task)")):
        s = s.replace(hole, filled)
    path.write_text(s)
    return cid


# The registries that ENUMERATE the verb set. A 27th verb has to reach every one of them, and
# the only thing that makes that ripple finite is a list somebody can read (E6).
VERB_REGISTRIES = (
    "skill/add/SKILL.md",
    "src/add_method/_bundled/skill/add/SKILL.md",
    "README.md",
)


def test_every_registry_enumerating_verbs_learned_drop():
    """covers: E6 — the ripple a new verb causes, named in one place."""
    missing = [rel for rel in VERB_REGISTRIES
               if "drop" not in (REPO / rel).read_text(encoding="utf-8")]
    assert not missing, (
        "a registry that enumerates the verb set never learned `drop`:\n"
        + "\n".join(f"  {m}" for m in missing)
        + "\n\nA verb the engine dispatches and no registry names is a verb nobody finds.")

    host = ROOT / ".claude/skills/add/SKILL.md"
    if host.is_file():          # a fresh checkout may not carry the host-installed tree
        assert "drop" in host.read_text(encoding="utf-8"), \
            "the host-installed skill tree drifted from the shipped ones"
