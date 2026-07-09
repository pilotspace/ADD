# TASK: Scope-gate repair path: default-scope fail-fast nudge + exact 3-step repair recipe in the scope_violation error

slug: scope-gate-repair-path · created: 2026-07-09 · stage: mvp
milestone: risk-proportional-ceremony
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): add-method/tooling/add.py:`_build_entry` (~1092, the tests→build crossing; snapshots §5 scope UNCONDITIONALLY and SILENTLY — even the template-default `./src/` which resolves to the TASK DIR's src, never the real project files) · `_heal_or_escalate` (~5351; its return_to_build print gives ONE generic advice line — "Revert the tampered file or rebuild src honestly" — right for source="scope-tamper"/"refute-read", WRONG for source="scope" whose repair is fix-§5 → re-cross → re-gate) · `_declared_scope` (~5327, resolution grammar — untouched) · scope check `_verify_scope` reason string (~5347)
Context (working folder): mr-lever-sonnet/rep2 transcript — gate PASS failed 3×on scope_violation, agent then grepped engine source ~10 turns to discover `re-cross`; ~15 wasted turns
Honors (patterns / conventions): tripwire/scope MECHANICS are frozen behavior (audit-hardening, verify-integrity) — this task changes MESSAGES + adds ONE pre-crossing warning, never the enforcement · warnings print to stdout, never block (cmd_check convention) · banned-slang string guard
Seams consulted: .add/SEAMS.md#scope-token-grammar (why `./src/` default resolves task-dir-relative — the trap's root)
Anchors the contract cites: `_build_entry` · `_heal_or_escalate` · `_verify_scope`'s scope_violation reason
Issues/Risks (→ feed §1): (1) legit `./src/` tasks EXIST (standalone fast lane; template says "Code lives in: ./src/") — the nudge must WARN, never refuse. (2) advice text must branch by heal `source` — tamper advice stays byte-identical (test_scope_violation_heal pins it? enumerate red-first). (3) heal loop and HEAL_CAP semantics untouched.
Related intent: milestone risk-proportional-ceremony LOOP-2 defect (a) — the scope_violation death spiral; exit criterion mean add.py calls ≤12
Ground SHA: 5a76222 — line refs "as of" this commit

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: scope-gate repair path — a scope_violation names its own exact repair; the crossing warns when §5 Scope is still the template default
Framings weighed: message-layer-only (chosen — enforcement untouched, smallest diff, zero floor risk) · auto-suggest scope from git-touched files (rejected: the engine can't know intent; a wrong auto-scope grants wrong cover) · make default-scope a hard refusal (rejected: legit ./src/ fast-lane tasks exist)
Must:
<must>
  - M1 the tests→build crossing (_build_entry) prints a WARNING when the declared §5 Scope line still carries the template placeholder (`<fill before the §3 freeze`) — naming the trap (./src/ = the TASK dir, not the project) and the fix (edit the §5 line to real project paths; the collapsed `re-cross --by <name>` recipe if already crossed)
  - M2 a scope_violation heal (source=="scope") prints the exact 3-step repair recipe: 1. edit the §5 Scope line to cover the real paths · 2. `add.py re-cross --by <name>` (re-snapshots scope + tripwire) · 3. `add.py advance` then `add.py gate PASS`
  - M3 tamper/refute-read heal advice stays byte-identical; HEAL_CAP, exit codes (3 redo · 1 die), heal counter mechanics untouched
  - M4 3-tree parity + ENGINE_MD5 re-pin + full suite green
</must>
Reject:
<reject>
  - weakening/skipping the scope snapshot or the violation refusal itself -> forbidden (enforcement layer untouched)
  - a warning that blocks a legit ./src/ crossing -> forbidden (warn = stdout line, exit unchanged)
</reject>
After:
<after>
  - an agent hitting scope_violation can repair in 3 commands from the error text alone — zero engine-source reads
  - a task crossing with the untouched template scope line sees the trap named BEFORE building
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the template-placeholder detection (`<fill before the §3 freeze` on the Scope line) is the right "still default" signal — lowest confidence because an agent may delete the comment but keep `./src/` deliberately; if wrong: a missed warning (cost: one benchmark rep's death spiral persists) — acceptable, the M2 recipe still catches it at the violation itself
  - [x] existing tests pin the heal print — test_scope_violation_heal.py asserts on return_to_build text (red-first enumeration will show exactly which; updated in TESTS phase)
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: default-scope crossing warns   # M1
  Given a task at tests whose §5 Scope line still carries the template placeholder
  When it crosses tests->build (advance)
  Then stdout contains a warning naming the ./src/-is-the-task-dir trap and the §5 fix
  And the crossing still succeeds (exit 0, phase=build, snapshot taken as today)

Scenario: real-scope crossing stays silent   # M1 guard
  Given a task whose §5 Scope names real project paths (no placeholder)
  When it crosses tests->build
  Then no default-scope warning is printed

Scenario: scope violation names its repair   # M2
  Given a built task that touched files outside its declared §5 Scope
  When the verify gate refuses with scope_violation (return_to_build)
  Then the error text contains the 3 steps: edit §5 Scope · re-cross --by <name> · advance + gate PASS
  And the heal attempt counter increments exactly as today (exit 3)

Scenario: tamper advice unchanged   # M3
  Given a task whose tripwire detects a tampered test file (source=scope-tamper)
  When return_to_build fires
  Then the advice line is byte-identical to today's ("Revert the tampered file...")
  And HEAL_CAP escalation (heal_exhausted) is unchanged
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
_build_entry(...)   # tests->build crossing — ADDITIVE stdout only
  §5 Scope line contains the template placeholder "<fill before the §3 freeze"
    -> print warning: "warning: §5 Scope is still the template default — `./src/` resolves to
       THIS TASK's dir (.add/tasks/<slug>/src/), not your project files; edit the §5 Scope line
       to the real paths your build may touch (or it will trip scope_violation at the gate;
       repair then: edit §5 -> add.py re-cross --by <name>)"
    -> crossing behavior otherwise byte-identical (exit, snapshot, state)
  no placeholder -> zero new output

_heal_or_escalate(source=="scope")   # message layer only
  return_to_build print gains the recipe (replacing the generic revert advice FOR THIS SOURCE):
    "repair: 1. edit the §5 Scope line to cover the real paths · 2. add.py re-cross --by <name>
     (re-snapshots scope + tripwire) · 3. add.py advance, then add.py gate PASS"
  source in {"scope-tamper","refute-read", ...} -> advice byte-identical to today
  exit codes (3 / 1), HEAL_CAP, counter increments, heal history entries: unchanged

Schema: no state-shape change; heal history entry dicts byte-compatible
```

Glossary deltas: none
Least-sure flag surfaced at freeze: [spec] the placeholder-string detection is the weakest part — an agent that deletes the template comment but keeps a wrong `./src/` gets no crossing warning; accepted because the M2 recipe still names the repair AT the violation, which is the death-spiral killer. Cost if wrong: one warning missed, never a wrong refusal.
Status: FROZEN @ v1 — approved by Tin Dang
Reported: <yes — the freeze report (banner/ARC/SHAPE) rendered before this froze | no>

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every §2 scenario = 1 test; both new message branches covered
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_default_scope_crossing_warns: task with template §5 line / advance tests->build / assert warning text + exit 0 + phase build + snapshot exists · covers: M1
  - test_real_scope_crossing_silent: task with real §5 paths / cross / assert no "template default" text · covers: M1 guard
  - test_scope_violation_names_repair: declared scope, touch outside, gate / assert exit 3 + "re-cross --by" + "edit the §5 Scope" + attempts==1 · covers: M2
  - test_tamper_advice_unchanged: tamper a tripwired test file, gate / assert exit 3 + "Revert the tampered file" + no "re-cross --by" recipe line · covers: M3
  - (existing) test_scope_violation_heal.py / test_scope_gate_enforce.py pinned strings — red-first enumeration; update only asserts invalidated by the frozen message change
</test_plan>

Tests live in: `add-method/tooling/test_scope_repair_path.py` (new, sibling convention) · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `.add/tooling/engine_pin.py` `add-method/src/add_method/_bundled/tooling/engine_pin.py` `add-method/tooling/test_scope_repair_path.py` `add-method/tooling/test_scope_violation_heal.py` `add-method/tooling/test_scope_gate_enforce.py`
Strategy (ordered batches): 1. red suite (new file + enumerate pinned-string breakage in the 2 existing scope suites). 2. `_build_entry`: placeholder check on the §5 Scope line -> warning print (after the snapshot block, before the completing return). 3. `_heal_or_escalate`: branch the advice tail by `source` ("scope" -> recipe; else today's text verbatim). 4. twins sync + re-pin + full suite to file.
Approach (domain strategy): message-layer repair — the enforcement stays byte-identical; only WHAT THE ERROR TEACHES changes. Mirrors first-call-ergonomics: the engine hands the exact next command at the moment of failure.
Data strategy: none — no state shape touched; heal entries byte-compatible.
Pattern: extends the exact-command surface (status-guide-fold glossary) to the failure path.
Optimization stance: token-cost (turn-count) — kill the ~15-turn death spiral; budget = LOOP-2 criterion. ⚠ least-trusted facet: placeholder detection breadth (flagged at freeze). correctness-first otherwise.

Persona (required): methodology-engine-dev
Spawn isolation (default): none — INLINE build by the orchestrator (user speed directive 2026-07-10; single-file message-layer diff)
Known-problem fixes: banned-slang string guard · `| tail` exit masking · prepare_bundle deletes bundled engine_pin (git-restore + re-pin) · __pycache__ parity flake · SEAMS line-pin drift (re-pin after) · pinned-string churn in scope suites (red-first enumeration)
Strategy actually used: <fill at VERIFY — the strategy you ACTUALLY used (or "as planned"); harvested into the §7 Decisions (ADR) block as the [AI] build decision>
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `add-method/tooling/add.py` (canonical; twins synced at build end)
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass   (full suite Ran 3350 — OK; new suite 5/5; scope suites green post-sync)
- [x] coverage did not decrease   (5 new tests; zero removed/weakened; both message branches covered)
- [x] no test or contract was altered during build   (suite written red-first in TESTS; §3 untouched post-freeze; zero existing-test edits needed — the old advice string was not pinned)
- [x] the green was EARNED, not gamed — refute-read below
- [x] concurrency / timing safe   (advisor lens 2)
- [x] no exposed secrets / injection / new deps   (advisor lens 1 — print-only)
- [x] layering follows CONVENTIONS.md   (advisor lens 3)
- [ ] a person reviewed and approved the change   (human backstop — spot-audit welcome; auto-gate below)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] a live smoke: template-scope crossing printed `warning: task 't1' §5 Scope is still the template default — ./src/ resolves to THIS TASK's dir...re-snapshot: add.py re-cross --by <name>`; forced violation printed `repair: 1. edit the §5 Scope line...2. add.py re-cross --by <name>...3. add.py advance, then add.py gate PASS` exit=3 attempt 1 of 3 (smoke-sgrp2, 2026-07-10); tamper advice byte-pinned by test_tamper_advice_unchanged
- [x] 3 trees byte-identical + ENGINE_MD5 re-pinned — md5 `14787483…` ×3
- [x] full suite Ran 3350 in 255.9s — OK (/tmp/sgrp-fullsuite.txt)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — no new symbol; two in-place message branches (the `_build_entry` warning block · `_heal_or_escalate` advice branch), both exercised by the new suite
- [x] DEAD-CODE (code) — none introduced; both branches reachable and tested (warn/silent · scope/tamper)
- [x] SEMANTIC (prose / non-code) — new stdout strings read in full: no banned slang; the recipe's 3 commands verified against real CLI signatures (re-cross --by exists, gate PASS exists)

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] every symbol §3 CONTRACT cites still resolves — `_build_entry` (~1092, warning at ~1160) · `_heal_or_escalate` (advice branch ~5395) · `_verify_scope` reason untouched — grep-confirmed post-build
- [x] anchors moved: `_declared_scope` 5206→5219 → SEAMS.md re-pinned x14 (this task's own warning block above it)

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self (orchestrator; built inline per user speed directive) · adversarially checked: the M1 guard tests prove the warning does NOT fire on real/undeclared scope (no over-warn); M2 test asserts the heal counter still increments and exit stays 3 (message-only, no enforcement drift); M3 test asserts the scope recipe never leaks into tamper advice AND today's tamper text survives byte-for-byte; live smoke reproduced the exact benchmark death-spiral sequence and the recipe now names all 3 repair commands

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self (orchestrator)
1. Security: CLEAR — print-only branches; no new input parsing, writes, or subprocess; enforcement (snapshot, HEAL_CAP, exit codes) byte-identical and test-pinned
2. Concurrency: CLEAR — no new state access; the warning reads the already-loaded §5 body
3. Architecture: CLEAR — message layer extends the exact-command surface convention; no new symbol, no parallel emitter
Verdict: PASS
Residue: none
Binding: advisory — mechanical (stdout messages only)

### GATE RECORD
Reported: yes — live-smoke stdout + suite lines rendered to the user before recording
Outcome: PASS
Reviewed by: auto-gate (autonomy: auto — inline build by orchestrator, refute-read EARNED, advisor 3-lens CLEAR/PASS, residue none, sensitivity mechanical; human backstop box open) · date: 2026-07-10

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency — the §5 Optimization stance budget is a monitor here, not just an intention>

### Decisions (ADR)
- [AI] specify — chose message-layer-only; rejected auto-suggest scope from git-touched files (rejected: the engine can't know intent; a wrong auto-scope grants wrong cover) · make default-scope a hard refusal (rejected: legit ./src/ fast-lane tasks exist)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — approach: message-layer repair — the enforcement stays byte-identical; only WHAT THE ERROR TEACHES changes. Mirrors first-call-ergonomics: the engine hands the exact next command at the moment of failure.
- [AI] build — data strategy: none — no state shape touched; heal entries byte-compatible.
- [AI] build — pattern: extends the exact-command surface (status-guide-fold glossary) to the failure path.
- [AI] build — optimization stance: token-cost (turn-count) — kill the ~15-turn death spiral; budget = LOOP-2 criterion. ⚠ least-trusted facet: placeholder detection breadth (flagged at freeze). correctness-first otherwise.
- [AI] build — strategy used: as planned
- [AI] verify — gate PASS (reviewed by auto-gate (autonomy: auto — inline build by orchestrator, refute-read EARNED, advisor 3-lens CLEAR/PASS, residue none, sensitivity mechanical; human backstop box open))

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

