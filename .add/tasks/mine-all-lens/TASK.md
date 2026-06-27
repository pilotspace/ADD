# TASK: mine --all: widen the ownership lens past active milestones

slug: mine-all-lens · created: 2026-06-26 · stage: mvp
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
- `add-method/tooling/add.py:_my_work` (166-186) — pure lens: NOT-done tasks owned/assigned to `me` whose milestone ∈ `active_set`, sorted by active order then slug. TODAY filters `t.get("milestone") not in active_set`. ADD a `scope_all=False` param: when True, DROP the active-set filter (span every milestone + loose). Sort needs NO change — `order.get(milestone, len(order))` already sorts non-active/None after active, then by slug.
- `add-method/tooling/add.py:cmd_mine` (2369-2388) — reads `--actor`/`--json`, calls `_my_work(state, me)`, renders `mine: <who> — N open task(s) across active milestones:` + `  <slug> [<milestone>] phase=… (<role>)`. ADD: read `getattr(args,"all",False)`, pass to `_my_work`; header/empty-line say "all milestones" under --all; render a loose (milestone-less) row as `[loose]` not `[None]`.
- `add-method/tooling/add.py` mine subparser (`--actor`, `--json`): ADD `--all` (store_true).
- helper reused unchanged: `identity._actor_matches` — ALREADY does email-first-then-name match (the "email-OR-name" half shipped with the original `mine`); `_task_done`, `_fmt_actor`.
- `engine_pin.py:ENGINE_MD5` = `1e01586bbb7df7328f792e508b08f499` — re-pin after this engine edit.

Context (working folder):
- 3 byte-identical add.py copies (`add-method/tooling` · `.add/tooling` · `add-method/src/add_method/_bundled/tooling`) — edit in lockstep + re-pin. `add-method/tooling/test_my_work_lens.py` is the sibling oracle: `test_mine_excludes_done_unowned_nonactive` asserts plain `mine` EXCLUDES a mine-but-non-active task — `--all` must NOT change that path. New tests land in `add-method/tooling/test_mine_all_lens.py`.

Honors (patterns / conventions):
- additive + opt-in: `--all` is a NEW flag; plain `mine` (active-only) text + json stay byte-identical (`scope_all=False` default keeps today's filter + header + render exactly).
- pure/total lens: `_my_work` stays pure (no I/O, no mutation); the new arm only widens the membership predicate; read-only command.
- present-only render: a loose row renders `[loose]` (mirrors `ready`'s no-bracket-for-milestone-less convention, made explicit) — never `[None]`.
- engine-edit discipline: 3-tree byte-identity + same-commit ENGINE_MD5 re-pin; the existing suite is the regression oracle.

Anchors the contract cites: `_my_work(state, me, scope_all=False)` · `cmd_mine` (the `--all` arm + loose render) · the `--all` subparser flag · `identity._actor_matches` (reused) · `engine_pin.ENGINE_MD5`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `mine --all` widens the ownership lens past the active SET — `_my_work` gains a `scope_all` arm that lists EVERY not-done task owned-by/assigned-to the actor across ALL milestones (and loose, milestone-less tasks), not just the active ones. The email-OR-name match already ships in `_actor_matches`; this adds only the scope widening + the flag.
Framings weighed: a `scope_all` param on `_my_work` (chosen — one lens, the new arm just drops the active-set filter; plain `mine` stays the `scope_all=False` default, byte-identical) · a separate `_my_work_all` function (rejected — duplicates the owner/assignee/sort logic) · make `mine` always span all and add a `--active-only` flag (rejected — inverts the default, breaks byte-identity + the existing tests).
Must:
<must>
  - `mine --all` lists every NOT-done task owned-by OR assigned-to the actor across ALL milestones — active, non-active, AND loose (milestone-less) — using the existing `_actor_matches` (email-first, then name; case-insensitive).
  - plain `mine` (no `--all`) is UNCHANGED: active-milestones-only, same header "across active milestones", same `[<milestone>]` render — byte-identical text + json (the existing test_my_work_lens is the oracle, no test weakened).
  - under `--all` the header/empty-line read "across all milestones"; a loose (milestone-less) row renders `[loose]`, never `[None]`; ordering stays active-milestones-first (by active order) then the rest by slug.
  - `--all` composes with `--actor` (inspect another actor's full queue) and `--json` (the json `tasks` array just carries more rows; shape unchanged: {slug, milestone, phase, role}, milestone null for loose).
  - read-only + pure/total preserved: `_my_work` never mutates, never raises on malformed input; `mine` writes nothing.
  - all 3 add.py copies byte-identical + `ENGINE_MD5` re-pinned; parity/pin tests green.
</must>
Reject:
<reject>
  - (no new error code — `mine` has no failure mode here; an empty `--all` queue is the same plain exit-0 line as today, just "across all milestones".)
</reject>
After:
<after>
  - `add.py mine --all` surfaces the actor's whole backlog across every milestone (+ loose); plain `mine` is unchanged; the full suite is green with no test changed; 3 copies + pin green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ `--all` INCLUDES loose (milestone-less) tasks owned by the actor — I read "across ALL milestones" as "all my open work", and a loose task is still my work. Lowest confidence because the criterion says "milestones" and a loose task is in none; if you'd rather `--all` mean "all MILESTONE-bound tasks", I drop the loose rows (and the `[loose]` render). Cost if wrong: a one-line filter + remove one render branch.
  - [ ] loose rows render `[loose]` (not `[None]`/no-bracket) — chosen for an unambiguous, present token; confirm the label.
  - [ ] done tasks stay excluded under `--all` (it widens MILESTONE scope, not the not-done filter) — confirm; "my work" = open work.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: --all surfaces a mine-but-non-active task
  Given milestone m1 (active) with my task t1, and milestone paused (NOT active) with my task t2
  When `mine --all` runs
  Then both t1 and t2 are listed
  And the header reads "across all milestones"

Scenario: plain mine still excludes the non-active task (byte-identical)
  Given the same state
  When `mine` runs (no --all)
  Then t1 is listed but t2 is NOT
  And the header reads "across active milestones"

Scenario: --all includes a loose (milestone-less) task and renders [loose]
  Given a loose task t3 (milestone none) that I own
  When `mine --all` runs
  Then t3 is listed rendered with "[loose]" (never "[None]")

Scenario: --all still excludes done and unowned tasks
  Given a done task I own and an unowned open task, both in a non-active milestone
  When `mine --all` runs
  Then neither is listed (it widens milestone scope, not the not-done/ownership filters)

Scenario: --all composes with --json
  Given a mine-but-non-active task t2
  When `mine --all --json` runs
  Then the json "tasks" array includes t2 with shape {slug, milestone, phase, role}

Scenario: The engine edit stays pinned
  Given all three add.py copies are edited
  When the parity + ENGINE_MD5 tests run
  Then the three copies are byte-identical AND match the re-pinned ENGINE_MD5
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
# mine --all — widen the ownership lens past the active SET (internal CLI; READ-ONLY, pure)

_my_work(state, me, scope_all=False) -> list[dict]    # NEW param; scope_all=False == today, byte-identical
  for slug, t in tasks.items():
    if not isinstance(t, dict) or _task_done(t): continue
    if not scope_all and t.get("milestone") not in active_set: continue   # active filter only when NOT scope_all
    owns = identity._actor_matches(t.get("owner"), me)
    assigned = identity._actor_matches(t.get("assignee"), me)
    if not (owns or assigned): continue
    role = "both"/"owner"/"assignee"
    rows.append({slug, milestone: t.get("milestone"), phase, role})   # milestone may be None under scope_all
  order = {m: i for i, m in enumerate(active)}                        # unchanged sort
  rows.sort(key=lambda r: (order.get(r["milestone"], len(order)), r["slug"]))   # active first, rest by slug
  return rows

cmd_mine(args):
  all_ = getattr(args, "all", False)
  rows = _my_work(state, me, scope_all=all_)
  scope = "all" if all_ else "active"
  json:  {"actor": me, "tasks": rows}                                # shape unchanged (milestone null for loose)
  text:  header "mine: <who> — N open task(s) across {scope} milestones:" (or "no open tasks … across {scope} milestones")
         row    "  <slug>  [<milestone> or 'loose'>]  phase=<p>  (<role>)"   # loose → "[loose]", never "[None]"

mine subparser: add `--all` (store_true).
Invariant: scope_all=False path (plain `mine`) text + json BYTE-IDENTICAL to pre-change (test_my_work_lens the oracle).
Errors: none new. Engine: 3 add.py copies byte-identical + ENGINE_MD5 re-pinned same commit.
```

Status: FROZEN @ v1 — approved by Tin Dang
Least-sure flag surfaced at freeze: [spec] `--all` INCLUDES loose (milestone-less) tasks the actor owns, rendered `[loose]` — I read "across ALL milestones" as "all my open work", but a loose task is in NO milestone, so this is a judgment call. If you'd rather `--all` mean "all MILESTONE-bound tasks", I drop the loose rows + the `[loose]` render (a one-line filter). Second flag: [contract] plain `mine` must stay byte-identical — guaranteed by `scope_all=False` defaulting to today's exact filter/header/render; the existing test_my_work_lens is the oracle.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the `scope_all` arm of `_my_work` + the `--all` arm of `cmd_mine` (text + json + loose render); the existing test_my_work_lens as the byte-identity oracle for plain `mine`.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_all_surfaces_nonactive: m1 active{t1 mine}, paused non-active{t2 mine} → `mine --all` lists t1 AND t2; header "across all milestones"
  - test_plain_mine_still_excludes_nonactive: same state → `mine` (no flag) lists t1, NOT t2; header "across active milestones"
  - test_all_includes_loose_renders_loose: loose task t3 (milestone none) I own → `mine --all` lists t3 with "[loose]", not "[None]"
  - test_all_excludes_done_and_unowned: done-mine + unowned in a non-active milestone → `mine --all` lists neither
  - test_all_json_includes_nonactive: `mine --all --json` → tasks array has t2 with {slug, milestone, phase, role}
  - (regression) the FULL existing suite incl. test_my_work_lens stays green with NO test changed (plain mine byte-identical)
  - test_three_trees_pinned: 3 add.py copies byte-identical AND == engine_pin.ENGINE_MD5
</test_plan>

Tests live in: `add-method/tooling/test_mine_all_lens.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_mine_all_lens.py`
Strategy (ordered batches): 1. write `test_mine_all_lens.py` red (scope_all arm + --all text/json + loose render + byte-identity). · 2. in `add-method/tooling/add.py`: add `scope_all=False` to `_my_work` (gate the active-set filter on `not scope_all`); add `--all` arm to `cmd_mine` (scope word in header/empty-line; `[loose]` render for milestone-less rows); add `--all` subparser flag. · 3. run the FULL suite — plain `mine` (test_my_work_lens) must stay green with NO test change. · 4. mirror byte-identically to the other 2 copies; re-pin ENGINE_MD5; green incl. parity/pin.
Safety rule (feature-specific): `scope_all=False` MUST reproduce today's `_my_work` exactly (same filter, same rows, same order); the render change is conditional on a milestone being falsy so the active-only path (always has a milestone) is untouched. Diff the 3 copies before re-pinning.
Code lives in: `add-method/tooling/add.py` (+ its two mirror copies)
Constraints: do NOT change any test or the contract; stdlib only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 2054 OK (2048→2054, +6 test_mine_all_lens); check 442/0; audit clean (92 tasks)
- [x] coverage did not decrease — 6 new tests cover scope_all (non-active surfaced, plain-mine still excludes), loose render, done/unowned exclusion, json shape, pin
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; NO existing test changed (the unchanged test_my_work_lens is the byte-identity oracle and stayed green); the only test edit was to the NEW test_mine_all_lens fixture: `_task(slug, None)` now pokes milestone=None so it ACTUALLY creates a loose task — the assertion (`[loose]` present) was untouched; this corrected the Given, it did not weaken a Then
- [x] the green was EARNED, not gamed — the 4 --all tests were RED for the right reason ("unrecognized arguments: --all") before, GREEN after; the loose-render fixture bug surfaced a real gap (new-task auto-links to the active milestone) and was fixed to test the real path, not asserted away; LIVE `mine` vs `mine --all` show the correct "active" vs "all milestones" headers
- [x] concurrency / timing of the risky operation is safe — read-only lens; `_my_work` pure/total (no mutation, no raise); single-process CLI
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only, no new import; reads state.json only
- [x] layering & dependencies follow CONVENTIONS.md — `scope_all` param on the existing `_my_work`; `--all` arm on the existing `cmd_mine`; reuses `identity._actor_matches`/`_task_done`/`_fmt_actor`; no new surface
- [x] a person reviewed and approved the change — Tin Dang (auto-mode standing authorization) + the §3 freeze approval ("Freeze as-is" — --all spans all milestones + loose)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `mine --all` lists a mine-but-NON-active task (in a milestone not in the active SET) + header reads "across all milestones" — confirmed: test_all_surfaces_nonactive green
- [x] plain `mine` (no flag) STILL excludes that non-active task + header reads "across active milestones" — confirmed: test_plain_mine_still_excludes_nonactive + the unchanged test_my_work_lens suite green (byte-identity oracle)
- [x] `mine --all` lists a loose (milestone-less) owned task rendered `[loose]`, never `[None]` — confirmed: test_all_includes_loose_renders_loose green (after the fixture fix that actually creates a loose task)
- [x] `mine --all` still excludes done + unowned tasks (widens milestone scope only) — confirmed: test_all_excludes_done_and_unowned green
- [x] `mine --all --json` carries the non-active task with shape {slug, milestone, phase, role} (milestone null for loose) — confirmed: test_all_json_includes_nonactive green
- [x] 3 add.py copies byte-identical + `ENGINE_MD5` re-pinned — confirmed: all three == `d1c1b68702543c38c9e97bde71e39ba6` == engine_pin.ENGINE_MD5

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `cmd_mine` reads `getattr(args,"all",False)` → `_my_work(state, me, scope_all=...)`; the `--all` subparser flag feeds it; the `[loose]` render branch fires on a falsy milestone; verified via the live `mine --all` run (correct "all milestones" header)
- [x] DEAD-CODE (code) — no orphan symbol; the `scope_all=True` arm is reached by `--all` (test_all_surfaces_nonactive), the loose render branch by a milestone-less task (test_all_includes_loose_renders_loose)
- [ ] SEMANTIC (prose / non-code) — N/A (code change; help text + headers passed the ubiquitous-language lint in the full suite)

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang (auto-mode standing authorization) · date: 2026-06-26

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): is `mine --all` actually used over plain `mine`? if so, the active-only default may be too narrow for how people track their backlog — a signal to reconsider which is the default.

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · carried] `mine --all` could grow a `--milestone <slug>` narrowing or a `--stage`/phase filter for a large all-milestone backlog — deferred as scope creep (evidence: this task scoped the boolean widening only) [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [TDD · folded] a fixture that calls `new-task` with no `--milestone` does NOT make a loose task — new-task auto-links to the active milestone; a "loose" fixture must poke milestone=None explicitly. The red test passed its assertion against the WRONG arrange until the build surfaced it (evidence: test_all_includes_loose_renders_loose showed `[m1]` not `[loose]`) [folded foundation-version 55]
