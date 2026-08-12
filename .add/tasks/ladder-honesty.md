---
type: Task
title: verify.md — every documented rung must be stampable
status: done
depth: standard
milestone: all-domain-evidence
scope:
  - add-method/skill/add
  - add-method/src/add_method/_bundled/skill/add
  - .claude/skills/add
  - add-method/tests/skill
gives:
  - S1 the evidence-kind ladder — the rungs `verify.md` tells an agent to expect on a receipt
generated: { by: add/3.1.0, at: 2026-08-12 }
verified:
  - { by: "Tin Dang", at: 2026-08-12, act: freeze, authority: human, direction: "sha256:e7313c1f55e840e0" }
  - { by: "cli", at: 2026-08-12, act: brief, authority: process, brief: "sha256:74942d0437f0e909" }
  - { by: "process:run", at: 2026-08-12, act: run, authority: process, outcome: PASS, receipt: /tasks/ladder-honesty.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-08-12, act: gate, authority: process, outcome: PASS, receipt: /tasks/ladder-honesty.d/runs/1.md, brief: "sha256:74942d0437f0e909" }
---
## CARD
goal: every evidence rung the skill documents is one the engine can actually stamp, and every kind it can stamp is documented
why: `verify.md` promises `test-ids > artifact-hash > command-exit > human-observed`. The engine writes exactly `test-ids`, `command-exit` (add.py:1929) and `sources` (add.py:2781). So the doc is wrong in BOTH directions — two rungs that can never be earned, and one real kind it never mentions. An unearnable rung is not a ladder, it is a label.
beat: done · next: add status

## RULES
<must>
- M1 every evidence kind the skill documents must be one the engine can stamp
- M2 every kind the engine can stamp must be documented — the orphan direction, the same asymmetry that let `domains.md` and `terms.md` ship unreachable
- M3 the change must land byte-identical across all three skill trees
</must>
<reject>
- R:PINSTRINGS pinning today's rung names as literals in the check — the guard must DERIVE the set from the engine, or it goes stale exactly the way the doc it replaces did -> "PINSTRINGS"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · n/a · the engine alone writes a receipt kind; no actor chooses one
- A2 [which] covers: S1 · the request does not say whether `sources` belongs on the same ladder as the run kinds; taking "yes — it is a kind the engine stamps on a gate, and a reader who never sees it cannot recognise it on an explore receipt" -> if wrong, the ladder mixes two incomparable axes and implies an explore is weaker than a command-exit
- A3 [when] covers: S1 · n/a · a kind is stamped at run or gate; the ladder describes strength, not timing
- A4 [absent] covers: S1 · the request does not say what to do about the two unearnable rungs; taking "DELETE, not demote — a rung nothing can stamp is not a weak rung, it is a false one, and `add learn` already records honest weakening elsewhere" -> if wrong, the doc keeps teaching a ladder with phantom steps
- A5 [order] covers: S1 · the request does not say what orders the kinds; taking "the engine's own promotion rule — `test-ids` only when a runner reported IDs, else `command-exit` — with `sources` named separately as the explore path's kind rather than ranked against them" -> if wrong, a reader ranks an explore receipt against a test receipt and picks the wrong lane

## PLAN
contract: one honest ladder line in `verify.md`, and a DERIVED guard that keeps the docs and the engine from drifting apart again
strategy: the guard is the point, not the line. Four documentation-vs-engine drifts have now surfaced in this milestone (phantom profiles, orphan refs, the receipt-path leak, these rungs) and nothing in the repo systematically checks shipped prose against engine reality. This closes the rung instance with a check that reads `add.py` rather than pinning strings — so it stays true when the engine gains or loses a kind.
scope: add-method/skill/add, add-method/src/add_method/_bundled/skill/add, .claude/skills/add, add-method/tests/skill

## EDGES
- E1 a kind the engine stamps in a branch the extractor cannot see — the guard must fail loud on an empty extraction rather than pass vacuously on finding nothing

## CHECKS
- test_documented_rungs_are_stampable · covers: M1 · every kind the skill names is one the engine emits
- test_stampable_rungs_are_documented · covers: M2 · every kind the engine emits is named by the skill
- test_rung_set_is_derived_not_pinned · covers: R:PINSTRINGS · the extractor picks up a fabricated kind from synthetic source, proving it reads the engine rather than a literal list
- test_extractor_fails_loud_on_empty · covers: E1 · an extraction that finds nothing raises rather than passing vacuously
- test_skill_bundle_matches_canonical · covers: M3 · package payload tree matches canonical
- test_dogfood_skill_matches_canonical_when_present · covers: M3 · dogfood mirror matches canonical
red-first: TWO are driven red — M1 fails on `artifact-hash`/`human-observed`, M2 fails on the undocumented `sources`. FOUR are guards, declared: R:PINSTRINGS and E1 are properties of the extractor and went green as soon as it was authored (they are Direction artefacts, not build outcomes), and the two parity tests catch a missed tree. NOTE the extractor was itself wrong on its first run — an unanchored ternary pattern swept up freshness values (`content`/`mtime`) and manufactured five phantom failures; anchoring every pattern on `kind` fixed it. A derived guard is only as honest as its anchor.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
