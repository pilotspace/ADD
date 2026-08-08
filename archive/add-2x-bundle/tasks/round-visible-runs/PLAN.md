# PLAN: Round-visible runs — every verify→build return trip is engine-recorded

slug: round-visible-runs · created: 2026-07-22 · stage: mvp
milestone: thin-engine-loop
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: round-visible runs — record every verify→build return trip (a "round") in engine
state, uncapped and observational, so dynamic verify→fix workflows are engine-visible in
status and traces with zero new ceremony.
Framings weighed: implicit transition-recording on existing verbs (chosen — zero new verbs;
the verb census, roster pins, and README "thin kernel" claim stay untouched; rounds appear
for free whenever the flow already bounces) · a new `round` verb (rejected: verb-census
ripple + opt-in means unused) · `heal --honest` (rejected: muddies the monotonic cheat-cap).
Must:
<must>
  - M1 a verify→build transition via `add.py phase build` increments `tasks[slug].rounds.count` and appends `{at, source: "phase", note}` to `rounds.history`, atomically with the phase write
  - M2 `add.py phase build <slug> --note "finding"` stores the note on that round; note omitted stores null
  - M3 every NON-exhausted heal return (`_heal_or_escalate`, any source) also appends a round carrying its source — the heal `attempts` counter, cap, and exit semantics are byte-for-byte unchanged
  - M4 `status` surfaces `round N` on the active-task row when count > 0, silent at 0 (zero cost when unused)
  - M5 the `route-outcomes.jsonl` gate trace carries `"rounds": count` beside the existing `"heals"` field
</must>
Reject:
<reject>
  - `--note` passed with a phase target other than build -> "phase_note_build_only"
</reject>
After:
<after>
  - rounds are monotonic per task; a `new-task --force` re-create preserves them exactly like the heal counter (the F8 force-preserve pattern)
  - forward or same-phase transitions leave `rounds` byte-identical; a task that never bounced has NO `rounds` key (state shape unchanged for all existing tasks)
</after>
Boundary: none — no external input shape (`--note` is a plain string, stored verbatim)
<assumptions>
  ⚠ the status renderer has ONE active-task-row seam to carry `round N` — if wrong (multiple render paths), cost: the surfacing lands in `status --all` only and the bare row stays quiet
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>
</scenarios>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
CLI add.py phase build SLUG [--note "finding"]
  verify→build -> tasks[SLUG].rounds { count: +1, history: +[{at, source: "phase", note}] } · exit 0
  other→build  -> rounds untouched (existing _build_entry guard stack unchanged)
  --note with a non-build target -> exit 2 error: "phase_note_build_only"
CLI add.py heal SLUG --reason "f"  (non-exhausted path)
  -> existing heal semantics UNCHANGED, plus rounds +1 { source: the heal source }
Render: status active-task row gains "round N" when N > 0; route-outcomes.jsonl row gains "rounds": N
Schema: state.json tasks[SLUG].rounds = { count: int, history: [{at, source, note}] } — key absent until the first round
Anchors: cmd_phase · _heal_or_escalate · the cmd_gate route-trace writer · the status task-row renderer · engine_pin ENGINE_MD5 (re-aim; add_engine untouched so ENGINE_PKG_MD5 holds)
```

Target (measurable): after one `phase build` return and one heal return on a verify-phase task, `rounds.count == 2` with sources `["phase", "refute-read"]`; `status` names `round 2`; the gate trace row carries `"rounds": 2`; full tooling suite ≥ 1951 passed / 0 failed and `add.py check` 0-failed (the regression floor holds).
Status: FROZEN @ v1 — approved by Tin Dang
Least-sure flag surfaced at freeze: [contract] the status renderer may have more than one
task-row path — if so, `round N` lands in the primary active-task row only and the other
views follow in a later task (accepted: visibility beats completeness here).
Reported: yes — contract + tradeoffs rendered to the human before this freeze

### Build-strategy (SOFT: preferred; the builder self-improves and records actual at verify)
Scope (may touch): `add-method/tooling/` `.add/tooling/` `add-method/src/` `add-method/skill/` `.claude/skills/` `tmp/` `./`
Regression floor: the full tooling suite (`add-method/tooling/./t` — 1951 passing at draft) + `add.py check` 0-failed
Persona (required): `.add/personas/methodology-engine-dev.md` (engine change — NO-EXEC, pins, 3-tree propagation are its critical rules)

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_phase_verify_to_build_records_round: task at verify → `phase build` → count 1, history entry has at + source "phase" · covers: M1
  - test_phase_note_stored_on_round: `phase build --note "3 api tests red"` → history[0].note carries it verbatim · covers: M2
  - test_note_refused_off_build_target: `phase verify --note x` → exit ≠ 0, names phase_note_build_only, state byte-unchanged · covers: R:phase_note_build_only
  - test_heal_return_counts_a_round_cap_unchanged: heal at verify → rounds.count 1 with the heal source AND heal.attempts 1 (cap semantics untouched) · covers: M3
  - test_forward_transition_records_nothing: direction→build (post-freeze) then build→verify → no rounds key ever appears · covers: After
  - test_force_recreate_preserves_rounds: accrue a round, `new-task --force` → rounds survive (F8 mirror) · covers: After
  - test_status_surfaces_round_count: bounced task active → status text names "round 1"; un-bounced → "round" absent · covers: M4
  - test_route_trace_carries_rounds: gate a bounced task → route-outcomes.jsonl row has "rounds": 1 · covers: M5
</test_plan>

Tests live in: `add-method/tooling/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned, plus one refute-driven repair loop — the advisor's
refute-read (NOT-EARNED, 3 findings: exit 1 vs contracted exit 2 · whitespace note slipped
the refusal · note stored stripped not verbatim) drove a code fix in `cmd_phase` and
strengthened asserts via the recorded re-cross path. The five engine seams: `--note` on
the phase parser · validate-then-write refusal + `_record_round` in `cmd_phase` ·
`_record_round` call on `_heal_or_escalate`'s non-exhausted branch · F8-mirror preserve in
`new-task --force` · `round N` on the status now-row + `"rounds"` in the gate trace row.
Code lives in: `add-method/tooling/` (canonical engine; propagate to `.add/tooling/` + the bundle after green)
Spawn (multi-agent): build/verify subagent spawns default `isolation: worktree`; cross-agent advisor — spawn `add-advisor` (an agent OTHER than the builder) for the freeze `--cross` and the §6 refute-read; `self` only when solo.
Constraints: do NOT change any test or the frozen §3 contract; stay inside §3 Scope (an out-of-scope build fails the gate: scope_violation); keep the §3 Regression floor green; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests (or §4 acceptance checks) pass — including the §3 Regression floor (host suite): full tooling suite 1959 passed / 0 failed (was 1951 pre-task + 8 new); `add.py check` 0-failed
- [x] coverage did not decrease — 8 new tests cover every Must/Reject/After clause
- [x] no test or contract was altered during build — the one assert-strengthening landed via the RECORDED re-cross (approved by Tin Dang), tripwire re-snapshotted
- [x] the green was EARNED, not gamed — adversarial refute-read by add-advisor (cross-agent): first pass NOT-EARNED with 3 confirmed contract deviations; all fixed; mutation-checks on M1 confirmed non-vacuous
- [x] concurrency / timing of the risky operation is safe — the round increment rides the SAME atomic save_state as the phase write; _build_entry raises BEFORE any round is recorded (no half-write)
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib-only, NO-EXEC path untouched; note stored as data, never executed or rendered as markup
- [x] layering & dependencies follow CONVENTIONS.md — pure helper `_record_round` beside `_heal_or_escalate`; add_engine package untouched (ENGINE_PKG_MD5 holds)
- [x] a person reviewed and approved the change — contract frozen by Tin Dang; re-cross approved by Tin Dang; gate recorded in-session

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: add-advisor (cross-agent, two-pass) · adversarially checked: note-refusal exit code (2) ·
whitespace-flag refusal with byte-unchanged state · verbatim padded/whitespace note storage ·
exhausted-heal records no round · round accumulation across bounces · M1 mutation-check
non-vacuous · pin/twin integrity · re-cross provenance (first pass NOT-EARNED, 3 findings fixed)

### GATE RECORD
Reported: <yes — the gate report (banner/ARC) rendered before this outcome recorded | no>
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-22

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose implicit transition-recording on existing verbs; rejected a new `round` verb (rejected: verb-census ripple + opt-in means unused) · `heal --honest` (rejected: muddies the monotonic cheat-cap).
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned, plus one refute-driven repair loop — the advisor's refute-read (NOT-EARNED, 3 findings: exit 1 vs contracted exit 2 · whitespace note slipped the refusal · note stored stripped not verbatim) drove a code fix in `cmd_phase` and strengthened asserts via the recorded re-cross path. The five engine seams: `--note` on the phase parser · validate-then-write refusal + `_record_round` in `cmd_phase` · `_record_round` call on `_heal_or_escalate`'s non-exhausted branch · F8-mirror preserve in `new-task --force` · `round N` on the status now-row + `"rounds"` in the gate trace row.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).
- [SPEC · open] a `--note` riding a NON-verify→build entry (e.g. direction→build via --skip-freeze) is accepted then silently dropped with exit 0 — silent data loss the contract never adjudicated; decide refuse-vs-warn next pass (evidence: advisor refute-read probe P4, 2026-07-22)

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
