---
type: Task
title: every verb refuses with None
status: direction
depth: standard
milestone: refuse-in-one-voice
scope:
  - add-method/tooling/add.py
  - add-method/tests/engine/test_refuse_with_one_shape.py
  - add-method/tests/
  - add-method/tooling/engine_pin.py
gives:
  - S1 the `(value, message)` return contract every verb in the engine shares — what its first element means when it is falsy
generated: { by: add/3.6.0, at: 2026-09-10 }
verified:
  - { by: "plan:refuse-in-one-voice", at: 2026-09-10, act: freeze, authority: process, direction: "sha256:cffd60e4bde3de5d", binding: "sha256:e37997c610d7465f" }
  - { by: "builder", at: 2026-09-10, act: replan, authority: process, note: "A2's survey missed two things the sweep found. (1) `done` returns 3-TUPLES, so a sweep looking at 2-tuples could not see its two False refusals — 37 sites, not 35. (2) Six verbs answer an empty COLLECTION from a query that ran (deltas, search, interview, todo, locate, neighborhood); that is an answer, not a refusal, and my caller sweep wrongly tightened 10 of those assertions to `is None` before the suite caught it. RESULT_VERBS now covers both shapes: a boolean no, and an empty collection." }
  - { by: "plan:refuse-in-one-voice", at: 2026-09-10, act: refreeze, authority: process, direction: "sha256:cffd60e4bde3de5d", binding: "sha256:e37997c610d7465f" }
---
## CARD
goal: a caller writing `if x is None` sees every refusal the engine can give, from any verb
why: two checks in one branch were GREEN only because `freeze` refused with `False`, and `False is not None`. Eleven verbs still answer that way, so the class is live — and the caller crossing two verbs is the one who pays, because each verb is self-consistent and none of them looks wrong on its own
beat: direction · next: add freeze refuse-with-one-shape

## RULES
<must>
- M1 `None` is the refusal shape, bundle-wide: a verb that could not do its work returns `None` as its first element, whatever the verb
- M2 a boolean RESULT is not a refusal and keeps its boolean — a verb answering a yes/no question may still return `False` when the honest answer is no
- M3 a verb that answers a question gains a third state where one is real: `True` yes · `False` no · `None` cannot tell, and the caller can distinguish all three
- M4 a check ENUMERATES every verb and holds each to M1/M2, so a verb added later cannot answer a refusal in a second shape
- M5 every message is unchanged by this task — only the falsy first element moves, and a `git diff` shows no string edits
- M6 no caller is left asserting a refusal by truthiness where identity is what it means
</must>
<reject>
- R:TWOSHAPES a verb answers a refusal with a falsy value that is not `None` -> "TWOSHAPES"
- R:LOSTANSWER an honest `False` result is rewritten as `None`, so a caller can no longer tell no from cannot-tell -> "LOSTANSWER"
- R:SILENTCALLER a caller keeps an assertion that passes under both the old shape and the new, and so proves nothing about either -> "SILENTCALLER"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the request does not say who consumes the first element; taking "every in-repo caller and every test — the engine is not a published Python API, and `cli.py` is the only shipped consumer, which reads it as a truthy exit code" · found: 11 verbs answer `False`, 38 sites; 122 in-repo assertions touch `is False`, `== False`, `assert not ok` or `assert not node` (evidence: AST survey + grep over add-method/tests, add-method/tooling) -> an unannounced contract change breaks a consumer nobody enumerated
- A2 [which] covers: S1 · the request does not say which `False` returns are refusals; taking "a return is a REFUSAL when the verb did not do its work, and a RESULT when the verb ran and the answer is no" · found: 35 of 38 are refusals; the exceptions are `fresh` at add.py:3633 and :3636 (`changed since the run`, `has vanished` — the receipt is genuinely stale, which is the ANSWER) and `render_card` at :3035 (`card is current` — nothing to render). `fresh` at :3622 (`no content digest — freshness cannot be established`) IS a refusal and moves (evidence: add.py, read at each site) -> the sweep destroys `fresh`, whose whole job is to answer no
- A3 [when] covers: S1 · the request does not say when a verb should GAIN the third state; taking "only where cannot-tell is genuinely different from no — `fresh` is the one: stale and unmeasurable are different facts, and the engine already refuses to report UNKNOWN as a clean answer elsewhere (R:UNKNOWNCLEAN)" -> a third state is invented for verbs that have no use for it, and every caller grows a branch it never takes
- A4 [absent] covers: S1 · the request does not say what a caller asserting `assert not ok` means after the change; taking "it is now AMBIGUOUS — it passes on both `False` and `None`, so it proves nothing about which the verb gave; every such caller on a refusal path is tightened to `is None` (R:SILENTCALLER)" -> 122 assertions keep passing while the contract underneath them changes, which is the shape that hid two green checks
- A5 [order] covers: S1 · the request does not say the order of conversion; taking "one verb at a time, each with its callers, because a half-converted verb is the exact state the bug lives in" -> a partial sweep leaves the mixed shape this task exists to remove
- A6 [experience] covers: S1 · the request does not say what the enumerating check says when it fires; taking "the verb, the line number and the value it returned, plus the one question that decides it — did the verb DO its work, or ANSWER a question?" -> the author is told a shape is wrong with no way to know which of the two rules applies

## PLAN
contract: every refusal in the engine returns `(None, message)`. A boolean RESULT keeps its boolean, and `fresh` becomes genuinely three-valued — `True` fresh · `False` stale · `None` cannot establish. 35 of 38 `False` sites move; 3 stay, each with a comment saying why. Every message is byte-identical afterwards. A static check walks the module AST, groups returns by function, and refuses any falsy first element that is neither `None` nor a documented boolean result.
strategy: the enumerating check first, so it names its own 38; then verb by verb with its callers (A5); the three exceptions last, so the exception list is written against a suite that is otherwise already green.

## EDGES
- E1 `fresh` — the one verb where the sweep would destroy meaning: two results stay, one refusal moves
- E2 `render_card`'s `card is current` — a result that reads like a refusal because the message is terse
- E3 a caller asserting `assert not ok` on a refusal path — passes under both shapes, so it proves nothing and must be tightened (R:SILENTCALLER)
- E4 a caller asserting `assert not ok` on a RESULT path (`fresh` returning stale) — must NOT be tightened to `is None`, which would invert it
- E5 `cli.py` turns the first element into an exit code by truthiness — every conversion must leave the exit code unchanged
- E6 a verb added after this task that answers a refusal with `False` — the enumerating check refuses it by name

## CHECKS
- test_every_refusal_in_the_engine_is_none · covers: M1, M4, R:TWOSHAPES, A5, A6, E6 · the static enumeration over every verb, naming the function, line and value, and the question that decides it
- test_an_honest_no_keeps_its_boolean · covers: M2, M3, R:LOSTANSWER, A2, A3, E1, E2 · `fresh` answers stale with `False` and unmeasurable with `None`, and `render_card` still answers `False` when the card is current
- test_no_caller_is_blind_to_the_change · covers: M6, R:SILENTCALLER, A1, A4, E3, E4 · every in-repo assertion on a refusal path tests identity; the ones on result paths are shown to still test truthiness deliberately
- test_the_messages_are_untouched · covers: M5 · every refusal message is byte-identical to the committed version — only the first element moved
- test_the_exit_code_is_unchanged · covers: E5 · `cli.py` returns the same exit code for every converted verb, driven through argv
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
