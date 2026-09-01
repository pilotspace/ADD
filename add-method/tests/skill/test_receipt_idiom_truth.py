"""The run line the skill tells you to copy is a line that earns a bound receipt.

Red-first for `/tasks/receipt-idiom-truth.md`.

`--junitxml` on `add run` is READ-ONLY: the engine passes the wrapped argv through unchanged,
so a command that does not itself write the report leaves nothing to read. The receipt then
records `kind: command-exit`, `reported` is empty, every `covers:` referent is unbound, and the
gate refuses the PASS naming `unbound_covers` — a message that says nothing about the missing
flag on the user's own command. Measured 2026-09-01: all three canonical renderings showed
`-- <test cmd>` with no report-writing half. This repo's own receipts carry the correct idiom,
and the lesson was recorded on an earlier node; it never reached the shipped skill.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "skill" / "add"
sys.path.insert(0, str(REPO / "tooling"))

# Every `add run` example across the shipped skill tree, enumerated from the FILES (M3) —
# a hand list would go stale the day someone adds an example, which is the failure mode.
RUN_LINE = re.compile(r"add run\s+\S+.*?--\s+(?P<cmd>.+)$")


def _run_examples():
    """Every `add run` example, with shell continuations JOINED first.

    A command that wraps with a trailing `\\` carries the half that matters on the NEXT
    physical line — reading one line at a time is how a guard reads green over a claim that
    is still there, which this repo has paid for twice.
    """
    out = []
    for f in sorted(SKILL.rglob("*.md")):
        raw = f.read_text(encoding="utf-8").splitlines()
        i = 0
        while i < len(raw):
            start, line = i + 1, raw[i].rstrip()
            while line.endswith("\\") and i + 1 < len(raw):
                i += 1
                line = line[:-1].rstrip() + " " + raw[i].strip()
            if "add run " in line and "--" in line:
                m = RUN_LINE.search(line.strip().strip("`"))
                if m:
                    out.append((f.relative_to(SKILL), start, line.strip(), m.group("cmd")))
            i += 1
    return out


def _reads_a_report(line: str) -> bool:
    return "--junitxml" in line.split("--", 1)[0] or "add-run.xml" in line.split(" -- ")[0]


def test_every_printed_run_example_writes_its_report():
    """covers: M1, M3, R:HOLLOWRUN · examples enumerated from the tree; each writes what run reads."""
    examples = _run_examples()
    assert examples, "no `add run` example found in the skill tree — the guard would be vacuous"
    hollow = []
    for rel, lineno, line, cmd in examples:
        if not _reads_a_report(line):
            continue                      # not a report-reading example; nothing to bind
        if "junitxml" not in cmd and "add-run.xml" not in cmd:
            hollow.append(f"{rel}:{lineno} — the wrapped command writes no report: {line}")
    assert not hollow, (
        "these printed examples produce a `command-exit` receipt when copied verbatim, and the "
        "gate then refuses every bound rule:\n  " + "\n  ".join(hollow))


def test_verify_states_run_only_reads_the_report():
    """covers: M2, A3 · the read/write split is stated in words, not only shown."""
    text = " ".join((SKILL / "phases" / "verify.md").read_text(encoding="utf-8").split())
    assert "reads" in text and "writes" in text, \
        "verify.md never says that `run` READS the report and the wrapped command WRITES it"


def test_the_domains_example_still_passes():
    """covers: E1, A1 · the incumbent non-pytest example satisfies the guard."""
    hits = [e for e in _run_examples() if str(e[0]) == "domains.md"]
    assert hits, "domains.md no longer carries a run example"
    for rel, lineno, line, cmd in hits:
        if _reads_a_report(line):
            assert "add-run.xml" in cmd, f"{rel}:{lineno} regressed: {line}"


def test_a_deliberately_receiptless_example_is_not_flagged():
    """covers: E2 · the guard scopes itself to report-READING examples only."""
    assert not _reads_a_report("add run slug -- python3 -m pytest -q")


def test_skill_md_is_within_its_line_pin():
    """covers: M4, E3 · the budget holds after the edit — funded by compression, never a bump."""
    lines = (SKILL / "SKILL.md").read_text(encoding="utf-8").splitlines()
    assert len(lines) <= 176, f"SKILL.md is {len(lines)} lines, over its pinned 176"


def test_no_engine_behaviour_changes_in_this_task():
    """covers: A2 · no engine behaviour changes in this task.

    A2 took the incumbent handling of a MISSING JUnit report as correct: the receipt honestly
    records `command-exit` and the gate then refuses every bound rule. The failure the assumption
    names is a fix that HIDES the failure instead of preventing it — an engine that quietly
    synthesizes IDs, or downgrades the refusal. So the probe is behavioural, not textual: drive a
    run with no report and assert the engine still records the weak kind and still refuses.
    """
    import subprocess
    import tempfile

    sys.path.insert(0, str(REPO / "tooling"))
    import add

    root = Path(tempfile.mkdtemp())
    add.init(root, "code", "T")
    cid, _ = add.new(root, "Task", "unreported", title="unreported", depth="quick")
    node = root / cid.lstrip("/")
    t = node.read_text(encoding="utf-8")
    t = t.replace("goal: <one line>", "goal: a real authored goal.")
    t = t.replace("- S1 <the surface this publishes — an endpoint, function, or section>",
                  "- S1 a real surface")
    t = re.sub(r"## CHECKS\n.*?\nred-first",
               "## CHECKS\n- test_a_bound_check · covers: goal · proves it\nred-first",
               t, flags=re.S)
    node.write_text(t, encoding="utf-8")

    missing = str(root / "never-written.xml")
    # Read the path `run` RETURNS: the receipt dir is derived from a shortened slug, and a
    # hand-built path silently misses the file and fails for the wrong reason.
    out = add.run(root, "unreported", ["python3", "-c", "pass"], junit=missing)
    assert out["receipt"]["kind"] == "command-exit", \
        f"a run with no report no longer records the WEAK kind: {out['receipt']['kind']}"
    assert out["receipt"]["passed"] == [], "the engine claimed reported IDs it never read"
    body = Path(out["path"]).read_text(encoding="utf-8")
    # Read the KIND FIELD, not the whole file: the receipt's honest note contains the words
    # "does not claim `test-ids`", so a substring scan reads the disclosure as the claim.
    kind = re.search(r"^\s*kind:\s*(\S+)", body, re.M)
    assert kind and kind.group(1).strip("`\"'") == "command-exit", \
        f"the written receipt disagrees with the returned one: {body[:400]}"

    # And the gate still REFUSES on that receipt — the assumption's whole point is that the
    # weakness stays visible rather than being papered over.
    node = root / cid.lstrip("/")
    verdict = add.gate(root, cid, "PASS", by="prober")
    refusal = verdict[1] if isinstance(verdict, tuple) else str(verdict)
    assert "cannot record" in refusal or "no reported passing check" in refusal, \
        f"the gate accepted a PASS on a receipt that bound nothing: {refusal}"
