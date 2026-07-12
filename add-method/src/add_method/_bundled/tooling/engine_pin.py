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

ENGINE_MD5 = "07659b10a8a7bc8b1d45c7009c107d17"  # re-aimed @ plan-phase-core v1 (expectations-first: collapse ground+contract into the plan phase; PHASES/seam/grounding/scope re-point + plan->tests freeze gate). prior: 16cd7cca… @ fast-lane-boundary-line
ENGINE_PKG_MD5 = "45e288b049b34fde3a967257fd3f0fff"  # re-aimed @ plan-phase-core v1 (add_engine/constants.py: PHASES/PHASE_GROUPS/PHASE_OWNER/PHASE_AGENT/PHASE_GUIDE + fallback templates). prior: 710a009f… @ spec-dialect-floor
