# TASK: Add cursor/windsurf/trae/copilot/cline/aider profiles to both twins

slug: agents-md-profiles · created: 2026-06-18 · stage: mvp
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
- `add-method/bin/cli.js:AGENT_PROFILES` (line 84) — ordered JS array of `{ id, label, integration_file, env:[...], envPrefix, next_step }`; `generic` is last (fallback). Consumed by `detectAgent` (115–116), `detectAgentEnriched` byId map (150), and the clack agent-select `AGENT_PROFILES.map(...)` (347).
- `add-method/bin/cli.js:detectAgentEnriched` (line 145) — machine-signal PATH probe loop `for (const id of ["claude","codex","opencode"])` (154); env signal wins, then CLAUDE.md repo signal, then installed-CLI.
- `add-method/bin/cli.js:GENERIC_NEXT` (line 79) — the generic onramp string the `generic` profile's `next_step` reuses.
- `add-method/src/add_method/_installer.py:AGENT_PROFILES` (line 253) — the parity TWIN: tuple of dicts, same fields but snake_case `env_prefix`; `_GENERIC_NEXT` (248). `generic` last.
- `add-method/src/add_method/_installer.py:_detect_agent` (284) / `_detect_agent_enriched` (294) — probe tuple `("claude","codex","opencode")` (311); `_readiness_line` (338) reads the enriched label.
- `add-method/tooling/test_agent_detect.py:ParityTest::test_parity_profiles` (215) — token list BOTH twins must contain; `DetectTest` (56) per-env detection cases; `NpmAgentTest` (183) drives real cli.js via node subprocess.

Context (working folder): README.md / GETTING-STARTED.md / `help` copy name the supported agents — DEFERRED to sibling task `onboarding-docs-refresh` (out of scope here). Research facts (June 2026): Cursor, Windsurf, Trae all natively read `AGENTS.md` (root); Copilot's native file is `.github/copilot-instructions.md` (also reads AGENTS.md); Cline → `.clinerules`; Aider → `CONVENTIONS.md` (both also read AGENTS.md). Per-agent file CHOICE is the §1/§3 decision below.

Honors (patterns / conventions):
- twin parity — every profile + detection decision identical in both twins (guarded by `test_agent_detect.py::ParityTest`); rendering may differ, decisions may not.
- detection contract FROZEN @ v1 (per test_agent_detect docstring): `_detect_agent` is pure · total · deterministic · never-throws · generic-last; this task EXTENDS the registry the contract operates over, additively — it does not change that behavior.
- best-effort env signal: a mis-detect degrades to generic and is overridable in the interactive picker; the non-interactive write stays env-only (enrichment is interactive-default only).
- ENGINE_MD5 pin: `add.py` is NOT touched by this task (installer twins only).

Anchors the contract cites: `AGENT_PROFILES` (bin/cli.js + _installer.py), the enriched-detection probe list (`detectAgentEnriched` / `_detect_agent_enriched`), `_detect_agent` / `detectAgent`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Six new agent profiles (cursor · windsurf · trae · copilot · cline · aider) in the installer's `AGENT_PROFILES` registry, mirrored across both twins, each detected best-effort and given its most-reliable auto-loaded context file plus a tailored onramp.
Framings weighed: native-file-per-agent (chosen — each profile points at the file the agent actually auto-loads on first run) · uniform-AGENTS.md-for-all (rejected — Cline auto-loads `.clinerules` not workspace AGENTS.md [proposal only], so a uniform AGENTS.md silently fails to onboard it) · agent-native-rule-directories (rejected — `.cursor/rules/*.mdc`, `.windsurf/rules/`, `.clinerules/` dir trees are explicitly OUT per MILESTONE; ADD writes ONE markdown pointer file per agent).
Must:
<must>
  - Both twins' `AGENT_PROFILES` include cursor, windsurf, trae, copilot, cline, aider — each as `{ id, label, integration_file, env, env_prefix|null, next_step }`, inserted BEFORE the `generic` fallback (generic stays last).
  - integration_file per agent is the file it auto-loads (all at the project ROOT, no nesting): cursor→`AGENTS.md` · windsurf→`AGENTS.md` · trae→`AGENTS.md` · copilot→`AGENTS.md` · aider→`AGENTS.md` · cline→`.clinerules`.
  - `_detect_agent` / `detectAgent` returns the matching profile when that agent's env signal is present; an unknown/empty env still returns `generic` (the FROZEN-@-v1 contract holds: pure · total · deterministic · never-throws · generic-last).
  - The enriched-detection machine-probe list (`detectAgentEnriched` / `_detect_agent_enriched`) is extended with the new agents' CLI binary names so an installed CLI is a machine signal — AFTER the env signal and the CLAUDE.md repo signal (precedence unchanged).
  - The pointer writer (`writeAgentPointer` / `_write_agent_pointer`) is UNCHANGED — every integration_file is a project-root file, so the existing writer already handles all six.
  - Each profile's `next_step` names the agent and how it loads ADD; copilot's and aider's also name the one config step they need (copilot reads AGENTS.md automatically in recent versions; aider needs `.aider.conf.yml` / `--read` since it auto-loads no file by default).
  - Both twins stay decision-equal; `test_agent_detect.py::ParityTest` passes with the six new tokens present in BOTH files.
</must>
Reject:
<reject>
  - integration_file target is undecodable (not valid UTF-8) -> warn + skip the pointer, leave bytes untouched -> "integration_unreadable"  (existing v1 reject — preserved for the new agents)
  - integration_file target is unwritable -> warn + skip the pointer, never abort the drop -> "integration_unwritable"  (existing v1 reject — preserved for the new agents)
  - an env value present but empty/whitespace for a signal key -> treated as unset (no match) -> falls through to generic (no error; mirrors today's `CLAUDECODE:"" -> generic`)
</reject>
After:
<after>
  - Invoking the installer under any of the six agents' env signals writes that agent's integration_file with exactly one ADD pointer block (shared `_GUIDE_BEGIN`/`_GUIDE_END` markers) and prints that agent's tailored next_step.
  - Detection stays pure · total · deterministic · never-throws · generic-last; an unknown env still gets generic `AGENTS.md`.
  - Both twins enumerate the same six profiles in the same order; ParityTest green; `add.py` (engine) untouched (ENGINE_MD5 pin holds).
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ aider auto-loads NO file by default — writing `AGENTS.md` for it only onboards aider once the user adds it via `.aider.conf.yml` / `--read` (that config step is OUT of this task). Lowest confidence because it's the one agent whose first-run onramp is NOT automatic. If wrong (user never wires it): aider silently never reads the pointer (the drop + skill still succeed; only aider's pointer is unread). Decided with the human at freeze: aider stays on the shared AGENTS.md with a next_step that names the config step.
  - [ ] env-detection signals per agent are best-effort (the tools' launch env vars are largely undocumented), so detection may mis-fire to generic — acceptable under the FROZEN best-effort/overridable contract; the interactive picker + the installed-CLI machine-probe are the second/third signals. If wrong: a worse auto-DEFAULT, never a wrong write (the picker corrects it).
  - [ ] cline's integration_file is the single-file `.clinerules` form (not the `.clinerules/` directory); Cline reads both, and the single file matches ADD's one-pointer-file model.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: Detect each new agent from its env signal
  Given an env carrying a known agent's signal (e.g. CURSOR_AGENT, WINDSURF, TRAE_AI_IDE, COPILOT_*, CLINE_*, AIDER_*)
  When the installer detects the agent
  Then it returns that agent's profile (id == cursor|windsurf|trae|copilot|cline|aider)

Scenario: Unknown env still degrades to generic
  Given an env with none of the known agent signals
  When the installer detects the agent
  Then it returns the generic profile with integration_file AGENTS.md
  And detection never throws on empty/odd input

Scenario: Each profile maps to its auto-loaded file (all at project root)
  Given the AGENT_PROFILES registry
  When I read each new profile's integration_file
  Then cursor|windsurf|trae|copilot|aider == AGENTS.md and cline == .clinerules

Scenario: An installed agent CLI is a machine signal when env is silent
  Given an env with no agent signal but a probe reporting the agent's CLI on PATH
  When enriched detection runs
  Then it returns that agent's profile (env signal would still win if present; CLAUDE.md repo signal still outranks the CLI probe)

Scenario: A tailored next_step is printed per agent
  Given an install under a known agent's env
  When the drop completes
  Then the closing line names that agent and how it loads ADD (copilot's and aider's also name the config step they need)

Scenario: Both twins enumerate the same six profiles
  Given bin/cli.js and src/add_method/_installer.py
  When ParityTest scans both for the new tokens
  Then cursor, windsurf, trae, copilot, cline, aider all appear in BOTH files

Scenario: Undecodable integration target is left untouched   # Reject integration_unreadable
  Given a Cursor target whose AGENTS.md is not valid UTF-8
  When the installer writes the agent pointer
  Then the write is skipped
  And the file is left byte-identical

Scenario: Unwritable integration target does not abort the drop   # Reject integration_unwritable
  Given a Cursor target where AGENTS.md cannot be written (a directory exists at that path)
  When the installer runs the full drop
  Then the pointer write warns and is skipped
  And the managed-layer drop (skill/tooling/docs) is still intact and the run exits 0

Scenario: An empty env value is treated as unset   # Reject (fall-through, not an error)
  Given an env where a known signal key is present but empty/whitespace
  When the installer detects the agent
  Then that key does not match and detection falls through toward generic
  And no error is raised
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
# AGENT_PROFILES — six new entries, inserted BEFORE `generic` (generic stays last), in BOTH twins.
# Profile shape (unchanged): { id, label, integration_file, env, env_prefix(py)|envPrefix(js), next_step }

cursor   : integration_file=AGENTS.md    env=[CURSOR_AGENT, CURSOR_TRACE_ID]  prefix=CURSOR_
windsurf : integration_file=AGENTS.md    env=[WINDSURF, WINDSURF_ENV]         prefix=WINDSURF_
trae     : integration_file=AGENTS.md    env=[TRAE_AI_IDE]                    prefix=TRAE_
copilot  : integration_file=AGENTS.md    env=[COPILOT_AGENT]                  prefix=null   # NOT GITHUB_ prefix (CI false-positive)
cline    : integration_file=.clinerules  env=[CLINE_ACTIVE]                   prefix=CLINE_
aider    : integration_file=AGENTS.md    env=[AIDER_*]                        prefix=AIDER_   # auto-loads via .aider.conf.yml/--read (user-wired; next_step says so)

# Detection (signatures + invariants UNCHANGED — registry extended, contract preserved):
detectAgent(env) / _detect_agent(env) -> profile
  · walks AGENT_PROFILES top→bottom, first env-match wins, generic last
  · pure · total · deterministic · never-throws  (FROZEN @ v1 — this task does not alter it)
detectAgentEnriched(env, target, which) / _detect_agent_enriched(...) -> profile
  · precedence: env signal > CLAUDE.md repo signal > installed-CLI machine probe > generic
  · machine-probe id list EXTENDED to: [claude, codex, opencode, cursor, windsurf, trae, copilot, cline, aider]

# Pointer writer — UNCHANGED (every integration_file is a project-root file; existing writer handles all six):
writeAgentPointer(target, profile) / _write_agent_pointer(...) -> "created"|"updated"|"unchanged"|"skipped"
  · undecodable/unwritable target -> "skipped" (warn), never raises, never aborts the drop  (existing v1 behavior)

Schema: no persisted state; AGENT_PROFILES is the in-code registry. `add.py` (engine) untouched.
Out of scope (this task): aider's .aider.conf.yml / gemini's settings.json config wiring (gemini-settings-config owns JSON config); agent-native rule DIRECTORIES.
```

Status: FROZEN @ v1 — approved by Tin Dang (2026-06-18; copilot moved to shared AGENTS.md, nested-path machinery dropped)
Least-sure flag surfaced at freeze: [contract] aider auto-loads no file by default — writing AGENTS.md only onboards it once the user wires `.aider.conf.yml`/`--read` (out of this task); if the user never wires it, aider silently never reads the pointer. Accepted: aider stays on the shared AGENTS.md with a next_step that names the config step. Secondary [contract]: per-agent env-detection signals are best-effort guesses (tools' launch env vars undocumented) — a mis-detect degrades to generic and is overridable in the picker.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every new profile + every Reject exercised (parity-equivalent in both twins; pip hermetic, npm via node subprocess — honest-skip without node).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_detect_each_new_agent_from_env: for each of the 6, _detect_agent({signal:"1"}) -> that id (subTest per agent)
  - test_unknown_still_generic: _detect_agent({}) -> generic, integration_file AGENTS.md; _detect_agent({CURSOR_AGENT:""}) -> generic (empty == unset)
  - test_integration_file_mapping: assert each profile's integration_file == expected (cursor/windsurf/trae/copilot/aider AGENTS.md, cline .clinerules)
  - test_enriched_cli_probe: _detect_agent_enriched({}, target=None, which=lambda c: c=="cursor") -> cursor; env signal still wins; an existing CLAUDE.md still outranks the CLI probe
  - test_next_step_per_agent: each new profile's next_step names the agent; copilot's + aider's mention the config step they need
  - test_parity_six_profiles: ParityTest tokens extended — cursor/windsurf/trae/copilot/cline/aider present in BOTH cli.js and _installer.py
  - test_undecodable_target_skipped: AGENTS.md written as UTF-16 -> _write_agent_pointer(cursor) -> "skipped", bytes unchanged
  - test_unwritable_does_not_abort: cursor install where AGENTS.md path is a directory -> drop exits 0, skill/tooling/docs intact
  - test_npm_detect_each_new_agent (subprocess, skipUnless node): init --yes under each agent env writes the expected integration_file + prints the tailored next step
</test_plan>

Tests live in: `add-method/tooling/test_agent_detect.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/bin/cli.js` `add-method/src/add_method/_installer.py` `add-method/tooling/test_agent_detect.py`
Strategy (ordered batches): 1. extend test_agent_detect.py (the red suite — new detection/mapping/parity/reject cases) · 2. add the 6 entries to AGENT_PROFILES + extend the enriched probe list in _installer.py (pip twin) · 3. mirror byte-decision-equal into cli.js (pointer writer unchanged) · 4. run the suite green.
Safety rule (feature-specific): the two twins must stay decision-equal — change both in the same batch; never let cli.js and _installer.py diverge on a profile or a probe id.
Code lives in: `add-method/bin/cli.js` + `add-method/src/add_method/_installer.py`
Constraints: do NOT change any test or the contract; no new dependency (stdlib / Node built-ins only); `add.py` (engine) stays byte-identical (ENGINE_MD5 pin); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 1355 green (test_agent_detect 26/26, incl. live cli.js npm subprocess per new agent)
- [x] coverage did not decrease — 10 new tests added, none removed
- [x] no test or contract was altered during build — only the red suite (written in §4) + the two twins changed
- [x] the green was EARNED, not gamed — tests assert real behavior: env→id, integration_file mapping, next_step content, parity tokens present in BOTH files, and a LIVE node subprocess that actually writes each agent's file. No fixtures stubbed.
- [x] concurrency / timing of the risky operation is safe — N/A: pure in-memory data registry + a PATH-lookup probe; no IO race, no shared state
- [x] no exposed secrets, injection openings, or unexpected dependencies — no secrets; no new dependency (stdlib / Node built-ins); env keys are read, never executed
- [x] layering & dependencies follow CONVENTIONS.md — twin parity preserved; detection contract (pure·total·deterministic·never-throws·generic-last) unchanged
- [x] a person reviewed and approved the change — Tin Dang approved the frozen contract (§3) and directed the merge/release

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] Each of the 6 env signals resolves to its own profile id; an unknown/empty env resolves to generic — confirmed by test_detect_each_new_agent_from_env + test_unknown_and_empty_still_generic green
- [x] Each new profile's integration_file is the expected root file (5×AGENTS.md, cline→.clinerules) and a write produces exactly one ADD pointer block — confirmed by test_integration_file_mapping + test_pointer_written_for_new_agent + test_cline_writes_clinerules
- [x] Both twins literally contain all six new ids — confirmed by test_parity_six_new_profiles green AND live `WINDSURF=1 → AGENTS.md`, `CLINE_ACTIVE=1 → "Open Cline — it reads .clinerules"` from node bin/cli.js
- [x] An unwritable/undecodable target skips the pointer without aborting the drop (exit 0, managed layer intact) — confirmed by test_unwritable_target_does_not_abort_drop + the existing v1 reject tests green
- [x] add.py is byte-identical — confirmed: `git diff --stat tooling/add.py` empty; the ENGINE_MD5 pin test passed in the full run

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — the 6 new entries are consumed by `detectAgent`/`_detect_agent` (registry loop), the clack agent-select (`AGENT_PROFILES.map`), and the enriched probe list; cli.js references AGENT_PROFILES in 7 places; a live node install writes each agent's file
- [x] DEAD-CODE (code) — no new unused symbols: the entries are data consumed by existing loops; the probe list gained 6 string ids, all reachable via `which`
- [ ] SEMANTIC (prose / non-code) — N/A (code change; no prose contract)

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-18

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
