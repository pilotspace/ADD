"""`add search` — one verb that finds any concept in the bundle, at LESSON granularity.

The failure this exists to end is measurable in this repo's own bundle: a lookup that can only
answer `specs/method.md` points at thirty unrelated lessons, so nobody looks anything up. A hit
must therefore address the DELTA (`/specs/method.md#M28`), not the file that holds it.

Three shapes these checks guard against, all drawn from this corpus's own record:
  * a facet over an EMPTY field — it matches nothing and ships dead, the `okf_version` failure
    in a new costume; so `test_the_live_specs_carry_tags_that_search_matches` runs against the
    REAL bundle, never a fixture, and asserts the tags are words that corpus already uses;
  * a listing that leaks a body — a search that prints what it read is a context cost, not a
    lookup, so a 4000-character delta must still yield a bounded line;
  * a check whose SUBJECT the live corpus does not contain — the live specs hold zero undated,
    zero rejected and zero malformed deltas, so every check about those is fixture-backed and
    pins a literal, and each is proved red by withholding its subject.
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LIVE = REPO.parent / ".add"
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

CLI = REPO / "tooling" / "cli.py"

# A single delta whose text is far past any sensible line — R:BODYLEAK's boundary (E1).
HUGE_TEXT = "leviathan " * 400          # 4000 characters
RECEIPT_TOKEN = "zzqreceiptonly"        # appears ONLY inside a Run receipt's computation
BODY_TOKEN = "zzqbodyonly"              # appears ONLY inside a task body, in no matched field
BIND_TOKEN = "zzqbindonly"              # appears ONLY inside a `Decisions that bind` item
UNDATED = "zzqundated"                  # the two legacy undated deltas, and nothing else

METHOD_DELTAS = [
    "- [ADD · M1 · open · 2026-08-11] a gateway lesson filed in august (evidence: /tasks/a.md)",
    "- [ADD · M2 · open · 2026-09-01] a gateway lesson filed in september (evidence: /tasks/b.md)",
    "- [ADD · M3 · folded · 2026-08-11→2026-09-01] a gateway lesson folded (evidence: /tasks/c.md)",
    "- [ADD · M5 · rejected · 2026-08-11→2026-08-20] a gateway lesson rejected (evidence: /tasks/g.md)",
    f"- [ADD · M4 · open · 2026-08-11] {HUGE_TEXT} gateway (evidence: /tasks/d.md)",
    "- [ADD · M6 · open · 2026-08-11] a gateway.*lesson carrying metacharacters (evidence: /tasks/h.md)",
    f"- [ADD · M7 · open · 2026-09-02] a dated {UNDATED} decoy (evidence: /tasks/i.md)",
]
# The subject the LIVE corpus does not contain: legacy heads with no id and no interval.
LEGACY = [
    f"- [ADD · open] the first {UNDATED} legacy lesson (evidence: /tasks/e.md)",
    f"- [ADD · open] the second {UNDATED} legacy lesson (evidence: /tasks/f.md)",
]


def _spec(root, lens, *, tags, deltas, binds, title=None, description="a spec"):
    body = ("## Now\nx\n\n## Decisions that bind\n" + "".join(b + "\n" for b in binds)
            + "\n## Deltas\n" + "".join(d + "\n" for d in deltas))
    tagline = "tags: [" + ", ".join(tags) + "]"
    (root / "specs" / f"{lens}.md").write_text(
        f"---\ntype: Spec\ntitle: {title or lens.title()}\nlens: {lens}\n"
        f"description: {description}\n{tagline}\nsources: []\n---\n{body}", encoding="utf-8")


def _bundle(tmp_path, *, legacy=True):
    """A bundle carrying one of every searchable shape — and one of every shape that must NOT hit.

    `legacy=False` withholds the undated lines, which is how the footer check is proved red.
    """
    root = tmp_path / ".add"
    for sub in ("specs", "tasks", "personas", "tasks/alpha.d/runs"):
        (root / sub).mkdir(parents=True, exist_ok=True)
    (root / "index.md").write_text(
        '---\nabf_version: "1.3"\nname: b\n---\n\n<!-- COMPILED BODY -->\n\n'
        "- [Alpha](tasks/alpha.md) — the alpha goal about gateways\n", encoding="utf-8")
    _spec(root, "method", tags=["registry", "gate"], binds=[
        f"- a {BIND_TOKEN} decision that constrains the rest",
    ], deltas=METHOD_DELTAS + (LEGACY if legacy else []))
    # An EMPTY facet: `tags: []` must contribute no hit at all, never an empty-string match.
    _spec(root, "quality", tags=[], binds=["- <the first decision that constrains the rest>"],
          deltas=[], description="a gateway spec with no tags")
    (root / "tasks" / "alpha.md").write_text(
        "---\ntype: Task\ntitle: Alpha\nstatus: direction\n---\n"
        "## CARD\ngoal: the alpha goal about gateways\n\n"
        f"## PLAN\ncontract: {BODY_TOKEN} lives only in a body\n", encoding="utf-8")
    # A second ACTIVE task, so `todo` performs a real multi-node T2 read in the §4 measurement.
    (root / "tasks" / "beta.md").write_text(
        "---\ntype: Task\ntitle: Beta\nstatus: direction\n---\n"
        "## CARD\ngoal: the beta goal, about ordinary things\n", encoding="utf-8")
    (root / "personas" / "p.md").write_text(
        "---\ntype: Persona\ntitle: P\nsources:\n  - personas-teacher/gateway-lens.md (distilled)\n"
        "---\n## Identity\nx\n", encoding="utf-8")
    (root / "tasks" / "alpha.d" / "runs" / "1.md").write_text(
        f'---\ntype: Run\ntask: /tasks/alpha.md\ncomputation: "pytest {RECEIPT_TOKEN} gateway"\n'
        "receipt:\n  kind: test-ids\n  exit: 0\n---\n", encoding="utf-8")
    return root


def _cli(root, *args):
    return subprocess.run([sys.executable, str(CLI), "--root", str(root), "search", *args],
                          capture_output=True, text=True)


def _addresses(hits):
    return [h[0] for h in hits]


# ------------------------------------------------------------------ M1 · lesson granularity

def test_a_spec_hit_is_addressed_to_the_delta_not_the_file(tmp_path):
    """covers: M1, M2, A4 — the address is the deliverable; a whole-file hit is the old answer."""
    root = _bundle(tmp_path)
    hits, note = add.search(root, "filed in september")
    assert hits, f"the fixture spec carries this delta, so a hit is required — {note}"
    assert _addresses(hits) == ["/specs/method.md#M2"], (
        f"a delta hit must address the LESSON, not the file that holds it — {_addresses(hits)}")
    assert "/specs/method.md#M2" in note, note

    # And a whole-file hit never stands in for the lines inside it.
    hits, note = add.search(root, "gateway lesson")
    assert len(hits) >= 4, f"four delta lines carry this phrase — {_addresses(hits)}"
    assert "/specs/method.md" not in _addresses(hits), (
        f"the spec answered at FILE granularity beside its own lessons — {_addresses(hits)}")
    for address in _addresses(hits):
        assert address.startswith("/specs/method.md#"), f"a delta hit with no concept address: {address}"


def test_search_matches_the_declared_fields_and_no_others(tmp_path):
    """covers: M2, A4 — a delta line, frontmatter and a CARD goal. Never a body, never a bind item."""
    root = _bundle(tmp_path)
    hits, note = add.search(root, "gateway")
    assert hits, f"floor: the fixture is full of this term, so an empty result proves nothing — {note}"

    goal, _ = add.search(root, "the alpha goal")
    assert "/tasks/alpha.md#card" in _addresses(goal), f"a CARD goal line must hit — {goal}"
    assert "/index.md" not in _addresses(goal), (
        "index.md is COMPILED from the nodes; searching it doubles every title hit")

    source, _ = add.search(root, "gateway-lens.md")
    assert [h for h in source if h[1] == "sources"], (
        f"a Persona's populated `sources:` is a live facet and must hit — {source}")

    for token, why in ((BODY_TOKEN, "a term living only in a node BODY"),
                       (BIND_TOKEN, "a `Decisions that bind` item — deliberately out of scope")):
        planted, _ = add.search(root, token)
        assert planted == [], f"{why} must not hit — {planted}"
    text = (root / "specs" / "method.md").read_text(encoding="utf-8")
    assert BIND_TOKEN in text and BODY_TOKEN in (root / "tasks" / "alpha.md").read_text("utf-8"), \
        "floor: both withheld tokens must actually be in the bundle, or the checks above are vacuous"

    # Every declared field class must be reachable — a class that never hits is a dead facet.
    titled, _ = add.search(root, "Alpha")
    assert [h for h in titled if h[0] == "/tasks/alpha.md" and h[1] == "title"], (
        f"a node title must hit — {titled}")
    reached = ({h[1].partition(":")[0] for h in hits} | {h[1] for h in goal}
               | {h[1] for h in source} | {h[1] for h in titled})
    assert {"delta", "goal", "title", "description", "sources"} <= reached, \
        f"a declared field class produced no hit anywhere in the fixture — {sorted(reached)}"


# ------------------------------------------------------------------ M3 · literal, case-insensitive

def test_search_matches_are_case_insensitive_and_literal(tmp_path):
    """covers: M3, E3 — the query is text; a metacharacter is a character."""
    root = _bundle(tmp_path)
    lower, _ = add.search(root, "gateway lesson filed in september")
    upper, _ = add.search(root, "GATEWAY Lesson Filed In September")
    assert lower and lower == upper, f"matching must be case-insensitive — {lower} vs {upper}"

    # The fixture plants `gateway.*lesson` VERBATIM in exactly one delta. A literal matcher finds
    # that one; a compiled pattern would also match "gateway lesson", of which there are four.
    meta, note = add.search(root, "gateway.*lesson")
    assert len(meta) == 1, (
        f"a metacharacter query must match LITERALLY — one planted delta, not a compiled "
        f"pattern's four — {_addresses(meta)} / {note}")
    assert meta[0][0] == "/specs/method.md#M6", meta

    bracket, note = add.search(root, "[ADD")
    assert bracket is not None, f"an unbalanced bracket must not raise — {note}"


# ------------------------------------------------------------------ M4 · total, byte-stable order

def test_search_output_is_byte_stable_and_totally_ordered(tmp_path):
    """covers: M4, A11, A12 — every tie broken, so the listing is diffable."""
    root = _bundle(tmp_path)
    first_hits, first = add.search(root, "gateway")
    second_hits, second = add.search(root, "gateway")
    assert first == second and first_hits == second_hits, \
        "two searches over an unchanged bundle must emit byte-identical output"

    tiers = [add.SEARCH_TIERS[h[1].partition(":")[0]] for h in first_hits]
    assert len(set(tiers)) >= 3, (
        "floor: the fixture must produce hits in at least three distinct field tiers, or the "
        f"ordering assertion below is about a single group — {list(zip(tiers, _addresses(first_hits)))}")
    assert tiers == sorted(tiers), f"hits are not grouped by field tier — {list(zip(tiers, first_hits))}"

    statuses = [h[1] for h in first_hits if h[1].startswith("delta:")]
    assert set(statuses) == {"delta:open", "delta:folded", "delta:rejected"}, (
        f"floor: the fixture must carry all three delta statuses — {sorted(set(statuses))}")
    assert statuses == sorted(statuses, key=lambda s: add.DELTA_STATUSES.index(s.partition(":")[2])), \
        f"open must rank before folded before rejected — {statuses}"

    opens = [h for h in first_hits if h[1] == "delta:open"]
    assert len(opens) > 1, f"floor: several open deltas must match, or ordering proves nothing — {opens}"
    assert opens[0][0] == "/specs/method.md#M2", (
        f"within `open`, the newest validity-interval start comes first — {[h[0] for h in opens]}")

    # A12 — a tag list renders in AUTHORED order, never sorted: a re-sort churns the frontmatter.
    assert ["registry", "gate"] != sorted(["registry", "gate"]), \
        "fixture setup: the authored tag order must differ from the sorted order"
    tags_hit, _ = add.search(root, "registry")
    snippet = next(h[2] for h in tags_hit if h[0] == "/specs/method.md" and h[1] == "tags")
    assert snippet.index("registry") < snippet.index("gate"), \
        f"the tags facet was re-sorted; the authored order must survive — {snippet!r}"


# ------------------------------------------------------------------ M5 · --as-of

def test_search_as_of_reports_the_status_a_delta_held_then(tmp_path):
    """covers: M5, A6, E4 — the half-open interval `deltas()` already implements."""
    root = _bundle(tmp_path)
    on_close, _ = add.search(root, "gateway lesson folded", as_of="2026-09-01")
    assert [h[1] for h in on_close] == ["delta:folded"], (
        "the interval is half-open [from, to): a delta folded ON this date was not asserted "
        f"that day — {on_close}")

    day_before, _ = add.search(root, "gateway lesson folded", as_of="2026-08-31")
    assert [h[1] for h in day_before] == ["delta:open"], (
        f"the day before its close it still held `open` — {day_before}")

    early, note = add.search(root, "gateway", as_of="2026-01-01")
    assert not [h for h in early if h[1].startswith("delta:") and "legacy" not in h[2]], (
        f"no dated delta had started by this date — {early}")
    assert early, "the hits with no validity interval must survive an early --as-of, not vanish"
    assert "no validity interval" in note, note


def test_search_counts_interval_free_hits_exactly_once(tmp_path):
    """covers: R:SILENT_DROP, A7 — a smaller number reads as success, and so does a trebled one.

    `deltas()` increments its own `undated` counter BEFORE its status filter, so a caller that
    invokes it once per status and reuses that counter reports 3x the truth. This pins the
    literal, and the second half proves the check red by WITHHOLDING its subject.
    """
    root = _bundle(tmp_path)
    unfiltered, _ = add.search(root, UNDATED)
    assert len(unfiltered) == 3, (
        f"floor: the fixture plants two legacy undated lines and one dated decoy — {unfiltered}")

    filtered, note = add.search(root, UNDATED, as_of="2026-09-30")
    assert len(filtered) == 3, f"--as-of dropped an interval-free hit — {filtered}"
    assert sum(1 for h in filtered if "legacy" in h[2]) == 2, filtered
    footer = next((ln for ln in note.splitlines() if "no validity interval" in ln), None)
    assert footer, f"a filtered listing with unjudgeable hits must carry the footer — {note}"
    assert footer.startswith("\u2014 2 hit"), (
        "the footer must state exactly the two interval-free hits — a trebled count is what "
        f"reusing `deltas()`'s own undated counter produces — {footer!r}")

    # Withhold the subject: with no undated lines there is nothing the filter cannot judge.
    bare = _bundle(tmp_path / "bare", legacy=False)
    _bare_hits, bare_note = add.search(bare, UNDATED, as_of="2026-09-30")
    assert "no validity interval" not in bare_note, (
        f"the footer must be ABSENT when every hit is datable — {bare_note}")


# ------------------------------------------------------------------ M6 · a live, non-empty facet

def test_the_live_specs_carry_tags_that_search_matches():
    """covers: M6, A9, A14, A15 — against the REAL bundle: a facet over an empty field ships dead."""
    assert LIVE.is_dir(), f"the live bundle is the subject of this check, and it is missing: {LIVE}"
    specs = sorted((LIVE / "specs").glob("*.md"))
    assert len(specs) == 5, f"expected the five living specs, found {[p.name for p in specs]}"

    for path in specs:
        fm = add.read(path, "T0")["fm"] or {}
        tags = fm.get("tags") or []
        assert isinstance(tags, list) and tags, (
            f"{path.name}: `tags:` is empty, so every tag facet over it matches nothing "
            "— a populated field is what makes the facet real")

        # A14/A15 — a tag nobody would type is a tag nobody matches. Every tag must be a word
        # this spec's own text already carries; the day the vocabulary drifts past the taxonomy,
        # this reds instead of decaying silently.
        elsewhere = "\n".join(ln for ln in path.read_text(encoding="utf-8").splitlines()
                              if not ln.startswith("tags:"))
        for tag in tags:
            assert str(tag).lower() in elsewhere.lower(), (
                f"{path.name}: the tag `{tag}` appears nowhere in the spec's own description, "
                "`## Now` or deltas — it is an invented taxonomy, not the corpus vocabulary")
            hits, note = add.search(LIVE, str(tag))
            assert [h for h in hits or [] if h[0] == f"/specs/{path.stem}.md" and h[1] == "tags"], (
                f"{path.name}: a query for its own tag `{tag}` does not return it on the tags "
                f"field — the facet is populated and still dead — {note[:400]}")

    # A9 — the empty-facet reading is honest, proved on a fixture because no live spec is empty.
    assert add.read(LIVE / "specs" / "method.md", "T0")["fm"].get("sources") is not None, \
        "`sources:` must stay a declared slot even when this bundle has nothing honest to put in it"


def test_an_empty_tag_facet_contributes_no_hit(tmp_path):
    """covers: A9 — an absent value is not an empty-string match that every query contains."""
    root = _bundle(tmp_path)
    hits, note = add.search(root, "gateway spec with no tags")
    assert [h for h in hits if h[0] == "/specs/quality.md" and h[1] == "description"], (
        f"floor: the empty-facet spec must be reachable by its description — {note}")
    assert not [h for h in hits if h[0] == "/specs/quality.md" and h[1] == "tags"], (
        f"a spec with `tags: []` must contribute no tags hit — {hits}")


# ------------------------------------------------------------------ M7 · FORMAT §4

def test_format_section_four_bounds_the_reads_the_engine_performs(tmp_path):
    """covers: M7, A16 — measured, not asserted from a hand list.

    §4's absolute ("no operation may read the full body of more than the one node it was asked
    about") was already false in five shipped sites when it was written, and FORMAT's own
    preamble makes that a defect to report rather than an exception to carve for a sixth. The
    repair keeps the BRIEF's absolute and states four conditions — so this counts real T2 reads
    per verb and requires every multi-node reader to be named there.
    """
    text = (REPO / "FORMAT.md").read_text(encoding="utf-8")
    section = text[text.index("## §4 Read tiers"):text.index("## §5 The Task body")]
    assert len(section) > 800, (
        "floor: §4 was gutted rather than repaired — a denylist satisfied by DELETING the "
        "paragraph makes the document shorter and worse (/specs/system.md#S2, R:NEUTERED)")

    assert "no operation may read the full body of more than the one node it was asked about" \
        not in section, (
            "§4 still asserts an absolute that five shipped sites break; the format must state "
            "the rule the engine implements")
    for condition in ("bounded", "lazy", "cache", "extraction"):
        assert condition in section.lower(), \
            f"§4 does not state the `{condition}` condition a multi-node T2 read must meet"
    assert "brief" in section and "T0" in section, \
        "§4 must still bind the brief to a single T2 and keep `status` at T0"
    assert "`join`" in section and "write" in section.lower(), \
        "§4 must name `join` separately: it copies node BYTES between bundles and parses none"

    # ---- the measurement: distinct T2 paths read per verb, against a real fixture bundle.
    root = _bundle(tmp_path)
    seen, real_read = {}, add.read

    def counting(path, tier="T0"):
        if tier == "T2":
            seen.setdefault(counting.verb, set()).add(str(path))
        return real_read(path, tier)

    graph = add.scan(root)
    probes = {"status": lambda: add.status(root), "locate": lambda: add.locate(root, "x"),
              "todo": lambda: add.todo(root), "deltas": lambda: add.deltas(root),
              "bind_sections": lambda: add.bind_sections(root),
              "doctor": lambda: add.doctor(root, graph),
              "search": lambda: add.search(root, "gateway"),
              "brief": lambda: add.brief(root, "/tasks/alpha.md")}
    add.read = counting
    try:
        for name, call in probes.items():
            counting.verb = name
            call()
    finally:
        add.read = real_read

    specs = {str(q) for q in (root / "specs").glob("*.md")}
    assert seen.get("brief"), "floor: the brief probe measured no T2 read at all"
    assert seen["brief"] - specs == {str(root / "tasks" / "alpha.md")}, (
        "`brief` composes exactly ONE whole body — its subject. Every other T2 it touches is a "
        "spec read through `bind_sections`, which yields a bounded extraction (§7.1) — "
        f"it read {sorted(Path(q).name for q in seen['brief'])}")
    assert not seen.get("status"), f"`status` must stay at T0 — it read {seen.get('status')}"
    multinode = {name for name, paths in seen.items() if len(paths) > 1}
    assert multinode, "floor: the probe measured no multi-node reader at all, so it proves nothing"
    for name in sorted(multinode):
        assert f"`{name}`" in section, (
            f"`{name}` read {len(seen[name])} distinct T2 bodies in one call and §4 does not "
            "name it — the format is describing an engine it does not have")


# ------------------------------------------------------------------ M9 · every branch teaches

def test_search_next_lines_name_a_real_verb(tmp_path):
    """covers: M9, A13 — law 4, on every branch; and the address is pasteable as it stands."""
    import re
    import cli as cli_mod
    verbs = set(cli_mod.build_parser()._subparsers._group_actions[0].choices)
    root = _bundle(tmp_path)

    notes = {
        "hit": add.search(root, "gateway")[1],
        "no hit": add.search(root, "nothing matches this at all")[1],
        "blank": add.search(root, "   ")[1],
        "bad date": add.search(root, "gateway", as_of="last tuesday")[1],
    }
    for branch, note in notes.items():
        last = note.strip().splitlines()[-1]
        assert last.startswith("next:"), f"{branch}: the note does not end in a `next:` — {note!r}"
        named = re.findall(r"\badd ([a-z][a-z-]*)", last)
        assert named, f"{branch}: `{last}` names no `add <verb>`"
        for verb in named:
            assert verb in verbs, f"{branch}: `{verb}` is not an engine verb — {last!r}"

    # A13 — the address is the deliverable, so it must resolve through the ENGINE's own resolver
    # (§3.3 puts a delta id third, behind frontmatter keys and heading slugs; a regex shape check
    # would be the plausible-but-wrong version of this assertion).
    hits, _ = add.search(root, "filed in september")
    _cid, value, why = add.resolve(add.scan(root), hits[0][0], src="/specs/method.md")
    assert why == "delta" and value, (
        f"an emitted address must resolve as a relations target, verbatim — {hits[0][0]} ({why})")


# ------------------------------------------------------------------ R:BODYLEAK

def test_a_four_thousand_character_delta_yields_a_bounded_line(tmp_path):
    """covers: R:BODYLEAK, E1 — a search that prints what it read is a cost, not a lookup."""
    root = _bundle(tmp_path)
    assert len(HUGE_TEXT) == 4000, "fixture setup: the oversized delta must actually be oversized"
    hits, note = add.search(root, "leviathan")
    assert "/specs/method.md#M4" in _addresses(hits), (
        f"floor: the 4000-character delta must still be FOUND, or the bound below is vacuous — {note}")

    snippet = next(h[2] for h in hits if h[0] == "/specs/method.md#M4")
    assert len(snippet) <= add.SEARCH_SNIPPET + 2, (
        f"the snippet is {len(snippet)} characters, past the {add.SEARCH_SNIPPET} budget")
    assert "…" in snippet, "an elided snippet must say so"
    assert HUGE_TEXT.strip() not in note, "the delta's whole text rode out in the listing"
    for line in note.splitlines():
        assert len(line) <= 300, f"an emitted line ran to {len(line)} characters: {line[:120]!r}"


# ------------------------------------------------------------------ R:EMPTYQUERY · R:TODAYFALLBACK

def test_a_blank_query_refuses_instead_of_matching_everything(tmp_path):
    """covers: R:EMPTYQUERY, A8 — an empty substring is inside every string."""
    root = _bundle(tmp_path)
    for blank in ("", "   ", "\t"):
        hits, note = add.search(root, blank)
        assert hits is None, (
            f"a blank query answered with {len(hits or [])} hits instead of refusing — {note}")
        assert "EMPTYQUERY" in note, note
    assert _cli(root, "").returncode == 1, "a refusal is exit 1, not a silent success"


def test_an_unreadable_as_of_refuses_and_never_falls_back_to_today(tmp_path):
    """covers: R:TODAYFALLBACK — today would answer a question nobody asked."""
    root = _bundle(tmp_path)
    hits, note = add.search(root, "gateway", as_of="09/01/2026")
    assert hits is None, f"a malformed date must refuse, not list — {note}"
    assert "TODAYFALLBACK" in note and "add search" in note, note
    assert "/specs/method.md" not in note, "a refusal must not also emit a listing"
    assert "add deltas" not in note, (
        "the refusal must name `add search`, the verb the operator ran — a bare delegation to "
        f"`deltas()` emits its refusal instead — {note}")

    proc = _cli(root, "gateway", "--as-of", "09/01/2026")
    assert proc.returncode == 1, proc.stdout + proc.stderr


def test_a_no_hit_search_is_a_recorded_outcome(tmp_path):
    """covers: E2 — law 3: a failing lookup is a recorded outcome, not an exception."""
    root = _bundle(tmp_path)
    hits, note = add.search(root, "nothing matches this at all")
    assert hits is not None, "None marks a REFUSAL and only a refusal; a no-hit is an empty list"
    assert hits == [], f"a no-hit search returns an empty list — {hits}"
    assert 'no hit for "nothing matches this at all"' in note, note

    proc = _cli(root, "nothing matches this at all")
    assert proc.returncode == 0, f"a search with no hit exits 0 — {proc.stdout}{proc.stderr}"
    assert "no hit" in proc.stdout, proc.stdout


# ------------------------------------------------------------------ A1 · A3 · what search must not touch

def test_search_never_writes_and_never_reads_a_run_receipt(tmp_path):
    """covers: A1, A3 — read-only, and 115 near-identical receipts never bury the concepts."""
    import hashlib
    root = _bundle(tmp_path)
    before = {p: hashlib.md5(p.read_bytes()).hexdigest() for p in sorted(root.rglob("*.md"))}
    assert before, "fixture setup: the bundle must have files to compare"

    receipt, note = add.search(root, RECEIPT_TOKEN)
    assert receipt == [], (
        f"a Run receipt is evidence, not a concept — searching it buries the concepts — {receipt}")
    assert RECEIPT_TOKEN in (root / "tasks" / "alpha.d" / "runs" / "1.md").read_text("utf-8"), \
        "floor: the receipt token must actually be in the bundle, or the check above is vacuous"
    control, _ = add.search(root, "gateway")
    assert control, f"floor: the same bundle must yield hits for a live term — {note}"

    after = {p: hashlib.md5(p.read_bytes()).hexdigest() for p in sorted(root.rglob("*.md"))}
    assert after == before, "search wrote to the bundle; it is a read"


def test_the_cli_wires_search_with_its_flag(tmp_path):
    """covers: M8 — the verb dispatches for real, and its flag reaches the engine."""
    root = _bundle(tmp_path)
    proc = _cli(root, "gateway")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "/specs/method.md#M2" in proc.stdout, proc.stdout

    dated = _cli(root, "gateway lesson folded", "--as-of", "2026-08-31")
    assert dated.returncode == 0 and "delta:open" in dated.stdout, dated.stdout + dated.stderr
