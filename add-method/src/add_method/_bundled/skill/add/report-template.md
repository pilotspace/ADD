# Chat reports — the decision-point template (for the AI, not for add.py)

The engine renders artifacts (`report`, `report --decide`, `status`); this file governs the CHAT MESSAGE you wrap around them.

Use it every time you report at or near a decision point.

## The decision arc — rendered first, above the report blocks

Every report at a human gate opens with the **ARC** — three labelled lines placing the decision in the work's whole arc. Render it first, then a separator, then the report blocks:

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

- **verify** — `goal:` ship the decision arc · `done:` report-arc tests 6/6 green · `plan:` PASS → wire the arc into every gate → goal.
- **contract-freeze** — `goal:` … · `done:` bundle drafted, lowest-confidence flag surfaced · `plan:` freeze §3 → build → goal.

## The report blocks, in order

Render every block (write "none" rather than dropping one); add MORE when needed.

```
SUMMARY   one line: intent + target + where we are + what we done
DECISION  what you need from the human (or "none — FYI") — exactly one
FLAGS     lowest-confidence first: why + cost-if-wrong
DECIDED   highest-confidence first: the autonomous calls you made + why each was safe
EVIDENCE  small table: tests · gates · parity · check — engine-sourced
NEXT      the recommended next actions, ranked (top ▶ highlighted, bolded) + what each unlocks
```

1. **SUMMARY** — one line: intent + target + position.
2. **DECISION** — as a **guided decision**: one `▶ … (recommended)` + 1–3 described alternatives. Exactly one per report, or "none — FYI". Ask after everything below (show-before-ask).
3. **FLAGS** — lowest-confidence first, each with *why* and *cost if wrong*. Where TASK.md markers exist (`⚠` / `- [~]` / `- [ ]`), quote verbatim and keep document order.
4. **DECIDED** — high-confidence autonomous calls, highest-confidence first, each with *why* it was safe. "none" when none. NEVER list a security / residue / lowered-autonomy call here.
5. **EVIDENCE** — engine-sourced facts from `add.py` output, never re-typed.
6. **NEXT** — ranked next actions, top one marked `▶` with what it unlocks. Mirror the rollup's `DECIDE NEXT` for the top action; overrule it only with a stated reason. **Informational, not a second gate**.

### Beyond the core blocks

When a report needs more — a `RISK` ledger, a `DIFF`, a `SCOPE` map — add an extra block (SCREAMING-CASE label · one-line intent · engine-sourced where possible) AFTER EVIDENCE and BEFORE NEXT. Add only when it carries what the core blocks don't; never pad; never drop a core block.

### The DECISION block as a guided choice

```
DECISION  <the question>

  ▶ <recommended option>  (recommended)
      <one-line description — what it means · what it unlocks or costs>
    <alternative option>
      <one-line description>
```

- **Exactly one** option carries `▶ … (recommended)`. `confidence.md` self-score informs which; the human overrides freely.
- **1–3 real alternatives** only — no strawmen; if there is genuinely one path, show one — never invent filler to reach three.
- **Every option is described** — pick and each alternative carry a one-line description.
- **Human gates only** — render at `[human gate]` points; not at `[you drive]` steps.

**The ask itself** — when block 2 becomes an `AskUserQuestion` picker: recommended option goes first with `(Recommended)` suffix. On tools without `AskUserQuestion`, render as a numbered/`▶` menu. The question is a summary, never the artifact — intent + what "yes" means + the flag count.

## Hard rules

<constraints>
- **Summary-first.** Never bury the decision under a task list or a diff.
- **Show before ask.** Render the artifact (digest · diff · report) before any approval question.
- **Guided decision.** At a `[human gate]`, block 2 is a guided choice — one `▶ … (recommended)` + 1–3 described alternatives; never a bare next step.
- **Reconcile the count.** FLAGS must reconcile with `add.py report --decide`'s open-item count before the ask. Engine wins if prose disagrees — fix the data, not the sentence.
- **Never pre-stamp a human decision point.** Freeze / gate / lock fields stay DRAFT or blank until the answer returns: show → ask → stamp → advance.
- **One report per decision point.** After an approval, point at the frozen artifact — do not re-render the bundle.
- **Honest scope.** "Done" means the request, not the last task: report "task 2/3", never "done" while approved scope remains.
- **The question is a summary, never the artifact.** A compact SUMMARY · DECISION · FLAGS block sits in chat immediately before the ask; the question text itself is two lines at most — intent + what "yes" means + flag count — pointing at the report above.
- **NEXT is not a second gate.** The single decision stays in DECISION; NEXT is ranked recommendations only.
- **DECIDED never holds a gate-class call.** Security / residue / lowered-autonomy calls escalate in DECISION.
</constraints>
