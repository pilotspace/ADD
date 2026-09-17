"""RED contract for a complete, immutable decision manifest at freeze/refreeze.

The current interview digest is intentionally narrower than the approval candidate: it covers
questions, not every declaration the freeze approves.  These checks drive public freeze/interview
behavior and artifacts.  They do not prescribe a private compiler API.
"""
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path


REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


M1 = ("- M1 the freeze records the complete approval candidate "
      "(from: request · fails-on: candidate can be partial)")
M2 = ("- M2 refreeze shows the decision delta "
      "(from: request · fails-on: removed work disappears)")
M2_UNSOURCED = "- M2 refreeze shows the decision delta"
REJECT = '- R:NO_GUESS an omitted item is treated as approved -> "NO_GUESS"'
A1 = ("- A1 [who] covers: S1 S2 · the request does not say who reviews the candidate; "
      "taking per-node review -> a shared approval can hide an unreviewed node")
RETIRED = (
    "- A2 [which] covers: S1 S2 · n/a · the fixture candidate enumerates every class",
    "- A3 [when] covers: S1 S2 · n/a · freeze is the only fixture transition",
    "- A4 [absent] covers: S1 S2 · n/a · absence has a dedicated contract check",
    "- A5 [order] covers: S1 S2 · n/a · authored IDs define order",
    "- A6 [experience] covers: S1 S2 · n/a · the fixture reads the machine artifact",
)
E1 = "- E1 Given one omitted answer · When freeze runs · Then the item remains owed"
E2 = "- E2 Given a removed obligation · When refreeze runs · Then the old row remains visible"


def _bundle(path: Path) -> Path:
    root = path / ".add"
    add.init(root, "code", "decision manifest fixture")
    return root


def _task(root: Path, slug: str, *, security=False, questions=False,
          unsourced_must=False, extra_edge=False):
    cid, note = add.new(
        root, "Task", slug, title=slug, depth="standard" if security else "quick",
        sensitivity="security" if security else "mechanical",
    )
    assert cid, note
    path = root / cid.lstrip("/")
    node = add.read(path, "T2")
    raw = add.set_key(node["raw"], "gives", [
        "S1 approval candidate",
        "S2 refreeze delta",
    ])
    assumptions = [A1 if questions else
                   "- A1 [who] covers: S1 S2 · n/a · the process fixture has no human reviewer",
                   *RETIRED]
    edges = [E1] + ([E2] if extra_edge else [])
    m2 = M2_UNSOURCED if unsourced_must else M2
    covered = ["M1", "M2", "R:NO_GUESS", "E1"] + (["E2"] if extra_edge else [])
    body = "\n".join([
        "## CARD",
        f"goal: freeze {slug}'s decision candidate",
        "why: exercise the decision-manifest contract",
        f"beat: direction · next: add freeze {slug}",
        "",
        "## RULES",
        "<must>", M1, m2, "</must>",
        "<reject>", REJECT, "</reject>",
        "",
        "## ASSUMPTIONS", *assumptions,
        "every surface is swept in this fixture.",
        "",
        "## PLAN",
        "contract: one immutable decision candidate",
        "regression: none · isolated fixture",
        "",
        "## EDGES", *edges,
        "",
        "## CHECKS",
        f"- test_contract · covers: {','.join(covered)} · proves the fixture contract",
        "red-first: the decision artifact does not exist yet.",
        "",
        "## EVIDENCE", "receipt: pending", "gate: pending",
        "",
        "## LESSONS", "none yet", "",
    ])
    add.write(path, f"---\n{raw}\n---\n{body}")
    return cid, path


def _milestone(root: Path, slug: str, criteria):
    cid, note = add.new(root, "Milestone", slug, title=slug,
                        goal=f"make {slug} observable")
    assert cid, note
    path = root / cid.lstrip("/")
    node = add.read(path, "T2")
    boxes = "\n".join(f"- [ ] {criterion}" for criterion in criteria)
    body = (f"## CARD\ngoal: make {slug} observable\nwhy: exercise stable EXIT identities\n"
            f"next: add freeze {slug}\n\n## SCOPE\nIn: decision identity\nOut: build work\n\n"
            f"## GROUND\ntouches: fixture\nrisks:\n  - ordinal identity\n\n"
            f"## EXIT\n{boxes}\n\n## CLOSE\nevidence: pending\n")
    add.write(path, f"---\n{node['raw']}\n---\n{body}")
    return cid, path


def _answer(root: Path, cid: str, answers=None):
    questions, note = add.interview(root, cid)
    assert isinstance(questions, list), note
    supplied = answers if answers is not None else {q["id"]: "confirm" for q in questions}
    node, note = add.interview(root, cid, answers=supplied, by="Human Fixture")
    assert node, note
    return questions


def _freeze(root: Path, cid: str, *, human=False):
    node, note = add.freeze(root, cid, by="human:Fixture" if human else "plan:fixture",
                            authority="human" if human else "plan")
    assert node, note
    return note


def _stamps(root: Path, cid: str):
    fm = add.read(root / cid.lstrip("/"), "T0")["fm"]
    return [s for s in (fm.get("verified") or []) if isinstance(s, dict)]


def _latest_freeze(root: Path, cid: str):
    return next(s for s in reversed(_stamps(root, cid))
                if s.get("act") in ("freeze", "refreeze"))


def _manifest(root: Path, cid: str):
    stamp = _latest_freeze(root, cid)
    claim = str(stamp.get("decisions") or "")
    assert re.fullmatch(r"sha256:[0-9a-f]{64}", claim), (
        f"freeze/refreeze carries no full decision manifest digest: {stamp}")
    assert stamp.get("decision_schema") == 1, stamp
    node_path = root / cid.lstrip("/")
    path = node_path.parent / f"{node_path.stem}.d" / "decisions" / f"{claim[7:]}.json"
    assert path.is_file(), f"claimed decision manifest is missing: {path}"
    raw = path.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == claim[7:], "filename does not address exact bytes"
    assert not raw.endswith(b"\n"), "canonical manifest has a trailing newline"
    doc = json.loads(raw.decode("utf-8"))
    canonical = json.dumps(doc, sort_keys=True, separators=(",", ":"),
                           ensure_ascii=False).encode("utf-8")
    assert raw == canonical, "manifest bytes are not compact sorted-key canonical JSON"
    return stamp, path, raw, doc


def _rewrite(path: Path, old: str, new: str):
    text = path.read_text(encoding="utf-8")
    assert old in text, f"fixture text not found: {old!r}"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def _ids_on_line(note: str, label: str):
    match = re.search(rf"(?im)^\s*{re.escape(label)}\s*:\s*([^\n]+)", str(note))
    assert match, f"no `{label}:` decision line in:\n{note}"
    return set(re.findall(r"R:[A-Z0-9_]+|[A-Z]+[1-9][0-9]*", match.group(1)))


def _walk_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key)
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_keys(child)


def test_manifest_format_and_reorder_are_stable(tmp_path):
    """covers: M1,M2,M3,M4,A5,E1 — formatting/order do not change the candidate."""
    root = _bundle(tmp_path)
    cid, path = _task(root, "stable", extra_edge=True)
    _freeze(root, cid)
    first_stamp, first_path, first_raw, first_doc = _manifest(root, cid)

    _rewrite(path, M1 + "\n" + M2, M2 + "  \n\n" + M1)
    _rewrite(path, E1 + "\n" + E2, E2 + "  \n" + E1)
    _rewrite(path, RETIRED[0] + "\n" + RETIRED[1], RETIRED[1] + "\n" + RETIRED[0])
    _freeze(root, cid)
    second_stamp, second_path, second_raw, second_doc = _manifest(root, cid)

    assert second_stamp["act"] == "refreeze"
    assert first_stamp["decisions"] == second_stamp["decisions"]
    assert (first_path, first_raw, first_doc) == (second_path, second_raw, second_doc)
    assert len(list(first_path.parent.glob("*.json"))) == 1


def test_substantive_change_moves_digest_and_keeps_old_snapshot(tmp_path):
    """covers: M1,M4,A3,A5,E1 — real text moves the content address; history stays immutable."""
    root = _bundle(tmp_path)
    cid, path = _task(root, "moves")
    _freeze(root, cid)
    first_stamp, first_path, first_raw, _ = _manifest(root, cid)

    _rewrite(path, "complete approval candidate", "complete identified approval candidate")
    _freeze(root, cid)
    second_stamp, second_path, _, _ = _manifest(root, cid)

    assert first_stamp["decisions"] != second_stamp["decisions"]
    assert first_path != second_path and first_path.read_bytes() == first_raw
    assert sorted(p.name for p in first_path.parent.glob("*.json")) == sorted(
        [first_path.name, second_path.name])


def test_task_candidate_refuses_missing_and_duplicate_ids(tmp_path):
    """covers: M3,R:MISSING_DECISION_ID,R:DUPLICATE_DECISION_ID,E2 — all five Task classes."""
    root = _bundle(tmp_path)
    missing = [
        ("s", None, None),
        ("m", M1, M1.replace("- M1 ", "- ", 1)),
        ("r", REJECT, REJECT.replace("- R:NO_GUESS ", "- ", 1)),
        ("a", "- A1 [who]", "- [who]"),
        ("e", E1, E1.replace("- E1 ", "- ", 1)),
    ]
    duplicate = [
        ("s", None, None),
        ("m", M2, M2.replace("- M2 ", "- M1 ", 1)),
        ("r", REJECT, REJECT + "\n" + REJECT),
        ("a", RETIRED[0], RETIRED[0] + "\n" + RETIRED[0]),
        ("e", E1, E1 + "\n" + E1),
    ]
    failures = []
    for mode, cases, code in (("missing", missing, "R:MISSING_DECISION_ID"),
                              ("duplicate", duplicate, "R:DUPLICATE_DECISION_ID")):
        for kind, old, new in cases:
            cid, path = _task(root, f"{mode}-{kind}")
            if kind == "s":
                node = add.read(path, "T2")
                gives = (["approval candidate", "S2 refreeze delta"] if mode == "missing"
                         else ["S1 approval candidate", "S1 refreeze delta"])
                add.write(path, f"---\n{add.set_key(node['raw'], 'gives', gives)}\n---\n{node['body']}")
            else:
                _rewrite(path, old, new)
            before = len(_stamps(root, cid))
            node, note = add.freeze(root, cid, by="plan:fixture", authority="plan")
            if node is not None or code not in str(note) or len(_stamps(root, cid)) != before:
                failures.append(f"{mode} {kind}: node={bool(node)} note={note!r}")
    assert failures == [], "decision ID refusals missed:\n" + "\n".join(failures)


def test_milestone_candidate_refuses_missing_and_duplicate_c_ids(tmp_path):
    """covers: M3,R:MISSING_DECISION_ID,R:DUPLICATE_DECISION_ID,E5 — C ids are authored."""
    root = _bundle(tmp_path)
    failures = []
    for slug, criteria, code in (
        ("missing-c", ["criterion one", "C2 criterion two"], "R:MISSING_DECISION_ID"),
        ("duplicate-c", ["C1 criterion one", "C1 criterion two"], "R:DUPLICATE_DECISION_ID"),
    ):
        cid, _ = _milestone(root, slug, criteria)
        before = len(_stamps(root, cid))
        node, note = add.freeze(root, cid, by="plan:fixture", authority="plan")
        if node is not None or code not in str(note) or len(_stamps(root, cid)) != before:
            failures.append(f"{slug}: node={bool(node)} note={note!r}")
    assert failures == [], "Milestone C identity refusals missed:\n" + "\n".join(failures)


def test_complete_candidate_and_question_subset_have_exact_rows(tmp_path):
    """covers: M2,M3,M5,A2,E2 — complete candidate and question projection stay distinct."""
    root = _bundle(tmp_path)
    cid, _ = _task(root, "complete", questions=True, unsourced_must=True, extra_edge=True)
    _freeze(root, cid)
    _, _, _, doc = _manifest(root, cid)

    expected = ["S1", "S2", "M1", "M2", "R:NO_GUESS",
                "A1", "A2", "A3", "A4", "A5", "A6", "E1", "E2"]
    assert doc["decision_schema"] == 1 and doc["node"] == cid
    assert [row["id"] for row in doc["decisions"]] == expected
    by_id = {row["id"]: row for row in doc["decisions"]}
    row_keys = {"id", "kind", "declaration", "declaration_digest", "sources", "examples",
                "required_authority", "proposed_reading", "ask_required"}
    assert all(set(row) == row_keys for row in doc["decisions"])
    for row in doc["decisions"]:
        want = "sha256:" + hashlib.sha256(row["declaration"].encode("utf-8")).hexdigest()
        assert row["declaration_digest"] == want
    assert doc["question_ids"] == ["M2", "R:NO_GUESS", "A1", "E1", "E2"]
    assert by_id["M1"]["sources"] == ["request"]
    assert by_id["M1"]["examples"] == ["candidate can be partial"]
    assert by_id["M1"]["ask_required"] is False
    assert by_id["M2"]["sources"] == [] and by_id["M2"]["ask_required"] is True
    assert by_id["A1"]["proposed_reading"] == "per-node review"
    assert by_id["A2"]["ask_required"] is False and by_id["A2"]["proposed_reading"] is None
    assert by_id["E1"]["examples"] and by_id["E1"]["ask_required"] is True
    assert {row["required_authority"] for row in doc["decisions"]} == {"process"}


def test_answers_never_enter_manifest_and_sparse_verdicts_keep_their_meaning(tmp_path):
    """covers: M2,M5,R:DECISION_ANSWER,R:UNINTERVIEWED,E3 — explicit answers stay separate."""
    root = _bundle(tmp_path)
    cid, _ = _task(root, "answers", security=True, questions=True)
    questions, _ = add.interview(root, cid)
    ids = [q["id"] for q in questions]
    assert len(ids) == 3, ids

    _answer(root, cid, {ids[0]: "confirm"})
    _answer(root, cid, {ids[1]: "defer", ids[2]: "correct"})
    node = add.read(root / cid.lstrip("/"), "T2")
    assert add.interview_gap(node, add.read(root / cid.lstrip("/"), "T0")["fm"]) == [ids[2]]
    _answer(root, cid, {ids[2]: "defer"})
    node = add.read(root / cid.lstrip("/"), "T2")
    assert add.interview_gap(node, add.read(root / cid.lstrip("/"), "T0")["fm"]) == []
    _freeze(root, cid, human=True)
    _, _, raw, doc = _manifest(root, cid)

    forbidden = {"answer", "answers", "answered", "verdict", "signer", "persona"}
    assert forbidden.isdisjoint({key.lower() for key in _walk_keys(doc)})
    assert not any(word in raw.decode("utf-8") for word in ("confirm", "correct", "defer"))
    assert set(doc["question_ids"]) == set(ids)


def test_stale_interview_is_whole_set_while_candidate_delta_is_per_row(tmp_path):
    """covers: M5,M6,A6,E4 — row equality never revives a whole stale interview."""
    root = _bundle(tmp_path)
    cid, path = _task(root, "stale", security=True, questions=True)
    original_questions = _answer(root, cid)
    _freeze(root, cid, human=True)
    _manifest(root, cid)

    _rewrite(path, "taking per-node review", "taking named-owner review")
    node = add.read(path, "T2")
    gap = add.interview_gap(node, add.read(path, "T0")["fm"])
    assert gap == [q["id"] for q in original_questions], gap
    _, note = add.interview(root, cid)
    assert _ids_on_line(note, "changed") == {"A1"}
    unchanged = _ids_on_line(note, "unchanged")
    assert {"E1", "R:NO_GUESS"}.issubset(unchanged)
    assert _ids_on_line(note, "stale") == set(gap)


def test_refreeze_keeps_added_removed_and_unchanged_obligations_visible(tmp_path):
    """covers: M1,M6,A3,E5 — a removed row survives in the old content-addressed snapshot."""
    root = _bundle(tmp_path)
    cid, path = _task(root, "delta", extra_edge=True)
    _freeze(root, cid)
    _, old_path, _, old_doc = _manifest(root, cid)

    _rewrite(path, "complete approval candidate", "complete named approval candidate")
    _rewrite(path, E2 + "\n", "")
    _rewrite(path, RETIRED[-1], RETIRED[-1] + "\n- A7 [which] n/a · an added declaration")
    _, preview = add.interview(root, cid)
    assert _ids_on_line(preview, "added") == {"A7"}
    assert _ids_on_line(preview, "changed") == {"M1"}
    assert _ids_on_line(preview, "removed") == {"E2"}
    assert {"S1", "S2", "M2"}.issubset(_ids_on_line(preview, "unchanged"))

    note = _freeze(root, cid)
    assert _ids_on_line(note, "added") == {"A7"}
    assert _ids_on_line(note, "removed") == {"E2"}
    _, new_path, _, new_doc = _manifest(root, cid)
    assert old_path != new_path and old_path.is_file()
    assert "E2" in {row["id"] for row in old_doc["decisions"]}
    assert "E2" not in {row["id"] for row in new_doc["decisions"]}
    assert "A7" in {row["id"] for row in new_doc["decisions"]}


def _strip_decision_claim(path: Path):
    text = path.read_text(encoding="utf-8")
    text = re.sub(r', decisions: "sha256:[0-9a-f]{64}", decision_schema: 1(?= \})',
                  "", text, count=1)
    path.write_text(text, encoding="utf-8")


def _append_claim(root: Path, cid: str, digest: str):
    path = root / cid.lstrip("/")
    node = add.read(path, "T2")
    stamp = (f'{{ by: "plan:fixture", at: 2026-09-16, act: refreeze, authority: plan, '
             f'direction: "{add.direction_digest(node)}", binding: "{add.binding_digest(node)}", '
             f'gives: "{add.gives_digest(node)}", decisions: "sha256:{digest}", '
             f'decision_schema: 1 }}')
    written, note = add._transition(root, cid, appends=[("verified", stamp)])
    assert written, note


def test_legacy_is_unknown_but_missing_or_malformed_claim_refuses(tmp_path):
    """covers: M7,R:DECISION_MANIFEST,A4,E6 — unknown history is not corrupt claimed history."""
    problems = []

    legacy_root = _bundle(tmp_path / "legacy")
    legacy_cid, legacy_path = _task(legacy_root, "legacy")
    _freeze(legacy_root, legacy_cid)
    _strip_decision_claim(legacy_path)
    shutil.rmtree(legacy_path.parent / "legacy.d" / "decisions", ignore_errors=True)
    _rewrite(legacy_path, "complete approval candidate", "complete current approval candidate")
    node, note = add.freeze(legacy_root, legacy_cid, by="plan:fixture", authority="plan")
    if node is None or "unknown" not in str(note).lower():
        problems.append(f"legacy baseline was not reported unknown: node={bool(node)} note={note!r}")
    elif not _latest_freeze(legacy_root, legacy_cid).get("decisions"):
        problems.append("legacy refreeze wrote no full decision baseline")

    for mode in ("missing", "malformed"):
        root = _bundle(tmp_path / mode)
        cid, path = _task(root, mode)
        _freeze(root, cid)
        digest = ("1" if mode == "missing" else "2") * 64
        _append_claim(root, cid, digest)
        if mode == "malformed":
            target = path.parent / f"{path.stem}.d" / "decisions" / f"{digest}.json"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text("{", encoding="utf-8")
        before = len(_stamps(root, cid))
        node, note = add.freeze(root, cid, by="plan:fixture", authority="plan")
        if node is not None or "R:DECISION_MANIFEST" not in str(note) \
                or len(_stamps(root, cid)) != before:
            problems.append(f"{mode} claim did not refuse atomically: node={bool(node)} note={note!r}")

    assert problems == [], "\n".join(problems)


def test_security_interviews_and_manifests_remain_per_node(tmp_path):
    """covers: M4,M8,R:UNINTERVIEWED,A1,E7 — completeness never transfers authority."""
    root = _bundle(tmp_path)
    first, _ = _task(root, "security-one", security=True, questions=True)
    second, second_path = _task(root, "security-two", security=True, questions=True)

    _answer(root, first)
    _freeze(root, first, human=True)
    node, note = add.freeze(root, second, by="human:Fixture", authority="human")
    assert node is None and "R:UNINTERVIEWED" in str(note), note
    assert not (second_path.parent / "security-two.d" / "decisions").exists()

    _answer(root, second)
    _freeze(root, second, human=True)
    first_stamp, first_path, _, first_doc = _manifest(root, first)
    second_stamp, second_manifest, _, second_doc = _manifest(root, second)
    assert first_path != second_manifest
    assert first_stamp["decisions"] != second_stamp["decisions"]
    assert first_doc["node"] == first and second_doc["node"] == second
    assert second not in first_path.read_text(encoding="utf-8")
