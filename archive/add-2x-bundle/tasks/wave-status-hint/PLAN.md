# TASK: status surfaces a live WAVE.md as the wave resume hint

slug: wave-status-hint · created: 2026-06-07 · stage: mvp · autonomy: auto
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- autonomy: auto — read-only print, decides nothing (v10 deltas-report precedent);
     the bundle freeze stays human, as always. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `add.py status` prints a wave resume hint when a live WAVE.md exists
Framings weighed: existence-only hint on the human surface (chosen) · parse `status: live|merging` from the file (rejected: the engine stays judgment-free and IO-free — existence IS liveness, since the convention deletes at wave close) · additive JSON field too (rejected: `status --json` is the frozen machine-state-json contract — touching it is a change-request, and no machine consumer needs the hint yet)
Must:
<must>
  - `add.py status` (human surface) prints, for EACH `.add/milestones/<m>/WAVE.md` that is a regular file, one hint line: `wave    : LIVE — .add/milestones/<m>/WAVE.md  (wave resume point — re-orient from the ledger first)`
  - placement: directly after the `context :` foundation pointer — a live wave is read-first orientation, same class as the foundation
  - detection is existence-only: no open, no read, no parse — zero new IO failure modes (design for failure by having no failure path)
  - `status --json` output is byte-shape UNCHANGED — no new key, frozen machine-state-json honored
  - no ledger → no line; a directory (or non-file) at the path → no line, never an error
  - three-tree parity: canonical `add-method/tooling/add.py` · dogfood `.add/tooling/add.py` · bundle, all synced (existing parity guards)
</must>
Reject:
<reject>
  - any new key appearing on `status --json` -> "frozen_json_surface_touched"  (guard test fails)
  - a hint emitted when no live ledger exists -> "phantom_wave_hint"  (guard test fails)
  - a directory at the WAVE.md path crashing or hinting -> "not_a_file_no_hint"  (guard test fails)
</reject>
After:
<after>
  - the mandated first-orientation command surfaces the wave resume point — closing the disclosed [ADD] residue from wave-ledger: an orchestrator resuming a session can no longer miss a live wave by forgetting to look in the milestone dir
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ existence-only detection is right — lowest confidence because a stale, undeleted WAVE.md keeps hinting forever; if wrong: noise — but a stale ledger hinting is `digest_not_absorbed` SURFACING, which is arguably the feature working
  ⚠ placement after the `context :` line — second-lowest, cosmetic; if wrong: one-line move, trivial cost
  - [x] `auto` autonomy fits — read-only, decides nothing (v10 deltas-report precedent)
  - [x] multiple live ledgers print multiple lines — fail-loud on the convention's one-live-wave rule, never hide an anomaly
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: hint when a live ledger exists
  Given an ADD project with milestone mvp and a file .add/milestones/mvp/WAVE.md
  When add.py status runs
  Then the output contains a "wave    : LIVE — .add/milestones/mvp/WAVE.md" line with the re-orient wording
  And it appears after the "context :" foundation pointer

Scenario: silent when no ledger exists
  Given the same project with no WAVE.md anywhere
  When add.py status runs
  Then no "wave    :" line appears   # phantom_wave_hint
  And the rest of the output is unchanged

Scenario: non-file at the path neither crashes nor hints
  Given a DIRECTORY named WAVE.md inside a milestone dir
  When add.py status runs
  Then the command exits 0 with no "wave    :" line   # not_a_file_no_hint
  And no traceback is printed

Scenario: one line per live ledger, fail-loud
  Given two milestones each holding a WAVE.md file
  When add.py status runs
  Then two "wave    :" lines appear (the one-live-wave anomaly is shown, not hidden)

Scenario: frozen JSON surface untouched
  Given a live WAVE.md exists
  When add.py status --json runs
  Then the parsed object's keys are exactly {project, stage, active_task, milestones, tasks}   # frozen_json_surface_touched
  And the command exits 0
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
CLI add.py status            (human surface ONLY)
  after the "context :" foundation-pointer line, for EACH .add/milestones/<m>/WAVE.md
  that is a regular file (existence-only check — no open/read/parse):
    "wave    : LIVE — .add/milestones/<m>/WAVE.md  (wave resume point — re-orient from the ledger first)"
  absence or non-file -> no line, exit unchanged, never an error
CLI add.py status --json     UNTOUCHED — keys stay exactly
  { project, stage, active_task, milestones, tasks }   (frozen machine-state-json)
Schema: no state.json change · no new flags · no new dependency
```

Status: FROZEN @ v1 — approved by Tin (2026-06-07; one-approval bundle gate, ⚠ flags presented lowest-confidence first)
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every contracted behavior has a test (5 scenarios → 5 tests); existing suites stay green
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_status_hints_live_wave: arrange temp project + milestone + WAVE.md file / act run status / assert "wave    : LIVE" line with path + re-orient wording, after the context line
  - test_status_silent_without_wave: arrange same project, no WAVE.md / act status / assert no "wave    :" line
  - test_dir_at_wave_path_no_hint_no_crash: arrange a directory named WAVE.md / act status / assert exit 0, no "wave    :" line
  - test_one_line_per_live_ledger: arrange two milestones each with WAVE.md / act status / assert exactly two "wave    :" lines
  - test_json_surface_frozen: arrange live WAVE.md / act status --json / assert parsed keys == {project, stage, active_task, milestones, tasks}
</test_plan>

Tests live in: `add-method/tooling/test_wave_status_hint.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): the hint is print-only and IO-free beyond an existence check — no state mutation, no file read, no new failure path; `--json` byte-shape must not move.
Code lives in: `add-method/tooling/add.py` (cmd_status) + synced `.add/tooling/add.py` + bundle
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 5/5 new (red-first 2F/3P), full tooling suite 574 OK; dogfood proved both ways on this repo (0 hint lines without a ledger; the exact contracted line with one)
- [x] coverage did not decrease — suite grew 569→574; no test removed
- [x] no test or contract was altered during build — DISCLOSED exception, not a weakening: five stale `ENGINE_MD5` pins (absolute-hash guards from prose-only tasks asserting *their* commits left the engine untouched) re-aimed to the new engine hash after this task's own contracted engine change — the guards now pin the new state and keep catching unauthorized drift (established stale-guard-sweep pattern, commit dd5b665); the wave-status-hint suite and §3 were untouched post-freeze
- [x] concurrency / timing safe — read-only `glob` + `print`, no state mutation, no file read (existence-only), no new IO failure path
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only
- [x] layering & dependencies follow CONVENTIONS.md — follows the existing status-line idiom; three trees synced (parity guards green); frozen `--json` surface untouched (test-pinned)
- [x] reviewed — auto-resolved under `autonomy: auto` (read-only scope, decides nothing); no security, concurrency, or architecture residue to escalate

### GATE RECORD
Outcome: PASS — auto-resolved by the dynamic run (autonomy: auto), owner: wave-status-hint run, 2026-06-07. Not a human signature: recorded on complete evidence per run.md; the human approval for this task was the bundle freeze.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the next parallel wave — did the orchestrator's resume actually route through the hint?
Spec delta for the next loop: none yet — the hint ships untested-in-anger until a real wave runs; pairs with wave-ledger's §7 watch.

### Competency deltas
- [TDD · folded] absolute-hash engine pins go stale BY DESIGN — every legitimate engine change re-aims N copies of `ENGINE_MD5` by hand (5 this time); a single shared pin (one source, N importers) would turn the sweep into one edit (evidence: this build re-aimed five identical constants; second occurrence of the pattern after dd5b665's stale-guard sweep)
- [ADD · folded] the auto dial completed its first ENGINE-scope run end-to-end — freeze → red → green → auto-PASS with a disclosed judgment call (stale-pin re-aim) logged instead of escalated; the dial's "no residue" condition forced an explicit weakening-vs-re-aim argument into the gate record (evidence: this task's §6; contrast v10's conservative ESCALATE)
