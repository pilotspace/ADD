# TASK: One TASK.md.tmpl under 3 phase banners; delete TASK.fast.md.tmpl; --fast = full minus _FAST_SECTIONS

slug: template-unify · created: 2026-07-16 · stage: mvp
milestone: thin-engine-loop
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

> Projected from milestone Ground (thin-engine-loop) + the decided unify design ([[project_unify_task_template_planned]]): one task template, the fast lane is a computed subset.
Feature: one TASK.md.tmpl for every lane — `--fast` = the full render minus `_FAST_SECTIONS`
Framings weighed: subset-by-construction drop-set applied at render (chosen) · keep two templates and lint them into agreement (rejected — two sources of truth; template drift is this repo's recorded failure mode) · byte-prefix truncation (rejected — fast's value is FEWER whole sections, not a shorter file)
Must:
<must>
  - M1 `new-task --fast` (and the lanes that imply fast: --oneshot, tiny-milestone default) renders from templates/TASK.md.tmpl ONLY; templates/TASK.fast.md.tmpl is DELETED from every template tree, and the `_FALLBACK_TASK_FAST` embedded twin is deleted with it
  - M2 the fast render = the full render minus exactly the `_FAST_SECTIONS` heading blocks, plus a spliced `fast: true` header line — every other fast line is byte-identical to a full-render line (subset by construction, machine-checkable)
  - M3 `--oneshot` still gets `oneshot: true` + `gate_mode: ai-plan-verify` header lines AND the §3 `### AI-verify record` block (spliced at render); `freeze --ai-plan-verify` keeps reading that block unchanged
  - M4 the template family leans: TASK.md.tmpl · MILESTONE.md.tmpl · personas/_template.md.tmpl · PROMPT.persona.md.tmpl each end measurably smaller than today, with every machine-read line, form tag, and label intact (byte ledger recorded in the task)
  - M5 TASK.md.tmpl's marker line reads `phase: direction` natively — cmd_new_task's render-time marker rewrite becomes a documented no-op on the updated template
  - M6 the full §1 gains the fast lane's `Boundary:` line so the input-dialect floor (boundary_unfilled, present-only lint) survives unification on BOTH lanes
</must>
Reject:
<reject>
  - a `--fast` render still containing any `_FAST_SECTIONS` heading -> "fast_sections_leak" (red suite name; the engine surface is the subset test)
  - a fast-render line with no byte-identical counterpart in the full render (beyond the spliced headers) -> "subset_broken"
  - the lean-pass touching a machine-read seam (phase marker · `# TASK:` title · `Status: DRAFT` · `Outcome:` · the Must/Reject/After/Assumptions labels · form tags) -> form_tag_offenses red (existing guard binds)
  - `freeze --ai-plan-verify` on a oneshot scaffold missing the AI-verify record -> "ai_freeze_checklist_incomplete" (existing floor, byte-unchanged)
</reject>
After:
<after>
  - ONE task template is the single source of truth for every lane; TASK.fast.md.tmpl is gone from all four template trees; a --fast scaffold is a provable strict subset of the full render
  - the family byte ledger is recorded (before → after per file) and every template guard (form tags · seams · tree parity) is green on the new shape
</after>
Boundary: template text in/out only — no state.json shape change, no new CLI flag; the render pipeline's only new input is the `_FAST_SECTIONS` constant
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the fast lane's condensed WORDING (the `Accept:` line grammar · one-line §4 plan · condensed §6 checkboxes) can retire without losing a floor — lowest confidence because ~10 fast-pinning test files pin that wording (the pinned-phrase census is LONG, six-phase-loop lesson); if wrong: a floor proves un-migratable and the drop-set must shrink (cost: the fast render keeps one more block)
  - [ ] no engine path reads TASK.fast.md by name besides _render_template's fallback table — confirm by grep before build
  - [ ] the tree-parity census (7 .tmpl files) and the 4 template trees update cleanly to the 6-file shape
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: fast render is a strict subset   # M2, R2
  Given a fresh project
  When `new-task a --fast` and `new-task b` (full) both run
  Then every line of a's TASK.md except the spliced `fast: true` header appears byte-identical in b's render
  And a's render contains none of the _FAST_SECTIONS headings

Scenario: fast drops exactly the drop-set   # M2, R1
  Given a `--fast` scaffold
  When its headings are compared to the full render's headings
  Then the missing set is EXACTLY _FAST_SECTIONS (§7 OBSERVE · §6 Deep checks · §6 Live-verify evidence · §6 Refute-read verdict · §6 Advisor 3-lens verdict)
  And §1–§6 core, the GATE RECORD, and Build expectations remain

Scenario: the fast template file is gone   # M1
  Given the four template trees (canonical · bundle · both dogfoods)
  When each is listed
  Then no TASK.fast.md.tmpl exists anywhere
  And _FALLBACK_TASK_FAST no longer exists in add.py

Scenario: oneshot keeps its AI-verify floor   # M3, R4
  Given `new-task o --oneshot`
  Then the scaffold carries oneshot: true · gate_mode: ai-plan-verify · a §3 "### AI-verify record" block
  When the block is filled and `freeze --by agent --ai-plan-verify --cross` runs
  Then the freeze passes; with the block MISSING it dies "ai_freeze_checklist_incomplete"

Scenario: default lane render unchanged in shape   # regression
  Given `new-task plain` with no lane flag
  Then the render carries every section of TASK.md.tmpl (nothing stripped)
  And the marker line reads `phase: direction` (natively — no rewrite needed)   # M5

Scenario: the boundary floor binds both lanes   # M6
  Given a full-lane task whose §1 Boundary: line still carries the template placeholder
  When `freeze --by <name> --cross` runs
  Then it dies "boundary_unfilled"
  And the same holds on a --fast scaffold

Scenario: lean-pass keeps the machine seams   # M4, R3
  Given the leaned template family
  When the form-tag and seam guards run (test_template_form_tags)
  Then zero offenses — every label, form tag, phase marker, Status/Outcome seam intact
  And each family file's byte count is below its recorded pre-task baseline
```

</scenarios>

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Grounding (the real code the contract will cite — gather BEFORE you freeze)
Touches (files · symbols · signatures): add.py:_render_template (fallback table {"TASK.md": _FALLBACK_TASK, "TASK.fast.md": _FALLBACK_TASK_FAST} — fast entry deleted) · add.py:cmd_new_task (render call `"TASK.fast.md" if fast else "TASK.md"` → always "TASK.md" + strip; the oneshot splice anchored on the `fast: true` line; the phase-marker rewrite that goes no-op) · add.py:_FALLBACK_TASK_FAST (delete) · add_engine/constants.py:_FAST_SECTIONS (create) · templates/TASK.md.tmpl (marker → direction · gains Boundary: · lean-pass) · templates/TASK.fast.md.tmpl (delete ×4 trees) · templates/MILESTONE.md.tmpl + personas/_template.md.tmpl + PROMPT.persona.md.tmpl (lean-pass only) · freeze readers kept byte-stable: boundary_unfilled (add.py ~1188) · ai_freeze_checklist_incomplete (~1234) · the §3 AI-verify sub-section reader (~2093)
Context (working folder): the 4 template trees — add-method/tooling/templates (canonical) · src/add_method/_bundled/tooling/templates · .add/tooling/templates · add-method/.add/tooling/templates
Honors (patterns / conventions): engine records / skill drives · stdlib-only kernel · doc/template edits alone do NOT repin, but add.py+constants edits DO (ENGINE_MD5 + ENGINE_PKG_MD5 + twins ×4) · 3 git-tracked twin trees byte-identical · splice-under-header idiom (the existing oneshot regex sub)
Seams consulted: .add/SEAMS.md#engine-md5-repin · .add/SEAMS.md#three-tree-parity
Anchors the contract cites: _render_template · cmd_new_task · _FAST_SECTIONS · _FALLBACK_TASK_FAST · boundary_unfilled · ai_freeze_checklist_incomplete
Issues/Risks: ~10 test files pin the OLD fast wording (test_fast_lane_template · test_fast_boundary_line · test_fastlane_ground_lite · test_dialect_vocab_lines · test_fast_lane_skips · test_fast_new_task_flag · test_ground_wiring · test_milestone_backlink · test_persona_required_domain_hint · test_template_form_tags's 7-file tree census) — migrate value-pins, delete wording-pins under the recorded authorization; ceiling-pin duplicates migrate in lockstep (byte-ledger lesson); the fast render GROWS vs today (~5.3KB → ~7KB post-lean) — accepted cost of one source of truth, recorded in the ledger
Related intent: thin-engine-loop exit criterion 2 (one template, fast = strict subset, family leaner) · GLOSSARY "route" (persona-routes-depth builds its route header ON this unified template)
Ground SHA: d9d4fac — stamped by freeze

### Contract (freeze the shape — the HARD, tamper-guarded core)

```
new-task <slug> [--fast | --oneshot | --full]   render source: templates/TASK.md.tmpl (the ONLY task template)
  full    -> render(TASK.md.tmpl)                                     (byte-shape of today minus the lean-pass)
  fast    -> strip_fast_sections(full) + splice header "fast: true"
  oneshot -> fast + splice "oneshot: true\ngate_mode: ai-plan-verify" + splice §3 "### AI-verify record" block
  _FAST_SECTIONS (add_engine/constants.py) = (
    "## 7 · OBSERVE", "### Deep checks", "### Live-verify evidence",
    "### Refute-read verdict", "### Advisor 3-lens verdict")
  strip rule: each key removes its heading line through the line before the next heading of
  same-or-higher level (### stops at next ###/##; ## stops at next ##), trailing separator absorbed
  subset law: set(lines(fast)) ⊆ set(lines(full)) ∪ {the spliced header lines}
  errors (test names, engine floors unchanged): fast_sections_leak · subset_broken ·
    boundary_unfilled · ai_freeze_checklist_incomplete
Schema: no state.json change — tasks[slug].fast stays the durable lane marker; templates/TASK.fast.md.tmpl ceases to exist
```

Glossary deltas: none ("route" is persona-routes-depth's)
Least-sure flag surfaced at freeze: [test] ~10 files pin the OLD fast template's condensed wording — the census is long; a missed value-pin costs one extra red-fix loop, no floor at risk.
Status: FROZEN @ v2 — approved by Tin Dang 2026-07-17 (v2 = scope widened to the skill trees so the fast-lane guide wording tracks the one-template truth; contract shape unchanged)
Reported: yes — the freeze report (banner/ARC/SHAPE) rendered before this froze

### Build-strategy (the intended approach — SOFT: preferred; the builder self-improves and records what it ACTUALLY did at verify)
Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/` `add-method/.add/tooling/` `.add/tooling/` `add-method/skill/` `.claude/skills/` `.add/SEAMS.md` `tmp/`
Strategy (ordered batches): 1. red suite test_template_unify.py (subset law · drop-set exactness · file-gone · oneshot splice · boundary floor · native marker · family byte ledger) · 2. _FAST_SECTIONS + strip helper in the engine; cmd_new_task renders TASK.md always, splices fast/oneshot; delete _FALLBACK_TASK_FAST + fallback entry · 3. TASK.md.tmpl: marker → `phase: direction`, §1 gains Boundary:, lean-pass · 4. delete TASK.fast.md.tmpl ×4 trees; lean MILESTONE/persona/PROMPT templates (grep pinned phrases BEFORE each cut) · 5. migrate/delete the ~10 fast-pinning test files (floors migrated, wording deleted under the authorization) · 6. repin ENGINE_MD5+PKG · sync 4 twins · full suite · byte ledger
Approach (domain strategy): compute the variant, never store it — the fast lane becomes a pure function of the one template (derived-render, from §1 chosen framing)
Data strategy: _FAST_SECTIONS is an ordered tuple of heading literals in constants.py (beside PHASES); the strip is line-span deletion on the rendered string — agrees with the Contract's strip rule; no persisted shape changes
Pattern: the oneshot splice-under-header idiom (cmd_new_task) extended to the fast header + AI-verify block; constants own policy, add.py owns mechanics (phase-collapse-3 precedent)
Optimization stance: template bytes per scaffold — budget: every family file smaller than today; ⚠ least-sure facet: the fast render grows ~+1.7KB vs the old fast template (accepted, ledgered)
Persona (required): generic (no project persona covers template/render surgery; the roster's add-build drives the batches)
Spawn isolation (default): inline build (sequential, single surface — inline-over-heavy-spawns feedback); any parallel test-migration spawn uses disjoint file sets in the shared tree (phase-collapse-3 precedent)
Known-problem fixes: pinned-phrase census is LONG → grep each cut phrase across tests before deleting it · ceiling-pins duplicate → migrate byte-ledger pins in lockstep · rendered-marker regex sub must stay (older bundled twins may lag one release) → keep the sub, document as no-op · tmp/ scaffolds tripping scope → tmp/ declared

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every §2 scenario has exactly one red test; family ledger covers all 4 lean-pass files
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_fast_is_strict_subset: arrange full+fast scaffolds in a temp project / act line-set diff / assert set(fast) ⊆ set(full) ∪ spliced headers · covers: M2, R:subset_broken
  - test_fast_drops_exactly_fast_sections: arrange both renders / act compare present headings / assert the five _FAST_SECTIONS headings absent in fast, EVERY other full heading present · covers: M2, R:fast_sections_leak
  - test_fast_template_file_gone: arrange repo tree / act glob TASK.fast.md.tmpl across the 4 template trees + grep _FALLBACK_TASK_FAST in add.py / assert zero hits · covers: M1
  - test_oneshot_keeps_ai_verify_floor: arrange --oneshot scaffold / act freeze without the AI-verify boxes ticked / assert refused ai_freeze_checklist_incomplete + headers oneshot: true/gate_mode present · covers: M3
  - test_default_lane_unchanged_and_native_marker: arrange plain new-task / act read scaffold / assert every §1–§7 heading present + line 6 literally `phase: direction` with no legacy names in the marker comment · covers: M5
  - test_boundary_floor_both_lanes: arrange full AND fast scaffolds / act freeze with Boundary: placeholder untouched / assert boundary_unfilled refused on BOTH · covers: M6
  - test_family_byte_ledger: arrange the 4 family templates / act stat bytes / assert each under its recorded pre-task size (ledger pinned in-test) with machine-read lines (form tags · labels · GATE RECORD) still present · covers: M4
</test_plan>

Tests live in: `add-method/tooling/` (file: test_template_unify.py) · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

> The change plan — grounding + contract + build-strategy — was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope, follow the strategy (improve on it if the code teaches you better), and touch no test or the frozen contract.
Strategy actually used: as planned, one deviation — the drop-set red test contradicted the frozen strip rule (a ## key absorbs its nested ### headings); fixed the TEST to the contract + sanctioned via re-cross --by (2026-07-17). Fixture ripple was wider than the §3 flag guessed: 6 freeze-fixture files needed a Boundary fill (the new M6 floor firing as designed), not just the ~10 fast-pinning files.
Safety rule (feature-specific): every freeze-reader floor (boundary_unfilled · ai_freeze_checklist_incomplete · least-sure flag · form-tag census) must fire on renders of the ONE template — no floor may vanish with the deleted file
Code lives in: `add-method/tooling/` (+ the 3 twin trees, synced at batch 6)
Constraints: do NOT change any test or the frozen §3 contract; stay inside the §3 Build-strategy Scope; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [ ] all tests pass
- [ ] coverage did not decrease
- [ ] no test or contract was altered during build
- [ ] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [ ] concurrency / timing of the risky operation is safe
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] `python3 -m unittest test_template_unify -v` prints `Ran 13 tests` + `OK` (7 reds flipped, 6 floor pins held) — confirmed by the run transcript 2026-07-17
- [x] `ls templates/TASK.fast.md.tmpl` fails in all 4 template trees and `grep _FALLBACK_TASK_FAST add.py` prints nothing — confirmed by the shell output (find shows only worktree/benchmark archives)
- [x] a temp-project `new-task probe --fast` scaffold's line-set is ⊆ the full scaffold's ∪ {`fast: true`} — confirmed by test_fast_is_strict_subset green
- [x] full suite `python3 -m unittest discover` green — Ran 3092 tests, OK (scratchpad/full-suite-tu2.log); count −22 vs 3114 = test_fast_lane_template.py deleted (−35 defs) + 13 new
- [x] `md5 add.py` matches the re-aimed ENGINE_MD5 8eaca350… across all 4 tooling twins; PKG ed7bf3e1… — confirmed by the distinct=1 parity sweep + test_engine_package_skeleton green
Byte ledger (family lean-pass): TASK.md.tmpl 12209→12015 (Boundary line ADDED) · MILESTONE 4211→3729 · PROMPT.persona 3225→3046 · personas/_template 6922→5411 — every machine-read anchor pinned green (test_family_byte_ledger).

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [ ] DIALECT — tests speak the same value formats the spec's examples use (spec-dialect floor): <what confirmed>
- [ ] WIRING (code) — every new symbol is referenced; record where / how confirmed
- [ ] DEAD-CODE (code) — no new unused or orphaned symbol introduced
- [ ] SEMANTIC (prose / non-code) — read in full, not skimmed: <what read · what confirmed>

### Live-verify evidence — confirm the §3 PLAN grounding anchors still resolve (fill at the gate)
> Re-resolve every symbol the §3 Contract cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [ ] every symbol the §3 Contract cites still resolves in the current tree — confirmed by <how / where>
- [ ] any anchor that moved/renamed since Ground SHA is named here, not left silent

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: <EARNED | NOT-EARNED>
By: <self | agent-id> · adversarially checked: <what was probed>

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: <agent-id | self>
1. Security: <CLEAR | HARD-STOP: finding>
2. Concurrency: <CLEAR | RESIDUE: finding>
3. Architecture: <CLEAR | RESIDUE: finding>
Verdict: <PASS | HARD-STOP>
Residue: <none | summary>
Binding: <yes — mechanical | advisory — <sensitivity>>

### GATE RECORD
Reported: yes — gate report (banner/ARC/SUMMARY/EVIDENCE/FLAG) rendered 2026-07-17; gap closed pre-gate (scope v2 + skill-tree fix) per the human's ratify
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-17

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): scaffold bytes per lane (fast render ~7.0KB vs old 5.3KB — accepted; watch real-task friction) · any tree resurrecting TASK.fast.md.tmpl (test_fast_template_gone_from_every_tree) · family byte ceilings (test_family_byte_ledger re-pins on the next lean-pass)

### Decisions (ADR)
- [AI] specify — chose subset-by-construction drop-set applied at render; rejected keep two templates and lint them into agreement (rejected — two sources of truth; template drift is this repo's recorded failure mode) · byte-prefix truncation (rejected — fast's value is FEWER whole sections, not a shorter file)
- [human] freeze — froze §3 @ v2 (approved by Tin Dang 2026-07-17 (v2 = scope widened to the skill trees so the fast-lane guide wording tracks the one-template truth; contract shape unchanged))
- [AI] build — approach: compute the variant, never store it — the fast lane becomes a pure function of the one template (derived-render, from §1 chosen framing)
- [AI] build — data strategy: _FAST_SECTIONS is an ordered tuple of heading literals in constants.py (beside PHASES); the strip is line-span deletion on the rendered string — agrees with the Contract's strip rule; no persisted shape changes
- [AI] build — pattern: the oneshot splice-under-header idiom (cmd_new_task) extended to the fast header + AI-verify block; constants own policy, add.py owns mechanics (phase-collapse-3 precedent)
- [AI] build — optimization stance: template bytes per scaffold — budget: every family file smaller than today; ⚠ least-sure facet: the fast render grows ~+1.7KB vs the old fast template (accepted, ledgered)
- [AI] build — strategy used: as planned, one deviation — the drop-set red test contradicted the frozen strip rule (a ## key absorbs its nested ### headings); fixed the TEST to the contract + sanctioned via re-cross --by (2026-07-17). Fixture ripple was wider than the §3 flag guessed: 6 freeze-fixture files needed a Boundary fill (the new M6 floor firing as designed), not just the ~10 fast-pinning files.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).
- [SPEC · open] skill-loop-fold folds the 7 phase guides to the 3-phase walk — fast-lane.md's step list still narrates the OLD per-phase beats around the fixed line (evidence: add-method/skill/add/phases/fast-lane.md steps 2-4)
- [SPEC · open] the old fast template pre-seeded the `Least-sure flag surfaced at freeze:` LABEL; the unified render does not — the floor still refuses, but the affordance is gone; consider a template label or a freeze hint (evidence: unflagged_freeze fired on this task's own first freeze)

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
- [TDD · open] a new freeze floor (boundary_unfilled both lanes) ripples into EVERY fixture that freezes a rendered scaffold — grep the freeze-helper idiom BEFORE the build, not after the full suite (evidence: 6 files, 33 reds, all one fixture line)
- [ADD · open] when a red test contradicts its own frozen contract, fix the TEST to the contract + re-cross --by — never bend the build (evidence: drop-set test's nested-### bug, re-crossed 2026-07-17)

