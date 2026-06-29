# TASK: Persist auto+parallel run mode as machine state

slug: persist-run-mode · created: 2026-06-29 · stage: mvp · risk: high
autonomy: conservative   <!-- LOWERED from project default: this milestone is risk:high + method-defining (advisor-gated-autonomy) — the human owns the verify gate; engine refuses an unguarded high-risk auto completion. Original note: inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. Multi-component repo (monorepo/multi-repo)? add a `component: <name>` line (declared in `.add/components.toml`) to ADD that component's root to your §5 Scope; omit for single-component projects (byte-identical default). -->
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
  - `add_engine/autonomy.py:_project_autonomy(root)` — resolves the project-default autonomy by reading the `autonomy:` declaration line in **PROJECT.md** (fail-safe: absent→auto, garbled→conservative). PROOF the run-mode throttle is persisted in PROJECT.md, NOT state.json.
  - `add_engine/autonomy.py:_autonomy_level / _effective_autonomy / _project_autonomy_token` — the autonomy resolver set.
  - `add.py:_autonomy_decl_line(text, level)` — PURE idempotent rewrite of the single `autonomy:` declaration line (preserves trailing comment; inserts after `slug:`/heading/prepend); caller does `_atomic_write`. The pattern a `streams:` line mirrors.
  - `add.py:cmd_autonomy` (parser `autonomy` ~6191) — `show`/`set`; `--project` writes the line into PROJECT.md (comment ~1092: "state.json is untouched — autonomy stays a header token").
  - `add.py:cmd_status` ~1474-1477 — prints `project autonomy: {_project_autonomy(root)} (default — new tasks inherit)`, read LIVE from PROJECT.md each session; ~1588-1592 prints the active task's `autonomy:` level. The render point a combined run_mode line joins.
  - `add.py:cmd_waves` / `_schedule` ~2998-3110 — read-only DAG scheduler (waves · critical_path · tiers · blocked), recomputed each call; NO persisted parallel flag — the streams half of run mode is implicit here.
  - `add.py:save_state` / `load_state` + `.add/state.json` — keys: project · stage · active_task · tasks · created · updated · milestones · active_milestone · archived · active_milestones · active_tasks · todos. NO autonomy/run_mode/streams key today.
  - `_RISK_HIGH_RE` ~957 / `_autonomy_decl_line` grammar ~1101 — anchored declaration-line parsing (line-start or `·`-inline; value stops at space/`<`/`#`/`|`). The grammar a `streams:` token reuses.
Context (working folder):
  - `phases/0-setup.md` "Run mode" ~63-72 — proposes `parallel · auto`; "Record the chosen mode in **PROJECT.md Key Decisions**" = the prose-only home today.
  - `streams.md` (skill) — defines run mode: "`parallel + auto` … is the project default"; downgrade via `autonomy set conservative --project`. Parallel = orchestrator behavior, not a stored flag.
  - `.add/PROJECT.md` (Key Decisions + the `autonomy:` declaration line) · `.add/state.json` (machine-state file, keys above).
Honors (patterns / conventions):
  - Shared decision "persist only what you gate or audit": autonomy IS gated (verify owner) → persisted in PROJECT.md; parallel scheduling is recomputed → not persisted. A `streams` flag must earn its persistence (it sets concurrency posture + feeds the step-spawn-hint).
  - The throttle is read LIVE from PROJECT.md so the human sees it every session (cmd_status comment ~1476) — a human-readable declaration, not buried machine state.
  - Declaration-line grammar is anchored (never a title/prose substring) with fail-safe defaults (absent→auto, garbled→conservative); a `streams:` token follows the same shape. Engine never spawns; PURE transform + atomic write.
Anchors the contract cites:
  - `_project_autonomy(root)` · `_autonomy_decl_line(text, level)` · `cmd_status` run-mode render block (~1474-1477) · `cmd_waves`/`_schedule`
  - NEW (this task): `_project_streams(root)` (mirrors `_project_autonomy`, in `add_engine/autonomy.py`) · `_streams_decl_line(text, posture)` (mirrors `_autonomy_decl_line`, in `add.py`) · `cmd_streams` + parser · a `cmd_status` run-mode render line · the `streams` enum `parallel | sequential`. **HOME = PROJECT.md declaration (decided), NOT state.json.**
  - BUILD TARGET (engine parity — 3 git-tracked trees, ENGINE_MD5-pinned): edit CANONICAL `add-method/tooling/add.py` + `add-method/tooling/add_engine/autonomy.py`; add tests `add-method/tooling/test_*.py` (mirror `test_autonomy_command.py` · `test_explicit_autonomy_dial.py` · `test_autonomy_reader_anchor.py`); then re-sync the 2 mirrors (`add-method/src/add_method/_bundled/tooling/` + `.add/tooling/`) byte-identical + re-pin `add-method/tooling/engine_pin.py`. The `.add/tooling/*` line refs above are the RUNTIME MIRROR, not the edit target.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Persisted streams posture + combined run-mode surfacing
Framings weighed: PROJECT.md `streams:` declaration mirroring `autonomy:` (chosen) · a `streams` key in state.json · unify both halves into a state.json `run_mode` object
Must:
<must>
  - `add.py streams set <parallel|sequential>` writes/updates a SINGLE `streams:` declaration line in PROJECT.md — idempotent (replace in place, count=1), preserving any trailing comment — via a PURE `_streams_decl_line` + atomic write (mirrors `_autonomy_decl_line`).
  - `_project_streams(root)` resolves the posture from PROJECT.md using the ANCHORED grammar (HTML comments stripped; line-start or `·`-inline; value stops at space/`<`/`#`/`|`) — a title/prose substring is never a declaration.
  - resolution is FAIL-SAFE: absent line -> `parallel` (the documented project default: parallel+auto) · unrecognized token -> `sequential` · unreadable PROJECT.md -> `parallel`.
  - `add.py streams` (show, default) prints the resolved posture; `add.py status` surfaces the COMBINED run mode as one line `run mode: <streams> + <autonomy>` (e.g. `parallel + auto`), read live from PROJECT.md.
  - state.json is NOT written by any streams operation (the posture lives in PROJECT.md, mirroring autonomy; "state.json is untouched").
</must>
Reject:
<reject>
  - `add.py streams set <x>` where x ∉ {parallel, sequential} -> "streams_posture_invalid" (and PROJECT.md is left byte-unchanged)
</reject>
After:
<after>
  - PROJECT.md holds EXACTLY ONE `streams:` line after a set; re-running set replaces it in place (never a second line); the trailing comment survives.
  - `add.py status` shows `run mode: <streams> + <autonomy>`.
  - a project with NO `streams:` line resolves effective `parallel` AND PROJECT.md stays byte-identical until the first set (no silent write on read).
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [spec] absent `streams:` resolves to **parallel** (not sequential) — lowest confidence because it sets the IMPLIED posture for every EXISTING project that never set it; if wrong: `status` reads "parallel" where a human expected "sequential" — harmless to execution (the posture is ADVISORY; the engine never spawns) but surprising. Mitigation: garbled -> sequential; the value is advisory-only, never an auto-trigger.
  - [ ] [contract] streams is PROJECT-scoped ONLY (no per-task `streams:`), unlike autonomy — parallelism is ACROSS tasks, so a per-task posture is meaningless. Confirm.
  - [ ] [contract] NO raise-guard on sequential->parallel (autonomy guards a raise toward `auto`) — parallel is not a trust escalation: it overlaps builds, it drops no human gate. Confirm.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: set the project streams posture
  Given a PROJECT.md with no streams: line
  When I run `add.py streams set sequential`
  Then PROJECT.md gains exactly one `streams: sequential` declaration line
  And state.json is byte-unchanged

Scenario: set is idempotent and preserves the trailing comment
  Given a PROJECT.md whose streams line is `streams: parallel   <!-- run mode -->`
  When I run `add.py streams set sequential`
  Then the line becomes `streams: sequential   <!-- run mode -->` (one line, comment intact)
  And no second streams: line is added

Scenario: status surfaces the combined run mode
  Given a project with `streams: parallel` and project autonomy `auto`
  When I run `add.py status`
  Then the output contains `run mode: parallel + auto`
  And no streams: line is written by the read

Scenario: absent posture resolves to the documented default
  Given a PROJECT.md with no streams: line
  When the engine resolves `_project_streams(root)`
  Then it returns `parallel`
  And PROJECT.md stays byte-identical (no write on read)

Scenario: garbled posture fails safe to sequential
  Given a PROJECT.md whose line is `streams: turbo`
  When the engine resolves `_project_streams(root)`
  Then it returns `sequential`
  And PROJECT.md stays byte-identical

Scenario: an invalid set is rejected
  Given any PROJECT.md
  When I run `add.py streams set turbo`
  Then it exits non-zero with `streams_posture_invalid`
  And PROJECT.md is left byte-unchanged
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
CLI  add.py streams [show | set <parallel|sequential>]
  show (default)        -> stdout: "streams: <posture>"            exit 0   (read-only; no write)
  set <parallel|sequential>
                        -> writes the `streams:` line in PROJECT.md; stdout "project streams -> <posture>"  exit 0
  set <other>           -> stderr "streams_posture_invalid: must be one of parallel|sequential"  exit 2

ENGINE  _project_streams(root: Path) -> "parallel" | "sequential"     # PURE; reads PROJECT.md, fail-safe
        _streams_decl_line(text: str, posture: str) -> str            # PURE; idempotent in-place rewrite/insert
        cmd_status                                                     # adds one line: "run mode: <streams> + <autonomy>"

Schema: PROJECT.md gains ONE `streams: <parallel|sequential>` declaration line (anchored grammar,
        mirrors `autonomy:`). state.json: UNCHANGED — no new key. Default when absent: parallel.
```

Least-sure flag surfaced at freeze: [spec] absent `streams:` resolves to parallel (not sequential) — because it sets the implied posture for every existing project that never set it; if wrong: status reads "parallel" where sequential was expected (harmless — the posture is advisory, the engine never spawns; garbled→sequential mitigates). Human-approved this default at the freeze.
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

Coverage target: the new symbols fully exercised (mirror test_explicit_autonomy_dial coverage)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_streams_set_persists: write a temp PROJECT.md w/o streams / run `streams set sequential` / assert one `streams: sequential` line + state.json unchanged
  - test_streams_set_idempotent_keeps_comment: line w/ trailing comment / set sequential / assert in-place rewrite, comment intact, no 2nd line
  - test_status_shows_combined_run_mode: streams parallel + autonomy auto / run status / assert "run mode: parallel + auto" + no write
  - test_project_streams_absent_defaults_parallel: no line / call _project_streams / assert "parallel" + file byte-identical
  - test_project_streams_garbled_failsafe_sequential: `streams: turbo` / assert "sequential"
  - test_streams_set_invalid_rejected: `streams set turbo` / assert exit!=0 + "streams_posture_invalid" + PROJECT.md unchanged
  - test_streams_reader_anchor: a TITLE/prose substring "streams: parallel" is NOT read as a declaration (mirror test_autonomy_reader_anchor)
</test_plan>

Tests live in: `add-method/tooling/` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/tooling/` `.add/tooling/`   <!-- canonical source + tests + engine_pin · bundled mirror · dogfood mirror — all 3 parity trees the build writes + re-syncs -->
Strategy (ordered batches): 1. add `_streams_decl_line` (PURE, next to `_autonomy_decl_line`) + `_project_streams` (in autonomy.py, next to `_project_autonomy`) · 2. add `cmd_streams` + argparse `streams` subparser · 3. add the `run mode:` line to `cmd_status` · 4. write the 7 red tests · 5. green the build on canonical · 6. re-sync both mirrors byte-identical + re-pin ENGINE_MD5
Known-problem fixes: editing only the canonical tree while a mirror drifts → parity test + ENGINE_MD5 red (re-sync all 3 before verify) · a line-start `streams:` in a comment being read as a declaration → strip HTML comments first (mirror the autonomy anchor) · a silent write on read → resolver is PURE/read-only
Strategy actually used: as planned — mirrored the autonomy seam end-to-end (constants enum → autonomy.py resolvers → add.py decl-line + cmd + status line + parser), wrote 7 red tests, greened canonical, then prepare_bundle + dogfood-sync + re-pin both ENGINE_MD5/ENGINE_PKG_MD5. One mid-build discovery: the new subcommand needed a test_min_pillar lifecycle entry — added it back in the TESTS phase and re-crossed tests→build to re-baseline the tamper snapshot (per the known-problem note).
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
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

- [x] all tests pass — full add-method suite **2294 passed, OK** (incl. the 7 new streams tests)
- [x] coverage did not decrease — net-new code with net-new tests covering every new symbol
- [x] no test or contract was altered during build — §3 frozen untouched; the only test edit (`test_min_pillar` lifecycle entry) was made back in the TESTS phase and tests→build re-crossed to re-baseline the tamper snapshot
- [x] the green was EARNED, not gamed — refute-read below: real CLI invocations + byte-compares, no overfit/vacuous/stub
- [x] concurrency / timing safe — the PROJECT.md write goes through `_atomic_write` (temp+replace), mirroring autonomy; resolver is read-only/PURE
- [x] no exposed secrets, injection openings, or unexpected dependencies — posture is a closed enum, validated; anchored regex; zero new deps
- [x] layering & dependencies follow CONVENTIONS.md — `_project_streams` in autonomy.py (run-mode resolvers), `_streams_decl_line`/`cmd_streams` in add.py, enum in constants.py — exact mirror of the autonomy layering
- [ ] a person reviewed and approved the change — **YOUR gate (conservative)**

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `add.py streams set sequential` then re-reading PROJECT.md shows EXACTLY ONE `streams: sequential` line and state.json is byte-unchanged — confirmed live (dogfood smoke test) + test_streams_set_persists
- [x] `add.py status` prints the line `run mode: parallel + auto` — confirmed live (dogfood status) + test_status_shows_combined_run_mode
- [x] `add.py streams set turbo` exits non-zero with `streams_posture_invalid` and PROJECT.md is byte-unchanged — confirmed live + test_streams_set_invalid_rejected
- [x] a project with no `streams:` line resolves `parallel` and PROJECT.md is byte-identical after a `status` read (no silent write) — confirmed by test_project_streams_absent_defaults_parallel
- [x] all 3 parity trees are byte-identical and ENGINE_MD5 re-pinned; the full add-method suite is green — md5 of all 3 add.py = 3da08586…; ENGINE_MD5/ENGINE_PKG_MD5 re-pinned; test_bundle_parity + test_shared_engine_pin + test_engine_repin_parity green

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_STREAMS_POSTURES` (constants) → imported in autonomy.py + add.py; `_streams_posture`→`_project_streams_token`→`_project_streams` (autonomy.py) → `_project_streams` imported into add.py, used by `cmd_streams` + `cmd_status`; `_streams_decl_line` used by `cmd_streams`; `cmd_streams` registered `func=cmd_streams`. All referenced (grep-confirmed).
- [x] DEAD-CODE (code) — no orphaned symbol; every new name has a caller / registration
- [ ] SEMANTIC (prose / non-code) — n/a (code task; the docs-align task carries the prose)

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self · adversarially checked: probed for (a) overfit — tests use real CLI runs against temp PROJECT.md, not hardcoded fixtures; (b) vacuous asserts — each asserts file content / exit code / output string / state.json byte-equality; (c) stubbed logic — resolver + decl-line + command are real mirrors of the autonomy seam; (d) anchor bypass — the reader-anchor test proves a prose/title `streams:` substring is NOT read as a declaration.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-29

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose PROJECT.md `streams:` declaration mirroring `autonomy:`; rejected a `streams` key in state.json · unify both halves into a state.json `run_mode` object
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned — mirrored the autonomy seam end-to-end (constants enum → autonomy.py resolvers → add.py decl-line + cmd + status line + parser), wrote 7 red tests, greened canonical, then prepare_bundle + dogfood-sync + re-pin both ENGINE_MD5/ENGINE_PKG_MD5. One mid-build discovery: the new subcommand needed a test_min_pillar lifecycle entry — added it back in the TESTS phase and re-crossed tests→build to re-baseline the tamper snapshot (per the known-problem note).
- [human] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
