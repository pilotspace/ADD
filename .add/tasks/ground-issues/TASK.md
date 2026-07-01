# TASK: §0 Issues/Risks field that feeds SPECIFY

slug: ground-issues · created: 2026-06-30 · stage: mvp
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
  - `add-method/skill/add/phases/0-ground.md` — the GROUND guide; `## Gather` bullets (Touches/Context/Honors/Anchors) + `## Exit gate`. Where the new "Issues/Risks (→ feed §1)" gather bullet lands. (×3 skill trees: skill/add, .claude/skills/add, src/add_method/_bundled/skill/add)
  - `add-method/tooling/templates/TASK.md.tmpl` — `## 0 · GROUND` section, lines 18-21 (Touches/Context/Honors/Anchors lines). New `Issues/Risks (→ feed §1):` line lands between Context and Honors (or after Anchors). (×3 template trees: tooling/templates, .add/tooling/templates, src/add_method/_bundled/tooling/templates)
  - `add-method/skill/add/phases/1-specify.md` — the consume point; `## AI prompt` "Read first:" (l.35) + `## Produce`/`Co-specify`. §1 must build on the §0 issues. (×3 skill trees)
  - `add-method/tooling/test_ground_issues.py` — NEW test, mirrors `test_ground_context.py` (the proven sibling pattern).
Context (working folder):
  - sibling test `add-method/tooling/test_ground_context.py` — exact pattern (a §0 field across 3 guide + 3 template trees, engine untouched, byte-identical parity).
  - `add-method/tooling/engine_pin.py:ENGINE_MD5` — the no-EXEC pin; this task adds NO engine code → must stay byte-identical.
  - `add-method/tooling/test_skill_lean.py` POOLS — the "phases" pool (ratio 0.80, baseline 40065, target 32052).
Honors (patterns / conventions):
  - PROJECT.md leanness: §0 fields are **task-delta only, never a re-scan**; a `<…>` placeholder = WEAK grounding.
  - **phases pool is at its FLOOR** (32049/32052, 3 B headroom) → new guide/specify bytes MUST be absorbed by compacting the phase guides (per the lean-over-budget steer), NOT a rebaseline unless unavoidable + human-approved.
  - 3-tree parity (test_ground_context pattern; test_tree_parity / test_bundle_parity); prepare_bundle.py regenerates `_bundled/`.
  - the grounding measure (`add.py:_grounded_state` / `_section0_anchors`) keys ONLY on the `Anchors the contract cites:` line — preserve it verbatim; engine untouched.
Anchors the contract cites: 0-ground.md `## Gather` "Issues/Risks (→ feed §1)" bullet · TASK.md.tmpl §0 `Issues/Risks (→ feed §1):` line · 1-specify.md "Read first" consume reference · the `Anchors the contract cites:` invariant line (preserved) · engine_pin.ENGINE_MD5 (unchanged)

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: §0 GROUND fifth field — "Issues/Risks (→ feed §1)" — gathered at ground, consumed by specify
Framings weighed: fifth §0 sub-field, guide+template prose, specify consumes (chosen) · engine-enforced ground check (rejected — adds engine surface, breaks this task's NO-EXEC + heavier) · fold into the existing Context field (rejected — conflates non-code artifacts with code problems; loses the explicit feed-to-§1 intent)
Must:
<must>
  - M1: `0-ground.md` `## Gather` names a new **"Issues/Risks (→ feed §1)"** category — the concrete problems / traps / untestable risks the AI finds in the REAL code while grounding (task-delta only, never a re-scan).
  - M2: `TASK.md.tmpl` `## 0 · GROUND` gains ONE light `Issues/Risks (→ feed §1):` line.
  - M3: `1-specify.md` CONSUMES it — §1 SPECIFY explicitly builds on the §0 Issues/Risks (named in "Read first" + the produce/co-specify flow), so the spec answers problems found, not assumed.
  - M4: the guide states the field is **task-delta only** (a `<…>` placeholder = WEAK grounding, same rule as the other fields).
  - M5: invariants preserved — the `Anchors the contract cites:` line verbatim, the `## 0`/`GROUND` headings, and `add.py` byte-identical to `engine_pin.ENGINE_MD5` (no engine edit).
  - M6: `0-ground.md` ×3 skill trees and `TASK.md.tmpl` ×3 template trees stay byte-identical; the `phases` lean pool stays ≤ target (32052) — absorbed by compacting phase-guide prose, NOT a rebaseline.
</must>
Reject:
<reject>
  - the build edits/moves the `Anchors the contract cites:` measure line -> "anchors_line_broken"
  - the build changes `add.py` (ENGINE_MD5 drifts) -> "engine_touched"
  - the new field's bytes are met by bumping the pool baseline instead of compaction (no human approval) -> "lean_rebaselined"
  - any guide or template tree copy drifts from its siblings -> "tree_drift"
</reject>
After:
<after>
  - The GROUND gather names 5 categories (Touches · Context · Honors · Anchors · Issues/Risks); §0 template carries the Issues/Risks line; §1 specify reads it; engine unchanged; phases pool ≤ 32052; guide×3 + template×3 byte-identical; full suite green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ The `phases` pool is at its FLOOR (32049/32052, 3 B headroom) — the new field + consume edit (~300–500 B) must be reclaimed by compacting phase-guide prose WITHOUT breaking another phase-guide's pinned phrases (test_ground_context, test_verify_deepen, test_setup_*, etc.). Lowest confidence: which prose is safe to compress. If wrong: a sibling phase-guide test goes red → rework, or a human-approved rebaseline.
  - [ ] Placement of the new template line — AFTER the Anchors line (last §0 line) is safest (doesn't disturb the measured Anchors line or the Context/Honors order other tests assume). Confirm at contract.
  - [ ] "Reject" codes are guard-test names (this is a doc/method task) — the negative scenarios are invariant-violations, not runtime inputs. Confirm that framing is acceptable.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: guide names the Issues/Risks gather category   # M1, M4
  Given the 0-ground.md guide
  When I read its ## Gather section
  Then it names an "Issues/Risks (→ feed §1)" category for problems/traps/untestable risks found in real code
  And it says the field is task-delta only
  And the Touches/Context/Honors/Anchors categories remain

Scenario: template carries the Issues/Risks line   # M2
  Given the TASK.md.tmpl ## 0 · GROUND section
  When I read it
  Then it has one "Issues/Risks (→ feed §1):" line
  And the "Anchors the contract cites:" line is unchanged

Scenario: specify consumes the grounded issues   # M3
  Given the 1-specify.md guide
  When I read its "Read first" / produce flow
  Then it directs §1 to build on the §0 GROUND Issues/Risks
  And the existing co-specify three-moves and exit gate remain

Scenario: the grounding measure line is untouched   # R:anchors_line_broken
  Given the change is applied
  When add.py _grounded_state reads a §0 with the Anchors line filled
  Then it still reports grounded
  And the "Anchors the contract cites:" line text is byte-for-byte unchanged

Scenario: the engine is not touched   # R:engine_touched, M5
  Given the change is applied
  When I md5 every add.py copy
  Then each equals engine_pin.ENGINE_MD5
  And no add.py byte changed

Scenario: lean pool stays under budget by compaction   # R:lean_rebaselined, M6
  Given the new guide+specify bytes are added
  When I sum the phases pool
  Then it is ≤ 32052 (the unchanged target)
  And the test_skill_lean phases baseline is still 40065

Scenario: all tree copies stay byte-identical   # R:tree_drift, M6
  Given the change is applied
  When I md5 the 3 guide copies and the 3 template copies
  Then each set is byte-identical
  And the _bundled copies match their canonical source
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
GROUND §0 fifth field — frozen shape @ v1   (a doc/method contract: the exact text-shape + invariants)

0-ground.md  ## Gather:
  + bullet "Issues/Risks (→ feed §1)" — concrete problems / traps / untestable risks found in the
    REAL code while grounding; task-delta only (never a re-scan).
  ## Exit gate: + a checkbox for the new field (non-optional, like the other four).

TASK.md.tmpl  ## 0 · GROUND:
  + ONE line, placed AFTER "Anchors the contract cites:":
      Issues/Risks (→ feed §1): <problems/traps/untestable risks found in the real code — task-delta>

1-specify.md  (consume):
  "Read first:" names the §0 GROUND Issues/Risks; the produce/co-specify flow builds §1 on them.

INVARIANTS (must hold post-change):
  - "Anchors the contract cites:" line byte-for-byte unchanged (the grounding measure keys on it)
  - "## 0" / "GROUND" headings preserved
  - every add.py copy == engine_pin.ENGINE_MD5 (no engine edit)
  - 0-ground.md ×3 + TASK.md.tmpl ×3 byte-identical; _bundled regenerated via prepare_bundle.py
  - phases lean pool ≤ 32052 (baseline 40065 unchanged) — met by compacting phase-guide prose

Tests: add-method/tooling/test_ground_issues.py  (mirrors test_ground_context.py)
```

Least-sure flag surfaced at freeze: [contract/test] the invariant "phases pool ≤ 32052, met by compaction (no rebaseline)" is the least-sure part of this bundle — the pool is at its floor (3 B headroom), so the new surface may not compress without risking a sibling phase-guide's pinned phrase; fallback is a human-approved rebaseline, brought back to you, never silent.
Status: FROZEN @ v1 — approved by Tin
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: behavioral guards (doc/method task — no coverage %); mirrors test_ground_context.py
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_guide_names_issues_category: 0-ground.md ## Gather names "Issues/Risks (→ feed §1)" + task-delta; Touches/Context/Honors/Anchors remain   (M1,M4)
  - test_template_has_issues_line: TASK.md.tmpl §0 has "Issues/Risks (→ feed §1):"; Anchors line unchanged   (M2)
  - test_specify_consumes_issues: 1-specify.md "Read first"/produce builds §1 on the §0 issues; three-moves + exit gate remain   (M3)
  - test_grounded_measure_line_intact: the "Anchors the contract cites:" line byte-unchanged   (R:anchors_line_broken)
  - test_engine_byte_identical_to_pin: every add.py == engine_pin.ENGINE_MD5   (R:engine_touched,M5)
  - test_phases_pool_under_budget: phases pool ≤ 32052 AND test_skill_lean phases baseline still 40065   (R:lean_rebaselined,M6)
  - test_copies_byte_identical: 0-ground.md ×3 + TASK.md.tmpl ×3 each byte-identical   (R:tree_drift,M6)
</test_plan>

Tests live in: `add-method/tooling/test_ground_issues.py` · MUST run red (missing field) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/phases/` `.claude/skills/add/phases/` `add-method/src/add_method/_bundled/skill/add/phases/` `add-method/tooling/templates/` `.add/tooling/templates/` `add-method/src/add_method/_bundled/tooling/templates/` `add-method/tooling/test_ground_issues.py`
Strategy (ordered batches): 1. write test_ground_issues.py RED (mirror test_ground_context.py). 2. add the "Issues/Risks (→ feed §1)" gather bullet + exit-gate checkbox to 0-ground.md (canonical) and the §0 line to TASK.md.tmpl (canonical, after Anchors). 3. add the consume reference to 1-specify.md (canonical). 4. RECLAIM the pool: compact equal-or-more prose within 0-ground.md/1-specify.md (the guides I'm already in) so the phases pool stays ≤32052 — compaction, not rebaseline. 5. propagate canonical → twins (cp), run prepare_bundle.py for _bundled. 6. full suite green.

Persona (optional): <name the persona file under `.add/personas/` this build embodies as a domain stance atop SOUL.md — advisory, never lowers a gate; absent = generic>
Known-problem fixes: <trap → planned fix — the failure modes this build must dodge; guidance, not enforced>
Strategy actually used: <fill at VERIFY — the strategy you ACTUALLY used (or "as planned"); harvested into the §7 Decisions (ADR) block as the [AI] build decision>
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) is live: a completing verify gate refuses an
     out-of-scope build (scope_violation → self-heal) and add.py check surfaces it.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 2508/0
- [x] coverage did not decrease — n/a (doc/method task; behavioral guards, no coverage metric)
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; no existing test edited (only the new test_ground_issues.py added)
- [x] the green was EARNED, not gamed — refute-read below
- [x] concurrency / timing — n/a (static guide/template prose; no runtime)
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose only; no new deps
- [x] layering & dependencies follow CONVENTIONS.md — the new field follows the existing §0 sub-field pattern
- [ ] a person reviewed and approved the change — auto-resolved under `autonomy: auto` (human approved the §3 freeze; build auto-PASSed; refute-read is the backstop)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] template §0 carries `Issues/Risks (→ feed §1):` AFTER the Anchors line — confirmed by test_section0_has_issues_line + test_issues_line_after_anchors (green)
- [x] `0-ground.md` reads with a 5th gather category "Issues/Risks (→ feed §1)" (task-delta) + an exit-gate checkbox — confirmed: line 19 (gather) + line 52 (exit gate)
- [x] `1-specify.md` directs §1 to build on the §0 Issues/Risks — confirmed: "Read first" + Converge step both name it
- [x] `test_ground_issues` all green AND full suite green — confirmed: Ran 2508 tests, OK
- [x] phases pool ≤ 32052 with baseline still 40065 — confirmed: pool = 32051; test_phases_baseline_unchanged green
- [x] add.py md5 == engine_pin.ENGINE_MD5; guide ×3 + template ×3 byte-identical — confirmed: add.py==pin True; parity = 1 md5 each

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose / non-code) — read in full: 0-ground.md + 1-specify.md (canonical) re-read end-to-end after edits — the new field reads coherently, the consume references resolve, and no pinned token (AI-owned · working folder · the 4 context keywords · subagent/index/skim/deepen · Touches/Context/Honors/Anchors) was dropped; the compaction kept meaning.
- [x] WIRING — the new field is referenced by the consume in 1-specify (Read-first + Converge) and guarded by test_ground_issues; no orphaned text.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self · adversarially checked: tried to refute the green — (a) is the field real or vacuous? the gather bullet + exit checkbox + template line + specify consume are substantive prose, not stubs; (b) could the pool test pass by gaming? no — it measures real bytes (32051) and pins baseline 40065, so a silent rebaseline would fail test_phases_baseline_unchanged; (c) did parity tests pass trivially? no — they md5 three real files each; (d) did the §0 measure regress? no — test_section0_preserves_anchors_line + the engine-pin test both green. No overfit, no weakened test.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: self
1. Security: CLEAR — guide/template prose; no code path, no input handling, no secrets
2. Concurrency: CLEAR — static documents; no runtime, no shared state
3. Architecture: CLEAR — the field follows the existing §0 sub-field pattern; no layering/engine change (add.py == ENGINE_MD5)
Verdict: PASS
Residue: none
Binding: yes — mechanical

### GATE RECORD
Outcome: PASS
Reviewed by: self (auto-resolved under autonomy: auto; mechanical + green + no residue) · date: 2026-06-30

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. The Advisor 3-lens verdict and the Refute-read verdict are both measured by `add.py audit` (`advisor_verdict_unrecorded` · `refute_unrecorded`) — neither is engine-blocked; a human spot-audit is the backstop for any finding the AI did not surface or record. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose fifth §0 sub-field, guide+template prose, specify consumes; rejected engine-enforced ground check (rejected — adds engine surface, breaks this task's NO-EXEC + heavier) · fold into the existing Context field (rejected — conflates non-code artifacts with code problems; loses the explicit feed-to-§1 intent)
- [human] freeze — froze §3 @ v1 (approved by Tin)
- [AI] build — strategy used: as planned
- [AI] verify — gate PASS (reviewed by self (auto-resolved under autonomy: auto; mechanical + green + no residue))

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
