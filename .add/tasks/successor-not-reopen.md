---
type: Task
title: Closed history is superseded, never reopened
status: done
depth: standard
sensitivity: mechanical
milestone: loop-that-closes
scope:
  - add-method/tooling/add.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - add-method/tests/engine
  - add-method/tooling/engine_pin.py
  - add-method/tooling/cli.py
  - add-method/src/add_method/_bundled/tooling/cli.py
  - add-method/skill/add
  - add-method/src/add_method/_bundled/skill/add
  - .claude/skills/add
  - add-method/tests/skill
  - add-method/FORMAT.md
gives:
  - S1 `reopen` refuses a done task whose milestone is `done` or `archived` (R:CLOSEDHISTORY) and names the successor form `add new Task <slug> --supersedes /tasks/<old>.md`
  - S2 `new --supersedes <ref>` writes the `supersedes:` edge (a list of cids) to an existing Task, refusing a ref that resolves to no node (R:PHANTOMPREDECESSOR); `show` walks it both ways
  - S3 loop.md and FORMAT say closed history is superseded, never reopened — the old node, its receipts and its PASS are never edited
generated: { by: add/3.6.0, at: 2026-09-11 }
verified:
  - { by: "plan:loop-that-closes", at: 2026-09-12, act: freeze, authority: plan, direction: "sha256:d8146f7e410016d2", binding: "sha256:ef0880511f9ce00d", gives: "sha256:d2c6428d81e6b16e" }
  - { by: "cli", at: 2026-09-12, act: brief, authority: process, brief: "sha256:e6b9ad288196f33d" }
  - { by: "process:run", at: 2026-09-12, act: run, authority: process, outcome: PASS, receipt: /tasks/successor-not-reopen.d/runs/1.md }
  - { by: "process:run", at: 2026-09-12, act: run, authority: process, floor: regression, outcome: FAIL, receipt: /tasks/successor-not-reopen.d/runs/2.md }
  - { by: "plan:loop-that-closes", at: 2026-09-12, act: refreeze, authority: plan, direction: "sha256:5821a8a6c4790cbc", binding: "sha256:634815e6c6684531", gives: "sha256:d2c6428d81e6b16e" }
  - { by: "cli", at: 2026-09-12, act: brief, authority: process, brief: "sha256:b6914fb8e5db4a05" }
  - { by: "process:run", at: 2026-09-12, act: run, authority: process, outcome: PASS, receipt: /tasks/successor-not-reopen.d/runs/3.md }
  - { by: "process:run", at: 2026-09-12, act: run, authority: process, floor: regression, outcome: FAIL, receipt: /tasks/successor-not-reopen.d/runs/4.md }
  - { by: "process:run", at: 2026-09-12, act: run, authority: process, outcome: PASS, receipt: /tasks/successor-not-reopen.d/runs/5.md }
  - { by: "process:run", at: 2026-09-12, act: run, authority: process, floor: regression, outcome: PASS, receipt: /tasks/successor-not-reopen.d/runs/6.md }
  - { by: "plan:loop-that-closes", at: 2026-09-12, act: gate, authority: process, outcome: PASS, receipt: /tasks/successor-not-reopen.d/runs/5.md, brief: "sha256:6dbca71d63586094" }
---
## CARD
goal: `reopen` refuses a task whose milestone is done or archived (R:CLOSEDHISTORY) and names `add new Task <slug> --supersedes /tasks/<old>.md`; `new` accepts `--supersedes`, writes the edge key that has had zero live uses since it was admitted, and `show` walks it both ways; the old node, its receipts and its PASS are never edited
why: `verified[]` is append-only so a reopen keeps the old PASS, but loop.md calls a reopen inside a closed milestone "incoherent, resolved by hand" and no `status --check` finding exists for it — post-close correction must not rewrite verified history (C10), and the edge key that says so already exists with no writer
beat: done · next: add status

## RULES
<must>
- M1 `reopen` refuses a done Task whose `milestone:` resolves to a Milestone with status `done` or `archived`, naming the milestone and its status and the fix `add new Task <slug>-2 --supersedes /tasks/<slug>.md --milestone <an open milestone>` -> R:CLOSEDHISTORY; no stamp lands and `status:` does not move; a done Task with no `milestone:`, or whose milestone is active, reopens exactly as before
- M2 `new Task <slug> --supersedes <ref>` (cli flag; engine field `supersedes`) writes `supersedes:` as a list holding the resolved cid; the ref may be a cid or a bare slug; a ref that resolves to no node refuses R:PHANTOMPREDECESSOR naming it and writes nothing; the predecessor need not be done
- M3 `show <new>` lists the predecessor under `supersedes` as declared here (↓) and `show <old>` lists the successor as declared elsewhere (↑); `doctor` raises no finding for a resolvable `supersedes:` edge
- M4 neither `new --supersedes` nor the refused `reopen` changes one byte of the old node's file or its `.d/` receipts -> R:REWRITTENPAST
- M5 loop.md's reopen section says a reopen inside a closed milestone is REFUSED (R:CLOSEDHISTORY) and names the successor form, replacing "surfaced by `add status --check` as incoherent and resolved by hand" — a finding the engine never had; FORMAT's zero-live-uses sentence names `supersedes` as the key that gained its writer and reader; the skill surface stays line-neutral vs HEAD and the three trees identical
</must>
<reject>
- R:CLOSEDHISTORY a done task reopened inside a closed milestone -> "CLOSEDHISTORY"
- R:PHANTOMPREDECESSOR a `supersedes:` edge written to a node that does not exist -> "PHANTOMPREDECESSOR"
- R:REWRITTENPAST the old node, its receipts or its PASS edited by the successor's creation or by the refusal -> "REWRITTENPAST"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 S2 S3 · the request does not say who may supersede; taking anyone who can `new` — the successor is a fresh node that walks the whole loop (freeze, receipts, gate) under its own milestone's authority, so no seam is skipped by superseding -> cost if wrong: a successor is created to dodge a closed milestone's history; the edge names the old node and `show` walks it, so the dodge is visible
- A2 [which] covers: S1 · the request does not say which milestone statuses are "closed"; taking `done` and `archived` — the two states past the goal-gate, exactly what `release` accepts — and every other status (active, direction, no status) as open -> cost if wrong: a milestone hand-marked closed under another word stays reopenable · probe: a milestone with `status: shipped` does not refuse
- A3 [when] covers: S1 S2 · the request does not say whether the successor must be created before the refusal; taking NO ordering — the refusal names the form and creating the successor is the author's next verb, not a precondition -> cost if wrong: none; the refusal is idempotent
- A4 [absent] covers: S1 S2 · the request does not say what a task with no `milestone:` means; taking it as open history (no milestone closed it), reopenable as before, and a `supersedes:` written by hand before this verb as a plain edge `show` already walks -> cost if wrong: an orphan task is reopened after its era; the reopen stamp records the reason as it always has
- A5 [order] covers: S2 · the request does not say how many predecessors a successor may name; taking a list — one `--supersedes` per call writes one cid, a second call on the same slug refuses R:DUPSLUG as today, and a hand-written list of several is read as several edges -> cost if wrong: a task superseding two closed tasks needs a hand edit for the second cid
- A6 [experience] covers: S1 S2 S3 · the request does not say who reads the refusal; the reader is the person who just found a defect in a shipped milestone; hard for them is a refusal with no way forward — taking the refusal to carry the exact successor command with the old cid filled in, and `show <old>` to answer "what replaced this" without a search -> cost if wrong: the person hand-edits `status:` and the closed history is rewritten anyway
- A7 [which] covers: S2 · the request does not say which ref FORMS `--supersedes` accepts; taking what `resolve_ref` already answers — a bare slug or a cid — and refusing a fragment address like `/tasks/t.md#M1`, because a predecessor is a NODE and an edge to part of one is not a history -> cost if wrong: an author naming a lesson meets R:PHANTOMPREDECESSOR and writes the node address instead · probe: `--supersedes /tasks/t.md#M1` refuses
- A8 [which] covers: S3 · the request does not say which surfaces must carry the sentence; taking loop.md (the method every agent reads) and FORMAT.md (the key census that counted `supersedes` unused) — not README and not the book chapters, because those two files are the ones that made the false promise -> cost if wrong: a book reader meets the old wording until the next docs pass
- A9 [when] covers: S3 · the request does not say when the new reading takes effect; taking THIS engine forward, with no migration and no re-judging of history — a bundle that already reopened a task inside a closed milestone keeps its record, because the refusal guards the next call, never the past (M4's own law) -> cost if wrong: an old bundle reads as conformant under prose it predates
- A10 [absent] covers: S3 · the request does not say what an ABSENT or diverged skill tree means; taking all three trees as one surface — the check compares bytes, so a missing or stale tree fails loudly rather than letting the installed copy promise the finding the engine never had -> cost if wrong: a partial install ships the old sentence; the mirror check is the thing that catches it
- A11 [order] covers: S1 S3 · the request does not say where the new rung sits among `reopen`'s existing ones; taking LAST — after type, `done` and the beat are validated — so a malformed call is still named by the flag the operator typed, and the doc edit lands in the source tree first and is mirrored, never edited per-tree -> cost if wrong: a user with both a bad beat and a closed milestone is told about the milestone first

## PLAN
contract: `reopen(root, cid, to, reason)` gains the R:CLOSEDHISTORY rung after the `done` check · `new(...)` resolves `supersedes` to a cid list, refusing R:PHANTOMPREDECESSOR · cli `new --supersedes REF` · loop.md lines rewritten in place · FORMAT sentence rewritten
strategy: the milestone is read through `_membership_ref`/the node's `milestone:` slug as `milestone_done`'s members are found; `show` already walks every EDGE_KEY so M3 needs no renderer change, only a check; four twins, both pins, three skill trees line-neutral
scope: add-method/tooling/add.py add-method/src/add_method/_bundled/tooling/add.py add-method/tests/engine add-method/tooling/engine_pin.py add-method/tooling/cli.py add-method/src/add_method/_bundled/tooling/cli.py add-method/skill/add add-method/src/add_method/_bundled/skill/add .claude/skills/add add-method/tests/skill add-method/FORMAT.md
regression: full · python3 -m pytest add-method/tests -q -p no:cacheprovider · engine change (method.md bind)
port: `add.reopen`, `add.new`, `add.show` on a bundle fixture with a done milestone and a done task

## EDGES
- E1 Given task t done under milestone m whose status is done (and again archived) · When `reopen t --to build` · Then R:CLOSEDHISTORY naming m, its status and `add new Task t-2 --supersedes /tasks/t.md`; t's file is byte-identical
- E2 Given t done under an active milestone, and u done with no milestone · When `reopen` · Then both reopen with a stamp, as before
- E3 Given `new Task t-2 --supersedes t` (slug) and `--supersedes /tasks/t.md` (cid) · When created · Then `supersedes:` holds `/tasks/t.md`; given `--supersedes ghost` · Then R:PHANTOMPREDECESSOR and no file
- E4 Given t-2 supersedes t · When `show t-2` and `show t` · Then t-2's rows carry `↓ supersedes … /tasks/t.md` and t's carry `↑ supersedes … /tasks/t-2.md`; `doctor` names no finding on either
- E5 Given a milestone with `status: shipped` (an unknown word) · When `reopen` · Then it reopens — only `done` and `archived` are closed
- E6 Given release-stamp's frozen M3/E12, which needs a member reopened AFTER its closing gate inside a milestone that is `done` at release time · When that suite runs under this rung · Then the state is reached in the legal order — reopen while the milestone is active, then close it — and the older claim, its assertion and its refusal are untouched; the rung still refuses the NEXT reopen (a contract collision resolved by ORDER, never by weakening either side)

## CHECKS
- test_reopen_refuses_inside_a_closed_milestone · covers: M1, R:CLOSEDHISTORY, E1 · acceptance · done and archived both refuse, naming the milestone and the successor command; no stamp
- test_reopen_still_returns_open_history · covers: M1, A2, A4, E2, E5 · acceptance · active, no-milestone and `shipped` all reopen with a stamp
- test_new_supersedes_writes_the_edge · covers: M2, E3 · acceptance · slug and cid both land as the resolved cid list
- test_new_refuses_a_phantom_predecessor · covers: M2, R:PHANTOMPREDECESSOR, E3 · acceptance · named, nothing written
- test_show_walks_supersedes_both_ways · covers: M3, E4 · acceptance · ↓ on the successor, ↑ on the predecessor, doctor silent
- test_the_past_is_never_rewritten · covers: M4, R:REWRITTENPAST · acceptance · old node bytes and receipts identical after a refused reopen and a successor
- test_cli_new_carries_supersedes · covers: M2 · acceptance · the parser has --supersedes and the dispatch writes the edge
- test_loop_md_and_format_state_it · covers: M5 · static · loop.md names R:CLOSEDHISTORY and the successor form, not the phantom finding; FORMAT names supersedes' writer; trees identical; line-neutral vs HEAD
- test_a_fragment_is_no_predecessor · covers: M2, A7, R:PHANTOMPREDECESSOR · acceptance · a lesson address is not a node
- test_the_state_a_closed_milestone_member_reaches_by_order · covers: M1, A11, E6 · acceptance · the older contract keeps its claim
red-first: every check MUST fail first.

## EVIDENCE
receipt: /tasks/successor-not-reopen.d/runs/5.md · kind: test-ids · 10/10 reported · exit 0 · 2026-09-12
gate: PASS · authority process · by plan:loop-that-closes · receipt /tasks/successor-not-reopen.d/runs/5.md · 2026-09-12

## LESSONS
- none filed — no lesson cites /tasks/successor-not-reopen.md (add learn <lens> "<lesson>" --evidence /tasks/successor-not-reopen.md)
