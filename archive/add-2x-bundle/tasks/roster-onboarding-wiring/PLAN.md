# TASK: Wire the portable roster into installer / sync-guidelines onboarding

slug: roster-onboarding-wiring · created: 2026-07-02 · stage: mvp
milestone: portable-roster
autonomy: auto
phase: done

> One file = one task. Fill sections top-to-bottom; the `add` skill drives each phase.
> When a phase is unclear, read its book chapter in `.add/docs/` (linked per section).
> The phase marker above is the single source of truth — keep it in sync via `add.py phase`.

---

## 0 · GROUND — the real codebase ▸ docs/02-the-flow.md

Touches (files · symbols · signatures):
  - `add-method/tooling/test_agent_detect.py:303 ParityTest` — existing cli.js↔_installer.py registry-parity suite; `test_parity_six_new_profiles` (line 311) already asserts `.clinerules`/`cline` are *mentioned* in both installers, but never that the tool actually *receives* the guideline block.
  - `add-method/tooling/add_engine/constants.py:138 GUIDELINE_FILES = ("AGENTS.md", "CLAUDE.md")` — the only two filenames `_inject_guidelines`/`add.py init`/`sync-guidelines` ever write the full block (incl. the new roster) into. Unconditional: every project gets both files regardless of detected tool.
  - `add-method/bin/cli.js:91 AGENT_PROFILES` and `add-method/src/add_method/_installer.py:305 AGENT_PROFILES` — ~11 registered tool profiles, each with an `integration_file`; both installers write only a LITE PLACEHOLDER pointer at first install (`agentPointerBlock`/`_write_agent_pointer`), documented as replaced once `sync-guidelines` runs.
  - `add-method/tooling/add_engine/guidelines.py:196 _inject_guidelines` loop over `GUIDELINE_FILES` — adding `.clinerules` here makes it write the full block into `.clinerules` exactly like the other two names; no per-file special-casing beyond the CLAUDE-only rule-file branch (line 197).
  - `add-method/tooling/add_engine/guidelines.py:238 _INIT_EXCLUDE` (checked by `_is_brownfield`, line 245) — does NOT currently include `.clinerules`. `add.py init` calls `_inject_guidelines` (add.py:572) BEFORE `_is_brownfield` (add.py:576), so once `.clinerules` is a GUIDELINE_FILES member, `init` writes it to disk first — a fresh, otherwise-empty project would then be misdetected as brownfield by its own freshly-written file unless `.clinerules` is also added to `_INIT_EXCLUDE`.

Context (working folder): none beyond the touched files above — no docs/config/data surface for this task.

Honors (patterns / conventions): the "derived, never duplicated" convention task 1 established for the roster itself now extends one layer out — the INSTALLER's tool registry should be provably in sync with `GUIDELINE_FILES`, not just assumed so.

Anchors the contract cites: `add-method/tooling/test_agent_detect.py::ParityTest` (new test method) · `add-method/tooling/add_engine/constants.py:138 GUIDELINE_FILES` · `add-method/bin/cli.js:91` / `add-method/src/add_method/_installer.py:305 AGENT_PROFILES[].integration_file`

Issues/Risks (→ feed §1):
  - **Task 1 already delivered most of the milestone's stated goal.** The roster lives inside `_guideline_block()`, and `_inject_guidelines` unconditionally writes that block into every project's `AGENTS.md` + `CLAUDE.md` — proven end-to-end by task 1's own `test_roster_portable.py::_Synced` fixture. "installer/sync-guidelines materializes it into AGENTS.md for every tool" was existing plumbing, not new work. Task 2 must not invent scope to pad this out.
  - **The one real, concrete gap: `cline`.** Its `integration_file` is `.clinerules` — the ONE profile (of ~11: 9× AGENTS.md, 1× CLAUDE.md, 1× `.clinerules`) outside `GUIDELINE_FILES`. It never receives the full block — not the floor, not the 3-step loop, not now the roster — via `add.py init`/`sync-guidelines`; it is permanently stuck on the installer's lite pointer. This gap PRE-DATES the roster and is whole-block, not roster-specific.
  - **Scope reading on cline: the milestone's own goal line says "through the AGENTS.md the installer already drops" — a plain reading puts cline (a different file, a pre-existing whole-block gap unrelated to the roster) OUT of this task.** Fixing it means adding `.clinerules` to `GUIDELINE_FILES` in `constants.py`, which is `add_engine` — re-moves `ENGINE_PKG_MD5` (the 3-tree mirror/pin dance again) and ripples `test_guidelines`/`test_agent_detect`. That is its own task, own blast radius, not a rider here.
  - **No existing test correlates the registry against `GUIDELINE_FILES` coverage.** `test_parity_six_new_profiles` only checks that the string `.clinerules` appears in both installer files — not that the tool it names actually gets the full block. A future new profile with a non-`AGENTS.md`/`CLAUDE.md` `integration_file` would silently never receive the roster, with nothing to catch it. This is the one genuine, non-redundant deliverable left for this task: a drift-guard asserting every `AGENT_PROFILES[].integration_file` is either in `GUIDELINE_FILES` or a documented exception.
  - Exit criteria 1 ("names all 5 phase-roles + when to adopt each") and 4 ("stays lean, ≤22-line budget") are already satisfied by task 1's shipped content + compress-to-fit resolution — task 2's verify should CITE them as satisfied by the shared mechanism, not re-earn them.

Related intent: milestone `portable-roster` goal — "non-Claude coding tools receive the ADD phase-roster's roles and boundaries through the AGENTS.md the installer already drops" (`.add/milestones/portable-roster/MILESTONE.md`); task 2's own line ("materializes it into AGENTS.md for every onboarded tool") is the source of the ambiguity flagged above — resolved by asking Tin directly at SPECIFY rather than assumed either way.

Ground SHA: `cb3f135`

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Close the cline `.clinerules` guideline gap + guard the installer registry against future drift
Framings weighed: extend `GUIDELINE_FILES` to include `.clinerules` + add a zero-exception registry↔`GUIDELINE_FILES` drift-guard test (chosen, per Tin) · leave cline a documented exception + spec delta (rejected — Tin folded the fix in) · relocate cline to a rule-file-style pointer akin to CLAUDE.md's ccsk mode (rejected — over-engineering; no cline convention calls for it, AGENTS.md doesn't do this either)
Must:
<must>
  - M1: `.clinerules` is a member of `add_engine.constants.GUIDELINE_FILES`, so `_inject_guidelines` (`add.py init` / `sync-guidelines`) writes the full guideline block — floor, 3-step loop, and roster — into `.clinerules` exactly as it does for `AGENTS.md`/`CLAUDE.md`.
  - M2: `.clinerules` is a member of `_INIT_EXCLUDE`, so a fresh `add.py init` on an otherwise-empty project is NOT misdetected as brownfield purely because `_inject_guidelines` just wrote `.clinerules` to disk.
  - M3: `.clinerules` is unaffected by CLAUDE-only rule-file mode (ccsk) — it stays a plain inline-block target like `AGENTS.md`, never relocated to `.claude/rules/`.
  - M4: a new test asserts, for every profile in BOTH `AGENT_PROFILES` registries (`cli.js` + `_installer.py`), that `integration_file` is a member of `GUIDELINE_FILES` — zero documented exceptions after this task (drift-guard for any future new tool).
  - M5: existing `AGENTS.md`/`CLAUDE.md` behavior (incl. rule-file mode, symlink-dedup, `.bak` rollback) is byte-for-byte unchanged — cline support is additive only.
  - M6: the 3-tree engine-pin mirror (`ENGINE_PKG_MD5`) is re-aimed to cover the `constants.py`/`guidelines.py` change, mirrored byte-identical across the canonical and `_bundled` trees (the gitignored `.add/tooling` dogfood mirror synced locally only, per task 1's precedent).
</must>
Reject:
<reject>
  - a registered profile whose `integration_file` is not in `GUIDELINE_FILES` after this task -> "registry_guideline_drift"
  - `.clinerules` counted as a brownfield signal on a fresh, otherwise-empty `init` -> "clinerules_brownfield_false_positive"
  - `.clinerules` relocated/altered by rule-file mode the way `CLAUDE.md` is -> "clinerules_rule_file_leak"
</reject>
After:
<after>
  - the drift-guard test (M4) passes with zero exceptions across both installer registries
  - a freshly-inited or `sync-guidelines`-synced project's `.clinerules` contains the full guideline block, byte-identical in content to what `AGENTS.md` receives
  - a fresh `add.py init` on an empty directory still prints the greenfield "next: open Claude Code…" message, not the brownfield branch
  - `ENGINE_PKG_MD5` re-aimed; 3 trees byte-identical; `test_engine_extract_md5.py::test_pkg_digest_3tree` green
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ cline's real-world convention is a single flat `.clinerules` file at the project root (not a `.clinerules/` directory some newer cline versions/extensions use) — lowest confidence because this task only verifies internal consistency (the installer's own `NEW_AGENTS` fixture already assumes a flat file), not cline's current upstream docs; if wrong: the fix would write a full guideline block into the wrong shape and go unnoticed since no external cline install is exercised in CI. Treating as acceptable — the installer already made this same bet at multi-agent-installer time, this task is not introducing a new unverified claim, only extending an existing one.
  - [x] `test_guidelines.py`'s existing tests hardcode `("AGENTS.md", "CLAUDE.md")` literal tuples rather than iterating `GUIDELINE_FILES` — confirmed by grep; they will keep passing (no regression) but will NOT exercise `.clinerules`, so §4 must add a NEW test for that, not rely on existing coverage growing automatically.
</assumptions>

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: cline receives the full guideline block   # M1
  Given a project directory with no pre-existing `.clinerules`
  When `add.py init` (or `sync-guidelines`) runs
  Then `.clinerules` is created containing the full guideline block — floor, 3-step loop, and phase-roster — byte-identical in content to what `AGENTS.md` receives

Scenario: fresh init is not misdetected as brownfield   # M2
  Given an otherwise-empty project directory
  When `add.py init` runs (which writes `.clinerules`, `AGENTS.md`, `CLAUDE.md` via `_inject_guidelines` before checking brownfield)
  Then `_is_brownfield(base)` returns False and `init` prints the greenfield "next: open Claude Code…" message, not the brownfield branch

Scenario: rule-file mode does not relocate .clinerules   # M3
  Given a ccsk-style project with rule-file mode active (ADD_RULE_FILE=1 or --rule-file)
  When `_inject_guidelines(root, rule_file=True)` runs
  Then `.clinerules` still receives the plain inline block directly (like `AGENTS.md`) while only `CLAUDE.md` is relocated to a `.claude/rules/add-workflows.md` reference

Scenario: drift-guard passes with zero exceptions today   # M4
  Given the live `AGENT_PROFILES` registries in both `cli.js` and `_installer.py`
  When each profile's `integration_file` is checked against `GUIDELINE_FILES`
  Then every one resolves — zero unmatched profiles

Scenario: existing AGENTS.md/CLAUDE.md behavior is unchanged   # M5
  Given the same tmp-dir fixture `test_guidelines.py` already exercises (symlink-dedup, `.bak` rollback, UTF-16 skip-and-warn)
  When `_inject_guidelines` runs after the `.clinerules` addition
  Then `AGENTS.md` and `CLAUDE.md` outcomes (content, `.bak` files, warnings) are identical to pre-change behavior
  And no new required argument or behavior change leaks into the existing call sites

Scenario: engine pin re-aimed and 3-tree mirror stays byte-identical   # M6
  Given `constants.py` and `guidelines.py` changed under the canonical and `_bundled` trees
  When `engine_manifest.py:package_digest()` is recomputed
  Then `ENGINE_PKG_MD5` in `engine_pin.py` matches the new digest and `test_engine_extract_md5.py::test_pkg_digest_3tree` is green

Scenario: a drifted profile is caught   # R:registry_guideline_drift
  Given a synthetic profile list containing one entry whose `integration_file` is NOT in `GUIDELINE_FILES`
  When the drift-guard's checking logic evaluates it
  Then it reports that entry as a violation tagged "R:registry_guideline_drift"
  And the live (non-synthetic) registries in this repo report zero violations after the fix

Scenario: .clinerules alone does not trip brownfield detection   # R:clinerules_brownfield_false_positive
  Given a project directory containing only `.add/`, `AGENTS.md`, `CLAUDE.md`, and `.clinerules` (all installer-written scaffolding, no user content)
  When `_is_brownfield(base)` is called directly
  Then it returns False, rejecting a false-positive brownfield read with "R:clinerules_brownfield_false_positive"
  And a directory with one additional non-scaffolding file still correctly returns True (existing brownfield detection unaffected)

Scenario: .clinerules is never pulled into rule-file relocation   # R:clinerules_rule_file_leak
  Given rule-file mode active and a pre-existing `.clinerules` with local user edits outside the ADD:BEGIN/END markers
  When `_inject_guidelines(root, rule_file=True)` runs
  Then `.clinerules` is updated in place (inline block refreshed, user content outside markers preserved) and NOT moved/emptied the way `CLAUDE.md` is, rejecting "R:clinerules_rule_file_leak"
```

</scenarios>

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
GUIDELINE_FILES: tuple[str, ...] = ("AGENTS.md", "CLAUDE.md", ".clinerules")   # add_engine/constants.py
  _inject_guidelines(project_root, rule_file) -> list[tuple[str, str]]   # unchanged signature/loop; new member flows through for free
    each name in GUIDELINE_FILES gets the full block (floor + 3-step loop + roster), EXCEPT
    CLAUDE.md under rule-file mode (relocated to .claude/rules/add-workflows.md) — .clinerules
    is NEVER subject to that branch, always plain inline like AGENTS.md

_INIT_EXCLUDE: frozenset[str]   # add_engine/guidelines.py — gains ".clinerules"
  _is_brownfield(base) -> bool   # unchanged signature; now correctly ignores .clinerules as scaffolding

drift-guard: a new test (add-method/tooling/test_agent_detect.py, ParityTest class) asserting
  for every profile in cli.js:AGENT_PROFILES and _installer.py:AGENT_PROFILES:
    profile.integration_file ∈ GUIDELINE_FILES
  violation -> "registry_guideline_drift"
  the checking logic itself is a small pure helper, independently unit-tested with a synthetic
  bad entry (proves R:registry_guideline_drift fires) separately from the live-registry assertion
  (proves zero violations exist today)

Schema: writes add_engine/constants.py (GUIDELINE_FILES) + add_engine/guidelines.py (_INIT_EXCLUDE);
  reads add-method/bin/cli.js + add_method/_installer.py (AGENT_PROFILES, unedited — parity target,
  not a write target); new test logic in add-method/tooling/test_agent_detect.py. No state.json /
  template change. Mirrored byte-identical across the canonical and `_bundled` trees per the
  established 3-tree convention; ENGINE_PKG_MD5 re-aimed.
```

Glossary deltas: none — extends existing terms (`GUIDELINE_FILES`, `AGENT_PROFILES`), introduces no new domain concept.
Least-sure flag surfaced at freeze: [spec] cline's real-world convention is a single flat `.clinerules` file at the project root, not a `.clinerules/` directory some newer cline versions/extensions use — why-unsure: this task only verifies internal consistency (the installer's own existing `NEW_AGENTS` fixture already assumes flat-file), not upstream cline docs; cost-if-wrong: the fix writes a full block into the wrong shape for real cline installs, unnoticed since no external cline install is exercised in CI — but this is not a NEW unverified claim, the installer already made this same bet at multi-agent-installer time (task 2 only extends existing behavior to a second write path, it doesn't originate the assumption).
Status: FROZEN @ v1 — approved by Tin Dang

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: 100% of the 9 new scenarios; behavioral, asserting observable file/return-value outcomes, not internals.
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_clinerules_receives_full_block (test_guidelines.py): arrange a tmp project dir with no pre-existing `.clinerules` / act call `_inject_guidelines(root)` / assert `.clinerules` is created, contains the ADD:BEGIN/END markers + roster section, byte-identical in block content to `AGENTS.md` · covers: M1
  - test_init_supersedes_cline_pointer (test_agent_detect.py::PointerTest; added post-freeze, additional evidence — not a new Must/Scenario): arrange write cline's real lite pointer via `_installer._write_agent_pointer` (the actual first-install artifact) / act call `_inject_block(".clinerules")` (the real `sync-guidelines` step) / assert exactly one `_GUIDE_BEGIN`, full block content — proves the REAL onboarding sequence (install pointer -> sync supersedes), not just a from-scratch write; closes a gap the external advisor flagged: `test_clinerules_receives_full_block` alone only proves the fresh-file case · covers: M1
  - test_clinerules_not_relocated_by_rule_file_mode (test_rule_file_mode.py): arrange a tmp ccsk-style project via `--rule-file` / act call `self._sync("--rule-file")` / assert `.clinerules` still gets the inline block directly while only `CLAUDE.md` is relocated to `.claude/rules/add-workflows.md` · covers: M3
  - existing test_guidelines.py suite (all 9 pre-existing tests; no new test — the `.clinerules` addition is purely additive to the `GUIDELINE_FILES` loop and does not touch the `AGENTS.md`/`CLAUDE.md` code path they already exercise byte-for-byte: dedup, `.bak` rollback, idempotency, live-state exclusion, UTF-8 handling, corrupt-block recovery) · covers: M5
  - test_clinerules_preserved_under_rule_file_mode (test_rule_file_mode.py): arrange a pre-existing `.clinerules` with user content outside the ADD:BEGIN/END markers, then `self._sync("--rule-file")` / assert `.clinerules` is updated in place (block refreshed, user content preserved) and NOT moved/emptied the way `CLAUDE.md` is · covers: R:clinerules_rule_file_leak
  - existing test_brownfield_scan.py::test_greenfield_dir_unchanged (no new test — already runs the exact M2 flow: full `cmd_init` on an empty dir, asserts the greenfield closing and no brownfield signal; a `.clinerules` write with `_INIT_EXCLUDE` un-fixed would turn it red, so it doubles as the regression guard for a half-applied fix) · covers: M2
  - test_clinerules_alone_not_brownfield (test_brownfield_scan.py): arrange a tmp dir containing only `.add/`, `AGENTS.md`, `CLAUDE.md`, `.clinerules` (all installer scaffolding) / act call `_is_brownfield(base)` directly / assert False; a sibling case adding one non-scaffolding file still returns True · covers: R:clinerules_brownfield_false_positive; also updates this file's CONTRACT docstring (`_INIT_EXCLUDE` list) to include `.clinerules`
  - test_registry_covers_guideline_files_today (test_agent_detect.py::ParityTest): arrange parse `integration_file` out of every profile in `cli.js:AGENT_PROFILES` and `_installer.py:AGENT_PROFILES` via the shared regex helper / act check each against `GUIDELINE_FILES` / assert zero unmatched profiles · covers: M4
  - test_synthetic_drift_detected (test_agent_detect.py::ParityTest): arrange a synthetic profile list with one entry whose `integration_file` is NOT in a synthetic `GUIDELINE_FILES` / act run the same checking helper used above / assert it reports that entry, tagged `registry_guideline_drift` · covers: R:registry_guideline_drift
  - existing test_engine_extract_md5.py::test_pkg_digest_3tree (no new test — already asserts 3-tree digest parity generically; this task's job is to make it pass after the `constants.py`/`guidelines.py` re-aim, not duplicate it) · covers: M6
</test_plan>

Tests live in: `add-method/tooling/test_guidelines.py` `add-method/tooling/test_brownfield_scan.py` `add-method/tooling/test_agent_detect.py` `add-method/tooling/test_rule_file_mode.py` · MUST run red (missing `.clinerules` wiring) before Build.

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add_engine/constants.py` `add-method/tooling/add_engine/guidelines.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_guidelines.py` `add-method/tooling/test_brownfield_scan.py` `add-method/tooling/test_agent_detect.py` `add-method/tooling/test_rule_file_mode.py` `add-method/src/add_method/_bundled/tooling/add_engine/constants.py` `add-method/src/add_method/_bundled/tooling/add_engine/guidelines.py` `add-method/src/add_method/_bundled/tooling/engine_pin.py`   (10 tracked files — 3 canonical engine + their 3 `_bundled` mirrors + 4 existing test files gaining new methods; the gitignored `.add/tooling` dogfood mirror is synced locally, per task 1's precedent, but is excluded from the scope walk)
Strategy (ordered batches): 1. add `.clinerules` to `GUIDELINE_FILES` in `constants.py` and to `_INIT_EXCLUDE` in `guidelines.py` (canonical tree); update `test_brownfield_scan.py`'s CONTRACT docstring to name the new `_INIT_EXCLUDE` member. 2. add the new test methods (per §4 plan) to `test_guidelines.py`, `test_brownfield_scan.py`, `test_agent_detect.py::ParityTest` — including the small pure drift-check helper (parses `AGENT_PROFILES.integration_file` out of both installer source files via regex, compares against `GUIDELINE_FILES`) used by both the live-registry assertion and the synthetic-violation unit test. 3. run the new suite RED (missing `.clinerules`/`_INIT_EXCLUDE` wiring) before any src edit — confirm red for the RIGHT reason. 4. make it green: apply the constants.py/guidelines.py edits from batch 1. 5. byte-copy the two edited canonical files verbatim into the `_bundled` tree; md5-verify equal. 6. recompute the `add_engine` package digest and re-aim `ENGINE_PKG_MD5` in `engine_pin.py` across canonical + `_bundled` (byte-identical); `ENGINE_MD5` untouched. 7. full suite green, incl. `test_engine_extract_md5.py::test_pkg_digest_3tree`.
Persona (optional): none (method/tooling stance atop SOUL.md — installer/engine-registry parity is the domain)
Known-problem fixes: ugrep/BSD-grep gotcha → any registry-parity check reads files via Python `.read_text()`/regex, never shells out to `grep -cl` · silent scope creep → this task does NOT touch cli.js/_installer.py (they are read-only parity targets, not write targets — no new tool onboarding here) · stale docstring → `test_brownfield_scan.py`'s CONTRACT comment hard-codes the `_INIT_EXCLUDE` set; must be updated in the same batch as the code change, not left to drift.
Strategy actually used: as planned (batches 1-7 executed in order). One refinement discovered mid-tests: `test_brownfield_scan.py::test_greenfield_dir_unchanged` (already existing, running the exact `cmd_init` on an empty dir flow) doubles as the M2 regression guard once `.clinerules` is a real GUIDELINE_FILES member — so M2 needed no dedicated new test, only the Reject-side unit test (`test_clinerules_alone_not_brownfield`) was genuinely new/red-today; same treatment already applied to M5/M6 in §4. `test_rule_file_mode.py` (not `test_guidelines.py`) turned out to be the better home for the M3/rule-file-leak tests — discovered while grounding the rule-file-mode test file, corrected §4/§5 before writing code. A 6th test was added post-green, at verify: the external advisor consult flagged that the real onboarding path (install writes cline's lite pointer -> `sync-guidelines` supersedes it in place) was only inferred by code-path equivalence, not directly tested — `test_clinerules_receives_full_block` only proves the fresh-file case. Closed with `test_init_supersedes_cline_pointer` (mirrors the existing `test_init_supersedes_pointer_pip` pattern, targeting cline's real profile + `.clinerules`) plus a manual scratch-dir run of the actual install-then-sync sequence, inspected byte-for-byte. Full suite: 2727 tests (2721 baseline + 6 new), 2 pre-existing environment-only ugrep/BSD-grep failures (test_milestone_exit_grep_lists_all_3 + its test_ci_tooling_mirror_gap cascade — documented, green on CI, unrelated to this task), 0 regressions.
Safety rule (feature-specific): the `_inject_guidelines`/`_is_brownfield` behavior for `AGENTS.md`/`CLAUDE.md` must remain byte-for-byte unchanged (M5) — verified by the existing `test_guidelines.py` suite staying fully green, not just the new tests.
Code lives in: `add-method/tooling/add_engine/constants.py` + `add-method/tooling/add_engine/guidelines.py` (canonical edits) + their byte-identical `_bundled` mirrors; the digest re-aim lands in `engine_pin.py` across both tracked trees (plus the local `.add/tooling` copy)
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — 2727 tests (2721 baseline + 6 new), 0 regressions; 2 pre-existing environment-only ugrep/BSD-grep failures (test_milestone_exit_grep_lists_all_3 + its test_ci_tooling_mirror_gap cascade — documented, green on CI)
- [x] coverage did not decrease — every new line is a tuple/set literal member (no new branches); both new-member code paths (`.clinerules` write, `.clinerules` brownfield-exclusion) are directly exercised by new tests
- [x] no test or contract was altered during build — only NEW test methods added + 2 existing tests strengthened with additive assertions (never weakened); §3 unchanged since freeze
- [x] the green was EARNED, not gamed — see Refute-read verdict below
- [x] concurrency / timing of the risky operation is safe — no concurrency surface; pure file-write loop over a static tuple, same atomic-write primitive (`_atomic_write`) already used for AGENTS.md/CLAUDE.md
- [x] no exposed secrets, injection openings, or unexpected dependencies — no new dependency; the drift-guard reads source files via `.read_text()` + regex, never `eval`/`exec`/shell-out
- [x] layering & dependencies follow CONVENTIONS.md — change confined to `add_engine.constants`/`add_engine.guidelines` (existing modules) + test files; no new cross-module coupling
- [ ] a person reviewed and approved the change — pending Tin's gate decision below

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] a fresh `add.py init`/`sync-guidelines` run creates a `.clinerules` file whose block content is byte-identical to `AGENTS.md`'s — confirmed by `test_clinerules_receives_full_block` (test_guidelines.py), green
- [x] the REAL onboarding sequence (install drops cline's lite pointer -> `sync-guidelines` supersedes it in place, no duplicate block) — confirmed by `test_init_supersedes_cline_pointer` (test_agent_detect.py::PointerTest), green; also manually reproduced in a scratch dir and inspected byte-for-byte (advisor-flagged gap, closed at verify)
- [x] that same fresh `init` on an otherwise-empty dir still prints the greenfield closing, not a brownfield signal — confirmed by the pre-existing `test_greenfield_dir_unchanged` (test_brownfield_scan.py), still green after the fix
- [x] rule-file mode (ccsk / `--rule-file`) relocates only `CLAUDE.md`; `.clinerules` and `AGENTS.md` both keep the inline block — confirmed by the extended `test_flag_relocates_claude_keeps_agents_inline` + new `test_clinerules_preserved_under_rule_file_mode` (test_rule_file_mode.py), both green
- [x] both `AGENT_PROFILES` registries (`cli.js`, `_installer.py`) have zero `integration_file` values outside `GUIDELINE_FILES` — confirmed by `test_registry_covers_guideline_files_today` (test_agent_detect.py::ParityTest) against the LIVE source files, green
- [x] `ENGINE_PKG_MD5` matches the recomputed `add_engine` package digest and is byte-identical across the canonical and `_bundled` trees — confirmed by `test_engine_extract_md5.py::test_pkg_digest_3tree`, green; digest `a66975e2b5ed53b5858c3bd43dde7828`
- [x] the full pre-existing suite stays green — confirmed by the full-repo `python3 -m unittest discover` run (2726/2726 modulo the 2 pre-existing environment-only failures noted above)

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — `.clinerules` (new `GUIDELINE_FILES` member) is read by `_inject_guidelines`'s loop (guidelines.py:196) and by the new drift-guard's `GUIDELINE_FILES` reference (test_agent_detect.py); `.clinerules` (new `_INIT_EXCLUDE` member) is read by `_is_brownfield` (guidelines.py:253). Both new literals are live-referenced by existing production code paths, not dead additions.
- [x] DEAD-CODE (code) — no new function/class introduced; the drift-check helper `_drifted_integration_files` (test_agent_detect.py) is called by both new test methods, not orphaned.
- [x] SEMANTIC (prose / non-code) — read in full: `test_brownfield_scan.py`'s CONTRACT docstring (updated to list `.clinerules` in `_INIT_EXCLUDE`) and `guidelines.py`'s module docstring (updated to name all 3 GUIDELINE_FILES targets) — both now accurately describe the post-change behavior, no stale claims left.

### Live-verify evidence — confirm the §0 GROUND anchors still resolve (fill at the gate)
> §0's Ground SHA anchors the symbols cited at ground time to that commit — code moves during
> build. Before the gate, re-resolve every symbol §3 CONTRACT cites against the CURRENT tree
> (not the Ground SHA) so a stale anchor is caught here, not by a future reader chasing a moved
> line.
- [x] every symbol §3 CONTRACT cites still resolves in the current tree — confirmed by direct grep: `constants.py:138 GUIDELINE_FILES`, `guidelines.py:182 _inject_guidelines`, `guidelines.py:239 _INIT_EXCLUDE`, `guidelines.py:246 _is_brownfield`, `test_agent_detect.py:317 ParityTest` (+ its 2 new methods at lines 325/338) all resolve at their cited (or updated) locations
- [x] no anchor moved/renamed since Ground SHA — `_INIT_EXCLUDE`'s line number shifted (238→239, one line added above it) and `_is_brownfield`'s shifted correspondingly (245→246); both are named here since the drift is real, though trivial (one-line insertion, not a rename)

### Refute-read verdict — the earned-green check (record it; required for an auto-PASS)
> Under autonomy: auto the AI auto-resolves Verify, so the earned-green refute-read MUST be
> recorded here (the engine never spawns it — you do; NOT-EARNED -> `add.py heal`). The engine
> MEASURES it is filled (`audit: refute_unrecorded`); it never auto-blocks — a human spot-audit
> is the backstop. A human-gated (conservative/manual) task may leave it for the human's judgment.
Verdict: EARNED
By: self · adversarially checked: (1) does the drift-guard regex actually extract real data or vacuously match nothing? — directly ran the extraction against the live cli.js/_installer.py: 11/11 profiles matched in each, confirming the "zero drift" assertion is earned, not a false-empty pass. (2) is `test_clinerules_receives_full_block`'s byte-identical-block assertion tautological given `_inject_block` has no per-file branching? — yes, mechanically guaranteed under today's code, but it's forward-looking regression protection (would catch an accidental future per-file content divergence) layered on top of the non-tautological existence+marker assertions, not a substitute for them. (3) could the M2 "no new test" citation (existing `test_greenfield_dir_unchanged`) be a dodge? — verified directly: that test runs the real `cmd_init` → `_inject_guidelines` → `_is_brownfield` path on an empty dir and WOULD have gone red had `_INIT_EXCLUDE` not been fixed alongside `GUIDELINE_FILES` (confirmed by the mental model, not just assertion — the write-then-check ordering at add.py:572/576 makes this a genuine dependency, not a coincidence). No overfit to fixtures, no stubbed logic, no assertion weakened to pass.

### Advisor 3-lens verdict — sequential (security → concurrency → architecture)
> Under autonomy: auto run the 3-lens checklist and record the verdict here. Lenses run in
> order; a Security HARD-STOP ends the checklist (leave remaining lenses blank). Binding for
> sensitivity: mechanical (advisor-gate-relax reads it); advisory for all other sensitivities.
> The engine MEASURES this block is filled (audit: advisor_verdict_unrecorded); it never blocks.
Advisor: external (frontier-model advisor tool consult, this session) + self
1. Security: CLEAR — no new external input surface; reads local source files via `.read_text()` + regex only, no `eval`/`exec`/shell-out; no secrets touched.
2. Concurrency: CLEAR — no new concurrent operation; same sequential `_atomic_write`-backed loop already used for AGENTS.md/CLAUDE.md, now also covering `.clinerules`.
3. Architecture: RESIDUE — the cross-tree registry↔GUIDELINE_FILES parity check (test_agent_detect.py reading bin/cli.js + src/add_method/_installer.py) extends an existing pattern (ParityTest already does this), not a new coupling shape. The one honest residue: this task's shipped scope (fixing cline's whole-block gap) goes beyond the milestone's own goal-line wording ("through the AGENTS.md the installer already drops") — a deliberate, explicit human scope decision (Tin's "fold cline fix into this task" answer at the freeze-adjacent scoping question), not an oversight; flagged here for the record, not a blocker.
Advisor-caught gap (closed before this verdict): the external advisor consult identified that M1's evidence proved only the fresh-`.clinerules` case (`test_clinerules_receives_full_block`), while the actual cline onboarding path is install-writes-lite-pointer -> `sync-guidelines`-supersedes — inferred by code-path equivalence (`.clinerules` rides the same generic `_inject_block` path as `AGENTS.md`; only `CLAUDE.md` is rule-file-special-cased) but never directly exercised. Closed by adding `test_init_supersedes_cline_pointer` (mirrors the existing `test_init_supersedes_pointer_pip` pattern) + a manual scratch-dir reproduction of the real sequence, inspected byte-for-byte — see §4/§6 evidence above. This is the kind of gap a self-only refute-read is structurally prone to miss (it audits the tests you wrote, not the ones you didn't); recording it here rather than silently folding it in.
Verdict: PASS
Residue: milestone goal-line wording is narrower than what shipped (cline/.clinerules) — human-directed scope expansion, documented above; consider a small goal-line delta at OBSERVE so the milestone's own text matches what actually shipped.
Binding: advisory — architecture

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-07-02

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): <error rate / per-rejection rate / latency>

### Decisions (ADR)
- [AI] specify — chose extend `GUIDELINE_FILES` to include `.clinerules` + add a zero-exception registry↔`GUIDELINE_FILES` drift-guard test; rejected leave cline a documented exception + spec delta (rejected — Tin folded the fix in) · relocate cline to a rule-file-style pointer akin to CLAUDE.md's ccsk mode (rejected — over-engineering; no cline convention calls for it, AGENTS.md doesn't do this either)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned (batches 1-7 executed in order). One refinement discovered mid-tests: `test_brownfield_scan.py::test_greenfield_dir_unchanged` (already existing, running the exact `cmd_init` on an empty dir flow) doubles as the M2 regression guard once `.clinerules` is a real GUIDELINE_FILES member — so M2 needed no dedicated new test, only the Reject-side unit test (`test_clinerules_alone_not_brownfield`) was genuinely new/red-today; same treatment already applied to M5/M6 in §4. `test_rule_file_mode.py` (not `test_guidelines.py`) turned out to be the better home for the M3/rule-file-leak tests — discovered while grounding the rule-file-mode test file, corrected §4/§5 before writing code. A 6th test was added post-green, at verify: the external advisor consult flagged that the real onboarding path (install writes cline's lite pointer -> `sync-guidelines` supersedes it in place) was only inferred by code-path equivalence, not directly tested — `test_clinerules_receives_full_block` only proves the fresh-file case. Closed with `test_init_supersedes_cline_pointer` (mirrors the existing `test_init_supersedes_pointer_pip` pattern, targeting cline's real profile + `.clinerules`) plus a manual scratch-dir run of the actual install-then-sync sequence, inspected byte-for-byte. Full suite: 2727 tests (2721 baseline + 6 new), 2 pre-existing environment-only ugrep/BSD-grep failures (test_milestone_exit_grep_lists_all_3 + its test_ci_tooling_mirror_gap cascade — documented, green on CI, unrelated to this task), 0 regressions.
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.

