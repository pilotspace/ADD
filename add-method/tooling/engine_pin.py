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

ENGINE_MD5 = "26d1db26d19e9330cdff0d6d0cdd747d"  # re-aimed @ persona-task-kinds (ADD 2.0 M1: _TASK_KIND_RE/_task_kind header reader + _append_route_trace — every gate outcome appends a route-outcome JSONL trace, the persona scoreboard's evidence stream). prior: ec9a5730… @ persona-routes-depth
ENGINE_PKG_MD5 = "991ce1315c39abb7404f954826ee1d95"  # re-aimed @ persona-task-kinds (constants.py gains TASK_KINDS closed taxonomy; predicates.py _persona_quality_warnings gains Finding C — task-kinds outside the taxonomy is a named WARN). prior: ed7bf3e1… @ template-unify
