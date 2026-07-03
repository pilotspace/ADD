# OBSERVE-NOTES — global-lock-followups

> Written at ESCALATE (pre-tests): the build agent's start-gate check found the local worktree's
> `TASK.md`/`state.json` do not match the task's own briefing. Full diagnosis below; delta tagged
> per the `add` skill's `deltas.md` grammar.

## What was found

The build agent (this run) was briefed that `.add/tasks/global-lock-followups/TASK.md` carries a
FROZEN @ v1 §3 contract, 14 §2 scenarios, `risk: high` / `autonomy: conservative`, and a filled §5
Scope+Strategy. Reading the file at the start gate (step 1 of the build persona's own checklist —
"confirm the start gate... if anything looks off, STOP and escalate rather than guess") showed
instead the raw, unfilled `TASK.md.tmpl` scaffold: `phase: ground`, `autonomy: auto`, no `risk:`
line, `Status: DRAFT` (by omission — the freeze block is the template placeholder), all §0-§5
prose still bracketed placeholders (`<name>`, `<must>`, `<required behavior>`, …).

Root cause, confirmed mechanically (all read-only checks, nothing mutated):
- This worktree's branch (`worktree-agent-a942c20ba49abefe8`) HEAD is `eb631bc` (the PR #127
  merge commit into `main`).
- The real Specify→Scenarios→Contract→Freeze work for all 3 `install-update-hardening` tasks
  happened as 2 LATER commits directly on `release/1.15.0` (checked out in the non-worktree repo
  root): `6daad53` "feat(add): draft + freeze 3 install-update-hardening contracts" and `cda1a16`
  "feat(add): fill §5 BUILD scope+strategy for the 2 newly-drafted tasks" — both authored by
  Tin Dang today (2026-07-03), `state.json`'s `freeze.approved_by: "Tin Dang"`,
  `frozen_at: 2026-07-03T02:21:22+00:00`.
- `git merge-base --is-ancestor eb631bc cda1a16` → NO. This worktree's branch and `release/1.15.0`
  are not in a fast-forward relationship from where this worktree sits — `release/1.15.0` moved
  forward with the contract-freeze work AFTER this worktree's branch was already cut from an
  earlier point in the same line.
- This worktree has ZERO commits of its own yet (`git log eb631bc..HEAD` is empty) — nothing of
  this run's would be lost by re-pointing the branch.
- **Systemic, not isolated**: the sibling worktree `agent-a72da2c9b203c689d` (also `locked`, HEAD
  `eb631bc`) shows the identical gap — zero commits beyond `eb631bc`. At least 2 of the 3 parallel
  `install-update-hardening` build-agent worktrees were branched before the contracts they were
  meant to build against existed.
- **Zero code drift**: `git diff --stat eb631bc cda1a16 -- add-method/src/add_method/_installer.py
  add-method/src/add_method/_cli.py add-method/bin/cli.js
  add-method/tooling/test_global_update_harden.py` is empty — the divergence is 100% confined to
  `.add/` task-tracking docs (3 `TASK.md` + `MILESTONE.md` + `dag-plan.json` + `state.json`), never
  touching actual source or test code. The pre-existing `test_global_update_harden.py` suite (15
  tests, FROZEN @ v2) runs green on this worktree's current checkout.
- The real frozen content (read via `git show cda1a16:.add/tasks/global-lock-followups/TASK.md`,
  a pure read — no branch/file mutation) was inspected in full and matches the build agent's
  briefing exactly: 14 scenarios (counted), `risk: high` / `autonomy: conservative`, §5 Scope =
  the same 4 files this run's touch-boundary named, `Status: FROZEN @ v1 — approved by Tin Dang`.

## Why this run did not self-heal

The touch-boundary this run was given explicitly forbids editing §1-§3 of `TASK.md` ("the frozen
bundle"), and explicitly forbids writing `MILESTONE.md`/`state.json`/any sibling task's files — the
exact files a self-heal would need to touch to bring this worktree's tracking docs in line with
`release/1.15.0`. Combined with the run's own explicit start-gate instruction ("if anything looks
off, STOP and escalate rather than guess") and this task's `risk: high` / `autonomy: conservative`
posture (a human decides, not the AI), the build agent stopped before writing any test or source
file rather than (a) fabricating its own contract, or (b) unilaterally rewriting a
protected/frozen file to "restore" content sourced from a different branch.

## Recommended fix (proposed, not executed — a process/orchestration decision, not this run's to make)

Neither affected worktree branch (`worktree-agent-a942c20ba49abefe8`,
`worktree-agent-a72da2c9b203c689d`) has any commits of its own, so re-pointing each to
`release/1.15.0` (currently `cda1a16`) is lossless — e.g. `git branch -f
worktree-agent-a942c20ba49abefe8 release/1.15.0` (run from outside the worktree, or `git switch -C
worktree-agent-a942c20ba49abefe8 release/1.15.0` from inside it), then resume/re-invoke the build
agent. This is a recommendation for the orchestrator/human to weigh, not an action this run took.

## Delta

- [ADD · open] a parallel-build worktree can be branched before the orchestrator finishes that
  same task's Specify→Contract→Freeze work, leaving the worker's own `TASK.md`/`state.json` at the
  blank template while the real frozen contract exists only on the integration branch — the worker
  has no way to detect this except by re-reading its own `TASK.md` at the start gate (which this
  run did, per its own briefing's explicit instruction to confirm the gate before proceeding).
  Recommend either freezing all of a milestone's task contracts BEFORE cutting worker worktrees,
  or rebasing/re-pointing each worker worktree onto the integration branch immediately before
  resuming its build agent (evidence: this session — `worktree-agent-a942c20ba49abefe8` and
  `worktree-agent-a72da2c9b203c689d` both branched at `eb631bc`, confirmed 2 commits behind
  `release/1.15.0`@`cda1a16` which drafted+froze all 3 `install-update-hardening` contracts;
  `git merge-base --is-ancestor eb631bc cda1a16` = NO; both worktrees show zero commits of their
  own; the divergence is 100% confined to `.add/` tracking docs, zero source/test drift).

---

## BUILD phase (post-repair) — findings

> The coordinator repaired this worktree (`git merge cda1a16`, 6 files, no conflicts). Independently
> re-verified before resuming: `TASK.md` MD5 `20c6ceb5…` byte-identical to `cda1a16`'s copy;
> `phase: contract`, `risk: high`, `autonomy: conservative`, `Status: FROZEN @ v1 — approved by Tin
> Dang` all confirmed present. Proceeded with tests (commit `8d11de8`, RED confirmed: 9
> AssertionError + 4 TypeError on the not-yet-built surface; 5 new tests + 14 pre-existing already
> green as legitimate regression guards) then build (this section's findings, commit follows).

1. [ADD · open] **A regression this run introduced, then fixed within its own new code** —
   `install(as_global=True)`'s new lock-wrap (M3) initially caught only `except BlockingIOError:`
   around `with _update_lock(...)`. `_update_lock`'s own (pre-existing, unchanged) first line —
   `home.mkdir(parents=True, exist_ok=True)` — raises a plain `FileExistsError` when `home` exists
   as a non-directory (a plain file), which is NOT a `BlockingIOError` and was propagating
   uncaught. Caught by the PRE-EXISTING `test_global_install.py::GlobalInstallTest
   ::test_home_unwritable_fails` (outside this task's declared 4-file touch scope — the test was
   never at risk of being edited; the fix landed in my own new `install()` code: an added
   `except OSError as exc: return _fail(f"cannot write global home {home} — {exc}")` clause AFTER
   the `except BlockingIOError:` one). Verified via a `git stash`-based baseline diff (my 3 changed
   implementation files stashed out, the same 9 initially-observed failures re-run): 8 of 9
   reproduced identically without any of my code (proving them pre-existing/environmental — see
   #2 below); only `test_home_unwritable_fails` was absent from the baseline run, confirming it
   as the one genuine regression, now fixed and re-verified green (evidence: 5 consecutive full
   runs of `test_global_update_harden.py` all 32/32 green; the 27-file targeted regression sweep,
   305 tests, now 297/305 green with the remaining 8 proven pre-existing).

2. [ADD · open] **A related-but-distinct discovered contract gap, deliberately NOT fixed here** —
   `_update_global` (the `update --global` path) contains the SAME latent shape (`_update_lock`'s
   `home.mkdir()` can raise an uncaught `FileExistsError`/`OSError` if `home` is a plain file), but
   it is dormant there today: `_update_global`'s own `no_global_home` pre-check
   (`if not _stamp_path(home).exists(): return _fail(...)`) short-circuits BEFORE `_update_lock` is
   ever reached in every currently-exercised path (`Path(...).exists()` returns `False` cleanly for
   a non-directory `home`, never raising). This task's touch-boundary explicitly forbids touching
   `_update_global`'s existing lock-usage body "beyond threading `lock_timeout`" — so this residual
   was surfaced, not silently patched beyond scope. A natural, cheap follow-up (mirror the same
   `except OSError` widening there too, or harden `_update_lock` itself to translate a home-mkdir
   failure into its own distinct signal) — named for Specify to pick up next, not decided here.

3. [ADD · open] **Pre-existing, proven-unrelated environmental gaps found while regression-sweeping**
   (none caused by this build; none in this task's touch scope to fix) —
   (a) `.add/tooling/add.py` does not exist in this worktree (`git log` shows it was deliberately
   untracked as a "regenerable dogfood mirror" at commit `16afe85`, prior to this task) — breaks
   `test_installer_handoff.py`/`test_installer_prompts.py::EnginePinTest::test_engine_untouched`
   and `test_onboarding_brand.py::BrandSeamsHeldTest::test_engine_untouched_by_the_render`, all of
   which compare this repo's OWN `.add/tooling/add.py` against `ENGINE_MD5`. A `git worktree add`
   checkout does not materialize an untracked/gitignored tree that a prior commit stopped tracking —
   likely the SAME class of worktree-setup gap as the stale-TASK.md issue above, applied to a
   different untracked path. (b) 5 PTY/interactive-driver tests
   (`test_installer_prompts.py::UserCancelledNpmTest::test_user_cancelled_writes_nothing_npm`,
   `test_pty_clack.py::{ClackTimeoutTest::test_child_timeout_raises,
   ClackAgentOverrideTest::test_agent_override_writes_codex, ClackCancelTest::test_cancel_writes_nothing,
   ClackHappyPathTest::test_happy_path_drops_brain}`) fail/error identically with or without this
   build's code — root cause NOT diagnosed by this run (out of declared scope to investigate
   further); the pattern (a `prompt_timeout` marker instead of an expected one, a cancel returning
   0 instead of 130) is consistent with either a genuine pre-existing PTY-driver defect or a
   sandboxed-environment PTY-timing mismatch (this session's own tool environment is known to
   intercept/alter some standard process behavior — see this task's earlier `rtk`-wrapper finding).
   All 8 confirmed via a `git stash` baseline comparison (identical failure set with this build's 3
   changed files removed) — evidence, not a fix, offered for the independent verifier / a future
   loop to triage.

4. [ADD · open] **Disclosed test-design scope limit on concurrency evidence** — the TOCTOU/race
   coverage this build added (`test_concurrent_stale_reclaim_exactly_one_wins`,
   `test_two_concurrent_install_global_no_interleave`) exercises IN-PROCESS multi-threading
   (6 real `threading.Thread`s hitting real `os.open`/`os.unlink` syscalls, and a
   hold-lock-then-release-then-second-call simulation, respectively) — genuine OS-level exclusivity
   IS exercised (the syscalls are real), but neither test spawns truly simultaneous SEPARATE
   processes/CLI invocations racing each other. Named here as a disclosed evidence-scope limit for
   the human/independent-verify concurrency judgment (§6's "concurrency / timing... is safe"
   checkbox is deliberately left unchecked in TASK.md for this same reason), not silently assumed
   equivalent to full cross-process proof.
