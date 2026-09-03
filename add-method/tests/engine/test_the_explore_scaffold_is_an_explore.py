"""A lane's scaffold produces a node that lane's own freeze refuses.

`--kind explore` is a whole shipped lane. It has a guide (`phases/explore.md`), a freeze refusal
that requires a budget, a gate path that reads `## FINDINGS` instead of a receipt, and three
refusal codes of its own — `explore_drift`, `explore_placeholders`, `hollow_explore`.

It has no front door. Measured 2026-09-03:

    $ add new Task probe --kind explore
    created tasks/probe.md
    $ grep -c 'FINDINGS\\|budget:' .add/tasks/probe.md
    0                                           <- the identical build-lane body
    $ add freeze probe
    cannot freeze `probe` — ... `## PLAN` carries no `budget:` line -> "R:UNBOUNDED"

The author is handed a body for a different lane, then refused for a line the body never offered.

What the explore lane actually wants, from explore.md: RULES are questions, `## PLAN` carries a
required `budget:`, `## FINDINGS` starts empty, and `## CHECKS` STAYS — in acceptance form,
judged at the gate against the findings rather than by pytest.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _bundle(tmp_path):
    add.init(tmp_path, "code", "T")
    return tmp_path


def _body(root, slug, **fields):
    cid, note = add.new(root, "Task", slug, title=slug, **fields)
    assert cid, note
    return add.read(root / cid.lstrip("/"), "T2")["body"], cid


# ------------------------------------------------------------------ M1/M2 · the missing sections

def test_an_explore_scaffold_carries_findings_and_a_budget(tmp_path):
    """covers: M1, M2, A2, R:UNBUILDABLE — the two sections the lane reads and the body lacked."""
    body, _ = _body(_bundle(tmp_path), "probe", kind="explore")
    assert "## FINDINGS" in body, "the gate reads ## FINDINGS and the scaffold writes none"
    assert re.search(r"^budget:", add._section_of(body, "PLAN"), re.M), \
        "`freeze` requires a `budget:` line in ## PLAN and the scaffold offers no slot"


def test_an_explore_freezes_after_filling_only_what_it_was_given(tmp_path):
    """covers: M2, A6, S2 — the measured refusal, closed.

    This is the whole task in one check: an author who fills in every slot the scaffold offered
    must reach a freeze, not a refusal naming a line they were never shown.
    """
    root = _bundle(tmp_path)
    body, cid = _body(root, "probe", kind="explore")
    p = root / cid.lstrip("/")
    text = p.read_text(encoding="utf-8")
    # fill only the slots the scaffold OFFERS — every `<...>` placeholder it shipped
    text = text.replace("covers: <S ids>", "covers: S1")
    text = re.sub(r"<[^<>\n]+>", "x", text)
    text = re.sub(r"^- S1 .*$", "- S1 the surface", text, flags=re.M)
    p.write_text(text, encoding="utf-8")
    node, note = add.freeze(root, cid, by="t", authority="process")
    assert node, f"a fully-filled explore scaffold was still refused: {note}"


# ------------------------------------------------------------------ M3/M4 · the prompts

def test_the_rules_prompt_asks_for_a_question(tmp_path):
    """covers: M3, A2 — a Must in this lane is a question the explore must answer."""
    body, _ = _body(_bundle(tmp_path), "probe", kind="explore")
    rules = add._section_of(body, "RULES")
    assert "question" in rules.lower(), \
        f"the explore RULES prompt still asks for a rule, not a question:\n{rules}"


def test_the_explore_body_keeps_its_checks(tmp_path):
    """covers: M4, A2 — explore.md keeps ## CHECKS, in acceptance form.

    Stated because the first reading of this task had CHECKS dropped, which explore.md
    contradicts in as many words: "one line per question, `covers:` bound, each judged at the
    gate against `## FINDINGS` — not by pytest".
    """
    body, _ = _body(_bundle(tmp_path), "probe", kind="explore")
    assert "## CHECKS" in body, "the explore body dropped ## CHECKS, which explore.md keeps"
    assert "covers:" in add._section_of(body, "CHECKS")


# ------------------------------------------------------------------ M5/M6 · one lane, not the template

def test_a_non_explore_task_body_is_unchanged(tmp_path):
    """covers: M5, E1 — one lane branched, not the template rewritten."""
    root = _bundle(tmp_path)
    # the CARD `next:` carries the node's own slug, so compare with that substituted out
    plain, _ = _body(root, "plain")                       # E1: no kind at all
    feature, _ = _body(root, "feat", kind="feature")
    assert plain.replace("plain", "S") == feature.replace("feat", "S"), \
        "a kind-less Task and a feature Task diverged"
    assert "## FINDINGS" not in plain, "the build lane grew a section it never reads"
    assert not re.search(r"^budget:", add._section_of(plain, "PLAN"), re.M), \
        "the build lane grew a budget line it never reads"


def test_a_fresh_explore_gates_as_hollow(tmp_path):
    """covers: M6, A3, A4, A5, E2 — empty FINDINGS means every question is open.

    A4: the section starts empty on purpose. Pre-filling it would fabricate an answer, and the
    gate's `hollow_explore` refusal is what makes "unanswered" a recorded outcome rather than a
    silent one. E2/A3: the budget is a SLOT, so an unfilled one is still refused at freeze.
    """
    root = _bundle(tmp_path)
    body, cid = _body(root, "probe", kind="explore")
    # "starts empty" means empty OF FINDINGS. The section carries the shape a finding must take
    # — the `(evidence: <ref>)` form is exacting and the gate refuses anything that misses it —
    # but the hint closes no question, so every Must stays open.
    findings = add._section_of(body, "FINDINGS")
    assert "answers M" in findings, "the section teaches the finding shape to nobody"
    assert not re.search(r"answers M\d+\b[^\n]*\(evidence:\s*[^)\s<][^)]*\)", findings), \
        "a fresh explore ships a finding it did not find"

    # E2: the budget slot left as shipped must still refuse, FOR THE BUDGET. The first cut of
    # this check only asserted `node is None`, which passed vacuously — the node was refused for
    # its other placeholders and the budget was never isolated. `test_explore_gate` caught what
    # this missed: the slot satisfied `^budget:\s*\S`, so a fully-drafted explore froze with no
    # budget at all. A refusal assertion that does not name its refusal proves nothing.
    p = root / cid.lstrip("/")
    text = p.read_text(encoding="utf-8")
    text = text.replace("covers: <S ids>", "covers: S1")
    text = re.sub(r"^budget: <[^\n]*$", "budget: <one hard number>", text, flags=re.M)
    keep_budget = re.search(r"^budget: <[^\n]*$", text, re.M)
    text = re.sub(r"<[^<>\n]+>", "x", text)
    text = re.sub(r"^- S1 .*$", "- S1 the surface", text, flags=re.M)
    if keep_budget:                      # restore the SLOT exactly as shipped
        text = re.sub(r"^budget: .*$", "budget: <one hard number>", text, flags=re.M)
    p.write_text(text, encoding="utf-8")
    node, note = add.freeze(root, cid, by="t", authority="process")
    assert node is None, "an explore froze with its budget slot unfilled"
    assert "budget" in note.lower(), \
        f"refused, but not for the budget — the check proves nothing about E2: {note}"
