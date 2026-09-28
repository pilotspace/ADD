# 01 · Core principles

[← 00 The shift: why ADD exists](./00-introduction.md) · [Contents](./README.md) · Next: [02 The loop, and what is disposable →](./02-the-flow.md)

---

## 1. Direction before speed

An AI agent accelerates in whatever direction it is given, so the direction must be fixed before the acceleration begins. The rules, the assumptions and the failing checks are not optional preamble. They are the steering, and the build is the engine. You do not start the engine until the wheel is set.

**Consequence:** no production code is written before the task's rules, assumptions and checks exist and the checks have failed for the right reason.

## 2. Trust through evidence, not inspection

AI output is often wrong in ways that read as correct. You cannot establish correctness by reading the code and finding it plausible. You establish it by defining "correct" in advance, as checks, confirming the code passes them on a fresh run, and then examining by hand only what checks cannot catch.

**Consequence:** checks are written *before* the implementation, and a change is trusted because its checks pass on the committed tree and its residue was read — not because someone liked the diff.

## 3. The artifacts survive; the code is disposable

The durable assets of a project are its decisions: the rules, the assumptions, the contract, the checks, the evidence. The code is one implementation that satisfies them and can be regenerated. Protect the decisions; treat the code as replaceable.

**Consequence:** effort goes into keeping rules, contracts and specs clear and stable. Metrics that count code volume measure the wrong thing.

## 4. The loop is re-entrant, not a waterfall

The loop has an order, but it is not a one-way march. Any beat may reveal a gap in an earlier one, and then you go back, fix the artifact, and come forward again.

**Consequence:** finding a missing rule during the build is the method working. The sealed contract is the one door that does not swing freely: it reopens only through a visible `refreeze(<slug>)` commit that says why.

## 5. Ceremony is sized by what the work touches

Not every change needs a contract. A typo gets a failing test and a commit; a behavior other code will depend on gets a task file; a theme gets a milestone. The size of the diff does not decide this alone — *what the change touches* does. Anything touching **security, data or architecture**, or a surface other code consumes, is at least a Task however small it looks.

**Consequence:** the agent routes each request to the lightest lane that is safe, sizes up when in doubt, and never takes the light lane for sensitive work.

## 6. You cannot move faster than you can verify

When an agent produces more than anyone can check, the excess is not speed; it is unverified risk piling up. But verification is not the same as a person reading. A passing suite, a contract check and an attempt to break the green are all verification, and they scale in a way human reading does not. What they cannot cover is the residue — security, concurrency, architecture — and that part stays at the speed of careful reading.

**Consequence:** if output outpaces verification, strengthen the checks or size the work down. More latitude is earned by more verification, never by a lower bar.

## 7. No silent outcomes

Every task ends with exactly one written verdict: `PASS`, `RISK-ACCEPTED` with a reason and an owner, or `HARD-STOP`. Every guess the agent had to make is written down as an assumption. Nothing is quietly waved through, and nothing is quietly decided.

**Consequence:** a reviewer can read what was decided, on what evidence, and what was guessed — and a security finding is always a `HARD-STOP`, put at the top of the report.

## 8. Tool-agnostic by construction

The method is plain text that refers to files in the repository. Its seal is a git commit; its evidence is the output of your own test command. Nothing ties it to one agent or one product.

**Consequence:** the same project works under Claude Code, Cursor, Codex, Copilot or any agent that can read a file and run a command. The agent is replaceable; the method is not.

## 9. Two layers: the state you load, the story you reference

A method that fills the context window with its own documentation defeats itself. So ADD keeps two layers apart. The **working state** is what the agent loads each session: the skill file and the lean state of the `.add/` bundle — `PROJECT.md`, the open task, its milestone, the specs it touches. The **story** is this book: read by a person to understand and trust the method, and never loaded into the agent's context.

**Consequence:** the book can be as thorough as trust requires without costing a runtime token, while the loaded surface stays small. That is why the ADD block in `CLAUDE.md` / `AGENTS.md` *points* at the skill and the bundle rather than copying them.

---

> **The principles, compressed.** Steer before you accelerate. Trust evidence, not impressions. Keep the decisions, throw away the code. Loop freely, but never change the contract silently. Size ceremony by what the work touches. Write down every verdict and every guess.
