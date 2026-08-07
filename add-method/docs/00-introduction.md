# 00 · The shift: why ADD exists

[Contents](./README.md) · Next: [01 Core principles →](./01-principles.md)

---

## Code became cheap

For the whole history of software, writing code was the slow, expensive, central act. Methodologies — waterfall, agile, and the rest — were arrangements for managing that expensive act: how to plan it, divide it, review it, and ship it.

AI changed the cost. An agent can now produce a working module in the time it takes to describe it. The marginal cost of *writing* a piece of code, and of *re-writing* it, has fallen close to zero.

When the cost of one activity collapses, value moves to whatever is still scarce. Three things remain scarce:

1. **Validated decisions** — knowing what should be built, and being right about it.
2. **Stable contracts** — the agreed interfaces and data shapes that everything else depends on.
3. **Verification capacity** — the rate at which people can confirm that what was produced is actually correct.

AIDD is a development method organized around protecting those three things, because they are now where the difficulty lives.

## The failure mode AIDD prevents

The naïve way to use an AI agent is to describe a feature in a sentence and accept whatever it returns. This works for a throwaway script and fails for real software, for one reason: **an AI agent is fast in whatever direction it is pointed.**

If the direction is vague, the agent does not slow down and ask. It produces a confident, plausible, complete-looking result that is subtly wrong — built on an assumption you never made, missing an edge case you never stated. Because it looks finished, the error survives a quick read and surfaces later, when it is expensive to fix.

Speed in the wrong direction is not progress; it is faster waste. The entire purpose of AIDD is to fix the direction *before* turning on the speed.

## Where value moves — and what that means for you

If writing code is no longer the scarce skill, then a software person's value is no longer "can write code." It is two new things:

- **Direction** — turning a fuzzy need into an unambiguous, buildable definition.
- **Verification** — establishing, through evidence, that the result is correct and safe.

This is not a smaller job than coding; it is a harder one. It is the part of engineering that was always the real work, now made explicit because the typing has been automated away.

## What this book gives you

The rest of the book is the practical consequence of the shift:

- A **flow** (Part II) that front-loads direction and back-loads AI execution, with verification built in.
- An **operating manual** (Part III) for running that flow across stages, roles, and risk levels.
- **Reference material** (Part IV) — templates, prompts, and a fully worked example — so the method is concrete from day one.

> **The thesis in one line.** Build the right thing (direction), prove it is right (verification), and let the AI do the building in between.
