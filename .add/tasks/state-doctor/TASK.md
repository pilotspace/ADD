# TASK: add.py doctor — validate state integrity + referential consistency

slug: state-doctor · created: 2026-06-22 · stage: mvp · risk: high
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
- `add-method/tooling/add.py` (+ 2 mirror copies) — ADD a read-only `doctor` diagnostic:
  - NEW `_doctor_findings(root) -> list[str]` (~near cmd_check / the load helpers) — read state.json's RAW text (NOT via the dying load_state, so doctor REPORTS instead of aborting); collect findings: (1) file missing/unreadable → one finding; (2) `_CONFLICT_MARKER_RE` match → "unresolved git merge markers" finding (+ stop — can't parse); (3) unparseable JSON → finding (+ stop); (4) on a parseable state (after `_migrate_state`), REFERENTIAL checks — every `active_milestones[*]` ∈ milestones · every `active_tasks[ms]` ∈ tasks (and that task's `milestone` == ms) · every task's `milestone` (when not None) ∈ milestones. Each finding is a one-line problem + fix. PURE: reads only, returns the list.
  - NEW `cmd_doctor(args)` — print `doctor: PASS — …` and exit 0 when findings is empty; else print `doctor: N problem(s):` + each `✗ <problem>` / `fix: <fix>` to STDOUT and exit non-zero. NEVER mutates state (no save_state).
  - NEW `doctor` subparser (~5433, beside `whoami`/`assign`) — no args; `set_defaults(func=cmd_doctor)`.
- `add-method/tooling/test_min_pillar.py` LIFECYCLE — add `["doctor"]` (new read-only subcommand census co-update; reads state, never docs/).
- `engine_pin.py:ENGINE_MD5` — re-pin after this engine edit (same commit).

Context (working folder):
- task-1 (`merge-guard`) added `_CONFLICT_MARKER_RE` + `_state_text_or_die` (the LOAD-path guard that fails fast). doctor is the PROACTIVE counterpart the guard's message points at ("run `add.py doctor` to verify") — it REPORTS every problem instead of dying at the first, so a user post-merge sees the full picture. It REUSES `_CONFLICT_MARKER_RE` but reads independently (must not die at load).
- the multi-active schema (M1) is what doctor validates referentially: `active_milestones` (SET) · `active_tasks` (per-ms map) · each task's `milestone`. `_migrate_state` normalizes a legacy state first so doctor judges the canonical shape.

Honors (patterns / conventions):
- detect, never auto-resolve (the milestone's standing rule) — doctor REPORTS + guides; it NEVER repairs/mutates a diverged state. Read-only.
- fail-loud + actionable (design-for-failure) — each finding carries a concrete fix; a healthy state says PASS plainly.
- additive-cue convention — doctor is a NEW command; no existing output/precedent changes.
- engine-edit discipline — 3-tree byte-identity + same-commit ENGINE_MD5 re-pin; new subcommand → `test_min_pillar` LIFECYCLE census co-update.

Anchors the contract cites: `_doctor_findings(root)` (the read-only check list) · `cmd_doctor` (PASS exit 0 / problems exit non-zero, stdout report) · the `doctor` subparser · the referential rules (active_milestones→milestones · active_tasks→tasks+milestone · task.milestone→milestones) · reuse of `_CONFLICT_MARKER_RE`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: a read-only `add.py doctor` that proactively validates state.json integrity + referential consistency and REPORTS each problem (with a fix) or PASS — the proactive counterpart to merge-guard's load-time guard, mutating nothing.
Framings weighed: doctor reports ALL findings + exits non-zero on any (chosen — a post-merge user wants the full picture in one run, not fail-fast-at-first) · reuse the dying load_state (rejected — it aborts at the first conflict/parse error, so doctor could never REPORT a conflict, only crash on it) · doctor auto-REPAIRS a diverged state (rejected — the milestone's standing rule is detect-never-auto-resolve; the human reconciles).
Must:
<must>
  - `_doctor_findings(root)` returns a list of problem strings (each problem + its fix), reading state.json's RAW text directly (never through the dying load_state), so a conflicted/corrupt state is REPORTED, not aborted on.
  - it reports, in order, the FIRST blocking class then stops (can't go deeper): file missing/unreadable → one finding; else conflict markers (`_CONFLICT_MARKER_RE`) → one finding; else unparseable JSON → one finding.
  - on a PARSEABLE state (after `_migrate_state`), it runs REFERENTIAL checks and reports EACH violation: an `active_milestones` entry with no milestone record · an `active_tasks[ms]` task with no task record (or whose `milestone` != ms) · a task whose `milestone` (non-None) has no milestone record.
  - `cmd_doctor` prints `doctor: PASS — …` and exits 0 when there are no findings; otherwise prints `doctor: N problem(s):` + each `✗ <problem>` / `fix: <fix>` to STDOUT and exits NON-ZERO.
  - doctor NEVER writes state (no save_state) — a run leaves state.json byte-identical. New `doctor` subparser; `test_min_pillar` LIFECYCLE census co-update. All 3 add.py copies byte-identical + `ENGINE_MD5` re-pinned same commit.
</must>
Reject:
<reject>
  - doctor itself has no input to reject; it REPORTS findings. A problem found -> non-zero exit with the report (not an error_code _die — the report IS the output). A healthy state -> exit 0.
</reject>
After:
<after>
  - `add.py doctor` on a healthy project prints PASS + exits 0; on a conflicted/corrupt/inconsistent state it prints each specific problem + fix + exits non-zero; in all cases state.json is unchanged; the prior suite is green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ The referential check set (active_milestones→milestones · active_tasks→tasks+milestone-match · task.milestone→milestones) is the RIGHT integrity surface for an MVP doctor — lowest confidence because there are more invariants one COULD check (owner/assignee dict shape, gate values, phase ∈ PHASES, archived consistency) and I'm scoping to the cross-reference ones a bad MERGE most plausibly breaks. If wrong (a real-world merge corrupts a field doctor doesn't check): add that check — `_doctor_findings` is an append-only list, so a new rule is one block, no contract change to the command surface.
  - [ ] reporting ALL referential findings (not stopping at the first) is right — confirmed: a merge can break several refs at once; the user wants them all.
  - [ ] doctor exits NON-ZERO on findings (so CI / a wrapper can gate on it) — confirmed: a silent exit-0-with-warnings would let a broken state pass a scripted check.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: doctor passes a healthy state
  Given a valid project with consistent state.json
  When `add.py doctor`
  Then it prints "doctor: PASS" and exits 0
  And state.json is byte-identical (read-only)

Scenario: doctor reports a conflicted state
  Given state.json contains git conflict markers
  When `add.py doctor`
  Then it prints a problem naming "git merge markers" + a fix and exits non-zero
  And state.json is unchanged

Scenario: doctor reports unparseable JSON
  Given state.json is invalid JSON with no conflict markers
  When `add.py doctor`
  Then it prints a problem naming invalid JSON + a fix and exits non-zero

Scenario: doctor reports a dangling active milestone
  Given state.active_milestones lists "ghost" but milestones has no "ghost"
  When `add.py doctor`
  Then it prints a problem naming active milestone "ghost" + a fix and exits non-zero
  And state.json is unchanged

Scenario: doctor reports a task pointing at a missing milestone
  Given a task "t" whose milestone is "gone" but milestones has no "gone"
  When `add.py doctor`
  Then it prints a problem naming task "t" -> milestone "gone" + a fix and exits non-zero

Scenario: doctor reports an active task with no task record
  Given state.active_tasks maps a live milestone to "phantom" but tasks has no "phantom"
  When `add.py doctor`
  Then it prints a problem naming active task "phantom" + a fix and exits non-zero
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
_doctor_findings(root: Path) -> list[str]   # each item = "<problem> — fix: <fix>"
  read state.json RAW (own try/except, never via dying load_state):
    OSError                     -> ["state.json missing/unreadable — fix: restore from git/backup"]   (stop)
    _CONFLICT_MARKER_RE.search  -> ["unresolved git merge markers — fix: resolve <<<</====/>>>> or git checkout --ours/--theirs"]   (stop)
    JSONDecodeError             -> ["state.json is not valid JSON — fix: restore from git/backup"]   (stop)
  else state = _migrate_state(parsed); referential (append EACH):
    am in active_milestones, am not in milestones      -> "active milestone '<am>' has no record — fix: deactivate or recreate"
    (ms,t) in active_tasks, t and t not in tasks        -> "active task '<t>' (milestone '<ms>') has no record — fix: use a real task or clear"
    (ms,t) in active_tasks, t in tasks, tasks[t].milestone != ms -> "active task '<t>' is mislabeled under '<ms>' — fix: re-use it under its own milestone"
    slug,task in tasks, task.milestone not None and not in milestones -> "task '<slug>' references missing milestone '<m>' — fix: set-milestone to a real one or none"

cmd_doctor(args):
  root = find_root() or _die("no_project")
  f = _doctor_findings(root)
  f empty -> print("doctor: PASS — state.json is healthy (parseable · conflict-free · references intact)"); exit 0
  else    -> print(f"doctor: {len(f)} problem(s):"); for x in f: print(f"  ✗ {x}"); raise SystemExit(1)

doctor subparser: no args -> set_defaults(func=cmd_doctor)

Schema: READ-ONLY — no state write, no schema change, no new state key. New `doctor` command
  + `_doctor_findings` helper. Reuses `_CONFLICT_MARKER_RE` (merge-guard) + `_migrate_state`.
```

Status: FROZEN @ v1 — approved by Tin Dang (auto-mode standing authorization) · 2026-06-22

Least-sure flag surfaced at freeze:
- [spec] the referential check SET (active_milestones→milestones · active_tasks→tasks+milestone-match · task.milestone→milestones) as the MVP integrity surface — could miss an invariant a real merge breaks (owner/assignee shape, gate values, phase∈PHASES, archived consistency). Chosen the cross-reference checks a bad merge most plausibly breaks; `_doctor_findings` is an append-only list, so adding a rule later is one block with no command-surface change. Cost if wrong: a corrupt field doctor doesn't yet check passes — caught by adding the rule (cheap), not a re-freeze.
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
  - test_doctor_passes_healthy: valid project; `doctor` prints "doctor: PASS", exit 0; state bytes unchanged
  - test_doctor_reports_conflict: markers in state.json; `doctor` names "merge markers", exit !=0; state unchanged
  - test_doctor_reports_bad_json: "{bad" (no markers); `doctor` names invalid JSON, exit !=0
  - test_doctor_reports_dangling_active_milestone: active_milestones=["ghost"], no record; `doctor` names "ghost", exit !=0; state unchanged
  - test_doctor_reports_task_missing_milestone: task t.milestone="gone", no record; `doctor` names t -> "gone", exit !=0
  - test_doctor_reports_active_task_no_record: active_tasks={m:"phantom"}, no task; `doctor` names "phantom", exit !=0
  - test_three_trees_byte_identical_and_pinned: md5(3 copies)==1 and ==ENGINE_MD5
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
Tests in: `add-method/tooling/test_state_doctor.py`
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_min_pillar.py` `add-method/tooling/test_state_doctor.py`
Strategy (ordered batches): 1. write `_doctor_findings(root)` + `cmd_doctor(args)` + the `doctor` subparser in the canonical add.py. 2. add `["doctor"]` to test_min_pillar LIFECYCLE (census). 3. mirror to the other 2 copies (`cp`) + re-pin ENGINE_MD5. 4. run the red suite green.
Safety rule (feature-specific): doctor is READ-ONLY — it NEVER calls save_state; a run leaves state.json byte-identical (asserted in the healthy + conflict + dangling tests). `_doctor_findings` reads RAW (own try/except), never via the dying load_state.
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

- [x] all tests pass — `test_state_doctor` 9/9 green; full tooling suite 1496 green (was 1494; +2 new)
- [x] coverage did not decrease — net +2 tests (mislabeled-active-task rule 3 + type-corrupt robustness); no test removed
- [x] no test or contract was altered during build — §3 frozen unchanged; test edits were ADDITIONS + one assert tightened (`"t"`→`"'t'"`), never a weakening; re-crossed tests→build to re-anchor the snapshots
- [x] the green was EARNED, not gamed — independent python-expert refute-read: verdict MERGE-WITH-NITS, no HARD-STOP, no stub/overfit; its two real nits (a robustness crash path + a vacuous slug assert) were FIXED, not waived
- [x] concurrency / timing — n/a: doctor is a single-shot READ; it opens state.json once, never writes (no save_state on any path), so there is no race it can lose
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only (`re`/`json`, already imported); no shell, no eval, no new import
- [x] layering & dependencies follow CONVENTIONS.md — `_doctor_findings` sits beside the load helpers, reuses `_CONFLICT_MARKER_RE` + `_migrate_state`; `cmd_doctor` mirrors the read-only `cmd_check` shape; subparser registered beside `check`
- [x] a person reviewed and approved the change — auto-mode standing authorization (risk:high → conservative), independent subagent review on record

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] a healthy project prints `doctor: PASS — …` and exits 0 — confirmed by live run on this repo: "doctor: PASS — state.json is healthy (parseable · conflict-free · references intact)", exit=0
- [x] a conflicted state names the git merge markers + a fix and exits non-zero — confirmed by a temp-copy run: "✗ state.json has unresolved git merge markers — fix: resolve … (or git checkout --ours/--theirs)", exit=1
- [x] state.json is byte-identical after any run — confirmed by the read-only asserts in the healthy/conflict/dangling tests + no save_state call path
- [x] a type-corrupt-but-parseable state is REPORTED, never crashes — confirmed by test_doctor_reports_not_aborts_on_type_corrupt_state (no Traceback; the milestone's "guides instead of crashing" promise)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `cmd_doctor` is wired via the `doctor` subparser `set_defaults(func=cmd_doctor)`; `_doctor_findings` is called by `cmd_doctor`; `doctor` is exercised by the LIFECYCLE census in test_min_pillar — all referenced
- [x] DEAD-CODE (code) — no orphaned symbol; both new functions are on the live call path; no leftover scaffolding
- [x] SEMANTIC — n/a (code task; WIRING path applies)

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang (auto-mode standing authorization) · date: 2026-06-22

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): doctor-exit-nonzero rate post-merge · which finding class fires most (conflict vs referential) · any real-world corrupt field that doctor reports PASS on (a missed invariant)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · carried] widen doctor's referential set as merges reveal new break surfaces — owner/assignee dict shape, gate ∈ {PASS,RISK-ACCEPTED,HARD-STOP}, phase ∈ PHASES, archived consistency (evidence: §1 ⚠ flagged the MVP set covers only cross-reference invariants; `_doctor_findings` is an append-only list so each new rule is one block, no command-surface change) [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]
- [SPEC · carried] a `doctor --json` machine surface for CI gating on state health (evidence: §1 confirmed non-zero-exit-on-findings is for scripted gates; a structured `{problems:[…]}` would let a CI wrapper read each finding, mirroring `check --json`) [carried: deferred to backlog 2026-06-27 (delta-drain) — archived-task delta, not now-actionable; retrievable via 'add.py deltas --carried', reopen/seed via 'new-task --from-delta' when scheduled]

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [ADD · folded] a "REPORTS instead of aborts" diagnostic must be tested against TYPE-corrupt (not just parse-corrupt) state — the refute-read found an AttributeError path the 6 contracted scenarios missed; the design-for-failure promise only holds with an explicit type-robustness scenario (evidence: test_doctor_reports_not_aborts_on_type_corrupt_state added post-review) [folded foundation-version 44]
- [TDD · folded] a substring assert on a 1-char slug (`assertIn("t", out)`) is vacuous — incidental letters in the PASS line satisfy it; assert the QUOTED form (`"'t'"`) so the test actually pins provenance (evidence: refute-read Finding 2, tightened in this build) [folded foundation-version 44]
