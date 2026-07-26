# PLAN: Interrupt-resume mechanics: progress-sampled kill, fresh-context resume, kill point recorded

slug: bench-interrupt-mechanics · created: 2026-07-26 · stage: mvp
milestone: add-bench-2
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: interrupt an arm mid-milestone at a PROGRESS-sampled point, resume it with a fresh conversation on the same workspace, and record the kill point — the mechanics the interrupt-resume track needs before any metric can mean anything.
Framings weighed: KILL AT THE K-TH CODE-WRITING EVENT (chosen — holds progress constant and varies only the method, which is the question "who recovers better?" actually asks) · kill at a wall-clock fraction (rejected — arms differ in pace and in how front-loaded their thinking is, so a wall-clock kill catches a planning-first method earlier in its code progress and the metric measures pace, not recovery) · kill at a fraction of the arm's own median run length (rejected — needs per-arm calibration, so the kill point depends on earlier measurements of the thing being measured).
Must:
<must>
  - M1 `sample_kill_point(wm, rep, seed)` is DETERMINISTIC and arm-independent: the same (wm, rep) yields the same K for every arm.
  - M2 the agent is killed once the K-th code-writing event appears in its streaming transcript, and the whole process group dies with it.
  - M3 a wall-clock backstop kills a run that never reaches K, so a method that writes no code cannot buy immunity by not building.
  - M4 resume re-invokes on the SAME workspace with a FRESH conversation — the on-disk state is the only carrier, which is the shape every method claims to support.
  - M5 the record carries the kill point actually used, whether it fired on the K-th write or on the backstop.
  - M6 an uninterrupted run is byte-identical to today: no kill, no new record fields beyond the interrupt block, no behaviour change when interruption is off.
</must>
Reject:
<reject>
  - a kill point that differs per arm for the same (wm, rep) -> "unfair_kill_point"
  - a run that reaches K and is not killed -> "missed_interrupt"
  - a resume that carries the prior conversation -> "context_carryover" (it would measure memory, not recovery)
</reject>
After:
<after>
  - a run can be interrupted and resumed under harness control, with the kill point on the record for audit.
  - the track-specific metrics (recovery, duplicated work) become buildable on top; they are NOT in this task.
</after>
Boundary: a streaming JSONL transcript whose code-writing acts appear as Write/Edit tool_use OR a source-writing Bash command — the same two shapes `_first_code_write_offset` already counts, reused rather than re-derived.
<assumptions>
  ⚠ that holding CODE progress constant is the fair comparison. It advantages a method that thinks longer before writing, because it reaches the K-th write later in wall-clock and has done more planning by then. That is arguably the honest question for a RESUME track — but it is a choice, and if the reading is wrong the track rewards front-loading rather than recoverability.
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
benchmark/interrupt.py                                        NEW
  sample_kill_point(wm, rep, *, seed=DEFAULT_SEED,
                    lo=2, hi=8) -> int
      deterministic per (wm, rep); NEVER takes an arm — an arm-dependent K
      would compare arms at different progress points (unfair_kill_point).

  count_code_writes(transcript_text) -> int
      reuses the Write/Edit + source-writing-Bash vocabulary already pinned by
      benchmark.score, so the kill trigger and the edit_pos cut-point can never
      drift apart.

  watch_and_kill(proc, transcript_path, *, k, backstop_s, poll_s=0.5)
      -> {"fired": "kth_write"|"backstop"|"none", "writes_seen": int,
          "elapsed_s": float}
      polls the STREAMING transcript; on the k-th write kills the whole process
      group. backstop_s bounds a run that never reaches k (M3).

benchmark/runner/core.py
  execute_wm(..., interrupt: dict | None = None)
      None (default) = today's behaviour, unchanged (M6).
      set  = kill per watch_and_kill, then re-invoke ONCE on the SAME workspace
             with a FRESH conversation and the arm's resume prompt (M4).
  record.artifacts["interrupt"] = json.dumps({k, fired, writes_seen, elapsed_s})
```

Target (measurable): sample_kill_point returns the same K for every arm at fixed (wm, rep) across 100 samples and spans its range; a fake agent that writes N>k files is killed with exactly k writes observed and its child process group is dead; a fake agent that writes nothing is killed by the backstop; a resume invocation receives no prior conversation; an uninterrupted execute_wm produces a record byte-identical to one produced before this change; benchmark suite green.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: yes — this bundle is the freeze report
### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT (the builder self-improves and records actual at verify)
Scope (may touch): `benchmark/interrupt.py` `benchmark/runner/` `benchmark/tests/`
Regression floor: the full `benchmark/tests` suite — green before the gate; M6 makes the existing runner behaviour part of the contract, not just the floor.
Persona (optional): `.add/personas/tdd-verifier.md`

Least-sure flag surfaced at freeze: [spec] the ⚠ above — that holding CODE progress constant is the fair comparison. Every sampling rule encodes a theory of what "the same point in the work" means, and there is no neutral choice. Progress-sampling advantages a method that plans before writing; wall-clock sampling advantages a method that writes early. I chose progress because the track's question is "given the same code written, who recovers better?", and because wall-clock would let arm SPEED leak into a recovery metric. Mitigation: the kill point and the observed write count are both on the record, so a reader can check whether the kill landed at a comparable place per arm — and if it did not, the honest response is to report the track as not-yet-fair rather than to publish the numbers.
### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_kill_point_is_deterministic: same (wm, rep, seed) -> same K · covers: M1
  - test_kill_point_is_arm_independent: sample_kill_point takes no arm parameter and is equal across arm names · covers: M1, R:unfair_kill_point
  - test_kill_point_spans_its_range: 100 (wm, rep) pairs cover more than one value · covers: M1
  - test_code_write_counting_matches_the_scorer: same vocabulary as benchmark.score, so trigger and cut-point cannot drift · covers: M2
  - test_kills_on_the_kth_write: a fake agent writing 5 files with k=3 is killed having seen exactly 3 · covers: M2, R:missed_interrupt
  - test_kill_takes_the_whole_process_group: the fake agent's CHILD is dead too · covers: M2
  - test_backstop_kills_a_run_that_never_writes: covers: M3
  - test_no_kill_when_the_run_finishes_first: fired == "none" · covers: M6
  - test_resume_runs_on_the_same_workspace: covers: M4
  - test_resume_carries_no_prior_conversation: covers: M4, R:context_carryover
  - test_record_carries_the_kill_point: covers: M5
  - test_uninterrupted_execute_wm_is_unchanged: interrupt=None leaves today's record shape identical · covers: M6
</test_plan>

Rigor: one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. Minor/secondary behaviors are DESCRIBED in prose below as build-guidance — no `covers:` tag, no red test, not gated. Add a Given/When/Then line inline ONLY when a human stakeholder needs a readable case — never as ceremony; the test_plan is the canonical encoding of every scenario.

Tests live in: `benchmark/tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: <fill at VERIFY — what you ACTUALLY did (or "as planned"); harvested into §7 Decisions (ADR)>
Code lives in: `src/`
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
Verdict: <EARNED | NOT-EARNED>
By: <self | agent-id> · adversarially checked: <what was probed>

### GATE RECORD
Reported: <yes — the gate report (banner/ARC) rendered before this outcome recorded | no>
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-26

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose KILL AT THE K-TH CODE-WRITING EVENT; rejected kill at a wall-clock fraction (rejected — arms differ in pace and in how front-loaded their thinking is, so a wall-clock kill catches a planning-first method earlier in its code progress and the metric measures pace, not recovery) · kill at a fraction of the arm's own median run length (rejected — needs per-arm calibration, so the kill point depends on earlier measurements of the thing being measured).
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
