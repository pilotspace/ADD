---
type: Task
title: Spec nodes carry OKF's recommended frontmatter, and the bundle declares its OKF version
status: done
depth: standard
sensitivity: architecture
milestone: okf-graph-time
scope:
  - add-method/tooling/add.py
  - add-method/tooling/engine_pin.py
  - add-method/src/add_method/_bundled/tooling
  - add-method/FORMAT.md
  - add-method/tests/engine/test_spec_okf_frontmatter.py
  - add-method/tests/engine/test_init_identity.py
  - .add/tooling
  - add-method/.add/tooling
  - .add/specs
  - .add/index.md
gives:
  - S1 `init()` Spec scaffold — the OKF frontmatter block written to every scaffolded Spec node
  - S2 `init()` bundle header — `okf_version` on the bundle-root `index.md`
  - S3 `_render_index()` Specs-section row — the catalogue detail read from a Spec's description
  - S4 `FORMAT.md` — the documented OKF frontmatter contract for a Spec and for the bundle header
  - S5 the five backfilled live Spec nodes under .add/specs/
  - S6 `.add/index.md` — this bundle's own okf_version declaration
generated: { by: add/3.4.0, at: 2026-09-03 }
verified:
  - { by: "plan:okf-graph-time", at: 2026-09-03, act: freeze, authority: plan, direction: "sha256:d8f8197b0725f27c", binding: "sha256:e022d65552d3fadc" }
  - { by: "cli", at: 2026-09-03, act: brief, authority: process, brief: "sha256:9b90d37418ce8d20" }
  - { by: "process:run", at: 2026-09-03, act: run, authority: process, outcome: FAIL, receipt: /tasks/okf-spec-frontmatter.d/runs/1.md }
  - { by: "plan:okf-graph-time", at: 2026-09-04, act: refreeze, authority: plan, direction: "sha256:48de3b50b9b9e916", binding: "sha256:e022d65552d3fadc" }
  - { by: "cli", at: 2026-09-04, act: brief, authority: process, brief: "sha256:ac45d18c4db1d710" }
  - { by: "cli", at: 2026-09-04, act: brief, authority: process, brief: "sha256:94a2b7617df7010c" }
  - { by: "process:run", at: 2026-09-04, act: run, authority: process, outcome: PASS, receipt: /tasks/okf-spec-frontmatter.d/runs/2.md }
  - { by: "plan:okf-graph-time", at: 2026-09-04, act: gate, authority: plan, outcome: PASS, receipt: /tasks/okf-spec-frontmatter.d/runs/2.md, brief: "sha256:94a2b7617df7010c" }
advised_by: engine-notary
---
## CARD
goal: a Spec node carries OKF v0.2's recommended description/tags/sources, the bundle root declares `okf_version: "0.2"`, and the index catalogue is rendered from the description so the key has a reader on the day it lands
why: ADD's specs already look OKF-shaped by accident but declare no version and carry no catalogue line, so `.add/index.md` lists five bare titles and nobody can tell which lens to open — and this repo has measured three FORMAT §3.2 edge keys with ZERO live uses, so a key added without a reader is a compatibility burden forever — `description:` therefore ships WITH its reader, and `tags:`/`sources:` ship as slots a human fills, never as keys that claim a consumer they do not have
beat: done · next: add status

## RULES
<must>
- M1 `init` writes OKF's recommended `description:` and `tags:` plus provenance `sources:` into every Spec it scaffolds, using OKF's own key names, with `description:` carrying that lens's own goal string. `description:` is what the LENS IS FOR — stable, machine-read, a catalogue label; `## Now` is what is CURRENTLY TRUE in this project's lens — a living statement that should drift as the project moves. They coincide only at birth, because `init` seeds both from one goal string; thereafter they diverge legitimately and neither is stale
- M2 `init` writes `okf_version: "0.2"` into the bundle-root index frontmatter and into no other file — OKF v0.2 declares the version once, at the root
- M3 a Spec's `description:` is the machine-read catalogue line: the Specs-section row is rendered from that frontmatter key rather than from the preserved index tail — the same STRUCTURAL rule a Persona's row already follows through its `use-when:`, though not the same key (a Persona's own `description:` is read by nothing) — so the index can never disagree with the node
- M4 `okf_version:` survives a `doctor --sync` that rewrites the index body — bundle-header frontmatter is carried across verbatim, never recomputed
- M5 the five live specs under .add/specs/ and this bundle's index carry the new keys, and every spec that holds deltas still holds its `delta_seq:` counter
- M7 the payoff is realised in THIS bundle, not only in a scaffold: `.add/index.md`'s Specs section is recompiled so each row carries its node's description — an index left with five bare titles is M3 reported green and not delivered
- M8 `okf_version` has a READER: `doctor` reports an `okf_conformance` finding derived from the declared version and the bundle's Spec nodes. The stamp was REMOVED on 2026-08-08 (baa066ae) for a reason that is still true — "nothing in the engine, the validator, or the skill ever READS it" — and re-landing dead metadata would reverse that decision rather than answer it. The old guard's RULE (no key that nothing reads) is kept and re-aimed; only its factual premise about this key changes, and this rule is what changes it
- M9 `tests/engine/test_init_identity.py`'s OKF assertion is re-aimed, never deleted: it must still assert something about `okf_version` in a fresh bundle, and its sibling assertions (`abf_version` present, the project named for the project) must survive untouched
- M6 FORMAT documents the contract: `okf_version` in the bundle-header key list, and a Spec frontmatter paragraph saying which of the three keys this engine READS and which it merely records
</must>
<reject>
- R:TAILEATEN a Spec with no `description:` losing its authored index tail when the index is recomputed -> "TAILEATEN"
- R:OKFSPRAWL `okf_version:` written onto any node other than the bundle-root index -> "OKFSPRAWL"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1,S2,S4 · the request does not say who fills description/tags/sources after the scaffold; taking "the authoring human or agent — the engine writes the seed and then never validates, lints or edits them (NO-EXEC)" -> authors wait for a lint that never comes and the keys rot
- A2 [who] covers: S3 · the request does not say whose sentence wins when a hand-edited index row disagrees with the node; taking "the NODE wins — the row is recomputed from frontmatter, the rule already applied to a Persona's use-when:" -> an authored index tail is overwritten, bounded by E1's fallback
- A3 [who] covers: S5,S6 · the request does not say who backfills an EXISTING bundle; taking "a human or agent by hand, never `doctor --sync` — a Spec is not a compiled file and the bundle header's frontmatter is never rewritten (FORMAT §1.1, R:SYNCAUTHORED); this task backfills THIS repo by hand" -> every bundle in the wild silently lacks the keys and a future search finds nothing
- A4 [which] covers: S1,S4 · the request does not say which OKF keys are in; taking "description + tags + sources only — OKF `status:` and `stale_after:` excluded by decision (status collides with ADD's task lifecycle, precedent test_no_okf_doc_status_key), and relations: belongs to the sibling typed-relations task" -> rework inside the same milestone · probe: a scaffolded Spec carries neither a status: nor a stale_after: key
- A5 [which] covers: S2,S6 · the request does not say which files declare the OKF version; taking "the bundle-root index and nothing else" -> N declarations that can disagree with each other
- A6 [which] covers: S3 · the request does not say which node types change how their row is rendered; taking "only Spec — Project, Milestone, Task and Persona rows keep the detail rule they have today" -> an unrelated index section churns under a change that claimed not to touch it
- A7 [which] covers: S5 · the request does not say which live specs; taking "all five under .add/specs/ — add-method/.add/ is a gitignored secondary bundle and is left alone" -> a second bundle diverges from the format it ships
- A8 [when] covers: S1,S2 · the request does not say when the keys appear; taking "at init time only — the scaffold writer never overwrites, so re-running init on an existing bundle adds nothing and clobbers nothing" -> authors expect a re-init to upgrade an old bundle and it silently does not
- A9 [when] covers: S3 · the request does not say when the Specs row re-reads the description; taking "on every index recompute, the same trigger the Persona row already uses" -> a stale row until an unrelated change forces a rebuild
- A10 [when] covers: S4,S5,S6 · the request does not say when the document and the live bundle change relative to the engine; taking "in this one task, together — a documented key with no scaffold, or a scaffold with no document, is exactly the drift lesson M25 records" -> FORMAT promises a key the engine never writes
- A11 [absent] covers: S1 · the request does not say what an empty tags/sources means; taking "an empty inline list means NOT YET CLASSIFIED, never has-no-tags — and it is scaffolded as a real empty list, never a placeholder string, so the first consumer reads an empty list and not a one-item list of angle-bracket text" -> placeholder text pollutes the first consumer · probe: a scaffolded Spec's tags and sources each parse as an empty list
- A12 [absent] covers: S3 · the request does not say what an ABSENT description renders as; taking "the authored index tail is used instead, and where there is no tail the row carries no detail at all rather than a dangling separator" -> R:TAILEATEN, authored prose lost on an old bundle's first sync
- A13 [absent] covers: S2,S6 · the request does not say what an absent okf_version means; taking "a pre-OKF bundle — recorded, never refused (law 3): no verb gains a refusal and `doctor` gains no new finding code" -> every existing bundle in the wild starts reporting a finding nobody asked for
- A14 [absent] covers: S4,S5 · the request does not say what an absent description means on a LIVE spec; taking "an absent description means the key is simply not supplied — FORMAT states it is RECOMMENDED, never required, and the index falls back to the preserved tail rather than treating the Spec as defective; separately, none is absent here because all five are backfilled" -> a conformance claim stronger than the engine enforces
- A15 [order] covers: S1,S5 · the request does not say key order; taking "description then tags then sources, inserted after project: and before generated:, matching the Persona scaffold's OKF tail; delta_seq: keeps its own position and its value" -> cosmetic diff churn only
- A16 [order] covers: S2,S6 · the request does not say where the version key sits; taking "immediately after abf_version:, so the two format declarations read together" -> cosmetic only
- A17 [order] covers: S3 · the request does not say what orders the Specs section; taking "unchanged — sorted by concept id, as today" -> the index reorders under a change that claimed to touch only the detail text
- A18 [order] covers: S4 · the request does not say where in FORMAT the contract lands; taking "the §1 bundle-header key row gains the version key, and §3 gains a Spec-frontmatter paragraph beside the existing type vocabulary" -> a reader looks in §2 and misses it
- A19 [experience] covers: S1,S5 · the request does not say who receives a scaffolded Spec; taking "the author opening a fresh specs/method.md, for whom the hard part is a key whose purpose is invisible — so description arrives already carrying the lens goal instead of angle-bracket text they must decode; on a LIVE spec that generic goal is then replaced with a bundle-specific line, because a row restating the lens taxonomy tells a cold reader nothing they did not already know" -> three empty keys read as noise and get deleted
- A20 [experience] covers: S3,S6 · the request does not say who reads the rendered index; taking "a cold reader scanning .add/index.md to decide which spec to open, for whom the hard part today is five bare titles with no line saying what each lens is for" -> the catalogue stays unreadable and the milestone's stated why is unaddressed
- A21 [experience] covers: S2 · the request does not say who reads the version declaration; taking "an external OKF tool inspecting the bundle root and a human auditing conformance — both need it at the root and quoted as a string, so the value never parses as a float and never round-trips as 0.20" -> a consumer compares a number against a string and reads the bundle as unversioned · probe: the declared value reads back as the two-character string, not as a number
- A22 [experience] covers: S4 · the request does not say who reads FORMAT's new text; taking "an implementer of a second ABF-1 engine, for whom the hard part is telling REQUIRED from RECOMMENDED — so the paragraph must say plainly that description is read by the index and that tags and sources are recorded and read by nothing in this engine" -> a re-implementer enforces a key ADD itself never enforces

## PLAN
contract: three literals added to `init`'s Spec scaffold and one to its index header; one line of `_render_index` prefers a Spec's `description:` over the preserved tail; FORMAT §1 and §3 state the contract; the live bundle is backfilled by hand. No verb is added, no refusal is added, no `doctor` finding code is added — the engine stays a notary that writes a seed and reads it back.
strategy: red-first in `tests/engine/test_spec_okf_frontmatter.py`, then the engine, then FORMAT, then the hand backfill, then recompile `.add/index.md` so the Specs rows actually carry the descriptions (checking `card_drift` is empty first, so a full sync cannot rewrite a sibling task's node). The engine edit forces a twin sweep: `add-method/tooling/add.py` is canonical, `add-method/src/add_method/_bundled/tooling/add.py` is the parity-enforced package twin, and `.add/tooling/add.py` plus `add-method/.add/tooling/add.py` are the two gitignored vendored copies the CLI actually executes — all four go byte-identical and `ENGINE_MD5` is re-aimed in the same change, prior pointer kept.
scope: add-method/tooling/add.py · add-method/tooling/engine_pin.py · add-method/src/add_method/_bundled/tooling · add-method/FORMAT.md · add-method/tests/engine · .add/tooling · add-method/.add/tooling · .add/specs · .add/index.md
regression floor: `add-method/tooling/test_tree_parity.py` green (8 tests); `tests/engine/test_persona_index.py` green UNMODIFIED — it is the one pre-existing pin on a `_render_index` detail branch, including the stale-authored-tail overwrite, so it is the named proof that the Persona branch is untouched; and `tests/engine` green at its 798-passed/7-skipped baseline with every pre-existing test unmodified — the untouched path proven by the suite that already covered it, never by "should be unaffected".

## EDGES
- E1 a Spec with no `description:` — an existing bundle never re-scaffolded — keeps its authored index tail through a recompute, and a Spec with neither carries no detail rather than a dangling separator
- E2 the `doc` profile scaffolds four lenses, not five: each one gets all three keys, with `description:` seeded from that profile's own goal string and not from the `code` profile's

## CHECKS
- test_init_scaffolds_okf_keys_on_every_spec · covers: M1,A11 · every scaffolded Spec carries description == its profile lens goal, and tags/sources each parse as an empty list, never a placeholder string
- test_okf_version_is_declared_only_at_the_bundle_root · covers: M2,R:OKFSPRAWL,A21 · the index exists and declares the two-character string "0.2"; no other file init writes declares okf_version
- test_index_specs_row_reads_the_node_description · covers: M3 · the rendered Specs section carries each spec's frontmatter description as its detail
- test_okf_version_survives_doctor_sync · covers: M4 · after a sync that rewrites the index body, the header still reads "0.2"
- test_a_spec_without_a_description_keeps_its_authored_index_tail · covers: E1,R:TAILEATEN · three subjects in one rendered index: a described spec shows its description, a description-less spec with an authored tail keeps that tail, and a description-less spec with NO tail renders a bare row rather than a dangling separator
- test_doc_profile_specs_carry_okf_keys_too · covers: E2 · four lenses under the doc profile, each seeded from that profile's own goal
- test_live_specs_and_index_are_backfilled · covers: M5,A14 · this repo's five specs each carry a non-empty description plus list-valued tags and sources, at least four specs match the dated delta grammar and every one that does still holds delta_seq, and .add/index.md declares okf_version
- test_live_index_catalogue_carries_each_spec_description · covers: M7 · the Specs section of .add/index.md renders every live spec's own description as its catalogue line, and no live description is merely the generic profile goal string
- test_format_documents_the_okf_frontmatter_contract · covers: M6,A4,A22 · FORMAT names okf_version in the bundle-header keys and states, for a Spec, which keys are read and which are only recorded — and names neither status nor stale_after as a Spec key
- test_doctor_reports_okf_conformance · covers: M8 · a bundle declaring okf_version yields an `okf_conformance` finding naming the declared version and the Spec/description counts, and a bundle declaring none yields no such finding — the reader discriminates, it does not always fire
- test_init_identity_guard_still_binds_the_okf_stamp · covers: M9 · the re-aimed guard asserts the stamp is PRESENT and deliberate, its abf_version and project-naming assertions are untouched, and the file still names okf_version so a silent re-removal goes red
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
