---
type: Task
title: A filename that names a node resolves to it, and an ambiguity refusal is bounded
status: direction
depth: standard
milestone: walk-truth
scope:
  - add-method/tooling/add.py
  - add-method/tooling/engine_pin.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - .add/tooling/add.py
  - add-method/.add/tooling/add.py
  - add-method/tests/engine

gives:
  - S1 add.resolve_ref(root, ref) — a filename that names exactly one node resolves to it, instead of refusing a node that exists
  - S2 add.resolve_ref's ambiguity refusal — bounded the way the depth cap is bounded, so one refusal cannot cost unbounded context
generated: { by: add/3.4.0, at: 2026-09-04 }
verified:
  - { by: "plan:walk-truth", at: 2026-09-04, act: freeze, authority: plan, direction: "sha256:bd115d6c3166394d", binding: "sha256:bd1235c2e1600e93" }
  - { by: "cli", at: 2026-09-04, act: brief, authority: process, brief: "sha256:ab36281547583439" }
---
## CARD
goal: a name an operator actually types resolves, and the refusal that lists alternatives is bounded.
why: two defects found by review. `resolve_ref` routes anything ending `.md` to the cid branch with no fallback, so `add show okf-graph-lookup.md` refuses a node that exists — and tab-completing a filename is the likeliest way to type it. The refusal asserts something false about the bundle, which is the exact failure the function's own docstring says it was written to end. Separately, the ambiguity refusal lists every candidate uncapped: `add show 1` prints 78 lines and grows with the task count, on a verb whose sibling path is capped precisely so one read cannot cost unbounded context.
beat: direction · next: add freeze ref-resolution-accepts-what-an-operator-types

## RULES
<must>
- M1 a bare filename that names exactly one node resolves to that node
- M2 a filename naming no node still refuses, and the refusal is the one a reader can act on
- M3 the ambiguity refusal lists at most a bounded number of candidates and says how many more there are
- M4 the bound is a named constant, stated once, and pinned BY VALUE outside the module that declares it
- M5 the cid branch is unchanged for a ref that already resolved before this task
</must>
<reject>
- R:FALSEREFUSAL a refusal must never assert that a node does not exist when it does -> "FALSEREFUSAL"
- R:GUESSAGAIN a filename matching several nodes must still refuse and list them, never pick one -> "GUESSAGAIN"
- R:UNBOUNDED a refusal must not grow without limit with the size of the bundle -> "UNBOUNDED"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 S2 · n/a · read-only ref resolution; no stamp, no floor, no write path, no authority
- A2 [which] covers: S1 · the request does not say which filenames fall back; taking one with NO `/` in it — a value carrying a separator is a path the operator meant literally, and second-guessing it would reopen the guessing this verb refuses · probe: `resolve_ref` already splits its two branches on `"/" in text or text.endswith(".md")` -> if wrong, a real path silently resolves to a same-named node elsewhere
- A3 [which] covers: S2 · the request does not say which candidates are shown; taking the FIRST n of the existing sorted order, so the list stays deterministic and the `next:` line keeps naming a real one -> if wrong, the shown subset varies between runs and the refusal is not reproducible
- A4 [when] covers: S1 · the request does not say when the fallback runs; taking AFTER the cid branch misses — a ref that resolves today must resolve identically tomorrow (M5), so the fallback only ever adds answers, never changes one -> if wrong, this task changes what an existing caller gets back
- A5 [when] covers: S2 · the request does not say when the count line appears; taking ONLY when candidates were withheld, so a refusal that fits says nothing about truncation -> if wrong, every ambiguity refusal carries a line about hiding nothing
- A6 [absent] covers: S1 · the request does not say what an empty or whitespace ref is; taking the refusal that exists today, unchanged — a ref naming nothing is already its own message -> if wrong, an empty ref falls into basename matching and matches everything
- A7 [absent] covers: S2 · the request does not say what happens below the bound; taking the full list with no count line, exactly as today -> if wrong, the common case grows a line it does not need
- A8 [order] covers: S1 S2 · the request does not say what orders candidates; taking the existing sorted cid order, unchanged, so a truncated list is the deterministic prefix of the full one -> if wrong, truncation and ordering interact and two runs show different candidates
- A9 [experience] covers: S1 · the receiver is an operator who tab-completed a filename; what would make it hard is being told the node does not exist, so the fallback answers rather than refusing -> if wrong, the likeliest input stays the one that fails
- A10 [experience] covers: S2 · the receiver is an agent paying context for every line; what would make it hard is 78 candidates, so the refusal shows a usable few and counts the rest -> if wrong, the refusal costs more than the read it replaced

## PLAN
contract: `resolve_ref` tries the cid branch first; when it misses and the ref carries no `/`, it falls back to basename matching against `<ref>` and `<ref>.md`. The ambiguity refusal lists at most `RESOLVE_CANDIDATES` candidates and appends a count of those withheld.
strategy: write the false-refusal check against the LIVE shape first — `okf-graph-lookup.md` names a real node — and the bound check against a fixture that exceeds it, so both are red for the defect and not for the fixture.

## EDGES
- E1 a filename naming exactly one node resolves
- E2 a filename naming several nodes refuses and lists them
- E3 a filename naming no node still refuses
- E4 a ref containing `/` is treated as a path, never as a basename
- E5 an ambiguity with more candidates than the bound is truncated and counted

## CHECKS
- test_a_filename_that_names_one_node_resolves · covers: M1, R:FALSEREFUSAL, E1 · a cid's own basename with `.md` resolves to that cid
- test_a_filename_naming_several_still_refuses · covers: R:GUESSAGAIN, E2 · several matches refuse and the note lists candidates
- test_a_filename_naming_nothing_still_refuses · covers: M2, E3 · an unknown filename refuses and names its fix
- test_a_ref_with_a_separator_is_a_path · covers: A2, E4 · a ref containing `/` never falls back to basename matching
- test_the_candidate_list_is_bounded · covers: M3, R:UNBOUNDED, E5, A5 · more candidates than the bound yields a truncated list and a count of the rest
- test_the_bound_is_pinned_by_value · covers: M4 · the constant equals a literal this check states, not one it reads from the engine
- test_refs_that_resolved_before_resolve_the_same · covers: M5, A4 · a bare slug and a full cid return exactly what they returned before
red-first: every check MUST fail first.

## EVIDENCE
receipt: runs/n.md
gate: PASS | RISK-ACCEPTED | HARD-STOP

## LESSONS
- a lesson -> add learn lens
