# 07 · Setup and the four lanes

[← 06 The loop — observe, learn, close](./06-the-loop.md) · [Contents](./README.md) · Next: [08 Parallel work — waves and worktrees →](./08-parallel-work.md)

---

## Setup: the AI drafts, you approve the baseline

Before the first feature, the project needs a foundation — but standing it up is no longer your chore. One command creates the bundle the whole project depends on:

```bash
add init --profile code "<name>"      # also: --profile doc
```

`init` **vendors the engine and the seed persona corpus into `.add/`**, so the bundle runs standalone — the `add` you call afterwards is that vendored copy, and the project never has to have this repo. It writes the five empty **living specs** under `.add/specs/`, and it is idempotent: a re-run never clobbers a file a human already wrote.

**What the AI drafts.** From an existing codebase it works from the code — the code answers the questions a setup interview would ask. On an empty repo it interviews you briefly, then drafts. Either way it fills the five living specs — the standing picture every task reads — and drafts the first milestone and its first task:

| Spec (`.add/specs/`) | Holds |
|------|-------|
| `domain` | what the product must be true about |
| `system` | how it is built, and what that forecloses |
| `experience` | who uses it and what they feel |
| `quality` | what counts as proof |
| `method` | how work proceeds, and what a gate costs |

These are the specs the `learn` lenses (`ddd · sdd · udd · tdd · add`) fold back into as the project runs — the documentation that outlives all the code. Drafting them is AI-owned and adds no approval; it aims the whole project at reality instead of assumption.

**The baseline approval.** There is no separate review ceremony and no review file to sign — the baseline is approved the same way every task is: **one freeze**. When the specs, the first milestone, and the first task's contract are drafted, a person freezes that first task:

```bash
add freeze <slug> --by "<name>" --authority human
```

That single act is the [contract freeze](./03-direction.md) doing double duty: it approves the foundation and the first contract together, and it opens the first build. Before the freeze the engine lets the AI draft but refuses to cross into build; after it, the build opens. The AF leads with its lowest-confidence guess so your one signature is aimed, not given blind.

**Setup exit check**

- [ ] `add init` has vendored the engine + seed personas into `.add/`, and the five living specs exist.
- [ ] The specs are drafted — from the code on a brownfield repo, from a short interview on an empty one — with the AI's thinnest guesses flagged.
- [ ] A first milestone and its first task are drafted.
- [ ] A person **froze** the first task — and only then did its build open.

Do not start a feature until the foundation is frozen. The baseline freeze turns the AI's draft into committed direction; from there, every change flows through the three-beat loop.

---

## The four lanes: size the request before you create scope

Not every request deserves a full task, and forcing one onto a typo is ceremony. Before any node exists, ADD reads the raw request into shape and routes it to the **cheapest lane that fits**. The AI proposes the lane; **the human vetoes** — you never create scope without a confirmed proposal. This replaces the old instinct to pick a "size of project" up front: you size each request as it arrives.

**Quick — below the scope floor.** Fits when *all* hold: one file or a few adjacent ones · behavior the specs already cover (a typo, a wording fix, a config value, a mechanical rename) · no new contract surface anyone consumes · mechanical sensitivity. Then there is **no task node** — you make the edit and leave a receipt:

- the **git diff** is the change record (commit as usual);
- `add learn <ddd|sdd|udd|tdd|add> "<lesson>" --evidence <ref>` files what was learned into the living spec. A quick lane that teaches nothing appends nothing.

**Task — one atomic node.** Fits the active milestone's scope, or is a single behavior that needs a frozen contract. Create the node and run the three-beat loop:

```bash
add new Task <slug> --title "..." --depth quick|standard|deep
```

**Explore — the answer IS the deliverable.** Fits when the primary work is *answering questions*,
not editing — investigate a defect, evaluate a library, research an approach — whatever the
eventual code size. One Task node with `--kind explore`: the questions freeze as the contract, a
hard budget caps the loop, and a cited `## FINDINGS` brief is the deliverable. High uncertainty
routes here FIRST — one contract-shaping unknown already argues explore-first, because freezing a
contract on a guess ships the wrong thing with perfect receipts. The full lane, its engine floors,
and the rest of the dynamic path are chapter [19](./19-dynamic-workflow.md).

**Project / milestone — a theme or a slice.** A new product theme no active milestone covers, or a slice too big for one task. Draft the milestone *first* — **goal · in/out scope · exit criteria · a breadth-first task list** (each task a `slug · depends-on · one line`) — confirm it, then create it and list its tasks. `add milestone-done` refuses to close a milestone while any exit box is unchecked.

### The closed floor — what always sizes up

A change touching **security · data · architecture** ALWAYS becomes a real task — never Quick, no matter how small. New behavior, a new or changed contract, or anything you would want a frozen `gives:` for → a Task at least. **Security is a HARD-STOP everywhere.** The route is the AI's to propose; the veto is the human's — "make it a task" always wins. When in doubt, size up.

> **Do:** route a typo or a config bump to Quick and leave a receipt — no node.
> **Don't:** send anything touching auth, data, or an architectural boundary to Quick, however trivial the diff looks.

### Change-request — touching already-frozen scope

If the request modifies a **frozen** contract or a shipped promise, it is not new scope — it is a change-request back to Direction of the affected node: the old `gives:` stays, a refreeze stamp lands, and dependents that `need:` it are flagged stale. Never fork the truth into a parallel node.

---

## The depth dial: same steps, tuned ceremony

Depth is neither a lane nor a phase — it is a dial on **how much ceremony a single task carries**. The steps never change as you turn it; what changes is how heavily you run each one. Crucially, **depth tunes ceremony, never authority.** The authority floor is computed from the task's `sensitivity:` — `security → human`, `data | architecture → plan`, else `process` — so turning the dial down can lighten the paperwork but can never lower who must sign.

- **quick** — the lean node (CARD · CHECKS · EVIDENCE). At a green, `covers`-bound receipt the AI may record the PASS itself at `process` authority — an explicit pass you run, not an engine auto-verdict — *unless the sensitivity floor is higher*.
- **standard** — the full node, evidence-gated, at whatever authority the floor computes.
- **deep** — the full node plus milestone strategy, presented lowest-confidence-first; a human owns the freeze whenever the floor, or your own judgment, calls for it.

> **Do:** dial a well-understood, mechanical task down to `quick` to spend less ceremony on it.
> **Don't:** expect `quick` to lower the gate on security or data work — the `sensitivity:` floor holds no matter where the dial sits.

The pace of a project is set by judgment and review capacity, not by how fast the AI can type. Adding more AI does not compress the human-led decision points; it only fills the gaps between them — which is exactly what [parallel work](./08-parallel-work.md) is for.

---
