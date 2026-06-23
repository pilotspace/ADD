# Foundation compaction — collapse the stable tail

`fold.md` PREPENDS new learnings (newest-first); foundation compaction COLLAPSES the stable tail of each foundation spec into a rolled-up settled line — keeping PROJECT.md, CONVENTIONS.md, GLOSSARY.md, and MODEL_REGISTRY.md to one screen as the project grows.

You **gather and propose**; the **human confirms**; you then write the settled line. This is a **convention**, not a command — there is no `add.py compact-foundation`. It is DISTINCT from engine `add.py compact <slug>` (the archive recovery-bundle move).

## When

At **milestone close** (after `fold.md`) or **on demand** when a spec has grown past one screen. Always a SEPARATE step from `fold.md`.

## Eligibility

An entry is compaction-eligible **IFF** its milestone is **shipped** (done/archived) **AND** it carries **zero open residues**/deltas. Unshipped or open-residue entries are NOT eligible (`open-residue-version`).

## The ritual

1. **Gather** — collect the stable, shipped, zero-residue tail of the target spec.
2. **Propose** — draft the per-spec rolled-up settled line and show the human.
3. **Confirm** — no write happens without confirmation.
4. **Write** — replace the collapsed tail with ONE settled line at the BOTTOM (newest-first: live records stay on top, settled line anchors at the tail), carrying a git/archive pointer.

## Per-spec rolled-line shapes

- **PROJECT.md §Spec** — `[folded fv N..M]` bullets → `settled fvN–fvM — <theme> (see git)`.
- **PROJECT.md §Key-Decisions** — shipped rows → `| settled <dateA>–<dateB> | <N> decisions rolled | … | see git |` at the tail.
- **CONVENTIONS.md** — `(TAG)` learnings → `- settled conventions <range> — <N> rules (see git)`.
- **GLOSSARY.md** — verbose stable definition → terse canonical line + `(rationale: see git)`.
- **MODEL_REGISTRY.md** — superseded model rows → `Prior models: <list> (see git)`.

## Preservation

- **Never delete** — summarize and point; a settled line is lossy on prose, lossless on traceability.
- A git/archive pointer is mandatory (`trail-loss` if dropped).
- OPEN residues stay live.

## Reject codes

- `open-residue-version` — entry is unshipped or has ≥1 open delta/residue; leave it live.
- `trail-loss` — the collapse would drop the git/archive pointer or audit summary.
- `wrong-order` — a record is not newest-first, or the settled line is not at the tail.
