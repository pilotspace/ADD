# TASK: add.py release <version> (guarded, record-only) — CHANGELOG prepend + RELEASES.md append-only row + milestone attribution; the 4-code readiness floor with an un-forceable security HARD-STOP

slug: release-command · created: 2026-06-16 · stage: mvp · risk: high
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
  - the 3 byte-identical ENGINE homes (md5 d0d9b1ed): `add-method/tooling/add.py` · `.add/tooling/add.py` · `add-method/src/add_method/_bundled/tooling/add.py`. ADD: a `release` subparser (positional `version` + `--force` + a waiver-disclosure flag + an evidence/note flag) + `cmd_release` (GUARDED, record-only) + the readiness-floor checks + the CHANGELOG/RELEASES.md writers.
  - `add.py:cmd_stage` (L951) — the EXACT guarded-write template: validate → `_die("code: msg … use --force to override")` → mutate → `save_state` → footer. `--force` precedent (lock/stage). release DIVERGES: `release_security_open` IGNORES `--force` (the one un-forceable reject).
  - `add.py:release_data` (just built, task 2) + `_releasable` + `_released_milestones` (fail-open) + `_releases_path` (root-level) + `RELEASES_FILE` — release REUSES these: `_releasable` = the bundle to attribute; `release_data["blockers"]` (open HARD-STOP) feeds `release_security_open`; `release_data["waivers"]` feeds `release_undisclosed_waiver`; `release_data["changed"]` (RETRO + §Key-Decisions) seeds the CHANGELOG body.
  - `add.py:_atomic_write` (L157) — design-for-failure writer (temp-file + os.replace; no half-written file). USE for BOTH writes. `_now` (L154, UTC) / `date.today().isoformat()` for the YYYY-MM-DD row date (mirrors `cmd_archive_milestone`'s `archived` field).
  - `add.py:cmd_archive_milestone` (L2227) — the validate-before-ANY-mutation idiom (a reject leaves disk byte-for-byte unchanged); release mirrors it: ALL floor checks run BEFORE the first write.
  - `add.py:_require_root` (L206) · `load_state` · `_die` · the `release-report` subparser block (mirror the registration site).
Context (working folder): MILESTONE.md shared decisions (engine-records-human-ships · security HARD-STOP un-forceable · append-only newest-first · attribution = RELEASES.md membership). The frozen `release.md` (task 1) `## The floor` SPECIFIES the 4 reject codes verbatim — this task realizes them. NO CHANGELOG.md exists anywhere in the repo (releases used 3 version sources + git tags, never a changelog) → `release` CREATES CHANGELOG.md at the project root the first time (a new, free artifact for any ADD project).
Honors (patterns / conventions): engine-records-never-acts (NO tag/publish/deploy, NO version-source bump — the human's publish pipeline owns those) · gather-vs-act split (release-report gathers; release acts, guarded) · validate-before-write (reject ⇒ disk byte-unchanged) · 3-home byte-parity + engine_pin re-aim · design-for-failure (`_atomic_write`; floor checks are the rollback — nothing is written until all pass) · the security HARD-STOP is never auto-passed / never forceable.
Anchors the contract cites: `cmd_release` · the `release` subparser (`version` positional + flags) · the 4 floor codes (`release_security_open` un-forceable · `release_tests_red` · `release_no_closed_milestone` · `release_undisclosed_waiver`) · `_releasable` (the bundle) · `release_data` (the floor inputs) · `_releases_path`/`RELEASES_FILE` (the ledger) · CHANGELOG.md at root · `_atomic_write` · the RELEASES.md row schema (`## <version> — <date>` + `milestones:`/`waivers:`/`evidence:`).

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: `add.py release <version>` — a GUARDED, record-only command that cuts a versioned release bundling the closed-unreleased milestones: it enforces the 4-code readiness floor, then RECORDS the cut by prepending a CHANGELOG.md entry + an append-only RELEASES.md row (which attributes the bundled milestones). The engine records; the human runs the tag / publish / deploy. Realizes `release.md`'s `## The floor`.
Framings weighed: record-only writer guarded like `cmd_stage` (chosen — same validate→guard→write→footer shape; `--force` precedent; one divergence: security is un-forceable) · engine runs the tag/publish too (rejected — violates engine-records-human-ships + tool-agnostic; the human's pipeline owns the outward act) · attribution written into state.json (rejected — task 2 froze attribution = RELEASES.md membership so the cue never reads compacted milestone files; release writes ONLY markdown).
Must:
<must>
  - VERSION ARG: `release <version>` takes a REQUIRED positional `version` (free-form string — semver / calver / any; NO format enforcement, tool-agnostic). `--force`, a waiver-disclosure flag, and an evidence flag are optional.
  - FLOOR — all 4 checks run BEFORE any write (validate-before-write; a reject leaves BOTH files byte-for-byte unchanged AND state.json untouched):
      · `release_security_open` — `release_data["blockers"]` non-empty (≥1 open HARD-STOP gate). The un-forceable reject: `--force` does NOT override (a security finding is never shipped).
      · `release_tests_red` — recorded-evidence PROXY (the engine is tool-agnostic, it never runs the suite): ≥1 ACTIVE task with `phase ∈ {build, verify}` AND `gate == "none"` (a build entered without a recorded PASS/RISK-ACCEPTED). `--force` overrides.
      · `release_no_closed_milestone` — `_releasable(root, state)` is empty (nothing new since the last release). `--force` overrides.
      · `release_undisclosed_waiver` — `release_data["waivers"]` non-empty AND not disclosed (the disclosure flag absent). `--force` overrides; passing the disclosure flag is the NORMAL path (it records the waivers in the row).
  - RECORD (record-only; exactly TWO writes via `_atomic_write`; NO state.json mutation; NO tag / publish / deploy / version-source bump):
      · CHANGELOG.md at the PROJECT ROOT (`root.parent`): PREPEND a `## <version> — <YYYY-MM-DD>` block (create the file with a `# Changelog` header if absent), body = one bullet per bundled milestone drawn from `release_data["changed"]` (title + carried-delta / key-decision summary).
      · RELEASES.md at the PROJECT ROOT: PREPEND a newest-first block — `## <version> — <YYYY-MM-DD>` then `milestones: <slug, …>` · `waivers: <slug, … | none>` · `evidence: <text>`. Append-only: existing rows are NEVER rewritten.
  - ATTRIBUTION: the bundled milestone slugs land on the new RELEASES.md `milestones:` line → `_releasable` now excludes them → the `→ releasable: N` cue clears (or drops) with NO state.json write.
  - FORCE: `--force` overrides the 3 forceable rejects but NEVER `release_security_open`; a forced bypass prints a one-line notice naming what was bypassed (mirrors `stage --force`).
  - DESIGN-FOR-FAILURE / ROLLBACK: build both contents in memory first; write CHANGELOG.md, then RELEASES.md (the attribution commit point); if the RELEASES.md write raises, ROLL BACK CHANGELOG.md to its prior bytes (or unlink it if it did not exist) and refuse `release_write_failed` — never leave a half-recorded cut.
  - 3-HOME PARITY: the engine edit is byte-identical across the 3 `add.py` homes; `engine_pin.ENGINE_MD5` re-aimed.
</must>
Reject:
<reject>
  - an open HARD-STOP exists -> "release_security_open"   (UN-FORCEABLE — `--force` is ignored)
  - a build is in flight without a recorded green gate -> "release_tests_red"
  - nothing closed-and-unreleased to bundle -> "release_no_closed_milestone"
  - an open RISK-ACCEPTED waiver rides in undisclosed -> "release_undisclosed_waiver"
  - the second write fails after the first -> "release_write_failed"  (CHANGELOG rolled back; not a floor code — an IO-robustness path)
  - run outside a project -> "no_project"
</reject>
After:
<after>
  - on a green cut: CHANGELOG.md has a new top `## <version>` block; RELEASES.md has a new top row whose `milestones:` line names the bundled slugs; `status` no longer counts them in `→ releasable`; state.json is byte-unchanged; the 3 engine homes are byte-identical; NO git tag / publish was performed.
  - on any reject: exit non-zero, BOTH files + state.json byte-for-byte unchanged.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ `release_tests_red` is a RECORDED-EVIDENCE PROXY, not a real test run — it fires iff an active task is mid-build (`phase ∈ {build,verify}` AND `gate == none`). LOWEST confidence because `release.md`'s prose ("the suite is not green") reads like the engine runs the tests; I proxy because the engine is tool-agnostic (it never shells out to pytest/jest). If wrong (the human expects an actual suite run): the check under-enforces a genuinely-red tree that has no in-flight ADD task. Mitigation: the human's real test run IS their readiness step in release.md (the floor is human-confirmed at the cut); the engine enforces the evidence proxy + leaves `--force`. Flagged at the freeze.
  - [ ] release writes ONLY the 2 markdown files, NEVER state.json (attribution = RELEASES.md membership — task-2 frozen decision) — treated settled.
  - [ ] CHANGELOG.md + RELEASES.md both at the PROJECT ROOT (`root.parent`), both PREPEND / newest-first — settled (CHANGELOG is a sibling of the RELEASES.md task-2 froze there).
  - [ ] waiver disclosure = a `--with-waivers` flag that also records `waivers: <slugs>` in the row; absent + open waivers → reject — settled.
  - [ ] `--force` overrides the 3 forceable codes but never security; `version` is free-form (no semver enforcement) — settled.
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: green cut records two files and clears the cue
  Given a closed-unreleased milestone, no open HARD-STOP, no in-flight build, no open waiver
  When I run `release 1.0.0`
  Then CHANGELOG.md (project root) gains a top `## 1.0.0 — <today>` block naming the milestone
  And RELEASES.md gains a top row whose `milestones:` line names the bundled slug
  And `release-report --json` no longer lists that milestone in `releasable`
  And state.json is byte-for-byte unchanged and no git tag was created

Scenario: security HARD-STOP is un-forceable
  Given a closed-unreleased milestone AND an open HARD-STOP gate
  When I run `release 1.0.0 --force`
  Then it refuses with "release_security_open"
  And CHANGELOG.md, RELEASES.md, and state.json are byte-for-byte unchanged

Scenario: an in-flight build blocks the cut
  Given a closed-unreleased milestone AND an active task at phase=build gate=none
  When I run `release 1.0.0`
  Then it refuses with "release_tests_red"
  And both files and state.json are byte-for-byte unchanged

Scenario: --force overrides a red build (a forceable reject)
  Given the same in-flight build as above
  When I run `release 1.0.0 --force`
  Then the cut is recorded and a notice names the bypass
  And no other floor reject was bypassed silently

Scenario: nothing to release is refused
  Given every closed milestone is already attributed in RELEASES.md
  When I run `release 1.0.1`
  Then it refuses with "release_no_closed_milestone"
  And both files and state.json are byte-for-byte unchanged

Scenario: an undisclosed waiver blocks the cut
  Given a closed-unreleased milestone AND an open RISK-ACCEPTED waiver, with no disclosure flag
  When I run `release 1.0.0`
  Then it refuses with "release_undisclosed_waiver"
  And both files and state.json are byte-for-byte unchanged

Scenario: disclosing the waiver records it and cuts
  Given the same open waiver
  When I run `release 1.0.0 --with-waivers`
  Then the cut is recorded and the RELEASES.md row's `waivers:` line names the waiver's task slug
  And the cue clears for the bundled milestone

Scenario: the ledger is append-only newest-first
  Given a RELEASES.md that already holds a `## 1.0.0` row
  When I run a second `release 2.0.0` (a new closed milestone exists)
  Then the `## 2.0.0` row is at the TOP and the prior `## 1.0.0` row is preserved verbatim below

Scenario: a failed second write rolls back the first
  Given a green cut whose RELEASES.md write will fail
  When I run `release 1.0.0`
  Then it refuses with "release_write_failed"
  And CHANGELOG.md is rolled back to its prior bytes (or absent if it did not exist) and state.json is unchanged

Scenario: run outside a project
  Given no .add/ project on the path
  When I run `release 1.0.0`
  Then it refuses with "no_project"
  And nothing is written
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
add.py release <version> [--force] [--with-waivers] [--evidence "<text>"]      GUARDED, record-only
  exit 0  -> prepended CHANGELOG.md + RELEASES.md (newest-first); the row's `milestones:` line
             attributes the bundle; state.json UNTOUCHED; no git tag/publish. Prints a cut summary + `next:` footer.
  exit !=0 (refuse; BOTH files + state.json byte-for-byte unchanged):
     "release_security_open"        # >=1 open HARD-STOP — UN-FORCEABLE (--force ignored)
     "release_tests_red"            # an in-flight build w/o recorded green — --force overrides
     "release_no_closed_milestone"  # _releasable == []                    — --force overrides
     "release_undisclosed_waiver"   # open waiver, no --with-waivers        — --force overrides
     "release_write_failed"         # 2nd write raised -> CHANGELOG rolled back (IO path, not a floor code)
     "no_project"                   # no .add/ on the path

cmd_release(args):
  root=_require_root(); state=load_state(root); d=release_data(root,state)
  # FLOOR (order; ALL before any write):
  if d["blockers"]:                                   _die("release_security_open …")   # ignores --force
  if not args.force and _build_in_flight(state):      _die("release_tests_red …")
  if not args.force and not _releasable(root,state):  _die("release_no_closed_milestone …")
  if not args.force and d["waivers"] and not args.with_waivers: _die("release_undisclosed_waiver …")
  bundle=_releasable(root,state); ver=args.version; day=date.today().isoformat()
  changelog_new = _render_changelog_block(ver, day, d["changed"]) + prior_changelog   # prepend after header
  releases_new  = _render_releases_row(ver, day, bundle, d["waivers"] if args.with_waivers else [], args.evidence) + prior_releases
  before = CHANGELOG bytes or None
  _atomic_write(CHANGELOG, changelog_new)
  try: _atomic_write(RELEASES, releases_new)
  except OSError: restore CHANGELOG(before); _die("release_write_failed …")
  print(summary); print(_next_footer(root,state))     # NO save_state

_build_in_flight(state) -> bool:   # the release_tests_red proxy (PURE)
  any(t.get("phase") in ("build","verify") and t.get("gate")=="none" for t in (state.get("tasks") or {}).values())

RELEASES.md  @ root.parent/RELEASES.md  (create w/ `# Releases` header if absent; PREPEND row after header):
  ## <version> — <YYYY-MM-DD>
  milestones: <slug, …>          # the _releasable bundle at cut time ("none" only when forced empty)
  waivers: <task-slug, … | none> # d["waivers"] slugs when --with-waivers, else "none"
  evidence: <--evidence text | "recorded by add.py release">

CHANGELOG.md @ root.parent/CHANGELOG.md  (create w/ `# Changelog` header if absent; PREPEND block after header):
  ## <version> — <YYYY-MM-DD>
  - <milestone title> — <N carried · M key decision(s)>     # one per bundled milestone (d["changed"])

Writes: CHANGELOG.md + RELEASES.md @ project root (root.parent), both create-if-absent + prepend.
NOT written: state.json · version sources (pyproject/package.json/__init__) · git. Engine: 3 homes byte-identical + engine_pin re-aimed.
```

Status: FROZEN @ v1 — approved by Tin Dang (2026-06-16)
Least-sure flag surfaced at freeze: [spec] `release_tests_red` is a RECORDED-EVIDENCE PROXY, not a real suite run — the tool-agnostic engine never shells to pytest/jest, so it fires iff an active task is mid-build (`phase ∈ {build,verify}` AND `gate == none`); if the human expects an actual test run it under-enforces a red tree with no in-flight ADD task (mitigation: the human's real run is their readiness step in release.md; the engine keeps the proxy + `--force`). [contract] waiver disclosure = the `--with-waivers` flag (it records the riding waivers on the row's `waivers:` line); without it + open waivers → reject. Both surfaced + accepted at the freeze.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: <e.g. 90%>
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_<scenario>: arrange <Given> / act <When> / assert <Then> + assert <unchanged>
</test_plan>

Tests live in: `./tests/` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_min_pillar.py` `./tests/`   — `cmd_release` + the `release` subparser + the 4 floor checks + `_build_in_flight` + the CHANGELOG/RELEASES writers/renderers in the 3 byte-identical engine homes, the ENGINE_MD5 re-aim, the subcommand-census ratification (`test_min_pillar` LIFECYCLE += release — release WRITES so it lands in `_NONZERO_OK` and runs EARLY where it rejects `release_no_closed_milestone`, exercised under the read-spy with a tolerated non-zero exit, like `heal`/`wave-verify`), and this task's guard tests. NO `CHANGELOG.md`/`RELEASES.md` in scope — those are RUNTIME writes (tests use temp projects; the dogfood is NOT cut here).
Strategy (ordered batches): 1. write `./tests/` red (temp-project harness like test_release_report) · 2. implement `cmd_release` + `_build_in_flight` + `_render_changelog_block` + `_render_releases_row` + the `release` subparser in ONE home `add-method/tooling/add.py` · 3. register the census (`test_min_pillar` LIFECYCLE += `["release", …]` + `_NONZERO_OK`) · 4. copy add.py byte-identical to the other 2 homes (md5) · 5. recompute + update `engine_pin.ENGINE_MD5` · 6. run green (this suite + full engine suite).
Safety rule (feature-specific): ALL 4 floor checks run BEFORE the first write (validate-before-write); both file contents are built in memory first; CHANGELOG is written, then RELEASES.md (the attribution commit) — a failed RELEASES.md write ROLLS BACK CHANGELOG to its prior bytes (or unlinks it if it was created) and refuses `release_write_failed`. NO `save_state` (state.json is never touched). NO git / tag / publish / version-source bump.
Code lives in: the 3 add.py engine homes + engine_pin.py
Constraints: do NOT change any test or the frozen contract; the security HARD-STOP is UN-FORCEABLE; allow-list only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — release-command suite 12/12 + full add-method engine suite 1152/1152 green
- [x] coverage did not decrease — +12 new task tests; engine suite count steady at 1152; +1 LIFECYCLE census slot (`release`)
- [x] no test or contract was altered during build — §3 FROZEN @ v1 untouched; the red suite is byte-unchanged since RED; the only existing-test edit is ADDITIVE (test_min_pillar LIFECYCLE += release + `release` ∈ _NONZERO_OK — the self-maintaining census)
- [x] the green was EARNED, not gamed — adversarial self-refute: each test exercises REAL behavior (2-file write + cue-clear, NO state.json mutation, append-only newest-first, --with-waivers records the row, --force overrides forceable rejects, SECURITY un-forceable even with --force + nothing written, in-flight-build/no-closed/undisclosed rejects, monkeypatched 2nd-write rollback, no_project); none vacuous/overfit/stubbed. Corroborated by the dogfood smoke (`release 9.9.9` cut 38 milestones into a well-formed RELEASES.md row + CHANGELOG, cleared the cue — files then removed)
- [x] concurrency / timing of the risky operation is safe — validate-before-write (all 4 floor checks precede the first write); two `_atomic_write`s (temp-file + os.replace, no half-file); CHANGELOG→RELEASES order with a rollback if the 2nd raises; NO state.json write (no lock contention introduced)
- [x] no exposed secrets, injection openings, or unexpected dependencies — NO new imports (date/_atomic_write/_next_footer already present); no shell/eval/network; version + evidence are written as literal text, never executed
- [x] layering & dependencies follow CONVENTIONS.md — guarded like `cmd_stage` (validate→guard→write→footer), one deliberate divergence (security un-forceable); engine-records-never-acts (NO tag/publish/deploy/version-bump); reuses `release_data`/`_releasable`/`_releases_path`/`_atomic_write`; 3 homes from ONE source + engine_pin re-aimed
- [x] a person reviewed and approved the change — Tin Dang approved PASS at the conservative + risk:high gate (2026-06-16)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — cmd_release ← the `release` subparser (set_defaults); _build_in_flight ← cmd_release (release_tests_red); _prepend_block/_render_changelog_block/_render_releases_row ← cmd_release; reuses _releasable/release_data/_releases_path/_atomic_write/_next_footer. Confirmed by 12 tests + the live dogfood cut.
- [x] DEAD-CODE (code) — no orphaned symbol: every new helper has a caller (grep + suite); no leftover scaffold.
- [x] SEMANTIC (non-code) — the dogfood smoke (`release 9.9.9`) was an INTENTIONAL end-to-end validation, NOT a real cut — both files were inspected (correct schema) then removed; the §5 scope excludes CHANGELOG/RELEASES.md (runtime writes); the phase was at `tests` when the smoke ran, so `_build_in_flight` correctly returned False (a task at `tests` is not mid-build).

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-16

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): the cue fires on milestone-done + on archive, clears on release; the floor refuses on all 4 codes; the ledger stays append-only newest-first; release never writes state.json.
Spec delta for the next loop: the FULL release lifecycle (milestone-done → archive → release → re-cue → re-release-refused → security-un-forceable) is validated end-to-end on a real project (tmp/dogfood_release_flow.py, all handoffs green). release-docs-align (task 4) MUST document: (a) the lifecycle order, (b) the brownfield first-cut bundles ALL closed milestones (no prior ledger), (c) `release` writes CHANGELOG.md at the PROJECT ROOT — a repo with a different changelog convention (e.g. this dogfood's root POINTER → add-method/CHANGELOG.md) gets release blocks PREPENDED above its existing content; reconcile per-repo.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
- [ADD · folded] release is a WRITER guarded like cmd_stage with ONE divergence — the security reject runs FIRST and has NO `not forced` guard, so `--force` can never reach it; modeling "the un-forceable reject" as an unguarded leading check is the clean encoding (evidence: test_security_hardstop_unforceable + dogfood step 6 both refuse under --force)
- [ADD · folded] the engine stays tool-agnostic + decoupled by RECORDING only (2 markdown files) and NEVER writing state.json — attribution lives in RELEASES.md membership, so the cue re-reads the ledger and release is a pure 2-file write (evidence: test_green_cut_does_not_touch_state + the dogfood cue clears with state.json byte-unchanged)
- [ADD · folded] `release` writes CHANGELOG.md at the project ROOT, but a repo can carry a different changelog convention — this dogfood's root CHANGELOG.md is a deliberate POINTER to add-method/CHANGELOG.md; release prepends above it (preserving it via _prepend_block's header-detection), creating a hybrid that contradicts the pointer's intent (evidence: a real `release 9.9.9` on this repo prepended a release block above the pointer; the generic root-CHANGELOG decision is correct, the nested-package case needs doc/awareness — task 4)
- [TDD · folded] design-for-failure rollback is testable by monkeypatching _atomic_write to fail on the 2nd write — assert the 1st file is rolled back + state unchanged (evidence: test_failed_second_write_rolls_back_first)
- [ADD · folded] a tool-agnostic engine cannot run the suite, so `release_tests_red` is a recorded-evidence proxy (in-flight build w/o a green gate) + the human's real run is the release.md readiness backstop (evidence: the §3 freeze flag; accepted at the conservative gate)
