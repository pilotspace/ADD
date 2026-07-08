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

ENGINE_MD5 = "c52e9bf27d8f9b367e37832073e7a929"  # re-aimed @ persona-nudge-quiet (status nudge gated to idle). prior: 352d8bc2… @ engine-hint-context-ops
ENGINE_PKG_MD5 = "d3bb5326feacf06f54ecd338d5be2413"  # re-aimed @ never-defer-invariants (guidelines block binds PROJECT.md invariants). prior: a00e1d36… @ verify-flow-value
