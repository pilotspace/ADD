"""token_anatomy — attribute a run transcript's cache-read cost to categories
(token-anatomy milestone, anatomy-core TASK.md §3 CONTRACT @ v1).

The honest-fidelity benchmark showed ADD costs ~3.6x spec-kit, and the token
anatomy traced ~98% of that to cache-reads of carried context (output is
negligible). This attributor splits the cost by WHAT is being carried —
method-doc reads, engine (`add.py`) output, build-work IO, or plain conversation
— by residency-weighting each message (`size x #later turns it stays resident`),
so ceremony optimization targets the real drivers with data, not guesses.

Reads transcripts only — no `add-method/` engine dependency. Stdlib, fail-loud
on a missing transcript (BenchError), fault-tolerant on malformed lines.
"""
from __future__ import annotations

import json
import pathlib

from benchmark.schema.run_record import BenchError

_CATS = ("method_doc", "engine_output", "build_work", "conversation")

# a Read/Grep/Glob whose target name contains one of these is a method-doc surface
_METHOD_PATHS = ("PROJECT.md", "SOUL.md", "TASK.md", "MILESTONE.md",
                 "CLAUDE.md", "SKILL.md", "/.add/docs/", "/docs/")


def _est_size(text: str) -> int:
    """Stdlib token heuristic (no tokenizer dep): ~4 chars/token."""
    return len(text) // 4


def _message_text(msg: dict) -> str:
    """The renderable text of one transcript message — the bytes that sit in the
    KV-cache: tool_use inputs + tool_result contents + assistant thinking/text."""
    m = msg.get("message", msg)
    content = m.get("content") if isinstance(m, dict) else None
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return ""
    parts: list[str] = []
    for block in content:
        if not isinstance(block, dict):
            continue
        bt = block.get("type")
        if bt == "tool_result":
            c = block.get("content", "")
            parts.append(c if isinstance(c, str) else json.dumps(c))
        elif bt == "tool_use":
            parts.append(json.dumps(block.get("input", {})))
        elif bt in ("thinking", "text"):
            parts.append(block.get(bt, ""))
    return "".join(parts)


def _categorize(msg: dict, tool_use_by_id: dict) -> str:
    """M4 — tool-aware category. A tool_result is classed by the tool_use that
    made it (matched on tool_use_id); everything else is conversation."""
    m = msg.get("message", msg)
    content = m.get("content") if isinstance(m, dict) else None
    if not isinstance(content, list):
        return "conversation"
    for block in content:
        if isinstance(block, dict) and block.get("type") == "tool_result":
            tu = tool_use_by_id.get(block.get("tool_use_id"))
            return _classify_tool_use(tu) if tu else "build_work"
    return "conversation"


def _classify_tool_use(tu: dict) -> str:
    name = tu.get("name", "")
    inp = tu.get("input", {}) or {}
    if name in ("Read", "Grep", "Glob"):
        target = str(inp.get("file_path") or inp.get("path") or inp.get("pattern") or "")
        if any(mp in target for mp in _METHOD_PATHS):
            return "method_doc"
        return "build_work"
    if name == "Bash" and "add.py" in str(inp.get("command", "")):
        return "engine_output"
    return "build_work"


def _parse_lines(path: pathlib.Path) -> list[dict]:
    out: list[dict] = []
    for line in path.read_text(errors="replace").splitlines():
        line = line.strip()
        if not line or line[0] != "{":
            continue
        try:
            out.append(json.loads(line))
        except ValueError:
            continue  # M3: skip malformed lines, never raise mid-parse
    return out


def token_anatomy(transcript_path: str | pathlib.Path) -> dict:
    """Attribute the transcript's cache-read tokens to `_CATS`. See module doc.

    Returns {categories, total_cache_read, turns, attributed_pct, residual_pct}.
    Deterministic; a no-usage transcript yields all-zeros; a missing path raises
    BenchError("anatomy_no_transcript: ...")."""
    path = pathlib.Path(transcript_path)
    if not path.exists():
        raise BenchError(f"anatomy_no_transcript: {path}")

    messages = _parse_lines(path)

    # forward pass: id -> tool_use (assistant tool_use precedes its user tool_result)
    tool_use_by_id: dict = {}
    # indices of assistant turns that carry a usage.cache_read (the billed turns)
    assistant_turn_idx: list[int] = []
    total_cache_read = 0
    for i, msg in enumerate(messages):
        m = msg.get("message", msg)
        if msg.get("type") == "assistant":
            for block in (m.get("content") or []):
                if isinstance(block, dict) and block.get("type") == "tool_use":
                    tool_use_by_id[block.get("id")] = block
            usage = m.get("usage") if isinstance(m, dict) else None
            if isinstance(usage, dict) and "cache_read_input_tokens" in usage:
                assistant_turn_idx.append(i)
                total_cache_read += int(usage.get("cache_read_input_tokens", 0) or 0)

    turns = len(assistant_turn_idx)
    weights = {c: 0 for c in _CATS}
    if turns and total_cache_read:
        # residency weight: a message resident from index i is re-read by every
        # assistant turn strictly after i.
        for i, msg in enumerate(messages):
            size = _est_size(_message_text(msg))
            if not size:
                continue
            resident_turns = sum(1 for ti in assistant_turn_idx if ti > i)
            if resident_turns:
                weights[_categorize(msg, tool_use_by_id)] += size * resident_turns

    total_weight = sum(weights.values())
    if total_weight:
        categories = {c: round(total_cache_read * weights[c] / total_weight) for c in _CATS}
    else:
        categories = {c: 0 for c in _CATS}

    attributed = sum(weights[c] for c in ("method_doc", "engine_output", "build_work", "conversation"))
    attributed_pct = (attributed / total_weight) if total_weight else 0.0
    return {
        "categories": categories,
        "total_cache_read": total_cache_read,
        "turns": turns,
        "attributed_pct": attributed_pct,
        "residual_pct": 1.0 - attributed_pct,
    }
