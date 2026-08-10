# Gate — the human-decision surface (presentation only)

The engine renders facts (`add status`, `add gate`, `add brief`); this file governs the CHAT MESSAGE
you wrap around them at every human gate — intake · freeze · verify · milestone-close. It is
**presentation only**: it adds no gate, moves no floor, and changes no PASS / RISK-ACCEPTED /
HARD-STOP / freeze verdict. Its facts are **engine-sourced** — if your wording and `add` disagree,
the engine wins; fix the data, not the sentence.

**The fitting persona owns the render** — these are PRINCIPLES, not a fixed template. CONVEY the
content below; the persona owns structure, order, and cadence per project. The layout shown is a
sensible DEFAULT; the four floors it may never drop are at the end.

## The banner — first, above everything

So a human scanning a long chat spots "this needs me" without reading prose:

```
════════════════════════════════════════════════════════════════
 PLAN · <task/milestone title, bold> · <gate name> → APPROVE?
 📄 <task's PLAN path>  ·  <milestone node path — milestones/<slug>.md>
════════════════════════════════════════════════════════════════
```

- Title is the real H1 (bolded), not the bare slug. Name the actual file(s) so the human opens them;
  omit the milestone half for a milestone-free task.
- Any `§`-named section referenced in the report is **bolded** (`**§3 PLAN**`) so a scanning eye lands.

## The ARC — rendered next

Three labelled lines placing the decision in the whole arc — right after the banner, then a separator:

```
ARC  goal: <the milestone / project goal this decision serves>
     done: <proven progress — tasks done · exit-criteria met · what this gate proves>
     plan: <this gate → the next step → the goal>
```

- **goal** — read from the milestone goal in `add status --all`, never from memory.
- **done** — proven progress only: exit-criteria met/total, tasks done, what this gate proves. An
  honest fact, never a hope.
- **plan** — this gate → the next step → the goal.

Required at every human gate. It adds no gate; it only frames the one already there.

## Show before ask — the report blocks

Render the artifact BEFORE the question. A gate report CONVEYS these; the persona owns the order and
may merge or trim to fit — convey each (write "none" rather than silently dropping one), never drop a
floor:

```
SUMMARY   one line: intent + target + where we are + what's done
FLAGS     lowest-confidence first: why + cost-if-wrong
DECIDED   highest-confidence first: the autonomous calls you made + why each was safe
EVIDENCE  small table: tests · gates · residue · check — engine-sourced, never re-typed
APPROVE   what you need from the human (or "none — FYI") — exactly one — sits last
NEXT      ranked recommended actions (top ▶ bolded) + what each unlocks
```

- **SUMMARY** never optional. **FLAGS** lowest-confidence-first, quoting `⚠` / `- [~]` / `- [ ]`
  verbatim. **DECIDED** never holds a security / residue / lowered-autonomy call — those escalate in
  APPROVE. **EVIDENCE** engine-sourced. **NEXT** is not a second gate.
- Need more? Add an extra block (SCREAMING-CASE label · one-line intent · engine-sourced) AFTER
  EVIDENCE and BEFORE APPROVE. Never pad; never drop a core block.

## APPROVE as a guided choice

```
APPROVE  <the question>

  ▶ <recommended option>  (recommended)
      <one line — what it means · what it unlocks or costs>
    <real alternative>
      <one line>
```

- **Exactly one** `▶ … (recommended)` (per the direction confidence self-score; the human overrides)
  + **1–3 real described alternatives** — no strawmen. As an `AskUserQuestion` picker: recommended
  first, marked `(Recommended)`. The question is a summary, never the artifact — intent + what "yes"
  means + the flag count, two lines at most, pointing at the report above.

## The four floors — the persona owns the form, never these

- **show-before-ask** — render the artifact before any approval question; ARC/report counts.
- **one-approval-at-the-freeze** — one crossing per decision; do not serialize sub-approvals.
- **never-pre-stamp** — freeze / gate / lock fields stay DRAFT or blank until the answer returns:
  show → ask → stamp → advance.
- **security = HARD-STOP** — the one **un-persona-negotiable** floor: a security finding is never
  persona-softened; only the human may strike this carve-out.

<constraints>
- **Summary-first.** Never bury the decision under a task list or a diff.
- **Reconcile the count.** FLAGS must match the engine's open-item count before the ask. Engine wins.
- **One report per decision point.** After an approval, point at the frozen artifact — do not re-render.
- **Batch, don't serialize.** N same-gate decisions ready together render as ONE report; APPROVE
  covers the batch in one ask, any item held back by name.
- **Honest scope.** "Done" means the request, not the last task: report "task 2/3", never "done"
  while approved scope remains.
- **Presentation only.** This file never adds a gate, moves a floor, or overrides a verdict.
</constraints>
