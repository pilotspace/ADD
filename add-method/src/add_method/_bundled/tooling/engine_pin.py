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

ENGINE_MD5 = "4230eb2ef4f27fb9f480781fee92e5a5"  # re-aimed @ verify-traceability-glint (_guarantee_lint_notices/cmd_audit gain rule_coverage_gap — this task's own §1 Must/Reject-vs-§2/§4 tag gap, surfaced at verify via `add.py audit`, not only a separate `check` sweep). prior: a8ab76ae… @ status-pagination
ENGINE_PKG_MD5 = "a66975e2b5ed53b5858c3bd43dde7828"  # re-aimed @ roster-onboarding-wiring (constants.py GUIDELINE_FILES + guidelines.py _INIT_EXCLUDE/docstring gained .clinerules; no other add_engine/*.py changed). prior: 82297e49… @ roster-portable-shape
