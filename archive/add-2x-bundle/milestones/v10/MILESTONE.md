# MILESTONE: Dogfood parallel-streams on fold-support tooling

goal: Validate the new streams orchestration by shipping two independent fold-support features through it
stage: mvp · status: active · created: 2026-06-03

> SDD living doc for this milestone. Keep it THIN: breadth, shared decisions, and
> exit criteria only — per-task detail lives in each `.add/tasks/<slug>/TASK.md`,
> written just-in-time. Update this doc whenever a task reveals a milestone gap.

> **Why now.** The new parallel-streams flow (`skill/add/streams.md`) is a draft never run.
> This milestone dogfoods it: two genuinely independent fold-support features, built as
> parallel worktree workers, merged serially. It validates streams *orchestration*, not the
> spawn-template *portability* (both workers are Claude Code `Task()` — the one verified column).

## Scope
In:  (1) **deltas-report** — read-only `add.py deltas [--json]`: scan every task's OBSERVE
     block for `open` competency deltas, group by the five competencies with counts; a
     human-facing aid for the fold ritual. autonomy: **auto** (read-only, decides nothing).
     (2) **deltas-lint** — extend `add.py check`: a fail-closed guard that every delta line
     parses the grammar AND routes to a known competency (the `unroutable_delta`/malformed
     cases from `fold.md`); a behavioral proof, read-only. autonomy: **conservative** (a guard
     feeding the fold decision).
Out: an `add.py fold` command (deliberately none — the engine stays judgment-free, `fold.md`);
     auto-applying or writing folds; any change to `streams.md`/`run.md` semantics (this USES
     them); testing non-Claude runners (Task() workers only — portability stays unverified).

## Shared decisions & glossary deltas   (living — every task must honor these)
- **Fail-closed, read-only** (carried from v2): a new guard FAILS on malformed/unparseable
  input, never silently passes; neither command mutates state.
- **Per-scope autonomy dial** (principle 5): `deltas-report=auto`, `deltas-lint=conservative` —
  chosen per risk, NOT blanket. The dogfood deliberately exercises both rows of the dial table.
- **Three-tree parity is part of "tests green"**: any `add.py` change must sync the canonical
  (`add-method/tooling/add.py`), the dogfood (`.add/tooling/add.py`), and the bundle
  (`scripts/prepare_bundle.py`) — `test_tree_parity`/`test_bundle_parity`/`test_cospecify_scaffold`
  enforce it. *(amended 2026-06-03 — the streams commit broke skill-tree parity; the guard caught it.)*

## Shared / risky contracts (freeze these first)
- the two **CLI surfaces** (`add.py deltas` output shape · `add.py check` new failure codes) —
  each owned by its task; independent, so they freeze independently (no cross-task contract).

## Tasks (breadth-first decomposition; detail lives in each TASK.md)
- [ ] deltas-report   depends-on: none   autonomy: auto          — read-only `add.py deltas` report, open deltas grouped by competency
- [ ] deltas-lint     depends-on: none   autonomy: conservative  — `add.py check` guard: delta grammar + competency routing, fail-closed

## Exit criteria (observable; map each to the task that delivers it)
- [x] `add.py deltas` lists every `open` delta grouped by competency, with counts            (← deltas-report)
- [x] `add.py check` FAILS on a malformed or unroutable delta and passes on valid ones        (← deltas-lint)
- [x] both tasks were built as parallel worktree workers, then merged serially + integration-verified  (← streams dogfood)
- [x] a RETRO/delta records what the streams flow validated and what it did NOT (portability)  (← close note below)

## Close note (2026-06-03)
Both tasks gated PASS; all four exit criteria met. Milestone **done**.

**What the streams dogfood VALIDATED** (Claude Code `Task()` workers):
- ready→worker→verdict→serial-merge→integration-verify→gate, end to end on two real features;
- **pipelining** — worker A built while the orchestrator drafted B's front (reviewer never blocked on a build);
- **both dial rows** — `deltas-report` (auto) self-PASSed on evidence; `deltas-lint` (conservative) returned
  ESCALATE and a human recorded its verify gate;
- **the one-approval front caught a real spec defect before any code** — the line-based delta grammar would
  have red-ed the repo; corrected to multi-line/open-only at the front (backward-correction);
- **the guard's first catch** — a real malformed OPEN delta (`onboarding-align`, no evidence) found + fixed.

**What it did NOT validate (honesty):**
- spawn-template **portability** — both workers were Claude Code `Task()`; Codex/opencode/pi-mono adapters stay
  UNVERIFIED (illustrative only in `streams.md`);
- **stale worktree base** — both agent worktrees forked from a pre-v10 commit; A recreated the frozen test, B
  needed a `git merge main` step 0. `streams.md` should add an explicit "verify worktree base == HEAD" step.
  (filed as an `[ADD · open]` delta on deltas-report.)
