# Consolidating lessons — how the foundation self-improves

This **closes the loop**. `deltas.md` lets a task EMIT lessons (`open` lessons learned in OBSERVE); retrospective consolidation gathers the confirmed ones and writes them into a **versioned foundation**, so `DDD · SDD · UDD · TDD · ADD` sharpen across milestones.

`add.py fold` is **judgment-free**: it only TRANSCRIBES each lesson's own captured text into its routed home and bumps the version. It NEVER composes or merges prose, and it **never self-approves** a consolidation — running the command records the human's confirmation. Deciding WHICH lessons to keep, and polishing raw transcribed bullets into lean one-screen prose, remain the human's work — the latter via the **compaction door** (`compact-foundation.md`).

## When to consolidate

At **milestone close** (the natural version bump), or **on demand** when open lessons pile up. One run of `add.py fold` = ONE consolidation session: bumps `foundation-version` exactly once and stamps every resolved lesson with that version.

## The ritual

1. **Gather** — `add.py deltas` reads every task's OBSERVE block for lessons still `open`.
2. **Confirm** — decide which to keep; a lesson you do NOT want is marked `rejected` and left in place. Running `add.py fold` over the rest IS your confirmation.
3. **Write** — `add.py fold [--task <slug>] [--comp <TAG>]` performs the mechanical write atomically:
   - flips each selected `open` lesson to `folded` and stamps it `[folded foundation-version N]`;
   - transcribes each lesson VERBATIM as one bullet at the TOP (newest-first) of its routed section;
   - prepends one row to §Key Decisions (date · what · why · outcome);
   - bumps `foundation-version` by one.
   Validate-all-then-write: if any precondition fails the command writes NOTHING.
4. **Propose & polish** — transcribed bullets are RAW; afterward consolidate/merge into lean prose (append-only, newest-first) via the compaction door.

## Consolidation routing

| competency | consolidates into | how |
|------------|-----------|-----|
| `DDD` | `PROJECT.md` §Domain | transcribed bullet at the top (newest-first) |
| `SDD` | `PROJECT.md` §Spec | transcribed bullet at the top |
| `UDD` | `PROJECT.md` §Users | transcribed bullet at the top |
| `TDD` | `CONVENTIONS.md` §Method learnings | transcribed bullet |
| `ADD` | `CONVENTIONS.md` §Method learnings | transcribed bullet |

Every consolidation ALSO prepends one row at the TOP of `PROJECT.md` §Key Decisions: date · decision · why · outcome.

## Status transitions & version

- **confirm**: `open` → `folded` (text transcribed at top of routed target, newest-first).
- **decline**: `open` → `rejected`, left in place — "we considered and chose not to act" stays auditable.
- Consolidation is **append-only (newest-first)**: PREPENDS new bullets/rows, never silently rewrites — EXCEPT via the recorded compaction door.
- Each `add.py fold` run **bumps** `foundation-version:` in `PROJECT.md` by one (monotonic int).

## Reject codes

<reject_codes>
- `no_open_deltas` — nothing is `open` in the selected scope. Version is NOT bumped.
- `missing_route_section` — a lesson routes to a foundation section that does not exist. Add the section header, then re-run. Nothing is written.
- `no_foundation_version` — `PROJECT.md` carries no parseable `foundation-version:` marker to bump.
</reject_codes>

Convention-era codes `unconfirmed_fold` and `unroutable_delta` are **retired**: invoking `add.py fold` IS the confirmation; a missing destination surfaces as `missing_route_section`.

## Worked example

The `competency-deltas` task closed its OBSERVE with two lessons:

```
- [ADD · open] dogfood .add/tooling template can silently diverge from canonical (evidence: md5 mismatch this build)
- [TDD · open] structural tests guard canonical artifacts but not their dogfood twins (evidence: scope-loop note + this build)
```

The human keeps both and runs `add.py fold`. Routing transcribes each into `CONVENTIONS.md` §Method learnings, prepends a §Key Decisions row, flips them to `folded` with `[folded foundation-version N]`, and bumps `foundation-version` 1 → 2 — all in one atomic write.
