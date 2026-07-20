# TASK: init ends with an AI handoff; flags become optional

slug: installer-handoff · created: 2026-06-05 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower
     the dial with `autonomy: conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: a flagless install is the documented, behaviorally-pinned default —
  `npx @pilotspace/add init` (and the pip twin) with zero flags succeeds and
  ends in the conversational handoff; the manual-init escape hint drops its
  flags too (the engine already infers the name) (v15 exit criterion 2)
GAP RE-VERIFIED before scoping (foundation rule: re-verify a routed gap):
  v12 already shipped most of this — both installers print "open Claude Code,
  run `/add`…", all flags are optional, --stage defaults to prototype, and the
  engine's cmd_init already infers --name from the folder (proj_name =
  args.name or base.name). What is GENUINELY missing: (a) no behavioral test
  runs a flagless install end-to-end (the v8 guards pin WORDS in source, not
  the run — words-exist ≠ method-works); (b) the manual-init hint always
  echoes `--stage prototype` and an optional --name, presenting a flagged
  command where a flagless one works — the hint should be
  `python3 .add/tooling/add.py init --await-lock` unless the user explicitly
  passed flags (then echo them); (c) README's install examples lead with
  flags (`--name "My App" --stage prototype`) — flagless-first there too.
Framings weighed: hint-drops-flags + behavioral pin (chosen: the engine
  already owns name-inference; the installers should present the shortest
  true command) · echo an inferred --name into the hint (rejected: duplicates
  engine logic in two installers and shows a longer command for no benefit) ·
  auto-run init from the installer (rejected & guarded: test_cli_does_not_
  autorun_init pins install-without-state as intentional — the agent or the
  human arms the lock, never the installer)
Must:
  - `node bin/cli.js init` with NO flags in an empty dir: exit 0 · installs
    .claude/skills/add/ + .add/tooling/ + .add/docs/ · creates NO
    .add/state.json · final output names the conversation ("open Claude
    Code", `/add`).
  - The pip twin (add_method installer) behaves identically on a flagless
    `init <dir>`.
  - The manual-init escape hint in BOTH installers: flagless invocation →
    `python3 .add/tooling/add.py init --await-lock` (no --name, no --stage);
    explicit flags passed → they echo into the hint as today. `--await-lock`
    stays in the hint always (v8 guard).
  - cli.js and _installer.py closing-hint text stay byte-equivalent
    (they are today; the edit preserves the parity).
  - README install examples lead flagless: `npx @pilotspace/add init` and
    `pilotspace-add init` with no flags first; the flagged form may follow as
    an option. README "Use it" /add lead-in stays intact (v8 guard).
  - ENGINE untouched: add.py byte-identical ×3 (the inference already lives
    there); GETTING-STARTED.md untouched (owned by getting-started-rewrite).
Reject:
  - installer auto-runs init -> never (pre-existing guard pins it)
  - hint loses --await-lock -> test_v8_install red
  - hint shows --stage/--name the user never typed -> test_*_hint_flagless red
  - engine or GETTING-STARTED edits -> md5 pin red / review rejects the diff
Assumptions — least-sure first:
  ⚠ [test] the behavioral tests need `node` on the test host — least sure
    because the suite has so far only shelled to python; if a host lacks
    node, the npx-side tests must SKIP honestly (skipUnless shutil.which
    "node"), mirroring test_packaging's npm-gated precedent; cost if wrong:
    a skipped (not red/green) pin on exactly the hosts that cannot run it
  ⚠ [spec] dropping `--stage prototype` from the default hint changes a
    string four shipped tests may incidentally match — least sure because
    hint text is pinned by _closing_hint assertions; checked: they require
    '/add', intake|milestone|build-phrases, '--await-lock', and ban
    'new-task' — none pin --stage; if wrong: one of those guards reds at
    build and the hint is reflowed (no contract change)
  - [x] engine cmd_init infers name (read: proj_name = args.name or
    base.name, add.py:351) — the flagless hint loses nothing

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: flagless npx install lands the brain and hands off
  Given an empty directory and no flags
  When node bin/cli.js init runs in it
  Then it exits 0 and .claude/skills/add + .add/tooling + .add/docs exist
  And no .add/state.json is created
  And the output says to open Claude Code and run /add

Scenario: flagless pip install behaves identically
  Given an empty directory
  When the add_method installer runs init with no flags
  Then the same tree, the same no-state rule, the same handoff text

Scenario: the escape hint is as short as the truth
  Given a flagless install
  When the closing hint is printed
  Then the manual-init line is `init --await-lock` with no --name and no --stage

Scenario: explicit flags still echo
  Given an install with --name "Acme" --stage mvp
  When the closing hint is printed
  Then the manual-init line carries both flags

Scenario: README leads flagless
  Given README.md's install examples
  Then `npx @pilotspace/add init` appears with no flags on its line
  And the "Use it" /add lead-in is unchanged

Scenario: nothing else moves
  Given the build
  Then add.py is byte-identical ×3 and GETTING-STARTED.md is untouched
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add-method/bin/cli.js              hint builder: flagless run -> manual-init
                                   hint `python3 .add/tooling/add.py init
                                   --await-lock` (no --stage/--name); explicit
                                   flags echo as today; everything else
                                   byte-unchanged (no autorun, same copies)
add-method/src/add_method/_installer.py  the pip twin, same hint rule,
                                   closing text stays byte-equivalent to cli.js
add-method/src/add_method/_cli.py  only if needed to pass "flag was explicit"
                                   (argparse default sentinel) — no new flags
add-method/README.md               install examples flagless-first; "Use it"
                                   section untouched
ENGINE UNTOUCHED: add.py byte-identical ×3 (md5 ccb0aa1589c09d3238d7e7fbca1e0240).
GETTING-STARTED.md UNTOUCHED (owned by getting-started-rewrite).
GUARD: add-method/tooling/test_installer_handoff.py — flagless behavioral
install ×2 (node-gated skip if no node) · flagless hint ×2 · explicit-flag
echo · README flagless-first · engine pin.
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (one-approval front via AskUserQuestion — both v15 fronts approved together; least-sure ⚠ flags led the freeze)   <!-- becomes: FROZEN @ v1 once approved. Changing a frozen contract = change request back to SPECIFY. -->
<!-- The freeze IS the one approval. Lead it with the bundle's least-sure flag: the 1–2 points
     most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], with why + cost.
     The §1 ⚠ assumptions are its first feeder; a flag may point at a scenario or the contract too. See run.md. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: every Must has a test; live-registry/npm-publish surfaces are
out of scope (this task never publishes).
Plan (one test per scenario, asserting behavior not internals):
  - test_npx_flagless_install_behavioral: tmpdir · run node cli.js init ·
    exit 0 · skill/tooling/docs trees exist · no state.json · stdout has
    "open Claude Code" + /add (green-by-design behavioral PIN that was
    missing; node-gated skipUnless)
  - test_npx_flagless_hint_drops_flags: same run's stdout — the manual-init
    hint line has --await-lock and NO --stage/--name token (RED: hint echoes
    --stage prototype today)
  - test_pip_flagless_install_behavioral: tmpdir · run the add_method
    installer via python (PYTHONPATH=src) · same tree/no-state/handoff
    assertions (green-by-design behavioral pin)
  - test_pip_flagless_hint_drops_flags: same run — flagless hint rule (RED)
  - test_explicit_flags_echo_into_hint: run cli.js init --name "Acme"
    --stage mvp · hint carries both flags (green-by-design: preserves
    today's echo for explicit flags)
  - test_readme_install_examples_flagless_first: README has a line exactly
    `npx @pilotspace/add init` (no flags) in its install fence (RED: flagged
    form only today)
  - test_engine_untouched: add.py md5 ccb0aa1589c09d3238d7e7fbca1e0240 ×3
    (green-by-design pin)

Tests live in: `add-method/tooling/test_installer_handoff.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): the installers NEVER run init (pre-existing
guard); the hint rule is presentation-only — no copy/install logic changes;
cli.js and _installer.py closing text stay byte-equivalent.
Code lives in: `add-method/bin/cli.js` · `add-method/src/add_method/_installer.py` · `add-method/src/add_method/_cli.py` · `add-method/README.md`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — suite 448/448 OK; 3 red→green per §4 + 4 behavioral
      pins; v8 hint guards green (--await-lock kept; no --stage pinned)
- [x] coverage did not decrease — +9 tests (7 planned + 2 STRENGTHENING
      amendment, disclosed below); check 189/0
- [x] no test or contract was altered during build — EXCEPT one disclosed
      in-build STRENGTHENING amendment (foundation rule: legal, never
      silent): adversarial verify found cli.js silently DROPPING a trailing
      --stage/--name with no value while the pip twin errors (exit 2);
      +test_missing_flag_value_fails ×2, npx side proven RED against the
      unfixed cli.js, then fixed to fail loudly (parity)
- [x] concurrency / timing — installers stay copy-only; no autorun (guard
      green); idempotent skip-if-exists semantics unchanged
- [x] no exposed secrets / injection / dependencies — no new deps; hint is
      static text; engine md5 pinned ×3
- [x] layering follows CONVENTIONS.md — npm↔pip parity held (hint text
      byte-equivalent incl. new win32 launcher branch in BOTH); two
      out-of-contract ONE-LINE truth fixes disclosed: __init__.py stale
      "then runs add.py init" docstring; README survivor-files install-table
      row (both pre-existing falsehoods the story-lens verifier surfaced)
- [x] a person reviewed and approved the change — escalated disclosures
      adjudicated: Tin confirmed PASS ×2 (strengthening amendment + the two
      out-of-contract one-line truth fixes accepted)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin · date: 2026-06-05
Evidence: suite 448/448 (3 red→green + 4 behavioral pins + 2 strengthening
  tests, npx side proven red pre-fix); npm↔pip hint parity incl. win32
  launcher; no autorun guard held.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the flagless install + hint ship with
the NEXT version tag — until then the registries serve the flagged hint; the
behavioral tests are the pre-release monitors.
Spec delta for the next loop: cli.js still accepts any --stage string while
the pip twin enforces choices — a parity candidate for a future task.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [ADD · folded] adversarial verify lenses catch cross-surface DIVERGENCE the
  suite structurally cannot — cli.js silently dropped a valueless flag while
  argparse errored; pair every multi-surface build with a parity hunter
  (evidence: the blocker finding, fixed via disclosed strengthening amendment)
- [TDD · folded] behavioral pins on the happy path found nothing new; the
  missing-value EDGE found a real bug — pin behavior at the edges first
  (evidence: test_missing_flag_value_fails red on npx, green on pip)
- [SDD · folded] re-verifying the routed gap shrank this task from "implement
  the handoff" to "pin it + fix the hint" — half the scoped work already
  existed (evidence: §1 GAP RE-VERIFIED block; v12 shipped the handoff)
