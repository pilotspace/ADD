# TASK: Reusable PTY test helper for clack interactive paths

slug: pty-clack-harness · created: 2026-06-18 · stage: mvp
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
  - `add-method/bin/cli.js:runClackPreamble(clack, target, detected, askScope)` (L317) — the npm clack
    interactive flow under test; returns `{cancelled, target, profile, global, intent}`. The prompt
    sequence: `clack.text` target (L323) → `clack.confirm` write (L328) → `clack.select` scope (L335,
    `askScope`) → `clack.select` agent / the D8 step (L345) → `clack.text` intent (L356).
  - `add-method/bin/cli.js:runClackPreamble` guard `if (!process.stdin.isTTY) return {cancelled:true,…}` (L322)
    — the exact line a piped force-seam can't pass: clack needs a real TTY for raw mode, so a non-TTY
    stdin short-circuits to cancelled BEFORE the first prompt. This is why a PTY is required.
  - `add-method/bin/cli.js:interactive(args)` (L238) + the `ADD_INSTALLER_FORCE_INTERACTIVE` seam (L240–242):
    `"1"` forces interactive, `"fail"` forces a clack-import throw (→ clack_unavailable fallback).
  - `add-method/bin/cli.js:loadClack()` (L245), `scopeOptions()` (L303), `AGENT_PROFILES` (L84),
    `renderBrand`/`readinessLine` (L292/L163), `writeIntentNote(target,intent)` (L368) — symbols whose
    rendered output / file side-effects the harness will assert.
  - `add-method/tooling/test_installer_prompts.py` — the existing twin-coverage test; `_run_node` (pipes
    stdin → never a TTY), `_brain_landed`, `_nothing_written`, `PipInteractiveHappyTest` (the AUTOMATED pip
    model the npm path must match), and the in-file docstring disclosing the npm clack happy-path (M1) as the
    PTY-manual-only gap this task closes.
  - `add-method/tooling/test_agent_detect.py` — drives `node cli.js init --yes` (NON-interactive) only;
    markers D7/D8/D9; the interactive agent-select (D8) keystroke path is the second uncovered path.

Context (working folder):
  - `add-method/package.json` — `@clack/prompts ^1.5.1` is the ONLY runtime dep; `scripts.test` =
    `python3 -m unittest discover -s tooling -p 'test_*.py'`; `node >=18`. (No PTY dep here — see Honors.)
  - `.github/workflows/ci.yml` — `setup-node@v5` (node 20) + `npm ci` + unittest discover on py 3.10/3.12;
    `publish.yml` re-runs the same suite at tag time. New tests must pass under both, headless.
  - No PTY helper exists in `tooling/` (grep clean). Python's `pty` + `os`/`select`/`termios` stdlib IS
    available (verified) — a real pseudo-terminal with zero new npm/pip dependency.

Honors (patterns / conventions; MILESTONE.md + CONVENTIONS.md, task-delta only):
  - Out (MILESTONE): NO installer behavior change (both twins frozen — harness/tests only); NO new runtime
    dependency (test-only PTY via stdlib); NO engine (`add.py`) edits.
  - Tests are Python `test_*.py` in `tooling/`, unittest-discovered; npm-side tests `@unittest.skipUnless(NODE, …)`
    honest-skip when node is absent (`add-method/tooling/test_agent_detect.py:182`).
  - `_run_node` pops `CI` from the env so a parent CI var can't override the force-seam (the PTY harness
    must do the same). Twin-parity convention (cli.js mirrors `_installer.py`) is honored but UNCHANGED — this
    task adds CI coverage for the npm twin's already-frozen behavior.

Anchors the contract cites: `runClackPreamble` · the `ADD_INSTALLER_FORCE_INTERACTIVE="1"` seam · the new `drive_clack` PTY-helper API · `_brain_landed`/`_nothing_written` — detailed below.
  - `runClackPreamble` (the flow driven), the `ADD_INSTALLER_FORCE_INTERACTIVE="1"` seam, the npm clack
    prompt sequence (target → confirm → scope → agent/D8 → intent).
  - The NEW PTY-helper API §3 will freeze (a test-only `tooling/` helper that allocates a PTY, spawns
    `node cli.js`, sends keystrokes, and returns rendered output + exit + written files).
  - Reused assertion anchors: `_brain_landed`, `_nothing_written` (drop vs. cancel observability).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: A reusable PTY test helper that drives clack select/confirm so the installer's
interactive TUI paths are exercised in CI (not just node-syntax-checked + logic-unit-tested).
Seeded (deduped) from two ARCHIVED SPEC deltas the engine can't `--from-delta` (their source
tasks shipped in 1.7.0, so they are out of the live state registry — flipped to seeded by hand):
  - [agent-detect] "extract a reusable PTY test helper that drives clack select/confirm so the
    interactive agent-select step (D8) is covered in CI" — disclosed at its gate as PTY-only-reachable.
  - [installer-prompts] "extract a reusable PTY test helper so interactive happy-paths are
    automatable in CI" — the same need from the original installer milestone.
The agent-select step + the clack happy-path prompts (intro → target → scope → agent → intent) are
the keystroke paths a force-seam can't reach (`runClackPreamble` returns cancelled before the prompt
when stdin isn't a TTY); a committed PTY harness driving real keystrokes closes that gap for both twins.
Scope (confirmed in diverge, 2026-06-18): npm clack twin ONLY (the real gap; pip is already
CI-automated by PipInteractiveHappyTest over piped stdin). Coverage = happy-path accept-defaults
+ one agent-select OVERRIDE + a mid-flow cancel.
Framings weighed: Python stdlib `pty` helper in `tooling/` (chosen — zero new dep, matches the
  Python-test convention, drives the REAL clack flow) · npm `node-pty` devDependency + a JS test
  (rejected — native-compiled devDep hurts `npm ci` portability + diverges from the py-test convention)
  · fake-TTY seam patched into cli.js (rejected — changes FROZEN installer behavior and still tests
  a fake, not clack's real raw-mode keystroke parsing).
Must:
<must>
  - Provide ONE importable, test-only helper in `tooling/` that allocates a real PTY, spawns
    `node bin/cli.js init` with `ADD_INSTALLER_FORCE_INTERACTIVE="1"` and `CI` removed from the env,
    so `runClackPreamble` sees `process.stdin.isTTY === true` and renders the real clack prompts.
  - Drive the prompt sequence by sending keystrokes — text = `\r`; select = arrow (`\x1b[B`/`\x1b[A`)
    then `\r` — waiting for each prompt to RENDER (read-until-marker) before the next keystroke, never
    fixed sleeps, so CI is deterministic, not flaky.
  - Capture and return the combined rendered output, the child exit code, and the target dir, so a
    test can assert what rendered AND the file side-effects (reusing `_brain_landed` / `_nothing_written`).
  - Be reusable: callable from both npm test files (test_installer_prompts, test_agent_detect) without
    copy-paste.
  - Back tests that cover: (a) accept-defaults happy path → the brain drops; (b) agent-select OVERRIDE
    via an arrow key → the chosen (non-detected) agent's pointer is written (D8 keystroke path); (c) a
    mid-flow cancel → nothing is written.
</must>
Reject:
<reject>
  - node not on PATH -> honest skip "node_unavailable"   (skip, never a silent pass)
  - PTY/termios unavailable on the platform (non-POSIX) -> honest skip "pty_unavailable"
  - a prompt does not render within the read deadline -> fail "prompt_timeout"   (never hang the suite)
  - the child does not exit within the deadline -> fail "child_timeout"           (never hang the suite)
</reject>
After:
<after>
  - The clack agent-select step (D8) and the happy-path prompt sequence are exercised by a committed CI
    test driving real keystrokes — no longer PTY-manual-only; the test_installer_prompts docstring gap is closed.
  - `python3 -m unittest discover -s tooling -p 'test_*.py'` is green on a PTY-capable host; honest-skips elsewhere.
  - No installer behavior changed (twins frozen); no new runtime OR dev dependency; `add.py` untouched.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ clack ≥1.5 renders + parses keystrokes correctly under a Python-allocated PTY with the force-seam —
    arrow `\x1b[B` drives select and `\r` confirms text — within its render cadence. Lowest confidence
    because I have not yet executed clack's raw-mode key parsing through a stdlib PTY here; if wrong the
    harness hangs (mitigated: read-until-marker + deadline → "prompt_timeout") or asserts the wrong frame
    (→ flaky/red), costing bounded iteration on the keystroke/marker protocol during build (test-only, no ship risk).
  - [ ] The L322 `!process.stdin.isTTY` short-circuit is the ONLY guard between the force-seam and the
    prompts (verified by read; confirm no second guard at build). If wrong: add the missing precondition. Low stakes.
  - [ ] CI's ubuntu runner + setup-node node 20 expose a usable POSIX `pty` (true for ubuntu/macos;
    Windows honest-skips via "pty_unavailable"). Low stakes.
  - [ ] Matching on prompt-message substrings (read-until-marker) is stable across clack's 1.x range;
    if a label shifts, widen the marker. Low stakes (bounded).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: Happy-path accept-defaults drops the brain   # Must (a)
  Given a real PTY and node on PATH
  When the harness spawns `node cli.js init` with ADD_INSTALLER_FORCE_INTERACTIVE=1 and
       sends Enter through target -> confirm -> scope -> agent -> intent
  Then the child exits 0 and `_brain_landed(target)` is true (.add/ tooling + skill written)
  And the rendered output shows the clack prompts (target / agent) — proving real keystrokes reached the TUI

Scenario: Agent-select override via arrow key writes the chosen agent   # Must (b) — D8 keystroke path
  Given a real PTY, node on PATH, and a detected default of claude (seeded via CLAUDECODE=1)
  When the harness drives to the agent SELECT and sends DOWN + Enter to pick the next agent (codex)
  Then the codex pointer (AGENTS.md) is written under target and the detected claude pointer (CLAUDE.md) is NOT
  And the brain still landed (override changes only which agent profile, not whether files drop)

Scenario: Mid-flow cancel writes nothing   # Must (c)
  Given a real PTY and node on PATH
  When the harness sends a cancel (Ctrl-C / ESC) at the confirm prompt
  Then the child exits without writing and `_nothing_written(target)` is true
  And the target directory is byte-for-byte untouched (cancel happens before any write)

Scenario: One helper drives both npm test files   # Must (reusable)
  Given the helper lives in `tooling/` as an importable module
  When both test_installer_prompts and test_agent_detect import and call it
  Then neither file re-implements PTY spawn/keystroke logic (single source)
  And the helper's public call shape is unchanged across both call sites

Scenario: node absent -> honest skip   # Reject node_unavailable
  Given node is NOT on PATH
  When a PTY test runs
  Then it reports skipped "node_unavailable" (an explicit skip, not a pass)
  And no false-green is recorded and nothing is written to disk

Scenario: PTY unavailable -> honest skip   # Reject pty_unavailable
  Given a platform without POSIX pty/termios (e.g. Windows)
  When a PTY test runs
  Then it reports skipped "pty_unavailable"
  And no false-green is recorded and nothing is written to disk

Scenario: Prompt never renders -> fail, never hang   # Reject prompt_timeout
  Given the expected prompt marker does not appear within the read deadline
  When the harness waits for it
  Then it raises/fails "prompt_timeout" within the deadline
  And the suite does not hang and the child process is terminated (no orphan)

Scenario: Child never exits -> fail, never hang   # Reject child_timeout
  Given the child does not exit within the deadline after the last keystroke
  When the harness waits for exit
  Then it raises/fails "child_timeout" within the deadline
  And the suite does not hang and the child process is terminated (no orphan)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
# tooling/pty_clack.py  — TEST-ONLY helper · stdlib pty/os/select/termios only · NO new dependency
# (function-signature contract: the HTTP template doesn't fit a Python test harness)

# --- module constants (tests guard on these; non-POSIX / no-node => honest skip) ------
NODE: str | None          # shutil.which("node")  -> None => skip "node_unavailable"
PTY_SUPPORTED: bool        # POSIX pty usable      -> False => skip "pty_unavailable"
ENTER  = b"\r"             # confirm a text prompt / accept a select default
DOWN   = b"\x1b[B"         # move selection down (override)        UP = b"\x1b[A"
CANCEL = b"\x03"           # Ctrl-C — clack reads it as isCancel in raw mode

# --- the one public entry point -------------------------------------------------------
drive_clack(args, steps, *, cwd, env_extra=None, read_timeout=10.0, exit_timeout=15.0) -> PtyRun
  args:    list[str]                 # e.g. ["init"]  (spawns: node <CLI_JS> *args)
  steps:   list[(marker: str, keys: bytes)]
           # per step: wait until `marker` substring appears in the rendered stream (<= read_timeout),
           #           THEN write `keys`. read-until-marker — never a fixed sleep.
  env:     parent env + {ADD_INSTALLER_FORCE_INTERACTIVE:"1"} + (env_extra or {}), with "CI" REMOVED
  cwd:     the directory init writes into (caller asserts _brain_landed / _nothing_written on it)

  success -> PtyRun(output: str, exit_code: int)     # full rendered stream + child exit code
  raises  -> PtyTimeout("prompt_timeout")  if a step marker never renders within read_timeout
           | PtyTimeout("child_timeout")   if the child never exits within exit_timeout
             (the child is killed before either raise — no orphan process, suite never hangs)

Schema: no DB. Files touched at BUILD: new `tooling/pty_clack.py` (helper) + new test(s) using it
        (e.g. `tooling/test_pty_clack.py`), and import-site edits in test_installer_prompts /
        test_agent_detect to call the shared helper. cli.js / add.py / _installer.py: UNTOUCHED.
```

Status: FROZEN @ v1 — approved by Tin Dang (2026-06-18). Changing this contract = change request back to SPECIFY.
Least-sure flag surfaced at freeze: ⚠ [contract][spec] clack ≥1.5 renders + parses keystrokes correctly under a Python stdlib-allocated PTY with the force-seam — arrow `\x1b[B` drives `select`, `\r` confirms `text` — within its async render cadence; I had NOT executed this through a stdlib PTY at freeze. If wrong: the harness hangs (guarded → `prompt_timeout`, child killed) or asserts the wrong frame (flaky/red), costing bounded build-time iteration on the keystroke/marker protocol (test-only — no ship risk). Secondary [contract]: the `steps: list[(marker, keys)]` shape matches clack prompt-message substrings, which could shift across clack 1.x — mitigation is widening the marker. Approved by Tin Dang at the freeze.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every scenario has exactly one test; the helper's public surface (drive_clack +
the skip/timeout rejects) is fully exercised. (No % target — `tooling/` has no coverage harness; the
suite is behavioral, run via `python3 -m unittest`.)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_happy_path_drops_brain: arrange real PTY + node + clean tmp HOME/target / act drive_clack(["init"],
    steps=[(target marker, ENTER),(write? marker, ENTER),(scope marker, DOWN+ENTER→project),(agent marker, ENTER),
    (intent marker, ENTER)]) / assert exit_code==0 AND _brain_landed(target) AND prompts seen in output
  - test_agent_override_writes_codex: arrange CLAUDECODE=1 (detected=claude) + tmp target / act drive to agent
    select, send DOWN+ENTER (→codex) / assert (target/AGENTS.md exists w/ GUIDE_BEGIN) AND NOT (target/CLAUDE.md) AND _brain_landed
  - test_cancel_writes_nothing: arrange real PTY + tmp target / act send CANCEL at the confirm prompt / assert
    _nothing_written(target) AND child exited (no write)
  - test_helper_is_shared_single_source: arrange / act import pty_clack from both test modules / assert
    drive_clack is the same object (no re-implemented PTY logic) — guards reuse
  - test_node_unavailable_skips: covered by @skipUnless(NODE,"node_unavailable") on the PTY classes (explicit skip)
  - test_pty_unavailable_skips: covered by @skipUnless(PTY_SUPPORTED,"pty_unavailable") on the PTY classes
  - test_prompt_timeout_raises: arrange a marker that never renders (bogus marker, tiny read_timeout) / act
    drive_clack / assert raises PtyTimeout("prompt_timeout") within deadline AND child terminated (no orphan)
  - test_child_timeout_raises: arrange a step set that leaves the child waiting + tiny exit_timeout / act
    drive_clack / assert raises PtyTimeout("child_timeout") within deadline AND child terminated
</test_plan>

Tests live in: `add-method/tooling/test_pty_clack.py` · MUST run red (missing `pty_clack` module) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/pty_clack.py` `add-method/tooling/test_pty_clack.py`
  (test already written in §4 — listed so the scope-walk sees the whole task diff; build writes ONLY the helper)
Strategy (ordered batches): 1. helper skeleton — module constants (NODE, PTY_SUPPORTED, ENTER/DOWN/UP/CANCEL),
  PtyRun (namedtuple/dataclass), PtyTimeout(code) · 2. drive_clack: openpty → spawn `node CLI_JS *args` (env =
  os.environ − CI + force-seam + env_extra) → per step: select-read-until-marker (deadline → prompt_timeout) then
  write keys → wait-for-exit (deadline → child_timeout) · 3. always reap/kill the child in a finally (no orphan) ·
  4. run test_pty_clack until green; iterate ONLY the keystroke/marker protocol (the ⚠ flag), never the tests.
Safety rule (feature-specific): the child PTY process MUST be terminated on every exit path (success, timeout,
  exception) in a `finally` — a leaked node process would hang CI. read_timeout/exit_timeout bound every wait.
Code lives in: `add-method/tooling/pty_clack.py`   (test-only; stdlib pty/os/select/termios; NO new dependency)
Constraints: do NOT change any test or the contract; cli.js / add.py / _installer.py UNTOUCHED; stdlib only.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 1325 green (1319 → 1325, +6); `python3 -m unittest discover -s tooling -p 'test_*.py'`
- [x] coverage did not decrease — 6 tests added, none removed
- [⚠] no test or contract was altered during build — CONTRACT untouched. But THIS task's own new test
      `test_pty_clack.py` WAS edited after the red snapshot: (a) in build, the self-referential
      `HelperReuseTest` was redesigned (its source-grep could never pass); (b) in verify, two tests were
      STRENGTHENED per the adversarial review (all-5-prompts-rendered + project-scope-took; cancel pinned to
      exit 130). No pre-existing/sibling/frozen test touched; every edit strengthens, none weakens. ESCALATED
      to the human (the mechanical tamper tripwire flags the hash change — this is the disclosure of why).
- [x] the green was EARNED — adversarial refute-read (subagent) verdict EARNED-WITH-CONCERNS; the 3 real
      concerns CLOSED (see above); NO cheat found (no fixture overfit, no vacuous assert, no stubbed logic).
      Tests assert the REAL installer's file side-effects against a real `node cli.js`, not a fake.
- [x] concurrency / timing — each test isolates its own tmp target + tmp HOME; the harness BOUNDS every wait
      (read_timeout / exit_timeout) and kills the child process GROUP in a `finally` (no orphan, no hang); the
      whole suite finishes in ~25s with no hang, the timeout tests in ~4s.
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only (fcntl/struct/termios/
      os/select/subprocess/signal); package.json unchanged; no new npm/pip dependency.
- [x] layering & dependencies follow CONVENTIONS.md — test-only helper in `tooling/`, unittest-discovered,
      honest-skip (`@skipUnless`) pattern matched; installer twins + engine UNTOUCHED.
- [ ] a person reviewed and approved the change — PENDING (this gate; escalated due to the ⚠ above).

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] a PTY-driven accept-defaults `init` RENDERS all 5 clack prompts (target→confirm→scope→agent→intent)
      AND drops the brain into the target — confirmed by the 5-marker assertion + `_brain_landed` in test_happy_path
- [x] the project-scope DOWN keystroke actually LANDS — nothing is written under HOME (a global pick would) —
      confirmed by `not (HOME/.add).exists()` in test_happy_path (closes the "DOWN no-op" hollow path)
- [x] DOWN at the agent select flips the pointer claude→codex: `AGENTS.md` written containing "Codex",
      `CLAUDE.md` absent — confirmed by test_agent_override (traced: "Codex" is exclusive to codex's next_step, cli.js:88–90)
- [x] Ctrl-C at the confirm prompt = exit 130 + nothing written — confirmed by test_cancel (`_nothing_written` + exit 130)
- [x] a non-rendering prompt / non-exiting child raises `prompt_timeout` / `child_timeout` within the deadline,
      child killed — confirmed by the timeout tests (distinct codes) + the suite not hanging

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `drive_clack`, `PtyRun`, `PtyTimeout`, `ENTER`/`DOWN`/`CANCEL`, `NODE`, `PTY_SUPPORTED`
      are imported + exercised by test_pty_clack.py; `_build_env` + `_terminate` + `CLI_JS` are called inside
      `drive_clack`. `UP` is exported for down/up API symmetry — referenced by HelperReuseTest's hasattr check
      but not exercised by a keystroke (intentional public-constant completeness, not dead code).
- [x] DEAD-CODE (code) — no orphaned symbol; `UP` is the only unexercised export and it is part of the frozen §3 surface.
- [x] SEMANTIC — read cli.js in full where the assertions anchor: runClackPreamble (L317–362), cmdInit (L412–462,
      confirmed exit 130 on cancel at L435), writeAgentPointer/agentPointerBlock (L179–238), AGENT_PROFILES (L84–96).

### GATE RECORD
Outcome: PASS — human-reviewed. The build/verify test edits to test_pty_clack.py were reviewed and
accepted as legitimate strengthening (defect-fix of a self-referential reuse test + adversarial-review
tightening); approved with a human-sanctioned tripwire re-baseline (tests→build re-snapshot). Adversarial
earned-green verdict EARNED-WITH-CONCERNS, all 3 concerns closed; no cheat; no security/concurrency/architecture residue.
If RISK-ACCEPTED -> owner: n/a · ticket: n/a · expires: n/a   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-18

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): CI flake rate on the PTY tests (a rise = clack render-cadence /
marker drift); honest-skip rate (a spike on a runner that SHOULD have node+pty = a regressed guard).

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · carried] route test_installer_prompts' npm happy-path + test_agent_detect's D8 through pty_clack for deeper cross-file reuse (evidence: §3 Schema named import-site edits; deferred as minimal-build — one consumer today) [carried: deferred to backlog 2026-06-27 (delta-drain) — not now-actionable; retrievable via 'add.py deltas --carried', reopen or seed via 'new-task --from-delta' when scheduled]
- [SPEC · carried] drive the clack_unavailable fallback + the "fail" seam under a PTY too; today only the force="1" happy/override/cancel paths are PTY-covered (evidence: completeness gap noted at verify) [carried: deferred to backlog 2026-06-27 (delta-drain) — not now-actionable; retrievable via 'add.py deltas --carried', reopen or seed via 'new-task --from-delta' when scheduled]

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [TDD · folded] interactive-TUI tests need a non-zero PTY winsize (e.g. 80×24 via TIOCSWINSZ) or the emulator wraps per-character and substring markers never match (evidence: happy-path raised prompt_timeout until the winsize was set in pty_clack.py) [folded foundation-version 40]
- [ADD · folded] a flag-first freeze flag naming the riskiest unknown ("clack under a stdlib PTY") localized the ACTUAL bug site — flag-first paid off (evidence: the §3 ⚠ assumption was exactly the winsize defect) [folded foundation-version 40]
- [TDD · folded] a test that greps its OWN source for a literal token is self-referential and unpassable; assert object identity / `__module__` instead (evidence: HelperReuseTest had to be redesigned mid-build) [folded foundation-version 40]
- [ADD · folded] the tamper tripwire correctly forced human review of build/verify test edits; the human-approved re-baseline (phase tests → re-advance to re-snapshot) is the sanctioned path, not a launder (evidence: gate PASS blocked until re-baseline this loop) [folded foundation-version 40]
- [ADD · folded] the engine measures §0 grounding from content INLINE on the `Anchors the contract cites:` line — a following bullet list reads as empty → false `task_not_grounded` (evidence: check warned not-grounded until the anchors were inlined on that line) [folded foundation-version 40]
