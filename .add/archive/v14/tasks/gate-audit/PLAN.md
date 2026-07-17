# TASK: add.py audit — judgment-free checks of recorded human seams

slug: gate-audit · created: 2026-06-05 · stage: mvp
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `add.py audit` — judgment-free verification that human seams left
  well-formed RECORDS (v14 centerpiece; closes "a self-asserted gate is circular",
  open since v7, when audit-ci wires it into CI)
Framings weighed: record-shape audit (chosen: the engine can verify what a human
  SIGNED, never whether they engaged — honest mechanical guarantee) · semantic
  audit (rejected: judging outcomes inside the engine breaks judgment-free) ·
  git-history audit (rejected: state+prose are the canonical records; git is
  optional in ADD projects)
Must:
  - New read-only command `audit [--json]` over ACTIVE-state tasks; exit 0 clean,
    exit 1 with findings; each finding = {task, code, detail}, text + --json twins.
  - Checks per task (all record-shape, zero judgment):
    F1 unstamped_freeze — task done/gated but §3 lacks
       `Status: FROZEN @ vN — approved by <name>` (name non-empty)
    F2 malformed_gate_record — done/gated but §6 has not exactly ONE
       `Outcome:` line valued PASS | RISK-ACCEPTED | HARD-STOP
    F3 gate_record_mismatch — §6 Outcome prefix ≠ state.json gate
    F4 unescalated_security_note — the §6 security checklist item carries an
       escalation marker (`NOTE` or `⚠`) while GATE RECORD `Reviewed by:` names
       the auto-gate — the mechanized v13 lesson
    F5 risk_accepted_security — Outcome RISK-ACCEPTED while the security item
       carries a marker (never allowed, rule 4)
    F6 waiver_incomplete — RISK-ACCEPTED without owner AND ticket AND expires
  - Prose accord: phases/6-verify.md states the marker convention (a security-line
    note MUST start `NOTE` or `⚠` so the audit can see it) — synced ×3.
  - Purity: no write, no state change, existing commands byte-identical.
Reject:
  - unreadable/missing TASK.md or §6 on a done task -> finding (fail-closed,
    never a crash; the audit reports, exit 1)
  - tasks not yet done/gated -> SKIPPED (the front is still open; nothing to audit)
After:
  - CI (audit-ci, next task) can fail a commit whose seam records are malformed —
    enforcement distinct from the agent exists for the first time.
Assumptions — least-sure first:
  ⚠ the marker grammar (`NOTE`/`⚠` on the security item) is how the audit SEES a
    security note — least sure because an unmarked note escapes F4; mitigation:
    the 6-verify guide states the convention and F4 catches the marked majority;
    if wrong: tighten the grammar in a later contract (cost: additive)
  ⚠ shape-not-engagement is the honest limit — a forged name passes the audit; it
    raises silent self-gating from "free" to "explicit forgery", which is the
    achievable mechanical guarantee (words-exist ≠ method-works, named in §4)
  - [ ] legacy active tasks (e.g. orphan WARN tasks) may carry old record shapes —
    the build run will surface them; real findings get fixed, not grandfathered

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: clean board exits zero
  Given every done task has a named freeze stamp and one matching gate outcome
  When add.py audit runs (text and --json)
  Then exit 0 and zero findings

Scenario: unstamped freeze is named
  Given a done task whose §3 says FROZEN without "approved by <name>"
  When audit runs
  Then exit 1 with finding unstamped_freeze naming the task

Scenario: gate record must have exactly one outcome
  Given a done task with zero (or two) Outcome lines in §6
  When audit runs
  Then finding malformed_gate_record

Scenario: prose and state must agree
  Given §6 says Outcome: PASS but state.json records HARD-STOP
  When audit runs
  Then finding gate_record_mismatch

Scenario: the v13 lesson is mechanized
  Given a security item carrying "NOTE …" and Reviewed by: auto-gate
  When audit runs
  Then finding unescalated_security_note
  And the same task with a human-named reviewer produces NO finding

Scenario: risk-accepted never on security
  Given Outcome: RISK-ACCEPTED and a ⚠-marked security item
  When audit runs
  Then finding risk_accepted_security

Scenario: incomplete waiver
  Given RISK-ACCEPTED without owner/ticket/expires
  When audit runs
  Then finding waiver_incomplete

Scenario: open tasks are skipped
  Given a task still at specify
  When audit runs
  Then it contributes no finding

Scenario: audit is pure
  Given any board above
  When audit and --json run
  Then the file set and state.json bytes are unchanged
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add.py audit [--json]                       # NEW read-only command
  exit 0 -> clean ("audit: clean (<n> tasks checked)")
  exit 1 -> findings; text: one line per finding "audit: <code> <task> — <detail>"
            --json: {"checked": n, "findings": [{"task","code","detail"}]}
  scope: tasks in ACTIVE state whose phase is done/observe OR gate != none;
         others skipped (front still open)
  finding codes (frozen set v1): unstamped_freeze · malformed_gate_record ·
    gate_record_mismatch · unescalated_security_note · risk_accepted_security ·
    waiver_incomplete
  parsers: stamp r"Status:\s*FROZEN @ v\d+\s*[—-]+\s*approved by\s+\S+" ·
    outcome r"^Outcome:\s*(PASS|RISK-ACCEPTED|HARD-STOP)" (count must be 1) ·
    auto-reviewer = "auto-gate" in the Reviewed-by line ·
    security marker = "NOTE" or "⚠" in the §6 security checklist item text
prose accord: phases/6-verify.md gains the marker convention line, synced ×3
no existing command/JSON/exit-code changes — audit is purely additive
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (one-approval front; marker grammar + shape-not-engagement limit accepted)   <!-- Changing a frozen contract = change request back to SPECIFY. -->
<!-- The freeze IS the one approval. Lead it with the bundle's least-sure flag: the 1–2 points
     most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], with why + cost.
     The §1 ⚠ assumptions are its first feeder; a flag may point at a scenario or the contract too. See run.md. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: every finding code red at least once + the no-finding twins
(human-named reviewer · clean security line · open task skipped) + purity + --json
shape; asserting CLI output and exit codes, never parser internals. HONEST LIMIT
(named per words-exist ≠ method-works): the audit proves records are WELL-FORMED,
not that a human engaged — a forged name passes; CI wiring (audit-ci) makes the
forgery explicit and attributable, which is the mechanical ceiling.
Plan (one test per scenario):
  - test_clean_board_exit_zero (also asserts the counted-tasks line)
  - test_unstamped_freeze · test_missing_name_is_unstamped
  - test_zero_outcomes_malformed · test_two_outcomes_malformed
  - test_prose_state_mismatch
  - test_security_note_autogate_flagged · test_security_note_human_ok ·
    test_clean_security_autogate_ok (the three-way F4 matrix)
  - test_risk_accepted_security
  - test_waiver_incomplete
  - test_open_task_skipped
  - test_audit_json_shape · test_audit_pure
  - test_guide_states_marker_convention (prose accord anchor, ×3 parity)

Tests live in: `add-method/tooling/test_gate_audit.py` (suite root, like every
prior tooling task) · MUST run red (no audit command) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): audit reads, never writes; every existing command,
JSON key, and exit code byte-identical; the engine stays judgment-free (shape checks only).
Code lives in: `add-method/tooling/add.py` (canonical) → synced ×3; guide line in
  `add-method/skill/add/phases/6-verify.md` → synced ×3.
Constraints: do NOT change any test or the contract; stdlib only.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — 395/395 (381 prior + 14 new), `add.py check` 201/0 (4 pre-existing warns)
- [x] coverage did not decrease — 14 tests added incl. the three-way F4 matrix; 13 red for the
      right reason (no audit command), 1 green-by-design (purity); two harness items during
      build, neither a weakening: the RISK-ACCEPTED fixture had to pass the engine's own
      --owner/--ticket/--expires flags (repairing an arrange step that crashed pre-assert), and
      `audit` was classified into test_min_pillar's LIFECYCLE — that guard's own documented
      maintenance path (coverage EXPANDED to the new command, placed pre-gate so it runs clean)
- [x] no test or contract was altered during build — §3 untouched post-freeze; no assertion changed
- [x] concurrency / timing safe — read-only scan, no shared state
- [x] no exposed secrets, injection openings, or unexpected dependencies — audit READS TASK.md +
      state.json (files every report path already reads); no write, stdlib only; nothing on this
      line to escalate
- [x] layering & dependencies follow CONVENTIONS.md — judgment-free shape checks only; 3-tree md5
      parity 92bdaae03677674e756568ab7c69fed8 ×3; prose accord (marker convention) in 6-verify.md ×3
- [x] a person reviewed and approved the change — Tin approved the frozen contract AND the gate
      (escalated: live dogfood surfaced 43 unstamped_freeze findings — residue adjudicated by the
      human: retro-ratify, recorded as a present-day act, never a fabricated past one)

### GATE RECORD
Outcome: PASS — HUMAN-confirmed (the 43-finding dogfood run is the audit working as designed on a
legacy board; resolution: all 43 legacy freezes retro-ratified by Tin 2026-06-05, audit now
exit 0 "clean (43 tasks checked)")
Reviewed by: Tin (human gate — residue: live-board findings) · date: 2026-06-05

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): security notes written WITHOUT the NOTE/⚠ marker (escape
F4 — the accepted ⚠); audit exit-1 noise on legitimate in-flight states (none seen: open fronts
are skipped); the forged-name ceiling (audit proves shape, not engagement — audit-ci makes
forgery attributable, a CI-history fact).
Spec delta for the next loop: the enforcement seam EXISTS — audit-ci can now wire `audit` into
CI and the finding grammar is frozen; the v7-era "self-asserted gate is circular" gap is one
task from closed.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
  - [ADD · folded] a new enforcement surface applied to a legacy board surfaces convention-epoch
    debt as true positives — adjudicate at the human gate (here: retro-ratify as an honest
    present-day act), never auto-grandfather and never fabricate past records (evidence: 43
    unstamped_freeze findings on first live run, human-resolved same day)
  - [ADD · folded] bulk adjudication must surface the CONTRADICTING SUBSET, not just the count —
    a blanket stamp over 43 records silently wrote "approved by Tin" onto 6 tasks whose own
    record said "NOT human-approved"; the audit (shape-only) reported clean over the
    contradiction. Fix ritual: grep the target set for text that negates the act being
    stamped, show that subset to the human, get an informed yes BEFORE writing (evidence:
    advisor-caught post-commit; human re-adjudicated the 6 as informed ratification, lines
    reworded to one coherent claim, 2026-06-05)
  - [TDD · folded] a fixture arranging through the REAL engine inherits the engine's own input
    contracts — the RISK-ACCEPTED arrange step crashed until it passed the waiver flags the
    engine enforces; arrange-through-CLI is stronger than file-writing but costs fidelity to
    its argument grammar (evidence: test_risk_accepted_security errored pre-assert)
