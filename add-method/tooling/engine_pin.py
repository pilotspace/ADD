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

ENGINE_MD5 = "07750e20aa7a09f7403f9ea375ab48dc"  # re-aimed @ migrate-verb (ADD 2.0 M6a: task doc TASK.md → PLAN.md engine-wide + new one-shot `migrate` verb, 30→31). prior: 46b3057d… @ engine-kernel-trim
ENGINE_PKG_MD5 = "0c8b1abadfed44b273298b1c65e19d09"  # re-aimed @ migrate-verb (ADD 2.0 M6a: the TASK.md → PLAN.md rename ripples through the package's doc-path literals). prior: 1f2abc63… @ engine-kernel-trim
