# TASK: Readiness pre-flight + smarter agent detection

slug: readiness-and-detect · created: 2026-06-18 · stage: mvp
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
  - `bin/cli.js:detectAgent(env)` + `profileMatches(profile, env)` + `AGENT_PROFILES` — TODAY's env-only detector (CLAUDECODE/CODEX_*/OPENCODE). KEEP UNCHANGED (test_agent_detect pins it); a NEW enriched layer wraps it.
  - `bin/cli.js:cmdInit(args)` — sets `profile = detectAgent(env)` then overrides via the clack select. The ENRICHED default feeds the select's initialValue (interactive only).
  - `bin/cli.js:runClackPreamble` / `renderBrand` — the interactive render point; the readiness pre-flight line renders here, after the banner.
  - `src/add_method/_installer.py:_detect_agent(env)` + `AGENT_PROFILES` — the pip env-only twin (hermetic: takes an explicit env dict). KEEP UNCHANGED.
  - `src/add_method/_installer.py:install(...)` interactive block + `_render_brand` — pip's interactive render point for the readiness line.
Context (working folder):
  - `tooling/test_agent_detect.py` — PINS `_detect_agent({})` == generic + env-only determinism. The enriched layer must NOT change `_detect_agent(env)`; it is a SEPARATE function.
  - `tooling/test_installer_prompts.py` — the byte-identical non-interactive pin + the `ADD_INSTALLER_FORCE_INTERACTIVE` seam.
  - `tooling/test_onboarding_brand.py` — the interactive-only / fail-soft pattern the readiness line follows.
  - the dev machine has `claude` on PATH — so any installed-CLI probe MUST be injectable (`which` seam) or it leaks into hermetic tests.
Honors (patterns / conventions):
  - env-only `_detect_agent(env)` / `detectAgent(env)` is FROZEN behavior (test_agent_detect) — enrichment is additive, never a rewrite.
  - byte-identical non-interactive boundary (onboarding-brand FROZEN) — the readiness line + enriched default are INTERACTIVE-ONLY; the non-interactive write keeps env-only detection.
  - design-for-failure — every probe (which git/python3/agent-CLI, file existence) is fail-soft: PATH lookup only (no blocking subprocess), never throws, never hangs; absent → "–"/generic.
  - twin decision-equivalence; engine add.py untouched (ENGINE_MD5).
Anchors the contract cites:
  - `detectAgentEnriched(env, target, which)` (npm) / `_detect_agent_enriched(env, target, which)` (pip) — the new additive detector.
  - the readiness-line renderer (interactive only) + the clack select `initialValue` (enriched default, user overrides).
  - `tooling/test_agent_detect.py:test_unknown_falls_back_to_generic` (the env-only pin the enrichment must not break).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: smarter agent detection (env > integration-file > installed-CLI) for the interactive default + a readiness pre-flight line (git · python3 · agent), interactive-only.
Framings weighed: an ADDITIVE enriched detector wrapping the env-only one, used for the interactive default only (chosen) · rewrite detectAgent to fold in file/CLI everywhere (rejected — breaks test_agent_detect + changes the non-interactive write by machine state) · run agent CLIs to detect (rejected — slow/hangs; PATH lookup only).
Must:
<must>
  - Add an ENRICHED detector (`detectAgentEnriched`/`_detect_agent_enriched`(env, target, which)): env match → that agent (== the env-only result, authoritative) · else CLAUDE.md in target → claude · else `which` finds an agent CLI → that agent · else generic. PURE + never throws.
  - The env-only `detectAgent(env)`/`_detect_agent(env)` is UNCHANGED; the NON-interactive write keeps using it (byte-identical boundary + test_agent_detect stay green). The enriched default is used ONLY to seed the interactive agent select (the user still overrides).
  - Render a readiness pre-flight line on the INTERACTIVE path only (after the banner): `git <✓|–> · python3 <✓|–> · agent: <label>`, where ✓/– come from a fail-soft PATH probe.
  - Every probe (which git/python3/agent-CLI · CLAUDE.md existence) is fail-soft: PATH/file lookup only (no blocking subprocess), never throws, never hangs; a failure reads as absent/generic.
  - The installed-CLI probe is INJECTABLE (a `which` parameter, default the stdlib resolver) so hermetic tests are not polluted by the dev machine's installed agents.
  - Both twins are decision-equivalent; the non-interactive stdout stays byte-identical (no readiness line); the engine add.py is never edited (ENGINE_MD5 holds).
</must>
Reject:
<reject>
  - a probe binary missing / PATH unreadable / file unreadable -> read as ABSENT, never an error -> "probe_degraded"
  - the integration file is AGENTS.md (shared by codex/opencode/generic) -> it does NOT pick a specific agent; fall through to the CLI/generic step -> "ambiguous_integration_file"
  - enriched detection or the readiness line applied on the NON-interactive path -> NOT applied (env-only + no line there) -> "noninteractive_unchanged"
</reject>
After:
<after>
  - On an interactive run with no agent env but a CLAUDE.md in the target (or `claude` on PATH), the agent select defaults to Claude Code; the user can still override; the readiness line shows git/python3/agent.
  - A non-interactive run is byte-identical to today: env-only detection, no readiness line.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ The enriched default must NOT change the NON-interactive write — only the interactive select default. Lowest confidence because "smarter detection" could be read as 'detect harder everywhere'; if wrong: a machine with `claude` installed silently writes CLAUDE.md on every `--yes` install + breaks test_agent_detect's `_detect_agent({})==generic` pin. Mitigation: the env-only detector is untouched; enrichment is a separate function wired ONLY into the interactive select.
  - [ ] PATH-lookup (not running the CLI) is enough signal for "installed agent" — confirm: `shutil.which`/a PATH walk is synchronous, safe, and sufficient; running the agent would hang/slow the installer.
  - [ ] git + python3 are the right two readiness checks — confirm: python3 runs the engine (`python3 .add/tooling/add.py`), git is assumed by the loop; both are the real prerequisites, agent is informational.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: env signal wins (authoritative)
  Given CLAUDECODE is set AND the target has an AGENTS.md AND codex is on PATH
  When the enriched detector runs
  Then it returns the claude profile (env beats file and CLI)
  And detectAgent(env) (env-only) returns the same profile — unchanged

Scenario: integration-file signal with no env
  Given no agent env AND the target contains CLAUDE.md
  When the enriched detector runs
  Then it returns the claude profile (the repo's CLAUDE.md is the signal)
  And the env-only detectAgent(env) still returns generic — unchanged

Scenario: installed-CLI signal with no env and no file
  Given no agent env AND no integration file AND a `which` that resolves "codex"
  When the enriched detector runs
  Then it returns the codex profile
  And nothing was executed — only a PATH lookup was performed

Scenario: nothing detected falls back to generic
  Given no agent env, no integration file, and a `which` that resolves nothing
  When the enriched detector runs
  Then it returns generic
  And the call never throws

Scenario: env-only detector is unchanged (the pin holds)
  Given an empty env
  When detectAgent({}) / _detect_agent({}) runs
  Then it returns generic (test_agent_detect stays green)
  And no target or PATH was consulted

Scenario: readiness line on the interactive path
  Given a forced-interactive run
  When the installer starts
  Then a pre-flight line shows git, python3, and the detected agent, after the banner
  And the install proceeds to the prompts

Scenario: readiness line + enriched default are interactive-only
  Given a non-interactive run (CI / --yes / pipe)
  When the installer runs
  Then NO readiness line is printed and the agent write uses env-only detection
  And the non-interactive stdout stays byte-identical (the boundary holds)

Scenario: a probe never crashes the install
  Given a probe (which/file) that raises
  When the readiness line / enriched detector runs
  Then the failing signal reads as absent ("–" / generic)
  And the install still completes
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
detectAgentEnriched(env, target, which = <stdlib PATH resolver>) -> profile   (pure; never throws)
  env match (CLAUDECODE | CODEX_* | OPENCODE)  -> that profile     # == detectAgent(env), authoritative
  else CLAUDE.md exists in target              -> claude           # repo signal (AGENTS.md is ambiguous -> skip)
  else which("claude"|"codex"|"opencode") hit  -> that profile     # machine signal; PATH lookup only, injectable
  else                                         -> generic
_detect_agent_enriched(env, target, which=shutil.which) -> profile   # pip twin, same decisions

readinessLine(env, target, which) -> "Pre-flight: git <✓|–> · python3 <✓|–> · agent: <label>"
  rendered ONLY on the interactive path, AFTER the banner; each field a fail-soft probe (✓ present / – absent)

INVARIANT (unchanged): detectAgent(env) / _detect_agent(env) stay ENV-ONLY and pure — the NON-interactive
  write path uses them as today (byte-identical boundary + test_agent_detect hold). Enriched detection + the
  readiness line are wired ONLY into the interactive flow (the clack select initialValue / the preamble).
Fail-soft: every probe is a PATH/file lookup (NO process spawn); any error reads as absent/generic.
Seams unchanged: interactive() · ENGINE_MD5 (add.py untouched) · the clack agent select (user overrides the default).
```

Status: FROZEN @ v1 — approved by Tin Dang
Least-sure flag surfaced at freeze: [spec] the enriched default must NOT change the non-interactive write — only the interactive select default; if folded in everywhere, a machine with `claude` on PATH silently writes CLAUDE.md on every `--yes` install and breaks test_agent_detect's `_detect_agent({})==generic` pin. Mitigated: the env-only detector is untouched and the non-interactive write keeps using it; enrichment + the readiness line are wired ONLY into the interactive flow.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: ≥1 behavioral test per scenario; test_agent_detect + test_installer_prompts pins stay green.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_enriched_env_wins: env=CLAUDECODE + target has AGENTS.md + which→codex / assert enriched==claude
  - test_enriched_file_signal: no env + target has CLAUDE.md / assert enriched==claude AND _detect_agent({})==generic
  - test_enriched_cli_signal: no env, no file, which→"codex" / assert enriched==codex (no spawn — which is the injected fake)
  - test_enriched_generic_fallback: no env/file, which→None / assert enriched==generic AND never raises
  - test_env_only_detector_unchanged: _detect_agent({}) / detectAgent({}) == generic (the test_agent_detect pin re-asserted here)
  - test_readiness_line_fields: build the line with fakes / assert it names git, python3, and the agent label
  - test_readiness_line_interactive_only_{pip,npm}: force-interactive run shows the line; non-interactive run does NOT (byte-identical)
  - test_noninteractive_write_uses_env_only: a target with CLAUDE.md + --yes (no env) still writes via env-only detection (generic→AGENTS.md), not enriched
  - test_probe_failure_is_absent: a which/file probe that raises / assert "–"/generic and exit 0
  - test_engine_md5_unchanged + twin decision-equivalence (both detectors agree on the same inputs)
</test_plan>

Tests live in: `add-method/tooling/test_readiness_detect.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/bin/cli.js` `add-method/src/add_method/_installer.py`   <the two installer twins — npm + pip; package code, not skill/template/doc>
Strategy (ordered batches): 1. add `detectAgentEnriched`/`_detect_agent_enriched(env, target, which)` WRAPPING the unchanged env-only detector 2. add a fail-soft `readinessLine` probe (git/python3/agent via PATH lookup) 3. wire the enriched default into the interactive agent select + render the readiness line after the banner (interactive only) — leave the non-interactive write on the env-only detector.
Safety rule (feature-specific): the env-only `detectAgent`/`_detect_agent` is NEVER modified; enrichment + the readiness line are wired ONLY into the interactive path; every probe is a PATH/file lookup wrapped fail-soft (no spawn, never throws); the non-interactive stdout stays byte-identical.
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

- [x] all tests pass — full suite 1300 OK (was 1286; +14 test_readiness_detect); `test_readiness_detect` 14/14
- [x] coverage did not decrease — +14 tests over the new symbols; the env-only pins (test_agent_detect, the byte-identical boundary) still green
- [x] no test or contract was altered during build — test_readiness_detect.py unchanged since the tests phase (untracked, no build-phase edit); §3 FROZEN @ v1 untouched
- [x] the green was EARNED, not gamed — the enriched detector is hermetic (injectable `which`, no spawn); the interactive subprocess tests assert real stdout ("Pre-flight" present interactive / absent non-interactive); the boundary test proves the non-interactive write stays env-only (CLAUDE.md present → still writes AGENTS.md)
- [x] concurrency / timing of the risky operation is safe — every probe is a synchronous local PATH/file lookup (no spawn, no network, no shared state); each wrapped fail-soft (a throwing probe reads as absent)
- [x] no exposed secrets, injection openings, or unexpected dependencies — `whichSync` joins FIXED literals ("git"/"python3"/"claude"/"codex"/"opencode") onto PATH dirs (no user input, no shell); no new dependency; add.py untouched (ENGINE pin holds)
- [x] layering & dependencies follow CONVENTIONS.md — both twins keep parity (npm clack / pip input()); enrichment WRAPS the env-only detector, never rewrites it; design-for-failure: fail-soft probes + the existing `.bak` rollback in writeAgentPointer
- [x] a person reviewed and approved the change — auto-resolved under `autonomy: auto` (no security/concurrency/architecture residue); live smoke confirmed both twins render `Pre-flight: git ✓ · python3 ✓ · agent: …` (unicode) and `git + | python3 + | agent: …` (ASCII)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `detectAgentEnriched`/`_detect_agent_enriched` seed the interactive agent default (cli.js cmdInit → runClackPreamble select initialValue; _installer.py interactive write at the drop) · `readinessLine`/`_readiness_line` render after the banner in the interactive block of both twins · `whichSync` backs the npm probes · npm exports added (`module.exports`) + `require.main === module` guard so the harness can `require()` without running the installer
- [x] DEAD-CODE (code) — no orphans: every new symbol is referenced (detectors by the writes + readiness line + tests; whichSync by readiness/enriched; exports by test_readiness_detect's node harness)
- [x] SEMANTIC (prose / non-code) — n/a (code-only change; no prose/doc edited)

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang (auto-resolved, autonomy: auto) · date: 2026-06-18

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
