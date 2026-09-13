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

ENGINE_MD5 = "0e67c3822e628ae996bf25afeff31dea"  # re-aimed @ refute-tier-floor: the tier rung is an ALLOWLIST — `SIGNING_TIERS`, DERIVED as `REFUTE_TIERS` minus T1 so it follows if the ladder moves. The security lens measured that `tier: "T1 "` rendered as `tier T1` in the engine's own EVIDENCE view and still recorded a human-floor PASS, a well-formed stamp attesting nothing; `sensitivity_floor`'s R:SILENT_FLOOR law (an unreadable declaration floors UP) now governs the control too. The REFUSAL states the reason true of the value it read (M1 never quotes it); the plan-floor NOTICE is M2's frozen literal for T1/no-tier, because a Must that states a string IS that string — threading the new clause through it drifted off the contract invisibly. prior: 90404d26… @ must-carries-source (`must_lines`) — NOT 70d1db24…, which this file briefly named by mistake: that is the pre-correction value M60/M62 are about, and naming it here skipped a link in the chain those lessons keep honest
# ADD 3.0 (ABF-1): the engine is a flat two-file pair (add.py + cli.py), no add_engine/ package.
# ENGINE_PKG_MD5 is repurposed to pin the dispatch entry cli.py (the second engine file).
ENGINE_PKG_MD5 = "6bb27c137985b21bcd6b9ebe76aa4376"  # re-aimed @ successor-not-reopen: `new --supersedes REF`. prior: d2583eb8… @ escape-with-prevention
