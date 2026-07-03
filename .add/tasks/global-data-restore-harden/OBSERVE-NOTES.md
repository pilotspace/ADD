# OBSERVE-NOTES — global-data-restore-harden

Method lessons from this dynamic run, for the orchestrator/human to fold into the milestone's
own OBSERVE pass and/or the next loop's Spec/Competency deltas. Tagged in `deltas.md`'s own
grammar; each line ends with `(evidence: …)` per this repo's own lint convention.

## Findings

- [ADD · open] Parallel build worktrees were forked BEFORE the shared design-phase commits
  (`6daad53` draft+freeze, `cda1a16` fill §5) landed on the integration branch
  (`release/1.15.0`), leaving 2 of 3 sibling worktrees (this task's and `global-lock-followups`)
  holding a stale, pre-freeze TASK.md (Status: DRAFT, phase: ground) instead of the
  human-approved FROZEN @ v1 bundle. Reconciled here via a narrow, disclosed
  `git checkout cda1a16 -- .add/tasks/global-data-restore-harden/TASK.md` (verified those 2
  upstream commits touch zero source code before pulling), committed as its own isolated commit
  (`735343a`) before any test/build work began. If the orchestrator's own worktree-fork step ran
  strictly AFTER the design-phase commits landed (or re-synced each worktree's TASK.md
  immediately before spawning its build agent), this class of gap would not occur (evidence:
  this task's own TASK.md required a manual sync before Ground could even be read; see
  `tmp/sync-task-md.txt`-style commit `735343a`).

- [TDD · open] The concurrency non-goal's own self-heal mechanism cannot distinguish "stale from
  a crash" from "live from a concurrent, in-flight sibling call" — a nested/interleaved second
  `_persist_data` call's OWN step-0 self-heal sweep can (and, in the committed
  `test_persist_two_interleaved_calls_land_one_full_valid_snapshot`, does) delete the FIRST
  call's still-in-progress staging directory, causing the first (outer) call to raise OSError
  rather than complete — a losing caller RAISES instead of silently corrupting, which is a
  strictly better failure mode than the pre-task behavior, but it is a consequence worth naming
  explicitly rather than leaving implicit in the "concurrent runs are out of scope" carve-out.
  The committed test tolerates either outcome (`try/except OSError: pass` around the outer call)
  and asserts only the guaranteed weak property (one caller's full content, never a mix; no
  scratch survives) — traced by hand against the actual implementation, not assumed (evidence:
  test_persist_two_interleaved_calls_land_one_full_valid_snapshot passes green in the build
  commit `a3b832f`, and its docstring records this exact reasoning).

- [SDD · open] `_persist_data` does NOT call `.resolve()` on `project_abspath` internally
  (unlike `_restore_data`, which resolves at its own top) — safe today only because its single
  production caller, `install()`, always resolves `target_path` before calling it (confirmed by
  reading `install()`'s body: `target_path = Path(target).resolve()` precedes both the persist
  and restore call sites). This asymmetry is a latent trap for any FUTURE direct caller of
  `_persist_data` that doesn't resolve first — it would key its snapshot under an unresolved-path
  hash that no `_restore_data` call (which always resolves) could ever find. Not fixed in this
  task (out of the frozen §3 signature; `_persist_data(home, project_abspath) -> bool` is
  contracted UNCHANGED) — named here as a candidate hardening for whoever next touches either
  function's signature (evidence: `_installer.py:_persist_data` line 739 vs `_restore_data` line
  828, `proj = Path(project_abspath).resolve()`; `install()` line ~918 resolves before both call
  sites at 1163/1178).

- [SDD · open] A PRE-EXISTING (not introduced by this task) symlink-dereference asymmetry
  between the JS twins: `persistData`'s `fs.cpSync` calls carry no `dereference` option
  (Node's default is `false` — PRESERVES a top-level symlink as a symlink), while
  `restoreData`'s own `fs.cpSync` calls explicitly pass `dereference: true` (matching Python's
  `shutil.copytree`/`copyfile`, which dereference by default on BOTH functions). This task
  preserved persistData's existing behavior exactly (M12/the INV line freezes "every existing
  scenario's final on-disk CONTENT... BYTE-IDENTICAL to before this task" — fixing an unrelated,
  pre-existing cross-twin inconsistency would have gone beyond that scope) but the asymmetry
  itself was not previously documented anywhere the builder could find. Worth a dedicated Spec
  delta if a top-level symlink inside a persisted `.add/` is ever a real scenario (evidence:
  `cli.js:persistData` line ~994 `fs.cpSync(..., { recursive: true })` vs `restoreData` line
  ~1087/1090 `{ ..., dereference: true }`).

- [TDD · open] The frozen M15/§2 scenario names a real-node-subprocess behavioral smoke for
  RESTORE + prune only, not persist — a deliberate scope decision (confirmed in Ground: the
  origin task's 3 named follow-ups are mid-write atomicity, a directory `--force` test, and an
  npm behavioral test for restore specifically). This leaves `persistData`'s OWN happy-path and
  refresh/2-rename-commit path exercised only structurally (`test_parity_call_site_shape`) and
  via the Python-side unit tests, never via a real `node` subprocess in the committed suite. The
  builder closed this gap for its OWN adversarial confidence via a throwaway, uncommitted manual
  script (2 rounds: fresh persist, then a refresh exercising the actual 2-rename commit; both
  passed) rather than unilaterally expanding the frozen test scope. Candidate follow-up: extend
  `test_npm_restore_and_prune_behavioral_smoke` (or a new sibling) to also drive
  `node cli.js init --global-data` twice against a real project (evidence: manual smoke script,
  not committed, run during this task's build phase; `test_parity_call_site_shape` is the only
  COMMITTED JS-side check that touches `persistData`'s new code).

## Competency deltas
- [TDD · open] A fault-injection mock that raises IMMEDIATELY (before writing anything) can fail
  to discriminate "wrote straight to the final name" from "wrote to an isolated staged copy" for
  a single-file entry — both old and new code leave the same "nothing at the final name" outcome.
  The fix: have the mock WRITE partial/garbage content to whatever path it's actually called
  with, THEN raise — this exposes old code's real corruption (garbage lands at the entry's final
  name) vs new code's safety (garbage only ever lands in an isolated staged sibling). Caught by
  re-checking the RED run for tests that looked "surprisingly green" against the OLD
  implementation before trusting the suite (evidence:
  test_restore_mid_stage_failure_earlier_committed_entries_survive's mock was strengthened from
  a bare `raise OSError("boom")` to `Path(dst).write_text("PARTIAL-GARBAGE"); raise OSError(...)`
  specifically because the immediate-raise version passed on both old and new code).
