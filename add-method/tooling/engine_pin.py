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

ENGINE_MD5 = "dd612bc46b51b85485ff12c1edc3bd89"  # re-aimed @ guided-upgrade W5 (`upgrade` archives a 2.x bundle whole, inits 3.0, writes MIGRATION.md in the archive — nothing deleted, nothing translated). prior: a50e4b42… @ routing-index-freshness W4
# ADD 3.0 (ABF-1): the engine is a flat two-file pair (add.py + cli.py), no add_engine/ package.
# ENGINE_PKG_MD5 is repurposed to pin the dispatch entry cli.py (the second engine file).
ENGINE_PKG_MD5 = "b4a7249845259f3fbcf8e1dae013b03c"  # re-aimed @ guided-upgrade W5 (upgrade subparser + dispatch; operates on the project root, not the bundle). prior: 3d21a9c2… @ brief-gate W1
