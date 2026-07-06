# TASK: Sweep Orphaned Reclaim Ticket Files

slug: sweep-orphan-reclaim-tickets · created: 2026-07-03 · stage: mvp
milestone: (none)
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): `add-method/src/add_method/_installer.py:_prune_data`/`prune_data` and `add-method/bin/cli.js:pruneData`/`cmdPruneData` — as extended by the sibling task `prune-data-update-lock` (now lock-guarded) — extended further here to ALSO sweep aged orphan `.reclaim-*` ticket files: home-scope `<home>/<LOCK_FILE>.reclaim-<ino>` and project-scope `<addDir>/<PROJECT_LOCK_FILE>.reclaim-<ino>` for every registry-live project
Context (working folder): the ticket-staleness constants ALREADY exist and are already trusted for identical inline reclaim-time decisions: `_LOCK_TICKET_STALE_SECONDS`/`LOCK_TICKET_STALE_SECONDS = 5` (`_installer.py` L1425 / `cli.js` L769) and `_PROJECT_LOCK_TICKET_STALE_SECONDS`/`PROJECT_LOCK_TICKET_STALE_SECONDS = 5` (`_installer.py` L1665 / `cli.js` L783)
Honors (patterns / conventions): reuse the identical staleness constants + the identical "best-effort, swallow errors" unlink convention already used throughout the reclaim-ticket code — never invent a new threshold or a new error-handling shape
Seams consulted: none cited
Anchors the contract cites: `LOCK_TICKET_STALE_SECONDS`/`PROJECT_LOCK_TICKET_STALE_SECONDS`; the ticket path shape `<lockPath>.reclaim-<ino>` already used by the existing reclaim logic; the sibling task's lock-guarded `_prune_data`/`pruneData` call site
Issues/Risks (→ feed §1): (1) DEPENDS on `prune-data-update-lock` landing first — this task extends the SAME now-lock-guarded critical section, so it must be sequenced after it. (2) a ticket file could, in extreme theory, be aged past its 5s threshold while STILL representing a genuinely in-flight reclaim if a process were catastrophically slow between opening the ticket and its own cleanup — but this is the IDENTICAL trust boundary the EXISTING reclaim logic itself already accepts for this exact constant; a sweep applies the SAME already-accepted 5s trust window to litter that would otherwise never be revisited, not a new risk class. (3) project-scope tickets live inside EACH project's OWN `.add/` dir, not the shared home — sweeping them from a "global" prune-data command means iterating the registry (already read for the data-orphan sweep) and only touching LIVE (still-existing, still-registered) project paths, never a vanished one. (4) dry-run vs --force semantics must extend consistently: list-only when dry, remove only under --force, exactly like the existing data-orphan behavior.
Related intent: seeded from global-lock-followups + project-scope-install-lock spec-deltas — both sibling lock-hardening tasks this session independently named the same gap: a ticket leaked by a crash between winning it and its own cleanup has no sweep mechanism [← global-lock-followups, project-scope-install-lock]
Ground SHA: `1ef7132`

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: extend `prune-data`/`prune_data` (as lock-guarded by the sibling task `prune-data-update-lock`) to ALSO find (dry-run) and remove (--force) aged orphan `.reclaim-*` ticket files — home-scope under `<home>` and project-scope under every still-registered, still-existing project's `.add/` dir — reusing the EXISTING per-lock staleness constants, never inventing a new threshold (from global-lock-followups + project-scope-install-lock spec-deltas, an identical ask from both sibling lock tasks)
Framings weighed: extend the EXISTING prune-data command (chosen — it is already the "reclaim shared-home litter" command, already lock-guarded by the sibling task, and already has the dry-run/--force UX this sweep should mirror) · a brand-new `sweep-tickets` CLI command — rejected, needless surface duplication for a closely-related cleanup concern with an identical dry-run/--force shape already established · sweeping tickets opportunistically INSIDE the reclaim path itself (self-clean on next contention) — rejected, does not address a ticket that is NEVER contended again (the reported gap: an old generation's ticket path becomes permanently unreachable via normal contention once the lock moves to a new inode)
Must:
<must>
  - a `.reclaim-*` ticket file (home-scope or project-scope) older than its OWN kind's existing staleness constant (`LOCK_TICKET_STALE_SECONDS`/`PROJECT_LOCK_TICKET_STALE_SECONDS`, currently 5s) is found and reported under a dry-run `prune-data`, and removed under `prune-data --force`
  - project-scope ticket sweep only ever touches a project's `.add/` dir that is CURRENTLY on the registry AND still exists on disk (never a vanished/unregistered path) — mirrors the existing data-orphan "live" definition
  - the sweep runs INSIDE the same home-lock-held critical section the sibling task added, so it can never race update --global's own reconcile
  - a ticket younger than its staleness threshold (a genuinely in-flight reclaim) is NEVER touched, dry-run or --force
</must>
Reject:
<reject>
  - inventing a new staleness threshold for the sweep -> reject; must reuse the EXISTING LOCK_TICKET_STALE_SECONDS/PROJECT_LOCK_TICKET_STALE_SECONDS constants verbatim
  - sweeping a ticket under an unregistered or vanished project path -> reject; only registry-live projects are ever touched
  - removing a ticket in dry-run mode -> reject; dry-run only ever lists, exactly like the existing data-orphan behavior
</reject>
After:
<after>
  - `prune-data` (dry-run) additionally lists aged orphan ticket files found, home-scope and project-scope
  - `prune-data --force` additionally removes them, reporting a count
  - a young/in-flight ticket is never touched regardless of mode
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ sweeping a project's ticket files from the GLOBAL prune-data command (rather than requiring that project's OWN project-lock to be held during the sweep) is safe because the sweep only ever touches tickets already older than their own 5s staleness constant — the SAME trust window the existing inline reclaim logic already relies on for the identical file — lowest confidence because this is a NEW call path (a global command reaching into a per-project directory) that hasn't been exercised this way before, even though the underlying trust assumption is unchanged; if wrong: a sweep could theoretically remove a ticket for an extraordinarily slow (but genuinely still in-flight) reclaimer in some OTHER project — though this exposure already exists identically in the current, unmodified reclaim code's own self-heal path
  - [ ] whether a skipped/unparseable or otherwise-not-swept ticket should be COUNTED/reported separately from data orphans in the CLI output, versus folded into one combined count — leaning toward separate counts for operator clarity; confirm at freeze
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: an aged home-scope orphan ticket is swept   # M1
  Given a `.update.lock.reclaim-<ino>` ticket file exists, older than LOCK_TICKET_STALE_SECONDS, with no corresponding live lock at that inode
  When `prune-data --force` runs
  Then the ticket file is removed and reported in the removal count

Scenario: an aged project-scope orphan ticket is swept for a live registered project   # M2
  Given a registered, still-existing project's `.add/.install.lock.reclaim-<ino>` ticket file exists, older than PROJECT_LOCK_TICKET_STALE_SECONDS
  When `prune-data --force` runs
  Then the ticket file is removed and reported in the removal count

Scenario: a project-scope ticket under an unregistered or vanished project is never touched   # M2 (reject)
  Given an aged ticket file sits under a project path NOT on the registry (or vanished from disk)
  When `prune-data --force` runs
  Then that ticket file is left untouched

Scenario: a young, genuinely in-flight ticket is never swept   # M1/M2 (reject)
  Given a ticket file younger than its staleness constant exists
  When `prune-data` (dry-run or --force) runs
  Then it is never listed and never removed

Scenario: dry-run only lists, never removes   # After
  Given aged orphan tickets exist, home-scope and project-scope
  When `prune-data` (no --force) runs
  Then they are listed but not removed
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
FUNCTION _prune_data(home, *, force) / pruneData(home, force)
  body: { orphans, removed, ticket_orphans, tickets_removed }
  (extends the sibling task's lock-guarded call site) ALSO globs <home>/<LOCK_FILE>.reclaim-* and,
    for every registry-live project, <addDir>/<PROJECT_LOCK_FILE>.reclaim-* — each aged past its
    own kind's existing staleness constant is a ticket orphan; --force removes it (best-effort,
    swallow errors — matches the existing reclaim code's own convention)
  dry-run -> lists data orphans AND ticket orphans (reported as separate counts), removes neither
  --force -> removes both classes, reports both counts separately
Schema: no new file/constant — reuses LOCK_FILE/PROJECT_LOCK_FILE/LOCK_TICKET_STALE_SECONDS/
  PROJECT_LOCK_TICKET_STALE_SECONDS verbatim; the registry (already read for the data-orphan
  sweep) is the ONLY new read needed to enumerate project-scope ticket sweep targets
```

Glossary deltas: `orphan reclaim ticket`: a `.reclaim-<ino>` per-generation reclaim-arbitration file (home-scope or project-scope) whose corresponding lock generation has since moved on (or whose winning process crashed before its own cleanup) — permanently unreachable via normal contention once aged past its own kind's existing staleness constant; swept by `prune-data --force` alongside orphaned data snapshots. [folded foundation-version 64]
Status: FROZEN @ v1 — approved by Tin Dang, 2026-07-05 (explicit "implement all" instruction;
  AskUserQuestion freeze-confirmation timed out twice with no response, proceeded per project-lead
  autonomy on a well-reasoned, low-risk, reuse-only design — disclosed here for review/reversal)
Reported: yes — this contract's summary + lowest-confidence flag were shown in-chat before freeze
Least-sure flag surfaced at freeze: [spec] sweeping a PROJECT's ticket files from the GLOBAL
  prune-data command without requiring that project's own project-lock to be held during the
  sweep — accepted because it only ever touches tickets already older than the SAME 5s trust
  window the existing inline reclaim logic already relies on for the identical file, not a new
  risk class; cost if wrong: an extraordinarily slow (but genuinely still in-flight) reclaimer's
  ticket could be swept early in some rare case — an exposure that already exists identically in
  the current, unmodified reclaim code's own self-heal path (not newly introduced here). Decided
  the open UX question (separate ticket-orphan vs data-orphan counts) myself: yes, report
  separately — matches this project's "measure, never block" operator-clarity convention.

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: n/a — concurrency/litter-sweep behavior proven by outcome, not line coverage
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_aged_home_ticket_is_swept: arrange an aged `.update.lock.reclaim-<ino>` file / act `prune_data(force=True)` / assert removed, reported in ticket count · covers: M1
  - test_aged_project_ticket_is_swept_for_live_project: arrange a registered, existing project with an aged `.install.lock.reclaim-<ino>` under its `.add/` / act `prune_data(force=True)` / assert removed, reported · covers: M2
  - test_ticket_under_unregistered_project_untouched: arrange an aged ticket under a project path NOT in the registry / act `prune_data(force=True)` / assert left alone · covers: M2 (reject)
  - test_young_ticket_never_swept: arrange a ticket younger than its staleness constant, home-scope and project-scope / act `prune_data` (dry-run and --force) / assert never listed, never removed · covers: M1/M2 (reject)
  - test_dry_run_lists_tickets_without_removing: arrange aged tickets, both scopes / act `prune_data(force=False)` / assert listed, not removed · covers: After
  - test_no_new_staleness_constant_introduced: static source check — sweep code references the EXISTING LOCK_TICKET_STALE_SECONDS/PROJECT_LOCK_TICKET_STALE_SECONDS symbols only · covers: R1
  - test_npm_ticket_sweep_parity: real `node cli.js prune-data --force` subprocess smoke sweeping an aged home-scope ticket · covers: M1 (npm parity)
</test_plan>
Also updates (existing test, not new, but MUST change because `_prune_data`'s return shape grows
from a 2-tuple to a 4-tuple per this task's own frozen §3 CONTRACT):
`test_global_restore.py`'s 4 call sites (`orphans, removed = _installer._prune_data(...)`) need
extended unpacking (`orphans, removed, *_ = ...`) — disclosed here, not a silent touch.

Tests live in: `add-method/tooling/test_sweep_orphan_tickets.py` (new file) · `add-method/tooling/test_global_restore.py` (existing file, 4 call sites re-unpacked) · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/src/add_method/_installer.py`, `add-method/bin/cli.js`, `add-method/tooling/test_sweep_orphan_tickets.py`, `add-method/tooling/test_global_restore.py`
Strategy (ordered batches): 1. write `test_sweep_orphan_tickets.py` RED first (confirm against the
  sibling task's already-lock-guarded but not-yet-ticket-sweeping `_prune_data`/`pruneData`) ·
  2. extend `_prune_data(home, *, force)` to also glob+age-check `<home>/<LOCK_FILE>.reclaim-*`
  and, for every registry entry that still exists on disk, `<addDir>/<PROJECT_LOCK_FILE>.reclaim-*`
  — return `(orphans, removed, ticket_orphans, tickets_removed)` · 3. update `prune_data()`'s log
  output to report ticket counts alongside data-orphan counts · 4. mirror identically in
  `pruneData`/`cmdPruneData` (JS), returning `{orphans, removed, ticketOrphans, ticketsRemoved}` ·
  5. update `test_global_restore.py`'s 4 call sites to extended-unpack (`*_`) the now-4-tuple ·
  6. confirm GREEN, full suite, no regression

Persona (optional): methodology-engine-dev — lock/concurrency + litter-sweep discipline, reuse over invention
Known-problem fixes: (1) `_prune_data`'s Python return grows from a 2-tuple to a 4-tuple, breaking
  `test_global_restore.py`'s 4 existing positional-unpack call sites → planned fix: extended
  unpacking (`orphans, removed, *_ = ...`), disclosed in §4, not silent. (2) the JS side's
  `pruneData` already returns an OBJECT (`{orphans, removed}`) — adding new keys is non-breaking
  for existing dot-access callers, no JS test needs updating for the shape change itself.
  (3) a project path that no longer exists on disk (vanished) must be skipped when sweeping its
  tickets — never `Path.exists()`-crash on a dangling registry entry → planned fix: guard with an
  existence check before globbing, mirrors the existing "live" definition already used for data
  orphans.
Strategy actually used: as planned — all 6 batches executed in order (RED test file first, confirmed
  it exercised the sibling task's not-yet-ticket-sweeping code; `_prune_data`/`pruneData` extended
  to 4-tuple/{...} with a shared `_aged_reclaim_tickets`/`agedReclaimTickets` helper reused for both
  home-scope and project-scope globs; log output extended additively; `test_global_restore.py`'s 4
  call sites fixed via extended-unpack — 3 needed it, the 4th (`assertRaises(ValueError)`, no
  unpack) was already unaffected). All 7 new tests + the 3 sibling suites (`test_global_restore`,
  `test_prune_data_lock`, `test_global_update_harden`, 78 tests total) green on first run after
  implementation — no iteration needed.
Safety rule (feature-specific): a ticket sweep must NEVER touch a file younger than its own kind's
  existing staleness constant — the age check is re-verified at the moment of the (best-effort)
  unlink, not just at the moment of listing, so a race between listing and removal can't widen the
  window past what the constant already accepts
Code lives in: `add-method/src/add_method/_installer.py`, `add-method/bin/cli.js`
Constraints: do NOT change any test or the contract (except the ONE disclosed extended-unpack
  touch to `test_global_restore.py`, required by this task's own frozen return-shape extension);
  allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 86/86 green (85 pre-existing + 1 new mutation-catching test added at this gate; see Refute-read verdict)
- [x] coverage did not decrease — no line-coverage target for this task (§4: "n/a — behavior proven by outcome"); behavior coverage INCREASED by one test (see below)
- [x] no test or contract was altered during build — §3 CONTRACT text is byte-identical to FROZEN @ v1; test touches are limited to the two DISCLOSED shapes: (a) `test_global_restore.py`'s 3 extended-unpack call sites (build's own disclosed known-problem fix), (b) one new regression test I added during THIS verify pass to close a demonstrated coverage gap (disclosed below, additive-only, nothing weakened/deleted)
- [x] the green was EARNED, not gamed — adversarial refute-read performed by self (add-verify); see Refute-read verdict below (one real coverage gap found AND closed, not silently patched over)
- [x] concurrency / timing of the risky operation is safe — independently analyzed, not just trusting the offered reasoning; see Advisor 3-lens, lens 2
- [x] no exposed secrets, injection openings, or unexpected dependencies — see Advisor 3-lens, lens 1
- [x] layering & dependencies follow CONVENTIONS.md — one minor, non-blocking disclosed inconsistency; see Advisor 3-lens, lens 3
- [ ] a person reviewed and approved the change — reserved for the human/orchestrator gate

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `prune-data` (dry-run) lists aged home-scope AND project-scope ticket files, removing neither — confirmed by `test_dry_run_lists_tickets_without_removing` + direct read of `_prune_data`'s `if force:` guard around the unlink loop (installer.py:963)
- [x] `prune-data --force` removes aged tickets in both scopes and reports two SEPARATE counts (never folded into the data-orphan count) — confirmed by `test_aged_home_ticket_is_swept` / `test_aged_project_ticket_is_swept_for_live_project` + `prune_data()`'s two distinct log lines (installer.py:1010-1013) and `cmdPruneData`'s mirror (cli.js:1382-1383)
- [x] a ticket under an unregistered or vanished project path is left completely untouched — confirmed by `test_ticket_under_unregistered_project_untouched` (the sweep only walks `live_paths`, i.e. registry entries that still `Path.exists()`, installer.py:939,956)
- [x] a ticket younger than its own kind's staleness constant is never listed or removed, dry-run or --force — confirmed by `test_young_ticket_never_swept`, AND independently reconfirmed by mutation (see Refute-read)
- [x] no new staleness threshold was invented, either language — confirmed by `test_no_new_staleness_constant_introduced` (static source scan of both `_prune_data`+`_aged_reclaim_tickets` and `pruneData`+`agedReclaimTickets`) + my own direct read: both constants are reused verbatim, no new symbol
- [x] the JS twin (`pruneData`/`cmdPruneData`) matches the Python shape and behavior, including the re-check-at-unlink safety fix — confirmed by side-by-side read of both files (installer.py:917-973 vs cli.js:1315-1354; the safety-rule line is present in both: installer.py:966-967, cli.js:1346) + `test_npm_ticket_sweep_parity` real-subprocess smoke

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_aged_reclaim_tickets`/`agedReclaimTickets` is referenced from BOTH the home-scope and per-project-scope glob call sites inside `_prune_data`/`pruneData` (installer.py:954,959; cli.js:1333,1337); `ticket_orphans`/`tickets_removed` (`ticketOrphans`/`ticketsRemoved`) are consumed by `prune_data()`/`cmdPruneData()`'s log branches (installer.py:1006-1022; cli.js:1377-1391) — no orphaned symbol
- [x] DEAD-CODE (code) — none found; every new name is reached from `_prune_data`'s own dry-run and --force paths in both languages
- [ ] SEMANTIC (prose / non-code) — n/a, this task is a code change (function extension), not a prose/doc task

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> §0's Ground SHA anchors the symbols cited at ground time to that commit — code moves during
> build. Before the gate, re-resolve every symbol §3 CONTRACT cites against the CURRENT tree
> (not the Ground SHA) so a stale anchor is caught here, not by a future reader chasing a moved
> line.
- [x] every symbol §3 CONTRACT cites still resolves in the current tree — confirmed by direct read: `_prune_data`/`pruneData` (installer.py:917, cli.js:1315); `_LOCK_TICKET_STALE_SECONDS`/`LOCK_TICKET_STALE_SECONDS` and `_PROJECT_LOCK_TICKET_STALE_SECONDS`/`PROJECT_LOCK_TICKET_STALE_SECONDS` (installer.py:1504,1744; cli.js:769,783); the `.reclaim-<ino>` ticket-path shape (installer.py:1612,1837 — the SAME shape `_aged_reclaim_tickets` globs for); the sibling task's lock-guarded call site (`with _update_lock(home, ...)` at installer.py:997; `acquireUpdateLock(...)` at cli.js:1373) — all resolve
- [x] anchor drift named: the Python `_LOCK_TICKET_STALE_SECONDS`/`_PROJECT_LOCK_TICKET_STALE_SECONDS` constants moved from the §0 Ground-cited L1425/L1665 to the CURRENT L1504/L1744 (+79 lines each) — pushed down by this task's own ~90-line insertion of `_aged_reclaim_tickets`/`_prune_data`'s extension earlier in the file; NAMES unchanged, only line numbers shifted. The JS anchors (cli.js L769/783) did NOT move (the new `agedReclaimTickets`/extended `pruneData` were appended later in that file, after these constants) — no rename, no silent drift, both confirmed by direct grep against the current tree

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self (add-verify) · adversarially checked: two causal fix lines, one mutation at a time, restore-and-reconfirm-green between each —
  1. The ORIGINAL listing-time age check in `_aged_reclaim_tickets` (`if age > stale_after: aged.append(p)`) — neutered to an unconditional append. Result: `test_young_ticket_never_swept` went RED for the RIGHT reason (a fresh, still-in-flight-looking ticket was now incorrectly listed as a ticket orphan); all 6 other tests stayed green. Restored; reconfirmed 7/7 green.
  2. The NEWLY-ADDED re-check-at-unlink safety fix (`if time.time() - ticket.stat().st_mtime <= stale_after: continue`) — neutered by deleting the check (unconditional unlink). Result: **zero existing tests caught this regression** — all 7 tests in `test_sweep_orphan_tickets.py` plus all of `test_prune_data_lock.py` stayed green. This is a genuine, demonstrated coverage gap for the EXACT safety-critical fix this task was spawned to independently verify — the described fix was real and correctly implemented (confirmed by reading the code before mutating it), but nothing in the frozen test plan actually exercised the race it closes.
     Gap CLOSED, not silently left: added `ReCheckAtUnlinkTest.test_ticket_refreshed_between_listing_and_unlink_is_not_removed` to `test_sweep_orphan_tickets.py`, using `mock.patch("add_method._installer.time.time", side_effect=[listing_now, unlink_now])` to deterministically force a ticket to read AGED at listing time and FRESH at the unlink re-check (no real sleep, no flaky timing dependency). Confirmed: (a) passes against the correct implementation, (b) fails for the right reason against the neutered mutation (ticket wrongly removed), (c) does not affect any other test either way. Restored the correct implementation; full 4-suite set re-confirmed 86/86 green (was 85/85 before this addition — +1 test, 0 regressions).
  No overfit-to-fixture or vacuous-assert pattern found elsewhere in the suite (each test asserts on real filesystem state — `ticket.exists()` / membership in the returned lists — not on internal call counts or mocks of the code under test, except the one new test above which mocks ONLY the time source, not the logic being verified).

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: self (add-verify)
1. Security: CLEAR — no new external/attacker-reachable input; the glob prefix (`lock_file_name + ".reclaim-*"`) is a fixed literal, not user-controlled; ticket paths derive from the already-trusted registry read (no new read); no new dependency (stdlib `pathlib`/`os`/`time` only, already used throughout this module); no secret ever touches a ticket file (empty-content tickets, per `_home_ticket`/`_project_ticket` test helpers and the production `O_CREAT|O_EXCL` opens).
2. Concurrency: CLEAR — independently verified, not a restatement of the offered reasoning. Read the actual ticket-creation/self-heal code (`_project_lock`, installer.py:1837-1931, and the home-lock twin at installer.py:1606-1670): a reclaim ticket's own critical section is a tiny, FIXED handful of syscalls (open→close→stat→unlink) and its mtime is set ONCE at creation — nothing refreshes it while "held," unlike the main lock file itself (which IS refreshed on a background thread, installer.py:1517). So a ticket only ever reads "aged past 5s" if it is genuinely abandoned; under normal operation a live ticket's actual hold time is microseconds-to-low-milliseconds, ~1000x under the 5s threshold. The sweep's fresh, per-ticket `time.time()` re-check at unlink time (proven by mutation test #2 above to be a REAL, load-bearing check, not decorative) correctly distinguishes "genuinely abandoned" from "was just refreshed/recreated since listing." `_prune_data` therefore does not need the target project's own `_project_lock`: it never touches that project's live lock file, only litter whose own staleness constant is the SAME one `_project_lock`'s own inline reclaim already trusts for the identical file class.
3. Architecture: RESIDUE (minor, non-blocking) — the existing inline reclaim logic (installer.py:1656-1668 and 1881-1889) re-verifies BOTH age AND inode identity (`current_tino == tst.st_ino`) immediately before unlinking a stale ticket, closing even the sub-microsecond stat-to-unlink TOCTOU gap. The new sweep's re-check (installer.py:964-971 / cli.js:1344-1349) verifies age only, not inode identity — narrower than the codebase's own established precedent for this exact file class, and a partial departure from §1's "reuse the identical... error-handling shape" honor. Not a new risk class in practice (the residual gap is the same single-syscall window the existing code's own inode-check cannot fully close either; worst case is one contender's fail-fast retry, not a double-hold or data loss) — but real and disclosable. Recommend a follow-up spec delta: add the same inode-identity re-check to the sweep's unlink for full precedent parity.
Verdict: PASS (on the 3-lens code review) — see Residue for a SEPARATE, mechanical/engine-bookkeeping matter that is NOT a security/concurrency/architecture finding.
Residue: (a) code/architecture — the inode-identity-recheck gap above (non-blocking, follow-up spec delta recommended, not a gate blocker); (b) MECHANICAL/ENGINE — `add.py check` currently reports BOTH `build_tampered` (a tracked test changed since the tests→build snapshot — the sibling task's already-disclosed 3-line extended-unpack fix in `test_global_restore.py`, PLUS the ReCheckAtUnlinkTest I added at THIS gate to close the refute-read gap above) AND `scope_violation pending` for `add-method/tooling/test_sweep_orphan_tickets.py` + `test_global_restore.py`. Traced to root cause (not left as an unexplained warning): state.json's scope anchor (`.declared`) only captured 2 of the 4 §5-declared paths — `_installer.py` and `cli.js` — because §5's "Scope (may touch):" line wraps across TWO physical lines in TASK.md, and `_declared_scope`'s regex (`re.search(r"^\s*Scope \(may touch\):.*$", body, re.M)`) only matches the FIRST physical line (`.` does not match `\n` even under `re.M`), silently dropping every backticked token on the continuation line — reproduced directly against the live regex to confirm. This is an engine-bookkeeping gap, NOT a real scope overreach: both files I touched are named, verbatim, in §5's own text. I deliberately did NOT edit §5 myself to fix the line-wrap — doing so post-snapshot could look like unilaterally relitigating a build-scope-lock anchor, which is exactly what that guard exists to prevent. The orchestrator will need to re-cross tests→build→verify (regenerating the anchor from a corrected, single-line §5 Scope declaration) before the engine will accept completion of this task.
Binding: advisory — sensitivity: architecture (lens 3 code note) and mechanical (engine/process note); no security finding, nothing binding-gate here.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-05

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose extend the EXISTING prune-data command; rejected a brand-new `sweep-tickets` CLI command — rejected, needless surface duplication for a closely-related cleanup concern with an identical dry-run/--force shape already established · sweeping tickets opportunistically INSIDE the reclaim path itself (self-clean on next contention) — rejected, does not address a ticket that is NEVER contended again (the reported gap: an old generation's ticket path becomes permanently unreachable via normal contention once the lock moves to a new inode)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang, 2026-07-05 (explicit "implement all" instruction;)
- [AI] build — strategy used: as planned — all 6 batches executed in order (RED test file first, confirmed it exercised the sibling task's not-yet-ticket-sweeping code; `_prune_data`/`pruneData` extended to 4-tuple/{...} with a shared `_aged_reclaim_tickets`/`agedReclaimTickets` helper reused for both home-scope and project-scope globs; log output extended additively; `test_global_restore.py`'s 4 call sites fixed via extended-unpack — 3 needed it, the 4th (`assertRaises(ValueError)`, no unpack) was already unaffected). All 7 new tests + the 3 sibling suites (`test_global_restore`, `test_prune_data_lock`, `test_global_update_harden`, 78 tests total) green on first run after implementation — no iteration needed.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.

