"""Red suite for `refuse-with-one-shape` — `None` is the refusal, bundle-wide.

Two checks in one branch were GREEN only because `freeze` refused with `False`, and
`False is not None`. Eleven verbs still answer that way. Each is self-consistent, so none of
them looks wrong on its own — the caller crossing two verbs is the one who pays.

The sweep is NOT "every False becomes None". Three of the 38 are honest ANSWERS: `fresh` says
`False` when a receipt is genuinely stale, and `render_card` says `False` when the card is
already current. Rewriting those would destroy the one thing those verbs are for. The rule is
the question — did the verb DO its work, or ANSWER a question?
"""

import ast
import inspect
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

ENGINE = REPO / "tooling" / "add.py"

# The three falsy returns that are RESULTS, not refusals — each verb's honest "no". Keyed by
# the verb and the exact message, never by line number, so the list survives an edit above it.
HONEST_NO = {
    ("fresh", "has vanished since the run"),
    ("fresh", "changed since the run"),
    ("render_card", "card is current"),
}


def _returns():
    """Every `return <falsy>, <msg>` in the engine: (verb, line, value, first message string)."""
    out = []
    for fn in [n for n in ast.parse(ENGINE.read_text()).body if isinstance(n, ast.FunctionDef)]:
        for n in ast.walk(fn):
            if not (isinstance(n, ast.Return) and isinstance(n.value, ast.Tuple)
                    and len(n.value.elts) == 2):
                continue
            first = n.value.elts[0]
            if not (isinstance(first, ast.Constant) and first.value in (False, None)
                    and not isinstance(first.value, int) or
                    isinstance(first, ast.Constant) and first.value is False):
                if not (isinstance(first, ast.Constant) and first.value is None):
                    continue
            msg = " ".join(c.value for c in ast.walk(n.value.elts[1])
                           if isinstance(c, ast.Constant) and isinstance(c.value, str))
            out.append((fn.name, n.lineno, first.value, msg))
    return out


def _is_honest_no(verb, msg):
    return any(verb == v and frag in msg for v, frag in HONEST_NO)


def test_every_refusal_in_the_engine_is_none():
    """covers: M1, M4, R:TWOSHAPES, A5, A6, E6 — enumerated, so a new verb cannot drift."""
    offenders = [(v, ln, msg) for v, ln, val, msg in _returns()
                 if val is False and not _is_honest_no(v, msg)]
    assert not offenders, (
        "R:TWOSHAPES — these verbs refuse with `False`, so a caller writing `if x is None` walks "
        "straight past them:\n"
        + "\n".join(f"  add.py:{ln}  {v}()  — {msg.strip()[:70]}" for v, ln, msg in offenders)
        + "\n\nThe question that decides each one: did the verb DO its work (a refusal → `None`), "
          "or ANSWER a question (a result → keep the boolean, and add it to HONEST_NO here)?")


def test_an_honest_no_keeps_its_boolean(tmp_path):
    """covers: M2, M3, R:LOSTANSWER, A2, A3, E1, E2 — no and cannot-tell are different facts."""
    found = {(v, msg.strip()[:40]) for v, _, val, msg in _returns() if val is False}
    assert len(found) == len(HONEST_NO), (
        f"R:LOSTANSWER — the engine keeps {len(found)} boolean result(s); this task documents "
        f"{len(HONEST_NO)}:\n  kept: {sorted(found)}")

    # `fresh` is the verb where the sweep would have destroyed the meaning. Three states now.
    src = inspect.getsource(add.fresh)
    assert "return None" in src, \
        "E1 — `fresh` cannot say `cannot establish`; an unmeasurable receipt reads as stale"
    assert src.count("return False") == 2, (
        "E1 — `fresh` must keep BOTH honest answers (vanished, changed) as `False`: a stale "
        "receipt is the answer, not a failure to answer")


def test_no_caller_is_blind_to_the_change():
    """covers: M6, R:SILENTCALLER, A1, A4, E3, E4 — an assertion true under both shapes proves nothing.

    Narrowly aimed, on purpose. `assert not hits` about a list of grep matches has nothing to do
    with this contract; what matters is a name BOUND from a verb's first element and then tested
    for falsiness, because that assertion passes on `False` and on `None` alike and cannot say
    which the verb gave. That is the exact shape that let two checks pass on a refusal.
    """
    # Verbs whose falsy answer is a RESULT, so a truthiness test on them is deliberate, not
    # blind (E4). Two shapes: a boolean no (`fresh` stale, `render_card` current), and an empty
    # collection from a query that RAN and matched nothing — which is an answer, not a failure.
    RESULT_VERBS = {"fresh", "render_card",
                    "deltas", "search", "interview", "todo", "locate", "neighborhood"}
    blind = set()
    for f in sorted((REPO / "tests").rglob("test_*.py")):
        if f.name == Path(__file__).name:
            continue
        tree = ast.parse(f.read_text())
        for fn in ast.walk(tree):
            if not isinstance(fn, (ast.FunctionDef, ast.Module)):
                continue
            bound = {}
            for n in ast.walk(fn):
                # `ok, note = add.<verb>(...)` — remember the name and the verb it came from.
                if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call):
                    # ONLY `add.<verb>(...)` — a name bound from `sorted()` or a local helper is
                    # not this contract, and flagging it would train the reader to ignore this.
                    call = n.value.func
                    if not (isinstance(call, ast.Attribute)
                            and isinstance(call.value, ast.Name) and call.value.id == "add"):
                        continue
                    fname = call.attr
                    for t in n.targets:
                        names = t.elts if isinstance(t, ast.Tuple) else [t]
                        if names and isinstance(names[0], ast.Name):
                            bound[names[0].id] = fname
                if (isinstance(n, ast.Assert) and isinstance(n.test, ast.UnaryOp)
                        and isinstance(n.test.op, ast.Not)
                        and isinstance(n.test.operand, ast.Name)):
                    name = n.test.operand.id
                    verb = bound.get(name)
                    if verb and verb not in RESULT_VERBS:
                        blind.add(f"  {f.relative_to(REPO).as_posix()}:{n.lineno}  "
                                  f"`assert not {name}` — bound from `add.{verb}()`")
    assert not blind, (
        "R:SILENTCALLER — these assertions pass under both the old shape and the new, so they "
        f"prove nothing about either ({len(blind)} sites):\n" + "\n".join(sorted(blind)[:25])
        + "\n\nOn a REFUSAL path write `is None`; the point is that the assertion names which "
          "falsy value it means.")


def test_the_messages_are_untouched():
    """covers: M5 — only the falsy first element moved."""
    # Against the branch's MERGE-BASE, not HEAD. A working-tree diff goes green the moment you
    # commit, which would make this check vacuous exactly when it matters — the lesson this repo
    # bound as a decision two tasks ago (`a scope guard names the commit range it guards`).
    base = subprocess.run(["git", "merge-base", "HEAD", "origin/main"],
                          cwd=str(REPO.parent), capture_output=True, text=True)
    assert base.returncode == 0, "no merge-base with origin/main; the message pin cannot run"
    head = subprocess.run(["git", "show", f"{base.stdout.strip()}:add-method/tooling/add.py"],
                          cwd=str(REPO.parent), capture_output=True, text=True)
    assert head.returncode == 0, "the engine is not tracked; the message pin cannot run"
    before = {(v, msg) for v, _, _, msg in _returns_from(head.stdout)}
    after = {(v, msg) for v, _, _, msg in _returns()}
    # LOSSES only. A reworded message shows up as one loss and one gain, so asserting the losses
    # still catches every edit this task could make — while a message ADDED since the merge-base
    # is a later rung's doing (`drop`, `R:SILENTABANDON`) and not this check's business. Asserting
    # gains too would have made the pin fire on every stacked branch and be waved past.
    lost = before - after
    assert not lost, (
        "M5 — this task moves the falsy first element and NOTHING else, but these refusal "
        "messages were lost or reworded:\n"
        + "".join(f"  - {v}: {m.strip()[:70]}\n" for v, m in sorted(lost)))


def _returns_from(source: str):
    out = []
    for fn in [n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef)]:
        for n in ast.walk(fn):
            if (isinstance(n, ast.Return) and isinstance(n.value, ast.Tuple)
                    and len(n.value.elts) == 2
                    and isinstance(n.value.elts[0], ast.Constant)
                    and n.value.elts[0].value in (False, None)):
                msg = " ".join(c.value for c in ast.walk(n.value.elts[1])
                               if isinstance(c, ast.Constant) and isinstance(c.value, str))
                out.append((fn.name, n.lineno, n.value.elts[0].value, msg))
    return out


def test_the_exit_code_is_unchanged(tmp_path):
    """covers: E5 — `cli.py` reads the first element as an exit code, by truthiness."""
    add.init(tmp_path, "code", "Exit")
    cli = [sys.executable, str(REPO / "tooling" / "cli.py"), "--root", str(tmp_path)]
    for argv, want, why in (
            (["reopen", "nope", "--to", "build", "--reason", "x"], 1, "a refusal exits non-zero"),
            (["drop", "nope", "--reason", "x"], 1, "a refusal exits non-zero"),
            (["learn", "add", "a real lesson", "--evidence", "somewhere"], 0, "a success exits zero"),
    ):
        got = subprocess.run(cli + argv, capture_output=True, text=True).returncode
        assert got == want, f"E5 — `add {argv[0]}` exited {got}, wanted {want} ({why})"
