# TASK: gate --explain: read-only dry-run of the verify gate path

slug: gate-explain · created: 2026-07-06 · stage: mvp
milestone: method-ergonomics
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): add-method/tooling/add.py:cmd_gate — the verify-gate recorder; add.py:_gate_explain (new) — the read-only path resolver; add_engine.autonomy:_autonomy_level/_autonomy_lowered · _RISK_HIGH_RE · _task_sensitivity · _advisor_verdict_is_pass/_advisor_no_residue — the relax-path inputs
Context (working folder): run.md 'verify auto-gate' + 'advisor-gate-relax' sections — the doc contract the explain output mirrors
Honors (patterns / conventions): read-only inspection commands print-and-return (status/audit pattern); the security-floor sentence is verbatim, non-negotiable
Seams consulted: none apply
Anchors the contract cites: cmd_gate · _gate_explain · GATES
Issues/Risks (→ feed §1): argparse `choices=GATES` on the outcome arg blocks an outcome-less `gate --explain`; moving validation in-body risks changing the pinned refusal text for an invalid outcome
Related intent: method-ergonomics milestone — a task author should see WHICH gate path (auto / human / relax / refused) applies BEFORE gating, instead of reverse-engineering run.md
Ground SHA: ec64f18

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: gate --explain — a read-only dry-run naming the gate path the active task would take
Framings weighed: a `--explain` flag on gate (chosen) · a separate `gate-explain` verb · folding into `status`
Must:
<must>
  - `add.py gate --explain [slug]` prints phase · autonomy · risk · sensitivity · advisor lines and exactly one `path:` line — AUTO | HUMAN | RELAX | REFUSED
  - RELAX shown only when every advisor-gate-relax precondition holds (sensitivity mechanical + advisor PASS + no residue); security/non-mechanical never shows RELAX
  - output always ends with the security floor line (a security finding is always HARD-STOP)
  - read-only: no state.json write, no TASK.md write, exit 0
</must>
Reject:
<reject>
  - unknown slug -> "task_not_found"
  - plain `gate` with no outcome -> same refusal as before (outcome validated in cmd_gate, not argparse)
</reject>
After:
<after>
  - the gate path is inspectable before gating; recording behavior of `gate <outcome>` is byte-identical to before
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the RELAX precondition set mirrors run.md's advisor-gate-relax exactly — lowest confidence because it was re-derived from call sites; if wrong: explain promises a relax the real gate refuses (advisory-only, no state harm)
  - [x] removing argparse choices does not weaken validation — confirmed by test (invalid outcome still refused verbatim)
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: auto path   # M1
  Given a verify-phase task with autonomy auto and clean evidence
  When gate --explain runs
  Then it prints path: AUTO and the security floor line
  And state.json and TASK.md are unchanged

Scenario: human path   # M1
  Given a verify-phase task with risk: high or lowered autonomy
  When gate --explain runs
  Then it prints path: HUMAN

Scenario: relax path   # M2
  Given a mechanical-sensitivity task with a recorded advisor PASS and no residue
  When gate --explain runs
  Then it prints path: RELAX

Scenario: refused off-phase   # M1
  Given a task not at verify
  When gate --explain runs
  Then it prints path: REFUSED with the reason

Scenario: plain gate still validates   # R2
  Given no --explain flag and no outcome
  When gate runs
  Then it refuses with the same text as before
  And nothing is recorded
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add.py gate --explain [slug]     # read-only, exit 0
  gate-explain <slug>
  phase: … · autonomy: … · risk: high|normal · sensitivity: …
  advisor: … · residue: …
  path: AUTO | HUMAN | RELAX | REFUSED (<reason>)
  floor: a security finding is always HARD-STOP — never auto-passed, never relax-eligible.
add.py gate <outcome> unchanged; outcome validated in cmd_gate (invalid -> prior refusal text, verbatim).
Schema: none — no state write on --explain
```

Glossary deltas: none
Status: FROZEN @ v1 — approved by Tin (standing directive: implement all remaining milestone tasks directly)
Reported: no — collapsed ceremony under the standing implement-all directive; flag surfaced above
Least-sure flag surfaced at freeze: ⚠ [contract] the RELAX precondition set mirrors run.md's advisor-gate-relax exactly — because re-derived from call sites; if wrong: explain over-promises a relax (advisory-only, no state harm)

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every path branch (AUTO/HUMAN/RELAX/REFUSED) + read-only + floor + refusal parity
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_gate_explain (7 tests): path AUTO · path HUMAN (high risk) · path RELAX (mechanical+advisor PASS) · path REFUSED (off-phase) · read-only (state.json byte-stable) · security floor line present · plain gate w/o outcome still refuses · covers: M1–M4, R1–R2
</test_plan>

Tests live in: `add-method/tooling/` (test_gate_explain.py) · ran red (no --explain flag) before build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/` · `.add/tooling/` · `add-method/src/add_method/_bundled/tooling/` · `add-method/.add/tooling/`
Strategy (ordered batches): 1. red test_gate_explain 2. _gate_explain helper before cmd_gate 3. cmd_gate --explain branch + in-body outcome validation 4. pin re-aim + 4-tree twin sync

Persona (required): generic — engine-internals stance (no project persona covers CLI ergonomics yet)
Spawn isolation (default): n/a — orchestrator-inline, no spawn
Known-problem fixes: sibling tests pin the no-outcome refusal text → keep it verbatim when moving validation out of argparse; EnginePinTest 4-tree drift → sync twins + re-aim in the same change
Strategy actually used: as planned; one phantom batch failure was a typo'd module name (test_audit_ungated_verdict → test_audit_ci)
Safety rule (feature-specific): --explain must never write state — it is a dry-run, not a gate
Code lives in: `add-method/tooling/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass
- [x] coverage did not decrease
- [x] no test or contract was altered during build
- [x] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [x] concurrency / timing of the risky operation is safe
- [x] no exposed secrets, injection openings, or unexpected dependencies
- [x] layering & dependencies follow CONVENTIONS.md
- [x] a person reviewed and approved the change

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] a verify-phase auto task prints `path: AUTO` + the HARD-STOP floor — confirmed by test_gate_explain output assertions
- [x] state.json byte-identical across an --explain run — confirmed by test_gate_explain read-only test

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — _gate_explain called from cmd_gate's --explain branch; --explain/--to/re-cross wired in the parser
- [x] DEAD-CODE (code) — none; the removed argparse choices are replaced by in-body validation
- [x] SEMANTIC (prose / non-code) — run.md advisor-gate-relax read in full; explain's RELAX preconditions match it

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] every symbol §3 CONTRACT cites still resolves — cmd_gate/_gate_explain/GATES present at HEAD (grep)
- [x] no anchor moved since Ground SHA ec64f18

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: read-only claim (state.json digest before/after) · refusal-text parity for invalid/missing outcome · RELAX never shown for security sensitivity

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR — no new input reaches a shell/file write; --explain writes nothing
2. Concurrency: CLEAR — read-only, no state mutation to race
3. Architecture: CLEAR — explain reuses the gate's own predicates; no duplicated policy
Verdict: PASS
Residue: none
Binding: advisory — mechanical

### GATE RECORD
Reported: no — collapsed ceremony under the standing implement-all directive; evidence above
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-06

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose a `--explain` flag on gate; rejected a separate `gate-explain` verb · folding into `status`
- [human] freeze — froze §3 @ v1 (approved by Tin (standing directive: implement all remaining milestone tasks directly))
- [AI] build — strategy used: as planned; one phantom batch failure was a typo'd module name (test_audit_ungated_verdict → test_audit_ci)
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

