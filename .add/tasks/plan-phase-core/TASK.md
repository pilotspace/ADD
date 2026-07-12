# TASK: Reorder to expectations-first: collapse ground+contract into the plan phase

slug: plan-phase-core · risk: high · created: 2026-07-12 · stage: mvp
milestone: expectations-first
autonomy: conservative   <!-- level: manual < conservative < auto — lower for a high-risk task (`add.py autonomy set`). Multi-component repo? add a `component: <name>` line (.add/components.toml) to join that root to §5 Scope. -->
phase: build   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining? declare `risk: high` on the slug line + a lowered autonomy — the engine refuses an unguarded completion (`unguarded_high_risk_auto`). A comment is never a declaration. -->

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add_engine/constants.py`: `PHASES` (drop `ground`, rename `contract`→`plan`) · `PHASE_GUIDE` (ground/contract keys) · `PHASE_OWNER` (`ground:ai`, `contract:seam`) · `PHASE_GROUPS.DIRECTION` · `PHASE_AGENT` (ground/contract) · `_FALLBACK_TASK` + `_FALLBACK_TASK_FAST` (embedded task templates, phase:ground, "Anchors the contract cites:") · `_SKIPPABLE_PHASES` comment
  - `add.py`: `_phase_index` (ground/contract→plan legacy map) · `cmd_new_task` (seed `"phase":"specify"`, was ground; the plan-phase opens the run) · `cmd_freeze` (`_phase_index("contract")` gate → `plan`) · `_build_entry`/`cmd_advance` freeze gate (reads §3 `Status:`) · `cmd_advance` `nxt=="contract"` + `cmd_phase` `args.phase=="contract"` (consumer-hold — RENAME to plan) · `_FRONT_PHASES` (contract→plan) · `decide_data`/`render_decide` seam (`phase=="ground"` seam + `ground` label; `_FRONT_PHASES` "front"; seam_label "CONTRACT APPROVAL"→"PLAN") · `_next_command` (`("ground","specify","scenarios")`, `phase=="contract"`) · `_SPAWN_HINTS` (`ground` key) · `_PHASE_GUIDE_FILES` (`0-ground.md`/`3-contract.md`) · `_grounded_state` + `_section0_anchors` + `_ground_section`/`_read_ground_sha`/`_ground_cites_line_ref` (§0→§3-plan grounding sub-block) · `task_phases`/render.py `PHASES[:-1]` phase-detail · status/guide `_frozen = ph=="contract"` · `advance --to` bounds + help
  - `engine_pin.py`: `ENGINE_MD5` + `ENGINE_PKG_MD5` (re-aim after edits)
  - `templates/TASK.md.tmpl` + `TASK.fast.md.tmpl` (×3 trees): drop §0, §3 CONTRACT→§3 PLAN with `### Grounding`/`### Contract`/`### Build-strategy` sub-blocks; phase marker `ground`→`specify`; §5 `§0 Honors` xref
Context (working folder): `.add/tooling/` is a GITIGNORED dogfood twin — resync from source after edits (byte-identical is a tested floor); `.add/SEAMS.md` pins add.py line numbers (will drift); abandoned `plan-phase-merge` history = the prior attempt (196 test failures, self-inflicted "fold" slang).
Honors (patterns / conventions): 3-tree byte parity (tooling · _bundled · .add) enforced by tests · ENGINE_MD5/PKG pins · slang guard bans "fold"/"folded" in string literals (test_ubiquitous_language) · TESTS re-cross discipline (test edits via `phase tests`→edit→`phase build`) · grounding floor invariant (contract cites only grounded anchors).
Seams consulted: `.add/SEAMS.md` (add.py line pins — expect drift) · the abandoned plan-phase-merge diff (what NOT to repeat).
Anchors the contract cites: `PHASES` · `PHASE_GROUPS.DIRECTION` · `PHASE_OWNER` · `_FRONT_PHASES` · `_phase_index` · `_grounded_state`/`_section0_anchors` · `cmd_freeze` freeze gate · `decide_data` seam · templates §3 PLAN sub-blocks (`### Grounding`/`### Contract`/`### Build-strategy`).
Issues/Risks (→ feed §1):
  - ⚠ `contract` is HEAVILY overloaded — the cross-component contract system (`_contracts`, `_contract_snapshot`, `producer_contract_*`, `contract_pin`, `.add/contracts/*.json`, `_contract_body_hash`, `_FRONT_PHASES` aside) is UNRELATED to the contract PHASE. Renaming must be SURGICAL (phase-token only), never a blanket s/contract/plan/.
  - The §-renumber is SMALL: only §0 drops + §3 CONTRACT→§3 PLAN; §1/§2/§4–§7 keep their numbers. `_contract_frozen(raw[3])` still reads §3 (freeze stays §3) — minimal.
  - Grounding measure `_grounded_state` reads §0 (`raw[0]`) — must re-point to §3 PLAN's grounding sub-block; the "Anchors the contract cites:" line moves with it.
  - BUILD-STRATEGY LOCATION is the size fork (→ §1 lowest-confidence flag): physically MOVE §5's Strategy/Approach into §3 PLAN (big ripple: ADR harvest, §5 scope-lock, facets, tamper guard) vs a LIGHT §3 `### Build-strategy` sub-block, §5 execution unchanged.
  - Legacy state migration: existing task records at phase `ground`/`contract` must still load (map ground→specify, contract→plan) — fail-soft in `_phase_index` + a load normalizer; the prior attempt corrupted state.json via an over-eager load migration (persisted spurious flips).
  - Test blast radius is large (prior smaller change = 196 fails); every phase-walk / §0-field / seam / freeze-gate / fixture test touches this.
Related intent: milestone `expectations-first` goal (grounding serves the HOW, WHAT flows from the milestone); human analysis 2026-07-12; GLOSSARY `ground:`/`contract:` terms (→ `plan:`).
Ground SHA: ad950c2

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Expectations-first phase flow — collapse `ground`+`contract` into a single `plan` phase.
Framings weighed: full-move plan phase (chosen — `plan` owns grounding+contract+build-strategy; §5 is execution-only) · light-reference plan (rejected: human wants the plan to OWN the strategy, not point at §5) · reorder-only keeping contract a separate phase (rejected: doesn't unify the change plan).
Must:
<must>
  - M1  `PHASES == ("specify","scenarios","plan","tests","build","verify","observe","done")` — `ground` and `contract` are absent as phases; 7 work phases.
  - M2  `PHASE_GROUPS["DIRECTION"] == ("specify","scenarios","plan","tests")`; PHASE_OWNER/PHASE_AGENT/PHASE_GUIDE carry `plan`, not ground/contract.
  - M3  `new-task` seeds phase `specify` (the run opens by stating the projected expectations, not by grounding).
  - M4  the single human freeze is at `plan`: `cmd_freeze` requires phase ≥ `plan`; crossing `plan → tests` requires §3 PLAN FROZEN (`contract_not_frozen` otherwise); the `--skip-freeze` recorded bypass still works.
  - M5  the TASK.md (both templates, ×3 trees) renders `## 3 · PLAN` with `### Grounding` (prose) → `### Contract` (a FENCED shape block, first fence in §3) → `### Build-strategy` (prose); the `Status:` freeze line lives in §3.
  - M6  grounding floor preserved: `_grounded_state` reads the §3 PLAN `### Grounding` "Anchors the contract cites:" line; the frozen contract may cite ONLY anchors named there; the ground-anchor-sha drift check reads §3.
  - M7  contract stays HARD, grounding+build-strategy stay SOFT: the tamper fingerprint (`_contract_body_hash`) keys on the first fenced block in §3 (the Contract) only — prose sub-blocks are not tamper-frozen.
  - M8  §5 BUILD is execution-only: `Scope (may touch)` + Strategy/Approach/Data/Pattern/Optimization/Persona MOVE into §3 `### Build-strategy`; §5 keeps `Strategy actually used` (verify-time) + the §7 ADR harvest of the build decision. The build scope-lock reads the §3 Scope line.
  - M9  decision seam: an unfrozen `plan` is the "PLAN" approval seam (replaces the ground seam + CONTRACT-APPROVAL label); the `ground` seam is gone; `_FRONT_PHASES` names `plan`, not `contract`.
  - M10 legacy states load: a task record at phase `ground` maps to `specify`, `contract` maps to `plan` (fail-soft `_phase_index` + an idempotent load normalizer) — status/check never crash; migration is idempotent (no spurious re-writes of already-migrated or unrelated tasks).
  - M11 the cross-component contract system (`_contracts`/`_contract_snapshot`/`producer_contract_*`/`contract_pin`) is UNTOUCHED — only the phase token changes.
  - M12 3-tree byte parity holds (tooling · _bundled · .add); `ENGINE_MD5` + `ENGINE_PKG_MD5` re-pinned; full suite green.
</must>
Reject:
<reject>
  - a blanket `s/contract/plan/` that renames the cross-component contract system -> "component_contract_broken" (a design defect, caught by test_cross_component_*)
  - an over-eager load migration that persists phase rewrites to unrelated/already-migrated tasks -> "state_corrupted" (the prior-attempt failure mode)
  - crossing `plan → tests` with a DRAFT §3 and no `--skip-freeze` -> "contract_not_frozen"
  - a §3 PLAN whose contract cites an anchor not named in its `### Grounding` -> grounding-floor violation (freeze-review + task_not_grounded warning)
</reject>
After:
<after>
  - a fresh task walks `specify → scenarios → plan →[freeze]→ tests → build → verify → observe → done`; grounding + contract + build-strategy are all inside the one frozen `plan`.
  - every existing engine behavior (freeze gate, tamper guard, scope-lock, ADR harvest, cross-component holds, fast lane, ai-plan-verify) works under the new token map with no weakened test.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ Legacy phase migration is the lowest-confidence part — mapping `ground→specify` / `contract→plan` and PERSISTING it on load. Low confidence because the prior attempt corrupted state.json by persisting spurious flips (engine + state drifted apart). If wrong: active tasks silently jump phase or check crashes. Mitigation: idempotent normalizer that only rewrites the two legacy tokens, shipped ATOMICALLY with the engine (never half-applied); pinned by a legacy-load test.
  - [ ] The tamper guard reads only the FIRST fenced block in §3 (so Build-strategy prose isn't frozen) — confirm `_contract_body_hash`/`_contract_fingerprint` take `m.group(1)` of the first fence; if a build-strategy fence precedes the contract fence it breaks. Mitigation: Contract sub-block's fence is FIRST in §3.
  - [ ] `report <task>` phase-detail on ARCHIVED legacy TASK.md (§0..§7 layout) renders best-effort under new §-map — acceptable (out of scope: perfect legacy render); status/check loading is the floor.
</assumptions>

<!-- EXIT: every rule + rejection stated; assumptions ranked lowest-confidence first, top 1–2 ⚠-flagged with why + cost (or an honest "none material" naming the biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: phase order is expectations-first          # M1, M2
  Given the engine constants
  Then PHASES == ("specify","scenarios","plan","tests","build","verify","observe","done")
  And "ground" and "contract" are not members
  And PHASE_GROUPS["DIRECTION"] == ("specify","scenarios","plan","tests")

Scenario: a new task opens at specify                # M3
  Given an initialised project
  When I run new-task
  Then the task state phase is "specify"
  And its TASK.md marker line reads "phase: specify"

Scenario: the one human freeze is at plan             # M4
  Given a task at phase "plan" with a drafted §3 PLAN + a least-sure flag
  When the human runs freeze
  Then §3 Status becomes "FROZEN @ v1 — approved by <name>"
  And a task at "scenarios" (before plan) is refused freeze (contract_not_drafted)

Scenario: crossing plan→tests needs a frozen plan     # M4, R3
  Given a task at "plan" with a DRAFT §3
  When advance crosses into tests without --skip-freeze
  Then it is refused "contract_not_frozen"
  And with --skip-freeze it crosses and records a freeze_skipped marker

Scenario: template renders the §3 PLAN sub-blocks      # M5
  Given a rendered TASK.md (each template tree)
  Then §3 is "## 3 · PLAN" containing "### Grounding", "### Contract", "### Build-strategy"
  And the first fenced block in §3 is the Contract shape
  And a "Status:" freeze line sits within §3

Scenario: the grounding floor reads §3                 # M6
  Given a §3 PLAN whose "Anchors the contract cites:" line is filled
  Then _grounded_state(raw) is True
  And a placeholder/empty Anchors line gives False; no §3 plan section gives None

Scenario: contract hard, grounding+strategy soft       # M7
  Given a frozen §3 PLAN
  When the ### Build-strategy or ### Grounding prose is edited but the fenced Contract is not
  Then no "contract_tampered" is raised
  And editing the fenced Contract shape raises "contract_tampered"

Scenario: build is execution-only; scope reads §3      # M8
  Given the §3 PLAN "Scope (may touch)" line and §5 BUILD
  Then the build scope-lock reads the §3 Scope line
  And §5 retains "Strategy actually used" harvested into the §7 Decisions (ADR)

Scenario: plan is the approval decision seam           # M9
  Given a task at "plan" with an unfrozen §3
  When the decision-seam digest is rendered
  Then the seam label reads "PLAN" (not "GROUND" or "CONTRACT APPROVAL")
  And _FRONT_PHASES contains "plan" and not "contract"

Scenario: legacy ground/contract states still load     # M10, R2
  Given a state.json record at phase "ground" and another at "contract"
  When the engine loads and runs status then check
  Then neither crashes
  And "ground" resolves as "specify" and "contract" as "plan"
  And a second load rewrites nothing further (idempotent; unrelated tasks untouched)

Scenario: cross-component contracts are untouched       # M11, R1
  Given a producer/consumer component-contract fixture
  Then producer_contract_* holds and _contract_snapshot behave exactly as before
  And the cross_component test suites stay green (a blanket rename would fail them)

Scenario: three trees stay byte-identical and pinned    # M12
  Given the tooling, _bundled, and .add engine trees
  Then add.py, constants.py, and both templates are byte-identical across the three
  And ENGINE_MD5 + ENGINE_PKG_MD5 match engine_pin
  And the full test suite is green

Scenario: an ungrounded frozen contract is flagged      # R4
  Given a FROZEN §3 PLAN citing an anchor not named in its ### Grounding
  When check runs
  Then it warns "task_not_grounded"
  And the shape stays frozen (a warning, never a silent pass)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
ENGINE SHAPE (add_engine/constants.py)
  PHASES        = ("specify","scenarios","plan","tests","build","verify","observe","done")
  PHASE_GROUPS  = { DIRECTION:("specify","scenarios","plan","tests"), BUILD:("build",), VERIFY:("verify","observe") }
  PHASE_OWNER   = { specify:human, scenarios:human, plan:seam, tests:ai, build:ai, verify:human, observe:ai, done:human }
  PHASE_AGENT   = { specify:add-design, scenarios:add-design, plan:add-design, tests:add-build, build:add-build, verify:add-verify, observe:add-verify }
  PHASE_GUIDE / _PHASE_GUIDE_FILES / _SPAWN_HINTS: keyed on `plan` (no ground/contract keys)

ENGINE BEHAVIOR (add.py)
  new-task            -> seeds phase "specify"
  cmd_freeze          -> allowed when _phase_index(phase) >= _phase_index("plan"); stamps §3 Status: FROZEN @ vN
  advance plan->tests -> requires _contract_frozen(§3) else _die("contract_not_frozen"); --skip-freeze records freeze_skipped
  _FRONT_PHASES       = ("specify","scenarios","plan","tests")
  decide_data/seam    -> unfrozen "plan" => seam "front", label "PLAN"; NO "ground" seam
  _grounded_state     -> reads §3 PLAN "### Grounding" "Anchors the contract cites:" (was §0)
  ground-anchor-sha   -> _ground_section/_read_ground_sha read §3 PLAN grounding sub-block
  scope-lock          -> reads the §3 "Scope (may touch):" line (was §5)
  _contract_body_hash -> UNCHANGED: first fenced block in §3 (the Contract) => contract HARD, prose SOFT
  legacy load         -> _phase_index + idempotent normalizer: state phase "ground"->"specify", "contract"->"plan"
  UNTOUCHED           -> cross-component contract system (_contracts/_contract_snapshot/producer_contract_*/contract_pin)

TEMPLATE SHAPE (templates/TASK.md.tmpl + TASK.fast.md.tmpl, ×3 trees, byte-identical)
  no "## 0 · GROUND"; phase marker "specify"
  ## 3 · PLAN
    ### Grounding      (Touches/Context/Honors/Seams/Anchors the contract cites/Issues/Related intent/Ground SHA)
    ### Contract       (the FENCED shape block — FIRST fence in §3 — + Glossary deltas + Status + Reported)
    ### Build-strategy (Scope (may touch)/Strategy/Approach/Data strategy/Pattern/Optimization stance/Persona)
  ## 5 · BUILD         (Strategy actually used/Safety rule/Code lives in/Constraints — execution-only)

PINS: engine_pin.ENGINE_MD5 + ENGINE_PKG_MD5 re-aimed; 3-tree byte parity; full suite green.
```

Glossary deltas: `plan: the third task phase — the frozen change plan uniting grounding (real code), the contract (frozen shape), and the build-strategy (soft, self-improvable); replaces the ground and contract phases`. Retires GLOSSARY `ground:`/`contract:` phase terms (the cross-component `contract` artifact term stays).
Status: FROZEN @ v1 — approved by Tin Dang
Least-sure flag surfaced at freeze: [spec] the legacy phase migration (state `ground`→`specify`, `contract`→`plan`) is the lowest-confidence part — the prior attempt corrupted state.json by persisting spurious flips. Mitigated by an idempotent normalizer shipped atomically with the engine + a legacy-load test; cost if wrong: active tasks jump phase / check crashes.
Reported: yes
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag (§1 ⚠ feeds it; a flag may point at any part — run.md). Approved -> Status: FROZEN @ vN — approved by <name>; changing a frozen contract = change request back to SPECIFY. EXIT: frozen · every §1 rejection has a contracted response · names match GLOSSARY (new terms = Glossary delta) · flag surfaced. -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: behavior-complete over M1–M12 + R1–R4 (new suite) + the full existing suite migrated green.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - ConstantsShape: PHASES/DIRECTION/PHASE_OWNER-AGENT-GUIDE name `plan` · plan owner=seam · _FRONT_PHASES · covers M1,M2,M4,M9
  - GroundingFloorReadsPlan: _grounded_state True/False/None reading §3 PLAN grounding · covers M6
  - ContractHardStrategySoft: _contract_body_hash keys on first §3 fence (prose soft, fence hard) · covers M7
  - TreeParityAndPins: add.py ×3 byte-identical == ENGINE_MD5; templates ×3 identical · covers M12
  - _CLI.test_new_task_seeds_specify: new-task → phase specify · covers M3
  - _CLI.test_template_renders_plan_subblocks: no §0; §3 PLAN Grounding/Contract/Build-strategy · covers M5
  - _CLI.test_plan_phase_is_approval_seam: seam=front, label PLAN · covers M9
  - _CLI.test_legacy_ground_contract_states_load: ground→specify, contract→plan, idempotent · covers M10, R2
  - _CLI.test_plan_to_tests_needs_frozen: DRAFT §3 refuses cross (contract_not_frozen) · covers M4, R3
  - MIGRATION: existing suite (cross_component/*, ground_*, phase_*, freeze_*, fastlane_*, streams…) migrated to new tokens — R1 proven by test_cross_component_* staying green.
</test_plan>

Tests live in: `add-method/tooling/test_plan_phase_flow.py` (new) + the migrated existing suite under `add-method/tooling/` · MUST run red before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir · a token with "/" = the project root · a bare name = a sibling of the previous token's dir · a directory counts its *.py files (non-recursive) · declared counts marked † · outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/` `.add/tooling/` `.add/SEAMS.md` `tmp/`
Strategy (ordered batches): 1. red suite (test_plan_phase_flow.py) pinning M1–M12 · 2. constants.py (PHASES/groups/owners/agents/guides/_FALLBACK_*) · 3. add.py surgical phase-token edits (freeze gate · seam · _FRONT_PHASES · _grounded_state→§3 · scope-lock→§3 · _next_command · guide-files/spawn-hints · legacy normalizer) · 4. templates ×3 (§3 PLAN sub-blocks · §5 execution-only) · 5. migrate the existing red suite through TESTS re-cross · 6. resync dogfood + re-pin ENGINE_MD5/PKG · 7. full suite green.
Approach (domain strategy): a phase-token RENAME + a §-section relocation, done surgically to avoid the cross-component `contract` collision — token-scoped edits guided by the §0 Touches map, never a blanket substitution; migration idempotent + atomic with the engine.
Data strategy: task phase records (state.json) migrate legacy `ground`→`specify`/`contract`→`plan` on load; TASK.md §3 becomes the PLAN section carrying grounding-anchors + fenced contract + build-strategy; measures (`_grounded_state`, scope-lock, tamper hash) re-point their §-reads.
Pattern: extends the engine's existing PHASES-index-is-§-ordinal convention (§0 Honors: 3-tree byte parity + engine_pin re-aim + slang guard) — the same discipline every prior phase-shape task followed.
Optimization stance: correctness-first, no budget; ⚠ the legacy-migration idempotency is the facet trusted least (risk: high → consult add-advisor at verify).

Persona (required): methodology-engine-dev — builds the engine that drives builds; deterministic, fail-loud, no silent skips.
Spawn isolation (default): inline build (tightly coupled engine+template+test edits on add.py; parallel worktrees would conflict); a refute-read/3-lens verify subagent may spawn at VERIFY.
Known-problem fixes: blanket s/contract/plan/ → surgical token edits + cross_component tests as the guard · over-eager load migration → idempotent, two-token-only normalizer + legacy-load test · build-strategy fence before contract fence → Contract sub-block's fence is FIRST in §3.
Strategy actually used: <fill at VERIFY — the strategy you ACTUALLY used (or "as planned"); harvested into the §7 Decisions (ADR) block as the [AI] build decision>
Safety rule (feature-specific): the cross-component contract system stays byte-behavior-identical (test_cross_component_* green throughout); the dogfood engine + state move atomically (never half-migrated).
Code lives in: `add-method/tooling/` (source of truth; mirrored to `_bundled` + `.add/tooling`)
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token with "/" = project root · a bare name = sibling of the previous token's dir · a DIRECTORY token covers its whole subtree (diverges from §4's non-recursive counting) · outside-root resolutions drop fail-closed · absent line = UNDECLARED (grandfathered, never retro-red) · enforcement live: a completing verify gate refuses an out-of-scope build (scope_violation → self-heal); check surfaces it. EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

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
- [ ] `add.py status` on a fresh task shows `phase: specify` and a walk reaches `plan` before `tests` — confirmed by running new-task + advance twice
- [ ] a rendered TASK.md has no `## 0 · GROUND` and a `## 3 · PLAN` with Grounding/Contract/Build-strategy sub-blocks — confirmed by reading the rendered file
- [ ] the full existing suite + test_plan_phase_flow are green; test_cross_component_* unchanged-green (R1) — confirmed by `python3 -m unittest`
- [ ] a legacy state at phase `ground`/`contract` loads without crash (migrates to specify/plan) — confirmed by the legacy-load test + `add.py check`
- [ ] add.py/constants/templates byte-identical across the 3 trees == engine_pin — confirmed by md5 + TreeParityAndPins

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [ ] DIALECT — tests speak the same value formats the spec's examples use (spec-dialect floor): <what confirmed>
- [ ] WIRING (code) — every new symbol is referenced; record where / how confirmed
- [ ] DEAD-CODE (code) — no new unused or orphaned symbol introduced
- [ ] SEMANTIC (prose / non-code) — read in full, not skimmed: <what read · what confirmed>

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [ ] every symbol §3 CONTRACT cites still resolves in the current tree — confirmed by <how / where>
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

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency — the §5 Optimization stance budget is a monitor here, not just an intention>

### Decisions (ADR)
<harvested at done from §1/§3/§5/§6 — do not hand-edit; one actor-tagged line per decision, refilled only while this placeholder stands>

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
