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

ENGINE_MD5 = "a773d868899bb5dc2b162fc6a4bef8d6"  # re-aimed @ status-lean-default (engine-minimalism: bare `status` gates goal/m-goal prose + personas roster + milestone/task rows + per-stream detail behind --all — count/pointer lines instead). prior: 1dd8c1b1… @ help-diet
ENGINE_PKG_MD5 = "265dd143fd850317c66ffb3ad021c98d"  # re-aimed @ hygiene-bundle (engine-hygiene: taskdoc._HEADING_RE — static §-heading regex hoisted to module load). prior: 955023db… @ harness-workspace-isolation
