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

ENGINE_MD5 = "11fe18dbbd8534a7be246693639131c5"  # re-aimed @ specs-5dd (ADD 2.0 M3: init seeds the five living 5-DD specs under .add/specs/ (ONE templates/specs/SPEC.md.tmpl, five renders, never-clobber) + the `delta-append <dd>` kernel verb — newest-first [open · date] line under ## Deltas, active-task stamp, delta_dd_unknown pre-write refusal, on-demand legacy seeding). prior: 9cc73f6e… @ plan-target
ENGINE_PKG_MD5 = "cd2d7e81ce3ac0b9fb16c29d3caecc5a"  # re-aimed @ specs-5dd (ADD 2.0 M3: constants.py gains SPEC_DDS — the closed dd -> (file, title, lens) map for the five living specs). prior: d82eeae0… @ roster-distill
