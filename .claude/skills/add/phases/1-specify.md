# Phase 1 — Specify (the rules + the scenarios)

Goal: state what the feature MUST do and what it must REJECT, with zero ambiguity
for the AI to resolve by guessing — then make every rule concrete as a pass/fail
scenario. Fill **§1 SPECIFY** and **§2 SCENARIOS** in TASK.md (one drafting phase
owns both since the six-phase merge).

Specify is **co-specification**: brainstorm the shape WITH the user, draft, then validate. If you cannot write the spec, you don't yet understand the feature — stop and ask.

## Co-specify in three moves

1. **Diverge** — surface the decision space: the 2–3 genuine framings + the open questions you'd otherwise guess. Invite the user to add, kill, redirect. (Conversational — no new file; at prototype/poc, one sentence.)
2. **Converge** — draft §1 by PROJECTING from the milestone `## Ground` + the request; then RANK where confidence is lowest (below).
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

## Scenarios (§2) — every rule made checkable

Rewrite each rule as a Given/When/Then that people can read and machines can check:

<output_format>
```gherkin
Scenario: <short name>
  Given <starting situation>
  When <action>
  Then <observable result>
  And <what must remain unchanged>   # REQUIRED for every rejection
```
</output_format>

Write **one scenario per Must** and **one per Reject**; the `And ... unchanged`
clause (on every rejection) catches corrupting partial failures. Then sweep the
edge cases — boundary · duplicate · partial failure · concurrency · malformed
input — add one per applicable case, or rule it out on purpose. Every Then is a
specific, observable fact, never "then it works".

## The lowest-confidence flag is bundle-wide

The single approval is at the contract freeze, over the whole bundle — your §1 ranking feeds the bundle-level flag the user reads there (`run.md`).

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
  4. Produce §2 — one scenario per Must and per Reject (And-unchanged on every
     rejection), then the edge-case sweep.
Never: resolve an ambiguity by guessing; never a vague result — specific and observable.
</prompt>

## Exit gate

<exit_gate>
- [ ] Framings weighed noted; every required behavior stated.
- [ ] Every rejection has a named error code; success state-change described.
- [ ] Assumptions ordered lowest-confidence first; the 1–2 `⚠` flags carry why + cost — or an honest
      "none material" that still names the single biggest risk (never a blank "none").
- [ ] §2: one scenario per Must and per Reject; every rejection asserts what stays unchanged.
- [ ] §2: edge cases covered (boundary · duplicate · partial failure · …) or ruled out on purpose.
</exit_gate>

> **Persona** — load the fit `.add/personas/<slug>.md`; its `## Critical Rules` shape §1 (advisory; never lowers a gate).
> **Advisor · Confidence** — for an unfamiliar domain spawn a researcher, for a large surface delegate a wide scenario sweep (advisor.md); self-score the spec — the lowest dimension aims your ⚠ flag, a missing edge case surfaces in the Edge-cases score first (confidence.md).

## Next

`python3 .add/tooling/add.py advance` → read `phases/3-plan.md`.
Book: `docs/03-step-1-specify.md`. (UI feature? also sketch flows + every screen
state: loading/empty/error/success; name it in the parent MILESTONE.md's Scope-hint
vocabulary, not generic prose.)
