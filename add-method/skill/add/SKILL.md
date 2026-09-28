---
name: add
description: >-
  ADD (AI-Driven Development) — the AI plans, builds and verifies; the human owns direction and
  reviews the result. Every change is sized, then driven Direction (rules · assumptions · failing
  checks, sealed by a git commit) → Build (to green, sealed files untouched) → Verify (seal intact ·
  fresh green run · residue review · evidence written). Research routes to the Explore lane. Use
  whenever a repo has a `.add/` folder, or the user says "add", "/add", "start a task", "specify
  this", "ADD method", "AI-driven development", or wants spec- and tests-first discipline over
  vague-prompt coding. Resumes across sessions from `.add/` and git alone.
user-invocable: true
category: workflows
keywords: [add, aidd, ai-driven-development, spec-first, tdd, contract, evidence, task, explore]
argument-hint: "<describe the change or goal> | status"
license: MIT
metadata: { author: add, version: "4.0.0", format: ABF-1 }
---

# ADD — direction · evidence · a durable bundle

You are the planner and the hands. ADD keeps you fast and honest: fix direction before the build
(rules, assumptions, failing checks), trust the result only on evidence you actually produced, and
leave a bundle (`.add/`) the next session — and the human reviewing your work — can read. There is
no engine and no CLI: your tools are files, git, and the project's own test command.

## Orient — every session, first

1. Read `.add/PROJECT.md`: `goal:`, `invariants:` (they bind every change), `test_cmd:`.
2. Find open work — task and milestone files whose `status:` is not `done`/`dropped`
   (`grep -lE '^status: (direction|build|active)' .add/tasks/*.md .add/milestones/*.md`)
   — and `git log --oneline -15`.
3. Resume an open task at its `status:`; otherwise size the request. Read what the task touches,
   never the whole repo.

No `.add/` yet → create `PROJECT.md` and empty `specs/ milestones/ tasks/` from
`references/format.md`, find the test command, then continue.

## Size the work — you route and go

| the request | lane | what persists |
|---|---|---|
| mechanical, or a small behavior: ≤3 adjacent files, one sitting, no unknowns | **Quick** | a red→green test + one commit |
| one behavior worth a written contract | **Task** | `.add/tasks/<slug>.md` + its commits |
| the answer IS the deliverable — investigate · evaluate · research | **Explore** (`references/explore.md`) | the task's `## FINDINGS` |
| a theme, or more than one task | **Milestone** | `.add/milestones/<slug>.md` + its tasks |

**Floor:** anything touching security · data · architecture, or a surface other code consumes, is at
least a Task — never Quick. When in doubt, size up. Nobody approves the route; the human reviews after.

**Quick:** write the failing test, watch it fail, make it pass, run the suite, review your diff,
commit `<type>(<scope>): <what>` with a one-line why. `invariants:` still hold.

## The task loop — Direction → Build → Verify

### 1 · Direction — write the contract, watch it fail, seal it

Ground first: read the code the task touches (files, signatures, conventions) and the relevant
`## Decisions that bind` in `.add/specs/`; load a persona if one fits (§ Personas). Then write
`.add/tasks/<slug>.md` (shape: `references/format.md`) in one pass:

- **CARD** — `goal:` one line · `why:` one line.
- **RULES** — `M<n>` Musts (what it must do) · `R:<CODE>` Rejects (what it must refuse). Only what
  you were told or what code and specs require; cite it: `(from: request | <file> | <spec>)`.
- **ASSUMPTIONS** — every silence you had to fill: `A<n> [<dim>] <what is not said> → <reading
  taken> → <cost if wrong>`. Sweep each public surface on six dims: *who* may (authorization) ·
  *which* cases are in · *when* (boundaries inclusive?) · *absent* values · *order* and ties ·
  *experience* (who receives it, what makes it hard). One silence per line. A guess you can check
  cheaply, check now: `· found: <answer> (evidence: <file:line | command>)`. The human reviews this
  section instead of approving up front — never hide a guess inside a Must.
- **PLAN** — `gives:` (surfaces other code will depend on) · `scope:` (paths you may touch) ·
  strategy · the `check:` command (this task's checks) and the `regression:` command.
- **CHECKS** — `C<n> covers: <M/R/A ids> · <mode> · <test id>`. At least one per Must and Reject,
  each written to FAIL on the most plausible wrong implementation. Prefer acceptance checks through
  the public seam; add a property or contract check where an invariant or a consumer exists. Keep
  the task's checks in files of their own. A Must you cannot encode as a check is not understood yet.

Write the checks as real tests and **run them: they must fail because the behavior is absent** — not
on an import error or a typo. A check that is green before the build proves nothing; fix it.

**Seal:** set `status: build`, then commit the task file and its check files together:

    git commit -m "freeze(<slug>): <goal>"

That commit is the seal. From here the task file and every file named in CHECKS are frozen — its
`status:` changes again only in the verify commit.

### 2 · Build — code to green, inside the lines

Write code until every check passes. Three lines you do not cross:
1. **Never edit a sealed check or the contract to get green.** A hard check is telling you about the code.
2. **Never move a `gives:` surface silently.** Internals are free.
3. **Stay inside `scope:`.** Needing another path means the plan was wrong.

Changed your mind about the contract (a rule was wrong, a check mis-aimed, scope must grow)? That is
legitimate: edit the task file and checks, note why under `## LOG`, and commit
`refreeze(<slug>): <why>`. History shows it; nothing is silent. Other tests are yours to add, change
or delete. Commit build progress normally.

### 3 · Verify — trust evidence, not the diff

1. **Seal intact:** `F=$(git log -1 --format=%H --grep='freeze(<slug>)')`, then
   `git diff $F HEAD -- .add/tasks/<slug>.md <check files>` must print nothing.
2. **Fresh green:** on the committed tree (clean `git status`), run `check:` and `regression:`.
   Record the real exit codes and counts from output you saw — never a result you did not run.
3. **Residue** — what passing tests cannot show. Read the diff for **security** (authz, injection,
   secrets, unsafe input) · **concurrency** (races, ordering, atomicity) · **architecture**
   (boundaries, dependencies); plus by kind — data: migration reversibility · infra and release:
   the rollback path · UI: keyboard and screen-reader reach · integration: retries, idempotency.
4. **Refute** — try to break your own green with 1–3 probes derived only from the frozen rules (new
   values for a rule · two rules composed · a boundary a rule implies). For security · data ·
   architecture work, spawn a fresh subagent that reads the task file before the diff and tries to
   break it. A probe that breaks it is a defect: back to Build, or refreeze if the rule was wrong.
5. **Verdict** — exactly one, written to `## EVIDENCE` with freeze sha, head sha, commands, exit
   codes, counts, residue and refute notes:
   - `PASS` — seal intact, fresh green, residue clean.
   - `RISK-ACCEPTED` — a known non-security risk, with reason and owner.
   - `HARD-STOP` — a security finding, or a green you cannot honestly trust. The task stays open
     and leads your report; to retry, fix it and re-seal with `refreeze(<slug>): <finding>` first.

   Set `status: done` only on PASS or RISK-ACCEPTED. Commit `verify(<slug>): <verdict>`.

### 4 · Learn — close the loop

A lesson worth keeping (a surprise, a wrong assumption, an escaped defect) goes into the matching
`.add/specs/<lens>.md` under `## Deltas` with evidence — lenses `domain` · `system` · `experience`
· `quality` · `method`. A lesson that held on later work is promoted to `## Decisions that bind`,
which binds future tasks. An escaped defect records why the checks missed it and the check that now
prevents it.

## Milestones

A theme becomes `.add/milestones/<slug>.md`: CARD (goal · why) · SCOPE (in/out) · EXIT (checkbox
criteria that prove the goal) · TASKS (breadth-first, dependencies noted). Ground once for the
milestone, then run each task through the loop. It is done when every EXIT box is checked with
evidence — not when its tasks are. Tasks done but goal unmet: gather open deltas and out-of-scope
finds, add the next tasks, continue.

## Report — the human's review

End every session with a summary the human can act on: HARD-STOPs and open risks first, then per
task — goal, verdict, freeze sha, evidence, and **every ASSUMPTION you took** (the decisions they
did not make). Update PROJECT.md's CARD. Open a PR when the repo uses them. Your report is their
approval surface — make disagreeing easy.

## Personas — an optional lens

`.add/personas/<name>.md` holds a project's expert lenses (`flow:` the beats it serves ·
`use-when:`). Before Direction or Verify, load the one that fits; none fits → proceed. To author one
use the `persona-author` skill; source material is in `personas-teacher/`, routed by
`personas-index/use-when.md`. A persona advises; it never lowers a rule here.

## Parallel work

Read-only research fans out to subagents freely. Writes serialize per tree: parallel tasks each get
their own git worktree and branch, with disjoint `scope:`.

## Non-negotiable rules

<constraints>
1. **Direction before build.** No production code before RULES · ASSUMPTIONS · CHECKS exist and the
   checks have failed for the right reason.
2. **Evidence, not inspection.** A change is trusted because checks you ran pass on the committed
   tree and the residue was read. A green proves the checks you wrote ran — never that they were enough.
3. **Never weaken a sealed check or edit the contract to pass.** Changed intent is a visible
   `refreeze` with a reason.
4. **No silent outcomes.** Every task ends PASS, RISK-ACCEPTED or HARD-STOP in its EVIDENCE; every
   guess is an ASSUMPTION the human can read.
5. **The bundle tells the truth.** `.add/` is plain markdown you maintain: keep `status:` current,
   never record a run you did not do, never rewrite a closed task's EVIDENCE.
6. **`invariants:` bind every change**, Quick included.
</constraints>

Non-code work (docs, research, operations) runs the same loop; a check is anything that can fail —
a script, a validator, a pass/fail rubric (`references/format.md` § Non-code work).
