---
type: Task
title: A bundle that exists above you is a bundle status sends you to, never one init offers to replace
status: direction
depth: standard
sensitivity: architecture
milestone: first-run-truth
scope:
  - add-method/tooling/add.py
  - add-method/tests/engine
gives:
  - S1 `ancestor_bundle` — the upward walk that answers "is there a bundle above this directory"
  - S2 the `status` no-bundle branch — what an orienting reader is told when one exists above
  - S3 the `init` admission check — when creating a bundle here is refused
generated: { by: add/3.3.0, at: 2026-09-01 }
verified:
  - { by: "Tin Dang", at: 2026-09-01, act: freeze, authority: human, direction: "sha256:82ff2145c5f33eb7" }
---
## CARD
goal: `status` run where there is no bundle names an ancestor bundle if one exists and sends the reader to it, and `init` refuses to create a nested bundle under one unless `--nested` says that is deliberate.
why: Reproduced 2026-09-01 in this repo: `cd add-method/src && python3 ../../.add/tooling/cli.py status` prints `no bundle here — run `add init` to create one` / `next: add init`. Following the engine's own `next:` line creates a second `index.md` beside the real one. `grep -c ancestor` over `add.py` and `cli.py` returns 0, and no test in either root mentions it — the guard has never existed. Changing directory into a subdirectory is the single most common thing an engineer does, and ADD's whole promise is that state on disk is the source of truth; two bundles in one repo destroys that, and the engine is what instructs the user to build the second one. The refusal messages elsewhere in this engine are its best feature — this is the one that is confidently wrong rather than merely vague.
beat: direction · next: add freeze nested-bundle-guard

## RULES
<must>
- M1 `ancestor_bundle(root)` walks upward from the directory ABOVE the candidate root and returns the nearest ancestor holding a bundle marker (`index.md`), or None.
- M2 `status` on a directory with no bundle of its own names the ancestor bundle when one exists, and its `next:` line sends the reader to that bundle rather than to `init`.
- M3 `init` refuses to create a bundle when an ancestor bundle exists, unless `--nested` is passed; the refusal names the ancestor and both ways forward.
- M4 `init --nested` under an ancestor creates the bundle and says plainly that two bundles now exist.
- M5 The walk stops at the filesystem root and at a directory it cannot read, and never follows a symlink out of the tree it started in.
</must>
<reject>
- R:RIVALBUNDLE `init` must never silently create a bundle nested under another -> "R:RIVALBUNDLE"
- R:MISDIRECT a bundle-less directory under an existing bundle must never be told `next: add init` -> "R:MISDIRECT"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S3 · the request does not say who may create a nested bundle; taking anyone who passes `--nested` explicitly — the engine cannot tell a monorepo maintainer from a lost newcomer, so the flag IS the distinction -> if wrong a legitimate sub-bundle costs one extra flag · probe: `init --nested` under an ancestor succeeds and says two bundles now exist.
- A2 [which] covers: S1 · the request does not say which marker proves a bundle; taking `index.md`, which `init` always writes and nothing else does — the same marker `status` already keys its own no-bundle branch on -> if wrong the walk misses a real bundle or invents one · probe: a directory holding only `graph.json` is not an ancestor bundle.
- A3 [when] covers: S1 · the request does not say where the walk stops; taking the filesystem root, an unreadable directory, or leaving the starting tree via a symlink — whichever comes first -> if wrong the walk climbs out of the project or raises on a permission error · probe: the walk terminates on an unreadable parent and returns None rather than raising.
- A4 [absent] covers: S2 · the request does not say what a MISSING ancestor means; taking the incumbent behaviour unchanged — no ancestor is exactly today's `next: add init` -> if wrong the common first-run case regresses · probe: `status` in a bundle-less tree with no ancestor still prints the incumbent line verbatim.
- A5 [order] covers: S2 · the request does not say what happens when a 2.x bundle sits here AND an ancestor exists; taking the 2.x branch first, because it answers "the upgrade ate my project", which is the more alarming reading -> if wrong a 2.x user is sent upward instead of being reassured · probe: the 2.x branch fires ahead of the ancestor branch.
- A6 [experience] covers: S2 · the request does not say what the reader should see; taking the ancestor's path plus a runnable `cd … && add status`, because the recovery must be copy-pasteable at the moment of confusion -> if wrong the reader is told they are wrong without being told where to go · probe: the printed `next:` line is a runnable command naming the ancestor path.
- A7 [who] covers: S1 · n/a · a pure upward path walk takes no actor.
- A8 [who] covers: S2 · n/a · orientation is read-only and identical for every reader.
- A9 [which] covers: S2 · n/a · A2 fixes the marker for every surface that consults the walk.
- A10 [which] covers: S3 · n/a · A2's marker is what `init` admits on.
- A11 [when] covers: S2 · n/a · the walk's boundary is A3's; `status` adds none of its own.
- A12 [when] covers: S3 · n/a · admission is evaluated once, before anything touches the filesystem, exactly as `R:BADPROFILE` already is.
- A13 [absent] covers: S1 · n/a · "no ancestor" is the walk's documented None return, not a missing value.
- A14 [absent] covers: S3 · n/a · A4's reading governs: no ancestor means `init` behaves exactly as it does today.
- A15 [order] covers: S1 · n/a · the walk is nearest-first by construction.
- A16 [order] covers: S3 · n/a · the profile refusal already runs before any write and this check joins it there (A12).
- A17 [experience] covers: S1 · n/a · the walk prints nothing; its experience is S2's and S3's.
- A18 [experience] covers: S3 · n/a · the refusal names the ancestor and both ways forward per M3, which is A6's reading applied to `init`.
every `gives:` surface is swept on every dimension; `[<dim>] n/a · <why>` retires one. one line, one silence — split, never bundle. `· probe: <what shipped behavior must show>` declares a reading checkable: cite its A id from CHECKS and the gate holds the PASS to it.

## PLAN
contract: a module-level `ancestor_bundle(root)` in `add.py`; `status`'s no-bundle branch consults it after the 2.x branch; `init` consults it before any write and refuses with `R:RIVALBUNDLE` unless `nested=True`; `cli.py` grows `init --nested`. No reader of an existing bundle changes.
scope: add-method/tooling/add.py, add-method/tests/engine

## EDGES
- E1 a bundle-less directory with NO ancestor bundle — the incumbent `next: add init` line is unchanged.
- E2 a 2.x bundle sitting here while a 3.0 ancestor exists — the 2.x message wins (A5).
- E3 an unreadable or permission-denied parent directory — the walk returns None rather than raising (A3).
- E4 the repository root itself — the walk terminates at the filesystem root and returns None.
- E5 `init` called ON an existing bundle directory — unchanged: `init` never overwrites, and this guard is about ANCESTORS, not about self.

## CHECKS
- test_ancestor_bundle_finds_the_nearest_bundle_above · covers: M1, A2 · a directory two levels under a bundle resolves to that bundle.
- test_ancestor_bundle_is_none_at_the_top · covers: M1, E4 · a tree with no bundle anywhere returns None.
- test_ancestor_bundle_stops_on_an_unreadable_parent · covers: M5, A3, E3 · the walk returns None rather than raising.
- test_status_names_the_ancestor_and_sends_you_there · covers: M2, A6 · the output names the ancestor path and its `next:` is a runnable `cd … && add status`.
- test_status_without_an_ancestor_is_unchanged · covers: A4, E1, R:MISDIRECT · the incumbent line is printed verbatim.
- test_status_prefers_the_2x_message · covers: A5, E2 · the 2.x branch fires ahead of the ancestor branch.
- test_init_refuses_under_an_ancestor_bundle · covers: M3, R:RIVALBUNDLE · the refusal names the ancestor and no file is written.
- test_init_refuses_before_it_writes_anything · covers: A12, A16 · the candidate root holds no `index.md` after the refusal.
- test_init_nested_creates_and_says_so · covers: M4, A1 · the bundle is created and the note states two bundles now exist.
- test_init_without_an_ancestor_is_unchanged · covers: A14, E5 · a normal `init` and an `init` on an existing bundle both behave exactly as today.
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
