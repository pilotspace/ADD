"""Red suite for `orientation-sees-carried-work` — the instrument, before any refusal.

75 lessons stood open in this repo's own bundle while `status`, `todo` and `doctor` between
them reported none of them, and `.add/PROJECT.md` read `state: initialised` for a month
because `upgrade` carried only `title:` forward. Nothing here refuses anything: the whole
task is three listings and one seeded key, so the rest of the milestone can be measured
instead of trusted.

One test per Must / Reject of tasks/orientation-sees-carried-work, plus its filled edges and
its probed assumptions — the gate binds every one of them (M31).
"""

import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))

import add  # noqa: E402


def _spec(root, lens):
    return Path(root) / "specs" / f"{lens}.md"


@pytest.fixture
def bundle(tmp_path):
    add.init(tmp_path, "code", "Orient")
    return tmp_path


# ------------------------------------------------------------------ S1 · the counter


def test_learn_and_fold_maintain_the_counter(bundle):
    """covers: M7, A7, A3, E3 — one write, and only `open` is counted."""
    add.learn(bundle, "method", "first lesson about gates", evidence="/tasks/a.md")
    raw = _spec(bundle, "method").read_text()
    assert "open_deltas: 1" in raw, "learn did not raise the counter in the same write"

    add.learn(bundle, "method", "second lesson about gates", evidence="/tasks/b.md")
    assert "open_deltas: 2" in _spec(bundle, "method").read_text()

    # E3: one fold matching BOTH lessons decrements by the number actually retagged.
    ok, note = add.fold(bundle, "method", "lesson about gates")
    assert ok, note
    assert "folded 2 delta(s)" in note
    assert "open_deltas: 0" in _spec(bundle, "method").read_text(), \
        "fold decremented by one, not by the number it retagged"

    # A3: a folded delta is resolved and must not be counted again.
    add.learn(bundle, "method", "a third, still open", evidence="/tasks/c.md")
    assert "open_deltas: 1" in _spec(bundle, "method").read_text()


# ------------------------------------------------------------------ S2 · the status header


def test_status_counts_open_deltas(bundle):
    """covers: M1 — the total spans every Spec, and the project goal is named."""
    add.learn(bundle, "method", "one", evidence="/tasks/a.md")
    add.learn(bundle, "quality", "two", evidence="/tasks/b.md")
    add.learn(bundle, "quality", "three", evidence="/tasks/c.md")
    root = Path(bundle)
    project = root / "PROJECT.md"
    project.write_text(project.read_text().replace(
        "goal: <one sentence — what is true when this ships>", "goal: ship the drain"))

    out = add.status(bundle)
    assert "3 open deltas" in out, f"status did not name the total:\n{out}"
    assert "ship the drain" in out, f"status did not name the project goal:\n{out}"


def test_status_unknown_counter_is_not_zero(bundle):
    """covers: M2, R:UNKNOWNCLEAN, A10 — absent and unparsable both read UNKNOWN."""
    # ABSENT: strip the seeded key the way every bundle written before it exists.
    add.learn(bundle, "method", "one", evidence="/tasks/a.md")
    legacy = _spec(bundle, "system")
    legacy.write_text("\n".join(l for l in legacy.read_text().splitlines()
                                if not l.startswith("open_deltas:")) + "\n")
    out = add.status(bundle)
    assert "?" in out and "0 open deltas" not in out and "1 open delta" not in out, \
        f"an unmigrated Spec read as clean, or was silently dropped from the total:\n{out}"

    # UNPARSABLE: present, and not a number.
    spec = _spec(bundle, "quality")
    spec.write_text(spec.read_text().replace("delta_seq:", "open_deltas: many\ndelta_seq:", 1))
    out = add.status(bundle)
    assert "?" in out, f"an unparsable counter read as a number:\n{out}"


def test_status_clause_names_its_verb(bundle):
    """covers: A16, A13 — a number with no next verb is not orientation."""
    add.learn(bundle, "method", "one", evidence="/tasks/a.md")
    out = add.status(bundle)
    assert "add deltas" in out, f"the count named no verb:\n{out}"
    assert len(out.splitlines()) <= 22, f"the clause cost a new line:\n{out}"


def test_status_stays_t0(bundle, monkeypatch):
    """covers: R:T2SCAN — the count must not be bought with a body read."""
    add.learn(bundle, "method", "one", evidence="/tasks/a.md")
    real, leaks = add.read, []

    def spy(path, tier="T0"):
        if tier != "T0":
            leaks.append((str(path), tier))
        return real(path, tier)

    monkeypatch.setattr(add, "read", spy)
    out = add.status(bundle)
    # Withhold the subject and this guard proves nothing: assert the clause is actually
    # PRESENT before asserting how it was bought, or a status that counts nothing passes.
    assert "1 open delta" in out, f"no count was produced, so no tier was tested:\n{out}"
    assert leaks == [], f"status read past T0 to count deltas: {leaks}"


# ------------------------------------------------------------------ S3 · the two findings


def _codes(root):
    return [f["code"] for f in add.doctor(root)]


def test_doctor_warns_unauthored_root(bundle):
    """covers: M3, R:GREENROOT, A17 — a scaffold root is never a clean bundle."""
    findings = [f for f in add.doctor(bundle) if f["code"] == "unauthored_root"]
    assert findings, "a freshly initialised bundle reported no finding against its own root"
    assert all(f["severity"] == "warn" for f in findings)
    project = [f for f in findings if "PROJECT.md" in (f["node"] or "")]
    assert project, "no finding named PROJECT.md"
    assert "goal" in project[0]["detail"], \
        f"the finding named the file, not the slot: {project[0]['detail']}"
    assert len([f for f in findings if "specs/" in (f["node"] or "")]) == 5, \
        "the five scaffold Specs were not each named"


def test_doctor_root_finding_reads_the_card_too(bundle):
    """covers: E4, A4 — an authored frontmatter goal does not clear a scaffold CARD."""
    root = Path(bundle)
    project = root / "PROJECT.md"
    project.write_text(project.read_text().replace(
        "goal: <one sentence — what is true when this ships>", "goal: ship the drain"))
    findings = [f for f in add.doctor(bundle)
                if f["code"] == "unauthored_root" and "PROJECT.md" in (f["node"] or "")]
    assert findings, "the CARD goal was still scaffold and nothing said so"
    assert "ship the drain" in add.status(bundle), \
        "status read the CARD goal, not the frontmatter goal"


def test_doctor_reports_and_syncs_delta_drift(bundle):
    """covers: M4, E2 — drift is reported, and `--sync` repairs every Spec at once."""
    assert "delta_count_drift" not in _codes(bundle), \
        "a bundle with no deltas and no key reported drift"      # E1
    add.learn(bundle, "method", "one", evidence="/tasks/a.md")
    spec = _spec(bundle, "method")
    spec.write_text(spec.read_text().replace("open_deltas: 1", "open_deltas: 7"))
    drift = [f for f in add.doctor(bundle) if f["code"] == "delta_count_drift"]
    assert drift and drift[0]["severity"] == "info", "a lying counter was not reported"

    changed, note = add.doctor_sync(bundle)
    assert changed, note
    assert "open_deltas: 1" in spec.read_text(), "sync did not rewrite the counter"
    assert "delta_count_drift" not in _codes(bundle)


# ------------------------------------------------------------------ S4 · the authored root


def test_init_writes_invariants_and_doctor_reads_it(bundle):
    """covers: M5, R:DEADKEY, A2 — the key CLAUDE.md binds to exists, and has a reader."""
    raw = (Path(bundle) / "PROJECT.md").read_text()
    assert "invariants: []" in raw, "init wrote no invariants: key"
    src = (REPO / "tooling" / "add.py").read_text()
    doctor_src = src[src.index("def doctor("):src.index("def doctor_sync(")]
    assert "invariants" in doctor_src, \
        "invariants: is written by init and read by nothing (R:DEADKEY)"


def test_upgrade_carries_the_goal(tmp_path):
    """covers: M6, R:CLOBBERGOAL, A6, E5 — a year-old goal survives the clean break."""
    def legacy(goal_line):
        root = tmp_path / f"p{abs(hash(goal_line))}" / ".add"
        (root / "tooling" / "add_engine").mkdir(parents=True)
        (root / "tooling" / "add_engine" / "__init__.py").write_text("# 2.x\n")
        (root / "state.json").write_text('{"schema": 3}\n')
        (root / "PROJECT.md").write_text(f"# PROJECT: Ledger\n\ntitle: Ledger\n{goal_line}\n")
        return root.parent

    carried = legacy("goal: ship a lean, trustworthy method")
    add.upgrade(carried, by="human:tindang")
    assert "goal: ship a lean, trustworthy method" in (carried / ".add" / "PROJECT.md").read_text(), \
        "upgrade replaced an authored goal with a placeholder (R:CLOBBERGOAL)"

    bare = legacy("stage: mvp")                                   # E5
    _report, note = add.upgrade(bare, by="human:tindang")
    fresh = (bare / ".add" / "PROJECT.md").read_text()
    assert "goal: <one sentence" in fresh, f"upgrade invented a goal: {note}"


# ------------------------------------------------------------------ the shape of the change


def test_no_new_verb(bundle):
    """covers: A5, A9, A15 — flags, rungs and listings only; and Persona stays untouched."""
    cli_src = (REPO / "tooling" / "cli.py").read_text()
    for absent in ('add_parser("drain"', 'add_parser("bind"', 'add_parser("invariants"'):
        assert absent not in cli_src, f"a new verb was added: {absent}"
    add.new(bundle, "Persona", "a-lens", title="A lens")
    roots = [f for f in add.doctor(bundle) if f["code"] == "unauthored_root"]
    # Assert the producer CAN emit this code before filtering on it, or the exclusion below
    # is a filter over an empty list and passes on an engine that does nothing.
    assert any("specs/" in (f["node"] or "") for f in roots), \
        "unauthored_root is emitted for no Spec, so the Persona exclusion tests nothing"
    assert not [f for f in roots if "personas/" in (f["node"] or "")], \
        "unauthored_root reached a Persona, which has no RULES to author"
