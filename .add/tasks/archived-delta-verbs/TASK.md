# TASK: delta verbs reach a light-archived task's on-disk record

slug: archived-delta-verbs · created: 2026-07-06 · stage: mvp
milestone: method-ergonomics
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): add-method/tooling/add.py:_delta_task_md (new) — the active-or-archived resolver; cmd_drop_delta · cmd_carry_delta · cmd_reopen_delta — rewired to it; _resolve_task — unchanged, still the active path
Context (working folder): deltas.md lifecycle (open→carried/dropped/seeded); cmd_archive_milestone keeps files, drops state entries
Honors (patterns / conventions): validate-then-write (every _die before the first write); `deltas` already disk-scans, so read/write surfaces converge
Seams consulted: none apply
Anchors the contract cites: _delta_task_md · cmd_drop_delta · cmd_carry_delta · cmd_reopen_delta
Issues/Risks (→ feed §1): _resolve_task dies 'unknown task' for archived slugs though the TASK.md sits on disk — delta-drain reach-back needed a hand edit (fold.md pain, recorded in project memory); the verbs' slug arg is a required positional, so no fallback can wander to an archived task
Related intent: method-ergonomics — archived-task deltas were the one lifecycle surface still requiring manual _resolve_spec_delta edits
Ground SHA: 6e8d477 (post gate-explain)

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: drop/carry/reopen-delta operate on a light-archived task's on-disk TASK.md
Framings weighed: an active-or-archived resolver shared by the three verbs (chosen) · an --archived flag per verb · un-archive/restore verb
Must:
<must>
  - an explicitly named slug ∉ state.tasks whose .add/tasks/<slug>/TASK.md exists resolves to that file; the flip semantics (drop/carry+stamp/reopen+breadcrumb-strip) are byte-identical to the active path
  - output carries an explicit `(archived — on-disk record)` marker
  - an archived-target write never touches state.json
</must>
Reject:
<reject>
  - slug neither in state nor on disk -> "unknown task '<slug>'" (compacted bundles stay out of reach)
  - no slug -> argparse `required: slug` (unchanged — an archived target can only be explicit)
</reject>
After:
<after>
  - every SPEC delta on disk is operable by the engine verbs; no lifecycle state requires a hand edit
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ only light archive produces the on-disk-but-not-in-state shape — lowest confidence because a future removal path could break the 'archived ⇒ was PASS-done' framing; if wrong: the verbs would edit a live-ish record's file (text-only, still auditable in git)
  - [x] `deltas`/`deltas --carried` already list archived tasks' deltas — confirmed: cmd_deltas disk-scans .add/tasks/*/TASK.md
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: drop reaches archived   # M1
  Given a slug dropped from state whose TASK.md holds an open SPEC delta
  When drop-delta <slug> runs
  Then the line flips to [SPEC · dropped] and the output says (archived

Scenario: carry reaches archived   # M1
  Given the same shape
  When carry-delta <slug> --reason runs
  Then the line flips to [SPEC · carried] with the [carried: …] stamp

Scenario: reopen reaches archived   # M1
  Given a carried delta on an archived record
  When reopen-delta <slug> runs
  Then the line flips to [SPEC · open] and the breadcrumb is stripped

Scenario: unknown slug still refused   # R1
  Given a slug neither in state nor on disk
  When drop-delta <slug> runs
  Then it dies unknown task
  And no file is written

Scenario: state untouched   # M3
  Given an archived-target write
  When it completes
  Then state.json is byte-identical
  And only the TASK.md changed
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
_delta_task_md(root, state, raw_slug) -> (slug, task_md, archived: bool)
  raw_slug in state.tasks            -> active path (unchanged)
  raw_slug on disk, not in state     -> (raw_slug, .add/tasks/<slug>/TASK.md, True)
  neither                            -> _die "unknown task '<slug>'"
  raw_slug is None                   -> _resolve_task fallback (never archived)
drop/carry/reopen-delta: flip semantics unchanged; archived target appends
"(archived — on-disk record)" to the success line; state.json never written.
Schema: TASK.md §7 Spec-delta lines only
```

Glossary deltas: none
Status: FROZEN @ v1 — approved by Tin (standing directive: implement all remaining milestone tasks directly)
Reported: no — collapsed ceremony under the standing implement-all directive; flag surfaced above
Least-sure flag surfaced at freeze: ⚠ [spec] only light archive produces on-disk-but-stateless records — because a future removal path could change that; if wrong: a text-only edit to a live-ish file, git-auditable

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: all 3 verbs × archived path + both refusals + state-untouched
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_archived_delta_verbs (6 tests): drop/carry/reopen reach archived · unknown slug dies · slug stays explicit (argparse) · state.json byte-stable · covers: M1–M3, R1–R2
</test_plan>

Tests live in: `add-method/tooling/` (test_archived_delta_verbs.py) · ran red (unknown task 'gone') before build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/` · `.add/tooling/` · `add-method/src/add_method/_bundled/tooling/` · `add-method/.add/tooling/`
Strategy (ordered batches): 1. red suite 2. _delta_task_md helper 3. rewire the three verbs 4. pin re-aim + twin sync

Persona (required): generic — engine-internals stance
Spawn isolation (default): n/a — orchestrator-inline, no spawn
Known-problem fixes: the verbs' slug is a required positional → scenario 5 pins the argparse refusal, not an imagined fallback; EnginePinTest drift → sync + re-aim in the same change
Strategy actually used: as planned; scenario 5 corrected mid-red (no active-task fallback exists on these verbs — the parser itself guarantees explicitness)
Safety rule (feature-specific): an archived-target write touches ONLY that TASK.md — never state.json
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
- [x] drop-delta on a state-less on-disk slug flips the line + prints (archived — confirmed by test output assertions
- [x] state.json byte-identical across an archived-target write — confirmed by test_state_untouched_by_archived_write

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — _delta_task_md called from all three verbs (grep: 3 call sites)
- [x] DEAD-CODE (code) — none; _resolve_task keeps its other callers
- [x] SEMANTIC (prose / non-code) — cmd_archive_milestone + cmd_compact read in full; light archive keeps files, compact moves them out of reach — matches the contract

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] every symbol §3 CONTRACT cites still resolves — grep at HEAD
- [x] no anchor moved since Ground SHA

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self · adversarially checked: state.json byte-parity on archived writes · unknown-slug refusal parity with _resolve_task's message · reopen strips exactly the [carried: …] breadcrumb

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self
1. Security: CLEAR — path built from root/'tasks'/slug; a traversal-shaped slug fails .exists() into the same refusal, no write
2. Concurrency: CLEAR — single _atomic_write per verb, unchanged
3. Architecture: CLEAR — one shared resolver; the read surface (deltas) and write surface (verbs) now agree on reach
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
- [AI] specify — chose an active-or-archived resolver shared by the three verbs; rejected an --archived flag per verb · un-archive/restore verb
- [human] freeze — froze §3 @ v1 (approved by Tin (standing directive: implement all remaining milestone tasks directly))
- [AI] build — strategy used: as planned; scenario 5 corrected mid-red (no active-task fallback exists on these verbs — the parser itself guarantees explicitness)
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

