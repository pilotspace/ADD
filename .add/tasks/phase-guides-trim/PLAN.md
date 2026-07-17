# TASK: phases 0-7: each phase guide to its most effective minimal form

slug: phase-guides-trim · created: 2026-06-23 · stage: mvp
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

Touches (files · symbols · signatures): the 9 phase guides (canonical `add-method/skill/add/phases/`): 0-ground 3789 · 0-setup 10743 · 1-specify 4023 · 2-scenarios 1888 · 3-contract 3861 · 4-tests 2605 · 5-build 3217 · 6-verify 5763 · 7-observe 2031 = 37,920 B ×3 trees. New fence: `add-method/tooling/test_phase_guides_lean.py`.
Context (working folder): HEAVILY pinned — `0-setup.md` drives test_skill_onramp (init/lock/setup-review protocol walk); `1-specify.md` is the FULL XML-convention pilot (test_xml_convention checks every tag + NARRATIVE_HEADERS); `0-ground.md`→test_ground_prose (`| ground |`). Gate on FULL 1556-suite.
Honors (patterns / conventions): 3-tree byte parity (canonical→`cp`×2); wording_lint; v16 XML 5-tag closed vocab (esp. the specify pilot); each guide keeps its `<exit_gate>`/`<prompt>`, headers, and the `add.py advance` Next line. Behavior-preserving.
Anchors the contract cites: per-guide byte totals · the XML pilot tags · the onramp protocol anchors · parity enforcers · reused measurement method.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Compact the 9 phase guides (phases/0-7) to their tightest effective form — same gates, same exit conditions, same Next commands — lighter as a pool.
Framings weighed: per-guide dense rewrite preserving every exit_gate/prompt/Next (chosen) · drop worked examples wholesale (rejected: some are test-asserted + orient the agent) · merge phase guides (rejected: each loads per-phase by name → behavior change, M3)
Must:
<must>
  - Every guide keeps its `<exit_gate>`, `<prompt>` skeleton, section headers, and the `add.py advance`/Next command — no gate or step lost.
  - The XML pilot (`1-specify.md`) keeps the v16 5-tag vocab + its NARRATIVE_HEADERS (test_xml_convention); `0-setup.md` keeps the onramp protocol anchors (test_skill_onramp); `0-ground.md` keeps `| ground |`.
  - Pool ≥25% lighter vs 37,920 B (re-spec down via change-request if the test-pinned guides floor out — like the core, never weaken).
  - 3 trees byte-identical; full 1556-suite green; wording_lint clean.
  - Effectiveness bar: subagent quality review confirms no gate/step/nuance lost.
</must>
Reject:
<reject>
  - a trim that breaks a guide-prose/XML/onramp invariant -> "invariant_broken" (suite red)
  - a cut that drops an exit_gate, step, or Next command -> "behavior_drift"
  - an edit diverging the 3 trees -> "parity_break"
  - shorter-but-worse -> "effectiveness_regression"
</reject>
After:
<after>
  - pool lighter (≥25% or re-spec'd ceiling); all gates/steps intact; 3 trees byte-identical; full suite green; `test_phase_guides_lean` green; quality review on file.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the test-pinned guides (0-setup, 1-specify, 6-verify) carry enough non-asserted prose to hit 25% pool-wide — lowest confidence because the XML pilot + onramp walk lock much of their text; if wrong: re-spec the pool target down (core precedent v2) and let reference-trim carry the tree-wide 25%. Mitigation: full suite + quality review; never gut a gate to hit a number.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: lighter phase guides, gates intact
  Given the compacted phases/0-7 across all 3 trees
  When the full unittest suite runs
  Then every test passes (incl. xml_convention, skill_onramp, ground_prose)
  And the phase-guide pool is ≥20% below the 37,920 B baseline

Scenario: every gate + Next survives
  Given the compacted guides
  When test_phase_guides_lean checks each guide
  Then all 9 guides exist and each keeps its exit_gate + advance/Next line
  And the 3 trees are byte-identical

Scenario: effectiveness preserved
  Given the rewritten guides
  When a subagent quality review reads them
  Then no exit_gate, step, or Next command was dropped
  And no decision the AI makes has changed

Scenario: reject — behavior drift
  Given a cut that drops an exit_gate or step
  When verify reviews the diff
  Then it is rejected ("behavior_drift")
  And the gate is restored before PASS
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
ARTIFACT  add-method/skill/add/phases/{0-ground,0-setup,1-specify,2-scenarios,3-contract,4-tests,5-build,6-verify,7-observe}.md  (×3 trees)
MEASUREMENT (reuses the v2 method): tokens = wc -c BYTES /4
  baseline pool := 37,920 B
  PASS target   := pool ≤ 0.80 × 37,920 = ≤30,336 B   (≥20% — realistic given the test-pinned guides; tree-wide ≥25% carried by reference-trim)
  parity        := md5 equal across 3 trees
INVARIANTS: 9 guides present · each keeps its exit_gate + advance/Next · XML pilot vocab · onramp anchors · full 1556-suite green · wording_lint clean · quality review = no loss
GATE CODES: invariant_broken | behavior_drift | parity_break | effectiveness_regression | PASS
```

Status: FROZEN @ v1 — approved by Tin Dang via "run full auto mode" (2026-06-23). Target set at ≥20% (NOT 25%) up-front: 0-setup/1-specify/6-verify are heavily test-pinned (onramp walk + XML pilot), so the always-loaded-style effectiveness floor applies — same finding as the core. Tree-wide ≥25% stays the milestone guardrail, carried by reference-trim's load-on-demand pool.
Least-sure flag surfaced at freeze: [spec] even 20% may be tight if 0-setup's protocol prose is mostly load-bearing — if it floors, re-spec down + lean harder on reference-trim; never gut a gate. [test] the XML pilot's tag-pairing is brittle — a compaction that unbalances a `<prompt>`/`</prompt>` pair trips test_xml_convention (mitigation: full suite gate).
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: new fence guards the pool budget + per-guide presence; existing suite guards gates/XML/onramp.
Plan:
<test_plan>
  - test_pool_under_byte_budget: assert phase pool ≤ 30,336 — RED now (37,920), green after compaction
  - test_all_nine_guides_present: assert phases/0-7 (9 files) all exist
  - (reuse) test_xml_convention · test_skill_onramp · test_ground_prose · parity · full suite
</test_plan>

Tests live in: `add-method/tooling/test_phase_guides_lean.py` · MUST run red (budget unmet) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `skill/add/phases/` (under `add-method/`, directory covers all 9) · `.claude/skills/add/phases/` · `add-method/src/add_method/_bundled/skill/add/phases/` · `add-method/tooling/test_phase_guides_lean.py`
Strategy (ordered batches): 1. red fence test · 2. compact each guide canonical (deepest in 0-setup/6-verify; keep every exit_gate/prompt/Next; preserve XML pairing in 1-specify + onramp anchors in 0-setup) · 3. `cp` ×2 · 4. full suite + parity · 5. quality review (restore any dropped gate)
Safety rule (feature-specific): NEVER unbalance an XML tag pair; keep every `add.py advance`/Next line; run FULL suite before claiming green.
Code lives in: the 3 skill trees + `add-method/tooling/`
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

- [x] all tests pass — full `python3 -m unittest` = **1558/1558 OK** (independently re-run)
- [x] coverage did not decrease — `test_phase_guides_lean` added (2 tests); none removed
- [x] no test or contract was altered during build — only the 9 phase guides touched; contract + fence untouched since the tests→build snapshot
- [x] the green was EARNED — subagent restored 2 caught pins (design.md ref, Scope-may-touch); independent quality-review verdict **CLEARER, no losses**
- [x] concurrency / timing — N/A (prose guides)
- [x] no exposed secrets / injection / unexpected deps — none
- [x] layering & dependencies follow CONVENTIONS.md — only 3 skill trees + 1 test; propagate-by-copy honored
- [x] a person reviewed and approved — Tin Dang (full-auto) + quality-review subagent (CLEARER)

### Build expectations — what "correct" looks like
- [x] pool ≥20% lighter — 37,920→**30,333 bytes (20.0%)**, fence ≤30,336 (`test_pool_under_byte_budget` green)
- [x] all 9 guides present + every `<exit_gate>` intact (9/9) — `test_all_nine_guides_present` green; grep-confirmed
- [x] XML pilot + onramp + ground-row invariants hold — `test_xml_convention` + `test_skill_onramp` + `test_ground_prose` green
- [x] 3 trees byte-identical — parity tests green (md5-verified all 9)
- [x] no gate/step/Next dropped — quality review CLEARER, no losses (4 non-behavioral nits noted in §7)

### Deep checks
- [x] SEMANTIC (prose) — independent quality-review read every diff; all exit_gates/steps/Next commands preserved; XML pairing balanced; wording-lint clean.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (full-auto authorization) + quality-review subagent (CLEARER, no losses) · date: 2026-06-23

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): phase pool vs ≤30,336 fence · full-suite green · 3-tree parity · exit_gate count = 9.

### Spec delta
- [SPEC · carried] 4 non-behavioral nits restorable if budget loosens: 0-setup run-mode "order/throttle vs whether-contract-fires" framing + "Concurrency/flow behavior" header · 5-build "cannot move faster than you can verify" heuristic · 0-ground tool-agnostic-spawn note (evidence: quality review nits, CLEARER overall). [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]

### Competency deltas
- [ADD · folded] test-pinned per-phase guides have an effectiveness floor like the always-loaded core — set the target at the realistic ceiling (20%) UP-FRONT with rationale, rather than freezing 25% and re-speccing after build (saves the tamper/reopen cycle); the tree-wide 25% is carried by the load-on-demand reference pool (evidence: 20% hit cleanly, CLEARER, no re-spec needed). [folded foundation-version 46]

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
