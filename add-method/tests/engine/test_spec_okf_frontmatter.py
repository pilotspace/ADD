"""Red suite for `okf-spec-frontmatter` — a Spec carries OKF's recommended keys, and the
bundle root declares the OKF version it conforms to.

OKF v0.2 (GoogleCloudPlatform/knowledge-catalog `okf/SPEC.md`) recommends `description:`
and `tags:`, defines provenance under the plural `sources:`, and declares `okf_version:`
on the BUNDLE-ROOT index and nowhere else. ADD's Spec nodes already carry `type:`,
`title:` and `generated: {by, at}` by accident of design; this task makes the conformance
deliberate and, crucially, gives the headline key a READER on the day it lands — the
Specs section of the compiled index is rendered from `description:`, exactly as a
Persona's row is already rendered from its `use-when:`.

Excluded by decision, and pinned here so the exclusion cannot rot: OKF's doc-status
lifecycle (`status:`) collides with ADD's task lifecycle — the `okf-persona-template`
precedent already rejected it for Personas — and `stale_after:` has nothing left to say
now that every delta carries its own validity interval.

Driven as dogfood task `.add/tasks/okf-spec-frontmatter.md` (milestone `okf-graph-time`).
"""
import re
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REPO_ROOT = REPO.parent
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

OKF_SPEC_KEYS = ("description", "tags", "sources")


def _fm(path: Path) -> dict:
    return add.read(path, "T2")["fm"]


def _raw(path: Path) -> str:
    # A compiled reserved file (log.md) has no frontmatter at all, so `raw` is None there.
    return add.read(path, "T2")["raw"] or ""


def test_init_scaffolds_okf_keys_on_every_spec(tmp_path):
    """covers: M1, A11 — every scaffolded Spec carries description/tags/sources, the
    description IS that lens's own goal, and the two lists are real empty lists."""
    add.init(tmp_path, "code", "T")
    specs = sorted((tmp_path / "specs").glob("*.md"))
    assert len(specs) == len(add.PROFILES["code"]), \
        "the code profile must scaffold one Spec per lens — nothing below is meaningful otherwise"
    for path in specs:
        fm = _fm(path)
        for key in OKF_SPEC_KEYS:
            assert key in fm, f"specs/{path.name} carries no `{key}:` — OKF's recommended set"
        assert fm["description"] == add.PROFILES["code"][path.stem], (
            f"specs/{path.name}'s description must BE the lens goal that `## Now` opens with, "
            f"so the two are identical by construction at birth")
        # A11's probe: an empty list means NOT YET CLASSIFIED. A placeholder string here
        # would reach the first consumer as a one-item list of angle-bracket text.
        for key in ("tags", "sources"):
            assert fm[key] == [], (
                f"specs/{path.name}'s `{key}:` must scaffold as a real empty list, "
                f"never a placeholder — got {fm[key]!r}")
        # A4's probe: OKF doc-status and staleness stay OUT of a Spec.
        for excluded in ("status", "stale_after"):
            assert excluded not in fm, \
                f"specs/{path.name} must not carry `{excluded}:` — excluded by decision"


def test_okf_version_is_declared_only_at_the_bundle_root(tmp_path):
    """covers: M2, R:OKFSPRAWL, A21 — the root index declares it; nothing else does."""
    _graph, created, _note = add.init(tmp_path, "code", "T")
    index = tmp_path / "index.md"
    assert index.is_file(), "no index.md — assert the subject exists before asserting about it"
    fm = _fm(index)
    assert fm.get("okf_version") == "0.2", (
        "the bundle root must declare `okf_version: \"0.2\"` — quoted, so a consumer reads the "
        f"two-character string and never a float that round-trips as 0.20; got {fm.get('okf_version')!r}")
    sprawl = []
    for rel in created:
        path = tmp_path / rel.lstrip("/")
        if path.suffix != ".md" or path == index or not path.is_file():
            continue
        if re.search(r"^okf_version:", _raw(path), re.M):
            sprawl.append(rel)
    assert not sprawl, (
        f"R:OKFSPRAWL — the OKF version is declared once, at the bundle root; found it also on "
        f"{sprawl}")


def test_index_specs_row_reads_the_node_description(tmp_path):
    """covers: M3 — the compiled Specs section carries each node's frontmatter description."""
    add.init(tmp_path, "code", "T")
    body = add._render_index(tmp_path, add.load(tmp_path))
    section = body.split("## Specs", 1)[-1].split("\n## ", 1)[0]
    assert section.strip(), "no Specs section rendered — nothing below is meaningful"
    for lens, goal in add.PROFILES["code"].items():
        assert f"(specs/{lens}.md) — {goal}" in section, (
            f"the Specs row for `{lens}` must carry its node's description as the catalogue "
            f"line, so the index can never disagree with the node")


def test_okf_version_survives_doctor_sync(tmp_path):
    """covers: M4 — a sync that rewrites the index BODY leaves the header declaration alone."""
    add.init(tmp_path, "code", "T")
    index = tmp_path / "index.md"
    assert _fm(index).get("okf_version") == "0.2", \
        "init must write the declaration before this test can say anything about surviving a sync"
    add.new(tmp_path, "Task", "a-node-that-forces-a-body-rewrite")
    before = index.read_text(encoding="utf-8")
    changed, _note = add.doctor_sync(tmp_path)
    after = index.read_text(encoding="utf-8")
    assert changed and after != before, \
        "the sync must actually have rewritten the index, or surviving it proves nothing"
    assert "a-node-that-forces-a-body-rewrite" in after, "the BODY is what a sync recomputes"
    assert _fm(index).get("okf_version") == "0.2", \
        "`doctor --sync` ate the bundle header's OKF declaration — frontmatter is never recomputed"


def test_a_spec_without_a_description_keeps_its_authored_index_tail(tmp_path):
    """covers: E1, R:TAILEATEN — description wins when present; an authored tail survives
    when it is absent; and a Spec with neither renders a bare row, not a dangling separator.

    `init` writes an index with NO TOC rows at all, so the authored tail has to be planted
    into a MATERIALIZED index — a `.replace` against the freshly-initialised file is a
    silent no-op, and the assertion it feeds would then fail for a fixture reason wearing a
    behaviour reason's clothes.
    """
    add.init(tmp_path, "code", "T")
    index = tmp_path / "index.md"

    def strip_description(lens):
        path = tmp_path / "specs" / f"{lens}.md"
        node = add.read(path, "T2")
        raw = "\n".join(l for l in node["raw"].splitlines() if not l.startswith("description:"))
        path.write_text(f"---\n{raw}\n---\n{node['body']}")
        assert "description" not in add.read(path, "T2")["fm"], \
            f"the fixture must actually remove {lens}'s description"

    # Two OLD-bundle specs: one a human gave an index tail, one nobody ever described.
    strip_description("method")
    strip_description("domain")

    add.doctor_sync(tmp_path)  # materialize the TOC — without it the plant below is a no-op
    authored = "the lens a human described by hand"
    planted = index.read_text(encoding="utf-8").replace(
        "(specs/method.md)", f"(specs/method.md) — {authored}")
    assert authored in planted, \
        "the fixture must actually plant the authored tail — a no-op replace proves nothing"
    index.write_text(planted)

    rendered = add._render_index(tmp_path, add.load(tmp_path))
    specs = rendered.split("## Specs", 1)[-1].split("\n## ", 1)[0]

    assert f"(specs/experience.md) — {add.PROFILES['code']['experience']}" in specs, \
        "a described Spec must render its description as the catalogue line"
    assert f"(specs/method.md) — {authored}" in specs, \
        "R:TAILEATEN — a Spec with no description lost the tail a human authored"
    assert re.search(r"^- \[Domain\]\(specs/domain\.md\)$", specs, re.M), (
        "a Spec with neither a description nor an authored tail must render a bare row — "
        f"got: {[l for l in specs.splitlines() if 'domain' in l]}")


def test_doc_profile_specs_carry_okf_keys_too(tmp_path):
    """covers: E2 — the doc profile scaffolds four lenses, each seeded from ITS own goals."""
    add.init(tmp_path, "doc", "T")
    goals = add.PROFILES["doc"]
    specs = sorted((tmp_path / "specs").glob("*.md"))
    assert {p.stem for p in specs} == set(goals), \
        "the doc profile scaffolds its own four lenses — not the code profile's five"
    for path in specs:
        fm = _fm(path)
        assert fm.get("description") == goals[path.stem], (
            f"specs/{path.name} was seeded from the wrong profile's goal string — "
            f"got {fm.get('description')!r}")
        assert fm.get("tags") == [] and fm.get("sources") == [], \
            f"specs/{path.name} must carry the OKF lists under every profile"


def test_live_specs_and_index_are_backfilled():
    """covers: M5, A14 — this repo's own bundle conforms, and the backfill did not clobber
    the delta counter the id minter maintains."""
    specs_dir = REPO_ROOT / ".add" / "specs"
    index = REPO_ROOT / ".add" / "index.md"
    assert specs_dir.is_dir() and index.is_file(), \
        "the dogfood bundle must exist — a missing file must never read as conforming"
    specs = sorted(specs_dir.glob("*.md"))
    assert len(specs) == 5, f"expected the five live lenses, found {[p.stem for p in specs]}"

    assert _fm(index).get("okf_version") == "0.2", \
        ".add/index.md does not declare the OKF version this bundle conforms to"

    dated = 0
    for path in specs:
        node = add.read(path, "T2")
        fm = node["fm"]
        assert str(fm.get("description") or "").strip(), \
            f".add/specs/{path.name} carries no description — the catalogue line the index reads"
        assert isinstance(fm.get("tags"), list), f".add/specs/{path.name}: `tags:` must be a list"
        assert isinstance(fm.get("sources"), list), f".add/specs/{path.name}: `sources:` must be a list"
        # The backfill edits frontmatter by hand; `delta_seq` is the id minter's high-water
        # mark and losing it re-mints ids that are already published as concept addresses.
        if re.search(r"^- \[\w+ · \w+ · ", node["body"], re.M):
            dated += 1
            assert "delta_seq" in fm, (
                f".add/specs/{path.name} holds deltas but lost `delta_seq:` — the next "
                f"`add learn` would re-mint an id that is already a published address")
    assert dated >= 4, (
        f"only {dated} specs matched the dated delta grammar — the delta_seq guard above went "
        f"silent, and a guard that inspects nothing reports clean")


def test_format_documents_the_okf_frontmatter_contract():
    """covers: M6, A4, A22 — FORMAT states the contract a second implementer must honour."""
    text = (REPO / "FORMAT.md").read_text(encoding="utf-8")
    assert text.strip(), "FORMAT.md is empty — nothing below is meaningful"
    assert "okf_version" in text, \
        "FORMAT does not name `okf_version` — a key the engine writes and the document omits"
    header_row = next((l for l in text.splitlines()
                       if l.startswith("| `index.md`")), "")
    assert "okf_version" in header_row, \
        "§1's bundle-header key row must list `okf_version` beside `abf_version`"
    for key in OKF_SPEC_KEYS:
        assert f"`{key}:`" in text or f"`{key}`" in text, \
            f"FORMAT does not document the Spec key `{key}` that `init` now writes"
    # A22: a re-implementer must be able to tell READ from merely RECORDED.
    assert re.search(r"description.{0,400}?(read|renders?|catalogue)", text, re.S | re.I), \
        "FORMAT must say that `description:` is the key the index READS"
    assert re.search(r"(tags|sources).{0,400}?(recorded|not read|no engine)", text, re.S | re.I), \
        "FORMAT must say that `tags:`/`sources:` are recorded and read by nothing in this engine"
    # The CHECKS line binds this to "names neither status nor stale_after AS A SPEC KEY".
    # Forbidding the WORD was stricter than that and wrong: an exclusion a reader cannot see
    # is one a second implementer re-adds. So require both halves — absent from the key
    # table, and explicitly named as excluded in the prose beside it.
    table = re.search(r"\| key \| role \| read by the engine\? \|(.*?)\n\n", text, re.S)
    assert table, "FORMAT must carry a Spec frontmatter key table naming what a Spec carries"
    for excluded in ("status", "stale_after"):
        assert f"`{excluded}:`" not in table.group(1), \
            f"FORMAT lists `{excluded}:` as a key a Spec carries — it is excluded by decision"
    assert "stale_after" in text and "status:" in text, \
        "FORMAT must NAME both exclusions, not silently omit them — a silent omission gets re-added"


def test_live_index_catalogue_carries_each_spec_description():
    """covers: M7 — the payoff, asserted where it is claimed: this bundle's own index.

    M3 is provable in a tmp scaffold while `.add/index.md` still shows five bare titles,
    because nothing recompiles it. That would be M3 reported green and not delivered.
    """
    index = REPO_ROOT / ".add" / "index.md"
    specs_dir = REPO_ROOT / ".add" / "specs"
    assert index.is_file() and specs_dir.is_dir(), \
        "the dogfood bundle must exist — a missing file must never read as conforming"
    section = index.read_text(encoding="utf-8").split("## Specs", 1)[-1].split("\n## ", 1)[0]
    assert section.strip(), ".add/index.md renders no Specs section — nothing below is meaningful"

    generic = set(add.PROFILES["code"].values())
    for path in sorted(specs_dir.glob("*.md")):
        description = str(_fm(path).get("description") or "").strip()
        assert description, f".add/specs/{path.name} has no description to render"
        assert f"(specs/{path.name}) — {description}" in section, (
            f"the catalogue row for {path.name} does not carry its node's description — "
            f"recompile the index so M3's payoff is real in this bundle")
        # A20/C4: a row restating the lens taxonomy tells a cold reader nothing new.
        assert description not in generic, (
            f".add/specs/{path.name} still carries the generic profile goal string as its "
            f"description — a live spec earns a bundle-specific line")


# --------------------------------------------------------------- M8/M9: the stamp has a reader
#
# `okf_version` was REMOVED from `init` on 2026-08-08 (baa066ae) because "nothing in the engine,
# the validator, or the skill ever READS it". That reason was still true when this task re-landed
# the stamp, so re-landing it alone would have reversed a decision instead of answering it. The
# old guard's RULE survives — no key that nothing reads — and these two checks are what make the
# premise false rather than the rule wrong.

def test_doctor_reports_okf_conformance(tmp_path):
    """covers: M8 — the reader discriminates; it does not always fire.

    A finding that appears whatever the bundle says would be a reader in name only, so the
    negative case is asserted first: strip the declaration and the finding must disappear.
    """
    root = tmp_path / "declared" / ".add"
    add.init(root, "code", "Declared")
    codes = [f["code"] for f in add.doctor(root)]
    assert "okf_conformance" in codes, f"a declaring bundle produced no okf finding: {codes}"

    detail = next(f["detail"] for f in add.doctor(root) if f["code"] == "okf_conformance")
    assert "0.2" in detail, f"the finding does not name the declared version: {detail!r}"

    bare = tmp_path / "undeclared" / ".add"
    add.init(bare, "code", "Bare")
    idx = bare / "index.md"
    idx.write_text(idx.read_text(encoding="utf-8").replace('okf_version: "0.2"\n', ""),
                   encoding="utf-8")
    assert "okf_version" not in idx.read_text(encoding="utf-8"), "fixture: the strip did not apply"
    bare_codes = [f["code"] for f in add.doctor(bare)]
    assert "okf_conformance" not in bare_codes, (
        f"the finding fired on a bundle declaring no okf_version: {bare_codes}")


def test_init_identity_guard_still_binds_the_okf_stamp():
    """covers: M9 — the conflicting guard was RE-AIMED, never deleted.

    Deleting it would have been the cheapest way to green, and would have left nothing pinning
    the stamp in either direction — so a later silent re-removal would pass. The guard must
    still name the key, and its unrelated sibling assertions must be untouched.
    """
    src = (Path(__file__).parent / "test_init_identity.py").read_text(encoding="utf-8")
    assert "okf_version" in src, "the OKF assertion was deleted rather than re-aimed"
    assert "abf_version" in src, "the sibling abf_version assertion was lost in the re-aim"
    assert "test_the_project_is_named_for_the_project_not_the_bundle_dir" in src, (
        "the unrelated project-naming test was collateral damage")

    # Naming the key proves only that the guard was not deleted — it passes whichever DIRECTION
    # the assertion runs in. So drive the guard against a real fresh bundle: one asserting the
    # stamp is absent fails there, one asserting it is present passes.
    import test_init_identity as guard
    fns = [v for k, v in vars(guard).items()
           if k.startswith("test_") and "okf" in (v.__doc__ or k).lower() + k.lower()]
    assert fns, "no test in test_init_identity.py addresses the OKF stamp any more"
    for fn in fns:
        with tempfile.TemporaryDirectory() as tmp:
            fn(Path(tmp))   # a guard still pinning ABSENCE raises here
