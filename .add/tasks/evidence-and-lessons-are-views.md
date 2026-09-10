---
type: Task
title: EVIDENCE and LESSONS are written by the engine — a done node never carries the scaffold
status: done
depth: standard
sensitivity: architecture
scope:
  - add-method/tooling
  - add-method/FORMAT.md
  - add-method/tests
  - add-method/src/add_method/_bundled
  - add-method/docs/12-bundle-format.md
  - .add/tooling
gives:
  - S1 `## EVIDENCE` on a Task is an engine-written VIEW of `verified[]` — `receipt:` at `run`, `refute:` at `refute`, `gate:` at `gate` — keyed lines replaced in place, the scaffold never surviving a run
  - S2 `## LESSONS` on a Task is harvested at close (a closing gate, or `done`) from the five specs — one line per delta whose evidence pointer names this task, `- none filed` when none does
  - S3 `add doctor --sync` backfills both sections on every Task whose section is still the scaffold and whose record entitles the line; `add doctor` reports a done Task still carrying either scaffold (`evidence_scaffold`, info)
generated: { by: add/3.6.0, at: 2026-09-10 }
verified:
  - { by: "plan:evidence-over-tests", at: 2026-09-10, act: freeze, authority: plan, direction: "sha256:7e8c1037eef84ede", binding: "sha256:882cf8210471dfac" }
  - { by: "cli", at: 2026-09-10, act: brief, authority: process, brief: "sha256:cbb2abbff28c350c" }
  - { by: "process:run", at: 2026-09-10, act: run, authority: process, outcome: PASS, receipt: /tasks/evidence-and-lessons-are-views.d/runs/1.md }
  - { by: "session:fable-T1", at: 2026-09-10, act: refute, authority: process, outcome: held, probes: 4, receipt: /tasks/evidence-and-lessons-are-views.d/runs/1.md, note: "key order kept · near-miss slugs (viewed-2, xviewed) not harvested · live sync idempotent on 2nd pass · absent section untouched" }
  - { by: "plan:evidence-over-tests", at: 2026-09-10, act: gate, authority: plan, outcome: PASS, receipt: /tasks/evidence-and-lessons-are-views.d/runs/1.md, brief: "sha256:7cbd2760a84efbe1" }
advised_by: engine-notary
---
## CARD
goal: a done Task never carries the scaffold in EVIDENCE or LESSONS — the engine writes both sections as views of the record it already holds, and `doctor --sync` backfills the 88 + 64 nodes on this bundle that were promised it and never got it
why: FORMAT §5 says "EVIDENCE receipt / gate · LESSONS harvested at done", docs 12 says the same, and the engine's own placeholder guard explains it skips these sections because "EVIDENCE and LESSONS are filled by the run and the close" — no code path writes either. The truth lived only in `verified[]`; the body beside it kept the template. A promise the engine does not implement is the method-truth class this bundle has closed twice
beat: done · next: add status

## RULES
<must>
- M1 `add run` writes the EVIDENCE `receipt:` line from the receipt it just recorded — `<run cid> · kind: <test-ids|command-exit> · exit <n>` — replacing the scaffold or the previous `receipt:` line and touching no other line
- M2 `add refute` writes or replaces the EVIDENCE `refute:` line — `<held|refuted> · <n> probe(s) · by <name> · <run cid>`
- M3 `add gate` writes or replaces the EVIDENCE `gate:` line — `<verdict> · authority <a> · by <name> · <date> · <run cid>` — naming the receipt it gated, and a gate that closes also harvests LESSONS
- M4 the harvest: every delta across the specs whose evidence pointer names this task (its cid, its slug, or a path under `<slug>.d/`) becomes one LESSONS line `- [<lens> · <ID> · <status>] <lesson>`; when none does the section reads `- none filed — no delta cites this task`; the scaffold line never survives a close, and `done` harvests the same way
- M5 `add doctor --sync` backfills EVIDENCE and LESSONS on every Task whose section is still the scaffold and whose stamps entitle the line, reporting each under `recomputed`; on this bundle that repairs the 88 EVIDENCE and 64 LESSONS scaffolds measured at direction
- M6 `add doctor` reports a done Task still carrying either scaffold as `evidence_scaffold` (info), and FORMAT §5, docs 12 and the `placeholders_in` comment say the sections are engine-written views
</must>
<reject>
- R:TWOHOMES an EVIDENCE line carries no fact `verified[]` does not already hold, and a LESSONS line no text a spec does not hold — the sections are views, never a second store; a hand-authored line that is neither the scaffold nor an engine key survives untouched -> "TWOHOMES"
- R:MANUFACTURED `--sync` writes no `receipt:`/`refute:`/`gate:` line for a stamp that does not exist and no lesson for a delta that does not cite the task — a backfill is a recomputation, never invented history -> "MANUFACTURED"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2, S3 · the request does not say who may write these sections; taking the engine only, on the verbs that produce the fact (run · refute · gate · done · sync) — a human line that is neither scaffold nor keyed is left alone -> a human note in EVIDENCE would otherwise be clobbered by the next run
- A2 [which] covers: S1, S2, S3 · the request does not say which deltas belong to a task; taking the CITATION rule — evidence names the task's cid, slug or a path under its `.d/` — never a date window, because same-day lessons would land on every task frozen that day -> lessons whose evidence cites a test file (as this session's did) are not harvested; `learn`'s note now tells the caller to cite the task · probe: a lesson citing `add-method/tests/x.py` does not appear in the task's LESSONS, one citing `/tasks/<slug>.md` does
- A3 [when] covers: S1, S2, S3 · the request does not say whether LESSONS is harvested before close; taking close only (a closing gate or `done`) — FORMAT's own word is "harvested at done" — while EVIDENCE lines land as each fact is recorded -> a lesson filed after close is not on the node; `--sync` re-harvests, so it lands on the next sync
- A4 [absent] covers: S1, S2, S3 · the request does not say what a node with no EVIDENCE or LESSONS heading gets; taking nothing — a body without the heading is authored that way (pre-3.0 nodes), and the engine appends no section it was not scaffolded -> older nodes stay as they are; `doctor` does not report them because there is no scaffold to report
- A5 [order] covers: S1, S2, S3 · the request does not say the line order inside EVIDENCE; taking `receipt:` · `refute:` · `gate:` — the order the facts are produced — and the latest run wins the `receipt:` line, the gate names the receipt it gated -> a two-run task shows run 2 on `receipt:` and the gated cid on `gate:`; both agree unless someone gated a stale run, which the gate refuses
- A6 [experience] covers: S1, S2, S3 · the request does not say who reads the sections; taking a human opening the node cold — so each line is one keyed sentence with the cid, never a table, and `- none filed` says why rather than leaving the heading empty -> an empty heading reads as "nothing happened", which is the silence this task exists to end

## PLAN
contract: S1 · S2 · S3 — `_set_keyed_line(body, section, key, value)` replaces a `key:` line or the scaffold inside one section, else appends; `render_evidence(root, cid)` derives the three lines from stamps and the receipt file; `harvest_lessons(root, cid)` from `deltas(status=each)` filtered by the citation rule; called from `run`, `refute`, `gate` (both paths), `done`, and `doctor_sync` (backfill over every Task with a scaffold section and an entitling stamp); `doctor` gains `evidence_scaffold` (info); FORMAT §5 and docs 12 reworded; the `placeholders_in` comment made true.
strategy: red suite first (tests/engine/test_evidence_and_lessons_views.py); helpers, then the five call sites, then sync + doctor; full suite before the receipt; run `add doctor --sync` on this bundle as the live measurement and record the count in EVIDENCE via the receipt.
port: `add.render_evidence(root, cid)` · `add.harvest_lessons(root, cid)` · `add.doctor_sync(root)` — the tests drive the library through the verbs

## EDGES
- E1 Given a node whose EVIDENCE was hand-edited to `receipt: pending` · When `add run` records a receipt · Then the `receipt:` line is replaced and every other line in the section is byte-identical
- E2 Given a Task with two run receipts · When gated PASS on the second · Then `receipt:` names run 2 and `gate:` names run 2

## CHECKS
- test_run_writes_the_receipt_line · covers: M1, E1 · acceptance · after a run the scaffold is gone, `receipt:` names the run cid and kind; a `pending` line is replaced, a foreign line survives
- test_refute_writes_the_refute_line · covers: M2 · acceptance · held/refuted, probe count, by, run cid on one keyed line
- test_gate_writes_the_gate_line_naming_the_gated_receipt · covers: M3, E2, A5 · acceptance · two runs, gate → `gate:` and `receipt:` both name run 2
- test_close_harvests_lessons_that_cite_the_task · covers: M4, A2 · acceptance · a delta citing `/tasks/<slug>.md` lands, one citing a test file does not; `done` harvests too
- test_close_with_no_citing_lesson_writes_none_filed · covers: M4 · acceptance · the scaffold line is gone and the section says why
- test_sync_backfills_scaffold_sections_from_the_record · covers: M5 · acceptance · a done node with scaffold sections and real stamps is repaired and reported; a node with no stamps is left alone
- test_sync_and_verbs_never_overwrite_authored_lines · covers: R:TWOHOMES · acceptance · a free-text line in EVIDENCE survives run, gate and sync byte-for-byte
- test_sync_never_manufactures_a_line · covers: R:MANUFACTURED · acceptance · no refute stamp → no `refute:` line; no citing delta → `none filed`, never a borrowed lesson
- test_doctor_reports_a_done_node_still_carrying_the_scaffold · covers: M6 · acceptance · `evidence_scaffold` info finding before sync, none after
- test_format_book_and_comment_state_the_sections_as_views · covers: M6 · static · FORMAT §5, docs 12 and the `placeholders_in` comment carry the word "view" and name the writing verbs
- test_live_bundle_backfill_count · covers: M5 · acceptance · on this repo's own bundle, `doctor --sync` in a temp copy leaves no done Task with a scaffold EVIDENCE or LESSONS section
red-first: every check MUST fail first.

## EVIDENCE
receipt: /tasks/evidence-and-lessons-are-views.d/runs/1.md · kind: test-ids · 12/12 reported · exit 0 · 2026-09-10
refute: held · 4 probe(s) · by session:fable-T1 · against /tasks/evidence-and-lessons-are-views.d/runs/1.md · 2026-09-10 · key order kept · near-miss slugs (viewed-2, xviewed) not harvested · live sync idempotent on 2nd pass · absent section untouched
gate: PASS · authority plan · by plan:evidence-over-tests · receipt /tasks/evidence-and-lessons-are-views.d/runs/1.md · 2026-09-10

## LESSONS
- [method · M52 · open] A section the format PROMISES a writer for is a section nobody writes until a guard demands it: EVIDENCE and LESSONS were skipped by the placeholder guard because 'the run and the close fill them', and 88/113 done tasks carried the scaffold. Make it a view of the record (verb writes its keyed line, sync backfills) and pin it with a live-bundle count. (evidence: /tasks/evidence-and-lessons-are-views.md)
