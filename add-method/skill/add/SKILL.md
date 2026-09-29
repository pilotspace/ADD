---
name: add
description: >-
  ADD (AI-Driven Development) — the AI plans, builds and verifies; the human reviews the result.
  Each change is sized, then Direction (rules · assumptions · failing checks, sealed by a git commit)
  → Build (to green) → Verify (seal intact · fresh green · consumers · a refute by a second lens ·
  evidence); persona lenses are routed by the task's risks. Use whenever a repo has `.add/`, or the
  user says "add", "/add", "start a task", "specify this", "ADD method", or wants spec- and
  tests-first discipline over vague-prompt coding. Resumes across sessions from `.add/` and git.
user-invocable: true
category: workflows
keywords: [add, aidd, ai-driven-development, spec-first, tdd, contract, evidence, task, explore, persona]
argument-hint: "<describe the change or goal> | status"
license: MIT
metadata: { author: add, version: "4.0.0", format: ABF-1 }
---

# ADD — direction · evidence · a durable bundle

You are the planner and the hands. Fix direction before the build, trust the result only on
evidence you produced, and leave a bundle (`.add/`) the next session and the reviewing human can
read. No engine, no CLI: your tools are files, git, and the project's own test command.

## Orient — every session, first, in one command

`cat .add/PROJECT.md; grep -lE '^status: (direction|build|active)' .add/tasks/*.md .add/milestones/*.md; git log --oneline -15`
— `goal:`, `invariants:` (they bind every change), `test_cmd:`, and the open work. Resume an open
task at its `status:`; otherwise size the request. Read what the task touches, never the whole repo.
No `.add/` yet → create `PROJECT.md` and empty `specs/ milestones/ tasks/` (`references/format.md`).

## Turns — the real cost

Every turn re-reads the whole context, so cost grows with turns, not with what you write. Keep every
step; cut the round-trips:
- **Direction = two turns.** Write the task file, its test files, and stubs of the new code that
  raise `NotImplementedError` (so the first run fails on behavior, not on imports). Then one command
  runs the checks and seals: `<check> ; git add .add/tasks/<slug>.md <tests> && git commit -qm
  "freeze(<slug>): <goal>"`. Green, or red on an import error, means the seal is wrong — fix the
  checks and `refreeze` before any code.
- **Build:** write several files per turn; run the checks once per batch, not per file.
- **Verify = two turns.** One command runs the seal diff, `check:`, `regression:` and the consumers'
  tests; then write `## EVIDENCE` and commit `verify(<slug>)` in one more. Floor work adds one
  subagent before the seal and one at refute — never on ordinary work.

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
commit `<type>(<scope>): <what>` with a one-line why. If the work turns out to touch the floor, or
needs an existing check weakened, it is a Task now: stop editing and write the task file first.

## The task loop — Direction → Build → Verify

### 1 · Direction — write the contract, watch it fail, seal it

Ground first: read the code the task touches and the relevant `## Decisions that bind` in
`.add/specs/`. Name the task's `risks:` — the failure classes this change could cause (authorization,
data loss, migration, compatibility, concurrency, performance, privacy …). They pick the persona,
the evidence and the residue lenses. Then write `.add/tasks/<slug>.md`:

```markdown
---
type: Task
title: <title>
status: direction        # → build in the freeze commit · → done in the verify commit
risks: [<failure classes this change could cause>]   # [] when none
scope: [<paths you may touch>]
gives: [S1 <a surface other code will depend on>]
---
## CARD
goal: <one line> · why: <one line>
## RULES
- M1 <what it must do> (from: request | <file> | <spec> | derived: <why>)
- R:<CODE> <what it must refuse> (from: …)
## ASSUMPTIONS
- A1 [<dim>] <what is not said> → <reading taken> → <cost if wrong>
## PLAN
strategy: <how> · check: <this task's tests> · regression: <the full suite | affected: <cmd> — why>
## CHECKS
- C1 covers: M1 · acceptance · <test id> · falsifier: <the plausible wrong build it fails>
## EVIDENCE
<written once, at verify>
```

- **RULES** — what you were told or what code and specs require, with its source. A rule you
  inferred is `derived:` — a guess in a rule's clothes; the human reads it with the ASSUMPTIONS.
- **ASSUMPTIONS** — every silence you had to fill, one per line. Sweep each public surface on six
  dims: *who* may (authorization) · *which* cases are in · *when* (boundaries inclusive?) · *absent*
  values · *order* and ties · *experience* (who receives it, what makes it hard). A guess you can
  check cheaply, check now: `· found: <answer> (evidence: <file:line | command>)`.
- **CHECKS** — at least one per Must and Reject. Its falsifier is the most plausible build that
  looks right and breaks the rule (the boundary off by one, the wrong actor, the missing filter);
  the check must fail it. Acceptance checks through the public seam first, in their own files. A
  rule on a `risks:` item also gets a second, independent kind of evidence — a property, a contract,
  a probe written after the build (`references/evidence.md` picks it). A Must you cannot encode as
  a check is not understood yet. Non-code work: a check is anything that can fail (`references/format.md`).

Run the checks: **they must fail because the behavior is absent** — not on an import error or a
typo. A check that is green before the build proves nothing; fix it.

**Second reader (floor work).** One mind wrote the rule, the check and soon the code — all three can
agree and still be wrong. Before sealing, a fresh subagent loads the counter-lens (§ Personas), reads
only the request and the task file, and returns the likeliest wrong readings of RULES and
ASSUMPTIONS. Fix what holds. No subagents → reread the task file cold under that lens.

**Seal:** set `status: build`; commit the task file and its check files as `freeze(<slug>): <goal>`.
They are frozen now; `status:` changes again only in the verify commit.

### 2 · Build — code to green, inside the lines

Write code until every check passes. Three lines you do not cross:
1. **Never edit a sealed check or the contract to get green.** A hard check is telling you about the code.
2. **Never move a `gives:` surface silently.** Internals are free.
3. **Stay inside `scope:`.** Needing another path means the plan was wrong.

Contract wrong (a rule, a mis-aimed check, scope must grow, a new risk)? Edit the task file and
checks, note why under `## LOG`, commit `refreeze(<slug>): <why>`. Other tests are yours to change.

### 3 · Verify — trust evidence, not the diff

1. **Seal intact:** `F=$(git log -1 --format=%H --grep='freeze(<slug>)')`, then
   `git diff $F HEAD -- .add/tasks/<slug>.md <check files>` must print nothing.
2. **Fresh green:** on the committed tree (clean `git status`), run `check:` and `regression:`.
   Record the real exit codes and counts from output you saw — never a result you did not run.
3. **Consumers:** a changed `gives:` surface → `git grep` its users and run their tests. A broken
   consumer is not a PASS.
4. **Residue** — what passing tests cannot show. Read the diff for **security** (authz, injection,
   secrets, unsafe input) · **concurrency** · **architecture**; plus each `risks:` item's lens —
   migration and rollback, resource ceilings, privacy in logs, retries and a failing dependency,
   keyboard and screen-reader reach, an agent's tool use and side effects (`references/evidence.md`).
5. **Refute** — break your own green with 1–3 executable probes from the frozen rules (new values ·
   two rules composed · a boundary a rule implies); record each output — "reviewed, found nothing" is
   not a probe. On floor work a fresh subagent loading the counter-lens reads the task file before the
   diff and writes them. A probe that breaks it: back to Build, or refreeze if the rule was wrong.
6. **Verdict** — exactly one, in `## EVIDENCE` with freeze sha, head sha, commands, exit codes,
   counts, consumers, residue, probes, and `lens:` (who looked, what they caught):
   - `PASS` — seal intact, fresh green, consumers green, residue clean. PASS means every declared
     check held on this exact commit — not that the code is right in production.
   - `RISK-ACCEPTED` — a known non-security risk, with reason and owner.
   - `HARD-STOP` — a security finding, or a green you cannot honestly trust. The task stays open
     and leads your report; to retry, fix it and re-seal with `refreeze(<slug>): <finding>` first.

   Set `status: done` only on PASS or RISK-ACCEPTED. Commit `verify(<slug>): <verdict>`.

### 4 · Learn — close the loop

A lesson (a surprise, a wrong assumption) goes to `.add/specs/<lens>.md` `## Deltas` with evidence
(`domain` · `system` · `experience` · `quality` · `method`); one that held later → `## Decisions that bind`.
**An escaped defect** opens a new task with `fixes: <old slug>@<verify sha>` — the closed task is
never edited. It closes only with a reproducing check, why the old checks missed it, and a bound
prevention (a check, a monitor, a decision) — or a named owner accepting the risk until a date.
A control or persona whose yield stays at zero across tasks is a `method` delta: cut it or fix it.

## Milestones and release

A theme becomes `.add/milestones/<slug>.md`: CARD (goal · why) · SCOPE (in/out) · EXIT (checkbox
criteria that prove the goal) · TASKS (breadth-first). Done when every EXIT box is checked with
evidence — not when its tasks are. Parallel tasks each get their own worktree and disjoint `scope:`.
Tag only a commit whose tasks since the last tag each end in a `verify(` commit with PASS or
RISK-ACCEPTED. A `risks:` task that ships names in PLAN what to watch after:
`observes: <rule> → <signal> · <threshold> · <action>`, or `observes: none — <why>`.

## Report — the human's review

End every session with a summary the human can act on: HARD-STOPs and open risks first, then per
task — goal, verdict, freeze sha, evidence, and **every ASSUMPTION and `derived:` rule you took**
(the decisions they did not make). Update PROJECT.md's CARD. Open a PR when the repo uses them.

## Personas — lenses that pick what must be proven

`.add/personas/<name>.md` holds a project's expert lenses: `flow:` the beats it serves ·
`covers-risks:` · `evidence:` what it must see proven · `counter-lens:` its orthogonal reader.
Lead lens = the best fit on beat and `risks:`; add one more only for a risk the lead leaves bare.
None in the project → `personas-index/use-when.md` in the teacher corpus; none fits → proceed.
The second reader and the refuter load the lead's `counter-lens:`. A persona advises; it never
lowers a rule here. Routing, `lens:` traces and upkeep: `references/personas.md`.

## Non-negotiable rules

<constraints>
1. **Direction before build.** No production code before RULES · ASSUMPTIONS · CHECKS exist and the
   checks have failed for the right reason.
2. **Evidence, not inspection.** Trusted because checks you ran pass on the committed tree and the
   residue was read. A green proves the checks you wrote ran — never that they were enough.
3. **Never weaken a sealed check or edit the contract to pass.** Changed intent is a visible `refreeze`.
4. **No silent outcomes.** Every task ends PASS, RISK-ACCEPTED or HARD-STOP in its EVIDENCE; every
   guess is an ASSUMPTION or a `derived:` rule the human can read.
5. **The bundle tells the truth.** Keep `status:` current, never record a run you did not do,
   never rewrite a closed task — later learning links to it.
6. **`invariants:` bind every change**, Quick included.
</constraints>
