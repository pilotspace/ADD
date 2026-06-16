# Phase 1 — Specify (the rules)

Goal: state what the feature MUST do and what it must REJECT, with zero ambiguity
for the AI to resolve by guessing. Fill **§1 SPECIFY** in TASK.md.

Specify is **co-specification**: brainstorm the shape WITH the user, draft it, then let
the user validate with your advice. If you cannot write the spec, you do not yet
understand the feature — that is information, not an obstacle. Stop and ask.

## Co-specify in three moves

1. **Diverge** — before drafting, surface the decision space: the 2–3 genuine framings of the
   feature + the open questions you would otherwise guess. Invite the user to add, kill,
   redirect. (Conversational — no new file. At prototype/poc this shortens to one sentence.)
2. **Converge** — draft §1, then RANK where your confidence is lowest (below).
3. **Validate** — present the ranked uncertainty first; the user confirms, corrects, or sends back.

**Identity is direction, not default (UDD).** For UI/design work, identity values — the brand
color, the core palette, the typeface — are human-owned. Surface them for discussion during
Diverge; never assume a brand value. The UDD token dialect checks a token's *shape*; its *value*
is the user's call (`udd-tokens.md`). For a UI feature with a screen, run the design-definition
loop in `design.md` — domain → research and reuse components → wireframe → a real captured screen
the human confirms before build — and carry the confirmed layout into the contract.

**AI feature (EDD).** For a task created with `--kind ai`, run the eval-definition loop in `ai.md`
instead — spec → ladder → eval-set → freeze-the-contract — and carry the frozen eval contract
(`AI-SPEC.md` + the `.add/ai/` named set) into the bundle. Verify will gate on the measured eval
score, not a green unit suite. Silent for a non-AI task.

## Produce (in TASK.md §1)

<output_format>
- **Framings weighed** — a one-line trace of what you considered: `X (chosen) · Y · Z`.
- **Must** — each required behavior.
- **Reject** — each refused input/situation, paired with a **named error code**
  (`amount <= 0 -> "amount_invalid"`, never "handle bad input").
- **After** — the state that is true once it succeeds.
- **Assumptions — lowest-confidence first** — ranked most-likely-wrong → least. The top 1–2 carry a
  `⚠` flag: `⚠ <assumption> — lowest confidence because <why>; if wrong: <cost>`. The rest are the
  low-stakes `[x]` tail. Keep the ranking visible — a flat list of equal `[x]` ticks gets approved without reading.
</output_format>

## The lowest-confidence flag is bundle-wide

The single human approval happens once, at the contract freeze, over the whole bundle. So your
§1 ranking is the first input into a bundle-level flag the user reads at the decision point (`run.md`):
*"of everything I'm asking you to freeze, these 1–2 are most likely wrong."* A flag may point at
a §1 assumption, an uncovered scenario, or the contract shape.

## AI prompt

<prompt>
Role: a domain analyst who brainstorms, then asks rather than assumes.
Read first: CONVENTIONS · GLOSSARY · the user's raw input.
Objective: fill §1 SPECIFY with zero ambiguity left for the AI to resolve by guessing.
Steps:
  1. Surface 2–3 framings + the open questions; let the user react before you draft.
  2. Produce §1 — Framings weighed, every Must, every Reject with a named error code, the
     After state, and the Assumptions RANKED lowest-confidence first.
  3. Flag the 1–2 where your confidence is lowest, each with why + cost.
Never: resolve an ambiguity by guessing.
</prompt>

## Exit gate

<exit_gate>
- [ ] Framings weighed noted; every required behavior stated.
- [ ] Every rejection has a named error code; success state-change described.
- [ ] Assumptions ordered lowest-confidence first; the 1–2 `⚠` flags carry why + cost — or an honest
      "none material" that still names the single biggest risk (never a blank "none").
</exit_gate>

> **Advisor · Confidence** — for an unfamiliar domain, spawn a researcher (advisor.md); self-score the spec and let the lowest dimension aim your ⚠ flag (confidence.md).

## Next

`python3 .add/tooling/add.py advance` → read `phases/2-scenarios.md`.
Book: `docs/03-step-1-specify.md`. (UI feature? also sketch flows + every screen
state: loading/empty/error/success.)
