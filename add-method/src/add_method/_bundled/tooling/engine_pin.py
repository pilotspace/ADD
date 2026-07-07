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

ENGINE_MD5 = "35e7f7014ebb184ffcc4859e1ade1634"  # re-aimed @ facet-adr-harvest (_facets loop in _stamp_adr_record — per-facet [AI] build ADR lines). prior: 78baf42b… @ persona-schema-hardening
ENGINE_PKG_MD5 = "c29c2e05e429948813c2b0ba0d325da8"  # re-aimed @ persona-schema-hardening (_persona_quality_warnings + PERSONA_FLOW_VALUES). prior: a59f79d0… @ fastlane-ground-lite
