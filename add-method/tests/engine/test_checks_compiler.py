"""Red suite for e14 `compile-checks-from-suite` — the CHECKS section, compiled.

F2 measured this project's own defect: 61 cited test names that were never written, across nine
gated M0 tasks, and nobody noticed because a plausible test name reads exactly like a real one.
The fix is not more care at authoring time — e13 opened with 12 authored checks and its suite
finished at 25, every addition discovered DURING the build. The knowledge does not exist when the
section is written. So the section must be extracted, not authored (L7).

Two carriers, because this repo already has two: docstrings (mine) and `# --- name · covers: … ---`
headers (e15's subagent). A rule written against one author's habit is broken by the next author
without anyone intending to.
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402


def _at(found, name):
    """One entry from `checks_of`, looked up by its bare test name.

    Since e16 `checks_of` keys by `module::name` (M1/M3) so two same-named tests in different
    files cannot collapse — this repo lost one that way. A citation is still written bare (M5),
    so a bare lookup resolves through the production grammar rather than by key equality.
    """
    hits = add.cite_hits(name, found)
    assert len(hits) == 1, f"{name!r} resolved to {len(hits)} ids: {hits}"
    return found[hits[0]]


SUITE_DOCSTRING = '''"""A suite carrying covers: in docstrings."""


def test_alpha():
    """covers: M1 — the first rule is enforced here."""


def test_beta():
    """covers: M2, R:BAD — the second rule and the reject."""


def test_unlabelled():
    """No covers: anywhere. A gap, not a free pass."""
'''

SUITE_HEADER = '''"""A suite carrying covers: in comment headers, as e15's subagent wrote them."""


# --- test_gamma · covers: M3 --------------------------------------------------


def test_gamma():
    """Proves the third rule."""
'''

NODE_BODY = """## CARD
goal: a node whose CHECKS should be compiled
beat: build · next: add run

## RULES
<must>
- M1 the first rule
- M2 the second rule
- M3 the third rule
</must>
<reject>
- R:BAD something forbidden -> "BAD"
</reject>

## CHECKS
- test_invented · covers: M1 · a name that exists in no suite
red-first: every check MUST fail first.

## EVIDENCE
receipt: pending
"""


@pytest.fixture
def bundle(tmp_path):
    add.init(tmp_path, "code", "Compiling")
    cid, _ = add.new(tmp_path, "Task", "subject", title="Subject", depth="standard")
    path = tmp_path / cid.lstrip("/")
    n = add.read(path, "T2")
    add.write(path, f"---\n{n['raw']}\n---\n{NODE_BODY}")
    suite = tmp_path / "suite"
    suite.mkdir()
    (suite / "test_docstring.py").write_text(SUITE_DOCSTRING)
    (suite / "test_header.py").write_text(SUITE_HEADER)
    return tmp_path


CID = "/tasks/subject.md"


def _suite(bundle):
    return sorted((bundle / "suite").glob("test_*.py"))


# ---------------------------------------------------------- extraction (M1, M3, R:GUESS)


def test_checks_extracted_from_docstrings(bundle):
    """covers: M1 — the citation is read from the test, not from the node."""
    found = add.checks_of(_suite(bundle))
    assert _at(found, "test_alpha")[0] == ["M1"]
    assert _at(found, "test_beta")[0] == ["M2", "R:BAD"]


def test_checks_extracted_from_comment_headers(bundle):
    """covers: M1 — e15's carrier, discovered before this was built rather than after.

    A subagent wrote `# --- test_gamma · covers: M3 ---` above the function instead of a
    docstring. One task was enough for the convention to diverge.
    """
    assert _at(add.checks_of(_suite(bundle)), "test_gamma")[0] == ["M3"]


def test_unlabelled_test_is_reported(bundle):
    """covers: M3, R:GUESS — an unlabelled test is a visible gap, never an inferred label."""
    found = add.checks_of(_suite(bundle))
    assert _at(found, "test_unlabelled")[0] == [], f"a rule was invented for an unlabelled test: {found}"
    assert "test_unlabelled" in add.unlabelled(_suite(bundle))


def test_no_rule_inferred_from_a_name(bundle):
    """covers: M3, R:GUESS — `test_m1_something` must not be read as covering M1."""
    (bundle / "suite" / "test_naming.py").write_text(
        '"""s"""\n\n\ndef test_m1_the_first_rule():\n    """No covers: line at all."""\n')
    assert _at(add.checks_of(_suite(bundle)), "test_m1_the_first_rule")[0] == []


# ------------------------------------------------------------------ verify (M2)


def test_verify_catches_fictional_citation(bundle):
    """covers: M2 — F2's first shape: a CHECKS line naming a test that exists nowhere."""
    findings = add.checks_verify(bundle, CID, _suite(bundle))
    assert any("test_invented" in str(f) for f in findings), findings


def test_verify_catches_unresolvable_referent(bundle):
    """covers: M2 — F2's second shape, which the M0 validator accepted.

    `define-scale-rules` cites `G1`/`G2`/`G3` and declares no rules at all. A citation to a rule
    the node never states is as empty as a citation to a test that was never written.
    """
    path = bundle / CID.lstrip("/")
    n = add.read(path, "T2")
    add.write(path, f"---\n{n['raw']}\n---\n" + n["body"].replace(
        "- test_invented · covers: M1 ·", "- test_alpha · covers: G7 ·"))
    findings = add.checks_verify(bundle, CID, _suite(bundle))
    assert any("G7" in str(f) for f in findings), findings


def test_pending_citation_is_not_a_defect(bundle):
    """covers: M2 — a test not yet written on a node not yet gated is not a finding.

    Run on the live bundle, `checks_verify` reported 13 nodes. Nine were F2's gated M0 tasks — real
    defects. Four were M1 tasks still in `direction`, citing tests that do not exist yet because
    the task has not been built. That is the normal, correct state of a planned task. A report
    that grades those the same as a false claim on a gated node will be ignored, and then it
    protects nothing.
    """
    findings = add.checks_verify(bundle, CID, _suite(bundle))
    assert findings, "the fictional citation should still be reported"
    assert all(f.get("severity") == "pending" for f in findings), \
        f"an ungated node's unwritten test was graded as a defect: {findings}"


def test_gated_citation_is_a_defect(bundle):
    """covers: M2 — once a gate is taken against the claim, the same gap is an error."""
    path = bundle / CID.lstrip("/")
    n = add.read(path, "T2")
    add.write(path, f"---\n{add.append_item(n['raw'], 'verified', '{ by: \"human:t\", at: 2026-07-30, act: gate, authority: human, outcome: PASS }')}\n---\n{n['body']}")
    findings = add.checks_verify(bundle, CID, _suite(bundle))
    assert any(f["severity"] == "error" for f in findings), findings


def test_unresolvable_referent_is_always_an_error(bundle):
    """covers: M2 — a rule the node never declares is wrong whatever its status.

    Unlike a missing test, this cannot become true later: `covers: G7` on a node with no G7 is a
    claim about the node's own contents, and the node is right there.
    """
    path = bundle / CID.lstrip("/")
    n = add.read(path, "T2")
    add.write(path, f"---\n{n['raw']}\n---\n" + n["body"].replace(
        "- test_invented · covers: M1 ·", "- test_alpha · covers: G7 ·"))
    findings = add.checks_verify(bundle, CID, _suite(bundle))
    assert any(f["severity"] == "error" and "G7" in f["message"] for f in findings), findings


def test_a_test_inside_a_string_literal_is_not_a_test(bundle):
    """covers: M1, R:GUESS — a regex over source text reads code out of quoted strings.

    Found by running `checks_sync` on THIS task's own node: the compiled section listed
    `test_alpha`, `test_beta` and `test_gamma`, which are not tests at all — they are `def test_…`
    text inside this file's own fixture string constants. Same class as the validator defect e15
    fixed: an unanchored pattern over a whole file reads things that are not there. Function
    discovery has to come from the parser, not from a regex.
    """
    (bundle / "suite" / "test_quoted.py").write_text(
        'FIXTURE = """\n\n\ndef test_not_real():\n    \\"\\"\\"covers: M1 — invented.\\"\\"\\"\n"""\n\n\n'
        'def test_real():\n    """covers: M1 — an actual test."""\n')
    found = add.checks_of([bundle / "suite" / "test_quoted.py"])
    assert add.cite_hits("test_real", found), found
    # Resolved through the grammar, not by key membership: keys are `module::name` since e16,
    # so a bare `not in found` is vacuously true and this negative assertion would pass even
    # if the extractor DID invent the test. Caught on review of e16's own diff.
    assert not add.cite_hits("test_not_real", found), \
        f"a `def test_` inside a string literal was extracted as a test: {sorted(found)}"


def test_description_survives_compilation(bundle):
    """covers: M1 — compile the citation, keep the human's reason for the check.

    The first compiled section rendered every line as `· proves M1` — mechanically true and
    worthless. The citation is what must be extracted (a human cannot be trusted to keep it
    honest); the DESCRIPTION is knowledge only the author has. Losing it to win the citation
    trades the wrong thing.
    """
    add.checks_sync(bundle, CID, _suite(bundle))
    body = add.read(bundle / CID.lstrip("/"), "T2")["body"]
    assert "proves M1" not in body, "the description was replaced by mechanical filler"
    assert "an actual test" in body or "the first rule is enforced here" in body, \
        f"the author's description did not survive compilation:\n{body}"


def test_verify_is_clean_after_sync(bundle):
    """covers: M2, M4 — the two halves agree: what sync writes, verify accepts."""
    add.checks_sync(bundle, CID, _suite(bundle))
    assert add.checks_verify(bundle, CID, _suite(bundle)) == []


# -------------------------------------------------------------- sync (M4, R:WIDEEDIT)


def test_sync_writes_the_checks_section(bundle):
    """covers: M1 — the invented line goes; the real ones arrive."""
    add.checks_sync(bundle, CID, _suite(bundle))
    body = add.read(bundle / CID.lstrip("/"), "T2")["body"]
    assert "test_alpha · covers: M1" in body
    assert "test_gamma · covers: M3" in body


def test_no_authored_check_survives_sync(bundle):
    """covers: M1, R:AUTHOREDCHECK — a citation with no test behind it does not persist."""
    add.checks_sync(bundle, CID, _suite(bundle))
    assert "test_invented" not in add.read(bundle / CID.lstrip("/"), "T2")["body"]


def test_sync_rewrites_only_checks(bundle):
    """covers: M4, R:WIDEEDIT — every byte outside the CHECKS section survives."""
    path = bundle / CID.lstrip("/")
    before = path.read_text().split("## CHECKS")
    add.checks_sync(bundle, CID, _suite(bundle))
    after = path.read_text().split("## CHECKS")
    assert after[0] == before[0], "content before CHECKS changed"
    assert after[1].split("## EVIDENCE")[1] == before[1].split("## EVIDENCE")[1], \
        "content after CHECKS changed"


def test_sync_is_idempotent(bundle):
    """covers: M4 — a second sync writes nothing at all."""
    add.checks_sync(bundle, CID, _suite(bundle))
    first = (bundle / CID.lstrip("/")).read_bytes()
    changed, note = add.checks_sync(bundle, CID, _suite(bundle))
    assert changed is False, note
    assert (bundle / CID.lstrip("/")).read_bytes() == first


def test_sync_preserves_unlabelled_note(bundle):
    """covers: M3 — the honest gap is carried into the section, not dropped from it.

    e15 recorded two machinery tests as `unlabelled by design`. A sync that silently omits
    unlabelled tests turns a visible gap into an invisible one.
    """
    add.checks_sync(bundle, CID, _suite(bundle))
    body = add.read(bundle / CID.lstrip("/"), "T2")["body"]
    assert "test_unlabelled" in body, f"an unlabelled test vanished from the record:\n{body}"


def test_sync_refuses_a_gated_node(bundle):
    """covers: M4, R:SILENTFIX — §3.6: a gated claim is recorded, never repaired.

    This is the asymmetry F2 turned on. e12's own CHECKS were corrected freely because nothing
    had been stamped; M0's nine cannot be, because a gate was taken against them.
    """
    path = bundle / CID.lstrip("/")
    n = add.read(path, "T2")
    add.write(path, f"---\n{add.append_item(n['raw'], 'verified', '{ by: \"human:t\", at: 2026-07-30, act: gate, authority: human, outcome: PASS }')}\n---\n{n['body']}")
    before = path.read_bytes()

    changed, note = add.checks_sync(bundle, CID, _suite(bundle))
    assert changed is False and "gate" in note.lower(), note
    assert path.read_bytes() == before, "a gated node's CHECKS were rewritten"


def test_sync_on_a_gated_node_still_reports(bundle):
    """covers: M2, M4 — refusing to fix is not refusing to say. The finding survives the refusal."""
    path = bundle / CID.lstrip("/")
    n = add.read(path, "T2")
    add.write(path, f"---\n{add.append_item(n['raw'], 'verified', '{ by: \"human:t\", at: 2026-07-30, act: gate, authority: human, outcome: PASS }')}\n---\n{n['body']}")
    assert add.checks_verify(bundle, CID, _suite(bundle)), \
        "a gated node with a fictional citation reported nothing"


# ------------------------------------------------------------------- the live bundle


def test_live_bundle_verify_reports_f2():
    """covers: M2 — F2's 65 rules, REPORTED by the verb rather than by an ad-hoc script.

    Reports rather than asserting zero: the nine M0 tasks are gated, so `--sync` must refuse them
    and this must keep saying so. A count that goes to zero here would mean someone repaired a
    gated claim.
    """
    root = REPO / ".add"
    suite = sorted((REPO / "tests").rglob("test_*.py"))
    affected = {}
    for cid, node in sorted(add.scan(root).items()):
        if (node["fm"] or {}).get("type") != "Task":
            continue
        findings = add.checks_verify(root, cid, suite)
        if findings:
            affected[cid.split("/")[-1][:-3]] = len(findings)
    print(f"\nnodes with unverifiable CHECKS citations: {len(affected)} -> {affected}")
    assert isinstance(affected, dict)


def test_a_long_description_is_cut_at_a_word(bundle):
    """covers: M1 — a compiled line that ends mid-word is a line a reader stops trusting.

    The first compiled section of this task's own node ended lines at `own n` and `covers`. Cutting
    is fine — the CHECKS section is a summary, not the test. Cutting silently, mid-word, is not:
    the reader cannot tell a truncation from a typo. It cuts at a space and says that it cut.
    """
    src = bundle / "suite" / "test_long.py"
    src.write_text(
        'def test_long():\n'
        '    """covers: M1 — ' + "supercalifragilistic reasoning " * 6 + '."""\n'
    )
    desc = _at(add.checks_of([src]), "test_long")[1]
    assert desc.endswith("…"), f"a cut description did not say it was cut: {desc!r}"
    assert not desc.rstrip("…").endswith(("supercalifragilisti", "supercalifragilis")), \
        f"cut mid-word: {desc!r}"
    assert desc.rstrip("… ").split()[-1] in ("supercalifragilistic", "reasoning"), \
        f"cut at something other than a word boundary: {desc!r}"


def test_a_generator_of_paths_reports_the_true_file_count(bundle):
    """covers: M1 — the verb must not report a number it has made false by its own iteration.

    `checks_sync` walks `paths` twice: once to compile, once to count. Handed a generator the
    second walk sees nothing, so it reports "N checks compiled from 0 suite files" — the checks
    are right and the count is a lie. Guessed wrong about this once: the first version of this
    test assumed the SECTION came out empty. It does not, because compilation is the first walk.
    A notary whose own report carries a false number is the defect, however small the number.
    """
    files = _suite(bundle)
    assert add.checks_of(f for f in files), "a generator of paths yielded no tests at all"
    ok, note = add.checks_sync(bundle, CID, (f for f in files))
    assert ok, f"sync over a generator refused: {note}"
    assert "from 0 suite files" not in note, f"reported a count its own iteration destroyed: {note}"
    assert f"from {len(files)} suite" in note, f"wrong file count: {note}"
