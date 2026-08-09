# TASK: Project-extensible sensitivity glossary + AI guide

slug: sensitivity-glossary · created: 2026-06-29 · stage: mvp · risk: high · sensitivity: architecture
autonomy: conservative   <!-- LOWERED: method-defining (advisor-gated-autonomy milestone) — the human owns the verify gate. Original note: inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. Multi-component repo (monorepo/multi-repo)? add a `component: <name>` line (declared in `.add/components.toml`) to ADD that component's root to your §5 Scope; omit for single-component projects (byte-identical default). -->
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
  - `add.py:_SENSITIVITY_RE` + `_task_sensitivity(hdr)` (risk-sensitivity-taxonomy) — today validates against the CLOSED base `_SENSITIVITY_VALUES`. This task widens validation to base ∪ project-declared domain values; the reader gains an optional `valid` set.
  - `add.py:cmd_freeze` `sensitivity_invalid` step · `cmd_status` sensitivity render · `_guarantee_lint_notices` `sensitivity_unset` — the three callers that must validate/surface against the UNION.
  - `add_engine/constants.py:_SENSITIVITY_VALUES` (the universal base, unchanged) + `SETUP_FILES` (GLOSSARY.md is already a setup file).
  - GLOSSARY.md — flat `Term: definition` lines today, NO `##` subsections; the engine has NO glossary reader yet (this adds the first). A new `## Sensitivity classes` section will hold `- <token>: <definition>` domain lines.
  - `cmd_init` / the GLOSSARY.md template (SETUP_FILES seeding) — seeds the `## Sensitivity classes` section on init.
  - skill: `add-method/skill/add/` (canonical) + `_bundled/skill/add/` mirror + `SKILL.md` pointer — a new on-demand guide; ripples into the 3-tree skill parity + the lean-fence token budget + the wording-lint registries (known from component-method-docs).
Context (working folder): user request — "allow AI to add a sensitivity glossary, kept up to date, belonging to each project's domain." Builds on risk-sensitivity-taxonomy (base enum shipped + gated). Decided with the human: domain values live in GLOSSARY.md (base ∪ project); guide = a dedicated skill guide + a status/check nudge; book chapter deferred to docs-align (9/9).
Honors (patterns / conventions): the base four stay UNIVERSAL (advisor-gate-relax keys off `mechanical`); projects EXTEND, never replace · engine validates a human/AI-declared token, never classifies · fail-safe readers (no section → base only) · PURE/read-only resolver. BUILD TARGET = 3 git-tracked engine trees (ENGINE_MD5+ENGINE_PKG_MD5) AND 3 git-tracked skill trees (skill parity) — edit canonical, re-sync mirrors, re-pin.
Anchors the contract cites: `_project_sensitivity_values(root)` (new) · `_task_sensitivity(hdr, valid=None)` (widened) · `cmd_freeze`/`cmd_status`/`_guarantee_lint_notices` union validation · GLOSSARY.md `## Sensitivity classes` section · the new skill guide + SKILL.md pointer

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Project-extensible sensitivity glossary (base ∪ domain) + an AI guide
Framings weighed: domain values in a GLOSSARY.md `## Sensitivity classes` section (chosen — the human said "glossary") · a `sensitivity-values:` declaration line in PROJECT.md · a per-component list in components.toml
Must:
<must>
  - `_project_sensitivity_values(root)` returns base `_SENSITIVITY_VALUES` ∪ the domain tokens parsed from GLOSSARY.md's `## Sensitivity classes` section (each `- <token>: <definition>` / `- <token> — …` line → `<token>` lowercased); PURE, read-only, deduped, base-first order.
  - resolution is FAIL-SAFE: no GLOSSARY.md, no such section, or unreadable → base only (never crashes, never empties the base).
  - `_task_sensitivity(hdr, valid=None)` tests membership against `valid` when given, else the base (back-compat); freeze/status/audit pass `_project_sensitivity_values(root)` so a declared domain value reads as a valid member (not "?").
  - `add.py freeze` accepts a header sensitivity that is in base ∪ project; only a token in NEITHER → `sensitivity_invalid`.
  - `add.py init` seeds a `## Sensitivity classes` section into the project's GLOSSARY.md (the base four documented + a commented how-to template) so the vocabulary is visible from day one.
  - a NEW on-demand skill guide documents how the AI maintains the project sensitivity glossary; `SKILL.md` points to it; `add.py status`/`check` emits a MEASURE-only nudge when a project declares no domain classes (never blocks).
</must>
Reject:
<reject>
  - `freeze` on a header `sensitivity: <x>` where x ∉ (base ∪ project GLOSSARY classes) -> "sensitivity_invalid" (TASK.md/§3 byte-unchanged — validate-then-write preserved)
</reject>
After:
<after>
  - a project can declare domain sensitivity classes in GLOSSARY.md and freeze tasks that use them; the base four always remain valid; an unknown-everywhere token still refuses.
  - a fresh `init` produces a GLOSSARY.md carrying the `## Sensitivity classes` section; byte-identical engine/skill across all mirror trees.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the GLOSSARY.md section parse format (`## Sensitivity classes` + `- <token>: …` lines) — lowest confidence because a project may write a different bullet/heading style and the token won't parse; if wrong: a declared domain value reads as undeclared → its freeze refuses. Mitigation: tolerant token regex (`- <token>` then `:`/`—`/space) + fail-safe to base + the seeded template models the exact format.
  - [ ] the base four must never be removable by a project (advisor-gate-relax keys off `mechanical`) — the reader always unions base IN, never replaces.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: project domain classes union with the base
  Given a GLOSSARY.md with a "## Sensitivity classes" section listing "- pii: ..." and "- payments: ..."
  When _project_sensitivity_values(root) runs
  Then it returns the base four AND "pii" AND "payments"

Scenario: no glossary section falls back to base
  Given a GLOSSARY.md with no "## Sensitivity classes" section (or no GLOSSARY.md)
  When _project_sensitivity_values(root) runs
  Then it returns exactly the base four (never empty, never crashes)

Scenario: a declared domain value freezes cleanly
  Given a project that declares "pii" in its glossary, and a drafted+flagged §3 task whose header says "sensitivity: pii"
  When add.py freeze runs
  Then §3 becomes "FROZEN @ v1" (a domain value is a valid member, not "?")

Scenario: a value in neither base nor glossary still refuses
  Given a task header "sensitivity: spicy" and "spicy" is not in the glossary
  When add.py freeze runs
  Then it exits non-zero with "sensitivity_invalid"
  And the §3 stays DRAFT and TASK.md is byte-unchanged

Scenario: init seeds the glossary section
  Given a fresh `add.py init`
  When the project's GLOSSARY.md is read
  Then it contains a "## Sensitivity classes" section documenting the base four

Scenario: nudge when no domain classes declared
  Given a project with the section absent or carrying only the base
  When add.py check runs
  Then it surfaces a measure-only nudge to declare domain sensitivity classes
  And check still exits 0 (a measure, never a block)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add.py / add_engine  (extends risk-sensitivity-taxonomy; the base stays valid)
  _project_sensitivity_values(root: Path) -> tuple[str, ...]
     = _SENSITIVITY_VALUES (base, always first)  ∪  domain tokens parsed from GLOSSARY.md
       "## Sensitivity classes" section (line "- <token>: …" | "- <token> — …" → token.lower())
     PURE, read-only, deduped. FAIL-SAFE: no file / no section / unreadable -> base only.
  _task_sensitivity(hdr: str, valid=None) -> member | None | "?"
     valid defaults to _SENSITIVITY_VALUES (back-compat); membership tested against `valid`.
  cmd_freeze : tok = _task_sensitivity(hdr, valid=_project_sensitivity_values(root));
               tok == "?"  -> _die("sensitivity_invalid: … one of <base ∪ project>")   # no write
  cmd_status : prints "sensitivity: <member>" resolved against the union (domain value not "?")
  _guarantee_lint_notices : sensitivity_unset measure unchanged (None still = unset)
  cmd_init   : seed a "## Sensitivity classes" section into GLOSSARY.md (base four + commented template)
  status/check : MEASURE-only nudge when a project declares NO domain classes (never blocks, exit 0)

skill (3 git-tracked trees + SKILL.md): a new on-demand guide on maintaining the project
  sensitivity glossary; SKILL.md "Beyond the bundle" gains a one-line pointer.

Schema: GLOSSARY.md gains a "## Sensitivity classes" section (`- <token>: <definition>` lines),
  human + AI maintained. state.json is NOT a source of truth (read live, like the base).
```

`Least-sure flag surfaced at freeze:` [contract] the GLOSSARY.md section parse format (`## Sensitivity classes` + `- <token>: …`) — if a project writes a different style the domain token won't parse and its freeze refuses; mitigated by a tolerant token regex + fail-safe-to-base + the init-seeded template modelling the exact format.
Status: FROZEN @ v1 — approved by Tin Dang
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + the named Reject
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_union_includes_domain: GLOSSARY with "## Sensitivity classes" + "- pii: x"/"- payments: y" -> _project_sensitivity_values ⊇ base ∪ {pii, payments}
  - test_no_section_falls_back_to_base: no section / no GLOSSARY -> exactly the base four (non-empty)
  - test_domain_value_freezes: project declares "pii"; task header "sensitivity: pii"; freeze -> §3 FROZEN @ v1
  - test_unknown_everywhere_refuses: header "sensitivity: spicy" not in glossary; freeze -> exit!=0 "sensitivity_invalid"; §3 still DRAFT + TASK.md byte-unchanged
  - test_init_seeds_section: after init, GLOSSARY.md contains "## Sensitivity classes" + the base four
  - test_check_nudges_when_no_domain_classes: project with only base/absent section -> check stdout carries the nudge AND exit 0
  - test_task_sensitivity_valid_param: _task_sensitivity("…sensitivity: pii", valid=("pii",)) == "pii"; default (base) -> "?"
</test_plan>

Tests live in: `add-method/tooling/test_sensitivity_glossary.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/tooling/` `.add/tooling/` `add-method/skill/` `add-method/src/add_method/_bundled/skill/`
Strategy (ordered batches): 1. red tests (test_sensitivity_glossary.py) · 2. `_project_sensitivity_values(root)` reader (parse GLOSSARY.md section) + widen `_task_sensitivity(hdr, valid=None)` · 3. freeze/status pass the union; nudge in check · 4. seed `## Sensitivity classes` into the GLOSSARY.md template + cmd_init · 5. new skill guide + SKILL.md pointer · 6. green canonical · 7. prepare_bundle (engine + skill) + dogfood-sync · 8. re-pin BOTH digests · 9. full suite — fix skill-parity + lean-fence + wording-lint ripples (do test edits in TESTS phase, re-cross).
Known-problem fixes: a NEW skill guide ripples into 3-tree skill parity + the lean-fence token budget + 2 wording-lint registries (component-method-docs lesson) → update all in the TESTS phase, then re-cross tests→build · GLOSSARY.md template lives in templates/ AND the embedded fallback — seed both for parity · the reader must union base IN unconditionally (never let an empty/garbled section drop the base).
Strategy actually used: <fill at VERIFY — the strategy you ACTUALLY used (or "as planned"); harvested into the §7 Decisions (ADR) block as the [AI] build decision>
Safety rule (feature-specific): the reader always unions the base in (a project can extend, never remove the universal four); validate-then-write preserved in cmd_freeze.
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

- [ ] all tests pass
- [ ] coverage did not decrease
- [ ] no test or contract was altered during build
- [ ] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [ ] concurrency / timing of the risky operation is safe
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] a header sensitivity equal to a domain class declared in GLOSSARY.md's "## Sensitivity classes" section freezes cleanly (§3 -> FROZEN) — confirmed by FreezeUnionTest.test_domain_value_freezes + `_project_sensitivity_values` returning base ∪ {pii,payments}
- [x] a value in NEITHER base nor glossary still refuses `sensitivity_invalid` with TASK.md byte-unchanged — confirmed by FreezeUnionTest.test_unknown_everywhere_refuses
- [x] a fresh `init` GLOSSARY.md carries the "## Sensitivity classes" section AND `check` nudges `sensitivity_classes_unset` (exit 0) until a domain class is declared — confirmed by InitAndNudgeTest + the live dogfood `check` (this project, no domain classes yet)
- [x] the resolver is FAIL-SAFE — no GLOSSARY.md / no section -> exactly the base four, never empty — confirmed by ProjectSensitivityValuesTest.test_missing_glossary_is_base / test_no_section_falls_back_to_base
- [x] the new `sensitivity.md` skill guide ships byte-identical across all 3 skill trees + SKILL.md points to it — confirmed by test_bundle_parity + test_tree_parity + test_skill_lean (pointer + lean fence)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_project_sensitivity_domain`/`_project_sensitivity_values` are called by cmd_freeze (707) + cmd_status (1708) + cmd_check (2594); `_task_sensitivity(valid=)` is exercised by freeze/status; the GLOSSARY section + skill guide are wired via init/SKILL.md
- [x] DEAD-CODE (code) — no orphaned symbol; the two readers + the widened param all have live call sites (grep-confirmed above)
- [x] SEMANTIC (prose / non-code) — sensitivity.md read in full: base four + extend-per-project + AI-maintenance + hold-the-line, no banned idioms, matches the engine behavior

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self · adversarially checked: probed for overfit (freeze test runs the REAL freeze command — a missing union → sensitivity_invalid → red, so the union path is genuinely exercised), vacuous asserts (union test checks base AND pii AND payments; reject test checks exit!=0 AND byte-unchanged), and stub (the reader actually parses a real GLOSSARY.md; the init+nudge pair proves the commented examples are NOT counted, i.e. the comment-strip is live, not stubbed). Conservative task → final resolution is the human's.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-29

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose domain values in a GLOSSARY.md `## Sensitivity classes` section; rejected a `sensitivity-values:` declaration line in PROJECT.md · a per-component list in components.toml
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned
- [human] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
