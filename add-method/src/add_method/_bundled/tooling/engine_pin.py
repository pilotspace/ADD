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

ENGINE_MD5 = "147820fde5c6806d7360a43e81f7af5b"  # re-aimed @ status-guide-fold v1 (_next_command single composer feeds guide/status/footer + setup exact-flag commands; contract->freeze --by; docstring de-slanged). prior: 6bb86306… @ advance-chain-collapse v1
ENGINE_PKG_MD5 = "5f60c0b2af321c1dcb053a5a06473a92"  # re-aimed @ fast-lane-skips v1 (add_engine/constants.py: _SKIPPABLE_PHASES; add_engine/predicates.py: _skip_lane_eligible/_skip_set_allowed). prior: 9e9eb184… @ ai-plan-verify-gate v2
