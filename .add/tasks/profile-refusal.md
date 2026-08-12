---
type: Task
title: init refuses a profile it cannot honour
status: done
depth: standard
sensitivity: architecture
milestone: adoption-beyond-code
scope:
  - add-method/tooling/
  - add-method/src/add_method/_bundled/tooling/
  - add-method/tests/
gives:
  - S1 the `add init --profile` argument — the CLI surface where a reader chooses their lenses
  - S2 the `add.PROFILES` mapping — the engine-data set of lens bundles the engine can honour
generated: { by: add/3.1.0, at: 2026-08-12 }
verified:
  - { by: "Tin Dang", at: 2026-08-12, act: freeze, authority: human, direction: "sha256:b510edc640037d40" }
  - { by: "cli", at: 2026-08-12, act: brief, authority: process, brief: "sha256:d3e6d1080c238062" }
  - { by: "process:run", at: 2026-08-12, act: run, authority: process, outcome: PASS, receipt: /tasks/profile-refusal.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-08-12, act: refreeze, authority: human, direction: "sha256:16acbd495cf5c3fe" }
  - { by: "cli", at: 2026-08-12, act: brief, authority: process, brief: "sha256:f412e79767d84c09" }
  - { by: "process:run", at: 2026-08-12, act: run, authority: process, outcome: PASS, receipt: /tasks/profile-refusal.d/runs/2.md }
  - { by: "Tin Dang", at: 2026-08-12, act: gate, authority: plan, outcome: PASS, receipt: /tasks/profile-refusal.d/runs/2.md, brief: "sha256:f412e79767d84c09" }
advised_by: engine-notary
---
## CARD
goal: `init --profile finance` refuses and names what it does ship, instead of writing code lenses under a name it never understood
why: `add.py:911` reads `lenses = PROFILES.get(profile) or PROFILES["code"]`, so every unrecognised profile silently becomes `code`. A finance lead who follows the obvious guess gets a bundle whose five lenses ask how the product is built and what it forecloses, believes ADD understood their domain, and only finds out at the first spec that it did not — the worst possible moment, because by then they have written into it. `all-domain-evidence` named this "the one true residual, deferred by human constraint, not because it is unreal"; the constraint has since been lifted for this milestone. The same line also carries a comment promising that "the remaining three ship as template files (amendment A1)" — no such template exists anywhere in the tree, so the engine's own source documents three profiles that were never shipped.
beat: done · next: add status

## RULES
<must>
- M1 `init` with a profile the engine does not ship refuses: it exits non-zero, creates no bundle, and its message names every profile that IS shipped
- M2 a refused `init` leaves the directory exactly as it found it — no partial bundle, no half-vendored tooling
- M3 every shipped profile still initialises exactly as before, and an omitted `--profile` still defaults to `code`
- M4 no comment or docstring in the engine promises a profile the engine does not ship
- M5 the two git-tracked engine twins stay byte-identical
</must>
<reject>
- R:SILENTFALLBACK an unrecognised profile must never resolve to `code` lenses without saying so -> "silent_fallback"
- R:NEWFLOOR no sensitivity may raise the authority floor above `process` other than `security · data · architecture`, and no new authority value may appear -> "new_floor"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2 · the request does not say whether the npm and pip installers pass `--profile` through on their own `init`, and so whether they inherit the refusal; taking it as inherited, because both delegate to this same engine entrypoint rather than reimplementing it -> if wrong, the refusal holds only for the vendored CLI and the package installers keep the silent fallback, which is the path most first-time users are actually on
      **DISPROVEN during build, and it cost something.** `bin/cli.js` never accepts `--profile` at all — its own "profile" is the AGENT profile (Claude Code · Cursor · Codex detection), an unrelated concept. `node bin/cli.js init --profile doc` answers `warn: ignoring unknown flag --profile` and then reads `doc` as a TARGET DIRECTORY. The installers drop files and deliberately do not initialise the bundle, so `--profile` is only ever an argument to the vendored `cli.py init` the agent runs. The real cost: `front-door-truth` had already shipped `npx @pilotspace/add init --profile doc` into the root README on the strength of this assumption — the same class of silently-mishandled argument this task exists to remove, reintroduced by me one task earlier. Repaired by reopening that task, not by leaving it for the reader to find.
- A2 [which] covers: S1, S2 · it does not say whether a case difference (`--profile CODE`) is an unknown profile or a shipped one; taking it as unknown, because `PROFILES` keys are lowercase and quietly case-folding would be a second silent coercion of exactly the kind this task removes -> if wrong, a reader is refused for a typo the engine could have understood
- A3 [when] covers: S1, S2 · it does not say whether the refusal applies to a re-`init` over an existing bundle; taking it as checked FIRST, before any existing-bundle handling, since validating the argument cannot depend on what is already on disk -> if wrong, an unknown profile is accepted on a second run and rejected on the first
- A4 [absent] covers: S1, S2 · it does not say what an omitted `--profile` means; taking absence as the `code` default it is today — the rule forbids honouring a WRONG name, not omitting one -> if wrong, every existing scripted `init` with no flag starts failing, which is a breaking change nobody asked for
- A5 [order] n/a · `PROFILES` is a mapping and the refusal is a membership test; no check depends on the order its keys are declared or listed

## PLAN
contract: `add.init` validates `profile` against `PROFILES` before it touches the filesystem and, on a miss, returns the engine's standard refusal shape — `(None, [], "<message> -> \"R:BADPROFILE\"")`. `cli.py` propagates it as a non-zero exit, the same way `new`, `freeze` and `replan` already do. The `or PROFILES["code"]` fallback is removed, and the comment promising three unshipped template profiles is deleted rather than left as an aspiration in the source. No profile is ADDED here: what the walkthrough needs is decided in `beyond-code-walkthrough` from evidence, not guessed now.
scope: add-method/tooling/, add-method/src/add_method/_bundled/tooling/, add-method/tests/

## EDGES
- E1 no path this task declares in `scope:` may be gitignored — freshness digests a git blob, so a gitignored scope entry cannot be attested. The vendored `.add/tooling/` copy is both gitignored AND the engine this milestone is driven by, so it stays out of scope and is re-vendored as an operational step after the gate.
- E2 `--profile` omitted entirely must still produce a `code` bundle and must never hit the refusal — the rule binds a wrong name, not a missing one.

## CHECKS
- test_unknown_profile_refuses · covers: M1, R:SILENTFALLBACK · `init --profile finance` exits non-zero and its message contains every key of `add.PROFILES`
- test_refused_init_leaves_nothing_behind · covers: M2 · after a refused `init` the target directory holds no `.add/` at all
- test_shipped_profiles_still_initialise · covers: M3 · every key of `add.PROFILES`, driven from the engine rather than listed, initialises a bundle whose specs match that profile's lenses
- test_omitted_profile_still_defaults_to_code · covers: M3, E2 · `init` with no `--profile` produces the `code` lens set and exits zero
- test_engine_promises_no_unshipped_profile · covers: M4 · no engine comment or docstring names a profile absent from `PROFILES`, and the "remaining three ship as template files" claim is gone
- test_engine_twins_are_identical · covers: M5 · the canonical and `_bundled` engines digest the same
- test_refusal_adds_no_floor_or_evidence_kind · covers: R:NEWFLOOR · the engine's floor names and stampable evidence kinds are unchanged by this task
- test_no_scope_path_is_gitignored · covers: E1 · every `scope:` entry this task declares is asked of `git check-ignore`, and an ignored one fails — a gitignored scope entry has no blob, so its freshness cannot be attested
red-first: 3 of 7 are red at freeze — the silent fallback, the partial bundle it leaves, and the unshipped-profile comment. The other 4 are GREEN by design: they guard behaviour this change must NOT break (every shipped profile still initialises, a bare `init` still defaults to `code`, the twins stay identical, no floor moves). A regression guard on a breaking CLI change cannot be red first without breaking the thing it protects. Two check defects were found by running them red and fixed before freeze: the floor check conflated sensitivity NAMES with authority VALUES and failed on the legitimate `mechanical` key, and the comment check matched a claim that WRAPS across two comment lines, so it read green while the claim stood.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
