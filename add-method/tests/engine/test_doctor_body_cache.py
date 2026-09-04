"""`doctor` reads each node's body once per run, not two or three times.

Measured before this task, on a 196-node graph: `doctor` performed 386 `read()` calls and
594 `parse()` calls, while `status` over the same graph parsed 208 times. Three loops each
re-read the same T2 bodies — fragment resolution re-reads a target once per incoming
fragment edge, the markdown-link loop reads every node again, and the placeholder loop
reads every lifecycle node a third time.

The parser is already hand-optimised, so the cost was never the parse. It was doing it
three times.

The dangerous half of this change is not speed, it is STALENESS: a cache that outlived one
call would let `doctor` report a finding computed from a body that has since been repaired
(R:STALEDOC), which is exactly the failure `doctor --sync` would then hide.
"""
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _bundle(tmp_path, *, fragments=0, bodies=2, empty=False):
    root = tmp_path / ".add"
    (root / "tasks").mkdir(parents=True)
    (root / "specs").mkdir(parents=True)
    (root / "index.md").write_text('---\nabf_version: "1.3"\nname: b\n---\n', encoding="utf-8")
    (root / "PROJECT.md").write_text("---\ntype: Project\ntitle: b\n---\n## CARD\ngoal: g\n",
                                     encoding="utf-8")
    (root / "specs" / "method.md").write_text(
        "---\ntype: Spec\ntitle: Method\n---\n## Now\nx\n\n## Decisions that bind\n- a real one\n",
        encoding="utf-8")
    for i in range(bodies):
        body = "" if empty else f"## CARD\ngoal: g{i}\nwhy: w\n\n## RULES\n<must>\n- M1 real\n</must>\n"
        # `fragments` edges from EVERY task point at the SAME target — E1's shape.
        edges = "".join(f"  - /specs/method.md#decisions-that-bind\n" for _ in range(fragments))
        rel = f"relates_to:\n{edges}" if edges else ""
        (root / "tasks" / f"t{i}.md").write_text(
            f"---\ntype: Task\ntitle: t{i}\nstatus: done\n{rel}---\n{body}", encoding="utf-8")
    return root


def _count_reads(root):
    """(reads_per_path, total) for one `doctor()` call."""
    seen, orig = [], add.read
    def spy(path, tier="T0"):
        if tier == "T2":
            seen.append(str(path))
        return orig(path, tier)
    add.read = spy
    try:
        add.doctor(root)
    finally:
        add.read = orig
    per = {}
    for p in seen:
        per[p] = per.get(p, 0) + 1
    return per, len(seen)


def test_doctor_reads_each_body_at_most_once(tmp_path):
    """covers: M1,E1,E2 — repeated fragment targets and dual-loop nodes read once."""
    root = _bundle(tmp_path, fragments=3, bodies=4)
    per, total = _count_reads(root)
    assert total > 0, "control: doctor read no bodies at all — this test proves nothing"
    repeated = {p: n for p, n in per.items() if n > 1}
    assert not repeated, f"these bodies were read more than once: {repeated}"


def test_doctor_findings_are_byte_identical(tmp_path):
    """covers: M2,A6 — same findings, same order; only the reading changed."""
    root = _bundle(tmp_path, fragments=2, bodies=3)
    (root / "tasks" / "scaffold.md").write_text(
        "---\ntype: Task\ntitle: s\nstatus: direction\n---\n## CARD\ngoal: <one line>\n",
        encoding="utf-8")
    (root / "tasks" / "t0.md").write_text(
        (root / "tasks" / "t0.md").read_text(encoding="utf-8")
        + "\nSee [gone](./nowhere.md) and [there](./t1.md).\n", encoding="utf-8")
    findings = add.doctor(root)
    codes = [f["code"] for f in findings]
    assert codes, "control: a bundle seeded with a scaffold and a broken link produced no findings"
    assert "broken_md_link" in codes, codes
    assert "unauthored_node" in codes, codes
    assert add.doctor(root) == findings, "doctor is not deterministic across calls"


def test_doctor_cache_does_not_survive_the_call(tmp_path):
    """covers: M3,R:STALEDOC,A1 — the second call sees an edit the first could not.

    This is the check that matters. A module-level or memoised-across-calls cache passes
    every other test in this file and fails only here.
    """
    root = _bundle(tmp_path, bodies=1)
    (root / "tasks" / "t0.md").write_text(
        "---\ntype: Task\ntitle: t0\nstatus: direction\n---\n## CARD\ngoal: <one line>\n",
        encoding="utf-8")
    before = [f["code"] for f in add.doctor(root)]
    assert "unauthored_node" in before, f"control: the scaffold was not flagged: {before}"

    (root / "tasks" / "t0.md").write_text(
        "---\ntype: Task\ntitle: t0\nstatus: direction\n---\n"
        "## CARD\ngoal: a real authored goal\nwhy: a real reason\n"
        "\n## RULES\n<must>\n- M1 authored\n</must>\n", encoding="utf-8")
    after = [f["code"] for f in add.doctor(root)]
    assert "unauthored_node" not in after, (
        f"R:STALEDOC — the repair was invisible to the second call: {after}")


def test_doctor_never_reads_a_body_it_does_not_need(tmp_path):
    """covers: M4,R:PREFETCH,A3 — lazy, never a prefetch that games the count."""
    no_frag = _bundle(tmp_path / "a", fragments=0, bodies=3)
    with_frag = _bundle(tmp_path / "b", fragments=2, bodies=3)
    _, total_no = _count_reads(no_frag)
    _, total_yes = _count_reads(with_frag)
    assert total_no <= total_yes, (
        f"a fragment-free bundle read MORE bodies ({total_no}) than one with fragments "
        f"({total_yes}) — the cache is prefetching")
    # and the count must track the graph, not be a constant
    bigger = _bundle(tmp_path / "c", fragments=0, bodies=8)
    _, total_big = _count_reads(bigger)
    assert total_big > total_no, "read count does not grow with the graph — is doctor reading at all?"


def test_empty_body_is_cached_not_reread(tmp_path):
    """covers: E3,A4 — absence of content is not absence of a cache entry."""
    root = _bundle(tmp_path, fragments=1, bodies=2, empty=True)
    per, _ = _count_reads(root)
    repeated = {p: n for p, n in per.items() if n > 1}
    assert not repeated, f"empty-bodied nodes were re-read: {repeated}"


def test_doctor_body_reads_equal_the_nodes_that_need_one(tmp_path):
    """covers: A2 — an EXACT total, not merely "no repeats".

    "No path read twice" is satisfied by a cache that covers three of four sites, because the
    fourth would simply be the single read of some node. Pinning the TOTAL against the graph is
    what makes a fifth uncached site a failure instead of a quietly smaller win. That is not
    hypothetical: this task's first reading said "the three loops inside doctor()" and a
    traceback during build found a fourth, in `card_drift`.
    """
    root = _bundle(tmp_path, fragments=3, bodies=5)
    per, total = _count_reads(root)
    graph = add.scan(root)
    # Every graph node's body is wanted by the markdown-link loop, which is unconditional.
    assert total == len(graph), (
        f"doctor read {total} bodies for a {len(graph)}-node graph — "
        f"an uncached site remains, or a body is read that nothing needs")
    assert set(per) == {str(n["path"]) for n in graph.values()}, "read set != graph node set"
