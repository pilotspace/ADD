---
type: Task
title: A relations: family carries typed concept edges over a closed vocabulary
status: done
depth: standard
sensitivity: architecture
milestone: okf-graph-time
depends_on:
  - /tasks/dated-addressable-deltas.md
needs:
  - /tasks/dated-addressable-deltas.md#gives
scope:
  - add-method/tooling/add.py
  - add-method/tooling/engine_pin.py
  - add-method/scripts/validate_bundle.py
  - add-method/FORMAT.md
  - add-method/tests/engine
  - add-method/src/add_method/_bundled/tooling/add.py
  - .add/tooling/add.py
  - add-method/.add/tooling/add.py
  - .add/specs
gives:
  - S1 add.RELATION_VOCAB — the closed rel vocabulary, one home in the engine, mirrored once by the second oracle
  - S2 add.relations(graph) — one tuple per entry: source cid, source id, rel, ref, and the resolved target or None
  - S3 add.resolve(graph, ref, src) — a third §3.3 form, a delta id in the target's Deltas section, reported as why delta
  - S4 add.doctor(root) — the relation findings unknown_rel, relation_malformed, edge_unresolved and edge_out_of_bundle
  - S5 the second oracle `validate_bundle.py` — its relations pass, its delta-id fragment form, and the identical severities
  - S6 `FORMAT.md` — the relations family in §3.2, the third resolution form in §3.3, the new codes and severities in §9
  - S7 the migrated relations recorded on the living specs — every vocabulary term carrying at least one live instance
generated: { by: add/3.4.0, at: 2026-09-03 }
verified:
  - { by: "plan:okf-graph-time", at: 2026-09-04, act: freeze, authority: plan, direction: "sha256:9eb247c9c4e614d9", binding: "sha256:e8e1db804764e4a0" }
  - { by: "cli", at: 2026-09-04, act: brief, authority: process, brief: "sha256:7f15f464170f0abb" }
  - { by: "process:run", at: 2026-09-04, act: run, authority: process, outcome: PASS, receipt: /tasks/typed-relations.d/runs/1.md }
  - { by: "process:run", at: 2026-09-04, act: run, authority: process, outcome: PASS, receipt: /tasks/typed-relations.d/runs/2.md }
  - { by: "plan:okf-graph-time", at: 2026-09-04, act: refreeze, authority: plan, direction: "sha256:97f5b1f8297aa26a", binding: "sha256:e8e1db804764e4a0" }
  - { by: "cli", at: 2026-09-04, act: brief, authority: process, brief: "sha256:eb3a200161144e70" }
  - { by: "process:run", at: 2026-09-04, act: run, authority: process, outcome: PASS, receipt: /tasks/typed-relations.d/runs/3.md }
  - { by: "plan:okf-graph-time", at: 2026-09-04, act: gate, authority: plan, outcome: PASS, receipt: /tasks/typed-relations.d/runs/3.md, brief: "sha256:eb3a200161144e70" }
---
## CARD
goal: a `relations:` frontmatter family carries typed edges between DELTA CONCEPTS over a two-term closed vocabulary, resolves through §3.2 and a new §3.3 delta-id form in both oracles, records an unknown rel instead of rejecting it, and ships migrated with real instances of every term
why: the milestone exists to kill file granularity, so an edge whose source is a FILE would rebuild the very failure it is here to end; and this repo's measured base rate for a vocabulary that ships without instances is three dead keys out of seven in §3.2, so the migration is part of the build and not a follow-up
beat: done · next: add status

## RULES
<must>
- M1 the rel vocabulary is CLOSED and stated ONCE in the engine as `RELATION_VOCAB` — `refines`, and ONLY the terms with a live corpus instance in this same change — and the second oracle mirrors that one statement rather than keeping an independent list
- M2 a `relations:` entry is a block-list PLAIN STRING of exactly three whitespace-separated fields, source id then rel then target, and both oracles read byte-identical values from it: a list of flow maps parses to a dict in add.py and to a raw brace string in the validator, so the plain-string shape is part of the contract, not a style preference
- M3 the source and rel fields are stripped BEFORE the target is normalised, in BOTH oracles — a relation target resolving outside the bundle root reports `edge_out_of_bundle` at severity error, the same code and the same severity the identical target reports through `depends_on:`
- M4 an unknown rel is RECORDED, never rejected: `unknown_rel` at severity info, and the entry's target is still normalised, still resolved and still containment-tested
- M5 §3.3 gains a THIRD resolution form: after a frontmatter key and after a heading slug, a delta id in the target's `## Deltas` section resolves, and `resolve` reports `why` as `delta`; unresolved stays last, so no reference that resolves today changes meaning
- M6 the SOURCE field resolves too — a source that is not a delta id in the node's own body reports `edge_unresolved` at severity info, so a relation dead at its source end is as visible as one dead at its target end
- M7 an entry that is not exactly three whitespace-separated fields reports `relation_malformed` at severity info and is never absent from the report entirely, whatever the shape of its failure — it yields NO edge, and the format states plainly that such a value carries no resolvable target and therefore no containment claim
- M8 every code this family adds is `info`, and the one error it can raise — `edge_out_of_bundle` — is decided from the frontmatter value and the root path ALONE, never by opening the target, so §9's universal rule holds verbatim: every body-derived finding is info, and all three error codes stay decidable from frontmatter alone
- M9 FORMAT states the family in §3.2, the third resolution form in §3.3, and every new code with its severity in §9 — stating the plain-string shape as the REASON rather than as an example, and stating that the `supersedes` edge key and the `supersedes` relation verb are two distinct grammars that share one word
- M10 the living specs ship MIGRATED: real relations recorded in `.add/specs`, every one resolving on BOTH ends against the live bundle, and every term in the vocabulary carrying at least one of them
- M11 `EDGE_KEYS` is UNCHANGED and `edges()` keeps its contract — typed, and only from that allowlist — so relations are a SECOND family with their own reader, and `cycles()`, the wave planner and the `graph.json` export all keep the exact meaning they have today
</must>
<reject>
- R:DEADVOCAB a rel term with no instance in the live corpus in this same change must never ship -> "DEADVOCAB"
- R:SILENTESCAPE a relation whose target resolves outside the bundle root must never report anything weaker than `edge_out_of_bundle` at error, and must never be downgraded by an unstripped head absorbing a `..` segment -> "SILENTESCAPE"
- R:DIVERGE the two oracles must never disagree about a `relations:` entry — not on the value parsed, not on the code, not on the severity -> "DIVERGE"
- R:REJECTUNKNOWN an unknown rel must never be an error and must never suppress the resolution or the containment test of its own target -> "REJECTUNKNOWN"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the request names no authority for WIDENING the vocabulary; taking the reading that it is closed in the ENGINE, so a new term is an engine change held to R:DEADVOCAB and never a per-bundle setting -> if wrong, a project widens the vocabulary in its own bundle and two conforming engines disagree about what a rel means
- A2 [who] covers: S2, S3, S4, S5, S6, S7 · the request does not say who may author or read a relation; taking the reading that a relation is exactly as authored-and-read as any other frontmatter — no actor model, no per-caller filtering, every reader of the bundle sees every relation -> if wrong, a relation a human meant as private is published to every consumer of the bundle
- A3 [which] covers: S1 · the request names no vocabulary; taking `refines` ONLY. `contradicts`, `evidenced_by` and `derived_from` were cut for zero instances — `evidenced_by` doubly, since all 43 delta lines already carry in-band `(evidence: ...)` that `DELTA_EVIDENCE` enforces. `supersedes` was drafted, given an instance, and CUT at verify: its one candidate (M28 over M19) was refuted on measurement — the phantom-verb fixture M19 enumerates still exists, so M28 does not replace M19, the two are overlapping siblings, and M19 is still `open` -> if wrong the family ships a dead term, joining the three §3.2 keys that already have zero live uses · probe: every term in the vocabulary is used by at least one live relation in the shipped specs
- A4 [which] covers: S7 · the request does not say WHICH lessons get relations; taking the four the corpus already supports and no others — Q9 refines M21 refines M5 (the covers-binding chain, crossing quality.md into method.md) and M8 and M31 each refining M4 (the referent kinds the gate binds) — inventing no edge a reader of both lines would dispute, which is the bar that killed the fifth -> if wrong the migration fabricates structure the corpus does not have, and a vocabulary ends up justified by its own output
- A5 [which] covers: S2, S3, S4, S5, S6 · the request does not say which NODE TYPES may carry the key; taking every type under law 3 — a Task carrying `relations:` is read and reported, with a source naming no delta reported unresolved rather than refused -> if wrong the key is silently ignored on every type but Spec, which is the reading a maintainer cannot tell from a working one
- A6 [when] covers: S3 · the request does not say where the delta-id form falls in the §3.3 order; taking THIRD, after frontmatter key and after heading slug, so a reference that resolves today keeps resolving the same way -> if wrong an existing `#gives` or `#deltas` reference starts resolving to a delta line and every brief silently re-scopes · probe: a fragment that is both a frontmatter key and a delta id in one file still resolves as frontmatter
- A7 [when] covers: S1, S2, S4, S5, S6, S7 · the request does not say when a relation is evaluated; taking read-time on every doctor and validator run, with nothing stored and nothing cached — the same law that keeps activity derived -> if wrong a stored index answers for a corpus that has since been hand-edited, and the drift is invisible
- A8 [absent] covers: S2, S4 · the request does not say what an ABSENT `relations:` key means; taking absent equals no relations — zero tuples, zero findings, no crash — and requiring the finding to fire on a bundle that HAS one, so it is never a report that reads the same either way -> if wrong every one of the 209 nodes without the key emits a spurious line into a 459-line info report · probe: a bundle with no relations anywhere emits no relation finding while a bundle with one malformed entry emits exactly that finding
- A9 [absent] covers: S1, S3, S5, S6, S7 · the request does not say what an absent ENDPOINT means — a source id retired by hand, a target file or delta deleted; taking each end reported independently at info, so a half-dead relation stays visible instead of being dropped -> if wrong a relation that survived a delete reads as healthy and `add search` follows it into nothing
- A10 [order] covers: S2, S4, S5 · the request does not say the field order inside an entry; taking source then rel then target — subject verb object, three whitespace-separated fields — so a fourth field is malformed rather than silently ignored -> if wrong the two oracles split one line differently and R:DIVERGE lands on the live bundle
- A11 [order] covers: S1, S3, S6, S7 · the request does not say what wins when an entry is BOTH unknown-rel and out-of-bundle; taking every applicable finding emitted, with the fatal one never suppressed by the info one -> if wrong a containment escape hides behind an unknown-rel report and the only fatal code this family can raise becomes unreachable
- A12 [experience] covers: S4, S5 · the request does not say who RECEIVES a relation finding; taking the bundle maintainer running doctor before a gate, for whom a finding whose detail does not quote the offending entry verbatim is unactionable among 459 info lines -> if wrong the finding is noise the reader learns to skip, which is how a real one gets missed
- A13 [experience] covers: S6, S7 · the request does not say who reads FORMAT §3.2 or a migrated spec; taking an implementer of a SECOND ABF-1 engine, for whom the hard part is knowing the entry is a plain string and not a flow map — the exact divergence measured between our own two oracles -> if wrong a second engine ships a relations reader that agrees with neither of ours and every relation reads as garbage
- A14 [experience] covers: S1, S2, S3 · the request does not say who consumes these engine surfaces; taking the next task in this milestone, `add search`, traversing relations to answer at lesson granularity, for whom an unresolved target indistinguishable from a resolved one makes the traversal silently lossy -> if wrong search returns dead links as hits and the milestone's whole premise is unmet
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: a SECOND edge family, read from FRONTMATTER only.

```yaml
relations:
  - Q9 refines /specs/method.md#M21          # source id · rel · target concept
  - M28 supersedes /specs/method.md#M19
```

The source is a delta id in the node's OWN body; the target is any bundle concept address.
Both endpoints are concepts — which is what makes this a concept edge rather than the
file-granular edge this milestone exists to kill.

**Why frontmatter and not the delta line.** Authoring the relation as a `(refines: ...)` clause
on the delta line and DERIVING the frontmatter index was drafted and rejected on two grounds, not
on ergonomics. It breaks FORMAT law 1 — no derived artefact is ever authoritative, which is
exactly what `graph.json` being write-only protects — and it has no legal writer: `doctor --sync`
is barred by R:SYNCAUTHORED (it writes only what FORMAT declares COMPILED, and a Spec is
authored), `learn` cannot see a hand-edit it did not make, `fold` only closes an interval, and
this milestone's one new verb is spent on `add search`. A body-only relation was rejected too,
definitionally: §3.2 IS the frontmatter allowlist, so a body-only relation is not a §3.2 edge and
would not deliver the criterion. The frozen sibling's M10 keeps the delta tail OPEN and its check
stays green either way — M10 is a guarantee of parser TOLERANCE, not an obligation on a producer
— but `add.py`'s comment predicting that this task would append such a clause becomes a stale
prediction and is re-argued on the tolerance's own merits, with the tolerance and its check kept.

**Why `relations` is NOT added to `EDGE_KEYS`.** Tradeoff taken knowingly, against the advisor's
preference for an 8th composite-valued key. `edges()` yields `(src, key, ref, target)`; a
relation folded into that shape loses BOTH the source id and the rel type, and `_norm` on the
unsplit entry is precisely the containment downgrade M3 forbids. A separate `relations(graph)`
reader keeps every field, leaves `cycles()`'s adjacency and the `graph.json` export byte-identical,
and costs one extra loop in each oracle. §3.2 documents two families rather than one allowlist.

**`relations:` is NOT scaffolded** into a new node. `_is_template` exists because a scaffolded
`gives:` placeholder shadowed §3.3 fragment resolution, and a placeholder `scope:` turned 29 tests
red. `append_item` already creates a missing key, so a future writer needs no slot.

strategy: `RELATION_VOCAB` and a `relations(graph)` reader in add.py; `resolve()` gains the
delta-id form between heading slug and unresolved; `doctor()` grows one loop beside its existing
`edges(graph)` loop; `validate_bundle.py` mirrors all three from the same stated vocabulary;
FORMAT §3.2/§3.3/§9 state them. The family and the §3.3 form land in ONE change — landing the
family first would report `edge_unresolved` on every migrated instance while looking migrated.
Then the migration, then the four add.py twins, then ENGINE_MD5.

scope: add-method/tooling/add.py · add-method/tooling/engine_pin.py · add-method/scripts/validate_bundle.py · add-method/FORMAT.md · add-method/tests/engine · add-method/src/add_method/_bundled/tooling/add.py · .add/tooling/add.py · add-method/.add/tooling/add.py · .add/specs

known residue, declared not fixed: `join` keeps main's frontmatter while appending the stream's
delta lines verbatim, so a worktree stream's `relations:` is silently dropped — the mirror of
R:REUSEDID, and out of scope here.

regression floor: the full `tests/` suite plus `tooling/test_tree_parity.py` report 0 failed with
every pre-existing test body unmodified; the live bundle still reports 0 error under BOTH oracles;
`test_parity_with_m0_oracle` and `test_a_second_trailing_clause_leaves_the_delta_readable` — a
frozen sibling's checks — stay green untouched. ENGINE_MD5 is re-aimed; ENGINE_PKG_MD5 is not,
because no CLI surface changes.

## EDGES
- E1 an entry that is BOTH an unknown rel AND out of bundle: the info finding must not swallow the fatal one — both are reported for the one entry
- E2 a relation whose target file exists but whose delta id was deleted: `edge_unresolved`, never a crash and never silence
- E3 a `relations:` key on a node that has no `## Deltas` section at all: every source reports unresolved, nothing raises
- E4 a SELF edge — `M8 refines /specs/method.md#M4` lives IN method.md, so source cid equals target cid: it must manufacture no node-level edge, no dependency-cycle finding and no wave ordering, EVEN IF the family were wrongly folded into `EDGE_KEYS`

## CHECKS
- test_relation_vocabulary_is_closed_and_stated_once · covers: M1 · the engine states the closed vocabulary in one place
- test_the_second_oracle_mirrors_the_one_vocabulary · covers: M1 · the validator agrees BY BEHAVIOUR — every engine term silent, a non-term reported — so two lists cannot drift
- test_every_relation_term_is_used_by_a_live_relation · covers: R:DEADVOCAB, A3 · each term has an instance in the shipped specs; withholding one term's instance reds it
- test_both_oracles_parse_one_relation_entry_identically · covers: M2 · the plain-string entry yields the same value in add.py and the validator, where a flow map does not
- test_a_relation_escaping_the_bundle_is_fatal_like_a_depends_on · covers: M3, R:SILENTESCAPE · the same escaping target through `relations:` and through `depends_on:` reports `edge_out_of_bundle` at error in one assertion, in both oracles
- test_an_unknown_rel_is_recorded_not_rejected · covers: M4, R:REJECTUNKNOWN · `unknown_rel` is info, the exit code is unchanged, and the target still resolves
- test_a_delta_id_is_the_third_fragment_resolution_form · covers: M5 · a `#M4` fragment resolves with why `delta`, and a frontmatter key of the same name still wins
- test_a_frontmatter_key_still_beats_a_delta_id_of_the_same_name · covers: A6 · the probe for the §3.3 ordering reading
- test_a_relation_source_that_names_no_delta_is_reported · covers: M6 · a source id absent from the node's own body reports `edge_unresolved`
- test_a_malformed_relation_entry_is_never_dropped · covers: M7 · two fields and four fields each report `relation_malformed` and neither vanishes
- test_noising_every_body_leaves_the_relation_exit_code_unchanged · covers: M8 · §9's invariant re-run with relations present
- test_format_documents_the_relation_family_and_its_severities · covers: M9 · §3.2 names the family and the shape, §3.3 the third form, §9 every new code with its severity, read from the engine's own constants
- test_the_live_specs_carry_relations_that_resolve_on_both_ends · covers: M10 · a floor on the count, then every live relation resolving at source and at target
- test_relations_do_not_leak_into_the_edge_key_family · covers: M11 · `EDGE_KEYS` is unchanged and `edges()` returns nothing for a node whose only link is a relation
- test_both_oracles_agree_on_every_adversarial_relation · covers: R:DIVERGE · code AND detail compared across both oracles over a table of adversarial values, each of which can go red
- test_both_oracles_agree_on_relations_in_the_live_bundle · covers: R:DIVERGE · the live-bundle smoke half, since the dogfood parity oracle in test_graph.py is skipped
- test_an_unknown_rel_escaping_the_bundle_reports_both · covers: E1 · the info finding does not suppress the fatal one
- test_a_relation_to_a_deleted_delta_id_is_unresolved · covers: E2 · the target file exists, the concept does not
- test_a_node_with_no_deltas_reports_every_relation_source_unresolved · covers: E3 · a Task carrying relations is read and reported, never refused and never crashed
- test_a_concept_relation_manufactures_no_dependency_cycle · covers: E4 · the self-edge in the live specs produces no `dependency_cycle` finding and no entry in `cycles()`, proven against an adjacency built as if relations WERE edge keys
- test_an_absent_relations_key_emits_no_finding_and_a_present_one_does · covers: A8 · the probe against a report that reads the same either way
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- a vocabulary term is earned by an instance the corpus SUPPORTS, not by an instance you authored: `supersedes` shipped a migration edge (M28 over M19) that a refute-read disputed and a measurement killed — the phantom-verb fixture M19 enumerates still exists, so M28 never replaced it. R:DEADVOCAB binds the term to a live instance; nothing bound the instance to the corpus, so the check passed while the term died -> add learn method
- one spelling is not a containment test: `/specs/../../outside.md` was fatal all along and hid `../../outside.md`, which `_norm` clamped to `/outside.md` — inside the bundle — silently downgrading one of the three FATAL codes to info for BOTH edge families. `os.path.normpath` cannot ascend above `/`, so a cid-builder must never be the containment oracle. Found by an adversarial sweep; the suite never asked -> add learn quality
- a parity check over a CLEAN corpus compares `[]` with `[]`: the live-bundle oracle for R:DIVERGE stayed green with BOTH relation readers deleted. A parity claim needs values that each produce a finding, plus controls that must stay silent — otherwise it proves the two tools agree about nothing -> add learn quality
- two parsers of one format diverge on what neither was written to handle: the engine strips a YAML ` #` comment and the M0 validator did not, so `M1 refines #M2` was two fields in one and three in the other, and a bare `- ` was `{}` here and `[]` there. Byte-identical VALUES is the claim; equal code paths is not -> add learn system
- a stated REASON is a claim and rots like any other: FORMAT §3.3 justified the resolution ladder with "the two sets cannot intersect", which `DELTA_ID`'s own `[A-Za-z]` makes false. The behaviour was right and the reason was wrong, which is worse than silence for the second-engine implementer the assumption named as the reader -> add learn method
