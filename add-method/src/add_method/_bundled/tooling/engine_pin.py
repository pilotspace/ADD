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

ENGINE_MD5 = "26f78f0480771939d4604d21f62546f6"  # re-aimed @ compound-ticks (call-floor 4/5: opt-in freeze --cross lands a plan freeze in tests; a completing gate at build auto-crosses to verify; the new-task recipe advertises the compressed lane). prior: 6f4e791f… @ scope-coverage-hint 
ENGINE_PKG_MD5 = "d83fc67fc7979adde37358a29d5e3f46"  # re-aimed @ kickoff-truth v2 (io_state.py: _die gains the dup-failure short-circuit — _register_invocation/_clear_last_fail/_dup_fail_hint; the sig sidecar lives in the OS tmp dir keyed by md5(root), NEVER in the .add tree — the reject-writes-nothing floor; constants.py untouched at v2). prior: 28212a55… @ guides-and-skill
