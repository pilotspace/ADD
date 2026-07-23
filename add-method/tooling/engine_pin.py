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

ENGINE_MD5 = "e226727414f44e3c66cf432e72768fb5"  # re-aimed @ fold-scenarios-tests (add.py drops §2-scenario blurbs; rule-coverage warning → §4 covers). prior: 5c769b93… @ graph-html
ENGINE_PKG_MD5 = "43b6f9dbc1acc6ee9cbe55d7b0319629"  # re-aimed @ fold-scenarios-tests (constants._FALLBACK_TASK drops ## 2 SCENARIOS, retitles ## 4 TESTS & SCENARIOS). prior: 81553881… @ remove-rule-file-mode
