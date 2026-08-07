#!/usr/bin/env python3
"""book_renumber — one-shot: apply the frozen target-TOC manifest to the book (structure only).

Idempotent-ish and content-preserving: it MOVES and RELINKS, it never rewrites prose. It reads every
old chapter, computes the new set (1:1 renames + the 03-merge + the 10-split + two stubs), regenerates
each file's H1 and nav line from the manifest, repoints inline ./NN links, writes the new files, and
removes the collapsed orphans — for BOTH docs/ (canonical) and the repo-root mirror. Then it patches
the repo-root mkdocs.yml nav and README.md ./NN links.

Run from add-method/:  python3 scripts/book_renumber.py
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import book_lint as BL  # noqa: E402

ADD_METHOD = HERE.parent
REPO_ROOT = ADD_METHOD.parent
DOCS = ADD_METHOD / "docs"

# every old source filename (the ones that carry content into the new set)
MERGE_INTO_03 = ["03-step-1-specify.md", "05-step-3-plan.md", "06-step-4-tests.md"]
SPLIT_SOURCE = "10-setup-and-stages.md"
SPLIT_MARKER = "## Parallel streams"     # old-10 body splits here: before → new 07, from here → new 08
# 1:1 renames (old → new) that are a straight move of one file's body
ONE_TO_ONE = {
    "00-introduction.md": "00-introduction.md",
    "01-principles.md": "01-principles.md",
    "02-the-flow.md": "02-the-flow.md",
    "07-step-5-build.md": "04-build.md",
    "08-step-6-verify.md": "05-verify.md",
    "09-the-loop.md": "06-the-loop.md",
    "11-governance.md": "09-governance.md",
    "12-roles.md": "10-personas.md",
    "13-adoption.md": "11-adoption.md",
    "14-foundation.md": "14-foundation.md",
    "15-foundations-and-lineage.md": "15-foundations-and-lineage.md",
    "16-releasing.md": "16-releasing.md",
    "17-components.md": "17-components.md",
    "18-personas.md": "18-personas.md",
}
ALL_OLD = set(MERGE_INTO_03) | {SPLIT_SOURCE} | set(ONE_TO_ONE)

TITLES = {num: title for num, _, title in BL.target_chapters()}
FILE_BY_NUM = {num: fn for num, fn, _ in BL.target_chapters()}
NUM_BY_FILE = {fn: num for num, fn, _ in BL.target_chapters()}
ORDER = [fn for _, fn, _ in BL.target_chapters()]


def _nav_label(num: str) -> str:
    """A resolving nav label from the manifest title: '03 · Direction — …' → '03 Direction — …'."""
    return TITLES[num].replace(" · ", " ")


def _nav_line(num: str) -> str:
    i = ORDER.index(FILE_BY_NUM[num])
    parts = []
    if i > 0:
        pn = NUM_BY_FILE[ORDER[i - 1]]
        parts.append(f"[← {_nav_label(pn)}](./{ORDER[i - 1]})")
    parts.append("[Contents](./README.md)")
    if i < len(ORDER) - 1:
        nn = NUM_BY_FILE[ORDER[i + 1]]
        parts.append(f"Next: [{_nav_label(nn)} →](./{ORDER[i + 1]})")
    return " · ".join(parts)


def _body_after_header(text: str) -> str:
    """Drop the leading '# H1', the nav line, and the first '---' hrule — return the body below it."""
    lines = text.splitlines()
    for idx, ln in enumerate(lines):
        if ln.strip() == "---" and idx <= 8:      # the hrule under the nav, near the top
            return "\n".join(lines[idx + 1:]).lstrip("\n")
    # no hrule found — fall back to dropping just the H1 line
    return "\n".join(lines[1:]).lstrip("\n")


def _repoint_links(body: str) -> str:
    """Rewrite every ](./OLD.md…) to its new filename. Old 05/06/03 → 03-direction; old 10 → 07."""
    def sub(m):
        old, anchor = m.group(1), m.group(2) or ""
        new = BL.RENAME.get(old, old)
        return f"](./{new}{anchor})"
    return re.sub(r"\]\(\.\/([0-9A-Za-z][0-9A-Za-z._-]*\.md)(#[^)]*)?\)", sub, body)


def _compose(num: str, body: str) -> str:
    """A finished chapter file: new H1 + regenerated nav + hrule + repointed body."""
    return f"# {TITLES[num]}\n\n{_nav_line(num)}\n\n---\n\n{_repoint_links(body).rstrip()}\n"


def _build_new_set(src_dir: Path) -> dict:
    """Return {new_filename: new_text} for one book copy (docs/ or repo root)."""
    read = lambda fn: (src_dir / fn).read_text(encoding="utf-8")
    out = {}

    # 1:1 renames — straight body moves
    for old, new in ONE_TO_ONE.items():
        num = NUM_BY_FILE[new]
        out[new] = _compose(num, _body_after_header(read(old)))

    # merge old 03+05+06 → new 03-direction.md
    merged = "\n\n---\n\n".join(_body_after_header(read(fn)) for fn in MERGE_INTO_03)
    out["03-direction.md"] = _compose("03", merged)

    # split old 10 → new 07 (setup+stages) + new 08 (parallel work)
    ten_body = _body_after_header(read(SPLIT_SOURCE))
    if SPLIT_MARKER in ten_body:
        before, after = ten_body.split(SPLIT_MARKER, 1)
        after = SPLIT_MARKER + after
    else:                                          # marker absent → all to 07, empty 08 note
        before, after = ten_body, "_(parallel-streams content not found in source — see book-part3.)_"
    out["07-setup-and-lanes.md"] = _compose("07", before)
    out["08-parallel-work.md"] = _compose("08", after)

    # two new reference-chapter stubs
    for fn in BL.NEW_STUBS:
        num = NUM_BY_FILE[fn]
        out[fn] = _compose(num, f"> **Stub.** This chapter is written by the book-part4 task.\n")

    return out


def _repoint_other_md(src_dir: Path):
    """Repoint ./NN links in every non-chapter .md (appendices, README/Contents, getting-started) so
    the renumber leaves no dangling link anywhere in the copy. Chapters already carry new links."""
    chapters = set(ORDER)
    fixed = 0
    for md in src_dir.glob("*.md"):
        if md.name in chapters:
            continue
        text = md.read_text(encoding="utf-8")
        new = _repoint_links(text)
        if new != text:
            md.write_text(new, encoding="utf-8")
            fixed += 1
    return fixed


def _apply_to_dir(src_dir: Path, is_docs: bool):
    """Write the new set into src_dir, git-rm the collapsed orphans, repoint every other .md."""
    new_set = _build_new_set(src_dir)
    for fn, text in new_set.items():
        (src_dir / fn).write_text(text, encoding="utf-8")
    # remove old files that do not survive as a new filename
    survivors = set(new_set)
    for old in ALL_OLD:
        if old not in survivors and (src_dir / old).is_file():
            (src_dir / old).unlink()
    fixed = _repoint_other_md(src_dir)
    where = "docs/" if is_docs else "repo root"
    print(f"  {where}: wrote {len(new_set)} chapters, removed "
          f"{len(ALL_OLD - survivors)} orphans, relinked {fixed} other files")


def _patch_mkdocs():
    """Rewrite the nav's chapter entries to the target order/titles; keep Parts + appendices."""
    p = REPO_ROOT / "mkdocs.yml"
    text = p.read_text(encoding="utf-8")
    # Rebuild the whole nav block deterministically from the manifest, preserving Home + appendices.
    parts = [
        ("Part I — Foundations", ["00", "01"]),
        ("Part II — The three-beat loop", ["02", "03", "04", "05", "06"]),
        ("Part III — Operating the method", ["07", "08", "09", "10", "11"]),
        ("Part IV — Reference", ["12", "13", "14", "15", "16", "17", "18"]),
    ]
    lines = ["nav:", "  - Home: README.md"]
    for part_title, nums in parts:
        lines.append(f"  - {part_title}:")
        for num in nums:
            lines.append(f'      - "{TITLES[num]}": {FILE_BY_NUM[num]}')
    lines.append("  - Part V — Reference appendices:")
    for ap, title in [
        ("a-templates", "Appendix A · Templates"),
        ("b-prompts", "Appendix B · Prompt library"),
        ("c-glossary", "Appendix C · Glossary"),
        ("d-worked-example", "Appendix D · The worked example, end to end"),
        ("e-checklists", "Appendix E · Checklists"),
        ("f-requirements-matrix", "Appendix F · Document requirements matrix"),
        ("g-references", "Appendix G · References & lineage"),
        ("h-add-vs-spec-kit", "Appendix H · ADD vs spec-kit — the honest comparison"),
    ]:
        lines.append(f'      - "{title}": appendix-{ap}.md')
    new_nav = "\n".join(lines) + "\n"
    patched = re.sub(r"(?ms)^nav:\n.*\Z", new_nav, text)
    p.write_text(patched, encoding="utf-8")
    print("  patched mkdocs.yml nav")


def main():
    print("book_renumber: applying the frozen target TOC")
    _apply_to_dir(DOCS, is_docs=True)          # canonical — and its appendices/README relinked
    _apply_to_dir(REPO_ROOT, is_docs=False)    # mirror — repo-root README + other .md relinked here
    _patch_mkdocs()
    print("done. verify: python3 -m pytest tests/book/test_toc_structure.py")


if __name__ == "__main__":
    main()
