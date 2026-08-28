"""`add check` writes the checklist tally the engine already reads.

covers: task `box-check-verb` (milestone `checkbox-verb`). `milestone_done` gates on a
`- [x]`/`- [ ]` tally in `## EXIT` but the engine shipped no verb that could write one, so every
tick was a hand edit to markdown the engine parses. The human chose the GENERAL verb (any box,
any node, any section) over the evidence-bound notary, and chose an audit stamp over a refusal —
so the stamp and the close line are the only things left standing where the goal-gate was.
Every assertion names the verb, the node and the expectation.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _bundle(tmp_path, boxes=("a", "b", "c")):
    """A bundle with one milestone whose EXIT carries `boxes`, and one task with a PLAN box."""
    add.init(tmp_path, "code", "T")
    mcid, _ = add.new(tmp_path, "Milestone", "ms", title="M")
    mp = tmp_path / mcid.lstrip("/")
    text = mp.read_text(encoding="utf-8")
    exit_block = "## EXIT\n" + "".join(f"- [ ] {b}\n" for b in boxes)
    text = re.sub(r"## EXIT\n(?:- \[[ x]\].*\n)*", exit_block, text)
    mp.write_text(text, encoding="utf-8")
    tcid, _ = add.new(tmp_path, "Task", "t", title="T", milestone="ms")
    tp = tmp_path / tcid.lstrip("/")
    ttext = tp.read_text(encoding="utf-8").replace(
        "## PLAN\n", "## PLAN\n- [ ] p1\n- [ ] p2\n", 1)
    tp.write_text(ttext, encoding="utf-8")
    return mcid, tcid


def _boxes(tmp_path, cid):
    body = add.read(tmp_path / cid.lstrip("/"), "T2")["body"]
    return re.findall(r"^\s*- \[([ xX])\]", body, re.M)


def test_check_marks_and_unmarks_by_index(tmp_path):
    """covers: M1, A3, A9."""
    mcid, _ = _bundle(tmp_path)
    before = (tmp_path / mcid.lstrip("/")).read_text(encoding="utf-8")
    ok, msg = add.check(tmp_path, mcid, [2], by="Tin")
    assert ok, f"add check: refused a valid index 2 on {mcid} — {msg}"
    assert _boxes(tmp_path, mcid) == [" ", "x", " "], \
        f"add check: index 2 did not mark exactly the second box of {mcid}"
    ok, msg = add.check(tmp_path, mcid, [2], off=True, by="Tin")
    assert ok, f"add check --off: refused to unmark box 2 of {mcid} — {msg}"
    assert _boxes(tmp_path, mcid) == [" ", " ", " "], \
        f"add check --off: box 2 of {mcid} was not restored to unmarked"
    after = (tmp_path / mcid.lstrip("/")).read_text(encoding="utf-8")
    assert add._section(after, "exit") == add._section(before, "exit"), \
        f"add check: the EXIT section of {mcid} did not round-trip byte-identically"


def test_check_shares_one_box_pattern_with_the_tally(tmp_path):
    """covers: M1, A3 — one pattern, so the verb and the tally can never disagree."""
    src = (REPO / "tooling" / "add.py").read_text(encoding="utf-8")
    assert re.search(r"^BOX(_RE)?\s*=\s*re\.compile", src, re.M), \
        "add.py: no module-level compiled box pattern — the verb and milestone_done must share one"
    done = src[src.find("def milestone_done"):]
    done = done[:done.find("\ndef ", 1)]
    assert re.search(r"\b(BOX|_box_lines)\b", done), \
        "add.py milestone_done: does not read boxes through the shared pattern"
    assert not re.search(r"re\.(findall|search|match)\(r?[\"'].*\\\[", done), \
        "add.py milestone_done: still counts boxes with its OWN inline regex — one pattern, or the verb can tick a box the goal-gate cannot count"


def test_check_reaches_any_node_and_any_section(tmp_path):
    """covers: M7, A4."""
    mcid, tcid = _bundle(tmp_path)
    ok, msg = add.check(tmp_path, tcid, [1], by="Tin")
    assert ok, f"add check: refused a `## PLAN` box on the Task {tcid} — {msg}"
    assert _boxes(tmp_path, tcid) == ["x", " "], \
        f"add check: the first `## PLAN` box of {tcid} was not marked"
    ok, msg = add.check(tmp_path, mcid, [1], section="EXIT", by="Tin")
    assert ok, f"add check --section EXIT: refused index 1 on {mcid} — {msg}"
    assert _boxes(tmp_path, mcid)[0] == "x", \
        f"add check --section EXIT: index 1 did not re-index from 1 within EXIT on {mcid}"


def test_check_stamps_exactly_one_verified_entry(tmp_path):
    """covers: M3, A2, A5, A19, A30, A34, R:SILENT_TICK."""
    mcid, _ = _bundle(tmp_path)
    add.check(tmp_path, mcid, [1, 3], by="Tin")
    fm = add.read(tmp_path / mcid.lstrip("/"), "T2")["fm"]
    stamps = [s for s in (fm.get("verified") or []) if str(s.get("act")) == "check"]
    assert len(stamps) == 1, f"add check: expected exactly ONE `act: check` stamp on {mcid}, got {len(stamps)}"
    s = stamps[0]
    assert s.get("by") == "Tin", f"add check: the stamp on {mcid} does not name the caller"
    assert "1" in str(s.get("boxes")) and "3" in str(s.get("boxes")), \
        f"add check: the stamp on {mcid} does not name which boxes moved (got {s.get('boxes')!r})"
    assert "EXIT" in str(s.get("boxes")).upper(), \
        f"add check: the stamp on {mcid} does not name the section it wrote (got {s.get('boxes')!r})"
    add.check(tmp_path, mcid, [1], off=True)
    fm = add.read(tmp_path / mcid.lstrip("/"), "T2")["fm"]
    uns = [s for s in fm["verified"] if str(s.get("act")) == "uncheck"]
    assert len(uns) == 1, f"add check --off: no `act: uncheck` stamp on {mcid}"
    assert uns[0].get("by") == "process:check", \
        f"add check: an unattributed call must stamp `process:check` on {mcid}, got {uns[0].get('by')!r}"


def test_check_is_idempotent_and_stamps_nothing_when_nothing_moved(tmp_path):
    """covers: M2, A6, A27, E4."""
    mcid, _ = _bundle(tmp_path)
    add.check(tmp_path, mcid, [1], by="Tin")
    before = (tmp_path / mcid.lstrip("/")).read_text(encoding="utf-8")
    ok, msg = add.check(tmp_path, mcid, [1], by="Tin")
    assert ok, f"add check: a re-run on an already-marked box of {mcid} must succeed, not error — {msg}"
    assert "unchanged" in msg.lower(), f"add check: a no-op on {mcid} does not report `unchanged` — {msg!r}"
    assert (tmp_path / mcid.lstrip("/")).read_text(encoding="utf-8") == before, \
        f"add check: a no-op on {mcid} wrote to the file (a second stamp, or a rewritten box)"


def test_check_refuses_out_of_range_without_writing(tmp_path):
    """covers: M4, M5, A10, E1, R:PARTIAL_WRITE, R:SILENT_NOOP."""
    mcid, _ = _bundle(tmp_path)
    before = (tmp_path / mcid.lstrip("/")).read_text(encoding="utf-8")
    ok, msg = add.check(tmp_path, mcid, [1, 2, 99], by="Tin")
    assert not ok, f"add check: accepted out-of-range index 99 on {mcid}"
    assert "99" in msg, f"add check: the refusal on {mcid} does not name the bad index — {msg!r}"
    assert (tmp_path / mcid.lstrip("/")).read_text(encoding="utf-8") == before, \
        f"add check: a refused call on {mcid} still wrote boxes 1 and 2 (validate ALL before writing ANY)"


def test_check_refuses_bare_ref_by_listing_the_boxes(tmp_path):
    """covers: A7 — no index is never an implicit --all."""
    mcid, _ = _bundle(tmp_path)
    before = (tmp_path / mcid.lstrip("/")).read_text(encoding="utf-8")
    ok, msg = add.check(tmp_path, mcid, [], by="Tin")
    assert not ok, f"add check {mcid} with no index must refuse, never tick everything"
    for i, label in ((1, "a"), (2, "b"), (3, "c")):
        assert f"{i}" in msg and label in msg, \
            f"add check: the bare-ref refusal on {mcid} does not enumerate box {i} ({label!r}) — {msg!r}"
    assert (tmp_path / mcid.lstrip("/")).read_text(encoding="utf-8") == before, \
        f"add check: the bare-ref refusal on {mcid} wrote to the file"


def test_check_refuses_missing_section_and_boxless_node(tmp_path):
    """covers: M4, A8, E3, R:SILENT_NOOP."""
    mcid, _ = _bundle(tmp_path)
    ok, msg = add.check(tmp_path, mcid, [1], section="NOPE", by="Tin")
    assert not ok, f"add check --section NOPE: accepted a heading {mcid} does not carry"
    assert "NOPE" in msg, f"add check: the missing-section refusal does not name `NOPE` — {msg!r}"
    empty, _ = _bundle(tmp_path / "b2", boxes=())
    ok, msg = add.check(tmp_path / "b2", empty, [1], by="Tin")
    assert not ok, f"add check: accepted an index on {empty}, which carries no checkbox at all"
    assert "box" in msg.lower(), f"add check: the boxless refusal does not say so — {msg!r}"


def test_check_ignores_boxes_inside_fenced_blocks(tmp_path):
    """covers: A3, E5, E6 — the index a human reads is the index the verb uses."""
    mcid, _ = _bundle(tmp_path)
    path = tmp_path / mcid.lstrip("/")
    text = path.read_text(encoding="utf-8").replace(
        "## EXIT\n", "## GROUND\nnote:\n```\n- [ ] not a real box\n```\n\n## EXIT\n", 1)
    path.write_text(text, encoding="utf-8")
    ok, msg = add.check(tmp_path, mcid, [1], by="Tin")
    assert ok, f"add check: refused index 1 on {mcid} after a fenced example was added — {msg}"
    body = add.read(path, "T2")["body"]
    assert "- [ ] not a real box" in body, \
        f"add check: index 1 marked the example inside a fenced block in {mcid}, not the first real box"


def test_milestone_done_names_who_checked(tmp_path):
    """covers: M6, A12, A20, A31, E2."""
    mcid, _ = _bundle(tmp_path)
    add.check(tmp_path, mcid, [1, 2], by="Tin")
    add.check(tmp_path, mcid, [3])                       # unattributed — the gate falls here
    path = tmp_path / mcid.lstrip("/")
    raw = path.read_text(encoding="utf-8").replace("why: <why this task exists — optional>", "why: because")
    path.write_text(re.sub(r"(?m)^why: .*$", "why: because", raw), encoding="utf-8")
    ok, msg = add.milestone_done(tmp_path, mcid)
    assert ok, f"milestone_done: refused a fully checked {mcid} — {msg}"
    assert "checked by" in msg, f"milestone_done: the close line does not name who checked — {msg!r}"
    assert "Tin" in msg and "process:check" in msg, \
        f"milestone_done: the close line must name BOTH checkers, oldest first — {msg!r}"
    assert msg.find("Tin") < msg.find("process:check"), \
        f"milestone_done: checkers are not named in stamp order — {msg!r}"


def test_milestone_done_says_by_hand_without_stamps(tmp_path):
    """covers: M6, A14 — a hand-edited milestone invents no name."""
    mcid, _ = _bundle(tmp_path)
    path = tmp_path / mcid.lstrip("/")
    text = path.read_text(encoding="utf-8").replace("- [ ] ", "- [x] ")
    path.write_text(re.sub(r"(?m)^why: .*$", "why: because", text), encoding="utf-8")
    ok, msg = add.milestone_done(tmp_path, mcid)
    assert ok, f"milestone_done: refused a hand-checked {mcid} — {msg}"
    assert "by hand" in msg, \
        f"milestone_done: a milestone with no `act: check` stamp must close saying `by hand` — {msg!r}"


def test_check_never_refuses_on_who(tmp_path):
    """covers: M7, A1, R:GATE_GUARD — the human chose reach over the notary constraint."""
    src = (REPO / "tooling" / "add.py").read_text(encoding="utf-8")
    fn = src[src.find("\ndef check("):]
    fn = fn[:fn.find("\ndef ", 1)]
    assert fn, "add.py: no `check` function found"
    # M3 REQUIRES `authority_for` for the stamp, so the string alone proves nothing. What
    # R:GATE_GUARD forbids is a REFUSAL that turns on who is calling or on task evidence.
    for line in fn.splitlines():
        s = line.strip()
        if s.startswith("return False") or s.startswith("return None,"):
            for tell in ("authority", "by", "human", "process:"):
                assert tell not in s, \
                    f"add.py check: refuses on WHO is ticking — {s!r} mentions `{tell}` (R:GATE_GUARD)"
    assert "←" not in fn, \
        "add.py check: consults a `(← task)` referent — the notary design was decided against (R:GATE_GUARD)"
    code = re.sub(r'"""1?.*?"""', "", fn, flags=re.S)                 # prose is not behavior
    code = "\n".join(ln for ln in code.splitlines() if not ln.strip().startswith("#"))
    assert "gate(" not in code, \
        "add.py check: calls the gate — evidence-bound ticking was decided against (R:GATE_GUARD)"


def test_check_guard_messages_name_their_target():
    """covers: A13, A18."""
    src = Path(__file__).read_text(encoding="utf-8")
    for line in src.splitlines():                      # A18 — runs on any machine, no outside fixture
        if line.startswith(("import ", "from ")):
            mod = line.split()[1].split(".")[0]
            assert mod in {"re", "sys", "hashlib", "pathlib", "add", "cli", "engine_pin"}, \
                f"test_check_verb.py: imports `{mod}` from outside the repo"
    bare = [ln for ln in src.splitlines()
            if ln.strip().startswith("assert ") and ", " not in ln and "\\" not in ln]
    assert not bare, f"test_check_verb.py: bare asserts with no message: {bare[:3]}"


# --- the shipped surface: CLI, the four engine twins, the skill sentence -----------------

ROOT = REPO.parent
ENGINE_TWINS = (REPO / "tooling",
                REPO / "src" / "add_method" / "_bundled" / "tooling",
                REPO / ".add" / "tooling",
                ROOT / ".add" / "tooling")
SKILL_TREES = (REPO / "skill" / "add",
               ROOT / ".claude" / "skills" / "add",
               REPO / "src" / "add_method" / "_bundled" / "skill" / "add")


def test_cli_exposes_check_with_its_flags(tmp_path, capsys):
    """covers: S2, M1, A11, A23, A29."""
    sys.path.insert(0, str(REPO / "tooling"))
    import cli  # noqa: E402
    mcid, _ = _bundle(tmp_path)
    rc = cli.main(["--root", str(tmp_path), "check", "ms", "2", "--by", "Tin"])
    out = capsys.readouterr().out
    assert rc == 0, f"add check ms 2: exited {rc} — {out!r}"
    assert "b" in out, "cli check: stdout does not quote the text of the box it moved (A11)"
    assert _boxes(tmp_path, mcid) == [" ", "x", " "], "cli check: the CLI did not mark box 2"
    rc = cli.main(["--root", str(tmp_path), "check", "ms", "1", "--all"])
    assert rc != 0, "cli check: `--all` alongside an explicit index must refuse, not guess (A29)"
    got = add.check(tmp_path, mcid, [2], by="Tin")   # already marked: probes the shape, moves nothing (A33)
    assert isinstance(got, tuple) and len(got) == 2 and isinstance(got[1], str), \
        f"add.check: returns {got!r}, not the engine's (ok, message) pair that every verb returns"
    rc = cli.main(["--root", str(tmp_path), "check", "ms", "2", "--off"])
    assert rc == 0 and _boxes(tmp_path, mcid) == [" ", " ", " "], "cli check --off: did not unmark box 2"


def test_four_engine_twins_and_both_pins():
    """covers: M8, A22, A26, A32, R:PIN_DRIFT."""
    import hashlib
    source = (REPO / "tooling")
    for name in ("add.py", "cli.py"):
        want = (source / name).read_bytes()
        for twin in ENGINE_TWINS[1:]:
            path = twin / name
            assert path.exists(), f"engine twin missing (not a skip): {path}"
            assert path.read_bytes() == want, f"{path}: differs from add-method/tooling/{name}"
    sys.path.insert(0, str(REPO / "tooling"))
    import engine_pin  # noqa: E402
    for name, pin in (("add.py", engine_pin.ENGINE_MD5), ("cli.py", engine_pin.ENGINE_PKG_MD5)):
        got = hashlib.md5((source / name).read_bytes()).hexdigest()
        assert got == pin, f"engine_pin: {name} is {got}, pinned at {pin} — re-aim the pin (R:PIN_DRIFT)"


def test_skill_names_check_in_the_wired_surface():
    """covers: M9, A17, A21, A25, A28, A35, R:BUDGET_BUMP."""
    for tree in SKILL_TREES:
        skill = tree / "SKILL.md"
        assert skill.exists(), f"skill tree missing (not a skip): {skill}"
        text = skill.read_text(encoding="utf-8")
        line = next((ln for ln in text.splitlines() if "reopen" in ln and "deltas" in ln), None)
        assert line, f"{skill}: no sentence listing the wired loop surface"
        assert "check" in line, f"{skill}: the wired-surface sentence does not name `check` — {line!r}"
    n = len((SKILL_TREES[0] / "SKILL.md").read_text(encoding="utf-8").splitlines())
    assert n <= 176, f"SKILL.md is {n} lines — over the 176 pin (R:BUDGET_BUMP)"


def test_check_summary_lines_pluralise(tmp_path):
    """Found by hand-driving a real bundle: `2 box marked` reads like a defect to an operator."""
    mcid, _ = _bundle(tmp_path)
    _ok, one = add.check(tmp_path, mcid, [1], by="Ada")
    _ok, many = add.check(tmp_path, mcid, [2, 3], by="Ada")
    _ok, noop = add.check(tmp_path, mcid, [2, 3], by="Ada")
    assert one.startswith("1 box marked"), f"add check: one box should read `1 box marked` — {one.splitlines()[0]!r}"
    assert many.startswith("2 boxes marked"), f"add check: two boxes should read `2 boxes marked` — {many.splitlines()[0]!r}"
    assert noop.startswith("unchanged — boxes 2, 3"), \
        f"add check: a multi-box no-op should read `boxes 2, 3` — {noop.splitlines()[0]!r}"
    _ok, single = add.check(tmp_path, mcid, [1], by="Ada")
    assert single.startswith("unchanged — box 1"), \
        f"add check: a single-box no-op should read `box 1` — {single.splitlines()[0]!r}"


def test_every_registry_learned_the_new_verb():
    """covers: M10, S7, A36, A37, A38, A39, A40, A41, R:STALE_REGISTRY.

    A verb ships with every count of it, or the front door lies. This drives the SAME five
    registries that went red when `check` landed — the CLI's WIRED set, both README counts,
    the book command reference, and the phantom fixture that used `add check` precisely
    BECAUSE no such verb existed.
    """
    verbs = set(re.findall(r'sub\.add_parser\("([a-z-]+)"', (REPO / "tooling" / "cli.py").read_text("utf-8")))
    n = len(verbs)
    assert "check" in verbs, "cli.py: `check` is not a registered subcommand"

    wired = (REPO / "tests" / "engine" / "test_cli.py").read_text(encoding="utf-8")
    wired_set = set(re.findall(r'"([a-z-]+)"', wired[wired.find("WIRED = {"):wired.find("}", wired.find("WIRED = {"))]))
    assert wired_set == verbs, f"test_cli.py WIRED drifted from the CLI: {wired_set ^ verbs}"

    for rel in ("README.md", "add-method/README.md"):
        text = (REPO.parent / rel).read_text(encoding="utf-8")
        for claim in re.findall(r"(\d+)-verb kernel", text) + re.findall(r"CLI — (\d+) verbs", text):
            assert int(claim) == n, f"{rel}: claims {claim} verbs, the CLI ships {n} (R:STALE_REGISTRY)"

    ref = (REPO / "docs" / "13-command-reference.md").read_text(encoding="utf-8")
    assert "`check`" in ref, "13-command-reference.md: no row for `check` (R:STALE_REGISTRY)"

    part4 = (REPO / "tests" / "book" / "test_part4.py").read_text(encoding="utf-8")
    phantoms = part4[part4.find("PHANTOM_VERBS"):part4.find("]", part4.find("PHANTOM_VERBS"))]
    assert "add check" not in phantoms, \
        "test_part4.py: `add check` is still listed as a phantom verb, but the engine ships it"
    fixture = (REPO / "tests" / "test_shipped_docs.py").read_text(encoding="utf-8")
    planted = re.search(r"run `add ([a-z-]+)` until green", fixture)
    assert planted, "test_shipped_docs.py: the phantom fixture no longer plants a verb"
    assert planted.group(1) not in verbs, \
        f"test_shipped_docs.py: the phantom fixture plants `{planted.group(1)}`, which the engine now SHIPS — the detector test would pass vacuously (A39)"
