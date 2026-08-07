# 01 · Core principles

[← 00 The shift: why ADD exists](./00-introduction.md) · [Contents](./README.md) · Next: [02 The three-beat loop, and what is disposable →](./02-the-flow.md)

---

## 1. Direction before speed

An AI agent accelerates in whatever direction it is given. Therefore the direction must be fixed before the acceleration begins. In practice this means the early, human-led steps of the flow are not optional preamble — they are the steering, and the build step is the engine. You do not start the engine until the wheel is set.

**Consequence:** the specification, scenarios, and contract come *before* any code, every time.

## 2. Trust through evidence, not inspection

AI output is often wrong in ways that read as correct. You cannot establish correctness by reading the code and judging it plausible. You establish it by defining, in advance, what "correct" means — as automated tests — and confirming the code satisfies them, then checking by hand only the narrow set of things tests cannot catch.

**Consequence:** tests are written *before* the implementation, and a feature is trusted because its tests pass, not because someone reviewed it and liked it.

## 3. The artifacts survive; the code is disposable

The durable assets of a project are the decisions and agreements: the specification, the scenarios, the contract, the tests. The code is merely one implementation that satisfies them and can be regenerated at will. Protect the artifacts; treat the code as replaceable.

**Consequence:** effort goes into keeping contracts and specs stable and clear, not into preserving particular code. Metrics that count code volume or reuse measure the wrong thing.

## 4. The loop is re-entrant, not a waterfall

The flow has an order, but it is not a one-way march. Any step may reveal a gap in an earlier one — and when it does, you return to that earlier step, fix the artifact, and come forward again. The specification is a living document, not a frozen contract signed once.

**Consequence:** discovering a missing rule during the build is the method working, not failing. The only true one-way door is the frozen interface contract, and even that reopens through a deliberate change request.

## 5. Trust is earned per scope, not granted globally

How much you let the AI run unattended is not a single switch. It is set per task, by *what the task touches* — not by a global mode. The lever is the task's **sensitivity**: purely mechanical work carries a light floor; anything touching **data**, **architecture**, or **security** is held to a real task with a human at the freeze, and **security is always a hard stop**. Orthogonally, the **depth dial** (quick · standard · deep) tunes how much ceremony a task runs — never how much authority it has.

Two things never move, whatever the task: the contract-freeze decision point stays human (the AI never freezes the interface it then builds against), and a security- or architecture-shaping scope is never resolved on evidence alone.

**Consequence:** trust is a per-task judgment set by the task's sensitivity floor and its depth, not a mode you flip; a high-risk scope is held to a human gate regardless (see [09 Governance](./09-governance.md)).

## 6. You cannot move faster than you can verify

When an agent produces more than the team can review, the excess is not speed — it is unreviewed risk accumulating. Verification capacity is the real ceiling on throughput.

But *verification* is not the same as *human reading*. The ceiling is what you can trust to a recorded standard, and automated verification raises it: a passing test suite, a contract check, an adversarial verifier are all verification, and they scale in a way human review cannot. This is only principle 2 taken to its limit. What automation cannot cover is the residue principle 2 names — the narrow set tests miss: security, concurrency, and architecture. That residue stays at human speed. So the rule sharpens: you may move as fast as your *automated* verification carries you, and no faster on the part only a human can check.

**Consequence:** if AI output outpaces verification, the correct response is to strengthen the automated checks or size the work down — never to rush or skip. More latitude is earned by more verification, not by a lower bar.

## 7. No silent skips

Every checkpoint resolves explicitly. A step is either passed, or passed with a recorded and signed acceptance of a known risk, or stopped. Nothing is quietly waved through.

An *automated* pass is still an explicit pass, not a skip — provided it records an outcome and escalates what it cannot judge. A gate may be resolved by evidence rather than by a person when that evidence is sufficient and the result is logged to an accountable owner: a named run, against a recorded standard, is as accountable as a signature. The line between a pass and a skip is the recorded outcome, not who signed it. The exception is absolute: security always escalates to a human and is never auto-passed — a security finding is a hard stop, whatever the evidence says.

**Consequence:** every gate produces a recorded outcome with an accountable owner — a person, or a named automated run — and security always stops for a person (see [09 Governance](./09-governance.md)).

## 8. Tool-agnostic by construction

The instructions you give the AI are plain text that reference files in the repository, not commands tied to one product. Enforcement of the gates lives in your build pipeline, not in the agent. This keeps the method portable: the agent is replaceable; the method is not.

**Consequence:** the same project works whether the team uses one AI coding tool or another, and switching tools changes nothing structural.

## 9. Two layers: the working state you load, the audit trail you reference

A method that fills the context window with its own documentation defeats itself — the agent rots before it reaches the work. So ADD keeps two documentation layers and never loads both. The **working state** is everything an agent loads to do the work each session: the `add` skill itself (its router `SKILL.md` and the one beat currently in play) together with the lean, current state of the `.add/` bundle — the active task node, its milestone, and the five living specs — surfaced by `add status`. The **audit trail** is this book plus the records behind it: the whole method, read once by a person to understand and trust ADD, and thereafter **never auto-loaded** into agent context — only referenced by a pointer. Depth lives in the audit trail; leanness is enforced on the working state; they never compete for the same tokens.

**Consequence:** the book can be as rich as trust requires without costing a single runtime token, while the loaded surface stays small enough never to rot. It is why the guideline block in `CLAUDE.md`/`AGENTS.md` *points* to `add status` and the `.add/` bundle rather than copying them.

---

> **The principles, compressed.** Steer before you accelerate. Trust evidence, not impressions. Keep the decisions, throw away the code. Loop freely, but never skip silently. Load the State; reference the Story. Grant the AI only as much latitude as you can verify.
