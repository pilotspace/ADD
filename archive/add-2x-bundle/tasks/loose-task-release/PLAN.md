# TASK: Release-attribute milestone-free done tasks as RELEASES.md loose items

slug: loose-task-release · created: 2026-06-25 · stage: mvp
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
- `add-method/tooling/add.py:_released_milestones` (6032) — reads `milestones:` rows from RELEASES.md (fail-open); MODEL for the parallel loose reader.
- `:_releasable` (6067) — closed-unreleased milestones; drives the cue + `release_data`.
- `:release_data` (6089) — the GATHER-never-JUDGE facts dict (releasable/changed/waivers/blockers/monitors + summary).
- `:_render_releases_row` (6238) — the append-only RELEASES.md row: `milestones:` / `waivers:` / `actor:` / `evidence:`. ADD a `loose tasks:` line here.
- `:cmd_release` (6254) — floor (incl. `release_no_closed_milestone` no-op guard, keyed off `_releasable`) → writes CHANGELOG + RELEASES via `_atomic_write_many` (all-or-nothing).
- status cue: `add.py:1982-1984` + `RELEASABLE_CUE` (49) — `→ releasable: N milestone(s)…`. ADD a SEPARATE loose-task cue line (leave the milestone cue + constant untouched).
- `:_task_done` (1159) — phase=="done" AND gate in (PASS, RISK-ACCEPTED). REUSE for loose eligibility.
- engine 3 trees + `engine_pin.py:ENGINE_MD5` (same mirror+re-pin discipline as the prior 2 engine tasks).
Context (working folder): RELEASES.md (project root, the attribution ledger) — fail-OPEN reads.
Honors (patterns / conventions): GATHER-never-JUDGE (release_data) · validate-before-write (floor before any write) · fail-open ledger reads · the engine RECORDS, the human ships.
Anchors the contract cites: `_released_loose_tasks` · `_releasable_loose_tasks` · `release_data["loose"]` · the `loose tasks:` RELEASES.md line · the loose cue line.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Loose-task release attribution — a done milestone-free task is a first-class releasable item, swept into a RELEASES.md `loose tasks:` row.
Framings weighed: a parallel "loose task" track mirroring the milestone track (chosen) · forcing every loose task into a synthetic micro-milestone (rejected — re-introduces the ceremony the standalone lane removed) · a separate LOOSE.md ledger (rejected — splits the single attribution source).
Must:
<must>
  - A "loose task" = a task with `milestone is None` AND `_task_done` (done + PASS/RISK-ACCEPTED) AND its slug not yet in any RELEASES.md `loose tasks:` row. (Milestone-free, NOT fast-restricted — a full standalone done task needs attribution too.)
  - `release_data` gains a `loose` record-set (`[{slug, title}]`) + a `summary["loose"]` count, GATHER-never-JUDGE.
  - `add.py release <v>` writes a `loose tasks: <slugs|none>` line into the new RELEASES.md row, attributing the loose bundle.
  - The no-op floor guard (`release_no_closed_milestone`) does NOT fire when loose tasks are releasable — a loose-only bundle (zero releasable milestones) can still cut.
  - An attributed loose task drops out of the releasable-loose set on the next read (`_released_loose_tasks` reader; fail-OPEN like the milestone reader).
  - `status` prints a SEPARATE loose-task cue line when ≥1 loose task is releasable (the milestone cue + its constant stay byte-unchanged).
</must>
Reject:
<reject>
  - (no NEW hard-reject code: the release floor is unchanged — `release_security_open` stays the un-forceable HARD-STOP; loose tasks never weaken it)
</reject>
After:
<after>
  - the new RELEASES.md row carries BOTH `milestones:` and `loose tasks:`; every attributed loose task is no longer releasable; the cut prints both counts.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ loose = milestone-free + done (NOT fast-restricted) — lowest confidence because the user said "fast tasks", but restricting to fast would orphan full standalone done tasks (incl. THIS task); if wrong: add an `AND t.get("fast")` filter (one clause).
  - [ ] a SEPARATE loose cue line (vs folding into the milestone cue) — chosen to keep the milestone cue constant untouched; if wrong, merge the counts and reword the constant.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: a done loose task is releasable and gets attributed
  Given a project with no releasable milestones but one milestone-free task done+PASS
  When I run `add.py release 0.1.0`
  Then the cut succeeds and the new RELEASES.md row carries `loose tasks: <slug>`
  And the milestone cue line + RELEASABLE_CUE constant are byte-unchanged

Scenario: an attributed loose task is no longer releasable
  Given a loose task already named in a RELEASES.md `loose tasks:` row
  When release_data is gathered
  Then that slug is absent from the `loose` record-set
  And re-running `release` reports it would be a no-op (nothing left to bundle)

Scenario: status shows a separate loose cue
  Given ≥1 milestone-free done+PASS task not yet released
  When I run `add.py status`
  Then a separate `→ releasable: N loose task(s) …` line prints
  And the existing `→ releasable: M milestone(s) …` cue is unchanged

Scenario: a milestone-attached or not-done task is NOT loose
  Given a done task attached to a milestone, and a milestone-free task still in build
  When release_data is gathered
  Then neither appears in the `loose` record-set
  And the milestone track (`releasable`/`changed`) is unchanged

Scenario: security HARD-STOP still blocks a loose-only cut
  Given a releasable loose task AND an open HARD-STOP gate elsewhere
  When I run `add.py release 0.1.0` (even with --force)
  Then it refuses `release_security_open`
  And RELEASES.md + CHANGELOG.md are byte-unchanged (validate-before-write)
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
_released_loose_tasks(root) -> set[str]
    # union of every RELEASES.md "loose tasks:" row token; fail-OPEN (missing/unreadable -> set())
    # exact parallel of _released_milestones.

_releasable_loose_tasks(root, state) -> list[{slug, title}]
    # [ t for slug,t in state.tasks if t.milestone is None AND _task_done(t)
    #     AND slug not in _released_loose_tasks(root) ]  — title = t.get("title", slug)

release_data(root, state) gains:
    "loose":   [{slug, title}, …]          # from _releasable_loose_tasks
    "summary": { …, "loose": <count> }     # existing keys untouched (additive)

_render_releases_row(version, day, bundle, waiver_slugs, evidence, actor=None, loose=None) -> str
    # inserts ONE new line after "milestones:" :  "loose tasks: <slugs|none>"
    # loose=None or [] -> "none". Existing milestones:/waivers:/actor:/evidence: lines unchanged.

cmd_release(version):
    loose_bundle = _releasable_loose_tasks(root, state)
    # FLOOR: release_no_closed_milestone fires only if NOT _releasable AND NOT loose_bundle
    #   (a loose-only bundle can cut). release_security_open / tests_red / undisclosed_waiver UNCHANGED.
    # RECORD: pass loose_bundle to _render_releases_row; print "recorded N milestone(s) + M loose task(s)".

status cue (1982-1984):  AFTER the milestone cue, additively:
    _loose = _releasable_loose_tasks(root, state)
    if _loose: print(f"  → releasable: {len(_loose)} loose task(s) since last release")
    # the milestone cue + RELEASABLE_CUE constant are NOT touched.

RELEASES.md row shape (additive line):
    ## <v> — <day>
    milestones: <slugs|none>
    loose tasks: <slugs|none>          # NEW
    waivers: <slugs|none>
    actor: <actor>
    evidence: <text>
```

`Least-sure flag surfaced at freeze:` [spec] loose = milestone-free + done, NOT fast-restricted — RESOLVED at freeze: any milestone-free done task (fast OR full), so full standalone tasks (incl. this one) are attributable. Secondary [contract] separate cue line vs merged: kept separate (milestone cue constant untouched).
Status: FROZEN @ v1 — approved by Tin Dang (AskUserQuestion freeze, any milestone-free done task), 2026-06-25.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the 5 scenarios + the regression invariants (milestone track untouched).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_loose_task_attributed: init → milestone-free task done+PASS → `release 0.1.0` → RELEASES.md row has `loose tasks: <slug>`; milestone cue constant unchanged.
  - test_attributed_loose_drops_out: with a `loose tasks:` row present → release_data["loose"] excludes it; re-`release` → no-op refusal.
  - test_status_loose_cue: milestone-free done task → `status` prints a separate `releasable: N loose task(s)` line; milestone cue line unchanged.
  - test_not_loose: milestone-attached done task + milestone-free in-build task → neither in release_data["loose"]; `releasable`/`changed` unchanged.
  - test_security_blocks_loose_cut: releasable loose task + open HARD-STOP → `release` (even --force) refuses release_security_open; both ledgers byte-unchanged.
  - regression: existing release suites stay green (test_release_altitude / test_release_docs_accord / the forward-pin test_release_1_10_0 may assert the RELEASES.md row shape — update if they pin the exact line set).
</test_plan>

Tests live in: `add-method/tooling/test_loose_task_release.py` · MUST run red (no loose track yet) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` · `.add/tooling/add.py` · `add-method/src/add_method/_bundled/tooling/add.py` · `add-method/tooling/engine_pin.py` · `add-method/tooling/test_loose_task_release.py`
Strategy (ordered batches): 1. `_released_loose_tasks` + `_releasable_loose_tasks` readers. 2. `release_data` += loose record-set. 3. `_render_releases_row` += loose line (keyword-arg, default none → back-compat). 4. `cmd_release` floor + record. 5. status cue line. 6. mirror 3 trees + re-pin. 7. reconcile any release-suite that pins the row shape (declare it in §5 if so).
Safety rule (feature-specific): validate-before-write — every floor check BEFORE any ledger write; `_render_releases_row`'s new param defaults to none so existing callers/rows stay byte-identical.
Code lives in: `add-method/tooling/` (+ mirrored trees)
Constraints: do NOT change any test (except a row-shape pin that legitimately must learn the new line) or the contract; allow-list packages only; the milestone track + `release_security_open` floor stay byte-behavior-unchanged.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite **1761/0** (+5 new); dogfood `check` 390/0 (15 warns, all pre-existing/orphan-info), `audit` clean 77.
- [x] coverage did not decrease — 5 new behavioral tests added; none removed/weakened.
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; `test_loose_task_release.py` written at the tests phase (red), unchanged through build; no existing test edited (no row-shape pin existed to update).
- [x] the green was EARNED, not gamed — refute-read: tests drive real CLI flows (init/lock/new-task/gate/release/status) and assert OBSERVABLE artifacts (RELEASES.md `loose tasks:` row, `release_data["loose"]`, status text), not internals; no vacuous asserts; the security-floor test is a genuine regression guard that already held.
- [x] concurrency / timing of the risky operation is safe — release writes both ledgers via the existing `_atomic_write_many` (all-or-nothing); validate-before-write unchanged; no new IO path.
- [x] no exposed secrets, injection openings, or unexpected dependencies — pure stdlib (re/dict comprehension); no new deps; no user-controlled data reaches a sink.
- [x] layering & dependencies follow CONVENTIONS.md — `_releasable_loose_tasks` mirrors `_releasable`; `_released_loose_tasks` mirrors `_released_milestones` (fail-OPEN); GATHER-never-JUDGE preserved in `release_data`.
- [x] a person reviewed and approved the change — Tin Dang froze the contract (any milestone-free done task); auto-gated on complete evidence (autonomy: auto).

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `add.py release` on a milestone-free done task writes `loose tasks: <slug>` into RELEASES.md — confirmed by test_loose_task_attributed reading the cut row
- [x] `add.py status` shows a `releasable: N loose task(s)` line when a loose task is unreleased — confirmed live on THIS repo: `→ releasable: 17 loose task(s) since last release` (dogfooded on its own historical standalone tasks)
- [x] an attributed loose task is absent from `release_data["loose"]` on the next read — confirmed by test_attributed_loose_drops_out + the no-op refusal on re-cut
- [x] the milestone track + `release_security_open` floor are byte-behavior-unchanged — confirmed: security check is the FIRST floor gate (precedes the no-op guard), un-forceable even for a loose-only cut (test_security_blocks_loose_only_cut); all pre-existing release suites green

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_released_loose_tasks` ← `_releasable_loose_tasks` ← `release_data` + `cmd_release` (floor + record line) + the status cue; all four call sites confirmed by grep + a green suite that exercises each path.
- [x] DEAD-CODE (code) — no orphan: every new symbol has a live caller; `_render_releases_row`'s `loose=` kwarg is passed by `cmd_release`.
- [x] SEMANTIC (prose / non-code) — read the floor ordering in cmd_release (6316-6326): security blocker reject precedes the relaxed no-op guard; the relaxation can only ENABLE a cut that has real work, never bypass a HARD-STOP.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang (auto-gate on evidence, autonomy: auto) · date: 2026-06-25
OBSERVE: [SPEC · open] a FULL standalone task still draws the `task '<x>' is outside a milestone` WARN at `check` (only `--fast` standalones soft-INFO) — now that loose-task-release blesses ANY milestone-free done task, the check tier could treat a done full standalone as INFO too (evidence: loose-task-release itself WARNs at its own gate). [ADD · open] `release-report` does not yet render the `loose` record-set (out of this contract's scope) — a follow-up could surface loose tasks in the dashboard for discoverability.

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): a release that should attribute loose work but writes `loose tasks: none` · an attributed loose task that re-appears in the cue (drop-out regression).

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
