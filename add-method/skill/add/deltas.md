# Competency deltas — how each loop sharpens the foundation

A **competency delta** is a single learning a task produces, tagged by which of ADD's five
competencies it improves. You write deltas in a task's **OBSERVE** phase; later, the
`foundation-update-loop` gathers the confirmed ones and folds them into a versioned `PROJECT.md`.
This is how `DDD · SDD · UDD · TDD · ADD` stop being write-once and start converging.

You (the AI) **emit** deltas as `open`. Only the **human** moves a delta to `folded` or `rejected`
(folding into the foundation is judgment — see the verify/observe seam). You never self-fold.

## The grammar (frozen)

Each delta begins on its own **tag line**; the learning may wrap onto continuation lines:

```
- [<COMPETENCY> · <status>] <learning> (evidence: <pointer>)
```

- `<COMPETENCY>` — exactly one of the five (below).
- `<status>` — `open` | `folded` | `rejected`. A **newly emitted delta is `open`**.
- `<learning>` — the insight ("the domain model missed multi-tenancy"). It may run past one line;
  the `- [COMPETENCY · status]` tag line must come **first**, and the `(evidence: …)` clause must
  **close** the delta (on its last line).
- `(evidence: …)` — **required**, non-empty: a failing scenario, a production signal, a review
  note. No evidence → it is an opinion, not a delta.

A long learning may wrap — the lint (`add.py check`) joins continuation lines, so this is **one**
delta, not two:

```
- [SDD · open] the export endpoint must reject a tenant-scoped token used cross-tenant,
  returning `forbidden` (not `not_found`) (evidence: scenario_cross_tenant_export failed)
```

## The five competencies (pick exactly one per delta)

| tag | competency | a delta here means you learned something about… |
|-----|------------|--------------------------------------------------|
| `DDD` | Domain | the domain model — an entity, rule, or boundary the spec assumed wrong |
| `SDD` | Spec | what the feature must do / must reject — a missing or wrong requirement |
| `UDD` | UI/UX | the user-facing shape — a flow, affordance, or wording that misled |
| `TDD` | Test | how we prove correctness — a missing scenario, a flaky or hollow test |
| `ADD` | AI/build | how the AI builds — a harness, prompt, or convention that helped or hurt |

If a learning seems to touch two, ask "which competency, once updated, would have PREVENTED this?"
That is its home. Split genuinely separate learnings into separate deltas; never tag one twice.

## Status lifecycle

```
emit (OBSERVE)        human review (foundation-update-loop)
   open  ───────────▶  folded     (the learning is merged into PROJECT.md; version bumps)
         └──────────▶  rejected   (considered and deliberately NOT folded — the trail is kept)
```

An `open` delta is a pending signal. `folded` and `rejected` are both human decisions; a `rejected`
delta is left in place (not deleted) so "we saw this and chose not to act" stays auditable.

## Reject codes (well-formedness — you are the first check, the human is the backstop)

There is no engine validator yet, so before you record a delta, self-check it:

- `unknown_competency` — the tag is missing or not one of `DDD · SDD · UDD · TDD · ADD`. Fix the tag.
- `no_evidence` — the `(evidence: …)` pointer is missing or empty. Add the proof, or drop the line.
- `unknown_status` — the status is not `open | folded | rejected`. A fresh delta is `open`.

## Worked example

A task that built a tenancy feature finished its OBSERVE phase with:

```
- [DDD · open] the account model conflated org and workspace (evidence: scenario_cross_tenant_read failed)
- [TDD · open] no scenario covered a deleted tenant's dangling sessions (evidence: review note, PR thread)
- [ADD · open] the scaffold's allow-list missed the tenancy lib, slowing build (evidence: build log retry)
```

Three learnings, three competencies, each with a pointer. At the next foundation update the human
folded the DDD and TDD deltas into `PROJECT.md` (→ `folded`) and rejected the ADD one as a one-off
(→ `rejected`). The foundation got sharper; nothing was silently lost.
