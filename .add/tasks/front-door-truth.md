---
type: Task
title: The README says what the engine does
status: done
depth: standard
milestone: adoption-beyond-code
scope:
  - README.md
  - add-method/README.md
  - add-method/tests/skill/
gives:
  - S1 README.md — the repository front door, the first surface any adopter reads
  - S2 add-method/README.md — the package front door, what npm and PyPI render
generated: { by: add/3.1.0, at: 2026-08-12 }
verified:
  - { by: "Tin Dang", at: 2026-08-12, act: freeze, authority: human, direction: "sha256:e8d5c6f6a2a95f9a" }
  - { by: "Tin Dang", at: 2026-08-12, act: refreeze, authority: human, direction: "sha256:0c91397293e3d172" }
  - { by: "Tin Dang", at: 2026-08-12, act: refreeze, authority: human, direction: "sha256:7df4c8e9d4d30d0c" }
  - { by: "process:run", at: 2026-08-12, act: run, authority: process, outcome: PASS, receipt: /tasks/front-door-truth.d/runs/1.md }
  - { by: "cli", at: 2026-08-12, act: brief, authority: process, brief: "sha256:dc9a66bfd462cfc0" }
  - { by: "process:run", at: 2026-08-12, act: run, authority: process, outcome: PASS, receipt: /tasks/front-door-truth.d/runs/2.md }
  - { by: "Tin Dang", at: 2026-08-12, act: gate, authority: process, outcome: PASS, receipt: /tasks/front-door-truth.d/runs/2.md, brief: "sha256:dc9a66bfd462cfc0" }
  - { by: loop, at: 2026-08-12, act: reopen, to: build, reason: "the gate passed over a claim I introduced in the same commit: the root README now shows `npx @pilotspace/add init --profile doc`, and the npm installer does not accept --profile at all — it warns 'ignoring unknown flag' and reads 'doc' as a target directory. M5's check only executes <engine>.py <verb> forms, so an npx form was never run. Disproven by A1 of profile-refusal." }
  - { by: "Tin Dang", at: 2026-08-12, act: refreeze, authority: human, direction: "sha256:a94c097b03eb0ad8" }
  - { by: "cli", at: 2026-08-12, act: brief, authority: process, brief: "sha256:71b0d994bcd5d6e3" }
  - { by: "process:run", at: 2026-08-12, act: run, authority: process, outcome: PASS, receipt: /tasks/front-door-truth.d/runs/3.md }
  - { by: "Tin Dang", at: 2026-08-12, act: gate, authority: process, outcome: PASS, receipt: /tasks/front-door-truth.d/runs/3.md, brief: "sha256:71b0d994bcd5d6e3" }
advised_by: method-steward
---
## CARD
goal: no claim on either README survives that the engine contradicts — and a guard that derives its expectation from the engine keeps it that way
why: four claims are false today, and every one of them is load-bearing for a first-time reader. `.add/state.json` appears 4× across both files while `add.py:974` calls `state.json` the marker of a **2.x** bundle ("3.0 has no state file") — so the one command a reader is told resumes their work names a file `init` never creates. The verb count is stated three times as two different numbers (31 · 31 · 21) and the CLI registers 22, so the package README contradicts itself on its own install page — and a hand count off the `--help` output got this wrong once during drafting, which is the argument for deriving it. `PLAN.md` is described 6× as the one file per feature; a fresh bundle has no `PLAN.md` and a task lives at `tasks/<slug>.md`. And `--profile doc` — the only non-code affordance already shipping — is named on neither. This is the same defect `all-domain-evidence` found five times inside the skill, now at the loudest surface ADD has: nothing checks shipped prose against the engine.
beat: done · next: add status

## RULES
<must>
- M1 no README names a path under `.add/` that the engine never creates — the baseline is a bundle that has been USED (init, then a first task), not one that has only been initialised
- M2 every verb count stated in a README equals the number of verbs the CLI ships, and the two READMEs never state different numbers for the same thing
- M3 every profile the engine ships is named where a reader chooses one, and no README names a profile the engine does not ship
- M4 each guard reads its expectation out of the engine at test time, so the next verb or profile that lands moves the expectation with it
- M5 every engine command a README shows a reader is one that actually answers when run
</must>
<reject>
- R:PINNED a guard must never compare against a literal copied from today's engine, which would rot exactly as the prose did -> "pinned"
- R:VACUOUS a guard must never pass because it extracted nothing to compare -> "vacuous"
- R:IMAGEWASH a false claim rendered inside a shipped image must never be treated as repaired by editing the prose around it -> "imagewash"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2 · the request does not say whether the book under `docs/` and the benchmark reports are also "shipped prose" bound by this rule; taking it as the two READMEs only, because those are what npm, PyPI and the repo landing page render unasked -> if wrong, a reader following a book link hits the same dead `state.json` and the fix looks half-done
- A2 [which] covers: S1, S2 · it does not say whether a mention of `state.json` while *explaining the 2.x break* is a violation; taking it as allowed when the sentence names it as 2.x, since `upgrade` genuinely needs to describe what it detects -> if wrong, the guard forbids the one honest use and the docs cannot explain migration
- A3 [when] covers: S1, S2 · it does not say whether the count must match at commit time or at release time; taking it as every test run, because a number that is only true at release is false for everyone reading main -> if wrong, the guard fails a legitimate mid-milestone state where a verb has landed and prose has not
- A4 [absent] covers: S1, S2 · it does not say what a README that states NO verb count should do; taking silence as compliant — the rule forbids a wrong number, it does not compel a number -> if wrong, a README quietly drops the claim to pass and the reader loses a real fact
- A5 [order] n/a · neither README publishes an ordered collection; the claims are independent statements, and no check depends on their sequence

## PLAN
contract: both READMEs state only what `add.py` and `cli.py` can be read to confirm — bundle files, verb count, and profile names. Every guard derives: bundle files by running a real `init` into a temp root and listing what appears, verbs by introspecting the CLI's registered subparsers, profiles by reading `add.PROFILES`. The image residual is recorded in the task, not painted over.
scope: README.md, add-method/README.md, add-method/tests/skill/

## EDGES
- E1 three shipped PNGs render the false claims inside the artwork — `add-install.png` draws `.add/state.json`, `add-task-growth-wheel.png` and `add-milestone-task-lifecycle.png` draw `PLAN.md` and the retired `§0…§7` numbering. No text edit reaches a rasterised word, so the alt text must not restate the false claim and the residual must be reported as open, never closed silently.

## CHECKS
- test_readmes_name_no_absent_bundle_file · covers: M1 · drives a real bundle in a temp root — `init`, then `new Task` — and fails on any `.add/<name>` a README cites that the used bundle still lacks. WIDENED after the first build attempt: the original probe stopped at `init`, which made the corrected prose `.add/tasks/<slug>.md` fail alongside the dead `state.json` it was replacing. `tasks/` is not a dead name, it is a lazily-created one, and a check that cannot tell those apart forces the docs to describe a bundle nobody actually has. Widened by re-freeze rather than edited under the seal, and it still refuses `state.json` and `PLAN.md`.
- test_readme_verb_counts_match_the_cli · covers: M2 · reads every `N-verb`/`N verbs` claim in both files and compares each against the CLI's registered subparser count
- test_readmes_do_not_contradict_each_other · covers: M2 · the set of verb counts stated across both files must have exactly one member
- test_readmes_name_every_shipped_profile · covers: M3 · both directions against `add.PROFILES` — no profile unnamed, no profile named that does not ship
- test_expectations_are_derived_not_pinned · covers: M4, R:PINNED · feeds the extractors a fabricated engine and asserts the fabricated verb and profile come back, proving no literal list
- test_extractors_fail_loud_on_empty · covers: R:VACUOUS · an extraction that finds nothing raises rather than reporting agreement with nothing
- test_alt_text_does_not_restate_stale_image_claims · covers: E1, R:IMAGEWASH · the alt text of each stale PNG must not itself assert `state.json` or per-feature `PLAN.md`
- test_shown_installer_flags_are_accepted · covers: M5 · hands every installer-form command in either README to the installer's OWN parser and fails on its own `ignoring unknown flag` / `was retired` diagnostic. ADDED after this task's first gate passed over a claim the same commit introduced: `npx @pilotspace/add init --profile doc`. The installer takes no `--profile` — its "profile" is agent detection — so it ignores the flag and reads `doc` as the target directory, the precise failure its own source cites as the reason `--stage` had to be rejected explicitly. The rule was right and the check was narrower than the rule; this closes the class rather than the instance.
- test_shown_commands_actually_answer · covers: M5 · executes every `<engine>.py <verb>` invocation the READMEs show, in a real bundle, and fails any that returns no output — `add.py` is a library and answers nothing, which the package README itself states while the root README instructs readers to run it three times
red-first: 5 of 7 are red at freeze — the four false claims plus the alt text. `test_expectations_are_derived_not_pinned` and `test_extractors_fail_loud_on_empty` are GREEN at freeze and cannot honestly be red: their subject is the extractor authored in this same beat, not the READMEs, so they guard a future regression in my own instrument rather than a present defect. Recorded here so the record does not imply a red they never had.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
