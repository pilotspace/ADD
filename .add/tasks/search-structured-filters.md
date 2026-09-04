---
type: Task
title: add search selects by field beside its free-text grammar, and an empty ask still refuses
status: direction
depth: standard
sensitivity: architecture
milestone: okf-graph-lookup
scope:
  - add-method/tooling/add.py
  - add-method/tooling/engine_pin.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - .add/tooling/add.py
  - add-method/.add/tooling/add.py
  - add-method/tooling/cli.py
  - add-method/src/add_method/_bundled/tooling/cli.py
  - .add/tooling/cli.py
  - add-method/.add/tooling/cli.py
  - add-method/FORMAT.md
  - add-method/docs/13-command-reference.md
  - add-method/tests/engine
gives:
  - S1 add.search(root, query, as_of, type, status, milestone) — three node-scoped filters beside the free-text grammar; `query` becomes optional and the refusal for an ask that names nothing survives
  - S2 cli.py `add search [QUERY] [--type T] [--status S] [--milestone M]` — the flags and the now-optional positional, plus the book command reference row that documents them
  - S3 the reported exclusion — when a node-scoped filter is present the note states how many delta hits it could not judge, so a smaller number never reads as success
generated: { by: add/3.4.0, at: 2026-09-04 }
verified:
  - { by: "plan:okf-graph-lookup", at: 2026-09-04, act: freeze, authority: plan, direction: "sha256:dc2db6a93c7901e3", binding: "sha256:bbab0c662dde5a9e" }
  - { by: "cli", at: 2026-09-04, act: brief, authority: process, brief: "sha256:01681d8ab0cfc026" }
  - { by: "plan:okf-graph-lookup", at: 2026-09-04, act: refreeze, authority: plan, direction: "sha256:dc2db6a93c7901e3", binding: "sha256:bbab0c662dde5a9e" }
  - { by: "cli", at: 2026-09-04, act: brief, authority: process, brief: "sha256:253bf559cef6b2f8" }
---
## CARD
goal: `add search` selects nodes by field as well as by substring, and an ask that names nothing still refuses.
why: `search` matches a literal substring and nothing else, so "every Task still in direction under this milestone" is unanswerable — the one question a planning loop actually asks. `status` and `todo` answer fixed slices; neither takes a field. The whole surface exists already; what is missing is a way to say WHICH nodes rather than WHAT TEXT.
beat: direction · next: add freeze search-structured-filters

## RULES
<must>
- M1 `--type`, `--status` and `--milestone` each select nodes by that frontmatter field, and two or more filters AND together
- M2 the positional query is OPTIONAL — a filter alone is a complete ask, and `add search --type Task` is valid with no query at all
- M3 an ask that names NOTHING — no query and no filter — still refuses with the existing `R:EMPTYQUERY`, unchanged
- M4 an off-taxonomy `--type` REFUSES and names the taxonomy it was checked against; it never returns zero hits as though nothing matched
- M5 `--milestone` accepts a bare slug or a full cid and treats them as one value, the way `_wave_slug` already does for `todo` and `wave`
- M6 when any node-scoped filter is present, delta hits are excluded — a delta carries no `type:` or `milestone:` and its status vocabulary is a different one — and the note REPORTS how many were excluded
- M7 with no filter given, the free-text grammar and `--as-of` behave exactly as they do today, byte for byte
</must>
<reject>
- R:SILENT_DROP a filter must never quietly remove a hit class from the count; an unreported exclusion reports a smaller number and a smaller number reads as success -> "SILENT_DROP"
- R:UNKNOWNCLEAN an unrecognised filter value must never read as a legitimate empty result — the shape that let an unknown `sensitivity:` degrade to the lowest floor (M24) -> "UNKNOWNCLEAN"
- R:REGRESS making the positional optional must not re-open `R:EMPTYQUERY`; an empty string with no filter is still a refusal -> "REGRESS"
- R:HIDDENTYPE `--type Run` must not silently return nothing because the free-text path excludes receipts; an explicit request for a type is not the blanket case that exclusion was written for -> "HIDDENTYPE"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 S2 S3 · n/a · every surface is a read over frontmatter already present; no stamp, no verdict, no authority floor consulted, no path to `done`
- A2 [which] covers: S1 · the request does not say which fields are filterable; taking `type`, `status` and `milestone` ALONE — the three the planning loop asks about and the three every node type carries or meaningfully lacks. `depth` and `sensitivity` are Task-only and were cut for having no cross-type meaning · probe: the three flags together answer "every Task still in direction under this milestone" in one call -> if wrong, the verb grows a flag per field and none of them compose
- A3 [which] covers: S2 · the request does not say which node types a `--type` may name; taking `add.ABF_TYPES`, the taxonomy the engine already publishes and the second oracle already mirrors, rather than a new list · found: ABF_TYPES is a tuple at add.py:5201 and validate_bundle.py:34 mirrors it -> if wrong, a fourth copy of the taxonomy joins the two that must already stay in lockstep
- A4 [which] covers: S3 · the request does not say which hit classes a filter judges; taking NODE hits only — a delta has no `type:` and no `milestone:`, and its open/folded/rejected vocabulary is not the node lifecycle -> if wrong, `--status done` silently means two different things depending on which half of the index answered
- A5 [when] covers: S1 S2 · the request does not say when an ask is empty enough to refuse; taking the boundary at NOTHING NAMED — a query or any one filter is an ask, and only the absence of both refuses -> if wrong, either a filter-only ask refuses or an empty ask answers with the whole bundle
- A6 [when] covers: S3 · the request does not say when the exclusion is reported; taking ALWAYS-WHEN-NONZERO, on the same line the `--as-of` unjudgeable count already uses, so one reader learns one convention -> if wrong, a second reporting convention appears for the same class of problem
- A7 [absent] covers: S1 · the request does not say what an absent `status:` means; taking it as NOT MATCHING any `--status` value — 135 of 220 nodes carry no status, so treating absent as a wildcard would return most of the bundle for every status query · found: measured on this bundle, absent 135 · done 91 · direction 5 · archived 1 -> if wrong, `--status done` returns 226 hits of which 135 have no status at all
- A8 [absent] covers: S2 · the request does not say what an absent filter means; taking it as NO CONSTRAINT on that field, so omitting a flag never narrows -> if wrong, a default value narrows silently and the unfiltered result is unreachable
- A9 [absent] covers: S3 · the request does not say what to report when nothing was excluded; taking SILENCE at zero, because a line reading "0 excluded" on every filtered search is noise that trains the reader to skip the line that matters -> if wrong, the one report that carries a real number is skipped with the rest
- A10 [order] covers: S1 · the request does not say what orders filtered hits; taking `search`'s existing total order UNCHANGED — filters remove rows, never reorder them -> if wrong, the same hit sits at a different rank depending on which flags were passed, and no two runs are diffable
- A11 [order] covers: S2 S3 · n/a · flag parsing is order-independent by argparse's contract, and the exclusion note is a single trailing line with nothing to order against
- A12 [experience] covers: S1 S2 · the receiver is the planning loop asking "what is still open here"; what would make it hard is a filter that answers zero without saying why, so an unmatched `--status` lists the statuses that DO exist in the bundle -> if wrong, a typo and an empty slice look identical and the reader retries the typo
- A13 [experience] covers: S3 · the receiver is a reader counting results; taking the wording already used for `--as-of`'s unjudgeable hits, so the two exclusions read as one convention rather than two features -> if wrong, the reader learns the convention twice and trusts neither

## PLAN
contract: `search(root, query, as_of=None, type=None, status=None, milestone=None)` keeps its `(hits, note)` shape and its total order. `query` defaults to None. The refusal ladder gains one rung ahead of `R:EMPTYQUERY`: an off-taxonomy `--type` refuses naming `ABF_TYPES`. When any of the three filters is set, the delta half of the index is skipped and the count of skipped hits is carried into the note. `--type Run` lifts the blanket receipt exclusion for that call only. `cli.py` makes `query` `nargs="?"` and adds the three flags.
strategy: write the checks first, including the two that pin TODAY's behaviour unchanged (M7), so the regression surface is red-proven before the filters land. Then the engine, then the CLI, then the book row.

## EDGES
- E1 `--type task` in lower case resolves to `Task`
- E2 `--type Run` returns Run nodes, which the free-text path otherwise excludes wholesale
- E3 a `--status` no node holds returns an empty list and a note naming the statuses that exist
- E4 `--milestone okf-graph-lookup` and `--milestone /milestones/okf-graph-lookup.md` return identical hits
- E5 a query AND a filter returns a subset of the same query with no filter
- E6 `--as-of` together with a node filter reports the delta exclusion once, and does not also report an unjudgeable-interval count for hits it already removed
- E7 an off-taxonomy `--type` refuses, and the refusal exits 1 while a zero-hit filtered search exits 0

## CHECKS
- test_each_filter_selects_by_its_field · covers: M1, A2 · each of the three flags alone returns exactly the nodes carrying that value, counted against the graph
- test_filters_and_together · covers: M1, E5 · type plus milestone returns the intersection, and it is a subset of either alone
- test_a_filter_alone_is_a_complete_ask · covers: M2, A5 · `search` with no query and one filter returns hits
- test_an_ask_that_names_nothing_still_refuses · covers: M3, R:REGRESS · no query and no filter returns None and the existing refusal code
- test_off_taxonomy_type_refuses_and_names_the_taxonomy · covers: M4, R:UNKNOWNCLEAN, E7 · a bogus type returns None and a note listing ABF_TYPES; a real type with no members returns []
- test_type_filter_is_case_insensitive · covers: E1 · lower case resolves to the canonical taxonomy form
- test_explicit_run_type_lifts_the_receipt_exclusion · covers: R:HIDDENTYPE, E2 · `--type Run` returns receipts, and an unfiltered search still does not
- test_milestone_accepts_a_slug_or_a_cid · covers: M5, E4 · both spellings return identical hits
- test_absent_status_never_matches · covers: A7 · a node with no `status:` is not returned by any `--status`
- test_delta_exclusion_is_reported · covers: M6, R:SILENT_DROP, A6 · a filtered search that removes delta hits states the number in the note
- test_no_exclusion_line_when_nothing_excluded · covers: A9 · an unfiltered search carries no exclusion line
- test_unmatched_status_names_what_exists · covers: A12, E3 · a zero-hit `--status` note lists the statuses present in the bundle
- test_unfiltered_search_is_unchanged · covers: M7, A10 · the hit list and note for a query with no filters are identical to the pre-change behaviour, pinned by value
- test_as_of_and_filter_do_not_double_report · covers: E6 · one exclusion line, not two counts of the same removed hits
red-first: every check MUST fail first.

## EVIDENCE
receipt: runs/n.md
gate: PASS | RISK-ACCEPTED | HARD-STOP

## LESSONS
- a lesson -> add learn lens
