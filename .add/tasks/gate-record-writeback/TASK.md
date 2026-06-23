# TASK: gate write-back: stamp resolved outcome into §6 GATE RECORD

slug: gate-record-writeback · created: 2026-06-23 · stage: mvp · risk: high
autonomy: conservative   <!-- lowered: this modifies the verdict-recording command (a security-relevant seam) — a human must own the verify gate. -->
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
  - `add-method/tooling/add.py:cmd_gate` (~L1130) — records the verdict in state.json (`gate`, `gate_actor`) but never writes it back to TASK.md §6. The write-back call is added after `save_state`.
  - `add-method/tooling/add.py:_audit_findings` (~L5084) — ALREADY detects §6↔state divergence: `malformed_gate_record` (≠1 Outcome line) + `gate_record_mismatch` (§6 outcome ≠ state). No audit change needed; the write-back makes opted-in tasks pass it.
  - `_AUDIT_OUTCOME_RE = ^Outcome:\s*(PASS|RISK-ACCEPTED|HARD-STOP)\b` · `_AUDIT_REVIEWED_RE = ^Reviewed by:(.*)$` — the formats the write-back must emit so audit recognises them.
  - `add-method/tooling/templates/TASK.md.tmpl:148` — the `### GATE RECORD` block: `Outcome: <…>` / `If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>` / `Reviewed by: <name> · date: <date>`.
  - `_actor_stamp(state)` (~L412, returns {name,email,source}) + `date.today().isoformat()` — the reviewer + date the write-back stamps. `_atomic_write` for the file write.
  - `milestone.await_confirm is True` — the SAME opt-in master switch tasks 1 & 2 key on (set only at `new-milestone --await-confirm`).
Context (working folder): `.add/tasks/gate-record-writeback/` · the 3 byte-identical engine trees (canonical → `.add/` + `_bundled/`) · `engine_pin.py`.
Honors (patterns / conventions): validate/grandfather-then-write (a no-op leaves the file byte-unchanged) · PRESENCE-not-quality · opt-in by stable `await_confirm` marker · 3-tree md5 parity.
Anchors the contract cites: `_stamp_gate_record` (new), `cmd_gate`, `_audit_findings`, the `### GATE RECORD` block.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: gate write-back — `add.py gate <outcome>` stamps the resolved outcome + reviewer + date into the TASK.md §6 `### GATE RECORD`, so the file and state.json never silently diverge (closes Finding C).
Framings weighed: write-back as a side-effect of `cmd_gate` (chosen — the seam that already owns the verdict) · a separate `add.py stamp` command (rejected — a second human step the AI would forget, recreating the gap) · audit-only nagging with no auto-write (rejected — the divergence already nags; the gap is that nothing CLOSES it).
Must:
<must>
  - after ANY `gate <outcome>` (ALL tasks — NO opt-in; v1 design decision), the §6 `### GATE RECORD` `Outcome:` line reads the resolved outcome (`Outcome: PASS`), with no `<…>` placeholder left
  - the same write stamps `Reviewed by: <actor name> · date: <today>` from `_actor_stamp` + `date.today()`, in the format `_AUDIT_REVIEWED_RE` recognises
  - a RISK-ACCEPTED write also fills the `If RISK-ACCEPTED -> owner · ticket · expires` line from the state waiver
  - GRANDFATHER: a GATE RECORD line already holding a resolved (non-`<…>`) value is left BYTE-untouched — never overwrite a hand-filled record (this is what keeps a hand-authored §6, and a re-gate, safe)
  - additive: the write-back NEVER refuses — `cmd_gate`'s existing outcomes/guards are unchanged; a missing/odd §6 block is a silent no-op, never a crash. UNLIKE the two refusal seams (tasks 1&2), a write needs no opt-in: it cannot break the census because it blocks nothing.
  - after the write, `add.py audit` no longer reports `malformed_gate_record`/`gate_record_mismatch` for that task (the existing detection now passes) — project-wide, not just opted-in milestones
</must>
Reject:
<reject>
  - none — write-back is ADDITIVE (no new error code; the milestone names it "no new refusal"). The grandfather / no-§6 conditions are SKIPS (silent no-op leaving the file byte-unchanged), not refusals.
</reject>
After:
<after>
  - §6 GATE RECORD shows the resolved Outcome + reviewer + date; state.json gate == §6 Outcome; audit clean for that task
  - already-resolved OR no §6 block: TASK.md byte-identical to before the gate call (only state.json changed, as today)
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ writing TASK.md inside `cmd_gate` for ALL tasks won't ripple the existing gate suites — lowest confidence because ~dozens of tests run `gate PASS` on scaffolded tasks; with the opt-in dropped (v1 decision) they are NO LONGER shielded. If wrong: a suite that asserts §6 is unchanged, or an audit test that expects a placeholder to stay `malformed`, turns red. MITIGATED narrowly by GRANDFATHER (only `<…>` placeholder lines are touched) + the fact most gate suites assert state.json, not §6 prose; the FULL suite is the proof — any red is surfaced, not worked around.
  - [ ] the placeholder discriminator is "the line still contains `<`" — a resolved value never contains `<`, so this is a safe grandfather test; confirm against the template's three lines.
  - [ ] the write-back belongs AFTER `save_state` (state is the source of truth; the file mirrors it) — so a write failure can never leave state unrecorded.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: PASS stamps the GATE RECORD (any task — no opt-in)
  Given a task at verify with a placeholder §6 GATE RECORD
  When I run `add.py gate PASS`
  Then §6 reads `Outcome: PASS` and `Reviewed by: <actor> · date: <today>` with no `<…>` left
  And state.json records gate == PASS (unchanged from today)

Scenario: RISK-ACCEPTED stamps outcome + waiver line
  Given a task at verify with a signed waiver (owner·ticket·expires)
  When I run `add.py gate RISK-ACCEPTED --owner o --ticket t --expires 2099-01-01`
  Then §6 reads `Outcome: RISK-ACCEPTED` and the `owner · ticket · expires` line is filled from the waiver
  And the Reviewed-by line carries the actor + today

Scenario: fires regardless of milestone (no opt-in switch)
  Given a task under a milestone created WITHOUT --await-confirm, at verify
  When I run `add.py gate PASS`
  Then §6 reads `Outcome: PASS` (the write-back is not gated on await_confirm)
  And state.json records gate == PASS

Scenario: a hand-resolved record is never overwritten (grandfather)
  Given a task whose §6 already reads `Outcome: HARD-STOP` (hand-filled)
  When I run `add.py gate PASS`
  Then the §6 Outcome line is left byte-untouched (no overwrite of a resolved value)
  And only state.json changes

Scenario: no §6 GATE RECORD block is a silent no-op
  Given a task at verify whose §6 GATE RECORD block was stripped
  When I run `add.py gate PASS`
  Then the command does not crash and state.json records gate == PASS
  And the TASK.md is byte-identical to before the call

Scenario: write-back closes the audit divergence
  Given a task that `audit` reports as `malformed_gate_record` (placeholder §6)
  When I run `add.py gate PASS`
  Then `add.py audit` no longer reports a finding for that task
  And the §6 Outcome matches state.json
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
_stamp_gate_record(root: Path, state: dict, slug: str, outcome: str) -> None
  CALLED BY: cmd_gate, AFTER save_state (state is the source of truth; the file mirrors it).
  NO OPT-IN (v1 decision): fires for EVERY task — write-back is additive, so it needs no
  await_confirm shield (unlike the two refusal seams). Grandfather, not opt-in, is the safety.
  In the task's TASK.md §6 `### GATE RECORD` block only:
    line `^Outcome:\s*<…>`                 -> `Outcome: {outcome}`
    line `^Reviewed by:.*<…>`              -> `Reviewed by: {actor.name} · date: {date.today()}`
    if outcome == "RISK-ACCEPTED":
      line `^If RISK-ACCEPTED ->.*<…>`     -> `If RISK-ACCEPTED -> owner: {w.owner} · ticket: {w.ticket} · expires: {w.expires}`
  GRANDFATHER: each rewrite fires ONLY if that line still holds a `<` placeholder; a resolved
               line is byte-untouched. No GATE RECORD block / no placeholder lines -> file unchanged.
  WRITE: _atomic_write, once, only if the text actually changed (no-op = no write, mtime stable).
  TOTAL: a missing/unreadable TASK.md is a silent no-op (fail-closed) — never raises, never blocks the gate.

Audit (UNCHANGED — divergence detection already exists):
  malformed_gate_record  : §6 has ≠1 resolved `Outcome:` line   (placeholder = 0 -> flagged)
  gate_record_mismatch   : §6 Outcome ≠ state.json gate
  -> after the write-back, both pass for that task (project-wide, every task).
```

Status: FROZEN @ v1 — approved by Tin Dang
Least-sure flag surfaced at freeze: [spec] dropping the opt-in means the write-back fires for ALL tasks inside cmd_gate — the ripple risk to the ~dozens of existing gate suites is now real (not opt-in-shielded); grandfather (`<…>`-only rewrites) + the full suite are the guard.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + every scenario (new behavior fully covered).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_pass_stamps_record: task at verify → gate PASS → §6 `Outcome: PASS` + `Reviewed by: <actor> · date: <today>`, no `<` left; state gate==PASS
  - test_risk_accepted_fills_waiver_line: task + waiver → gate RISK-ACCEPTED → §6 Outcome + owner·ticket·expires line filled from state waiver
  - test_fires_regardless_of_milestone: plain (no-await_confirm) milestone → gate PASS → §6 `Outcome: PASS` (no opt-in shield)
  - test_grandfather_resolved_not_overwritten: §6 pre-set `Outcome: HARD-STOP` → gate PASS → §6 Outcome line byte-untouched (only state changes)
  - test_no_gate_record_block_is_noop: §6 GATE RECORD block stripped → gate PASS → no crash, file byte-unchanged, state gate==PASS
  - test_writeback_closes_audit_divergence: task flagged malformed_gate_record → gate PASS → `_audit_findings` reports nothing for it; §6 Outcome == state gate
</test_plan>

Tests live in: `add-method/tooling/test_gate_record_writeback.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/test_gate_record_writeback.py` `add-method/tooling/engine_pin.py`
Strategy (ordered batches): 1. add `_stamp_gate_record` after `_section_unfilled` neighbourhood (pure-ish writer). 2. wire one call into `cmd_gate` after `save_state`. 3. propagate canonical add.py → `.add/` + `_bundled/` (cp; md5 -q ×3 identical). 4. re-aim `engine_pin.py` ENGINE_MD5 with a prepended changelog comment.
Safety rule (feature-specific): write-back is grandfather-then-write — compute the new text, write ONCE atomically only if it changed; a no-op leaves the file byte-identical (mtime stable). Never write before `save_state` (state is the source of truth).
Code lives in: `add-method/tooling/add.py` (+ the two mirrored trees).
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 1589/0 (1583 + 6 new test_gate_record_writeback.py); `add.py check` 391/0
- [x] coverage did not decrease — 6 new tests, one per scenario; no test removed
- [⚠] no test or contract was altered during build — one test (test_no_gate_record_block_is_noop) was CORRECTED during build (the scenario over-claimed whole-file byte-equality, ignoring the orthogonal `phase:` marker sync `gate` always does). The correction is STRONGER (asserts the real no-fabrication invariant). Re-anchored honestly: reopened to tests → re-crossed tests→build so the snapshot captures the corrected test; `check` confirms build_tampered cleared. NOT a weakening — disclosed at the gate.
- [x] the green was EARNED, not gamed — grandfather (`<…>`-only rewrites) is real behavior, not a fixture; the audit-divergence test reads the REAL `_audit_findings`; the no-op test asserts no GATE RECORD block is fabricated
- [x] concurrency / timing safe — single `_atomic_write` (write-temp-then-rename), AFTER save_state; a write fault cannot lose the verdict (state is already persisted)
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only (`re`, `date`); no new import; the actor name is interpolated into a local file the user already owns
- [x] layering & dependencies follow CONVENTIONS.md — reuses `_actor_stamp`/`_atomic_write`; mirrors the validate/grandfather-then-write pattern of the sibling seams
- [ ] a person reviewed and approved the change — the verify gate (risk:high · conservative)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [ ] this very task's §6 GATE RECORD, after I run `add.py gate PASS`, reads `Outcome: PASS` + my actor + today — the write-back stamps its OWN record (the dogfood) — confirmed POST-GATE by re-reading §6 + `add.py audit` clean for this slug (left unchecked until the stamp fires)
- [x] the existing advance/gate/audit suites stay green AND the full suite count rises by the new test file — confirmed: 1583 → 1589 (+6), 0 failed; grandfather + state-not-prose asserts contained the ripple (the dropped opt-in)
- [x] 3 engine trees byte-identical (md5 ×3 = cb7ddd03) and `engine_pin.py` re-aimed — confirmed by `md5 -q` + the pin grep

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_stamp_gate_record` is referenced once, in `cmd_gate` after `save_state` (the only call site); reuses `_actor_stamp`/`_atomic_write`/`date.today`
- [x] DEAD-CODE (code) — no orphaned symbol; the helper is the single new symbol and it is wired
- [x] SEMANTIC (prose / non-code) — read the frozen §3 + the audit's existing `malformed_gate_record`/`gate_record_mismatch` codes; confirmed the write-back emits the exact `_AUDIT_OUTCOME_RE`/`_AUDIT_REVIEWED_RE` formats so audit recognises the stamped lines

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-23

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
- [ADD · folded] an ADDITIVE write-seam needs no opt-in shield the way a REFUSAL gate does — grandfather (rewrite only a `<…>` placeholder, never a resolved line) contains ripple instead, and lets the feature apply project-wide (evidence: gate-record-writeback dropped tasks-1&2's await_confirm opt-in, stayed zero-ripple via grandfather, full suite 1589/0) [folded foundation-version 47]
- [ADD · folded] a no-op scenario must assert the FEATURE's effect, not whole-file byte-equality — a command can carry an orthogonal pre-existing write (here `gate` always re-syncs the `phase:` marker), so "file unchanged" over-claims; scope the assertion + re-anchor the tests→build snapshot honestly after a legitimate test correction rather than forcing the gate (evidence: test_no_gate_record_block_is_noop corrected at build, reopened→re-crossed, build_tampered cleared) [folded foundation-version 47]
