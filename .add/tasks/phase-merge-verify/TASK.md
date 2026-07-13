# TASK: Merge observe into verify: 7->6 phase list

slug: phase-merge-verify · created: 2026-07-14 · stage: mvp
milestone: six-phase-loop
autonomy: auto
phase: done
fast: true

> Fast lane — one small task, minimal sections, filled top-to-bottom. The trust floor still
> holds: a FROZEN §3 contract · ≥1 red test before build · a recorded §6 gate (security = HARD-STOP).
> The acceptance scenario collapses into §1 `Accept:`; OBSERVE is one optional line at the gate.

---

## 1 · SPECIFY — the rules

> Project the expectations from the milestone Ground + this request — light, not re-invented.
Feature: phase-merge-verify — the observe PHASE folds into verify (six-phase-loop 2/6, the second human-decided TRUE merge): verify owns evidence + gate AND the watch/spec-delta duty; §7 OBSERVE stays as a section (the stable API) rendered under verify, exactly as §2 renders under specify
Must:
  - PHASES drops "observe" (6 tokens incl done: specify,plan,tests,build,verify,done); a bare `advance` from verify lands at done; every phase map follows (PHASE_GUIDE verify action gains the watch+spec-delta duty · PHASE_OWNER · PHASE_GROUPS VERIFY=("verify",) · PHASE_AGENT · spawn hints · guide-file map · every phase-set membership list: autonomy audit, deltas-gate, status recorded-lens, audit verdict/refute scans)
  - legacy state migrates on read: phase token "observe" -> "verify" via _normalize_phase_tokens's _legacy map (same silent/TOTAL/idempotent normalize-on-read as scenarios->specify)
  - _SKIPPABLE_PHASES = () — nothing is skippable; the cmd_advance skip-hop block (dead once the tuple empties) is PRUNED; a vestigial `skips:` header declaration (any token) is tolerated LOUD at gate/completion time — one advisory note, never a die (the grammar itself is retired)
  - _PHASE_SECTIONS gains "verify": (6, 7) — the §7 body renders under the verify block; task_phases emits 5 pre-done blocks
  - the two residual ordinal->section mappings repair to the _PHASE_SECTIONS table: advance --fill (add.py ~1537) and status --section <phase> (~2706) — both broke silently at phase-merge-specify (plan resolved to §2, not §3); each targets the phase's PRIMARY (first) section; --section digits 0-7 still reach any section directly
  - the observe-crossing fold nudge (add.py ~1722) moves to gate completion output (where the ADR harvest already lives); installer showcase twins (cli.js BRAND_LOOP · _installer.py _LOOP) shrink to the 5 pre-done steps
Reject:
  - `advance --to observe` / `phase observe <slug>` -> the existing unknown/invalid-phase refusal (observe is no longer a phase token)
  - a `skips:` declaration naming ANY token (retired or not) -> the advisory gate-time note (not a die, not a silent accept — loud-never-silent floor held with the grammar retired)
Accept: Given a task at verify with §6 filled, When `gate PASS` runs, Then the task is done and the fold nudge printed at gate; and Given a pre-merge state.json with a task at phase "observe", When any command loads state, Then the task reads as phase "verify" and its recorded gate (if any) still counts it as gate-recorded.
Boundary: two legacy dialects again — the state token ("observe" in state.json, possibly WITH a recorded gate) and the header skip declaration (`skips: observe`); both land tolerated (silent normalize vs loud gate-note)
Assumptions: ⚠ pruning the cmd_advance skip block rewrites test_fast_lane_skips (just rebuilt around observe-only) plus the M13 zero-skip-logic pins and task 1's own LegacySkipDeclarationTest — why: those tests pin the observe crossing, which stops existing; if wrong (a pin resists rewrite because it guards a live behavior I missed): re-cross and re-shape the note placement (cost: fence rounds). Ripple estimate ~30 suites again (report dots · phase-detail blocks · len/range pins · onboarding slice).

---

## 3 · PLAN — the change plan: ground · contract · build-strategy

### Grounding
Touches (files · symbols): add-method/tooling/add_engine/constants.py:PHASES/_SKIPPABLE_PHASES/PHASE_GUIDE/PHASE_OWNER/PHASE_GROUPS/PHASE_AGENT · add-method/tooling/add.py:_normalize_phase_tokens/_PHASE_SECTIONS/cmd_advance-skip-block-1602/observe-note-1722/fill-ordinal-1537/section-ordinal-2706/spawn-hint-2042/guide-map-3073/membership-lists-3825-4025-6354-7420-7551-7580/help-8455-8650 · add-method/bin/cli.js:BRAND_LOOP · add-method/src/add_method/_installer.py:_LOOP · fixture files stepping the observe phase (fence-named, declared ripples)
Context (working folder): ENGINE_MD5 + ENGINE_PKG_MD5 both re-aim; SEAMS _declared_scope pin drifts on add.py line shifts; sync engine x3 never tests
Honors (patterns / conventions): the phase-merge-specify precedent verbatim (_legacy map · _RETIRED_SKIP_TOKENS · explicit _PHASE_SECTIONS over ordinal math · sections never renumber) · defaults loud, never silent-skip · guides/SKILL.md prose re-cut deferred to guide-recut
Anchors the contract cites: PHASES · _normalize_phase_tokens · _SKIPPABLE_PHASES · _RETIRED_SKIP_TOKENS · _PHASE_SECTIONS · PHASE_GROUPS
Ground SHA: fa12a4d — stamped by freeze

### Contract

```
constants.py:
  PHASES = ("specify", "plan", "tests", "build", "verify", "done")
  _SKIPPABLE_PHASES = ()
  PHASE_GUIDE["verify"] action += "; then note what to watch + the spec delta
    for the next loop (§7)"
  PHASE_GROUPS["VERIFY"] = ("verify",)
  PHASE_OWNER/PHASE_AGENT/PHASE_GUIDE: observe keys removed
add.py:
  _normalize_phase_tokens: _legacy gains "observe": "verify"
  _RETIRED_SKIP_TOKENS = frozenset({"scenarios", "observe"})
  cmd_advance: the `if nxt in _SKIPPABLE_PHASES:` hop block PRUNED (dead);
    the observe fold-nudge block PRUNED (moves to gate)
  cmd_gate completion: header carries a `skips:` line -> print one note
    "the skip grammar is retired — no phase can be skipped (six-phase-loop);
    the declaration is ignored"; then the fold nudge (add.py <fold-verb>
    --task <slug>) prints on every completion
  _PHASE_SECTIONS = {"specify": (1,2), "plan": (3,), "tests": (4,),
                     "build": (5,), "verify": (6,7)}
  advance --fill + status --section <phase>: n = _PHASE_SECTIONS[cur][0]
    (ordinal+1 math retired; digit args unchanged 0-7)
  membership lists drop "observe"; spawn hint + guide-map entries removed;
  help text: --to (specify..verify) · skip-unlock prose retired
installer twins: BRAND_LOOP/_LOOP = (Specify, Plan, Tests, Build, Verify)
```

`Least-sure flag surfaced at freeze:` [test] the gate-time note placement — why: gate has TWO paths to completion (direct `gate` at verify and the compound tick from build) plus reopen->re-gate; the note must fire on all completion paths without double-printing or tripping the report/e2e suites that pin gate output lines; if wrong: anchor the note in the one shared completion helper the paths already funnel through (cost: one refactor round)
Status: FROZEN @ v1 — approved by Tin Dang
### Build-strategy
Scope (may touch): `add-method/tooling/` `add-method/src/add_method/_bundled/tooling/` `.add/tooling/` `add-method/.add/` `add-method/bin/` `add-method/src/add_method/_installer.py`
Strategy & known-problem fixes: red tests -> constants maps -> _legacy/_RETIRED tokens -> prune skip block + observe nudge -> gate-time note + fold nudge -> _PHASE_SECTIONS repairs (--fill/--section) -> membership/help sweeps -> installer twins -> fence -> fixture ripple rounds. Traps: the ordinal->section class (NO index math anywhere — table only) · test_fast_lane_skips + M13 pins + task 1's LegacySkipDeclarationTest all pin the observe crossing (rewrite to gate-time) · a pre-merge observe task WITH recorded gate must stay gate-recorded after normalize · sync x3 · both MD5 pins re-aim · SEAMS line pin drifts.
Approach (domain strategy): lifecycle shrinks again, section API frozen; migrate-on-read; retire the skip grammar loud; duties move to the gate seam where the ADR harvest already lives

### AI-verify record (required when gate_mode: ai-plan-verify)
- [x] §3 PLAN grounding anchors resolve in the current tree (constants.py:59/83/94/106/117/347 + add.py:1537/1602/1722/2042/2706/3073/3825/4025/6354/7420/7551/7580/8455/8650 all read this session)
- [x] §1 every Must + every Reject present, each paired with its outcome
- [x] §3 Contract shape is concrete (no template placeholder text remains)
- [x] Lowest-confidence flag surfaced and substantive (the gate-note double-print risk across the two completion paths)
Verified by: claude-fable-5 (orchestrator, inline) · at: 2026-07-14T01:35:00Z

---

## 4 · TESTS — failing-first (red)

Plan: test_phases_has_no_observe · test_advance_verify_lands_done · test_gate_pass_at_verify_marks_done_with_fold_nudge · test_legacy_observe_state_normalizes (plain AND with a recorded gate) · test_phase_cmd_observe_refused · test_vestigial_skips_header_noted_at_gate_never_dies · test_fill_and_section_use_the_sections_table (plan->§3, verify->§6) · test_phase_sections_verify_owns_6_and_7.
Tests live in: `add-method/tooling/test_phase_merge_verify.py` · MUST run red before Build.

---

## 5 · BUILD — AI writes the code (execution)

> The change plan was frozen in §3 PLAN. Build to it: honor the §3 Build-strategy Scope; improve on the strategy if the code teaches you better.
Strategy actually used: as planned, plus: the whole cmd_advance skip block pruned clean (not just the hop) — with _SKIPPABLE_PHASES empty every line of it was dead; the gate note anchors AFTER the verify-command lines on the `completing` branch (the one shared path both completion routes funnel through — the freeze flag's double-print risk never materialized); the skip HELPERS stay as read-tolerance (status line for historic recorded skips · resolver still names a bad token · audit rationale glint on historic boards); the fast template's skips scaffold removed (grammar retired end-to-end). Ripple: 49 failures/17 suites in fence r1, fast_lane_skips rewritten to pin the RETIREMENT, all repaired, zero weakened.
Code lives in: `./src/`   ·   Constraints: change no test, no frozen contract; stay inside the §3 Build-strategy Scope; allow-list packages only.

---

## 6 · VERIFY — evidence + gate

- [x] all tests pass · coverage held · no test or contract altered during build
- [x] green was EARNED — no overfit / vacuous asserts / stubbed-away logic
- [x] input dialect held — tests speak the spec's example formats (spec-dialect floor)
- [x] no exposed secrets, injection openings, or unexpected dependencies (security = HARD-STOP)

Build expectations (from §1 Accept + §3 CONTRACT): PHASES carries no `observe`; a bare advance from verify lands at done; gate PASS at verify completes with the fold nudge printed; a legacy `observe` state token normalizes to verify keeping any recorded gate; a vestigial `skips:` header (any token) is noted loud at gate, never a die; --fill and --section resolve through _PHASE_SECTIONS (verify owns §6+§7) — confirmed by test_phase_merge_verify 13/13 (12 red first + 1 boundary-keeper) + the FULL fence 3527 tests OK / REAL_EXIT=0 (fence-pmv-r2.log; 49-failure ripple across 17 suites repaired as the §1-declared rewrite, zero tests weakened); engine twins ×3 byte-identical; ENGINE_MD5 5d5e0538 + ENGINE_PKG_MD5 fc40ad47 re-pinned; SEAMS `_declared_scope` anchor re-pinned to add.py:5603.

### GATE RECORD
Outcome: PASS
Reviewed by: Tin Dang · date: 2026-07-14

