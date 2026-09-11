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

ENGINE_MD5 = "4aba26157052ade6b73ad7719d019928"  # re-aimed @ release-stamp: release · _anchor · _tag_tree · _tree_blobs (shared with _committed_to_head) · status tag suffix · show release lines · anchor = the newest CLOSING gate's receipt, after the last reopen, empty anchor refuses, the note names not-done members, row clamp (three T2 founds) · a cited receipt must be the member's own. prior: (consumers-go-stale) stamped_gives · _pins_of · needs_pins · stale_needs · consumers_of — nine T2 founds
# ADD 3.0 (ABF-1): the engine is a flat two-file pair (add.py + cli.py), no add_engine/ package.
# ENGINE_PKG_MD5 is repurposed to pin the dispatch entry cli.py (the second engine file).
ENGINE_PKG_MD5 = "775585d7990114d53823b706b4989e9b"  # re-aimed @ release-stamp: the release parser and dispatch. prior: a6b9eb04… @ regression-floor
