#!/usr/bin/env python3
"""Deterministically refresh the vendored teacher snapshot under add-method/personas-teacher/.

Standalone maintenance script — run by a human or the scheduled refresh CI. It is NEVER imported or
invoked by the ADD engine (the engine performs no fetch and no child-process launch; the release
build is zero-network and reads only the committed snapshot).

What it does:
  1. clone the upstream teacher repo at a ref (default: its default branch HEAD) into a temp dir,
  2. apply the TRIM rules (keep the agent-definition domain folders + LICENSE + README + roster
     manifests; drop the upstream CI, scripts, other-tool integrations, contributing/dotfiles),
  3. replace add-method/personas-teacher/ with the trimmed tree,
  4. rewrite personas-teacher/VENDOR.md with the resolved commit SHA + fetch date + the trim rules.

Usage:  python3 add-method/scripts/update_teacher.py [--ref <git-ref>] [--date YYYY-MM-DD]
The vendored content is RAW + verbatim — this script never edits an upstream file's contents.
"""
import argparse
import shutil
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

UPSTREAM = "https://github.com/msitarzewski/agency-agents"
HERE = Path(__file__).resolve().parent
DEST = HERE.parent / "personas-teacher"

# TRIM rules (frozen by the vendor-teacher-snapshot contract):
DROP_DIRS = {".git", ".github", "scripts", "integrations"}
DROP_FILES = {
    "CONTRIBUTING.md", "CONTRIBUTING_zh-CN.md", "SECURITY.md",
    ".gitignore", ".gitattributes",
}


def _run(cmd, cwd=None):
    subprocess.run(cmd, cwd=cwd, check=True)


def _resolve_sha(repo: Path) -> str:
    out = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                         check=True, capture_output=True, text=True)
    return out.stdout.strip()


def _apply_trim(src: Path, dst: Path) -> None:
    """Copy src→dst keeping only agent material. Verbatim file contents."""
    dst.mkdir(parents=True, exist_ok=True)
    for child in sorted(src.iterdir()):
        if child.name in DROP_DIRS or child.name in DROP_FILES:
            continue
        target = dst / child.name
        if child.is_dir():
            shutil.copytree(child, target)
        else:
            shutil.copy2(child, target)


def _write_vendor(sha: str, fetched: str) -> None:
    body = (
        "# Vendored teacher snapshot — pin record\n\n"
        f"- upstream: {UPSTREAM}\n"
        f"- commit:   {sha}\n"
        f"- fetched:  {fetched}\n\n"
        "## Trim rules (what is vendored)\n\n"
        "KEEP: the agent-definition domain folders (engineering, security, design, product, "
        "finance, marketing, testing, sales, support, strategy, project-management, academic, "
        "game-development, gis, spatial-computing, paid-media, specialized, examples), plus "
        "`README.md` and the `divisions.json`/`tools.json` roster manifests, plus `LICENSE`.\n\n"
        "DROP: the upstream `.github/` CI, `scripts/`, other-tool `integrations/`, "
        "`CONTRIBUTING*`, `SECURITY.md`, and dotfiles.\n\n"
        "Content is RAW + verbatim — regenerate with "
        "`python3 add-method/scripts/update_teacher.py`. Attribution: see the repo-root "
        "`THIRD_PARTY_NOTICES.md` and the retained `LICENSE` in this folder (MIT).\n"
    )
    (DEST / "VENDOR.md").write_text(body, encoding="utf-8")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Refresh the vendored teacher snapshot.")
    ap.add_argument("--ref", default=None, help="git ref/SHA to vendor (default: upstream HEAD)")
    ap.add_argument("--date", default=None, help="fetch date stamp (default: today, UTC)")
    args = ap.parse_args(argv)

    fetched = args.date or date.today().isoformat()
    with tempfile.TemporaryDirectory() as tmp:
        clone = Path(tmp) / "upstream"
        _run(["git", "clone", UPSTREAM, str(clone)])
        if args.ref:
            _run(["git", "-C", str(clone), "checkout", "--detach", args.ref])
        sha = _resolve_sha(clone)
        staged = Path(tmp) / "staged"
        _apply_trim(clone, staged)
        if DEST.exists():
            shutil.rmtree(DEST)
        shutil.move(str(staged), str(DEST))
        _write_vendor(sha, fetched)
    print(f"vendored teacher snapshot @ {sha} -> {DEST}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
