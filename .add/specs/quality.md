---
type: Spec
title: Quality
lens: quality
project: AIDD-Book
generated: { by: add/3.0.0, at: 2026-08-08 }
delta_seq: 10
---
## Now
what counts as proof

## Decisions that bind
- <the first decision that constrains the rest>

## Deltas
- <what changed, and the evidence that changed it>
- [TDD · Q10 · open · 2026-09-03] A benchmark harness that copies the file under test between arms pays a bytecode-recompile tax on every run — 31ms for a 4731-line engine — which inflates both arms and flattens the ratio. Measure the instrument first: the same binary under two labels gave medians 21ms apart but mins within 0.1ms, so min is the statistic and median is noise. Three successive readings of one change gave -27%, -17% and -24%; only the last had a verified control. (evidence: /tasks/doctor-reads-each-body-once.md · interleaved A/B, warm .pyc both arms)
- [TDD · Q9 · open · 2026-09-01] The gate binds covers: referents by BARE test id, so a PARAMETRIZED check binds NOTHING — pytest reports it as test_x[param]. A green parametrized check can leave its rule unbound while reading as covered. A module name (test_tree_parity) binds nothing either; cite the real test function names. (evidence: /tasks/claimed-output-guard.md gate)
- [TDD · Q8 · open · 2026-09-01] A gate that cannot READ its input must refuse, never tally zero. Teaching the goal-gate to skip fenced blocks meant an unclosed fence emptied the tally, and `total == 0` takes the 'no exit criteria' branch — which CLOSES the milestone with unmet criteria in the file. (evidence: tests/engine/test_premerge_review_fixes.py)
- [TDD · Q7 · open · 2026-09-01] Never take a timestamp from the clock to compare against a filesystem. Flooring the clock to the second fixed the coarse-filesystem false-stale but blunted the check; a sentinel written on the SAME filesystem fixes it without losing any discrimination the filesystem offers. (evidence: tests/engine/test_premerge_review_fixes.py)
- [TDD · Q6 · open · 2026-08-28] Every capability a doc PROMISES is a test nobody wrote: the sentence "a box the AI ticked never reads as a human's" was false for two minor versions because no check bound prose to behaviour. (evidence: /tasks/sealed-gate-enforcement.md M6 · runs/2.md)
- [TDD · Q5 · open · 2026-08-12] A green suite is only evidence about the tests that RAN. The command that runs a subset must not produce output shaped like the command that runs everything — an uncollected suite reports as a smaller number, and a smaller number reads as success. (evidence: /tasks/partial-run-visible.md)
- [TDD · Q4 · open · 2026-08-12] an assumption is worth writing only if you will go DISPROVE it: A1 assumed the installers pass --profile through. Ten minutes of reading bin/cli.js showed its 'profile' is agent detection and the flag is ignored — with its value silently becoming the target directory. The assumption cost a shipped falsehood because it was recorded and then trusted rather than tested (evidence: .add/tasks/profile-refusal.md)
- [TDD · Q3 · open · 2026-08-12] a derived guard must distinguish a DEAD name from a LAZILY-CREATED one: probing with `init` alone made the corrected prose .add/tasks/<slug>.md fail beside the state.json it replaced. Drive the probe through a bundle that has been USED (init + first task), which still refuses names no sequence of verbs produces (evidence: add-method/tests/skill/test_front_door_truth.py)
- [TDD · Q2 · open · 2026-08-12] a 'must never contain X' check passes vacuously when the file is missing — assert existence FIRST or it rides into the freeze proving nothing (evidence: add-method/tests/skill/test_domains_recipe.py:32)
- [TDD · Q1 · folded · 2026-08-11→2026-08-11] the gate coverage map binds EVERY referent — probed A-lines and E-lines included; write covers: complete at Direction or the first gate refuses on rules your suite already proves (evidence: /tasks/explore-lane.d/runs/2.md)
