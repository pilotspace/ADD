---
type: Task
title: join refuses what it cannot read
status: done
kind: feature
depth: quick
gives:
  - S1 add.join() — the unreadable-stream refusal
generated: { by: add/3.3.0, at: 2026-09-03 }
verified:
  - { by: "Tin Dang", at: 2026-09-03, act: freeze, authority: plan, direction: "sha256:8fafb781d66db312", binding: "sha256:ce3302faea043e0b" }
  - { by: "Tin Dang", at: 2026-09-03, act: refreeze, authority: plan, direction: "sha256:2c4e7e0045af4686", binding: "sha256:901c5b554e941628" }
  - { by: "Tin Dang", at: 2026-09-03, act: brief, authority: process, brief: "sha256:ca47b74b64542795" }
  - { by: "process:run", at: 2026-09-03, act: run, authority: process, outcome: PASS, receipt: /tasks/join-refuses-what-it-cannot-read.d/runs/1.md }
  - { by: "Tin Dang", at: 2026-09-03, act: gate, authority: process, outcome: PASS, receipt: /tasks/join-refuses-what-it-cannot-read.d/runs/1.md, brief: "sha256:1fda1821316a0116" }
---
## CARD
goal: `join` refuses a stream path it cannot read, instead of reporting a clean no-op merge.
why: measured — `add join /nonexistent/.add` prints "joined 0 stream(s)" and exits 0; a typo'd worktree path is indistinguishable from a wave that legitimately merged nothing.

## RULES
<must>
- M1 `join` refuses a stream path that is not a readable bundle
- M2 the refusal names the path it could not read
- M3 a readable stream that merged nothing is still a success — zero is a real answer
- M4 no stream is merged when any path is refused; the refusal is checked before any write
</must>
<reject>
- R:PHANTOMSTREAM a path the engine never read is reported as a stream that merged cleanly -> "PHANTOMSTREAM"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1 · n/a · a path either resolves or does not; no authority makes an unread path readable
- A2 [which] covers: S1 · the request does not say what makes a path a bundle; taking `_is_bundle_index` — the `abf_version:` marker `init` writes and nothing else — over the presence of `tasks/`, which `new` creates lazily so a legitimate stream that has not authored a node yet has none -> keying on `tasks/` would refuse a real stream, turning a missing-input guard into a false refusal · probe: a bundle with no `tasks/` directory is still accepted
- A3 [when] covers: S1 · the request does not say whether to refuse or warn; taking refuse with a non-zero exit, matching the `run` fabricated-receipt fix -> a wave script checking exit codes cannot tell a typo from a no-op · probe: the CLI exits non-zero
- A4 [absent] covers: S1 · the request does not say what an empty stream list means; taking it as a legal no-op -> refusing it would break a wave that scheduled nothing · probe: join with no paths still succeeds
- A5 [order] covers: S1 · the request does not say what happens when one of several paths is bad; taking all-or-nothing, checked before the first write -> a partial merge leaves the bundle in a state no receipt describes · probe: no node is copied when any path is refused
- A6 [experience] covers: S1 · the request does not say who reads the refusal; taking the author who typed or scripted the path -> "joined 0 stream(s)" tells them nothing went wrong · probe: the refusal names the offending path

## PLAN
contract: `join` validates every stream path against `_is_bundle_index` before merging any of them, refuses with the first unreadable path and R:PHANTOMSTREAM, and writes nothing. An empty list, a bundle with no `tasks/` yet, and a readable stream with no gated node all remain successes.
scope: add-method/tooling/add.py, add-method/tooling/cli.py, add-method/tests/engine/test_join_refuses_what_it_cannot_read.py

## EDGES
- E1 a path that exists but is a file, not a directory
- E2 a directory that exists and holds no bundle index — a bundle-shaped guess
- E3 a real bundle that has not created `tasks/` yet, which `init` never writes

## CHECKS
- test_join_refuses_a_path_that_does_not_exist · covers: M1, A3, R:PHANTOMSTREAM · the measured typo
- test_the_refusal_names_the_path · covers: M2, A6 · the fix is to correct the path, so print it
- test_a_readable_stream_that_merged_nothing_is_a_success · covers: M3, A4, E3 · zero is a real answer, and a fresh bundle has no tasks/
- test_nothing_is_merged_when_any_path_is_refused · covers: M4, A5 · all-or-nothing, before the first write
- test_a_file_or_a_non_bundle_directory_is_refused · covers: M1, A2, E1, E2 · existing is not readable
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- a verb that iterates a collection reports success over an empty one, and an unread input is empty -> add learn method
