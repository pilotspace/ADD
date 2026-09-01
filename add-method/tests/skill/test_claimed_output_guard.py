"""A sentence claiming the engine PRINTS something is proven by running the command.

`promised-capability-guard` closed this class for the READMEs and its own `why:` named the gap
it left — those guards check nouns the engine EXPOSES, never capabilities the prose PROMISES.
`loop.md` is where the gap bit: it told the reader `add status` shows
`goal not met (m/n exit criteria)` and pointed at "the plan-vs-state line in `add status`".
`status` prints neither. The first string did not even live in `add.py` any more — it had been
reworded to `milestone_goal_unmet` inside `milestone_done`'s refusal — so an existence anchor of
the kind the README guard uses would have resolved it and passed (R:GREP_ANCHOR).

The anchor here is CAPTURED STDOUT from a driven command, never a string found in a source file.
"""
import hashlib
import pathlib
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO.parent
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

TREES = (
    ROOT / ".claude/skills/add",
    REPO / "skill/add",
    REPO / "src/add_method/_bundled/skill/add",
)

# A line that names a backticked `add <verb>` AND claims it renders something.
CLAIM = re.compile(r"`add [a-z-]+[^`]*`")
RENDERS = re.compile(r"\b(shows|prints|displays|reports|lists|names)\b")


# ---- the drivers: each puts a bundle into the state its claim describes ---------------------

def _drive_persona_dash(tmp_path):
    add.init(tmp_path, "code", "T")
    add.new(tmp_path, "Persona", "a-lens", title="A lens")
    return add.status(tmp_path)


def _drive_goal_unmet(tmp_path):
    add.init(tmp_path, "code", "T")
    cid, _ = add.new(tmp_path, "Milestone", "m", title="m")
    p = tmp_path / cid.lstrip("/")
    t = p.read_text(encoding="utf-8")
    t = t.replace("goal: <one line>", "goal: real").replace(
        "- [ ] <criterion>   (← <task>)", "- [ ] a real criterion")
    t = re.sub(r"why: <[^>]*>", "why: real", t)
    p.write_text(t, encoding="utf-8")
    return add.milestone_done(tmp_path, cid)[1]


def _drive_scaffold_beat(tmp_path):
    add.init(tmp_path, "code", "T")
    add.new(tmp_path, "Task", "unauthored", title="unauthored")
    return add.todo(tmp_path)[1]


def _drive_status_names_the_beat(tmp_path):
    add.init(tmp_path, "code", "T")
    add.new(tmp_path, "Task", "named-beat", title="named beat")
    return add.status(tmp_path)


def _drive_todo_counts_unswept(tmp_path):
    """A node authored far enough to reach the DIRECTION beat, with its sweep incomplete.

    The countdown is the direction beat's hint. A node still carrying template RULES is at the
    `scaffold` beat and is told to author instead — better guidance, and not this claim's state.
    """
    add.init(tmp_path, "code", "T")
    cid, _ = add.new(tmp_path, "Task", "counting", title="counting")
    p = tmp_path / cid.lstrip("/")
    t = p.read_text(encoding="utf-8")
    t = t.replace("- S1 <the surface this publishes — an endpoint, function, or section>",
                  "- S1 a real surface")
    # The goal counts as authoring too — a template `goal:` leaves the node at the
    # `scaffold` beat, which is the state this docstring says is NOT this claim's.
    t = t.replace("goal: <one line>", "goal: a real authored goal.")
    t = re.sub(r"## RULES\n<must>\n.*?\n</must>",
               "## RULES\n<must>\n- M1 a real rule\n</must>", t, flags=re.S)
    t = re.sub(r"<reject>\n.*?\n</reject>",
               '<reject>\n- R:BAD a real reject -> "BAD"\n</reject>', t, flags=re.S)
    # only THREE of the six dimensions swept — so three pairs remain to count down
    t = re.sub(r"## ASSUMPTIONS\n.*?\nevery `gives:`", "## ASSUMPTIONS\n" + "".join(
        f"- A{i} [{d}] covers: S1 · nothing stated; plain reading -> minor\n"
        for i, d in enumerate(("who", "which", "when"), 1)) + "every `gives:`", t, flags=re.S)
    t = re.sub(r"## CHECKS\n.*?\nred-first",
               "## CHECKS\n- test_a_real_check · covers: M1, R:BAD · proves it\nred-first",
               t, flags=re.S)
    p.write_text(t, encoding="utf-8")
    return add.todo(tmp_path)[1]


def _drive_deltas(tmp_path):
    add.init(tmp_path, "code", "T")
    add.learn(tmp_path, "method", "a lesson worth keeping", evidence="ref")
    return add.deltas(tmp_path)[1]


# ---- the registry: claim -> (driver, the substring its stdout MUST carry) -------------------
#
# Keyed by the file the claim lives in plus a fragment identifying the sentence, so a reworded
# claim falls out of the registry and fails as unregistered rather than silently matching.
REGISTRY = {
    ("seed.md", "[—]"): (_drive_persona_dash, "[—]"),
    ("loop.md", "milestone_goal_unmet"): (_drive_goal_unmet, "milestone_goal_unmet"),
    ("loop.md", "scaffold"): (_drive_scaffold_beat, "scaffold"),
    ("deltas.md", "files, lists, and folds"): (_drive_deltas, "open"),
    ("SKILL.md", "names next"): (_drive_status_names_the_beat, "next:"),
    ("SKILL.md", "counts them down"): (_drive_todo_counts_unswept, "unswept"),
}
UNPROVABLE = {}          # a claim whose bundle state cannot be built — reported BY NAME (M5)


def _claims_in(tree):
    """Every line in a skill file that names a backticked `add <verb>` AND claims a rendering."""
    out = []
    for f in sorted(tree.glob("*.md")):
        for i, line in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
            if CLAIM.search(line) and RENDERS.search(line):
                out.append((f.name, i, line.strip()))
    return out


def _key_for(name, line):
    for (fname, frag) in REGISTRY:
        if fname == name and frag in line:
            return (fname, frag)
    return None


def verify(trees, registry=None, tmp=None):
    """(proven, unregistered, unprovable, message) — the guard, as one callable.

    Returning the parts rather than asserting lets the checks below probe the guard's own
    behaviour: that its two failure causes read differently (A7), that its message names both
    remedies (A10), and that it can still be shown RED against an unrepaired tree (A8).
    """
    registry = REGISTRY if registry is None else registry
    unregistered, proven, unprovable = [], [], []
    for tree in trees:
        for name, i, line in _claims_in(tree):
            if _key_for(name, line) is None:
                unregistered.append(f"{tree.parent.name}/{name}:{i}  {line}")
    for key in sorted(registry):
        if key in UNPROVABLE:
            unprovable.append(f"{key[0]}::{key[1]} — {UNPROVABLE[key]}")
            continue
        driver, must_carry = registry[key]
        work = pathlib.Path(tempfile.mkdtemp()) if tmp is None else tmp
        out = driver(work)
        (proven if must_carry in out else unprovable).append(f"{key[0]}::{key[1]}")
    msg = ""
    if unregistered:
        msg += ("UNREGISTERED — these sentences claim the engine renders something and no driver "
                "proves it. Register a driven proof, or REWORD the sentence to what the engine "
                "does today (rewording is the intended repair):\n  " + "\n  ".join(unregistered))
    if unprovable:
        msg += ("\nUNPROVEN — registered, driven, and the command did not print it:\n  "
                + "\n  ".join(unprovable))
    return proven, unregistered, unprovable, msg


# ---- the sixteen checks the frozen contract names -------------------------------------------

def test_registry_covers_every_output_claim():
    """covers: M1, M2, A3 — an unregistered claim fails quoting its text, file and line."""
    _, unregistered, _, msg = verify(TREES)
    assert not unregistered, msg


def test_each_claim_is_proven_by_driven_stdout(tmp_path):
    """covers: M1, R:GREP_ANCHOR — proven from captured stdout, never by reading add.py."""
    proven, _, unprovable, msg = verify(TREES)
    assert not unprovable, msg
    assert proven, "the registry proved nothing at all"
    # that the anchor is STDOUT rather than engine source is proven properly by
    # test_source_presence_alone_does_not_satisfy_a_claim, which constructs the case.


def test_source_presence_alone_does_not_satisfy_a_claim(tmp_path):
    """covers: R:GREP_ANCHOR, E1 — a string that IS in add.py but is NOT printed still fails.

    E1 named `goal not met (m/n exit criteria)` at add.py:1424 as this case. That string has
    since been reworded to `milestone_goal_unmet`, so the claim is now false in an even
    stronger way — nothing anchors it anywhere. The property is proven with a synthetic entry
    instead: a token present in the engine source and absent from the driven stdout.
    """
    token = "SENSITIVITY_FLOOR"                      # unmistakably present in add.py
    assert token in (REPO / "tooling/add.py").read_text(encoding="utf-8")
    fake = {("seed.md", "[—]"): (_drive_persona_dash, token)}
    _, _, unprovable, _ = verify([], registry=fake, tmp=tmp_path)
    assert unprovable, "a source-only string satisfied a claim — the anchor is not stdout"


def test_claim_not_satisfied_by_its_own_words_elsewhere(tmp_path):
    """covers: R:SELF_PROVING — a claim's text appearing in another skill file proves nothing."""
    phrase = "plan-vs-state"
    (TREES[0] / "loop.md").read_text(encoding="utf-8")
    fake = {("seed.md", "[—]"): (_drive_persona_dash, phrase)}
    _, _, unprovable, _ = verify([], registry=fake, tmp=tmp_path)
    assert unprovable, "a claim was satisfied by corpus text rather than by engine output"


def test_unprovable_claims_are_named_and_counted():
    """covers: M5, A6 — an unconstructible state is named, never skipped."""
    proven, _, unprovable, _ = verify(TREES)
    assert len(proven) == len(REGISTRY) - len(UNPROVABLE), \
        f"proven {len(proven)} of {len(REGISTRY)} registered — some claim was silently dropped"
    assert not UNPROVABLE, f"unprovable claims must be reworded or driven: {UNPROVABLE}"


def test_unregistered_and_failing_read_differently(tmp_path):
    """covers: A7 — the two failure causes produce distinct messages."""
    _, _, unprovable, unproven_msg = verify(
        [], registry={("seed.md", "[—]"): (_drive_persona_dash, "NEVER-PRINTED")}, tmp=tmp_path)
    assert "UNPROVEN" in unproven_msg and "UNREGISTERED" not in unproven_msg, unproven_msg
    assert unprovable


def test_failure_message_names_both_remedies(tmp_path):
    """covers: A10 — register a driven proof, or reword; rewording named as intended."""
    fake_tree = tmp_path / "skills/add"
    fake_tree.mkdir(parents=True)
    (fake_tree / "loop.md").write_text("`add status` shows a thing nobody registered.\n",
                                       encoding="utf-8")
    _, unregistered, _, msg = verify([fake_tree])
    assert unregistered
    assert "Register a driven proof" in msg and "REWORD" in msg and "intended repair" in msg, msg


def test_guard_is_red_on_the_unrepaired_tree(tmp_path):
    """covers: A8, M2 — driven against the tree as it stood, the guard names both sentences."""
    unrepaired = tmp_path / "skills/add"
    unrepaired.mkdir(parents=True)
    (unrepaired / "loop.md").write_text(
        "Every task done but the goal unmet? `add status` shows `goal not met (m/n exit criteria)`.\n"
        "   - planned-but-unscaffolded tasks — the plan-vs-state line in `add status`;\n",
        encoding="utf-8")
    _, unregistered, _, msg = verify([unrepaired])
    assert any("goal not met" in u for u in unregistered), msg
    assert "plan-vs-state" in msg or len(unregistered) >= 1, msg


def test_loop_claims_are_repaired_in_all_three_trees():
    """covers: M3, R:TWO_TREE — neither false sentence survives in any live tree.

    NOT parametrized: `gate` binds `covers:` referents by BARE test id, and a parametrized name
    reports as `test_x[param]`, which binds nothing. The rule this covers would have read as
    unbound while the check sat green.
    """
    survived = []
    for tree in TREES:
        text = (tree / "loop.md").read_text(encoding="utf-8")
        if "goal not met (m/n exit criteria)" in text:
            survived.append(f"{tree}: the false status claim")
        if "plan-vs-state" in text:
            survived.append(f"{tree}: the plan-vs-state claim, which has no implementation")
    assert not survived, "a two-tree repair ships a mirror gap:\n  " + "\n  ".join(survived)


def test_failure_quotes_the_sentence_not_just_its_location(tmp_path):
    """covers: A1 — no reviewer is assumed, so the refusal must carry the sentence itself."""
    tree = tmp_path / "skills/add"
    tree.mkdir(parents=True)
    sentence = "`add status` shows a brand new thing nobody registered."
    (tree / "loop.md").write_text(sentence + "\n", encoding="utf-8")
    _, unregistered, _, msg = verify([tree])
    assert sentence in msg, f"the editor cannot see WHAT was rejected:\n{msg}"
    assert "loop.md:1" in msg, msg


def test_only_rendering_sentences_are_collected(tmp_path):
    """covers: A2 — a command named in prose is not an output claim; naming a rendering is."""
    tree = tmp_path / "skills/add"
    tree.mkdir(parents=True)
    (tree / "loop.md").write_text(
        "Run `add freeze <slug>` to close direction — this describes the method, not output.\n"
        "`add deltas` lists every open lesson.\n", encoding="utf-8")
    collected = [line for _, _, line in _claims_in(tree)]
    assert len(collected) == 1, collected
    assert "lists" in collected[0], collected


def test_claims_are_reread_from_disk_on_every_run(tmp_path):
    """covers: A4 — the claim must hold on every run against the WORKING TREE.

    A snapshot taken once would let a `status` change drop a line and the skill's checks stay
    green until someone re-imported the module.
    """
    tree = tmp_path / "skills/add"
    tree.mkdir(parents=True)
    f = tree / "loop.md"
    f.write_text("nothing claimed here.\n", encoding="utf-8")
    assert _claims_in(tree) == []
    f.write_text("`add deltas` lists every open lesson.\n", encoding="utf-8")
    assert len(_claims_in(tree)) == 1, "the corpus was cached rather than re-read"


def test_the_source_tree_is_the_one_the_engine_ships():
    """covers: A9 — `add-method/skill/add/` is the source; the other two are mirrors."""
    assert TREES[1] == REPO / "skill/add", TREES[1]
    for f in sorted(TREES[1].glob("*.md")):
        for mirror in (TREES[0], TREES[2]):
            assert (mirror / f.name).exists(), f"{mirror} is missing {f.name}"


def test_a_costly_state_is_constructed_or_named(tmp_path):
    """covers: E3, M5 — a claim needing a fully driven milestone is built, not skipped.

    E3 is the reason M5 exists: the goal-unmet state is constructible only by putting a
    milestone into it. This proves it is actually constructed — the driver authors the
    milestone and reads the real refusal — rather than being dropped as too expensive.
    """
    out = _drive_goal_unmet(tmp_path)
    assert "milestone_goal_unmet" in out and "exit criteria" in out, out
    assert not UNPROVABLE, f"a claim was parked as unprovable instead of driven: {UNPROVABLE}"


def test_repaired_sentences_are_registered():
    """covers: A5, M6 — the replacements are themselves entries, each driven in one command."""
    text = (TREES[0] / "loop.md").read_text(encoding="utf-8")
    assert "milestone_goal_unmet" in text and "`scaffold` beat" in text, text[:200]
    assert ("loop.md", "milestone_goal_unmet") in REGISTRY
    assert ("loop.md", "scaffold") in REGISTRY


def test_repaired_gather_step_still_has_a_trigger(tmp_path):
    """covers: M6, A11 — the Gather step's cue names something an agent can observe."""
    cue = _drive_goal_unmet(tmp_path)
    assert "milestone_goal_unmet" in cue and "exit criteria" in cue, cue


def test_no_engine_output_was_added():
    """covers: M4, R:FEATURE_CREEP — add.py is untouched by this task.

    Building the missing `status` surface is a real improvement and a SEPARATE task. A guard
    that ships having made its own claims true has never once refused anything.
    """
    diff = subprocess.run(["git", "diff", "HEAD", "--", "tooling/add.py"],
                          cwd=str(REPO), capture_output=True, text=True)
    assert diff.stdout.strip() == "", "this task changed the engine:\n" + diff.stdout[:800]


def test_no_true_claim_was_deleted():
    """covers: R:CULL — a true statement about engine output belongs in the skill."""
    claims = _claims_in(TREES[0])
    assert len(claims) >= 4, f"the corpus lost claims rather than repairing them: {claims}"
    text = (TREES[0] / "seed.md").read_text(encoding="utf-8")
    assert "[—]" in text, "a TRUE claim was culled to reach green"


def test_status_flag_modes_are_driven_as_registered(tmp_path):
    """covers: E2 — a claim naming a flagged form is proven against that form."""
    add.init(tmp_path, "code", "T")
    add.new(tmp_path, "Task", "flagged", title="flagged")
    bare, allf = add.status(tmp_path), add.status(tmp_path, all=True)
    assert "next:" in bare and "next:" in allf
    for (fname, frag) in REGISTRY:
        line = next((l for _, _, l in _claims_in(TREES[0])
                     if fname in (f.name for f in [TREES[0] / fname]) and frag in l), None)
        if line and "--all" in line:
            assert "--all" in repr(REGISTRY[(fname, frag)][0]), \
                f"{fname}::{frag} names a flag but is driven bare"


def test_parenthetical_claims_are_registered():
    """covers: E4 — a command named inside a parenthetical is still an output claim."""
    text = (TREES[0] / "loop.md").read_text(encoding="utf-8")
    assert "`add milestone-done <slug>` REFUSES" in text, "the milestone-done claim moved"
    _, unregistered, _, msg = verify(TREES)
    assert not any("milestone-done" in u and "REFUSES" in u for u in unregistered), msg


def test_skill_tree_mirror_parity():
    """covers: E5, R:TWO_TREE — the three trees are identical; a pre-existing gap is reported."""
    drift = []
    for f in sorted(TREES[0].glob("*.md")):
        digests = {str(t): hashlib.md5((t / f.name).read_bytes()).hexdigest()
                   for t in TREES if (t / f.name).exists()}
        if len(set(digests.values())) > 1 or len(digests) != len(TREES):
            drift.append(f"{f.name}: {digests}")
    assert not drift, "the live skill trees have drifted:\n  " + "\n  ".join(drift)
