---
type: Task
title: one placeholder oracle, one covers grammar, and no doc that contradicts the engine
status: done
depth: standard
sensitivity: architecture
milestone: loop-that-drains
scope:
  - add-method/tooling
  - add-method/tests
  - add-method/.add/tooling
  - add-method/src/add_method/_bundled/tooling
  - .add/tooling
  - .add/personas
gives:
  - S1 ONE placeholder oracle — every reader of template text applies the same code-span stripping rule
  - S2 ONE covers: grammar — a list of referents parses identically wherever it is written
  - S3 doc-truth on two numbers the engine contradicts — the front-door claim guard and the steward persona
generated: { by: add/3.5.0, at: 2026-09-08 }
verified:
  - { by: "plan:loop-that-drains", at: 2026-09-08, act: freeze, authority: plan, direction: "sha256:8a29b0a1302846f6", binding: "sha256:a214a014483300ee" }
  - { by: "cli", at: 2026-09-08, act: brief, authority: process, brief: "sha256:09d2978fa3670163" }
  - { by: "process:run", at: 2026-09-08, act: run, authority: process, outcome: PASS, receipt: /tasks/one-oracle-one-truth.d/runs/1.md }
  - { by: "plan:loop-that-drains", at: 2026-09-08, act: gate, authority: plan, outcome: PASS, receipt: /tasks/one-oracle-one-truth.d/runs/1.md, brief: "sha256:ec5b744156f9addc" }
---
## CARD
goal: the engine tells one story about what a placeholder is, one about what a covers: list is, and no doc quotes a number the engine has moved
why: the placeholder oracle has three readers and two rules — `placeholders_in` and `_placeholder_only` strip code spans before matching, `gives_unauthored` and the milestone EXIT box check do not — so a line written in the engine's own vocabulary reads as unauthored scaffold. It refused this milestone's own freeze twice. The `covers:` key is worse than inconsistent: the ASSUMPTIONS reader takes everything up to the next separator, the CHECKS reader splits on commas ALONE, so a space-separated covers: in CHECKS parses as one rule name and binds NOTHING while looking correct — the vacuous-binding class this whole milestone is about. And two docs state numbers the engine contradicts.
beat: done · next: add status

## RULES
<must>
- M1 every reader of template text applies the SAME rule: a backticked span is code and is stripped before the placeholder match, so `gives_unauthored` and the milestone EXIT box check agree with `placeholders_in`
- M2 a `covers:` list parses identically in ASSUMPTIONS and in CHECKS: referents separate on commas OR whitespace, so a space-separated list binds exactly what a comma-separated one binds
- M3 `test_front_door_claims_hold.py` states what `deltas` actually prints, in its docstring and in its assertion message alike
- M4 `.add/personas/method-steward.md` cites the pin's test rather than copying its number, so a re-pin cannot leave it lying
- M5 no reader is loosened: a line that is genuinely all template still reads as unauthored, and a `covers:` entry that names nothing still binds nothing
</must>
<reject>
- R:LOOSENED making the oracles agree must never make either accept a line it should refuse -> "LOOSENED"
- R:SILENTBIND a covers: list must never parse into a referent name that no rule could ever match -> "SILENTBIND"
- R:RECOPIED a doc must never be repaired by copying the engine's current number into it -> "RECOPIED"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2 · the request does not say who these oracles serve; taking the reading that both serve the AUTHOR at direction and the gate at verify identically, which is exactly why two rules is a defect rather than a specialisation -> a reader tuned per caller would reintroduce the split under a different name
- A2 [who] covers: S3 · the request does not say who owns the persona's budget number; taking the reading that the TEST owns it and the persona cites the test, so there is one writer -> two writers of one number is how it rotted
- A3 [which] covers: S1 · the request does not say which readers must change; taking the reading that it is exactly the two that disagree — `gives_unauthored` and the milestone EXIT box check — and that the two already correct are left byte-untouched · probe: the four readers agree on a line containing a backticked engine token
- A4 [which] covers: S2 · the request does not say which separators are legal; taking the reading that commas and whitespace both separate, since the ASSUMPTIONS reader already accepts both and the CHECKS reader is the one that is narrower · probe: a space-separated covers: in CHECKS binds the same referents a comma-separated one binds
- A5 [which] covers: S3 · the request does not say which docs are in; taking the reading that it is the two the backlog actually named, X6 and M3, and no wider doc sweep -> a general doc audit is its own task with its own budget
- A6 [when] covers: S1, S2 · the request does not say when the change takes effect for already-frozen nodes; taking the reading that it is immediate and retroactive, because both fixes only ever ADD parses that should always have worked — nothing already accepted stops being accepted (this is M5)
- A14 [when] covers: S3 · the request does not say when a doc-truth citation goes stale; taking the reading that it cannot, because the citation names a file rather than a value — the whole point of citing the pin is that there is no second copy to drift · probe: the persona carries no number a test could contradict
- A7 [absent] covers: S1 · the request does not say what an empty `gives:` means; taking the reading that it stays unauthored, unchanged — the off-switch that predicate exists to close is deleting `gives:`, and the code-span rule does not touch that case · probe: an absent gives: still reads unauthored
- A8 [absent] covers: S2 · the request does not say what an empty covers: means; taking the reading that it yields no referents and binds nothing, exactly as today -> yielding an empty-string referent is R:SILENTBIND with a different shape
- A9 [absent] covers: S3 · the request does not say what an absent pin means; taking the reading that the persona cites the test by PATH, so a reader who cannot find it knows the citation is stale rather than reading a number
- A10 [order] covers: S2 · the request does not say what order referents keep; taking the reading that document order is preserved, since `covers()` builds a dict keyed by rule and order has never been asserted anywhere
- A11 [order] covers: S1, S3 · n/a — a placeholder match is a boolean per line and a doc citation is one sentence; neither carries a sequence for anything to order
- A12 [experience] covers: S1 · the receiver is an author writing about the engine in the engine's own vocabulary, and what would make this hard is a refusal that cannot be complied with; taking the reading that backticking the token is the documented way to write it literally · probe: a criterion naming a backticked engine token freezes clean
- A13 [experience] covers: S2, S3 · the receiver is an author who wrote a covers: list the way the neighbouring section writes one; taking the reading that both spellings simply work, so nothing must be learned and no refusal is added -> a refusal on the narrower spelling would teach a rule that exists only because of a parser

## PLAN
contract: `gives_unauthored` and the milestone EXIT box check route their placeholder test through one shared helper that strips backticked spans first — the same `re.sub(r"`[^`]*`", "", line)` the other two readers already apply. `COVERS_IN_CHECK`'s consumer splits on `[,\s]+` rather than `,`. `test_front_door_claims_hold.py`'s docstring and assertion message state the real output. `method-steward.md` cites `test_surface.py` instead of quoting 150.
strategy: checks red first, including one that asserts all four placeholder readers agree on the SAME input — the defect is disagreement, so the check must compare them rather than test each. Full suite before the receipt (B-M3).

## EDGES
- E1 a line that is entirely a backticked engine token and nothing else still reads as authored
- E2 a line with a real angle-bracket placeholder OUTSIDE backticks still reads as unauthored
- E3 a CHECKS covers: mixing commas and whitespace binds every referent in it
- E4 an empty or absent `gives:` still reads unauthored, unchanged by the code-span rule
- E5 a covers: entry naming a referent that does not exist still binds nothing and is not invented

## CHECKS
- test_all_four_placeholder_readers_agree · covers: M1, A3, A12, E1 · one line carrying a backticked engine token is read the same way by `placeholders_in`, `_placeholder_only`, `gives_unauthored` and the milestone EXIT box check, and a milestone criterion naming such a token freezes clean
- test_a_real_placeholder_still_refuses · covers: M5, R:LOOSENED, A7, E2, E4 · an angle-bracket slot outside backticks still reads unauthored, and an absent or empty `gives:` is unchanged
- test_covers_splits_on_commas_or_whitespace · covers: M2, A4, A10, E3 · a space-separated, a comma-separated and a mixed covers: bind the identical referent set in document order
- test_covers_invents_no_referent · covers: R:SILENTBIND, A8, E5 · an empty covers: yields nothing and a covers: naming an absent rule binds nothing, with no empty-string referent produced
- test_the_front_door_guard_states_the_real_output · covers: M3, A5 · the docstring and the assertion message both name the address form `deltas` actually prints, and neither carries the retired form
- test_the_persona_cites_the_pin · covers: M4, R:RECOPIED, A2, A9, A14 · the persona names the pin's test file and carries no hard-coded budget number that the test could contradict
red-first: every check MUST fail first.

## EVIDENCE
receipt: pending
gate: pending

## LESSONS
- pending
