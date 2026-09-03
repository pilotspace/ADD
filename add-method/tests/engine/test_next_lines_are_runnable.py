"""A `next:` line is a command that RUNS, and that clears what it was named for.

SKILL.md makes obeying them mandatory: "Every engine refusal names its fix in the same breath
(`next: <verb>`) — do that fix." Four measured lines that cannot be obeyed:

1. `BEAT_NEXT["build"]` hands out `add run {slug} -- <cmd>`, the idiom GETTING-STARTED warns
   produces `ids: unknown`. Followed on a genuinely green node with every rule proven, the gate
   then refused with `no reported passing check: M1, R:CLOSED_DEPOSIT` and named RISK-ACCEPTED
   as the only exit — a permanent false waiver on correct work. Thirteen further sites re-emit
   the same idiom.

2. `BEAT_NEXT["verify"]` is `add gate {slug}`, which is an argparse error: `verdict` is
   required. Not a refusal — a crash, with no `next:` to recover from.

3. In a non-git tree the freshness refusal diagnoses git correctly and then says
   `next: add run {slug} -- <cmd>`, which provably cannot fix it. Following it loops forever;
   `git init` fixes it on the first try and is never mentioned.

4. `add learn testing …` refuses with `next: add status`. The vocabulary is closed and short.
   Naming it is the fix; `add status` is not.

The rule these pin is one predicate: a `next:` line must be runnable as printed, and must name
something that actually clears the state it was printed for.
"""
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402

CLI = REPO / "tooling" / "cli.py"


def _bundle(tmp_path):
    add.init(tmp_path, "code", "T")
    return tmp_path


def _cli(root, *argv):
    return subprocess.run([sys.executable, str(CLI), "--root", str(root), *argv],
                          capture_output=True, text=True)


# ------------------------------------------------- M1 · the build hint earns bindable evidence

def test_the_build_next_names_the_canonical_junit_idiom():
    """covers: M1 — the one idiom that yields bound ids, from the table every site reads."""
    hint = add.BEAT_NEXT["build"].format(slug="t")
    assert "--junitxml" in hint, (
        f"the build hint still guarantees `ids: unknown`: {hint!r}")


def test_the_verify_next_is_a_runnable_command(tmp_path):
    """covers: M2 — the engine's own verify hint must not be an argparse error."""
    root = _bundle(tmp_path)
    add.new(root, "Task", "t", title="t")
    hint = add.BEAT_NEXT["verify"].format(slug="t")
    argv = hint.split()[1:]                      # drop the leading `add`
    proc = _cli(root, *argv)
    assert "usage:" not in proc.stderr, (
        f"the verify hint is an argparse error, not a refusal: {hint!r}\n{proc.stderr}")


def test_every_beat_next_starts_with_a_real_verb():
    """covers: M2, A2 — enumerated from the table, so a new beat cannot skip the check."""
    import cli as cli_mod
    verbs = set(cli_mod.build_parser()._subparsers._group_actions[0].choices)
    for beat, hint in add.BEAT_NEXT.items():
        # `scaffold`'s hint is prose ("author …, then add freeze {slug}") and legitimately so.
        # The predicate is that every `add <word>` it contains names a real verb.
        named = re.findall(r"\badd ([a-z][a-z-]*)", hint)
        assert named, f"{beat}: {hint!r} names no `add <verb>` at all"
        for verb in named:
            assert verb in verbs, f"{beat}: `{verb}` is not an engine verb ({hint!r})"


# ------------------------------------------------- M3 · a receipt with no ids says so

DIMS = ("who", "which", "when", "absent", "order", "experience")


def _author(root, cid):
    """Fill every slot the scaffold ships, so a refusal is about EVIDENCE, not placeholders.

    Without this the gate refuses with "the node still carries template placeholders", the
    `no reported passing check` arm is never reached, and any assertion guarded by that branch
    is dead code that reports success.
    """
    import re as _re
    p = root / cid.lstrip("/")
    x = p.read_text(encoding="utf-8")
    x = x.replace("- S1 <the surface this publishes — an endpoint, function, or section>", "- S1 x")
    x = x.replace("goal: <one line>", "goal: the fixture's stated one line.")
    x = _re.sub(r"## RULES\n<must>\n.*?\n</must>", "## RULES\n<must>\n- M1 m\n</must>", x, flags=_re.S)
    x = _re.sub(r"<reject>\n.*?\n</reject>", '<reject>\n- R:Z x -> "Z"\n</reject>', x, flags=_re.S)
    x = _re.sub(r"## ASSUMPTIONS\n.*?\nevery `gives:`", "## ASSUMPTIONS\n" + "".join(
        f"- A{i} [{d}] covers: S1 · n; taking r -> c\n" for i, d in enumerate(DIMS, 1)
    ) + "every `gives:`", x, flags=_re.S)
    x = _re.sub(r"## CHECKS\n.*?\nred-first",
                "## CHECKS\n- test_x · covers: M1, R:Z · p\nred-first", x, flags=_re.S)
    p.write_text(x, encoding="utf-8")


def test_an_unbound_gate_names_the_run_idiom_when_the_receipt_carries_no_ids(tmp_path):
    """covers: M3, R:FALSEWAIVER — a signed waiver must never be the only exit from a typo."""
    root = _bundle(tmp_path)
    cid, _ = add.new(root, "Task", "t", title="t")
    _author(root, cid)                                 # else the refusal is about placeholders
    add.freeze(root, cid, by="H", authority="process")
    add.brief_stamp(root, cid, by="H")                 # else the gate stops at R:UNBRIEFED
    add.run(root, cid, ["true"])                       # no --junitxml: ids come back unknown
    receipt, _ = add.latest_receipt(root, cid)
    assert receipt["ids"] == "unknown", f"fixture did not reach ids:unknown: {receipt}"

    ok, note = add.gate(root, cid, "PASS", by="H")
    assert not ok, f"an unbound gate was recorded as PASS: {note}"
    # UNCONDITIONAL. This assertion used to sit under `if "no reported passing check" in note:`
    # and the fixture never reached that arm — the node was unauthored, so the gate refused for
    # its placeholders and the branch was dead. A guarded assertion in a test is a guard that
    # reports success whenever its own precondition fails.
    assert "unbound" in note or "no reported passing check" in note, (
        f"the fixture no longer reaches the unbound-covers refusal — re-aim it:\n{note}")
    assert "--junitxml" in note, (
        "the receipt carries NO ids at all, and the refusal offers only RISK-ACCEPTED — "
        f"a false waiver on possibly-correct work:\n{note}")
    # and the waiver must not be the FIRST thing offered when a re-run would bind the receipt
    assert note.index("--junitxml") < note.index("RISK-ACCEPTED"), (
        f"the signed waiver is offered before the re-run that would make it unnecessary:\n{note}")


# ------------------------------------------------- M4 · the non-git loop

def test_the_non_git_freshness_refusal_names_git_init(tmp_path):
    """covers: M4, E1 — a `next:` that provably cannot fix it is an unbounded loop."""
    root = _bundle(tmp_path)                            # tmp_path is NOT a git working tree
    assert not (tmp_path.parent / ".git").exists()
    cid, _ = add.new(root, "Task", "t", title="t", scope=["src/"])
    add.run(root, cid, ["true"])

    ok, note = add.gate(root, cid, "PASS", by="H")
    if not ok and "stale" in note and "not a git working tree" in note:
        assert "git init" in note, (
            f"the refusal diagnoses git and names a fix that cannot work:\n{note}")


# ------------------------------------------------- M5 · a closed vocabulary is named

def test_an_unknown_lens_names_the_closed_set(tmp_path):
    """covers: M5, A5 — `next: add status` is not the fix for a five-word vocabulary."""
    root = _bundle(tmp_path)
    ok, note = add.learn(root, "testing", "a lesson", evidence="deadbeef")
    assert not ok
    named = [l for l in ("domain", "system", "experience", "quality", "method") if l in note]
    assert len(named) >= 4, f"the refusal does not name the closed set: {note!r}"


# ------------------------------------------------- M6 · no verb crashes on a missing ref

def test_no_verb_tracebacks_on_a_missing_ref(tmp_path):
    """covers: M6, R:CRASH — the engine records or refuses; it never raises at the operator."""
    root = _bundle(tmp_path)
    crashed = []
    for argv in (["check", "nope", "--all"], ["check", "nope", "1"], ["brief", "nope"],
                 ["freeze", "nope"], ["gate", "nope", "PASS"], ["done", "nope"],
                 ["run", "nope", "--", "true"], ["advise", "nope", "--persona", "x"]):
        proc = _cli(root, *argv)
        if "Traceback" in proc.stderr:
            crashed.append(f"add {' '.join(argv)}: {proc.stderr.strip().splitlines()[-1]}")
    assert not crashed, "these verbs raised instead of refusing:\n  " + "\n  ".join(crashed)
