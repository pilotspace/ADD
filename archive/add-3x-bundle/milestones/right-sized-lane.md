---
type: Milestone
title: ADD ceremony is proportional to task size: small goes direct, medium/large take a node
status: done
generated: { by: add/3.2.0, at: 2026-08-28 }
verified:
  - { by: "Tin Dang", at: 2026-08-28, act: freeze, authority: human, direction: "sha256:75a11da44c802486" }
---
## CARD
goal: A small change runs directly under an inline ADD checklist with no task artifact, a medium change takes a Task at `--depth quick`, a large one a standard/deep Task or a Milestone — and every reader of the method (the skill, this repo's CLAUDE.md, the installer's shipped pointer) is told the sizing rule before it is told the loop.
why: The Quick lane exists (`intake.md`) but admits only mechanical edits — "behavior the specs already
  cover" — and carries no checklist at all: its whole discipline is "make the edit". Meanwhile the
  CLAUDE.md block and the installer pointer never mention sizing; a Cursor/Codex agent reading only that
  block is told "Each task drafts the specification bundle" and runs the full loop for a one-liner. Both
  failures are the same defect from opposite ends: ceremony is not proportional to size. Decided with the
  human 2026-08-28: size-based admission with the closed floor kept · route-and-go (no confirm) for Quick
  · an inline card + red→green + commit receipt + a mandatory `add learn` trace line · the text lands in
  the skill (3 trees), this repo's CLAUDE.md block and the installer pointer twins.
next: add milestone-done right-sized-lane

## SCOPE
In:  the Quick lane's admission rule, checklist and receipt (`intake.md` + the SKILL.md bullet, all
  three skill trees) · this repo's CLAUDE.md ADD block (which also names retired verbs today) · the
  installer pointer block in `_installer.py` + `cli.js` · guard tests for all of the above.
Out: a new lane vocabulary (medium = Task `--depth quick`, large = standard/deep/Milestone — reuse) · any
  engine verb or stamp for the Quick lane (it persists nothing by design) · the book chapters.

## GROUND
touches: .claude/skills/add · add-method/skill/add · add-method/src/add_method/_bundled/skill/add · add-method/src/add_method/_installer.py · add-method/bin/cli.js · add-method/tests · CLAUDE.md
risks:
  - A size-based gate lets a small change with a consumed contract surface slip past the floor — the closed floor and the `gives:` test must stay ahead of size in the rule's order.
  - SKILL.md is at 172/176 lines; the bullet must be funded by compression, never by a budget bump.

## EXIT
- [x] Quick lane admits by size with the floor closed, carries the 5-step inline checklist and the receipt rule   (← direct-lane-size-gate)
- [x] CLAUDE.md block and both installer pointer twins state the sizing rule and name no retired verb   (← direct-lane-size-gate)
- [x] All three skill trees identical; both test roots green   (← direct-lane-size-gate)

## CLOSE
evidence:
  - direct-lane-size-gate · gate PASS (authority plan, freshness fresh) · receipt /tasks/direct-lane-size-gate.d/runs/4.md · both test roots green (726+7s, 8)
