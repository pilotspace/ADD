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
    assert re.fullmatch(r"[0-9a-f]{16,64}", str(ps.get("gives") or "")), f"provider stamp pins no gives digest: {ps}"
    assert str(cs.get("needs") or "").startswith("/tasks/p.md#gives=") and str(ps["gives"])[:8] in str(cs["needs"]), \
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
    old = str(_stamp(bundle, p)["gives"])[:8]
    _move_provider(bundle, p)
    new = str(_stamp(bundle, p)["gives"])[:8]
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
