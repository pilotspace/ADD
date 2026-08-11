---
type: Task
title: persona-author references speak 3.0
status: done
milestone: v3-final-collateral
scope:
  - add-method/skill/add/persona-author/references/contract.md
  - add-method/tests/skill/test_persona_author_30.py
gives:
  - S1 `references/contract.md` — the persona contract spec, 3.0-true
  - S2 `tests/skill/test_persona_author_30.py` — the suite pinning that truth
generated: { by: add/3.0.0, at: 2026-08-11 }
verified:
  - { by: "human:tindang", at: 2026-08-11, act: freeze, authority: process, direction: "sha256:0553518672a7510a" }
  - { by: "cli", at: 2026-08-11, act: brief, authority: process, brief: "sha256:7bf132775e7d4ec5" }
  - { by: "process:run", at: 2026-08-11, act: run, authority: process, outcome: PASS, receipt: /tasks/persona-author-30.d/runs/1.md }
  - { by: "process:run", at: 2026-08-11, act: run, authority: process, outcome: PASS, receipt: /tasks/persona-author-30.d/runs/2.md }
  - { by: "human:tindang", at: 2026-08-11, act: gate, authority: process, outcome: PASS, receipt: /tasks/persona-author-30.d/runs/2.md, brief: "sha256:7bf132775e7d4ec5" }
---
## CARD
goal: contract.md stops describing the 2.5 world — seeding claim, method-lens definition and verify vocabulary all name artifacts that ship in 3.0
why: the sub-skill is loaded verbatim by persona authors; a doc teaching `constants.METHOD_PERSONAS` and `PLAN.md §3` teaches a world that no longer exists
beat: done · next: add status
## RULES
<must>
- M1 contract.md names only artifacts that ship in 3.0 — no 2.x engine symbols (`constants.METHOD_PERSONAS`), no 2.x files (`PLAN.md`, `.add/personas/` seeding), no retired verbs (`migrate`)
- M2 the method-lens / domain-lens line survives, restated over 3.0 artifacts (Task RULES/CHECKS, `gives:`, the freeze seal, beats)
</must>
<reject>
- R:PHANTOM a shipped doc naming an engine symbol, file or verb that does not ship -> "PHANTOM"
</reject>
## ASSUMPTIONS
- A1 [who] covers: S1, S2 · the request does not say who consumes contract.md beyond persona authors; taking "authors + the phantom-verb doc gates" -> cost if wrong: a consumer relying on the 2.x seeding claim breaks silently
- A2 [which] covers: S1, S2 · probe: pattern vocabulary survives the scrub · the request does not say which 2.x-era WORDS count as residue; taking "engine symbols, files and verbs only — persona-pattern vocabulary (qualification gate, refute-read as a judging stance) stays" -> cost if wrong: over-scrub strips the sub-skill's teaching voice
- A3 [when] covers: S1, S2 · the request does not say when the scar story (twelve dead presets) stops being worth its lines; taking "keep it — it is the rationale for the lens line" -> cost if wrong: the doc carries history a reader no longer needs
- A4 [absent] covers: S1, S2 · the request does not say what replaces the seeding claim if 3.0 seeds nothing; taking "state the 3.0 truth: no personas are seeded — the teacher corpus is vendored read-only and roster nodes are authored via add new Persona" -> cost if wrong: authors look for a personas/ dir that never appears
- A5 [order] covers: S1, S2 · the request does not say whether tests or doc edits land first; taking "red tests first — the suite must fail on today's contract.md before any edit" -> cost if wrong: the pin proves nothing

## PLAN
contract: `references/contract.md` re-grounded on 3.0; sibling docs untouched unless a named phantom lives there
scope: add-method/skill/add/persona-author/references/contract.md · add-method/tests/skill/test_persona_author_30.py
## EDGES
- E1 <a boundary or failure case a check must cover — optional>

## CHECKS
- test_contract_names_no_2x_engine_symbols · covers: M1, R:PHANTOM · constants.METHOD_PERSONAS / PLAN.md / §3 / migrate-as-verb all gone
- test_seeding_claim_matches_the_30_engine · covers: M1 · the doc states 3.0 seeds no personas and points at add new Persona + the vendored corpus
- test_lens_line_restated_over_30_artifacts · covers: M2 · method-lens definition names 3.0 artifacts, and the scar story survives
- test_pattern_vocabulary_survives · covers: A2 · qualification gate stays in patterns.md and SKILL.md — the scrub is scoped to engine truth
red-first: every check MUST fail first.
## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>