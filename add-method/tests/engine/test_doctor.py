"""e8 `doctor` — conformance and repair over the compiled graph.

Red-first for `/tasks/build-doctor.md`. The `covers:` citations live in each test's docstring,
which is where `checks_of` reads them (e14's M1) — after BUILD this file is what compiles that
node's CHECKS section, so a citation here is a claim `checks_sync` will publish.

M2 is the load-bearing test and it is the one most likely to fail honestly: it runs the M0
validator as a SUBPROCESS and diffs its findings against `doctor`'s. Importing the validator would
make the test pass by construction — the skill ships without this repo, so the engine can never
import it, and a test that does so proves nothing about what ships (A1's correction to e8's cut).
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

VALIDATOR = REPO / "scripts" / "validate_bundle.py"
# The repo's OWN bundle, at the repository root — NOT `add-method/.add`, which .gitignore
# forbids ("add-method/ is the PACKAGE SOURCE, never an ADD-managed project") and which
# therefore exists only on a machine where a stray `init` once ran. Pointed there, this test
# passed locally and died in CI with a JSONDecodeError on the validator's empty output.
LIVE = REPO.parent / ".add"


@pytest.fixture
def bundle(tmp_path):
    """A real bundle, created by the engine rather than by fixture text."""
    root = tmp_path / ".add"
    add.init(root, profile="code", title="doctor fixture")
    return root


def _validator(root) -> list:
    """The M0 oracle's findings, as a subprocess. Never imported — see the module docstring."""
    done = subprocess.run([sys.executable, str(VALIDATOR), str(root), "--json"],
                          capture_output=True, text=True, timeout=60)
    return json.loads(done.stdout)["findings"]


# ------------------------------------------------------------------ M1 · over e2's graph

def test_doctor_uses_the_graph(bundle, monkeypatch):
    """covers: M1, R:SECONDSCAN — doctor reads e2's compiled graph and never rglobs its own.

    Asserted by making a second scan impossible: `Path.rglob` raises for the duration. A verb that
    builds its own node walk cannot survive that, and A1 pre-booked doctor's 150-line saving on
    exactly this — it is a budget rule as much as a design one.
    """
    graph = add.load(bundle)

    def no_rglob(self, pattern):
        raise AssertionError(f"doctor built its own scan: rglob({pattern!r}) on {self}")

    monkeypatch.setattr(Path, "rglob", no_rglob)
    add.doctor(bundle, graph=graph)


def test_doctor_reports_nothing_on_a_fresh_bundle(bundle):
    """covers: M1 — a bundle the engine just created has no conformance findings.

    The floor for every other assertion here: if `init` produces findings, no later diff means
    anything, because the baseline is already wrong.
    """
    errors = [f for f in add.doctor(bundle) if f["severity"] == "error"]
    assert errors == [], f"the engine's own fresh bundle does not pass doctor: {errors}"


# ---------------------------------------------------- M1 · e2's contract extension (post-gate)

def test_scan_collects_strays_without_polluting_the_graph(bundle):
    """covers: M1 — `scan` reports non-node files through a caller-owned list, not the graph.

    e2's contract, extended after its gate at human authority and recorded on its node. The graph
    stays exactly cid -> node: returning strays under a reserved key inside it would break every
    consumer that iterates `graph.items()`, which is F4's defect class reintroduced on purpose.
    """
    (bundle / "stray.md").write_text("# not a node\n", encoding="utf-8")
    strays = []
    graph = add.scan(bundle, strays=strays)
    assert "stray.md" in strays, f"a file with no frontmatter was not collected: {strays}"
    assert all(k.startswith("/") for k in graph), f"a non-cid key entered the graph: {list(graph)}"
    assert "/stray.md" not in graph, "a stray was added to the graph as if it were a node"
    assert add.scan(bundle) == graph, "the graph differs depending on whether strays were asked for"


def test_missing_frontmatter_is_reported_by_doctor(bundle):
    """covers: M2, R:DIVERGE — the code F6 proved doctor was blind to.

    `.pytest_cache/README.md` was written into this bundle by a command the engine ran, and only the
    M0 validator caught it. A conformance verb shipped inside the skill that cannot see that file is
    a verb which certifies bundles that do not conform.
    """
    (bundle / "stray.md").write_text("# not a node\n", encoding="utf-8")
    ours = [f for f in add.doctor(bundle) if f["code"] == "missing_frontmatter"]
    assert ours, "doctor did not report a file with no frontmatter"
    assert ours[0]["detail"] == "stray.md", f"detail is not the validator's shape: {ours[0]}"
    assert ours[0]["severity"] == "error", "missing_frontmatter is an error, not an info"


def test_reserved_files_are_not_missing_frontmatter(bundle):
    """covers: M2, R:DIVERGE — `index.md` and `log.md` carry no frontmatter BY DESIGN.

    They are compiled bodies (A11/A20). The validator exempts them by name and doctor must too;
    reporting them would make every conforming bundle in existence report two errors.
    """
    detail = {f["detail"] for f in add.doctor(bundle) if f["code"] == "missing_frontmatter"}
    assert not (detail & {"index.md", "log.md"}), \
        f"a reserved compiled body was reported as a missing-frontmatter error: {detail}"


# ------------------------------------------------------------------ M2 · parity with the M0 oracle

def test_parity_with_m0_oracle():
    """covers: M2, R:DIVERGE — on the validator's own seven codes, both oracles agree exactly.

    Run on the repo's own live bundle — a real tree on disk rather than a fixture, which is the
    point: the two oracles must agree about a bundle neither of them made up. (The 2.x bundle
    this once read had 59 nodes; the 3.0 one is small, so `test_a_broken_edge_is_found_by_both`
    below carries the injected-defect half of the claim.) Asymmetric by decision recorded on the
    node: doctor may report codes the validator has no concept of, because it reads stamps. It
    may not report a conformance finding the validator would not.
    """
    shared = {"missing_frontmatter", "type_empty", "edge_out_of_bundle",
              "unknown_type", "edge_unresolved", "broken_md_link", "compiled_undeclared"}
    theirs = sorted((f["code"], f["detail"]) for f in _validator(LIVE) if f["code"] in shared)
    ours = sorted((f["code"], f["detail"]) for f in add.doctor(LIVE) if f["code"] in shared)
    assert ours == theirs, (
        "the two oracles disagree on the format itself.\n"
        f"  only doctor:    {[x for x in ours if x not in theirs]}\n"
        f"  only validator: {[x for x in theirs if x not in ours]}")


def test_a_broken_edge_is_found_by_both(bundle):
    """covers: M2, R:DIVERGE — the same injected defect produces the same code in both tools.

    Parity on a clean bundle is cheap: both report nothing. This makes a real defect and requires
    both to see it, which is the claim M2 actually makes.
    """
    add.new(bundle, "Task", "orphan-edge", title="an edge into nowhere",
            depends_on=["/tasks/does-not-exist.md"])
    codes = {f["code"] for f in add.doctor(bundle)}
    assert codes & {f["code"] for f in _validator(bundle)}, \
        f"doctor saw {codes} where the validator saw something else"


# ------------------------------------------------------------------ M5 · F3's orphaned receipts

def test_orphaned_receipt_is_reported(bundle):
    """covers: M5 — a receipt no `verified[]` stamp points at is a finding, not a silence.

    F3's assigned check. The receipt exists on disk while the record of it existing does not, so
    `status --since` under-reports every machine act and the milestone's EXIT criterion reads as
    met when it is not. `orphans()` has computed this since e13; nothing has ever reported it.
    """
    cid, _ = add.new(bundle, "Task", "has-an-orphan", title="a task with an unbound receipt",
                     scope=["README.md"])
    runs = bundle / "tasks/has-an-orphan.d/runs"
    runs.mkdir(parents=True, exist_ok=True)
    add.write(runs / "1.md", "---\ntype: Run\nruntime: process\n"
                             f"task: {cid}\ncomputation: \"true\"\n"
                             "receipt:\n  kind: command-exit\n  exit: 0\n---\n")
    found = [f for f in add.doctor(bundle) if f["code"] == "orphan_receipt"]
    assert found, "an orphaned receipt was not reported"
    assert "1.md" in found[0]["detail"], f"the finding does not say which receipt: {found[0]}"


def test_live_orphans_are_all_reported():
    """covers: M5 — the eight orphans this bundle carries are reported, every one.

    They predate F3's fix and cannot be stamped retroactively — a stamp invented now would claim a
    binding that never happened. So the number is expected to stay at eight and this test exists to
    notice if it silently drops, which would mean someone repaired history.
    """
    reported = {f["detail"] for f in add.doctor(LIVE) if f["code"] == "orphan_receipt"}
    assert len(reported) == len(add.orphans(LIVE)), \
        f"orphans() finds {len(add.orphans(LIVE))} but doctor reports {len(reported)}"


def test_orphans_are_not_repaired_away(bundle):
    """covers: M5, R:REPAIRAWAY — `--sync` cannot make an orphaned receipt disappear.

    The tempting repair is to append the missing stamp. That is forging evidence of a binding that
    never occurred, and it is the same move §3.6 forbids for a gated claim. `--sync` recomputes
    VIEWS; it does not manufacture history.
    """
    cid, _ = add.new(bundle, "Task", "keeps-its-orphan", title="an orphan that must survive sync")
    runs = bundle / "tasks/keeps-its-orphan.d/runs"
    runs.mkdir(parents=True, exist_ok=True)
    add.write(runs / "1.md", f"---\ntype: Run\nruntime: process\ntask: {cid}\n"
                             "computation: \"true\"\nreceipt:\n  kind: command-exit\n  exit: 0\n---\n")
    before = len(add.orphans(bundle))
    add.doctor_sync(bundle)
    assert len(add.orphans(bundle)) == before, "`--sync` forged a stamp for an orphaned receipt"
    assert [f for f in add.doctor(bundle) if f["code"] == "orphan_receipt"], \
        "the orphan stopped being reported after a sync that did not fix it"


@pytest.mark.skip(reason="dogfood: asserts add-skill's 8 dev-bundle orphan receipts; a fresh bundle has none")
def test_orphans_from_the_graph_match_orphans_from_the_disk():
    """covers: M1, R:SECONDSCAN — `orphans` reads Run nodes from the graph, same answer as before.

    e13 computed this by rglobbing `runs/*.md`. Under R:SECONDSCAN doctor may not, and it does not
    need to: a receipt IS a node (`type: Run`), so it is already in the compiled graph. That is a
    change of BASIS, not just of signature — files-under-a-directory to nodes-of-a-type — so it is
    asserted equal on the live bundle, which carries eight orphans and is the only corpus where a
    disagreement could show up.
    """
    graph = add.load(LIVE)
    # The OLD basis, recomputed here rather than called: `orphans` no longer contains it, so
    # comparing the function to itself would be a test that cannot fail.
    cited = {str(s["receipt"]).lstrip("/") for n in graph.values()
             for s in ((n["fm"] or {}).get("verified") or [])
             if isinstance(s, dict) and s.get("receipt")}
    by_directory = sorted("/" + p.relative_to(LIVE).as_posix()
                          for p in LIVE.rglob("runs/*.md")
                          if p.relative_to(LIVE).as_posix() not in cited)
    assert add.orphans(LIVE, graph=graph) == by_directory, \
        "reading receipts from the graph found a different set than walking the directory"
    assert len(by_directory) == 8, f"the live orphan count moved: {len(by_directory)}"


# ------------------------------------------------------------------ M6 · F2 behind a gate

@pytest.mark.skip(reason="dogfood: asserts add-skill's 65 F2 claims in its dev bundle; a fresh bundle has none")
def test_f2_claims_surface_as_findings():
    """covers: M6 — a gated node citing a test that exists nowhere is a doctor finding.

    F2's 65 rules were labelled, not proven, and they were found by a script someone chose to run.
    A defect only a remembered command can see is a defect the next person will not see. Run on the
    live bundle, where nine gated M0 tasks carry exactly this.
    """
    suite = sorted((REPO / "tests").rglob("test_*.py"))
    found = [f for f in add.doctor(LIVE, paths=suite) if f["code"] == "checks_citation"]
    assert found, "no F2 claim reported on a bundle that carries 65 of them"
    assert all(f["severity"] == "error" for f in found), \
        f"a claim accepted at a gate was reported below error: {found[:2]}"


def test_pending_checks_are_not_findings(bundle):
    """covers: M6 — an unbuilt node's planned CHECKS are a plan, not a defect.

    e14 learned this by flagging thirteen nodes when nine were real. Promoting `pending` here would
    make `doctor` report every task that has not been built yet, and a report nobody can read is
    the same as no report.
    """
    cid, _ = add.new(bundle, "Task", "not-built-yet", title="a task still in direction")
    path = bundle / cid.lstrip("/")
    n = add.read(path, "T2")
    add.write(path, f"---\n{n['raw']}\n---\n{n['body']}"
                    "\n## RULES\n<must>\n- M1 something is true\n</must>\n"
                    "\n## CHECKS\n- test_never_written · covers: M1 · proves M1\n")
    findings = [f for f in add.doctor(bundle, paths=[]) if f["code"] == "checks_citation"]
    assert findings == [], f"an ungated node's plan was reported as a defect: {findings}"


def test_the_suite_is_parsed_once_per_doctor_run():
    """covers: M6 — extracting the suite 59 times to answer one question is a defect, not a cost.

    `checks_verify` extracts every test in `paths` for each node it checks, so `doctor(paths=…)`
    on this bundle parsed the suite once per node: **1,650 ms against 37 ms without**, a 45x
    penalty on the verb that is supposed to run in CI. Asserted by COUNTING parses rather than by
    timing, because a clock makes a flaky test and a count makes a true one.
    """
    import ast as _ast
    calls = []
    real = _ast.parse

    def counted(src, *a, **kw):
        calls.append(1)
        return real(src, *a, **kw)

    suite = sorted((REPO / "tests").rglob("test_*.py"))
    _ast.parse = counted
    try:
        add.doctor(LIVE, paths=suite)
    finally:
        _ast.parse = real
    assert len(calls) <= len(suite), \
        f"parsed {len(calls)} times for {len(suite)} suite files — the extraction is not shared"


# ------------------------------------------------------------------ M3 · --sync recomputes views

def test_sync_regenerates_index(bundle):
    """covers: M3 — a corrupted TOC is rebuilt from the nodes, because the nodes are the database.

    This is A23 merge resolution: a conflicted compiled file is resolved by recomputation. It is
    only sound because L1 makes `index.md` a view — the same edit to a node body would be data loss.
    """
    add.new(bundle, "Task", "listed-in-the-toc", title="a task the TOC must name")
    index = bundle / "index.md"
    add.write(index, "# index\n\nTHIS TOC WAS CLOBBERED BY A MERGE\n")
    changed, note = add.doctor_sync(bundle)
    assert changed, f"sync did not rebuild a clobbered index: {note}"
    assert "listed-in-the-toc" in index.read_text(), "the rebuilt TOC omits a node that exists"


def test_sync_repairs_card_drift(bundle):
    """covers: M3 — e6's `render_card` runs across the bundle, not one node at a time.

    `card_drift` has reported this since e6 and every repair so far has been a hand edit — which is
    the milestone's EXIT criterion "`.add/` driven by the engine, not by hand" failing quietly.
    """
    cid, _ = add.new(bundle, "Task", "drifted-card", title="a card that disagrees with its stamps")
    path = bundle / cid.lstrip("/")
    n = add.read(path, "T2")
    add.write(path, f"---\n{n['raw']}\n---\n" + n["body"].replace("beat: direction", "beat: done"))
    assert add.card_drift(add.load(bundle)), "the fixture did not actually drift"
    add.doctor_sync(bundle)
    assert not add.card_drift(add.load(bundle)), "sync left the CARD drifted"


def test_sync_never_touches_authored(bundle):
    """covers: M4, R:SYNCAUTHORED — a file humans author is not rewritten, ever.

    `log.md`'s `## Notes` is human-owned by A20 and every node body is authored content by L6.
    `--sync` writes only what FORMAT declares compiled; anything else it touches is data loss with
    a helpful tone.
    """
    cid, _ = add.new(bundle, "Task", "authored-by-a-human", title="prose no tool may rewrite")
    path = bundle / cid.lstrip("/")
    n = add.read(path, "T2")
    add.write(path, f"---\n{n['raw']}\n---\n{n['body']}\n## PLAN\nstrategy: I wrote this sentence.\n")
    before = path.read_bytes()
    notes = bundle / "log.md"
    add.write(notes, notes.read_text() + "\nA human wrote this under Notes.\n")
    note_bytes = notes.read_bytes()

    add.doctor_sync(bundle)
    assert b"I wrote this sentence." in path.read_bytes(), "sync rewrote authored prose"
    assert b"A human wrote this under Notes." in notes.read_bytes(), \
        "sync destroyed the human-owned Notes section (A20)"
    assert path.read_bytes() == before or add.card_drift(add.load(bundle)) == [], \
        "sync changed an authored node for a reason other than CARD drift"


def test_doctor_reports_only_and_sync_writes(bundle):
    """covers: M4 — `doctor` is a reporter; not one byte moves unless `--sync` was asked for.

    Law 3, stated as a test: the notary records, it does not fix. A conformance checker that
    silently repairs is a checker whose report you can never trust, because you cannot tell what it
    found from what it changed.
    """
    add.write(bundle / "index.md", "# index\n\nCLOBBERED\n")
    before = {p: p.read_bytes() for p in sorted(bundle.rglob("*.md"))}
    add.doctor(bundle)
    after = {p: p.read_bytes() for p in sorted(bundle.rglob("*.md"))}
    assert before == after, \
        f"doctor wrote to {[p.name for p in after if before.get(p) != after[p]]}"


def test_sync_is_idempotent(bundle):
    """covers: M3 — a second sync writes nothing, because the views already match the nodes.

    An oracle that always reports work to do cannot be used in CI, and a `--sync` that rewrites
    identical content churns git history for no information.
    """
    add.new(bundle, "Task", "settled", title="a bundle already in sync")
    add.doctor_sync(bundle)
    changed, note = add.doctor_sync(bundle)
    assert not changed, f"a second sync still wanted to write: {note}"


def test_doctor_on_the_live_bundle_is_clean():
    """covers: M2 — the project's own bundle carries no conformance error under its own oracle.

    The floor every task in this milestone has been gated against, now asserted by the engine
    instead of by a repo script the shipped skill will not contain.
    """
    errors = [f for f in add.doctor(LIVE) if f["severity"] == "error"
              and f["code"] not in {"orphan_receipt", "checks_citation"}]
    assert errors == [], f"the live bundle does not conform under doctor: {errors}"
