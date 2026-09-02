"""The refusals ADD's docs promise and the engine did not make.

Every test here was RED against 3.2.0 and corresponds to a defect confirmed by execution during
the 2026-08-28 adversarial review (four lenses: method integrity, trust boundary, adoption cost,
engine architecture). The unifying defect they found: every guard fired on the PRESENCE of a
malformed thing and never on the ABSENCE of a required one, so the way past each refusal was to
delete rather than to forge.
"""
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402


def _bundle(tmp_path):
    add.init(tmp_path, "code", "T")
    return tmp_path


def _authored(tmp_path, slug, **fields):
    """A node the placeholder guard accepts — so these tests probe the SEAL, not authoring."""
    cid, _ = add.new(tmp_path, "Task", slug, title=slug, **fields)
    p = tmp_path / cid.lstrip("/")
    t = p.read_text(encoding="utf-8")
    t = t.replace("- S1 <the surface this publishes — an endpoint, function, or section>",
                  "- S1 the lister")
    t = t.replace("goal: <one line>", "goal: the fixture states its one line.")
    t = re.sub(r"## RULES\n<must>\n.*?\n</must>",
               "## RULES\n<must>\n- M1 the lister returns only the caller's rows\n</must>", t, flags=re.S)
    t = re.sub(r"<reject>\n.*?\n</reject>",
               '<reject>\n- R:LEAK another tenant\'s row is returned -> "LEAK"\n</reject>', t, flags=re.S)
    t = re.sub(r"## ASSUMPTIONS\n.*?\nevery `gives:`", "## ASSUMPTIONS\n" + "".join(
        f"- A{i} [{d}] covers: S1 · the request does not say; taking the plain reading -> minor\n"
        for i, d in enumerate(("who", "which", "when", "absent", "order", "experience"), 1)
    ) + "every `gives:`", t, flags=re.S)
    t = re.sub(r"## CHECKS\n.*?\nred-first",
               "## CHECKS\n- test_only_own_rows · covers: M1, R:LEAK · proves isolation\nred-first",
               t, flags=re.S)
    p.write_text(t, encoding="utf-8")
    return cid


def _junit(path, name="t::test_only_own_rows"):
    cls, _, case = name.partition("::")
    path.write_text('<testsuites><testsuite name="p" tests="1" failures="0" errors="0">'
                    f'<testcase classname="{cls}" name="{case}" time="0.01"/>'
                    '</testsuite></testsuites>', encoding="utf-8")


# --- 1. the ONE approval is not optional -------------------------------------------------
def test_gate_refuses_pass_without_a_freeze_seal(tmp_path):
    """The whole post-freeze apparatus was guarded on `if sealed` with no else, so skipping the
    approval switched off drift detection and R:UNBRIEFED instead of refusing."""
    root = _bundle(tmp_path)
    cid = _authored(root, "nofreeze")
    _junit(tmp_path / "j.xml")
    add.run(root, cid, ["/usr/bin/true"], junit=str(tmp_path / "j.xml"))
    ok, msg = add.gate(root, cid, "PASS", by="Tin")
    assert not ok, "gate: recorded a PASS on a node that was never frozen — the ONE approval is optional"
    assert "freeze" in msg.lower(), f"gate: the refusal does not name the missing freeze — {msg!r}"
    assert (root / cid.lstrip("/")).read_text(encoding="utf-8").count("status: done") == 0, \
        "gate: the node closed despite the refusal"


def test_gate_refuses_without_a_seal_at_quick_depth_too(tmp_path):
    """Quick is ceremony-tuned, not approval-exempt — the lane under time pressure is exactly
    the one that must not be able to skip the human."""
    root = _bundle(tmp_path)
    cid = _authored(root, "quicknofreeze", depth="quick")
    _junit(tmp_path / "j.xml")
    add.run(root, cid, ["/usr/bin/true"], junit=str(tmp_path / "j.xml"))
    ok, msg = add.gate(root, cid, "PASS", by="Tin")
    assert not ok, "gate: --depth quick still closes without a freeze stamp"


# --- 2. the receipt must stand for the run that produced it -------------------------------
def test_junit_not_written_during_the_run_downgrades_to_command_exit(tmp_path):
    """`kind: test-ids` was earned by a file's existence: /usr/bin/true plus a hand-typed XML
    naming tests that do not exist produced the strongest evidence rung."""
    root = _bundle(tmp_path)
    cid = _authored(root, "stale")
    stale = tmp_path / "old.xml"
    _junit(stale)
    time.sleep(0.01)
    add.run(root, cid, ["/usr/bin/true"], junit=str(stale))
    body = (root / f"tasks/stale.d/runs/1.md").read_text(encoding="utf-8")
    assert "kind: command-exit" in body, \
        "run: a report not written during the run still claimed `kind: test-ids`"
    assert re.search(r"note:.*(stale|not written|predates)", body, re.I), \
        f"run: the receipt does not SAY why it was downgraded — {body}"


def test_junit_written_by_the_command_still_earns_test_ids(tmp_path):
    """The honest path must keep working, or the fix is a regression."""
    root = _bundle(tmp_path)
    cid = _authored(root, "fresh")
    out = tmp_path / "fresh.xml"
    add.run(root, cid, [sys.executable, "-c",
                        f"open({str(out)!r},'w').write('<testsuites><testsuite name=\"p\" tests=\"1\" "
                        f"failures=\"0\" errors=\"0\"><testcase classname=\"t\" "
                        f"name=\"test_only_own_rows\"/></testsuite></testsuites>')"],
            junit=str(out))
    body = (root / f"tasks/fresh.d/runs/1.md").read_text(encoding="utf-8")
    assert "kind: test-ids" in body, f"run: a report written BY the command was not trusted — {body}"


# --- 3. the security floor, both directions ------------------------------------------------
def test_sensitive_paths_match_through_a_directory_scope(tmp_path):
    """Widening scope LOWERED authority: `src/` did not match `src/auth/*`, so the honest broad
    declaration that CONTAINS the sensitive file escaped the floor."""
    graph = {"/index.md": {"fm": {"sensitive_paths": ["src/auth/*"]}},
             "/tasks/broad.md": {"fm": {"scope": ["src/"]}},
             "/tasks/exact.md": {"fm": {"scope": ["src/auth/keys.py"]}}}
    assert add.authority_for(graph, "/tasks/exact.md") == "human", "the exact scope lost its floor"
    assert add.authority_for(graph, "/tasks/broad.md") == "human", \
        "a scope CONTAINING a sensitive path does not raise the floor — widening scope lowers authority"


def test_gate_refuses_when_an_undeclared_sensitive_path_changed(tmp_path):
    """Nothing compared the declared scope to what actually changed, so omitting the path from
    `scope:` defeated the one floor that does not rest on self-declared sensitivity."""
    repo = tmp_path
    root = tmp_path / ".add"          # the engine reads the diff of the bundle's PARENT
    root.mkdir()
    add.init(root, "code", "T")
    (repo / "src").mkdir(exist_ok=True)
    (repo / "src/auth.py").write_text("def login(): return check()\n", encoding="utf-8")
    (repo / "src/ui.py").write_text("def render(): pass\n", encoding="utf-8")
    for cmd in (["init", "-q"], ["add", "-A"],
                ["-c", "user.email=a@b", "-c", "user.name=a", "commit", "-qm", "base"]):
        subprocess.run(["git", *cmd], cwd=repo, check=True, capture_output=True)
    idx = root / "index.md"
    idx.write_text(idx.read_text(encoding="utf-8")
                   .replace("sensitive_paths: []", 'sensitive_paths: ["src/auth.py"]'), encoding="utf-8")
    cid = _authored(root, "sneaky", scope="src/ui.py")
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "-c", "user.email=a@b", "-c", "user.name=a",
                    "commit", "-qm", "bundle"], cwd=repo, check=True, capture_output=True)
    (repo / "src/auth.py").write_text("def login(): return True  # backdoor\n", encoding="utf-8")
    _junit(tmp_path / "j.xml")
    add.freeze(root, cid, "Tin")
    add.brief_stamp(root, cid)
    add.run(root, cid, ["/usr/bin/true"], junit=str(tmp_path / "j.xml"))
    ok, msg = add.gate(root, cid, "PASS", by="Tin")
    assert not ok, "gate: a build that changed an undeclared SENSITIVE path still recorded PASS"
    assert "auth.py" in msg, f"gate: the refusal does not name the undeclared sensitive file — {msg!r}"


# --- 4. the ledger, and the crashes ---------------------------------------------------------
def test_gate_reason_cannot_swallow_the_next_stamp(tmp_path):
    """An unbalanced brace in --reason made the parser consume the FOLLOWING stamp: two records
    written, one read back. `replan` already sanitises its note; `gate` did not."""
    root = _bundle(tmp_path)
    cid = _authored(root, "brace", scope="src/x.py")
    _junit(tmp_path / "j.xml")
    add.freeze(root, cid, "Tin")
    add.brief_stamp(root, cid)
    add.run(root, cid, ["/usr/bin/true"], junit=str(tmp_path / "j.xml"))
    add.gate(root, cid, "HARD-STOP", by="Tin", reason="the { id } lookup leaks")
    add.gate(root, cid, "HARD-STOP", by="Tin", reason="a second, later finding")
    stamps = [s for s in (add.read(root / cid.lstrip("/"), "T2")["fm"].get("verified") or [])
              if isinstance(s, dict) and s.get("act") == "gate"]
    assert len(stamps) == 2, \
        f"gate: a brace in --reason deleted a stamp from the append-only ledger (read {len(stamps)} of 2)"


def test_receipt_numbering_never_overwrites(tmp_path):
    """Receipt names came from a COUNT, so deleting one made the next run overwrite an existing
    receipt — a red run could be turned green by arithmetic, with no forgery."""
    root = _bundle(tmp_path)
    cid = _authored(root, "count", scope="src/x.py")
    for _ in range(3):
        add.run(root, cid, ["/usr/bin/true"])
    runs = root / "tasks/count.d/runs"
    (runs / "2.md").unlink()
    add.run(root, cid, ["/usr/bin/true"])
    names = sorted(p.name for p in runs.glob("*.md"))
    assert "4.md" in names, f"run: numbering reused a taken name instead of max+1 — {names}"
    assert names.count("3.md") == 1 and "1.md" in names, f"run: an existing receipt was overwritten — {names}"


def test_milestone_done_survives_a_malformed_stamp(tmp_path):
    """The credit loop was the only stamp iteration in add.py with no isinstance guard, so one
    bad entry crashed the verb whose job is to report the bundle's state."""
    root = _bundle(tmp_path)
    mcid, _ = add.new(root, "Milestone", "ms", title="M")
    p = root / mcid.lstrip("/")
    t = p.read_text(encoding="utf-8")
    t = re.sub(r"(?m)^why: .*$", "why: because", t)
    t = re.sub(r"## EXIT\n(?:- \[[ x]\].*\n)*", "## EXIT\n- [x] done\n", t)
    t = t.replace("verified: []", 'verified:\n  - a bare string, not a mapping')
    p.write_text(t, encoding="utf-8")
    ok, msg = add.milestone_done(root, mcid)          # must not raise
    assert isinstance(msg, str), "milestone_done: crashed on a malformed stamp instead of reporting"


# --- 5. `add check` must agree with the gate it feeds ----------------------------------------
def test_check_and_milestone_done_agree_on_exit_boxes(tmp_path):
    """One shared BOX pattern was not enough: the SECTION BOUNDARY differed, so `check` could tick
    a criterion the goal-gate would never count."""
    body = ("## CARD\ngoal: g\n\n## EXIT\n- [x] first\n\n## SCOPE\nin: x\n\n"
            "## EXIT\n- [ ] second, uncounted\n\n## CLOSE\n")
    tallied = add._box_lines(add._section_of(body, "EXIT"))
    listed = add._box_lines(body, "EXIT")
    assert len(tallied) == len(listed), (
        f"check/milestone_done disagree: the gate tallies {len(tallied)} box(es), "
        f"`check --section EXIT` enumerates {len(listed)}")


def test_check_refuses_to_tick_a_template_placeholder(tmp_path):
    """The goal-gate closed on `- [x] <criterion>   (← <task>)` — unauthored text, credited to a
    named human. The engine owns a placeholder detector and never pointed it here."""
    root = _bundle(tmp_path)
    mcid, _ = add.new(root, "Milestone", "ms", title="M")
    ok, msg = add.check(root, mcid, [1], by="Tin")
    assert not ok, "check: ticked a template placeholder, releasing the goal-gate on unauthored text"
    assert re.search(r"placeholder|template", msg, re.I), \
        f"check: the refusal does not say why the box was rejected — {msg!r}"


def test_check_stamp_records_how_it_was_invoked(tmp_path):
    """`--by` is free text, so `loop.md`'s promise — 'a box the AI ticked never reads as a human's'
    — was false. The name stays free; what it was typed AT is now recorded beside it."""
    root = _bundle(tmp_path)
    mcid, _ = add.new(root, "Milestone", "ms", title="M")
    p = root / mcid.lstrip("/")
    t = re.sub(r"## EXIT\n(?:- \[[ x]\].*\n)*", "## EXIT\n- [ ] a real criterion\n",
               p.read_text(encoding="utf-8"))
    p.write_text(re.sub(r"(?m)^why: .*$", "why: because", t), encoding="utf-8")
    add.check(root, mcid, [1], by="Tin Dang")                     # library call: unattended
    stamp = [s for s in add.read(p, "T2")["fm"]["verified"] if s.get("act") == "check"][0]
    assert stamp.get("via") == "process", \
        f"check: an unattended tick does not record its caller context — {stamp}"
    ok, msg = add.milestone_done(root, mcid)
    assert ok, f"milestone_done refused a fully checked milestone — {msg}"
    assert "Tin Dang" in msg and re.search(r"unattended|via process|not at a terminal", msg, re.I), \
        f"milestone_done: an unattended tick reads exactly like a human's — {msg!r}"


# --- the edges the new refusals must NOT break ------------------------------------------------
def test_a_pre_seal_freeze_without_a_digest_still_gates(tmp_path):
    """covers: E1 — the tolerance is for a missing DIGEST, not a missing STAMP.

    Bundles frozen by a pre-3.0 engine carry a freeze stamp with no `direction:` field. Refusing
    those would retroactively strand every task frozen before the seal shipped (R:RETROBREAK), so
    the new refusal must read the STAMP and leave the digest tolerance exactly where it was.
    """
    root = _bundle(tmp_path)
    cid = _authored(root, "legacy")
    add.freeze(root, cid, "Tin")
    add.brief_stamp(root, cid)
    p = root / cid.lstrip("/")
    p.write_text("\n".join(l.split(", direction:")[0] + " }" if ", direction:" in l else l
                           for l in p.read_text(encoding="utf-8").splitlines()), encoding="utf-8")
    out = tmp_path / "e1.xml"
    add.run(root, cid, [sys.executable, "-c",
                        f"open({str(out)!r},'w').write('<testsuites><testsuite><testcase "
                        f"classname=\"t\" name=\"test_only_own_rows\"/></testsuite></testsuites>')"],
            junit=str(out))
    ok, msg = add.gate(root, cid, "PASS", by="Tin")
    assert ok, f"gate: a pre-seal freeze was refused — the digest tolerance was lost ({msg})"


def test_a_bundle_outside_a_git_tree_still_gates(tmp_path):
    """covers: E2 — `_changed_paths` returns `[]` where git cannot answer, so the scope-vs-diff
    refusal can only ever ADD a refusal where git is present, never invent one where it is not."""
    root = _bundle(tmp_path)
    assert add._changed_paths(tmp_path) == [], "a non-repo tree reported changes"
    cid = _authored(root, "nogit")                     # no `scope:` — freshness is n/a
    add.freeze(root, cid, "Tin")
    add.brief_stamp(root, cid)
    out = tmp_path / "e2.xml"
    add.run(root, cid, [sys.executable, "-c",
                        f"open({str(out)!r},'w').write('<testsuites><testsuite><testcase "
                        f"classname=\"t\" name=\"test_only_own_rows\"/></testsuite></testsuites>')"],
            junit=str(out))
    ok, msg = add.gate(root, cid, "PASS", by="Tin")
    assert ok, f"gate: a bundle outside a git working tree was refused — {msg}"


def test_a_single_entry_scope_is_not_iterated_per_character(tmp_path):
    """covers: E3 — `scope: src/ui.py` parses as a STRING, and every reader iterated it, so the
    freshness set became one entry per character and `/` resolved to the filesystem root."""
    assert add._scope_list({"scope": "src/ui.py"}) == ["src/ui.py"], \
        "a single-entry scope iterated per character — the freshness set names nothing real"
    assert add._scope_list({"scope": ["a", "b"]}) == ["a", "b"], "a list scope was not preserved"
    assert add._scope_list({}) == [] and add._scope_list(None) == [], "an absent scope is not empty"
