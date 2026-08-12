---
type: Task
title: A sixth sweep dimension: who receives this, and what would make it hard
status: done
depth: standard
sensitivity: architecture
milestone: experience-in-plan
scope:
  - add-method/tooling/add.py
  - add-method/src/add_method/_bundled/tooling/add.py
  - add-method/skill/add/SKILL.md
  - add-method/skill/add/phases/direction.md
  - add-method/src/add_method/_bundled/skill/add/SKILL.md
  - add-method/src/add_method/_bundled/skill/add/phases/direction.md
  - .claude/skills/add/SKILL.md
  - .claude/skills/add/phases/direction.md
  - add-method/FORMAT.md
  - add-method/GETTING-STARTED.md
  - add-method/docs/03-direction.md
  - add-method/docs/12-bundle-format.md
  - add-method/tests/engine/conftest.py
  - add-method/tests/engine/test_experience_dimension.py
  - add-method/tests/skill/test_dimension_vocabulary_truth.py
gives:
  - S1 the `[experience]` member of the closed sweep vocabulary — what freeze refuses when a surface is unswept on it
  - S2 the scaffold assumption line the `new` verb writes for that dimension
  - S3 the living prose that enumerates the dimension vocabulary to a reader
generated: { by: add/3.1.0, at: 2026-08-12 }
verified:
  - { by: "Tin Dang", at: 2026-08-12, act: freeze, authority: human, direction: "sha256:a1b1b6170e878d75" }
  - { by: "cli", at: 2026-08-12, act: brief, authority: process, brief: "sha256:8f17bfd560517dcf" }
  - { by: "process:run", at: 2026-08-12, act: run, authority: process, outcome: PASS, receipt: /tasks/experience-sweep.d/runs/1.md }
  - { by: "process:run", at: 2026-08-12, act: run, authority: process, outcome: PASS, receipt: /tasks/experience-sweep.d/runs/2.md }
  - { by: "Tin Dang", at: 2026-08-12, act: gate, authority: plan, outcome: PASS, receipt: /tasks/experience-sweep.d/runs/2.md, brief: "sha256:8f17bfd560517dcf" }
  - { by: loop, at: 2026-08-12, act: reopen, to: verify, reason: "the PASS recorded freshness n/a because scope: was authored in ## PLAN but never in frontmatter, where the engine reads it — the receipt was never bound to the files the build changed" }
  - { by: "process:run", at: 2026-08-12, act: run, authority: process, outcome: PASS, receipt: /tasks/experience-sweep.d/runs/3.md }
  - { by: "Tin Dang", at: 2026-08-12, act: gate, authority: plan, outcome: PASS, receipt: /tasks/experience-sweep.d/runs/3.md, brief: "sha256:0328dfc0e2e00c56" }
  - { by: loop, at: 2026-08-12, act: reopen, to: verify, reason: "the dated-record check pins CHANGELOG.md byte-identical to HEAD, which would refuse the release entry this very milestone has to write — classification (excluded from must-agree) and the unchanged-pin are two different jobs and were conflated" }
  - { by: "process:run", at: 2026-08-12, act: run, authority: process, outcome: PASS, receipt: /tasks/experience-sweep.d/runs/4.md }
  - { by: "Tin Dang", at: 2026-08-12, act: gate, authority: plan, outcome: PASS, receipt: /tasks/experience-sweep.d/runs/4.md, brief: "sha256:0328dfc0e2e00c56" }
---
## CARD
goal: a standard-depth task cannot freeze until every surface it publishes has been asked who receives it and what would make that output hard for them
why: the `experience` lens ships in both profiles, maps to UDD in the lens table, and gets a spec file in every bundle — but nothing in the loop ever writes it. UDD exists only as a retrospective tag on `add learn`, filed after something already misled someone. Every instrument ADD has is about correctness, so a task can be provably correct and unusable and the loop registers nothing. The sweep is the one mechanism that already refuses, is already domain-neutral, and already sits in the plan, which is where the gap is.
beat: done · next: add status

## RULES
<must>
- M1 `experience` is a member of the closed sweep vocabulary, so freeze refuses a standard-depth task whose published surface is unswept on it, and names the pair it is waiting on
- M2 the scaffold line written for the new dimension frames BOTH halves — who receives this output, and what would make it hard for them — in the not-said register the other five use
- M3 every LIVING surface that enumerates the vocabulary to a reader agrees with the engine's own list, established by derivation from that list rather than by a pinned copy of it
- M4 depth and authority are untouched: `quick` stays exempt from the sweep, and the sensitivity floor is byte-identical — this adds a question, not a gate
</must>
<reject>
- R:PINNED a check must not establish the vocabulary by pinning a literal list of names — a second hand-maintained copy of the list is the very drift this closes -> "pinned"
- R:REWRITE a dated announcement post must not be edited to match — each described the release it announced accurately, and rewriting it would falsify a record to flatter the present -> "rewrite"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2, S3 · the request does not say how the new dimension stays distinct from `who`, which already asks whose data and which caller may act; taking them as disjoint — `who` is authorization, the new one is audience — and saying exactly that in the comment that defines the vocabulary -> if wrong, authors answer the same question twice, and the cheapest way out is to retire the new one as a duplicate, which returns the method to where it is today
- A2 [which] covers: S1, S2, S3 · it does not say which depths or which documents are in scope; taking it as every depth the sweep already runs at — so `quick` stays exempt — and every LIVING doc, with dated announcement posts excluded because each was true of the release it announced -> if wrong, either quick tasks gain ceremony they were promised they would not, or a doc a reader trusts keeps naming five
- A3 [when] covers: S1, S2, S3 · it does not say what becomes of work already frozen under the five-name vocabulary, nor how often the prose must agree; taking the sweep as freeze-time only, so a frozen task is never re-swept and only UNFROZEN work meets the sixth pair, and taking the prose agreement as checked on every test run -> if wrong, an engine upgrade invalidates in-flight tasks in every installed project, which is a far worse fault than the one being fixed
- A4 [absent] covers: S1, S2, S3 · it does not say what an author writes when a surface genuinely has no distinguishable recipient — an internal helper, say; taking the existing retirement form with a stated reason as sufficient, adding no new escape hatch -> if wrong, an author either invents an audience to satisfy a refusal or stalls at it with no honest way through, and an invented answer is worse than no question
- A5 [order] covers: S1, S2, S3 · it does not say where the new dimension sits in the vocabulary or in the scaffold; taking it as last in both — audience is the question you ask once you know what is true — which also leaves the five existing A-numbers where a reader of an older bundle expects them -> if wrong, the numbering shifts under existing readers and buys nothing

## PLAN
contract: one name is appended to the engine's closed sweep vocabulary and one line to the node scaffold, framing both halves in the not-said register. Both engine twins move together. Every living surface that enumerates the vocabulary is updated, and a guard establishes agreement by reading the engine's list and enumerating the living surfaces that must carry it — failing loudly on a surface it has not classified, so a new doc cannot join silently. Dated announcements are named as excluded, with the reason, and pinned unchanged against git HEAD. Depth exemption and the sensitivity floor are asserted unchanged.
scope: add-method/tooling/, add-method/src/add_method/_bundled/tooling/, add-method/skill/, add-method/src/add_method/_bundled/skill/, .claude/skills/add/, add-method/FORMAT.md, add-method/GETTING-STARTED.md, add-method/docs/, add-method/tests/

## EDGES
- E1 the vocabulary is enumerated as a literal in several living files and as the bare word "five" in running prose, where no list appears to match against. A guard that only greps for the new name would pass while a sentence still tells the reader there are five, so the guard must enumerate the living surfaces it covers and fail on one it has not classified.

## CHECKS
- test_experience_joins_the_closed_vocabulary · covers: M1 · the engine's sweep vocabulary carries the new name, and carries it last
- test_freeze_refuses_an_unswept_experience_pair · covers: M1, A3 · a real bundle whose task is swept on the five older dimensions is refused at freeze, the refusal names the unswept pair, and a task frozen before the change is not re-swept
- test_scaffold_frames_both_halves · covers: M2 · the line the scaffold writes for the new dimension names a recipient AND what would make the output hard, in the not-said register
- test_living_prose_agrees_with_the_engine · covers: M3, E1, R:PINNED · every enumerated living surface carries the vocabulary read from the engine, no living surface still tells a reader there are five, and an unclassified doc that enumerates dimensions fails the check by name
- test_dated_announcements_keep_their_release_framing · covers: R:REWRITE · the announcement posts still describe the release they announced, unchanged against git HEAD
- test_depth_exemption_and_authority_floor_unchanged · covers: M4 · a quick-depth task still freezes with no sweep, and the sensitivity floor mapping is unchanged
red-first: 3 of 6 are red at freeze — the vocabulary, the refusal and the scaffold line, all failing because the sixth dimension does not exist yet. The prose check is GREEN today and this is a property of it, not a gap: it derives what it expects from the engine's own list, so while the engine still says five, prose that says five is correct. It turns red on the first engine edit and stays red until the last living surface follows — which is the behaviour wanted from it. The remaining 2 are GREEN by design and stay armed through the build: the quick-depth exemption with the authority floor, and the dated announcements. Their job is to fail if the build widens past its contract, which is what M4 and R:REWRITE name.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
