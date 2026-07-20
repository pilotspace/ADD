# TASK: Per-phase advisory subagent-spawn hint in status/guide

slug: step-spawn-hint · created: 2026-06-29 · stage: mvp · sensitivity: mechanical · risk: low
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
  - `add-method/tooling/add.py:cmd_status` + `cmd_guide` — where the per-phase spawn hint line is rendered for the ACTIVE task.
  - `add-method/tooling/add.py` readers it keys off: `_project_autonomy`/`_project_streams` (run_mode) · the active task's `phase` + `risk` (header) — same accessors persist-run-mode/risk-sensitivity-taxonomy use.
  - precedent to mirror: `_wave_block_lines` "tier hint: top → …; mid → …" — the advisory-tier line idiom + the mid/top vocabulary (streams.md / advisor.md §"Choosing the model").
  - source of the phase→idiom map: the 8 phase guides' `> Advisor · Confidence` hooks — ground=broad sweep · specify=researcher · scenarios=wide sweep · contract=NONE · tests=test-author · build=delegable batch · verify=refute-read · observe=lessons reviewer.
  - `add-method/tooling/test_per_step_hooks.py` (the existing advisor-hook guard) + a new `test_step_spawn_hint.py`.
Context (working folder):
  - engine ships across trees: canonical `add-method/tooling/` → `_bundled/` + repo-root `.add/tooling/`; an engine change re-pins ENGINE_MD5 + re-bundles.
  - heavily-tested surfaces: `cmd_status` (test_identity_in_status, test_streams_posture, …) + `cmd_guide` (test_guide) — a new line must not shift existing assertions (conditional render).
Honors (patterns / conventions):
  - **advisory only — the engine NEVER spawns** (run.md / advisor.md / the milestone's shared decision); this prints a HINT that points at advisor.md.
  - tier vocabulary is `mid`/`top` (streams.md), risk-keyed; a stronger tier never buys back a human gate.
  - the hint is the per-step companion to `waves`' tier hint — measure/surface, never block; absent where delegation doesn't fit (the contract human-gate).
Anchors the contract cites: `cmd_status`/`cmd_guide` render · `_spawn_hint_line(task, run_mode)` + `_SPAWN_HINTS` map · `_project_autonomy` · the active task `phase`/`risk`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: A per-phase advisory subagent-spawn hint in `status`/`guide` for the active task — idiom + tier, keyed off run_mode + risk; advisory, never spawns.
Framings weighed: a `_SPAWN_HINTS` phase→idiom map rendered as one conditional line in status/guide, tier from risk (chosen — mirrors the `waves` tier hint) · a flag-gated `--hint` subcommand (rejected — the hint belongs inline where the human already looks) · putting it only in `guide` (rejected — `status` is the primary resume surface)
Must:
<must>
  - `add.py status` and `add.py guide` print ONE `spawn hint:` line for the ACTIVE task's phase: `spawn hint: <phase> → <idiom> (tier: <mid|top>)`.
  - the idiom comes from the per-phase map (ground=broad sweep · specify=domain researcher · scenarios=wide scenario sweep · tests=red-suite test-author · build=independent well-scoped batch · verify=earned-green refute-read · observe=lessons-mining reviewer).
  - NO hint is printed where delegation doesn't fit — the `contract` human-gate phase (and `done`).
  - tier is risk-keyed: `top` when the active task is `risk: high`, else `mid`.
  - the hint is gated on run_mode: shown when autonomy is `auto`/`conservative`; under `manual` (human drives every step) no hint.
  - advisory ONLY — the line points to advisor.md; the engine never spawns. NO state.json change.
</must>
Reject:
<reject>
  - active task at phase `contract` -> NO spawn-hint line (delegation doesn't fit a human freeze gate) — the criterion's named example
  - autonomy `manual` -> NO spawn-hint line
  - (no runtime error codes — this is additive read-only surfacing)
</reject>
After:
<after>
  - in a self-driving run (auto/conservative), `status`/`guide` show the active phase's spawn idiom + tier; at `contract`/`done`/`manual` the line is absent; `add.py` is otherwise byte-identical.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the run_mode keying — I gate PRESENCE on autonomy (`manual` → no hint; auto/conservative → show) and set TIER from risk (`high`→top), and DON'T branch on streams (parallel/sequential). lowest confidence because the task says "keyed off run_mode" and run_mode = autonomy + streams; I judge streams (concurrency) irrelevant to a per-STEP spawn decision (that's `waves`' job), but the human may want sequential to suppress hints too. if wrong: add a streams branch — a one-line predicate change, no contract reshape.
  - [ ] the phase→idiom wording matches the phase guides' Advisor hooks (single source); if a guide's idiom is reworded later, the map is the pinned copy — acceptable drift (the map is the engine's terse label, the guide the prose). if wrong: derive from the guide instead of a literal map.
  - [ ] `contract` (+`done`) are the ONLY no-hint phases; if scenarios/tests should also be human-led-only, trim the map.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: a self-driving phase shows the spawn hint
  Given the active task is at phase verify under autonomy auto
  When I run add.py status
  Then it prints "spawn hint: verify → earned-green refute-read (tier: mid)"
  And add.py guide prints the same hint

Scenario: a high-risk task raises the tier to top
  Given the active task is risk: high at phase build
  When I run add.py status
  Then the spawn hint reads "(tier: top)"

Scenario: the contract human-gate shows no hint
  Given the active task is at phase contract
  When I run add.py status
  Then no "spawn hint:" line is printed

Scenario: manual autonomy shows no hint
  Given the active task is at phase build under autonomy manual
  When I run add.py status
  Then no "spawn hint:" line is printed

Scenario: the hint is advisory only
  Given any phase with a hint
  When the hint is printed
  Then no subagent is spawned and state.json is unchanged
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
ENGINE  _SPAWN_HINTS: dict[str, str]      # phase -> idiom; contract/done ABSENT → no hint
          ground:"broad sweep" · specify:"domain researcher" · scenarios:"wide scenario sweep" ·
          tests:"red-suite test-author" · build:"independent well-scoped batch" ·
          verify:"earned-green refute-read" · observe:"lessons-mining reviewer"
        _spawn_hint_line(task: dict, autonomy: str) -> str | None     # PURE
          None  if  phase ∉ _SPAWN_HINTS   OR   autonomy == "manual"
          else  f"spawn hint: {phase} → {_SPAWN_HINTS[phase]} (tier: {tier})"
          tier := "top" if task risk == "high" else "mid"

cmd_status / cmd_guide:  print _spawn_hint_line(active_task, _project_autonomy(root)) when non-None,
                         for the ACTIVE task only; placed so existing assertions don't shift.

Schema: NO state.json change. add.py otherwise byte-identical. Advisory only — never spawns.
        Idiom labels are the engine's pinned terse copy of the phase guides' Advisor hooks.
```

Least-sure flag surfaced at freeze: [spec] the run_mode keying — PRESENCE gates on autonomy (`manual`→none) and TIER on risk; it does NOT branch on the streams (parallel/sequential) half. Why least-sure: "keyed off run_mode" names both halves, but a per-STEP spawn decision is orthogonal to concurrency (that's `waves`). Cost if wrong: add a one-line streams branch — no contract reshape.

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

Coverage target: every contract branch (7 mapped phases · 2 suppression rules · both tiers) + 2 render surfaces
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_map_exact / test_contract_and_done_absent: `_SPAWN_HINTS` is the exact 7-phase map; contract+done absent
  - test_mid_tier_default: build + no risk + auto → "spawn hint: build → independent well-scoped batch (tier: mid)"
  - test_top_tier_for_high_risk: verify + risk:high + conservative → "(tier: top)"
  - test_none_at_manual: any phase + autonomy manual → None
  - test_none_at_unmapped_phase: contract/done → None
  - test_every_mapped_phase_renders: each of the 7 phases → its idiom line
  - test_status_renders_hint_for_active_ground: live `status`, fresh ground task, auto → the line appears
  - test_manual_dial_suppresses_hint: `autonomy set manual --project` → no "spawn hint:" in status
  - test_guide_renders_hint: live `guide` → the line appears
  - test_status_does_not_mutate_state: status leaves state.json byte-identical (advisory/read-only)
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/tooling/` `.add/tooling/`
Strategy (ordered batches): 1. red tests (`test_step_spawn_hint.py`) · 2. `_SPAWN_HINTS` map + `_spawn_hint_line(task, autonomy)` helper · 3. wire one conditional line into `cmd_status` + `cmd_guide` (active task only) · 4. green canonical suite · 5. `prepare_bundle` (engine) + dogfood-sync · 6. re-pin ENGINE_MD5 across trees · 7. full suite — fix any status/guide assertion ripples.
Known-problem fixes: the new line sits in heavily-tested `cmd_status`/`cmd_guide` → render conditionally (None → omit) + place it AFTER existing lines so test_identity_in_status / test_streams_posture / test_guide don't shift · engine change → re-pin all trees + re-bundle · keep the line absent at `contract`/`done`/`manual` (the named no-hint cases) · do NOT touch `waves`' own tier hint.
Strategy actually used: as planned. Added `_SPAWN_HINTS` (7-phase map) + pure `_spawn_hint_line(task, autonomy)` beside `_autonomy_lowered`. Wired one conditional line into cmd_status (after the `sensitivity:` line) and cmd_guide (after the `guide:` line) — active task only, placed AFTER existing lines so no prior assertion shifted. The contract named `_project_autonomy(root)` as the dial source — it EXISTS (used at the project-autonomy status line), so I used it verbatim; risk is header-derived via the existing `_RISK_HIGH_RE` + `_task_header` (state carries no risk). One escapee fix: the word "dial" in the helper docstring tripped `test_ubiquitous_language` (domain term is "autonomy level") → reworded. Re-bundled + dogfood-synced + re-pinned ENGINE_MD5 twice (the lint fix changed the md5).
Safety rule (feature-specific): advisory only — the hint never triggers a spawn and never mutates state; pure render derived from the active task header + project autonomy.
Code lives in: the three engine trees above (`add.py` + `engine_pin.py` re-pin + bundle mirror).
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

- [x] all tests pass — full canonical suite 2333/0 green (+11 test_step_spawn_hint)
- [x] coverage did not decrease — added 11 tests (pure helper branches + 2 render surfaces)
- [x] no test or contract was altered during build — frozen §3 v1 untouched; only the new test file added
- [x] the green was EARNED — adversarial refute-read (scratch CLI): risk:high header → tier:top (real integration path), contract & manual → suppressed — see verdict below
- [x] concurrency / timing safe — advisory render only; status/guide are read-only (load_state, never save_state); no spawn, no mutation
- [x] no exposed secrets, injection openings, or unexpected dependencies — pure stdlib render; no new deps
- [x] layering & dependencies follow CONVENTIONS.md — helper beside _autonomy_lowered; reuses _project_autonomy/_RISK_HIGH_RE/_task_header; waves' own tier hint untouched
- [x] reviewed — self-gated per risk-tiered posture (mechanical/additive; human spot-audit is the backstop)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [ ] `add.py status` for an active task at a mapped phase under a non-manual autonomy level prints exactly one `spawn hint:` line naming the phase, its idiom, and a tier of top or mid — confirmed live (status showed `spawn hint: tests → red-suite test-author (tier: mid)`)
- [ ] the line VANISHES under `autonomy: manual` and at the contract/done phases — confirmed by test_manual_dial_suppresses_hint + test_none_at_unmapped_phase
- [ ] `add.py guide` prints the same advisory line; neither status nor guide mutates state.json (advisory-only) — confirmed by test_guide_renders_hint + test_status_does_not_mutate_state
- [ ] `add.py waves` output and all prior status/guide assertions are unshifted (additive line, placed after existing lines) — confirmed by full suite 2333/0

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_spawn_hint_line` is called in both cmd_status and cmd_guide; `_SPAWN_HINTS` is read only inside `_spawn_hint_line`. Confirmed live (status + guide both rendered the line) + by the 2 CLI tests.
- [x] DEAD-CODE (code) — no orphan: the map has exactly one reader (the helper), the helper exactly two callers (status, guide). No symbol added "for later".
- [x] SEMANTIC — idiom labels are the pinned terse copy of the phase guides' Advisor hooks; cross-checked against §0's hook list (ground=broad sweep … observe=lessons reviewer). Match.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self · adversarially checked: ran the real CLI in a scratch project (not just the pure helper) — a `risk: high` header produced `(tier: top)` (proves cmd_status parses risk from the header via _RISK_HIGH_RE, not a hardcoded mid); the `contract` phase printed NO line; `autonomy: manual` printed NO line even at build. Also confirmed status leaves state.json byte-identical (advisory/read-only). No overfit/stub — green is earned.

### GATE RECORD
Outcome: PASS
Reviewed by: Claude (self-gated — risk-tiered posture: mechanical/additive task auto-resolves verify on evidence + recorded refute-read; Tin's spot-audit is the backstop) · date: 2026-06-29

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose a `_SPAWN_HINTS` phase→idiom map rendered as one conditional line in status/guide, tier from risk; rejected a flag-gated `--hint` subcommand (rejected — the hint belongs inline where the human already looks) · putting it only in `guide` (rejected — `status` is the primary resume surface)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned. Added `_SPAWN_HINTS` (7-phase map) + pure `_spawn_hint_line(task, autonomy)` beside `_autonomy_lowered`. Wired one conditional line into cmd_status (after the `sensitivity:` line) and cmd_guide (after the `guide:` line) — active task only, placed AFTER existing lines so no prior assertion shifted. The contract named `_project_autonomy(root)` as the dial source — it EXISTS (used at the project-autonomy status line), so I used it verbatim; risk is header-derived via the existing `_RISK_HIGH_RE` + `_task_header` (state carries no risk). One escapee fix: the word "dial" in the helper docstring tripped `test_ubiquitous_language` (domain term is "autonomy level") → reworded. Re-bundled + dogfood-synced + re-pinned ENGINE_MD5 twice (the lint fix changed the md5).
- [AI] verify — gate PASS (reviewed by Claude (self-gated — risk-tiered posture: mechanical/additive task auto-resolves verify on evidence + recorded refute-read; Tin's spot-audit is the backstop))

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
