# 03 · Step 1 — Specify

[← 02 The flow](./02-the-flow.md) · [Contents](./README.md) · Next: [04 Step 2 Scenarios →](./04-step-2-scenarios.md)

> **Purpose:** state, in plain language, what the feature must do and what it must reject, with no ambiguity left for the AI to resolve by guessing.
> **Produces:** the **§1 SPECIFY** block of the task's `TASK.md` (one file per task — what this chapter is the *why* behind; historically a separate `SPEC.md`).
> **How it works — co-specification:** AI and human **brainstorm the shape together**; the AI drafts; the **human validates, with the AI's advice.** The decisive advice is a *lowest-confidence flag* — the AI names the one or two things most likely to be wrong, so the human's attention lands where it matters. The human owns the decision; the AI owns surfacing what it does not yet know.

---

## Why this step is first

The specification is the description the AI will build from. Every other artifact descends from it. Anything vague here does not stay vague — it becomes a concrete wrong guess in the code, discovered late. The cheapest moment to remove an ambiguity is now, in a sentence, before anything depends on it.

There is also a diagnostic value: **if you cannot write the spec, you do not yet understand the feature well enough to build it.** The inability to specify is information, not an obstacle to push past.

## Co-specification — how the spec gets made

A specification is not dictated by one side. It is made in three moves:

1. **Diverge — brainstorm by both.** Before drafting, the AI surfaces the *decision space*: the two or three genuine ways to frame the feature, and the open questions it would otherwise resolve by guessing. You react — add, kill, redirect. This is the brainstorm, and it lives in the conversation, not in a new document.
2. **Converge — the AI drafts, and ranks its own uncertainty.** The AI writes the spec below, then ranks where its confidence is lowest. It does not hand you a flat list of equal-looking assumptions to nod through; it tells you *where it is most likely wrong, and what that would cost.*
3. **Validate — you decide, with the AI's advice.** You read the ranked uncertainty first, then confirm, correct, or send it back. Your approval is real because your attention was aimed.

The brainstorm leaves a *light trace, not a document.* What you chose becomes a rule; what you weighed and dropped becomes a one-line **`Framings weighed:`** note; what stayed genuinely uncertain becomes a **lowest-confidence flag**. Nothing new to maintain — the residue lands in the spec you were writing anyway.

## What a good specification contains

Four parts, kept short:

1. **Must** — the behaviors the feature is required to perform.
2. **Reject** — the inputs or situations it must refuse, each paired with a named error.
3. **After** — the state that is true once it succeeds (what changed).
4. **Assumptions — lowest-confidence first** — the things you are taking for granted, **ranked so the most-likely-wrong come first.** The top one or two carry a `⚠` flag with *why it is uncertain* and *what it costs if wrong*; the rest are the low-stakes tail. A spec with genuinely nothing uncertain still names its single biggest risk, however small — the AI never claims a blank mind.

Naming the errors matters. "Reject bad amounts" is an instruction to guess; `amount <= 0 -> "amount_invalid"` is a rule that produces a testable scenario and a defined contract response.

### Rule IDs (optional — opt-in by usage)

Give each Must a stable `M<n>:` ID; a Reject's own error code already IS its ID (referenced later as `R:<error_code>`). Once a task uses a tag anywhere in §2 SCENARIOS or §4 TESTS, `add.py check` starts asking that every Must/Reject be covered by a scenario tag or a test's `covers:` line — a task that never tags anything is never retro-flagged. See the template's own inline example for the exact grammar.

## Template

```
# SPEC.md
Feature: <name>
Framings weighed: <chosen> (chosen) · <alternative> · <alternative>
Must:
  - <required behavior>
Reject:
  - <bad input / situation> -> "<error_code>"
After:
  - <what is true once it succeeds>
Assumptions — lowest-confidence first:
  ⚠ <most-likely-wrong assumption> — lowest confidence because <why>; if wrong: <cost>
  - [x] <confirmed / low-stakes assumption> — <one line>
```

## ▶ Example

```
Feature: Transfer money between my own accounts
Framings weighed: synchronous single-currency transfer (chosen) · queued transfer · multi-currency with FX
Must:
  - move an amount from one of my accounts to another of mine
  - amount > 0
  - source and destination are different accounts
  - source has enough balance
After:
  - source balance -= amount, destination balance += amount
Reject:
  - amount <= 0           -> "amount_invalid"
  - source == destination -> "same_account"
  - balance < amount      -> "insufficient_funds"
  - account not mine      -> "forbidden"
Assumptions — lowest-confidence first:
  ⚠ same currency only (no FX) in v1 — lowest confidence because the ticket never said; if wrong: the whole amount/rounding model changes and this contract is wrong
  - [x] no daily limit in v1 — confirmed: out of scope for v1
```

The `Framings weighed:` line shows what was considered and dropped, so the chosen shape is a *decision*, not a default. The `⚠` line is the one the stakeholder reads first: the assumption most likely to be wrong and most expensive to get wrong. The flat `[x]` line is real but low-stakes. A reviewer can now spend their attention where it pays.

## The AI's role here

Use the AI to **open the space and then narrow it honestly.** First it brainstorms the genuine framings with you (diverge). Then it drafts the spec from whatever raw material you have — a ticket, an interview, a contract document — listing every assumption it had to make, **ranked lowest-confidence first**, and flagging the one or two it is least confident in with *why* and *what it costs if wrong*. Its instinct is to fill gaps silently and present a confident wall; the method forces those gaps into the open, and forces the confident wall to declare its own soft spots. See `playbook/1_specify.md` in [Appendix B](./appendix-b-prompts.md).

The defining instruction: *if a requirement is unclear, ask — do not resolve it by guessing — and of the things you must assume, say plainly where your confidence is lowest.*

## Common mistakes

- **Stating only the happy path.** The "Reject" list is where most real complexity lives; an empty one usually means it has not been thought through.
- **Free-text errors.** Errors must be named codes, not sentences, so they can become scenarios and contract responses.
- **Hidden assumptions.** If an assumption is not written down, it is not confirmed — it is a future bug with a delay timer.
- **A flat list of "confirmed" assumptions.** Eight equal-looking ticks invite a reflex approval. Rank them; flag the one or two that are load-bearing. An unranked list hides the risk inside the noise.
- **"Existing behavior" claims without a citation.** An assumption row that asserts "this is how X works today" is describing intent, not code. Any wiring claim or assumption that depends on the current state of an existing path must carry a grep/line citation (e.g. `file.rs:203`) — otherwise it is a future bug in disguise.
- **Wiring claims that name a symbol, not a caller chain.** Verifying that a function exists is not the same as verifying it is reachable. A wiring claim is only valid when it names the production caller chain from an actual entry point — not just the symbol's location in a file. A function that nothing calls is dead, not wired.

## Exit check

A spec is done when:

- [ ] Every required behavior is stated explicitly.
- [ ] Every rejection has a named error code.
- [ ] The success state-change is described.
- [ ] The assumptions are ordered lowest-confidence first, and the one or two `⚠` flags carry *why* + *cost* — or, for genuinely trivial scope, an honest "none material" that still names the single biggest risk.

The shift from older practice: you no longer pre-confirm every assumption to advance. You confirm that the AI has *ranked* its uncertainty and that you have *engaged the top of the rank.* Stated honestly: the flag makes a genuine review cheap and a lazy one visibly negligent — it cannot force the read. That is the most a lightweight check can buy.

## If the check fails

If you cannot state a rule clearly, the feature is not ready to build. Stop, take the question to whoever owns the requirement, and resolve it. Do not let the AI proceed on an unresolved point — that is the exact failure the whole method exists to prevent.

---

## The one approval, and where the flag really lands

In the one-approval flow, you do not approve the spec alone — you approve the whole frozen bundle (spec, scenarios, contract, tests) once, at the contract freeze. So the lowest-confidence flag is **bundle-wide**: at that single decision point the AI leads with *"of everything I'm asking you to freeze, these one or two points are most likely wrong"* — and a flag may point at an uncovered scenario or the contract shape, not only a spec assumption. The ranking you do here in Specify is the first input into that one gate. See [05 Contract](./05-step-3-contract.md) and the `add` skill's `run.md`.

---

## When the feature has a user interface

For anything with a UI, extend this step with a quick design: the **user flows** (the happy path and the main alternatives) and **every screen state** — loading, empty, error, and success. Correct logic behind a confusing or incomplete interface is still a poor product, and undesigned states are exactly where an AI will improvise something ugly. In the early **Prototype** stage, this design work is the main event and the code is throwaway (see [10 Stages](./10-setup-and-stages.md)).
