"""The receipt scratch file must not land in the working tree.

Two things are easy to conflate and only one is required:

  the JUnit XML   REQUIRED. It is what upgrades a receipt from `command-exit` (an exit code)
                  to `test-ids` (named checks). `covers:` binds against the IDs the runner
                  REPORTED, so with no XML nothing binds and the gate refuses every bound
                  rule — verified at standard AND quick depth.
  the path        NOT required. The engine parses whatever path it is handed. Verified:
                  `--junitxml /tmp/add-run-probe.xml` → kind test-ids, 2/2 reported, gate
                  PASS, zero repo footprint.

So the fix is docs-only. Nothing is ignored anywhere, because nothing lands anywhere.
The leak was hit live during `domain-evidence-recipe`, where `r.xml` reached the index.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
ADD_METHOD = REPO / "add-method"
SKILL_TREES = [ADD_METHOD / "skill" / "add",
               ADD_METHOD / "src" / "add_method" / "_bundled" / "skill" / "add",
               REPO / ".claude" / "skills" / "add"]
DOC_FILES = [ADD_METHOD / "GETTING-STARTED.md", *(ADD_METHOD / "docs").glob("*.md")]

# A backtick ENDS the token: these paths sit inside markdown inline code, and the closing
# backtick is markup, not part of the shell argument. Excluding it is correct parsing.
# Contrast with the quote: a quote IS part of the argument, and tolerating its absence is
# exactly what let three variants through the first gate — so that stayed strict, this did not.
JUNITXML = re.compile(r"--junitxml[= ]([^\s`]+)")
# a documented path is out-of-tree if it is absolute or resolves through a temp-dir variable
OUT_OF_TREE = re.compile(r"^(\$\{?TMPDIR|/tmp/|\$TMPDIR)")
PLACEHOLDER = re.compile(r"^<")


def _unquote(path: str) -> str:
    """Read the argument the way a SHELL would, not the way a regex first captures it.

    `--junitxml "${TMPDIR:-/tmp}/add-run.xml"` is correct — and better — shell than the bare
    form, but the naive capture keeps the opening quote, so every out-of-tree check read it as
    relative and failed. The docs were right and this parser was wrong; reshaping the docs to
    satisfy it would have shipped worse shell to make a broken check green.
    """
    return path.strip().strip('"\'').rstrip("`")


def _instructed():
    """(source, path) for every documented `--junitxml` argument on a shipped surface."""
    out = []
    for base in (*SKILL_TREES, *DOC_FILES):
        files = sorted(base.rglob("*.md")) if base.is_dir() else [base]
        for f in files:
            if f.is_file():
                out += [(f, _unquote(m.group(1)))
                        for m in JUNITXML.finditer(f.read_text(encoding="utf-8"))]
    return out


def test_documented_receipt_paths_are_outside_the_tree():
    """M1 — every instructed path resolves outside the working tree."""
    found = _instructed()
    assert found, "no --junitxml instruction found at all — the search is broken, not the docs"
    stray = sorted({(str(f.relative_to(REPO)), p) for f, p in found
                    if not OUT_OF_TREE.match(p) and not PLACEHOLDER.match(p)})
    assert not stray, f"receipt scratch documented inside the working tree: {stray}"


CANONICAL = '"${TMPDIR:-/tmp}/add-run.xml"'


def test_receipt_path_has_one_canonical_form():
    """M3 — one form, quoted, everywhere.

    The first gate passed on THREE variants (8 bare, 1 quoted, 1 with a stray trailing backtick).
    Every one is valid bash and `_unquote` accepted them all, so the check was honest about what
    it claimed — out-of-tree — and blind to the thing nobody had claimed. Bare `${TMPDIR:-/tmp}`
    also word-splits if TMPDIR ever contains a space. This pins the raw documented string, before
    any unquoting, so a variant cannot slip back in.
    """
    variants = {}
    for base in (*SKILL_TREES, *DOC_FILES):
        files = sorted(base.rglob("*.md")) if base.is_dir() else [base]
        for f in files:
            if not f.is_file():
                continue
            for m in JUNITXML.finditer(f.read_text(encoding="utf-8")):
                variants.setdefault(m.group(1), []).append(str(f.relative_to(REPO)))
    assert variants, "no --junitxml instruction found at all — the search is broken"
    stray = {v: sorted(set(w)) for v, w in variants.items() if v != CANONICAL}
    assert not stray, f"documented receipt path is not canonical ({CANONICAL}): {stray}"


def test_no_shipped_doc_writes_into_the_tree():
    """R:TREELEAK — a relative path is in-tree by definition, wherever it points."""
    leaks = sorted({(str(f.relative_to(REPO)), p) for f, p in _instructed()
                    if not p.startswith(("/", "$")) and not PLACEHOLDER.match(p)})
    assert not leaks, (f"shipped docs instruct an in-tree receipt artifact: {leaks} — "
                       f"a relative path lands in whatever directory the agent ran from")
