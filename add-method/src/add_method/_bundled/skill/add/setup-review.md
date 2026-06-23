# Setup review — the one page the human signs

Autonomous setup ends at a single human gate: the **baseline approval** (`add.py lock`). `SETUP-REVIEW.md` is that page: every decision you made while drafting the foundation, first-scope, and the first contract, **ordered lowest-confidence-first** so the riskiest guesses meet the human's eye first.

The engine never reads this file — `add.py lock` is judgment-free, the signature *is* the gate. The human **reading** this page is the review.

## Where it lives

Write **one** artifact at `.add/SETUP-REVIEW.md`. **Never clobber a human-edited one** — if it already exists with hand edits, append/update, don't overwrite. It sits beside `PROJECT.md`, not under a task.

## The template

```markdown
# SETUP REVIEW — <project>

<stage> · <brownfield | greenfield> · drafted by <model> @ <date>

| # | Decision | Lands in | Tag | Why / Evidence |
|---|----------|----------|-----|----------------|
| 1 | <the drafted decision> | PROJECT.md \| scope \| first-contract | `guessed` | <the inference + why you had to guess> |
| 2 | <…> | <…> | `evidence-grounded` | <cite the source file/line you read it from> |

Sign: confirm in chat → the agent runs `add.py lock --by "<name>"` (typing it yourself works too)
```

Rows are numbered for reference at the gate ("row 1 is where my confidence is lowest").

## The two rules that make it honest

<constraints>
1. **Lowest-confidence-first.** Order rows by confidence **ascending**. A `guessed` row always floats above an `evidence-grounded` one. The top of the table is the part the human actually needs to challenge.

2. **Every row is tagged — `guessed` or `evidence-grounded`.**
   - `evidence-grounded` — you read it from the code/repo. **Cite the file** (e.g. `pyproject.toml`). Brownfield onboarding (see `adopt.md`) is mostly these.
   - `guessed` — the repo was silent, so you inferred it. **State the inference and why.** Thin-greenfield onboarding produces these. These are what the human must check; that is why they sit on top.

   The tag vocabulary is shared with `adopt.md` — brownfield map tags flow straight into this table.
</constraints>

## Where it ends

`SETUP-REVIEW.md` is read-only context for the baseline approval — present it lowest-confidence-first, not field-by-field; the human confirms in conversation; you run the lock:

```bash
python3 .add/tooling/add.py lock --by "<name>"
```

`lock` records the lock layers and opens the build — it does **not** parse or validate this file. Make the top of the table the truth they most need.
