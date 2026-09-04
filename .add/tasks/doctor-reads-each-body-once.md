---
type: Task
title: doctor reads each node's body once per run
status: done
depth: standard
sensitivity: architecture
scope:
  - add-method/tooling/add.py
  - add-method/tests/engine/test_doctor_body_cache.py
gives:
  - S1 `add.py` `doctor()` reads each node's body at most once per call, through a run-scoped cache
  - S2 `tests/engine/test_doctor_body_cache.py` — the suite pinning read-once, finding parity, and per-run freshness
generated: { by: add/3.4.0, at: 2026-09-03 }
verified:
  - { by: "plan:engine-perf-diagnosis", at: 2026-09-03, act: freeze, authority: plan, direction: "sha256:e6557d6389aeb282", binding: "sha256:a0e60e91b83d9d93" }
  - { by: "cli", at: 2026-09-03, act: brief, authority: process, brief: "sha256:7d562fb1f4fe8cd1" }
  - { by: "process:run", at: 2026-09-03, act: run, authority: process, outcome: PASS, receipt: /tasks/doctor-reads-each-body-once.d/runs/1.md }
  - { by: "plan:engine-perf-diagnosis", at: 2026-09-03, act: refreeze, authority: plan, direction: "sha256:5eb2d77fa83ce94d", binding: "sha256:a0e60e91b83d9d93" }
  - { by: "cli", at: 2026-09-03, act: brief, authority: process, brief: "sha256:727b622a8ff6e270" }
  - { by: "process:run", at: 2026-09-03, act: run, authority: process, outcome: PASS, receipt: /tasks/doctor-reads-each-body-once.d/runs/2.md }
  - { by: "plan:engine-perf-diagnosis", at: 2026-09-03, act: gate, authority: plan, outcome: PASS, receipt: /tasks/doctor-reads-each-body-once.d/runs/2.md, brief: "sha256:727b622a8ff6e270" }
---
## CARD
goal: doctor stops re-reading bodies it already read — same findings, a third of the parsing
why: measured after the scan fix — `doctor` performs 386 `read()` calls and 594 `parse()` calls over a 196-node graph, because three loops each re-read the same T2 bodies: the fragment-resolution loop re-reads a target's body once per incoming fragment edge, the markdown-link loop reads every node again, and the placeholder loop reads every lifecycle node a third time. `status` parses 208 times for the same graph; doctor parses 594. The parser is already hand-optimised (`_split_commas` jumps between specials rather than visiting characters), so the cost is not the parse — it is doing it three times.
beat: done · next: add status

## RULES
<must>
- M1 `doctor()` MUST read any given node's body at most once per call
- M2 `doctor()`'s findings MUST be unchanged — same codes, same severities, same targets, same order
- M3 the cache MUST be scoped to ONE call: a later `doctor()` on the same bundle MUST see edits made since the earlier call
- M4 a node whose body `doctor` never needs MUST NOT be read at all — the cache is lazy, never a prefetch
</must>
<reject>
- R:STALEDOC a finding computed from a body read during an earlier `doctor()` call -> "STALEDOC"
- R:PREFETCH reading every body up front to make the counting check pass -> "PREFETCH"
</reject>

## ASSUMPTIONS
- A1 [who] covers: S1,S2 · the request does not say who may share the cache; taking "nobody — it is a local of one `doctor()` call, never a module global, never passed in or out, so no other verb and no later call can observe it" -> cost if wrong: a stale finding survives a repair and `--sync` reports work it did not do -> R:STALEDOC · probe: a check edits a file between two `doctor()` calls and asserts the second sees the edit
- A2 [which] covers: S1,S2 · the request does not say which reads are cached; taking "every T2 body read doctor causes, INCLUDING the one inside `card_drift` — the first reading said 'the three loops inside doctor()' and was wrong: a traceback during build found a fourth site in `card_drift`, which is why it now takes an optional `body_of` reader. `read(idx, \"T2\")` for the compiled index is a single read of a reserved file and stays direct" -> cost if wrong: a fifth site keeps re-reading and the win silently halves · probe: the read-count check asserts an EXACT total against the graph, not merely 'no repeats'
- A3 [when] covers: S1,S2 · the request does not say when a body enters the cache; taking "lazily, at first use — a bundle where no edge carries a fragment reads no target bodies for that loop at all" -> cost if wrong: doctor reads MORE than before on a fragment-free bundle -> R:PREFETCH · probe: a check asserts a body never needed is never read
- A4 [absent] covers: S1,S2 · the request does not say what a missing body means; taking "an empty body is a cached value like any other and is not re-read on the next hit — absence of content is not absence of an entry" -> cost if wrong: an empty-bodied node is re-read every time, which is the bug this closes
- A5 [order] covers: S1,S2 · [order] n/a · every loop already iterates `sorted(graph.items())` and caching changes no iteration order; M2 pins finding order explicitly
- A6 [experience] covers: S1,S2 · the request does not say who receives this; taking "the operator running `add doctor` and the agent running `doctor --sync` — both must see byte-identical output, because a report that changed its wording while getting faster is a report you re-read to check what moved" -> cost if wrong: an operator distrusts a clean report · probe: a check compares full rendered output before and after

## PLAN
contract: a run-scoped memo inside `doctor()` keyed by node path, filled lazily at first use, holding the T2 body string. Total held is 534 KB across 207 nodes on this bundle (largest single body 21 KB), so the cache is bounded by the bundle the verb is already walking.
scope: add-method/tooling/add.py · add-method/tests/engine/test_doctor_body_cache.py

## EDGES
- E1 two fragment edges pointing at the SAME target — the target's body is read once, not twice
- E2 a node read by BOTH the markdown-link loop and the placeholder loop — one read, not two
- E3 a node with an empty body — cached and not re-read

## CHECKS
- test_doctor_reads_each_body_at_most_once · covers: M1,E1,E2 · a bundle with repeated fragment targets yields at most one read per node path
- test_doctor_findings_are_byte_identical · covers: M2,A6 · the full finding list and rendered output match the pre-change engine exactly
- test_doctor_cache_does_not_survive_the_call · covers: M3,R:STALEDOC,A1 · a body edited between two calls is seen by the second
- test_doctor_never_reads_a_body_it_does_not_need · covers: M4,R:PREFETCH,A3 · a fragment-free bundle reads no more bodies than the loops require
- test_doctor_body_reads_equal_the_nodes_that_need_one · covers: A2 · the EXACT total, so a fifth uncached site is a failure not a smaller win
- test_empty_body_is_cached_not_reread · covers: E3,A4 · a node with an empty body is read once
red-first: every check MUST fail first.

## EVIDENCE
receipt: <runs/<n>.md>
gate: <PASS | RISK-ACCEPTED | HARD-STOP>

## LESSONS
- <lesson> -> add learn <lens>
