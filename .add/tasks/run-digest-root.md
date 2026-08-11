---
type: Task
title: run's digest root is the bundle parent — and a degrade is said, not silent
status: done
milestone: v3-final-collateral
scope:
  - add-method/tooling/add.py
  - add-method/tests/engine/test_run_digest_root.py
gives:
  - S1 `run()` — scope digest computed from the bundle parent, the same root `gate` resolves
  - S2 `run()` receipt `note:` — a declared scope that yields no digest is recorded with its cause
  - S3 `fresh()` no-digest refusal — the message names the candidate causes
generated: { by: add/3.0.0, at: 2026-08-11 }
verified:
  - { by: "human:tindang", at: 2026-08-11, act: freeze, authority: process, direction: "sha256:b91d9a947c5e1092" }
  - { by: "cli", at: 2026-08-11, act: brief, authority: process, brief: "sha256:22c88e221287e593" }
  - { by: "process:run", at: 2026-08-11, act: run, authority: process, outcome: PASS, receipt: /tasks/run-digest-root.d/runs/1.md }
  - { by: "human:tindang", at: 2026-08-11, act: gate, authority: process, outcome: PASS, receipt: /tasks/run-digest-root.d/runs/1.md, brief: "sha256:22c88e221287e593" }
---
## CARD
goal: the receipt's freshness digest and the gate's freshness check resolve `scope:` from the SAME root, and any degrade to mtime says why on the record
why: field finding from hardening tally #1 — `run --cwd add-method` silently produced a digest-less receipt that `gate` then refused with a message naming neither the cwd cause nor the fix; honest refusal, opaque experience
beat: done · next: add status
## RULES
<must>
- M1 `run()` computes `scope_digest` from the bundle parent (`root.parent`) — the identical root `gate` passes to `fresh()` — regardless of `--cwd`, which remains only the command's working directory
- M2 a node that declares `scope:` whose run records no digest gets the cause written into the receipt's `note:` — the degrade is on the record, never silent
- M3 `fresh()`'s no-digest refusal names the candidate causes (not a git working tree, or the `scope:` paths did not exist at run time)
</must>
<reject>
- R:SILENTDEGRADE a receipt degrading from content to mtime freshness with nothing on the record saying why -> "SILENTDEGRADE"
</reject>
## ASSUMPTIONS
- A1 [who] covers: S1,S2,S3 · the request does not say who consumes the degrade note; taking "the human reading the receipt or the gate refusal — no machine branches on it" -> cost if wrong: a tool parses prose it should not
- A2 [which] covers: S1,S2,S3 · the request does not say which degrade causes are named; taking "the two the engine can see: no git tree at the bundle parent, and scope entries missing there" -> cost if wrong: a third cause stays opaque · probe: the refusal text names both causes
- A3 [when] covers: S1,S2,S3 · the request does not say when the note is written; taking "at run time, into the receipt — gate only reads; existing receipts are untouched" -> cost if wrong: gate grows a write path (law 3 breach)
- A4 [absent] covers: S1,S2,S3 · the request does not say what a scope-less node gets; taking "unchanged: no scope means no digest, no note, and gate's existing freshness-n/a path" -> cost if wrong: doc-lane tasks start drawing degrade notes
- A5 [order] covers: S1,S2,S3 · the request does not say precedence between a run-failure note and a degrade note; taking "both survive, joined with `; ` — a timeout note is never overwritten" -> cost if wrong: one diagnosis erases the other
## PLAN
contract: one-line digest-root change in `run()` + a degrade note branch; two-clause cause list in `fresh()`'s no-digest message
scope: add-method/tooling/add.py · add-method/tests/engine/test_run_digest_root.py
## EDGES
- E1 `--cwd` a SUBDIR of the project (the tally-#1 reproduction) — digest must still land, content-fresh
## CHECKS
- test_digest_root_is_the_bundle_parent_not_the_cwd · covers: M1,E1 · run from a project subdir still records `freshness: content` with parent-relative paths
- test_missing_scope_paths_degrade_loudly · covers: M2,R:SILENTDEGRADE · a scope of ghosts yields mtime AND a receipt note saying why
- test_degrade_note_never_clobbers_a_failure_note · covers: M2 · a timeout's note and the degrade note both survive
- test_gate_refusal_names_the_causes · covers: M3,A2 · the probe: `fresh()`'s no-digest message names both candidate causes
- test_scopeless_nodes_stay_silent · covers: M2 · no scope, no note — the doc lane is untouched
red-first: every check MUST fail first.
## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>
## LESSONS
- <lesson> -> add learn <lens>
