---
type: Task
title: Status shows the last consequential verdict
status: done
depth: standard
kind: feature
milestone: state-that-tells-truth
scope:
  - add-method/tooling/add.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - .add/tooling/add.py
  - add-method/tooling/engine_pin.py
  - add-method/tooling/test_tree_parity.py
  - add-method/tests/engine/test_status_shows_last_verdict.py
  - add-method/tests/engine/test_status_answers_what_needs_me.py
  - add-method/tests/engine/test_regression_floor.py
gives:
  - S1 `add status [--all]` orientation view of open Task attention and gate evidence
generated: { by: add/3.6.0, at: 2026-09-15 }
verified:
  - { by: "plan:codex", at: 2026-09-15, act: freeze, authority: plan, direction: "sha256:0b0650d5fc7f3693", binding: "sha256:0003dc4a436879be", gives: "sha256:f8c12de50748e3f2" }
  - { by: "cli", at: 2026-09-15, act: brief, authority: process, brief: "sha256:431ee7be7eb38c09" }
  - { by: "plan:codex", at: 2026-09-15, act: refreeze, authority: plan, direction: "sha256:fb021d5d3190f794", binding: "sha256:0003dc4a436879be", gives: "sha256:f8c12de50748e3f2" }
  - { by: "cli", at: 2026-09-15, act: brief, authority: process, brief: "sha256:7ac241c517144e98" }
  - { by: "plan:codex", at: 2026-09-15, act: refreeze, authority: plan, direction: "sha256:e238e849b5d59e20", binding: "sha256:531d95a1d41b601f", gives: "sha256:f8c12de50748e3f2" }
  - { by: "cli", at: 2026-09-15, act: brief, authority: process, brief: "sha256:46f00a8babc411c9" }
  - { by: "process:run", at: 2026-09-15, act: run, authority: process, outcome: PASS, receipt: /tasks/status-shows-last-verdict.d/runs/1.md }
  - { by: "agent:gpt-5.6-status-b1-fresh-refute", at: 2026-09-15, act: refute, authority: process, outcome: refuted, probes: 13, receipt: /tasks/status-shows-last-verdict.d/runs/1.md, tier: T2, note: "valid 85-character Task slug makes global last line 111 columns despite the 100-column orientation contract" }
  - { by: "plan:codex", at: 2026-09-15, act: refreeze, authority: plan, direction: "sha256:ebb1f92c4267c899", binding: "sha256:65b74a3cf57a15d6", gives: "sha256:f8c12de50748e3f2" }
  - { by: "cli", at: 2026-09-15, act: brief, authority: process, brief: "sha256:8c69101d48dc6127" }
  - { by: "process:run", at: 2026-09-15, act: run, authority: process, outcome: PASS, receipt: /tasks/status-shows-last-verdict.d/runs/2.md }
  - { by: "agent:gpt-5.6-status-b1-v2-refute", at: 2026-09-15, act: refute, authority: process, outcome: refuted, probes: 8, receipt: /tasks/status-shows-last-verdict.d/runs/2.md, tier: T2, note: "receipt 2 scope digest differs from all eight current scoped files; 70/70 result is stale for this candidate" }
  - { by: "process:run", at: 2026-09-15, act: run, authority: process, outcome: PASS, receipt: /tasks/status-shows-last-verdict.d/runs/3.md }
  - { by: "agent:gpt-5.6-status-b1-v2-refute", at: 2026-09-15, act: refute, authority: process, outcome: held, probes: 8, receipt: /tasks/status-shows-last-verdict.d/runs/3.md, tier: T2, note: "receipt 3 Git blob hashes match all eight scoped files; 70 JUnit cases and all 16 frozen CHECKS bind; earlier stale claim retracted because raw SHA1 was compared to Git blob SHA1" }
  - { by: "agent:codex", at: 2026-09-15, act: gate, authority: process, outcome: PASS, receipt: /tasks/status-shows-last-verdict.d/runs/3.md, brief: "sha256:99c0678098d6ca66" }
---
## CARD
goal: Resume state shows the active beat and its latest consequential gate with same-stamp evidence
why: a later run, check, brief, or refute currently takes the `last:` line and can obscure an unresolved stop
beat: done · next: add status

## RULES
<must>
- M1 `status` selects one open Task attention subject as `now`: an effective latest HARD-STOP after the Task's last reopen outranks other Tasks; ties use existing attention rank then canonical CID. Without a stop, it uses the Task named by the final runnable `next:` route when there is one, then the first open Task by existing attention rank and CID. It names the Task's `_beat_of` beat. If no Task is open, `now` and current gate evidence are absent even under `--all`. (from: state-that-tells-truth EXIT B1 · fails-on: hidden stop, dead subject, or status/brief beat contradiction)
- M2 `status` names that Task's latest readable `act: gate` verdict in append-only verified order after its last `act: reopen` as `last-gate=PASS | RISK-ACCEPTED | HARD-STOP`, and only a later gate with a readable verdict may supersede it. A later run, check, brief, refute, verdictless legacy gate, or equal-day timestamp cannot erase a known stop. An open Task with no readable gate says `last-gate=none`; a pre-reopen verdict is historical. (from: state-that-tells-truth EXIT B1 · fails-on: unresolved stop hidden by latest act or stale PASS projected across reopen)
- M3 `status` ties evidence to the selected gate stamp: a gate-stamped canonical receipt CID renders as its Task-local `runs/<n>.md` plus a `/tasks/<slug>.md#verified` reference; a sources gate without a receipt renders `/tasks/<slug>.md#FINDINGS`; a legacy gate without receipt says `receipt=unrecorded` and points to `#verified`. It never borrows a later run's receipt. The global `last:` act keeps its separate activity meaning and marks equal-day cross-node order as unknown. The final `next:` names a complete gate action when that is due; a build Task with no Task-owned run computation routes to `add show <slug>` so a different Task's global last command cannot become its test instruction. An owned command that already writes JUnit appears once. (from: state-that-tells-truth EXIT B1 · fails-on: evidence laundering, false chronology, foreign test command, or dead navigation)
- M4 Bare and `--all` status keep frontmatter-only T0 orientation and existing row order; the bare view retains its 20-row cap while `--all` remains uncapped. Headline, rows, and consequence/activity summaries are at most 100 columns. The final exact runnable `next:` may exceed that width when a legal long slug requires it; clipping the command would break navigation. The `now`/evidence summary remains visible when its Task row is capped. (from: status-answers-what-needs-me · fails-on: body-scan latency or truncated attention)
</must>
<reject>
- R:ACTASVERDICT A later non-gate act must never overwrite the consequential gate in orientation. -> "R:ACTASVERDICT"
- R:STALEGATE A gate before the last reopen must never appear as the current verdict. -> "R:STALEGATE"
- R:BORROWED_RECEIPT A gate must never cite a run that the gate stamp did not cite. -> "R:BORROWED_RECEIPT"
- R:T2SCAN Orientation must never read a Task body to produce its gate summary. -> "R:T2SCAN"
- R:FOREIGN_CMD A Task's next action must never replay another Task's test computation. -> "R:FOREIGN_CMD"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the caller is a human or agent resuming a local bundle; taking frontmatter as a reported claim rather than signer authentication -> external attestation remains a separate contract · probe: `status` reports stamp fields without inventing a signer
- A2 [which] covers: S1 · the plan does not define an attention subject for a no-Task board; taking only open Tasks as eligible, even under `--all` -> a completed bundle has no current gate summary · probe: historical done gates never become `now`
- A3 [when] covers: S1 · stamps share day-only `at`; taking verified list position within a Task after the last reopen as chronology, while equal-day stamps on different nodes cannot establish real global order -> hand-edited reorder changes the reported Task history and a date tie must be explicit · probe: same-day later act on the same Task cannot displace a gate; cross-node tie is marked; reopen resets it
- A4 [absent] covers: S1 · legacy gates may lack receipt or outcome; taking no receipt as `unrecorded`, no readable verdict ever as `none`, and a verdictless later gate as unable to supersede an earlier known stop -> old evidence stays explicit rather than inferred · probe: later run or verdictless gate is not borrowed
- A5 [order] covers: S1 · several stops can coexist; taking existing attention rank then CID to break ties after HARD-STOP priority -> stable board across reads · probe: capped rows and tie order still select the same Task
- A6 [experience] covers: S1 · a cold reader needs a navigable, narrow answer; taking bounded `now:`, `evidence:`, and `last:` summaries while preserving a full final action command -> a legal long slug can make only that final command overwide · probe: subject, beat, verdict, activity uncertainty, and evidence remain legible when the Task row is hidden

## PLAN
contract: `status(root, all=False, check=False)` keeps the existing headline, rows, global `last:`, and final action `next:`. Before final `next:`, add bounded `now: <slug> · beat=<derived> · last-gate=<effective verdict|none>` and, when a gate exists, `evidence: receipt=<runs/n.md|unrecorded> · ref=</tasks/slug.md#verified|#FINDINGS>`. `now` is absent when no open Task exists. Gate selection is per Task, after the last reopen, by verified[] index: the latest readable gate wins, while a verdictless gate wins only if no readable gate exists. The receipt token is taken from that exact selected gate stamp; canonical `/tasks/<slug>.d/runs/<n>.md` renders Task-local `runs/<n>.md`. Sources-kind gate lacking receipt references FINDINGS. A legacy missing receipt references the gate's verified stamp. Same-day `last:` picks later append position within a node; across nodes a deterministic CID tie is explicitly marked because day-only stamps cannot prove global sequence. A verify `next:` includes the required verdict. Build command replay resolves the latest narrow Task run stamp to its own Run frontmatter at T0; when none exists `next: add show <slug>` opens the Task PLAN. A computation carrying JUnit is not duplicated. Long valid slugs/refs truncate only summary display within 100 columns; the final action command retains the exact slug even if overwide. No separate stored verdict or body read is introduced.
regression: affected · `python3 -m pytest -q add-method/tests/engine/test_status_shows_last_verdict.py add-method/tests/engine/test_status_answers_what_needs_me.py add-method/tests/engine/test_beat_read_truth.py add-method/tests/engine/test_regression_floor.py add-method/tooling/test_tree_parity.py add-method/tests/skill/test_claimed_output_guard.py --junitxml=/private/tmp/status-shows-last-verdict-v3.xml` · checks the new consequence view, Task-owned command route, old orientation/floor guarantees, source/bundled/live parity, and reported check IDs
- O1 covers: M2,M3 · signal status/gate mismatch in host fixtures · window each tooling release · threshold any mismatch · action rollback

## EDGES
- E1 Given a HARD-STOP and same-day later run/check/refute, When status resumes, Then the stop and its gate-stamped receipt remain current while global `last:` reports the later act.
- E2 Given two gates before and after a reopen, When status resumes, Then only the post-reopen gate is current; without that later gate it says none.
- E3 Given PASS after HARD-STOP and then another act, When status resumes, Then PASS supersedes the stop and the original stop receipt is not borrowed.
- E4 Given two open stopped Tasks including one beyond the 20-row cap, When status resumes, Then the deterministic stop priority and CID tie are visible in `now` under both modes.
- E5 Given a sources-only gate or a legacy gate without receipt, When status resumes, Then its own FINDINGS/verified pointer is shown without an invented run.
- E6 Given no open Task but historical done gates, When status resumes, Then no current subject/verdict/evidence is projected.
- E7 Given a known HARD-STOP followed by a verdictless legacy gate, When status resumes, Then the known stop and its own receipt remain current; the later gate is only global activity.
- E8 Given a legal long Task slug, When status resumes, Then last/now/evidence stay within 100 columns and the final action retains the full slug.
- E9 Given two nodes with stamps on the same day, When status resumes, Then `last:` marks the cross-node order unknown instead of claiming which act actually occurred last.
- E10 Given a stored verify Task as final route, When status resumes, Then `next:` includes `gate <slug> PASS` plus its actor slot rather than an argparse-invalid bare gate command.
- E11 Given a run on Task A and an unrun build Task B, When status resumes B, Then it opens B's plan; A's computation never appears in B's next instruction.
- E12 Given B's own computation already writes JUnit, When status resumes B's build, Then that exact command appears once without an appended second JUnit destination.

## CHECKS
- test_same_day_later_acts_keep_the_stopped_gate_and_its_receipt · covers: M1,M2,M3,R:ACTASVERDICT,R:BORROWED_RECEIPT,A3,E1 · verdict and receipt remain tied to gate, independent of last act
- test_later_gate_supersedes_stop_without_borrowing_receipts · covers: M2,M3,R:BORROWED_RECEIPT,E3 · only a later gate can resolve a stop
- test_reopen_resets_the_current_gate · covers: M2,R:STALEGATE,E2 · pre-reopen PASS is history
- test_multiple_stops_have_stable_attention_even_under_row_cap · covers: M1,M4,A5,A6,E4 · priority and width survive truncation
- test_sources_and_legacy_gate_evidence_is_explicit · covers: M3,A4,E5 · absent receipts have honest refs
- test_no_open_task_has_no_current_verdict · covers: M1,A2,E6 · done history is not current work
- test_verdictless_gate_does_not_clear_a_known_stop · covers: M2,M3,A4,R:ACTASVERDICT,E7 · a later gate with no verdict cannot launder a stop
- test_long_slug_keeps_summaries_bounded_and_next_exact · covers: M3,M4,A6,E8 · legal names do not wrap summaries or clip the action
- test_cross_node_same_day_last_marks_unknown_order · covers: M3,A3,E9 · no false cross-node chronology
- test_verify_next_includes_required_gate_verdict · covers: M3,E10 · final action is parseable with a verdict and actor
- test_unrun_build_next_does_not_borrow_foreign_command · covers: M3,R:FOREIGN_CMD,E11 · a build Task with no own run opens its plan
- test_task_owned_junit_command_replays_once · covers: M3,R:FOREIGN_CMD,E12 · one Task-owned computation and one JUnit path
- test_status_gate_summary_stays_frontmatter_only · covers: M4,R:T2SCAN,A1 · T0 bounded orientation
- test_live_engine_matches_canonical_when_present · covers: M4 · the installed dogfood engine stays byte-identical to the canonical engine when this repo carries it
- test_every_hint_names_something_that_runs · covers: M3 · an unrun Task opens its plan and an owned run becomes replayable without a foreign computation
- test_floor_only_run_keeps_the_build_beat · covers: M3 · a floor-only receipt still needs a narrow run chosen from the Task plan
red-first: seven original checks failed; the verdictless-gate check failed against candidate 1; the long-slug, day-tie, and incomplete-gate-cue checks failed after the fresh T2 width refutation; the foreign-command and duplicate-JUnit checks failed against that repair. All thirteen failures are retained as discriminating cases.

## EVIDENCE
receipt: /tasks/status-shows-last-verdict.d/runs/3.md · kind: test-ids · 70/70 reported · exit 0 · 2026-09-15
refute: held · 8 probe(s) · tier T2 · by agent:gpt-5.6-status-b1-v2-refute · against /tasks/status-shows-last-verdict.d/runs/3.md · 2026-09-15 · receipt 3 Git blob hashes match all eight scoped files; 70 JUnit cases and all 16 frozen CHECKS bind; earlier stale claim retracted because raw SHA1 was compared to Git blob SHA1
gate: PASS · authority process · by agent:codex · receipt /tasks/status-shows-last-verdict.d/runs/3.md · 2026-09-15

## LESSONS
- none filed — no lesson cites /tasks/status-shows-last-verdict.md (add learn <lens> "<lesson>" --evidence /tasks/status-shows-last-verdict.md)
