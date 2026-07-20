# TASK: engine seam: hold new-task until the parent MILESTONE.md is confirmed

slug: confirm-parent · created: 2026-06-23 · stage: mvp · risk: high
autonomy: conservative   <!-- LOWERED from project default (auto): engine BEHAVIOR change (new-task gate). risk:high → the v14 guard refuses an unguarded auto completion; verify STOPS at the human gate. -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): the new-task seam in the engine ×3 trees (VERIFIED via `test_engine_repin_parity.py` L40-42: canonical `add-method/tooling/add.py`; mirrors `.add/tooling/add.py` + `add-method/src/add_method/_bundled/tooling/add.py` — all md5-identical):
  · `add.py:cmd_new_task` (L748) — links a task to a milestone at L762-765: `milestone = args.milestone or _active_milestone(state)`; validates ONLY existence (`milestone not in state["milestones"] -> _die("unknown_milestone")`). This is the insertion point: ALSO require the parent milestone be CONFIRMED before scaffolding the task. The unattached case (no milestone) is warn-never-block (L831-835).
  · `add.py:cmd_new_milestone` (L2564) — seeds `state["milestones"][slug] = { title, goal, stage, status:"active", created, updated }` (L2580-2583). NO `confirmed` field today; sets active immediately.
  · PRECEDENT — the SETUP-LOCK gate: `_setup_locked(state)` + `add.py lock`; `cmd_new_task` L752-753 already refuses a 2nd pre-lock task (`setup_unlocked: lock the foundation first`). confirm-parent is the SAME shape one level down: a per-milestone confirm before its tasks.
Context (working folder): the PROCESS LESSON that spawned this task (lean-pass M1 retro) — `new-milestone → new-task` has no confirmation seam; the AI dug into task §0–§5 before the human confirmed the parent MILESTONE.md. Goal: hold `new-task` until the parent is confirmed.
Honors (patterns / conventions): 3-tree engine parity (canonical add.py → 2 mirrors; a parity test asserts md5-identical); validate-then-write (refuse before any state mutation, like the existing `unknown_milestone`/`setup_unlocked` _die chain); fail-SAFE grandfathering (existing milestones carry no `confirmed` field — absent must not break the active flow); reject-code vocabulary (snake_case `_die` tokens); the human owns the confirm act (engine records, never self-confirms — like `lock`).
Anchors the contract cites: `cmd_new_task` parent-validation block (L762-765) · the milestone state record shape (add `confirmed`?) · a new confirm command (mirrors `add.py lock`) · the reject code for an unconfirmed parent · the grandfather rule (absent `confirmed` ⇒ treated how) · 3-tree engine parity.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Hold `new-task` until the parent milestone is human-confirmed — an OPT-IN per-milestone confirm gate that mirrors the setup-lock (`init --await-lock` / `add.py lock`) one level down. `new-milestone --await-confirm` seeds the milestone unconfirmed; the guided skill flow passes the flag so the gate fires exactly where the human reviews the MILESTONE.md.
Framings weighed: (OPT-IN via `--await-confirm`, mirroring `_setup_locked`) CHOSEN by Tin Dang at the v1→v2 change-request — `new-milestone --await-confirm` seeds `confirmed:false`; WITHOUT the flag no `confirmed` key is written (grandfathered-confirmed); `new-task` HARD-BLOCKS on an unconfirmed parent; `add.py milestone-confirm` is the human gate. Fires in the guided/skill flow (which passes the flag); raw CLI + the 342 existing engine tests are untouched. · (DEFAULT-ON — every new milestone gated, v1 frozen) REJECTED at v2 — its true cost was 342 broken test methods across 61 files (mixed call-shapes, not cleanly scriptable), ~7× the freeze estimate; a large risky migration for no gain over opt-in (the process lesson is about the GUIDED draft-then-confirm flow, where the skill passes the flag). · (soft-warn) REJECTED earlier — no teeth.
Must:
<must>
  - A milestone is "confirmed" when its state record has `confirmed is True` OR the `confirmed` key is ABSENT (grandfather-by-missing-key for PRE-EXISTING milestones, mirroring `_setup_locked`). Only `confirmed is False` is unconfirmed. A pure helper `_milestone_confirmed(state, mslug)` decides it.
  - `new-milestone --await-confirm` seeds `confirmed:false` (+ `confirmed_at:null`, `confirmed_by:null`). WITHOUT the flag, NO `confirmed` key is written → grandfathered-confirmed → never gates. Existing call sites + the 342 engine tests are byte-unchanged in behavior (they pass no flag).
  - `cmd_new_task` HARD-BLOCKS (validate-then-write, before any scaffold/state write): if the resolved parent milestone exists AND `not _milestone_confirmed(...)` → `_die("milestone_unconfirmed: confirm it first — add.py milestone-confirm <slug>")`. The unattached (no-milestone) case stays warn-never-block (unchanged).
  - New `add.py milestone-confirm <slug>` (human-run, mirrors `cmd_lock`): validate-then-write — unknown milestone → `_die("unknown_milestone")`; sets `confirmed:true`, `confirmed_at`, `confirmed_by` (the actor); re-confirm is idempotent (a note, not an error). The engine RECORDS; never self-confirms.
  - 3-tree engine parity (canonical `add-method/tooling/add.py` → 2 mirrors, md5-identical); a red-first `test_confirm_parent.py`; full suite + `add.py check` green; NO existing test touched or weakened (grandfather makes that automatic).
  - Skill guidance (SKILL.md intake + scope.md) updated: the guided milestone flow creates the milestone with `--await-confirm`, SHOWS the filled MILESTONE.md, then `milestone-confirm` AFTER the human confirms — closing the process gap. The skill is what opts into the gate.
Reject:
<reject>
  - new-task on an --await-confirm (unconfirmed) parent is allowed to scaffold -> "gate_bypassed" (the block didn't fire)
  - the block fires for a milestone created WITHOUT --await-confirm (no `confirmed` key) -> "grandfather_broken" (existing flows regressed)
  - milestone-confirm writes a confirm the human did not run (auto/self-confirm) -> "self_confirm"
  - the 3 engine trees diverge -> "parity_break"
  - an existing test weakened/deleted to make the gate pass -> "test_weakened"
</reject>
After:
<after>
  - `--await-confirm` milestones gate new-task until `milestone-confirm`; non-flag + pre-existing milestones behave exactly as before (no key, no block); the human owns the confirm; the 342 existing tests stay green UNTOUCHED; 3 trees identical; suite + check green; the guided flow shows-then-confirms.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [contract] The gate is OPT-IN via `--await-confirm` (not default-on) — lowest confidence because a strict reading of "a task can't be detailed before confirmed" could want EVERY new milestone gated. Chosen at the v2 change-request because default-on's true cost was 342 broken test methods (61 files, mixed call-shapes) for no real gain — the process lesson is about the GUIDED flow, where the skill passes `--await-confirm`. It mirrors the proven `--await-lock` precedent exactly. If wrong: flip to default-on (the v1 path) + migrate the 342 tests. Surfaced as the freeze flag.
  - [x] grandfather is byte-safe — VERIFIED at v1 build: with default-on the gate fired 342×, all `milestone_unconfirmed` (the gate works); opt-in writes NO key without the flag, so those 342 grandfather → green untouched.
  - [x] `confirmed_by` reuses `cmd_lock`'s actor source — VERIFIED: `who = args.by or getpass.getuser()` (free-text) + `_actor_stamp(state)` (structured). milestone-confirm mirrors this, not reinvents.
  - [x] mirror set VERIFIED = 3 trees (canonical `add-method/tooling/add.py` + `.add/tooling/add.py` + `add-method/src/add_method/_bundled/tooling/add.py`) per `test_engine_repin_parity.py` L40-42 — edit canonical, propagate ×2.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: --await-confirm milestone blocks new-task until confirmed
  Given a milestone created with `new-milestone --await-confirm` (confirmed:false)
  When `new-task <slug>` targets it (active or via --milestone)
  Then it dies "milestone_unconfirmed: confirm it first — add.py milestone-confirm <slug>"
  And no TASK.md, tests/, src/, or state entry is written for the new task

Scenario: milestone-confirm opens the gate
  Given an --await-confirm (unconfirmed) milestone
  When the human runs `add.py milestone-confirm <slug>`
  Then the record gets confirmed:true + confirmed_at + confirmed_by (the actor)
  And a subsequent `new-task` on it succeeds

Scenario: plain new-milestone is grandfathered (no flag, no gate)
  Given a milestone created with plain `new-milestone` (no --await-confirm)
  When `new-task <slug>` targets it
  Then the milestone record has NO `confirmed` key
  And the task scaffolds normally (no block)

Scenario: unattached task stays warn-never-block
  Given no active milestone and no --milestone
  When `new-task <slug>` runs
  Then it succeeds with the existing "not attached … size it via /add" note
  And the confirm gate does not fire

Scenario: reject self_confirm
  Given an --await-confirm (unconfirmed) milestone
  When any command other than `add.py milestone-confirm` runs
  Then no confirmed:true is written by any auto path
  And only the human-run milestone-confirm sets it -> else "self_confirm"

Scenario: reject parity_break
  Given the canonical add.py is edited
  When propagated to the 2 mirrors
  Then all three add.py are md5-identical
  And divergence fails -> "parity_break"

Scenario: reject test_weakened
  Given the 342 existing new-milestone→new-task tests
  When the opt-in gate ships
  Then they stay green UNTOUCHED (grandfathered — they pass no --await-confirm)
  And weakening/deleting any to pass fails -> "test_weakened"
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
NEW-MILESTONE <slug> [--await-confirm]   (default: NO confirmed key written)
  200 -> { }                                         # no key → grandfathered-confirmed (no gate)
  200 (--await-confirm) -> { confirmed: false, confirmed_at: null, confirmed_by: null }

NEW-TASK <slug> --milestone <m>   body: { parent: <m>, confirmed: bool|absent }
  200 -> { scaffolded: true }                        # parent confirmed OR no key (grandfathered)
  4xx -> { error: "milestone_unconfirmed" }          # parent.confirmed is False

MILESTONE-CONFIRM <slug>   (human-run; mirrors `add.py lock`)
  200 -> { confirmed: true, confirmed_at, confirmed_by, actor }
  4xx -> { error: "unknown_milestone" }
  re-confirm -> idempotent note (not an error)

Schema (state.json milestones.<slug>):
  ADD field `confirmed: bool` — written false ONLY by `new-milestone --await-confirm`
    (+ confirmed_at:null, confirmed_by:null). WITHOUT the flag, NO key is written.
    ABSENT key ⇒ grandfathered-confirmed (non-flag + all pre-existing milestones).
  ON confirm: confirmed:true, confirmed_at:<iso>, confirmed_by:<who>, actor:<_actor_stamp>.
Engine (canonical add-method/tooling/add.py → +2 mirrors, md5-identical):
  NEW  _milestone_confirmed(state, mslug) -> bool   # True if confirmed is True OR key absent;
       False only if confirmed is False. PURE. Mirrors `_setup_locked` exactly.
  EDIT cmd_new_milestone — add `--await-confirm` flag: when set, seed confirmed:false (+ nulls);
       when UNSET, write NO confirmed key (grandfather). Plain-create output byte-unchanged.
  EDIT cmd_new_task — after the existence check (L764-765), before any write:
       `if milestone and not _milestone_confirmed(state, milestone): _die("milestone_unconfirmed: …")`.
  NEW  cmd_milestone_confirm + subparser `milestone-confirm <slug> [--by]` — validate-then-write,
       sets confirmed:true/at/by/actor; unknown→_die("unknown_milestone"); re-confirm idempotent.
  SKILL  SKILL.md (Intake) + scope.md — guided flow: `new-milestone --await-confirm` → show the
       filled MILESTONE.md → `milestone-confirm` AFTER the human confirms → then new-task. (×3 skill trees.)
  TESTS  NEW test_confirm_parent.py (red-first). The 342 existing tests are UNTOUCHED (grandfathered).
  Measurement: full suite + `add.py check` green; 3 engine trees + 3 skill trees parity.
```

Status: FROZEN @ v2 — approved by Tin Dang (change-request from v1: OPT-IN via `--await-confirm`, mirroring `--await-lock`; non-flag + pre-existing milestones grandfathered; 342 existing tests untouched). risk:high · autonomy:conservative → verify STOPS at the human gate.

Least-sure flag surfaced at freeze: [contract] the gate is OPT-IN (not default-on) — why it could be wrong: a strict reading of "a task can't be detailed before confirmed" could want EVERY new milestone gated. Chosen at v2 because default-on's TRUE cost (measured at the v1 build) was 342 broken test methods across 61 files (mixed call-shapes, not cleanly scriptable) — ~7× the v1 freeze estimate — for no gain over opt-in (the process lesson is about the GUIDED flow, where the skill passes `--await-confirm`). Mirrors the proven `--await-lock`. Cost if wrong: flip to default-on (the v1 path) + migrate the 342 tests. Human chose opt-in at the v1→v2 change-request.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + every Reject has a fence (behavior, not internals)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_await_confirm_seeds_unconfirmed: `new-milestone --await-confirm` → assert state milestone confirmed:false (+ confirmed_at:null, confirmed_by:null)
  - test_plain_new_milestone_writes_no_key: plain `new-milestone` (no flag) → assert NO "confirmed" key in the milestone record (grandfathered-confirmed)
  - test_await_confirm_blocks_new_task: `new-milestone --await-confirm` → new-task → assert SystemExit/_die "milestone_unconfirmed"; assert NO tasks/<slug>/TASK.md and no state["tasks"][slug] written
  - test_milestone_confirm_opens_gate: --await-confirm milestone → milestone-confirm → assert confirmed:true + confirmed_at + confirmed_by set; then new-task → assert it scaffolds
  - test_plain_milestone_never_gates: plain `new-milestone` (no flag) → new-task → assert scaffolds (no block); assert still no "confirmed" key added
  - test_grandfather_injected_key_absent: a milestone record with the key stripped (pre-existing, injected into state) → new-task → assert scaffolds; assert no key re-added
  - test_unattached_task_warn_never_block: no milestone → new-task → assert succeeds + the existing "not attached" note; gate does not fire
  - test_no_self_confirm: an --await-confirm milestone → run an unrelated command (status) → assert confirmed stays False (only cmd_milestone_confirm writes true)
  - test_unknown_milestone_confirm: milestone-confirm <absent> → assert _die "unknown_milestone"
  - test_reconfirm_idempotent: confirm an already-confirmed milestone → assert note, exit 0, confirmed stays true
  - parity carried by test_engine_repin_parity (3 add.py md5-identical) + test_bundle_parity + the skill-tree parity tests
  - the 342 existing new-milestone→new-task tests are UNTOUCHED (they pass no --await-confirm → no key → grandfathered green); weakening any → test_weakened
</test_plan>

Tests live in: `add-method/tooling/test_confirm_parent.py` (new) · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/test_confirm_parent.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_min_pillar.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/skill/add/SKILL.md` `add-method/skill/add/scope.md` `.claude/skills/add/SKILL.md` `.claude/skills/add/scope.md` `add-method/src/add_method/_bundled/skill/add/SKILL.md` `add-method/src/add_method/_bundled/skill/add/scope.md`
<!-- OPT-IN keeps the blast radius tiny: only the canonical engine + its new test + the 2 add.py mirrors + the 6 skill files, plus the TWO sanctioned sibling ratifications any engine+subcommand change requires: engine_pin.py (re-aim the single-source ENGINE_MD5) + test_min_pillar.py (LIFECYCLE += `milestone-confirm` census). The ~342 existing test_*.py are NOT touched (grandfathered). -->
Strategy (ordered batches): 1. canonical engine `add-method/tooling/add.py`: add `_milestone_confirmed` (mirror `_setup_locked`) · cmd_new_milestone seeds confirmed:false ONLY under `--await-confirm` (no key otherwise; plain-create output byte-unchanged) · the cmd_new_task block · cmd_milestone_confirm + `--await-confirm`/`milestone-confirm` subparsers 2. propagate add.py ×2 (cp) 3. write test_confirm_parent.py → run RED 4. run FULL suite → expect GREEN (the 342 existing tests grandfather: no flag → no key → no gate) 5. skill guidance SKILL.md + scope.md (canonical) → propagate ×2 6. full suite + check green.
Safety rule (feature-specific): the cmd_new_task block is VALIDATE-THEN-WRITE — it must `_die` BEFORE any mkdir/_atomic_write/state mutation (no partial scaffold on a blocked task). Grandfather is by MISSING KEY (never write `confirmed` unless `--await-confirm`) so the 342 existing tests stay byte-green with ZERO churn.
Code lives in: canonical `add-method/tooling/add.py` + `add-method/skill/add/` → propagated to mirrors
Constraints: do NOT change any existing test or weaken one; the gate is risk:high → verify STOPS at the human gate (autonomy:conservative); allow-list paths only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 1570/0 (`python3 -m unittest discover`), incl. red→green test_confirm_parent.py [10]
- [x] coverage did not decrease — +10 new tests; the 342 existing new-milestone→new-task tests untouched & green
- [x] no test or contract was altered during build — §3 FROZEN @ v2 unchanged; only NEW test_confirm_parent.py + the sanctioned census add (test_min_pillar LIFECYCLE += milestone-confirm) + engine_pin re-aim
- [x] the green was EARNED, not gamed — adversarial refute-read run (below); it CAUGHT one stale "(default-on)" inline comment → corrected to "(OPT-IN)" (comment-only). Grandfather green is real: the 342 pass because no flag → no key → _milestone_confirmed True, not because a test was loosened
- [x] concurrency / timing of the risky operation is safe — no new IO/threading; the gate is a pure in-memory `_milestone_confirmed` read before the existing single-writer save_state path; validate-then-write means a blocked new-task writes NOTHING
- [x] no exposed secrets, injection openings, or unexpected dependencies — no new imports; reuses getpass/_actor_stamp already present
- [x] layering & dependencies follow CONVENTIONS.md — mirrors `_setup_locked`/`cmd_lock` exactly, one level down; 3-tree engine parity + 3-tree skill parity held (md5-identical)
- [ ] a person reviewed and approved the change — **PENDING: risk:high + autonomy:conservative → this gate STOPS for the human (you)**

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `new-milestone --await-confirm` seeds `confirmed:false` (+ nulls); plain `new-milestone` writes NO `confirmed` key — confirmed by the state.json records in test_await_confirm_seeds_unconfirmed + test_plain_new_milestone_writes_no_key, and the plain-create stdout is byte-unchanged from pre-task
- [x] `new-task` on an `--await-confirm` parent dies `milestone_unconfirmed` with NO partial scaffold (no TASK.md, no tests/src dirs, no state entry) — confirmed by test_await_confirm_blocks_new_task + the `_die` sitting at add.py:783-784, BEFORE the mkdir(812)/_atomic_write_many(827)/state-write(833)
- [x] `milestone-confirm <slug>` opens the gate (confirmed:true/at/by/actor) and only then does `new-task` scaffold — confirmed by test_milestone_confirm_opens_gate; no other command flips it (test_no_self_confirm)
- [x] the guided skill flow now routes create→show→confirm→detail — confirmed by the SKILL.md Intake + scope.md "Confirm the milestone before detailing tasks" edits (×3 skill trees, md5-identical)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_milestone_confirmed` is referenced at cmd_new_task:783; `--await-confirm` flows args.await_confirm→cmd_new_milestone:2602; `cmd_milestone_confirm` reached via the `milestone-confirm` subparser; all exercised by the census LIFECYCLE walk (test_min_pillar) + test_confirm_parent
- [x] DEAD-CODE (code) — no orphaned symbol; the v1 `--confirmed` path was fully removed (renamed to `--await-confirm`), no stragglers (grep clean)
- [x] SEMANTIC (prose / non-code) — read the SKILL.md + scope.md edits in full: the guided flow reads correctly, the gate is described as opt-in, byte-budgets held (core 14849≤14866 · reference 40405≤40406 · tree 123198≤123249) by reclaiming genuine redundancy (no rule lost)

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
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
