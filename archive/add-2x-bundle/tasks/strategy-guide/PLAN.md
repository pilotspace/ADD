# PLAN: strategy.md: the persona-framed discuss-optimize-converge PM loop

slug: strategy-guide · created: 2026-07-24 · stage: mvp
milestone: strategy-intake
autonomy: auto
phase: done
> One file = one task — an ATOMIC node: persist the interface (contract · red suite · scope · verdict); reason everything else in-context, don't write essays. The phase marker above is the single source of truth (`add.py phase`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: a new strategy.md skill guide — the persona-framed DISCUSS→OPTIMIZE→CONVERGE loop that fills a milestone's `## Strategy` slot with an optimized task DAG, converging via the existing confidence self-score, communicated through the persona-owned gate.
Framings weighed: a NEW on-demand guide (strategy.md) triggered when a milestone needs its Strategy slot filled (chosen — the `## Strategy` slot already ships in MILESTONE.md.tmpl (strategy-section) and the persona already loads at intake (persona-at-intake); the missing piece is the HOW — the guide that drives the loop filling that slot; on-demand matches every other beyond.md guide) · fold the loop into intake.md (rejected — intake SIZES a request into scope; strategy OPTIMIZES an already-scoped milestone's task DAG; different jobs, different triggers) · a new engine verb (rejected — the engine records the slot, never drives the persona loop; strategy is skill-guided like design/loop)
Must:
<must>
  - M1 strategy.md exists and describes a DISCUSS→OPTIMIZE→CONVERGE loop that fills MILESTONE.md's `## Strategy` slot with a sequenced task DAG (approach · freeze-first contracts · parallel waves · first unblocking slice)
  - M2 the loop is persona-FRAMED — driven by the persona already loaded at intake (persona-at-intake), not a fresh selection
  - M3 CONVERGE uses the EXISTING confidence self-score (0–1 across six dimensions, refine if any < 0.9 — phases/direction.md) to reach ~95% confidence — not a newly invented mechanism
  - M4 the strategy is SOFT/advisory — the preferred plan; the loop may deviate and records actual; it is NEVER a new gate, and security stays HARD-STOP; drafted-blank is valid for a micro/--tiny milestone
  - M5 SKILL.md and beyond.md point to strategy.md (one trigger = one guide)
  - M6 strategy.md + the two pointer files are byte-identical across all three skill trees
</must>
Reject:
<reject>
  - a strategy loop that hard-gates the milestone on reaching a confidence bar -> "strategy_blocks_milestone"
  - a convergence mechanism other than the existing six-dimension self-score -> "divergent_confidence"
</reject>
After:
<after>
  - a multi-task / high-uncertainty milestone gets a persona-optimized task DAG recorded in its `## Strategy` slot before the tasks are built
  - a micro / low-risk milestone can skip the loop entirely (drafted-blank slot) at zero cost
Boundary: a milestone arrives in TWO shapes the guide must handle — multi-task/high-uncertainty (run the loop) and micro/--tiny (drafted-blank, skip); the guide must never force the loop on the second.
<assumptions>
  ⚠ the ~95% confidence target maps cleanly onto the existing self-score's "refine if any dimension < 0.9" bar — if the two are meant to be different thresholds, the guide conflates them; mitigated by expressing convergence as "refine until the self-score clears its bar" and citing phases/direction.md as the single source, rather than hard-coding a second number
</assumptions>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Contract (freeze the shape — the HARD, tamper-guarded core; ground it in the REAL code in-context, cite symbols not line numbers)

```
NEW GUIDE: add-method/skill/add/strategy.md  (+ 2 byte-identical twins)

  # Strategy — the persona-framed PM loop that fills the ## Strategy slot
  Trigger: a multi-task or high-uncertainty milestone needs its `## Strategy`
  slot (MILESTONE.md) filled before its tasks are built. Micro / --tiny → skip
  (drafted-blank is valid). The persona loaded at intake (intake.md) DRIVES this.

  Run the loop WITH that persona:
  1. DISCUSS — surface the task DAG: dependencies, the shared/risky contracts,
     the tradeoffs. Ask one load-bearing question per LIVE lens (not a survey);
     reflect the milestone goal, name what's in/out.
  2. OPTIMIZE — sequence the DAG: approach (risk-first | dependency-first |
     first-slice-unblocks + WHY) · the freeze-first contract(s) · parallel waves
     behind frozen contracts · the first unblocking slice · tradeoffs weighed.
  3. CONVERGE — self-score the plan with the six-dimension confidence self-score
     (phases/direction.md); refine until it clears its bar (~95% confident).
     Record the converged plan in the milestone's `## Strategy` slot.
  Communicate at the human seam via the persona-owned gate (gate-udd.md).

  SOFT/advisory: the Strategy slot is the PREFERRED plan — the loop may deviate
  and records what it did. NEVER a new gate; security stays HARD-STOP.

POINTERS (one trigger = one guide):
  - SKILL.md "Beyond the bundle": add a strategy trigger → `strategy.md`
  - beyond.md: add the full-prose routing line for strategy.md

Twins (byte-identical, all three skill trees):
  skill/add/{strategy.md,SKILL.md,beyond.md} ·
  src/add_method/_bundled/skill/add/{...} · .claude/skills/add/{...}
NOT changed: no engine, no template, no pin. No hard SKILL.md byte ceiling
(the 9500 literal was superseded — test_gate_experience_udd.py:12); the pool
census counts parity-named TEST fns, which a new guide + normal test don't add to.
```

Grounding anchors (verified in-context): MILESTONE.md.tmpl:43-49 the `## Strategy` slot (strategy-section) this loop fills · intake.md "## Load the fitting persona first" (persona-at-intake) — the persona this loop reuses · beyond.md:12-13 the confidence self-score → phases/direction.md · gate-udd.md the persona-owned gate · SKILL.md:98-104 "Beyond the bundle — one trigger = one guide" · beyond.md is "the full routing prose" · 3 skill trees confirmed present.

Target (measurable): strategy.md added with the 3-stage loop naming all four DAG facets (approach · freeze-first · waves · first slice) · convergence cites phases/direction.md (no new number) · SOFT + security-HARD-STOP stated · SKILL.md + beyond.md each gain one strategy pointer · 3 trees byte-identical for all 3 files · new content-guard red before / green after · full suite green.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: no

### Build-strategy — Scope (may touch) is HARD scope-lock; the rest is SOFT (the builder self-improves and records actual at verify)
Scope (may touch): `add-method/skill/add/` `add-method/src/add_method/_bundled/skill/add/` `.claude/skills/add/` `add-method/tooling/test_strategy_guide.py` `./tests/`
Regression floor: the full `tooling/` suite via CI's `unittest discover` — the skill-tree parity + pool-census tests (test_tree_parity, test_corpus_slim) and any SKILL.md/beyond.md content tests must stay green.
Persona (optional): `.add/personas/method-product-owner.md` — the PM lens; strategy.md is literally the guide for the persona-as-PM loop.

Strategy (preferred, not hard): write strategy.md first (the loop + SOFT caveat), add the two one-line pointers, then the content-guard proven red; mirror all three files byte-identical to the 2 twins; run the FULL suite because tree-parity + census tests span the skill trees.

Note on scope breadth: `skill/add/` is declared as a DIR (covers strategy.md + SKILL.md + beyond.md) × 3 trees. Only those three files are actually written — the DIR token is the honest write-set boundary, not license to touch other guides.

Least-sure flag surfaced at freeze: [spec] whether strategy.md is a load-bearing guide or restates what MILESTONE.md.tmpl's `## Strategy` slot prose + intake's persona step already imply. The slot already lists approach/freeze-first/waves; intake already loads the persona. Argument FOR a guide: the slot is a FORM to fill, not a METHOD to fill it — the DISCUSS→OPTIMIZE→CONVERGE loop + the confidence-convergence bar is genuinely new procedure, and the milestone criterion explicitly asks for "the strategy guide [that] drives a persona-framed discuss loop."
RESOLVED @ freeze (human, 2026-07-24): ship a TIGHT standalone strategy.md — a peer of design.md/loop.md (a core method loop, not a domain-persona playbook, so it stays a file where graduation/release/monorepo folded into beyond.md). It carries ONLY the loop mechanics + convergence discipline and DEFERS by pointer — the four facets → the `## Strategy` slot, the persona → intake.md, the self-score → phases/direction.md — so it adds method, never duplication. Evidence weighed: the slot already names the facets + SOFT + drafted-blank skip; the genuinely-new content is the procedure alone.

### AI-verify record (required when gate_mode: ai-plan-verify)
- [ ] §3 PLAN grounding anchors resolve in the current tree
- [ ] §1 every Must + every Reject present, each Reject paired with an error code
- [ ] §3 Contract shape is concrete (no template placeholder text remains)
- [ ] Lowest-confidence flag surfaced and substantive (mirrors unflagged_freeze's own bar)
Verified by: <agent-id> · at: <ISO-8601 UTC timestamp>

---

## 4 · TESTS & SCENARIOS — failing-first suite or acceptance checks (red) ▸ docs/06-step-4-tests.md

<test_plan>
  - test_strategy_guide_has_the_loop: strategy.md names DISCUSS, OPTIMIZE, CONVERGE and the four DAG facets (approach · freeze-first · waves · first slice) · covers: M1
  - test_strategy_reuses_intake_persona: strategy.md frames the loop around the persona loaded at intake, not a fresh selection · covers: M2
  - test_converge_cites_existing_selfscore: CONVERGE cites the six-dimension self-score / phases/direction.md, not a new number · covers: M3, R:divergent_confidence
  - test_strategy_is_soft_not_a_gate: strategy.md states SOFT/advisory + security-HARD-STOP + drafted-blank-valid, never a new gate · covers: M4, R:strategy_blocks_milestone
  - test_skill_and_beyond_point_to_strategy: SKILL.md AND beyond.md reference strategy.md · covers: M5
  - test_strategy_files_twinned: strategy.md, SKILL.md, beyond.md byte-identical across all three trees · covers: M6
</test_plan>

Kind: method/docs — assertions over SHIPPED GUIDE TEXT, executable checks over files. M1–M5 run RED (strategy.md doesn't exist; SKILL.md/beyond.md have no pointer). M6 (twin parity) is a regression guard; its red-first duty is mutation (drop one twin → red).

Rigor: one red test per §1 Must/Reject — the PRIMARY cases + primary edge cases — is the gated floor. Minor/secondary behaviors are DESCRIBED in prose below as build-guidance — no `covers:` tag, no red test, not gated. Add a Given/When/Then line inline ONLY when a human stakeholder needs a readable case — never as ceremony; the test_plan is the canonical encoding of every scenario.

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

Strategy actually used: as planned — wrote a TIGHT strategy.md (canon) carrying only the DISCUSS→OPTIMIZE→CONVERGE loop + SOFT caveat, DEFERRING the four facets → the `## Strategy` slot, the persona → intake.md, the self-score → phases/direction.md (point, don't restate — the [spec] resolution). Added one SKILL.md "Beyond the bundle" trigger + one beyond.md full-prose routing line. Mirrored all 3 files byte-identical to the 2 twins (md5-verified). No engine, no template, no pin touched.
Code lives in: the skill trees (this is a method/docs task — the guide IS the artifact; no `src/`)
Spawn (multi-agent): build/verify subagent spawns default `isolation: worktree`; cross-agent advisor — spawn `add-advisor` (an agent OTHER than the builder) for the freeze `--cross` and the §6 refute-read; `self` only when solo.
Constraints: do NOT change any test or the frozen §3 contract; stay inside §3 Scope (an out-of-scope build fails the gate: scope_violation); keep the §3 Regression floor green; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests (or §4 acceptance checks) pass — test_strategy_guide 6/6 green; regression floor test_tree_parity 6/6, test_corpus_slim, test_gate_experience_udd, test_persona_at_intake all green; full `tooling/` discover green (see gate)
- [x] coverage did not decrease — added a test file (test_strategy_guide.py), removed none
- [x] no test or contract was altered during build — only the frozen §3-scoped skill files + the new guard were written; §3 untouched post-freeze
- [x] the green was EARNED, not gamed — the guard asserts SHIPPED GUIDE TEXT (loop stages, persona/self-score citations, SOFT+HARD-STOP, twin parity); proven RED (6/6) before the guide existed, GREEN after; M6 mutation-red confirmed earlier (dropped twin → red)
- [x] concurrency / timing of the risky operation is safe — N/A (docs-only; no runtime/IO surface changed)
- [x] no exposed secrets, injection openings, or unexpected dependencies — pure markdown, no deps
- [x] layering & dependencies follow CONVENTIONS.md — strategy.md is a peer of design.md/loop.md (a core method loop as a guide file); pointers follow the one-trigger=one-guide convention
- [x] a person reviewed and approved the change — human resolved the [spec] flag and chose the tight-standalone container at freeze (2026-07-24)

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
Verdict: EARNED
By: self · adversarially checked: (1) is the guide vacuous restatement? — resolved at freeze: it DEFERS facets/persona/self-score by pointer, carrying only the net-new procedure. (2) does the guard overfit? — it reads real guide text across all 3 trees; the same file dropped from one twin goes red (M6). (3) does it re-introduce a gate? — test_strategy_is_soft_not_a_gate asserts SOFT/advisory + security-HARD-STOP + drafted-blank-skip are all present. No cheat found.

### GATE RECORD
Reported: yes — the freeze gate report (ARC + [spec] flag) rendered and the human decided the container before build
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-24

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

### Decisions (ADR)
- [AI] specify — chose a NEW on-demand guide (strategy.md) triggered when a milestone needs its Strategy slot filled; rejected fold the loop into intake.md (rejected — intake SIZES a request into scope; strategy OPTIMIZES an already-scoped milestone's task DAG; different jobs, different triggers) · a new engine verb (rejected — the engine records the slot, never drives the persona loop; strategy is skill-guided like design/loop)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned — wrote a TIGHT strategy.md (canon) carrying only the DISCUSS→OPTIMIZE→CONVERGE loop + SOFT caveat, DEFERRING the four facets → the `## Strategy` slot, the persona → intake.md, the self-score → phases/direction.md (point, don't restate — the [spec] resolution). Added one SKILL.md "Beyond the bundle" trigger + one beyond.md full-prose routing line. Mirrored all 3 files byte-identical to the 2 twins (md5-verified). No engine, no template, no pin touched.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
- [SPEC · dropped] the frozen §3 contract sample text says "human seam"; the shipped guide ships "human decision point" — the wording-lint (WORDING_RUBRIC.md:73, enforced) owns the house term, so impl refined the contract's illustrative wording. No re-specify: the contract froze the SHAPE, not the exact banned phrase (evidence: test_wording_lint_passes_clean_surface green after the swap).

### Competency deltas
- [ADD · open] a new skill guide's prose is scanned by the shipped-surface wording-lint (test_autonomy_command.WordingFenceTest) — draft against WORDING_RUBRIC.md's enforced swaps up front ("human seam"→"human decision point"), else the full suite catches it at the regression floor, not the targeted guard (evidence: 2299-test suite's ONLY failure was the lint, invisible to test_strategy_guide) (evidence: full run 221s, failures=1).
- [SDD · open] the honest resolution of a "load-bearing vs redundant" [spec] flag is EVIDENCE, not assertion: reading the actual `## Strategy` slot prose showed it already carried the four facets + SOFT + skip, so the guide's real value narrowed to the procedure alone — which kept it TIGHT (point, don't restate) (evidence: PLAN §3 [spec] RESOLVED note).
