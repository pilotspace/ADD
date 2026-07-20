# TASK: First-call ergonomics: true post-transition footers + idempotent retries + kickoff command hand-off

slug: first-call-ergonomics · created: 2026-07-09 · stage: mvp
milestone: risk-proportional-ceremony
autonomy: auto
phase: done

> One file = one task — fill top-to-bottom; the phase marker above is the single source of truth (`add.py phase`); unclear phase → its book chapter.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): add-method/tooling/add.py:`_next_command(phase)` (~6002, pure composer keyed on phase ONLY — the defect: `contract` has two states) · `_next_footer(root, state)` (~6021, Arm A reads task phase, prints post-mutation) · `cmd_freeze` (~946; success tail prints the footer while phase is STILL `contract` → footer says `freeze --by <name>` again) · `already_frozen` die (~968) · `cmd_lock`/`already_locked` die (~2151) · advance at-final-phase dies (~1221 `--fill` path, ~1276 main path) · `cmd_init` (~556; stdout tail ends without a kickoff hand-off)
Context (working folder): live benchmark transcripts `scratchpad/mr-lever-sonnet/rep{1,2}/add/wm1/transcript.jsonl` (2026-07-09, pinned sonnet) — the evidence: post-freeze footer literally printed `next: add.py freeze --by <name>`; best run made 7 `--help` calls + hit `already_locked`/`skip_not_allowed`; worst run retried `freeze`→`already_frozen`
Honors (patterns / conventions): footer is PURE render computed after save_state, fail-soft, never aborts a saved verb (docstring contract of `_next_footer`) · `_next_command` is the ONE composer for status/guide/footer (status-guide-fold invariant — do NOT add a parallel emitter) · backward-compatible CLI (milestone shared decision) · error codes are snake_case prefixes (`already_frozen: …`)
Seams consulted: .add/SEAMS.md#scope-token-grammar (scope declaration parsing — §5 line below) · engine 3-tree byte parity (canonical → `prepare_bundle.py` → bundled; manual cp → .add dogfood; engine_pin.py re-pin)
Anchors the contract cites: `_next_command` · `_next_footer` · `cmd_freeze` · `cmd_lock` · `cmd_init` · `cmd_advance` at-final-phase guards · tests in add-method/tooling/test_next_footer_engine.py
Issues/Risks (→ feed §1): (1) `_next_command` is deliberately PURE-by-phase; giving it state risks breaking its 3 call surfaces — extend the SIGNATURE additively (default arg) so existing callers stay valid. (2) idempotent no-op must NOT weaken the floor: `freeze` on an unfrozen-but-undrafted §3 must still die; ONLY the exact already-in-target-state retry becomes exit-0. (3) `--force` re-lock path must keep working. (4) banned-slang guard scans string literals — keep "fold"/"blast radius"/"least-sure" out of new strings. (5) any add.py line growth drifts SEAMS.md line pins (known, re-pin routine).
Related intent: milestone risk-proportional-ceremony LOOP-2 defects (b)+(c) — MILESTONE.md "LOOP round 2" block; goal = mean add.py calls ≤12 on pinned-sonnet WM1 (re-anchored exit criterion)
Ground SHA: 4d0c52e (branch feat/add-bench-scaffold) — line refs "as of" this commit

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: first-call ergonomics — a headless agent's FIRST attempt at each engine verb succeeds or is redirected in the same stdout, never via a repair loop
Framings weighed: extend-the-one-composer + no-op-the-exact-retry (chosen — smallest diff, keeps the status/guide/footer unifier invariant) · new `add.py next` subcommand (rejected: a 4th surface to drift + a new subcommand ripples into min_pillar LIFECYCLE + slang-guard spans) · rewrite errors as warnings globally (rejected: weakens floor guards that must stay loud)
Must:
<must>
  - M1 post-freeze next-command is TRUE: when the active task's phase is `contract` AND §3 is FROZEN, `_next_command`/status/guide/footer emit `add.py advance` (cross into tests) — never `freeze --by` again; `cmd_freeze`'s own success footer shows it
  - M2 exact-state retries are exit-0 no-ops that restate state + the true next command: `freeze` on an already-FROZEN §3 · `lock` on already-locked setup (without --force) · `advance` on a task already at `done`
  - M3 `cmd_init` success stdout ends with the kickoff hand-off: the exact next commands with their required flags (new-milestone --title/--goal → new-task --title --milestone → advance --to contract), so first-use `--help` reads are unnecessary
  - M4 all three engine trees stay byte-identical and ENGINE_MD5 re-pinned; existing ~3k suite stays green (backward-compatible CLI)
</must>
Reject:
<reject>
  - freeze on a §3 that is not drafted / unflagged -> "contract_not_drafted" / "unflagged_freeze" (unchanged — floor guards stay loud errors)
  - a no-op retry that MUTATES state (re-stamps freeze version, re-locks, bumps phase) -> forbidden; no-op means zero state change
  - emitting `advance --to` past the tests stop-point from any new hand-off text -> "advance_to_stops_at_tests" semantics stay intact
</reject>
After:
<after>
  - a duplicated/retried freeze · lock · advance-at-done exits 0, prints `already …` + `next: <true command>`, and state.json is byte-identical to before the retry
  - after `freeze` succeeds, every surface (freeze footer, status, guide) names `advance` as next
  - `init` stdout alone is enough to reach `advance --to contract` with zero `--help` calls
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ exit-0 on already_frozen retry does not mask a REAL misuse (an agent trying to re-freeze a CHANGED shape) — lowest confidence because freeze stamps rather than diffs §3 content; if wrong: a silently divergent contract. Mitigation: the no-op line restates the frozen version + `re-freeze only via change request` so intent-to-change is still redirected.
  - [x] dependents on the literal `already_frozen`/`already_locked` error behavior — censused (grep 2026-07-09): tests `test_freeze_command.py`/`test_setup_lock.py`/`test_brownfield_scan.py` assert them (updated legitimately in the TESTS phase, pre-freeze) + skill prose `adopt.md`/`phases/0-setup.md` name `already_locked` as a STATE not an exit code (doc-truth check at verify; SEMANTIC_INVENTORY.md pins the term census — update if the term's surface moves)
  - [x] `_next_footer` can see frozen-ness cheaply — yes: `cmd_freeze` already holds `raw3`/state; footer Arm A can re-read the TASK.md §3 marker via the existing `_contract_frozen` helper
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: post-freeze footer names advance   # M1
  Given an active task at phase contract whose §3 was just FROZEN by cmd_freeze
  When cmd_freeze prints its success footer (and status / guide are called after)
  Then all three surfaces emit "add.py advance" as the next command
  And none of them emits "freeze --by" again

Scenario: pre-freeze contract surfaces still teach freeze   # M1 guard
  Given an active task at phase contract whose §3 is DRAFT
  When status / guide / a footer render
  Then the next command is still "add.py freeze --by <name>"

Scenario: retried freeze is an exit-0 no-op   # M2
  Given a task whose §3 is already FROZEN @ v1
  When "add.py freeze --by X" runs again
  Then it exits 0, prints the frozen version + that a shape change needs a change request, and "next: add.py advance"
  And state.json and TASK.md are byte-identical to before the retry

Scenario: retried lock is an exit-0 no-op   # M2
  Given a project whose setup is already locked
  When "add.py lock" runs without --force
  Then it exits 0, restates locked + the true next command
  And state.json is unchanged and --force still re-locks

Scenario: advance at done is an exit-0 no-op   # M2
  Given the active task is at phase done
  When "add.py advance" runs (bare or --fill)
  Then it exits 0, states the task is done, and prints the Arm-B milestone next step
  And no phase or state field changes

Scenario: init hands off the kickoff sequence   # M3
  Given an empty directory
  When "add.py init --name X --stage mvp" completes
  Then its stdout tail lists the exact new-milestone / new-task / advance --to contract commands with required flags

Scenario: undrafted freeze still dies   # R1
  Given a task at contract whose §3 span is not drafted
  When "add.py freeze --by X" runs
  Then it exits non-zero with "contract_not_drafted"
  And no freeze stamp is written

Scenario: no-op never mutates   # R2
  Given any of the three retry cases above
  When the retried verb exits 0
  Then a byte-compare of .add/state.json (and the task file for freeze) before/after shows zero change
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
_next_command(phase: str, *, contract_frozen: bool = False) -> str      # ADDITIVE default arg — existing 3 call surfaces stay valid
  phase=="contract" and contract_frozen -> "add.py advance"             # M1: the post-freeze truth
  phase=="contract" and not frozen      -> "add.py freeze --by <name>"  # unchanged
  all other phases                      -> unchanged strings

CLI add.py freeze <slug>   (§3 already FROZEN, no shape change)
  exit 0 -> stdout: "already frozen @ <vN> — a shape change is a change request back to SPECIFY"
            + _next_footer line ("next: add.py advance …")
  state.json / TASK.md: ZERO bytes changed
CLI add.py freeze <slug>   (§3 not drafted / unflagged)
  exit != 0 -> stderr: "contract_not_drafted" | "unflagged_freeze"      # unchanged floor guards

CLI add.py lock            (already locked, no --force)
  exit 0 -> stdout: "already locked" + _next_footer line; state unchanged; --force path unchanged

CLI add.py advance [<slug>] [--fill …]   (task at done)
  exit 0 -> stdout: "task '<slug>' is done" + Arm-B footer; state unchanged

CLI add.py init … (success)
  stdout tail (after today's lines) -> "kickoff:" block: exact `add.py new-milestone <slug> --title "…" --goal "…"`,
  `add.py new-task <slug> --title "…" --milestone <ms>`, `add.py advance --to contract` — copy-pasteable, flags included

Schema: .add/state.json — READ-ONLY in every new no-op path; TASK.md §3 freeze marker read via existing _contract_frozen
```

Glossary deltas: none (reuses: freeze · lock · advance · footer — all existing GLOSSARY terms)
Least-sure flag surfaced at freeze: [spec] the exit-0 re-freeze no-op could soften a real re-freeze-intent signal (an agent meaning to freeze a CHANGED shape) — freeze stamps rather than diffs §3, so the engine cannot distinguish retry from re-intent; if wrong: a silently divergent contract. Mitigated in the contracted stdout itself: the no-op restates the frozen version AND redirects "a shape change is a change request back to SPECIFY"; the undrafted/unflagged paths stay hard errors. Human approved this trade at the freeze gate (option: keep-error was offered and declined).
Status: FROZEN @ v1 — approved by Tin Dang
Reported: <yes — the freeze report (banner/ARC/SHAPE) rendered before this froze | no>

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every §2 scenario = 1 test; new no-op paths 100% branch-covered
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_post_freeze_footer_names_advance: freeze a drafted §3 / capture cmd_freeze stdout + status + guide / assert all three contain "add.py advance" + none contain "freeze --by" · covers: M1
  - test_pre_freeze_contract_still_teaches_freeze: task at contract, §3 DRAFT / render status+guide+footer / assert "freeze --by <name>" · covers: M1 guard
  - test_refreeze_is_exit0_noop: freeze twice / assert 2nd exit 0, stdout has frozen version + "change request" + "next: add.py advance" / assert state.json + TASK.md bytes identical · covers: M2, R2
  - test_relock_is_exit0_noop: lock a locked setup w/o --force / assert exit 0 + state unchanged; then --force / assert re-lock still works · covers: M2, R2
  - test_advance_at_done_is_exit0_noop: gate PASS a task to done, advance again (bare + --fill) / assert exit 0 + "done" + footer + zero state change · covers: M2, R2
  - test_init_prints_kickoff_handoff: init in a tmpdir / assert stdout tail names new-milestone --title --goal, new-task --title --milestone, advance --to contract · covers: M3
  - test_undrafted_freeze_still_dies: freeze with undrafted §3 / assert non-zero + "contract_not_drafted" + no stamp · covers: R1
  - (existing suites) update pinned asserts in test_freeze_command.py / test_setup_lock.py / test_brownfield_scan.py that expect non-zero on the exact-retry cases — behavior change is THE feature, updated here in TESTS phase pre-freeze, never during build
</test_plan>

Tests live in: `add-method/tooling/test_first_call_ergonomics.py` (new, sibling of the engine per repo convention) · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `.add/tooling/engine_pin.py` `add-method/src/add_method/_bundled/tooling/engine_pin.py` `add-method/tooling/test_next_footer_engine.py` `add-method/tooling/test_freeze_command.py` `add-method/tooling/test_setup_lock.py` `add-method/tooling/test_brownfield_scan.py` `add-method/tooling/test_first_call_ergonomics.py` `add-method/tooling/SEMANTIC_INVENTORY.md`
Strategy (ordered batches): 1. add `contract_frozen` default arg to `_next_command`; thread it from `_next_footer` Arm A (read via `_contract_frozen` on the active task doc) so freeze-footer/status/guide all flip to `advance` post-freeze. 2. convert the three exact-retry dies (already_frozen · already_locked · advance-at-done ×2 sites) to exit-0 no-op prints + footer, zero writes. 3. append the `kickoff:` hand-off block to `cmd_init` success stdout. 4. red-first the new suite (test_first_call_ergonomics.py) + update the pinned-string asserts in the 3 existing test files. 5. sync twins (prepare_bundle + cp .add), git-restore bundled engine_pin, re-pin ENGINE_MD5, rm __pycache__, full suite to a file (grep Ran/OK — never trust `| tail` exit).
Approach (domain strategy): same DRY seam as status-guide-fold — extend the ONE composer rather than adding a surface; idempotency by early-return-print, never by widening a mutation path. methodology-engine-dev stance: deterministic, fail-loud where the floor guards, quiet where a retry is harmless.
Data strategy: no data-shape change; all new paths are READ-only over state.json/TASK.md (the §3 Schema line) — no-op means zero bytes written.
Pattern: extends `next-footer-engine` + the status-guide-fold unifier invariant (§0 Honors); error-code convention untouched for real errors.
Optimization stance: token-cost (turn-count) — kill the retry repair-turns + the 7 first-use `--help` reads; budget = LOOP-2 criterion, mean add.py calls ≤12 on pinned-sonnet WM1. ⚠ least-trusted facet: pinned-string churn in the 3 existing test suites — mitigated by red-first enumeration. correctness-first otherwise.

Persona (required): methodology-engine-dev
Spawn isolation (default): shared-tree, no spawn planned — single-file engine edit on the critical path; serialize local git (worktree-git-contention lesson)
Known-problem fixes: banned-slang guard scans string literals → keep "fold"/"blast radius"/"least-sure" out of new stdout text · `| tail` masks unittest exit → capture to file + grep `Ran/OK|FAILED` · prepare_bundle DELETES bundled engine_pin.py → git-restore then re-pin · transient `_bundled/__pycache__` flakes parity → rm before checks · SEAMS.md line pins drift on add.py growth → re-pin after build · tmp/ commit-msg name collisions → milestone-prefixed filename
Strategy actually used: as planned (M1 composer → M2 no-ops → M3 kickoff → red-first → 3-tree sync) with two deviations: (1) split the unknown-phase check from the done no-op in both advance sites so a corrupted state.json still dies loud (builder); (2) orchestrator post-review fix — when §3 is frozen the footer's why/driver halves flip WITH the command ("§3 frozen; cross into tests [you drive]"), killing a stale "[human gate]" that could stall a headless agent (found by live smoke of the builder's output).
Safety rule (feature-specific): a no-op path must be READ-only — any write in an exit-0 retry is a defect; floor guards (contract_not_drafted · unflagged_freeze · advance_to_stops_at_tests · gate/freeze human seams) keep non-zero exits
Code lives in: `add-method/tooling/add.py` (canonical; twins synced at build end)
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass   (full suite: Ran 3345 in 264.9s — OK, file-captured /tmp/fce-fullsuite.txt; targeted 47/47 OK)
- [x] coverage did not decrease   (7 new tests added; zero tests removed/weakened; every new engine path test-covered)
- [x] no test or contract was altered during build   (tests written in TESTS phase pre-crossing; build + orchestrator marker-fix touched engine code only; §3 untouched post-freeze)
- [x] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP)
- [x] concurrency / timing of the risky operation is safe   (advisor lens 2 — no-op paths read-only, no new lock window)
- [x] no exposed secrets, injection openings, or unexpected dependencies   (advisor lens 1 — stdlib only, no new parsing surface)
- [x] layering & dependencies follow CONVENTIONS.md   (advisor lens 3 — single-composer invariant held, existing accessors reused)
- [ ] a person reviewed and approved the change   (human backstop — spot-audit welcome; auto-gate below per autonomy: auto)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> OBSERVABLE outcomes a correct build must produce, derived from the §2 scenarios + §3 contract — evidence you can SEE, not test names.
- [x] a live dogfood smoke (`freeze` → footer says `advance`; re-`freeze` → exit 0 no-op; `lock` retry → exit 0; `advance` at done → exit 0; fresh-tmpdir `init` → kickoff block) — confirmed 2026-07-10 scratchpad smoke-fce: post-freeze footer `next: add.py advance — §3 frozen; cross into tests [you drive]`; re-freeze `already frozen @ v1 — a shape change is a change request back to SPECIFY` exit=0; status `next: add.py advance`; guide `then   : add.py advance`; init tail `kickoff:` block with all 3 commands
- [x] zero-write no-ops — confirmed by byte-compare asserts in test_first_call_ergonomics (state.json AND TASK.md before/after re-freeze; state.json for re-lock + advance-at-done bare AND `--fill /nonexistent/...` which also proves the payload is never read)
- [x] all 3 engine trees byte-identical + ENGINE_MD5 re-pinned — md5 `bbbb9a9f…` ×3 add.py; ENGINE_MD5 value equal in all 3 engine_pin.py (test_mirrors_and_pin green)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_task_contract_frozen` referenced at 3 sites (cmd_status ~2700 · cmd_guide ~2824 · _next_footer ~6100); `contract_frozen` kwarg consumed in `_next_command`'s contract branch — confirmed by grep + the M1 test hitting all 3 surfaces
- [x] DEAD-CODE (code) — no orphan: every added path (4 no-op returns, kickoff block, helper) is exercised by a test; diff reviewed hunk-by-hunk by orchestrator
- [x] SEMANTIC (prose / non-code) — new stdout strings read in full: no banned slang ("fold"/"blast radius"/"least-sure" absent from new string literals); error-code convention untouched for the paths that stay errors

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> Re-resolve every symbol §3 cites against the CURRENT tree (code moved since Ground SHA) — catch a stale anchor here, not later.
- [x] every symbol §3 CONTRACT cites still resolves in the current tree — `_next_command` (~6035) · `_task_contract_frozen` (new, ~6060) · `_next_footer` (~6070) · `cmd_freeze` (~972 no-op) · `cmd_lock` (~2170) · `cmd_init` kickoff (~636) · advance guards (~1230/~1293) — grep-confirmed post-build
- [x] anchors that moved since Ground SHA 4d0c52e: everything below cmd_init shifted +7 to +47 lines (this task's own additions); `_declared_scope` 5173→5206 → .add/SEAMS.md#scope-token-grammar re-pinned x13 (test_seams_doc green in the full run)

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under auto, record the earned-green refute-read (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). Audit-measured (`refute_unrecorded`), never blocked; a human spot-audit is the backstop.
Verdict: EARNED
By: self (orchestrator, independent of the add-build builder — a85b40ef) · adversarially checked: byte-compare asserts are real (both files, before/after) not md5-of-nothing; the `--fill /nonexistent/path` probe proves the done no-op never reads the payload; floor-guard test asserts the ABSENCE of a freeze stamp in state, not just the error string; pre-freeze surfaces asserted to STILL teach freeze (no over-flip); `--force` re-lock exercised, not just asserted locked; found + fixed one builder residue via live smoke (stale `[human gate]` marker post-freeze)

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Lenses run in order; a Security HARD-STOP ends the checklist (leave the rest blank). Binding for sensitivity: mechanical (advisor-gate-relax); advisory otherwise. Audit-measured (`advisor_verdict_unrecorded`), never blocked.
Advisor: self (orchestrator)
1. Security: CLEAR — no new input parsing (the version re.search runs on already-read §3 text), no new writes, no subprocess/network; exit-0 paths are strictly read-only; all floor guards (contract_not_drafted · unflagged_freeze · advance_to_stops_at_tests · gate seams) unchanged and test-asserted
2. Concurrency: CLEAR — no-op paths take no locks and write nothing, so no new TOCTOU window; --force lock path byte-unchanged
3. Architecture: CLEAR — single-composer invariant preserved (one additive kwarg, no parallel emitter); new helper `_task_contract_frozen` reuses existing `_raw_phase_bodies`/`_contract_frozen` accessors, fail-closed on unreadable TASK.md; footer keeps its fail-soft try/except envelope
Verdict: PASS
Residue: none
Binding: advisory — mechanical (CLI ergonomics; no data/security/architecture sensitivity)

### GATE RECORD
Reported: yes — gate report rendered to the user before recording (three-way evidence: full suite 3345 OK · 47 targeted OK · live smoke · trio md5 bbbb9a9f)
Outcome: PASS
Reviewed by: auto-gate (autonomy: auto — refute-read EARNED by orchestrator independent of builder a85b40ef, advisor 3-lens CLEAR/PASS, residue none, sensitivity mechanical, security floor untouched; human backstop box left open for spot-audit) · date: 2026-07-10

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency — the §5 Optimization stance budget is a monitor here, not just an intention>

### Decisions (ADR)
- [AI] specify — chose extend-the-one-composer + no-op-the-exact-retry; rejected new `add.py next` subcommand (rejected: a 4th surface to drift + a new subcommand ripples into min_pillar LIFECYCLE + slang-guard spans) · rewrite errors as warnings globally (rejected: weakens floor guards that must stay loud)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — approach: same DRY seam as status-guide-fold — extend the ONE composer rather than adding a surface; idempotency by early-return-print, never by widening a mutation path. methodology-engine-dev stance: deterministic, fail-loud where the floor guards, quiet where a retry is harmless.
- [AI] build — data strategy: no data-shape change; all new paths are READ-only over state.json/TASK.md (the §3 Schema line) — no-op means zero bytes written.
- [AI] build — pattern: extends `next-footer-engine` + the status-guide-fold unifier invariant (§0 Honors); error-code convention untouched for real errors.
- [AI] build — optimization stance: token-cost (turn-count) — kill the retry repair-turns + the 7 first-use `--help` reads; budget = LOOP-2 criterion, mean add.py calls ≤12 on pinned-sonnet WM1. ⚠ least-trusted facet: pinned-string churn in the 3 existing test suites — mitigated by red-first enumeration. correctness-first otherwise.
- [AI] build — strategy used: as planned (M1 composer → M2 no-ops → M3 kickoff → red-first → 3-tree sync) with two deviations: (1) split the unknown-phase check from the done no-op in both advance sites so a corrupted state.json still dies loud (builder); (2) orchestrator post-review fix — when §3 is frozen the footer's why/driver halves flip WITH the command ("§3 frozen; cross into tests [you drive]"), killing a stale "[human gate]" that could stall a headless agent (found by live smoke of the builder's output).
- [AI] verify — gate PASS (reviewed by auto-gate (autonomy: auto — refute-read EARNED by orchestrator independent of builder a85b40ef, advisor 3-lens CLEAR/PASS, residue none, sensitivity mechanical, security floor untouched; human backstop box left open for spot-audit))

### Spec delta
One line per forward change, tagged `[SPEC · open|seeded|dropped]` + evidence — each re-enters at Specify (`deltas.md`).
- [SPEC · open] `skip_not_allowed` fires once mid-advance then clears on bare retry — a 4th non-idempotent surface this task did not cover; worth the same restate-plus-next treatment (evidence: mr-lever-sonnet/rep1 transcript, advance → skip_not_allowed → advance → ok)

### Competency deltas
One lesson per line: `[DDD|SDD|UDD|TDD|ADD · open] the learning (evidence: …)` — see `deltas.md`.

