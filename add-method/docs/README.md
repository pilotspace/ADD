# AI-Driven Development

### A practical book on building software when AI writes the code

**Edition:** 4.0 · **Type:** Methodology + operating manual

---

## What this book is

This is a guide to **ADD (AI-Driven Development)**: a way of building software in which an AI agent plans, writes and verifies the code, and people do the two things an AI cannot reliably do alone: decide *what* to build, and judge whether what was built is right.

The method's center in one sentence: **the agent is the hands; ADD is the memory, judgment and conscience — the part of the team that survives when the context window doesn't.** What is true so far, what was promised, and what must never be traded away live as plain files in the repository, sealed by git, not in a conversation. A fresh session loses nothing.

ADD 4.0 is **one skill file** the agent follows. There is no engine, no CLI and no approval step. The tools are the ones every project already has: files, git, and the project's own test command. The human reviews the work after it is done, from a report that lists every assumption the agent took.

**What it measurably buys Claude Code** — stronger tests, a floor that always holds, evidence you can re-run, and what that costs — is shown in [an animated tour of the 4.0 benchmark](./add-value.html).

Read it once front to back, then keep it open as a manual. Part I explains *why* the method has its shape; Part II walks the loop; Part III covers operating it; Part IV and the appendices are reference. One worked example, *transferring money between a user's own accounts*, runs through the whole book.

## The method in one paragraph

For every change worth a contract, before any production code is written, the agent writes one task file: the rules the change must obey, the assumptions it had to make, and the checks that will prove it. It runs those checks and watches them fail. It commits the task file and the checks together — `freeze(<slug>)` — and that commit is the seal. It then builds until the checks pass without touching the sealed files, verifies on a fresh run that the seal is intact, reviews what tests cannot show, tries to break its own green, and writes a verdict with the real command output into the task file. The code is disposable; the rules, checks and evidence are the durable asset.

## The flow

> **Direction → Build → Verify → learn, then repeat.**

---

## Table of contents

**Part I — Foundations**
- [00 · The shift: why ADD exists](./00-introduction.md)
- [01 · Core principles](./01-principles.md)

**Part II — The loop**
- [02 · The loop, and what is disposable](./02-the-flow.md)
- [03 · Direction — rules, assumptions, checks, the seal](./03-direction.md)
- [04 · Build — red to green, inside the lines](./04-build.md)
- [05 · Verify — evidence, residue, refute, verdict](./05-verify.md)
- [06 · Learn — lessons, milestones, the report](./06-the-loop.md)

**Part III — Operating the method**
- [07 · Setup and the four lanes](./07-setup-and-lanes.md)
- [19 · Explore — when the answer is the deliverable](./19-dynamic-workflow.md)
- [08 · Parallel work — worktrees](./08-parallel-work.md)
- [09 · Governance — verdicts, floors, review after](./09-governance.md)
- [10 · Personas — expert lenses](./10-personas.md)
- [11 · Adoption](./11-adoption.md)

**Part IV — Reference**
- [12 · The .add/ bundle — ABF-1 format](./12-bundle-format.md)
- [13 · Files and commits](./13-files-and-commits.md)
- [14 · The foundation and the five living specs](./14-foundation.md)
- [15 · Foundations and lineage](./15-foundations-and-lineage.md)
- [16 · Releasing](./16-releasing.md)
- [17 · Components — monorepo and multi-repo](./17-components.md)
- [20 · What changed in 4.0 — migrating from 3.x](./20-whats-new-in-4.md)

**Appendices**
- [Appendix C · Glossary](./appendix-c-glossary.md)
- [Appendix D · The worked example, end to end](./appendix-d-worked-example.md)
- [Appendix E · Checklists](./appendix-e-checklists.md)
- [Appendix G · References & lineage](./appendix-g-references.md)
- [Appendix H · ADD vs spec-kit — the honest comparison](./appendix-h-add-vs-spec-kit.md)

---

## Conventions used in this book

- **▶ Example** marks the running worked example.
- **Do / Don't** boxes give a rule in its shortest form.
- A **verdict** is the one outcome every task ends with: `PASS`, `RISK-ACCEPTED` (a known non-security risk, with a reason and an owner), or `HARD-STOP`.
- Paths like `.add/tasks/<slug>.md` and `.add/specs/` are files in the project's bundle; see [12 · The `.add/` bundle](./12-bundle-format.md).
- Every term the method uses is defined once in [Appendix C](./appendix-c-glossary.md).
