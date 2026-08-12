---
type: Task
title: SKILL.md — profile truth + the write-a-checker pointer
status: done
depth: standard
milestone: all-domain-evidence
scope:
  - add-method/skill/add
  - add-method/src/add_method/_bundled/skill/add
  - .claude/skills/add
  - add-method/tests/skill
gives:
  - S1 the profile line — what `init` actually ships, in the always-loaded router
  - S2 the write-a-checker pointer — the sentence that makes `domains.md` reachable at all
generated: { by: add/3.1.0, at: 2026-08-12 }
verified:
  - { by: "Tin Dang", at: 2026-08-12, act: freeze, authority: human, direction: "sha256:82a8e13c6cd6e323" }
  - { by: "cli", at: 2026-08-12, act: brief, authority: process, brief: "sha256:d78a71de5c6fb0f1" }
  - { by: "process:run", at: 2026-08-12, act: run, authority: process, outcome: PASS, receipt: /tasks/skill-pointer-truth.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-08-12, act: gate, authority: process, outcome: PASS, receipt: /tasks/skill-pointer-truth.d/runs/1.md, brief: "sha256:d78a71de5c6fb0f1" }
---
## CARD
goal: an agent learns from the always-loaded router that it may WRITE a checker, and is never told to pass a profile the engine does not ship
why: `domains.md` shipped last task and NOTHING names it — SKILL.md lists 12 refs and that is not one of them, so no agent will ever load it. Its ten bound checks proved it correct, mirrored and in budget; none asked whether it was reachable.
beat: done · next: add status

## RULES
<must>
- M1 SKILL.md must name only profiles the engine ships — the `<code|doc|…>` ellipsis promises more than `init` has, and `init` silently falls back to `code` on anything else
- M2 every ref file in the skill tree must be named by SKILL.md — an orphan ref is unreachable and cannot do the job it was written for, whatever its contents prove
- M3 the Verify beat must tell an agent that when no runner exists for the domain it may WRITE one, and point at `domains.md`
</must>
<reject>
- R:BUDGETBUST landing the pointer by breaking a pin — SKILL.md over 176 lines or the surface over 1500 -> "BUDGETBUST"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · n/a · the router is read identically by every agent; no actor distinction
- A2 [which] covers: S1 · the request does not say whether to name the profiles or drop the list; taking "name both explicitly — an honest short list beats an ellipsis that implies a menu" -> if wrong, a reader invents `--profile finance` and gets code lenses under a finance label
- A3 [when] covers: S1 · n/a · the line is read at orientation, always, with no ordering question
- A4 [absent] covers: S1 · the request does not say what a reader should do when no profile fits; taking "`doc` is the non-code default and `domains.md` carries the re-author table" -> if wrong, the ellipsis is merely replaced by a dead end
- A5 [order] covers: S1 · n/a · two profiles, no precedence
- A6 [who] covers: S2 · n/a · same router, same readers
- A7 [which] covers: S2 · the request does not say which refs the orphan rule binds; taking "every `.md` in the skill tree except the nested `persona-author/` sub-skill, which is loaded on its own terms — the same carve-out `_own_docs()` already makes" -> if wrong the check fights an existing, deliberate exemption
- A8 [when] covers: S2 · n/a · reachability is a static property of the tree
- A9 [absent] covers: S2 · the request does not say what happens to a ref deliberately not surfaced; taking "there is no such thing — an unreferenced ref is dead weight against the surface pin, so it is named or it is deleted" -> if wrong, a legitimate private ref gets forced into the router and costs budget
- A10 [order] covers: S2 · n/a · refs are named in whatever order reads best

## PLAN
contract: two edits to the always-loaded router, plus a generalised orphan-ref guard that would have caught last task's miss
strategy: the orphan check is the real deliverable — it is `test_every_wired_verb_is_documented` one level up. That test already guards the ORPHAN direction for VERBS (a verb the engine ships that no doc names); nothing guarded it for REFS, which is exactly how `domains.md` shipped unreachable. Fund the added lines by compressing, never by raising a pin.
scope: add-method/skill/add, add-method/src/add_method/_bundled/skill/add, .claude/skills/add, add-method/tests/skill

## EDGES
- E1 `persona-author/` is a nested sub-skill with its own budget — the orphan rule must exempt it exactly as `_own_docs()` does, or it forces a private tree into the router

## CHECKS
- test_router_names_only_shipped_profiles · covers: M1 · every profile SKILL.md names is one PROFILES ships, and no ellipsis implies more
- test_no_orphan_refs · covers: M2 · every ref in the skill tree is named by SKILL.md
- test_router_points_at_the_checker_recipe · covers: M3 · the Verify beat names domains.md and says a checker may be written
- test_router_within_line_budget · covers: R:BUDGETBUST · SKILL.md stays within its 176-line pin
- test_total_surface_within_budget · covers: R:BUDGETBUST · the surface stays within 1500
- test_orphan_rule_exempts_nested_subskill · covers: E1 · persona-author/ is not forced into the router
- test_skill_bundle_matches_canonical · covers: M2 · package payload tree matches canonical
- test_dogfood_skill_matches_canonical_when_present · covers: M2 · dogfood mirror matches canonical
red-first: THREE are driven red — M1, M2 and M3 all fail against today's router (the ellipsis is there, domains.md is orphaned, no checker sentence exists). The rest are guards, declared: R:BUDGETBUST's two are the EXISTING pins (they go red only if the edit overspends, which is their job), E1's asserts an exemption that must survive the new rule, and the two parity tests catch a missed tree.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
