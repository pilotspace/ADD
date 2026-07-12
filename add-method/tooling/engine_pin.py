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

ENGINE_MD5 = "33f46b7de23cacd5bb1febe077b87f01"  # re-aimed @ plan-phase-core v1 (expectations-first: collapse ground+contract into the plan phase; PHASES/seam/grounding/scope re-point + plan->tests freeze gate + phase-ordinal→§-number fixes: task_phases/fill/status-section, facet harvest §3, re-cross freeze, skip-rationale header). prior: 16cd7cca… @ fast-lane-boundary-line
ENGINE_PKG_MD5 = "a968f9e6713cffd9656e72c2fa5e8849"  # re-aimed @ plan-phase-core v1 (add_engine/constants.py: PHASES/PHASE_GROUPS/PHASE_OWNER/PHASE_AGENT/PHASE_GUIDE + fallback templates incl. fast §5 BUILD). prior: 710a009f… @ spec-dialect-floor
