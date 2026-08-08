# OBSERVE notes — project-scope-atomic-reconcile

Written by the build agent (tests → build), separate from TASK.md §7 (that section is
harvested at `done`, not hand-filled mid-task). Deltas below follow the `add` skill's
`deltas.md` grammar — emitted `open`; only a human moves one to `folded`/`rejected`.

## What happened, in one paragraph

Redesigned `_clean_replace`/`cleanReplaceTree` from wipe-then-copy to a crash-safe
self-heal → stage → commit → sweep sequence. Tests: 27 tests in `test_reconcile_rollup.py`
(12 pre-existing + 15 new across `StageCommitUnitTest`/`ConcurrencyDisclosureTest`/
`CrossTwinStagedCommitTest`), confirmed red for the right reason before build (10 failing,
17 passing — an honest mixed red per CONVENTIONS.md fv49), then green after build (27/27),
plus all 4 sibling suites named in M8 (47/47) unchanged throughout. Verified beyond the
mocked unit suite with a real (non-mocked) SIGKILL sent to a live subprocess mid-copy —
`dest` survived byte-for-byte untouched, and the very next call self-healed the leftover
staging directory and landed the full new generation with zero scratch residue.

## Spec delta

- [SPEC · open] the contract's step 0 (SELF-HEAL) names what to do when a stale backup is
  found while dest is absent — rename it onto dest — but not what happens if THAT recovery
  rename itself fails (e.g. a permission error on the parent dir). The current build lets
  this propagate uncaught (fail-loud, no special handling), which is a defensible default
  but was never a named scenario or Reject code — flagging so a future loop can decide
  on purpose whether "self-heal's own restore fails" deserves an explicit contracted
  response, rather than inheriting today's implicit choice (evidence: adversarial
  completeness pass during build convergence, no scenario in §2 exercises this path).

## Competency deltas

- [TDD · open] mocking `shutil.copytree` with `mock.patch.object(shutil, "copytree", ...)`
  intercepts EVERY call the patched name receives — including `shutil.copytree`'s OWN
  internal recursive re-invocation of the public `copytree` symbol for each subdirectory
  it walks. A spy/assertion written assuming "this fires once, for the top-level call"
  silently asserts against a NESTED call's arguments instead whenever the source tree has
  a subdirectory, producing a confusing false failure that looks like an implementation
  bug but is a test-harness scoping gap. Fix: gate the assertion on `Path(source) == the
  original src argument` (evidence: `test_scn3_strip_tests_applied_before_commit_not_after`
  failed post-build with the raw copy already proven correct; traceback showed the
  assertion firing from inside `shutil.py`'s own `_copytree` recursion, not from
  `_clean_replace`'s single call).
- [TDD · open] an injected single-shot failure keyed only on a call's ARGUMENTS (e.g. "raise
  when the rename target equals dest") can accidentally also block a later, DIFFERENT,
  legitimate call that happens to share the same arguments — such as a rollback/recovery
  step that (by design) retries the same destination after the first attempt failed. A
  fault-injection mock for a retry/rollback code path needs a "fire once, then pass
  through for real" flag, not a pure argument predicate, or the mock makes the very
  recovery path it should be testing impossible to exercise (evidence:
  `test_scn6_commit_land_failure_after_aside_rolls_back` — the rollback rename targets the
  same `dest` as the intentionally-failed landing rename, so the original predicate
  blocked both).
- [TDD · open] when a freshly-drafted test's expected value is ambiguous (here: whether a
  swapped-in new filename counts as "restored" or "refreshed"), cross-check it against an
  established, FROZEN, unchanged sibling test in the same file before assuming the
  implementation is wrong — `test_orphan_swept_not_counted` (pre-existing, untouched)
  settled it unambiguously in favor of fixing the new test's expectation, not the
  implementation (evidence: `test_scn7_stale_staging_leftover_swept_before_new_stage`
  initially asserted `{"restored": 0, "refreshed": 1}`, corrected to `{"restored": 1,
  "refreshed": 0}`).
- [ADD · open] an isolated per-task git worktree can be created ONE commit before an
  upstream freeze-stamp-only commit lands on the integration branch, producing a start-gate
  that LOOKS like "not actually frozen" (phase/status stamp lines read DRAFT) when the
  human approval already happened upstream. Before escalating a seemingly-unmet start
  gate, check whether it's a linear-history staleness gap: `git log --oneline --all -- <path>`
  + `git diff <worktree-branch-point> <later-commit> -- <path>` — if the only delta is the
  phase/status stamp with zero content change, sync the two stamp lines rather than
  guessing OR hard-escalating on a technically-true-but-unhelpful "not frozen" reading
  (evidence: this task's TASK.md showed `phase: ground`/`Status: DRAFT` at spawn; commit
  `6daad53` on `release/1.15.0`, one commit ahead of this worktree's branch point, was a
  pure stamp sync to `phase: contract`/`FROZEN @ v1 — approved by Tin Dang` with an empty
  diff otherwise).
