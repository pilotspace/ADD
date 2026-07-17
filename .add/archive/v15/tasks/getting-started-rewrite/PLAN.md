# TASK: GETTING-STARTED: the conversational path becomes the spine

slug: getting-started-rewrite · created: 2026-06-05 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower
     the dial with `autonomy: conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: GETTING-STARTED.md restructured so a newcomer reading top-to-bottom
  types exactly ONE command (the install) before their first verified feature —
  the conversational path (install → open Claude Code → /add → talk) is the
  whole spine; the by-hand seven-phase walk becomes a self-contained
  escape-hatch appendix (v15 exit criterion 1)
Framings weighed: full spine restructure (chosen: the v15 goal IS the
  perception flip — a light edit leaves the command walk reading as the main
  path) · light-touch edit of the fast-path section (rejected: the spine would
  still route the reader through new-task/advance by hand) · split into two
  docs (rejected: two files = two divergence surfaces; the escape hatch
  belongs beside the promise it backs)
Must:
  - Spine order: Prerequisites → Install (flagless-first examples + the
    handoff echo: "open Claude Code, type /add") → Your first feature — talk
    to the agent (the /add + transfer-money prompt · the four on-ramp steps
    Orient/Intake/One-approval/Self-driving · the On-ramp callout) → What
    just happened (status/guide framed as YOUR override + resume commands,
    not steps) → Resume next session → Self-check → Enforce the seams in CI →
    escape-hatch appendix → Where to read more.
  - The spine (all text BEFORE the escape-hatch heading) never asks the
    reader to type a phase-walk command: `add.py new-task` · `add.py advance`
    · `add.py gate` · `add.py stage` appear ONLY at/after the escape-hatch
    heading. (status · guide · check · audit stay in the spine as
    override/CI surfaces.)
  - The escape-hatch appendix is SELF-CONTAINED: it adds the `new-task`
    scaffold step and the stage-change command before the seven phase
    walkthroughs, so the by-hand path works without the old spine §3
    (golden spine: init → new-task → advance×5 → gate PASS stays executable).
  - UNION of shipped guards held (all pre-existing, must stay green):
    the 9 REQUIRED_STRINGS literals (npx @pilotspace/add init · pip install
    pilotspace-add · pilotspace-add init · add.py status/new-task/advance/
    gate PASS/check/guide) · `guide  :` exact (two spaces) · "talk to the
    agent" BEFORE "seven phases" · /add + "intake" + "milestone" before the
    phase-walk boundary (first of "## 4 "/"seven phases"/…) · a heading
    containing "under the hood" or "escape hatch" · "one-approval front"
    present · no stale-caveat strings · every `add.py <word>` a real
    subcommand.
  - ENGINE + skill untouched: this task edits ONLY add-method/GETTING-STARTED.md
    (file ownership: README + installers belong to installer-handoff).
Reject:
  - a phase-walk command in the spine -> test_spine_free_of_phase_walk_commands red
  - any shipped guard literal dropped -> the pre-existing suites go red (the union rule)
  - an `add.py <word>` that is not a real subcommand -> test_documented_commands_are_real red
  - edits outside GETTING-STARTED.md -> engine-md5/parity pins red; README diffs rejected at review
Assumptions — least-sure first:
  ⚠ [contract] the merged "Your first feature — talk to the agent" section
    satisfies BOTH lead-in guards at once (v8's boundary regex + onboarding-
    align's phrase order) — least sure because the boundary is the FIRST of
    four markers and a renumbered "## 4 " heading moves it; if wrong: a
    pre-existing guard goes red at build and the section order is shuffled
    (cost: one reflow, no contract change). Mitigated: both guard mechanics
    were read before this freeze; /add+intake+milestone land in §2.
  - [x] golden-spine test is hardcoded (does not parse the doc) — verified by
    reading test_quickstart.py; placement cannot break it
  - [x] "add.py check" in the spine is safe — only new-task/advance/gate/stage
    are phase-walk commands; check/status/guide/audit are maintenance surfaces

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: the spine asks for exactly one typed command
  Given GETTING-STARTED.md
  When the text before the escape-hatch heading is scanned
  Then it contains no add.py new-task, advance, gate, or stage command
  And the install fences remain (the one command the reader types)

Scenario: install hands off to the conversation
  Given the Install section
  When its content is read
  Then the flagless `npx @pilotspace/add init` form leads the examples
  And the section says to open Claude Code and type /add next

Scenario: the first feature is a conversation
  Given a heading "Your first feature — talk to the agent"
  When its section is read
  Then it shows the /add + transfer-money prompt
  And names intake, milestone, and the one-approval front
  And the On-ramp callout survives

Scenario: the CLI is reframed as the override
  Given a heading "What just happened"
  When its section is read
  Then add.py status appears framed as the reader's own check/resume surface
  And no phase-walk command appears

Scenario: the escape hatch is self-contained
  Given the escape-hatch appendix
  When its content is read
  Then new-task, the stage-change command, advance, and gate PASS all appear
  And the documented by-hand spine still drives a project to PASS
    (pre-existing golden-spine test)

Scenario: nothing shipped breaks
  Given the rewrite
  When the full suite runs
  Then every pre-existing GETTING-STARTED/README guard stays green
  And the engine add.py is byte-untouched ×3
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add-method/GETTING-STARTED.md  REWRITE (only file this task touches)
  Spine:    0 Prerequisites · 1 Install (flagless-first + handoff echo) ·
            2 Your first feature — talk to the agent (merged fast-path +
            /add prompt + 4 on-ramp steps + On-ramp callout) ·
            3 What just happened (status/guide = override + resume) ·
            Resume next session · Self-check · Enforce the seams in CI
  Appendix: "Under the hood — the seven phases by hand (escape hatch)"
            heading KEPT; gains new-task scaffold + stage-change intro;
            seven H3 phase blocks stay; Where to read more closes the doc.
  Spine command ban: add.py new-task/advance/gate/stage appear only at/after
            the escape-hatch heading.
  Guards:   the full shipped-guard UNION stays green (9 literals · `guide  :`
            · lead-in rules · heading rule · one-approval front · real
            subcommands · golden spine).
ENGINE UNTOUCHED: add.py byte-identical ×3 (md5 ccb0aa1589c09d3238d7e7fbca1e0240).
GUARD: add-method/tooling/test_getting_started_spine.py — spine command ban ·
flagless-first install + handoff · merged first-feature section · override
framing · self-contained escape hatch · engine pin.
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (one-approval front via AskUserQuestion — both v15 fronts approved together; least-sure ⚠ flags led the freeze)   <!-- becomes: FROZEN @ v1 once approved. Changing a frozen contract = change request back to SPECIFY. -->
<!-- The freeze IS the one approval. Lead it with the bundle's least-sure flag: the 1–2 points
     most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], with why + cost.
     The §1 ⚠ assumptions are its first feeder; a flag may point at a scenario or the contract too. See run.md. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: every Must has a test; one test per scenario (the
"nothing shipped breaks" scenario is carried by the pre-existing suites +
the engine pin, not duplicated).
Plan (one test per scenario, asserting behavior not internals):
  - test_spine_free_of_phase_walk_commands: spine = text before the
    escape-hatch heading line; assert no add.py new-task/advance/gate/stage
    tokens in it (RED: new-task + stage mvp sit in today's spine)
  - test_install_section_flagless_first_with_handoff: Install section shows
    a flagless `npx @pilotspace/add init` fence line first + says open
    Claude Code / type /add (RED: flags + no handoff today)
  - test_first_feature_section_merged: heading "your first feature — talk to
    the agent" exists; its section carries the /add prompt fence, transfer
    money, intake, milestone, one-approval (RED: heading absent today)
  - test_what_just_happened_overrides: heading "what just happened" exists;
    section carries add.py status with override/resume framing and no
    phase-walk command (RED: heading absent today)
  - test_escape_hatch_self_contained: from the escape-hatch heading on,
    new-task AND a stage command AND advance AND gate PASS all appear
    (RED: new-task + stage live before the heading today)
  - test_engine_untouched: add.py md5 ccb0aa1589c09d3238d7e7fbca1e0240 ×3
    (green-by-design pin — prose-only task)

Tests live in: `add-method/tooling/test_getting_started_spine.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): GETTING-STARTED.md is the ONLY file edited;
design every paragraph to the shipped-guard UNION before writing (grep the
guards, then write); the escape hatch keeps the full by-hand walk honest.
Code lives in: `add-method/GETTING-STARTED.md`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — suite 448/448 OK; 5 red→green per §4 + engine pin;
      ALL pre-existing doc guards (quickstart · v8-docs · onboarding-align ·
      release-1-1-0) green on the rewrite — the union held first pass
- [x] coverage did not decrease — +6 tests; check 189/0
- [x] no test or contract was altered during build — §3/§4 untouched;
      adversarial verify pass (3 independent lenses) fixed prose coherence
      only: intro one-SHELL-command claim, appendix init-vs---await-lock
      note, cold-start self-containment, `.add/docs/` prefixes, "Before the
      phases" heading, docs range shorthand, lock-down terminology bridge
- [x] concurrency / timing — n/a (prose); golden-spine behavioral guard green
- [x] no exposed secrets / injection / dependencies — prose only; engine md5
      pinned ×3
- [x] layering follows CONVENTIONS.md — single contracted file edited;
      README/installers untouched by THIS task (ownership held)
- [x] a person reviewed and approved the change — escalated residue
      adjudicated: Tin confirmed PASS ×2 and chose the root-doc pointer-stub
      change request (applied alongside this gate)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin · date: 2026-06-05
Evidence: suite 448/448 (5 red→green + engine pin; 16-guard union green
  first pass); 3-lens adversarial verify — prose-coherence fixes applied
  in-build; root-doc residue closed by Tin's pointer-stub decision.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): newcomer confusion reports against the
spine (issues citing "which command do I run") — the doc's rejection scenarios
are its monitors; next release ships this doc in both registries.
Spec delta for the next loop: the root pointer stub means future doc tasks
have ONE contracted surface — keep it that way.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [SDD · folded] designing to the grepped guard-UNION before writing landed a
  16-guard doc rewrite green first pass — the union rule's first premeditated
  application (evidence: zero pre-existing guard reds at build)
- [UDD · folded] "zero-command" survived contact only as "one SHELL command" —
  /add is still typed; precise promises beat catchy absolutes (evidence:
  doc-truth verifier caught the intro contradicting §1)
