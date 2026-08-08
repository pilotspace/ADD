# TASK: Gemini profile + .gemini/settings.json context.fileName merge

slug: gemini-settings-config · created: 2026-06-18 · stage: mvp
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
- `add-method/src/add_method/_installer.py:AGENT_PROFILES` (~253) — add the `gemini` entry (sibling of cursor/.. added in agents-md-profiles); `install()` (567) calls `_write_agent_pointer(target_path, profile)` at line 677 — the hook point for the new settings merge.
- `add-method/bin/cli.js:AGENT_PROFILES` (84) — add the `gemini` entry; `dropFiles()` (400) calls `writeAgentPointer(target, profile)` at line 408 — the JS hook point.
- NEW symbol both twins: `_write_gemini_settings(target)` / `writeGeminiSettings(target)` — read-merge-write `.gemini/settings.json` so `context.fileName` includes "AGENTS.md"; fail-soft, idempotent.
- `add-method/tooling/test_agent_detect.py` — sibling tests already cover detection/parity; the gemini detection token rides the same ParityTest. New settings-merge tests go in a new file `add-method/tooling/test_gemini_settings.py`.

Context (working folder): Gemini CLI `settings.json` schema (researched): `{ "context": { "fileName": <string | string[]> } }` — default "GEMINI.md"; if both GEMINI.md and AGENTS.md exist, GEMINI.md wins, so AGENTS.md must be added to context.fileName to be loaded. Lives at `<project>/.gemini/settings.json` (project scope). The pointer (AGENTS.md) is written by the existing `_write_agent_pointer` for the gemini profile; this task only ADDS the settings wiring.

Honors (patterns / conventions):
- twin parity — the gemini profile + the settings-merge decision identical in both twins.
- fail-soft + idempotent — mirror `_write_intent_note` / `_write_agent_pointer`: a write/parse error warns + skips, never raises, never aborts the drop; a second run is a no-op.
- preserve user keys — a read-merge-write must keep every existing settings.json key untouched (only context.fileName is augmented).
- ENGINE_MD5 pin: `add.py` untouched.

Anchors the contract cites: `AGENT_PROFILES` (gemini entry), `_write_gemini_settings` / `writeGeminiSettings`, the `install()` / `dropFiles()` hook after the pointer write.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: A `gemini` agent profile plus a NEW fail-soft, idempotent merge of `.gemini/settings.json` so Gemini CLI auto-loads the AGENTS.md pointer ADD already writes.
Framings weighed: merge-context.fileName (chosen — adds AGENTS.md to Gemini's config so it loads on first run, preserving GEMINI.md) · write-GEMINI.md-instead (rejected — the human picked AGENTS.md + settings; a second GEMINI.md pointer would duplicate the block) · overwrite-settings.json (rejected — clobbers the user's existing Gemini config).
Must:
<must>
  - Both twins' `AGENT_PROFILES` include a `gemini` entry: id `gemini`, integration_file `AGENTS.md`, env signals + `GEMINI_` prefix, a next_step naming AGENTS.md (and that ADD wires the settings for it), inserted before `generic`.
  - A NEW `_write_gemini_settings(target)` / `writeGeminiSettings(target)` ensures `"AGENTS.md"` is in `settings["context"]["fileName"]` of `<target>/.gemini/settings.json`: missing file → create `{"context":{"fileName":["AGENTS.md"]}}`; a string value → `[<existing>, "AGENTS.md"]`; a list → append `"AGENTS.md"` if absent; already present → no write.
  - Every OTHER key in settings.json is preserved verbatim (read-merge-write, never overwrite).
  - The merge is invoked from `install()` / `dropFiles()` AFTER the pointer write, ONLY when `profile.id == "gemini"`.
  - Idempotent: a second run on a settings.json that already lists AGENTS.md makes no change ("unchanged").
  - Fail-soft: an unparsable or unwritable settings.json (or `.gemini/` dir) warns + skips the merge, never raises, never aborts the drop.
  - `add.py` untouched (ENGINE_MD5 pin); both twins decision-equal.
</must>
Reject:
<reject>
  - settings.json present but not valid JSON -> warn + skip the merge, leave the file byte-untouched -> "settings_unparsable"
  - `.gemini/` dir or settings.json unwritable -> warn + skip, never abort the drop -> "settings_unwritable"
  - a non-gemini profile -> the merge is never invoked (not an error; no `.gemini/` is created)
</reject>
After:
<after>
  - A Gemini install writes AGENTS.md (the pointer) AND a `.gemini/settings.json` whose `context.fileName` includes "AGENTS.md", preserving any prior keys; re-running is a no-op; a broken settings file is left as-is and the drop still exits 0.
  - No `.gemini/` is created for any non-gemini agent.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ The Gemini settings schema is `context.fileName` (a nested object, value string|list) — confirmed against current Gemini CLI docs, but it is an EXTERNAL tool's evolving config. If the key path changed: ADD writes a key Gemini ignores → AGENTS.md not auto-loaded (the drop + the AGENTS.md pointer are still fine; only the auto-wire silently no-ops). Lowest confidence because we cannot pin an external schema from tests.
  - [ ] creating the whole `context` object when settings.json is absent is safe — Gemini merges user+project settings and we write only project scope; we never touch `~/.gemini`.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: Detect gemini and write the AGENTS.md pointer
  Given an env with the Gemini signal
  When the installer detects the agent
  Then it returns the gemini profile with integration_file AGENTS.md

Scenario: Fresh project gets a settings.json that loads AGENTS.md
  Given a target with no .gemini/settings.json
  When the gemini settings merge runs
  Then .gemini/settings.json is created with context.fileName == ["AGENTS.md"]

Scenario: A string fileName becomes a list including AGENTS.md
  Given settings.json with context.fileName == "GEMINI.md"
  When the merge runs
  Then context.fileName == ["GEMINI.md", "AGENTS.md"]

Scenario: AGENTS.md is appended to an existing list
  Given settings.json with context.fileName == ["GEMINI.md"]
  When the merge runs
  Then context.fileName contains both "GEMINI.md" and "AGENTS.md"

Scenario: Other settings keys are preserved
  Given settings.json with an unrelated key (e.g. {"theme":"dark", "context":{...}})
  When the merge runs
  Then the unrelated key is unchanged

Scenario: Re-running is a no-op (idempotent)
  Given settings.json whose context.fileName already includes "AGENTS.md"
  When the merge runs again
  Then the file is unchanged (outcome "unchanged")

Scenario: Malformed settings.json is left untouched   # Reject settings_unparsable
  Given settings.json containing invalid JSON
  When the merge runs
  Then the merge is skipped and the file is byte-identical
  And no exception is raised

Scenario: Unwritable settings does not abort the drop   # Reject settings_unwritable
  Given a Gemini install where .gemini/settings.json cannot be written
  When the full drop runs
  Then the merge warns and is skipped
  And the managed-layer drop is intact and the run exits 0

Scenario: No .gemini for a non-gemini agent
  Given a Cursor install
  When the drop runs
  Then no .gemini/ directory is created
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
# gemini profile (both twins), inserted before generic:
gemini : integration_file=AGENTS.md   env=[GEMINI_CLI, GEMINI_SANDBOX]   prefix=GEMINI_
         next_step="Open Gemini CLI — ADD wired .gemini/settings.json to load AGENTS.md; say what you want to build."

# NEW symbol (both twins):
writeGeminiSettings(target) / _write_gemini_settings(target) -> "created"|"updated"|"unchanged"|"skipped"
  path  : <target>/.gemini/settings.json     (project scope; ~/.gemini is never touched)
  invariant: ensure "AGENTS.md" ∈ settings["context"]["fileName"]
    · missing file         -> write {"context":{"fileName":["AGENTS.md"]}}          -> "created"
    · fileName is string s  -> [s, "AGENTS.md"]   (existing first, AGENTS.md appended) -> "updated"
    · fileName is a list    -> append "AGENTS.md" iff absent                          -> "updated"
    · "AGENTS.md" already in -> no write                                              -> "unchanged"
    · every other key        -> preserved verbatim (read → merge → write, 2-space JSON)
    · unparsable / unwritable -> warn, return "skipped", file byte-untouched, drop continues
  hook  : install()/dropFiles() call it AFTER the pointer write, iff profile.id == "gemini"

Schema: project-scope JSON config file; no persisted ADD state; `add.py` (engine) untouched.
Out of scope: ~/.gemini global settings; GEMINI.md authoring; any non-gemini agent config.
```

Status: FROZEN @ v1 — approved by Tin Dang (2026-06-18; approach pre-chosen at intake: "AGENTS.md + configure settings.json"; ship-the-milestone directive)
Least-sure flag surfaced at freeze: [contract] the Gemini settings schema is `context.fileName` (nested object, string|list) — confirmed against current Gemini CLI docs but an external, evolving config; if the key path changed upstream, ADD writes a key Gemini ignores → AGENTS.md not auto-loaded (drop + AGENTS.md pointer still fine; only the auto-wire no-ops). Mitigated: read-merge-write preserves user keys, fail-soft on parse/write error.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every merge branch + every Reject; pip hermetic; one npm subprocess flow test (skip without node).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_detect_gemini: _detect_agent({GEMINI_CLI:"1"}) -> id gemini, integration_file AGENTS.md
  - test_fresh_creates_settings: _write_gemini_settings(tmp) -> "created"; .gemini/settings.json context.fileName == ["AGENTS.md"]
  - test_string_fileName_becomes_list: seed {"context":{"fileName":"GEMINI.md"}} -> fileName == ["GEMINI.md","AGENTS.md"]
  - test_list_appends_agents_md: seed {"context":{"fileName":["GEMINI.md"]}} -> both present
  - test_other_keys_preserved: seed {"theme":"dark","context":{"fileName":["GEMINI.md"]}} -> theme == "dark" after
  - test_idempotent: run twice -> second returns "unchanged", file bytes unchanged
  - test_malformed_skipped: settings.json = "{not json" -> "skipped", bytes unchanged, no raise
  - test_unwritable_does_not_abort: install(gemini env) where .gemini/settings.json path is a dir -> drop exits 0, skill intact
  - test_no_gemini_dir_for_other_agent: install(cursor env) -> no .gemini/ created
  - test_install_flow_writes_pointer_and_settings: install(gemini env) -> AGENTS.md (one block) AND .gemini/settings.json lists AGENTS.md
  - test_parity_gemini_symbol: both cli.js and _installer.py mention gemini + the settings-merge symbol (writeGeminiSettings/_write_gemini_settings)
  - test_npm_gemini_writes_settings (subprocess, skipUnless node): init --yes under GEMINI env writes AGENTS.md + .gemini/settings.json
</test_plan>

Tests live in: `add-method/tooling/test_gemini_settings.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/bin/cli.js` `add-method/src/add_method/_installer.py` `add-method/tooling/test_gemini_settings.py`
Strategy (ordered batches): 1. write test_gemini_settings.py (red) · 2. add the gemini profile + `_write_gemini_settings` + the install() hook in _installer.py · 3. mirror into cli.js (writeGeminiSettings + dropFiles hook + export) · 4. green.
Safety rule (feature-specific): read-merge-write — NEVER overwrite settings.json; preserve every existing key; the merge is fail-soft (a parse/write error returns "skipped", never raises).
Code lives in: `add-method/bin/cli.js` + `add-method/src/add_method/_installer.py`
Constraints: do NOT change any test or the contract; no new dependency (json stdlib / Node JSON); `add.py` byte-identical; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 1367 green (test_gemini_settings 12/12, incl. live cli.js npm subprocess)
- [x] coverage did not decrease — 12 new tests in a new file; none removed
- [x] no test or contract was altered during build — only the red suite + the two twins changed
- [x] the green was EARNED, not gamed — tests assert real merge behavior across every branch (create/string→list/append/idempotent/preserve-keys/malformed-skip) + a LIVE node install that writes & re-reads .gemini/settings.json. No stubs.
- [x] concurrency / timing safe — single synchronous read-merge-write of one file; no shared state, no race
- [x] no exposed secrets, injection openings, or unexpected dependencies — JSON via stdlib/Node built-in; no new dep; settings values are data, never executed
- [x] layering & dependencies follow CONVENTIONS.md — twin parity held; fail-soft mirrors _write_intent_note/_write_agent_pointer
- [x] a person reviewed and approved the change — Tin Dang pre-chose the AGENTS.md+settings approach at intake and directed the ship

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] A gemini install produces BOTH AGENTS.md (one ADD block) and .gemini/settings.json with "AGENTS.md" in context.fileName — confirmed live: `GEMINI_CLI=1 node bin/cli.js init` wrote AGENTS.md + `{"context":{"fileName":["AGENTS.md"]}}`
- [x] An existing settings.json keeps its other keys and its prior fileName entries after the merge — confirmed by test_other_keys_preserved + test_string_fileName_becomes_list + test_list_appends_agents_md
- [x] A malformed or unwritable settings.json never aborts the drop (exit 0) and is left byte-identical — confirmed by test_malformed_skipped + test_unwritable_does_not_abort
- [x] No .gemini/ is created for a non-gemini agent — confirmed by test_no_gemini_dir_for_other_agent
- [x] Both twins define the gemini profile + the settings-merge symbol — confirmed by test_parity_gemini_symbol; add.py byte-identical (git diff empty)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_write_gemini_settings`/`writeGeminiSettings` are called from install()/dropFiles() (gemini branch) and exported in cli.js; a live install exercised the path end-to-end
- [x] DEAD-CODE (code) — no orphan: the function has one caller (the gemini branch) + the test + the export; the gemini profile is consumed by the same registry loop as the others
- [ ] SEMANTIC (prose / non-code) — N/A (code change)

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
