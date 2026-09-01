"""Red suite for the eval fixture — PROPOSAL v6 §3, D-10.

The spike's smoke drive refused at the gate because its scoped file did not exist, so no content
digest could be taken (freshness degraded to mtime). That was the engine behaving correctly. To
run `v0'` and see a GREEN drive, the arms need a fixture with **real, git-tracked scoped files**.

This proves the fixture supports the full trust chain through the spike dispatch: a standard task,
scoped to a real file, run with a junit report, reaches `gate PASS` (fresh receipt + bound
`covers:`) and then `done`, and the bundle still CONFORMS. If this is red, the fixture cannot host
the kill-test.
"""

import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "tooling"
sys.path.insert(0, str(SCRIPTS))

import add  # noqa: E402
import spike_cli  # noqa: E402

FIXTURE = REPO / "eval" / "fixture"
VALIDATOR = REPO / "scripts" / "validate_bundle.py"


def git(*args, cwd):
    return subprocess.run(["git", *args], cwd=str(cwd), capture_output=True, text=True)


def _repo(tmp_path):
    """The fixture, copied into a fresh git repo — one commit, so scope digests are stable."""
    repo = tmp_path / "work"
    shutil.copytree(FIXTURE, repo)
    git("init", "-q", cwd=repo)
    git("config", "user.email", "e@example.com", cwd=repo)
    git("config", "user.name", "Eval", cwd=repo)
    git("add", "-A", cwd=repo)
    git("commit", "-q", "-m", "fixture", cwd=repo)
    return repo


NODE = """## CARD
goal: multiply two numbers
beat: build · next: add run

## RULES
<must>
- M1 mul returns the product of its two arguments
</must>

## CHECKS
- test_mul · covers: M1 · proves the product
red-first: every check MUST fail first.
"""


def test_fixture_is_a_real_passing_project(tmp_path):
    """The fixture's own test must pass — a fixture that cannot go green proves nothing green."""
    repo = _repo(tmp_path)
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "tests"],
                       cwd=str(repo), capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_fixture_supports_a_green_standard_drive(tmp_path):
    """init -> new -> (author) -> implement -> run --junitxml -> gate PASS -> done, all green."""
    repo = _repo(tmp_path)
    root = repo / ".add"

    assert spike_cli.main(["init", "--root", str(root), "Fixture"]) == 0
    assert spike_cli.main(["new", "Task", "mul-fn", "--depth", "standard",
                           "--scope", "src/calc.py", "--root", str(root)]) == 0

    # author the node (a human/agent act the engine never does) and put it in build
    path = root / "tasks" / "mul-fn.md"
    stub = add.read(path, "T2")
    add.write(path, f"---\n{add.set_key(stub['raw'], 'status', 'build')}\n---\n{NODE}")

    # implement the change and commit, so the receipt earns a content digest (freshness)
    calc = repo / "src" / "calc.py"
    calc.write_text(calc.read_text() + "\n\ndef mul(a, b):\n    \"\"\"Return the product.\"\"\"\n    return a * b\n")
    git("add", "-A", cwd=repo)
    git("commit", "-q", "-m", "add mul", cwd=repo)

    # a junit report a real runner would emit for the passing check — WRITTEN BY the command,
    # so the receipt's two halves come from one process (a report that predates the run is
    # downgraded to `kind: command-exit`)
    xml = repo / "r.xml"
    doc = ('<testsuites><testsuite>'
           '<testcase classname="tests.test_calc" name="test_mul"/>'
           '</testsuite></testsuites>')

    # drive the trust chain through the dispatch — including the ONE approval and its brief
    assert spike_cli.main(["freeze", "mul-fn", "--by", "human:tindang",
                           "--authority", "human", "--root", str(root)]) == 0
    assert spike_cli.main(["brief", "mul-fn", "--by", "human:tindang",
                           "--root", str(root)]) == 0
    assert spike_cli.main(["run", "mul-fn", "--junitxml", str(xml), "--root", str(root),
                           "--", sys.executable, "-c",
                           f"open({str(xml)!r},'w').write({doc!r})"]) == 0
    assert spike_cli.main(["gate", "mul-fn", "PASS", "--by", "human:tindang",
                           "--authority", "human", "--root", str(root)]) == 0, "the gate refused a bound, fresh receipt"
    assert spike_cli.main(["done", "mul-fn", "--root", str(root)]) == 0

    node = add.read(path, "T0")
    assert node["fm"]["status"] == "done"
    v = subprocess.run([sys.executable, str(VALIDATOR), str(root)], capture_output=True, text=True)
    assert v.returncode == 0 and "CONFORMS" in v.stdout, v.stdout
