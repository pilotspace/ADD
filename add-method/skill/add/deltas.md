# Deltas — the 5-DD grammar for how each loop sharpens the specs

A **delta** is one learning a task produces, tagged by which of ADD's five competencies it improves.
Emit deltas as you learn them; they fold into the living `.add/specs/` — how the five specs stop
being write-once and converge on reality.

> **Command status.** `add learn <dd> "<lesson>"` (delta-append), `add deltas` (list open), and
> `add fold` (consolidate) are all **wired** — the real `add` CLI files, lists, and folds deltas in
> the living spec. The grammar and lifecycle below are what those verbs enforce.

**Emit in-flight, not batched.** The moment a lesson lands — any beat, any task — file it with
`add learn <dd> "<lesson>"` (`<dd>` = `ddd|sdd|udd|tdd|add`). It prepends one `[open · <date>]`
line (newest-first, active task stamped) into the lesson's living spec under `.add/specs/`. The
task's own record stays the per-task trail; the living spec is where lessons accumulate across tasks.

## The grammar (frozen)

Each delta begins on its own **tag line**; the learning may wrap:

```
- [<COMPETENCY> · <ID> · <status> · <valid-from>] <learning> (evidence: <pointer>)
- [<COMPETENCY> · <ID> · <status> · <valid-from>→<valid-to>] <learning> (evidence: <pointer>)
```

- `<COMPETENCY>` — exactly one of the five (below).
- `<ID>` — the lesson's **address**: a lens letter (`D`omain · `S`ystem · e`X`perience · `Q`uality ·
  `M`ethod) then an integer, unique within its spec file. It is the `#fragment` of the concept
  address `/specs/method.md#M12`, so it holds no space, dot or punctuation. `learn` mints it above
  a high-water mark the spec's `delta_seq:` carries, so **an id is never reused** — not after a
  fold, not after a delete. Ids **retire in place**: nothing ever renumbers a survivor, because a
  renumber silently re-points every relation aimed at it.
- `<status>` — `open | folded | rejected`. A **newly emitted delta is `open`**.
- `<valid-from>` / `<valid-to>` — the **validity interval**, `YYYY-MM-DD`, **closed-closed**: a
  delta folded today was still carried today. `open` carries the start alone; a **terminal** status
  (`folded` or `rejected`) closes the window. This is what makes `--as-of` possible — the window a
  lesson was actually carried, rather than a file with no time in it at all.
- `<learning>` — the insight; the tag line comes **first**, `(evidence: …)` closes it.
- `(evidence: …)` — **required**, non-empty: a failing scenario, a production signal, a review note.
  No evidence → it is an opinion, not a delta.
- **the tail stays open** — a clause may follow the evidence clause (a persona hint, a typed
  relation). Anything after `(evidence: …)` is carried, never parsed away.
- **persona target (optional)** — a lesson MAY add `· persona:<slug> · <critical-rule|success-metric|
  anti-pattern|ability>` **in the tail**; the persona loop lands it in `.add/personas/<slug>.md`
  under that section (newest-first, never clobbering) instead of the shared specs (`personas.md`).

**The LEGACY two-field head `- [<COMPETENCY> · <status>] …` is read forever.** Not generosity —
there is nowhere else for it to go. A legacy head carries no date, and an installed bundle has no
way to recover one; at any deprecation date the only moves left would be making a user's real
lessons malformed, or stamping an invented date, and inventing a date is the one thing this format
forbids. So an undated delta lists normally, with an unbounded interval, and is never reported.

A long learning may wrap onto continuation lines — they join into **one** delta:

```
- [SDD · S4 · open · 2026-08-11] the export endpoint must reject a tenant-scoped token used
  cross-tenant, returning `forbidden` (not `not_found`) (evidence: scenario_cross_tenant_export failed)
```

## The five competencies → their living spec (pick exactly one)

| tag | competency | lands in `.add/specs/` | a delta here means you learned about… |
|-----|------------|------------------------|----------------------------------------|
| `DDD` | Domain | `domain.md` | an entity, rule, or boundary the spec assumed wrong |
| `SDD` | Spec | `system.md` | a missing or wrong must-do / must-reject requirement |
| `UDD` | UI/UX | `experience.md` | a flow, affordance, or wording that misled the user |
| `TDD` | Test | `quality.md` | a missing scenario, or a flaky / hollow test |
| `ADD` | AI/build | `method.md` | a harness, prompt, or convention that helped or hurt |

Touches two? Ask "which competency, once updated, would have **PREVENTED** this?" — that is its home.
Split separate learnings; never tag one delta twice.

## Status lifecycle — the AI never self-consolidates

```
emit (observe)        human review
   open  ───────────▶ folded    (merged into its .add/specs/<dd> spec; version bumps)
         └──────────▶ rejected  (deliberately NOT merged — the trail is kept, line left in place)
```

You **emit** `open`; only the **human** moves a delta to `folded` or `rejected`. Consolidation is
judgment, and judgment is the human's — the same rule that stops the AI grading its own work.

## Reject codes

<reject_codes>
- `unparsed` — the head is neither two fields (legacy) nor four (dated). Count the `·` separators.
- `unknown_competency` — the tag is missing or not one of `DDD · SDD · UDD · TDD · ADD`. Fix the tag.
- `no_evidence` — the `(evidence: …)` pointer is missing or empty. Add the proof, or drop the line.
- `unknown_status` — the status is not `open | folded | rejected`. A fresh delta is `open`.
- `bad_id` — the id is not a letter followed by letters, digits, `_` or `-`. It must survive as a
  `#fragment`, so it may hold no space, dot or other punctuation.
- `bad_date` — an endpoint is not `YYYY-MM-DD`. Fix the format.
- `bad_interval` — the close is earlier than the open. Swap the endpoints.
- `open_carries_close` — an `open` head carries a close date. An open lesson is still carried:
  drop the close, or move the status to `folded`.
</reject_codes>

## Worked example

```
- [DDD · D7 · open · 2026-08-11] the account model conflated org and workspace (evidence: scenario_cross_tenant_read failed)
- [TDD · Q3 · open · 2026-08-11] no scenario covered a deleted tenant's dangling sessions (evidence: review note)
- [ADD · M12 · folded · 2026-08-11→2026-09-03] the scaffold's allow-list missed the tenancy lib (evidence: build log)
```

At close the human folded DDD+TDD (→ `folded`) and rejected ADD. Sharper foundation; nothing lost.
