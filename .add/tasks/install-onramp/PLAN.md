# TASK: Make init output AI-first: agent next-hint + bundle skill and book

slug: install-onramp · created: 2026-06-02 · stage: mvp · v8 · depends-on: none
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
autonomy: conservative   <!-- edits the install path (adoption-critical) under method-defining v8 -> hold at verify for human diff review -->

> v8 · *DD driver: ADD. Owns the install next-hint (bin/cli.js + add.py cmd_init) + a regression
> guard. SCOPE CORRECTED at planning: the skill+book bundling already works via bin/cli.js — the
> earlier "init doesn't bundle" finding was a test artifact (bare `add.py init` bypasses cli.js).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

After install, the first thing a user reads is the installer's next-hint. Today both emitters point
at bare `new-task` (`bin/cli.js`: "Next: … add.py new-task <slug>"; `add.py cmd_init`: "next: add.py
new-task …") — CLI-first, and skipping the intake/milestone layer. Re-aim them at the AI-first entry,
and guard the bundling (which already works) so it can't silently regress.

Must:
  - the `bin/cli.js` next-hint sends the user to the **AI-first entry**: open Claude Code, run `/add`,
    describe what to build; the agent runs intake → milestone → one-approval (not bare `new-task`)
  - the `add.py cmd_init` closing line names the same AI-first entry, not `new-task <slug>` as step one
  - `new-task`, if mentioned, is framed as the **agent's tool**, not the user's first move
  - the **bundling is guarded**: package.json `files` ships `skill/` + `docs/` + `tooling/add.py`, and
    `bin/cli.js` copies `skill → .claude/skills/add/` and `docs → .add/docs/` (the AI-first brain is
    present after `npx @mrq/add init`)
Reject:
  - a next-hint that makes bare `new-task` the user's first step (CLI-first, skips intake)  -> "newtask_first_hint"
  - package/installer stops shipping or placing the skill or the book                        -> "unbundled_brain"
After:
  - a freshly `npx`-installed project greets the user with the AI-first entry, and a guard fails if the
    bundling or the AI-first hint regresses.
Assumptions (confirm before building):
  - [x] canonical install is `npx @mrq/add init` (cli.js); bare `add.py init` is the fallback path — verified in cli.js
  - [x] bundling already works (cli.js copies skill+docs); this task GUARDS it, does not add it — verified
  - [x] `/add` is the user-invocable skill name for the conversational entry — confirmed (skill `name: add`)

<!-- EXIT: every rule stated, every rejection has a named code, zero open assumptions. -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: the cli.js next-hint is AI-first
  Given bin/cli.js after install
  Then its closing hint tells the user to run `/add` and describe what to build (intake → milestone),
       and does NOT make bare `new-task` the prescribed first step

Scenario: the add.py init next-hint is AI-first
  Given add.py cmd_init's closing print
  Then it names the AI-first entry, not `new-task <slug>` as step one

Scenario: the brain is bundled (guarded)
  Given package.json and bin/cli.js
  Then package.json `files` ships skill/ + docs/ + tooling, and cli.js copies skill → .claude/skills/add
       and docs → .add/docs

Scenario: a regression trips the guard
  Given a next-hint reverted to bare new-task, or skill/docs dropped from `files`
  Then test_v8_install fails (the guard is real, not decorative)
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
ARTIFACT: the install next-hint — bin/cli.js cmdInit closing block + add.py cmd_init closing print —
          plus a regression guard test (add-method/tooling/test_v8_install.py).
FROZEN:   (a) both next-hints name the AI-first entry (`/add` → describe → intake → milestone →
          one-approval), not bare `new-task`; (b) `new-task` if shown is the agent's tool; (c) the
          guard asserts package.json `files` ships skill/ + docs/ + tooling and cli.js copies
          skill → .claude/skills/add + docs → .add/docs.
GUARD:    test_v8_install.py — cli-hint-ai-first · init-hint-ai-first · cli-bundles-brain · package-ships-brain
reject codes: newtask_first_hint, unbundled_brain
NON-GOAL: changing what cli.js copies (bundling already works); changing the 7-phase flow.
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (retro-ratified at v14 gate-audit) · (HUMAN-approved at the seam — AskUserQuestion "Approve & freeze", 2026-06-02)

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY. -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Structural (reads the source text of bin/cli.js + package.json + add.py, like test_v7/test_v8_onramp).
Lives in `add-method/tooling/test_v8_install.py`.

Plan (one test per scenario):
  - test_cli_next_hint_is_ai_first:  cli.js closing hint names `/add` + intake/milestone; not bare new-task  [RED now]
  - test_init_next_hint_is_ai_first: add.py cmd_init closing print names the AI-first entry, not new-task     [RED now]
  - test_cli_bundles_brain:          cli.js copies skill → .claude/skills/add AND docs → .add/docs            [green — invariant]
  - test_package_ships_brain:        package.json `files` includes skill/ + docs/ + tooling/add.py            [green — invariant]

RED now: the two hint tests fail (current hints say new-task, no `/add`). The two bundling tests start
green — they GUARD the working bundling so the build can't break it. Words-exist != method-works.

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule: edit only the two next-hint emitters (`bin/cli.js` cmdInit close + `add.py` cmd_init
close); do NOT change what cli.js copies (bundling already works). `add.py` edit must mirror to both
trees byte-identical. `bin/cli.js` lives only in add-method/ (not mirrored).
Files: `add-method/bin/cli.js`, `add-method/tooling/add.py` (+ mirror `.add/tooling/add.py`).
Constraints: did NOT touch test_v8_install.py or the frozen contract; no new dependency.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — `test_v8_install` 4/4; full tooling suite **162 OK**; `add.py check` **112/0**
- [x] coverage did not decrease — added 4 structural tests; none removed/weakened
- [x] no test or contract was altered during build — contract FROZEN @ v1; test_v8_install unchanged since red
- [x] concurrency / timing — N/A (print/log strings; no IO race)
- [x] no exposed secrets / injection / unexpected dependencies — static strings, no inputs, no new deps
- [x] layering & dependencies follow CONVENTIONS.md — both add.py trees identical; cli.js copy logic untouched
- [x] a person reviewed and approved the change — human approved at verify (AskUserQuestion 2026-06-02)

Evidence (end-to-end): `node bin/cli.js init /tmp/...` prints the AI-first next-hint and installs the
skill (`.claude/skills/add/`) + book (`.add/docs/`) — the brain is present and the greeting is AI-first.
Blind-spot (completeness-critic): the guard proves the hint TEXT + file ops; it does NOT prove a user
follows `/add` instead of ad-hoc coding (words-exist != method-works — OBSERVE watch, shared with the block).

### GATE RECORD
Outcome: PASS   <!-- human-approved at verify; clean (no conflict) -->
Reviewed by: Tin Dang (human, at verify gate) · date: 2026-06-02

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): do `npx`-installed users actually run `/add` + describe, or fall
back to manual `new-task`? (the same words-exist≠method-works watch as the orientation block).
Spec delta for the next loop: the install greeting + the block both now promise the AI-first flow —
the deferred CI/runtime enforcer (v7 carry-forward) should check the seam is honored, not just printed.

### Competency deltas
- [ADD · folded] A planning-phase verification overturned a stated finding: "init doesn't bundle the
  skill+book" was a TEST ARTIFACT (bare `add.py init` bypasses `bin/cli.js`, which does the bundling).
  Evidence: `node bin/cli.js init` installs skill+book; bare `add.py init` does not. Lesson — verify a
  gap against the REAL entry path before scoping a fix. Candidate book note: "test the shipped path."
  [folded foundation-version 8 → CONVENTIONS.md "Verify a gap against the shipped path"]
- [ADD · folded] Two next-hint emitters (cli.js + add.py) print on the same install (stdio inherited) —
  drift risk if only one is updated. Evidence: both had to change for a consistent greeting. Candidate:
  single-source the hint, or a guard that both match.
  [folded foundation-version 8 → reinforces CONVENTIONS.md "Dogfood parity" (single-source duplicated output)]
