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

ENGINE_MD5 = "5948731aa3c961bb374e5624599395d1"  # re-aimed @ fastlane-intake-nudge (cmd_new_task gains the advisory `_fastlane_nudge` print, non-fast path only). prior: cf97f937… @ persona-fit-nudge
ENGINE_PKG_MD5 = "e14b7d383587bf27a61087d423ba0c89"  # re-aimed @ persona-fit-nudge (constants.py gains PERSONA_FIT_HINT_TEMPLATE; io_state.py gains _real_persona_slugs). prior: f38b2006… @ persona-seed-nudge v2
