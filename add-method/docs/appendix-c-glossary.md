# Appendix C · Glossary

[← 20 What changed in 4.0](./20-whats-new-in-4.md) · [Contents](./README.md) · Next: [Appendix D Worked example →](./appendix-d-worked-example.md)

Every term the method uses, defined once.

---

## The method

**ADD (AI-Driven Development)** — a method in which an AI agent plans, writes and verifies the code and people own direction and review the result. In 4.0 it is one skill file run with files, git and the project's own test command.

**Skill** — the markdown file the agent follows: `SKILL.md`, with `references/format.md` and `references/explore.md`. Installed at `.claude/skills/add/`. See [07](./07-setup-and-lanes.md).

**Bundle** — the project's `.add/` directory: `PROJECT.md`, specs, milestones, tasks, personas. Plain markdown, maintained by hand. See [12](./12-bundle-format.md).

**Disposable code** — code as one regenerable implementation of the direction, not the durable asset.

**Verification capacity** — the rate at which output can be confirmed correct. The real ceiling on safe speed.

## Sizing

**Lane** — the route a request takes: **Quick** (a test and a commit, no task file), **Task**, **Explore**, or **Milestone**. See [07](./07-setup-and-lanes.md).

**Floor** — the closed rule that anything touching security · data · architecture, or a surface other code consumes, is at least a Task.

## The loop

**Beat** — one of **Direction**, **Build**, **Verify**. A task's current beat is its `status:` — `direction`, `build`, then `done` (or `dropped`).

**Direction** — grounding in the code, then writing the task file's rules, assumptions, plan and checks, running the checks red, and sealing. See [03](./03-direction.md).

**Build** — code until the checks pass, inside `scope:`, sealed files untouched. See [04](./04-build.md).

**Verify** — seal check, fresh run, residue read, refute, verdict. See [05](./05-verify.md).

**Learn** — lessons with evidence into the living specs. See [06](./06-the-loop.md).

**Grounding** — reading what the task touches (files, signatures, conventions, binding decisions) before writing its direction.

## Inside a task file

**CARD** — `goal:` and `why:`, one line each.

**Must (`M<n>`)** — a behavior the change must perform.

**Reject (`R:<CODE>`)** — an input or situation the change must refuse, with a named error.

**Assumption (`A<n> [<dim>]`)** — a silence the agent filled: what was not said → the reading taken → the cost if wrong. Swept over six **dimensions**: `who`, `which`, `when`, `absent`, `order`, `experience`.

**Found** — an assumption checked on the spot, with its evidence appended: `· found: <answer> (evidence: …)`.

**Edge (`E<n>`)** — an optional Given/When/Then example; a written edge needs a check.

**`scope:`** — the paths the build may touch.

**`gives:`** — surfaces other code depends on (`S<n>`). May not move silently.

**`needs:`** — surfaces from other tasks this one builds on.

**Check (`C<n>`)** — `covers: <ids> · <mode> · <test id>`: a test aimed at the most plausible wrong implementation of the rules it covers. Modes include `acceptance`, `property`, `contract`, and for non-code work `script`, `validator`, `rubric`.

**`check:` / `regression:`** — the PLAN's two commands: this task's checks, and the host suite.

**Red for the right reason** — a check that fails because the behavior is absent, not because of an import error or typo.

## The seal and the evidence

**Seal** — the `freeze(<slug>)` commit of the task file and its check files. From then on they are frozen.

**Refreeze** — a legitimate change of contract: edit, note why under `## LOG`, commit `refreeze(<slug>): <why>`.

**Seal check** — `git diff <freeze> HEAD -- <sealed files>`, which must print nothing.

**Fresh run** — `check:` and `regression:` run on the committed, clean tree during Verify, with the real exit codes and counts recorded.

**Residue** — what passing tests cannot show: security, concurrency, architecture, plus a lens by kind (migration reversibility, rollback path, accessibility, retries).

**Refute** — one to three probes derived only from the sealed rules, trying to break the green. A fresh subagent does it for security, data or architecture work.

**EVIDENCE** — the task section written once at Verify: freeze and head commits, seal result, commands with exit codes and counts, residue and refute notes, verdict.

**Verdict** — exactly one of **`PASS`** (seal intact, fresh green, residue clean), **`RISK-ACCEPTED`** (a known non-security risk with reason and owner), **`HARD-STOP`** (a security finding, or a green that cannot be trusted; the task stays open).

**Verify commit** — `verify(<slug>): <verdict>`.

**Report** — the session summary the human reviews: HARD-STOPs first, then per task goal, verdict, freeze commit, evidence, and every assumption taken.

## Explore

**Explore task** — `kind: explore`: sealed `## QUESTIONS` and `## BUDGET`, answered in cited `## FINDINGS`. See [19](./19-dynamic-workflow.md).

**Budget** — a hard ceiling on tool calls, sources or spikes.

**Finding** — an answer with its confidence and its citation. No citation, no finding.

## The foundation

**PROJECT.md** — `goal:`, `invariants:`, `test_cmd:`, `stage:`, and a CARD with `state:` and `next:`. Read first every session.

**Invariant** — a property no change may break, Quick included.

**Living spec** — one file per lens under `.add/specs/`: **domain**, **system**, **experience**, **quality**, **method**. Each has `## Now`, `## Decisions that bind`, `## Deltas`. See [14](./14-foundation.md).

**Delta** — a lesson with evidence, `open` until `folded` into a decision or `rejected`.

**Decision that binds** — a lesson that held, promoted so that every future task follows it.

**Milestone** — `.add/milestones/<slug>.md`: CARD, SCOPE, EXIT, TASKS. Done when every EXIT box is ticked with evidence.

## Personas

**Persona** — `.add/personas/<name>.md`, an expert lens loaded before a beat when its `use-when:` fits. Advises; never lowers a rule. See [10](./10-personas.md).

**Teacher corpus** — `.add/personas-teacher/`, vendored source material personas are distilled from; never loaded at run time.

**persona-author** — the sub-skill that writes or sharpens a persona.

## Parallel work

**Worktree stream** — one independent task built in its own git worktree and branch, with `scope:` disjoint from every other stream. See [08](./08-parallel-work.md).

**Fan-out** — read-only research spread across subagents; facts merge, writes serialize.
