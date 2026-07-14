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

ENGINE_MD5 = "c0c972e2ace3e8434906e2b480191da5"  # re-aimed @ status-orientation-diet (call-residuals: cmd_status plain view leads with a "now" resume glance card — active slug · phase · next verb · TASK.md path — reusing _next_footer, so a single status read orients without the measured 3-4x/rep re-reads). prior: 3b438d30… @ scope-first-draft
ENGINE_PKG_MD5 = "fc40ad47544db6f5204b6197b95daf04"  # re-aimed @ phase-merge-verify (constants.py: PHASES drops observe; _SKIPPABLE_PHASES=(); PHASE_GUIDE/OWNER/GROUPS/AGENT follow). prior: 870a4ce0… @ phase-merge-specify 
