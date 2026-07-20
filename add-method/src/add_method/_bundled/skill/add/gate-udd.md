# Gate reports — the text-mode UDD gate surface (for the AI, not add.py)

The engine renders artifacts (`report`, `report --decide`, `status`); this file governs the CHAT MESSAGE you wrap around them. Use it at every human gate; its UDD-family design home is `design.md`.

**The fitting persona owns the gate report** — these are PRINCIPLES, not a fixed template: CONVEY the content below, but the persona owns structure, order, and cadence per project. The layout shown is a sensible DEFAULT; the four floors (below) it may never drop.

## The decision banner — rendered first, above everything

Every report at a human gate opens with a banner line, so a human scanning a long chat can spot "this needs my input" without reading prose:

```
════════════════════════════════════════════════════════════════
 PLAN · <task/milestone title, bold> · <gate name> → APPROVE?
 📄 <task's PLAN.md path>  ·  <milestone's MILESTONE.md path>
════════════════════════════════════════════════════════════════
```

- The title is the real H1 from PLAN.md/MILESTONE.md, **bolded** — not the bare slug.
- The path line names the actual file(s) so the human can open them directly; omit the milestone half for a milestone-free/fast task.
- Any `§`-numbered section named anywhere in the report (SHAPE, FLAGS, APPROVE, NEXT) is **bolded** — e.g. `**§3 CONTRACT**` — so a scanning eye finds exactly which part of the file is in play.

## The decision arc — rendered next

Every report at a human gate carries the **ARC** — three labelled lines placing the decision in the work's whole arc. Render it right after the banner, then a separator, then the report blocks:

```
ARC  goal: <the milestone / project goal this decision serves>
     done: <proven progress — tasks done · exit-criteria met · what this gate proves>
     plan: <this gate → the next step → the goal>
```

- **goal** — read from `m-goal` in `add.py status --all`; never from memory.
- **done** — proven progress only: exit-criteria met/total, tasks done, what this gate proves. An honest fact, never a hope.
- **plan** — this gate → the next step → the goal, mirroring the rollup's `DECIDE NEXT` line.

The arc is required at every human gate: **baseline-lock · contract-freeze · verify · intake · scope · milestone-close · graduation**. It is presentation only — it adds no gate and changes no PASS / RISK-ACCEPTED / HARD-STOP / freeze decision.

Its facts are engine-sourced (goal = `m-goal` · done = exit-criteria + tasks done · plan = `DECIDE NEXT`); if your arc and `add.py` disagree, the engine wins.

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

- **Collapse done to a count** (never enumerate finished); **cap live items ~5–7**, dependency-ordered, footer `+N more queued`; one line each — never restate the PLAN.md.
- **Glyphs fixed** — ✅ done · 🔄 active · ⬜ pending · ⚠ blocked/flagged; never invent new ones.
- **Sourced from `add.py status`, summarized by you** — never pasted raw into chat.
- **SHAPE is freeze-only** — the concrete shape being locked, so the human reviews it, not commentary.
- **BUILD PLAN is the HOW** — at a freeze `report --decide` also renders the §3 Build-strategy (Scope · batches · Persona · Spawn) as a `BUILD PLAN (§3 …)` block, so the human approves how the build runs, not only the SHAPE; placeholders skipped.

## The report blocks — what to convey (you own the order)

A gate report CONVEYS these; the persona owns the order and may merge, reorder, or trim to fit the project — conveying each (write "none" rather than silently dropping one), never dropping a floor. A sensible default order follows, not a mandate; add MORE when needed.

```
SUMMARY   one line: intent + target + where we are + what we done
FLAGS     lowest-confidence first: why + cost-if-wrong
DECIDED   highest-confidence first: the autonomous calls you made + why each was safe
EVIDENCE  small table: tests · gates · parity · check — engine-sourced
APPROVE   what you need from the human (or "none — FYI") — exactly one — sits last, right before the ask
NEXT      the recommended next actions, ranked (top ▶ highlighted, bolded) + what each unlocks
```

- **SUMMARY** never optional — one line even when PLAN/SHAPE carries the context. **FLAGS** lowest-confidence-first (why + cost-if-wrong; quote PLAN.md `⚠` / `- [~]` / `- [ ]` verbatim). **DECIDED** highest-confidence-first ("none" when none; never a security / residue / lowered-autonomy call). **EVIDENCE** engine-sourced, never re-typed. **APPROVE** the guided ask, last, after show-before-ask. **NEXT** ranked recommendations, not a second gate. **The ask itself** is a summary, never the artifact.

### Beyond the core blocks

When a report needs more — a `RISK` ledger, a `DIFF`, a `SCOPE` map — add an extra block (SCREAMING-CASE label · one-line intent · engine-sourced) AFTER EVIDENCE and BEFORE APPROVE. Add only when it carries what the core blocks don't; never pad; never drop a core block.

### The APPROVE block as a guided choice

```
APPROVE  <the question>

  ▶ <recommended option>  (recommended)
      <one-line description — what it means · what it unlocks or costs>
    <alternative option>
      <one-line description>
```

- **Exactly one** `▶ … (recommended)` (per the confidence self-score, `phases/direction.md`; human overrides) + **1–3 real alternatives**, each described — no strawmen. **Human gates only** (`[human gate]`, not `[you drive]`). As an `AskUserQuestion` picker: recommended first with `(Recommended)`; else a numbered/`▶` menu. The question is a summary, never the artifact — intent + what "yes" means + flag count.

## The four floors — the persona owns the form, never these

Whatever shape the persona renders per project, it MUST hold all four:
- **show-before-ask** · **one-approval-at-the-freeze** · **never-pre-stamp** a human decision point
- **security = HARD-STOP** — the one **un-persona-negotiable** floor: a security finding is never persona-softened (the human alone may strike this carve-out). The "## Hard rules" below detail how they play out.

## Hard rules

<constraints>
- **Summary-first.** Never bury the decision under a task list or a diff.
- **Show before ask.** Render the artifact (digest · diff · report) before any approval question; PLAN/SHAPE counts too.
- **Guided decision.** At a `[human gate]`, APPROVE is a guided choice — one `▶ … (recommended)` + 1–3 described alternatives; never a bare next step.
- **Reconcile the count.** FLAGS must reconcile with `add.py report --decide`'s open-item count before the ask. Engine wins on disagreement — fix the data, not the sentence.
- **Never pre-stamp a human decision point.** Freeze / gate / lock fields stay DRAFT or blank until the answer returns: show → ask → stamp → advance.
- **Never dump raw engine output as the plan.** Summarize `add.py status`/`report` through PLAN/SHAPE (or prose) — the engine's verbosity is for `add.py`, not the chat wrapped around it.
- **One report per decision point.** After an approval, point at the frozen artifact — do not re-render the bundle.
- **Batch, don't serialize.** N same-gate decisions ready together (intake items · ready-to-freeze contracts) render as ONE report: PLAN lists each with its own lowest-confidence flag; APPROVE covers the batch in one ask, any item held back by name.
- **Honest scope.** "Done" means the request, not the last task: report "task 2/3", never "done" while approved scope remains.
- **The question is a summary, never the artifact.** A compact SUMMARY · FLAGS block sits in chat immediately before the ask; the question text itself is two lines at most — intent + what "yes" means + the flag count — pointing at the report above.
- **NEXT is not a second gate.** The decision stays in APPROVE; NEXT is ranked recommendations only.
- **DECIDED never holds a gate-class call.** Security / residue / lowered-autonomy calls escalate in APPROVE.
- **Recorded, not just performed.** A gate render is recorded, not assumed — PLAN.md `Reported: yes` (§3/§6) is the trace; a human spot-audit is the backstop for a missed render.
</constraints>
