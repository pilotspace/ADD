# TASK: Seed project requirements personas at setup

slug: persona-setup · created: 2026-06-29 · stage: mvp
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
  - `add-method/tooling/add.py:cmd_init` (≈363) — scaffolds the living docs at init via the survivor-layer loop `for fname in SETUP_FILES: _render_template(...)`, never-clobber; the engine-side seed hook for a personas scaffold.
  - `add-method/tooling/add_engine/constants.py:SETUP_FILES` (91) — `("PROJECT.md","CONVENTIONS.md","GLOSSARY.md","MODEL_REGISTRY.md","dependencies.allowlist","DESIGN.md","SOUL.md")`; the living-doc file list a persona seed may extend.
  - `add-method/tooling/add.py:_render_template` (138) + `_templates_dir` (134) — `templates/<name>.tmpl` renderer (`{{key}}` subs, built-in fallback); a new persona template would join `templates/`.
  - `add-method/tooling/templates/*.tmpl` — existing seed templates (PROJECT.md.tmpl · GLOSSARY.md.tmpl · DESIGN.md.tmpl · MILESTONE.md.tmpl · TASK.md.tmpl …); a persona template lands here (3-tree parity).
  - `add-method/skill/add/phases/0-setup.md` — the setup-phase guide; the AI-authoring step (read agency-agents as teacher → distill project-fit personas under the baseline approval) is documented here.
  - `add-method/skill/add/design.md` — UDD loop; the DOWNSTREAM consumer (persona success-metrics → captured-screen confirm checklist). Referenced, not edited in THIS task (owned by udd-persona-loop).
  - `add-method/tooling/add_engine/predicates.py:_section_unfilled` — the fill/placeholder predicate pattern to mirror if a persona-schema fill check is added.
Context (working folder):
  - `.add/PROJECT.md` (the 4-lens foundation the personas are tailored to) · `.add/GLOSSARY.md` (term home for PERSONA) · `.add/CONVENTIONS.md`.
  - `.add/milestones/persona-learning-loop/MILESTONE.md` — parent: persona schema + scope + shared decisions (NO-EXEC, teacher-not-dependency, fail-safe).
  - external TEACHER: github.com/msitarzewski/agency-agents — persona structure (vibe · identity · critical-rules · default-req · measurable success-metrics); read off-build by the AI, never by the engine.
  - parity surfaces: engine 3 trees (`add-method/tooling` · `.add/tooling` · `_bundled/tooling`); skill 3 trees (`add-method/skill/add` · `.claude/skills/add` · `_bundled/skill/add`); book `add-method/docs/`.
Honors (patterns / conventions):
  - NO-EXEC engine — no network/spawn in engine code paths (MILESTONE shared decision); authoring is an off-build AI action.
  - survivor never-clobber idiom (`cmd_init` SETUP_FILES) — a seeded persona file is never overwritten if it exists.
  - 3-tree parity for engine · skill · templates (byte-identical), enforced by parity tests.
  - design-for-failure IO (global CLAUDE.md) — offline fallback for the teacher read; never block.
  - red/green TDD (global CLAUDE.md); tests in `add-method/tooling/test_*.py`, run via `python3 -m unittest discover`.
Anchors the contract cites: persona schema `.add/personas/<slug>.md` · setup seed seam (`cmd_init` / `SETUP_FILES` / `_render_template` + a `templates/` persona template) · `phases/0-setup.md` authoring step.
  - the persona file schema at `.add/personas/<slug>.md` (frontmatter · identity · critical-rules · default-requirement · measurable success-metrics).
  - the setup seed seam — `cmd_init` / `SETUP_FILES` / `_render_template` (+ a persona template under `templates/`).
  - the `phases/0-setup.md` authoring step (teacher read → distill → baseline-approval coverage).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Persona seed + schema — at `cmd_init` the engine scaffolds `.add/personas/` with a schema-conformant persona TEMPLATE (placeholders) for every new project, survivor never-clobber; on the first setup run the AI authors project-tailored personas into it from PROJECT.md + the agency-agents teacher (off-build, fail-safe), covered by the setup baseline approval. The engine owns + freezes the persona schema and validates it (measure-not-block); it NEVER fetches or spawns.
Framings weighed: auto-seed at cmd_init via SETUP_FILES + AI authors content on first run (chosen) · dedicated `persona` subcommand (opt-in, isolated) · skill-only authoring, engine validates only
Must:
<must>
  - Define the persona schema: `.add/personas/<slug>.md` = frontmatter (`name`, `vibe`) + four sections: `## Identity`, `## Critical Rules`, `## Default Requirement`, `## Success Metrics` (measurable). This is the frozen contract.
  - At `cmd_init`, scaffold `.add/personas/` containing ONE schema-conformant template persona (placeholders), via the SETUP_FILES survivor-layer (rendered from a `templates/` persona template), creating the dir if absent.
  - Survivor never-clobber: an existing `.add/personas/` file is never overwritten by init (mirrors the SETUP_FILES idiom); re-init is idempotent.
  - The engine performs NO network IO and NO spawn on this path; offline, the template still scaffolds (fail-safe — never blocks init).
  - Provide a schema validator (predicate, mirroring `_section_unfilled`) that flags a persona file missing/placeholder in any required section — MEASURE, surfaced via `add.py check`/status, not a hard block.
  - The first-run AI authoring step (read the teacher → distill project-fit personas → no generic examples committed) is documented in `phases/0-setup.md` and covered by the existing setup baseline approval (no new gate).
  - All three engine trees (canonical · dogfood · _bundled) and the templates carry the change byte-identically (3-tree parity).
</must>
Reject:
<reject>
  - a persona file missing/placeholder in a required schema section -> "persona_schema_incomplete"
  - a persona filename whose slug is not alphanumeric with - or _ -> "persona_slug_invalid"
  - any attempt to make the engine fetch the teacher or spawn on the seed/validate path -> "persona_engine_no_exec"
</reject>
After:
<after>
  - Every newly-init'd project has `.add/personas/` with a schema-conformant template; the persona schema is FROZEN; `add.py check` validates personas (measure-not-block).
  - On the first setup run, ≥1 project-tailored persona exists in `.add/personas/`, authored by the AI from PROJECT.md + teacher, recorded under the baseline approval; re-running init never clobbers it.
  - No engine code path on seed/validate touched the network or spawned; init succeeds offline.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the four schema sections (Identity · Critical Rules · Default Requirement · Success Metrics) are exactly what udd-persona-loop + advisor-persona-select need downstream — lowest confidence because those consumer tasks aren't specified yet; if wrong: they churn and the frozen schema reopens as a change-request. (Mitigation: the sections mirror the agency-agents teacher structure the milestone already cites.)
  - [x] RESOLVED — SETUP_FILES can seed a `.add/personas/` DIRECTORY with NO cmd_init change: `_atomic_write` does `path.parent.mkdir(parents=True)` and cmd_init already renders each SETUP_FILES name via `_render_template`; a path-bearing entry (`personas/persona.template.md` ← `templates/personas/persona.template.md.tmpl`) auto-creates the dir. Seam = tuple addition + one nested template per tree.
  - [ ] measure-not-block validation (not a hard gate) is the right strictness for a seeded living doc — if wrong: raise `persona_schema_incomplete` to a blocking gate (a later change-request).
  - [ ] "every project" seeding is acceptable even for tiny/CLI projects (one harmless template file) — if wrong: gate the seed behind a flag/stage.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: init seeds the personas dir with a schema-conformant template
  Given an empty directory with no .add/
  When add.py init runs
  Then .add/personas/persona.template.md exists
  And it contains frontmatter keys name and vibe plus the sections "## Identity", "## Critical Rules", "## Default Requirement", "## Success Metrics"

Scenario: the seeded template validates as schema-conformant
  Given a freshly init'd project
  When add.py check runs
  Then the seeded persona template is reported schema-conformant (no persona_schema_incomplete)

Scenario: re-init never clobbers an authored persona (survivor)
  Given a project whose .add/personas/frontend.md was edited by the AI
  When add.py init --force runs again
  Then .add/personas/frontend.md keeps its authored content byte-for-byte
  And the edited persona file is unchanged

Scenario: seeding succeeds offline (fail-safe, no network)
  Given no network access
  When add.py init runs
  Then init exits success and .add/personas/persona.template.md is written
  And no outbound network call was attempted by the engine

Scenario: a persona missing a required section is flagged (measure-not-block)
  Given .add/personas/broken.md lacking the "## Success Metrics" section
  When add.py check runs
  Then it surfaces persona_schema_incomplete naming broken.md as a WARNING
  And the check still exits 0 (measured, not a hard block)

Scenario: a persona missing a required section yields the named error from the validator predicate
  Given a persona file lacking the "## Critical Rules" section
  When the schema validator predicate evaluates it
  Then it returns persona_schema_incomplete
  And no other persona file's state is changed

Scenario: an invalid persona slug is rejected
  Given a persona filename slug "bad name!" (spaces and punctuation)
  When a persona is created/validated under that slug
  Then it is rejected with persona_slug_invalid
  And no persona file is written for that slug

Scenario: the engine never fetches the teacher or spawns on the seed/validate path
  Given the persona seed and validate code paths
  When they execute during init and check
  Then no network IO and no subprocess/spawn occurs (engine NO-EXEC)
  And the teacher (agency-agents) is read only by the AI authoring step, never by the engine

Scenario: the first-run authoring step is documented and baseline-approval-covered
  Given a freshly init'd project at the setup phase
  When phases/0-setup.md is read
  Then it documents authoring project-tailored personas from PROJECT.md + the teacher
  And it states the authored set is covered by the existing setup baseline approval (no new gate)

Scenario: the seed change is byte-identical across all three engine/template trees
  Given the persona template and SETUP_FILES change
  When the three trees (canonical · dogfood · _bundled) are compared
  Then the persona template and SETUP_FILES entry are byte-identical in each
  And the parity test passes
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

PERSONA FILE SCHEMA — `.add/personas/<slug>.md`  (slug: alnum + `-`/`_`)
  (described inline — no bare `---`/line-start `##` so the §3 span stays intact)
  • YAML frontmatter (fenced by triple-dash lines) with keys: `name` · `vibe`
  • then four H2 section headers, each written `## <Title>`:
    `## Identity` · `## Critical Rules` · `## Default Requirement` · `## Success Metrics`
  CONFORMANT iff: frontmatter has keys `name` AND `vibe`, AND all four required
  section headers are present (presence-based — content quality is the AI's
  authoring concern, not the engine gate). Required set is the single source of truth:
  `constants.PERSONA_FRONTMATTER_KEYS = ("name","vibe")` ·
  `constants.PERSONA_REQUIRED_SECTIONS = ("## Identity","## Critical Rules","## Default Requirement","## Success Metrics")`

SEED SEAM — `constants.SETUP_FILES` gains `"personas/_template.md"`
  (rendered from `templates/personas/_template.md.tmpl`; `_atomic_write` mkdirs `.add/personas/`).
  cmd_init loop is UNCHANGED (existing survivor never-clobber: `if dest.exists(): continue`).
  The template is itself schema-CONFORMANT (all sections + keys present, placeholder values).

VALIDATOR — `predicates._persona_missing(md_text: str) -> list[str]`  (pure; mirrors `_section_unfilled`)
  returns the missing required frontmatter-keys + section-headers; `[]` == conformant.
  Surfaced by `add.py check` as one census line per `.add/personas/*.md`:
    conformant  -> PASS  "persona '<slug>' schema-conformant"
    missing any -> WARN  "persona_schema_incomplete: <slug> missing <names>"   (measure-not-block; check still exits 0)

ERROR CODES (every §1 Reject has a response)
  persona_schema_incomplete -> validator names the missing keys/sections (WARN census, never a hard block)
  persona_slug_invalid      -> a persona slug failing `s.replace("-","").replace("_","").isalnum()` (mirrors new-task)
  persona_engine_no_exec    -> INVARIANT: the seed + validate paths perform NO network IO and NO spawn
                               (asserted by test over the touched symbols; the teacher is read only by the AI authoring step)

AUTHORING (skill, not engine) — `phases/0-setup.md` documents: read the teacher (agency-agents) →
  distill project-tailored personas into `.add/personas/` (no generic examples committed) →
  covered by the EXISTING setup baseline approval (no new gate). Off-build, fail-safe (offline -> template only).

PARITY — persona template + `SETUP_FILES` change land byte-identical in all 3 engine/template trees
  (`add-method/tooling` · `.add/tooling` · `_bundled/tooling`); skill change in all 3 skill trees.

Least-sure flag surfaced at freeze: ⚠ [contract] the four schema sections (Identity · Critical Rules · Default Requirement · Success Metrics) may not be exactly what the downstream consumers (udd-persona-loop · advisor-persona-select) need — they aren't specified yet; if they need a different shape, this frozen schema reopens as a change-request. Mitigation: the sections mirror the agency-agents teacher structure the milestone already cites.

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

Coverage target: every Must + Reject scenario has one test (new symbols 100%)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_init_seeds_persona_template: init a temp project / assert `.add/personas/_template.md` exists with frontmatter name+vibe + the 4 section headers
  - test_seeded_template_is_conformant: init / assert `_persona_missing(template_text) == []`
  - test_reinit_never_clobbers_authored_persona: write `.add/personas/frontend.md`, run init --force / assert its bytes unchanged
  - test_seed_offline_failsafe: monkeypatch network to raise / run init / assert success + template written + no network attempted
  - test_validator_flags_missing_section: persona text minus "## Success Metrics" / assert `_persona_missing` returns ["## Success Metrics"]
  - test_check_census_warns_not_blocks: project with a broken persona / run cmd_check / assert WARN persona_schema_incomplete naming the slug AND check exit 0
  - test_persona_slug_invalid: slug "bad name!" / assert rejected persona_slug_invalid + no file written
  - test_engine_no_exec_on_persona_paths: AST/scan the seed+validate symbols / assert no socket/urllib/subprocess/spawn import or call (persona_engine_no_exec invariant)
  - test_setup_guide_documents_authoring: read phases/0-setup.md / assert it names teacher→distill→baseline-approval-covered (3 skill trees)
  - test_persona_seed_3tree_parity: assert `_template.md.tmpl` + SETUP_FILES entry byte-identical across the 3 engine/template trees + ENGINE_PKG_MD5/ENGINE_MD5 re-aimed
</test_plan>

Tests live in: `add-method/tooling/test_persona_setup.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add_engine/constants.py` `add-method/tooling/add_engine/predicates.py` `add-method/tooling/add.py` `add-method/tooling/templates/personas/_template.md.tmpl` `add-method/tooling/engine_pin.py` `add-method/tooling/test_persona_setup.py` `.add/tooling/add_engine/constants.py` `.add/tooling/add_engine/predicates.py` `.add/tooling/add.py` `.add/tooling/templates/personas/_template.md.tmpl` `add-method/src/add_method/_bundled/tooling/add_engine/constants.py` `add-method/src/add_method/_bundled/tooling/add_engine/predicates.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/src/add_method/_bundled/tooling/templates/personas/_template.md.tmpl` `add-method/skill/add/phases/0-setup.md` `.claude/skills/add/phases/0-setup.md` `add-method/src/add_method/_bundled/skill/add/phases/0-setup.md`
Strategy (ordered batches): 1. constants.py — add PERSONA_FRONTMATTER_KEYS, PERSONA_REQUIRED_SECTIONS, append "personas/_template.md" to SETUP_FILES (export via __all__). 2. predicates.py — `_persona_missing(md_text)->list[str]` (pure, mirrors `_section_unfilled`), re-export in add.py. 3. templates/personas/_template.md.tmpl — schema-conformant placeholder persona. 4. add.py cmd_check — one census line per `.add/personas/*.md`. 5. mirror all to the other 2 engine trees + 3 skill trees (byte-identical via cp). 6. phases/0-setup.md — document the authoring step. 7. re-aim engine_pin (ENGINE_MD5 + ENGINE_PKG_MD5). Run red→green per batch.
Known-problem fixes: SETUP_FILES path-bearing entry needs the nested `.tmpl` to exist or it renders blank+skips (circuit-breaker warning) → create the template in all 3 trees BEFORE relying on the seed · slug with a dot (`_template`) is valid (`.isalnum()` after stripping -/_); avoid a `.`-bearing slug · editing add.py re-aims BOTH pins (md5 add.py + pkg digest) · the §6 build-expectations + earned-green refute-read must be filled (auto autonomy).
Strategy actually used: as planned (constants → predicate → template → census → 3-tree mirror → guide → re-aim both pins), PLUS a verify-phase self-heal: the earned-green refute-read returned NOT-EARNED (4 under-asserting tests — vacuous offline test, swallowed exit-code, predicate-only NO-EXEC scan, one-word guide check). Rewound to TESTS, strengthened all 4 to the §4 plan (fresh-init socket monkeypatch + no-network assert · explicit exit-0 capture · seed-path scan of cmd_init/_render_template/_atomic_write · 5-token authoring check), mutation-proved the 2 critical ones go red on regression, re-crossed tests→build to re-baseline the tripwire, removed the now-dead `_run` helper; the 2nd independent refute-read returned EARNED (0.95).
Safety rule (feature-specific): the engine seed/validate path stays NO-EXEC — no network/spawn imports or calls; offline init must still succeed (fail-safe).
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

- [x] all tests pass — full suite 2428/0 (`python3 -m unittest discover`)
- [x] coverage did not decrease — 12 new persona tests added; no test deleted (one dead helper `_run` removed, no assertion lost)
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; test strengthening done in the TESTS phase with tests→build re-crossed (tripwire re-baselined), not hand-edited under the tripwire
- [x] the green was EARNED — 1st refute-read NOT-EARNED (4 weak tests) → strengthened + re-crossed → 2nd independent refute-read EARNED (0.95); 2 critical assertions mutation-proven to go red on regression
- [x] concurrency / timing — read-only single-pass census; the seed is the existing atomic survivor never-clobber (`_atomic_write`); no new shared mutable state, no new race
- [x] no exposed secrets, injection openings, or unexpected dependencies — pure local file read + regex predicate; no eval/exec; no new dependency; slug is display/validate-only (no path traversal — glob stays inside `.add/personas/`)
- [x] layering & dependencies follow CONVENTIONS.md — predicate in predicates.py, constants in constants.py, census mirrors the existing warning/info append idiom, template in templates/; NO-EXEC honored; 3-tree parity held
- [x] reviewed — auto-resolved under `autonomy: auto` (no residue); two independent adversarial refute-read agents + a human spot-audit backstop

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] a freshly init'd project has `.add/personas/_template.md` with frontmatter name+vibe + the 4 section headers — CONFIRMED: ran `add.py init` in a temp dir, opened the file (frontmatter `name`/`vibe` + `## Identity`/`## Critical Rules`/`## Default Requirement`/`## Success Metrics`)
- [x] `add.py check` lists each `.add/personas/*.md` and WARNs persona_schema_incomplete on a broken one while still exiting 0 — CONFIRMED live: `WARN persona 'broken' persona_schema_incomplete: missing ## Success Metrics` + `INFO persona '_template' schema-conformant`, check exited 0
- [x] re-running `init --force` leaves an authored persona byte-identical — CONFIRMED: md5 before==after (66bfbb92…) on an authored `broken.md`
- [x] the persona template + SETUP_FILES entry are byte-identical across all 3 engine trees and the 3 skill 0-setup.md guides carry the authoring step — CONFIRMED: `test_persona_template_3tree_parity`, `test_setup_files_entry_in_all_trees`, `test_setup_guide_documents_authoring` (5 content tokens × 3 trees) green
- [x] no network/spawn token appears in the persona seed AND validate source — CONFIRMED: `test_engine_no_exec_on_persona_paths` scans `_persona_missing`/`_persona_slug_valid` + `cmd_init`/`_render_template`/`_atomic_write`, all FORBIDDEN_EXEC tokens absent

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_persona_slug_valid` ref'd add.py:2660 · `_persona_missing` ref'd add.py:2665 (both re-exported add.py:159) · `PERSONA_FRONTMATTER_KEYS`/`PERSONA_REQUIRED_SECTIONS` used predicates.py:84,87 · `SETUP_FILES` "personas/_template.md" consumed by the cmd_init loop add.py:382 (renders `templates/personas/_template.md.tmpl`). Verified by grep of call sites.
- [x] DEAD-CODE (code) — no new unused/orphaned symbol; the test-only `_run` helper that became unused after strengthening was REMOVED (flagged by the 2nd refute-read as a latent SystemExit-swallowing trap).
- [x] SEMANTIC (prose) — read `phases/0-setup.md` persona-seeding bullet in full (all 3 skill trees byte-identical): it documents author-from-PROJECT.md + teacher (agency-agents), read off-build/fail-safe, covered by the baseline approval, never-clobber — matches §3 AUTHORING.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED (after one self-heal cycle)
By: two independent refute-read agents · adversarially checked: the 3 judgment cheats (overfit / vacuous asserts / stubbed logic) + whether each test creates a real failure condition.
  - 1st read: NOT-EARNED — src correct but 4 tests under-asserted the §3/§4 contract: offline test was vacuous (re-init survivor-skip, no monkeypatch), exit-0 measure-not-block half swallowed by a helper, NO-EXEC scan covered only the 2 predicates (not the seed path), guide test was a one-word substring.
  - heal: strengthened all 4 in the TESTS phase (re-crossed tests→build, tripwire re-baselined) + mutation-proved the offline (network-on-fresh-seed → red) and exit-code (warning-blocks → red) tests catch regressions; removed the now-dead `_run` helper. heal.attempts stays 0 — this was a TEST-coverage strengthening (the green was honestly earned by src), not a src-cheat heal loop.
  - 2nd read: EARNED (0.95) — all 4 holes genuinely closed with real failure conditions; no new vacuity/isolation defect.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: self (diff review) + corroborated by the refute-read agents
1. Security: CLEAR — pure local file read + regex predicate, no eval/exec, no new dependency; slug is display/validate-only and the glob stays inside `.add/personas/` (no path traversal); no secrets.
2. Concurrency: CLEAR — read-only single-pass census; seed is the existing atomic survivor never-clobber (`_atomic_write`); no new shared mutable state or race.
3. Architecture: CLEAR — follows predicate/constants/census/template idioms; NO-EXEC honored; 3-tree parity held.
Verdict: PASS
Residue: none
Binding: advisory — sensitivity: method/engine-behavior (new predicate + census + seed are engine behavior, not a purely mechanical edit)

### GATE RECORD
Outcome: PASS
Reviewed by: auto-resolved (autonomy: auto, no residue) — owner Tin Dang · date: 2026-06-29

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. The Advisor 3-lens verdict and the Refute-read verdict are both measured by `add.py audit` (`advisor_verdict_unrecorded` · `refute_unrecorded`) — neither is engine-blocked; a human spot-audit is the backstop for any finding the AI did not surface or record. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose auto-seed at cmd_init via SETUP_FILES + AI authors content on first run; rejected dedicated `persona` subcommand (opt-in, isolated) · skill-only authoring, engine validates only
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned (constants → predicate → template → census → 3-tree mirror → guide → re-aim both pins), PLUS a verify-phase self-heal: the earned-green refute-read returned NOT-EARNED (4 under-asserting tests — vacuous offline test, swallowed exit-code, predicate-only NO-EXEC scan, one-word guide check). Rewound to TESTS, strengthened all 4 to the §4 plan (fresh-init socket monkeypatch + no-network assert · explicit exit-0 capture · seed-path scan of cmd_init/_render_template/_atomic_write · 5-token authoring check), mutation-proved the 2 critical ones go red on regression, re-crossed tests→build to re-baseline the tripwire, removed the now-dead `_run` helper; the 2nd independent refute-read returned EARNED (0.95).
- [AI] verify — gate PASS (reviewed by auto-resolved (autonomy: auto, no residue) — owner Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
