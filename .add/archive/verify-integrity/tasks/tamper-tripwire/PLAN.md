# TASK: Mechanical tamper tripwire — freeze test+contract md5 at tests→build, flag any edit at verify

slug: tamper-tripwire · created: 2026-06-11 · stage: mvp · risk: high
autonomy: conservative   <!-- lowered from project default `auto`: this task adds the method's FIRST mechanical HARD-STOP + new engine state — verify must escalate to the human, never auto-pass. -->
<!-- risk: high declared — the engine refuses an unguarded completion (unguarded_high_risk_auto). -->
<!-- inherited project default is `auto` (manual < conservative < auto); kept conservative here on purpose. -->
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
  - `add-method/tooling/add.py:cmd_advance` (528–559) — advances one phase; next is POSITIONAL (`PHASES.index(cur)+1`). Already has an `if nxt == "build":` block (the `unflagged_freeze` check + sets `state[...]["flag_verified"]`). THE snapshot seam: take the md5 snapshot inside this exact block, on `tests→build`.
  - `add-method/tooling/add.py:cmd_gate` (613–660) — records PASS/RISK-ACCEPTED/HARD-STOP; the `if completing:` block writes `state[...]["gate"]`. THE re-check seam: compare snapshot vs current before any completing outcome; divergence → `_die(...)` HARD-STOP.
  - `add-method/tooling/add.py:load_state`(180–188)/`save_state`(212–214) — per-task dict `state["tasks"][slug]`; a new `"tripwire": {"contract_md5": str, "test_files_md5": {path: md5}}` key slots in (no schema enforcement). Mirrors `flag_verified`/`waiver` keys.
  - `add-method/tooling/add.py:_tests_count`(1676–1680) → `.add/tasks/<slug>/tests/*.py` (PRIMARY, stable) · `_declared_tests_count`(1693–1729) §4 `Tests live in:` fallback (⚠ stateful/order-dependent) · `_tests_info`(1732–1741) selects (primary wins >0) · `_count_test_defs`(1667) the `def test_` regex · `_confined`(1683) no-`..`/no-symlink guard. The tripwire must REUSE this resolution to hash the SAME file set, never re-glob.
  - `add-method/tooling/add.py:_raw_phase_bodies`(1912–1919)`.get(3,"")` via `_phase_spans`(1885–1909) — extracts the raw §3 CONTRACT text to hash. ⚠ `_phase_spans` truncates a §body on an inline `## ` / bare `---` (rare).
  - `add-method/tooling/add.py:cmd_check`(999–1132) — WARN idiom (`warnings.append((name, reason))`, never-red) e.g. `task_not_grounded`(1116) — the shape a standing "stale tripwire / tampered" monitor mirrors.
  - `add-method/tooling/engine_pin.py:ENGINE_MD5`(13) = `e6b8c3da98ef092c38f5d1c78760c4ad` — MUST bump (canonical add.py changes). Sync ×3 add.py trees.
  - `add-method/tooling/test_tamper_tripwire.py` (NEW) — stdlib unittest; the red guard (snapshot taken at tests→build · a post-red test/contract edit detected at verify · pin/×3 parity).
Context (working folder):
  - docs — `.add/milestones/verify-integrity/MILESTONE.md` (the shared contract: snapshot SHAPE+storage+timing is the freeze-first risky contract; tamper = a measure WITH TEETH unlike never-red WARNs). `.claude/skills/add/phases/6-verify.md` (where the tamper flag surfaces — Part one "No test or contract altered during build" is today a manual checkbox this task mechanizes).
  - config/data — `.add/state.json` (the live per-task state the snapshot persists into); `.add/tasks/tamper-tripwire/tests/` (this task's own primary test dir — the stable path the tripwire keys on).
  - no todos relevant.
Honors (patterns / conventions):
  - **engine pin ×3** — canonical add.py edit → `cp` ×2 mirrors → bump `engine_pin.ENGINE_MD5` → md5 parity (the release-gate idiom).
  - **fail-closed / OSError→safe default** — the existing test-count + state readers fail closed; the snapshot/hash must too (a missing file → recorded-absent, never a crash; CLAUDE.md "design for failure").
  - **measure mirrors the proven shape, but this one has TEETH** — the standing monitor uses the never-red WARN idiom; the GATE check is the method's FIRST mechanical HARD-STOP (deliberate, milestone-defining).
  - **reuse the canonical resolver, never re-implement** — hash the file set `_tests_info`/`_declared_tests_count` resolve, so the snapshot and the engine agree.
  - **never weaken a test / edit a frozen contract** (CONVENTIONS + add.py:266) — this task gives that rule mechanical enforcement.
Anchors the contract cites: `cmd_advance` `if nxt == "build":` (snapshot point) · `cmd_gate` `if completing:` (re-check point, `_die` HARD-STOP) · `state["tasks"][slug]["tripwire"]` (the persisted snapshot shape) · `_tests_info`/`_declared_tests_count`/`_confined` (the test-file resolution reused) · `_raw_phase_bodies(...).get(3,"")` (the §3 text hashed) · `cmd_check` WARN idiom (the standing stale/tamper monitor) · `engine_pin.ENGINE_MD5` (the pin bump) · `test_tamper_tripwire.py` (the new guard)

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Mechanical tamper tripwire — freeze the md5 of the red test files + the frozen §3 contract at the `tests→build` advance; at the verify gate, refuse a completing outcome if any of them changed since the red run.
Framings weighed: snapshot in `state.json` keyed per task, co-witnessed by `flag_verified` (chosen — reuses the existing per-task dict + the existing snapshot moment; tool-agnostic) · a separate sidecar hash file under the task dir (rejected — a second file to keep in sync, same writable-tree weakness, more surface) · git-diff since the tests commit (rejected — assumes git, breaks tool-agnostic).
Must:
<must>
  - SNAPSHOT at `tests→build`: inside `cmd_advance`'s existing `if nxt == "build":` block, UNCONDITIONALLY overwrite `state["tasks"][slug]["tripwire"] = {"contract_md5": md5(raw §3 text), "tests": {relpath: md5(bytes)}}`. The test set is exactly what `_tests_info`/`_declared_tests_count` resolve (REUSE the resolver, never re-glob); the §3 text is `_raw_phase_bodies(root,slug).get(3,"")`. Overwrite (not write-if-absent) so a legitimate change-request that re-crosses `tests→build` re-snapshots cleanly. `flag_verified` is already set in this same block — it is the co-witness.
  - RE-CHECK at the verify gate: inside `cmd_gate`, BEFORE writing any COMPLETING outcome (PASS | RISK-ACCEPTED), re-resolve + re-hash. Any tracked test file whose md5 differs, any tracked test file now missing, OR a changed §3 contract md5 → `_die` HARD-STOP refusing the outcome (the task stays at `verify` for an honest redo — exactly like the existing `unflagged_freeze` block guard). A tamper finding is HARD-STOP-class — NOT launderable through RISK-ACCEPTED.
  - TRI-STATE absent-snapshot, CO-WITNESSED by `flag_verified` (closes the self-erase bypass): snapshot present + all match → pass through. Present + any divergence → block. Absent → split by the co-witness: `flag_verified` true but `tripwire` absent ⇒ SUSPICIOUS (the snapshot was crossed-then-erased) → block/escalate (`tripwire_missing`); both absent ⇒ LEGACY (a task that predates this feature) → skip, never block.
  - FAIL-CLOSED: any md5/read error on a tracked file → treat that file as DIVERGED (block at the gate), never crash (CLAUDE.md design-for-failure; mirrors the existing OSError→safe-default readers).
  - STANDING MONITOR: `cmd_check` emits a never-red WARN when a non-done task's tripwire diverges (early signal; the GATE is where it actually bites). Mirrors the `task_not_grounded` WARN idiom — `check` still exits 0.
  - SYNC ×3 add.py byte-identical + bump `engine_pin.ENGINE_MD5`.
  - NECESSARY-NOT-SUFFICIENT (stated so a green tripwire is not over-trusted): the tripwire proves only "the red test files + frozen §3 are UNCHANGED since the red run" — NOT that the tests were strong, non-vacuous, or actually red. Strength/vacuity is task 2's adversarial refute-read (`earned-green-rubric`); red-before-build is the existing tests-phase gate. A clean tripwire means "the evidence wasn't edited", not "the build was honest".
</must>
Reject:
<reject>
  - a tracked test file weakened / deleted / `skip`-marked after the red run, detected at the gate -> "build_tampered" (HARD-STOP)
  - the frozen §3 contract text edited after `tests→build`, detected at the gate -> "contract_tampered" (HARD-STOP)
  - the `tripwire` snapshot erased while `flag_verified` still stands (suspicious-absent) -> "tripwire_missing" (HARD-STOP / escalate)
  - a tamper divergence presented as RISK-ACCEPTED -> still HARD-STOP (a cheat is never launderable; non-security RISK-ACCEPTED does not apply)
  - (OUT of scope — owned by `heal-then-escalate`: the ≤3 honest-redo attempt counter + the after-3 escalation. Task 1 only DETECTS + blocks; the loop budget wraps this block.)
</reject>
After:
<after>
  - every task that crosses `tests→build` carries a `state[...]["tripwire"]` snapshot (test+contract md5s) alongside the existing `flag_verified`.
  - a verify completing outcome (PASS/RISK-ACCEPTED) is reachable only when the red suite + frozen §3 are byte-identical to that snapshot, OR the task is honestly legacy-absent.
  - add.py is byte-identical ×3; `engine_pin.ENGINE_MD5` is bumped; the full unittest suite is green; `add.py check` is clean (the new WARN is never-red).
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [contract] the snapshot lives in `.add/state.json` — the SAME tree a cheating build agent can write. The `flag_verified` co-witness raises a bypass from "delete one key" to "forge BOTH `tripwire` and `flag_verified` consistently", but a determined agent that patches both still slips the mechanical floor. v1 ACCEPTS this residual as an HONEST CEILING — the tripwire's job is to RAISE THE COST, with the adversarial refute-read (task 2) + the human gate as the backstops; a fully unbypassable floor needs git or an external secret (rejected — not tool-agnostic). Lowest confidence because it decides whether the milestone delivers TEETH or only the APPEARANCE of teeth. If the human rejects this stance: the milestone needs an external-witness redesign. → surfaced as the §3 freeze flag.
  - [ ] [contract] absent-snapshot is split by `flag_verified` — this holds only if `reopen` + re-advance actually RE-CROSS `tests→build` (so the snapshot refreshes) and `flag_verified`/`tripwire` never desync. Confirm `reopen` walks back past `tests→build`; if it can land at `verify` with a stale snapshot, a legit change false-positives forever.
  - [ ] [spec] the §3 hash uses `_raw_phase_bodies().get(3,"")`, which `_phase_spans` truncates on an inline `## ` / bare `---` inside the contract body — CONSISTENT at snapshot + check (no false positive), but it leaves an undetected-edit window past the first such marker. Accept as a documented known-limit vs hash the raw slice a different way.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: snapshot taken at tests->build
  Given a task at phase `tests` with one resolved red test file and a frozen §3
  When `add.py advance` crosses into `build`
  Then state["tasks"][slug]["tripwire"] holds contract_md5 + a tests:{relpath:md5} entry
  And flag_verified is set in the same block (the co-witness)

Scenario: snapshot overwrites on re-cross (legit change-request)
  Given a task that already has a tripwire snapshot
  When the contract is reopened, re-frozen, and `advance` re-crosses tests->build
  Then the tripwire is OVERWRITTEN with the new md5s (not write-if-absent)
  And the prior snapshot's hashes do not survive

Scenario: weakened test blocks the gate
  Given a tripwire snapshot of the red test files
  When an assert in a tracked test file is weakened and `add.py gate PASS` is run
  Then the engine HARD-STOPs with "build_tampered" naming the changed file
  And no PASS is recorded (the task stays at verify)

Scenario: deleted test blocks the gate
  Given a tripwire snapshot of the red test files
  When a snapshotted test file is removed and `add.py gate PASS` is run
  Then the engine HARD-STOPs with "build_tampered" naming the missing file
  And no PASS is recorded

Scenario: frozen contract edit blocks the gate
  Given a tripwire snapshot of the §3 contract
  When the §3 contract text is edited after tests->build and `gate PASS` is run
  Then the engine HARD-STOPs with "contract_tampered"
  And no PASS is recorded

Scenario: clean build passes
  Given a tripwire snapshot and no change to the tracked files since the red run
  When `add.py gate PASS` is run
  Then the gate proceeds and records PASS
  And the tripwire is left intact

Scenario: legacy task with no snapshot skips
  Given a task with NO tripwire AND flag_verified false (predates the feature)
  When `add.py gate PASS` is run
  Then the tamper check skips and the gate proceeds
  And no tamper block is raised

Scenario: suspicious-absent (self-erased snapshot) blocks
  Given flag_verified true but the tripwire key erased
  When `add.py gate PASS` is run
  Then the engine HARD-STOPs with "tripwire_missing"
  And no PASS is recorded

Scenario: a tamper finding is not launderable
  Given a tripwire divergence (a weakened test)
  When `add.py gate RISK-ACCEPTED ...` is run
  Then the engine still HARD-STOPs (a cheat is never RISK-ACCEPTED-waived)
  And no RISK-ACCEPTED is recorded

Scenario: fail-closed on an unreadable tracked file
  Given a tripwire snapshot
  When a tracked test file can no longer be read (OSError) and `gate PASS` is run
  Then that file is treated as DIVERGED and the engine HARD-STOPs
  And the engine does not crash

Scenario: standing monitor warns but never reddens check
  Given a non-done task whose tracked files diverge from its snapshot
  When `add.py check` is run
  Then a never-red WARN names the tampered task
  And `check` still exits 0
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
TAMPER TRIPWIRE — engine contract (add.py, no HTTP surface)

SNAPSHOT  cmd_advance, on tests->build (inside the existing `if nxt == "build":` block):
  state["tasks"][slug]["tripwire"] = {                       # UNCONDITIONAL overwrite
    "contract_md5": md5(_raw_phase_bodies(root, slug).get(3, "")),
    "tests": { relpath: md5(open(relpath,'rb').read())       # relpath as _tests_info resolves
               for relpath in resolved_test_files(root, slug) },
  }
  # flag_verified is already set in this same block — it is the absent-snapshot co-witness.
  # resolved_test_files REUSES _tests_info / _declared_tests_count / _confined (never re-globs).

CHECK  cmd_gate, BEFORE writing a COMPLETING outcome (PASS | RISK-ACCEPTED):
  tw = state["tasks"][slug].get("tripwire")
  if tw is None:
      if state["tasks"][slug].get("flag_verified"):
          _die HARD-STOP "tripwire_missing"          # suspicious-absent (crossed then erased)
      else:
          pass                                       # legacy-absent → skip, never block
  else:
      diffs = []
      if md5(_raw_phase_bodies(root,slug).get(3,"")) != tw["contract_md5"]:
          diffs.append("contract_tampered")
      for relpath, snap_md5 in tw["tests"].items():
          cur = md5_or_None(relpath)                 # read error / missing → None (fail-closed)
          if cur != snap_md5: diffs.append("build_tampered:"+relpath)
      if diffs: _die HARD-STOP diffs                 # NOT launderable via RISK-ACCEPTED
      # else: proceed to record the completing outcome

STANDING  cmd_check (non-done task, tripwire present + any divergence):
  warnings.append(("build_tampered", "<task> tampered since red run: <files>"))   # never-red

State key (load_state/save_state, no schema enforcement):
  state["tasks"][slug]["tripwire"] = {"contract_md5": str, "tests": {relpath: md5}}

Invariants:
  - fail-closed: any md5/read error on a tracked file → that file counts as DIVERGED (block).
  - HARD-STOP-class: a tamper divergence is never recorded as PASS or RISK-ACCEPTED.
  - necessary-not-sufficient: proves "red suite + frozen §3 UNCHANGED", NOT "tests strong/red".
  - tool-agnostic: hashes file bytes only; never runs tests, never measures coverage.
  - sync: add.py byte-identical ×3; engine_pin.ENGINE_MD5 bumped.
  - out of scope: the ≤3 attempt counter + escalation (heal-then-escalate).

Known limit (documented, not fixed here): _phase_spans truncates §3 on an inline `## ` /
  bare `---`; consistent at snapshot + check (no false positive) but leaves an undetected-edit
  window past the first such marker inside a contract body.
```

Status: FROZEN @ v1 — approved by Tin Dang 2026-06-11.
Least-sure flag surfaced at freeze: [contract] the snapshot lives in the agent-writable `.add/state.json`; the `flag_verified` co-witness raises a bypass from "delete one key" to "forge two consistently", but a determined agent patching both still slips the mechanical floor. v1 ACCEPTS this as an honest ceiling — the tripwire RAISES the cost; the adversarial refute-read (task 2) + the human gate are the backstops. A fully unbypassable floor needs git / an external secret (rejected — breaks tool-agnostic). Human chose "Freeze — accept honest ceiling".
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: every Must + every Reject (the snapshot, the gate re-check, the tri-state, the invariants). Engine behavior, not line %.
Plan (one test per scenario, asserting behavior not internals — each builds a temp `.add/` project, drives `add.py` via its CLI/functions):
<test_plan>
  - test_snapshot_taken_on_tests_to_build: advance a task tests->build / assert state[slug]["tripwire"] has contract_md5 + tests{} / assert flag_verified also set
  - test_snapshot_overwrites_on_recross: snapshot, reopen+refreeze+re-advance / assert the md5s changed to the new content (not the stale ones)
  - test_weakened_test_blocks_gate: snapshot, weaken an assert, gate PASS / assert HARD-STOP "build_tampered" + phase still verify (no PASS)
  - test_deleted_test_blocks_gate: snapshot, delete a tracked test file, gate PASS / assert HARD-STOP names the missing file + no PASS
  - test_contract_edit_blocks_gate: snapshot, edit §3 text, gate PASS / assert HARD-STOP "contract_tampered" + no PASS
  - test_clean_build_passes_gate: snapshot, no change, gate PASS / assert gate recorded PASS + phase done + tripwire intact
  - test_legacy_absent_skips: task with no tripwire AND flag_verified false, gate PASS / assert proceeds, no tamper block
  - test_suspicious_absent_blocks: flag_verified true + tripwire erased, gate PASS / assert HARD-STOP "tripwire_missing" + no PASS
  - test_tamper_not_launderable_via_risk_accepted: divergence, gate RISK-ACCEPTED / assert still HARD-STOP + no RISK-ACCEPTED recorded
  - test_fail_closed_on_unreadable_file: divergence simulated by an unreadable/missing tracked file, gate PASS / assert HARD-STOP, no crash/traceback
  - test_standing_warn_never_red: non-done tampered task, run check / assert a WARN names it AND check exit code is 0
  - test_clean_risk_accepted_records_waiver: clean (no tamper) RISK-ACCEPTED still records its signed waiver (guards the tamper check sits BEFORE the waiver-write block, not breaking it)
</test_plan>
The ×3 add.py parity + the engine_pin.ENGINE_MD5 bump are NOT re-tested here — the existing `test_shared_engine_pin.py::test_pin_matches_all_three_engines` already reds automatically when canonical add.py changes without a synced ×3 + bumped pin.

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- The actual engine suite runs from add-method/tooling/test_tamper_tripwire.py (the canonical
     unittest tree). Test files are NOT mirrored ×3 — only add.py / templates / skill / docs are.
     This `./tests/` declaration is the method's user-facing convention; for THIS engine-dogfood task
     the dir is intentionally empty (the real tests live in the canonical tree), so the snapshot
     protects this task's §3 contract only — necessary-not-sufficient, exactly as §1 states. -->
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Safety rule (feature-specific): <e.g. debit+credit in one atomic transaction>
Code lives in: `./src/`
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 815 OK (was 803 + the new 12 tamper-tripwire tests); the 12 ran RED before build (8 FAIL + 1 ERROR core; 3 over-block guards green) → GREEN after.
- [x] coverage did not decrease — +12 behavior tests; the `_tests_count`/`_declared_tests_count` refactor PRESERVED every count (delegates to the new `_primary_test_files`/`_declared_test_files`); no existing test changed.
- [x] no test or contract was altered during build — now MECHANICALLY self-enforced: this very task carries a tripwire (`contract_md5 786a844e…`, tests `{}` — §3-only for this engine-dogfood task); the 12-test suite proves a weakened/deleted test or edited §3 HARD-STOPs the gate.
- [x] concurrency / timing — N/A: single-process CLI, no concurrency added; the snapshot rides the existing atomic `save_state` (temp + os.replace). No new shared-state race.
- [x] no exposed secrets, injection openings, or unexpected dependencies — only `import hashlib` (stdlib) added; no external dep; paths stay inside `_confined` (no `..`/symlink escape).
- [x] ⚠ SECURITY-LINE CLASSIFICATION — HUMAN-RATIFIED (Tin Dang, 2026-06-11, "PASS — ratify both"): md5 is tamper-EVIDENCE, not authentication, and is NOT a security HARD-STOP — consistent with `engine_pin`'s file-identity idiom; the realistic bypass is editing state.json directly (the already-accepted honest ceiling), NOT forging an md5. This classification was NEW (not in the §3 freeze flag), so it was surfaced for explicit human sign-off at the gate rather than self-granted.
- [x] layering & dependencies follow CONVENTIONS.md — new helpers are PURE + fail-closed (mirror the existing resolver/state-reader idioms); the gate guard mirrors the `unflagged_freeze` block; the standing WARN mirrors `task_not_grounded`.
- [x] a person reviewed and approved the change — risk: high / autonomy: conservative → Tin Dang owned this gate and recorded PASS (2026-06-11), ratifying both the md5 classification and that this closes task 1 of 3 (mechanical floor only).

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — every new symbol is referenced: `_primary_test_files`→(`_tests_count`,`_resolved_test_files`) · `_declared_test_files`→(`_declared_tests_count`,`_resolved_test_files`) · `_resolved_test_files`→`_tripwire_snapshot` · `_md5_text`/`_md5_file`→(`_tripwire_snapshot`,`_tripwire_divergence`) · `_tripwire_snapshot`→`cmd_advance` · `_tripwire_divergence`→(`_tamper_guard`,`cmd_check`) · `_tamper_guard`→`cmd_gate`. All resolve; suite green confirms.
- [x] DEAD-CODE (code) — no orphan: the two refactored counters keep every prior caller; no symbol added without a reference.
- [x] SEMANTIC (prose / non-code) — the frozen §3 contract + the §1 honest-ceiling flag read in full; the implementation honors the frozen shape (snapshot-at-tests→build · check-before-waiver-write · tri-state co-witness · fail-closed) with no contract drift.

### GATE RECORD
Outcome: PASS — human gate (risk: high / autonomy: conservative). The mechanical tamper tripwire is built, ×3 byte-identical, 815 suite green, dogfood clean; the human ratified the md5 = not-a-security-HARD-STOP classification and accepted this as task 1 of 3 (mechanical floor; the ≤3 self-heal loop + adversarial refute-read remain in earned-green-rubric / heal-then-escalate).
Reviewed by: Tin Dang · date: 2026-06-11

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the `cmd_check` standing WARN is the live monitor — a non-done task whose tripwire diverged ("build_tampered") surfaces early, never-red. Watch the per-task `build_tampered` WARN RATE across a milestone: a cluster signals systemic gaming, not a one-off honest re-cross.
Spec delta for the next loop: the mechanical floor alone is PARTIAL — a tamper is now an immediate hard block with NO loop budget and the judgment cheats (overfit · vacuous · stub) have NO detection yet. `earned-green-rubric` (the adversarial refute-read) + `heal-then-escalate` (the ≤3 honest-redo loop the human actually asked for) complete the goal; until they land, a verify PASS on this milestone closes the floor, not the feature.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] the method now has a reusable mechanical-HARD-STOP pattern — snapshot at a phase seam, re-check at the gate before any completing outcome, fail-closed, tri-state co-witnessed by an existing flag — generalizable to any "freeze X at phase A, enforce at phase B" guard beyond tamper (evidence: tamper-tripwire shipped as the method's FIRST mechanical HARD-STOP, 815 suite green, dogfood check clean)
- [TDD · folded] a tripwire whose snapshot lives in agent-writable state.json is necessary-not-sufficient: a co-witness flag raises the bypass cost (forge two, not one) but a determined agent patching both still slips — mechanical TDD enforcement raises cost, it does not seal; the semantic refute-read + the human gate stay the real backstops (evidence: the §3 freeze flag "accept honest ceiling", human-ratified at the verify gate)
- [ADD · folded] a security-line classification can EMERGE during build (md5-as-tamper-evidence), not only at the §3 freeze — when it does, surface it for human ratification AT the verify gate rather than self-granting, even when the reasoning holds (evidence: §6 md5 ratification line; the advisor caught a pre-checked self-granted box and it was reframed to an explicit ask)
- [SDD · folded] when a new feature needs the exact file set an existing counter resolves, extract a path-returning helper and delegate the counter to it (one resolution source), never re-glob — the snapshot and the engine then agree by construction (evidence: the `_primary_test_files`/`_declared_test_files`/`_resolved_test_files` refactor preserved every prior count, full suite green)
- [ADD · folded] a LIVE engine-dogfood task that crossed a phase seam under the OLD engine can re-snapshot under the NEW engine via `phase tests` + `advance` (the method-sanctioned backward move for a live task; `reopen` only works on `done` tasks) — the overwrite-on-cross snapshot makes this re-anchor path work (evidence: own task re-snapshotted to tripwire {contract_md5 786a844e…, tests {}} after the ×3 sync)
