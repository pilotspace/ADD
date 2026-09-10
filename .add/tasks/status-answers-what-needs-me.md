---
type: Task
title: status answers what needs me
status: done
depth: standard
scope:
  - add-method/tooling/add.py
  - add-method/tests/engine/test_status_answers_what_needs_me.py
  - add-method/tests/engine/test_output_trims.py
  - add-method/tests/engine/test_authoring_beat.py
  - add-method/tests/engine/test_roadmap_reads_as_a_roadmap.py
  - add-method/tests/skill/test_claimed_output_guard.py
  - add-method/tooling/engine_pin.py
  - add-method/skill/add/seed.md
  - add-method/src/add_method/_bundled/skill/add/seed.md
  - .claude/skills/add/seed.md
gives:
  - S1 `add status` bare — the rows a reader sees, what they are ordered by, and the `next:` line that ends it
  - S2 `add status --all` — the way back to everything the bare report withheld
generated: { by: add/3.6.0, at: 2026-09-10 }
verified:
  - { by: "process:auto", at: 2026-09-10, act: freeze, authority: process, direction: "sha256:c80acbb0c1394afe", binding: "sha256:eee2d62f1dce3265" }
  - { by: "builder", at: 2026-09-10, act: replan, authority: process, note: "M3 found a bigger defect than the empty-board case it was written for. `BEAT_NEXT[build]` is 'add run {slug} -- <test cmd> --junitxml=...' — so EVERY frozen task's next: line hands back an unrunnable slot, not just the nothing-open branch. A notary genuinely cannot know a project's test command, but it does not have to guess: `run` is handed the real command every time it is called. It now REMEMBERS the last one on index.md, and the build hint replays it. The slot survives only until the first run, and after that the next: line is the command that actually worked here." }
  - { by: "builder", at: 2026-09-10, act: replan, authority: process, note: "M3 as written is too absolute, and the empty board is where it shows. A slot only the HUMAN can fill (a slug they have not chosen, a test command a notary cannot know) is legitimate guidance; a slot the ENGINE could have filled is the defect. The empty-board next: goes back to naming `add new`, because pointing a reader with nothing to do at `add doctor` answers a question they did not ask." }
  - { by: "process:auto", at: 2026-09-10, act: refreeze, authority: process, direction: "sha256:c80acbb0c1394afe", binding: "sha256:eee2d62f1dce3265" }
  - { by: "cli", at: 2026-09-10, act: brief, authority: process, brief: "sha256:8592ddb0da18ad91" }
  - { by: "process:run", at: 2026-09-10, act: run, authority: process, outcome: PASS, receipt: /tasks/status-answers-what-needs-me.d/runs/1.md }
  - { by: "process:auto", at: 2026-09-10, act: refreeze, authority: process, direction: "sha256:7235daed01b007c2", binding: "sha256:eee2d62f1dce3265" }
  - { by: "cli", at: 2026-09-10, act: brief, authority: process, brief: "sha256:4b94df229d75bd4a" }
  - { by: "process:run", at: 2026-09-10, act: run, authority: process, outcome: PASS, receipt: /tasks/status-answers-what-needs-me.d/runs/2.md }
  - { by: "process:auto", at: 2026-09-10, act: gate, authority: process, outcome: PASS, receipt: /tasks/status-answers-what-needs-me.d/runs/2.md, brief: "sha256:4b94df229d75bd4a" }
---
## CARD
goal: orientation shows the work that needs a decision, says so plainly when none does, and always ends in a command you can run
why: on this bundle `status` prints three rows — PROJECT, `index`, and an ARCHIVED milestone — while hiding 112 nodes, and ends in `next: add new task <slug>`, which is not a command. It was tuned for a bundle mid-flight and degrades at both ends: nothing actionable on a nearly-done board, and 85% unreachable on a large one
beat: done · next: add status

## RULES
<must>
- M1 the bare report lists WORK THAT NEEDS A DECISION — a node with a real beat — and never a `done` or `archived` one; a node carrying no state at all is counted by type, never printed as a row
- M2 rows are ordered by how close the work is to needing a human: verify · build · direction · queued · abandoned · adrift, and only then by slug — never by node type, which put an archived milestone above every open task
- M3 the report ends in a command that RUNS: no `<slug>` placeholder ever reaches the `next:` line
- M4 a reader who withheld nothing gets no hint to withhold less: `--all` never advises `--all`, and every row the cap hides is reachable by a named, runnable command
- M5 a bundle where nothing needs a decision SAYS SO in one line, and still names what to do next — silence and a wall of done nodes are both wrong answers
- M6 the report names where the reader left off — the last recorded act and its node — because a resume point that omits the last session is not a resume point
- M7 nothing in the report wraps or misaligns at 100 columns: one row is one line, and a truncated value ends on a word boundary
</must>
<reject>
- R:DEADHINT the report advises a flag or verb that cannot change what it just printed -> "DEADHINT"
- R:NOWAYIN a row is withheld from the bare report and no runnable command reaches it -> "NOWAYIN"
- R:DEADROW a node carrying no state prints a row in the bare report -> "DEADROW"
- R:PLACEHOLDER_NEXT the `next:` line contains an unexpanded `<…>` slot -> "PLACEHOLDER_NEXT"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the request does not say who reads it; taking "an AGENT resuming cold with no memory of the session, and a human reviewer reading a bundle they did not build — both ask one question, `what needs me?`, and neither can act on an inventory" -> the report optimises for the author who already knows the board, who is the one reader who did not need it
- A2 [which] covers: S1 · the request does not say which nodes are work; taking "a node with a real beat — `verify · build · direction` plus the three scaffold words; `done`, `dropped` and `archived` are ANSWERED, and a stateless Spec/Persona/Project/index is vocabulary, not board" · probe: on this bundle the bare report prints zero rows and says so, rather than printing PROJECT, index and an archived milestone -> the same three useless rows survive under a new layout
- A3 [when] covers: S1, S2 · the request does not say when the cap applies; taking "the cap bounds the BARE report only — `--all` is the way back and must never itself be capped, because a cap under `--all` leaves rows no command can reach (R:NOWAYIN)" · probe: `--all` on a 132-node bundle prints every kept row, and the bare report's hint names a command that produces them -> the escape hatch is spent and 112 nodes stay unreachable
- A4 [absent] covers: S1 · the request does not say what an EMPTY board means; taking "a real answer, not an empty list — `nothing needs you` plus the counts that prove it and a runnable next" -> a finished bundle is indistinguishable from a broken read
- A5 [order] covers: S1 · the request does not say what breaks a tie inside one beat; taking "slug, ascending — stable, so two runs of a read verb never disagree, and a reader can find a row by name" -> rows shuffle between runs and the report cannot be diffed
- A6 [experience] covers: S1 · the request does not say the width; taking "100 columns, one row per line, and a truncated title or goal ends on a word boundary with `…`" · probe: no line of the bare report exceeds 100 columns on a bundle whose titles are long -> rows wrap in a narrow terminal and the columns stop being columns
- A7 [who] covers: S2 · the request does not say who runs `--all`; taking "the same reader, one step further in — so `--all` is a superset of the bare report and never re-orders it" -> the two views disagree about the same bundle and neither can be trusted
- A8 [which] covers: S2 · the request does not say which withheld rows `--all` restores; taking "every kept row, done and archived included — `--all` means all, and any further filtering belongs to `search`" -> a third view is invented and the reader has to learn which one lies
- A9 [absent] covers: S2 · the request does not say what `--all` shows on an EMPTY bundle; taking "the same one-line answer the bare report gives — the flag widens the board, it does not change what an empty board means" -> `--all` reports nothing at all and reads as a failure
- A10 [order] covers: S2 · the request does not say whether `--all` re-sorts; taking "identical ordering to the bare report (M2), with the withheld rows interleaved in their proper place, not appended" -> a reader who learned the bare order has to relearn it
- A11 [experience] covers: S2 · the request does not say what `--all` costs a reader; taking "it is uncapped by design (A3) and can print hundreds of rows, so its FIRST line states how many are coming — a reader who asked for everything should still know the size of what they asked for before it scrolls past" -> the escape hatch trades an unreachable row for an unreadable wall

## PLAN
contract: `status` partitions the graph ONCE into `needs` (a real beat), `answered` (done/dropped/archived) and `vocabulary` (no `status:` at all — Project, index, Spec, Persona alike, a PREDICATE not a type list). The bare report prints `needs`, ordered by `ATTENTION_RANK`; `answered` is counted and reachable by a named `add search --status done`; `vocabulary` is counted by type as it is today. An empty `needs` prints one line. A new `last:` line reads the most recent stamp across the graph. `next:` resolves through `_next_verb` or, when nothing is open, a concrete `add new Task <slug> --title "…"` template is replaced by the one runnable thing left — `add doctor` when there are findings, else the literal creation command with no slot.
strategy: partition first (every rule reads it), then ordering, then the two hint lines, then width.

## EDGES
- E1 `--all` on a bundle with more kept rows than the cap — every row prints, and no `--all` hint appears
- E2 a bundle where every node is done — one line, plus a runnable next
- E3 a node whose `status:` is a value the engine does not know — it is WORK (unrecognised is not answered), so it prints rather than vanishing
- E4 a fresh `init` bundle — vocabulary only, no work; the empty answer must not read as an error
- E5 a title long enough to force truncation, in a row whose slug is also at the column limit
- E6 the `last:` line on a bundle with NO stamps anywhere — absent, never a guessed date

## CHECKS
- test_the_board_shows_only_what_needs_a_decision · covers: M1, M5, R:DEADROW, A2, A4, E2, E3, E4 · done/archived/stateless never print as rows; an unknown status still does; an empty board answers in one line
- test_rows_are_ordered_by_attention · covers: M2, A5, A10, E1 · the six beats sort in that order and ties break by slug, identically under `--all`
- test_every_hint_names_something_that_runs · covers: M3, M4, R:DEADHINT, R:PLACEHOLDER_NEXT, R:NOWAYIN, A3, A7, A8 · no `<…>` in `next:`; `--all` never advises `--all`; every withheld row is reachable by the command the bare report names, driven for real
- test_the_report_says_where_you_left_off · covers: M6, E6 · the last recorded act and its node appear, and are absent rather than guessed when no stamp exists
- test_no_row_wraps_or_misaligns · covers: M7, A1, A6, A9, E5 · every line ≤100 columns and every truncation ends on a word boundary, on a bundle built with long titles
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
