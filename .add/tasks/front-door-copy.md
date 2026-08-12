---
type: Task
title: The framing stops presupposing a repo
status: done
depth: quick
scope:
  - README.md
  - add-method/README.md
  - add-method/tests/skill/
gives:
  - S1 the framing sentences of both READMEs — the problem statement, the prerequisite line, and the what-ADD-is paragraph
generated: { by: add/3.1.0, at: 2026-08-12 }
verified:
  - { by: "Tin Dang", at: 2026-08-12, act: freeze, authority: human, direction: "sha256:80f3e1fc90e9146c" }
  - { by: "cli", at: 2026-08-12, act: brief, authority: process, brief: "sha256:4ba95115041e1288" }
  - { by: "process:run", at: 2026-08-12, act: run, authority: process, outcome: PASS, receipt: /tasks/front-door-copy.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-08-12, act: gate, authority: process, outcome: PASS, receipt: /tasks/front-door-copy.d/runs/1.md, brief: "sha256:4ba95115041e1288" }
---
## CARD
goal: the sentences that tell a non-code reader "this is not for you" stop saying it, without the title, the tagline or a single measured claim moving
why: `adoption-beyond-code` fixed what was FALSE at the front door and made the non-code walkthrough reachable. What is left is not false — it is narrow. The problem statement is "AI coding doesn't fail on day one", the prerequisite is "a CLI **coding** agent", and the package's one-line summary is "for building software when the AI writes the code". A reconciliation lead who got as far as the walkthrough link has already been told three times that this is a tool for people who write code. This is the cheap, reversible half of the positioning question — and after measuring the rename it is the ONLY half with evidence behind it: the barriers this milestone actually found were defects and omissions, never the name.
beat: done · next: add status

## RULES
<must>
- M1 the phrases that narrow ADD to software — named individually — are gone from both READMEs
- M2 the project's identity is untouched: name, tagline, package names and book title byte-identical
- M3 every measured or benchmark claim keeps its code framing, because that is what was actually measured
</must>
<reject>
- R:NEUTERED the edit must not remove a claim rather than widen it — a sentence deleted to satisfy a checker costs the reader a real fact -> "neutered"
- R:REGRESS a phrase retired here must not come back later -> "regress"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · it does not say whether developers remain the PRIMARY audience; taking it as yes — they are who ADD was built for and who the benchmark measured — so this widens the framing rather than re-centring it on anyone else -> if wrong, the front door reads as generic to the audience that actually adopts it, which is a worse trade than the one being fixed
- A2 [which] covers: S1 · it does not say whether "code-shaped" includes claims about the BENCHMARK; taking it as excluded, because the benchmark ran a six-milestone software project and describing it in any other terms would be a false generalisation of real evidence -> if wrong, the copy is inconsistent, which is far cheaper than overstating what was measured
- A3 [when] covers: S1 · it does not say whether this is checked once or continuously; taking it as every test run, matching the rule already in force for these two files -> if wrong, the phrases drift back the next time someone edits the pitch
- A4 [absent] covers: S1 · it does not say what to do about `the code is disposable`, which is a PRINCIPLE heading rather than a description of the audience; taking it as in scope but widened rather than cut, since the principle is true of any artifact and the heading is load-bearing prose -> if wrong, a well-known line changes for a reader who valued it
- A5 [order] n/a · the framing sentences are independent claims in different sections; no check depends on the order they appear

## PLAN
contract: five narrowing phrases are widened in place across the two READMEs. The title, tagline, package names, book title and every benchmark sentence are untouched. A guard pins the retired phrases as a denylist — the one place a literal is correct, because the rule is "do not bring these back" — and asserts the widened sentence still carries its claim rather than having been deleted.
scope: README.md, add-method/README.md, add-method/tests/skill/

## EDGES
- E1 the identity strings and the retired phrases overlap in the same paragraphs. A guard that only forbids the old phrases would be satisfied by deleting whole sentences, so each retirement is paired with an assertion that the surrounding claim survived.

## CHECKS
- test_narrowing_phrases_are_gone · covers: M1, R:REGRESS · none of the five named phrases appears in either README
- test_widened_claims_survived · covers: R:NEUTERED, E1 · each retired phrase's paragraph still carries its claim — the sentence was widened, not deleted
- test_benchmark_claims_keep_their_code_framing · covers: M3, A2 · the measured-result sentences still describe a software project
- test_identity_untouched_by_copy_pass · covers: M2 · name, tagline and package names still present and unchanged against git HEAD
red-first: 1 of 4 is red at freeze, on all five phrases at once. The other 3 are GREEN by design and stay armed THROUGH the build — they guard what the edit must not destroy (the claims inside the widened sentences, the benchmark's code framing, the identity strings). Their job is to fail if the build takes the cheap route of deleting rather than widening, which is exactly the failure mode R:NEUTERED names.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
