"""Red suite for `brief-names-the-candidate-lens` — an unlensed brief names who could fit.

`brief` emits `<persona>` only when the node ALREADY carries `persona:`/`advised_by:`. The only
verb that stamps one is `add advise`, and no next-hint on the normal path names it — the todo row
refuses a second verb by design (A12). So the lens could only reach a node by an act nothing in
the loop ever asked for, and 175 of this bundle's 190 lifecycle nodes carry none.

This closes the circle at the one surface that is already the agent's instructions. The engine
PRESENTS the fitting set; it selects nothing — `personas.md`'s NO-EXEC floor is the point, not an
obstacle to route around.
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

# The roster's own beat→`flow:` mapping, as `agents/add-worker.md` §2 states it.
SURFACE = {"direction": "design", "build": "build", "verify": "verify"}

PERSONA = """---
type: Persona
title: {title}
vibe: a one-line stance
flow: {flow}
task-kinds: {kinds}
use-when: the boundary that routes this one
not-when: the near miss that belongs to a sibling
description: a lens
sources:
  - none
generated: {{ by: add/3.6.0, at: 2026-09-10 }}
verified: []
---
## Identity
A lens with earned perspective.

## Critical Rules
- **NEVER_IN_A_BRIEF** — this clause is the body-leak tripwire; a brief must never carry it
"""


def seed(root, slug, *, flow, kinds, title="A lens"):
    (Path(root) / "personas").mkdir(exist_ok=True)
    (Path(root) / "personas" / f"{slug}.md").write_text(
        PERSONA.format(title=title, flow=flow, kinds=kinds))
    return slug


def task(root, slug, *, kind=None, depth="standard"):
    kwargs = {"title": f"Task {slug}", "depth": depth}
    if kind:
        kwargs["kind"] = kind
    cid, _ = add.new(root, "Task", slug, **kwargs)
    return cid


@pytest.fixture
def bundle(tmp_path):
    add.init(tmp_path, "code", "Cand")
    # `init` seeds a starting roster; clear it so each check states its own.
    for f in (tmp_path / "personas").glob("*.md"):
        f.unlink()
    return tmp_path


def _text(root, cid, phase=None):
    return add.brief(root, cid, phase=phase)["text"]


def test_an_unlensed_node_is_offered_the_fitting_roster(bundle):
    """covers: M1, A1, A4 — the fitting entries, and the verb that records a pick."""
    seed(bundle, "fits", flow="design, advisor", kinds="docs, refactor")
    seed(bundle, "wrong-flow", flow="build", kinds="docs, refactor")
    seed(bundle, "wrong-kind", flow="design", kinds="security")
    cid = task(bundle, "unlensed", kind="docs")
    out = _text(bundle, cid, phase="direction")

    assert "fits" in out, f"the fitting roster entry was never offered:\n{out}"
    assert "wrong-flow" not in out, f"an entry whose `flow:` misses this beat was offered:\n{out}"
    assert "wrong-kind" not in out, f"an entry whose `task-kinds:` misses `kind:` was offered:\n{out}"
    assert "add advise" in out, \
        f"the candidates were named with no verb that records a pick:\n{out}"

    # A4 — `kind:` is OPTIONAL on a Task. Gating the whole feature on a field most nodes never
    # set would leave it dark for most of this bundle, so `flow:` alone decides when it is absent.
    nokind = task(bundle, "no-kind-declared")
    assert "fits" in _text(bundle, nokind, phase="direction"), \
        "a node that declared no `kind:` was shown an empty roster"


def test_the_engine_names_no_choice(bundle):
    """covers: M2, R:ENGINEPICKS, A5 — sorted by slug, and nothing marks one as the pick."""
    for slug in ("zeta", "alpha", "mike"):
        seed(bundle, slug, flow="design", kinds="docs")
    out = _text(bundle, task(bundle, "choose", kind="docs"), phase="direction")

    seen = [s for s in ("alpha", "mike", "zeta") if s in out]
    assert seen == ["alpha", "mike", "zeta"], f"A5 — not sorted by slug: {seen}\n{out}"
    assert out.index("alpha") < out.index("mike") < out.index("zeta"), out
    for word in ("recommend", "best", "preferred", "chosen", "selected"):
        assert word not in out.lower(), (
            f"R:ENGINEPICKS — the brief calls a candidate {word!r}. The engine emits the fitting "
            f"set and stops; ranking is the orchestrating agent's judgment.")


def test_the_keys_are_the_rosters_own(bundle):
    """covers: M3 — direction→design · build→build · verify→verify, advisor as verify's fallback."""
    for beat, flow in SURFACE.items():
        seed(bundle, f"lens-{beat}", flow=flow, kinds="docs")
    for beat in SURFACE:
        out = _text(bundle, task(bundle, f"node-{beat}", kind="docs"), phase=beat)
        assert f"lens-{beat}" in out, f"beat {beat} did not draw its own surface's lens:\n{out}"
        for other in SURFACE:
            if other != beat:
                assert f"lens-{other}" not in out, \
                    f"beat {beat} drew {other}'s lens — the mapping is not the roster's:\n{out}"

    # verify falls back to `advisor` when nothing declares verify — `add-worker.md` §2's own rule.
    (bundle / "personas" / "lens-verify.md").unlink()
    seed(bundle, "second-mind", flow="advisor", kinds="docs")
    out = _text(bundle, task(bundle, "fallback", kind="docs"), phase="verify")
    assert "second-mind" in out, f"verify did not fall back to an advisor lens:\n{out}"


def test_a_lensed_or_roster_less_node_is_unchanged(bundle):
    """covers: M4, A2 — the addition speaks only where it has something to say."""
    empty = task(bundle, "no-roster", kind="docs")
    before = _text(bundle, empty, phase="direction")
    assert "<persona ref=\"none\"" in before, before
    assert "add advise" not in before, (
        "M4 — a bundle whose roster has no fitting entry was told to advise anyway. With nothing "
        "to offer, the brief must be what it already was, byte for byte.")

    seed(bundle, "fits", flow="design", kinds="docs")
    lensed = task(bundle, "already-lensed", kind="docs")
    add.advise(bundle, lensed, "fits")
    out = _text(bundle, lensed, phase="direction")
    assert 'ref="none"' not in out, f"A2 — a node that already names a lens got a candidate list:\n{out}"


def test_no_persona_body_reaches_the_brief(bundle):
    """covers: M5, R:BODYLEAK, A6, R:SILENTGROWTH — frontmatter only, and inside the budget."""
    for i in range(6):
        seed(bundle, f"lens-{i}", flow="design", kinds="docs")
    cid = task(bundle, "budgeted", kind="docs", depth="quick")
    result = add.brief(bundle, cid, phase="direction")

    assert "NEVER_IN_A_BRIEF" not in result["text"], \
        "R:BODYLEAK — a candidate's `## Critical Rules` reached the brief"
    assert "## Identity" not in result["text"], "R:BODYLEAK — a candidate's body section reached the brief"
    assert result["bytes"] <= result["budget"] or result["degraded"], (
        f"R:SILENTGROWTH — the candidate list pushed the brief to {result['bytes']}B over a "
        f"{result['budget']}B budget with nothing recorded as degraded")
