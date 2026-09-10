---
type: Task
title: add refute — the refute-read becomes a stamp the gate can order, and filled edges join the interview
status: done
depth: standard
sensitivity: architecture
milestone: evidence-over-tests
scope:
  - add-method/tooling/add.py
  - add-method/tooling/cli.py
  - add-method/FORMAT.md
  - add-method/tests/engine
  - add-method/src/add_method/_bundled/tooling
  - add-method/tests/skill
  - add-method/tests/test_front_door_claim_truth.py
  - add-method/skill/add/SKILL.md
  - .claude/skills/add/SKILL.md
  - add-method/src/add_method/_bundled/skill/add/SKILL.md
  - add-method/docs/13-command-reference.md
  - add-method/README.md
  - README.md
  - .add/tooling
gives:
  - S1 `add refute <slug> --by "<name>" (--held | --found "<the input the bound checks never exercise>") [--probes N] [--note "<text>"]` — exit 0 and a stamp, exit 1 and a named refusal
  - S2 `act: refute` stamp appended to `verified[]` — `{ by, at, act: refute, authority: process, outcome: held|refuted, probes: <n>, receipt: <run cid it read>, note: "<text>" }`
  - S3 `add interview <slug>` compiles every FILLED `E<n>` edge as a question (id `E<n>`, dim `edge`), after the assumptions and before the Rejects
generated: { by: add/3.6.0, at: 2026-09-10 }
verified:
  - { by: "plan:evidence-over-tests", at: 2026-09-10, act: freeze, authority: plan, direction: "sha256:7021fa9d48223d90", binding: "sha256:882cf8210471dfac" }
  - { by: "cli", at: 2026-09-10, act: brief, authority: process, brief: "sha256:ab3015464cf31c8b" }
  - { by: "plan:evidence-over-tests", at: 2026-09-10, act: refreeze, authority: plan, direction: "sha256:7021fa9d48223d90", binding: "sha256:882cf8210471dfac" }
  - { by: "cli", at: 2026-09-10, act: brief, authority: process, brief: "sha256:b62e9c736f3b41ae" }
  - { by: "process:run", at: 2026-09-10, act: run, authority: process, outcome: PASS, receipt: /tasks/refute-verb.d/runs/1.md }
  - { by: "process:run", at: 2026-09-10, act: run, authority: process, outcome: PASS, receipt: /tasks/refute-verb.d/runs/2.md }
  - { by: "builder:claude (same session, tier T1)", at: 2026-09-10, act: refute, authority: process, outcome: held, probes: 3, receipt: /tasks/refute-verb.d/runs/2.md, note: "P1 refute on a Milestone via argv → R:NOTATASK exit 1, no stamp · P2 --probes -1 was recorded as given — a silence, not a frozen rule; argparse now refuses a negative count · P3 a finding with a double quote and a newline parses back as one flow-map note" }
  - { by: "plan:evidence-over-tests", at: 2026-09-10, act: gate, authority: plan, outcome: PASS, receipt: /tasks/refute-verb.d/runs/2.md, brief: "sha256:bff0cee927fcce86" }
advised_by: engine-notary
---
## CARD
goal: the refute-read becomes a record the gate can ORDER — `add refute` stamps who tried to break the green, against which receipt, and what they found; and the readable example (a filled edge) joins the interview so a human confirms it before the freeze
why: verify.md mandates a refute-read and `add-advisor` has a refute mode, yet nothing on the node says a green was ever read against — the one act that distinguishes evidence from a plausible diff lives only in the transcript. And Vaccari's test of an acceptance example is that the owner confirms it; `add interview` compiled assumptions and Rejects and never the example
beat: done · next: add status

## RULES
<must>
- M1 `add refute <slug> --by <name> --held` on a frozen Task with a run receipt appends one `act: refute` stamp with `outcome: held`, `probes: <n>`, and `receipt:` naming the LATEST run's cid
- M2 `add refute <slug> --by <name> --found "<input>"` appends the same stamp with `outcome: refuted` and the finding in `note:`, and its `next:` names the fix (build or refreeze, then `add run`, then refute again) — never a verdict
- M3 `add interview <slug>` compiles every filled `E<n>` line as a numbered question a human answers `confirm | correct | defer`, and an untouched `<placeholder>` edge is not a question
- M4 `refute` is a registered CLI verb wired to `add.refute`, counted by every registry that pins the verb set (28), and stated in FORMAT §8.4 with the stamp shape
</must>
<reject>
- R:NORECEIPT a refute on a Task with no run receipt is refused — a refute reads a green, and nothing has run -> "NORECEIPT"
- R:NOFINDING `--found` with an empty finding is refused, and `--held` with `--found` is refused — one outcome, and a refutation names its input -> "NOFINDING"
- R:UNSEALED a refute on an unfrozen Task is refused — there is no approved intent to read the green against -> "UNSEALED"
- R:NOVERDICT `refute` writes no gate stamp, moves no `status:`, lowers no floor — it is a lens on a green, exactly as `advise` is a lens on a beat -> "NOVERDICT"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2, S3 · the request does not say who may record a refute; taking anyone the `--by` names — the engine is a notary and records the name verbatim, as `interview` does (R:SELFANSWER is skill discipline) -> a stamp recorded by the building session reads the same as one by a fresh verifier; the tier ladder (C6) and the persona bind honesty, the engine binds presence
- A2 [which] covers: S1, S2, S3 · the request does not say which receipt a refute reads; taking the LATEST run receipt at the moment of the refute, named in the stamp so a later run can be told apart -> a refute against a stale run would otherwise pass as current; naming the receipt is what lets the gate rung (T5) order it · probe: the stamp's `receipt:` equals `latest_receipt()`'s cid at refute time
- A3 [when] covers: S1, S2, S3 · the request does not say whether a refute may precede the freeze or the first run; taking neither — refused as R:UNSEALED / R:NORECEIPT, the same stance `brief_stamp` takes on an unfrozen node -> a refute recorded before there is a green to read would be a stamp attesting nothing
- A4 [absent] covers: S1, S2, S3 · the request does not say what `--probes` and `--note` mean when omitted; taking `probes: 0` and no `note:` key on a held refute — recorded as given, never invented — and a refuted outcome with no finding refused (R:NOFINDING) -> a held refute with zero probes is visibly weaker on the record, which is the honest reading
- A5 [order] covers: S1, S2, S3 · the request does not say where an edge question sits in the interview; taking assumptions, then filled edges, then Rejects — the sweep first, the examples, then what must be refused — and interview_digest covers the edge text so rewording an edge re-opens the pass exactly as an assumption does -> existing nodes with filled edges and a recorded interview go stale once, on the bundle that ships this; they are all closed
- A6 [experience] covers: S1, S2, S3 · the request does not say who reads the refute stamp; taking the gate caller (T5) and a human reading the node — so the stamp carries the finding text inline, not a sidecar path, and the CLI `next:` after a held refute is the gate line -> a finding only in a sidecar would make the node unreadable without a second file open

## PLAN
contract: S1 · S2 · S3 above — `refute()` modelled on `brief_stamp` (frozen-Task check, `_transition` append) and `advise` (NO-EXEC, no floor change); the CLI subparser with a mutually-exclusive `--held | --found`; `_open_decisions` grows an EDGES pass between assumptions and Rejects using `edges_of`'s filled-edge rule; FORMAT §8.4 states the stamp; the verb count pins (test_search_registry · test_show_verb · test_authoring_beat · README) re-aim 27 -> 28; `engine_pin` and the `_bundled/tooling` twin re-pinned after the build.
strategy: red suite first in tests/engine/test_refute_verb.py; build add.py then cli.py; run the full suite before the receipt (engine change); repin last.
port: `add.refute(root, cid, by, held, finding, probes, note)` — the tests drive the library and the CLI both (M40: a verb is met only at the front door)

## EDGES
- E1 Given a Task whose `## EDGES` still carries the scaffold `<placeholder>` line · When `add interview` compiles · Then no `E` question is asked and the digest is unchanged from a node with no EDGES
- E2 Given a held refute stamp recorded against run 1 · When `add run` records run 2 · Then the refute stamp still names run 1 — chronology is on the record for the gate rung to read

## CHECKS
- test_refute_held_appends_stamp_naming_latest_receipt · covers: M1, A2 · acceptance · frozen + briefed + run → `--held --probes 3` → one act: refute stamp, outcome held, probes 3, receipt == latest_receipt cid
- test_refute_found_records_finding_and_names_the_fix · covers: M2 · acceptance · `--found "amount == 0"` → outcome refuted, note carries the finding, next names run + refute, no gate stamp
- test_refute_refuses_without_receipt · covers: R:NORECEIPT · acceptance · frozen, no run → None + "NORECEIPT"
- test_refute_refuses_empty_or_double_outcome · covers: R:NOFINDING · acceptance · `--found ""` and `--held --found x` both refused at the library and at argparse
- test_refute_refuses_unsealed · covers: R:UNSEALED · acceptance · unfrozen Task → None + "UNSEALED"
- test_refute_writes_no_verdict · covers: R:NOVERDICT · acceptance · after a held refute: no act: gate stamp, status unchanged, authority_for unchanged
- test_refute_is_wired_and_counted · covers: M4 · contract · parser has `refute`, WIRED names it, count pins read 28, FORMAT names §8.4 with `act: refute`
- test_interview_compiles_filled_edges_and_skips_placeholders · covers: M3, E1 · acceptance · a filled `E1 Given · When · Then` is a question with dim edge between A and R; the scaffold line is not; answering E1=confirm completes
- test_refute_stamp_survives_a_later_run · covers: E2 · acceptance · refute against run 1, then run 2 → the stamp still names run 1
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
