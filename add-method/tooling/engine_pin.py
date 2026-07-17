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

ENGINE_MD5 = "ec9a57303adce545a2a2ba64329747c2"  # re-aimed @ persona-routes-depth (thin-engine-loop W5: _ROUTE_LINE_RE/_route_record — freeze records the persona-proposed lane; audit gains route_unrecorded/route_lane_mismatch, grandfathered). prior: 34990170… @ skill-loop-fold
ENGINE_PKG_MD5 = "ed7bf3e1c9e6e7fdf53833dc2914c290"  # re-aimed @ template-unify (constants.py: _FAST_SECTIONS replaces _FALLBACK_TASK_FAST; _FALLBACK_TASK gains Ground SHA). prior: 89a75e5d… @ phase-collapse-3
