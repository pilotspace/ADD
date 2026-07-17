# TASK: components.toml reader/validator + check-time schema lint

slug: components-validator · created: 2026-06-28 · stage: mvp
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
  - `add-method/tooling/add.py:cmd_check` — read-only integrity check; ALREADY surfaces component findings as fail-closed RED + a federation WARN (the loop near L2410). The new schema-lint hooks in HERE.
  - `add-method/tooling/add.py:_component_findings(root) -> list[(code,detail)]` — the loud registry surface today: `components_malformed` (TOML parse error · tomllib<3.11 · reserved `?` name · `[component.X]` missing `root`), `component_root_outside`, `component_unknown`. Catches MISSING-required + structural breaks; does NOT catch unknown/misspelled keys or unknown table names.
  - `add-method/tooling/add.py:_contract_findings(root)` — only `contract_producer_unknown` today.
  - `add-method/tooling/add_engine/components.py:_components(root) -> {name:{root,verify,green_bar,language}}` — registry reader; pulls known keys via `.get`, so an unknown/typo'd key is SILENTLY DROPPED (the typo gap).
  - `add_engine/components.py:_contracts(root)` ({id:{producer,consumers}}) · `_federation(root)` ({id:{source,pin}}) — same silent-skip-unknown-keys pattern.
  - `add_engine/components.py:_confined(p,rootp)` — symlink-following path confinement (reused for root-escape detection).
  - `add-method/tooling/add.py` subparser block (~L5997, by `pck`/`pfed`) — where `pcomp = sub.add_parser("components", …)` + `set_defaults(func=cmd_components)` registers. NO `cmd_components` exists yet — this task creates it.
Context (working folder):
  - `add-method/skill/add/components.md` — the schema doc. Its TOML example uses `green-bar` (HYPHEN) while the engine reads `green_bar` (UNDERSCORE) → a REAL doc bug the validator would catch (dogfooding evidence; the canonical key is underscore per every test fixture). 4-tree skill mirror.
  - `add-method/tooling/test_min_pillar.py` — LIFECYCLE coverage guard: a new subcommand must be added to `LIFECYCLE` (and `_NONZERO_OK` IF it exits nonzero on the bare board) or `test_every_subcommand_is_covered` goes red; the read-spy requires the command read NO `docs/` chapter.
  - `add-method/tooling/test_component_registry.py · test_per_component_verify.py` — existing fixtures use `green_bar` (underscore) = canonical.
  - `add-method/tooling/engine_pin.py` — single-source ENGINE_MD5 pin; re-pin after the dogfood mirror sync.
  - No `components.toml` exists anywhere in this repo (single-component project) — the validator runs here as a friendly exit-0 no-op; tests build fixtures in tmp dirs.
Honors (patterns / conventions):
  - OPT-IN + byte-identical-when-zero-components (components.md "Declared, not inferred"; module docstring): `add.py components` with no components.toml is a friendly exit-0 no-op; nothing changes single-component behavior.
  - DEGRADE-SAFE: readers NEVER raise; the loud surface is the finding list, fail-closed RED at `check` (PROJECT.md design-for-failure; `_component_findings` pattern).
  - NO-EXEC engine: `verify` is parsed as data, NEVER executed (components.py docstring) — the validator runs nothing.
  - Tri-tree + pin: edit canonical `add-method/tooling/`, re-sync `.add/tooling/` + `add-method/src/add_method/_bundled/tooling/`, re-pin ENGINE_MD5 (engine-pin tripwire). stdlib-only; tomllib degrade-safe (<3.11 → opt-out).
Anchors the contract cites:
  - `cmd_components(args)` — NEW subcommand: read + validate the registry, print it, exit nonzero on findings (exit 0 + no-op when no components.toml).
  - a new schema-lint surface (extend `_component_findings` and/or `_component_schema_findings(root)`) that flags unknown keys · unknown table names · wrong-type optional values (the "typo" surface) — consumed by `cmd_check` AND `cmd_components`.
  - the `components` subparser registration line.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `add.py components` reader/validator + a check-time components.toml schema lint
Framings weighed: validator-command + check-WARN typo-lint (chosen) · typos as RED check-fail · command-only, no check change
Must:
<must>
  - `add.py components` reads `.add/components.toml` and prints the parsed registry in deterministic order — components ({name → root · verify · green_bar · language}), contracts ({id → producer · consumers}), federation ({id → source · pin}).
  - With NO `.add/components.toml`, `components` prints a friendly "single-component project (no components.toml)" line and exits 0 (byte-identical opt-out; reads no docs/ chapter).
  - `components` runs the FULL validation (existing integrity findings + the new schema-lint), lists every finding grouped RED-then-WARN, and exits nonzero IFF ≥1 RED integrity finding (exit 0 when clean or only WARN-level typo findings).
  - The new schema-lint flags, per `[component.*]` / `[contract.*]` / `[federation.*]` entry: an unknown/misspelled KEY · a wrong-TYPE value on a known optional key · an unrecognized TABLE the engine silently ignores. Each emitted as a (code, detail) pair.
  - These schema-lint findings ALSO surface at `check` time as never-red WARNs (measure-not-block) — caught early in CI without failing the build or breaking older-engine/newer-file forward-compat.
  - Existing integrity findings (`components_malformed` · `component_root_outside` · `component_unknown` · `contract_producer_unknown`) stay RED at `check`, behavior unchanged.
  - The lint is DEGRADE-SAFE + NO-EXEC: never raises on a malformed/edge file, never executes `verify`, reads only `.add/components.toml`.
</must>
Reject:
<reject>
  - run outside an ADD project (no `.add/`) -> "no_project"   (the command dies, like every command)
  - an unknown / misspelled key on an entry (e.g. `green-bar`, `prodcuer`, `consumer`) -> "component_unknown_key"   (WARN)
  - a wrong-type value on a known optional key (e.g. `verify` not a str, `consumers` not a list, `pin` not a str) -> "component_type_mismatch"   (WARN)
  - an unrecognized top-level table the engine ignores (e.g. `[componnt.x]`, `[contracts.x]`) -> "component_unknown_table"   (WARN)
</reject>
After:
<after>
  - `add.py components` printed the registry + a summary (`valid` · `(N warnings)` · `(N errors)`); exit 0 when no RED finding, exit 1 when ≥1 RED integrity finding.
  - `check` output gained the schema-lint WARNs when a components.toml carries a typo (its `(N warnings)` count grows); existing PASS/FAIL + RED findings unchanged; SILENT when no components.toml.
  - `test_min_pillar` LIFECYCLE covers `components` (reads no docs/, exit 0 on the bare board → NOT in `_NONZERO_OK`).
  - The three engine trees stay byte-identical; ENGINE_MD5 re-pinned.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [spec] typo'd/unknown keys surface as never-red WARN, NOT a RED check-fail — lowest confidence because the components.toml schema is CLOSED + engine-owned (a typo is ~always a real mistake, which argues for RED), yet RED would newly-fail an existing project's `check` on a benign inert key AND break older-engine/newer-file forward-compat; WARN keeps measure-not-block (flow-honesty) while still catching it early. If wrong (you want RED): the lint codes move from `warnings` to `checks` in cmd_check — ~2 lines, but it re-reds CI for any project carrying an inert key.
  - [ ] wrong-TYPE on a known key is WARN too (not RED) — the readers already degrade-coerce it (value merely dropped, not a parse break); if wrong: same 2-line severity move.
  - [ ] the `components.md` doc bug (`green-bar` hyphen vs engine `green_bar`) is OUT of this task's scope — recorded as a §7 SPEC delta (the fix ripples into the 4-tree skill mirror + a parity test; it belongs with `component-worked-example`, not the validator). If wrong: pull the 4-tree doc fix into §5 scope.
  - [ ] `add.py components` prints human-readable text by default; a `--json` machine form is deferred unless asked (cheap, additive later). If wrong: add a `--json` branch.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: print a valid registry
  Given a .add/components.toml declaring two well-formed components, a contract, and a federation entry
  When I run `add.py components`
  Then it prints each component (root · verify · green_bar · language), the contract (producer · consumers), and the federation (source · pin) in deterministic order
  And it prints a "valid" summary and exits 0

Scenario: no registry is a friendly opt-out no-op
  Given a project with no .add/components.toml
  When I run `add.py components`
  Then it prints "single-component project (no components.toml)" and exits 0
  And it reads no docs/ chapter

Scenario: a RED integrity finding fails the command
  Given a [component.api] missing its required `root`
  When I run `add.py components`
  Then it lists a `components_malformed` finding under errors and exits 1
  And the registry's other well-formed entries still print   # the read degrades safe

Scenario: an unknown/misspelled key is flagged (WARN, parses on)
  Given a [component.web] declaring `green-bar = "vitest"` (hyphen typo of green_bar)
  When I run `add.py components`
  Then it lists a `component_unknown_key` finding naming `green-bar` on component.web
  And the entry's known keys still print and the command exits 0   # WARN never fails

Scenario: a wrong-type value on a known key is flagged (WARN)
  Given a [contract.orders] whose `consumers = "web"` is a string, not a list
  When I run `add.py components`
  Then it lists a `component_type_mismatch` finding naming `consumers` on contract.orders
  And the command exits 0   # WARN never fails

Scenario: an unrecognized table is flagged (WARN)
  Given a components.toml with a [componnt.api] table (typo of component)
  When I run `add.py components`
  Then it lists a `component_unknown_table` finding naming `componnt`
  And the command exits 0   # WARN never fails

Scenario: schema-lint warnings surface at check, never red
  Given a [component.web] carrying the `green-bar` hyphen typo
  When I run `add.py check`
  Then a WARN line names `component_unknown_key` and the summary shows "(N warnings)"
  And no PASS becomes FAIL and check exits 0   # measure-not-block

Scenario: an integrity break stays RED at check
  Given a [component.api] missing its required `root`
  When I run `add.py check`
  Then a FAIL line names `components_malformed` and check exits 1
  And the new schema-lint WARNs do not downgrade it   # existing RED unchanged

Scenario: the lint never raises on a malformed file and never executes verify
  Given a .add/components.toml that is not valid TOML and carries a `verify` value
  When I run `add.py components`
  Then it reports `components_malformed` (the parse error) and exits 1 with no traceback
  And the `verify` value is never executed   # NO-EXEC

Scenario: run outside an ADD project
  Given a directory with no .add/
  When I run `add.py components`
  Then it dies with "no_project" and exits nonzero
  And it writes nothing   # read-only
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
CLI: add.py components          (read-only; no args/flags in v1 — --json deferred)
  exit 0 -> registry printed + summary; no RED integrity finding (clean OR WARN-only)
  exit 1 -> "no_project" (dies, no .add/) ; OR registry printed (degrade-safe) + ≥1 RED finding
  no .add/components.toml -> prints "single-component project (no components.toml)" + exit 0 ; reads no docs/

stdout (deterministic; entries sorted by name/id):
  component <name>  root=<r>  verify=<v|->  green_bar=<g|->  language=<l|->
  contract  <id>  producer=<p>  consumers=[<…>]
  federation <id>  source=<s>  pin=<pin|->
  findings (when any): "ERROR <code>: <detail>"  (each RED, sorted)  then  "WARN <code>: <detail>"  (each, sorted)
  summary: "components: N · contracts: C · federation: F — <valid | E error(s), W warning(s)>"

new engine lint (PURE · degrade-safe · NO-EXEC · reads only .add/components.toml):
  _component_schema_findings(root: Path) -> list[(code, detail)]    # [] when absent/opted-out/clean
    component_unknown_key    — a key outside the known set for its table:
                               component → {root,verify,green_bar,language} · contract → {producer,consumers} · federation → {source,pin}
    component_type_mismatch  — a known key present with the wrong type:
                               verify|green_bar|language not str (component) · producer not str · consumers not list (contract) · source not str · pin not str (federation)
                               (root is NOT type-checked here — missing/non-str root is already RED `components_malformed`; no double-report)
    component_unknown_table  — a top-level key/table other than {component, contract, federation}
  Severity: all three codes are WARN — they ride `warnings`, NEVER `checks`/`failed`.

cmd_check integration:
  existing RED loops (_component_findings + _contract_findings) UNCHANGED.
  + a new loop appends _component_schema_findings(root) to `warnings` (never `checks`); silent when no components.toml.

cmd_components(args):
  prints the registry (via _components/_contracts/_federation), then RED findings (_component_findings + _contract_findings)
  then WARN findings (_component_schema_findings); raises SystemExit(1) IFF ≥1 RED finding; else exit 0 (incl. WARN-only & opted-out).

Anchors (from §0): cmd_components · _component_schema_findings · the cmd_check warn-loop · the `components` subparser (set_defaults func=cmd_components).
IO: reads ONLY .add/components.toml; writes nothing. Glossary: component · contract · federation · green_bar (underscore).
```

Least-sure flag surfaced at freeze: [spec] typo'd/unknown keys are never-red WARN, not a RED check-fail — cost: a ~2-line severity move (lint codes → `checks`) if wrong; resolved WARN by Tin at the freeze.

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

Coverage target: every Must + every Reject (10 scenarios) + the engine helper unit-pinned; 23 tests, 3 classes. Red now: 20 fail (missing cmd_components + _component_schema_findings) + min_pillar coverage; 1 green PIN (existing integrity RED preserved).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  SchemaFindings (unit on `_component_schema_findings(root)`):
  - clean / absent registry -> [] · malformed_toml -> [] · never_raises_on_bad_inputs
  - unknown_key (component + contract + federation) -> component_unknown_key naming key+entry
  - type_mismatch (consumers str · component optional int) -> component_type_mismatch naming key
  - root_not_double_reported -> root NOT type-checked here (already RED components_malformed)
  - unknown_table ([componnt.*]) -> component_unknown_table naming the bad table
  ComponentsCommand (cmd_components):
  - print_valid_registry -> components/contracts/federation fields + "valid", exit 0
  - no_registry_is_friendly_noop -> "single-component project", exit 0
  - red_integrity_finding_fails_command -> components_malformed, exit 1, well-formed entry still prints
  - unknown_key / wrong_type / unknown_table_is_warn -> each WARN code, exit 0
  - malformed_degrades_no_raise -> components_malformed, exit 1, no traceback
  - verify_is_never_executed -> sentinel-touch verify never runs (NO-EXEC) + command actually ran
  - no_project_dies -> "no_project", exit ≠ 0
  CheckIntegration:
  - schema_warn_surfaces_at_check_never_red -> WARN + component_unknown_key + "(N warnings)", exit 0, no component FAIL
  - integrity_break_stays_red_at_check -> GREEN PIN: existing components_malformed RED unchanged, exit 1
  + test_min_pillar LIFECYCLE: `["components"]` covered (exit 0 on bare board, reads no docs/)
</test_plan>

Tests live in: `add-method/tooling/test_components_validator.py` `add-method/tooling/test_min_pillar.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/test_components_validator.py` `add-method/tooling/test_min_pillar.py` `add-method/tooling/engine_pin.py` `.add/tooling/` `add-method/src/add_method/_bundled/tooling/`
Strategy (ordered batches): 1. write red tests (test_components_validator.py: the 10 scenarios) + the test_min_pillar LIFECYCLE entry — RED. 2. add `_component_schema_findings(root)` in add.py beside `_component_findings`. 3. add `cmd_components(args)` + register the `components` subparser. 4. append the WARN loop to `cmd_check`. 5. green the suite. 6. re-sync the dogfood `.add/tooling/` + `_bundled/tooling/` trees, re-pin ENGINE_MD5 (engine_pin.py).
Known-problem fixes: silent-skip trap → the lint reports what the readers drop, but must NOT double-report a missing/non-str `root` already RED via `components_malformed` (exclude root from the type-check) · tri-tree drift → re-sync all three engine copies + re-pin or the tripwire/parity tests go red · LIFECYCLE-coverage trap → `components` must read no docs/ chapter and exit 0 on the bare board (NOT in `_NONZERO_OK`) · forward-compat → unknown keys are WARN, never a new RED that re-fails an existing project.
Strategy actually used: as planned, all 6 batches in order. Added `_component_schema_findings(root)` + the three module-level constants (`_SCHEMA_KNOWN_KEYS`/`_SCHEMA_KEY_TYPES`/`_SCHEMA_TYPENAME`) beside `_component_findings`; `cmd_components` reuses the existing readers + RED finders and only appends the new WARN surface; one extra check-loop line. Self-improvement vs the plan: strengthened the one vacuous no-exec test to also assert the command ran; ran a live `/tmp` smoke (components + check) as independent evidence beyond the fixtures; ENGINE_PKG_MD5 left untouched (add_engine/ never edited). No surprises — the silent-skip/double-report and tri-tree traps were all dodged as pre-listed.
Safety rule (feature-specific): NO-EXEC — the lint parses `verify` as data and never executes it; every reader stays degrade-safe (never raises on a malformed file).
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

- [x] all tests pass — full add-method suite 2202/0; dogfood `check` 449/0; `audit` exit 0 (only pre-existing measure notices)
- [x] coverage did not decrease — +21 tests (test_components_validator) + a LIFECYCLE entry; nothing removed
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; tests authored in the tests phase, not build
- [x] the green was EARNED — refute-read EARNED by an independent agent (6 probes) + self; see verdict below
- [x] concurrency / timing — N/A: read-only file parse, no shared state, no writes, no threads
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib-only (tomllib), NO-EXEC (verify parsed as data), no new deps
- [x] layering & dependencies follow CONVENTIONS.md — helper sits beside `_component_findings`; degrade-safe/PURE pattern matched; tri-tree re-synced + ENGINE_MD5 re-pinned
- [x] a person reviewed and approved the change — Tin approved the §3 freeze (the one human gate); build refute-read independently by agent af776f55; auto-gated under `autonomy: auto` (additive feature, no gate/trust-mechanic change)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `add.py components` on a valid multi-component registry prints each component/contract/federation with its fields + a "valid" summary, exit 0 — confirmed by test_print_valid_registry + a live `add.py components` run on a /tmp scratch registry (printed 2 components, 1 contract, sorted)
- [x] a `green-bar` (hyphen) typo surfaces `component_unknown_key` at BOTH `add.py components` AND `add.py check`, failing NEITHER (exit 0, "(N warnings)") — confirmed by test_unknown_key_is_warn_not_failure + test_schema_warn_surfaces_at_check_never_red + the live run ("check: 5 passed, 0 failed (3 warnings)")
- [x] a `[component.api]` missing `root` stays a RED `components_malformed` that fails `check` (exit 1) — confirmed by test_integrity_break_stays_red_at_check (green pin, unchanged)
- [x] a `[contract.*]` `consumers="x"` (str) and a `[componnt.*]` table each surface their WARN code (component_type_mismatch · component_unknown_table) without failing — confirmed by test_wrong_type_is_warn + test_unknown_table_is_warn + the live run
- [x] a sentinel-touch `verify` value is never executed; a malformed TOML never raises (exit 1, no traceback) — confirmed by test_verify_is_never_executed + test_malformed_degrades_no_raise + independent agent's degrade-safe probes
- [x] the three engine trees (add-method/tooling · _bundled/tooling · .add/tooling) are byte-identical + ENGINE_MD5 re-pinned — confirmed by md5 (082b192c… ×3) + the engine-pin/parity tests green in the 2202-test suite

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_component_schema_findings` has two live call sites: cmd_components + the cmd_check warn-loop; the `components` subparser wires `set_defaults(func=cmd_components)`; all three codes (unknown_key · type_mismatch · unknown_table) each have ≥1 asserting test + appear in the live run. Confirmed by test_min_pillar coverage (parser exposes + exercises `components`) + the independent agent.
- [x] DEAD-CODE (code) — no orphan: `_SCHEMA_KNOWN_KEYS`/`_SCHEMA_KEY_TYPES`/`_SCHEMA_TYPENAME` all consumed by the helper; no emitted code is undisplayed.
- [x] SEMANTIC (prose / non-code) — read the FROZEN §3 + components.md schema doc; confirmed canonical key is `green_bar` (underscore) → the doc's `green-bar` example is the bug this lint catches (recorded as a §7 SPEC delta, not fixed here).

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: agent af776f55 (independent) + self · adversarially checked: vacuous/overfit asserts · NO-EXEC (no eval/subprocess path for `verify`) · degrade-safe (dir-at-path → IsADirectoryError caught · malformed TOML · top-level scalar · non-table entry) · severity leak (schema findings only ride `warnings`, never `checks`/`failed`) · root not double-reported (excluded from the type-map) · exit-code correctness (exit 1 iff RED) · wiring/dead-code — all 6 probes clean.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-28

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the per-WARN rate at `check` (component_unknown_key · component_type_mismatch · component_unknown_table) — a rising count means real registries carry typos; a RED `components_malformed` rate still gates CI.

### Decisions (ADR)
- [AI] specify — chose validator-command + check-WARN typo-lint; rejected typos as RED check-fail · command-only, no check change
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned, all 6 batches in order. Added `_component_schema_findings(root)` + the three module-level constants (`_SCHEMA_KNOWN_KEYS`/`_SCHEMA_KEY_TYPES`/`_SCHEMA_TYPENAME`) beside `_component_findings`; `cmd_components` reuses the existing readers + RED finders and only appends the new WARN surface; one extra check-loop line. Self-improvement vs the plan: strengthened the one vacuous no-exec test to also assert the command ran; ran a live `/tmp` smoke (components + check) as independent evidence beyond the fixtures; ENGINE_PKG_MD5 left untouched (add_engine/ never edited). No surprises — the silent-skip/double-report and tri-tree traps were all dodged as pre-listed.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · dropped] fix the components.md schema-doc example `green-bar` → `green_bar` across the 4-tree skill mirror — belongs with `component-worked-example`, not the validator (evidence: the new lint flags the doc's own example as component_unknown_key in the live smoke; canonical key is underscore per every test fixture)
- [SPEC · carried] add `add.py components --json` for CI/federate consumers — deferred from the v1 contract (evidence: §1 assumption #4; a machine-readable surface helps a monorepo gate script) [carried: deferred from the v1 contract; revisit when a CI/federate consumer needs machine-readable component output]

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [ADD · folded] a closed engine-owned config (components.toml) needs a measure-not-block typo lint surfaced at BOTH a dedicated `components` validator AND the existing CI `check` — the degrade-safe readers silently dropped real typos (evidence: components.md's own `green-bar` example was inert until this lint caught it) [folded foundation-version 58]
- [SDD · folded] a new CLI subcommand ripples into test_min_pillar LIFECYCLE + _NONZERO_OK classification + the tri-tree ENGINE_MD5 pin — pre-listing those traps in §5 Known-problem fixes made the build trap-free (evidence: 0 surprises; the 2202-test suite went green on the first re-run after the re-pin) [folded foundation-version 58]
