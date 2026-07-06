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

ENGINE_MD5 = "27cbc59759eb94385dada8f43bea3b85"  # re-aimed @ worktree-prep (new cmd_worktree_prep: cut a worker worktree at HEAD, materialize gitignored .add/tooling+.add/docs, echo the fork base; workspace-only, no state write). prior: 1c647fed… @ archived-delta-verbs
ENGINE_PKG_MD5 = "a59f79d0fdc40553838e0a6449050d12"  # re-aimed @ fastlane-ground-lite (_FALLBACK_TASK_FAST §0 gains the Ground SHA drift-anchor line, matching the fast template). prior: e14b7d38… @ persona-fit-nudge
