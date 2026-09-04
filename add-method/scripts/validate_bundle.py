#!/usr/bin/env python3
"""validate_bundle.py — the ABF-1 conformance validator.

    python3 scripts/validate_bundle.py <bundle-root> [--json] [--quiet]

Exits 0 iff the bundle has zero `error` findings (FORMAT.md §9). Stdlib only.

Two rules govern this script, and both come from the format it checks:

* **The verdict is frontmatter-only (T0).** Only three codes are `error`, and all three
  are decidable from frontmatter: `missing_frontmatter`, `type_empty`,
  `edge_out_of_bundle`. Bodies are read to *enrich* the report — heading-slug fragments,
  markdown links, `covers:` referents — and everything they produce is `info`. Replacing
  every body in a bundle with noise cannot change the exit code.
* **Notary, not guard** (law 3, OKF §11). Unknown keys, unknown types and broken links
  are recorded, never rejected. Only a containment escape is fatal.

Not implemented here, deliberately: `receipt_stale`, `covers_unverified` and
`placeholder_survived` are gate-time conditions that need a receipt and a freeze stamp to
evaluate. They belong to the engine (M1), not to a static scan, and claiming them here
would report an absence of findings that was never checked.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# Mirrors add.ABF_TYPES. `Interview` joined when `interview` began writing its `.d/interviews/`
# sidecar with frontmatter — the engine emits the type, so both oracles must know it.
ABF_TYPES = {"Project", "Milestone", "Task", "Spec", "Persona", "Prompt", "Run", "Interview"}
RESERVED = {"index.md", "log.md"}

# A23 (FORMAT §1.1) — reserved files whose bodies are rendered, not authored. Each must
# declare itself twice: a marker a human sees when they open it, and a `.gitattributes`
# entry git sees when it merges. Only checked once a file HAS a body: an empty
# `index.md` in the three-file minimum bundle has no generated content to lose.
COMPILED = ("index.md", "log.md")
COMPILED_MARKER = "COMPILED BODY"

# Only these keys carry graph edges. The allowlist is the point: `scope:` holds repo
# paths and `persona_corpus:` holds a config path — neither is a bundle edge, and a
# pattern-matching scanner that guessed would mis-read `templates/task.md.tmpl` as a
# link to `/task.md` (observed 2026-07-29, recorded in build-worked-example LESSONS).
EDGE_KEYS = {"depends_on", "needs", "tasks", "milestone", "relates_to", "task", "supersedes"}

# FORMAT §3.2's membership rule, mirrored from `add.py`'s `MEMBERSHIP_KEY`/`_membership_ref`.
# Mirrored rather than imported: this validator is the SECOND oracle and must stay a standalone
# script. The two copies are held to one value by a parity test that drives both readers over
# one bundle — a resolving membership is silent in both, a dangling one is reported by both.
MEMBERSHIP_KEY = "milestone"
MEMBERSHIP_DIR = "milestones"
SLUG = re.compile(r"\A[A-Za-z0-9][A-Za-z0-9._-]*\Z")


def membership_ref(key, ref):
    """A bare-slug `milestone:` value -> the ref it names; `""` when the value is not one."""
    if key != MEMBERSHIP_KEY or ".md" in ref or not SLUG.match(ref):
        return ""
    return f"/{MEMBERSHIP_DIR}/{ref}.md"

# The SECOND edge family (FORMAT §3.2): `relations:` entries are `<src delta id> <rel> <ref>`,
# one plain string per block-list item. Mirrors `add.RELATION_VOCAB` and MUST stay in lockstep —
# this script is stdlib-only and standalone, so it cannot import the engine. The lockstep is not
# left to a human: `tests/engine/test_typed_relations.py::test_the_second_oracle_mirrors_the_one
# _vocabulary` drives every term of the ENGINE's tuple through this script and requires silence,
# then drives a non-term and requires a report.
RELATION_VOCAB = {"refines"}

# §3.3's third fragment form: a delta id in the target's body. Mirrors `add.parse_delta_head`'s
# grammar field for field — a LAXER reader here would resolve a fragment the engine's own delta
# grammar rejects, and the two oracles would disagree about what a concept address means.
DELTA_HEAD = re.compile(r"^-\s+\[([^\]]*)\]")
DELTA_ID = re.compile(r"\A[A-Za-z][A-Za-z0-9_-]*\Z")
DELTA_DATE = re.compile(r"\A\d{4}-\d{2}-\d{2}\Z")
DELTA_ARROW = "\u2192"
DELTA_STATUSES = {"open", "folded", "rejected"}
DELTA_TERMINAL = {"folded", "rejected"}
DELTA_COMPS = {"DDD", "SDD", "UDD", "TDD", "ADD",
               "domain", "system", "experience", "quality", "method"}

FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n?(.*)\Z", re.DOTALL)
MD_LINK = re.compile(r"\]\(([^)\s]+\.md)\)")

# FORMAT §6.1 — the legal `covers:` referents, by depth. Stated HERE, once, as module
# constants rather than compiled inline where they are used: a grammar with no address
# cannot be cited by a second oracle, and two oracles that cannot cite each other drift
# (F1, open since M0). `tests/test_covers_grammar.py` holds these against the
# `covers-grammar` block in FORMAT §6.1 and against the engine's `RULE_ID`.
#
# RESOLVED (e15, human:tindang 2026-07-30): widened to admit digits, matching the engine.
# These two patterns are byte-identical to the `covers-grammar` block in FORMAT §6.1, and
# `tests/test_covers_grammar.py::test_grammar_stated_once` asserts that equality rather
# than trusting a human to re-check it.
COVERS_QUICK = re.compile(r"\A(goal|G\d+)\Z")
COVERS_RULE = re.compile(r"\A(M\d+|R:[A-Z0-9_]+|E\d+)\Z")

# A `covers:` referent is a field of a CHECKS list item (FORMAT §8.3), so it is matched
# line-anchored and only inside that section. An unanchored scan of the whole body reads
# `· covers: …` out of PLAN prose and then runs `[^·]+?` across newlines, which both
# invents referents and swallows the real check lines behind them (observed on
# tasks/build-evidence-binding.md: 4 of this bundle's 7 `covers_referent` lines).
# The engine's `COVERS_IN_CHECK` is anchored the same way, for the same reason.
COVERS_IN_CHECK = re.compile(r"^-\s+\S+\s+·\s*covers:\s*([^·\n]+?)\s*·", re.MULTILINE)
SECTION = "## "


def section_of(body: str, name: str) -> str:
    """The body of one `## <name>` section, heading exclusive, "" when absent."""
    out, collecting = [], False
    for line in body.splitlines():
        if line.startswith(SECTION):
            collecting = line[len(SECTION) :].strip() == name
            continue
        if collecting:
            out.append(line)
    return "\n".join(out)


# --------------------------------------------------------------------------- parsing


def strip_comment(line: str) -> str:
    """Drop a trailing `#` comment, honouring quotes — mirrors `add._strip_comment`.

    Without this the two oracles read DIFFERENT VALUES out of one line: the engine strips a
    YAML comment and this script did not, so `- M1 refines #M2` was `M1 refines` (two fields,
    `relation_malformed`) in one and `M1 refines #M2` (three fields, an edge) in the other.
    A `#` with no space before it is data — that is what keeps `/specs/method.md#M21` a fragment.
    """
    if "#" not in line:
        return line
    quote = None
    for i, ch in enumerate(line):
        if quote:
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
        elif ch == "#" and (i == 0 or line[i - 1].isspace()):
            return line[:i]
    return line


def parse_frontmatter(text: str):
    """Return (frontmatter_dict, body) or (None, text) when there is no frontmatter.

    A deliberately small YAML subset — enough for T0: top-level scalars, block lists,
    inline empty lists, and block scalars (whose value is discarded, but whose KEY is
    recorded, because fragment resolution asks whether a key exists).
    """
    m = FRONTMATTER.match(text)
    if not m:
        return None, text
    raw, body = m.group(1), m.group(2)
    data, current = {}, None
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        line = strip_comment(line)
        if not line.strip():
            continue
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        if stripped.startswith("- "):
            if current is not None and isinstance(data.get(current), list):
                data[current].append(stripped[2:].strip().strip("\"'"))
            continue
        if indent == 0 and ":" in stripped:
            key, _, value = stripped.partition(":")
            key, value = key.strip(), value.strip()
            if value in ("", "[]", ">-", ">", "|", "|-"):
                data[key] = []
                current = key if value in ("", "[]") else None
            else:
                data[key] = value.strip("\"'")
                current = None
    return data, body


def delta_ids(body: str) -> set[str]:
    """Every well-formed dated delta id in a body — FORMAT §3.3's third resolution form."""
    out = set()
    for line in body.splitlines():
        m = DELTA_HEAD.match(line.strip())
        if not m:
            continue
        fields = [f.strip() for f in m.group(1).split("\u00b7")]
        if len(fields) != 4:
            continue
        comp, did, status, interval = fields
        if status not in DELTA_STATUSES or comp not in DELTA_COMPS or not DELTA_ID.match(did):
            continue
        ends = [e.strip() for e in interval.split(DELTA_ARROW)]
        if len(ends) > 2 or any(not DELTA_DATE.match(e) for e in ends):
            continue
        if len(ends) == 2 and (status not in DELTA_TERMINAL or ends[1] < ends[0]):
            continue
        out.add(did)
    return out


def heading_slugs(body: str) -> set[str]:
    slugs = set()
    for line in body.splitlines():
        if line.startswith("#"):
            text = line.lstrip("#").strip()
            slugs.add(re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", text.lower())).strip("-"))
    return slugs


# --------------------------------------------------------------------------- scanning


class Scan:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.findings: list[dict] = []
        self.nodes: dict[str, dict] = {}
        self.report = {
            "depths": [],
            "statuses": [],
            "types": [],
            "fragment_forms": {"frontmatter_key": 0, "heading_slug": 0,
                               "delta_id": 0, "unresolved": 0},
            "relation_count": 0,
            "resolved_fragments": {},
            "node_count": 0,
            "edge_count": 0,
        }

    def find(self, severity, code, detail):
        self.findings.append({"severity": severity, "code": code, "detail": detail})

    # -- pass 1: every file's frontmatter (this pass alone decides the verdict) --
    def load(self):
        for path in sorted(self.root.rglob("*.md")):
            rel = path.relative_to(self.root).as_posix()
            if rel.split("/", 1)[0] in ("tooling", "personas-teacher", "personas-index"):
                continue  # vendored engine material, seed corpus, and its generated routing index —
                # not project nodes (mirrors add.scan; the two lists must stay in lockstep)
            text = path.read_text(encoding="utf-8")
            fm, body = parse_frontmatter(text)
            if fm is None:
                if rel not in RESERVED:
                    self.find("error", "missing_frontmatter", rel)
                continue
            node_type = fm.get("type")
            if not node_type or not isinstance(node_type, str):
                if rel not in RESERVED:
                    self.find("error", "type_empty", rel)
            elif node_type not in ABF_TYPES:
                self.find("info", "unknown_type", f"{rel}: {node_type}")
            self.nodes["/" + rel] = {"rel": rel, "fm": fm, "body": body}
        self.report["node_count"] = len(self.nodes)

    # -- pass 2: edges --
    def edges(self):
        for cid, node in self.nodes.items():
            for key in EDGE_KEYS & node["fm"].keys():
                value = node["fm"][key]
                for ref in value if isinstance(value, list) else [value]:
                    ref = str(ref).strip()
                    if ".md" not in ref:
                        # §3.2: `milestone:` alone resolves a bare slug, because membership is
                        # the one key whose target directory is implied. Every other bare value
                        # stays a non-edge, which is what keeps `edge_unresolved` meaningful.
                        if not (ref := membership_ref(key, ref)):
                            continue
                    self.report["edge_count"] += 1
                    self.resolve(cid, node, ref)

    def resolve(self, cid, node, ref):
        target, _, fragment = ref.partition("#")
        if target.startswith("/"):
            resolved = (self.root / target.lstrip("/")).resolve()
        else:
            resolved = (self.root / node["rel"]).parent.joinpath(target).resolve()
        if not resolved.is_relative_to(self.root):
            self.find("error", "edge_out_of_bundle", f"{node['rel']} -> {ref}")
            return
        tid = "/" + resolved.relative_to(self.root).as_posix()
        if tid not in self.nodes:
            self.find("info", "edge_unresolved", f"{node['rel']} -> {ref}")
            if fragment:
                self.report["fragment_forms"]["unresolved"] += 1
            return
        if not fragment:
            return
        # FORMAT §3.3: frontmatter key first, then heading slug, else unresolved.
        form = (
            "frontmatter_key"
            if fragment in self.nodes[tid]["fm"]
            else "heading_slug"
            if fragment in heading_slugs(self.nodes[tid]["body"])
            else "delta_id"
            if fragment in delta_ids(self.nodes[tid]["body"])
            else "unresolved"
        )
        self.report["fragment_forms"][form] += 1
        self.report["resolved_fragments"][f"{tid}#{fragment}"] = form
        if form == "unresolved":
            self.find("info", "edge_unresolved", f"{node['rel']} -> {ref}")

    # -- pass 2b: the SECOND edge family (§3.2) --
    def relations(self):
        """`relations:` — typed CONCEPT edges. The target end reuses `resolve` unchanged.

        Reusing it is the point: the containment decision for a relation must be the identical
        code at the identical severity as for a `depends_on:` naming the identical target. The
        head is stripped HERE, before `resolve` ever sees the value — passing the whole entry
        would let the rel token absorb a `../` and silently downgrade `edge_out_of_bundle`.
        """
        for cid, node in self.nodes.items():
            value = node["fm"].get("relations")
            if value is None:
                continue
            for entry in (value if isinstance(value, list) else [value]):
                fields = str(entry).strip().split()
                if len(fields) != 3:
                    self.find("info", "relation_malformed",
                              f"{node['rel']} -> {str(entry).strip()}")
                    continue
                src_id, verb, ref = fields
                self.report["relation_count"] += 1
                if verb not in RELATION_VOCAB:
                    self.find("info", "unknown_rel", f"{node['rel']} -> {verb} ({ref})")
                if src_id not in delta_ids(node["body"]):
                    self.find("info", "edge_unresolved", f"{node['rel']} -> {src_id}")
                self.resolve(cid, node, ref)

    # -- pass 3: body-derived enrichment; every finding here is `info` --
    def bodies(self):
        depths, statuses, types = set(), set(), set()
        for cid, node in self.nodes.items():
            fm, body, rel = node["fm"], node["body"], node["rel"]
            if isinstance(fm.get("depth"), str):
                depths.add(fm["depth"])
            if isinstance(fm.get("status"), str):
                statuses.add(fm["status"])
            if isinstance(fm.get("type"), str):
                types.add(fm["type"])

            # FORMAT §6.1 — what `covers:` may refer to, by depth.
            depth = fm.get("depth")
            if fm.get("type") == "Task" and isinstance(depth, str):
                pattern = COVERS_QUICK if depth == "quick" else COVERS_RULE
                for group in COVERS_IN_CHECK.findall(section_of(body, "CHECKS")):
                    for key in (k.strip() for k in group.split(",")):
                        if key and not pattern.match(key):
                            self.find(
                                "info",
                                "covers_referent",
                                f"{rel}: depth={depth} cannot cite `{key}`",
                            )

            for link in MD_LINK.findall(body):
                if link.startswith(("http://", "https://")):
                    continue
                if not (self.root / rel).parent.joinpath(link).exists():
                    self.find("info", "broken_md_link", f"{rel} -> {link}")

        self.report["depths"] = sorted(depths)
        self.report["statuses"] = sorted(statuses)
        self.report["types"] = sorted(types)

    # -- pass 4: A23 — compiled files declare themselves; `info` only --
    def compiled(self):
        attrs = self.root / ".gitattributes"
        declared = attrs.read_text(encoding="utf-8") if attrs.is_file() else ""
        for name in COMPILED:
            path = self.root / name
            if not path.is_file():
                continue
            _, body = parse_frontmatter(path.read_text(encoding="utf-8"))
            if not body.strip():
                continue  # nothing rendered yet, so nothing a human can lose
            missing = []
            if COMPILED_MARKER not in body:
                missing.append(f"no `{COMPILED_MARKER}` marker")
            if not any(line.split()[:1] == [name] for line in declared.splitlines()):
                missing.append("no .gitattributes entry")
            if missing:
                self.find("info", "compiled_undeclared", f"{name}: {', '.join(missing)}")

    def run(self):
        self.load()
        self.edges()
        self.relations()
        self.bodies()
        self.compiled()
        return self

    @property
    def errors(self):
        return [f for f in self.findings if f["severity"] == "error"]


# --------------------------------------------------------------------------- output


def main(argv=None):
    ap = argparse.ArgumentParser(description="Validate an ABF-1 bundle.")
    ap.add_argument("bundle", type=Path)
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--quiet", action="store_true", help="verdict line only")
    args = ap.parse_args(argv)

    if not args.bundle.is_dir():
        print(f"[error] no such bundle: {args.bundle}", file=sys.stderr)
        return 2

    scan = Scan(args.bundle).run()
    failed = len(scan.errors)

    if args.json:
        json.dump({"findings": scan.findings, "report": scan.report}, sys.stdout, indent=2)
        sys.stdout.write("\n")
        # A6: the affordance line goes to stderr so stdout stays parseable.
        print(next_line(scan, failed), file=sys.stderr)
        return 1 if failed else 0

    if not args.quiet:
        for f in scan.findings:
            print(f"  [{f['severity']}] {f['code']}: {f['detail']}")
        if not scan.findings:
            print("  no findings")
    r = scan.report
    print(
        f"\n{r['node_count']} nodes · {r['edge_count']} edges · "
        f"{len(scan.findings) - failed} info · {failed} error"
    )
    print("CONFORMS" if not failed else f"DOES NOT CONFORM — {failed} error finding(s)")
    print(next_line(scan, failed))
    return 1 if failed else 0


def next_line(scan, failed):
    """A6 — every verb's output ends with the exact next command."""
    if failed:
        first = scan.errors[0]
        return f"next: fix {first['code']} in {first['detail'].split(' ->')[0]}, then re-run this validator"
    return "next: record the receipt — python3 -m pytest tests/ -q --junitxml=<receipt>.xml"


if __name__ == "__main__":
    raise SystemExit(main())
