# TASK: Derive test_skill_lean TREE_BASELINE_BYTES from the pool baselines (kill the drift class)

slug: lean-tree-baseline-derive · created: 2026-06-25 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. Multi-component repo (monorepo/multi-repo)? add a `component: <name>` line (declared in `.add/components.toml`) to ADD that component's root to your §5 Scope; omit for single-component projects (byte-identical default). -->
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
  - `add-method/tooling/test_skill_lean.py:TREE_BASELINE_BYTES` — today a hand-maintained sum literal (`18049 + 50098 + 37920 + 65756 + 1291` = 173114) that LAGS the four POOLS baselines (live sum = 173916, drift 802). The drift class: every pool rebaseline must ALSO be hand-added here, and the components are already stale vs the live pools (e.g. phases 37920 vs the pool's 39008). THE fix site.
  - `add-method/tooling/test_skill_lean.py:POOLS` — the four pools, each with a per-pool `baseline` (core 18465 · orchestration 50098 · phases 39008 · reference 66345). The single source of truth the tree budget should DERIVE from.
  - `add-method/tooling/test_skill_lean.py:TREE_TARGET_BYTES` — `int(TREE_BASELINE_BYTES * 0.75)`; its inline comment (`≤129835`) is already stale.
  - `add-method/tooling/test_skill_lean.py:SkillLeanTest.test_tree_under_byte_budget` — the consumer; reads TREE_TARGET_BYTES. Behavior unchanged (the whole-tree guardrail stays ≥25% under).
Context (working folder):
  - Single tree: `test_skill_lean.py` is a tooling test, NOT mirrored ×3 (no _bundled/.claude copy) → no parity sync, no ENGINE_MD5 (engine untouched).
  - fv51-folded method: pools rebaseline by surface÷ratio on approved additions — that's WHY pool baselines grow and the hand-summed tree constant drifts behind.
Honors (patterns / conventions):
  - Keep the whole-tree guardrail's INTENT (≥25% under baseline); only change HOW the baseline is computed (derive, don't hand-sum). The 0.75 ratio is kept.
  - Red/green TDD; no engine change.
Anchors the contract cites: `TREE_BASELINE_BYTES` · `POOLS` (its `baseline` keys) · `TREE_TARGET_BYTES`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: derive `TREE_BASELINE_BYTES` from the live POOLS baselines (`sum(p["baseline"] for p in POOLS)`) instead of a hand-maintained sum literal — so a pool rebaseline AUTOMATICALLY updates the tree budget and the two can never drift again.
Framings weighed: derive-from-pools (chosen) · pin-to-original-precompaction · derive-minus-fixed-headroom
  - chosen: TREE_BASELINE_BYTES = sum of pool baselines; TREE_TARGET_BYTES stays int(baseline * 0.75). A new test pins the invariant (baseline == sum of pools) so re-hardcoding fails. Kills the drift class at the source.
  - pin-to-original-precompaction: keep a frozen literal = the true pre-lean tree size (171823). Rejected — that's exactly today's design; it drifts because pools rebaseline above it and someone must hand-bump (the 802-byte drift + my +1291 last task).
  - derive-minus-fixed-headroom: derive but subtract a constant to keep the budget tighter. Rejected — adds a second magic number, reintroducing a drift surface.
Must:
<must>
  - `TREE_BASELINE_BYTES == sum(p["baseline"] for p in POOLS)` — the tree baseline is DERIVED, not a literal; a pool rebaseline propagates with no second edit.
  - `TREE_TARGET_BYTES` stays `int(TREE_BASELINE_BYTES * 0.75)` — the 0.75 whole-tree ratio is unchanged.
  - The existing `test_tree_under_byte_budget` still holds (current tree 129797 ≤ derived target 130437) — the guardrail still catches UNTRACKED growth (a guide that grows without an approved pool rebaseline).
  - The stale inline comments (`= 171823 … sum of the four pool baselines`, `≤129835`) are corrected to reflect the derivation.
</must>
Reject:
<reject>
  - `TREE_BASELINE_BYTES != sum(p["baseline"] for p in POOLS)` (re-hardcoded / drifted) -> the new invariant test fails (a fence assertion, not an engine error code)
</reject>
After:
<after>
  - The tree baseline can never silently lag the pool baselines again; the only knob is each pool's own (human-approved, contract-gated) baseline.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ Deriving INTENTIONALLY changes the guardrail's semantics: the tree budget now FLOATS UP with each approved pool rebaseline (was: nominally pinned near the pre-compaction size). Lowest confidence because someone might want the tree pinned to the original 171823 as an absolute "never regrow past pre-lean" anchor. Cost if wrong: the tree fence loosens as pools grow — but every pool growth is already human-approved at its own contract, so the tree just tracks decisions already made. Flagged at freeze.
  - [x] `test_skill_lean.py` is single-tree (tooling test, not mirrored) — confirmed; no parity/ENGINE_MD5 impact.
  - [x] Current tree (129797) sits under the derived target (130437) — confirmed; no guide needs trimming.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the tree baseline equals the sum of the pool baselines
  Given test_skill_lean.py after the change
  When I compute sum(p["baseline"] for p in POOLS)
  Then it equals TREE_BASELINE_BYTES (no drift)

Scenario: a pool rebaseline propagates to the tree with no second edit
  Given the derived TREE_BASELINE_BYTES
  When a pool's baseline is bumped by N
  Then TREE_BASELINE_BYTES increases by N automatically (still == the sum)

Scenario: the whole-tree guardrail still holds
  Given the current canonical skill tree (129797 bytes)
  When test_tree_under_byte_budget runs against the derived target (130437)
  Then it passes, and the 0.75 ratio is unchanged
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
test_skill_lean.py:
  TREE_BASELINE_BYTES = sum(p["baseline"] for p in POOLS)   # derived — was a hand-summed literal
  TREE_TARGET_BYTES   = int(TREE_BASELINE_BYTES * 0.75)     # 0.75 ratio unchanged
  + a new invariant test: assertEqual(TREE_BASELINE_BYTES, sum(p["baseline"] for p in POOLS))
    (RED while the literal 173114 ≠ live sum 173916; GREEN once derived; guards re-hardcoding)
  + corrected inline comments (drop "= 171823 / ≤129835"; explain the derivation)

Invariants: 0.75 ratio kept · test_tree_under_byte_budget still passes (tree 129797 ≤ 130437) ·
            single-tree change (no mirror, no ENGINE_MD5) · no engine code touched.
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-25 (derive TREE_BASELINE_BYTES from the pool baselines).
Least-sure flag surfaced at freeze: [contract] deriving INTENTIONALLY changes the guardrail's semantics — the whole-tree budget now floats UP with each approved pool rebaseline rather than being pinned near the pre-compaction size (171823); cost if wrong = it no longer acts as an absolute "never regrow past pre-lean" anchor, but every pool growth is already human-approved at its own contract, so the tree only tracks decisions already made. No engine change → no ENGINE_MD5 re-pin; single-tree (test not mirrored).
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the invariant + the unchanged guardrail (3 scenarios).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_tree_baseline_derived_from_pools: assertEqual(TREE_BASELINE_BYTES, sum(p["baseline"] for p in POOLS)) — RED now (173114 != 173916), GREEN after derivation; guards re-hardcoding/drift
  - test_pool_rebaseline_propagates_to_tree: bump a copy of POOLS by N, recompute the derived sum, assert it rises by N (the propagation property) — proves no second edit needed
  - test_tree_under_byte_budget (EXISTING, unchanged): still green against the derived target — the guardrail holds
</test_plan>

Tests live in: `add-method/tooling/test_skill_lean.py` · MUST run red (missing derivation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/test_skill_lean.py`   <!-- single-tree tooling test; not mirrored, no engine -->
Strategy (ordered batches): 1. add the 2 new tests (test_tree_baseline_derived_from_pools RED + test_pool_rebaseline_propagates_to_tree). 2. change TREE_BASELINE_BYTES to the derived sum + fix the inline comments. 3. green; full suite + the existing test_tree_under_byte_budget stay green.
Safety rule (feature-specific): keep the 0.75 ratio and the guardrail intent; derive only the baseline. No engine code, no mirror, no ENGINE_MD5.
Code lives in: `add-method/tooling/test_skill_lean.py`
Constraints: do NOT change any test's intent or the contract; allow-list packages only; ask if unclear.
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

- [x] all tests pass — full suite 1805/0 (was 1803; +2 F10 tests)
- [x] coverage did not decrease — +2 invariant tests; the existing test_tree_under_byte_budget kept
- [x] no test or contract was altered during build — the 2 §4 tests were authored in the tests phase (RED) and unchanged since; the build changed only the non-test constant TREE_BASELINE_BYTES (+ its comment) in the same file → re-crossed tests→build to re-baseline the tripwire honestly on the final file (src and tests share one file; no test ASSERTION weakened)
- [x] the green was EARNED, not gamed — refute-read (manual): test_tree_baseline_derived_from_pools compares the module constant to an INDEPENDENT recompute of sum(POOLS) (RED proven at 173114≠173916); the propagation test bumps by N and checks the derived sum rises by N (RED before, tied to the live constant); not vacuous — they fail if the constant is re-hardcoded/drifts
- [x] concurrency / timing — n/a (pure module-constant derivation; no runtime path, no engine change)
- [x] no exposed secrets, injection openings, or unexpected dependencies — single-file test edit; no new imports
- [x] layering & dependencies follow CONVENTIONS.md — single-tree (test not mirrored); engine untouched → ENGINE_MD5 unchanged
- [x] a person reviewed and approved the change — Tin Dang froze v1 (derive from pools, accepting the floats-with-pool-rebaselines semantics)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] TREE_BASELINE_BYTES now equals the live sum of pool baselines (173916), not the old literal (173114) — confirmed: drift went 802 → 0; test_tree_baseline_derived_from_pools green
- [x] the whole-tree guardrail still holds — confirmed: tree 129797 ≤ derived target 130437; test_tree_under_byte_budget green, 0.75 ratio unchanged

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — TREE_BASELINE_BYTES is consumed by TREE_TARGET_BYTES → test_tree_under_byte_budget; the new derivation references POOLS (defined above it); the 2 new tests reference the constant + POOLS. All resolve.
- [x] DEAD-CODE — no orphaned symbol; the old hand-sum literal + stale comments are removed
- [x] SEMANTIC (code) — the derivation reads `sum(p["baseline"] for p in POOLS)`; POOLS is defined earlier in the module, so the constant is computable at import; comments corrected (no stale 171823/129835)

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-25

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
- [ADD · folded] a TEST-ONLY task (src and tests share one file, e.g. test_skill_lean.py) trips the tamper tripwire at the gate — the build edit changes the same file the tests→build snapshot captured (build_tampered). Honest fix: re-cross tests→build AFTER the build edit to re-baseline the tripwire on the final file; no test ASSERTION is weakened (evidence: F10 — gate would flag build_tampered:test_skill_lean.py without the re-cross, same shape as ground-phase-harden's change-request redo). Recurs for F14 (tempdir-leak sweep across ~109 test files). [folded foundation-version 52]
- [ADD · folded] a hand-summed budget that should track sub-budgets DRIFTS — derive it (sum the parts) and pin the invariant with a test, rather than hand-bumping a literal each time a part grows (evidence: F10 — TREE_BASELINE_BYTES lagged the pool baselines by 802 B + a forgotten edit; F4/F8's spirit: enforce the invariant at the seam). [folded foundation-version 52]
