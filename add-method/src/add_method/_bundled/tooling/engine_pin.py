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

ENGINE_MD5 = "bfd472014a1f3bdcb76c0a7f103fc44b"  # re-aimed @ run-mode-decouple (run mode = the autonomy dial only; the streams: posture coupling is removed — --run-mode no longer writes a streams line, status drops its `run mode:` row, concurrency is now 'spawn a subagent per task'). prior: 427a2501… @ graph-views
ENGINE_PKG_MD5 = "8f3d546ad34f44309d6bb5dc9dfdf6c7"  # re-aimed @ advisor-split (add_engine guidelines.py roster citation -> add-worker+add-advisor two-agent block; constants.py PHASE_AGENT values add->add-worker). prior: e0ff925d… @ run-mode-decouple
