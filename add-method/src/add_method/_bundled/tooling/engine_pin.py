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

ENGINE_MD5 = "46b3057d70bd15304659a63ceabb8ac4"  # re-aimed @ engine-kernel-trim (ADD 2.0 M5: 54→30 verbs — the platform pillars (streams/waves/DAG · components/federation · release/graduation · audit · fold/compact · team verbs · SPEC-delta trio · doctor/worktree-prep) died; add.py 9,558→6,596 lines; their playbooks live in the seed personas). prior: 11fe18db… @ specs-5dd
ENGINE_PKG_MD5 = "1f2abc63c0aced8aa8cf47b87d7b2044"  # re-aimed @ engine-kernel-trim (ADD 2.0 M5: release.py deleted; components.py slimmed to the two generic scope utilities; constants.py drops the graduation/release cues). prior: cd2d7e81… @ specs-5dd
