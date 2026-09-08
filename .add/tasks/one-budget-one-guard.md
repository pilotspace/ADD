---
type: Task
title: one budget, one guard
status: done
depth: quick
milestone: rules-that-hold-for-us
scope:
  - add-method/tests/skill/skill_budget.py
  - add-method/tests/skill/test_one_budget_one_guard.py
  - add-method/tests/skill/test_surface.py
  - add-method/tests/skill/test_uncertainty_routing.py
  - add-method/tests/skill/test_domains_recipe.py
  - add-method/tests/skill/test_skill_reads_the_graph.py
  - add-method/tests/skill/test_edges_documented.py
  - add-method/tests/skill/test_quick_lane_size_gate.py
  - add-method/tests/skill/test_explore_lane.py
  - add-method/tests/skill/test_receipt_idiom_truth.py
  - add-method/tests/test_front_door_claim_truth.py
  - add-method/tests/engine/test_check_verb.py
  - add-method/tests/skill/test_search_registry.py
  - add-method/tests/skill/test_skill_reads_the_graph.py
  - add-method/tests/skill/test_skill_profile_truth.py
gives:
  - S1 tests/skill/skill_budget.py — the one module holding SKILL.md's line, byte and surface budgets, and the one guard that asserts them
generated: { by: add/3.5.0, at: 2026-09-08 }
verified:
  - { by: "plan:rules-that-hold-for-us", at: 2026-09-08, act: freeze, authority: process, direction: "sha256:9e1a493a990b9a13", binding: "sha256:e9a79d98e3503d91" }
  - { by: "plan:rules-that-hold-for-us", at: 2026-09-08, act: refreeze, authority: process, direction: "sha256:9e1a493a990b9a13", binding: "sha256:e9a79d98e3503d91" }
  - { by: "plan:rules-that-hold-for-us", at: 2026-09-08, act: refreeze, authority: process, direction: "sha256:9e1a493a990b9a13", binding: "sha256:e9a79d98e3503d91" }
  - { by: "builder", at: 2026-09-08, act: replan, authority: process, note: "A4's reading does not survive M2. It said test_front_door_claim_truth should keep asserting EQUALITY to the pin while sourcing the constant — but `n == LINE_BUDGET` still asserts the budget, so a one-line overrun would report TWO failures, not one. The check's real subject is that the three skill trees agree with EACH OTHER; that is what it now asserts, and the budget stays the owner's alone." }
  - { by: "builder", at: 2026-09-08, act: replan, authority: process, note: "A2's count was low, and the shape is worse than the exit imagined. Four more modules carry the budget as their OWN module-level constant (LINE_PIN/LINE_BUDGET = 176), which no literal-in-assert scan can see — and three of them then pin each other's SOURCE TEXT: test_skill_profile_truth regex-scrapes 'n <= (\\d+)' out of test_surface.py, and test_quick_lane_size_gate pins that scrape. A web of source-text pins on one number. All of it collapses to reading skill_budget.LINE_BUDGET; the 'the pin was not moved' rule is exactly what test_one_module_owns_the_budgets already asserts, once, in the owner. The meta-check is strengthened to flag a module-level ASSIGNMENT of a budget value, not only a literal inside an assert." }
  - { by: "plan:rules-that-hold-for-us", at: 2026-09-08, act: refreeze, authority: process, direction: "sha256:9e1a493a990b9a13", binding: "sha256:e9a79d98e3503d91" }
  - { by: "cli", at: 2026-09-08, act: brief, authority: process, brief: "sha256:4a0aefdf6eb84bc4" }
  - { by: "process:run", at: 2026-09-08, act: run, authority: process, outcome: PASS, receipt: /tasks/one-budget-one-guard.d/runs/1.md }
  - { by: "plan:rules-that-hold-for-us", at: 2026-09-08, act: gate, authority: process, outcome: PASS, receipt: /tasks/one-budget-one-guard.d/runs/1.md, brief: "sha256:534ff1e7d0bb37aa" }
---
## CARD
goal: the skill budget lives in one module and is asserted by one guard, so a one-line overrun reports one failure and is re-pinned in one place
why: SKILL.md went one line over its 176-line pin and FOURTEEN checks across seven files reported it. Fourteen failures for one fact — and re-pinning the budget means finding all eight literals, so the number drifts the first time someone finds only seven
beat: done · next: add status

## RULES
<must>
- M1 the budgets live in ONE module — a line budget, a byte budget and a whole-surface budget, each a single literal that a re-pin edits once
- M2 exactly ONE check asserts the SKILL.md line budget; an overrun reports one failure, not fourteen
- M3 every other check keeps its own subject and stops asserting the budget incidentally — a lane check proves the lane is documented, not that the file is short
- M4 the budget's rationale — human-set, re-pinned from 150 at 3.1.0 — travels with the literal, so a re-pinner sees why the number is what it is
- M5 a meta-check enumerates the suite and refuses a budget literal asserted anywhere but the owning guard
</must>
<reject>
- R:SCATTERED the same budget number is asserted in more than one module, so an overrun reports once per module -> "SCATTERED"
- R:SILENTPIN a budget is re-pinned in some modules and not others, leaving two live numbers and no error -> "SILENTPIN"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the request does not say who re-pins the budget; taking "a human, deliberately, at a release — so the literal carries its rationale and its history inline (M4), the way engine_pin.py already does for ENGINE_MD5" -> the next re-pinner changes a number with no idea what it was protecting
- A2 [which] covers: S1 · the request does not say which numbers are in; taking "all three that gate the skill surface — the 176-line pin, the 13258-byte pin, and the 1500-line whole-tree budget" · found: 176 appears in 8 assertions across 7 files, 1500 in 2, 13258 in 1 (evidence: grep -rn over add-method/tests) -> a second scattered budget is left behind and the meta-check goes red immediately
- A3 [when] covers: S1 · the request does not say when a check may still MENTION a budget; taking "a check may read the constant to compute something (a remaining-headroom message), but only the owning guard may ASSERT it" -> every incidental mention is rewritten and checks lose useful context
- A4 [absent] covers: S1 · the request does not say what test_front_door_claim_truth's `n == 176` means; taking "it is a PARITY check, not a budget check — it proves the three skill trees are byte-identical, and equality to the pin is how it says so; it sources the number from the module and keeps asserting equality" -> a real parity guard is deleted as a duplicate and three trees drift apart unnoticed
- A5 [order] covers: S1 · the request does not say what happens if the owning guard is deleted; taking "the meta-check requires the owner to exist by name, so removing it turns the meta-check red rather than leaving the budget unguarded" -> the last assertion is deleted and every module is compliant with nothing enforcing anything
- A6 [experience] covers: S1 · the request does not say what an overrun should say; taking "the one failure reports the current count, the budget, the overage, and the instruction to fund the add by compressing — the guidance the fourteen messages carried between them" -> the surviving message is terser than the fourteen it replaced and the reader loses the fix

## PLAN
contract: `tests/skill/skill_budget.py` holds `LINE_BUDGET = 176`, `BYTE_BUDGET = 13258` and `SURFACE_BUDGET = 1500`, each with its rationale inline. `test_surface.py::test_router_within_line_budget` is the sole asserter of the line budget; the other nine assertions are removed and their checks keep their own subjects. `test_front_door_claim_truth` keeps its equality assertion but sources the number (A4). A meta-check walks the suite's AST and refuses a budget literal in any assert outside the owning module.
strategy: the meta-check first, so it names its own offenders; then strip them.

## EDGES
- E1 the self-pin at test_surface.py:132 asserts the literal string `n <= 176` is present in its own source — it must be re-aimed at the constant, or it pins a line that no longer exists
- E2 a check that READS the budget to build a message but does not assert it — allowed (A3), and the meta-check must not flag it
- E3 the meta-check's own source names the budget numbers in prose and in its offender list — it must not flag itself
- E4 the byte budget (13258) and the surface budget (1500) move to the module too, or the task fixes one scatter and leaves two

## CHECKS
- test_one_module_owns_the_budgets · covers: M1, M4, E4, A2 · the three literals live in skill_budget.py, each carrying its rationale, and no other module defines them
- test_only_one_guard_asserts_the_line_budget · covers: M2, M5, R:SCATTERED, A5, E2, E3 · the meta-check: exactly one assert of the line budget in the suite, in the named owner, which must exist
- test_an_overrun_reports_once_and_says_how_to_fix_it · covers: M2, A6, R:SILENTPIN · a SKILL.md one line over budget produces exactly one failure, naming count, budget, overage and the fix
- test_the_other_checks_keep_their_own_subject · covers: M3, E1, A4 · the nine stripped checks still prove what they were written for, and the self-pin now pins the constant
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
