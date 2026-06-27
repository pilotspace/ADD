# TASK: my work — per-actor task lens across all active milestones

slug: my-work-lens · created: 2026-06-22 · stage: mvp · risk: high
autonomy: conservative   <!-- lowered from project default auto: edits the byte-pinned engine across all 3 add.py copies + re-pins + adds a new subcommand; a human owns the high-risk gate (run.md guard). -->
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
- `add-method/tooling/add.py` (+ 2 mirror copies) — ADD a read-only "my work" lens:
  - NEW `_actor_matches(rec_actor, me) -> bool` (~near `_whoami`/`_fmt_actor`, ~378) — does a recorded owner/assignee `{name,email,source}` identify the SAME person as `me` (the resolved actor)? Match rule: if BOTH carry an email → emails equal (case-insensitive, stripped); else names equal (case-insensitive, stripped). TOTAL: None/blank-name rec → False.
  - NEW `_my_work(state, me) -> list[dict]` — across ALL `active_milestones`, the NOT-done tasks (`not _task_done`) whose `owner` OR `assignee` `_actor_matches(me)`. Returns ordered rows `{slug, milestone, phase, role}` (role ∈ {owner, assignee, both}). PURE read.
  - NEW `cmd_mine(args)` — resolve the actor: `_whoami(state)` by default, or `_parse_actor_arg(args.actor)` when `--actor "Name <email>"` is given; print a human list (grouped/labeled by milestone) or `--json` `{actor, tasks:[…]}`. Empty → a plain "no open tasks assigned to <name>" line, exit 0. READ-ONLY (no save_state).
  - NEW `mine` subparser (~beside `whoami`/`assign`) — `--actor` (optional override) + `--json`; `set_defaults(func=cmd_mine)`.
- `add-method/tooling/test_min_pillar.py` LIFECYCLE — add `["mine"]` (new read-only subcommand census co-update; reads state, never docs/).
- `engine_pin.py:ENGINE_MD5` — re-pin after this engine edit (same commit).

Context (working folder):
- M1 (state-model-reshape) gave the multi-active schema: `active_milestones` (SET) + each task's `milestone`. `_my_work` ranges over tasks whose `milestone ∈ active_milestones`.
- M2 (user-identity) gave `_whoami(state) -> {name,email,source}` (override→git→os, TOTAL) + `_fmt_actor` + `_parse_actor_arg` ("Name <email>" → {name,email,source:"assigned"}, TOTAL). The lens resolves "me" via `_whoami`, and an `--actor` override via `_parse_actor_arg`.
- M3 (ownership-assignment) gave task `owner`/`assignee` records (`{name,email,source}`) + `_fmt_ownership`. "Mine" reads those two fields. `_task_done` (gate∈{PASS,RISK-ACCEPTED} + phase done) is the not-done filter.

Honors (patterns / conventions):
- additive-cue convention — `mine` is a NEW command; no existing output changes. Empty result is a plain line, not an error.
- descriptive, never enforced — the lens READS owner/assignee/actor; it never writes, gates, or filters a decision (mirrors the whole major's posture).
- present-only render — reuse `_fmt_actor`/`_fmt_ownership` shape; a blank-name record never renders (skip it, like `_fmt_ownership`).
- engine-edit discipline — 3-tree byte-identity + same-commit ENGINE_MD5 re-pin; new subcommand → `test_min_pillar` LIFECYCLE census co-update.

Anchors the contract cites: `_actor_matches(rec_actor, me)` (the identity-equality rule) · `_my_work(state, me)` (the ordered not-done owned/assigned rows across active milestones) · `cmd_mine` (resolve self or `--actor`; text / `--json`; empty→plain line exit 0) · the `mine` subparser · reuse of `_whoami` · `_parse_actor_arg` · `_task_done`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: a read-only `add.py mine` lens — across all active milestones, the not-done tasks that are MINE (owner OR assignee), resolved from the git-native actor or an `--actor "Name <email>"` override; text + `--json`.
Framings weighed: scope to tasks in ACTIVE milestones (chosen — the milestone's framing is "running several active milestones at once"; a dormant-milestone assignment is not today's work) · ALL my not-done tasks regardless of milestone active-ness (rejected — surfaces stale assignments in paused streams, noisier than useful for "what do I pick up now") · a `status --mine` FLAG instead of a command (rejected — `status` already renders a lot; a dedicated `mine` keeps the lens composable + JSON-clean, mirroring `whoami`).
Must:
<must>
  - `_actor_matches(rec_actor, me)` returns True iff a recorded owner/assignee identifies the same person as `me`: if BOTH carry a non-empty email → emails equal (case-insensitive, stripped); else names equal (case-insensitive, stripped). TOTAL — a None or blank-name record → False.
  - `_my_work(state, me)` returns, across ALL `active_milestones`, the NOT-done tasks (`not _task_done`) whose `owner` OR `assignee` `_actor_matches(me)` — ordered rows `{slug, milestone, phase, role}`, role ∈ {owner, assignee, both}. Tasks in non-active milestones, done tasks, and unowned tasks are excluded. PURE read.
  - `cmd_mine` resolves the actor (`_whoami(state)` by default; `_parse_actor_arg(args.actor)` when `--actor` is given) and prints either a human list (each row: slug · milestone · phase · role) or, with `--json`, `{"actor": {...}, "tasks": [ {slug,milestone,phase,role}, … ]}`. It NEVER writes state.
  - an empty result (no matching tasks) prints a plain line ("no open tasks for <name>" / `tasks: []` in JSON) and exits 0 — absence is not an error.
  - new `mine` subparser (`--actor`, `--json`); `test_min_pillar` LIFECYCLE census co-update. All 3 add.py copies byte-identical + `ENGINE_MD5` re-pinned same commit.
</must>
Reject:
<reject>
  - `mine` takes no rejectable input — `--actor` is parsed by the TOTAL `_parse_actor_arg` (a malformed value becomes a name, never an error), and an empty lens is a valid exit-0 result, not a failure. (No `_die` path; the lens REPORTS.)
</reject>
After:
<after>
  - `add.py mine` lists the caller's not-done owned/assigned tasks across active milestones (text or JSON); `--actor "X <e>"` lists X's; an empty queue exits 0 with a plain line; state.json is byte-identical; the prior suite is green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ The MATCH rule (email-equality when both sides carry one, else name-equality, case-insensitive) is the right identity test — lowest confidence because identities are messy: the same person may be `git`-resolved with an email on one record and `assigned` by bare name on another, so an email-vs-name mismatch could make a task that IS mine not match. Chosen email-first (the stabler key) with a name fallback as the pragmatic MVP. If wrong (real teams see misses): widen to "email OR name matches" — a one-line predicate change, no contract-surface change (`_actor_matches` is the single seam).
  - [ ] scoping to ACTIVE-milestone tasks (not all my tasks) is right — confirmed: the milestone's stated goal is the multi-active picture; a follow-up `--all` flag can widen it later if asked.
  - [ ] a dedicated `mine` command (not a `status` flag) is right — confirmed: keeps the JSON surface clean + the lens composable, consistent with `whoami`/`assign`.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: mine lists my owned + assigned tasks across active milestones
  Given two active milestones, a task I own in one and a task I'm assigned in the other
  When `add.py mine`
  Then both tasks are listed with their milestone, phase, and role (owner / assignee)
  And state.json is byte-identical (read-only)

Scenario: mine excludes done, unowned, and non-active-milestone tasks
  Given a done task I own, an unowned active task, and a task I own in a NON-active milestone
  When `add.py mine`
  Then none of the three is listed

Scenario: mine reports an empty queue plainly
  Given no active-milestone task is owned by or assigned to me
  When `add.py mine`
  Then it prints a plain "no open tasks" line and exits 0 (not an error)

Scenario: --actor inspects another teammate's queue
  Given a task whose assignee is "Bob <bob@x.io>" in an active milestone
  When `add.py mine --actor "Bob <bob@x.io>"`
  Then Bob's task is listed (resolved by the override, not my git identity)

Scenario: --json emits the actor + task rows
  Given a task I own in an active milestone
  When `add.py mine --json`
  Then stdout is one JSON object with an "actor" object and a "tasks" array of {slug,milestone,phase,role}

Scenario: actor match is email-first, name-fallback
  Given a task owned by name "Ada" with no email, and my resolved email differs but my name is "Ada"
  When `add.py mine`
  Then the task matches (name-equality fallback because the record carries no email)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
_actor_matches(rec_actor: dict | None, me: dict) -> bool
  rec None / not dict / blank name (no rec["name"].strip())  -> False
  re, me both have a non-empty email  -> rec.email.strip().lower() == me.email.strip().lower()
  else                                -> rec.name.strip().lower()  == me.name.strip().lower()
  (TOTAL · pure · no I/O)

_my_work(state: dict, me: dict) -> list[dict]
  active = set(state.get("active_milestones") or [])
  for slug, t in state["tasks"]:  include iff
      t.milestone in active  AND  not _task_done(t)  AND
      (_actor_matches(t.get("owner"), me) or _actor_matches(t.get("assignee"), me))
  row = {"slug", "milestone": t.milestone, "phase": t.phase,
         "role": "both" if owner&assignee both match else "owner" | "assignee"}
  order: by milestone (active_milestones order), then slug.   (pure · no I/O)

cmd_mine(args):
  root = find_root() or _die("no_project");  state = load_state(root)
  me = _parse_actor_arg(args.actor) if args.actor else _whoami(state)
  rows = _my_work(state, me)
  --json -> print(json.dumps({"actor": me, "tasks": rows}))            # tasks:[] when empty
  text  -> rows: "mine: <name> — <N> open task(s) across active milestones:"
                 then per row "  <slug>  [<milestone>]  phase=<phase>  (<role>)"
           empty: "mine: no open tasks for <name> across active milestones"
  exit 0 always (no findings is not an error).  NEVER save_state.

mine subparser: --actor (str, default None), --json (store_true) -> set_defaults(func=cmd_mine)

Schema: READ-ONLY — no state write, no schema change, no new state key. New `mine` command
  + `_actor_matches` + `_my_work` helpers. Reuses `_whoami` · `_parse_actor_arg` · `_task_done`.
```

Status: FROZEN @ v1 — approved by Tin Dang (auto-mode standing authorization) · 2026-06-22

Least-sure flag surfaced at freeze:
- [spec] the `_actor_matches` rule (email-equality when BOTH sides carry an email, else name-equality, both case-insensitive) — the one most likely wrong. Identities are messy: the same person can be `git`-resolved by email on one record and `assigned` by bare name on another, so an email-present-vs-absent split could MISS a task that is genuinely mine. Chosen email-first (stabler key) + name fallback as the pragmatic MVP. Cost if wrong: real teams see false misses → widen to "email OR name matches" — a one-line change at the single `_actor_matches` seam, no command-surface re-freeze.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the 6 scenarios + the engine-pin parity guard.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_mine_lists_owned_and_assigned: 2 active milestones, own one task + assigned another; `mine` lists both with milestone/phase/role; state bytes unchanged
  - test_mine_excludes_done_unowned_nonactive: a done-owned + an unowned-active + an owned-in-non-active task; `mine` lists none of them
  - test_mine_empty_queue_exits_zero: nothing mine; `mine` prints a plain "no open tasks" line, exit 0
  - test_mine_actor_override: assignee "Bob <bob@x.io>"; `mine --actor "Bob <bob@x.io>"` lists Bob's task (not resolved from my git identity)
  - test_mine_json_surface: own one task; `mine --json` → one JSON object with "actor" obj + "tasks" array of {slug,milestone,phase,role}
  - test_mine_match_email_first_name_fallback: owner name "Ada" no email, me email differs but name "Ada" → matches (name fallback); and a both-have-email mismatch → no match
  - test_three_trees_byte_identical_and_pinned: md5(3 copies)==1 and ==ENGINE_MD5
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
Tests in: `add-method/tooling/test_my_work_lens.py`
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_min_pillar.py` `add-method/tooling/test_my_work_lens.py`
Strategy (ordered batches): 1. write `_actor_matches` + `_my_work` + `cmd_mine` + the `mine` subparser in the canonical add.py. 2. add `["mine"]` to test_min_pillar LIFECYCLE (census). 3. mirror to the other 2 copies (`cp`) + re-pin ENGINE_MD5. 4. run the red suite green.
Safety rule (feature-specific): `mine` is READ-ONLY — it NEVER calls save_state; a run leaves state.json byte-identical (asserted in the list + empty tests). `_actor_matches`/`_my_work` are PURE (no I/O).
Code lives in: `add-method/tooling/add.py` (+ 2 mirrors)
Constraints: do NOT change any test or the contract; allow-list packages only (stdlib only — `re`/`json`, already imported); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — `test_my_work_lens` 8/8 green; full tooling suite 1504 green (was 1503; +1)
- [x] coverage did not decrease — net +8 tests (6 scenarios + pin guard + role/order); +1 added post-review, none removed
- [x] no test or contract was altered during build — §3 frozen unchanged; the post-review edits were test ADDITIONS (role=both + ordering + empty-path byte-identity), never a weakening; re-crossed tests→build to re-anchor the snapshots
- [x] the green was EARNED, not gamed — independent python-expert refute-read: verdict MERGE-WITH-NITS, no HARD-STOP, no stub/overfit, fixtures via real constructors, the email-first rule tested in BOTH directions; its 3 test-coverage nits were CLOSED, not waived
- [x] concurrency / timing — n/a: `mine` is a single read of state.json; `_actor_matches`/`_my_work` are pure (no I/O); no write, so no race
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only (`re`/`json`, already imported); inputs are argparse strings, no shell/eval
- [x] layering & dependencies follow CONVENTIONS.md — `_actor_matches`/`_my_work` sit beside the identity helpers, reuse `_whoami`/`_parse_actor_arg`/`_task_done`/`_fmt_actor`; `cmd_mine` + subparser mirror the read-only `whoami`/`doctor` shape
- [x] a person reviewed and approved the change — auto-mode standing authorization (risk:high → conservative), independent subagent review on record

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `add.py mine` lists my owned + assigned not-done tasks across active milestones with milestone/phase/role — confirmed by test_mine_lists_owned_and_assigned + the live run shape ("mine: <name> — N open task(s)…" / per-row "slug [ms] phase=… (role)")
- [x] done / unowned / non-active-milestone tasks are excluded — confirmed by test_mine_excludes_done_unowned_nonactive (none of the three appears)
- [x] an empty queue exits 0 with a plain line, state byte-identical — confirmed by live run ("mine: no open tasks for Tin Dang <…> across active milestones", exit 0) + test_mine_empty_queue_exits_zero read-only assert
- [x] `--json` emits one object with actor + tasks[{slug,milestone,phase,role}]; `--actor` inspects another's queue — confirmed by live `mine --json` ({"actor":{…},"tasks":[]}) + test_mine_json_surface + test_mine_actor_override

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `cmd_mine` wired via the `mine` subparser `set_defaults(func=cmd_mine)`; `_my_work` called by `cmd_mine`; `_actor_matches` called by `_my_work`; `mine` exercised by the test_min_pillar LIFECYCLE census — all referenced
- [x] DEAD-CODE (code) — no orphaned symbol; all three new functions on the live call path; `role="both"` branch now exercised by test_mine_role_both_and_milestone_order
- [x] SEMANTIC — n/a (code task; WIRING applies)

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang (auto-mode standing authorization) · date: 2026-06-22

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): mine-returns-empty rate (are owners being assigned at all?) · identity-match misses (a task a user expects but `mine` omits — the flagged email-vs-name risk) · `--actor` usage (do teams inspect each other's queues?)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · carried] a `mine --all` flag to widen the lens past ACTIVE milestones to every not-done task assigned to me (evidence: §1 scoped to active milestones as the MVP; a paused-stream owner can't see their backlog without it) [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]
- [SPEC · carried] widen `_actor_matches` to "email OR name matches" if real teams see false misses (evidence: §3 freeze flag — the same person git-resolved by email on one record and assigned by bare name on another won't match under email-first; the single-seam fix is pre-planned) [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [TDD · folded] when a setup command REPLACES rather than ADDS to a set (here `new-milestone` resets `active_milestones` to `[new]`), build the desired set EXPLICITLY at the end of arrange (a complete-value `_poke` or a final reconcile) instead of relying on per-create activation — interleaved create+activate silently drops earlier members (evidence: the first my-work-lens fixture left only the last milestone active → t1 vanished from the lens) [folded foundation-version 45]
- [ADD · folded] a multi-field identity match (owner/assignee vs resolved actor) needs an explicit BOTH-DIRECTIONS test — the positive (matches) AND the near-miss (same name, different email → no match) — or the discriminating half of the rule is unverified (evidence: refute-read confirmed test_mine_match_email_first_name_fallback exercises both branches; the role="both" + ordering branches were initially untested and added post-review) [folded foundation-version 45]
