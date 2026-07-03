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
