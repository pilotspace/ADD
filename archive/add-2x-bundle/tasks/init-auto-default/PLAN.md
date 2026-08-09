# TASK: Project seeds autonomy: auto by default at init

slug: init-auto-default · created: 2026-06-10 · stage: mvp
autonomy: conservative   <!-- lowered: a trust-layer touch (the autonomy machinery itself) — a human owns the verify gate. NOT risk: high — the change is mechanical/additive/reversible and does not move the default. Ratify this risk call at the freeze. -->
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: project-level autonomy default — `init` DECLARES `autonomy: auto` in PROJECT.md;
`new-task` INHERITS that declared default into each new TASK.md; `status` SURFACES it. The
autonomy posture becomes explicit, project-scoped, and inheritable — today it is a constant
buried in the TASK.md template (every task is already auto, but nothing declares it).
Framings weighed: inherit (chosen) · declare-only · init --autonomy flag
<!-- inherit: PROJECT.md declares the default -> new-task reads it -> task inherits -> status surfaces;
     the declared line is LOAD-BEARING (change it, new tasks follow).
     declare-only (REJECTED): add a PROJECT.md line for visibility but keep new-task's hardcoded seed —
     the prose≠enforcement trap we just folded a delta about; the declared default LIES the moment it
     is edited (the seed wins).
     init --autonomy flag (DEFERRED → §7 / milestone Out): a CLI knob for a non-auto default at init —
     YAGNI for "auto default"; the goal is auto-by-default, not configurable-at-init. -->
Must:
<must>
  - `init` writes a header line `autonomy: auto` into PROJECT.md
  - `new-task` seeds the new TASK.md `autonomy:` line from the project's DECLARED default (inherit), not a hardcoded constant
  - a project that declares a NON-auto default (e.g. `autonomy: conservative`) has that default flow into every new task it creates
  - when PROJECT.md has NO autonomy line, `new-task` inherits the method default `auto` (established v7 semantics: absent = auto)
  - when PROJECT.md's autonomy line is GARBLED/unrecognized, `new-task` seeds `conservative` (fail-SAFE — never silently `auto`) and warns on stderr
  - `status` surfaces the project autonomy default every session
</must>
Reject:
<reject>
  - PROJECT.md autonomy line present but unrecognized (e.g. `autonomy: yolo`) -> seed is forced to `conservative` + a `garbled_project_autonomy` WARNING (new-task still proceeds — degrade-and-flag, NOT refuse-to-create) -> "garbled_project_autonomy"
</reject>
After:
<after>
  - a freshly-init'd PROJECT.md carries `autonomy: auto`
  - every new task created under a project inherits that project's declared autonomy default
  - `status` shows the project autonomy default
  - a corrupt project autonomy line NEVER silently yields an unsupervised (`auto`) task
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [spec] The BEHAVIORAL delta over today is near-zero — `new-task` already seeds `auto` from the hardcoded template; the real deliverable is making the posture EXPLICIT + project-scoped + INHERITABLE, so a project can declare a non-auto default that FLOWS into new tasks. Lowest confidence because the user said "auto default" (not "configurable default"): if they want only the visible declaration and NOT runtime inheritance, the read-path + the conservative-inherits test are wasted. If wrong: ~30 lines of read-path + 1 test drop; the declared PROJECT.md line stays. (Read as INHERIT because the milestone exit criterion says "inherited" and declare-only is the prose≠enforcement trap just folded into foundation-version 23.)
  - [ ] [contract] The fail-safe rung for a GARBLED project autonomy line is `conservative` + warn, NOT a hard die — new-task still creates the task. If wrong (should die): a typo in PROJECT.md would block ALL new-task creation (over-strict). Chosen degrade-and-flag because creating a task is benign and the always-valid seed + warn covers the risk.
  - [ ] [contract] This task is NORMAL-risk + `autonomy: conservative` (a human owns the verify gate for a trust-layer touch), NOT `risk: high` (the change is mechanical/additive/reversible and does not move the default). Ratify the risk call at the freeze — judging high-risk is human judgment.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: init writes the project autonomy default
  Given a fresh empty directory
  When I run `init --name demo`
  Then PROJECT.md contains a header line `autonomy: auto`

Scenario: a new task inherits the auto default (existing seed contract unchanged)
  Given a project init'd with `autonomy: auto` in PROJECT.md
  When I run `new-task fresh`
  Then fresh/TASK.md's header contains `autonomy: auto`
  And the established new-task seed contract is unchanged

Scenario: a NON-auto project default flows into a new task   # LOAD-BEARING — proves inheritance is real
  Given a project whose PROJECT.md declares `autonomy: conservative`
  When I run `new-task t2`
  Then t2/TASK.md's header contains `autonomy: conservative`
  And the seed is NOT `auto`

Scenario: an absent project autonomy line defaults to auto
  Given a PROJECT.md with no `autonomy:` line
  When I run `new-task t3`
  Then t3/TASK.md's header contains `autonomy: auto`

Scenario: a garbled project autonomy line degrades fail-safe (rejection)
  Given a PROJECT.md whose line reads `autonomy: yolo` (unrecognized)
  When I run `new-task t4`
  Then t4/TASK.md's header contains `autonomy: conservative`
  And a `garbled_project_autonomy` warning is emitted
  And the seed is NEVER `auto` (never silently unsupervised)

Scenario: status surfaces the project autonomy default
  Given a project init'd with `autonomy: auto`
  When I run `status`
  Then the output names the project autonomy default `auto`
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
init <dir> --name <n> [--stage <s>]
  -> PROJECT.md gains a header line:  autonomy: auto

new-task <slug> --title <t>
  -> TASK.md header line:  autonomy: <level>
     where <level> = _project_autonomy(root):
       declared & recognized   -> that rung (manual|conservative|auto)
       no `autonomy:` line      -> "auto"          (method default; v7 absent = auto)
       garbled / unrecognized   -> "conservative"  (fail-SAFE) + warn "garbled_project_autonomy"

status
  -> prints a line naming the project autonomy default, e.g.  project autonomy: auto

_project_autonomy(root: Path) -> str        # PURE read-path; mirrors _project_goal,
  # reuses the existing _AUTONOMY_LINE_RE / _autonomy_level (member | None=absent | "?"=garbled)
  # PREREQUISITE (satisfied @ 55d64d9): that reader is now anchored to a declaration
  # position, so reading PROJECT.md will NOT match the §Spec/§Key-Decisions prose that
  # mentions `autonomy: <x>` — _project_autonomy is collision-safe by construction.

Schema (files touched, all ×3 trees — canonical · .add dogfood · _bundled):
  - templates/PROJECT.md.tmpl : + header line `autonomy: auto`
  - templates/TASK.md.tmpl    : line 4 `autonomy: auto` -> `autonomy: {{autonomy}}`
  - add.py _FALLBACK_TASK      : stays a VALID fallback (keeps a concrete safe rung)
  - add.py cmd_new_task        : passes autonomy=_project_autonomy(root) into _render_template
  - add.py cmd_status          : prints the project autonomy default line
  - engine_pin.py ENGINE_MD5   : re-pinned ×3 after add.py changes
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-10
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

Least-sure flag surfaced at freeze: [spec] does "init in auto" mean runtime INHERITANCE
(PROJECT.md drives new-task; chosen) or only a VISIBLE declaration (task seed stays hardcoded)?
— highest cost if wrong; see the §1 ⚠. Secondary: [contract] garbled → conservative+warn (degrade,
not die); [contract] this task = normal-risk + conservative (ratify at freeze).

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 95% of the new read-path (`_project_autonomy`) + the new-task seed branch
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_init_writes_autonomy_auto: act `init` / assert PROJECT.md contains `autonomy: auto`
  - test_new_task_inherits_auto: arrange init'd project / act `new-task` / assert TASK.md header `autonomy: auto` (existing seed contract held)
  - test_non_auto_default_inherited: arrange PROJECT.md `autonomy: conservative` / act `new-task` / assert TASK.md `autonomy: conservative` + assert NOT `auto`   # LOAD-BEARING
  - test_absent_project_autonomy_defaults_auto: arrange PROJECT.md with no autonomy line / act `new-task` / assert `autonomy: auto`
  - test_garbled_project_autonomy_failsafe_conservative: arrange `autonomy: yolo` / act `new-task` / assert seed `conservative` + `garbled_project_autonomy` warning + assert seed NOT `auto`
  - test_status_surfaces_project_default: arrange init'd project / act `status` / assert output names project autonomy `auto`
  - test_project_autonomy_helper_resolves: unit — `_project_autonomy(root)` returns auto (declared), conservative (declared non-auto), auto (absent), conservative (garbled)
  - test_templates_carry_autonomy_3_trees: assert PROJECT.md.tmpl has `autonomy: auto` and TASK.md.tmpl has `{{autonomy}}` across all three template trees
</test_plan>

Tests live in: `add-method/tooling/test_init_auto_default.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): `_project_autonomy` is a PURE fail-SAFE read — a missing/unreadable/garbled PROJECT.md NEVER resolves to `auto`; absent → method-default `auto`, garbled → `conservative`. Mirror `_project_goal`'s fail-closed OSError handling.
Code lives in: `add-method/tooling/add.py` (+ ×3 template/engine sync)
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 734/734 green (`unittest discover`), incl. the 8 init-auto-default + 9 reader-anchor
- [x] coverage did not decrease — new code (`_project_autonomy`/`_token`, cmd_new_task seed+warn, cmd_status line) all exercised by the 17 new tests; no code removed
- [x] no test or contract was altered during build — only NEW test files added; the one out-of-contract JSON key (`project_autonomy`) was REVERTED when the frozen status --json surface test caught it; frozen §3 untouched during build
- [x] concurrency / timing of the risky operation is safe — `_project_autonomy` is a PURE read; TASK.md still written via `_atomic_write`; no shared state, no new IO race
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only (`re`); reads PROJECT.md read-only; no secrets
- [x] layering & dependencies follow CONVENTIONS.md — read-path mirrors `_project_goal` (fail-closed OSError); reuses the anchored `_autonomy_level`; no new layer
- [x] a person reviewed and approved the change — Tin confirmed PASS at the conservative gate, 2026-06-10

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_project_autonomy` referenced at cmd_new_task:437 (seed) + cmd_status:789 (surface); `_project_autonomy_token` at cmd_new_task:442 (garble warn) + inside `_project_autonomy`. Every new symbol is reached.
- [x] DEAD-CODE (code) — no new unused/orphaned symbol; both helpers have live callers
- [x] SEMANTIC (prose / non-code) — read in full: PROJECT.md.tmpl + TASK.md.tmpl (×3 trees, byte-identical), .add/PROJECT.md header declaration, and the `project autonomy:` status line — all name the inherited posture consistently with the GLOSSARY `autonomy level` term

### GATE RECORD
Outcome: PASS — feature green (734/734), build held the frozen contract (the one out-of-contract JSON key was caught + reverted), no security finding
Reviewed by: Tin (human) · date: 2026-06-10

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): rate of `garbled_project_autonomy` warnings (a spike means projects are hand-editing PROJECT.md autonomy badly); new tasks whose seed ≠ project default (would mean inheritance regressed).
Spec delta for the next loop: the autonomy posture is now project-scoped + inheritable — the next task (`goal-auto-ready-gate`) builds the goal-clarity bar ON this default; whether a clarified goal can RELAX the freeze gate stays deferred to its own milestone.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] a declaration-token reader must anchor to a declaration POSITION (line-start or `·`-separator) — a freeform H1 title or quoted prose containing `token: value` must never be read as a declaration, and the symmetric hazard (a title faking a lowered rung) can defeat a guard (evidence: init-auto-default titled "…autonomy: auto…" read as `auto` despite declaring `conservative`, `_autonomy_level -> auto`; fixed @ 55d64d9, anchoring both the autonomy and risk readers).
- [SDD · folded] a project's autonomy posture is a project-level INHERITABLE default (`auto`), declared in PROJECT.md and surfaced in status — not a constant buried in the task template; `new-task` inherits the declared rung, fail-SAFE (absent→auto, garbled→conservative) (evidence: init-auto-default shipped `_project_autonomy` + the load-bearing `test_non_auto_default_inherited`).
- [SDD · folded] an `init --autonomy <level>` CLI knob (a non-auto project default set at init) was DEFERRED as YAGNI for "auto default" — record it so a future "configurable default" need is not re-discovered from scratch (evidence: weighed + rejected in the init-auto-default framings at freeze).
- [ADD · folded] the build must stay INSIDE the frozen contract even for "harmless additive" changes — a bonus `project_autonomy` key on `status --json` was caught by the frozen-surface guard and reverted, not test-edited (evidence: test_json_surface_frozen fired `json_surface_unsanctioned_key`; the JSON key was removed, the frozen test left intact).
