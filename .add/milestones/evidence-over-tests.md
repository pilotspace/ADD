---
type: Milestone
title: Evidence over tests — trust on independent evidence against frozen intent
status: direction
generated: { by: add/3.6.0, at: 2026-09-10 }
verified:
  - { by: "plan:evidence-over-tests design memo, go by Tin Dang 2026-09-10", at: 2026-09-10, act: freeze, authority: plan, direction: "sha256:75a11da44c802486", binding: "sha256:e3b0c44298fc1c14" }
advised_by: method-steward
---
## CARD
goal: a task is trusted because independent evidence held against its frozen intent, and the record shows who tried to refute it
why: the book says "one check per Must" and "trust comes from passing tests" while the gate enforces ≥1 discriminating check per referent and §10 concedes a check can assert nothing — and the one act that reads a green against its intent, the refute, is prose in verify.md that nothing records. A 2026 research pass (Vaccari ATs · Example Mapping · SpecBench visible-suite overfitting · TDFlow · mutation-vs-coverage) says the same AI writing rule, check and code shares one misunderstanding three times; the fix is a readable oracle a human confirms and an independent read the record can show
next: add todo --milestone evidence-over-tests

## SCOPE
In:  the Direction prose that sizes CHECKS (skill direction.md · SKILL.md · docs 03/12/appendix c,e), the Build line that freezes tests, an evidence router keyed on kind × computed floor, three JUnit-emitting recipes in domains.md, a new `add refute` verb and `act: refute` stamp, two PASS-only gate refusals at floor ≥ plan, filled edges compiled into `add interview`, the verify tier ladder and probe derivation rule, and one budgeted explore that measures the result on real work.
Out: any PROOFS schema or new frontmatter field, a mutation rung in the receipt kind ladder, hidden-test infrastructure, a required port seam, the four-arm benchmark (T7 decides), the README tagline (human-owned wording), and every part of the trust spine the design keeps — seal, digest, covers grammar, floors, security HARD-STOP, the notary law.

## GROUND
touches: add-method/skill/add/{SKILL.md,phases/direction.md,phases/build.md,phases/verify.md,domains.md,gate.md} + its two twins (.claude/skills/add · src/add_method/_bundled/skill/add) · add-method/docs/{03,04,05,12,13,appendix-c,appendix-e}.md · add-method/tooling/{add.py,cli.py} + _bundled/tooling twin + engine_pin repin · add-method/FORMAT.md §3/§8 · add-method/agents/{add-advisor,add-worker}.md · add-method/tests/engine
risks:
  - the refute stamp is presence-only: a stamp recorded without a real attempt is indistinguishable from an earned one — the engine binds that someone tried, the persona and the floor bind whether it was honest. Say so in FORMAT §10; never let the rung read as a correctness proof
  - ceremony grows back through the new stamp — exempt quick depth, process floor and explore, or the mechanical lane pays for a rule aimed at payments
  - a new verb ripples ~9 registries (cli · SKILL cookbook · docs 13 · FORMAT · README verb count ×2 · CHANGELOG · agents · tests · twins); miss one and the mirror-gap check fails publish
  - the phase files carry byte and sha pins; direction.md +1.6 KB must be funded by compressing its duplicated ASSUMPTIONS prose, not by raising a ceiling

## EXIT
- [ ] no shipped tree says "one check per Must" — every binding referent is named by ≥1 check that would fail on the most plausible wrong implementation, and one check may cover several   (← direct: checks-bind-not-count)
- [ ] for code, the default frozen check is an acceptance check through the port, the readable example is a filled E-edge in Given/When/Then that an acceptance check covers, and build.md freezes only BOUND checks   (← direct: acceptance-first-checks)
- [ ] direction.md carries the evidence router (kind × floor → modes) and domains.md carries property · contract · mutation-on-changed-code recipes that each earn `test-ids` when run   (← direct: evidence-router-and-recipes)
- [ ] `add refute` records `act: refute` with outcome, probes and the receipt it read; `add interview` compiles filled edges as questions   (← refute-verb)
- [ ] `add gate PASS` refuses R:UNREFUTED / R:REFUTED at standard|deep × floor ≥ plan, binds PASS only, and quick · process · explore are exempt   (← refute-gate-rung)
- [ ] verify.md and add-advisor.md state the closed probe derivation list and the T0–T4 tier ladder once, parity-pinned   (← direct: verify-tiers-and-probes)
- [ ] one real milestone ran under the new rules and the numbers (bound checks per Must · refutes found · human minutes at freeze) decide the bench   (← dogfood-and-measure)

## CLOSE
evidence: <one row per task>
