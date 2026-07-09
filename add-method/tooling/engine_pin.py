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

ENGINE_MD5 = "54029cedd869eab4c6e0a9435b6da2ea"  # re-aimed @ ai-plan-verify-gate v2 (cmd_freeze: skip the generic "?" guard on --ai-plan-verify so a malformed sensitivity routes to ai_freeze_unknown_sensitivity, not sensitivity_invalid). prior: 4b61de4f… @ ai-plan-verify-gate v1
ENGINE_PKG_MD5 = "9e9eb184c76bf657963eef9df9d7a5ee"  # unchanged @ ai-plan-verify-gate v2 (only add.py changed this round; add_engine/*.py untouched). prior: 9883ce72… @ phase-bundles
