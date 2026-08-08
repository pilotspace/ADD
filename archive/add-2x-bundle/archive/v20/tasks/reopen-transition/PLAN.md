# TASK: Engine reopen action + task lifecycle re-freeze

slug: reopen-transition · created: 2026-06-08 · stage: mvp · risk: high · autonomy: conservative
phase: done   <!-- specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- risk: high — adds an engine command (add.py reopen) AND re-freezes the 7-phase lifecycle
     contract (done becomes reopenable via a recorded action). Engine + trust-layer edit: the dial
     drops to conservative so a human owns the gate; the engine refuses an unguarded high-risk
     completion (`unguarded_high_risk_auto`, run.md guard). The slug-line fields ARE the declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: an engine action `add.py reopen <slug> --to <phase> --reason "<why>"` that returns an already-`done` task to a named earlier phase with a never-silent recorded reason and a reset gate. The flow already permits backward correction ("any phase may return to an earlier one" — book ch02); `done` is the one state the diagram draws terminal. reopen is the engine-enforced, recorded form of that backward edge OFF `done`: it sets the phase to <phase>, resets the gate to `none` (the task must re-earn its verdict), and records WHY — so a done task whose criterion a deepened verify (verify-deepen) later finds unmet can re-enter the flow without a silent marker-edit. The 7-phase lifecycle contract is re-frozen: `done` is terminal EXCEPT via this recorded action.
Framings weighed: dedicated `reopen` command + state-recorded reason + gate reset (chosen — matches the milestone's `add.py reopen <done-task> --to <phase>`; gives the already-frozen backward-correction edge an engine-enforced, never-silent form for the `done` state; leaves the generic `cmd_phase` marker-set as the documented override) · a `--reopen` flag on `cmd_phase` (rejected: overloads the bare escape-hatch with preconditions — done-only, mandatory reason, gate reset — that do not belong on a generic phase setter) · auto-reopen wired into the verify gate (rejected: scope — the milestone separates the reopen ACTION (this task) from the loop that DECIDES to fire it (`dynamic-task-loop`); reopen is the verb, the loop is the trigger)
Must:
<must>
  - `add.py reopen <slug> --to <phase> --reason "<text>"` moves a task whose phase is `done` to the named earlier phase (one of specify..observe) and resets its gate to `none`
  - the reopen is NEVER SILENT — the reason, the from-phase, a timestamp, and the voided verdict (prior_gate, and prior_waiver if one existed) are recorded as an append-only entry in state.json (`reopens: [{from, to, reason, at, prior_gate, prior_waiver?}]`), and the command prints a recorded confirmation
  - reopen keeps the verdict-state COHERENT — a task done via RISK-ACCEPTED carries a live `waiver`; reopen folds it into the reopens entry and DROPS the live `waiver` key, so no signed waiver lingers without a verdict (it is archived in history, never discarded silently)
  - reopen REFUSES a task that is not `done` -> "reopen_not_done" (backward correction inside a live run is the existing `phase`/HARD-STOP path, not reopen)
  - reopen REFUSES an empty or missing `--reason` -> "reopen_reason_required" (no silent un-done)
  - reopen REFUSES a `--to` target that is not one of the seven real phases specify..observe -> "reopen_target_invalid" (never `done`, never an unknown name)
  - the 7-phase lifecycle contract is RE-FROZEN to state `done` is terminal EXCEPT via the recorded `reopen` action; the re-freeze is human-approved at the §3 freeze (Rule 3) and the foundation's survivor-contract line (PROJECT.md) is updated to name the reopen back-edge
  - adding the `reopen` CLI verb is classified in `test_min_pillar`'s LIFECYCLE census (the pre-declared instrument reaction — CONVENTIONS: a contract adding a CLI verb pre-declares this); the FULL suite is run during TESTS to surface every other census/help guard pre-freeze
  - the engine change is mirrored across every `add.py` copy (canonical · bundle · dogfood) and `engine_pin.ENGINE_MD5` is re-aimed to the new digest (one literal, all importers re-anchor); `engine_pin.py` copies and all parity guards stay green
</must>
Reject:
<reject>
  - a task whose phase is not `done` -> "reopen_not_done"
  - an empty or missing `--reason` -> "reopen_reason_required"
  - a `--to` phase that is not one of specify..observe -> "reopen_target_invalid"
</reject>
After:
<after>
  - `add.py reopen <done-task> --to <phase> --reason "..."` moves the task to <phase>, resets gate to none, appends the reason to state.json's `reopens` log, and prints it; `_task_done` then reports the task not-done; the lifecycle contract (book ch02 + the PROJECT.md survivor line) names `done` as reopenable only via the recorded action; `add.py` is mirrored across trees, `engine_pin` re-aimed, the full suite green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [contract] the lifecycle "re-freeze vN" = this task's §3 FROZEN @ v1 + an INLINE update to PROJECT.md's survivor-contract line (the 7-phase flow now names a recorded reopen back-edge) — NOT a separate global lifecycle version stamp — lowest confidence because Rule 3 says "re-freeze vN, human-approved" and "vN" could mean a visible version bump; chosen inline because project-goal set the same-milestone precedent (it edited PROJECT.md inline when the edit WAS its deliverable, no deferred fold) and "the lifecycle contract is re-frozen" IS this task's exit criterion; if wrong: the foundation edit moves to the v20 fold, or a version token is added — cheap either way, but it is your altitude call
  ⚠ [spec] the existing silent `cmd_phase` escape hatch (`add.py phase <done-slug> build` already un-dones a task with no reason and a kept gate) is LEFT as the documented "deliberate, logged override" (cmd_gate already names it that); reopen is the never-silent path, not the SOLE done→earlier path — lowest confidence because an adversarial reviewer will ask "can I still un-done silently?" and find cmd_phase; chosen leave-it because cmd_phase is a generic marker-set relied on as an override and narrowing it is out of scope; if wrong: reopen becomes the only done→earlier path and cmd_phase refuses a done task (a new reject) — a clean later addition
  ⚠ [contract] "never silent" is satisfied by the FROZEN DATA SEAM (`reopens` append-only list in state.json) + stdout; a human-facing `status`/`report` marker is lean-DEFERRED presentation (freeze-data-not-presentation convention) — low confidence on whether you want the reopen visible in `status` in THIS task; if wrong: add a one-line marker later (presentation, no re-freeze)
  - [ ] reopen leaves MILESTONE status untouched — reopening a task in a done-but-unarchived milestone yields a done milestone with an open task; reactivating the milestone belongs to `dynamic-task-loop` (it owns "milestone-done holds while GOAL unmet"). High confidence; named so it is not an undefined gap (archived-milestone slugs are absent from state["tasks"], so `_resolve_task` already refuses them)
  - [ ] resetting gate to `none` (not preserving the prior PASS) is correct — a reopened task's prior verdict was wrong by definition; `report_data`/`cmd_audit` read it honestly (audit skips phase∉(done,observe) & gate==none; `_task_done` flips False). High confidence; verified against both readers
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: reopen returns a done task to an earlier phase
  Given a task at phase "done" with gate "PASS"
  When I run `add.py reopen <slug> --to build --reason "wiring check failed post-merge"`
  Then the task's phase is "build" and its gate is "none"
  And the PHASES tuple is unchanged (done stays a state, not removed)

Scenario: the reopen is recorded, never silent
  Given a done task being reopened with a reason
  When the reopen succeeds
  Then state.json gains an append-only reopens entry {from:"done", to:"build", reason:"…", at:<iso>}
  And the command prints a confirmation naming the from/to phases and that the reason was recorded

Scenario: two reopens append, never overwrite
  Given a task already reopened once (one reopens entry)
  When it is completed and reopened a second time
  Then the reopens list has two entries in order
  And the first entry is unchanged

Scenario: reopening a RISK-ACCEPTED task voids and records its waiver
  Given a task done via RISK-ACCEPTED with a live waiver {owner,ticket,expires}
  When I run `add.py reopen <slug> --to verify --reason "waiver criterion unmet"`
  Then the live `waiver` key is removed from the task record
  And the reopens entry carries prior_gate=="RISK-ACCEPTED" and prior_waiver=={the waiver}

Scenario: reject reopening a task that is not done
  Given a task at phase "build" (not done)
  When I run `add.py reopen <slug> --to specify --reason "x"`
  Then it exits non-zero with "reopen_not_done"
  And the task's phase and gate are unchanged

Scenario: reject an empty or missing reason
  Given a done task
  When I run `add.py reopen <slug> --to build --reason ""`
  Then it exits non-zero with "reopen_reason_required"
  And the task stays done with its gate unchanged

Scenario: reject an invalid --to target
  Given a done task
  When I run `add.py reopen <slug> --to done` (or an unknown phase name)
  Then it exits non-zero with "reopen_target_invalid"
  And the task stays done with its gate unchanged

Scenario: the lifecycle re-freeze is documented
  Given the shipped book ch02 and the foundation PROJECT.md
  When I read the flow description and the survivor-contract line
  Then both state that done is terminal EXCEPT via the recorded reopen action
  And no prior survivor-contract entry was removed (additive)

Scenario: the new verb is census-classified and the engine re-anchors
  Given the reopen subcommand added to the parser
  When the full tooling suite runs
  Then reopen is classified in test_min_pillar's LIFECYCLE census (no uncovered-command failure)
  And md5(every add.py copy) == engine_pin.ENGINE_MD5 (re-aimed, all importers green)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add.py reopen <slug?> --to <phase> --reason "<text>"      # slug omitted -> active task (like phase/gate)
  ok   -> stdout: task '<slug>' reopened: done -> <phase> (reason recorded); gate reset to none
          state: tasks[<slug>].phase = <phase>
                 tasks[<slug>].gate  = "none"
                 tasks[<slug>].reopens += { from:"done", to:<phase>, reason:<text>, at:<iso>,
                                            prior_gate:<the voided gate>,
                                            prior_waiver:<the voided waiver dict> }   # prior_waiver only if one existed; append-only
                 del tasks[<slug>].waiver        # a void verdict's signed waiver is void — folded into the reopens
                                                 # entry above (never discarded silently), removed as LIVE state
                 tasks[<slug>].updated = <iso>
  errs -> "reopen_not_done"         when tasks[<slug>].phase != "done"
          "reopen_reason_required"  when --reason is empty/whitespace (argparse permissive; validated in-body)
          "reopen_target_invalid"   when --to not in {specify,scenarios,contract,tests,build,verify,observe}
          (unknown slug reuses the existing `_resolve_task` death; archived slugs are absent from state)

Waiver coherence: a done task may have been done via RISK-ACCEPTED, which `cmd_gate` stamps with a
  live `waiver:{owner,ticket,expires}`. Resetting only the gate would leave a waiver with no verdict
  (cmd_check reads waiver ONLY under gate=="RISK-ACCEPTED", so it is latent, not active — but still
  incoherent). reopen folds the voided gate + waiver into the reopens history entry and DROPS the live
  `waiver` key, so the audit trail is preserved (never-silent) and no stale verdict-state lingers.

Lifecycle (RE-FROZEN @ this contract): the 7-phase flow already permits backward correction
  (book ch02: "any phase may return to an earlier one"). This adds the recorded edge OFF the
  terminal state: `done` is terminal EXCEPT via `add.py reopen`, which records why and resets the
  gate. The PHASES tuple is UNCHANGED (done stays a state; reopen is a transition, not a new phase).

Schema (state.json task record): + `reopens: list[{from,to,reason,at}]`  — append-only; absent until
  the first reopen; never overwritten. No other task field changes shape.

Engine parity (build obligations, not new external shape): add.py mirrored across every tree
  (canonical · _bundled · dogfood .add/tooling); `engine_pin.ENGINE_MD5` re-aimed to the new digest
  (one literal, 7 importers re-anchor); engine_pin.py copies kept identical; test_bundle_parity +
  test_tree_parity stay green.

Instrument reaction (PRE-DECLARED — CONVENTIONS: a contract adding a CLI verb names this class):
  test_min_pillar's LIFECYCLE census gains `["reopen", "--to", "<phase>", "--reason", "<text>"]`
  (a done task is set up in that test's fixture). The FULL suite is run during TESTS to surface any
  OTHER census/help guard that reacts to the new verb (v18 lesson: found pre-freeze -> contracted;
  found post-build -> residue). Surfacing-only book/foundation doc edits are additive.
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-08 (the lifecycle re-freeze, Rule 3: the 7-phase flow
gains a recorded reopen back-edge off `done`). All three flags resolved as recommended: (1) §3 v1 + INLINE
PROJECT.md survivor-line re-freeze (no separate version stamp); (2) the `cmd_phase` override is LEFT open
(reopen is the never-silent path, not the sole one); (3) never-silent = `reopens` data seam + stdout (no
status marker this task). The waiver-coherence rule was added pre-freeze (advisor-caught). Changing this
frozen contract = a change request back to SPECIFY.

<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: behavior-complete — one test per scenario (happy path + 3 rejects + history + re-freeze doc + census/parity); driven through `add.main([...])` against a temp project (arrange-through-CLI-contracts).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_reopen_moves_done_task_to_phase: arrange a done/PASS task / act `reopen --to build --reason x` / assert phase=="build" + PHASES tuple unchanged
  - test_reopen_resets_gate_to_none: arrange done/PASS / act reopen / assert gate=="none" AND _task_done flips False
  - test_reopen_records_reason_never_silent: act reopen / assert state.reopens[-1]=={from:"done",to:...,reason:...,at:...} AND stdout names from/to + "recorded"
  - test_reopen_appends_history: arrange one prior reopen (re-done, re-reopen) / assert two ordered entries, first unchanged (append-only)
  - test_reopen_voids_and_records_waiver: arrange a RISK-ACCEPTED done task with a waiver / act reopen / assert live `waiver` key gone AND reopens entry has prior_gate=="RISK-ACCEPTED" + prior_waiver=={waiver}
  - test_reopen_rejects_not_done: arrange a task at "build" / act reopen / assert SystemExit + "reopen_not_done" + phase/gate unchanged
  - test_reopen_rejects_empty_reason: arrange done / act `--reason ""` / assert "reopen_reason_required" + task stays done
  - test_reopen_rejects_invalid_target: arrange done / act `--to done` and `--to bogus` / assert "reopen_target_invalid" + task stays done
  - test_lifecycle_refreeze_documented: assert book ch02 (canonical) AND PROJECT.md survivor line both state done is terminal EXCEPT via the recorded reopen action; no prior survivor entry removed
  - test_reopen_in_lifecycle_census: assert "reopen" in build_parser() sub.choices AND in test_min_pillar's LIFECYCLE (no uncovered-command failure)
  - test_engine_repinned: assert md5(every add.py copy) == engine_pin.ENGINE_MD5 AND the copies are byte-identical (re-aim landed, parity holds)
</test_plan>

Tests live in: `add-method/tooling/test_reopen_transition.py` · MUST run red (no `reopen` command yet) before Build.
<!-- real path (matches project-goal / verify-deepen): dogfood suite ships beside the engine it guards;
     `_declared_tests_count` resolves the `/`-token from project root and counts the real file. -->
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 605 → 616 green (11 new test_reopen_transition tests, 0 regressions), exit 0
- [x] coverage did not decrease — every Must/Reject has a behavioral test driven through the real CLI
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched. Two build-time edits, both disclosed, neither a weakening: (a) the PRE-DECLARED test instrument-reaction — test_min_pillar LIFECYCLE census gains `reopen` (its own documented self-maintenance: "a new subcommand fails this until classified"), a coverage EXPANSION; (b) one reactive SOURCE edit — a `cmd_reopen` docstring word "folds"→"records" to satisfy the ubiquitous-language prose ban — prose-only, no behavior / assertion / contract touched
- [x] concurrency / timing — N/A: reopen is one atomic state read→mutate→`save_state` (`_atomic_write`), no shared mutable runtime state; same single-writer model as gate/advance/phase
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only; no new import in add.py; the reason/target are validated, never shell-interpolated
- [x] layering & dependencies follow CONVENTIONS.md — reopen reuses the existing seam helpers (`_resolve_task`/`_die`/`_now`/`_sync_task_marker`/`save_state`); engine stays judgment-free (it enforces the recorded transition, never classifies WHEN to reopen); all parity guards green
- [x] a person reviewed and approved the change — Tin Dang owned the conservative gate and resolved PASS (2026-06-08), affirming both disclosed build-time edits as non-weakenings

### Deep checks — do not skim (this task produced BOTH code and prose — both paths apply)
- [x] WIRING (code) — `cmd_reopen` is defined (add.py:599) and referenced (add.py:2541 `pr.set_defaults(func=cmd_reopen)`); the parser exposes `reopen` (test asserts it in `sub.choices`); every new symbol (`cmd_reopen`, the `reopens`/`prior_gate`/`prior_waiver` fields) is read by a passing test. No new dead/unused code (AST scan of the test file: 0 unused imports, 0 orphan helpers).
- [x] DEAD-CODE (code) — clean. The lean reject-validation path (no argparse `choices` on --to/--reason) means no unreachable branch; `_now()` computed once and reused; no leftover scaffolding.
- [x] SEMANTIC (prose — the lifecycle re-freeze) — read in full, not skimmed: book ch02 (canonical) now carries the "**`done` is terminal — except via the recorded reopen**" paragraph; all 4 book copies byte-identical (964e83b8…); PROJECT.md's survivor-contract line names the re-frozen v20 back-edge. Confirmed by reading each edit, not just the test pass — the wording matches the frozen §3 (done terminal except via the recorded action; gate reset; never a silent un-done).
- [x] SECURITY — no finding (else mandatory HARD-STOP). No secrets / injection / network / new dependency; the reopen mutation is confined to the resolved task's state record; add.py md5 == engine_pin (611fa233…, re-aimed; 7 importers + parity green).

### GATE RECORD
Outcome: PASS (conservative, human-gated — Tin Dang owned the gate; both build-time edits affirmed as non-weakenings: the test_min_pillar LIFECYCLE census expansion and the cmd_reopen docstring prose fix. The lifecycle re-freeze (done terminal except via recorded reopen) was human-approved at §3, Rule 3.)
If RISK-ACCEPTED -> N/A (clean PASS, no waiver; no security finding)
Reviewed by: Tin Dang · date: 2026-06-08

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): per-rejection counts of the three named codes (`reopen_not_done` / `reopen_reason_required` / `reopen_target_invalid`) — a spike in `reopen_not_done` means callers reach for reopen during a live run (wrong tool: that's `phase`/HARD-STOP). Every `reopens[]` entry must carry a non-empty `reason` and a `prior_gate`; a reopen of a RISK-ACCEPTED task must show `prior_waiver` archived and the live `waiver` key gone (no signed waiver lingering without a verdict).
Spec delta for the next loop: reopen is the ACTION (the verb); the decision of WHEN to fire it — a verify criterion later found unmet → reopen the done task — is `dynamic-task-loop`'s trigger. A reopened task lands inside a milestone that already earned `milestone-done`; `add.py check` correctly flags the reopened-task-in-a-done-milestone (surfacing, not a bug). dynamic-task-loop owns the milestone-reactivation handoff: re-open the milestone, fold the reopened task back into the work queue, and hold `milestone-done` while the GOAL is unmet.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] A CLI-verb contract must pre-declare **all three** instrument-reaction guard classes — (1) the subcommand census (`test_min_pillar` LIFECYCLE), (2) the `engine_pin` re-aim, AND (3) the ubiquitous-language **prose-ban** on add.py string literals. §3 here pre-declared only the first two; the prose-ban surfaced during the build's full-suite run (a `cmd_reopen` docstring word "folds" tripped `test_ubiquitous_language`), forcing a reactive source edit + a second pin re-aim. By the v18 rule (found pre-freeze → contracted; found post-build → residue) that third class was residue. Evidence: the build's full-suite run went 0d72a2dd→611fa233 (two pin re-aims, not one). Fix: the next verb-adding contract enumerates all three guard classes in its Instrument-reaction note up front. (CONVENTIONS.md:286-298.)
- [ADD · folded] `dynamic-task-loop` inherits the milestone-reactivation handoff from this task — reopen deliberately scoped out the TRIGGER (the human left the generic `cmd_phase` marker-set hatch open as the documented override). The loop owns: reading the deepened-verify "criterion unmet" signal, firing `reopen`, re-activating the now-`done` milestone, and re-queuing the task. Evidence: §1 framings rejected "auto-reopen wired into the verify gate" as out-of-scope (verb vs trigger separation).
- [ADD · folded] The §6 **Deep checks** block now travels — verify-deepen's observe flagged that downstream v20 tasks lacked it; reopen-transition adopted it (WIRING / DEAD-CODE / SEMANTIC / SECURITY all recorded). `dynamic-task-loop`'s TASK.md must carry the same block. Evidence: the block on this task proved the rubric portable (it re-confirmed wiring + no dead code; nothing new found, but the discipline is now standard).
- [SDD · folded] §3 over-anticipated the mirror topology — it said "engine_pin.py copies kept identical", but there is ONE canonical `engine_pin.py` (a single `ENGINE_MD5` literal, 7 importers re-anchor). Trivially satisfied, not violated. A contract should name the real mirror counts: add.py ×3 (canonical · `_bundled` · dogfood), book ×4, but engine_pin ×1 and test_min_pillar ×1. Evidence: parity verified one pin, not copies.
