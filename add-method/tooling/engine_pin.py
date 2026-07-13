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

ENGINE_MD5 = "b27ce845f42aa832b1338c4881f9cb27"  # re-aimed @ phase-merge-specify (six-phase-loop 1/6: scenarios PHASE merged into specify — legacy state token + retired skips: token both tolerated; sections untouched). prior: 26f78f04… @ compound-ticks 
ENGINE_PKG_MD5 = "870a4ce0603599ca359302910df01614"  # re-aimed @ phase-merge-specify (constants.py: PHASES drops scenarios; _SKIPPABLE_PHASES=(observe,); PHASE_GUIDE/OWNER/GROUPS/AGENT follow). prior: d83fc67f… @ kickoff-truth v2 
