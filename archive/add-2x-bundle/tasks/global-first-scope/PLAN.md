# TASK: Global-first scope step (recommended, explicit pick)

slug: global-first-scope · created: 2026-06-18 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. -->
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
  - `bin/cli.js:cmdInit(args)` — sets `args.global` from the `--global` flag, then `if (args.global) installGlobal(args, chosenTarget)` runs BEFORE `dropFiles`. The interactive outcome currently carries only {cancelled, target, profile}; the scope step adds `global` to it.
  - `bin/cli.js:runClackPreamble(clack, target, detected)` — the interactive sequence (target text → write-confirm → agent select). The new scope step is a `clack.select` inserted here, AFTER the target confirm, BEFORE the agent select. All steps sit behind the `if (!process.stdin.isTTY) return cancelled` guard.
  - `bin/cli.js:interactive(args)` — returns false for `--yes`/`--non-interactive`/CI/pipes; this is the gate that keeps the scope step (and global) out of non-interactive runs.
  - `bin/cli.js:installGlobal(args, chosenTarget)` / `resolveGlobalHome(env)` / `claudeSkillsDir(env)` — the existing additive global path (writes ~/.add + ~/.claude/skills/add + registry.json). UNCHANGED; the scope step only decides whether to set `args.global`.
  - `src/add_method/_installer.py:install(...)` interactive block — `_render_brand` → readiness → `_prompt_target`. The pip scope prompt is inserted after `_prompt_target`; its result sets the local `as_global` that drives the existing `if as_global:` home block.
  - `src/add_method/_installer.py:_prompt_target(default_path)` — the single-confirm input() prompt the pip scope prompt mirrors (lean UI, parity-enough).
  - `src/add_method/_installer.py:_interactive(yes, non_interactive)` — the pip gate (same role as npm `interactive`).
Context (working folder):
  - `tooling/test_global_install.py` — PINS the opt-in `--global` contract; ALL its cases run NON-interactive (`as_global=True` param / `--yes`). G7 `test_plain_install_untouched_by_global` already pins "no global flag ⇒ home untouched" — the strong regression guard for "CI never auto-global".
  - `tooling/test_installer_prompts.py` — the `ADD_INSTALLER_FORCE_INTERACTIVE` seam + the byte-identical non-interactive boundary (a scope line must NOT appear non-interactively).
  - `tooling/test_readiness_detect.py` / `test_onboarding_brand.py` — the interactive-only + fail-soft render pattern the scope step follows; pip input() is automatable via stdin, npm clack happy-path is PTY/manual.
Honors (patterns / conventions):
  - global is STRICTLY ADDITIVE + OPT-IN (installer-experience FROZEN): `installGlobal` runs before the per-project drop, which always runs; the scope step only flips the opt-in, never the per-project drop.
  - CI/non-interactive NEVER auto-global — the scope step lives ONLY inside the interactive block; the default flag stays opt-in.
  - decision-suggestions convention — the recommended pick is ▶-flagged with a one-line why + a described alternative (guided choice at the gate).
  - twin decision-equivalence; engine add.py untouched (ENGINE_MD5); non-interactive stdout byte-identical.
Anchors the contract cites:
  - the npm scope `clack.select` (recommended=global, why hint) + the `global` field added to runClackPreamble's outcome + `if (outcome.global) args.global = true` in cmdInit.
  - `_prompt_scope(default_global)` (pip) — input() prompt returning the global choice (or CANCEL), mirroring `_prompt_target`; sets `as_global`.
  - a pure `scopeOptions()`/recommended-default seam (npm exported for the node harness) so the recommended choice + why are hermetically testable.
  - G7 `test_plain_install_untouched_by_global` (the "no auto-global non-interactively" pin the change must not break).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: a global-first scope step in the INTERACTIVE installer — recommend "Global home + this project" (▶ default, with a one-line why) but require an explicit pick; CI/non-interactive NEVER auto-go-global.
Framings weighed: a guided scope SELECT inside the interactive block that flips the existing opt-in `--global` (chosen) · make global the DEFAULT everywhere incl. non-interactive (rejected — breaks G7 + surprises CI with ~/.add writes) · a separate `add init --global` only, no interactive step (rejected — global stays discoverable only by flag, defeats "global-first").
Must:
<must>
  - Add an interactive SCOPE step (npm clack.select / pip input()) offering two choices: "Global home + this project" (recommended ▶, with a one-line why: a shared ~/.add + ~/.claude/skills/add reused across every project) and "This project only".
  - The recommended choice is the highlighted default, but the step always RENDERS and the user makes an explicit pick (Enter on the highlighted option counts as the pick); choosing global sets the existing opt-in so `installGlobal`/the `as_global` block runs, THEN the per-project drop still runs (global is strictly additive — unchanged).
  - The scope step runs ONLY on the interactive path (behind `interactive(args)`/`_interactive(...)`); a non-interactive / `--yes` / CI / piped run shows NO scope line and stays project-only (env-only, byte-identical boundary holds).
  - If `--global`/`--global-data` was already passed explicitly, honor it and SKIP the scope prompt (already an explicit choice) — never double-ask.
  - The recommended option + its why are exposed through a pure, hermetically-testable seam (npm export for the node harness; pip a pure helper); both twins are decision-equivalent.
  - A cancel at the scope step writes NOTHING (exit 130 / CANCEL), same as a cancel at the target prompt; engine add.py is never edited (ENGINE_MD5 holds).
</must>
Reject:
<reject>
  - a non-interactive / `--yes` / CI / piped run -> NO scope prompt, project-only; the global home is NOT created -> "noninteractive_never_global"
  - `--global` (or `--global-data`) already passed -> the scope prompt is SKIPPED (honored, not re-asked) -> "explicit_flag_not_reasked"
  - a cancel (EOF / Ctrl-C / clack cancel) at the scope step -> nothing written, exit 130 -> "scope_cancel_writes_nothing"
</reject>
After:
<after>
  - On an interactive run with no `--global`, the user sees the scope step with global recommended + a why; picking global creates ~/.add + ~/.claude/skills/add + registers the project AND drops the per-project files; picking project-only drops only the per-project files (home untouched).
  - A non-interactive run is byte-identical to today: no scope line, project-only unless `--global` was passed.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ "requires an explicit pick" is satisfied by a rendered select whose highlighted default is global (Enter = the pick) — NOT by a free-form re-type. Lowest confidence because "explicit" could mean 'force a non-default keystroke'; if wrong: a user who blind-Enters through prompts gets a global install they didn't deliberate. Mitigation: the why is shown inline, global is strictly additive (no destruction), and the alternative "This project only" is one arrow-key away — matching the decision-suggestions convention already shipped at every other gate.
  - [ ] global stays STRICTLY ADDITIVE — confirm: picking global still runs the per-project drop (installGlobal before drop is already wired); the scope step only flips the opt-in, it never replaces the per-project install.
  - [ ] the pip lean prompt (input() with Enter=recommended) is parity-ENOUGH vs npm's clack.select — confirm: decision-equivalent (same two choices, same default), leaner UI is the accepted §1 parity assumption, not a bug.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: recommended option is global, with a why (pure seam)
  Given the scope-options seam (npm scopeOptions / pip helper)
  When it is queried
  Then the recommended option is the global one, flagged ▶, carrying a one-line why
  And a second "This project only" option is offered

Scenario: interactive pick of global goes additive
  Given an interactive run with no --global flag and an injected hermetic HOME
  When the user picks "Global home + this project" at the scope step
  Then the global home (~/.add + ~/.claude/skills/add + registry.json) is created
  And the per-project drop still runs (the project's .add/ + skill land too)

Scenario: interactive pick of project-only leaves the home untouched
  Given an interactive run with no --global flag and an injected hermetic HOME
  When the user picks "This project only" at the scope step
  Then only the per-project files are dropped
  And the global home is NOT created

Scenario: non-interactive never auto-global  (Reject: noninteractive_never_global)
  Given a --yes / non-interactive / piped run with an injected hermetic HOME
  When init runs
  Then no scope line is shown
  And the global home is NOT created (project-only)

Scenario: explicit --global is honored, not re-asked  (Reject: explicit_flag_not_reasked)
  Given an interactive run invoked WITH --global
  When init runs
  Then the scope prompt is skipped (the flag is the explicit choice)
  And the global home is created (the flag still works as today)

Scenario: cancel at the scope step writes nothing  (Reject: scope_cancel_writes_nothing)
  Given an interactive run at the scope step
  When the user cancels (EOF / Ctrl-C / clack cancel)
  Then nothing is written and the process exits 130
  And neither the global home nor the per-project files are created
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
# npm — bin/cli.js
scopeOptions() -> [ {value:"global", label, hint:<why>, recommended:true},
                    {value:"project", label, hint} ]    # PURE, exported for the node harness
runClackPreamble(clack, target, detected)
  -> { cancelled, target, profile, global:boolean }       # +global field
     scope SELECT runs AFTER target-confirm, BEFORE agent-select; initialValue = "global"
     a clack.isCancel at the scope step -> { cancelled:true }
cmdInit(args):
  if (args.global) -> scope step SKIPPED (explicit flag honored)         # explicit_flag_not_reasked
  else if interactive -> outcome.global picked; if (outcome.global) args.global = true
  # installGlobal(args, target) BEFORE dropFiles is UNCHANGED (additive)

# pip — src/add_method/_installer.py
_scope_options() -> same shape (pure; the recommended/why parity seam)
_prompt_scope(default_global=True) -> True | False | CANCEL              # input(); Enter = recommended (global)
install(...) interactive block:
  after _prompt_target, if NOT already as_global: as_global = _prompt_scope(); CANCEL -> exit 130
  # the existing `if as_global:` home block + the per-project drop are UNCHANGED

INVARIANTS:
  - scope step is INTERACTIVE-ONLY (behind interactive()/_interactive); non-interactive shows no line, stays project-only -> noninteractive_never_global
  - global is STRICTLY ADDITIVE: per-project drop always runs; scope only flips the opt-in
  - cancel writes NOTHING (exit 130) -> scope_cancel_writes_nothing
  - env-only non-interactive boundary byte-identical; add.py untouched (ENGINE_MD5)
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-18
Least-sure flag surfaced at freeze: [spec] "requires an explicit pick" = a rendered select whose highlighted default is global (Enter = the pick), NOT a forced non-default keystroke — chosen for "global-first" with the why shown inline + additive (no destruction) + "This project only" one key away.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + every Reject has a test (8 tests).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_recommends_global_with_a_why (pip) / test_recommends_global (npm): _scope_options()/scopeOptions() — global recommended=True + a hint; project present, not recommended
  - test_pick_global_is_additive: interactive, scope→global / assert home+registry+skill created AND per-project drop still ran (additive)
  - test_pick_project_only_leaves_home_untouched: interactive, scope→project / assert home NOT created + per-project dropped
  - test_cancel_at_scope_writes_nothing: interactive, cancel at scope / assert exit 130 + neither home nor proj/.add written
  - test_noninteractive_never_global: --non-interactive / assert no home + per-project dropped (CI never auto-global)
  - test_explicit_global_flag_skips_scope_prompt: as_global already set / assert only the target prompt runs (scope skipped) + home created
  - test_yes_run_never_creates_home (npm subprocess): `node cli.js init --yes` with injected home / assert no home + no scope line + per-project dropped
</test_plan>
Hermetic seam: pip interactive driven in-process (FORCE seam + monkeypatched input + injected ADD_HOME/HOME); npm via the exported pure seam (node harness) + a `--yes` subprocess; the clack happy-path pick is PTY/manual (established convention).

Tests live in: `add-method/tooling/test_global_scope.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/bin/cli.js` `add-method/src/add_method/_installer.py` `add-method/tooling/test_installer_prompts.py` `add-method/tooling/test_onboarding_brand.py` `add-method/tooling/test_readiness_detect.py`   <the two installer twins + the 3 sibling pip-interactive tests that must feed the new scope step's extra input (navigation only — assertions intact, NOT weakened)>
Strategy (ordered batches): 1. add the pure `scopeOptions`/`_scope_options` seam (recommended=global + why) 2. add the interactive scope step (npm clack.select in runClackPreamble → adds `global` to the outcome; pip `_prompt_scope` after `_prompt_target`) 3. wire the pick into cmdInit/install — skip when `--global` already passed; never on the non-interactive path 4. export the npm seam for the node harness 5. feed the new scope answer (project-only, hermetic) to the 3 sibling pip-interactive tests so they navigate the grown flow.
Safety rule (feature-specific): the scope step is INTERACTIVE-ONLY and global stays STRICTLY ADDITIVE — the per-project drop always runs; a cancel writes nothing (exit 130); the env-only non-interactive boundary stays byte-identical. Sibling-test edits are stdin-navigation ONLY (one extra "n" line) — no assertion changed.
Code lives in: `add-method/bin/cli.js` · `add-method/src/add_method/_installer.py`.
Constraints: do NOT change any test or the contract; no new dependency; add.py is never edited (ENGINE_MD5 holds); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 1308 OK (was 1300; +8 test_global_scope); the 4 sibling pip-interactive tests green after the navigation edit
- [x] coverage did not decrease — +8 tests over the new seam + scope step; G7 (no-auto-global) + the byte-identical boundary still green
- [~] no test or contract was altered during build — THIS task's contract is FROZEN/untouched and its tests (test_global_scope.py) are unchanged since red. DISCLOSED DEVIATION: the new pip scope step adds a 2nd interactive input, so 3 sibling pip-interactive tests (test_installer_prompts happy-path · test_onboarding_brand ×2 · test_readiness_detect) each got ONE extra stdin line ("n" = project-only, hermetic). NAVIGATION ONLY — no assertion changed, no pin weakened (the engine-md5 pin + the non-interactive byte-identical boundary in test_installer_prompts are untouched). Declared in §5; surfaced to the human at the gate.
- [x] the green was EARNED, not gamed — the scope step is exercised by real behavior: additive global creates home+registry+skill AND the per-project drop; project-only leaves the home absent; cancel→130 writes nothing; the npm pure seam is checked via the node harness; --yes never creates a home (subprocess)
- [x] concurrency / timing of the risky operation is safe — no new IO beyond the existing additive global install (already fail-closed on unwritable home / corrupt registry); the scope step is a single synchronous prompt, no shared state
- [x] no exposed secrets, injection openings, or unexpected dependencies — no new dependency; the scope prompt is a fixed-choice select/confirm (no user-path-into-shell); add.py untouched (ENGINE pin holds)
- [x] layering & dependencies follow CONVENTIONS.md — both twins decision-equivalent (npm clack / pip input()); global stays STRICTLY ADDITIVE (per-project drop always runs); design-for-failure: cancel writes nothing (130), caps-aware ASCII fallback on the scope marker
- [x] a person reviewed and approved the change — Tin Dang confirmed PASS at the gate after seeing the exact sibling-test diffs (one stdin line each; pins + assertions intact)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `scopeOptions`/`_scope_options` feed the scope select + are exported (npm)/tested (pip); `_prompt_scope` wired into install()'s interactive block (after _prompt_target, skipped when as_global); npm scope select in runClackPreamble adds `global` to the outcome, honored by cmdInit (`if(outcome.global) args.global=true`) with askScope=!(--global)
- [x] DEAD-CODE (code) — no orphans: every new symbol referenced (seam by the select + tests; _prompt_scope by install; scope field by cmdInit)
- [x] SEMANTIC (prose / non-code) — n/a (code + test-navigation only; no prose/doc edited)

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang (human-confirmed; sibling-test navigation ripple disclosed + diffs shown) · date: 2026-06-18

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
