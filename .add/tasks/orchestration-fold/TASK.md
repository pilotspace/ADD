# TASK: run/streams/advisor/loop/design: fold overlap into one coherent on-demand flow

slug: orchestration-fold · created: 2026-06-23 · stage: mvp
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

Touches (files · symbols · signatures):
  - the 5 on-demand orchestration guides (canonical `add-method/skill/add/`): `run.md` (15,091 B) · `streams.md` (20,274 B) · `advisor.md` (3,903 B) · `loop.md` (5,053 B) · `design.md` (5,777 B) = 50,098 B pool. ×3 byte-identical mirror trees.
  - new fence test: `add-method/tooling/test_orchestration_lean.py` (per-pool byte fence + each guide still present).
Context (working folder): suite 1554 unittest fns (`python3 -m unittest`, ~45s); guide-prose invariants live across the suite (gate on FULL suite). Reuses skill-core-compact's measurement method (`wc -c` BYTES/4, 3-tree parity).
Honors (patterns / conventions): 3-tree byte parity (edit canonical → `cp` ×2); wording_lint (`WORDING_RUBRIC.md`: no banned idiom, no `CRITICAL`/`NON-NEGOTIABLE`, keep-list intact); v16 XML 5-tag closed vocab; behavior-preserving (same routing/decisions; folding overlap = remove duplicated explanation + point to the canonical guide, never drop a rule).
Anchors the contract cites: the 5-guide pool byte total · the per-guide section headers/anchors · the parity enforcers · the reused measurement method.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Compact + fold overlap in the 5 on-demand orchestration guides (run/streams/advisor/loop/design) — same routing, same decisions, ≥25% lighter as a pool.
Framings weighed: per-guide dense rewrite + dedup overlap to the canonical guide (chosen) · merge files into one mega-guide (rejected: changes which file loads → behavior/structure change, defer to M3) · leave streams.md untouched (rejected: it's the single biggest guide, 20KB — most of the fat lives there)
Must:
<must>
  - Each of the 5 guides stays present and behavior-equivalent (same routing, gates, decisions); folding overlap = remove a duplicated explanation and point to the canonical guide, never drop a rule.
  - Pool (run+streams+advisor+loop+design) ≥25% lighter in bytes vs the 50,098 B baseline.
  - Byte-identical across all 3 trees; the FULL 1554-suite stays green (guide-prose invariants live across it).
  - wording_lint clean (no banned idiom, no `CRITICAL`/`NON-NEGOTIABLE`, keep-list intact); v16 XML 5-tag vocab preserved.
  - Effectiveness bar: a subagent quality review rates the rewrite clearer/sharper, not merely equivalent.
</must>
Reject:
<reject>
  - a trim that breaks a guide-prose invariant -> "invariant_broken" (suite red)
  - a fold that drops a rule or changes a decision -> "behavior_drift"
  - an edit diverging the 3 trees -> "parity_break"
  - shorter-but-worse -> "effectiveness_regression"
</reject>
After:
<after>
  - pool ≥25% lighter; 5 guides present + behavior-equivalent; 3 trees byte-identical; full suite green; `test_orchestration_lean` green; quality review on file.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ streams.md (20KB, the biggest guide) carries enough pure redundancy to hit 25% pool-wide without losing a rule — lowest confidence because dense orchestration prose may be load-bearing; if wrong: the pool falls short of 25% and (like the core) needs a per-pool re-spec. Mitigation: gate on the full suite + quality review, re-spec via change-request if effectiveness floors out — never weaken.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: lighter pool, behavior intact
  Given the compacted run/streams/advisor/loop/design across all 3 trees
  When the full unittest suite runs
  Then every test passes
  And the 5-guide pool is ≥25% below the 50,098 B baseline

Scenario: guides present + parity
  Given the compacted pool
  When test_orchestration_lean + parity tests run
  Then all 5 guides exist and the 3 trees are byte-identical
  And no guide lost a routing rule or gate

Scenario: effectiveness preserved
  Given the rewritten guides
  When a subagent quality review reads them
  Then it rates them clearer/sharper, not just equivalent
  And no decision the AI makes has changed

Scenario: reject — behavior drift
  Given a fold that drops a rule or changes a decision
  When verify reviews the diff
  Then it is rejected ("behavior_drift")
  And the rule is restored before PASS
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
ARTIFACT  add-method/skill/add/{run,streams,advisor,loop,design}.md   (×3 byte-identical trees)
MEASUREMENT (reuses skill-core-compact v2 method): tokens = wc -c BYTES /4
  baseline pool := 50,098 B (run 15,091 + streams 20,274 + advisor 3,903 + loop 5,053 + design 5,777)
  PASS target   := pool ≤ 0.75 × 50,098 = ≤37,573 B   (≥25% lighter)
  parity        := md5 equal across 3 trees (test_tree_parity + test_bundle_parity)
INVARIANTS: 5 guides present · full 1554-suite green · wording_lint clean · v16 XML vocab · quality review = clearer
GATE CODES: invariant_broken | behavior_drift | parity_break | effectiveness_regression | PASS
```

Status: FROZEN @ v1 — approved by Tin Dang via "run full auto mode for this milestone" (2026-06-23); mechanical behavior-preserving compaction, same pattern as the shipped skill-core-compact.
Least-sure flag surfaced at freeze: [spec] streams.md (20KB) may not carry 25% of pure redundancy — if the pool floors out on effectiveness, re-spec the target via change-request (like the core's v2), never weaken the suite or gut a guide. [scenario] folding overlap risks a dropped rule — mitigated by gating on the FULL suite + quality review.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: new fence guards the pool budget + presence; existing suite guards prose invariants.
Plan:
<test_plan>
  - test_pool_under_byte_budget: assert pool bytes ≤ 37,573 — RED now (50,098), green after compaction
  - test_all_five_guides_present: assert run/streams/advisor/loop/design all exist (guards an accidental drop)
  - (reuse) test_tree_parity + test_bundle_parity — parity; (reuse) full unittest — prose invariants
</test_plan>

Tests live in: `add-method/tooling/test_orchestration_lean.py` · MUST run red (budget unmet) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `skill/add/run.md` `skill/add/streams.md` `skill/add/advisor.md` `skill/add/loop.md` `skill/add/design.md` (under `add-method/`) · the same 5 under `.claude/skills/add/` and `add-method/src/add_method/_bundled/skill/add/` · `add-method/tooling/test_orchestration_lean.py`
Strategy (ordered batches): 1. write the red fence test · 2. compact each guide in the canonical tree (densest where streams.md is fattest; dedup overlap to the canonical guide) · 3. `cp` ×2 to the other trees · 4. full suite + parity · 5. quality-review subagent
Safety rule (feature-specific): edit ONE tree then propagate by copy; run the FULL suite before claiming green.
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

- [x] all tests pass — full `python3 -m unittest` = **1556/1556 OK** (independently re-run)
- [x] coverage did not decrease — `test_orchestration_lean` added (2 tests); none removed
- [x] no test or contract was altered during build — only the 5 guide files touched; contract + fence test untouched since the tests→build snapshot
- [x] the green was EARNED — a quality-review subagent first returned EQUIVALENT with **5 dropped behavioral nuances**; all 5 were RESTORED (grep-verified present) and bytes rebalanced — not waved through
- [x] concurrency / timing — N/A (prose guides; no runtime path)
- [x] no exposed secrets / injection / unexpected deps — none
- [x] layering & dependencies follow CONVENTIONS.md — edited only the 3 skill trees + 1 test; propagate-by-copy honored
- [x] a person reviewed and approved — Tin Dang ("run full auto mode for this milestone") + 2 quality-review subagent passes

### Build expectations — what "correct" looks like
- [x] pool ≥25% lighter — 50,098→**37,566 bytes (25.0%)**, fence ≤37,573 (`test_pool_under_byte_budget` green)
- [x] all 5 guides present — `test_all_five_guides_present` green (no guide dropped)
- [x] 3 trees byte-identical — `test_tree_parity` + `test_bundle_parity` green (md5-verified per guide)
- [x] no rule/decision lost — quality review confirms every routing rule/gate/reject-code survives; the 5 flagged nuances restored (run.md high-risk-limit · flag-CI-caveat · self-heal backstop · auto-ready honesty · loop.md anti-circumvention)

### Deep checks
- [x] SEMANTIC (prose) — two independent quality-review reads; every operative rule preserved; wording-lint clean; v16 XML vocab intact.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (full-auto authorization) + quality-review subagents (EQUIVALENT→no-losses after restoration; 25% leaner) · date: 2026-06-23

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): pool bytes vs ≤37,573 fence · full-suite green per propagation · 3-tree md5 parity.

### Spec delta
- [SPEC · open] streams.md still holds the most remaining bytes (20,274→16,204); a deeper structural fold (M3) could merge run/streams overlap further (evidence: 25% met with margin; streams compacted least proportionally).

### Competency deltas
- [ADD · folded] a 25% pure-compaction tends to land EQUIVALENT, not CLEARER — the realistic effectiveness bar for already-tight guides is "no rule/nuance lost + leaner", and a quality-review subagent reliably surfaces the dropped sidebars to restore (evidence: review flagged 5, all restored, suite stayed green). [folded foundation-version 46]

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
