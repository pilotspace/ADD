"""A claim on the front door is backed by the shipped artifact, or it is not made.

Every case below was executed against the 3.3.0 tree. They share one shape — prose that
described a capability the engine does not have, in the places a reader meets first:

* "gaming a test to get green is structurally impossible" (README's own See-it-yourself demo).
  The freeze seal digests RULES · CHECKS · `gives:` — the NAMES. It never digests the test
  FILES those names point at. Running the demo the table invites (reopen, gut both frozen
  tests to bare `pass`, re-run, gate) records `gate PASS ... freshness: fresh`. SKILL.md and
  GETTING-STARTED both say so plainly; only the front door claimed otherwise.
* A "Network: one optional advisory update check ... disable with ADD_NO_UPDATE_CHECK=1" in the
  section a security reviewer reads. There is no network code in the shipped surface at all,
  and nothing reads that variable. The true statement — zero network — is strictly stronger.
* `--stage mvp`, the Install section's only flag example, which the installer explicitly rejects.
* `cli.py deltas` sold as "the per-lane scoreboard: what got gated, passed, healed". It prints
  `[LENS] spec: text`. GEPA, per-lane, scoreboard and fast lane appear nowhere in the engine.
* `add upgrade` — a real verb that archives a 2.x bundle and writes MIGRATION.md — named in no
  README, while the engine's own 2.x refusal says `next: add init`, which writes a 3.0 bundle
  INTO the live 2.x directory and leaves a permanent doctor error.
* `SOUL.md`, a 2.x file 3.x never creates, still the routing target for tone rules.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO.parent
sys.path.insert(0, str(REPO / "tooling"))
import add  # noqa: E402
import cli as cli_mod  # noqa: E402

READMES = [ROOT / "README.md", REPO / "README.md"]
SKILL = REPO / "skill" / "add"
GETTING_STARTED = REPO / "GETTING-STARTED.md"
VERBS = set(cli_mod.build_parser()._subparsers._group_actions[0].choices)

NET = re.compile(r"require\(['\"](https?|net|dns|tls)['\"]\)|^\s*import (urllib|socket|http|requests)"
                 r"|\bfetch\(|https?\.(get|request)\(", re.M)
SHIPPED_CODE = [REPO / "bin" / "cli.js", REPO / "src" / "add_method" / "_installer.py",
                REPO / "src" / "add_method" / "_cli.py",
                REPO / "tooling" / "add.py", REPO / "tooling" / "cli.py"]


def _text(p):
    return p.read_text(encoding="utf-8") if p.is_file() else ""


# ------------------------------------------------- M1 · the trust claim

def test_no_front_door_claims_test_tampering_is_structurally_prevented():
    """covers: M1, R:OVERCLAIM — the seal covers the contract TEXT, never the test BODIES."""
    bad = []
    for doc in READMES:
        for line in _text(doc).splitlines():
            if re.search(r"gaming a test.*(impossible|tampering)", line, re.I):
                bad.append(f"{doc}: {line.strip()[:140]}")
    assert not bad, (
        "the front door promises what SKILL.md:123 and GETTING-STARTED:374 disclaim — a check "
        "that asserts nothing still binds and still passes:\n  " + "\n  ".join(bad))


def test_the_skill_still_states_the_honest_limit():
    """covers: M1, A1 — the counter-guard: do not fix the claim by deleting the disclosure."""
    honest = _text(SKILL / "SKILL.md") + _text(GETTING_STARTED)
    assert re.search(r"asserts nothing|cannot judge|only prove you ran", honest, re.I), (
        "the honest limit on what a seal can prove is no longer stated anywhere")


# ------------------------------------------------- M2 · the network disclosure

def test_the_network_disclosure_matches_the_shipped_code():
    """covers: M2, R:FALSEBOUNDARY — a security reviewer reads this paragraph before approving."""
    reaches = [p.name for p in SHIPPED_CODE if p.is_file() and NET.search(_text(p))]
    # A NEGATED mention ("no update check", "Network: none") is the honest disclosure this
    # guard wants, not the claim it hunts. Match only lines that assert a call happens.
    claims = [f"{d}:{i}" for d in READMES
              for i, line in enumerate(_text(d).splitlines(), 1)
              if re.search(r"HTTPS GET|npm registry|advisory update check", line, re.I)
              and not re.search(r"\bno\b|\bnone\b|never", line, re.I)]
    assert not reaches, (
        "shipped code now makes a network call — the disclosure must be re-read, and this "
        f"check must not go silent about it: {reaches}")
    if not reaches:
        assert not claims, (
            f"no shipped file makes a network call, yet the boundary section claims one: {claims}")


def test_no_doc_names_an_env_var_nothing_reads():
    """covers: M2, E1 — a reviewer who sets it in CI believes they closed an egress."""
    src = "".join(_text(p) for p in SHIPPED_CODE)
    named = set()
    for doc in READMES + [GETTING_STARTED, SKILL / "SKILL.md"]:
        named |= set(re.findall(r"\b(ADD_[A-Z0-9_]+)\b", _text(doc)))
    dead = sorted(v for v in named if v not in src)
    assert not dead, f"documented environment variables nothing reads: {dead}"


# ------------------------------------------------- M3 · every documented flag runs

def test_every_installer_flag_shown_in_a_readme_is_accepted():
    """covers: M3, R:DEADFLAG — the first flag a new user copies must not fail their install."""
    js = _text(REPO / "bin" / "cli.js")
    bad, retired, seen = [], [], 0
    for doc in READMES:
        for flag in set(re.findall(r"(?<![\w-])(--[a-z][a-z0-9-]+)", _text(doc))):
            seen += 1
            if flag in ("--junitxml", "--by", "--reason", "--all", "--check", "--sync",
                        "--persona", "--evidence", "--depth", "--sensitivity", "--scope",
                        "--to", "--answer", "--timeout", "--cwd", "--section", "--off",
                        "--milestone", "--status", "--title", "--kind", "--authority",
                        "--phase", "--root", "--help", "--nested", "--no-skill",
                        "--profile"):   # an `add init` flag, guarded by test_profile_refusal
                continue                      # engine verbs / covered by their own guards
            if re.search(rf'"{re.escape(flag)}"|{re.escape(flag)}\b', js):
                # PRESENT in cli.js — but present-and-rejected is the worse case, so ask which.
                if re.search(rf'{re.escape(flag)}\b[^\n]*retired', js):
                    retired.append(f"{doc.name}: {flag}")
                continue
            bad.append(f"{doc.name}: {flag}")

    # `retired` used to be filtered OUT of `bad` — flags absent from cli.js — while requiring the
    # flag to be IN cli.js. Mutually exclusive, so it was `[]` for every possible input, and the
    # real `bad` list was computed and then discarded. Both halves now assert, on disjoint sets.
    assert not retired, f"a README teaches a flag the installer explicitly rejects: {retired}"
    assert not bad, (
        "a README teaches an installer flag `bin/cli.js` does not accept — the first flag a new "
        f"user copies must not fail their install: {bad}")
    assert seen >= 4, f"only {seen} README flag(s) were examined — the check is not running"


def test_the_stage_flag_is_gone_from_every_readme():
    """covers: M3 — `--stage` was retired in 3.0 and the installer errors on it."""
    bad = [d.name for d in READMES if "--stage" in _text(d)]
    assert not bad, f"`--stage` was retired in 3.0 and still appears in: {bad}"


# ------------------------------------------------- M4 · deltas is described as it behaves

def test_deltas_is_not_sold_as_a_scoreboard():
    """covers: M4, R:PHANTOMFEATURE — vocabulary the shipped artifact does not carry."""
    engine = _text(REPO / "tooling" / "add.py")
    absent = [w for w in ("GEPA", "per-lane", "scoreboard", "fast lane")
              if w.lower() not in engine.lower()]
    bad = [f"{d.name}: {w}" for d in READMES + [GETTING_STARTED]
           for w in absent if w.lower() in _text(d).lower()]
    assert not bad, (
        "these words name nothing in the engine — `deltas` prints `[LENS] spec: text`:\n  "
        + "\n  ".join(bad))


# ------------------------------------------------- M5 · the migration path

def test_the_upgrade_verb_is_documented():
    """covers: M5, E2 — a real verb built for exactly this, named in no README."""
    assert "upgrade" in VERBS
    documented = any("add upgrade" in _text(d) for d in READMES + [GETTING_STARTED,
                                                                   SKILL / "SKILL.md"])
    assert documented, "`add upgrade` archives a 2.x bundle and is named in no shipped doc"


def test_the_2x_refusal_names_upgrade_not_init():
    """covers: M5 — following `next: add init` writes a 3.0 bundle INTO the live 2.x dir."""
    engine = _text(REPO / "tooling" / "add.py")
    m = re.search(r"this is an ADD 2\.x bundle.*?next: add (\w+)", engine, re.S)
    assert m, "the 2.x refusal was not found — this guard is stale"
    assert m.group(1) == "upgrade", (
        f"the 2.x refusal still points at `add {m.group(1)}`, which corrupts the bundle")


# ------------------------------------------------- M6 · no doc routes to a file 3.x never writes

def test_no_shipped_doc_routes_to_soul_md():
    """covers: M6, R:PHANTOMFILE — a 2.x file no template, verb or `put()` produces."""
    bad = [str(p.relative_to(REPO)) for p in SKILL.rglob("*.md") if "SOUL.md" in _text(p)]
    assert not bad, f"these route the author to SOUL.md, which 3.x never creates: {bad}"


# ------------------------------------------------- M7 · the storefront

def test_the_marketplace_entry_describes_the_shipped_method():
    """covers: M7 — the only text a user sees before deciding to install."""
    mk = ROOT / ".claude-plugin" / "marketplace.json"
    if not mk.is_file():
        mk = REPO / ".claude-plugin" / "marketplace.json"
    blob = json.dumps(json.loads(_text(mk))) if mk.is_file() else ""
    assert blob, (
        "marketplace.json is missing or unparseable — the storefront copy is unchecked, "
        "which is how it sold retired 2.x phases for two minor versions")
    if not blob:
        return
    retired = [w for w in ("Specify", "Scenarios", "Observe") if w in blob]
    assert not retired, f"the storefront sells retired 2.x phases: {retired}"
    assert "book into your project" not in blob and "AIDD book into" not in blob, \
        "the storefront claims the book materializes into the project; it never installs"
