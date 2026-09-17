"""Red suite for `regression-floor` — the host suite is a PLAN line the freeze demands and the gate reads.

direction.md listed "the regression floor" among what PLAN carries; nothing gave it a grammar, a
slot or a reader, and the 3.2 cut shipped a task green over a red host. Now: a rung-bound task
freezes only with `regression: full | affected · <cmd> · <why>` or `none · <why>` (R:NOFLOOR);
`run --floor` records a receipt carrying `floor: regression` that `latest_receipt` never returns;
and `gate PASS` on a declared `full|affected` floor refuses while no floor receipt is fresh and
green (R:FLOORUNRUN). Arms exactly where the refute rung arms.

Driven as `.add/tasks/regression-floor.md` under milestone `loop-that-closes`.
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
FLOOR = "regression: full · python3 -c pass · the host suite"
JUNIT = "<testsuite><testcase classname='t' name='test_only_own_rows'/></testsuite>"


def git(*args, cwd):
    subprocess.run(["git", "-c", "user.email=t@e.c", "-c", "user.name=T", *args],
                   cwd=str(cwd), capture_output=True, text=True, check=True)


def _authored(root, slug, floor_line=None, **fields):
    """A sealed-ready Task every other freeze rung accepts; `floor_line` lands in PLAN if given."""
    cid, _ = add.new(root, "Task", slug, title=slug, **fields)
    p = root / cid.lstrip("/")
    t = p.read_text(encoding="utf-8")
    t = t.replace("- S1 <the surface this publishes — an endpoint, function, or section>", "- S1 the lister")
    t = t.replace("goal: <one line>", "goal: the lister lists only the caller's rows.")
    t = re.sub(r"## RULES\n<must>\n.*?\n</must>",
               "## RULES\n<must>\n- M1 the lister returns only the caller's rows\n</must>", t, flags=re.S)
    t = re.sub(r"<reject>\n.*?\n</reject>", '<reject>\n- R:R1 thing 1 happens -> "R1"\n</reject>', t, flags=re.S)
    lines = "".join(f"- A{i} [{d}] covers: S1 · the request does not say thing {i}; taking reading {i} -> cost {i}\n"
                    for i, d in enumerate(DIMS, 1))
    t = re.sub(r"## ASSUMPTIONS\n.*?\nevery `gives:`", "## ASSUMPTIONS\n" + lines + "every `gives:`", t, flags=re.S)
    t = re.sub(r"## CHECKS\n.*?(?=\n## )",
               "## CHECKS\n- test_only_own_rows · covers: M1, R:R1 · acceptance · proves isolation\nred-first: every check MUST fail first.\n", t, flags=re.S)
    plan = "## PLAN\ncontract: the lister\n" + (floor_line + "\n" if floor_line else "")
    t = re.sub(r"## PLAN\n.*?\n\n", plan + "\n", t, flags=re.S)
    p.write_text(t, encoding="utf-8")
    return cid


@pytest.fixture
def project(tmp_path):
    """A git repo with one commit, a scoped source file, and a bundle at .add/."""
    git("init", "-q", cwd=tmp_path)
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "a.py").write_text("x = 1\n")
    git("add", "src/a.py", cwd=tmp_path)
    git("commit", "-q", "-m", "one", cwd=tmp_path)
    bundle = tmp_path / ".add"
    add.init(bundle, "code", "P")
    return tmp_path, bundle


def _junit_cmd(tmp_path, exit_code=0):
    report = tmp_path / "r.xml"
    return [sys.executable, "-c",
            f"open({str(report)!r},'w').write({JUNIT!r}); raise SystemExit({exit_code})"], report


def _to_verify(project, floor_line=FLOOR, sensitivity="architecture"):
    """Freeze → brief → narrow run → refute held: a task one floor receipt short of PASS."""
    root, bundle = project
    cid = _authored(bundle, "t", floor_line, sensitivity=sensitivity, scope=["src/a.py"])
    assert add.freeze(bundle, cid, by="plan", authority="plan")[0] is not None
    add.brief_stamp(bundle, cid)
    cmd, report = _junit_cmd(root)
    assert add.run(bundle, cid, cmd, cwd=root, junit=report)["receipt"]["exit"] == 0
    assert add.refute(bundle, cid, by="fresh", held=True, probes=1, tier="T2")[0] is not None
    return root, bundle, cid


def test_freeze_refuses_rung_bound_task_without_floor(project):
    """covers: M1, R:NOFLOOR, E1 — no line, or the template line, refuses by name."""
    _, bundle = project
    cid = _authored(bundle, "bare", None, sensitivity="architecture")
    node, note = add.freeze(bundle, cid, by="plan", authority="plan")
    assert node is None and "R:NOFLOOR" in note, f"froze with no regression line: {note!r}"
    assert "regression:" in note, "the refusal does not name the line to add"
    cid = _authored(bundle, "tmpl", "regression: <full | affected · <cmd> · <why>>", sensitivity="architecture")
    node, note = add.freeze(bundle, cid, by="plan", authority="plan")
    assert node is None and "R:NOFLOOR" in note, "a template line counted as a floor"


def test_freeze_accepts_none_with_a_why(project):
    """covers: M1, E2 — `none · <why>` freezes; a bare `none` does not."""
    _, bundle = project
    cid = _authored(bundle, "ok", "regression: none · a doc-only change touches no host suite", sensitivity="architecture")
    assert add.freeze(bundle, cid, by="plan", authority="plan")[0] is not None
    cid = _authored(bundle, "bare", "regression: none", sensitivity="architecture")
    node, note = add.freeze(bundle, cid, by="plan", authority="plan")
    assert node is None and "R:NOFLOOR" in note, "`none` with no why froze"


def test_exempt_lanes_freeze_without_the_line(project):
    """covers: M2, E3 — mechanical · quick · explore never pay."""
    _, bundle = project
    assert add.freeze(bundle, _authored(bundle, "mech", None, sensitivity="mechanical"), by="p")[0] is not None
    assert add.freeze(bundle, _authored(bundle, "quick", None, sensitivity="architecture", depth="quick"),
                      by="plan", authority="plan")[0] is not None
    cid = _authored(bundle, "ex", None, sensitivity="architecture", kind="explore")
    p = bundle / cid.lstrip("/")
    p.write_text(p.read_text().replace("## PLAN\ncontract: the lister\n", "## PLAN\ncontract: the lister\nbudget: ~10 calls\n")
                 .replace("## FINDINGS\n", "## FINDINGS\n- F1 (answers M1) · pending · (evidence: none yet)\n"))
    node, note = add.freeze(bundle, cid, by="plan", authority="plan")
    assert node is not None, f"an explore paid the floor rung: {note!r}"


def test_floor_receipt_is_marked_and_kept_out_of_latest(project):
    """covers: M3, R:FLOORASGATE, E4 — the floor receipt is marked, stamped, and never the gated one."""
    root, bundle = project
    cid = _authored(bundle, "t", FLOOR, sensitivity="architecture", scope=["src/a.py"])
    add.freeze(bundle, cid, by="plan", authority="plan")
    cmd, report = _junit_cmd(root)
    narrow = add.run(bundle, cid, cmd, cwd=root, junit=report)
    floor = add.run(bundle, cid, [sys.executable, "-c", "pass"], cwd=root, floor=True)
    assert floor["receipt"].get("floor") == "regression"
    assert "floor: regression" in Path(floor["path"]).read_text()
    _, latest_cid = add.latest_receipt(bundle, cid)
    assert latest_cid == "/" + str(Path(narrow["path"]).relative_to(bundle)), \
        "latest_receipt handed back the floor receipt — the full suite would be gated as the narrow run"
    fr, fcid = add.latest_floor_receipt(bundle, cid)
    assert fcid == "/" + str(Path(floor["path"]).relative_to(bundle)) and fr.get("floor") == "regression"
    stamps = add.scan(bundle)[cid]["fm"]["verified"]
    assert any(s.get("act") == "run" and s.get("floor") == "regression" for s in stamps), "no floor run stamp"


def test_gate_refuses_a_declared_floor_never_run(project):
    """covers: M4, R:FLOORUNRUN, E5 — everything else earned, the floor missing; then earned."""
    root, bundle, cid = _to_verify(project)
    node, note = add.gate(bundle, cid, "PASS", by="plan")
    assert node is None and "R:FLOORUNRUN" in note, f"PASS over a floor never run: {note!r}"
    assert "never run" in note and "--floor" in note and "python3 -c pass" in note, \
        f"the refusal does not name the cause and the PLAN's own command: {note!r}"
    assert add.run(bundle, cid, [sys.executable, "-c", "pass"], cwd=root, floor=True)["receipt"]["exit"] == 0
    node, note = add.gate(bundle, cid, "PASS", by="plan")
    assert node is not None, f"a fresh green floor still refused: {note!r}"


def test_gate_refuses_a_stale_or_red_floor(project):
    """covers: M4, E6, A3 (probe) — an edit after the floor run is stale; a red floor names its exit."""
    root, bundle, cid = _to_verify(project)
    assert add.run(bundle, cid, [sys.executable, "-c", "raise SystemExit(1)"], cwd=root, floor=True)["receipt"]["exit"] == 1
    node, note = add.gate(bundle, cid, "PASS", by="plan")
    assert node is None and "R:FLOORUNRUN" in note and "exit 1" in note, f"a red floor passed: {note!r}"
    add.run(bundle, cid, [sys.executable, "-c", "pass"], cwd=root, floor=True)
    (root / "src" / "a.py").write_text("x = 2\n")
    cmd, report = _junit_cmd(root)
    add.run(bundle, cid, cmd, cwd=root, junit=report)          # a fresh NARROW receipt
    add.refute(bundle, cid, by="fresh", held=True, probes=1, tier="T2")
    node, note = add.gate(bundle, cid, "PASS", by="plan")
    assert node is None and "R:FLOORUNRUN" in note and "stale" in note, f"a stale floor passed: {note!r}"


def test_floor_rung_never_refuses_risk_accepted(project):
    """covers: M5 — evidence-class: a signed acceptance lands with no floor receipt."""
    _, bundle, cid = _to_verify(project)
    node, note = add.gate(bundle, cid, "RISK-ACCEPTED", by="plan", reason="owner · ticket · expiry")
    assert node is not None, f"the floor rung refused a RISK-ACCEPTED: {note!r}"


def test_verify_hint_names_the_floor_run(project):
    """covers: M6 — at verify the hint replays the PLAN's command behind --floor."""
    root, bundle, cid = _to_verify(project)
    graph = add.scan(bundle)
    hint = add._next_verb(graph, cid, t2=add.read(graph[cid]["path"], "T2"), root=bundle)
    assert "--floor" in hint and "python3 -c pass" in hint, f"the hint does not name the floor run: {hint!r}"


def test_scaffold_format_and_guides_state_the_floor():
    """covers: M7 — the slot, the section, the two guides."""
    assert "regression:" in add.BODIES["Task"].split("## PLAN", 1)[1].split("## EDGES", 1)[0], \
        "the Task scaffold's PLAN carries no regression slot"
    fmt = (REPO / "FORMAT.md").read_text()
    sec = fmt.split("### §8.5", 1)[1].split("\n## §9", 1)[0] if "### §8.5" in fmt else ""
    assert "R:NOFLOOR" in sec and "R:FLOORUNRUN" in sec and "latest_receipt" in sec, "FORMAT §8.5 is missing or incomplete"
    direction = (REPO / "skill" / "add" / "phases" / "direction.md").read_text()
    assert "regression: full | affected" in direction and "none · <why>" in direction, "direction.md lacks the grammar"
    verify = (REPO / "skill" / "add" / "phases" / "verify.md").read_text()
    assert "--floor" in verify and "R:FLOORUNRUN" in verify, "verify.md lacks the floor run"


def test_latest_run_readers_skip_the_floor_stamp(project):
    """covers: E7, R:FLOORASGATE — found by the T2 refute: the hint's reader saw the floor as the latest run."""
    root, bundle, cid = _to_verify(project)
    graph = add.scan(bundle)
    narrow = add._latest_run_cid(graph[cid]["fm"]["verified"])
    assert add.run(bundle, cid, [sys.executable, "-c", "pass"], cwd=root, floor=True)["receipt"]["exit"] == 0
    graph = add.scan(bundle)
    assert add._latest_run_cid(graph[cid]["fm"]["verified"]) == narrow, \
        "_latest_run_cid names the floor receipt — a reader of 'the latest run' took the floor as the narrow run"
    hint = add._next_verb(graph, cid, t2=add.read(graph[cid]["path"], "T2"), root=bundle)
    assert "refute" not in hint and "gate" in hint, f"a second refute is demanded after an earned floor: {hint!r}"


def test_floor_run_never_overwrites_the_remembered_test_cmd(project):
    """covers: E8, R:FLOORASGATE — found by the T2 refute: the floor command became the build hint."""
    root, bundle = project
    cid = _authored(bundle, "t", FLOOR, sensitivity="architecture", scope=["src/a.py"])
    add.freeze(bundle, cid, by="plan", authority="plan")
    cmd, report = _junit_cmd(root)
    add.run(bundle, cid, cmd, cwd=root, junit=report)
    before = add._last_test_cmd(bundle)
    assert before and "r.xml" in before
    add.run(bundle, cid, [sys.executable, "-m", "pytest", "THE_FULL_SUITE", "-q"], cwd=root, floor=True)
    assert add._last_test_cmd(bundle) == before, \
        "the floor command overwrote the remembered narrow command — the next build hint replays the full suite"


def test_floor_only_run_keeps_the_build_beat(project):
    """covers: E9, R:FLOORASGATE — found by the second T2 refute: a floor-first run closed the build beat."""
    root, bundle = project
    cid = _authored(bundle, "t", FLOOR, sensitivity="architecture", scope=["src/a.py"])
    add.freeze(bundle, cid, by="plan", authority="plan")
    add.brief_stamp(bundle, cid)
    assert add.run(bundle, cid, [sys.executable, "-c", "pass"], cwd=root, floor=True)["receipt"]["exit"] == 0
    graph = add.scan(bundle)
    assert add._beat_of(graph[cid], None, graph) == "build", "a floor stamp closed the build beat — the narrow run vanished"
    hint_t0 = add._next_verb(graph, cid, root=bundle)
    hint_t2 = add._next_verb(graph, cid, t2=add.read(graph[cid]["path"], "T2"), root=bundle)
    for hint in (hint_t0, hint_t2):
        assert hint == "add show t", \
            f"floor-only evidence should open the Task PLAN before its narrow run: {hint!r}"
