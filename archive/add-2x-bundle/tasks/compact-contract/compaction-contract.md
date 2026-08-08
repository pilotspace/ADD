# Foundation-compaction contract  (FROZEN @ v1 — compact-contract §3)

The canonical, frozen rule-set the consumer tasks build against (`invariant-amend` ·
`compact-guide` · `apply-compaction` · `compact-book-align`). This doc RESTATES the frozen
TASK.md §3 — it does not extend it. A change here is a change request back to SPECIFY.

**Foundation compaction is a convention-guided ritual — the engine stays judgment-free.**

---

## Eligibility (one shared test)

An append-only entry is **compaction-eligible IFF** its milestone is **shipped**
(done/archived) **AND** `open_residues == 0` (zero open deltas/residues).

```
eligibility(entry) -> eligible IFF  shipped(entry.milestone)  AND  open_residues == 0
```

An entry that is unshipped, or carries ≥1 open delta/residue, is **not** eligible — it
stays live and is rejected with `open-residue-version`.

## Ordering (newest-first, all append-only sequences)

```
ordering(sequence) -> newest-first: prepend the newest record at the TOP;
                      the rolled-up settled line is anchored at the BOTTOM (tail / oldest)
```

Every append-only foundation sequence (PROJECT §Key-Decisions · §Spec bullets ·
CONVENTIONS learnings) **prepends** new records at the top. Compaction collapses **upward
from the tail**: stale, shipped entries sink to the bottom and roll into the settled line.
A record placed out of newest-first order, or a settled line not at the tail, is rejected
with `wrong-order`.

## Per-spec rolled-line shapes (tailored — one per spec)

Each spec collapses by its OWN shape; the shapes are distinct:

| spec section | stable input | rolled-line shape |
|---|---|---|
| PROJECT.md §Spec | run of `[folded fv N..M]` bullets | `-> "settled fvN–fvM — <1-line theme> (see git)"` |
| PROJECT.md §Key-Decisions | matching shipped rows | `-> "| settled <dateA>–<dateB> | <N> decisions rolled | (see git) |"` |
| CONVENTIONS.md | run of stable `(TAG)` learnings | `-> "- settled conventions <range> — <N> rules (see git)"` |
| GLOSSARY.md | a verbose, stable definition | `-> "<term>: <terse canonical> (rationale: see git)"` |
| MODEL_REGISTRY.md | superseded model rows | `-> "Prior models: <list> (see git)"` |

GLOSSARY.md and MODEL_REGISTRY.md are tiny today — their shapes are minimal and
forward-looking, applied only when an entry actually becomes eligible.

## Preservation guarantees (every collapse)

- **NEVER delete** — a collapse summarizes and points; it never removes history.
- A surviving **git**/archive pointer is mandatory on every settled line (lossy on prose,
  lossless on traceability).
- **OPEN residues stay live** — never collapsed while any delta/residue is open.
- The audit trail is **summarized-not-deleted**.

A collapse that would drop the git/archive pointer or the summarized audit trail is
rejected with `trail-loss`.

## Reject codes (judgment-checked — the AI proposes, the human confirms)

| code | condition |
|---|---|
| `open-residue-version` | entry is unshipped OR has ≥1 open delta/residue — leave it live |
| `trail-loss` | the collapse would drop the git/archive pointer or the audit summary |
| `wrong-order` | a record is not newest-first, or the settled line is not at the tail |

## Seam — distinct from the engine `compact`

Foundation compaction is **NOT** the engine command `add.py compact <slug>` (which moves a
light-archived milestone into the recovery bundle). It is a **convention** realized in
`compact-foundation.md` (the AI proposes, the human confirms), operating on living survivor
specs. Per ADD's judgment-free-engine ethos (mirroring fold): **NO new engine command** and
**NO add.py check enforcement** — a `check` WARN on un-compacted bloat is a deferred,
out-of-scope follow-up.
