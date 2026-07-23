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

ENGINE_MD5 = "8001ed1664506900cbb45fb4cb3e87df"  # re-aimed @ claude-md-minimal (add.py status context line → read-first foundation + .add/specs/ pointer). prior: e2267274… @ fold-scenarios-tests
ENGINE_PKG_MD5 = "b80004dfce6be148f37cc98c1f0c727e"  # re-aimed @ claude-md-minimal (guidelines._guideline_block minimized: specs/ pointer, Tests & Scenarios bundle, tightened roster). prior: 43b6f9db… @ fold-scenarios-tests
