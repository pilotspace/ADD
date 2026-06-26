"""add_engine.render — terminal-render primitives (engine-modularization 9/N).

Progress bars, the phase track, ASCII/Unicode + color tiers, clip/wrap. A closed,
unpatched cluster (transitive-closure AST = zero outbound calls). The render-private
_ANSI palette lives here; the SHARED _DEFAULT_WIDTH is imported from constants (its
single source — the staying report default-args use it too).
"""
from __future__ import annotations

import os
import re
import shutil
import sys

from add_engine.constants import PHASES, _DEFAULT_WIDTH

_ANSI = {"green": "\x1b[32m", "yellow": "\x1b[33m", "red": "\x1b[31m",
         "dim": "\x1b[2m", "reset": "\x1b[0m"}


def _bar(num: int, den: int, cells: int, g: dict) -> str:
    """A progress bar; 0/0 -> all-empty (no divide-by-zero)."""
    filled = 0 if den <= 0 else round(num / den * cells)
    filled = max(0, min(cells, filled))
    return g["reached"] * filled + g["pending"] * (cells - filled)

def _phase_track(phase: str, g: dict) -> str:
    """Compact 9-cell pipeline (no labels — a single legend explains it):
    reached · current · pending. A done task -> all reached."""
    try:
        ci = PHASES.index(phase)
    except ValueError:
        ci = 0
    cells = []
    for i in range(len(PHASES)):
        if phase == "done" or i < ci:
            cells.append(g["reached"])
        elif i == ci:
            cells.append(g["current"])
        else:
            cells.append(g["pending"])
    return "".join(cells)

def _use_ascii() -> bool:
    """ASCII tier when the terminal can't render Unicode (non-UTF-8 / dumb)."""
    enc = (getattr(sys.stdout, "encoding", "") or "").lower()
    return ("utf" not in enc) or (os.environ.get("TERM") == "dumb")

def _color_enabled() -> bool:
    """Color only on an interactive tty, honoring NO_COLOR and TERM."""
    return (sys.stdout.isatty() and not os.environ.get("NO_COLOR")
            and os.environ.get("TERM", "") not in ("dumb", ""))

def _term_width() -> int:
    try:
        import shutil
        return min(max(shutil.get_terminal_size().columns, 64), 100)
    except Exception:
        return _DEFAULT_WIDTH

def _colorize(s: str) -> str:
    """Apply ANSI to status tokens — redundant to the text, never the sole signal.
    Applied ONLY to tty stdout; the persisted RETRO.md string stays plain."""
    c = _ANSI
    s = re.sub(r"\bDONE\b", c["green"] + "DONE" + c["reset"], s)
    s = re.sub(r"\bBLOCKED\b", c["red"] + "BLOCKED" + c["reset"], s)
    s = re.sub(r"\bPASS\b", c["green"] + "PASS" + c["reset"], s)
    s = re.sub(r"\bRISK\b", c["yellow"] + "RISK" + c["reset"], s)
    s = re.sub(r"\bSTOP\b", c["red"] + "STOP" + c["reset"], s)
    return s

def _clip(s: str, maxlen: int) -> str:
    """Trim a string to fit a fixed-width frame, ellipsizing if it overruns."""
    return s if len(s) <= maxlen else s[:maxlen - 1].rstrip() + "…"

def _wrap(text: str, width: int, label: str) -> list[str]:
    """Wrap `text` to `width`; the first line carries `label`, continuations are
    blank-indented to the same width (so a multi-line goal shows 'goal' once)."""
    cont = " " * len(label)
    lines, cur = [], ""
    for w in text.split():
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    lines = lines or ["(unknown)"]
    return [(label if i == 0 else cont) + ln for i, ln in enumerate(lines)]
