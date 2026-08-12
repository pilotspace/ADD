"""The skill surface: valid frontmatter, within budget, and every command it names is real.

The last test is the load-bearing one — it makes the "dispatch gap" seam impossible to ship
silently. If SKILL.md tells an agent to run `add <verb>` and no dispatch verb exists, this fails.
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SKILL = REPO / "skill" / "add"
sys.path.insert(0, str(REPO / "tooling"))

import argparse  # noqa: E402
import cli  # noqa: E402  — the real ABF-1 CLI; the skill must stay honest to its verb set


def _cli_verbs():
    sub = [a for a in cli.build_parser()._actions if isinstance(a, argparse._SubParsersAction)][0]
    return set(sub.choices)


def _frontmatter(text: str) -> str:
    m = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    return m.group(1) if m else ""


def test_router_frontmatter_is_valid():
    fm = _frontmatter((SKILL / "SKILL.md").read_text(encoding="utf-8"))
    assert re.search(r"^name:\s*add\s*$", fm, re.M), "name: add missing"
    assert "description:" in fm, "description missing"
    assert re.search(r"^user-invocable:\s*true\s*$", fm, re.M), "user-invocable: true missing (needed for /add)"


def test_router_within_line_budget():
    n = len((SKILL / "SKILL.md").read_text(encoding="utf-8").splitlines())
    assert n <= 176, f"SKILL.md is {n} lines (budget 176 — the only always-loaded cost; re-pinned from 150 at 3.1.0, human call)"


def test_no_single_ref_over_split_threshold():
    for path in SKILL.rglob("*.md"):
        if path.name == "SKILL.md":
            continue
        n = len(path.read_text(encoding="utf-8").splitlines())
        assert n <= 350, f"{path.relative_to(SKILL)} is {n} lines — split it (T3 rule)"


def _own_docs():
    """The `add` skill's own docs. `persona-author/` is a NESTED sub-skill with its own SKILL.md and
    its own budget — it is loaded on its own terms, not as part of this router's disclosure cost, so
    it is not counted here (the add-skill-2 tree this came from has no nested sub-skill at all)."""
    return [p for p in SKILL.rglob("*.md") if "persona-author" not in p.relative_to(SKILL).parts]


def test_total_surface_within_budget():
    total = sum(len(p.read_text(encoding="utf-8").splitlines()) for p in _own_docs())
    assert total <= 1500, f"skill surface is {total} lines (budget 1500; 2.5 was 2031)"


def test_every_wired_verb_is_documented():
    """The other direction of the anti-seam: a verb the engine ships that no doc names.

    The phantom direction (a doc naming a verb the CLI lacks) was already guarded. The orphan
    direction was not, so a shipped verb could be invisible to the only thing an agent reads —
    which is how `advise` (the sequential remedy R:NOCOVERAGE's refusal asks for), `doctor`,
    `locate` and `todo` came to be documented nowhere.
    """
    documented = set()
    for path in _own_docs():
        text = path.read_text(encoding="utf-8")
        documented |= {m.group(1) for m in re.finditer(r"`?add\s+([a-z][a-z-]{1,22})\b", text)}
    orphans = _cli_verbs() - documented
    assert not orphans, f"engine ships verbs no skill doc names: {sorted(orphans)}"


def test_router_commands_are_real_dispatch_verbs():
    """Every `add <verb>` in SKILL.md's bash cookbook maps to a real spike_cli verb."""
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    blocks = re.findall(r"```bash\n(.*?)```", text, re.DOTALL)
    assert blocks, "SKILL.md has no ```bash cookbook block"
    verbs = {m.group(1) for b in blocks for line in b.splitlines()
             if (m := re.match(r"add\s+([a-z-]+)", line.strip()))}
    assert verbs, "no `add <verb>` command lines found in the cookbook"
    unknown = verbs - _cli_verbs()
    assert not unknown, f"SKILL.md names commands with no dispatch verb: {sorted(unknown)}"
