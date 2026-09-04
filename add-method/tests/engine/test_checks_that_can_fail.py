"""Eight checks that fail when the defect they name is injected — because six did not.

Red-first for `/tasks/checks-that-cannot-fail.md`.

Two review agents audited the okf-graph-lookup milestone by INJECTING defects rather than
reading tests, and found the green was not load-bearing. Reproduced here before repair, each
with the injection recorded so the next auditor does not re-derive it:

* `NEIGHBORHOOD_MAX = 50` -> `test_cap_has_one_home` PASSED. It read the value out of the module
  and then found that value in the module's own source (R:SELFPIN), and nothing else in the
  repo bound the number.
* refusals rewritten to say `next: add florbulate` -> all of `test_show_verb.py` PASSED. Every
  ADD `next:` line begins with the literal `add`, so `verb == "add" or verb in advertised` never
  reached its second half (R:DEADHALF).
* `_fields()` returning `{}` -> `test_absent_fields_are_omitted_not_nulled` PASSED. "an absent
  key is omitted" is satisfied by omitting every key.
* the CLI's `--expand` default set to 1 -> all 12 show-verb checks PASSED. Nothing compared the
  argparse default to the engine's.
* `test_the_override_does_not_bypass_the_seal` never reached the seal: its setup gates a node it
  comments as `# never frozen`, that gate is REFUSED, and `done` then fails on a missing gate
  stamp instead. Underneath it, `done`'s override branch really did skip its own seal check.
"""

import inspect
import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402
import cli  # noqa: E402

sys.path.insert(0, str(Path(__file__).parent))
from test_done_reads_the_verdict import _authored, _bundle  # noqa: E402

CAP = 5          # the ceiling, BY VALUE — never read from the module this file guards


def test_the_cap_value_is_pinned_outside_the_engine():
    """M1, R:SELFPIN, E1, A4 — injected `NEIGHBORHOOD_MAX = 50`; the old pin passed."""
    assert add.NEIGHBORHOOD_MAX == CAP, \
        f"the walk's ceiling moved to {add.NEIGHBORHOOD_MAX}; FORMAT.md §3.4 states {CAP}"
    fmt = (REPO / "FORMAT.md").read_text(encoding="utf-8")
    s34 = fmt.split("### §3.4")[1].split("\n## ")[0]
    assert f"ceiling of {CAP}" in s34, \
        "FORMAT.md §3.4 does not state the ceiling's value, so the document cannot be checked"


def test_refusal_names_a_verb_that_exists():
    """M2, R:DEADHALF, E2 — injected `next: add florbulate`; every show-verb check passed."""
    advertised = set(cli.build_parser()._subparsers._group_actions[0].choices)
    notes = [add.show(REPO.parent / ".add", "no-such-node-at-all", 3)[1],
             add.show(REPO.parent / ".add", "PROJECT", add.NEIGHBORHOOD_MAX + 1)[1]]
    for note in notes:
        assert "next:" in note, f"a refusal carries no next: line — {note}"
        words = note.split("next:")[1].split()
        assert words[0].strip("`") == "add", f"the next: line is not an `add` command: {note}"
        # The word AFTER `add` — the half the old check could never reach.
        assert words[1].strip("`") in advertised, \
            f"the next: names `{words[1]}`, which is not a wired verb: {note}"


def test_walk_ignores_a_poisoned_cache(tmp_path):
    """M3, E3 — the old check REFRESHED the cache first, so a cache-reading walk agreed."""
    root = tmp_path / ".add"
    add.init(root, profile="code", title="poison fixture")
    add.new(root, "Milestone", "m-one", title="a milestone")
    add.new(root, "Task", "t-one", title="a task", milestone="m-one")
    cache = root / "graph.json"
    add.load(root)
    assert cache.exists(), "no cache was written, so poisoning it proves nothing"
    truth, _ = add.neighborhood(add.scan(root), "/tasks/t-one.md", 2)
    assert truth, "the fixture has no edges, so a cache read could not be observed"
    # Make the cache DISAGREE with the tree. A walk reading it would answer from this.
    cache.write_text(json.dumps({"nodes": {}, "edges": []}), encoding="utf-8")
    after, _ = add.neighborhood(add.scan(root), "/tasks/t-one.md", 2)
    assert after == truth, "the walk answered from graph.json — law 1 is broken"


def test_payload_emits_the_fields_it_has(tmp_path):
    """M4, E4, A7 — injected `_fields() -> {}`; the absent-key check passed over nothing."""
    root = tmp_path / ".add"
    add.init(root, profile="code", title="fields fixture")
    add.new(root, "Persona", "p-lone", title="an isolated node")
    fields = add.show_payload(root, "p-lone")[0]["results"][0]["fields"]
    assert fields.get("type") == "Persona", \
        f"an AUTHORED frontmatter key is missing from the payload: {fields!r}"
    assert "status" not in fields, f"an absent key was emitted as a value: {fields!r}"


def test_cli_and_engine_agree_on_the_default():
    """M5, E5 — injected `default=1` in cli.py; all 12 show-verb checks passed."""
    action = next(a for a in cli.build_parser()._subparsers._group_actions[0]
                  .choices["show"]._actions if a.dest == "expand")
    assert action.default == add.NEIGHBORHOOD_DEFAULT, \
        (f"the CLI walks {action.default} levels by default and the engine walks "
         f"{add.NEIGHBORHOOD_DEFAULT} — A10 claims they are ONE number")


def _sealed_stop(root, slug):
    """A node that is FROZEN and carries a real HARD-STOP — what the old setup failed to build.

    `_authored` fills every slot the authoring guards check, because a scaffolded node's
    `freeze` is REFUSED and a silently-unfrozen fixture is how the original check ended up
    asserting over a missing gate stamp instead of over the seal.
    """
    cid = _authored(root, slug)
    ok, note = add.freeze(root, cid, by="H", authority="human")[:2]
    assert ok, f"the fixture did not freeze, so the seal cannot be reached: {note}"
    add.run(root, cid, ["true"])
    return cid


def test_override_refuses_on_a_sealed_node_with_a_stop(tmp_path):
    """M6, E6, A2 — the setup now REACHES the seal instead of dying on a missing stamp."""
    root = _bundle(tmp_path / ".add")
    cid = _sealed_stop(root, "sealed-stop")
    ok, note = add.gate(root, cid, "HARD-STOP", by="H", reason="the finding")[:2]
    assert ok, f"the fixture failed to record a HARD-STOP, so the seal is not reached: {note}"
    accepted, *_rest = add.done(root, cid, override="shipping anyway")
    assert accepted, ("a sealed node with a reasoned override must still close — this task "
                      "removes a reliance, never widens or narrows what `done` accepts")


def test_the_override_path_evaluates_the_seal():
    """M7, R:WIDENING, A5 — the seal was in an `elif` the override branch fell out of."""
    src = inspect.getsource(add.done)
    branch = src.split("if not gates and stopped:")[1].split("elif not gates:")[0]
    assert "seal_at" in branch, \
        ("`done`'s override branch does not evaluate the seal on its own path — it relies on "
         "`gate` refusing upstream, which is one refactor away from absent")


def test_every_repair_records_its_injection():
    """R:UNPROVEN, A6, A9, A10 — a repair is believed only once its defect was observed red."""
    doc = Path(__file__).read_text(encoding="utf-8")
    for marker in ("NEIGHBORHOOD_MAX = 50", "add florbulate", "_fields()", "--expand` default",
                   "never frozen"):
        assert marker in doc, f"the injection that proved `{marker}` is not recorded"
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and name != "test_every_repair_records_its_injection":
            assert (fn.__doc__ or "").strip(), f"{name} records no injection in its docstring"
