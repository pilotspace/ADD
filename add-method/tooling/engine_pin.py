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

ENGINE_MD5 = "0d98f6934351c7c1d60b9b4cf06c4d18"  # re-aimed @ atomic-node (ONE atomic PLAN.md template; --fast/--oneshot/--thin/--full lane scaffolds retired; AI-verify block template-borne; Regression-floor + multi-agent Advisor seams; Build-expectations block + opt-in gate retired; + neighborhood-status card). prior: abac501b… @ route-scoreboard
ENGINE_PKG_MD5 = "ec7f8093d556a5e00b25353005b018b0"  # re-aimed @ atomic-node (constants drops _FAST_SECTIONS — the lane scaffolds retired with the fat template blocks; _section_unfilled serves contract-fill only). prior: 557f500f… @ book-stops-shipping
