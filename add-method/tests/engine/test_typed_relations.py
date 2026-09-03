"""`relations:` — a second edge family carrying TYPED edges between delta concepts.

Red-first for `/tasks/typed-relations.md`.

Two disciplines shape this file, both inherited:

* **The validator is a SUBPROCESS, never an import** (`test_doctor.py`'s module docstring).
  Importing it would make every parity claim true by construction, and the shipped skill does
  not contain this repo.
* **Every parity claim is asserted across BOTH oracles in ONE test.** The measured failure this
  guards is silent: with `relations` folded into `EDGE_KEYS` and no head-split, `_norm` reads
  `"refines /specs/../../outside.md"` as a relative path, `is_relative_to(root)` returns True,
  and `edge_out_of_bundle` — one of the three FATAL codes — downgrades to `info`. A green suite
  over a dead graph. Two per-oracle tests would each pass while the two tools disagreed.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

VALIDATOR = REPO / "scripts" / "validate_bundle.py"
LIVE = REPO.parent / ".add"

# Every code this family can put in either oracle's report. Enumerated HERE, once, so a test
# that filters the report cannot quietly filter on a code no producer emits.
RELATION_CODES = ("unknown_rel", "relation_malformed", "edge_unresolved", "edge_out_of_bundle")


# ------------------------------------------------------------------------------ helpers

def _validator(root) -> dict:
    """The M0 oracle: `{findings, exit}`. A subprocess, never an import."""
    done = subprocess.run([sys.executable, str(VALIDATOR), str(root), "--json"],
                          capture_output=True, text=True, timeout=60)
    return {"findings": json.loads(done.stdout)["findings"], "exit": done.returncode}


def _codes(findings, code) -> list:
    return [f for f in findings if f["code"] == code]


@pytest.fixture
def bundle(tmp_path):
    """A real bundle, created by the engine rather than by fixture text."""
    root = tmp_path / ".add"
    add.init(root, profile="code", title="relations fixture")
    return root


def _set_relations(root, lens, entries, *, extra_fm: str = "") -> Path:
    """Write a `relations:` block list into a live Spec's frontmatter, raw.

    Written as TEXT, deliberately: the contract under test is what the two PARSERS make of a
    block list of plain strings, so a helper that went through a serialiser would be testing
    the serialiser instead.
    """
    path = Path(root) / "specs" / f"{lens}.md"
    text = path.read_text(encoding="utf-8")
    head, sep, rest = text.partition("\n---\n")
    block = "\nrelations:\n" + "".join(f"  - {e}\n" for e in entries)
    path.write_text(head + extra_fm + block.rstrip("\n") + sep + rest, encoding="utf-8")
    return path


def _add_delta(root, lens, line) -> None:
    path = Path(root) / "specs" / f"{lens}.md"
    text = path.read_text(encoding="utf-8")
    path.write_text(text.rstrip("\n") + "\n" + line + "\n", encoding="utf-8")


def _relation_entries(root) -> list:
    """`[(cid, entry)]` for every `relations:` entry in a bundle, read from frontmatter."""
    out = []
    for cid, node in add.scan(Path(root)).items():
        for entry in (node["fm"] or {}).get("relations") or []:
            out.append((cid, str(entry)))
    return out


# ------------------------------------------------------------------- M1 · the closed vocabulary

def test_relation_vocabulary_is_closed_and_stated_once():
    """covers: M1 — the engine states the vocabulary in ONE place.

    Only the engine half. The claim that the second oracle agrees is a BEHAVIOURAL claim and
    lives in the next test — a docstring describing a body that is not here is how a reader of
    a `covers:` binding is misled about what was proven.
    """
    assert add.RELATION_VOCAB == ("refines",), (
        "the vocabulary is closed to the terms with a live corpus instance; `supersedes` was "
        "drafted and cut at verify when its one instance was refuted on measurement")


def test_the_second_oracle_mirrors_the_one_vocabulary(bundle):
    """covers: M1 — every engine term is silent in the validator; a non-term is reported."""
    _add_delta(bundle, "method", "- [ADD · M1 · open · 2026-08-11] a lesson (evidence: /x.md)")
    _add_delta(bundle, "method", "- [ADD · M2 · open · 2026-08-11] another (evidence: /x.md)")
    entries = [f"M1 {term} /specs/method.md#M2" for term in add.RELATION_VOCAB]
    entries.append("M1 informs /specs/method.md#M2")
    _set_relations(bundle, "method", entries)
    reported = _codes(_validator(bundle)["findings"], "unknown_rel")
    assert len(reported) == 1, \
        f"the validator's vocabulary differs from the engine's: {reported}"
    assert "informs" in reported[0]["detail"], reported[0]


def test_every_relation_term_is_used_by_a_live_relation():
    """covers: R:DEADVOCAB, A3 — the probe. Every term ships with an instance in the corpus.

    The floor comes FIRST: a vocabulary term set that is empty, or a corpus with no relations at
    all, would make `used == set(vocab)` degrade to `set() == set()` and pass proving nothing.
    """
    assert add.RELATION_VOCAB, "an empty vocabulary makes every claim below vacuous"
    entries = _relation_entries(LIVE)
    assert len(entries) >= 4, \
        f"the live corpus carries no relations to justify the vocabulary: {entries}"
    used = {e.split()[1] for _cid, e in entries if len(e.split()) == 3}
    assert used == set(add.RELATION_VOCAB), (
        f"a term ships without a live instance (dead on arrival): "
        f"{sorted(set(add.RELATION_VOCAB) - used)}; "
        f"or the corpus uses a term the vocabulary does not close over: "
        f"{sorted(used - set(add.RELATION_VOCAB))}")


# ------------------------------------------------------------------------------ M2 · the shape

def test_both_oracles_parse_one_relation_entry_identically(bundle):
    """covers: M2 — the plain-string shape is the contract; a flow map is not.

    Measured before this task: `- {{ rel: refines, target: /x.md#M1 }}` parses to a DICT in
    `add.parse` and to the raw brace STRING in `validate_bundle.parse_frontmatter`. Same file,
    two values, no error anywhere. The plain string parses identically in both, which is why the
    shape is frozen rather than left to taste.
    """
    _add_delta(bundle, "method", "- [ADD · M1 · open · 2026-08-11] a lesson (evidence: /x.md)")
    _add_delta(bundle, "method", "- [ADD · M2 · open · 2026-08-11] another (evidence: /x.md)")
    _set_relations(bundle, "method", ["M1 refines /specs/method.md#M2"])
    ours = {f["code"] for f in add.doctor(bundle) if f["code"] in RELATION_CODES}
    theirs = {f["code"] for f in _validator(bundle)["findings"] if f["code"] in RELATION_CODES}
    assert ours == theirs == set(), \
        f"a well-formed plain-string relation was reported: doctor={ours} validator={theirs}"

    _set_relations(bundle, "method", ["{ rel: refines, target: /specs/method.md#M2 }"])
    ours = {f["code"] for f in add.doctor(bundle) if f["code"] in RELATION_CODES}
    theirs = {f["code"] for f in _validator(bundle)["findings"] if f["code"] in RELATION_CODES}
    assert ours == theirs == {"relation_malformed"}, (
        "a flow-map entry must be reported the SAME way by both oracles — this is the exact "
        f"shape the two parsers disagreed about: doctor={ours} validator={theirs}")


# -------------------------------------------------------------- M3 · containment, the fatal one

def test_a_relation_escaping_the_bundle_is_fatal_like_a_depends_on(bundle):
    """covers: M3, R:SILENTESCAPE — one node, one target, two keys, one assertion.

    Asserted TOGETHER so the two can never drift: the identical escaping target must produce the
    identical fatal code whether it arrives through `depends_on:` or through `relations:`. Split
    into two tests, the relation half passes at `info` for a year.

    BOTH escape spellings are driven. The absolute one (`/specs/../../outside.md`) was fatal
    before this task and would have carried the whole claim on its own — while the RELATIVE one
    was silently downgraded in `doctor` and fatal in the validator, so the two oracles disagreed
    about a containment escape. `_norm` builds its cid with `os.path.normpath` on a leading-`/`
    string, where `..` clamps at the root instead of ascending: `../../outside.md` became
    `/outside.md`, which is inside the bundle. One spelling is not a containment test.
    """
    _add_delta(bundle, "method", "- [ADD · M1 · open · 2026-08-11] a lesson (evidence: /x.md)")
    for escape in ("/specs/../../outside.md", "../../outside.md", "/../outside.md"):
        _set_relations(bundle, "method", [f"M1 refines {escape}"],
                       extra_fm=f"\ndepends_on:\n  - {escape}")
        for label, findings in (("doctor", add.doctor(bundle)),
                                ("validator", _validator(bundle)["findings"])):
            fatal = _codes(findings, "edge_out_of_bundle")
            assert all(f["severity"] == "error" for f in fatal), \
                f"{label}: `{escape}` downgraded: {fatal}"
            details = " | ".join(f["detail"] for f in fatal)
            assert len(fatal) == 2, (
                f"{label}: `{escape}` reported {len(fatal)} times, not twice — the same target "
                f"escapes through both keys, so both must be fatal: {details}")


# -------------------------------------------------------------------------- M4 · law 3 for rels

def test_an_unknown_rel_is_recorded_not_rejected(bundle):
    """covers: M4, R:REJECTUNKNOWN — recorded at info, exit unchanged, target still resolved."""
    _add_delta(bundle, "method", "- [ADD · M1 · open · 2026-08-11] a lesson (evidence: /x.md)")
    _add_delta(bundle, "method", "- [ADD · M2 · open · 2026-08-11] another (evidence: /x.md)")
    _set_relations(bundle, "method", ["M1 contradicts /specs/method.md#M2"])
    report = _validator(bundle)
    unknown = _codes(report["findings"], "unknown_rel")
    assert len(unknown) == 1 and unknown[0]["severity"] == "info", unknown
    assert report["exit"] == 0, "an unknown rel must never change the verdict"

    # POSITIVE, not `assert not`. `assert not edge_unresolved` reads the same whether the target
    # resolved or was never tested at all: making the unknown-rel branch `continue` — the exact
    # regression this line names — removes the finding AND the test, and the absence assertion
    # still passes. Require the entry to be present in the reader's output with a RESOLVED target.
    graph = add.scan(bundle)
    entry = [r for r in add.relations(graph) if r[2] == "contradicts"]
    assert len(entry) == 1, f"the unknown rel was dropped from the reader entirely: {entry}"
    assert entry[0][4] == "/specs/method.md", (
        f"an unknown rel suppressed its own target's resolution: target={entry[0][4]}")
    assert not _codes(report["findings"], "edge_unresolved"), \
        "the target is a real concept and must resolve whatever the verb says"


# ------------------------------------------------------------- M5 · §3.3 gains a third form

def test_a_delta_id_is_the_third_fragment_resolution_form(bundle):
    """covers: M5 — `#M4` is neither a frontmatter key nor a heading slug of `method.md`."""
    _add_delta(bundle, "method",
               "- [ADD · M4 · open · 2026-08-12] the gate binds every referent (evidence: /x.md)")
    graph = add.scan(bundle)
    cid, value, why = add.resolve(graph, "/specs/method.md#M4", "/specs/quality.md")
    assert why == "delta", (
        f"a delta id resolved as `{why}` — without this form every concept edge in the "
        f"migration reports edge_unresolved while looking migrated")
    assert value and "binds every referent" in str(value), value


def test_a_frontmatter_key_still_beats_a_delta_id_of_the_same_name(bundle):
    """covers: A6 — the probe for the ordering reading: the delta form is THIRD, not first.

    A reference can never resolve two ways (§3.3). Constructed so both forms could match the
    same fragment, which is the only shape that can catch a mis-ordered ladder.

    The SHADOWED half comes first and is the floor. Without it this test is green before any
    build — `frontmatter` wins trivially while the delta form does not exist at all, and a
    green check before the build proves nothing. `M8` has no frontmatter key, so it can only
    resolve through the form this task adds.
    """
    _add_delta(bundle, "method",
               "- [ADD · M8 · open · 2026-08-12] only in the body (evidence: /x.md)")
    _add_delta(bundle, "method",
               "- [ADD · M9 · open · 2026-08-12] from the body (evidence: /x.md)")
    _set_relations(bundle, "method", ["M9 refines /specs/method.md#M8"],
                   extra_fm="\nM9: from-the-frontmatter")
    graph = add.scan(bundle)
    _cid, value, why = add.resolve(graph, "/specs/method.md#M8", "/specs/quality.md")
    assert why == "delta", (
        f"the third form does not exist, so the ordering claim below is untestable: got `{why}`")
    assert "only in the body" in str(value), value

    _cid, value, why = add.resolve(graph, "/specs/method.md#M9", "/specs/quality.md")
    assert why == "frontmatter", f"the delta form jumped the ladder and resolved as `{why}`"
    assert "from-the-frontmatter" in str(value), value

    # The HEADING half of the same ladder claim. The two id spaces are NOT disjoint — a delta id
    # is `[A-Za-z][A-Za-z0-9_-]*`, so a lower-case id equals a heading slug — which is why what
    # makes resolution single-valued is the ORDER, not the alphabet. FORMAT §3.3 says exactly
    # this; it used to claim the sets could not intersect, which is false and is what this half
    # pins.
    _add_delta(bundle, "method",
               "- [ADD · zz · open · 2026-08-12] a lower-case id (evidence: /x.md)")
    path = bundle / "specs" / "method.md"
    path.write_text(path.read_text(encoding="utf-8") + "\n## zz\n\nfrom-the-heading\n",
                    encoding="utf-8")
    graph = add.scan(bundle)
    _cid, value, why = add.resolve(graph, "/specs/method.md#zz", "/specs/quality.md")
    assert why == "heading", f"a delta id outranked a heading slug of the same name: `{why}`"
    assert "from-the-heading" in str(value), value


# ------------------------------------------------------------------ M6 · the source end resolves

def test_a_relation_source_that_names_no_delta_is_reported(bundle):
    """covers: M6 — a relation with a real target and a phantom source is a half-edge."""
    _add_delta(bundle, "method", "- [ADD · M2 · open · 2026-08-11] a lesson (evidence: /x.md)")
    _set_relations(bundle, "method", ["M99 refines /specs/method.md#M2"])
    for label, findings in (("doctor", add.doctor(bundle)),
                            ("validator", _validator(bundle)["findings"])):
        dead = _codes(findings, "edge_unresolved")
        assert len(dead) == 1 and dead[0]["severity"] == "info", f"{label}: {dead}"
        assert "M99" in dead[0]["detail"], (
            f"{label}: the finding does not quote the offending source, so a maintainer cannot "
            f"act on it: {dead[0]['detail']}")


# ------------------------------------------------------------------------- M7 · never dropped

def test_a_malformed_relation_entry_is_never_dropped(bundle):
    """covers: M7 — two fields and four fields each report, in both oracles."""
    _add_delta(bundle, "method", "- [ADD · M1 · open · 2026-08-11] a lesson (evidence: /x.md)")
    _set_relations(bundle, "method",
                   ["refines /specs/method.md#M1", "M1 refines /specs/method.md#M1 extra"])
    for label, findings in (("doctor", add.doctor(bundle)),
                            ("validator", _validator(bundle)["findings"])):
        bad = _codes(findings, "relation_malformed")
        assert len(bad) == 2, f"{label}: a malformed entry vanished from the report: {bad}"
        assert all(f["severity"] == "info" for f in bad), f"{label}: {bad}"


# ------------------------------------------------------------------------ M8 · §9's invariant

def test_noising_every_body_leaves_the_relation_exit_code_unchanged(bundle, tmp_path):
    """covers: M8 — §9 re-run with relations present, including an escaping one.

    The verdict is frontmatter-only. Relations live in frontmatter, so noising every body must
    move nothing: the escape stays fatal and the exit code is byte-for-byte the same.
    """
    _add_delta(bundle, "method", "- [ADD · M1 · open · 2026-08-11] a lesson (evidence: /x.md)")
    _set_relations(bundle, "method", ["M1 refines /specs/../../outside.md"])
    before = _validator(bundle)
    assert before["exit"] == 1, "the fixture must be non-conforming for this to mean anything"

    noised = tmp_path / "noised"
    shutil.copytree(bundle, noised)
    for path in noised.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        head, sep, _body = text.partition("\n---\n")
        if sep:
            path.write_text(head + sep + "qqq noise noise noise\n", encoding="utf-8")
    assert _validator(noised)["exit"] == before["exit"], \
        "replacing every body with noise changed the verdict — a body-derived error exists"


# ------------------------------------------------------------------------------ M9 · the format

def test_format_documents_the_relation_family_and_its_severities():
    """covers: M9 — read from the engine's own constants, never from string literals.

    A guard that lists the vocabulary as literals matches its own source (M17/M20, both live).
    Every term and every code below comes from the engine tuple this file already imports.
    """
    text = (REPO / "FORMAT.md").read_text(encoding="utf-8")
    flat = " ".join(text.split())
    for section in ("### §3.2", "### §3.3", "## §9"):
        assert section in text, f"FORMAT lost {section}"
    edges_section = text.split("### §3.2", 1)[1].split("### §3.3", 1)[0]
    assert "relations" in edges_section, "§3.2 never names the family"
    for term in add.RELATION_VOCAB:
        assert term in edges_section, f"§3.2 does not state the vocabulary term `{term}`"
    assert "plain string" in edges_section.lower() or "plain-string" in edges_section.lower(), \
        "§3.2 states no shape, so a second engine cannot know a flow map is not one"
    resolution = text.split("### §3.3", 1)[1].split("## §4", 1)[0]
    assert "delta" in resolution.lower(), "§3.3 never states the third resolution form"
    conformance = text.split("## §9", 1)[1]
    for code in ("unknown_rel", "relation_malformed"):
        assert code in conformance, f"§9's table does not carry `{code}`"
        row = [l for l in conformance.splitlines() if code in l]
        assert any("info" in l for l in row), f"`{code}` is stated without severity info: {row}"
    assert "two distinct grammars" in flat or "distinct grammars" in flat, (
        "FORMAT never says the `supersedes` edge key and the `supersedes` relation verb are "
        "different grammars sharing one word")


# --------------------------------------------------------------------------- M10 · the migration

def test_the_live_specs_carry_relations_that_resolve_on_both_ends():
    """covers: M10 — a floor first, then every live relation resolving at source AND target."""
    graph = add.scan(LIVE)
    entries = _relation_entries(LIVE)
    assert len(entries) >= 4, f"the migration recorded no relations: {entries}"
    dead = []
    for cid, entry in entries:
        fields = entry.split()
        assert len(fields) == 3, f"a live relation is malformed: {cid} -> {entry}"
        src_id, _rel, target = fields
        # `why == "delta"`, not `why != "edge_unresolved"`. M6 requires the source be a delta id
        # in the node's OWN body; the weaker form would accept a frontmatter key or a heading slug
        # as a relation endpoint, which is file granularity wearing a concept's clothes.
        _c, _v, why = add.resolve(graph, f"{cid}#{src_id}", cid)
        if why != "delta":
            dead.append(f"{cid} source {src_id} resolved as {why}, not a concept")
        _c, _v, why = add.resolve(graph, target, cid)
        if why != "delta":
            dead.append(f"{cid} target {target} resolved as {why}, not a concept")
    assert not dead, f"a shipped relation is dead on one end: {dead}"


# ------------------------------------------------------------- M11 · the first family is untouched

def test_relations_do_not_leak_into_the_edge_key_family(bundle):
    """covers: M11 — `EDGE_KEYS` is unchanged and `edges()` never yields a relation.

    A relation folded into the four-tuple loses BOTH the source id and the rel type, and `_norm`
    on the unsplit entry is the containment downgrade M3 forbids.
    """
    assert add.EDGE_KEYS == ("depends_on", "needs", "tasks", "milestone",
                             "relates_to", "task", "supersedes"), \
        "the §3.2 simple-edge allowlist changed — relations are a SECOND family"
    _add_delta(bundle, "method", "- [ADD · M1 · open · 2026-08-11] a lesson (evidence: /x.md)")
    _set_relations(bundle, "method", ["M1 refines /specs/method.md#M1"])
    graph = add.scan(bundle)
    leaked = [e for e in add.edges(graph) if e[1] == "relations" or " refines " in str(e[2])]
    assert not leaked, f"a relation leaked into edges(): {leaked}"
    assert add.relations(graph), "the relation reader returned nothing for a bundle that has one"


# --------------------------------------------------------------------------- R:DIVERGE · parity

# Values chosen so every one produces a DIFFERENT finding shape, and so that each has already
# broken parity once. The first four are measured regressions, not hypotheticals:
#   `#M2`            — the engine strips a YAML comment and the validator did not, so one read
#                      two fields and the other three
#   `... # note`     — the same defect with a real trailing comment
#   a bare `- `      — parses to `{}` here and to an empty list there
#   `../../x.md`     — `_norm` clamps `..` at the root, so a containment escape read as inside
# Each MUST produce at least one finding, and both oracles must produce the same one.
ADVERSARIAL = [
    "M1 refines #M2",                       # comment strip: two fields here, three there
    "M1 refines ../../outside.md",          # `_norm` clamped `..` at the root -> read as inside
    "M1 refines /specs/../../outside.md",   # the spelling that WAS fatal, so the pair can drift
    "M1 informs /specs/method.md#M2",       # outside the closed vocabulary
    "M1 refines /specs/method.md#M77",      # target file exists, concept does not
    "M99 refines /specs/method.md#M2",      # source names no concept in this node's own body
    "refines /specs/method.md#M2",          # two fields
    "M1 refines /specs/method.md#M2 extra", # four fields
]

# Each MUST be silent in BOTH. Without these the test above is satisfiable by a reader that
# reports EVERYTHING, which agrees just as well as one that reports the right things.
CONTROL = [
    "M1 refines /specs/method.md#M2",          # the well-formed entry
    "M1 refines /specs/method.md#M2 # note",   # a YAML comment, stripped by both
    "",                                        # a bare `- ` — parsed `{}` here, `[]` there
]


def test_both_oracles_agree_on_every_adversarial_relation(bundle):
    """covers: R:DIVERGE — code AND detail, over values that can actually break parity.

    The live-bundle comparison below is a smoke test and cannot carry this rule: every migrated
    relation is clean, so both sides of it are `[]` and it stays green even with BOTH relation
    readers deleted. This drives values that each produce a finding, so withholding either
    oracle's reader turns it red.
    """
    _add_delta(bundle, "method", "- [ADD · M1 · open · 2026-08-11] a lesson (evidence: /x.md)")
    _add_delta(bundle, "method", "- [ADD · M2 · open · 2026-08-11] another (evidence: /x.md)")

    def _both(entry):
        _set_relations(bundle, "method", [entry])
        return (sorted((f["code"], f["detail"]) for f in add.doctor(bundle)
                       if f["code"] in RELATION_CODES),
                sorted((f["code"], f["detail"]) for f in _validator(bundle)["findings"]
                       if f["code"] in RELATION_CODES))

    disagreed, silent = [], []
    for entry in ADVERSARIAL:
        ours, theirs = _both(entry)
        if not ours:
            silent.append(entry)
        if ours != theirs:
            disagreed.append(f"\n  {entry!r}\n    doctor:    {ours}\n    validator: {theirs}")
    assert not silent, (
        f"these adversarial values produced NO finding, so their agreement is agreement about "
        f"silence: {silent}")

    noisy = []
    for entry in CONTROL:
        ours, theirs = _both(entry)
        if ours or theirs:
            noisy.append(f"\n  {entry!r}\n    doctor:    {ours}\n    validator: {theirs}")
        if ours != theirs:
            disagreed.append(f"\n  {entry!r}\n    doctor:    {ours}\n    validator: {theirs}")
    assert not noisy, (
        "a control value was reported — a reader that flags everything agrees with one that "
        "flags the right things, and this is what tells them apart:" + "".join(noisy))
    assert not disagreed, "the two oracles disagree about a relations: entry:" + "".join(disagreed)


def test_both_oracles_agree_on_relations_in_the_live_bundle():
    """covers: R:DIVERGE — the live-bundle smoke half, on a tree neither tool made up.

    `test_live_bundle_compiles` in `test_graph.py` is `@pytest.mark.skip`, so the folded delta's
    claim that the parity oracle catches a shape defect on the live bundle is FALSE today. This
    is the narrow replacement. It is a SMOKE test by construction — a clean corpus makes both
    sides empty — so R:DIVERGE's binding weight sits on the adversarial table above.
    """
    entries = _relation_entries(LIVE)
    assert entries, "no relations on the live bundle would make this parity claim vacuous"
    ours = sorted((f["code"], f["detail"]) for f in add.doctor(LIVE)
                  if f["code"] in RELATION_CODES)
    theirs = sorted((f["code"], f["detail"]) for f in _validator(LIVE)["findings"]
                    if f["code"] in RELATION_CODES)
    assert ours == theirs, (
        "the two oracles disagree about the relations family on the live bundle.\n"
        f"  only doctor:    {[x for x in ours if x not in theirs]}\n"
        f"  only validator: {[x for x in theirs if x not in ours]}")


# ------------------------------------------------------------------------------------- edges

def test_an_unknown_rel_escaping_the_bundle_reports_both(bundle):
    """covers: E1 — the info finding must not swallow the fatal one."""
    _add_delta(bundle, "method", "- [ADD · M1 · open · 2026-08-11] a lesson (evidence: /x.md)")
    _set_relations(bundle, "method", ["M1 informs /specs/../../outside.md"])
    for label, findings in (("doctor", add.doctor(bundle)),
                            ("validator", _validator(bundle)["findings"])):
        codes = {f["code"] for f in findings if f["code"] in RELATION_CODES}
        assert "unknown_rel" in codes, f"{label}: the unknown verb went unreported: {codes}"
        fatal = _codes(findings, "edge_out_of_bundle")
        assert fatal and all(f["severity"] == "error" for f in fatal), (
            f"{label}: an unknown rel suppressed the containment escape — the only fatal code "
            f"this family can raise became unreachable through an info finding: {codes}")


def test_a_relation_to_a_deleted_delta_id_is_unresolved(bundle):
    """covers: E2 — the target FILE exists; the concept does not."""
    _add_delta(bundle, "method", "- [ADD · M1 · open · 2026-08-11] a lesson (evidence: /x.md)")
    _set_relations(bundle, "method", ["M1 refines /specs/method.md#M77"])
    for label, findings in (("doctor", add.doctor(bundle)),
                            ("validator", _validator(bundle)["findings"])):
        dead = _codes(findings, "edge_unresolved")
        assert len(dead) == 1 and "M77" in dead[0]["detail"], f"{label}: {dead}"
        assert not _codes(findings, "edge_out_of_bundle"), \
            f"{label}: an in-bundle target reported as an escape"


def test_a_node_with_no_deltas_reports_every_relation_source_unresolved(bundle):
    """covers: E3 — a Task carrying `relations:` is read and reported, never refused."""
    add.new(bundle, "Task", "carrier", title="a task that carries a relation")
    path = bundle / "tasks" / "carrier.md"
    text = path.read_text(encoding="utf-8")
    head, sep, rest = text.partition("\n---\n")
    path.write_text(head + "\nrelations:\n  - M1 refines /specs/method.md#M1" + sep + rest,
                    encoding="utf-8")
    for label, findings in (("doctor", add.doctor(bundle)),
                            ("validator", _validator(bundle)["findings"])):
        dead = _codes(findings, "edge_unresolved")
        assert dead, f"{label}: a relation on a node with no Deltas section vanished"
        assert any("M1" in f["detail"] for f in dead), f"{label}: {dead}"


def test_a_concept_relation_manufactures_no_dependency_cycle():
    """covers: E4 — a live self-edge: `M8 refines /specs/method.md#M4`, both in method.md.

    `cycles()` builds its adjacency from `edges()` on `("depends_on", "needs", "supersedes")`.
    A concept-level `supersedes` that reached that tuple would make a spec depend on itself.
    """
    graph = add.scan(LIVE)
    selfies = [(cid, e) for cid, e in _relation_entries(LIVE)
               if len(e.split()) == 3 and e.split()[2].partition("#")[0] == cid]
    assert selfies, "no self-referencing relation on the live bundle — this claim is vacuous"
    assert add.cycles(graph) == [], \
        f"a concept-level relation manufactured a node-level dependency cycle: {add.cycles(graph)}"
    assert not [f for f in add.doctor(LIVE) if f["code"] == "dependency_cycle"], \
        "doctor reports a dependency cycle over a concept edge"

    # The claim above is nearly free while M11 holds — `cycles()` reads `edges()`, and `edges()`
    # never sees `relations:`. So prove the claim that actually matters: even if the family WERE
    # folded into the edge-key adjacency, a concept self-edge must not become a node self-cycle.
    # Built here rather than asserted about, so this can go red.
    adjacency = {c: [] for c in graph}
    for cid, sid, verb, ref, target in add.relations(graph):
        if target and verb in add.RELATION_VOCAB:
            adjacency[cid].append(target)
    self_cycles = {c for c, targets in adjacency.items() if c in targets}
    assert self_cycles, "no self-edge reached the adjacency — the probe below proves nothing"
    assert all(add.resolve(graph, f"{c}#{e.split()[0]}", c)[2] == "delta"
               for c, e in selfies), "a self-relation's source is not a concept in its own body"


# ---------------------------------------------------------------------------- A8 · the absent key

def test_an_absent_relations_key_emits_no_finding_and_a_present_one_does(bundle):
    """covers: A8 — the probe: a report that reads the same either way is not a reader.

    Both halves in one test, deliberately. The silent half alone is the vacuous shape this repo
    has been burned by (`assert not <collection>` with no floor); the loud half is the floor.
    """
    for label, findings in (("doctor", add.doctor(bundle)),
                            ("validator", _validator(bundle)["findings"])):
        noise = [f for f in findings if f["code"] in RELATION_CODES]
        assert not noise, f"{label}: a bundle with no relations: key emitted {noise}"

    _set_relations(bundle, "method", ["not-three-fields"])
    for label, findings in (("doctor", add.doctor(bundle)),
                            ("validator", _validator(bundle)["findings"])):
        loud = [f for f in findings if f["code"] in RELATION_CODES]
        assert len(loud) == 1 and loud[0]["code"] == "relation_malformed", \
            f"{label}: the reader is silent on a bundle that HAS a relation: {loud}"
