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

ENGINE_MD5 = "a793a0a2ea93603b551dde422ab02665"  # re-aimed @ method-truth-sweep: the ancestor-bundle guard, the derived beat in status/brief, the persona seed at init, the routing-key taxonomies, the CARD `goal:` placeholder guard, the routing-key check skipping an UNTOUCHED scaffold slot, the seeding loop no longer shadowing `title`, and `ancestor_bundle` keying on `abf_version:` so a docs homepage is not read as a bundle. prior: 6be570d8… @ method-truth-sweep
# ADD 3.0 (ABF-1): the engine is a flat two-file pair (add.py + cli.py), no add_engine/ package.
# ENGINE_PKG_MD5 is repurposed to pin the dispatch entry cli.py (the second engine file).
ENGINE_PKG_MD5 = "8e32e4dc9b652f02b128d62980754156"  # re-aimed @ method-truth-sweep (`init --nested`). prior: a943d7c6… @ enforcement-gaps
