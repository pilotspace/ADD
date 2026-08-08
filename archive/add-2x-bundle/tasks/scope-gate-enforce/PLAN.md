# TASK: the verify gate refuses a build that touched outside its declared §5 Scope

slug: scope-gate-enforce · created: 2026-06-12 · stage: mvp · risk: high
autonomy: conservative   <!-- lowered from the project default: engine-change task (method-defining) — the verify gate is human-held; the engine refuses an unguarded high-risk completion. -->
phase: done   <!-- ground -> specify -> scenarios -> contract -> tests -> build -> verify -> observe -> done -->
<!-- high-risk/method-defining scope? declare `risk: high` on the slug line above and lower the
     autonomy level to `manual` or `conservative` — the engine refuses an unguarded completion
     (`unguarded_high_risk_auto`, run.md guard). A comment is never a declaration. -->

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures): VERIFIED 2026-06-12 — `add-method/tooling/add.py` (engine change: ENGINE_MD5 re-pin + ×3 sync). The snapshot PRECEDENT: `_tripwire_snapshot(root, slug, raw3)` (add.py:1990) — md5 of resolved test files + frozen §3, keyed by project-root-relative paths; written at the tests→build advance (cmd_advance :563–567, UNCONDITIONAL overwrite so a re-crossed change-request re-snapshots cleanly; co-witnessed by `flag_verified`); stored at `state["tasks"][slug]["tripwire"]`. Divergence: `_tripwire_divergence` (:2009) re-reads each TRACKED path directly — never re-globs — fail-closed on deleted/unreadable. Gate placement: `cmd_gate` (:625–677) completing path = setup_locked → verify-phase guard → `unguarded_high_risk_auto` (:652) → `_tamper_guard` (:2060, BEFORE the waiver write so a finding is never launderable through RISK-ACCEPTED; tri-state, `tripwire_missing` when flag_verified but no snapshot). Heal router (NEXT task's seam, NOT this one): `_heal_or_escalate` (:2023) — sources "tamper"/"refute-read", HEAL_CAP monotonic, exit 3, phase set DIRECTLY so the baseline is not re-snapshotted mid-loop. §5 Scope parser DOES NOT EXIST yet — the analog to clone: `_declared_test_files` (:1911), grammar frozen by scope-decl-template §3 v2 (backticked tokens · FIRST declaring line · `./…`→task dir · `/`→project root · bare→sibling · outside-root dropped fail-closed · directory = WHOLE SUBTREE · absent = UNDECLARED grandfathered). Section reader: `_raw_phase_bodies` §-keyed (§5 has NO engine consumer today). Named-refusal grammar: `_die(f"<snake_code>: …")` (~35 codes; e.g. unflagged_freeze · tripwire_missing · heal_exhausted). check standing monitor precedent: build_tampered WARN at :1111 (early surface, never red — the GATE is where it bites).
Context (working folder): `.add/milestones/build-scope-lock/MILESTONE.md` — this task owns the milestone's other freeze-first contract: "git-free touched-file detection (snapshot mechanism: content-hash vs mtime, scope of the snapshot set)". MEASURED 2026-06-12 on this repo: snapshot population ≈3,950 files (6,233 incl. .add/archive; 85 MB); full-tree md5 walk = 0.49 s real (stdlib, cold-ish cache) — content-hash at advance is affordable; state.json is 32 KB today, a per-file snapshot adds ≈400 KB (sidecar-vs-state.json is contract material). NO gitignore-aware walker exists in add.py (that logic lives only in test helpers); the engine's only ignore precedent is the init-scan list (:348–350: .add · .git · CI/editor/legal scaffolding). Guard suites coupled to the seams this task extends: `test_tamper_tripwire.py` · `test_heal_then_escalate.py` · `test_high_risk_signal.py` · `test_archive_compaction.py` · `test_earned_green_rubric.py` (tripwire/tamper consumers) + `test_scope_decl_template.py` (the frozen grammar's token pins).
Honors (patterns / conventions): engine pin idiom — any add.py change re-aims `engine_pin.ENGINE_MD5` + syncs ×3 byte-identical trees; tool-agnostic engine (bytes + stdlib only, NO git — the milestone names the detection git-free); fail-closed everywhere (unreadable/deleted ⇒ touched, outside-root ⇒ dropped); grandfather rule from the frozen §5 grammar (absent Scope line = UNDECLARED ⇒ this gate must NOT retro-red old tasks); named refusal codes (snake_case prefix, audit-greppable); WARN-early/GATE-bite split (check warns, gate refuses); sandbox-only mutating-verb probes + grammar-drift fixtures (fv28); wording-guard sweep done — "scope of impact" is the surface vocabulary, `blast radius`/`seam` banned (scope-decl-template §7 lesson, applied at ground this time).
Anchors the contract cites: `_tripwire_snapshot` / `_tripwire_divergence` / `_tamper_guard` / `_heal_or_escalate` (placement + router, NOT rewired here) · `cmd_advance` tests→build block (:563–567) · `cmd_gate` completing path (:639–659) · `_declared_test_files` (:1911) + the scope-decl-template §3 v2 grammar · `_raw_phase_bodies` · `state["tasks"][slug]["tripwire"]` key shape (`{"contract_md5", "tests":{rel:md5}}`) · `engine_pin.ENGINE_MD5` (RE-PINNED by this task) · init-scan ignore list (:348).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: the verify gate enforces the declared §5 Scope — at the tests→build advance the engine parses the frozen Scope declaration and snapshots the project tree (git-free content-hash); at a COMPLETING gate it re-walks, diffs, and refuses with a named code when any touched file falls outside the declared scope. Grandfathered: a task with no Scope line is UNDECLARED — never retro-red. The heal routing of a violation is the NEXT task (scope-violation-heal); this gate refuses, it does not yet heal.
Framings weighed: full-tree content-hash snapshot + re-walk diff (chosen — mirrors `_tripwire_snapshot`, bytes-only witness, catches modify+add+delete; measured 0.49 s / ~3,950 files on this repo) · mtime+size snapshot (rejected — false negatives on revert-after-touch, mtime granularity lies; content is the only honest witness) · `git status` porcelain (rejected — the milestone freezes the detection GIT-FREE; the engine is tool-agnostic) · hash only the out-of-scope complement (rejected — saves little after exclusions, loses the in-scope/out-of-scope evidence split at gate, and couples the walk to a parse that may re-freeze)
Must:
<must>
  - a new parser `_declared_scope(root, slug)` reads the §5 `Scope (may touch):` line via the frozen scope-decl-template §3 v2 grammar: backticked tokens · FIRST declaring line · `./…` → task dir · token with `/` → project root · bare name → sibling of the previous token's dir · outside-root resolutions dropped fail-closed · a directory token covers its WHOLE SUBTREE · NO Scope line → None (UNDECLARED)
  - at the tests→build advance (same block as the tripwire, same UNCONDITIONAL-overwrite semantics): if the scope is declared, walk the project tree and snapshot `{rel_path: md5}`; the walk prunes a NAMED minimal exclusion set — `.git` · `.add` (engine domain, already guarded by tripwire+audit) · `__pycache__`/`*.pyc`/`.DS_Store` — nothing else, no gitignore parsing
  - the snapshot payload lives in a sidecar `.add/tasks/<slug>/scope-snapshot.json`; state.json carries the anchor `{"declared": [...], "snapshot_md5": <md5-of-sidecar-bytes>}` — a tampered/absent sidecar under a present anchor is itself a named refusal (fail-closed, tamper-equivalent to the tripwire's trust boundary)
  - at a COMPLETING gate (PASS / RISK-ACCEPTED) on a scope-anchored task: re-walk with the same exclusions, diff against the snapshot — modified + new + deleted files are TOUCHED; unreadable-at-gate counts as touched (fail-closed); refuse with `scope_violation: <rel paths>` when any touched path is outside every declared token (whole-subtree containment for directory tokens)
  - placement: immediately after `_tamper_guard` in the completing path, BEFORE the waiver write — a scope violation is never launderable through RISK-ACCEPTED; HARD-STOP is never blocked (stopping is always allowed)
  - grandfather: UNDECLARED tasks take NO snapshot and the gate SKIPS the check silently — pre-existing tasks and scope-less bundles stay valid forever (frozen grammar rule)
  - `add.py check` mirrors the build_tampered precedent: a non-done, scope-anchored task whose current walk already shows an out-of-scope touch surfaces a WARN (`scope_violation` pending) — early surface, never red; the GATE is where it bites
  - single-file-erase parity with the tripwire (v2, refute-driven): the sidecar and the anchor co-witness each other — an anchor-less task whose sidecar EXISTS is a `scope_anchor_missing` refusal at a completing gate; only the simultaneous two-file erase remains, the explicitly accepted floor
  - the declared->undeclared transition cleans up (v3, refute-disclosed): an UNDECLARED tests->build crossing pops the stale anchor and unlinks the stale sidecar — a task that legitimately removed its Scope line is never falsely refused by the previous declaration's leftovers
  - engine change discipline: ENGINE_MD5 re-pinned, ×3 trees byte-identical, all existing suites stay green ×2 interpreters; every new refusal/warn code is snake_case and audit-greppable
</must>
Reject:
<reject>
  - a completing outcome when touched ⊄ declared -> "scope_violation"
  - a present state.json anchor whose sidecar is missing or hash-mismatched -> "scope_snapshot_tampered" (never launderable; RISK-ACCEPTED refused the same way)
  - an ERASED anchor over a still-present sidecar -> "scope_anchor_missing" (v2 — the one-key state.json erase the refute-read reproduced; never a silent skip)
  - a Scope token resolving outside the project root -> dropped fail-closed at parse (never widens the allowlist; inherited from the frozen grammar)
  - an UNDECLARED task refused or warned for missing scope -> never: absence = grandfathered (retro-red is the named anti-goal)
  - any git invocation in the detection path -> never: bytes + stdlib only (tool-agnostic engine)
</reject>
After:
<after>
  - a completing gate on a scope-declared task is provably inside its declared blast area from bytes alone: the snapshot exists, the diff is empty outside scope, and a violation names its files and its code; UNDECLARED tasks behave exactly as before this version; the engine pin is re-aimed and all three trees match
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ the minimal NAMED exclusion set (.git · .add · pyc/junk) is enough for real projects — lowest confidence because artifact-heavy builds (node_modules, dist, target) will inflate the walk and read as out-of-scope touches; if wrong: false `scope_violation` reds or slow advances force an additive, named ignore seam in a follow-up change-request — the exclusion list is a single constant, so the re-freeze is cheap and additive
  ⚠ the sidecar+anchor split is tamper-equivalent to in-state storage — lowest confidence because a build could edit BOTH sidecar and state.json; if wrong: the gate is gameable by a deliberate two-file tamper — accepted boundary: state.json was ALWAYS inside the build's reach (the tripwire shares it); the method's defense stays discipline + audit, not cryptography
  - [ ] full-walk cost stays acceptable beyond this repo (0.49 s here; unmeasured on larger trees) — confirm at verify with a timing line
  - [ ] §4-declared test files never legitimately change during build (tripwire-frozen) so they never appear as touched — confirm in scenarios
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: the parser resolves the frozen grammar
  Given a TASK.md §5 with Scope (may touch): `./src/` `add-method/tooling/` `helpers.py`
  When _declared_scope resolves it
  Then ./src/ maps under the task dir, add-method/tooling/ under the project root, helpers.py as its sibling
  And a directory token contains its WHOLE subtree (a nested file is in scope)

Scenario: no Scope line means UNDECLARED
  Given a TASK.md §5 without a Scope line
  When _declared_scope resolves it
  Then it returns the UNDECLARED marker (None) — not an empty allowlist

Scenario: an outside-root token never widens the allowlist
  Given a Scope line declaring `../outside/`
  When the declaration is resolved
  Then the token is dropped fail-closed
  And a build touch under ../outside/ still counts as outside every declared token

Scenario: the advance snapshots a declared task
  Given a sandbox task at tests with a declared Scope and a frozen §3
  When add.py advance crosses tests->build
  Then .add/tasks/<slug>/scope-snapshot.json exists with {rel_path: md5} entries
  And state.json carries {"declared": [...], "snapshot_md5": <md5 of the sidecar bytes>}
  And the .git/.add/junk exclusions are absent from the snapshot

Scenario: a declared->undeclared re-cross cleans up its leftovers (v3)
  Given a scope-anchored task whose §5 Scope line is then removed
  When tests->build is re-crossed and the build touches a file outside the OLD declaration
  Then the gate completes normally — the stale anchor and sidecar were removed at the crossing
  And no scope refusal fires   # UNDECLARED is never refused, on every path

Scenario: an UNDECLARED task takes no snapshot and is grandfathered
  Given a sandbox task at tests with NO Scope line
  When it advances tests->build, builds, and gates PASS at verify
  Then no scope-snapshot.json is written, no anchor lands in state.json
  And the gate completes with no scope check and no warning   # never retro-red

Scenario: a re-crossed change-request re-snapshots cleanly
  Given a scope-anchored task returned to tests and re-advanced
  When the second tests->build crossing runs
  Then the sidecar and anchor are overwritten unconditionally (the tripwire's semantics)

Scenario: an in-scope build completes
  Given a snapshot, then a build that only modified files under the declared tokens
  When add.py gate PASS runs at verify
  Then the gate records PASS
  And tripwire-frozen §4 test files were never flagged as touched (they did not change)

Scenario: an out-of-scope MODIFY refuses with the named code
  Given a snapshot, then a build that modified a file outside every declared token
  When add.py gate PASS runs
  Then it dies with scope_violation naming the offending rel path
  And the task stays at verify, gate unrecorded   # nothing ships on a violation

Scenario: an out-of-scope NEW file and a DELETED file are touches too
  Given a snapshot, then a new file created (and another deleted) outside scope
  When add.py gate PASS runs
  Then both paths appear in the scope_violation refusal

Scenario: a violation is never launderable through RISK-ACCEPTED
  Given a pending out-of-scope touch
  When add.py gate RISK-ACCEPTED --owner x --ticket y --expires z runs
  Then it dies with scope_violation BEFORE the waiver is recorded
  And no waiver lands in state.json

Scenario: a tampered or missing sidecar is its own refusal
  Given a scope-anchored task whose scope-snapshot.json is edited (or deleted) after the advance
  When a completing gate runs
  Then it dies with scope_snapshot_tampered
  And the anchor in state.json is unchanged   # fail-closed, evidence preserved

Scenario: an erased anchor over a living sidecar is its own refusal (v2)
  Given a scope-anchored task whose state.json scope key is deleted while scope-snapshot.json remains
  When a completing gate runs
  Then it dies with scope_anchor_missing
  And the sidecar is untouched   # the co-witness caught the one-file erase; only the two-file erase remains (accepted floor)

Scenario: HARD-STOP is never blocked
  Given a pending out-of-scope touch
  When add.py gate HARD-STOP runs
  Then the stop is recorded normally   # stopping is always allowed

Scenario: check surfaces a pending violation early as WARN
  Given a non-done scope-anchored task with an out-of-scope touch already on disk
  When add.py check runs
  Then a scope_violation-pending WARN appears
  And check stays green (never red) — the gate is where it bites

Scenario: the engine pin discipline holds
  Given the build is complete
  When the parity and pin guards run
  Then add.py is byte-identical x3 and engine_pin.ENGINE_MD5 equals the new add.py md5
  And every pre-existing suite stays green on two interpreters
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
NEW engine seams (add.py — ×3 trees + ENGINE_MD5 re-pin; stdlib only, no git):

_SCOPE_EXCLUDES: dir names pruned at ANY depth = (".git", ".add", "__pycache__",
  "node_modules") · file junk skipped = ("*.pyc", ".DS_Store")
  — ONE named constant; widening it later is an additive change-request, never silent

_declared_scope(root, slug) -> list[str] | None
  §5 `Scope (may touch):` FIRST declaring line · backticked tokens · the frozen
  scope-decl-template grammar (./… task dir · "/" project root · bare = sibling of
  previous · outside-root dropped fail-closed · directory = WHOLE SUBTREE)
  returns project-root-relative strings, directory tokens carry a trailing "/"
  None = no Scope line (UNDECLARED) · [] = line present but every token dropped
  (a garbage declaration grants NO cover: empty allowlist, every touch violates)

_scope_walk(rootp) -> dict[rel, md5]
  os.walk from the project root, prunes _SCOPE_EXCLUDES; a file unreadable at
  SNAPSHOT time is skipped; any path unreadable at GATE time counts as touched

sidecar  .add/tasks/<slug>/scope-snapshot.json = {"version": 1, "files": {rel: md5}}
anchor   state["tasks"][slug]["scope"] = {"declared": [...], "snapshot_md5": <md5
  of the sidecar bytes>}
  written in the cmd_advance tests->build block DIRECTLY AFTER the tripwire line
  (:567) · UNCONDITIONAL overwrite on every crossing · an UNDECLARED crossing
  CLEANS UP instead (v3): pops the stale anchor + unlinks the stale sidecar, so a
  declared->undeclared re-cross can never be falsely refused (the frozen
  "UNDECLARED is never refused" Reject clause holds on every path)

_scope_guard(root, state, slug)   called in cmd_gate's completing path IMMEDIATELY
  after _tamper_guard, BEFORE the waiver write; HARD-STOP never calls it
  anchor × sidecar truth table (v2 — the sidecar is the co-witness, born in the
  same tests->build crossing, so EITHER single-file erase is caught; only the
  accepted two-file erase floor remains):
    anchor present · sidecar matching  -> enforce
    anchor present · sidecar missing/diverged/unparseable
                                 -> _die("scope_snapshot_tampered: task '<slug>' — …")
    anchor ABSENT  · sidecar PRESENT
                                 -> _die("scope_anchor_missing: task '<slug>' — …")
    anchor absent  · sidecar absent -> return          (UNDECLARED / legacy: silent)
  touched := modified ∪ added ∪ deleted vs snapshot (re-walk, same exclusions)
  out     := touched outside every declared token (file = exact rel · dir = prefix)
  out != [] -> _die("scope_violation: task '<slug>' touched outside its declared
               §5 Scope — <p1> · <p2> · … (N total)")   # list caps at 5 paths + count

check (standing monitor): a non-done, scope-anchored task whose current walk already
  shows out-of-scope touches -> WARN carrying "scope_violation" + "pending" — never red

UNCHANGED: _tamper_guard / _heal_or_escalate (the heal routing of a scope violation
is the NEXT task) · every existing CLI surface · the §5 template text (consumed, not
edited). New codes: scope_violation · scope_snapshot_tampered · scope_anchor_missing
(snake_case, greppable).
```

Status: FROZEN @ v3 — approved by Tin Dang (2026-06-12, close-gap-before-gate micro change-request: the delta refute pass EARNED v2 but disclosed the declared->undeclared stale-anchor false-refusal — v3 adds the UNDECLARED-crossing cleanup so the frozen "UNDECLARED is never refused" clause holds on every path. v2 same day: the anchor×sidecar truth table restoring single-file-erase parity after the v1 anchor-erase REFUTE. v1 approved earlier the same day with the two original flags).
Least-sure flag surfaced at freeze: ⚠ [contract] after v2 the irreducible floor is the TWO-file erase (anchor + sidecar together = indistinguishable from legacy/UNDECLARED) — accepted explicitly; if wrong: the refute pass could name no narrower hole, and the tripwire shares the same editable-state floor. ⚠ [contract] the minimal NAMED exclusion set may false-red artifact-heavy builds — if wrong: an additive widening change-request of ONE constant.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: all 14 scenarios pinned; pre-existing suite count (871) never decreases; ×2 interpreters. RED drivers: 10 tests fail today on clean AssertionErrors because the seams do not exist (`_declared_scope`/`_scope_guard` absent, no sidecar written, gate completes despite out-of-scope touches, check silent). FOUR GREEN pins at write (declared honestly — grandfather + non-regression pins that must hold both before AND after the build): test_advance_skips_undeclared · test_gate_in_scope_pass · test_hard_stop_never_blocked · test_mirrors_and_pin.
Red run (2026-06-12): `Ran 14 · FAILED (failures=10)` — all 10 are AssertionErrors on the missing seams (zero incidental errors); the 4 declared pins green.
Red run v2 (2026-06-12, change-request): test_anchor_erase_refused fails `AssertionError: 0 == 0 : the gate must refuse` against the v1 engine — the exact bypass the refute-read reproduced; the other 14 stay green.
Red run v3 (2026-06-12, change-request): test_undeclared_recross_cleans_up fails `'scope' unexpectedly found … the stale anchor must be popped at an UNDECLARED crossing` against the v2 engine — the exact transition the delta pass disclosed; the other 15 stay green.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_parser_resolves_grammar: §5 fixture with ./src/ + rooted dir + bare sibling / resolve / assert rel mapping + whole-subtree containment of a nested path
  - test_parser_undeclared_none: no Scope line -> None, NOT []
  - test_parser_outside_root_dropped: `../outside/` declared -> dropped; resolution [] (empty allowlist ≠ UNDECLARED)
  - test_advance_snapshots_declared: sandbox task, declared scope, tests->build / sidecar exists with {rel: md5} / anchor in state.json / .git//.add//junk paths absent from snapshot
  - test_advance_skips_undeclared: no Scope line -> no sidecar, no anchor
  - test_recross_resnapshots: phase back to tests, re-advance -> sidecar + anchor overwritten (mtimes/md5 change with a changed tree)
  - test_gate_in_scope_pass: modify only under declared tokens / gate PASS records / §4 test files unflagged
  - test_gate_out_of_scope_modify_refused: modify outside / gate PASS dies scope_violation naming the rel path / task stays verify, gate unrecorded
  - test_gate_new_and_deleted_refused: create + delete outside / both rel paths in the refusal message
  - test_waiver_not_launderable: RISK-ACCEPTED with owner/ticket/expires dies scope_violation / no waiver in state.json
  - test_sidecar_tamper_refused: edit sidecar bytes post-advance / completing gate dies scope_snapshot_tampered / anchor unchanged
  - test_anchor_erase_refused (v2): delete the state.json scope key, keep the sidecar / completing gate dies scope_anchor_missing / sidecar untouched
  - test_undeclared_recross_cleans_up (v3): arm declared, remove the Scope line, re-cross tests->build / anchor popped + sidecar unlinked / out-of-old-scope touch gates PASS cleanly
  - test_hard_stop_never_blocked: pending violation / gate HARD-STOP records normally
  - test_check_warns_pending: out-of-scope touch on disk, non-done task / check output carries scope_violation + pending as WARN / exit stays green
  - test_mirrors_and_pin: md5(add.py) ×3 equal AND == engine_pin.ENGINE_MD5 (GREEN pin at write; survives the re-pin)
</test_plan>

Tests live in: `add-method/tooling/test_scope_gate_enforce.py` · MUST run red (missing seams) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/src/add_method/_bundled/tooling/add.py` `.add/tooling/add.py` `add-method/tooling/test_scope_gate_enforce.py`
Strategy (ordered batches): 1. parser `_declared_scope` + grammar fixtures green · 2. walk + snapshot at advance (sidecar + anchor) · 3. `_scope_guard` at the gate (violation + tamper + waiver paths) · 4. check WARN monitor · 5. re-pin ENGINE_MD5 + sync ×3 + full suite ×2 interpreters
Safety rule (feature-specific): fail-closed in every ambiguity — unreadable file = touched, garbage token = no cover, missing sidecar under an anchor = refusal; and the grandfather is sacred: an UNDECLARED task must be byte-for-byte indistinguishable from today's behavior.
Code lives in: `add-method/tooling/add.py` (synced ×3) · tests beside the suite.
Constraints: do NOT change any test or the contract; stdlib only, no git; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — task suite 16/16; full suite 887/887 OK on python3.14.5 AND python3.10.20 (delta pass also confirmed on 3.11.15)
- [x] coverage did not decrease — suite 871 → 887 (+16); zero failures; each contract version added its red test before its build (10 v1 + 1 v2 + 1 v3 red runs recorded in §4)
- [x] no test or contract was altered during build — each human-approved change-request (v2, v3) re-armed the tripwire via phase tests→build; `add.py check` 267/0, no build_tampered
- [x] the green was EARNED — TWO adversarial refute passes: pass 1 REFUTED v1 (anchor-erase bypass, reproduced empirically) → v2 truth table; delta pass 2 EARNED v2 (original bypass confirmed DEAD by repro; 15 vectors CLEARED incl. symlinks, prefix collisions, re-snapshot games, laundering; the regression-pin probe confirmed test_anchor_erase_refused catches a v1-revert) and disclosed the stale-anchor false-refusal → closed as v3 BEFORE this gate
- [x] concurrency / timing — single-process CLI engine, no shared mutable state across invocations beyond state.json (existing model); the walk is read-only; snapshot writes are whole-file
- [x] no exposed secrets, injection openings, or unexpected dependencies — stdlib only, no git, no subprocess in the new seams; snapshot stores only paths + md5
- [x] layering & dependencies follow CONVENTIONS.md — clones the §4 grammar verbatim (one NAMED divergence), mirrors the tripwire's placement + overwrite + WARN-early/GATE-bite split; ENGINE_MD5 re-aimed (fadd8f7242d3eb07070f779281d3cb7b) ×3 byte-identical; refusal codes snake_case (scope_violation · scope_snapshot_tampered · scope_anchor_missing)
- [x] a person reviewed and approved the change — Tin Dang approved freeze v1 + change-requests v2/v3 in-chat; THIS gate is human-held (autonomy: conservative, risk: high)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — every new symbol referenced: _declared_scope+_scope_walk ← cmd_advance hook; _scope_findings ← _scope_guard + cmd_check monitor; _scope_guard ← cmd_gate completing path; _in_scope ← _scope_findings; confirmed by the suite exercising each path through the REAL CLI (no direct unit calls except the parser tests)
- [x] DEAD-CODE (code) — no orphan: all 6 new names consumed (refute pass mapped clause→code→test); the v3 else-branch exercised by test_undeclared_recross_cleans_up
- [x] SEMANTIC (prose / non-code) — n/a beyond the engine_pin re-aim annotation (read in full; documents the v1→v3 history and the carried prior gates)

### GATE RECORD
Outcome: PASS
Human-held gate (risk: high · autonomy: conservative) — recorded on Tin Dang's in-chat decision over the full evidence: two refute passes (v1 REFUTED → fixed; delta EARNED with its disclosure closed as v3 before this gate), 887/887 ×2 interpreters, tripwire clean, both residual boundaries accepted at freeze.
Reviewed by: Tin Dang (gate) · refute subagents ×2 (earned-green) · date: 2026-06-12

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the first REAL scope_violation refusal on a live task (proves the gate bites outside sandboxes); advance latency on declared tasks (the walk added ~0.5 s here — watch it on bigger trees); false-red reports from artifact-heavy projects (the accepted exclusion-set flag's failure mode).
Spec delta for the next loop: scope-violation-heal routes the `scope_violation` refusal through `_heal_or_escalate` (source tag + shared HEAL_CAP) instead of dying in place — the refusal message and the truth table here are its frozen inputs.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [TDD · folded] a co-witness pair must be born ATOMICALLY in the same crossing or single-file erasure splits them — the tripwire got this right by accident of history (flag_verified born with it); new snapshot seams must design the witness in (evidence: refute pass 1 reproduced the anchor-erase bypass scope_anchor_missing now blocks)
- [ADD · folded] every state-creating seam needs its state-REMOVING transition specified in the same contract — declared->undeclared had no cleanup path until a refute pass disclosed it (evidence: v3 change-request; test_undeclared_recross_cleans_up)
- [SDD · folded] "same trust boundary as X" is a testable parity CLAIM, not a rhetorical flag — the refuter falsified it empirically and the contract had to be re-frozen (evidence: v1 flag #2 vs the one-key erase repro)
- [TDD · folded] declare green pins by NAME in §4 (not "one pin") — this task declared 4 and the refute pass audited each against its claim (evidence: §4 coverage line; refute pass green-pin honesty check)

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
