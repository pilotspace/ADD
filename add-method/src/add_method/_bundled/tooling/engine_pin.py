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

ENGINE_MD5 = "7e6ebec010c066734818faf6599a2571"  # re-aimed @ plan-in-report (plan-legibility: decide_data/render_decide gain a `plan` key + BUILD PLAN block surfacing the §3 build-strategy plan-of-action at the freeze; _build_plan single-line extractor — no field bleed; milestone --json payload +plan:[]). prior: 33f46b7d… @ plan-phase-core v1
ENGINE_PKG_MD5 = "28212a55d53a354dc1b57ab4cddeb243"  # re-aimed @ guides-and-skill (add_engine/constants.py: PHASE_GUIDE["plan"] chapter 05-step-3-contract.md → 05-step-3-plan.md, following the book-chapter rename cascade). prior: a968f9e6… @ plan-phase-core v1
