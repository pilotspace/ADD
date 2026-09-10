---
type: Milestone
title: a persona loads by fit, on the path that does not spawn
status: done
generated: { by: add/3.6.0, at: 2026-09-10 }
verified:
  - { by: "human:tindang", at: 2026-09-10, act: interview, authority: human, interview: "sha256:634e5975e46b11d2", receipt: /tasks/personas-load-by-fit.d/interviews/1.md, answers: "C1=confirm|C2=confirm|C3=confirm|C4=confirm" }
  - { by: "human:tindang", at: 2026-09-10, act: freeze, authority: human, direction: "sha256:75a11da44c802486", binding: "sha256:e3b0c44298fc1c14" }
advised_by: method-steward
---
## CARD
goal: the beat guides select a persona the way a spawned subagent already must, so the lens is a function of fit and not of whether the human spawned an agent
why: measured over this bundle, 15 of 190 lifecycle nodes carry a lens — and 3 of 40 milestones, the one lane the skill already says must load one. The mandate is real but it lives in `agents/add-worker.md` §2 ("Become the persona FIRST"), a file loaded ONLY when a subagent is spawned. So the lens is a function of whether the human spawned an agent, not of fit — which is exactly the report: personas load on a spawn and nowhere else
next: add new task <slug>

## SCOPE
In:  the three beat guides (`phases/direction.md · build.md · verify.md`), the router sentence that calls the load `opt-in`, and the one engine surface that could name a candidate lens without selecting one — `brief`.
Out: the NO-EXEC floor (the engine never selects, loads, spawns or judges a persona — `personas.md` is right and stays), the `add advise` verb itself, the roster's contents, `streams.md`'s delegation path (already correct), and the ratchet budgets, which are funded not raised.

## GROUND
touches: add-method/skill/add/ (3 git-tracked trees) · add-method/tooling/add.py (4 twins + engine_pin) · add-method/tests/skill/ · add-method/tests/engine/
risks:
  - the surface budget has EIGHT lines of headroom (1492/1500) and SKILL.md has zero (176/176 lines, 13258/13258 bytes). A fix that writes the instruction into three guides costs three lines minimum, so it is funded by compression or it is not designed yet
  - the todo row already refuses a second verb (A12, `row.count("add ") <= 1`), so the hint cannot be bolted onto the row — the candidate has to surface where the agent reads its instructions, which is `brief`
  - naming a candidate is one step from CHOOSING one; the engine must present the roster and stop there, or the NO-EXEC floor is gone

## EXIT
- [x] each of the three beat guides names the two-tier selector, so an agent working a beat sequentially reads the same rule `add-worker.md` §2 gives a spawned one   (← persona-loads-on-every-path)
- [x] the router no longer calls the LOAD opt-in — the roster is optional, the load is by fit   (← persona-loads-on-every-path)
- [x] `brief` names the roster candidates that fit a node carrying no lens, and selects none of them   (← brief-names-the-candidate-lens)
- [x] every budget holds at its pinned ceiling, with the added lines funded by compression   (all)

## CLOSE
evidence: recorded at close
