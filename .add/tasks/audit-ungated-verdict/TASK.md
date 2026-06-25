# TASK: _audit_findings flags a §6 verdict recorded with no engine gate (gate=none)

slug: audit-ungated-verdict · created: 2026-06-25 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. Multi-component repo (monorepo/multi-repo)? add a `component: <name>` line (declared in `.add/components.toml`) to ADD that component's root to your §5 Scope; omit for single-component projects (byte-identical default). -->
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
  - `add-method/tooling/add.py:_audit_findings` (5882) — the seam-audit core. At ~5915 it parses `outcomes = _AUDIT_OUTCOME_RE.findall(s6)`; `len != 1` → `malformed_gate_record`; `elif gate != "none" and outcomes[0] != gate` → `gate_record_mismatch`. THE GAP (F13): when `len(outcomes)==1` but `state.gate=="none"`, NEITHER branch fires — a §6 verdict the engine never recorded passes clean. Fix site: add an `elif gate == "none"` arm.
  - `add-method/tooling/add.py:cmd_gate` (1488) — the ONLY writer of `state.tasks[slug].gate` (+ `gate_actor`); sets `phase="done"`. Confirms: a real engine gate ALWAYS sets gate≠none. So done/observe + gate=="none" = the verdict was NOT engine-recorded.
  - `add-method/tooling/add.py:cmd_advance` — crosses verify→observe→done with NO gate check at those steps, so a task can reach done/observe ungated via plain `advance` (then a hand-written §6 PASS is the F13 bypass). Not grandfather-only.
  - `add-method/tooling/add.py:_audit_findings` line 5898 — the skip: `phase not in (done,observe) and gate=="none"` → continue. So a done/observe task IS audited even with gate=="none" (it must already pass unstamped_freeze + exactly-1-outcome).
Context (working folder):
  - `add-method/tooling/test_gate_audit.py` — `GateAuditTest`: `_mk_done(slug, sec3, sec6, gate)` gates via the engine then overwrites §3/§6; `_codes(out)` reads `--json` finding codes. The new test needs an UNGATED arrangement (advance/override to done/observe WITHOUT `gate`, then a §6 verdict).
  - Engine mirrored ×3 under ENGINE_MD5 → change re-mirrors (_bundled + .add) + re-pins.
Honors (patterns / conventions):
  - Audit checks record SHAPE, never re-decides an outcome; PURE read. "Never retro-red the board" — but here the live board is clean (all 84 done = gate PASS; 0 grandfathered), and the method MANDATES the engine gate (constraint 4: every Verify ends in exactly one RECORDED outcome), so an ungated §6 verdict is a real method violation, not a false positive.
  - red/green TDD; 3-tree mirror + ENGINE_MD5 re-pin; new finding code wired into the existing findings list (no closed-set code registry to update — verified).
Anchors the contract cites: `_audit_findings` · `_AUDIT_OUTCOME_RE` · `state.tasks[slug].gate` · the new finding code (`ungated_verdict`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `_audit_findings` flags a task whose §6 GATE RECORD carries a real verdict (exactly one Outcome line) while `state.json` recorded NO engine gate (`gate=="none"`) — a verdict written without the engine ever gating it. New finding code `ungated_verdict`.
Framings weighed: new-code-unconditional (chosen) · reuse-gate_record_mismatch · grandfather-escape
  - chosen: a distinct `ungated_verdict` code, fired whenever an audited (done/observe) task has exactly 1 §6 outcome AND gate=="none". Precise signal ("the engine never gated this") distinct from gate_record_mismatch ("§6 and state disagree on WHICH outcome"). The live board is clean (0 affected), and the method mandates the gate, so it is method-correct, not a false positive.
  - reuse-gate_record_mismatch: fold it into the existing code with a different detail string. Rejected — conflates "no gate at all" with "two different verdicts"; weaker audit signal.
  - grandfather-escape: skip when the task lacks engine-era markers (so an upgrading user's hand-advanced board isn't retro-redded). Considered — but there is NO clean discriminator (a bypassed task and a grandfathered one BOTH lack gate/gate_actor), and the method always required the gate. SURFACED at freeze as the lowest-confidence decision.
Must:
<must>
  - For an audited task (phase ∈ done/observe, OR gate≠none) with exactly ONE §6 Outcome line AND state.gate=="none": emit `ungated_verdict` naming the §6 outcome and that state recorded no gate.
  - The existing arms are unchanged: 0 or 2+ outcomes → `malformed_gate_record`; gate≠none and §6≠state → `gate_record_mismatch`. The new arm fires only in the previously-uncaught `len==1 AND gate==none` cell.
  - PURE read; no re-decision of any outcome; a properly engine-gated task (gate set) never trips the new code.
</must>
Reject:
<reject>
  - `ungated_verdict` — §6 records a verdict (Outcome: X) but state.json recorded no gate (gate=none); the verdict was written without the engine gate.
</reject>
After:
<after>
  - A §6 verdict not backed by an engine gate is caught by `add.py audit`; the seam audit's gate/§6 coverage is complete across all three len×gate cells.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ Flagging UNCONDITIONALLY (no grandfather escape) will not unfairly retro-red real upgrading boards. Lowest confidence because a user who reached `done` via plain `advance` (skipping `gate`) with a hand-written §6 PASS would newly red — there is no clean marker to tell that from a deliberate bypass. I judge it method-correct (constraint 4 mandates the recorded gate) and the live board is clean (0 affected). DECISION SURFACED at freeze — the human picks unconditional vs a grandfather escape.
  - [x] no closed-set audit-code registry to update (a new code just appends to `findings`) — confirmed by grep.
  - [x] a done/observe task is already audited even at gate=="none" (line 5898 only skips OPEN fronts) — confirmed.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: a §6 verdict with no engine gate is flagged
  Given a done/observe task with state.gate=="none" and §6 with exactly one "Outcome: PASS"
  When add.py audit runs
  Then findings include ungated_verdict for that task (exit 1)
  And no outcome is re-decided (PURE read)

Scenario: a properly engine-gated task is unaffected
  Given a task gated through add.py gate PASS (state.gate=="PASS", §6 Outcome: PASS)
  When add.py audit runs
  Then ungated_verdict is NOT raised (the clean board stays clean)

Scenario: the existing arms still fire (no regression)
  Given a gated task whose §6 says HARD-STOP but state.gate=="PASS"
  When add.py audit runs
  Then gate_record_mismatch is raised (not ungated_verdict)
  And a task with 0 or 2+ §6 outcomes raises malformed_gate_record
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
_audit_findings (add.py ~5915), the §6-outcome arm — add the third cell:
    outcomes = _AUDIT_OUTCOME_RE.findall(s6)
    if len(outcomes) != 1:
        f(slug, "malformed_gate_record", f"{len(outcomes)} Outcome lines in §6 (need exactly 1)")
    elif gate != "none" and outcomes[0] != gate:
        f(slug, "gate_record_mismatch", f"§6 records {outcomes[0]} but state.json records {gate}")
+   elif gate == "none":
+       f(slug, "ungated_verdict",
+         f"§6 records {outcomes[0]} but state.json recorded no gate (gate=none) — "
+         f"the verdict was written without the engine gate")

Finding shape (unchanged): {"task": slug, "code": "ungated_verdict", "detail": "..."}
Decision: UNCONDITIONAL (no grandfather escape). PURE read; existing arms byte-unchanged.
Invariants: 3-tree mirror + ENGINE_MD5 re-pin · no closed-set code registry to update ·
            a gated task (gate set) never reaches the new arm.
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-25 (add the ungated_verdict arm, UNCONDITIONAL — no grandfather escape).
Least-sure flag surfaced at freeze: [contract] flagging unconditionally may retro-red an upgrading user's hand-advanced board (reached `done` via `advance`, §6 PASS, never gated); cost = a possibly-surprising red on upgrade. Accepted as method-correct (constraint 4 mandates a RECORDED gate) and the live board is clean (0 affected); there is no clean discriminator for a grandfather escape. Engine change → 3-tree mirror + ENGINE_MD5 re-pin.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the new cell + both controls (3 scenarios).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_ungated_verdict_flagged: arrange a done/observe task with gate=="none" and §6 "Outcome: PASS" (advance/override to done WITHOUT `gate`, write §6 with a real verdict); assert `ungated_verdict` in codes + exit 1 (RED now — no such arm)
  - test_engine_gated_task_not_flagged: a normally-gated PASS task; assert `ungated_verdict` NOT in codes (the clean board stays clean — guards over-firing)
  - test_existing_arms_unregressed: a gated task whose §6 says HARD-STOP vs state PASS → `gate_record_mismatch` (NOT ungated_verdict); a 0-outcome §6 → `malformed_gate_record`
</test_plan>

Tests live in: `add-method/tooling/test_gate_audit.py` · MUST run red (no `ungated_verdict` arm) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_gate_audit.py`   <!-- canonical engine + bundled mirror + ENGINE_MD5 pin + the audit test home; .add/tooling/add.py dogfood mirror is pruned (.add excluded), synced via prepare_bundle -->
Strategy (ordered batches): 1. add 3 tests to test_gate_audit.py (1 red ungated_verdict + 2 controls). 2. add the `elif gate == "none"` arm in _audit_findings. 3. green; mirror canonical -> _bundled + .add + re-pin ENGINE_MD5; full suite + parity green.
Safety rule (feature-specific): the new arm is an `elif` AFTER the mismatch arm — it must not shadow malformed_gate_record (len!=1) nor gate_record_mismatch (gate!=none). PURE read; touch no outcome value.
Code lives in: `add-method/tooling/add.py` (+ its two mirrors)
Constraints: do NOT change any other test or contract; allow-list packages only; ask if unclear.
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

- [x] all tests pass — full suite 1811/0 (was 1808 on main; +3 F13 tests); gate-audit class 17/17; parity + dual-tree pin green
- [x] coverage did not decrease — +3 tests (new arm + 2 controls); none removed
- [x] no test or contract was altered during build — the 3 §4 tests were authored in the tests phase (1 RED) and unchanged since; build edited only add.py (the elif arm) + engine_pin re-pin + the _bundled mirror — not the test file (no tripwire divergence)
- [x] the green was EARNED, not gamed — refute-read (manual): the red test arranges a GENUINE ungated board (admin `phase observe`, no `gate`) so state.gate=="none" while §6 has a real "Outcome: PASS"; the control `engine_gated_task_not_flagged` proves a properly-gated PASS stays clean (no over-fire); `mismatch_takes_precedence` proves the new elif sits AFTER and doesn't shadow gate_record_mismatch — not vacuous
- [x] concurrency / timing — n/a (PURE read-only audit; no IO mutation)
- [x] no exposed secrets, injection openings, or unexpected dependencies — added an f-string finding; no new imports
- [x] layering & dependencies follow CONVENTIONS.md — engine mirrored ×3, ENGINE_MD5 re-pinned 73f9609e → f1255904
- [x] a person reviewed and approved the change — Tin Dang froze v1 (ungated_verdict, UNCONDITIONAL)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `add.py audit` on a done/observe task with gate=none + a §6 verdict exits 1 with `ungated_verdict <slug>` — confirmed by test_ungated_verdict_flagged (text + --json codes)
- [x] this repo's own board stays clean — confirmed: `add.py audit` = clean (84 tasks) post-build (all are properly gated, gate=PASS)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — the new `elif gate == "none"` is the third branch of the existing outcome chain (reached only when len(outcomes)==1 AND not the mismatch case); `f(...)` is the same local emitter; reuses `outcomes`, `gate`, `slug`
- [x] DEAD-CODE — no orphaned symbol; the arm is exercised by test_ungated_verdict_flagged
- [x] SEMANTIC (code) — re-read the chain: malformed (len!=1) → mismatch (gate!=none & differ) → ungated (gate==none); the three cells are mutually exclusive and now exhaustive for len==1

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-25

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
