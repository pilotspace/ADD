# Phase 1 — Specify (the rules)

Goal: state what the feature MUST do and what it must REJECT, with zero ambiguity
for the AI to resolve by guessing. Fill **§1 SPECIFY** in TASK.md.

Specify is **co-specification**: brainstorm the shape WITH the user, draft, then validate. If you cannot write the spec, you don't yet understand the feature — stop and ask.

## Co-specify in three moves

1. **Diverge** — surface the decision space: the 2–3 genuine framings + the open questions you'd otherwise guess. Invite the user to add, kill, redirect. (Conversational — no new file; at prototype/poc, one sentence.)
2. **Converge** — draft §1 answering the §0 GROUND **Issues/Risks**, then RANK where your confidence is lowest (below).
3. **Validate** — present the ranked uncertainty first; the user confirms, corrects, or sends back.

**Identity is direction, not default (UDD).** Brand color, palette, typeface are human-owned — surface them during Diverge, never assume. For a UI feature with a screen, run the design-definition loop in `design.md`.

## Produce (in TASK.md §1)

<output_format>
- **Framings weighed** — one-line trace: `X (chosen) · Y · Z`.
- **Must** — each required behavior.
- **Reject** — each refused input/situation, paired with a **named error code** (`amount <= 0 -> "amount_invalid"`, never "handle bad input").
- **After** — the state that is true once it succeeds.
- **Assumptions — lowest-confidence first** — ranked most-likely-wrong → least. The top 1–2 carry a `⚠` flag: `⚠ <assumption> — lowest confidence because <why>; if wrong: <cost>`. Keep the ranking visible — a flat list of equal `[x]` ticks gets approved without reading.
</output_format>

## The lowest-confidence flag is bundle-wide

The single approval is at the contract freeze, over the whole bundle — so your §1 ranking feeds the bundle-level flag the user reads there (`run.md`): *"of all I'm asking you to freeze, these 1–2 are most likely wrong."*

## AI prompt

<prompt>
Role: a domain analyst who brainstorms, then asks rather than assumes.
Read first: CONVENTIONS · GLOSSARY · §0 GROUND Issues/Risks · the user's raw input.
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

> **Persona** — load the fit `.add/personas/<slug>.md`; its `## Critical Rules` shape §1 (advisory; never lowers a gate).
> **Advisor · Confidence** — for an unfamiliar domain, spawn a researcher (advisor.md); self-score the spec and let the lowest dimension aim your ⚠ flag (confidence.md).

## Next

`python3 .add/tooling/add.py advance` → read `phases/2-scenarios.md`.
Book: `docs/03-step-1-specify.md`. (UI feature? also sketch flows + every screen
state: loading/empty/error/success; name it in the parent MILESTONE.md's Scope-hint
vocabulary, not generic prose.)
