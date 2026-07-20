# TASK: Logo + feature showcase (interactive-only, byte-identical boundary)

slug: onboarding-brand · created: 2026-06-18 · stage: mvp
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
  - `bin/cli.js:runClackPreamble(clack, target, detected)` — the interactive clack flow; today `clack.intro("ADD — AI-Driven Development")` then text(target)→confirm(write)→select(agent). The logo + feature showcase render HERE (interactive path only).
  - `bin/cli.js:interactive(args)` — the gate (TTY && stdin.isTTY && !CI && !--yes/-non-interactive, + the ADD_INSTALLER_FORCE_INTERACTIVE seam). Everything the byte-identical boundary protects is the path where this returns false.
  - `bin/cli.js:loadClack()` — dynamic import() seam; the logo must NOT move clack to a top-level require (ClackLazyImportTest pins this).
  - `bin/cli.js:dropFiles(args,target,profile)` + `log/warn` — the plain-path `log()` handoff lines that MUST stay byte-identical on the non-interactive path.
  - `src/add_method/_installer.py:_prompt_target(default_path)` — pip's single input() confirm; the twin entry where a condensed banner renders.
  - `src/add_method/_installer.py:_interactive(yes, non_interactive)` — pip's interactive gate (parity with cli.js:interactive).
  - `src/add_method/_installer.py:install(...)` + `_log()` — pip flow; the `_log` lines are the byte-identical plain output.
Context (working folder):
  - `tooling/test_installer_prompts.py` — the pins: `test_noninteractive_byte_identical_{npm,pip}` (the boundary), `ClackLazyImportTest` (no top-level clack), `EnginePinTest`/`ENGINE_PATHS` (md5), and the `ADD_INSTALLER_FORCE_INTERACTIVE` seam ("1"=force, "fail"=force+import-throws). New tests for this task live alongside.
  - `tooling/engine_pin.py:ENGINE_MD5` — the add.py md5 the EnginePinTest asserts (installer never edits the engine).
  - `.add/PROJECT.md` — SOURCE OF TRUTH for the faithful feature-showcase lines + the 7-step Specify→Observe loop (lines are grounded here, never invented marketing).
  - `package.json` — `@clack/prompts ^1.5.1`, `engines.node ">=18"` (no new dependency allowed).
Honors (patterns / conventions):
  - Design-for-failure (CLAUDE.md critical rule + installer header) — logo/showcase are fail-soft: non-TTY, no-unicode/no-color, and narrow terminals degrade to a plain rendering; never throw.
  - Twin parity — bin/cli.js ↔ src/add_method/_installer.py stay decision-equivalent (rendering may differ: clack vs stdlib input()).
  - Byte-identical-non-interactive invariant — the installer-prompts FROZEN contract; new output rides the interactive path only.
  - Lazy clack — no top-level import (ClackLazyImportTest).
Anchors the contract cites:
  - `bin/cli.js:runClackPreamble` (npm render point) · `bin/cli.js:interactive` (the interactive-only boundary)
  - `src/add_method/_installer.py:_prompt_target` / `install` (pip render point) · `_installer.py:_interactive` (boundary)
  - `tooling/test_installer_prompts.py:test_noninteractive_byte_identical_{npm,pip}` (the pin the contract must not break)

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Branded onboarding — ADD logo + feature showcase on the interactive installer path.
Framings weighed: brand+showcase rides the INTERACTIVE path only (chosen) · show a plain banner on every path incl. non-interactive (rejected — breaks the byte-identical pin) · ship logo now, showcase later (rejected — user asked for the fuller showcase together).
Must:
<must>
  - On a real interactive TTY (interactive()/_interactive() == true) render an ADD logo banner + a feature showcase (a short value line + the 7-step Specify→Scenarios→Contract→Tests→Build→Verify→Observe loop) BEFORE the first prompt.
  - The render is fail-soft: a no-unicode / no-color / narrow (< ~40 col) terminal degrades to a plain-ASCII rendering of the same brand+showcase; it never throws and never aborts the install.
  - The non-interactive / CI / --yes / piped path stays BYTE-IDENTICAL to today (no banner, no showcase) — the frozen boundary holds.
  - Feature-showcase lines are sourced from PROJECT.md / the book (faithful to the method), never invented marketing.
  - Both twins render the same DECISIONS; pip may show a CONDENSED banner (stdlib input() can't do a rich panel), npm the fuller clack panel — twin-decision-equivalent, not byte-equal output.
  - clack stays lazy-imported (no top-level require); the engine add.py is never edited (ENGINE_MD5 pin holds).
</must>
Reject:
<reject>
  - non-TTY / CI / --yes / piped invocation -> render NOTHING new (the plain path is suppressed-by-design, not an error) -> "byte_identical_path"
  - clack import fails on the interactive path -> fall back to plain text (existing clack_unavailable path), no banner, install still completes -> "clack_unavailable"
  - unicode/encoding error while rendering the banner -> degrade to plain ASCII, never crash the install -> "render_degraded"
</reject>
After:
<after>
  - An interactive run shows brand + showcase, then proceeds to the existing target/agent prompts; the install completes exactly as before.
  - A non-interactive run is unchanged — byte-for-byte identical stdout to the pre-task baseline.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ The "plain fallback" lives INSIDE the interactive path only — a non-interactive run shows NOTHING new. Lowest confidence because "plain-text fallback for non-unicode/CI" could be misread as 'print a plain banner even on the non-interactive path'; if wrong: breaks test_noninteractive_byte_identical_{npm,pip} and re-opens a frozen pin (rework + a change-request).
  - [x] The logo WORDMARK CONTENT is a human identity decision (asked OPEN this phase) — RESOLVED: the human delegated ("continue") a swappable DEFAULT: an ANSI-Shadow "ADD" block banner + "AI-Driven Development" subtitle + NO forced color (degrades to plain `ADD — AI-Driven Development`). The spec pins the SLOT + fail-soft behavior, not the glyphs; this default drops into the slot and the human can swap glyphs/tagline/accent later WITHOUT a contract change (no rule above references the exact content).
  - [ ] "Fuller showcase" on pip = a condensed banner (input() has no rich-panel surface) — twins stay decision-equivalent, not byte-equal output.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: interactive run renders brand + showcase
  Given a real interactive TTY (interactive()/_interactive() == true; not CI, not --yes, stdin is a TTY)
  When the installer starts
  Then an ADD logo banner + a feature showcase (a value line + the 7-step Specify→Scenarios→Contract→Tests→Build→Verify→Observe loop) renders before the first prompt
  And the existing target/agent prompts and the install outcome are unchanged

Scenario: non-interactive run is byte-identical
  Given a non-interactive invocation (CI / --yes / -non-interactive / piped stdin / non-TTY)
  When the installer runs
  Then stdout is byte-for-byte identical to the pre-task baseline — no banner, no showcase
  And test_noninteractive_byte_identical_{npm,pip} stay green   # byte_identical_path

Scenario: degraded terminal still shows the brand in plain ASCII
  Given an interactive TTY with no-unicode OR no-color OR width < ~40 columns
  When the brand + showcase renders
  Then it degrades to a plain-ASCII rendering of the SAME brand + showcase
  And the install completes — the render never throws and never aborts the install   # render_degraded

Scenario: clack unavailable on the interactive path falls back to plain text
  Given an interactive TTY where the lazy clack import throws (ADD_INSTALLER_FORCE_INTERACTIVE=fail)
  When the installer starts
  Then it falls back to the existing plain-text path with no banner
  And the install still completes   # clack_unavailable

Scenario: feature lines are faithful to PROJECT.md
  Given the rendered feature showcase
  When each feature line and loop-step label is compared to PROJECT.md / the book
  Then every line is grounded there — no invented marketing copy
  And the 7 loop steps match the method's phase names

Scenario: twins render the same decisions; engine + lazy-clack seams hold
  Given both bin/cli.js and src/add_method/_installer.py on an interactive TTY
  When each renders the brand + showcase
  Then both show the same DECISIONS (banner + value line + 7-step loop), pip condensed / npm fuller — decision-equivalent
  And clack stays lazy-imported (no top-level require) and add.py md5 (ENGINE_MD5) is unchanged
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
renderBrand(interactive: bool, caps: {unicode, color, width}) -> writes to stdout, returns void (never throws)
  interactive == false                 -> NO-OP: writes NOTHING (the frozen non-interactive byte stream is unchanged)   # byte_identical_path
  interactive == true,  caps full      -> rich brand banner + value line + 7-step loop (clack panel on npm · condensed on pip)
  interactive == true,  caps degraded  -> plain-ASCII rendering of the SAME content (no-unicode | no-color | width < ~40)  # render_degraded
  clack import throws (npm only)        -> existing plain-text fallback path, no banner; install continues               # clack_unavailable
  ANY render exception                  -> swallowed; fall through to the prompts; install never aborts                   # render_degraded

Boundary (FROZEN): renderBrand emits output ONLY when interactive()/_interactive() == true. The
  non-interactive stdout byte-stream is unchanged from the pre-task baseline (the installer-prompts pin).
Seams (unchanged): bin/cli.js:interactive() · loadClack() lazy import · _installer.py:_interactive() ·
  ENGINE_MD5 (add.py untouched) · ADD_INSTALLER_FORCE_INTERACTIVE ("1"=force, "fail"=force+import-throws).
Twin rule: bin/cli.js ↔ _installer.py are DECISION-equivalent (same banner/value/loop content), rendering surface differs (clack vs stdlib).
Source of truth: every feature line + the 7 loop-step labels are derived from PROJECT.md (goal + the 8-phase flow, showcasing the 7 post-ground steps) — no invented copy.
Content slot (SWAPPABLE, not frozen): the exact wordmark glyphs · tagline text · accent color. Default = ANSI-Shadow "ADD" + "AI-Driven Development" + no forced color; the human may swap these later without a contract change.
```

Status: FROZEN @ v1 — approved by Tin Dang
Least-sure flag surfaced at freeze: [spec] the plain fallback lives INSIDE the interactive path only — a non-interactive run shows NOTHING new (renderBrand is a NO-OP when interactive==false); if misread as "print a plain banner on the non-interactive path" it breaks the byte-identical pin and re-opens a frozen contract. Mitigated: the contract states `interactive == false -> NO-OP` explicitly and test_noninteractive_byte_identical_{npm,pip} pin the byte stream.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: ≥1 behavioral test per scenario; the existing test_installer_prompts pins stay green (no regression).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_interactive_renders_brand_and_showcase_{npm,pip}: arrange force-interactive (ADD_INSTALLER_FORCE_INTERACTIVE=1, piped) / act run installer / assert stdout has the ADD banner + value line + all 7 loop-step labels, BEFORE the first prompt
  - test_noninteractive_still_byte_identical_{npm,pip}: arrange non-interactive (CI/--yes/pipe) / act run / assert stdout byte-for-byte == pre-task baseline (no banner) — the frozen boundary
  - test_degraded_terminal_plain_ascii_{npm,pip}: arrange force-interactive + NO_COLOR / no-unicode / COLUMNS<40 / act run / assert plain-ASCII same brand+showcase appears AND exit code 0 (never throws)
  - test_clack_unavailable_falls_back_npm: arrange ADD_INSTALLER_FORCE_INTERACTIVE=fail / act run / assert no banner + install completes (clack_unavailable path)
  - test_feature_lines_grounded_in_project_md: arrange read PROJECT.md / act extract showcase lines from the source / assert every line + the 7 loop labels are grounded (subset of method phase names), none invented
  - test_twins_decision_equivalent + test_engine_md5_unchanged + test_clack_stays_lazy: assert both twins emit the same banner/value/loop DECISIONS · add.py md5 == ENGINE_MD5 · no top-level clack import (ClackLazyImportTest holds)
</test_plan>

Tests live in: `add-method/tooling/test_onboarding_brand.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/bin/cli.js` `add-method/src/add_method/_installer.py`   <the two installer twins — npm + pip; no parity-tree copies, this is package code, not skill/template/doc>
Strategy (ordered batches): 1. add a fail-soft `renderBrand` to `bin/cli.js` (interactive path only, lazy-clack, try/catch→fall-through) + source the feature/loop lines from PROJECT.md 2. twin it in `_installer.py` (condensed banner via stdlib, same decisions) 3. confirm the non-interactive byte stream is untouched on both.
Safety rule (feature-specific): `renderBrand` emits ONLY when `interactive()`/`_interactive()` == true; the whole render is wrapped so ANY exception is swallowed and falls through to the prompts — it NEVER aborts the install; the non-interactive stdout byte-stream stays byte-identical.
Code lives in: `add-method/bin/cli.js` · `add-method/src/add_method/_installer.py`.
Constraints: do NOT change any test or the contract; no new dependency (clack already present, lazy); add.py is never edited (ENGINE_MD5 holds); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 1286 green (+10 new test_onboarding_brand)
- [x] coverage did not decrease — added 10 behavioral/structural tests; removed none
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; only the 2 declared twins edited
- [x] the green was EARNED, not gamed — tests assert REAL subprocess output (showcase markers in stdout), the byte-identical boundary, source wiring, AND faithfulness (loop labels == engine phases); 4 RED before build, a no-op render fails them
- [x] concurrency / timing of the risky operation is safe — N/A (synchronous, single-shot banner render before the prompt)
- [x] no exposed secrets, injection openings, or unexpected dependencies — no new dep (clack already present + still lazy); plain stdout writes only; no user input echoed
- [x] layering & dependencies follow CONVENTIONS.md — byte-identical boundary held · lazy-clack held · ENGINE_MD5 unchanged (engine never edited)
- [x] a person reviewed and approved the change — AUTO-RESOLVED (autonomy: auto, no residue): the run is the accountable owner; the human approved the freeze + delegated the build ("continue")

### Build expectations — what "correct" looks like (confirmed at this gate)
- [x] an interactive run renders the ADD banner + value line + the 7-step loop BEFORE the first prompt — confirmed by the live smoke render + test_pip_interactive_renders_brand_and_showcase
- [x] a non-interactive / CI run shows NO showcase (byte stream unchanged) — confirmed by test_{pip,npm}_noninteractive_has_no_showcase + the existing byte-identical pins still green
- [x] fail-soft holds: a failed clack import AND a degraded (NO_COLOR / narrow) terminal still complete the install — confirmed by test_npm_clack_unavailable + test_pip_no_color_narrow_still_shows_plain_brand (exit 0, plain ASCII, no ANSI)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `renderBrand` is called at `runClackPreamble` (cli.js) and `_render_brand` in the `_interactive` block of `install()` (_installer.py); both reachable ONLY on the interactive path. Confirmed by grep + the passing interactive test + the live smoke run.
- [x] DEAD-CODE (code) — no orphans: `brandLines`/`terminalCaps` (npm) and `_brand_lines`/`_terminal_caps` (pip) are each called only by `renderBrand`/`_render_brand`, which the interactive paths call.
- [ ] SEMANTIC (prose / non-code) — N/A (code change; faithfulness of the showcase prose is pinned by test_loop_steps_are_the_real_post_ground_phases)

### GATE RECORD
Outcome: PASS
Reviewed by: auto-resolved (onboarding-brand run; human froze the contract + delegated the build) · date: 2026-06-18

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
