"""The bundle scan stops parsing evidence nothing in the graph reads.

Measured on the live bundle before this task: 97 Run receipts were 68% of all T0 parse time,
because `receipt.scope_digest` and `receipt.passed` put 7979 `path:` entries and 953 test-id
lines into frontmatter that EVERY command parses. Both grow monotonically and nothing prunes
them — the digest is one entry per file in scope (66 -> 103 per receipt in three weeks) and
receipts are append-only — so `add status` pays for the whole project history on every run.

The payload's only readers, `fresh()` and the gate's coverage map, are both fed by
`latest_receipt()`, which does its own direct single-node read. So the graph never needed it.

Two properties keep this safe rather than merely fast: a direct `read()` is untouched (M3),
and a scanned node's `raw` stays byte-complete (M2) so the one write path cannot lose a byte
it never parsed.
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

HEAVY = ("scope_digest", "passed", "failed")


def _bundle(tmp_path, *, receipts=1, digest=3, ids=2):
    """A minimal bundle with `receipts` Run nodes, each carrying a real evidence payload."""
    root = tmp_path / ".add"
    (root / "tasks" / "t.d" / "runs").mkdir(parents=True)
    (root / "specs").mkdir(parents=True)
    (root / "index.md").write_text("---\nabf_version: \"1.3\"\nname: b\n---\n", encoding="utf-8")
    (root / "PROJECT.md").write_text("---\ntype: Project\ntitle: b\n---\n## CARD\ngoal: g\n",
                                     encoding="utf-8")
    (root / "tasks" / "t.md").write_text(
        "---\ntype: Task\ntitle: t\nstatus: done\nscope:\n  - src\n---\n## CARD\ngoal: g\n",
        encoding="utf-8")
    for n in range(1, receipts + 1):
        dig = "".join(f'    - {{ path: src/f{i}.py, blob: "sha1:{i:040d}" }}\n'
                      for i in range(digest))
        pas = "".join(f"    - tests.engine.test_x::test_{i}\n" for i in range(ids))
        (root / "tasks" / "t.d" / "runs" / f"{n}.md").write_text(
            "---\ntype: Run\nruntime: process\ntask: /tasks/t.md\n"
            'computation: "pytest -q"\n'
            "receipt:\n  kind: test-ids\n  exit: 0\n  freshness: content\n"
            f"  at: 2026-09-03\n  passed:\n{pas}  failed:\n"
            f"  scope_digest:\n{dig}---\n## Notes\n", encoding="utf-8")
    return root


def _receipt_fm(graph, n=1):
    return (graph[f"/tasks/t.d/runs/{n}.md"]["fm"] or {}).get("receipt") or {}


def test_graph_scan_elides_the_receipt_evidence_payload(tmp_path):
    """covers: M1,M5 — the payload is absent from the graph on a receipt-bearing bundle."""
    root = _bundle(tmp_path, digest=5, ids=4)
    receipt = _receipt_fm(add.scan(root))
    # Positive control FIRST: the node must have been scanned at all, or absence proves nothing.
    assert receipt.get("kind") == "test-ids", f"the receipt node did not scan: {receipt!r}"
    for key in HEAVY:
        assert key not in receipt, f"scan parsed `{key}` into the graph: {receipt!r}"


def test_scan_node_raw_stays_byte_complete(tmp_path):
    """covers: M2,R:LOSSYRAW — `raw` is the file's own frontmatter, byte for byte.

    The one write path does its own read today, but a lean `raw` would be a loaded gun for
    the next writer that does not: it would silently drop every digest line on save.
    """
    root = _bundle(tmp_path, digest=4)
    node = add.scan(root)["/tasks/t.d/runs/1.md"]
    on_disk = (root / "tasks" / "t.d" / "runs" / "1.md").read_text(encoding="utf-8")
    expected, _ = add.split(on_disk)
    assert node["raw"] == expected, "scan returned a lossy `raw` — a write would drop bytes"
    assert "scope_digest" in node["raw"], "control: raw should still carry the elided block"


def test_direct_read_still_carries_the_payload(tmp_path):
    """covers: M3,A3 — `read()` is the public tiered API and is untouched."""
    root = _bundle(tmp_path, digest=3, ids=2)
    fm = add.read(root / "tasks" / "t.d" / "runs" / "1.md", "T0")["fm"]
    receipt = fm.get("receipt") or {}
    assert len(receipt.get("scope_digest") or []) == 3, receipt
    assert len(receipt.get("passed") or []) == 2, receipt


def test_latest_receipt_still_feeds_freshness_and_coverage(tmp_path):
    """covers: M3,R:BLINDGATE,A1 — the gate's two consumers see an intact receipt."""
    root = _bundle(tmp_path, receipts=2, digest=3, ids=2)
    receipt, cid = add.latest_receipt(root, "/tasks/t.md")
    assert cid == "/tasks/t.d/runs/2.md", cid
    assert len(receipt.get("scope_digest") or []) == 3, receipt
    assert len(receipt.get("passed") or []) == 2, receipt


def test_scanned_graph_is_otherwise_identical(tmp_path):
    """covers: M4,A2 — nothing but the three keys moved.

    Compares against a graph built from full `read()` calls. The elision assertion runs FIRST
    as a positive control: if the strip never fired, every other assertion here is vacuous.
    """
    root = _bundle(tmp_path, receipts=2, digest=4, ids=3)
    scanned = add.scan(root)
    full = {cid: add.read(root / cid.lstrip("/"), "T0") for cid in scanned}

    elided = [c for c in scanned
              if any(k in ((full[c]["fm"] or {}).get("receipt") or {}) for k in HEAVY)]
    assert elided, "control: no node carried an evidence payload — this test proves nothing"

    assert set(scanned) == set(full), set(scanned) ^ set(full)
    for cid in scanned:
        a, b = dict(scanned[cid]["fm"] or {}), dict(full[cid]["fm"] or {})
        ra, rb = dict(a.pop("receipt", {}) or {}), dict(b.pop("receipt", {}) or {})
        assert a == b, f"{cid}: a non-receipt key changed"
        for k in HEAVY:
            rb.pop(k, None)
        assert ra == rb, f"{cid}: a non-evidence receipt key changed"
        # `verified[]` must NOT be elided — edges and authority are read off it.
        assert ("verified" in a) == ("verified" in b)


def test_elision_is_anchored_to_the_receipt_block(tmp_path):
    """covers: E2 — a top-level `passed:` on a non-Run node is not evidence and survives."""
    root = _bundle(tmp_path)
    (root / "specs" / "quality.md").write_text(
        "---\ntype: Spec\ntitle: Quality\npassed:\n  - a keeper\n---\n## Now\nx\n",
        encoding="utf-8")
    fm = add.scan(root)["/specs/quality.md"]["fm"]
    assert fm.get("passed") == ["a keeper"], f"a non-receipt `passed:` was eaten: {fm!r}"


def test_bundle_with_no_receipts_is_unchanged(tmp_path):
    """covers: E3,M5 — no receipts, no elision, no difference."""
    root = _bundle(tmp_path, receipts=0)
    scanned = add.scan(root)
    assert scanned, "control: the receipt-free bundle produced an empty graph"
    for cid, node in scanned.items():
        assert node["fm"] == add.read(root / cid.lstrip("/"), "T0")["fm"], cid


def test_status_output_is_unchanged(tmp_path):
    """covers: A6 — a scan that got cheaper has nothing to say to the operator."""
    root = _bundle(tmp_path, receipts=2, digest=4)
    out = subprocess.run([sys.executable, str(REPO / "tooling" / "cli.py"),
                          "--root", str(root), "status"], capture_output=True, text=True)
    assert out.returncode == 0, out.stderr
    assert "scope_digest" not in out.stdout and "sha1:" not in out.stdout, out.stdout
    assert "b" in out.stdout, out.stdout


def test_receipt_with_an_empty_payload_still_scans(tmp_path):
    """covers: E1 — an empty or absent `passed:` makes the elision a no-op, not a failure.

    A `command-exit` receipt reports no ids at all, so `passed:`/`failed:` are present as bare
    keys with nothing under them. The block regex must consume the key line and stop, leaving a
    node that still scans with its non-evidence keys intact.
    """
    root = _bundle(tmp_path, receipts=0)
    (root / "tasks" / "t.d" / "runs").mkdir(parents=True, exist_ok=True)
    (root / "tasks" / "t.d" / "runs" / "1.md").write_text(
        "---\ntype: Run\nruntime: process\ntask: /tasks/t.md\n"
        'computation: "pytest -q"\n'
        "receipt:\n  kind: command-exit\n  exit: 0\n  passed:\n  failed:\n"
        "  at: 2026-09-03\n---\n## Notes\n", encoding="utf-8")
    receipt = _receipt_fm(add.scan(root))
    assert receipt.get("kind") == "command-exit", f"the node did not scan: {receipt!r}"
    assert receipt.get("at") == "2026-09-03", f"a key AFTER the empty block was eaten: {receipt!r}"
    for key in HEAVY:
        assert key not in receipt, f"an empty `{key}` leaked into the graph: {receipt!r}"
