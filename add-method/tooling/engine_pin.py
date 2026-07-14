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

ENGINE_MD5 = "9476543399d46916313f38ffb01f9142"  # re-aimed @ status-ancestor-warn (orientation-honesty: cmd_status prints a one-line stderr note + exact `init` cmd when it resolved an ANCESTOR project — a nested agent stops grepping find_root internals). prior: 9267a41f… @ help-habit-kill
ENGINE_PKG_MD5 = "955023db4358bd3f80a22078bc365361"  # re-aimed @ harness-workspace-isolation (io_state.find_root: opt-in ADD_ROOT_CEILING env bounds the upward walk so a nested workspace resolves its own project, not an ancestor). prior: fc40ad47… @ phase-merge-verify
