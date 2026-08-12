---
type: Task
title: A partial test run must say so
status: done
depth: standard
sensitivity: architecture
scope:
  - add-method/conftest.py
  - add-method/pytest.ini
  - add-method/tests/skill/test_run_completeness.py
gives:
  - S1 the notice a partial run prints when it collected fewer test roots than the repo has
  - S2 the guard that every test root a bare run should reach is actually reachable
generated: { by: add/3.2.0, at: 2026-08-12 }
verified:
  - { by: "Tin Dang", at: 2026-08-12, act: freeze, authority: human, direction: "sha256:b49bdd9134edc2ae" }
  - { by: "cli", at: 2026-08-12, act: brief, authority: process, brief: "sha256:e966ac52f2b62953" }
  - { by: "Tin Dang", at: 2026-08-12, act: refreeze, authority: human, direction: "sha256:b49bdd9134edc2ae" }
  - { by: "cli", at: 2026-08-12, act: brief, authority: process, brief: "sha256:8c7db565edbd8da7" }
  - { by: "process:run", at: 2026-08-12, act: run, authority: process, outcome: FAIL, receipt: /tasks/partial-run-visible.d/runs/1.md }
  - { by: "process:run", at: 2026-08-12, act: run, authority: process, outcome: PASS, receipt: /tasks/partial-run-visible.d/runs/2.md }
  - { by: "Tin Dang", at: 2026-08-12, act: gate, authority: plan, outcome: PASS, receipt: /tasks/partial-run-visible.d/runs/2.md, brief: "sha256:8c7db565edbd8da7" }
---
## CARD
goal: a test run that covered less than the whole suite says so in its own output, and a test root that a bare run cannot reach fails a check by name
why: across an entire session I reported "suite green" from `pytest add-method/tests/` while `add-method/tooling/` — 8 checks, including the `ENGINE_MD5` pins, which CI also runs — was RED. Every green I reported was true of the suite I ran and silent about the one I did not. A red branch reached the point of merge on that basis. The repo was not at fault: `pytest.ini` already makes a bare `pytest` from `add-method/` collect all 715, and its comment already explains why `tooling/` must stay collectable. Nothing can stop someone typing a narrower command — but a run that covered part of the suite can refuse to look like a run that covered all of it.
beat: done · next: add status

## RULES
<must>
- M1 a run that collects from fewer than every known test root prints a notice naming the roots it did NOT reach, and the command that would
- M2 the notice never fails the run — a narrow run while iterating is legitimate and making it an error would train people to pass a suppression flag
- M3 a test root that a bare run cannot reach fails a check BY NAME, so a new suite cannot be added and go silently uncollected
- M4 a full run prints nothing new — a notice that appears every time is one nobody reads
</must>
<reject>
- R:GAGGED the notice must not be suppressible by an environment variable or flag added for convenience; the one thing it exists to survive is someone finding it inconvenient -> "gagged"
- R:PINNED the set of known roots must be discovered from the tree, not written down — a hand-maintained list would have omitted `tooling/` exactly as I did -> "pinned"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1, S2 · it does not say who the notice is for; taking it as whoever ran the command, human or agent, printed to the run's own terminal output rather than a log file, because the failure being fixed is someone READING a green summary and believing it covered everything -> if wrong, the notice lands somewhere nobody looks and the run still reads as complete
- A2 [which] covers: S1, S2 · it does not say what counts as a test root; taking it as any directory holding a `test_*.py` file that a bare run from the package root would collect, which excludes the `eval/fixture/` sample project that `norecursedirs` already excludes for a documented reason -> if wrong, the notice fires on every run about a fixture that is not part of the suite, and M4 is defeated on day one
- A3 [when] covers: S1, S2 · it does not say when the notice prints; taking it as at session finish, after the summary line, so it is the last thing on screen next to the count it qualifies -> if wrong, it scrolls past above hundreds of lines of test output and is never seen
- A4 [absent] covers: S1, S2 · it does not say what to do when collection is empty or the run was aborted; taking it as: print nothing, because a run that collected nothing has an obvious problem of its own and a second message about coverage would bury it -> if wrong, a crashed run gains a confusing extra notice
- A5 [order] covers: S1, S2 · it does not say whether root discovery must be deterministic; taking it as sorted, so two runs of the same partial command print the same list and a diff of two outputs is meaningful -> if wrong, the notice churns between runs and reads as noise
- A6 [experience] covers: S1, S2 · it does not say what the reader needs from the notice; taking it as someone who believes they just ran the whole suite, so the notice must state what was MISSED rather than what ran, and hand them the exact command that would cover it — a bare "partial run" tells them nothing they can act on, and a count tells them less than a name -> if wrong, they read it as noise, learn to skip it, and the next stale pin ships exactly as this one did

## PLAN
contract: a `conftest.py` at the package root discovers every test root under it, compares that set against the roots the current session actually collected from, and at session finish prints the difference — the missed roots by name plus the command that covers them. Nothing is printed when the run was complete or collected nothing. A guard asserts the discovery is derived rather than listed, that every discovered root is reachable from a bare run, and that a full run stays silent.
scope: add-method/conftest.py, add-method/pytest.ini, add-method/tests/skill/test_run_completeness.py
widened after freeze: the reachability check found a REAL uncollected suite on its first execution — `norecursedirs = eval …` matches any directory NAMED eval, so `tests/eval` (2 tests) has never been collected by a bare run or by CI, while the exclusion was only ever meant for the top-level `eval/` fixture project. Fixing what the check found needs `pytest.ini`, which the original scope did not reach. Re-frozen rather than edited under seal.

## EDGES
- E1 the guard runs INSIDE the suite it is measuring, so it can see its own session's collected roots and would trivially pass whenever the full suite runs it. It must therefore establish reachability by asking the collector what a bare run WOULD collect, not by observing what the current run did.

## CHECKS
- test_every_test_root_is_reachable_from_a_bare_run · covers: M3, E1, R:PINNED · every directory holding a `test_*.py` under the package root is collected by a bare run, discovered from the tree rather than from a list
- test_partial_run_names_what_it_missed · covers: M1, A6 · a run restricted to one root prints the missed roots by name and the command that covers them
- test_full_run_prints_no_notice · covers: M4 · a complete run adds nothing to its output
- test_notice_has_no_off_switch · covers: R:GAGGED, M2 · the notice is not gated on any environment variable or option, and its emission never changes the exit code
red-first: 3 of 4 are red at freeze — `conftest.py` does not exist at the package root, so there is nothing to discover roots, nothing to print, and nothing to inspect for an off switch. The reachability check is red for a subtler reason worth stating: without the discovery helper it cannot enumerate roots at all, which is the same gap that let `tooling/` stay invisible. The fourth is green VACUOUSLY — nothing prints today, so a full run trivially prints no notice — and that is the honest reason, not a claim it is proving anything yet. It stays armed through the build as the one check that fails if the notice fires on a complete run, which is how M4 dies.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
