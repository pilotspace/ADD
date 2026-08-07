# 11 · Adoption

[← 10 Personas — the team as lenses](./10-personas.md) · [Contents](./README.md) · Next: [12 The .add/ bundle — ABF-1 format →](./12-bundle-format.md)

---

## A 90-day rollout

Adopt the method on one real product, not as an all-at-once mandate.

1. **Days 1–15 — Lock the foundation.** On one pilot service, let the AI draft the foundation — conventions, glossary, dependency allow-list, model record — from the existing code (or the four-lens interview if greenfield), then **lock it down** with one signature. The prompt playbook is [Appendix B](./appendix-b-prompts.md).
2. **Days 16–45 — One feature, end to end.** Run a single feature through the whole flow at the **Express** profile. Capture friction; tune the prompts' golden cases as you go.
3. **Days 46–75 — Turn on the gates.** Wire the three reports and the gate-fail protocol into the pipeline; introduce the autonomy ladder at the generate-behind-gate level.
4. **Days 76–90 — Promote.** Move the pilot to the **Standard** profile, draft the **Regulated** variant for any compliance-bound product, and publish the prompts as a shared, versioned playbook.

## Choosing a profile

| Choose… | When… |
|---------|-------|
| **Express** | startup, spike, or internal tool; speed of learning dominates; small scope of impact |
| **Standard** | a normal product with real users and ordinary risk |
| **Regulated** | finance, health, or anything audited; failure is expensive or legally consequential |

The choice is deliberate and owned by the delivery lead; different products can run at different profiles.

## Onboarding: enter from the build end

The most common onboarding mistake is to start newcomers at the most abstract step. Specification and domain discovery require judgment a newcomer has not yet built. So bring people in from the *concrete* end and move them toward judgment:

1. **Weeks 1–4 — Build and Tests.** Implement tasks against specs and contracts handed to you; write tests. Learn the architecture check and the evidence bundle.
2. **Weeks 5–8 — Contract and design.** Start contributing to contracts and screen states; learn why the surface is frozen.
3. **Weeks 9–12 — Scenarios and Specify.** Co-author scenarios and specs; practice removing ambiguity.
4. **Beyond — Domain discovery.** The most abstract work comes last, once judgment is calibrated.

You graduate *up* the flow, from execution toward direction. Deciding what to build is the senior skill, not the entry skill.

## Tool portability

The prompts are plain text that reference files in the repository, and the gates are enforced in the pipeline, not in the agent. So the method does not depend on any one AI coding tool — the agent is replaceable, the method is not. A conformant prompt is (1) tool-agnostic plain language, (2) anchored to repository files rather than chat memory, (3) self-describing about which model and exit criteria it assumes, and (4) checkable by the pipeline.

| Concern | Where it lives |
|---------|----------------|
| Prompt discovery | a folder convention in the repo (`playbook/`) |
| Context | repository files the prompt names explicitly |
| Gate enforcement | the build pipeline |

Switching tools changes the discovery convention and nothing structural.

## First week, by role

| Role | First-week task |
|------|------------------|
| Product / Domain | run the Specify prompt on a real input; produce a glossary you would defend |
| Architect / Lead | review the AI's setup draft and lock it down (the first contract freezes with it); wire the architecture check into the pipeline |
| Engineer (Senior) | run the Build prompt on one small task; produce a full evidence bundle |
| Engineer (Junior) | take a handed-over spec; make a red test green without weakening it |
| QA / Test | convert one rule into a scenario, then a failing test |
| Designer | take a spec; produce flows, all screen states, and a clickable prototype |
| DevOps / SRE | wire one gate report into the pipeline; add secret-scan and allow-list to setup |
| Security | build the dependency allow-list; make security findings a `HARD-STOP` |
| EM / Delivery | choose the pilot's profile; stand up the review-throughput metric |

---

> Adoption is a loop too. The method itself is a living document: every cycle should feed improvements back into your copy of these prompts and conventions.
