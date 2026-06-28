"""add_engine.release — the RELEASE-pillar render helpers (engine-modularization 14/N).

Render the CHANGELOG block and the append-only RELEASES.md attribution row, locate the
ledger, find closed milestones / key decisions for a cut, and summarise the in-flight build.
A closed, unpatched cluster (transitive-closure AST = zero outbound). Deps: constants + stdlib.
"""
from __future__ import annotations

import re
from pathlib import Path

from add_engine.constants import RELEASES_FILE


def _releases_path(root: Path) -> Path:
    """The append-only release ledger — at the PROJECT ROOT (root IS the .add dir, so its
    parent), a sibling of CHANGELOG.md. NOT inside .add/."""
    return root.parent / RELEASES_FILE

def _closed_milestones(state: dict) -> list[dict]:
    """Every CLOSED milestone (its milestone-done gate passed): LIVE done milestones
    (status == 'done', still in state) + ARCHIVED milestones (all were PASS-done before
    archive — see _archived_task_slugs). Each: {slug, title, tier}."""
    out: list[dict] = []
    for slug, m in (state.get("milestones") or {}).items():
        if m.get("status") == "done":
            out.append({"slug": slug, "title": m.get("title", slug), "tier": "live"})
    for rec in state.get("archived") or []:
        if rec.get("slug"):
            out.append({"slug": rec["slug"], "title": rec.get("title", rec["slug"]),
                        "tier": "archived"})
    return out

def _key_decisions_for(root: Path, slug: str) -> list[str]:
    """Best-effort §Key-Decisions rows from PROJECT.md that NAME this milestone slug — the
    consolidated decisions the changelog can cite. Fail-open: a missing section / unreadable
    foundation / no slug match -> [] (a gather never raises). READ-ONLY."""
    try:
        text = (root / "PROJECT.md").read_text(encoding="utf-8")
    except OSError:
        return []
    m = re.search(r"^#{1,6}[^\n]*key decision[^\n]*$(.*?)(?=^#{1,6}\s|\Z)", text, re.S | re.M | re.I)
    if not m:
        return []
    return [st.lstrip("-* ").strip() for st in (ln.strip() for ln in m.group(1).splitlines())
            if st.startswith(("-", "*")) and slug in st]

def _build_in_flight(state: dict) -> bool:
    """release_build_in_flight proxy (PURE): is any ACTIVE task mid-build without a recorded green
    gate — phase ∈ {build, verify} AND gate == 'none'? The tool-agnostic engine never runs the
    suite, so an entered-but-ungated build is the recorded-evidence stand-in for 'the suite is red'."""
    return any(t.get("phase") in ("build", "verify") and t.get("gate") == "none"
               for t in (state.get("tasks") or {}).values())

def _render_changelog_block(version: str, day: str, bundle: list[dict],
                            changed_by_slug: dict) -> str:
    """A CHANGELOG block: `## <version> — <date>` + one bullet per bundled milestone (title +
    carried-delta / key-decision counts from release_data['changed'])."""
    lines = [f"## {version} — {day}", ""]
    if bundle:
        for m in bundle:
            c = changed_by_slug.get(m["slug"], {})
            lines.append(f"- {m['title']} — {c.get('carried_deltas', 0)} carried · "
                         f"{len(c.get('key_decisions', []))} key decision(s)")
    else:
        lines.append("- (no milestone bundled)")
    return "\n".join(lines) + "\n\n"

def _render_releases_row(version: str, day: str, bundle: list[dict],
                         waiver_slugs: list[str], evidence: str | None,
                         actor: str | None = None, loose: list[dict] | None = None) -> str:
    """One append-only RELEASES.md row — the attribution source (`milestones:` membership +,
    additively, `loose tasks:` membership for done milestone-free standalones). The `actor:`
    line records WHO cut the release (structured-actor stamping); absent on a legacy row
    (back-compat) when no actor is supplied. `loose` defaults to None so existing callers keep
    working; the `loose tasks:` line always renders (`none` when empty), the other lines unchanged."""
    ms = ", ".join(m["slug"] for m in bundle) if bundle else "none"
    lt = ", ".join(t["slug"] for t in loose) if loose else "none"
    wv = ", ".join(waiver_slugs) if waiver_slugs else "none"
    actor_line = f"actor: {actor}\n" if actor else ""
    return (f"## {version} — {day}\n"
            f"milestones: {ms}\n"
            f"loose tasks: {lt}\n"
            f"waivers: {wv}\n"
            f"{actor_line}"
            f"evidence: {evidence or 'recorded by add.py release'}\n\n")
