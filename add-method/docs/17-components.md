# 17 · Components — monorepo and multi-repo

[← 16 Releasing](./16-releasing.md) · [Contents](./README.md) · Next: [20 What changed in 4.0 →](./20-whats-new-in-4.md)

---

Most of this book treats a project as one codebase with one green bar. Real systems are rarely that tidy: a backend and a frontend, a shared library and two apps, three services across three repositories. ADD handles all of them with fields every task already has — `scope:`, `gives:`, `needs:` — and the commands in each task's PLAN. Nothing extra is needed until a milestone genuinely spans more than one part.

## Scope is declared on the task

A task names the paths it may touch in its `scope:` frontmatter. In a monorepo that simply spans parts:

```yaml
scope: [apps/gateway/routes/transfers.ts, services/payments/transfers.py, services/payments/tests/test_transfer_contract.py]
```

There is no registry of components to keep in sync, and nothing infers ownership from the directory layout. To find which task owns a path, search the task files: `grep -l 'services/payments' .add/tasks/*.md`.

## Each task against its own green bar

A backend task and a frontend task pass on different toolchains. Each task's PLAN names its own `check:` and `regression:` commands — `pytest` for one, `npm test` for the other — and Verify runs exactly those, fresh, and records their real output. Two tasks, one milestone, two green bars, each held to its own.

## A contract between parts

When one part produces an interface another consumes, the boundary is the producer task's `gives:` and the consumer task's `needs:`:

```yaml
# producer: .add/tasks/transfer-endpoint.md
gives:
  - S1 POST /transfers -> 200 {transferId, fromBalance, toBalance} | 400 {error} | 403 {error}

# consumer: .add/tasks/transfer-form.md
needs: [tasks/transfer-endpoint.md#gives]
```

The producer's `gives:` is sealed in its `freeze` commit. The consumer should not seal against a surface that is not sealed yet, so the milestone lists it `(after: transfer-endpoint)`. If the producer later refreezes a changed surface, every task whose `needs:` cites it is re-verified before it is trusted again — internals may change freely; an interface change propagates as explicit re-verification.

Put producer and consumer in the **same** milestone to ship a vertical slice, ordered by the sealed contract. Independent parts can build at the same time in separate worktrees ([08](./08-parallel-work.md)).

## Across repositories: one bundle each

Each repository keeps its own `.add/` — its own `PROJECT.md`, specs and tasks. A `needs:` cannot point into another repository's bundle, so the hand-off is the contract itself: the producing repository seals its `gives:` and commits it; the consuming repository records a copy of that shape in its own task as the contract of record, citing the producer's freeze commit. That is deliberately not an automatic sync — a boundary between two teams' repositories is exactly where a committed, cited contract beats a background pull.

## What this is not

- **Not auto-discovery.** Scope is declared per task, never inferred.
- **Not a central server.** Each repository's bundle stands alone.
- **Not a new approval.** It rides the same loop: the same seal, the same verify, the same verdicts.
