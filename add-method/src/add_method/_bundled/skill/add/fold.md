# Consolidating lessons — how the foundation self-improves

This **closes the loop**. `deltas.md` lets a task EMIT `open` lessons in OBSERVE; consolidation gathers the confirmed ones into a **versioned foundation**, so `DDD · SDD · UDD · TDD · ADD` sharpen across milestones.

`add.py fold` is **judgment-free**: it only TRANSCRIBES each lesson's captured text into its routed home and bumps the version — it never composes prose and **never self-approves** (running the command records the human's confirmation). Choosing which lessons to keep, and polishing raw bullets into lean prose (the **compaction door**, `compact-foundation.md`), stay the human's work.

## When to consolidate

At **milestone close**, or on demand when opens pile up. One `add.py fold` = ONE session: one `foundation-version` bump, every resolved lesson stamped with it.

## The ritual

1. **Gather** — `add.py deltas` reads every task's OBSERVE block for lessons still `open`.
2. **Confirm** — mark any lesson you do NOT want `rejected` (left in place); running `add.py fold` over the rest IS your confirmation.
3. **Write** — `add.py fold [--task <slug>] [--comp <TAG>]` performs the mechanical write atomically:
   - flips each selected `open` lesson to `folded` and stamps it `[folded foundation-version N]`;
   - transcribes each VERBATIM as one bullet at the TOP (newest-first) of its routed section;
   - prepends one §Key Decisions row (date · what · why · outcome);
   - bumps `foundation-version` by one.
   Validate-all-then-write: if any precondition fails the command writes NOTHING.
4. **Propose & polish** — raw bullets later merge into lean prose (append-only, newest-first) via the compaction door.

## Consolidation routing

| competency | consolidates into | how |
|------------|-----------|-----|
| `DDD` | `PROJECT.md` §Domain | transcribed bullet at the top (newest-first) |
| `SDD` | `PROJECT.md` §Spec | same |
| `UDD` | `PROJECT.md` §Users | same |
| `TDD` | `CONVENTIONS.md` §Method learnings | same |
| `ADD` | `CONVENTIONS.md` §Method learnings | same |
| `persona:<slug>` | `.add/personas/<slug>.md` §Critical Rules / §Success Metrics / §Anti-patterns / §Abilities | dated bullet at top; schema stays conformant |

A `persona:<slug> · <hint>` lesson routes into that persona doc, not a foundation file; it is still flipped `folded` and still bumps the version once (`deltas.md`).

## Status transitions & version

- **confirm** `open` → `folded`; **decline** `open` → `rejected` (left in place — auditable trail).
- Consolidation is **append-only (newest-first)** — PREPENDS, never silently rewrites, EXCEPT via the recorded compaction door.

## Reject codes

<reject_codes>
- `no_open_deltas` — nothing is `open` in the selected scope. Version is NOT bumped.
- `missing_route_section` — a lesson routes to a foundation section that does not exist. Add the section header, then re-run. Nothing is written.
- `no_foundation_version` — `PROJECT.md` carries no parseable `foundation-version:` marker to bump.
- `missing_persona_target` — a `persona:<slug>` lesson with no `.add/personas/<slug>.md`. Fail-closed: nothing written, no bump. Seed the persona first.
- `persona_section_unroutable` — the section hint is not one of `critical-rule | success-metric | anti-pattern | ability`. Nothing is written.
- `persona_clobber_forbidden` — INVARIANT: a persona consolidation prepends only; it never drops existing content or breaks the schema.
</reject_codes>

Retired: `unconfirmed_fold` · `unroutable_delta` — running `add.py fold` IS the confirmation; a missing destination is `missing_route_section`.

## Worked example

The `competency-deltas` task closed its OBSERVE with two lessons:

```
- [ADD · open] dogfood .add/tooling can silently diverge from canonical (evidence: md5 mismatch)
- [TDD · open] structural tests guard canonical artifacts but not their dogfood twins (evidence: this build)
```

The human runs `add.py fold`: both transcribe into `CONVENTIONS.md` §Method learnings, a §Key Decisions row is prepended, both flip to `folded`, and `foundation-version` bumps 1 → 2 — one atomic write.
