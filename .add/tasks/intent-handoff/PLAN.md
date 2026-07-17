# TASK: Build-intent note handoff to /add (never init)

slug: intent-handoff · created: 2026-06-18 · stage: mvp
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
  - `bin/cli.js:runClackPreamble(...)` — the interactive sequence (target → scope → agent). The intent prompt is the LAST, OPTIONAL step; its value rides back on the outcome as `intent`.
  - `bin/cli.js:dropFiles(args, target, profile)` — drops `.add/` then writes the agent pointer. The intent note is written here, AFTER the drop, so `.add/` exists. NEW `writeIntentNote(target, intent)`.
  - `bin/cli.js:cmdInit(args)` — threads `outcome.intent` into `dropFiles`.
  - `src/add_method/_installer.py:install(...)` interactive block + the drop — captures the intent (interactive only), writes `.add/.intent` after the drop. NEW `_prompt_intent()` + `_write_intent_note(target, intent)`.
  - `skill/add/SKILL.md` (+ 2 parity copies `.claude/skills/add/SKILL.md`, `src/add_method/_bundled/skill/add/SKILL.md`) — the autonomous-setup bullet: `/add` reads `.add/.intent` (if present) to seed its kickoff suggestion. A NOTE, never an init trigger.
Context (working folder):
  - the module headers of BOTH twins (cli.js lines 13-16 · _installer.py lines 3-6) — the DEFERRED-INIT invariant: the installer DROPS FILES ONLY, never runs `add.py init` (a pre-run init grandfather-locks the v12 gate + burns the brownfield signal). The `.intent` note must NOT break this — it persists the build-intent signal WITHOUT running init.
  - `phases/0-setup.md` step 2 (the kickoff suggestion) — where `/add` uses the `.intent` hint; SKILL.md points at it.
  - `tooling/test_installer_prompts.py` / `test_onboarding_brand.py` / `test_readiness_detect.py` — pip-interactive tests now feed `"\nn\n"` (target, scope); the intent prompt being EOF-tolerant (skip on exhausted stdin) means they need NO further stdin.
  - `tooling/test_global_scope.py` — its `_Script` raises on extra input() calls; the new (optional) intent prompt adds a trailing call, so `_Script` must become EOF-tolerant (raise EOFError when exhausted → intent skips) + the explicit-flag test asserts "scope prompt absent" instead of call-count==1.
Honors (patterns / conventions):
  - DEFERRED-INIT is sacred: write a NOTE only; NEVER exec `add.py`/init; no state.json is created by the installer (test_installer_handoff pins this).
  - the intent prompt is INTERACTIVE-ONLY + FULLY OPTIONAL: EOF / empty / Ctrl-C → skip (no note, install still succeeds, never a cancel) — so it never breaks the non-interactive boundary or rejects a valid install.
  - twin decision-equivalence; engine add.py untouched (ENGINE_MD5); non-interactive stdout byte-identical; the 3 skill trees stay md5-equal (parity test).
Anchors the contract cites:
  - `_prompt_intent()` / the npm intent prompt → returns the one-line intent or "" (skip); EOF/empty/interrupt → "".
  - `_write_intent_note(target, intent)` / `writeIntentNote(target, intent)` → writes `<target>/.add/.intent` IFF intent is non-empty; returns whether written; never touches state.json.
  - the SKILL.md autonomous-setup line that makes `/add` read `.add/.intent`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: an optional one-line "what do you want to build first?" capture in the INTERACTIVE installer that writes a NOTE (`.add/.intent`) for `/add` to read — WITHOUT running init (deferred-init invariant preserved).
Framings weighed: a last optional interactive prompt that writes a `.add/.intent` note + a SKILL.md line so `/add` reads it (chosen) · run `add.py init` with the intent as the project goal (REJECTED — grandfather-locks the v12 gate + burns the brownfield signal, the exact failure the deferred-init invariant exists to prevent) · stash the intent in an env var / stdout only (rejected — ephemeral; the AI never sees it across the terminal boundary, which is why a persisted note is needed).
Must:
<must>
  - Add a LAST, OPTIONAL interactive prompt ("What do you want to build first? (optional — Enter to skip)"); a non-empty answer writes `<target>/.add/.intent` containing that one line; empty/skip writes nothing.
  - The prompt is FULLY OPTIONAL + fail-soft: EOF / empty / Ctrl-C → skip (return ""), the install still SUCCEEDS (exit 0) — the intent prompt never cancels a valid install and never blocks the drop.
  - The note is written AFTER the per-project drop (so `.add/` exists) and ONLY persists text — the installer NEVER runs `add.py`/init and NEVER creates state.json (the deferred-init invariant is pinned and must stay green).
  - `/add` reads `.add/.intent` (if present) at autonomous setup to SEED its kickoff suggestion — as a NOTE/hint, explicitly NOT a trigger to init. Wire this in SKILL.md (+ the 2 parity copies, kept md5-equal).
  - INTERACTIVE-ONLY: a non-interactive / `--yes` / CI run shows no intent prompt and writes no `.add/.intent`; the non-interactive stdout stays byte-identical.
  - Both twins decision-equivalent; engine add.py untouched (ENGINE_MD5); the write helper is a pure, testable seam (writes iff non-empty; returns whether written).
</must>
Reject:
<reject>
  - empty / whitespace-only / skipped / EOF / Ctrl-C at the intent prompt -> NO note written, install still succeeds -> "intent_skipped_no_note"
  - a non-interactive / `--yes` / CI run -> NO intent prompt, NO `.add/.intent` -> "noninteractive_no_intent"
  - the installer running init or creating state.json from the intent -> NEVER (the note is inert text; deferred-init holds) -> "intent_never_inits"
</reject>
After:
<after>
  - After an interactive install where the user typed an intent, `<target>/.add/.intent` holds that one line, no state.json exists, and a later `/add` reads it to seed the first-milestone kickoff.
  - After a skip / non-interactive install, no `.add/.intent` exists and the install is byte-identical to today.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ Making the intent prompt EOF/empty/Ctrl-C → SKIP (never cancel) is the correct optionality. Lowest confidence because a Ctrl-C is usually "abort" elsewhere in this flow (target/scope cancel → 130); if wrong: a user who Ctrl-C's at the intent step expecting to abort instead gets a completed install. Mitigation: the intent step is the LAST thing AFTER the successful drop — the install has already succeeded, so "skip the optional note" is the only sane meaning; the earlier (pre-write) prompts keep their cancel semantics.
  - [ ] a NOTE (not init) is the right handoff — confirm: a pre-run init grandfather-locks the v12 gate + burns the brownfield signal (the documented invariant); a persisted note is the only way the intent survives to where `/add`/the AI reads it.
  - [ ] `.add/.intent` (raw one line) is enough for `/add` — confirm: the AI reads it verbatim as the kickoff seed; no structured schema needed (a header comment is optional polish, not required).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: intent typed writes the note (no init)
  Given an interactive install
  When the user types "a todo app" at the intent prompt
  Then <target>/.add/.intent contains "a todo app"
  And no .add/state.json exists (the installer never inits)

Scenario: write helper is pure  (no-empty / non-empty)
  Given the write helper _write_intent_note(target, text)
  When called with non-empty text / with empty-or-whitespace text
  Then it writes <target>/.add/.intent and returns truthy / writes nothing and returns falsy
  And it never creates or reads state.json

Scenario: skipped intent writes nothing  (Reject: intent_skipped_no_note)
  Given an interactive install
  When the user presses Enter (or EOF / Ctrl-C) at the intent prompt
  Then no .add/.intent file is created
  And the install still succeeds (exit 0)

Scenario: non-interactive writes no intent  (Reject: noninteractive_no_intent)
  Given a --yes / non-interactive / piped install
  When init runs
  Then no intent prompt is shown and no .add/.intent is written
  And the brain still lands (per-project drop) with no state.json

Scenario: the installer never inits from intent  (Reject: intent_never_inits)
  Given any install, with or without an intent
  When init completes
  Then no .add/state.json exists (deferred-init invariant holds)
  And the agent never has the v12 lock-down gate grandfather-locked

Scenario: /add reads the note  (skill wiring)
  Given the SKILL.md autonomous-setup guidance (all 3 trees)
  When inspected
  Then it instructs /add to read .add/.intent (if present) as a kickoff seed, a NOTE not an init trigger
  And the 3 SKILL.md trees stay md5-equal
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
# pip — src/add_method/_installer.py
_prompt_intent() -> str            # interactive prompt; one-line intent, or "" on empty/EOF/Ctrl-C (skip, never cancel)
_write_intent_note(target, intent) -> bool      # writes <target>/.add/.intent IFF intent.strip(); returns written?
install(...) interactive block: capture intent (after the scope step); AFTER the drop -> _write_intent_note(target, intent)

# npm — bin/cli.js
runClackPreamble(...) -> { ..., intent }         # LAST optional prompt; clack cancel/empty -> intent:""
writeIntentNote(target, intent) -> bool          # twin of _write_intent_note
cmdInit: thread outcome.intent -> dropFiles(args, target, profile, intent); dropFiles writes the note after writeAgentPointer

# skill — SKILL.md (+ .claude/skills/add/SKILL.md + src/add_method/_bundled/skill/add/SKILL.md, md5-equal)
autonomous-setup bullet: "if .add/.intent exists, read it (the one-line first-build intent the user gave the
installer — a NOTE, never an init trigger) and let it seed your kickoff suggestion" — BEFORE running init.

INVARIANTS:
  - DEFERRED-INIT: the installer writes a NOTE only — never execs add.py/init, never creates state.json -> intent_never_inits
  - INTERACTIVE-ONLY + OPTIONAL: no prompt & no note on --yes/CI; EOF/empty/Ctrl-C -> skip, exit 0 -> intent_skipped_no_note / noninteractive_no_intent
  - non-interactive stdout byte-identical; add.py untouched (ENGINE_MD5); 3 SKILL.md trees md5-equal
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-18
Least-sure flag surfaced at freeze: [spec] EOF/empty/Ctrl-C at the intent prompt → SKIP (exit 0), NOT cancel — chosen because the intent step runs AFTER the successful drop, so "skip the optional note" is the only coherent meaning; the earlier pre-write prompts (target/scope) keep cancel→130.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + every Reject + the skill wiring has a test (11 tests).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_writes_when_nonempty / test_skips_when_empty_or_whitespace: _write_intent_note pure — writes .add/.intent iff non-empty; never creates state.json
  - test_eof_returns_empty_string / test_keyboard_interrupt_returns_empty_string: _prompt_intent skips (returns "") on EOF / Ctrl-C (never raises, never cancels)
  - test_typed_intent_writes_note_and_never_inits: interactive [target, scope, "a todo app"] → .add/.intent == it AND no state.json
  - test_skipped_intent_writes_nothing: interactive [target, scope, ""] → no .intent, exit 0, per-project drop still ran
  - test_noninteractive_no_intent_no_state: --non-interactive → no prompt, no .intent, no state.json, brain landed
  - test_writeIntentNote_writes_when_nonempty (npm node harness) + test_yes_run_writes_no_intent (npm subprocess)
  - test_skill_instructs_add_to_read_intent + test_three_skill_trees_md5_equal: all 3 SKILL.md mention .add/.intent and stay byte-identical
</test_plan>
Hermetic: pip in-process (FORCE seam + mock input side_effect, injected HOME); npm via the node harness (writeIntentNote side-effect) + a `--yes` subprocess.

Tests live in: `add-method/tooling/test_intent_handoff.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/bin/cli.js` `add-method/src/add_method/_installer.py` `add-method/skill/add/SKILL.md` `.claude/skills/add/SKILL.md` `add-method/src/add_method/_bundled/skill/add/SKILL.md` `add-method/tooling/test_global_scope.py`   <the two twins + the 3 md5-equal SKILL.md trees (dogfood · canonical · bundle) + the task-3 test whose _Script must become EOF-tolerant for the new optional prompt>
Strategy (ordered batches): 1. pip `_write_intent_note` (pure) + `_prompt_intent` (EOF/empty→"") 2. wire pip: capture intent in the interactive block, write note after the drop 3. npm `writeIntentNote` + intent prompt in runClackPreamble (outcome.intent) + thread through cmdInit→dropFiles 4. SKILL.md autonomous-setup reads `.add/.intent` — edit all 3 trees identically (keep md5-equal) 5. make test_global_scope's `_Script` EOF-tolerant (raise EOFError when exhausted) + switch the explicit-flag assertion to "scope prompt absent".
Safety rule (feature-specific): DEFERRED-INIT is sacred — write a NOTE only, NEVER exec add.py/init, NEVER create state.json. The intent prompt is the LAST, OPTIONAL step (EOF/empty/Ctrl-C → skip, exit 0, never cancel). Non-interactive stays byte-identical; the 3 SKILL.md trees stay md5-equal.
Code lives in: the two twins + the 3 SKILL.md trees.
Constraints: do NOT change the contract or weaken any assertion; no new dependency; add.py is never edited (ENGINE_MD5 holds); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 1319 OK (was 1308; +11 test_intent_handoff); the 3 sibling pip-interactive tests stay green UNCHANGED (the intent prompt is EOF-tolerant, so their `"\nn\n"` simply skips it)
- [x] coverage did not decrease — +11 tests over the new symbols + the skill wiring; the deferred-init pin (no state.json) + the non-interactive boundary still green
- [~] no test or contract was altered during build — THIS task's contract is FROZEN/untouched; its tests (test_intent_handoff.py) unchanged since red. DISCLOSED: test_global_scope.py (my own task-3 test, declared in §5) had its `_Script` made EOF-tolerant (raise EOFError when exhausted, modelling closed stdin) so the new OPTIONAL trailing prompt skips; its explicit-flag assertion became MORE precise ("scope prompt text absent" vs a raw call-count, which also fixed a latent `gscope-`-tempdir substring bug). Robustness, NOT weakening — no assertion dropped, no pin touched (engine-md5 + the non-interactive boundary in test_installer_prompts untouched)
- [x] the green was EARNED, not gamed — real behavior: a typed intent writes `.add/.intent` AND no state.json (deferred-init); skip/EOF/Ctrl-C/non-interactive write nothing; the npm helper writes via the node harness; `--yes` writes no note (subprocess); the 3 SKILL.md trees are asserted md5-equal AND to contain `.add/.intent`
- [x] concurrency / timing of the risky operation is safe — a single synchronous prompt + one local file write, both fail-soft (a write error is swallowed; the note never blocks a successful install); no network, no shared state
- [x] no exposed secrets, injection openings, or unexpected dependencies — the note is the user's own typed text written to a fixed path under the chosen target (no shell, no eval); no new dependency; add.py untouched (ENGINE pin)
- [x] layering & dependencies follow CONVENTIONS.md — twins decision-equivalent; DEFERRED-INIT honored (NOTE only, no add.py exec, no state.json); the skill change is the contracted `/add` read-side, kept md5-equal across 3 trees
- [x] a person reviewed and approved the change — auto-resolved under `autonomy: auto`: no security/concurrency/architecture residue and NO frozen-pin file touched (unlike task 3); the one test edit is a disclosed robustness change to my own task-3 test. Live smoke confirmed both twins (intent→note+no-state.json; --yes→no note)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_prompt_intent`/intent prompt captured in install()/runClackPreamble; `_write_intent_note`/`writeIntentNote` called after the drop (pip) / in dropFiles after writeAgentPointer (npm); cmdInit threads `outcome.intent`→dropFiles; npm `writeIntentNote` exported for the harness; SKILL.md (×3) autonomous-setup reads `.add/.intent`
- [x] DEAD-CODE (code) — no orphans: every new symbol referenced (prompts by install/preamble; write helpers by the drop + tests; the export by the node harness)
- [x] SEMANTIC (prose) — read the SKILL.md autonomous-setup edit in full across all 3 trees: it instructs `/add` to read `.add/.intent` as a NOTE that seeds the kickoff, explicitly NOT an init trigger — consistent with the deferred-init invariant; the 3 trees are byte-identical

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang (auto-resolved, autonomy: auto — test edit disclosed, no frozen-pin touch) · date: 2026-06-18

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
- [TDD · folded] every NEW interactive prompt ripples into existing interactive tests that feed fixed stdin — make trailing OPTIONAL prompts EOF-tolerant (skip on exhausted stdin), so they don't re-break sibling tests (evidence: the scope step broke 3 sibling pip-interactive tests at EOF→cancel, needing a nav stdin edit; the intent step, made EOF→skip, broke none). [folded foundation-version 39]
- [ADD · folded] when a build legitimately ripples into sibling-test files, declare them in §5 and re-anchor (re-cross tests→build) BEFORE the gate; surface the ripple at the gate (human-confirm if it touches a frozen-pin file, auto-resolve otherwise) — never silently (evidence: global-first-scope touched test_installer_prompts' happy-path stdin → human-confirmed; intent-handoff touched only its own task-3 test → auto-resolved). [folded foundation-version 39]
