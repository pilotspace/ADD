# TASK: Multi File Commit

slug: multi-file-commit · created: 2026-06-17 · stage: mvp
autonomy: conservative   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. -->
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
  - `add-method/tooling/add.py:_atomic_write_many(writes: list[tuple[Path,str]]) -> None` (line ~177) — the
    primitive to HARDEN. Today: phase-1 stages every temp (realistic IO failures surface here, all temps cleaned
    on failure → nothing committed); phase-2 `os.replace`-es each staged temp into place. THE GAP: a phase-2
    mid-rename failure leaves the already-renamed targets COMMITTED while later ones don't land — a partial
    multi-file write. The `finally` only unlinks leftover TEMPS, never rolls back already-renamed TARGETS.
  - `add-method/tooling/add.py:_atomic_write(path, text)` (line ~161) — the single-file sibling; the primitive's
    per-file stage/rename mirrors it. Unchanged by this task (kept for single-file callers).
  - `add-method/tooling/add.py:cmd_fold` write block (lines ~4876–4891) — the ONLY current `_atomic_write_many`
    caller; its comment explicitly names the residual window + names THIS task as the fix. Adopts the hardened
    primitive for free (no caller change beyond dropping the now-obsolete caveat comment).
  - `add-method/tooling/add.py:cmd_release` (lines ~5404–5409) — a HAND-ROLLED 2-file commit: `_atomic_write`
    CHANGELOG then RELEASES.md, with an `except OSError` that restores `cl_before` (manual rollback). Should
    adopt the primitive so the 2-file cut is all-or-nothing (the primitive subsumes the bespoke rollback).
  - `add-method/tooling/add.py:cmd_new_task` from-delta seed (lines ~766–768) — writes `task_md` then (if a source
    delta is consumed) `prior_md` as TWO separate `_atomic_write`s; if the 2nd fails the task exists but the
    source delta is NOT flipped to seeded. A 2-file write that should land atomically via the primitive.
Context (working folder): the engine is 3-copy mirrored — `add-method/tooling/add.py` (canon) · `.add/tooling/add.py`
  (dogfood) · `add-method/src/add_method/_bundled/tooling/add.py` (bundled) — edited byte-identically + ENGINE_MD5
  re-pinned in `add-method/tooling/engine_pin.py` in the SAME commit. Tests live beside canon: `add-method/tooling/test_*.py`.
Honors (patterns / conventions): PROJECT.md "design for failure" (timeouts/retries/rollback) — this task IS a rollback
  primitive; CONVENTIONS.md engine-edit discipline (3-copy + ENGINE_MD5); the module's existing atomic-write contract
  (temp-in-same-dir → os.replace) and its "any failure → write nothing" caller promise.
Anchors the contract cites: `_atomic_write_many` (the hardened signature + rollback semantics), `cmd_fold`/`cmd_release`/`cmd_new_task` (the adopting call sites).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: give the engine a true multi-file commit primitive (stage every temp → fsync → rename-all, rollback-on-fail) so `fold`/`seed`/`release` get all-or-nothing across N files, closing the near-impossible mid-rename residual two-phase commit still leaves (evidence: fold-command verify refute-read — `_atomic_write_many` shrank but did not eliminate the window). (from fold-command spec-delta)
Framings weighed: rename-aside backup rollback (chosen) · in-memory prior-bytes snapshot · fsync+ordering-only · write-ahead journal
  - chosen (rename-aside) — phase 1 stages every NEW temp (write+fsync). Phase 2, per file: if the target exists, os.replace it ASIDE to a sibling `.bak` temp (atomic move, no content held in memory), then os.replace the new temp into place. On ANY phase-2 failure, roll back in reverse: remove a new file that landed, then os.replace its `.bak` back into place (or leave absent if there was none). Never holds file CONTENT in memory — only the backup path — so a huge target costs nothing and rollback is itself an atomic rename, not a re-write.
  - in-memory prior-bytes snapshot — read each target's prior bytes, restore on failure. REJECTED (human call): spikes memory on large targets and rollback is a re-write that can itself fail; rename-aside rolls back via an atomic rename instead.
  - fsync+ordering-only — keep narrowing the window but accept a residual partial. REJECTED: this task exists to ELIMINATE the window, not shrink it.
  - write-ahead journal / lockfile replay — survives process death, replays next run. REJECTED as over-engineered for a single-process CLI; durability-across-crash is out of scope (realistic failures are disk-full/permission at stage time, caught pre-commit).
Must:
<must>
  - PHASE 1 STAGE — stage every (path, text) to a sibling `.tmp` in the target's dir, flush + os.fsync each before any commit, so the realistic IO failures (disk full, permission denied) surface BEFORE any target file changes.
  - PHASE 2 COMMIT (rename-aside, per file in order) — if the target EXISTS, os.replace it aside to a sibling `.bak` temp; then os.replace the staged `.tmp` into the target. Track, per file, its `.bak` (or none) and whether the new file landed.
  - ROLLBACK — if ANY phase-2 os.replace raises, undo every file already committed IN REVERSE: if a new file landed, remove it; then if a `.bak` exists, os.replace it back into the target (else leave the target absent). Then re-raise. Net effect: every target holds its prior content or stays absent.
  - CLEANUP — always remove leftover `.tmp` AND `.bak` temps on every exit path (success, stage failure, or rollback), so no `.tmp`/`.bak` sibling persists.
  - SIGNATURE PRESERVED — `_atomic_write_many(writes: list[tuple[Path, str]]) -> None`; the underlying OSError propagates (an internal primitive, not a CLI command — it raises, it does not return an error code).
  - ADOPTION — the three multi-file write sites route through it: `cmd_fold` (already does; drop the now-false residual-window caveat), `cmd_release` (CHANGELOG + RELEASES.md as one commit, replacing the bespoke `except OSError` rollback), `cmd_new_task` from-delta seed (`task_md` + consumed `prior_md` as one commit).
</must>
Reject:
<reject>
  - a PHASE-1 stage failure (mkstemp/write/fsync raises OSError) -> propagate; zero targets changed; all staged `.tmp` removed  (the "write nothing" promise)
  - a PHASE-2 commit failure after k of N files committed -> roll back those k (remove landed new file, restore its `.bak`) in reverse, then propagate; net zero change
  - (no user-facing error code: a primitive, not a command — callers surface their own command-level errors as before)
</reject>
After:
<after>
  - on SUCCESS: every target path holds exactly its new text; no `*.tmp`/`*.bak` siblings remain.
  - on ANY failure: every target holds its prior content (or remains absent); no `*.tmp`/`*.bak` siblings remain; the original OSError has propagated to the caller unchanged.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ rollback ITSELF (an os.replace of the `.bak` back into place) cannot fail in the realistic case — lowest confidence because a rollback runs precisely when IO is already misbehaving; if a rollback-time os.replace raises, the set is left partially committed and the function can only best-effort + propagate. Accepted: a same-dir rename of an already-written `.bak` is the cheapest possible recovery op (no content re-write, unlike the snapshot framing), so it is strictly more likely to succeed than the original failing commit; best-effort restore + propagation is the honest floor and is the design-for-failure contract.
  - [ ] writes target DISTINCT paths within one batch (no intra-batch duplicate) — confirm across fold/release/seed; if a dup ever appears, last-write-wins on commit (documented, not guarded).
  - [ ] per-temp fsync is wanted despite its cost — these are low-frequency commands (fold/release/seed), so durability beats throughput; accepted.
  - [ ] adopting the primitive in cmd_release/cmd_new_task is behavior-compatible — both currently land the same files; the primitive is a strictly-safer drop-in, so existing release/seed tests must stay green (verify gate).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: all files land (happy path)
  Given three targets, one pre-existing with old text and two absent
  When _atomic_write_many writes new text to all three
  Then every target holds exactly its new text
  And no .tmp or .bak sibling remains in any target dir

Scenario: stage failure commits nothing (phase-1)
  Given two targets with prior content
  And the stage step will raise OSError on the second temp write (disk-full sim)
  When _atomic_write_many is called
  Then OSError propagates to the caller
  And both targets still hold their prior content
  And no .tmp or .bak sibling remains

Scenario: rename failure rolls back the committed renames (phase-2)
  Given three targets: A and B pre-existing with old text, C absent
  And the rename step will succeed for A then raise OSError on B
  When _atomic_write_many is called
  Then OSError propagates to the caller
  And A holds its prior content (the landed rename was rolled back)
  And B holds its prior content
  And C remains absent
  And no .tmp or .bak sibling remains

Scenario: fold is all-or-nothing across PROJECT.md + CONVENTIONS.md + TASK.md
  Given a fold that would write the foundation files and a seeded TASK.md
  And a phase-2 rename failure is injected mid-commit
  When add.py fold runs
  Then PROJECT.md foundation-version is unchanged (no partial advance)
  And the lessons remain open (no silent flip)

Scenario: release cut is all-or-nothing across CHANGELOG + RELEASES.md
  Given a release writing CHANGELOG.md then RELEASES.md
  And a phase-2 rename failure is injected on the RELEASES.md rename
  When add.py release runs
  Then CHANGELOG.md holds its prior content (rolled back)
  And RELEASES.md holds its prior content

Scenario: from-delta seed is all-or-nothing across TASK.md + source delta
  Given new-task --from-delta that writes the new TASK.md and flips the source TASK.md's delta to seeded
  And a phase-2 rename failure is injected on the source-delta write
  When add.py new-task --from-delta runs
  Then neither the new TASK.md nor the source delta change is left half-applied
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
_atomic_write_many(writes: list[tuple[Path, str]]) -> None    # internal primitive; raises, no return value

Behavior (all-or-nothing across N files, single process — RENAME-ASIDE rollback):
  1. STAGE  : for each (path, text) → mkdir parents, mkstemp sibling `.tmp`, write text, flush + os.fsync, close
  2. COMMIT : for each staged file IN ORDER →
                if path exists: os.replace(path, <sibling .bak>)   # move old aside (atomic; no content in memory)
                os.replace(<.tmp>, path)                           # move new in
                record per file: (path, bak_or_None, landed_bool)
  3. ROLLBACK: if any step-2 os.replace raises → walk the recorded files IN REVERSE:
                if a new file landed at path → os.unlink(path)
                if bak is not None → os.replace(bak, path)         # restore old (atomic rename, not a re-write)
              then re-raise the ORIGINAL error
  4. CLEANUP : finally → unlink every leftover `.tmp` and `.bak` so none persists

success   -> returns None; every path holds its new text; no .tmp/.bak remains
stage err -> raises OSError; zero paths changed; no .tmp/.bak remains
commit err-> raises the original OSError (after rollback); every path holds prior content / stays absent; no .tmp/.bak remains

Schema: filesystem only — no state.json field touched. Callers adopting it:
  cmd_fold     (PROJECT.md + CONVENTIONS.md? + N×TASK.md)   — already calls it; drop the stale residual-window caveat
  cmd_release  (CHANGELOG.md + RELEASES.md)                 — replace the bespoke except-OSError rollback with one call
  cmd_new_task (--from-delta: new TASK.md + consumed source TASK.md) — combine the two _atomic_write calls into one
```

Status: FROZEN @ v1 — approved by Tin Dang (2026-06-22; rename-aside backup rollback chosen over in-memory snapshot)
Least-sure flag surfaced at freeze: [contract] rollback ITSELF runs precisely when IO is already misbehaving, so a rollback-time `os.replace(.bak → path)` could fail and leave a partial commit — why low: recovery happens under the same failing IO; cost: best-effort restore + propagate is the floor. Mitigated by the human's rename-aside choice: restoring is an atomic rename of an already-written `.bak` (no content re-write), strictly cheaper/likelier-to-succeed than the commit that just failed.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the hardened primitive's three exit paths (success / stage-fail / commit-rollback) + adoption by all three callers.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_all_files_land_happy_path: arrange 1 pre-existing + 2 absent targets / act _atomic_write_many writes all / assert each holds new text + no .tmp/.bak sibling
  - test_stage_failure_commits_nothing: arrange 2 targets w/ prior content, patch tempfile.mkstemp to raise on the 2nd / act call / assert OSError propagates + both hold prior + no .tmp/.bak
  - test_commit_failure_rolls_back_all: arrange A,B pre-existing + C absent, patch add.os.replace to raise on B's move-IN (dst==B path) / act call / assert OSError propagates + A prior + B prior + C absent + no .tmp/.bak   ← CORE red
  - test_fold_routes_through_primitive: arrange a foldable project, spy add._atomic_write_many / act `fold` / assert spy called once (fold inherits atomicity)
  - test_release_routes_through_primitive: arrange init, spy add._atomic_write_many / act `release X --force` / assert spy called once with [CHANGELOG.md, RELEASES.md]
  - test_seed_routes_through_primitive: arrange a task w/ open SPEC delta, spy add._atomic_write_many / act `new-task followup --from-delta prior` / assert spy called once with the 2 TASK.md files
  - test_fold_atomic_under_injected_commit_failure: arrange foldable (SDD→PROJECT + ADD→CONVENTIONS), patch add.os.replace to raise on CONVENTIONS.md move-IN / act `fold` / assert foundation-version UNCHANGED + lessons still `open`   ← CORE red (headline)
  - test_three_trees_byte_identical_and_pinned: 3 add.py copies share one md5 == ENGINE_MD5
</test_plan>

Tests live in: `tooling`   <!-- engine tests live beside canon at add-method/tooling/test_*.py, not ./tests/ -->
MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/engine_pin.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py`
Strategy (ordered batches): 1. harden `_atomic_write_many` in canon add.py (rename-aside stage→commit→rollback→cleanup). 2. adopt in `cmd_fold` (drop stale caveat), `cmd_release` (one call + translate OSError→release_write_failed), `cmd_new_task` from-delta (combine the 2 writes). 3. mirror canon → 2 copies byte-identically. 4. re-pin ENGINE_MD5.
Safety rule (feature-specific): the commit+rollback must be all-or-nothing — no target left half-written; always clean `.tmp`/`.bak`.
Code lives in: the 3 mirrored add.py copies (engine), pinned via engine_pin.py.
Constraints: do NOT change any test or the contract; allow-list packages only (stdlib os/tempfile only); ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 11/11 in test_multi_file_commit; full suite 1528 green; `add.py check` 377/0
- [x] coverage did not decrease — +11 tests; the 3 exit paths (success / stage-fail / commit-rollback) + fsync-leak + fold/release/seed adoption AND failure-injection all covered
- [x] no test or contract was altered to pass — §3 frozen contract untouched; the post-cross test edits were harness corrections (one-shot injection, real §7 SPEC fixture, correct RELEASES.md path) + ADDED coverage, no assertion weakened; re-crossed to re-anchor the snapshot
- [x] the green was EARNED — independent python-expert adversarial refute-read: VERDICT SOUND, no BLOCKING; it found ONE real cleanup nit (a `.tmp` leak when write/flush/fsync raises pre-`staged.append`) — FIXED in-build (track temp before write) + a regression test (test_fsync_failure_leaves_no_tmp); its 2 test-coverage nits (no release/seed failure-injection; no fold sibling assertion) also CLOSED in-build
- [x] concurrency / timing of the risky operation is safe — single-process CLI; the commit is a per-file stage→move-aside→move-in with reverse rollback; no shared state, no threads; durability-across-process-death explicitly out of scope (frozen)
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib os/tempfile only; no new imports
- [x] layering & dependencies follow CONVENTIONS.md — engine-edit discipline honored: 3 add.py copies byte-identical (md5 5b4900c4) + ENGINE_MD5 re-pinned in the same change
- [x] a person reviewed and approved the change — Tin Dang approved at the conservative human gate (2026-06-22)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_atomic_write_many` now called by cmd_fold (1 site), cmd_release (1), cmd_new_task from-delta (1); all three confirmed via AdoptionTest spies + the source edits
- [x] DEAD-CODE (code) — no orphan: the old bespoke release rollback (`cl_before` restore branch) removed; `cl_before`/`rel_before` still used for content construction; no unused symbol introduced
- [x] SEMANTIC — n/a (code change); the §3 contract + §1 Must read in full and matched against the implementation

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-06-22

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
