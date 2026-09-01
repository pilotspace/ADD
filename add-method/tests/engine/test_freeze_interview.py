"""The ONE approval asks its questions out loud.

`freeze` already refuses an incomplete contract eight ways — template placeholders, an
unauthored `gives:`, collapsed surfaces, unswept (dimension, surface) pairs, an unbudgeted
explore. Every one of those checks the DOCUMENT. None checks the CONVERSATION.

`## ASSUMPTIONS` is by construction a list of silences the AI filled in on the human's behalf,
each line carrying the reading taken and the cost if it is wrong. The sweep made the AI write
those down. Nothing made it ASK. So the ONE human approval ADD asks for is a single stamp that
says nothing about whether the human was ever shown a single decision they are approving.

At a human floor, `freeze` now refuses until every open decision has been put to a human and
answered: R:UNINTERVIEWED. The refusal keys on the COMPUTED floor, never on `--authority`,
because a guard with a one-flag off switch is a guard that gets switched off.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

DIMS = ("who", "which", "when", "absent", "order", "experience")
TREES = (Path(".claude/skills/add"),
         Path("add-method/skill/add"),
         Path("add-method/src/add_method/_bundled/skill/add"))


def _bundle(tmp_path):
    add.init(tmp_path, "code", "T")
    return tmp_path


def _authored(root, slug="t", rejects=1, na=0, **fields):
    """A Task every existing freeze refusal accepts, so these checks probe the INTERVIEW."""
    cid, _ = add.new(root, "Task", slug, title=slug, **fields)
    p = root / cid.lstrip("/")
    t = p.read_text(encoding="utf-8")
    t = t.replace("- S1 <the surface this publishes — an endpoint, function, or section>",
                  "- S1 the lister")
    t = re.sub(r"## RULES\n<must>\n.*?\n</must>",
               "## RULES\n<must>\n- M1 the lister returns only the caller's rows\n</must>",
               t, flags=re.S)
    rj = "\n".join(f'- R:R{i} thing {i} happens -> "R{i}"' for i in range(1, rejects + 1))
    t = re.sub(r"<reject>\n.*?\n</reject>", f"<reject>\n{rj}\n</reject>", t, flags=re.S)
    lines = []
    for i, d in enumerate(DIMS, 1):
        if i <= na:
            lines.append(f"- A{i} [{d}] covers: S1 · n/a · nothing to decide here\n")
        else:
            lines.append(f"- A{i} [{d}] covers: S1 · the request does not say thing {i}; "
                         f"taking reading {i} -> cost {i}\n")
    t = re.sub(r"## ASSUMPTIONS\n.*?\nevery `gives:`",
               "## ASSUMPTIONS\n" + "".join(lines) + "every `gives:`", t, flags=re.S)
    t = re.sub(r"## CHECKS\n.*?\nred-first",
               "## CHECKS\n- test_only_own_rows · covers: M1, R:R1 · proves isolation\nred-first",
               t, flags=re.S)
    p.write_text(t, encoding="utf-8")
    return cid


def _human_floor(root, slug="h", **kw):
    """A node whose COMPUTED floor is `human` — that is what the interview binds to."""
    return _authored(root, slug, sensitivity="security", **kw)


def _answer_all(root, cid, verdict="confirm", by="Tin Dang"):
    qs, _ = add.interview(root, cid)
    return add.interview(root, cid, answers={q["id"]: verdict for q in qs}, by=by)


def _note(result):
    return str(result[-1])


# ------------------------------------------------------------------ M1 · compile

def test_interview_compiles_one_question_per_open_decision(tmp_path):
    """covers: M1, A2 — non-`n/a` assumptions plus Rejects, and nothing else.

    An `n/a` retirement already states its own reason, and a Must came FROM the human; re-asking
    either is noise, and an interview people learn to click through buys nothing.
    """
    root = _bundle(tmp_path)
    cid = _human_floor(root, "compiled", rejects=2, na=3)   # 6 dims, 3 retired -> 3 + 2 = 5

    qs, _ = add.interview(root, cid)
    ids = [q["id"] for q in qs]
    assert ids == ["A4", "A5", "A6", "R:R1", "R:R2"], ids


def test_interview_prints_the_reading_and_the_cost(tmp_path):
    """covers: M1, A6 — the reader is a human being asked to accept a risk; an id tells them nothing."""
    root = _bundle(tmp_path)
    cid = _human_floor(root, "readable", na=5)

    qs, note = add.interview(root, cid)
    q = next(x for x in qs if x["id"] == "A6")
    assert "reading 6" in q["reading"], q
    assert "cost 6" in q["cost"], q
    assert "reading 6" in note and "cost 6" in note, note


def test_bare_interview_records_nothing(tmp_path):
    """covers: M1 — compiling is a read; only `--answer` writes."""
    root = _bundle(tmp_path)
    cid = _human_floor(root, "readonly")
    add.interview(root, cid)

    stamps = add.read(root / cid.lstrip("/"), "T0")["fm"].get("verified") or []
    assert not [s for s in stamps if isinstance(s, dict) and s.get("act") == "interview"]
    assert not (root / "tasks" / "readonly.d" / "interviews").exists()


# ------------------------------------------------------------------ M2/M3 · record

def test_interview_records_a_stamp_and_a_sidecar(tmp_path):
    """covers: M3 — the answers persist as evidence, not just as a boolean."""
    root = _bundle(tmp_path)
    cid = _human_floor(root, "recorded", na=5)
    node, note = _answer_all(root, cid)
    assert node, note

    stamps = [s for s in add.read(root / cid.lstrip("/"), "T0")["fm"]["verified"]
              if isinstance(s, dict) and s.get("act") == "interview"]
    assert len(stamps) == 1, stamps
    assert stamps[0]["by"] == "Tin Dang"
    assert stamps[0]["interview"].startswith("sha256:")
    side = root / "tasks" / "recorded.d" / "interviews" / "1.md"
    assert side.is_file(), "no sidecar written"
    assert "reading 6" in side.read_text(encoding="utf-8")
    assert "confirm" in side.read_text(encoding="utf-8")


def test_interview_refuses_an_unknown_verdict(tmp_path):
    """covers: M2 — three verdicts, named in the refusal."""
    root = _bundle(tmp_path)
    cid = _human_floor(root, "badverdict", na=5)

    node, note = add.interview(root, cid, answers={"A6": "maybe", "R:R1": "confirm"}, by="H")
    assert not node
    for v in ("confirm", "correct", "defer"):
        assert v in note, note


def test_interview_refuses_an_unknown_id(tmp_path):
    """covers: A10 — a typo must not silently leave a real item unanswered."""
    root = _bundle(tmp_path)
    cid = _human_floor(root, "badid", na=5)

    node, note = add.interview(root, cid, answers={"A99": "confirm"}, by="H")
    assert not node
    assert "A6" in note and "R:R1" in note, note


# ------------------------------------------------------------------ M4/M5 · the refusal

def test_freeze_refuses_an_uninterviewed_human_floor_node(tmp_path):
    """covers: M4, R:UNINTERVIEWED — the headline. Approval for decisions nobody was shown."""
    root = _bundle(tmp_path)
    cid = _human_floor(root, "unasked", na=4)

    node, note = add.freeze(root, cid, by="Tin Dang", authority="human")
    assert not node, "the ONE approval was recorded for questions never asked"
    assert "R:UNINTERVIEWED" in note, note


def test_freeze_refusal_keys_on_the_computed_floor(tmp_path):
    """covers: M5, E1 — `authority = authority or authority_for(...)`, so the flag can DOWNGRADE.

    Keying the interview on the passed argument would ship the guard with its own off switch.
    """
    root = _bundle(tmp_path)
    cid = _human_floor(root, "downgraded", na=4)

    node, note = add.freeze(root, cid, by="Tin Dang", authority="process")
    assert not node, "`--authority process` switched the interview off on a security node"
    assert "R:UNINTERVIEWED" in note, note


def test_a_process_floor_node_is_never_interviewed(tmp_path):
    """covers: M4 — no human in the room, no interview. `plan`/`process` freezes are exempt."""
    root = _bundle(tmp_path)
    cid = _authored(root, "mech", sensitivity="mechanical", na=4)

    node, note = add.freeze(root, cid, by="plan:m")
    assert node, note


def test_freeze_accepts_a_completed_interview(tmp_path):
    """covers: M4 — the happy path still reaches the stamp."""
    root = _bundle(tmp_path)
    cid = _human_floor(root, "asked", na=4)
    _answer_all(root, cid)

    node, note = add.freeze(root, cid, by="Tin Dang", authority="human")
    assert node, note


def test_all_deferred_is_a_complete_interview(tmp_path):
    """covers: E5 — deferring IS answering. A human may accept a risk knowingly."""
    root = _bundle(tmp_path)
    cid = _human_floor(root, "deferred", na=4)
    _answer_all(root, cid, verdict="defer")

    node, note = add.freeze(root, cid, by="Tin Dang", authority="human")
    assert node, note


def test_a_corrected_item_leaves_the_interview_incomplete(tmp_path):
    """covers: M6, E6 — `correct` is cleared by EDITING the item, not by recording it."""
    root = _bundle(tmp_path)
    cid = _human_floor(root, "corrected", na=5)
    qs, _ = add.interview(root, cid)
    add.interview(root, cid, answers={q["id"]: ("correct" if q["id"] == "A6" else "confirm")
                                      for q in qs}, by="Tin Dang")

    node, note = add.freeze(root, cid, by="Tin Dang", authority="human")
    assert not node, "an item the human asked to CORRECT was frozen as approved"
    assert "A6" in note, note


# ------------------------------------------------------------------ M7 · staleness

def test_editing_an_assumption_makes_the_interview_stale(tmp_path):
    """covers: M7, E3 — same shape as `direction:` and `brief:`: a digest, not a boolean."""
    root = _bundle(tmp_path)
    cid = _human_floor(root, "moved", na=5)
    _answer_all(root, cid)
    p = root / cid.lstrip("/")
    p.write_text(p.read_text(encoding="utf-8").replace("taking reading 6", "taking reading six"),
                 encoding="utf-8")

    node, note = add.freeze(root, cid, by="Tin Dang", authority="human")
    assert not node, "an assumption was reworded after approval and the stamp still counted"
    assert "R:UNINTERVIEWED" in note, note


def test_editing_a_must_does_not_stale_the_interview(tmp_path):
    """covers: E2 — the Musts came from the human; re-interviewing for one is ceremony."""
    root = _bundle(tmp_path)
    cid = _human_floor(root, "mustedit", na=5)
    _answer_all(root, cid)
    p = root / cid.lstrip("/")
    p.write_text(p.read_text(encoding="utf-8").replace(
        "only the caller's rows", "only the caller's own rows"), encoding="utf-8")

    node, note = add.freeze(root, cid, by="Tin Dang", authority="human")
    assert node, note


def test_a_refreeze_needs_no_second_interview(tmp_path):
    """covers: E4 — an unchanged node refreezes on the interview it already has."""
    root = _bundle(tmp_path)
    cid = _human_floor(root, "again", na=5)
    _answer_all(root, cid)
    add.freeze(root, cid, by="Tin Dang", authority="human")

    node, note = add.freeze(root, cid, by="Tin Dang", authority="human")
    assert node, note


def test_freeze_reads_the_matching_interview_not_the_latest(tmp_path):
    """covers: E8 — recency is not authority; the digest is."""
    root = _bundle(tmp_path)
    cid = _human_floor(root, "twice", na=5)
    _answer_all(root, cid)                     # interview 1, matches
    p = root / cid.lstrip("/")
    original = p.read_text(encoding="utf-8")
    p.write_text(original.replace("taking reading 6", "taking reading 6b"), encoding="utf-8")
    _answer_all(root, cid)                     # interview 2, matches the EDITED text
    p.write_text(original, encoding="utf-8")   # ...and now revert: 1 matches again, 2 does not

    node, note = add.freeze(root, cid, by="Tin Dang", authority="human")
    assert node, "the earlier interview matches the current text and must satisfy the gate: " + str(note)


# ------------------------------------------------------------------ M8/M9 · edges

def test_an_empty_question_set_needs_no_interview(tmp_path):
    """covers: M8, A4, E7 — `quick` is sweep-exempt, so a security quick node has nothing to ask."""
    root = _bundle(tmp_path)
    cid, _ = add.new(root, "Task", "quiet", title="quiet", depth="quick", sensitivity="security")
    p = root / cid.lstrip("/")
    t = p.read_text(encoding="utf-8")
    t = t.replace("- S1 <the surface this publishes — an endpoint, function, or section>",
                  "- S1 the lister")
    t = re.sub(r"## RULES\n<must>\n.*?\n</must>",
               "## RULES\n<must>\n- M1 the lister returns only the caller's rows\n</must>",
               t, flags=re.S)
    t = re.sub(r"<reject>\n.*?\n</reject>", "<reject>\n</reject>", t, flags=re.S)
    t = re.sub(r"## ASSUMPTIONS\n.*?\nevery `gives:`", "## ASSUMPTIONS\nevery `gives:`",
               t, flags=re.S)
    t = re.sub(r"## CHECKS\n.*?\nred-first",
               "## CHECKS\n- test_only_own_rows · covers: M1 · proves isolation\nred-first",
               t, flags=re.S)
    p.write_text(t, encoding="utf-8")

    qs, _ = add.interview(root, cid)
    assert qs == []
    node, note = add.freeze(root, cid, by="Tin Dang", authority="human")
    assert node, note


def test_interview_runs_last_in_the_ladder(tmp_path):
    """covers: M9, A5 — you cannot interview a human about text that is still a template."""
    root = _bundle(tmp_path)
    cid, _ = add.new(root, "Task", "stub", title="stub", sensitivity="security")

    node, note = add.freeze(root, cid, by="Tin Dang", authority="human")
    assert not node
    assert "R:UNINTERVIEWED" not in note, "asked the human about template slots: " + str(note)
    assert "placeholder" in str(note).lower(), note


def test_the_refusal_names_a_next_verb_and_the_ids(tmp_path):
    """covers: A12 — the reader is an agent that will act on `next:` with no human present."""
    root = _bundle(tmp_path)
    cid = _human_floor(root, "advice", na=4)

    node, note = add.freeze(root, cid, by="Tin Dang", authority="human")
    assert re.search(r"next: add interview advice", str(note)), note
    assert "A5" in str(note) and "R:R1" in str(note), note


# ------------------------------------------------------------------ M10 · the skill

def test_the_interview_instruction_is_in_all_three_skill_trees():
    """covers: M10, A13 — a two-tree edit has shipped a mirror gap in this repo before.

    Deliberately NOT parametrized: pytest reports a parametrized check as `test_x[param]`, and
    `gate` binds bare ids, so a parametrized check binds nothing while sitting there green.
    """
    missing = []
    for tree in TREES:
        taught = any("add interview" in md.read_text(encoding="utf-8")
                     for md in sorted((REPO.parent / tree).rglob("*.md")))
        if not taught:
            missing.append(str(tree))
    assert missing == [], f"the interview is not taught in: {missing}"


def test_no_body_section_was_renumbered():
    """covers: R:RENUMBER — the engine keys sections by name; renaming one silently unbinds it."""
    src = (REPO / "tooling" / "add.py").read_text(encoding="utf-8")
    body = re.search(r'BODIES = \{.*?\n\}', src, re.S).group(0)
    assert body.count("## ") == len(re.findall(r"## [A-Z]", body))
    for section in ("## CARD", "## RULES", "## ASSUMPTIONS", "## PLAN",
                    "## EDGES", "## CHECKS", "## EVIDENCE", "## LESSONS"):
        assert section in body, f"{section} disappeared from the Task template"
