"""A task kind that routes to no lens takes the generic fallback, silently.

3.4's `init` seeds a starting roster because the selector — which searches `flow:` then
`task-kinds:` — had nothing to search, and not one of the 232 teacher files carries either key.
Four templates were seeded. `PERSONA_TASK_KINDS` has eleven entries.

Measured 2026-09-03:

    build-craftsman     feature, refactor, test, integration, infra
    task-planner        feature, refactor, integration
    milestone-planner   feature, integration, infra
    release-planner     release, infra
    ----------------------------------------------------------------
    unclaimed           docs, ui, data, security, explore

`security` mattered most: the gate REFUSES a security PASS without a named lens (R:NOCOVERAGE),
so a fresh install dead-ended on its first security task with nothing seeded that could clear it.
This branch hit that refusal live, authored a lens into THIS repo's bundle to clear it — and
never seeded it, so the fix did not ship. The seeded template is the artifact.

When a rule quantifies over a set, its check must ENUMERATE that set from the source.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

TMPL_DIR = REPO / "tooling" / "templates" / "personas"


def _lenses():
    """{slug: frontmatter dict} for every seeded template — read from disk, never a hand list."""
    out = {}
    for t in sorted(TMPL_DIR.glob("*.md.tmpl")):
        head = t.read_text(encoding="utf-8").split("---")[1]
        out[t.name[: -len(".md.tmpl")]] = {
            k.strip(): v.strip()
            for k, _, v in (l.partition(":") for l in head.splitlines() if ":" in l)}
    return out


def _values(fm, key):
    return [v.strip() for v in fm.get(key, "").replace(",", " ").split() if v.strip()]


# ------------------------------------------------------------------ M1/M2 · the coverage

def test_every_task_kind_routes_to_a_seeded_lens():
    """covers: M1, A2, A4, R:DEADTIER — the measured 6-of-11.

    A4/A6: the absence is a FAILING TEST, not a doctor nudge, and the failure names the
    unclaimed kind so the maintainer is not sent reading nine files.
    """
    claimed = {k for fm in _lenses().values() for k in _values(fm, "task-kinds")}
    unclaimed = sorted(set(add.PERSONA_TASK_KINDS) - claimed)
    assert not unclaimed, (
        f"{len(unclaimed)} task kind(s) route to no seeded lens: {', '.join(unclaimed)} — a task "
        f"of that kind takes the generic fallback and the receipt records no expert")


def test_the_guard_enumerates_the_taxonomy():
    """covers: M2, A4 — the next kind added to the constant must fail the check above.

    A hand-written list of eleven strings would pass forever after the twelfth is added, which
    is precisely how the roster fell five behind in the first place.
    """
    src = Path(__file__).read_text(encoding="utf-8")
    assert "add.PERSONA_TASK_KINDS" in src, \
        "the coverage check does not read the constant — it cannot notice a new kind"
    claimed = {k for fm in _lenses().values() for k in _values(fm, "task-kinds")}
    assert not (claimed - set(add.PERSONA_TASK_KINDS)), \
        f"a lens claims a kind outside the taxonomy: {sorted(claimed - set(add.PERSONA_TASK_KINDS))}"


# ------------------------------------------------------------------ M3/M4 · what a lens must carry

def test_every_seeded_lens_declares_only_closed_taxonomy_values():
    """covers: M3, E2 — a lens `doctor` would file a routing finding against is not seeded."""
    for slug, fm in _lenses().items():
        for key, allowed in (("task-kinds", add.PERSONA_TASK_KINDS), ("flow", add.PERSONA_FLOWS)):
            bad = [v for v in _values(fm, key) if v not in allowed]
            assert not bad, f"{slug} declares {key}: {bad} outside the closed taxonomy"


def test_every_seeded_lens_names_its_source():
    """covers: M4, A3, A6, R:UNSOURCED — expertise with material behind it, and a stated near-miss.

    An invented lens produces confident prose with nothing behind it, which is WORSE than an
    absent one because it is trusted. A lens with no `not-when:` cannot be told from its siblings.
    """
    for slug, fm in _lenses().items():
        assert re.search(r"personas-teacher/\S+\.md", fm.get("source", "")), \
            f"{slug} claims expertise with no teacher file behind it: {fm.get('source')!r}"
        for key in ("vibe", "use-when", "not-when", "flow", "task-kinds"):
            assert fm.get(key), f"{slug} is missing `{key}:`, which the selector or the reader needs"


# ------------------------------------------------------------------ counter-guards

def test_overlapping_claims_are_legitimate():
    """covers: A5, E1 — two lenses may claim one kind; narrowing that would be a second decision.

    `test` is claimed by build-craftsman and security-reviewer, and both readings are right.
    """
    counts = {}
    for fm in _lenses().values():
        for k in _values(fm, "task-kinds"):
            counts[k] = counts.get(k, 0) + 1
    assert any(c > 1 for c in counts.values()), \
        "no kind is claimed twice — the fixture no longer exercises the overlap it guards"


def test_init_seeds_them_all_and_overwrites_none(tmp_path):
    """covers: M5, A1 — the roster is the project's from the moment it lands."""
    add.init(tmp_path, "code", "T")
    landed = {p.name[:-3] for p in (tmp_path / "personas").glob("*.md")}
    assert set(_lenses()) <= landed, f"not every template was seeded: {set(_lenses()) - landed}"

    edited = tmp_path / "personas" / "security-reviewer.md"
    edited.write_text("---\ntype: Persona\ntitle: mine\n---\n## Identity\nmine\n", encoding="utf-8")
    add.init(tmp_path, "code", "T")
    assert "mine" in edited.read_text(encoding="utf-8"), "a re-init clobbered an edited lens"
