# AI-Driven Development

### A complete, practical book on building software when AI writes the code

**Edition:** 1.0 · **Type:** Methodology + operating manual

---

## What this book is

This is a complete guide to **AIDD (AI-Driven Development)** — a way of building software in which an AI agent writes most of the code and people do the two things AI cannot reliably do alone: decide *what* to build, and *verify* that what was built is correct.

The method's center in one sentence: **the agent is the hands; ADD is the memory, judgment, and conscience — the part of the team that survives when the context window doesn't.** Everything an agent structurally cannot keep — what is true so far, what was promised, what worked here before, what must never be traded away — lives as artifacts on disk, not in a conversation. That is why a fresh session loses nothing, and why the method's quality holds across milestones while chat-carried work decays.

It is written to be read once front to back, then kept open beside you as a working manual. The early chapters explain *why* the method has the shape it does; the middle chapters explain each step in detail; the later chapters explain how to operate it across a real team and product; the appendices are copy-paste reference material.

A single worked example — *transferring money between a user's own accounts* — runs through the entire book so that every abstract step has a concrete form you can see.

## Who it is for

Anyone who builds software with AI in the loop: engineers, architects, testers, designers, product owners, and the managers who lead them. No part assumes you have read the others; cross-references point you to what you need.

## The method in one paragraph

For every feature, before AI writes any code, you write four short artifacts in order — the rules it must obey, those rules as pass/fail scenarios, the data and interface contract, and the failing tests — and then you direct the AI to make the tests pass without changing them, and finally you verify the result through evidence rather than inspection. That ordered set of artifacts *is* the method. The code is disposable; the artifacts are the durable asset. Direction comes before speed, and trust comes from passing tests rather than from reading code and finding it plausible.

## The flow

> **Specify → Scenarios → Contract → Tests → Build → Verify → observe, then repeat.**

---

## Table of contents

**Part I — Foundations**
- [00 · The shift: why AIDD exists](./00-introduction.md)
- [01 · Core principles](./01-principles.md)
- [02 · The flow, and what is disposable](./02-the-flow.md)

**Part II — The method, step by step**
- [03 · Step 1 — Specify](./03-step-1-specify.md)
- [05 · Step 3 — Contract](./05-step-3-plan.md)
- [06 · Step 4 — Tests & Scenarios](./06-step-4-tests.md)
- [07 · Step 5 — Build](./07-step-5-build.md)
- [08 · Step 6 — Verify](./08-step-6-verify.md)
- [09 · The loop — observe and learn](./09-the-loop.md)

**Part III — Operating the method**
- [10 · Project setup and stages](./10-setup-and-stages.md)
- [11 · Governance](./11-governance.md)
- [12 · Roles and responsibilities](./12-roles.md)
- [13 · Adoption and onboarding](./13-adoption.md)
- [14 · The foundation: project context across milestones](./14-foundation.md)

**Lineage**
- [15 · Foundations & Lineage](./15-foundations-and-lineage.md)

**Releasing**
- [16 · Releasing](./16-releasing.md)

**Part IV — Reference**
- [Appendix A · Templates](./appendix-a-templates.md)
- [Appendix B · Prompt library](./appendix-b-prompts.md)
- [Appendix C · Glossary](./appendix-c-glossary.md)
- [Appendix D · The worked example, end to end](./appendix-d-worked-example.md)
- [Appendix E · Checklists](./appendix-e-checklists.md)
- [Appendix F · Document requirements matrix (Project → Milestone → Task)](./appendix-f-requirements-matrix.md)
- [Appendix G · References & lineage](./appendix-g-references.md)

---

## Conventions used in this book

- **▶ Example** marks the running worked example.
- **Do / Don't** boxes give the rule in its shortest form.
- A **gate** is a checkpoint with an explicit pass/fail exit. Its outcome is always one of `PASS`, `RISK-ACCEPTED` (a signed waiver), or `HARD-STOP`.
- File names like `SPEC.md`, `features/*.feature`, `contracts/*` refer to the artifacts you create per feature; see [Appendix A](./appendix-a-templates.md).
- Where this book uses a plain step name, the formal phase name (for teams mapping to a larger standard) appears once in [Appendix C](./appendix-c-glossary.md).
