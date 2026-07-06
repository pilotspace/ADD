# Chat reports — the decision-point template (for the AI, not for add.py)

The engine renders artifacts (`report`, `report --decide`, `status`); this file governs the CHAT MESSAGE you wrap around them.

Use it every time you report at or near a human gate.

## The decision banner — rendered first, above everything

Every report at a human gate opens with a banner line, so a human scanning a long chat can spot "this needs my input" without reading prose:

```
════════════════════════════════════════════════════════════════
 PLAN · <task/milestone title, bold> · <gate name> → APPROVE?
 📄 <task's TASK.md path>  ·  <milestone's MILESTONE.md path>
════════════════════════════════════════════════════════════════
```

- The title is the real H1 from TASK.md/MILESTONE.md, **bolded** — not the bare slug.
- The path line names the actual file(s) so the human can open them directly; omit the milestone half for a milestone-free/fast task.
- Any `§`-numbered section named anywhere in the report (SHAPE, FLAGS, APPROVE, NEXT) is **bolded** — e.g. `**§3 CONTRACT**` — so a scanning eye finds exactly which part of the file is in play.

## The decision arc — rendered next

Every report at a human gate carries the **ARC** — three labelled lines placing the decision in the work's whole arc. Render it right after the banner, then a separator, then the report blocks:

```
ARC  goal: <the milestone / project goal this decision serves>
     done: <proven progress — tasks done · exit-criteria met · what this gate proves>
     plan: <this gate → the next step → the goal>
```

- **goal** — read from `m-goal` in `add.py status`; never re-typed from memory.
- **done** — proven progress only: exit-criteria met/total, tasks done, what this gate proves. An honest fact, never a hope.
- **plan** — this gate → the next step → the goal, mirroring the rollup's `DECIDE NEXT` line.

The arc is required at every human gate: **baseline-lock · contract-freeze · verify · intake · scope · milestone-close · graduation**. It is presentation only — it adds no gate and changes no PASS / RISK-ACCEPTED / HARD-STOP / freeze decision.

Its facts are engine-sourced (goal = `m-goal` · done = exit-criteria + tasks done · plan = `DECIDE NEXT`); if your arc and `add.py` disagree, the engine wins.

### Per-gate examples

- **verify** — `goal:` ship the arc · `done:` tests 6/6 green · `plan:` PASS → every gate → goal.
- **contract-freeze** — `done:` bundle drafted, flag surfaced · `plan:` freeze §3 → build → goal.

## PLAN / SHAPE — when there's more than one step, or a shape to freeze

Render one of these (never both) right after the ARC, whenever the message needs to show more than a single fact — a multi-task breakdown, a roadmap, mid-milestone orientation, or (at a contract freeze) the shape itself:

```
PLAN   <milestone or theme — one line>
  ✅ done (N)          <collapsed — never enumerated by name>
  🔄 <active-slug>      <one line: what it's doing right now>
  ⬜ <next-slug>        <one line — "depends-on: <slug>" if it blocks>
  ⬜ <next-slug>
  ⚠ <flagged-slug>     <one line — why it's flagged>
  … +N more queued     <only if the live list exceeds the cap>
```

```
SHAPE   <task title, bold> — v<N>  (DRAFT — not yet frozen)
  <endpoint/type/field>        <new | changed | unchanged>
  <error case / reject token>  <what triggers it>
```

- **Collapse done to a count.** Never enumerate finished tasks by name.
- **Cap live items at ~5–7**, dependency-ordered; footer `+N more queued`.
- **One line per item** — slug + what it does or blocks on; never restate the whole TASK.md.
- **Glyphs are fixed** — ✅ done · 🔄 active · ⬜ pending · ⚠ blocked/flagged; never invent new ones.
- **Sourced from the engine, summarized by you** — pull from `add.py status`'s `tasks:`/`streams:` output; never paste it verbatim into chat.
- **SHAPE is freeze-only** — the concrete thing being locked, so the human reviews the actual shape, not just commentary about it.

## The report blocks, in order

Render every block (write "none" rather than dropping one); add MORE when needed.

```
SUMMARY   one line: intent + target + where we are + what we done
FLAGS     lowest-confidence first: why + cost-if-wrong
DECIDED   highest-confidence first: the autonomous calls you made + why each was safe
EVIDENCE  small table: tests · gates · parity · check — engine-sourced
APPROVE   what you need from the human (or "none — FYI") — exactly one — sits last, right before the ask
NEXT      the recommended next actions, ranked (top ▶ highlighted, bolded) + what each unlocks
```

1. **SUMMARY** — one line: intent + target + position. **Never optional** — even when PLAN/SHAPE already carries most of the context, SUMMARY still renders as its own line; it is never merged into or silently replaced by another block.
2. **FLAGS** — lowest-confidence first, each with *why* and *cost if wrong*. Where TASK.md markers exist (`⚠` / `- [~]` / `- [ ]`), quote verbatim and keep document order.
3. **DECIDED** — high-confidence autonomous calls, highest-confidence first, each with *why* it was safe. "none" when none. NEVER list a security / residue / lowered-autonomy call here.
4. **EVIDENCE** — engine-sourced facts from `add.py` output, never re-typed.
5. **APPROVE** — as a **guided decision**: one `▶ … (recommended)` + 1–3 described alternatives. Exactly one per report, or "none — FYI". Rendered last among the core blocks — the actual interactive ask fires only after everything above it (show-before-ask).
6. **NEXT** — ranked next actions, top one marked `▶` with what it unlocks. Mirror the rollup's `DECIDE NEXT` for the top action; overrule it only with a stated reason. **Informational, not a second gate**.

### Beyond the core blocks

When a report needs more — a `RISK` ledger, a `DIFF`, a `SCOPE` map — add an extra block (SCREAMING-CASE label · one-line intent · engine-sourced where possible) AFTER EVIDENCE and BEFORE APPROVE. Add only when it carries what the core blocks don't; never pad; never drop a core block.

### The APPROVE block as a guided choice

```
APPROVE  <the question>

  ▶ <recommended option>  (recommended)
      <one-line description — what it means · what it unlocks or costs>
    <alternative option>
      <one-line description>
```

- **Exactly one** option carries `▶ … (recommended)`. `confidence.md` self-score informs which; the human overrides freely.
- **1–3 real alternatives** only — no strawmen, no filler; one genuine path → show one.
- **Every option is described** — pick and each alternative carry a one-line description.
- **Human gates only** — render at `[human gate]` points; not at `[you drive]` steps.

**The ask itself** — when the APPROVE block becomes an `AskUserQuestion` picker: recommended option goes first with `(Recommended)` suffix. On tools without `AskUserQuestion`, render as a numbered/`▶` menu. The question is a summary, never the artifact — intent + what "yes" means + the flag count.

## Hard rules

<constraints>
- **Summary-first.** Never bury the decision under a task list or a diff.
- **Show before ask.** Render the artifact (digest · diff · report) before any approval question. PLAN/SHAPE counts as the artifact here too.
- **Guided decision.** At a `[human gate]`, APPROVE is a guided choice — one `▶ … (recommended)` + 1–3 described alternatives; never a bare next step.
- **Reconcile the count.** FLAGS must reconcile with `add.py report --decide`'s open-item count before the ask. Engine wins if prose disagrees — fix the data, not the sentence.
- **Never pre-stamp a human decision point.** Freeze / gate / lock fields stay DRAFT or blank until the answer returns: show → ask → stamp → advance.
- **Never dump raw engine output as the plan.** Summarize `add.py status`/`report` through PLAN/SHAPE (or prose) — the engine's full verbosity is for `add.py` itself, not the chat message wrapped around it.
- **One report per decision point.** After an approval, point at the frozen artifact — do not re-render the bundle.
- **Batch, don't serialize.** N same-gate decisions ready together (intake items · ready-to-freeze contracts) render as ONE report: PLAN lists each item with its own lowest-confidence flag; APPROVE covers the batch in one ask, and any item can be held back by name.
- **Honest scope.** "Done" means the request, not the last task: report "task 2/3", never "done" while approved scope remains.
- **The question is a summary, never the artifact.** A compact SUMMARY · FLAGS block sits in chat immediately before the ask; the question text itself is two lines at most — intent + what "yes" means + flag count — pointing at the report above.
- **NEXT is not a second gate.** The single decision stays in APPROVE; NEXT is ranked recommendations only.
- **DECIDED never holds a gate-class call.** Security / residue / lowered-autonomy calls escalate in APPROVE.
- **Recorded, not just performed.** Rendering this template at a gate is recorded, not assumed — TASK.md's `Reported: yes` (§3/§6) is the mechanical trace; `add.py audit` surfaces an unrecorded one (`contract_report_unrecorded` / `verify_report_unrecorded`), a spot-audit the backstop.
</constraints>
