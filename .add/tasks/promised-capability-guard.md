---
type: Task
title: A front-door promise must name what makes it true
status: done
depth: standard
milestone: experience-in-plan
scope:
  - README.md
  - add-method/README.md
  - add-method/tests/skill/test_promised_capabilities.py
gives:
  - S1 the Highlights list of the root README — the promises a reader meets while deciding
  - S2 the Highlights list of the package README, which a reader meets on the registry page instead
  - S3 the registry that binds each promise to the shipped artifact making it true
generated: { by: add/3.1.0, at: 2026-08-12 }
verified:
  - { by: "Tin Dang", at: 2026-08-12, act: freeze, authority: human, direction: "sha256:3c7ef81c90649e12" }
  - { by: "cli", at: 2026-08-12, act: brief, authority: process, brief: "sha256:6af7baeb022ff400" }
  - { by: "process:run", at: 2026-08-12, act: run, authority: process, outcome: PASS, receipt: /tasks/promised-capability-guard.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-08-12, act: gate, authority: process, outcome: PASS, receipt: /tasks/promised-capability-guard.d/runs/1.md, brief: "sha256:6af7baeb022ff400" }
---
## CARD
goal: every bullet the front door promises names a shipped artifact that makes it true, and a bullet that cannot name one is retired rather than left standing
why: both READMEs still promise "a wireframe and a zero-dependency HTML mock, approved before any build". The skill tree contains no mention of either — it was a 1.7-era UI step that 3.0 removed, and nothing noticed, because a promise nobody checks rots silently while a test nobody can weaken does not. The milestone before this one found seven false front-door claims and built guards for all of them, and this one still got through: those guards check nouns the engine EXPOSES — bundle files, verb counts, profiles, runnable commands — and never capabilities the prose PROMISES. Two more turned up while looking: a "built-in reasoning floor" whose three named behaviours appear nowhere in the shipped surface, and a bullet that is fine but was never tied to anything.
beat: done · next: add status

## RULES
<must>
- M1 no front-door bullet promises a capability the shipped surface does not carry — the wireframe-and-mock promise and the unbacked reasoning-floor behaviours are gone from both READMEs
- M2 every surviving bullet is registered against a shipped artifact that makes it true — a verb the CLI registers, an engine value, or a file in the skill tree — and the guard proves that artifact exists
- M3 a bullet with no registered anchor fails the guard BY NAME, so a new promise cannot join the list silently
- M4 the identity strings and every measured claim are untouched, and no bullet is deleted whose promise the shipped surface actually keeps
</must>
<reject>
- R:LOOSE an anchor must not be satisfied by the bullet's own words appearing somewhere in the corpus — the promise proving itself is the failure mode being closed -> "loose"
- R:CULL the guard must not be satisfied by deleting a bullet that is true; a promise the product keeps belongs on the front door -> "cull"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2, S3 · it does not say who may add a bullet later; taking it as anyone editing either README, with no reviewer assumed and no privileged path — which is why the refusal has to name the offending bullet rather than merely fail -> if wrong, the guard protects only the bullets present today and the next marketing pass reopens the hole
- A2 [which] covers: S1, S2, S3 · it does not say which prose counts as a promise; taking it as the Highlights bullets only, not the tagline, the comparison table or the benchmark prose, because a bullet is a capability claim in a fixed list while the surrounding prose is argument -> if wrong, the guard either misses a promise made outside the list or demands an anchor for a sentence that is making a case rather than a claim
- A3 [when] covers: S1, S2, S3 · it does not say when the anchor must hold; taking it as every test run against the working tree, so a capability removed from the skill breaks the front door's checks in the same commit that removes it -> if wrong, the promise and the removal diverge exactly as the wireframe step did, and the gap is found by a reader instead
- A4 [absent] covers: S1, S2, S3 · it does not say what to do with a bullet that is TRUE but has no crisp artifact to point at; taking it as: the anchor may be any of the three kinds, and if none of them fits, the honest move is to reword the bullet to what the product does carry rather than register a vague anchor -> if wrong, an anchor gets stretched until it means nothing, and the guard becomes a ritual that passes
- A5 [order] covers: S1, S2, S3 · it does not say whether the two lists must agree or stay in the same order; taking them as independent — the package README is shorter by design and drops bullets the registry page has no room for — so the registry is keyed per file -> if wrong, one file is edited to match the other and loses a claim its own readers wanted
- A6 [experience] covers: S1, S2, S3 · it does not say who the refusal is FOR; taking it as whoever is editing the front door months from now with no knowledge of this task, so the failure has to name the bullet, say which anchor kinds exist, and say that retiring an unbackable promise is the intended outcome rather than a workaround -> if wrong, the next author reads a failing check as an obstacle and satisfies it with a vague anchor, which is worse than no check because it now reads as verified

## PLAN
contract: the wireframe-and-mock bullet is retired from both READMEs, and the reasoning-floor bullet is reduced to the part the shipped surface keeps. Every remaining bullet is registered against one shipped artifact by kind — a verb the CLI registers, an engine value, or a skill-tree file — and the guard resolves each anchor against the real tree. A bullet with no registry entry fails by name, with the anchor kinds and the retire-it option in the message. Identity strings and benchmark prose are asserted unchanged, and each retirement is paired with the claim that must survive it.
scope: README.md, add-method/README.md, add-method/tests/skill/test_promised_capabilities.py

## EDGES
- E1 the two lists differ in length and wording, and share most bullets. A registry keyed only by bullet text would silently accept a bullet present in one file and missing from the other, so the registry is keyed per file and every bullet in each file must resolve.

## CHECKS
- test_every_highlight_names_a_shipped_artifact · covers: M2, M3, E1, R:LOOSE · every bullet in each Highlights list has a registry entry, and every entry resolves to a verb, an engine value or a file that exists
- test_unregistered_bullet_fails_by_name · covers: M3, A6 · a bullet with no entry is reported by its own text with the anchor kinds and the retire option named
- test_retired_promises_are_gone · covers: M1 · neither README still promises a wireframe, an HTML mock, or the reasoning-floor behaviours the shipped surface does not carry
- test_retirement_did_not_cull_a_true_claim · covers: M4, R:CULL · the identity strings, the benchmark prose and the surviving bullet count are what the contract says they are
red-first: 2 of 4 are red at freeze — the by-name refusal, which reports three unbackable bullets across the two lists, and the retirement check, which reports all five surviving phrases. The anchor-resolution check is GREEN at freeze and that is a property of it, not a gap: every anchor authored into the registry resolves today, which is what registering one means. It turns red the moment a capability leaves the shipped surface, which is the failure it exists to catch and the one nothing caught before. The fourth is GREEN by design and armed through the build: it fails if the build reaches green by deleting bullets rather than retiring the unbackable ones, which is what R:CULL names.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
