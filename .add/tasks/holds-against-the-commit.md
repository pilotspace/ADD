---
type: Task
title: holds-against-the-commit
status: direction
depth: standard
sensitivity: security
milestone: seal-what-you-signed
scope:
  - add-method/tooling/add.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - add-method/tooling/engine_pin.py
  - add-method/tests/engine
  - add-method/FORMAT.md
  - add-method/CHANGELOG.md
gives:
  - S1 `learn` evaluates a cited commit's deleted and renamed paths against the owning human-frozen scope in that commit's tree, independent of the caller's checked-out branch
generated: { by: add/3.6.0, at: 2026-09-13 }
verified: []
advised_by: engine-notary
---
## CARD
goal: a quick lesson about deleting or renaming a human-owned path is refused from the cited commit, even when the live worktree no longer contains that path
why: scope ownership currently expands against the caller's worktree, so a deletion or rename changes the security decision merely by checking out another branch
beat: direction · next: add interview holds-against-the-commit, then add freeze holds-against-the-commit --by "human:<name>"

## RULES
<must>
- M1 the owner half of `quick_hit` evaluates a cited deletion against the parent tree of that cited commit, so a path removed by the commit remains inside its signed scope (from: /milestones/seal-what-you-signed.md EXIT 3 · fails-on: deleting a scoped path makes the quick lesson land)
- M2 the same commit-anchored scope reader handles both sides of a rename and yields the same decision from a branch with or without the old path (from: /milestones/seal-what-you-signed.md EXIT 3 · fails-on: checkout state changes whether the same evidence is routed)
</must>
<reject>
- R:WORKTREE_SCOPE a cited commit's scope ownership is decided from files in the caller's current worktree -> "WORKTREE_SCOPE"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the milestone does not say whether a plan-frozen owner is sufficient for a non-sensitive quick owner check; taking existing open-frozen owner authority unchanged -> strengthening signer policy here would duplicate scope-in-the-seal
- A2 [which] covers: S1 · the milestone does not say which commit tree a deletion belongs to; taking the first parent tree that existed before the cited commit -> merge semantics need an explicit follow-up if first-parent is not accepted
- A3 [when] covers: S1 · the milestone does not say whether a later checkout may influence historical evidence; taking no -> the same receipt evidence cannot produce branch-dependent routing
- A4 [absent] covers: S1 · the milestone does not say how an unreadable parent tree should behave; taking existing non-blocking unreadable-evidence behavior -> unavailable git history must not turn the direct lane into a traceback
- A5 [order] covers: S1 · the milestone does not say which path a rename is checked first; taking both old and new names before returning a hit -> a rename cannot evade ownership through path ordering
- A6 [experience] covers: S1 · the milestone does not say how a deletion refusal explains a path absent from disk; taking a message that identifies the cited path and owner -> the named remedy remains understandable after the file is gone

## PLAN
contract: thread the evidence commit/tree into the one scope-expansion reader used by quick ownership; add `git ls-tree` as the accepted read-only tree source and preserve current behavior when evidence cannot be read. The tracked canonical and bundled `add.py` are the implementation pair; ignored runtime copies are parity/vendor evidence, not manually edited scope.
strategy: create real commits for deletion and rename, then make `_scope_files` and its callers consume the anchored tree
regression: affected · python3 -m pytest add-method/tests/engine/test_holds_against_the_commit.py -q · run the full engine suite before a receipt because scope expansion also feeds freshness and routing

## EDGES
- E1 Given a human-owned file deleted by the cited commit · When the caller is checked out where the file is absent · Then `learn` refuses R:QUICKSIZEUP rather than filing the quick lesson
- E2 Given a human-owned file renamed by the cited commit · When the caller is checked out before or after the rename · Then the cited evidence produces the same owner refusal

## CHECKS
- test_deleted_scope_holds_from_both_checkout_states · covers: M1, R:WORKTREE_SCOPE, E1 · acceptance · proves the same deleted-path evidence is refused before and after the checkout loses the file
- test_renamed_scope_holds_from_both_checkout_states · covers: M2, R:WORKTREE_SCOPE, E2 · acceptance · proves the same renamed-path evidence is refused before and after the checkout loses the old name
red-first: `python3 -m pytest add-method/tests/engine/test_holds_against_the_commit.py -q` fails before Build because a deletion removes the live file that `_scope_files` currently needs.

## EVIDENCE
receipt: pending — targeted red run is recorded in tmp/seal-direction-evidence.md
gate: HARD-STOP until the human answers the open assumptions, reject, and edges

## LESSONS
none yet
