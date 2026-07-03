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

ENGINE_MD5 = "3d7496bb5c4347707dae5718612e2b80"  # re-aimed @ roster-install-drift (direct chat-directed edit, human present live — cmd_check gains roster_uninstalled: a project whose guideline files cite the agent roster but has no `.claude/agents/add-*.md` installed, WARN-only, measure-not-block; comment corrected post-revert to not imply `.claude/agents/*.md` is the shipped citation). prior: 568381a3… @ report-rendered-trace
ENGINE_PKG_MD5 = "a66975e2b5ed53b5858c3bd43dde7828"  # reverted to @ roster-onboarding-wiring (the roster-install-drift attempt to cite `.claude/agents/*.md` in _guideline_block() broke the FROZEN test_roster_portable.py contract — that path is a Claude-only mechanism leaking into the shared AGENTS.md/.clinerules block; reverted the prose to `add-method/agents/*.md` since the real fix, packaging + installer materialization + the roster_uninstalled lint, does not depend on this citation string). prior: f26fc329… @ roster-install-drift (superseded, same session, never committed)
