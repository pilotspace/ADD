# Intake — size a request into versioned scope

Before a task exists, ADD turns a raw request into correctly-sized, versioned scope — the
**intake level** (the per-task flow is phases 0–7; intake is the step *before* a task). You
(the AI) **propose**; the human **confirms**. Never create scope without a confirmed proposal.

## Load the fitting persona first

Intake is a decision — size it WITH the project's expertise, not generically. Before you
analyze or size, load the fitting persona (the PM / product-direction lens), exactly as
`design.md` loads the design-fit persona:

- **match** a persona in `.add/personas/` by role/flow (frontmatter, else description-match)
  — e.g. a `product-lead` / `method-product-owner` lens;
- **none fits?** seed from `.add/personas-teacher/` via the add agent in persona mode, then
  load — offered, **never required**;
- the persona shapes the framing, the latent-requirement read, and the sizing tradeoffs. It
  is **advisory**: it never lowers the `ask_human` floor, the frozen-scope tie-break, or the
  security-always-escalates rule.

No fitting persona and none seeded? Proceed generically — intake still runs. The persona already
OWNS the intake report (`gate-udd.md`); loading it here makes it own the SIZING too, so the two agree.

## Analyze the request before you size it

A raw request is rarely a task yet — it is intent wrapped in prose. ADD's first job is not to
route it but to *read it into a task shape*. Do this BEFORE any bucket or interview:

1. **Restate the intent** in one line — the outcome the human wants, in their world, not the
   mechanism. If you cannot state it, it is underspecified → `ask_human` (never guess it).
2. **Extract the latent requirements** — the acceptance signals hiding in the ask ("fast",
   "secure", "works like X") are the measurable Targets in disguise; name each one explicitly.
3. **Name the unstated** — the assumptions, defaults, and edge behavior the prose skips. These
   become the interview agenda below; surface them, never silently fill them.
4. **Surface the hidden work** — the migrations, new contract surface, and risks a naive read
   misses. This is what separates a real task from a wish, and what escalates sensitivity.

This analysis IS the task's raw material: the restated intent seeds §1 grounding, the latent
requirements seed the §3 Target, the unstated becomes what the interview settles. Sizing (below)
only decides *where* the task lives — the analysis decides *what it is*. Skipping it is how a
vague prompt becomes a mis-sized, under-specified task.

## Interview before you size

Run `add.py search <keyword> ...` first — it surfaces overlapping/prior work in one command. When
the request is a question or won't place in one bucket, explore it WITH the user first: reflect
the intent, name in/out of scope, offer 2–3 sized options with a recommendation. Only then emit
`{ bucket, rationale, command }`. `ask_human` stays the floor: if interviewing can't sharpen it,
reject — never guess a bucket.

## The inline lane — below the bucket floor

Buckets create versioned scope; some changes are too small to deserve any. After the
interview sharpens the request, judge the lane FIRST — you (the AI) route it, silently:

**Inline fits when ALL hold**: one file or a few adjacent ones · behavior the current specs
already cover (a typo, a wording fix, a config value, a mechanical rename) · no new contract
surface anyone else consumes · sensitivity mechanical. Then: **no task, no milestone** — make
the edit directly, and leave the receipt:

1. the **git diff** is the change record (commit it as usual);
2. `add.py delta-append <dd> "<lesson>"` files what was learned into the living 5-DD spec —
   the spec diff IS the approval artifact; a lane run that teaches nothing appends nothing.

**The floor is closed**: a change touching **security · data · architecture** ALWAYS escalates
to a real task — never inline, no matter how small (security stays HARD-STOP everywhere).
New behavior, a new/changed contract, or anything you would want a frozen §3 for → bucket it.
The route is yours, the veto is not: the human saying "make it a task" overrides the lane,
always. When in doubt, bucket — the lane is for changes whose whole story fits in a diff.

## The four buckets

Classify every request into exactly ONE bucket:

| Bucket | Decision test | Implied command |
|--------|---------------|-----------------|
| `new-major` | a new product theme/pillar no active milestone's goal covers | `add.py new-milestone vN` |
| `sub-milestone` | a slice of an EXISTING major theme, too big for one task | `add.py new-milestone vN-M` |
| `task` | fits within the ACTIVE milestone's stated scope | `add.py new-task <slug>` |
| `change-request` | modifies ALREADY-FROZEN scope (a frozen contract or a shipped promise) | `add.py phase specify\|contract <affected>` |

**Tie-break order: the frozen-scope test runs FIRST, before the size test.** Ask "does this change
already-frozen scope?" → if yes it is a `change-request` (never re-size frozen work as new scope).
Only if no, apply the size test: a new theme → `new-major`; a slice of a live theme → `sub-milestone`;
fits the active milestone → `task`.

**Size the freeze, not the template (task bucket only).** ONE atomic template serves every task;
single behavior · no new contract surface others consume · sensitivity mechanical → propose drafting
the whole Direction bundle in one pass to a single freeze. Any doubt → draft §1–§4 beat by beat.

**One-task gap rule.** ONE task that does NOT fit the active milestone's scope: never force it
into `sub-milestone` — create a micro-milestone to house it (`new-milestone` + `new-task`) for
ledger attribution + clear exit criteria without inflating scope.

**Batched intake.** N same-bucket items arriving together classify as ONE proposal: one report,
one human confirm covering the batch — never N sequential asks. Mixed buckets stay
`split_required`.

## What you emit (the proposal)

Present the proposal via `gate-udd.md` — open with the ARC (goal · done · plan): the goal this
request serves, what is already covered, and the plan the chosen bucket sets up. Render it as a guided
choice — the recommended bucket + its described alternatives (per `gate-udd.md`). For every
request, emit ONE of:

- **a classification** — `{ bucket, rationale, command }` — `rationale` names WHY (the theme, the
  slice, the fit, or the frozen scope touched) and `command` is the exact `add.py …` from the table.
  The human confirms or overrides before you run it.
- **a rejection** — `{ reject, rationale }` — create nothing, from this closed set:

<reject_codes>
- `ask_human` — too ambiguous/underspecified to size. Ask the human; never guess a bucket.
- `frozen_scope` — it changes frozen scope; route it as a `change-request` back to SPECIFY/CONTRACT of
  the affected task — never spawn a parallel milestone that forks the truth.
- `split_required` — it spans more than one bucket; propose the SMALLEST set of correctly-sized items,
  each with its own rationale; never force it into one milestone.
</reject_codes>

When confirmed, record the `rationale` in the artifact you create or affect — the new MILESTONE.md
goal/body, the new PLAN.md, or a note in the affected PLAN.md — never in state.json.

## Roadmap — a request that is several milestones

Some requests decompose into **N>1 milestones of the same line** — a roadmap.
Don't create only the first and lose the rest. Instead:

1. **Propose** the roadmap — the ordered milestone list, each with a one-line goal.
2. **Confirm** — the human confirms before anything is created; never auto-create N
   milestones unprompted (the `ask_human` floor holds).
3. **Create** all N on confirm — the first with `add.py new-milestone <slug>` (active), the rest
   with `add.py new-milestone --queued <slug>` (status `queued`, not focused).
4. **Promote** — `add.py activate <slug>` flips each queued→active as started; one active
   milestone at a time, the queue is the agreed backlog surfaced at resume.

NOT `split_required` (that is for a request spanning **different buckets**); a roadmap is
several milestones of the **same line**, created queued.
