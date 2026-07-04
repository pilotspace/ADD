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

ENGINE_MD5 = "cd5a00c16b88e8723758b26210063370"  # re-aimed @ strip-scaffold-backtick-comment-fix (_strip_live_scaffold's fence-split regex gains a narrow `` `<!--...-->` `` alternative, protecting an inline backtick-quoted literal comment example in prose without fragmenting a real live comment that merely contains unrelated backtick-quoted code). prior: 976d6568… @ persona-seed-nudge v2
ENGINE_PKG_MD5 = "f38b20063c8ce9300821b2c9c51ed104"  # re-aimed @ persona-seed-nudge v2 (add_engine/constants.py gains the single-sourced PERSONA_HINT constant referenced by all three call sites). prior: d35035d4… @ persona-seed-nudge v1
