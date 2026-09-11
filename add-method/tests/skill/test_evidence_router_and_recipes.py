"""The evidence router, and three recipes that EARN `test-ids` rather than describe it.

Direct-lane change under `/milestones/evidence-over-tests.md` (criterion C3).

A property, a consumer contract and a mutation score on changed code are all "a checker that
emits JUnit" — the shape `domains.md` §1 already teaches for reconciliation. Each recipe here is
lifted out of the shipped ref and run through the real ADD loop in a real bundle; if a recipe ever
stops earning a bound `test-ids` receipt, this goes red. A phrase pin would have stayed green while
the recipe rotted (the `test_domains_recipe` lesson).

The router is a table keyed on change kind × the engine's COMPUTED floor — a value that exists, so
nothing new is declared. It is stated in the guide and in the book with the same row keys.
"""
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "skill" / "add"
DIRECTION = SKILL / "phases" / "direction.md"
DOMAINS = SKILL / "domains.md"
DOC03 = REPO / "docs" / "03-direction.md"

ROUTER_KINDS = {"mechanical", "business rule", "algorithm", "boundary", "migration", "UI", "concurrency", "security"}
RECIPES = ("property", "contract", "mutation")


def _text(p: Path) -> str:
    assert p.exists(), f"{p} does not exist"
    return p.read_text(encoding="utf-8")


def _router_rows(p: Path) -> set:
    """Row keys of the first table whose header names the floor — the router, wherever it sits."""
    text = _text(p)
    m = re.search(r"^\|[^\n]*floor[^\n]*\|\n\|[-| ]+\|\n((?:\|[^\n]*\|\n)+)", text, re.M | re.I)
    assert m, f"{p.name}: no router table (a header row naming the floor, then rows)"
    return {row.split("|")[1].strip() for row in m.group(1).strip().splitlines()}


def _kinds_in(rows: set) -> set:
    return {k for k in ROUTER_KINDS if any(k.lower() in r.lower() for r in rows)}


def test_router_stated_in_guide_and_book_with_the_same_kinds():
    guide, book = _router_rows(DIRECTION), _router_rows(DOC03)
    assert _kinds_in(guide) == ROUTER_KINDS, f"direction.md router misses {ROUTER_KINDS - _kinds_in(guide)}"
    assert _kinds_in(book) == ROUTER_KINDS, f"docs 03 router misses {ROUTER_KINDS - _kinds_in(book)}"


def test_router_is_preferred_not_enforced():
    t = " ".join(_text(DIRECTION).split())
    assert re.search(r"[Pp]referred, not enforced", t), "direction.md: the router reads as a gate"


def _recipe(name: str) -> str:
    """The shipped script itself — not a copy: a fork in this file could pass while the shipped one rots."""
    return _text(SKILL / "scripts" / f"{name}_check.py")


def test_all_three_recipes_are_published_and_named_by_the_ref():
    ref = _text(DOMAINS)
    for name in RECIPES:
        assert "sys.argv[1]" in _recipe(name), f"{name} recipe does not write the JUnit path it is handed"
        assert f"scripts/{name}_check.py" in ref, f"domains.md does not point at scripts/{name}_check.py"


# --- run each recipe through the real loop ---------------------------------------------------

def _sh(*args, cwd, check=True):
    r = subprocess.run(list(args), cwd=str(cwd), capture_output=True, text=True)
    if check:
        assert r.returncode == 0, f"{args}\n{r.stdout}\n{r.stderr}"
    return r


def _add(*args, cwd):
    return subprocess.run([sys.executable, str(Path(cwd) / ".add/tooling/cli.py"), *args],
                          cwd=str(cwd), capture_output=True, text=True)


def _project(tmp_path: Path, name: str) -> Path:
    proj = tmp_path / name
    proj.mkdir()
    _sh("git", "init", "-q", ".", cwd=proj)
    _sh("git", "config", "user.email", "t@t.t", cwd=proj)
    _sh("git", "config", "user.name", "t", cwd=proj)
    sys.path.insert(0, str(REPO / "tooling"))
    import add  # noqa: E402
    add.init(proj / ".add", "code", name)
    return proj


def _loop(proj: Path, slug: str, scope: str, checks: str, cmd: list, want_ids: list):
    """Author · freeze · brief · run — and assert the receipt reached `test-ids` with every id bound."""
    import add  # noqa: E402
    _add("new", "Task", slug, "--title", slug, "--depth", "standard", "--scope", scope, cwd=proj)
    node = proj / f".add/tasks/{slug}.md"
    raw = node.read_text(encoding="utf-8").replace(
        "  - S1 <the surface this publishes — an endpoint, function, or section>", "  - S1 the port under check")
    head, fm, body = raw.split("---", 2)
    for heading, new in (
        ("CARD", f"goal: {slug} earns a bound receipt through the recipe.\nwhy: the recipe's worked example.\nbeat: direction"),
        ("RULES", "<must>\n- M1 the invariant the recipe checks holds\n</must>\n<reject>\n- R:DRIFT the surface drifts from what the consumer depends on -> \"DRIFT\"\n</reject>"),
        ("ASSUMPTIONS", "\n".join(f"- A{i} [{d}] covers: S1 · n/a · fixed by the fixture" for i, d in enumerate(add.SWEEP_DIMENSIONS, 1))),
        ("CHECKS", checks + "\nred-first: every check MUST fail first."),
    ):
        lines = body.splitlines()
        start = next(i for i, ln in enumerate(lines) if ln.strip() == f"## {heading}")
        end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
        body = "\n".join(lines[:start + 1] + [new] + lines[end:])
    node.write_text(head + "---" + fm + "---" + body)
    r = _add("freeze", slug, "--by", "t", "--authority", "human", cwd=proj)
    assert r.returncode == 0, r.stdout + r.stderr
    _add("brief", slug, cwd=proj)
    run = _add("run", slug, "--junitxml", "r.xml", "--", *cmd, cwd=proj)
    assert run.returncode == 0, run.stdout + run.stderr
    receipt = sorted((proj / f".add/tasks/{slug}.d/runs").glob("*.md"))[-1].read_text()
    assert "kind: test-ids" in receipt, f"{slug}: recipe did not reach the top rung:\n{receipt}"
    for cited in want_ids:
        assert cited in receipt.split("passed:", 1)[-1], f"{slug}: {cited} not bound in the receipt"


def test_property_recipe_earns_test_ids(tmp_path):
    proj = _project(tmp_path, "props")
    (proj / "ledger.py").write_text(
        "class Ledger:\n"
        "    def __init__(self, b): self.b = dict(b)\n"
        "    def total(self): return sum(self.b.values())\n"
        "    def transfer(self, a, b, amt):\n"
        "        if amt <= 0 or self.b[a] < amt: return 'rejected'\n"
        "        self.b[a] -= amt; self.b[b] += amt; return 'ok'\n")
    (proj / "checks").mkdir()
    (proj / "checks" / "props.py").write_text(_recipe("property"))
    _sh("git", "add", "-A", cwd=proj); _sh("git", "commit", "-qm", "ledger", cwd=proj)
    _loop(proj, "conserve", "ledger.py",
          "- checks.props::test_balance_is_conserved · covers: M1, R:DRIFT · property · Σ balances before == after",
          [sys.executable, "checks/props.py", "r.xml"], ["test_balance_is_conserved"])


def test_contract_recipe_earns_test_ids(tmp_path):
    proj = _project(tmp_path, "pact")
    (proj / "api.py").write_text(
        "def handle(method, path, body=None):\n"
        "    if (method, path) == ('POST', '/transfers'): return 201, {'id': 't1', 'amount': int(body['amount'])}\n"
        "    return 404, {}\n")
    (proj / "pact.json").write_text(
        '{"interactions": [{"name": "create_transfer", "request": {"method": "POST", "path": "/transfers", '
        '"body": {"amount": 30}}, "response": {"status": 201, "body": {"id": "str", "amount": "int"}}}]}')
    (proj / "checks").mkdir()
    (proj / "checks" / "pact.py").write_text(_recipe("contract"))
    _sh("git", "add", "-A", cwd=proj); _sh("git", "commit", "-qm", "api", cwd=proj)
    _loop(proj, "transfers-api", "api.py,pact.json",
          "- checks.pact::test_create_transfer · covers: M1, R:DRIFT · contract · POST /transfers matches the consumer pact",
          [sys.executable, "checks/pact.py", "r.xml"], ["test_create_transfer"])


def test_mutation_recipe_earns_test_ids(tmp_path):
    proj = _project(tmp_path, "mut")
    (proj / "src").mkdir(); (proj / "tests").mkdir()
    (proj / "src" / "calc.py").write_text("def add(a, b):\n    return 0\n")
    (proj / "tests" / "test_calc.py").write_text(
        "import sys; sys.path.insert(0, 'src')\nfrom calc import add\n"
        "def test_add(): assert add(2, 3) == 5\n")
    (proj / "checks").mkdir()
    (proj / "checks" / "mutate.py").write_text(_recipe("mutation"))
    _sh("git", "add", "-A", cwd=proj); _sh("git", "commit", "-qm", "base", cwd=proj)
    (proj / "src" / "calc.py").write_text("def add(a, b):\n    return a + b\n")     # the changed code
    _sh("git", "add", "-A", cwd=proj); _sh("git", "commit", "-qm", "add", cwd=proj)
    _loop(proj, "add-mutation", "src,tests",
          "- checks.mutation::test_mutation_score_changed_code · covers: M1, R:DRIFT · mutation · ≥ 0.8 of mutants in changed src/ killed",
          [sys.executable, "checks/mutate.py", "r.xml", "0.8", "src", sys.executable, "-m", "pytest", "-q", "tests"],
          ["test_mutation_score_changed_code"])


def test_mutation_recipe_goes_red_when_the_suite_is_blind(tmp_path):
    """Withhold the subject: a suite that asserts nothing kills no mutant, and the recipe says so."""
    proj = _project(tmp_path, "blind")
    (proj / "src").mkdir(); (proj / "tests").mkdir()
    (proj / "src" / "calc.py").write_text("def add(a, b):\n    return 0\n")
    (proj / "tests" / "test_calc.py").write_text("def test_nothing(): assert True\n")
    (proj / "checks").mkdir()
    (proj / "checks" / "mutate.py").write_text(_recipe("mutation"))
    _sh("git", "add", "-A", cwd=proj); _sh("git", "commit", "-qm", "base", cwd=proj)
    (proj / "src" / "calc.py").write_text("def add(a, b):\n    return a + b\n")
    _sh("git", "add", "-A", cwd=proj); _sh("git", "commit", "-qm", "add", cwd=proj)
    r = _sh(sys.executable, "checks/mutate.py", "r.xml", "0.8", "src", sys.executable, "-m", "pytest", "-q", "tests",
            cwd=proj, check=False)
    assert r.returncode != 0, "a blind suite must fail the mutation threshold"
    assert "<failure" in (proj / "r.xml").read_text(), "the failure is not reported in the JUnit"
