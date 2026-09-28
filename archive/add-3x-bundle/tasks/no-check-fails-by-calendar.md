---
type: Task
title: the search-filter suite pins its clock and still catches the regression
status: done
depth: quick
milestone: rules-that-hold-for-us
scope:
  - add-method/tests/engine
gives:
  - S1 a fixed clock for the search-filter fixture, so every date-dependent assertion in that suite reads the same on any run date
generated: { by: add/3.5.0, at: 2026-09-08 }
verified:
  - { by: "plan:rules-that-hold-for-us", at: 2026-09-08, act: freeze, authority: plan, direction: "sha256:3bd5c0567a83a3af", binding: "sha256:e5b452bc7893cc45" }
  - { by: "cli", at: 2026-09-08, act: brief, authority: process, brief: "sha256:5ba73203677d4df8" }
  - { by: "process:run", at: 2026-09-08, act: run, authority: process, outcome: PASS, receipt: /tasks/no-check-fails-by-calendar.d/runs/1.md }
  - { by: "plan:rules-that-hold-for-us", at: 2026-09-08, act: gate, authority: process, outcome: PASS, receipt: /tasks/no-check-fails-by-calendar.d/runs/1.md, brief: "sha256:34baf272d6e85e0f" }
---
## CARD
goal: the suite has no check that passes or fails because of what day it is run
why: `add.learn` stamps `valid_from` with today, and `test_as_of_and_filter_do_not_double_report` asks `as_of="2026-09-04"`. On the day it was written the fixture's delta was inside that window; it is now outside, the exclusion line differs, and the check has failed on main every day since. A check that fails by calendar is not a check — it trains everyone reading CI to ignore one red line, which is how the next real one is missed.
beat: done · next: add status

## RULES
<must>
- M1 the fixture's clock is FIXED, so `valid_from` on its delta and the `as_of` the checks ask for move together and neither drifts with the run date
- M2 the check still fails when the defect it names returns — an `--as-of` exclusion line double-reporting hits the type filter already removed
- M3 no assertion is loosened: the same exclusion-line count and the same delta-tier assertion hold
</must>
<reject>
- R:DATEFREE the fix must never be a loosened assertion that passes on every date because it asserts less -> "DATEFREE"
- R:CLOCKLEAK the fixed clock must never leak past this suite into another module's view of today -> "CLOCKLEAK"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the request does not say who owns the clock; taking the reading that the FIXTURE owns it and pins it for its own module only, never a global or a session fixture -> a clock pinned wider would silently change what every other suite believes today is (this is R:CLOCKLEAK)
- A2 [which] covers: S1 · the request does not say which date to pin; taking the reading that it is the date the fixture's own data is written on, so the `as_of` literal already in the file keeps its meaning rather than being renumbered · probe: the pinned clock equals the `as_of` the checks already ask for
- A3 [when] covers: S1 · the request does not say when the clock applies; taking the reading that it applies for the whole fixture build and is released before the checks run, because the checks read data and do not write it -> a clock still held during assertions would hide a real dependency on today
- A4 [absent] covers: S1 · the request does not say what happens if the engine stops calling `_today()`; taking the reading that the pin then simply has no effect and the checks still hold, because they assert on the DATA the fixture wrote, never on the patch itself · probe: the checks pass against data whose dates are read back from the fixture
- A5 [order] covers: S1 · n/a — a clock is one value for the whole fixture; there is no sequence in it to order
- A6 [experience] covers: S1 · the receiver is whoever next sees this suite go red, and what would make it hard is a fixed date with no stated reason; taking the reading that the pin carries a comment naming the failure it ends · probe: the pin is accompanied by a comment naming the calendar dependency

## PLAN
contract: the `bundle` fixture pins `add._today` to the date the suite's `as_of` literals already name, for the duration of the fixture build only. No assertion changes. One new check proves the regression the original guard was written for is still caught, by constructing the double-report condition directly.

## EDGES
- E1 the suite passes when run on a date far after the pinned one
- E2 the double-report defect, reintroduced, still fails the check

## CHECKS
- test_as_of_and_filter_do_not_double_report · covers: M1, M3, A2, A3, E1 · the existing guard, now clock-pinned, holds with its assertions unchanged
- test_the_exclusion_guard_still_catches_its_defect · covers: M2, R:DATEFREE, A4, A6, E2 · a search whose as_of removes hits the type filter did NOT remove still produces exactly one exclusion line, and the pin carries a comment naming the calendar dependency
- test_the_clock_pin_does_not_leak · covers: R:CLOCKLEAK, A1 · `add._today()` outside this fixture returns the real date
red-first: every check MUST fail first.

## EVIDENCE
receipt: /tasks/no-check-fails-by-calendar.d/runs/1.md · kind: test-ids · 16/16 reported · exit 0 · 2026-09-08
gate: PASS · authority process · by plan:rules-that-hold-for-us · receipt /tasks/no-check-fails-by-calendar.d/runs/1.md · 2026-09-08

## LESSONS
- pending
- none filed — no lesson cites /tasks/no-check-fails-by-calendar.md (add learn <lens> "<lesson>" --evidence /tasks/no-check-fails-by-calendar.md)
