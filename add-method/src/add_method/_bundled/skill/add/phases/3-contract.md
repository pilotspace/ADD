# Phase 3 — Contract (freeze the shape)

Goal: fix the external shape — interfaces, data, names, error cases — and FREEZE it. The decision point that makes the AI-led build safe: below it code is disposable; above it the shape does not move. Fill **§3 CONTRACT** in TASK.md.

## Produce (in TASK.md §3)

<output_format>
- Interfaces (endpoints/functions/messages) with inputs/outputs.
- Request/response shapes + persistent schema (note transactional needs).
- Names drawn from `GLOSSARY.md` (same concept = same name everywhere).
- A response for **every** Reject error code from §1.

Then mark `Status: FROZEN @ v1`. Generate a mock + contract tests so dependent
work can start before the real code exists.
</output_format>

**The freeze is the one approval.** Present the bundle **lowest-confidence first**: the 1–2 points most likely wrong (`⚠ [spec|scenario|contract|test] … — because …; if wrong: …`). Open with the ARC per `report-template.md`, rendering SHAPE then the freeze APPROVE as a guided choice (recommended pick + alternatives) — **render before `FROZEN`, then record `Reported: yes` in §3; never on a timeout.** See `run.md`. The approval also freezes §5 **Scope (may touch)** + Strategy.

## The freeze review checklist

The human's one minute, aimed. Walk these seven before saying yes:

- **⚠ flags first** — read the lowest-confidence flags; accept each knowing its cost if wrong. The engine refuses an unflagged freeze before build (`unflagged_freeze`); `audit` re-checks it on every record that crossed.
- **Intent** — does §1 say what you actually want built?
- **Cases** — does every Must and Reject have an observable §2 scenario?
- **Shape** — glossary names, error codes, additive vs breaking: is THIS the shape to freeze?
- **Grounded** — does §3 cite anchors that exist in the §0 GROUND map? `status`/`check` surface this.
- **Risk** — high-risk or method-defining? Require `risk: high · autonomy: conservative` in the TASK.md header.
- **Tests** — will §4 go red for the right reason, asserting behavior rather than internals?

Reject any line and the bundle goes back to draft; the freeze stays the only gate.

## AI prompt

<prompt>
Role: an interface architect; frozen contracts are immutable.
Read first: §1 · §2 · GLOSSARY.
Objective: produce §3 — the frozen external shape, nothing more.
Steps:
  1. Define interfaces, shapes, and schema named from the glossary, with a response for every Reject code.
  2. Generate a mock returning the contracted shapes and contract tests pinning them.
  3. Mark FROZEN. No business logic.
Never: change a frozen contract — a change reopens Specify.
</prompt>

## Exit gate

<exit_gate>
- [ ] Versioned and marked `FROZEN`.
- [ ] Contract tests pass against the mock.
- [ ] Every name matches the glossary.
- [ ] Every spec rejection has a contracted response.
</exit_gate>

> **Advisor · Confidence** — a second opinion on a risky shape is worth a spawn (advisor.md); a low self-score is your cue to lower autonomy before you freeze (confidence.md).

## Next

`python3 .add/tooling/add.py advance` → read `phases/4-tests.md`.
Book: `docs/05-step-3-contract.md`.
