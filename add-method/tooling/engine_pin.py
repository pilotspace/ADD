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

ENGINE_MD5 = "bbbb9a9fbcdc0bb3f7e63e8f3990b306"  # re-aimed @ first-call-ergonomics v1 (contract_frozen threaded through _next_command so freeze footer/status/guide name advance post-freeze; freeze/lock/advance-at-done exact retries are exit-0 no-ops; init prints a kickoff hand-off). prior: 10ffdf96… @ status-guide-fold v1
ENGINE_PKG_MD5 = "b287ceedad9e29013a798b8faa978605"  # re-aimed @ fast-lane-skips v1 (add_engine/constants.py: _SKIPPABLE_PHASES; add_engine/predicates.py: _skip_lane_eligible/_skip_set_allowed). prior: 9e9eb184… @ ai-plan-verify-gate v2
