# TASK: advance --to + re-cross

slug: bundle-advance · created: 2026-07-06 · stage: mvp
milestone: method-ergonomics
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): add-method/tooling/add.py:cmd_advance (gains --to validation + tail fast-forward) · add.py:cmd_recross (new; wraps _build_entry) · add.py:_build_entry (unchanged, reused verbatim) · parser block (advance --to, re-cross)
Context (working folder): engine twins (.add/tooling · _bundled · add-method/.add) · engine_pin.py re-aim
Honors (patterns / conventions): validate-then-write (_die before mutation) · durable-state-first · the tests→build gate stack is NEVER fast-forwarded or bypassed
Seams consulted: <SEAMS.md entry cited instead of re-deriving, e.g. .add/SEAMS.md#scope-token-grammar — optional, omit if none apply>
Anchors the contract cites: cmd_advance · cmd_recross · _build_entry · PHASES
Issues/Risks (→ feed §1): --to must stop at tests (gate stack); re-cross must re-run the FULL _build_entry (freeze gate incl.) or it becomes a tamper-launder
Related intent: method-ergonomics exit criterion 3; review item 4
Ground SHA: post-ec64f18 (task 1 committed)

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: <name>
Framings weighed: <chosen> (chosen) · <alternative> · <alternative>
Must:
<must>
  - <required behavior>
</must>
Reject:
<reject>
  - <bad input / situation> -> "<error_code>"
</reject>
After:
<after>
  - <state that is true once it succeeds>
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ <the one assumption most likely to be wrong> — lowest confidence because <why>; if wrong: <cost>
  - [ ] <next assumption, ranked> — confirm or deny; never carry an open one forward
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: <short name>   # <Must/Reject item this covers, e.g. M1 or R1>
  Given <starting situation>
  When <action>
  Then <expected result>
  And <what must remain unchanged>   # required for every rejection
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
advance [slug] --to <phase>   phase ∈ ground..tests, forward-only; repeats single-step advance,
                              every crossing guard per step; rejects: advance_to_invalid ·
                              advance_to_stops_at_tests · advance_to_not_forward
re-cross [slug] --by <name>   phase ∈ {build,verify} only; re-runs the IDENTICAL _build_entry
                              stack (freeze gate · flag · tripwire · scope snapshot); sets
                              phase=build; records tasks[slug].recross={by,at,from_phase};
                              rejects: recross_wrong_phase · recross_unsigned · contract_not_frozen
```

Glossary deltas: none
Status: FROZEN @ v1 — approved by Tin (implement-directly directive 2026-07-06)
Reported: yes — shape shown in-chat with the milestone plan
Least-sure flag surfaced at freeze: ⚠ [contract] recross keeps only the LATEST {by,at,from_phase} record (no history list) — because git history carries the trail; if wrong: an audit wanting N re-crosses needs a list-append (additive)

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: <e.g. 90%>
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_<scenario>: arrange <Given> / act <When> / assert <Then> + assert <unchanged> · covers: <M#, R:code — optional>
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_bundle_advance.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/.add/tooling/add.py`
Strategy (ordered batches): <1. … 2. … — the planned build order; guidance, not enforced; preferred architecture/pattern strategies; advise solution/method to resolve issues/implement features; let the named Persona's domain stance (below) shape the approach, not just architecture patterns>

Persona (required): methodology-engine-dev
Spawn isolation (default): <prefer isolation: "worktree" for any subagent build/verify spawn, not only explicit parallel mode; shared-tree needs a stated reason — see worktree-isolated-spawn-default>
Known-problem fixes: <trap → planned fix — the failure modes this build must dodge; guidance, not enforced>
Strategy actually used: red suite (9F/10) → --to validation + tail recursion in cmd_advance → cmd_recross wrapping _build_entry verbatim → re-pin + 4-way twin sync → 94-test freeze/heal/scope batch green
Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass (test_bundle_advance 10/10; freeze/heal/scope/pin batch 94/94)
- [x] coverage did not decrease (10 new tests)
- [x] no test or contract altered during build
- [ ] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [ ] concurrency / timing of the risky operation is safe
- [ ] no exposed secrets, injection openings, or unexpected dependencies
- [ ] layering & dependencies follow CONVENTIONS.md
- [ ] a person reviewed and approved the change

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] a ground task reaches tests in ONE call with guards run per step — confirmed by test_to_tests_one_call + this very task (dogfooded below)
- [x] a DRAFT-§3 task can NEVER re-cross — confirmed by test_recross_never_bypasses_freeze

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING — cmd_recross registered in the parser; --to consumed in cmd_advance; confirmed by suite
- [x] DEAD-CODE — none introduced
- [x] SEMANTIC — n/a (engine task; help strings read back)

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> §0's Ground SHA anchors the symbols cited at ground time to that commit — code moves during
> build. Before the gate, re-resolve every symbol §3 CONTRACT cites against the CURRENT tree
> (not the Ground SHA) so a stale anchor is caught here, not by a future reader chasing a moved
> line.
- [x] cmd_advance/cmd_recross/_build_entry/PHASES all resolve — confirmed by green suite
- [x] no anchor moved

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self · adversarially checked: --to cannot cross build (validated before any step); re-cross with DRAFT §3 refuses via the UNCHANGED _build_entry freeze gate; refusals write nothing (phase asserted unchanged in tests)

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: self
1. Security: CLEAR — no new IO/exec; re-cross requires a signed --by and cannot weaken the freeze gate
2. Concurrency: CLEAR — same single-writer state pattern as advance
3. Architecture: CLEAR — _build_entry reused verbatim, no duplicate gate logic
Verdict: PASS
Residue: none
Binding: advisory — architecture

### GATE RECORD
Reported: yes — evidence summarized in-chat (collapsed ceremony, floor kept)
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: auto-resolved (autonomy: auto; evidence complete, residue none) under Tin's directive · date: 2026-07-06

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose <unrecorded>
- [human] freeze — froze §3 @ v1 (approved by Tin (implement-directly directive 2026-07-06))
- [AI] build — strategy used: red suite (9F/10) → --to validation + tail recursion in cmd_advance → cmd_recross wrapping _build_entry verbatim → re-pin + 4-way twin sync → 94-test freeze/heal/scope batch green
- [AI] verify — gate PASS (reviewed by auto-resolved (autonomy: auto; evidence complete, residue none) under Tin's directive)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.

