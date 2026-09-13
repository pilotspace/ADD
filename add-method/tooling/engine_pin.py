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

ENGINE_MD5 = "c75177bc6e330720c142a9d4cf20d636"  # re-aimed @ quick-lane-tripwire: the floor now reads WHO SIGNED the freeze, not the authority the engine computed. Round six made routing require `authority_for == "human"` — but `freeze` WRITES `authority: human` whenever the floor it computes is human: `claimed_authority(None, floor)` returns the floor, the default `--by` is `cli`, and `interview_gap` has nothing to put to a human when the author left ASSUMPTIONS empty, which the author controls. So `add new Persona p --scope src/auth/token.py` then a bare `add freeze p` stamped `authority: human` with no person anywhere, and the sensitive floor stood down in TWO commands — reading the computed floor back asks the engine whether the engine thought a human was owed, never whether one signed. A `by:` string is still a claim; it is a DELIBERATE one, and telling `human:<name>` from a default `cli` is the line the ledger already draws. prior: f7c639fb… @ same task (the computed floor)
# ADD 3.0 (ABF-1): the engine is a flat two-file pair (add.py + cli.py), no add_engine/ package.
# ENGINE_PKG_MD5 is repurposed to pin the dispatch entry cli.py (the second engine file).
ENGINE_PKG_MD5 = "6bb27c137985b21bcd6b9ebe76aa4376"  # re-aimed @ successor-not-reopen: `new --supersedes REF`. prior: d2583eb8… @ escape-with-prevention
