---
type: Task
title: upgrade leaves a working bundle — the engine must not archive itself away
status: done
milestone: v3-final-collateral
scope:
  - add-method/tooling/add.py
  - add-method/tests/engine/test_upgrade_working_bundle.py
gives:
  - S1 `upgrade()` — the fresh 3.0 bundle keeps a runnable engine and the vendored corpus trees
  - S2 `tests/engine/test_upgrade_working_bundle.py` — the suite pinning post-upgrade drivability
generated: { by: add/3.0.0, at: 2026-08-11 }
verified:
  - { by: "human:tindang", at: 2026-08-11, act: freeze, authority: process, direction: "sha256:f0bf7eb1e312c7c8" }
  - { by: "cli", at: 2026-08-11, act: brief, authority: process, brief: "sha256:0e624c97ec8c9941" }
  - { by: "process:run", at: 2026-08-11, act: run, authority: process, outcome: PASS, receipt: /tasks/upgrade-working-bundle.d/runs/1.md }
  - { by: "human:tindang", at: 2026-08-11, act: gate, authority: process, outcome: PASS, receipt: /tasks/upgrade-working-bundle.d/runs/1.md, brief: "sha256:0e624c97ec8c9941" }
---
## CARD
goal: after `add upgrade`, the very next `add status` runs — the fresh bundle carries tooling/ and the corpus trees, restored by copy from the archive
why: release-blocker found live in the updater test (2.5 -> 3.0.0 chain): `upgrade` renames the WHOLE bundle — including the engine executing it — into the archive, inits only the nine starter files, and the printed `next: add status` dies on a missing cli.py; beta.2's review checked archive fidelity, never post-upgrade drivability
beat: done · next: add status
## RULES
<must>
- M1 after `upgrade`, `root/.add/tooling/` exists with `add.py` and `cli.py` byte-identical to the archived (running) engine
- M2 the vendored trees present in the old bundle (`personas-teacher/`, `personas-index/`) are restored into the fresh bundle the same way
- M3 restoration is COPY, never move — the archive stays the complete, byte-identical record it was promised to be
</must>
<reject>
- R:SELFARCHIVE an upgrade whose report says `next: add status` while the command it names cannot run -> "SELFARCHIVE"
</reject>
## ASSUMPTIONS
- A1 [who] covers: S1,S2 · the request does not say which engine gets restored; taking "the archived one — `upgrade` is a 3.0 verb, so the engine that dispatched it is by construction the current engine" -> cost if wrong: a stale engine restored where a newer package exists · probe: restored add.py is byte-identical to the archived add.py
- A2 [which] covers: S1,S2 · the request does not say which trees are restored; taking "tooling, personas-teacher, personas-index — the installer-managed trees; authored 2.x state stays archived-only, that is the whole point of the clean break" -> cost if wrong: a managed tree missing or a state file leaking forward
- A3 [when] covers: S1,S2 · the request does not say when restoration runs; taking "inside `upgrade`, immediately after `init` — never a separate verb the report merely recommends" -> cost if wrong: the dead-bundle window this task exists to close
- A4 [absent] covers: S1,S2 · the request does not say what happens when the old bundle lacks a tree; taking "skip it silently — a 2.x bundle with no corpus yields a 3.0 bundle with none, and the installer's next run fills it" -> cost if wrong: an upgrade crash on a minimal bundle
- A5 [order] covers: S1,S2 · the request does not say copy order; taking "any — the trees are disjoint; `__pycache__` is excluded as build noise" -> cost if wrong: none beyond noise files
## PLAN
contract: a copytree loop in `upgrade()` after `init`, archive -> fresh bundle, for the three managed trees when present
scope: add-method/tooling/add.py · add-method/tests/engine/test_upgrade_working_bundle.py
## EDGES
- E1 a minimal 2.x bundle with no tooling/ at all — upgrade still succeeds, nothing to restore
## CHECKS
- test_upgrade_restores_a_runnable_engine · covers: M1,A1,R:SELFARCHIVE · tooling/add.py+cli.py exist post-upgrade, byte-identical to the archive's
- test_vendored_trees_are_restored · covers: M2 · personas-teacher/personas-index present in the fresh bundle when the old one had them
- test_archive_stays_complete · covers: M3 · every archived file still present after restoration — copy, not move
- test_minimal_bundle_still_upgrades · covers: A4,E1 · no tooling in the old bundle: upgrade succeeds, nothing restored
red-first: every check MUST fail first.
## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>
## LESSONS
- <lesson> -> add learn <lens>
