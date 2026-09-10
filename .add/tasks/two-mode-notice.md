---
type: Task
title: freeze names the plan-floor Musts that carry one evidence mode — a notice, never a refusal
status: done
depth: standard
sensitivity: architecture
milestone: refute-at-t2
scope:
  - add-method/tooling/add.py
  - add-method/tooling/cli.py
  - add-method/FORMAT.md
  - add-method/tests/engine
  - add-method/src/add_method/_bundled/tooling
  - add-method/docs/03-direction.md
  - add-method/skill/add/phases/direction.md
  - .claude/skills/add/phases/direction.md
  - add-method/src/add_method/_bundled/skill/add/phases/direction.md
  - add-method/tests/skill
  - .add/tooling
gives:
  - S1 `add.check_modes(node) -> {check_id: mode | None}` — the mode word of each CHECKS line, from the closed set `acceptance · property · contract · static · unit · e2e · manual`
  - S2 `add.single_mode_musts(node) -> [(M<n>, mode), …]` — the Musts whose covering checks carry exactly one known mode
  - S3 `add freeze` success note — under the refute rung's arming (standard|deep × Task × floor plan|human × not explore) a `notice:` line naming those Musts; the stamp is written regardless
  - S4 `add todo` direction hint — `<n> single-mode Must(s)` appended to the existing counts under the same arming
  - S5 FORMAT §6.2, docs 03 and direction.md (three trees) state the notice and that it never refuses
generated: { by: add/3.6.0, at: 2026-09-10 }
verified:
  - { by: "plan:refute-at-t2 — apply all by Tin Dang 2026-09-10", at: 2026-09-11, act: freeze, authority: plan, direction: "sha256:ce55efcea1ff563f", binding: "sha256:882cf8210471dfac" }
  - { by: "cli", at: 2026-09-11, act: brief, authority: process, brief: "sha256:0c3fa13661e00363" }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/two-mode-notice.d/runs/1.md }
  - { by: "advisor:method-steward (fresh add-advisor session, opus)", at: 2026-09-11, act: refute, authority: process, outcome: refuted, probes: 3, receipt: /tasks/two-mode-notice.d/runs/1.md, tier: T2, note: "two CHECKS lines sharing one check id (- test_b covers M1 · contract, then - test_b covers M2 · acceptance): check_modes keys by check id and the last line wins, so M1's contract mode is dropped and the notice falsely names M1 as single-mode (acceptance) though it meets the rule" }
  - { by: "plan:refute-at-t2 — apply all by Tin Dang 2026-09-10 (refreeze: T2 refute graduated E3)", at: 2026-09-11, act: refreeze, authority: plan, direction: "sha256:209de4f4b39846bc", binding: "sha256:0b417b4206ea56c4" }
  - { by: "cli", at: 2026-09-11, act: brief, authority: process, brief: "sha256:4ffc8cd9c4d9999d" }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/two-mode-notice.d/runs/2.md }
  - { by: "advisor:engine-notary (fresh add-advisor session, opus)", at: 2026-09-11, act: refute, authority: process, outcome: refuted, probes: 3, receipt: /tasks/two-mode-notice.d/runs/2.md, tier: T2, note: "two single-mode Musts on different modes at a plan floor: freeze emits 'notice: M1 (acceptance), M2 (contract) carry one evidence mode — …' but FORMAT.md §6.2 documents 'notice: M1, M3 carry one evidence mode (acceptance) — …', a shape the engine never emits (M5 via M3 and A6); test_prose_states_the_notice greps keywords only" }
  - { by: "builder", at: 2026-09-11, act: replan, authority: process, note: "second T2 refute: FORMAT §6.2 example carried the pre-refreeze notice shape; example corrected and test_prose_states_the_notice tightened to match the engine's format string (check strengthened, not renamed)" }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/two-mode-notice.d/runs/3.md }
  - { by: "advisor:engine-notary (fresh add-advisor session, opus)", at: 2026-09-11, act: refute, authority: process, outcome: refuted, probes: 3, receipt: /tasks/two-mode-notice.d/runs/3.md, tier: T2, note: "a Must id declared twice in ## RULES, each Must single-mode: single_mode_musts iterates rules_of(node) undeduped, so freeze emits 'notice: M1 (acceptance), M1 (acceptance), M2 (unit) …' and add todo reports 3 single-mode Musts for two, while uncovered_obligations dedupes the same input" }
  - { by: "plan:refute-at-t2 — apply all by Tin Dang 2026-09-10 (refreeze: third T2 refute graduated E4)", at: 2026-09-11, act: refreeze, authority: plan, direction: "sha256:d3ea8a70c8e53931", binding: "sha256:8fd57a8108a35a7f" }
  - { by: "cli", at: 2026-09-11, act: brief, authority: process, brief: "sha256:fedee028e18c9dcf" }
  - { by: "process:run", at: 2026-09-11, act: run, authority: process, outcome: PASS, receipt: /tasks/two-mode-notice.d/runs/4.md }
  - { by: "advisor:engine-notary (fresh add-advisor session, opus)", at: 2026-09-11, act: refute, authority: process, outcome: held, probes: 3, receipt: /tasks/two-mode-notice.d/runs/4.md, tier: T2, note: "P1 R:NOISE's unbound Milestone clause: _rung_bound type-gates before single_mode_musts is called, a Milestone freeze prints no notice · P2 R:NOTAMUST through M2: a covers list mixing M1/M2 with a filled E1 and a probed A1 each on one mode lists only the Musts · P3 degenerate bodies: no CHECKS / no RULES give () and [] with no crash, todo renders, freeze refuses first with R:UNCOVERED so the success-note notice is unreachable" }
  - { by: "plan:refute-at-t2 — apply all by Tin Dang", at: 2026-09-11, act: gate, authority: plan, outcome: PASS, receipt: /tasks/two-mode-notice.d/runs/4.md, brief: "sha256:64a3b7e17595608d" }
---
## CARD
goal: the rule "at a plan or human floor a Must carries two checks of different mode" gets a reader — the freeze names the Musts still on one mode, so compliance is measurable on the next milestone and the rule is either promoted to a refusal or dropped on evidence
why: dogfood-and-measure F1 — the session that wrote the two-mode rule froze 0 of 10 plan-floor Musts that way one task later; prose nobody follows binds nothing. A refusal would grow ceremony back on the mechanical lane (the previous milestone's own risk line); a notice costs one line and makes the count visible where the author still has the file open
beat: done · next: add status

## RULES
<must>
- M1 `check_modes` reads each `## CHECKS` line as `- <id> · covers: <refs> · <mode> …` — the first token after the second `·`, stripped of surrounding backticks or parentheses (direction.md's own typography) and lowercased, is the mode when it is one of `acceptance property contract static unit e2e manual`; any other word, or no third segment, is `None`
- M2 `single_mode_musts` lists a Must exactly when the known modes of the CHECKS LINES that cover it form ONE distinct value — keyed by line, so two lines sharing one check id each keep their own mode — a Must with no known mode is not listed (nothing to judge), one with two or more is not listed; only `M<n>` referents are considered
- M3 `freeze` — armed by `_rung_bound` — appends `notice: M1 (acceptance), M3 (contract) carry one evidence mode — a plan-floor Must carries two (direction.md § router)` (`carries` for one) to its SUCCESS note and still writes the stamp; with no single-mode Must the note is unchanged
- M4 `todo` appends `<n> single-mode Must(s)` to the direction-beat hint under the same arming, after the unswept and uncovered counts
- M5 FORMAT §6.2 states the notice (what it reads, when it arms, that it never refuses); docs 03 and direction.md's CHECKS paragraph (all three trees) name it in one sentence
</must>
<reject>
- R:REFUSED `freeze` never refuses on mode count — a node whose every Must is single-mode freezes at a plan floor with the notice on the note -> "REFUSED"
- R:NOISE `depth: quick`, a `process` floor, `kind: explore` and a Milestone print no notice and no hint, whatever their CHECKS say -> "NOISE"
- R:NOTAMUST Rejects, edges and probed assumptions are never listed — the rule is about Musts -> "NOTAMUST"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2, S3, S4, S5 · the request does not say who acts on the notice; taking the author at the freeze (the AI under a standing go-ahead, or the human at a human floor) — the notice names the fix in the same breath, the engine judges nothing -> a notice with no named fix is noise the reader learns to skip
- A2 [which] covers: S1, S2 · the request does not say which lines count; taking every CHECKS line `covers()` already parses — a line the covers regex rejects has no mode either — and the mode set closed to the seven words direction.md lists -> an open set would let `unit-ish` count as a second mode · probe: `- t · covers: M1 · Acceptance · …` and `- t · covers: M1 · acceptance-ish · …` read as `acceptance` and `None`
- A3 [when] covers: S3, S4 · the request does not say when the notice arms; taking exactly the refute rung's arming (`_rung_bound`) — the two rules are aimed at the same floor and a second arming law would drift from the first -> a notice on a quick task is the ceremony-regrowth the milestone's risk line names
- A4 [absent] covers: S1, S2, S3, S4 · the request does not say what a check with no mode word means; taking `None`, ignored by the count — a Must covered only by mode-less checks is not listed, since the author never claimed a mode -> listing it would push authors to add a word, not a second kind of evidence
- A5 [order] covers: S3, S4 · the request does not say where the notice sits; taking the freeze note's line between the `recorded` line and `next:`, and the todo hint's count last in the bits — appended, so existing readers of both keep their positions -> a re-ranked hint chain changes what an author is told first for reasons unrelated to this rung
- A6 [experience] covers: S1, S2, S3, S4, S5 · the request does not say how the notice reads; taking each Must id with its one mode beside it in parentheses, and the pointer to the router, in one line -> a notice that only counts sends the reader back to the file to find which Must
- A7 [which] covers: S3, S4, S5 · n/a · the arming rule (A3) is the whole selection
- A8 [when] covers: S1, S2, S5 · n/a · pure readers of a body, and prose
- A9 [absent] covers: S5 · n/a · prose
- A10 [order] covers: S1, S2, S5 · n/a · a map and a list in authored RULES order, each Must id once (the third T2 refute: a duplicated `M1` line is named once); prose

## PLAN
contract: S1–S5 above — `CHECK_MODES = ("acceptance", "property", "contract", "static", "unit", "e2e", "manual")`; `check_modes(node)` splits each CHECKS line on ` · ` and reads segment 3's first word; `single_mode_musts(node)` composes `covers(node)` and `rules_of(node)`; `freeze` computes the list when `_rung_bound(graph, cid, fm)` and inserts the `notice:` line before `next:`; `todo` appends the count to `bits`; FORMAT §6.2 new; docs 03 and direction.md one sentence each (direction.md's byte growth funded by trimming its own CHECKS paragraph); engine twins ×4 and `engine_pin` re-aimed last.
strategy: red suite first in tests/engine/test_two_mode_notice.py; build add.py; prose; full suite before the receipt; repin last.
port: `add.single_mode_musts(node)` and `add.freeze(...)`'s note — tests drive the library and the CLI both

## EDGES
- E1 Given M1 covered by one `acceptance` check and one check with no mode word · When freeze runs at a plan floor · Then the notice names M1 (acceptance)
- E2 Given M1 covered by an `acceptance` check and a `contract` check, M2 by two `acceptance` checks · When freeze runs at a plan floor · Then the notice names M2 only
- E3 Given two CHECKS lines sharing the id `test_b` — one covering M1 with mode `contract`, one covering M2 with mode `acceptance` — and M1 also covered by an `acceptance` line · When freeze runs at a plan floor · Then M1 is not named (the T2 refute's finding, graduated)
- E4 Given `M1` declared on two RULES lines and every Must single-mode · When freeze runs at a plan floor · Then M1 is named once and `add todo` counts two Musts (the third T2 refute's finding, graduated)

## CHECKS
- test_check_modes_reads_the_closed_set · covers: M1, A2 · acceptance · seven words parse, `Acceptance` lowercases, `` `property` `` and `(contract)` strip, `acceptance-ish` and a two-segment line are None
- test_single_mode_musts_lists_one_known_mode_only · covers: M2, R:NOTAMUST, E1, E2 · acceptance · one mode listed, two not, none-known not, a Reject with one mode not
- test_freeze_notice_at_plan_floor_still_stamps · covers: M3, R:REFUSED, E2 · acceptance · the note carries `notice: M2 (acceptance) carries one evidence mode`, the freeze stamp exists, M1 absent from the notice
- test_freeze_silent_when_unarmed_or_two_modes · covers: M3, R:NOISE · acceptance · quick · process floor · explore → no `notice:`; every Must two-mode at plan → no `notice:`
- test_todo_hint_counts_single_mode_musts · covers: M4, R:NOISE · acceptance · `1 single-mode Must` on a plan-floor direction task, absent on a quick one
- test_freeze_notice_reaches_the_cli · covers: M3 · contract · `cli.py freeze` prints the notice line and exits 0
- test_duplicate_check_id_keeps_each_lines_mode · covers: M2, E3 · acceptance · two lines sharing `test_b`: M1 keeps `contract`, is not listed, and the freeze prints no notice
- test_duplicate_must_id_is_named_once · covers: M2, M4, E4 · acceptance · `M1` on two RULES lines: listed once, counted once, named once
- test_prose_states_the_notice · covers: M5 · contract · FORMAT has `### §6.2`, `notice` and `never refuses`; docs 03 and direction.md ×3 name the notice; direction.md twins byte-identical
red-first: every check MUST fail first.

## EVIDENCE
receipt: /tasks/two-mode-notice.d/runs/4.md · kind: test-ids · 9/9 reported · exit 0 · 2026-09-11
refute: held · 3 probe(s) · tier T2 · by advisor:engine-notary (fresh add-advisor session, opus) · against /tasks/two-mode-notice.d/runs/4.md · 2026-09-11 · P1 R:NOISE's unbound Milestone clause: _rung_bound type-gates before single_mode_musts is called, a Milestone freeze prints no notice · P2 R:NOTAMUST through M2: a covers list mixing M1/M2 with a filled E1 and a probed A1 each on one mode lists only the Musts · P3 degenerate bodies: no CHECKS / no RULES give () and [] with no crash, todo renders, freeze refuses first with R:UNCOVERED so the success-note notice is unreachable
gate: PASS · authority plan · by plan:refute-at-t2 — apply all by Tin Dang · receipt /tasks/two-mode-notice.d/runs/4.md · 2026-09-11

## LESSONS
- none filed — no lesson cites /tasks/two-mode-notice.md (add learn <lens> "<lesson>" --evidence /tasks/two-mode-notice.md)
