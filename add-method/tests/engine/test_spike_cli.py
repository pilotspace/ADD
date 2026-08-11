"""Red suite for the spike dispatch — PROPOSAL v6 §3, D-18.

The throwaway `add/scripts/spike_cli.py` wires the eight drive-critical verbs to the engine so
the M4 cost census (`v8`) and the unwrapped drive (`v0'`) can run WITHOUT the 200-line `e11`
CLI. It is deleted on NARROW/STOP and replaced by `e11` on PASS.

These tests assert the DISPATCH contract — argv in, the right engine function called, the right
exit code out — not the engine internals, which `tests/engine/*` already cover. The dispatch's
one job is to be a faithful, thin wire: success is exit 0, an engine refusal is a non-zero exit,
and `--root` targets the named bundle.
"""

import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SCRIPTS = REPO / "tooling"
sys.path.insert(0, str(SCRIPTS))

import add  # noqa: E402
import spike_cli  # noqa: E402  (the module under test — absent until it is written)

VALIDATOR = REPO / "scripts" / "validate_bundle.py"


def validate(root):
    r = subprocess.run([sys.executable, str(VALIDATOR), str(root)], capture_output=True, text=True)
    return r.returncode, r.stdout


# ------------------------------------------------------------ dispatch guards


def test_no_args_is_usage_error():
    """An empty invocation must not touch the bundle; it reports usage and exits 2."""
    assert spike_cli.main([]) == 2


def test_unknown_verb_is_usage_error():
    assert spike_cli.main(["frobnicate"]) == 2


# ---------------------------------------------------------- init + status (orient)


def test_init_creates_a_conforming_bundle(tmp_path):
    """The whole point: a bundle the dispatch creates satisfies M0's oracle, unedited."""
    root = tmp_path / ".add"
    assert spike_cli.main(["init", "--root", str(root), "Spike"]) == 0
    code, out = validate(root)
    assert code == 0 and "CONFORMS" in out, out


def test_status_orients_after_init(tmp_path, capsys):
    root = tmp_path / ".add"
    spike_cli.main(["init", "--root", str(root), "Spike"])
    capsys.readouterr()
    assert spike_cli.main(["status", "--root", str(root)]) == 0
    assert "next:" in capsys.readouterr().out.lower()


# ------------------------------------------------------- new + freeze + brief


def test_new_then_freeze_wire_through(tmp_path, draft):
    root = tmp_path / ".add"
    spike_cli.main(["init", "--root", str(root), "Spike"])
    assert spike_cli.main(["new", "Task", "widget", "--depth", "standard", "--root", str(root)]) == 0
    assert (root / "tasks" / "widget.md").is_file()
    draft(root, "/tasks/widget.md")   # freeze refuses a scaffold — draft it first
    # freeze resolves the bare slug to its cid and stamps it
    assert spike_cli.main(["freeze", "widget", "--by", "test", "--root", str(root)]) == 0


def test_new_collision_returns_nonzero(tmp_path):
    """A colliding slug is an engine refusal; the dispatch must surface it as exit 1."""
    root = tmp_path / ".add"
    spike_cli.main(["init", "--root", str(root), "Spike"])
    spike_cli.main(["new", "Task", "widget", "--root", str(root)])
    assert spike_cli.main(["new", "Task", "widget", "--root", str(root)]) == 1


def test_brief_emits_the_xml_pack(tmp_path, capsys):
    root = tmp_path / ".add"
    spike_cli.main(["init", "--root", str(root), "Spike"])
    spike_cli.main(["new", "Task", "widget", "--root", str(root)])
    capsys.readouterr()
    assert spike_cli.main(["brief", "widget", "--root", str(root)]) == 0
    assert "<task" in capsys.readouterr().out


# ----------------------------------------------------------- run records evidence


def test_run_records_a_receipt(tmp_path, capsys):
    root = tmp_path / ".add"
    spike_cli.main(["init", "--root", str(root), "Spike"])
    spike_cli.main(["new", "Task", "widget", "--depth", "standard", "--root", str(root)])
    capsys.readouterr()
    rc = spike_cli.main(["run", "widget", "--root", str(root),
                         "--", sys.executable, "-c", "print('ok')"])
    assert rc == 0
    assert "receipt" in capsys.readouterr().out.lower()
    assert (root / "tasks" / "widget.d" / "runs").is_dir()


# ------------------------------------------------- gate refusal wires the error code


def test_gate_without_receipt_refuses_nonzero(tmp_path):
    """A gate with no fresh receipt is the notary's refusal; the dispatch returns 1, not 0."""
    root = tmp_path / ".add"
    spike_cli.main(["init", "--root", str(root), "Spike"])
    spike_cli.main(["new", "Task", "widget", "--depth", "standard", "--root", str(root)])
    assert spike_cli.main(["gate", "widget", "PASS", "--by", "test", "--root", str(root)]) == 1


# ------------------------------------------------------ --root and the entry point


def test_root_flag_targets_the_named_dir(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    spike_cli.main(["init", "--root", str(a), "A"])
    assert (a / "PROJECT.md").is_file()
    assert not b.exists()


def test_subprocess_entrypoint_runs(tmp_path):
    """`python spike_cli.py status` — the real __main__ path an agent invokes."""
    root = tmp_path / ".add"
    spike_cli.main(["init", "--root", str(root), "Spike"])
    r = subprocess.run([sys.executable, str(SCRIPTS / "spike_cli.py"), "status", "--root", str(root)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert "next:" in r.stdout.lower()
