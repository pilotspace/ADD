---
type: Milestone
title: The persona tier the method claims is the persona tier a fresh bundle loads
status: done
generated: { by: add/3.3.0, at: 2026-09-01 }
verified:
  - { by: "Tin Dang", at: 2026-09-01, act: freeze, authority: human, direction: "sha256:75a11da44c802486" }
---
## CARD
goal: A fresh bundle selects a real persona on its first beat, a project whose `.add/personas/` misses reaches the 232-lens teacher corpus before the generic fallback, the skill documents the frontmatter keys the roster actually selects on, and a routing key outside its closed taxonomy is a `doctor` finding rather than a silence.
why: "Personas carry the expertise; the agent carries the discipline" is the method's headline value claim,
  and it is false by default. Two independent reviews reached it from opposite directions on 2026-09-01.
  `3.0 seeds no personas`, so `.add/personas/` is empty on every fresh project and the roster's selector —
  which both agent files run on `flow:` then `task-kinds:` — has nothing to search. The 232-file teacher
  corpus carries `flow:` in ZERO files and `task-kinds:` in ZERO files, so it could not satisfy that
  selector even if the agents were told it exists, which they are not. The three planner templates that DO
  carry both keys sit in `tooling/templates/personas/` and are seeded by nothing, though `CHANGELOG.md:194`
  says they are seeded at init. `personas.md:30` compounds it by telling authors those keys are "read by
  nothing" — so a persona authored to the documented contract is never selected, silently, with no refusal
  and no warning. `seed.md:26` names three archetypes (`backend-systems` · `security-reviewer` ·
  `frontend-ux`) that resolve to zero files, so the single documented bridge from corpus to roster begins
  with a dead link. And the taxonomy is closed but unchecked: ADD's own two personas carry five
  `task-kinds:` values outside it, so by the method's own contract they route nothing. The failure mode
  throughout is silent degradation to the generic fallback, unrecorded in the receipt — the worst shape
  for a trust-based method. This repo is the proof: 109 nodes closed against a 232-lens corpus and a
  roster of two hand-written personas.
next: add milestone-done live-persona-tier

## SCOPE
In:  seeding a persona at `init` · a corpus fallback tier in both agent files, routed through
  `personas-index/use-when.md` · the `personas.md` frontmatter contract · the `seed.md` archetype
  pointers and the guard that should have caught them · a `doctor` finding enumerating `flow:` and
  `task-kinds:` against their closed sets · `explore` as a routing key · ADD's own two personas.
Out: re-authoring the vendored corpus (it is a reference library, kept as-is) · a concurrency lens and an
  explore lens as authored personas (worth doing, sized separately once the tier is live) · the roster's
  reachability, which is roster-reachable's work.

## GROUND
touches: add-method/tooling/add.py · add-method/agents · add-method/skill/add · .add/personas · add-method/tests · add-method/src/add_method/_bundled
risks:
  - Seeding personas at `init` changes engine behaviour and re-aims `ENGINE_MD5` across four live twins.
  - A `doctor` finding that enumerates a closed set must enumerate it from the SOURCE of the taxonomy,
    not from a hand-copied list, or it rots the first time the taxonomy grows.
  - Adding `explore` to the taxonomy touches a documented closed vocabulary in two files at once.

## EXIT
- [x] A freshly `init`ed bundle carries at least one selectable persona, and both agents reach the corpus when it misses   (← persona-tier-live)
- [x] `personas.md` states the keys the roster selects on, and `seed.md`'s archetypes all resolve under a guard   (← persona-contract-truth)
- [x] `doctor` reports a `flow:` or `task-kinds:` value outside its closed set, and ADD's own personas pass   (← persona-routing-keys-checked)

## CLOSE
evidence:
