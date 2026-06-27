# TASK: Interactive npm installer via @clack/prompts + plain-text fallback (pip parity)

slug: installer-prompts · created: 2026-06-17 · stage: mvp
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
  - `add-method/bin/cli.js:main()` — npm entry; parses `argv[0]` as subcommand (default `init`), dispatches `cmdInit`/`cmdUpdate`/help. Where the interactive-vs-plain decision lands.
  - `add-method/bin/cli.js:cmdInit(args)` / `cmdUpdate(args)` — the flows that emit the post-install "Next: …" guidance via `log()`; today fully non-interactive.
  - `add-method/bin/cli.js:parseArgs(argv)` — flag parser (`--force --check --no-skill --stage --name`); a `--yes`/non-interactive flag is added here for CI parity.
  - `add-method/bin/cli.js:log/warn/fail` — the ONLY output sink today (`process.stdout.write`); tests assert on these strings, so interactive UI must route through a layer that degrades to these.
  - `add-method/package.json` — has NO `dependencies` key (zero-dep today); `engines.node ">=18"` (clack needs ≥18 — compatible). `@clack/prompts` is added here.
  - `add-method/src/add_method/_cli.py:main(argv)` — pip CLI twin (argparse); gets the matching non-interactive default + `--yes` flag for parity.
  - `add-method/src/add_method/_installer.py:install()/update()` + `_log/_warn` — pip flow that prints the identical "Next: …" guidance; the plain-text path npm falls back to.
Context (working folder):
  - tests pinning the installer contract: `add-method/tooling/test_installer_handoff.py` (drops-files-only, "Next" guidance), `test_v8_install.py`, `test_update.py` (stamp/clean-replace), `test_packaging.py` (files manifest), `test_shared_engine_pin.py`. New red tests sit alongside these; none may regress.
  - `add-method/package.json:files[]` ships `bin/` already; `dependencies` will be the first non-empty dep set — `npm install`/`npx` resolves it, no bundling needed.
Honors (patterns / conventions):
  - DROPS-FILES-ONLY — never run `add.py init` from the installer (cli.js header; preserves v12 lock-down gate + brownfield signal). Interactivity changes UX only, not this.
  - Designed-for-failure (CLAUDE.md): clack import / TTY probe must degrade to the existing plain-text `log/warn/fail` — never throw on a non-TTY, piped, or CI invocation.
  - npm↔pip parity (PROJECT.md §Domain "twins"): every non-clack behavior identical; pip keeps plain-text, gains the same `--yes` flag + non-interactive default.
Anchors the contract cites:
  - `bin/cli.js:main` + a new interactive gate (`process.stdout.isTTY` && !`--yes`/`--non-interactive` && !`CI`)
  - `bin/cli.js:parseArgs` → `--yes` / `--non-interactive` flag
  - `package.json:dependencies["@clack/prompts"]`
  - `src/add_method/_cli.py:main` → matching `--yes` flag + non-interactive default

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Interactive installer onramp — guided prompts when a real terminal is present, byte-identical plain-text behavior everywhere else, on both the npm and pip twins
Framings weighed: thin UI-abstraction + dynamic-import clack, default-to-plain on any doubt (chosen) · ESM-migrate cli.js + static-import clack (rejected: breaks CJS, pays clack cost in CI) · zero-dep readline-only (rejected: user chose clack in Q2)
Must:
<must>
  - M1 npm: when interactive, `init` renders a clack flow (intro → text(target, default=cwd) → confirm(write?) → drop managed trees → outro with the agent handoff).
  - M2 pip: when interactive, `init` renders a stdlib `input()` flow (confirm target → proceed) — NO new Python dependency.
  - M3 both: when NOT interactive, stdout + exit code + dropped files are byte-identical to today's plain-text init/update (the 5 existing installer tests pass UNCHANGED).
  - M4 interactive iff `stdout.isTTY && stdin.isTTY && !--yes && !--non-interactive && !env.CI` (plus the documented `ADD_INSTALLER_FORCE_INTERACTIVE` test seam).
  - M5 `--yes` and `--non-interactive` are accepted on BOTH runtimes; either forces the non-interactive path (identical outcome to a piped run).
  - M6 npm loads clack lazily via dynamic `import("@clack/prompts")` ONLY on the interactive path — a non-interactive / CI run never imports it (no top-level require).
  - M7 if the clack import fails, npm warns and degrades to the plain-text path, still completing the install (exit 0) — never throws.
  - M8 a cancel (clack isCancel / Ctrl-C / pip KeyboardInterrupt) BEFORE the write step writes NO files and exits as a cancel, not a crash.
  - M9 `@clack/prompts` declared in `package.json:dependencies` (`^1.5.1`); `engines.node>=18` kept; drops-files-only invariant unchanged (installer still never runs `add.py init`).
</must>
Reject:
<reject>
  - the interactive npm path is taken but `import("@clack/prompts")` throws -> "clack_unavailable"  (warn + degrade to plain-text + continue; exit 0 — NOT a hard error)
  - the user aborts at a prompt before the write -> "user_cancelled"  (no files written; cancel exit 130)
  # non-TTY / CI / --yes are NOT rejects — they are the default (plain-text) branch.
</reject>
After:
<after>
  - an interactive init dropped exactly the managed trees a plain init would (skill · tooling · docs), created NO state.json, and additionally showed the guided UX; pip likewise via stdlib prompts.
  - a non-interactive / CI run is unchanged and never imported clack.
  - package.json carries the pinned `@clack/prompts` dep; the 5 installer tests + the full suite stay green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ A1 [contract] Making `cmdInit`/`main` async (required to `await import()` the ESM-only clack 1.5.1) does NOT perturb the stdout ordering or exit codes the piped installer tests assert — lowest confidence because async reordering of writes / `process.exit` is subtle; if wrong: flaky or red existing tests, await-ordering bugs. Mitigation: the non-interactive path stays a straight-line, await-free sequence; tests run piped (non-interactive).
  ⚠ A2 [spec] "pip matching flow" via a single stdlib `input()` confirm is parity ENOUGH (vs a richer Python prompt lib) — lowest confidence because npm's clack UX is visibly richer; if wrong: pip feels thinner. Cost is low — a Python prompt dep is a deferrable follow-up (consistent with the milestone Out-list).
  - [ ] the non-interactive signal = `env.CI` set OR not a TTY (covers GitHub Actions and most CI) — confirm or deny.
  - [ ] pinning `^1.5.1` is safe (clack just reached v1 stable).
  - [ ] a cancel exits 130 (POSIX SIGINT convention) writing nothing — confirm the exit code.
  - [ ] the `ADD_INSTALLER_FORCE_INTERACTIVE` env seam (force the interactive branch in piped tests; `=fail` simulates a clack import failure) is acceptable production surface for designed-for-failure testing.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: Interactive npm init in a real terminal            # M1
  Given a TTY terminal with @clack/prompts installed
  When the user runs `npx @pilotspace/add init` and accepts the prompts
  Then a clack guided flow runs and skill + tooling + docs land under the chosen target
  And no .add/state.json is created (drops-files-only invariant holds)

Scenario: Interactive pip init in a real terminal            # M2
  Given a TTY terminal
  When the user runs `pilotspace-add init` and confirms the target
  Then a stdlib input() flow runs and skill + tooling + docs land
  And no new third-party Python dependency is required

Scenario: Non-interactive run is byte-identical              # M3 (regression pin)
  Given output is piped / not a TTY (the test harness)
  When `init` runs with no flags
  Then stdout, exit code, and dropped files match today's plain-text install exactly
  And the existing installer tests pass unchanged

Scenario: --yes forces the non-interactive path              # M4, M5
  Given a TTY terminal
  When the user runs `init --yes` (or `--non-interactive`) on npm or pip
  Then no prompts are shown and the plain-text install completes (exit 0)
  And the same managed trees are dropped as a piped run

Scenario: clack is lazy-loaded                               # M6
  Given a non-interactive / CI run
  When `init` runs
  Then @clack/prompts is never imported (dynamic import only on the interactive path)
  And the run completes exit 0

Scenario: clack_unavailable degrades gracefully             # M7 / Reject clack_unavailable
  Given the interactive path is taken but import("@clack/prompts") throws
  When `init` runs
  Then a `warn:` line is emitted and the plain-text install completes (exit 0)
  And the managed trees are still dropped (no files lost; not a crash)

Scenario: user_cancelled writes nothing                      # M8 / Reject user_cancelled
  Given the interactive flow is showing a prompt
  When the user cancels (Ctrl-C / clack isCancel / pip KeyboardInterrupt) before confirming the write
  Then a cancel message is shown and the process exits as a cancel (130)
  And no files are written under the target (.claude/ and .add/ untouched)

Scenario: clack dependency is declared and pinned            # M9
  Given the published package.json
  When its dependencies are read
  Then @clack/prompts is present pinned to ^1.5.1
  And engines.node remains ">=18"
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
CLI surface  (commands UNCHANGED; one new flag per twin)
  npm  npx @pilotspace/add [init|update|help] [target]
         [--yes | --non-interactive]  (NEW)  [--force --check --no-skill --stage --name]
  pip  pilotspace-add        [init|update|help] [target]
         [--yes | --non-interactive]  (NEW)  [--force --check]

interactive(args, env, streams) -> bool            # the single gate, both runtimes
  = streams.stdout.isTTY && streams.stdin.isTTY
    && !args.yes && !args.nonInteractive && !env.CI
  test seam: env.ADD_INSTALLER_FORCE_INTERACTIVE in {"1","fail"} forces true,
             still overridden to false by --yes / --non-interactive
  npm only: if the lazy clack import throws -> treated as plain (see clack_unavailable)

cmdInit(args)              # npm: async (awaits the dynamic import)
  interactive == true:
    npm -> p = await import("@clack/prompts")      # lazy; the "fail" seam throws here
           p.intro -> p.text(target, default=cwd) -> p.confirm("write?")
           -> [drop managed trees] -> p.outro(handoff)
    pip -> input() target confirm -> [drop managed trees] -> print(handoff)
    cancel (isCancel / KeyboardInterrupt) BEFORE the drop -> "user_cancelled"
  interactive == false:
    -> EXACT current plain-text init (byte-identical stdout + exit code; managed trees dropped)

errors
  clack_unavailable -> stderr "warn: …" + degrade to plain-text init + exit 0 (files dropped)
  user_cancelled    -> "cancelled" message + exit 130 + NO files written

ui layer (both runtimes): { intro, note, text, confirm, outro, log, warn, fail }
  interactive npm -> clack-backed ; otherwise -> today's plain log/warn/fail (UNCHANGED strings)

package.json
  dependencies += { "@clack/prompts": "^1.5.1" }   # engines.node ">=18" retained

State / schema: NONE — installer is stateless drops-files-only; never reads/writes .add/state.json.
Invariant kept: installer NEVER runs `add.py init` (v12 lock-down + brownfield signal preserved).
```

Least-sure flag surfaced at freeze:
  ⚠ [contract] async `cmdInit`/`main` (forced by ESM-only clack) must not perturb the stdout
     ordering / exit codes the piped tests assert — if wrong, existing installer tests go red.
  ⚠ [spec] pip parity via one stdlib `input()` confirm (not a richer prompt lib) — if wrong, pip UX reads thinner.

Status: FROZEN @ v1 — approved by Tin Dang on 2026-06-17 (open assumptions resolved: CI-or-not-TTY signal · cancel exit 130 · ADD_INSTALLER_FORCE_INTERACTIVE test seam — all adopted)
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: behavior-complete across the 8 scenarios on BOTH twins via subprocess. One honest gap, NOT silently skipped: the npm clack happy-path TUI (M1) needs a real PTY → it is **manual-verified** in a terminal; CI covers its branch reachability via the `fail`/`1` seams + the byte-identical plain path. pip's input() flow IS line-based, so M2 is fully automated.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_noninteractive_byte_identical_{npm,pip}: piped `init`, no flags / act run / assert exit 0 + brain landed + handoff text + NO state.json (M3 regression).
  - test_yes_flag_recognized_{npm,pip}: `init --yes` / assert exit 0 + brain landed + stderr does NOT say "ignoring unknown flag --yes" (M4,M5 — RED today: --yes is an unknown flag now).
  - test_non_interactive_alias_{npm,pip}: `init --non-interactive` / same asserts (M4,M5).
  - test_clack_dependency_declared: read package.json / assert dependencies["@clack/prompts"] == "^1.5.1" AND engines.node == ">=18" (M9 — RED: no deps today).
  - test_clack_lazy_no_toplevel_import: read bin/cli.js / assert NO top-level `require("@clack/prompts")` or static `import … "@clack/prompts"` AND a dynamic `import(` IS present (M6 — RED: no dynamic import today).
  - test_clack_unavailable_falls_back_npm: env ADD_INSTALLER_FORCE_INTERACTIVE=fail / assert exit 0 + brain landed + a stderr warn mentioning clack/interactive fallback (M7, clack_unavailable — RED: seam ignored today, no warn).
  - test_user_cancelled_writes_nothing_{npm,pip}: env ADD_INSTALLER_FORCE_INTERACTIVE=1 + empty/closed stdin / assert exit 130 + NEITHER .claude/ NOR .add/ written (M8, user_cancelled — RED: exits 0 + writes files today).
  - test_pip_interactive_happy_path: env=1 + stdin "\n" (accept default target) / assert exit 0 + a target prompt shown in output + brain landed (M2 — RED: no prompt today).
  - test_engine_untouched: md5-pin add.py across the 3 copies (parity with test_installer_handoff — build must not touch the engine).
</test_plan>

Tests live in: `add-method/tooling/test_installer_prompts.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/bin/cli.js` `add-method/package.json` `add-method/src/add_method/_cli.py` `add-method/src/add_method/_installer.py` `add-method/tooling/test_installer_prompts.py`
  (generated, not hand-edited: `add-method/package-lock.json` may appear from `npm install`.)
Strategy (ordered batches): 1. add `--yes`/`--non-interactive` to both CLIs + the `interactive()` gate (no clack yet) → 2. extract the `ui` layer so plain-text strings are unchanged → 3. wire the lazy `await import` clack flow on npm + `clack_unavailable`/`user_cancelled` paths → 4. add the stdlib pip interactive confirm → 5. declare the dep in package.json + `npm install`.
Safety rule (feature-specific): the non-interactive path stays a straight-line, await-free sequence emitting today's exact strings — the interactive layer is strictly additive and default-off; nothing is written to the target before the confirm step.
Code lives in: `add-method/` (the package — NOT this task's `./src/`).
Constraints: do NOT change any test or the contract; allow-list packages only (`@clack/prompts`); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — new suite 13/13 green; full suite 1213 green (was ~1152; +13 here, no regressions).
- [x] coverage did not decrease — only added a test file + additive code; nothing removed.
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; the §4 red tests were not edited to pass (the implementation made the UNCHANGED suite go green).
- [x] the green was EARNED — adversarial refute-read: tests assert real on-disk effects (files dropped / NOT dropped), real exit codes (0 vs 130), flag recognition (no "ignoring unknown flag"), the declared dep, and a real dynamic `import(`. The two fault-injection seams (`fail`, forced-interactive) are CONTRACTED, not stubs that delete logic; the npm clack happy path was verified END-TO-END via a real pseudo-terminal (exit 0 · brain landed · no state.json · clack UI rendered) — the contract's one manual-verify gap is CLOSED, not skipped.
- [x] concurrency / timing safe — the only new async is the interactive path's `await import()` + sequential prompts (no shared state, no races); the non-interactive path stays a straight-line, await-free sequence; `process.exit(130)` on cancel fires BEFORE any write, so a cancel can never leave a partial tree.
- [x] no exposed secrets / injection / UNEXPECTED dependencies — the one new dependency (`@clack/prompts ^1.5.1`, +5 transitive: @clack/core · sisteransi · fast-string-width · fast-wrap-ansi · fast-string-truncated-width — pure-JS terminal-UI utils, no native code/install hooks) was EXPECTED: chosen at intake Q2 and frozen in §3. pip deps unchanged (`[]`). No secrets; no shell/eval; target paths are `path.resolve`/`Path.resolve`d.
- [x] layering & dependencies follow conventions — npm↔pip parity held (same flags, same gate semantics, byte-identical plain path); the installer still DROPS-FILES-ONLY (never runs `add.py init`); engine md5-pin intact (test_engine_untouched green).
- [x] a person reviewed and approved the change — human chose "independent review → PASS"; a fresh subagent ran an adversarial pre-merge review (verdict **MERGE-WITH-NITS · 0 BLOCK**), confirming the green is earned + the frozen contract honored. All 4 nits closed as a disclosed strengthening amendment: (1) guarded the cancel-message stdout write against EPIPE before `exit(130)`; (2+3) added single-quote require/import guards + a `--yes`-beats-the-seam test on both twins; (4) commented the deliberate pip single-confirm (A2). Suite re-run 15/15 + 1215 full, green.

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — every new symbol is referenced: `interactive`/`loadClack`/`runClackPreamble`/`dropFiles` all called from `cmdInit`; `cmdInit` awaited in `main`; `--yes`/`--non-interactive` parsed in `parseArgs` and read by `interactive`; pip `_interactive`/`_prompt_target`/`CANCEL` used in `install()`; `yes`/`non_interactive` flow `_cli.py → install()`.
- [x] DEAD-CODE (code) — no orphaned symbol: the `dropFiles` refactor reuses the old inline body (no duplication); `CANCEL` sentinel is produced + consumed; no unused import (added only `os` in _installer, used by `_interactive`).
- [x] SEMANTIC (prose) — read the cli.js header in full and CORRECTED its stale "Zero npm dependencies" claim to describe the one lazy optional dep; confirmed README/GETTING-STARTED/docs carry no zero-dep claim that the change falsifies (grep clean).

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (authorized "independent review → PASS") + adversarial subagent pre-merge review (MERGE-WITH-NITS, 0 blocking, nits closed) · date: 2026-06-17

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): clack import failure rate (clack_unavailable warns) · cancel rate (exit 130) · any "ignoring unknown flag" regression on --yes/--non-interactive.

### Spec delta
- [SPEC · seeded] the agent-detect prompt is a STEP in this interactive flow — render it through the established npm `ui` layer / clack flow, not a separate prompt stack (evidence: §3 ui layer + the milestone decomposition; agent-detect depends conceptually on this shell) [→ agent-detect]
- [SPEC · carried] give pip a richer interactive prompt lib (e.g. questionary/rich) for true parity with npm's two-step clack flow — deferred per A2 / milestone Out-list (evidence: pip is a single stdlib input() confirm by deliberate choice). [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]
- [SPEC · carried] extract a reusable PTY test helper so interactive happy-paths are automatable in CI (agent-detect/heal will need it too) (evidence: M1 was verified by an ad-hoc pty probe, not a committed test). [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]

### Competency deltas
- [ADD · folded] an ESM-only dep forces a CJS installer to dynamic-import() + go async; keep the non-interactive path await-free so exit-code/stdout ordering the piped tests assert is preserved (evidence: A1 flag held; clack 1.x is type:module; full suite stayed green after the async refactor). [folded foundation-version 38]
- [TDD · folded] interactive TUI flows aren't feedable via piped stdin (clack raw-mode); test branch-reachability via a CONTRACTED force seam ({"1","fail"}) + the happy path via a PTY probe — the seam is fault-injection, not a logic-deleting stub (evidence: earned-green refute-read passed; pty probe closed the M1 gap). [folded foundation-version 38]
- [SDD · folded] a new runtime dependency falsifies any "zero-dep" prose; grep + fix the claim in the SAME change (evidence: cli.js header corrected from "Zero npm dependencies"; README/GETTING-STARTED/docs grepped clean). [folded foundation-version 38]
