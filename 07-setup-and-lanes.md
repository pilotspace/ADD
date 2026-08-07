# 07 · Setup and the three lanes

[← 06 The loop — observe, learn, close](./06-the-loop.md) · [Contents](./README.md) · Next: [08 Parallel work — waves and worktrees →](./08-parallel-work.md)

---

## Setup: the AI drafts, you approve the baseline

Before the first feature, the project needs a foundation — but standing it up is no longer your chore. Point ADD at the repo and **the AI does the drafting**: it runs `init` itself, reads what is there, and fills the foundation the whole project depends on. Your single act is the **baseline approval** — the one human gate that freezes it.

**What the AI drafts.** From an existing codebase it works **silently** — the code answers the questions a setup interview would ask. On an empty repo it runs a short **four-lens interview** (domain · spec · users · decisions), then drafts. Either way it fills the living documentation — the files that outlive all code — and drafts the first milestone's scope and the first task's candidate contract:

| Item | File | Purpose |
|------|------|---------|
| Foundation | `PROJECT.md` + `.add/specs/` | `PROJECT.md` = goal · invariants · key decisions · pointers (read first); `.add/specs/` = the standing 5-DD picture — domain · system · experience · quality · method — every task reads |
| Conventions | `CONVENTIONS.md` | naming, layout, language, formatter — living documentation |
| Model record | `MODEL_REGISTRY.md` | which AI model and version the project uses, for reproducibility and audit |
| Dependency allow-list | `dependencies.allowlist` | the packages the AI may use; the pipeline rejects others |
| Prompt playbook | `playbook/` | the six prompts from [Appendix B](./appendix-b-prompts.md) |
| Repository + pipeline | — | runs the gates on every change |

Every drafted decision is tagged **evidence-grounded** (read from the code) or **guessed** (thin or inferred) and listed lowest-confidence-first in a `SETUP-REVIEW.md`, so the one signature you give is informed rather than given without reading.

**The baseline approval.** The AI presents `SETUP-REVIEW.md`; you check the `guessed` rows; you **lock** — once. That single act freezes the foundation, the first scope, and the first contract together. It is the setup-level analog of the [contract freeze](./03-direction.md), and it doubles as the first task's contract approval — so there is no separate sign-off. Before the lock the engine lets the AI draft but refuses to cross into build; after it, the build opens.

**Setup exit check**

- [ ] Foundation + living docs drafted (brownfield: from the code, evidence-tagged; greenfield: from the interview, gaps flagged `guessed`).
- [ ] `SETUP-REVIEW.md` lists every drafted decision lowest-confidence-first.
- [ ] The model is pinned; the allow-list exists and the pipeline fails on any package outside it.
- [ ] The pipeline runs and is green on the empty skeleton.
- [ ] The human **locked down** — and only then did the first feature's build open.

Do not start a feature until the pipeline is green and the foundation is locked. The baseline approval turns the AI's draft into committed direction; the pipeline enforces every later exit check without anyone having to remember to.

---

## Stages: the same flow at increasing depth

A *stage* is one pass through the flow at a chosen depth. The steps never change between stages; what changes is how deeply you run each one. The instinct to skip steps for an early prototype is right in spirit but wrong in form — you do not skip steps, you run them lightly.

### The depth matrix

Depth: **Deep** (full rigor) · **Core** (real but scoped) · **Light** (just enough) · **—** (skipped or stubbed).

| Step | Prototype | Proof of Concept | MVP | Production-Ready |
|------|:---------:|:----------------:|:---:|:----------------:|
| 1 Specify | Light | Deep (risky slice) | Deep | Deep |
| (design, if UI) | **Deep** | Light | Core | Deep |
| 3 Contract | — | Core | Deep | Deep |
| 4 Tests & Scenarios | Light | Core | Deep | Deep |
| 5 Build | Light (throwaway) | Core | Core | Deep |
| 6 Verify | Light | Core | Core | Deep |
| Loop / operate | — | — | Light | Deep |
| **Typical time\*** | ~2–5 days | ~1–3 weeks | ~4–8 weeks | ~4–8+ weeks |
| **Code is** | disposable | disposable | kept | hardened |

\* *Ranges assume a small team on a single product slice. Scale by scope and by the number of parallel streams. The pace is set by judgment and review capacity, not by how fast the AI can type — adding more AI does not compress the human-led steps.*

### Stage by stage

**Prototype — prove the experience.** Run the design deeply and everything else lightly; the code is throwaway. The achievement is that a stakeholder reacts to something tangible and a go/no-go on the concept becomes possible. Do not expect real data, tests, or anything that survives.

**Proof of Concept — retire the biggest technical risk.** Run the contract, tests, and build *deeply but only on the single riskiest slice*. The achievement is evidence that the hardest unknown is solvable, which turns an MVP estimate from hopeful into credible. Do not expect breadth or polish.

**MVP — deliver value to real users.** Run the full flow at a narrow scope — the first complete loop, including light observation. The achievement is real users getting value while you learn from them. Do not expect scale or full operational rigor.

**Production-Ready — run safely at scale.** Run every step at full rigor and deepen the operate-and-learn loop: service objectives, incident response, tested rollback, gradual delivery. The achievement is a system that is tested, secure, observable, and supportable. Do not expect "zero defects"; expect managed risk with a working feedback loop.

### What carries forward

The durable thing is never the code:

| Transition | Discard | Keep |
|------------|---------|------|
| Prototype → POC | the prototype code | the validated experience (design, flows) |
| POC → MVP | the spike code | the validated approach + the risky-interface contract |
| MVP → Production | nothing | everything; the code is real and is hardened |

The living documentation thickens as you move right: a prototype leaves you a validated design; a proof of concept adds a proven approach and a contract; the MVP adds real, kept code. By production, you are hardening, not rebuilding.

### Graduating between stages

Moving up a stage — most consequentially MVP → Production — is its own scope level, the fourth after setup, intake, and the milestone loop. It is *not* a label someone types: a project earns production through a human-confirmed roadmap of the hardening work, never through a bare flip. The `add` skill drives this in `graduate.md`; the shape is five steps.

**The cue.** When every milestone is `done` *and* the human's **stage-goal-criteria** in `PROJECT.md` are all `[x]`, `add.py status` prints `→ MVP covered → propose graduation`. Until both tallies complete, nothing here applies — a project with no stage-goal-criteria block behaves exactly as before.

1. **Gather the analytics.** `add.py graduation-report` clusters the whole MVP loop's evidence into five labeled record-sets — open deltas by competency, open RISK-ACCEPTED waivers by expiry, RETRO records, verify residue, and observe-loop coverage gaps. It *gathers, never judges*: there is no readiness verdict, only the records you reason from.
2. **Interview.** Synthesize *what production means here* with the human, using those records as the agenda. This synthesis is the judgment the engine refuses to make.
3. **Draft the roadmap.** For each production outcome the interview surfaces, draft a production milestone with the existing command — `add.py new-milestone <slug> --stage production --goal "…"` — and write its exit criteria. The roadmap is **≥1** milestone; the hardening work itself is what those milestones contain.
4. **Human confirms.** The human accepts, edits, or declines each draft. Nothing is created on an unconfirmed draft.
5. **Flip — the final step.** Only now run `add.py stage production`.

**The floor the engine enforces.** `add.py stage production` is guarded: it refuses with `stage_no_roadmap` (non-zero exit, state byte-unchanged) when no milestone has `stage: production`. The check is a *tally* — does a production-roadmap record exist? — never a readiness judgment, mirroring the milestone goal-gate. `--force` overrides it for grandfathered or edge cases; use it deliberately, not as the normal path. The guard is on the `→production` transition only; flips to prototype/poc/mvp are unchanged. The engine never advances the stage on its own — it gathers, counts, and holds the floor while the human judges and confirms.

---
