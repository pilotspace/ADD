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

ENGINE_MD5 = "4c2a048d03478968ee738c2832b575a2"  # re-aimed @ risk-accepted-integrity: every INTEGRITY refusal in `gate` binds RISK-ACCEPTED too (only EVIDENCE refusals stay PASS-only), `done` refuses a gate no freeze precedes, `_paths_touch` matches whole path segments, and an unreadable `sensitivity:` floors UP. prior: 1bf61710… @ authoring-beat-named
# ADD 3.0 (ABF-1): the engine is a flat two-file pair (add.py + cli.py), no add_engine/ package.
# ENGINE_PKG_MD5 is repurposed to pin the dispatch entry cli.py (the second engine file).
ENGINE_PKG_MD5 = "fced1ae9ad5743024aaa2610e5a99a7c"  # re-aimed @ enforcement-gaps (`check` records the caller context: tty vs process). prior: 5c37c3e0… @ box-check-verb
