#!/usr/bin/env python3
"""add_engine.predicates — pure state/markdown predicates for the ADD engine.

Phase ownership, setup/milestone gating checks, and section-filled detection.
Extracted from add.py (engine-modularization 5/N); add.py re-exports them as module
globals so `add._phase_owner` etc. resolve unchanged.
"""
from __future__ import annotations

import re

from add_engine.constants import (
    PHASE_OWNER, PHASE_GROUPS, PERSONA_FLOW_VALUES, PERSONA_FRONTMATTER_KEYS, PERSONA_REQUIRED_SECTIONS,
    TASK_KINDS,
    _MUST_ID_RE, _REJECT_CODE_RE, _SCENARIO_TAG_RE, _COVERS_LINE_RE, _TAG_TOKEN_RE,
)
from add_engine.io_state import _die


def _phase_owner(phase: str) -> str:
    """Map a phase to its owner (human|seam|ai); `unmapped_phase` if absent (fail closed)."""
    owner = PHASE_OWNER.get(phase)
    if owner is None:
        _die("unmapped_phase")
    return owner

def _phase_bundle(phase: str) -> str | None:
    """Map a phase to its PHASE_GROUPS bundle name (DIRECTION|BUILD|VERIFY); `None` for
    the terminal "done" phase (a deliberate, documented non-crash — done is a human-led
    terminal state, not work any of the three roster agents drive); `_die
    ("unmapped_phase_bundle")` for any other token absent from PHASE_GROUPS (fail closed,
    mirrors `_phase_owner`'s exact idiom)."""
    if phase == "done":
        return None
    for bundle, phases in PHASE_GROUPS.items():
        if phase in phases:
            return bundle
    _die("unmapped_phase_bundle")

def _ai_freeze_allowed(gate_mode: str | None, sensitivity: str | None, autonomy: str) -> tuple[bool, str | None]:
    """The ai-plan-verify-gate predicate: may an AI agent perform the §3 contract freeze in
    place of a human? PURE, fail-closed. A BLOCK-list (not an allow-list of one, human freeze
    decision 2026-07-09): the human floor is exactly {security, data, architecture} plus a
    malformed "?" token; undeclared sensitivity (None), the literal "mechanical" token, and any
    other valid project-GLOSSARY class all qualify — the double opt-in (gate_mode: ai-plan-verify
    AND autonomy: auto, both human-declared) IS the sign-off. Sibling of advisor-gate-relax (a
    DIFFERENT, narrower allow-list-of-"mechanical" floor at the VERIFY/completion boundary) —
    related but not identical floors, never interchangeable."""
    if gate_mode != "ai-plan-verify":
        return False, "ai_freeze_not_opted_in"
    if autonomy != "auto":
        return False, "ai_freeze_requires_auto"
    if sensitivity in ("security", "data", "architecture"):
        return False, "ai_freeze_blocked_sensitivity"
    if sensitivity == "?":
        return False, "ai_freeze_unknown_sensitivity"
    return True, None


def _skip_lane_eligible(fast: bool, oneshot: bool, benchmark_mode: bool) -> bool:
    """fast-lane-skips: may a task declare a scenarios/observe skip at all? PURE. True iff
    ANY of the three independent triggers MILESTONE.md Scope(3) names is set — the existing
    fast lane, the new --oneshot flag, or a project-wide benchmark_mode:true opt-in. Does not
    itself validate the declared token set (see _skip_set_allowed) — single responsibility."""
    return fast or oneshot or benchmark_mode


def _skip_set_allowed(skip_tokens: frozenset[str], eligible: bool) -> tuple[bool, str | None]:
    """fast-lane-skips: may THIS declared (already closed-set-validated) skip-set be honored?
    PURE, fail-closed. `skip_tokens` is assumed already validated by _task_skip_set — this
    predicate's single responsibility is the LANE-ELIGIBILITY axis, not set-membership (two
    distinct error codes for two distinct failure shapes, mirrors _ai_freeze_allowed's split
    from _task_gate_mode). An EMPTY skip-set is always permitted (nothing declared, nothing to
    gate) regardless of eligibility."""
    if skip_tokens and not eligible:
        return False, "skip_lane_required"
    return True, None


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
    placeholder test the contract-fill gate uses at confirm.
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


def _persona_quality_warnings(md_text: str) -> list[str]:
    """Quality findings the presence-based schema check can't see (persona-schema-hardening).
    `[]` == clean. WARN-only at the caller (measure-not-block); never a gate. Two findings:
    (A) a `flow:` frontmatter value outside PERSONA_FLOW_VALUES — no apply-surface loads an
    unknown flow, so a typo otherwise fails silently; an ABSENT `flow:` line is conformant
    (that is `_persona_missing` territory, and flow is only RECOMMENDED). (B) a bare `<…>`
    placeholder outside backtick code spans and HTML comments — a half-filled template copy
    passes the presence check. PURE; NO-EXEC — text in, list of strings out."""
    findings: list[str] = []
    fm = re.match(r"\s*---\s*\n(.*?)\n---\s*\n", md_text, re.S)
    fm_body = fm.group(1) if fm else ""
    m = re.search(r"(?m)^\s*flow\s*:\s*(.+)$", fm_body)
    if m:
        for v in (tok.strip() for tok in m.group(1).split(",")):
            if v and v not in PERSONA_FLOW_VALUES:
                findings.append(f"flow value '{v}' not one of " + "|".join(PERSONA_FLOW_VALUES))
    # (C) persona-task-kinds: a `task-kinds:` value outside the closed taxonomy scores as
    # NOTHING on the persona scoreboard (the trace join key never matches), so a typo would
    # otherwise fail silently — same shape as Finding A; an ABSENT line is conformant.
    m = re.search(r"(?m)^\s*task-kinds\s*:\s*(.+)$", fm_body)
    if m:
        for v in (tok.strip() for tok in m.group(1).split(",")):
            if v and v not in TASK_KINDS:
                findings.append(f"task-kinds value '{v}' not one of " + "|".join(TASK_KINDS))
    # strip comments FIRST (a backtick inside a comment is already gone), then ```-fenced
    # blocks (a Playbook skeleton legitimately carries <placeholder> lines), then inline spans
    no_comments = re.sub(r"<!--.*?-->", "", md_text, flags=re.S)
    no_fences = re.sub(r"(?ms)^```.*?^```\s*$", "", no_comments)
    no_code = re.sub(r"`[^`\n]*`", "", no_fences)
    for ph in re.findall(r"<[^>\n]+>", no_code):
        findings.append(f"bare <…> placeholder remains: '{ph[:40]}'")
    return findings


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
