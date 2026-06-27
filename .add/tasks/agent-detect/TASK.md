# TASK: Detect the coding agent, write its integration file, print its exact next step

slug: agent-detect · created: 2026-06-17 · stage: mvp
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
  - `add-method/bin/cli.js:dropFiles(args,target)` — drops the managed layer then prints a GENERIC closing next-step (lines 115-120: "open your AI Agent CLI (like Claude Code, Codex, etc.), then run `/add`…"). The agent-specific next-step lands here.
  - `add-method/bin/cli.js:runClackPreamble(clack,target)` — the interactive step sequence (intro → text target → confirm). Per the seeded delta, the agent-detect confirm is a STEP in THIS flow, not a separate prompt stack.
  - `add-method/bin/cli.js:cmdInit/interactive/loadClack` — the TTY gate + lazy clack import (unchanged; detection rides the same gate).
  - `add-method/src/add_method/_installer.py:install(...)` — pip twin: identical generic closing next-step (lines 158-162), cancel→130, returns 0. Detection + agent-specific next-step mirror here for parity.
  - `add-method/tooling/add.py:_guideline_block()` — the canonical agent-agnostic ADD block; ALREADY agent-aware in content ("On Claude Code the `add` skill drives this loop… other agents follow the three steps").
  - `add-method/tooling/add.py:_inject_block(path)` — marker-injection safety to MIRROR for any drop-time pointer write: created|updated|unchanged · `.bak` on change · replace only the `_GUIDE_BEGIN.._GUIDE_END` region · append-if-no-block (preserve user content) · fail-soft.
  - `add-method/tooling/add.py:GUIDELINE_FILES=("AGENTS.md","CLAUDE.md")` · `_GUIDE_BEGIN`/`_GUIDE_END` markers · `cmd_sync_guidelines`/`_inject_guidelines` — writes BOTH files at `init` (NOT at the installer drop). Symlink-dedup + per-target OSError isolation.
Context (working folder):
  - Today the installer DROPS FILES ONLY: it does NOT run `add.py init` and does NOT write AGENTS.md/CLAUDE.md — those appear when `/add`→init runs sync-guidelines. So a freshly-`npx`'d project has NO integration file until init.
  - Hard constraints (pinned by tests, MUST hold): `test_v8_install.py::test_cli_does_not_autorun_init` (no `spawnSync`/`initArgs` — the installer may NOT run Python) · `test_installer_py_does_not_autorun_init` (no `mod.main`/`init_argv`) · `test_v8_install` closing-hint guards (AI-first · conversational-only · names `/add`) · `test_agent_portability.py` (a non-Claude agent reaches the phase guide from AGENTS.md ALONE) · `test_guidelines.py` (inject idempotency/.bak/symlink/UTF-8 safety) · `test_installer_prompts.py` (interactive/cancel/fallback order) · `test_v8_onramp.py` (block content).
  - Seeded SPEC delta (from installer-prompts): the agent-detect prompt is a STEP in the clack flow, rendered through the established `ui` layer — not a separate prompt stack.
Honors (patterns / conventions):
  - drops-files-only (no `add.py init`, no Python spawn from the installer) · designed-for-failure on every new IO path (unknown agent → generic AGENTS.md + generic next-step = today's behavior; unwritable file → warn + continue) · npm↔pip parity (identical detection + next-step + file-write semantics; only clack richness differs) · the managed↔user-data boundary (a drop-time pointer uses the SAME markers so init's sync-guidelines supersedes it — never a competing block).
Anchors the contract cites: a shared **agent profile** registry + a pure `detectAgent(env)`/`_detect_agent(env)` → `{id, label, integration_file, next_step}` (env-signal precedence, unknown→generic); the installer's closing next-step = the detected profile's `next_step`; an optional drop-time `writeAgentPointer`/`_write_agent_pointer(target, profile)` that mirrors `_inject_block` (same `_GUIDE_BEGIN/_GUIDE_END` markers); an interactive clack confirm STEP inside `runClackPreamble`.
  - `bin/cli.js`: `AGENT_PROFILES`, `detectAgent(env)`, `writeAgentPointer(target, profile)`, agent-aware closing next-step in `dropFiles`, a profile-confirm step in `runClackPreamble`.
  - `_installer.py`: `AGENT_PROFILES` (parity), `_detect_agent(env)`, `_write_agent_pointer(target, profile)`, agent-aware closing next-step in `install()`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Agent detection — the installer detects the active coding agent, writes THAT agent's integration file (a marker-delimited ADD pointer), and prints THAT agent's exact next step; an unknown agent degrades to the generic AGENTS.md + today's generic next step
Framings weighed: a shared ordered **agent-profile registry** + a pure env-driven `detectAgent(env)`, surfaced as (a) the closing next-step and (b) a drop-time integration-file pointer, with an interactive clack confirm step (chosen) · detect from ON-DISK markers (.claude/, .cursor/) instead of env (rejected: markers describe the project's PRIOR setup, not which agent is invoking NOW — env is the live signal; markers misfire when a project has .claude/ but the user runs Codex) · write the FULL guideline block at drop time (rejected: would duplicate add.py's single-sourced `_guideline_block()` in JS+pip or force a Python spawn — both break a constraint; a minimal SAME-MARKER pointer that init's sync-guidelines supersedes is leaner and parity-safe) · next-step message only, no file write (rejected: a non-Claude agent like Codex/OpenCode has no skill mechanism, so without a drop-time AGENTS.md it cannot discover ADD until init — the file write is the core "auto-correct" value)
Must:
<must>
  - D1 detectAgent(env) is PURE + DETERMINISTIC: an ordered profile registry, first match wins, generic always last → returns a profile {id, label, integration_file, next_step}. Same env in → same profile out; never throws.
  - D2 the Claude family (Claude Code / Claude app) is detected from its env signal (CLAUDECODE truthy OR CLAUDE_CODE_ENTRYPOINT set) → integration_file CLAUDE.md · next_step names `/add`.
  - D3 a known non-Claude CLI agent (Codex · OpenCode) is detected from its env signal → integration_file AGENTS.md · next_step names AGENTS.md as the entry ("it reads AGENTS.md; say what you want to build").
  - D4 an UNKNOWN agent (no signal matches) → the generic profile: integration_file AGENTS.md · next_step = today's generic message (byte-identical onramp wording is preserved).
  - D5 the installer's CLOSING next-step prints the detected profile's next_step (replacing the fixed generic line) — npm and pip identical.
  - D6 the installer WRITES the detected profile's integration_file at the target root as a marker-delimited ADD pointer, mirroring `_inject_block`: created if absent · only the `_GUIDE_BEGIN.._GUIDE_END` region is (re)written if present · user content outside the markers preserved · `.bak` on a real change · idempotent (no-op + no .bak when unchanged).
  - D7 the pointer uses the SAME `_GUIDE_BEGIN/_GUIDE_END` markers as sync-guidelines, so a later `/add`→init→sync-guidelines REPLACES it in place — never a second/duplicate block.
  - D8 interactive (npm clack): a confirm/select STEP inside the existing preamble shows the detected agent and lets the user accept or override it BEFORE any file is written; cancel still writes nothing (exit 130). Rendered through the established clack `ui` layer (seeded delta), not a separate prompt stack.
  - D9 drops-files-only holds: detection + pointer-write run no `add.py init` and spawn no Python (no spawnSync / no mod.main); no state.json is created.
  - D10 npm↔pip parity: identical profile registry (same ids, signals, files, next-step wording), identical detection result for the same env, identical pointer semantics; only clack richness differs (pip prints the detected agent + uses input() confirm).
  - D11 designed-for-failure: an unwritable/undecodable integration file → warn + continue (the managed-layer drop already succeeded; exit stays 0); detection on a missing/empty env → generic.
</must>
Reject:
<reject>
  - the chosen integration file exists but is not valid UTF-8 (e.g. a UTF-16 CLAUDE.md) -> "integration_unreadable" (warn + skip the pointer write, leave the file byte-identical; the drop still succeeds, exit 0)
  - the chosen integration file / its dir is unwritable (read-only FS) -> "integration_unwritable" (warn + continue; exit 0 — never abort the successful drop)
  # NOT a reject: an unknown agent is the generic-fallback path (D4), not an error.
</reject>
After:
<after>
  - after a drop, exactly one ADD-marked pointer exists in the detected agent's integration_file at the target root (created or refreshed in place), user content outside the markers intact; the closing output named that agent's exact next step; no state.json; the managed trees are unchanged by this step.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ D-A1 [contract] the per-agent ENV SIGNALS (CLAUDECODE for Claude, CODEX_*/OPENCODE_* for the others) are the right discriminators for "which agent is invoking the installer" — lowest confidence because each tool's exact env var is not authoritatively pinned and may change across releases; if wrong: an agent is mis-detected. Mitigation: detection is best-effort and NEVER harmful — the interactive confirm (D8) lets the human override, and every miss degrades to generic AGENTS.md (D4), which is exactly today's working behavior (proven agent-portable by test_agent_portability). The env-key table is data, refinable via a SPEC delta. (Accept.)
  ⚠ D-A2 [contract] a MINIMAL same-marker pointer (not the full block) is enough orientation at drop time — lowest because a non-Claude user sees only a short pointer until init runs. Mitigation: the pointer names `add.py status`/`guide`, which carry the full guidance via the CLI; init's sync-guidelines then supersedes it with the full block (D7). (Accept.)
  - [x] Claude Code / Claude app share ONE "claude" profile (CLAUDE.md + `/add`) — ADOPTED: no reliable signal distinguishes the desktop app from the CLI, and both use the skill + CLAUDE.md; the label names both.
  - [x] write only the DETECTED agent's single file at drop time (not both) — ADOPTED: matches "writes ITS integration file" (singular); init later writes both anyway, so nothing is lost.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: detect Claude Code from env                              # D1,D2
  Given the process env has CLAUDECODE=1
  When detectAgent(env) runs
  Then it returns the claude profile (integration_file CLAUDE.md, next_step names /add)

Scenario: detect a non-Claude CLI agent from env                  # D1,D3
  Given the process env signals Codex (CODEX_HOME set)
  When detectAgent(env) runs
  Then it returns the codex profile (integration_file AGENTS.md, next_step names AGENTS.md)

Scenario: unknown agent falls back to generic                     # D1,D4
  Given a process env with no known agent signal
  When detectAgent(env) runs
  Then it returns the generic profile (integration_file AGENTS.md, generic next_step)
  And the generic next_step wording is byte-identical to today's onramp line

Scenario: closing next-step is agent-specific                     # D5,D10
  Given a non-interactive install with CLAUDECODE=1
  When the installer finishes the drop
  Then the closing output names the claude profile's exact next step (/add)
  And the same env on npm and on pip prints the same next-step wording

Scenario: drop writes the detected agent's integration pointer    # D6,D7
  Given a non-interactive install with CLAUDECODE=1 in a fresh project
  When the installer finishes
  Then CLAUDE.md exists at the target root containing one ADD:BEGIN..ADD:END block
  And the block markers are byte-identical to sync-guidelines' markers

Scenario: pointer is idempotent and preserves user content        # D6,D7
  Given a project whose AGENTS.md has user prose plus a prior ADD pointer block
  When a generic install reconciles the pointer
  Then only the marked region is rewritten, the user prose is intact
  And re-running the install a second time changes nothing and writes no new .bak

Scenario: init supersedes the drop-time pointer                   # D7
  Given an installed project carrying the minimal drop-time pointer in CLAUDE.md
  When add.py sync-guidelines runs
  Then the marked region is replaced in place by the full guideline block
  And there is exactly one ADD:BEGIN in the file (no duplicate block)

Scenario: interactive confirm can override the detection          # D8
  Given an interactive (clack) install where Codex is detected
  When the user picks "claude" at the agent-confirm step
  Then the claude profile drives the next-step and the CLAUDE.md pointer
  And a cancel at that step writes nothing and exits 130

Scenario: detection + pointer run no init and no Python spawn      # D9
  Given any install path
  When the installer detects + writes the pointer
  Then no add.py init runs, no subprocess is spawned, and no state.json is created

Scenario: an undecodable integration file is left untouched       # Reject integration_unreadable
  Given the target's CLAUDE.md is non-UTF-8 (UTF-16 bytes)
  When a claude install tries to write the pointer
  Then it warns and skips, the file is byte-identical, and the install still exits 0

Scenario: an unwritable integration file does not abort the drop  # Reject integration_unwritable
  Given the target root is read-only for the integration file
  When the installer tries to write the pointer
  Then it warns and continues, the managed-layer drop is intact, and exit is 0
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
AGENT PROFILE  { id, label, integration_file, next_step }
  shared registry, IDENTICAL in cli.js (AGENT_PROFILES) and _installer.py (AGENT_PROFILES).
  ORDERED; detectAgent walks it top→bottom, first match wins, generic is the last entry.

AGENT_PROFILES (ordered):
  claude   label "Claude Code / Claude app"  file ".claude"→CLAUDE.md
           detect: env CLAUDECODE truthy  OR  env CLAUDE_CODE_ENTRYPOINT set
           next_step: "Open Claude Code and run `/add` — the skill drives intake → milestone → build."
  codex    label "Codex"                    file AGENTS.md
           detect: env CODEX_HOME set  OR  any env key matching /^CODEX_/
           next_step: "Open Codex — it reads AGENTS.md; run `/add` or say what you want to build."
  opencode label "OpenCode"                 file AGENTS.md
           detect: env OPENCODE set  OR  any env key matching /^OPENCODE/
           next_step: "Open OpenCode — it reads AGENTS.md; say what you want to build."
  generic  label "your AI agent"            file AGENTS.md
           detect: always (fallback)
           next_step: <TODAY'S EXACT onramp line — byte-identical: "open your AI Agent CLI
                       (like Claude Code, Codex, etc.), then run `/add`, and say what you want to build…">

detectAgent(env) -> profile            # pure, deterministic, total; never throws
  _detect_agent(env) is its pip twin; same registry, same result for the same env.

writeAgentPointer(target, profile) -> "created"|"updated"|"unchanged"|"skipped"
  _write_agent_pointer(target, profile) is its pip twin. Writes POINTER into
  <target>/<profile.integration_file>, mirroring add.py:_inject_block:
    - markers: the SAME _GUIDE_BEGIN / _GUIDE_END constants sync-guidelines uses
    - POINTER body (minimal, transitional): names the project as ADD + the bootstrap
      commands `python3 .add/tooling/add.py status` and `… guide`, plus profile.next_step
    - present file: replace only the marked region; preserve content outside the markers
    - absent file: create with the block; unchanged on-disk match: no write, no .bak
    - real change: write <file>.bak first (rollback), then the new content
    - OSError / UnicodeDecodeError -> warn + return "skipped" (file untouched)  [integration_unreadable | integration_unwritable]

install flow (both twins; drops-files-only — no init, no Python spawn):
  profile = detectAgent(env)            # interactive: a clack confirm/select STEP may override it
  reconcile(...) (managed-layer drop, unchanged from heal-reconcile)
  writeAgentPointer(target, profile)    # the integration file
  print closing: profile.next_step      # the agent-specific next step

interactive (npm clack) — a STEP in runClackPreamble (rendered via the clack ui layer):
  show detected profile.label; clack.select/confirm lets the user keep or change it;
  isCancel -> { cancelled:true } -> exit 130, nothing written (unchanged cancel contract).
  pip: print the detected label (no clack); input() confirm stays the single pip prompt.

State / schema: NO state.json, NO .add/ writes by this step. Only the chosen root-level
  integration file (AGENTS.md or CLAUDE.md) is created/updated (+ a .bak on change).
  _INIT_EXCLUDE already treats AGENTS.md/CLAUDE.md as tool-owned, so a drop-time write
  never flips a greenfield brownfield-detection.

errors (both non-fatal — the managed drop already succeeded; exit stays 0):
  integration_unreadable -> warn "could not write <file> — <err>; skipped", file byte-identical
  integration_unwritable -> warn "could not write <file> — <err>; skipped", drop intact
```

Least-sure flag surfaced at freeze:
  ⚠ [contract] the per-agent ENV SIGNALS (CLAUDECODE · CODEX_* · OPENCODE_*) may not match what each tool actually sets — a mis-detect is possible. Accepted because detection NEVER fails harmfully: the interactive confirm overrides it and every miss degrades to the generic AGENTS.md path that works today (test_agent_portability proves agent-portability); the env table is data, refinable via a SPEC delta.
  ⚠ [contract] a drop-time pointer is a SECOND (minimal) writer of an ADD block beside Python's sync-guidelines — risk = duplication/drift. Accepted because it reuses the SAME _GUIDE_BEGIN/_GUIDE_END markers, so init's sync-guidelines replaces it in place (one block, no duplicate — pinned by test_init_supersedes_pointer).

Status: FROZEN @ v1 — approved by Tin Dang (full-auto mode delegated 2026-06-17; open assumptions resolved: one folded "claude" profile · single detected-file write — both adopted)
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: behavior-complete across the 11 scenarios. pip is hermetic (detection takes an
explicit `env` dict; `install(bundled=…)` reuses heal-reconcile's synthetic-bundle hook + a `target`).
npm uses subprocess with an injected env (skips honestly without node). Detection is env-injected, so
no test depends on a real agent being present.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_detect_claude_from_env_pip: _detect_agent({"CLAUDECODE":"1"}) -> id=="claude", integration_file=="CLAUDE.md", "/add" in next_step (D1,D2).
  - test_detect_codex_from_env_pip: _detect_agent({"CODEX_HOME":"/x"}) -> id=="codex", file=="AGENTS.md", "AGENTS.md" in next_step (D1,D3).
  - test_unknown_falls_back_to_generic_pip: _detect_agent({}) -> id=="generic", file=="AGENTS.md"; next_step byte-equals the captured generic onramp line (D1,D4).
  - test_closing_next_step_is_agent_specific_pip: install(bundled, target, env={"CLAUDECODE":"1"}), capture stdout / closing names "/add" (D5).
  - test_drop_writes_pointer_pip: install(env CLAUDECODE) in fresh target / CLAUDE.md exists with exactly one _GUIDE_BEGIN..._GUIDE_END region (D6,D7).
  - test_pointer_idempotent_preserves_user_content_pip: AGENTS.md = user prose + prior pointer / generic install / only marked region rewritten, prose intact, 2nd run -> "unchanged" + no new .bak (D6,D7).
  - test_init_supersedes_pointer_pip: minimal project with a drop-time pointer in CLAUDE.md / add.main(["sync-guidelines"]) / full block present, exactly one _GUIDE_BEGIN (D7).
  - test_no_init_no_spawn_no_state_pip: install(env) / no state.json created; (structural) cli.js has no spawnSync, _installer.py no mod.main (D9).
  - test_undecodable_integration_left_untouched_pip: CLAUDE.md = UTF-16 bytes / install(env CLAUDECODE) / file byte-identical, return 0, warn emitted (Reject integration_unreadable).
  - test_unwritable_integration_does_not_abort_pip: monkeypatch the pointer write to raise OSError / install / managed drop intact, return 0 (Reject integration_unwritable).
  - test_detect_claude_from_env_npm: subprocess init --yes with env CLAUDECODE=1 / CLAUDE.md written + closing names /add (D2,D5,D10) [skipUnless node].
  - test_unknown_generic_npm: subprocess init --yes with a scrubbed env / AGENTS.md written + generic closing line (D4,D10) [skipUnless node].
  - test_parity_profiles: cli.js + _installer.py expose the same profile ids (claude·codex·opencode·generic), the same integration_file per id, and the same next-step keywords (/add, AGENTS.md) (D10 structural).
  # interactive override (D8) is reached via the ADD_INSTALLER_FORCE_INTERACTIVE seam where feasible;
  # the clack happy path is branch-reachability + (if a PTY helper lands) a probe, mirroring installer-prompts.
</test_plan>

Tests live in: `add-method/tooling/test_agent_detect.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/bin/cli.js` `add-method/src/add_method/_installer.py` `add-method/tooling/test_agent_detect.py` `add-method/tooling/test_installer_handoff.py`
  (NO add.py change — sync-guidelines/_inject_block already exist and are only READ/reused; the pointer
   re-uses their `_GUIDE_BEGIN/_GUIDE_END` markers, which the JS/pip twins re-declare as local constants.)
  test_installer_handoff.py is a COMPANION edit: the flagless-install handoff tests inherited the
  ambient agent env (CLAUDECODE under Claude Code) and so saw the now-agent-aware handoff; scrubbed
  the agent signal in their runners so they deterministically pin the GENERIC baseline handoff (the
  generic-wording guard is preserved, not weakened — agent-specific paths are covered by test_agent_detect; see §6 SEMANTIC).
Strategy (ordered batches): 1. add the shared `AGENT_PROFILES` registry + pure `detectAgent(env)`/`_detect_agent(env)` (env param; generic last) → 2. add `writeAgentPointer`/`_write_agent_pointer` mirroring _inject_block (markers, created/updated/unchanged/.bak, fail-soft) → 3. wire the install flow: detect → reconcile → write pointer → print profile.next_step → 4. npm interactive: a clack confirm/select STEP in runClackPreamble (override + cancel-safe); pip prints the detected label.
Safety rule (feature-specific): the closing region (after "Done.") MUST still literally contain the generic onramp line so `test_v8_install` closing-hint guards stay green — print the generic literal as the default branch and override with profile.next_step only for a non-generic detected agent; never let detection or the pointer write throw (catch → warn → continue, exit 0); no Python spawn, no init.
Code lives in: `add-method/` (the package — NOT this task's `./src/`).
Constraints: do NOT change any test or the contract; no new dependency (clack already present); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — agent-detect suite 16/16 (incl. 2 npm subprocess + parity + init-supersedes); full suite **1242 OK**
- [x] coverage did not decrease — +16 new tests; no test removed (test_installer_handoff runners scrubbed agent env — intent preserved, see SEMANTIC)
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; the §4 suite re-anchored cleanly at the tests→build re-cross (after the in-build idempotent-test correction + the companion handoff edit)
- [x] the green was EARNED, not gamed — detection asserts real profile dicts from real env; pointer asserts real on-disk markers/idempotency/.bak/preserved-content; init-supersedes calls the REAL add_engine._inject_block (drift in the markers → 2 BEGINs → fail); npm tests spawn real node + assert the real written file + stdout. No stubs, no vacuous asserts
- [x] concurrency / timing of the risky operation is safe — detection is pure; the pointer write is synchronous + fail-soft (warn→skip), never partial-aborts the managed drop that precedes it (proven by test_unwritable_pointer_does_not_abort_drop)
- [x] no exposed secrets, injection openings, or unexpected dependencies — env is READ-only for detection (never echoed into the written file); no new dependency (clack already present); the pointer body is a fixed template + the profile's own next_step
- [x] layering & dependencies follow CONVENTIONS.md — npm↔pip parity held (same profile ids/files/signals/markers; ParityTest + the structural parity test pin it); drops-files-only + no-Python-spawn + no state.json all preserved
- [x] a person reviewed and approved the change — full-auto mode delegated by Tin Dang (2026-06-17); careful manual diff review + earned-green refute-read done; auto-resolved PASS (no security/concurrency/architecture residue). DISCLOSED GAP below is non-security, accepted for mvp.

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — every new symbol referenced: `AGENT_PROFILES`/`detectAgent`/`writeAgentPointer`/`agentPointerBlock`/`profileMatches`/`GUIDE_BEGIN/END` (cli.js) wired into `cmdInit`→`runClackPreamble`→`dropFiles`; `AGENT_PROFILES`/`_detect_agent`/`_write_agent_pointer`/`_agent_pointer_block`/`_profile_matches`/`_GUIDE_BEGIN/END` (_installer.py) wired into `install()`; `env` param threaded from tests
- [x] DEAD-CODE (code) — no orphaned symbol; every helper has a caller (verified by grep + the wiring above)
- [x] SEMANTIC (prose / non-code) — TWO disclosures (show-before-ask):
      (1) DISCLOSED GAP — D8 the interactive clack agent-SELECT step is reachable only via a real PTY (clack raw-mode; `runClackPreamble` returns cancelled before the prompt when stdin isn't a TTY, so the force-seam can't reach it — same limit installer-prompts hit). The select step is implemented + node-syntax-checked + follows the EXACT established clack text/confirm pattern, and the detection LOGIC it surfaces is fully unit-tested; the executing gap is the TUI keystroke path only. Accepted for mvp; seeded as a §7 SPEC delta (a reusable PTY helper closes it — the open installer-prompts PTY-helper delta).
      (2) COMPANION EDIT — test_installer_handoff.py: scrubbed the agent-signal env (CLAUDECODE/CODEX_*/OPENCODE*) in its two flagless-install runners so they deterministically pin the GENERIC baseline handoff. NOT a weakening — the generic-wording guard is preserved exactly; the test now tests the no-agent baseline it was always meant to, and the agent-specific handoff has its own coverage in test_agent_detect. Declared in §5 scope.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang (full-auto mode delegated 2026-06-17) · date: 2026-06-17

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): per-agent detection rate vs generic-fallback rate (signal accuracy); integration_unreadable/unwritable skip rate; pointer created-vs-superseded ratio at init.

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`).

- [SPEC · seeded] [→ pty-clack-harness] extract a reusable PTY test helper that drives clack select/confirm so the interactive agent-select step (D8) is covered in CI (evidence: D8 disclosed as PTY-only-reachable at the gate; consolidated with the installer-prompts PTY-helper delta into the installer-smarts-polish task pty-clack-harness — flipped by hand because this task is archived out of the live state registry, so `--from-delta` could not reach it)
- [SPEC · carried] widen the agent registry to Cursor + Copilot (.cursor/rules · .github/copilot-instructions.md) with their own integration files (evidence: the user's "etc." in the ask; the milestone scoped only claude/codex/opencode/generic for mvp) [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]
- [SPEC · carried] confirm the real env signals each agent sets (CODEX_*/OPENCODE*) against their shipping CLIs and pin them (evidence: D-A1 accepted at freeze as best-effort, refinable data) [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence.

- [ADD · folded] "detect + auto-correct the agent" splits cleanly into a PURE detect (unit-testable) + a fail-soft WRITE (mirror the existing marker-injector, same markers so the canonical writer supersedes it) — never a second source of truth for the block (evidence: test_init_supersedes_pointer proves sync-guidelines replaces the drop-time pointer in place) [folded foundation-version 38]
- [TDD · folded] a test that inherits the ambient agent env (CLAUDECODE under Claude Code) silently changes behavior between local and CI — scrub the signal to pin the intended scenario deterministically (evidence: test_installer_handoff passed in CI but failed locally until its runners scrubbed the agent env) [folded foundation-version 38]
- [ADD · folded] env-signal detection should degrade to a SAFE default that equals prior behavior, so a wrong guess is never harmful — gate the feature on graceful fallback, not signal accuracy (evidence: every unmatched env → the generic AGENTS.md path proven agent-portable by test_agent_portability) [folded foundation-version 38]
