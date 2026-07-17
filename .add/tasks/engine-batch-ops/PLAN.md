# TASK: Engine batch ops: advance --fill (write section + advance in one call) + status --brief

slug: engine-batch-ops · created: 2026-07-07 · stage: mvp
milestone: add-lean-loop
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): add-method/tooling/add.py:cmd_advance (guard-stacked single-step advance; --to/--skip-freeze flags; parser at sub.add_parser("advance")) · add.py:cmd_status (full orient dump) · add_engine/taskdoc.py:_phase_spans (the ONE canonical `^##\s*<n>\s*·` heading scan; body runs to next `## `/`---`) · add.py:_atomic_write (the only sanctioned write path)
Context (working folder): add-bench round-3 decomposition — 21–27 engine round-trips + ~17 TASK.md writes per milestone = 41–64% of tokens pre-code; each round-trip re-reads full context
Honors (patterns / conventions): validate-before-write (every _die precedes the first mutation) · guards never bypassed (--fill must run the IDENTICAL crossing stack) · fail-closed named errors, never tracebacks · 3-tree byte parity + ENGINE_MD5 pin (engine_pin.py) · dogfood twin add-method/.add pins its own bytes
Seams consulted: _phase_spans heading grammar (taskdoc.py docstring) — reuse it for locating the section to fill, never a second parser
Anchors the contract cites: cmd_advance · _phase_spans · _atomic_write · cmd_status
Issues/Risks (→ feed §1): (1) filling a section then a crossing guard _die-ing leaves content written but phase unmoved — must be the DOCUMENTED semantics, not an accident; (2) §body containing line-start `## `/`---` truncates in _phase_spans — a --fill payload containing them would corrupt the section map; (3) SEAMS.md line pins + lean byte fences drift on any add.py growth; (4) phase→section mapping must be explicit (ground→0 … observe→7)
Related intent: add-lean-loop MILESTONE.md task 1 — engine calls per milestone 21–27 → ≤8; trust floor untouched
Ground SHA: ff4568a

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: engine batch ops — advance --fill + status --brief
Framings weighed: extend advance with --fill (chosen — one round-trip per transition, guards intact) · a new `fill` subcommand (rejected: second round-trip defeats the purpose; new subcommand ripples into min_pillar LIFECYCLE + slang-guard spans) · agent-side batching only (rejected: leaves the engine chatty for every other agent)
Must:
<must>
  - `advance --fill <path>` (or `--fill -` for stdin) replaces the CURRENT phase's TASK.md section body (phase→§: ground→0 specify→1 scenarios→2 contract→3 tests→4 build→5 verify→6 observe→7) using the _phase_spans heading grammar, writes via _atomic_write, THEN runs the unchanged single-step advance with its full crossing-guard stack.
  - ALL-OR-NOTHING (human-chosen at freeze): a guard refusal restores TASK.md byte-identical to its pre-fill state and leaves the phase unmoved — the engine snapshots the original bytes, writes the fill, runs the unchanged guard stack, and rolls back on any refusal.
  - `status --brief` prints only the resume essentials: the active-task line (slug · phase) and the `next:` hint — no foundation/read-list/roster dump.
</must>
Reject:
<reject>
  - --fill combined with --to -> "fill_with_to_unsupported"
  - --fill payload unreadable (missing file / bad encoding) -> "fill_unreadable"
  - --fill payload containing a line-start `## ` or a bare `---` line -> "fill_body_unparseable" (would truncate the _phase_spans scan)
  - current phase's section heading absent from TASK.md -> "fill_section_missing"
  - task already at final phase -> existing "already at final phase" refusal, nothing written
</reject>
After:
<after>
  - one engine call = one drafted section + one phase transition; TASK.md section content byte-equals the payload; all existing crossing guards demonstrably still fire (freeze gate, build-entry stack, expectations guard)
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ replacing a section body never disturbs sibling sections or the `---` separators — lowest confidence because _phase_spans is a scan, not a writer; a fenced code block inside a payload could still contain `---`; if wrong: TASK.md census/freeze parsers misread downstream — cost: one corrupted task file caught by the round-trip test
  - [ ] byte fences / SEAMS line pins will bind on add.py growth — plan a compensating trim or human-signed rebaseline, never silent
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: fill and advance in one call   # M1
  Given a task at specify with drafted §1 content in a file
  When add.py advance --fill draft.md runs
  Then TASK.md §1 body byte-equals the draft and the phase is scenarios

Scenario: guard refusal rolls the fill back   # M2
  Given a task at tests with an unfrozen §3 and a §4 draft
  When advance --fill draft.md runs (tests->build crossing)
  Then the freeze gate refuses as today, TASK.md is byte-identical to before, phase stays tests
  And no state mutation precedes the refusal

Scenario: brief status   # M3
  Given an active task
  When add.py status --brief runs
  Then output contains the slug+phase line and the next: hint and is under 6 lines

Scenario: fill with --to rejected   # R1
  Given any task
  When advance --fill f --to tests runs
  Then it dies "fill_with_to_unsupported" and TASK.md is unchanged

Scenario: unreadable payload rejected   # R2
  Given --fill pointing at a missing file
  Then it dies "fill_unreadable" and TASK.md + phase are unchanged

Scenario: unparseable payload rejected   # R3
  Given a payload containing a line-start "## " or bare "---"
  Then it dies "fill_body_unparseable" and TASK.md is unchanged

Scenario: missing section heading rejected   # R4
  Given a TASK.md whose current-phase heading was hand-deleted
  Then it dies "fill_section_missing" and nothing is written
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add.py advance [slug] --fill <path|-> [--skip-freeze]
  ok  -> "filled §<n> (<phase>) · task '<slug>' phase <cur> -> <next>" + existing next-hint
  die -> fill_with_to_unsupported | fill_unreadable | fill_body_unparseable | fill_section_missing
         (guard refusals unchanged: freeze gate · build-entry stack · setup_unlocked · already-final)
  write order: snapshot TASK.md bytes -> _atomic_write(§body replaced) -> unchanged advance
               guard stack -> on ANY guard refusal: restore the snapshot byte-identical (all-or-
               nothing; the refusal message is unchanged), phase unmoved
  section map: PHASES index -> §0..§7 (ground→0 … observe→7)

add.py status [--brief]
  --brief -> exactly: the active-task resume line (slug · phase) + the `next:` hint (≤6 lines)
  (plain status unchanged, byte-identical output)

Schema: TASK.md §bodies located by the taskdoc._phase_spans grammar (the one canonical scan);
        no state.json shape change; no new files.
```

Glossary deltas: none
`Least-sure flag surfaced at freeze:` [contract] the all-or-nothing rollback path — _die exits via SystemExit, so the restore must run in a finally/except wrapper around the guard stack; if the wrapper misses an exit path, a refused crossing leaves the fill on disk (the rejected write-then-guard behavior) — cost: one escaped path caught by the M2 round-trip test.
Status: FROZEN @ v1 — approved by Tin Dang (2026-07-07, all-or-nothing variant chosen at freeze)
Reported: yes — banner/ARC/SHAPE + flag rendered in-session before the freeze

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + Reject behavior-asserted (10 tests)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_fill_writes_section_and_advances: real subprocess round-trip; §1 body byte-contains draft; phase bumps · covers: M1
  - test_fill_from_stdin: `--fill -` reads stdin · covers: M1
  - test_guard_refusal_rolls_back_byte_identical: unfrozen §3 tests->build crossing; TASK.md bytes restored; phase held · covers: M2
  - test_brief_is_slug_phase_and_next_only (+ plain-status-unchanged guard) · covers: M3
  - test_fill_with_to_rejected · covers: R1
  - test_fill_unreadable_rejected · covers: R2
  - test_fill_unparseable_body_rejected (line-start "## " AND bare "---") · covers: R3
  - test_fill_section_missing_rejected · covers: R4
  - test_three_trees_byte_identical: parity fence
</test_plan>

Tests live in: `add-method/tooling/test_engine_batch_ops.py` · red 7/10 pre-build (the 3 greens are pre-existing invariants the suite pins).

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` · `add-method/tooling/test_engine_batch_ops.py` · `.add/tooling/add.py` · `add-method/src/add_method/_bundled/tooling/add.py` · `add-method/tooling/engine_pin.py` · `add-method/.add/tooling/engine_pin.py` · `add-method/tooling/SEAMS.md`
Strategy (ordered batches): 1. `_fill_section` helper in add.py (snapshot bytes · validate payload · replace §body via the _phase_spans grammar · _atomic_write) 2. wire `--fill` into cmd_advance behind a try/SystemExit-restore wrapper around the existing guard flow 3. `--brief` early-return at the top of cmd_status 4. parser flags 5. propagate to 2 twin trees + re-pin ENGINE_MD5 6. absorb byte-fence/SEAMS drift
Approach (domain strategy): flag-extension over new subcommand (from §1 Framings) — zero LIFECYCLE ripple; rollback via byte snapshot + except SystemExit re-raise, the only pattern that catches every _die exit path
Data strategy: TASK.md §bodies via taskdoc._phase_spans (the one canonical scan, per §3 Schema); no state.json change
Pattern: validate-before-write (§0 Honors) extended with snapshot-restore for the one write that must precede guards
Optimization stance: agent token cost (engine round-trips 21–27 → ≤8 per milestone); ⚠ least-trusted facet: the SystemExit-restore wrapper covering every guard exit path

Persona (required): methodology-engine-dev
Spawn isolation (default): no spawn — inline build (engine edit needs the session's accumulated fence/ripple knowledge)
Known-problem fixes: _die exits before restore → wrap guards in try/except SystemExit + finally-restore-on-failure · payload with fenced `---` corrupts scan → R3 reject up front · twin drift → byte-copy + md5 assert · SEAMS line pins drift on growth → re-pin in same change
Strategy actually used: as planned (snapshot→fill→guard→restore wrapper; --brief early-return; one SEAMS re-pin absorbed)
Safety rule (feature-specific): the fill write and the phase bump are one observable transaction — no path may leave a filled section WITH an unmoved phase after a refusal (all-or-nothing, human-chosen)
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass (test_engine_batch_ops 10/10 · targeted fences 48/48 · full tooling suite exit 0 backgrounded · benchmark suite unaffected)
- [x] coverage did not decrease (10 new behavior tests; none removed)
- [x] no test or contract was altered during build
- [x] the green was EARNED — rollback asserted by byte-compare on a REAL refused crossing (unfrozen §3), not a mock; reject codes asserted on stderr of real subprocess runs
- [x] concurrency / timing safe — fill+advance is a single-process sequence; _atomic_write both directions; no new shared state
- [x] no exposed secrets, injection openings, or unexpected dependencies (stdlib only; payload treated as text, never executed)
- [x] layering follows conventions — reuses taskdoc grammar, _atomic_write, _die; no new module
- [x] human-owned freeze chose the all-or-nothing semantics; diff summarized to Tin Dang in-session

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] one CLI call fills + bumps — confirmed by M1 round-trip test (real subprocess, real init'd project)
- [x] refused crossing restores byte-identical — confirmed by M2 before/after byte compare
- [x] `status --brief` ≤6 lines with slug·phase·next — confirmed by M3 test + plain-status-unchanged guard
- [x] 3 trees byte-identical (md5 201637d9b4e27b4f4921d72c04d13912, re-pinned); SEAMS scope-token-grammar anchor re-pinned 4798→4870; fences green

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING — _fill_and_advance called from cmd_advance; --fill/--brief wired in parser; confirmed by green behavior tests exercising both
- [x] DEAD-CODE — one new helper, one new branch, both exercised
- [x] SEMANTIC — SEAMS.md anchor comment updated & re-read; help strings read back via --help paths in tests

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] §3 anchors resolve: cmd_advance, _phase_spans (taskdoc), _atomic_write, cmd_status — all present at build SHA
- [x] moved anchors: _declared_scope def line 4798→4870 (named in SEAMS re-pin); none renamed

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: rollback probed against a REAL guard refusal (not simulated); payload-injection probes (## / --- smuggling) rejected fail-closed; recursion re-entry after --to fast-forward confirmed impossible (R1 rejects the combination)

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR — payload is inert text; no shell, no eval; paths confined to the task's TASK.md
2. Concurrency: CLEAR — single-process, atomic writes both directions
3. Architecture: CLEAR — grammar reused, no second parser; flag not subcommand (no LIFECYCLE ripple)
Verdict: PASS
Residue: none
Binding: advisory — method-engine change, human-reviewed at freeze

### GATE RECORD
Reported: yes — build summary + evidence rendered in-session before this record
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-07

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency — the §5 Optimization stance budget is a monitor here, not just an intention>

### Decisions (ADR)
- [AI] specify — chose extend advance with --fill; rejected a new `fill` subcommand (rejected: second round-trip defeats the purpose; new subcommand ripples into min_pillar LIFECYCLE + slang-guard spans) · agent-side batching only (rejected: leaves the engine chatty for every other agent)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang (2026-07-07, all-or-nothing variant chosen at freeze))
- [AI] build — approach: flag-extension over new subcommand (from §1 Framings) — zero LIFECYCLE ripple; rollback via byte snapshot + except SystemExit re-raise, the only pattern that catches every _die exit path
- [AI] build — data strategy: TASK.md §bodies via taskdoc._phase_spans (the one canonical scan, per §3 Schema); no state.json change
- [AI] build — pattern: validate-before-write (§0 Honors) extended with snapshot-restore for the one write that must precede guards
- [AI] build — optimization stance: agent token cost (engine round-trips 21–27 → ≤8 per milestone); ⚠ least-trusted facet: the SystemExit-restore wrapper covering every guard exit path
- [AI] build — strategy used: as planned (snapshot→fill→guard→restore wrapper; --brief early-return; one SEAMS re-pin absorbed)
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

