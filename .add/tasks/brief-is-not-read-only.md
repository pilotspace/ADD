---
type: Task
title: what brief writes is stated where it is read, and pinned by a check
status: direction
depth: standard
milestone: read-cost
scope:
  - add-method/tooling/add.py
  - add-method/tooling/engine_pin.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - .add/tooling/add.py
  - add-method/.add/tooling/add.py
  - add-method/tests/engine

gives:
  - S1 add.brief(...)'s docstring — it names the FUNCTION that is pure, not the verb that is not
  - S2 the purity boundary itself, pinned by checks on both sides: the function writes nothing, and the verb writes one stamp only on a frozen Task
generated: { by: add/3.4.0, at: 2026-09-04 }
verified:
  - { by: "plan:read-cost", at: 2026-09-04, act: freeze, authority: plan, direction: "sha256:f0ce93f6ddc57ca0", binding: "sha256:e9a79d98e3503d91" }
  - { by: "cli", at: 2026-09-04, act: brief, authority: process, brief: "sha256:6d25767c75dfde61" }
---
## CARD
goal: the line that says `brief` is read-only says which `brief` it means, and a check holds the boundary it describes.
why: a review agent declared `brief` read-only, ran it in an audit, and then found `cli.py` calls `brief_stamp` on any frozen Task. The finding is real but narrower than reported, and the narrowing matters: `add.brief()` the function IS pure, `brief_stamp` is the write, and `docs/13-command-reference.md` already documents the stamp accurately. What is wrong is one docstring sentence saying "`brief` is read-only" without saying which `brief` — read as the verb, it is false, and a reviewer read it that way. And nothing pins the boundary: no check asserts the function writes nothing, or that the verb writes exactly one stamp and only where it should.
beat: direction · next: add freeze brief-is-not-read-only

## RULES
<must>
- M1 the docstring names the FUNCTION as the pure one, so the sentence cannot be read as a claim about the verb
- M2 a check asserts `add.brief()` leaves the bundle byte-identical
- M3 a check asserts the CLI path records exactly one `act: brief` stamp on a frozen Task
- M4 a check asserts it records none on an unfrozen node
- M5 no behaviour changes — this states and pins what the code already does
</must>
<reject>
- R:NEWWRITE this task must not add, move or remove a write; it describes and pins one -> "NEWWRITE"
- R:BYNAME the purity check must compare bundle CONTENT, not merely count stamps, so a write elsewhere is caught too -> "BYNAME"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 S2 · n/a · a docstring and three checks over an existing boundary; no authority, no floor, no new write
- A2 [which] covers: S1 · the request does not say which text is wrong; taking ONLY the sentence that says "`brief` is read-only" — the command reference already documents the stamp, so a sweep would rewrite text that is already true · found: the reference row names the `act: brief` stamp and what reads it -> if wrong, correct documentation is rewritten as though it were the defect
- A3 [which] covers: S2 · the request does not say which surface is pinned; taking BOTH sides of the boundary, because a check on one side alone is satisfied by moving the write across it -> if wrong, the write migrates and the pin still passes
- A4 [when] covers: S1 S2 · the request does not say when the stamp is written; taking the existing condition unchanged — a frozen Task, which is what `gate`'s R:UNBRIEFED reads -> if wrong, a documentation task changes when a gate can pass
- A5 [absent] covers: S2 · the request does not say what an absent stamp means; taking the existing reading — no entry means the brief never entered the build -> if wrong, absence acquires a second meaning
- A6 [absent] covers: S1 · the request does not say what is unstated; taking the docstring's silence about the CLI wrapper as the defect itself, so the sentence says what it excludes rather than leaving it inferred -> if wrong, the sentence stays true only to a reader who already knew
- A7 [order] covers: S2 · the request does not say what order the compile and the stamp happen in; taking print-then-stamp, unchanged, so a failed stamp cannot suppress the prompt a reader needs -> if wrong, an ordering change hides output behind a write
- A8 [order] covers: S1 · the request does not say where the qualification sits; taking it in the same sentence, because a caveat a paragraph away is one a reader skips -> if wrong, the correction is present and unread
- A9 [experience] covers: S1 · the receiver is someone deciding whether it is safe to run this verb while auditing; what would make it hard is a sentence saying read-only about a verb that writes — which already happened -> if wrong, the next audit mutates a bundle it meant to observe
- A10 [experience] covers: S2 · the receiver is the next author moving code across this boundary; taking checks on both sides so the move is caught rather than discovered -> if wrong, the boundary is documented and unenforced

## PLAN
contract: the docstring sentence names `brief()` explicitly and says the CLI wrapper stamps. Checks pin the boundary: the function leaves the bundle byte-identical; the CLI path stamps once on a frozen Task and not at all on an unfrozen one.
strategy: write the byte-identical check first — it is the one that would have told the reviewer the truth in a single command.

## EDGES
- E1 `add.brief()` on a frozen Task leaves every file byte-identical
- E2 the CLI path on a frozen Task adds exactly one `act: brief` stamp
- E3 the CLI path on an unfrozen node adds none
- E4 each compile records its OWN entry — I assumed re-running would be idempotent and it is not; the gate asks whether ANY entry sits after the last (re)freeze, so a per-compile trail is the right record and M5 forbids changing it

## CHECKS
- test_the_compile_writes_nothing · covers: M2, R:BYNAME, E1 · every file's bytes before and after `add.brief()` are identical
- test_the_verb_records_one_entry · covers: M3, E2 · the stamping path adds exactly one `act: brief`
- test_an_unfrozen_node_records_none · covers: M4, E3, A4 · no stamp before the seal
- test_each_compile_records_its_own_entry · covers: E4, M5 · re-running adds a second entry, and the gate still reads the node as briefed
- test_the_docstring_names_the_function · covers: M1, A2, A6, A8, A9 · the sentence says which `brief` is pure and that the CLI wrapper stamps
- test_no_write_moved · covers: M5, R:NEWWRITE, A3 · `brief` contains no transition call and `brief_stamp` still does
red-first: every check MUST fail first.

## EVIDENCE
receipt: runs/n.md
gate: PASS | RISK-ACCEPTED | HARD-STOP

## LESSONS
- a lesson -> add learn lens
