"""`--json` — one envelope, both read verbs, byte-stable across runs.

Red-first for `/tasks/json-emission.md`.

`show` and `search` are the two doors a machine reads this bundle through, and until now both
answered only in prose. A consumer that parses the human render is coupled to wording no test
pins. Two failures a happy-path test would never see drive most of these checks:

* a refusal rendered as JSON that exits 0 reads, to any caller checking the status code, as an
  answer (R:FALSESUCCESS);
* an envelope whose bytes move because a dict iterated differently, or because a release bumped
  a version string into the payload, fails INTERMITTENTLY — the worst way to fail (R:UNSTABLE).

The envelope is `results[] + edges[]` because that is the one shape both verbs fit: `show` is
one node plus its walk, `search` is N hits and no walk.
"""

import inspect
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402

CLI = [sys.executable, str(REPO / "tooling" / "cli.py")]
KEYS = {"schema", "verb", "ok", "request", "results", "edges", "note"}


@pytest.fixture
def bundle(tmp_path):
    """A milestone, two tasks under it, one isolated node, and a non-ASCII body."""
    root = tmp_path / ".add"
    add.init(root, profile="code", title="payload fixture")
    add.new(root, "Milestone", "m-one", title="a milestone")
    add.new(root, "Task", "t-one", title="a task under the milestone", milestone="m-one")
    add.new(root, "Task", "t-two", title="a second task", milestone="m-one")
    add.new(root, "Persona", "p-lone", title="an isolated node")   # carries no status:
    node = root / "tasks" / "t-one.md"
    node.write_text(node.read_text(encoding="utf-8") + "\nédge · café — naïve\n",
                    encoding="utf-8")
    return root


def _cli(root, *args):
    """Run the CLI and hand back `(exit, stdout, stderr)` — bytes decoded, never parsed."""
    p = subprocess.run(CLI + ["--root", str(root), *args], capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


# ------------------------------------------------------------------ M1 · one envelope

def test_both_verbs_emit_one_envelope(bundle):
    """M1, R:TWOSHAPES, A2, A10 — identical key sets, and neither adapter names them itself."""
    show, _ = add.show_payload(bundle, "t-one")
    found, _ = add.search_payload(bundle, "task")
    assert set(show) == set(found) == KEYS, \
        f"the two payloads disagree: show={sorted(show)} search={sorted(found)}"
    assert show["verb"] == "show" and found["verb"] == "search"
    assert found["edges"] == [], "`search` must carry an EMPTY edges list, never a missing key"
    for name in ("show_payload", "search_payload"):
        src = inspect.getsource(getattr(add, name))
        assert "read_payload(" in src, f"`{name}` does not go through the one builder"
        assert '"schema"' not in src, f"`{name}` names an envelope key itself (R:TWOSHAPES)"


def test_stdout_is_byte_stable_across_runs(bundle):
    """M2, R:UNSTABLE, A12 — the same command twice over an unchanged bundle, identical bytes."""
    for args in (("show", "t-one", "--json"), ("search", "task", "--json"),
                 ("search", "--milestone", "m-one", "--json")):
        first = _cli(bundle, *args)
        second = _cli(bundle, *args)
        assert first[0] == 0, f"{args} refused: {first[1]}{first[2]}"
        assert first[1] == second[1], f"{args} is not byte-stable across runs"


# ------------------------------------------------------------------ M3/M4 · refusals

# Deliberately NOT parametrized: a `covers:` binding names a test ID, and pytest renames a
# parametrized case to `test_x[args0]`, so the node's rule would bind nothing at all.
REFUSALS = (
    ("show", "t-one", "--expand", "9"),          # over the cap
    ("show", "no-such-node-anywhere"),           # resolves to nothing
    ("search",),                                 # no query and no filter
)


def test_a_refusal_is_a_payload_not_a_traceback(bundle):
    """M3, E1 — a refusal emits the envelope, `ok` false, and carries its own `next:` line."""
    for args in REFUSALS:
        code, out, err = _cli(bundle, *args, "--json")
        body = json.loads(out)
        assert set(body) == KEYS, f"{args} emitted a different shape: {sorted(body)}"
        assert body["ok"] is False, f"{args} was reported as ok"
        assert "next:" in body["note"], f"{args} dropped its fix: {body['note']!r}"
        assert not err.strip(), f"{args} wrote to stderr as well: {err!r}"


def test_a_refusal_keeps_its_exit_code(bundle):
    """M4, R:FALSESUCCESS, E1, A15 — and the same command SUCCEEDS when it should (floor)."""
    assert _cli(bundle, "show", "t-one", "--json")[0] == 0, \
        "the floor failed: a good `show --json` does not exit 0, so a non-zero proves nothing"
    for args in REFUSALS:
        assert _cli(bundle, *args, "--json")[0] != 0, f"{args} exited 0 under --json"


# ------------------------------------------------------------------ M5 · stdout is the payload

def test_json_owns_stdout_alone(bundle):
    """M5, R:DIRTYSTDOUT — stdout parses WHOLE, with no prose before or after it."""
    for args in (("show", "t-one", "--json"), ("search", "task", "--json")):
        code, out, _ = _cli(bundle, *args)
        json.loads(out)                       # raises if anything shares the stream
        assert out.endswith("\n") and not out.endswith("\n\n"), \
            f"{args}: exactly one trailing newline, got {out[-3:]!r}"
        human = _cli(bundle, *args[:-1])[1]
        assert human not in out, f"{args}: the human render is riding along with the payload"


def test_empty_result_is_not_a_refusal(bundle):
    """E2 — zero hits is a SUCCESS with an empty list; only a malformed ask is a refusal."""
    code, out, _ = _cli(bundle, "search", "zzz-nothing-matches-this", "--json")
    body = json.loads(out)
    assert code == 0 and body["ok"] is True, f"a zero-hit search refused: {body['note']!r}"
    assert body["results"] == []


def test_absent_fields_are_omitted_not_nulled(bundle):
    """A9, E3, E4 — an unauthored slot has no key, non-ASCII survives, edges is [] not absent."""
    lone, _ = add.show_payload(bundle, "p-lone")
    assert lone["results"][0]["match"] == "node"
    fields = lone["results"][0]["fields"]
    assert "status" not in fields, f"an absent `status:` was emitted as a value: {fields!r}"
    assert lone["edges"] == [], "an isolated node must carry an empty edges list (E4)"
    text = add.as_json(add.show_payload(bundle, "t-one")[0])
    assert "café" in text, "non-ASCII was escaped away — ensure_ascii must be False"


def test_the_schema_is_pinned_in_format(bundle):
    """M6, M7, A5, A6 — FORMAT.md names every key emitted, and no engine version rides along."""
    fmt = (REPO / "FORMAT.md").read_text(encoding="utf-8")
    for key in sorted(KEYS):
        assert f"`{key}`" in fmt, f"FORMAT.md does not pin the envelope key `{key}`"
    body, _ = add.show_payload(bundle, "t-one")
    # The ENVELOPE, not the node content it carries: a node's own `generated: {by: add/3.4.0}`
    # is data being copied faithfully, and M7 is about what the schema itself adds.
    envelope = {k: v for k, v in body.items() if k not in ("results", "edges")}
    assert add.ENGINE not in json.dumps(envelope), \
        f"the engine version {add.ENGINE} is in the envelope — a release would move the bytes (M7)"
    assert add.ENGINE in json.dumps(body["results"]), \
        "the floor failed: the fixture node carries no version, so the check above proves nothing"
    assert body["schema"] in fmt, f"FORMAT.md does not name the schema id {body['schema']!r}"
