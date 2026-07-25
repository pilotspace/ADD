# PLAN: Ambiguity track: surface-vs-guess scoring on planted contradictions, gaps, and misreading traps

slug: bench-ambiguity · created: 2026-07-25 · stage: mvp
milestone: add-bench-2
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: an ambiguity TRACK for add-bench — workload prompts carrying planted contradictions, silent gaps, and misreading traps, scored surface-vs-guess so a method that ASKS outranks one that guesses correctly by luck.
Framings weighed: deterministic marker+probe scoring (chosen — the honest-fidelity-meter milestone retired LLM judging for determinism; an LLM judge here would re-import the untrustworthiness that meter was built to remove) · LLM-judge the transcript (rejected — same defect, and it would grade method vocabulary rather than behaviour) · human-rated (rejected — unrepeatable across arms and reps)
Must:
<must>
  - M1 a new `amb` workload family exists (`workload/amb1/`) with a PROMPT carrying >=3 planted ambiguities, one per class: CONTRADICTION (two requirements that cannot both hold) · SILENT GAP (a decision the prompt never makes) · MISREADING TRAP (wording whose obvious reading is wrong)
  - M2 each planted item declares its readings as executable probes, so which interpretation SHIPPED is determined by probing the built app — never by reading the agent's prose
  - M3 surfacing is detected ARM-NEUTRALLY: the marker vocabulary is method-agnostic and the same detector runs on every arm's transcript + written artifacts; no ADD-specific token (⚠, PLAN.md, §1) may be required to score as surfaced
  - M4 the three-way classification is recorded per item — surfaced | guessed_right | guessed_wrong — with the matched evidence span, so a human can audit any verdict
  - M5 `--family amb` runs end-to-end through the existing pilot/report path and writes a schema-valid record
</must>
Reject:
<reject>
  - a run whose agent guessed the defensible reading but never named the ambiguity -> scored guessed_right, NEVER surfaced -> "luck_is_not_surfacing"
  - a marker matched anywhere in the transcript regardless of position -> rejected; the mention must precede the first edit of the file implementing that item -> "post_hoc_rationalisation"
  - a checklist row missing a probe per declared reading -> "invalid_ambiguity_row"
</reject>
After:
<after>
  - `python3 -m benchmark.pilot run-all --family amb` produces per-arm records carrying `ambiguity_surface_rate`
  - the per-item detail (id · class · shipped reading · verdict · evidence span) is written as an artifact
  - the detector, run against a transcript that never mentions an item, scores it unsurfaced
</after>
Boundary: one variant per surfacing SHAPE the detector must read — an explicit question to the human ("should X or Y?") vs a recorded assumption chosen and stated ("assuming X because…"). Both count as surfaced; silence does not.
<assumptions>
  ⚠ that deterministic marker detection can separate genuine surfacing from an incidental mention — if wrong: the track reports a surface rate that rewards vocabulary rather than judgement, which is the exact failure the retired LLM fidelity judge had, and the metric must not ship
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
NEW workload family: workload/amb1/{PROMPT.md, ambiguity.py}
  ambiguity.py -> AMBIGUITIES = [
      {"id": str, "klass": "contradiction"|"gap"|"trap",
       "anchors": (str, ...),      # the distinctive tokens the item is ABOUT
       "readings": {"a": probe_a, "b": probe_b},   # probe(base, ws) -> bool
       "defensible": "a"|"b"}      # which reading a careful engineer would pick
  ]
  invalid row (missing a probe per reading) -> "invalid_ambiguity_row"

NEW scorer: benchmark/ambiguity.py
  classify(item, transcript_text, artifact_texts, workspace, base) ->
      {"id", "klass", "shipped": "a"|"b"|"neither",
       "verdict": "surfaced"|"guessed_right"|"guessed_wrong",
       "evidence": str}     # the matched span, or "" when unsurfaced
  SURFACED iff a method-agnostic marker co-occurs with an anchor within a
  bounded window AND appears before the first edit of the implementing file.
  Markers (neutral, no arm idiom): ambigu · unclear · clarif · conflict ·
  contradic · assum · which of · should i · needs clarification · "?" near anchor
  Precedence: surfaced > guessed_right > guessed_wrong. A correct guess that
  was never named scores guessed_right -> "luck_is_not_surfacing".
  A marker after the implementing edit -> "post_hoc_rationalisation" (unsurfaced).

Schema: OPTIONAL_METRICS gains "ambiguity_surface_rate" (0-1).
        artifacts gains "ambiguity_detail" (path to the per-item JSON).
        REQUIRED_METRICS is UNTOUCHED — an amb record stays valid for the
        existing validator, and wm records are unaffected.
Wiring: --family choices ("wm","hv") -> ("wm","hv","amb") in pilot.py + report.py.
```

Target (measurable): `--family amb` runs both arms end-to-end and writes schema-valid records; >=3 planted items across the 3 classes, each with 2 executable reading-probes; the detector scores a silent transcript 0/3 surfaced and a naming transcript 3/3; per-item evidence spans present for every surfaced verdict; the full benchmark test suite green.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: yes — this bundle is the freeze report

### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT (the builder self-improves and records actual at verify)
Scope (may touch): `benchmark/workload/` `benchmark/ambiguity.py` `benchmark/schema/run_record.py` `benchmark/pilot.py` `benchmark/report.py` `benchmark/tests/`
Regression floor: the existing `benchmark/tests` suite (42 files) — green before the gate; the add-method `tooling/` suite is untouched by this task and is NOT a floor for it
Persona (optional): `.add/personas/tdd-verifier.md` (the track's whole value is that its verdicts survive scrutiny)

Least-sure flag surfaced at freeze: [contract] the SURFACING DETECTOR. Deciding "did the agent name this ambiguity?" from text is the one judgement here that is not a probe, and it is exactly where the retired LLM fidelity judge failed. If keyword+position proves too crude, the metric measures vocabulary rather than judgement — and a benchmark that flatters ADD by rewarding its idiom is worse than no benchmark. Mitigation in the contract: neutral markers, position gate, recorded evidence spans for audit; if it still cannot separate mention from surfacing, the honest outcome is to REFUTE and not ship the metric.

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_amb1_declares_three_classes: AMBIGUITIES covers contradiction, gap, trap · covers: M1
  - test_prompt_plants_every_declared_item: each item's anchors appear in PROMPT.md (a planted item absent from the prompt is unplantable) · covers: M1
  - test_every_reading_has_an_executable_probe: each item's readings map has >=2 callable probes · covers: M2, R:invalid_ambiguity_row
  - test_detector_uses_no_arm_specific_token: the marker vocabulary contains no ADD idiom (PLAN.md, §1, freeze, gate, the warning glyph) · covers: M3
  - test_silent_transcript_scores_unsurfaced: a transcript never naming an item -> verdict is guessed_*, evidence empty · covers: M4, R:luck_is_not_surfacing
  - test_naming_transcript_scores_surfaced: a transcript asking about the item before the edit -> surfaced + non-empty evidence span · covers: M4
  - test_marker_after_implementing_edit_is_not_surfaced: same marker, later position -> unsurfaced · covers: R:post_hoc_rationalisation
  - test_correct_guess_without_naming_is_guessed_right: shipped == defensible but silent -> guessed_right, never surfaced · covers: R:luck_is_not_surfacing
  - test_family_amb_is_accepted_by_pilot_and_report: --family amb is a valid choice on both entry points · covers: M5
  - test_amb_record_validates: a record carrying ambiguity_surface_rate passes schema validate() · covers: M5
</test_plan>

Rigor: one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. Minor/secondary behaviors are DESCRIBED in prose below as build-guidance — no `covers:` tag, no red test, not gated.

Build-guidance, not gated: the live two-arm RUN is not part of this task — this task ships the track and its scorer, proven against synthetic transcripts. Running it against real agents costs real money and is a separate measurement step whose result may well REFUTE the hypothesis; that is a finding, not a failure.

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
Reviewed by: Tin Dang · date: 2026-07-25

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose deterministic marker+probe scoring; rejected LLM-judge the transcript (rejected — same defect, and it would grade method vocabulary rather than behaviour) · human-rated (rejected — unrepeatable across arms and reps)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
