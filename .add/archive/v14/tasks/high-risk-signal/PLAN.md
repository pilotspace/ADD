# TASK: unguarded_high_risk_auto moves prose to engine

slug: high-risk-signal · created: 2026-06-05 · stage: mvp · risk: high · autonomy: conservative
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.
> THIS task is method-defining (it changes the trust layer), so its own header
> dogfoods the rule it implements: `risk: high` declared, dial lowered to
> `conservative` — the human leads this verify gate by construction.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: the run.md high-risk guard becomes MECHANICAL for the declared case —
  `gate` refuses to complete an unguarded high-risk task, and `add.py audit`
  flags `unguarded_high_risk_auto` on records (v14 exit criterion 3: "refused by
  the engine, not by prose")
Framings weighed: declared-risk token enforced as a header contradiction (chosen:
  judgment of WHAT is high-risk stays human — declared `risk: high` in the TASK.md
  header, reviewed at the freeze like every header; the engine then enforces the
  pure token contradiction risk-high∧not-conservative, staying judgment-free) ·
  engine classifies risk from scope content (rejected: judgment inside the engine,
  out of v14 scope by the shared decisions) · audit-only detection (rejected: the
  exit criterion says REFUSED by the engine — after-the-fact flagging alone lets
  the unguarded pass happen first)
Must:
  - Header grammar: the TASK.md header region (text before the first `## `) may
    declare `risk: high`; the existing `autonomy: conservative|auto` token lives
    there too (absent = auto, the v7 default). Pure token reads, no judgment.
  - ENGINE refusal: `add.py gate <PASS|RISK-ACCEPTED> <slug>` on a task whose
    header declares `risk: high` WITHOUT `autonomy: conservative` dies with
    error `unguarded_high_risk_auto` — state untouched (gate/phase unchanged).
    Completion is refused until a human owns the gate via the lowered dial.
  - HARD-STOP is ALWAYS recordable, guarded or not — never block the stop path.
  - AUDIT finding F7 `unguarded_high_risk_auto` (additive code; {task, code,
    detail} shape frozen by gate-audit @ v1, new code values anticipated by the
    v14 shared-contracts note): a checked task with `risk: high` whose header
    lacks `autonomy: conservative` (post-gate tampering / legacy records), OR
    whose GATE RECORD `Reviewed by:` names the auto-gate (declared conservative
    but auto-resolved). One finding per task. CI (audit-ci, live) enforces it.
  - Prose accord: run.md's high-risk-guard paragraph states the mechanization —
    judgment stays human at the freeze, the declared combination is enforced by
    the engine; TASK.md.tmpl documents the `risk: high` token. Synced ×3.
  - Existing boards unaffected: no legacy task declares `risk: high`, so the live
    45-task audit stays clean and every existing gate path behaves identically.
Reject:
  - gate PASS on `risk: high` + no autonomy token (default auto) -> "unguarded_high_risk_auto"
  - gate PASS on `risk: high` + explicit `autonomy: auto`        -> "unguarded_high_risk_auto"
  - gate RISK-ACCEPTED on an unguarded high-risk header           -> "unguarded_high_risk_auto"
  - a done task whose header says `risk: high` but not conservative, or whose
    gate record reviewer is the auto-gate -> audit exit 1, code "unguarded_high_risk_auto"
After:
  - a high-risk/method-defining scope left at `auto` cannot COMPLETE (engine) and
    cannot HIDE (audit + CI); the v6 dogfood blind-spot — the whole method built
    at auto with no friction — is closed by machinery, not discipline
Assumptions — least-sure first:
  ⚠ the honest limit: an UNDECLARED high-risk scope still passes — the engine
    enforces the declared case only; declaring `risk: high` remains the human's
    judgment at the freeze (same shape-not-engagement honesty as gate-audit) —
    least sure because a lazy front could simply never declare; if wrong: the
    review-checklist task (v14) puts "is this scope high-risk?" on the freeze
    checklist, making the declaration prompt explicit
  - [x] `autonomy:` absent means auto (v7 default) — so absence + risk: high is
    unguarded BY DESIGN; confirmed against run.md's dial section
  - [x] new finding code is additive to gate-audit's frozen grammar — confirmed:
    MILESTONE shared contracts names high-risk-signal as a consumer of that seam

<!-- EXIT: every rule stated, every rejection named; assumptions ranked least-sure first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

```gherkin
Scenario: unguarded high-risk completion is refused (default auto)
  Given a task at verify whose header declares `risk: high` and no autonomy token
  When `add.py gate PASS <slug>` runs
  Then it dies naming unguarded_high_risk_auto
  And state is untouched (phase still verify, gate still none)

Scenario: explicit auto is refused the same way
  Given the same task with `autonomy: auto` written out
  When gate PASS runs
  Then the same refusal, state untouched

Scenario: RISK-ACCEPTED cannot bypass the guard
  Given the same unguarded header
  When `add.py gate RISK-ACCEPTED <slug> --owner ... --ticket ... --expires ...` runs
  Then the same refusal, state untouched

Scenario: HARD-STOP is never blocked
  Given the same unguarded header
  When `add.py gate HARD-STOP <slug>` runs
  Then it records (stopping is always allowed)

Scenario: guarded high-risk completes normally
  Given the header declares `risk: high · autonomy: conservative`
  When gate PASS runs (the human led the gate)
  Then it records PASS and the task is done

Scenario: ordinary tasks are untouched
  Given a task with no risk token
  When gate PASS runs
  Then it behaves exactly as today (regression)

Scenario: audit catches the unguarded record
  Given a done task whose header was edited to drop `autonomy: conservative`
        after a guarded gate (post-gate tampering)
  When `add.py audit` runs
  Then exit 1 with finding code unguarded_high_risk_auto naming the task

Scenario: audit catches an auto-resolved high-risk gate
  Given a done `risk: high · autonomy: conservative` task whose GATE RECORD
        reviewer names the auto-gate
  When audit runs
  Then exit 1 with the same code

Scenario: audit stays silent where it should
  Given a guarded high-risk task with a human reviewer, and ordinary tasks with
        auto-resolved gates
  When audit runs
  Then no unguarded_high_risk_auto finding (live 45-task board stays clean)
```

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
HEADER GRAMMAR (TASK.md, text before the first "## "):
  risk: high                  optional token; declares high-risk/method-defining
  autonomy: conservative      the existing dial token; absent = auto (v7)

add.py gate <PASS|RISK-ACCEPTED> <slug>
  header has risk:high AND lacks autonomy:conservative
    -> exit 1, error "unguarded_high_risk_auto: ..." · state UNTOUCHED
  otherwise -> unchanged behavior (byte-identical paths for no-risk-token tasks)
  HARD-STOP -> always recordable (never block the stop path)

add.py audit [--json]
  NEW finding code (additive value; {task, code, detail} shape unchanged):
    unguarded_high_risk_auto — risk:high ∧ (header lacks autonomy:conservative
      OR GATE RECORD reviewer names the auto-gate); max one per task
  exit semantics unchanged (0 clean / 1 findings)

PROSE ACCORD (synced ×3): run.md high-risk-guard paragraph states the split —
judgment (declaring risk: high) stays human at the freeze; the declared
combination is enforced by gate + audit + CI. TASK.md.tmpl documents the token.

HONEST LIMIT (named, like gate-audit's): an undeclared high-risk scope passes —
declaration is the human seam; the engine enforces what was declared.
GUARD: add-method/tooling/test_high_risk_signal.py — gate refusal state-purity,
HARD-STOP path, audit matrix, prose anchors ×3. Engine change -> md5 resync ×3.
```

Status: FROZEN @ v1 — approved by Tin, 2026-06-05 (one-approval front via AskUserQuestion; ⚠ undeclared-scope honest limit + absent-dial-counts-unguarded flags surfaced and accepted; conservative dial on this task itself)   <!-- Changing a frozen contract = change request back to SPECIFY. -->

<!-- EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the bundle's least-sure flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — red safety net ▸ docs/06-step-4-tests.md

Coverage target: every Must + Reject has a test; the 401-test suite stays green
(no legacy task declares the token, so zero behavior change outside it).
Plan (one test per scenario, asserting behavior not internals):
  - test_gate_refuses_default_auto: arrange verify-phase task, append `risk: high`
    to header / act gate PASS / assert SystemExit + code named + state untouched (RED)
  - test_gate_refuses_explicit_auto: same with `autonomy: auto` written (RED)
  - test_gate_refuses_risk_accepted_bypass: full waiver flags supplied, still
    refused on the unguarded header (RED)
  - test_gate_hard_stop_always_allowed: unguarded header, HARD-STOP records (RED)
  - test_gate_allows_guarded: `risk: high · autonomy: conservative` -> PASS lands (RED)
  - test_gate_ordinary_unaffected: no token -> PASS lands exactly as today (guard)
  - test_audit_flags_tampered_header: gate guarded, then strip `autonomy:
    conservative` from header / audit -> exit 1 + code (RED)
  - test_audit_flags_auto_reviewed_record: guarded header, REC_AUTO reviewer
    (constants imported from test_gate_audit — one source of truth) -> finding (RED)
  - test_audit_silent_guarded_human + ordinary-auto: no finding; live-board-shape
    fixture stays clean (guards)
  - test_run_md_states_mechanized_guard / test_template_documents_risk_token:
    prose anchors + byte parity ×3 (RED)

Tests live in: `add-method/tooling/test_high_risk_signal.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): the guard reads tokens, never judges scope; the
refusal path must leave state byte-identical (no partial write before _die); the
HARD-STOP path must stay reachable from every header shape.
Code lives in: `add-method/tooling/add.py` (cmd_gate + _audit_findings + header helper) · `add-method/skill/add/run.md` · `add-method/tooling/templates/TASK.md.tmpl` · synced ×3
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + blind-spot checks ▸ docs/08-step-6-verify.md

- [x] all tests pass — suite 413/413 OK (was 401; +12 in test_high_risk_signal.py)
- [x] coverage did not decrease — 7 red→green + 5 green-by-design guards;
      check 203/0 (4 pre-existing warnings)
- [~] no test or contract was altered during build — DISCLOSED: one harness
      repair in _assert_triplet (the twin path computed `.add/templates/…`,
      dropping `tooling/` — the test ERRORED on a nonexistent path pre-assert;
      fixed the path, assertions untouched). §3 contract untouched; the run.md
      reflow fixed the BUILD output, never the matcher.
- [x] concurrency / timing of the risky operation is safe — the refusal fires
      BEFORE any state mutation reaches save_state (state-snapshot purity
      asserted byte-exactly in test_gate_refuses_default_auto); the audit stays
      read-only; no shared mutable state between gate and audit paths
- [x] no exposed secrets, injection openings, or unexpected dependencies —
      pure stdlib regex token reads; one in-build DESIGN REFINEMENT disclosed
      (not security residue): tokens are read with HTML comments STRIPPED,
      because the new template documents `risk: high` inside a comment and an
      unstripped read would have declared EVERY new task high-risk — a comment
      is never a declaration (stated in the template; ordinary-task regression
      test pins it)
- [x] layering & dependencies follow CONVENTIONS.md — engine change synced ×3
      (md5 c2381269e4e080bcd70468f50ff55406); run.md + TASK.md.tmpl ×3; the
      finding grammar consumed additively ({task, code, detail} unchanged)
- [x] a person reviewed and approved the change — HUMAN-LED BY CONSTRUCTION
      (risk: high · autonomy: conservative on this task's own header) and
      confirmed by Tin via AskUserQuestion; the recording `gate PASS` itself ran
      the new guard against this header and completed only because the dial is
      lowered — the rule proved itself on its own gate

### GATE RECORD
Outcome: PASS — human-confirmed (conservative dial; disclosures accepted:
  comment-stripping refinement · harness path repair · undeclared-scope honest
  limit carried to review-checklist)
Reviewed by: Tin (human gate) · date: 2026-06-05

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): whether new fronts actually DECLARE risk: high
where scope warrants (the honest limit — review-checklist adds the prompt); false
positives from prose mentions of the tokens in header regions (comments are
stripped; blockquote prose is not — keep headers terse); the first real-world
refusal (does the error message route the human correctly to the dial).
Spec delta for the next loop: v14 exit criterion 3 CLOSED — the high-risk guard
is engine+audit+CI, not prose; review-checklist should add the "is this scope
high-risk?" prompt at the freeze seam to shrink the undeclared-scope limit.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
  - [SDD · folded] when a guide documents a machine-read token, the reader must
    ignore documentation forms of it — strip comments before token matching, or
    every scaffold self-triggers (evidence: the template's `risk: high` comment
    would have declared every new task high-risk; caught in build, pinned by the
    ordinary-task regression test)
  - [ADD · folded] a method-defining task should dogfood the rule it ships in its
    own header — the gate that records it becomes the rule's first live proof
    (evidence: high-risk-signal's own `gate PASS` ran the new guard and completed
    only because its dial was lowered)
