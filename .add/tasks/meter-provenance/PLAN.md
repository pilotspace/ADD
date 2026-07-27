# PLAN: A scored record states which meter produced it

slug: meter-provenance · created: 2026-07-27 · stage: mvp
milestone: direction-velocity
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: a scored record states which meter produced it, and the collection-shape guard covers ORACLES as well as checklists.
Framings weighed: stamp a content hash of the scoring modules onto every record + widen the existing guard to enumerate oracle files (chosen — the two defects are one concern: a number you cannot date and a probe that encodes an unstated preference are both the meter lying) · stamp only, file the oracle gap as a delta (rejected — six live surfaces distort scores today, and the guard that was supposed to catch them already exists and simply looks at the wrong half of the tree) · hand-maintained meter version constant (rejected — a version someone must remember to bump is the `turn_ceiling` failure mode: declared, never true)
Must:
<must>
  - every scored record carries a meter_version derived from the CONTENT of the scoring modules, so editing a scorer changes it without anyone remembering to
  - the collection-shape guard enumerates oracle files as well as checklists — a bare-array assertion anywhere in the workload tree fails it
  - no oracle asserts a bare JSON array where the workload PROMPT never fixed the serialization
</must>
<reject>
  - a scoring module edited with no change in meter_version -> "stale_meter_stamp"
  - an oracle asserting isinstance(body, list) for a collection the prompt left open -> "bare_array_assertion"
</reject>
After:
<after>
  - two records scored by different meters are distinguishable without reading git history
  - the guard that caught the ported payments track's 8 defects now covers the half of the tree it was blind to
</after>
Boundary: the record's `artifacts` dict is the only carrier (string values only); `metrics` is a closed key-set validated by `run_record.validate`, so provenance must NOT ride there.
<assumptions>
  ⚠ scoring is deterministic given the module content, so a content hash is a sound version — if wrong (a scorer reads an unhashed input, e.g. a workload checklist), two runs could share a stamp yet differ; cost = widen the hashed set, the stamp mechanism itself is unaffected.
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
benchmark/meter.py  (NEW)
  METER_MODULES : tuple[str, ...]   the files whose content defines a score
  meter_version() -> str            md5 over those files' bytes, 12 hex chars

record.artifacts["meter_version"] : str    stamped by score_record

benchmark/tests/test_collection_shape.py  (WIDENED)
  enumerates workload/*/checklist.py  AND  workload/*/oracle/*.py
  a banned bare-array assertion in EITHER -> fail
```
Ground: `benchmark/schema/run_record.py` — `REQUIRED_ARTIFACTS` is a subset check (:110 tests only for MISSING keys), so an extra artifact key is accepted; `REQUIRED_METRICS`/`OPTIONAL_METRICS` (:21/:37) are a CLOSED set that rejects extras, which is why the stamp rides in artifacts. `benchmark/score.py::score_record` builds `artifacts`. `benchmark/workload/_oracle_lib.py::records` (:139) is the existing envelope-tolerant reader. The six live surfaces: `wm1/oracle/test_bookings.py:46` · `wm1/oracle/survivors.py:51` · `wm4/oracle/survivors.py:80,96` · `wm5/oracle/survivors.py:96` · `amb1/oracle/test_amb1_clean.py:60`.

Target (measurable): the widened guard is RED naming all 6 oracle surfaces before the fix and GREEN after, with 0 bare-array assertions left in `benchmark/workload/`; `meter_version()` is stable across two calls and CHANGES when any scoring module's bytes change; `benchmark/tests/` stays green (514 -> 514+new).
Status: FROZEN @ v1 — approved by Tin Dang
Reported: <yes — the freeze report (banner/ARC/SHAPE) rendered before this froze | no>

### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT (the builder self-improves and records actual at verify)
Scope (may touch): `benchmark/meter.py` `benchmark/score.py` `benchmark/workload/` `benchmark/tests/`   <HARD — fill before the freeze; the file write-set, single source of truth; every file the build may write. Token grammar (backtick each): name/ = project root · ./… = THIS task's dir (rarely what a build writes) · a directory covers its whole subtree>
Regression floor: `benchmark/tests/` — all 514 stay green; `run_record.validate` must accept the extra artifact key with no schema change.   <optional — the existing suite(s) that must stay green; the host repo's own tests are a floor when present; run them before the gate — or omit / "none — greenfield">
Persona (optional): `.add/personas/tdd-verifier.md`.   <persona file under `.add/personas/` this build embodies — advisory, never lowers a gate; omit or "generic" if none fits>

Least-sure flag surfaced at freeze: [test] widening the guard to oracles may fire on a survivor probe whose bare-array assertion is CORRECT — a survivor re-run against a later workspace legitimately pins the shape the earlier milestone froze. If so the fix is a narrow, reasoned allowlist entry, not loosening the guard; cost = one triage pass over the 6 surfaces.

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_meter_version_is_stable_across_calls: two calls agree · covers: M1  [GATED]
  - test_meter_version_tracks_module_content: mutate a hashed module in a tmp copy -> stamp changes · covers: M1, R:stale_meter_stamp  [GATED]
  - test_scored_record_carries_the_stamp: score_record output has artifacts["meter_version"] · covers: M1  [GATED]
  - test_validate_accepts_the_extra_artifact_key: run_record.validate passes with the stamp present · covers: M1  [GATED]
  - test_guard_covers_oracle_files_too: the enumerated set includes workload/*/oracle/*.py · covers: M2  [GATED]
  - test_no_bare_array_assertion_anywhere_in_workload: 0 offenders across checklists AND oracles · covers: M3, R:bare_array_assertion  [GATED]
  - test_meter_version_is_short_and_hex: 12 hex chars, safe in a filename or a table cell · covers: M1  [edge]
  - test_missing_module_fails_loud: a METER_MODULES entry that does not exist raises rather than hashing nothing · covers: M1  [edge]
</test_plan>

Rigor: one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. Minor/secondary behaviors are DESCRIBED in prose below as build-guidance — no `covers:` tag, no red test, not gated. Add a Given/When/Then line inline ONLY when a human stakeholder needs a readable case — never as ceremony; the test_plan is the canonical encoding of every scenario.

Tests live in: `benchmark/tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned, plus one widening the plan did not anticipate — `_probe_sources` in test_collection_shape.py had to yield `workload/*/oracle/*.py` as a SECOND glob rather than a broadened single pattern, because oracle probes live one directory deeper than checklists. All 6 named surfaces were real (the least-sure flag's "legitimately pins an earlier frozen shape" case did not occur); each was fixed with the existing `records(body) is not None` reader rather than an allowlist.
Code lives in: `benchmark/`
Spawn (multi-agent): build/verify subagent spawns default `isolation: worktree`; cross-agent advisor — spawn `add-advisor` (an agent OTHER than the builder) for the freeze `--cross` and the §6 refute-read; `self` only when solo.
Constraints: do NOT change any test or the frozen §3 contract; stay inside §3 Scope (an out-of-scope build fails the gate: scope_violation); keep the §3 Regression floor green; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all tests (or §4 acceptance checks) pass — including the §3 Regression floor (host suite)
- [ ] coverage did not decrease
- [ ] no test or contract was altered during build
- [ ] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (a confirmed cheat is HARD-STOP)
- [ ] concurrency / timing of the risky operation is safe
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self · adversarially checked: (1) the stamp test was run against a mutated tmp COPY of the module set, so it proves content-tracking rather than re-asserting the same function twice; (2) `test_missing_module_fails_loud` monkeypatches METER_MODULES to a nonexistent file and requires a raise, killing the "skip absentees" mutant that would drift the stamp toward a constant; (3) the widened guard was confirmed RED naming all 6 oracle surfaces BEFORE the fixes, so it is not vacuous; (4) `test_scored_record_carries_the_stamp` reads score_record's source rather than trusting a caller to stamp.

### GATE RECORD
Reported: yes
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-27

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose stamp a content hash of the scoring modules onto every record + widen the existing guard to enumerate oracle files; rejected stamp only, file the oracle gap as a delta (rejected — six live surfaces distort scores today, and the guard that was supposed to catch them already exists and simply looks at the wrong half of the tree) · hand-maintained meter version constant (rejected — a version someone must remember to bump is the `turn_ceiling` failure mode: declared, never true)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned, plus one widening the plan did not anticipate — `_probe_sources` in test_collection_shape.py had to yield `workload/*/oracle/*.py` as a SECOND glob rather than a broadened single pattern, because oracle probes live one directory deeper than checklists. All 6 named surfaces were real (the least-sure flag's "legitimately pins an earlier frozen shape" case did not occur); each was fixed with the existing `records(body) is not None` reader rather than an allowlist.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
