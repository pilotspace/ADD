# TASK: Scaffold .add/.gitignore at init to keep transient engine artifacts out of git

slug: gitignore-scaffold · created: 2026-06-15 · stage: mvp · risk: high
autonomy: conservative   <!-- method-defining (engine cmd_init edit) → high-risk; the engine refuses unguarded high-risk auto (unguarded_high_risk_auto). Standing human authorization to self-drive the freeze+verify gates (user chose "autonomous like advisor-context"), evidence surfaced per phase. -->
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
- `add-method/tooling/add.py:cmd_init` (L364–417) — the init command. Creates `(root/"tasks").mkdir(...)`, renders `SETUP_FILES` survivor docs via `_render_template`, saves state. The SEAM: write `.add/.gitignore` right after the `tasks/` mkdir (before the survivor-file loop), idempotent + never-clobber.
- `add-method/tooling/add.py:_atomic_write` (L132) — `(path, text)` durable write helper; used to write the gitignore body.
- `add-method/tooling/add.py:ROOT_DIRNAME` (L27 = ".add") — the engine root dir; `.gitignore` lands at `root/".gitignore"`.
- `add-method/tooling/add.py` scope-snapshot writer (L578, `tasks/<slug>/scope-snapshot.json`) and archive `.bak` writer (`cmd_archive_milestone` L1983, `milestones/<slug>/pre-archive-state.bak.json`) — the TWO transient artifacts the scaffold must ignore. Both are local working state (snapshot = the verify scope-gate touch-baseline read from disk; .bak = archive recovery net, read by nothing).
- `add-method/tooling/test_add.py:AddToolTest.test_init_creates_state_and_setup_files` (L28) — the init test home; the new RED guard `test_init_scaffolds_gitignore` lands here (setUp already gives a tmp-dir `init`).
- `add-method/tooling/engine_pin.py:ENGINE_MD5` (L14 = `7b67afd1b85c8493f12f2933cf9be9a6`) — single-source engine pin; a cmd_init edit changes add.py's md5 → re-aim this ONE literal.

Context (working folder):
- `/.gitignore` (repo root, L1–41) — already ignores `*.bak` (L21) but MISSES `*.bak.json` (the archive net) and `scope-snapshot.json` (never listed) → 12 snapshots + 20 .baks already tracked (leaked). Decision: the systemic fix is a co-located `.add/.gitignore` scaffolded at init, NOT broadening the root file (per the chosen altitude).
- `add-method/scripts/prepare_bundle.py` — produces the `_bundled/tooling/add.py` copy; run after the canonical edit.
- Three byte-identical engine copies (same md5): `add-method/tooling/add.py` (canonical) · `.add/tooling/add.py` (md5 mirror — the LIVE dogfood engine) · `add-method/src/add_method/_bundled/tooling/add.py` (package bundle).

Honors (patterns / conventions):
- CONVENTIONS §Method learnings: `engine-pin-3-mandatory-parts` (a real cmd_init edit must re-aim ENGINE_MD5 + re-sync all 3 copies); `token-presence+mirror-parity`; the SDD `new-engine-doc-trips-inventory-guards` / `§5-scope-frozen-at-tests-build` (declare EVERY guard-touched file in §5 BEFORE tests→build) and the ADD `build-in-build` rule (author the impl in BUILD, never specify — else the tests→build snapshot captures an already-built tree and the scope-gate is a no-op) — both folded @ foundation-version 30 from this very repo's last milestone.
- Design-for-failure (CLAUDE.md + cmd_init's own idiom): scaffold is never-clobber (skip an existing `.add/.gitignore`) + idempotent; the `.bak` recovery net stays ON DISK (we git-ignore, never delete it).

Anchors the contract cites: `cmd_init` (the scaffold seam) · `ROOT_DIRNAME` + `_atomic_write` (where/how the file is written) · the two ignore patterns `scope-snapshot.json` and `pre-archive-state.bak.json` (bare filenames → match at any depth under `.add/`) · `engine_pin.ENGINE_MD5` (the re-aim) · `test_init_scaffolds_gitignore` (the guard).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: init scaffolds a co-located `.add/.gitignore` so the engine's transient local artifacts are never committed.
Framings weighed: scaffold a co-located `.add/.gitignore` at init (chosen — systemic; every ADD project inherits it; tool-agnostic, git-is-git, zero lifecycle change) · broaden the repo-root `.gitignore` only (this-repo fix, no method-level benefit) · engine self-deletes the artifacts at lifecycle end (changes semantics + weakens the `.bak` recovery net — rejected, option C)
Must:
<must>
  - `cmd_init` writes `.add/.gitignore` (at `root/".gitignore"`, `root = base/ROOT_DIRNAME`) when it initializes a project.
  - The scaffold body ignores `scope-snapshot.json` (the verify scope-gate touch-baseline) AND `pre-archive-state.bak.json` (the archive recovery net), each as a bare-filename pattern so it matches at any depth under `.add/` (tasks/ · milestones/ · archive/).
  - The scaffold is NEVER-CLOBBER: if `.add/.gitignore` already exists, leave its bytes untouched (preserve human edits) — mirrors the SETUP_FILES skip-not-clobber idiom.
  - The scaffold body is a static module-level constant (no template render) — so it is never blank by construction (no 0-content circuit breaker needed, unlike the template-rendered SETUP_FILES).
  - The scaffold MUTATES NEITHER artifact on disk: the `.bak` recovery net and any existing snapshot survive untouched — git-ignore only, never delete.
  - All three engine copies stay byte-identical and `engine_pin.ENGINE_MD5` is re-aimed to the new add.py md5 (engine-pin-3-mandatory-parts).
</must>
Reject:
<reject>
  - `.add/.gitignore` already present -> skip, leave existing bytes (never-clobber; not an error — init continues) -> "gitignore_exists_skip" (an internal skip-state, no caller error code; init prints nothing new on the happy path)
</reject>
After:
<after>
  - a freshly `init`-ed project has `.add/.gitignore` containing both bare-filename patterns; a `git status` in that project never surfaces `scope-snapshot.json` or `pre-archive-state.bak.json`.
  - an `init` over an existing `.add/.gitignore` leaves it byte-for-byte unchanged.
  - the three engine trees are byte-identical (md5 parity) and ENGINE_MD5 matches the live add.py.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ git-ignoring `scope-snapshot.json` is safe for the scope-gate — lowest confidence because the verify gate treats a snapshot MISSING-against-its-state.json-anchor as `scope_snapshot_tampered` (add.py:2651); if a task were handed off mid-build across machines via git, the committed state.json anchor would arrive WITHOUT the (now-ignored) snapshot and the gate would refuse. Why acceptable: the gate reads the snapshot from LOCAL DISK where tests→build creates it (add.py:2603), ADD is single-driver-local, and the documented recovery is re-cross tests→build (re-snapshots). If wrong: a fresh-clone mid-build verify fires a spurious tamper HARD-STOP. (verified: the snapshot is created+read locally; nothing reads it from git)
  - [ ] bare-filename gitignore patterns match at any depth under `.add/` — git semantics: a pattern with no `/` matches in every directory; confirmed standard, low risk.
  - [ ] `.add/` itself is not git-ignored, so `.add/.gitignore` is effective + tracked — confirmed: root `.gitignore` ignores only `.add/docs/` + `.add/tooling/__pycache__/`, not `.add/`.
  - [ ] `git rm --cached` of the 32 already-tracked artifacts (the dogfood) leaves them on disk → the live scope-gate/recovery still works — confirmed: `--cached` drops the index entry only.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: Fresh init scaffolds the ignore file
  Given a directory with no .add/state.json
  When `add.py init` runs
  Then .add/.gitignore exists
  And its body contains the bare-filename patterns "scope-snapshot.json" and "pre-archive-state.bak.json"

Scenario: The scaffolded patterns actually keep the artifacts out of git (enforcement, not string-presence)
  Given a git repo freshly init-ed as an ADD project (the scaffolded .add/.gitignore present)
  And a file .add/tasks/demo/scope-snapshot.json and a file .add/milestones/demo/pre-archive-state.bak.json
  When git evaluates its ignore rules (`git check-ignore`)
  Then both artifact paths are reported IGNORED
  And .add/state.json is NOT ignored   # the rule is artifact-specific, never a blanket .add/ ignore

Scenario: Never-clobber an existing .add/.gitignore
  Given a directory whose .add/.gitignore already carries custom human bytes (no state.json yet)
  When `add.py init` runs
  Then .add/.gitignore is byte-for-byte unchanged
  And init still completes (state.json is created)   # skip is not an error
```

</scenarios>

<!-- Must "all three engine copies byte-identical + ENGINE_MD5 re-aimed" is a cross-tree
     invariant already owned by test_tree_parity · test_bundle_parity · the engine_pin
     importers — NOT a new behavioral scenario (no-duplicate convention). It is asserted
     in §4 by re-running those existing guards green, not by a new test. -->

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
cmd_init(args)  — on init, AFTER (root/"tasks").mkdir, BEFORE the SETUP_FILES loop:
  write  root/".gitignore"   (root = base/ROOT_DIRNAME = "<base>/.add")  from the
         module-level constant  _GITIGNORE_BODY
    FROZEN body invariant — the body MUST contain, each on its own line, the two
    bare-filename patterns (order/comments are non-frozen presentation):
        scope-snapshot.json
        pre-archive-state.bak.json
  never-clobber:  root/".gitignore" exists  -> skip (leave bytes), init continues  [gitignore_exists_skip]
  additive:       writes ONLY root/".gitignore" — creates/deletes/modifies NO
                  scope-snapshot.json and NO pre-archive-state.bak.json on disk

Engine invariant (engine-pin-3-mandatory-parts):
  md5(add-method/tooling/add.py) == md5(.add/tooling/add.py)
                                  == md5(add-method/src/add_method/_bundled/tooling/add.py)
  AND engine_pin.ENGINE_MD5 == that md5
```

Status: FROZEN @ v1 — approved by Tin Dang (standing autonomous authorization, 2026-06-15).
Least-sure flag surfaced at freeze: [spec] git-ignoring `scope-snapshot.json` is scope-gate-safe — the verify gate reads the snapshot from LOCAL DISK where tests→build creates it (add.py:2603), and ADD is single-driver-local; the only failure mode is a cross-machine mid-build handoff (committed state.json anchor arrives without the now-ignored snapshot), which fires a RECOVERABLE `scope_snapshot_tampered` HARD-STOP cleared by a tests→build re-cross. Cost if wrong: a spurious stop, never data loss.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: the 3 scenarios — behavioral, not line %.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_init_scaffolds_gitignore: arrange tmp dir / act `init` / assert .add/.gitignore exists AND its text contains both "scope-snapshot.json" and "pre-archive-state.bak.json" (presence — necessary).
  - test_gitignore_ignores_transient_artifacts: arrange `git init` + `add.py init` in a tmp repo, create .add/tasks/demo/scope-snapshot.json + .add/milestones/demo/pre-archive-state.bak.json / act `git check-ignore <both paths>` / assert BOTH reported ignored AND `git check-ignore .add/state.json` returns non-ignored (enforcement — the rule is artifact-specific, not a blanket .add/ ignore). Skips cleanly if `git` is unavailable (design-for-failure).
  - test_init_never_clobbers_existing_gitignore: arrange a pre-written .add/.gitignore with sentinel bytes (no state.json) / act `init` / assert the file is byte-for-byte the sentinel AND state.json was created (skip is not an error).
  - (engine parity + pin — NO new test) the §3 engine invariant is re-asserted by the EXISTING guards: test_tree_parity · test_bundle_parity · the engine_pin importers (e.g. test_shared_engine_pin). Build re-aims engine_pin.ENGINE_MD5 and re-syncs the 3 copies → those go/stay green.
</test_plan>

Tests live in: `add-method/tooling/test_add.py` · MUST run red (missing implementation) before Build.
RED triage (verified before build): test_init_scaffolds_gitignore RED ("init did not scaffold .add/.gitignore") · test_gitignore_ignores_transient_artifacts RED (git check-ignore matches nothing yet) · test_init_never_clobbers_existing_gitignore GREEN — disclosed regression guard (preserving an existing file is indistinguishable from "no scaffold" pre-build; it can only fail if a future change makes the scaffold clobber). The two RED drivers exercise the new behavior directly.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_add.py` `add-method/src/add_method/_bundled/tooling/add.py`
Strategy (ordered batches): 1. write the RED guards in test_add.py (cmd_init does not yet scaffold → red). 2. add `_GITIGNORE_BODY` constant + the scaffold write in `cmd_init` (canonical add.py). 3. sync the mirrors — copy canonical → `.add/tooling/add.py`, run `prepare_bundle.py` → `_bundled/.../add.py`. 4. re-aim `engine_pin.ENGINE_MD5` to the new md5. 5. dogfood THIS repo: write `.add/.gitignore`, `git rm --cached` the 32 leaked files + PR #16's 4. 6. full suite green + `add.py check`.
Safety rule (feature-specific): scaffold is never-clobber + additive — it writes ONLY `.add/.gitignore` and never creates/deletes/modifies a snapshot or .bak; `git rm --cached` keeps every file on disk (the .bak recovery net survives).
Code lives in: `add-method/tooling/add.py` (the engine).
Constraints: do NOT change any test or the contract; allow-list packages only (stdlib only); ask if unclear.
<!-- ALSO touched but UNDER `.add/` → invisible to the scope-gate (_SCOPE_EXCLUDE_DIRS includes `.add`),
     so NOT declared above: `.add/tooling/add.py` (md5 mirror — the live dogfood engine) and `.add/.gitignore`
     (the dogfood file). The `git rm --cached` leaves the working tree unchanged → not a scope touch either.
     engine_pin.py is NOT mirrored (single canonical file). -->

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — the 3 new guards green + 1019 others; the ONLY 8 failures are pre-existing installer-hint drift (test_installer_handoff ×5 · test_v8_install ×2 · test_shared_engine_pin ×1 cascade) in cli.js/_installer.py, which this task NEVER touched (git status confirms 0 installer files changed). `add.py check` on the dogfood repo: 294 passed, 0 failed.
- [x] coverage did not decrease — +3 tests, 0 removed/weakened.
- [x] no test or contract was altered during build — build touched only add.py (constant + scaffold), engine_pin.py (pin), and the 2 mirrors; the 3 tests authored in the tests phase are byte-unchanged; §3 stays FROZEN @ v1.
- [x] the green was EARNED, not gamed — adversarial refute RAN: removing the scaffold write block from a copy of add.py makes test_gitignore_ignores_transient_artifacts FAIL (proved non-vacuous). The test asserts real `git check-ignore` enforcement + that .add/state.json is NOT ignored (rule is artifact-specific, not blanket). The never-clobber test is disclosed as a green-pre-build regression guard, not a driver.
- [x] concurrency / timing — the never-clobber `exists()`-then-write has a benign TOCTOU, but `init` is a single-process bootstrap (not concurrent); safe. No risky operation.
- [x] no exposed secrets, injection openings, or unexpected dependencies — the body is a static module constant (no user input → no injection surface); stdlib only (Path · _atomic_write).
- [x] layering & dependencies follow CONVENTIONS.md — honors engine-pin-3-mandatory-parts: pin re-aimed (7b67afd1 → f15eb52a) + all 3 add.py copies byte-identical (verified md5).
- [x] a person reviewed and approved the change — standing autonomous authorization (user chose "autonomous like advisor-context"); evidence surfaced per phase.

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `_GITIGNORE_BODY` is referenced exactly once, in `cmd_init`'s scaffold write (the refute confirms removing it breaks the behavior); the 3 new test methods are discovered + run by unittest.
- [x] DEAD-CODE (code) — no orphaned symbol; `_GITIGNORE_BODY` has exactly one consumer.
- [x] SEMANTIC (prose / non-code) — read in full: the dogfood `.add/.gitignore` (matches `_GITIGNORE_BODY` byte-for-byte) and the `engine_pin.ENGINE_MD5` re-aim note; `git check-ignore` confirmed both artifacts ignored AND all leaked files still on disk (recovery nets intact).

### GATE RECORD
Outcome: PASS
Disclosed residue (pre-existing, OUT of scope — not introduced here): 8 installer-hint-drift failures — cli.js/_installer.py were reworded to a tool-agnostic hand-off ("open your AI Agent CLI (like Claude Code, Codex, etc.)", dropped "--await-lock") but test_installer_handoff/test_v8_install still assert the old text; candidate for a separate stale-test task. Verified independent: pin matches live add.py, no installer file in this task's diff.
Reviewed by: Tin Dang (standing autonomous authorization) · date: 2026-06-15

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): does a future engine change drop the `.add/.gitignore` scaffold from cmd_init (test_init_scaffolds_gitignore catches it)? does the dogfood `.add/.gitignore` drift from `_GITIGNORE_BODY`?
Spec delta for the next loop: an already-inited project (like this repo) does NOT retro-get `.add/.gitignore` — only `init` scaffolds it; a future `add.py update`/migration could backfill existing projects. Side-finding (separate task candidate): 8 installer-hint tests (test_installer_handoff · test_v8_install) are STALE against a reworded tool-agnostic installer hand-off.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] the scope-walk EXCLUDES `.add/` (_SCOPE_EXCLUDE_DIRS = .git/.add/__pycache__/node_modules), so an engine task that ALSO edits files UNDER `.add/` (the md5 mirror, a dogfood scaffold, a `git rm --cached`) gets ZERO scope-gate coverage there — only the canonical `add-method/…` tree is gated; declare the canonical files and treat the `.add/` twins as ride-along (evidence: §5 declared only the 4 add-method/ files; the .add/tooling/add.py mirror + .add/.gitignore + the 36-file untrack were all gate-invisible and the verify scope-gate passed clean)
- [TDD · folded] a "git ignores X" feature must be verified by REAL `git check-ignore` enforcement + a refute (delete the impl → the test fails), never by asserting the pattern STRING is present in the file — string-presence is necessary-not-sufficient and passes against a wrong pattern (evidence: the refute removed the scaffold write block from a copy of add.py → test_gitignore_ignores_transient_artifacts FAILED, proving it earned)
- [TDD · folded] a never-clobber / preserve-existing guard cannot run RED pre-build (doing nothing already satisfies "leave the file unchanged") — disclose it as a green regression guard, do NOT manufacture a vacuous RED; the RED must come from the create/enforce drivers (evidence: test_init_never_clobbers green pre+post-build; the 2 drivers carried the right-reason RED)
