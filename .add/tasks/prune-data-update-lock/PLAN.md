# TASK: Prune-Data / Update-Global Lock Race

slug: prune-data-update-lock · created: 2026-07-03 · stage: mvp
milestone: (none)
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): `add-method/src/add_method/_installer.py:_prune_data`(~L899-918)/`prune_data`(~L920-942) and `add-method/bin/cli.js:pruneData`(~L1285-1301)/`cmdPruneData`(~L1305-1321) — both call `shutil.rmtree`/`fs.rmSync` on `<home>/data/<key>` with ZERO lock held today
Context (working folder): `update --global`'s own reconcile loop WRITES into that SAME `<home>/data/<key>` directory — `_installer.py:update` L1966-1967 (`_persist_data(home, np)` refreshing an existing snapshot for every still-registered, still-existing project) / `cli.js` L1717 (`persistData(home, np)`) — all while HOLDING `_update_lock`/`acquireUpdateLock`. `prune-data` never acquires that lock.
Honors (patterns / conventions): reuse the EXISTING, already-proven `_update_lock`/`acquireUpdateLock` primitive (reclaim-ticket-race/global-lock-followups) — mirrors `project-scope-install-lock`'s own precedent of wrapping an existing call site in an existing proven lock at `autonomy: auto`, not inventing a new one
Seams consulted: none cited
Anchors the contract cites: `_prune_data`/`pruneData`'s call site inside `prune_data`/`cmdPruneData`; `_update_lock(home, *, timeout=None, env=None)` / `acquireUpdateLock(home, {timeout}, env)`'s existing signature
Issues/Risks (→ feed §1): (1) if `update --global`'s reconcile loop ever transiently drops a still-live project from the registry (e.g. self-healing a bad entry) while `prune-data` concurrently reads that shrunk registry, `prune-data` could misclassify a live project's snapshot as an orphan and remove it while `update --global` is mid-refreshing it — the exact cross-command race this task exists to close. (2) two concurrent `prune-data --force` runs are already largely idempotent (`rmSync`/`rmtree` tolerate an already-removed target) but not officially serialized — no data-loss bug found there, only a possible spurious `registry_corrupt` under a genuinely mid-write registry read, already fail-closed. (3) the fix must reuse the EXACT existing lock — no new file, no new threshold — matching `project-scope-install-lock`'s low-risk precedent.
Related intent: seeded from global-data-restore spec-delta — named as belonging to the sibling task `global-update-harden` at the time; still unaddressed after global-lock-followups's own hardening this session, which explicitly scoped itself to `update --global` + `install --global` only, never `prune-data` [← global-data-restore]
Ground SHA: `1ef7132`

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: serialize `prune-data` against `update --global` (and, incidentally, a second concurrent `prune-data`) by acquiring the SAME existing home lock (`_update_lock`/`acquireUpdateLock`) around prune-data's registry-read + orphan-computation + removal critical section — reuses the proven primitive, invents nothing new (from global-data-restore spec-delta)
Framings weighed: reuse the existing `_update_lock`/`acquireUpdateLock` around prune-data's critical section (chosen — the exact race this task closes is prune-data vs update --global; both must hold the SAME lock to mutually exclude) · a NEW, separate prune-data-only lock file — rejected, would serialize two prune-data runs against each other but do NOTHING to prevent the actual update-global-vs-prune-data race this task exists to close · an optimistic "snapshot the registry, retry-if-changed" read — rejected, more complex than reusing an already-tested mutual-exclusion primitive for a low-frequency admin command where a brief fail-fast is acceptable
Must:
<must>
  - prune-data's registry-read + orphan-computation + removal critical section holds the SAME home lock (`_update_lock`/`acquireUpdateLock`) `update --global` already holds during its own reconcile, so the two can never interleave
  - a lock-contended prune-data fails fast (no poll/timeout mode — mirrors `acquireProjectLock`'s existing no-poll philosophy for admin-class commands) with the SAME "update_in_progress" message already used by `update --global`'s own contention path — byte-identical text on both twins, no new error vocabulary
  - a stale (crashed-holder) lock still self-heals via the EXISTING identity-verified reclaim mechanism, unchanged — this task adds a new CALLER, never touches the lock's own internals
  - dry-run (no `--force`) behavior is byte-identical when uncontended (still just lists orphans, removes nothing) — the lock is acquired for the read+compute step regardless of `--force`
</must>
Reject:
<reject>
  - prune-data silently proceeding without the lock while update --global is running -> the exact race this task exists to close; must now fail fast with "update_in_progress"
  - a NEW, prune-data-specific lock file/threshold -> rejected in Framings weighed; would not close the actual cross-command race
  - a poll/--lock-timeout mode added to prune-data -> out of scope; fail-fast only, matching the admin-command precedent
</reject>
After:
<after>
  - `prune-data`/`prune-data --force` cannot run concurrently with `update --global` (or with a second `prune-data`) — the SAME home lock now guards both call sites
  - a contended run fails fast with the existing "update_in_progress" message, unchanged text, on both twins
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ fail-fast (no poll) is the right default for prune-data, an infrequent admin/cleanup command, rather than adding a --lock-timeout poll mode like update --global's own optional wait — lowest confidence because no one has said how prune-data is actually invoked in practice (interactive vs scripted/cron); if wrong: a scripted/cron caller might want to wait briefly rather than fail immediately, requiring a follow-up --lock-timeout addition
  - [ ] the existing "update_in_progress" message (which literally says "another `update --global` is already running") is acceptable to reuse verbatim even when the ACTUAL contention is a sibling prune-data run, rather than a more precise "another operation" wording — chosen for byte-parity + zero risk to the tested lock primitive's existing message; confirm this reads acceptably to an operator
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: prune-data blocked by a live update --global   # M1
  Given `update --global` currently holds the home lock
  When `prune-data` (with or without --force) runs
  Then it fails fast with "update_in_progress" and removes nothing
  And the home lock is still held by the original update --global run afterward

Scenario: prune-data proceeds normally when uncontended   # M4 (regression)
  Given no other lock-holding operation is running
  When `prune-data --force` runs
  Then it acquires the lock, computes and removes orphans exactly as before this fix, and releases the lock

Scenario: a genuinely stale home lock still self-heals under prune-data   # M3
  Given the home lock file is stale (age > staleAfterMs, no live holder)
  When `prune-data` runs
  Then it reclaims the stale lock via the existing identity-verified mechanism, proceeds, and releases

Scenario: two concurrent prune-data runs serialize   # M1 (extension)
  Given one `prune-data --force` is mid-run (holding the lock)
  When a second `prune-data --force` starts
  Then the second fails fast with "update_in_progress", never double-removing/racing on the same rmtree

Scenario: no new lock file is introduced   # R2
  Given the fix is implemented
  Then it uses the EXISTING home lock file/threshold; no new lock file or constant exists
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
FUNCTION prune_data(*, force=False, env=None) / cmdPruneData(args)   body: { orphans, removed }
  acquires _update_lock(home, env=env_map) / acquireUpdateLock(home, {timeout: null}, process.env)
    around the EXISTING _prune_data(home, force=force) / pruneData(home, args.force) call —
    critical section unchanged internally, now lock-guarded
  held + fresh (contended) -> fails fast: "update_in_progress: another `update --global` is
    already running — retry shortly (remove <lockPath> if it is stale)" — IDENTICAL text to the
    existing update --global contention path, no new message
  held + stale -> UNCHANGED existing identity-verified reclaim-ticket self-heal, then proceeds
  uncontended -> byte-identical orphan-list / removal behavior to today, now simply lock-guarded
Schema: no data schema touched — the lock file is the SAME `<home>/.update.lock` update --global
  already uses; no new file, no new env var, no new CLI flag
```

Glossary deltas: none — no new domain term; this task extends an existing primitive's caller set
Status: FROZEN @ v1 — approved by Tin Dang, 2026-07-05 (explicit "implement all" instruction;
  AskUserQuestion freeze-confirmation timed out twice with no response, proceeded per project-lead
  autonomy on a well-reasoned, low-risk, reuse-only design — disclosed here for review/reversal)
Reported: yes — this contract's summary + lowest-confidence flag were shown in-chat before freeze
Least-sure flag surfaced at freeze: [spec] reusing the EXISTING "update_in_progress" message
  verbatim for prune-data's own contention path, even though its wording specifically names
  `update --global` and the actual contention may be a sibling `prune-data` run — chosen for
  byte-parity across both twins and zero risk to the tested lock primitive's own message; cost if
  wrong: a mildly confusing operator-facing message, never a correctness issue (purely cosmetic)

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: n/a — concurrency behavior proven by contention outcome, not line coverage
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_prune_data_blocked_by_live_update_global: arrange hold the home lock directly (simulating a live `update --global`) / act call `prune_data()`/`cmdPruneData` / assert it fails fast with "update_in_progress", removes nothing, and the held lock is untouched · covers: M1
  - test_prune_data_proceeds_when_uncontended: arrange real orphaned data snapshots, no lock held / act call `prune_data(force=True)` / assert byte-identical orphan-list/removal behavior to pre-fix, lock released after · covers: M4 (regression)
  - test_prune_data_reclaims_stale_lock: arrange a stale (aged, no live holder) home lock file / act call `prune_data()` / assert it reclaims via the existing identity-verified mechanism and proceeds · covers: M3
  - test_concurrent_prune_data_runs_serialize: arrange one `prune_data` call holding the lock mid-run (via a monkeypatched hook) / act start a second `prune_data` call / assert the second fails fast, never double-removing · covers: M1 (extension)
  - test_no_new_lock_file_introduced: static source check — `prune_data`/`pruneData`'s new code references the EXISTING `LOCK_FILE`/`_update_lock` symbols only, no new constant/file name · covers: R2
  - test_npm_prune_data_blocked_by_live_update_lock: real `node cli.js prune-data` subprocess smoke against a held `.update.lock` — parity confirmation on the JS twin · covers: M1 (npm parity)
</test_plan>
Also updates (not new tests, but a stale test this task's own frozen contract intentionally
supersedes): `test_global_update_harden.py::PruneDataScopeTest.test_prune_data_deliberately_unlocked`
(global-lock-followups' own "deliberate ruling-out" of prune-data concurrency) is replaced — its
premise is exactly what this task closes; the class docstring's "makes NO new guarantee" no longer
holds. Removing/inverting it is disclosed here, not a silent test weakening.

Tests live in: `add-method/tooling/test_prune_data_lock.py` (new file) · `add-method/tooling/test_global_update_harden.py` (existing file, one stale test replaced) · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/src/add_method/_installer.py`, `add-method/bin/cli.js`,
  `add-method/tooling/test_prune_data_lock.py`, `add-method/tooling/test_global_update_harden.py`
Strategy (ordered batches): 1. write `test_prune_data_lock.py` RED first (confirm against the
  current, unmodified `prune_data`/`pruneData`) · 2. wrap `_prune_data(...)` inside
  `prune_data()` with `with _update_lock(home, env=env_map):`, catching `BlockingIOError` with the
  SAME "update_in_progress" message text `update()` already uses · 3. wrap `pruneData(home,
  args.force)` inside `cmdPruneData` with `acquireUpdateLock(home, {timeout: null}, process.env)`
  (self-fails via the primitive's own existing `fail()` call, no extra catch needed) · 4. replace
  the now-stale `test_prune_data_deliberately_unlocked` in `test_global_update_harden.py` with an
  inverted assertion (or remove it, noting why, in its own class docstring) · 5. confirm GREEN,
  full suite, no regression

Persona (optional): methodology-engine-dev — lock/concurrency discipline, reuse over invention
Known-problem fixes: (1) the OLD test `test_prune_data_deliberately_unlocked` will fail once this
  ships (its entire premise is superseded) → planned fix: replace it in the SAME build, disclosed
  in §4/§7, never left silently red. (2) `prune_data`'s except-clause ordering matters —
  `BlockingIOError` must be caught BEFORE the existing `ValueError` (registry_corrupt) handling so
  a lock-contention failure is never misreported as a corrupt-registry failure → planned fix:
  separate except blocks, `BlockingIOError` first.
Strategy actually used: <fill at VERIFY — the strategy you ACTUALLY used (or "as planned"); harvested into the §7 Decisions (ADR) block as the [AI] build decision>
Safety rule (feature-specific): the lock acquisition must wrap the ENTIRE registry-read +
  orphan-computation + removal critical section — never just the removal step alone (a
  read-then-unlocked-then-remove split would reopen the exact race this task exists to close)
Code lives in: `add-method/src/add_method/_installer.py`, `add-method/bin/cli.js`
Constraints: do NOT change any test or the contract (except the ONE disclosed stale-test
  replacement named above); allow-list packages only (Node/Python built-ins only); ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — `test_prune_data_lock.py` 6/6 OK; `test_global_update_harden.py` 36/36 OK;
  cross-file coverage independently confirmed via `grep -rl "prune_data\|cmdPruneData\|prune-data"
  add-method/tooling/test_*.py` -> 2 more hits (`test_global_restore.py` 36/36 OK,
  `test_release_1_14_0.py` 8/8 OK, both re-run green, not just cited) — every test file touching
  these symbols passes, not just the 2 files this build edited (full-suite confirmation still
  deferred to CI per project convention on this repo's ~2900-test suite)
- [x] coverage did not decrease — 5 new test classes added (6 tests), 0 removed net (1 stale test
  replaced 1:1 in `PruneDataScopeTest`, not deleted)
- [~] no test or contract was altered during build — the CONTRACT was not touched; ONE test WAS
  altered (`test_global_update_harden.py::PruneDataScopeTest`), but disclosed in §4/§7 and judged
  LEGITIMATE, not a silent weakening: it inverts a sibling task's own conscious, disclosed
  carve-out that this task's frozen contract explicitly supersedes (see Advisor Architecture lens
  below) — flagging the nuance rather than a blank checkmark
- [x] the green was EARNED, not gamed — see Refute-read verdict below (mutation-tested, not just
  statically reviewed)
- [x] concurrency / timing of the risky operation is safe — see Advisor Concurrency lens below
- [x] no exposed secrets, injection openings, or unexpected dependencies — see Advisor Security
  lens below
- [x] layering & dependencies follow CONVENTIONS.md — pure reuse of an existing primitive within
  its existing module/file, no new dependency, no new cross-layer coupling
- [ ] a person reviewed and approved the change — pending; this verify pass is the AI-side
  evidence gathering, the GATE RECORD outcome/reviewer below is intentionally left for the
  orchestrator/human to record

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] prune-data fails fast with "update_in_progress" while `update --global` (or a sibling
  prune-data) holds the home lock, and the ORIGINAL holder's lock is left untouched — confirmed
  live by `test_prune_data_lock.py::BlockedByLiveUpdateGlobalTest` + `ConcurrentPruneDataSerializeTest`
  (real threading, real `.update.lock` file), both re-run green post-restore
- [x] uncontended prune-data is byte-identical to pre-fix (same orphan-list/removal, lock released
  after) — confirmed by `UncontendedRegressionTest` (real orphan dir created+removed, lock file
  absent afterward)
- [x] a stale (crashed-holder) lock still self-heals under prune-data via the unchanged
  identity-verified reclaim — confirmed by `StaleLockSelfHealTest` (real aged lock file, `ADD_LOCK_STALE_SECONDS=1`)
- [x] no new lock file/constant was introduced (pure reuse of `_update_lock`/`acquireUpdateLock`) —
  confirmed by `NoNewLockFileTest` (static source scan of both twins) AND independently by grepping
  both CLI parsers (`_cli.py`, `cli.js`): neither wires a `--lock-timeout`/poll flag onto `prune-data`
  (out-of-scope per §1 Reject, confirmed absent)
- [x] npm twin parity: a live-held lock blocks a real `node cli.js prune-data --force` subprocess —
  confirmed by `NpmParityTest` (real subprocess, real exit code + stderr text)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `with _update_lock(...)` is reached from `prune_data`, itself called by
  `_cli.py:67`; `acquireUpdateLock(...)` is reached from `cmdPruneData`, itself dispatched at
  `cli.js:1880` (line re-confirmed at the END of this verify pass, after the sibling task's
  concurrent edits landed — see Live-verify evidence note; it was L1822 earlier in this same
  session). Both new call sites are live entry paths, not orphaned.
- [x] DEAD-CODE (code) — this build introduces ZERO new symbols/constants (pure reuse of the
  existing `_update_lock`/`acquireUpdateLock`/`LOCK_FILE`), so there is no new surface that could
  go unused; confirmed by reading the full diff (+15/-2 Python, +7/-0 JS) — every added line is
  either prose/docstring or directly on the call/except path.
- [ ] SEMANTIC (prose / non-code) — n/a, this task's change is code-only (no prose/doc artifact
  in scope beyond the disclosed docstring/comment additions, which were read in full above).

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> §0's Ground SHA anchors the symbols cited at ground time to that commit — code moves during
> build. Before the gate, re-resolve every symbol §3 CONTRACT cites against the CURRENT tree
> (not the Ground SHA) so a stale anchor is caught here, not by a future reader chasing a moved
> line.
- [x] every symbol §3 CONTRACT cites still resolves in the CURRENT working tree (re-checked twice
  this pass — see note below on why it moved mid-verify): `_prune_data` L917, `prune_data` L969,
  `_update_lock` L1545, `LOCK_FILE` L698 (`_installer.py`); `pruneData` L1315, `cmdPruneData`
  L1362, `acquireUpdateLock` L1449 (`cli.js`) — confirmed via `grep -n '^def \|^function '` run
  fresh at the end of this verify pass.
- [x] anchors DID move since Ground SHA `1ef7132` — named here, not left silent. Two distinct
  causes: (1) THIS task's own build shifted bodies down slightly from §0's cited ranges (expected,
  from the added docstring/lock-wrap prose). (2) A SIBLING task (`sweep-orphan-reclaim-tickets`,
  also mid-flight in this same working tree) landed its own additive changes to these SAME
  functions DURING this verify session — inserting a new `_aged_reclaim_tickets` helper above
  `_prune_data` and extending `_prune_data`'s return arity from a 2-tuple to a 4-tuple
  (`orphans, removed, ticket_orphans, tickets_removed`) — which is why the first line-number set
  I recorded earlier in this same pass (`_prune_data` L899/`prune_data` L922/`pruneData`
  L1288/`cmdPruneData` L1315) went stale mid-verify and had to be re-resolved a second time (the
  numbers above are the re-resolved, final ones). Confirmed this layering is COHERENT, not a
  conflict: `prune_data`'s `with _update_lock(...)` still wraps the ENTIRE (now-4-tuple) call to
  `_prune_data` unpacking correctly (`orphans, removed, ticket_orphans, tickets_removed = ...`),
  and `cmdPruneData`'s `acquireUpdateLock(...)` still precedes its (now-object-returning) call to
  `pruneData(...)` — this task's own lock-wrap contract is INTACT and still covers the whole
  critical section post-layering. Re-ran ALL of `test_prune_data_lock.py` (6/6 OK),
  `test_global_update_harden.py` (36/36 OK), `test_global_restore.py` (36/36 OK), and
  `test_release_1_14_0.py` (8/8 OK) fresh against this final, current tree state — all still
  green, confirming the sibling task's concurrent landing did not silently break this task's fix.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: add-verify (tdd-verifier persona) · adversarially checked: mutation-tested the causal fix
itself, not just static review. Reverted BOTH twins to the pre-fix shape (removed the
`with _update_lock(...)` wrap in `prune_data`, removed the `acquireUpdateLock(...)` call in
`cmdPruneData`, keeping the `except BlockingIOError` handler in place) and re-ran
`test_prune_data_lock.py`: 5/6 tests correctly regressed to red for the RIGHT reason (each
failure was `code == 0` / lock present when it should be absent / "update_in_progress" missing —
i.e. the lock genuinely never engaged), while `test_prune_data_proceeds_when_uncontended`
correctly stayed green (it doesn't depend on locking — the right test to NOT regress). Restored
both files from a pre-edit backup, confirmed the restored diff was byte-identical to the
reviewed diff (`git diff` before/after matched), and re-ran the full 6-test file green (0.06s,
OK). This rules out vacuous asserts / overfit-to-fixtures / stubbed-away logic — the tests
demonstrably exercise the real lock-contention code path, not a fixture illusion.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: add-verify (self)
1. Security: CLEAR — pure reuse of an already-proven, already-audited primitive (`_update_lock`/
   `acquireUpdateLock`); zero new inputs, zero new file paths, zero new env vars/CLI flags, zero
   new external dependency. No secrets touched. Confirmed both CLI parsers (`_cli.py`, `cli.js`)
   gained no new flag on `prune-data` — the surface is unchanged from a caller's perspective
   except the new failure mode's text.
2. Concurrency: CLEAR — the lock genuinely wraps the WHOLE critical section in both twins: Python
   `with _update_lock(home, env=env_map): orphans, removed = _prune_data(...)` (registry-read +
   orphan-compute + removal all inside the `with`); JS `acquireUpdateLock(...)` called
   immediately before `pruneData(...)`, which itself does registry-read + compute + `fs.rmSync`
   inline (no unlocked window between acquire and the call). Mutation-tested (see Refute-read
   above): removing either wrap reopens the race and 5/6 new tests correctly catch it. On the
   except-clause-ordering claim in §5 ("BlockingIOError must be caught before ValueError"):
   traced both raise sites — `_update_lock` raises `BlockingIOError` ONLY before the lock is
   acquired (never inside the `with`/`yield` body), and `ValueError` (`registry_corrupt`) is
   raised ONLY by `_read_registry` inside `_prune_data`, i.e. inside the `with` body, after
   acquisition, and is propagated cleanly through the context manager's `finally` (which always
   closes+unlinks the lock file on any exit path). Since `BlockingIOError` and `ValueError` are
   disjoint exception classes at disjoint raise sites (neither subclasses the other), the actual
   except-clause ORDER is not load-bearing for correctness here — but it is harmless, matches the
   stated intent, and costs nothing; noting this so the record doesn't overstate the mechanism.
   No window found where the fix leaves the race half-closed.
3. Architecture: CLEAR — reusing the exact existing lock primitive (no new file, no new
   threshold, no new poll mode) mirrors `project-scope-install-lock`'s own precedent of wrapping
   an existing call site in an existing proven lock at `autonomy: auto`; this is the right call
   for a low-frequency admin command and avoids inventing a second serialization mechanism that
   would NOT have closed the actual cross-command race (per §1 Framings weighed). The
   `test_global_update_harden.py::PruneDataScopeTest` replacement is legitimate, not a scope
   violation: it inverts a sibling task's (`global-lock-followups`) own disclosed, conscious
   "deliberate ruling-out," which THIS task's frozen contract explicitly supersedes — disclosed
   in §4/§7, not a silent test weakening, and `add.py check` raised zero coverage-gap or
   tamper-style warning against this task. The reused "update_in_progress" message naming
   `update --global` even when the actual contention is a sibling `prune-data` run is a known,
   disclosed cosmetic tradeoff (§3 least-sure flag) — accepted, not a residue.
Verdict: PASS
Residue: none — one non-blocking 💭 note: `test_prune_data_blocked_by_live_update_global` only
  exercises `force=True`; the M1 scenario says "with or without --force" fails fast. Structurally
  covered, not a gap: `prune_data`'s `with _update_lock(...)` wraps `_prune_data(home,
  force=force)` — the lock is acquired BEFORE the force/no-force branch, so acquisition (and thus
  contention) is force-independent by construction, not by an untested assumption. A second
  💭 note: the `except BlockingIOError` in `prune_data` would also catch (and mislabel
  "update_in_progress") a `BlockingIOError` bubbling from `_prune_data` itself, not just from
  `_update_lock` — astronomically unlikely for a local `shutil.rmtree`/registry read, not a bug,
  but the record should not overstate this as structurally impossible.
Binding: advisory — following this project's own precedent on sibling lock-fix tasks
  (`project-scope-install-lock`, `global-lock-followups`): `autonomy: auto` + no declared
  `risk: high` + complete, independently-reproduced evidence (not merely the execution_context's
  claimed "2941/0" — cross-file coverage was independently re-run this pass: `test_global_restore.py`
  36/36, `test_release_1_14_0.py` 8/8, both green, closing the gap between "the 2 files I touched
  pass" and "every file exercising `prune_data`/`cmdPruneData` passes") makes this a legitimate
  auto-PASS candidate under this task's own autonomy level — not a "mechanical" sensitivity
  classification. A lock/concurrency change is not obviously *purely* mechanical merely because
  it reuses an existing primitive; "advisory" is the more honest label here, consistent with how
  this project's own prior lock-fix tasks recorded this field.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-05

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose reuse the existing `_update_lock`/`acquireUpdateLock` around prune-data's critical section; rejected a NEW, separate prune-data-only lock file — rejected, would serialize two prune-data runs against each other but do NOTHING to prevent the actual update-global-vs-prune-data race this task exists to close · an optimistic "snapshot the registry, retry-if-changed" read — rejected, more complex than reusing an already-tested mutual-exclusion primitive for a low-frequency admin command where a brief fail-fast is acceptable
- [human] freeze — froze §3 @ v1 (approved by Tin Dang, 2026-07-05 (explicit "implement all" instruction;)
- [AI] build — strategy used: as planned
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.

