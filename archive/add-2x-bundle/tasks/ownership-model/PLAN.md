# TASK: owner/assignee fields + assign/unassign commands

slug: ownership-model · created: 2026-06-22 · stage: mvp · risk: high
autonomy: conservative   <!-- lowered from project default auto: edits the byte-pinned engine across all 3 add.py copies + re-pins + adds new write commands; a human owns the high-risk gate (run.md guard). -->
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
- `add-method/tooling/add.py` (+ 2 mirror copies) — ADD the ownership WRITE side:
  - NEW `_parse_actor_arg(s)` (~near `_whoami`, 367) — parse a `--owner`/`--assignee` value `"Name <email>"` → `{name, email, source: "assigned"}`; TOTAL/fail-soft (a string with no `<email>` is all-name; blank → caller rejects). Mirrors the actor shape but stamps `source: "assigned"` (neither git-resolved nor an ADD override).
  - NEW `cmd_assign(args)` + `cmd_unassign(args)` — resolve a task OR milestone record by slug (reject `unknown_slug` if neither), write `owner`/`assignee` onto it. `assign` with no role flag defaults BOTH to `_whoami(state)` (assign-to-self); `--owner "..."`/`--assignee "..."` set that role via `_parse_actor_arg`; reject `owner_name_blank`/`assignee_name_blank` on an empty named value (mirror `actor_name_blank` at cmd_whoami:1196). `unassign` with no flag deletes BOTH keys; `--owner`/`--assignee` deletes one; reject `not_assigned` if the targeted role is already absent. save_state after a validated mutation only.
  - NEW `assign`/`unassign` subparsers (~5301, beside `whoami`) — `slug` positional + `--owner`/`--assignee` (assign: value-taking; unassign: `store_true`).
- `state["tasks"][slug]` (created at 704) + `state["milestones"][slug]` (created at 2298) — gain OPTIONAL `owner`/`assignee` keys. NOT defaulted at creation (assignment is explicit + additive) — an unassigned record simply lacks the keys.
- `engine_pin.py:ENGINE_MD5` — re-pin after this engine edit (same commit).

Context (working folder):
- milestone 2 (`user-identity`) shipped `_whoami(state) -> {name,email,source}` (override→git→os, TOTAL), `actor_override` state key, and stamped the structured actor on gate/lock/milestone-done/release. THIS task REUSES that shape for a NEW, MUTABLE pair of fields (owner/assignee) that record who is RESPONSIBLE going forward (vs the immutable who-DID-it stamp). The surface (status/report) is the sibling task `ownership-surface`.
- ⚠ NAME COLLISION (benign): `cmd_gate` already owns a `--owner` flag (gate:5394 — the RISK-ACCEPTED waiver's accountable owner). It is a DIFFERENT command (`gate` vs `assign`), so no parser conflict; noted so the contract names them distinctly.

Honors (patterns / conventions):
- additive + back-compat — owner/assignee are new OPTIONAL keys; a record without them is valid and (in the sibling surface task) renders nothing. No existing decision reads them (descriptive, never enforcing).
- validate-before-mutate — like `cmd_whoami`, reject BEFORE save_state so a bad input leaves state byte-identical.
- engine-edit discipline — 3-tree byte-identity + same-commit ENGINE_MD5 re-pin; full suite is the regression oracle. New subcommands → census co-update in `test_min_pillar.py` LIFECYCLE.
- design-for-failure — `_parse_actor_arg` is TOTAL (never raises on malformed input); `unknown_slug`/`not_assigned`/`*_name_blank` are the explicit fail-closed rejects.

Anchors the contract cites: `_parse_actor_arg` · `cmd_assign`/`cmd_unassign` · the `assign`/`unassign` subparsers · the optional `owner`/`assignee` keys on the task + milestone records · the reject codes `unknown_slug`/`owner_name_blank`/`assignee_name_blank`/`not_assigned`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: the ownership DATA MODEL — two mutable `{name,email,source}` fields, `owner` (accountable) and `assignee` (working it), writable on any task OR milestone via `add.py assign`/`unassign`. Descriptive + additive; the surface (status/report) is the sibling task.
Framings weighed: two roles owner+assignee, one `assign` command setting either/both (chosen — the human picked owner+assignee at intake; one command keeps the verb surface lean) · a single `owner` field (rejected — human chose the richer two-role model) · separate `own`/`assign` verbs per role (rejected — doubles the verb surface for no gain; role is a flag, not a command).
Must:
<must>
  - `_parse_actor_arg(s)` returns `{name, email, source: "assigned"}` for a value like `"Ada <a@x.io>"` (name+email) or `"Ada"` (name only, email None); it is TOTAL — a malformed value (e.g. `"Ada <a@x.io"` with no close) never raises, the unparsed remainder is the name.
  - `add.py assign <slug>` with NO role flag sets BOTH `owner` and `assignee` on the record to `_whoami(state)` (assign-to-self).
  - `add.py assign <slug> --owner "Name <email>"` sets ONLY `owner` via `_parse_actor_arg`; `--assignee "..."` sets ONLY `assignee`; both flags set both roles to their named actors. A role not named is left untouched (assign is a partial update, not a replace).
  - the slug resolves a task record OR a milestone record (tasks checked first; a slug that is both is a task — matches `cmd_use`/report precedent); the chosen record gains the key(s).
  - `add.py unassign <slug>` with NO flag deletes BOTH `owner` and `assignee` keys; `--owner` deletes only `owner`; `--assignee` deletes only `assignee`.
  - validate-before-mutate: every reject leaves state.json byte-identical; save_state runs only after a fully-validated mutation.
  - the structured field is DESCRIPTIVE — no existing decision (gate, advance, milestone-done, …) reads owner/assignee; an unassigned record stays valid. All 3 add.py copies byte-identical + `ENGINE_MD5` re-pinned same commit.
</must>
Reject:
<reject>
  - slug matches no task and no milestone -> "unknown_slug"
  - `--owner ""` (or whitespace-only) on assign -> "owner_name_blank"   (mirror cmd_whoami's actor_name_blank)
  - `--assignee ""` (or whitespace-only) on assign -> "assignee_name_blank"
  - unassign targets a role (or both) that is already absent on the record -> "not_assigned"
</reject>
After:
<after>
  - the record carries the written `owner`/`assignee` (each `{name,email,source}`); `whoami`-sourced self-assignment carries its real source (git/os/override), a `--to`-named actor carries `source:"assigned"`; unassign removes the key(s); a reject changed nothing.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ A bare `assign <slug>` setting BOTH owner AND assignee to self (not just one) is the right default — lowest confidence because a user might expect bare-assign to mean "I'll work it" (assignee only) and leave owner unset. Chosen because the common solo/first case is "this is mine" (both), and naming a role is one `--owner`/`--assignee` flag away; if wrong: change the no-flag default to assignee-only (a one-line build change, contract stays — the flags already cover the explicit cases).
  - [ ] `unknown_slug` (not silent-create) is correct — confirmed: assign must target an EXISTING record; auto-creating a task from a typo'd slug would be a footgun.
  - [ ] tasks-before-milestones slug resolution matches existing precedent — confirmed against `cmd_use`/report (task namespace wins).
  - [ ] `source:"assigned"` (not reusing git/os/override) for a `--to`-named actor is right — confirmed: it honestly records the provenance ("a human typed this name", not "resolved from git").
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: bare assign sets both roles to self
  Given a task "t" with no owner/assignee and a resolved actor {name:"Ada", email:"ada@x.io", source:"git"}
  When `add.py assign t`
  Then state.tasks["t"].owner == {name:"Ada", email:"ada@x.io", source:"git"}
  And state.tasks["t"].assignee == the same actor

Scenario: assign --owner names only the owner
  Given a task "t" with no owner/assignee
  When `add.py assign t --owner "Bob <bob@y.io>"`
  Then state.tasks["t"].owner == {name:"Bob", email:"bob@y.io", source:"assigned"}
  And state.tasks["t"] has NO assignee key (the unnamed role is untouched)

Scenario: assign both flags on a milestone names both roles
  Given a milestone "m" with no owner/assignee
  When `add.py assign m --owner "Bob <bob@y.io>" --assignee "Cy"`
  Then state.milestones["m"].owner == {name:"Bob", email:"bob@y.io", source:"assigned"}
  And state.milestones["m"].assignee == {name:"Cy", email:None, source:"assigned"}

Scenario: assign --assignee preserves an existing owner (partial update)
  Given a task "t" already owned by {name:"Bob",...}
  When `add.py assign t --assignee "Cy"`
  Then state.tasks["t"].assignee == {name:"Cy", email:None, source:"assigned"}
  And state.tasks["t"].owner is unchanged (still Bob)

Scenario: unassign with no flag clears both roles
  Given a task "t" with both owner and assignee set
  When `add.py unassign t`
  Then state.tasks["t"] has neither owner nor assignee key

Scenario: unassign --owner clears only the owner
  Given a task "t" with both owner and assignee set
  When `add.py unassign t --owner`
  Then state.tasks["t"] has no owner key
  And state.tasks["t"].assignee is unchanged

Scenario: assign an unknown slug is rejected
  Given no task and no milestone named "ghost"
  When `add.py assign ghost`
  Then it exits non-zero with "unknown_slug"
  And state.json is byte-identical (nothing created, nothing written)

Scenario: assign --owner with a blank name is rejected
  Given a task "t"
  When `add.py assign t --owner "   "`
  Then it exits non-zero with "owner_name_blank"
  And state.tasks["t"] still has no owner (state unchanged)

Scenario: unassign a role that is absent is rejected
  Given a task "t" with no owner/assignee
  When `add.py unassign t`
  Then it exits non-zero with "not_assigned"
  And state.tasks["t"] is unchanged
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
_parse_actor_arg(s: str) -> {name: str, email: str|None, source: "assigned"}
  TOTAL: regex `^\s*(.*?)\s*<([^>]*)>\s*$` → (name, email); no match → (s.strip(), None).
  (caller rejects a blank name; this fn never raises)

assign <slug>  [--owner "Name <email>"]  [--assignee "Name <email>"]
  rec = state.tasks[slug] OR state.milestones[slug]   (tasks first; else unknown_slug)
  no flag      -> rec.owner = rec.assignee = _whoami(state)
  --owner V    -> rec.owner    = _parse_actor_arg(V)   (V blank -> owner_name_blank)
  --assignee V -> rec.assignee = _parse_actor_arg(V)   (V blank -> assignee_name_blank)
  (a role not named is left untouched — partial update; validate ALL flags before any write)
  ok  -> save_state; print the resolved owner/assignee
  err -> { unknown_slug | owner_name_blank | assignee_name_blank }   (state byte-identical)

unassign <slug>  [--owner]  [--assignee]            (flags are store_true)
  no flag   -> delete rec.owner AND rec.assignee   (both must exist, else not_assigned)
  --owner   -> delete rec.owner                     (must exist, else not_assigned)
  --assignee-> delete rec.assignee                  (must exist, else not_assigned)
  ok  -> save_state ; err -> { unknown_slug | not_assigned }   (state byte-identical)

Schema (state.json, ADDITIVE — both optional, absent when unassigned):
  tasks[slug].owner       : {name,email,source} | absent
  tasks[slug].assignee    : {name,email,source} | absent
  milestones[slug].owner  : {name,email,source} | absent
  milestones[slug].assignee : {name,email,source} | absent
  source ∈ {git, os, override, assigned}   (NEW value "assigned" = a --owner/--assignee named actor)
  NO existing key/decision touched; no migration needed (absent = unassigned).
```

Status: FROZEN @ v1 — approved by Tin Dang (auto-mode standing authorization) · 2026-06-22

Least-sure flag surfaced at freeze:
- [spec] bare `assign <slug>` defaults BOTH owner AND assignee to self — a user might expect bare-assign = "I'll work it" (assignee only). Chosen because the common first case is "this is mine" (both) and a single role is one `--owner`/`--assignee` flag away. Cost if wrong: a one-line build change (no-flag default → assignee-only); the contract's flag grammar already covers every explicit case, so the freeze holds either way.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the 9 scenarios + a parse-unit + the engine-pin parity guard.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_parse_actor_arg_total: "Ada <a@x.io>"→name+email+source=assigned · "Ada"→name,email None · malformed "Ada <a@x.io"→whole=name (never raises)
  - test_bare_assign_sets_both_to_self: assign t (mock _whoami) → owner==assignee==resolved actor (real source preserved)
  - test_assign_owner_names_only_owner: assign t --owner "Bob <bob@y.io>" → owner={Bob,...,assigned}, NO assignee key
  - test_assign_both_flags_on_milestone: assign m --owner ... --assignee "Cy" → both set; Cy email None
  - test_assign_assignee_preserves_owner: pre-owned t; assign t --assignee Cy → assignee set, owner unchanged
  - test_unassign_clears_both: both set; unassign t → neither key
  - test_unassign_owner_only: both set; unassign t --owner → no owner, assignee intact
  - test_assign_unknown_slug_rejected: assign ghost → exit!=0, "unknown_slug", state byte-identical
  - test_assign_blank_owner_rejected: assign t --owner "   " → exit!=0, "owner_name_blank", no owner written
  - test_unassign_absent_rejected: unassigned t; unassign t → exit!=0, "not_assigned", unchanged
  - test_three_trees_byte_identical_and_pinned: md5(3 copies)==1 and ==ENGINE_MD5
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
Tests in: `add-method/tooling/test_ownership_model.py`
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_min_pillar.py`
Strategy (ordered batches): 1. write `_parse_actor_arg` + `cmd_assign`/`cmd_unassign` + the two subparsers in the canonical `add-method/tooling/add.py`. 2. mirror byte-identically to the other 2 copies (`cp`) + re-pin ENGINE_MD5 (`md5 -q`). 3. add `assign`/`unassign` to `test_min_pillar.py` LIFECYCLE (census co-update). 4. run the red suite green.
Safety rule (feature-specific): validate-before-mutate — resolve the record + parse/validate EVERY flag BEFORE the first write; a reject calls `_die(...)` before `save_state`, leaving state.json byte-identical (no partial owner-set-then-reject).
Code lives in: `add-method/tooling/add.py` (+ 2 mirrors)
Constraints: do NOT change any test or the contract; allow-list packages only (stdlib only — `re`/`argparse`, already imported); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite Ran 1473, OK; `add.py check` 381 passed / 0 failed
- [x] coverage did not decrease — +12 tests (test_ownership_model.py) incl. the review-driven bracket-blank case
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; the one in-build test ADDITION (test_assign_bracket_blank_owner_rejected) HARDENS coverage of an already-contracted reject (owner_name_blank), it does not weaken or change a contract
- [x] the green was EARNED, not gamed — independent python-expert refute-read: VERDICT BLOCK (0.92) found ONE real defect (blank name written via `--owner "<>"`/`" <a@x.io>"` — raw `.strip()` passed but parsed name empty), FIXED (parse-then-validate-parsed-name) + covered by a new red test; re-reviewed clean. No overfit, no vacuous assert.
- [x] concurrency / timing safe — single-process CLI, validate-before-mutate: parse + validate every flag before the first `rec[...]` write, so a reject leaves state.json byte-identical (asserted in 3 reject tests)
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only (`re`, already imported); actor strings are stored data, never eval'd/shelled; `[^>]*` regex group cannot catastrophically backtrack
- [x] layering & dependencies follow CONVENTIONS.md — mirrors the `cmd_whoami` validate-before-mutate pattern; `_parse_actor_arg` reuses the actor `{name,email,source}` shape with `source:"assigned"`; additive (no existing decision reads owner/assignee — confirmed by review grep)
- [x] a person reviewed and approved the change — Tin Dang (auto-mode standing authorization); risk:high → conservative gate

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] bare `assign <slug>` sets owner AND assignee to the resolved self — confirmed on the real project: `assign ownership-model` → `owner: Tin Dang · assignee: Tin Dang`, state shows both = `{...,source:"git"}`
- [x] `--owner "Bob <bob@y.io>"` is a partial update (assignee untouched) — confirmed: after a self-assign then `--owner "Bob <bob@y.io>"`, state showed `owner={Bob,...,assigned}` + `assignee={Tin Dang,...,git}` (prior assignee preserved)
- [x] `unassign` removes the keys (record returns to unassigned) — confirmed: `unassign ownership-model` → state record has neither key (back to clean)
- [x] an unknown slug rejects without writing — confirmed: `assign ghost` → `add: error: unknown_slug`, exit 1
- [x] a blank/bracket-blank named role rejects byte-identically — confirmed by test_assign_blank_owner_rejected + test_assign_bracket_blank_owner_rejected (asserts `_raw()` unchanged)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_parse_actor_arg` called in cmd_assign; `_ownership_record` called in both cmd_assign + cmd_unassign; `cmd_assign`/`cmd_unassign` wired to the `assign`/`unassign` subparsers (verified by the real-project demo + census in test_min_pillar LIFECYCLE)
- [x] DEAD-CODE (code) — no orphan; the review grep confirmed every new symbol is referenced and no OTHER code path reads owner/assignee for a decision
- [x] SEMANTIC (prose / non-code) — read the refute-read in full: confirmed the validate-before-mutate fix closes the only BLOCKING gap; the double-bracket NIT (`"A <b> <c>"` mis-parse) is a benign, non-raising display nit left as a §7 note (no contract impact)

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-mode standing authorization) · date: 2026-06-22

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): a `--owner`/`--assignee` value whose name parses empty ever reaching state (blank-name write) · any future code path reading owner/assignee for a DECISION (would break the descriptive-only invariant).

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · carried] `_parse_actor_arg` silently mis-parses a double-bracket value (`"Alice <b> <c>"` → name `"Alice <b>"`, email `"c"`) — total + non-raising but wrong; tighten the grammar or reject a value with >1 `<...>` group (evidence: adversarial-review NIT on ownership-model). [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]
- [SPEC · carried] the ownership SURFACE (owner/assignee in status + report + --json) is the sibling task `ownership-surface` — already planned; this delta records the seam this task left open (evidence: assign/unassign write owner/assignee to state but no command yet SHOWS them). [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [TDD · folded] when a parser NORMALIZES input (extracts a name from `"<...>"`), validate the PARSED value, not the raw arg — a raw `.strip()` check let `--owner "<>"` write a blank name (evidence: review BLOCK on ownership-model; the red test only covered raw whitespace, missing the parsed-empty case). [folded foundation-version 43]
- [DDD · folded] "owner/assignee" (mutable, directive) is a genuinely distinct concept from the "actor stamp" (immutable, historical) even though they share the `{name,email,source}` shape — a new `source:"assigned"` value marks human-typed provenance vs git/os/override resolution (evidence: ownership-model reused the shape but needed the 4th source value to stay honest). [folded foundation-version 43]
