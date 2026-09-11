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

ENGINE_MD5 = "cf3b418a9b304426b73ba4befea2a33c"  # re-aimed @ consumers-go-stale: stamped_gives · _pins_of · needs_pins (pins the provider's STAMPED digest, deduped by resolved target) · stale_needs (sorted, open tasks only) · consumers_of · the refreeze note names only consumers whose pin differs · needs_stale in doctor and todo · R:STALENEEDS at gate · a ref carrying `,`/`=` pins `?` and reads back as `?` · the pin's unit is (node, fragment) and a scalar gives: is one surface · an unattestable ref is written delimiter-stripped and the reader takes exact tokens only · _PIN_UNSAFE covers the stamp line's own alphabet · consumers_of reads the stamp, not live edges — nine T2 founds · the R:STALENEEDS recipe names add brief. prior: (regression-floor) regression_floor · R:NOFLOOR at freeze · run(floor=) · latest_floor_receipt · R:FLOORUNRUN at gate
# ADD 3.0 (ABF-1): the engine is a flat two-file pair (add.py + cli.py), no add_engine/ package.
# ENGINE_PKG_MD5 is repurposed to pin the dispatch entry cli.py (the second engine file).
ENGINE_PKG_MD5 = "a6b9eb04c240193d0a2c50eb5973b9d7"  # re-aimed @ regression-floor: --floor on the run parser. prior: b3c4372a… @ refute-tier-and-changed
