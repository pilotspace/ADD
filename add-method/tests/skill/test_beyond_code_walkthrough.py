"""`BEYOND-CODE.md` — the non-code walkthrough, proved by running it.

A walkthrough is a promise that a reader who types these commands gets this result. This milestone
has now found six places where shipped prose said something the engine contradicted, so the one
acceptable form of that promise is an executed one.

Everything runnable is LIFTED from the shipped document through named anchors (R:FIXTUREFORK). A
private copy here would let the document rot while the test kept passing against its own fork —
the same trap `test_domains_recipe.py` avoids for the checker recipe.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DOC = REPO / "BEYOND-CODE.md"
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402 — the engine is the authority on profiles, floors and evidence kinds

FLOORS = {"security", "data", "architecture"}

# The verbs this file actually drives to reach a PASS, in the order it drives them. Both directions
# are checked against it: nothing shown that is not run, and nothing run that is not shown.
EXECUTED = ("init", "new", "freeze", "brief", "run", "gate")


def _text() -> str:
    assert DOC.exists(), f"{DOC.relative_to(REPO.parent)} does not exist — a check that asserts " \
                         f"'the document must not say X' passes vacuously on a missing file"
    return DOC.read_text(encoding="utf-8")


def _block(anchor: str) -> str:
    """Lift one anchored fenced block from the shipped document."""
    m = re.search(rf"<!--\s*{anchor}\s*-->\s*```[a-z]*\n(.*?)```", _text(), re.DOTALL)
    assert m, f"the walkthrough publishes no `<!-- {anchor} -->` fenced block"
    return m.group(1)


def _shown_verbs():
    """Every `add <verb>` the document shows a reader, in the order shown.

    Both the bare `add …` form and the explicit `python3 .add/tooling/cli.py …` form count — they
    are the same instruction, and a reader meets whichever the page happens to print.
    """
    return re.findall(r"^\s*(?:add|python3 \.add/tooling/cli\.py)\s+([a-z][a-z-]*)",
                      _text(), re.M)


def _cli(*args, cwd):
    return subprocess.run([sys.executable, str(Path(cwd) / ".add/tooling/cli.py"), *args],
                          cwd=str(cwd), capture_output=True, text=True)


def _git(*args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True, check=True)


def _project(tmp_path, name="close"):
    """A real git repo with a real bundle, framed exactly as the document instructs."""
    proj = tmp_path / name
    proj.mkdir()
    _git("init", "-q", ".", cwd=proj)
    _git("config", "user.email", "t@t.t", cwd=proj)
    _git("config", "user.name", "t", cwd=proj)
    graph, _, note = add.init(proj / ".add", _profile_from_doc(), "Month-end close")
    assert graph, f"the profile the walkthrough instructs was refused: {note}"
    return proj


def _profile_from_doc() -> str:
    named = set(re.findall(r"--profile\s+([a-z]+)", _text()))
    assert len(named) == 1, f"the walkthrough should instruct exactly one profile, found {named}"
    return named.pop()


def _author_node(proj, ledger: str):
    """Create the task and fill it from the document's own RULES and CHECKS blocks."""
    (proj / "ledger.json").write_text(ledger, encoding="utf-8")
    checks_dir = proj / "checks"
    checks_dir.mkdir(exist_ok=True)
    (checks_dir / "close.py").write_text(_block("recon-checker"), encoding="utf-8")
    _git("add", "-A", cwd=proj)
    _git("commit", "-qm", "close", cwd=proj)

    _cli("new", "Task", "close", "--title", "Month-end close", "--depth", "standard",
         "--scope", "ledger.json", cwd=proj)
    node = proj / ".add/tasks/close.md"
    raw = node.read_text(encoding="utf-8")
    raw = raw.replace("  - S1 <the surface this publishes — an endpoint, function, or section>",
                      "  - S1 the month-end reconciliation report")
    head, fm, body = raw.split("---", 2)
    for heading, new in (("CARD",
                          # Authored here for the same reason ASSUMPTIONS is: it is not a
                          # command the document publishes, and `freeze` refuses a template
                          # `goal:` — the ONE approval is an approval OF the goal.
                          "goal: the month-end close reconciles to the ledger, or says why not.\n"
                          "why: the walkthrough's worked example.\n"
                          "beat: direction"),
                         ("RULES", _block("recon-rules")),
                         ("ASSUMPTIONS", "\n".join(
                             f"- A{i} [{d}] covers: S1 · n/a · fixed by this walkthrough's fixture"
                             for i, d in enumerate(add.SWEEP_DIMENSIONS, 1))),
                         ("CHECKS", _block("recon-checks") +
                          "\nred-first: every check MUST fail first.")):
        lines = body.splitlines()
        start = next(i for i, ln in enumerate(lines) if ln.strip() == f"## {heading}")
        end = next((i for i in range(start + 1, len(lines))
                    if lines[i].startswith("## ")), len(lines))
        body = "\n".join(lines[:start + 1] + [new] + lines[end:])
    node.write_text(head + "---" + fm + "---" + body, encoding="utf-8")
    return node


def test_walkthrough_runs_end_to_end(tmp_path):
    """M1 + M2 — the whole promise, executed: a reconciliation reaches the top rung."""
    proj = _project(tmp_path)
    _author_node(proj, _block("recon-data"))

    frozen = _cli("freeze", "close", "--by", "t", "--authority", "human", cwd=proj)
    assert frozen.returncode == 0, frozen.stdout + frozen.stderr
    _cli("brief", "close", cwd=proj)
    run = _cli("run", "close", "--junitxml", "r.xml", "--",
               sys.executable, "checks/close.py", "r.xml", cwd=proj)
    assert run.returncode == 0, run.stdout + run.stderr

    receipt = sorted((proj / ".add/tasks/close.d/runs").glob("*.md"))[-1].read_text()
    assert "kind: test-ids" in receipt, f"the walkthrough does not reach the top rung:\n{receipt}"
    assert "freshness: content" in receipt, f"no content digest earned:\n{receipt}"
    bound = receipt.split("passed:", 1)[-1]
    for cited in re.findall(r"^-\s+(\S+)\s+·\s+covers:", _block("recon-checks"), re.M):
        assert cited.split("::")[-1] in bound, f"`{cited}` is cited but not bound in the receipt"

    gate = _cli("gate", "close", "PASS", "--by", "t", cwd=proj)
    assert gate.returncode == 0 and "PASS" in gate.stdout, gate.stdout + gate.stderr


def test_walkthrough_shows_both_refusals(tmp_path):
    """M3 + E1 — two refusals, for two DIFFERENT reasons, told apart.

    A blown threshold is a FAILING CHECK inside a valid run. A post-run edit is a STALE FRESHNESS
    refusal at the gate. A test asserting only "it refused" would still pass if one collapsed into
    the other, and the document would then be teaching a protection that no longer exists.
    """
    # (a) threshold breach — the run itself fails, and the materiality check is the one that failed
    proj = _project(tmp_path, "breach")
    blown = json.loads(_block("recon-data"))
    blown["variance"] = blown["gross"]          # far past any materiality threshold
    _author_node(proj, json.dumps(blown))
    _cli("freeze", "close", "--by", "t", "--authority", "human", cwd=proj)
    _cli("brief", "close", cwd=proj)
    run = _cli("run", "close", "--junitxml", "r.xml", "--",
               sys.executable, "checks/close.py", "r.xml", cwd=proj)
    receipt = sorted((proj / ".add/tasks/close.d/runs").glob("*.md"))[-1].read_text()
    assert "failed" in receipt.lower(), f"a blown threshold did not fail the run:\n{receipt}"
    gate = _cli("gate", "close", "PASS", "--by", "t", cwd=proj)
    assert gate.returncode != 0, "a gate passed over a failing run"
    breach_said = (gate.stdout + gate.stderr).lower()
    assert "stale" not in breach_said, (
        "the threshold breach was reported as a STALENESS problem — the two refusals have "
        f"collapsed into one and the walkthrough cannot teach them apart:\n{breach_said}")

    # (b) stale green — the run passed, then the artifact moved under it
    proj2 = _project(tmp_path, "stale")
    _author_node(proj2, _block("recon-data"))
    _cli("freeze", "close", "--by", "t", "--authority", "human", cwd=proj2)
    _cli("brief", "close", cwd=proj2)
    ok = _cli("run", "close", "--junitxml", "r.xml", "--",
              sys.executable, "checks/close.py", "r.xml", cwd=proj2)
    assert ok.returncode == 0, ok.stdout + ok.stderr
    edited = json.loads(_block("recon-data"))
    edited["variance"] = edited["variance"] + 1
    (proj2 / "ledger.json").write_text(json.dumps(edited), encoding="utf-8")
    _git("add", "-A", cwd=proj2)
    _git("commit", "-qm", "late edit", cwd=proj2)
    stale = _cli("gate", "close", "PASS", "--by", "t", cwd=proj2)
    assert stale.returncode != 0, "the gate passed a green receipt over an artifact that had changed"
    said = (stale.stdout + stale.stderr).lower()
    assert "stale" in said or "changed" in said or "fresh" in said, \
        f"the gate refused, but not for staleness — the two refusals are not distinguishable:\n{said}"


def test_walkthrough_teaches_only_shipped_surface():
    """M4 + R:GATEBUY — a walkthrough that teaches an unshipped thing is worse than none."""
    text = _text()
    named = set(re.findall(r"--profile\s+([a-z]+)", text))
    assert not (named - set(add.PROFILES)), \
        f"the walkthrough instructs profiles the engine does not ship: {sorted(named - set(add.PROFILES))}"

    claimed_floors = set(re.findall(r"`([a-z]+)`\s+floor", text))
    assert not (claimed_floors - FLOORS), \
        f"floor names outside the closed set: {sorted(claimed_floors - FLOORS)}"

    for banned, why in ((r"gate\s+\S+\s+RISK-ACCEPTED", "instructs RISK-ACCEPTED as a route"),
                        (r"--authority\s+process", "instructs a hand-lowered authority"),
                        (r"human-observed", "names a rung the engine cannot stamp"),
                        (r"artifact-hash", "names a rung the engine cannot stamp")):
        assert not re.search(banned, text), f"the walkthrough {why}"


def test_every_shown_command_is_executed():
    """R:PROSEONLY — a shown verb the test never ran is an unverified promise.

    The comparison is against the verbs this file actually drives, listed here as the record of
    what was executed. A new verb in the document forces a new step in the test.
    """
    shown = set(_shown_verbs())
    assert shown, "the walkthrough shows no `add` command at all"
    unrun = shown - set(EXECUTED)
    assert not unrun, (f"the walkthrough shows commands no test executes: {sorted(unrun)} — either "
                       f"drive them here or take them out; an unrun command is the defect this "
                       f"milestone has now corrected six times")


def test_the_shown_sequence_is_sufficient():
    """M1, the reverse direction — a reader following this document must not hit a step it omits.

    The first draft left out `add brief`. Every check passed: the test ran `brief` itself, so the
    loop reached a PASS, and the forward check saw no shown-but-unrun command because a MISSING
    step is not a shown one. A reader following the page literally would have reached the gate and
    been refused with `R:UNBRIEFED` — the walkthrough would have worked while following the
    walkthrough did not.

    Order matters too, not just membership: `freeze` after `run` would be a different method.
    """
    shown = _shown_verbs()
    missing = [v for v in EXECUTED if v not in shown]
    assert not missing, (
        f"the loop needs {missing} to reach a PASS and the walkthrough never shows it — a reader "
        f"following this page hits a refusal the page did not prepare them for")

    order = [v for v in shown if v in EXECUTED]
    first = []
    for v in order:                     # first appearance only; a verb may be shown twice
        if v not in first:
            first.append(v)
    assert first == list(EXECUTED), (
        f"the walkthrough teaches the beats in the wrong order: {first} — the loop runs "
        f"{list(EXECUTED)}, and an order that differs is a different method")
