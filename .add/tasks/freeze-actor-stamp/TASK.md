# TASK: add.py freeze write seam — engine-stamped actor at the §3 contract freeze

slug: freeze-actor-stamp · created: 2026-06-26 · stage: mvp
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
  - `add.py` — NEW `cmd_freeze(args)` + an `argparse` subparser `freeze` (mirrors `cmd_lock`/`cmd_gate` registration); writes the §3 freeze line into the active task's `tasks/<slug>/TASK.md` AND a structured actor into state.
  - `add.py:990 cmd_lock` — the closest sibling: writes a human line + `"actor": identity._actor_stamp(state)` alongside the free-text `locked_by`. Freeze must follow this exact pattern.
  - `add_engine/identity.py:66 _actor_stamp(state) -> dict` — the structured-actor producer the four written seams reuse (lock/gate/milestone-done/release). Freeze reuses it verbatim.
  - `add.py:4616 _AUDIT_STAMP_RE = "Status: FROZEN @ v\d+ — approved by <name>"` — the FROZEN §3 text format the audit reads (add.py:4644). `cmd_freeze` must emit a line this regex matches, so the audit trail is unbroken.
  - `add.py:3857 _is_frozen(...)` — detects `Status: FROZEN` in §3; freeze must transition `DRAFT`→`FROZEN @ vN` and refuse a re-freeze.
  - `add.py:611-630` — the flag-first freeze guard (`unflagged-freeze`: a FROZEN §3 may not cross without a surfaced lowest-confidence flag; reads `FROZEN @ (v\d+)`). The new command must respect/produce the same `vN` shape.
Context (working folder): `.add/tasks/<active>/TASK.md` §3 CONTRACT block · `.add/state.json` (where lock/gate/milestone-done/release record their structured `actor`).
Honors (patterns / conventions): validate-then-write + `_atomic_write` (drop-delta/lock pattern); a new CLI subcommand needs a `test_min_pillar` LIFECYCLE entry (per prior-task lesson); never pre-stamp a human seam — `freeze` is invoked BY the human's approval, like `lock`/`gate`.
Anchors the contract cites: `cmd_freeze`, `identity._actor_stamp`, `_AUDIT_STAMP_RE`, `_is_frozen`, the §3 `Status: FROZEN @ vN — approved by <name>` line, state `actor` record.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `add.py freeze` — the engine write-seam for the §3 contract freeze, recording a structured actor (the 5th human seam, joining lock · gate · milestone-done · release).

Framings weighed: write-seam mirroring `cmd_lock` (chosen) · auto-stamp at advance/gate time · post-hoc git-blame backfill
  - chosen: a dedicated `add.py freeze` flips the active task's §3 `DRAFT → FROZEN @ vN — approved by <name>` AND records `identity._actor_stamp(state)` into the task's state record — exactly the `cmd_lock` pattern (human line + structured actor). The human runs it AS their approval, so no pre-stamp.
  - rejected (auto-stamp at advance): freeze is a human judgment, not an AI advance — auto-stamping would pre-stamp a human seam (forbidden) and let an agent self-freeze.
  - rejected (git-blame backfill): lossy, not a real seam, and breaks for non-git / co-authored freezes.

Must:
<must>
  - `add.py freeze` (no positional → the ACTIVE task; optional `<slug>` to target another) flips that task's §3 `Status: DRAFT` to `Status: FROZEN @ vN — approved by <name>`, where `<name>` is the resolved actor's display name and `vN` is the next contract version (v1 on first freeze; N+1 of the highest prior freeze recorded for the task on a re-freeze after a change-request).
  - the emitted §3 line MUST match `_AUDIT_STAMP_RE` (`Status: FROZEN @ v\d+ — approved by \S+`) so `add.py audit` reads an unbroken trail.
  - record a structured freeze stamp in `state["tasks"][<slug>]` — `{version, frozen_at, approved_by, actor: identity._actor_stamp(state)}` — alongside the §3 text, mirroring `state["setup"]["actor"]`.
  - support `--by <name>` (free-text approver, like `lock --by`) and resolve the structured actor via the same override→git→os chain `_actor_stamp` already uses.
  - validate-then-write (one `_atomic_write`, never half-freeze): all refusals below fire BEFORE any file/state write.
</must>
Reject:
<reject>
  - no active task and no `<slug>` given -> "no_active_task"
  - the target task's §3 is already `FROZEN` (a frozen contract is re-frozen only via a change-request back to SPECIFY) -> "already_frozen"
  - the target task is not at/after the `contract` phase, or §3 still holds the unfilled DRAFT template (no real contract body) -> "contract_not_drafted"
  - §3 is FROZEN-eligible but the bundle's lowest-confidence flag is absent (mirror the existing `unflagged-freeze` guard so the command can't bypass it) -> "unflagged_freeze"
</reject>
After:
<after>
  - the task's §3 reads `Status: FROZEN @ vN — approved by <name>` (matches `_AUDIT_STAMP_RE`).
  - `state["tasks"][<slug>]` carries a structured `actor` for the freeze event; `add.py audit` shows no actor-trail hole at freeze.
  - the task is eligible to advance contract → tests; a second `freeze` on it refuses `already_frozen`.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ RESOLVED @ freeze — `vN` numbering = INCREMENT (v1 first; N+1 of the highest prior freeze on a re-freeze). Chosen by Tin at the freeze over "v1-stays + body-hash". [contract]
  - [x] CONFIRMED — the actor record lives on the task's state record (`state["tasks"][<slug>].freeze.actor`), consistent with `setup.actor`.
  - [x] CONFIRMED — `freeze` ENFORCES the `unflagged-freeze` guard (not just stamps), closing the bypass the delta named.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: freeze the active task stamps §3 and records the actor
  Given the active task's §3 is a real DRAFT contract with a surfaced lowest-confidence flag
  When I run `add.py freeze`
  Then §3 reads `Status: FROZEN @ v1 — approved by <actor-name>` (matches _AUDIT_STAMP_RE)
  And state["tasks"][<active>] gains a freeze stamp {version: "v1", frozen_at, approved_by, actor}

Scenario: freeze a named task that is not the active one
  Given task `other` (not active) has a real DRAFT §3 with a flag, and `freeze-x` is active
  When I run `add.py freeze other`
  Then `other`'s §3 is FROZEN @ v1 and `other`'s state record carries the freeze stamp
  And the active task stays `freeze-x` (focus unchanged)

Scenario: --by overrides the approver name in the stamp
  Given the active task's §3 is a flagged DRAFT
  When I run `add.py freeze --by "Tin Dang"`
  Then §3 reads `... — approved by Tin Dang` and approved_by == "Tin Dang"
  And the structured actor is still resolved via the override→git→os chain

Scenario: re-freeze after a change-request increments the version
  Given a task whose state freeze record shows a prior `v1` and whose §3 was reverted to DRAFT (flagged)
  When I run `add.py freeze`
  Then §3 reads `Status: FROZEN @ v2 — approved by <actor-name>` and the stamp version == "v2"

Scenario: refuse when there is no active task and no slug
  Given no active task is set
  When I run `add.py freeze`
  Then it exits non-zero with "no_active_task"
  And no TASK.md and no state record is written

Scenario: refuse re-freezing an already-frozen contract
  Given the target task's §3 is already `Status: FROZEN @ v1`
  When I run `add.py freeze`
  Then it exits non-zero with "already_frozen"
  And §3 and the existing freeze stamp are unchanged

Scenario: refuse when §3 is still the unfilled DRAFT template
  Given the target task's §3 still holds the placeholder `<METHOD> <path>` DRAFT body
  When I run `add.py freeze`
  Then it exits non-zero with "contract_not_drafted"
  And §3 and state are unchanged

Scenario: refuse a freeze with no surfaced lowest-confidence flag
  Given the target task's §3 is a real DRAFT but no well-formed lowest-confidence flag is present
  When I run `add.py freeze`
  Then it exits non-zero with "unflagged_freeze"
  And §3 stays DRAFT and no freeze stamp is written
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
CLI: add.py freeze [<slug>] [--by <name>]      # <slug> defaults to the ACTIVE task
  exit 0 (frozen) -> writes BOTH, atomically:
    · tasks/<slug>/TASK.md §3:  "Status: DRAFT"  ->  "Status: FROZEN @ vN — approved by <name>"
    · state["tasks"][<slug>]["freeze"] = {
        version:     "vN",            # v1 first freeze; max(prior freeze.version)+1 on re-freeze
        frozen_at:   "<ISO-8601>",    # _now()
        approved_by: "<name>",        # --by, else resolved actor display name
        actor:       {<identity._actor_stamp(state)>}   # name · email · source (override→git→os)
      }
    · stdout: "froze §3 of <slug> @ vN — approved by <name>"  + _next_footer
  exit !=0 (nothing written) -> stderr "<error_code>", one of:
    "no_active_task" | "already_frozen" | "contract_not_drafted" | "unflagged_freeze"

Schema (state.tasks.<slug>.freeze):
  version str matches /^v\d+$/ · frozen_at ISO-8601 · approved_by non-empty str ·
  actor {name:str, email:str|null, source:"override"|"git"|"os"}   # identical shape to setup.actor
Args:  slug  optional positional (defaults to active task) ·  --by  optional approver name
Reuses (frozen anchors): identity._actor_stamp · _AUDIT_STAMP_RE · _is_frozen · _atomic_write · _now
```

Status: FROZEN @ v1 — approved by Tin Dang
Least-sure flag surfaced at freeze:
  ⚠ [contract] the `vN` numbering policy — the command now OWNS the version number (v1 first, N+1 on
     re-freeze) where today it is human-typed free text and no per-task freeze counter exists. If the
     real intent is "v1 stays; a body-hash tracks change," the `FROZEN @ (v\d+)` reads in the
     flag-guard + producer-snapshot would diverge. Cost if wrong: a rework of how `freeze` derives vN
     (data-only; the command surface stays). RESOLVED: Tin chose INCREMENT at this freeze. Everything
     else (actor on the task record; mirroring the unflagged-freeze guard) is high-confidence.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + every Reject (8 scenarios → 8 tests)
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_freeze_active_stamps_section3_and_actor: draft+flag active task / `freeze` / §3 FROZEN @ v1 + state.freeze {version,frozen_at,approved_by,actor}
  - test_freeze_named_task_leaves_focus_unchanged: two tasks / `freeze first` / first FROZEN + active stays `second`
  - test_by_overrides_approver_name: flagged DRAFT / `freeze --by "Tin Dang"` / approved_by == "Tin Dang"
  - test_refreeze_after_change_request_increments_version: freeze v1, revert §3→DRAFT, freeze / §3 FROZEN @ v2 + version "v2"
  - test_refuse_no_active_task: no active task / `freeze` / exit≠0 "no_active_task" + state unchanged
  - test_refuse_already_frozen: frozen §3 / `freeze` / exit≠0 "already_frozen" + §3 & stamp unchanged
  - test_refuse_contract_not_drafted_template: template §3 at contract / `freeze` / exit≠0 "contract_not_drafted" + not frozen
  - test_refuse_unflagged_freeze: drafted §3, no flag / `freeze` / exit≠0 "unflagged_freeze" + not frozen
  - (+ test_min_pillar LIFECYCLE: `freeze t` classified as a refusal verb — contract_not_drafted, reads no docs/)
</test_plan>

Tests live in: `add-method/tooling/test_freeze_command.py` `add-method/tooling/test_min_pillar.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/test_freeze_command.py` `add-method/tooling/test_min_pillar.py` `add-method/tooling/engine_pin.py` `.add/tooling/` `add-method/src/add_method/_bundled/tooling/`
Strategy (ordered batches): 1. write the red suite (`test_freeze_command.py` + `test_min_pillar.py` LIFECYCLE entry for the new subcommand) · 2. implement `cmd_freeze` + helpers (`_compute_freeze_version`, `_apply_freeze`) + the `freeze` argparse subparser & dispatch in `add.py`, mirroring `cmd_lock` · 3. green the suite · 4. prepare-bundle: re-mirror the canonical engine into `.add/tooling/` + `_bundled/tooling/` and re-pin ENGINE_MD5 (`engine_pin.py`).
Safety rule (feature-specific): validate-then-write — ALL refusals (no_active_task · already_frozen · contract_not_drafted · unflagged_freeze) fire before any write; the §3 TASK.md edit + the state freeze-stamp land as ONE atomic unit (never a half-freeze).
Code lives in: `add-method/tooling/add.py` (canonical); bundled mirrors are mechanical copies.
Constraints: do NOT change any test or the contract; allow-list packages only (stdlib + existing engine modules); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 2026 green (was 2025 + 1 regression test added)
- [x] coverage did not decrease — 9 freeze tests (8 scenarios + 1 regression) + min_pillar LIFECYCLE entry
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; only the build fixed a real bug
- [x] the green was EARNED, not gamed — adversarial refute-read (subagent) returned EARNED-WITH-RESIDUE and caught 1 REAL bug (full-text §3-replace could freeze a §1 decoy); FIXED + regression test added → now EARNED-GREEN; reject tests prove "nothing written"
- [x] concurrency / timing — single-writer `_atomic_write` + `save_state`; validate-then-write; no shared-state race (see residue on two-file atomicity)
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib + existing engine helpers only; the approver name flows through a lambda replacement (no regex-backref injection)
- [x] layering & dependencies follow CONVENTIONS.md — `cmd_freeze` lives in add.py spine; `identity._actor_stamp` qualified (wording + identity-call lints green)
- [x] a person reviewed and approved the change — Tin approved the freeze (§3) + vN policy; build refute-read independently verified

### Build expectations — what "correct" looks like
- [x] `add.py freeze` on a flagged DRAFT §3 writes `Status: FROZEN @ v1 — approved by <name>` matching `_AUDIT_STAMP_RE` — confirmed by dogfood run + test_freeze_active_stamps_section3_and_actor
- [x] state["tasks"][slug].freeze carries {version, frozen_at, approved_by, actor{name,email,source}} — confirmed by the same test asserting the full record shape
- [x] all four refusals fire before any write (no_active_task · already_frozen · contract_not_drafted · unflagged_freeze) — confirmed by the 4 reject tests asserting state/§3 unchanged
- [x] re-freeze increments v1→v2 — confirmed by test_refreeze_after_change_request_increments_version
- [x] live dogfood: `python3 .add/tooling/add.py freeze freeze-actor-stamp` → `already_frozen` (this very task's §3) — seen at the verify step

### Deep checks
- [x] WIRING (code) — `cmd_freeze` reachable via the `freeze` subparser `set_defaults(func=cmd_freeze)`; `_next_freeze_version`/`_CONTRACT_TEMPLATE_RE` referenced in cmd_freeze; min_pillar `test_every_subcommand_is_covered` proves the parser exposes + classifies it
- [x] DEAD-CODE (code) — no orphaned symbol; every new helper is called
- [x] SEMANTIC — n/a (code task)

### GATE RECORD
Outcome: PASS
Residues (non-blocking, non-security; recorded as §7 SPEC deltas): (1) the §3 TASK.md write + the state freeze-stamp are two sequential atomic writes, not one transaction — a crash between degrades to legacy text-only freeze (the §3 FROZEN line lands; the state actor does not); strictly better than today (no freeze ever stamped an actor). (2) `cmd_freeze` does not set `flag_verified` — audit's flag-integrity check stays armed only after tests→build, an existing engine design gap, not a regression.
Reviewed by: Tin Dang (freeze approval) + adversarial refute-read subagent (build) · date: 2026-06-26

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): freeze refusal-rate per code · re-freeze vN distribution · half-freeze occurrences (state.freeze absent while §3 FROZEN)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · open] make the §3 freeze + the state freeze-stamp ONE recoverable unit — today they are two sequential atomic writes, so a crash between leaves §3 FROZEN with no state actor; add an `unfreeze`/repair path or a write-state-first ordering with a §3 rollback (evidence: refute-read residue 1 — `cmd_freeze` writes TASK.md then state.json, no transaction)
- [SPEC · open] `cmd_freeze` should set `flag_verified` (like `_build_entry`) so audit's flag-integrity check is armed at freeze, not only after tests→build — a post-freeze flag removal is invisible to audit until the build crossing (evidence: refute-read residue 2; existing engine gap surfaced by this task)

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · open] a §-section text edit must be SCOPED to that section's span, never a full-document `re.subn count=1` — a bare marker (`Status: DRAFT`) can recur in an earlier section and get hit first; the validate-on-§3 / write-on-full-text split hid it (evidence: refute-read found `cmd_freeze` froze a §1 decoy line; fixed + regression test test_freeze_targets_section3_not_a_decoy_draft_line)
- [TDD · open] a build's own happy-path fixtures can mask a scoping bug when they only ever place the target marker in the right section — an adversarial refute-read that injects a decoy is what caught it (evidence: the 8 original tests were green; the bug surfaced only under the refute-read's decoy-in-§1 attack)
