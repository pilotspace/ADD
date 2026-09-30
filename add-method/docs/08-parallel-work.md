# 08 · Parallel work — worktrees

[← 19 Explore — when the answer is the deliverable](./19-dynamic-workflow.md) · [Contents](./README.md) · Next: [09 Governance — verdicts, floors, review after →](./09-governance.md)

---

## Reads fan out; writes serialize per tree

The default is one task at a time. Two kinds of work can go wider:

- **Read-only research** — questions, spec reads, codebase surveys — needs no seal and can run in any order; facts merge. Within one session the subagent budget still holds: at most one per beat, in the foreground, and only where its reading would flood the context.
- **Independent tasks** — when a milestone's next tasks do not depend on each other — can build at the same time, **each in its own git worktree and branch, with disjoint `scope:`**.

Writes serialize per tree. Two agents never write the same working tree, and two parallel tasks never share a file in `scope:`. That one rule is what makes parallel builds unable to race.

**Be honest about the gain.** Verification and review are serial. The win is not N× throughput; it is that nobody waits on a build while other work is being checked.

## How to fan out

1. **Pick independent tasks.** No dependency between them (`after:` in the milestone's TASKS, `needs:` in the task files), and no shared path in their `scope:`. If two tasks need the same file, they sequence.
2. **One worktree per task.** From the same starting commit:

   ```bash
   git worktree add ../wt-transfer -b task/transfer-own-accounts
   git worktree add ../wt-statement -b task/monthly-statement
   ```

3. **Each runs the full loop in its worktree** — its own seal, its own build, its own verify commit. A task that ends `HARD-STOP` does not merge.
4. **Merge one at a time.** Bring each verified branch back, run the full suite after each merge, and read the combined diff for the concurrency and architecture conflicts two tasks green in isolation can still produce.

## Design for failure

- **Isolation** — an agent owns only its own worktree; disjoint scope means a conflict is a planning error, caught before anything is built.
- **Time-box each stream** — a stream that stalls or dies is dropped, not trusted: its partial work is not merged.
- **Rollback is dropping a worktree** — the others are untouched.
- **Circuit-break to sequential** — if several streams fail in one round, go back to one task at a time. Repeated failure means the scope was cut wrong, not that you need more parallelism.

## The floors hold for N agents exactly as for one

Each stream seals, builds and verifies its own task. A security finding is a `HARD-STOP` per stream and at the merge. Every stream stays inside its `scope:` and never moves a `gives:` surface other streams depend on. Parallelism is a scheduling choice, never a lowered bar.
