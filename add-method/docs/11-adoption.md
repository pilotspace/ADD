# 11 · Adoption

[← 10 Personas — the team as lenses](./10-personas.md) · [Contents](./README.md) · Next: [12 The .add/ bundle — ABF-1 format →](./12-bundle-format.md)

---

## A 90-day rollout

Adopt the method on one real product, not as an all-at-once mandate.

1. **Days 1–15 — Lay the foundation.** On one pilot service, run `add init` and let the AI draft the living specs — domain, system, experience, quality, method — from the existing code (or a short interview if greenfield). Seed a starter persona or two for the domain, and record the model behind the work. A human confirms; the specs are the foundation everything else freezes against. The skill carries the prompting; you drive it with the verbs in [13 · The `add` command reference](./13-command-reference.md).
2. **Days 16–45 — One task, end to end.** Run a single feature through the whole loop at **quick** depth: Direction (rules · plan · red checks) → one `add freeze` → Build to green → Verify with `add gate`. Capture friction as you go.
3. **Days 46–75 — Trust the gate.** Wire `add run` and `add gate` into the pipeline so a `HARD-STOP` is automatic, not a meeting, and a security finding stops for a person by construction. Confirm the gate refuses a stale or unbound receipt on a real change.
4. **Days 76–90 — Widen.** Move to **standard** depth for tasks that warrant more ceremony, run a first parallel **wave** once several tasks read `PASS` and a reviewer is ready, and keep folding lessons back into the specs and personas so the method sharpens with use.

## Sizing the work — lanes, not a mode

There is no project-wide dial to set. Each piece of work picks its **lane** by size, and its authority by what it touches:

| Choose… | When… |
|---------|-------|
| **quick lane** | one or a few files, no new contract — an edit and a receipt, no task node |
| **task lane** | one atomic change — the full three-beat loop behind one frozen contract |
| **project / milestone lane** | a breadth of related work — draft a milestone, then a first task list |

The floor is closed regardless of lane: anything touching **security, data, or architecture** always becomes a real task with a human at the freeze, and security is always `HARD-STOP` (see [09 Governance](./09-governance.md)). You do not choose a lane for a sensitive task — its sensitivity already chose.

## Onboarding: enter from the build end

The most common onboarding mistake is to start newcomers at the most abstract beat. Direction and domain discovery require judgment a newcomer has not yet built. So bring people in from the *concrete* end and move them toward judgment:

1. **Weeks 1–4 — Build and checks.** Implement tasks against rules and contracts handed to you; make red checks green without weakening them. Learn the architecture lens and the evidence receipt.
2. **Weeks 5–8 — Contract and edges.** Start contributing to the frozen contract and the edge cases; learn why the surface is a one-way door.
3. **Weeks 9–12 — Rules and Direction.** Co-author the rules and lead Direction; practice removing ambiguity before the freeze.
4. **Beyond — Domain discovery.** The most abstract work comes last, once judgment is calibrated.

You move *up* the loop, from execution toward direction. Deciding what to build is the senior skill, not the entry skill — and the persona corpus is how a team's hard-won judgment is handed to a newcomer as a loadable lens rather than folklore.

## Tool portability

The prompts are plain text that reference files in the repository, and the gate is enforced in the pipeline, not in the agent. So the method does not depend on any one AI coding tool — the agent is replaceable, the method is not. A conformant prompt is (1) tool-agnostic plain language, (2) anchored to the `.add/` bundle rather than chat memory, (3) self-describing about which model and exit criteria it assumes, and (4) checkable by the pipeline through `add run` and `add gate`.

| Concern | Where it lives |
|---------|----------------|
| Working state | `add status` — the active task, its milestone, the living specs |
| Context | the `.add/` bundle files the prompt names explicitly |
| Gate enforcement | the build pipeline, via `add run` and `add gate` |

Switching tools changes which agent reads the bundle and nothing structural.

## Coming from ADD 2.x

If a project already carries a 2.x bundle, `add upgrade` is the path. It renames the whole
2.x bundle into `.add-2x-archive/` — byte-identical, nothing deleted — initialises a fresh
3.0 bundle beside it, and leaves a `MIGRATION.md` in the archive that walks the
re-authoring task by task. 2.x state is deliberately *not* translated: its phase markers
and signed waivers mean things 3.0 refuses to mean, so the direction work transfers by
re-authoring against the archived plans, and the bypasses do not transfer at all.

## First week — where to enter

| Coming in as… | First-week task |
|---------------|------------------|
| A product / domain lens | run Direction on a real ticket; produce rules and a glossary you would defend |
| An architecture lens | review the AI's `add init` draft and confirm it; wire the architecture lens into Verify |
| A senior build lens | run one small task through Build; produce a fresh, bound receipt with `add run` |
| A newcomer | take a handed-over contract; make a red check green without weakening it |
| A testing lens | turn one rule into a check that is red before the build |
| A security lens | seed the security persona; confirm the gate stops on a planted finding |

If a lens is never the thing the gate turns on, it is not yet using the method — find the beat where its judgment *is* the gate.

---

> Adoption is a loop too. The method itself is a living document: every cycle should fold improvements back into your copy of these specs, prompts, and personas.
