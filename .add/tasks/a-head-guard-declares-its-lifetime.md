---
type: Task
title: a guard reading a git ref says whether it is durable or a tripwire
status: done
depth: standard
kind: test
milestone: checks-that-hold-in-ci
scope:
  - add-method/tests/engine/test_scope_guard_ranges.py
  - add-method/tests/test_installer_reach_parity.py
  - add-method/tests/test_front_door_claim_truth.py
  - add-method/tests/skill/test_front_door_copy.py
  - add-method/tests/skill/test_positioning.py
  - add-method/tests/skill/test_promised_capabilities.py
  - add-method/tests/skill/test_dimension_vocabulary_truth.py
  - add-method/tests/skill/test_persona_load_by_fit.py
gives:
  - S1 the shape guard in `test_scope_guard_ranges.py` — which git invocations it enumerates, which refs it admits, and what it demands a working-tree-vs-HEAD guard say about its own lifetime
generated: { by: add/3.6.0, at: 2026-09-10 }
verified:
  - { by: "plan:checks-that-hold-in-ci", at: 2026-09-10, act: freeze, authority: plan, direction: "sha256:7b9ed6254479f15b", binding: "sha256:a046adc15422753b" }
  - { by: "cli", at: 2026-09-10, act: brief, authority: process, brief: "sha256:d7a1ad4a281c3cd8" }
  - { by: "process:run", at: 2026-09-10, act: run, authority: process, outcome: PASS, receipt: /tasks/a-head-guard-declares-its-lifetime.d/runs/1.md }
  - { by: "plan:checks-that-hold-in-ci", at: 2026-09-10, act: gate, authority: process, outcome: PASS, receipt: /tasks/a-head-guard-declares-its-lifetime.d/runs/1.md, brief: "sha256:e9516e85cd1ea070" }
advised_by: engine-notary
---
## CARD
goal: every guard in the suite that resolves a git ref is enumerated, reads only a ref a fresh shallow checkout actually has, and says in its own source whether it is a durable invariant or a live-editing tripwire
why: the repo bound `a scope guard names the commit range it guards` (Q28) and built a shape guard to enforce it — over `git diff` ONLY. Seven more call sites resolve a git ref through `git show HEAD:` and one through `git merge-base`, and every one of them is satisfied by `git commit`. The `merge-base` one took CI red on a ref a depth-1 clone does not have. A rule enforced over one spelling of a shape is a rule the other spellings do not have
beat: done · next: add status

## RULES
<must>
- M1 the shape guard enumerates `git show` and `git merge-base` alongside `git diff` — one rule over every spelling of the shape, not over the one that happened to be found first
- M2 a guard may resolve only a ref a fresh shallow checkout HAS: `HEAD`, or a range whose ends it names. `origin/<branch>` is refused, because `actions/checkout` does not fetch it and the guard then reads `cannot establish` as `false`
- M3 every function that compares the working tree to `HEAD` says so in its own source — that it fires while the edit is being made and is INERT once committed — so a green CI is never read as the claim having held
- M4 no claim is weakened: every existing guard keeps asserting exactly what it asserted, and the retired-guard record rung is untouched
</must>
<reject>
- R:ABSENTREF a guard resolves a ref a fresh shallow checkout does not have -> "ABSENTREF"
- R:SILENTTRIPWIRE a guard satisfied by `git commit` presents as a durable invariant, so CI green is mistaken for the claim holding -> "SILENTTRIPWIRE"
- R:CLAIMDROP a guard is retired or softened to satisfy this task rather than annotated -> "CLAIMDROP"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · the request does not say who writes the lifetime note; taking "whoever writes the guard, at the moment they choose HEAD as the baseline — that is when they know which of the two they meant" -> the notes are added in bulk later by someone guessing intent from the assertion
- A2 [which] covers: S1 · the request does not say which git invocations count; taking "`show`, `diff` and `merge-base` — the three the suite actually uses to resolve a ref. `ls-files`, `rev-parse` and `status` read the INDEX, not a revision, and nothing about them expires" · probe: the enumeration finds the eight known call sites and no more -> the guard flags every git call in the suite and gets waved past
- A3 [when] covers: S1 · the request does not say when a tripwire is acceptable at all; taking "always, when labelled — it fires during the edit, which is when it can help. The defect is not the tripwire, it is believing a green CI means it held" -> seven working guards are deleted to fix a CI story, and the live protection goes with them
- A4 [absent] covers: S1 · the request does not say what a checkout with NO git means; taking "not this task's question — every guard here reads `HEAD`, which exists wherever git does, and the one ref that could be missing is the one M2 refuses" · probe: the suite passes in a shallow clone -> a second unavailability mode is discovered on CI later, exactly as this one was
- A5 [order] covers: S1 · the request does not say whether the ref rung runs before the lifetime rung; taking "independent — a guard can fail both, and reporting only the first would hide the second behind a fix" -> an author fixes the ref, re-runs, and is then told about the label
- A6 [experience] covers: S1 · the request does not say what the label looks like; taking "the word TRIPWIRE in the function's own source, followed by a sentence — greppable, and it reads as a warning to the next person in the file rather than as satisfying a checker" -> the label becomes a token pasted to clear a check and says nothing to a reader
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: `_git_ref_calls()` replaces `_git_diff_calls()` and yields every `git show|diff|merge-base` site with its enclosing function; two new rungs read it — one for the ref, one for the lifetime label.
strategy: widen the enumerator first and let it report all eight sites red, then annotate the seven tripwires, and keep every existing assertion byte-identical.

## EDGES
- E1 <a boundary or failure case a check must cover — optional>

## CHECKS
- test_no_guard_reads_a_ref_a_fresh_checkout_lacks · covers: M2, R:ABSENTREF, A2, A4, A5 · a guard resolving `origin/<branch>` is named, and the eight known sites are all found
- test_a_worktree_guard_declares_it_is_a_tripwire · covers: M1, M3, R:SILENTTRIPWIRE, A1, A6 · every function comparing the working tree to HEAD carries the label in its own source
- test_the_widening_dropped_no_claim · covers: M4, R:CLAIMDROP, A3 · each annotated guard still holds the assertion it held
red-first: every check MUST fail first.

## EVIDENCE
receipt: /tasks/a-head-guard-declares-its-lifetime.d/runs/1.md · kind: test-ids · 6/6 reported · exit 0 · 2026-09-10
gate: PASS · authority process · by plan:checks-that-hold-in-ci · receipt /tasks/a-head-guard-declares-its-lifetime.d/runs/1.md · 2026-09-10

## LESSONS
- [method · M48 · folded] A guard comparing the working tree to HEAD is a live-editing TRIPWIRE, not an invariant: it fires while the edit is made and is inert once committed. That is a legitimate lifetime — the defect is leaving it unlabelled, so a green CI reads as the claim having held. (evidence: /tasks/a-head-guard-declares-its-lifetime.md)
- [system · S14 · folded] A rule enforced over one spelling of a shape is a rule the other spellings do not have. The scope guard enumerated `git diff` because that is what the two retired guards used; seven more sites read a ref through `git show` and one through `merge-base`, all satisfied by `git commit`. (evidence: /tasks/a-head-guard-declares-its-lifetime.md)
