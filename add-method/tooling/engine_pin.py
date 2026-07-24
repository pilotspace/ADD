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
prose (its PLAN.md) is the place to record the full rationale for a re-aim —
this file only ever holds the newest pointer.
"""

ENGINE_MD5 = "60eef504c87d5ed39d58a8722401f5aa"  # re-aimed @ egg-info-prune (suffix-prune *.egg-info dirs from the scope walk). prior: 946b76cf… @ scope-walk-prune
ENGINE_PKG_MD5 = "3d7ec2b90d11b91fd0211b1fc61b4c19"  # re-aimed @ fold-residue-engine-guide (PHASE_GUIDE["direction"] stops instructing a retired §2; the one-case-per-rule duty folds into the §4 clause). prior: 96f41126… @ claude-md-block-finalize
