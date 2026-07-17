# TASK: add a drafted-blank ## Strategy slot to MILESTONE.md.tmpl + engine handling

slug: strategy-section · created: 2026-07-16 · stage: mvp
milestone: strategy-intake
autonomy: auto   <!-- level: manual<conservative<auto — lower for high-risk (`add.py autonomy set`). Multi-component? a `component: <name>` line (.add/components.toml) joins that root to §5 Scope. Relations: `--depends-on`/`--extends`/`--relates-to` task edges (GLOSSARY; `check` validates). -->
phase: tests   <!-- specify→plan→tests→build→verify→done; plan unites grounding + frozen contract + build strategy -->
<!-- high-risk/method-defining? declare `risk: high` on the slug line + lowered autonomy — the engine refuses an unguarded completion (`unguarded_high_risk_auto`). A comment is never a declaration. -->

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: a drafted-blank `## Strategy` slot in the milestone template
Framings weighed: drafted-blank template section like Close/Release (chosen) · an engine-parsed required section · a separate STRATEGY.md file
Must:
<must>
  - M1 the milestone template (`MILESTONE.md.tmpl`) carries a `## Strategy` section, drafted-blank (placeholder guidance + `<...>` slots, exactly like `## Close` / `## Release steps`)
  - M2 a milestone created via `add.py new-milestone` renders the `## Strategy` slot into its `MILESTONE.md`
  - M3 the `## Strategy` section is placed OUTSIDE the engine-parsed spans (`## Tasks`, `## Exit criteria`) so the task-DAG parse and `milestone-confirm`/`check` are byte-behaviour-unchanged
  - M4 all three `MILESTONE.md.tmpl` twins (source · `_bundled` · `.add` mirror) stay byte-identical
</must>
Reject:
<reject>
  - R1 a new-milestone flow that HOLDS or warns on an UNFILLED `## Strategy` -> "strategy_must_stay_soft" (drafted-blank is valid; Strategy is advisory, never a gate)
  - R2 placing `## Strategy` INSIDE the `## Tasks` span (between `## Tasks` and the next `## `) so the depends-on/DAG parse changes -> "tasks_parse_corrupted"
</reject>
After:
<after>
  - every new `MILESTONE.md` carries a drafted-blank `## Strategy` slot; existing milestone parsing (Tasks DAG · confirm · check) is unchanged; the 3 template twins are byte-identical
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the engine does NOT need to PARSE `## Strategy` for this task — lowest confidence because add.py already parses some milestone `## ` sections (Tasks DAG @ ~1336; a pre-confirm section check @ ~4828); if wrong: engine section-handling creeps in and this task grows past a template edit
  - [ ] `## Strategy` placed AFTER `## Exit criteria` (before `## Close`) leaves every engine-parsed span intact — confirm by a red test on the Tasks-DAG parse + a live new-milestone
</assumptions>

<!-- EXIT: the specify guide's exit_gate binds (rules + ranked ⚠ assumptions). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: new milestone renders the Strategy slot   # M1, M2
  Given a project with the strategy-aware MILESTONE.md.tmpl
  When I run `add.py new-milestone demo`
  Then the created MILESTONE.md contains a `## Strategy` heading, drafted-blank
  And the `## Tasks` and `## Exit criteria` sections are still present and parseable

Scenario: the Tasks DAG parse is unchanged   # M3, R2
  Given a MILESTONE.md with a `## Strategy` section and N depends-on task rows
  When the engine parses the `## Tasks` span for the DAG
  Then it reads exactly the N task rows
  And no `## Strategy` line is mistaken for a task row

Scenario: Strategy stays soft — never a gate   # R1
  Given a milestone whose `## Strategy` slot is left drafted-blank
  When I run `add.py milestone-confirm` and `add.py check`
  Then both succeed with no strategy-related hold or warning
  And the milestone confirms exactly as before this section existed

Scenario: the three template twins stay identical   # M4
  Given the strategy-aware MILESTONE.md.tmpl
  When I md5 the source, _bundled, and .add-mirror copies
  Then all three hashes are equal
```

</scenarios>

<!-- EXIT: the scenarios guide's exit_gate binds. -->

---

## 3 · PLAN — the change plan: ground · contract · build-strategy ▸ docs/05-step-3-plan.md

### Grounding (the real code the contract will cite — gather BEFORE you freeze)
Touches (files · symbols · signatures): `add-method/tooling/templates/MILESTONE.md.tmpl` (+ `_bundled` + `.add` twins) — insert one `## Strategy` section between the `## Exit criteria` and `## Close — ship review` headings. NO `add.py` symbol: `new-milestone` renders the template verbatim, so the slot flows without an engine edit.
Context (working folder): `.add/milestones/*/MILESTONE.md` (rendered instances) · `scope.md` (the guide that FILLS Strategy — a later task, not this one).
Honors (patterns / conventions): the drafted-blank section convention of `## Close` / `## Release steps` (placeholder `<...>` slots + a guidance `>` blockquote); the 3-tree template-parity pattern.
Seams consulted: none (no scope-token grammar touched).
Anchors the contract cites: the `## Exit criteria` heading (insert AFTER) · the `## Close — ship review` heading (insert BEFORE) · the `## Tasks` DAG-parse span (add.py ~1336).
Issues/Risks: add.py reads the `## Tasks` span up to the next `## ` heading (~1336) — a section placed INSIDE that span would be mis-read as a task row (R2). Safe placement is AFTER `## Exit criteria`. No engine parse consumes `## Strategy` this task.
Related intent: the `strategy-intake` milestone rationale (the persona-led strategy session); GLOSSARY term "milestone strategy".
Ground SHA: 5cd78b1 — stamped by freeze

### Contract (freeze the shape — the HARD, tamper-guarded core)

```
MILESTONE.md.tmpl gains ONE section, inserted between `## Exit criteria (...)` and
`## Close — ship review (...)`:

    ## Strategy   (AI-drafted WITH the human — the optimized task plan; SOFT/advisory like §5; drafted-blank for a micro/--fast milestone)
    > The persona-led strategy over THIS milestone's tasks — sequencing, freeze-first contracts,
    > parallel waves, the first unblocking slice, tradeoffs named. SOFT: the preferred plan; the
    > loop may deviate and records what it did. Drafted-blank is valid (risk-proportional).
    - Approach (sequencing): <risk-first | dependency-first | first-slice-unblocks — and WHY>
    - Freeze-first: <the shared/risky contract to freeze before the rest>
    - Waves (parallel): <task slugs that can run concurrently behind frozen contracts — or "sequential">
    - Tradeoffs weighed: <alternative decompositions considered + why this one>

Invariants (HARD):
  - placement AFTER `## Exit criteria`, BEFORE `## Close` — NEVER inside the `## Tasks` span
  - the engine does NOT parse or gate on `## Strategy` (no reject code, no confirm/advance/check hold)
  - all 3 MILESTONE.md.tmpl twins byte-identical
  - no add.py edit, no ENGINE_MD5 repin (template renders verbatim)
```

Glossary deltas: milestone strategy: the SOFT, persona-led optimized task plan recorded in a milestone's `## Strategy` section.
Least-sure flag surfaced at freeze: whether placing `## Strategy` after `## Exit criteria` leaves the `## Tasks` DAG parse (add.py ~1336) and the pre-confirm section scan (~4828) byte-behaviour-unchanged — a dedicated red test asserts the DAG reads exactly N task rows and confirm/check stay clean [contract/test]
Status: FROZEN @ v1 — approved by tindang
Reported: <yes — the freeze report (banner/ARC/SHAPE) rendered before this froze | no>

### Build-strategy (the intended approach — SOFT: preferred; the builder self-improves and records what it ACTUALLY did at verify)
Scope (may touch): `add-method/tooling/templates/MILESTONE.md.tmpl` · `add-method/src/add_method/_bundled/tooling/templates/MILESTONE.md.tmpl` · `.add/tooling/templates/MILESTONE.md.tmpl` · `add-method/tooling/test_strategy_section.py`
Strategy (ordered batches): 1. write the RED test (renders the slot · Tasks-DAG reads exactly N rows · confirm/check clean · 3-twin md5 parity) 2. add `## Strategy` to the SOURCE template after `## Exit criteria` 3. sync the 2 twins byte-for-byte 4. green.
Approach (domain strategy): a drafted-blank template section mirroring the `## Close` / `## Release steps` convention — NO engine parsing (renders verbatim via `new-milestone`), so zero `engine_pin` churn; derives from the "drafted-blank section like Close/Release" framing chosen in §1.
Data strategy: n/a — static template text; the rendered `MILESTONE.md` instance is the only artifact, and it must agree with the Contract's placement invariants.
Pattern: the existing drafted-blank section convention (`## Close`, `## Release steps`) + the 3-tree template-parity pattern.
Optimization stance: correctness-first, no perf budget — ⚠ the facet I trust least is placement NOT disturbing the `## Tasks` DAG parse; a dedicated red test asserts the parse reads exactly N task rows.
Persona (required): methodology-engine-dev — the method/engine domain stance (advisory, never lowers a gate).
Spawn isolation (default): inline — sequential template edit, no subagent spawn (per the inline-build preference).
Known-problem fixes: Tasks-DAG parse truncation → place AFTER `## Exit criteria` + test the parse reads exactly N rows · twin drift → md5 3-parity test · covert-gate creep → test milestone-confirm/check stay clean with Strategy drafted-blank.

<!-- The freeze IS the one approval — it freezes the whole PLAN; lead it with the bundle's lowest-confidence flag (§1 ⚠ feeds it; a flag may point at any part — run.md). The Contract shape is HARD (tamper-guarded); Grounding + Build-strategy are SOFT (the builder may improve on the strategy, recording actual at §5/verify). Approved -> Status: FROZEN @ vN — approved by <name>; changing the frozen Contract = change request back to SPECIFY. Scope tokens, backticked, on the Scope line: `./…` = this task dir · a token with "/" = project root · a bare name = sibling of the previous token's dir · a DIRECTORY token covers its whole subtree · outside-root resolutions drop fail-closed · absent line = UNDECLARED (grandfathered — an undeclared task is never retro-red). The plan guide's exit_gate binds: frozen · every rejection contracted · names match GLOSSARY · anchors grounded · flag surfaced. -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: <e.g. 90%>
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_<scenario>: arrange <Given> / act <When> / assert <Then> + assert <unchanged> · covers: <M#, R:code — optional>
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir · a token with "/" = the project root · a bare name = a sibling of the previous token's dir · a directory counts its *.py files (non-recursive) · declared counts marked † · outside the project root counts 0 -->

<!-- EXIT: the tests guide's exit_gate binds (red for the RIGHT reason). -->

---

## 5 · BUILD — AI writes the code (execution) ▸ docs/07-step-5-build.md

> The change plan — grounding + contract + build-strategy — was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope, follow the strategy (improve on it if the code teaches you better), and touch no test or the frozen contract.
Strategy actually used: <fill at VERIFY — the strategy you ACTUALLY used (or "as planned"); harvested into the §7 Decisions (ADR) block as the [AI] build decision>
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the frozen §3 contract; stay inside the §3 Build-strategy Scope; allow-list packages only; ask if unclear.

<!-- Scope-lock source: the §3 `Scope (may touch)` line; an out-of-scope build fails the gate (scope_violation); the build guide's exit_gate binds. -->

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
- [ ] <observable outcome a correct build must produce> — confirmed by <how / where>
- [ ] <another observable outcome> — confirmed by <evidence seen>

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
Reported: <yes — the gate report (banner/ARC) rendered before this outcome recorded | no>
Outcome: <PASS | RISK-ACCEPTED | HARD-STOP>
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: <name> · date: <date>

<!-- Security is ALWAYS HARD-STOP; record exactly one outcome — no silent pass. The Advisor 3-lens and Refute-read verdicts are audit-measured (`advisor_verdict_unrecorded` · `refute_unrecorded`), never engine-blocked; a human spot-audit backstops anything unrecorded. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency — the §3 Build-strategy Optimization stance budget is a monitor here, not just an intention>

### Decisions (ADR)
<harvested at done from §1/§3/§5/§6 — do not hand-edit; one actor-tagged line per decision, refilled only while this placeholder stands>

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
