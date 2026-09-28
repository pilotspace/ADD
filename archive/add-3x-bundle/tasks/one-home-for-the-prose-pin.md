---
type: Task
title: the SKILL.md sha256 pin has one home, like the budgets
status: done
depth: standard
kind: test
milestone: checks-that-hold-in-ci
scope:
  - add-method/tests/skill/skill_budget.py
  - add-method/tests/skill/test_surface.py
  - add-method/tests/skill/test_skill_reads_the_graph.py
  - add-method/tests/skill/test_one_budget_one_guard.py
  - add-method/tests/skill/test_persona_load_by_fit.py
gives:
  - S1 where the skill-tree prose pins live and how a check reads one — the constant, its owner, and the re-aim record that travels with it
generated: { by: add/3.6.0, at: 2026-09-10 }
verified:
  - { by: "plan:checks-that-hold-in-ci", at: 2026-09-10, act: freeze, authority: plan, direction: "sha256:af1d53f4e2a58e7c", binding: "sha256:a046adc15422753b" }
  - { by: "plan:checks-that-hold-in-ci", at: 2026-09-10, act: refreeze, authority: plan, direction: "sha256:af1d53f4e2a58e7c", binding: "sha256:a046adc15422753b" }
  - { by: "cli", at: 2026-09-10, act: brief, authority: process, brief: "sha256:99061b5f37ae1192" }
  - { by: "process:run", at: 2026-09-10, act: run, authority: process, outcome: PASS, receipt: /tasks/one-home-for-the-prose-pin.d/runs/1.md }
  - { by: "cli", at: 2026-09-10, act: brief, authority: process, brief: "sha256:a2a68dc484d6159a" }
  - { by: "process:run", at: 2026-09-10, act: run, authority: process, outcome: PASS, receipt: /tasks/one-home-for-the-prose-pin.d/runs/2.md }
  - { by: "plan:checks-that-hold-in-ci", at: 2026-09-10, act: gate, authority: process, outcome: PASS, receipt: /tasks/one-home-for-the-prose-pin.d/runs/2.md, brief: "sha256:a2a68dc484d6159a" }
advised_by: engine-notary
---
## CARD
goal: the SKILL.md prose pin is a named constant in one module, imported by every check that reads it, so a re-aim is one edit and no check parses another check's source text
why: carried out of 3.6.0 as a known: the sha256 lives as a literal in `test_surface.py` and `test_skill_reads_the_graph.py` reads it back by REGEXING that file's source. That is the same shape `skill_budget.py` was built to kill — three modules that pinned each other's source text, so the number could only be re-pinned everywhere at once or nowhere (R:SILENTPIN)
beat: done · next: add status

## RULES
<must>
- M1 each prose pin is ONE named constant in `skill_budget.py`, the module that already exists to be the single home for a pinned fact about the skill surface
- M2 every check that needs a prose pin IMPORTS it; no check parses another check's source text to find a value
- M3 each pin carries the task that aimed it, the reason, and the prior hash — the record that already rides these pins does not get dropped in the move
- M4 the claims are unchanged: an edited SKILL.md or intake.md still turns red, and the re-aim record is still checked
</must>
<reject>
- R:SOURCESCRAPE a check recovers a value by reading another module's source text rather than importing it -> "SOURCESCRAPE"
- R:LOSTRECORD a pin arrives in its new home without the task, reason and prior hash it carried -> "LOSTRECORD"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the request does not say who owns the pin now; taking "`test_surface.py::test_skill_tree_prose_unedited_by_this_task` keeps owning the ASSERTION and `skill_budget.py` holds the VALUE — the same split the three budgets already use" -> a second module starts asserting the pin and the scatter is back in a new shape
- A2 [which] covers: S1 · the request does not say which pins move; taking "both in that dict — SKILL.md and intake.md. Moving one and leaving the other is the scatter with fewer members" · probe: no 64-hex literal for either file remains outside `skill_budget.py` -> half the fix ships and reads as done
- A3 [when] covers: S1 · the request does not say when a pin may move; taking "when a human deliberately edits the prose, in the same commit, with the reason — unchanged from today" -> the move is read as relaxing the pin
- A4 [absent] covers: S1 · the request does not say what a pin with no `prior:` means; taking "the first aim, which is legitimate and already how these read — so the record rung demands a task and a reason, and `prior:` only once one exists" · probe: the record rung passes on a first aim -> a newly added pin cannot satisfy a rung written for re-aims
- A5 [order] covers: S1 · the request does not say whether the value or the record is checked first; taking "independent rungs — a pin can be correct and unexplained, or explained and stale, and each is worth its own failure" -> one masks the other
- A6 [experience] covers: S1 · the request does not say how a re-aimer finds the pin; taking "the failure names the constant and its module by name, so the one edit is findable from the error alone" -> the author greps for a hex string, which is exactly the search that found seven of eight literals last time
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: `PROSE_PINS: dict[str, str]` in `skill_budget.py`, each value carrying its re-aim record in a trailing comment; `test_surface.py` and `test_skill_reads_the_graph.py` both import it.
strategy: widen `test_one_budget_one_guard.py`'s scatter rung to prose pins so the new home is enforced the same way the budgets are, then move the values, then delete the regex reader.

## EDGES
- E1 <a boundary or failure case a check must cover — optional>

## CHECKS
- test_one_module_owns_the_prose_pins · covers: M1, M2, A1, A2, R:SOURCESCRAPE · the hashes live in one module and no check regexes another check's source to find one
- test_the_prose_pins_kept_their_record · covers: M3, R:LOSTRECORD, A4, A5, A6 · each pin names the task that aimed it and its reason, and the failure names the constant to edit
- test_the_prose_claims_are_unchanged · covers: M4 · an edited SKILL.md still turns the owning guard red
red-first: every check MUST fail first.

## EVIDENCE
receipt: /tasks/one-home-for-the-prose-pin.d/runs/2.md · kind: test-ids · 254/254 reported · exit 0 · 2026-09-10
gate: PASS · authority process · by plan:checks-that-hold-in-ci · receipt /tasks/one-home-for-the-prose-pin.d/runs/2.md · 2026-09-10

## LESSONS
- [quality · Q35 · folded] A guard written broader than its rule goes red on true statements. `no budget literal moved` was implemented as `the module is byte-identical`, so adding an unrelated constant to it reported a pin bump that never happened. (evidence: /tasks/one-home-for-the-prose-pin.md)
