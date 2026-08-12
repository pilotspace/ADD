"""`domains.md` — the all-domain evidence ref, proved by EXECUTION not by phrase pins.

The load-bearing test is `test_recipe_earns_bound_test_ids`: it lifts the checker recipe out of
the shipped ref and runs the real ADD loop with it, in a real bundle, on a non-code domain node.
If the recipe ever stops earning a bound `test-ids` receipt, this goes red — a phrase pin would
have stayed green while the thing it documents rotted.

Every test asserts the ref EXISTS before asserting anything about its content. A "must never
contain X" assertion passes vacuously on a missing file, which is exactly the assert-nothing trap
the method warns about (`FORMAT.md` §10).
"""
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "skill" / "add"
DOMAINS = SKILL / "domains.md"

# The closed floor set. A pack may map its own vocabulary ONTO these; it may never add to them.
FLOORS = {"security", "data", "architecture"}
# The profiles the engine actually ships. `init` REFUSES anything else as of 3.2 — it used to fall
# back to `code` silently, which is why a ref naming a phantom profile once produced a bundle that
# lied about its own domain. The refusal removed the damage; naming an unshipped profile is now
# simply an instruction that cannot be followed.
SHIPPED_PROFILES = {"code", "doc"}


def _text() -> str:
    assert DOMAINS.exists(), "skill/add/domains.md does not exist"
    return DOMAINS.read_text(encoding="utf-8")


def _recipe_block() -> str:
    """The runnable checker the ref publishes, lifted from its `<!-- checker-recipe -->` anchor.

    Extracted rather than duplicated: a copy in this file would let the shipped recipe rot while
    the test kept passing against its own private fork.
    """
    text = _text()
    m = re.search(r"<!--\s*checker-recipe\s*-->\s*```python\n(.*?)```", text, re.DOTALL)
    assert m, "domains.md publishes no `<!-- checker-recipe -->` fenced python block"
    return m.group(1)


def _run(*args, cwd):
    return subprocess.run([sys.executable, str(Path(cwd) / ".add/tooling/cli.py"), *args],
                          cwd=str(cwd), capture_output=True, text=True)


def test_recipe_earns_bound_test_ids(tmp_path):
    """The whole claim of this milestone, executed: a NON-CODE domain node reaches the top rung."""
    proj = tmp_path / "ledger"
    proj.mkdir()
    subprocess.run(["git", "init", "-q", "."], cwd=proj, check=True)
    subprocess.run(["git", "config", "user.email", "t@t.t"], cwd=proj, check=True)
    subprocess.run(["git", "config", "user.name", "t"], cwd=proj, check=True)

    sys.path.insert(0, str(REPO / "tooling"))
    import add  # noqa: E402 — the vendoring engine, same one the installer drops
    add.init(proj / ".add", "doc", "Ledger")

    # the domain artifact under check — data, not code
    (proj / "recon.json").write_text(json.dumps(
        {"gross": 1_000_000, "variance": 3_200,
         "lines": [{"id": "v1", "amt": 3_200, "source_doc": "BS-2026-07-p4"}]}))
    checks = proj / "checks"
    checks.mkdir()
    (checks / "recon.py").write_text(_recipe_block())
    subprocess.run(["git", "add", "-A"], cwd=proj, check=True)
    subprocess.run(["git", "commit", "-qm", "recon"], cwd=proj, check=True)

    _run("new", "Task", "recon", "--title", "Reconcile", "--depth", "standard",
         "--scope", "recon.json", cwd=proj)
    node = proj / ".add/tasks/recon.md"
    raw = node.read_text(encoding="utf-8")
    raw = raw.replace("  - S1 <the surface this publishes — an endpoint, function, or section>",
                      "  - S1 the month-end reconciliation report")
    body = raw.split("---", 2)[2]
    for heading, new in (
        ("RULES", "<must>\n- M1 unexplained variance stays within materiality\n</must>\n"
                  "<reject>\n- R:UNEXPLAINED a variance line with no cited source document"
                  ' -> "UNEXPLAINED"\n</reject>'),
        ("ASSUMPTIONS", "\n".join(
            f"- A{i} [{d}] covers: S1 · n/a · fixed by the fixture"
            for i, d in enumerate(add.SWEEP_DIMENSIONS, 1))),
        ("CHECKS", "- checks.recon::test_variance_within_materiality · covers: M1 · within materiality\n"
                   "- checks.recon::test_every_variance_line_cited · covers: R:UNEXPLAINED · every line cited\n"
                   "red-first: every check MUST fail first."),
    ):
        lines = body.splitlines()
        start = next(i for i, ln in enumerate(lines) if ln.strip() == f"## {heading}")
        end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
        body = "\n".join(lines[:start + 1] + [new] + lines[end:])
    node.write_text(raw.split("---", 2)[0] + "---" + raw.split("---", 2)[1] + "---" + body)

    assert _run("freeze", "recon", "--by", "t", "--authority", "human", cwd=proj).returncode == 0
    _run("brief", "recon", cwd=proj)
    run = _run("run", "recon", "--junitxml", "r.xml", "--",
               sys.executable, "checks/recon.py", "r.xml", cwd=proj)
    assert run.returncode == 0, run.stdout + run.stderr

    receipt = sorted((proj / ".add/tasks/recon.d/runs").glob("*.md"))[-1].read_text()
    assert "kind: test-ids" in receipt, f"recipe did not reach the top rung:\n{receipt}"
    assert "freshness: content" in receipt, f"recipe did not earn a content digest:\n{receipt}"
    for cited in ("test_variance_within_materiality", "test_every_variance_line_cited"):
        assert cited in receipt.split("passed:", 1)[-1], f"{cited} not bound in the receipt"

    gate = _run("gate", "recon", "PASS", "--by", "t", cwd=proj)
    assert "PASS" in gate.stdout and gate.returncode == 0, gate.stdout + gate.stderr


def test_domains_exists_within_surface_budget():
    """M3 — the ref must exist AND be funded.

    Binding M3 to the pre-existing `test_total_surface_within_budget` was wrong: that test is
    green with no `domains.md` at all, so it would have ridden into the freeze proving nothing.
    Existence is the conjunct that makes this red before the build.
    """
    _text()  # existence first — the budget alone is satisfied by writing nothing
    own = [p for p in SKILL.rglob("*.md") if "persona-author" not in p.relative_to(SKILL).parts]
    total = sum(len(p.read_text(encoding="utf-8").splitlines()) for p in own)
    assert total <= 1500, f"skill surface is {total} lines (budget 1500) — fund the add by compressing"


def test_floor_map_targets_only_existing_floors():
    """Every floor the map routes TO is one the engine already computes."""
    rows = re.findall(r"^\|[^|]+\|\s*`?([a-z]+)`?\s*(?:floor)?\s*\|", _text(), re.M)
    assert rows, "domains.md publishes no floor-mapping table rows"
    stray = {r for r in rows} - FLOORS
    assert not stray, f"floor map targets floors the engine does not compute: {sorted(stray)}"


def test_introduces_no_new_floor_name():
    """R:NEWFLOOR — a pack may rename nothing into the floor vocabulary."""
    claimed = set(re.findall(r"`([a-z]+)`\s+floor", _text()))
    stray = claimed - FLOORS
    assert not stray, f"domains.md introduces floor names outside the closed set: {sorted(stray)}"


def test_states_freshness_degrade(tmp_path):
    """E1 — a domain with no digestible artifact.

    POST-HOC GUARD, not a red-first check: `domains.md` already carried this sentence when the
    check was written, because E1 was authored as a gate referent with no check covering it and
    the gate caught it after the build. Recorded as a guard so it cannot silently drop out.
    """
    text = _text()
    assert re.search(r"mtime", text), "the ref never names the mtime fallback"
    assert re.search(r"freshness falls back to mtime", text), \
        "the ref must say the freshness degrade OUT LOUD, not merely mention mtime"


def test_unmapped_word_routes_to_size_up():
    """E2 — a domain word the map does not carry must route to size-up, never to silence.

    POST-HOC GUARD — same provenance as `test_states_freshness_degrade`.
    """
    text = _text()
    assert re.search(r"size up", text), "the ref never routes an unmapped word to size-up"
    assert re.search(r"[Aa]bsence from the table is never evidence", text), \
        "the ref must deny the silence reading explicitly, not just recommend sizing up"


def test_recipe_buys_no_gate():
    """R:GATEBUY — the ref must never teach a cheaper route to a verdict."""
    text = _text()
    for banned, why in (
        (r"gate\s+\S+\s+RISK-ACCEPTED", "instructs RISK-ACCEPTED as a domain route"),
        (r"--authority\s+process", "instructs a hand-lowered authority"),
        (r"human-observed", "names a rung the engine cannot stamp"),
        (r"artifact-hash", "names a rung the engine cannot stamp"),
    ):
        assert not re.search(banned, text), f"domains.md {why}"


def test_names_no_phantom_profile():
    """R:PHANTOMPROFILE — a ref must not instruct a profile the engine will refuse."""
    named = set(re.findall(r"--profile\s+([a-z]+)", _text()))
    stray = named - SHIPPED_PROFILES
    assert not stray, (f"domains.md instructs profiles the engine does not ship: {sorted(stray)} "
                       f"— `init` refuses them, so the instruction cannot be followed")
