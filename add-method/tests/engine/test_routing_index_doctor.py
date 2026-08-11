"""Red suite for `routing-index-freshness` (beta-2, W4) — a stale index misroutes silently.

The routing index (`personas-index/use-when.md`) is how a lens is FOUND: the corpus says what
each persona is, the index says when to reach for it. Both are vendored into every bundle —
and nothing checked that they still agree. A teacher refresh, a hand-pruned corpus, or a
deleted index file leaves `advise`/`wave` routing against a roster that no longer exists,
with no finding anywhere. Doctor gets the check (blog docket item 6's remaining sliver):

  * corpus present + index absent  → warn `routing_index_missing`
  * corpus and index disagree on the persona count → warn `routing_index_stale`
  * no corpus → silence (nothing to route), and non-persona corpus files (README, VENDOR,
    LICENSE — anything without a `description:`) are not counted, mirroring the generator's
    own definition of "persona".
"""

import shutil
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402


@pytest.fixture
def bundle(tmp_path):
    add.init(tmp_path, "code", "Routed")
    return tmp_path


def _routing_findings(root):
    return [f for f in add.doctor(root) if f["code"].startswith("routing_index")]


def test_a_freshly_vendored_bundle_is_clean(bundle):
    """covers: M1 — init vendors corpus and index together; doctor must agree they match."""
    assert _routing_findings(bundle) == []


def test_a_missing_index_is_reported(bundle):
    """covers: M2 — personas without routing is a corpus nobody can reach for."""
    shutil.rmtree(bundle / "personas-index")
    findings = _routing_findings(bundle)
    assert [f["code"] for f in findings] == ["routing_index_missing"], findings
    assert findings[0]["severity"] == "warn"


def test_a_stale_index_is_reported_with_both_counts(bundle):
    """covers: M3 — the corpus moved without the index; the finding names the drift."""
    extra = bundle / "personas-teacher" / "engineering" / "zz-new-lens.md"
    extra.write_text("---\ndescription: Expert in something the index never heard of\n---\n")
    findings = _routing_findings(bundle)
    assert [f["code"] for f in findings] == ["routing_index_stale"], findings
    assert "build_persona_index" in findings[0]["detail"], \
        f"the finding must say how to fix it: {findings[0]['detail']}"


def test_a_bundle_without_a_corpus_is_silent(bundle):
    """covers: E1 — no corpus, nothing to route, nothing to find."""
    shutil.rmtree(bundle / "personas-teacher")
    assert _routing_findings(bundle) == []


def test_non_persona_corpus_files_are_not_counted(bundle):
    """covers: E2 — a README carries no `description:`; the generator skips it, so must doctor."""
    (bundle / "personas-teacher" / "NOTES.md").write_text("no frontmatter here\n")
    assert _routing_findings(bundle) == []
