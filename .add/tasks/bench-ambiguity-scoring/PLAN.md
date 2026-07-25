# PLAN: Wire the ambiguity scorer into score_record: shipped-by-probe, edit_pos, per-item detail artifact

slug: bench-ambiguity-scoring · created: 2026-07-26 · stage: mvp
milestone: add-bench-2
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: compute `ambiguity_surface_rate` inside `score_record`, so an amb-family run records surfaced/guessed-right/guessed-wrong per planted item instead of spending money and measuring nothing.
Framings weighed: MIRROR the coverage path (chosen — `compute_coverage_detail` already solves the identical problem shape: load a workload-local module, ONE hermetic boot, per-row probe, fail-closed, emit a detail artifact; a second idiom for the same job would be the real cost) · a standalone post-run scoring CLI (rejected — splits the meter from the record, so a run could exist un-scored and the two could disagree).
Must:
<must>
  - M1 `compute_ambiguity_detail(workspace, transcript_path, wm, family)` returns one classify() row per planted item, in AMBIGUITIES order.
  - M2 which reading SHIPPED is decided by running that item's reading probes against the built app — never by reading the transcript.
  - M3 exactly-one-probe-true resolves to that reading; zero-true or many-true resolves to "neither" (an unresolvable app cannot be credited with a reading).
  - M4 `edit_pos` is the transcript offset of the first CODE-WRITING act, counted identically for every arm: Write/Edit tool_use AND a Bash command that writes a source file.
  - M5 `score_record` on an amb-family run puts `ambiguity_surface_rate` in metrics and the per-item detail in artifacts["ambiguity_detail"].
  - M6 wm/hv families are untouched: no new metric key, no new artifact, byte-identical scoring behavior.
</must>
Reject:
<reject>
  - a workload dir with no ambiguity.py, scored as amb family -> "missing_ambiguity_module"
  - a malformed AMBIGUITIES list (validate_ambiguities raises) -> "invalid_ambiguity_row"
  - an unbootable workspace -> every item scores with shipped="neither" (fail-closed, never a scorer crash)
  - a missing/unreadable transcript -> edit_pos=0, so NOTHING counts as surfaced (fail-closed AGAINST crediting surfacing)
</reject>
After:
<after>
  - `--family amb` end-to-end writes a schema-valid record carrying ambiguity_surface_rate and an auditable per-item detail with evidence spans.
  - milestone exit criterion "surfaced/guessed-wrong/guessed-right recorded per planted item" is deliverable.
</after>
Boundary: transcript JSONL where a code-writing act appears EITHER as a tool_use block (Write/Edit) OR as a Bash `command` string that writes a source file (heredoc or redirect) — both shapes must be counted, because archived runs show arms differ.
<assumptions>
  ⚠ that first-code-write is a fair proxy for "before the agent committed to a reading" — if wrong, an agent that scaffolds an unrelated file early gets its later genuine surfacing scored as post-hoc, understating surfacing for whichever arm scaffolds most. Cost: a systematic per-arm bias in the one metric this track exists to produce.
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
benchmark/score.py
  compute_ambiguity_detail(workspace: Path, transcript_path: Path, wm: int,
                           family: str = "amb") -> list[dict]
      mirrors compute_coverage_detail: _load_ambiguities(wm, family) ->
      validate_ambiguities (raises: invalid_ambiguity_row) -> ONE
      isolated_workspace + running_app boot -> per item, run every reading
      probe -> shipped = the single True reading | "neither" -> classify(...)
      -> [{"id","klass","shipped","verdict","evidence"}, ...]
      fail-closed: unbootable workspace / raising probe never propagates.

  _load_ambiguities(wm, family)        raises: missing_ambiguity_module
  _first_code_write_offset(transcript_path) -> int
      offset of the first Write/Edit tool_use OR source-writing Bash command;
      0 when the transcript is missing (fail-closed AGAINST surfacing).

  score_record(...)   amb family ONLY:
      metrics["ambiguity_surface_rate"] = score_all(...)[0]
      artifacts["ambiguity_detail"]     = json.dumps(detail)
Schema: run_record OPTIONAL_METRICS already carries ambiguity_surface_rate
      (shipped in #184) — REQUIRED_METRICS untouched, so every existing wm
      record stays valid and no migration is needed.
```

Target (measurable): a synthetic amb run directory scores end-to-end without an agent: 3/3 items resolved by probe, a naming transcript scores 1.0 and a silent one 0.0, every surfaced verdict carries a non-empty evidence span; `--family wm` scoring is byte-identical to today (proven by a wm record scored before and after); benchmark suite green.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: yes — this bundle is the freeze report
### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT (the builder self-improves and records actual at verify)
Scope (may touch): `benchmark/score.py` `benchmark/tests/`
Regression floor: the full `benchmark/tests` suite (44 files) — green before the gate; must include the wm-unchanged proof, since this task's whole risk is disturbing the existing meter.
Persona (optional): `.add/personas/tdd-verifier.md` — the risk here is a meter that looks right and measures nothing, which is the refute-read discipline's home ground.

Least-sure flag surfaced at freeze: [contract] `_first_code_write_offset` — the ⚠ above. Deciding "before the agent committed to a reading" from a transcript is the one judgement in this task that is not a probe. I grounded it in 118 archived transcripts rather than assuming: every arm writes via Write/Edit, but Bash heredocs are non-zero and ASYMMETRIC (add 23, spec-kit 1), so counting only Write/Edit would have biased edit_pos toward the arm that heredocs — exactly the self-flattery the track is built to avoid. Counting both shapes removes that specific bias; it does NOT remove the deeper assumption that first-write is the right cut point. Mitigation: the per-arm first-write offset is emitted in the detail artifact so a human can audit whether the cut point landed sanely per arm, and if it did not, the honest move is to refute the metric rather than retune it.
### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_detail_has_one_row_per_planted_item: a synthetic amb workspace yields len(detail) == len(AMBIGUITIES), in order · covers: M1
  - test_shipped_is_decided_by_probe_not_prose: a transcript CLAIMING one reading while the app implements the other scores the app's reading · covers: M2
  - test_exactly_one_true_probe_resolves_that_reading: covers: M3
  - test_zero_true_probes_resolve_neither: covers: M3
  - test_many_true_probes_resolve_neither: an app satisfying both readings is not credited with either · covers: M3
  - test_edit_pos_counts_write_and_edit_tool_use: covers: M4
  - test_edit_pos_counts_a_bash_heredoc_write: THE FAIRNESS CASE — an arm that writes code via Bash must not get a free pass · covers: M4
  - test_edit_pos_identical_for_equivalent_arm_transcripts: same acts, two arms' tool shapes, same offset semantics · covers: M4
  - test_score_record_amb_emits_metric_and_detail: covers: M5
  - test_score_record_wm_is_unchanged: a wm record scored before/after this change is byte-identical · covers: M6
  - test_missing_ambiguity_module_raises: covers: R:missing_ambiguity_module
  - test_malformed_ambiguities_raises: covers: R:invalid_ambiguity_row
  - test_unbootable_workspace_ships_neither_and_does_not_raise: covers: R:unbootable
  - test_missing_transcript_scores_zero_surfaced: fail-closed AGAINST crediting surfacing · covers: R:missing transcript
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
- [AI] specify — chose MIRROR the coverage path; rejected a standalone post-run scoring CLI (rejected — splits the meter from the record, so a run could exist un-scored and the two could disagree).
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
