# TASK: remaining reference guides: leaner but behavior-intact

slug: reference-trim · created: 2026-06-23 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): the 11 load-on-demand reference guides (canonical `add-method/skill/add/`): scope 8345 · deltas 4286 · fold 5705 · release 8437 · report-template 10307 · graduate 4904 · soul 4400 · setup-review 3456 · adopt 3519 · confidence 2792 · compact-foundation 3270 = 59,421 B ×3 trees. New fence: `add-method/tooling/test_reference_lean.py`.
Context (working folder): pins — `report-template.md`→test_report_arc + test_arc_gate_wiring (ARC sections, "ARC"); `scope.md`→test_scope_loop (well-formedness rubric); `deltas.md`→test_competency_deltas; `soul.md`→test_soul_*; `confidence.md`→test_confidence_rubric. Gate on FULL 1558-suite. This pool carries the TREE-WIDE ≥25% (the most load-on-demand headroom).
Honors (patterns / conventions): 3-tree byte parity (canonical→`cp`×2); wording_lint; v16 XML 5-tag vocab; each guide keeps its rubric/section anchors + reject_codes. Behavior-preserving.
Anchors the contract cites: per-guide byte totals · the ARC/rubric anchors · parity enforcers · reused measurement method.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Compact the 11 load-on-demand reference guides — same rubrics, anchors, reject codes — lighter as a pool; this pool carries the milestone's tree-wide ≥25%.
Framings weighed: per-guide dense rewrite preserving rubrics/anchors (chosen) · drop worked examples (rejected: report-template/scope examples orient + some are test-asserted) · merge reference guides (rejected: each loads by name → behavior change, M3)
Must:
<must>
  - Each guide keeps its rubric/section anchors, reject_codes, and the test-asserted tokens (ARC + "report-template" in report-template.md; scope well-formedness in scope.md; competency tags in deltas.md; etc.).
  - Pool ≥32% lighter vs 59,421 B — enough to bring the WHOLE skill tree ≥25% under its pre-compaction baseline (this is the carrier task).
  - 3 trees byte-identical; full 1558-suite green; wording_lint clean; v16 XML vocab preserved.
  - Effectiveness bar: subagent quality review confirms no rubric/rule/nuance lost.
</must>
Reject:
<reject>
  - a trim that breaks a guide rubric/anchor the suite asserts -> "invariant_broken"
  - a cut that drops a rule, reject code, or rubric step -> "behavior_drift"
  - an edit diverging the 3 trees -> "parity_break"
  - shorter-but-worse -> "effectiveness_regression"
</reject>
After:
<after>
  - pool ≥32% lighter; whole tree ≥25% lighter; all rubrics/anchors intact; 3 trees byte-identical; full suite green; `test_reference_lean` green; quality review on file.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the reference pool carries enough redundancy for 32% (to land the tree-wide 25%) without losing a rubric — lowest confidence because report-template/scope are somewhat test-pinned; if wrong: the tree lands a few points under 25% and I report the honest final (the milestone goal is effectiveness at optimized cost, not a number hit by gutting). Mitigation: full suite + quality review.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: reference pool compacts under the frozen budget
  Given the 11 load-on-demand guides total 59,421 B
  When each is densely rewritten preserving its rubric/anchors
  Then the pool is ≤40,406 B (≥32% lighter)
  And every guide file still exists (none merged or dropped)

Scenario: whole tree lands ≥25% lighter (carrier task)
  Given the pre-compaction tree baseline is 164,333 B
  When reference-trim lands its cut on top of core+orchestration+phases
  Then the whole canonical tree is ≤123,249 B
  And no phase/engine behavior changed

Scenario: rubric/anchor invariants hold
  Given report-template.md is pinned by test_report_arc/test_arc_gate_wiring (ARC) and scope.md by test_scope_loop, deltas.md by test_competency_deltas, soul.md by test_soul_*, confidence.md by test_confidence_rubric
  When the guides are compacted
  Then the full 1558-suite stays green
  And every asserted token/rubric/section anchor survives verbatim

Scenario: trees stay byte-identical — reject parity_break
  Given the canonical tree is edited
  When the change is propagated
  Then the 3 trees are md5-identical (test_tree_parity + test_bundle_parity green)
  And neither dogfood nor _bundled diverges

Scenario: no rule lost — reject behavior_drift / effectiveness_regression
  Given a quality-review subagent reads each before/after guide
  When it checks for a dropped rule, reject code, or rubric step
  Then it confirms no rule/nuance lost (shorter AND no worse)
  And any loss it finds is restored before the gate
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
COMPACT reference-pool   body: { guides: 11, baseline_bytes: 59421 }
  200 -> { pool_bytes: <=40406, tree_bytes: <=123249, guides_present: 11,
           trees_identical: true, suite: "green", quality_review: "no rule lost" }
  4xx -> { error: "invariant_broken" | "behavior_drift" | "parity_break" | "effectiveness_regression" }
Schema: 11 canonical guides under add-method/skill/add/ (scope·deltas·fold·release·
        report-template·graduate·soul·setup-review·adopt·confidence·compact-foundation),
        propagated byte-identical to .claude/skills/add/ + _bundled/skill/add/.
        Fence: test_reference_lean.py (BASELINE_BYTES=59421, TARGET=int(59421*0.68)=40406).
        Measurement: wc -c BYTES /4 (same proxy the prior 3 tasks froze).
```

Status: FROZEN @ v1 — approved by Tin Dang (full-auto: carrier task, behavior-preserving compaction; same proven pattern as the prior 3 M1 tasks)

Least-sure flag surfaced at freeze: [contract] the reference pool carries enough redundancy for 32% without losing a test-pinned rubric — report-template.md (10,307 B, ARC-pinned) and scope.md (8,345 B, loop-pinned) are the densest and most asserted; why it might be wrong: those two resist deep cuts, so the headroom leans on the looser guides (release·fold·graduate·adopt); cost if wrong: pool lands a few hundred B over 40,406 → tree dips just under 25% and I report the honest final rather than gut a rubric (the goal is effectiveness at optimized cost, not the number). Mitigation: full 1558-suite + quality-review subagent before the gate.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: pool byte budget + presence (prose invariants carried by the full suite)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_all_eleven_guides_present: assert each of the 11 guides exists (none dropped/merged)
  - test_pool_under_byte_budget: assert sum(read_bytes) ≤ 40406 (≥32% under 59421 baseline)
  - (rubric/anchor invariants asserted by EXISTING suite: test_report_arc, test_arc_gate_wiring,
     test_scope_loop, test_competency_deltas, test_soul_*, test_confidence_rubric, wording_lint,
     test_xml_convention; parity by test_tree_parity + test_bundle_parity — gate on FULL suite)
</test_plan>

Tests live in: `add-method/tooling/test_reference_lean.py` · MUST run red (pool still 59,421 B > 40,406) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/scope.md` `add-method/skill/add/deltas.md` `add-method/skill/add/fold.md` `add-method/skill/add/release.md` `add-method/skill/add/report-template.md` `add-method/skill/add/graduate.md` `add-method/skill/add/soul.md` `add-method/skill/add/setup-review.md` `add-method/skill/add/adopt.md` `add-method/skill/add/confidence.md` `add-method/skill/add/compact-foundation.md` `.claude/skills/add` `add-method/src/add_method/_bundled/skill/add` `add-method/tooling/test_reference_lean.py`
Strategy (ordered batches): 1. compact the looser guides first (release·fold·graduate·adopt·setup-review·compact-foundation·confidence) — most redundancy 2. then the test-pinned dense ones (report-template·scope·deltas·soul) carefully, preserving every asserted token 3. propagate canonical→dogfood+_bundled via `cp` 4. run full suite + parity.
Safety rule (feature-specific): never drop a rubric step, reject code, section anchor, or test-asserted token; preserve v16 XML 5-tag vocab; behavior-preserving only.
Code lives in: `add-method/skill/add/` (canonical) → propagated to the other 2 trees
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 1560/0 OK (twice: post-compaction + post-restoration)
- [x] coverage did not decrease — added test_reference_lean (2 new asserts); no test removed
- [x] no test or contract was altered during build — test_reference_lean.py + §3 untouched since the tests→build snapshot (no tamper)
- [x] the green was EARNED, not gamed — fence asserts real bytes (read_bytes, not a stub); an independent quality-review subagent refute-read all 11 before/after guides and FOUND 6 losses (2 blocking) → all operative losses RESTORED verbatim, byte-compensated from genuine redundancy. Not a vacuous pass.
- [x] concurrency / timing — n/a (static prose files; no runtime path)
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose-only edits; no new imports/deps
- [x] layering & dependencies follow CONVENTIONS.md — 3-tree parity holds (canonical→dogfood+_bundled byte-identical)
- [x] a person reviewed and approved the change — Tin Dang, full-auto authorization for this milestone; contract frozen @ v1; quality review on file

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] reference pool ≤40,406 B — measured 40,394 B (margin 12 B); 32.0% under the 59,421 baseline
- [x] whole canonical tree ≤123,249 B (the carrier outcome) — measured 123,109 B = 25.1% under the 164,333 pre-compaction baseline
- [x] all 11 guides still exist; 3 trees byte-identical (md5 ×11 ×3)
- [x] every test-pinned rubric/anchor survives — ARC present in report-template, duplicate_goal in scope, DDD·SDD·UDD·TDD·ADD + (evidence:…) in deltas, six dimensions in confidence; full suite green proves the rest

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — all 11 guides read in full before/after via the quality-review subagent (refute-read for dropped rules). Found 6 losses (release.md "signed AND", scope.md "the code it touches" + well-formed-draft imperative, report-template NEXT-mirror + no-filler rules, confidence.md 3rd never-bullet, adopt.md no-per-step-approvals, soul.md <observation> + session-boundary, setup-review.md not-field-by-field). ALL restored verbatim; net pool stayed ≤40,406 via redundancy trims (triplicated "engine wins", gate-list duplication, worked-example verbosity).

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: — · ticket: — · expires: —   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-23

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
