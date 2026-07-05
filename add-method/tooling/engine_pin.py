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

ENGINE_MD5 = "1f04d22460462c165bf3c72260ef4e85"  # re-aimed @ fold-glossary-deltas verify (widened `_TASK_ATTR_LINE_RE`'s character class to include `-`/`'`/digits: the real corpus routinely follows `Glossary deltas:` with a hyphenated freeze-time label — e.g. "Least-sure flag surfaced at freeze:" — which the narrower class failed to recognize as a continuation stop, silently over-joining that unrelated field into the glossary candidate; confirmed against the live task corpus, not just synthetic fixtures). prior: 89f9eeed… @ fold-glossary-deltas (build)
ENGINE_PKG_MD5 = "f38b20063c8ce9300821b2c9c51ed104"  # re-aimed @ persona-seed-nudge v2 (add_engine/constants.py gains the single-sourced PERSONA_HINT constant referenced by all three call sites). prior: d35035d4… @ persona-seed-nudge v1
