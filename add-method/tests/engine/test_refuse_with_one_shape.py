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
import hashlib
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



MESSAGE_DIGEST = "bd6707ccc342a09415198d9a2eb54078a1aeee185018c10b78290fa33d7849ab"  # re-aimed @ the-message-pin-is-a-content-pin: the baseline was `git merge-base HEAD origin/main`, which returns 128 on CI's depth-1 clone and CONTAINS the change once merged. Same claim, a baseline that survives both. prior: (a git merge-base, never a digest)
MESSAGE_COUNT = 98


def _message_digest() -> tuple:
    """`(sha256 over the sorted (verb, message) pairs, their count)` — the pin's own subject.

    Computed by calling the module's own extractor, so there is exactly ONE reading of what a
    refusal message is (M4). Sorted before hashing, so the digest is a function of the CONTENT and
    not of the order `ast.walk` happened to yield (A5).
    """
    pairs = sorted((verb, " ".join(msg.split())) for verb, _, _, msg in _returns())
    blob = "\n".join(f"{v}\x1f{m}" for v, m in pairs).encode()
    return hashlib.sha256(blob).hexdigest(), len(pairs)


def test_the_messages_are_untouched():
    """covers: M5 — only the falsy first element moved.

    RE-AIMED (the-message-pin-is-a-content-pin): this read its baseline from
    `git merge-base HEAD origin/main`, which returns 128 on `actions/checkout`'s depth-1 clone —
    so it passed locally and failed CI, reading *cannot establish a baseline* as *the claim is
    false*. And a merge-base CONTAINS the change once the branch merges, so the day CI could run
    it, it would have proved nothing. The claim is unchanged; the baseline is now a pin over the
    content itself, the way `test_skill_tree_prose_unedited_by_this_task` and `engine_pin.py`
    already hold theirs.
    """
    got, count = _message_digest()
    assert got == MESSAGE_DIGEST, (
        f"M5 — a refusal message was reworded or lost ({count} messages now, {MESSAGE_COUNT} when "
        f"the pin was aimed).\n  pinned: {MESSAGE_DIGEST}\n  actual: {got}\n\n"
        "Two exits, and only two: restore the wording, or re-aim the pin IN THE SAME COMMIT with "
        "the task and the reason on its line. A digest cannot name which message moved — "
        "`git diff` on the engine can, and knowing why is the point of re-aiming it by hand.")
    assert count == MESSAGE_COUNT, \
        f"the message COUNT moved ({MESSAGE_COUNT} -> {count}) — re-aim both, with the reason"


def test_the_pin_records_why_it_points_here():
    """covers: M3, R:SILENTREPIN, A1, A3 — a pin with no reason is a number nobody can audit."""
    src = Path(__file__).read_text(encoding="utf-8")
    line = next(l for l in src.splitlines() if l.startswith("MESSAGE_DIGEST ="))
    assert "re-aimed @" in line, \
        "R:SILENTREPIN — the digest names no task that aimed it"
    assert len(line.split("re-aimed @", 1)[1].strip()) > 40, \
        "R:SILENTREPIN — the digest names a task but no reason; a slug is not a why"


def test_the_guard_never_degrades_to_green():
    """covers: R:SKIPTOGREEN — the easy fix for a red baseline is the one that must not exist."""
    # By AST, not substring: the docstring below says the word "returns", and a scan that flags
    # prose trains the reader to ignore the check. Only real control flow counts.
    tree = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
              and n.name == "test_the_messages_are_untouched")
    escapes = []
    for n in ast.walk(fn):
        if isinstance(n, (ast.Return, ast.Try)):
            escapes.append(type(n).__name__)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) \
                and n.func.attr in ("skip", "xfail"):
            escapes.append(f"pytest.{n.func.attr}")
        if isinstance(n, ast.Name) and n.id == "subprocess":
            escapes.append("subprocess")
    assert not escapes, (
        f"R:SKIPTOGREEN — the message guard grew {sorted(set(escapes))}. A guard that goes green "
        f"when it cannot establish its subject is worse than the red it replaced: it reports "
        f"success on every possible engine. The pin exists so there is nothing to fail to reach.")


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
