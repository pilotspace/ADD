# PLAN: Fix three scorer defects that all penalise document-first methods (artifacts unread, cross-item attribution, plan-write closes window)

slug: ambiguity-meter-fixes · created: 2026-07-26 · stage: mvp
milestone: add-bench-2
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: fix three scorer defects the first live run exposed — all three penalise methods that think ON DISK rather than in chat, and together they produced a 1.0-vs-0.0 gap that is substantially an artifact of the instrument.
Framings weighed: FIX ALL THREE BEFORE ANY MORE SPEND (chosen — more reps of a biased meter buy more confident wrong numbers) · publish rep 0 with caveats (rejected — a caveat under a headline number is read as the number) · drop the metric (rejected — the defects are in the wiring, not the idea, and each has a concrete fix validated against live evidence).
Must:
<must>
  - M1 compute_ambiguity_detail passes the workspace's WRITTEN artifacts to classify, not an empty tuple — a method that surfaces in a document scores like one that says it in chat.
  - M2 one evidence sentence credits AT MOST ONE item: the one with the most anchor matches; a tie credits nobody.
  - M3 the surfacing window closes on the first IMPLEMENTATION write, not the first write of any kind — writing an analysis document is the act of surfacing, not of committing to a reading.
  - M4 the implementation/analysis split is ARM-NEUTRAL: decided by file kind (code vs prose), never by a path any one method owns.
  - M5 re-scoring the archived rep-0 workspaces yields a defensible per-item verdict for BOTH arms, and the detail records which artifact carried each surfacing.
</must>
Reject:
<reject>
  - crediting an item from a sentence that surfaced a DIFFERENT item -> "misattributed_surfacing"
  - counting a markdown/plan write as the commitment point -> "analysis_counted_as_commitment"
  - an artifact allow-list naming .add/ or .specify/ -> "arm_specific_path"
</reject>
After:
<after>
  - re-scoring rep 0 costs nothing and produces numbers whose per-item verdicts survive reading.
  - reps 1-2 become worth paying for.
</after>
Boundary: a workspace tree containing BOTH prose artifacts (*.md, any depth) and implementation code (*.py and friends) — the two must be told apart without naming any method's directory.
<assumptions>
  ⚠ that "code file vs prose file" is a fair proxy for "committing vs still deciding". A method that writes executable scaffolding early while still reasoning would have its window closed early; a method that writes prose forever would keep an unbounded window. Cost: the cut-point still favours prose-first methods, just less crudely than today.
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
benchmark/ambiguity.py
  score_all(...)/classify(...)   unchanged signature; attribution added:
    _attribute(sentence, items) -> item_id | None
      the item with the MOST anchor matches wins; a TIE credits nobody,
      because an unattributable recognition is not evidence about any one
      item. Validated on the live rep-0 sentence: conflict-response 4
      matches, priority 1, position 1 -> credits conflict-response only
      (today that one sentence credits all three, 1/3 read as 3/3).

  CODE_SUFFIXES / _is_implementation_write(path) -> bool
    prose (.md/.rst/.txt) is ANALYSIS; code (.py/.js/.ts/.go/...) is
    COMMITMENT. Decided by file KIND, never by a directory any method owns
    (R:arm_specific_path).

benchmark/score.py
  _first_code_write_offset(...)  -> only IMPLEMENTATION writes close the window
  _workspace_artifacts(workspace, *, limit) -> list[str]
      the workspace's prose documents, so a document-first method is read
      (M1). Bounded and deterministic (sorted) so scoring stays reproducible.
  compute_ambiguity_detail(...)  -> classify(..., artifacts=_workspace_artifacts(ws))
      detail rows gain "source": "transcript" | "artifact"
```

Target (measurable): re-scoring the two archived rep-0 workspaces (zero spend) gives ADD >=1 surfaced with its PLAN.md contradiction paragraph as evidence, gives spec-kit exactly 1 surfaced (its contradiction sentence, no longer credited to the priority and position items), every surfaced row names the artifact that carried it, and no probe path names `.add` or `.specify`; benchmark suite green.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: yes — this bundle is the freeze report
### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT (the builder self-improves and records actual at verify)
Scope (may touch): `benchmark/ambiguity.py` `benchmark/score.py` `benchmark/tests/`
Regression floor: the full `benchmark/tests` suite — green before the gate.
Persona (optional): `.add/personas/tdd-verifier.md`

Least-sure flag surfaced at freeze: [spec] the ⚠ above — that file KIND is a fair proxy for "committing versus still deciding". It is better than today's rule, which counts a method's own planning document as its commitment, but it is not neutral either: a method that scaffolds executable stubs while still reasoning gets an early cut-point, and one that reasons in prose indefinitely keeps an unbounded window. I am the party with an interest in this landing favourably, and all three of today's defects happened to point the same way, so the mitigation is disclosure rather than confidence: each detail row records WHICH artifact carried the surfacing, so a reader can see whether a verdict rests on chat or on a document, and re-scoring is free — the numbers can be re-derived by anyone from the archived workspaces.
### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_artifacts_are_passed_to_classify: compute_ambiguity_detail reads workspace prose · covers: M1
  - test_document_only_surfacing_scores: surfacing present ONLY in a workspace .md scores surfaced · covers: M1
  - test_one_sentence_credits_at_most_one_item: covers: M2, R:misattributed_surfacing
  - test_best_anchor_match_wins_attribution: the live rep-0 sentence credits conflict-response only · covers: M2
  - test_tie_credits_nobody: equal anchor matches surface neither · covers: M2
  - test_markdown_write_does_not_close_the_window: covers: M3, R:analysis_counted_as_commitment
  - test_code_write_closes_the_window: covers: M3
  - test_split_names_no_arm_specific_path: source scan for `.add` / `.specify` / `constitution` · covers: M4, R:arm_specific_path
  - test_rescoring_add_rep0_finds_the_plan_contradiction: covers: M5
  - test_rescoring_speckit_rep0_yields_exactly_one: covers: M5
  - test_detail_rows_name_their_source: covers: M5
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
- [AI] specify — chose FIX ALL THREE BEFORE ANY MORE SPEND; rejected publish rep 0 with caveats (rejected — a caveat under a headline number is read as the number) · drop the metric (rejected — the defects are in the wiring, not the idea, and each has a concrete fix validated against live evidence).
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
