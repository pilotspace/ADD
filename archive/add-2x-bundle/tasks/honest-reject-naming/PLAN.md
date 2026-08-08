# TASK: Honest reject naming — rename release_tests_red, reconcile SPEC-delta reject vocab, relabel scope/goal framing

slug: honest-reject-naming · created: 2026-06-28 · stage: mvp
autonomy: auto   <!-- inherited from the project default (PROJECT.md); explicit level: manual < conservative < auto (visible · overridable) — lower below if a high-risk task needs it, or run `add.py autonomy set`. Multi-component repo (monorepo/multi-repo)? add a `component: <name>` line (declared in `.add/components.toml`) to ADD that component's root to your §5 Scope; omit for single-component projects (byte-identical default). -->
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
- `add_engine/release.py:_build_in_flight` (×3 trees: add-method/tooling · .add/tooling · _bundled) — helper already honestly named; its docstring (line ~49) labels the proxy `release_tests_red` (the reject-code string to rename).
- `add.py:cmd_release` (×3 trees, line ~5528) — `_die("release_tests_red: a build is in flight …")` — the reject-code STRING to rename → `release_build_in_flight`.
- `add.py:cmd_carry_delta` (×3 trees, line ~614) — `_die("ambiguous_spec_delta: …")` for a `--match` that hits >1 OPEN delta; line ~611 folds a `--match` MISS into `no_open_spec_delta`.
- `add.py:cmd_reopen_delta` (×3 trees, line ~639) — `_die("ambiguous_spec_delta: …")` for a `--match` that hits >1 CARRIED delta (no-carried case = `no_carried_spec_delta`, line ~636).
- `add.py:cmd_drop_delta` / `cmd_new_task --from-delta` seed (×3 trees, lines ~470-474 / ~562-566) — the TARGET vocab to standardize on: `no_matching_spec_delta` (a `--match` miss, distinct from no-open) + `ambiguous_spec_match` (a `--match` hits >1).
- `add.py:cmd_check` goal_not_auto_ready emit (×3 trees, line ~2358) — code STRING unchanged; only its PROSE framing is reframed (no engine edit).
- `engine_pin.py` (canonical only) — re-aim `ENGINE_MD5` (add.py changed) + `ENGINE_PKG_MD5` (add_engine/release.py docstring changed); line ~13 genealogy comment mentions `release_tests_red` historically (a past-pin annotation, treat as historical record — NOT a live reference).

Context (working folder):
- Guide prose (×3 skill trees: add-method/skill/add · .claude/skills/add · _bundled/skill/add): `release.md:38` (`- \`release_tests_red\` — suite not green.`) · `scope.md:14` (`**Confirm before create is the invariant.**`) · `run.md:141-145` (the goal-clarity paragraph).
- Book prose (×3 TRACKED trees: add-method/docs · repo-root mirror · _bundled/docs — `.add/docs/` is GITIGNORED, regenerated on install, OUT of scope): `16-releasing.md:89` + `appendix-c-glossary.md:105` (both list `release_tests_red`) · `11-governance.md:26` + `appendix-c-glossary.md:111` (the "prerequisite that *earns* trust" framing).
- `.add/milestones/flow-honesty/MILESTONE.md` — exit criterion: "`release_tests_red` is gone (renamed) everywhere; scope.md + `goal_not_auto_ready` framing read honestly (verify: grep + test_reject_names)". `test_reject_names` DOES NOT EXIST — must be created.
- 5 open SPEC deltas: the reconcile drains the delta-drain "reject vocabulary" delta.

Honors (patterns / conventions):
- 3-tree byte-identity: add.py ×3 (test_shared_engine_pin via ENGINE_MD5) · skill guides ×3 (test_tree_parity + test_bundle_parity) · book ×3 tracked (test_book_parity root-mirror + test_bundle_parity bundled) · add_engine ×3 (ENGINE_PKG_MD5).
- Milestone ethic (MILESTONE.md "Shared decisions"): HONEST LABELING, judgment-free engine unchanged, backward-compatible/grandfather, security HARD-STOP untouched. This task adds NO new gate — it renames a code + reframes prose.
- Never rewrite HISTORY: archived `.add/tasks/*` records, CHANGELOG.md, engine_pin genealogy comment honestly recorded the OLD code at the time — excluded from the rename (the grep targets LIVE emit sites + guide/book floor lists, not historical annotations).
- test_skill_lean byte-budget (canonical tree, reference + core pools): scope.md/run.md prose edits must stay within frozen ratios or rebaseline (ratio kept exactly) per the security-escalation-disclosure lesson.

Anchors the contract cites: `_build_in_flight` · reject codes `release_tests_red`→`release_build_in_flight` · `ambiguous_spec_delta`→`ambiguous_spec_match` · carry/reopen `--match` miss → `no_matching_spec_delta` · `cmd_carry_delta` · `cmd_reopen_delta` · `cmd_drop_delta` · `goal_not_auto_ready` (string unchanged) · `engine_pin.ENGINE_MD5` / `ENGINE_PKG_MD5` · new `test_reject_names.py`.

---

## 1 · SPECIFY — the rules ▸ docs/03-step-1-specify.md

Feature: Honest reject naming — rename one misleading reject code, reconcile the divergent SPEC-delta reject vocab onto one set, and reframe two over-claiming prose labels. Pure honest-labeling: NO new gate, NO changed gate condition; the only behavior change is which reject-code STRING a user sees.
Framings weighed: honest-naming sweep (chosen — rename code + reframe prose + reconcile vocab, gates byte-unchanged) · minimal rename-only (leaves the vocab divergence the milestone scopes in — rejected) · reject-code registry/glossary (a new abstraction nobody asked for — rejected, over-engineering)
Must:
<must>
  - Rename the release readiness-floor reject code `release_tests_red` → `release_build_in_flight` at its emit site (`add.py:cmd_release` die message, ×3 add.py trees); the `_build_in_flight` proxy docstring (`add_engine/release.py`, ×3 trees) drops the `release_tests_red` label. The gate CONDITION (`_build_in_flight(state)`) and `--force`-ability are byte-unchanged — only the code STRING changes.
  - Name the new code in the floor's guide + book prose: `release.md:38`, book `16-releasing.md:89` + `appendix-c-glossary.md:105` say `release_build_in_flight` with an honest gloss ("a build is in flight — a task entered build/verify with no recorded green gate").
  - Reconcile the SPEC-delta reject vocabulary onto ONE set (the seed/drop vocab): `cmd_carry_delta` + `cmd_reopen_delta` emit `ambiguous_spec_match` (not `ambiguous_spec_delta`) when `--match` hits >1; `cmd_carry_delta` emits `no_matching_spec_delta` (not the lumped `no_open_spec_delta`) when `--match` MISSES while open deltas exist. `no_open_spec_delta` (no open delta at all) and reopen's `no_carried_spec_delta` (nothing carried) are KEPT — distinct conditions. Seed/drop already use this vocab → UNCHANGED.
  - Reframe the `goal_not_auto_ready` over-claim in `11-governance.md:26` + `appendix-c-glossary.md:111`: "the prerequisite that *earns* trust" → it MEASURES citation presence (a citation slot per criterion); it does not by itself earn trust — an honest citation does, which the engine cannot verify. The code string `goal_not_auto_ready` is UNCHANGED (no engine edit).
  - Relabel scope.md:14 "**Confirm before create is the invariant.**" to read honestly: confirm-before-create is the loop CONVENTION; the engine enforces it only through the OPT-IN `--await-confirm` gate (`milestone_unconfirmed`). Across all 3 skill trees.
  - Add `test_reject_names.py`: asserts the engine emits `release_build_in_flight` + `ambiguous_spec_match` + `no_matching_spec_delta` (behavioral), and that `release_tests_red` / `ambiguous_spec_delta` are ABSENT from live engine emit sites + guide/book floor lists (grep, excluding historical records).
  - All mirror trees stay byte-identical (add.py ×3 · add_engine ×3 · skill ×3 · book ×3 tracked); `ENGINE_MD5` + `ENGINE_PKG_MD5` re-aimed; full suite green; no existing assertion weakened.
</must>
Reject:
<reject>
  - carry/reopen `--match` matches >1 candidate delta -> "ambiguous_spec_match"   (was "ambiguous_spec_delta")
  - carry `--match` matches 0 while the task HAS open deltas -> "no_matching_spec_delta"   (was lumped into "no_open_spec_delta")
  - carry with no open SPEC delta at all -> "no_open_spec_delta"   (UNCHANGED)
  - reopen with no carried SPEC delta -> "no_carried_spec_delta"   (UNCHANGED)
  - `add.py release` while a build is in flight (a task in build/verify with gate=none) -> "release_build_in_flight"   (was "release_tests_red"; still --force-able)
  - the other release floor rejects (`release_security_open` un-forceable · `release_no_closed_milestone` · `release_undisclosed_waiver`) -> UNCHANGED
</reject>
After:
<after>
  - `grep -r release_tests_red` and `grep -r ambiguous_spec_delta` over LIVE code + guide + book trees find ZERO hits (only CHANGELOG / archived TASK.md / engine_pin genealogy remain — honest history).
  - The engine emits the new codes; `goal_not_auto_ready` prose reads as measurement (not "earns trust"); scope.md reads "opt-in gate" (not "the invariant").
  - All mirrors byte-identical, both pins re-aimed, `test_reject_names` + full suite green.
</after>
Assumptions — lowest-confidence first:
<assumptions>
  ⚠ [contract] the reconcile DIRECTION is to standardize carry/reopen ONTO the seed/drop vocab (`ambiguous_spec_match` + `no_matching_spec_delta`), not the reverse — lowest confidence because it is a genuine human-owned 2-way choice; I picked it for fewest test-breaks (one: test_delta_drain asserting `ambiguous_spec_delta`), the more precise "the MATCH is ambiguous" reading, and delta-match-selector's deliberate `no_matching_spec_delta` precedent. If wrong (human prefers the `_delta`/lumped-`no_open` vocab): invert to make seed/drop adopt carry's codes — more test edits (test_delta_match_selector), trivial to flip at the freeze, costly after build.
  ⚠ [spec] carry should ALSO distinguish a `--match` MISS as `no_matching_spec_delta` (a behavior refinement, the one place this task changes a code PATH not just a string), not keep folding it into `no_open_spec_delta` — low confidence because pure-renaming is the safer reading of "naming task". If wrong (human wants string-only, zero behavior change): reconcile ONLY the ambiguous code, leave carry's `--match` miss → `no_open_spec_delta` (residual asymmetry: carry still can't tell "your match missed" from "nothing to carry").
  - [ ] [scope] "gone everywhere" EXCLUDES historical records (CHANGELOG, archived `.add/tasks/*`, engine_pin genealogy comment) — the grep targets LIVE emit sites + guide/book floor lists; literal-zero-including-history would rewrite honest history (rejected).
  - [ ] [scope] `.add/docs/` is gitignored (regenerated on install) → OUT; the book change is the 3 TRACKED trees (canonical · repo-root mirror · _bundled).
</assumptions>

<!-- EXIT: every rule stated, every rejection named; assumptions ranked lowest-confidence first, the top one or two ⚠-flagged with why + cost (or, for trivial scope, an honest "none material" that still names the single biggest risk). -->

---

## 2 · SCENARIOS — pass/fail cases ▸ docs/04-step-2-scenarios.md

<scenarios>

```gherkin
Scenario: release refuses a build-in-flight with the renamed code
  Given a board with one task in phase=build and gate=none, ≥1 closed-not-released milestone
  When I run `add.py release <version>` (no --force)
  Then it exits non-zero naming "release_build_in_flight"
  And it does NOT name "release_tests_red"
  And no release is recorded (CHANGELOG / RELEASES.md unchanged)

Scenario: the build-in-flight floor is still --force-able (behavior unchanged)
  Given the same build-in-flight board
  When I run `add.py release <version> --force`
  Then the release is recorded (the gate condition + --force-ability are byte-unchanged)

Scenario: carry --match hitting >1 uses the reconciled ambiguous code
  Given a task with two open SPEC deltas both containing "cache"
  When I run `add.py carry-delta <task> --match cache --reason r`
  Then it exits non-zero naming "ambiguous_spec_match"
  And it does NOT name "ambiguous_spec_delta"
  And the task TASK.md is byte-unchanged

Scenario: carry --match that misses (open deltas exist) is now distinct
  Given a task with one open SPEC delta containing "cache"
  When I run `add.py carry-delta <task> --match zzz --reason r`
  Then it exits non-zero naming "no_matching_spec_delta"
  And it does NOT name "no_open_spec_delta"
  And the task TASK.md is byte-unchanged

Scenario: carry with no open delta at all keeps no_open_spec_delta (unchanged)
  Given a task with zero open SPEC deltas
  When I run `add.py carry-delta <task> --reason r`
  Then it exits non-zero naming "no_open_spec_delta"
  And the task TASK.md is byte-unchanged

Scenario: reopen --match hitting >1 uses the reconciled ambiguous code
  Given a task with two carried SPEC deltas both containing "queue"
  When I run `add.py reopen-delta <task> --match queue`
  Then it exits non-zero naming "ambiguous_spec_match"
  And it does NOT name "ambiguous_spec_delta"
  And the task TASK.md is byte-unchanged

Scenario: the old codes are gone from live code + guide + book
  Given the live engine, skill, and tracked book trees (excluding CHANGELOG / archived tasks / engine_pin genealogy)
  When I grep for "release_tests_red" and "ambiguous_spec_delta"
  Then there are zero hits

Scenario: the over-claiming prose now reads honestly
  Given 11-governance.md, appendix-c-glossary.md, and scope.md
  When I read the goal_not_auto_ready paragraph and scope.md line 14
  Then goal-clarity is framed as "measures citation presence" (the phrase "earns trust" is gone there)
  And scope.md frames confirm-before-create as the convention enforced only by the opt-in --await-confirm gate (not "the invariant")

Scenario: all mirrors stay byte-identical and the suite is green
  Given the rename + reconcile + reframe applied across every tree
  When I run the full suite (including test_shared_engine_pin, test_tree_parity, test_bundle_parity, test_book_parity, the new test_reject_names)
  Then every test passes
  And ENGINE_MD5 + ENGINE_PKG_MD5 match all three engine copies
```

</scenarios>

<!-- EXIT: one scenario per Must AND per Reject; each result is observable. -->

---

## 3 · CONTRACT — freeze the shape ▸ docs/05-step-3-contract.md

```
RELEASE FLOOR (add_engine/release.py:_build_in_flight — condition UNCHANGED; --force-able)
  add.py release <v>     a task in build/verify with gate=none  ->  _die "release_build_in_flight: …"   (was "release_tests_red")

SPEC-DELTA RESOLUTION VOCAB — reconciled to ONE set (the seed/drop vocab); validate-before-write (a reject writes nothing):
  add.py carry-delta <t> --match S    S matches >1 OPEN delta     ->  _die "ambiguous_spec_match: …"      (was "ambiguous_spec_delta")
  add.py carry-delta <t> --match S    S matches 0, OPEN exists    ->  _die "no_matching_spec_delta: …"     (was lumped → "no_open_spec_delta")
  add.py carry-delta <t> [--all]      no OPEN delta at all        ->  _die "no_open_spec_delta: …"          (UNCHANGED)
  add.py reopen-delta <t> --match S   S matches >1 CARRIED delta  ->  _die "ambiguous_spec_match: …"      (was "ambiguous_spec_delta")
  add.py reopen-delta <t>             no CARRIED delta            ->  _die "no_carried_spec_delta: …"       (UNCHANGED — distinct condition)
  (new-task --from-delta SEED + drop-delta already emit ambiguous_spec_match / no_matching_spec_delta — UNCHANGED)

PROSE FRAMINGS (read-only docs — NO code/behavior change; the code STRING "goal_not_auto_ready" is UNCHANGED):
  release.md:38 + 16-releasing.md + appendix-c-glossary.md floor list   "release_tests_red — suite not green"
                                                                     ->  "release_build_in_flight — a build is in flight (a task in build/verify, no recorded green gate)"
  11-governance.md + appendix-c-glossary.md   goal_not_auto_ready "the prerequisite that *earns* trust"
                                                                     ->  "measures citation presence" (a citation slot per criterion; does not by itself earn trust)
  scope.md:14   "**Confirm before create is the invariant.**"        ->  honest: confirm-before-create is the loop CONVENTION; the engine
                                                                         enforces it only via the OPT-IN --await-confirm gate (milestone_unconfirmed)

INVARIANTS (frozen):
  - gate CONDITIONS + behaviors byte-unchanged; only reject-code STRINGS change; the one behavior refinement is carry's --match-miss gaining a distinct code.
  - "goal_not_auto_ready" code string UNCHANGED (prose-only reframe → no engine edit, no test_goal_auto_ready_gate break).
  - historical records NOT rewritten (CHANGELOG · archived .add/tasks/* · engine_pin genealogy comment).
  - mirror byte-identity: add.py ×3 · add_engine ×3 · skill ×3 · book ×3 tracked (canonical · _bundled · repo-root); ENGINE_MD5 + ENGINE_PKG_MD5 re-aimed.
Names: the reject codes ARE the GLOSSARY's vocabulary (appendix-c-glossary.md release entry lists the four floor codes).
```

Status: FROZEN @ v1 — approved by Tin Dang
Least-sure flag surfaced at freeze: [contract] reconcile DIRECTION — standardize carry/reopen onto the seed/drop vocab (`ambiguous_spec_match` + carry's `--match`-miss → distinct `no_matching_spec_delta`) rather than the reverse. why low: a genuine human-owned 2-way naming choice; cost if wrong: invert to the `_delta` family (more test edits — test_delta_match_selector) — cheap pre-build, costly after. Secondary [spec]: carry gains a distinct `--match`-miss code path (the one behavior change vs a pure rename). RESOLVED at freeze: Tin chose "Freeze as drafted" — seed/drop vocab, full reconcile.
<!-- The freeze IS the one approval — lead it with the bundle's lowest-confidence flag: the 1–2
     points most likely wrong across the whole bundle, tagged [spec|scenario|contract|test], each
     with why + cost (the §1 ⚠ assumptions feed it; a flag may point at a scenario or the contract
     too — see run.md). Approved -> Status: FROZEN @ vN — approved by <name>. Changing a frozen
     contract = change request back to SPECIFY.
     EXIT: frozen + every spec rejection has a contracted response + names match GLOSSARY + the
     bundle's lowest-confidence flag was surfaced at the freeze (or an honest "none material"). -->

---

## 4 · TESTS — failing-first suite (red) ▸ docs/06-step-4-tests.md

Coverage target: one test per Must/Reject scenario (9 new in test_reject_names.py + 1 conformed assert in test_delta_drain.py); full existing suite stays green; mirror parity guarded by the existing test_shared_engine_pin / test_tree_parity / test_bundle_parity / test_book_parity (not re-authored).
Plan (one test per scenario, asserting behavior not internals):
<test_plan>
  - test_release_floor_uses_new_code: build-in-flight board (task phase=build, gate=none; ≥1 closed-unreleased ms) / `release <v>` / assert exit≠0 + "release_build_in_flight" in out + "release_tests_red" NOT in out + no CHANGELOG/RELEASES write
  - test_release_floor_still_forceable: same board / `release <v> --force` / assert release recorded (condition + --force-ability byte-unchanged)
  - test_carry_ambiguous_uses_match_code: 2 OPEN deltas both "cache" / `carry-delta t --match cache --reason r` / assert exit≠0 + "ambiguous_spec_match" + NOT "ambiguous_spec_delta" + TASK.md byte-unchanged
  - test_carry_match_miss_distinct: 1 OPEN delta "cache" / `carry-delta t --match zzz --reason r` / assert exit≠0 + "no_matching_spec_delta" + NOT "no_open_spec_delta" + byte-unchanged
  - test_carry_no_open_unchanged: 0 OPEN deltas / `carry-delta t --reason r` / assert exit≠0 + "no_open_spec_delta" + byte-unchanged
  - test_reopen_ambiguous_uses_match_code: 2 CARRIED deltas both "queue" / `reopen-delta t --match queue` / assert exit≠0 + "ambiguous_spec_match" + NOT "ambiguous_spec_delta" + byte-unchanged
  - test_old_codes_absent_from_live_trees: grep live engine+skill+book trees (EXCLUDING CHANGELOG.md, .add/tasks/*, .add/archive/*, engine_pin.py genealogy) / assert ZERO "release_tests_red" + ZERO "ambiguous_spec_delta"
  - test_goal_prose_measures_not_earns: read 11-governance.md + appendix-c-glossary.md / assert the goal-clarity passage frames it as "measures citation presence" + the "prerequisite that earns trust" phrasing is gone
  - test_scope_md_opt_in_not_invariant: read scope.md / assert confirm-before-create is framed as the convention enforced only by the opt-in --await-confirm gate, NOT "the invariant"
  - (conform) test_delta_drain.py:183 — assert "ambiguous_spec_match" (was "ambiguous_spec_delta") — a faithful conform to the reconciled code, not a weakening
</test_plan>

Tests live in: `add-method/tooling/test_reject_names.py` `add-method/tooling/test_delta_drain.py` · MUST run red (missing implementation) before Build.
<!-- declare paths as backticked tokens on this line: `./…` = this task dir ·
     a token with "/" = project root · a bare name = sibling of the previous
     token's dir · a directory counts its *.py files (non-recursive); reports
     mark declared counts with † · anything resolving outside the project root counts 0 -->

<!-- EXIT: one test per scenario; suite red for the RIGHT reason; target recorded. -->

---

## 5 · BUILD — AI writes code ▸ docs/07-step-5-build.md

Scope (may touch): `add-method/tooling/add.py` `.add/tooling/add.py` `add-method/src/add_method/_bundled/tooling/add.py` `add-method/tooling/add_engine/release.py` `.add/tooling/add_engine/release.py` `add-method/src/add_method/_bundled/tooling/add_engine/release.py` `add-method/tooling/engine_pin.py` `add-method/tooling/test_reject_names.py` `add-method/tooling/test_delta_drain.py` `add-method/skill/add/release.md` `add-method/skill/add/scope.md` `add-method/skill/add/run.md` `.claude/skills/add/release.md` `.claude/skills/add/scope.md` `.claude/skills/add/run.md` `add-method/src/add_method/_bundled/skill/add/release.md` `add-method/src/add_method/_bundled/skill/add/scope.md` `add-method/src/add_method/_bundled/skill/add/run.md` `add-method/docs/16-releasing.md` `add-method/docs/11-governance.md` `add-method/docs/appendix-c-glossary.md` `add-method/src/add_method/_bundled/docs/16-releasing.md` `add-method/src/add_method/_bundled/docs/11-governance.md` `add-method/src/add_method/_bundled/docs/appendix-c-glossary.md` `add-method/../16-releasing.md` `add-method/../11-governance.md` `add-method/../appendix-c-glossary.md` `.add/CONVENTIONS.md`
<!-- add.py ×3 + add_engine/release.py ×3 + engine_pin.py (canonical re-pin) + 2 canonical tests (new test_reject_names + edit test_delta_drain) + skill ×3 (release/scope/run) + book ×3 TRACKED homes (canonical add-method/docs · _bundled/docs · repo-root via the `add-method/..` climb — a slash-bearing token resolves at project root; a BARE name would resolve to the task dir → false scope_violation, the site-scaffold lesson). `.add/docs/` is GITIGNORED (0 tracked files) → ride-along, synced by hand for local dogfood, never gated/committed. Modeled on adr-audit-and-docs §5. `.add/CONVENTIONS.md` ADDED post-freeze (verify-gate, human-approved): the refute-read found a folded foundation-version-34 lesson still naming `release_tests_red`; declared for honesty though `.add/` is `_SCOPE_EXCLUDE_DIRS`-pruned (gate never walks it — documentary, not gated; anchor.declared synced to match). -->
Strategy (ordered batches): 1. write `add-method/tooling/test_reject_names.py` RED (engine emits new codes + old codes absent from live trees). 2. conform the ONE existing assertion `test_delta_drain.py:183` `ambiguous_spec_delta`→`ambiguous_spec_match` (faithful, not a weakening). 3. edit canonical add.py (cmd_release die msg → `release_build_in_flight`; carry/reopen ambiguous → `ambiguous_spec_match`; carry `--match`-miss → `no_matching_spec_delta`) + `add_engine/release.py` docstring (drop `release_tests_red` label). 4. write-once-copy add.py + add_engine/release.py byte-identical to `.add/tooling/` + `_bundled/tooling/`; re-aim ENGINE_MD5 + ENGINE_PKG_MD5 in engine_pin.py. 5. edit canonical skill release.md/scope.md/run.md → copy to `.claude/skills/add/` + `_bundled/skill/add/`. 6. edit canonical book 16-releasing.md/11-governance.md/appendix-c-glossary.md → copy to repo-root + `_bundled/docs/`; sync `.add/docs/` (ride-along). 7. run from `add-method/`: full suite + check + audit green.
Known-problem fixes: carry's `--match` miss is currently lumped at add.py:610-612 (`if status in ("no_open","no_match")`) — SPLIT it: `no_match`→`no_matching_spec_delta`, keep `no_open`→`no_open_spec_delta` (don't break the no-open path) · reopen keeps `no_carried_spec_delta`, only its ambiguous → `ambiguous_spec_match` · `test_reject_names` absence-grep MUST exclude CHANGELOG/archived `.add/tasks/*`/engine_pin genealogy (else false-fail on honest history) · test_skill_lean byte budget: keep scope.md/run.md edits length-neutral (the goal_not_auto_ready reframe is in BOOK, not run.md) or rebaseline ratio-kept · a post-build §5 fix needs a tests→build re-cross to re-anchor.
Strategy actually used: <fill at VERIFY — the strategy you ACTUALLY used (or "as planned"); harvested into the §7 Decisions (ADR) block as the [AI] build decision>
Safety rule (feature-specific): every mirrored file written from ONE canonical source (write-once-copy) so byte/md5 parity is STRUCTURAL — never hand-edit a mirror independently. Never weaken a test to pass a build; the gate conditions stay byte-unchanged (only the reject STRINGS move).
Code lives in: the canonical `add-method/tooling/` (add.py · add_engine/release.py · engine_pin.py · tests) + `add-method/skill/add/` + `add-method/docs/`, propagated byte-identical to every mirror tree.
Constraints: do NOT change any test or the contract; allow-list packages only; ask if unclear.

<!-- Scope tokens, backticked, FIRST declaring line: `./…` = this task dir · a token
     with "/" = project root · a bare name = sibling of the previous token's dir ·
     outside-root resolutions are dropped fail-closed · a DIRECTORY token covers its
     whole subtree (containment — diverges from §4's non-recursive counting) ·
     absent line = UNDECLARED (pre-existing tasks grandfathered, never retro-red) ·
     engine enforcement (touched ⊆ declared) lands in scope-gate-enforce.
     EXIT: all green; coverage held; no test/contract touched; no unlisted dependency. -->

---

## 6 · VERIFY — evidence + non-functional review ▸ docs/08-step-6-verify.md

- [x] all tests pass — full suite 2144/0; test_reject_names 12/12 + test_delta_drain 11/11
- [x] coverage did not decrease — +1 file/12 tests (test_reject_names) + 1 conformed assert (test_delta_drain); no test removed or loosened
- [x] no test or contract was altered during build — all test edits done in the TESTS phase; §3 FROZEN @ v1 untouched; tamper tripwire intact (build touched only add.py · add_engine/release.py · prose · engine_pin)
- [x] the green was EARNED, not gamed — independent adversarial refute-read **VERDICT: EARNED** (agent `a5521157ea366a70f`): all 6 failure modes refuted — no weakened test, no vacuous/overfit asserts (`test_carry_match_miss_is_distinct` can't be fooled by the prose "no open SPEC delta"), gate conditions byte-unchanged, no stray live old code, mirrors+pins correct, prose honest. One disclosed residue → Residue below
- [x] concurrency / timing of the risky operation is safe — N/A: pure reject-string rename + read-only prose; no runtime/concurrent path changed
- [x] no exposed secrets, injection openings, or unexpected dependencies — string/prose edits only; stdlib only; no new deps
- [x] layering & dependencies follow CONVENTIONS.md — 3-tree byte-identity held; engine NO-EXEC; the `_build_in_flight` condition + `--force`-ability are byte-unchanged
- [x] a person reviewed and approved the change — **human approved** (Tin Dang, 2026-06-28): escalated method/trust-layer residue reviewed; chose PASS + close the disclosed CONVENTIONS.md ref first (done below)

### Build expectations — what "correct" looks like (fill BEFORE build; confirm each at the gate)
> Pre-declare the OBSERVABLE outcomes a correct build must produce — derived from §2 SCENARIOS
> + §3 CONTRACT — so this gate checks the build is RIGHT, not merely that tests are green. Each
> row is evidence you can SEE, not a restatement of a test name.
- [x] `add.py release` on a build-in-flight board prints `release_build_in_flight` (NOT `release_tests_red`) and writes nothing; `--force` still cuts past it — confirmed: `ReleaseFloorNamingTest` (live run; `test_release_floor_still_forceable` proves `--force` cuts) + the floor grep
- [x] `carry-delta --match` hitting >1 prints `ambiguous_spec_match`; a `--match` miss with open deltas prints `no_matching_spec_delta`; no-open still prints `no_open_spec_delta`; reopen `--match` >1 prints `ambiguous_spec_match` — confirmed: `SpecDeltaVocabTest` (4 live CLI runs, all green)
- [x] `grep -rn release_tests_red` / `ambiguous_spec_delta` over live engine + skill + book trees returns 0 hits (CHANGELOG / `.add/tasks/*` / engine_pin genealogy excluded) — confirmed: live grep `>>> ZERO live hits (clean)`
- [x] `11-governance.md` reads "measures citation presence" with no "earns trust"; scope.md reads "Confirm before create is the convention …" + the opt-in `--await-confirm` gate (not "the invariant") — confirmed: `ProseFramingTest` green + read in full
- [x] all 3 add.py + add_engine copies byte-identical and ENGINE_MD5 / ENGINE_PKG_MD5 match; skill ×3 + book ×3 byte-identical — confirmed: test_shared_engine_pin + test_tree_parity + test_bundle_parity + test_book_parity green; ENGINE_MD5→`93fb0745`, ENGINE_PKG_MD5→`795abe88`; add.py md5 identical ×3, release.py md5 identical ×3 (refute-read)
- [x] full suite green incl. test_reject_names (12/12) + test_delta_drain (11/11); `add.py check` + `audit` clean — confirmed: suite 2144/0, check 469/0, audit exit 0

### Deep checks — do not skim (fill the path that applies; the resolver judges which)
- [x] WIRING (code) — no NEW symbol (only reject-string literals changed). Renamed die-strings emit at `add.py` cmd_release (`release_build_in_flight`), cmd_carry_delta (`no_matching_spec_delta` on `_select_spec_delta`→`no_match`; `ambiguous_spec_match` on `→ambiguous`), cmd_reopen_delta (`ambiguous_spec_match`). carry now SPLITS `no_open`/`no_match`; reopen still maps `no_match`→`no_carried_spec_delta` (unchanged, per §3). All branches reachable + exercised by green tests (refute-read traced `_select_spec_delta`).
- [x] DEAD-CODE (code) — no new symbols introduced; no orphan. `_build_in_flight` retained, condition byte-identical (only its docstring relabeled).
- [x] SEMANTIC (prose / non-code) — read in full: `11-governance.md §goal-clarity` (lint now "measures citation presence", drops "earns trust"; `goal_not_auto_ready` code unchanged), `scope.md` (confirm-before-create = "the convention … enforced only by the opt-in `--await-confirm`"), `release.md` floor gloss + `16-releasing.md §16.4` (`release_build_in_flight` = "a build is in flight, ungated"), `appendix-c-glossary.md` readiness-floor entry. No over-claim remains in edited prose; `run.md` carries no stray "earns trust" (refute-read confirmed).

### Residue — escalated to human; both items resolved before PASS
- **METHOD / TRUST-LAYER edit (PROJECT.md v6 residue category).** This task edits the BOOK (11-governance.md · 16-releasing.md · appendix-c-glossary.md — the trust layer users read) + guides (scope.md · release.md) + engine reject-code strings. Per PROJECT.md v6, method/trust-layer edits escalate to a human even under `autonomy: auto`. Not a security/concurrency/architecture finding; evidence complete + refute-read EARNED. → **Human reviewed + approved** (Tin Dang, 2026-06-28).
- **DISCLOSED (refute-read) → RESOLVED.** `.add/CONVENTIONS.md:171` — a folded foundation-version-34 lesson still named `release_tests_red`. The refute-read scoped its hygiene scan narrowly (engine + skill + 3 book files); a follow-up **comprehensive `git grep` over ALL tracked files** confirmed this was the ONLY stale live ref (the shipped `CONVENTIONS.md.tmpl` template + everything else clean; `state.json` hit is the descriptive task title). Human chose **close-now**: swapped the token → `release_build_in_flight` (keeps the lesson's meaning; the new name matches the parenthetical "in-flight build with no green gate" already there → MORE honest, not a history rewrite — git preserves v34 wording). `.add/` is `_SCOPE_EXCLUDE_DIRS`-pruned so the swap can't trip `scope_violation`; declared in §5 + anchor for honesty anyway. Post-fix sweep: **ZERO stale refs**; check 469/0, audit exit 0.

### GATE RECORD
Outcome: PASS
If RISK-ACCEPTED -> owner: <name> · ticket: <link> · expires: <date>   (never for a security gap)
Reviewed by: Tin Dang · date: 2026-06-28

<!-- A security finding is ALWAYS HARD-STOP. Record exactly one outcome — no silent pass. -->

---

## 7 · OBSERVE — feed the next loop ▸ docs/09-the-loop.md

Watch (reuse scenarios as monitors): `test_reject_names` is the live monitor — it fails if any of the renamed reject codes regresses (engine stops emitting `release_build_in_flight` / `ambiguous_spec_match` / `no_matching_spec_delta`) or if an old code (`release_tests_red` / `ambiguous_spec_delta`) reappears in a live engine/guide/book surface.

### Decisions (ADR)
- [AI] specify — chose honest-naming sweep; rejected minimal rename-only (leaves the vocab divergence the milestone scopes in — rejected) · reject-code registry/glossary (a new abstraction nobody asked for — rejected, over-engineering)
- [human] freeze — froze §3 @ v1 (approved by Tin Dang)
- [AI] build — strategy used: as planned
- [AI] verify — gate PASS (reviewed by Tin Dang)

### Spec delta
Forward changes for the next loop — each re-enters at Specify as the next task. One line
each, tagged `[SPEC · open|seeded|dropped]`, with evidence (e.g. `[SPEC · open] rate-limit
the retry path (evidence: prod herd spikes)`). See the `add` skill's `deltas.md`.
- [SPEC · dropped] the delta-drain "reject vocabulary divergence" delta is resolved — carry/reopen now emit `ambiguous_spec_match` + carry's `--match`-miss emits `no_matching_spec_delta`, matching seed/drop (evidence: SpecDeltaVocabTest green, test_delta_drain conformed).
- [SPEC · seeded] widen the rename/honesty hygiene scan to the SHIPPED `CONVENTIONS.md.tmpl` template + folded foundation lessons, not just engine+guide+book floor-lists — a narrowly-scoped absence-test/refute-read missed `.add/CONVENTIONS.md:171`; only a comprehensive `git grep` caught it (evidence: refute-read EARNED yet a stale ref survived → feeds `stale-guide-sync`).

### Competency deltas
What did this loop teach the foundation? One line each, tagged by competency
(`DDD · SDD · UDD · TDD · ADD`), status `open`, with evidence. See the `add` skill's `deltas.md`.
<!-- e.g.  - [DDD · open] the model missed multi-tenancy (evidence: scenario_x failed) -->
- [ADD · folded] a code rename ripples beyond emit sites into folded foundation lessons (`CONVENTIONS.md`) + the shipped template; a hygiene grep / refute-read scoped to "engine+guide+book" misses them — sweep ALL tracked files (exclude only CHANGELOG/archive/`.add/tasks`/`.add/milestones`/engine_pin-genealogy/worktrees) (evidence: comprehensive `git grep` caught `.add/CONVENTIONS.md:171` after the narrow refute-read passed EARNED). [folded foundation-version 57]
- [ADD · folded] `.add/` is `_SCOPE_EXCLUDE_DIRS`-pruned, so editing any `.add/`-tree file is invisible to the scope gate — a `.add/` §5 token is documentary, not gated, and re-anchoring an excluded-dir fix needs NO tests→build re-cross (evidence: the verify-time CONVENTIONS.md fix tripped no `scope_violation`; corrects the §5 "Known-problem" note that assumed a re-cross). [folded foundation-version 57]
- [ADD · folded] method/trust-layer edits (the BOOK + guides + reject-code strings) escalate the verify gate to a human even under `autonomy: auto` — a built-in auto-gate carve-out like security (PROJECT.md v6 residue category) (evidence: this gate escalated via AskUserQuestion; not auto-passed). [folded foundation-version 57]
- [TDD · folded] when an honest-reframe ADDS prose bytes and trips `test_skill_lean`, reclaim from the same guide's own gloss (book carries the full description; the guide stays terse) rather than rebaselining the budget (evidence: reference pool 45148→≤45114 after a 2-line trim, ratios untouched). [folded foundation-version 57]
