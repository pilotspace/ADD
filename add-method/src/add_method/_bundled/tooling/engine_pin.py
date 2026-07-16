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

ENGINE_MD5 = "6f688c4162bb15e7f0e732463f1d57fd"  # re-aimed @ phase-collapse-3 (thin-engine-loop W2: PHASES collapses 6→3+done (direction·build·verify·done); legacy phase names normalize at the ONE read accessor (LEGACY_PHASES, zero task-file rewrites — check's marker-parity check normalizes too); the thin lane's direction-span freeze --cross becomes the UNIVERSAL walk (--thin now a no-op); the two retired crossings' cross-component hold + producer snapshot/consumer pin relocate into _build_entry's shared floor; guide never re-teaches a passed freeze — post-freeze direction steers to advance). prior: ee9631f9… @ thin-engine-loop W1
ENGINE_PKG_MD5 = "89a75e5dfd7665020b1ddb29a52df0d4"  # re-aimed @ phase-collapse-3 (constants.py: PHASES 6→3+done + LEGACY_PHASES read-side map + direction-span PHASE_GUIDE/OWNER/GROUPS/AGENT). prior: 265dd143… @ hygiene-bundle
