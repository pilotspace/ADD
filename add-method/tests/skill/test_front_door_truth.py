"""Both READMEs must state only what the engine can be read to confirm.

`all-domain-evidence` found one defect five times inside the skill: nothing checked shipped prose
against engine reality. This is the same defect at the loudest surface ADD has — the two files npm,
PyPI and the repo landing page render to anyone who has not adopted yet.

Every expectation here is DERIVED at test time: bundle files by running a real `init`, verbs by
introspecting the CLI's registered subparsers, profiles by reading `add.PROFILES`. A pinned literal
would go stale exactly the way the prose it replaces did — silently, and only visible to whoever
went looking. `test_expectations_are_derived_not_pinned` proves the derivation by feeding the
extractors a fabricated engine.
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[3]
PACKAGE = REPO / "add-method"
ROOT_README = REPO / "README.md"
PKG_README = PACKAGE / "README.md"
CLI = PACKAGE / "tooling" / "cli.py"
sys.path.insert(0, str(PACKAGE / "tooling"))

import add  # noqa: E402 — the engine is the authority on profiles

READMES = (ROOT_README, PKG_README)

# `.add/<name>` as a reader would meet it: in inline code, in prose, or inside image alt text.
BUNDLE_REF = re.compile(r"\.add/([A-Za-z0-9_.-]+)")
# "31-verb kernel" and "21 verbs" are the two shapes actually shipped; both are claims about the CLI.
VERB_CLAIM = re.compile(r"(\d+)[- ]verbs?\b")
PROFILE_CLAIM = re.compile(r"--profile\s+(?:<([^>]+)>|`?([a-z]+)`?)")

# A1: the rule binds the two READMEs only — what a reader is shown before adopting.
# A2: naming `state.json` while explaining the 2.x break is honest and stays allowed; the marker is
# the word "2.x" on the same line, because `upgrade` genuinely has to say what it detects.
LEGACY_EXEMPT = re.compile(r"2\.x", re.I)


def _readme(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _label(path: Path) -> str:
    """Both files are named `README.md`, so a bare name makes a failure unactionable."""
    return str(path.relative_to(REPO))


def fresh_bundle_entries(cli: Path) -> set:
    """Top-level names the engine creates in `.add/`. Raises if it creates nothing.

    The probe drives a bundle that has been USED — `init`, then a first task — not one that has
    only been initialised. `tasks/` is created lazily on the first `new`, so an init-only baseline
    cannot distinguish a lazily-created directory from a dead one, and would force the docs to
    describe a bundle no working project ever has. It still refuses `state.json` and `PLAN.md`,
    which no sequence of verbs produces.

    R:VACUOUS — a failed `init` would yield an empty set, and every M1 assertion would then pass by
    comparing against nothing.
    """
    with tempfile.TemporaryDirectory() as tmp:
        out = subprocess.run([sys.executable, str(cli), "init", "Probe"],
                             capture_output=True, text=True, cwd=tmp)
        subprocess.run([sys.executable, str(cli), "new", "Task", "probe-task", "--title", "probe"],
                       capture_output=True, text=True, cwd=tmp)
        bundle = Path(tmp) / ".add"
        entries = {p.name for p in bundle.iterdir()} if bundle.is_dir() else set()
        if not entries:
            raise AssertionError(
                f"`init` created no bundle to compare against, so nothing could be checked:\n"
                f"{out.stdout}{out.stderr}")
        return entries


def cli_verbs(cli: Path) -> set:
    """Every verb the CLI registers, read from its own parser rather than from a list here."""
    src = cli.read_text(encoding="utf-8")
    found = set()
    for m in re.finditer(r"add_parser\(\s*[\"']([a-z][a-z-]*)[\"']", src):
        found.add(m.group(1))
    if not found:
        raise AssertionError("extracted no verbs from the CLI — the registration shape changed; "
                             "fix the extractor, do not relax the check")
    return found


def _claimed_counts(text: str) -> set:
    return {int(m.group(1)) for m in VERB_CLAIM.finditer(text)}


def _claimed_profiles(text: str) -> set:
    named = set()
    for m in PROFILE_CLAIM.finditer(text):
        if m.group(2):
            named.add(m.group(2))
        else:
            named |= {p.strip(" `") for p in m.group(1).split("|")}
    return named


def test_readmes_name_no_absent_bundle_file():
    """M1 — `.add/state.json` is the 2.x marker; `add.py` says 3.0 has no state file."""
    real = fresh_bundle_entries(CLI)
    ghosts = []
    for path in READMES:
        for line in _readme(path).splitlines():
            if LEGACY_EXEMPT.search(line):
                continue        # A2 — explaining what `upgrade` detects is an honest mention
            for name in BUNDLE_REF.findall(line):
                if name not in real:
                    ghosts.append(f"{_label(path)}: .add/{name}")
    assert not ghosts, (f"READMEs cite bundle files a fresh `init` never creates: {sorted(set(ghosts))} "
                        f"— it creates {sorted(real)}")


def test_readme_verb_counts_match_the_cli():
    """M2 — three claims, two numbers, and the CLI ships a third."""
    shipped = len(cli_verbs(CLI))
    wrong = {f"{_label(p)}: {n}" for p in READMES
             for n in _claimed_counts(_readme(p)) if n != shipped}
    assert not wrong, f"verb counts that contradict the CLI's {shipped}: {sorted(wrong)}"


def test_readmes_do_not_contradict_each_other():
    """M2, the second half — the package README states 31 in its highlights and 21 on its own
    install page. Whatever the right number is, a reader must not be able to catch the two files
    disagreeing; A4 keeps silence compliant, so an empty set passes."""
    stated = set().union(*(_claimed_counts(_readme(p)) for p in READMES))
    assert len(stated) <= 1, f"the READMEs state different verb counts: {sorted(stated)}"


def test_readmes_name_every_shipped_profile():
    """M3 — both directions against the engine, the rule the evidence ladder now holds to."""
    shipped, named = set(add.PROFILES), set().union(*(_claimed_profiles(_readme(p)) for p in READMES))
    assert not (named - shipped), \
        f"READMEs name profiles the engine does not ship: {sorted(named - shipped)}"
    assert not (shipped - named), (
        f"the engine ships profiles no README names: {sorted(shipped - named)} — a reader choosing "
        f"how to start cannot pick an option nobody told them exists")


def test_expectations_are_derived_not_pinned(tmp_path):
    """M4 + R:PINNED — fabricate an engine and require the fabrication to come back."""
    fake_cli = tmp_path / "cli.py"
    fake_cli.write_text('sub.add_parser("totally-made-up-verb", help="x")\n', encoding="utf-8")
    assert "totally-made-up-verb" in cli_verbs(fake_cli), \
        "the verb extractor is pinning literals — it will rot the way the prose did"
    assert _claimed_profiles("run `add init --profile invented` first") == {"invented"}, \
        "the profile extractor is pinning literals"


def test_extractors_fail_loud_on_empty(tmp_path):
    """R:VACUOUS — nothing extracted must raise, never read as agreement."""
    empty = tmp_path / "cli.py"
    empty.write_text("def main():\n    return 0\n", encoding="utf-8")
    with pytest.raises(AssertionError, match="extracted no verbs"):
        cli_verbs(empty)
    missing = tmp_path / "not-a-cli.py"
    missing.write_text("print('no init here')\n", encoding="utf-8")
    with pytest.raises(AssertionError, match="created no bundle"):
        fresh_bundle_entries(missing)


def test_shown_commands_actually_answer():
    """M5 — a command a README hands a reader must respond when they run it.

    The root README shows `add.py status` three times. `add.py` is the engine MODULE: run as a
    script it exits 0 and prints nothing at all, so a reader following the front door concludes
    their install is broken. The package README already says this ("a library, not a command") on
    its own install table — so the two files contradict each other about how to drive the engine.

    The premise is PROVEN here, not assumed: each shown invocation is executed inside a real
    bundle, and silence is the failure. That way the rule tracks the engine — the day `add.py`
    grows a `__main__`, this check stops objecting on its own.
    """
    shown = set()
    for path in READMES:
        for m in re.finditer(r"`([a-z_]+\.py)\s+([a-z][a-z-]*)[^`]*`", _readme(path)):
            if m.group(2) in cli_verbs(CLI):
                shown.add((_label(path), m.group(1), m.group(2)))
    assert shown, "no engine invocation found in either README — the extractor has drifted"

    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([sys.executable, str(CLI), "init", "Probe"],
                       capture_output=True, text=True, cwd=tmp)
        mute = []
        for label, script, verb in sorted(shown):
            engine = PACKAGE / "tooling" / script
            if not engine.is_file():
                mute.append(f"{label}: `{script} {verb}` — no such file ships")
                continue
            out = subprocess.run([sys.executable, str(engine), verb],
                                 capture_output=True, text=True, cwd=tmp)
            if not (out.stdout + out.stderr).strip():
                mute.append(f"{label}: `{script} {verb}` — exits {out.returncode}, prints nothing")
    assert not mute, (f"READMEs instruct readers to run commands that answer nothing: {mute} — "
                      f"a reader who follows them concludes the install is broken")


def test_shown_installer_flags_are_accepted():
    """M5, the installer half — a flag the installer ignores is worse than one it rejects.

    The first pass of this task shipped `npx @pilotspace/add init --profile doc` into the root
    README. The installer takes no `--profile` at all: its own "profile" is AGENT detection
    (Claude Code · Cursor · Codex), so it answers `warn: ignoring unknown flag --profile` and then
    reads `doc` as the TARGET DIRECTORY — installing into `./doc` if that happens to exist. The
    installer's own source says this is why `--stage` had to be rejected explicitly rather than
    left to the unknown-flag warning.

    `test_shown_commands_actually_answer` did not catch it because it only executes
    `<engine>.py <verb>` forms. This closes the class: each installer-form command is handed to
    the installer's OWN parser, and its own diagnostic is the verdict. Safe because it runs in a
    temp cwd against a target directory that does not exist, so the parse happens and nothing is
    written.
    """
    installer = PACKAGE / "bin" / "cli.js"
    if not installer.is_file():
        raise AssertionError(f"no installer at {installer} — the extractor has drifted")

    # Only fenced command lines, and only up to a trailing `# comment` — prose that merely mentions
    # the package name is not an instruction, and `init      # Node / npm` is one argument, not four.
    shown = []
    for path in READMES:
        for line in _readme(path).splitlines():
            m = re.match(r"^\s*(?:npx @pilotspace/add\S*|pilotspace-add)\s+(.+)$", line)
            if not m:
                continue
            argv = m.group(1).split("#")[0].split()
            if argv and argv[0].isalpha():          # a verb, not a sentence continuing the prose
                shown.append((_label(path), argv))
    assert shown, "no installer invocation found in either README — the extractor has drifted"

    with tempfile.TemporaryDirectory() as tmp:
        absent = str(Path(tmp) / "no-such-target")
        bad = []
        for label, argv in shown:
            out = subprocess.run(["node", str(installer), *argv, absent],
                                 capture_output=True, text=True, cwd=tmp)
            said = out.stdout + out.stderr
            for line in said.splitlines():
                if "ignoring unknown flag" in line or "was retired" in line:
                    bad.append(f"{label}: `{' '.join(argv)}` — {line.strip()}")
    assert not bad, (f"READMEs show installer flags the installer does not accept: {bad} — an "
                     f"ignored flag leaves its VALUE on the positional list, where it is read as "
                     f"the target directory")


def test_alt_text_does_not_restate_stale_image_claims():
    """E1 + R:IMAGEWASH — three PNGs render the false claims into the artwork.

    `add-install.png` draws `.add/state.json`; the two lifecycle diagrams draw `PLAN.md` as the
    per-feature file and the retired `§0…§7` numbering. No text edit reaches a rasterised word, so
    the honest move is to stop the ALT TEXT from repeating the claim and to carry the image itself
    as a reported residual. Alt text that still asserts it would make the repair look complete.
    """
    offenders = []
    for path in READMES:
        for line in _readme(path).splitlines():
            if not line.lstrip().startswith("!["):
                continue
            alt = line[line.index("![") + 2: line.index("](")] if "](" in line else line
            if re.search(r"state\.json", alt) or re.search(r"\bPLAN\.md\b", alt):
                offenders.append(f"{_label(path)}: {alt[:70]}…")
    assert not offenders, (f"image alt text still asserts what the engine contradicts: {offenders} "
                           f"— the artwork cannot be edited here, so the alt text must not repeat it")
