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

ENGINE_MD5 = "d8fb245ea769ff834a03ba8c1932be72"  # re-aimed @ round-visible-runs (verify->build return trips recorded as uncapped rounds; phase --note refusal exit 2, verbatim note; status round N; trace rounds). prior: 1cebca7e… @ persona-skill
ENGINE_PKG_MD5 = "bcc35aa23727c5ecb19b9f3e3a53d348"  # re-aimed @ persona-skill (constants SETUP_FILES drops personas/_template.md; PERSONA_HINT/FIT point at the persona-author skill; io_state comment). prior: 8f3d546a… @ advisor-split
