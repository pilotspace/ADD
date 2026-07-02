#!/usr/bin/env python3
"""add_engine.predicates — pure state/markdown predicates for the ADD engine.

Phase ownership, setup/milestone gating checks, and section-filled detection.
Extracted from add.py (engine-modularization 5/N); add.py re-exports them as module
globals so `add._phase_owner` etc. resolve unchanged.
"""
from __future__ import annotations

import re

from add_engine.constants import (
    PHASE_OWNER, PERSONA_FRONTMATTER_KEYS, PERSONA_REQUIRED_SECTIONS,
    _MUST_ID_RE, _REJECT_CODE_RE, _SCENARIO_TAG_RE, _COVERS_LINE_RE, _TAG_TOKEN_RE,
)
from add_engine.io_state import _die


def _phase_owner(phase: str) -> str:
    """Map a phase to its owner (human|seam|ai); `unmapped_phase` if absent (fail closed)."""
    owner = PHASE_OWNER.get(phase)
    if owner is None:
        _die("unmapped_phase")
    return owner

def _setup_locked(state: dict) -> bool:
    """True when the project's setup is locked — i.e. the build-boundary gate is OPEN.

    A state with NO "setup" key is GRANDFATHERED-locked: plain `init` and every legacy
    project are never gated (the lock is opt-in via `init --await-lock`). The gate is
    therefore active in exactly one case: "setup" present AND locked is False."""
    return ("setup" not in state) or (state["setup"].get("locked") is True)

def _milestone_confirmed(state: dict, mslug: str) -> bool:
    """True when milestone `mslug` is confirmed — i.e. the new-task gate is OPEN.

    Mirrors `_setup_locked` one level down. A milestone record with NO "confirmed" key is
    GRANDFATHERED-confirmed: every milestone created WITHOUT `--await-confirm` (and every
    pre-existing one) is never gated. Opt-in: `new-milestone --await-confirm` seeds confirmed:false,
    so the gate is active in exactly one case: the record is present AND confirmed is False. An
    unknown milestone is treated as confirmed here (existence is cmd_new_task's separate check)."""
    m = (state.get("milestones") or {}).get(mslug)
    if not isinstance(m, dict) or "confirmed" not in m:
        return True
    return m["confirmed"] is True

def _section_unfilled(md_text: str, header: str) -> bool:
    """True iff the `header` section is PRESENT but UNFILLED — empty (no real bullet) or
    still a `<…>` template placeholder. ABSENT section -> False (grandfathered legacy);
    a filled section (>=1 real bullet, no `<…>`) -> False. Pure predicate — the shared
    placeholder test the fill gates use (contract-fill at confirm; build-expectations at build).
    Angle brackets INSIDE a backtick code span are literal technical notation (`<persona>`,
    `.add/personas/<slug>.md`), not a fill placeholder — only a BARE <…> counts as unfilled."""
    body, in_sec, present = [], False, False
    for ln in md_text.splitlines():
        if ln.startswith(header):
            in_sec, present = True, True
            continue
        if in_sec:
            if ln.startswith("#"):          # ANY next header (## or ###) ends our section
                break
            if ln.lstrip().startswith(">"):  # skip blockquote GUIDANCE — it is not content
                continue
            body.append(ln)
    if not present:
        return False                        # absent -> grandfather
    text = "\n".join(body).strip()
    if not text:
        return True                         # present but empty
    no_code = re.sub(r"`[^`\n]*`", "", text)     # drop code spans — backtick <…> is content
    return bool(re.search(r"<[^>\n]+>", no_code))  # a BARE <…> placeholder remains


def _persona_missing(md_text: str) -> list[str]:
    """The required frontmatter keys + section headers ABSENT from a persona file
    (`.add/personas/<slug>.md`). `[]` == schema-conformant. Presence-based: a section
    counts as present iff its `## <Title>` header line appears; a frontmatter key counts
    iff a `^<key>:` line appears inside the leading `---`-fenced block. Content QUALITY is
    the AI's authoring concern, not this gate (measure-not-block). PURE; NO-EXEC — no file IO,
    no network, no process launch. The single source of truth is constants.PERSONA_* so the
    schema and its validator never drift."""
    missing: list[str] = []
    fm = re.match(r"\s*---\s*\n(.*?)\n---\s*\n", md_text, re.S)
    fm_body = fm.group(1) if fm else ""
    for key in PERSONA_FRONTMATTER_KEYS:
        if not re.search(rf"(?m)^\s*{re.escape(key)}\s*:", fm_body):
            missing.append(key)
    for section in PERSONA_REQUIRED_SECTIONS:
        if not re.search(rf"(?m)^{re.escape(section)}\s*$", md_text):
            missing.append(section)
    return missing


def _persona_slug_valid(slug: str) -> bool:
    """A persona file slug is valid iff non-empty and alphanumeric with `-`/`_` only
    (mirrors new-task's slug rule). PURE; NO-EXEC."""
    return bool(slug) and slug.replace("-", "").replace("_", "").isalnum()


def _rule_coverage_gaps(sec1: str, sec2: str, sec4: str) -> list[tuple[str, str]]:
    """§1 Must/Reject IDs with no §2 scenario tag and no §4 `covers:` reference — a coverage
    gap (rule-id-coverage). A task that carries NO tag anywhere in §2/§4 is grandfathered
    (never adopted the convention) -> []. A bare `<…>` template placeholder (e.g. the
    unfilled `covers: <M#, R:code — optional>` scaffold) is stripped before scanning — it
    is not authored content, mirrors `_section_unfilled`'s own placeholder convention.
    De-dupes a repeated/typo'd ID. PURE; NO-EXEC."""
    strip_placeholders = lambda text: re.sub(r"<[^>\n]+>", "", text or "")
    tag_ids: set[str] = set()
    for m in _SCENARIO_TAG_RE.finditer(strip_placeholders(sec2)):
        tag_ids.update(_TAG_TOKEN_RE.findall(m.group(1)))
    for m in _COVERS_LINE_RE.finditer(strip_placeholders(sec4)):
        tag_ids.update(_TAG_TOKEN_RE.findall(m.group(1)))
    if not tag_ids:
        return []                                          # grandfathered — never opted in
    musts = [(mid, "Must") for mid in _MUST_ID_RE.findall(sec1 or "")]
    rejects = [(f"R:{code}", "Reject") for code in _REJECT_CODE_RE.findall(sec1 or "")]
    gaps = [(rid, kind) for rid, kind in musts + rejects if rid not in tag_ids]
    return list(dict.fromkeys(gaps))                        # de-dup a repeated ID


def _task_done(t: dict) -> bool:
    # Matrix 3: a task is done when Verify reads PASS *or a signed RISK-ACCEPTED*.
    # Both completing gates advance phase to "done" (cmd_gate), and a waiver is
    # signed at gate time — so a verdict gate is enough here; we need not re-read
    # the waiver. HARD-STOP never reaches "done". A bare `phase done` (escape
    # hatch, gate still "none") deliberately does NOT count: completion needs a
    # recorded verdict, not just a phase marker.
    return t.get("phase") == "done" and t.get("gate") in ("PASS", "RISK-ACCEPTED")
