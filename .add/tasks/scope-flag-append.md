---
type: Task
title: repeated --scope flags append — a CLI argument is never silently dropped
status: done
milestone: v3-final-collateral
scope:
  - add-method/tooling/cli.py
  - add-method/tests/engine/test_scope_append.py
gives:
  - S1 `add new --scope` — repeatable, each occurrence appended, comma form still splitting
  - S2 `tests/engine/test_scope_append.py` — the suite pinning both forms and their composition
generated: { by: add/3.0.0, at: 2026-08-11 }
verified:
  - { by: "human:tindang", at: 2026-08-11, act: freeze, authority: process, direction: "sha256:0ce637278a109155" }
  - { by: "cli", at: 2026-08-11, act: brief, authority: process, brief: "sha256:ea95656764123a83" }
  - { by: "process:run", at: 2026-08-11, act: run, authority: process, outcome: PASS, receipt: /tasks/scope-flag-append.d/runs/1.md }
  - { by: "human:tindang", at: 2026-08-11, act: gate, authority: process, outcome: PASS, receipt: /tasks/scope-flag-append.d/runs/1.md, brief: "sha256:ea95656764123a83" }
---
## CARD
goal: `add new Task x --scope a.py --scope b.py` records both paths, in order — and `--scope a.py,b.py` keeps working
why: scratch-build finding (slugline, published 3.0.0b2 wheel) — the second flag silently replaced the first, and a fresh adopter's first node shipped with half its scope; silent argument loss is the exact papercut class hour-one users hit
beat: done · next: add status
## RULES
<must>
- M1 repeated `--scope` occurrences accumulate in command-line order
- M2 the documented comma form still splits, and composes with repetition
</must>
<reject>
- R:LASTWINS a repeated flag silently dropping earlier values -> "LASTWINS"
</reject>
## ASSUMPTIONS
- A1 [who] covers: S1,S2 · the request does not say which flags get this treatment; taking "`--scope` only — the one list-valued field `new` wires; other flags are scalars where last-wins is argparse convention" -> cost if wrong: another list flag added later repeats the bug · probe: `--scope` is the only `new` flag carrying plural help text
- A2 [which] covers: S1,S2 · the request does not say whether blanks survive; taking "empty chunks from stray commas are dropped, whitespace trimmed" -> cost if wrong: a `scope:` entry of ''
- A3 [when] covers: S1,S2 · the request does not say when splitting happens; taking "at dispatch, before the engine — `add.new` keeps receiving a plain list, its signature untouched" -> cost if wrong: an engine-level parse leaks into every caller
- A4 [absent] covers: S1,S2 · the request does not say what no flag means; taking "unchanged: scope omitted entirely, Task scaffold behavior untouched" -> cost if wrong: an empty scope list where none was declared
- A5 [order] covers: S1,S2 · the request does not say ordering across forms; taking "strict command-line order, commas expanding in place" -> cost if wrong: cosmetic reorder of the freshness set only
## PLAN
contract: `action="append"` on the flag plus a flatten-split at dispatch; the engine sees the same list shape it always did
scope: add-method/tooling/cli.py · add-method/tests/engine/test_scope_append.py
## EDGES
- E1 both forms mixed in one command (`--scope a.py --scope b.py,c.py`) — three entries, in order
## CHECKS
- test_repeated_scope_flags_append · covers: M1,R:LASTWINS · two flags, two entries, in order
- test_comma_form_still_splits · covers: M2 · the documented form is untouched
- test_mixed_flags_and_commas_compose · covers: M2,E1 · repetition and commas expand in place
- test_scope_is_the_only_plural_flag · covers: A1 · the probe: no other `new` flag advertises plural values
red-first: every check MUST fail first.
## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>
## LESSONS
- <lesson> -> add learn <lens>
