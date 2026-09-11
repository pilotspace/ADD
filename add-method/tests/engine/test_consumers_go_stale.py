"""Red suite for `consumers-go-stale` — a refreeze that moves a gives: marks every consumer stale.

Four shipped sentences promised that dependents citing a moved `#gives` are "flagged stale" and
cited a FORMAT §3.5 that was never written; the refreeze branch wrote one stamp and told nobody.
Now every freeze stamp carries `gives: <sha>` and, on a consumer, `needs: "<target>#gives=<sha8>"`;
`doctor` emits `needs_stale`, `todo` hints it, the refreeze note names the consumers, and a
rung-bound consumer's `gate PASS` refuses R:STALENEEDS until it re-crosses. Digests, never dates.

Driven as `.add/tasks/consumers-go-stale.md` under milestone `loop-that-closes`.
"""
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

DIMS = ("who", "which", "when", "absent", "order", "experience")
JUNIT = "<testsuite><testcase classname='t' name='test_only_own_rows'/></testsuite>"


def git(*args, cwd):
    subprocess.run(["git", "-c", "user.email=t@e.c", "-c", "user.name=T", *args],
                   cwd=str(cwd), capture_output=True, text=True, check=True)


def _authored(root, slug, gives="the lister", **fields):
    cid, _ = add.new(root, "Task", slug, title=slug, **fields)
    p = root / cid.lstrip("/")
    t = p.read_text(encoding="utf-8")
    t = t.replace("- S1 <the surface this publishes — an endpoint, function, or section>", f"- S1 {gives}")
    t = t.replace("goal: <one line>", "goal: the lister lists only the caller's rows.")
    t = re.sub(r"## RULES\n<must>\n.*?\n</must>",
               "## RULES\n<must>\n- M1 the lister returns only the caller's rows\n</must>", t, flags=re.S)
    t = re.sub(r"<reject>\n.*?\n</reject>", '<reject>\n- R:R1 thing 1 happens -> "R1"\n</reject>', t, flags=re.S)
    lines = "".join(f"- A{i} [{d}] covers: S1 · the request does not say thing {i}; taking reading {i} -> cost {i}\n"
                    for i, d in enumerate(DIMS, 1))
    t = re.sub(r"## ASSUMPTIONS\n.*?\nevery `gives:`", "## ASSUMPTIONS\n" + lines + "every `gives:`", t, flags=re.S)
    t = re.sub(r"## CHECKS\n.*?(?=\n## )",
               "## CHECKS\n- test_only_own_rows · covers: M1, R:R1 · acceptance · proves isolation\nred-first: every check MUST fail first.\n", t, flags=re.S)
    t = re.sub(r"## PLAN\n.*?\n\n", "## PLAN\ncontract: the lister\nregression: none · fixture\n\n", t, flags=re.S)
    p.write_text(t, encoding="utf-8")
    return cid


def _set_gives(root, cid, text):
    p = root / cid.lstrip("/")
    p.write_text(re.sub(r"^  - S1 .*$", f"  - S1 {text}", p.read_text(), count=1, flags=re.M))


def _stamp(root, cid, act=("freeze", "refreeze")):
    stamps = add.scan(root)[cid]["fm"]["verified"]
    return [s for s in stamps if s.get("act") in act][-1]


@pytest.fixture
def pair(tmp_path):
    """Provider P (frozen) and consumer C (`needs: [/tasks/p.md#gives]`, frozen), in a git repo."""
    git("init", "-q", cwd=tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x = 1\n")
    git("add", "src/a.py", cwd=tmp_path)
    git("commit", "-q", "-m", "one", cwd=tmp_path)
    bundle = tmp_path / ".add"
    add.init(bundle, "code", "P")
    p = _authored(bundle, "p", gives="auth.verify(token) -> Claims", sensitivity="mechanical")
    assert add.freeze(bundle, p, by="plan")[0] is not None
    c = _authored(bundle, "c", sensitivity="architecture", scope=["src/a.py"], needs=["/tasks/p.md#gives"])
    assert add.freeze(bundle, c, by="plan", authority="plan")[0] is not None
    return tmp_path, bundle, p, c


def _move_provider(bundle, p):
    _set_gives(bundle, p, "auth.verify(token, aud) -> Claims")
    return add.freeze(bundle, p, by="plan")


def _to_verify(root, bundle, c):
    add.brief_stamp(bundle, c)
    report = root / "r.xml"
    cmd = [sys.executable, "-c", f"open({str(report)!r},'w').write({JUNIT!r})"]
    assert add.run(bundle, c, cmd, cwd=root, junit=report)["receipt"]["exit"] == 0
    assert add.refute(bundle, c, by="fresh", held=True, probes=1, tier="T2")[0] is not None


def test_freeze_stamp_pins_gives_and_needs(pair):
    """covers: M1, A2 (probe) — both keys land; a #findings need pins `?`."""
    _, bundle, p, c = pair
    ps, cs = _stamp(bundle, p), _stamp(bundle, c)
    assert re.fullmatch(r"(sha256:)?[0-9a-f]{16,64}", str(ps.get("gives") or "")), f"provider stamp pins no gives digest: {ps}"
    assert str(cs.get("needs") or "").startswith("/tasks/p.md#gives=") and str(ps["gives"]).split(":")[-1][:8] in str(cs["needs"]), \
        f"consumer stamp pins nothing: {cs}"
    x = _authored(bundle, "x", sensitivity="mechanical", needs=["/tasks/p.md#findings"])
    add.freeze(bundle, x, by="plan")
    assert _stamp(bundle, x).get("needs") == "/tasks/p.md#findings=?", "a non-gives need was pinned as a contract"


def test_refreeze_with_moved_gives_names_consumers(pair):
    """covers: M2, E1, E3 — the note lists C exactly when the digest moved."""
    _, bundle, p, c = pair
    node, note = add.freeze(bundle, p, by="plan")             # unchanged gives
    assert node is not None and "/tasks/c.md" not in note and "stale" not in note, f"an unmoved refreeze named a consumer: {note!r}"
    node, note = _move_provider(bundle, p)
    assert node is not None
    assert "c" in note and "stale" in note and "add freeze c" in note, f"the moved refreeze did not name its consumer: {note!r}"


def test_doctor_reports_needs_stale(pair):
    """covers: M3, E2, E3, A5 — one warn per pair, both digests, sorted; none when unchanged."""
    _, bundle, p, c = pair
    add.freeze(bundle, p, by="plan")
    assert not [f for f in add.doctor(bundle) if f["code"] == "needs_stale"], "unchanged gives reported stale"
    d = _authored(bundle, "d", sensitivity="mechanical", needs=["/tasks/p.md#gives"])
    add.freeze(bundle, d, by="plan")
    old = str(_stamp(bundle, p)["gives"]).split(":")[-1][:8]
    _move_provider(bundle, p)
    new = str(_stamp(bundle, p)["gives"]).split(":")[-1][:8]
    finds = [f for f in add.doctor(bundle) if f["code"] == "needs_stale"]
    assert [f["node"] for f in finds] == ["/tasks/c.md", "/tasks/d.md"], f"expected one warn per consumer, sorted: {finds}"
    assert all(f["severity"] == "warn" and "/tasks/p.md" in f["detail"] and old in f["detail"] and new in f["detail"]
               and "add freeze" in f["detail"] for f in finds), finds


def test_todo_hints_the_stale_consumer(pair):
    """covers: M4, E2 — the consumer's row carries the hint and the verb."""
    _, bundle, p, c = pair
    _move_provider(bundle, p)
    _, out = add.todo(bundle)
    row = next(l for l in str(out).splitlines() if "· c " in l or l.strip().startswith("· c"))
    assert "needs stale" in row and "p#gives" in row and "add freeze c" in row, f"todo row carries no stale hint: {row!r}"


def test_consumer_gate_refuses_then_passes_after_recross(pair):
    """covers: M5, R:STALENEEDS, E4 — refused after the move; passes once C refroze."""
    root, bundle, p, c = pair
    _to_verify(root, bundle, c)
    _move_provider(bundle, p)
    node, note = add.gate(bundle, c, "PASS", by="plan")
    assert node is None and "R:STALENEEDS" in note and "/tasks/p.md" in note and "add freeze c" in note, \
        f"PASS over a moved contract: {note!r}"
    assert add.freeze(bundle, c, by="plan", authority="plan")[0] is not None     # re-cross
    _to_verify(root, bundle, c)
    node, note = add.gate(bundle, c, "PASS", by="plan")
    assert node is not None, f"still refused after the re-cross: {note!r}"


def test_rung_is_evidence_class_and_never_blocks_the_provider(pair):
    """covers: M6, R:PROVIDERBLOCKED, R:CLOCKPIN — RISK-ACCEPTED lands; P gates; dates decide nothing."""
    root, bundle, p, c = pair
    _to_verify(root, bundle, c)
    _move_provider(bundle, p)
    assert add.gate(bundle, c, "RISK-ACCEPTED", by="plan", reason="owner · ticket · expiry")[0] is not None
    # the provider: a full flow of its own, gated PASS while its consumer is stale
    q = _authored(bundle, "q", gives="q.thing()", sensitivity="mechanical", scope=["src/a.py"])
    add.freeze(bundle, q, by="plan")
    r = _authored(bundle, "r", sensitivity="mechanical", needs=["/tasks/q.md#gives"])
    add.freeze(bundle, r, by="plan")
    _set_gives(bundle, q, "q.thing(v2)")
    add.freeze(bundle, q, by="plan")
    _to_verify(root, bundle, q)
    node, note = add.gate(bundle, q, "PASS", by="plan")
    assert node is not None, f"the provider was blocked by its consumer's pin: {note!r}"
    # digests, not dates: a consumer whose freeze stamp is DATED after the provider's refreeze is still stale
    stale = [f for f in add.doctor(bundle) if f["code"] == "needs_stale" and f["node"] == "/tasks/r.md"]
    assert stale, "r froze on q's old digest and is not reported"
    path = bundle / "tasks" / "r.md"
    path.write_text(re.sub(r"(act: freeze[^}]*at: )\d{4}-\d{2}-\d{2}", r"\g<1>2099-01-01", path.read_text()))
    assert [f for f in add.doctor(bundle) if f["code"] == "needs_stale" and f["node"] == "/tasks/r.md"], \
        "a later DATE on the consumer's stamp cleared the staleness -> R:CLOCKPIN"


def test_unpinned_freeze_reports_nothing(pair):
    """covers: M3, E5, A4 — a stamp with no needs key (pre-3.7) yields no finding and no refusal."""
    root, bundle, p, c = pair
    path = bundle / "tasks" / "c.md"
    path.write_text(re.sub(r', needs: "[^"]*"', "", path.read_text()))
    assert "needs:" not in str(_stamp(bundle, c)), "fixture: the pin survived"
    _move_provider(bundle, p)
    assert not [f for f in add.doctor(bundle) if f["code"] == "needs_stale"], "an unpinned consumer was reported stale"
    _to_verify(root, bundle, c)
    node, note = add.gate(bundle, c, "PASS", by="plan")
    assert node is not None, f"an unpinned consumer was refused: {note!r}"


def test_format_and_docs_state_it():
    """covers: M7 — FORMAT §3.5 and the four sentences name the finding or the rung."""
    fmt = (REPO / "FORMAT.md").read_text()
    assert "### §3.5" in fmt, "FORMAT §3.5 is still cited and still unwritten"
    sec = fmt.split("### §3.5", 1)[1].split("\n## §4", 1)[0]
    for word in ("needs_stale", "R:STALENEEDS", "refreeze", "gives:"):
        assert word in sec, f"FORMAT §3.5 never says {word}"
    for rel, needle in (("skill/add/intake.md", "flagged stale"), ("skill/add/phases/build.md", "stale"),
                        ("docs/appendix-c-glossary.md", "flagged stale"), ("docs/appendix-d-worked-example.md", "flagged stale")):
        text = (REPO / rel).read_text()
        line = next((l for l in text.splitlines() if needle in l), "")
        assert line, f"{rel}: the sentence that promised the flagging is gone"
        window = text[max(0, text.find(line) - 400): text.find(line) + len(line) + 400]
        assert "needs_stale" in window or "R:STALENEEDS" in window, \
            f"{rel}: the sentence still promises a flagging it does not name — bind it to the finding"


def test_two_moved_providers_report_in_cid_order(pair):
    """covers: E6, A5 — found by the T2 refute: the per-consumer provider order followed the stamp."""
    root, bundle, p, c = pair
    q = _authored(bundle, "q", gives="q.thing()", sensitivity="mechanical")
    add.freeze(bundle, q, by="plan")
    z = _authored(bundle, "z", sensitivity="architecture", scope=["src/a.py"], needs=["/tasks/q.md#gives", "/tasks/p.md#gives"])
    assert add.freeze(bundle, z, by="plan", authority="plan")[0] is not None
    _to_verify(root, bundle, z)
    _move_provider(bundle, p)
    _set_gives(bundle, q, "q.thing(v2)")
    add.freeze(bundle, q, by="plan")
    finds = [f["detail"] for f in add.doctor(bundle) if f["code"] == "needs_stale" and f["node"] == "/tasks/z.md"]
    assert [d.split(" froze on ")[1].split("#")[0] for d in finds] == ["/tasks/p.md", "/tasks/q.md"], \
        f"doctor reported the providers in the pin's written order, not cid order: {finds}"
    assert [t for t, _, _ in add.stale_needs(add.scan(bundle), z)] == ["/tasks/p.md", "/tasks/q.md"]
    node, note = add.gate(bundle, z, "PASS", by="plan")
    assert node is None and note.find("/tasks/p.md") < note.find("/tasks/q.md"), f"the refusal names providers out of order: {note!r}"


def test_duplicate_need_is_one_pair(pair):
    """covers: E7, M3 — found by the second T2 refute: a repeated needs: entry doubled every reader."""
    root, bundle, p, c = pair
    d = _authored(bundle, "d", sensitivity="architecture", scope=["src/a.py"], needs=["/tasks/p.md#gives", "/tasks/p.md#gives"])
    assert add.freeze(bundle, d, by="plan", authority="plan")[0] is not None
    assert str(_stamp(bundle, d)["needs"]).count("/tasks/p.md#gives=") == 1, "the pin carries the provider twice"
    _to_verify(root, bundle, d)
    _move_provider(bundle, p)
    finds = [f for f in add.doctor(bundle) if f["code"] == "needs_stale" and f["node"] == "/tasks/d.md"]
    assert len(finds) == 1, f"two warns for one (consumer, provider) pair: {finds}"
    _, out = add.todo(bundle)
    row = next(l for l in str(out).splitlines() if l.strip().startswith("· d"))
    assert row.count("needs stale") == 1, f"the hint is doubled: {row!r}"
    node, note = add.gate(bundle, d, "PASS", by="plan")
    assert node is None and note.count("/tasks/p.md#gives") == 1, f"the refusal names the provider twice: {note!r}"


def test_two_spellings_pin_one_target(pair):
    """covers: E8, M1 — found by the third T2 refute: the writer deduped by text, not by target."""
    root, bundle, p, c = pair
    d = _authored(bundle, "d", sensitivity="architecture", scope=["src/a.py"], needs=["/tasks/p.md#gives", "p.md#gives"])
    assert add.freeze(bundle, d, by="plan", authority="plan")[0] is not None
    pin = str(_stamp(bundle, d)["needs"])
    assert pin.count("=") == 1 and pin.startswith("/tasks/p.md#gives="), f"one provider pinned under two spellings: {pin!r}"


def test_closed_consumers_are_not_told_to_refreeze(pair):
    """covers: E9, M2, M3 — a done and a dropped consumer draw no note, no warn, no hint."""
    root, bundle, p, c = pair
    _to_verify(root, bundle, c)
    assert add.gate(bundle, c, "PASS", by="plan")[0] is not None            # c is done
    x = _authored(bundle, "x", sensitivity="mechanical", needs=["/tasks/p.md#gives"])
    add.freeze(bundle, x, by="plan")
    assert add.drop(bundle, x, reason="withdrawn")[0] is not None            # x is dropped
    node, note = _move_provider(bundle, p)
    assert node is not None and "stale" not in note, f"a closed consumer was told to refreeze: {note!r}"
    assert not [f for f in add.doctor(bundle) if f["code"] == "needs_stale"], "a closed consumer was reported stale"
    assert "needs stale" not in str(add.todo(bundle)[1])


def test_unfrozen_provider_pins_unknown(pair):
    """covers: E10, A3, M1 — found by the fourth T2 refute: the pin read the live list, not the stamp."""
    root, bundle, p, c = pair
    q = _authored(bundle, "q", gives="cache.get(key) -> bytes", sensitivity="mechanical")     # never frozen
    d = _authored(bundle, "d", sensitivity="architecture", scope=["src/a.py"], needs=["/tasks/q.md#gives"])
    assert add.freeze(bundle, d, by="plan", authority="plan")[0] is not None
    assert _stamp(bundle, d).get("needs") == "/tasks/q.md#gives=?", f"a consumer pinned an unfrozen provider's draft: {_stamp(bundle, d)}"
    _set_gives(bundle, q, "cache.get(key, ttl) -> bytes")
    node, note = add.freeze(bundle, q, by="plan")                                            # q's FIRST freeze
    assert node is not None and "stale" not in note, f"a first freeze named a consumer stale: {note!r}"
    assert not [f for f in add.doctor(bundle) if f["code"] == "needs_stale"], "a `?` pin was reported stale"
    _to_verify(root, bundle, d)
    assert add.gate(bundle, d, "PASS", by="plan")[0] is not None, "a `?` pin refused the consumer's gate"


def test_silent_edit_moves_no_pin(pair):
    """covers: E11, M3 — a gives: edit without a refreeze is not a moved contract."""
    root, bundle, p, c = pair
    before = _stamp(bundle, p)["gives"]
    _set_gives(bundle, p, "auth.verify(token, aud) -> Claims")                                # no refreeze
    assert _stamp(bundle, p)["gives"] == before
    assert not [f for f in add.doctor(bundle) if f["code"] == "needs_stale"], "a silent edit was reported as a moved gives"
    assert "needs stale" not in str(add.todo(bundle)[1])
    _to_verify(root, bundle, c)
    assert add.gate(bundle, c, "PASS", by="plan")[0] is not None, "a silent edit refused the consumer's gate"


def test_round_trip_names_no_consumer(pair):
    """covers: E12, M2 — the note is the M3 comparison, never a prev != new proxy."""
    root, bundle, p, c = pair
    node, note = _move_provider(bundle, p)                                                    # v1 -> v2
    assert node is not None and "add freeze c" in note
    _set_gives(bundle, p, "auth.verify(token) -> Claims")                                     # back to v1
    node, note = add.freeze(bundle, p, by="plan")
    assert node is not None and "stale" not in note, f"a round trip named a consumer whose pin is current: {note!r}"
    assert not [f for f in add.doctor(bundle) if f["code"] == "needs_stale"], "a current pin was reported stale"


def test_pin_round_trips_through_delimiters(pair):
    """covers: E13, M1, A2 — found by the fifth T2 refute: the pin string had no escaping."""
    root, bundle, p, c = pair
    q = _authored(bundle, "q", gives="cache.get(key) -> bytes", sensitivity="mechanical")
    assert add.freeze(bundle, q, by="plan")[0] is not None
    d = _authored(bundle, "d", sensitivity="architecture", scope=["src/a.py"], needs=["/tasks/p.md#gives=deadbeef"])
    assert add.freeze(bundle, d, by="plan", authority="plan")[0] is not None
    assert str(_stamp(bundle, d)["needs"]).endswith("=?"), f"a pasted stamp text was pinned as a contract: {_stamp(bundle, d)}"
    e = _authored(bundle, "e", sensitivity="architecture", scope=["src/a.py"], needs="/tasks/p.md#gives, /tasks/q.md#gives")
    assert add.freeze(bundle, e, by="plan", authority="plan")[0] is not None
    graph = add.scan(bundle)
    for cid in (d, e):
        assert add.stale_needs(graph, cid) == [], f"nothing moved, yet {cid} reads stale: {add.stale_needs(graph, cid)}"
        assert add._pins_of(graph, cid) == {}, f"the reader recovered a digest the writer never attested: {add._pins_of(graph, cid)}"
    assert not [f for f in add.doctor(bundle) if f["code"] == "needs_stale"]
    assert "needs stale" not in str(add.todo(bundle)[1])
    _to_verify(root, bundle, d)
    assert add.gate(bundle, d, "PASS", by="plan")[0] is not None, "a `?` pin with a delimiter refused the gate"
    # the property: every written pin reads back as written, for a ref text carrying either delimiter
    for cid, want in ((c, {p: _stamp(bundle, p)["gives"].split(":")[-1][:8]}), (d, {}), (e, {})):
        assert add._pins_of(graph, cid) == want, (cid, add._pins_of(graph, cid), want)


def test_two_fragments_of_one_provider_both_pin(pair):
    """covers: E14, M1, M3 — found by the sixth T2 refute: the dedupe key stripped the fragment."""
    root, bundle, p, c = pair
    digest = str(_stamp(bundle, p)["gives"]).split(":")[-1][:8]
    d = _authored(bundle, "d", sensitivity="architecture", scope=["src/a.py"], needs=["/tasks/p.md#findings", "/tasks/p.md#gives"])
    assert add.freeze(bundle, d, by="plan", authority="plan")[0] is not None
    e = _authored(bundle, "e", sensitivity="architecture", scope=["src/a.py"], needs=["/tasks/p.md#gives=deadbeef", "/tasks/p.md#gives"])
    assert add.freeze(bundle, e, by="plan", authority="plan")[0] is not None
    graph = add.scan(bundle)
    for cid in (d, e):
        pin = str(_stamp(bundle, cid)["needs"])
        assert f"/tasks/p.md#gives={digest}" in pin, f"the #gives need was dropped from the stamp: {pin!r}"
        assert add._pins_of(graph, cid) == {p: digest}, (cid, add._pins_of(graph, cid))
    assert "/tasks/p.md#findings=?" in str(_stamp(bundle, d)["needs"])
    node, note = _move_provider(bundle, p)
    assert node is not None and "add freeze d" in note and "add freeze e" in note, f"a two-fragment consumer was not named: {note!r}"
    finds = [f["node"] for f in add.doctor(bundle) if f["code"] == "needs_stale"]
    assert finds == ["/tasks/c.md", "/tasks/d.md", "/tasks/e.md"], finds
    _to_verify(root, bundle, d)
    res, msg = add.gate(bundle, d, "PASS", by="plan")
    assert res is None and "R:STALENEEDS" in msg, f"a stale two-fragment consumer gated PASS: {msg!r}"


def test_scalar_gives_digests_as_one_item(pair):
    """covers: E15, M1 — a scalar gives: is one surface, never a string of characters."""
    _, bundle, p, c = pair
    as_list = add.gives_digest({"fm": {"gives": ["auth.verify(token) -> Claims"]}})
    as_str = add.gives_digest({"fm": {"gives": "auth.verify(token) -> Claims"}})
    assert as_list == as_str, f"a scalar gives: digests differently from its one-item list: {as_str} != {as_list}"
    assert as_str != add.gives_digest({"fm": {"gives": ["auth.verify(token) -> Claims", "x"]}})


def test_pin_string_never_carries_an_inner_delimiter(pair):
    """covers: E16, E13, M1, A2 — found by the seventh T2 refute: the reader split on `,` before `=`."""
    root, bundle, p, c = pair
    digest = str(_stamp(bundle, p)["gives"]).split(":")[-1][:8]
    q = _authored(bundle, "q", gives="cache.get(key) -> bytes", sensitivity="mechanical")
    assert add.freeze(bundle, q, by="plan")[0] is not None
    qd = str(_stamp(bundle, q)["gives"]).split(":")[-1][:8]
    hostile = ["/tasks/p.md#gives=deadbeef,/tasks/q.md#gives=cafebabe", "/tasks/p.md#gives=deadbeef,", ",/tasks/p.md#gives",
               "/tasks/p.md#gives==", "/tasks/p.md#gives,=?", "=,"]
    d = _authored(bundle, "d", sensitivity="architecture", scope=["src/a.py"], needs=hostile)
    assert add.freeze(bundle, d, by="plan", authority="plan")[0] is not None
    pin = str(_stamp(bundle, d)["needs"])
    for tok in pin.split(","):
        ref, eq, val = tok.rpartition("=")
        assert eq and "=" not in ref and val == "?", f"a token carries an inner delimiter or a digest nobody attested: {tok!r} in {pin!r}"
    graph = add.scan(bundle)
    assert add._pins_of(graph, d) == {}, add._pins_of(graph, d)
    assert not [f for f in add.doctor(bundle) if f["code"] == "needs_stale"]
    assert "needs stale" not in str(add.todo(bundle)[1])
    _to_verify(root, bundle, d)
    assert add.gate(bundle, d, "PASS", by="plan")[0] is not None, "an unattested pin refused the gate"
    # the property: over every combination, exactly the honest #gives refs come back, at the stamped digest
    honest = {"/tasks/p.md#gives": p, "/tasks/q.md#gives": q, "q.md#gives": q}
    for combo in ([h for h in hostile] + ["/tasks/p.md#gives"], ["/tasks/q.md#gives", "=,", "q.md#gives"], hostile,
                  ["/tasks/p.md#gives,/tasks/q.md#gives", "/tasks/q.md#gives"]):
        e = _authored(bundle, "e", sensitivity="mechanical", needs=combo)
        assert add.freeze(bundle, e, by="plan")[0] is not None
        want = {honest[r]: (digest if honest[r] == p else qd) for r in combo if r in honest}
        got = add._pins_of(add.scan(bundle), e)
        assert got == want, (combo, got, want)
        (bundle / e.lstrip("/")).unlink()


def test_pin_survives_the_stamp_lines_own_delimiters(pair):
    """covers: E17, M1, M3 — found by the eighth T2 refute: the pin bypassed `_oneline`'s discipline."""
    root, bundle, p, c = pair
    digest = str(_stamp(bundle, p)["gives"]).split(":")[-1][:8]
    for slug, hostile in (("d", '/tasks/x".md#gives'), ("e", "/tasks/{p.md#gives"), ("f", "/tasks/p.md#gives 'y")):
        cid = _authored(bundle, slug, sensitivity="architecture", scope=["src/a.py"])
        _inline_needs(bundle, cid, [hostile, "/tasks/p.md#gives"])
        assert add.freeze(bundle, cid, by="plan", authority="plan")[0] is not None
        add.brief_stamp(bundle, cid)
        graph = add.scan(bundle)
        stamps = graph[cid]["fm"]["verified"]
        assert [s.get("act") for s in stamps] == ["freeze", "brief"], f"the stamp swallowed its successor: {stamps}"
        assert add.stamped_gives(graph, cid), f"the seal vanished after {hostile!r}: {stamps}"
        assert add._pins_of(graph, cid) == {p: digest}, (hostile, add._pins_of(graph, cid), _stamp(bundle, cid))
    node, note = _move_provider(bundle, p)
    assert node is not None and all(f"add freeze {x}" in note for x in "cdef"), note
    assert [f["node"] for f in add.doctor(bundle) if f["code"] == "needs_stale"] == [f"/tasks/{x}.md" for x in "cdef"]
    # the property over the serializer's alphabet: every hostile ref pins `?` and never hides an honest sibling
    for ch in list(add._SPECIALS.pattern.replace("\\", "").strip("[]")) + ["=", " ", "\t"]:
        g = _authored(bundle, "g", sensitivity="mechanical")
        _inline_needs(bundle, g, [f"/tasks/p.md#gives{ch}x", f"/tasks/q{ch}.md#gives", "/tasks/p.md#gives"])
        assert add.freeze(bundle, g, by="plan")[0] is not None
        add.brief_stamp(bundle, g)
        graph = add.scan(bundle)
        assert [s.get("act") for s in graph[g]["fm"]["verified"]] == ["freeze", "brief"], (ch, graph[g]["fm"]["verified"])
        pin = str(_stamp(bundle, g)["needs"])
        assert pin.count("=?") == 2 and f"/tasks/p.md#gives={_short_of(bundle, p)}" in pin, (ch, pin)
        assert add._pins_of(graph, g) == {p: _short_of(bundle, p)}, (ch, add._pins_of(graph, g))
        (bundle / g.lstrip("/")).unlink()


def _inline_needs(bundle, cid, refs):
    """Write `needs:` in inline-list form — the block form's own parser is a separate hole (a `{` in an item swallows the frontmatter)."""
    path = bundle / cid.lstrip("/")
    t = path.read_text(encoding="utf-8")
    quoted = ", ".join(f"'{r}'" if '"' in r else f'"{r}"' for r in refs)
    t = re.sub(r"^needs:\n(?:  - .*\n)*", f"needs: [{quoted}]\n", t, count=1, flags=re.M)
    if "needs: [" not in t:
        t = t.replace("generated:", f"needs: [{quoted}]\ngenerated:", 1)
    path.write_text(t, encoding="utf-8")


def _short_of(bundle, cid):
    return str(_stamp(bundle, cid)["gives"]).split(":")[-1][:8]


def test_note_and_readers_share_one_consumer_source(pair):
    """covers: E18, M2, M3 — found by the ninth T2 refute: the note walked live edges, the readers the stamp."""
    root, bundle, p, c = pair
    q = _authored(bundle, "q", gives="cache.get(key) -> bytes", sensitivity="mechanical")
    assert add.freeze(bundle, q, by="plan")[0] is not None
    d = _authored(bundle, "d", sensitivity="mechanical", needs=["/tasks/p.md#gives"])
    assert add.freeze(bundle, d, by="plan")[0] is not None
    # unsealed edits: c deletes its needs:, d retargets to q — no refreeze on either
    cp, dp = bundle / c.lstrip("/"), bundle / d.lstrip("/")
    cp.write_text(re.sub(r"^needs:\n(?:  - .*\n)*", "", cp.read_text(), count=1, flags=re.M))
    dp.write_text(dp.read_text().replace("  - /tasks/p.md#gives\n", "  - /tasks/q.md#gives\n", 1))   # the list, not the stamp
    graph = add.scan(bundle)
    assert "needs" not in graph[c]["fm"] and graph[d]["fm"]["needs"] == ["/tasks/q.md#gives"]
    node, note = _move_provider(bundle, p)
    assert node is not None
    named = sorted(x for x in "cd" if f"add freeze {x}" in note)
    warned = sorted(f["node"].rsplit("/", 1)[-1][:-3] for f in add.doctor(bundle) if f["code"] == "needs_stale")
    assert named == warned == ["c", "d"], f"the note and doctor disagree on who is stale: note={named} doctor={warned} ({note!r})"
    for x in "cd":
        assert f"add freeze {x}" in str(add.todo(bundle)[1])
    # one refreeze clears every reader at once
    for cid in (c, d):
        assert add.freeze(bundle, cid, by="plan", authority="plan")[0] is not None
    assert not [f for f in add.doctor(bundle) if f["code"] == "needs_stale"]
    assert "needs stale" not in str(add.todo(bundle)[1])
    node, note = add.freeze(bundle, p, by="plan")
    assert node is not None and "stale" not in note
