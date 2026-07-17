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

ENGINE_MD5 = "9433f6e36d72cf101d04150a596eb686"  # re-aimed @ roster-distill (ADD 2.0 M1: roster_uninstalled lint follows the ONE add agent — cites agents/add.md, globs add*.md). prior: 26d1db26… @ persona-task-kinds
ENGINE_PKG_MD5 = "d82eeae040e30f0f70511555205c5f9b"  # re-aimed @ roster-distill (ADD 2.0 M1: PHASE_AGENT all-phases -> the ONE "add" agent; PERSONA_HINT/PERSONA_FIT_HINT reworded to "add agent, persona mode"; guidelines.py roster block -> 1-agent + modes). prior: 991ce131… @ persona-task-kinds
