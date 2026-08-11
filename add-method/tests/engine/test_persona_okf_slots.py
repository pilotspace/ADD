"""Red suite for `okf-persona-template` — the Persona scaffold gets its routing slots.

The persona contract (persona-author/references/contract.md) calls `vibe`/`flow`/
`task-kinds` routing-critical and `use-when`/`not-when` the selection boundary — yet
`new()` scaffolded a slot for none of them but `use-when`. The engine's own recorded scar
(the `gives:` lesson in `new()`) names the failure mode: an instruction with no slot to
fill is an instruction that does not happen.

OKF (Open Knowledge Format v0.2 — GoogleCloudPlatform/knowledge-catalog) recommends
`description:` and defines provenance under the plural `sources:` key; ADD's trust layer
(`type:`, `generated:`, `verified:` events, `human:<id>` actors, reserved index/log) is
already OKF-shaped, so the scaffold adopts those two keys verbatim. OKF's doc-status
lifecycle (`status: draft|stable|deprecated`) stays OUT by decision — `status:` is ADD's
task-lifecycle key, and a Persona carries none (test_persona_scaffold.py).

Driven as dogfood task `.add/tasks/okf-persona-template.md` (v3.0.0 hardening tally #2).
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

ROUTING_KEYS = ("vibe", "flow", "task-kinds", "use-when", "not-when")


def _fm(text: str) -> str:
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    return m.group(1) if m else ""


def _scaffold(tmp_path, slug="backend-systems", **fields) -> str:
    add.init(tmp_path, "code", "T")
    cid, _ = add.new(tmp_path, "Persona", slug, **fields)
    return _fm((tmp_path / cid.lstrip("/")).read_text(encoding="utf-8"))


def test_scaffold_offers_every_routing_slot(tmp_path):
    """covers: M1 — the contract's routing keys each get a slot to fill."""
    fm = _scaffold(tmp_path, title="backend lens")
    for key in ROUTING_KEYS:
        assert re.search(rf"^{re.escape(key)}:", fm, re.M), \
            f"the Persona scaffold offers no `{key}:` slot — a slot-less instruction does not happen"


def test_scaffold_offers_okf_description_and_sources(tmp_path):
    """covers: M2 — OKF-recommended `description:` and plural provenance `sources:`."""
    fm = _scaffold(tmp_path, title="backend lens")
    assert re.search(r"^description:", fm, re.M), "OKF-recommended `description:` is not scaffolded"
    assert re.search(r"^sources:", fm, re.M), \
        "provenance is not scaffolded — OKF names the family `sources:` (plural)"
    assert not re.search(r"^source:", fm, re.M), "the singular `source:` would shadow OKF's key"


def test_caller_values_survive_the_scaffold(tmp_path):
    """covers: M1,E1 · R:CLOBBER — supplied fields verbatim, missing ones placeholdered."""
    fm = _scaffold(tmp_path, title="security lens", vibe="no unaudited crypto ships",
                   flow="verify", **{"use-when": "auth or crypto in scope"})
    assert re.search(r"^vibe: no unaudited crypto ships$", fm, re.M), "caller `vibe` clobbered"
    assert re.search(r"^flow: verify$", fm, re.M), "caller `flow` clobbered"
    assert re.search(r"^use-when: auth or crypto in scope$", fm, re.M), "caller `use-when` clobbered"
    assert re.search(r"^task-kinds: <", fm, re.M), "unsupplied `task-kinds` got no placeholder"


def test_no_okf_doc_status_key(tmp_path):
    """covers: A2 (probe) — OKF doc-status stays out; `status:` is ADD's task-lifecycle key."""
    fm = _scaffold(tmp_path, title="ux lens")
    assert not re.search(r"^status:", fm, re.M), \
        "the scaffold grew a `status:` key — OKF doc-status collides with ADD task-lifecycle"


def test_slots_are_placeholders_not_validation(tmp_path):
    """covers: M3 — the engine is a notary: a garbage `flow:` is recorded, never refused."""
    fm = _scaffold(tmp_path, title="odd lens", flow="not-a-real-flow")
    assert re.search(r"^flow: not-a-real-flow$", fm, re.M), \
        "`new` judged a slot's content — scaffolding grew into a linter"
