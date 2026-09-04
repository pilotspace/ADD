---
type: Task
title: add deltas filters by lens, by --since, and by --as-of
status: done
depth: quick
milestone: okf-graph-time
scope:
  - add-method/tests/engine/test_deltas_time_filters.py
  - add-method/tooling/add.py
  - add-method/tooling/cli.py
  - add-method/tests/engine
gives:
  - S1 `add.py` `deltas()` with `lens` · `since` · `as_of` filters over the recorded validity intervals
  - S2 `cli.py` `add deltas --lens --since --as-of` flags, with the half-open boundary stated in --help
generated: { by: add/3.4.0, at: 2026-09-03 }
verified:
  - { by: "plan:okf-graph-time", at: 2026-09-04, act: freeze, authority: plan, direction: "sha256:01d3ab36c9075a19", binding: "sha256:a0e60e91b83d9d93" }
  - { by: "cli", at: 2026-09-04, act: brief, authority: process, brief: "sha256:ce12ae9703df1967" }
  - { by: "plan:okf-graph-time", at: 2026-09-04, act: refreeze, authority: plan, direction: "sha256:f3c876647f9462b4", binding: "sha256:a0e60e91b83d9d93" }
  - { by: "cli", at: 2026-09-04, act: brief, authority: process, brief: "sha256:af17c53b72e046ef" }
  - { by: "process:run", at: 2026-09-04, act: run, authority: process, outcome: PASS, receipt: /tasks/deltas-time-filters.d/runs/1.md }
  - { by: "plan:okf-graph-time", at: 2026-09-04, act: refreeze, authority: plan, direction: "sha256:b455a8dee680c653", binding: "sha256:a0e60e91b83d9d93" }
  - { by: "cli", at: 2026-09-04, act: brief, authority: process, brief: "sha256:ce4b01b19d3e4c95" }
  - { by: "process:run", at: 2026-09-04, act: run, authority: process, outcome: PASS, receipt: /tasks/deltas-time-filters.d/runs/2.md }
  - { by: "plan:okf-graph-time", at: 2026-09-04, act: gate, authority: process, outcome: PASS, receipt: /tasks/deltas-time-filters.d/runs/2.md, brief: "sha256:ce4b01b19d3e4c95" }
---
## CARD
goal: `add deltas` answers "what did this spec assert, and when" — by lens, since a date, and as of a past date
why: the dated grammar landed ids and validity intervals on all 43 lessons, and nothing reads the dates. A `## Deltas` section is append-only and now 42 entries deep across five specs, so the inventory the loop reads before planning is a wall with no way to ask which lessons are recent, which belong to one lens, or what the spec asserted when a past decision was taken. The interval is already recorded; this is the reader for it.
beat: done · next: add status

## RULES
<must>
- M1 `--lens <name>` restricts the listing to one spec, and refuses an unknown lens by naming the closed set — the same refusal shape `learn` and `fold` already use
- M2 `--since <date>` lists only deltas whose interval STARTS on or after that date
- M3 `--as-of <date>` reconstructs the listing as it stood on that date: a delta whose interval starts after it is excluded, one whose interval closed on or before it is excluded, and one open at that date is listed with the status it HELD THEN, never the status it holds today
- M4 the interval is half-open `[valid_from, valid_to)` — start inclusive, end exclusive — and the `--help` text says so, because a boundary the format does not state is one two readers will disagree about
- M5 a LEGACY undated delta under `--since`/`--as-of` is INCLUDED and MARKED, never silently dropped, and a footer names how many were shown — a filter that hides what it cannot judge reports a smaller number, and a smaller number reads as success
- M6 an unparseable `--since`/`--as-of` argument REFUSES and names the accepted form; it never falls back to today, and never treats the value as absent
- M7 a delta whose own recorded date is unreadable is REPORTED as `bad_date` in the malformed section and never date-defaulted — never epoch-zero, never today. AMENDED at Direction after the build: the first reading said 'treated as UNDATED and listed', which would have been a WEAKER guarantee than the grammar already gives. `parse_delta_head` classifies a bad date as malformed, so the line is named, quoted and counted in its own section rather than blended into a listing as merely unjudged. The rule's intent — an unreadable value never reads as a clean one — is met by the louder mechanism, and the check is re-aimed to assert THAT
- M8 the filters compose: `--lens` with `--since` or `--as-of` narrows on both axes
</must>
<reject>
- R:SILENT_DROP a time filter excluding a delta it could not date, without saying so -> "SILENT_DROP"
- R:TODAYFALLBACK an unreadable date argument or field resolving to the current date -> "TODAYFALLBACK"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1,S2 · the request does not say who reads a filtered listing; taking "the planning beat — SKILL.md now routes intake through `add deltas` before drafting a Task or Milestone, so the filters exist to make that read tractable rather than to serve a report" -> cost if wrong: filters tuned for reporting, not planning · probe: `--lens` and `--since` are the two a planner reaches for and both ship
- A2 [which] covers: S1,S2 · the request does not say which date field orders a delta; taking "`valid_from` for `--since` — when the lesson was FILED, which is what a planner means by recent; `valid_to` participates only in `--as-of`'s exclusion test" -> cost if wrong: `--since` silently means 'recently folded' · probe: a folded delta with an old start is absent from a recent `--since`
- A3 [when] covers: S1,S2 · the request does not say whether interval ends are inclusive; taking "half-open [from, to) — a delta folded ON date D was still asserted for D's predecessor and not for D, which is the only reading under which fold-then-ask-as-of-that-day is not double-counted" -> cost if wrong: an off-by-one at every boundary · probe: a delta folded exactly on the queried date is EXCLUDED
- A4 [absent] covers: S1,S2 · the request does not say what an absent date means; taking "unknown, never zero and never now — a legacy line is shown and marked under a time filter, and the count of such lines is stated" -> cost if wrong: silent loss from the inventory the loop plans against -> R:SILENT_DROP
- A5 [order] covers: S1,S2 · the request does not say how a filtered listing orders; taking "the existing order is preserved exactly — filename then file order — because this task adds a FILTER and any reorder would change output the current suites already pin" -> cost if wrong: churn in tests that are not about time
- A6 [experience] covers: S1,S2 · the request does not say who receives this; taking "an operator who has just been told by the skill to read the deltas before planning, and who needs to know when a listing is PARTIAL — so every filtered listing states what it filtered on, and a filter matching nothing says so rather than printing an empty success" -> cost if wrong: a planner reads a narrowed listing as the whole inventory · probe: the rendered header names the active filters

## PLAN
contract: `deltas()` gains `lens`, `since` and `as_of` parameters, all optional and defaulting to today's behaviour byte-for-byte; `cli.py` grows the three flags. Dates parse as ISO `YYYY-MM-DD` only — the format the grammar already writes.
scope: add-method/tooling/add.py · add-method/tooling/cli.py · add-method/tests/engine/test_deltas_time_filters.py

## EDGES
- E1 `--as-of` a date BEFORE every recorded delta — an empty listing that says so, never an error
- E2 a delta folded exactly ON the queried date — excluded, by M4's half-open rule
- E3 `--lens` naming a spec that exists but holds no deltas — an empty listing for that lens, distinct from an unknown lens

## CHECKS
- test_lens_filter_narrows_to_one_spec · covers: M1,M8 · one lens listed, others absent, and an unknown lens refuses by naming the closed set
- test_since_lists_only_intervals_that_start_on_or_after · covers: M2,A2 · a delta filed before the date is absent, one filed on it is present, and a FOLDED delta with an old start stays absent
- test_as_of_reports_the_status_held_then · covers: M3 · a delta folded today is listed as `open` when the query date precedes its close
- test_as_of_excludes_a_delta_closed_on_the_queried_date · covers: M4,E2,A3 · the half-open boundary, asserted at the exact date
- test_undated_deltas_are_shown_and_counted_never_dropped · covers: M5,R:SILENT_DROP,A4 · a legacy line appears under both filters, is marked, and the footer states how many
- test_an_unreadable_date_argument_refuses · covers: M6,R:TODAYFALLBACK · a garbage `--since` refuses, names the accepted form, and does not list as if unfiltered
- test_a_malformed_recorded_date_is_reported_not_defaulted · covers: M7,A4 · a broken date is named in the malformed section with its line quoted, is absent from the items list, and no date default is invented for it
- test_filters_compose_and_the_header_names_them · covers: M8,A6 · lens with as-of narrows on both, and the rendered header states the active filters
- test_as_of_before_everything_is_an_empty_listing_not_an_error · covers: E1 · exit 0 and a stated empty result
- test_a_lens_with_no_deltas_differs_from_an_unknown_lens · covers: E3 · an empty listing versus a refusal
- test_the_planning_flags_a_planner_reaches_for_are_wired · covers: A1 · A1's own probe: --lens/--since/--as-of are reachable from the CLI and the half-open boundary is stated in --help
- test_unfiltered_output_is_byte_identical · covers: A5 · no flags renders exactly what it renders today
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
