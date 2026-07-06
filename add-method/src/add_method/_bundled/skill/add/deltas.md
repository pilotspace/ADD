# Lessons learned — how each loop sharpens the foundation

A **lesson learned** is a single learning a task produces, tagged by which of ADD's five competencies it improves. Write deltas in **OBSERVE**; later `fold.md` consolidates confirmed ones into a versioned `PROJECT.md` — how `DDD · SDD · UDD · TDD · ADD` stop being write-once and converge.

You **emit** deltas as `open`; only the **human** moves one to `folded` or `rejected`. You never self-approve a consolidation.

## The grammar (frozen)

Each delta begins on its own **tag line**; the learning may wrap:

```
- [<COMPETENCY> · <status>] <learning> (evidence: <pointer>)
```

- `<COMPETENCY>` — exactly one of the five (below).
- `<status>` — `open` | `folded` | `rejected`. A **newly emitted delta is `open`**.
- `<learning>` — the insight; the tag line comes **first**, `(evidence: …)` **closes** the delta.
- `(evidence: …)` — **required**, non-empty: a failing scenario, a production signal, a review note. No evidence → it is an opinion, not a delta.
- **persona target (optional)** — a competency lesson MAY add `· persona:<slug> · <critical-rule|success-metric|anti-pattern|ability>` in brackets, e.g. `- [UDD · open · persona:ui-designer · success-metric] 4.5:1 contrast (evidence: audit)`. At `add.py fold` it lands in `.add/personas/<slug>.md` under that section (newest-first, never clobbering) instead of `PROJECT.md` (`fold.md`).

A long learning may wrap — `add.py check` joins continuation lines into **one** delta:

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

If a learning touches two, ask "which competency, once updated, would have PREVENTED this?" — that is its home. Split separate learnings; never tag one twice.

## Status lifecycle

```
emit (OBSERVE)        human review
   open  ───────────▶  folded     (merged into PROJECT.md; version bumps)
         └──────────▶  rejected   (deliberately NOT consolidated — trail kept)
```

## Reject codes

<reject_codes>
- `unknown_competency` — the tag is missing or not one of `DDD · SDD · UDD · TDD · ADD`. Fix the tag.
- `no_evidence` — the `(evidence: …)` pointer is missing or empty. Add the proof, or drop the line.
- `unknown_status` — the status is not `open | folded | rejected`. A fresh delta is `open`.
</reject_codes>

## Worked example

```
- [DDD · open] the account model conflated org and workspace (evidence: scenario_cross_tenant_read failed)
- [TDD · open] no scenario covered a deleted tenant's dangling sessions (evidence: review note)
- [ADD · open] the scaffold's allow-list missed the tenancy lib, slowing build (evidence: build log)
```

At the next update the human consolidated DDD+TDD (→ `folded`) and rejected ADD. Sharper foundation; nothing lost.
