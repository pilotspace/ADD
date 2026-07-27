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

ENGINE_MD5 = "e39496922e519202994cecc6c95c3689"  # re-aimed @ invariant-inherit (new-task prints the transitive invariants it inherits — a view, no new store). prior: 108469eb… @ invariants-publish
ENGINE_PKG_MD5 = "c635ca53a41360940620f081bf5b329d"  # re-aimed @ seed-method-personas (METHOD_PERSONAS lands in add_engine.constants). prior: 3d7ec2b9… @ fold-residue-engine-guide
