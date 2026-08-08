# TASK: Setup: multi-turn per-drive domain deep-dive + ADRs

slug: setup-domain-deepdive · created: 2026-06-15 · stage: mvp
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
- `add-method/skill/add/phases/0-setup.md` (≈34–51 "§2b the 4-lens interview") — today one question per lens (Domain/Spec/Users/Decisions), single pass. This task adds a "## 2c · Domain deep-dive" step that deepens each of the four DRIVES (DDD·SDD·UDD·TDD) across MULTIPLE TURNS, captures the user's ADRs, and auto-completes under autonomy=auto. 3 byte-identical trees.
- `add-method/skill/add/phases/1-specify.md` — the co-specify diverge→converge→validate move §2b already lifts; the deep-dive applies it per drive, deeper.
- `.add/PROJECT.md` Key Decisions — where captured ADRs land (the existing "Decisions" lens becomes explicit ADR capture).
- prior art: `add-method/tooling/test_cospecify_lift.py` (content-test pattern); the run.md autonomy model (auto = full context → the AI may complete without stopping).
Context (working folder): the four drives are the method's spines — DDD (domain model), SDD (spec/outcomes), UDD (users/UI surface), TDD (what "done & trusted" looks like — the 4th drive §2b's "Decisions" lens did not name). ADR = architecture decision record.
Honors (patterns / conventions): no engine change (guide only); the autonomy model (auto = AI drafts with full context, still surfaces the lowest-confidence flag — never skips the human's baseline approval); 3-tree byte-identical sync; the one lowest-confidence-flag notation.
Anchors the contract cites: the "## 2c · Domain deep-dive" step · the four named drives DDD·SDD·UDD·TDD · the multi-turn clarification · ADR capture into PROJECT.md Key Decisions · the autonomy=auto auto-complete behavior (still flag-first).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: a "## 2c · Domain deep-dive" setup step that clarifies domain knowledge across multiple turns,
deep-diving each of the four drives (DDD · SDD · UDD · TDD), capturing the user's ADRs, and — under
autonomy=auto with full context — auto-completing all four drives (still surfacing the flag).
Framings weighed: a multi-turn per-drive deepening that auto-completes under auto (chosen) · keep the
single-question-per-lens §2b pass only (rejected — the user asked to deepen domain knowledge per drive) ·
auto-complete that SKIPS the human baseline approval (rejected — auto deepens drafting, never the gate).
Must:
<must>
  - phases/0-setup.md gains a "## 2c · Domain deep-dive" step that deepens domain knowledge across
    MULTIPLE TURNS, one deep-dive per drive — DDD, SDD, UDD, and TDD (the 4th drive §2b's lens list omitted).
  - it CAPTURES the user's ADRs (architecture decision records) into PROJECT.md Key Decisions as they surface.
  - under autonomy=auto with full context, it AUTO-COMPLETES all four drives in one pass (drafts without
    stopping to interview each), still ranking lowest-confidence-first and surfacing the top flag.
  - the auto-complete NEVER skips the human baseline approval (auto deepens drafting, not the gate) — the
    lock stays the one human decision.
  - all 3 skill trees stay byte-identical.
</must>
Reject:
<reject>
  - (prose task) a freeze whose step omits any of the four drives OR ADR capture OR the auto-complete
    behavior OR the gate-preserved note -> content tests stay red; never ship a half-section.
</reject>
After:
<after>
  - a reader of 0-setup.md knows the deep-dive covers DDD·SDD·UDD·TDD across multiple turns, captures ADRs,
    and auto-completes under auto without skipping the baseline approval.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [spec] adding a 4th drive (TDD) + multi-turn deepening risks making greenfield setup HEAVIER than the
    deliberately-short §2b interview — lowest confidence because §2b was kept short on purpose; if wrong:
    setup drags — mitigated by "ask only the live ones" (skip what the request answers) and the auto-mode
    auto-complete that collapses the turns when the AI already has full context.
  - [ ] [contract] ADRs land in PROJECT.md Key Decisions (not a new ADR file) — assumes the existing
    Decisions area suffices; if wrong: a later task adds an adr/ log.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the deep-dive step names all four drives across multiple turns
  Given a reader opens phases/0-setup.md at the new "## 2c · Domain deep-dive" step
  When they read it
  Then it deepens domain knowledge across MULTIPLE TURNS, one deep-dive per drive — DDD, SDD, UDD, TDD
  And the existing "## 2b" 4-lens interview section is unchanged

Scenario: the deep-dive captures the user's ADRs into the foundation
  Given the reader is on the "## 2c · Domain deep-dive" step
  When they read how a surfaced decision is recorded
  Then it says ADRs (architecture decision records) are captured into PROJECT.md Key Decisions
  And the lock stays the one human baseline approval (the gate is unchanged)

Scenario: auto mode auto-completes all four drives in one pass
  Given autonomy=auto with full context
  When the step describes auto-mode behavior
  Then it AUTO-COMPLETES all four drives without stopping to interview each, still flag-first
  And it NEVER skips the human baseline approval (auto deepens drafting, not the gate)

Scenario: the three skill trees stay byte-identical
  Given the edit lands in the canonical skill tree
  When the bundle + dogfood trees are compared
  Then all three copies of phases/0-setup.md are byte-identical
  And test_tree_parity / test_bundle_parity stay green

Scenario (reject): a half-section that omits a drive or the gate note stays red
  Given a draft "## 2c" step that omits one of DDD/SDD/UDD/TDD, ADR capture, the auto-complete behavior, or the gate-preserved note
  When the content suite runs
  Then it fails (red) — the section is not shippable
  And no existing 0-setup.md content (§1/§2a/§2b/§3/Run mode/§4/§5) is removed to make it pass
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
PROSE CONTRACT — phases/0-setup.md gains "## 2c · Domain deep-dive" (no engine change)
  The new section MUST contain, as readable prose:
    - the literal heading "## 2c · Domain deep-dive"
    - all four drive tokens: DDD, SDD, UDD, TDD  (each named at least once)
    - the multi-turn clarification: the phrase "multiple turns" (deepens across more than one turn)
    - ADR capture: the token "ADR" AND that it lands in "PROJECT.md" "Key Decisions"
    - the autonomy=auto auto-complete behavior: under "auto" it auto-completes all four drives
      in one pass (drafts without stopping per drive), still surfacing the lowest-confidence flag
    - the gate-preserved note: auto deepens DRAFTING, never the baseline approval / lock gate
  Invariants (unchanged):
    - "## 2b" 4-lens interview text is retained (the deep-dive deepens it, does not replace it)
    - all other 0-setup.md sections (§1, §2a, §3, Run mode, §4, §5, Exit gate) retained
    - no engine/CLI change — guide-only edit; all 3 skill trees byte-identical
Schema: docs only — phases/0-setup.md in the 3 skill trees (canonical · dogfood · bundle); no state.json change
```

Status: FROZEN @ v1 — approved by Tin Dang (autonomous authorization 2026-06-15)
Least-sure flag surfaced at freeze: [spec] adding a 4th drive (TDD) + per-drive multi-turn deepening risks making greenfield setup HEAVIER than the deliberately-short §2b interview — mitigated by "ask only the live ones" (skip what the request already answers) and the auto-mode auto-complete that collapses the turns when the AI has full context; if it still drags in practice, a §7 delta trims the turns.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the new "## 2c · Domain deep-dive" section, asserted by substring on the CANONICAL guide
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_deepdive_names_four_drives: read canonical 0-setup.md / find the "## 2c · Domain deep-dive"
    region / assert all of DDD, SDD, UDD, TDD appear in it + assert "## 2b" heading still present (unchanged)
  - test_deepdive_is_multi_turn: assert the region says "multiple turns"
  - test_deepdive_captures_adrs: assert the region names "ADR" AND "PROJECT.md" AND "Key Decisions"
  - test_deepdive_auto_completes: assert the region ties autonomy "auto" to auto-completing the four
    drives in one pass (drafts without stopping) AND still surfaces the lowest-confidence flag
  - test_deepdive_preserves_gate: assert the region says auto deepens drafting, NOT the baseline approval / lock
  - test_deepdive_three_trees_identical: assert the 3 skill-tree copies of 0-setup.md are byte-identical
    (dogfood + bundle == canonical)
  - test_deepdive_no_section_dropped (reject): assert §2a, §2b, "Run mode", "§ 4 · The one human gate"
    anchors all still present after the edit (no half-section that drops existing content)
</test_plan>

Tests live in: `tooling/test_setup_domain_deepdive.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/phases/0-setup.md` `.claude/skills/add/phases/0-setup.md` `add-method/src/add_method/_bundled/skill/add/phases/0-setup.md`
Strategy (ordered batches): 1. add "## 2c · Domain deep-dive" to the CANONICAL guide (after §2b, before §3) covering the four drives, multi-turn, ADR→PROJECT.md Key Decisions capture, auto auto-complete (flag-first), gate-preserved note · 2. `cp` canonical → dogfood · 3. run `prepare_bundle.py` to regenerate `_bundled/` · 4. run the full suite green (watch wording lint — no banned slang; use "autonomy level" not "dial")
Safety rule (feature-specific): prose-only — no engine/CLI/state change; the lock stays the only setup gate; §2b text retained (deepened, not replaced)
Code lives in: the 3 skill trees above (canonical is the source; dogfood + bundle are regenerated copies)
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

- [x] all tests pass — full suite 1077 green (was 1069; +8 new in test_setup_domain_deepdive)
- [x] coverage did not decrease — net +8 content tests; no test removed
- [x] no test or contract was altered during build — only the 3 skill-tree copies of 0-setup.md changed
- [x] the green was EARNED, not gamed — the suite ran RED first (8/8 failed on the missing "## 2c" marker), GREEN only after the section landed; assertions check real prose tokens (DDD/SDD/UDD/TDD, "multiple turns", ADR→PROJECT.md Key Decisions, auto auto-complete + flag, drafting-not-lock) scoped to the new region — not whole-file substrings a sibling section could satisfy
- [x] concurrency / timing of the risky operation is safe — n/a (prose-only; no runtime, no IO, no state mutation)
- [x] no exposed secrets, injection openings, or unexpected dependencies — none; docs-only edit, zero new deps
- [x] layering & dependencies follow CONVENTIONS.md — canonical→dogfood→bundle sync honored; 3 trees byte-identical
- [x] a person reviewed and approved the change — auto-resolved under autonomy=auto (autonomous authorization 2026-06-15); no security/residue escalation triggers

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read in full, not skimmed: read the rendered "## 2c · Domain deep-dive" section end-to-end. Confirmed: it deepens §2b (does not replace — §2b retained); names all four drives with a distinct deepening per drive incl. the TDD "trust" drive §2b's lens list omitted; captures ADRs into PROJECT.md Key Decisions; ties autonomy=auto to one-pass auto-complete that stays lowest-confidence-flag-first; states auto deepens DRAFTING and never the lock/baseline-approval gate. No banned slang (no "dial"); wording lint green.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang (autonomous authorization 2026-06-15) · date: 2026-06-15

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): does the deep-dive make real greenfield setups DRAG? (the flagged risk) — watch session length at setup; if the four-drive turns feel heavy in practice, trim via a §7 delta.
Spec delta for the next loop: the deep-dive and §2b now overlap (both lift the co-specify move at foundation level); a later pass could merge §2b into 2c as one "interview → deepen" arc rather than two sections.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [TDD · folded] setup's lens list omitted the trust/"done & trusted" drive — the four drives weren't symmetric at foundation level until 2c named TDD explicitly (evidence: §2b table had Domain/Spec/Users/Decisions, no trust lens; test_names_all_four_drives now guards all four)
- [ADD · folded] auto-mode's "deepen drafting, never the gate" rule now applies at SETUP, not just per-task verify — auto-complete collapses the deep-dive turns but never the lock (evidence: test_preserves_the_baseline_approval_gate)
