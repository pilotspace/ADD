"""Red suite for `quick-lane-tripwire` — the direct lane's own size-up, read from the commit.

intake.md routes a small change to the direct lane on the author's judgement, and the floor is
checked FIRST and always wins: security · data · architecture, a `gives:` surface, or frozen scope
→ a node, however small. Nothing enforced that. A `quick:` lesson is the lane's one bundle write,
so it is where the engine can look: `learn` now resolves the lesson's `--evidence` as a commit,
reads that commit's changed paths READ-ONLY, and refuses R:QUICKSIZEUP when one touches a
`sensitive_paths:` pattern or an open frozen Task's `scope:`.

The lane is never blocked on git's absence (R:LANEBLOCKED) and the engine never moves the tree
(R:OUTWARD).

Driven as `.add/tasks/quick-lane-tripwire.md` under milestone `loop-that-closes`.
"""
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

from conftest import git  # noqa: E402

TREES = (REPO / "skill" / "add", REPO / "src" / "add_method" / "_bundled" / "skill" / "add",
         REPO.parent / ".claude" / "skills" / "add")


def _repo(tmp_path, sensitive=None, under=""):
    """A real git repo with an ADD bundle in it — the tripwire reads git, so the fixture is git.

    `under` puts the bundle BELOW the repo root (`add init --nested`, and this project's own
    `add-method/.add`). That topology is not decoration: `diff-tree` prints repo-root-relative
    paths whatever the cwd, while `sensitive_paths:` and `scope:` are written relative to the
    BUNDLE PARENT, so the two frames only coincide when the bundle sits at the root — which is
    where every check in this file used to build it.
    """
    tmp_path.mkdir(parents=True, exist_ok=True)
    git("init", "-q", cwd=tmp_path)
    git("config", "user.email", "t@example.com", cwd=tmp_path)
    git("config", "user.name", "T", cwd=tmp_path)
    parent = tmp_path / under if under else tmp_path
    parent.mkdir(parents=True, exist_ok=True)
    root = parent / ".add"
    add.init(root, "code", "P")
    if sensitive is not None:
        idx = root / "index.md"
        n = add.read(idx, "T2")
        add.write(idx, f"---\n{add.set_key(n['raw'], 'sensitive_paths', sensitive)}\n---\n" + n["body"])
    return root


def _repo_in(work, sensitive=None):
    """The bundle alone, in a git repo the caller already built — a clone, say, whose history the
    fixture cannot make with `git init`."""
    root = work / ".add"
    add.init(root, "code", "P")
    if sensitive is not None:
        idx = root / "index.md"
        n = add.read(idx, "T2")
        add.write(idx, f"---\n{add.set_key(n['raw'], 'sensitive_paths', sensitive)}\n---\n" + n["body"])
    return root


def _commit(tmp_path, rel, text="x = 1\n"):
    """Commit one file and return its sha — the evidence a quick lesson cites.

    `rel` is REPO-root-relative, as git reports it; a nested fixture passes the prefixed path.
    """
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)
    git("add", "-A", cwd=tmp_path)
    git("commit", "-q", "-m", f"touch {rel}", cwd=tmp_path)
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(tmp_path),
                          capture_output=True, text=True).stdout.strip()


def _head(cwd):
    """The sha the fixture just made — the evidence a quick lesson cites."""
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(cwd),
                          capture_output=True, text=True).stdout.strip()


def _branch_at(cwd, sha) -> str:
    """The branch name holding `sha` — whatever git called the first one here."""
    out = subprocess.run(["git", "branch", "--contains", sha, "--format=%(refname:short)"],
                         cwd=str(cwd), capture_output=True, text=True).stdout.split()
    return next(b for b in out if b != "side")


def _branch(cwd) -> str:
    """Whatever git called the first branch here — `main` or `master`, by the caller's config."""
    return subprocess.run(["git", "branch", "--show-current"], cwd=str(cwd),
                          capture_output=True, text=True).stdout.strip()


def _frozen_task(root, slug, scope, closed=None, freeze=True, by="plan:m", authority="plan"):
    """An OPEN FROZEN Task owning `scope` — M2's definition, built through the engine.

    `by`/`authority` because A17 floors a Task whose scope lies inside a declared
    `sensitive_paths:` pattern to `human`, and refuses a `plan:` freeze there — so a fixture that
    needs a frozen node on a sensitive path has to freeze it the way the method would.
    """
    cid, _ = add.new(root, "Task", slug, title=slug, scope=scope)
    p = root / cid.lstrip("/")
    if freeze:
        from conftest import DRAFTED_ASSUMPTIONS, DRAFTED_CHECKS, DRAFTED_RULES, draft_direction
        draft_direction(root, cid, rules=DRAFTED_RULES, checks=DRAFTED_CHECKS,
                        assumptions=DRAFTED_ASSUMPTIONS)
        n = add.read(p, "T2")
        add.write(p, f"---\n{n['raw']}\n---\n"
                  + n["body"].replace("## PLAN", "## PLAN\nregression: none · fixture", 1))
        if authority == "human":
            # A17 floors a Task scoped inside a declared `sensitive_paths:` pattern to `human`,
            # and a human freeze is an INTERVIEWED one — so the fixture answers the node's own
            # open decisions the way the method makes a person answer them.
            qs, _ = add.interview(root, cid)
            add.interview(root, cid, {q["id"]: "confirm" for q in qs}, by)
        ok, why = add.freeze(root, cid, by, authority)
        assert ok, f"the fixture could not freeze `{slug}`: {why}"
    if closed:
        n = add.read(p, "T2")
        add.write(p, f"---\n{add.set_key(n['raw'], 'status', closed)}\n---\n" + n["body"])
    return cid


def _no_bypass_advice(note: str):
    """M6, read over EVERY line — not the last one, and not one draft string.

    The check this replaces asserted `not note.endswith("ordinary lesson)")` while the engine
    actually ended `` `quick:` prefix, if so)``: pinned to a wording that was never emitted, so
    DELETING the whole clause shipped green and so did replacing it with "just drop the `quick:`
    prefix and it lands". A rule about what a message must not say is bound by reading the
    message, not by matching one sentence someone drafted.
    """
    for line in note.splitlines():
        low = line.lower()
        if "quick" in low and any(w in low for w in ("drop", "without", "omit", "remove", "no prefix")):
            raise AssertionError(f"a refusal recommends dropping the `quick:` prefix: {line!r}")


def _deltas(root, lens="method"):
    return add._section(add.read(root / "specs" / f"{lens}.md", "T2")["body"], "deltas")


def test_quick_commit_into_a_sensitive_path_is_refused(tmp_path):
    """covers: M1, R:QUICKSIZEUP, A5, E1 — the floor is checked FIRST and always wins. The refusal
    names the path, says `floor human`, and hands the exact `add new Task` line with that path as
    `--scope`; nothing is written, because a refusal that half-filed would leave the lane's one
    record saying the change was small."""
    root = _repo(tmp_path / "r", sensitive="[src/auth/**]")
    sha = _commit(tmp_path / "r", "src/auth/token.py")
    before = _deltas(root)
    out, note = add.learn(root, "method", "quick: rotate the signing keys — small", evidence=sha)
    assert out is None and "R:QUICKSIZEUP" in note, f"a sensitive path took the direct lane: {note!r}"
    assert "src/auth/token.py" in note and "floor human" in note, note
    assert "add new Task" in note and "--scope" in note, f"the refusal names no fix: {note!r}"
    assert _deltas(root) == before, "a refused quick lesson still wrote to the spec"

    # A5 is an ORDER, and an order binds only where the two answers differ. Every fixture above
    # matches exactly one of the two, so inverting `quick_hit`'s loops left the whole suite green.
    # A path matching BOTH is fiddly on purpose: the task's own scope ENTRY must miss the pattern
    # or A17 floors the task to `human` and it cannot be frozen by `plan:` at all.
    both = _repo(tmp_path / "b", sensitive="[**/*.key]")
    cid = _frozen_task(both, "secrets", ["src/secrets"])
    _commit(tmp_path / "b", "README.md", "# hi\n")
    sha = _commit(tmp_path / "b", "src/secrets/prod.key")
    out, note = add.learn(both, "method", "quick: rotate the prod key", evidence=sha)
    assert out is None, f"a path that is both sensitive and owned took the lane: {note!r}"
    # A5: the floor is named FIRST, and the halves DO overlap. `secrets` is frozen at `plan:`
    # authority because A17 cannot see that a directory entry holds a `.key` file — and a node no
    # human ever approved cannot stand this floor down, so the floor fires even though an open
    # frozen Task holds the path. The floor is the right answer precisely there.
    assert "floor human" in note and "**/*.key" in note, \
        f"a path that is both sensitive and owned was not named by the floor (A5): {note!r}"
    assert cid not in note, f"the owner was reported over the floor: {note!r}"
    assert add.authority_for(add.scan(both), cid) != "human", \
        "the fixture's owner node is human-floored — it no longer discriminates A5"
    assert add.quick_hit(both, add.scan(both), ["src/secrets/prod.key"], owners=False) is not None, \
        "the floor stood down for a node no human ever approved"

    # …and however the author capitalised the lane's own word. Asserted where it DISCRIMINATES:
    # in a bundle that declares sensitive paths the widened floor refuses every lesson anyway, so
    # a `Quick:` assertion there passes on nothing — dropping `re.I` shipped the whole suite green.
    # The mark only decides anything on the OWNER half, so that is where it is read.
    owned = _repo(tmp_path / "cap")
    cid = _frozen_task(owned, "billing", ["src/billing.py"])
    _commit(tmp_path / "cap", "README.md", "# hi\n")
    owned_sha = _commit(tmp_path / "cap", "src/billing.py")
    for mark in ("quick:", "Quick:", "QUICK:", "  quick :"):
        out, note = add.learn(owned, "method", f"{mark} tidy the rounding", evidence=owned_sha)
        assert out is None and cid in note, f"{mark!r} walked the owner half: {note!r}"
    assert add.learn(owned, "method", "quickly tidy the rounding", evidence=owned_sha)[0], \
        "a word merely STARTING with quick was read as the lane's mark"


def test_quick_commit_into_an_open_frozen_scope_is_refused(tmp_path):
    """covers: M1, M2, A2, E2 — OPEN means not done/dropped/archived AND carrying a freeze stamp:
    a done task's scope is history and an unfrozen task's scope is a draft nobody sealed, so
    neither owns anything. The refusal names the path and the owning task's cid."""
    root = _repo(tmp_path / "r")
    cid = _frozen_task(root, "billing", ["src/billing.py"])
    sha = _commit(tmp_path / "r", "src/billing.py")
    out, note = add.learn(root, "method", "quick: tidy the billing rounding", evidence=sha)
    assert out is None and "R:QUICKSIZEUP" in note, f"a frozen scope took the direct lane: {note!r}"
    assert "src/billing.py" in note and cid in note, note

    # M2 names THREE closed states and a check that binds one of them binds none of the others:
    # `CLOSED_TASK_STATES = ("done",)` passed the whole suite while `dropped` and `archived` then
    # falsely refused a clean commit. Swept in the body, because a parametrized check reports
    # `name[param]` and binds NOTHING at the gate.
    for state in ("done", "dropped", "archived"):
        closed = _repo(tmp_path / f"c-{state}")
        _frozen_task(closed, "billing", ["src/billing.py"], closed=state)
        sha = _commit(tmp_path / f"c-{state}", "src/billing.py")
        landed, note = add.learn(closed, "method", "quick: tidy it", evidence=sha)
        assert landed, f"a {state.upper()} task still owned its scope: {note!r}"

    # …and a scope entry that is a DIRECTORY owns what lies under it — "lies under" is M1's word,
    # and every fixture above named a FILE, so the containment direction was unbound too.
    dirs = _repo(tmp_path / "dir")
    cid = _frozen_task(dirs, "billing", ["src/billing"])
    sha = _commit(tmp_path / "dir", "src/billing/rounding.py")
    out, note = add.learn(dirs, "method", "quick: tidy the rounding", evidence=sha)
    assert out is None and cid in note, f"a DIRECTORY scope owned nothing under it: {note!r}"

    draft = _repo(tmp_path / "u")
    _frozen_task(draft, "billing", ["src/billing.py"], freeze=False)
    sha = _commit(tmp_path / "u", "src/billing.py")
    assert add.learn(draft, "method", "quick: tidy it", evidence=sha)[0], "an UNFROZEN scope owned something"


def test_clean_quick_commit_lands(tmp_path):
    """covers: M1, E3 — the tripwire is a floor check, not a default-deny: a commit touching
    nothing declared is the lane working as intended."""
    root = _repo(tmp_path / "r", sensitive="[src/auth/**]")
    _frozen_task(root, "billing", ["src/billing.py"])
    sha = _commit(tmp_path / "r", "README.md", "# hi\n")
    out, note = add.learn(root, "method", "quick: fix a typo in the readme", evidence=sha)
    assert out, f"a clean quick commit was refused: {note!r}"
    assert "quick: fix a typo" in _deltas(root)


def test_lane_is_never_blocked_on_git(tmp_path):
    """covers: M3, R:LANEBLOCKED, A4, E4 — the direct lane's ONE bundle write must never be lost
    to the engine's own inability to look. A receipt cid, an unresolvable sha and a tree that is
    not a repo all land exactly as they did before. What does NOT belong here any more is the
    non-quick lesson: the refreeze made the FLOOR read every lesson, so that case is E5's and is
    asserted — inverted — in `test_the_floor_does_not_read_the_prefix`. A lane blocked by the
    engine's inability to look is R:LANEBLOCKED; a lane stopped by the floor is the control."""
    root = _repo(tmp_path / "r", sensitive="[src/auth/**]")
    sha = _commit(tmp_path / "r", "src/auth/token.py")
    for why, lesson, ev in (
            ("a receipt cid", "quick: something", "/tasks/t.d/runs/1.md"),
            ("an unresolvable sha", "quick: something", "deadbeefdeadbeefdeadbeefdeadbeefdeadbeef"),
            ("prose", "quick: something", "a hallway conversation")):
        out, note = add.learn(root, "method", lesson, evidence=ev)
        assert out, f"{why}: the lane was blocked -> {note!r}"

    outside = tmp_path / "bare" / ".add"          # no git repo anywhere above it
    add.init(outside, "code", "P")
    out, note = add.learn(outside, "method", "quick: outside any repo", evidence=sha)
    assert out, f"a bundle outside a repo blocked the lane: {note!r}"


def test_tripwire_calls_git_read_only(tmp_path, monkeypatch):
    """covers: M4, R:OUTWARD, E6 — a NO-EXEC notary may look at the tree and must never move it.
    The spy records every git subcommand the verb reaches for, so a future edit that adds a
    `checkout` to "be sure of the state" fails here rather than in someone's working tree.

    Over ALL THREE shapes `_commit_paths` distinguishes, because R:OUTWARD is a property of the
    VERB and a spy proves it only where it walks. This check used to build one fixture whose
    commit was that repo's FIRST, so it walked the parentless branch alone: a `checkout` inserted
    at the head of the merge branch shipped the whole suite green — a tree-moving verb, unbound,
    under a `sensitivity: security` node. A check that cannot fail on the defect passes on
    nothing, and the branches a spy does not walk are exactly where that hides."""
    seen = []
    real = add._git

    def spy(r, *args, **kw):
        seen.append(args[0] if args else "")
        return real(r, *args, **kw)

    # 1 — a PARENTLESS commit: the `--root` branch
    first = _repo(tmp_path / "f", sensitive="[src/auth/**]")
    sha = _commit(tmp_path / "f", "src/auth/token.py")
    monkeypatch.setattr(add, "_git", spy)
    add.learn(first, "method", "quick: rotate the signing keys", evidence=sha)
    monkeypatch.undo()
    assert seen, "the tripwire never called git at all"
    root_calls = list(seen)

    # 2 — an ORDINARY commit and 3 — a MERGE: the first-parent branch
    work = tmp_path / "m"
    merged = _repo(work, sensitive="[src/auth/**]")
    _commit(work, "README.md", "# hi\n")
    base = _head(work)
    seen.clear()
    monkeypatch.setattr(add, "_git", spy)
    add.learn(merged, "method", "quick: touch the readme", evidence=_head(work))
    monkeypatch.undo()
    plain_calls = list(seen)

    git("checkout", "-q", "-b", "side", base, cwd=work)
    _commit(work, "src/auth/token.py")
    git("checkout", "-q", "-", cwd=work)
    _commit(work, "other.py")
    git("merge", "-q", "--no-ff", "-m", "merge side", "side", cwd=work)
    seen.clear()
    monkeypatch.setattr(add, "_git", spy)
    add.learn(merged, "method", "quick: merge the token tidy-up", evidence=_head(work))
    monkeypatch.undo()
    merge_calls = list(seen)

    # 4 — a SHALLOW boundary: the early return, which never reaches `diff-tree` at all
    origin = tmp_path / "o"
    origin.mkdir()
    git("init", "-q", cwd=origin)
    git("config", "user.email", "t@example.com", cwd=origin)
    git("config", "user.name", "T", cwd=origin)
    _commit(origin, "src/auth/token.py")
    _commit(origin, "README.md", "# hi\n")
    shallow_work = tmp_path / "s"
    subprocess.run(["git", "clone", "-q", "--depth", "1", f"file://{origin}", str(shallow_work)],
                   capture_output=True, text=True, check=True)
    shallow = _repo_in(shallow_work, sensitive="[src/auth/**]")
    seen.clear()
    monkeypatch.setattr(add, "_git", spy)
    add.learn(shallow, "method", "quick: fix a typo", evidence=_head(shallow_work))
    monkeypatch.undo()
    shallow_calls = list(seen)

    for shape, calls in (("parentless", root_calls), ("single-parent", plain_calls),
                         ("merge", merge_calls), ("shallow boundary", shallow_calls)):
        assert calls, f"the {shape} shape called no git at all — the spy walked nothing"
        assert set(calls) <= {"rev-parse", "diff-tree"}, \
            f"the {shape} shape ran a git command that can move the tree: {calls}"
    # …and each shape really is a DIFFERENT walk, or the sweep above is four copies of one probe
    assert merge_calls != root_calls != shallow_calls, \
        f"three shapes walked one path: {root_calls} / {merge_calls} / {shallow_calls}"
    assert "diff-tree" in merge_calls and "diff-tree" not in shallow_calls, \
        f"the merge and shallow branches were not the ones walked: {merge_calls} / {shallow_calls}"


def test_intake_md_states_it():
    """covers: M5 — the direct lane reads exactly one page, so the pre-edit step lives there: the
    Quick step names `add locate` before the first edit and R:QUICKSIZEUP as what the learn line
    refuses after. Three trees identical, and the surface stays line-neutral vs HEAD."""
    intake = (TREES[0] / "intake.md").read_text(encoding="utf-8")
    assert "add locate" in intake, "the Quick step does not name `add locate` before the edit"
    assert "R:QUICKSIZEUP" in intake, "the Quick step does not name what the learn line refuses"
    for tree in TREES[1:]:
        assert (tree / "intake.md").read_bytes() == (TREES[0] / "intake.md").read_bytes(), tree
    head = subprocess.run(["git", "show", "HEAD:add-method/skill/add/intake.md"],
                          cwd=str(REPO.parent), capture_output=True, text=True)
    if head.returncode == 0:   # TRIPWIRE: HEAD vs worktree, and `git commit` makes them identical
        assert len(intake.splitlines()) == len(head.stdout.splitlines()), \
            "the skill surface grew — fund the addition by compressing"


def test_the_tripwire_reads_paths_in_the_bundles_own_frame(tmp_path):
    """covers: M1, M2, A5, E1 — M2 says the match is A17's matcher, and A17's matcher is defined
    over BUNDLE-PARENT-relative entries. `diff-tree` prints REPO-ROOT-relative paths whatever the
    cwd, so for any bundle below the git root the two frames differ and every comparison silently
    missed: the sensitive floor was inert exactly where this project's own `add-method/.add` lives.

    The engine already knew — `_changed_paths` carries a five-line comment naming this trap and
    naming this repo's nested bundle. This verb reused its matcher and not its `--show-prefix`
    normalisation. The whole class was untestable here because every other check in this file
    builds the bundle at the repo root, where the two frames coincide by accident."""
    root = _repo(tmp_path / "r", sensitive="[src/auth/**]", under="add-method")
    sha = _commit(tmp_path / "r", "add-method/src/auth/token.py")
    out, note = add.learn(root, "method", "quick: rotate the signing keys", evidence=sha)
    assert out is None and "R:QUICKSIZEUP" in note, \
        f"a nested bundle's sensitive floor was inert: {note!r}"
    assert "src/auth/token.py" in note and "add-method/src/auth" not in note, \
        f"the refusal names the path in git's frame, not the bundle's: {note!r}"

    # A17 is the floor this rung exists to anticipate, so they must agree on the same node — and
    # the node has to be frozen the way A17 itself demands, at human authority after an interview.
    # This freeze used to be attempted at `plan:` authority, where A17 REFUSES it: `add.freeze`
    # returned falsy, nothing asserted that, and the check went green on an unfrozen node.
    cid = _frozen_task(root, "auth", ["src/auth/token.py"], by="human:T", authority="human")
    assert add.authority_for(add.scan(root), cid) == "human", "the fixture no longer reaches A17"

    # A path ABOVE the bundle parent is not this bundle's to police — no entry of its could ever
    # name it. The case that BINDS that is a sibling path which would match the pattern if it were
    # merely left unstripped instead of dropped: `src/auth/other.py` at the REPO root belongs to
    # whatever else lives there, and reading it in this bundle's frame refuses on a file this
    # bundle cannot see.
    outside = _commit(tmp_path / "r", "src/auth/other.py")
    out, note = add.learn(root, "method", "quick: touch a sibling project", evidence=outside)
    assert out, f"a path above the bundle parent was policed by this bundle: {note!r}"


def test_a_nested_bundle_sees_its_own_scopes(tmp_path):
    """covers: M1, M2, A2, E2 — the same frame error hid the scope half too: an open frozen task
    owning `src/billing.py` never matched the commit's `add-method/src/billing.py`."""
    root = _repo(tmp_path / "r", under="add-method")
    cid = _frozen_task(root, "billing", ["src/billing.py"])
    sha = _commit(tmp_path / "r", "add-method/src/billing.py")
    out, note = add.learn(root, "method", "quick: tidy the rounding", evidence=sha)
    assert out is None and "R:QUICKSIZEUP" in note, f"a nested bundle's scopes owned nothing: {note!r}"
    assert cid in note and "src/billing.py" in note, note


def test_a_path_git_must_quote_is_still_matched(tmp_path):
    """covers: M1, R:QUICKSIZEUP, E1 — `diff-tree` renders any path outside ASCII through
    `core.quotepath`, so `src/auth/tokén.py` arrives as the literal 14-character string
    `"src/auth/tok\\303\\251n.py"` — quotes and octal escapes and all — which matches no pattern
    anyone would write. The sibling `_changed_paths` reads `-z` for exactly this reason; a floor
    that a non-ASCII filename walks straight through is not a floor."""
    root = _repo(tmp_path / "r", sensitive="[src/auth/**]")
    sha = _commit(tmp_path / "r", "src/auth/tokén.py")
    out, note = add.learn(root, "method", "quick: rename a token helper", evidence=sha)
    assert out is None and "R:QUICKSIZEUP" in note, f"a quoted path walked the floor: {note!r}"
    assert "\\303" not in note and '"src/auth' not in note, f"the path was reported quoted: {note!r}"


def test_a_merge_commit_is_read_through_its_parents(tmp_path):
    """covers: M1, M2, R:QUICKSIZEUP, A6, E1, E3 — `diff-tree` on a MERGE prints nothing at all
    unless told which parent to diff against, so a merge that carried a sensitive path into the
    branch read as a commit that changed no files and the quick lesson landed. A sensitive path
    arriving by merge is a sensitive path arriving.

    Which parent is the whole question. `-m` unions the diff against EVERY parent, and for any
    parent but the first that is "what the other branch was BEHIND on" — so a merge of a side
    branch forked before a sensitive path moved on main was refused naming a file the author
    never touched, which is E3 broken and A6's promise broken with it. Against the FIRST parent
    is what the merge introduced, and that is what M1 means by the commit's changed paths."""
    work = tmp_path / "r"
    root = _repo(work, sensitive="[src/auth/**]")
    _commit(work, "README.md", "# hi\n")
    git("checkout", "-q", "-b", "side", cwd=work)
    _commit(work, "src/auth/token.py")
    git("checkout", "-q", "-", cwd=work)
    _commit(work, "other.py")
    git("merge", "-q", "--no-ff", "-m", "merge side", "side", cwd=work)
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(work),
                         capture_output=True, text=True).stdout.strip()
    out, note = add.learn(root, "method", "quick: merge the token tidy-up", evidence=sha)
    assert out is None and "R:QUICKSIZEUP" in note, f"a merge carried a sensitive path in: {note!r}"
    assert "src/auth/token.py" in note, note

    # An OCTOPUS: the first parent lacks every other branch's contribution, so one diff still
    # carries them all — reading against the first parent loses nothing a union would catch.
    oct_ = tmp_path / "o"
    oroot = _repo(oct_, sensitive="[src/auth/**]")
    _commit(oct_, "README.md", "# hi\n")
    trunk, base = _branch(oct_), _head(oct_)
    for i, rel in enumerate(("a.py", "b.py", "src/auth/token.py")):
        git("checkout", "-q", "-b", f"s{i}", base, cwd=oct_)
        _commit(oct_, rel)
    git("checkout", "-q", trunk, cwd=oct_)
    git("merge", "-q", "--no-ff", "-m", "octopus", "s0", "s1", "s2", cwd=oct_)
    sha = _head(oct_)
    assert len(subprocess.run(["git", "rev-parse", "HEAD^@"], cwd=str(oct_), capture_output=True,
                              text=True).stdout.split()) == 4, "the fixture built no octopus"
    out, note = add.learn(oroot, "method", "quick: land three branches", evidence=sha)
    assert out is None and "src/auth/token.py" in note, f"an octopus hid a sensitive path: {note!r}"

    # …and the direction that was broken: a merge whose OWN contribution is clean. `side` forked
    # before main moved `src/auth/token.py`, so a union against every parent reports that path as
    # though this merge had touched it.
    clean = tmp_path / "c"
    croot = _repo(clean, sensitive="[src/auth/**]")
    _commit(clean, "README.md", "# hi\n")
    base = _head(clean)
    _commit(clean, "src/auth/token.py")
    git("checkout", "-q", "-b", "side", base, cwd=clean)
    _commit(clean, "docs/guide.md", "# g\n")
    git("checkout", "-q", "-", cwd=clean)
    git("merge", "-q", "--no-ff", "-m", "merge side", "side", cwd=clean)
    out, note = add.learn(croot, "method", "quick: merge the doc branch", evidence=_head(clean))
    assert out, f"a merge that introduced only docs/guide.md was refused: {note!r}"


def test_a_parentless_commit_is_read_only_when_git_truly_knows_it(tmp_path):
    """covers: M1, M3, R:LANEBLOCKED, A8, E3 — `--root` is how a repo's genuine FIRST commit gets
    read at all (it has no parent to diff against, so every path it introduced would otherwise
    read as untouched, and the one commit most likely to be someone dropping their secrets in
    would be waved through). But a SHALLOW clone's boundary commit is GRAFTED to look parentless,
    and `--root` there lists the entire tree: `git clone --depth 1`, which is what CI checks out
    by default, turned a clean README-only commit into a refusal naming a file the author never
    touched. The engine cannot see that commit's diff, and A8 says every flavour of cannot-look
    lands the lesson — so the two parentless shapes must be told apart, not treated alike."""
    origin = tmp_path / "o"
    origin.mkdir()
    git("init", "-q", cwd=origin)
    git("config", "user.email", "t@example.com", cwd=origin)
    git("config", "user.name", "T", cwd=origin)
    _commit(origin, "src/auth/token.py")
    _commit(origin, "README.md", "# hi\n")

    # a genuine root commit: `--root` reads it, and the sensitive path it introduced is refused
    first = _repo(tmp_path / "g", sensitive="[src/auth/**]")
    _commit(tmp_path / "g", "src/auth/token.py")
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(tmp_path / "g"),
                         capture_output=True, text=True).stdout.strip()
    out, note = add.learn(first, "method", "quick: start the project", evidence=sha)
    assert out is None and "src/auth/token.py" in note, f"a ROOT commit read as empty: {note!r}"

    # a shallow boundary that only LOOKS parentless: the lane is never blocked on what git
    # cannot tell the engine (R:LANEBLOCKED)
    work = tmp_path / "s"
    subprocess.run(["git", "clone", "-q", "--depth", "1", f"file://{origin}", str(work)],
                   capture_output=True, text=True, check=True)
    git("config", "user.email", "t@example.com", cwd=work)
    git("config", "user.name", "T", cwd=work)
    shallow = _repo_in(work, sensitive="[src/auth/**]")
    sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(work),
                         capture_output=True, text=True).stdout.strip()
    out, note = add.learn(shallow, "method", "quick: fix a typo in the readme", evidence=sha)
    assert out, f"a shallow clone's boundary commit refused a README-only change: {note!r}"


def test_the_bundles_frame_survives_a_name_git_reports_whole(tmp_path):
    """covers: M1, M2, R:QUICKSIZEUP, E1 — `_git` strips by default, and a directory is entitled
    to a LEADING space, so `--show-prefix` for a bundle parent named ` nest` came back as `nest/`.
    Every repo-root-relative path then failed `startswith(prefix)` and was DROPPED as though it
    lay above the parent: `_commit_paths` returned nothing at all and the sensitive floor was
    entirely inert. The frame fix that closed the nested-bundle hole reopened it one character to
    the left; a prefix must be read the way git writes it, with only its own newline removed."""
    root = _repo(tmp_path / "r", sensitive="[src/auth/**]", under=" nest")
    _commit(tmp_path / "r", "README.md", "# hi\n")   # so the cited commit is not the root one
    sha = _commit(tmp_path / "r", " nest/src/auth/token.py")
    out, note = add.learn(root, "method", "quick: rotate the signing keys", evidence=sha)
    assert out is None and "R:QUICKSIZEUP" in note, f"the floor went inert on a name: {note!r}"
    assert "src/auth/token.py" in note and " nest/" not in note, \
        f"the path was not brought into the bundle's frame: {note!r}"


def test_both_walkers_read_one_frame(tmp_path):
    """covers: M2 — the differential. "A repo-root path, as this bundle's own entries are written"
    is ONE fact, and it had TWO readers: the working-tree walker the gate's scope guard uses and
    the commit walker this node added. It was wrong in both, differently — the commit walker read
    `--show-prefix` from the bundle instead of its parent, and BOTH stripped a leading space off
    the answer. Fixing one reader is how a milestone spends six refutes on the same shape, so this
    asks the engine, never a second copy of the rule: the same file, uncommitted and committed,
    must arrive at the same name."""
    work = tmp_path / "r"
    root = _repo(work, sensitive="[src/auth/**]", under=" nest")
    _commit(work, "README.md", "# hi\n")   # so the cited commit is not the root one
    parent = root.parent
    # TRACKED and modified, not untracked: `?? <path>` is the one porcelain shape a mis-strip
    # cannot corrupt, and an untracked fixture was how this differential passed while the sibling
    # walker still mangled ` M add-method/src/auth/token.py` into `dd-method/…`.
    (parent / "src" / "auth").mkdir(parents=True, exist_ok=True)
    (parent / "src" / "auth" / "token.py").write_text("x = 1\n")
    git("add", "-A", cwd=work)
    git("commit", "-q", "-m", "track it", cwd=work)
    (parent / "src" / "auth" / "token.py").write_text("x = 2\n")
    from_tree = add._changed_paths(parent)
    sha = _commit(work, " nest/src/auth/token.py")
    from_commit = add._commit_paths(root, sha)
    assert "src/auth/token.py" in from_tree, f"the working-tree walker lost the frame: {from_tree}"
    assert from_commit == ["src/auth/token.py"], f"the commit walker disagrees: {from_commit}"
    assert [r for r in from_tree if r.endswith("token.py")] == from_commit, \
        f"two readers of one frame gave two answers: {from_tree} vs {from_commit}"


def test_a_merge_refusal_does_not_advertise_the_bypass(tmp_path):
    """covers: M1, A6, R:QUICKSIZEUP — the refusal is read by an author who took the lane in good
    faith, and for a MERGE it names a path they did not write. `git pull` is the ordinary way that
    happens: the author's own change is one doc page, a colleague's sensitive commit arrives with
    the merge, and the engine cannot tell the two apart — no `diff-tree` flag separates a pull from
    merging your own branch (`-c` reports nothing for either, which is how the carry got missed in
    the first place).

    So the detection stays and the ADVICE changes. A6's own cost-if-wrong is that the author drops
    the `quick:` prefix and the leak stays visible as an unrouted lesson — a refusal that ENDS by
    recommending that teaches the bypass to exactly the population this control is for. On a merge
    it must say the path came in by merge, and it must not close on the escape hatch."""
    work = tmp_path / "r"
    root = _repo(work, sensitive="[src/auth/**]")
    _commit(work, "README.md", "# hi\n")
    base = _head(work)
    trunk = _branch(work)
    _commit(work, "src/auth/token.py")            # a colleague's commit on the trunk
    git("checkout", "-q", "-b", "side", base, cwd=work)
    _commit(work, "docs/guide.md", "# g\n")       # the author's own, and only, change
    git("merge", "-q", "--no-ff", "-m", "merge the trunk in", trunk, cwd=work)
    out, note = add.learn(root, "method", "quick: add a guide page", evidence=_head(work))
    assert out is None and "src/auth/token.py" in note, f"the carry went unseen: {note!r}"
    # On the FIRST line, where the refusal says what happened — not merely somewhere in the note.
    # The aside also contains the word, so `"merge" in note` passed while the lede still said the
    # commit "touched" the path, which is the claim M6 is about.
    assert "merge" in note.splitlines()[0].lower(), \
        f"the refusal's own account still says the commit touched it: {note.splitlines()[0]!r}"
    assert "add new Task" in note and "--scope" in note, f"M1's fix line is gone: {note!r}"
    _no_bypass_advice(note)
    # M6's other half: every route it names must be one the author can take. Forbidding the bad
    # advice is not enough — DELETING the aside outright satisfied that and shipped green, which
    # leaves a refusal that names a path the author did not write and no way to act on it.
    assert "the commit that made it" in note, \
        f"the merge refusal offers no route for a path the author did not write: {note!r}"

    # …and an ordinary, non-merge refusal keeps naming the fix exactly as M1 froze it.
    plain = _repo(tmp_path / "p", sensitive="[src/auth/**]")
    _commit(tmp_path / "p", "README.md", "# hi\n")
    sha = _commit(tmp_path / "p", "src/auth/token.py")
    out, note = add.learn(plain, "method", "quick: rotate them", evidence=sha)
    assert out is None and "add new Task" in note and "--scope" in note, note
    assert "merge" not in note.lower(), f"a plain commit was called a merge: {note!r}"
    _no_bypass_advice(note)

    # M6 binds BOTH halves, merge and not: the owner half's refusal is where dropping the prefix
    # actually WORKS, so it is the one that must never mention it.
    owned = _repo(tmp_path / "o")
    _frozen_task(owned, "billing", ["src/billing.py"])
    _commit(tmp_path / "o", "README.md", "# hi\n")
    sha = _commit(tmp_path / "o", "src/billing.py")
    out, note = add.learn(owned, "method", "quick: tidy the rounding", evidence=sha)
    assert out is None, note
    _no_bypass_advice(note)
    assert "--evidence" in note and "/tasks/billing.md" in note, \
        f"the owner half names no route to the node that owns the path: {note!r}"
    assert add.learn(owned, "method", "tidy the rounding", evidence=sha)[0], \
        "the owner half stopped reading the quick line — the asymmetry is gone"


def test_locate_answers_for_the_floor_not_only_the_owner(tmp_path):
    """covers: S2, M5 — `add locate <path>` is the ONE pre-edit step the Quick route runs, and S2
    says it is what makes the tripwire fire "before the commit". It read `scope:` alone, so on a
    bundle declaring `sensitive_paths: [src/auth/**]` it answered `no node scopes src/auth/token.py`
    — a FALSE ALL-CLEAR for the security half, from the step whose whole promise is that changing
    course is still free. The pre-edit control covered the OWNER and not the FLOOR, which is
    backwards: the floor is checked FIRST and always wins."""
    root = _repo(tmp_path / "r", sensitive="[src/auth/**]")
    hits, note = add.locate(root, "src/auth/token.py")
    assert "src/auth/**" in note and "floor" in note.lower(), \
        f"the pre-edit step gave an all-clear on a declared sensitive path: {note!r}"
    assert "no node scopes" in note, f"the owner half of the answer was lost: {note!r}"

    # a path the floor does NOT claim still answers exactly as it always did (E2's shape)
    _, clean = add.locate(root, "docs/guide.md")
    assert "no node scopes" in clean and "floor" not in clean.lower(), clean

    # and an owner is still named when there is one, floor or no floor
    cid = _frozen_task(root, "billing", ["src/billing.py"])
    _, owned = add.locate(root, "src/billing.py")
    assert cid.rsplit("/", 1)[-1][:-3] in owned, owned


def test_the_floor_does_not_read_the_prefix(tmp_path):
    """covers: M1, M3, R:QUICKSIZEUP, E5 — the floor is unstrikeable, so a prefix the author picks
    cannot gate it. The refusal used to end by recommending exactly that prefix be dropped, which
    made "drop `quick:`" the one-token evasion the control advertised to the population it exists
    for. Now the sensitive half reads EVERY lesson whose evidence resolves to a commit.

    The OWNER half still reads the quick line alone, and that asymmetry is the point: `learn` takes
    a commit sha OR a task cid as evidence, never both, so a lesson about a Task's own work
    legitimately cites that Task's own commit — inspecting the owner half there would refuse the
    normal case. An owner is a routing hint; a floor is a floor."""
    root = _repo(tmp_path / "r", sensitive="[src/auth/**]")
    _commit(tmp_path / "r", "README.md", "# hi\n")
    sha = _commit(tmp_path / "r", "src/auth/token.py")
    for lesson in ("rotating the signing keys turned out to need a migration",
                   "Quick: rotate them", "  quick: rotate them", "the keys rotate cleanly now"):
        out, note = add.learn(root, "method", lesson, evidence=sha)
        assert out is None and "R:QUICKSIZEUP" in note, \
            f"the floor read the prefix and let {lesson!r} through: {note!r}"
        assert "floor human" in note, note

    # …and the OWNER half reads the quick line alone: the same commit under a frozen scope lands
    # when the lesson is an ordinary one, because that is how a Task's own work gets written up.
    owned = _repo(tmp_path / "o")
    cid = _frozen_task(owned, "billing", ["src/billing.py"])
    _commit(tmp_path / "o", "README.md", "# hi\n")
    sha = _commit(tmp_path / "o", "src/billing.py")
    landed, note = add.learn(owned, "method", "rounding needed a decimal, not a float", evidence=sha)
    assert landed, f"a lesson about a task's own work was refused by the owner half: {note!r}"
    out, note = add.learn(owned, "method", "quick: tidy the rounding", evidence=sha)
    assert out is None and cid in note, f"the owner half stopped reading the quick line: {note!r}"


def test_a_routed_path_has_nothing_left_to_size_up(tmp_path):
    """covers: M1, E9 — the tripwire exists to catch a change with NO node. Widening the floor to
    every lesson closed the prefix evasion and, with it, the route for writing up security work at
    all: an `--escape` post-mortem ABOUT a security fix necessarily cites that fix's commit, and a
    write-up of work a done Task already routed cites that Task's commit. Both were refused, and
    told to `add new Task` for a path a node already owns. A refusal an author cannot act on is one
    they route around — so a path some node scopes, whatever its status, has nothing left to size
    up. Unrouted work is still refused, and the prefix still buys nothing."""
    root = _repo(tmp_path / "r", sensitive="[src/auth/**]")
    _commit(tmp_path / "r", "README.md", "# hi\n")
    sha = _commit(tmp_path / "r", "src/auth/token.py")
    out, note = add.learn(root, "method", "the rotation taught us to pin", evidence=sha)
    assert out is None and "R:QUICKSIZEUP" in note, f"unrouted work escaped the floor: {note!r}"

    for state in (None, "done"):
        routed = _repo(tmp_path / f"n-{state}", sensitive="[src/auth/**]")
        _frozen_task(routed, "rotate", ["src/auth/token.py"], closed=state,
                     by="human:T", authority="human")
        _commit(tmp_path / f"n-{state}", "README.md", "# hi\n")
        sha = _commit(tmp_path / f"n-{state}", "src/auth/token.py")
        landed, note = add.learn(routed, "method", "the rotation taught us to pin", evidence=sha)
        assert landed, f"a path a {state or 'open'} node already scopes was refused: {note!r}"

    # the escape lane, which is the one this most matters for: a post-mortem about a security fix
    esc = _repo(tmp_path / "e", sensitive="[src/auth/**]")
    _frozen_task(esc, "bypass", ["src/auth/token.py"], by="human:T", authority="human")
    _commit(tmp_path / "e", "README.md", "# hi\n")
    sha = _commit(tmp_path / "e", "src/auth/token.py")
    landed, note = add.learn(esc, "method", "the bypass escaped because the check ran after the redirect",
                             evidence=sha, escape=True, why_missed="no test drove an unauthenticated redirect",
                             prevention="check → tests/test_auth_redirect.py")
    assert landed, f"an escape post-mortem about routed security work was refused: {note!r}"

    # …and the OWNER half is untouched by the exemption. A path that is owned but NOT sensitive
    # is the only way to ask that question in isolation: a Task scoped INTO a declared sensitive
    # pattern is floored to `human` by A17 and cannot be `plan:`-frozen at all, which is why the
    # fixture cannot simply reuse the one above.
    owned = _repo(tmp_path / "w")
    cid = _frozen_task(owned, "billing", ["src/billing.py"])
    _commit(tmp_path / "w", "README.md", "# hi\n")
    sha = _commit(tmp_path / "w", "src/billing.py")
    out, note = add.learn(owned, "method", "quick: tweak the rounding", evidence=sha)
    assert out is None and cid in note, f"the exemption ate the owner half: {note!r}"


def test_a_node_that_holds_nothing_routes_nothing(tmp_path):
    """covers: M1, M2 — the floor stands down on a path some node already scopes, so what counts
    as "scopes" IS the security boundary. Read with `fnmatch`, `*` crosses `/`, and one unfrozen
    node created by anyone — `add new Task junk --scope '**'`, exit 0, no freeze, no human —
    stood the floor down for EVERY sensitive path in the bundle, permanently. The node routed
    nothing: M2 binds containment to how `scope_digest` reads an entry, where `Path.glob` does NOT
    cross `/`, so `*.py`'s freshness set is empty and that node provably holds zero files.

    One fact, one reader: an entry covers a path when the freshness set it expands to contains it.
    A node whose scope holds no files cannot have routed anything."""
    for entry in ("**", "*", "*.py", "**/*", "[a-z]*"):
        root = _repo(tmp_path / f"g{abs(hash(entry))}", sensitive="[src/auth/**]")
        add.new(root, "Task", "junk", title="junk", scope=[entry])
        _commit(tmp_path / f"g{abs(hash(entry))}", "README.md", "# hi\n")
        sha = _commit(tmp_path / f"g{abs(hash(entry))}", "src/auth/token.py")
        out, note = add.learn(root, "method", "quick: dropped a key in token.py", evidence=sha)
        assert out is None and "R:QUICKSIZEUP" in note, \
            f"`--scope {entry}` stood the security floor down: {note!r}"

    # …and an UNFROZEN node routes nothing either, however exactly it names the path. `add new`
    # is one command with no validation and no human; a node that has been through none of the
    # loop has routed nothing, which is what M2 already says for the owner half.
    draft = _repo(tmp_path / "draft", sensitive="[src/auth/**]")
    add.new(draft, "Task", "rotate", title="rotate", scope=["src/auth/token.py"])
    _commit(tmp_path / "draft", "README.md", "# hi\n")
    sha = _commit(tmp_path / "draft", "src/auth/token.py")
    out, note = add.learn(draft, "method", "quick: dropped a key", evidence=sha)
    assert out is None and "R:QUICKSIZEUP" in note, \
        f"an unfrozen node stood the security floor down: {note!r}"

    # a FROZEN node that holds the file routes it — the exemption is real, not removed
    real = _repo(tmp_path / "real", sensitive="[src/auth/**]")
    _frozen_task(real, "rotate", ["src/auth/token.py"], by="human:T", authority="human")
    _commit(tmp_path / "real", "README.md", "# hi\n")
    sha = _commit(tmp_path / "real", "src/auth/token.py")
    assert add.learn(real, "method", "the rotation taught us to pin", evidence=sha)[0], \
        "a node that genuinely scopes the path stopped routing it"

    # …and a FROZEN node whose glob entry holds NOTHING routes nothing either. This is the case
    # the freeze requirement alone does not catch: `--scope '*.py'` is not a sensitive scope, so
    # A17 does not floor it and a milestone PLAN can freeze it with no human at all. Read with
    # `fnmatch`, `*` crosses `/` and that node stands the floor down for `src/auth/token.py`
    # while its own freshness set is empty — the node holds one file, `top.py`, and routed nothing.
    wide = _repo(tmp_path / "wide", sensitive="[src/auth/**]")
    _frozen_task(wide, "pyfiles", ["*.py"])
    (tmp_path / "wide" / "top.py").write_text("x = 1\n")
    _commit(tmp_path / "wide", "README.md", "# hi\n")
    sha = _commit(tmp_path / "wide", "src/auth/token.py")
    out, note = add.learn(wide, "method", "quick: dropped a key in token.py", evidence=sha)
    assert out is None and "R:QUICKSIZEUP" in note, \
        f"a FROZEN node holding only top.py stood the floor down for src/auth/: {note!r}"
    assert {d["path"] for d in add.scope_digest(tmp_path / "wide", ["*.py"])} == {"top.py"}, \
        "the fixture's glob entry does not hold what this check assumes"

    # The OWNER half reads the same entry the same way, or the two halves diverge and A5's
    # disjointness — what makes the corrected ordering true — quietly stops holding. Asked where
    # it DISCRIMINATES: with a sensitive pattern in play the floor answers first and the owner
    # half is never reached, so this bundle declares none. `_paths_touch('src/auth/token.py',
    # '*.py')` is True — fnmatch's `*` crosses `/` — while the freshness set for `*.py` holds
    # `top.py` alone, so the two readers disagree exactly here.
    plainb = _repo(tmp_path / "plainb")
    _frozen_task(plainb, "pyfiles", ["*.py"])
    (tmp_path / "plainb" / "top.py").write_text("x = 1\n")
    _commit(tmp_path / "plainb", "README.md", "# hi\n")
    deep = _commit(tmp_path / "plainb", "src/auth/token.py")
    landed, note = add.learn(plainb, "method", "quick: something deep", evidence=deep)
    assert landed, f"the owner half claimed a path its own freshness set does not hold: {note!r}"
    shallow = _commit(tmp_path / "plainb", "top.py", "x = 2\n")
    out, note = add.learn(plainb, "method", "quick: something shallow", evidence=shallow)
    assert out is None and "/tasks/pyfiles.md" in note, \
        f"the owner half lost the file its scope DOES hold: {note!r}"

    # a node of ANY type routes, not only a Task — `_scoped_by_any` is type-blind on purpose
    ms = _repo(tmp_path / "ms", sensitive="[src/auth/**]")
    cid, _ = add.new(ms, "Milestone", "wave", title="wave", scope=["src/auth/token.py"])
    mp = ms / cid.lstrip("/")
    nd = add.read(mp, "T2")
    stamp = 'verified:\n  - { by: "human:T", at: 2026-09-13, act: freeze, authority: human }'
    add.write(mp, f"---\n{nd['raw']}\n{stamp}\n---\n" + nd["body"])
    _commit(tmp_path / "ms", "README.md", "# hi\n")
    sha = _commit(tmp_path / "ms", "src/auth/token.py")
    assert add.learn(ms, "method", "the rotation taught us to pin", evidence=sha)[0], \
        "a frozen Milestone scoping the path routed nothing — the exemption is Task-only"

    # a DIRECTORY entry holds what lies under it, as `scope_digest` reads one
    dirs = _repo(tmp_path / "dirs", sensitive="[src/auth/**]")
    _frozen_task(dirs, "auth", ["src/auth"], by="human:T", authority="human")
    _commit(tmp_path / "dirs", "README.md", "# hi\n")
    sha = _commit(tmp_path / "dirs", "src/auth/token.py")
    assert add.learn(dirs, "method", "the rotation taught us to pin", evidence=sha)[0], \
        "a directory scope entry did not route the file beneath it"


def test_one_reader_of_what_a_scope_entry_holds(tmp_path):
    """covers: M2 — the differential. "Does this entry cover this path" had THREE readers: the
    floor exemption (`fnmatch`, `*` crosses `/`), the owner half (the same), and `scope_digest`'s
    freshness set (`Path.glob`, `*` does not) — which is the one M2 names. They disagreed exactly
    where it mattered, and `locate` was a fourth answering differently again, so the pre-edit step
    said "floor human · no node scopes it" for a path `learn` waved straight through.

    Asked of the ENGINE, never re-implemented here: whatever `scope_digest` says an entry holds is
    what every other reader of that entry must say."""
    work = tmp_path / "r"
    root = _repo(work, sensitive="[src/auth/**]")
    (work / "src" / "auth").mkdir(parents=True)
    (work / "src" / "auth" / "token.py").write_text("k = 1\n")
    (work / "top.py").write_text("x = 1\n")
    git("add", "-A", cwd=work)
    git("commit", "-q", "-m", "files", cwd=work)
    for entry in ("*.py", "**", "src/auth", "src/auth/token.py"):
        held = {d["path"] for d in add.scope_digest(work, [entry])}
        for path in ("src/auth/token.py", "top.py"):
            assert add._scope_holds(work, entry, path) == (path in held), (
                f"`{entry}` covers {path!r}? the freshness set says {path in held}, "
                f"the floor's reader says {add._scope_holds(work, entry, path)}")


def test_the_owner_half_names_a_route_that_works(tmp_path):
    """covers: M1, M6, E10 — M6 says every route a refusal names must be one the author can take,
    and the owner half's `next:` was not. Run verbatim against the task that already owns the path,
    `add new Task <slug> --scope <path>` creates a SECOND node colliding with a frozen contract and
    lands the author back on a byte-identical refusal. Only the parenthetical `--evidence <cid>`
    worked — so the working route was in brackets and the named one was a dead end.

    The same `next:` line does work on the FLOOR half, where no node owns the path. So the halves
    name different routes, and this drives both to the end rather than reading the strings."""
    root = _repo(tmp_path / "r")
    cid = _frozen_task(root, "billing", ["src/billing.py"])
    _commit(tmp_path / "r", "README.md", "# hi\n")
    sha = _commit(tmp_path / "r", "src/billing.py")
    out, note = add.learn(root, "method", "quick: tidy the rounding", evidence=sha)
    assert out is None, note
    nxt = next(l for l in note.splitlines() if l.startswith("next:"))
    assert "--evidence" in nxt and cid in nxt, \
        f"the owner half's `next:` is not the route that works: {nxt!r}"
    assert "add new Task" in note, "the separate-work route is gone entirely"

    # …and it is DRIVEN: the named route files the lesson, it does not merely read well.
    landed, why = add.learn(root, "method", "tidy the rounding", evidence=cid)
    assert landed, f"the route the refusal names does not file the lesson: {why!r}"

    # the FLOOR half keeps `add new Task` as its `next:`, where it is the route that works
    floor = _repo(tmp_path / "f", sensitive="[src/auth/**]")
    _commit(tmp_path / "f", "README.md", "# hi\n")
    sha = _commit(tmp_path / "f", "src/auth/token.py")
    out, note = add.learn(floor, "method", "quick: rotate them", evidence=sha)
    assert out is None, note
    nxt = next(l for l in note.splitlines() if l.startswith("next:"))
    assert "add new Task" in nxt and "--scope" in nxt, \
        f"the floor half lost the route that works for it: {nxt!r}"
    _no_bypass_advice(note)


def test_only_a_node_the_floor_itself_floored_can_route(tmp_path):
    """covers: M1, M2, R:QUICKSIZEUP, E9 — the exemption trusts a freeze stamp, and a freeze stamp
    costs no human when A17 cannot see the scope entry. `authority_for` reads an entry with
    `_paths_touch`, where `_paths_touch('**/*', 'src/auth/**')` is False, so the interview never
    arms and `add freeze` stamps at `process`; `_scoped_by_any` reads the SAME entry with
    `_scope_holds`, where `**/*` holds every file in the tree. The one shape invisible to the
    human-authority gate was exactly the shape that holds everything — four commands, no human,
    and the sensitive floor was down bundle-wide and permanently.

    So routing is not "a node was frozen" but "a node THIS FLOOR ITSELF FLOORED was frozen". The
    two matchers still disagree; the disagreement now fails CLOSED, because a node A17 reads as
    `process` routes nothing no matter how wide its entry."""
    for entry in ("**/*", "**", ".", "./", "src/..", "*"):
        work = tmp_path / f"w{abs(hash(entry))}"
        root = _repo(work, sensitive="[src/auth/**]")
        cid, _ = add.new(root, "Task", "junk", title="junk", scope=[entry])
        p = root / cid.lstrip("/")
        from conftest import DRAFTED_ASSUMPTIONS, DRAFTED_CHECKS, DRAFTED_RULES, draft_direction
        draft_direction(root, cid, rules=DRAFTED_RULES, checks=DRAFTED_CHECKS,
                        assumptions=DRAFTED_ASSUMPTIONS)
        n = add.read(p, "T2")
        add.write(p, f"---\n{n['raw']}\n---\n"
                  + n["body"].replace("## PLAN", "## PLAN\nregression: none · fixture", 1))
        ok, _ = add.freeze(root, cid, "cli", None)     # the DEFAULT freeze: no --by, no authority
        _commit(work, "README.md", "# hi\n")
        sha = _commit(work, "src/auth/token.py")
        for lesson in ("quick: dropped a key in token.py", "dropped a key in token.py"):
            out, note = add.learn(root, "method", lesson, evidence=sha)
            assert out is None and "R:QUICKSIZEUP" in note, (
                f"`--scope {entry}` + a no-human freeze (recorded: {bool(ok)}) stood the "
                f"security floor down for {lesson!r}: {note!r}")

    # …and a node A17 DID floor to human still routes, or the exemption you asked for is gone
    real = _repo(tmp_path / "real", sensitive="[src/auth/**]")
    cid = _frozen_task(real, "rotate", ["src/auth/token.py"], by="human:T", authority="human")
    assert add.authority_for(add.scan(real), cid) == "human", "the fixture no longer reaches A17"
    _commit(tmp_path / "real", "README.md", "# hi\n")
    sha = _commit(tmp_path / "real", "src/auth/token.py")
    assert add.learn(real, "method", "the rotation taught us to pin", evidence=sha)[0], \
        "a node A17 floored to human stopped routing its own path"


def test_a_scope_entry_never_takes_the_lane_down(tmp_path):
    """covers: M3, M4, R:LANEBLOCKED, R:OUTWARD, E6 — `_scope_files` is now reached from `learn`
    for EVERY node in the graph, which is exposure this build created: before it, `learn` read no
    node's scope at all. An absolute entry raised out of the verb — `Path.glob('/etc/*')` is a
    NotImplementedError and `relative_to` on an out-of-tree path is a ValueError — so ONE node
    anyone can write turned every `add learn` into a traceback instead of a refusal, and the
    direct lane's one bundle write was lost to the engine's own inability to look."""
    root = _repo(tmp_path / "r", sensitive="[src/auth/**]")
    _commit(tmp_path / "r", "README.md", "# hi\n")
    sha = _commit(tmp_path / "r", "src/auth/token.py")
    for i, entry in enumerate(("/etc/*", "/etc/hosts", "../../outside.py", "")):
        cid, _ = add.new(root, "Task", f"n{i}", title="n", scope=[entry])
        p = root / cid.lstrip("/")
        n = add.read(p, "T2")
        # `sensitivity: security` is not decoration: `_scoped_by_any` reads the freeze stamp and
        # the computed floor BEFORE it reads any scope entry, so a fixture node left at the
        # scaffold's `process` is skipped and `_scope_files` is never called on its entry at all.
        # Raising unconditionally inside `_scope_candidates` shipped 24/24 green until these two
        # lines landed — the guard worked, and the check that claimed to bind it reached nothing.
        raw = add.set_key(n["raw"], "sensitivity", "security")
        stamp = 'verified:\n  - { by: "human:T", at: 2026-09-13, act: freeze, authority: human }'
        add.write(p, f"---\n{raw}\n{stamp}\n---\n" + n["body"])
        assert add.authority_for(add.scan(root), cid) == "human", \
            f"the fixture node scoping {entry!r} is not floored to human, so the floor never " \
            "reads its entry and this loop measures nothing"
        out, note = add.learn(root, "method", "quick: a note", evidence=sha)
        assert note and "R:QUICKSIZEUP" in note, \
            f"a node scoping {entry!r} did not leave the lane a refusal: {note!r}"

    # R:OUTWARD over the reader the refactor put on this path: a frozen DIRECTORY scope sends
    # `_scope_files` through `git ls-files`, a verb the enumeration did not anticipate, and no
    # fixture declared one — a `checkout` injected there shipped the whole suite green.
    d = _repo(tmp_path / "d", sensitive="[src/auth/**]")
    _frozen_task(d, "dirs", ["src"], by="human:T", authority="human")
    _commit(tmp_path / "d", "README.md", "# hi\n")
    sha = _commit(tmp_path / "d", "src/auth/token.py")
    seen, real = [], add._git

    def spy(r, *args, **kw):
        seen.append(args[0] if args else "")
        return real(r, *args, **kw)

    add._git = spy
    try:
        add.learn(d, "method", "quick: a note", evidence=sha)
    finally:
        add._git = real
    assert seen, "the spy walked nothing"
    assert set(seen) <= {"rev-parse", "diff-tree", "ls-files"}, \
        f"a frozen directory scope ran a git command that can move the tree: {seen}"
    assert "ls-files" in seen, "the directory branch was never walked — this proves nothing"


def test_a_scope_entry_holds_a_path_exactly(tmp_path):
    """covers: M2 — containment is EQUALITY over the freshness set, and nothing said so: reading
    it as `startswith` shipped the whole suite green, which would make `src/auth/token.py.bak`
    route `src/auth/token.py`. Also pins the glob semantics this control's security depends on —
    `Path.glob('**')` matches no files before 3.13 and every file from 3.13, so CI (3.10, 3.12)
    and a developer's interpreter disagree about the literal entry M1's rationale names."""
    work = tmp_path / "r"
    root = _repo(work, sensitive="[src/auth/**]")
    (work / "src" / "auth").mkdir(parents=True)
    for rel in ("src/auth/token.py", "src/auth/token.py.bak", "top.py"):
        (work / rel).write_text("x = 1\n")
    git("add", "-A", cwd=work)
    git("commit", "-q", "-m", "files", cwd=work)
    assert add._scope_holds(work, "src/auth/token.py.bak", "src/auth/token.py") is False, \
        "a longer path routed a shorter one — containment is not a prefix test"
    assert add._scope_holds(work, "src/auth/token.py", "src/auth/token.py") is True

    import sys
    held = {f.relative_to(work).as_posix() for f in add._scope_files(work, "**")}
    if sys.version_info >= (3, 13):
        assert "src/auth/token.py" in held, "3.13+ `**` should hold files"
    else:
        assert held == set(), f"before 3.13 `**` holds no files, got {sorted(held)[:4]}"
    # …and the shape that is version-INDEPENDENT, which is the one the attack used
    assert "src/auth/token.py" in {f.relative_to(work).as_posix()
                                   for f in add._scope_files(work, "**/*")}, \
        "`**/*` must hold every file on every supported interpreter"


def test_a_freeze_nobody_signed_routes_nothing(tmp_path):
    """covers: M1, M2, R:QUICKSIZEUP, E9 — the seal is not the signature.

    Round six closed the disarm by demanding that A17 have floored the routing node to `human`.
    That reads the COMPUTED floor, and `freeze` WRITES `authority: human` whenever the computed
    floor is human: `claimed_authority(None, floor)` returns the floor, the default `--by` is
    `cli`, and `interview_gap` has nothing to ask when the author left no open decisions — which
    the author controls. So `add new <type> <slug> --scope <a sensitive path>` followed by a bare
    `add freeze` stamped `authority: human` with no human anywhere, and the floor stood down on
    it in two commands. M1 says the seal and WHO SIGNED IT do not stay blind. Who signed it was
    read nowhere; `human:` appears in no comparison in the engine.

    So the routing node must carry a signature, not just a computed floor. A `by:` string is
    still a claim — a notary cannot verify a person — but it is a DELIBERATE claim, and that is
    exactly the line the ledger already draws between `human:<name>`, `plan:<m>` and `cli`.
    """
    root = _repo(tmp_path / "r", sensitive="[src/auth/**]")
    _commit(tmp_path / "r", "README.md", "# hi\n")
    sha = _commit(tmp_path / "r", "src/auth/token.py")

    # the negative control: with no node at all, the floor refuses. If this ever passes, every
    # assertion below is measuring nothing.
    out, note = add.learn(root, "method", "rotated the key", evidence=sha)
    assert out is None and "R:QUICKSIZEUP" in note, \
        f"the floor did not refuse an unrouted sensitive path, so this check proves nothing: {note!r}"

    # THE DISARM, driven the way the refute drove it: two verbs, no flags beyond --scope, and
    # the engine itself computes `authority: human` off A17 and stamps `by: cli`.
    for kind in ("Task", "Persona"):
        work = tmp_path / f"d{kind}"
        r = _repo(work, sensitive="[src/auth/**]")
        _commit(work, "README.md", "# hi\n")
        deep = _commit(work, "src/auth/token.py")
        if kind == "Task":
            # a Task's placeholders must be authored first — which is the AI's own job, and the
            # author controls the one thing that arms the interview: `interview_gap` has nothing
            # to put to a human when ASSUMPTIONS is empty, so `freeze` never demands one.
            from conftest import draft_direction
            cid, _ = add.new(r, kind, "p", title="p", scope=["src/auth/token.py"])
            draft_direction(r, cid, assumptions="",
                            rules="<must>\n- M1 the key is rotated (from: the author)\n"
                                  "</must>\n<reject>\n</reject>",
                            checks="- test_rotation · covers: M1 · the key changes")
            n = add.read(r / cid.lstrip("/"), "T2")
            add.write(r / cid.lstrip("/"), f"---\n{n['raw']}\n---\n"
                      + n["body"].replace("## PLAN", "## PLAN\nregression: none · fixture", 1))
            assert add.interview(r, cid)[0] == [], \
                "the fixture's node has open decisions, so `freeze` demands an interview and the " \
                "disarm this check measures is not the one the refute drove"
            ok, why = add.freeze(r, cid, "cli", None)
            assert ok, f"the fixture could not freeze the {kind}: {why}"
        else:
            # a Persona is not a LIFECYCLE type, so `placeholders_in` finds no RULES to demand
            # and a bare freeze lands on a file nobody authored at all
            cid, _ = add.new(r, kind, "p", title="p", scope=["src/auth/token.py"])
            ok, why = add.freeze(r, cid, "cli", None)
            assert ok, f"the fixture could not freeze the {kind}: {why}"
        stamp = next((v for v in (add.read(r / cid.lstrip("/"), "T2")["fm"].get("verified") or [])
                      if v.get("act") == "freeze"), None)
        assert stamp and stamp.get("authority") == "human" and stamp.get("by") == "cli", (
            f"the fixture no longer reproduces the disarm — a bare freeze on a {kind} stamped "
            f"{stamp!r}. If `freeze` now refuses this, say so here and keep the check; if it "
            "stamps something else, this check is measuring a shape the engine cannot make.")
        out, note = add.learn(r, "method", "rotated the key", evidence=deep)
        assert out is None and "R:QUICKSIZEUP" in note, (
            f"a {kind} frozen by `cli` with a computed `authority: human` stood the security "
            f"floor down — two commands, no human, no interview: {note!r}")

    # …and a `plan:` signature does not buy it either. A milestone plan is the AI's own ratified
    # authority; A17 exists precisely because a plan may not sign for a sensitive path.
    pl = _repo(tmp_path / "pl", sensitive="[src/auth/**]")
    _commit(tmp_path / "pl", "README.md", "# hi\n")
    deep = _commit(tmp_path / "pl", "src/auth/token.py")
    cid, _ = add.new(pl, "Persona", "p", title="p", scope=["src/auth/token.py"])
    add.freeze(pl, cid, "plan:m", None)
    out, note = add.learn(pl, "method", "rotated the key", evidence=deep)
    assert out is None and "R:QUICKSIZEUP" in note, \
        f"a `plan:` signature stood a human-floored path down: {note!r}"

    # The exemption is still REAL: a node a person actually signed routes its own path, and the
    # lesson lands. Without this the fix is indistinguishable from deleting the exemption.
    ok = _repo(tmp_path / "ok", sensitive="[src/auth/**]")
    _frozen_task(ok, "rotate", ["src/auth/token.py"], by="human:T", authority="human")
    _commit(tmp_path / "ok", "README.md", "# hi\n")
    good = _commit(tmp_path / "ok", "src/auth/token.py")
    landed, note = add.learn(ok, "method", "the rotation taught us to pin", evidence=good)
    assert landed, f"a node a human signed stopped routing its own path: {note!r}"


def test_every_reader_of_a_scope_entry_is_known_and_fails_closed(tmp_path):
    """covers: M1, M2 — the census, and the invariant that survives the census being wrong.

    Six rounds of refutes on this node found the same defect three times, each a gate to the left
    of the last, because "does this scope entry cover this path" has SIX readers through THREE
    matchers and no check enumerated them. `authority_for` decides whether a freeze owes a human;
    `_scoped_by_any` decides whether the floor stands down. They read the same entry differently,
    and `--scope '**/*'` was the shape only one of them could see.

    They cannot be collapsed into one matcher — A17 governs every node's authority engine-wide and
    that is not this node's to move. So two things are bound instead. First a CENSUS: the set of
    functions reading a `scope:` entry is known, and a new one fails here rather than silently
    becoming reader number seven. Second the INVARIANT that makes the disagreement SAFE rather than
    absent: over every entry that has been used to attack this floor, a node routes a sensitive path
    only if A17 owes a human for it. An entry the two matchers read differently does not route —
    that is the fail-CLOSED half, and it is asserted to be non-empty too, because an invariant that
    never meets a disagreement is an invariant that passes on nothing."""
    import ast
    src = (REPO / "tooling" / "add.py").read_text()
    readers = {fn.name for fn in ast.walk(ast.parse(src)) if isinstance(fn, ast.FunctionDef)
               and any(isinstance(c, ast.Call) and isinstance(c.func, ast.Name)
                       and c.func.id == "_scope_list" for c in ast.walk(fn))}
    assert readers == {"authority_for", "gate", "locate", "quick_hit", "_scoped_by_any",
                       "run", "wave"}, (
        f"the set of functions reading a `scope:` entry changed: {sorted(readers)}.\n"
        "Whichever way it moved, say which matcher the new reader uses and why that is the right "
        "one for the question it asks — three readers disagreeing is how this node's security "
        "floor was disarmed three times.")

    # The invariant, over the entries that have actually been used to attack this floor.
    routed, closed = set(), set()
    for i, entry in enumerate(("**/*", "**", ".", "./", "src/..", "*", "*.py", "src",
                               "src/auth/token.py", "[a-z]*", "**/**", "src/auth")):
        work = tmp_path / f"e{i}"
        root = _repo(work, sensitive="[src/auth/**]")
        (work / "src" / "auth").mkdir(parents=True)
        (work / "src" / "auth" / "token.py").write_text("k = 1\n")
        cid, _ = add.new(root, "Task", "n", title="n", scope=[entry])
        p = root / cid.lstrip("/")
        n = add.read(p, "T2")
        stamp = ('verified:\n  - { by: "human:T", at: 2026-09-13, act: freeze, '
                 'authority: human }')
        add.write(p, f"---\n{n['raw']}\n{stamp}\n---\n" + n["body"])
        graph = add.scan(root)
        holds = add._scope_holds(work, entry, "src/auth/token.py")
        if add._scoped_by_any(work, graph, "src/auth/token.py"):
            assert add.authority_for(graph, cid) == "human", (
                f"`--scope {entry}` stands the sensitive floor down on src/auth/token.py, but A17 "
                f"reads it as `{add.authority_for(graph, cid)}` — so a `plan:` freeze buys the "
                "exemption and no human ever sees it. That is the disarm, and it is open again.")
            routed.add(entry)
        elif holds:
            closed.add(entry)
    assert {"src", "src/auth", "src/auth/token.py"} <= routed, (
        f"only {sorted(routed)} route — an entry that honestly names the sensitive path must still "
        "be able to own it, or the floor refuses work that is properly contracted.")
    assert closed, (
        "no entry HOLDS the path while failing to route it, so the fail-closed branch never ran and "
        "this check would pass with `_scoped_by_any` trusting the matcher it does not use.")

    # The other half of the same question, swept the same way: the computed floor is not a
    # signature. Every entry that routed above must STOP routing when the identical node is
    # signed by anyone but a person — `cli` is what a bare `add freeze` writes, and `plan:<m>`
    # is the AI's own ratified authority, which A17 exists to say may not sign here.
    for signer in ("cli", "plan:m", "agent:add-worker", "human", "shuman:x"):
        work = tmp_path / f"s{signer.replace(':', '_')}"
        root = _repo(work, sensitive="[src/auth/**]")
        (work / "src" / "auth").mkdir(parents=True)
        (work / "src" / "auth" / "token.py").write_text("k = 1\n")
        cid, _ = add.new(root, "Task", "n", title="n", scope=["src/auth/token.py"])
        p = root / cid.lstrip("/")
        n = add.read(p, "T2")
        add.write(p, f"---\n{n['raw']}\nverified:\n  - {{ by: \"{signer}\", at: 2026-09-13, "
                     f"act: freeze, authority: human }}\n---\n" + n["body"])
        graph = add.scan(root)
        assert add.authority_for(graph, cid) == "human", "the fixture stopped being A17-floored"
        assert not add._scoped_by_any(work, graph, "src/auth/token.py"), (
            f"a freeze signed `{signer}` stood the sensitive floor down. The computed floor is "
            "written BY the engine off A17, so reading it back asks the engine whether the engine "
            "thought a human was owed — never whether one signed.")

    # And the two remaining ways a node could reach the exemption without being the thing M1
    # names — each one a mutant that shipped the whole file green until it was written down.
    for label, sensitivity, act in (("a plan-floored node", "data", "freeze"),
                                    ("an interview with no freeze", "security", "interview")):
        work = tmp_path / f"b{label.replace(' ', '_')}"
        root = _repo(work, sensitive="[src/auth/**]")
        (work / "src" / "auth").mkdir(parents=True)
        (work / "src" / "auth" / "token.py").write_text("k = 1\n")
        # `**/*` so A17 cannot see the entry (the round-six disarm shape) and the node's own
        # `sensitivity:` sets the floor — and it HOLDS the path, or the loop measures nothing
        cid, _ = add.new(root, "Task", "n", title="n",
                         scope=["**/*" if act == "freeze" else "src/auth/token.py"])
        p = root / cid.lstrip("/")
        n = add.read(p, "T2")
        raw = add.set_key(n["raw"], "sensitivity", sensitivity)
        add.write(p, f'---\n{raw}\nverified:\n  - {{ by: "human:T", at: 2026-09-13, '
                     f'act: {act}, authority: human }}\n---\n' + n["body"])
        graph = add.scan(root)
        assert not add._scoped_by_any(work, graph, "src/auth/token.py"), (
            f"{label}, signed by a person, stood the sensitive floor down. Only a FREEZE at the "
            "floor this control itself demanded a human for may route — a plan is the AI's own "
            "ratified authority, and an interview is a question asked, not an answer sealed.")
