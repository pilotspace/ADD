# TASK: global-data-restore follow-ups: mid-write atomicity, directory-restore test, npm behavioral test

slug: global-data-restore-harden · created: 2026-07-02 · stage: mvp
milestone: install-update-hardening
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
- `add-method/src/add_method/_installer.py:_persist_data(home: Path, project_abspath) -> bool` (717-736) — the one-way WHOLE-SNAPSHOT-DIRECTORY replace: `if dest.exists(): shutil.rmtree(dest)` then `dest.mkdir()` then a per-entry `copytree`/`copyfile` loop writing DIRECTLY onto `dest`'s (= `home/data/<key>`) final path — no staging. A crash mid-loop leaves `dest` a random partial mix of old+new. FOLDED INTO this task's scope (§1 decides this explicitly, not silently).
- `add-method/src/add_method/_installer.py:_restore_data(home: Path, project_abspath, *, force=False) -> bool` (740-776) — the fill-gaps inverse. Per entry: fill-gaps (dest absent) copies straight onto dest's final name; force (dest present) does an ATOMIC `os.replace(dest, bak)` first (already safe) but THEN copies the new content straight onto dest's now-freed final name (NOT atomic) — a crash mid-copy in EITHER sub-case leaves that one entry a partial tree sitting at its final name. This per-entry direct-to-final-name copy is the atomicity gap this task closes.
- `add-method/src/add_method/_installer.py:_is_user_data(name) -> bool` (704-713) + `_DATA_EXCLUDE` (691) — the exact-name/pattern filter both functions use to scan `.add/`'s top-level entries; does not (yet) recognize a scratch-staging sibling name (see Issues/Risks #3).
- `add-method/src/add_method/_installer.py:install(...)` (888-1078) — calls `_persist_data` at line 1056 (`as_global_data`) and `_restore_data` at line 1071 (`as_global_data_restore`); both stay UNCHANGED callers (same call, same `except OSError` mapping to `data_unwritable`/`restore_failed`).
- `add-method/src/add_method/_installer.py:_update_global(...)` (1252-1331) — ALSO calls `_persist_data` at line 1321 ("keep the opted-in project's snapshot current," inside the per-registered-project loop of `update --global`) — an unchanged caller that benefits from the hardening for free.
- `add-method/bin/cli.js:persistData` (942-954), `restoreData` (981-1001), `isUserData` (932-938) / `DATA_EXCLUDE` (921) — the npm twins, identical shape and identical gap; `persistData` is likewise auto-called from `cmdUpdateGlobal`'s (1117) per-project loop at line 1151.
- `add-method/src/add_method/_installer.py:_prune_data(home, *, force=False)` (780-799) — read for context only, CONFIRMED OUT of scope: a single `shutil.rmtree` per orphan KEY directory (a whole-directory delete, not wipe-then-copy) — no partial-write class of bug here; its registered-vanished-owner design (`live = {data_key(p) for p in reg if Path(p).exists()}`) is untouched by this task.

Context (working folder):
- `.add/milestones/install-update-hardening/MILESTONE.md` — still template-blank (goal: "...survive a crash or a concurrent run without leaving a half-written .add/ tree or a wedged lock"); NOT filled here — the orchestrator fills it once all 4 sibling tasks' scope is known.
- Predecessor `.add/tasks/global-data-restore/TASK.md` (phase: done, FROZEN @ v1, shipped 2026-06-28) — this task's 3 named follow-ups are VERBATIM from its own §7 Spec delta, each evidenced by its refute-read's own named Holes 1/2/3: (a) mid-write atomicity, (b) a missing directory-entry `--force` test, (c) a real npm behavioral test to replace the structural-only `ParityRestoreTest`.
- Sibling `.add/tasks/project-scope-atomic-reconcile/TASK.md` (Status: DRAFT, phase: contract, same milestone) — read in full as the exemplar: `_clean_replace`/`cleanReplaceTree` (~1130 Python / 790 JS) get an IDENTICAL wipe-then-copy defect fixed via self-heal → whole-tree stage → 2-rename commit → sweep. Reused directly for `_persist_data` below; adapted to per-entry granularity for `_restore_data` (§1 names why the shapes diverge).
- Other siblings in this milestone (NOT read, per this task's own isolation boundary): `global-lock-followups` (drafted in parallel by another agent — owns "a home file-lock to serialize prune-data" per the predecessor's own delta #4, explicitly not this task's concern) and `project-scope-install-lock` (named only as the atomic-reconcile task's own `depends_on` — owns cross-process concurrency generally).
- Tests (canonical): `add-method/tooling/test_global_restore.py` (286 lines — classes `_Base`/`RestoreTest`/`RestoreUnitTest`/`PruneTest`/`ParityRestoreTest`). CONFIRMED by reading the actual test methods: `test_force_overwrites_with_bak` is FILE-only (no directory-entry force test exists anywhere in the file); `test_unwritable_dest_raises` covers a WHOLESALE-unwritable `.add` (replaced by a plain file before the call), not a failure partway through a multi-entry loop; `ParityRestoreTest.test_parity_surface` is exactly 6 `assertIn` string-presence checks and contains no `subprocess`/`node` invocation at all — confirming all 3 origin follow-ups are real, currently-uncommitted gaps. `test_global_update_harden.py` (321 lines) is the exemplar BEHAVIORAL pattern: `shutil.which("node")`-gated `subprocess.run(["node", str(CLI_JS), ...])` asserting real stdout/exit-code, not string presence.

Honors (patterns / conventions):
- `.add/personas/methodology-engine-dev.md` Critical Rules (line 14): "Design for failure. Every IO touch has a fail-closed path... Atomic writes only; no partial state." — the same anchor the sibling task cites; adapted-fit here (that persona nominally covers `add.py`/`add_engine`, not the installer, but its design-for-failure + never-weaken-a-test rules apply directly, matching the sibling's own precedent).
- CONVENTIONS.md: "The Python tool is the only writer of state; writes are atomic (temp + os.replace) and never clobber" — the house rule this task extends from single files to multi-entry/whole-directory writes.
- CONVENTIONS.md (fv59, cited by the sibling too): "a frozen contract that pins a per-twin IMPLEMENTATION mechanism can fail its own INTENT — freeze the OBSERVABLE behavior... not the mechanism."
- CONVENTIONS.md (fv59, from `global-data-restore` itself): "a hermetic unit test that keys on an UNresolved tmp path misses a snapshot keyed on the RESOLVED path on macOS" — `_restore_data` already resolves `project_abspath` internally (`proj = Path(project_abspath).resolve()`); this task's staging logic operates on that SAME resolved path, no new resolution risk introduced.
- The EXISTING, already-FROZEN (from `global-data-restore` v1) `<name>.bak` sidecar is a PERMANENT, user-visible artifact (part of the contracted After-state), not a transient scratch file — this task's new staging mechanism must never confuse the two, nor sweep the permanent `.bak` after a successful call.

Seams consulted: none apply (`.add/SEAMS.md`'s 4 entries — engine-md5-repin, three-tree-parity, scope-token-grammar, phase-body-extraction — cover ADD's own engine/template conventions, not installer atomic-write patterns).

Anchors the contract cites: `_persist_data` · `_restore_data` · `_is_user_data` (extended) · their `cli.js` twins `persistData` / `restoreData` / `isUserData` — the only symbols §3 freezes; `install()` / `_update_global()` and their JS twins change behavior only as an observable consequence of the hardening (zero edits), the same convention the sibling task uses for its own callers.

Issues/Risks (→ feed §1):
1. Core bug, both functions: a wipe/overwrite-then-copy-to-final-name step is not atomic. `_persist_data` wipes the WHOLE snapshot directory then rebuilds it in place; `_restore_data` copies each entry's new content DIRECTLY onto its final name (after, in the force case, safely renaming the original to `.bak` first). Either way, a crash mid-copy leaves the write target a partial mix — worse than either the before- or after-state.
2. Same portability ceiling as the sibling task: no portable single-syscall atomic swap of an EXISTING non-empty directory exists (POSIX `rename(2)` / Windows `MoveFileEx` both require the target be absent-or-empty). The achievable guarantee is "never observed half-composed," not "never observed momentarily absent."
3. A NEW scratch-sibling collision risk this task's own fix would introduce if left unaddressed: `_restore_data`'s per-entry staging sibling must live INSIDE `.add/` (a same-parent requirement, for the commit rename to be atomic) — `_is_user_data`'s exact-name/pattern filter does not recognize it, so a stale one (left by a hard crash) would be scanned as legitimate user-data by a LATER `_persist_data` call. Unlike the sibling task's own version of this same risk (its disclosed Issue #4, which relies on same-invocation call ORDER — reconcile always precedes persist — rather than a filter fix), this task closes it directly by extending `_is_user_data` (already one of this task's own cited anchors, so in-scope). Side effect, not claimed as this task's job: reusing the identical `.add-tmp-`/`.add-bak-` marker convention the sibling's own §3 specifies for `_clean_replace` means this same fix incidentally also excludes a stale `_clean_replace`-created scratch sibling, since both mechanisms would deposit siblings inside the same `.add/` — named here for whoever builds either task, not a cross-task dependency.
4. `_persist_data`'s own new scratch sibling lives in `home/data/` (a sibling of `home/data/<key>` itself), a directory `_is_user_data` never scans — no analogous collision there. `_prune_data`'s existing "any dir under `home/data/` not in `live`" rule already, harmlessly, sweeps a stale persist-scratch as an incidental bonus (confirmed by reading `_prune_data`'s body; no change needed to it).
5. `_persist_data`'s CURRENT "zero entries to persist" path returns `False` BEFORE ever touching `dest` — a project whose snapshot at `home/data/<key>` was created by an earlier successful persist, but which now has NO user-data at all, is left with that STALE snapshot completely untouched by a later empty persist call. This is existing, pre-task behavior, genuinely different from `_clean_replace`'s "always wipe, even for an empty src" — this task PRESERVES it exactly (flagged so the new whole-tree-staging mechanism doesn't accidentally "improve" it into an always-wipe).
6. `cli.js:fail()` (same as the sibling's own Issue #8) calls `process.exit(1)` directly, skipping pending `finally` blocks — `persistData`/`restoreData` never call `fail()` internally today (only their callers do, after catching a thrown error); this task's new stage/commit code inside those two functions must keep that precedent (`throw` real `Error`s only).
7. Two concurrent, lock-less `install`/`update` processes racing on the SAME `.add/` or the SAME `home/data/<key>` is explicitly out of scope — owned by this milestone's lock/concurrency-focused sibling(s), mirroring the sibling task's own identical carve-out.

Related intent:
- `.add/personas/methodology-engine-dev.md` Critical Rules: "Design for failure... Atomic writes only; no partial state" (the invariant this task fulfills for the user-data persist/restore path).
- Milestone `install-update-hardening` goal: "add.py init/update... survive a crash or a concurrent run without leaving a half-written .add/ tree or a wedged lock" — this task delivers the "survive a crash... without a half-written [snapshot/entry]" half for the user-data path specifically (the sibling `project-scope-atomic-reconcile` delivers the same half for the managed-tree reconcile path).
- `global-data-restore`'s own §7 Spec delta (evidence: its refute-read's named Holes 1/2/3) is this task's literal origin.
- GLOSSARY.md: no existing entry for "stage-then-commit" / "scratch sibling" / "self-heal" — established internal code vocabulary (via the sibling task), not a formal domain term; this task doesn't promote one either (§3 Glossary deltas: none).

Ground SHA: c8d373a

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: crash-safe mid-write atomicity for `_persist_data`/`persistData` + `_restore_data`/`restoreData` (the user-data snapshot/restore path), plus 2 committed test gaps (directory `--force`, real npm behavioral parity).
Framings weighed: per-function-shaped stage-then-commit — WHOLE-TREE staging for `_persist_data` (mirrors `_clean_replace` exactly, its dest `home/data/<key>` is self-owned) + PER-ENTRY staging for `_restore_data` (dest `.add/` is a SHARED directory most of which this function must leave alone) (chosen) · one uniform whole-tree stage for BOTH, via a full `.add/` copy (rejected — every restore call would swap the ENTIRE `.add/`, including `tooling/add.py` itself, just to fill in a few entries; a far larger blast radius and crash window than today) · one uniform per-entry stage for BOTH (rejected for persist — its self-owned dest gains nothing from per-entry granularity over the simpler, already-designed whole-tree sibling pattern)
Must:
<must>
  - M1 (persist, whole-tree stage): `_persist_data`/`persistData` copies its (already `_is_user_data`-filtered) entries into a freshly created, uniquely-named directory that is a SIBLING of `home/data/<key>` in the SAME parent (`home/data/`); `home/data/<key>` itself is not opened for writing or deletion during this step.
  - M2 (persist, commit): `home/data/<key>` is updated by a two-step, same-parent rename commit that never targets an already-existing name: (a) if `home/data/<key>` currently exists, rename it aside to a fresh, uniquely-named backup sibling; (b) rename the staged directory onto `home/data/<key>`'s path. The old snapshot (now at the backup path) is removed only STRICTLY AFTER (b) has landed.
  - M3 (persist, self-heal): every `_persist_data`/`persistData` call begins by self-healing any scratch sibling of `home/data/<key>` left by an earlier INTERRUPTED call — a stale backup found while `home/data/<key>` is currently absent is restored onto its path FIRST (recovering the last-known-good snapshot fast, since nothing else re-derives it on a routine cadence); any stale staging directory is discarded outright (never merged/reused). Mirrors the sibling task's own self-heal exactly, same shape and reasoning (persist's snapshot has no other live source to fall back to — closer to the sibling's own `add.py`-availability concern than to restore's case below).
  - M4 (persist, failure containment): a failure while staging leaves `home/data/<key>` completely untouched (still absent, or still its exact prior content) and removes the partial staged directory, the exception still propagating; a failure during the commit rolls back what it safely can (if the aside-rename already landed but the swap-in rename then fails, the backup is renamed back onto `home/data/<key>`'s path before the error propagates).
  - M5 (persist, unchanged behavior): the "zero entries to persist" path is UNCHANGED — `_persist_data`/`persistData` returns `False` WITHOUT ever touching `home/data/<key>` when there is nothing to persist, exactly matching today's behavior; a deliberate preservation, not something this task "improves" into an always-wipe.
  - M6 (restore, per-entry stage): for EACH `_is_user_data`-filtered snapshot entry being written (a fill-gaps write into an absent target, or a `--force` overwrite of a present one), `_restore_data`/`restoreData` first copies that ONE entry — honoring the existing symlink-dereference-to-content rule, unchanged — into a freshly created, uniquely-named sibling of the entry's own final name, inside `.add/` (same parent, so the commit rename is same-filesystem); the entry's final name is not opened for writing during this step.
  - M7 (restore, commit — fill-gaps, entry absent): the staged entry is landed by ONE same-parent rename onto the entry's final (currently-absent) name.
  - M8 (restore, commit — force, entry present): landing is a two-step, same-parent rename that never targets an already-existing name: (a) rename the present entry aside onto its EXISTING, already-contracted `<name>.bak` path (replacing a stale `.bak` first, exactly as today — the UNCHANGED, permanent, user-visible sidecar, never the new transient staging marker); (b) rename the staged entry onto the entry's now-freed final name. If (b) fails after (a) succeeded, `.bak` is renamed back onto the entry's final name before the error propagates, so that ONE entry ends exactly where it started.
  - M9 (restore, failure containment): a failure while staging ONE entry leaves that entry's current state (absent, or its exact prior content) untouched and removes the partial staged sibling, the exception propagating — entries already committed in EARLIER iterations of the SAME call stay committed (this task does not make the whole multi-entry loop one all-or-nothing transaction — see the lowest-confidence flag).
  - M10 (restore, self-heal): every `_restore_data`/`restoreData` call begins by sweeping any stale per-entry staging sibling left by an earlier INTERRUPTED call (discarded outright, never merged/reused/completed) — DELIBERATELY SIMPLER than persist's M3 / the sibling's own richer recovery: restore does not attempt to recover or complete an interrupted commit, because the untouched, read-only snapshot at `home/data/<key>` is always still there, so the VERY NEXT restore call naturally re-derives the correct end state for that entry via its own ordinary fill-gaps-or-force logic — unlike `add.py`/`tooling` (executable, possibly invoked by something else at any instant) or `home/data/<key>` (persist's only copy outside the live project), a momentarily-absent user-data entry between one restore call and the next carries no comparable urgency.
  - M11 (`_is_user_data` extension): `_is_user_data`/`isUserData` additionally excludes any name carrying the reserved scratch-staging marker (the same `.add-tmp-`/`.add-bak-`-infix convention `project-scope-atomic-reconcile`'s own §3 specifies for `_clean_replace`) — so a stale scratch sibling left inside `.add/` by an interrupted `_restore_data` call (or, incidentally, by `_clean_replace`) is never mistaken for real user-data by a LATER `_persist_data` scan or a later `_restore_data` re-entrant scan.
  - M12 (unchanged surface): signatures, return contracts (`_persist_data`/`persistData` -> bool "persisted-or-not"; `_restore_data`/`restoreData` -> bool "was >=1 entry ACTUALLY written, honoring fill-gaps skips"), and the final on-disk CONTENT for every existing scenario (byte-copy, symlink-deref, fill-gaps skip, `.bak` sidecar semantics) are UNCHANGED — this task changes ONLY the crash-safety of how each target gets there. `install()`, `_update_global()`, and their `cli.js` twins need ZERO edits; every existing test in `test_global_restore.py`, `test_global_data.py`, `test_global_update_harden.py`, `test_global_install.py` stays green untouched.
  - M13 (both twins): `_persist_data`/`persistData` and `_restore_data`/`restoreData` guarantee the SAME observable staged-commit behavior on both twins, each using native primitives (`tempfile`/`os.replace` vs `fs.mkdtempSync`/`fs.renameSync`); internal `cli.js` failures inside the new stage/commit region `throw` real `Error`s, never call `fail()` (which calls `process.exit(1)` directly, skipping `finally`).
  - M14 (test gap — directory `--force`): commit a NEW test exercising `--force` restore on a DIRECTORY entry (e.g. `tasks/` -> `tasks.bak/`), covering what was previously only manually verified at a prior gate.
  - M15 (test gap — real npm behavioral parity): replace/extend `ParityRestoreTest` (today 6 bare `assertIn` string checks) with a `shutil.which("node")`-gated subprocess smoke that actually RUNS `node cli.js init --from-global-data [--force]` and `prune-data [--force]` and asserts real stdout/exit-code/filesystem effects, mirroring `test_global_update_harden.py`'s established pattern.
</must>
Reject:
<reject>
  (internal functions + 2 test-only additions; NO new user-facing error code — `data_unwritable`/`restore_failed`/`no_global_home` keep their existing meaning. "Reject" here names the guaranteed observable POST-STATE for each failure/interruption situation, mirroring the sibling task's own framing.)
  - persist: staging fails -> `home/data/<key>` left byte-for-byte exactly as it was before the call -> "persist_stage_failure_untouched"
  - persist: commit step (a) (rename-aside) fails -> `home/data/<key>` unchanged (single syscall either fully happened or didn't), staged dir cleaned up -> "persist_commit_aside_failure_unchanged"
  - persist: commit step (b) (rename-in) fails AFTER (a) succeeded -> the backup is renamed back onto `home/data/<key>`'s path before the error propagates -> "persist_commit_land_failure_rolls_back"
  - persist: a hard crash between commit (a) and (b) -> the VERY NEXT `_persist_data`/`persistData` call for that key self-heals (restores the backup first) -> "persist_stale_backup_self_heals_next_call"
  - restore: staging ONE entry fails -> that entry's current state (absent, or its exact prior content) is untouched, the partial staged sibling is removed, exception propagates; entries already committed earlier in the SAME loop stay committed -> "restore_entry_stage_failure_untouched"
  - restore: commit step (b) (staged->final-name) fails on a FORCE entry AFTER step (a) (original->`.bak`) succeeded -> `.bak` is renamed back onto the entry's final name before the error propagates, so that entry ends exactly where it started -> "restore_entry_commit_land_failure_rolls_back"
  - restore: a hard crash leaves a stale per-entry staging sibling -> the VERY NEXT call for that entry sweeps it unconditionally (never merged/reused/completed) and the ordinary fill-gaps-or-force logic re-derives the correct end state -> "restore_entry_stale_stage_swept_next_call"
  - a stale scratch sibling (from persist, restore, or `_clean_replace`) inside `.add/` is scanned by `_is_user_data`/`isUserData` -> excluded, never snapshotted as user-data -> "scratch_sibling_excluded_from_user_data"
  - two concurrent, lock-less callers racing on the SAME `home/data/<key>` or the SAME `.add/` entry -> explicitly OUT of scope; this task makes no guarantee about which writer wins, only that EACH writer's own target is never observed half-composed from its own copy — the real fix is owned by this milestone's lock/concurrency-focused sibling task(s), ruled out on purpose, not a silent gap.
</reject>
After:
<after>
  - `home/data/<key>` (persist) and every restored `.add/` entry (restore) hold exactly the same final content as today's contract, for every EXISTING scenario (byte-copy, symlink-deref, fill-gaps skip, `.bak` sidecar) — unchanged.
  - no scratch sibling (staging or backup) of `home/data/<key>`, or of any restored entry, survives a SUCCESSFUL call.
  - at most one scratch sibling per target can survive an unsuccessful/interrupted call, and it is self-healed (persist: restored-from-or-discarded; restore: discarded) by the very next call touching that SAME target — never accumulates across repeated crashes.
  - `install()`, `_update_global()`, and their `cli.js` twins are unchanged (zero edits); every existing test across the 4 files named in M12 stays green with no edits.
  - `test_global_restore.py` gains a passing directory-`--force` test and a genuinely behavioral (not just structural) npm parity smoke.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ A1 (lowest confidence): `_restore_data`'s multi-entry loop is NOT wrapped in one all-or-nothing transaction — each entry gets its own atomic stage-then-commit, but a failure on entry N of M (per the origin follow-up's own framing) leaves entries 1..N-1 already landed and N+1..M untouched — read as "no partial ENTRY," not "no partial SET." Lowest confidence because a stricter reading of the origin wording could mean "the whole restore call is one transaction" (already ruled out in Framings weighed on blast-radius grounds). If wrong: a bigger, riskier redesign, not a small addition — needs an explicit go-ahead.
  ⚠ A2: `_persist_data`/`persistData` is folded INTO this task's scope (not left for a separate task) — the same defect class, and its dest maps EVEN MORE cleanly onto the sibling's already-designed whole-tree pattern than restore's own per-entry design does. If wrong (the human wanted it split out): this task's scope shrinks by roughly a third (M1-M5), cheap to separate since M1-M5 don't entangle with M6-M11.
  - [ ] A3: restore's SIMPLER (sweep-only, no-recovery) self-heal (M10) is the right choice, diverging from the sibling's richer restore-the-backup self-heal — justified by "the untouched snapshot lets the next call re-derive," a genuinely different situation from `_clean_replace`'s `add.py`-availability concern; if wrong (the human wants restore's self-heal to also proactively recover an interrupted commit for consistency), the change is small and additive (mirror persist's M3 recovery step at the per-entry level).
  - [ ] A4: extending `_is_user_data`/`isUserData` (M11) is accepted as in-scope even though `_is_user_data` is not one of the two functions named in this task's own title — justified because it's a direct, small, necessary consequence of M6's own new staging siblings living inside `.add/`, and `_is_user_data` was already a cited Ground anchor; if wrong (the human wants this deferred/flagged instead), the fallback is the sibling's own weaker "relies on call order" posture, disclosed as residual risk rather than closed.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: a fresh snapshot is fully materialized via stage-then-commit   # M1, M2, M12
  Given no snapshot yet exists at home/data/<key>
  And the project's .add/ holds user-data entries PROJECT.md, state.json, tasks/
  When I call _persist_data(home, project) / persistData(home, project)
  Then home/data/<key> ends up containing exactly those entries, byte-for-byte
  And no staging or backup scratch sibling remains next to home/data/<key> afterward

Scenario: an existing snapshot is refreshed via stage-then-commit, never wiped in place   # M1, M2, M12
  Given home/data/<key> already holds a prior snapshot
  And the project's .add/ now holds different user-data content
  When I call _persist_data(home, project) / persistData(home, project)
  Then home/data/<key> ends up containing exactly the new content
  And at no point does a caller observe home/data/<key> missing files that were unchanged between the prior and new snapshot
  And no staging or backup scratch sibling remains afterward

Scenario: zero entries to persist leaves an existing snapshot completely untouched   # M5
  Given home/data/<key> holds a snapshot from an earlier successful persist
  And the project's .add/ now has NO user-data entries at all
  When I call _persist_data(home, project) / persistData(home, project)
  Then the call returns False
  And home/data/<key> is byte-unchanged (not wiped, not touched at all)

Scenario: a mid-stage persist failure leaves the snapshot exactly as it was   # M4, Reject persist_stage_failure_untouched
  Given home/data/<key> holds known prior content (or does not exist)
  And a simulated failure partway through copying the filtered entries into the staging sibling
  When I call _persist_data(home, project) / persistData(home, project)
  Then the call raises/throws the underlying error
  And home/data/<key> still holds its exact prior content (or is still absent), never partially overwritten
  And no partial staging directory survives the call

Scenario: a persist commit-aside failure leaves the snapshot unchanged   # M4, Reject persist_commit_aside_failure_unchanged
  Given home/data/<key> holds known prior content and staging has fully succeeded
  And the commit's first rename (home/data/<key> -> backup sibling) is simulated to fail
  When _persist_data / persistData runs its commit step
  Then the call raises/throws the underlying error
  And home/data/<key> is unchanged (the rename never happened)
  And the staged directory is removed before the error propagates

Scenario: a persist commit-land failure rolls back to the original snapshot   # M4, Reject persist_commit_land_failure_rolls_back
  Given home/data/<key> holds known prior content, staging has fully succeeded, and the commit's second rename (staged -> home/data/<key>) is simulated to fail AFTER the first rename (home/data/<key> -> backup) already succeeded
  When _persist_data / persistData runs its commit step
  Then the call raises/throws the underlying error
  And home/data/<key> is restored to hold its exact original content (the backup was renamed back)
  And no staging or backup scratch sibling survives the call

Scenario: a stale persist backup self-heals an absent snapshot on the next call   # M3, Reject persist_stale_backup_self_heals_next_call
  Given home/data/<key> does NOT currently exist, but a scratch sibling matching the reserved backup pattern sits next to it holding the last known-good snapshot (simulating a crash between the two commit renames on a PRIOR call)
  When I call _persist_data(home, project) / persistData(home, project) again
  Then home/data/<key> is first restored to the backup's content (self-heal), then updated to the fresh content by this call's own normal stage-then-commit
  And no backup scratch sibling survives the call

Scenario: a stale persist staging leftover is swept before new staging begins   # M3
  Given a scratch directory matching this key's OWN staging-name pattern already sits in home/data/ (simulating a crash mid-copy on a PRIOR call), and home/data/<key> holds its normal current content
  When I call _persist_data(home, project) / persistData(home, project) again
  Then the stale staging leftover is gone after the call (never merged into the result)
  And home/data/<key> ends up holding exactly the fresh content, same as the normal-success scenario

Scenario: fill-gaps restores one absent entry via a single-rename commit   # M6, M7, M12
  Given the snapshot holds SOUL.md and the target .add/ does not have SOUL.md yet
  When I call _restore_data(home, project) / restoreData(home, project) (no force)
  Then SOUL.md is restored, byte-identical to the snapshot
  And no staging sibling of SOUL.md survives the call

Scenario: --force restores one present entry, backing the original up first, via a two-rename commit   # M6, M8, M12
  Given the snapshot holds PROJECT.md (content "HOME") and the target .add/ already has PROJECT.md (content "LOCAL")
  When I call _restore_data(home, project, force=True) / restoreData(home, project, true)
  Then PROJECT.md now reads "HOME"
  And PROJECT.md.bak reads "LOCAL" (the same permanent, contracted sidecar name as today)
  And no NEW transient staging sibling of PROJECT.md survives the call

Scenario: --force on a DIRECTORY entry is backed up and replaced the same way   # M6, M8, M14
  Given the snapshot holds a tasks/ directory and the target .add/ already has a DIFFERENT tasks/ directory
  When I call _restore_data(home, project, force=True) / restoreData(home, project, true)
  Then tasks/ now holds exactly the snapshot's content
  And tasks.bak/ holds exactly the original local content, byte-for-byte
  And this scenario is now covered by a COMMITTED test (test_global_restore.py), not just a manual gate check

Scenario: a mid-stage restore failure on one entry leaves it untouched while earlier-committed entries survive   # M9, Reject restore_entry_stage_failure_untouched
  Given the snapshot holds two entries A and B, both absent locally, and a simulated failure occurs partway through staging entry B (entry A already landed in an earlier loop iteration)
  When I call _restore_data(home, project) / restoreData(home, project)
  Then the call raises/throws the underlying error
  And entry A is present in .add/ (already committed, stays committed)
  And entry B is still absent (its partial staging sibling was removed, nothing landed at B's final name)

Scenario: a restore commit-land failure on a force entry rolls .bak back onto that one entry   # M9, Reject restore_entry_commit_land_failure_rolls_back
  Given the snapshot holds PROJECT.md, the target already has PROJECT.md present, staging has fully succeeded, and the commit's second rename (staged -> PROJECT.md) is simulated to fail AFTER the first rename (PROJECT.md -> PROJECT.md.bak) already succeeded
  When _restore_data / restoreData runs this entry's commit step
  Then the call raises/throws the underlying error
  And PROJECT.md is restored to hold its exact original content (PROJECT.md.bak was renamed back)
  And no staging sibling of PROJECT.md survives the call

Scenario: a stale per-entry staging leftover is swept and the next call re-derives correctly   # M10, Reject restore_entry_stale_stage_swept_next_call
  Given a scratch sibling matching PROJECT.md's own staging-name pattern already sits in .add/ (simulating a crash mid-copy on a PRIOR restore call), and PROJECT.md itself is absent (the interrupted call never landed it)
  When I call _restore_data(home, project) / restoreData(home, project) again
  Then the stale staging leftover is gone after the call
  And PROJECT.md ends up holding exactly the snapshot's content, via this call's own ordinary fill-gaps logic (no special recovery step was needed)

Scenario: a snapshot symlink is still dereferenced to content through the new staging step   # M6 edge case, ties M12
  Given the snapshot holds a regular file note.md and a symlink link.md -> note.md
  When I call _restore_data(home, project) / restoreData(home, project)
  Then target note.md is byte-identical to the snapshot
  And target link.md is a regular file holding note.md's content (not a symlink), exactly as before this task

Scenario: a fresh --force restore replaces a stale permanent .bak from an earlier interrupted run, never merges it   # edge case named at Ground, ties M8
  Given a stale PROJECT.md.bak already exists (left over from an earlier force-restore) and the target now has a NEW PROJECT.md present
  When I call _restore_data(home, project, force=True) / restoreData(home, project, true) again
  Then the stale PROJECT.md.bak is replaced (not merged with) by a fresh backup of the CURRENT PROJECT.md content
  And PROJECT.md ends up holding the snapshot's content

Scenario: a scratch sibling is excluded from _is_user_data in either direction   # M11, Reject scratch_sibling_excluded_from_user_data
  Given a stale scratch directory matching the reserved .add-tmp-/.add-bak- marker sits inside a project's .add/ (left by an interrupted restore, or by _clean_replace)
  When _persist_data / persistData scans that .add/ for user-data entries to snapshot
  Then the scratch sibling is excluded from the entries list
  And a subsequent restore call's own re-entrant scan likewise never treats it as a real, present entry

Scenario: both twins guarantee the same staged-commit behavior under a simulated failure   # M13
  Given the same simulated mid-copy failure applied once to the Python _persist_data (or _restore_data) call and once to the Node persistData (or restoreData) call via `node bin/cli.js`
  When each twin's staging step fails
  Then both twins leave their own target byte-for-byte untouched and remove their own partial staging sibling
  And a structural check confirms both source files carry the same staged-commit call-site shape (self-heal -> stage -> commit-by-rename -> sweep), not just the same function names

Scenario: a zero-entry snapshot is an honest no-op, unaffected by the new mechanism   # edge case, ties existing After / no_snapshot behavior
  Given home/data/<key> is absent, or exists but holds no _is_user_data entries
  When I call _restore_data(home, project) / restoreData(home, project)
  Then the call returns False without ever creating a staging or backup sibling
  And .add/ is left exactly as it was (a caller-facing "nothing to restore" skip, not a reject)

Scenario: the real npm behavioral smoke proves restore + prune actually run, not just token-present   # M15
  Given a global home with a snapshot for the target project, and node available on PATH
  When the test runs `node cli.js init --from-global-data`, `node cli.js prune-data`, and `node cli.js prune-data --force`
  Then the restore subprocess's real stdout/exit-code AND the target's filesystem content are asserted (not merely that "restoreData"/"pruneData" appear as substrings in cli.js)
  And the OLD ParityRestoreTest's string-only assertions are subsumed or replaced, not left as the only npm coverage

Scenario: two concurrent, lock-less callers racing on the same target — ruled out on purpose   # Reject concurrent runs, concurrency edge case
  Given two processes both invoke _persist_data/persistData (or _restore_data/restoreData) for the SAME home/data/<key> (or the same .add/ entry) at overlapping times, with no lock held
  When both stage independently and then race to commit
  Then this task makes NO guarantee about which writer's content ultimately wins the race
  And this task DOES guarantee neither writer's own target is ever observed half-composed from ITS OWN copy
  And this is a deliberate, disclosed non-goal recorded here — not a silently missed case — with the real fix owned by this milestone's lock/concurrency-focused sibling task(s)
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
crash-safe persist/restore  [internal helpers, no new CLI surface]
  _persist_data(home: Path, project_abspath) -> bool                       # signature UNCHANGED
  _restore_data(home: Path, project_abspath, *, force: bool = False) -> bool  # signature UNCHANGED
  _is_user_data(name: str) -> bool                                         # EXTENDED (step below)
  persistData(home, projectAbspath) · restoreData(home, projectAbspath, force) ·
  isUserData(name)                                                        # cli.js twins, UNCHANGED signatures
  Callers unchanged (zero edits, reach these targets ONLY through these functions):
    install() / cmdInit · _update_global() / cmdUpdateGlobal

### _persist_data / persistData — WHOLE-TREE stage-then-commit (mirrors _clean_replace/cleanReplaceTree)
  0. SELF-HEAL (start of every call, before this call's own work):
       tmp_stale = any pre-existing sibling of home/data/<key> matching "<key>.add-tmp-*"
       bak_stale = any pre-existing sibling matching "<key>.add-bak-*"
       if home/data/<key> is ABSENT and a bak_stale exists -> rename it onto <key>'s path first
         (recovers the last known-good snapshot; >1 candidate is a defensive tie-break, not an
         expected path — the most-recently-modified one is authoritative)
       remove any remaining tmp_stale / bak_stale siblings
  1. FILTER: entries = _is_user_data-filtered top-level names under <project>/.add   # UNCHANGED rule
     -> if entries is empty: return False WITHOUT touching home/data/<key> at all   # UNCHANGED —
        an existing stale snapshot from an earlier persist is left exactly as-is, never wiped
  2. STAGE: create a fresh, uniquely-named directory sibling of home/data/<key>, IN home/data/
       ("<key>.add-tmp-<token>"); copy every filtered entry into it in full
       -> on ANY exception: remove the staged directory, re-raise. home/data/<key> was never
          opened for writing in this step, so it is provably whatever it was before the call.
  3. COMMIT — two same-parent renames, neither targets an already-existing name:
       a. if home/data/<key> exists: rename it -> a fresh "<key>.add-bak-<token>" sibling
       b. rename the staged directory -> home/data/<key>'s path
       -> if (a) raises: staged dir removed, home/data/<key> untouched, re-raise.
       -> if (b) raises (a already landed): rename the backup back onto home/data/<key>, remove
          the staged dir, re-raise. A hard CRASH between (a) and (b) is NOT rolled back
          synchronously — the NEXT call's step 0 recovers it.
  4. SWEEP: remove the backup sibling from step 3a — only after 3b has landed.
     returns True (entries were persisted)                                 # UNCHANGED return semantics

### _restore_data / restoreData — PER-ENTRY stage-then-commit (.add/ is a SHARED directory; whole-
### tree staging would swap in the ENTIRE .add/ — including tooling/add.py — on every call)
  0. SELF-HEAL (start of every call, before this call's own work): for every name under
       <project>/.add, any sibling matching "<name>.add-tmp-*" is a stale leftover from an
       earlier INTERRUPTED call — remove it unconditionally (never merged/reused/completed; the
       untouched snapshot lets this call's own ordinary logic below re-derive the correct end
       state for that entry — no backup-recovery step is needed here, unlike step 0 above).
  1. For each _is_user_data-filtered snapshot entry (sorted, as today):
       a. dest = <project>/.add/<entry-name>. If dest exists (or is a symlink) and NOT force:
          skip — UNCHANGED fill-gaps rule; no staging even begins for a skipped entry.
       b. STAGE: copy this ONE entry (honoring the existing symlinks=False deref-to-content rule,
          UNCHANGED) into a fresh, uniquely-named sibling of dest, IN .add/ ("<entry-name>.add-
          tmp-<token>") — dest's own name is not opened for writing in this step.
          -> on ANY exception: remove the partial staged sibling, re-raise. dest is untouched.
       c. COMMIT:
          - dest exists (force path): replace a stale <entry-name>.bak first (UNCHANGED), rename
            dest -> <entry-name>.bak (the SAME permanent, already-contracted sidecar name as
            today — never a new token-suffixed name), then rename the staged sibling -> dest's
            freed name.
            -> if the second rename fails after the first succeeded: rename <entry-name>.bak
               back onto dest's name before the error propagates (this ONE entry ends exactly
               where it started; entries from earlier loop iterations are unaffected).
          - dest was absent (fill-gaps path): rename the staged sibling -> dest's name directly
            (single rename; no backup needed, nothing existed to preserve).
       d. mark restored = True for this entry.                            # UNCHANGED semantics
  returns restored                                                        # UNCHANGED return semantics
  (an exception on entry N leaves entries 1..N-1, committed earlier in the SAME call, landed;
   entry N and the remaining entries are untouched — this call is NOT one all-or-nothing
   transaction across its whole entry set; see the lowest-confidence flag)

### _is_user_data / isUserData — one new exclusion
  additionally returns False for any name containing the reserved scratch-staging marker
  (".add-tmp-" or ".add-bak-") — a stale sibling left by an interrupted _persist_data,
  _restore_data, OR (incidentally, same marker convention) _clean_replace call is never scanned
  as real user-data by a LATER _persist_data snapshot or a later _restore_data self-heal sweep.

Reject-code post-states (traced to the numbered steps above; no NEW user-facing error code —
  data_unwritable / restore_failed / no_global_home keep their existing meaning):
  persist_stage_failure_untouched              -> persist step 2's exception path
  persist_commit_aside_failure_unchanged        -> persist step 3(a) exception path
  persist_commit_land_failure_rolls_back        -> persist step 3(b) exception path
  persist_stale_backup_self_heals_next_call     -> persist step 0
  restore_entry_stage_failure_untouched         -> restore step 1(b) exception path
  restore_entry_commit_land_failure_rolls_back  -> restore step 1(c) force-path exception branch
  restore_entry_stale_stage_swept_next_call     -> restore step 0
  scratch_sibling_excluded_from_user_data       -> the _is_user_data extension above

Schema / files touched: add-method/src/add_method/_installer.py (_persist_data, _restore_data,
  _is_user_data) · add-method/bin/cli.js (persistData, restoreData, isUserData) ·
  add-method/tooling/test_global_restore.py (M14 directory-force test + M15 behavioral parity —
  test bodies are §4's job, committed here as a Must). No new persisted state, no new CLI flag,
  no new dependency (stdlib tempfile/os/shutil · Node builtin fs/path only). A transient, self-
  cleaning scratch sibling may exist ONLY (a) for the duration of one call's stage/commit window,
  or (b) between an abnormal process termination and the next call touching that SAME target —
  never as steady state; never mistaken for real content by _is_user_data (step above), by
  _prune_data (which harmlessly sweeps a stale persist-scratch as an ordinary orphan — no change
  needed there, confirmed by reading its body), or by anything else that lists home/data/'s or
  .add/'s entries.

INV: home/data/<key> (persist) and each individually restored .add/ entry (restore), observed
     from OUTSIDE these functions at any instant, are always exactly ONE of three states — (a)
     exact prior content, (b) momentarily absent (the sub-instant window between a commit's two
     renames), or (c) the fully-staged final content — NEVER a partial mix of old and new. Same
     achievable-guarantee ceiling as the sibling task (a portable single-syscall atomic replace
     of an EXISTING non-empty directory does not exist; state (b) is real and closed by the NEXT
     call's self-heal, not by this call) — and, as there, a STRICT improvement over today's much
     larger crash window (a whole wipe+rebuild, or a whole direct-to-final-name copy).
INV: every existing scenario's final on-disk CONTENT, both return contracts, and every existing
     caller (install, _update_global, and their cli.js twins) are BYTE-IDENTICAL to before this
     task — a crash-safety mechanism change only.
INV: both twins guarantee the SAME state machine (self-heal -> stage -> commit -> sweep) via each
     platform's own primitives (tempfile.mkdtemp/os.replace vs fs.mkdtempSync/fs.renameSync) —
     mirrors the _update_lock/acquireUpdateLock + _clean_replace/cleanReplaceTree precedent
     (CONVENTIONS.md fv59: freeze the observable behavior, not the mechanism).
INV: restore's per-entry loop is NOT one all-or-nothing transaction across its whole entry set —
     each entry's OWN atomicity is guaranteed; atomicity across the SET is explicitly not (ties
     to the lowest-confidence flag below).

OUT of scope (named, not silently dropped): two concurrent lock-less callers racing on the SAME
  home/data/<key> or the SAME .add/ entry (owned by this milestone's lock/concurrency-focused
  sibling task(s)) · _clean_replace/cleanReplaceTree's own hardening (owned by project-scope-
  atomic-reconcile, read here only as prior art) · a home file-lock for prune-data (named by
  global-data-restore's own §7 as belonging to global-lock-followups, not here) · making the
  whole multi-entry restore loop one all-or-nothing transaction (ruled out — see Framings weighed
  + the lowest-confidence flag).
```

Glossary deltas: none (this task hardens existing internal mechanisms — "stage-then-commit",
  "scratch sibling", "self-heal" are the same internal vocabulary the sibling task already uses
  and declines to promote; "user-data" / "managed tree" are already-established PROJECT.md
  domain concepts, unchanged by this task).

Least-sure flag surfaced at freeze:
  ⚠ [spec] A1 — restore's per-entry loop is NOT one all-or-nothing transaction across the whole
    multi-entry call (a failure on entry N leaves 1..N-1 committed, N+1..M untouched) — read from
    the origin delta's "no partial restore" as PER-ENTRY atomicity, not WHOLE-CALL atomicity; the
    whole-call alternative was considered and rejected (would require staging a full .add/ copy,
    a much larger blast radius — see Framings weighed). If the human meant whole-call atomicity,
    this is a materially bigger redesign, not a small follow-up — needs an explicit go-ahead.
  ⚠ [contract] A2 — restore's self-heal is deliberately SIMPLER than persist's (sweep-only, no
    backup-recovery step), diverging from the sibling task's richer recovery — justified by
    restore's untouched read-only snapshot letting the next call re-derive the correct state,
    unlike persist (no other live copy) or _clean_replace (add.py's own executability). If the
    human wants restore's self-heal to also proactively recover an interrupted commit for
    consistency, the change is small and additive (mirror persist's step 0 at the per-entry
    level) — flagging so the simpler choice is a conscious freeze decision, not an assumed one.

Status: FROZEN @ v1 — approved by Tin Dang

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 100% of the 21 §2 scenarios + every M1-M15 + every named Reject-code exercised by a passing test (19 new methods + 4 reused pre-existing, confirmed non-vacuous by tracing each against the OLD implementation).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_persist_fresh_snapshot_stage_then_commit: fresh snapshot fully materialized · covers: M1,M2,M12
  - test_persist_refresh_never_wiped_in_place: existing snapshot refreshed, dest never rmtree'd in place · covers: M1,M2,M12
  - test_persist_zero_entries_leaves_existing_snapshot_untouched: 0 entries -> False, byte-unchanged · covers: M5
  - test_persist_mid_stage_failure_leaves_snapshot_untouched: mid-stage copyfile raises -> dest untouched · covers: M4, R:persist_stage_failure_untouched
  - test_persist_commit_aside_failure_leaves_snapshot_unchanged: rename(dest,backup) raises -> dest unchanged · covers: M4, R:persist_commit_aside_failure_unchanged
  - test_persist_commit_land_failure_rolls_back: rename(staged,dest) raises after aside landed -> rollback · covers: M4, R:persist_commit_land_failure_rolls_back
  - test_persist_stale_backup_self_heals_next_call: stale `.add-bak-*` + absent dest -> self-heal recovers then updates · covers: M3, R:persist_stale_backup_self_heals_next_call
  - test_persist_stale_staging_swept_before_new_staging: stale `.add-tmp-*` swept, fresh content lands · covers: M3
  - fill-gaps restores one absent entry (EXISTING test_restore_rehydrates_fresh_clone + test_fill_gaps_never_clobbers_present, re-confirmed green post-hardening) · covers: M6,M7,M12
  - --force restores one present entry with .bak (EXISTING test_force_overwrites_with_bak, file-only, re-confirmed green) · covers: M6,M8,M12
  - test_restore_force_directory_entry_backed_up_and_replaced: --force on a DIRECTORY entry -> tasks.bak/ · covers: M6,M8,M14
  - test_restore_mid_stage_failure_earlier_committed_entries_survive: entry B staging fails (PARTIAL-GARBAGE-then-raise mock) -> A stays committed, B absent not corrupted · covers: M9, R:restore_entry_stage_failure_untouched
  - test_restore_commit_land_failure_on_force_entry_rolls_back_bak: 2nd os.replace raises -> .bak rolled back onto entry · covers: M9, R:restore_entry_commit_land_failure_rolls_back
  - test_restore_stale_per_entry_staging_swept_next_call_rederives: stale `<name>.add-tmp-*` swept, ordinary fill-gaps re-derives · covers: M10, R:restore_entry_stale_stage_swept_next_call
  - symlink still dereferenced to content (EXISTING test_symlinks_dereferenced, re-confirmed green through the new staging step) · covers: M6 edge case, M12
  - test_restore_fresh_force_replaces_stale_bak_never_merges: stale .bak REPLACED by a fresh backup of current content, not merged · covers: edge case, M8
  - test_is_user_data_excludes_scratch_markers_directly + test_scratch_sibling_excluded_from_persist_and_restore_scans: `.add-tmp-`/`.add-bak-` excluded in both directions · covers: M11, R:scratch_sibling_excluded_from_user_data
  - test_parity_call_site_shape: both twins carry the same self-heal->stage->commit->sweep call-site shape (mkdtemp(dir=.../mkdtempSync(path.join(, os.replace(str(staged).../fs.renameSync(staged, scratch-marker tokens) · covers: M13
  - test_restore_zero_qualifying_entries_is_honest_noop (+ EXISTING test_nothing_to_restore_returns_false): 0 qualifying entries -> False, .add/ never even created · covers: edge case, existing After/no_snapshot behavior
  - test_npm_restore_and_prune_behavioral_smoke: real `node cli.js init --from-global-data` + `prune-data`/`prune-data --force` subprocess, real stdout/exit-code/filesystem asserted · covers: M15
  - test_persist_two_interleaved_calls_land_one_full_valid_snapshot: a nested full 2nd call inside the 1st's staging window -> outer may itself raise (tolerated), final content is ONE caller's full content never a mix, no scratch survives · covers: Reject concurrent runs (disclosed non-goal)
</test_plan>

Tests live in: `add-method/tooling/test_global_restore.py` · MUST run red (missing implementation) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/src/add_method/_installer.py` `add-method/bin/cli.js` `add-method/tooling/test_global_restore.py`
Strategy (ordered batches): 1. `_persist_data` (Python): add the step-0 self-heal (sweep/restore `<key>.add-tmp-*`/`<key>.add-bak-*` siblings under `home/data/`), then replace the direct `rmtree`+rebuild with: stage filtered entries into `tempfile.mkdtemp(dir=str(home/"data"), prefix=key+".add-tmp-")`, commit via same-parent renames (dest-aside to `.add-bak-<token>` if it exists, then staged-in), sweep the backup only after the land succeeds. Preserve the "zero entries → return False, untouched" early-return exactly as today. 2. `_restore_data`: add its own step-0 self-heal (sweep any stale `<entry>.add-tmp-*` sibling inside `.add/`), then change the per-entry write so it stages into a fresh `<entry-name>.add-tmp-<token>` sibling first — fill-gaps path commits via one rename onto the (absent) final name; force path keeps the existing `dest → <name>.bak` rename, then rename staged → dest, rolling `.bak` back onto dest if the second rename fails. 3. `_is_user_data`: add one more exclusion for names containing `.add-tmp-`/`.add-bak-`. 4. Mirror all 3 in `cli.js` (`persistData`/`restoreData`/`isUserData`) via `fs.mkdtempSync`/`fs.renameSync`/`fs.rmSync` — internal failures `throw` real `Error`s, never call `fail()`. 5. Extend `test_global_restore.py`: mid-stage/mid-commit failure + self-heal scenarios for both functions, the missing directory-`--force` test (M14), and a `shutil.which("node")`-gated behavioral subprocess smoke for restore+prune replacing/extending `ParityRestoreTest`'s string-only checks (M15) — do not weaken or remove any existing v1-frozen assertion.

Persona (optional): methodology-engine-dev
Known-problem fixes: `cli.js:fail()` calls `process.exit(1)` directly (skips `finally`) → new stage/commit code in `persistData`/`restoreData` must `throw`, never call `fail()` · `shutil.copytree`'s target must be an EMPTY pre-existing dir for `dirs_exist_ok=True` — `tempfile.mkdtemp` already guarantees that · staging MUST live inside the same parent as its target (`home/data/` or `.add/`) or the commit rename becomes cross-filesystem and silently degrades to a slow, non-atomic copy+delete.
Strategy actually used: Largely as planned, with 2 deliberate deviations. (1) §4 TESTS was written and committed as its OWN standalone, confirmed-RED commit BEFORE any implementation batch began (`bdbc373`) — the listed strategy names 5 build-oriented batches without saying whether tests land before or interleaved with them; TDD discipline put the full red suite first, verified 12/36 new tests failing for the traced right reason (missing self-heal/stage/commit/rollback/exclusion logic) and 0 regressions in the other 24 (17 pre-existing + 3 happy-path/preserved-behavior + 1 disclosed-non-goal case, each traced against the OLD implementation to confirm non-vacuity) before touching `_installer.py`. (2) Batches 1-3 (`_persist_data`, `_restore_data`, `_is_user_data`) were implemented together in ONE pass in `_installer.py` (plus a new shared `_sweep_scratch` helper) rather than as 3 separate sequential edits, since all three share that helper and the self-heal/stage/commit shape; batch 4 (cli.js mirror) followed as a second pass once the Python side was green. Suite went RED (12/36) -> GREEN (36/36 + 39/39 siblings) in one implementation pass per language, committed as a single green commit (`a3b832f`) separate from the red commit, so git history shows genuine red-then-green, not a squash. Additionally ran a throwaway, uncommitted manual smoke (real `node cli.js init --global-data` against a real project, twice — fresh commit then refresh/2-rename commit) to close a self-identified gap: no existing or new COMMITTED test exercises persistData's own happy path via a real node subprocess (the frozen M15 scope names only restore+prune for the real-subprocess treatment); did not add this as new committed test scope since the contract's own M15/scenario deliberately named only restore+prune — flagged as a §7 Spec delta candidate instead of unilaterally expanding frozen test scope.
Safety rule (feature-specific): `home/data/<key>` (persist) and each restored `.add/` entry (restore) are never opened for writing or deletion until their staged copy has FULLY succeeded — copy-then-swap-then-sweep-old, never wipe-then-copy.
Code lives in: `add-method/` (the package — NOT this task's `./src/`).
Constraints: do NOT change any test or the contract; no new dependency (stdlib `tempfile`/`os`/`shutil` · Node builtin `fs`/`path` only); ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 75/75 green: test_global_restore.py 36/36 (19 new + 17 pre-existing), test_global_data.py/test_global_update_harden.py/test_global_install.py 39/39 unchanged
- [x] coverage did not decrease — 19 new test methods added, 0 removed/weakened; every pre-existing test method name and assertion is byte-unchanged (diffed against the tests-red commit)
- [x] no test or contract was altered during build — the build commit (`a3b832f`) touches only `_installer.py`+`cli.js`; TASK.md §1-§3 unchanged since freeze; `test_global_restore.py` unchanged since the tests-red commit (`bdbc373`)
- [x] the green was EARNED, not gamed — no overfit to fixtures, vacuous asserts, or stubbed-away logic (score with an adversarial refute-read — a subagent recommended under `autonomy: auto`; a confirmed cheat is HARD-STOP) — RESOLVED: independent reviewer's Refute-read verdict below records EARNED (RED independently reproduced, not trusted on the builder's word)
- [x] concurrency / timing of the risky operation is safe — RESOLVED: independent Advisor concurrency lens below records RESIDUE (bounded, matches the pre-declared carve-out, independently traced) — not a full clearance, but a judged, recorded verdict, not an open item
- [x] no exposed secrets, injection openings, or unexpected dependencies — RESOLVED: independent Advisor security lens below records CLEAR (full STRIDE pass) + one informational, safe-direction note (a directory permission tightening)
- [x] layering & dependencies follow CONVENTIONS.md — stdlib/builtin-only imports, matches §5's declared "no new dependency" constraint exactly
- [ ] a person reviewed and approved the change — pending human review

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] a crash mid-persist-stage or mid-commit leaves home/data/<key> byte-for-byte unchanged (never wiped, never a partial mix) — confirmed by test_persist_mid_stage_failure_leaves_snapshot_untouched / test_persist_commit_aside_failure_leaves_snapshot_unchanged / test_persist_commit_land_failure_rolls_back all green, each traced to its exact contract step (§3 persist steps 2/3a/3b)
- [x] a stale `.add-bak-*`/`.add-tmp-*` scratch sibling from an earlier interrupted call is gone after the very next call touching that target, and correct content lands — confirmed by test_persist_stale_backup_self_heals_next_call / test_persist_stale_staging_swept_before_new_staging / test_restore_stale_per_entry_staging_swept_next_call_rederives all green
- [x] `--force` restore on a DIRECTORY entry backs the original up to `<name>.bak/` and lands the snapshot's content — confirmed by test_restore_force_directory_entry_backed_up_and_replaced (M14, previously only manually verified, now a committed passing test)
- [x] the real `node cli.js init --from-global-data` + `prune-data`/`prune-data --force` subprocess actually mutates the filesystem and reports real stdout/exit codes (not string-presence) — confirmed by test_npm_restore_and_prune_behavioral_smoke green; additionally, persistData's OWN happy-path + refresh/2-rename-commit path (not required by the frozen M15 scope, which names only restore+prune) was confirmed via a throwaway manual `node` subprocess smoke — both rounds passed (fresh commit, then refresh with an existing dest)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_sweep_scratch`/`sweepScratch` (new private helpers) are each referenced from 5 call sites in their own file (persist's stage-failure/commit-aside-failure/commit-land-failure/final-sweep + restore's self-heal/stage-failure/commit-land-rollback); the `.add-tmp-`/`.add-bak-` literals are referenced in `_is_user_data`/`isUserData` (exclusion), `_persist_data`/`persistData` and `_restore_data`/`restoreData` (naming), and asserted present by test_parity_call_site_shape — confirmed by direct read-through of both files post-edit (not grep-only)
- [x] DEAD-CODE (code) — no orphaned symbol: `_sweep_scratch`/`sweepScratch` are both used (see WIRING above); the only new imports (`tempfile`, `uuid` in Python) are both used; JS's `crypto` module was already imported pre-task, this task adds one new call site (`crypto.randomBytes`) to an existing import, not a new unused one
- [x] SEMANTIC (prose / non-code) — N/A as a deliverable (this task's scope is code + tests only); TASK.md's own §0-§3 frozen prose was read in FULL (not skimmed) before writing a single test or line of implementation, and re-read again during this adversarial pass to re-verify every M1-M15 clause against the actual committed code

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> §0's Ground SHA anchors the symbols cited at ground time to that commit — code moves during
> build. Before the gate, re-resolve every symbol §3 CONTRACT cites against the CURRENT tree
> (not the Ground SHA) so a stale anchor is caught here, not by a future reader chasing a moved
> line.
- [x] every symbol §3 CONTRACT cites still resolves in the current tree — confirmed by direct grep/read against the post-build tree: `_installer.py` — `data_key` 696-705, `_is_user_data` 706-723, `_sweep_scratch` 724-738 (NEW), `_persist_data` 739-812, `_restore_data` 813-886, `_prune_data` 887-1521 (untouched), `install` 996 (untouched, calls `_persist_data` at 1163 and `_restore_data` at 1178), `_clean_replace` 1237 (untouched, sibling task's own scope), `_update_global` 1360 (untouched, calls `_persist_data` at 1428); `cli.js` — `dataKey` 924-933, `isUserData` 934-945, `sweepScratch` 946-955 (NEW), `persistData` 956-1027, `installGlobalData` 1028-1041 (untouched, calls `persistData` at 1033), `isSymlink` 1042-1054, `restoreData` 1055-1119, `installGlobalDataRestore` 1120-1139 (untouched, calls `restoreData` at 1126), `pruneData` 1140+ (untouched); `cmdUpdateGlobal`'s own `persistData` call site at 1265 (untouched)
- [x] any anchor that moved/renamed since Ground SHA is named here, not left silent — NONE renamed (all names identical to Ground, per M12); ALL 6 target-function anchors MOVED (line-shifted only, pushed down by the new code inserted above/within them): Python `_persist_data` Ground 717-736 -> now 739-812, `_restore_data` Ground 740-776 -> now 813-886, `_is_user_data` Ground 704-713 -> now 706-723; JS `persistData` Ground 942-954 -> now 956-1027, `restoreData` Ground 981-1001 -> now 1055-1119, `isUserData` Ground 932-938 -> now 934-945. Every OTHER cited anchor (`install`, `_update_global`, `_prune_data`, `_clean_replace`, and their JS callers) kept its Ground content byte-identical, only shifting position for the same reason.

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: independent reviewer (add-verify subagent, TDD-Verifier persona) · adversarially checked:
  (1) RED reproduced independently, not trusted on the builder's word: swapped bdbc373's
  pre-implementation `_installer.py`/`cli.js` into the worktree and re-ran the full 36-test
  suite — got `FAILED (failures=11, errors=1)` = 12 failures, NAME-FOR-NAME identical to
  bdbc373's own commit-message list; restored via `git checkout HEAD --` immediately after,
  re-confirmed 36/36 green again. Proves the new tests genuinely discriminate old vs. new
  behavior — not vacuous, not overfit to fixtures.
  (2) Read (not skimmed) the 3 highest-risk test bodies directly against their claims: the
  interleaved-calls test's `racing_copyfile` hook + its weak "one caller's full content, never
  a mix / no scratch survives" asserts; the mid-stage-failure test's write-garbage-then-raise
  mock (the exact fix OBSERVE-NOTES' own competency delta names, confirmed present in the
  committed test, not just described); the full `ParityRestoreTest` class (confirmed
  `test_npm_restore_and_prune_behavioral_smoke` genuinely subprocesses `node`, scoped to
  restore+prune only — no persist happy-path coverage, see Advisor Architecture lens below).
  (3) Confirmed via a PLAIN (non-git) diff of full pre/post file content — not the commit's own
  stat — that the build touches exactly 3 hunks in `_installer.py` (imports ·
  `_is_user_data`+`_sweep_scratch` · `_persist_data`/`_restore_data`) and 2 in `cli.js`
  (`isUserData`+`sweepScratch`+`persistData` · `restoreData`); `install()`/`_update_global()`
  and their JS callers are BYTE-IDENTICAL, not merely claimed so.
  No vacuous asserts, no stubbed-away logic found; every assertion checks real filesystem
  post-state (content, absence, exact leftover sets), not internal call-counts alone.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: independent reviewer (add-verify subagent, TDD-Verifier persona; STRIDE lens borrowed
  from security-gatekeeper for lens 1)
1. Security: CLEAR — STRIDE pass found no hit: no new auth/identity surface; frozen §1-§3 and
  every existing test proven untouched since freeze (commit stats + plain diff, not just
  claimed); 0 new dependencies beyond stdlib `tempfile`/`uuid` + Node builtin `fs`/`path`/
  `crypto` (already imported), confirmed via diff; both twins stage via `tempfile.mkdtemp`/
  `fs.mkdtempSync` (collision/TOCTOU-safe by construction) INSIDE the same privileged parent as
  the final target, never a shared/world-writable tmp location; no eval/dynamic-exec, no
  secrets, no network IO added.
  One independently-discovered 💭 note (not a finding, not previously disclosed by the builder):
  `_persist_data`'s stage-via-mkdtemp mechanism changes `home/data/<key>`'s OWN top-level
  directory mode from the old mkdir-default (e.g. 0755, umask-dependent) to a fixed 0700
  (owner-only) — empirically verified (old `mkdir` -> `drwxr-xr-x` vs new `mkdtemp`+rename ->
  `drwx------`), because no `copystat`-equivalent step ever restores the top-level dir's mode
  after staging. Confirmed this is SPECIFIC to persist's whole-tree case: `_restore_data`'s
  directory-entry path is unaffected (empirically verified — `shutil.copytree(...,
  dirs_exist_ok=True)` still fixes the mode via its own internal `copystat` call, landing at the
  source's original mode either way). Strictly MORE restrictive, not less — a safe-direction side
  effect, not a vulnerability; worth a Spec-delta line so it becomes a conscious choice.
2. Concurrency: RESIDUE — the self-heal-vs-interleaved-caller interaction (OBSERVE-NOTES finding
  1) is real; independently re-derived by hand-tracing every commit-window interleaving (not
  trusted from the builder's account) AND by reading the committed
  `test_persist_two_interleaved_calls_land_one_full_valid_snapshot` directly: the weak guarantee
  provably holds under adversarial interleaving — dest always ends up ONE caller's full valid
  content, never a mix; a losing/interleaved caller always raises (including a "second-order"
  raise on its own rollback attempt, when the interleaver's self-heal already consumed the
  rollback's target), never silently misreports success. The "already-accepted, out-of-scope"
  framing IS honest: this is a specific instance of the pre-declared "two lock-less callers
  racing on the same target" carve-out (§3 Reject), and its stated guarantee holds under my own
  independent trace, not just the builder's word — not a new failure mode the carve-out fails to
  cover. `_restore_data`'s simpler (sweep-only) self-heal is actually SAFER by construction than
  persist's — its `.add-tmp-*` glob target structurally cannot match the permanent, non-token
  `.bak` sidecar, so a concurrent self-heal can never consume a force-restore's in-flight backup
  the way persist's can consume its own in-flight backup. Residual debuggability rough edge (a
  confusing second-order exception rather than the root cause reaching the caller) noted for the
  next loop; not a correctness or data-loss defect. Non-blocking.
3. Architecture: RESIDUE — (a) `persistData`'s own happy/refresh path has NO committed real-
  node-subprocess test (confirmed directly: `test_npm_restore_and_prune_behavioral_smoke` drives
  only restore+prune; `test_parity_surface`/`test_parity_call_site_shape` are pure string/
  substring checks, never a subprocess) — a real but frozen-AT-DESIGN-TIME (M15's own scope
  named only restore+prune), not build-time-corner-cut, gap; acceptable non-blocking given the
  Python reference implementation is exhaustively tested for this exact logic and a structural
  parity check at least confirms the JS mirror's call-site shape. Recommend the next loop's Spec
  delta promote this to a Must.
  (b) The pre-existing JS `persistData`-vs-`restoreData` symlink-dereference asymmetry is
  confirmed via `git log -S"dereference"` to predate this task (introduced by `bbc8562`, a prior
  task) and is correctly left untouched (frozen scope's byte-identical-content invariant) —
  sharper framing than OBSERVE-NOTES' own: it is not just cross-function but also CROSS-TWIN
  (Python's `_persist_data` already dereferences via `copytree`/`copyfile` defaults; only JS's
  `persistData` is the odd one out). Worth tightening the Spec-delta wording, not a blocker.
Verdict: PASS
Residue: non-security only — (1) self-heal-vs-interleaved-caller: bounded/fail-loud, matches the
  pre-declared concurrency carve-out, confirmed by independent trace + test read, not merely
  asserted; (2) `persistData`'s real-subprocess test coverage thinner than `restoreData`'s, a
  frozen-at-design-time scope choice, not a build-time cut; (3) pre-existing (not this task's) JS
  cross-twin symlink-dereference asymmetry, correctly left alone; (4) NEW, independently-found,
  safe-direction (more restrictive) permission-bit change on `home/data/<key>`'s own directory
  mode. None are security findings; none indicate a gamed green.
Binding: advisory — architecture (this task hardens core installer data-safety mechanisms, not a
  purely mechanical change; feeds the human's own GATE RECORD decision, does not self-resolve it)

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-03

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose per-function-shaped stage-then-commit — WHOLE-TREE staging for `_persist_data` (mirrors `_clean_replace` exactly, its dest `home/data/<key>` is self-owned) + PER-ENTRY staging for `_restore_data` (dest `.add/` is a SHARED directory most of which this function must leave alone); rejected one uniform whole-tree stage for BOTH, via a full `.add/` copy (rejected — every restore call would swap the ENTIRE `.add/`, including `tooling/add.py` itself, just to fill in a few entries; a far larger blast radius and crash window than today) · one uniform per-entry stage for BOTH (rejected for persist — its self-owned dest gains nothing from per-entry granularity over the simpler, already-designed whole-tree sibling pattern)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: Largely as planned, with 2 deliberate deviations. (1) §4 TESTS was written and committed as its OWN standalone, confirmed-RED commit BEFORE any implementation batch began (`bdbc373`) — the listed strategy names 5 build-oriented batches without saying whether tests land before or interleaved with them; TDD discipline put the full red suite first, verified 12/36 new tests failing for the traced right reason (missing self-heal/stage/commit/rollback/exclusion logic) and 0 regressions in the other 24 (17 pre-existing + 3 happy-path/preserved-behavior + 1 disclosed-non-goal case, each traced against the OLD implementation to confirm non-vacuity) before touching `_installer.py`. (2) Batches 1-3 (`_persist_data`, `_restore_data`, `_is_user_data`) were implemented together in ONE pass in `_installer.py` (plus a new shared `_sweep_scratch` helper) rather than as 3 separate sequential edits, since all three share that helper and the self-heal/stage/commit shape; batch 4 (cli.js mirror) followed as a second pass once the Python side was green. Suite went RED (12/36) -> GREEN (36/36 + 39/39 siblings) in one implementation pass per language, committed as a single green commit (`a3b832f`) separate from the red commit, so git history shows genuine red-then-green, not a squash. Additionally ran a throwaway, uncommitted manual smoke (real `node cli.js init --global-data` against a real project, twice — fresh commit then refresh/2-rename commit) to close a self-identified gap: no existing or new COMMITTED test exercises persistData's own happy path via a real node subprocess (the frozen M15 scope names only restore+prune for the real-subprocess treatment); did not add this as new committed test scope since the contract's own M15/scenario deliberately named only restore+prune — flagged as a §7 Spec delta candidate instead of unilaterally expanding frozen test scope.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · carried] promote a real node-subprocess behavioral test for `persistData`'s own [carried: deliberate M15/§2 scope cut at design time, still valid; not urgent enough to seed standalone]
  happy-path + refresh/2-rename-commit path to a Must next loop — today it's exercised only
  via Python-side unit tests + a structural JS call-site check, never a real `node`
  subprocess in the committed suite (a deliberate M15/§2 scope choice at design time, not a
  build-time cut) (evidence: OBSERVE-NOTES.md's own TDD finding; independent add-verify
  pass's Advisor Architecture lens; a throwaway, uncommitted manual smoke closed this gap
  for build-time confidence only, never committed)
- [SPEC · carried] decide + document whether `home/data/<key>`'s new directory-mode tightening [carried: needs a human intent call (normalize vs keep 0700), not a code fix; carry until decided]
  (~0755 → 0700, a side effect of the `mkdtemp`-based staging with no `copystat`-equivalent
  restore of the top-level dir's mode) is intended, or should be normalized back to match
  pre-task permissions — independently discovered, safe-direction (more restrictive), not
  previously disclosed by the build (evidence: independent add-verify pass's Advisor
  Security lens, empirically confirmed via a before/after permission-bit check)
- [SPEC · carried] sharpen the pre-existing JS `persistData`-vs-`restoreData` symlink [carried: narrow cross-twin gap, no known failure currently triggering it; low urgency]
  dereference asymmetry as CROSS-TWIN, not merely cross-function as first framed — Python's
  `_persist_data` already dereferences via `copytree`/`copyfile` defaults; only JS's
  `persistData` carries no `dereference` option (evidence: OBSERVE-NOTES.md's own SDD
  finding; independent add-verify pass confirmed via `git log -S"dereference"` that this
  traces to a prior task, `bbc8562`, not this one)
- [SPEC · carried] `_persist_data` does not call `.resolve()` on `project_abspath` internally [carried: latent trap only for a future direct caller that skips resolving first; no current caller affected]
  (unlike `_restore_data`, which resolves at its own top) — safe today only because its one
  production caller, `install()`, always resolves `target_path` before calling either; a
  latent trap for any FUTURE direct caller that doesn't resolve first (evidence:
  OBSERVE-NOTES.md's own SDD finding, `_installer.py:_persist_data` line 739 vs
  `_restore_data` line 828, `install()` resolves before both call sites)

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [TDD · folded] a self-heal mechanism cannot distinguish "stale from a crash" from "live from [folded foundation-version 63]
  a concurrent, in-flight sibling call" — a nested/interleaved second call's OWN step-0
  self-heal can delete the FIRST call's still-in-progress staging directory, causing the
  first (outer) call to raise rather than silently corrupt (a strictly better failure mode
  than the pre-task behavior, but worth naming explicitly). Consider a liveness signal (e.g.
  a PID-stamped lock) for a future concurrency-focused task (evidence:
  test_persist_two_interleaved_calls_land_one_full_valid_snapshot, independently re-traced
  by hand by the add-verify pass, not merely trusted from the builder's account)
- [TDD · folded] a fault-injection mock that raises IMMEDIATELY (before writing anything) can [folded foundation-version 63]
  fail to discriminate "wrote straight to the final name" from "wrote to an isolated staged
  copy" — both old and new code leave the same "nothing at the final name" outcome.
  Strengthen it to write partial/garbage content THEN raise, exposing old code's real
  corruption vs new code's safety (evidence:
  test_restore_mid_stage_failure_earlier_committed_entries_survive's mock was strengthened
  from a bare `raise OSError` to a write-then-raise specifically because the immediate-raise
  version passed on both old and new code)
- [ADD · folded] the SAME parallel-build-worktree-vs-frozen-contract gap diagnosed fully in [folded foundation-version 63]
  `global-lock-followups`'s own §7/OBSERVE-NOTES.md recurred here too — this task's own
  `TASK.md` needed a manual `git checkout cda1a16 --` sync (commit `735343a`) before Ground
  could even be read, after confirming zero source-code drift in the 2 upstream commits
  being pulled (evidence: `735343a`; see `global-lock-followups`'s fuller diagnosis + fix
  recommendation rather than duplicating it here)

