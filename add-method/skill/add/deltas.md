# Lessons learned — how each loop sharpens the foundation

A **lesson learned** is a single learning a task produces, tagged by which of ADD's five competencies it improves. Write deltas in **OBSERVE** and file each into its living spec (`add.py delta-append`) — how `DDD · SDD · UDD · TDD · ADD` stop being write-once and converge.

You **emit** deltas as `open`; only the **human** moves one to `folded` or `rejected`. You never self-approve a consolidation.

**Emit in-flight, not batched**: the moment a lesson is learned — any phase, any task — file it with `add.py delta-append <dd> "<lesson>"` (`ddd|sdd|udd|tdd|add`). The verb prepends one `[open · <date>]` line (newest first, active task stamped) into the lesson's **living spec** under `.add/specs/` — `domain.md · system.md · experience.md · quality.md · method.md`, seeded at init and on demand for pre-2.0 projects. The task's §7 Competency-deltas block stays the per-task record; the living spec is where the lessons accumulate across tasks.

## The grammar (frozen)

Each delta begins on its own **tag line**; the learning may wrap:

```
- [<COMPETENCY> · <status>] <learning> (evidence: <pointer>)
```

- `<COMPETENCY>` — exactly one of the five (below).
- `<status>` — `open` | `folded` | `rejected`. A **newly emitted delta is `open`**.
- `<learning>` — the insight; the tag line comes **first**, `(evidence: …)` **closes** the delta.
- `(evidence: …)` — **required**, non-empty: a failing scenario, a production signal, a review note. No evidence → it is an opinion, not a delta.
- **persona target (optional)** — a competency lesson MAY add `· persona:<slug> · <critical-rule|success-metric|anti-pattern|ability>` in brackets, e.g. `- [UDD · open · persona:ui-designer · success-metric] 4.5:1 contrast (evidence: audit)`. The persona loop lands it in `.add/personas/<slug>.md` under that section (newest-first, never clobbering) instead of the shared specs.

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
   open  ───────────▶  folded     (merged into its `.add/specs/<dd>` spec; version bumps)
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

## Voice deltas — SOUL.md converges to the human

`SOUL.md` (Tone · Communication style · Trust) is the AI's voice — a proposed starter,
**human-owned**. Emit voice deltas beside the lessons learned in observe, grounded ONLY in the
working session — their wordings, their corrections, their flow — never their private files:

```
- [VOICE · <status>] <observation about the voice> (evidence: <in-session pointer>)
```

`<status>` = `open` | `confirmed` | `declined`; evidence is required (a correction, a re-ask, a
visible preference) — none → drop it. The loop: **emit** `open` (show-before-ask) → the human
**confirms or declines** each → on a confirm, rewrite the routed SOUL.md section surgically
(how I *sound* → `## Tone` · how I *structure* → `## Communication style` · what keeps *trust* →
`## Trust`) and record the line `confirmed` at the top of `## Voice deltas` (newest-first,
append-only; declined stays in place). **The human's confirm is the only writer.** Rejects:
`unconfirmed_voice_rewrite` (a SOUL.md write without a recorded confirm — stop, get the confirm) ·
`no_open_voice_deltas` (nothing open — a no-op, touch nothing) · `unroutable_voice_delta` (maps
to no section — fix the delta or widen the routing before writing). No `add.py` command writes
the voice.
