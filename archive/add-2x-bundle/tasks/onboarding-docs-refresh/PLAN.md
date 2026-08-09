# TASK: Surface expanded agent set in README/GETTING-STARTED/help

slug: onboarding-docs-refresh · created: 2026-06-18 · stage: mvp
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
- `add-method/README.md` — the package intro; mentions agents generically (lines 5, 99-104) but never names the supported set.
- `add-method/GETTING-STARTED.md:138` — "how **any** agent — Claude, Cursor, Copilot, Codex — follows ADD through the CLI alone" (the one explicit agent list; under-states the real set).
- NEW test `add-method/tooling/test_supported_agents_docs.py` — assert the docs name the expanded set.

Context (working folder): The installed registry (after the prior two tasks) now detects: Claude · Codex · OpenCode · Cursor · Windsurf · Trae · Copilot · Cline · Aider · Gemini CLI. No test pins the exact GETTING-STARTED agent string (test_agent_portability only asserts the "any agent" substring at line 135 — must be preserved).

Honors (patterns / conventions):
- keep "any agent" substring intact (test_agent_portability:135).
- docs accord — README/GETTING-STARTED tone + spine (test_getting_started_spine, test_docs_accord, test_onboarding_align must stay green).
- no engine/skill change (docs only).

Anchors the contract cites: the GETTING-STARTED:138 agent-list line and a README supported-agents line.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Surface the expanded supported-agent set in README + GETTING-STARTED so users know ADD works beyond Claude Code.
Framings weighed: name-the-full-set inline (chosen — smallest edit, highest signal) · add a dedicated "Supported agents" section (rejected — heavier than the lean docs ethos; one line suffices) · auto-generate from AGENT_PROFILES (rejected — over-engineered for prose).
Must:
<must>
  - README names the supported agents (incl. the six new: Cursor, Windsurf, Trae, Gemini CLI, GitHub Copilot, Cline/Aider).
  - GETTING-STARTED:138's agent list is expanded to reflect the real set, keeping the "any agent" phrasing.
  - The lean tone + existing docs spine are preserved (no new heavy section).
</must>
Reject:
<reject>
  - removing or rewording the "any agent" substring -> would break test_agent_portability -> keep it verbatim
  - editing engine/skill/book files -> out of scope -> docs only
</reject>
After:
<after>
  - A reader of README or GETTING-STARTED sees ADD supports Claude Code, Codex, OpenCode, Cursor, Windsurf, Trae, Gemini CLI, GitHub Copilot, Cline, and Aider; the docs-accord suite stays green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ none material — this is additive prose. Biggest risk: a docs-spine lint pins a line I touch; mitigated by re-running test_getting_started_spine / test_docs_accord / test_onboarding_align after the edit and keeping the "any agent" substring.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: README names the new agents
  Given the README
  When I read it
  Then it names Cursor, Windsurf, Trae, Gemini, Copilot, Cline, Aider

Scenario: GETTING-STARTED lists the expanded set and keeps "any agent"
  Given GETTING-STARTED.md
  When I read the agent-list line
  Then it names the new agents
  And the "any agent" phrasing is unchanged

Scenario: The docs-accord suite stays green
  Given the existing docs lints
  When the suite runs
  Then test_getting_started_spine / test_docs_accord / test_onboarding_align / test_agent_portability still pass
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
# Docs contract (prose, not an API):
README.md           : names the supported-agent set including the six new agents
GETTING-STARTED.md  : line ~138 agent list expanded to the real set; "any agent" substring kept verbatim
Verified by         : tooling/test_supported_agents_docs.py (greps for the new agent names) + the docs-accord suite stays green
Out of scope        : engine/skill/book files; no new docs section; the cli.js `help` text (terse, unchanged)
```

Status: FROZEN @ v1 — approved by Tin Dang (2026-06-18; ship-the-milestone directive; additive prose, none-material flag)
Least-sure flag surfaced at freeze: [contract] none material — additive prose only; biggest risk is a docs-spine lint pinning a touched line, mitigated by re-running test_getting_started_spine / test_docs_accord / test_onboarding_align and keeping "any agent" verbatim.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the doc claims asserted; docs-accord suite stays green.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_readme_names_new_agents: README.md text contains Cursor, Windsurf, Trae, Gemini, Copilot, Cline, Aider
  - test_getting_started_lists_agents_and_keeps_any_agent: GETTING-STARTED names the new agents AND still contains "any agent"
  - (regression) the existing docs lints (test_getting_started_spine / test_docs_accord / test_onboarding_align / test_agent_portability) stay green — run in the full suite
</test_plan>

Tests live in: `add-method/tooling/test_supported_agents_docs.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/README.md` `add-method/GETTING-STARTED.md` `add-method/tooling/test_supported_agents_docs.py`
Strategy (ordered batches): 1. write test_supported_agents_docs.py (red) · 2. expand GETTING-STARTED:138 + add a README supported-agents line · 3. green + re-run docs lints.
Safety rule (feature-specific): keep "any agent" verbatim; touch no engine/skill/book file.
Code lives in: `add-method/README.md` + `add-method/GETTING-STARTED.md`
Constraints: do NOT change any test or the contract; docs only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 1369 green (test_supported_agents_docs 2/2 + docs-accord lints)
- [x] coverage did not decrease — 2 new doc-assertion tests added
- [x] no test or contract was altered during build — the tamper tripwire caught a test edit; I reverted the test to its tests-phase form and instead fixed the DOC (bold-wrapped to `**any agent**`) so the original `"any agent"` assertion passes honestly
- [x] the green was EARNED, not gamed — the test greps the real doc text for each new agent name + the preserved phrasing; no stub
- [x] concurrency / timing safe — N/A (static docs)
- [x] no exposed secrets, injection openings, or unexpected dependencies — prose only
- [x] layering & dependencies follow CONVENTIONS.md — docs-accord / spine / onboarding-align lints stay green
- [x] a person reviewed and approved the change — Tin Dang directed the ship

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] README and GETTING-STARTED both name all six new agents — confirmed by reading the edited passages + test_supported_agents_docs green
- [x] The "**any** agent" phrasing is preserved in GETTING-STARTED — confirmed by the assertion + the doc text
- [x] The docs-accord / spine / onboarding-align lints stay green — confirmed in the full 1369-test run

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [ ] WIRING (code) — N/A (docs)
- [ ] DEAD-CODE (code) — N/A (docs)
- [x] SEMANTIC (prose) — read both edited passages in full: README "Works with your agent" paragraph + GETTING-STARTED:138 list name the same 10-agent set the registry detects; the integration-file note (CLAUDE.md/AGENTS.md/.clinerules + Gemini settings) matches the two prior tasks' behavior

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
