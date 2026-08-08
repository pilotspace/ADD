# SUMMARY — status-lock-hint build stream

task: status-lock-hint
outcome: PASS-PROPOSED
worktree: /Users/tindang/workspaces/tind-repo/AIDD-Book/.claude/worktrees/agent-a843de3bd42cd6a05
branch: worktree-agent-a843de3bd42cd6a05

## Evidence

own_suite:
  python3 -m unittest test_status_lock_hint -v
  → 4/4 passed (0 failures, 0 errors)

regression_net:
  python3 -m unittest test_setup_lock test_machine_state test_v8_onramp test_onboarding_align test_min_pillar -v
  → 32/34 passed; 2 expected failures (test_addpy_parity, test_addpy_dual_tree_md5)
    are bundle-parity tests documented as out-of-scope in touch_boundary

json_branch_untouched: lines 598-614 of cmd_status (--json early return) byte-identical to pre-edit
no_test_contract_altered: only add-method/tooling/add.py and .add/tasks/status-lock-hint/ modified

## What changed

cmd_status in add-method/tooling/add.py — human-view tail only.

Predicate: unlocked = not _setup_locked(state) computed once after load_state;
canonical helper reused, no parallel predicate.

Two edit sites (--json branch at lines 598-614 untouched):

1. No-tasks early-return (~line 649): when unlocked, print the lock hint instead
   of the generic first-run /add panel. tasks: (none yet) header preserved; returns early either way.

2. With-tasks tail (~line 668): if unlocked: <hint>  elif active and active in tasks: <resume>.
   Suppresses resume block while unlocked; existing resume text unchanged when locked/grandfathered.

Hint shape (both sites):
  setup   : UNLOCKED — review .add/SETUP-REVIEW.md (least-sure first), then sign: add.py lock
            (the build-boundary gate is closed until the foundation is locked)

Contains required literals .add/SETUP-REVIEW.md and add.py lock;
does not contain any asserted-absent string from the test negatives.

## Residue

none — read-only status surface; no security, concurrency, or architecture findings.

## Proposed competency deltas

- status surfaces setup gate (open): cmd_status non-json view identifies the unlocked window
  and directs users to review SETUP-REVIEW.md + run add.py lock; both unlocked sub-states covered
  (zero tasks, with tasks); locked/grandfathered output byte-identical to before.

## Integration note (cherry-pick disclosure)

Branch base was 7f7ee54, one commit behind the frozen-front commit c896698 which
added the test files. To obtain test_status_lock_hint.py, I cherry-picked c896698
as 18328be. That commit also carried the sibling stream's files
(test_delta_grammar_dedup.py, .add/tasks/delta-grammar-dedup/), .add/state.json,
and .add/milestones/ — all of which touch_boundary forbids touching directly.

The deliverable commit 98c8834 is scoped-clean (verified via git show --stat):
only add-method/tooling/add.py, .add/tasks/status-lock-hint/TASK.md, and
.add/tasks/status-lock-hint/SUMMARY.md.

ORCHESTRATOR ACTION REQUIRED: integrate via cherry-pick of 98c8834 onto a base
that already has c896698 (the frozen-front commit), NOT a branch merge. A branch
merge would re-apply the sibling's files and state changes from 18328be.
