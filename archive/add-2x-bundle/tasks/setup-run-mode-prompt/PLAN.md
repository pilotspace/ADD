# TASK: Setup phase asks the human to choose run mode

slug: setup-run-mode-prompt · created: 2026-06-29 · stage: mvp · sensitivity: mechanical · risk: low
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
  - `add-method/skill/add/phases/0-setup.md` — already has a `## Run mode` step (proposes parallel+auto, confirm-to-keep, records in Key Decisions) but only names `autonomy set`; it must also persist the STREAMS half to its new machine home.
  - `add-method/skill/add/streams.md` — names parallel+auto as the default/opt-out (test_setup_run_mode asserts this); the persist wiring is mirrored here.
  - existing persist mechanism (NO new engine code): `add.py streams set <parallel|sequential> --project` (persist-run-mode — writes PROJECT.md `streams:`) + `add.py autonomy set <level> --project` (autonomy-command — writes PROJECT.md `autonomy:`).
  - `add-method/tooling/test_setup_run_mode.py` — the content+parity guard for this step (test_cospecify_lift pattern).
Context (working folder):
  - 3-tree skill parity: canonical `add-method/skill/add/` → `add-method/src/add_method/_bundled/skill/add/` + repo-root `.add/` skill mirror; a guide edit ripples into the parity guards + lean fence + wording-lint.
  - `add.py cmd_init` writes `autonomy: auto` to PROJECT.md and NO `streams:` line (absent → parallel) — the non-interactive baseline that must stay byte-identical.
Honors (patterns / conventions):
  - the persistence HOME is PROJECT.md (`autonomy:` + `streams:` lines), read live by `_project_autonomy`/`_project_streams` — this task PERSISTS the setup answer there, not only as Key-Decisions prose.
  - prose-only: the engine already provides the set commands (persist-run-mode + autonomy-command); non-interactive `init` is untouched → byte-identical, NO re-pin.
  - the engine NEVER prompts — the ASK happens in the orchestrator's setup conversation (the guide directs it); show-before-ask + confirm-to-keep default (UDD: setup SUGGESTS, never interrogates).
Anchors the contract cites: `phases/0-setup.md` `## Run mode` step · `add.py streams set --project` · `add.py autonomy set --project` · `cmd_init` byte-identical baseline.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: The setup "Run mode" step explicitly asks the human to choose the run mode and persists BOTH halves (autonomy + streams) to PROJECT.md's machine home.
Framings weighed: prose wiring to the existing `streams set`/`autonomy set --project` commands PLUS a non-interactive `add.py init --run-mode {auto,conservative}` flag (chosen — human decision at the wave-1 freeze; covers both the interactive setup conversation and scripted installs) · prose-only (rejected at freeze — leaves no non-interactive seam) · leave the choice in Key-Decisions prose only (rejected — not machine-read by `_project_streams`/`_project_autonomy`)
Must:
<must>
  - the `## Run mode` step in `phases/0-setup.md` explicitly ASKS the human to choose `auto + parallel` vs `conservative + sequential` (confirm-to-keep default = `parallel + auto`).
  - on the answer, the guide PERSISTS BOTH halves to the machine home: `add.py autonomy set <level> --project` AND `add.py streams set <posture> --project` (today it names only autonomy).
  - `add.py init` gains a `--run-mode {auto,conservative}` flag for the non-interactive/scripted path: `auto` → `autonomy: auto` + `streams: parallel`; `conservative` → `autonomy: conservative` + `streams: sequential` (written via the existing `_autonomy_decl_line`/`_streams_decl_line` helpers).
  - `add.py init` with NO `--run-mode` flag is BYTE-IDENTICAL to today: `autonomy: auto`, NO `streams:` line (absent → parallel).
  - `streams.md` keeps naming `parallel + auto` as the default / opt-out.
  - all skill trees stay byte-identical (parity); the engine re-pins across trees.
</must>
Reject:
<reject>
  - a Run mode step that persists ONLY autonomy (omits `streams set`) -> content guard "run_mode_persist_incomplete" (the stale-machine-home gap this closes) — test asserts BOTH set commands are named
  - `add.py init --run-mode <other>` (not auto|conservative) -> argparse choices rejection (exit 2)
</reject>
After:
<after>
  - `phases/0-setup.md` directs an explicit ask + BOTH persist commands; `streams.md` names the default; skill parity holds.
  - `add.py init --run-mode conservative` writes `autonomy: conservative` + `streams: sequential`; `--run-mode auto` writes `autonomy: auto` + `streams: parallel`; NO flag → byte-identical to today; engine re-pinned across trees.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the flag's value vocabulary — `--run-mode {auto,conservative}` (two presets that each set BOTH halves) rather than two orthogonal flags (`--autonomy` + `--streams`). lowest confidence because a user might want an off-diagonal combo (e.g. auto + sequential); I judge the two presets match the setup comparison table's two rows and keep the seam minimal. if wrong: split into two flags (still byte-identical when both absent) — a contained argparse change.
  - [ ] the confirm-to-keep DEFAULT stays `parallel + auto` (matches the project default + streams.md); if wrong: flip the proposed default.
  - [ ] absent-flag `init` MUST stay byte-identical (no `streams:` line) — the non-negotiable invariant; verified by the existing init suite staying green.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the Run mode step asks and persists both halves
  Given the setup phase guide phases/0-setup.md
  When I read the "## Run mode" step
  Then it presents auto+parallel vs conservative+sequential (confirm-to-keep, default parallel+auto)
  And it directs persisting via BOTH add.py autonomy set <level> --project AND add.py streams set <posture> --project

Scenario: streams.md still names the default
  Given streams.md
  When I read it
  Then it names parallel+auto as the default / opt-out

Scenario: non-interactive init with no flag is byte-identical
  Given add.py init with no --run-mode flag
  When init completes
  Then PROJECT.md has autonomy: auto and NO streams: line
  And the output is byte-identical to today

Scenario: init --run-mode conservative seeds both halves
  Given add.py init --run-mode conservative
  When init completes
  Then PROJECT.md has autonomy: conservative AND streams: sequential

Scenario: init --run-mode auto seeds both halves
  Given add.py init --run-mode auto
  When init completes
  Then PROJECT.md has autonomy: auto AND streams: parallel

Scenario: an invalid run-mode value is rejected
  Given add.py init --run-mode turbo
  When init runs
  Then argparse rejects the value (exit 2)
  And no project is created

Scenario: the skill trees stay in parity
  Given the edited guide
  When parity is checked
  Then canonical and _bundled skill trees are byte-identical

Scenario: an incomplete persist is rejected by the guard
  Given a Run mode step that names only autonomy set (omits streams set)
  When the content guard runs
  Then it fails "run_mode_persist_incomplete"
  And the engine surface is unchanged
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
CONTENT CONTRACT (phases/0-setup.md + streams.md, verified by test_setup_run_mode.py)
  "## Run mode" step MUST:
    - present the choice: auto+parallel  vs  conservative+sequential  (confirm-to-keep; default parallel+auto)
    - name BOTH persist commands:  add.py autonomy set <level> --project  AND  add.py streams set <posture> --project
  streams.md MUST keep naming: "parallel", "auto", "default"/"opt-out"
  Reject (content guard): a step omitting "streams set" → "run_mode_persist_incomplete".

ENGINE CONTRACT (add.py cmd_init — verified by test_setup_run_mode / test_init_auto_default)
  add.py init [--run-mode {auto,conservative}]
    (absent)            -> BYTE-IDENTICAL to today: PROJECT.md "autonomy: auto", NO "streams:" line
    --run-mode auto      -> PROJECT.md "autonomy: auto"          + "streams: parallel"
    --run-mode conservative -> PROJECT.md "autonomy: conservative" + "streams: sequential"
    --run-mode <other>   -> argparse choices rejection (exit 2); no project created
  Implementation: reuse _autonomy_decl_line + _streams_decl_line after the existing PROJECT.md write.
  ENGINE_MD5 re-pinned across all 3 tooling trees + re-bundled.
Parity: canonical skill + _bundled skill byte-identical; engine trees byte-identical.
```

Least-sure flag surfaced at freeze: [spec] the flag's value vocabulary — `--run-mode {auto,conservative}` (two presets, each setting BOTH halves) vs two orthogonal `--autonomy`/`--streams` flags. Why least-sure: an off-diagonal combo (auto + sequential) isn't expressible; I judge the two presets match the setup table's two rows and keep the seam minimal. Cost if wrong: split into two flags (byte-identical when both absent) — a contained argparse change. [Human chose to add this engine flag at the wave-1 freeze.]

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

Coverage target: every `init --run-mode` branch (absent · auto · conservative · invalid) + the setup-content guard
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_init_runmode_absent_byte_identical: `init` (no flag) → PROJECT.md keeps "autonomy: auto", NO "streams:" line
  - test_init_runmode_auto: `init --run-mode auto` → PROJECT.md "autonomy: auto" AND "streams: parallel"
  - test_init_runmode_conservative: `init --run-mode conservative` → "autonomy: conservative" AND "streams: sequential"
  - test_init_runmode_invalid_exit2: `init --run-mode bogus` → exit 2 (argparse choices); no .add/ created
  - test_setup_step_names_both_persist_cmds: phases/0-setup.md Run mode step names BOTH "autonomy set ... --project" and "streams set ... --project"
  - test_streams_md_keeps_vocab: streams.md still names "parallel", "auto", "default"/"opt-out"
  - test_persist_incomplete_guard: a Run mode step lacking "streams set" trips the content guard (run_mode_persist_incomplete)
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/tooling/` `.add/tooling/` `add-method/skill/` `add-method/src/add_method/_bundled/skill/`
Strategy (ordered batches): 1. red tests in `test_setup_run_mode.py` (BOTH set commands named in the Run mode step + the persist-incomplete guard + the `init --run-mode` matrix: absent byte-identical · auto · conservative · invalid→exit2) · 2. `cmd_init` gains `--run-mode {auto,conservative}` argparse choice; after the existing PROJECT.md write, apply `_autonomy_decl_line`/`_streams_decl_line` when set · 3. edit `phases/0-setup.md` Run mode step (explicit ask + `streams set --project`) + keep `streams.md` green · 4. green canonical suite · 5. `prepare_bundle` (engine + skill) + dogfood-sync · 6. re-pin ENGINE_MD5 across trees · 7. full suite — fix init-default / skill-parity / lean-fence / wording-lint ripples (test edits in TESTS phase, re-cross).
Known-problem fixes: ABSENT-flag `init` MUST stay byte-identical → guard with the existing init suite + add an explicit assert; only WRITE the streams line when the flag is set · a skill-guide edit ripples into parity + lean fence + wording-lint — reclaim bytes from the same guide's prose, do test edits in TESTS phase, re-cross · engine change → re-pin all trees + re-bundle (`test_shared_engine_pin` / `test_bundle_parity`) · argparse `choices=["auto","conservative"]` gives the exit-2 rejection for free.
Strategy actually used: as planned, DELEGATED to a build subagent (live demonstration of advisor-gated-autonomy's actionable spawn — the `build → independent well-scoped batch` hint, run via the Agent tool while the orchestrator kept the engine-never-spawns invariant). The subagent wrote test_setup_run_mode.py (6 red InitRunMode tests), added `--run-mode {auto,conservative}` to cmd_init's argparse (choices→exit-2 for free), and inserted a post-SETUP_FILES block applying `_autonomy_decl_line` + `_streams_decl_line` ONLY when the flag is set, plus the `streams set --project` half in phases/0-setup.md (net ~0 bytes — reclaimed from a low-value parenthetical to respect the lean fence). The ORCHESTRATOR then independently reviewed the diff, propagated to all 3 trees (prepare_bundle + cp add.py to .add + cp 0-setup.md to .claude/skills), re-pinned ENGINE_MD5, ran the full suite (2339/0), and refute-read the live init matrix.
Safety rule (feature-specific): the absent-flag path is untouched (byte-identical); the flag only ADDS declaration lines via the existing idempotent decl-line helpers; the engine never prompts (the ASK is the orchestrator's).
Code lives in: the engine trees (`cmd_init` + `engine_pin.py` re-pin + bundle) and the skill trees (`phases/0-setup.md`).
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

- [x] all tests pass — full canonical suite 2339/0 green (+6 InitRunMode tests)
- [x] coverage did not decrease — 6 new engine tests + the 5 pre-existing RunModeStep content tests still green
- [x] no test or contract was altered during build — frozen §3 v1 untouched; tests were ADDED (red→green) by the build subagent in the tests phase
- [x] the green was EARNED — orchestrator independently refute-read the LIVE init matrix (not just the subagent's tests): no-flag byte-identical, auto→parallel, conservative→sequential, bogus→exit 2 no project — see verdict below
- [x] concurrency / timing safe — init is single-shot; the run-mode block only ADDS decl lines via idempotent helpers + atomic write; absent path untouched
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only; argparse choices bound the input
- [x] layering & dependencies follow CONVENTIONS.md — reuses _autonomy_decl_line/_streams_decl_line/_atomic_write; no new engine machinery; cmd_init structure preserved
- [x] reviewed — orchestrator manually reviewed the subagent's diff (block placement, byte-identical guard, guide edit) + self-gated per risk-tiered posture (mechanical; human spot-audit is the backstop)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [ ] `init` with NO flag leaves PROJECT.md byte-identical to today (autonomy: auto, no streams line) — confirmed by test_init_runmode_absent_byte_identical
- [ ] `init --run-mode auto` writes autonomy:auto + streams:parallel; `--run-mode conservative` writes autonomy:conservative + streams:sequential — confirmed by reading PROJECT.md in the matrix tests
- [ ] `init --run-mode bogus` exits 2 and creates no project — confirmed by test_init_runmode_invalid_exit2
- [ ] phases/0-setup.md Run mode step names both persist commands; streams.md keeps its vocab — confirmed by the two content tests + full suite parity/lean/wording green

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `--run-mode` argparse arg feeds `args.run_mode`, consumed by the new cmd_init block; reuses existing `_autonomy_decl_line`/`_streams_decl_line`/`_atomic_write` (no new symbols). Confirmed by the live init matrix + the 6 tests.
- [x] DEAD-CODE (code) — no orphan: the block is guarded by `run_mode is not None` and is the sole consumer of the new arg; no helper added.
- [x] SEMANTIC — read phases/0-setup.md Run mode step in full: it now names BOTH `autonomy set … --project` and `streams set … --project`; the removed parenthetical ("read from the dir name…") was redundant with "your judgment" — meaning preserved, net ~0 bytes.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self (orchestrator) · adversarially checked: did NOT trust the build subagent's own tests — re-ran the REAL `add.py init` in four scratch projects: (1) no flag → PROJECT.md keeps `autonomy: auto` with ZERO `streams:` lines (the sacred byte-identical invariant); (2) `--run-mode auto` → `streams: parallel` + `autonomy: auto`; (3) `--run-mode conservative` → `streams: sequential` + `autonomy: conservative`; (4) `--run-mode bogus` → exit 2 and NO `.add/` created. Also manually reviewed the diff for block placement (after the PROJECT.md write) and the guide's net-zero-byte edit. No overfit/stub — green is earned.

### GATE RECORD
Outcome: PASS
Reviewed by: Claude (self-gated — risk-tiered posture: mechanical/additive task auto-resolves verify on evidence + recorded refute-read; build delegated to a subagent, independently reviewed by the orchestrator; Tin's spot-audit is the backstop) · date: 2026-06-29

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose prose wiring to the existing `streams set`/`autonomy set --project` commands PLUS a non-interactive `add.py init --run-mode {auto,conservative}` flag; rejected prose-only (rejected at freeze — leaves no non-interactive seam) · leave the choice in Key-Decisions prose only (rejected — not machine-read by `_project_streams`/`_project_autonomy`)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned, DELEGATED to a build subagent (live demonstration of advisor-gated-autonomy's actionable spawn — the `build → independent well-scoped batch` hint, run via the Agent tool while the orchestrator kept the engine-never-spawns invariant). The subagent wrote test_setup_run_mode.py (6 red InitRunMode tests), added `--run-mode {auto,conservative}` to cmd_init's argparse (choices→exit-2 for free), and inserted a post-SETUP_FILES block applying `_autonomy_decl_line` + `_streams_decl_line` ONLY when the flag is set, plus the `streams set --project` half in phases/0-setup.md (net ~0 bytes — reclaimed from a low-value parenthetical to respect the lean fence). The ORCHESTRATOR then independently reviewed the diff, propagated to all 3 trees (prepare_bundle + cp add.py to .add + cp 0-setup.md to .claude/skills), re-pinned ENGINE_MD5, ran the full suite (2339/0), and refute-read the live init matrix.
- [AI] verify — gate PASS (reviewed by Claude (self-gated — risk-tiered posture: mechanical/additive task auto-resolves verify on evidence + recorded refute-read; build delegated to a subagent, independently reviewed by the orchestrator; Tin's spot-audit is the backstop))

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
