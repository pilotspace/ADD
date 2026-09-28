---
type: Milestone
title: The engine writes the checklist it reads
status: done
sensitivity: architecture
generated: { by: add/3.2.0, at: 2026-08-28 }
verified:
  - { by: "Tin Dang", at: 2026-08-28, act: check, authority: plan, boxes: "EXIT:1,2,3,4" }
---
## CARD
goal: `add check` marks and unmarks a checklist box in any node, records who did it, and `milestone-done` names those people when it closes — so the tally the engine already reads stops being hand-edited markdown.
why: `milestone_done` reads a `- [x]`/`- [ ]` tally out of `## EXIT` and refuses to close while a box
  is unchecked, but the engine ships no verb that can WRITE one. Every tick is a hand edit to
  markdown the engine parses — this session closed `right-sized-lane` by running a throwaway Python
  script against the file, which is the same class of defect as editing a frozen contract by hand:
  the state the engine gates on is reachable only outside the engine. It is also silent. The
  docstring calls checking the last box "the human's single affirmation", yet nothing records WHO
  affirmed it, so an agent's tick and a human's are indistinguishable after the fact.
  Decided with the human 2026-08-28, over the narrower notary design: the verb ticks ANY box in ANY
  node (not only evidence-backed `(← task)` referents) and reaches every section (not only `EXIT`).
  The goal-gate therefore becomes self-serve BY CHOICE — the mitigation is legibility, not refusal:
  every tick is stamped, and `milestone-done` reports the stampers at close.
next: add freeze box-check-verb

## SCOPE
In:  a new `check` verb in the engine (`add.py` + the `cli.py` dispatch) and its four engine twins ·
  the `verified:` stamp it appends · `milestone_done`'s close line naming who checked · the skill
  text wherever the wired loop surface is listed · engine tests + both MD5 pins.
Out: any refusal based on WHO is ticking (decided against — the verb does not defend the goal-gate) ·
  a notary mode that ticks only boxes whose `(← task)` referent is done+PASS (a later task if the
  audit trail proves insufficient) · a TUI or interactive picker · checkbox syntax beyond
  `- [ ]`/`- [x]` · the book chapters.

## GROUND
touches: add-method/tooling/add.py · add-method/tooling/cli.py · the three engine twins ·
  add-method/tooling/engine_pin.py (BOTH pins) · add-method/tests · the three skill trees
risks:
  - Any `add.py` edit re-aims `ENGINE_MD5` and any `cli.py` edit re-aims `ENGINE_PKG_MD5`, and the
    engine has FOUR live twins that must move together — a one-tree edit ships a mirror gap CI
    catches late.
  - Two test roots both run in CI (`add-method/tests/` and `add-method/tooling/`, which owns the
    pins). Running one and shipping is how a red branch has gone out before.
  - The verb writes into node bodies. `_transition` is the one write path and edits frontmatter;
    a body edit needs the same atomic-replace discipline or a crash mid-write truncates a node.
  - Ticking is now reachable by an agent. If the stamp is missing or unreadable, the goal-gate has
    been dissolved with nothing left in its place — the stamp IS the mitigation, so it is load-bearing.

## EXIT
- [x] `add check <ref> <n>…` marks boxes, `--off` unmarks them, and both refuse an out-of-range index rather than writing nothing silently   (← box-check-verb)
- [x] Every invocation appends ONE `verified:` stamp naming who checked which boxes   (← box-check-verb)
- [x] `milestone-done`'s close line names who checked the boxes, so a self-served goal-gate is visible at the moment it closes   (← box-check-verb)
- [x] Four engine twins identical, both MD5 pins re-aimed, both test roots green   (← box-check-verb)

## CLOSE
evidence:
  - box-check-verb · gate PASS (authority plan, freshness fresh) · receipt /tasks/box-check-verb.d/runs/2.md · both test roots green (744+7s, 8)
