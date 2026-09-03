"""e16 · test IDs carry their file — a failing check cannot be recorded as passed.

The red suite for `repair-evidence-ids`. Every check here must fail for the RIGHT reason
before BUILD: not because a name is missing, but because the engine records the wrong value.

Two defects of one class are under test:
  F7  two tests sharing a bare name collide, and the last parsed wins — so a FAILURE
      disappears from the evidence.
  F12 a `<skipped/>` case falls through to the pass branch — so a rule is proven by a
      test that never ran.

Both live in `extract_ids`, both are silent, and both entitle a gate.
"""
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tooling"))
import add  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]


def _junit(tmp_path, cases) -> Path:
    """`cases` is a list of `(classname, name, outcome)` with outcome in pass|fail|skip."""
    body = []
    for classname, name, outcome in cases:
        inner = {"pass": "", "fail": '<failure message="boom"/>', "skip": '<skipped message="no"/>'}[outcome]
        body.append(f'<testcase classname="{classname}" name="{name}">{inner}</testcase>')
    path = tmp_path / "j.xml"
    path.write_text(f'<testsuite tests="{len(cases)}">{"".join(body)}</testsuite>', encoding="utf-8")
    return path


def _node(tmp_path, covers_line: str, rules: str = "- M1 the thing holds") -> dict:
    """A minimal Task node on disk, with a RULES and a CHECKS section."""
    path = tmp_path / "t1.md"
    path.write_text(
        "---\ntype: Task\ntitle: t1\nstatus: build\ndepth: standard\n---\n"
        f"## RULES\n<must>\n{rules}\n</must>\n\n"
        f"## CHECKS\n{covers_line}\n",
        encoding="utf-8",
    )
    return {"path": path}


# ---------------------------------------------------------------- M1 · one name, one test

def test_two_tests_one_name_are_two_ids(tmp_path):
    """covers: M1 · junit's classname distinguishes two same-named tests in different files."""
    j = _junit(tmp_path, [("tests.engine.test_a", "test_same", "fail"),
                          ("tests.engine.test_b", "test_same", "pass")])
    ids = add.extract_ids(j)
    assert len(ids) == 2, f"one bare name overwrote the other: {ids}"
    assert ids["tests.engine.test_a::test_same"] == "fail"
    assert ids["tests.engine.test_b::test_same"] == "pass"


def test_a_masked_failure_is_recorded(tmp_path):
    """covers: M2, R:MASK · F7's exact demonstration — the failure must survive extraction."""
    j = _junit(tmp_path, [("tests.engine.test_a", "test_same", "fail"),
                          ("tests.engine.test_b", "test_same", "pass")])
    outcomes = set(add.extract_ids(j).values())
    assert "fail" in outcomes, "the failing run disappeared from the evidence"


def test_ambiguous_citation_proves_nothing(tmp_path):
    """covers: M1, R:MASK · a bare citation matching two IDs resolves to ambiguous, never pass."""
    reported = {"tests.engine.test_a::test_same": "fail",
                "tests.engine.test_b::test_same": "pass"}
    assert add.resolve_check("test_same", reported) == "ambiguous"


# ---------------------------------------------------------------- M3 · one grammar, two call sites

def test_checks_of_keys_by_file_too():
    """covers: M3 · e14's extractor carries the same defect, and loses a real test to it."""
    # DISCOVERED, not named. This pinned `test_sync_is_idempotent` — a real collision at the
    # time — and went red the day one of the two was deleted for an unrelated reason, reporting
    # a keying defect that did not exist. The property is "a bare name appearing in two files
    # yields two keys"; the suite is asked which name that is.
    import collections
    suite = sorted((ROOT / "tests").rglob("test_*.py"))
    keyed = add.checks_of(suite)
    bare = collections.Counter(k.rpartition("::")[2] for k in keyed)
    dupes = [name for name, n in bare.items() if n > 1]
    assert dupes, "no test name appears in two files — this guard cannot prove anything today"
    for name in dupes:
        keys = [k for k in keyed if k.endswith(f"::{name}")]
        assert len(keys) == bare[name], f"checks_of collapsed a real collision: {keys}"


def test_one_id_grammar(tmp_path):
    """covers: M3, R:DRIFT · both call sites form an ID through the same function."""
    assert add.qualify("tests.engine.test_a", "test_x") == "tests.engine.test_a::test_x"
    assert add.qualify("tests/engine/test_a.py", "test_x") == "tests.engine.test_a::test_x"


# ---------------------------------------------------------------- M4/M5 · the reader, not a sweep

def test_bare_citation_still_binds(tmp_path):
    """covers: M4, M5 · an old bare-name receipt keeps binding through the exact-hit arm."""
    assert add.resolve_check("test_ok", {"test_ok": "pass"}) == "pass"
    assert add.resolve_check("test_ok", {"tests.engine.test_a::test_ok": "pass"}) == "pass"
    assert add.resolve_check("test_gone", {"tests.engine.test_a::test_ok": "pass"}) == "absent"


@pytest.mark.skip(reason="dogfood: reads add-skill's own dev node .add/tasks/repair-evidence-ids.md; not present in a fresh bundle")
def test_migration_decision_is_recorded():
    """covers: M4 · the node carries the reason, not just the outcome."""
    node = (ROOT / ".add" / "tasks" / "repair-evidence-ids.md").read_text(encoding="utf-8")
    assert "## DECISION" in node, "the migration outcome was taken without a recorded reason"
    assert "Why not the alternatives" in node


def test_no_gated_citation_rewritten():
    """covers: M5, R:SWEEP · gated M0 nodes keep their citations byte-identical."""
    out = subprocess.run(["git", "diff", "--name-only", "HEAD", "--", ".add/tasks"],
                         cwd=ROOT, capture_output=True, text=True, timeout=30)
    touched = {Path(p).stem for p in out.stdout.split()}
    gated_m0 = {"define-entity-model", "define-task-schema", "define-authority-rules",
                "define-read-protocol", "define-log-rotation", "align-standards-citations",
                "define-scale-rules", "define-compat-contract", "define-evidence-binding"}
    assert not (touched & gated_m0), f"a gated M0 node was edited: {sorted(touched & gated_m0)}"


# ---------------------------------------------------------------- M6 · a skip is not a pass

def test_a_skipped_test_is_not_a_pass(tmp_path):
    """covers: M6, R:PHANTOM · F12's demonstration — `<skipped/>` must not read as pass."""
    j = _junit(tmp_path, [("tests.engine.test_a", "test_one", "skip"),
                          ("tests.engine.test_a", "test_two", "pass")])
    ids = add.extract_ids(j)
    assert ids["tests.engine.test_a::test_one"] == "skip", \
        "a test that never ran was recorded as passing"
    assert ids["tests.engine.test_a::test_two"] == "pass"


def test_a_skip_proves_no_rule(tmp_path):
    """covers: M6, R:PHANTOM · bind refuses to prove a rule from a skipped check."""
    node = _node(tmp_path, "- test_ok · covers: M1 · proves it")
    proven, unproven = add.bind(node, {"tests.engine.test_a::test_ok": "skip"})
    assert "M1" not in proven, "a Must was proven by a test that never ran"
    assert "M1" in unproven
