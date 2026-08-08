# MILESTONE: Complete, well-positioned scope drafting

goal: Scope-drafting yields a complete, correctly-positioned MILESTONE.md — the guide covers the whole template shape (with a draft well-formedness gate) and requires grounding the goal in current assets + the milestone map before the goal sentence is drafted.
rationale: new-major — a method-quality theme no active milestone's goal covers; surfaced when installer-smarts was drafted "incomplete before digest into task" (scope.md is silent on 3 of the template's 9 sections and prescribes no goal-positioning step). Improving the scope-drafting GUIDE, not any frozen contract.
stage: mvp · status: active · created: 2026-06-18

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

## Scope
In:  E1 — scope.md's section-by-section covers ALL 9 template sections: adds `rationale`,
     and states that `Close — ship review` + `Release steps` are drafted-BLANK (owned by the
     close/release flows), plus a draft well-formedness gate (a checklist a draft passes before
     it is proposed). E2 — a new first step "Position the goal": ground the goal in current
     assets (PROJECT.md · code · docs) AND cross-reference every existing+archived milestone
     goal to capture the relationship (extends / depends-on / overlaps / duplicates), recorded
     in `rationale`; a new `duplicate_goal` reject. Landed in all 3 scope.md parity trees.
Out: No engine (add.py) change — guide/convention only. No new add.py command to dump milestone
     goals (the step greps `.add/milestones/*` + `.add/archive/*`). No change to MILESTONE.md.tmpl
     itself (the template is already complete; the GUIDE is what drifted). No book chapter rewrite
     beyond a minimal accord touch if docs/ describes scope drafting. installer-smarts is untouched
     (resumed after this).

## Shared decisions & glossary deltas   (living — every task must honor these)
- 3-tree scope.md parity — dogfood (`.claude/skills/add`) · packaged (`add-method/skill/add`) ·
  pip bundle (`add-method/src/add_method/_bundled/skill/add`) stay byte-identical (md5-equal).
- the guide must pass `wording-lint` (no bare status/process slang; backtick lifecycle terms).
- "Position the goal" is the FIRST move of scope drafting (before Diverge) — you cannot draft a
  good goal sentence without knowing where it sits in the asset + milestone map.

## Shared / risky contracts (freeze these first)
- scope.md structural seam (the new step heading + `duplicate_goal` reject token + the 9-section
  coverage + 3-tree parity) -> owning task scope-complete-position

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] scope-complete-position   depends-on: none   — Rewrite scope.md for full-template coverage (E1) + the Position-the-goal step & duplicate_goal reject (E2), across all 3 parity trees; pin with a structure+parity test.

## Exit criteria (observable; map each to the task that delivers it)
- [x] scope.md's drafting section names all 9 template sections, marks Close/Release as drafted-blank, and carries a draft well-formedness gate   (← scope-complete-position)
- [x] scope.md has a "Position the goal" step (assets + cross-milestone relationship) as the first move, and a `duplicate_goal` reject code   (← scope-complete-position)
- [x] all 3 scope.md copies are md5-equal and the suite (wording-lint + the new structure test) is green   (← scope-complete-position)

## Close — ship review   (AI fills when every task is done — the evidence behind the engine gate, read before the boxes are checked)
> Whole-milestone, cross-task review the AI fills in. It is the evidence behind the EXISTING engine
> gate (milestone-done / checking the Exit-criteria boxes) — NOT a new approval. Tool-agnostic.

### Ship by domain   (what changed, per bounded context)
- tooling : `test_scope_loop.py` +5 assertions (frozen tokens · Position-the-goal is first · 9-section coverage · Close/Release drafted-blank · well-formedness gate) + a `_bundled` scope path; `add.py` untouched (ENGINE_MD5 holds).
- skill   : `scope.md` rewritten across all 3 parity trees — a "Position the goal" FIRST step (ground in assets + cross-reference every active+archived milestone goal), 9-section coverage, a Close/Release drafted-blank note, a draft well-formedness gate, and a `duplicate_goal` reject. md5-equal across dogfood · canonical · pip bundle.
- book    : untouched — book-accord honestly SKIPPED: no `docs/` chapter enumerates the milestone scope-drafting steps; `scope.md` is the source (the book covers task-level co-specify in docs/03).

### Cross-task evidence   (one row per task)
- scope-complete-position : gate=PASS · tests=1276 green · residue=none (high-risk method edit, human-gated; §5 re-anchored after the §5 default was corrected to the real scope.md trees)

### Goal met?   (map the evidence back to this milestone's Exit criteria — read before the Exit-criteria boxes are checked)
- [x] each Exit criterion above is satisfied by a Cross-task evidence row or a Ship-by-domain change (cite which) — all 3 delivered by `scope-complete-position` (skill rewrite + tooling assertions), suite 1276 green
- goal: scope-drafting now yields a complete, correctly-positioned MILESTONE.md — proven by `scope.md` covering all 9 template sections + a well-formedness gate + a Position-the-goal first step (assets + milestone map) + `duplicate_goal`, asserted by `test_scope_loop` and md5-equal across 3 trees.

## Release steps   (AI-DEFINED — fill the ordered steps to ship this milestone; engine records, human gate)
> The AI writes the release steps for THIS milestone here (hints, not engine commands). MERGE is one
> small step among them. These feed the release scope (release.md) when the cut is bundled.
- [ ] open a PR bundling this milestone (alongside verify-expectations) from the Close ship-review above; the human (TinDang97) reviews + merges
- [ ] no separate publish — these are method-quality guide/test edits; they ride the next ADD release cut (release.md) when the closed milestones are bundled
