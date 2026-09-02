"""A node that was never authored is never advised to freeze.

`direction.md` states the design — "There is no author verb — you fill those sections by editing
that file directly" — and no affordance in the engine knew it. `BEAT_NEXT["direction"]` mapped the
whole beat to `add freeze {slug}`, so from the moment `add new Task` wrote a file of placeholders,
five surfaces recommended a verb `freeze` is structurally guaranteed to refuse (add.py:1394).

On Milestones the same advice is not refused — it SUCCEEDS. `placeholders_in` reads only
RULES · ASSUMPTIONS · CHECKS (add.py:2595) and a Milestone body carries none of those, so the
guard is Task-only by construction and silently vacuous on the other lifecycle type: ADD's one
human approval could be stamped against a node stating no goal, no scope, no exit criterion.

Every check here drives a real surface against a real node. Grepping `add.py` for the new string
would prove the string exists, not that any surface emits it — which is the exact shape of check
that let the defect ship (R:GREEN_BY_SOURCE).
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

AUTHORING = "author"          # the corrected advice names the authoring work


def _recommends_freeze(text: str, slug: str) -> bool:
    """Does this advice recommend `freeze` as the IMMEDIATE next action?

    Not a substring test. M3 requires the advice to match `freeze`'s own refusal sentence word
    for word — "author <slug>'s RULES, ASSUMPTIONS and CHECKS, then add freeze <slug>" — which
    NAMES the verb that follows the authoring, and must, or an agent matching on a leading
    `add …` loses its cue entirely (A1). What M1 forbids is recommending freeze as the thing to
    run NOW. So the test is position, not presence.
    """
    for line in text.splitlines():
        line = line.strip().removeprefix("next:").strip()
        line = re.sub(r"^[·\s]*\S+\s+→\s+", "", line)      # todo's `· slug → <advice>` arrow
        if line.startswith(f"add freeze {slug}"):
            return True
    return False


def _bundle(tmp_path):
    add.init(tmp_path, "code", "T")
    return tmp_path


def _scaffold(root, slug="scaffold", node_type="Task"):
    """A node exactly as `new` writes it — every section still template."""
    cid, msg = add.new(root, node_type, slug, title=slug)
    return cid, msg


def _authored_task(root, slug="authored", **fields):
    """A Task the placeholder guard accepts — so these checks probe the ADVICE, not authoring."""
    cid, _ = add.new(root, "Task", slug, title=slug, **fields)
    p = root / cid.lstrip("/")
    t = p.read_text(encoding="utf-8")
    t = t.replace("- S1 <the surface this publishes — an endpoint, function, or section>",
                  "- S1 the lister")
    t = t.replace("goal: <one line>", "goal: the fixture states its one line.")
    t = re.sub(r"## RULES\n<must>\n.*?\n</must>",
               "## RULES\n<must>\n- M1 the lister returns only the caller's rows\n</must>", t, flags=re.S)
    t = re.sub(r"<reject>\n.*?\n</reject>",
               '<reject>\n- R:LEAK another tenant\'s row is returned -> "LEAK"\n</reject>', t, flags=re.S)
    t = re.sub(r"## ASSUMPTIONS\n.*?\nevery `gives:`", "## ASSUMPTIONS\n" + "".join(
        f"- A{i} [{d}] covers: S1 · the request does not say; taking the plain reading -> minor\n"
        for i, d in enumerate(("who", "which", "when", "absent", "order", "experience"), 1)
    ) + "every `gives:`", t, flags=re.S)
    t = re.sub(r"## CHECKS\n.*?\nred-first",
               "## CHECKS\n- test_only_own_rows · covers: M1, R:LEAK · proves isolation\nred-first",
               t, flags=re.S)
    p.write_text(t, encoding="utf-8")
    return cid


def _milestone_authored_narrowly(root, slug="narrow-ms"):
    """goal · why · EXIT authored; SCOPE and GROUND deliberately left template.

    This is the boundary M7 was narrowed to (decided 2026-09-01): the three fields the milestone
    lifecycle already depends on, since `milestone_done` refuses on `why:` and on the EXIT tally.
    """
    cid, _ = add.new(root, "Milestone", slug, title=slug)
    p = root / cid.lstrip("/")
    t = p.read_text(encoding="utf-8")
    t = t.replace("goal: <one line>", "goal: prove the guard stops where it was told to stop")
    t = re.sub(r"why: <[^>]*>", "why: a guard everyone widens past is worse than a narrow one", t)
    t = t.replace("- [ ] <criterion>   (← <task>)", "- [ ] the one real criterion   (← some-task)")
    p.write_text(t, encoding="utf-8")
    return cid


def _authored_milestone(root, slug="real-ms"):
    """A Milestone with a stated goal, why, scope, ground and one exit criterion."""
    cid, _ = add.new(root, "Milestone", slug, title=slug)
    p = root / cid.lstrip("/")
    t = p.read_text(encoding="utf-8")
    t = t.replace("goal: <one line>", "goal: prove an authored milestone is still accepted")
    t = re.sub(r"why: <[^>]*>", "why: the guard must refuse a scaffold without refusing real work", t)
    t = re.sub(r"<[a-z_][^>\n]*>", "authored", t)     # every remaining template slot
    p.write_text(t, encoding="utf-8")
    return cid


# ---- M1 · the five surfaces --------------------------------------------------------------

def test_status_advises_authoring_for_a_scaffold_task(tmp_path):
    """covers: M1, R:GREEN_BY_SOURCE — drives `status`, reads its emitted text."""
    root = _bundle(tmp_path)
    _scaffold(root, "s1")
    out = add.status(root)
    assert not _recommends_freeze(out, "s1"), f"status advised a verb freeze would refuse:\n{out}"
    assert AUTHORING in out.lower(), out


def test_todo_advises_authoring_for_a_scaffold_task(tmp_path):
    """covers: M1, R:GREEN_BY_SOURCE — the arrow must not contradict its own annotation."""
    root = _bundle(tmp_path)
    _scaffold(root, "s2")
    _, note = add.todo(root)
    assert not _recommends_freeze(note, "s2"), f"todo advised a verb freeze would refuse:\n{note}"
    assert AUTHORING in note.lower(), note


def test_new_returns_authoring_advice(tmp_path):
    """covers: M1, R:GREEN_BY_SOURCE — the message `new` hands back."""
    root = _bundle(tmp_path)
    _, msg = _scaffold(root, "s3")
    assert not _recommends_freeze(msg, "s3"), msg
    assert AUTHORING in msg.lower(), msg


def test_new_card_line_names_authoring(tmp_path):
    """covers: M1, M6 — the `beat:` line inside the FILE, read back from disk."""
    root = _bundle(tmp_path)
    cid, _ = _scaffold(root, "s4")
    body = (root / cid.lstrip("/")).read_text(encoding="utf-8")
    card = next(ln for ln in body.splitlines() if ln.startswith("beat:"))
    assert not card.strip().startswith("beat: direction"), card
    assert AUTHORING in card.lower(), card


def test_new_advises_authoring_for_a_scaffold_milestone(tmp_path):
    """covers: M1, A2 — the Milestone path gets the same treatment as the Task path.

    Driven against `new`, NOT `status`: `status`'s `next:` line targets the task frontier and
    never names a milestone at all, so asserting there would pass without the fix (the vacuous
    shape R:VACUOUS_GUARD forbids). `new` is where the milestone advice is actually emitted —
    and unlike the Task path, the freeze it recommends SUCCEEDS.
    """
    root = _bundle(tmp_path)
    _, msg = _scaffold(root, "s5", node_type="Milestone")
    assert not _recommends_freeze(msg, "s5"), f"a milestone scaffold was advised to freeze:\n{msg}"
    assert AUTHORING in msg.lower(), msg


# ---- M2 · one notion of "authored" -------------------------------------------------------

def test_advice_and_freeze_agree_over_a_fixture_table(tmp_path):
    """covers: M2, A3, R:SECOND_TRUTH — advised-to-freeze and freeze-accepts are one boolean."""
    root = _bundle(tmp_path)
    cases = {"tpl": _scaffold(root, "tpl")[0], "real": _authored_task(root, "real")}
    graph = add.scan(root)
    for name, cid in cases.items():
        slug = cid.rsplit("/", 1)[-1][:-3]
        advised = _recommends_freeze(add._next_verb(graph, cid), slug)
        accepted = bool(add.freeze(root, cid, by="probe")[0])
        assert advised == accepted, (
            f"{name}: advice says freeze={advised} but freeze returned {accepted} — "
            f"two notions of authored")


def test_authoring_advice_matches_the_freeze_refusal_sentence(tmp_path):
    """covers: M3, A1 — one instruction, and it carries a runnable `add …` continuation."""
    root = _bundle(tmp_path)
    cid, _ = _scaffold(root, "s6")
    advice = add._next_verb(add.scan(root), cid)
    refusal = add.freeze(root, cid, by="probe")[1]
    assert AUTHORING in advice.lower(), advice
    assert "s6" in advice, advice
    assert "add " in advice, f"an agent matching on `add ` loses its cue entirely: {advice}"
    assert AUTHORING in refusal.lower(), refusal


# ---- M4 · a frozen node is untouched ------------------------------------------------------

def test_frozen_node_affordances_are_unchanged(tmp_path):
    """covers: M4, A9 — a stamped node still points at the build beat."""
    root = _bundle(tmp_path)
    cid = _authored_task(root, "sealed")
    assert bool(add.freeze(root, cid, by="probe")[0]) is True
    nxt = add._next_verb(add.scan(root), cid)
    assert AUTHORING not in nxt.lower(), f"a frozen node was dragged back to authoring: {nxt}"
    assert "add brief sealed" == nxt, nxt


def test_freeze_stamp_wins_over_placeholders(tmp_path):
    """covers: E2, A9 — a pre-3.0 bundle's stamped-but-templated node is not re-authored."""
    root = _bundle(tmp_path)
    cid = _authored_task(root, "legacy")
    add.freeze(root, cid, by="probe")
    p = root / cid.lstrip("/")
    p.write_text(p.read_text(encoding="utf-8").replace(
        "- M1 the lister returns only the caller's rows",
        "- M1 <the rule that must hold>"), encoding="utf-8")
    nxt = add._next_verb(add.scan(root), cid)
    assert AUTHORING not in nxt.lower(), f"frozen must win over placeholders: {nxt}"


# ---- the absent / degenerate readings ------------------------------------------------------

def test_unknown_beat_still_falls_back_to_status(tmp_path):
    """covers: A6 — an unrecognised beat degrades, never raises."""
    assert add.BEAT_NEXT.get("no-such-beat", "add status") == "add status"


def test_unreadable_body_advises_authoring(tmp_path):
    """covers: A7 — cannot read the body -> advise authoring, the conservative direction."""
    root = _bundle(tmp_path)
    cid, _ = _scaffold(root, "s7")
    p = root / cid.lstrip("/")
    fm = p.read_text(encoding="utf-8").split("---")[1]
    p.write_text(f"---{fm}---\n", encoding="utf-8")          # frontmatter only, no body
    nxt = add._next_verb(add.scan(root), cid)
    assert AUTHORING in nxt.lower(), f"an unreadable body was advised to freeze: {nxt}"


def test_authored_rules_with_template_gives_reads_unauthored(tmp_path):
    """covers: E1, A8 — the two predicates are combined, not chosen between."""
    root = _bundle(tmp_path)
    cid = _authored_task(root, "s8")
    p = root / cid.lstrip("/")
    p.write_text(p.read_text(encoding="utf-8").replace(
        "- S1 the lister",
        "- S1 <the surface this publishes — an endpoint, function, or section>"), encoding="utf-8")
    nxt = add._next_verb(add.scan(root), cid)
    assert AUTHORING in nxt.lower(), f"template `gives:` still read as authored: {nxt}"


def test_empty_frontier_affordance_is_unchanged(tmp_path):
    """covers: E3, M4 — the no-open-task path is untouched."""
    root = _bundle(tmp_path)
    out = add.status(root)
    assert "add new" in out, out


def test_frontier_order_is_unchanged(tmp_path):
    """covers: A10 — `ready()` ordering is identical before and after."""
    root = _bundle(tmp_path)
    for s in ("b-two", "a-one", "c-three"):
        _scaffold(root, s)
    assert add.ready(add.scan(root)) == sorted(add.ready(add.scan(root)))


# ---- M7 · the Milestone guard that was never there -----------------------------------------

def test_freeze_refuses_a_pure_milestone_scaffold(tmp_path):
    """covers: M7, E4 — RED against today's engine, which records the stamp."""
    root = _bundle(tmp_path)
    cid, _ = _scaffold(root, "ms-tpl", node_type="Milestone")
    ok, note = add.freeze(root, cid, by="probe")
    assert bool(ok) is False, f"a milestone stating no goal took the ONE human approval: {note}"


def test_milestone_guard_is_narrow_by_design(tmp_path):
    """covers: M7 — authored goal · why · EXIT with a TEMPLATE GROUND still freezes.

    M7 was narrowed on purpose. A guard reaching SCOPE and GROUND too would refuse real
    milestones whose ground is thin, and a guard everyone learns to widen past is worse than
    a narrow one that holds.
    """
    root = _bundle(tmp_path)
    cid = _milestone_authored_narrowly(root, "narrow")
    ok, note = add.freeze(root, cid, by="probe")
    assert bool(ok) is True, f"the guard over-reached past goal/why/EXIT: {note}"


def test_milestone_guard_names_sections_the_body_actually_has(tmp_path):
    """covers: R:VACUOUS_GUARD — driven against BOTH halves.

    A guard that looks in a section a Milestone body does not contain returns clean and passes
    the accept half while failing the refuse half. Both must hold.
    """
    root = _bundle(tmp_path)
    tpl, _ = _scaffold(root, "ms-vac", node_type="Milestone")
    real = _authored_milestone(root, "ms-real")
    assert bool(add.freeze(root, tpl, by="probe")[0]) is False, "the scaffold half"
    assert bool(add.freeze(root, real, by="probe")[0]) is True, \
        "the authored half — the guard over-refused"


# ---- the closed rejects ---------------------------------------------------------------------

def test_quick_lane_is_unaffected(tmp_path):
    """covers: E5, R:NEW_VERB — a scaffold detector must not fire on the one-call lane's slots."""
    root = _bundle(tmp_path)
    cid = _authored_task(root, "q1", depth="quick")
    assert bool(add.freeze(root, cid, by="probe")[0]) is True


def test_no_new_verb_in_the_cli_surface():
    """covers: R:NEW_VERB — the verb list is unchanged BY THIS TASK.

    Re-aimed 23 -> 24 when `interview` shipped (task freeze-interview). The pin is a
    value, not a ceiling: this check asserts that the authoring-beat work added no verb,
    and a later task legitimately adding one moves the number without weakening that.
    """
    sys.path.insert(0, str(REPO / "tooling"))
    import cli
    verbs = [a.choices.keys() for a in cli.build_parser()._subparsers._group_actions]
    assert len(list(verbs[0])) == 24, "this task changes what the engine SAYS, never its verb set"


def test_status_frontmatter_vocabulary_is_unchanged(tmp_path):
    """covers: R:STATUS_ENUM — the beat is DERIVED; no new `status:` value is written."""
    root = _bundle(tmp_path)
    cid, _ = _scaffold(root, "s9")
    fm = add.scan(root)[cid]["fm"]
    assert fm["status"] == "direction", fm["status"]
    assert "scaffold" not in add.ACTIVE_STATES


# ---- M8 · the replan's falsified A5 ---------------------------------------------------------

def test_frozen_node_card_names_brief(tmp_path):
    """covers: M8, S5 — the sibling the 2026-08-17 replan named.

    A freshly frozen node advertised `next: add freeze <slug>` in its own CARD — the approval it
    had just passed — because `freeze` does not move `status:` and the CARD line is written once.
    """
    root = _bundle(tmp_path)
    cid = _authored_task(root, "sealed-card")
    assert bool(add.freeze(root, cid, by="probe")[0]) is True
    add.render_card(root, cid)
    card = next(ln for ln in (root / cid.lstrip("/"))
                .read_text(encoding="utf-8").splitlines() if ln.startswith("beat:"))
    assert "add freeze" not in card, f"a frozen node advertises the verb it already passed: {card}"
    assert "brief" in card, card


def test_card_drift_compares_the_derived_beat(tmp_path):
    """covers: M8 — today `card_drift` compares against the RAW `status:` field.

    `freeze` leaves `status: direction`, so the CARD's stale `direction` matches it and the
    drift detector reports CLEAN on a node whose derived beat has moved to `build`.
    """
    root = _bundle(tmp_path)
    cid = _authored_task(root, "drifted")
    assert bool(add.freeze(root, cid, by="probe")[0]) is True
    graph = add.scan(root)
    assert add._beat_of(graph[cid]) == "build", "precondition: the derived beat moved"
    drift = [d for d in add.card_drift(graph) if d[0] == cid]
    assert drift, "card_drift called a node clean whose CARD names a beat it has left"


def test_a_half_authored_node_still_reads_unauthored(tmp_path):
    """covers: A4 — the probe: one remaining placeholder still reads unauthored.

    A4 took all-gone, matching `freeze` exactly. Taking first-real-edit instead would advise a
    half-authored node toward the freeze that refuses it — today's defect with a smaller window.
    """
    root = _bundle(tmp_path)
    cid = _authored_task(root, "half")
    p = root / cid.lstrip("/")
    p.write_text(p.read_text(encoding="utf-8").replace(
        "- M1 the lister returns only the caller's rows",
        "- M1 <the rule that must hold>"), encoding="utf-8")
    graph = add.scan(root)
    t2 = add.read(graph[cid]["path"], "T2")

    assert add._is_scaffold(graph[cid], t2) is True, "one placeholder left must still read unauthored"
    assert bool(add.freeze(root, cid, by="probe")[0]) is False, "and freeze must agree"


def test_cold_resume_reaches_authoring_without_a_refusal(tmp_path):
    """covers: A11 — the probe: the cold-resume path reaches authoring without first running a
    verb that refuses.

    A11's reader is the agent resuming a session having read nothing else: it reads `next:` and
    acts. Before this, it ran `freeze`, read a refusal, and spent a turn rediscovering what
    `status` could have said in the line it already printed.
    """
    root = _bundle(tmp_path)
    _scaffold(root, "cold")
    nxt = add.status(root).splitlines()[-1].removeprefix("next:").strip()

    assert not _recommends_freeze(nxt, "cold"), nxt
    assert AUTHORING in nxt.lower() and "cold" in nxt, nxt
    # and the verb it DOES name, when reached, is not a refusal
    assert "add freeze cold" in nxt, "the follow-on verb stays named, so an agent keeps a cue"
