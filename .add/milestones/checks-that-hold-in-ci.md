---
type: Milestone
title: a check holds where CI runs it, or it does not hold
status: done
generated: { by: add/3.6.0, at: 2026-09-10 }
verified:
  - { by: "human:tindang", at: 2026-09-10, act: interview, authority: human, interview: "sha256:dc4ef17853e29857", receipt: /tasks/checks-that-hold-in-ci.d/interviews/1.md, answers: "C1=confirm|C2=confirm|C3=confirm|C4=confirm" }
  - { by: "human:tindang", at: 2026-09-10, act: freeze, authority: human, direction: "sha256:75a11da44c802486", binding: "sha256:e3b0c44298fc1c14" }
advised_by: method-steward
---
## CARD
goal: no check in this suite asserts against a git ref that CI does not have or that its own commit satisfies — the baseline is a pin, or it is a named range
why: CI went red on a check this bundle wrote two tasks ago — `git merge-base HEAD origin/main` returns 128 on `actions/checkout`'s shallow clone, and the check read *cannot establish a baseline* as *the claim is false*. Behind that one failure is a class: nine call sites compare the working tree to a git ref, and every one of them is satisfied by `git commit`. The repo already bound the decision for `git diff` (Q28) and the guard that enforces it enumerates ONLY `git diff`
next: add new task <slug>

## SCOPE
In:  the nine call sites in `add-method/tests/` that resolve a git ref — `git show HEAD:<path>`, `git merge-base`, `git diff` — and the shape guard that enumerates them.
Out: what each of those guards ASSERTS (every claim is kept; only the baseline it reads changes), the CI workflow's checkout depth, and `git`-reading code in the engine, which is not a check.

## GROUND
touches: add-method/tests/engine/ · add-method/tests/skill/ · add-method/tests/ · add-method/tooling/ (pin only if the engine moves)
risks:
  - the easy fix is to make every one of these SKIP when git cannot resolve, which turns a red CI into a green CI that proves nothing — the exact class this milestone exists to close
  - a HEAD-vs-working-tree guard is not worthless: it fires while the edit is being made, which is when it can help. Deleting them all would remove a live tripwire to fix a CI story

## EXIT
- [x] the suite is green on CI's shallow checkout, and no check reads `cannot establish a baseline` as `the claim is false`   (← the-message-pin-is-a-content-pin)
- [x] a claim that must hold PERMANENTLY is pinned to content, not to a diff whose subject expires at merge   (← the-message-pin-is-a-content-pin)
- [x] every guard that compares the working tree to a git ref is enumerated and declares its lifetime — durable pin, named range, or live-editing tripwire   (← a-head-guard-declares-its-lifetime)
- [x] the SKILL.md prose pin has ONE home, the way the budgets got one   (← one-home-for-the-prose-pin)

## CLOSE
evidence: recorded at close
