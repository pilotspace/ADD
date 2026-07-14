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

ENGINE_MD5 = "a88bc24c7f1171f3e373c15fb1bf40ac"  # re-aimed @ orient-map (orientation-honesty: bare add.py + --help LEAD with a concise flow map (status/init/new-task/advance/freeze/gate) then the full list — kills the 1/rep initial --help orientation dump). prior: 9476543399… @ status-ancestor-warn
ENGINE_PKG_MD5 = "955023db4358bd3f80a22078bc365361"  # re-aimed @ harness-workspace-isolation (io_state.find_root: opt-in ADD_ROOT_CEILING env bounds the upward walk so a nested workspace resolves its own project, not an ancestor). prior: fc40ad47… @ phase-merge-verify
