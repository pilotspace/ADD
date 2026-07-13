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

ENGINE_MD5 = "bf89b03351ae87d72fb3a2dc5f5729af"  # re-aimed @ build-entry-spec-echo (six-phase-loop 6/6: _spec_echo pure-read helper + fail-open tail call in _build_entry — the tick INTO build re-renders §1 Must/Reject + the §3 contract head). prior: 5d5e0538… @ phase-merge-verify 
ENGINE_PKG_MD5 = "fc40ad47544db6f5204b6197b95daf04"  # re-aimed @ phase-merge-verify (constants.py: PHASES drops observe; _SKIPPABLE_PHASES=(); PHASE_GUIDE/OWNER/GROUPS/AGENT follow). prior: 870a4ce0… @ phase-merge-specify 
