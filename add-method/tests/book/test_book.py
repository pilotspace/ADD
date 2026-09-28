"""The book teaches ADD 4.0 — one skill, files, git and the project's own test command.

The 3.x book taught an engine: `add freeze`, `add gate`, refusal codes, a vendored `cli.py`. 4.0
removed all of it. A page that still tells the reader to run one of those verbs points at nothing,
so these checks hold the book to what the skill actually does: every nav entry is a real page and
every page is reachable, every internal link lands, no page instructs a retired verb or names a
removed engine file (the one migration page excepted — naming them is its job), and the reference
chapters agree with `skill/add/references/format.md`.
"""
import re
import sys
from pathlib import Path

PKG = Path(__file__).resolve().parents[2]            # add-method/
sys.path.insert(0, str(PKG / "scripts"))
import book_lint  # noqa: E402

DOCS = PKG / "docs"
FORMAT = PKG / "skill" / "add" / "references" / "format.md"


def _read(rel: str) -> str:
    return (DOCS / rel).read_text(encoding="utf-8")


# --- structure -------------------------------------------------------------------------------

def test_every_nav_page_exists():
    nav = book_lint.nav_pages()
    assert len(nav) >= 20, f"the nav reader found only {len(nav)} pages — it is misreading mkdocs.yml"
    missing = [p for p in nav if not (DOCS / p).is_file()]
    assert not missing, f"mkdocs nav names pages that do not exist: {missing}"


def test_every_docs_page_is_in_the_nav():
    orphans = sorted(set(book_lint.pages()) - set(book_lint.nav_pages()))
    assert not orphans, f"pages under docs/ that no reader can reach from the nav: {orphans}"


def test_the_nav_lists_each_page_once():
    nav = book_lint.nav_pages()
    dupes = sorted({p for p in nav if nav.count(p) > 1})
    assert not dupes, f"pages listed twice in the nav: {dupes}"


def test_internal_links_resolve():
    bad = book_lint.unresolved_links()
    assert not bad, f"relative links that land on no file inside docs/: {bad}"


def test_the_migration_page_is_in_the_book():
    assert book_lint.MIGRATION_PAGE in book_lint.nav_pages(), \
        "the 'what changed in 4.0' page is the one place the retired surface is named — keep it"


# --- vocabulary: nothing sends the reader to the removed engine -------------------------------

def test_no_page_instructs_a_retired_verb():
    hits = {rel: h for rel in book_lint.pages() if rel != book_lint.MIGRATION_PAGE
            if (h := book_lint.retired_verb_hits(_read(rel)))}
    assert not hits, f"pages that tell the reader to run a retired 3.x verb: {hits}"


def test_no_page_names_the_removed_engine():
    hits = {rel: h for rel in book_lint.pages() if rel != book_lint.MIGRATION_PAGE
            if (h := book_lint.engine_name_hits(_read(rel)))}
    assert not hits, f"pages that name removed engine files or roster agents: {hits}"


def test_the_verb_detector_catches_commands_and_ignores_english():
    """A detector that cannot fail is not a gate — plant each shape and check the verdict."""
    planted = ("you add a test, then add the rule to the spec\n"        # English — ignored
               "run `add freeze my-task` now\n"                          # code span — caught
               "npx @pilotspace/add init\n"                              # installer — ignored
               "`/add status` resumes the session\n"                     # skill call — ignored
               "`git add .add/tasks/x.md`\n"                             # git — ignored
               "```bash\nadd gate x PASS\npilotspace-add update\n```\n")  # block — gate caught
    assert book_lint.retired_verb_hits(planted) == [(2, "freeze"), (7, "gate")]


def test_the_engine_detector_catches_each_name():
    for name in book_lint.ENGINE_NAMES:
        assert book_lint.engine_name_hits(f"see {name} for details") == [(1, name)]
    assert book_lint.engine_name_hits("the skill, files, git and your test command") == []


def test_the_link_reader_skips_urls_and_anchors():
    text = "[a](./02-the-flow.md#top) [b](https://x.org/y.md) [c](#local) ![d](./img.png)"
    assert book_lint.internal_links(text) == ["./02-the-flow.md", "./img.png"]


# --- the reference chapters agree with the skill ----------------------------------------------

def _task_sections(text: str) -> list[str]:
    block = text.split("## Task", 1)[1].split("## Milestone", 1)[0]
    return re.findall(r"(?m)^## ([A-Z]+)$", block)


def test_the_bundle_chapter_names_every_task_section_the_skill_defines():
    sections = _task_sections(FORMAT.read_text(encoding="utf-8"))
    assert {"CARD", "RULES", "ASSUMPTIONS", "PLAN", "CHECKS", "EVIDENCE"} <= set(sections), \
        f"format.md's Task shape changed — re-read it before trusting this check: {sections}"
    chapter = _read("12-bundle-format.md")
    missing = [s for s in sections if f"## {s}" not in chapter]
    assert not missing, f"12-bundle-format.md omits task sections format.md defines: {missing}"


def test_the_worked_example_walks_the_whole_4_0_loop():
    text = _read("appendix-d-worked-example.md")
    for marker in ("freeze(", "verify(", "## EVIDENCE", "git diff", "verdict: PASS",
                   "## ASSUMPTIONS", "status: build", "status: done"):
        assert marker in text, f"the worked example never shows `{marker}`"
    assert text.index("freeze(") < text.index("verify("), "the example verifies before it seals"


def test_the_loop_chapters_state_the_seal_and_the_three_verdicts():
    direction, verify = _read("03-direction.md"), _read("05-verify.md")
    assert "freeze(" in direction and "git diff" in verify, "the git seal is not taught"
    for verdict in ("PASS", "RISK-ACCEPTED", "HARD-STOP"):
        assert verdict in verify, f"05-verify.md never names the {verdict} verdict"
