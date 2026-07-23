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

ENGINE_MD5 = "946b76cf263aed3fb4cdff7e7a9ec899"  # re-aimed @ scope-walk-prune (.venv/venv/.tox/.mypy_cache/.ruff_cache/.eggs pruned from the scope walk + self-explaining default warn). prior: 68109d80… @ scope-first-freeze
ENGINE_PKG_MD5 = "96f41126af98221befda9012d21b450b"  # re-aimed @ claude-md-block-finalize (guidelines._guideline_block: thin-index step 2, tightened flow/roster, portable agents/*.md). prior: fd36bb5e… @ migrate-specs-pointers
