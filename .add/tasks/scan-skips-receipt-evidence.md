---
type: Task
title: The graph scan stops parsing every receipt's evidence payload
status: done
depth: standard
sensitivity: architecture
scope:
  - add-method/tooling/add.py
  - add-method/tests/engine/test_scan_skips_receipt_evidence.py
  - add-method/FORMAT.md
gives:
  - S1 `add.py` scan-path node read that elides a Run receipt's evidence payload from the PARSED frontmatter while leaving `raw` byte-complete
  - S2 `tests/engine/test_scan_skips_receipt_evidence.py` — the suite pinning elision, raw completeness, and graph parity
  - S3 `FORMAT.md` §4 — the sentence stating what the graph scan parses and what it defers
generated: { by: add/3.4.0, at: 2026-09-03 }
verified:
  - { by: "plan:engine-perf-diagnosis", at: 2026-09-03, act: freeze, authority: plan, direction: "sha256:deca9d79842c7eb9", binding: "sha256:a0e60e91b83d9d93" }
  - { by: "cli", at: 2026-09-03, act: brief, authority: process, brief: "sha256:4c6d89bcb2737a8e" }
  - { by: "process:run", at: 2026-09-03, act: run, authority: process, outcome: PASS, receipt: /tasks/scan-skips-receipt-evidence.d/runs/1.md }
  - { by: "process:run", at: 2026-09-03, act: run, authority: process, outcome: PASS, receipt: /tasks/scan-skips-receipt-evidence.d/runs/2.md }
  - { by: "plan:engine-perf-diagnosis", at: 2026-09-03, act: refreeze, authority: plan, direction: "sha256:d8bc23b33580555d", binding: "sha256:a0e60e91b83d9d93" }
  - { by: "cli", at: 2026-09-03, act: brief, authority: process, brief: "sha256:c42e998953890637" }
  - { by: "process:run", at: 2026-09-03, act: run, authority: process, outcome: PASS, receipt: /tasks/scan-skips-receipt-evidence.d/runs/3.md }
  - { by: "plan:engine-perf-diagnosis", at: 2026-09-03, act: gate, authority: plan, outcome: PASS, receipt: /tasks/scan-skips-receipt-evidence.d/runs/3.md, brief: "sha256:c42e998953890637" }
---
## CARD
goal: a bundle-wide scan stops paying for evidence nothing in the graph reads — the receipt payload is parsed when a receipt is opened, never when the bundle is walked
why: measured on this bundle — 97 Run receipts are 68% of all T0 parse time, because `receipt.scope_digest` and `receipt.passed` put 7979 `path:` entries and 953 test-id lines into frontmatter that every command parses. Both grow monotonically and nothing prunes them: the digest is one entry per file in scope and rose 66 to 103 entries per receipt in three weeks, while receipts are append-only. So `add status` — the first command of every session — pays for the entire project history, and the only readers of that payload (`fresh` and the gate's coverage map) reach it through `latest_receipt`, which does its own direct single-node read.
beat: done · next: add status

## RULES
<must>
- M1 the bundle scan MUST NOT parse a Run receipt's `scope_digest`, `passed` or `failed` payload into the graph
- M2 a scan-produced node's `raw` MUST stay byte-identical to the file's frontmatter, so the one write path cannot lose a byte it never parsed
- M3 a direct `read()` of a receipt MUST still carry the full payload — `latest_receipt`, `fresh` and the gate's coverage map are unchanged
- M4 apart from those three keys, a scanned graph MUST be identical to the graph the unmodified scan produced — same nodes, same cids, same every other value
- M5 the elision MUST actually fire on a receipt-bearing bundle, and MUST NOT fire on a bundle with no receipts
</must>
<reject>
- R:LOSSYRAW a scan-produced node whose `raw` is missing bytes the file carries -> "LOSSYRAW"
- R:BLINDGATE a gate, freshness check or coverage map reading the payload off the graph instead of a direct read -> "BLINDGATE"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1,S2,S3 · the request does not say who may rely on the payload being in the graph; taking "no one — `fresh` (add.py:2701) and the coverage map (add.py:4246) are the only readers and both are fed by `latest_receipt`'s own direct read; verified by grep over both oracles" -> cost if wrong: a consumer silently reads an absent key as empty · probe: a check asserts the payload is absent from the graph AND present via direct read
- A2 [which] covers: S1,S2,S3 · the request does not say which keys are evidence; taking "exactly `scope_digest`, `passed`, `failed` — the three measured to dominate, all nested under `receipt:` on `type: Run` nodes; `verified[]` stamps stay parsed because edges and authority are read off them" -> cost if wrong: a fourth heavy key keeps the cost · probe: the suite names the three and a control asserts `verified` survives
- A3 [when] covers: S1,S2,S3 · the request does not say when elision applies; taking "the scan path only, never `read()` itself — `read()` is the public tiered API and FORMAT §4 defines it" -> cost if wrong: a direct receipt read loses its payload and the gate goes blind -> R:BLINDGATE · probe: a check reads a receipt directly and finds the payload
- A4 [absent] covers: S1,S2,S3 · the request does not say what an absent payload means; taking "absent from the graph means UNPARSED, never EMPTY — no consumer may treat a missing key as `[]`, which is why M3 keeps the direct read whole rather than defaulting" -> cost if wrong: a freshness check silently passes on zero recorded files
- A5 [order] covers: S1,S2,S3 · [order] n/a · elision is per-node and order-independent; `scan` already iterates `sorted(root.rglob(...))` and this changes no iteration
- A6 [experience] covers: S1,S2,S3 · the request does not say who receives this; taking "the operator running `add status` as their first command each session, and the agent paying it on every verb — neither is told anything, because a scan that got cheaper has nothing to say; the change must be invisible in OUTPUT and visible only in cost" -> cost if wrong: a chatty optimisation trains people to ignore engine output · probe: a check asserts `status` output is byte-identical before and after

## PLAN
contract: a scan-only reader that strips the three evidence blocks from the text handed to `parse()`, while taking `raw` from the ORIGINAL text so nothing a writer could need is ever dropped. `read()`, its tiers, and every direct-read consumer are untouched.
scope: add-method/tooling/add.py · add-method/tests/engine/test_scan_skips_receipt_evidence.py · add-method/FORMAT.md

## EDGES
- E1 a receipt whose `passed:` list is empty or absent — elision is a no-op, and the node still scans
- E2 a NON-Run node that happens to carry a key named `passed:` at top level — must NOT be elided, because the elision is anchored to the nested receipt block
- E3 a bundle with zero receipts — the graph is byte-for-byte the same as before, and no regex work is wasted

## CHECKS
- test_graph_scan_elides_the_receipt_evidence_payload · covers: M1,M5 · a receipt-bearing bundle scans with `scope_digest`/`passed`/`failed` absent from the graph node
- test_scan_node_raw_stays_byte_complete · covers: M2,R:LOSSYRAW · the scanned node's `raw` equals the file's own frontmatter text exactly
- test_direct_read_still_carries_the_payload · covers: M3,A3 · `read(path,"T0")` on the same receipt returns all three keys populated
- test_latest_receipt_still_feeds_freshness_and_coverage · covers: M3,R:BLINDGATE,A1 · `latest_receipt` returns a receipt whose digest and passed ids are intact
- test_scanned_graph_is_otherwise_identical · covers: M4,A2 · every node, cid and non-elided value matches an unmodified scan, with a positive control asserting the elision actually happened
- test_elision_is_anchored_to_the_receipt_block · covers: E2 · a top-level `passed:` on a non-Run node survives the scan
- test_receipt_with_an_empty_payload_still_scans · covers: E1 · an empty/absent `passed:` is a no-op, and the key after the block survives
- test_bundle_with_no_receipts_is_unchanged · covers: E3,M5 · a receipt-free bundle scans identically
- test_status_output_is_unchanged · covers: A6 · `status` renders byte-identical output before and after
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
