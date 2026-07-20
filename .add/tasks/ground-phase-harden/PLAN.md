# TASK: Enrich the §0 GROUND guide + template: require all four fields, richer prompt + exit gate

slug: ground-phase-harden · created: 2026-06-25 · stage: mvp
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
  - `add-method/skill/add/phases/0-ground.md` — the per-task ground guide. Its `## Gather` block already names all four fields (Touches · Context · Honors · Anchors), but its `<exit_gate>` lists only THREE checks (files/symbols · conventions · anchors) — **Context is silently absent**. THE per-task gap to close + a richer "grounding is complete when…" rubric.
  - `add-method/skill/add/scope.md` (lines 18–24, "## Position the goal — ground in assets") — the MILESTONE-level grounding step. Its "1. Ground in current assets" sub-step is one thin line; the milestone twin of the §0 fields. Enrich to a consistent rubric so milestone-init grounding is as strict as the per-task §0.
  - `add-method/tooling/templates/TASK.md.tmpl` (§0, lines 16–21) — four single-line `<…>` placeholders; no `<!-- EXIT -->` comment (every other section has one). Convey all-four-required + the multi-item shape good groundings use; add the EXIT comment.
  - `add-method/tooling/templates/TASK.fast.md.tmpl` (§0, line 14) — the fast lane's minimal §0 (single placeholder). DECISION at the contract: keep lean (collapse-never-skip) vs mirror the enrichment.
Context (working folder):
  - `add-method/tooling/test_ground_wiring.py` — the ground test home: `GroundedStateTest` (the `_grounded_state` measure), `StatusSurfaceTest`, and the §0 parsing wiring. The new content + 3-tree-parity guards land here.
  - `add-method/tooling/test_skill_lean.py` — the lean fence: `0-ground.md` ∈ the **phases** pool (baseline 38298, ratio 0.80), `scope.md` ∈ the **reference** pool (baseline 65756, ratio 0.68). Both guides grow → both pools rebaseline (surface÷ratio, ratio kept — the fv51-folded method).
  - 3-tree skill mirror (canonical → `_bundled/skill/add/` + `.claude/skills/add/`) and template mirror (`tooling/templates/` → `.add/tooling/templates/` + `_bundled/tooling/templates/`); parity guarded by test_tree_parity / test_bundle_parity.
Honors (patterns / conventions):
  - The F6 shape (just shipped): guide + template enrichment, **NO engine gate** — `_grounded_state` stays a fail-open measure-not-block; this raises the DRAFTING bar, not a new refusal.
  - fv51-folded ADD lesson: a contract-approved fence-busting addition is absorbed by REBASELINING (surface÷ratio, ratio kept), never token-golfed thinner.
  - Progressive disclosure + the closed 5-tag XML vocab on guides; collapse-never-skip for the fast lane.
Anchors the contract cites: `phases/0-ground.md` `<exit_gate>` · `scope.md` "Position the goal" step · `TASK.md.tmpl` §0 block · `test_ground_wiring.py` · the four ground fields (Touches · Context · Honors · Anchors).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: enrich the grounding seams at BOTH altitudes — the per-task `§0 GROUND` (guide + template) and the milestone-level "Position the goal — ground in assets" (scope.md) — so a complete grounding is demanded by a consistent rubric (all four fields, named from real assets). Guide + template only; NO engine gate (the F6 shape).
Framings weighed: guide+template-rubric (chosen) · engine-gate-grounding · template-only
  - chosen: raise the DRAFTING bar in the guides + template + one shared four-field rubric, mirrored across both altitudes. The `_grounded_state` measure is untouched (stays fail-open). No new refusal, no engine change → no ENGINE_MD5 re-pin.
  - engine-gate-grounding: promote `task_not_grounded` to a real gate. Rejected for THIS task — the user chose the guide+template path; the gate is a separate (already-considered) option, leave the measure as-is.
  - template-only: just fix the template placeholders. Rejected — the guide exit gate's missing Context line is the actual correctness gap; the template alone wouldn't fix the rubric.
Must:
<must>
  - `phases/0-ground.md` `<exit_gate>` names ALL FOUR fields — adds the missing **Context (working folder)** check beside files/symbols · conventions · anchors.
  - `phases/0-ground.md` carries a "grounding is complete when…" rubric distinguishing a STRONG grounding (every field from real assets, anchors that exist) from a weak/placeholder one.
  - `scope.md`'s "Position the goal — ground in assets" step states the SAME four-field rubric at milestone altitude (a milestone grounds in assets as rigorously as a task §0), explicitly cross-referencing the per-task fields.
  - `TASK.md.tmpl` §0 keeps all four field labels. [v2: the `<!-- EXIT -->` comment clause was dropped — it busted the frozen lean comment fence; the completeness guidance lives in `phases/0-ground.md`.]
  - All edits are byte-identical across the three skill trees (canonical · `_bundled` · `.claude/skills`) and the template across its trees; the lean fence stays green (rebaseline by surface÷ratio, ratio kept).
</must>
Reject:
<reject>
  - the §0/`scope.md` rubric omits any of the four fields (Touches · Context · Honors · Anchors) -> "incomplete_ground_rubric" (a CONTENT assertion the tests enforce, not an engine error code)
  - a guide edited in one tree but not mirrored -> caught by test_tree_parity / test_bundle_parity (existing parity guards)
</reject>
After:
<after>
  - Both grounding seams demand the same four-field rubric; a drafter reading either guide is told Context is non-optional and what "grounded" concretely means. No engine behavior changed (no gate, no re-pin).
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ✅ RESOLVED at freeze — the human chose UNIFORM grounding: the fast template (`TASK.fast.md.tmpl` §0) ALSO names the four fields (compactly; it need not carry the full prose rubric). The "stays lean" framing was the draft default; uniformity won. (was ⚠: fast stays lean vs enrich-everywhere — human picked enrich-everywhere 2026-06-25.)
  - [x] No engine gate / no ENGINE_MD5 re-pin — confirmed by the chosen framing (guide+template, the F6 shape); `_grounded_state` and its tests are untouched.
  - [x] The lean fence absorbs the growth by rebaselining (surface÷ratio, ratio kept), per the fv51-folded lesson — not by trimming won ground.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the per-task ground exit gate names all four fields
  Given phases/0-ground.md after the edit
  When I read its <exit_gate> block
  Then it has a check for each of Touches, Context, Honors, and Anchors
  And the existing three checks (files/symbols, conventions, anchors) remain

Scenario: the per-task guide carries a grounding-complete rubric
  Given phases/0-ground.md
  When I read it
  Then it states what a STRONG (complete) grounding looks like vs a placeholder one

Scenario: the milestone-level step states the same four-field rubric
  Given scope.md "Position the goal — ground in assets"
  When I read the "Ground in current assets" step
  Then it names the same four grounding fields / rubric as the per-task §0

Scenario: the task template §0 names all four fields
  Given TASK.md.tmpl
  When I read its §0 block
  Then all four fields are present   # v2: the <!-- EXIT --> comment clause dropped (lean-fence collision)

Scenario: every grounding guide/template edit is mirrored across trees
  Given the canonical edits
  When I compare the three skill trees and the template trees
  Then they are byte-identical (parity holds)
  And the lean fence stays green
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
THE FOUR GROUND FIELDS (the shared rubric, asserted at both altitudes):
  Touches  · Context (working folder)  · Honors  · Anchors

phases/0-ground.md:
  <exit_gate> MUST contain a check naming each of the four fields
    (adds the missing "Context (working folder)" check; keeps the existing three)
  + a "grounding is complete when…" rubric line (STRONG vs placeholder grounding)

scope.md "## Position the goal — ground in assets":
  the "Ground in current assets" step names the SAME four-field rubric at milestone
  altitude, cross-referencing the per-task §0 (consistent grounding across altitudes)

TASK.md.tmpl §0:
  all four field labels present (already). [v1→v2 CHANGE REQUEST: the `<!-- EXIT … -->` comment
  clause was DROPPED — adding it pushed the template comment count to 12, busting the lean-pass
  fence `test_template_form_tags` (count < 12), which is out of §5 scope and a frozen test I must
  not weaken. The completeness guidance lives in `phases/0-ground.md` instead.]

TASK.fast.md.tmpl §0:
  ALSO names the four fields (compact — labels, not the full prose rubric)
  [§1 flag RESOLVED: human chose uniform grounding everywhere]

Invariants:
  - NO engine change · NO ENGINE_MD5 re-pin · _grounded_state untouched (fail-open measure)
  - byte-identical across 3 skill trees + template trees (parity guards)
  - lean fence green via rebaseline (surface÷ratio, ratio kept)
```

Status: FROZEN @ v2 — approved by Tin Dang 2026-06-25 (enrich BOTH the per-task §0 and milestone-scope grounding + the fast template — uniform four-field grounding everywhere).
Change request v1→v2 (human-approved 2026-06-25, build-time): DROPPED the TASK.md.tmpl §0 `<!-- EXIT … -->` comment clause — adding it busted the frozen lean-pass comment fence (`test_template_form_tags`, count < 12, out of §5 scope), and weakening that test inverts the method. The §0 completeness guidance lives in `phases/0-ground.md` (its enriched exit gate + rubric) instead; the template keeps all four field labels.
Least-sure flag surfaced at freeze: [scenario/contract] the fast template §0 was the least-sure point — draft default kept it lean (collapse-never-skip), but the human chose UNIFORM grounding, so the fast §0 now also names the four fields (compact labels, not the full prose rubric); cost if wrong = a touch more ceremony in the fast lane, reversible by trimming the fast §0 back to a one-liner. No engine change → no ENGINE_MD5 re-pin.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + the Reject (5 scenarios), as content+parity assertions.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_ground_exit_gate_names_all_four_fields: read canonical 0-ground.md <exit_gate>; assert each of Touches/Context/Honors/Anchors appears (RED today — Context absent)
  - test_ground_guide_has_completeness_rubric: assert 0-ground.md carries the "grounding is complete when…"/STRONG-vs-placeholder rubric (RED today)
  - test_scope_position_goal_names_four_field_rubric: assert scope.md "Position the goal" step names the four-field grounding rubric (RED today)
  - test_task_template_section0_names_four_fields: assert TASK.md.tmpl §0 has all four field labels (v2: EXIT-comment assertion dropped — lean-fence collision)
  - test_fast_template_section0_names_four_fields: assert TASK.fast.md.tmpl §0 names all four fields (RED today — fast §0 is a one-liner; human chose uniform grounding)
  - test_ground_harden_three_tree_parity: assert 0-ground.md + scope.md byte-identical canonical vs _bundled vs .claude/skills (reuses the parity pattern)
</test_plan>

Tests live in: `add-method/tooling/test_ground_wiring.py` · MUST run red (missing enrichment) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/skill/add/phases/0-ground.md` `add-method/skill/add/scope.md` `add-method/src/add_method/_bundled/skill/add/phases/0-ground.md` `add-method/src/add_method/_bundled/skill/add/scope.md` `.claude/skills/add/phases/0-ground.md` `.claude/skills/add/scope.md` `add-method/tooling/templates/TASK.md.tmpl` `add-method/tooling/templates/TASK.fast.md.tmpl` `add-method/src/add_method/_bundled/tooling/templates/TASK.md.tmpl` `add-method/src/add_method/_bundled/tooling/templates/TASK.fast.md.tmpl` `add-method/tooling/test_ground_wiring.py` `add-method/tooling/test_skill_lean.py`   <!-- canonical guides + their _bundled mirrors + the .claude/skills dogfood mirror (NOT pruned from the scope walk — must be declared) + BOTH templates (standard + fast) + bundled templates + the test home + the lean fence; .add/tooling template mirror is pruned (.add tree excluded) -->
Strategy (ordered batches): 1. add the 6 tests to test_ground_wiring.py (5 red + 1 lean control). 2. edit canonical 0-ground.md (Context in exit gate + completeness rubric), scope.md (four-field rubric), TASK.md.tmpl §0 (EXIT comment + required framing). 3. rebaseline the two lean pools. 4. prepare_bundle to mirror _bundled + .claude/skills + .add/tooling templates; full suite + parity green.
Safety rule (feature-specific): prose/template only — no engine code, no ENGINE_MD5 re-pin. Keep the closed 5-tag XML vocab on guides; never drop a guide.
Code lives in: the skill guides + the TASK template (+ their mirrors)
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.
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

- [x] all tests pass — full suite 1803/0 (was 1797; +6 ground-harden tests); lean fence + 3-tree/bundle parity green
- [x] coverage did not decrease — +6 behavioral content/parity tests; none removed
- [x] no test or contract was altered during build — the §4 red tests were authored in the tests phase; the only test edits were the human-approved v1→v2 CHANGE REQUEST (dropped the §0 EXIT-comment assertion) — recorded in §3, not a silent weakening; the lean fence `test_template_form_tags` was NOT touched (the change kept the template at 11 comments)
- [x] the green was EARNED, not gamed — refute-read (manual): each test reads the REAL guide/template/mirror bytes (not a fixture); the four-field assertions fail loudly when a field is absent (proven RED before build — Context was missing, scope.md lacked the rubric, fast §0 was a one-liner); the lean-fence rebaseline kept the ratio (won ground intact), it did not relax the guard
- [x] concurrency / timing — n/a (static prose/template edits; no runtime path, no engine change)
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose + template only; no new imports
- [x] layering & dependencies follow CONVENTIONS.md — byte-identical across the 3 skill trees + template trees (parity green); no engine change → ENGINE_MD5 unchanged
- [x] a person reviewed and approved the change — Tin Dang: froze v1 (uniform grounding), then approved the v1→v2 change request (drop the EXIT-comment clause) when it collided with the lean fence

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] reading `phases/0-ground.md`'s exit gate, a drafter now sees a **Context** check beside files/Touches, Honors, Anchors + a "grounding is complete when…" STRONG-vs-placeholder rubric — confirmed by eye in the file + test_ground_exit_gate_names_all_four_fields / test_ground_guide_has_completeness_rubric
- [x] reading `scope.md`'s "Position the goal" step, a milestone is told to ground in the same four fields at milestone scope — confirmed in the file + test_scope_position_goal_names_four_field_rubric; both templates' §0 name all four fields (standard + fast)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] SEMANTIC (prose) — read in full: 0-ground.md exit gate + rubric (Context no longer silently absent; rubric distinguishes strong/weak), scope.md step (four fields named at milestone scope, "altitude" slang removed for the ubiquitous-language fence), both template §0 blocks (four labels). No instruction contradicts the existing Gather block.
- [x] WIRING (prose) — the four-field rubric is consistent across both altitudes + both templates; no dangling reference; §3's dropped EXIT clause is recorded as a change request, not orphaned
- [x] DEAD-CODE — n/a (no code symbols added)

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
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
