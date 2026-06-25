#!/usr/bin/env python3
"""add_engine.io_state — low-level IO + state primitives for the ADD engine.

The 4 atomic-write primitives (designed for failure: temp-then-rename, no silent
clobber, all-or-nothing for the many-writer). Extracted from add.py (engine-
modularization 2/N); add.py re-exports them as module globals so callers and
monkeypatch sites (`add._atomic_write = spy`) keep resolving unchanged.
"""
from __future__ import annotations

import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path


# --- low-level IO (designed for failure: atomic, no silent clobber) ----------

def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _atomic_write(path: Path, text: str) -> None:
    """Write via a temp file in the same dir, then atomically replace.

    Avoids a half-written file if the process dies mid-write.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            fh.write(text)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _atomic_write_bytes(path: Path, data: bytes) -> None:
    """Binary sibling of `_atomic_write` — lands `data` UNCHANGED (no newline translation), so a
    byte-for-byte copy stays exact. Same temp-then-replace crash-safety."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def _atomic_write_many(writes: list[tuple[Path, str]]) -> None:
    """True all-or-nothing commit across N files — design-for-failure for a multi-file write.

    Phase 1 STAGES every (path, text) to a sibling `.tmp`, flushing + fsync-ing each, so the
    realistic IO failures (disk full, permission denied) surface HERE, before any target changes —
    and on any stage failure every staged temp is removed, so NOTHING is committed. Phase 2 then
    COMMITS each file by renaming any existing target ASIDE to a sibling `.bak`, then `os.replace`-ing
    the staged `.tmp` into place. If ANY commit rename raises, every file already committed is rolled
    back IN REVERSE (remove the landed new file, rename its `.bak` back, or leave it absent) and the
    original error re-raised — so the whole set is all-or-nothing: either every file holds its new
    text, or every file holds its prior content. Restoring is an atomic rename of an already-written
    `.bak` (no content held in memory, no re-write), the cheapest recovery under failing IO. Leftover
    `.tmp`/`.bak` siblings are removed on every exit path.
    """
    staged: list[tuple[str, Path]] = []
    committed: list[list] = []                    # [path, bak_or_None, new_landed] per committed file
    try:
        for path, text in writes:                 # phase 1: stage every temp (fsync'd before any commit)
            path.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=str(path.parent), suffix=".tmp")
            staged.append((tmp, path))            # track BEFORE write so a write/fsync failure still cleans it
            with os.fdopen(fd, "w", encoding="utf-8") as fh:
                fh.write(text)
                fh.flush()
                os.fsync(fh.fileno())
        try:
            for tmp, path in staged:              # phase 2: commit via rename-aside
                bak = None
                existed = path.exists()
                if existed:
                    fd2, bak = tempfile.mkstemp(dir=str(path.parent), suffix=".bak")
                    os.close(fd2)
                committed.append([path, bak, False])   # track .bak NOW so cleanup never leaks it
                if existed:
                    os.replace(path, bak)         # move the existing target aside
                os.replace(tmp, path)             # move the new file in
                committed[-1][2] = True
        except OSError:
            for path, bak, landed in reversed(committed):   # roll back, newest-first
                try:
                    if landed and path.exists():
                        os.unlink(path)           # drop the new file we put in
                    if bak is not None and not path.exists():
                        os.replace(bak, path)     # restore the prior target (atomic rename)
                except OSError:
                    pass                          # best-effort restore under already-failing IO
            raise
    finally:
        for tmp, _ in staged:                     # leftover .tmp (failed/aborted stage) never persists
            if os.path.exists(tmp):
                os.unlink(tmp)
        for path, bak, landed in committed:       # leftover .bak (success, or orphaned post-rollback)
            if bak is not None and os.path.exists(bak):
                os.unlink(bak)
