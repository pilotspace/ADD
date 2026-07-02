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

ENGINE_MD5 = "a8ab76ae6ec1b7f525d2df1967242ee6"  # re-aimed @ status-pagination (cmd_status's milestones:/tasks[] lists now sort by `updated` desc + cap to 10 by default; new --all flag + JSON milestones_total/tasks_total fields). prior: ff7d9971… @ status-task-filter
ENGINE_PKG_MD5 = "a66975e2b5ed53b5858c3bd43dde7828"  # re-aimed @ roster-onboarding-wiring (constants.py GUIDELINE_FILES + guidelines.py _INIT_EXCLUDE/docstring gained .clinerules; no other add_engine/*.py changed). prior: 82297e49… @ roster-portable-shape
