"""engine_pin — single-source ENGINE_MD5 pin.

One constant, one home. The five prose-only suites import this value instead
of each carrying a duplicate hard-coded literal. When the engine legitimately
changes, re-aim this one line and the entire tooling suite re-anchors.

The pin is a hard-coded literal — never computed at runtime. A pin that
recomputes its own value from the file it is supposed to guard is vacuous:
it can never detect drift. The literal was recorded at the commit that first
introduced it and is updated only by a deliberate, human-approved task.

Trim policy: each annotation carries only the CURRENT re-aim plus a one-line
`prior: <hash>… @ <task>` pointer to the immediately-preceding re-aim — never
a deeper chain. `git log -p` on this file is the real, complete audit trail;
the comment is a quick-glance anchor, not an append-only ledger. A task's own
prose (its TASK.md) is the place to record the full rationale for a re-aim —
this file only ever holds the newest pointer.
"""

ENGINE_MD5 = "16cd7cca2754c31ae0ff147b14839bee"  # re-aimed @ fast-lane-boundary-line v1 (cmd_freeze boundary_unfilled guard after unflagged_freeze). prior: 7f96609e… @ spec-dialect-floor
ENGINE_PKG_MD5 = "710a009fd35e945f0d0143bcd59ee05c"  # re-aimed @ spec-dialect-floor v1 (add_engine/constants.py: _DIALECT_CLASSES registry). prior: 5f60c0b2… @ fast-lane-skips v1
