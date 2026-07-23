# 12 · Roles and responsibilities

[← 11 Governance](./11-governance.md) · [Contents](./README.md) · Next: [13 Adoption →](./13-adoption.md)

Everyone on an AIDD team becomes, in part, a *verifier*; most also become *authors of the artifacts*. This chapter says what each role owns and does. Find your section; each answers the same three questions — what you do, when, and what "done" means for you.

---

## Product / Domain Owner

- **Mission:** ensure the right thing gets built. You guard the problem.
- **Leads:** Specify. **Contributes to:** Scenarios; the loop (deciding what the next cycle addresses).
- **Owns:** the problem definition, the glossary of domain terms, the prioritized backlog.
- **Done means:** the spec states real user value with no disputed terms and its assumptions ranked lowest-confidence first — the one or two most likely wrong flagged with *why* and *what they cost*; after release, you have decided what the next loop must address.
- **Apply it:** run the Specify prompt against a real ticket or interview, then read the AI's lowest-confidence flag *first* and decide the one or two load-bearing assumptions before skimming the low-stakes tail. If you cannot confirm a load-bearing rule, it is not ready to build.

## Architect / Engineering Lead

- **Mission:** own the load-bearing surfaces and the checks that protect them.
- **Leads:** project setup; the Contract freeze. **Accountable for:** all the durable artifacts.
- **Owns:** `CONVENTIONS.md`, the contracts, the architecture check in verification, the model record.
- **Done means:** contracts are frozen and versioned; the architecture check runs in the pipeline; autonomy levels match the team's real review capacity.
- **Apply it:** treat the contract freeze as a one-way door. When a stream wants to change a frozen contract, route it as a change request that reopens Specify — never let code quietly move the surface.

## Software Engineer (Senior)

- **Mission:** direct the build and hold quality at the architecture check.
- **Leads:** Build. **Contributes to:** Contract, Tests; reviews others' changes.
- **Owns:** the implementation, the architecture conformance check, the evidence bundle on each change.
- **Done means:** all tests pass without any test being weakened; coverage holds; architecture and security checks pass; a person has reviewed it.
- **Apply it:** work in small batches the review can keep up with, and never let the AI edit a test to make it pass — that is the cardinal sin of the build step.

## Software Engineer (Junior)

- **Mission:** learn the craft by entering at the build end and growing toward judgment.
- **Leads:** nothing yet. **Contributes to:** Build (against handed-over specs and contracts), Tests.
- **Owns:** your tasks' code and tests; raising a flag when a spec is ambiguous — which is a contribution, not a failure.
- **Done means:** your task's tests pass honestly, your change has a clear evidence bundle, and a senior has reviewed it.
- **Apply it:** start with specs and contracts given to you and make red tests green without weakening them; over time move *up* toward design and specification as your judgment matures (see [13 Adoption](./13-adoption.md)).

## QA / Test Engineer

- **Mission:** make "done" machine-checkable; you are the guardrail for AI-written code.
- **Leads:** Tests. **Contributes to:** Scenarios (turning rules into checkable form); the loop (production monitors).
- **Owns:** the test suite, the scenario files, the coverage target, the test report at each gate.
- **Done means:** every scenario has a test that was red before the build; the suite is honest (nothing passes by default); coverage never regresses.
- **Apply it:** co-author the scenarios so the path from rule to test loses nothing, and confirm the suite fails for the *right* reason before the build begins.

## Product Designer (UI/UX)

- **Mission:** ensure correct logic does not ship inside a poor experience.
- **Leads:** the design portion of Specify; the Prototype stage. **Contributes to:** Scenarios (experience-side rules).
- **Owns:** the user flows, the specification of every screen state, the design document, the clickable prototype.
- **Done means:** every screen has all its states designed; the prototype matches the scenarios; the self-critique for generic, low-effort output has passed.
- **Apply it:** in the Prototype stage you lead — make the experience tangible fast, and carry the design forward while the prototype code is discarded.

## DevOps / SRE / Platform

- **Mission:** make the continuous concerns real and run the operate-and-learn loop.
- **Leads:** the loop / operations. **Contributes to:** setup (pipeline, observability conventions), Build (deployment, gradual delivery).
- **Owns:** gate enforcement in the pipeline, telemetry conventions, service-objective dashboards, rollback, the cost budget.
- **Done means:** the gate outcomes are enforced mechanically in the pipeline; instrumentation is required to pass the build gate; rollback is tested; objectives are observed after release.
- **Apply it:** wire the gate-fail protocol into the pipeline so a `HARD-STOP` is automatic, not a meeting, and shift security checks to setup rather than the end.

## Security Engineer

- **Mission:** keep AI-written code from importing AI-shaped risk.
- **Leads:** the security thread. **Contributes to:** setup (allow-list, secret scanning), Specify (threat modeling), Build (scanning), AI governance.
- **Owns:** the dependency allow-list, the provenance and license record, the security report at each gate, the supply-chain policy.
- **Done means:** zero high-severity findings at the build gate; every AI-suggested dependency verified real and intended; generated and pulled-in code license-scanned.
- **Apply it:** assume the AI will at some point hardcode a secret and invent a package name; gate against both from setup, and keep security findings as `HARD-STOP`, never waivers.

## Engineering Manager / Delivery Lead

- **Mission:** match intensity to risk, and protect verification capacity.
- **Leads:** profile selection and stage planning. **Contributes to:** unblocking every step; the loop (priorities).
- **Owns:** the chosen profile, the stage roadmap, the metrics dashboard.
- **Done means:** the team operates at an autonomy level its review capacity can sustain; metrics track the scarce things, not code volume; each stage exits on its real achievement, not a date.
- **Apply it:** choose the profile deliberately, and watch review throughput as the true measure of velocity — if AI output outpaces review, slow the engine rather than rushing the review.

---

## Responsibility matrix

`A` Accountable · `R` Responsible/Lead · `C` Consulted · `I` Informed

| Role | Setup | Specify | Contract | Tests & Scenarios | Build | Verify | Loop |
|------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| Product / Domain | C | **R** | I | R | I | I | R |
| Architect / Lead | **R/A** | C | **R/A** | C | A | A | C |
| Engineer (Senior) | C | I | R | R | **R** | R | C |
| Engineer (Junior) | I | I | I | R | R | I | I |
| QA / Test | I | C | C | **R** | C | C | C |
| Designer | I | R (design) | C | R | I | I | I |
| DevOps / SRE | R | I | I | C | C | R | R | **R** |
| Security | R | C | I | C | C | R | R | C |
| EM / Delivery | C | C | C | C | C | C | C | C |

> If your role is only ever `I`, you are not yet using the method — find the step where your judgment *is* the gate.
