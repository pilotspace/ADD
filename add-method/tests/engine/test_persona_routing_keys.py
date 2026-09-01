"""A routing key outside its closed taxonomy is a finding, never a silence.

Red-first for `/tasks/persona-routing-keys-checked.md`. The `covers:` citations live in each
test's docstring.

Measured 2026-09-01: `grep -n task-kinds tooling/add.py` found the key only in the scaffold
writer, never in a validator, and `references/contract.md:52-53` admitted outright that any
other value "is a typo that no surface loads — and NOTHING warns". ADD's own two personas
carried five of six `task-kinds:` values outside the taxonomy, so by the method's own
contract both of them routed nothing.
"""

import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

LIVE = REPO.parent / ".add"
CONTRACT = REPO / "skill" / "add" / "persona-author" / "references" / "contract.md"
PERSONAS_MD = REPO / "skill" / "add" / "personas.md"


@pytest.fixture
def bundle(tmp_path):
    root = tmp_path / ".add"
    add.init(root, profile="code", title="routing fixture")
    return root


def _persona(root, slug, **keys):
    root.joinpath("personas").mkdir(parents=True, exist_ok=True)
    fm = "\n".join(f"{k}: {v}" for k, v in keys.items())
    root.joinpath("personas", f"{slug}.md").write_text(
        f"---\ntype: Persona\ntitle: {slug}\n{fm}\n---\n## Identity\na lens.\n")


def _findings(root, code):
    return [f for f in add.doctor(root) if f.get("code") == code]


def test_doctor_reports_an_out_of_taxonomy_flow(bundle):
    """covers: M1, R:SILENTMISROUTE · the finding names node, key and value."""
    _persona(bundle, "bad-flow", flow="planning", **{"task-kinds": "feature"})
    hits = _findings(bundle, "persona_routing_key")
    assert hits, "an out-of-taxonomy `flow:` produced no finding"
    msg = " ".join(h["detail"] for h in hits)
    assert "bad-flow" in msg and "flow" in msg and "planning" in msg


def test_doctor_reports_an_out_of_taxonomy_task_kind(bundle):
    """covers: M1, E2 · only the offending value is named."""
    _persona(bundle, "bad-kind", flow="build", **{"task-kinds": "feature, engine, data"})
    msg = " ".join(h["detail"] for h in _findings(bundle, "persona_routing_key"))
    assert "engine" in msg
    assert "feature" not in msg.split("engine")[0].split("bad-kind")[-1]


def test_the_check_enumerates_the_taxonomy_from_source(bundle):
    """covers: M2 · no copied list — the constants are the single source."""
    assert isinstance(add.PERSONA_FLOWS, tuple) and add.PERSONA_FLOWS
    assert isinstance(add.PERSONA_TASK_KINDS, tuple) and add.PERSONA_TASK_KINDS
    _persona(bundle, "ok", flow=add.PERSONA_FLOWS[0], **{"task-kinds": add.PERSONA_TASK_KINDS[0]})
    assert not _findings(bundle, "persona_routing_key")


def test_explore_is_in_the_task_kind_taxonomy():
    """covers: M3, E5 · engine and every stating file agree."""
    assert "explore" in add.PERSONA_TASK_KINDS
    # The claim WRAPS across lines, so a line-anchored search reads green while the value is
    # missing — the same one-line-read trap `test_profile_refusal` records. Flatten first.
    flat = " ".join(CONTRACT.read_text(encoding="utf-8").split())
    stated = re.search(r"feature · refactor .*? explore`", flat)
    assert stated, "the stated task-kind taxonomy omits `explore`"
    for value in add.PERSONA_TASK_KINDS:
        assert value in stated.group(0), f"the stated taxonomy omits `{value}`"


def test_the_finding_never_gates(bundle):
    """covers: M4 · the finding is informational; `doctor` stays a reporter."""
    _persona(bundle, "bad-flow", flow="planning")
    assert all(h["severity"] == "info" for h in _findings(bundle, "persona_routing_key"))


def test_this_bundles_personas_pass():
    """covers: M5, A4 · ADD's own roster is in taxonomy."""
    if not LIVE.is_dir():
        pytest.skip("the live bundle is not present in this checkout")
    assert not _findings(LIVE, "persona_routing_key")


def test_a_persona_with_no_routing_keys_is_silent(bundle):
    """covers: A2, E1, E4 · absence is not an offence."""
    _persona(bundle, "keyless")
    assert not _findings(bundle, "persona_routing_key")


def test_a_non_persona_node_is_not_checked(bundle):
    """covers: A1, E3 · scope holds — a Task carrying a stray `flow:` is not reported."""
    add.new(bundle, "Task", "stray")
    p = bundle / "tasks" / "stray.md"
    p.write_text(p.read_text().replace("type: Task", "type: Task\nflow: nonsense", 1))
    assert not _findings(bundle, "persona_routing_key")


def test_findings_are_ordered_and_one_per_offence(bundle):
    """covers: A3 · the report is stable and diffable."""
    _persona(bundle, "zeta", flow="nope")
    _persona(bundle, "alpha", flow="nope")
    hits = _findings(bundle, "persona_routing_key")
    assert len(hits) == 2
    assert [h["detail"] for h in hits] == sorted(h["detail"] for h in hits)


def test_the_finding_prints_the_allowed_values(bundle):
    """covers: A4 · the reader is told what is right, not only that they are wrong."""
    _persona(bundle, "bad-flow", flow="planning")
    msg = _findings(bundle, "persona_routing_key")[0]["detail"]
    assert all(v in msg for v in add.PERSONA_FLOWS)
