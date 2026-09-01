---
type: Task
title: A stamp the notary reports written is a stamp that reads back
status: done
depth: standard
sensitivity: data
scope:
  - add-method/tooling/add.py
  - add-method/tests/engine
gives:
  - S1 the stamp writers — every verb that appends a flow-map record to `verified:`
  - S2 the `_oneline` normaliser — what it must neutralise for a flow-map scalar
generated: { by: add/3.2.0, at: 2026-09-01 }
verified:
  - { by: "Tin Dang", at: 2026-09-01, act: freeze, authority: human, direction: "sha256:e6b2551ca8df9afe" }
  - { by: "cli", at: 2026-09-01, act: brief, authority: process, brief: "sha256:9c08d55836a6b8f8" }
  - { by: "process:run", at: 2026-09-01, act: run, authority: process, outcome: PASS, receipt: /tasks/stamp-field-integrity.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-09-01, act: refreeze, authority: human, direction: "sha256:2293042cc7b4e254" }
  - { by: "cli", at: 2026-09-01, act: brief, authority: process, brief: "sha256:f677674f76672298" }
  - { by: "process:run", at: 2026-09-01, act: run, authority: process, outcome: PASS, receipt: /tasks/stamp-field-integrity.d/runs/2.md }
  - { by: "Tin Dang", at: 2026-09-01, act: gate, authority: plan, outcome: PASS, receipt: /tasks/stamp-field-integrity.d/runs/2.md, brief: "sha256:f677674f76672298" }
---
## CARD
goal: no operator-supplied value can make a stamp read back as something other than what the verb reported writing.
why: `_oneline` is applied to `--reason` and to nothing else. Seven writers interpolate `by:` raw. Measured 2026-09-01: `add freeze t --by 'O"Brien' --authority human` prints `freeze recorded at authority `human`` and writes a record that parses back carrying ONLY `by` — `act`, `authority` and `direction` are swallowed by the unterminated scalar. `_is_frozen` is then False and `sealed_direction` is None: the seal silently does not exist while the human is told it does. It fails CLOSED (the gate refuses with R:UNSEALED, so nothing is let through), and that is the whole severity — but a notary whose only job is to record faithfully must never report a record it did not write. The trigger is an ODD number of `"`; a balanced pair (`Tin "TinDang97" Dang`) round-trips, which is exactly why this survived every real use.
beat: done · next: add status

## RULES
<must>
- M1 `_oneline` neutralises the double quote as well as the brace, so a value it returns cannot terminate or re-key a flow-map scalar.
- M2 Every writer that interpolates an operator-supplied value into a `verified:` flow map passes it through `_oneline` — `freeze`, `brief`, `replan`, `check`, `interview`, and both `gate` paths.
- M3 A stamp written with any operator string reads back with every key the writer intended, and the actor is recognisable in the recorded value.
- M4 A verb that cannot write a faithful record reports a refusal, never a success.
</must>
<reject>
- R:LIE a verb must never report a stamp recorded when the record does not read back -> "R:LIE"
- R:LOSSY normalising must not silently delete an actor's name down to nothing -> "R:LOSSY"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the request does not say whose values need normalising; taking every operator-supplied one — `by`, `reason`, `persona`, `note` — since the engine cannot tell a careful actor from a careless one -> if wrong a writer is missed and the defect survives in the one place nobody probed · probe: a check enumerates the writers from the SOURCE rather than from a hand list.
- A2 [which] covers: S2 · the request does not say which characters break a flow map; taking the double quote (terminates a scalar) and the brace (ends the map), which is what `_oneline` already half-does -> if wrong another character corrupts a record · probe: a round-trip check over quotes, braces, colons, commas and newlines.
- A3 [when] covers: S1 · the request does not say what happens to stamps ALREADY written badly; taking them as-is — this fixes the writer, never rewrites history, because an append-only ledger whose past entries can be edited is not a ledger -> if wrong an existing damaged bundle stays damaged · probe: the fix touches no reader and no existing file.
- A4 [absent] covers: S2 · the request does not say what an EMPTY `by` means; taking the writers' existing defaults (`unrecorded`, `process:check`) unchanged -> if wrong a blank name becomes a silent anonymous stamp · probe: an empty `by` still lands its default, not an empty scalar.
- A5 [order] covers: S2 · the request does not say whether normalising happens at the CLI or at the writer; taking the writer, so the library is safe for any caller and not only for `cli.py` -> if wrong a direct library user writes the bad record · probe: the check calls `add.freeze` directly, never the CLI.
- A6 [experience] covers: S1 · the request does not say what the actor should see; taking substitution over rejection — a name is a person's, and refusing `O"Brien` teaches nothing -> if wrong an operator is blocked by their own name · probe: the quote becomes an apostrophe and the name stays recognisable.
- A7 [who] covers: S2 · n/a · `_oneline` is a pure string function taking no actor.
- A8 [which] covers: S1 · n/a · M2 names the writers exhaustively; A1's probe enumerates them from source.
- A9 [when] covers: S2 · n/a · a pure function has no temporal boundary.
- A10 [absent] covers: S1 · n/a · A4 covers the empty-value reading for both surfaces.
- A11 [order] covers: S1 · n/a · stamps are appended in call order, which this task does not touch.
- A12 [experience] covers: S2 · n/a · `_oneline` prints nothing; its experience is S1's.
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: `_oneline` additionally maps `"` to `'`. The seven `by:` interpolations call it. No reader changes and no existing stamp is rewritten.
scope: add-method/tooling/add.py, add-method/tests/engine

## EDGES
- E1 a BALANCED pair (`Tin "TinDang97" Dang`) — already round-trips; it must keep doing so.
- E2 an empty `by` — the writer's own default still lands.
- E3 a value that is nothing BUT quotes — normalising must not reduce it to an empty scalar (R:LOSSY).
- E4 an existing bundle carrying an already-damaged stamp — untouched (A3).

## CHECKS
- test_oneline_neutralises_the_double_quote · covers: M1 · the returned value carries no `"`.
- test_a_stamp_survives_an_odd_quote_in_by · covers: M2, M3, R:LIE · every intended key reads back and the seal exists.
- test_the_actor_stays_recognisable · covers: A6, R:LOSSY · `O"Brien` reads back as `O'Brien`, not as nothing.
- test_every_stamp_writer_normalises_its_by · covers: M2, A1, A8 · the writers are enumerated from the SOURCE, and each round-trips.
- test_balanced_quotes_still_round_trip · covers: E1 · the incumbent case is unchanged.
- test_an_empty_by_keeps_the_writers_default · covers: A4, E2 · `unrecorded` and `process:check` still land.
- test_a_value_of_only_quotes_is_not_erased · covers: E3, R:LOSSY · normalising substitutes, never deletes.
- test_the_library_is_safe_without_the_cli · covers: A5 · `add.freeze` called directly is enough.
- test_a_flow_map_round_trips_every_punctuation · covers: A2, M4 · what the verb reports matches what the ledger holds, over every punctuation.
- test_no_existing_stamp_is_rewritten · covers: A3, E4 · the fix touches the writer, not history.
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- A normaliser is only as good as the set of writers that call it: `_oneline` was correct and applied to one field of seven -> add learn add
